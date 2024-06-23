# __main__.py

from pathlib import Path
import datetime as dt
from time import sleep as sleep
import threading
from os import path as path
from platformdirs import user_config_dir, user_documents_dir
import logging

import nodens.gateway as nodens
from nodens.gateway import nodens_mesh, nodens_serv, nodens_thingsboard
from nodens.gateway import nodens_thingsboard as nodens_tb
from nodens.gateway import nodens_insight_hub as nodens_ih
from nodens.gateway import nodens_fns as ndns_fns


def sensor_thread(pipeline_thingsboard,pipeline_insight_hub):
    #def __init__(self):
    # Get time
    T0 = dt.datetime.now(dt.timezone.utc)
    

    #######################################
    # Connect to sensor mesh MQTT

    nodens.logger.debug("Mesh. sensor ip = {}. sensor port = {}. sensor topic = {}.".format(nodens.cp.SENSOR_IP,
                                                                                        nodens.cp.SENSOR_PORT, 
                                                                                        nodens.cp.SENSOR_TOPIC))
    nodens_mesh.MESH.end()
    nodens_mesh.MESH.connect(nodens.cp.SENSOR_IP,
                                nodens.cp.SENSOR_PORT,
                                60,
                                nodens.cp.SENSOR_TOPIC,
                                nodens_serv.on_message_sensorN)   

    nodens.logger.info("Connected to mesh")
    
    while 1:
        sleep(0.1)

        # Check message pipeline for messages to send
        idx = [i for i,val in enumerate(ndns_fns.message_pipeline.flag_send) if val == 1]
        for s_idx in idx:

            if nodens.cp.ENABLE_THINGSBOARD:
                pipeline_thingsboard.set_message(ndns_fns.message_pipeline.message[s_idx], "Producer")

            if nodens.cp.ENABLE_SIEMENS_IH:
                pipeline_insight_hub.set_message(ndns_fns.message_pipeline.message[s_idx], "Producer")

            ndns_fns.message_pipeline.clear(s_idx)

        # Check message pipeline for configs to update
        idx = [i for i,val in enumerate(ndns_fns.message_pipeline.config_flag_send) if val == 1]
        for s_idx in idx:

            if nodens.cp.ENABLE_THINGSBOARD:
                pipeline_thingsboard.set_message(ndns_fns.message_pipeline.config_message[s_idx], "Producer")

            ndns_fns.message_pipeline.clear_config(s_idx)

        if nodens_mesh.MESH.client.connect_status == 0:
            nodens.logger.debug("MESH: Time to reconnect")
            nodens_mesh.MESH.end()
            nodens_mesh.MESH.connect(nodens.cp.SENSOR_IP,
                                        nodens.cp.SENSOR_PORT,
                                        60,
                                        nodens.cp.SENSOR_TOPIC,
                                        nodens_serv.on_message_sensorN)  
            
    nodens.logger.info("EXIT WHILE LOOP")

#     #RunMQTT()
class ThingsboardHandler(logging.Handler):
    # TODO: better handling of logging to different gateways, devices, sensors, etc.
    def __init__(self):
        logging.Handler.__init__(self)
        self._destination = ''

    def emit(self, record):
        try:
            log_msg = self.format(record)
            nodens_tb.TB.prepare_log(log_msg)
            if len(ndns_fns.si.connected_sensors) > 0:
                self._destination = ndns_fns.si.connected_sensors[0]
                nodens_tb.TB.multiline_payload(self._destination)
        except Exception:
            self.handleError(record)

def thingsboard_thread(pipeline):
    """Function to trigger publish to Thingsboard Cloud service"""
    nodens.logger.info("Pipeline to Thingsboard connected")
    

    thingsboard_handler = ThingsboardHandler()
    thingsboard_handler.setLevel(logging.INFO)
    mqtt_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    thingsboard_handler.setFormatter(mqtt_format)

    #nodens.logger.addHandler(thingsboard_handler)

    search_folders_certs = [user_config_dir(nodens.APPNAME, nodens.APPAUTHOR)+"/certs/",
                  user_config_dir(nodens.APPNAME, nodens.APPAUTHOR)+"/",
                  nodens.CWD+"/certs/",
                  nodens.CWD+"/",
                  user_documents_dir()+"/certs/",
                  user_documents_dir()+"/",]

    # Initialise Thingsboard
    #if nodens.cp.ENABLE_THINGSBOARD:
    if nodens.cp.TB_ACCESS_TOKEN_FOLDER != "" and nodens.cp.TB_ACCESS_TOKEN_FOLDER != None:
        if path.exists(nodens.cp.TB_ACCESS_TOKEN_FOLDER+"/"+nodens.cp.TB_ACCESS_TOKEN_FILENAME):
            nodens_tb.TB.get_sensors(nodens.cp.TB_ACCESS_TOKEN_FOLDER+"/"+nodens.cp.TB_ACCESS_TOKEN_FILENAME)
            nodens.logger.info("Thingsboard tokens found")
        else:
            nodens.logger.warning("Thingsboard tokens not found in designated folder. Searching other locations...")
    i = 0
    while i < len(search_folders_certs):
        if path.exists(search_folders_certs[i]+"/"+nodens.cp.TB_ACCESS_TOKEN_FILENAME):
            nodens_tb.TB.get_sensors(search_folders_certs[i]+"/"+nodens.cp.TB_ACCESS_TOKEN_FILENAME)
            nodens.logger.info("Thingsboard tokens found")
            i=-1
            break
        i += 1
    if i > -1:
        nodens.logger.error("\n\nTHINGSBOARD: NO ACCESS TOKENS FOUND. Please locate file: thingsboard_access.json.\n\n")


    #nodens_thingsboard.TB.subscribe_to_attributes(ndns_fns.si.connected_sensors)
    while 1:
        try:
            message = pipeline.get_message("Consumer")
        #sleep(0.1)
            nodens_thingsboard.TB.subscribe_to_attributes(ndns_fns.si.connected_sensors)

            # Check if the message to send is a config (attribute)
            if "type" in message:
                if message["type"] == "CONFIG_TX":
                    nodens_thingsboard.TB.publish_config(message["addr"], message["payload"])
                elif message["type"] == "CONFIG_RX":
                    nodens_thingsboard.TB.get_config(message["addr"])
                else:
                    nodens_thingsboard.TB.prepare_data(message)
                    nodens_thingsboard.TB.multiline_payload(message['addr'])

            for i in range(len(nodens_thingsboard.TB.client_sub)):
                if nodens_thingsboard.TB.client_sub[i]._userdata != []:
                    nodens_thingsboard.TB.client_sub[i]._userdata = []
        except Exception as e:
            nodens.logger.error(f"THINGSBOARD: thread error: {e.args}")

def thingsboard_subscribe_thread(pipeline):
    """Function to trigger publish to Thingsboard Cloud service"""
    nodens.logger.info("Pipeline to Thingsboard subscribe connected")

    while 1:
        #message = pipeline.get_message("Consumer")
        
        nodens_thingsboard.TB.subscribe_to_attributes(ndns_fns.si.connected_sensors)
        sleep(5)

def insights_hub_thread(pipeline):
    """Function to trigger publish to Thingsboard Cloud service"""
    nodens.logger.info("Pipeline to Siemens Insights Hub connected")

    # Connect to Insight Hub
    if nodens.flag_ih_cert == 1:
        send_mc = nodens_ih.sendMindConnect(ca_cert = nodens.ih_ca_cert, certfile = nodens.ih_public_cert, private_key_file = nodens.ih_private_key)
    else:
        nodens.logger.warning("Insight HUB disabled: certificates not found.")
        nodens.cp.ENABLE_SIEMENS_IH = 0

    send_mc.connect_to_mindconnect()
    while 1:
        message = pipeline.get_message("Consumer")

        send_mc.send_mindconnect_payload(mqtt_data=message, sensor_data='')

class Pipeline:
    """
    Class to allow a single element pipeline between producer and consumer.
    From example: https://realpython.com/intro-to-python-threading/#producer-consumer-threading
    """
    def __init__(self):
        self.message = 0
        self.producer_lock = threading.Lock()
        self.consumer_lock = threading.Lock()
        self.consumer_lock.acquire()

    def get_message(self, name):
        self.consumer_lock.acquire()
        message = self.message
        self.producer_lock.release()
        return message

    def set_message(self, message, name):
        self.producer_lock.acquire()
        self.message = message
        self.consumer_lock.release()


if __name__ == "__main__":
    
    pipeline_thingsboard = Pipeline()
    #pipeline_thingsboard_sub = Pipeline()
    pipeline_insight_hub = Pipeline()
    
    thread_sensors = threading.Thread(target=sensor_thread, args=(pipeline_thingsboard,pipeline_insight_hub,), daemon=True)
    thread_thingsboard = threading.Thread(target=thingsboard_thread, args=(pipeline_thingsboard,), daemon=True)
    #thread_thingsboard_sub = threading.Thread(target=thingsboard_subscribe_thread, args=(pipeline_thingsboard_sub,), daemon=True)
    thread_insights_hub = threading.Thread(target=insights_hub_thread, args=(pipeline_insight_hub,), daemon=True)
    ## ADD NEW THREAD FOR CONFIG + ATTRIBUTES PUBLISH

    thread_sensors.start()
    if nodens.cp.ENABLE_THINGSBOARD:
        thread_thingsboard.start()
        #thread_thingsboard_sub.start()
    if nodens.cp.ENABLE_SIEMENS_IH:
        
        thread_insights_hub.start()

    while True:
        sleep(1)
