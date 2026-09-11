import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

from tkinter import messagebox, ttk

from app import DownloaderApp as BaseDownloaderApp


APP_NAME = "Zeo Downloader PRO"
APP_VERSION = "2.0-pro.2"


class DownloaderApp(BaseDownloaderApp):
    """ZEO 2.0 PRO layer over the stable 1.9 engine.

    Suno support automates only Suno's own visible authenticated Download flow.
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
        song_id = self._suno_song_id(url) or "canción"
        task_id = uuid.uuid4().hex
        task = {
            "id": task_id, "url": url, "title": f"Suno · {song_id}",
            "folder": str(folder), "kind": "audio", "quality": "mp3",
            "playlist": False, "status": "Iniciando", "progress": 0.0,
            "speed": "—", "eta": "—", "size": "—", "resolution": "MP3", "error": "",
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
            "ZEO abrirá un navegador independiente y usará el flujo oficial Download de Suno.\n"
            "Si pide iniciar sesión, hazlo en esa ventana; la sesión quedará guardada.\n\n"
            "La descarga consume el cupo normal de Suno.\n\n¿Descargar como MP3 ahora?",
        ):
            self.status.set("Suno detectado · descarga cancelada")
            return

        task_id, folder = self._new_suno_task(url)
        self.url.set("")
        self.status.set("Suno · preparando navegador…")
        threading.Thread(target=self._run_suno_official_download, args=(task_id, url, folder), daemon=True).start()

    @staticmethod
    def _visible(elements):
        result = []
        for element in elements:
            try:
                if element.is_displayed() and element.is_enabled():
                    result.append(element)
            except Exception:
                pass
        return result

    def _ensure_selenium(self):
        try:
            import selenium  # noqa: F401
            return
        except ImportError:
            pass
        self.events.put(("log", "Suno: Selenium no está instalado; ZEO intentará instalarlo automáticamente…"))
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "selenium"]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode != 0:
            raise RuntimeError("No se pudo instalar Selenium automáticamente. Ejecuta INSTALAR_ZEO_2_PRO.bat y vuelve a intentar.")

    @staticmethod
    def _find_edge_binary():
        candidates = [
            Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft/Edge/Application/msedge.exe",
            Path(os.environ.get("PROGRAMFILES", "")) / "Microsoft/Edge/Application/msedge.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/Edge/Application/msedge.exe",
        ]
        for path in candidates:
            if str(path) and path.exists():
                return str(path)
        return shutil.which("msedge") or shutil.which("msedge.exe")

    @staticmethod
    def _find_chrome_binary():
        candidates = [
            Path(os.environ.get("PROGRAMFILES", "")) / "Google/Chrome/Application/chrome.exe",
            Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Google/Chrome/Application/chrome.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe",
        ]
        for path in candidates:
            if str(path) and path.exists():
                return str(path)
        return shutil.which("chrome") or shutil.which("chrome.exe")

    def _new_browser(self, folder: Path):
        self._ensure_selenium()
        from selenium import webdriver

        folder = folder.resolve()
        prefs = {
            "download.default_directory": str(folder),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        errors = []

        edge_binary = self._find_edge_binary()
        if edge_binary:
            try:
                options = webdriver.EdgeOptions()
                options.binary_location = edge_binary
                profile_dir = (self.state_dir / "SunoEdgeProfile2").resolve()
                profile_dir.mkdir(parents=True, exist_ok=True)
                options.add_argument(f"--user-data-dir={profile_dir}")
                options.add_argument("--start-maximized")
                options.add_experimental_option("prefs", prefs)
                self.events.put(("log", f"Suno: iniciando Edge → {edge_binary}"))
                return webdriver.Edge(options=options), "Edge"
            except Exception as exc:
                errors.append(f"Edge: {exc}")
                self.events.put(("log", f"Suno: Edge no pudo iniciar: {exc}"))

        chrome_binary = self._find_chrome_binary()
        if chrome_binary:
            try:
                options = webdriver.ChromeOptions()
                options.binary_location = chrome_binary
                profile_dir = (self.state_dir / "SunoChromeProfile2").resolve()
                profile_dir.mkdir(parents=True, exist_ok=True)
                options.add_argument(f"--user-data-dir={profile_dir}")
                options.add_argument("--start-maximized")
                options.add_experimental_option("prefs", prefs)
                self.events.put(("log", f"Suno: probando Chrome → {chrome_binary}"))
                return webdriver.Chrome(options=options), "Chrome"
            except Exception as exc:
                errors.append(f"Chrome: {exc}")

        detail = " | ".join(errors[-2:]) if errors else "No se encontró Edge ni Chrome."
        raise RuntimeError(f"No pude iniciar un navegador automatizado. {detail}")

    @staticmethod
    def _snapshot_audio(folder: Path):
        snapshot = {}
        for ext in ("*.mp3", "*.wav", "*.m4a"):
            for path in folder.glob(ext):
                try:
                    snapshot[path.name] = (path.stat().st_mtime, path.stat().st_size)
                except OSError:
                    pass
        return snapshot

    @staticmethod
    def _new_audio_file(folder: Path, before):
        partial = list(folder.glob("*.crdownload"))
        newest = None
        newest_mtime = -1
        for ext in ("*.mp3", "*.wav", "*.m4a"):
            for path in folder.glob(ext):
                try:
                    stat = path.stat()
                    old = before.get(path.name)
                    changed = old is None or stat.st_mtime > old[0] + 0.25 or stat.st_size != old[1]
                    if changed and stat.st_mtime > newest_mtime:
                        newest, newest_mtime = path, stat.st_mtime
                except OSError:
                    pass
        return None if partial else newest

    def _try_click_download(self, driver):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys

        upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        lower = "abcdefghijklmnopqrstuvwxyz"
        def visible(xpath):
            try:
                return self._visible(driver.find_elements(By.XPATH, xpath))
            except Exception:
                return []

        # Some Suno layouts expose Download directly.
        direct = visible(
            f"//*[self::button or self::a or @role='button' or @role='menuitem']"
            f"[contains(translate(normalize-space(.),'{upper}','{lower}'),'download')]"
        )
        for item in direct[:5]:
            try:
                driver.execute_script("arguments[0].click();", item)
                time.sleep(0.8)
                mp3 = visible(
                    f"//*[self::button or self::a or @role='button' or @role='menuitem']"
                    f"[contains(translate(normalize-space(.),'{upper}','{lower}'),'mp3')]"
                )
                if mp3:
                    driver.execute_script("arguments[0].click();", mp3[0])
                return True
            except Exception:
                pass

        selectors = [
            "button[aria-label*='More'],button[aria-label*='more']",
            "button[title*='More'],button[title*='more']",
            "button[data-testid*='more'],button[data-testid*='menu'],button[data-testid*='action']",
            "[role='button'][aria-haspopup='menu']",
        ]
        candidates = []
        for selector in selectors:
            try:
                candidates.extend(self._visible(driver.find_elements(By.CSS_SELECTOR, selector)))
            except Exception:
                pass
        candidates.extend(visible("//button[normalize-space(.)='…' or normalize-space(.)='⋯' or normalize-space(.)='...']"))

        seen = set()
        unique = []
        for element in candidates:
            try:
                key = element.id
            except Exception:
                key = id(element)
            if key not in seen:
                seen.add(key)
                unique.append(element)

        for more in unique[:24]:
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", more)
                driver.execute_script("arguments[0].click();", more)
                time.sleep(0.6)
                downloads = visible(
                    f"//*[self::button or self::a or @role='button' or @role='menuitem' or @role='option']"
                    f"[contains(translate(normalize-space(.),'{upper}','{lower}'),'download')]"
                )
                if not downloads:
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    continue
                driver.execute_script("arguments[0].click();", downloads[0])
                time.sleep(0.7)
                mp3 = visible(
                    f"//*[self::button or self::a or @role='button' or @role='menuitem' or @role='option']"
                    f"[contains(translate(normalize-space(.),'{upper}','{lower}'),'mp3')]"
                )
                if mp3:
                    driver.execute_script("arguments[0].click();", mp3[0])
                return True
            except Exception:
                try:
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                except Exception:
                    pass
        return False

    def _run_suno_official_download(self, task_id: str, url: str, folder: Path):
        driver = None
        try:
            folder = folder.resolve()
            before = self._snapshot_audio(folder)
            driver, browser_name = self._new_browser(folder)
            self.events.put(("task_status", (task_id, "Descargando")))
            self.events.put(("status", f"Suno · {browser_name} abierto"))
            driver.get(url)
            self.events.put(("log", f"Suno: página abierta en {browser_name}. Si aparece Login, inicia sesión allí."))

            clicked = False
            deadline = time.time() + 90
            while time.time() < deadline:
                downloaded = self._new_audio_file(folder, before)
                if downloaded:
                    self._finish_suno_task(task_id, downloaded)
                    return
                if self._try_click_download(driver):
                    clicked = True
                    self.events.put(("log", "Suno: se accionó el control oficial Download."))
                    break
                time.sleep(2)

            # After automatic click, wait for the browser download.
            if clicked:
                finish_deadline = time.time() + 180
                while time.time() < finish_deadline:
                    downloaded = self._new_audio_file(folder, before)
                    if downloaded:
                        self._finish_suno_task(task_id, downloaded)
                        return
                    time.sleep(1)

            # Assisted fallback: browser remains open and ZEO watches Downloads.
            self.events.put(("log", "Suno: modo asistido. En la ventana de Suno pulsa ⋯ > Download > MP3; ZEO detectará el archivo automáticamente."))
            self.events.put(("status", "Suno · pulsa Download > MP3 en la ventana abierta"))
            self.after(0, lambda: messagebox.showinfo(
                APP_NAME,
                "ZEO abrió Suno correctamente, pero no pudo identificar automáticamente el menú actual.\n\n"
                "En la ventana de Suno pulsa:  ⋯  →  Download  →  MP3\n\n"
                "No cierres ZEO: detectará el archivo y marcará la descarga como terminada automáticamente.",
            ))
            assisted_deadline = time.time() + 300
            while time.time() < assisted_deadline:
                downloaded = self._new_audio_file(folder, before)
                if downloaded:
                    self._finish_suno_task(task_id, downloaded)
                    return
                time.sleep(1)
            raise RuntimeError("No se detectó una descarga de audio de Suno en 5 minutos.")

        except Exception as exc:
            message = str(exc)
            self.events.put(("log", f"Suno ERROR: {message}"))
            self.events.put(("task_error", (task_id, message)))
            self.events.put(("status", f"Suno ERROR · {message[:100]}"))
            self.after(0, lambda m=message: messagebox.showerror(
                APP_NAME,
                "La descarga de Suno no pudo iniciarse.\n\nDetalle técnico:\n" + m +
                "\n\nCopia o fotografía este mensaje si vuelve a ocurrir.",
            ))
        finally:
            if driver is not None:
                try:
                    driver.quit()
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
