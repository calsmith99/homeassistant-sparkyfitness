"""Sensor platform for SparkyFitness goals and progress."""
import asyncio
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from .sparky_api import SparkyFitnessAPI

SENSOR_TYPES = {
    # Goals and progress fields (water and exercise removed, but water intake current added)
    "calories": {"name": "Calories", "unit": "kcal"},
    "protein": {"name": "Protein", "unit": "g"},
    "carbs": {"name": "Carbohydrates", "unit": "g"},
    "fat": {"name": "Fat", "unit": "g"},
    "saturated_fat": {"name": "Saturated Fat", "unit": "g"},
    "polyunsaturated_fat": {"name": "Polyunsaturated Fat", "unit": "g"},
    "monounsaturated_fat": {"name": "Monounsaturated Fat", "unit": "g"},
    "trans_fat": {"name": "Trans Fat", "unit": "g"},
    "cholesterol": {"name": "Cholesterol", "unit": "mg"},
    "sodium": {"name": "Sodium", "unit": "mg"},
    "potassium": {"name": "Potassium", "unit": "mg"},
    "dietary_fiber": {"name": "Dietary Fiber", "unit": "g"},
    "sugars": {"name": "Sugars", "unit": "g"},
    "vitamin_a": {"name": "Vitamin A", "unit": "mcg"},
    "vitamin_c": {"name": "Vitamin C", "unit": "mg"},
    "calcium": {"name": "Calcium", "unit": "mg"},
    "iron": {"name": "Iron", "unit": "mg"},
    "water": {"name": "Water", "unit": "ml"},
}

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up SparkyFitness sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    token = data["token"]
    base_url = data["base_url"]
    user_id = data.get("user_id")
    api = SparkyFitnessAPI(base_url)

    async def async_update_data():
        goals = await api.async_get_goals_for_today(token)
        progress = {}
        water_intake = None
        from datetime import date
        today = date.today().isoformat()
        if user_id:
            progress = await api.async_get_progress_for_today(token, user_id)
            try:
                water_data = await api.async_get_water_intake(token, today)
                water_intake = float(water_data.get("water_ml", 0))
            except Exception:
                water_intake = None
        return {"goals": goals, "progress": progress, "water_intake": water_intake}

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="SparkyFitness goals and progress",
        update_method=async_update_data,
        update_interval=timedelta(minutes=15),
    )
    await coordinator.async_config_entry_first_refresh()

    sensors = []
    for key, meta in SENSOR_TYPES.items():
        if key == "water":
            sensors.append(SparkyFitnessWaterIntakeSensor(coordinator, key, meta))
            sensors.append(SparkyFitnessSensor(coordinator, "water_goal_ml", meta, "goals"))
        else:
            sensors.append(SparkyFitnessSensor(coordinator, key, meta, "goals"))
            sensors.append(SparkyFitnessSensor(coordinator, key, meta, "progress"))
    async_add_entities(sensors)

class SparkyFitnessWaterIntakeSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, meta):
        super().__init__(coordinator)
        self._key = key
        self._meta = meta
        self._attr_name = f"{meta['name']} Current"
        self._attr_native_unit_of_measurement = meta["unit"]
        self._attr_unique_id = f"sparkyfitness_water_intake_current"

    @property
    def native_value(self):
        return self.coordinator.data.get("water_intake")

    @property
    def available(self):
        return self.coordinator.data.get("water_intake") is not None

class SparkyFitnessSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, meta, source):
        super().__init__(coordinator)
        self._key = key
        self._meta = meta
        self._source = source  # 'goals' or 'progress'
        if source == "goals":
            self._attr_name = f"{meta['name']} Goal"
        else:
            self._attr_name = f"{meta['name']} Current"
        self._attr_native_unit_of_measurement = meta["unit"]
        self._attr_unique_id = f"sparkyfitness_{source}_{key}"

    @property
    def native_value(self):
        return self.coordinator.data.get(self._source, {}).get(self._key)

    @property
    def available(self):
        return self.coordinator.data is not None and self._key in self.coordinator.data.get(self._source, {})

import logging
_LOGGER = logging.getLogger(__name__)
