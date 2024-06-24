#  Copyright (c) 2024.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Arial"

XLSX_FILE = r"../data/snr.xlsx"

data = pd.read_excel(XLSX_FILE, sheet_name="thread_latency_certain_interval")

print(data["latency1"])
print(data["latency2"])
print(data["latency3"])
print(data["latency4"])

max_time_range = 40

INTERVAL_SECOND_LIST = [None, 0.064, 0.032, 0.016, 0.008]
LINESTYLE_LIST = [None, "solid", "dashed", "dashdot", "dotted"]

for i in range(1, 5):
    N = np.arange(0, max_time_range * (2**i))
    plt.plot(N * INTERVAL_SECOND_LIST[i], data["latency%d" % (i)][N], label="%.3f s" % INTERVAL_SECOND_LIST[i], linestyle=LINESTYLE_LIST[i])
    # plt.plot(N * 0.064, data["latency1"][N], label="0.064s")
    # plt.plot(N * 0.032, data["latency2"][N], label="0.032s")
    # plt.plot(N * 0.016, data["latency3"][N], label="0.016s")
    # plt.plot(N * 0.008, data["latency4"][N], label="0.008s")

plt.xlabel("Time [s]")
plt.ylabel("Latency [s]")
plt.tight_layout()

plt.legend()
plt.show()
