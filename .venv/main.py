from conv import converter
from resz import resizer

while True:

    func = input("Choose function (convert, resize): ")

    if func == "convert":

        original_format = input("Input original format: ")
        target_format = input("Input target format: ")
        mode = input("Select mode (single or mass or zip): ")
        if mode == "single":
            path = input("Input path to picture: ")
        elif mode == "mass":
            path = input("Input path to folder: ")
        elif mode == "zip":
            path = input("Input path to zip archive: ")

    elif func == "resize":

        save_proportions = bool(input("Save proportions (True, False): ").capitalize())
        width = int(input("Input width: "))
        height = int(input("Input height: "))
        mode = input("Select mode (single or mass or zip): ")
        if mode == "single":
            path = input("Input path to picture: ")
        elif mode == "mass":
            path = input("Input path to folder: ")
        elif mode == "zip":
            path = input("Input path to zip archive: ")

        resizer.resize(width, height, path, mode, save_proportions)