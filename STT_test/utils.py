import numpy as np
import os

def load_np_file(file_path):
    data = np.load(file_path, allow_pickle=True)
    return data

if __name__ == '__main__':
    data = load_np_file('test.npy')
    print(data)
