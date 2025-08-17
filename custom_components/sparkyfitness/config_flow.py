"""Config flow for SparkyFitness integration."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from .const import DOMAIN
from .sparky_api import SparkyFitnessAPI

class SparkyFitnessConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SparkyFitness."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            api = SparkyFitnessAPI(base_url=user_input["base_url"])
            try:
                token = await api.async_login(user_input["email"], user_input["password"])
            except Exception:
                errors["base"] = "auth_failed"
            else:
                return self.async_create_entry(title=user_input["email"], data={
                    "email": user_input["email"],
                    "token": token,
                    "base_url": user_input["base_url"]
                })
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("base_url", default="http://localhost:3004"): str,
                vol.Required("email"): str,
                vol.Required("password"): str,
            }),
            errors=errors,
        )
