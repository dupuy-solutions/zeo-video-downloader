import re
import webbrowser
from urllib.parse import urlparse

from tkinter import messagebox, ttk

from app import DownloaderApp as BaseDownloaderApp


APP_NAME = "Zeo Downloader PRO"
APP_VERSION = "2.0-pro"


class DownloaderApp(BaseDownloaderApp):
    """ZEO 2.0 PRO layer over the stable 1.9 engine.

    The PRO layer keeps the mature download/queue/recorder implementation from
    app.py and adds platform awareness and a safer workflow for services that
    require their own authenticated download flow (currently Suno).
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
        if host:
            return host.removeprefix("www.")
        return "unknown"

    @staticmethod
    def _suno_song_id(url: str):
        match = re.search(r"suno\.com/song/([0-9a-f-]{36})", url, re.I)
        return match.group(1) if match else None

    def _build_ui(self):
        super()._build_ui()

        # Make PRO identity visible without disturbing the stable 1.9 layout.
        try:
            pro_bar = ttk.Frame(self.input_frame)
            pro_bar.pack(fill="x", pady=(0, 10), before=self.input_frame.winfo_children()[1])
            ttk.Label(pro_bar, text="ZEO 2.0 PRO", style="Title.TLabel").pack(side="left")
            ttk.Label(
                pro_bar,
                text="Video + Audio · detección de plataforma · flujo Suno seguro",
                style="Hint.TLabel",
            ).pack(side="left", padx=(12, 0))
        except Exception:
            pass

    def _handle_suno(self, url: str):
        song_id = self._suno_song_id(url)
        self.url.set(url)
        self.kind.set("audio")
        try:
            self.kind_display.set(self.tr("format.audio"))
            self._toggle_quality()
        except Exception:
            pass

        detail = ""
        if song_id:
            detail = f"\n\nCanción detectada: {song_id}"

        answer = messagebox.askyesno(
            APP_NAME,
            "Suno detectado.\n\n"
            "Suno requiere usar su propio flujo autenticado para descargar. "
            "ZEO no intentará saltarse sus límites o protección.\n\n"
            "¿Quieres abrir esta canción en Suno para usar Download y luego "
            "seguir trabajando el MP3/WAV con ZEO?"
            + detail,
        )
        if answer:
            webbrowser.open(url)
            self.status.set("Suno abierto · usa Download en Suno y vuelve a ZEO")
        else:
            self.status.set("Suno detectado · enlace conservado")

    def add_download(self, url=None):
        url = (url or self.url.get()).strip()
        if not re.match(r"^https?://", url, re.I):
            messagebox.showwarning(APP_NAME, self.tr("url.invalid"))
            return

        platform = self._platform(url)
        if platform == "suno":
            self._handle_suno(url)
            return

        # Everything else continues through the stable 1.9 engine.
        self.status.set(f"Plataforma detectada: {platform}")
        return super().add_download(url)


if __name__ == "__main__":
    DownloaderApp().mainloop()
