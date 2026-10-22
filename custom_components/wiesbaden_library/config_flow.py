import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import CONF_AUSWEIS, CONF_PWD, DOMAIN


class WiesbadenLibraryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
  """Config flow for Wiesbaden Library."""

  VERSION = 1

  async def async_step_user(self, user_input=None):
    errors = {}
    if user_input is not None:
      # Hier könnte man theoretisch einen Test-Login einbauen
      return self.async_create_entry(
          title=f"Ausweis {user_input[CONF_AUSWEIS]}", data=user_input
      )

    schema = vol.Schema(
        {vol.Required(CONF_AUSWEIS): str, vol.Required(CONF_PWD): str}
    )

    return self.async_show_form(
        step_id="user", data_schema=schema, errors=errors
    )
