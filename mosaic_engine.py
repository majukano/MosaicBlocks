# mosaic_engine.py

from PIL import Image


class MosaicEngine:
    """Verwaltet die Bilddaten und Berechnungen."""

    def __init__(self):
        self.image = None
        self.original_aspect_ratio = 1.0  # Standardwert

    def load_image(self, path):
        """
        Lädt ein Bild von einem Pfad und speichert es für die weitere Bearbeitung.
        Gibt True bei Erfolg und False bei einem Fehler zurück.
        """
        try:
            self.image = Image.open(path)
            self.image.load()

            if self.image.mode not in ("RGB", "RGBA"):
                self.image = self.image.convert("RGBA")

            self.original_aspect_ratio = self.image.width / self.image.height

            print(f"Bild geladen: {path}")
            print(f"Größe: {self.image.size}")
            print(f"Format: {self.image.format}")
            return True

        except FileNotFoundError:
            print(f"Datei nicht gefunden: {path}")
            return False
        except Exception as e:
            print(f"Bild konnte nicht geladen werden: {e}")
            return False
