# -*- coding: utf-8 -*-
import sys

import numpy as np
import torch
device = "mps"

if __name__ in "__main__":
    for product_size in [64, 128, 256, 512, 1024]:
        for np_type in [np.float64, np.float32, np.float16]:
            signal_arr = np.random.random((product_size, 1)).astype(np_type)
            print(np_type, product_size, sys.getsizeof(signal_arr))

        for torch_type in [torch.float8_e5m2, torch.float8_e4m3fn]:
            signal_arr = torch.randn(product_size, 1, device=device, dtype=torch.float16)
            signal_arr_lower_bit = signal_arr.to(torch_type)
            print(torch_type, product_size, sys.getsizeof(signal_arr_lower_bit))

