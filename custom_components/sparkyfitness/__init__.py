"""SparkyFitness integration init."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = "sparkyfitness"

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration via yaml (not supported)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SparkyFitness from a config entry."""
    # Store the JWT token and email in hass.data for use by platforms
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data
    # Forward entry setup to sensor platform (modern HA)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    # Register service for logging water intake
    async def handle_log_water_intake(call):
        from .sparky_api import SparkyFitnessAPI
        import datetime
        data = hass.data[DOMAIN][entry.entry_id]
        token = data["token"]
        user_id = data["user_id"]
        base_url = data["base_url"]
        api = SparkyFitnessAPI(base_url)
        entry_date = datetime.date.today().isoformat()
        change_drinks = 1
        container_id = 1
        await api.async_log_water_intake(token, user_id, entry_date, change_drinks, container_id)

    hass.services.async_register(
        DOMAIN,
        "log_water_intake",
        handle_log_water_intake,
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
