# AudioVision

![Alt Text](audiovision.gif)

### Docker instruction for training

docker run -it -p 0.0.0.0:6006:6006 --rm -v d:/:/p3 -w /. tensorflow/tensorflow:latest bash

cd p3/audiovision

IMAGE_SIZE=224

ARCHITECTURE="mobilenet_0.50_${IMAGE_SIZE}"

python -m scripts.retrain \
  --bottleneck_dir=tf_files/bottlenecks \
  --how_many_training_steps=1000 \
  --model_dir=tf_files/models/ \
  --summaries_dir=tf_files/training_summaries/"${ARCHITECTURE}" \
  --output_graph=tf_files/retrained_graph.pb \
  --output_labels=tf_files/retrained_labels.txt \
  --architecture="${ARCHITECTURE}" \
  --image_dir=tf_files/speakers
  
Note: folow training progress on Tensorboard:(on an other console)

docker ps

docker exec -it <container_id> bash

### Tain data generation

Use train_data_gen.py script to generate training data samples. Use audio books or voice samples.

train_data_gen.py takes mono wav audio files and converts each 1s bin into a  ~ 224x224 spectrogram.

Samples should be placed in folders with foldernames relative to trainning data label, all within tf_files/speakers 


### PC start "tcp - mic - spec - flow" TCP sink server (port 1000) + real-time inference spectrogram generator

cd p3/audiovision

python flow.py


### OPTINAL - PC start gstreamer TCP server (Port 1010)

gst-launch-1.0 -v tcpserversrc host=0.0.0.0 port=10000 ! rawaudioparse use-sink-caps=false format=pcm pcm-format=s16le sample-rate=44100 num-channels=4 ! audioconvert ! audioresample ! volume volume=7 ! directsoundsink

Note: true Audio Mixer, redirect gstreamer's stream to virtual cable


### Start pi TCP mic array client true ODAS live
Note: make sure port sink 1000 and 1010 are configured for separated.pcm and postfiltered.pcm 


### Docker instruction during inference + web service handler (Flask)

docker run -it -p 0.0.0.0:5000:5000 --rm -v d:/:/p3 -w /. tensorflow/tensorflow:latest bash

pip install flask

cd p3/audiovision

export FLASK_APP=tensorflow_flask.py

flask run --host=0.0.0.0


----------------------------------------
#### Liste of procedures:
1. CMD - flow.py
2. OPTIONAL - CMD - gstreamer command
3. SSH (putty) - ODAS live
4. DOCKER - tensorflow_flask.py
  







python -m scripts.retrain \
  --bottleneck_dir=tf_files/bottlenecks \
  --how_many_training_steps=1000 \
  --model_dir=tf_files/models/ \
  --summaries_dir=tf_files/training_summaries/"${ARCHITECTURE}" \
  --output_graph=tf_files/retrained_graph.pb \
  --output_labels=tf_files/retrained_labels.txt \
  --architecture="${ARCHITECTURE}" \
  --image_dir=tf_files/speakers
  
Note: folow training progress on Tensorboard:(on an other console)

docker ps

docker exec -it <container_id> bash

### Tain data generation

Use train_data_gen.py script to generate training data samples. Use audio books or voice samples.

train_data_gen.py takes mono wav audio files and converts each 1s bin into a  ~ 224x224 spectrogram.

Samples should be placed in folders with foldernames relative to trainning data label, all within tf_files/speakers 


### PC start "tcp - mic - spec - flow" TCP sink server (port 1000) + real-time inference spectrogram generator

cd p3/audiovision

python flow.py


### OPTINAL - PC start gstreamer TCP server (Port 1010)

gst-launch-1.0 -v tcpserversrc host=0.0.0.0 port=10000 ! rawaudioparse use-sink-caps=false format=pcm pcm-format=s16le sample-rate=44100 num-channels=4 ! audioconvert ! audioresample ! volume volume=7 ! directsoundsink

Note: true Audio Mixer, redirect gstreamer's stream to virtual cable


### Start pi TCP mic array client true ODAS live
Note: make sure port sink 1000 and 1010 are configured for separated.pcm and postfiltered.pcm 


### Docker instruction during inference + web service handler (Flask)

docker run -it -p 0.0.0.0:5000:5000 --rm -v d:/:/p3 -w /. tensorflow/tensorflow:latest bash

pip install flask

cd p3/audiovision

export FLASK_APP=tensorflow_flask.py

flask run --host=0.0.0.0


----------------------------------------
#### Liste of procedures:
1. CMD - flow.py
2. OPTIONAL - CMD - gstreamer command
3. SSH (putty) - ODAS live
4. DOCKER - tensorflow_flask.py
  






