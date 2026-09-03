from cv2 import dft
from torch.utils.data import DataLoader, Dataset, random_split
from extract_spectrograms import extract_spectrograms

class Audio_Dataset(Dataset):
    def __init__(self, df):
        self.df = df
        self.duration = 30000
        self.sr = 44100
        self.channel = 2
        
    def __len__(self):
        return len(self.df)

    def __getitem__(self, index):
        pass
