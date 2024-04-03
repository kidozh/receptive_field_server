from keras.models import *
from keras.layers import *
from keras.optimizers import *


def resnet_no_bn_shortcut_relu_block(input, stride: int, filter=32, kernel_size=3, dropout=0.5):
    out = Conv1D(filter, kernel_size, padding='same', strides=stride, use_bias=False)(input)

    out = ReLU()(out)
    out = Dropout(dropout)(out)
    out = Conv1D(filter, kernel_size, padding='same', strides=1, use_bias=False)(out)

    out = ReLU()(out)
    out = Dropout(dropout)(out)

    if stride == 1:
        shortcut = input
    else:
        shortcut = Conv1D(filter, kernel_size, padding='same', use_bias=False, strides=stride)(input)

        shortcut = ReLU()(shortcut)

    out = add([out, shortcut])
    return out


def build_no_bn_shortcut_relu_model(depth: int, input_size=(128, 2), primary_filter=32, max_filter=256):
    STRIDE_PER_BLOCK = 5

    inp = Input(shape=input_size)

    out = inp

    out = resnet_no_bn_shortcut_relu_block(out, 2, filter=primary_filter, kernel_size=5,
                                           dropout=0.5)

    for layer_num in range(depth):
        stride_idx = layer_num // STRIDE_PER_BLOCK
        stride = 2 if layer_num != 0 and layer_num % STRIDE_PER_BLOCK == 0 else 1
        filter = min(max_filter, primary_filter * 2 ** stride_idx)

        out = resnet_no_bn_shortcut_relu_block(out, stride, filter=filter, kernel_size=3, dropout=0.5)

    out = Flatten()(out)
    out = Dense(5, activation="softmax")(out)
    model = Model(inputs=[inp], outputs=[out])
    model.compile(loss='categorical_crossentropy', metrics=['categorical_crossentropy', 'acc'])
    return model


class StrideStopModel:
    pass
