import os
import cloudinary
from dotenv import load_dotenv
import aiohttp
import aiofiles
import asyncio
from cloudinary.uploader import upload
from tqdm import tqdm
import cairosvg
import re

# Load environment variables from .env
load_dotenv()

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Function to convert filenames to snake_case
def to_snake_case(filename):
    return re.sub(r'[^a-z0-9]+', '_', filename.lower()).strip('_')

# Recursive function to get all SVG files in a directory and its subfolders, skipping files with prefix '._'
def get_svg_files(directory):
    svg_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".svg") and not file.startswith("._"):  # Skip files with prefix '._'
                svg_files.append(os.path.join(root, file))
    return svg_files

# Convert SVG to PNG using cairosvg
def convert_svg_to_png(svg_path, output_path):
    try:
        cairosvg.svg2png(url=svg_path, write_to=output_path)
        return output_path
    except Exception as e:
        print(f"Error converting {svg_path} to PNG: {e}")
        return None

async def upload_to_cloudinary(file_path, progress_bar):
    """Upload image to Cloudinary and update progress bar."""
    try:
        response = upload(file_path)
        progress_bar.update(1)  # Update progress bar after each successful upload
        return response.get("secure_url")
    except Exception as e:
        print(f"Cloudinary upload failed for {file_path}: {e}")
        return None

async def main():
    """Main function to convert and upload SVG files."""
    # Path to the 'army map' folder
    directory = os.path.join(os.getcwd(), "army map")  # Adjusted for your directory structure
    output_dir = os.path.join(directory, "converted_images")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get all SVG files in the 'army map' directory and subdirectories
    svg_files = get_svg_files(directory)

    if not svg_files:
        print("No SVG files found.")
        return

    # Convert SVG files to PNG
    converted_files = []
    for svg_file in tqdm(svg_files, desc="Converting SVG to PNG"):
        # Replicate the directory structure in the output folder
        relative_path = os.path.relpath(svg_file, directory)  # Get relative path to the army map folder
        output_folder = os.path.join(output_dir, os.path.dirname(relative_path))  # Create same folder structure
        os.makedirs(output_folder, exist_ok=True)

        # Convert filename to snake_case and change extension to PNG
        filename = to_snake_case(os.path.basename(svg_file)).replace(".svg", ".png")
        output_path = os.path.join(output_folder, filename)

        # Convert the SVG to PNG
        png_file = convert_svg_to_png(svg_file, output_path)
        if png_file:
            converted_files.append(png_file)

    # Set up the progress bar for uploads
    progress_bar = tqdm(total=len(converted_files), desc="Uploading to Cloudinary", unit="file")

    # Open the output text file to save the results
    output_file_path = os.path.join(os.getcwd(), "cloudinary_uploads.txt")
    with open(output_file_path, "w") as f:
        # Write the header to the file
        f.write(f"{'Filename':<35} | {'Cloudinary URL'}\n")
        f.write('-' * 75 + "\n")

        # Upload to Cloudinary and list the files
        async with aiohttp.ClientSession() as session:
            upload_tasks = [upload_to_cloudinary(file, progress_bar) for file in converted_files]
            uploaded_urls = await asyncio.gather(*upload_tasks)

            # Write each file's filename and Cloudinary URL to the text file
            for file_path, url in zip(converted_files, uploaded_urls):
                if url:
                    f.write(f"{os.path.basename(file_path):<35} | {url}\n")

    # Close the progress bar
    progress_bar.close()

    print(f"Upload results saved to: {output_file_path}")

if __name__ == "__main__":
    asyncio.run(main())
