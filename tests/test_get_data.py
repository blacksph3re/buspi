from buspi.get_data import get_next_departures, filter_departures, print_departures

def test_get_next_departures() -> None:
  departures = get_next_departures()
  assert len(departures)