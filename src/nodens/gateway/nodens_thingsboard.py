import paho.mqtt.client as mqtt
import time
import json
import logging
from datetime import datetime as dt
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
        s_idx = self.sensor_id.index(sensor_id)
        username = self.access_token[s_idx]
        self.client.username_pw_set(username)
        TB_CONNECT = 0
        T_temp = dt.utcnow()
        self.connect()
        # while TB_CONNECT == 0:
        #     if (dt.utcnow() - T_temp).seconds > 60:
        #         self.end()
        #         print("Wait 60s [T_temp: {}. T: {}]...".format(T_temp, dt.utcnow()), end='')
        #         time.sleep(5)
        #         self.connect()
        #         print("TB_CONNECT: {}".format(TB_CONNECT))
        #     else:
        #         time.sleep(1)

        json_message = json.dumps(self.payload)
        self.client.publish(nodens.cp.TB_PUB_TOPIC, json_message, qos=1)
        self.end()

TB = tb()

