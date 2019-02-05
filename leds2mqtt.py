import argparse
import configparser
import logging
import time
import paho.mqtt.client as mqtt

from leds.ws2801spirpi import LEDstripe

global client
global led

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

def on_log(client, userdata, level, buff):
    #otherwise we have silent exceptions
    logging.log(level, userdata+buff)

def notifyEnabledChange(enabled):
    if client:
        logging.info("pub LEDs " + str(enabled))
        client.publish('ledstripe/status', enabled)

def notifyRGBchange(color):
    color = ','.join(map(str, color))
    logging.info("pub LEDs RGB:" + color)
    client.publish('ledstripe/rgb/status', color)

def notifyBrightnessChange(perc):
    logging.info("pub LEDs brightness:" + perc)
    client.publish('ledstripe/brightness/status', int(perc* 100))

if __name__ == "__main__":
    global client
    global led
    client = None
    # init config
    conf = configparser.ConfigParser() 
    conf.read('leds2mqtt.conf')
    #anzahl leds
    # SPI Port und Device
    # MQTT server, user, pass
    # init CLI
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help="Print debugging statements",
        action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO,
    )
    parser.add_argument('-lt','--ledtest', help='Only selftest LED strip hardware', action='store_true')
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
    led.off()
    if  args['ledtest']:
        logging.info('LED test')
        led.blink()
        logging.info('LED test done')
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
        client.loop_forever()
