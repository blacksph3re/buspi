from buspi.get_data import cycle_filters, get_next_departures, filter_departures, print_departures
import time
from buspi.lcddriver import lcd
from buspi.button import init_button, has_triggered
from datetime import datetime

REFRESH_FREQUENCY = 30

def should_display_be_lit(last_button_press: float) -> str:
  hour = datetime.now().hour
  bool_state = hour > 6 and hour < 22

  if time.time() - last_button_press < 60:
    bool_state = True

  return "on" if bool_state else "off"


def main():
  print("Starting buspi")
  init_button()
  state_iter = cycle_filters()
  current_state = next(state_iter)
  button_state = False
  lcd_instance = lcd()
  backlight_state = "invalid"
  last_poll = time.time()
  last_button_press = time.time()
  departures = []
  
  try:
    while True:
      if time.time() - last_poll > REFRESH_FREQUENCY:
        new_departures = get_next_departures()
        if len(new_departures):
          departures = new_departures
        departures = filter_departures(departures, current_state)
        departures = print_departures(departures)

        if backlight_state == "on":
          for line in range(4):
            if len(departures) > line:
              data = departures[line]
            else:
              data = " " * 20
            lcd_instance.lcd_display_string(data, line+1)
        lcd_instance.lcd_backlight(backlight_state)
      
      time.sleep(0.1)
      if has_triggered():
        if backlight_state == "on":
          current_state = next(state_iter)
        print(f"Filter state {current_state}")
        last_button_press = time.time()
        last_poll = time.time() - REFRESH_FREQUENCY - 100
      
      cur_backlight = should_display_be_lit(last_button_press)
      if cur_backlight != backlight_state:
        print(f"Switching backlight to {cur_backlight}")
        backlight_state = cur_backlight
        lcd_instance.lcd_backlight(backlight_state)
  finally:
    lcd_instance.lcd_clear()



if __name__ == "__main__":
  main()