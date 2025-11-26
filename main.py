import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os 
from bird_species import BirdSpecies


class ImageCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Bird Cropper v9001")
        self.root.geometry("1000x1000")
        self.radiobuttons_list = []
        
        # Control panel
        control_frame = tk.Frame(root, bg="#f0f0f0", pady=10)
        control_frame.pack(fill="both")

        # Radio Button Variable
        self.ext_var = tk.StringVar(value=BirdSpecies.SPECIES_1.value)

        # UI Elements
        tk.Label(control_frame, text="Species:", bg="#f0f0f0").pack(side="left", padx=10)
        
        # Creates radio buttons for different bird species
        # You can modify bird species at bird_species.py
        for v in BirdSpecies:
            if v.value == BirdSpecies.EMPTY.value:
                continue
            radiobtn = tk.Radiobutton(control_frame, text=v.value, variable=self.ext_var, value=v.value, bg='#f0f0f0') 
            radiobtn.pack(side='left')
            self.radiobuttons_list.append(radiobtn)
      
            
            # self.radiobtn_bird_ = tk.Radiobutton(control_frame, text=v.value, variable=self.ext_var, 
            #            value=v.value, bg="#f0f0f0").pack(side="left")

        # Original photos folder button    
        self.btn_select_image_folder = tk.Button(control_frame, text="Select bird image folder", 
                  command=self.load_image)
        self.btn_select_image_folder.pack(side="left", padx=20)
        

        # Delete image button
        self.btn_delete_image = tk.Button(control_frame, text="Delete image", command=self.delete_image, state="disabled")
        self.btn_delete_image.pack(side="left", padx=20)

        # Save empty
        self.btn_save_empty = tk.Button(control_frame, text="Save empty", command=self.save_empty, state="disabled")
        self.btn_save_empty.pack(side="left", padx=10)

        # Original image save button
        self.btn_save_original = tk.Button(control_frame, text="Save original", command=self.save_original, state="disabled")
        self.btn_save_original.pack(side="left", padx=10)

        # Crop save button
        self.btn_save = tk.Button(control_frame, text="Save Selection", command=self.save_crop, state="disabled", bg="lightblue")
        self.btn_save.pack(side="left")
        
        # Next image button
        self.btn_next = tk.Button(control_frame, text="Next image", command=self.change_to_next)
        self.btn_next.pack(side="left", padx=20)


        # Keyboard button binds to make the sorting a bit faster
        for x in range(len(self.radiobuttons_list)):
            self.root.bind(f"{x+1}", lambda event, b=self.radiobuttons_list[x]: b.invoke())

        self.root.bind("<Shift_L>", lambda event: self.btn_next.invoke())
        self.root.bind("<space>", lambda event: self.btn_save.invoke())
        self.root.bind("e", lambda event: self.btn_save_empty.invoke())
        self.root.bind("q", lambda event: self.btn_delete_image.invoke())


        # Main canvas
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
        self.current_img_name = None
        self.img_dirpath = None
        self.handled_dir = None
        self.save_root_dirpath = None


    def load_image(self):
        # Select og image directory if not selected already
        if self.img_dirpath is None:
            self.img_dirpath = filedialog.askdirectory()
            self.btn_select_image_folder.config(state="disabled")

        # Creates new folder for handled images. Moves the handled images into this folder
        self.handled_dir = self.img_dirpath + "/" + "handled"
        if not os.path.isdir(self.handled_dir):
            os.mkdir(self.handled_dir)

        # Reads all the files from the selected og image folder. Ignores folders
        folder_contents = [f for f in os.listdir(self.img_dirpath) if os.path.isfile(os.path.join(self.img_dirpath, f))]


        for i in folder_contents:
            # Load image with PIL
            if self.image_opened is None:
                try:
                    # creates the path to image
                    image_path = self.img_dirpath + "/" + i

                    # Checks if the file is valid image file
                    self.image_opened = Image.open(image_path)
                    self.image_opened.verify()

                    # Verify changes the image to None type so it must be opened again
                    self.image_opened = Image.open(image_path)
                    
                    print(f"File: {os.path.basename(self.image_opened.filename)}")
                    # Convert to Tkinter compatible image
                    self.tk_image = ImageTk.PhotoImage(self.image_opened)


                    
                    #self.root.geometry(f"{min(w, 1200)}x{min(h+50, 900)}")
                    
                    # Draw image on canvas
                    w, h = self.image_opened.size
                    self.canvas.config(width=w, height=h)
                    self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")

                    # Enable buttons
                    self.btn_save.config(state="normal")
                    self.btn_save_original.config(state="normal")
                    self.btn_save_empty.config(state="normal")
                    self.btn_delete_image.config(state="normal")

                except Exception as e:
                    print(e)
                    continue
        


    def on_mouse_down(self, event):
        # Start recording the selection
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        
        # Create a rectangle around the selection
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
        
        if self.save_root_dirpath is None:
            self.save_root_dirpath = filedialog.askdirectory(title="Select save directory")

        
        # Calculate coordinates ensuring no negative widths
        left = min(self.start_x, self.cur_x)
        top = min(self.start_y, self.cur_y)
        right = max(self.start_x, self.cur_x)
        bottom = max(self.start_y, self.cur_y)

        # Check if selection is valid
        if right - left < 5 or bottom - top < 5:
            messagebox.showwarning("Warning", "Selection too small!")
            return

        # Crop using the original PIL image
        crop = self.image_opened.crop((left, top, right, bottom))
        
        # Save file
        ext = self.ext_var.get()
        
        save_dir = self.save_root_dirpath + "/" + ext.lower()
        if not os.path.isdir(save_dir):
            os.mkdir(save_dir)

        try:
            crop.save(self.get_unique_filename(save_dir + "/" + os.path.basename(self.image_opened.filename)))
            print("Successfully saved image!")
        except Exception as e:
            print(f"Failed to save image: {e}")

    # Saves image without cropping
    def save_original(self):
        if self.image_opened is None:
            return
        
        if self.save_root_dirpath is None:
            self.save_root_dirpath = filedialog.askdirectory(title="Select save directory")

        # Save file
        ext = self.ext_var.get()
        
        save_dir = self.save_root_dirpath + "/" + ext.lower()
        if not os.path.isdir(save_dir):
            os.mkdir(save_dir)

        try:
            self.image_opened.save(self.get_unique_filename(save_dir + "/" + os.path.basename(self.image_opened.filename)))
            print("Successfully saved image!")
            self.change_to_next()
        except Exception as e:
            print(f"Failed to save image: {e}")
    

    # Saves image that doesn't have any birds to "empty" folder
    def save_empty(self):
        if self.image_opened is None:
            return
        
        if self.save_root_dirpath is None:
            self.save_root_dirpath = filedialog.askdirectory(title="Select save directory")

        # Checks if the "empty" folder exists. If not, creates it
        save_dir = self.save_root_dirpath + "/" + BirdSpecies.EMPTY.value.lower()
        if not os.path.isdir(save_dir):
            os.mkdir(save_dir)
        
        try:
            self.image_opened.save(save_dir + "/" + os.path.basename(self.image_opened.filename))
            self.change_to_next()
        except Exception as e:
            print(f"Failed to save image: {e}")
    

    # Deletes current image
    def delete_image(self):
        if self.image_opened is None:
            return
        
        os.remove(self.image_opened.filename)
        self.image_opened = None
        self.load_image()

    # Moves current image into handled folder and changes to next image
    def change_to_next(self):
        os.replace(self.image_opened.filename, self.get_unique_filename(self.handled_dir + "/" + os.path.basename(self.image_opened.filename)))
        self.image_opened = None
        self.load_image()

    def get_unique_filename(self, filename):
        if not os.path.exists(filename):
            return filename
        
        base_name, extension = os.path.splitext(filename)
        counter = 1

        while True:
            # Format the counter with 2 digits (01, 02, ... 10)
            new_filename = f"{base_name}_{counter:02d}{extension}"
            
            if not os.path.exists(new_filename):
                return new_filename
                
            counter += 1
        

# Run the App
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCropper(root)
    root.mainloop()