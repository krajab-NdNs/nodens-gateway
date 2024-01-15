#!/usr/bin/python3
#print('nodens step0')

# Copyright NodeNs Medical Ltd. Author: Khalid Rajab, khalid@nodens.eu
# Functionality to connect to Siemens MindSphere MindConnect MQTT

import numpy as np
import paho.mqtt.client as mqtt
import datetime
from time import sleep
from random import randint,random, uniform
import json
import logging, traceback
import ssl
import os
from pathlib import Path

import nodens.gateway as nodens

global CONNECTION_ON

CONNECTION_ON = 0

## ~~~ MQTT client functionality ~~~ ##

def on_publish_MS(client,userdata,result):             #create function for callback
    i=1
    pass

def on_subscribe_MS(unused_client, unused_userdata, mid, granted_qos):
    nodens.logger.debug('INSIGHTS HUB: on_subscribe: mid {}, qos {}'.format(mid, granted_qos))

def on_connect_MS(client, userdata, flags, rc):
    global CONNECTION_ON
    nodens.logger.debug('INSIGHTS HUB: on_connect: {} userdata: {}. flags: {}. rc: {}'.format(mqtt.connack_string(rc), userdata, flags, rc))
    CONNECTION_ON = 1

def on_disconnect_MS(client, userdata, rc):
    global CONNECTION_ON
    nodens.logger.debug('INSIGHTS HUB: on_disconnect: {} userdata: {}.'.format(mqtt.connack_string(rc), userdata))
    CONNECTION_ON = 0

    if rc == 5:
        time.sleep(1)

def on_unsubscribe_MS(client, userdata, mid):
    nodens.logger.debug('INSIGHTS HUB: on_unsubscribe: mid {}. userdata: {}.'.format(mid, userdata))


def on_message_MS(client, unused_userdata, message):
    payload = str(message.payload.decode("utf-8"))
    nodens.logger.info(        "********************************\nReceived message '{}' on topic '{}' with Qos {}\n********************************".format(
            payload, message.topic, str(message.qos)))


## ~~~~~ Parse messages for MindConnect ~~~~~ ##

## ~~~~~ MindConnect messaging ~~~~~ ##

delay_time = 10
Nchirp = 16
Nud = 25

# Specify certificate locations
cwd = os.getcwd() + '/'
#dir = Path(cwd+'Certificates/')


# Get client
def get_mindconnect_client(
    tenantId,
    clientId,
    mqtt_hostname,
    mqtt_port,
    ca_cert,
    certfile,
    private_key_file,
    ):

    

    nodens.logger.debug("INSIGHTS HUB: Setting up client...")
    client = mqtt.Client("{}_{}".format(tenantId, clientId))

    # Register callbacks
    client.on_publish = on_publish_MS
    client.on_subscribe = on_subscribe_MS
    client.on_unsubscribe = on_unsubscribe_MS
    client.on_connect = on_connect_MS
    client.on_disconnect = on_disconnect_MS
    client.on_message = on_message_MS

    # Connect to MQTT client
    client.tls_set(ca_certs=ca_cert, certfile=certfile, keyfile=private_key_file, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
    client.connect(host=mqtt_hostname, port=mqtt_port)

    return client

# Send data
class sendMindConnect:
    def __init__(self, ca_cert, certfile, private_key_file):
        self.tenantId = nodens.cp.IH_TENANT_ID
        self.clientId = nodens.cp.IH_CLIENT_ID

        # MQTT connection
        self.ca_cert = ca_cert
        self.certfile = certfile
        self.private_key_file = private_key_file
        self.mqtt_hostname = nodens.cp.IH_HOST
        self.mqtt_port = nodens.cp.IH_PORT

        # MQTT topics
        self.topic_timeseries_send = "tc/{0}/{0}_{1}/o/mc_v3/ts".format(
            self.tenantId, self.clientId)

        # MindConnect mapping dataPoints
        self.dataPointLabels = ["sensor_id", 
                                "root_id", 
                                "occupancy", 
                                "timestamp", 
                                "x", 
                                "y", 
                                "z", 
                                "occupant_id", 
                                "sensor_id", 
                                "ud_sig",
                                "activity_detected",
                                "activity_type"]
        self.dataPointId = []
        for i in range(len(self.dataPointLabels)):
            self.dataPointId.append("dp"+"{:02d}".format(i+1))

    def connect_to_mindconnect(self):
        self.mqtt_client = get_mindconnect_client(
                            self.tenantId,
                            self.clientId,
                            self.mqtt_hostname,
                            self.mqtt_port,
                            self.ca_cert,
                            self.certfile,
                            self.private_key_file,
                            )
    
    def send_mindconnect_payload(self, 
                                mqtt_data,     # Note: this is equivalent to mqttDataFinal in the main processing chain
                                sensor_data = '',   # Note: this is equivalent to sd or parseTLV
                                delay_time=1   # Delay time between checking for MQTT connection
                                ):
        
        # Start MQTT client loop
        self.mqtt_client.loop_start()
        while CONNECTION_ON == 0:
            nodens.logger.warning("INSIGHTS HUB: Not connected yet")
            sleep(delay_time)

        if CONNECTION_ON == 1:
            # Message
            nodens.logger.debug("INSIGHTS HUB: Sending message to Insights Hub...")
            # Set values
            sensor_id = mqtt_data['addr']
            root_id = mqtt_data['addr'] # TODO: check format of payload for root data
            num_occupants = int(mqtt_data['Number of Occupants'])
            # try:
            #     mqttOccInfo = mqtt_data['Occupancy Info']
            # except:
            #     nodens.logger.warning("Occupancy Info not found in mqtt data. num occ: {}".format(num_occupants) )
            if sensor_data != '':
                ud_sig = sensor_data.ud_sig # Micro-Doppler signature
                Nchirp = 16
                Nud = 20

            T0 = datetime.datetime.utcnow()
            timestamp = T0.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"Z"
            timestamp_val = T0.strftime("%Y-%m-%dT%H:%M:%S")+"Z"
            activity_detected = mqtt_data['Activity detected']
            activity_type = mqtt_data['Activity type']

            nodens.logger.debug("INSIGHTS HUB: Detected: {}. Activity type to send: {} at {}".format(activity_detected, activity_type, timestamp))

            # sensor payload
            send_timeseries = []
            if num_occupants == 0:
                occupant_id = ''
                x = ''
                y = ''
                z = ''
                ud_val = ""
                value = [sensor_id, root_id, str(num_occupants), timestamp_val, 
                            "", "", "", str(occupant_id),
                            sensor_id, ud_val, "{}".format(activity_detected), "{}".format(activity_type)]
    
                send_values = []
                for j in range(len(self.dataPointLabels)):
                    send_value = {
                        "dataPointId": self.dataPointId[j],
                        "value": value[j],
                        "qualityCode": "0"
                    }
                    send_values.append(send_value)
    
                send_timeseries_1= {
                    "timestamp": timestamp,
                    "values": send_values
                }
                send_timeseries.append(send_timeseries_1)
                T0 = T0 + datetime.timedelta(milliseconds = 100)
                timestamp = T0.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"Z"
            else:
                mqttOccInfo = mqtt_data['Occupancy Info']

            for i in range(num_occupants):
                occupant_id = mqttOccInfo[i]['Occupant ID']
                x = mqttOccInfo[i]['X']
                y = mqttOccInfo[i]['Y']
                z = mqttOccInfo[i]['Z']
                ud_val = ""
                if sensor_data != '':
                    for i in range(Nchirp): # First downsample (simple mean)
                        for j in range(Nud):
                            temp_ud = np.floor(np.mean(ud_sig[4*i:4*i+4, 2*j:2*j+2]))
                            #if temp_ud > 0:
                            #    print("ud:",temp_ud)
                            ud_val += str(temp_ud) + ","
                    ud_val = ud_val[:-2]

                value = [sensor_id, root_id, str(num_occupants), timestamp_val, 
                            "{:.2f}".format(x), "{:.2f}".format(y), "{:.2f}".format(z), str(occupant_id),
                            sensor_id, ud_val, "{}".format(activity_detected), "{}".format(activity_type)]
                send_values = []
                for j in range(len(self.dataPointLabels)):
                    send_value = {
                        "dataPointId": self.dataPointId[j],
                        "value": value[j],
                        "qualityCode": "0"
                    }
                    send_values.append(send_value)
    
                send_timeseries_1= {
                    "timestamp": timestamp,
                    "values": send_values
                }
                send_timeseries.append(send_timeseries_1)
                T0 = T0 + datetime.timedelta(milliseconds = 100)
                timestamp = T0.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"Z"

            
            send_packet = {
                "timeseries": send_timeseries
            }
            nodens.logger.debug("INSIGHTS HUB: Sending to Insight Hub...")
            self.mqtt_client.publish(self.topic_timeseries_send,payload=json.dumps(send_packet),qos=0) # TODO: update topic
            self.mqtt_client.loop_stop()

            # Message
            nodens.logger.debug("INSIGHTS HUB: ...message sent.")
        else:
            nodens.logger.warning("INSIGHTS HUB: Not connected yet 2")
            sleep(1)

