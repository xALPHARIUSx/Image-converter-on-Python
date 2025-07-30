import os
from PIL import Image

class Converter:
    def convert(self, original_format, target_format, path, mode):
        if mode == "single":
            img = Image.open(f'{path}')
            if target_format.lower() == "jpg" or target_format.lower() == "jpeg":
                img = img.convert('RGB')
            if target_format == "jpg":
                img.save(f'{path[0:len(path) - len(target_format)+1]}.{target_format.lower()}', "jpeg")
            else:
                img.save(f'{path[0:len(path) - len(target_format)+1]}.{target_format.lower()}', f"{target_format}")
            print("Done!")
        if mode == "mass":
            try:
                os.mkdir(fr"{path}\result")
            except:
                pass

            images = []
            for x in os.listdir(path):
                if x.endswith(f".{original_format}"):
                    images.append(x)

            print("In queue: " + str(images) + "\n")

            for i in images:
                img = Image.open(fr'{path}\{i}')
                img.save(fr'{path}\result\{i[0:len(i) - len(target_format)+1]}.{target_format.lower()}', f'{target_format.lower()}')
                print(i + " Done!")

converter = Converter()
