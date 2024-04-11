#  Copyright (c) 2024.
from datetime import datetime

import numpy as np

from models import build_no_bn_shortcut_relu_model
total_depth = 25


model = build_no_bn_shortcut_relu_model(total_depth, primary_filter=32, input_size=(64, 2))
model.load_weights("RESNET_NO_BN_LAYER_d_25_f_1000_s_0.064_d0.50_PS_100/ep351-loss0.025-val_acc0.991.h5")

model.predict(np.zeros(shape=(1,64,2)))


before_execute = datetime.now()
res = model.predict(np.zeros(shape=(1000, 64, 2)))
after_execute = datetime.now()
print('Batch execution',after_execute - before_execute)

before_execute = datetime.now()
for i in range(1000):

    res = model.predict(np.zeros(shape=(1,64,2)))

after_execute = datetime.now()
print('Cycle execution',after_execute-before_execute)

