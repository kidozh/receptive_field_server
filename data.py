import os.path
import platform

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pywt
import scipy.signal
from scipy.fftpack import rfft, irfft, fftfreq, fft, ifft
from sklearn.utils import shuffle

RAW_SAMPLE_RATE = 100000

CURRENT_FILE_PATH = os.path.realpath(__file__)

# parent_dir = os.path.dirname(CURRENT_FILE_PATH)

if platform.system() == "Windows":
    parent_dir = r"C:\PythonProject\Philip-experiment"
elif platform.system() == "Darwin":
    parent_dir = r"~/data/Philip-exp"
else:
    parent_dir = r"~/python/Philip-experiment/"



SEGMENT_DATA_DIR = os.path.join(parent_dir, "data_auto_num")

XLSX_PATH = os.path.join(parent_dir, "./philip-data.xlsx")

BASE_SPINDLE_RATE = 4000 / 60

def get_cfrp_thickness(tool_index: int, hole_index: int) -> float:
    """
    get the thickness of CFRP
    :param tool_index: tool index
    :param hole_index: hole index
    :return: thickness of CFRP (mm)
    """
    data = pd.read_excel(XLSX_PATH, "CFRP")
    assert tool_index in [1, 2, 3]
    assert hole_index in [i for i in range(1, 28)]
    tool_label = "T%d" % tool_index
    return data[tool_label][hole_index - 1]


def get_al_thickness(tool_index: int, hole_index: int) -> float:
    """
    get the thickness of Al
    :param tool_index: tool index
    :param hole_index: hole index
    :return: thickness of Al (mm)
    """
    data = pd.read_excel(XLSX_PATH, "Al")

    assert tool_index in [1, 2, 3]
    assert hole_index in [i for i in range(1, 28)]
    tool_label = "T%d" % tool_index
    return data[tool_label][hole_index - 1]


def get_drilling_start_second(tool_index: int, hole_index: int) -> float:
    """
    get the start second of drilling process
    :param tool_index: tool index
    :param hole_index: hole index
    :return: start second (s)
    """
    data = pd.read_excel(XLSX_PATH, "start_sec")

    assert tool_index in [1, 2, 3]
    assert hole_index in [i for i in range(1, 28)]
    tool_label = "T%d" % tool_index

    return data[tool_label][hole_index - 1]


def get_drilling_end_second(tool_index: int, hole_index: int) -> float:
    """
    get the end second of drilling process
    :param tool_index: tool index
    :param hole_index: hole index
    :return: start second (s)
    """
    data = pd.read_excel(XLSX_PATH, "end_sec")

    assert tool_index in [1, 2, 3]
    assert hole_index in [i for i in range(1, 28)]
    tool_label = "T%d" % tool_index

    return data[tool_label][hole_index - 1]


def get_tool_wear(tool_index: int, hole_index: int) -> float:
    """
    get the end second of drilling process
    :param tool_index: tool index
    :param hole_index: hole index
    :return: start second (s)
    """
    XLSX_PATH = os.path.join(parent_dir, "./philip-data-new.xlsx")
    data = pd.read_excel(XLSX_PATH, "tool-wear.txt-hole")

    assert tool_index in [1, 2, 3]
    assert hole_index in [i for i in range(1, 28)]
    tool_label = "T%d" % tool_index

    return data[tool_label][hole_index - 1]


def get_tool_wear_corrected(tool_index: int, hole_index: int) -> float:
    """
    get the end second of drilling process
    :param tool_index: tool index
    :param hole_index: hole index
    :return: start second (s)
    """
    XLSX_PATH = os.path.join(parent_dir, "./philip-data-new.xlsx")
    data = pd.read_excel(XLSX_PATH, "Tool_wear_rows_real")

    assert tool_index in [1, 2, 3]
    assert hole_index in [i for i in range(1, 28)]
    tool_label = "T%d" % tool_index

    return data[tool_label][(hole_index - 1) // 3]


def get_drilling_duration(thickness: float, feed_rate=200) -> float:
    """
    get the drilling duration
    :param thickness: thickness of one layer
    :param feed_rate: feed rate (mm/min)
    :return: the traverse second (s)
    """
    return thickness / (feed_rate / 60)


def get_further_drill_time(tool_index: int) -> float:
    # no further milling time
    if tool_index == 1:
        return 0
    else:
        return get_drilling_duration(2.00)


CONE_TRAVERSE_SECOND = get_drilling_duration(2.403)

class Data:
    def get_segment_data_path(self, tool_index: int, hole_index: int) -> str:
        assert tool_index in [1, 2, 3]
        assert hole_index in [i for i in range(1, 28)]

        return os.path.join(SEGMENT_DATA_DIR, "T%dH%d.csv" % (tool_index + 1, hole_index))

    def get_segment_data(self, tool_index: int, hole_index: int) -> pd.DataFrame:
        return pd.read_csv(self.get_segment_data_path(tool_index, hole_index))