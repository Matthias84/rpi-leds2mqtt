import argparse
import configparser
import logging
import time
import paho.mqtt.client as mqtt

from leds.ws2801spirpi import LEDstripe

global client
global led
global effect

bool2mqtt = {True: "ON", False: "OFF"}

def on_connect(client, userdata, flags, rc):
    logging.debug("Connected with result code " + str(rc))
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
    logging.debug("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
    global effect
    logging.debug("MESSAGE: "+str(msg.topic)+" "+str(msg.payload))
    if msg.topic == 'ledstripe/set' :
        if msg.payload.decode() == 'ON':
            logging.info("LEDS on")
            led.on()
        elif 'OFF':
            logging.info("LEDS off")
            led.off()
        notifyEnabledChange(led.enabled)
    if msg.topic == 'ledstripe/rgb/set' :
        logging.info("LEDs RGB:" + msg.payload.decode())
        rgb = msg.payload.decode().split(',')
        led.rgb(int(rgb[0]),int(rgb[1]),int(rgb[2]))
        notifyRGBchange(rgb)
    if msg.topic == 'ledstripe/brightness/set' :
        val = int(msg.payload.decode())
        if (val >= 0) and (val <= 100):
            val = val / 100.0
            logging.info("LEDs brightness:" + str(val))
            led.setBrightness(val)
            notifyBrightnessChange(val)
        else:
            logging.error("invalid brightness value")
    if msg.topic == 'ledstripe/effect/set' :
        fx = str(msg.payload.decode())
        logging.info("LEDs effect:" + str(fx))
        if fx == 'blink':
            effect = 'blink'
            notifyEffectChange()
            led.blink()
        if fx == 'flash':
            effect = 'flash'
            notifyEffectChange()
            led.flash()
        effect = None
        notifyEffectChange()

def on_log(client, userdata, level, buff):
    #otherwise we have silent exceptions
    logging.log(level, userdata+'-'+buff)

def notifyEnabledChange(enabled):
    if client:
        enabled = bool2mqtt[enabled]
        logging.info("pub LEDs " + str(enabled))
        client.publish('ledstripe/status', enabled)

def notifyRGBchange(color):
    color = ','.join(map(str, color))
    logging.info("pub LEDs RGB:" + color)
    client.publish('ledstripe/rgb/status', color)

def notifyBrightnessChange(perc):
    logging.info("pub LEDs brightness:" + perc)
    client.publish('ledstripe/brightness/status', int(perc* 100))

def notifyEffectChange():
    logging.info("pub LEDs effect:" + effect)
    client.publish('ledstripe/effect/status', effect)

if __name__ == "__main__":
    global client
    global led
    global effect
    client = None
    effect = None
    # init config
    conf = configparser.ConfigParser() 
    conf.read('leds2mqtt.conf')
    # init CLI
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help="Print debugging statements",
        action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO,
    )
    parser.add_argument('-lt','--ledtest', help='Only selftest LED strip hardware', action='store_true')
    parser.add_argument('-et','--effecttest', choices=['blink','flash'], action='store')
    args = vars(parser.parse_args())
    # init logging
    logging.basicConfig(format='%(asctime)s  %(levelname)s:%(message)s', level=args['loglevel'])
    # init LEDs
    logging.info('Enable LED stripe')
    led = LEDstripe(port = int(conf['leds']['port']),
                    device = int(conf['leds']['device']),
                    pixel = int(conf['leds']['pixel']),
                    color = conf['leds']['color'],
                    brightness = float(conf['leds']['brightness']))
    if  args['ledtest']:
        logging.info('LED test')
        led.blink()
        logging.info('LED test done')
    elif args['effecttest']:
        logging.info('Effect test ({})' + args['effecttest'])
        if args['effecttest'] == 'blink':
            led.blink()
        elif args['effecttest'] == 'flash':
            led.flash()
        logging.info('Effect test done')
    else:
        # init MQTT
        logging.info('Enable MQTT listener')
        client = mqtt.Client()
        client.on_log = on_log
        client.on_connect = on_connect
        client.on_subscribe = on_subscribe
        client.on_message = on_message
        client.username_pw_set(conf['mqtt']['user'], conf['mqtt']['password'])
        client.connect(conf['mqtt']['host'], 1883, 60)
        notifyEnabledChange(led.enabled)
        client.loop_forever()
