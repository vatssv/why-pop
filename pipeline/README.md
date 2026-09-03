# Reproduction pipeline

These are the original research scripts that turn the raw **FMA** audio into the
trained model, the discovered **ACE** concepts, and the CSVs the `why-pop` app
consumes. They are provided so the project is self-contained and reproducible.

> ⚠️ **Heads-up: hardcoded paths.** These scripts were written for a specific WSL
> machine and contain absolute paths like `/mnt/f/Code/Music_Dataset/...`. They
> are **not** parameterized. Before running each script, edit the paths listed in
> [Paths you must edit](#paths-you-must-edit) to match your environment.

## Setup

```bash
python -m venv venv
# Windows:  venv\Scripts\activate
# macOS/Linux:  source venv/bin/activate
pip install -r requirements.txt
```

A CUDA-capable GPU is strongly recommended for Steps 2–3 (training + ACE).

## Order of execution

| # | Script | Input | Output |
|---|---|---|---|
| 0 | *(download FMA)* | — | `fma_small/` audio, `fma_metadata/` |
| 1 | `extract_spectrograms.py` | `fma_small/` MP3s | `converted_spectrograms.npy` (+ `.csv` of paths) |
| 2 | `preprocess_data.py`, `Dataset.py` | spectrograms + `tracks.csv` | labeled, split dataset |
| 3 | `train_network.py` (`DenseNet_Model.py`) | dataset | `model_torch.pth` |
| 4 | `extract_concepts.py` → `ace_run.py` (`ace.py`, `ace_helpers.py`) | spectrogram images + model | `concepts_<genre>/` |
| 5a | `post_process_concepts.py` | `concepts_<genre>/results_summaries/` | `data/concepts_data.csv` |
| 5b | `concept_similarity.ipynb` / `extract_concepts.ipynb` | CAVs | `all_concept_cavs.*`, `all_concept_clusters.csv` |
| 5c | `song_features.py` | FMA `echonest.csv` | `data/features.csv` |
| 6 | *(copy)* | `concepts_<genre>/` | `../public/seventh_concepts/` |

The 8 target genres throughout are:
`Electronic, Experimental, Folk, Hip-Hop, Instrumental, International, Pop, Rock`.

## Paths you must edit

| File | Line(s) | Currently points to | Change to |
|---|---|---|---|
| `extract_spectrograms.py` | ~334, ~336 | `.../fma_small/fma_small/`, `.../converted_spectrograms.npy` | your FMA audio dir / output `.npy` |
| `extract_spectrograms.py` | ~301 | default `file_path=.../converted_spectrograms.npy` | your cached `.npy` |
| `Dataset.py` | ~89–95 | `.../Music_dataset/Spectrograms/...` | your spectrogram-image output dir |
| `preprocess_data.py` | ~68, ~92, ~94 | fma_small dir, `Spectrograms/`, `fma_metadata/tracks.csv`, `converted_spectrograms.csv` | your paths |
| `train_network.py` | ~328, ~332 | fma_small dir, `fma_metadata/tracks.csv`, `model_torch_3.pth` | your paths / model output |
| `post_process_concepts.py` | ~8, ~28 | `Music_Dataset/`, `.../why-pop/data/concepts_data.csv` | your concepts root / this repo's `data/` |

The notebooks (`*.ipynb`) also contain absolute paths in their first cells —
update those before running.

## Notes

- Step 4 (`extract_concepts.py`) forwards CLI args to `ace_run.py`. Key args:
  `--source_dir` (spectrogram images), `--model_path` (your `.pth`),
  `--model_to_run`, `--bottlenecks`, `--num_random_exp`, `--max_imgs`,
  `--min_imgs`. `--model_to_run`/`--bottlenecks` must match the trained network.
- `ace.py` / `ace_helpers.py` are adapted from the reference
  [ACE implementation](https://github.com/amiratag/ACE) and depend on `tcav`.
- The generated `all_concept_cavs.{csv,pkl}` files are large (~1.6 GB) and are
  **intermediate** — the app does not read them, so they are gitignored.
