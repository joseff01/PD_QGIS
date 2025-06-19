import os
import pandas as pd
import rasterio
from rasterio.transform import rowcol
from rasterio.transform import Affine
import geopandas as gpd
from shapely.geometry import box

def import_geospatial_data(image_path: str, coord_path: str):
    """
    Imports a geospatial image and its corresponding coordinate data.
    The corresponding files must have the same name, with different extension
    
    The module first searches for images, and then tries to match the images name to 
    one of the csv files. It will return the error msg
    
    Args:
        image_path (str): Path to a .tif image or a folder containing .tif images.
        coord_path (str): Path to a .csv file or a folder containing .csv files.

    Returns:
        Tuple[List[str], List[str]]: 
            - List of image file paths.
            - List of corresponding coordinate CSV file paths.
        or str if there is an error (to be handled externally by the gui).
    """
    
    if not os.path.exists(image_path):
        return f"Image path not found: {image_path}"
    if not os.path.exists(coord_path):
        return f"Coordinate path not found: {coord_path}"

    # Collect image files
    if os.path.isdir(image_path): #If it's a path to a directory
        image_files = sorted([f for f in os.listdir(image_path) if f.lower().endswith('.tif')])
        image_files_full = [os.path.join(image_path, f) for f in image_files] #Get all paths to the images in an array
    elif image_path.lower().endswith('.tif'): #If it's a path to a single .tif file
        image_files = [os.path.basename(image_path)] 
        image_files_full = [image_path]
    else:
        return "Image path must be a .tif file or a folder containing .tif files."

    # Collect CSV files
    if os.path.isdir(coord_path):
        coord_files = sorted([f for f in os.listdir(coord_path) if f.lower().endswith('.csv')])
        coord_files_full = [os.path.join(coord_path, f) for f in coord_files]
    elif coord_path.lower().endswith('.csv'):
        coord_files_full = [coord_path]
    else:
        return "Coordinate path must be a .csv file or a folder containing .csv files."
    
    matched_images = []
    matched_csvs = []
    # Match image and CSV files by name
    for img_full in image_files_full:
        base_name = os.path.splitext(os.path.basename(img_full))[0]
        matching_csv = [csv for csv in coord_files_full if os.path.splitext(os.path.basename(csv))[0] == base_name]
        if matching_csv:
            matched_images.append(img_full)
            matched_csvs.append(matching_csv[0])
        else:
            return f"No matching CSV found for image: {base_name}"

    return matched_images, matched_csvs

"""
test_import = import_geospatial_data(
    "C:/Users/Joseff01/Documents/Git/PDJoseRetanaQGIS/Images/",
    "C:/Users/Joseff01/Documents/Git/PDJoseRetanaQGIS/Box_Coordinates/"
)

print(test_import)
"""

def preprocess_coordinates(image_paths, csv_paths):
    """
    Preprocesses bounding box coordinates from CSVs and maps them to georeferenced coordinates using TIF metadata.

    Args:
        image_paths: List of paths to .tif georeferenced images.
        csv_paths: List of paths to corresponding .csv files with bounding box coordinates.

    Returns:
        A tuple containing:
            - A list of lists of ((x1, y1), (x2, y2)) georeferenced bounding box corners per image.
            - A list of CRS strings for each image.
            - A list of error messages encountered during processing.
    """
    all_bboxes_per_image = []
    crs_list = []
    errors = []

    for img_path, csv_path in zip(image_paths, csv_paths):
        image_bboxes = []

        try:
            df = pd.read_csv(csv_path)
            required_cols = {'left', 'top', 'right', 'bottom'}
            if not required_cols.issubset(df.columns):
                errors.append(f"❌ Missing one of the required columns {required_cols} in {csv_path}")
                all_bboxes_per_image.append([])
                crs_list.append(None)
                continue

            bbox_pixel_coords = list(zip(df['left'], df['top'], df['right'], df['bottom']))

            with rasterio.open(img_path) as dataset:
                transform = dataset.transform
                crs = dataset.crs.to_string()
                crs_list.append(crs)

                for left, top, right, bottom in bbox_pixel_coords:
                    top_left = transform * (left, top)
                    bottom_right = transform * (right, bottom)
                    image_bboxes.append((top_left, bottom_right))

        except Exception as e:
            errors.append(f"❌ Error processing {img_path} and {csv_path}: {e}")
            image_bboxes = []
            crs_list.append(None)

        all_bboxes_per_image.append(image_bboxes)

    return all_bboxes_per_image, crs_list, errors

"""
test_preproces = preprocess_coordinates(test_import[0],test_import[1])
"""


def create_georeferenced_rectangles(bbox_coords_per_image, crs_list, image_paths, output_folder):
    """
    Creates georeferenced rectangles from grouped bounding box coordinates and saves a shapefile per image.

    Args:
        bbox_coords_per_image: List of lists of ((x1, y1), (x2, y2)) tuples.
        crs_list: List of CRS strings corresponding to each image's bounding boxes.
        output_folder: Path to the folder where the shapefiles will be saved.

    Returns:
        List of messages indicating success or failure for each image.
    """
    if not os.path.isdir(output_folder):
        return [f"❌ Output folder does not exist: {output_folder}"]

    messages = []

    for idx, (bbox_coords, crs, img_path) in enumerate(zip(bbox_coords_per_image, crs_list, image_paths)):
        
        geometries = []

        for i, ((x1, y1), (x2, y2)) in enumerate(bbox_coords):
            try:
                minx, maxx = sorted([x1, x2])
                miny, maxy = sorted([y1, y2])
                geom = box(minx, miny, maxx, maxy)
                geometries.append(geom)
            except Exception as e:
                print(f"⚠️ Error with rectangle {i} in image {idx}: {e}")

        if not geometries:
            messages.append(f"⚠️ No valid rectangles for image {idx}, skipping.")
            continue

        try:
            gdf = gpd.GeoDataFrame(geometry=geometries)
            if crs:
                gdf.set_crs(crs, inplace=True, allow_override=True)
            else:
                gdf.set_crs(epsg=4326, inplace=True)  #  In caso of no CRS

            base_name = os.path.splitext(os.path.basename(img_path))[0]
            output_path = os.path.join(output_folder, f"{base_name}_rectangles.shp")
            gdf.to_file(output_path, driver='ESRI Shapefile')
            messages.append(f"Shapefile created: {output_path} with {len(geometries)} rectangles.")

        except Exception as e:
            messages.append(f"❌ Error creating shapefile for image {idx}: {e}")

    return messages

"""
test_output = create_georeferenced_rectangles(test_preproces[0], test_preproces[1], "C:/Users/Joseff01/Documents/Git/PDJoseRetanaQGIS/")

print(test_output)
"""