import tkinter as tk
from PIL import Image, ImageTk


class MainMosaic:
    def __init__(self):
        self.image = None

    def load_image(self, path):
        """
        Lädt ein Bild von einem Pfad und speichert es für die weitere Bearbeitung.

        Unterstützte Formate hängen von Pillow ab, z. B.:
        JPG, JPEG, PNG, BMP, GIF, TIFF, WebP
        """
        try:
            self.image = Image.open(path)

            # Bilddaten tatsächlich einlesen und Datei danach schließen können
            self.image.load()

            # Einheitliches Format für spätere Bearbeitung
            if self.image.mode not in ("RGB", "RGBA"):
                self.image = self.image.convert("RGBA")

            print(f"Bild geladen: {path}")
            print(f"Größe: {self.image.size}")
            print(f"Format: {self.image.format}")

        except FileNotFoundError:
            print(f"Datei nicht gefunden: {path}")

        except Exception as e:
            print(f"Bild konnte nicht geladen werden: {e}")

    def show_image(self):
        if self.image is None:
            print("Kein Bild geladen.")
            return

        window = tk.Tk()
        window.title("MainMosaic")

        self.photo = ImageTk.PhotoImage(self.image)

        label = tk.Label(window, image=self.photo)
        label.pack()

        window.mainloop()


if __name__ == "__main__":
    Mosaic = MainMosaic()
    Mosaic.load_image("Bilder/Spiraling-snake-print.jpg")
    Mosaic.show_image()
