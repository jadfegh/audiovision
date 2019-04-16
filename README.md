# AudioVision

[![Alt Text](audiovision.gif)](https://youtu.be/pLerOFTmngQ)

### Tain data generation

Use `train_data_gen.py` script to generate training data samples. Use audio books or voice samples placed in the `train_data_gen\audio_samples` folder.

`train_data_gen.py` takes each mono wav audio files withing the `train_data_gen\audio_samples` folder and converts each 1s bin into a  ~ 224x224 spectrogram.

All original samples should be named after their labels, with the following filename structure:
1. label
2. _ (underscore)
3. anything_else.wav

All generated spectrogrammes will be placed within `tf_files/speakers` separated into distinct folders depending on their label.

Use the batch script `speaker_of_interest_picker.bat` to specify up to 4 speakers of interest from those in `tf_files/speakers`, all others will be merged into a new class *other*.


### Docker instruction for training
*Mostly inspired by [Pete Warden's TensorFlow for Poets](https://petewarden.com/2016/02/28/tensorflow-for-poets/)*

Run latest tensorflow container ([Installation instructions](https://www.tensorflow.org/install/docker)):

`docker run -it -p 0.0.0.0:6006:6006 --rm -v d:/:/p3 -w /. tensorflow/tensorflow:latest bash`

**Note:** p3 is a shared drive between PC and container containing this cloned repository 

```
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
```
  
**Note**: follow training progress on Tensorboard, from an other console:
```
docker ps

docker exec -it <container_id> bash

cd p3/audiovision

tensorboard --logdir tf_files/training_summaries &
```

If you encounter an error, run: `pkill -f "tensorboard"`


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