# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
# pylint: disable=invalid-name
"""MobileNet v2 models for Keras.

MobileNetV2 is a general architecture and can be used for multiple use cases.
Depending on the use case, it can use different input layer size and
different width factors. This allows different width models to reduce
the number of multiply-adds and thereby
reduce inference cost on mobile devices.

MobileNetV2 is very similar to the original MobileNet,
except that it uses inverted residual blocks with
bottlenecking features. It has a drastically lower
parameter count than the original MobileNet.
MobileNets support any input size greater
than 32 x 32, with larger image sizes
offering better performance.

The number of parameters and number of multiply-adds
can be modified by using the `alpha` parameter,
which increases/decreases the number of filters in each layer.
By altering the image size and `alpha` parameter,
all 22 models from the paper can be built, with ImageNet weights provided.

The paper demonstrates the performance of MobileNets using `alpha` values of
1.0 (also called 100 % MobileNet), 0.35, 0.5, 0.75, 1.0, 1.3, and 1.4
For each of these `alpha` values, weights for 5 different input image sizes
are provided (224, 192, 160, 128, and 96).

The following table describes the performance of
MobileNet on various input sizes:
------------------------------------------------------------------------
MACs stands for Multiply Adds
 Classification Checkpoint|MACs (M)|Parameters (M)|Top 1 Accuracy|Top 5 Accuracy
--------------------------|------------|---------------|---------|----|---------
| [mobilenet_v2_1.4_224]  | 582 | 6.06 |          75.0 | 92.5 |
| [mobilenet_v2_1.3_224]  | 509 | 5.34 |          74.4 | 92.1 |
| [mobilenet_v2_1.0_224]  | 300 | 3.47 |          71.8 | 91.0 |
| [mobilenet_v2_1.0_192]  | 221 | 3.47 |          70.7 | 90.1 |
| [mobilenet_v2_1.0_160]  | 154 | 3.47 |          68.8 | 89.0 |
| [mobilenet_v2_1.0_128]  | 99  | 3.47 |          65.3 | 86.9 |
| [mobilenet_v2_1.0_96]   | 56  | 3.47 |          60.3 | 83.2 |
| [mobilenet_v2_0.75_224] | 209 | 2.61 |          69.8 | 89.6 |
| [mobilenet_v2_0.75_192] | 153 | 2.61 |          68.7 | 88.9 |
| [mobilenet_v2_0.75_160] | 107 | 2.61 |          66.4 | 87.3 |
| [mobilenet_v2_0.75_128] | 69  | 2.61 |          63.2 | 85.3 |
| [mobilenet_v2_0.75_96]  | 39  | 2.61 |          58.8 | 81.6 |
| [mobilenet_v2_0.5_224]  | 97  | 1.95 |          65.4 | 86.4 |
| [mobilenet_v2_0.5_192]  | 71  | 1.95 |          63.9 | 85.4 |
| [mobilenet_v2_0.5_160]  | 50  | 1.95 |          61.0 | 83.2 |
| [mobilenet_v2_0.5_128]  | 32  | 1.95 |          57.7 | 80.8 |
| [mobilenet_v2_0.5_96]   | 18  | 1.95 |          51.2 | 75.8 |
| [mobilenet_v2_0.35_224] | 59  | 1.66 |          60.3 | 82.9 |
| [mobilenet_v2_0.35_192] | 43  | 1.66 |          58.2 | 81.2 |
| [mobilenet_v2_0.35_160] | 30  | 1.66 |          55.7 | 79.1 |
| [mobilenet_v2_0.35_128] | 20  | 1.66 |          50.8 | 75.0 |
| [mobilenet_v2_0.35_96]  | 11  | 1.66 |          45.5 | 70.4 |

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from tensorflow.python.keras import backend
backend.set_image_data_format('channels_first') # !!!

from tensorflow.python.keras import layers
from tensorflow.python.keras.applications import imagenet_utils
from tensorflow.python.keras.engine import training
from tensorflow.python.keras.utils import data_utils
from tensorflow.python.keras.utils import layer_utils
from tensorflow.python.platform import tf_logging as logging
from tensorflow.python.util.tf_export import keras_export

# BASE_WEIGHT_PATH = ('https://storage.googleapis.com/tensorflow/'
#                     'keras-applications/mobilenet_v2/')


# @keras_export('keras.applications.mobilenet_v2.MobileNetV2',
#               'keras.applications.MobileNetV2')
def MobileNetV2TSM(input_shapes=None,
                alpha=1.0,
                weights=None,
                input_tensor=None,
                classes=27,
                **kwargs):
  """Instantiates the MobileNetV2 architecture.

  Reference paper:
  - [MobileNetV2: Inverted Residuals and Linear Bottlenecks]
  (https://arxiv.org/abs/1801.04381) (CVPR 2018)

  Optionally loads weights pre-trained on ImageNet.

  Caution: Be sure to properly pre-process your inputs to the application.
  Please see `applications.mobilenet_v2.preprocess_input` for an example.

  Arguments:
    input_shape: Optional shape tuple, to be specified if you would
      like to use a model with an input image resolution that is not
      (224, 224, 3).
      It should have exactly 3 inputs channels (224, 224, 3).
      You can also omit this option if you would like
      to infer input_shape from an input_tensor.
      If you choose to include both input_tensor and input_shape then
      input_shape will be used if they match, if the shapes
      do not match then we will throw an error.
      E.g. `(160, 160, 3)` would be one valid value.
    alpha: Float between 0 and 1. controls the width of the network.
      This is known as the width multiplier in the MobileNetV2 paper,
      but the name is kept for consistency with `applications.MobileNetV1`
      model in Keras.
      - If `alpha` < 1.0, proportionally decreases the number
          of filters in each layer.
      - If `alpha` > 1.0, proportionally increases the number
          of filters in each layer.
      - If `alpha` = 1, default number of filters from the paper
          are used at each layer.
    include_top: Boolean, whether to include the fully-connected
      layer at the top of the network. Defaults to `True`.
    weights: String, one of `None` (random initialization),
      'imagenet' (pre-training on ImageNet),
      or the path to the weights file to be loaded.
    input_tensor: Optional Keras tensor (i.e. output of
      `layers.Input()`)
      to use as image input for the model.
    pooling: String, optional pooling mode for feature extraction
      when `include_top` is `False`.
      - `None` means that the output of the model
          will be the 4D tensor output of the
          last convolutional block.
      - `avg` means that global average pooling
          will be applied to the output of the
          last convolutional block, and thus
          the output of the model will be a
          2D tensor.
      - `max` means that global max pooling will
          be applied.
    classes: Integer, optional number of classes to classify images
      into, only to be specified if `include_top` is True, and
      if no `weights` argument is specified.
    classifier_activation: A `str` or callable. The activation function to use
      on the "top" layer. Ignored unless `include_top=True`. Set
      `classifier_activation=None` to return the logits of the "top" layer.
    **kwargs: For backwards compatibility only.

  Returns:
    A `keras.Model` instance.

  Raises:
    ValueError: in case of invalid argument for `weights`,
      or invalid input shape or invalid alpha, rows when
      weights='imagenet'
    ValueError: if `classifier_activation` is not `softmax` or `None` when
      using a pretrained top layer.
  """
  
  # 11 tensors: 0 is an input image and buffer is the rest 10 tensors
  print(input_shapes)
  inputs = [
    layers.Input(shape=input_shapes[i], name=f'i{i}') 
    for i in range(len(input_shapes))
  ]
  img_input = inputs[0]
  shift_buffer = inputs[1:]
  out_buffer = []

  channel_axis = 1 if backend.image_data_format() == 'channels_first' else -1

  first_block_filters = _make_divisible(32 * alpha, 8)
#   x = layers.ZeroPadding2D(
#       padding=imagenet_utils.correct_pad(img_input, 3),
#       name='Conv1_pad')(img_input)
  x = img_input
    
  block_id = 0
  x = layers.Conv2D(
      first_block_filters,
      kernel_size=3,
      strides=(2, 2),
      padding='valid',  # !!!
      use_bias=False,
      name='features.{}.0'.format(block_id))(
          x)
  x = layers.BatchNormalization(
      axis=channel_axis, epsilon=1e-5, momentum=0.1, name='features.{}.1'.format(block_id))(
          x)
  x = layers.ReLU(6., name='features.{}.relu.2'.format(block_id))(x)

  block_id += 1
  x = _inverted_res_block(  # 0
      x, filters=16, alpha=alpha, stride=1, expansion=1, block_id=block_id)

  block_id += 1
  x = _inverted_res_block(  # 1
      x, filters=24, alpha=alpha, stride=2, expansion=6, block_id=block_id)
  block_id += 1
  x, buf = _inverted_res_block_with_shift(  # 2
      x, shift_buffer[0], filters=24, alpha=alpha, stride=1, expansion=6, block_id=block_id)
  order_id = backend.zeros((1, buf.shape[1], buf.shape[2], 1)) + 1.0  # !!! assumes that `channels_last`, not `first`
  buf = layers.Concatenate(axis=channel_axis)([buf, order_id])
  out_buffer.append(buf)

  block_id += 1
  x = _inverted_res_block(  # 3
      x, filters=32, alpha=alpha, stride=2, expansion=6, block_id=block_id)
  block_id += 1
  x, buf = _inverted_res_block_with_shift(  # 4
      x, shift_buffer[1], filters=32, alpha=alpha, stride=1, expansion=6, block_id=block_id)
  order_id = backend.zeros((1, buf.shape[1], buf.shape[2], 1)) + 2.0
  buf = layers.Concatenate(axis=channel_axis)([buf, order_id])
  out_buffer.append(buf)
  block_id += 1
  x, buf = _inverted_res_block_with_shift(  # 5
      x, shift_buffer[2], filters=32, alpha=alpha, stride=1, expansion=6, block_id=block_id)
  order_id = backend.zeros((1, buf.shape[1], buf.shape[2], 1)) + 3.0
  buf = layers.Concatenate(axis=channel_axis)([buf, order_id])
  out_buffer.append(buf)

  block_id += 1
  x = _inverted_res_block(  # 6
      x, filters=64, alpha=alpha, stride=2, expansion=6, block_id=block_id)
  block_id += 1
  x, buf = _inverted_res_block_with_shift(  # 7
      x, shift_buffer[3], filters=64, alpha=alpha, stride=1, expansion=6, block_id=block_id)
  order_id = backend.zeros((1, buf.shape[1], buf.shape[2], 1)) + 4.0
  buf = layers.Concatenate(axis=channel_axis)([buf, order_id])
  out_buffer.append(buf)
  block_id += 1
  x, buf = _inverted_res_block_with_shift(  # 8
      x, shift_buffer[4], filters=64, alpha=alpha, stride=1, expansion=6, block_id=block_id)
  order_id = backend.zeros((1, buf.shape[1], buf.shape[2], 1)) + 5.0
  buf = layers.Concatenate(axis=channel_axis)([buf, order_id])
  out_buffer.append(buf)
  block_id += 1
  x, buf = _inverted_res_block_with_shift(  # 9
      x, shift_buffer[5], filters=64, alpha=alpha, stride=1, expansion=6, block_id=block_id)
  order_id = backend.zeros((1, buf.shape[1], buf.shape[2], 1)) + 6.0
  buf = layers.Concatenate(axis=channel_axis)([buf, order_id])
  out_buffer.append(buf)

  block_id += 1
  x = _inverted_res_block(  # 10
      x, filters=96, alpha=alpha, stride=1, expansion=6, block_id=block_id)
  block_id += 1
  x, buf = _inverted_res_block_with_shift(  # 11
      x, shift_buffer[6], filters=96, alpha=alpha, stride=1, expansion=6, block_id=block_id)
  order_id = backend.zeros((1, buf.shape[1], buf.shape[2], 1)) + 7.0
  buf = layers.Concatenate(axis=channel_axis)([buf, order_id])
  out_buffer.append(buf)
  block_id += 1
  x, buf = _inverted_res_block_with_shift(  # 12
      x, shift_buffer[7], filters=96, alpha=alpha, stride=1, expansion=6, block_id=block_id)
  order_id = backend.zeros((1, buf.shape[1], buf.shape[2], 1)) + 8.0
  buf = layers.Concatenate(axis=channel_axis)([buf, order_id])
  out_buffer.append(buf)

  block_id += 1
  x = _inverted_res_block(  # 13
      x, filters=160, alpha=alpha, stride=2, expansion=6, block_id=block_id)
  block_id += 1
  x, buf = _inverted_res_block_with_shift(  # 14
      x, shift_buffer[8], filters=160, alpha=alpha, stride=1, expansion=6, block_id=block_id)
  order_id = backend.zeros((1, buf.shape[1], buf.shape[2], 1)) + 9.0
  buf = layers.Concatenate(axis=channel_axis)([buf, order_id])
  out_buffer.append(buf)
  block_id += 1
  x, buf = _inverted_res_block_with_shift(  # 15
      x, shift_buffer[9], filters=160, alpha=alpha, stride=1, expansion=6, block_id=block_id)
  order_id = backend.zeros((1, buf.shape[1], buf.shape[2], 1)) + 10.0
  buf = layers.Concatenate(axis=channel_axis)([buf, order_id])
  out_buffer.append(buf)

  block_id += 1
  x = _inverted_res_block(  # 16
      x, filters=320, alpha=alpha, stride=1, expansion=6, block_id=block_id)

  # no alpha applied to last conv as stated in the paper:
  # if the width multiplier is greater than 1 we
  # increase the number of output channels
  if alpha > 1.0:
    last_block_filters = _make_divisible(1280 * alpha, 8)
  else:
    last_block_filters = 1280

  block_id += 1
  x = layers.Conv2D(
      last_block_filters, kernel_size=1, padding='valid', use_bias=False, name='features.{}.0'.format(block_id))(
          x)
  x = layers.BatchNormalization(
      axis=channel_axis, epsilon=1e-5, momentum=0.1, name='features.{}.1'.format(block_id))(
          x)
  x = layers.ReLU(6., name='features.{}.relu.2'.format(block_id))(x)

  x = layers.GlobalAveragePooling2D(data_format=backend.image_data_format())(x)
#     imagenet_utils.validate_activation(classifier_activation, weights)
  x = layers.Dense(classes, activation=None, name='classifier')(x)

  # Create model.
  model = training.Model(inputs, [x, *out_buffer], name='mobilenetv2_%0.2f_%s' % (alpha, 224))

  return model


def _inverted_res_block(inputs, expansion, stride, alpha, filters, block_id):
  """Inverted ResNet block."""
  channel_axis = 1 if backend.image_data_format() == 'channels_first' else -1

  in_channels = backend.int_shape(inputs)[channel_axis]
  pointwise_conv_filters = int(filters * alpha)
  pointwise_filters = _make_divisible(pointwise_conv_filters, 8)
  x = inputs
  prefix = 'features.{}'.format(block_id)

  cnt = 0  # for name compatibility with PyTorch
  # Expand
  if expansion > 1:
      x = layers.Conv2D(
          expansion * in_channels,
          kernel_size=1,
          padding='valid',
          use_bias=False,
          activation=None,
          name=prefix + '.conv.{}'.format(cnt))(
              x)
      cnt += 1
      x = layers.BatchNormalization(
          axis=channel_axis,
          epsilon=1e-5,
          momentum=0.1,
          name=prefix + '.conv.{}'.format(cnt))(
              x)
      cnt += 1
      x = layers.ReLU(6., name=prefix + '.conv.relu.{}'.format(cnt))(x)
      cnt += 1

  # Depthwise
  x = layers.DepthwiseConv2D(
      kernel_size=3,
      strides=stride,
      activation=None,
      use_bias=False,
      padding='same' if stride == 1 else 'valid',  # !!!
      name=prefix + '.conv.{}'.format(cnt))(
          x)
  cnt += 1
  x = layers.BatchNormalization(
      axis=channel_axis,
      epsilon=1e-5,
      momentum=0.1,
      name=prefix + '.conv.{}'.format(cnt))(
          x)
  cnt += 1
  x = layers.ReLU(6., name=prefix + '.conv.relu.{}'.format(cnt))(x)
  cnt += 1

  # Project
  x = layers.Conv2D(
      pointwise_filters,
      kernel_size=1,
      padding='valid',
      use_bias=False,
      activation=None,
      name=prefix + '.conv.{}'.format(cnt))(
          x)
  cnt += 1
  x = layers.BatchNormalization(
      axis=channel_axis,
      epsilon=1e-5,
      momentum=0.1,
      name=prefix + '.conv.{}'.format(cnt))(
          x)
  cnt += 1

  if in_channels == pointwise_filters and stride == 1:
    return layers.Add(name=prefix + 'add')([inputs, x])
  return x


def _inverted_res_block_with_shift(inputs, shift_buffer, expansion, stride, alpha, filters, block_id):
  """Inverted ResNet block with Temporal Shift Module."""
  channel_axis = 1 if backend.image_data_format() == 'channels_first' else -1

  in_channels = backend.int_shape(inputs)[channel_axis]
  pointwise_conv_filters = int(filters * alpha)
  pointwise_filters = _make_divisible(pointwise_conv_filters, 8)
    
  # !!!
  c = inputs.shape[channel_axis]
  if channel_axis == 1:
    x1, x2 = inputs[:, : c // 8], inputs[:, c // 8:]
  else:
    x1, x2 = inputs[:, :, :, : c // 8], inputs[:, :, :, c // 8:]
  x = layers.concatenate([shift_buffer, x2], axis=channel_axis)
  prefix = 'features.{}'.format(block_id)

  cnt = 0  # for name compatibility with PyTorch
  # Expand
  if expansion > 1:
      x = layers.Conv2D(
          expansion * in_channels,
          kernel_size=1,
          padding='valid',
          use_bias=False,
          activation=None,
          name=prefix + '.conv.{}'.format(cnt))(
              x)
      cnt += 1
      x = layers.BatchNormalization(
          axis=channel_axis,
          epsilon=1e-5,
          momentum=0.1,
          name=prefix + '.conv.{}'.format(cnt))(
              x)
      cnt += 1
      x = layers.ReLU(6., name=prefix + '.conv.relu.{}'.format(cnt))(x)
      cnt += 1

  # Depthwise
  x = layers.DepthwiseConv2D(
      kernel_size=3,
      strides=stride,
      activation=None,
      use_bias=False,
      padding='same' if stride == 1 else 'valid',  # !!!
      name=prefix + '.conv.{}'.format(cnt))(
          x)
  cnt += 1
  x = layers.BatchNormalization(
      axis=channel_axis,
      epsilon=1e-5,
      momentum=0.1,
      name=prefix + '.conv.{}'.format(cnt))(
          x)
  cnt += 1
  x = layers.ReLU(6., name=prefix + '.conv.relu.{}'.format(cnt))(x)
  cnt += 1

  # Project
  x = layers.Conv2D(
      pointwise_filters,
      kernel_size=1,
      padding='valid',
      use_bias=False,
      activation=None,
      name=prefix + '.conv.{}'.format(cnt))(
          x)
  cnt += 1
  x = layers.BatchNormalization(
      axis=channel_axis,
      epsilon=1e-5,
      momentum=0.1,
      name=prefix + '.conv.{}'.format(cnt))(
          x)
  cnt += 1
    
  return layers.Add(name=prefix + 'add')([inputs, x]), x1  # !!!


def _make_divisible(v, divisor, min_value=None):
  if min_value is None:
    min_value = divisor
  new_v = max(min_value, int(v + divisor / 2) // divisor * divisor)
  # Make sure that round down does not go down by more than 10%.
  if new_v < 0.9 * v:
    new_v += divisor
  return new_v


# @keras_export('keras.applications.mobilenet_v2.preprocess_input')
# def preprocess_input(x, data_format=None):
#   return imagenet_utils.preprocess_input(x, data_format=data_format, mode='tf')


# @keras_export('keras.applications.mobilenet_v2.decode_predictions')
# def decode_predictions(preds, top=5):
#   return imagenet_utils.decode_predictions(preds, top=top)


# preprocess_input.__doc__ = imagenet_utils.PREPROCESS_INPUT_DOC.format(
#     mode='', ret=imagenet_utils.PREPROCESS_INPUT_RET_DOC_TF)
# decode_predictions.__doc__ = imagenet_utils.decode_predictions.__doc__
