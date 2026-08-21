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
        Nutzt einen Cache, um wiederholte Berechnungen zu vermeiden.
        CIELAB-optimiert via OpenCV, um Farbmischungen (z. B. Grün/Grau) zu verhindern.
        """
        # Falls RGBA, ignoriere Alpha
        pixel_rgb = pixel_rgb[:3]

        if pixel_rgb in self.color_cache:
            return self.color_cache[pixel_rgb]

        # 1. Konvertiere die Ziel-RGB-Farbe in den LAB-Farbraum
        # cv2.cvtColor erwartet ein 3D-Array [Höhe, Breite, Kanäle] vom Typ uint8
        pixel_lab = cv2.cvtColor(np.uint8([[pixel_rgb]]), cv2.COLOR_RGB2LAB)[0][0]

        min_distance = float("inf")
        best_color = self.palette[0]

        # 2. Iteriere durch die Farbpalette
        for color in self.palette:
            # Konvertiere die Palettenfarbe in den LAB-Farbraum
            color_lab = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_RGB2LAB)[0][0]

            # 3. Berechne den euklidischen Abstand im LAB-Raum (Delta E* 76)
            # Wir casten zu float, um Berechnungsfehler durch uint8-Überläufe zu vermeiden
            distance = np.linalg.norm(pixel_lab.astype(float) - color_lab.astype(float))

            if distance < min_distance:
                min_distance = distance
                best_color = color

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
