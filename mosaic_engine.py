# mosaic_engine.py
import csv
from PIL import Image
from mosaic_generator import MosaicGenerator
from webrick_palette import WEBRICK_MOSAIC_PALETTE


class MosaicEngine:
    """Verwaltet die Bilddaten und Berechnungen."""

    def __init__(self, settings):
        self.original_image = None
        self.mosaic_image = None
        self.original_aspect_ratio = 1.0
        self.settings = settings
        self.blocks_summary = None  # Zum Speichern der Farb-Anzahl für den CSV-Export

        # Den Generator mit der Farbpalette aus der separaten Datei initialisieren
        palette = list(WEBRICK_MOSAIC_PALETTE.keys())
        self.generator = MosaicGenerator(palette)

    def load_image(self, path):
        """
        Lädt ein Bild von einem Pfad, speichert es als Originalbild und für die Bearbeitung.
        Gibt True bei Erfolg und False bei einem Fehler zurück.
        """
        if not path:
            return False
        try:
            image = Image.open(path)
            image.load()

            # Zurücksetzen, wenn ein neues Bild geladen wird
            self.mosaic_image = None
            self.blocks_summary = None

            if image.mode not in ("RGB", "RGBA"):
                self.original_image = image.convert("RGBA")
            else:
                self.original_image = image

            self.original_aspect_ratio = (
                self.original_image.width / self.original_image.height
            )

            print(f"Bild geladen: {path}")
            print(f"Größe: {self.original_image.size}")
            return True

        except FileNotFoundError:
            print(f"Datei nicht gefunden: {path}")
            return False
        except Exception as e:
            print(f"Bild konnte nicht geladen werden: {e}")
            return False

    def generate_mosaic(self, blocks_x):
        """
        Erzeugt das Mosaikbild mithilfe des MosaicGenerators.
        """
        if (
            self.original_image is None
            or not isinstance(blocks_x, int)
            or blocks_x <= 0
        ):
            return

        # Die create_mosaic Methode des Generators aufrufen
        mosaic_img, summary = self.generator.create_mosaic(
            self.original_image, blocks_x
        )

        self.mosaic_image = mosaic_img
        self.blocks_summary = summary
        print(f"Mosaik mit {blocks_x} Blöcken in der Breite erstellt.")

    def calc_real_size(self, blocks_x_str):
        """Berechnet Werte basierend auf der Eingabe."""
        if not blocks_x_str.isdigit():
            raise ValueError("Eingabe ist keine gültige Zahl.")

        blocks_x = int(blocks_x_str)
        if self.original_image is None or self.original_aspect_ratio == 0:
            return (0, 0)

        block_size_mm = self.settings.get("block_size", 8)
        real_size_x_mm = block_size_mm * blocks_x
        real_size_y_mm = block_size_mm * blocks_x / self.original_aspect_ratio
        return (real_size_x_mm, real_size_y_mm)

    def export_to_webrick_csv(self, filename="webrick_parts_list.csv"):
        """
        Exportiert die Teileliste im Webrick-Format.
        """
        if not self.blocks_summary:
            print("Keine Mosaikdaten zum Exportieren vorhanden.")
            return False

        # 3024 ist die offizielle LEGO/LDraw-Design-ID für eine "Plate 1x1"
        PART_ID_PLATE_1X1 = "3024"

        # Webrick Custom Made Sheets benötigen: Part (LDraw ID), Color (Lego ID), Quantity
        header = ["Part", "Color", "Quantity"]

        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(header)

            for rgb_color, quantity in self.blocks_summary.items():
                if rgb_color in WEBRICK_MOSAIC_PALETTE:
                    color_info = WEBRICK_MOSAIC_PALETTE[rgb_color]
                    writer.writerow(
                        [PART_ID_PLATE_1X1, color_info["lego_id"], quantity]
                    )

        print(f"Teileliste erfolgreich exportiert: {filename}")
        return True
