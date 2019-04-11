import pyaudio

p = pyaudio.PyAudio()
print(p.get_default_input_device_info())
print(p.get_device_count())
for i in range(p.get_device_count()):
    print(i, p.get_device_info_by_index(i))