# mosaic_generator.py
from PIL import Image, ImageDraw
from collections import defaultdict
import cv2
import numpy as np


class MosaicGenerator:
    def __init__(self, palette):
        """
        palette: Eine Liste von RGB-Tupeln, z.B. [(255, 0, 0), (0, 255, 0), ...]
        """
        self.palette = palette
        # Cache für schnellere Farbsuche
        self.color_cache = {}

    def _get_closest_palette_color_simple(self, pixel_rgb):
        """
        Findet die Farbe aus der Palette, die der übergebenen Farbe am nächsten ist.
        Nutzt einen Cache, um wiederholte Berechnungen zu vermeiden.
        """
        # Falls RGBA, ignoriere Alpha
        pixel_rgb = pixel_rgb[:3]
        if pixel_rgb in self.color_cache:
            return self.color_cache[pixel_rgb]

        r1, g1, b1 = pixel_rgb
        min_distance = float("inf")
        best_color = self.palette[0]

        for color in self.palette:
            r2, g2, b2 = color
            distance = (
                (2 * (r1 - r2) ** 2) + (7 * (g1 - g2) ** 2) + (3 * (b1 - b2) ** 2)
            )

            if distance < min_distance:
                min_distance = distance
                best_color = color

        self.color_cache[pixel_rgb] = best_color
        return best_color

    def _get_closest_palette_color(self, pixel_rgb):
        """
        Findet die Farbe aus der Palette, die der übergebenen Farbe am nächsten ist.
        Beinhaltet eine spezielle Regel für Schwarz, um die CIELAB-Ungenauigkeit zu korrigieren.
        Nutzt einen Cache für bessere Performance.
        """
        # Erzwinge, dass der RGB-Wert immer ein Tupel ist, um das Caching zu sichern.
        pixel_rgb = tuple(pixel_rgb[:3])

        # 1. Prüfe den Cache für bekannte Farben
        if pixel_rgb in self.color_cache:
            return self.color_cache[pixel_rgb]

        # 2. Ausnahmeregel für Schwarz
        #    LEGO-Schwarz ist (27, 42, 52), Dunkelbraun ist (54, 30, 13).
        #    Die Helligkeit (Luminanz) hilft, sie zu unterscheiden. Reines Schwarz (0,0,0)
        #    ist rechnerisch näher am dunklen Braun. Wir korrigieren das hier.
        #    Ein Helligkeits-Schwellenwert von unter 30 deckt die meisten schwarzen
        #    Farbtöne ab, ohne dunkle Farben wie "Dark Brown" oder "Dark Blue" fälschlicherweise
        #    zu erfassen.
        r, g, b = pixel_rgb
        brightness = 0.299 * r + 0.587 * g + 0.114 * b

        if brightness < 30:
            # Weise den Pixel direkt der Farbe "Schwarz" aus der Palette zu.
            # RGB-Wert für "Schwarz": (27, 42, 52)
            best_color = (27, 42, 52)
            self.color_cache[pixel_rgb] = best_color
            return best_color

        # 3. Wenn nicht schwarz, führe die normale CIELAB-Berechnung durch
        #    Dies bleibt der beste Weg für alle anderen Farben.
        pixel_lab = cv2.cvtColor(np.uint8([[pixel_rgb]]), cv2.COLOR_RGB2LAB)[0][0]

        min_distance = float("inf")
        best_color = self.palette[0]

        # Wir nutzen die CIELAB-konvertierten Farben der Palette für den Vergleich.
        for color in self.palette:
            # Konvertiere jede Palettenfarbe in den CIELAB-Raum
            color_lab = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_RGB2LAB)[0][0]
            # Berechne die euklidische Distanz im LAB-Raum
            distance = np.linalg.norm(pixel_lab.astype(float) - color_lab.astype(float))

            if distance < min_distance:
                min_distance = distance
                best_color = color

        # 4. Speichere das Ergebnis im Cache und gib es zurück
        self.color_cache[pixel_rgb] = best_color
        return best_color

    def create_mosaic(self, image, blocks_x):
        """
        Erstellt das Mosaikbild und gibt eine Zusammenfassung der Farben zurück.
        image: Ein PIL Image-Objekt.
        blocks_x: Anzahl der Kacheln in der Breite.
        Returns: Ein Tupel (mosaic_img, blocks_summary)
        """
        img = image.convert("RGB")
        width, height = img.size

        block_size_px = width / blocks_x
        blocks_y = int(height / block_size_px)

        mosaic_img = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(mosaic_img)

        blocks_summary = defaultdict(int)

        for x_idx in range(blocks_x):
            for y_idx in range(blocks_y):
                left = int(x_idx * block_size_px)
                top = int(y_idx * block_size_px)
                right = int(min((x_idx + 1) * block_size_px, width))
                bottom = int(min((y_idx + 1) * block_size_px, height))

                if right <= left or bottom <= top:
                    continue

                box = (left, top, right, bottom)
                tile = img.crop(box)

                tile_tiny = tile.resize((1, 1), Image.Resampling.BOX)
                avg_color = tile_tiny.getpixel((0, 0))

                best_color = self._get_closest_palette_color(avg_color)
                blocks_summary[best_color] += 1

                draw.rectangle([left, top, right, bottom], fill=best_color)

        return mosaic_img, dict(blocks_summary)
