# Auto Image Downloader and Uploader to Cloudinary

This Python script downloads images from a list of URLs and automatically uploads them to Cloudinary. It utilizes asynchronous operations to efficiently download and upload multiple images concurrently.

## Features

- Downloads images asynchronously from a list of URLs.
- Uploads downloaded images to Cloudinary.
- Uses `aiohttp` for non-blocking HTTP requests and `aiofiles` for async file handling.
- Supports environment variable configuration via `.env` for secure API key management.
  
## Requirements

- Python 3.x
- Required Python packages:
  - `aiohttp`
  - `aiofiles`
  - `cloudinary`
  - `python-dotenv`
  - `tqdm` (optional for progress bar)

## Installation

   ```bash
   git clone this repo
   python -m venv venv
   source venv/bin/activate
   pip install aiohttp aiofiles cloudinary python-dotenv tqdm
   python autodownload_img.py
