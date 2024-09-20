from buspi.get_data import cycle_filters, get_next_departures, filter_departures, print_departures, Departure
import time
from buspi.lcddriver import lcd
from buspi.button import init_button, has_triggered
from datetime import datetime
from typing import Optional

REFRESH_FREQUENCY = 30

def should_display_be_lit(last_button_press: float) -> str:
  hour = datetime.now().hour
  bool_state = hour > 6 and hour < 22

  if time.time() - last_button_press < 60:
    bool_state = True

  return "on" if bool_state else "off"

def print_to_lcd(departures: list[Departure], filter_state: Optional[str], backlight_state: str, lcd_instance: lcd) -> None:
  """Formats and displays the departures on the LCD"""
  display = filter_departures(departures, filter_state)
  display = print_departures(display)

  if backlight_state == "on":
    for line in range(4):
      if len(display) > line:
        data = display[line]
      else:
        data = " " * 20
      lcd_instance.lcd_display_string(data, line+1)



def main():
  print("Starting buspi")
  init_button()
  state_iter = cycle_filters()
  filter_state = next(state_iter)
  button_state = False
  lcd_instance = lcd()
  backlight_state = "invalid"
  last_poll = time.time()
  last_button_press = time.time()
  departures = get_next_departures()
  
  try:
    while True:
      if time.time() - last_poll > REFRESH_FREQUENCY:
        last_poll = time.time()
        new_departures = get_next_departures()
        if len(new_departures):
          departures = new_departures
        print_to_lcd(departures, filter_state, backlight_state, lcd_instance)
      
      time.sleep(0.1)
      if has_triggered():
        if backlight_state == "on":
          filter_state = next(state_iter)
        print(f"Filter state {filter_state}")
        last_button_press = time.time()
        print_to_lcd(departures, filter_state, backlight_state, lcd_instance)
      
      cur_backlight = should_display_be_lit(last_button_press)
      if cur_backlight != backlight_state:
        print(f"Switching backlight to {cur_backlight}")
        backlight_state = cur_backlight
        lcd_instance.lcd_backlight(backlight_state)
        print_to_lcd(departures, filter_state, backlight_state, lcd_instance)
  finally:
    lcd_instance.lcd_clear()



if __name__ == "__main__":
  main()