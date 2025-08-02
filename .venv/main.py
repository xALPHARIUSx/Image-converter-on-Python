from conv import converter

while True:

    original_format = input("Input original format: ")
    target_format = input("Input target format: ")
    mode = input("Select mode (single or mass or zip): ")
    if mode == "single":
        path = input("Input path to picture: ")
    elif mode == "mass":
        path = input("Input path to folder: ")
    elif mode == "zip":
        path = input("Input path to zip archive: ")
    
    converter.convert(original_format, target_format, path, mode)