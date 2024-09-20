import RPi.GPIO as GPIO

BUTTON_CHANNEL = 40

def init_button() -> None:
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(BUTTON_CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.add_event_detect(BUTTON_CHANNEL, GPIO.RISING)

def has_triggered() -> bool:
  return bool(GPIO.event_detected(BUTTON_CHANNEL))
