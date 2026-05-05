import os
import time
import shutil as sh
import zipfile as zf
from PIL import Image
from concurrent.futures import ThreadPoolExecutor


def _save_kwargs(fmt, quality):
    """
    Возвращает словарь kwargs для img.save() в зависимости от формата и качества.
    quality: int 0–100 (нормализованное значение из UI).
      - JPEG/JPG : quality=1..95
      - WEBP     : quality=1..100
      - PNG      : compress_level=0..9 (инвертировано: 100 → 0, 0 → 9)
      - остальные: kwargs пустой
    """
    fmt = fmt.lower()
    if fmt in ("jpg", "jpeg"):
        q = max(1, min(95, round(quality * 95 / 100)))
        return {"quality": q}
    elif fmt == "webp":
        q = max(1, min(100, quality))
        return {"quality": q}
    elif fmt == "png":
        # PNG сжатие без потерь: 0 = нет сжатия (быстро/большой файл),
        # 9 = максимум (медленно/маленький файл).
        # Инвертируем: quality=100 → compress_level=0, quality=0 → compress_level=9
        level = round((100 - quality) * 9 / 100)
        return {"compress_level": level}
    return {}


class Converter:
    def convert(self, original_format, target_format, path, mode, quality=50, on_progress=None):
        target_format = target_format.lower()
        original_format = original_format.lower()

        SUPPORTED_FORMATS = {"jpg", "jpeg", "png", "webp", "bmp", "tiff", "gif"}
        if target_format not in SUPPORTED_FORMATS:
            print(f"Unsupported format: {target_format}")
            return

        save_kw = _save_kwargs(target_format, quality)

        if mode == "single":
            img = Image.open(path)
            filename, _ = os.path.splitext(path)

            if target_format in ("jpg", "jpeg"):
                img = img.convert('RGB')
                img.save(f"{filename}.{target_format}", "JPEG", **save_kw)
            else:
                img.save(f"{filename}.{target_format}", target_format.upper(), **save_kw)

            if target_format == "jpg":
                img.save(f'{path[0:len(path) - len(target_format)+1]}.{target_format.lower()}', "jpeg", **save_kw)
            else:
                img.save(f'{path[0:len(path) - len(target_format)+1]}.{target_format.lower()}', f"{target_format}", **save_kw)
            print("Done!")
            if on_progress:
                on_progress(1, 1)

        elif mode == "mass":
            start_time = time.perf_counter()
            result_dir = os.path.join(path, "result")
            os.makedirs(result_dir, exist_ok=True)

            images = [
                f for f in os.listdir(path)
                if f.lower().endswith(f".{original_format}")
            ]

            print("In queue:", images, "\n")
            if on_progress:
                on_progress(0, len(images))

            done_count = [0]
            lock = __import__('threading').Lock()

            def process_image(filename):
                try:
                    img = Image.open(os.path.join(path, filename))
                    name, _ = os.path.splitext(filename)
                    save_path = os.path.join(result_dir, f"{name}.{target_format}")

                    if target_format in ("jpg", "jpeg"):
                        img = img.convert("RGB")
                        img.save(save_path, "JPEG", **save_kw)
                    else:
                        img.save(save_path, target_format.upper(), **save_kw)

                    print(f"{filename} Done!")
                    if on_progress:
                        with lock:
                            done_count[0] += 1
                            on_progress(done_count[0], len(images))
                except Exception as e:
                    print(f"{filename} failed: {e}")

            with ThreadPoolExecutor() as executor:
                executor.map(process_image, images)
            
            run_time = time.perf_counter() - start_time
            print(f"\n [Done in {run_time:.3f} sec.]\n")

        elif mode == "zip":
            start_time = time.perf_counter()
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
            if on_progress:
                on_progress(0, len(images))

            done_count = [0]
            lock = __import__('threading').Lock()

            def process_image(filename):
                try:
                    img = Image.open(os.path.join(source_dir, filename))
                    name, _ = os.path.splitext(filename)
                    save_path = os.path.join(result_dir, f"{name}.{target_format}")

                    if target_format in ("jpg", "jpeg"):
                        img = img.convert("RGB")
                        img.save(save_path, "JPEG", **save_kw)
                    else:
                        img.save(save_path, target_format.upper(), **save_kw)

                    print(f"{filename} Done!")
                    if on_progress:
                        with lock:
                            done_count[0] += 1
                            on_progress(done_count[0], len(images))
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

            run_time = time.perf_counter() - start_time
            print(f"\n [Done in {run_time:.3f} sec.]\n")

converter = Converter()
