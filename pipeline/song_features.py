import pandas as pd

def save_song_features(feature_file_path, save_location):
    df = pd.read_csv(feature_file_path)
    df = df.set_index('track_id')
    df = df.iloc[:, :8]
    df.to_csv(save_location)