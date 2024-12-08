import paho.mqtt.client as mqtt
import time
import json
import logging
import datetime as dt
import nodens.gateway as nodens
from nodens.gateway import nodens_fns as ndns_fns
from time import sleep as sleep

global TB_CONNECT
global TB_MSG_RX
global FLAG_TX_IN_PROGRESS

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
    nodens.logger.debug("THINGSBOARD: on_publish: result {}. userdata: {}".format(result, userdata))

def on_message_tb(client, userdata, msg):
    nodens.logger.info('THINGSBOARD: on_message_tb: userdata {}, msg {}'.format(userdata, msg.payload.decode('utf-8')))
    client.user_data_set(msg.payload.decode("utf-8"))

def on_message_config_tb(client, userdata, msg):
    global TB_MSG_RX
    nodens.logger.info(f"THINGSBOARD: CONFIG: on_message_config_tb: userdata {userdata}, msg {msg.payload.decode('utf-8')}")
    ndns_fns.sm.update_with_received_config(msg.payload.decode('utf-8'))
    TB_MSG_RX = 1
    nodens.logger.info(f"THINGSBOARD: CONFIG: TB_MSG_RX: {TB_MSG_RX}")


class tb:
    def __init__(self):
        global FLAG_TX_IN_PROGRESS

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

        self.req_id = []

        FLAG_TX_IN_PROGRESS = 0

    def get_sensors(self, file):
        with open(file) as f:
            json_data = json.load(f)

        for i in range(len(json_data)):
            self.sensor_id.append(json_data[i]["sensor_id"])
            self.access_token.append(json_data[i]["access_token"])
            self.req_id.append(0)
    
    def end(self):
        flag = 0
        while flag == 0:
            try:
                self.client.loop_stop()
                self.client.disconnect()
                flag = 1
            except Exception as e:
                nodens.logger.error(f"THINGSBOARD: end error: {e.args}")
                sleep(1)

    def connect(self):
        flag = 0
        while flag == 0:
            try:
                self.client.connect(nodens.cp.TB_HOST,nodens.cp.TB_PORT,nodens.cp.TB_KEEPALIVE)
                self.client.loop_start()
                flag = 1
            except Exception as e:
                nodens.logger.error(f"THINGSBOARD: connect error: {e.args}")
                sleep(1)

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

        # ~~~~~~~~~~~ BEHAVIOUR ~~~~~~~~~~~~~ #
        
        # Determine occupancy
        # if input_data['Number of Occupants'] > 0:
        #     self.payload["occupancy"] = "true"
        # else:
        #     self.payload["occupancy"] = "false"
        #self.payload["num_occupants"] = input_data['Number of Occupants']

        #self.payload["min_occupants"] = input_data['Minimum period occupancy']
        try:
            self.payload["max_occupancy"] = input_data['Maximum period occupancy']
            self.payload["avg_occupancy"] = input_data['Average period occupancy']
        except Exception as e:
            nodens.logger.error(f"THINGSBOARD: max/avg occupancy error: {e.args} for sensor: {input_data['addr']}")

        # Track ID - select tid with highest energy.
        
        # Occupant positions
        if int(self.payload["max_occupancy"]) > 0:
            try:
                self.payload["sensor_timestamp"] = f"{input_data['Sensor timestamp']}"

                # ~~~~~~~~~~~ Occupancy ~~~~~~~~~~~~~ #
                #temp = input_data['Occupancy Info'][0]
                self.payload["occupant_id"] = f"{input_data['Track id']}"
                self.payload["X"] = f"{input_data['X']:.2f}"
                self.payload["Y"] = f"{input_data['Y']:.2f}"
            except Exception as e:
                nodens.logger.error(f"THINGSBOARD: occupant error: {e.args} for sensor: {input_data['addr']}")

            try:
                # ~~~~~~~~~~~ ACTIVITY ~~~~~~~~~~~~~ #
                self.payload["dist_moved"] = f"{input_data['Distance moved']:.2f}"
                self.payload["was_active_this_period"] = input_data['Was active']
                # self.payload["most_inactive_track"] = input_data['Most inactive track']
                # self.payload["most_inactive_time"] = input_data['Most inactive time']

                # ~~~~~~~~~~~ SLEEP ~~~~~~~~~~~~~ #
                self.payload["rest_zone_presence"] = f"{input_data['Presence detected']}"

                # ~~~~~~~~~~~ GAIT ~~~~~~~~~~~~~ #
                self.payload["gait_distribution"] = f"{input_data['Gait distribution']}"
            except Exception as e:
                nodens.logger.error(f"THINGSBOARD: occupant error: {e.args} for sensor: {input_data['addr']}")
                try:
                    # ~~~~~~~~~~~ ACTIVITY ~~~~~~~~~~~~~ #
                    self.payload["dist_moved"] = f"{input_data['Distance moved']}"
                    self.payload["was_active_this_period"] = input_data['Was active']

                    # ~~~~~~~~~~~ SLEEP ~~~~~~~~~~~~~ #
                    self.payload["rest_zone_presence"] = f"{input_data['Presence detected']}"

                    # ~~~~~~~~~~~ GAIT ~~~~~~~~~~~~~ #
                    self.payload["gait_distribution"] = f"{input_data['Gait distribution']}"
                except Exception as e:
                    nodens.logger.error(f"THINGSBOARD: occupant error: {e.args} for sensor: {input_data['addr']}")

            

        # ~~~~~~~~~~~ ENERGY ~~~~~~~~~~~~~ #
        try:
            self.payload["track_ud_energy"] = f"{input_data['UD energy']:.2f}"
            self.payload["pc_energy"] = f"{input_data['PC energy']:.2f}"
        except Exception as e:
            nodens.logger.error(f"THINGSBOARD: energy error: {e.args} for sensor: {input_data['addr']}")
            try:
                self.payload["track_ud_energy"] = f"{input_data['UD energy']}"
                self.payload["pc_energy"] = f"{input_data['PC energy']}"
                nodens.logger.error(f"THINGSBOARD. track energy data: {input_data['UD energy']}. pc data: {input_data['PC energy']}. occupancy: {input_data['Average period occupancy']}")
            except:
                pass
        
        # ~~~~~~~~~~~ HEATMAP ~~~~~~~~~~~~~ #
        try:
            self.payload["room_occ_heatmap"] = f"{input_data['Occupancy heatmap']}"
        except Exception as e:
            nodens.logger.error(f"THINGSBOARD: heatmap error: {e.args} for sensor: {input_data['addr']}")
            try:
                nodens.logger.error(f"THINGSBOARD: heatmap data: {input_data['Occupancy heatmap']}. occupancy: {input_data['Average period occupancy']}")
            except:
                pass


                # self.payload["occ_1_X"] = "-"
                # self.payload["occ_1_Y"] = "-"
                # self.payload["most_inactive_track"] = "-"
                # self.payload["most_inactive_time"] = "-"
        # Don't send anything if no occupants.
        # else:

        #     self.payload["occ_1_X"] = "-"
        #     self.payload["occ_1_Y"] = "-"
        #     self.payload["most_inactive_track"] = "-"
        #     self.payload["most_inactive_time"] = "-"

        # ~~~~~~~~~~~ ACTIVITY ~~~~~~~~~~~~~ #
            
        # ~~~~~~~~~~~ VITAL SIGNS ~~~~~~~~~~~~~ #
            
        # ~~~~~~~~~~~ SLEEP ~~~~~~~~~~~~~ #
            
        # ~~~~~~~~~~~ DIAGNOSTICS ~~~~~~~~~~~~~ #

        # Full data
        try:
            if input_data['Full data flag'] == 0:
                self.payload["data_diagnostics"] = input_data['data'] 
            else:
                self.payload["data_diagnostics"] = input_data['data'] 
        except Exception as e:
            nodens.logger.error(f"THINGSBOARD: diagnostics error: {e.args} for sensor: {input_data['addr']}")   

        #nodens.logger.info(f"TB payload: {self.payload}")      # TEMP KZR
        
    def prepare_log(self, log_msg):
        # Initialize payload
        self.payload = {}

        # Populate payload
        # TODO: add different log types, e.g. commands, levels
        self.payload["log"] = log_msg

    def publish_config(self, sensor_id, config_payload):
        s_idx = self.sensor_id.index(sensor_id)
        username = self.access_token[s_idx]
        self.client.username_pw_set(username)

        # payload = ""
        # for config in config_payload:
        #     payload += config
        self.connect()

        json_message = json.dumps(config_payload)

        nodens.logger.info(f"THINGSBOARD PUBLISH CONFIG: {json_message} to {sensor_id} with {username}")
        ## Publish payload  then close connection ##
        flag = 0
        while flag == 0:
            try:
                self.client.publish(nodens.cp.TB_ATTRIBUTES_TOPIC, json_message, qos=1)
                flag = 1
            except Exception as e:
                nodens.logger.error(f"THINGSBOARD: multiline payload publish error: {e.args}")
                sleep(1)

        self.end()

    def get_config(self, sensor_id):
        global TB_CONNECT
        global TB_MSG_RX
        TB_MSG_RX = 0
        s_idx = self.sensor_id.index(sensor_id)
        username = self.access_token[s_idx]

        # Prepare config schema to retrieve
        sensor_config_schema = {
            "sensorID":"",
            "sensorPosition": "",
            "staticBoundaryBox": "",
            "boundaryBox": "",
            "presenceBoundaryBox":"",
            "compRangeBiasAndRxChanPhase":"",
            "profileCfg":"",
            "frameCfg":"",
            "dynamicRACfarCfg":"",
            "staticRACfarCfg":"",
            "dynamicRangeAngleCfg":"",
            "dynamic2DAngleCfg":"",
            "staticRangeAngleCfg":"",
            "fineMotionCfg":"",
            "gatingParam":"",
            "stateParam":"",
            "allocationParam":"",
            "trackingCfg":"",
            "publishRate":"",
            "fullData":"",
            "fullDataRate":""
            } 
        
        k = sensor_config_schema.keys()
        labels = ""
        for key in k:
            labels += f"{key},"

        payload = {
            "clientKeys":labels[:-1]
        }
        json_payload = json.dumps(payload)

        # Setup new mqtt client for config (attributes) check
        client_config = mqtt.Client()
        client_config.on_connect = on_connect_tb
        client_config.on_disconnect = on_disconnect_tb
        client_config.on_subscribe = on_subscribe_tb
        client_config.on_unsubscribe = on_unsubscribe_tb
        client_config.on_message = on_message_config_tb
        client_config.username_pw_set(username)

         # Connect and subscribe
        TB_CONNECT = 0
        client_config.connect(nodens.cp.TB_HOST,nodens.cp.TB_PORT,nodens.cp.TB_KEEPALIVE)
        client_config.loop_start()
        while TB_CONNECT == 0:
            sleep(1)
        client_config.subscribe(nodens.cp.TB_ATTRIBUTES_REQUEST_TOPIC, qos=1)
        
        
        while TB_MSG_RX == 0:
            while 1:
                j = 0 # check no
                client_config.publish(f"v1/devices/me/attributes/request/{self.req_id[s_idx]}", json_payload)
                while j < 3:
                    nodens.logger.warning(f"TB request req_id: {self.req_id[s_idx]} j: {j} TB_MSG_RX: {TB_MSG_RX}")
                    time.sleep(0.3)
                    if TB_MSG_RX == 1:
                        break
                    j+=1
                if TB_MSG_RX == 1:
                    break
                self.req_id[s_idx]+=1
        nodens.logger.warning("TB get_config unsub")
        client_config.unsubscribe("#")
        client_config.loop_stop()
        client_config.disconnect()
        nodens.logger.warning("TB get_config disconnect")
        




    def multiline_payload(self, sensor_id):
        global TB_CONNECT
        global FLAG_TX_IN_PROGRESS

        ## Disconnect and unsub from all sensor attribute subscriptions
        #  Then connect to client for sensor to publish ##
        try:
            while FLAG_TX_IN_PROGRESS == 1:
                sleep(0.1)
            FLAG_TX_IN_PROGRESS = 1
            for i in range(len(self.subscribed_sensors)):
                self.client_sub[i].loop_stop()
                self.client_sub[i].disconnect()
                self.client_sub[i].unsubscribe('#')
            s_idx = self.sensor_id.index(sensor_id)
            username = self.access_token[s_idx]
            self.client.username_pw_set(username)
            TB_CONNECT = 0
            T_temp = dt.datetime.now(dt.timezone.utc)
        except Exception as e:
            nodens.logger.error(f"THINGSBOARD: multiline payload initialise error: {e.args}")

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

        ## Prepare json payload to publish ##
        try:
            json_message = json.dumps(self.payload)
        except Exception as e:
            nodens.logger.error(f"THINGSBOARD multiline payload json error: {e.args}. Payload:{self.payload}")

        ## Publish payload  then close connection ##
        flag = 0
        while flag == 0:
            try:
                # nodens.logger.info(f"TB publish. {nodens.cp.TB_PUB_TOPIC} {json_message}")     # TEMP KZR
                self.client.publish(nodens.cp.TB_PUB_TOPIC, json_message, qos=1)
                flag = 1
            except Exception as e:
                try:
                    nodens.logger.error(f"THINGSBOARD: multiline payload publish error: {e.args}. json_message:{json_message}")
                except Exception as e:
                    nodens.logger.error(f"THINGSBOARD: multiline payload publish error: {e.args}")
                sleep(1)

        self.end()

        ## Resub to all sensor attribute subscriptions ##
        flag = 0
        while flag == 0:
            try:
                for i in range(len(self.subscribed_sensors)):
                    self.client_sub[i].connect(nodens.cp.TB_HOST,nodens.cp.TB_PORT,nodens.cp.TB_KEEPALIVE)
                    self.client_sub[i].loop_start()
                    self.client_sub[i].subscribe(nodens.cp.TB_ATTRIBUTES_TOPIC, qos=1)
                flag = 1
                FLAG_TX_IN_PROGRESS = 0
            except Exception as e:
                nodens.logger.error(f"THINGSBOARD: multiline payload finalise error: {e.args}. Topic: {nodens.cp.TB_ATTRIBUTES_TOPIC}. Sensor: {self.subscribed_sensors[i]}, {i}")
                sleep(1)

TB = tb()

