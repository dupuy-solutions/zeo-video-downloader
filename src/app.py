import os
import json
import queue
import re
import shutil
import subprocess
import sys
import threading
import tkinter as tk
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk
from urllib.parse import urlparse

from i18n import LANGUAGES, Translator, detect_language


APP_NAME = "Zeo Video Downloader"
APP_VERSION = "1.9"
EXTENSION_HOST = "127.0.0.1"
EXTENSION_PORT = 17835
SUPPORT_URL = "https://link.mercadopago.cl/zeovideodownloader"


def default_download_folder() -> str:
    folder = Path.home() / "Downloads"
    return str(folder if folder.exists() else Path.home())


def startupinfo():
    if os.name != "nt":
        return None
    info = subprocess.STARTUPINFO()
    info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return info


class ScreenRecorder(tk.Toplevel):
    def __init__(self, parent, folder, translator):
        super().__init__(parent)
        self.translator = translator
        self.tr = translator.tr
        self.title(self.tr("rec.title"))
        self.geometry("700x820")
        self.minsize(650, 760)
        self.configure(bg="#111827")
        self.transient(parent)
        self.folder = tk.StringVar(value=folder)
        self.fps = tk.StringVar(value="30 FPS")
        self.quality_options = {
            self.tr("rec.quality.light"): "light", self.tr("rec.quality.balanced"): "balanced",
            self.tr("rec.quality.high"): "high", self.tr("rec.quality.maximum"): "maximum",
        }
        self.limit_options = {
            self.tr("rec.limit.none"): None, self.tr("rec.limit.30"): 30, self.tr("rec.limit.60"): 60,
            self.tr("rec.limit.90"): 90, self.tr("rec.limit.120"): 120,
        }
        self.no_audio = self.tr("rec.no_audio")
        self.quality_preset = tk.StringVar(value=self.tr("rec.quality.balanced"))
        self.auto_stop = tk.StringVar(value=self.tr("rec.limit.none"))
        self.client_name = tk.StringVar()
        self.project_name = tk.StringVar()
        self.topic_name = tk.StringVar()
        self.system_audio = tk.StringVar(value=self.no_audio)
        self.microphone = tk.StringVar(value=self.no_audio)
        self.area_text = tk.StringVar(value=self.tr("rec.area_full"))
        self.capture_rect = None
        self.status = tk.StringVar(value=self.tr("rec.preparing"))
        self.process = None
        self.output_file = None
        self.recovery_file = None
        self.started_at = None
        self.timer_job = None
        self.auto_stop_job = None
        self.markers = []
        self._build()
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        self.bind("<F8>", lambda _event: self.take_screenshot())
        self.bind("<F9>", lambda _event: self.start() if not self.process else None)
        self.bind("<F10>", lambda _event: self.stop())
        threading.Thread(target=self._load_audio_devices, daemon=True).start()

    def _build(self):
        root = ttk.Frame(self, padding=24)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text=self.tr("rec.title"), style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            root,
            text=self.tr("rec.consent"),
            style="Hint.TLabel",
        ).pack(anchor="w", pady=(2, 18))

        ttk.Label(root, text=self.tr("rec.folder")).pack(anchor="w")
        folder_row = ttk.Frame(root)
        folder_row.pack(fill="x", pady=(5, 15))
        ttk.Entry(folder_row, textvariable=self.folder).pack(side="left", fill="x", expand=True)
        ttk.Button(folder_row, text=self.tr("choose"), command=self.choose_folder).pack(side="left", padx=(8, 0))

        identity = ttk.Frame(root)
        identity.pack(fill="x", pady=(0, 15))
        for label, variable in ((self.tr("rec.client"), self.client_name), (self.tr("rec.project"), self.project_name), (self.tr("rec.topic"), self.topic_name)):
            column = ttk.Frame(identity)
            column.pack(side="left", fill="x", expand=True, padx=(0, 8))
            ttk.Label(column, text=label).pack(anchor="w")
            ttk.Entry(column, textvariable=variable).pack(fill="x", pady=(4, 0))

        area_row = ttk.Frame(root)
        area_row.pack(fill="x", pady=(0, 15))
        area_left = ttk.Frame(area_row)
        area_left.pack(side="left", fill="x", expand=True)
        ttk.Label(area_left, text=self.tr("rec.area")).pack(anchor="w")
        ttk.Label(area_left, textvariable=self.area_text, style="Hint.TLabel").pack(anchor="w", pady=(4, 0))
        ttk.Button(area_row, text=self.tr("rec.select_area"), command=self.select_area).pack(side="left", padx=(8, 0))
        ttk.Button(area_row, text=self.tr("rec.fullscreen"), command=self.full_screen).pack(side="left", padx=(8, 0))

        ttk.Label(root, text=self.tr("rec.flow")).pack(anchor="w")
        capture_options = ttk.Frame(root)
        capture_options.pack(fill="x", pady=(5, 15))
        ttk.Combobox(capture_options, state="readonly", textvariable=self.fps, values=("30 FPS", "60 FPS"), width=14).pack(side="left")
        ttk.Combobox(capture_options, state="readonly", textvariable=self.quality_preset, values=tuple(self.quality_options), width=16).pack(side="left", padx=8)
        ttk.Combobox(capture_options, state="readonly", textvariable=self.auto_stop, values=tuple(self.limit_options), width=18).pack(side="left")

        ttk.Label(root, text=self.tr("rec.system_audio")).pack(anchor="w")
        self.system_box = ttk.Combobox(root, state="readonly", textvariable=self.system_audio, values=(self.no_audio,), width=66)
        self.system_box.pack(fill="x", pady=(5, 15))

        ttk.Label(root, text=self.tr("rec.microphone")).pack(anchor="w")
        self.mic_box = ttk.Combobox(root, state="readonly", textvariable=self.microphone, values=(self.no_audio,), width=66)
        self.mic_box.pack(fill="x", pady=(5, 15))

        ttk.Label(
            root,
            text=self.tr("rec.notice"),
            style="Hint.TLabel",
        ).pack(anchor="w")
        ttk.Label(root, textvariable=self.status).pack(anchor="w", pady=(12, 10))
        self.timer_label = ttk.Label(root, text="00:00:00", style="Title.TLabel")
        self.timer_label.pack(anchor="w", pady=(0, 8))

        row = ttk.Frame(root)
        row.pack(fill="x")
        self.start_btn = ttk.Button(row, text=self.tr("rec.start"), style="Accent.TButton", command=self.start)
        self.start_btn.pack(side="left")
        self.stop_btn = ttk.Button(row, text=self.tr("rec.stop"), state="disabled", command=self.stop)
        self.stop_btn.pack(side="left", padx=8)
        self.shot_btn = ttk.Button(row, text=self.tr("rec.shot"), state="disabled", command=self.take_screenshot)
        self.shot_btn.pack(side="left", padx=(0, 8))
        self.marker_btn = ttk.Button(row, text=self.tr("rec.marker"), state="disabled", command=self.add_marker)
        self.marker_btn.pack(side="left")
        ttk.Button(row, text=self.tr("rec.open"), command=self.open_folder).pack(side="right")

    def _ffmpeg(self):
        local = Path(sys.executable).resolve().parent / "ffmpeg.exe"
        return str(local) if local.exists() else (shutil.which("ffmpeg") or shutil.which("ffmpeg.exe"))

    def _load_audio_devices(self):
        ffmpeg = self._ffmpeg()
        if not ffmpeg or os.name != "nt":
            self.after(0, lambda: self.status.set(self.tr("rec.ffmpeg")))
            return
        result = subprocess.run(
            [ffmpeg, "-hide_banner", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            startupinfo=startupinfo(), creationflags=subprocess.CREATE_NO_WINDOW,
        )
        devices = []
        for line in result.stderr.splitlines():
            match = re.search(r'"([^"\r\n]+)"\s+\(audio\)', line, re.I)
            if match and match.group(1) not in devices:
                devices.append(match.group(1))
        self.after(0, lambda: self._set_devices(devices))

    def _set_devices(self, devices):
        values = (self.no_audio, *devices)
        self.system_box.configure(values=values)
        self.mic_box.configure(values=values)
        stereo = next((d for d in devices if "stereo mix" in d.lower() or "mezcla estéreo" in d.lower()), None)
        mic = next((d for d in devices if "microphone" in d.lower() or "micrófono" in d.lower()), None)
        if stereo:
            self.system_audio.set(stereo)
        if mic and mic != stereo:
            self.microphone.set(mic)
        self.status.set(self.tr("rec.devices", count=len(devices)))

    def choose_folder(self):
        selected = filedialog.askdirectory(initialdir=self.folder.get(), parent=self)
        if selected:
            self.folder.set(selected)

    def select_area(self):
        self.withdraw()
        self.after(150, lambda: RegionSelector(self.master, self._area_selected, self._area_cancelled, self.translator))

    def _area_selected(self, rect):
        self.capture_rect = rect
        x, y, width, height = rect
        self.area_text.set(self.tr("rec.area_custom", width=width, height=height, x=x, y=y))
        self.deiconify()
        self.lift()

    def _area_cancelled(self):
        self.deiconify()
        self.lift()

    def full_screen(self):
        self.capture_rect = None
        self.area_text.set(self.tr("rec.area_full"))

    def open_folder(self):
        folder = Path(self.folder.get()).expanduser()
        folder.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            os.startfile(str(folder))

    def start(self):
        ffmpeg = self._ffmpeg()
        if not ffmpeg:
            messagebox.showerror(APP_NAME, self.tr("rec.ffmpeg_not_found"), parent=self)
            return
        if not messagebox.askyesno(
            APP_NAME,
            self.tr("rec.confirm"),
            parent=self,
        ):
            return
        self.start_btn.configure(state="disabled")
        self.status.set(self.tr("rec.starts"))
        self._countdown(3)

    def _countdown(self, seconds):
        if seconds > 0:
            self.status.set(self.tr("rec.countdown", seconds=seconds))
            self.after(1000, lambda: self._countdown(seconds - 1))
            return
        self._begin_recording()

    @staticmethod
    def _safe_name(value):
        value = re.sub(r'[<>:"/\\|?*]+', "_", value.strip())
        return re.sub(r"\s+", "_", value)[:60]

    def _begin_recording(self):
        ffmpeg = self._ffmpeg()
        folder = Path(self.folder.get()).expanduser()
        folder.mkdir(parents=True, exist_ok=True)
        parts = [self._safe_name(v.get()) for v in (self.client_name, self.project_name, self.topic_name) if v.get().strip()]
        stem = "_".join(parts) or "Videollamada"
        stem += f"_{datetime.now():%Y-%m-%d_%H-%M-%S}"
        self.output_file = folder / f"{stem}.mp4"
        self.recovery_file = folder / f"{stem}.recuperacion.mkv"
        self.markers.clear()
        fps = "60" if self.fps.get().startswith("60") else "30"
        cmd = [ffmpeg, "-y", "-thread_queue_size", "1024", "-f", "gdigrab", "-framerate", fps, "-draw_mouse", "1"]
        if self.capture_rect:
            x, y, width, height = self.capture_rect
            cmd += ["-offset_x", str(x), "-offset_y", str(y), "-video_size", f"{width}x{height}"]
        cmd += ["-i", "desktop"]
        selected = []
        for device in (self.system_audio.get(), self.microphone.get()):
            if device != self.no_audio and device not in selected:
                selected.append(device)
                cmd += ["-thread_queue_size", "1024", "-f", "dshow", "-i", f"audio={device}"]
        if len(selected) == 2:
            cmd += ["-filter_complex", "[1:a][2:a]amix=inputs=2:duration=longest:dropout_transition=2[a]", "-map", "0:v", "-map", "[a]"]
        elif len(selected) == 1:
            cmd += ["-map", "0:v", "-map", "1:a"]
        else:
            cmd += ["-map", "0:v"]
        quality = {
            "light": ("ultrafast", "29"), "balanced": ("veryfast", "23"),
            "high": ("fast", "19"), "maximum": ("medium", "16"),
        }
        preset, crf = quality[self.quality_options[self.quality_preset.get()]]
        cmd += ["-c:v", "libx264", "-preset", preset, "-crf", crf, "-pix_fmt", "yuv420p"]
        if selected:
            cmd += ["-c:a", "aac", "-b:a", "160k"]
        cmd += [str(self.recovery_file)]
        try:
            self.process = subprocess.Popen(
                cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                text=True, encoding="utf-8", errors="replace", startupinfo=startupinfo(),
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
        except Exception as exc:
            self.start_btn.configure(state="normal")
            messagebox.showerror(APP_NAME, str(exc), parent=self)
            return
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.shot_btn.configure(state="normal")
        self.marker_btn.configure(state="normal")
        self.started_at = datetime.now()
        self._update_timer()
        minutes = self.limit_options.get(self.auto_stop.get())
        if minutes:
            self.auto_stop_job = self.after(minutes * 60 * 1000, self.stop)
        self.status.set(self.tr("rec.recording"))
        threading.Thread(target=self._watch_process, daemon=True).start()

    def _watch_process(self):
        error_text = self.process.stderr.read() if self.process and self.process.stderr else ""
        code = self.process.wait() if self.process else 1
        self.after(0, lambda: self._finished(code, error_text))

    def stop(self):
        if self.process and self.process.poll() is None:
            self.status.set(self.tr("rec.finalizing"))
            try:
                self.process.stdin.write("q\n")
                self.process.stdin.flush()
            except (BrokenPipeError, OSError):
                self.process.terminate()

    def _elapsed_seconds(self):
        return int((datetime.now() - self.started_at).total_seconds()) if self.started_at else 0

    @staticmethod
    def _clock(seconds):
        return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"

    def _update_timer(self):
        if self.process and self.process.poll() is None:
            self.timer_label.configure(text=self._clock(self._elapsed_seconds()))
            self.timer_job = self.after(500, self._update_timer)

    def add_marker(self):
        if not self.process:
            return
        note = simpledialog.askstring(APP_NAME, self.tr("rec.marker_prompt"), parent=self) or self.tr("rec.marker_default")
        self.markers.append((self._clock(self._elapsed_seconds()), note.strip()))
        self.status.set(self.tr("rec.marker_added", time=self.markers[-1][0], note=self.markers[-1][1]))

    def take_screenshot(self):
        if not self.process or not self.output_file:
            return
        ffmpeg = self._ffmpeg()
        shot = self.output_file.with_name(f"{self.output_file.stem}_captura_{self._clock(self._elapsed_seconds()).replace(':', '-')}.png")
        cmd = [ffmpeg, "-y", "-f", "gdigrab", "-framerate", "1", "-draw_mouse", "1"]
        if self.capture_rect:
            x, y, width, height = self.capture_rect
            cmd += ["-offset_x", str(x), "-offset_y", str(y), "-video_size", f"{width}x{height}"]
        cmd += ["-i", "desktop", "-frames:v", "1", str(shot)]
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, startupinfo=startupinfo(), creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        self.status.set(self.tr("rec.shot_saved", name=shot.name))

    def _finished(self, code, error_text):
        self.process = None
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None
        if self.auto_stop_job:
            self.after_cancel(self.auto_stop_job)
            self.auto_stop_job = None
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.shot_btn.configure(state="disabled")
        self.marker_btn.configure(state="disabled")
        if code == 0 and self.recovery_file and self.recovery_file.exists():
            self.status.set(self.tr("rec.finalizing"))
            threading.Thread(target=self._finalize_mp4, daemon=True).start()
        else:
            self.status.set(self.tr("rec.failed"))
            hint = self.tr("rec.audio_hint")
            if "Could not find audio only device" in error_text:
                hint = self.tr("rec.audio_missing")
            messagebox.showerror(APP_NAME, hint, parent=self)

    def _finalize_mp4(self):
        ffmpeg = self._ffmpeg()
        result = subprocess.run(
            [ffmpeg, "-y", "-i", str(self.recovery_file), "-c", "copy", "-movflags", "+faststart", str(self.output_file)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            startupinfo=startupinfo(), creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if result.returncode == 0:
            try:
                self.recovery_file.unlink()
            except OSError:
                pass
            if self.markers:
                notes = self.output_file.with_name(f"{self.output_file.stem}_marcas.txt")
                notes.write_text("\n".join(f"{time} – {note}" for time, note in self.markers), encoding="utf-8")
            self.after(0, lambda: self._finalized_ok())
        else:
            self.after(0, lambda: messagebox.showwarning(APP_NAME, self.tr("rec.warning", file=self.recovery_file), parent=self))

    def _finalized_ok(self):
        self.status.set(self.tr("rec.saved_status", name=self.output_file.name))
        messagebox.showinfo(APP_NAME, self.tr("rec.saved", file=self.output_file), parent=self)

    def close_window(self):
        if self.process and self.process.poll() is None:
            if not messagebox.askyesno(APP_NAME, self.tr("rec.close_active"), parent=self):
                return
            self.stop()
        self.destroy()


class RegionSelector(tk.Toplevel):
    def __init__(self, parent, on_select, on_cancel, translator):
        super().__init__(parent)
        self.translator = translator
        self.on_select = on_select
        self.on_cancel = on_cancel
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        try:
            self.attributes("-alpha", 0.35)
        except tk.TclError:
            pass
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry(f"{width}x{height}+0+0")
        self.canvas = tk.Canvas(self, bg="black", cursor="cross", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_text(
            width // 2, 35,
            text=translator.tr("rec.region"),
            fill="white", font=("Segoe UI Semibold", 14),
        )
        self.canvas.bind("<ButtonPress-1>", self._start)
        self.canvas.bind("<B1-Motion>", self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._finish)
        self.bind("<Escape>", lambda _event: self._cancel())
        self.focus_force()

    def _start(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            event.x, event.y, event.x, event.y, outline="#38bdf8", width=5, fill="#2563eb",
        )

    def _drag(self, event):
        if self.rect_id:
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def _finish(self, event):
        if self.start_x is None:
            return
        x1, x2 = sorted((self.start_x, event.x))
        y1, y2 = sorted((self.start_y, event.y))
        width = (x2 - x1) // 2 * 2
        height = (y2 - y1) // 2 * 2
        if width < 160 or height < 120:
            messagebox.showwarning(APP_NAME, self.translator.tr("rec.area_too_small"), parent=self)
            return
        self.destroy()
        self.on_select((x1, y1, width, height))

    def _cancel(self):
        self.destroy()
        self.on_cancel()


class DownloaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("1120x720")
        self.minsize(720, 430)
        self.configure(bg="#111827")
        self.events = queue.Queue()
        self.tasks = {}
        self.processes = {}
        self.starting = set()
        self.pause_requested = set()
        self.recent_log = []
        self.compact = False
        self.sort_reverse = {}
        self.active_sort = None
        base = Path(os.getenv("LOCALAPPDATA") or (Path.home() / ".zeo_downloader"))
        self.state_dir = base / "ZeoVideoDownloader"
        self.state_file = self.state_dir / "descargas.json"
        saved_language = self._saved_language()
        self.translator = Translator(saved_language)
        self.tr = self.translator.tr
        self.language_code = tk.StringVar(value=saved_language)
        self.language_display = tk.StringVar(value=LANGUAGES[saved_language])
        self.url = tk.StringVar()
        self.folder = tk.StringVar(value=default_download_folder())
        self.kind = tk.StringVar(value="video")
        self.kind_display = tk.StringVar(value=self.tr("format.video"))
        self.quality = tk.StringVar(value="best")
        self.quality_display = tk.StringVar(value=self.tr("quality.best"))
        self.playlist = tk.BooleanVar(value=False)
        self.parallel_downloads = tk.IntVar(value=3)
        self.fragments = tk.IntVar(value=8)
        self.status = tk.StringVar(value=self.tr("status.ready"))
        self.progress = tk.DoubleVar(value=0)
        self.logo_image = None
        logo_path = Path(__file__).resolve().parent / "assets" / "zeo_logo.png"
        if logo_path.exists():
            try:
                self.logo_image = tk.PhotoImage(file=str(logo_path))
                self.iconphoto(True, self.logo_image)
            except tk.TclError:
                self.logo_image = None
        self._build_ui()
        self._load_state()
        self._start_extension_bridge()
        self.protocol("WM_DELETE_WINDOW", self._close_app)
        self.after(100, self._drain_events)

    def _saved_language(self):
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding="utf-8"))
                code = data.get("language")
                if code in LANGUAGES:
                    return code
            except (OSError, ValueError, TypeError):
                pass
        return detect_language()

    def _start_extension_bridge(self):
        app = self

        class ExtensionHandler(BaseHTTPRequestHandler):
            def _reply(self, code, payload):
                body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self):
                if self.path != "/download" or self.headers.get("X-Zeo-Extension") != "firefox-1.0":
                    self._reply(403, {"ok": False, "error": "Solicitud no autorizada"})
                    return
                try:
                    length = min(int(self.headers.get("Content-Length", "0")), 16384)
                    data = json.loads(self.rfile.read(length).decode("utf-8"))
                    url = str(data.get("url", "")).strip()
                except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
                    self._reply(400, {"ok": False, "error": "Solicitud inválida"})
                    return
                if not re.match(r"^https?://", url, re.I):
                    self._reply(400, {"ok": False, "error": "La pestaña no contiene un enlace web válido"})
                    return
                app.events.put(("external_url", url))
                self._reply(202, {"ok": True, "message": "Enviado a Zeo Downloader"})

            def log_message(self, _format, *_args):
                return

        def serve():
            try:
                server = ThreadingHTTPServer((EXTENSION_HOST, EXTENSION_PORT), ExtensionHandler)
                server.daemon_threads = True
                server.serve_forever()
            except OSError:
                self.events.put(("log", "El enlace con Firefox no pudo iniciarse; puede que otra copia de Zeo Downloader ya esté abierta."))

        threading.Thread(target=serve, daemon=True).start()

    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#111827")
        style.configure("TLabel", background="#111827", foreground="#e5e7eb", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI Semibold", 22), foreground="#60a5fa")
        style.configure("Hint.TLabel", foreground="#9ca3af", font=("Segoe UI", 9))
        style.configure("Footer.TLabel", foreground="#6b7280", font=("Segoe UI Semibold", 8))
        style.configure("TButton", font=("Segoe UI Semibold", 10), padding=8)
        style.configure("Accent.TButton", background="#2563eb", foreground="white")
        style.map("Accent.TButton", background=[("active", "#1d4ed8"), ("disabled", "#374151")])
        style.configure("TCheckbutton", background="#111827", foreground="#e5e7eb")
        style.configure("TCombobox", padding=6)

        root = ttk.Frame(self, padding=18)
        root.pack(fill="both", expand=True)
        self.root_frame = root
        title_row = ttk.Frame(root)
        title_row.pack(fill="x")
        ttk.Label(title_row, text="Zeo Video Downloader", style="Title.TLabel").pack(side="left")
        self.compact_btn = ttk.Button(title_row, text=self.tr("view.compact"), command=self.toggle_compact)
        self.compact_btn.pack(side="right")
        self.maximize_btn = ttk.Button(title_row, text=self.tr("maximize"), command=self.toggle_maximize)
        self.maximize_btn.pack(side="right", padx=8)
        language_box = ttk.Combobox(title_row, state="readonly", textvariable=self.language_display, values=tuple(LANGUAGES.values()), width=14)
        language_box.pack(side="right", padx=(8, 0))
        language_box.bind("<<ComboboxSelected>>", self.change_language)
        ttk.Label(title_row, text=self.tr("language")).pack(side="right", padx=(12, 0))
        self.subtitle = ttk.Label(root, text=self.tr("subtitle"), style="Hint.TLabel")
        self.subtitle.pack(anchor="w", pady=(2, 16))

        self.input_frame = ttk.Frame(root)
        self.input_frame.pack(fill="x")
        ttk.Label(self.input_frame, text=self.tr("url.label")).pack(anchor="w")
        url_row = ttk.Frame(self.input_frame)
        url_row.pack(fill="x", pady=(6, 12))
        self.url_entry = ttk.Entry(url_row, textvariable=self.url, font=("Segoe UI", 11))
        self.url_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(url_row, text=self.tr("paste"), command=self.paste_url).pack(side="left", padx=(8, 0))
        self.download_btn = ttk.Button(url_row, text=self.tr("start"), style="Accent.TButton", command=self.add_download)
        self.download_btn.pack(side="left", padx=(8, 0))

        options = ttk.Frame(self.input_frame)
        options.pack(fill="x", pady=(0, 12))
        left = ttk.Frame(options)
        left.pack(side="left", fill="x", expand=True)
        ttk.Label(left, text=self.tr("format")).pack(anchor="w")
        self.kind_box = ttk.Combobox(left, state="readonly", textvariable=self.kind_display, values=(self.tr("format.video"), self.tr("format.audio")), width=20)
        self.kind_box.pack(anchor="w", pady=(5, 0))
        self.kind_box.bind("<<ComboboxSelected>>", self._kind_changed)
        middle = ttk.Frame(options)
        middle.pack(side="left", fill="x", expand=True, padx=20)
        ttk.Label(middle, text=self.tr("resolution")).pack(anchor="w")
        self.quality_box = ttk.Combobox(
            middle,
            state="readonly",
            textvariable=self.quality_display,
            values=(self.tr("quality.best"), "4320p (8K)", "2160p (4K)", "1440p (2K)", "1080p", "720p", "480p"),
            width=20,
        )
        self.quality_box.pack(anchor="w", pady=(5, 0))
        self.quality_box.bind("<<ComboboxSelected>>", self._quality_changed)
        right = ttk.Frame(options)
        right.pack(side="left", fill="x", expand=True)
        ttk.Label(right, text=self.tr("playlist")).pack(anchor="w")
        ttk.Checkbutton(right, text=self.tr("playlist.all"), variable=self.playlist).pack(anchor="w", pady=(6, 0))

        ttk.Label(self.input_frame, text=self.tr("destination")).pack(anchor="w")
        folder_row = ttk.Frame(self.input_frame)
        folder_row.pack(fill="x", pady=(6, 12))
        ttk.Entry(folder_row, textvariable=self.folder).pack(side="left", fill="x", expand=True)
        ttk.Button(folder_row, text=self.tr("choose"), command=self.choose_folder).pack(side="left", padx=(8, 0))
        ttk.Button(folder_row, text=self.tr("open"), command=self.open_folder).pack(side="left", padx=(8, 0))

        buttons = ttk.Frame(self.input_frame)
        buttons.pack(fill="x", pady=(0, 12))
        ttk.Button(buttons, text=self.tr("pause"), command=self.pause_selected).pack(side="left")
        ttk.Button(buttons, text=self.tr("resume"), command=self.resume_selected).pack(side="left")
        ttk.Button(buttons, text=self.tr("record"), command=self.open_recorder).pack(side="left", padx=(4, 0))
        ttk.Button(buttons, text=self.tr("update"), command=self.update_engine).pack(side="right")
        ttk.Button(buttons, text=self.tr("support"), command=lambda: webbrowser.open(SUPPORT_URL)).pack(side="right", padx=(0, 6))

        self.manager_frame = ttk.Frame(root)
        self.manager_frame.pack(fill="both", expand=True)
        manager_bar = ttk.Frame(self.manager_frame)
        manager_bar.pack(fill="x", pady=(0, 7))
        ttk.Label(manager_bar, text=self.tr("monitor"), style="Title.TLabel").pack(side="left")
        ttk.Label(manager_bar, text=self.tr("parallel")).pack(side="left", padx=(24, 5))
        ttk.Spinbox(manager_bar, from_=1, to=6, width=4, textvariable=self.parallel_downloads, command=self._settings_changed).pack(side="left")
        ttk.Label(manager_bar, text=self.tr("fragments")).pack(side="left", padx=(16, 5))
        ttk.Spinbox(manager_bar, from_=1, to=16, width=4, textvariable=self.fragments, command=self._settings_changed).pack(side="left")

        columns = ("titulo", "calidad", "tamano", "estado", "progreso", "velocidad", "restante")
        self.tree = ttk.Treeview(self.manager_frame, columns=columns, show="headings", selectmode="extended", height=10)
        labels = {"titulo": self.tr("col.video"), "calidad": self.tr("col.format"), "tamano": self.tr("col.size"), "estado": self.tr("col.status"), "progreso": self.tr("col.progress"), "velocidad": self.tr("col.speed"), "restante": self.tr("col.remaining")}
        self.column_labels = labels
        widths = {"titulo": 390, "calidad": 105, "tamano": 100, "estado": 110, "progreso": 85, "velocidad": 100, "restante": 80}
        for name in columns:
            self.tree.heading(name, text=labels[name], command=lambda column=name: self.sort_by(column))
            self.tree.column(name, width=widths[name], minwidth=70, anchor="w" if name == "titulo" else "center")
        self.tree.pack(fill="both", expand=True)

        queue_buttons = ttk.Frame(self.manager_frame)
        queue_buttons.pack(fill="x", pady=(8, 8))
        ttk.Button(queue_buttons, text=self.tr("pause.selected"), command=self.pause_selected).pack(side="left")
        ttk.Button(queue_buttons, text=self.tr("resume.selected"), command=self.resume_selected).pack(side="left", padx=6)
        ttk.Button(queue_buttons, text=self.tr("cancel"), command=self.cancel_selected).pack(side="left")
        ttk.Button(queue_buttons, text=self.tr("clear.completed"), command=self.clear_completed).pack(side="left", padx=6)
        ttk.Button(queue_buttons, text=self.tr("open"), command=self.open_folder).pack(side="right")

        ttk.Label(self.manager_frame, text=self.tr("activity"), style="Hint.TLabel").pack(anchor="w")
        self.log = tk.Text(self.manager_frame, height=4, bg="#0b1220", fg="#cbd5e1", insertbackground="white", relief="flat", font=("Consolas", 9), wrap="word")
        self.log.pack(fill="x", pady=(3, 0))
        self.log.configure(state="disabled")

        self.progress_bar = ttk.Progressbar(root, variable=self.progress, maximum=100)
        self.progress_bar.pack(fill="x", pady=(4, 5))
        ttk.Label(root, textvariable=self.status).pack(anchor="w")
        ttk.Label(root, text="DUPUY+SOLUTIONS", style="Footer.TLabel").pack(side="bottom", anchor="e", pady=(5, 0))
        self.url_entry.focus_set()

    def toggle_compact(self):
        self.compact = not self.compact
        if self.compact:
            self.manager_frame.pack_forget()
            self.subtitle.pack_forget()
            self.geometry("760x430")
            self.compact_btn.configure(text=self.tr("view.full"))
        else:
            self.manager_frame.pack(fill="both", expand=True, before=self.progress_bar)
            self.subtitle.pack(anchor="w", pady=(2, 16), before=self.input_frame)
            self.geometry("1120x720")
            self.compact_btn.configure(text=self.tr("view.compact"))

    def toggle_maximize(self):
        try:
            self.state("normal" if self.state() == "zoomed" else "zoomed")
        except tk.TclError:
            self.attributes("-zoomed", not self.attributes("-zoomed"))
        self.after(50, lambda: self.maximize_btn.configure(text=self.tr("restore") if self.state() == "zoomed" else self.tr("maximize")))

    def change_language(self, _event=None):
        selected = next((code for code, label in LANGUAGES.items() if label == self.language_display.get()), "es")
        if selected == self.language_code.get():
            return
        self.language_code.set(selected)
        self.translator.set_language(selected)
        self.tr = self.translator.tr
        self.kind_display.set(self.tr("format.audio") if self.kind.get() == "audio" else self.tr("format.video"))
        self.quality_display.set(self.tr("quality.best") if self.quality.get() == "best" else self._quality_label(self.quality.get()))
        self.status.set(self.tr("status.ready"))
        was_compact = self.compact
        self.compact = False
        self.root_frame.destroy()
        self._build_ui()
        for task in self.tasks.values():
            self._upsert_task(task)
        if was_compact:
            self.toggle_compact()
        self._save_state()

    @staticmethod
    def _quality_label(code):
        labels = {"4320": "4320p (8K)", "2160": "2160p (4K)", "1440": "1440p (2K)", "1080": "1080p", "720": "720p", "480": "480p"}
        return labels.get(str(code), "1080p")

    def _kind_changed(self, _event=None):
        self.kind.set("audio" if self.kind_display.get() == self.tr("format.audio") else "video")
        self._toggle_quality()

    def _quality_changed(self, _event=None):
        displayed = self.quality_display.get()
        if displayed == self.tr("quality.best"):
            self.quality.set("best")
            return
        match = re.match(r"(\d+)p", displayed)
        if match:
            self.quality.set(match.group(1))

    def _toggle_quality(self, _event=None):
        self.quality_box.configure(state="disabled" if self.kind.get() == "audio" else "readonly")

    def paste_url(self):
        try:
            self.url.set(self.clipboard_get().strip())
        except tk.TclError:
            messagebox.showinfo(APP_NAME, self.tr("clipboard.empty"))

    def choose_folder(self):
        selected = filedialog.askdirectory(initialdir=self.folder.get())
        if selected:
            self.folder.set(selected)

    def open_folder(self):
        folder = Path(self.folder.get()).expanduser()
        folder.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            os.startfile(str(folder))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(folder)])
        else:
            subprocess.Popen(["xdg-open", str(folder)])

    def open_recorder(self):
        ScreenRecorder(self, self.folder.get(), Translator(self.language_code.get()))

    def _settings_changed(self):
        self._save_state()
        self._schedule()

    def _engine(self):
        local = Path(sys.executable).resolve().parent / "yt-dlp.exe"
        if local.exists():
            return str(local)
        return shutil.which("yt-dlp") or shutil.which("yt-dlp.exe")

    def _command(self, task):
        engine = self._engine()
        if not engine:
            raise RuntimeError(self.tr("engine.missing"))
        out = str(Path(task["folder"]).expanduser() / "%(title).180B [%(id)s].%(ext)s")
        cmd = [
            engine,
            "--newline",
            "--windows-filenames",
            "--no-overwrites",
            "--continue",
            "--progress",
            "--retries", "infinite",
            "--fragment-retries", "infinite",
            "--retry-sleep", "exp=1:30",
            "--socket-timeout", "30",
            "--concurrent-fragments", str(max(1, min(16, int(self.fragments.get())))),
            "--print", "before_dl:ZEO_META|%(resolution)s|%(filesize_approx)s",
            "-o", out,
        ]
        hostname = (urlparse(task["url"]).hostname or "").lower()
        if hostname == "xfree.com" or hostname.endswith(".xfree.com"):
            # xfree.com protects its public page with TLS/browser fingerprinting.
            # yt-dlp's official Windows build includes curl_cffi for this mode.
            cmd += ["--extractor-args", "generic:impersonate"]
        cmd += ["--yes-playlist" if task["playlist"] else "--no-playlist"]
        if task["kind"] == "audio":
            cmd += ["-x", "--audio-format", "mp3", "--audio-quality", "0"]
        else:
            limits = {
                "best": None, "4320": 4320, "2160": 2160, "1440": 1440,
                "1080": 1080, "720": 720, "480": 480,
            }
            height = limits.get(str(task["quality"]))
            selector = "bv*+ba/b" if height is None else f"bv*[height<={height}]+ba/b[height<={height}]"
            cmd += ["-f", selector, "--merge-output-format", "mp4", "--remux-video", "mp4"]
        cmd.append(task["url"])
        return cmd

    def add_download(self, url=None):
        url = (url or self.url.get()).strip()
        if not re.match(r"^https?://", url, re.I):
            messagebox.showwarning(APP_NAME, self.tr("url.invalid"))
            return
        folder = Path(self.folder.get()).expanduser()
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))
            return
        task_id = uuid.uuid4().hex
        task = {
            "id": task_id, "url": url, "title": url, "folder": str(folder),
            "kind": self.kind.get(), "quality": self.quality.get(), "playlist": bool(self.playlist.get()),
            "status": "En cola", "progress": 0.0, "speed": "—", "eta": "—", "size": "—", "resolution": self.tr("resolution.detecting"), "error": "",
        }
        self.tasks[task_id] = task
        self._upsert_task(task)
        self.url.set("")
        self._save_state()
        self._schedule()

    def _schedule(self):
        limit = max(1, min(6, int(self.parallel_downloads.get())))
        for task in list(self.tasks.values()):
            if len(self.processes) + len(self.starting) >= limit:
                break
            if task["status"] == "En cola":
                self._start_task(task)

    def _start_task(self, task):
        try:
            command = self._command(task)
        except Exception as exc:
            task["status"] = "Error"
            task["error"] = str(exc)
            self._upsert_task(task)
            return
        task["status"] = "Iniciando"
        self.starting.add(task["id"])
        self._upsert_task(task)
        threading.Thread(target=self._run_task, args=(task["id"], command), daemon=True).start()

    def _run_task(self, task_id, command):
        try:
            flags = (subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP) if os.name == "nt" else 0
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", startupinfo=startupinfo(), creationflags=flags)
            self.processes[task_id] = process
            self.starting.discard(task_id)
            self.events.put(("task_status", (task_id, "Descargando")))
            for line in process.stdout:
                line = line.rstrip()
                self.events.put(("task_log", (task_id, line)))
                metadata = re.search(r"ZEO_META\|([^|]+)\|([^|]+)", line)
                if metadata:
                    resolution = metadata.group(1).strip().replace("x", "×")
                    raw_size = metadata.group(2).strip()
                    size = self._format_bytes(raw_size) if raw_size.isdigit() else None
                    self.events.put(("task_meta", (task_id, resolution, size)))
                destination = re.search(r"\[download\] Destination: (.+)$", line)
                if destination:
                    self.events.put(("task_title", (task_id, Path(destination.group(1)).name)))
                match = re.search(r"\[download\]\s+([\d.]+)%.*?at\s+([^\s]+).*?ETA\s+([^\s]+)", line)
                if match:
                    size_match = re.search(r"\bof\s+~?\s*([^\s]+)", line)
                    size = size_match.group(1) if size_match else None
                    self.events.put(("task_progress", (task_id, float(match.group(1)), match.group(2), match.group(3), size)))
            code = process.wait()
            self.events.put(("task_done", (task_id, code)))
        except Exception as exc:
            self.events.put(("task_error", (task_id, str(exc))))
        finally:
            self.processes.pop(task_id, None)
            self.starting.discard(task_id)

    def _selected_ids(self):
        selected = list(self.tree.selection()) if hasattr(self, "tree") else []
        if selected:
            return selected
        active = [t["id"] for t in self.tasks.values() if t["status"] in ("Descargando", "Iniciando")]
        return active[:1]

    @staticmethod
    def _stop_download_process(process):
        if not process or process.poll() is not None:
            return
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                startupinfo=startupinfo(), creationflags=subprocess.CREATE_NO_WINDOW,
            )
        else:
            process.terminate()

    def pause_selected(self):
        for task_id in self._selected_ids():
            task = self.tasks.get(task_id)
            if not task:
                continue
            process = self.processes.get(task_id)
            if process and process.poll() is None:
                self.pause_requested.add(task_id)
                task["status"] = "Pausando"
                self._stop_download_process(process)
            elif task["status"] == "En cola":
                task["status"] = "Pausada"
            self._upsert_task(task)
        self._save_state()

    def resume_selected(self):
        for task_id in self._selected_ids():
            task = self.tasks.get(task_id)
            if task and task["status"] in ("Pausada", "Error", "Interrumpida"):
                task["status"] = "En cola"
                task["error"] = ""
                self._upsert_task(task)
        self._save_state()
        self._schedule()

    def cancel_selected(self):
        for task_id in self._selected_ids():
            task = self.tasks.get(task_id)
            if not task:
                continue
            process = self.processes.get(task_id)
            if process and process.poll() is None:
                task["status"] = "Cancelada"
                self._stop_download_process(process)
            else:
                task["status"] = "Cancelada"
            self._upsert_task(task)
        self._save_state()

    def clear_completed(self):
        for task_id in list(self.tasks):
            if self.tasks[task_id]["status"] in ("Terminada", "Cancelada"):
                self.tasks.pop(task_id)
                self.tree.delete(task_id)
        self._save_state()

    def update_engine(self):
        engine = self._engine()
        if not engine:
            messagebox.showerror(APP_NAME, self.tr("installer.first"))
            return
        self.status.set(self.tr("status.updating"))
        threading.Thread(target=self._run_update, args=(engine,), daemon=True).start()

    def _run_update(self, engine):
        result = subprocess.run([engine, "-U"], capture_output=True, text=True, encoding="utf-8", errors="replace", startupinfo=startupinfo(), creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        self.events.put(("log", (result.stdout + result.stderr).strip()))
        self.events.put(("status", self.tr("status.updated") if result.returncode == 0 else self.tr("status.update_failed")))

    def _upsert_task(self, task):
        file_format = self.tr("format.audio") if task.get("kind") == "audio" else task.get("resolution", self.tr("resolution.detecting"))
        state_keys = {
            "En cola": "state.queued", "Iniciando": "state.starting", "Descargando": "state.downloading",
            "Pausando": "state.pausing", "Pausada": "state.paused", "Interrumpida": "state.interrupted",
            "Error": "state.error", "Cancelada": "state.cancelled", "Terminada": "state.done",
        }
        display_state = self.tr(state_keys.get(task["status"], "state.error"))
        values = (task["title"], file_format, task.get("size", "—"), display_state, f'{task["progress"]:.1f}%', task["speed"], task["eta"])
        if self.tree.exists(task["id"]):
            self.tree.item(task["id"], values=values)
        else:
            self.tree.insert("", "end", iid=task["id"], values=values)
        active = [t["progress"] for t in self.tasks.values() if t["status"] in ("Descargando", "Iniciando", "Pausando")]
        self.progress.set(sum(active) / len(active) if active else 0)
        if self.active_sort:
            ordered = sorted(self.tasks.values(), key=lambda item: self._sort_key(item, self.active_sort), reverse=self.sort_reverse[self.active_sort])
            for position, item in enumerate(ordered):
                if self.tree.exists(item["id"]):
                    self.tree.move(item["id"], "", position)

    @staticmethod
    def _format_bytes(value):
        try:
            number = float(value)
        except (TypeError, ValueError):
            return "—"
        units = ("B", "KB", "MB", "GB", "TB")
        unit = 0
        while number >= 1024 and unit < len(units) - 1:
            number /= 1024
            unit += 1
        return f"{number:.2f} {units[unit]}"

    @staticmethod
    def _scaled_number(value):
        text = str(value).replace("~", "").replace("/s", "").strip().upper()
        match = re.search(r"([\d.,]+)\s*([KMGT]?I?B)?", text)
        if not match:
            return -1.0
        number = float(match.group(1).replace(",", "."))
        unit = (match.group(2) or "B").replace("IB", "B")
        powers = {"B": 0, "KB": 1, "MB": 2, "GB": 3, "TB": 4}
        return number * (1024 ** powers.get(unit, 0))

    @staticmethod
    def _time_seconds(value):
        try:
            parts = [int(part) for part in str(value).split(":")]
            result = 0
            for part in parts:
                result = result * 60 + part
            return result
        except ValueError:
            return -1

    def _sort_key(self, task, column):
        if column == "titulo":
            return task.get("title", "").lower()
        if column == "calidad":
            match = re.search(r"(\d+)\s*[×x]\s*(\d+)", task.get("resolution", ""))
            return int(match.group(1)) * int(match.group(2)) if match else -1
        if column == "tamano":
            return self._scaled_number(task.get("size", "—"))
        if column == "estado":
            order = {"En cola": 0, "Iniciando": 1, "Descargando": 2, "Pausando": 3, "Pausada": 4, "Interrumpida": 5, "Error": 6, "Cancelada": 7, "Terminada": 8}
            return order.get(task.get("status"), 99)
        if column == "progreso":
            return float(task.get("progress", 0))
        if column == "velocidad":
            return self._scaled_number(task.get("speed", "—"))
        if column == "restante":
            return self._time_seconds(task.get("eta", "—"))
        return 0

    def sort_by(self, column):
        reverse = not self.sort_reverse.get(column, True)
        self.sort_reverse[column] = reverse
        self.active_sort = column
        for name, label in self.column_labels.items():
            arrow = " ▼" if name == column and reverse else " ▲" if name == column else ""
            self.tree.heading(name, text=label + arrow, command=lambda selected=name: self.sort_by(selected))
        ordered = sorted(self.tasks.values(), key=lambda task: self._sort_key(task, column), reverse=reverse)
        for position, task in enumerate(ordered):
            if self.tree.exists(task["id"]):
                self.tree.move(task["id"], "", position)

    def _save_state(self):
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            data = {"language": self.language_code.get(), "parallel": int(self.parallel_downloads.get()), "fragments": int(self.fragments.get()), "tasks": list(self.tasks.values())}
            temp = self.state_file.with_suffix(".tmp")
            temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            temp.replace(self.state_file)
        except (OSError, ValueError):
            pass

    def _load_state(self):
        if not self.state_file.exists():
            return
        try:
            data = json.loads(self.state_file.read_text(encoding="utf-8"))
            self.parallel_downloads.set(max(1, min(6, int(data.get("parallel", 3)))))
            self.fragments.set(max(1, min(16, int(data.get("fragments", 8)))))
            for task in data.get("tasks", []):
                old_kind = task.get("kind")
                task["kind"] = "audio" if old_kind in ("audio", "Audio MP3") else "video"
                old_quality = str(task.get("quality", "best"))
                quality_migration = {
                    "Máxima disponible": "best", "4320p (8K)": "4320", "2160p (4K)": "2160",
                    "1440p (2K)": "1440", "1080p": "1080", "720p": "720", "480p": "480",
                }
                task["quality"] = quality_migration.get(old_quality, old_quality if old_quality in ("best", "4320", "2160", "1440", "1080", "720", "480") else "best")
                task.setdefault("size", "—")
                task.setdefault("resolution", self.tr("format.audio") if task.get("kind") == "audio" else self.tr("resolution.pending"))
                if task.get("status") in ("Descargando", "Iniciando", "Pausando", "En cola"):
                    task["status"] = "Interrumpida"
                self.tasks[task["id"]] = task
                self._upsert_task(task)
            if self.tasks:
                self.status.set(self.tr("status.recovered"))
        except (OSError, ValueError, KeyError, TypeError):
            self.status.set(self.tr("status.read_failed"))

    def _close_app(self):
        active = [p for p in self.processes.values() if p.poll() is None]
        if active and not messagebox.askyesno(APP_NAME, self.tr("close.active")):
            return
        for process in active:
            self._stop_download_process(process)
        for task in self.tasks.values():
            if task["status"] in ("Descargando", "Iniciando", "Pausando"):
                task["status"] = "Interrumpida"
        self._save_state()
        self.destroy()

    def _append_log(self, text):
        self.recent_log.append(text)
        self.recent_log = self.recent_log[-80:]
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _friendly_error(self):
        detail = "\n".join(self.recent_log).lower()
        if "http error 403" in detail or "403: forbidden" in detail:
            return self.tr("error.403")
        if "drm" in detail:
            return self.tr("error.drm")
        if "private video" in detail or "login required" in detail or "sign in" in detail:
            return self.tr("error.private")
        if "not available in your country" in detail or "geo restricted" in detail:
            return self.tr("error.geo")
        if "no active stream" in detail or "stream is offline" in detail:
            return self.tr("error.offline")
        if "unsupported url" in detail:
            return self.tr("error.unsupported")
        if "no impersonate target" in detail:
            return self.tr("error.impersonate")
        return self.tr("error.default")

    def _drain_events(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "log":
                    self._append_log(value)
                elif kind == "status":
                    self.status.set(value)
                elif kind == "external_url":
                    self.deiconify()
                    self.lift()
                    self.focus_force()
                    self.add_download(value)
                    self.status.set(self.tr("status.extension"))
                elif kind == "task_status":
                    task_id, state = value
                    if task_id in self.tasks:
                        self.tasks[task_id]["status"] = state
                        self._upsert_task(self.tasks[task_id])
                elif kind == "task_title":
                    task_id, title = value
                    if task_id in self.tasks:
                        self.tasks[task_id]["title"] = title
                        self._upsert_task(self.tasks[task_id])
                elif kind == "task_meta":
                    task_id, resolution, size = value
                    if task_id in self.tasks:
                        task = self.tasks[task_id]
                        if resolution and resolution.upper() not in ("NA", "NONE"):
                            task["resolution"] = resolution
                        if size:
                            task["size"] = size
                        self._upsert_task(task)
                        self._save_state()
                elif kind == "task_progress":
                    task_id, percent, speed, eta, size = value
                    if task_id in self.tasks:
                        task = self.tasks[task_id]
                        task.update(progress=percent, speed=speed, eta=eta, status="Descargando")
                        if size:
                            task["size"] = size
                        self._upsert_task(task)
                        self.status.set(self.tr("status.active", count=len(self.processes)))
                        self._save_state()
                elif kind == "task_log":
                    task_id, line = value
                    self._append_log(f"[{task_id[:6]}] {line}")
                elif kind == "task_done":
                    task_id, code = value
                    task = self.tasks.get(task_id)
                    if task:
                        if task_id in self.pause_requested:
                            self.pause_requested.discard(task_id)
                            task["status"] = "Pausada"
                        elif task["status"] == "Cancelada":
                            pass
                        elif code == 0:
                            task.update(status="Terminada", progress=100.0, speed="—", eta="—")
                        else:
                            task["status"] = "Error"
                            task["error"] = self._friendly_error()
                        self._upsert_task(task)
                        self._save_state()
                    self.after(100, self._schedule)
                elif kind == "task_error":
                    task_id, error = value
                    task = self.tasks.get(task_id)
                    if task:
                        task["status"] = "Error"
                        task["error"] = error
                        self._upsert_task(task)
                        self._save_state()
                    self.after(100, self._schedule)
        except queue.Empty:
            pass
        self.after(100, self._drain_events)


if __name__ == "__main__":
    DownloaderApp().mainloop()
