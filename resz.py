import os
import shutil as sh
import zipfile as zf
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

class Resizer:
    def resize(self, req_width, req_height, path, mode, save_proportions):
        SUPPORTED_FORMATS = {"jpg", "jpeg", "png", "webp", "bmp", "tiff", "gif"}


        if mode == "single":

            try:
                img = Image.open(path)
                filename = os.path.basename(path)
                result_dir = os.path.join(os.path.split(path)[0], "result")
                save_path = os.path.join(result_dir, filename)

                if save_proportions == True:
                    original_width = img.width
                    original_height = img.height
                    ratio = original_width / original_height
                    ratio = int(ratio)

                    if ratio > 1:
                        new_height = round(req_height / int(ratio))
                        size = (req_width, new_height)
                        img = img.resize(size, Image.LANCZOS)
                        img_format = str(os.path.splitext(os.path.split(path)[1])[1])

                        if img_format.upper() == ".JPG":
                            img.save(save_path, "JPEG")
                        else:
                            img.save(save_path, img_format[1:len(img_format)])
                    else:
                        new_width = round(req_width * int(ratio))
                        size = (new_width, req_height)
                        img = img.resize(size, Image.LANCZOS)
                        img_format = str(os.path.splitext(os.path.split(path)[1])[1])

                        if img_format.upper() == ".JPG":
                            img.save(save_path, "JPEG")
                        else:
                            img.save(save_path, img_format[1:len(img_format)])
                    
                else:
                    size = (req_width, req_height)
                    img.resize(size, Image.LANCZOS)
                    img.save(os.path.join(result_dir, filename))

                print("Done!")
                
            except Exception as e:
                print(f"{filename} failed: {e}")

        elif mode == "mass":
            result_dir = os.path.join(path, "result")
            os.makedirs(result_dir, exist_ok=True)

            images = [
                f for f in os.listdir(path)
                if os.path.splitext(f)[1][1:].lower() in SUPPORTED_FORMATS
                ]

            print("In queue:", images, "\n")

            def process_image(filename):
                try:
                    save_path = os.path.join(result_dir, filename)
                    img = Image.open(os.path.join(path, filename))

                    if save_proportions == True:
                        original_width = img.width
                        original_height = img.height
                        ratio = original_width / original_height
                        ratio = int(ratio)

                        if ratio > 1:
                            new_height = round(req_height / int(ratio))
                            size = (req_width, new_height)
                            img = img.resize(size, Image.LANCZOS)
                            img_format = str(os.path.splitext(os.path.split(path)[1])[1])

                            if img_format.upper() == ".JPG":
                                img.save(save_path, "JPEG")
                            else:
                                img.save(save_path, img_format[1:len(img_format)])
                        else:
                            new_width = round(req_width * int(ratio))
                            size = (new_width, req_height)
                            img = img.resize(size, Image.LANCZOS)
                            img_format = str(os.path.splitext(os.path.split(path)[1])[1])

                            if img_format.upper() == ".JPG":
                                img.save(save_path, "JPEG")
                            else:
                                img.save(save_path, img_format[1:len(img_format)])
                        
                    else:
                        size = (req_width, req_height)
                        img.resize(size, Image.LANCZOS)
                        img.save(os.path.join(result_dir, filename))

                    print(f"{filename} Done!")
                except Exception as e:
                    print(f"{filename} failed: {e}")

            with ThreadPoolExecutor() as executor:
                executor.map(process_image, images)

        elif mode == "zip":

            result_dir = os.path.join(os.path.split(path)[0], "result")
            source_dir = os.path.join(os.path.split(path)[0], "source")
            os.makedirs(result_dir, exist_ok=True)
            os.makedirs(source_dir, exist_ok=True)

            with zf.ZipFile(path, 'r') as zipf:
                zipf.extractall(source_dir)

            images = [
                f for f in os.listdir(path)
                if os.path.splitext(f)[1][1:].lower() in SUPPORTED_FORMATS
                ]


            print("In queue:", images, "\n")

            def process_image(filename):
                try:

                    img = Image.open(path)
                    filename = os.path.basename(path)
                    save_path = os.path.join(result_dir, filename)

                    if save_proportions == True:
                        original_width = img.width
                        original_height = img.height
                        ratio = original_width / original_height
                        ratio = int(ratio)

                        if ratio > 1:
                            new_height = round(req_height / int(ratio))
                            size = (req_width, new_height)
                            img = img.resize(size, Image.LANCZOS)
                            img_format = str(os.path.splitext(os.path.split(path)[1])[1])

                            if img_format.upper() == ".JPG":
                                img.save(save_path, "JPEG")
                            else:
                                img.save(save_path, img_format[1:len(img_format)])
                        else:
                            new_width = round(req_width * int(ratio))
                            size = (new_width, req_height)
                            img = img.resize(size, Image.LANCZOS)
                            img_format = str(os.path.splitext(os.path.split(path)[1])[1])

                            if img_format.upper() == ".JPG":
                                img.save(save_path, "JPEG")
                            else:
                                img.save(save_path, img_format[1:len(img_format)])
                        
                    else:
                        size = (req_width, req_height)
                        img.resize(size, Image.LANCZOS)
                        img.save(os.path.join(result_dir, filename))


                    print(f"{filename} Done!")
                except Exception as e:
                    print(f"{filename} failed: {e}")

            with ThreadPoolExecutor() as executor:
                executor.map(process_image, images)

            images = [
                f for f in os.listdir(path)
                if os.path.splitext(f)[1][1:].lower() in SUPPORTED_FORMATS
                ]

            def packing_image(filename):
                abs_path = os.path.join(result_dir, filename)
                zipf.write(abs_path, arcname=filename)
                print(f"{filename} archived sucssesfully!")

            with zf.ZipFile(os.path.join(os.path.split(path)[0], f'_{os.path.splitext(os.path.split(path)[1])[0]}_result.zip'), 'w') as zipf:
                with ThreadPoolExecutor() as executor:
                    executor.map(packing_image, images)
                    
            
            sh.rmtree(source_dir)
            sh.rmtree(result_dir)

            print("\nWORK DONE!")

resizer = Resizer()