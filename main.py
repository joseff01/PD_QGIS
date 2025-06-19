import questionary
import argparse
import os
from CoffeeGeoreference import import_geospatial_data, preprocess_coordinates, create_georeferenced_rectangles

# Memory for intermediate steps
cache = {
    "images": None,
    "csvs": None,
    "bboxes": None,
    "crs_list": None
}

def run_from_args(args):
    print("Running in non-interactive mode...\n")

    result = import_geospatial_data(args.images, args.csvs)
    if isinstance(result, str):
        print(f"Import error: {result}")
        return
    else:
        images, csvs = result
        print("Import completed.")

    bboxes, crs_list, errors = preprocess_coordinates(images, csvs)
    if errors:
        print("\nPreprocessing warnings:")
        for e in errors:
            print("-", e)
    print("Preprocessing complete.")

    result = create_georeferenced_rectangles(bboxes, crs_list, images, args.output)
    print("\nShapefile generation results:")
    for line in result:
        print(line)

def step_import():
    img_path = questionary.path("📂 Enter path to image or image folder (.tif):").ask()
    csv_path = questionary.path("📄 Enter path to CSV or CSV folder:").ask()
    
    result = import_geospatial_data(img_path, csv_path)
    
    if isinstance(result, str):
        print(f"❌ Import error: {result}")
    else:
        cache["images"], cache["csvs"] = result
        print("✅ Files imported successfully.")


def step_preprocess():
    if not cache["images"] or not cache["csvs"]:
        print("⚠️ Please import files first.")
        return
    
    bboxes, crs_list, errors = preprocess_coordinates(cache["images"], cache["csvs"])
    cache["bboxes"] = bboxes
    cache["crs_list"] = crs_list

    print("✅ Preprocessing complete.")
    if errors:
        print("\n⚠️ Warnings:")
        for e in errors:
            print("-", e)

def step_generate():
    if not cache["bboxes"] or not cache["crs_list"] or not cache["images"]:
        print("⚠️ Please run preprocessing first.")
        return
    
    out_folder = questionary.path("📁 Enter output folder path for shapefiles:").ask()
    result = create_georeferenced_rectangles(cache["bboxes"], cache["crs_list"], cache["images"], out_folder)
    
    print("\n".join(result))

def main_menu():
    while True:
        choice = questionary.select(
            "Coffee Georeferencing Tool — Choose an option:",
            choices=[
                "1️⃣ Import Geospatial Data",
                "2️⃣ Preprocess Coordinates",
                "3️⃣ Generate Shapefile",
                "🚪 Exit"
            ]
        ).ask()

        if choice.startswith("1"):
            step_import()
        elif choice.startswith("2"):
            step_preprocess()
        elif choice.startswith("3"):
            step_generate()
        else:
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Coffee Plant Georeferencing Tool")
    parser.add_argument("--images", help="Path to image folder or .tif image")
    parser.add_argument("--csvs", help="Path to CSV folder or single CSV file")
    parser.add_argument("--output", help="Path to output folder for shapefiles")

    args = parser.parse_args()

    if args.images and args.csvs and args.output:
        run_from_args(args)
    else:
        main_menu()
