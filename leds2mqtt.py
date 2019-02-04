import time
import paho.mqtt.client as mqtt

from leds.ws2801spirpi import LEDstripe

global client
global led

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
        if msg.payload.decode() == 'ON':
            print("LEDS on")
            led.on()
        elif 'OFF':
            print("LEDS off")
            led.off()
        notifyEnabledChange(led.enabled)
    if msg.topic == 'ledstripe/rgb/set' :
        print("LEDs RGB:" + msg.payload.decode())
        rgb = msg.payload.decode().split(',')
        led.rgb(int(rgb[0]),int(rgb[1]),int(rgb[2]))
        notifyRGBchange(rgb)
    if msg.topic == 'ledstripe/brightness/set' :
        val = int(msg.payload.decode())
        if (val >= 0) and (val <= 100):
            val = val / 100.0
            print("LEDs brightness:" + str(val))
            led.setBrightness(val)
            notifyBrightnessChange(val)
        else:
            print("invalid value")

def on_log(client, userdata, level, buff):
    #otherwise we have silent exceptions
    print(userdata)
    print(buff)


def notifyEnabledChange(enabled):
    if client:
        print("pub LEDs " + str(enabled))
        client.publish('ledstripe/status', enabled)

def notifyRGBchange(color):
    color = ','.join(map(str, color))
    print("pub LEDs RGB:" + color)
    client.publish('ledstripe/rgb/status', color)

def notifyBrightnessChange(perc):
    client.publish('ledstripe/brightness/status', int(perc* 100))

if __name__ == "__main__":
    global client
    global led
    client = None
    # init MQTT
    client = mqtt.Client()
    client.on_log = on_log
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.username_pw_set('homeassistant', 'hello')
    client.connect("localhost", 1883, 60)
    # init LEDs
    led = LEDstripe()
    print(led.color)
    led.on()
    client.loop_forever()
