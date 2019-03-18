import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
import _thread
import socket
import shutil
import time
import sys
import os

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

# Function for processing buffer thread
def buffer_processing(buffer,id):
    # Set start timer
    start_processing_time = time.time()
    
    # Split wav file 4 channels into mono
    print(" splitting audio channels ...")
    fs = 44100
    nbr_channels = 4
    audio_data = np.frombuffer(buffer, dtype=np.int16)

    # Compute each channel spectrograms
    for chnl in range(nbr_channels):
        sig = audio_data[chnl::nbr_channels]
        
        # Directory of buffer computed spectrograms 
        save_path = 'static/audiovision/real_time/mic_'+ str(chnl)
        
        if (max(sig)>0):
            print(" channel "+str(chnl)+" processing ...")
            # Audio normalization
            sig = sig/max(sig)
    
            # Create directory for spectrograms
            if not os.path.exists(save_path):
                try:  
                    os.mkdir(save_path)
                except OSError:  
                    print (" creation of the directory %s failed ..." % save_path)
                else:  
                    print (" successfully created the directory %s ..." % save_path)
            
            bin_nbr = int(sig.size/fs)

            for i in range(bin_nbr):
                seg_start = i*fs
                seg_end = (1+i)*fs
                bin_data = sig[seg_start:seg_end]
                _, spectrogram = log_specgram(bin_data, fs)
                
                fig = plt.figure()
                plt.imshow(spectrogram.T, aspect='auto', origin='lower')
                plt.axis('off')
                filename = save_path+'/spectrogram_'+str(i)+'.jpg'
                fig.set_size_inches(4, 4)
                fig.savefig(filename, bbox_inches="tight",pad_inches=-0.3)
                plt.close(fig)

        else:
            print(" channel "+str(chnl)+" is empty ...")
            if(os.path.exists(save_path)):
                shutil.rmtree(save_path, ignore_errors=True)
                print (" deteled the directory %s ..." % save_path)
            
    enlapsed_processing_time = time.time() - start_processing_time
    print( " processing time: %.2f sec\n" % enlapsed_processing_time)
    print("Buffer %d :" % (id))
    print(" filling raw pcm data into buffer ...")
    

# Bind the socket to the port
server_address = ('192.168.0.101', 10000)
print('starting up on %s port %s' % server_address, file=sys.stderr)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

# buffer size: 8 sec of 16 bits (2 bytes) 4 channel pcm data sampled at 44100 Hz
buffer_size =  5*44100*4*2

# buffer
buffer_chunks = b""

# buffer id
buffer_id  = 0

try:
    while True:
        # Wait for a connection
        print('waiting for a connection...')
        connection, client_address = sock.accept()
        
        try:
            print('connection from', client_address)

            # Time reference to mesure enlapsed time
            start_time = time.time()



            # Receive the data in small chunks and write it to temp pcm file
            while True:
                data = connection.recv(1024)
                if data:
                    if (len(buffer_chunks) <= buffer_size) :
                        if(buffer_id<1):
                            print("Buffer %d :" % (buffer_id))
                            buffer_id_temp = buffer_id
                            
                            print(" filling raw pcm data into buffer ...")
                            
                            # Update buffer id
                            buffer_id +=1
                            
                        buffer_chunks += data
                    else :
                        # Start buffer processing thread
                        _thread.start_new_thread(buffer_processing,(buffer_chunks,buffer_id))

                        # Clear buffer
                        buffer_chunks = b""
                        buffer_chunks += data

                        # Update buffer id
                        buffer_id +=1
                else:
                    print('no more data from', client_address, file=sys.stderr)
                    break   
        
        finally:
            # Clean up the connection
            connection.close()

except KeyboardInterrupt:
    print('Interrupted')