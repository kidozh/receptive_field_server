# -*- coding: utf-8 -*-
import sys

import numpy as np
import torch
device = "cpu"

bit_depth = [64, 32, 16]

if __name__ in "__main__":
    for product_size in [64, 128, 256, 512, 1024]:
        for type_idx, np_type in enumerate([np.float64, np.float32, np.float16]):
            signal_arr = np.random.random((product_size, 1)).astype(np_type)
            print(bit_depth[type_idx], product_size, sys.getsizeof(signal_arr))

        for torch_type in [torch.float8_e5m2]:
            signal_arr = torch.randn(product_size, 1, device=device, dtype=torch.float16)
            signal_arr_lower_bit = signal_arr.to(torch_type).cpu()
            signal_size = signal_arr_lower_bit.element_size() * signal_arr_lower_bit.nelement()
            print(8, product_size, signal_size)

