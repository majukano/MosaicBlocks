# mosaic_gui.py

import tkinter as tk
from PIL import Image, ImageTk


class MosaicGUI:
    """Verwaltet die Benutzeroberfläche und deren Events."""

    def __init__(self, engine):
        # Die GUI erhält eine Instanz der Engine, um auf Daten zugreifen zu können
        self.engine = engine

        self.photo = None
        self.label = None
        self.window = tk.Tk()

    def _resize_image(self, event):
        """
        Passt die Bildgröße an die Fenstergröße an, BEHÄLT aber das Seitenverhältnis bei.
        Greift auf Daten aus der Engine zu (self.engine.image etc.).
        """
        window_width = event.width
        window_height = event.height

        # Verhindert Fehler bei Minimierung des Fensters
        if window_width < 2 or window_height < 2:
            return

        window_aspect_ratio = window_width / window_height

        if window_aspect_ratio > self.engine.original_aspect_ratio:
            new_height = window_height
            new_width = int(new_height * self.engine.original_aspect_ratio)
        else:
            new_width = window_width
            new_height = int(new_width / self.engine.original_aspect_ratio)

        resized_photo = self.engine.image.resize((new_width, new_height), Image.LANCZOS)
        final_image = Image.new("RGBA", (window_width, window_height), (0, 0, 0, 255))
        paste_x = (window_width - new_width) // 2
        paste_y = (window_height - new_height) // 2
        final_image.paste(resized_photo, (paste_x, paste_y))

        self.photo = ImageTk.PhotoImage(final_image)
        self.label.config(image=self.photo)

    def show_image(self, initial_height):
        """Initialisiert und startet die GUI."""
        if self.engine.image is None:
            print("Kein Bild zum Anzeigen vorhanden.")
            return

        self.window.title("MosaicBlocks")
        self.window.minsize(100, 100)

        # Startgröße berechnen
        initial_width = int(initial_height * self.engine.original_aspect_ratio)
        initial_size = (initial_width, initial_height)

        resized_image = self.engine.image.resize(initial_size, Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_image)

        self.label = tk.Label(self.window, image=self.photo)
        self.label.pack(fill="both", expand=True)
        self.window.geometry(f"{initial_size[0]}x{initial_size[1]}")
        self.window.bind("<Configure>", self._resize_image)

        # Haupt-Event-Schleife starten
        self.window.mainloop()
