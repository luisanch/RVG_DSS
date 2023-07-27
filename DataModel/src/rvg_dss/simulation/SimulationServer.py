import numpy as np 
from scipy.signal import butter, filtfilt
import json
from rvg_dss.simulation.SimulationTransform import SimulationTransform
from rvg_dss.serializers.FastSerializer import FastSerializer 
from rvg_dss.data_relay.DashboardWebsocket import DashboardWebsocket
from rvg_dss.colav.ColavManager import ColavManager
import math

class SimulationServer:
    def __init__(self, serializer = FastSerializer, websocket = DashboardWebsocket, 
                distance_filter=None, predicted_interval = 30 ,
                colav_manager = ColavManager, filt_order = 3, filt_cutfreq = 0.1, 
                filt_nyqfreq = 0.5):
        
        self._serializer = serializer
        self._buffer = serializer.sorted_data
        self._running = False 
        self.transform = SimulationTransform()
        self.ais_history = dict()
        self.ais_history_len = 30
        self.distance_filter = distance_filter
        self.gunnerus_lat=None
        self.gunnerus_lon=None
        self.websocket = websocket
        self._colav_manager = colav_manager
        self._predicted_interval = predicted_interval 
        self._butter_b, self._butter_a = butter(filt_order, filt_cutfreq/filt_nyqfreq, btype='low')
        self.rvg_state = {}
        self.rvg_heading = None
    
    def clear_ais_history(self):
        self.ais_history.clear()

    def _has_data(self, msg):
        msg_keys = msg.keys() 
        has_data = ("lat" in msg_keys and "lon" in msg_keys)
        return has_data
    
    def _has_prop(self, msg, prop = ""):
        msg_keys = msg.keys() 
        has_data = (prop in msg_keys)
        return has_data
    
    def _is_moving(self, msg):
        msg_keys = msg.keys() 
        has_data = ("course" in msg_keys and "speed" in msg_keys)
        return has_data

    def stop(self):
        self._running = False
        print("Simulation Client stopped")

    def dist(self, p,q):
        return math.sqrt( (q[0] - p[0])**2 + (q[1] - p[1])**2 )

    def _validate_coords(self, msg, distance):
        if (self.gunnerus_lat is None or self.gunnerus_lon is None): 
            return True
        
        if (msg["message_id"].find("!AI") == 0): 
            if (self._has_data(msg)): 
                lat = float(msg["lat"])
                lon = float(msg["lon"])
                
                p = [lat,lon]
                q = [self.gunnerus_lat,self.gunnerus_lon]

                return self.dist(p,q) < distance
            
        return True 
    
    def _set_predicted_position(self, msg):
        if self._is_moving(msg) and msg["speed"] > 0:
            speed = self.transform.kn_to_mps(msg["speed"]) 
            x = math.sin(math.radians(msg["course"])) * speed * self._predicted_interval
            y = math.cos(math.radians(msg["course"])) * speed * self._predicted_interval
            lat_p, lon_p = self.transform.xyz_to_coords(x, y, float(msg["lat"]), float(msg["lon"]))
            msg["lat_p"] = lat_p
            msg["lon_p"] = lon_p

    def _lp_filter_data(self, data=[]):
        if (len(data) < 15): return None
        data = np.array(data)
        filtered_data = filtfilt(self._butter_b, self._butter_a, data)
        return filtered_data

    def _set_history(self,msg):
        if (msg["message_id"].find("!AI") == 0):

            if (self._has_data(msg)):
                message_id = msg["message_id"]
                lat = float(msg["lat"])
                lon = float(msg["lon"])
                has_course = self._has_prop(msg, "course")

                if has_course:
                    course = float(msg["course"]) 

                if(message_id in self.ais_history.keys()): 
                    self.ais_history[message_id]["lon_history"].append(lon)
                    filt_lon = self._lp_filter_data(self.ais_history[message_id]["lon_history"]) 
                    self.ais_history[message_id]["lat_history"].append(lat)
                    filt_lat = self._lp_filter_data(self.ais_history[message_id]["lat_history"]) 

                    if (filt_lon is not None and filt_lat is not None):
                            filtered_pos = np.array([filt_lon , filt_lat]).T.tolist()
                            self.ais_history[message_id]["pos_history"] = filtered_pos 
                    else : 
                            unfiltered_pos = np.array(
                                [self.ais_history[message_id]["lon_history"] ,
                                    self.ais_history[message_id]["lat_history"]]
                                    ).T.tolist()
                            self.ais_history[message_id]["pos_history"] = unfiltered_pos

                    if (has_course): 
                        self.ais_history[message_id]["course_history"].append(course) 
                        filtered_course = self._lp_filter_data(self.ais_history[message_id]["course_history"]) 
                        if (filtered_course is not None):
                            self.ais_history[message_id]["filtered_course"] = filtered_course[-1]
                        else : 
                            self.ais_history[message_id]["filtered_course"] = course

                    if(len(self.ais_history[message_id]["lon_history"]) > self.ais_history_len):
                        self.ais_history[message_id]["lon_history"].pop(0)
                    if(len(self.ais_history[message_id]["lat_history"]) > self.ais_history_len):
                        self.ais_history[message_id]["lat_history"].pop(0)

                    if(has_course and (len(self.ais_history[message_id]["course_history"]) > self.ais_history_len)):
                        self.ais_history[message_id]["course_history"].pop(0)
                else: 
                    self.ais_history[message_id] = dict()
                    self.ais_history[message_id]["lon_history"] = [lon]
                    self.ais_history[message_id]["lat_history"] = [lat]
                    self.ais_history[message_id]["pos_history"] = []

                    if (has_course): 
                        self.ais_history[message_id]["course_history"] = [course]
                        self.ais_history[message_id]["filtered_course"] = course

                msg["pos_history"] = self.ais_history[message_id]["pos_history"]
                if (has_course):
                    msg["course"] = self.ais_history[message_id]["filtered_course"]

    def _compose_msg(self, msg, msg_type = "datain"): 
        self._set_history(msg)
        self._set_predicted_position(msg)
        return(json.dumps({
            "type": msg_type,
            "content": msg
            },default=str))

    def _set_gunnerus_coords(self, msg): 
        self.gunnerus_lon = self.transform.deg_2_dec(float(msg["lon"]), msg["lon_dir"])
        self.gunnerus_lat = self.transform.deg_2_dec(float(msg["lat"]), msg["lat_dir"])

    def _send(self, message): 
        if self._validate_coords(message, self.distance_filter): 
            json_msg = self._compose_msg(message)

            if self.websocket.enable: 
                self.websocket.send(json_msg) 

            valid_ais_msg = (
                message["message_id"].find("!AI") == 0 and
                message["message_id"].find("_ext_") != -1 and
                self._has_data(message)
                )
            
            if valid_ais_msg:
                self._colav_manager.update_ais_data(message)

            if message["message_id"]=="$PSIMSNS_ext":
                self.rvg_heading = message['head_deg']
                
            if message["message_id"]=="$GPRMC_ext": 
                self._set_gunnerus_coords(message)
                self._colav_manager.update_gunnerus_data(message)
                self.rvg_state = message 
                pass
                
    def pop_buffer(self, index = None):
        if len(self._buffer) < 1: return

        if index is not None:
            return self._buffer.pop(index)
        else:
            return self._buffer.pop()
        
    def start(self):
        self._running = True 
        print("Simulation Client running...")

        while self._running:
            if len(self._buffer):
                self._send(self._buffer[0])
                self.pop_buffer(0)
