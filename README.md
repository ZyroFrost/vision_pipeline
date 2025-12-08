# 🧠 Vision Pipeline (Demo)
This repository contains a demo vision pipeline for downloading images from multiple sources, processing metadata, and preparing datasets for computer vision experiments.
The project is currently in an early experimental stage and serves as a sandbox for testing ingestion logic and simple preprocessing tools.

# 🚀 Key Features
## 1. 🖼️ Image Downloading (Unsplash / Pexels)
- Search images by keyword
- Batch downloading
- Metadata generation (id, URL, author, etc.)
- Automatic duplicate detection

## 2. 🧹 Preprocessing Tools
- CLIP similarity filtering (basic)
- Basic metadata validation
- API retry and failure handling

## 3. 🔧 Dataset Preparation
- Organizing downloaded images
- (Optional) train/val/test splitting
- Ready for future training pipelines

## 4. 🧪 Notebooks for Experimentation
- Testing training models

# 📂 Project Structure
```
vision_pipeline/
│
├── src/
│   ├── ingest/                    # Image ingestion modules
│   │   ├── pexels_downloader.py   # Main script download image from pexels
│   │   ├── unsplash_downloader.py # Main script download image from unsplash
│   │   ├── clip_filter.py         # CLIP-based filtering (basic)
│   │   ├── data_ingest.py         # Initialize project folder structure (raw, metadata, processed)
│   │   └── inspect_json.py        # Metadata inspection utilities
│   │
│   └── training/                  # (demo) training or dataset prep utilities
│
├── notebooks/                     # Experiments and testing
├── models/                        # Model checkpoints (if any)
│
├── .env                           # API keys (not included in Git)
├── .gitignore
└── README.md
```

# 🛠️ Installation
## 1. Create a virtual environment
```
python -m venv .venv
source .venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

## 2. Add your API keys
Create a .env file:
```
PEXELS_API_KEY=your_key_here
UNSPLASH_ACCESS_KEY=your_key_here
```

## 3. Run the ingestion pipeline
```
python src/ingest/data_ingest.py
```

# ❗ Notes
- This is not a production-ready pipeline — it's a working demo under active development.
- Some modules are placeholders or prototypes and will be improved over time.

# 📌 Planned Improvements
- Full ingestion → cleaning → annotation → training pipeline
- Better dataset overview & visualization tools
- More robust retry/backoff logic
- Model training integration
