#!/usr/bin/python3
#print('nodens step0')

# Copyright NodeNs Medical Ltd. Author: Khalid Rajab, khalid@nodens.eu
# Captures multi-topic sensor MQTT data and publishes to GCP

# TODO: Command API
# TODO: Separate API script

import os
import datetime as dt
from os.path import dirname, join as pjoin
import numpy as np
import paho.mqtt.client as mqtt
import json
import base64
from pathlib import Path
import logging
import csv
import nodens.gateway as nodens
from nodens.gateway import nodens_fns as ndns_fns
from nodens.gateway import nodens_mesh as ndns_mesh
from platformdirs import user_documents_dir
import re

global mqttDataN
global T0
global idx_mqtt, idx_write
global file_save
global mqttData_SAVE, mqttData_SAVEFull
global heartbeat
global should_backoff

#global si
global cwd
global sv


#cwd = '/home/pi/nodens/'
#cwd = os.getcwd() + '/'
cwd = user_documents_dir() +'/' + nodens.APPAUTHOR + '/'

mqttDataN = [] 
mqttData_SAVE = []
mqttData_SAVEFull = []
heartbeat = ""

idx_mqtt = 0
idx_write = 0
T0 = dt.datetime.now(dt.timezone.utc)

if (nodens.cp.WRITE_FLAG == 1):
    file = 'data'
    sub_folder = 'Saved'
    Path(cwd+sub_folder).mkdir(parents=True, exist_ok=True)
    nodens.logger.info("SAVING DATA TO FOLDER: {}".format(cwd+sub_folder))

    file_save = pjoin(cwd, sub_folder, file)
    file_dtfmt = (T0.strftime("%Y") + T0.strftime("%m") + 
                                T0.strftime("%d") + T0.strftime("%H") + T0.strftime("%M"))
    file_save = file_save + file_dtfmt
    header = ['Time', 'Addr', 'num_occ', 'tid1', 'x1','y1','z1','tid2','x2','y2','z2','e', 'heatmap']                
    with open(file_save + ".csv", "a") as filehandle:
        writer = csv.writer(filehandle)
        # write the header
        writer.writerow(header)
    filehandle.close()

    header = ['Time', 'Addr', 'Full data']   
    with open(file_save + "_FULL.csv", "a") as filehandle:
        writer = csv.writer(filehandle)
        # write the header
        writer.writerow(header)
    filehandle.close()

######## ~~~~~~~~~~~~~~~~~~~~~~ ###############

# Function to clean invalid control characters
def clean_data(data):
    # Remove control characters except for allowed ones (e.g., newline, tab)
    return re.sub(r'[\x00-\x1F\x7F]', '', data)


# MQTT Message callback function #
def on_message_sensorN(client, userdata, msg):

    #getting data from mqtt
    global mqttDataN
    global mqttData_SAVE

    global T0
    global idx_mqtt, idx_write
    global file_save
    global mqttData_SAVE, mqttData_SAVEFull
    global heartbeat
    global print_text

    #global si, sv, sm

    #getting data from mqtt
    mqttDataN = (msg.payload)

    try:
         # Attempt to decode the data as UTF-8
        mqttDataN = mqttDataN.decode('utf-8', errors='ignore')
        # Clean the data to remove invalid control characters
        mqttDataN = clean_data(mqttDataN)
        mqttData = json.loads(mqttDataN)
    except UnicodeDecodeError as e:
        nodens.logger.error(f"Unicode decode error: {e}. Raw data: {mqttDataN}")
        # Handle the error by ignoring invalid bytes or replacing them
        mqttDataN = mqttDataN.decode('utf-8', errors='ignore')
        try:
            mqttData = json.loads(mqttDataN)
        except Exception as e:
            nodens.logger.error(f"{e.args}. Raw data: {mqttDataN}")
            mqttData = {}
    except json.JSONDecodeError as e:
        nodens.logger.error(f"JSON decode error: {e}. Raw data: {mqttDataN}")
        mqttData = {}
    except Exception as e:
        nodens.logger.error(f"Unexpected error: {e}. Raw data: {mqttDataN}")
        mqttData = {}

    try:
        # --- Temporarily handle V3 (new sensor) data --- #
        if nodens.cp.SENSOR_VERSION == 4:
            mqttData['type'] = 'v4'
            if 'sensorID' in mqttData:
                mqttData['addr'] = mqttData['sensorID']
            if 'rawData' in mqttData:
                mqttData['data'] = mqttData['rawData']
                
                data_len = len(mqttData['data'])
                if data_len % 4 != 0:
                    pad = (4 - (data_len % 4)) * "A"
                    mqttData['data'] += pad

            else:
                mqttData['data'] = mqttData
                
                # print(f"LEN: {data_len} {len(mqttData['data'])} {len(mqttData['data']) % 4} mqttData['data']: {mqttData['data']}")
    except Exception as e:
        nodens.logger.error(f"Error at start {e.args}.")
        mqttData = {}
    #print(f"mqttData: {mqttData}")
    # Get time
    T = dt.datetime.now(dt.timezone.utc)

    

    
    # ---- Parse Data ---- #
    
    idx_mqtt += 1
    idx_write += 1
    
    try:
        N = int(msg.topic[-1])
    except:
        N = 0
    
    if 'addr' in mqttData:
        # try:
        sen_idx = ndns_fns.si.check(mqttData)

        if (mqttData['addr'] not in ndns_fns.ew.id):
            ndns_fns.ew.id.append(mqttData['addr'])
            ndns_fns.ew.x.append([])
            ndns_fns.ew.y.append([])
            ndns_fns.ew.count.append(0)

        # Check if command is received
        try:
            if mqttData['data'][0:3] == "CMD":
                cmd_check = 1
            else:
                cmd_check = 0
        except:
            cmd_check = 0
        if cmd_check == 1:
            nodens.logger.warning("receive_cmd")
            ndns_mesh.MESH.status.receive_cmd(mqttData['data'], T, mqttData['addr'])
            ndns_fns.sm.update_config(mqttData)
        else:
            # Parse data 
            try:
                data = base64.b64decode(mqttData['data'])
                #print(f"data: {data}")     # Temp KZR
            except Exception as e:
                data = mqttData['data']

            try:  
                str_data = str(data[0])
                data_int = [data[0]]

                if len(data) > 6:
                    for i in range(7):
                        str_data = str_data + str(data[i+1])
                        data_int.append(data[i+1])
                else:
                    nodens.logger.warning("Data below length 8. Rx: {}".format(data))
            except Exception as e:
                str_data = ''

            # Check if full data packet received
            try:
                if str_data == '21436587':
                    ndns_fns.counts.update(mqttData['addr'], 'full')
                    for i in range(len(data)-8):
                        str_data = str_data + str(data[i+8])
                        data_int.append(data[i+8])
                    mqttDataFinal = mqttData

                    # Parse TLVs
                    ndns_fns.sd.update(nodens.cp.SENSOR_VERSION, data_int, 5)
                    #ndns_fns.sts.update(ndns_fns.sd,1000)
                    ndns_fns.class_eng.framewise_calculation(ndns_fns.sd, 0)
                    ndns_fns.class_eng.classify()

                    ndns_fns.si.update_full(sen_idx, T, ndns_fns.sd)

                    # Print frame count stats
                    #print(f"FRAME STATS \n\tFrame: {ndns_fns.sts.frame[-1]} \n\tAverage frame skip: {ndns_fns.sts.avg_frame_drop} \n\tMin frame skip: {ndns_fns.sts.min_frame_drop} \tMax frame skip: {ndns_fns.sts.max_frame_drop}")

                    # print("num_pnts:")
                    # print(ndns_fns.sd.pc_history.num_pnts)
                    # print(ndns_fns.sts.num_pnts)

                    heartbeat += "F"
                    heartbeat = "\r" + heartbeat
                    #print(heartbeat, end='')
                    mqttDataTemp = [T.strftime("%H:%M:%S")]
                    mqttDataTemp.append(mqttData['addr'])
                    mqttDataTemp.append(mqttData['data'])
                    mqttData_SAVEFull.append(mqttDataTemp)

                    temp_current_occupants = []
                    
                    if ndns_fns.sd.track.num_tracks > 0:
                        for idx, track in enumerate(ndns_fns.sd.track.tid):
                            temp_current_occupants.append(track)
                            ndns_fns.oh.update(mqttData['addr'],track,ndns_fns.sd.track.X[idx],ndns_fns.sd.track.Y[idx],ndns_fns.sd)
                            # except Exception as e:
                            #     nodens.logger.warning(f"SERV update. {e}. sensor_id: {mqttData['addr']}. num_tracks: {ndns_fns.sd.track.num_tracks}. tid: {ndns_fns.sd.track.tid}.",
                            #                           f"idx: {idx}. track: {track}. X: {ndns_fns.sd.track.X}. Y: {ndns_fns.sd.track.Y}. ids: {ndns_fns.oh.id}",
                            #                           f"ind_s: {ndns_fns.oh.sensor_id.index(mqttData['addr'])}. ind_t: {ndns_fns.oh.id[ndns_fns.oh.sensor_id.index(mqttData['addr'])].index(track)}")
                                
                        try:
                            ndns_fns.oh.sensor_activity(mqttData['addr'])
                        except Exception as e:
                                nodens.logger.warning(f"SERV sensor_activity. {e}. sensor_id: {mqttData['addr']}.")   
                    else: # TRYING THIS KZR
                        ndns_fns.oh.update(mqttData['addr'],[],[],[],ndns_fns.sd)
                    

                    # Update time period occupancy data
                    if mqttData['addr'] not in ndns_fns.ew.id:
                        ndns_fns.ew.update(mqttData['addr'])
                    send_idx_e = ndns_fns.ew.id.index(mqttData['addr'])

                    ndns_fns.si.update_refresh(sen_idx, send_idx_e, T, ndns_fns.ew)


                    #TODO: check cloud update
                    if ((T - ndns_fns.si.period_t[sen_idx]).total_seconds() > nodens.cp.CLOUD_WRITE_TIME):
                        # Mark for deletion tracks which have left
                        ndns_fns.oh.delete_track(mqttData['addr'], temp_current_occupants, mark_to_delete=1)

                        # Calculate occupant history outputs
                        ind_s = ndns_fns.oh.calculate_outputs(mqttData['addr'])

                        # diag_info = (f"SERV Cloud Full. sensor: {mqttData['addr']}.",
                        #                 f"Counts (heartbeat,full,basic): {ndns_fns.counts.print_counts(mqttData['addr'])}", 
                        #                 f"N frames: {ndns_fns.si.period_N[sen_idx]}. Avg rate: {nodens.cp.CLOUD_WRITE_TIME/ndns_fns.si.period_N[sen_idx]:.2f}")
                        # nodens.logger.info(diag_info)
                        ndns_fns.counts.initialise(mqttData['addr'])
                        
                        mqttTime = json.loads("{\"Time\": \"" + str(T) + "\"}")
                        # mqttClass = json.loads("{\"Activity detected\": \"" + str(int(ndns_fns.class_eng.activity_alert))
                        #                     + "\", \"Activity type\": \"" + str(int(ndns_fns.class_eng.classification))
                        #                     + "\"}")
                        mqttDataFinal = {**mqttTime, **mqttData, **mqttDataFinal, 
                                        'Sensor timestamp' : T,
                                        'Average period occupancy' : ndns_fns.si.period_sum_occ[sen_idx]/ndns_fns.si.period_N[sen_idx], 
                                        'Maximum period occupancy' : ndns_fns.si.period_max_occ[sen_idx],
                                        'Average entryway occupancy' : ndns_fns.si.ew_period_sum_occ[sen_idx]/ndns_fns.si.period_N[sen_idx], 
                                        'Maximum entryway occupancy' : ndns_fns.si.ew_period_max_occ[sen_idx],
                                        'Full data flag' : 0}
                        try:
                            mqttDataFinal = {**mqttDataFinal,
                                        'Track id' : ndns_fns.oh.outputs[ind_s].track_id,
                                        'X' : ndns_fns.oh.outputs[ind_s].track_X,
                                        'Y' : ndns_fns.oh.outputs[ind_s].track_Y
                            }
                        except Exception as e:
                            nodens.logger.error(f"SERV mqttDataFinal INITIAL {e}. sensor: {mqttData['addr']}. ind_s: {ind_s} sen_idx: {sen_idx}. len oh: {len(ndns_fns.oh.outputs)}.")
                        try:
                            mqttDataFinal = {**mqttDataFinal,
                                        'Distance moved' : ndns_fns.oh.outputs[ind_s].distance_moved,
                                        'Was active' : ndns_fns.oh.outputs[ind_s].was_active,
                                        'Presence detected' : ndns_fns.sd.presence.present
                                        }
                        except Exception as e:
                            nodens.logger.error(f"SERV mqttDataFinal SUPP {e}. sensor: {mqttData['addr']}. ind_s: {ind_s} sen_idx: {sen_idx}. len oh: {len(ndns_fns.oh.outputs)}.")
                            
                        try:
                            mqttDataFinal = {**mqttDataFinal,
                                        'UD energy' : ndns_fns.oh.outputs[ind_s].ud_energy,
                                        'PC energy' : ndns_fns.oh.outputs[ind_s].pc_energy
                                        }
                        except Exception as e:
                            nodens.logger.error(f"SERV mqttDataFinal ENERGY {e}. sensor: {mqttData['addr']}. ind_s: {ind_s} sen_idx: {sen_idx}. len oh: {len(ndns_fns.oh.outputs)}.")
                            
                        try:
                            mqttDataFinal = {**mqttDataFinal,
                                        'Occupancy heatmap' : ndns_fns.oh.outputs[ind_s].heatmap_string,
                                        'Gait distribution' : ndns_fns.oh.outputs[ind_s].gait_string
                                        }
                        except Exception as e:
                            nodens.logger.error(f"SERV mqttDataFinal NEW {e}. sensor: {mqttData['addr']}. ind_s: {ind_s} sen_idx: {sen_idx}. len oh: {len(ndns_fns.oh.outputs)}.")
                        
                        ndns_fns.class_eng.activity_alert = 0
                        try:
                            send_idx_o = ndns_fns.oh.sens_idx.index(mqttData['addr'])
                            mqttDataFinal = {**mqttDataFinal, 
                                        'Most inactive track' : ndns_fns.oh.most_inactive_track[send_idx_o],
                                        'Most inactive time' : str(ndns_fns.oh.most_inactive_time[send_idx_o]),
                                        'Distance walked' : ndns_fns.oh.tot_dist[send_idx_o],
                                        'Distance walked' : ndns_fns.oh.tot_dist[send_idx_o],
                                        }
                        except:
                            send_idx_o = None
                            mqttDataFinal = {**mqttDataFinal, 
                                        'Most inactive track' : "-",
                                        'Most inactive time' : "-",
                                        }
                        
                        # Log some occupancy statistics
                        print_text = ('Occupancy at timestamp: {} \n'.format(T) +
                                    '\t Current : {}\n'.format(ndns_fns.si.num_occ) +
                                    '\t Average.\tDirect: {},\tEntryway: {}\n'.format(mqttDataFinal['Average period occupancy'], mqttDataFinal['Average entryway occupancy']) +
                                    '\t Max.\t\tDirect: {},\tEntryway: {}\n'.format(mqttDataFinal['Maximum period occupancy'], mqttDataFinal['Maximum entryway occupancy']))

                        # Record message to send, if requested by ud service
                        ndns_fns.message_pipeline.update(mqttDataFinal)

                        # if nodens.cp.ENABLE_THINGSBOARD:
                        #     ndns_tb.TB.prepare_data(mqttDataFinal)
                        #     ndns_tb.TB.multiline_payload(mqttData['addr'])


                        ndns_fns.si.cloud_send_refresh(sen_idx, send_idx_e, T, ndns_fns.ew)
                        heartbeat = ""

                        # Refresh occupancy histories for next Cloud transmission frame
                        ndns_fns.oh.refresh(mqttData['addr'])

                elif (mqttData['type'] == 'json'):
                    nodens.logger.debug("JSON type: {}".format(mqttData))
                    ndns_fns.sm.update_config(mqttData)

                    # If sensor config has been received and is complete, then update database
                    s_idx = [idx for idx,val in enumerate(ndns_fns.sm.sensorStart_flag) if val == 1]
                    if len(s_idx) > 0:
                        nodens.logger.warning(f"Update database. ndns_fns.sm.sensorStart_flag: {ndns_fns.sm.sensorStart_flag}. s_idx: {s_idx}")
                    for idx in s_idx:
                        # Record message to send, if requested by Cloud service
                        ndns_fns.message_pipeline.config_update(ndns_fns.sm.sensor_id[idx], ndns_fns.sm.sensor_config[idx])
                        ndns_fns.sm.sensorStart_flag[idx] = 0

                # Process for new sensor version
                elif mqttData['type'] == 'v4':
                    print(f"V4")
                    ndns_fns.counts.update(mqttData['addr'], 'basic')

                    ndns_fns.sm.update(mqttData)
                    # mqttOcc = json.loads(data)
                    # mqttTime = json.loads("{\"Time\": \"" + str(T) + "\"}")
                    # mqttDataFinal = {**mqttTime, **mqttData, **mqttOcc}
                    ndns_fns.si.update_short(sen_idx, T, mqttData)
                    
                    # Temp variables
                    temp_dist_moved = ''
                    temp_gait_distr = ''
                    temp_pc_energy = ''
                    temp_current_occupants = []

                    ndns_fns.oh.update(mqttData['addr'],[],[],[],ndns_fns.sd)

                    # Update time period occupancy data
                    if mqttData['addr'] not in ndns_fns.ew.id:
                        ndns_fns.ew.update(mqttData['addr'])
                    send_idx_e = ndns_fns.ew.id.index(mqttData['addr'])
                    

                    if ('numOccupants' in mqttData):
                        mqttDataTemp = [T.strftime("%Y-%m-%dZ%H:%M:%S")]
                        mqttDataTemp.append(mqttData['addr'])
                        #ndns_fns.si.num_occ[sen_idx] = mqttDataFinal['Number of Occupants']
                        mqttDataTemp.append(mqttData['numOccupants'])

                        if ('occupancyInfo' in mqttData):
                            mqttOccInfo = mqttData['occupancyInfo']

                            for i in range(len(mqttData['occupancyInfo'])):
                                if 'trackID' in mqttData['occupancyInfo'][i]:
                                    temp_current_occupants.append(int(mqttData['occupancyInfo'][i]['trackID']))
                                if 'distance' in mqttData['occupancyInfo'][i]:
                                    if i == 0:
                                        temp_dist_moved = str(mqttData['occupancyInfo'][i]['distance'])
                                    else:
                                        temp_dist_moved = temp_dist_moved + ';' + str(mqttData['occupancyInfo'][i]['distance'])
                                if 'gaitDistr' in mqttData['occupancyInfo'][i]:
                                    if i == 0:
                                        temp_gait_distr = str(mqttData['occupancyInfo'][i]['gaitDistr'])
                                    else:
                                        temp_gait_distr = temp_gait_distr + ';' + str(mqttData['occupancyInfo'][i]['gaitDistr'])
                                if 'pcEnergy' in mqttData['occupancyInfo'][i]:
                                    if i == 0:
                                        temp_pc_energy = str(mqttData['occupancyInfo'][i]['pcEnergy'])
                                    else:
                                        temp_pc_energy = temp_pc_energy + ';' + str(mqttData['occupancyInfo'][i]['pcEnergy'])
                    print(f"here")        

                    ## ~~~~~~~~~~~ SEND TO CLOUD ~~~~~~~~~ ##
                    if ((T - ndns_fns.si.period_t[sen_idx]).total_seconds() > nodens.cp.CLOUD_WRITE_TIME):
                        # Mark for deletion tracks which have left
                        print(f"here2. {mqttData['addr']} {temp_current_occupants} {ndns_fns.oh.sensor_id}")
                        ndns_fns.oh.delete_track(mqttData['addr'], temp_current_occupants, mark_to_delete=1)

                        # Calculate occupant history outputs
                        ind_s = ndns_fns.oh.calculate_outputs(mqttData['addr'])

                        # diag_info = (f"SERV Cloud. sensor: {mqttData['addr']}.",
                        #              f"Counts (heartbeat,full,basic): {ndns_fns.counts.print_counts(mqttData['addr'])}", 
                        #              f"N frames: {ndns_fns.si.period_N[sen_idx]}. Avg rate: {nodens.cp.CLOUD_WRITE_TIME/ndns_fns.si.period_N[sen_idx]:.2f}")
                        # nodens.logger.info(diag_info)
                        ndns_fns.counts.initialise(mqttData['addr'])
                        print(f"here3")

                        
                        mqttTime = json.loads("{\"Time\": \"" + str(T) + "\"}")
                        # mqttClass = json.loads("{\"Activity detected\": \"" + str(int(ndns_fns.class_eng.activity_alert))
                        #                     + "\", \"Activity type\": \"" + str(int(ndns_fns.class_eng.classification))
                        #                     + "\"}")
                        mqttDataFinal = {#**mqttData, 
                                        'addr' : mqttData['addr'],
                                        'type' : mqttData['type'],
                                        'Sensor timestamp' : mqttData['timestamp'],
                                        'Average period occupancy' : mqttData['numOccupants'], 
                                        'Maximum period occupancy' : '',
                                        'Average entryway occupancy' : '', 
                                        'Maximum entryway occupancy' : '',
                                        'Full data flag' : 0}
                        try:
                            mqttDataFinal = {**mqttDataFinal,
                                        'Track id' : mqttData['occupancyInfo'][0]['trackID'],
                                        'X' : mqttData['occupancyInfo'][0]['X'],
                                        'Y' : mqttData['occupancyInfo'][0]['Y']
                            }
                        except Exception as e:
                            nodens.logger.error(f"SERV mqttDataFinal INITIAL {e}. sensor: {mqttData['addr']}. ind_s: {ind_s} sen_idx: {sen_idx}. len oh: {len(ndns_fns.oh.outputs)}.")
                            mqttDataFinal = {**mqttDataFinal,
                                        'Track id' : '',
                                        'X' : '',
                                        'Y' : ''
                            }
                        try:
                            mqttDataFinal = {**mqttDataFinal,
                                        'Distance moved' : temp_dist_moved,
                                        'Was active' : ndns_fns.oh.outputs[ind_s].was_active,
                                        'Presence detected' : ndns_fns.sd.presence.present
                                        }
                        except Exception as e:
                            nodens.logger.error(f"SERV mqttDataFinal SUPP {e}. sensor: {mqttData['addr']}. ind_s: {ind_s} sen_idx: {sen_idx}. len oh: {len(ndns_fns.oh.outputs)}.")
                            
                        try:
                            mqttDataFinal = {**mqttDataFinal,
                                        'UD energy' : 0,
                                        'PC energy' : temp_pc_energy
                                        }
                        except Exception as e:
                            nodens.logger.error(f"SERV mqttDataFinal ENERGY {e}. sensor: {mqttData['addr']}. ind_s: {ind_s} sen_idx: {sen_idx}. len oh: {len(ndns_fns.oh.outputs)}.")
                            
                        try:
                            mqttDataFinal = {**mqttDataFinal,
                                        'Occupancy heatmap' : mqttData['heatmap'],
                                        'Gait distribution' : temp_gait_distr
                                        }
                        except Exception as e:
                            nodens.logger.error(f"SERV mqttDataFinal NEW {e}. sensor: {mqttData['addr']}. ind_s: {ind_s} sen_idx: {sen_idx}. len oh: {len(ndns_fns.oh.outputs)}.")
                        
                        ndns_fns.class_eng.activity_alert = 0
                        try:
                            send_idx_o = ndns_fns.oh.sens_idx.index(mqttData['addr'])
                            mqttDataFinal = {**mqttDataFinal, 
                                        'Most inactive track' : ndns_fns.oh.most_inactive_track[send_idx_o],
                                        'Most inactive time' : str(ndns_fns.oh.most_inactive_time[send_idx_o]),
                                        }
                        except:
                            send_idx_o = None
                            mqttDataFinal = {**mqttDataFinal, 
                                        'Most inactive track' : "-",
                                        'Most inactive time' : "-",
                                        }

                        # Log some occupancy statistics
                        try:
                            print_text = ('Occupancy at timestamp: {} \n'.format(T) +
                                        '\t Current : {}\n'.format(mqttData['numOccupants']) +
                                        '\t Average.\tDirect: {},\tEntryway: {}\n'.format(mqttDataFinal['Average period occupancy'], mqttDataFinal['Average entryway occupancy']) +
                                        '\t Max.\t\tDirect: {},\tEntryway: {}\n'.format(mqttDataFinal['Maximum period occupancy'], mqttDataFinal['Maximum entryway occupancy']))
                        except Exception as e:
                            print(f"Error in print_text: {e}")

                        # Record message to send, if requested by Cloud service
                        ndns_fns.message_pipeline.update(mqttDataFinal)
                        # if nodens.cp.ENABLE_THINGSBOARD:
                        #     ndns_tb.TB.prepare_data(mqttDataFinal)
                        #     ndns_tb.TB.multiline_payload(mqttData['addr'])


                        ndns_fns.si.cloud_send_refresh(sen_idx, send_idx_e, T, ndns_fns.ew)
                        heartbeat = ""
                        # Refresh occupancy histories for next Cloud transmission frame
                        ndns_fns.oh.refresh(mqttData['addr'])
                        print(f"here4")



                # Otherwise process occupancy info
                elif "type" not in json.loads(data):
                    ndns_fns.counts.update(mqttData['addr'], 'basic')
                    ndns_fns.sm.update(mqttData)
                    mqttOcc = json.loads(data)
                    mqttTime = json.loads("{\"Time\": \"" + str(T) + "\"}")
                    mqttDataFinal = {**mqttTime, **mqttData, **mqttOcc}
                    #ndns_fns.si.last_t[sen_idx] = T
                    #mqttData_SAVE.append(mqttOcc)

                    ndns_fns.si.update_short(sen_idx, T, mqttDataFinal)
                    
                    if ('Number of Occupants' in mqttDataFinal):
                        mqttDataTemp = [T.strftime("%Y-%m-%dZ%H:%M:%S")]
                        mqttDataTemp.append(mqttData['addr'])
                        #ndns_fns.si.num_occ[sen_idx] = mqttDataFinal['Number of Occupants']
                        mqttDataTemp.append(mqttDataFinal['Number of Occupants'])

                        if ('Occupancy Info' in mqttDataFinal):
                            mqttOccInfo = mqttDataFinal['Occupancy Info']
                            for i in range(min(ndns_fns.si.num_occ[sen_idx],2)):
                                mqttDataTemp.append(mqttOccInfo[i]['Occupant ID'])
                                mqttDataTemp.append(mqttOccInfo[i]['X'])
                                mqttDataTemp.append(mqttOccInfo[i]['Y'])
                                mqttDataTemp.append(mqttOccInfo[i]['Z'])
                            while 1:
                                if i < 1:
                                    for j in range(4):
                                        mqttDataTemp.append('')
                                    i += 1
                                else:
                                    break
                            try:
                                if 'Heatmap energy' in mqttOccInfo[-1]:
                                    mqttDataTemp.append(mqttOccInfo[-1]['Heatmap energy'])
                                    mqttDataTemp.append(mqttOccInfo[-1]['Heatmap'])
                                else:
                                    mqttDataTemp.append(0)
                                    mqttDataTemp.append('')
                            except Exception as e:
                                nodens.logger.warning(f"Heatmap {e}")
                        else:
                            for i in range(8):
                                mqttDataTemp.append('')
                            mqttDataTemp.append(0)
                            mqttDataTemp.append('')

                        mqttData_SAVE.append(mqttDataTemp)
                        

                        # # Update max number of occupants
                        # if (ndns_fns.si.num_occ[sen_idx] > ndns_fns.si.max_occ[sen_idx]):
                        #     ndns_fns.si.max_occ[sen_idx] = ndns_fns.si.num_occ[sen_idx]

                        # If there are occupants, what are their locations?
                        temp_current_occupants = []
                        if (ndns_fns.si.num_occ[sen_idx] > 0):        # NodeNs KZR FIX : need to update so oh processes when num_occ=0
                            try:
                                occ_info = mqttDataFinal['Occupancy Info']
                            except:
                                occ_info = mqttDataFinal['Occupancy Info'][0]
                            # nodens.logger.debug('OCCUPANCY INFO')

                            # Update occupancy history and entryways for each occupant
                            for i in range(len(occ_info)):      # NodeNs KZR FIX: update ESP to create new payload
                                temp = occ_info[i]
                                temp_current_occupants.append(int(temp['Occupant ID']))
                                ndns_fns.oh.update(mqttData['addr'],int(temp['Occupant ID']),temp['X'],temp['Y'])
                                # Check if occupant has crossed entryway
                                ndns_fns.oh.entryway(mqttData['addr'],int(temp['Occupant ID']), ndns_fns.ew)
                                # nodens.logger.debug('Occupant no.: {}. X: {}. Y = {}.'.format(temp['Occupant ID'],temp['X'],temp['Y']))

                            # Look at general activity stats
                            ndns_fns.oh.sensor_activity(mqttData['addr'])
                        else:
                            ndns_fns.oh.update(mqttData['addr'])
                            ndns_fns.oh.sensor_activity(mqttData['addr'])


                        # Update time period occupancy data
                        if mqttData['addr'] not in ndns_fns.ew.id:
                            ndns_fns.ew.update(mqttData['addr'])
                        send_idx_e = ndns_fns.ew.id.index(mqttData['addr'])

                        ndns_fns.si.update_refresh(sen_idx, send_idx_e, T, ndns_fns.ew)

                        ## ~~~~~~~~~~~ ALERT: ACTIVITY DETECTED ~~~~~~~~~ ##
                        # if nodens.cp.ENABLE_SIEMENS_IH and ndns_fns.class_eng.activity_alert == 1:
                        #     print("ACTIVITY: Writing to cloud...T:{}".format(T))
                        #     mqttTime = json.loads("{\"Time\": \"" + str(T) + "\"}")
                        #     mqttClass = json.loads("{\"Activity detected\": \"" + str(int(ndns_fns.class_eng.activity_alert))
                        #                         + "\", \"Activity type\": \"" + str(int(ndns_fns.class_eng.classification))
                        #                         + "\"}")
                        #     mqttOccInfo = "" 
                        #     for i in range(sd.track.num_tracks):
                        #         mqttOccInfo += ( "{\"Occupant ID\":" + str(sd.track.tid[i]) +
                        #                         ",\"X\":" + str(sd.track.X[i]) + 
                        #                         ",\"Y\":" + str(sd.track.Y[i]) +
                        #                         ",\"Z\":" + str(sd.track.Z[i]) +
                        #                         "},") 
                        #     mqttOcc = json.loads("{\"Number of Occupants\": \"" + str(int(sd.track.num_tracks))
                        #                         + "\", \"Occupancy Info\": [" +
                        #                         "{}".format(mqttOccInfo[:-1]) + "]"
                        #                         + "}")
                        #     mqttDataFinal = {**mqttTime, **mqttData, **mqttClass, **mqttOcc}
                        #     ndns_fns.class_eng.activity_alert = 0
                        #     send_mc.send_mindconnect_payload(mqtt_data=mqttDataFinal, sensor_data=sd)

                        ## ~~~~~~~~~~~ SEND TO CLOUD ~~~~~~~~~ ##
                        if ((T - ndns_fns.si.period_t[sen_idx]).total_seconds() > nodens.cp.CLOUD_WRITE_TIME):
                            # Mark for deletion tracks which have left
                            ndns_fns.oh.delete_track(mqttData['addr'], temp_current_occupants, mark_to_delete=1)

                            # Calculate occupant history outputs
                            ind_s = ndns_fns.oh.calculate_outputs(mqttData['addr'])

                            # diag_info = (f"SERV Cloud. sensor: {mqttData['addr']}.",
                            #              f"Counts (heartbeat,full,basic): {ndns_fns.counts.print_counts(mqttData['addr'])}", 
                            #              f"N frames: {ndns_fns.si.period_N[sen_idx]}. Avg rate: {nodens.cp.CLOUD_WRITE_TIME/ndns_fns.si.period_N[sen_idx]:.2f}")
                            # nodens.logger.info(diag_info)
                            ndns_fns.counts.initialise(mqttData['addr'])

                            
                            mqttTime = json.loads("{\"Time\": \"" + str(T) + "\"}")
                            # mqttClass = json.loads("{\"Activity detected\": \"" + str(int(ndns_fns.class_eng.activity_alert))
                            #                     + "\", \"Activity type\": \"" + str(int(ndns_fns.class_eng.classification))
                            #                     + "\"}")
                            mqttDataFinal = {**mqttTime, **mqttData, **mqttDataFinal, 
                                            'Sensor timestamp' : T,
                                            'Average period occupancy' : ndns_fns.si.period_sum_occ[sen_idx]/ndns_fns.si.period_N[sen_idx], 
                                            'Maximum period occupancy' : ndns_fns.si.period_max_occ[sen_idx],
                                            'Average entryway occupancy' : ndns_fns.si.ew_period_sum_occ[sen_idx]/ndns_fns.si.period_N[sen_idx], 
                                            'Maximum entryway occupancy' : ndns_fns.si.ew_period_max_occ[sen_idx],
                                            'Full data flag' : 0}
                            try:
                                mqttDataFinal = {**mqttDataFinal,
                                            'Track id' : ndns_fns.oh.outputs[ind_s].track_id,
                                            'X' : ndns_fns.oh.outputs[ind_s].track_X,
                                            'Y' : ndns_fns.oh.outputs[ind_s].track_Y
                                }
                            except Exception as e:
                                nodens.logger.error(f"SERV mqttDataFinal INITIAL {e}. sensor: {mqttData['addr']}. ind_s: {ind_s} sen_idx: {sen_idx}. len oh: {len(ndns_fns.oh.outputs)}.")
                            try:
                                mqttDataFinal = {**mqttDataFinal,
                                            'Distance moved' : ndns_fns.oh.outputs[ind_s].distance_moved,
                                            'Was active' : ndns_fns.oh.outputs[ind_s].was_active,
                                            'Presence detected' : ndns_fns.sd.presence.present
                                            }
                            except Exception as e:
                                nodens.logger.error(f"SERV mqttDataFinal SUPP {e}. sensor: {mqttData['addr']}. ind_s: {ind_s} sen_idx: {sen_idx}. len oh: {len(ndns_fns.oh.outputs)}.")
                                
                            try:
                                mqttDataFinal = {**mqttDataFinal,
                                            'UD energy' : ndns_fns.oh.outputs[ind_s].ud_energy,
                                            'PC energy' : ndns_fns.oh.outputs[ind_s].pc_energy
                                            }
                            except Exception as e:
                                nodens.logger.error(f"SERV mqttDataFinal ENERGY {e}. sensor: {mqttData['addr']}. ind_s: {ind_s} sen_idx: {sen_idx}. len oh: {len(ndns_fns.oh.outputs)}.")
                                
                            try:
                                mqttDataFinal = {**mqttDataFinal,
                                            'Occupancy heatmap' : ndns_fns.oh.outputs[ind_s].heatmap_string,
                                            'Gait distribution' : ndns_fns.oh.outputs[ind_s].gait_string
                                            }
                            except Exception as e:
                                nodens.logger.error(f"SERV mqttDataFinal NEW {e}. sensor: {mqttData['addr']}. ind_s: {ind_s} sen_idx: {sen_idx}. len oh: {len(ndns_fns.oh.outputs)}.")
                            
                            ndns_fns.class_eng.activity_alert = 0
                            try:
                                send_idx_o = ndns_fns.oh.sens_idx.index(mqttData['addr'])
                                mqttDataFinal = {**mqttDataFinal, 
                                            'Most inactive track' : ndns_fns.oh.most_inactive_track[send_idx_o],
                                            'Most inactive time' : str(ndns_fns.oh.most_inactive_time[send_idx_o]),
                                            }
                            except:
                                send_idx_o = None
                                mqttDataFinal = {**mqttDataFinal, 
                                            'Most inactive track' : "-",
                                            'Most inactive time' : "-",
                                            }

                            # Log some occupancy statistics
                            print_text = ('Occupancy at timestamp: {} \n'.format(T) +
                                        '\t Current : {}\n'.format(mqttDataFinal['Number of Occupants']) +
                                        '\t Average.\tDirect: {},\tEntryway: {}\n'.format(mqttDataFinal['Average period occupancy'], mqttDataFinal['Average entryway occupancy']) +
                                        '\t Max.\t\tDirect: {},\tEntryway: {}\n'.format(mqttDataFinal['Maximum period occupancy'], mqttDataFinal['Maximum entryway occupancy']))

                            # Record message to send, if requested by Cloud service
                            ndns_fns.message_pipeline.update(mqttDataFinal)

                            # if nodens.cp.ENABLE_THINGSBOARD:
                            #     ndns_tb.TB.prepare_data(mqttDataFinal)
                            #     ndns_tb.TB.multiline_payload(mqttData['addr'])


                            ndns_fns.si.cloud_send_refresh(sen_idx, send_idx_e, T, ndns_fns.ew)
                            heartbeat = ""

                            # Refresh occupancy histories for next Cloud transmission frame
                            ndns_fns.oh.refresh(mqttData['addr'])
                        
                    else:
                        #ndns_fns.si.num_occ[sen_idx] = 0
                        pass
            
                    if mqttDataFinal['type'] == 'bytes':
                        ndns_fns.si.last_t[sen_idx] = T
                        heartbeat += "+"
                        heartbeat = "\r" + heartbeat
                        # nodens.logger.info(heartbeat, end='')
                        if 'Sensor Information' in mqttDataFinal:
                            temp_text = "Waiting for config"
                            if mqttDataFinal['Sensor Information'][:len(temp_text)] != temp_text:
                                nodens.logger.debug("Sensor information: {} for Device: {}". format(mqttDataFinal['Sensor Information'], mqttDataFinal['addr']))

                            # Check for sensor version
                            temp = mqttDataFinal['Sensor Information']
                            
                            if temp[:7] == 'VERSION':
                                nodens.logger.info(f"Version received: {temp[9:]}")
                                ndns_fns.sv.parse(temp[9:])
                                ndns_fns.sm.update_config(temp, mqttDataFinal['addr'])
                                

                            elif temp[0:6] == 'CONFIG':
                                ndns_fns.rcp.receive_config(temp[8:])
                                ndns_fns.sm.update_config(temp, mqttDataFinal['addr'])
                                sens_idx = ndns_fns.sm.sensor_id.index(mqttDataFinal['addr'])
                                if ndns_fns.sm.sensorStart_flag[sens_idx] == 1:
                                    ndns_fns.message_pipeline.config_check(mqttDataFinal['addr'])
                                    ndns_fns.sm.sensorStart_flag[sens_idx] = 0

                            elif temp[0:3] == 'MSG':
                                ndns_mesh.MESH.status.receive_msg(temp, mqttDataFinal['timestamp'])
                                ndns_mesh.MESH.status.receive_info(temp, mqttDataFinal['timestamp'], mqttDataFinal['addr'])
                                if ndns_mesh.MESH.status.last_msg.find("NEW CONFIG!") >= 0:
                                    msg = ndns_mesh.MESH.status.last_msg
                                    i0 = msg.find("X=")
                                    i1 = msg[i0:].find(",")
                                    i2 = msg[i0:].find(")")

                                    ndns_fns.rcp.ROOM_X_MIN = (msg[i0+3:i0+i1])
                                    ndns_fns.rcp.ROOM_X_MAX = (msg[i0+i1+1:i0+i2])

                                    i0 = (msg.find("Y="))
                                    i1 = (msg[i0:].find(","))
                                    i2 = msg[i0:].find(")")

                                    ndns_fns.rcp.ROOM_Y_MIN = (msg[i0+3:i0+i1])
                                    ndns_fns.rcp.ROOM_Y_MAX = (msg[i0+i1+1:i0+i2])

                            else:
                                ndns_mesh.MESH.status.receive_info(temp, mqttDataFinal['timestamp'], mqttDataFinal['addr'])
                    
                    elif mqttDataFinal['type'] == 'heartbeat':
                        heartbeat += "."
                        heartbeat = "\r" + heartbeat
                        #print(heartbeat, end='')
                    else:
                        nodens.logger.warning("Another type: {}".format(mqttDataFinal))
                
                else:
                    if json.loads(data)["type"] == 'heartbeat':
                        ndns_fns.counts.update(mqttData['addr'], 'heartbeat')
                        ndns_fns.sm.update(mqttData)
                        # nodens.logger.warning(f"heartbeat")
                        heartbeat += "."
                        heartbeat = "\r" + heartbeat
                    else:
                        nodens.logger.info(f"Unrecognised type: {json.loads(mqttData)['type']}. data: {mqttData}")
            except Exception as e:
                nodens.logger.error(f"TYPE. \n\tmsg: {e.args}. \n\tdata: {data}")

            ##~~~~~~~~ Print info to screen process ~~~~~~~##

            if ((T-T0).total_seconds()  > nodens.cp.PRINT_FREQ):
                T0 = dt.datetime.now(dt.timezone.utc)
                #print(heartbeat)
                heartbeat = ""
                try:
                    print_diagnostics = (f"\n***************")
                    for i,sensor_id in enumerate(ndns_fns.si.connected_sensors):
                        temp_min = nodens.cp.PRINT_FREQ/(ndns_fns.counts.print_counts(sensor_id)[1][1] + ndns_fns.counts.print_counts(sensor_id)[1][2])
                        temp_max = nodens.cp.PRINT_FREQ/(ndns_fns.counts.print_counts(sensor_id)[2][1] + ndns_fns.counts.print_counts(sensor_id)[2][2])
                        print_diagnostics += (f"\n{sensor_id} @  {ndns_fns.si.last_t[i]} - "
                                              f"\n\tFrame times. Min: {temp_min}. Max: {temp_max}."
                                              f"\n\tMax counts (heartbeat,full,basic): {ndns_fns.counts.print_counts(sensor_id)[1]}"
                                              f"\n\tMin counts (heartbeat,full,basic): {ndns_fns.counts.print_counts(sensor_id)[2]}"
                                              f"\n***************")
                    nodens.logger.info(print_diagnostics)
                except Exception as e:
                    nodens.logger.info(f"Step 2 didn't work: {e.args}")
                ndns_fns.counts.reset(mqttData['addr'])
                
                

            # if (T - T0).total_seconds() > 60:
            #     nodens.logger.debug("1 minute check. T: {}. T0: {}. T-T0: {}. idx_mqtt: {}. PRINT_FREQ: {}. connect_status: {}"
            #             .format(T, T0, (T - T0).total_seconds(), idx_mqtt, nodens.cp.PRINT_FREQ, ndns_mesh.MESH.client.connect_status))
            #     if ndns_mesh.MESH.client.connect_status == 0:
            #         ndns_mesh.MESH.end()
            
            # Save data
            if (idx_write > 5 and nodens.cp.WRITE_FLAG == 1):

                if len(mqttData_SAVE) > 0:
                    with open(file_save + ".csv", "a") as filehandle:
                        writer = csv.writer(filehandle)


                        # write the data
                        writer.writerows(mqttData_SAVE)

                    filehandle.close()

                if len(mqttData_SAVEFull) > 0:
                    with open(file_save + "_FULL.csv", "a") as filehandle:
                        writer = csv.writer(filehandle)

                        # write the header
                        #writer.writerow(header)

                        # write the data
                        writer.writerows(mqttData_SAVEFull)

                    filehandle.close()


                # Reset write count
                idx_write = 0
                mqttData_SAVE = []
                mqttData_SAVEFull = []

        # Check config if necessary
        if mqttData['addr'] in ndns_fns.sm.sensor_id:
            sens_idx = ndns_fns.sm.sensor_id.index(mqttData['addr'])
            if ndns_fns.sm.last_config_check_time[sens_idx] != []:
                if (T - ndns_fns.sm.last_config_check_time[sens_idx]).seconds > 15*60:
                    if mqttData['addr'] in ndns_fns.si.connected_sensors:
                        sen_idx_s = ndns_fns.si.connected_sensors.index(mqttData['addr'])
                        if (ndns_fns.si.num_occ[sen_idx_s] == 0):
                            ndns_fns.message_pipeline.config_check(mqttData['addr'])
                            ndns_fns.sm.last_config_check_time[sens_idx] = T

        # except:
        #     pass


