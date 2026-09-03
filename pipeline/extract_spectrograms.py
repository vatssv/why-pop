from email.mime import audio
from mmap import mmap
import os
from posixpath import sep
import random
import sys
from cv2 import threshold, transform
from isort import file
import librosa
import librosa.display
import matplotlib.pyplot as plt
from regex import E
from rsa import sign
from sympy import residue, total_degree
# from matplotlib import transforms
from torchaudio import transforms
from torchvision import transforms as T
import tensorflow as tf
from PIL import Image
import torch
import numpy as np
import torchaudio
import csv
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from IPython.display import HTML
import pandas as pd
from skimage.util import img_as_float
import skimage.io

class extract_spectrograms(object):
    def __init__(self, dir_path):
        self.path = dir_path

    def fetch_file_paths(self):
        self.files_list = []
        for root, dirs, files in os.walk(self.path):
            # print(f'Roots: {root}, Dirs: {dirs}, Files: {files}')
            if len(dirs) == 0:
                # file_counter = 0
                for file in files:
                    # if file_counter == 10:
                    #     break
                    self.files_list.append(os.path.join(root, file))
                    # file_counter += 1

        # print('Fetched files: ', self.files_list)
    
        return self.files_list

    @staticmethod
    def augment_spectrograms(spec, mask_percent=0.1, frequency_masks=1, time_masks=1):
        # print('Now augmenting spectrograms')
        # print('Spec is: ', spec, spec.shape)
        _, mels, steps = spec.shape
        mask_val = spec.mean()
        augmented_spec1, augmented_spec2, augmented_spec3 = spec, spec, spec

        frequency_masks_params = mask_percent * mels

        for i in range(frequency_masks):
            augmented_spec1 = transforms.FrequencyMasking(frequency_masks_params)(augmented_spec1)
            augmented_spec3 = transforms.FrequencyMasking(frequency_masks_params)(augmented_spec3)

        time_masks_param = mask_percent * steps

        for i in range(time_masks):
            augmented_spec2 = transforms.TimeMasking(time_masks_param)(augmented_spec2)
            augmented_spec3 = transforms.TimeMasking(time_masks_param)(augmented_spec3)

        return np.array(augmented_spec1), np.array(augmented_spec2), np.array(augmented_spec3)

    @staticmethod
    def save_spectrogram_image(spec: np.array, sample_rate: int, output_dir: str, file_name: str, context: str = 'original') -> None:

        fig = plt.figure(figsize=(14, 5))
        librosa.display.specshow(spec, sr=sample_rate, x_axis='time', y_axis='mel')
        plt.colorbar(format='%+2.0f dB')
        base = os.path.basename(file_name)
        base = os.path.splitext(base)[0]
        file_dir = file_name.split('/')[-2]
        # fig.savefig(f'{self.output_dir}{file_dir}_{base}.png')
        print(f'File name is: {output_dir}{file_dir}_{base}.png, individual paramters are: Output Dir: {output_dir}, Base: {base}, File Dir: {file_dir}, File: {file_name}')

    def load_file(self, file_name):
        try:
            signal, sample_rate = torchaudio.load(file_name)
            # print('Signal and sample after loading ', signal, sample_rate, signal.shape[0])
            signal, sample_rate = self.standardize_channel(signal=signal, sample_rate=sample_rate, no_of_channels=2)
            signal, sample_rate = self.resample_audio(signal=signal, sample_rate=sample_rate)
            return (signal, sample_rate)
        except RuntimeError:
            print('Error loading audio file, moving on.')
            return None, None

    @staticmethod
    def standardize_channel(signal, sample_rate, no_of_channels):
        if no_of_channels == signal.shape[0]:
            return signal, sample_rate

        if no_of_channels == 1:
            return signal[:1, :], sample_rate

        if no_of_channels == 2:
            return ((torch.cat([signal, signal]), sample_rate))

    @staticmethod
    def resample_audio(signal, sample_rate):
        standard_sample_rate = 44100
        # print('Sample rate is: ', sample_rate)
        if sample_rate == standard_sample_rate:
            return signal, sample_rate

        channel_one_signal = torchaudio.transforms.Resample(sample_rate, standard_sample_rate)(signal[:1, :])
        channel_two_signal = torchaudio.transforms.Resample(sample_rate, standard_sample_rate)(signal[1:, :])

        return ((torch.cat([channel_one_signal, channel_two_signal]), standard_sample_rate))

    @staticmethod
    def resize(signal, sample_rate, audio_length):
        num_rows, signal_length = signal.shape
        max_length = sample_rate//1000 * audio_length

        if signal_length > max_length:
            signal = signal[:, :max_length]

        elif signal_length < max_length:
            padding_begin_length = random.randint(0, max_length - signal_length)
            padding_end_length = max_length - signal_length - padding_begin_length

            padding_begin = torch.zeros((num_rows, padding_begin_length))
            padding_end = torch.zeros((num_rows, padding_end_length))

            signal = torch.cat((padding_begin, padding_end), 1)

        return signal, sample_rate

    def show_spectrogram(spec, ax=None, figsize=(14, 5)):
        # _, ax = plt.subplots(1, 1, figsize=figsize)
        # ax.imshow(spec)
        plt.specgram(spec, Fs=44100, cmap='rainbow')
        plt.xlabel('Time')
        plt.ylabel('Frequency')
        plt.show()

    @staticmethod
    def scale_minmax(X, min=0.0, max=1.0):
        X_std = (X - X.min()) / (X.max() - X.min())
        X_scaled = X_std * (max - min) + min
        return X_scaled

    @staticmethod
    def spectrogram_to_image(y, sr):
        # mels = librosa.feature.melspectrogram(y=y, sr= sr, n_mels=n_mels)
        # mels = librosa.amplitude_to_db(mels, ref=np.min)
        # print('Mel spectrogram is: ', y)
        mels = np.log(y + 1e-9)
        img = extract_spectrograms.scale_minmax(mels, 0, 255).astype(np.uint8)
        img = np.flip(img, axis=0)
        img = 255 - img
        # print('Img is: ', img, img.shape)
        # img = img[0]
        # skimage.io.imsave('/mnt/f/Code/Music_Dataset/Spectrograms/1.png', img)
        # print('Exiting.')
        # sys.exit(0)
        

        # print('Image created from spec: ', img)

        # return img

        # fig = Figure(figsize=(6.4, 4.8), dpi=100)
        # canvas = FigureCanvas(fig)
        # ax = fig.gca()
        # ax.axis('off')
        # librosa.display.specshow(y, sr=sr)
        # canvas.draw()
        # print('Figure attributes: ', fig.get_size_inches(), fig.get_dpi())
        # width, height = fig.get_size_inches() * fig.get_dpi()
        # img = np.frombuffer(canvas.tostring_rgb(), dtype='uint8')
        # print('Freshly extracted image: ', img)
        # print('Img shape: ', img.shape)
        # img = img.reshape(640, 480, 3)
        img = Image.fromarray(img)
        spec_image = img
        spec_image = spec_image.resize((224, 224))
        spec_image = np.array(spec_image)
        spec_image = np.stack((spec_image, spec_image, spec_image), axis=-1)
        resize = T.Resize((224, 224))
        img = resize(img)
        img = img_as_float(img)
        img = np.stack((img, img, img), axis=0)
        # print('Image after converting to 3 channels: ', img, img.shape)
        img = torch.from_numpy(img)
        # print('After converting to tensor, shape is: ', img, img.shape)
        # print('img shape: ', img.shape)
        # transform = T.Resize((224, 224))
        transform = T.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        # transform = T.Compose([T.ToTensor(), T.Normalize(mean=[0.485, 0.456, 0.406],
        #                          std=[0.229, 0.224, 0.225])])
        img = transform(img)
        # img = img / 255
        img = np.array(img)
        # print('Image after normalization: ', img)
        # print('Image transferred to test_data is :', img)
        # img = np.stack((img, img, img), axis=2)
        # print('Image shape is: ', img.shape)
        # plt.imshow(np.array(img).astype('uint8'))
        # print('Image data shape is: ', np.array(img).astype('uint8').shape)
        # plt.show()
        return img, spec_image

    def convert_to_spectrograms(self, file_path):

        counter = 0
        all_spectrograms = []
        all_file_names = []
        # print('Now converting to spectrograms.')

        # for file in self.files_list:
            # if counter == 10:
            #     break

            # samples, sample_rate = librosa.load(file)

            # print('Samples, sr: ', samples, sample_rate)

            # sgram = librosa.stft(samples)
            # sgram_mag, _ = librosa.magphase(sgram)
            # mel_scale = librosa.feature.melspectrogram(S=sgram_mag, sr=sample_rate)
            # mel_gram = librosa.amplitude_to_db(mel_scale, ref=np.min)

        signal, sample_rate = self.load_file(file_path)
        if signal is None or sample_rate is None:
            return None, None
        signal, sample_rate = self.resample_audio(signal, sample_rate)
        signal, sample_rate = self.standardize_channel(signal, sample_rate, 2)
        signal, sample_rate = self.resize(signal, sample_rate, 30000)
        top_db = 80
        mel_gram = transforms.MelSpectrogram(sample_rate, n_fft=1024, n_mels=128, win_length=None, hop_length=512, f_min=0.0, f_max=None, pad=0)(signal)
        # mel_gram = transforms.AmplitudeToDB(top_db=top_db)(mel_gram)

        augmented_gram1, augmented_gram2, augmented_gram3 = self.augment_spectrograms(mel_gram)
        all_spectrograms.append(np.asarray(mel_gram))
        all_spectrograms.append(np.asarray(augmented_gram1))
        all_spectrograms.append(np.asarray(augmented_gram2))
        all_spectrograms.append(np.asarray(augmented_gram3))

        spectrogram_images = []
        for i in range(4): # Since we have 4 different spectrograms for each audio file
            all_file_names.append(file_path)
            # spectrogram_images.append(extract_spectrograms.spectrogram_to_image(all_spectrograms[i], sample_rate))
            # self.save_spectrogram(augmented_gram1, sample_rate, self.output_dir, file, 'original')

            # counter += 1
        # print('Returning file names: ', all_file_names)
        # return spectrogram_images, all_file_names
        return all_spectrograms, all_file_names

    def save_spectrogram_array(self, file_path):
        # data = pd.DataFrame(columns=['spectrograms', 'songs'])
        # data.to_csv(file_path, sep='|', index=False)
        # counter = 0
        all_file_names = []
        if os.path.exists(file_path):
            os.remove(file_path)
        for i, file in enumerate(self.files_list):
            
            # if i == 10:
            #     break

            specs, files = self.convert_to_spectrograms(file)

            for i in range(len(specs)):
                specs[i] = np.asarray(specs[i])
            specs = np.asarray(specs)

            with open(file_path, 'ab') as arrayfile:
                np.save(arrayfile, specs)

            all_file_names.extend(files)


            # print(type(specs[0][0][0][0]))
            # new_df = pd.DataFrame({'spectrograms': specs, 'songs': files})
            # new_df['spectrograms'] = new_df[['spectrograms']].to_numpy()
            # print('dtypes: ', new_df.dtypes)
            # print('Newly created df is: ', new_df)
            # new_df.to_csv(file_path, mode='a', header=False, sep='|', index=False)
            # counter += 1

        # data.to_csv(file_path)
        df = pd.DataFrame(all_file_names)
        label_file_path = file_path.split('.')[0] + '.csv'
        df.to_csv(label_file_path, sep=',', header=False, index=False)
        print('Saved Data to csv.')
        # return pd.read_csv(file_path, sep='|')

    def fetch_spectrogram_data(self, file_path='/mnt/f/Code/Thesis/converted_spectrograms.npy', cached_data=True):
        if cached_data and os.path.exists(file_path):
            print('Getting cached data.')
            total_data = []
            # with open(file_path, 'rb') as data:
            #     d = np.load(data)
            #     total_data.append(d)
            #     d2 = np.load(data)
            #     if d == d2:
            #         print('They are same!')
            #     total_data.append(d2)
            # self.loaded_data = total_data
            
        elif cached_data and not os.path.exists(file_path):
            raise Exception(f'No cached data found at {file_path}. Please set cached_data=False.')
        else:
            print('Fetching data and caching data.')
            self.fetch_file_paths()
            # all_spectrograms, all_files = self.convert_to_spectrograms()        
            # data = self.save_spectrogram_array(file_path)
            self.save_spectrogram_array(file_path)
            data = self.fetch_spectrogram_data(cached_data=True)
            return data

    def show_spectrogram_data(self, file_path):
        with open(file_path, 'rb') as data:
            # reader = csv.reader(data, delimiter=',')
            # for d in reader:
            #     print(d)  
            d = np.load(data)
            print('Data loaded is: ', d)

def main():
    s = extract_spectrograms('/mnt/f/Code/Music_Dataset/fma_small/fma_small/')
    files = s.fetch_file_paths()
    save_spectrograms = '/mnt/f/Code/Thesis/converted_spectrograms.npy'
    all_spectrograms, all_file_names = s.convert_to_spectrograms(files[0])
    # data = s.save_spectrogram_array(save_spectrograms)
    # data = 
    # s.fetch_spectrogram_data(cached_data=True)
    # print(len(s.loaded_data), s.loaded_data[0].shape)
    # print(s.loaded_data)
    # data = s.fetch_spectrogram_data(save_spectrograms)
    # s.show_spectrogram_data(save_spectrograms)
    return s, all_spectrograms, all_file_names

if __name__ == '__main__':
    data = main()
    # main()
