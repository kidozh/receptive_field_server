#  Copyright (c) 2024.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Arial"

XLSX_FILE = r"../data/snr.xlsx"

eb_data = pd.read_excel(XLSX_FILE, sheet_name="thread_latency_EB")

no_eb_data = pd.read_excel(XLSX_FILE, sheet_name="thread_latency_no_queue")

max_time_range = 300

N = np.arange(0, max_time_range)

thread_4_no_eb = no_eb_data["Latency4"]

thread_4_eb = eb_data["latency3"]


plt.plot(N*0.064, thread_4_eb[N], label="EB and PQ mechanism (%.3fs)" %(thread_4_eb.mean()), linestyle="-")
plt.plot(N*0.064, thread_4_no_eb[N], label="Direct (%.3fs)" %(thread_4_no_eb.mean()), linestyle="--")


plt.xlabel("Time [s]")
plt.ylabel("Latency [s]")

plt.tight_layout()

plt.legend()
plt.show()




