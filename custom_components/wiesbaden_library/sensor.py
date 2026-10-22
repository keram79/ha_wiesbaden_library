from datetime import datetime, timedelta
import logging
from bs4 import BeautifulSoup
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
import requests
from .const import CONF_AUSWEIS, CONF_PWD, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
  ausweis = entry.data[CONF_AUSWEIS]
  pwd = entry.data[CONF_PWD]

  async def async_update_data():
    # Scraping in den Executor auslagern, da blockierend
    return await hass.async_add_executor_job(
        fetch_library_data, ausweis, pwd
    )

  coordinator = DataUpdateCoordinator(
      hass,
      _LOGGER,
      name="wiesbaden_library_coordinator",
      update_method=async_update_data,
      update_interval=timedelta(hours=6),
  )

  await coordinator.async_config_entry_first_refresh()
  async_add_entities([WiesbadenLibrarySensor(coordinator)])


def fetch_library_data(ausweis, pwd):
  session = requests.Session()
  BASE_URL = "https://bond.wiesbaden.de/webopac/"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"
          " (KHTML, like Gecko) Version/27.0.1 Safari/605.1.15"
      ),
      "Referer": BASE_URL + "index.asp?kontofenster=start",
  }

  try:
    session.get(BASE_URL + "index.asp?kontofenster=start", headers=headers)
    login_url = BASE_URL + "index.asp"
    login_payload = {
        "kontofenster": "true",
        "AUSWEIS": ausweis,
        "PWD": pwd,
        "B1": "   weiter   ",
        "target": "konto",
        "type": "K",
    }
    session.post(
        login_url, data=login_payload, headers=headers, allow_redirects=True
    )
    konto_url = BASE_URL + "index.asp?kontofenster=true&target=konto"
    konto_response = session.get(konto_url, headers=headers)

    soup = BeautifulSoup(konto_response.text, "html.parser")
    loans = []

    for row in soup.select("tr.tabKonto"):
      cols = row.find_all("td")
      if len(cols) >= 3:
        author = cols[0].text.strip()
        title = cols[1].text.strip()
        due_date_raw = cols[2].text.strip()
        branch = cols[5].text.strip() if len(cols) > 5 else ""

        if author == "..." or not author:
          author = ""

        if due_date_raw:
          dt_obj = datetime.strptime(due_date_raw, "%d.%m.%Y")
          iso_date = dt_obj.strftime("%Y-%m-%d")
          loans.append({
              "author": author,
              "title": title,
              "due_date": due_date_raw,
              "due_date_iso": iso_date,
              "branch": branch,
          })

    next_due_iso = "unknown"
    branches_list = []
    if loans:
      sorted_loans = sorted(
          loans, key=lambda x: datetime.strptime(x["due_date"], "%d.%m.%Y")
      )
      next_due_iso = sorted_loans[0]["due_date_iso"]
      branches_list = sorted(list(set(b["branch"] for b in loans if b["branch"])))

    return {
        "state": next_due_iso,
        "branches": branches_list,
        "total_books": len(loans),
        "books": loans,
    }
  except Exception as e:
    _LOGGER.error("Fehler beim Abrufen der Bibliotheksdaten: %s", e)
    return None


class WiesbadenLibrarySensor(CoordinatorEntity, SensorEntity):

  def __init__(self, coordinator):
    super().__init__(coordinator)
    self._attr_name = "Stadtbibliothek Nächste Rückgabe"
    self._attr_unique_id = "wiesbaden_library_next_due"
    self._attr_icon = "mdi:bookshelf"
    self._attr_device_class = "date"

  @property
  def native_value(self):
    if self.coordinator.data:
      return self.coordinator.data.get("state")
    return None

  @property
  def extra_state_attributes(self):
    if self.coordinator.data:
      return {
          "branches": self.coordinator.data.get("branches"),
          "total_books": self.coordinator.data.get("total_books"),
          "books": self.coordinator.data.get("books"),
      }
    return {}
