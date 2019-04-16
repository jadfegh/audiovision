import sys
import wave

for arg in sys.argv[1:]:
    with open(arg, 'rb') as pcmfile:
        pcmdata = pcmfile.read()
    with wave.open(arg[:-4]+'.wav', 'wb') as wavfile:
        wavfile.setparams((4, 2, 44100, 0, 'NONE', 'NONE'))
        wavfile.writeframes(pcmdata)