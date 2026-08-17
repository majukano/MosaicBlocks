# main.py

from mosaic_engine import MosaicEngine
from mosaic_gui import MosaicGUI

if __name__ == "__main__":
    # 1. Erstelle eine Instanz der Rechen-Engine
    engine = MosaicEngine()

    # 2. Lade das Bild über die Engine.
    # Der Pfad muss für Ihr System korrekt sein.
    if engine.load_image("Bilder/Test1.jpg"):
        # 3. Erstelle die GUI und übergib ihr die Engine-Instanz
        app = MosaicGUI(engine)

        # 4. Starte die Anzeige
        app.show_image(initial_height=400)
    else:
        print("Anwendung konnte nicht gestartet werden, da das Bild fehlt.")
