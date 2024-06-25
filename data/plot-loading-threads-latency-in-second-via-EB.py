#  Copyright (c) 2024.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Arial"

XLSX_FILE = r"../data/snr.xlsx"

data = pd.read_excel(XLSX_FILE, sheet_name="thread_loading_EB_test")

print(data)

print(data.keys())

max_time_range = 750

max_time_range = 550

INTERVAL_SECOND_LIST = [None, 0.064, 0.032, 0.016, 0.008]
LINESTYLE_LIST = [None, "solid", "dashed", "dashdot", "dotted", "dashed"]
LABEL_LIST = [None, "4 threads", "6 threads", "8 threads", "16 threads"]
N = np.arange(0, max_time_range)
arr = data["latency"][N]
timestamp = data["timestamp"][N]

timestamp = timestamp - timestamp[0]

plt.plot(timestamp, data["latency"][N], label="Latency")

for i in range(0, 16):
    plt.axvline(i*3, linestyle="dashed", color="grey", linewidth=1)
    plt.text(i*3, 1.0, "%d"%(i+1))

plt.xlabel("Time [s]")
plt.ylabel("Latency [s]")

plt.ylim(0, 1.2)
plt.tight_layout()

plt.legend()
plt.show()
