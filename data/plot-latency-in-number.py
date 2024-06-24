#  Copyright (c) 2024.
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Arial"

XLSX_FILE = r"../data/snr.xlsx"

data = pd.read_excel(XLSX_FILE, sheet_name="thread_latency_certain_interval")

print(data["latency1"])
print(data["latency2"])
print(data["latency3"])
print(data["latency4"])

max_time_range = 300

N = [i for i in range(0, max_time_range)]

plt.plot(N, data["latency1"][N], label="0.064s")
plt.plot(N, data["latency2"][N], label="0.032s")
plt.plot(N, data["latency3"][N], label="0.016s")
plt.plot(N, data["latency4"][N], label="0.008s")

plt.xlabel("Request number")
plt.ylabel("Latency [s]")
plt.tight_layout()

plt.legend()
plt.show()
