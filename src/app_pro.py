import re
import shutil
import threading
import time
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

from tkinter import messagebox, ttk

from app import DownloaderApp as BaseDownloaderApp


APP_NAME = "Zeo Downloader PRO"
APP_VERSION = "2.0-pro.5"
AUDIO_EXTENSIONS = (".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg")
PARTIAL_EXTENSIONS = (".crdownload", ".part", ".tmp")


class DownloaderApp(BaseDownloaderApp):
    """ZEO 2.0 PRO layer over the stable downloader.

    Suno support intentionally uses the user's normal authenticated browser.
    ZEO opens the song once, watches for the official Suno download, and then
    moves the completed audio file to the selected ZEO destination folder.
    """

    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {APP_VERSION}")
        self.status.set("ZEO 2.0 PRO listo")

    @staticmethod
    def _platform(url: str) -> str:
        try:
            host = (urlparse(url).hostname or "").lower()
        except ValueError:
            return "unknown"
        if host == "suno.com" or host.endswith(".suno.com"):
            return "suno"
        if host in {"youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com"}:
            return "youtube"
        return host.removeprefix("www.") if host else "unknown"

    @staticmethod
    def _suno_song_id(url: str):
        match = re.search(r"suno\.com/song/([0-9a-f-]{36})", url, re.I)
        return match.group(1) if match else None

    def _build_ui(self):
        super()._build_ui()
        try:
            pro_bar = ttk.Frame(self.input_frame)
            pro_bar.pack(fill="x", pady=(0, 10), before=self.input_frame.winfo_children()[1])
            ttk.Label(pro_bar, text="ZEO 2.0 PRO", style="Title.TLabel").pack(side="left")
            ttk.Label(
                pro_bar,
                text="Video + Audio · Suno asistido estable · sin Selenium/Playwright",
                style="Hint.TLabel",
            ).pack(side="left", padx=(12, 0))
        except Exception:
            pass

    def _new_suno_task(self, url: str):
        import uuid

        folder = Path(self.folder.get()).expanduser()
        folder.mkdir(parents=True, exist_ok=True)
        song_id = self._suno_song_id(url) or "cancion"
        task_id = uuid.uuid4().hex
        task = {
            "id": task_id,
            "url": url,
            "title": f"Suno · {song_id}",
            "folder": str(folder),
            "kind": "audio",
            "quality": "mp3",
            "playlist": False,
            "status": "Iniciando",
            "progress": 0.0,
            "speed": "—",
            "eta": "—",
            "size": "—",
            "resolution": "MP3",
            "error": "",
        }
        self.tasks[task_id] = task
        self._upsert_task(task)
        self._save_state()
        return task_id, folder

    @staticmethod
    def _watch_folders(destination: Path):
        folders = []
        for path in (destination, Path.home() / "Downloads"):
            try:
                resolved = path.expanduser().resolve()
                resolved.mkdir(parents=True, exist_ok=True)
                if resolved not in folders:
                    folders.append(resolved)
            except Exception:
                pass
        return folders

    @staticmethod
    def _snapshot(folders):
        result = {}
        for folder in folders:
            try:
                for path in folder.iterdir():
                    if not path.is_file():
                        continue
                    suffix = path.suffix.lower()
                    if suffix not in AUDIO_EXTENSIONS and suffix not in PARTIAL_EXTENSIONS:
                        continue
                    try:
                        stat = path.stat()
                        result[str(path)] = (stat.st_mtime, stat.st_size)
                    except OSError:
                        pass
            except OSError:
                pass
        return result

    @staticmethod
    def _new_completed_audio(folders, before, first_seen):
        now = time.time()
        candidates = []
        for folder in folders:
            try:
                entries = list(folder.iterdir())
            except OSError:
                continue

            # If any relevant browser partial file is still changing, keep waiting.
            for path in entries:
                if not path.is_file() or path.suffix.lower() not in PARTIAL_EXTENSIONS:
                    continue
                try:
                    stat = path.stat()
                except OSError:
                    continue
                old = before.get(str(path))
                if old is None or stat.st_mtime > old[0] + 0.2 or stat.st_size != old[1]:
                    first_seen[str(path)] = (stat.st_size, now)

            for path in entries:
                if not path.is_file() or path.suffix.lower() not in AUDIO_EXTENSIONS:
                    continue
                try:
                    stat = path.stat()
                except OSError:
                    continue
                old = before.get(str(path))
                changed = old is None or stat.st_mtime > old[0] + 0.2 or stat.st_size != old[1]
                if not changed:
                    continue

                key = str(path)
                previous = first_seen.get(key)
                if previous is None:
                    first_seen[key] = (stat.st_size, now)
                    continue

                old_size, seen_at = previous
                if stat.st_size != old_size:
                    first_seen[key] = (stat.st_size, now)
                    continue

                # Size has remained stable long enough to consider download complete.
                if now - seen_at >= 2.0 and stat.st_size > 0:
                    candidates.append((stat.st_mtime, path))

        if not candidates:
            return None
        candidates.sort(reverse=True, key=lambda item: item[0])
        return candidates[0][1]

    @staticmethod
    def _unique_destination(folder: Path, name: str):
        target = folder / name
        if not target.exists():
            return target
        stem = target.stem
        suffix = target.suffix
        index = 2
        while True:
            candidate = folder / f"{stem} ({index}){suffix}"
            if not candidate.exists():
                return candidate
            index += 1

    def _handle_suno(self, url: str):
        self.url.set(url)
        self.kind.set("audio")
        try:
            self.kind_display.set(self.tr("format.audio"))
            self._toggle_quality()
        except Exception:
            pass

        if not messagebox.askyesno(
            APP_NAME,
            "Suno detectado.\n\n"
            "ZEO abrirá esta canción UNA sola vez en tu navegador normal.\n\n"
            "En Suno pulsa el menú de la canción y luego Download → MP3. "
            "ZEO quedará esperando y detectará el archivo automáticamente.\n\n"
            "¿Continuar?",
        ):
            self.status.set("Suno detectado · cancelado")
            return

        task_id, folder = self._new_suno_task(url)
        self.url.set("")
        threading.Thread(
            target=self._run_suno_assisted_download,
            args=(task_id, url, folder),
            daemon=True,
        ).start()

    def _run_suno_assisted_download(self, task_id: str, url: str, destination: Path):
        try:
            destination = destination.expanduser().resolve()
            watch_folders = self._watch_folders(destination)
            before = self._snapshot(watch_folders)
            first_seen = {}

            self.events.put(("task_status", (task_id, "Descargando")))
            self.events.put(("status", "Suno · esperando descarga oficial"))
            self.events.put(("log", "Suno: abriendo la canción una sola vez en el navegador predeterminado…"))

            opened = webbrowser.open(url, new=2)
            if not opened:
                raise RuntimeError("Windows no pudo abrir el navegador predeterminado.")

            self.after(0, lambda: messagebox.showinfo(
                APP_NAME,
                "Suno ya está abierto en tu navegador.\n\n"
                "Ahora, en Suno, pulsa:\n\n"
                "⋯  →  Download  →  MP3\n\n"
                "ZEO seguirá abierto y detectará automáticamente cuando termine la descarga.",
            ))

            deadline = time.time() + 600
            found = None
            while time.time() < deadline:
                found = self._new_completed_audio(watch_folders, before, first_seen)
                if found:
                    break
                time.sleep(1)

            if not found:
                raise RuntimeError("No se detectó ningún MP3/WAV nuevo de Suno en 10 minutos.")

            final_path = found
            if found.parent.resolve() != destination:
                target = self._unique_destination(destination, found.name)
                try:
                    shutil.move(str(found), str(target))
                    final_path = target
                except Exception as exc:
                    self.events.put(("log", f"Suno: descargado en {found}; no se pudo mover: {exc}"))
                    final_path = found

            self._finish_suno_task(task_id, final_path)

        except Exception as exc:
            message = str(exc)
            self.events.put(("log", f"Suno ERROR: {message}"))
            self.events.put(("task_error", (task_id, message)))
            self.events.put(("status", f"Suno ERROR · {message[:100]}"))
            self.after(0, lambda m=message: messagebox.showerror(
                APP_NAME,
                "La descarga de Suno no pudo completarse.\n\n" + m,
            ))

    def _finish_suno_task(self, task_id, downloaded: Path):
        task = self.tasks.get(task_id)
        if task:
            try:
                task["title"] = downloaded.name
                task["size"] = self._format_bytes(downloaded.stat().st_size)
                task["resolution"] = downloaded.suffix.upper().lstrip(".")
            except OSError:
                pass
        self.events.put(("log", f"Suno: descarga detectada → {downloaded}"))
        self.events.put(("task_done", (task_id, 0)))
        self.events.put(("status", f"Suno descargado: {downloaded.name}"))

    def add_download(self, url=None):
        url = (url or self.url.get()).strip()
        if not re.match(r"^https?://", url, re.I):
            messagebox.showwarning(APP_NAME, self.tr("url.invalid"))
            return

        platform = self._platform(url)
        if platform == "suno":
            self._handle_suno(url)
            return

        self.status.set(f"Plataforma detectada: {platform}")
        return super().add_download(url)


if __name__ == "__main__":
    DownloaderApp().mainloop()
