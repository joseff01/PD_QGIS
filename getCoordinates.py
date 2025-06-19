from exif import Image

def show_all_exif(img_path):
    with open(img_path, 'rb') as img_file:
        img = Image(img_file)

    if img.has_exif:
        for attribute in dir(img):
            if not attribute.startswith('_') and not callable(getattr(img, attribute)):
                value = getattr(img, attribute)
                if value not in [None, b'']:
                    print(f"{attribute:30}: {value}")
    else:
        print("No EXIF data found.")

# Example usage
show_all_exif('Images/PLANTEX_01.jpg')
