import paho.mqtt.client as mqtt
import time
import json
import logging
import datetime as dt
import nodens.gateway as nodens

global reconnect_backoff

global CONNECT_STATE_7

CONNECT_STATE_7 = 1

def on_subscribe(unused_client, unused_userdata, mid, granted_qos):
    nodens.logger.debug('MESH: on_subscribe: mid {}, qos {}'.format(mid, granted_qos))

def on_connect(client, userdata, flags, rc):
    nodens.logger.debug('MESH: on_connect: {} userdata: {}. flags: {}. rc: {}. datetime: {}.'
                  .format(mqtt.connack_string(rc), userdata, flags, rc, dt.datetime.now(dt.timezone.utc)))
    client.connect_status = 1

def on_disconnect(client, userdata, rc):
    nodens.logger.debug('MESH: on_disconnect: {} userdata: {}. rc: {}. datetime: {}.'
                  .format(mqtt.connack_string(rc), userdata, rc, dt.datetime.now(dt.timezone.utc)))
    CONNECT_STATE_7 = 1

    if rc == 5:
        time.sleep(1)
    elif rc == 7:
        CONNECT_STATE_7 = 0
        client.connect_status = 0
        nodens.logger.debug("CONNECT_STATE_7 update")
    elif rc == 16:
        CONNECT_STATE_7 = 0
        client.connect_status = 0
        nodens.logger.debug("CONNECT_STATE_7 update")            

def on_unsubscribe(client, userdata, mid):
    nodens.logger.debug('MESH: on_unsubscribe: mid {}. userdata: {}.'.format(mid, userdata))

class mesh:
    def __init__(self):
        self.client = mqtt.Client()

        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_subscribe = on_subscribe
        self.client.on_unsubscribe = on_unsubscribe

        self.status = self.Status()
        
        self.client.connect_status = 1

    def end(self):
        nodens.logger.debug("MESH: end()...")
        self.client.loop_stop()
        self.client.unsubscribe('#')
        self.client.disconnect()
        nodens.logger.debug("MESH: end done")

    def connect(self, ip, port, timeout, topic, cb):
        nodens.logger.debug("MESH: connect()")
        self.client.message_callback_add(topic, cb)
        self.client.connect(ip,port,timeout)
        self.client.subscribe(topic)
        self.client.loop_start()
        nodens.logger.debug("MESH: connect done")

    def reconnect(self, ip, port, timeout, topic, cb):
        nodens.logger.debug("MESH: reconnect()")
        self.end()
        time.sleep(1)
        if CONNECT_STATE_7 == 1:
            self.client.connect(ip, port, timeout)
        else:
            nodens.logger.debug("MESH: connect for rc=7")
            self.connect(ip, port, timeout, topic, cb)
        nodens.logger.debug("MESH: reconnect done")

    def multiline_payload(self, ip, port, timeout, topic, cb, payload):
        #self.reconnect(ip, port, timeout, topic, cb)
        #time.sleep(2)
        for i in range(len(payload)):
            json_message = json.dumps(payload[i])
            nodens.logger.warning("CONFIG SEND: {}".format(json_message))
            self.client.publish(topic, json_message)
            time.sleep(0.1)
        # self.client.subscribe('#')
        # self.client.loop_start()
    
    class Status:
        def __init__(self):
            self.flag_connect = False
            self.flag_config_proc = False
            self.reset_history()
            self.reset_last_msg()
            self.reset_last_info()

        def reset_last_msg(self):
            self.last_msg = ''
            self.last_msg_timestamp = ''

        def reset_last_info(self):
            self.last_info = ''
            self.last_info_timestamp = ''
        
        def reset_history(self):         
            self.msg_history = []            
            self.msg_timestamp_history = []
            self.info_history = []            
            self.info_timestamp_history = []

        def receive_msg(self, payload, timestamp):
            self.last_msg = payload[5:]
            self.last_msg_timestamp = timestamp
            self.msg_history.insert(0,payload[5:])
            self.msg_timestamp_history.insert(0,timestamp)

        def receive_info(self, payload, timestamp, sensor_id):
            self.last_info = payload
            self.last_info_timestamp = timestamp
            self.info_history.insert(0,payload)
            self.info_timestamp_history.insert(0,timestamp)
            # nodens.logger.info("Info received: {} for sensor: {} at timestamp: {}".format(self.last_info, sensor_id, timestamp))

        def receive_cmd(self, payload, timestamp, sensor_id):
            self.commands = ["REQUEST VERSION", "REQUEST CONFIG", "PUBLISH RATE", "FULL DATA", "TI RESET"]
            self.last_cmd = payload[5:]
            self.last_cmd_num = -1

            # Check if received command matches
            for num,val in enumerate(self.commands):
                if self.last_cmd[:len(val)] == val:
                    self.last_cmd_num = num

            
            nodens.logger.info(f"Command verified: {payload} for sensor: {sensor_id} at timestamp: {timestamp}")



MESH = mesh()

## Commands received:

# Command verified: CMD: REQUEST VERSION
# Sensor information: VERSION: C02003B.R3D001B for Device: 7cdfa1016266

# Command verified: CMD: REQUEST CONFIG
# Sensor information: CONFIG: dfeDataOutputMode 1 for Device: 7cdfa1016266
# Sensor information: CONFIG: sensorStart for Device: 7cdfa1016266

# Command verified: CMD: PUBLISH RATE: 1

# Command verified: CMD: FULL DATA ON. RATE: 2.0
# Info received: Full data ON for sensor: 7cdfa1016266 at timestamp: 2024-06-18T14:47:39Z

# Command verified: CMD: TI RESET
# Info received: Sensor already running. Storing new config for sensor: 7cdfa1016266 at timestamp: 2024-06-18T14:47:42Z


## Info received:

# Sensor information: Sensor already running for Device: 7cdfa1016266
# Info received: Sensor already running for sensor: 7cdfa1016266 at timestamp: 2024-06-18T12:50:47Z
# Info received: ESP publish rate 5. Full data OFF for sensor: 7cdfa1016266 at timestamp: 2024-06-18T12:50:47Z
# Info received: Sensor Started for sensor: 7cdfa1016266 at timestamp: 2024-06-18T12:50:47Z
# Info received: Waiting for config for sensor: 7cdfa101721a at timestamp: 2024-06-18T09:04:34Z
# Info received: Using default config for sensor: 7cdfa101721a at timestamp: 2024-06-18T09:04:34Z
# Info received: Config sent to sensor for sensor: 7cdfa101721a at timestamp: 2024-06-18T09:04:38Z


