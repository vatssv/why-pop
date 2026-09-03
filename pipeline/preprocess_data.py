from curses import meta
from statistics import mode
import pandas as pd
import numpy as np
import os
# import cv2
# from matplotlib.image import imread
from skimage import io, transform
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
from sklearn.utils import shuffle
from extract_spectrograms import extract_spectrograms

class Dataset(object):

    def __init__(self, spectrograms_path, file_metadata_path):
        self.input_data_path = spectrograms_path
        self.metadata_path = file_metadata_path

    def fetch_label_data(self, file_path):
        self.label_data = []
        label_df = pd.read_csv(file_path, header=None, index_col=None)
        file_names = label_df[0]

        self.metadata = pd.read_csv(self.metadata_path, skiprows=1, dtype=str, index_col=0)
        self.metadata = self.metadata.loc[:, ~self.metadata.columns.str.contains('^Unnamed')]

        for f in file_names:
            track_id = f.split('/')[-1]
            track_id = track_id.split('.')[0]
            track_id = int(track_id.lstrip('0'))
            self.label_data.append(self.metadata.loc[f'{track_id}', ['genre_top']])
        self.label_data = [i['genre_top'] for i in self.label_data]
        self.label_data = np.array(self.label_data)
        # print('Label data: ', self.label_data)

    def fetch_train_data(self):
        print('Fetching all data')
        self.train_data = []
        # track_to_img_map = {}
        # metadata.index = metadata.index.astype(dtype=float)
        # print('Metadata columns: ', metadata.columns)
        # print('Metadata: ', metadata)

        # print('Metadata columns and index', metadata.index, metadata.columns)
        # print('Track id: 2', metadata.loc[['2'], ['title.1']])
        # return
        # counter = 0
        # for root, dirs, files in os.walk(self.input_data_path):
        #     for file in files:
        #         # if counter == 10:
        #         #     break

        #         img = io.imread(f'{root}{file}')
        #         res = transform.resize(img, (128, 128))
        #         res = res[:, :, :3]
        #         file = file.split('_')[-1]
        #         track_id = file.lstrip('0').split('.')[0]
        #         track_to_img_map[file] = res
        #         self.train_data.append(res)
        #         # print('Current label is: ', metadata.loc[f'{track_id}', ['genre_top']])
        #         self.label_data.append(metadata.loc[f'{track_id}', ['genre_top']])

        #         # counter += 1

        # self.label_data = [i['genre_top'] for i in self.label_data]
        # self.label_data = np.array(self.label_data)
        s = extract_spectrograms('/mnt/f/Code/Music_Dataset/fma_small/fma_small/')
        all_data = s.fetch_spectrogram_data(cached_data=True)
        # print('Got data: ', all_data.head)
        # print('Columns: ', list(all_data.columns))
        
        self.train_data = np.asarray(all_data['spectrograms'])

        # print('Train and test data is: ', self.train_data, self.label_data)

    def process_data(self):
        self.train_data = np.array(self.train_data)
        mlb = LabelBinarizer()
        labels = mlb.fit_transform(self.label_data)
        self.label_data = labels

    def train_and_test_data(self):
        print(f'Before Splitting shape is {self.train_data.shape} and {self.label_data.shape}')
        (xtrain, xtest, ytrain,  ytest) = train_test_split(self.train_data, self.label_data, test_size=0.3, random_state=42)
        xtrain, ytrain = shuffle(xtrain, ytrain)
        xtest, ytest = shuffle(xtest, ytest)
        print(f'After splitting {xtrain.shape} and {ytrain.shape}')
        return (xtrain, ytrain, xtest, ytest)

def main():
    dt = Dataset('/mnt/f/Code/Music_Dataset/Spectrograms/', '/mnt/f/Code/Music_Dataset/fma_metadata/fma_metadata/tracks.csv')
    # dt.fetch_train_data()
    dt.fetch_label_data('/mnt/f/Code/Thesis/converted_spectrograms.csv')
    # print('Labels before processing are: ', dt.label_data)
    # dt.process_data()
    # (xtrain, ytrain, xtest, ytest) = dt.train_and_test_data()
    return dt #, xtrain, ytrain, xtest, ytest

if __name__ == '__main__':
    dt = main()