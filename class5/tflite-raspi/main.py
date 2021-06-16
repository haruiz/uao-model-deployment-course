import wave

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pyaudio
import scipy
import tflite_runtime.interpreter as tflite
from scipy import signal
import python_speech_features
from util import noalsaerr
from scipy.io import wavfile

def read_wav(input_file):
    chunk_size = 1024
    with noalsaerr():
        pa = pyaudio.PyAudio()
    wf = wave.open(input_file, 'rb')
    print(wf.getnchannels())
    print(wf.getframerate())
    print(wf.getsampwidth())
    stream = pa.open(format=pa.get_format_from_width(wf.getsampwidth()),
                                 channels=wf.getnchannels(),
                                 rate=wf.getframerate(),
                                 output=True)
    # Read data in chunks
    data = wf.readframes(chunk_size)
    # Play the sound by writing the audio data to the stream
    data_chunks = []
    while data != b'':
        stream.write(data)
        data = wf.readframes(chunk_size)
        audio_data = np.frombuffer(data, dtype=np.int16)
        if len(audio_data) > 0:
            #normalized_data = audio_data / np.max(audio_data)
            #freq_data = np.fft.fft(normalized_data)
            #b, a = signal.butter(5, 1000 / (wf.getframerate() / 2), btype='highpass')
            #new_data = signal.lfilter(b, a, freq_data)
            data_chunks.append(audio_data)
    wave_data = np.hstack(data_chunks)
    # Close and terminate the stream
    stream.close()
    pa.terminate()
    return wave_data


#https://towardsdatascience.com/getting-to-know-the-mel-spectrogram-31bca3e2d9d0
#https://medium.com/analytics-vidhya/understanding-the-mel-spectrogram-fca2afa2ce53
#https://medium.com/analytics-vidhya/understanding-the-mel-spectrogram-fca2afa2ce53
def get_spectogram(waveform, target_size = 16000):
    waveform_length = np.shape(waveform)[0]
    if waveform_length < target_size:
        target_shape = 16000 - waveform_length
    else:
        target_shape = waveform_length - target_size
    padding = np.zeros(target_shape, dtype=np.float32)
    waveform = waveform.astype(np.float32)
    equal_length = np.concatenate([waveform, padding], 0) #shape: (124, 129)
    # mfccs = python_speech_features.base.mfcc(equal_length,
    #                                          samplerate=16000,
    #                                          winlen=0.003,
    #                                          winstep=0.01,
    #                                          numcep=129,
    #                                          nfilt=129,
    #                                          nfft=1024,
    #                                          preemph=0.0,
    #                                          ceplifter=0,
    #                                          highfreq = 0,
    #                                          appendEnergy=False,
    #                                          winfunc=np.hanning)
    # mfccs = mfccs.transpose()
    # print(mfccs.shape)
    # fig = plt.figure(figsize=(10,10))
    # plt.imshow(mfccs)
    # plt.show()
    # spectrogram = tf.signal.stft(
    #     equal_length, frame_length=255, frame_step=128)
    f, t, Zxx  = signal.stft(equal_length, nperseg=255)
    spec = np.abs(Zxx)
    print(spec.shape)
    spec = spec[:,:118]
    spec = cv2.resize(spec, (129,124))
    print(spec.shape)
    log_spec = 10 * np.log(spec)
    height = log_spec.shape[0]
    width = log_spec.shape[1]
    X = np.linspace(0, np.size(Zxx), num=width, dtype=int)
    Y = range(height)
    fig = plt.figure(figsize=(10,10))
    plt.pcolormesh(X, Y, log_spec)
    plt.show()
    return spec

def plot_waveform(data):
    fig = plt.figure(figsize=(10,5))
    ax = fig.add_subplot(111)
    ax.plot(data)
    ax.set_yticks(np.arange(-1.2, 1.2, 0.2))
    plt.show()



if __name__ == '__main__':
    f = "test-audio.wav"
    audio_data = read_wav(f)
    sample_rate, data = wavfile.read(f)
    print(sample_rate)

    #plot_waveform(audio_data)
    #spectogram = get_spectogram(audio_data)
    # spectogram = np.expand_dims(spectogram, 2) # channels dimension
    # spectogram = np.expand_dims(spectogram, 0) # batch dimension
    # print(spectogram.shape)
    #
    # interpreter = tflite.Interpreter(model_path="model.tflite")
    # input_details = interpreter.get_input_details()
    # output_details = interpreter.get_output_details()
    # interpreter.allocate_tensors()
    # interpreter.set_tensor(input_details[0]['index'], spectogram)
    # interpreter.invoke()
    # output = interpreter.get_tensor(output_details[0]['index'])
    # print(np.argmax(output))

    # recorder = AudioRecorder(sampling_rate=16000, channels=2, fmt=2)
    # in_device = recorder.device(device_type=DeviceType.INPUT)
    # wav_file = "test.wav"
    # print("recording...")
    # recorder.record(wav_file, device=in_device, time=3.0)
    # print("classifying...")
    # wave_data = read_wav(wav_file)
    # plot_waveform(wave_data)
    # spec = get_spectogram(wave_data)
    # spec = np.expand_dims(spec, 2)
    # spec = np.expand_dims(spec, 0)
    # print(spec.shape)
    #
    # interpreter = tflite.Interpreter(model_path="model.tflite")
    # interpreter.allocate_tensors()
    # input_details = interpreter.get_input_details()
    # output_details = interpreter.get_output_details()
    # interpreter.set_tensor(input_details[0]['index'], spec)
    # interpreter.invoke()
    # output = interpreter.get_tensor(output_details[0]['index'])
    # print(np.argmax(output))
