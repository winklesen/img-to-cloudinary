import os
import cloudinary
from dotenv import load_dotenv
import aiohttp
import aiofiles
import asyncio
from cloudinary.uploader import upload
from tqdm import tqdm

# Load environment variables from .env
load_dotenv()

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# List of image URLs to download
image_urls = [
    "https://m.media-amazon.com/images/M/MV5BOGUwMDk0Y2MtNjBlNi00NmRiLTk2MWYtMGMyMDlhYmI4ZDBjXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
    "https://m.media-amazon.com/images/M/MV5BMTkxNGFlNDktZmJkNC00MDdhLTg0MTEtZjZiYWI3MGE5NWIwXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
    "https://m.media-amazon.com/images/M/MV5BNWEwOTI0MmUtMGNmNy00ODViLTlkZDQtZTg1YmQ3MDgyNTUzXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
]

# Download directory
download_dir = "downloads"

async def download_image(session, url, filename):
    """Download an image asynchronously."""
    async with session.get(url) as response:
        if response.status == 200:
            file_path = f"{download_dir}/{filename}"
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(await response.read())
            return file_path
    return None

async def upload_to_cloudinary(file_path):
    """Upload image to Cloudinary."""
    try:
        response = upload(file_path)
        return response.get("secure_url")
    except Exception as e:
        print(f"Cloudinary upload failed for {file_path}: {e}")
        return None

async def main():
    """Main function to download and upload images."""
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    async with aiohttp.ClientSession() as session:
        # Download images asynchronously
        tasks = [download_image(session, url, f"image_{i}.jpg") for i, url in enumerate(image_urls)]
        downloaded_files = await asyncio.gather(*tasks)

        # Remove failed downloads
        downloaded_files = [file for file in downloaded_files if file]

        # Upload to Cloudinary
        upload_tasks = [upload_to_cloudinary(file) for file in downloaded_files]
        uploaded_urls = await asyncio.gather(*upload_tasks)

        # Print the uploaded URLs
        for url in uploaded_urls:
            if url:
                print(f"Uploaded to Cloudinary: {url}")

if __name__ == "__main__":
    asyncio.run(main())
