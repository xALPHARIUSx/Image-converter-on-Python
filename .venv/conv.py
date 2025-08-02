import os
import shutil as sh
import zipfile as zf
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

class Converter:
    def convert(self, original_format, target_format, path, mode):
        target_format = target_format.lower()
        original_format = original_format.lower()

        SUPPORTED_FORMATS = {"jpg", "jpeg", "png", "webp", "bmp", "tiff", "gif"}
        if target_format not in SUPPORTED_FORMATS:
            print(f"Unsupported format: {target_format}")
            return

        if mode == "single":
            img = Image.open(path)
            filename, _ = os.path.splitext(path)

            if target_format in ("jpg", "jpeg"):
                img = img.convert('RGB')
                img.save(f"{filename}.{target_format}", "JPEG")
            else:
                img.save(f"{filename}.{target_format}", target_format.upper())

            if target_format == "jpg":
                img.save(f'{path[0:len(path) - len(target_format)+1]}.{target_format.lower()}', "jpeg")
            else:
                img.save(f'{path[0:len(path) - len(target_format)+1]}.{target_format.lower()}', f"{target_format}")
            print("Done!")

        elif mode == "mass":
            result_dir = os.path.join(path, "result")
            os.makedirs(result_dir, exist_ok=True)

            images = [
                f for f in os.listdir(path)
                if f.lower().endswith(f".{original_format}")
            ]

            print("In queue:", images, "\n")

            def process_image(filename):
                try:
                    img = Image.open(os.path.join(path, filename))
                    name, _ = os.path.splitext(filename)
                    save_path = os.path.join(result_dir, f"{name}.{target_format}")

                    if target_format in ("jpg", "jpeg"):
                        img = img.convert("RGB")
                        img.save(save_path, "JPEG")
                    else:
                        img.save(save_path, target_format.upper())

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
                f for f in os.listdir(source_dir)
                if f.lower().endswith(f".{original_format}")
            ]

            print("In queue:", images, "\n")

            def process_image(filename):
                try:
                    img = Image.open(os.path.join(source_dir, filename))
                    name, _ = os.path.splitext(filename)
                    save_path = os.path.join(result_dir, f"{name}.{target_format}")

                    if target_format in ("jpg", "jpeg"):
                        img = img.convert("RGB")
                        img.save(save_path, "JPEG")
                    else:
                        img.save(save_path, target_format.upper())

                    print(f"{filename} Done!")
                except Exception as e:
                    print(f"{filename} failed: {e}")

            with ThreadPoolExecutor() as executor:
                executor.map(process_image, images)

            images = [
                m for m in os.listdir(result_dir)
                if m.lower().endswith(f".{target_format}")
            ]

            with zf.ZipFile(os.path.join(os.path.split(path)[0], f'_{os.path.splitext(os.path.split(path)[1])[0]}_result.zip'), 'w') as zipf:
                for u in images:
                    abs_path = os.path.join(result_dir, u)
                    zipf.write(abs_path, arcname=u)
                    print(f"{u} archived sucssesfully!")
            
            sh.rmtree(source_dir)
            sh.rmtree(result_dir)

            print("\nWORK DONE!")

converter = Converter()
