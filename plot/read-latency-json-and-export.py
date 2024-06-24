import os
import json
import numpy as np

DIR_FILE = "../websocket-latency"

json_key_list = ['connectivity', 'recordStartMicrosecond', 'recordMicrosecondList', 'totalLatencyList', 'clientToServerLatencyList', 'queueLatencyList', 'processLatencyList', 'serverToClientLatencyList', 'note', 'wsURL']

for filename in os.listdir(DIR_FILE):
    file_path = os.path.join(DIR_FILE, filename)
    with open(file_path) as file:
        latency_json = json.load(file)
        total_latency_list = np.array(latency_json["totalLatencyList"])
        client_to_server_latency_list = np.array(latency_json['clientToServerLatencyList'])
        queue_latency_list = np.array(latency_json['queueLatencyList'])
        process_latency_list = np.array(latency_json['processLatencyList'])
        server_to_client_latency_list = np.array(latency_json['serverToClientLatencyList'])
        connectivity = latency_json['connectivity']
        note = latency_json["note"]
        print(connectivity, note, np.average(total_latency_list),
              np.average(client_to_server_latency_list),
              np.average(queue_latency_list),
              np.average(process_latency_list),
              np.average(server_to_client_latency_list),
              sep="\t"
              )
