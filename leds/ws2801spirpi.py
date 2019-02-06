import colorsys
import logging
import time

import RPi.GPIO as GPIO
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI


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

#blink_color(pixels, blink_times = 2, wait=1.0, color=(0, 255, 0))
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

class LEDstripe():
    """LED control logic for WS2801 based LED stripsets connected via SPI on a Raspberry PI"""
    
    def __init__(self, port, device, pixel, color, brightness):
        self.data = []
        self.enabled = True # debouncing HASS repeated ON commands
        self.brightness = brightness
        if type(color) == str:
            color = color.split(',')
            color[0] = int(color[0])
            color[1] = int(color[1])
            color[2] = int(color[2])
        self.color = color
        # hardware init
        SPI_PORT   = port # Alternatively specify a hardware SPI connection on /dev/spidev0.0:
        SPI_DEVICE = device
        PIXEL_COUNT = pixel
        self.pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)
        time.sleep(0.1)
        self.off()

    def off(self):
        logging.debug("Turn LED off (from {})".format(self.enabled))
        if self.enabled: 
            self.pixels.clear()
            self.pixels.show()
            self.enabled = False 

    def on(self):
        logging.debug("Turn LED on (from {})".format(self.enabled))
        if not self.enabled:
            self.pixels.set_pixels(Adafruit_WS2801.RGB_to_color(self.color[0], self.color[1], self.color[2]))
            self.pixels.show()
            self.enabled = True 
    
    def rgb(self, r,g,b):
        self.color = r,g,b
        r = int(GAMMA_LUT[r] * self.brightness)
        g = int(GAMMA_LUT[g] * self.brightness)
        b = int(GAMMA_LUT[b] * self.brightness)
        logging.debug("calc x{}: R{} G{} B{}".format(self.brightness, r, g, b))
        self.pixels.set_pixels(Adafruit_WS2801.RGB_to_color(r,g,b))
        self.pixels.show()
    
    def setBrightness(self, perc):
        logging.debug("LEDs brightness perc:" + str(perc))
        if (perc >= 0.0) and (perc <=1.0):
            self.brightness = perc
            if self.enabled:
                self.rgb(self.color[0], self.color[1], self.color[2])
            else:
                logging.error("Invalid brightness:" + str(perc))

    def blink(self, times=3):
        logging.info("blink stripe {} times (current color)".format(times))
        for x in range(times):
            self.on()
            time.sleep(0.5)
            self.off()
            time.sleep(0.5)
