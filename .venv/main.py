from test import converter

while True:

    original_format = input("Input original format: ")
    target_format = input("Input target format: ")
    mode = input("Select mode (single or mass): ")
    if mode == "single":
        path = input("Input path to picture: ")
    else:
        path = input("Input path to folder: ")
    
    converter.convert(original_format, target_format, path, mode)