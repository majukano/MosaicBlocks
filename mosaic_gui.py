# mosaic_gui.py

import tkinter as tk

from PIL import Image, ImageTk


class MosaicGUI:
    """Verwaltet die Benutzeroberfläche und nutzt übergebene JSON-Einstellungen."""

    def __init__(self, engine, settings):
        self.engine = engine
        # Speichere das Einstellungs-Dictionary ab
        self.settings = settings

        self.photo = None
        self.label = None
        self.window = tk.Tk()
        self.block_number_var = tk.StringVar(value="100")

    def _resize_image(self, event):
        label_width = self.label.winfo_width()
        label_height = self.label.winfo_height()

        if label_width < 2 or label_height < 2:
            return

        label_aspect_ratio = label_width / label_height

        if label_aspect_ratio > self.engine.original_aspect_ratio:
            new_height = label_height
            new_width = int(new_height * self.engine.original_aspect_ratio)
        else:
            new_width = label_width
            new_height = int(new_width / self.engine.original_aspect_ratio)

        resized_photo = self.engine.image.resize((new_width, new_height), Image.LANCZOS)

        # NUTZUNG DER JSON-EINSTELLUNG: background_color
        bg_color = self.settings.get("background_color", (0, 0, 0, 255))
        final_image = Image.new("RGBA", (label_width, label_height), bg_color)

        paste_x = (label_width - new_width) // 2
        paste_y = (label_height - new_height) // 2
        final_image.paste(resized_photo, (paste_x, paste_y))

        self.photo = ImageTk.PhotoImage(final_image)
        self.label.config(image=self.photo)

    def show_image(self, initial_height):
        if self.engine.image is None:
            print("Kein Bild zum Anzeigen vorhanden.")
            return

        self.window.title(self.settings.get("window_title", "MosaicBlocks"))

        min_w = self.settings.get("window_min_width", 100)
        min_h = self.settings.get("window_min_height", 100)

        # Die Mindestbreite des Fensters wird um 200 Pixel erhöht, damit die
        # Sidebar links immer vollständig sichtbar bleibt und nicht gequetscht wird.
        self.window.minsize(min_w + 200, min_h)

        # -------------------------------------------------------------
        # HINZUGEFÜGT: DER KOMPLETTE SIDEBAR-BEREICH (LINKS)
        # -------------------------------------------------------------
        # 1. Erstellen des Containers für die linke Leiste
        sidebar = tk.Frame(self.window, width=200, bg="#2e2e2e", padx=10, pady=10)
        sidebar.pack(side="left", fill="y", expand=False)
        sidebar.pack_propagate(False)  # Verhindert automatisches Zusammenziehen

        # 2. Überschrift
        lbl_title = tk.Label(
            sidebar,
            text="Einstellungen",
            fg="white",
            bg="#2e2e2e",
            font=("Arial", 12, "bold"),
        )
        lbl_title.pack(anchor="w", pady=(0, 20))

        # 3. Button für Bildauswahl
        # btn_load = tk.Button(
        #     sidebar,
        #     text="Neues Bild laden",
        #     command=self._open_file_dialog,
        #     bg="#4a4a4a",
        #     fg="white",
        # )
        # btn_load.pack(fill="x", pady=(0, 20))

        # 4. Text für Slider
        lbl_mosaic = tk.Label(
            sidebar, text="Mosaik-Blockgröße:", fg="white", bg="#2e2e2e"
        )
        lbl_mosaic.pack(anchor="w")

        # 5. Slider-Element (Skala von 5 bis 100 Pixel)
        entry_blocks = tk.Entry(
            sidebar,
            textvariable=self.block_number_var,  # Verknüpft mit der StringVar
            bg="#4a4a4a",
            fg="white",
            justify="center",  # Zentriert den Text im Feld
            insertbackground="white",  # Farbe des Cursors
        )
        entry_blocks.pack(fill="x", pady=(5, 20))
        # entry_blocks.bind("<Return>", self._apply_mosaic)

        # 6. Button zum Ausführen
        btn_apply = tk.Button(
            sidebar,
            text="Start",
            command=self._apply_mosaic,
            bg="#007acc",
            fg="white",
            font=("Arial", 10, "bold"),
        )
        btn_apply.pack(fill="x", pady=(10, 0))
        # -------------------------------------------------------------

        # Wir platzieren das Bild-Label nun explizit auf der rechten Seite ("right")
        # und füllen den verbleibenden Platz aus ("both", expand=True).
        self.label = tk.Label(self.window, bg="black")
        self.label.pack(side="right", fill="both", expand=True)

        # Die Startbreite des Fensters muss um die 200 Pixel der Sidebar
        # vergrößert werden, damit das Bild beim Start nicht zusammengestaucht wird.
        initial_width = int(initial_height * self.engine.original_aspect_ratio) + 200
        self.window.geometry(f"{initial_width}x{initial_height}")

        # Das Configure-Event (Größenänderung) wird nun an das Bild-Label gebunden.
        # Dadurch wird das Bild nur neu skaliert, wenn sich die Arbeitsfläche rechts
        # verändert, und nicht, wenn sich in der Sidebar links etwas tut (bessere Performance!).
        self.label.bind("<Configure>", self._resize_image)
        self.window.mainloop()

    def _apply_mosaic(self):
        """Löst die Mosaikberechnung aus."""
        # block_size = self.block_size_var.get()
        print("Mosaik-Effekt berechnen mit Blockgröße:")
        # Hier später die Rechenmethode der Engine aufrufen:
        # self.engine.image = self.engine.apply_mosaic_effect(block_size)
        # self._force_ui_update()
