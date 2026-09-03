from cmath import nan
import math
import stat
from torch.utils.data import DataLoader, Dataset, random_split
import torchaudio
from extract_spectrograms import extract_spectrograms
import pandas as pd
import numpy as np
from PIL import Image
import os

class AudioDataset(Dataset):
    def __init__(self, data_path, metadata_path):
        self.data_path = str(data_path)
        self.sr = 44100
        self.channel = 2
        self.preprocess = extract_spectrograms(self.data_path)
        self.df = pd.DataFrame(self.preprocess.fetch_file_paths(), columns=['songs'])
        # self.df = pd.concat([song_df]*4, ignore_index= True)
        self.metadata = pd.read_csv(metadata_path, skiprows=1, dtype=str, index_col=0)
        self.metadata = self.metadata.loc[:, ~self.metadata.columns.str.contains('^Unnamed')]
        self.df['label'] = self.df.apply(lambda row: self.track_id_to_label(self.get_track_id(row.songs)), axis=1)
        # self.df = self.df.dropna(axis=0, how='all')
        print('Length of df is: ', len(self.df))
        self.df = self.df[self.df['label'].notna()]
        print('Length of df is: ', len(self.df))
        # label_df = pd.read_csv(label_path, names=['label'])
        # print('dfs are: ', song_df.shape, label_df.shape)
        # self.df = pd.concat([song_df, label_df], axis=1)
        # print('Song df is: ', song_df)
        # print('Na values are: ', self.df[self.df['songs'].isna()])
        # print('df is: ', self.df.loc[6083:,['label']])
        # print('Index is: ', self.df.index)
    
    @staticmethod
    def fetch_labels():
        return ['Electronic', 'Experimental', 'Folk', 'Hip-Hop', 'Instrumental', 'International', 'Pop', 'Rock']

    def get_track_id(self, path):
        song_id = path.split('/')[-1].split('.')[0].lstrip('0')
        # print('Path and song_id are: ', path, song_id)
        # label = self.metadata.loc[f'{song_id}', ['genre_top']]['genre_top']
        return song_id

    def track_id_to_label(self, track_id):
        return self.metadata.loc[f'{track_id}', ['genre_top']]['genre_top']

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        spec_images, labels = [], []
        try:
            audio_path = self.df.loc[idx, 'songs']
            # song_id = audio_path.split('/')[-1].split('.')[0].lstrip('0')
            # print('Song id is: ', song_id)
            # print('Metadata: ', self.metadata)
            # label = self.metadata.loc[f'{song_id}', ['genre_top']]['genre_top']
            # print('Type and value: ', type(label), label['genre_top'])
            # label = [i['genre_top'] for i in label]
            label = self.df.loc[idx, 'label']
            # print('Label is: ', label, type(label))
            if not(isinstance(label, str)) and math.isnan(label):
                print('Label is actually nan.')
                print('The audio path and index were: ', audio_path, idx, self.df.loc[idx])
                return None
            # label = [label for i in range(4)]
            for i in range(4):
                labels.append(label)

            # print('Working on audio_path: ', audio_path)

            specs, _ = self.preprocess.convert_to_spectrograms(audio_path)

            if specs is None:
                return None

            # spec_images = []
            for i, s in enumerate(specs):
                spec, original_spec = self.preprocess.spectrogram_to_image(s[0], sr=self.sr)
                # print('Original spec: ', original_spec, original_spec.shape)
                # reshaped_image = spec.swapaxes(0, 2)
                # reshaped_image = np.rollaxis(spec, 2)
                # reshaped_image = np.rollaxis(reshaped_image, 2)
                # print('Spec array shape: ', reshaped_image.shape)
                # print('Image data is: ', original_spec)
                im = Image.fromarray((original_spec * 255).astype(np.uint8))
                # print('Image shape is: ', spec.shape)
                if not os.path.exists(f'/mnt/f/Code/Music_dataset/Spectrograms/{label}'):
                    os.makedirs(f'/mnt/f/Code/Music_dataset/Spectrograms/{label}')
                # im.save(f'/mnt/f/Code/Music_dataset/Spectrograms/{label}/{self.get_track_id(audio_path)}_{i+1}.png')
                spec_images.append(spec)
                # im = Image.fromarray((spec * 255).astype(np.uint8))

                im.save(f'/mnt/f/Code/Music_dataset/Spectrograms/{label}/{self.get_track_id(audio_path)}_{i+1}.png')
            # print('Returning one data item: ', len(specs), spec_images[0].shape, labels)
            return spec_images, labels
        except KeyError:
            print('Key error caught, moving on.')
            return None
