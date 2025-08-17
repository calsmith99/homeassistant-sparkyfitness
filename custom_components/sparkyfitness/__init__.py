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
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
