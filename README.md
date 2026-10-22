# Stadtbibliothek Wiesbaden Integration für Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/dein-github-name/ha-wiesbaden-library)](https://github.com/dein-github-name/ha-wiesbaden-library/releases)

Eine Home-Assistant-Integration zum automatisierten Abrufen der ausgeliehenen Medien und Rückgabefristen der **Stadtbibliothek Wiesbaden** (`bond.wiesbaden.de`).

---

## Features

* **Automatisierter Abruf:** Holt regelmäßig (standardmäßig alle 6 Stunden) deine aktuellen Ausleihen direkt aus deinem Online-Konto ab.
* **Natives Datumselement:** Der Hauptsensor setzt das Fälligkeitsdatum der *nächsten* anstehenden Rückgabe im ISO-Format (`YYYY-MM-DD`), wodurch er perfekt für Automationen, Kalender und Home-Assistant-Dashboards geeignet ist.
* **Detaillierte Attribute:** 
  * Vollständige Liste aller geliehenen Bücher (inkl. Titel, Autor, Frist und Zweigstelle).
  * Automatische Erfassung aller beteiligten Zweigstellen (`branches`).
  * Gesamtanzahl der geliehenen Medien (`total_books`).
* **Einfache Konfiguration:** Vollständig über die Home-Assistant-Benutzeroberfläche (GUI / Config Flow) einrichtbar – kein Long-Lived Access Token oder manuelles Scripting notwendig!

---

## Installation via HACS (Empfohlen)

1. Stelle sicher, dass du [HACS](https://hacs.xyz/) installiert hast.
2. Klicke auf diesen Button oder füge das Repository manuell hinzu:
   * Gehe in HACS auf **Integrationen**.
   * Klicke oben rechts auf die drei Punkte und wähle **Benutzerdefiniertes Repository hinzufügen**.
   * Trage die URL deines Repositories ein und wähle als Kategorie **Integration**.
3. Suche nach **"Stadtbibliothek Wiesbaden"** und klicke auf **Installieren**.
4. Starte Home Assistant neu.

---

## Einrichtung

1. Gehe in Home Assistant auf **Einstellungen** -> **Geräte & Dienste** -> **Integration hinzufügen**.
2. Suche nach **Stadtbibliothek Wiesbaden**.
3. Gib deine **Ausweisnummer** und dein **Passwort** (bzw. Geburtsdatum) ein und schließe die Einrichtung ab.

---

## Verwendung im Dashboard

Du kannst dir alle ausgeliehenen Bücher beispielsweise über eine Markdown-Karte auf deinem Dashboard anzeigen lassen:

```yaml
type: markdown
title: "Stadtbibliothek Wiesbaden"
content: >
  Nächste Rückgabe: **{{ states('sensor.stadtbibliothek_naechste_rueckgabe') }}**
  
  {% set books = state_attr('sensor.stadtbibliothek_naechste_rueckgabe', 'books') %}
  {% if books %}
    | Titel | Rückgabe | Zweigstelle |
    | :--- | :--- | :--- |
    {% for book in books -%}
      | {{ book.title }} | {{ book.due_date }} | {{ book.branch }} |
    {% endfor %}
  {% else %}
    Keine Ausleihen gefunden.
  {% endif %}
