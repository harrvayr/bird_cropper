import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from os import listdir
from os.path import isfile, join
from enum import Enum

class BirdSpecies(Enum):
    SPECIES_1 = "talitintti"
    SPECIES_2 = "punatulkku"
    EMPTY = "empty"

class ImageCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Bird Cropper v9001")
        
        # --- 1. Control Panel (Top) ---
        control_frame = tk.Frame(root, bg="#f0f0f0", pady=10)
        control_frame.pack(fill="x")

        # Radio Button Variable
        self.ext_var = tk.StringVar(value=BirdSpecies.SPECIES_1.value)

        # UI Elements
        tk.Label(control_frame, text="Format:", bg="#f0f0f0").pack(side="left", padx=10)
        
        # Luo radiobuttonit lintulajeille
        for v in BirdSpecies:
            tk.Radiobutton(control_frame, text=v.value, variable=self.ext_var, 
                       value=v.value, bg="#f0f0f0").pack(side="left")
            
        tk.Button(control_frame, text="Select bird image folder", 
                  command=self.load_image).pack(side="left", padx=20)
        
        self.btn_save = tk.Button(control_frame, text="Save Selection", 
                                  command=self.save_crop, state="disabled", bg="lightblue")
        self.btn_save.pack(side="left")

        # --- 2. Image Canvas (Main Area) ---
        self.canvas = tk.Canvas(root, cursor="cross")
        self.canvas.pack(fill="both", expand=True)

        # Mouse Events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # State variables
        self.rect_id = None
        self.start_x = 0
        self.start_y = 0
        self.cur_x = 0
        self.cur_y = 0
        self.image_opened = None  # The PIL Image object
        self.tk_image = None      # The Tkinter display object
        self.img_dirpath = None
        self.save_dirpath = None

    def load_image(self):
        # Valitaan lintukuvien kansio
        self.img_dirpath = filedialog.askdirectory()
        if self.img_dirpath is None:
            return

        # Lukee tiedostot kansiosta
        folder_contents = [f for f in listdir(self.img_dirpath) if isfile(join(self.img_dirpath, f))]


        for i in folder_contents:
            # Load image with PIL
            if self.image_opened is None:
                try:

                    image_path = self.img_dirpath + "/" + i

                    # Tarkastetaan onko tiedosto kuva ja aukaistaan se sen jälkeen. Heittää erroria jos ei ole kuva.
                    self.image_opened = Image.open(image_path)
                    self.image_opened.verify()

                    # Verify muuttaa kuvan tyypiksi None, joten se täytyy avata uusiksi jotta sen saa takaisin kuvaksi.
                    self.image_opened = Image.open(image_path)

                    # Convert to Tkinter compatible image
                    self.tk_image = ImageTk.PhotoImage(self.image_opened)

                    # Resize window to fit image (optional limitation)
                    w, h = self.image_opened.size
                    print(self.image_opened.size)
                    self.root.geometry(f"{min(w, 1200)}x{min(h+50, 900)}")
                    
                    # Draw image on canvas
                    self.canvas.config(width=w, height=h)
                    self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")
                    self.btn_save.config(state="normal")

                except Exception as e:
                    print(e)
                    pass
        


    def on_mouse_down(self, event):
        # Start recording the selection
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        
        # Create a rectangle (outline only)
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)

    def on_mouse_drag(self, event):
        # Update the rectangle size as you drag
        self.cur_x = self.canvas.canvasx(event.x)
        self.cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, self.cur_x, self.cur_y)

    def on_mouse_up(self, event):
        # Finalize coordinates
        self.cur_x = self.canvas.canvasx(event.x)
        self.cur_y = self.canvas.canvasy(event.y)

    def save_crop(self):
        if self.image_opened is None:
            return
        
        if self.save_dirpath is None:
            self.save_dirpath = filedialog.askdirectory(title="Select save directory")

        
        # Calculate coordinates ensuring no negative widths
        left = min(self.start_x, self.cur_x)
        top = min(self.start_y, self.cur_y)
        right = max(self.start_x, self.cur_x)
        bottom = max(self.start_y, self.cur_y)

        # Check if selection is valid
        if right - left < 5 or bottom - top < 5:
            messagebox.showwarning("Warning", "Selection too small!")
            return

        print(f"left: {left}, right: {right}, top: {top}, bottom: {bottom}")
        # Crop using the original PIL image
        crop = self.image_opened.crop((left, top, right, bottom))
        
        # Save file
        ext = self.ext_var.get()

        match self.ext_var.get():
            case ".jpg":
                save_path = os.getdir
        save_path = filedialog.asksaveasfilename(defaultextension=ext, 
                                                 filetypes=[(ext.upper(), f"*{ext}")])
        if save_path:
            crop.save(save_path)
            messagebox.showinfo("Success", f"Saved to {save_path}")

    # Tyhjän kuvan tallennus napilla
    def save_empty(self):
        if self.image_opened is None:
            return
        
        if self.save_dirpath is None:
            self.save_dirpath = filedialog.askdirectory(title="Select save directory")

# Run the App
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCropper(root)
    root.mainloop()