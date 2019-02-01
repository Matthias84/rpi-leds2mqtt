import time
import colorsys
import paho.mqtt.client as mqtt

import RPi.GPIO as GPIO
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI

# Configure the count of pixels:
PIXEL_COUNT = 64

# Alternatively specify a hardware SPI connection on /dev/spidev0.0:
SPI_PORT   = 0
SPI_DEVICE = 0
pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)
ledson = True # debouncing HASS repeated ON commands

# https://learn.adafruit.com/led-tricks-gamma-correction/the-quick-fix
# Avoid to bright colors
GAMMA_LUT = [    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
   10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
   17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
   25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
   37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
   51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
   69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
   90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
  115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
  144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
  177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
  215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255]

global client
global brightness

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    """
    0: Connection successful
    1: Connection refused - incorrect protocol version
    2: Connection refused - invalid client identifier
    3: Connection refused - server unavailable
    4: Connection refused - bad username or password
    5: Connection refused - not authorised
    6-255: Currently unused."""
    client.subscribe("ledstripe/#")

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
    global brightness
    print(msg.topic)
    print(msg.payload)
    if msg.topic == 'ledstripe/set' :
        print(ledson)
        if msg.payload.decode() == 'ON':
            print("LEDS on")
            if ledson == False:
                leds_on()
        elif 'OFF':
            print("LEDS off")
            leds_off()
    if msg.topic == 'ledstripe/brightness/set' :
        val = int(msg.payload.decode())
        if (val >= 0) and (val <= 100):
            val = val / 100.0
            print("LEDs brightness:" + str(val))
            setBrightness(val)
        else:
            print("invalid value")
    if msg.topic == 'ledstripe/rgb/set' :
        print("LEDs RGB:" + msg.payload.decode())
        rgb = msg.payload.decode().split(',')
        leds_rgb(int(rgb[0]),int(rgb[1]),int(rgb[2]))

def notifyEnabledChange(enabled):
    if client:
        print("pub LEDs " + str(enabled))
        if enabled==True:
            enabled="on"
        else: "off"
        client.publish('ledstripe/status', enabled)

def notifyRGBchange(color):
    color = ','.join(map(str, color))
    print("pub LEDs RGB:" + color)
    client.publish('ledstripe/rgb/status', color)

def notifyBrightnessChange(perc):
    client.publish('ledstripe/brightness/status', int(perc* 100))


def leds_off():
    global ledson
    ledson = False
    notifyEnabledChange(ledson)
    pixels.clear()
    pixels.show()

def leds_on():
    global ledson
    ledson = True
    notifyEnabledChange(ledson)
    pixels.set_pixels(Adafruit_WS2801.RGB_to_color(1,25,10))
    pixels.show()

def leds_rgb(r,g,b):
    r = int(GAMMA_LUT[r] * brightness)
    g = int(GAMMA_LUT[g] * brightness)
    b = int(GAMMA_LUT[b] * brightness)
    print("calc x{}: R{} G{} B{}".format(brightness, r,g,b))
    pixels.set_pixels(Adafruit_WS2801.RGB_to_color(r,g,b))
    pixels.show()
    notifyRGBchange()

def setBrightness(perc):
    global brightness
    print("LEDs brightness oerc:" + str(perc))
    if (perc >= 0.0) and (perc <=1.0):
        notifyBrightnessChange(perc)
        brightness = perc


def blink_color(pixels, blink_times=5, wait=0.5, color=(255,0,0)):
    for i in range(blink_times):
        # blink two times, then wait
        pixels.clear()
        for j in range(2):
            for k in range(pixels.count()):
                pixels.set_pixel(k, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2] ))
            pixels.show()
            time.sleep(0.08)
            pixels.clear()
            pixels.show()
            time.sleep(0.08)
        time.sleep(wait)

if __name__ == "__main__":
    global client
    client = None
    brightness = 1.0
    # Clear all the pixels to turn them off.
    leds_off()
    #blink_color(pixels, blink_times = 2, wait=1.0, color=(0, 255, 0))
    # init MQTT
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.username_pw_set('homeassistant', 'hello')
    client.connect("localhost", 1883, 60)
    leds_off()
    client.loop_forever()
