# main.py
import json
import os
from mosaic_engine import MosaicEngine
from mosaic_gui import MosaicGUI

SETTINGS_FILE = "settings.json"

# Definiere feste "Fallback"-Standards für den Fall, dass die JSON-Datei fehlt
DEFAULT_SETTINGS = {
    "default_image_path": "Bilder/Test1.jpg",
    "initial_height": 400,
    "window_min_width": 100,
    "window_min_height": 100,
    "window_title": "MosaicBlocks",
    "background_color": [0, 0, 0, 255],
    "block_size": 8,  # [mm]
}


def load_settings():
    """Lädt die Einstellungen aus der JSON-Datei.
    Erstellt eine neue Datei mit Standardwerten, falls keine existiert."""
    if not os.path.exists(SETTINGS_FILE):
        try:
            # Falls die Datei gelöscht wurde, schreiben wir die Defaults neu
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
            # Konvertiere die Hintergrundfarbe von einer JSON-Liste in ein Python-Tupel
            if "background_color" in settings:
                settings["background_color"] = tuple(settings["background_color"])
            print("Einstellungen erfolgreich geladen.")
            return settings
    except Exception as e:
        print(f"Fehler beim Lesen der JSON-Datei. Nutze Fallback-Defaults. Fehler: {e}")
        return DEFAULT_SETTINGS


if __name__ == "__main__":
    # 1. Lade Einstellungen aus der JSON-Datei
    app_settings = load_settings()

    # 2. Instanziiere die Engine
    engine = MosaicEngine()

    # 3. Lade das Bild über den Pfad aus den Einstellungen
    image_path = app_settings.get("default_image_path")
    if engine.load_image(image_path):
        # 4. Erstelle die GUI und übergib ihr die Engine UND die geladenen Einstellungen
        app = MosaicGUI(engine, app_settings)

        # 5. Starte die GUI mit der konfigurierten Starthöhe
        app.show_image(initial_height=app_settings.get("initial_height", 400))
    else:
        print(f"Das Bild unter '{image_path}' konnte nicht geladen werden.")
