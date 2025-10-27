import laspy
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from scipy.interpolate import griddata
import tkinter.filedialog as fd
import os
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import time

# Function to process a single LAZ file and save the RGB orthoimage
def process_file(file):
    try:
        # Load the LAZ file
        las = laspy.read(file)

        # Extract XYZ and RGB values
        x, y = las.x, las.y
        r = las.red.astype(np.uint8)
        g = las.green.astype(np.uint8)
        b = las.blue.astype(np.uint8)

        resolution = 0.1

        # Compute grid extent
        x_min, x_max = np.min(x), np.max(x)
        y_min, y_max = np.min(y), np.max(y)

        # Generate grid coordinates
        x_grid = np.arange(x_min, x_max, resolution)
        y_grid = np.arange(y_min, y_max, resolution)
        xx, yy = np.meshgrid(x_grid, y_grid)

        # Interpolate RGB values onto the grid
        r_interp = griddata((x, y), r, (xx, yy), method="nearest")
        g_interp = griddata((x, y), g, (xx, yy), method="nearest")
        b_interp = griddata((x, y), b, (xx, yy), method="nearest")

        # Stack RGB channels
        rgb_image = np.stack([r_interp, g_interp, b_interp], axis=0).astype(np.uint8)

        # Define GeoTIFF transformation
        transform = from_bounds(x_min, y_max, x_max, y_min, rgb_image.shape[2], rgb_image.shape[1])
        output_path = os.path.join(output_directory, f"{file.split('/')[-1].split('.')[0]}.tif")

        # Save as GeoTIFF
        with rasterio.open(
            output_path,
            "w",
            driver="GTiff",
            height=rgb_image.shape[1],
            width=rgb_image.shape[2],
            count=3,  # 3 bands (R, G, B)
            dtype=rgb_image.dtype,
            crs="EPSG:28992",  # Set appropriate CRS (e.g., Amersfoort / RD New)
            transform=transform,
        ) as dst:
            dst.write(rgb_image)

        print(f"RGB orthoimage saved as {output_path}")
        return True

    except Exception as e:
        print(f"Error processing file {file}: {e}")
        return False

# Function to process files in parallel
def process_files_parallel(file_paths):
    results = {}
    start_time = time.time()  # Start timer for the entire pool
    global_timeout = 36000  # Global timeout for the entire pool (e.g., 1 hour)

    with Pool(processes=cpu_count()) as pool:
        try:
            # Use imap_unordered for parallel processing
            for result in tqdm(pool.imap_unordered(process_file, file_paths), total=len(file_paths), desc="Processing files"):
                # Check if the global timeout has been reached
                if time.time() - start_time > global_timeout:
                    print("Global timeout reached. Stopping processing.")
                    break

                if result is not None:
                    results[file_paths] = result

        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            # Ensure the pool is terminated
            pool.terminate()
            pool.join()

# Main script
def main(files):
    try:
        # Process files in parallel
        process_files_parallel(files)

    except Exception as e:
        print(f"An error occurred in the main script: {e}")

# Run the script
if __name__ == "__main__":
    files = fd.askopenfilenames()
    output_directory = "./RGB_chunks/folder_2"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    main(files)