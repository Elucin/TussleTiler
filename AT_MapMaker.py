import tkinter as tk
from tkinter import Menu, Label, Frame, Entry, simpledialog
import tkinter.tix as tix
import csv
from tkinter import filedialog as fd
from PIL import Image

color_map = {
    "#FF00FF": 0, # Spawn
    "#D9EAD3": 1, # Flat
    "#D2C87C": 2, # Ground
    "#93C47D": 3, # Ground + Int
    "#A4C2F4": 4, # Water
    "#3C78D8": 5, # Lower
    "#7D7060": 6, # Higher
    "#B3A89B": 7, # Obstacle
    "#B7E1CD": 8, # Standard
    "#EA9999": 9, # Maybe Enemy
    "#CC0000": 10, # Yes Enemy
    "#E69138": 11, # Random
    "#46BDC6": 12, # Bridge
}

tile_map = {
    0: "#FF00FF", # Spawn
    1: "#D9EAD3", # Flat
    2: "#D2C87C", # Ground
    3: "#93C47D", # Ground + Int
    4: "#A4C2F4", # Water
    5: "#3C78D8", # Lower
    6: "#7D7060", # Higher
    7: "#B3A89B", # Obstacle
    8: "#B7E1CD", # Standard
    9: "#EA9999", # Maybe Enemy
    10: "#CC0000", # Yes Enemy
    11: "#E69138", # Random
    12: "#46BDC6", # Bridge
}

colors = {
    "#FF00FF": "Spawn",
    "#D9EAD3": "Flat",
    "#D2C87C": "Ground",
    "#93C47D": "Ground + Int",
    "#A4C2F4": "Water",
    "#3C78D8": "Lower",
    "#7D7060": "Higher",
    "#B3A89B": "Obstacle",
    "#B7E1CD": "Standard",
    "#EA9999": "Maybe Enemy",
    "#CC0000": "Yes Enemy",
    "#E69138": "Random",
    "#46BDC6": "Bridge",
}

def get_closest_color(pixel):
    closest_dist = None
    closest = ''
    for c in color_map:
        c = c.lstrip('#')
        c_rgb = tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
        dist = (pixel[0] - c_rgb[0]) ** 2 + (pixel[1] - c_rgb[1]) ** 2 + (pixel[2] - c_rgb[2]) ** 2
        if closest_dist is None or dist < closest_dist:
            closest_dist = dist
            closest = '#' + c
            if closest_dist == 0:
                return closest
    return closest

class PaintApp:
    def __init__(self, master):
        self.master = master
        master.title("Tussle Tiler")

        self.grid_size = (25, 25)
        self.cell_size = 30
        self.selected_color = "#D9EAD3"
        self.default_color = "#D9EAD3"
        self.selected_button = None

        self.create_menu(master)

        self.canvas = tix.Canvas(master, width=self.grid_size[0] * self.cell_size, height=self.grid_size[1] * self.cell_size)
        self.canvas.pack(side="left", pady=10)

        self.create_palette_section(master)

        self.create_grid()

        self.canvas.bind("<B1-Motion>", self.paint_cell)
        self.canvas.bind("<Button-1>", self.paint_cell)

        # Initialize the color_grid with default color
        self.color_grid = [[self.default_color for _ in range(self.grid_size[0])] for _ in range(self.grid_size[1])]

    def create_grid(self):
        for i in range(0, self.grid_size[0] * self.cell_size, self.cell_size):
            for j in range(0, self.grid_size[1] * self.cell_size, self.cell_size):
                self.canvas.create_rectangle(i, j, i + self.cell_size, j + self.cell_size, fill=self.default_color)

    def create_palette_section(self, master):
        palette_frame = Frame(master, width=100, height=650)
        palette_frame.pack_propagate(0)
        palette_frame.pack(before=self.canvas, side="left", pady=10)

        self.palette_label = Label(palette_frame, text="Flat")
        self.palette_label.pack(pady=5)

        self.create_color_buttons(palette_frame)

    def create_color_buttons(self, frame):
        for color in colors.keys():
            tip = tix.Balloon(self.master)
            button = tk.Button(frame, bg=color, width=4, height=2, text=color_map.get(color), borderwidth=1)
            button.config(command=lambda c=color,b=button: self.select_color(c, b))
            button.pack(side="top", padx=2, pady=2)
            tip.bind_widget(button, balloonmsg=colors.get(color))

            if color == "#D9EAD3":
                self.select_color(color, button)
                # self.selected_button = button
                # button.config(highlightthickness=2, highlightbackground="red", highlightcolor="red", bd=10, borderwidth=2)

    def create_menu(self, master):
        menu = Menu(master)
        master.config(menu=menu)

        file_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export to CSV", command=self.export_to_csv)
        file_menu.add_command(label="Import From CSV", command=self.import_from_csv)
        file_menu.add_command(label="Import From Image", command=self.import_from_img)

        edit_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Set Grid Size", command=self.set_grid_size)

    def select_color(self, color, button):
        self.selected_color = color
        self.palette_label.configure(text = colors.get(color))
        button.config(highlightthickness=2, highlightbackground="red", highlightcolor="red", borderwidth=3)
        if self.selected_button is not None:
            self.selected_button.config(borderwidth=1, highlightthickness=0)
        self.selected_button = button

    def paint_cell(self, event):
        x = (event.x // self.cell_size) * self.cell_size
        y = (event.y // self.cell_size) * self.cell_size
        self.canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size, fill=self.selected_color)

        # Update the color_grid
        try:
            self.color_grid[event.y // self.cell_size][event.x // self.cell_size] = self.selected_color
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
        self.cell_size = int(30 / ((x if x >= y else y) / 25))
        self.cell_size = self.cell_size if self.cell_size >= 10 else 10
        self.canvas.config(width=self.grid_size[0] * self.cell_size, height=self.grid_size[1] * self.cell_size)
        self.create_grid()
        self.color_grid = [[self.default_color for _ in range(self.grid_size[0])] for _ in range(self.grid_size[1])]

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
            for i,row in enumerate(self.color_grid, 1):
                writer.writerow([f'Y{i}'] + [color_map.get(r, 1) for r in row])

        print(f"Color grid exported to {filename}")

    def import_from_csv(self):
        filename = fd.askopenfilename(filetypes=(('CSV Map', '*.csv'),))
        if not filename:
            return
        with open(filename, newline="") as file:
            reader = csv.reader(file, delimiter=",")
            rows = list(reader)[1:]
            self.update_grid_size(len(rows[0])- 1, len(rows))
            for j,row in enumerate(rows):
                for i,tile_num in enumerate(row[1:]):
                    cell_color = tile_map.get(int(tile_num), "#D9EAD3")
                    x = i * self.cell_size
                    y = j * self.cell_size
                    self.canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size, fill=cell_color)

                    # Update the color_grid
                    try:
                        self.color_grid[j][i] = cell_color
                    except IndexError:
                        pass

    def import_from_img(self):
        filename = fd.askopenfilename(filetypes=(('All', '*.jpg;*.png;*.bmp'), ('JPEG', '*.jpg'), ('PNG', '*.png'), ("BMP", "*.bmp"),))
        if not filename:
            return
        im = Image.open(filename)
        pix = im.load()

        x_size, y_size = im.size
        self.update_grid_size(x_size, y_size)
        for j in range(0,y_size):
            for i in range(0, x_size):
                pix_color = pix[i,j]
                if isinstance(pix_color, int):
                    pix_color = (pix_color, pix_color, pix_color, pix_color)
                cell_color = get_closest_color(pix_color[:3])
                x = i * self.cell_size
                y = j * self.cell_size
                self.canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size, fill=cell_color)

                # Update the color_grid
                try:
                    self.color_grid[j][i] = cell_color
                except IndexError:
                    pass

if __name__ == "__main__":
    root = tix.Tk()
    paint_app = PaintApp(root)
    root.mainloop()
