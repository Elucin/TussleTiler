import tkinter as tk
from tkinter import Menu, Label, Frame, Entry, simpledialog
import tkinter.tix as tix
import csv
from tkinter import filedialog as fd
from PIL import Image, ImageTk
from math import sqrt, cos, sin, radians

NUM_ICONS = 25
icons = [Image.open(f'icons/{i}.png').convert('RGBA') for i in range(NUM_ICONS)]

def rotate_vector(v, angle):
    angle = radians(angle)
    return ((v[0] * cos(angle)) - (v[1] * sin(angle)), (v[0] * sin(angle)) + (v[1] * cos(angle)))

tile_names = [
    "Spawn",
    "Flat",
    "Ground",
    "No Obstacle",
    "Water",
    "Low Ground",
    "High Ground",
    "Obstacle",
    "Standard Chance Tile",
    "Possible Enemy",
    "Guaranteed Enemy",
    "Totally Random",
    "Possible Water Crossing",
    "Bridge",
    "Wall Corner",
    "Wall X",
    "Wall Y",
    "Garrison",
    "Enemy Spawner",
    "Minefield",
    "Rough",
    "Forest",
    "Rocks",
    "Cliff",
    "Canyon",
]

class PaintApp:
    def __init__(self, master):
        self.master = master
        master.title("Tussle Tiler")

        self.grid_size = (25, 25)
        self.cell_size = 30
        self.half_cell_size = 15
        self.selected_tile = None
        self.default_tile = 1
        self.selected_button = None
        self.zoom_scale = 4

        self.create_menu(master)

        # Create a Frame to hold the Canvas and the scrollbars
        self.canvas_frame = Frame(master)
        self.canvas_frame.pack(padx=10, fill="both", anchor="center")

        # Create the horizontal and vertical scrollbars
        self.x_scroll = tk.Scrollbar(self.canvas_frame, orient="horizontal")
        self.x_scroll.pack(side="bottom", fill="x")
        self.y_scroll = tk.Scrollbar(self.canvas_frame, orient="vertical")
        self.y_scroll.pack(side="right", fill="y")

        self.canvas = tix.Canvas(self.canvas_frame, 
                                 # width=self.grid_size[0] * self.cell_size,
                                  height=self.grid_size[1] * self.cell_size,
                                  xscrollcommand=self.x_scroll.set,
                                  yscrollcommand=self.y_scroll.set)

        self.canvas.pack(fill="both", anchor="center")

        # Configure the scrollbars to scroll the Canvas
        self.x_scroll.config(command=self.canvas.xview)
        self.y_scroll.config(command=self.canvas.yview)

        self.canvas.bind("<B1-Motion>", self.paint_cell)
        self.canvas.bind("<Button-1>", self.paint_cell)
        self.canvas.bind("<Button-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.pan_canvas)
        self.canvas.bind("<ButtonRelease-3>", self.end_pan)
        self.pan_start_x = None
        self.pan_start_y = None
        self.canvas.bind("<MouseWheel>", self.zoom)

        # Initialize the tile_grid with default tile
        self.tile_grid = [[self.default_tile for _ in range(self.grid_size[0])] for _ in range(self.grid_size[1])]

        self.icons = [ImageTk.PhotoImage(i.resize((int(sqrt(2 * self.cell_size ** 2) / 2), int(sqrt(2 * self.cell_size ** 2) / 2))).rotate(45, expand=1)) for i in icons]
        self.button_icons = [ImageTk.PhotoImage(i.resize((int(sqrt(2 * self.cell_size ** 2) / 2), int(sqrt(2 * self.cell_size ** 2) / 2))).rotate(45, expand=1)) for i in icons]
        self.create_palette_section(master)
        self.create_grid() 
        
    def create_grid(self):

        x_ini = self.grid_size[0] * self.half_cell_size
        y_ini = self.half_cell_size
        for _ in range(0, self.grid_size[0] * self.cell_size, self.cell_size):
            x_ini = x_ini + self.half_cell_size 
            y_ini = y_ini + self.half_cell_size
            for j in range(0, self.grid_size[1] * self.cell_size, self.cell_size):
                x = x_ini - j / 2
                y = y_ini + j / 2
                
                self.canvas.create_image(x, y, image=self.icons[self.default_tile])
        self.canvas.update()

    def create_palette_section(self, master):
        palette_frame = Frame(master)
        palette_frame.pack_propagate(0)
        palette_frame.pack(before=self.canvas, side="left", pady=10, padx=10)

        self.palette_label = Label(palette_frame, text="Flat", wraplength=75, justify="center")
        # self.palette_label.pack(pady=5)
        self.palette_label.grid(column=0, row=0, columnspan=2, rowspan=2)

        self.create_tile_buttons(palette_frame)

    def create_tile_buttons(self, frame):
        for index in range(NUM_ICONS):
            tip = tix.Balloon(self.master)
            button = tk.Button(frame, width=32, height=32, text=index, borderwidth=1)
            button.config(command=lambda i=index, b=button: self.select_tile(i, b), image=self.button_icons[index])

            button.grid(column=index % 2, row=index//2 + 2)
            tip.bind_widget(button, balloonmsg=tile_names[index])

            if index == self.default_tile:
                self.select_tile(index, button)
                self.selected_button = button

    def create_menu(self, master):
        menu = Menu(master)
        master.config(menu=menu)

        file_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export to CSV", command=self.export_to_csv)
        file_menu.add_command(label="Import From CSV", command=self.import_from_csv)
        # file_menu.add_command(label="Import From Image", command=self.import_from_img)

        edit_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Set Grid Size", command=self.set_grid_size)

    def select_tile(self, index, button):
        if self.selected_tile == index:
            return
        self.selected_tile = index
        self.palette_label.configure(text = tile_names[index])
        button.config(highlightthickness=0, borderwidth=3)
        if self.selected_button is not None:
            self.selected_button.config(borderwidth=1, highlightthickness=0)
        self.selected_button = button

    def paint_cell(self, event):
        # Get the current scroll position
        x_scroll = self.canvas.canvasx(0)
        y_scroll = self.canvas.canvasy(0)

        # Calculate the position of the cell in the grid
        
        # Get the relative position of 0,0
        x_ini = self.grid_size[0] * self.half_cell_size + self.half_cell_size
        y_ini = self.half_cell_size
        # int(sqrt(2 * self.cell_size ** 2) / 2) / 2
        side = sqrt((self.half_cell_size ** 2) * 2)
        
        # Determine the length of the vector from 0,0 to mouse location.
        v1_length = sqrt((event.x + x_scroll - x_ini) ** 2 + (event.y + y_scroll - y_ini) ** 2)

        v1 = ((event.x + x_scroll - x_ini) / v1_length, (event.y + y_scroll - y_ini) / v1_length)

        v2 = rotate_vector(v1, -45)
        v2 = (v2[0] * v1_length, v2[1] * v1_length)
        v2_ = (int(v2[0] // side), int(v2[1]  // side))
        
        v2 = (x_ini + v2_[0] * self.half_cell_size - v2_[1] * self.half_cell_size, 
              y_ini + v2_[0] * self.half_cell_size + v2_[1] * self.half_cell_size + self.half_cell_size)

        # self.canvas.delete("arrow")
        # self.canvas.create_line(x_ini, 
        #                         y_ini, 
        #                         x_ini + v2_[0] * self.half_cell_size, 
        #                         y_ini + v2_[0] * self.half_cell_size, 
        #                         arrow=tk.LAST, tags="arrow")

        # self.canvas.create_line(x_ini + v2_[0] * self.half_cell_size, 
        #                         y_ini + v2_[0] * self.half_cell_size, 
        #                         x_ini + v2_[0] * self.half_cell_size - v2_[1] * self.half_cell_size, 
        #                         y_ini + v2_[0] * self.half_cell_size + v2_[1] * self.half_cell_size, 
        #                         arrow=tk.LAST, tags="arrow")
        
        if any([v2_[0] not in range(self.grid_size[0]), v2_[1] not in range(self.grid_size[1])]):
            return
        
        if self.tile_grid[v2_[0]][v2_[1]] == self.selected_tile:
            return

        self.canvas.create_image(*v2, image=self.icons[self.selected_tile])
        self.canvas.update()
        
        # Update the tile_grid
        try:
            self.tile_grid[v2_[0]][v2_[1]] = self.selected_tile
        except IndexError:
            pass

    def set_grid_size(self):
        paint_app = self

        class GridSizeDialog(simpledialog.Dialog):
            def body(self, master):
                self.x_label = Label(master, text="Width:")
                self.x_label.grid(row=0, column=0, pady=5, padx=5)
                self.x_entry = Entry(master)
                self.x_entry.grid(row=0, column=1, pady=5, padx=5)
                self.x_entry.insert(0, str(paint_app.grid_size[0]))

                self.y_label = Label(master, text="Height:")
                self.y_label.grid(row=1, column=0, pady=5, padx=5)
                self.y_entry = Entry(master)
                self.y_entry.grid(row=1, column=1, pady=5, padx=5)
                self.y_entry.insert(0, str(paint_app.grid_size[1]))

                return self.x_entry

            def apply(self):
                try:
                    x = int(self.x_entry.get())
                    y = int(self.y_entry.get())
                except ValueError:
                    print("Values must be numeric.")
                else:
                    paint_app.update_grid_size(x, y)

        GridSizeDialog(self.master)

    def update_grid_size(self, x, y):
        self.grid_size = (x, y)
        self.canvas.delete("all")
        self.canvas.config(width=self.grid_size[0] * self.cell_size, height=self.grid_size[1] * self.cell_size)
        self.create_grid()
        self.tile_grid = [[self.default_tile for _ in range(self.grid_size[0])] for _ in range(self.grid_size[1])]

    def zoom(self, event):
        
        if event.delta > 0:
            self.cell_size = min(self.cell_size + self.zoom_scale, 100)
        else:
            self.cell_size = max(self.cell_size - self.zoom_scale, 6)
        self.half_cell_size = self.cell_size / 2
        self.canvas.delete("all")
        self.canvas.config(# width = self.grid_size[0] * self.cell_size, 
                           # height = self.grid_size[1] * self.cell_size, 
                           scrollregion=(self.grid_size[0] * self.cell_size * - 0.5, 
                                         self.grid_size[1] * self.cell_size * -0.5, 
                                         self.grid_size[0] * self.cell_size * 1.5, 
                                         self.grid_size[1] * self.cell_size * 1.5))
        
        x_ini = self.grid_size[0] * self.half_cell_size
        y_ini = self.half_cell_size
        self.icons = [ImageTk.PhotoImage(i.resize((int(sqrt(2 * self.cell_size ** 2) / 2), int(sqrt(2 * self.cell_size ** 2) / 2))).rotate(45, expand=1)) for i in icons]
        for row in self.tile_grid:
            x_ini += self.half_cell_size 
            y_ini += self.half_cell_size
            for j, cell_tile_index in enumerate(row):
                x = x_ini - j * self.half_cell_size
                y = y_ini + j * self.half_cell_size
                
                self.canvas.create_image(x, y, image=self.icons[cell_tile_index])

    def start_pan(self, event):
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        self.canvas.scan_mark(event.x, event.y)

    def pan_canvas(self, event):
        if self.pan_start_x is not None and self.pan_start_y is not None:
            self.canvas.scan_dragto(event.x, event.y, gain=1)

    def end_pan(self, event):
        self.pan_start_x = None
        self.pan_start_y = None

    def export_to_csv(self):
        try:
            filename = fd.asksaveasfilename(filetypes=(('CSV Map', '*.csv'),))
            if filename[-4:].lower() != ".csv":
                filename += ".csv"
        except Exception:
            return
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([''] + [f'X{x}' for x in range(1,self.grid_size[0]+1)])
            for i,row in enumerate(self.tile_grid, 1):
                writer.writerow([f'Y{i}'] + row)

        print(f"Tile grid exported to {filename}")

    def import_from_csv(self):
        filename = fd.askopenfilename(filetypes=(('CSV Map', '*.csv'),))
        if not filename:
            return
        with open(filename, newline="") as file:
            reader = csv.reader(file, delimiter=",")
            rows = list(reader)[1:]
            self.update_grid_size(len(rows[0])- 1, len(rows))
            x_ini = self.grid_size[0] * self.half_cell_size
            y_ini = self.half_cell_size
            for i, row in enumerate(rows):
                x_ini += self.half_cell_size 
                y_ini += self.half_cell_size
                for j, cell_tile_index in enumerate(row[1:]):
                    x = x_ini - j * self.half_cell_size
                    y = y_ini + j * self.half_cell_size
                    
                    self.canvas.create_image(x, y, image=self.icons[int(cell_tile_index)])

                    # Update the tile grid
                    try:
                        self.tile_grid[i][j] = int(cell_tile_index)
                    except IndexError:
                        pass

if __name__ == "__main__":
    root = tix.Tk()
    paint_app = PaintApp(root)
    root.mainloop()
