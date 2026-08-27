import locale


LANGUAGES = {
    "es": "Español",
    "en": "English",
    "pt": "Português",
    "de": "Deutsch",
    "fr": "Français",
    "it": "Italiano",
    "zh": "简体中文",
}


EN = {
    "view.compact": "Compact view", "view.full": "Full view", "maximize": "Maximize", "restore": "Restore",
    "language": "Language", "subtitle": "Persistent multi-download manager · owned or authorized content.",
    "url.label": "Video or webpage URL", "paste": "Paste", "start": "Start", "format": "Format",
    "format.video": "MP4 video", "format.audio": "MP3 audio", "resolution": "Maximum requested resolution",
    "quality.best": "Best available", "playlist": "Playlist", "playlist.all": "Download full playlist",
    "destination": "Destination folder", "choose": "Choose", "open": "Open", "pause": "Pause", "resume": "Resume",
    "record": "Record screen", "update": "Update engine", "monitor": "Download monitor",
    "parallel": "Simultaneous downloads:", "fragments": "Fragments per download:",
    "col.video": "Video / URL", "col.format": "Format", "col.size": "Size", "col.status": "Status",
    "col.progress": "Progress", "col.speed": "Speed", "col.remaining": "Remaining",
    "pause.selected": "Pause selected", "resume.selected": "Resume selected", "cancel": "Cancel",
    "clear.completed": "Remove completed", "activity": "Technical activity", "support": "Support Zeo",
    "support.tip": "Optional contribution via Mercado Pago", "status.ready": "Ready to download",
    "status.recovered": "Previous session recovered. Select a download and press Resume.",
    "status.read_failed": "The previous history could not be read.", "status.extension": "Firefox URL added to the download monitor.",
    "status.active": "{count} active download(s)", "status.updating": "Updating engine…", "status.updated": "Engine updated",
    "status.update_failed": "Update failed", "clipboard.empty": "The clipboard is empty.",
    "url.invalid": "Paste a valid URL beginning with http:// or https://", "engine.missing": "yt-dlp was not found. Run INSTALAR_EN_WINDOWS.bat and reopen the app.",
    "installer.first": "yt-dlp was not found. Run the installer first.",
    "close.active": "Active downloads will be saved so you can resume them later. Close the application?",
    "state.queued": "Queued", "state.starting": "Starting", "state.downloading": "Downloading", "state.pausing": "Pausing",
    "state.paused": "Paused", "state.interrupted": "Interrupted", "state.error": "Error", "state.cancelled": "Cancelled", "state.done": "Completed",
    "resolution.detecting": "Detecting…", "resolution.pending": "Pending",
    "error.403": "The website rejected the download (403 Forbidden). Update the engine and try once more; if it continues, the server does not allow automated downloads for this URL.",
    "error.drm": "This content appears to be DRM protected and Zeo cannot process it.",
    "error.private": "This content is private or requires an account. Use only the website's official option.",
    "error.geo": "This content is region restricted and unavailable from your location.",
    "error.offline": "The public stream is not active right now.", "error.unsupported": "The engine does not recognize this page yet. Update the engine and try again.",
    "error.impersonate": "The official web compatibility component is missing. Run this version's installer again.",
    "error.default": "Could not complete the download. Check the details below and try Update engine.",
    "rec.title": "Record video call", "rec.consent": "Notify every participant before recording.",
    "rec.folder": "Recording folder", "rec.client": "Client", "rec.project": "Project", "rec.topic": "Topic",
    "rec.area": "Recording area", "rec.select_area": "Select area", "rec.fullscreen": "Full screen", "rec.flow": "Frame rate",
    "rec.quality.light": "Light", "rec.quality.balanced": "Balanced", "rec.quality.high": "High", "rec.quality.maximum": "Maximum",
    "rec.limit.none": "No limit", "rec.limit.30": "30 minutes", "rec.limit.60": "60 minutes", "rec.limit.90": "90 minutes", "rec.limit.120": "120 minutes",
    "rec.system_audio": "Computer audio (choose Stereo Mix if available)", "rec.microphone": "Microphone", "rec.no_audio": "No audio",
    "rec.notice": "Everything visible in the selected area, including notifications, will be recorded.",
    "rec.preparing": "Preparing audio devices…", "rec.devices": "{count} audio device(s) detected.",
    "rec.ffmpeg": "FFmpeg is unavailable. Run the installer again.", "rec.area_full": "Full screen",
    "rec.area_custom": "Custom area: {width} × {height} px, position {x}, {y}", "rec.start": "Start recording",
    "rec.stop": "Stop and save", "rec.shot": "Screenshot (F8)", "rec.marker": "Mark moment", "rec.open": "Open folder",
    "rec.ffmpeg_not_found": "FFmpeg was not found. Run INSTALAR_EN_WINDOWS.bat.",
    "rec.confirm": "Do you confirm that you notified the participants and have permission to record?",
    "rec.starts": "Recording starts in 3 seconds…", "rec.countdown": "Starting in {seconds}…",
    "rec.recording": "Recording… return here and press Stop and save.", "rec.finalizing": "Finalizing MP4…",
    "rec.marker_prompt": "Write a note for this moment:", "rec.marker_default": "Marker", "rec.marker_added": "Marker added: {time} – {note}",
    "rec.shot_saved": "Screenshot saved: {name}", "rec.failed": "The recording could not be completed.",
    "rec.audio_hint": "Check that the selected audio device is still connected.",
    "rec.audio_missing": "Windows could not find the selected audio device. Reopen this window to refresh the list.",
    "rec.warning": "The MP4 could not be finalized, but the recoverable file was kept:\n{file}",
    "rec.saved_status": "Recording saved: {name}", "rec.saved": "Recording saved to:\n{file}",
    "rec.close_active": "Recording is still active. Stop it and close?",
    "rec.region": "DRAG TO SELECT THE AREA · ESC TO CANCEL", "rec.area_too_small": "Select an area of at least 160 × 120 pixels.",
}


ES = {
    "view.compact": "Vista compacta", "view.full": "Vista completa", "maximize": "Maximizar", "restore": "Restaurar",
    "language": "Idioma", "subtitle": "Gestor persistente de descargas múltiples · contenido propio o autorizado.",
    "url.label": "Enlace del video o página", "paste": "Pegar", "start": "Iniciar", "format": "Formato",
    "format.video": "Video MP4", "format.audio": "Audio MP3", "resolution": "Resolución máxima solicitada",
    "quality.best": "Máxima disponible", "playlist": "Lista de reproducción", "playlist.all": "Descargar lista completa",
    "destination": "Carpeta de destino", "choose": "Elegir", "open": "Abrir", "pause": "Pausar", "resume": "Continuar",
    "record": "Grabar pantalla", "update": "Actualizar motor", "monitor": "Monitor de descargas",
    "parallel": "Descargas simultáneas:", "fragments": "Fragmentos por descarga:",
    "col.video": "Video / enlace", "col.format": "Formato", "col.size": "Tamaño", "col.status": "Estado",
    "col.progress": "Progreso", "col.speed": "Velocidad", "col.remaining": "Restante",
    "pause.selected": "Pausar seleccionadas", "resume.selected": "Continuar seleccionadas", "cancel": "Cancelar",
    "clear.completed": "Eliminar terminadas", "activity": "Actividad técnica", "support": "Apoyar a Zeo",
    "support.tip": "Aporte opcional mediante Mercado Pago", "status.ready": "Listo para descargar",
    "status.recovered": "Sesión anterior recuperada. Selecciona una descarga y pulsa Continuar.",
    "status.read_failed": "No se pudo leer el historial anterior.", "status.extension": "Enlace de Firefox agregado al monitor de descargas.",
    "status.active": "{count} descarga(s) activa(s)", "status.updating": "Actualizando motor…", "status.updated": "Motor actualizado",
    "status.update_failed": "No se pudo actualizar", "clipboard.empty": "El portapapeles está vacío.",
    "url.invalid": "Pega un enlace válido que comience con http:// o https://", "engine.missing": "No se encontró yt-dlp. Ejecuta INSTALAR_EN_WINDOWS.bat y vuelve a abrir la aplicación.",
    "installer.first": "No se encontró yt-dlp. Ejecuta primero el instalador.",
    "close.active": "Las descargas activas quedarán guardadas para continuarlas después. ¿Cerrar la aplicación?",
    "state.queued": "En cola", "state.starting": "Iniciando", "state.downloading": "Descargando", "state.pausing": "Pausando",
    "state.paused": "Pausada", "state.interrupted": "Interrumpida", "state.error": "Error", "state.cancelled": "Cancelada", "state.done": "Terminada",
    "resolution.detecting": "Detectando…", "resolution.pending": "Pendiente",
    "error.403": "El sitio rechazó la descarga (403 Forbidden). Actualiza el motor y prueba una vez más; si continúa, el servidor no permite la descarga automatizada de ese enlace.",
    "error.drm": "El contenido parece protegido con DRM y Zeo no puede procesarlo.",
    "error.private": "El contenido es privado o requiere una cuenta. Usa únicamente la opción oficial del sitio.",
    "error.geo": "El contenido tiene una restricción territorial y no está disponible desde esta ubicación.",
    "error.offline": "La transmisión pública no está activa en este momento.", "error.unsupported": "El motor todavía no reconoce esta página. Actualiza el motor y vuelve a intentarlo.",
    "error.impersonate": "Falta el componente oficial de compatibilidad web. Ejecuta nuevamente el instalador de esta versión.",
    "error.default": "No se pudo completar. Revisa el detalle inferior y prueba Actualizar motor.",
    "rec.title": "Grabar videollamada", "rec.consent": "Avisa a todos los participantes antes de iniciar la grabación.",
    "rec.folder": "Carpeta de grabaciones", "rec.client": "Cliente", "rec.project": "Proyecto", "rec.topic": "Tema",
    "rec.area": "Área de grabación", "rec.select_area": "Seleccionar área", "rec.fullscreen": "Pantalla completa", "rec.flow": "Fluidez",
    "rec.quality.light": "Liviana", "rec.quality.balanced": "Equilibrada", "rec.quality.high": "Alta", "rec.quality.maximum": "Máxima",
    "rec.limit.none": "Sin límite", "rec.limit.30": "30 minutos", "rec.limit.60": "60 minutos", "rec.limit.90": "90 minutos", "rec.limit.120": "120 minutos",
    "rec.system_audio": "Audio del computador (elige Mezcla estéreo si aparece)", "rec.microphone": "Micrófono", "rec.no_audio": "Sin audio",
    "rec.notice": "Se grabará todo lo visible en el área seleccionada, incluidos los avisos.",
    "rec.preparing": "Preparando dispositivos de audio…", "rec.devices": "{count} dispositivo(s) de audio detectado(s).",
    "rec.ffmpeg": "FFmpeg no está disponible. Ejecuta nuevamente el instalador.", "rec.area_full": "Pantalla completa",
    "rec.area_custom": "Área personalizada: {width} × {height} px, posición {x}, {y}", "rec.start": "Iniciar grabación",
    "rec.stop": "Detener y guardar", "rec.shot": "Captura (F8)", "rec.marker": "Marcar momento", "rec.open": "Abrir carpeta",
    "rec.ffmpeg_not_found": "No se encontró FFmpeg. Ejecuta INSTALAR_EN_WINDOWS.bat.",
    "rec.confirm": "¿Confirmas que avisaste a los participantes y tienes autorización para grabar?",
    "rec.starts": "La grabación comenzará en 3 segundos…", "rec.countdown": "Comenzando en {seconds}…",
    "rec.recording": "Grabando… vuelve aquí y pulsa Detener y guardar.", "rec.finalizing": "Finalizando MP4…",
    "rec.marker_prompt": "Escribe una nota para este momento:", "rec.marker_default": "Marca", "rec.marker_added": "Marca agregada: {time} – {note}",
    "rec.shot_saved": "Captura guardada: {name}", "rec.failed": "No se pudo completar la grabación.",
    "rec.audio_hint": "Revisa que el dispositivo de audio elegido siga conectado.",
    "rec.audio_missing": "Windows no encontró el dispositivo de audio seleccionado. Abre nuevamente esta ventana para actualizar la lista.",
    "rec.warning": "El MP4 no pudo finalizarse, pero conservamos el archivo recuperable:\n{file}",
    "rec.saved_status": "Grabación guardada: {name}", "rec.saved": "Grabación guardada en:\n{file}",
    "rec.close_active": "La grabación sigue activa. ¿Deseas detenerla y cerrar?",
    "rec.region": "ARRASTRA PARA SELECCIONAR EL ÁREA · ESC PARA CANCELAR", "rec.area_too_small": "Selecciona un área de al menos 160 × 120 píxeles.",
}


PT = {
    "view.compact":"Vista compacta","view.full":"Vista completa","maximize":"Maximizar","restore":"Restaurar","language":"Idioma",
    "subtitle":"Gerenciador persistente de vários downloads · conteúdo próprio ou autorizado.","url.label":"Link do vídeo ou página","paste":"Colar","start":"Iniciar",
    "format":"Formato","format.video":"Vídeo MP4","format.audio":"Áudio MP3","resolution":"Resolução máxima solicitada","quality.best":"Máxima disponível",
    "playlist":"Lista de reprodução","playlist.all":"Baixar lista completa","destination":"Pasta de destino","choose":"Escolher","open":"Abrir","pause":"Pausar","resume":"Continuar",
    "record":"Gravar tela","update":"Atualizar mecanismo","monitor":"Monitor de downloads","parallel":"Downloads simultâneos:","fragments":"Fragmentos por download:",
    "col.video":"Vídeo / link","col.format":"Formato","col.size":"Tamanho","col.status":"Estado","col.progress":"Progresso","col.speed":"Velocidade","col.remaining":"Restante",
    "pause.selected":"Pausar selecionados","resume.selected":"Continuar selecionados","cancel":"Cancelar","clear.completed":"Remover concluídos","activity":"Atividade técnica",
    "support":"Apoiar o Zeo","support.tip":"Contribuição opcional via Mercado Pago","status.ready":"Pronto para baixar","status.recovered":"Sessão anterior recuperada. Selecione um download e pressione Continuar.",
    "status.read_failed":"Não foi possível ler o histórico anterior.","status.extension":"Link do Firefox adicionado ao monitor.","status.active":"{count} download(s) ativo(s)",
    "status.updating":"Atualizando mecanismo…","status.updated":"Mecanismo atualizado","status.update_failed":"Falha ao atualizar","clipboard.empty":"A área de transferência está vazia.",
    "url.invalid":"Cole um link válido começando com http:// ou https://","state.queued":"Na fila","state.starting":"Iniciando","state.downloading":"Baixando","state.pausing":"Pausando",
    "state.paused":"Pausado","state.interrupted":"Interrompido","state.error":"Erro","state.cancelled":"Cancelado","state.done":"Concluído","resolution.detecting":"Detectando…","resolution.pending":"Pendente",
    "rec.title":"Gravar videochamada","rec.consent":"Avise todos os participantes antes de gravar.","rec.folder":"Pasta de gravações","rec.client":"Cliente","rec.project":"Projeto","rec.topic":"Tema",
    "rec.area":"Área de gravação","rec.select_area":"Selecionar área","rec.fullscreen":"Tela inteira","rec.flow":"Fluidez","rec.quality.light":"Leve","rec.quality.balanced":"Equilibrada","rec.quality.high":"Alta","rec.quality.maximum":"Máxima",
    "rec.limit.none":"Sem limite","rec.limit.30":"30 minutos","rec.limit.60":"60 minutos","rec.limit.90":"90 minutos","rec.limit.120":"120 minutos","rec.system_audio":"Áudio do computador (escolha Mixagem estéreo se disponível)",
    "rec.microphone":"Microfone","rec.no_audio":"Sem áudio","rec.notice":"Tudo que estiver visível na área selecionada será gravado.","rec.preparing":"Preparando dispositivos de áudio…","rec.devices":"{count} dispositivo(s) de áudio detectado(s).",
    "rec.area_full":"Tela inteira","rec.area_custom":"Área personalizada: {width} × {height} px, posição {x}, {y}","rec.start":"Iniciar gravação","rec.stop":"Parar e salvar","rec.shot":"Captura (F8)","rec.marker":"Marcar momento","rec.open":"Abrir pasta",
    "rec.confirm":"Você avisou os participantes e tem autorização para gravar?","rec.starts":"A gravação começará em 3 segundos…","rec.countdown":"Começando em {seconds}…","rec.recording":"Gravando… volte aqui e pressione Parar e salvar.",
    "rec.finalizing":"Finalizando MP4…","rec.marker_prompt":"Escreva uma nota para este momento:","rec.marker_default":"Marca","rec.marker_added":"Marca adicionada: {time} – {note}","rec.shot_saved":"Captura salva: {name}",
    "rec.failed":"Não foi possível concluir a gravação.","rec.saved_status":"Gravação salva: {name}","rec.saved":"Gravação salva em:\n{file}","rec.close_active":"A gravação ainda está ativa. Parar e fechar?","rec.region":"ARRASTE PARA SELECIONAR A ÁREA · ESC PARA CANCELAR",
}


DE = {
    "view.compact":"Kompaktansicht","view.full":"Vollansicht","maximize":"Maximieren","restore":"Wiederherstellen","language":"Sprache",
    "subtitle":"Persistenter Manager für mehrere Downloads · eigene oder autorisierte Inhalte.","url.label":"Video- oder Webseiten-URL","paste":"Einfügen","start":"Starten","format":"Format",
    "format.video":"MP4-Video","format.audio":"MP3-Audio","resolution":"Maximal gewünschte Auflösung","quality.best":"Beste verfügbar","playlist":"Wiedergabeliste","playlist.all":"Ganze Wiedergabeliste laden",
    "destination":"Zielordner","choose":"Auswählen","open":"Öffnen","pause":"Pausieren","resume":"Fortsetzen","record":"Bildschirm aufnehmen","update":"Engine aktualisieren","monitor":"Download-Monitor",
    "parallel":"Gleichzeitige Downloads:","fragments":"Fragmente pro Download:","col.video":"Video / URL","col.format":"Format","col.size":"Größe","col.status":"Status","col.progress":"Fortschritt","col.speed":"Geschwindigkeit","col.remaining":"Restzeit",
    "pause.selected":"Auswahl pausieren","resume.selected":"Auswahl fortsetzen","cancel":"Abbrechen","clear.completed":"Abgeschlossene entfernen","activity":"Technische Aktivität","support":"Zeo unterstützen","support.tip":"Optionaler Beitrag über Mercado Pago",
    "status.ready":"Bereit zum Herunterladen","status.recovered":"Vorherige Sitzung wiederhergestellt. Download auswählen und Fortsetzen drücken.","status.read_failed":"Vorheriger Verlauf konnte nicht gelesen werden.","status.extension":"Firefox-URL zum Download-Monitor hinzugefügt.",
    "status.active":"{count} aktive(r) Download(s)","status.updating":"Engine wird aktualisiert…","status.updated":"Engine aktualisiert","status.update_failed":"Aktualisierung fehlgeschlagen","clipboard.empty":"Die Zwischenablage ist leer.",
    "url.invalid":"Gültige URL mit http:// oder https:// einfügen","state.queued":"Warteschlange","state.starting":"Startet","state.downloading":"Wird geladen","state.pausing":"Wird pausiert","state.paused":"Pausiert","state.interrupted":"Unterbrochen","state.error":"Fehler","state.cancelled":"Abgebrochen","state.done":"Abgeschlossen","resolution.detecting":"Erkennung…","resolution.pending":"Ausstehend",
    "rec.title":"Videoanruf aufnehmen","rec.consent":"Informiere alle Teilnehmer vor der Aufnahme.","rec.folder":"Aufnahmeordner","rec.client":"Kunde","rec.project":"Projekt","rec.topic":"Thema","rec.area":"Aufnahmebereich","rec.select_area":"Bereich wählen","rec.fullscreen":"Vollbild","rec.flow":"Bildrate",
    "rec.quality.light":"Sparsam","rec.quality.balanced":"Ausgewogen","rec.quality.high":"Hoch","rec.quality.maximum":"Maximum","rec.limit.none":"Ohne Limit","rec.limit.30":"30 Minuten","rec.limit.60":"60 Minuten","rec.limit.90":"90 Minuten","rec.limit.120":"120 Minuten",
    "rec.system_audio":"Computer-Audio (Stereomix wählen, falls verfügbar)","rec.microphone":"Mikrofon","rec.no_audio":"Kein Audio","rec.notice":"Alles Sichtbare im ausgewählten Bereich wird aufgenommen.","rec.preparing":"Audiogeräte werden vorbereitet…","rec.devices":"{count} Audiogerät(e) erkannt.",
    "rec.area_full":"Vollbild","rec.area_custom":"Benutzerdefiniert: {width} × {height} px, Position {x}, {y}","rec.start":"Aufnahme starten","rec.stop":"Stoppen und speichern","rec.shot":"Screenshot (F8)","rec.marker":"Zeitpunkt markieren","rec.open":"Ordner öffnen",
    "rec.confirm":"Wurden alle Teilnehmer informiert und liegt eine Aufnahmegenehmigung vor?","rec.starts":"Die Aufnahme startet in 3 Sekunden…","rec.countdown":"Start in {seconds}…","rec.recording":"Aufnahme läuft… hier Stoppen und speichern drücken.","rec.finalizing":"MP4 wird fertiggestellt…","rec.marker_prompt":"Notiz für diesen Zeitpunkt:","rec.marker_default":"Marke","rec.marker_added":"Marke hinzugefügt: {time} – {note}","rec.shot_saved":"Screenshot gespeichert: {name}","rec.failed":"Aufnahme konnte nicht abgeschlossen werden.","rec.saved_status":"Aufnahme gespeichert: {name}","rec.saved":"Aufnahme gespeichert unter:\n{file}","rec.close_active":"Die Aufnahme läuft noch. Stoppen und schließen?","rec.region":"ZIEHEN, UM DEN BEREICH ZU WÄHLEN · ESC ZUM ABBRECHEN",
}


FR = {
    "view.compact":"Vue compacte","view.full":"Vue complète","maximize":"Agrandir","restore":"Restaurer","language":"Langue","subtitle":"Gestionnaire persistant de téléchargements multiples · contenu personnel ou autorisé.",
    "url.label":"Lien de la vidéo ou de la page","paste":"Coller","start":"Démarrer","format":"Format","format.video":"Vidéo MP4","format.audio":"Audio MP3","resolution":"Résolution maximale demandée","quality.best":"Meilleure disponible",
    "playlist":"Liste de lecture","playlist.all":"Télécharger toute la liste","destination":"Dossier de destination","choose":"Choisir","open":"Ouvrir","pause":"Pause","resume":"Reprendre","record":"Enregistrer l’écran","update":"Mettre à jour le moteur","monitor":"Moniteur des téléchargements",
    "parallel":"Téléchargements simultanés :","fragments":"Fragments par téléchargement :","col.video":"Vidéo / lien","col.format":"Format","col.size":"Taille","col.status":"État","col.progress":"Progression","col.speed":"Vitesse","col.remaining":"Restant",
    "pause.selected":"Mettre en pause","resume.selected":"Reprendre la sélection","cancel":"Annuler","clear.completed":"Supprimer les terminés","activity":"Activité technique","support":"Soutenir Zeo","support.tip":"Contribution facultative via Mercado Pago",
    "status.ready":"Prêt à télécharger","status.recovered":"Session précédente récupérée. Sélectionnez un téléchargement et cliquez sur Reprendre.","status.read_failed":"Impossible de lire l’historique précédent.","status.extension":"Lien Firefox ajouté au moniteur.","status.active":"{count} téléchargement(s) actif(s)",
    "status.updating":"Mise à jour du moteur…","status.updated":"Moteur mis à jour","status.update_failed":"Échec de la mise à jour","clipboard.empty":"Le presse-papiers est vide.","url.invalid":"Collez un lien valide commençant par http:// ou https://",
    "state.queued":"En attente","state.starting":"Démarrage","state.downloading":"Téléchargement","state.pausing":"Mise en pause","state.paused":"En pause","state.interrupted":"Interrompu","state.error":"Erreur","state.cancelled":"Annulé","state.done":"Terminé","resolution.detecting":"Détection…","resolution.pending":"En attente",
    "rec.title":"Enregistrer un appel vidéo","rec.consent":"Prévenez tous les participants avant l’enregistrement.","rec.folder":"Dossier d’enregistrement","rec.client":"Client","rec.project":"Projet","rec.topic":"Sujet","rec.area":"Zone d’enregistrement","rec.select_area":"Sélectionner une zone","rec.fullscreen":"Plein écran","rec.flow":"Fluidité",
    "rec.quality.light":"Légère","rec.quality.balanced":"Équilibrée","rec.quality.high":"Haute","rec.quality.maximum":"Maximum","rec.limit.none":"Sans limite","rec.limit.30":"30 minutes","rec.limit.60":"60 minutes","rec.limit.90":"90 minutes","rec.limit.120":"120 minutes",
    "rec.system_audio":"Audio de l’ordinateur (choisissez Mixage stéréo si disponible)","rec.microphone":"Microphone","rec.no_audio":"Sans audio","rec.notice":"Tout ce qui est visible dans la zone sélectionnée sera enregistré.","rec.preparing":"Préparation des périphériques audio…","rec.devices":"{count} périphérique(s) audio détecté(s).",
    "rec.area_full":"Plein écran","rec.area_custom":"Zone personnalisée : {width} × {height} px, position {x}, {y}","rec.start":"Démarrer l’enregistrement","rec.stop":"Arrêter et enregistrer","rec.shot":"Capture (F8)","rec.marker":"Marquer l’instant","rec.open":"Ouvrir le dossier",
    "rec.confirm":"Avez-vous prévenu les participants et obtenu l’autorisation d’enregistrer ?","rec.starts":"L’enregistrement commencera dans 3 secondes…","rec.countdown":"Démarrage dans {seconds}…","rec.recording":"Enregistrement… revenez ici et cliquez sur Arrêter et enregistrer.","rec.finalizing":"Finalisation du MP4…","rec.marker_prompt":"Écrivez une note pour cet instant :","rec.marker_default":"Repère","rec.marker_added":"Repère ajouté : {time} – {note}","rec.shot_saved":"Capture enregistrée : {name}","rec.failed":"L’enregistrement n’a pas pu être terminé.","rec.saved_status":"Enregistrement sauvegardé : {name}","rec.saved":"Enregistrement sauvegardé dans :\n{file}","rec.close_active":"L’enregistrement est actif. Arrêter et fermer ?","rec.region":"FAITES GLISSER POUR SÉLECTIONNER · ÉCHAP POUR ANNULER",
}


IT = {
    "view.compact":"Vista compatta","view.full":"Vista completa","maximize":"Massimizza","restore":"Ripristina","language":"Lingua","subtitle":"Gestore persistente di download multipli · contenuti propri o autorizzati.","url.label":"Link del video o della pagina","paste":"Incolla","start":"Avvia","format":"Formato","format.video":"Video MP4","format.audio":"Audio MP3","resolution":"Risoluzione massima richiesta","quality.best":"Massima disponibile","playlist":"Playlist","playlist.all":"Scarica playlist completa","destination":"Cartella di destinazione","choose":"Scegli","open":"Apri","pause":"Pausa","resume":"Riprendi","record":"Registra schermo","update":"Aggiorna motore","monitor":"Monitor download","parallel":"Download simultanei:","fragments":"Frammenti per download:",
    "col.video":"Video / link","col.format":"Formato","col.size":"Dimensione","col.status":"Stato","col.progress":"Avanzamento","col.speed":"Velocità","col.remaining":"Rimanente","pause.selected":"Metti in pausa","resume.selected":"Riprendi selezionati","cancel":"Annulla","clear.completed":"Rimuovi completati","activity":"Attività tecnica","support":"Sostieni Zeo","support.tip":"Contributo facoltativo tramite Mercado Pago","status.ready":"Pronto per il download","status.recovered":"Sessione precedente recuperata. Seleziona un download e premi Riprendi.","status.read_failed":"Impossibile leggere la cronologia precedente.","status.extension":"Link Firefox aggiunto al monitor.","status.active":"{count} download attivi","status.updating":"Aggiornamento motore…","status.updated":"Motore aggiornato","status.update_failed":"Aggiornamento non riuscito","clipboard.empty":"Gli appunti sono vuoti.","url.invalid":"Incolla un link valido che inizi con http:// o https://",
    "state.queued":"In coda","state.starting":"Avvio","state.downloading":"Download","state.pausing":"Pausa in corso","state.paused":"In pausa","state.interrupted":"Interrotto","state.error":"Errore","state.cancelled":"Annullato","state.done":"Completato","resolution.detecting":"Rilevamento…","resolution.pending":"In attesa",
    "rec.title":"Registra videochiamata","rec.consent":"Avvisa tutti i partecipanti prima di registrare.","rec.folder":"Cartella registrazioni","rec.client":"Cliente","rec.project":"Progetto","rec.topic":"Argomento","rec.area":"Area di registrazione","rec.select_area":"Seleziona area","rec.fullscreen":"Schermo intero","rec.flow":"Fluidità","rec.quality.light":"Leggera","rec.quality.balanced":"Bilanciata","rec.quality.high":"Alta","rec.quality.maximum":"Massima","rec.limit.none":"Senza limite","rec.limit.30":"30 minuti","rec.limit.60":"60 minuti","rec.limit.90":"90 minuti","rec.limit.120":"120 minuti","rec.system_audio":"Audio del computer (scegli Mix stereo se disponibile)","rec.microphone":"Microfono","rec.no_audio":"Senza audio","rec.notice":"Tutto ciò che è visibile nell’area selezionata verrà registrato.","rec.preparing":"Preparazione dispositivi audio…","rec.devices":"{count} dispositivo/i audio rilevato/i.","rec.area_full":"Schermo intero","rec.area.custom":"Area personalizzata: {width} × {height} px, posizione {x}, {y}","rec.start":"Avvia registrazione","rec.stop":"Ferma e salva","rec.shot":"Cattura (F8)","rec.marker":"Segna momento","rec.open":"Apri cartella","rec.confirm":"Hai avvisato i partecipanti e hai l’autorizzazione a registrare?","rec.starts":"La registrazione inizierà tra 3 secondi…","rec.countdown":"Avvio tra {seconds}…","rec.recording":"Registrazione… torna qui e premi Ferma e salva.","rec.finalizing":"Finalizzazione MP4…","rec.marker_prompt":"Scrivi una nota per questo momento:","rec.marker_default":"Segno","rec.marker_added":"Segno aggiunto: {time} – {note}","rec.shot_saved":"Cattura salvata: {name}","rec.failed":"Impossibile completare la registrazione.","rec.saved_status":"Registrazione salvata: {name}","rec.saved":"Registrazione salvata in:\n{file}","rec.close_active":"La registrazione è ancora attiva. Fermare e chiudere?","rec.region":"TRASCINA PER SELEZIONARE L’AREA · ESC PER ANNULLARE",
}


ZH = {
    "view.compact":"紧凑视图","view.full":"完整视图","maximize":"最大化","restore":"还原","language":"语言","subtitle":"可恢复的多任务下载管理器 · 仅限自有或已获授权的内容。","url.label":"视频或网页链接","paste":"粘贴","start":"开始","format":"格式","format.video":"MP4 视频","format.audio":"MP3 音频","resolution":"最高请求分辨率","quality.best":"最佳可用","playlist":"播放列表","playlist.all":"下载完整播放列表","destination":"保存文件夹","choose":"选择","open":"打开","pause":"暂停","resume":"继续","record":"录制屏幕","update":"更新引擎","monitor":"下载监视器","parallel":"同时下载数：","fragments":"每个下载的分片数：","col.video":"视频 / 链接","col.format":"格式","col.size":"大小","col.status":"状态","col.progress":"进度","col.speed":"速度","col.remaining":"剩余时间","pause.selected":"暂停所选","resume.selected":"继续所选","cancel":"取消","clear.completed":"移除已完成","activity":"技术日志","support":"支持 Zeo","support.tip":"通过 Mercado Pago 自愿支持","status.ready":"可以开始下载","status.recovered":"已恢复上次会话。请选择任务并点击继续。","status.read_failed":"无法读取以前的历史记录。","status.extension":"已将 Firefox 链接添加到下载监视器。","status.active":"{count} 个下载正在进行","status.updating":"正在更新引擎…","status.updated":"引擎已更新","status.update_failed":"更新失败","clipboard.empty":"剪贴板为空。","url.invalid":"请粘贴以 http:// 或 https:// 开头的有效链接",
    "state.queued":"排队中","state.starting":"正在启动","state.downloading":"正在下载","state.pausing":"正在暂停","state.paused":"已暂停","state.interrupted":"已中断","state.error":"错误","state.cancelled":"已取消","state.done":"已完成","resolution.detecting":"正在检测…","resolution.pending":"等待中",
    "rec.title":"录制视频通话","rec.consent":"录制前请告知所有参与者。","rec.folder":"录制文件夹","rec.client":"客户","rec.project":"项目","rec.topic":"主题","rec.area":"录制区域","rec.select_area":"选择区域","rec.fullscreen":"全屏","rec.flow":"帧率","rec.quality.light":"轻量","rec.quality.balanced":"均衡","rec.quality.high":"高质量","rec.quality.maximum":"最高质量","rec.limit.none":"无限制","rec.limit.30":"30 分钟","rec.limit.60":"60 分钟","rec.limit.90":"90 分钟","rec.limit.120":"120 分钟","rec.system_audio":"电脑音频（如可用，请选择立体声混音）","rec.microphone":"麦克风","rec.no_audio":"无音频","rec.notice":"所选区域中所有可见内容都会被录制。","rec.preparing":"正在准备音频设备…","rec.devices":"检测到 {count} 个音频设备。","rec.area_full":"全屏","rec.area_custom":"自定义区域：{width} × {height} 像素，位置 {x}, {y}","rec.start":"开始录制","rec.stop":"停止并保存","rec.shot":"截图 (F8)","rec.marker":"标记时刻","rec.open":"打开文件夹","rec.confirm":"你是否已告知参与者并获得录制授权？","rec.starts":"录制将在 3 秒后开始…","rec.countdown":"{seconds} 秒后开始…","rec.recording":"正在录制…请返回此处并点击停止并保存。","rec.finalizing":"正在生成 MP4…","rec.marker_prompt":"为此时刻添加备注：","rec.marker_default":"标记","rec.marker_added":"已添加标记：{time} – {note}","rec.shot_saved":"截图已保存：{name}","rec.failed":"无法完成录制。","rec.saved_status":"录制已保存：{name}","rec.saved":"录制已保存到：\n{file}","rec.close_active":"录制仍在进行。是否停止并关闭？","rec.region":"拖动以选择区域 · ESC 取消",
}


PT.update({
    "engine.missing":"yt-dlp não foi encontrado. Execute INSTALAR_EN_WINDOWS.bat e reabra o aplicativo.", "installer.first":"yt-dlp não foi encontrado. Execute primeiro o instalador.",
    "close.active":"Os downloads ativos serão salvos para continuar depois. Fechar o aplicativo?", "error.403":"O site recusou o download (403 Forbidden). Atualize o mecanismo e tente mais uma vez.",
    "error.drm":"Este conteúdo parece protegido por DRM e o Zeo não pode processá-lo.", "error.private":"O conteúdo é privado ou exige uma conta. Use somente a opção oficial do site.",
    "error.geo":"O conteúdo tem restrição regional e não está disponível nesta localização.", "error.offline":"A transmissão pública não está ativa agora.",
    "error.unsupported":"O mecanismo ainda não reconhece esta página. Atualize-o e tente novamente.", "error.impersonate":"Falta o componente oficial de compatibilidade web. Execute novamente o instalador.",
    "error.default":"Não foi possível concluir. Verifique os detalhes e tente Atualizar mecanismo.", "rec.area_too_small":"Selecione uma área de pelo menos 160 × 120 pixels.",
    "rec.ffmpeg":"FFmpeg não está disponível. Execute novamente o instalador.", "rec.ffmpeg_not_found":"FFmpeg não foi encontrado. Execute INSTALAR_EN_WINDOWS.bat.",
    "rec.audio_hint":"Verifique se o dispositivo de áudio selecionado ainda está conectado.", "rec.audio_missing":"O Windows não encontrou o dispositivo de áudio selecionado. Reabra esta janela para atualizar a lista.",
    "rec.warning":"O MP4 não pôde ser finalizado, mas o arquivo recuperável foi mantido:\n{file}",
})

DE.update({
    "engine.missing":"yt-dlp wurde nicht gefunden. INSTALAR_EN_WINDOWS.bat ausführen und die App neu öffnen.", "installer.first":"yt-dlp wurde nicht gefunden. Zuerst das Installationsprogramm ausführen.",
    "close.active":"Aktive Downloads werden gespeichert und können später fortgesetzt werden. Anwendung schließen?", "error.403":"Die Website hat den Download abgelehnt (403 Forbidden). Engine aktualisieren und erneut versuchen.",
    "error.drm":"Dieser Inhalt scheint DRM-geschützt zu sein und kann von Zeo nicht verarbeitet werden.", "error.private":"Der Inhalt ist privat oder erfordert ein Konto. Nur die offizielle Option der Website verwenden.",
    "error.geo":"Der Inhalt ist regional gesperrt und an diesem Standort nicht verfügbar.", "error.offline":"Der öffentliche Stream ist derzeit nicht aktiv.",
    "error.unsupported":"Die Engine erkennt diese Seite noch nicht. Aktualisieren und erneut versuchen.", "error.impersonate":"Die offizielle Web-Kompatibilitätskomponente fehlt. Installationsprogramm erneut ausführen.",
    "error.default":"Download konnte nicht abgeschlossen werden. Details prüfen und Engine aktualisieren.", "rec.area_too_small":"Einen Bereich von mindestens 160 × 120 Pixeln auswählen.",
    "rec.ffmpeg":"FFmpeg ist nicht verfügbar. Installationsprogramm erneut ausführen.", "rec.ffmpeg_not_found":"FFmpeg wurde nicht gefunden. INSTALAR_EN_WINDOWS.bat ausführen.",
    "rec.audio_hint":"Prüfen, ob das ausgewählte Audiogerät noch verbunden ist.", "rec.audio_missing":"Windows konnte das ausgewählte Audiogerät nicht finden. Dieses Fenster erneut öffnen.",
    "rec.warning":"MP4 konnte nicht fertiggestellt werden; die wiederherstellbare Datei wurde behalten:\n{file}",
})

FR.update({
    "engine.missing":"yt-dlp est introuvable. Exécutez INSTALAR_EN_WINDOWS.bat puis rouvrez l’application.", "installer.first":"yt-dlp est introuvable. Exécutez d’abord le programme d’installation.",
    "close.active":"Les téléchargements actifs seront enregistrés pour être repris plus tard. Fermer l’application ?", "error.403":"Le site a refusé le téléchargement (403 Forbidden). Mettez le moteur à jour et réessayez.",
    "error.drm":"Ce contenu semble protégé par DRM et Zeo ne peut pas le traiter.", "error.private":"Le contenu est privé ou nécessite un compte. Utilisez uniquement l’option officielle du site.",
    "error.geo":"Ce contenu est soumis à une restriction régionale et n’est pas disponible ici.", "error.offline":"La diffusion publique n’est pas active actuellement.",
    "error.unsupported":"Le moteur ne reconnaît pas encore cette page. Mettez-le à jour et réessayez.", "error.impersonate":"Le composant officiel de compatibilité Web manque. Relancez le programme d’installation.",
    "error.default":"Le téléchargement n’a pas pu être terminé. Consultez les détails et mettez le moteur à jour.", "rec.area_too_small":"Sélectionnez une zone d’au moins 160 × 120 pixels.",
    "rec.ffmpeg":"FFmpeg n’est pas disponible. Relancez le programme d’installation.", "rec.ffmpeg_not_found":"FFmpeg est introuvable. Exécutez INSTALAR_EN_WINDOWS.bat.",
    "rec.audio_hint":"Vérifiez que le périphérique audio sélectionné est toujours connecté.", "rec.audio_missing":"Windows ne trouve pas le périphérique audio sélectionné. Rouvrez cette fenêtre.",
    "rec.warning":"Le MP4 n’a pas pu être finalisé, mais le fichier récupérable a été conservé :\n{file}",
})

IT.update({
    "engine.missing":"yt-dlp non è stato trovato. Esegui INSTALAR_EN_WINDOWS.bat e riapri l’app.", "installer.first":"yt-dlp non è stato trovato. Esegui prima il programma di installazione.",
    "close.active":"I download attivi verranno salvati per essere ripresi in seguito. Chiudere l’applicazione?", "error.403":"Il sito ha rifiutato il download (403 Forbidden). Aggiorna il motore e riprova.",
    "error.drm":"Il contenuto sembra protetto da DRM e Zeo non può elaborarlo.", "error.private":"Il contenuto è privato o richiede un account. Usa solo l’opzione ufficiale del sito.",
    "error.geo":"Il contenuto ha una restrizione geografica e non è disponibile qui.", "error.offline":"La trasmissione pubblica non è attiva in questo momento.",
    "error.unsupported":"Il motore non riconosce ancora questa pagina. Aggiornalo e riprova.", "error.impersonate":"Manca il componente ufficiale di compatibilità web. Esegui nuovamente il programma di installazione.",
    "error.default":"Impossibile completare il download. Controlla i dettagli e aggiorna il motore.", "rec.area_custom":"Area personalizzata: {width} × {height} px, posizione {x}, {y}",
    "rec.area_too_small":"Seleziona un’area di almeno 160 × 120 pixel.", "rec.ffmpeg":"FFmpeg non è disponibile. Esegui nuovamente il programma di installazione.",
    "rec.ffmpeg_not_found":"FFmpeg non è stato trovato. Esegui INSTALAR_EN_WINDOWS.bat.", "rec.audio_hint":"Controlla che il dispositivo audio selezionato sia ancora collegato.",
    "rec.audio_missing":"Windows non trova il dispositivo audio selezionato. Riapri questa finestra.", "rec.warning":"Impossibile finalizzare l’MP4, ma il file recuperabile è stato conservato:\n{file}",
})

ZH.update({
    "engine.missing":"未找到 yt-dlp。请运行 INSTALAR_EN_WINDOWS.bat，然后重新打开应用。", "installer.first":"未找到 yt-dlp。请先运行安装程序。",
    "close.active":"正在进行的下载将被保存，以便稍后继续。是否关闭应用？", "error.403":"网站拒绝了下载（403 Forbidden）。请更新引擎后重试。",
    "error.drm":"此内容似乎受 DRM 保护，Zeo 无法处理。", "error.private":"此内容为私密内容或需要账户。请仅使用网站的官方选项。",
    "error.geo":"此内容有地区限制，当前位置无法访问。", "error.offline":"公开直播当前未开始。", "error.unsupported":"引擎尚不识别此页面。请更新后重试。",
    "error.impersonate":"缺少官方网页兼容组件。请重新运行此版本的安装程序。", "error.default":"无法完成下载。请查看下方详情并尝试更新引擎。",
    "rec.area_too_small":"请选择至少 160 × 120 像素的区域。", "rec.ffmpeg":"FFmpeg 不可用。请重新运行安装程序。", "rec.ffmpeg_not_found":"未找到 FFmpeg。请运行 INSTALAR_EN_WINDOWS.bat。",
    "rec.audio_hint":"请检查所选音频设备是否仍然连接。", "rec.audio_missing":"Windows 找不到所选音频设备。请重新打开此窗口刷新列表。",
    "rec.warning":"无法完成 MP4，但已保留可恢复文件：\n{file}",
})

TRANSLATIONS = {"en": EN, "es": ES, "pt": PT, "de": DE, "fr": FR, "it": IT, "zh": ZH}


def detect_language():
    try:
        code = (locale.getlocale()[0] or "").lower().split("_")[0].split("-")[0]
    except (ValueError, TypeError):
        code = ""
    return code if code in LANGUAGES else "es"


class Translator:
    def __init__(self, language="es"):
        self.language = language if language in LANGUAGES else "es"

    def set_language(self, language):
        self.language = language if language in LANGUAGES else "es"

    def tr(self, key, **values):
        text = TRANSLATIONS.get(self.language, {}).get(key, EN.get(key, key))
        try:
            return text.format(**values)
        except (KeyError, ValueError):
            return text
