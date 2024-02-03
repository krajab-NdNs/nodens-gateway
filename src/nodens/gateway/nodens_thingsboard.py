import paho.mqtt.client as mqtt
import time
import json
import logging
import datetime as dt
import nodens.gateway as nodens
from nodens.gateway import nodens_fns as ndns_fns

global TB_CONNECT

def on_subscribe_tb(unused_client, unused_userdata, mid, granted_qos):
    nodens.logger.debug('THINGSBOARD: on_subscribe: mid {}, qos {}'.format(mid, granted_qos))

def on_connect_tb(client, userdata, flags, rc):
    global TB_CONNECT
    
    TB_CONNECT = 1
    nodens.logger.debug('THINGSBOARD: on_connect: {} userdata: {}. flags: {}. TB_CONNECT: {}.'.format(mqtt.connack_string(rc), userdata, flags, TB_CONNECT))
    

def on_disconnect_tb(client, userdata, rc):
    global TB_CONNECT
    
    TB_CONNECT = 0
    nodens.logger.debug('THINGSBOARD: on_disconnect: {}. userdata: {}. rc: {}. TB_CONNECT: {}.'.format(mqtt.connack_string(rc), userdata, rc, TB_CONNECT))
    
    
    if rc == 5:
        time.sleep(1)

def on_unsubscribe_tb(client, userdata, mid):
    nodens.logger.debug('THINGSBOARD: on_unsubscribe: mid {}. userdata: {}.'.format(mid, userdata))

def on_publish_tb(client,userdata,result):             #create function for callback
    nodens.logger.debug("THINGSBOARD: on_publish: result {}. userdata: {} \n".format(result, userdata))

def on_message_tb(client, userdata, msg):
    print("msg received")
    nodens.logger.info('THINGSBOARD: on_message: userdata {}, msg {}'.format(userdata, msg.payload.decode("utf-8")))
    client.user_data_set(msg.payload.decode("utf-8"))

class tb:
    def __init__(self):
        self.client = mqtt.Client()

        self.client.on_connect = on_connect_tb
        self.client.on_disconnect = on_disconnect_tb
        self.client.on_subscribe = on_subscribe_tb
        self.client.on_unsubscribe = on_unsubscribe_tb
        self.client.on_publish = on_publish_tb

        self.sensor_id = []
        self.access_token = []
        self.subscribed_sensors = []
        self.client_sub = []

        self.message = []

    def get_sensors(self, file):
        with open(file) as f:
            json_data = json.load(f)

        for i in range(len(json_data)):
            self.sensor_id.append(json_data[i]["sensor_id"])
            self.access_token.append(json_data[i]["access_token"])
    
    def end(self):
        self.client.loop_stop()
        self.client.disconnect()

    def connect(self):
        self.client.connect(nodens.cp.TB_HOST,nodens.cp.TB_PORT,nodens.cp.TB_KEEPALIVE)
        self.client.loop_start()

    def subscribe_to_attributes(self, connected_sensors):
        for sensors in connected_sensors:
            if sensors not in self.subscribed_sensors:
                # Check index of new sensor to subscribe
                s_idx = self.sensor_id.index(sensors)
                self.subscribed_sensors.append(sensors)
                c_idx = self.subscribed_sensors.index(sensors)
                username = self.access_token[s_idx]

                # Initialise userdata (to pass on received messages ,etc.)
                client_message = []

                # Subscribe to new sensors
                self.client_sub.append(mqtt.Client(userdata=client_message))

                self.client_sub[c_idx].on_connect = on_connect_tb
                self.client_sub[c_idx].on_disconnect = on_disconnect_tb
                self.client_sub[c_idx].on_subscribe = on_subscribe_tb
                self.client_sub[c_idx].on_unsubscribe = on_unsubscribe_tb
                self.client_sub[c_idx].on_message = on_message_tb

                self.client_sub[c_idx].username_pw_set(username)
                self.client_sub[c_idx].connect(nodens.cp.TB_HOST,nodens.cp.TB_PORT,nodens.cp.TB_KEEPALIVE)
                self.client_sub[c_idx].loop_start()

                self.client_sub[c_idx].subscribe(nodens.cp.TB_ATTRIBUTES_TOPIC, qos=1)
                

                nodens.logger.info('THINGSBOARD: ...subscribed')
        # Check connected sensors -> check active sensors (active within time T)
        # Subscribe to connected sensors
        # Similar procedure for gateway?

    def prepare_data(self, input_data):
        # Initialize payload
        self.payload = {}
        
        # Determine occupancy
        if input_data['Number of Occupants'] > 0:
            self.payload["occupancy"] = "true"
        else:
            self.payload["occupancy"] = "false"
        self.payload["num_occupants"] = input_data['Number of Occupants']
        self.payload["avg_occupants"] = input_data['Average period occupancy']
        self.payload["max_occupants"] = input_data['Maximum period occupancy']
        
        # Occupant positions
        if self.payload["num_occupants"] > 0:
            try:
                temp = input_data['Occupancy Info'][0]
                self.payload["occ_1_X"] = temp['X']
                self.payload["occ_1_Y"] = temp['Y']

                # Activity statistics
                self.payload["most_inactive_track"] = input_data['Most inactive track']
                self.payload["most_inactive_time"] = input_data['Most inactive time']

            except:
                nodens.logger.debug("THINGSBOARD: occupant error")
                self.payload["occ_1_X"] = "-"
                self.payload["occ_1_Y"] = "-"
                self.payload["most_inactive_track"] = "-"
                self.payload["most_inactive_time"] = "-"
        else:
            self.payload["occ_1_X"] = "-"
            self.payload["occ_1_Y"] = "-"
            self.payload["most_inactive_track"] = "-"
            self.payload["most_inactive_time"] = "-"

        

        # Full data
        self.payload["data_diagnostics"] = input_data['data']      
        
    def prepare_log(self, log_msg):
        # Initialize payload
        self.payload = {}

        # Populate payload
        # TODO: add different log types, e.g. commands, levels
        self.payload["log"] = log_msg

    def multiline_payload(self, sensor_id):
        global TB_CONNECT
        for i in range(len(self.subscribed_sensors)):
            self.client_sub[i].loop_stop()
            self.client_sub[i].disconnect()
            self.client_sub[i].unsubscribe('#')
        s_idx = self.sensor_id.index(sensor_id)
        username = self.access_token[s_idx]
        self.client.username_pw_set(username)
        TB_CONNECT = 0
        T_temp = dt.datetime.now(dt.timezone.utc)
        self.connect()
        # while TB_CONNECT == 0:
        #     if (dt.datetime.now(dt.timezone.utc) - T_temp).seconds > 60:
        #         self.end()
        #         print("Wait 60s [T_temp: {}. T: {}]...".format(T_temp, dt.datetime.now(dt.timezone.utc)), end='')
        #         time.sleep(5)
        #         self.connect()
        #         print("TB_CONNECT: {}".format(TB_CONNECT))
        #     else:
        #         time.sleep(1)

        json_message = json.dumps(self.payload)
        self.client.publish(nodens.cp.TB_PUB_TOPIC, json_message, qos=1)
        self.end()

        for i in range(len(self.subscribed_sensors)):
            self.client_sub[i].connect(nodens.cp.TB_HOST,nodens.cp.TB_PORT,nodens.cp.TB_KEEPALIVE)
            self.client_sub[i].loop_start()
            self.client_sub[i].subscribe(nodens.cp.TB_ATTRIBUTES_TOPIC, qos=1)

TB = tb()

