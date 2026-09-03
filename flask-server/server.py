from audioop import add
from io import StringIO
import mimetypes
import os
from flask import Flask, Response, send_file
import json
import pandas as pd
import numpy as np
import csv
import matplotlib.image as mpimg
import io
from PIL import Image, ImageDraw, ImageFont

# Optionally load a local .env file (see .env.example). No-op if python-dotenv
# is not installed.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Configuration
#
# All paths are resolved relative to the why-pop project root by default, so the
# app runs after a fresh `git clone` without editing source. Override any of
# them with environment variables (e.g. in a .env file) if your data lives
# elsewhere.
#
#   WHYPOP_DATA_DIR       -> app data CSVs (default: <project_root>/data)
#   WHYPOP_PUBLIC_DIR     -> React public dir (default: <project_root>/public)
#   WHYPOP_CONCEPTS_SET   -> which concept run to serve (default: seventh_concepts)
#   WHYPOP_FMA_SMALL_DIR  -> fma_small audio (default: <PUBLIC_DIR>/fma_small)
#   WHYPOP_ERROR_IMAGE    -> fallback image (default: <PUBLIC_DIR>/error_image.png)
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get('WHYPOP_DATA_DIR', os.path.join(PROJECT_ROOT, 'data'))
PUBLIC_DIR = os.environ.get('WHYPOP_PUBLIC_DIR', os.path.join(PROJECT_ROOT, 'public'))
CONCEPTS_SET = os.environ.get('WHYPOP_CONCEPTS_SET', 'seventh_concepts')
CONCEPTS_DIR = os.path.join(PUBLIC_DIR, CONCEPTS_SET)
FMA_SMALL_DIR = os.environ.get('WHYPOP_FMA_SMALL_DIR', os.path.join(PUBLIC_DIR, 'fma_small'))
ERROR_IMAGE_PATH = os.environ.get('WHYPOP_ERROR_IMAGE', os.path.join(PUBLIC_DIR, 'error_image.png'))

TRACKS_CSV = os.path.join(DATA_DIR, 'tracks.csv')
FEATURES_CSV = os.path.join(DATA_DIR, 'features.csv')

selected_songs = None
selected_genre = None
features_loaded = pd.DataFrame()

@app.route('/<concept>')
def concept_examples(concept):
    concept_genre = concept.split('_')[0]
    global selected_genre
    selected_genre = concept_genre
    base_concept_dir = os.path.join(CONCEPTS_DIR, f'concepts_{concept_genre}', 'results') + os.sep
    all_concept_examples = []
    for root, dirs, files in os.walk(base_concept_dir):
        for file in files:
            if concept+'.' in file:
                all_concept_examples.append(os.path.join(root, file))
    global selected_songs
    selected_songs = all_concept_examples
    res = json.dumps({"conceptExamples": all_concept_examples})
    # print('Selected songs before extracting features: ', selected_songs, selected_genre)
    # selected_songs_features(selected_songs, concept_genre)
    return res

@app.route('/meta/<tracks>')
def concept_examples_meta(tracks):
    track_ids = tracks.split('_')
    track_ids = track_ids[:-1]
    tracks_path = TRACKS_CSV
    # print('Tracks are: ', track_ids)
    # df_tracks = pd.read_csv(tracks_path, skiprows=1, usecols=['track_id', 'title'], error_bad_lines=False)
    # df_filtered = df_tracks[df_tracks['track_id'].isin(track_ids)]
    with open(tracks_path) as f:
        lines = []
        for line in csv.reader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, skipinitialspace=True):
            # print('Line is: ', line)
            cleaned = [l for l in line if not l=='']
            # print('Clean line is: ', cleaned, len(cleaned))
            if len(cleaned) > 0:
                track_id = cleaned[0]
                track_title = cleaned[-1]
            else:
                continue
            if track_id in track_ids:
                # print('Line is now: ', cleaned, len(cleaned))
                lines.append(track_id + ',' + track_title)
        text = "\n".join(lines)
    
    # print('Text was: ', text)
    df_filtered = pd.read_csv(StringIO(text), names=['track_id', 'track_title'])
    # print('Looking at track explicitly ', df_tracks.shape)
    # print('df filtered is: ', df_filtered)
    resp = json.dumps({'data': df_filtered.to_json(orient='records')})
    return resp

@app.route('/features/<genre>/<num_samples>')
def selected_songs_features(genre, num_samples):
    global features_loaded
    # if not features_loaded.empty:
    #     print('Features were already loaded.')
    #     return json.dumps({'data': features_loaded.to_json(orient='records')})
    # if selected_songs is None:
    #     print('There were no songs selected.')
    #     return json.dumps({'data': []})
    
    num_samples = int(num_samples)
    features_path = FEATURES_CSV
    tracks_path = TRACKS_CSV
    df_features = pd.read_csv(features_path)
    # print('Tracks are: ', track_ids)
    # df_tracks = pd.read_csv(tracks_path, skiprows=1, usecols=['track_id', 'title'], error_bad_lines=False)
    # df_filtered = df_tracks[df_tracks['track_id'].isin(track_ids)]
    with open(tracks_path) as f:
        lines = []
        hasheader = csv.Sniffer().has_header(f.read(1024))
        f.seek(0)
        for line in csv.reader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, skipinitialspace=True):
            if hasheader:
                hasheader = False
                continue
            # print('Line is: ', line)
            cleaned = [l for l in line if not l=='']
            # print('Clean line is: ', cleaned, len(cleaned))
            if len(cleaned) > 0:
                track_id = cleaned[0]
                track_title = cleaned[-1]
                try:
                    converted = int(track_id)
                    for col in cleaned:
                        if col in ['Electronic', 'Experimental', 'Folk', 'Hip-Hop', 'Instrumental', 'International', 'Pop', 'Rock']:
                            track_genre = col
                except (ValueError, IndexError):
                    # print('Found a bad line. Moving on.')
                    continue
            else:
                continue
            # if track_id in track_ids:
                # print('Line is now: ', cleaned, len(cleaned))
            lines.append(track_id + ',' + track_title + ',' + track_genre)
        text = "\n".join(lines)
    
    # print('Text was: ', text)
    df_tracks = pd.read_csv(StringIO(text), names=['track_id', 'track_title', 'genre_top'])
    df_tracks['track_id'] = pd.to_numeric(df_tracks['track_id'], errors='coerce')
    df_features['track_id'] = pd.to_numeric(df_features['track_id'], errors='coerce')
    # print('df_features is: ', df_features)
    # df_tracks = df_tracks.dropna(inplace=True)
    # print('First row: ', df_tracks.iloc[0])
    # print('df_tracks head ', df_tracks['track_id'])

    # print('Df tracks shape ', df_tracks.shape)
    # print('df features: ', df_features)
    selected_song_ids = []
    global selected_songs
    for song in selected_songs:
        song = song.split('/')[-1].split('.')[-2].split('_')[-1]
        selected_song_ids.append(int(song))

    df_features = df_features.merge(df_tracks, on='track_id', how='inner')
    # print('Df Features: ', df_features.head(), df_features.shape, df_features['track_id'].dtypes)
    # print('Selected song ids: ', selected_song_ids, type(selected_song_ids))
    # print('Explicitly selected: ', df_features.loc[[2, 3], :])
    # df_features['track_id'] = df_features['track_id'].astype(np.int64)
    df_subset = df_features[df_features['track_id'].isin(selected_song_ids)]

    # print('Selected song ids and df_subset ', len(selected_song_ids), df_subset.shape, len(df_subset))
    # print('df features after merge: ', df_features)

    additional_songs_needed = num_samples - len(df_subset)
    # print('Additional songs needed: ', additional_songs_needed)
    if additional_songs_needed:
        global selected_genre
        dataframe_query = df_features.query(f"genre_top == '{genre}'")
        print('Query returned ', dataframe_query.shape)
        print('Genre selected was: ', genre)
        additional_songs = dataframe_query.sample(n=additional_songs_needed)
        # print('Additional songs fetched: ', additional_songs)
        df_subset = pd.concat([df_subset, additional_songs], axis=0)
    # print('Finally ', df_subset.head(), len(df_subset))
        
    # features_loaded = df_subset
    df_subset.drop(['genre_top'], axis=1, inplace=True)
    res = json.dumps({'data': df_subset.to_json(orient='records')})
    print('response for features was: ', res)
    return res

@app.route('/fma_small/<song_dir>/<song_id>')
def stream_song(song_dir, song_id):
    def generate():
        song_path = os.path.join(FMA_SMALL_DIR, song_dir, song_id + '.mp3')
        with open(song_path, 'rb') as file:
            data = file.read(1024)
            while data:
                yield data
                data = file.read(1024)
    return Response(generate(), mimetype='audio/mpeg')

@app.route('/fetchAvailableSongs/<genre>')
def fetchAvailableSongs(genre):
    base_dir = os.path.join(CONCEPTS_DIR, f'concepts_{genre}', 'concepts') + os.sep
    available_songs_ids = set()
    for root, dirs, files in os.walk(base_dir):
        if 'patches' in root:
            for file in files:
                track_id = file.split('_')[-1].split('.')[0]
                available_songs_ids.add(track_id)

    tracks_path = TRACKS_CSV
    with open(tracks_path) as f:
        lines = []
        for line in csv.reader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, skipinitialspace=True):
            cleaned = [l for l in line if not l=='']
            if len(cleaned) > 0:
                track_id = cleaned[0]
                track_title = cleaned[-1]
            else:
                continue
            if track_id in available_songs_ids:
                lines.append(track_id + ',' + track_title)
        text = "\n".join(lines)
    
    # print('Text was: ', text)
    df_filtered = pd.read_csv(StringIO(text), names=['track_id', 'track_title'])
    res = json.dumps({'data': df_filtered.to_json(orient='records')})
    return res

@app.route('/one_song/<track_id>')
def blended_images(track_id):
    # print('Passed track id: ', track_id)
    genre, track_id = track_id.split('_')
    # print('Genre, track_id: ', genre, track_id)
    images_to_blend = []
    base_dir = os.path.join(CONCEPTS_DIR, f'concepts_{genre}', 'concepts') + os.sep
    for root, dirs, files in os.walk(base_dir):
        # print('Root, dirs, files: ', root, dirs, files)
        if 'patches' in root and genre in root:
            # print('Looking at ', root)
            for file in files:
                # print('Looking at file: ', file)
                id = file.split('_')[2]
                # print('Id looking for vs from file is: ', track_id, id)
                if track_id in id:
                    # print('Found a file.')
                    images_to_blend.append(root + '/' + file)

    # actual_images = []
    # for img in images_to_blend:
    #     actual_images.append(mpimg.imread(img))

    # weight = 1 / len(actual_images)
    # output = np.zeros_like(actual_images[0])

    # print('Images to blend: ', images_to_blend)
    try:
        output = images_to_blend[0]
    except IndexError:
        return send_file(ERROR_IMAGE_PATH, mimetype='image/PNG')
    # print('First image: ', output, type(output))
    # font = ImageFont.truetype('DejaVuSansMono.ttf', 8)
    annotation_positions = {}
    for i in range(0, len(images_to_blend) - 1):
        concept_1 = images_to_blend[i].split('/')[-2].split('_')[1:3]
        concept_1 = '_'.join(concept_1)
        concept_2 = images_to_blend[i+1].split('/')[-2].split('_')[1:3]
        concept_2 = '_'.join(concept_2)
        output, concept_1_text, concept_2_text = blend_two_images(output, images_to_blend[i+1])

        if concept_1 not in annotation_positions:
            annotation_positions[concept_1] = concept_1_text

        if concept_2 not in annotation_positions:
            annotation_positions[concept_2] = concept_2_text

        # print('Concept 1 and 2 text starts: ', concept_1_text, concept_2_text)

        # output = Image.fromarray(output, 'L')
        # i_text = ImageDraw.Draw(output)
        # i_text.text(concept_1_text, concept_1, fill=0, font=font)
        # i_text.text(concept_2_text, concept_2, fill=0, font=font)
        # output = np.array(output.convert('L'))

    res = None
    for i, (text, pos) in enumerate(annotation_positions.items()):
        # print('Inputs to annotate image: ', type(output), output.shape, text, pos)
        if i == 0:
            res = annotate_image(output, pos, text)
        else:
            res = annotate_image(res, pos, text)

    output = Image.fromarray(res, 'L')
    file_object = io.BytesIO()
    output.save(file_object, 'PNG')
    file_object.seek(0)

    return send_file(file_object, mimetype='image/PNG')

def annotate_image(img, pos, text):
    img = Image.fromarray(img, 'L')
    font = ImageFont.truetype('DejaVuSansMono.ttf', 8)
    i_text = ImageDraw.Draw(img)
    i_text.text(pos, text, fill=0, font=font)
    return np.uint8(img)


def blend_two_images(img1, img2):

    if isinstance(img1, str):
        img1 = np.asarray(Image.open(img1).convert('L'))
    elif isinstance(img1, np.ndarray):
        pass
    else:
        raise ValueError('Invalid image format for image 1.')

    if isinstance(img2, str):
        img2 = np.asarray(Image.open(img2).convert('L'))
    elif isinstance(img2, np.ndarray):
        pass
    else:
        raise ValueError('Invalid image format for image 2.')

    res = np.full(img1.shape, 117)

    concept_1_start_pos, concept_2_start_pos = (-1, -1), (-1, -1)

    for i in range(0, len(img1)):
        for j in range(0, len(img1[0])):
            img1_pixel = abs(img1[i,j] - 117)
            img2_pixel = abs(img2[i,j] - 117)

            # print('Current pixels', img1_pixel, img2_pixel)

            # if img1_pixel == 0:
            #     res[i][j] = img1_pixel
            # elif img2_pixel == 0:
            #     res[i][j] = img2_pixel
            if img1_pixel > img2_pixel and img1_pixel > 10:
                res[i][j] = img1[i,j]
                if concept_1_start_pos == (-1, -1):
                    concept_1_start_pos = (i, j)
            elif img2_pixel > img1_pixel and img2_pixel > 10:
                res[i][j] = img2[i][j]
                if concept_2_start_pos == (-1, -1):
                    concept_2_start_pos = (i, j)
            else:
                res[i][j] = 117

    # print('Output: ', res)
    return np.uint8(res), concept_1_start_pos, concept_2_start_pos


if __name__ == '__main__':
    app.run(debug=True)