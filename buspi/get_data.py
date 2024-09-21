import requests
from dataclasses import dataclass
from datetime import datetime
from dateutil import parser
from typing import Optional
from collections.abc import Iterator


# Berkaer Strasse/Breite Strasse
STOP = "900046301"
FILTERS = ["249", "110", "186", None]
SCREEN_LINES = 4

@dataclass
class Departure:
  direction: str
  line: str
  when: datetime
  delay: float

def cycle_filters() -> Iterator[Optional[str]]:
  """Returns a generator that infinitely cycles filters"""
  while True:
    for filter in FILTERS:
      yield filter


def parse_departure(departure: dict) -> Departure:
  """Parse a single departure from the API format"""
  plannedWhen = parser.parse(departure["plannedWhen"])
  when = parser.parse(departure["when"])
  delay = (when - plannedWhen).total_seconds() // 60

  return Departure(
    direction = departure["direction"],
    line = departure["line"]["name"],
    when = when,
    delay = delay
  )

def get_next_departures() -> list[Departure]:
  """Returns all departures at the globally defined stop"""

  try:
    res = requests.get(f"https://v6.vbb.transport.rest/stops/{STOP}/departures?results=50&duration=60")
    data = res.json()
    departures = [parse_departure(departure) for departure in data["departures"]]
    return departures
  except Exception as e:
    print(e)
    return []

def filter_departures(departures: list[Departure], filter: Optional[str]) -> list[Departure]:
  """Filters the departures to only return one line"""
  departures = [departure for departure in departures if departure.when > datetime.now(departure.when.tzinfo)]
  if filter is None:
    return departures
  return [departure for departure in departures if departure.line==filter]

def format_departure(departure: Departure) -> str:
  """Formats a departure so it can be displayed on the screen"""
  minutes_until_departure = (departure.when - datetime.now(departure.when.tzinfo)).total_seconds() // 60
  minutes_until_departure = min(minutes_until_departure, 99)
  minutes_until_departure = max(minutes_until_departure, -99)
  sign = " "
  if departure.delay > 2:
    sign = "+"
  if departure.delay > 5:
    sign = "*"
  if departure.delay > 10:
    sign = "#"
  if minutes_until_departure < 0:
    sign = "-"

  minutes_until_departure = abs(minutes_until_departure)

  return f"{departure.line.ljust(3)[:3]} {departure.direction.ljust(12)[:12]} {sign}{int(minutes_until_departure):02}"

def print_departures(departures: list[Departure]) -> list[str]:
  """Formats a list of departures"""
  if len(departures) > SCREEN_LINES:
    departures = departures[:SCREEN_LINES]
  
  return [format_departure(departure) for departure in departures]