# LAZ to Raster Processing Scripts

This project contains two Python scripts for processing `.laz` (compressed LiDAR) point cloud files and converting them into raster (GeoTIFF) formats.

## 📜 Scripts

### 1. `laz2dsmints.py`
This script processes a folder of LAZ files to generate two types of rasters for each input file:
* **Digital Surface Model (DSM):** A raster where each pixel's value represents the **maximum elevation (Z value)** from the point cloud within that pixel's area.
* **Intensity Raster:** A raster where each pixel's value corresponds to the intensity reading of the *same point* that provided the maximum elevation for the DSM.

Empty pixels (gaps) in both rasters are filled using **linear interpolation**.

### 2. `laz2rgb_paralel.py`
This script processes user-selected LAZ files to generate a single **3-band (RGB) true-color orthoimage** for each input file.
* It uses **parallel processing** (`multiprocessing`) to convert multiple files simultaneously, significantly speeding up the workflow.
* It uses a **nearest neighbor** interpolation method to create the RGB raster from the point cloud's color values.

---

## 🔧 Requirements

### Python Libraries
You will need the following Python libraries to run these scripts:
* `laspy` (for reading LAZ files)
* `numpy` (for numerical operations)
* `rasterio` (for writing GeoTIFF files)
* `scipy` (for interpolation)
* `tqdm` (for progress bars)

The `multiprocessing` and `tkinter` modules are part of the Python standard library and **do not require separate installation** via `pip`. (Note: On some Linux systems, `tkinter` may need to be installed separately, e.g., `sudo apt-get install python3-tk`).

### `requirements.txt`
You can install all necessary packages using pip with the following `requirements.txt` file:

## 🚀 Installation

1.  **Clone** or download this repository.
2.  **Create** a virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install** the required packages:
    ```bash
    pip install -r requirements.txt
    ```

---

## 📂 Usage & Directory Structure

The scripts have hardcoded input and output paths. You must organize your folders as follows or modify the scripts to point to your data.

### 1. For `laz2dsmints.py`
This script reads from one folder and writes to two different output folders.

* **Input:** Place all your source `.laz` files in:
    ```
    ./folder_2_laz/
    ```
* **Output:** The script will automatically create and save the results in:
    * **DSM:** `./folder_2/derived_rasters/dsm/`
    * **Intensity:** `./folder_2/derived_rasters/intensity/`

* **To Run:**
    ```bash
    python laz2dsmints.py
    ```

### 2. For `laz2rgb_paralel.py`
This script will **prompt you with a file dialog** to select your input files. The output is saved to a hardcoded folder.

* **Input:** Run the script, and a window will pop up. Navigate to and select the `.laz` files you want to process.
* **Output:** The script will automatically create and save the RGB GeoTIFFs in:
    ```
    ./RGB_chunks/folder_2/
    ```

* **To Run:**
    ```bash
    python laz2rgb_paralel.py
    ```

---

## ⚙️ Configuration

You can modify parameters at the top of each script to fit your needs:

* **`resolution`:** Both scripts are set to `0.1` (e.g., 0.1 meters or 10cm pixels).
* **`crs_epsg`:** Both scripts are set to `"EPSG:28992"` (Amersfoort / RD New). Change this value if your data uses a different coordinate reference system.
* **File Paths:** You can change the `input_folder`, `output_base`, and `output_directory` variables in the scripts to match your own directory structure.
