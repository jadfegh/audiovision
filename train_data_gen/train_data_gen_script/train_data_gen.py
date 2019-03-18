from progressbar import ProgressBar
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal
import numpy as np
import time
import sys
import os
import re

if  len(sys.argv) < 4:
    sys.exit("Error: 3 input arguments must be  <TRAIN_WAV_FILE>  <VALID_WAV_FILE>  <LABEL>")

# Function definition to compute spectrogram
def log_specgram(audio, sample_rate, window_size=20, step_size=10, eps=1e-10):
    nperseg = int(round(window_size * sample_rate / 1e3))
    noverlap = int(round(step_size * sample_rate / 1e3))
    freqs, _, spec = signal.spectrogram(audio,
                                    fs=sample_rate,
                                    window='hann',
                                    nperseg=nperseg,
                                    noverlap=noverlap,
                                    detrend=False)
    fmin = 80 # Hz
    fmax = 8000 # Hz
    freq_slice = np.where((freqs >= fmin) & (freqs <= fmax))
    freqs   = freqs[freq_slice]
    spec = spec[freq_slice,:][0]
    return freqs, np.log(spec.T.astype(np.float32) + eps)

# Function definition to compute convolution
def conv(signal, imp_resp):
    ## Convolution
    sig_fft = np.fft.fft(signal)
    imp_fft = np.fft.fft(imp_resp)
    convolved_signal = np.fft.ifft(sig_fft*imp_fft).real
    ## Normalization
    convolved_signal = convolved_signal/max(convolved_signal)
    return convolved_signal

for n in range(2):    
    audio_file = sys.argv[n+1]
    fs, sig = wavfile.read(audio_file)

    # Original audio normalization
    sig = sig/max(sig)

    if n == 0:
        print('\n Computing training spectrograms...')
    else :
        print('\n Computing validation spectrograms...')


    # Make directory that will contain spectrograms
    if n == 1:
        save_path = sys.argv[3] + '_valid'
    else:
        save_path = sys.argv[3]

    if not os.path.exists(save_path):
        try:  
            os.mkdir(save_path)
        except OSError:  
            print (" Creation of the directory %s failed" % save_path)
        else:  
            print (" Successfully created the directory %s " % save_path)


    # Compute original training spectograms
    pbar = ProgressBar()
    timestr = time.strftime("%Y_%m_%d-%H_%M_%S")

    bin_nbr = int(sig.size/fs)
    for i in pbar(range(bin_nbr)):
        seg_start = i*fs
        seg_end = (1+i)*fs
        data = sig[seg_start:seg_end]
        _, spectrogram = log_specgram(data, fs)
        
        fig = plt.figure()
        plt.imshow(spectrogram.T, aspect='auto', origin='lower')
        plt.axis('off')
        filename = save_path+'/'+save_path+'-'+timestr+'-'+str(i)+'.jpg'
        fig.set_size_inches(4, 4)
        fig.savefig(filename, bbox_inches="tight",pad_inches=-0.3)
        plt.close(fig)


    if n == 0 :
        print('\n Computing varinant training spectrograms...')
        # Make directory that will contain all variant audio
        train_path = sys.argv[3]+"_variant_audio"
        if not os.path.exists(train_path):
            try:  
                os.mkdir(train_path)
            except OSError:  
                print (" Creation of the directory %s failed" % train_path)
            else:  
                print (" Successfully created the directory %s " % train_path)

        for file in os.listdir("./imp_resp"):
            # Impulse response reading, padding and normalization
            fs_imp, imp = wavfile.read("./imp_resp/"+file)
            imp = np.pad(imp,(0, (sig.size-imp.size)), 'constant')
            imp = imp/max(imp)
            
            # Wav audio variant generation
            conv_sig = np.asarray(conv(sig,imp), dtype=np.float32)
            variant_file_name = train_path+"/variant-"+audio_file[:-4]+"-"+file
            wavfile.write(variant_file_name, fs, conv_sig)

        # Compute all variant audio spectrograms only for training file
        pbar = ProgressBar()
        for file in pbar(os.listdir(train_path)):
            fs, sig = wavfile.read(train_path+"/"+file)
            timestr = time.strftime("%Y_%m_%d-%H_%M_%S")

            bin_nbr = int(sig.size/fs)

            for i in range(bin_nbr):
                seg_start = i*fs
                seg_end = (1+i)*fs

                data = sig[seg_start:seg_end]
                _, spectrogram = log_specgram(data, fs)

                fig = plt.figure()
                plt.imshow(spectrogram.T, aspect='auto', origin='lower')
                plt.axis('off')
                filename = save_path+'/'+file[:-4]+timestr+'-'+str(i)+'.jpg'
                fig.set_size_inches(4, 4)
                plt.savefig(filename, bbox_inches="tight",pad_inches=-0.3)
                plt.close(fig)

