import os
import laspy
import numpy as np
import rasterio
from rasterio.transform import from_origin
from tqdm import tqdm
from scipy.interpolate import griddata


# Input folder (LAZ files)
input_folder = "./folder_2_laz"

# Output folders
output_base = "./folder_2/derived_rasters"
dsm_folder = os.path.join(output_base, "dsm")
intensity_folder = os.path.join(output_base, "intensity")

# Klasörleri oluştur
os.makedirs(dsm_folder, exist_ok=True)
os.makedirs(intensity_folder, exist_ok=True)

# Parametreler
resolution = 0.1
crs_epsg = "EPSG:28992"  # Gerekirse değiştir

# Loop through each LAZ file
for filename in tqdm(os.listdir(input_folder)):
    if not filename.endswith('.laz'):
        continue

    laz_path = os.path.join(input_folder, filename)
    las = laspy.read(laz_path)

    x, y = las.x, las.y
    z = las.z
    intensity = las.intensity

    # Grid bounds
    min_x, max_x = np.floor(np.min(x)), np.ceil(np.max(x))
    min_y, max_y = np.floor(np.min(y)), np.ceil(np.max(y))

    n_cols = int(np.floor((max_x - min_x) / resolution)) + 1
    n_rows = int(np.floor((max_y - min_y) / resolution)) + 1

    col = ((x - min_x) / resolution).astype(int)
    row = ((max_y - y) / resolution).astype(int)

    # Initialize grids
    dsm_grid = np.full((n_rows, n_cols), np.nan, dtype=np.float32)
    intensity_grid = np.full((n_rows, n_cols), np.nan, dtype=np.float32)

    # Fill known values (max Z per cell)
    for r, c, z_val, i_val in zip(row, col, z, intensity):
        if 0 <= r < n_rows and 0 <= c < n_cols:
            if np.isnan(dsm_grid[r, c]) or z_val > dsm_grid[r, c]:
                dsm_grid[r, c] = z_val
                intensity_grid[r, c] = i_val

    # Meshgrid for interpolation
    xx, yy = np.meshgrid(
        np.arange(n_cols) * resolution + min_x,
        max_y - np.arange(n_rows) * resolution
    )

    # Interpolate NaNs (DSM)
    known_mask = ~np.isnan(dsm_grid)
    if np.any(known_mask):
        known_points = np.vstack((xx[known_mask], yy[known_mask])).T
        known_values = dsm_grid[known_mask]
        nan_mask = np.isnan(dsm_grid)
        nan_points = np.vstack((xx[nan_mask], yy[nan_mask])).T
        dsm_interp = griddata(known_points, known_values, nan_points, method='linear')
        dsm_grid[nan_mask] = dsm_interp

    # Interpolate NaNs (intensity)
    known_mask_i = ~np.isnan(intensity_grid)
    if np.any(known_mask_i):
        known_points_i = np.vstack((xx[known_mask_i], yy[known_mask_i])).T
        known_values_i = intensity_grid[known_mask_i]
        nan_mask_i = np.isnan(intensity_grid)
        nan_points_i = np.vstack((xx[nan_mask_i], yy[nan_mask_i])).T
        intensity_interp = griddata(known_points_i, known_values_i, nan_points_i, method='linear')
        intensity_grid[nan_mask_i] = intensity_interp

    # Raster transform
    transform = from_origin(min_x, max_y, resolution, resolution)

    # Output filenames
    name = os.path.splitext(filename)[0]
    dsm_output = os.path.join(dsm_folder, f"{name}_dsm.tif")
    intensity_output = os.path.join(intensity_folder, f"{name}_intensity.tif")

    # Save DSM
    with rasterio.open(
        dsm_output,
        'w',
        driver='GTiff',
        height=dsm_grid.shape[0],
        width=dsm_grid.shape[1],
        count=1,
        dtype='float32',
        crs=crs_epsg,
        transform=transform,
        nodata=np.nan
    ) as dst:
        dst.write(dsm_grid, 1)

    # Save intensity
    with rasterio.open(
        intensity_output,
        'w',
        driver='GTiff',
        height=intensity_grid.shape[0],
        width=intensity_grid.shape[1],
        count=1,
        dtype='float32',
        crs=crs_epsg,
        transform=transform,
        nodata=np.nan
    ) as dst:
        dst.write(intensity_grid, 1)