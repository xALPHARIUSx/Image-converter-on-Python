import webview
import os
import sys
import threading
import time

try:
    from conv import Converter
    converter = Converter()
except ImportError:
    converter = None

try:
    from resz import Resizer
    resizer = Resizer()
except ImportError:
    resizer = None


# ── перехватчик stdout (только для full log) ──────────────────────────────────

class StdoutCapture:
    """
    Буфер потокобезопасен (threading.local).
    Прогресс теперь идёт через колбэк — здесь только full log.
    """
    def __init__(self, original):
        self._original = original
        self.enabled   = False
        self._window   = None
        self._local    = threading.local()

    def _buf(self):
        if not hasattr(self._local, 'buf'):
            self._local.buf = ""
        return self._local.buf

    def _set_buf(self, val):
        self._local.buf = val

    def write(self, text):
        self._original.write(text)
        if not self.enabled or not self._window:
            return
        self._set_buf(self._buf() + text)
        while "\n" in self._buf():
            line, rest = self._buf().split("\n", 1)
            self._set_buf(rest)
            line = line.strip()
            if line:
                safe = line.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
                self._window.evaluate_js(f'logPrint(`{safe}`)')

    def flush(self):
        self._original.flush()


_capture = StdoutCapture(sys.stdout)
sys.stdout = _capture


# ── фабрика колбэка прогресса ─────────────────────────────────────────────────

def make_progress_callback(win):
    """
    Возвращает функцию on_progress(done, total).
    При done==0 инициализирует прогресс-бар (progressInit).
    При done>0  шлёт шаг + ETC (progressUpdate).
    """
    start_time = [None]

    def on_progress(done, total):
        if not win:
            return
        if done == 0:
            start_time[0] = time.monotonic()
            win.evaluate_js(f'progressInit({total})')
            return

        elapsed = time.monotonic() - start_time[0]
        if done > 0:
            per_item = elapsed / done
            remaining = per_item * (total - done)
            # форматируем ETC: mm:ss или просто сек
            if remaining >= 60:
                etc = f"{int(remaining // 60)}m {int(remaining % 60)}s"
            else:
                etc = f"{int(remaining)}s"
        else:
            etc = "…"

        safe_etc = etc.replace("\\", "\\\\").replace("`", "\\`")
        win.evaluate_js(f'progressUpdate({done}, {total}, `{safe_etc}`)')

    return on_progress


# ── API ───────────────────────────────────────────────────────────────────────

class API:

    def pick_file(self, file_types=None):
        types = file_types if file_types else ()
        result = window.create_file_dialog(webview.OPEN_DIALOG, file_types=tuple(types))
        return result[0] if result else ""

    def pick_folder(self):
        result = window.create_file_dialog(webview.FOLDER_DIALOG)
        return result[0] if result else ""

    def set_full_log(self, enabled: bool):
        _capture.enabled = bool(enabled)
        return {"ok": True}

    def convert(self, orig_fmt, tgt_fmt, path, mode, quality=50):
        if converter is None:
            return {"ok": False, "msg": "conv.py not found or failed to import."}
        if not os.path.exists(path):
            return {"ok": False, "msg": f"Path not found: {path}"}
        try:
            cb = make_progress_callback(window)
            converter.convert(orig_fmt, tgt_fmt, path, mode, quality=int(quality), on_progress=cb)
            return {"ok": True, "msg": f"Conversion complete: {orig_fmt} → {tgt_fmt}"}
        except Exception as e:
            return {"ok": False, "msg": str(e)}

    def resize(self, width, height, path, mode, keep_prop):
        if resizer is None:
            return {"ok": False, "msg": "resz.py not found or failed to import."}
        if not os.path.exists(path):
            return {"ok": False, "msg": f"Path not found: {path}"}
        try:
            cb = make_progress_callback(window)
            resizer.resize(int(width), int(height), path, mode, bool(keep_prop), on_progress=cb)
            return {"ok": True, "msg": f"Resize complete: {width}×{height}"}
        except Exception as e:
            return {"ok": False, "msg": str(e)}

    def module_status(self):
        return {
            "conv": converter is not None,
            "resz": resizer is not None,
        }


# ── запуск ────────────────────────────────────────────────────────────────────

def on_loaded():
    _capture._window = window


if __name__ == "__main__":
    api = API()
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui.html")

    window = webview.create_window(
        title="IMG TOOL",
        url=f"file://{html_path}",
        js_api=api,
        width=620,
        height=740,
        resizable=False,
        background_color="#171717",
    )

    webview.start(on_loaded, debug=False)
