from progressbar import ProgressBar
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal
import numpy as np
import time
import sys
import os
import re

if  len(sys.argv) < 2:
    sys.exit("Error: 1 input argument expected, must be  <./TRAIN_WAV_FILE_FOLDER>")

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

for file in os.listdir(sys.argv[1]):
    if file.endswith(".wav"):
        audio_file = os.path.join(sys.argv[1],file)

        # Get sample label from audio file name
        file_label = file.split('_', 1)[0]

        # Read audio file
        fs, sig = wavfile.read(audio_file)

        # Original audio normalization
        sig = sig/max(sig)


        print('\n Computing training spectrograms from '+ file +' ...')

        # Make directory that will contain spectrograms
        save_path = "../tf_files/speakers/" + file_label

        if not os.path.exists(save_path):
            try:  
                os.mkdir(save_path)
            except OSError:  
                print (" Creation of the directory %s failed" % file_label)
            else:  
                print (" Successfully created the directory %s " % file_label)


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
            filename = save_path+'/'+file[:-4]+'-'+timestr+'-'+str(i)+'.jpg'
            fig.set_size_inches(4, 4)
            fig.savefig(filename, bbox_inches="tight",pad_inches=-0.3)
            plt.close(fig)

        print('\n Computing audio variants for '+ file +' ...')

        # Make directory that will contain all variant audio
        variant_folder_name = file_label + "_audio_variant"
        train_path = "./audio_samples_variants/" + variant_folder_name
        if not os.path.exists(train_path):
            try:  
                os.mkdir(train_path)
            except OSError:  
                print (" Creation of the directory %s failed" % variant_folder_name)
            else:  
                print (" Successfully created the directory %s " % variant_folder_name)

        for imp_file in os.listdir("./imp_resp"):
            # Impulse response reading, padding and normalization
            fs_imp, imp = wavfile.read("./imp_resp/"+imp_file)
            imp = np.pad(imp,(0, (sig.size-imp.size)), 'constant')
            imp = imp/max(imp)
            
            # Wav audio variant generation
            conv_sig = np.asarray(conv(sig,imp), dtype=np.float32)
            variant_file_name = file[:-4]+"-"+imp_file
            variant_file_path = train_path+"/" + variant_file_name
            wavfile.write(variant_file_path, fs, conv_sig)

            # Compute variant audio spectrograms
            print('\n Computing training spectrograms from '+ variant_file_name +' ...')
            fs, sig = wavfile.read(variant_file_path)

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
                filename = save_path+'/'+variant_file_name[:-4]+'-'+timestr+'-'+str(i)+'.jpg'
                fig.set_size_inches(4, 4)
                plt.savefig(filename, bbox_inches="tight",pad_inches=-0.3)
                plt.close(fig)