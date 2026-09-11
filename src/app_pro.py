import re
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

from tkinter import messagebox, ttk

from app import DownloaderApp as BaseDownloaderApp


APP_NAME = "Zeo Downloader PRO"
APP_VERSION = "2.0-pro.3"


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
                text="Video + Audio · Suno autenticado · motor Chromium integrado",
                style="Hint.TLabel",
            ).pack(side="left", padx=(12, 0))
        except Exception:
            pass

    def _new_suno_task(self, url: str):
        import uuid
        folder = Path(self.folder.get()).expanduser()
        folder.mkdir(parents=True, exist_ok=True)
        song_id = self._suno_song_id(url) or "canción"
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
            "ZEO abrirá su navegador Chromium independiente y usará el flujo oficial Download de Suno.\n"
            "La primera vez inicia sesión en esa ventana. La sesión quedará guardada.\n\n"
            "La descarga consume el cupo normal de Suno.\n\n¿Descargar como MP3 ahora?",
        ):
            self.status.set("Suno detectado · descarga cancelada")
            return

        task_id, folder = self._new_suno_task(url)
        self.url.set("")
        self.status.set("Suno · iniciando Chromium…")
        threading.Thread(
            target=self._run_suno_playwright,
            args=(task_id, url, folder),
            daemon=True,
        ).start()

    @staticmethod
    def _first_visible(locator):
        try:
            count = min(locator.count(), 30)
        except Exception:
            return None
        for i in range(count):
            try:
                item = locator.nth(i)
                if item.is_visible() and item.is_enabled():
                    return item
            except Exception:
                pass
        return None

    def _click_visible(self, locator):
        item = self._first_visible(locator)
        if item is None:
            return False
        try:
            item.scroll_into_view_if_needed(timeout=1500)
        except Exception:
            pass
        try:
            item.click(timeout=2500)
            return True
        except Exception:
            try:
                item.evaluate("el => el.click()")
                return True
            except Exception:
                return False

    def _attempt_suno_download_click(self, page):
        """Try Suno's visible controls. Returns True if a Download action was clicked."""
        import re as _re

        # Direct Download button/menu item, if the layout exposes one.
        direct_candidates = [
            page.get_by_role("button", name=_re.compile("download", _re.I)),
            page.get_by_role("menuitem", name=_re.compile("download", _re.I)),
            page.get_by_text(_re.compile(r"^download$", _re.I)),
        ]
        for locator in direct_candidates:
            if self._click_visible(locator):
                time.sleep(0.5)
                mp3 = self._first_visible(page.get_by_text(_re.compile("mp3", _re.I)))
                if mp3 is not None:
                    try:
                        mp3.click(timeout=2500)
                    except Exception:
                        try:
                            mp3.evaluate("el => el.click()")
                        except Exception:
                            pass
                return True

        # Open likely More/ellipsis menus one by one until Download appears.
        more_sets = [
            page.locator('button[aria-label*="more" i]'),
            page.locator('button[title*="more" i]'),
            page.locator('button[aria-haspopup="menu"]'),
            page.locator('button').filter(has_text=_re.compile(r"^(\.\.\.|…|⋯)$")),
        ]

        seen = set()
        candidates = []
        for locator in more_sets:
            try:
                for i in range(min(locator.count(), 30)):
                    el = locator.nth(i)
                    key = None
                    try:
                        key = el.get_attribute("aria-label") or el.get_attribute("data-testid")
                    except Exception:
                        pass
                    key = key or f"{id(locator)}:{i}"
                    if key not in seen:
                        seen.add(key)
                        candidates.append(el)
            except Exception:
                pass

        for more in candidates[:30]:
            try:
                if not more.is_visible() or not more.is_enabled():
                    continue
                try:
                    more.scroll_into_view_if_needed(timeout=1000)
                except Exception:
                    pass
                try:
                    more.click(timeout=2000)
                except Exception:
                    more.evaluate("el => el.click()")
                time.sleep(0.45)

                download = self._first_visible(page.get_by_text(_re.compile(r"^download", _re.I)))
                if download is None:
                    try:
                        page.keyboard.press("Escape")
                    except Exception:
                        pass
                    continue

                try:
                    download.click(timeout=2500)
                except Exception:
                    download.evaluate("el => el.click()")
                time.sleep(0.45)

                mp3 = self._first_visible(page.get_by_text(_re.compile("mp3", _re.I)))
                if mp3 is not None:
                    try:
                        mp3.click(timeout=2500)
                    except Exception:
                        try:
                            mp3.evaluate("el => el.click()")
                        except Exception:
                            pass
                return True
            except Exception:
                try:
                    page.keyboard.press("Escape")
                except Exception:
                    pass
        return False

    def _run_suno_playwright(self, task_id: str, url: str, folder: Path):
        playwright = None
        context = None
        download_done = threading.Event()
        downloaded_path = {"path": None, "error": None}

        try:
            try:
                from playwright.sync_api import sync_playwright
            except ImportError:
                raise RuntimeError(
                    "Falta Playwright. Ejecuta INSTALAR_ZEO_2_PRO.bat de la versión nueva y vuelve a abrir ZEO."
                )

            folder = folder.resolve()
            profile = (self.state_dir / "SunoChromiumProfile").resolve()
            profile.mkdir(parents=True, exist_ok=True)

            self.events.put(("status", "Suno · cargando motor Chromium…"))
            self.events.put(("log", "Suno: iniciando Playwright/Chromium…"))

            playwright = sync_playwright().start()
            try:
                context = playwright.chromium.launch_persistent_context(
                    user_data_dir=str(profile),
                    headless=False,
                    accept_downloads=True,
                    viewport=None,
                    timeout=20000,
                    args=["--start-maximized"],
                )
            except Exception as exc:
                raise RuntimeError(
                    "Chromium no pudo iniciar. Ejecuta INSTALAR_ZEO_2_PRO.bat para instalar el navegador integrado. "
                    f"Detalle: {exc}"
                )

            def on_download(download):
                try:
                    target = folder / download.suggested_filename
                    base = target.stem
                    suffix = target.suffix
                    n = 1
                    while target.exists():
                        target = folder / f"{base} ({n}){suffix}"
                        n += 1
                    download.save_as(str(target))
                    downloaded_path["path"] = target
                except Exception as exc:
                    downloaded_path["error"] = str(exc)
                finally:
                    download_done.set()

            def attach(page):
                try:
                    page.on("download", on_download)
                except Exception:
                    pass

            context.on("page", attach)
            page = context.pages[0] if context.pages else context.new_page()
            attach(page)

            self.events.put(("task_status", (task_id, "Descargando")))
            self.events.put(("status", "Suno · Chromium abierto"))
            self.events.put(("log", "Suno: abriendo canción…"))
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # Give the user time to log in while ZEO repeatedly looks for the visible Download control.
            auto_deadline = time.time() + 60
            action_clicked = False
            while time.time() < auto_deadline and not download_done.is_set():
                try:
                    if self._attempt_suno_download_click(page):
                        action_clicked = True
                        self.events.put(("log", "Suno: control Download accionado."))
                        break
                except Exception:
                    pass
                time.sleep(2)

            if action_clicked and not download_done.is_set():
                self.events.put(("status", "Suno · esperando archivo MP3…"))
                download_done.wait(90)

            if not download_done.is_set():
                # Reliable fallback: keep the controlled browser open and capture the user's official click.
                self.events.put(("status", "Suno · pulsa ⋯ → Download → MP3 en Chromium"))
                self.events.put(("log", "Suno: modo asistido activo; ZEO capturará y guardará la descarga automáticamente."))
                self.after(0, lambda: messagebox.showinfo(
                    APP_NAME,
                    "Suno está abierto en el navegador de ZEO.\n\n"
                    "Si todavía no iniciaste sesión, hazlo ahora. Luego pulsa:\n\n"
                    "⋯  →  Download  →  MP3\n\n"
                    "ZEO detectará la descarga y la guardará automáticamente en la carpeta elegida.",
                ))
                download_done.wait(300)

            if not download_done.is_set():
                raise RuntimeError("No se recibió una descarga de Suno en 5 minutos.")
            if downloaded_path["error"]:
                raise RuntimeError("Suno inició la descarga, pero no pude guardar el archivo: " + downloaded_path["error"])
            if not downloaded_path["path"]:
                raise RuntimeError("Suno inició la descarga, pero ZEO no recibió la ruta del archivo.")

            self._finish_suno_task(task_id, downloaded_path["path"])

        except Exception as exc:
            message = str(exc)
            self.events.put(("log", f"Suno ERROR: {message}"))
            self.events.put(("task_error", (task_id, message)))
            self.events.put(("status", f"Suno ERROR · {message[:110]}"))
            self.after(0, lambda m=message: messagebox.showerror(
                APP_NAME,
                "La descarga de Suno no pudo completarse.\n\nDetalle técnico:\n" + m,
            ))
        finally:
            if context is not None:
                try:
                    context.close()
                except Exception:
                    pass
            if playwright is not None:
                try:
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
