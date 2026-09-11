import re
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

from tkinter import messagebox, ttk

from app import DownloaderApp as BaseDownloaderApp


APP_NAME = "Zeo Downloader PRO"
APP_VERSION = "2.0-pro.4"


class DownloaderApp(BaseDownloaderApp):
    """ZEO 2.0 PRO layer over the stable downloader.

    Suno support automates only Suno's visible authenticated Download controls.
    It does not extract hidden media URLs or bypass download allowances.
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
                text="Video + Audio · Suno autenticado · descarga oficial automatizada",
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
            "ZEO abrira Chromium y usara el flujo oficial Download de Suno.\n"
            "La primera vez inicia sesion en esa ventana. ZEO guardara la sesion para la proxima descarga.\n\n"
            "La descarga consume el cupo normal de Suno.\n\n"
            "¿Descargar como MP3 ahora?",
        ):
            self.status.set("Suno detectado · descarga cancelada")
            return

        task_id, folder = self._new_suno_task(url)
        self.url.set("")
        self.status.set("Suno · abriendo Chromium…")
        threading.Thread(
            target=self._run_suno_official_download,
            args=(task_id, url, folder),
            daemon=True,
        ).start()

    @staticmethod
    def _visible(locator):
        try:
            count = locator.count()
        except Exception:
            return []
        result = []
        for index in range(min(count, 40)):
            item = locator.nth(index)
            try:
                if item.is_visible() and item.is_enabled():
                    result.append(item)
            except Exception:
                pass
        return result

    def _save_suno_session(self, context, auth_file: Path):
        try:
            context.storage_state(path=str(auth_file), indexed_db=True)
        except TypeError:
            try:
                context.storage_state(path=str(auth_file))
            except Exception:
                pass
        except Exception:
            pass

    def _try_click_suno_download(self, page):
        """Try Suno's visible Download controls only. Return True if clicked."""
        try:
            direct = self._visible(
                page.locator("button, a, [role='button'], [role='menuitem'], [role='option']")
                .filter(has_text=re.compile(r"download", re.I))
            )
            for item in direct[:6]:
                try:
                    item.click(timeout=1500)
                    page.wait_for_timeout(500)
                    mp3 = self._visible(
                        page.locator("button, a, [role='button'], [role='menuitem'], [role='option']")
                        .filter(has_text=re.compile(r"mp3", re.I))
                    )
                    if mp3:
                        mp3[0].click(timeout=1500)
                    return True
                except Exception:
                    pass
        except Exception:
            pass

        candidate_selectors = [
            "button[aria-label*='More']",
            "button[aria-label*='more']",
            "button[title*='More']",
            "button[title*='more']",
            "button[data-testid*='more']",
            "button[data-testid*='menu']",
            "button[data-testid*='action']",
            "[role='button'][aria-haspopup='menu']",
        ]

        candidates = []
        for selector in candidate_selectors:
            try:
                candidates.extend(self._visible(page.locator(selector)))
            except Exception:
                pass
        try:
            candidates.extend(
                self._visible(page.get_by_role("button", name=re.compile(r"^(…|⋯|\.\.\.)$")))
            )
        except Exception:
            pass

        seen = set()
        unique = []
        for item in candidates:
            try:
                key = str(item)
            except Exception:
                key = id(item)
            if key not in seen:
                seen.add(key)
                unique.append(item)

        for more in unique[:24]:
            try:
                more.click(timeout=1500)
                page.wait_for_timeout(400)
                downloads = self._visible(
                    page.locator("button, a, [role='button'], [role='menuitem'], [role='option']")
                    .filter(has_text=re.compile(r"download", re.I))
                )
                if not downloads:
                    page.keyboard.press("Escape")
                    continue
                downloads[0].click(timeout=1500)
                page.wait_for_timeout(500)
                mp3 = self._visible(
                    page.locator("button, a, [role='button'], [role='menuitem'], [role='option']")
                    .filter(has_text=re.compile(r"mp3", re.I))
                )
                if mp3:
                    mp3[0].click(timeout=1500)
                return True
            except Exception:
                try:
                    page.keyboard.press("Escape")
                except Exception:
                    pass
        return False

    def _run_suno_official_download(self, task_id: str, url: str, folder: Path):
        browser = None
        context = None
        playwright = None
        try:
            try:
                from playwright.sync_api import sync_playwright
            except ImportError:
                raise RuntimeError(
                    "Playwright no esta instalado. Ejecuta INSTALAR_ZEO_2_PRO.bat y vuelve a abrir ZEO."
                )

            folder = folder.resolve()
            auth_file = self.state_dir / "suno_auth.json"
            self.state_dir.mkdir(parents=True, exist_ok=True)

            self.events.put(("log", "Suno: iniciando Chromium limpio…"))
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(
                headless=False,
                args=["--start-maximized"],
            )

            context_kwargs = {
                "accept_downloads": True,
                "viewport": None,
            }
            if auth_file.exists():
                context_kwargs["storage_state"] = str(auth_file)
                self.events.put(("log", "Suno: restaurando sesion guardada."))

            try:
                context = browser.new_context(**context_kwargs)
            except Exception:
                # If Suno changed/invalidated the saved auth state, retry clean.
                context_kwargs.pop("storage_state", None)
                context = browser.new_context(**context_kwargs)

            page = context.new_page()
            downloaded_path = {"path": None}
            download_event = threading.Event()

            def on_download(download):
                try:
                    suggested = download.suggested_filename or f"suno_{int(time.time())}.mp3"
                    destination = folder / suggested
                    download.save_as(str(destination))
                    downloaded_path["path"] = destination
                    download_event.set()
                    self.events.put(("log", f"Suno: archivo recibido → {destination.name}"))
                except Exception as exc:
                    self.events.put(("log", f"Suno: no se pudo guardar la descarga: {exc}"))

            page.on("download", on_download)
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            self.events.put(("task_status", (task_id, "Descargando")))
            self.events.put(("status", "Suno · Chromium abierto"))
            self.events.put(("log", "Suno: si aparece Login, inicia sesion en esta ventana. ZEO esperara."))

            auto_clicked = False
            deadline = time.time() + 120
            last_session_save = 0
            while time.time() < deadline and not download_event.is_set():
                if time.time() - last_session_save > 5:
                    self._save_suno_session(context, auth_file)
                    last_session_save = time.time()
                if not auto_clicked:
                    auto_clicked = self._try_click_suno_download(page)
                    if auto_clicked:
                        self.events.put(("log", "Suno: ZEO acciono el control oficial Download."))
                page.wait_for_timeout(1000)

            if not download_event.is_set():
                self.events.put(("log", "Suno: modo asistido. Pulsa manualmente ⋯ > Download > MP3 en Chromium."))
                self.events.put(("status", "Suno · pulsa Download > MP3 en Chromium"))
                self.after(0, lambda: messagebox.showinfo(
                    APP_NAME,
                    "ZEO no identifico automaticamente el menu actual de Suno.\n\n"
                    "En la ventana Chromium pulsa:\n\n"
                    "⋯  →  Download  →  MP3\n\n"
                    "Deja ZEO abierto. Capturara y guardara el archivo automaticamente.",
                ))

                assisted_deadline = time.time() + 300
                while time.time() < assisted_deadline and not download_event.is_set():
                    self._save_suno_session(context, auth_file)
                    page.wait_for_timeout(1000)

            self._save_suno_session(context, auth_file)

            if not download_event.is_set() or not downloaded_path["path"]:
                raise RuntimeError("No se detecto una descarga de audio de Suno en el tiempo disponible.")

            path = downloaded_path["path"]
            self._finish_suno_task(task_id, path)

        except Exception as exc:
            message = str(exc)
            self.events.put(("log", f"Suno ERROR: {message}"))
            self.events.put(("task_error", (task_id, message)))
            self.events.put(("status", f"Suno ERROR · {message[:100]}"))
            self.after(0, lambda m=message: messagebox.showerror(
                APP_NAME,
                "La descarga de Suno no pudo completarse.\n\n"
                "Detalle tecnico:\n" + m,
            ))
        finally:
            try:
                if context is not None:
                    context.close()
            except Exception:
                pass
            try:
                if browser is not None:
                    browser.close()
            except Exception:
                pass
            try:
                if playwright is not None:
                    playwright.stop()
            except Exception:
                pass

    def _finish_suno_task(self, task_id, downloaded: Path):
        task = self.tasks.get(task_id)
        if task:
            try:
                task["title"] = downloaded.name
                task["size"] = self._format_bytes(downloaded.stat().st_size)
                task["resolution"] = downloaded.suffix.upper().lstrip(".")
            except OSError:
                pass
        self.events.put(("log", f"Suno: descarga terminada → {downloaded}"))
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
