import typing
import wave
from enum import Enum, auto

import numpy as np
import pyaudio

from util import noalsaerr


# sudo apt-get install libatlas-base-dev
# from matplotlib.mlab import window_hanning,specgram

class DeviceType(Enum):
    INPUT = auto()
    OUTPUT = auto()
    BOTH = auto


class AudioRecorder:
    def __init__(self,
                 fmt=2,
                 channels=2,
                 sampling_rate=43900,
                 chunk_size=1024
                 ):
        with noalsaerr():
            self.audio_api = pyaudio.PyAudio()

        self.fmt = self.audio_api.get_format_from_width(fmt)
        self.channels = channels
        self.sampling_rate = sampling_rate
        self.chunk_size = chunk_size

    def info(self):
        return self.audio_api.get_default_host_api_info()

    def device(self, index=None, device_type=DeviceType.INPUT):
        if index is None:
            if device_type.INPUT:
                return self.audio_api.get_default_input_device_info()
            elif device_type.OUTPUT:
                return self.audio_api.get_default_output_device_info()
            else:
                return (
                    self.audio_api.get_default_output_device_info(),
                    self.audio_api.get_default_input_device_info()
                )
        else:
            devices_dic = self.devices(device_type)
            filtered_list = list(filter(
                lambda d: d["index"] == index,
                devices_dic.values())
            )
            if filtered_list:
                return filtered_list[0]
            else:
                raise IndexError("Invalid device index")

    def devices(self, device_type=DeviceType.INPUT):
        devices_dic = {}
        for ii in range(self.audio_api.get_device_count()):
            device = self.audio_api.get_device_info_by_index(ii)
            devices_dic[device["name"]] = device

        if device_type == DeviceType.OUTPUT:
            return {name: device for (name, device)
                    in devices_dic.items() if device.get('maxOutputChannels') > 0}
        elif device_type == DeviceType.INPUT:
            return {name: device for (name, device)
                    in devices_dic.items() if device.get('maxInputChannels') > 0}
        else:
            return devices_dic

    def record(self, output_file: str, device: typing.Union[int, dict] = 1, time: float = 3.0):
        if isinstance(device, dict):
            device = device["index"]
        stream = self.audio_api.open(
            format=self.fmt,
            rate=self.sampling_rate,
            channels=self.channels,
            input_device_index=device,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        frames = []
        # loop through stream and append audio chunks to frame array
        for ii in range(0, int((self.sampling_rate / self.chunk_size) * time)):
            data = stream.read(self.chunk_size)
            frames.append(data)
        # stop the stream, close it
        stream.stop_stream()
        stream.close()
        # self.audio_api.terminate()
        # save the audio frames as .wav file
        sampwidth = self.audio_api.get_sample_size(self.fmt)
        wavefile = wave.open(output_file, 'wb')
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(sampwidth)
        wavefile.setframerate(self.sampling_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()

    def play(self, input_file: str, device: typing.Union[int, dict] = 1):
        if isinstance(device, dict):
            device = device["index"]
        wf = wave.open(input_file, 'rb')
        stream = self.audio_api.open(format=self.audio_api.get_format_from_width(wf.getsampwidth()),
                                     channels=wf.getnchannels(),
                                     rate=wf.getframerate(),
                                     output_device_index=device,
                                     output=True)
        # Read data in chunks
        data = wf.readframes(self.chunk_size)
        # Play the sound by writing the audio data to the stream
        while data != b'':
            stream.write(data)
            data = wf.readframes(self.chunk_size)
        # Close and terminate the stream
        stream.close()
        # self.audio_api.terminate()

    def listen(self):
        config = {
            "format": self.fmt,
            "channels": self.channels,
            "rate": self.sampling_rate,
            "input": True,
            "output": True,
            "frames_per_buffer": self.chunk_size
        }
        stream = self.audio_api.open(**config)
        nfft = 1024  # 256#1024
        while True:
            try:
                if not stream.is_stopped():
                    data = stream.read(self.chunk_size)  # read audio stream
                    data_int = np.frombuffer(data, dtype=np.int32)
                    stream.write(data_int, self.chunk_size)  # play back audio stream
                    data_flt = data_int.astype('float32')
                    #plt.pcolormesh(t, f, Sxx, cmap="inferno")
                    #plt.specgram(data_flt, Fs=self.sampling_rate, cmap="inferno")
                    #plt.gca().invert_yaxis()
                    #plt.pause(0.005)
                else:
                    stream.close()
                    break
            except KeyboardInterrupt:
                stream.stop_stream()


if __name__ == '__main__':
    recorder = AudioRecorder()
    in_device = recorder.device(device_type=DeviceType.INPUT)
    out_device = recorder.device(device_type=DeviceType.OUTPUT)
    wav_file = "test-other.wav"
    print("recording...")
    recorder.record(wav_file, device=in_device, time=10.0)
    print("playing...")
    recorder.play(wav_file, device=out_device)
    #recorder.listen()
    print(recorder.devices(device_type=DeviceType.OUTPUT))
