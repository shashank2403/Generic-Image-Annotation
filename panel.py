from tkinter import *
from PIL import ImageTk,Image
from tkinter import filedialog

import tkinter as tk
import random
import numpy as np

class Panel(tk.Frame):
    def __init__(self, root):

        self.defaultDirectory = "/gui/images"
        self.frameWidth = 800
        self.frameHeight = 800
        

        self.temp_point_id = np.nan
        self.temp_point_text = np.nan
        self.imageWidth = self.frameWidth
        self.imageHeight =   self.frameHeight 
        tk.Frame.__init__(self, root)
        self.canvas = tk.Canvas(self, width=self.frameWidth, height=self.frameHeight, background="bisque")
        
        # self.xsb = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        # self.xsb.grid(row=2, column=0, sticky="ew")

        # self.ysb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        # self.ysb.grid(row=0, column=2, sticky="ns")
        
        # self.canvas.configure(yscrollcommand=self.ysb.set, xscrollcommand=self.xsb.set)
        self.canvas.configure(scrollregion=(-5000,-5000,5000,5000))
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.orig_img = Image.new("RGB", (self.frameWidth, self.frameHeight), (100, 100, 100))
        self.imageWidth, self.imageHeight = self.orig_img.size
        self.img = ImageTk.PhotoImage(self.orig_img)

        self.img_id = self.canvas.create_image(0,0,image=self.img, anchor="nw")

        # This is what enables scrolling with the mouse:
        self.canvas.bind("<MouseWheel>",self.zoomer) 
        
        self.point_ids_showing = []
        self.point_text_ids_showing = []
        self.initialise() 
        self.filename = None
        self.key_point_id = 0
        self.point_text = 0
        self.new_origin = (0, 0)


    def clear_points(self):
        for id in self.point_ids_showing:
            self.canvas.delete(id)
        for id in self.point_text_ids_showing:
            self.canvas.delete(id)
        
        self.key_points_x_list = None
        self.key_points_y_list = None

        
    def initialise(self):
        self.zoomcycle = 1
        self.zimg_id = None

        self.point_id  = None
        self.point_event = None
        self.actual_x = None
        self.actual_y = None

        self.key_points_x_list = None
        self.key_points_y_list = None
        self.key_points_id_list = None
        
        for id in self.point_ids_showing:
            self.canvas.delete(id)
        for id in self.point_text_ids_showing:
            self.canvas.delete(id)
        self.point_ids_showing = []
        self.point_text_ids_showing = []

    def scroll_start(self, event):
        # print(event.x, " start ", event.y)
        self.original_origin = (event.x, event.y)
        self.canvas.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        # print(event.x, " end ", event.y)
        self.new_origin = (self.new_origin[0]+event.x, self.new_origin[1]+event.y)
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def zoom_in(self):
        if self.zoomcycle <= 1: self.zoomcycle += 0.1
        elif self.zoomcycle <= 4: self.zoomcycle += 0.5
        self.resize()
    
    def zoom_out(self):
        if self.zoomcycle >1 :  self.zoomcycle -= 0.5
        elif self.zoomcycle >= 0.25: self.zoomcycle -= 0.1
        elif self.zoomcycle >= 0.1: self.zoomcycle -= 0.01
        self.resize()

    def zoomer(self,event):
        if (event.delta > 0):
            if self.zoomcycle <= 1: self.zoomcycle += 0.1
            elif self.zoomcycle <= 4: self.zoomcycle += 0.5
        elif (event.delta < 0):
            if self.zoomcycle >=1 :  self.zoomcycle -= 0.5
            elif self.zoomcycle >= 0.25: self.zoomcycle -= 0.1
        self.resize()

    def resize(self):
        if self.zimg_id: self.canvas.delete(self.zimg_id)
        if (self.zoomcycle) != 0:
            size = int(self.zoomcycle* self.imageWidth),int(self.zoomcycle*self.imageHeight)
            tmp = self.orig_img
            self.zimg = ImageTk.PhotoImage(tmp.resize(size))
            self.canvas.delete(self.img_id)
            self.zimg_id = self.canvas.create_image(0, 0, image=self.zimg,  anchor="nw")

            if self.actual_x is not None:

                self.show_point(self.actual_x*self.zoomcycle, self.actual_y*self.zoomcycle, self.key_point_id)
            if self.key_points_x_list is not None:
                self.show_all_key_points(self.key_points_x_list, self.key_points_y_list, self.key_points_id_list, True)
    
    def open(self, filename = None):
        if self.zimg_id: self.canvas.delete(self.zimg_id)
        if filename is None:
            self.filename = filedialog.askopenfilename(initialdir=self.defaultDirectory, title="Select A File", filetypes=(("jpg files", "*.jpg"), ("png files", "*.png"),("all files", "*.*")))
        else:
            self.filename = filename
        if self.os_type == 0: 
            # For windows, replace / with \
            self.filename = self.filename.replace("/", "\\")

        self.orig_img = Image.open(self.filename)
        
        self.imageWidth, self.imageHeight = self.orig_img.size
        self.img = ImageTk.PhotoImage(self.orig_img)
        self.canvas.delete(self.img_id)
        self.img_id = self.canvas.create_image(0,0,image=self.img, anchor="nw")

    def show_all_key_points(self, x_list, y_list, id_list, updateAll = False):
        self.key_points_x_list = x_list
        self.key_points_y_list = y_list
        self.key_points_id_list = id_list

        if(updateAll):
            for id in self.point_ids_showing:
                self.canvas.delete(id)
            for id in self.point_text_ids_showing:
                self.canvas.delete(id)
            
        #self.canvas.delete(self.point_id)
        #self.canvas.delete(self.point_text)
        for i in range(0, len(x_list)):
            print("RECEIVED " + str(self.key_points_id_list[i]))
            self.show_point(int(x_list[i])*self.zoomcycle, int(y_list[i])*self.zoomcycle, self.key_points_id_list[i], update = False)


    def show_point(self, x, y, id = 0, update = True):
        
        point_size = 5
        python_green = "#10ff10"
        python_text = "#10ff10"
        if self.point_id is not None:
            if update == True:
                self.canvas.delete(self.point_id)
                self.canvas.delete(self.point_text)
            else:
                self.point_ids_showing.append(self.point_id)
                self.point_text_ids_showing.append(self.point_text)

        if not np.isnan(x) and not np.isnan(y): 
            self.point_id = self.canvas.create_oval(x-point_size, y-point_size, x+point_size, y+point_size, fill=python_green)
            print("NOW PRINTING " + str(id))
            self.point_text = self.canvas.create_text(x+10, y-10, text=str(id), fill=python_text)

    def get_point(self, event, id_keypt = 0):
        self.actual_x = self.canvas.canvasx(event.x)//self.zoomcycle
        self.actual_y = self.canvas.canvasy(event.y)//self.zoomcycle
        self.key_point_id = id_keypt
        self.show_point(self.actual_x*self.zoomcycle, self.actual_y*self.zoomcycle, self.key_point_id)
        # print(actual_x," ",actual_y)
        return (self.actual_x, self.actual_y)

    def erase_temp_point(self):
        if self.temp_point_id == np.nan:
            return
        self.canvas.delete(self.temp_point_id)
        self.canvas.delete(self.temp_point_text)
        temp_point_id = np.nan
        temp_point_text = np.nan

    def add_temp_point(self, x, y, id):
        point_size = 5
        python_green = "#10ff10"
        python_text = "#10ff10"

        self.temp_point_id = self.canvas.create_oval(
            x-point_size, y-point_size, x+point_size, y+point_size, fill=python_green)
        self.temp_point_text = self.canvas.create_text(
            x+10, y-10, text=str(id), fill=python_text)


if __name__ == "__main__":
    root = tk.Tk()
    Panel(root).pack(fill="both", expand=True)
    root.mainloop()