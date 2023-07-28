from rvg_leidarstein_core.serializers.Serializer import Serializer 
from rvg_leidarstein_core.datastream_managers.DatastreamManager import DatastreamManager

class FastSerializer(Serializer):
    def __init__(self, save_headers, df_aliases, datastream_manager = DatastreamManager,
                overwrite_headers=False, verbose=False):
        
        #attribute aliases for incoming messages
        self.df_aliases = df_aliases

        # define name for unknown atribute
        self.def_unk_atr_name = 'unknown_'
        self.bufferBusy = False
        self._datstream_manager = datastream_manager
        self.sorted_data = []
        self._running = False
        self._save_headers = save_headers[0]
        self._headers_path = save_headers[1]     
        self._buffer_data = datastream_manager.parsed_msg_list
        self._overwrite_headers = overwrite_headers
        self._log_verbose = verbose[0]
        self._buffer_verbose = verbose[1]
        self.metadata_atr_names = ('unix_time', 'seq_num', 'src_id', 'src_name') 

        if not self._overwrite_headers:
            self._load_headers()
    
    def _serialize_data(self, message):
            msg_id, msg_atr, msg_values, unkown_msg_data, metadata = message

            # ToDo: Probably very inefficient
            if len(unkown_msg_data) > 1: 
                msg_values.extend(unkown_msg_data)

                for i, _ in enumerate(unkown_msg_data):
                    atr_name = self.def_unk_atr_name + str(i)
                    msg_atr.append(atr_name)   

            # ToDo: awful, inefficient, do better check and skip redundancy
            if msg_id in self.df_aliases: 
                alias_list = self.df_aliases[msg_id] 
                if len(alias_list) == len(msg_atr):
                    for i , alias in enumerate(alias_list): 
                        msg_atr[i] = alias 

            # ToDo: Probably very inefficient x2
            if metadata is not None: 
                msg_values.extend(metadata)
                msg_atr.extend(self.metadata_atr_names) 

            message = dict(zip(msg_atr, msg_values))  
            message['message_id'] = msg_id  
            self.sorted_data.append(message) 
            return 

    def _serialize_buffered_message(self):
        if len(self._buffer_data) < 1: 
            self.bufferBusy = False
            if self._buffer_verbose:  print('Buffer Empty')
            return  
        
        self.bufferBusy = True
        _message = self._buffer_data[-1][1] 
        msg_id = self._buffer_data[-1][0] 

        if (msg_id.find('!AI') == 0):
            msg_atr, msg_values, unkown_msg_data, mmsi = self._get_ais_attributes(_message)
            msg_id = msg_id + '_' + str(mmsi) 
        else:
            msg_atr, msg_values, unkown_msg_data = self._get_nmea_attributes(_message) 
        
        if len(self._buffer_data[-1]) == 3:
            metadata = self._buffer_data[-1][2]
        else:
            metadata = None

        message = (msg_id, msg_atr, msg_values, unkown_msg_data, metadata)
        
        self._serialize_data(message)
        self._datstream_manager.pop_parsed_msg_list() 

    def start(self):
        self._running = True
        print('FastSerializer running.')

        while self._running: 
            self._serialize_buffered_message()  
        # ToDo: handle loose ends on terminating process. 
        print('FastSerializer stopped.')
