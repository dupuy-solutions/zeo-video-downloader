# ZEO Downloader 2.0 PRO

Rama de prueba separada de la versión pública 1.9.

## Objetivo
Convertir Zeo Video Downloader en un gestor multimedia ZEO para video y audio, manteniendo compatibilidad con el motor estable existente.

## Implementado en esta rama
- Lanzador independiente `src/ABRIR_ZEO_2_PRO.bat`.
- Aplicación independiente `src/app_pro.py` construida sobre el motor 1.9.
- Identidad visible `ZEO 2.0 PRO`.
- Detección básica de plataforma por dominio.
- Detección específica de enlaces `suno.com`.
- Los enlaces Suno ya no se envían a `yt-dlp`.
- Cambio automático a modo Audio cuando se pega un enlace Suno.
- Flujo seguro: abre la canción en Suno para usar la descarga oficial autenticada y conserva el enlace en ZEO.
- La versión 1.9 pública permanece sin cambios.

## Próximos módulos PRO
1. Perfiles rápidos de descarga: Video máximo, 1080p, 720p, Audio MP3, Audio WAV cuando el origen lo permita.
2. Panel de información previo a descargar: plataforma, título, duración, formatos y tamaño estimado cuando el extractor pueda obtenerlos.
3. Importación local de audio/video para trabajar después de una descarga oficial de servicios autenticados.
4. Herramientas de audio con FFmpeg: convertir, recortar, unir, normalizar, fade-in/fade-out y crear versiones extendidas a partir de material propio o autorizado.
5. Historial PRO con búsqueda, filtro por plataforma y reapertura de carpeta.
6. Cola mejorada con prioridad, reintentos configurables y perfiles por tarea.
7. Integración del complemento del navegador con detección de plataforma antes de enviar la URL.
8. Empaquetado Windows independiente para pruebas sin sustituir la instalación estable.

## Prueba actual
1. Cambiar a la rama `zeo-2.0-pro`.
2. Abrir la carpeta `src`.
3. Ejecutar `ABRIR_ZEO_2_PRO.bat`.
4. Pegar un enlace normal compatible: debe continuar usando el motor 1.9.
5. Pegar un enlace de Suno: ZEO debe detectarlo como Suno, seleccionar Audio y ofrecer abrir la canción en Suno sin lanzar `yt-dlp`.

## Nota de seguridad y compatibilidad
ZEO no intenta eludir DRM, autenticación, cuotas de descarga ni protecciones de plataformas. Para servicios que exigen descarga desde una cuenta autenticada, ZEO guía al flujo oficial y después puede trabajar localmente con el archivo descargado por el usuario.
