## Update: cb="" in MESH.multiline_payload()

import json
import logging
import time
import configparser
import datetime as dt
import numpy as np
from pprint import pprint
import base64
import nodens.gateway as nodens
from nodens.gateway import nodens_mesh as ndns_mesh
from platformdirs import user_log_dir

# Get config from file #
def get_config(config, SECTION, CONFIG, CONFIG_str):
    try:
        output = config.get(SECTION, CONFIG_str).partition('#')[0]
    except:
        output = CONFIG
        nodens.logger.debug('{} not specified in config file. Default value used.'.format(CONFIG_str))
    else:
        output = config.get(SECTION, CONFIG_str).partition('#')[0].rstrip()
        nodens.logger.debug('CONFIG: {} = {}'.format(CONFIG_str, config.get(SECTION, CONFIG_str).partition('#')[0].rstrip()))
    
    return(output)

class radar_config_params:
    """Stores radar configuration information for the current sensor"""
    def __init__(self):
        ## ~~~~~~~ DEFAULT CONFIGURATION ~~~~~~~ ##
        # Radar config #
        self.cfg_idx = 0
        self.cfg_sensorStart = 1
        self.config_radar = [
                "dfeDataOutputMode 1",  # 0
                "channelCfg 15 7 0",
                "adcCfg 2 1",
                "adcbufCfg -1 0 1 1 1",
                "lowPower 0 0",
                "bpmCfg -1 1 0 2",  # 5
                "profileCfg 0 60.75 30.00 25.00 59.10 0 0 54.71 1 96 2950.00 2 1 36 ",
                "chirpCfg 0 0 0 0 0 0 0 5",
                "chirpCfg 1 1 0 0 0 0 0 2",
                "chirpCfg 2 2 0 0 0 0 0 5",
                "frameCfg 0 2 48 0 55.00 1 0",  # 10
                "dynamicRACfarCfg -1 4 4 2 2 8 12 4 8 4.00 8.00 0.40 1 1",
                "staticRACfarCfg -1 6 2 2 2 8 8 6 4 5.00 15.00 0.30 0 0",
                "dynamicRangeAngleCfg -1 0.75 0.0010 1 0",
                "dynamic2DAngleCfg -1 1.5 0.0300 1 0 1 0.30 0.85 8.00",
                "staticRangeAngleCfg -1 0 8 8", # 15
                "fineMotionCfg -1 1",
                "antGeometry0 0 -1 -2 -3 -2 -3 -4 -5 -4 -5 -6 -7",
                "antGeometry1 -1 -1 -1 -1 0 0 0 0 -1 -1 -1 -1",
                "antPhaseRot 1 1 1 1 1 1 1 1 1 1 1 1",
                "fovCfg -1 70.0 20.0",  # 20
                "compRangeBiasAndRxChanPhase 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0",
                "staticBoundaryBox -2 2 2 5.5 0 3",
                "boundaryBox -2.5 2.5 0.5 6 0 3",
                "sensorPosition 1 0 0",
                "gatingParam 3 1.5 1.5 2 4",    # 25
                "stateParam 3 3 12 65500 5 65500",
                "allocationParam 40 100 0.025 20 0.8 20",
                "maxAcceleration 0.1 0.1 0.1",
                "trackingCfg 1 2 800 15 46 96 55",
                "presenceBoundaryBox -4 4 0.5 6 0 3",   # 30
                "sensorStart"
                ]

        # Bed config #
        self.BED_FLAG = 0
        self.BED_X = []
        self.BED_Y = []

        # Entry config #
        self.CHAIR_FLAG = 0
        self.CHAIR_X = []
        self.CHAIR_Y = []

    def config_dim(self, radar_dim):
        if radar_dim == 3:
            self.config_radar = [
                "dfeDataOutputMode 1",  # 0
                "channelCfg 15 7 0",
                "adcCfg 2 1",
                "adcbufCfg -1 0 1 1 1",
                "lowPower 0 0",
                "bpmCfg -1 1 0 2",  # 5
                "profileCfg 0 60.75 30.00 25.00 59.10 0 0 54.71 1 96 2950.00 2 1 36 ",
                "chirpCfg 0 0 0 0 0 0 0 5",
                "chirpCfg 1 1 0 0 0 0 0 2",
                "chirpCfg 2 2 0 0 0 0 0 5",
                "frameCfg 0 2 48 0 55.00 1 0",  # 10
                "dynamicRACfarCfg -1 4 4 2 2 8 12 4 8 5.00 8.00 0.40 1 1",
                "staticRACfarCfg -1 6 2 2 2 8 8 6 4 5.00 15.00 0.30 0 0",
                "dynamicRangeAngleCfg -1 0.75 0.0010 1 0",
                "dynamic2DAngleCfg -1 1.5 0.0300 1 0 1 0.30 0.85 8.00",
                "staticRangeAngleCfg -1 0 8 8", # 15
                "fineMotionCfg -1 1",
                "antGeometry0 0 -1 -2 -3 -2 -3 -4 -5 -4 -5 -6 -7",
                "antGeometry1 -1 -1 -1 -1 0 0 0 0 -1 -1 -1 -1",
                "antPhaseRot 1 1 1 1 1 1 1 1 1 1 1 1",
                "fovCfg -1 70.0 20.0",  # 20
                "compRangeBiasAndRxChanPhase 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0",
                "staticBoundaryBox -2 2 2 5.5 0 3",
                "boundaryBox -2.5 2.5 0.5 6 0 3",
                "sensorPosition 1.2 0 0",
                "gatingParam 3 1.5 1.5 2 4",    # 25
                "stateParam 3 3 12 1000 5 6000",
                "allocationParam 80 200 0.1 40 0.5 20",
                "maxAcceleration 0.1 0.1 0.1",
                "trackingCfg 1 2 800 20 46 96 55",
                "presenceBoundaryBox -4 4 0.5 6 0 3",   # 30
                "sensorStart"
                ]
        else:
            self.config_radar = [
                "dfeDataOutputMode 1",
                "channelCfg 15 5 0",
                "adcCfg 2 1",
                "adcbufCfg 0 1 1 1",
                "profileCfg 0 62.00 30 10 69.72 0 0 28.42 1 128 2180 0 0 24",
                "chirpCfg 0 0 0 0 0 0 0 1",
                "chirpCfg 1 1 0 0 0 0 0 4",
                "frameCfg 0 1 128 0 50 1 0",
                "lowPower 0 0",
                "guiMonitor 1 1 1 1",
                "cfarCfg 6 4 4 4 4 8 12 4 8 20 33 0",
                "doaCfg 600 666 30 1 1 1 300 4 2",
                "AllocationParam 0 200 0.1 15 0.5 20",
                "GatingParam 3 1.5 1.5 0",
                "StateParam 3 3 10 1200 5 12000",
                "SceneryParam -5 5 0.25 10",
                "FilterParam 2.0 0.5 1.5",
                "trackingCfg 1 2 300 15 67 105 50 90",
                "classifierCfg 1 1 3 500 0.8 1.0 0.95 10",
                "sensorStart"
                ]

    def receive_config(self, raw):
        if self.cfg_idx == 0:
            self.config_radar = []
        if self.cfg_idx < len(self.config_radar):
            self.config_radar[self.cfg_idx] = raw
        else:
            self.config_radar.append(raw)
        if raw == "sensorStart":
            self.cfg_idx = 0
            self.cfg_sensorStart = 1
        else:
            self.cfg_idx+=1

        if "boundaryBox" in raw:
            temp = raw[len("boundaryBox")+1:]
            temp = temp.split(" ")

            self.ROOM_X = temp[0] + "," + temp[1]
            self.ROOM_Y = temp[2] + "," + temp[3]
            self.ROOM_Z = temp[4] + "," + temp[5]

        if "staticBoundaryBox" in raw:
            temp = raw[len("staticBoundaryBox")+1:]
            temp = temp.split(" ")

            self.MONITOR_X = temp[0] + "," + temp[1]
            self.MONITOR_Y = temp[2] + "," + temp[3]
            self.MONITOR_Z = temp[4] + "," + temp[5]

        if "compRangeBiasAndRxChanPhase" in raw:
            temp = raw[len("compRangeBiasAndRxChanPhase")+1:]

            self.RADAR_CAL = temp


# Parse updated sensor configuration file #
def parse_config(config_file, EntryWays, rcp, cp, rate_unit = 0.25):
    ## ~~~~~~~ UPDATE CONFIGURATION ~~~~~~~ ##
    #rcp = ndns_fns.radar_config_params()
    #ndns_fns.rcp = ndns_fns.radar_config_params()

    if config_file is None:
        nodens.logger.warning('No config file. Default values used.')
    elif config_file.is_file():
        config = configparser.RawConfigParser()
        config.read(config_file)
        nodens.logger.debug(config['Sensor target']['SENSOR_ID'])

        # Sensor target #
        nodens.cp.SENSOR_ROOT = (get_config(config,'Sensor target', nodens.cp.SENSOR_ROOT, 'ROOT_ID'))
        nodens.cp.SENSOR_TARGET = (get_config(config,'Sensor target', nodens.cp.SENSOR_TARGET, 'SENSOR_ID'))
        try:
            nodens.cp.SENSOR_TOPIC = config.get('Sensor target', 'SENSOR_TOPIC').partition('#')[0]  
        except:
            nodens.cp.SENSOR_TOPIC = 'mesh/' + nodens.cp.SENSOR_ROOT + '/toDevice'
            nodens.logger.debug('{} not specified in config file. Default value used: {}'.format('SENSOR_TOPIC', nodens.cp.SENSOR_TOPIC))
        else:
            nodens.cp.SENSOR_TOPIC = config.get('Sensor target', 'SENSOR_TOPIC').partition('#')[0].rstrip()
        if not bool(nodens.cp.SENSOR_TOPIC):
            nodens.cp.SENSOR_TOPIC = '#'
        nodens.logger.debug('Topic = {}'.format(nodens.cp.SENSOR_TOPIC))

        # Scanning config #
        nodens.cp.SCAN_TIME = float(get_config(config,'Scanning config', nodens.cp.SCAN_TIME, 'SCAN_TIME'))
        nodens.cp.FULL_DATA_FLAG = int(get_config(config,'Scanning config', nodens.cp.FULL_DATA_FLAG, 'FULL_DATA_FLAG'))
        nodens.cp.FULL_DATA_TIME = float(get_config(config,'Scanning config', nodens.cp.FULL_DATA_TIME, 'FULL_DATA_TIME'))

        # Radar config #
        nodens.cp.RADAR_SEND_FLAG = int(get_config(config,'Radar config', nodens.cp.RADAR_SEND_FLAG, 'RADAR_SEND_FLAG'))
        nodens.cp.ROOM_X = (get_config(config,'Radar config', nodens.cp.ROOM_X, 'ROOM_X'))
        nodens.cp.ROOM_Y = (get_config(config,'Radar config', nodens.cp.ROOM_Y, 'ROOM_Y'))
        nodens.cp.ROOM_Z = (get_config(config,'Radar config', nodens.cp.ROOM_Z, 'ROOM_Z'))
        nodens.cp.MONITOR_X = (get_config(config,'Radar config', nodens.cp.MONITOR_X, 'MONITOR_X'))
        nodens.cp.MONITOR_Y = (get_config(config,'Radar config', nodens.cp.MONITOR_Y, 'MONITOR_Y'))
        nodens.cp.MONITOR_Z = (get_config(config,'Radar config', nodens.cp.MONITOR_Z, 'MONITOR_Z'))
        nodens.cp.SENSOR_YAW = float(get_config(config,'Radar config', nodens.cp.SENSOR_YAW, 'SENSOR_YAW'))
        nodens.cp.SENSOR_PITCH = float(get_config(config,'Radar config', nodens.cp.SENSOR_PITCH, 'SENSOR_PITCH'))
        nodens.cp.SENSITIVITY = (get_config(config,'Radar config', nodens.cp.SENSITIVITY, 'SENSITIVITY'))
        nodens.cp.OCC_SENSITIVITY = (get_config(config,'Radar config', nodens.cp.OCC_SENSITIVITY, 'OCC_SENSITIVITY'))

        # Entry config #
        nodens.cp.ENTRY_FLAG = int(get_config(config,'Entry config', nodens.cp.ENTRY_FLAG, 'ENTRY_FLAG'))
        nodens.cp.ENTRY_X = get_config(config,'Entry config', nodens.cp.ENTRY_X, 'ENTRY_X')
        nodens.cp.ENTRY_Y = get_config(config,'Entry config', nodens.cp.ENTRY_Y, 'ENTRY_Y')
  
    else:
        nodens.logger.warning('No config file. Default values used.')

    # Check sensor version and update config #
    #sv.request(client, rcp.SENSOR_TOPIC, rcp.SENSOR_TARGET)
    sendCMDtoSensor.request_version(rcp,cp,sv)
    sendCMDtoSensor.request_config(rcp,cp)
    time.sleep(5)
    if len(rcp.config_radar) == 0:
        rcp.config_dim(sv.radar_dim)
    
    # Parse Publish rates to payload #
    # rate_unit = Baseline data transmission rate
    config_pub_rate = "CMD: PUBLISH RATE: " + str(round(nodens.cp.SCAN_TIME/rate_unit))
    payload_msg = [{ "addr" : [nodens.cp.SENSOR_TARGET],
                        "type" : "json",
                        "data" : config_pub_rate + "\n"}]

    if nodens.cp.FULL_DATA_FLAG:
        config_full_data = "CMD: FULL DATA ON. RATE: " + str(max(1,nodens.cp.FULL_DATA_TIME/nodens.cp.SCAN_TIME))
        nodens.logger.info(f"\nrate_unit: {rate_unit}s. SCAN TIME: {nodens.cp.SCAN_TIME}s. PUBLISH RATE: {str(round(nodens.cp.SCAN_TIME/rate_unit))}. FULL DATA RATE: {str(max(1,nodens.cp.FULL_DATA_TIME/nodens.cp.SCAN_TIME))}.\n")
    else:
        config_full_data = "CMD: FULL DATA OFF."
        nodens.logger.info(f"\nrate_unit: {rate_unit}s. SCAN TIME: {nodens.cp.SCAN_TIME}s. PUBLISH RATE: {str(round(nodens.cp.SCAN_TIME/rate_unit))}. FULL DATA OFF.\n")
        
    payload_msg.append({ "addr" : [nodens.cp.SENSOR_TARGET],
                    "type" : "json",
                    "data" : config_full_data + "\n"})
        
    # Send radar config #
    if nodens.cp.RADAR_SEND_FLAG:
        # Occupant tracker sensitivity #
        # NOTE: only implemented for 2D so far
        if sv.radar_dim == 2:
            param_temp = rcp.config_radar[12].split(" ")
            param_temp[1] = str(round(np.exp(1.8/float(nodens.cp.OCC_SENSITIVITY)+2.1)))
            param_temp[2] = str(round(np.exp(0.7/float(nodens.cp.OCC_SENSITIVITY)+5.3)))
            param_temp[4] = str(round(np.exp(0.7/float(nodens.cp.OCC_SENSITIVITY)+2)))
            rcp.config_radar[12] = " ".join(param_temp)
            nodens.logger.debug(rcp.config_radar[12])

        # Radar sensitivity #
        if sv.radar_dim == 2:
            param_temp = rcp.config_radar[10].split(" ")
            param_temp[10] = str(round(np.exp(0.7/float(nodens.cp.SENSITIVITY)+2.3)))
            param_temp[11] = str(round(np.exp(0.5/float(nodens.cp.SENSITIVITY)+3)))
            rcp.config_radar[10] = " ".join(param_temp)
            nodens.logger.debug(rcp.config_radar[10])
         
        # Room size #
        if sv.radar_dim == 2:
            param_temp = rcp.config_radar[15].split(" ")
            temp_x = nodens.cp.ROOM_X.split(',')
            temp_y = nodens.cp.ROOM_Y.split(',')
            param_temp[1:5] = [temp_x[0].strip(), temp_x[1].strip(), temp_y[0].strip(), temp_y[1].strip()]
            rcp.config_radar[15] = " ".join(param_temp)
            nodens.logger.debug(rcp.config_radar[15])
        elif sv.radar_dim == 3:
            # Static - 22
            i = 0
            while True:
                if i == len(rcp.config_radar):
                    nodens.logger.warning("Config error: {} not found!)".format("staticBoundaryBox "))
                    break
                elif "staticBoundaryBox " in rcp.config_radar[i]:  
                    param_temp = rcp.config_radar[i].split(" ")
                    temp_x = nodens.cp.MONITOR_X.split(',')
                    temp_y = nodens.cp.MONITOR_Y.split(',')
                    temp_z = nodens.cp.MONITOR_Z.split(',')
                    param_temp[1:7] = [temp_x[0].strip(), temp_x[1].strip(), temp_y[0].strip(), temp_y[1].strip(), temp_z[0].strip(), temp_z[1].strip()]
                    rcp.config_radar[i] = " ".join(param_temp)
                    nodens.logger.debug(rcp.config_radar[i])
                    break
                else:
                    i+=1
                    

            # Boundary - 23
            i = 0
            while True:
                if i == len(rcp.config_radar):
                    nodens.logger.warning("Config error: {} not found!)".format("boundaryBox "))
                    break
                elif "boundaryBox " in rcp.config_radar[i]:  
                    param_temp = rcp.config_radar[i].split(" ")
                    temp_x = nodens.cp.ROOM_X.split(',')
                    temp_y = nodens.cp.ROOM_Y.split(',')
                    temp_z = nodens.cp.ROOM_Z.split(',')
                    param_temp[1:7] = [temp_x[0].strip(), temp_x[1].strip(), temp_y[0].strip(), temp_y[1].strip(), temp_z[0].strip(), temp_z[1].strip()]
                    rcp.config_radar[i] = " ".join(param_temp)
                    nodens.logger.debug(rcp.config_radar[i])
                    break
                else:
                    i+=1

            # Presence - 30 (use bed if on, or static boundary otherwise)
            i = 0
            while True:
                if i == len(rcp.config_radar):
                    nodens.logger.warning("Config error: {} not found!)".format("presenceBoundaryBox "))
                    break
                elif "presenceBoundaryBox " in rcp.config_radar[i]:  
                    param_temp = rcp.config_radar[i].split(" ")
                    temp_x = nodens.cp.MONITOR_X.split(',')
                    temp_y = nodens.cp.MONITOR_Y.split(',')
                    temp_z = nodens.cp.MONITOR_Z.split(',')
                    param_temp[1:7] = [temp_x[0].strip(), temp_x[1].strip(), temp_y[0].strip(), temp_y[1].strip(), temp_z[0].strip(), temp_z[1].strip()]
                    rcp.config_radar[i] = " ".join(param_temp)
                    nodens.logger.debug(rcp.config_radar[i])
                    break
                else:
                    i+=1

            # Radar calibration - 21
            "compRangeBiasAndRxChanPhase 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0"
            i = 0
            while True:
                if i == len(rcp.config_radar):
                    nodens.logger.warning("Config error: {} not found!)".format("compRangeBiasAndRxChanPhase "))
                    break
                elif "compRangeBiasAndRxChanPhase " in rcp.config_radar[i]:  
                    temp_label = "compRangeBiasAndRxChanPhase "
                    temp_r = nodens.cp.RADAR_CAL
                    rcp.config_radar[i] = temp_label + temp_r
                    nodens.logger.debug(rcp.config_radar[i])
                    break
                else:
                    i+=1
            
        # Parse config to payload #
        for i in range(len(rcp.config_radar)):
            payload_msg.append({ "addr" : [nodens.cp.SENSOR_TARGET],
                        "type" : "json",
                        "data" : rcp.config_radar[i] + "\n"})


        payload_msg.append({ "addr" : [nodens.cp.SENSOR_TARGET],
                        "type" : "json",
                        "data" : "CMD: TI RESET" + "\n"})

    # Update entry points #
    if nodens.cp.ENTRY_FLAG:
        # Check for sensor id
        if (nodens.cp.SENSOR_TARGET not in EntryWays.id):
            EntryWays.id.append(nodens.cp.SENSOR_TARGET)
            EntryWays.x.append([])
            EntryWays.y.append([])
            EntryWays.count.append(0)
        sen_idx = EntryWays.id.index(nodens.cp.SENSOR_TARGET)

        temp = nodens.cp.ENTRY_X
        temp = temp.split(';')
        temp_parse = []
        for i in range(len(temp)):
            temp_split = temp[i].split(',')
            if len(temp_split) == 2:
                (temp_parse.append(float(temp_split[0])))
                (temp_parse.append(float(temp_split[1])))
                nodens.logger.debug('Entryway x: {},{}.'.format(float(temp_split[0]),float(temp_split[1])))
            else:
                nodens.logger.warning('WARNING! Incorrect format provided: {}. Format should be two numbers separated with a comma, e.g. \'-1,1\''.format(temp[i]))
        EntryWays.x[sen_idx] = temp_parse

        temp = nodens.cp.ENTRY_Y
        temp = temp.split(';')
        temp_parse = []
        for i in range(len(temp)):
            temp_split = temp[i].split(',')
            if len(temp_split) == 2:
                (temp_parse.append(float(temp_split[0])))
                (temp_parse.append(float(temp_split[1])))
                nodens.logger.debug('Entryway y: {},{}.'.format(float(temp_split[0]),float(temp_split[1])))
            else:
                nodens.logger.warning('WARNING! Incorrect format provided: {}. Format should be two numbers separated with a comma, e.g. \'-1,1\''.format(temp[i]))
        EntryWays.y[sen_idx] = temp_parse

    # OUTPUT #
    return(payload_msg,rcp,EntryWays)

# Store current mesh state #
class SensorMesh:
    def __init__(self):
        self.sensor_id = []  # ID of all connected sensors
        self.root_id = []    # ID of the root sensor
        self.last_time_connected = []    # timestamp of last detection
        self.layer_number = []   # Layer number

        # Config parameters
        # Update cloud db when sensorStart command received and config accepted
        self.last_user_config_update_time = [] # Last time config was updated
        self.sensor_config = [] # Latest sensor config
        self.sensor_version = [] # Sensor firmwave version
        self.sensor_publish_rate = []
        self.sensor_full_data = [] # 1 = ON, 0 = OFF
        self.sensor_full_data_rate = []
        self.sensorStart_flag = [] # 1 = sensorStart command received and config accepted

        self.room_id = []    # FUTURE: Room location
        self.site_id = []    # FUTURE: Site location
        self.user_id = []    # FUTURE: User that the sensor is assigned to

    # Update sensor mesh info
    # data - top level json data received via mqtt. Already checked that it's not the full data stream
    def update(self, data):
        addr = data["addr"]
        data_data = json.loads(base64.b64decode(data['data']))

        if addr in self.sensor_id:
            sens_idx = self.sensor_id.index(addr)
            self.sensor_id[sens_idx] = addr
            self.last_time_connected[sens_idx] = data_data["timestamp"]
            if "type" in data_data:
                self.root_id[sens_idx] = data_data["root"]
                self.layer_number[sens_idx] = data_data["layer"]

        else:
            try:
                self.sensor_id.append(addr)
                self.last_time_connected.append(data_data["timestamp"])
                if "type" in data_data:
                    self.root_id.append(data_data["root"])
                    self.layer_number.append(data_data["layer"])
                else:
                    self.root_id.append("")
                    self.layer_number.append("")
                
                self.last_user_config_update_time.append([])
                self.new_config()
                self.sensor_version.append([])
                self.sensor_publish_rate.append([])
                self.sensor_full_data.append([])
                self.sensor_full_data_rate.append([])
                self.sensorStart_flag.append([])
            except:
                nodens.logger.error("SensorMesh update 0: {}".format(data))

            try:
                # After initialising new sensor, request version and config
                sendCMDtoSensor.request_version(rcp,nodens.cp,sv,addr,self.root_id[self.sensor_id.index(addr)])
                sendCMDtoSensor.request_config(rcp,nodens.cp,addr,self.root_id[self.sensor_id.index(addr)])

            except:
                nodens.logger.error("SensorMesh update: {}".format(data))

    # Store sensor config when received
    def update_config(self, data):
        addr = data["addr"][0]
        msg_data = data["data"]
        commands = ["REQUEST VERSION", "REQUEST CONFIG", "PUBLISH RATE", "FULL DATA", "TI RESET"]
        T = dt.datetime.now(dt.timezone.utc)

        if addr in self.sensor_id:
            sens_idx = self.sensor_id.index(addr)

        else:
            self.sensor_id.append(addr)

        if msg_data[:3] == "CMD":
            payload = msg_data[5:]
            ndns_mesh.MESH.status.receive_cmd(msg_data, T, addr)
            cmd_num = ndns_mesh.MESH.status.last_cmd_num
            if cmd_num == 0: #
                self.sensor_version[sens_idx] = payload
            elif cmd_num == 2:
                self.sensor_publish_rate[sens_idx] = payload.split()[2]
            elif cmd_num == 3:
                if payload.split()[2][:2] == "ON":
                    self.sensor_full_data[sens_idx] = 1
                    self.sensor_full_data_rate[sens_idx] = payload.split()[4]
                else:
                    self.sensor_full_data[sens_idx] = 0
                

        else:
            self.sensor_config[sens_idx]["sensorID"] = addr
            token = msg_data.split()[0]
            if self.sensor_config[sens_idx] == []:
                # REQUEST CONFIG
                self.sensor_config[sens_idx] = rcp.config_radar
            if token == "sensorStart":
                self.sensorStart_flag[sens_idx] = 1
            else:
                if token in self.sensor_config[sens_idx]:
                    self.sensor_config[sens_idx][token] = msg_data[len(token):]
                    nodens.logger.warning(f"CONFIG. {token}: {self.sensor_config[sens_idx][token]}")
                # for idx,config in enumerate(self.sensor_config[sens_idx]):
                #     if token == config.split()[0]:
                #         self.sensor_config[sens_idx][idx] = msg_data
                #         break
                #     elif config.split()[0] == "sensorStart":
                #         nodens.logger.warning(f"SensorMesh update_config. Command not recognised: {msg_data}")

    # Store sensor config when received from remote server
    def update_with_received_config(self, payload):
        addr = payload["client"]["sensorID"]
        if addr in self.sensor_id:
            sens_idx = self.sensor_id.index(addr)

        keys = self.sensor_config[sens_idx].keys()
        for key in keys:
            if key in payload["client"]:
                self.sensor_config[sens_idx][key] = payload["client"][key]
                nodens.logger.info(f"SensorMesh. Received config from server. {key}: {self.sensor_config[sens_idx][key]}")


    def new_config(self):
        self.sensor_config.append({
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
            "trackingCfg":""
            }   
        )
    

            

# OTA update for ESP #
def ota_esp(config_params):
    addr = config_params.SENSOR_ID

    payload_msg = [{ "addr" : [addr],
                        "type" : "json",
                        "data" : "CMD: UPGRADE ROOT" + "\n"}]

    return(payload_msg)


# Sensor info #
class SensorInfo:
    """Information on the connected sensors."""
    def __init__(self):
        self.connected_sensors = []     # List of all connected sensors
        self.num_occ = []               # Number of occupants per sensor
        self.max_occ = []               # Max occ per sensor
        self.last_occ = []              # Not used?
        self.last_t = []                # Time of last payload received
        self.period_t = []              # Time of last payload to Cloud
        self.period_N = []              # Num of frames received since last sent to Cloud
        self.period_sum_occ = []        # Sum of occupancies since last sent to Cloud
        self.period_max_occ = []        # Max occ since last sent to Cloud
        self.ew_period_sum_occ = []     # As above for entryways
        self.ew_period_max_occ = []     # As above for entryways

    def check(self, mqttData):
        addr = mqttData['addr']
        if isinstance(addr, list):
            addr = addr[0]
        if (addr not in self.connected_sensors):
            T = dt.datetime.now(dt.timezone.utc)
            self.connected_sensors.append(addr)
            self.num_occ.append(0)
            self.max_occ.append(0)
            self.last_occ.append(0)
            self.last_t.append(T)
            self.period_t.append(T)
            self.period_N.append(1)
            self.period_sum_occ.append(0)
            self.period_max_occ.append(0)
            self.ew_period_sum_occ.append(0)
            self.ew_period_max_occ.append(0)

        sen_idx = self.connected_sensors.index(addr)

        return(sen_idx)
    
    def update_short(self, sen_idx, T, mqttData):
        self.last_t[sen_idx] = T

        if ('Number of Occupants' in mqttData):
            self.num_occ[sen_idx] = mqttData['Number of Occupants']

             # Update max number of occupants
            if (self.num_occ[sen_idx] > self.max_occ[sen_idx]):
                self.max_occ[sen_idx] = self.num_occ[sen_idx]

    def update_full(self, sen_idx, T, sensor_data):
        self.last_t[sen_idx] = T

        self.num_occ[sen_idx] = sensor_data.track.num_tracks

        # Update max number of occupants
        if (self.num_occ[sen_idx] > self.max_occ[sen_idx]):
            self.max_occ[sen_idx] = self.num_occ[sen_idx]

    def update_refresh(self, sen_idx, send_idx_e, T, entryway):
        self.period_N[sen_idx] += 1
        self.period_sum_occ[sen_idx] += self.num_occ[sen_idx]
        self.ew_period_sum_occ[sen_idx] += entryway.count[send_idx_e]
        if (self.num_occ[sen_idx] > self.period_max_occ[sen_idx]):
            self.period_max_occ[sen_idx] = self.num_occ[sen_idx]
        if (entryway.count[send_idx_e] > self.ew_period_max_occ[sen_idx]):
            self.ew_period_max_occ[sen_idx] = entryway.count[send_idx_e]

    def cloud_send_refresh(self, sen_idx, send_idx_e, T, entryway):
        self.update_refresh(sen_idx, send_idx_e, T, entryway)

        self.period_t[sen_idx] = T
        self.period_N[sen_idx] = 1
        self.period_sum_occ[sen_idx] = self.num_occ[sen_idx]
        self.period_max_occ[sen_idx] = self.num_occ[sen_idx]
        self.ew_period_sum_occ[sen_idx] = entryway.count[send_idx_e]
        self.ew_period_max_occ[sen_idx] = entryway.count[send_idx_e]

    

# Sensor version #
class sensor_version:
    """Sensor version. Reads both the radar firmwave version and the ESP firmware version. This is used to determine which version of code to use."""
    def __init__(self):
        self.string = []
        self.wifi_version = []
        self.radar_version = []
        self.radar_dim = 3

    def parse(self, str):
        #TODO: update to provide more flexibility with string
        if len(str) > 0:
            self.string = str
            if str[0] == 'C':
                self.wifi_version = str[0:7]
            else:
                nodens.logger.debug("VERSIONING ERROR. Mismatched Wi-Fi version. Expected 'CXX...'. Detected %s.", str)
                self.radar_dim = 2
            if (str[8] == 'R' and str[10] == 'D'):
                self.radar_version = str[8:]
                temp = int(str[9])
                if (temp == 2 or temp == 3):
                    self.radar_dim = temp
                else:
                    nodens.logger.debug("VERSIONING ERROR. Mismatched RADAR dimensions. Expected '...RXD...'. Detected %s.", str)
            else:
                nodens.logger.debug("VERSIONING ERROR. Mismatched RADAR version. Expected 'RXD...' where X=2/3. Detected %s. Revert to 2D.", str)
                self.radar_dim = 2
            print(self.wifi_version, self.radar_version)
        else:
            nodens.logger.debug("VERSIONING ERROR. No version provided. Defaulting to 2D config.")
            self.radar_dim = 2
    def request(self, client, root_topic, sensor_target):

        print("trying request")
        json_message = { "addr" : [sensor_target],
                    "type" : "json",
                    "data" : "CMD: REQUEST VERSION" + "\n"}
        json_message = json.dumps(json_message)
        client.publish(root_topic, json_message)

        nodens.logger.debug("Published sensor version request")
        temp = 0
        while (1):
            if self.string != []:
                nodens.logger.debug("Version received. Version = {}. Dimensions = {}.".format(self.string, self.radar_dim))
                break
            elif temp < 20:
                nodens.logger.debug("Waiting... {}".format(self.string))
                temp += 1
                time.sleep(0.2)
            else:
                nodens.logger.debug("No response to version request. Continue...")
                break

# Entry way info #
class EntryWays:
    def __init__(self):
        self.id = [] # Sensor ID
        self.x = [] # Array of 2-pules, i.e [[xa1, xa2],[xb1,xb2],...]
        self.y = [] # Same as x
        self.count = [] # Integer vector

    def update(self,new_id):
        self.id.append(new_id) # Add a new sensor
        self.x.append([])
        self.y.append([])
        self.count.append(0)

# Heatmap class #
class OccupantHeatmap:
    # TODO: Set heatmap extent from radar config (requires scanning sensor config)
    def __init__(self, sensor_id, Xres=1, Yres=[], Xrange=[-3,3], Yrange=[0,5]):
        self.sensor_id = sensor_id
        self.Xres = Xres

        if Yres == []:
            Yres = Xres
        
        self.Yres = Yres

        self.Xrange = Xrange
        self.Yrange = Yrange

        Xn = int(np.ceil(Xrange[1]/Xres)-np.floor(Xrange[0]/Xres))
        Yn = int(np.ceil(Yrange[1]/Yres)-np.floor(Yrange[0]/Yres))
        self.heatmap = np.zeros((Xn,Yn))
        self.heatmap_string = ""

    def reset_heatmap(self):
        self.heatmap = 0*self.heatmap
        self.heatmap_string = ""
    
    def update_heatmap(self, X, Y):
        #for i in range(track.num_tracks):
        try:
            # X index of track
            Xi = int(np.floor((X - self.Xrange[0])/self.Xres))
            # Y index of track
            Yi = int(np.floor((Y - self.Yrange[0])/self.Yres))
            # Iterate heatmap
            if (Xi>=0) & (Xi<np.size(self.heatmap,0)):
                if (Yi>=0) & (Yi<np.size(self.heatmap,1)):
                    self.heatmap[Xi,Yi] += 1
        except Exception as e:
            nodens.logger.warning(f"OccupantHeatmap.update_heatmap: {e}")

    def prepare_heatmap_string(self):
        string = ""
        try:
            for x in self.heatmap:
                for y in x:
                    string += chr(int(y))
        except Exception as e:
            nodens.logger.warning(f"OccupantHeatmap.heatmap_string: {e}")

        # Base64 encoding. Could compress this by storing multiple pixels per character
        try:
            bytes_value = string.encode()
            self.heatmap_string = base64.b64encode(bytes_value).decode()
        except Exception as e:
            nodens.logger.warning(f"OccupantHeatmap.heatmap_string: {e}")

# Gait calculation #
class GaitParameters:
    def __init__(self, sensor_id, num_hist_frames=250, num_window_frames=4):
        """This class records gait parameters for all tracks under a single sensor"""
        self.sensor_id = sensor_id
        self.track_id = []      # Record of all track ids for this sensor

        self.track_gait_params = []
        self.gait_str = ""

        self.num_hist_frames = num_hist_frames
        self.num_window_frames = num_window_frames

    class TrackGait:
        """This subclass records gait parameters for a single track"""
        def __init__(self, sensor_id, track_id, num_hist_frames=250, num_window_frames=4, 
                     gait_bins = [[19,0.1], [2,0.25]]):
            self.sensor_id = sensor_id
            self.track_id = track_id
            self.n_window = 0
            self.num_hist_frames = num_hist_frames
            self.num_window_frames = num_window_frames

            self.x0 = []    # previous
            self.y0 = []
            self.x1 = []    # current
            self.y1 = []

            self.speed = []
            num_gait_bins = 2   # 0 and above max
            self.gait_bins = [gait_bins[0][1]]
            for vals in gait_bins:
                if len(vals) == 2:
                    num_gait_bins += vals[0]
                    for i in range(vals[0]):
                        self.gait_bins.append(self.gait_bins[-1] + vals[1])
                else:
                    nodens.logger.warning(f"gait bin value {vals} should be a 2-pul, [num_bins, bin_size]")

            self.gait = [] # np.zeros((num_gait_bins))

        def update(self, track_id, Xh, Yh):
            if track_id == self.track_id:
                self.n_window += 1
                
                if self.n_window >= self.num_window_frames:
                    self.x0 = self.x1
                    self.y0 = self.y1

                    self.x1 = np.mean(Xh[0:self.num_window_frames])
                    self.y1 = np.mean(Yh[0:self.num_window_frames])

                    if (self.x0 != []) & (self.y0 != []):
                        self.speed.append(np.sqrt((self.x1-self.x0)**2 + (self.y1-self.y0)**2))
                    self.n_window = 0
            else:
                nodens.logger.warning(f"TrackGait.update. Track id: {track_id} does not match {self.track_id} for sensor: {self.sensor_id}")

        def reset(self):
            self.__init__(self.sensor_id, self.track_id, self.num_hist_frames, self.num_window_frames)
            # self.n_window = 0

            # self.x0 = []    # previous
            # self.y0 = []
            # self.x1 = []    # current
            # self.y1 = []

            # self.speed = []
            # self.num_values = 0

    def add_new_sensor(self, sensor_id):
        self.sensor_id = sensor_id
        self.track_id = [] 
        self.track_gait_params = []

    def add_new_track(self, sensor_id, track_id, Xh, Yh):
        if sensor_id == self.sensor_id:
            self.track_id.append(track_id)
            self.track_gait_params.append(self.TrackGait(self.sensor_id, track_id, num_hist_frames=self.num_hist_frames, num_window_frames=self.num_window_frames))

            self.track_gait_params[-1].update(track_id, Xh, Yh)
        else:
            nodens.logger.warning(f"GaitParameters.add_new_track. Sensor id: {sensor_id} does not match {self.sensor_id}")

    def update_track(self, sensor_id, track_id, Xh, Yh):
        if sensor_id == self.sensor_id:
            ind_t = self.track_id.index(track_id)

            self.track_gait_params[ind_t].update(track_id, Xh, Yh)
        else:
            nodens.logger.warning(f"GaitParameters.update_track. Sensor id: {sensor_id} does not match {self.sensor_id}")

    def delete_track(self, sensor_id, track_id):
        if sensor_id == self.sensor_id:
            ind_t = self.track_id.index(track_id)

            self.track_id.pop(ind_t)
            self.track_gait_params.pop(ind_t)
        else:
            nodens.logger.warning(f"GaitParameters.delete_track. Sensor id: {sensor_id} does not match {self.sensor_id}")

    def reset_tracks(self, sensor_id, track_id=[]):
        if sensor_id == self.sensor_id:
            if track_id == []:
                for track_gaits in self.track_gait_params:
                    track_gaits.reset()

            else:
                ind_t = self.track_id.index(track_id)
                self.track_gait_params[ind_t].reset()
        else:
            nodens.logger.warning(f"GaitParameters.reset_tracks. Sensor id: {sensor_id} does not match {self.sensor_id}")


    def calculate_gait_parameters(self, track_id=[]):
        """This function calculates gait parameters for all tracks recorded with this sensor, over num_hist_frames."""
        """To calculate parameters for a specific track, specify the track_id."""

        self.gait_str = ""
        if (track_id == []):
            for track_gaits in self.track_gait_params:
                track_gaits.gait = np.bincount(np.digitize(track_gaits.speed, track_gaits.gait_bins))
                if len(self.gait_str) > 0:
                    self.gait_str += ";"
                self.gait_str += ','.join(map(str, track_gaits.gait))
                
        else:
            ind_t = self.track_id.index(track_id)
            self.track_gait_params[ind_t].gait = np.bincount(np.digitize(self.track_gait_params[ind_t].speed, self.track_gait_params[ind_t].gait_bins))



# Occupant track history #
class OccupantHist:
    """Historical positions (X,Y) of occupants (tracks)."""
    def __init__(self, num_hist_frames=10, flag_time_based_record=0):
        """Initialises track histories"""
        self.sensor_id = []
        self.id = [] # track id
        self.x0 = [] # previous
        self.y0 = []
        self.x1 = [] # current
        self.y1 = []

        # Save inputs internally
        self.num_hist_frames = num_hist_frames
        self.flag_time_based_record = flag_time_based_record

        # History over last num_hist_frames
        self.xh = np.array(np.empty((self.num_hist_frames,),dtype=object), ndmin=3) # record of last num_hist_frames values
        self.yh = np.array(np.empty((self.num_hist_frames,),dtype=object), ndmin=3)

        # Energy statistics
        self.e_ud_h = np.array(np.empty((self.num_hist_frames,),dtype=object), ndmin=2) # sd.ud.signature_energy
        self.e_pc_h = np.array(np.empty((self.num_hist_frames,),dtype=object), ndmin=2) # sd.pc.energy

        # Activity statistics
        self.tot_dist = []  # Total distance moved over num_hist_frames
        self.max_dist = [] # Maximum movement over num_hist_frames
        self.flag_active = [] # Flag to identify whether occupant (track) is active or not (1 = active)
        self.time_inactive_start = []   # Time to mark start of inactive period

        # General inactivity stats per sensor
        self.most_inactive_track = []
        self.most_inactive_time = []

        # Room heatmaps per sensor
        self.room_heatmap = [] # Room heatmap showing occupancy positions

        # Gait parameters
        self.gait_params = []

        # Prepare outputs
        self.outputs = []

        # List of tracks to delete
        self.track_del_flag = []
        
    # Use this to refresh the histories
    def refresh(self, sensor_id):
        # Check for this specific sensor
        ind_s = self.sensor_id.index(sensor_id)

        self.xh[ind_s] = np.empty([self.xh.shape[1],self.xh.shape[2]], dtype=object)
        self.yh[ind_s] = np.empty([self.yh.shape[1],self.yh.shape[2]], dtype=object)

        self.e_ud_h[ind_s] = np.empty([self.e_ud_h.shape[1]], dtype=object)
        self.e_pc_h[ind_s] = np.empty([self.e_pc_h.shape[1]], dtype=object)

        # self.tot_dist[ind_s] = 0*self.tot_dist[ind_s]
        # self.max_dist[ind_s] = 0*self.max_dist[ind_s] 
        # self.flag_active[ind_s] = 1*self.flag_active[ind_s]
        for time in self.time_inactive_start[ind_s]:
            time = dt.datetime.now(dt.timezone.utc)

        # Reset room heatmap
        self.room_heatmap[ind_s].reset_heatmap()

        # Reset gait parameters
        self.gait_params[ind_s].reset_tracks(sensor_id)
    
    # Use this to update a track location everytime one is detected.
    def update(self, sensor_id, track_id=[], X=[], Y=[], sensor_data=[]):
        if (sensor_id in self.sensor_id):
            # Check for this specific sensor
            ind_s = self.sensor_id.index(sensor_id)
            #nodens.logger.info(f"OH.update. sensor_id: {sensor_id}. ind_s: {ind_s}. track_id: {track_id}. self.id[ind_s]: {self.id[ind_s]}. LOGIC: track exists: {track_id in self.id[ind_s]}")

            if (track_id == []):
                pass
            elif (track_id in self.id[ind_s]):
                # Check for this specific track
                ind_t = self.id[ind_s].index(track_id)

                # Update coordinates
                self.x0[ind_s][ind_t] = self.x1[ind_s][ind_t]
                self.y0[ind_s][ind_t] = self.y1[ind_s][ind_t]
                self.x1[ind_s][ind_t] = X
                self.y1[ind_s][ind_t] = Y

                # Update location histories
                try:
                    self.xh[ind_s][ind_t] = np.roll(self.xh[ind_s][ind_t],1)
                    self.xh[ind_s][ind_t][0] = X
                    self.yh[ind_s][ind_t] = np.roll(self.yh[ind_s][ind_t],1)
                    self.yh[ind_s][ind_t][0] = Y
                except Exception as e:
                    nodens.logger.error(f"OH.update. ind_s: {ind_s}. ind_t: {ind_t}. xh: {self.xh}. e: {e}")

                # Update energy  - UD currently only has one sig. TODO: check tid and then find other sigs + don't forget to add to new_track
                if sensor_data != []:       # Process only if receiving full data packet.
                    try:
                        self.e_ud_h[ind_s] = np.roll(self.e_ud_h[ind_s],1)
                    except Exception as e:
                        nodens.logger.error(f"OH.update 1. e: {e}")
                    try:
                        self.e_ud_h[ind_s][0] = sensor_data.ud.signature_energy
                    except Exception as e:
                        nodens.logger.error(f"OH.update 2. e: {e}")
                    try:
                        self.e_pc_h[ind_s] = np.roll(self.e_pc_h[ind_s],1)
                    except Exception as e:
                        nodens.logger.error(f"OH.update 3. e: {e}")
                    try:                        
                        self.e_pc_h[ind_s][0] = sensor_data.pc.energy[0]
                    except Exception as e:
                        self.e_pc_h[ind_s][0] = sensor_data.pc.energy


                # Update activity statistics
                try:
                    self.activity_detection(sensor_id, track_id)
                except Exception as e:
                    nodens.logger.error(f"OH.update activity_detection. e: {e}")

                # Update heatmap
                try:
                    self.room_heatmap[ind_s].update_heatmap(X,Y)
                except Exception as e:
                    nodens.logger.error(f"OH.update room_heatmap. e: {e}")

                # Update gait parameters
                try:
                    self.gait_params[ind_s].update_track(sensor_id, track_id, self.xh[ind_s][ind_t], self.yh[ind_s][ind_t])
                except Exception as e:
                    nodens.logger.error(f"OH.update gait_params. e: {e}")

            else:
                # Record new values if track did not previously exist
                #if track_id != []:
                try:
                    self.new_track(sensor_id,track_id,X,Y,new_sensor_flag=0)
                except Exception as e:
                    nodens.logger.error(f"OH.update new_track 1. e: {e}")
        else:
            try:
                self.new_sensor(sensor_id)
            except Exception as e:
                    nodens.logger.error(f"OH.update new_sensor. e: {e}")
            if track_id != []:
                try:
                    self.new_track(sensor_id,track_id,X,Y,new_sensor_flag=1)
                except Exception as e:
                    nodens.logger.error(f"OH.update new_track 2. e: {e}")


    # Procedure when a new track is detected
    def new_track(self,sensor_id,track_id,X,Y,new_sensor_flag):
        ind_s = self.sensor_id.index(sensor_id)
        # if new_sensor_flag == 0:
        self.id[ind_s].append(track_id)
        
        self.x0[ind_s].append(X)
        self.y0[ind_s].append(Y)
        self.x1[ind_s].append(X)
        self.y1[ind_s].append(Y)

        self.tot_dist[ind_s].append(0)
        self.max_dist[ind_s].append(0)
        self.flag_active[ind_s].append(1)   # By default mark them as active
        self.time_inactive_start[ind_s].append(dt.datetime.now(dt.timezone.utc))
        
        ind_t = self.id[ind_s].index(track_id)
        if ind_t > self.xh.shape[1]-1:
            new_track = np.empty((self.xh.shape[0],self.xh.shape[1],self.num_hist_frames),dtype=object)
            self.xh = np.concatenate((self.xh,new_track),axis=1)
            self.yh = np.concatenate((self.yh,new_track),axis=1)
        self.xh[ind_s][ind_t][0] = X
        self.yh[ind_s][ind_t][0] = Y

        # Gait paramaters sensor_id, track_id, Xh, Yh
        self.gait_params[ind_s].add_new_track(sensor_id, track_id, self.xh[ind_s][ind_t], self.yh[ind_s][ind_t])
        
    # Procedure when a new sensor is detected
    def new_sensor(self,sensor_id):
        #self.max_tracks.append(0)
        self.sensor_id.append(sensor_id)
        self.most_inactive_track.append(None)
        self.most_inactive_time.append(None)
        if len(self.sensor_id) == 1:
            self.xh = np.array(np.empty((self.num_hist_frames,),dtype=object), ndmin=3)
            self.yh = np.array(np.empty((self.num_hist_frames,),dtype=object), ndmin=3)
            self.e_ud_h = np.array(np.empty((self.num_hist_frames,),dtype=object), ndmin=2)
            self.e_pc_h = np.array(np.empty((self.num_hist_frames,),dtype=object), ndmin=2)
        else:
            new_sensor = np.empty((1,self.xh.shape[1],self.xh.shape[2]),dtype=object)
            self.xh = np.concatenate((self.xh,new_sensor),axis=0)
            self.yh = np.concatenate((self.yh,new_sensor),axis=0)
            new_sensor = np.empty((1,self.e_ud_h.shape[1]),dtype=object)
            self.e_ud_h = np.concatenate((self.e_ud_h,new_sensor),axis=0)
            self.e_pc_h = np.concatenate((self.e_pc_h,new_sensor),axis=0)

        self.id.append([])
        self.x0.append([])
        self.y0.append([])
        self.x1.append([])
        self.y1.append([])

        self.tot_dist.append([])
        self.max_dist.append([])
        self.flag_active.append([])    # By default mark them as active
        self.time_inactive_start.append([])

        self.track_del_flag.append([])

        # Room heatmap
        self.room_heatmap.append(OccupantHeatmap(sensor_id, Xres=0.25, Yres=0.25, Xrange=[-4.5,4.5], Yrange=[0,5]))

        # Gait parameters
        self.gait_params.append(GaitParameters(sensor_id, num_hist_frames=self.num_hist_frames))

    # Procedure to delete a track when it has left
    def delete_track(self,sensor_id,track_id, mark_to_delete=1):
        """This function can be used to specific tracks, or to mark them for deletion
        mark_to_delete=1. track_id is all *safe* tracks (i.e. tracks to keep); typically done by inputting an array of current tracks.
        mark_to_delete=0. track_id is the track to delete."""

        ind_s = self.sensor_id.index(sensor_id)

        if mark_to_delete == 1:
            for track in self.id[ind_s]:
                if track not in track_id:
                    self.track_del_flag[ind_s].append(track)
        else:
            ind_t = self.id[ind_s].index(track_id)

            self.x0[ind_s].pop(ind_t)
            self.y0[ind_s].pop(ind_t)
            self.x1[ind_s].pop(ind_t)
            self.y1[ind_s].pop(ind_t)

            self.tot_dist[ind_s].pop(ind_t)
            self.max_dist[ind_s].pop(ind_t)
            self.flag_active[ind_s].pop(ind_t)   # By default mark them as active
            self.time_inactive_start[ind_s].pop(ind_t)
            
            self.xh[ind_s][ind_t] = np.empty((self.num_hist_frames),dtype=object)
            self.yh[ind_s][ind_t] = np.empty((self.num_hist_frames),dtype=object)

            self.id[ind_s].pop(ind_t)

            # Delete gait params
            self.gait_params[ind_s].delete_track(sensor_id, track_id)
    
    # Use this to check entryways and see if anyone has entered/left the room
    def entryway(self, sensor_id, track_id, ew):
        if (sensor_id in ew.id):
            ind_s = self.sensor_id.index(sensor_id)
            ind_e = ew.id.index(sensor_id)
            ind_t = self.id[ind_s].index(track_id)
            [sx0,sx1] = [self.x0[ind_s][ind_t],self.x1[ind_s][ind_t]]
            [sy0,sy1] = [self.y0[ind_s][ind_t],self.y1[ind_s][ind_t]]
            
            try:
                if abs(sx0-sx1)+abs(sy0-sy1) > 0:
                    # if len(ew.x[ind_e]) == 0:
                    #     nodens.logger.debug('No entries defined')
                    for i in range(int(len(ew.x[ind_e])/2)):
                
                        [ex0,ex1] = [ew.x[ind_e][2*i],ew.x[ind_e][2*i+1]]
                        [ey0,ey1] = [ew.y[ind_e][2*i],ew.y[ind_e][2*i+1]]
                        t = ((sx0-ex0)*(ey0-ey1) - (sy0-ey0)*(ex0-ex1))/((sx0-sx1)*(ey0-ey1) - (sy0-sy1)*(ex0-ex1))
                        u = ((sx1-sx0)*(sy0-ey0) - (sy1-sy0)*(sx0-ex0))/((sx0-sx1)*(ey0-ey1) - (sy0-sy1)*(ex0-ex1))
                        if (0<=t<=1) and (0<=u<=1):
                            if (sx0**2 + sy0**2) > (sx1**2 + sy1**2):
                                ew.count[ind_e] += 1
                                nodens.logger.info('Entered room at entry {} with (t,u)=({},{}). Occupancy = {}.'.format(i,t,u,ew.count[ind_e]))
                            else:
                                ew.count[ind_e] -= 1
                                if ew.count[ind_e] < 0:
                                    ew.count[ind_e] = 0
                                    nodens.logger.warning('Warning! Count dropped below 0 and was reset.')
                                nodens.logger.info('Leaving room at entry {} with (t,u)=({},{}). Occupancy = {}.'.format(i,t,u,ew.count[ind_e]))
            except:
                nodens.logger.warning('Entryway update issue. (sx0,sx1)=({},{}). (sy0,sy1)=({},{})'.format(sx0,sx1,sy0,sy1))
    
    # Track activity/inactivity statistics
    def activity_detection(self, sensor_id, track_id, tot_dist_thresh=1, max_dist_thresh=1):
        ind_s = self.sensor_id.index(sensor_id)
        ind_t = self.id[ind_s].index(track_id)

        xh_check = self.xh[ind_s][ind_t][1:]

        if all( x is None for x in xh_check) == False :
            
            
            # Non-None values from history
            xh =  [val for i,val in enumerate(self.xh[ind_s][ind_t]) if val is not None]
            yh =  [val for i,val in enumerate(self.yh[ind_s][ind_t]) if val is not None]

            # Calculate distances for each frame
            try:
                xd = np.subtract(xh[1:],xh[0:-1])
                yd = np.subtract(yh[1:],yh[0:-1])
                rd = (xd**2 + yd**2)**0.5

                # Find statistics
                self.tot_dist[ind_s][ind_t] =  np.sum(rd)
                self.max_dist[ind_s][ind_t] = np.max(rd)

                # Check if active
                if self.tot_dist[ind_s][ind_t] > tot_dist_thresh:
                    self.flag_active[ind_s][ind_t] = 1
                    #print("Active!)")
                elif self.max_dist[ind_s][ind_t] > max_dist_thresh:
                    self.flag_active[ind_s][ind_t] = 1
                    #print("Active!)")
                else:
                    if (self.flag_active[ind_s][ind_t] == 1):
                        self.time_inactive_start[ind_s][ind_t] = dt.datetime.now(dt.timezone.utc)
                    self.flag_active[ind_s][ind_t] = 0

            except Exception as e:
                nodens.logger.error(f"""OH.activity_detection. {e.args}. sensor_id: {sensor_id}. track_id: {track_id}.""")
            #print("Inactive since {} for track: {} with dist: {}".format(self.time_inactive_start[ind_s][ind_t], track_id, self.tot_dist[ind_s][ind_t], self.max_dist[ind_s][ind_t]))

        # Calculate total energies for each frame
        # try:
        #     ud_e = [val for val in self.e_ud_h[ind_s][ind_t] if val is not None]
        #     print(f"ud: {ud_e}")


    # Calculate general activity statistics
    def sensor_activity(self, sensor_id):
        ind_s = self.sensor_id.index(sensor_id)
        inactive_tracks = [self.time_inactive_start[ind_s][i] for i,val in enumerate(self.flag_active[ind_s]) if val==0]
        if len(inactive_tracks) == 0:
            self.most_inactive_track[ind_s] = None
            self.most_inactive_time[ind_s] = None
        else:
            inactive_idx = min(range(len(inactive_tracks)), key=inactive_tracks.__getitem__)
            self.most_inactive_track[ind_s] = self.id[ind_s][inactive_idx]
            self.most_inactive_time[ind_s] = dt.datetime.now(dt.timezone.utc) - self.time_inactive_start[ind_s][inactive_idx]

    # Calculate outputs
    def calculate_outputs(self, sensor_id, thresh_distance = 0, energy_threshold = 0):
        # Re-initialise outputs
        self.outputs = []
        #self.outputs.__init__()

        ind_s = self.sensor_id.index(sensor_id)

            
        if len(self.outputs) <= ind_s:
            while True:
                self.outputs.append(self.Outputs())
                if len(self.outputs) > ind_s:
                    break

        self.outputs[ind_s] = self.Outputs()
        self.outputs[ind_s].sensor_id = sensor_id
        if len(self.id[ind_s]) > 0:
            # Determine track to send
            if max(self.tot_dist[ind_s]) >= thresh_distance: # Distance threshold at 0 for now, until UD sig tid is found.
                tid = self.tot_dist[ind_s].index(max(self.tot_dist[ind_s]))

                self.outputs[ind_s].track_id = self.id[ind_s][tid]

                # Record parameters
                self.outputs[ind_s].track_X = self.x1[ind_s][tid]
                self.outputs[ind_s].track_Y = self.y1[ind_s][tid]
                self.outputs[ind_s].distance_moved = self.tot_dist[ind_s][tid]
                
            else:
                pass
                #tid = self.ud_energy[ind_s].index(max(self.ud_energy[ind_s]))

            # Gait parameters
            self.gait_params[ind_s].calculate_gait_parameters()
            self.outputs[ind_s].gait_string = self.gait_params[ind_s].gait_str

        # Energy statistics (for scene not track)
        ud_e = [val for val in self.e_ud_h[ind_s] if val is not None]
        self.outputs[ind_s].ud_energy = sum(ud_e)
        if self.outputs[ind_s].ud_energy > energy_threshold:
            self.outputs[ind_s].was_active = 1
        else:
            self.outputs[ind_s].was_active = 0
        pc_e = [val for val in self.e_pc_h[ind_s] if val is not None]
        self.outputs[ind_s].pc_energy = sum(pc_e)
        
        # Room heatmaps
        self.room_heatmap[ind_s].prepare_heatmap_string()
        self.outputs[ind_s].heatmap_string = self.room_heatmap[ind_s].heatmap_string

        # Delete tracks which have left
        for ind_t, track in enumerate(self.id[ind_s]):
            if track in self.track_del_flag[ind_s]:
                self.delete_track(sensor_id,track,mark_to_delete=0)
        self.track_del_flag[ind_s] = []

        return ind_s


    
    # Class to define outputs
    class Outputs:
        def __init__(self) -> None:
            self.sensor_id = []
            self.track_id = []  # tid with highest distance walked, or if under threshold then highest energy
            self.track_X = []   # corresponding location for tid
            self.track_Y = []
            self.distance_moved = []   # total distance moved
            self.was_active = []        # check if ud_energy over threshold
            self.ud_energy = []
            self.pc_energy = []
            self.heatmap_string = []    # Array composed of heatmap strings
            self.gait_string = []       # Array composed of gait speed distribution
        
                    
                
        



class RX_Data:
    def __init__(self, header, data):
        self.header = header
        self.data = data
        
    def frame_num(self):
        self.frame_num = self.header[24] + 256*self.header[25] + 65536*self.header[26] + 16777216*self.header[27]

        
class point_cloud:
    """An old point cloud TLV"""
    def __init__(self,raw):
        self.num_obj = int((np.uint8(raw[4:8]).view(np.uint32) - 8 - 16)/6)
        self.angle_unit = np.array(raw[8:12], dtype='uint8').view('<f4')
        self.dopp_unit = np.array(raw[12:16], dtype='uint8').view('<f4')
        self.rng_unit = np.array(raw[16:20], dtype='uint8').view('<f4')
        self.snr_unit = np.array(raw[20:24], dtype='uint8').view('<f4')
        
        self.angle = []
        self.dopp = []
        self.rng = []
        self.snr = []
        for i in range(self.num_obj):
            self.angle.append(np.int8(raw[24 + 6*i]) * self.angle_unit)
            self.dopp.append(np.int8(raw[25 + 6*i]) * self.dopp_unit)
            self.rng.append(np.uint8(raw[(26+6*i):(28+6*i)]).view(np.uint16) * self.rng_unit)
            self.snr.append(np.uint8(raw[(28+6*i):(30+6*i)]).view(np.uint16) * self.snr_unit)
        
        self.X = self.rng * np.sin(np.deg2rad(self.angle))
        self.Y = self.rng * np.cos(np.deg2rad(self.angle))

class point_cloud_3D_new:
    """Point cloud 3D TLV, parsed based on firmware version."""
    def __init__(self,raw,radar_version='R3D001B'):
        # Version check: is SNR in TLV
        if radar_version == 'R3D002A':
            flag_snr = True
        else:
            flag_snr = False

        if len(raw) == 0:
            self.num_obj = 0
        else:
            if flag_snr:
                self.num_obj = int((np.uint8(raw[4:8]).view(np.uint32) - 8 - 20)/8)
            else:
                self.num_obj = int((np.uint8(raw[4:8]).view(np.uint32) - 8 - 16)/6)

        self.elev_unit = np.array(raw[8:12], dtype='uint8').view('<f4')
        self.azim_unit = np.array(raw[12:16], dtype='uint8').view('<f4')
        self.dopp_unit = np.array(raw[16:20], dtype='uint8').view('<f4')
        self.rng_unit = np.array(raw[20:24], dtype='uint8').view('<f4')
        
        self.elev = []
        self.azim = []
        self.dopp = []
        self.rng = []

        if flag_snr == True:
            self.snr_unit = np.array(raw[24:28], dtype='uint8').view('<f4')
            self.snr = []
            j = 28
            J = 8
        else:
            j = 24
            J = 6

        
        for i in range(self.num_obj):
            self.elev.append(np.int8(raw[j+J*i]) * self.elev_unit)
            self.azim.append(np.int8(raw[j+1+J*i]) * self.azim_unit)
            self.dopp.append(np.uint8(raw[(j+2+J*i):(j+4+J*i)]).view(np.int16) * self.dopp_unit)
            self.rng.append(np.uint8(raw[(j+4+J*i):(j+6+J*i)]).view(np.uint16) * self.rng_unit)
            if flag_snr == True:
                self.snr.append(np.uint8(raw[(j+6+J*i):(j+8+J*i)]).view(np.uint16) * self.snr_unit)
        
        self.X = self.rng * np.sin((self.azim)) * np.cos((self.elev))
        self.Y = self.rng * np.cos((self.azim)) * np.cos((self.elev))
        self.Z = self.rng * np.sin((self.elev))

        self.energy = np.sqrt(sum([val**2 for val in self.dopp]))

        
    

class PointCloudHistory:
    """This class stores the point cloud history over the last num_hist_frames frames.
    Each frame is composed of arrays of X,Y,Z spatial coordinates, and an array of Doppler values."""

    # TODO: define number of frames to store (currently set as 3)
    def __init__(self,num_hist_frames=10):
        """Initialises the point cloud histories."""
        self.X = np.array(np.empty((num_hist_frames,),dtype=object), ndmin=1)
        self.Y = np.array(np.empty((num_hist_frames,),dtype=object), ndmin=1)
        self.Z = np.array(np.empty((num_hist_frames,),dtype=object), ndmin=1)
        self.dopp = np.array(np.empty((num_hist_frames,),dtype=object), ndmin=1)
        self.num_pnts = np.array(np.empty((num_hist_frames,),dtype=object), ndmin=1)

    def update_history(self,pc):
        """Updates the point cloud history with the latest point cloud measurements."""
        # circular buffer
        self.X = np.roll(self.X, 1)
        self.Y = np.roll(self.Y, 1)
        self.Z = np.roll(self.Z, 1)
        self.dopp = np.roll(self.dopp, 1)
        self.num_pnts = np.roll(self.num_pnts, 1)

        # Update most recent frame
        self.X[0] = pc.X
        self.Y[0] = pc.Y
        self.Z[0] = pc.Z
        self.dopp[0] = pc.dopp
        self.num_pnts[0] = pc.num_obj
        
class track:
    """Track data. Tracks are typically room occupants."""
    def __init__(self, raw, version=3.112):
        self.tid = []
        self.X = []
        self.Y = []

        if np.floor(version) == 3:
            self.Z = []
        if len(raw) == 0:
            self.num_tracks = 0
        else:
            if np.floor(version) == 2:
                tlv_len = 68
            elif version == 3.40:
                tlv_len = 40
            elif version == 3.112:
                tlv_len = 112
            self.num_tracks = int((np.uint8(raw[4:8]).view(np.uint32) - 8)/tlv_len)

            for i in range(self.num_tracks):
                self.tid.append(np.uint8(raw[(8+tlv_len*i):(12+tlv_len*i)]).view(np.uint32)[0])
                self.X.append(np.uint8(raw[(12+tlv_len*i):(16+tlv_len*i)]).view('<f4')[0])
                self.Y.append(np.array(raw[(16+tlv_len*i):(20+tlv_len*i)], dtype='uint8').view('<f4')[0])
                if int(np.floor(version)) == 3:
                    self.Z.append(np.uint8(raw[(20+tlv_len*i):(24+tlv_len*i)]).view('<f4')[0])

class PresenceDetect:
    """Processes radar TLV related to presence detction"""
    def __init__(self) -> None:
        self.present = 0
        self.tlv_len = []

    def process(self, raw):
        try:
            self.tlv_len = np.uint8(raw[4:8]).view(np.uint32)[0]
            self.present = raw[8]
        except Exception as e:
            nodens.logger.warning(f"PresenceDetect.process: {e}. raw: {raw}")
            self.tlv_len = 0

class sensorTimeSeries:
    def __init__(self):
        self.frame = []
        self.packet_len = []
        self.num_tlv = []
        self.num_pnts = []
        self.num_tracks = []

        # Some stats
        self.count = 0
        self.total_frame_drop = 0
        self.min_frame_drop = 100000
        self.max_frame_drop = 0
        self.avg_frame_drop = 0

    def update(self, sensor_data, max_time_samples = 0):
        self.frame.append(sensor_data.frame)
        self.packet_len.append(sensor_data.packet_len)
        self.num_tlv.append(sensor_data.num_tlv)
        self.num_pnts.append(sensor_data.pc.num_obj)
        self.num_tracks.append(sensor_data.track.num_tracks)

        self.count += 1
        if self.count > 1:
            try:
                if isinstance(self.frame[-1], (float, int)) and isinstance(self.frame[-2], (float, int)):
                    if self.frame[-1] > self.frame[-2]:
                        frame_drop = self.frame[-1] - self.frame[-2]
                        self.total_frame_drop += frame_drop

                        if frame_drop > self.max_frame_drop:
                            self.max_frame_drop = frame_drop
                        
                        if frame_drop < self.min_frame_drop:
                            self.min_frame_drop = frame_drop

                        self.avg_frame_drop = self.total_frame_drop / self.count

                    else:
                        print(f"Frames not sequential. frame -1: {self.frame[-1]}. frame -2: {self.frame[-2]}")
                else:
                    print(f"Frames not a number. frame -1: {self.frame[-1]}. frame -2: {self.frame[-2]}")
            except:
                print(f"Frame count error {self.frame[-1]} {self.frame[-2]} {isinstance(self.frame[-1], (float, int))}")


        if max_time_samples < 0:
            print("WARNING: max_time_samples (= {}) must be greater than 0. Setting to 0.")
        elif max_time_samples > 0:
            if len(self.frame) > max_time_samples:
                self.frame = self.frame[1:]
                self.packet_len = self.packet_len[1:]
                self.num_tlv = self.num_tlv[1:]
                self.num_pnts = self.num_pnts[1:]
                self.num_tracks = self.num_tracks[1:]


class VitalSigns:
    """Storage of vital signs data."""
    def __init__(self, num_hist_samples = 100):
        self.heart_rate_raw = [None] * num_hist_samples
        self.breathing_rate_raw = [None] * num_hist_samples
        self.breathing_deviation = [None] * num_hist_samples
        self.heart_vote = [None] * num_hist_samples
        self.breathing_vote = [None] * num_hist_samples
        self.X = []
        self.Y = []
        self.heart_waveform = [None] * 95
        self.breathing_waveform = [None] * 95
        self.heart_rate = []
        self.breathing_rate = []
        self.heart_msg = ''
        self.breathing_msg = ''

    def update(self, raw):
        # Calculate target position
        r_res = 0.06
        a_res = 0.001
        r_idx = np.uint8(raw[(28):(30)]).view(np.uint16)[0]
        a_idx = np.uint8(raw[(30):(32)]).view(np.uint16)[0]
        X = r_idx*r_res * np.sin(a_idx*a_res)
        Y = r_idx*r_res * np.cos(a_idx*a_res)

        # Check (via proximity) if it's the previous target. If not, re-initialise
        # TODO: record tid on sensor
        if self.X != []:
            if (np.sqrt((X-self.X)**2 + (Y-self.Y)**2)) > 1:
                nodens.logger.debug("RESET VS: {}".format((np.sqrt((X-self.X)**2 + (Y-self.Y)**2))))
                self.__init__()
        
        # Roll history data through circular buffer
        self.heart_rate_raw = np.roll(self.heart_rate_raw, 1)
        self.breathing_rate_raw = np.roll(self.breathing_rate_raw, 1)
        self.breathing_deviation = np.roll(self.breathing_deviation, 1)
        self.heart_vote = np.roll(self.heart_vote, 1)
        self.breathing_vote = np.roll(self.breathing_vote, 1)

        # Get values
        self.X = X
        self.Y = Y
        self.heart_rate_raw[0] = np.uint8(raw[(8):(12)]).view('<f4')[0]
        self.breathing_rate_raw[0] = np.uint8(raw[(12):(16)]).view('<f4')[0]
        self.breathing_deviation[0] = np.uint8(raw[(16):(20)]).view('<f4')[0]
        self.heart_vote[0] = np.uint8(raw[20:24]).view('<f4')[0]
        self.breathing_vote[0] = np.uint8(raw[24:28]).view('<f4')[0]
        for i in range(95):
            temp = np.uint8(raw[(32+4*i):(36+4*i)]).view('<f4')[0]
            self.heart_waveform[i] = temp
            temp = np.uint8(raw[(412+4*i):(416+4*i)]).view('<f4')[0]
            self.breathing_waveform[i] = temp

        # Calculate values and Set messages
        if self.heart_rate_raw[0] != None:
            self.heart_rate = np.median([i for i in self.heart_rate_raw[0:10] if i != None])
            nodens.logger.debug(self.heart_rate, self.heart_rate_raw[0])
            if self.heart_rate_raw[0] - self.heart_rate > 8:
                self.heart_rate = self.heart_rate_raw[0]
            self.heart_msg = "Heart rate: {:.1f}".format(self.heart_rate)
            nodens.logger.info(self.heart_msg)
        else:
            self.heart_msg = "No heart rate detected"

        if self.breathing_rate_raw[0] != None:
            self.breathing_rate = np.median([i for i in self.breathing_rate_raw[0:10] if i != None])
            if self.breathing_rate_raw[0] - self.breathing_rate > 5:
                self.breathing_rate = self.breathing_rate_raw[0]

            if self.breathing_deviation[0] == 0:
                self.breathing_msg = "No presence detected"
            elif self.breathing_deviation[0] < 0.02:
                self.breathing_msg = "Holding breath!"
            else:
                self.breathing_msg = "Breathing rate: {:.1f}".format(self.breathing_rate)
        else:
            self.breathing_msg = "No breathing rate detected"


class MicroDoppler:
    """Micro-Doppler (UD) parameters and signatures."""
    def __init__(self):
        self.tid = []
        self.num_pnts = []
        self.azim = self.udFrameParam()
        self.elev = self.udFrameParam()
        self.range = self.udFrameParam()
        self.dopp = self.udFrameParam()
        self.z = self.udFrameParam()
        self.signature_energy = 0

    def signature(self, raw, Nud, spec_length, Nchirps):
        #TODO: add number of targets
        # check number of chirps compared to fft length
        if Nchirps > spec_length:
            Nchirps = spec_length
            nodens.logger.warning("Nchirps should be <= spec_length")

        # Check number of points
        
        # Save signature
        output = np.zeros([Nchirps,Nud])
        for i in range(Nchirps):
            for j in range(Nud):
                output[i,j] = raw[i + j*spec_length + 24]
        for j in range(Nud):
            if sum(output[:,j]) == 255*Nchirps:
                output[:,j] = 0*output[:,j]
        output = np.fft.fftshift(output, axes=0)
        #print(output)

        return output

    def calculate_sig_energy(self,ud_sig):
        self.signature_energy = np.sum(ud_sig)

    def parameters(self,raw):
        # General
        self.num_pnts = convert_4_to_1(raw[12:14])

        # Azimuth
        self.azim.mean = 0.01*180/np.pi*convert_uint_to_int(raw[14])
        self.azim.high_freq_env = self.azim.mean+0.01*180/np.pi*(raw[15])
        self.azim.low_freq_env = self.azim.mean-0.01*180/np.pi*(raw[16])
        #self.azim.maxmin()

        # Elevation
        self.elev.mean = 0.01*180/np.pi*convert_uint_to_int(raw[17])
        self.elev.high_freq_env = self.elev.mean+0.01*180/np.pi*(raw[18])
        self.elev.low_freq_env = self.elev.mean-0.01*180/np.pi*(raw[19])
        #self.elev.maxmin()

        # Range
        self.range.mean = 0.00025*convert_4_to_1(raw[20:22])
        self.range.high_freq_env = self.range.mean+0.00025*convert_4_to_1(raw[22:24])
        self.range.low_freq_env = self.range.mean-0.00025*convert_4_to_1(raw[24:26])
        #self.range.maxmin()

        # Doppler
        self.dopp.mean = 0.00028*convert_uint_to_int(raw[26:28])
        self.dopp.high_freq_env = self.dopp.mean+0.00028*convert_4_to_1(raw[28:30])
        self.dopp.low_freq_env = self.dopp.mean-0.00028*convert_4_to_1(raw[30:32])
        #self.dopp.maxmin()

        # Z
        self.z.mean = self.range.mean * np.sin(np.deg2rad(self.elev.mean))
        self.z.high_freq_env = self.range.high_freq_env * np.sin(np.deg2rad(self.elev.high_freq_env))
        self.z.low_freq_env = self.range.low_freq_env * np.sin(np.deg2rad(self.elev.low_freq_env))


    class udFrameParam:
        def __init__(self):
            self.mean = []
            self.high_freq_env = []
            self.low_freq_env = []


class udFrameParam:
    def __init__(self):
        self.mean = []
        self.hf = []
        self.lf = []

    #def maxmin(self):
    #    self.max = self.mean + self.high_freq_env
    #    self.min = self.mean + self.low_freq_env

class paramMaxMin:
    def __init__(self):
        self.max = 0
        self.min = 10000
        self.sum = 0
        

class paramHfLf:
    def __init__(self):
        self.hf = []
        self.lf = []

        x = [p for p in vars(self)]
        for i in range(len(x)):
            setattr(self,x[i],paramMaxMin())

class udHistParam:
    """Micro-Doppler parameters processed over a defined number of frames (previous are single-frame)."""
    def __init__(self, num_frames):
        self.count = 0
        self.num_pnts = 0
        self.azim = udFrameParam()
        self.elev = udFrameParam()
        self.range = udFrameParam()
        self.dopp = udFrameParam()

        # Initialise each measured object (azim,elev,range,dopp)
        x = [p for p in vars(self)]
        for i in range(2,len(x)):
            setattr(self,x[i],paramHfLf())

    def update(self,udParam, num_frames):
        # azim, elev, range, dopp
        x = [p for p in vars(self)]
        print("********\n",x)
        for i in range(2,len(x)):
            # mean, hf, lf
            y = [p for p in vars(getattr(self,x[i]))]
            for j in range(len(y)):
                temp = [-10000, 10000, 0, 0] # [max, min, sum, frame value]
                for k in range(num_frames):
                    temp[3] = getattr(getattr(udParam,x[i]),y[j])
                    temp[0] = max(temp[0], temp[3])
                    temp[1] = min(temp[1], temp[3])
                    temp[2] += temp[3]

                #TODO: next step is to populate the values

                # max, min, sum
                z = [p for p in vars(getattr(getattr(self,x[i]),y[j]))]
                for k in range(len(z)):
                    
                    setattr(
                        getattr(
                            getattr(
                                self,
                                x[i]
                            ),
                            y[j]
                        ),
                        z[k],
                        a2
                    )

        
    class paramMaxMin:
        def __init__(self):
            self.max = 0
            self.min = 10000
            self.sum = 0

## ~~~ CLASSIFICATION ~~~ ##

class classifierEngine:
    """Classifier engine. Currently a placeholder with a simple test."""
    def __init__(self, num_segments, class_frames_check, activity_wait_frames, energy_threshold):
        # Class buffer : class must have all positive hits to cause alert
        self.class_buffer = np.zeros(shape=[class_frames_check,])

        # Data buffers: used for calculating
        self.ud_sig_buffer = np.zeros(shape=[num_segments,])
        self.z_lf_buffer = np.zeros(shape=[num_segments,])
        self.z_track_buffer = np.zeros(shape=[num_segments,])

        self.ud_sig_energy = 0
        self.zt_bw = 0
        self.zt_grad_mean = 0
        self.z_lf = 0
        
        self.fall_score = 0
        self.jump_score = 0
        self.sit_score = 0
        
        self.activity_flag = 0
        self.classification = 0
        self.frames_since_activity = 0
        self.activity_wait_frames = activity_wait_frames

        self.energy_threshold = energy_threshold

        self.activity_alert = 0

    def framewise_calculation(self, sensor_data, t_idx):
        # Roll to remove oldest datapoint
        self.ud_sig_buffer = np.roll(self.ud_sig_buffer, 1)
        self.z_lf_buffer = np.roll(self.z_lf_buffer, 1)
        self.z_track_buffer = np.roll(self.z_track_buffer, 1)

        # Update with newest datapoint
        self.ud_sig_buffer[0] = sensor_data.ud.signature_energy
        try:
            self.z_lf_buffer[0] = sensor_data.ud.z.low_freq_env
        except:
            self.z_lf_buffer[0] = None
        try:
           self.z_track_buffer[0] = sensor_data.track.Z[t_idx]
        except:
            self.z_track_buffer[0] = None

        # Calculations
        self.ud_sig_energy = np.sum(self.ud_sig_buffer)
        if (np.isnan(self.z_track_buffer).all() == False):
            try:
                self.zt_bw = np.nanmax(self.z_track_buffer) - np.nanmin(self.z_track_buffer)
            except:
                self.zt_bw = 0
        else:
            self.zt_bw = 0
        self.zt_grad_mean = (self.z_track_buffer[-1] - self.z_track_buffer[0])/len(self.z_track_buffer)
        if (np.isnan(self.z_lf_buffer).all() == False):
            try:
                self.z_lf = np.nanmin(self.z_lf_buffer)
            except: 
                self.z_lf = 0
        else:
            self.z_lf = 0
        self.frames_since_activity += 1

    def activity_check(self):
        if self.ud_sig_energy > self.energy_threshold:
            self.activity_flag = 1
        else:
            self.activity_flag = 0

    def find_score(self, val, min_bnd, max_bnd):
        mid = (max_bnd + min_bnd)/2
        sig = (max_bnd - min_bnd)/2
        score = np.exp(-0.5*(val-mid)**2/(sig**2))

        return score

    def classify(self):
        self.fall_score_bw = self.find_score(self.zt_bw,0.85,1.2)
        self.fall_score_grad = self.find_score(self.zt_grad_mean,-0.12,-0.08)
        self.fall_score_lf = self.find_score(self.z_lf,-0.6,-0.4)
        self.fall_score_energy = self.find_score(self.ud_sig_energy,6600,17000)
        self.fall_score = 0.25*100*(self.fall_score_bw + self.fall_score_grad + 
                                   self.fall_score_lf + self.fall_score_energy)
        
        self.jump_score_bw = self.find_score(self.zt_bw,0.3,0.7)
        self.jump_score_grad = self.find_score(self.zt_grad_mean,-0.06,0.04)
        self.jump_score_lf = self.find_score(self.z_lf,-0.52,-0.43)
        self.jump_score_energy = self.find_score(self.ud_sig_energy,8700,17000)
        self.jump_score = 0.25*100*(self.jump_score_bw + self.jump_score_grad + 
                                   self.jump_score_lf + self.jump_score_energy)
        
        self.sit_score_bw = self.find_score(self.zt_bw,0.3,0.55)
        self.sit_score_grad = self.find_score(self.zt_grad_mean,-0.05,-0.01)
        self.sit_score_lf = self.find_score(self.z_lf,-0.85,-0.5)
        self.sit_score_energy = self.find_score(self.ud_sig_energy,2800,6000)
        self.sit_score = 0.25*100*(self.sit_score_bw + self.sit_score_grad + 
                                   self.sit_score_lf + self.sit_score_energy)

        self.activity_check()
        
        classes = ['None', 'Fall', 'Jump', 'Sit']
        # if self.activity_flag == 1:
        #     scores = [0, self.fall_score, self.jump_score, self.sit_score]
        #     self.class_buffer = np.roll(self.class_buffer, 1)
        #     self.class_buffer[0] = scores.index(max(scores))
        #     if np.min(self.class_buffer) == np.max(self.class_buffer) and self.frames_since_activity >= self.activity_wait_frames:
        #         self.classification = self.class_buffer[0][0]
        #         self.frames_since_activity = 0
        #         self.activity_alert = 1
        #         print("ACTIVITY DETECTED: {}".format(self.classification))
        #         print("Scores: {}, {}, {}".format(self.fall_score, self.jump_score, self.sit_score))

        # else:
        #     self.class_buffer = np.roll(self.class_buffer, 1)
        #     self.class_buffer[0] = 0

## ~~~~~~~~~~~~~~~~~~~~~~ ##

def convert_4_to_1(arg1, *argv):
    if  isinstance(arg1, (np.ndarray,)):
        arg1 = np.ndarray.tolist(arg1)
    if  isinstance(arg1, (list,)):   
        try:
            output = arg1[0]
            #if len(arg1) > 1:
            for x in range(1, len(arg1)):
                output += arg1[x]*256**x
        except:
            nodens.logger.error("convert_4_to_1 error. arg1: {}".format(arg1))
            output = 65536
    else:
        output = arg1
        x = 1
        for arg in argv:
            output += arg*256**x
            x += 1
            
    return output

def convert_uint_to_int(arg1):
    if isinstance(arg1, list):
        num_bits = 8*len(arg1)
    else:
        num_bits = 8
    x = convert_4_to_1(arg1)

    return x if x < 2**(num_bits-1) else x - 2**num_bits



class parseTLV:
    """Parse TLVs coming from the radar chip."""
    def __init__(self, version):
        if (version == 3):
            hl = 48
        self.packet_len = 0
        self.num_tlv = 0
        self.frame = 0
        self.pc = point_cloud_3D_new([], sv.radar_version)
        self.pc_history = PointCloudHistory()
        self.track = track([],3.112)
        self.ud_sig = np.zeros([64,40])
        self.ud = MicroDoppler()
        self.vs = VitalSigns()
        self.presence = PresenceDetect()
        self.message = []   # Use this to save any relevant messages to pass on to main process

    def update(self, version, data, Nud):
        if (version == 3):
            hl = 48
        self.packet_len = data[12] + 256*data[13]
        if len(data) < self.packet_len:
            nodens.logger.debug("Rx data size is smaller than expected. Expected: {}. Received: {}.".format(self.packet_len, len(data)))
            self.packet_len = len(data)
        self.num_tlv = data[44]
        self.frame = convert_4_to_1(data[20:24])
        j = hl
        flag_track = False
        flag_pc = False
        self.message = []
        while (j < self.packet_len):
            if (data[j:j+4] == [6,0,0,0]):
                flag_pc = True
                j,self.len6,self.data6 = self.tlvN(data,j)
                if (j <= self.packet_len):
                    self.pc = point_cloud_3D_new(self.data6, sv.radar_version)
                    self.pc_history.update_history(self.pc)

                # Enter the rest of the TLVs
            elif (data[j:j+4] == [7,0,0,0]): 
                flag_track = True
                j,self.len7,self.data7 = self.tlvN(data,j)
                if (j <= self.packet_len):
                    self.track = track(self.data7,3.112)
            elif (data[j:j+4] == [10,0,0,0]):
                j,self.len10,self.data10 = self.tlvN(data,j)
                print(f"TLV10. len:{self.len10}. data:{self.data10[0:12]} ")
                if (j <= self.packet_len):
                    self.vs.update(self.data10)
                    nodens.logger.debug("(X,Y): ({:.1f},{:.1f}). HR:{:.1f}. BR: {:.1f}.".format(self.vs.X, self.vs.Y,  self.vs.heart_rate, self.vs.breathing_rate))
                    nodens.logger.debug(" B dev: {}".format(self.vs.breathing_deviation[0:3]))
                    nodens.logger.debug(" B vote: {}".format(self.vs.breathing_vote[0:3]))
            elif (data[j:j+4] == [11,0,0,0]):
                j,self.len11,self.data11 = self.tlvN(data,j)
                self.presence.process(self.data11)
            elif (data[j:j+4] == [12,0,0,0]):   # UD signature 12
                j,self.len12,self.data12 = self.tlvN(data,j)
                #print(f"TLV12. len:{self.len12}. data:{self.data12[0:12]} ")
                if (j <= self.packet_len):
                    ud_sig_out = self.ud.signature(self.data12, Nud, 128, 64)
                    self.ud.calculate_sig_energy(ud_sig_out)
                    self.ud_sig = np.roll(self.ud_sig, -Nud, axis=1)
                    for i in range(64):
                        for k in range(Nud):
                            self.ud_sig[i,k+40-Nud] = ud_sig_out[i,k]
            elif (data[j:j+4] == [13,0,0,0]):   # UD parameters 13
                j,self.len13,self.data13 = self.tlvN(data,j)
                #print(f"TLV13. len:{self.len13}. data:{self.data13[0:12]} ")
                if (j <= self.packet_len):
                    #UD = ud()
                    self.ud.parameters(self.data13)
                #    self.elev = np.roll(self.elev,-1)
                #    self.elev[49] = UD.elev.mean
            else:
                j,lenN,dataN = self.tlvN(data,j)
        if flag_track is False:
            self.track = track([])
        if flag_pc is False:
            self.pc = point_cloud_3D_new([], sv.radar_version)
            self.pc_history.update_history(self.pc)

    def tlvN(self, data, j):
        if len(data) > j+8:
            lenN = convert_4_to_1(data[j+4:j+8])
            if (lenN == 65536):
                nodens.logger.warning("Data packet TLV length error. j: {}. len: {}.".format(j,len(data)))
            dataN = data[j:j+lenN]
            j += lenN
        else:
            nodens.logger.warning(f"End of data packet with remaining data: {data[j:]}. j: {j}. packet_length: {self.packet_len}")
            j = 65535
            lenN = 0
            dataN = []
            self.message = "EoP"
        
        return j,lenN,dataN

class sendCMDtoSensor(object):
    """Send a command (e.g. a new configuration) to the sensor via MQTT."""
    def full_data_off(rcp,cp):
        config_full_data = "CMD: FULL DATA OFF."

        payload_msg =[{ "addr" : [rcp.SENSOR_TARGET],
                        "type" : "json",
                        "data" : config_full_data + "\n"}]

        rcp.SENSOR_TOPIC = 'mesh/' + rcp.SENSOR_ROOT + '/toDevice'

        ndns_mesh.MESH.multiline_payload(cp.SENSOR_IP,cp.SENSOR_PORT,60, rcp.SENSOR_TOPIC,"", payload_msg)

    def full_data_on(rcp,cp):
        config_full_data = "CMD: FULL DATA OFF."
        # Parse Publish rates to payload #
        rate_unit = 2 # Baseline data transmission rate
        config_pub_rate = "CMD: PUBLISH RATE: " + str(round(2/rate_unit))
        payload_msg = [{ "addr" : [rcp.SENSOR_TARGET],
                            "type" : "json",
                            "data" : config_pub_rate + "\n"}]

        config_full_data = "CMD: FULL DATA ON. RATE: " + str(max(1,2/2))

        payload_msg.append({ "addr" : [rcp.SENSOR_TARGET],
                        "type" : "json",
                        "data" : config_full_data + "\n"})

        rcp.SENSOR_TOPIC = 'mesh/' + rcp.SENSOR_ROOT + '/toDevice'

        ndns_mesh.MESH.multiline_payload(cp.SENSOR_IP,cp.SENSOR_PORT,60, rcp.SENSOR_TOPIC,"", payload_msg)

    def request_version(rcp,cp,sv,sensor_target=[], sensor_root=[]):
        config_req = "CMD: REQUEST VERSION"

        if sensor_target == []:
            payload_msg =[{ "addr" : [rcp.SENSOR_TARGET],
                            "type" : "json",
                            "data" : config_req + "\n"}]
        else:
            payload_msg =[{ "addr" : [sensor_target],
                            "type" : "json",
                            "data" : config_req + "\n"}]

        if sensor_root == []:
            rcp.SENSOR_TOPIC = 'mesh/' + rcp.SENSOR_ROOT + '/toDevice'
            sensor_topic = 'mesh/' + rcp.SENSOR_ROOT + '/toDevice'
        else:
            sensor_topic = 'mesh/' + sensor_root + '/toDevice'
        

        ndns_mesh.MESH.multiline_payload(cp.SENSOR_IP,cp.SENSOR_PORT,60, sensor_topic,"", payload_msg)

        nodens.logger.info("Published sensor version request to {}".format(rcp.SENSOR_TOPIC))
        temp = 0
        while (1):
            if sv.string != []:
                nodens.logger.info("Version received. Version = {}. Dimensions = {}.".format(sv.string, sv.radar_dim))
                break
            elif temp < 20:
                nodens.logger.info("Waiting... {}".format(sv.string))
                temp += 1
                time.sleep(0.2)
            else:
                nodens.logger.info("No response to version request. Continue...")
                break

    def request_config(rcp,cp,sensor_target=[], sensor_root=[]):
        config_req = "CMD: REQUEST CONFIG"

        if sensor_target == []:
            payload_msg =[{ "addr" : [rcp.SENSOR_TARGET],
                            "type" : "json",
                            "data" : config_req + "\n"}]
        else:
            payload_msg =[{ "addr" : [sensor_target],
                            "type" : "json",
                            "data" : config_req + "\n"}]

        if sensor_root == []:
            rcp.SENSOR_TOPIC = 'mesh/' + rcp.SENSOR_ROOT + '/toDevice'
            sensor_topic = 'mesh/' + rcp.SENSOR_ROOT + '/toDevice'
        else:
            sensor_topic = 'mesh/' + sensor_root + '/toDevice'

        rcp.cfg_idx = 0
        rcp.cfg_sensorStart = 0
        ndns_mesh.MESH.multiline_payload(cp.SENSOR_IP,cp.SENSOR_PORT,60, sensor_topic,"", payload_msg)
       

    def start_config_proc(rcp,cp):
        config_req = "CMD: CONFIG STATE"

        payload_msg =[{ "addr" : [rcp.SENSOR_TARGET],
                        "type" : "json",
                        "data" : config_req + "\n"}]

        rcp.SENSOR_TOPIC = 'mesh/' + rcp.SENSOR_ROOT + '/toDevice'

        ndns_mesh.MESH.multiline_payload(cp.SENSOR_IP,cp.SENSOR_PORT,60, rcp.SENSOR_TOPIC,"", payload_msg)

    def end_config_proc(rcp,cp):
        config_req = "CMD: CONFIG FINISHED"

        payload_msg =[{ "addr" : [rcp.SENSOR_TARGET],
                        "type" : "json",
                        "data" : config_req + "\n"}]

        rcp.SENSOR_TOPIC = 'mesh/' + rcp.SENSOR_ROOT + '/toDevice'

        ndns_mesh.MESH.multiline_payload(cp.SENSOR_IP,cp.SENSOR_PORT,60, rcp.SENSOR_TOPIC,"", payload_msg)

    def ping_back(rcp, cp):
        config_req = "CMD: REQUEST PING"

        payload_msg =[{ "addr" : [rcp.SENSOR_TARGET],
                        "type" : "json",
                        "data" : config_req + "\n"}]

        rcp.SENSOR_TOPIC = 'mesh/' + rcp.SENSOR_ROOT + '/toDevice'

        ndns_mesh.MESH.multiline_payload(cp.SENSOR_IP,cp.SENSOR_PORT,60, rcp.SENSOR_TOPIC,"", payload_msg)

## ~~~~~~~~~~ MESSAGE SENDING BETWEEN PROCESSES (THREADS) ~~~~~~~~~~~~~~ ##

class MessagePipeline:
    def __init__(self):
        self.sensor_id = []
        self.flag_send = []
        self.message = []
        self.config_flag_send = []
        self.config_message = []


    def update(self, message):
        if message['addr'] in self.sensor_id:
            sens_idx = self.sensor_id.index(message['addr'])
            self.flag_send[sens_idx] = 1
            self.message[sens_idx] = message
        
        else:
            self.sensor_id.append(message['addr'])
            self.flag_send.append(1)
            self.message.append(message)

            # Initialise config params but leave empty
            self.config_flag_send.append(0)
            self.config_message.append([])

    def config_update(self, sensor_id, config_payload):
        config_message = {"type": "CONFIG", "addr":sensor_id, "payload":config_payload}
        if sensor_id in self.sensor_id:
            sens_idx = self.sensor_id.index(sensor_id)
            self.config_flag_send[sens_idx] = 1
            self.config_message[sens_idx] = config_message
        else:
            self.sensor_id.append(sensor_id)
            self.config_flag_send.append(1)
            self.config_message.append(config_message)

            # Initialise message params but leave empty
            self.flag_send.append(0)
            self.message.append([])

    def clear(self, index):
        if index < len(self.sensor_id):
            self.flag_send[index] = 0
            self.message[index] = ""
        else:
            nodens.logger.warning("Sensor index %d does not exist", index)

    def clear_config(self, index):
        if index < len(self.sensor_id):
            self.config_flag_send[index] = 0
            self.config_message[index] = ""
        else:
            nodens.logger.warning("Sensor index %d does not exist", index)    

## ~~~~~~~~~~ MESSAGE DIAGNOSTICS ~~~~~~~~~~~~~~ ##
class Counts:
    def __init__(self):
        self.sensor_id = []

        self.heartbeat = []
        self.full = []
        self.basic = []

        self.max_heartbeat = []
        self.max_full = []
        self.max_basic = []

        self.min_heartbeat = []
        self.min_full = []
        self.min_basic = []

    def new_sensor(self, sensor_id):
        self.sensor_id.append(sensor_id)

        self.heartbeat.append(0)
        self.full.append(0)
        self.basic.append(0)

        self.max_heartbeat.append(0)
        self.max_full.append(0)
        self.max_basic.append(0)

        self.min_heartbeat.append(100000000)
        self.min_full.append(100000000)
        self.min_basic.append(100000000)

    def initialise(self, sensor_id):
        if sensor_id not in self.sensor_id:
            self.new_sensor(sensor_id)

        ind_s = self.sensor_id.index(sensor_id)

        if self.heartbeat[ind_s] > self.max_heartbeat[ind_s]:
            self.max_heartbeat[ind_s] = self.heartbeat[ind_s]
        elif self.heartbeat[ind_s] < self.min_heartbeat[ind_s]:
            self.min_heartbeat[ind_s] = self.heartbeat[ind_s]

        if self.full[ind_s] > self.max_full[ind_s]:
            self.max_full[ind_s] = self.full[ind_s]
        elif self.full[ind_s] < self.min_full[ind_s]:
            self.min_full[ind_s] = self.full[ind_s]

        if self.basic[ind_s] > self.max_basic[ind_s]:
            self.max_basic[ind_s] = self.basic[ind_s]
        elif self.basic[ind_s] < self.min_basic[ind_s]:
            self.min_basic[ind_s] = self.basic[ind_s]

        self.heartbeat[ind_s] = 0
        self.full[ind_s] = 0
        self.basic[ind_s] = 0

    def reset(self, sensor_id):
        if sensor_id not in self.sensor_id:
            self.new_sensor(sensor_id)

        ind_s = self.sensor_id.index(sensor_id)

        self.max_heartbeat[ind_s] = 0
        self.max_full[ind_s] = 0
        self.max_basic[ind_s] = 0

        self.min_heartbeat[ind_s] = 100000000
        self.min_full[ind_s] = 100000000
        self.min_basic[ind_s] = 100000000

    def update(self, sensor_id, type):
        if sensor_id not in self.sensor_id:
            self.new_sensor(sensor_id)

        ind_s = self.sensor_id.index(sensor_id)

        if type == 'heartbeat':
            self.heartbeat[ind_s] += 1
        elif type == 'full':
            self.full[ind_s] += 1
        elif type == 'basic':
            self.basic[ind_s] += 1
        else:
            nodens.logger.error(f"COUNTS not found. type: {type}")

    def print_counts(self, sensor_id):
        ind_s = self.sensor_id.index(sensor_id)

        output = [[self.heartbeat[ind_s], self.full[ind_s], self.basic[ind_s]],
                  [self.max_heartbeat[ind_s], self.max_full[ind_s], self.max_basic[ind_s]],
                  [self.min_heartbeat[ind_s], self.min_full[ind_s], self.min_basic[ind_s]]]
        return output

# # Create a custom nodens.logger
# nodens.logger = logging.getnodens.logger(__name__)
# nodens.logger.setLevel(logging.DEBUG)

# # Create handlers
# log_file = user_log_dir(APPNAME, APPAUTHOR)+'/nodens_gateway.log'
# Path(user_log_dir(APPNAME, APPAUTHOR)).mkdir(parents=True, exist_ok=True)
# c_handler = logging.StreamHandler()
# f_handler = logging.FileHandler(log_file)

# c_handler.setLevel(logging.INFO)
# f_handler.setLevel(logging.DEBUG)

# # Create formatters and add it to handlers
# c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
# f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
# c_handler.setFormatter(c_format)
# f_handler.setFormatter(f_format)

# # Add handlers to the nodens.logger
# nodens.logger.addHandler(c_handler)
# nodens.logger.addHandler(f_handler)

## ~~~~~~~~~~ INITIALISE FUNCTIONS ~~~~~~~~~~~~~~ ## 
si = SensorInfo()               # Sensor info
ew = EntryWays()         # Entryway monitors
oh = OccupantHist(num_hist_frames=250)      # Occupant history
sm = SensorMesh()        # Sensor Mesh state
message_pipeline = MessagePipeline()
#cp = nodens.cp
rcp = radar_config_params()
sv = sensor_version()
class_eng = classifierEngine(11,5,100,3200)
sd = parseTLV(3)
counts = Counts()
#sts = sensorTimeSeries()