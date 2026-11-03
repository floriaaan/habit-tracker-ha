"""Local Habit Tracker API integration."""
import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.const import LOVELACE_DATA, MODE_STORAGE
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import config_validation as cv
from homeassistant.loader import async_get_integration

from .api import HabitApi
from .const import DOMAIN, PLATFORMS
from .coordinator import HabitCoordinator

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Serve and load the bundled card once, shared by all config entries."""
    integration = await async_get_integration(hass, DOMAIN)
    card_url = f"/habit_tracker/frontend/{integration.version}/habit-tracker-card.js"
    await hass.http.async_register_static_paths([
        StaticPathConfig(card_url, str(Path(__file__).parent / "www/habit-tracker-card.js"), True)
    ])
    lovelace = hass.data[LOVELACE_DATA]
    if lovelace.resource_mode == MODE_STORAGE:
        resources = lovelace.resources
        await resources.async_get_info()
        existing = [item for item in resources.async_items()
                    if item["url"].split("?", 1)[0].startswith("/habit_tracker/frontend/")
                    and item["url"].split("?", 1)[0].endswith("/habit-tracker-card.js")]
        if existing:
            if existing[0]["url"] != card_url or existing[0]["type"] != "module":
                await resources.async_update_item(existing[0]["id"], {"url": card_url, "res_type": "module"})
            for duplicate in existing[1:]:
                await resources.async_delete_item(duplicate["id"])
        else:
            await resources.async_create_item({"url": card_url, "res_type": "module"})
    else:
        _LOGGER.warning("Lovelace resources use YAML: add %s as type: module under lovelace.resources, then reload resources", card_url)
    return True


async def async_setup_entry(hass, entry):
    api = HabitApi(async_get_clientsession(hass), entry.data["url"], entry.data["token"])
    coordinator = HabitCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    coordinator.start()
    return True


async def async_unload_entry(hass, entry):
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False
    await entry.runtime_data.stop()
    return True
