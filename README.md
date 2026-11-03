# Habit Tracker for Home Assistant

**Your habits, progress rings and daily check-ins inside Home Assistant.**

English · [Français](README.fr.md)

This integration connects an existing Habit Tracker backend to Home Assistant.
It creates entities for your habits and includes a Lovelace card for category
rings, checkboxes, quantities, weekly comparisons and a 13-week heatmap.
Buttons record real backend events; changes arrive through a live SSE connection,
with a 60-second polling fallback.

The card is bundled and registered automatically when Lovelace resources are
managed through the HA UI. For YAML resources, use the declaration below.
No Mushroom cards or helper entities are required.

## Installation

### 1. Prepare the backend connection

You need:

- **Home Assistant 2026.10.2 or newer** and [HACS](https://www.hacs.dev/docs/use/).
- An existing Habit Tracker backend providing `/api/v1/dashboard` and
  `/api/v1/dashboard/events`, reachable from the HA server.
- A Habit Tracker PAT or service-account token with these scopes:

| Scope | Purpose |
| --- | --- |
| `habits:read` | Read habits and their settings |
| `statistics:read` | Read dashboard progress and history |
| `entries:write` | Check/uncheck habits and add/remove quantities |

Ask the backend administrator for its **base URL** and a token with a suitable
expiration. Use a Habit Tracker token, distinct from GitHub credentials or a
Home Assistant long-lived access token. Habits are created through the backend
API; this integration displays and updates them.

### 2. Add the repository in HACS

1. Open **HACS** in Home Assistant.
2. Open **⋮ → Custom repositories**.
3. Add this URL:

   ```text
   https://github.com/floriaaan/habit-tracker-ha
   ```

4. Select **Integration** as the type and click **Add**.
5. Find **Habit Tracker**, open it and download the latest release.
6. **Restart Home Assistant** to load the Python integration.

This single HACS entry includes both the integration and the card.

### 3. Configure Habit Tracker in Home Assistant

1. Go to **Settings → Devices & services → Add integration**.
2. Search for **Habit Tracker** and select it.
3. Fill in the connection form:

   | Field | Value |
   | --- | --- |
   | **API URL** | Backend base URL, without `/api/v1` |
   | **API token** | Habit Tracker token prepared in step 1 |
   | **Allow HTTP on a trusted local connection** | Enable only for a trusted local HTTP connection; HTTPS is the default |

4. Submit the form. HA checks the URL, token and read scopes before saving.
5. Open the integration's entities and find the **Dashboard** sensor. Its usual
   entity ID is `sensor.habit_tracker_dashboard`; copy the actual ID chosen by HA.

The URL must work **from the HA server**. `localhost` points to HA itself, and a
Docker-only hostname works only when the containers share its network. For HTTPS,
use a certificate trusted by HA. The integration does not follow redirects with
your token.

#### If Lovelace resources are managed in YAML

Version 0.1.2 registers the card as a Lovelace resource in UI/storage mode.
If your configuration uses `resource_mode: yaml`, add this entry to the existing
`lovelace` section in `configuration.yaml` instead:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /habit_tracker/frontend/0.1.2/habit-tracker-card.js
      type: module
```

Keep other resources. Reload Lovelace resources or restart HA, then reload your
browser. Update the version in this URL when upgrading; the integration never
rewrites your YAML files.

### 4. Add your first card

1. Reload your browser after configuring the integration.
2. Open an editable dashboard, or create one in **Settings → Dashboards**.
3. Choose **Edit dashboard → Add card → Manual**.
4. Paste this YAML, replacing the entity ID if necessary:

   ```yaml
   type: custom:habit-tracker-card
   entity: sensor.habit_tracker_dashboard
   mode: rings
   ```

5. Save the card. It displays the real progress of your backend habits.

For the complete layout, use [dashboard.yaml](custom_components/habit_tracker/www/dashboard.yaml)
in a new dashboard's **Raw configuration editor**, replacing the sensor ID throughout.
The file contains a full dashboard, including views and sections.

### 5. Choose the views you want

Add more manual cards with the same `entity` and one of these modes:

| `mode` | View |
| --- | --- |
| `rings` | Category rings and global score |
| `habits` | Habit groups, completion counters and checkboxes |
| `nutrition` | Hydration and nutrition quantities with +/− controls |
| `sport` | Sport goals and quantity controls |
| `weekly` | Current week compared with the previous week |
| `heatmap` | 13 weeks of real history |

For a filtered habit group:

```yaml
type: custom:habit-tracker-card
entity: sensor.habit_tracker_dashboard
mode: habits
category: mind
```

Category values are `mind`, `daily`, `sport` and `nutrition`. Icons, colors, ordering,
weights, quantity steps and reminders come from backend habit settings.
Setup is translated into English and French; the card's current labels are in French.

## Using the integration

HA creates a Dashboard sensor, a progress sensor per habit, switches for boolean
habits, and increment/decrement buttons for other habit types. New habits appear
automatically; archived habits become unavailable. The card uses these HA states
and calls `habit_tracker.perform_action`, without storing API credentials in Lovelace.

Checking/unchecking and +/− actions update backend entries and statistics. Removing
a quantity corrects or cancels manual entries; Strava entries are preserved.
The backend handles rest days, time zones, eligibility and idempotence. Notifications
require a separate outbound HA connector configuration on the backend.

## Updates

Install updates from HACS, restart HA, then fully reload the browser.
In UI/storage resource mode, the registration is created or updated without
duplicates; for YAML resources, also update the versioned URL above. Existing config
entries and entity identifiers are preserved; habit data remains in the backend.
When moving from a manual card installation, remove the old
`/local/habit-tracker/habit-tracker-card.js?...` Lovelace resource so the bundled
card is the one loaded. Keep the existing integration entry.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Cannot connect | URL reachable from HA, base path, certificate and reverse proxy |
| Invalid authentication or failed actions | Token expiration/revocation and the three scopes above; use HA's reauthentication flow when prompted |
| Card type unknown | Integration configured and loaded, browser fully reloaded; card listed as a JavaScript Module in Lovelace resources; for YAML, add the declaration above |
| Empty or unavailable cards | Actual Dashboard entity ID, backend availability and habits created through its API |
| Updates delayed | SSE proxy buffering disabled and long connections allowed; polling falls back to every 60 seconds |

To unblock version **0.1.1**, manually add
`/habit_tracker/frontend/0.1.1/habit-tracker-card.js` as a **JavaScript Module**
resource under Settings → Dashboards → ⋮ → Resources, then reload your browser.
A 404 means the integration is not loaded, the version differs, or the proxy
blocks that path. Version 0.1.2 automatically replaces this resource in UI/storage mode.

Tokens are stored server-side in HA config entries. Protect `.storage` and backups,
and share habit entities only with HA users allowed to access that data. Excluding
the Dashboard sensor's large attributes from Recorder can avoid duplicate history
storage when the backend history is sufficient.

Manual installation is also possible: copy `custom_components/habit_tracker` into
HA's configuration directory and continue at the restart/configuration steps above.

MIT license — [LICENSE](LICENSE).
