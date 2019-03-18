# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import time
import os

import random
import numpy as np
import tensorflow as tf
from flask import jsonify
from flask import Flask

app = Flask(__name__,static_url_path='')

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def load_graph(model_file):
  graph = tf.Graph()
  graph_def = tf.GraphDef()

  with open(model_file, "rb") as f:
    graph_def.ParseFromString(f.read())
  with graph.as_default():
    tf.import_graph_def(graph_def)

  return graph

def read_tensor_from_image_file(file_name, input_height=299, input_width=299,
				input_mean=0, input_std=255):
  input_name = "file_reader"
  output_name = "normalized"
  file_reader = tf.read_file(file_name, input_name)
  if file_name.endswith(".png"):
    image_reader = tf.image.decode_png(file_reader, channels = 3,
                                       name='png_reader')
  elif file_name.endswith(".gif"):
    image_reader = tf.squeeze(tf.image.decode_gif(file_reader,
                                                  name='gif_reader'))
  elif file_name.endswith(".bmp"):
    image_reader = tf.image.decode_bmp(file_reader, name='bmp_reader')
  else:
    image_reader = tf.image.decode_jpeg(file_reader, channels = 3,
                                        name='jpeg_reader')
  float_caster = tf.cast(image_reader, tf.float32)
  dims_expander = tf.expand_dims(float_caster, 0);
  resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
  normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
  sess = tf.Session()
  result = sess.run(normalized)

  return result

def load_labels(label_file):
  label = []
  proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
  for l in proto_as_ascii_lines:
    label.append(l.rstrip())
  return label

@app.route('/classify')
def running():
        response = {}
        random_lables = {}
        inference_folder_path = "static/audiovision/real_time"
        for folder in os.listdir(inference_folder_path):
          inference_file_path = inference_folder_path+"/"+folder

          # Random choice of a spectrogram in inference dataset
          file=random.choice(os.listdir(inference_file_path))

          random_lables[folder] = file

          file_name = inference_file_path+"/"+file
          model_file = "tf_files/retrained_graph.pb"
          label_file = "tf_files/retrained_labels.txt"
          input_height = 224
          input_width = 224
          input_mean = 128
          input_std = 128
          input_layer = "input"
          output_layer = "final_result"

          graph = load_graph(model_file)
          t = read_tensor_from_image_file(file_name,
                                          input_height=input_height,
                                          input_width=input_width,
                                          input_mean=input_mean,
                                          input_std=input_std)

          input_name = "import/" + input_layer
          output_name = "import/" + output_layer
          input_operation = graph.get_operation_by_name(input_name);
          output_operation = graph.get_operation_by_name(output_name);

          with tf.Session(graph=graph) as sess:
            start = time.time()
            results = sess.run(output_operation.outputs[0],
                              {input_operation.outputs[0]: t})
            end=time.time()
          results = np.squeeze(results)

          top_k = results.argsort()[-5:][::-1]
          labels = load_labels(label_file)

          print('\nPrediction for '+folder+' (in {:.3f}s):'.format(end-start))

          template = "{} (score={:0.5f})"

          # Response dictionary for each mic
          temp_dict = {}
          for i in top_k:
            print(template.format(labels[i], results[i]))
            temp_dict[labels[i]] = float(results[i])
            response[folder] = temp_dict
          response['img_lables'] = random_lables
        return jsonify(response)



# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response