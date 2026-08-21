# main.py
import json
import os
import tkinter as tk
from mosaic_engine import MosaicEngine
from mosaic_gui import MosaicGUI

SETTINGS_FILE = "settings.json"

# IKEA-Billi Regal Breite = 45 Noppen (8mm)

# Definiere feste "Fallback"-Standards für den Fall, dass die JSON-Datei fehlt
DEFAULT_SETTINGS = {
    "default_image_path": "Bilder/Test1.jpg",
    "initial_height": 400,
    "window_min_width": 100,
    "window_min_height": 100,
    "window_title": "MosaicBlocks",
    "background_color": (0, 0, 0, 255),
    "block_size": 8,  # [mm]
}


def load_settings():
    """Lädt die Einstellungen aus der JSON-Datei.
    Erstellt eine neue Datei mit Standardwerten, falls keine existiert."""
    if not os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_SETTINGS, f, indent=4)
            print(f"Neue '{SETTINGS_FILE}' mit Standardwerten wurde erstellt.")
            return DEFAULT_SETTINGS
        except Exception as e:
            print(f"Konnte Standard-Einstellungen nicht schreiben: {e}")
            return DEFAULT_SETTINGS

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
            if "background_color" in settings:
                settings["background_color"] = tuple(settings["background_color"])
            print("Einstellungen erfolgreich geladen.")
            return settings
    except Exception as e:
        print(f"Fehler beim Lesen der JSON-Datei. Nutze Fallback-Defaults. Fehler: {e}")
        return DEFAULT_SETTINGS


def main():
    """Hauptfunktion zum Starten der Anwendung."""
    # 1. Lade Einstellungen
    app_settings = load_settings()

    # 2. Instanziiere die Engine
    engine = MosaicEngine(app_settings)

    # 3. Lade das Bild über den Pfad aus den Einstellungen
    image_path = app_settings.get("default_image_path")
    if engine.load_image(image_path):
        # 4. Erstelle das Hauptfenster (root) von Tkinter
        root = tk.Tk()

        # 5. Erstelle die GUI und übergib ihr root, engine und die Einstellungen
        app = MosaicGUI(root, engine, app_settings)

        # 6. Starte die GUI mit der konfigurierten Starthöhe
        app.show_image(initial_height=app_settings.get("initial_height", 400))

        # 7. Starte die Tkinter-Ereignisschleife (hält das Fenster offen)
        root.mainloop()
    else:
        print(f"Das Bild unter '{image_path}' konnte nicht geladen werden.")


if __name__ == "__main__":
    main()
