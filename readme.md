** (preALPHA) UNDER DEVELOPMENT **

Python3 MQTT client that listens for commands to control your WS2801 RGB ledstripe (aka Neopixel) if they are connected directly to your Rasberry PI SPI bus. You can light up individual LEDs, color the whole stripe, or playback effects and 1D animations.
Allows easy integration with home assistant and other smarthome solutions.

## Development

We use python3 virtualenv
* `sudo apt-get install python3 python3-pip virtualenvwrapper`
* `mkvirtualenv -p /usr/bin/python3 leds2mqtt`
* `workon leds2mqtt`
* `pip install adafruit-ws2801 RPi.GPIO`
