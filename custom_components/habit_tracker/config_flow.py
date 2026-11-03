"""Configure a backend URL and tenant-scoped PAT, validated before saving."""
import asyncio
from uuid import uuid4

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector

from .api import ApiError, Forbidden, HabitApi, InvalidAuth, validate_url
from .const import CONF_ALLOW_HTTP, DOMAIN
from .presets import PRESETS, defaults

TOKEN_SELECTOR = selector.TextSelector(selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD))
SCHEMA = vol.Schema({vol.Required("url"): str,
                     vol.Required("token"): TOKEN_SELECTOR,
                     vol.Optional(CONF_ALLOW_HTTP, default=False): bool})


class HabitTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return HabitOnboardingFlow()

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                url = validate_url(user_input["url"], user_input.get(CONF_ALLOW_HTTP, False))
                api = HabitApi(async_get_clientsession(self.hass), url, user_input["token"])
                data = await api.dashboard()
                await self.async_set_unique_id(f"{url}|{data['user_id']}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Habit Tracker", data={**user_input, "url": url})
            except ValueError:
                errors["base"] = "invalid_url"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except (ApiError, aiohttp.ClientError, asyncio.TimeoutError):
                errors["base"] = "cannot_connect"
        return self.async_show_form(step_id="user", data_schema=SCHEMA, errors=errors)

    async def async_step_reauth(self, entry_data):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        return await self._token_form(self._get_reauth_entry(), user_input, "reauth_confirm", "reauth_successful")

    async def async_step_reconfigure(self, user_input=None):
        return await self._token_form(self._get_reconfigure_entry(), user_input, "reconfigure", "reconfigure_successful")

    async def _token_form(self, entry, user_input, step, reason):
        errors = {}
        if user_input:
            try:
                data = await HabitApi(async_get_clientsession(self.hass), entry.data["url"], user_input["token"]).dashboard()
                if f"{entry.data['url']}|{data['user_id']}" != entry.unique_id:
                    return self.async_abort(reason="wrong_account")
                return self.async_update_reload_and_abort(entry, data_updates=user_input, reason=reason)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except (ApiError, aiohttp.ClientError, asyncio.TimeoutError):
                errors["base"] = "cannot_connect"
        return self.async_show_form(step_id=step, data_schema=vol.Schema({vol.Required("token"): TOKEN_SELECTOR}), errors=errors)


def select(options, translation_key):
    return selector.SelectSelector(selector.SelectSelectorConfig(
        options=options, mode=selector.SelectSelectorMode.DROPDOWN, translation_key=translation_key))


class HabitOnboardingFlow(config_entries.OptionsFlow):
    """Create one habit at a time, with explicit confirmation and scoped API writes."""

    async def async_step_init(self, user_input=None):
        return self.async_show_menu(step_id="init", menu_options=["preset", "custom", "finish"])

    async def async_step_preset(self, user_input=None):
        if user_input:
            self._preset = user_input["preset"]
            self._values = defaults(self._preset, self.hass.config.language, self.hass.config.time_zone)
            self._key = str(uuid4())
            return await self.async_step_habit()
        return self.async_show_form(step_id="preset", data_schema=vol.Schema({
            vol.Required("preset"): select(list(PRESETS), "preset")}))

    async def async_step_custom(self, user_input=None):
        self._preset = "custom"
        self._values = defaults("custom", self.hass.config.language, self.hass.config.time_zone)
        self._key = str(uuid4())
        return await self.async_step_habit()

    async def async_step_habit(self, user_input=None):
        errors = {}
        if user_input:
            self._values.update(user_input)
            habit = {key: self._values[key] for key in
                     ("name", "category", "kind", "unit", "target", "period", "timezone")}
            illustration = "water" if habit["unit"] == "milliliters" else (
                "portions" if self._preset == "produce" and habit["unit"] == "count" else "plain")
            presentation = {"step": self._values["step"], "icon": self._values["icon"],
                            "color": self._values["color"], "illustration": illustration}
            entry = self.config_entry
            api = HabitApi(async_get_clientsession(self.hass), entry.data["url"], entry.data["token"])
            try:
                await api.create_habit(habit, presentation, self._key)
            except Forbidden:
                errors["base"] = "write_forbidden"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
                entry.async_start_reauth(self.hass)
            except ApiError as err:
                errors["base"] = {404: "backend_outdated", 409: "creation_conflict", 422: "invalid_habit"}.get(err.status, "cannot_connect")
            except (aiohttp.ClientError, asyncio.TimeoutError):
                errors["base"] = "cannot_connect"
            else:
                # Creation is committed already; a failed refresh must not invite a duplicate.
                coordinator = getattr(entry, "runtime_data", None)
                if coordinator is not None:
                    await coordinator.async_refresh()
                self._created_name = habit["name"]
                return await self.async_step_created()
        values = self._values
        schema = vol.Schema({
            vol.Required("name", default=values["name"]): selector.TextSelector(),
            vol.Required("category", default=values["category"]): select(["mind", "daily", "sport", "nutrition"], "category"),
            vol.Required("kind", default=values["kind"]): select(["boolean", "quantity", "duration", "frequency"], "kind"),
            vol.Required("unit", default=values["unit"]): select(["count", "meters", "seconds", "milliliters"], "unit"),
            vol.Required("target", default=values["target"]): selector.NumberSelector(selector.NumberSelectorConfig(min=0.001, max=1e12, step="any", mode=selector.NumberSelectorMode.BOX)),
            vol.Required("period", default=values["period"]): select(["daily", "weekly"], "period"),
            vol.Required("step", default=values["step"]): selector.NumberSelector(selector.NumberSelectorConfig(min=0.001, max=1e12, step="any", mode=selector.NumberSelectorMode.BOX)),
            vol.Required("timezone", default=values["timezone"]): selector.TextSelector(),
        })
        return self.async_show_form(step_id="habit", data_schema=schema, errors=errors)

    async def async_step_created(self, user_input=None):
        return self.async_show_menu(step_id="created", menu_options=["preset", "custom", "finish"],
                                    description_placeholders={"name": self._created_name})

    async def async_step_finish(self, user_input=None):
        return self.async_create_entry(title="", data=dict(self.config_entry.options))
