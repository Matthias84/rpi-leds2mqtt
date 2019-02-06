** (preALPHA) UNDER DEVELOPMENT **

Python3 MQTT client that listens for commands to control your WS2801 RGB ledstripe (aka Neopixel) if they are connected directly to your Rasberry PI SPI bus. You can light up individual LEDs, color the whole stripe, or playback effects and 1D animations.
Allows easy integration with home assistant and other smarthome solutions.

## Development

We use python3 virtualenv
* `sudo apt-get install python3 python3-pip virtualenvwrapper`
* `mkvirtualenv -p /usr/bin/python3 leds2mqtt`
* `workon leds2mqtt`
* `pip install adafruit-ws2801 RPi.GPIO paho-mqtt`

## NOT

* only 1D -> stripes
* only RGB stripes with single aderssable pixels

## Homeassistant

```yaml
light:
- platform: mqtt
    name: "Leuchtstreifen"
    state_topic: "ledstripe/status"
    command_topic: "ledstripe/set"
    brightness_command_topic: "ledstripe/brightness/set"
    brightness_scale: 100
    rgb_state_topic: "ledstripe/rgb/status"
    rgb_command_topic: "ledstripe/rgb/set"
    effect_list:
        - blink
        - dummy
    effect_command_topic: "ledstripe/effect/set"
    effect_state_topic: "ledstripe/effect/status"
    optimistic: true
```

## See also

Similar projects 

* [led there be light](https://github.com/rikvermeer/led_there_be_light) 2013 Python effect framework, only lpd8806  via Raspberry SPI
* [Open Websocket Ledstrip Server](https://github.com/ronbuist/owls) 2018 Python websocket service for Scratch IDE
* [rpi-ledstripe](https://github.com/nigeil/rpi-ledstrip) 2018 Python MQTT controlled but complete LEDs
* [ESP-MQTT-JSON-Digital-LEDs](https://github.com/bruhautomation/ESP-MQTT-JSON-Digital-LEDs) 2017 C, similar idea for ESP8266 boards
