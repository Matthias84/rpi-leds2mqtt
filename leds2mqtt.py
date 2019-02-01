import time
import paho.mqtt.client as mqtt

from leds.ws2801spirpi import leds_off, leds_on, leds_rgb, setBrightness

global client
global ledson
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
    global ledson
    print(msg.topic)
    print(msg.payload)
    if msg.topic == 'ledstripe/set' :
        print(ledson)
        if msg.payload.decode() == 'ON':
            print("LEDS on")
            if ledson == False:
                leds_on()
                ledson = True
                notifyEnabledChange(ledson)
        elif 'OFF':
            print("LEDS off")
            leds_off()
            ledson = False
            notifyEnabledChange(ledson)
    if msg.topic == 'ledstripe/brightness/set' :
        val = int(msg.payload.decode())
        if (val >= 0) and (val <= 100):
            val = val / 100.0
            print("LEDs brightness:" + str(val))
            setBrightness(val)
            notifyBrightnessChange(val)
        else:
            print("invalid value")
    if msg.topic == 'ledstripe/rgb/set' :
        print("LEDs RGB:" + msg.payload.decode())
        rgb = msg.payload.decode().split(',')
        leds_rgb(int(rgb[0]),int(rgb[1]),int(rgb[2]))
        notifyRGBchange()

def on_log(client, userdata, level, buff):
    print(userdata)
    print(buff)


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


if __name__ == "__main__":
    global client
    global ledson
    global brightness
    client = None
    ledson = False
    brightness = 1.0
    # Clear all the pixels to turn them off.
    leds_off()
    #blink_color(pixels, blink_times = 2, wait=1.0, color=(0, 255, 0))
    # init MQTT
    client = mqtt.Client()
    client.on_log = on_log
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.username_pw_set('homeassistant', 'hello')
    client.connect("localhost", 1883, 60)
    leds_off()
    client.loop_forever()
