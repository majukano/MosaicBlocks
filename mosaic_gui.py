# mosaic_gui.py
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


class MosaicGUI:
    """Verwaltet die Benutzeroberfläche und nutzt übergebene JSON-Einstellungen."""

    def __init__(self, root, engine, settings):
        self.root = root
        self.engine = engine
        self.settings = settings

        self.photo_tk = None  # Referenz für das Tkinter-Bild
        self.image_to_display = None  # Das PIL-Bild, das gerade angezeigt wird
        self.is_mosaic_view = False  # Zustand für den Umschalter

        # --- Tkinter Variablen ---
        self.block_number_var = tk.StringVar(value="100")
        self.real_width_var = tk.StringVar(value="--")
        self.real_height_var = tk.StringVar(value="--")

        # --- UI-Elemente ---
        self.label_image = None
        self.btn_save_csv = None
        self.btn_toggle_view = None

        self._create_widgets()
        self._update_ui_state()
        self._apply_picsize()

    def _create_widgets(self):
        """Erstellt alle GUI-Elemente."""
        self.root.title(self.settings.get("window_title", "MosaicBlocks"))
        min_w = self.settings.get("window_min_width", 100)
        min_h = self.settings.get("window_min_height", 100)
        self.root.minsize(min_w + 220, min_h)  # Sidebar etwas breiter gemacht

        # === Linke Sidebar ===
        sidebar = tk.Frame(self.root, width=220, bg="#2e2e2e", padx=10, pady=10)
        sidebar.pack(side="left", fill="y", expand=False)
        sidebar.pack_propagate(False)

        # --- Bedienelemente ---
        tk.Label(
            sidebar,
            text="Steuerung",
            fg="white",
            bg="#2e2e2e",
            font=("Arial", 12, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        btn_load = tk.Button(
            sidebar,
            text="Bild laden...",
            command=self._load_new_image,
            bg="#007acc",
            fg="white",
        )
        btn_load.pack(fill="x", pady=(0, 10))

        tk.Label(
            sidebar, text="Mosaik-Breite (Blöcke):", fg="white", bg="#2e2e2e"
        ).pack(anchor="w")
        entry_blocks = tk.Entry(
            sidebar,
            textvariable=self.block_number_var,
            bg="#4a4a4a",
            fg="white",
            justify="center",
            insertbackground="white",
        )
        entry_blocks.pack(fill="x", pady=5)
        entry_blocks.bind("<Return>", self._apply_picsize)

        btn_apply = tk.Button(
            sidebar,
            text="Mosaik generieren",
            command=self._apply_mosaic,
            bg="#007acc",
            fg="white",
            font=("Arial", 10, "bold"),
        )
        btn_apply.pack(fill="x", pady=10)

        # --- Umschalter und Speichern-Button ---
        self.btn_toggle_view = tk.Button(
            sidebar,
            text="Zu Mosaik wechseln",
            command=self._toggle_view,
            bg="#5a5a5a",
            fg="white",
        )
        self.btn_toggle_view.pack(fill="x", pady=(10, 5))

        self.btn_save_csv = tk.Button(
            sidebar,
            text="CSV-Stückliste speichern",
            command=self._save_csv,
            bg="#5a5a5a",
            fg="white",
        )
        self.btn_save_csv.pack(fill="x", pady=5)

        # --- Frame für reale Größe ---
        output_frame = tk.LabelFrame(
            sidebar,
            text=" Reale Mosaikgröße ",
            padx=10,
            pady=10,
            bg="#2e2e2e",
            fg="white",
            font=("Arial", 9, "bold"),
        )
        output_frame.pack(fill="x", pady=(20, 0))

        tk.Label(output_frame, text="Breite:", bg="#2e2e2e", fg="white").grid(
            row=0, column=0, sticky="w"
        )
        tk.Label(
            output_frame,
            textvariable=self.real_width_var,
            font=("Arial", 10, "bold"),
            bg="#2e2e2e",
            fg="#00aaff",
        ).grid(row=0, column=1, sticky="w", padx=(10, 0))
        tk.Label(output_frame, text="Höhe:", bg="#2e2e2e", fg="white").grid(
            row=1, column=0, sticky="w", pady=(5, 0)
        )
        tk.Label(
            output_frame,
            textvariable=self.real_height_var,
            font=("Arial", 10, "bold"),
            bg="#2e2e2e",
            fg="#00aaff",
        ).grid(row=1, column=1, sticky="w", padx=(10, 0), pady=(5, 0))

        # === Rechter Bildbereich ===
        self.label_image = tk.Label(self.root, bg="black")
        self.label_image.pack(side="right", fill="both", expand=True)
        self.label_image.bind("<Configure>", self._resize_image_on_canvas)

    def _update_ui_state(self):
        """Aktualisiert den Zustand der Buttons (aktiv/inaktiv)."""
        has_mosaic = self.engine.mosaic_image is not None

        # Umschalter nur aktiv, wenn ein Mosaik existiert
        self.btn_toggle_view.config(state=tk.NORMAL if has_mosaic else tk.DISABLED)
        # CSV-Speichern nur aktiv, wenn Mosaikdaten vorhanden sind
        self.btn_save_csv.config(
            state=tk.NORMAL if self.engine.blocks_summary else tk.DISABLED
        )

        # Text des Umschalters anpassen
        if self.is_mosaic_view:
            self.btn_toggle_view.config(text="Zum Original wechseln")
        else:
            self.btn_toggle_view.config(text="Zu Mosaik wechseln")

    def _load_new_image(self):
        """Öffnet einen Dateidialog und lädt ein neues Bild."""
        file_path = filedialog.askopenfilename(
            title="Bild auswählen",
            filetypes=[
                ("Bilddateien", "*.jpg *.jpeg *.png *.bmp"),
                ("Alle Dateien", "*.*"),
            ],
        )
        if file_path:
            if self.engine.load_image(file_path):
                self.is_mosaic_view = False  # Beim Laden immer zum Original zurück
                self.show_image()  # Zeigt das neu geladene Originalbild
                self._apply_picsize()  # Berechnet die Größe neu
            else:
                messagebox.showerror("Fehler", "Das Bild konnte nicht geladen werden.")

    def _apply_mosaic(self):
        """Löst die Mosaikberechnung aus."""
        try:
            blocks_x = int(self.block_number_var.get())
            if blocks_x <= 0:
                messagebox.showwarning(
                    "Ungültige Eingabe", "Die Blockanzahl muss größer als Null sein."
                )
                return

            print("Mosaik-Effekt wird berechnet...")
            self.engine.generate_mosaic(blocks_x)

            # Automatisch zur Mosaik-Ansicht wechseln
            self.is_mosaic_view = True
            self.show_image()
            self._apply_picsize()  # Berechnet die Größe neu

        except ValueError:
            messagebox.showerror(
                "Fehler", "Bitte geben Sie eine gültige Zahl für die Blockanzahl ein."
            )
        except Exception as e:
            messagebox.showerror(
                "Fehler", f"Ein unerwarteter Fehler ist aufgetreten: {e}"
            )

    def _toggle_view(self):
        """Wechselt die Ansicht zwischen Original und Mosaik."""
        self.is_mosaic_view = not self.is_mosaic_view
        self.show_image()

    def _save_csv(self):
        """Speichert die Mosaik-Stückliste als CSV-Datei."""
        file_path = filedialog.asksaveasfilename(
            title="CSV-Stückliste speichern unter...",
            defaultextension=".csv",
            filetypes=[("CSV-Dateien", "*.csv")],
            initialfile="webrick_parts_list.csv",
        )
        if file_path:
            if self.engine.export_to_webrick_csv(file_path):
                messagebox.showinfo(
                    "Erfolg",
                    f"Die Stückliste wurde erfolgreich unter\n{file_path}\ngespeichert.",
                )
            else:
                messagebox.showerror(
                    "Fehler", "Die CSV-Datei konnte nicht exportiert werden."
                )

    def show_image(self, initial_height=None):
        """Zeigt das aktuell ausgewählte Bild an (Original oder Mosaik)."""
        if initial_height:
            initial_width = (
                int(initial_height * self.engine.original_aspect_ratio) + 220
            )
            self.root.geometry(f"{initial_width}x{initial_height}")

        if self.is_mosaic_view and self.engine.mosaic_image:
            self.image_to_display = self.engine.mosaic_image
        else:
            self.image_to_display = self.engine.original_image

        self._update_ui_state()  # Aktualisiert Button-Zustände
        self._resize_image_on_canvas()

    def _resize_image_on_canvas(self, event=None):
        """Skaliert das Anzeigebild neu, wenn sich die Fenstergröße ändert."""
        if self.image_to_display is None:
            return

        label_w, label_h = (
            self.label_image.winfo_width(),
            self.label_image.winfo_height(),
        )
        if label_w < 2 or label_h < 2:
            return

        img_w, img_h = self.image_to_display.size
        aspect_ratio = img_w / img_h

        if label_w / label_h > aspect_ratio:
            new_h = label_h
            new_w = int(new_h * aspect_ratio)
        else:
            new_w = label_w
            new_h = int(new_w / aspect_ratio)

        resized_img = self.image_to_display.resize((new_w, new_h), Image.LANCZOS)

        bg_color = tuple(self.settings.get("background_color", (0, 0, 0, 255)))
        final_image = Image.new("RGBA", (label_w, label_h), bg_color)

        paste_x = (label_w - new_w) // 2
        paste_y = (label_h - new_h) // 2
        final_image.paste(resized_img, (paste_x, paste_y))

        self.photo_tk = ImageTk.PhotoImage(final_image)
        self.label_image.config(image=self.photo_tk)

    def _apply_picsize(self, event=None):
        """Aktualisiert die Anzeige der realen Größe."""
        try:
            blocks_x_str = self.block_number_var.get()
            real_width, real_height = self.engine.calc_real_size(blocks_x_str)
            self.real_width_var.set(f"{real_width:.1f} mm")
            self.real_height_var.set(f"{real_height:.1f} mm")
        except ValueError:
            self.real_width_var.set("Ungültig")
            self.real_height_var.set("Ungültig")
        except Exception:
            self.real_width_var.set("--")
            self.real_height_var.set("--")
