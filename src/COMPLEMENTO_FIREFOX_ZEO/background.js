"use strict";

async function notify(title, message) {
  await browser.notifications.create({
    type: "basic",
    iconUrl: browser.runtime.getURL("icons/zeo.svg"),
    title,
    message
  });
}

browser.browserAction.onClicked.addListener(async (tab) => {
  const url = tab && tab.url ? tab.url : "";
  if (!/^https?:\/\//i.test(url)) {
    await notify("ZEO", "Esta pestaña no contiene una página web descargable.");
    return;
  }

  browser.browserAction.setBadgeText({text: "…", tabId: tab.id});
  browser.browserAction.setBadgeBackgroundColor({color: "#2563eb"});
  try {
    const response = await fetch("http://127.0.0.1:17835/download", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Zeo-Extension": "firefox-1.0"
      },
      body: JSON.stringify({url})
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    browser.browserAction.setBadgeText({text: "✓", tabId: tab.id});
    browser.browserAction.setBadgeBackgroundColor({color: "#16a34a"});
    await notify("ZEO", "Enlace enviado. Zeo Downloader iniciará la descarga.");
  } catch (_error) {
    browser.browserAction.setBadgeText({text: "!", tabId: tab.id});
    browser.browserAction.setBadgeBackgroundColor({color: "#dc2626"});
    await notify("ZEO no está conectado", "Abre Zeo Video Downloader 1.5 y vuelve a pulsar el botón.");
  }
  setTimeout(() => browser.browserAction.setBadgeText({text: "", tabId: tab.id}), 3500);
});
