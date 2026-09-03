# why-pop — Explaining a Music-Genre Classifier with Concepts

`why-pop` is the interactive visualization built for my master's thesis on
**explainable AI for music-genre classification**. A DenseNet CNN is trained to
classify audio (as mel-spectrograms) into genres, and the
[ACE (Automated Concept-based Explanation)](https://arxiv.org/abs/1902.03129)
method is used to discover the visual *concepts* the network relies on. This app
lets you explore those concepts per genre, see the tracks that exemplify them,
compare audio features, and listen to the songs.

📄 **Thesis:** https://hdl.handle.net/2286/R.2.N.171505

- **Frontend:** React (Create React App) + D3.js — served on `http://localhost:3000`
- **Backend:** Flask API — served on `http://localhost:5000`

> **Note on data.** This repository contains only the app and the small CSVs it
> needs to boot. The raw audio (~7 GB), spectrograms, trained model, and the
> ~27k concept images are **not** committed. To get a fully working app you
> either regenerate them with the [pipeline](#reproducing-everything-from-scratch)
> or drop your own generated `public/seventh_concepts/` in place. See
> [What's included vs. what you generate](#whats-included-vs-what-you-generate).

---

## Table of contents

1. [Architecture](#architecture)
2. [Quick start (running the app)](#quick-start-running-the-app)
3. [What's included vs. what you generate](#whats-included-vs-what-you-generate)
4. [Reproducing everything from scratch](#reproducing-everything-from-scratch)
5. [Backend configuration](#backend-configuration)
6. [Project layout](#project-layout)
7. [Troubleshooting](#troubleshooting)

---

## Architecture

```
                 ┌──────────────────────┐        proxy /api calls
  Browser  ────► │  React app  :3000    │ ─────────────────────────┐
                 │  (D3 charts, audio)  │                          │
                 └──────────────────────┘                          ▼
                                                        ┌──────────────────────┐
                                                        │  Flask API  :5000    │
                                                        │  server.py           │
                                                        └──────────┬───────────┘
                                                                   │ reads
                    ┌──────────────────────────────────────────────┼───────────────┐
                    ▼                        ▼                       ▼               ▼
             data/*.csv         public/seventh_concepts/     public/fma_small/  error_image.png
          (tracks, features)   (concept patches & results)      (MP3 audio)      (fallback)
```

The React app imports the small CSVs in `src/data/` directly (via `d3.csv`) for
its charts, and calls the Flask API for concept examples, track metadata, blended
concept images, and audio streaming.

---

## Quick start (running the app)

Prerequisites: **Node 16+** and **Python 3.8+**.

### 1. Backend (Flask)

```bash
cd flask-server
python -m venv venv
# Windows:  venv\Scripts\activate
# macOS/Linux:  source venv/bin/activate
pip install -r requirements.txt

# optional: copy and edit the env file if your data lives elsewhere
cp .env.example .env

python server.py          # serves on http://localhost:5000
```

### 2. Frontend (React)

In a second terminal, from the project root:

```bash
npm install
npm start                 # opens http://localhost:3000
```

The frontend proxies API requests to `http://localhost:5000` (configured via
`"proxy"` in `package.json`), so both must be running.

> ⚠️ On a fresh clone the app boots but concept examples / audio will be empty
> until you provide `public/seventh_concepts/` and the `fma_small` audio (next
> sections).

---

## What's included vs. what you generate

**✅ Committed to the repo (small, needed to boot):**

| Path | What it is |
|---|---|
| `src/`, `public/index.html`, `package.json` | The React app |
| `flask-server/server.py` | The Flask API |
| `src/data/features.csv` | Audio features for the radar chart |
| `src/data/concepts_data.csv` | Concept → TCAV score |
| `src/data/all_concept_clusters.csv` | Concept clusters (t-SNE) |
| `src/data/iris.csv` | Sample data for the parallel-coordinates demo |
| `data/features.csv`, `data/concepts_data.csv`, `data/all_concept_clusters.csv` | Backend copies |
| `public/error_image.png` | Fallback image |
| `pipeline/` | All scripts to regenerate everything |

**🚫 Not committed (large — you generate or download these):**

| Path | Size | How to get it |
|---|---|---|
| `public/fma_small/` | ~7 GB | Download the FMA dataset (below) |
| `public/seventh_concepts/` | several GB, ~27k files | Run the ACE pipeline (below) |
| `data/tracks.csv` | ~70 MB | Copy from FMA `fma_metadata/tracks.csv` |
| `data/all_concept_cavs.{csv,pkl}` | ~1.6 GB each | Intermediate ACE artifact (not needed at runtime) |
| `data/all_concept_cav_means.pkl` | ~40 MB | Intermediate ACE artifact |
| `pipeline/*.pth`, `*.h5`, `*.npy` | 80 MB+ | Trained model / cached spectrograms |

---

## Reproducing everything from scratch

The full research pipeline lives in [`pipeline/`](pipeline/). It takes the raw
FMA audio and produces the model, the discovered concepts, and every CSV the app
consumes.

> ℹ️ These are the original research scripts. They contain **hardcoded absolute
> paths** (written for WSL, e.g. `/mnt/f/Code/Music_Dataset/...`). Before running,
> open each script and update the paths near `main()` to match your machine.
> See [`pipeline/README.md`](pipeline/README.md) for the exact lines to edit.

### Step 0 — Download the FMA dataset

The project uses the **[Free Music Archive (FMA)](https://github.com/mdeff/fma)**
dataset by Defferrard et al.

- **Audio — `fma_small.zip`** (~7.2 GB): 8,000 30-second clips, 8 balanced genres
  → https://os.unil.cloud.switch.ch/fma/fma_small.zip
- **Metadata — `fma_metadata.zip`** (~342 MB): `tracks.csv`, `genres.csv`,
  `features.csv`, `echonest.csv`
  → https://os.unil.cloud.switch.ch/fma/fma_metadata.zip

(Both links and checksums are listed on the FMA repo README.) The 8 genres —
`Electronic, Experimental, Folk, Hip-Hop, Instrumental, International, Pop, Rock` —
are exactly the classes used throughout the pipeline.

Extract the audio so files sit at `.../fma_small/<xxx>/<track_id>.mp3`.

### Step 1 — Audio → mel-spectrograms

`pipeline/extract_spectrograms.py` loads each MP3, resamples to 44.1 kHz, builds a
128-mel spectrogram, applies SpecAugment (frequency/time masking), and caches the
arrays to `.npy` plus a `.csv` of file paths.

```bash
cd pipeline
python extract_spectrograms.py    # edit the fma_small/output paths in main() first
```

### Step 2 — Build the labeled dataset

`Dataset.py` + `preprocess_data.py` join the spectrograms with genre labels from
FMA `tracks.csv` and split train/test.

### Step 3 — Train the DenseNet classifier

`train_network.py` (model in `DenseNet_Model.py`) fine-tunes DenseNet on the
spectrograms and saves a checkpoint (e.g. `model_torch.pth`).

```bash
python train_network.py           # produces the trained model checkpoint
```

### Step 4 — Discover concepts with ACE

`ace_run.py` runs ACE for one class; `extract_concepts.py` loops over all 8
genres and moves each result into `concepts_<genre>/`.

```bash
python extract_concepts.py \
  --source_dir   /path/to/spectrogram_images \
  --working_dir  ./ACE \
  --model_to_run DenseNet \
  --model_path   ./model_torch.pth \
  --num_random_exp 20 --max_imgs 40 --min_imgs 40
```

Each `concepts_<genre>/` contains `concepts/`, `results/`, `cavs/`, `acts/`, and
`results_summaries/ace_results.txt`.

### Step 5 — Derive the app CSVs

- **`concepts_data.csv`** (concept → TCAV score): `python post_process_concepts.py`
- **`all_concept_clusters.csv` / `all_concept_cavs.*`** (t-SNE clustering of the
  CAV vectors): run `concept_similarity.ipynb` (or `extract_concepts.ipynb`).
- **`features.csv`** (per-track audio features): `song_features.py` extracts the 8
  Echonest audio features (`acousticness, danceability, energy, instrumentalness,
  liveness, speechiness, tempo, valence`) from FMA `echonest.csv`.
- **`tracks.csv`**: copy FMA `fma_metadata/tracks.csv` to `data/tracks.csv`.

### Step 6 — Wire the outputs into the app

```bash
# Concept images the API serves:
cp -r pipeline/concepts_*   public/seventh_concepts/
# (or set WHYPOP_CONCEPTS_SET to another folder name)

# Audio the API streams:
#   point WHYPOP_FMA_SMALL_DIR at your fma_small dir, or copy it to public/fma_small/

# App CSVs used by the backend and frontend:
cp data/features.csv data/concepts_data.csv data/all_concept_clusters.csv src/data/
```

Then run the app as in [Quick start](#quick-start-running-the-app).

---

## Backend configuration

`server.py` resolves all paths relative to the project root by default, so it
works after a fresh clone. Override any of these via environment variables (or a
`flask-server/.env` file — see `flask-server/.env.example`):

| Variable | Default | Purpose |
|---|---|---|
| `WHYPOP_DATA_DIR` | `<root>/data` | `tracks.csv`, `features.csv` |
| `WHYPOP_PUBLIC_DIR` | `<root>/public` | React public dir |
| `WHYPOP_CONCEPTS_SET` | `seventh_concepts` | Which concept run to serve (folder under `public/`) |
| `WHYPOP_FMA_SMALL_DIR` | `<public>/fma_small` | MP3 audio, laid out `<dir>/000/000123.mp3` |
| `WHYPOP_ERROR_IMAGE` | `<public>/error_image.png` | Fallback image |

### API endpoints

| Route | Description |
|---|---|
| `GET /<concept>` | Example result images for a concept (e.g. `Pop_concept3`) |
| `GET /meta/<track_ids>` | Track titles for `_`-joined track ids |
| `GET /features/<genre>/<num_samples>` | Audio features for selected + sampled tracks |
| `GET /fetchAvailableSongs/<genre>` | Tracks that have concept patches for a genre |
| `GET /one_song/<genre>_<track_id>` | Blended, annotated concept image for a track |
| `GET /fma_small/<song_dir>/<song_id>` | Streams an MP3 |

---

## Project layout

```
why-pop/
├── README.md                 ← you are here
├── package.json              ← React app + proxy to :5000
├── public/
│   ├── index.html
│   ├── error_image.png       ← committed fallback
│   ├── fma_small/            ← (gitignored) MP3 audio
│   └── seventh_concepts/     ← (gitignored) ACE concept outputs
├── src/
│   ├── App.js
│   ├── Components/           ← Panel, Concepts, Clusters, RadarChart, ImagePanel, …
│   └── data/                 ← small CSVs imported by the charts
├── data/                     ← backend CSVs (tracks.csv gitignored)
├── flask-server/
│   ├── server.py             ← Flask API (path-configurable)
│   ├── requirements.txt
│   └── .env.example
└── pipeline/                 ← full reproduction pipeline (see its README)
```

---

## Troubleshooting

- **App loads but concepts/audio are empty** — you haven't provided
  `public/seventh_concepts/` and/or the `fma_small` audio. See
  [What's included vs. what you generate](#whats-included-vs-what-you-generate).
- **`FileNotFoundError` for `tracks.csv`** — copy FMA `tracks.csv` to
  `data/tracks.csv` (it's gitignored due to size).
- **API calls fail / CORS** — make sure Flask is running on `:5000` and you
  started React with `npm start` (the proxy only applies in dev).
- **`OSError: cannot open resource` for `DejaVuSansMono.ttf`** (the `/one_song`
  route) — install the DejaVu fonts, or change the font in
  `server.py:annotate_image` to one available on your system.
- **Pipeline scripts fail on paths** — remember they use hardcoded absolute
  paths; edit them per [`pipeline/README.md`](pipeline/README.md).

---

## Credits

- **FMA dataset:** Defferrard, Benzi, Vandergheynst, Bresson —
  *FMA: A Dataset For Music Analysis* (ISMIR 2017),
  [github.com/mdeff/fma](https://github.com/mdeff/fma).
- **ACE:** Ghorbani, Wexler, Zou, Kim —
  *Towards Automatic Concept-based Explanations* (NeurIPS 2019).
