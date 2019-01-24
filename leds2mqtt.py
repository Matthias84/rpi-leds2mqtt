import time
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
ledson = 42 # debouncing HASS repeated ON commands


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
    if msg.topic == 'ledstripe/rgb/set' :
        print("LEDs RGB:" + msg.payload.decode())
        rgb = msg.payload.decode().split(',')
        leds_rgb(int(rgb[0]),int(rgb[1]),int(rgb[2]))
        

def leds_off():
    global ledson
    ledson = False
    pixels.clear()
    pixels.show()

def leds_on():
    global ledson
    ledson = True
    pixels.set_pixels(Adafruit_WS2801.RGB_to_color(0,0,64))
    pixels.show()

def leds_rgb(r,g,b):
    pixels.set_pixels(Adafruit_WS2801.RGB_to_color(r,g,b))
    pixels.show()

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
