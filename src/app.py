from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import random
import shutil
import logging
from typing import List, Dict

class FileMover:
    def __init__(self):
        # Initialize main window
        self.window = tk.Tk()
        self.window.title("Random File Mover")
        self.window.geometry("800x1200")
        self.window.configure(bg='#1E1E1E')
        
        # Initialize instance variables
        self.current_image_path = None
        self._last_window_size = None
        
        # Configure window style
        style = ttk.Style()
        style.theme_use('default')
        
        # Define colors and styling
        style.configure('.',
            background='#1E1E1E',
            foreground='#FFFFFF',
            fieldbackground='#2D2D2D',
            troughcolor='#2D2D2D')
        
        style.configure('TFrame', 
            background='#1E1E1E')
            
        style.configure('TLabelframe', 
            background='#1E1E1E',
            foreground='#FFFFFF')
            
        style.configure('TLabelframe.Label', 
            background='#1E1E1E',
            foreground='#FFFFFF')
            
        style.configure('TButton',
            background='#264F78',
            foreground='#FFFFFF',
            padding=5)
            
        # Bind events
        self.window.bind('<Configure>', self._on_window_resize)
        
        # Entry styling
        style.configure('TEntry',
            fieldbackground='#3C3C3C',
            foreground='#FFFFFF',
            padding=5)
        
        # Combobox styling
        style.configure('TCombobox',
            fieldbackground='#3C3C3C',
            background='#3C3C3C',
            foreground='#FFFFFF',
            padding=5)
        
        # Enhanced Radio button styling
        style.configure('TRadiobutton',
            background='#1E1E1E',
            foreground='#FFFFFF')
        style.map('TRadiobutton',
            indicatorcolor=[('selected', '#0078D4'), ('!selected', '#3C3C3C')])
        
        # Progress bar styling
        style.configure('Horizontal.TProgressbar',
            background='#0078D4',
            troughcolor='#2D2D2D')
        
        
        # Initialize logging
        self._setup_logging()
        
        # Initialize variables
        self.source_folder = tk.StringVar()
        self.destination_folder = tk.StringVar()
        self.file_count_var = tk.StringVar(value="1")
        self.file_extension_var = tk.StringVar(value="All")
        self.operation_mode = tk.StringVar(value="move")
        self.preview_visible = tk.BooleanVar(value=True)
        self.move_history: List[Dict] = []
        
        # Add file types before UI creation
        self.file_types = {
            "Pictures": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".tiff"],
            "Videos": [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".m4v", ".3gp"],
            "Documents": [".txt", ".pdf", ".doc", ".docx", ".xlsx", ".csv", ".pptx", ".rtf"],
            "Music": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"],
            "Compressed": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
            "Code": [".py", ".java", ".c", ".cpp", ".js", ".html", ".css", ".php"],
            "All": []
        }
        
        self._create_ui()

    def _setup_logging(self):
        logging.basicConfig(
            filename='file_mover.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def _create_ui(self):
        main_container = ttk.Frame(self.window)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Preview panel with dark theme
        preview_frame = ttk.LabelFrame(main_container, text="Image Preview", padding=15)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Center container for preview
        center_frame = ttk.Frame(preview_frame)
        center_frame.pack(expand=True)
        
        self.preview_label = ttk.Label(center_frame, background='#1E1E1E')
        self.preview_label.pack(expand=True, anchor="center", padx=10, pady=10)

        # Folder selection frame
        folder_frame = ttk.LabelFrame(main_container, text="Folder Selection", padding=10)
        folder_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(folder_frame, text="Source:").grid(row=0, column=0, sticky="w")
        ttk.Entry(folder_frame, textvariable=self.source_folder).grid(row=0, column=1, sticky="ew")
        ttk.Button(folder_frame, text="Browse", command=self.select_source_folder).grid(row=0, column=2)

        # Add swap button between source and destination
        ttk.Button(folder_frame, text="⇅", command=self.swap_folders, width=3).grid(row=1, column=0)

        ttk.Label(folder_frame, text="Destination:").grid(row=2, column=0, sticky="w")
        ttk.Entry(folder_frame, textvariable=self.destination_folder).grid(row=2, column=1, sticky="ew")
        ttk.Button(folder_frame, text="Browse", command=self.select_destination_folder).grid(row=2, column=2)

        folder_frame.grid_columnconfigure(1, weight=1)

        # Options frame
        options_frame = ttk.LabelFrame(main_container, text="Options", padding=10)
        options_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(options_frame, text="Number of files:").grid(row=0, column=0, sticky="w")
        ttk.Entry(options_frame, textvariable=self.file_count_var, width=10).grid(row=0, column=1)
        
        ttk.Label(options_frame, text="File type:").grid(row=1, column=0, sticky="w")
        file_types = ["All", "Pictures", "Videos", "Documents", "Music", "Compressed", "Code"]
        ttk.Combobox(options_frame, textvariable=self.file_extension_var, values=file_types).grid(row=1, column=1)
        
        ttk.Radiobutton(options_frame, text="Move", variable=self.operation_mode, value="move").grid(row=2, column=0)
        ttk.Radiobutton(options_frame, text="Copy", variable=self.operation_mode, value="copy").grid(row=2, column=1)

        # Action buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(button_frame, text="Process Files", command=self.process_files).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Undo Last", command=self.undo_last_operation).pack(side="left", padx=5)

        # Progress bar
        self.progress = ttk.Progressbar(main_container, mode='determinate')
        self.progress.pack(fill="x", padx=5, pady=5)

        # Status bar
        self.status_var = tk.StringVar()
        ttk.Label(main_container, textvariable=self.status_var).pack(anchor="w", padx=5)


    def _on_window_resize(self, event):
        if event.widget == self.window and self.current_image_path:
            # Only resize if window width/height changed
            if hasattr(self, '_last_window_size'):
                if self._last_window_size == (event.width, event.height):
                    return
            self._last_window_size = (event.width, event.height)
            self.display_image(self.current_image_path)


    def display_image(self, image_path):
        try:
            self.current_image_path = image_path
            image = Image.open(image_path)
            
            # Get current window dimensions
            window_width = self.window.winfo_width()
            window_height = self.window.winfo_height()
            
            # Check if window is maximized or fullscreen
            is_maximized = self.window.state() == 'zoomed'
            
            # Calculate max dimensions with reduced height ratios
            if is_maximized:
                display_width = int(window_width * 0.95)    # 95% of width when maximized
                display_height = int(window_height * 0.60)   # 60% of height when maximized
            else:
                display_width = int(window_width * 0.90)    # 90% of width normally
                display_height = int(window_height * 0.55)   # 55% of height normally
            
            # Calculate aspect ratios
            width_ratio = display_width / image.width
            height_ratio = display_height / image.height
            
            # Use smaller ratio to maintain aspect ratio
            ratio = min(width_ratio, height_ratio)
            
            new_width = int(image.width * ratio)
            new_height = int(image.height * ratio)
            
            # High-quality resize
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert and display
            photo = ImageTk.PhotoImage(image)
            self.preview_label.configure(image=photo)
            self.preview_label.image = photo
            
        except Exception as e:
            logging.error(f"Error displaying image: {str(e)}")
            self.preview_label.configure(image='', text="No image preview available")


    def select_source_folder(self):
        folder = filedialog.askdirectory(
            title="Select Source Folder",
            mustexist=True
        )
        if folder:
            self.source_folder.set(folder)
            self.status_var.set(f"Source folder: {folder}")

    def select_destination_folder(self):
        folder = filedialog.askdirectory(
            title="Select Destination Folder",
            mustexist=True
        )
        if folder:
            self.destination_folder.set(folder)
            self.status_var.set(f"Destination folder: {folder}")

    def swap_folders(self):
        source = self.source_folder.get()
        destination = self.destination_folder.get()
        self.source_folder.set(destination)
        self.destination_folder.set(source)
        self.status_var.set("Swapped source and destination folders")

    def _get_matching_files(self) -> List[str]:
        try:
            src = self.source_folder.get()
            files = [f for f in os.listdir(src) if os.path.isfile(os.path.join(src, f))]
            
            file_type = self.file_extension_var.get()
            if file_type != "All" and file_type in self.file_types:
                files = [f for f in files if any(f.lower().endswith(ext) 
                        for ext in self.file_types[file_type])]
            
            return files
        except Exception as e:
            logging.error(f"Error in file matching: {str(e)}")
            messagebox.showerror("Error", f"Error matching files: {str(e)}")
            return []

    def validate_inputs(self) -> bool:
        try:
            file_count = int(self.file_count_var.get())
            if file_count < 1:
                raise ValueError("File count must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of files")
            return False

        if not self.source_folder.get() or not self.destination_folder.get():
            messagebox.showerror("Error", "Please select both folders")
            return False

        if not os.path.exists(self.source_folder.get()):
            messagebox.showerror("Error", "Source folder does not exist")
            return False

        if not os.path.exists(self.destination_folder.get()):
            messagebox.showerror("Error", "Destination folder does not exist")
            return False

        return True

    def process_files(self):
        if not self.validate_inputs():
            return

        try:
            files = self._get_matching_files()
            if not files:
                messagebox.showwarning("Warning", "No matching files found")
                return

            self.progress['maximum'] = int(self.file_count_var.get())
            operation = shutil.copy2 if self.operation_mode.get() == "copy" else shutil.move
            
            moved_files = []
            last_image = None
            
            for i in range(min(int(self.file_count_var.get()), len(files))):
                random_file = random.choice(files)
                src_path = os.path.join(self.source_folder.get(), random_file)
                dst_path = os.path.join(self.destination_folder.get(), random_file)
                
                operation(src_path, dst_path)
                moved_files.append({"src": src_path, "dst": dst_path})
                files.remove(random_file)
                
                # Update last image if it's a picture
                if any(random_file.lower().endswith(ext) for ext in self.file_types["Pictures"]):
                    last_image = dst_path
                
                self.progress['value'] = i + 1
                self.window.update_idletasks()

            # Display the last moved image if any
            if last_image:
                self.display_image(last_image)
            else:
                self.preview_label.configure(image='')
                self.preview_label.configure(text="No image preview available")

            self.move_history.append(moved_files)
            operation_name = "copied" if self.operation_mode.get() == "copy" else "moved"
            self.status_var.set(f"Successfully {operation_name} {len(moved_files)} files")
            logging.info(f"{operation_name.capitalize()} {len(moved_files)} files")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            logging.error(f"Error during file operation: {str(e)}")

    def undo_last_operation(self):
        if not self.move_history:
            messagebox.showinfo("Info", "No operations to undo")
            return
            
        last_operation = self.move_history.pop()
        operation = shutil.move  # Always move for undo
        
        try:
            for file_op in last_operation:
                if os.path.exists(file_op["dst"]):
                    operation(file_op["dst"], file_op["src"])
            
            self.status_var.set(f"Undid last operation: {len(last_operation)} files restored")
            logging.info(f"Undid operation of {len(last_operation)} files")
        except Exception as e:
            messagebox.showerror("Error", f"Error during undo: {str(e)}")
            logging.error(f"Undo error: {str(e)}")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = FileMover()
    app.run()