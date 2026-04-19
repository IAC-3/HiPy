import librosa
import numpy as np


def get_waveform(filepath, num_points=1000):
    y, sr = librosa.load(filepath, sr=None, mono=True)
    chunk_size = len(y) // num_points
    waveform = np.array([
        np.max(np.abs(y[i * chunk_size:(i + 1) * chunk_size]))
        for i in range(num_points)
    ])
    waveform = waveform / (np.max(waveform) + 1e-10)
    return waveform


if __name__ == "__main__":
    path = "/Users/marcomattiuz/Music/Music/Media.localized/Music/alt-J/This Is All Yours/05 Left Hand Free 1.mp3"
    waveform = get_waveform(path)
    print(f"Points: {len(waveform)}")
    print(waveform)