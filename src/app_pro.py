import re
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

from tkinter import messagebox, ttk

from app import DownloaderApp as BaseDownloaderApp


APP_NAME = "Zeo Downloader PRO"
APP_VERSION = "2.0-pro.1"


class DownloaderApp(BaseDownloaderApp):
    """ZEO 2.0 PRO layer over the stable 1.9 engine.

    Suno support uses an authenticated Microsoft Edge session and automates
    Suno's own visible Download controls. It does not extract hidden media URLs
    or bypass Suno download allowances/protections.
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
            "ZEO abrirá Microsoft Edge y usará el botón oficial de descarga de Suno. "
            "La primera vez inicia sesión en Suno dentro de esa ventana. ZEO conservará esa sesión.\n\n"
            "La descarga consume el cupo normal de Suno.\n\n"
            "¿Descargar como MP3 ahora?",
        ):
            self.status.set("Suno detectado · descarga cancelada")
            return

        task_id, folder = self._new_suno_task(url)
        self.url.set("")
        self.status.set("Suno · abriendo sesión autenticada…")
        threading.Thread(
            target=self._run_suno_official_download,
            args=(task_id, url, folder),
            daemon=True,
        ).start()

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

    def _run_suno_official_download(self, task_id: str, url: str, folder: Path):
        driver = None
        try:
            try:
                from selenium import webdriver
                from selenium.webdriver.common.action_chains import ActionChains
                from selenium.webdriver.common.by import By
                from selenium.webdriver.common.keys import Keys
            except ImportError:
                raise RuntimeError(
                    "Falta Selenium. Ejecuta INSTALAR_ZEO_2_PRO.bat una vez y vuelve a abrir ZEO."
                )

            folder = folder.resolve()
            before = {
                p.name: p.stat().st_mtime
                for p in folder.iterdir()
                if p.is_file()
            }

            options = webdriver.EdgeOptions()
            profile_dir = (self.state_dir / "SunoEdgeProfile").resolve()
            profile_dir.mkdir(parents=True, exist_ok=True)
            options.add_argument(f"--user-data-dir={profile_dir}")
            options.add_argument("--start-maximized")
            options.add_experimental_option(
                "prefs",
                {
                    "download.default_directory": str(folder),
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": True,
                },
            )

            self.events.put(("log", "Suno: iniciando Microsoft Edge autenticado…"))
            driver = webdriver.Edge(options=options)
            driver.get(url)
            self.events.put(("task_status", (task_id, "Descargando")))
            self.events.put(("log", "Suno: si aparece Login, inicia sesión una sola vez; ZEO esperará."))

            end = time.time() + 300
            clicked_mp3 = False
            lowercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            lowerdst = "abcdefghijklmnopqrstuvwxyz"

            while time.time() < end and not clicked_mp3:
                try:
                    # Look for visible More Actions / ellipsis buttons. We try each one
                    # until a menu containing Download appears.
                    more_candidates = []
                    selectors = [
                        (By.CSS_SELECTOR, "button[aria-label*='More'], button[aria-label*='more']"),
                        (By.CSS_SELECTOR, "button[title*='More'], button[title*='more']"),
                        (
                            By.XPATH,
                            f"//button[contains(translate(normalize-space(.),'{lowercase}','{lowerdst}'),'more') or normalize-space(.)='…' or normalize-space(.)='⋯' or normalize-space(.)='...']",
                        ),
                    ]
                    for by, selector in selectors:
                        try:
                            more_candidates.extend(self._visible(driver.find_elements(by, selector)))
                        except Exception:
                            pass

                    # Remove duplicates while preserving order.
                    unique = []
                    seen = set()
                    for element in more_candidates:
                        try:
                            key = element.id
                        except Exception:
                            key = id(element)
                        if key not in seen:
                            seen.add(key)
                            unique.append(element)

                    for more in unique[:12]:
                        try:
                            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", more)
                            driver.execute_script("arguments[0].click();", more)
                            time.sleep(0.6)

                            download_items = self._visible(
                                driver.find_elements(
                                    By.XPATH,
                                    f"//*[@role='menuitem' or self::button or @role='button'][contains(translate(normalize-space(.),'{lowercase}','{lowerdst}'),'download')]",
                                )
                            )
                            if not download_items:
                                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                                continue

                            download_item = download_items[0]
                            try:
                                ActionChains(driver).move_to_element(download_item).perform()
                            except Exception:
                                pass
                            time.sleep(0.6)

                            mp3_items = self._visible(
                                driver.find_elements(
                                    By.XPATH,
                                    f"//*[@role='menuitem' or self::button or @role='button'][contains(translate(normalize-space(.),'{lowercase}','{lowerdst}'),'mp3')]",
                                )
                            )
                            if not mp3_items:
                                driver.execute_script("arguments[0].click();", download_item)
                                time.sleep(0.7)
                                mp3_items = self._visible(
                                    driver.find_elements(
                                        By.XPATH,
                                        f"//*[@role='menuitem' or self::button or @role='button'][contains(translate(normalize-space(.),'{lowercase}','{lowerdst}'),'mp3')]",
                                    )
                                )

                            if mp3_items:
                                driver.execute_script("arguments[0].click();", mp3_items[0])
                                clicked_mp3 = True
                                self.events.put(("log", "Suno: MP3 solicitado mediante el menú oficial."))
                                break
                            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                        except Exception:
                            try:
                                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                            except Exception:
                                pass

                    if not clicked_mp3:
                        time.sleep(2)
                except Exception:
                    time.sleep(2)

            if not clicked_mp3:
                raise RuntimeError(
                    "No encontré el botón oficial Download/MP3. Comprueba que iniciaste sesión, "
                    "que la canción es tuya y que tu cuenta tiene descargas disponibles."
                )

            # Some accounts show a final confirmation dialog after choosing MP3.
            # Give it a moment, and if no file starts, click a visible Download/Confirm
            # button inside a dialog only.
            time.sleep(2)
            partial_started = any(folder.glob("*.crdownload"))
            if not partial_started:
                try:
                    dialogs = self._visible(driver.find_elements(By.CSS_SELECTOR, "[role='dialog']"))
                    for dialog in dialogs:
                        buttons = self._visible(
                            dialog.find_elements(
                                By.XPATH,
                                f".//button[contains(translate(normalize-space(.),'{lowercase}','{lowerdst}'),'download') or contains(translate(normalize-space(.),'{lowercase}','{lowerdst}'),'confirm')]",
                            )
                        )
                        if buttons:
                            driver.execute_script("arguments[0].click();", buttons[-1])
                            self.events.put(("log", "Suno: confirmación oficial aceptada."))
                            break
                except Exception:
                    pass

            download_end = time.time() + 180
            downloaded = None
            while time.time() < download_end:
                partial = list(folder.glob("*.crdownload"))
                candidates = []
                for ext in ("*.mp3", "*.wav", "*.m4a"):
                    candidates.extend(folder.glob(ext))
                for path in candidates:
                    try:
                        old_mtime = before.get(path.name)
                        if old_mtime is None or path.stat().st_mtime > old_mtime + 0.5:
                            downloaded = path
                            break
                    except OSError:
                        pass
                if downloaded and not partial:
                    break
                time.sleep(1)

            if not downloaded:
                raise RuntimeError(
                    "Suno aceptó la orden pero ZEO no detectó el MP3 terminado en la carpeta de destino."
                )

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

        except Exception as exc:
            self.events.put(("log", f"Suno ERROR: {exc}"))
            self.events.put(("task_error", (task_id, str(exc))))
            self.events.put(("status", "Suno · descarga no completada"))
        finally:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:
                    pass

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
