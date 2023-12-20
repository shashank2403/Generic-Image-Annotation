from asyncio.windows_events import NULL
from tkinter import *
from PIL import ImageTk, Image, ImageDraw, ImageFont
import platform

import tkinter as tk
from tkinter import ttk
from panel import Panel
from project import Project

from tkinter import filedialog, messagebox
from time import sleep
import os
import pandas as pd
import numpy as np
from natsort import natsorted

import yaml

import logging

logging.basicConfig(format='%(levelname)-8s|%(message)s', level=logging.INFO)


class UI(tk.Frame):
    def __init__(self, root):

        if platform.system() == "Windows":
            self.os_type = 0
        else:
            self.os_type = 1
        # self.os_type  = 0 # set to 0 for Windows and 1 for linux/macos

        self.style = ttk.Style()

        # self.style.configure('blue.TButton', foreground='white', background='blue')
        # self.style.map('blue.TButton', foreground = [('active', 'blue'), ('selected', 'green')], background = [('active', 'white'), ('selected', 'white')])

        # self.style.configure('cyan.TButton', foreground='white', background='cyan')
        # self.style.map('cyan.TButton', foreground = [('active', 'cyan'), ('selected', 'green')], background = [('active', 'white'), ('selected', 'white')])

        # self.style.configure('gray.TButton', foreground='black', background='gray')
        # self.style.map('gray.TButton', foreground = [('active', 'white'), ('selected', 'green')], background = [('active', 'black'), ('selected', 'white')])

        # self.style.configure('TEntry', foreground='white', background='blue')
        # self.style.map('TEntry', foreground = [('active', 'blue')], background = [('active', 'white')])

        # self.style.configure('ble.TMenubutton', foreground='white', background="blue")
        # self.style.map('ble.TMenubutton', foreground = [('active', 'blue')], background = [('active', 'white')])

        font_size = 20
        self.style.configure('.', font=('Helvetica', font_size), anchor="center", padding=10)

        tk.Frame.__init__(self, root)
        self.root = root
        self.root.title("Image Annotate")
        self.root.configure(bg="lightblue")
        icon = PhotoImage(file="assets/iitd_logo.png")
        self.root.iconphoto(True, icon)
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        self.root.geometry(f'{width}x{height}')

        self.last_selected = 0
        self.lpanel = Panel(root)
        self.rpanel = Panel(root)

        # self.img_list = []
        # self.curr_img = None

        self.folder_path = None
        self.save_folder = None

        self.opt_var = StringVar()
        self.options = None
        self.drop_down = None
        # self.csv_file_name = None

        self.bttn_prev = ttk.Button(root, text="Prev", command=self.prev_img, style='gray.TLabel')
        self.bttn_next = ttk.Button(root, text="Next", command=self.next_img, style='gray.TLabel')

        self.bttn_save_project = ttk.Button(root, text="Save Project", command=self.save_progress, style='cyan.TLabel')
        self.bttn_new_project = ttk.Button(root, text="New Project", command=self.new_project, style='blue.TLabel')
        self.bttn_load_project = ttk.Button(root, text="Load Project", command=self.load_project, style='blue.TLabel')
        self.bttn_rescan = ttk.Button(root, text="Re-Scan Folder", command=self.rescan, style='blue.TLabel')

        self.options = [0, 1]
        self.opt_var = StringVar(value="Keypoint")
        self.key_point_drop_down = ttk.OptionMenu(self.root, self.opt_var, *self.options,
                                                  command=self.change_keypoint_number, style='blue.TMenubutton')

        self.review_options = ["Un-reviewed", "Mislabeled", "Reviewed"]
        self.review_var = StringVar(value="Review Status")
        review_drop_down_options = [0] + self.review_options
        self.review_status = ttk.OptionMenu(self.root, self.review_var, *review_drop_down_options,
                                            command=self.change_review_status, style='blue.TMenubutton')

        self.zoom_in_lpanel_button = ttk.Button(root, text="+", command=self.lpanel.zoom_in, style='blue.TLabel')
        self.zoom_out_lpanel_button = ttk.Button(root, text="–", command=self.lpanel.zoom_out, style='blue.TLabel')
        self.zoom_in_rpanel_button = ttk.Button(root, text="+", command=self.rpanel.zoom_in, style='blue.TLabel')
        self.zoom_out_rpanel_button = ttk.Button(root, text="–", command=self.rpanel.zoom_out, style='blue.TLabel')

        self.export_annotated = ttk.Button(root, text="Export", command=self.export, style='blue.TLabel')

        self.project = None

        self.panMode = 1
        self.point_threshold = 30

        self.rpanel.canvas.bind('<Button-1>', self.mouse)
        self.rpanel.canvas.bind("<B1-Motion>", self.mouse_down)
        self.rpanel.canvas.bind("<ButtonRelease-1>", self.mouse_up)

        self.lpanel.canvas.bind('<Button-1>', self.lpanel.scroll_start)
        self.lpanel.canvas.bind("<B1-Motion>", self.lpanel.scroll_move)

        self.key_point_number = 0
        self.key_point_coordinates = (np.nan, np.nan)
        # self.data_frame = None
        self.lpanel.os_type = self.os_type
        self.rpanel.os_type = self.os_type

        # positioning of elements

        self.bttn_new_project.grid(row=0, column=0, padx=5, pady=(40, 5), sticky='nsew')
        self.bttn_save_project.grid(row=0, column=1, padx=5, pady=(40, 5), sticky='nsew')

        self.update_key_point_drop_down(0)
        self.review_status.grid(row=0, column=2, padx=5, pady=(40, 5), sticky="nsew")

        self.lpanel.grid(row=1, column=0, columnspan=2, rowspan=3, padx=5, pady=5, sticky='nsew')
        self.rpanel.grid(row=1, column=2, columnspan=2, rowspan=3, padx=5, pady=5, sticky='nsew')
        self.root.grid_rowconfigure((3), weight=1)
        self.root.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.bttn_prev.grid(row=4, column=2, padx=5, pady=(5, 40), sticky='nsew')
        self.bttn_next.grid(row=4, column=3, padx=5, pady=(5, 40), sticky='nsew')

        self.bttn_load_project.grid(row=4, column=0, padx=5, pady=(5, 40), sticky='nsew')
        self.bttn_rescan.grid(row=4, column=1, padx=5, pady=(5, 40), sticky='nsew')

        self.zoom_in_lpanel_button.grid(row=1, column=0, padx=20, pady=(30, 10), sticky="w")
        self.zoom_out_lpanel_button.grid(row=2, column=0, padx=20, pady=0, sticky="w")
        self.zoom_in_rpanel_button.grid(row=1, column=2, padx=20, pady=(30, 10), sticky="w")
        self.zoom_out_rpanel_button.grid(row=2, column=2, padx=20, pady=0, sticky="w")

        self.export_annotated.grid(row=3, column=3, padx=30, pady=(10, 30), sticky="se")

        self.configs = {}

    def new_project(self):

        self.project = Project()

        self.all_filled = {"name": True, "keypoint": True, "ref": False, "image": False, "root": True}

        newWindow = Toplevel(self.root)
        self.newWindow = newWindow
        self.newWindow.title("New Project")
        ratio = 0.75
        width = int(self.newWindow.winfo_screenwidth() * ratio)
        height = int(self.newWindow.winfo_screenheight() * ratio)
        self.newWindow.geometry(f'{width}x{height}')

        # self.newWindow.geometry("500x600")
        self.newWindow.configure(bg="lightblue")

        title = ttk.Label(self.newWindow, text="Creating a new Project")

        ask_proj_name = ttk.Label(self.newWindow, text="Project Name")
        self.proj_name = StringVar(value="Untitled_Project")
        enter_proj_name = ttk.Entry(self.newWindow, width=20, textvariable=self.proj_name)
        self.save_name()

        ask_root_path = ttk.Label(self.newWindow, text="Set Folder to save project")
        btn_root_path = ttk.Button(self.newWindow, text="Select", command=self.save_root_path)
        self.save_folder = os.getcwd()
        self.save_root_path(self.save_folder)

        btn_load_ref = ttk.Button(self.newWindow, text="Load Reference Image", command=self.load_ref)
        btn_image_path = ttk.Button(self.newWindow, text="Load Images Folder", command=self.load_images)

        ask_key_pts = ttk.Label(self.newWindow, text="Key-points")
        self.key_pts = StringVar(value="10")
        enter_key_pts = ttk.Entry(self.newWindow, width=20, textvariable=self.key_pts)
        self.save_keypoint_number()

        confirm = ttk.Button(self.newWindow, text="Confirm and Create Project!", command=self.confirm)

        title.grid(row=0, column=0, columnspan=7, padx=5, pady=(40, 5), sticky='nsew')

        ask_proj_name.grid(row=3, column=1, columnspan=1, padx=5, pady=5, sticky='nsew')
        enter_proj_name.grid(row=3, column=2, columnspan=1, padx=5, pady=5, sticky='nsew')

        ask_key_pts.grid(row=4, column=1, padx=5, pady=5, sticky='nsew')
        enter_key_pts.grid(row=4, column=2, padx=5, pady=5, sticky='nsew')

        ask_root_path.grid(row=2, column=1, columnspan=4, padx=5, pady=5, sticky='nsew')
        btn_root_path.grid(row=2, column=5, columnspan=1, padx=5, pady=5, sticky='nsew')

        btn_load_ref.grid(row=3, column=4, columnspan=2, padx=5, pady=5, sticky='nsew')
        btn_image_path.grid(row=4, column=4, columnspan=2, padx=5, pady=5, sticky='nsew')
        confirm.grid(row=6, column=1, columnspan=5, padx=5, pady=(5, 40), sticky='nsew')
        self.newWindow.grid_rowconfigure((1, 7), weight=1)
        self.newWindow.grid_columnconfigure((0, 6), weight=1)

    def confirm(self):
        self.save_name()
        self.save_keypoint_number()
        for key, item in self.all_filled.items():
            if not item:
                messagebox.showerror(title="Error", message="Please enter all the fields, missing: " + key)
                return
        self.newWindow.destroy()
        self.project.init_annotations()
        self.project.init_csv_path(self.project.name)
        self.project.update_image_list_in_csv(add_list=[im['Image_Name'] for im in self.project.data['Images']])
        logging.info(
            "====================================================\n\nRelevant details of the new project are: \n" + yaml.dump(
                self.project.data, indent=4, sort_keys=False) + "====================================================")

    def save_name(self):
        self.all_filled["name"] = True
        name = self.proj_name.get()
        self.project.set_name(name)

    def save_root_path(self, folder_path=None):
        self.all_filled["root"] = True
        if folder_path is None:
            self.save_folder = filedialog.askdirectory()
        else:
            self.save_folder = folder_path
        if self.os_type == 0:
            self.save_folder = self.save_folder.replace("/", "\\")
        if self.folder_path == "":
            logging.warning("No folder path chosen, setting to default current path")
            self.folder_path = os.getcwd()
            self.all_filled["root"] = False
            return
        self.project.set_root_path(self.save_folder)

    def load_ref(self):
        self.all_filled["ref"] = True
        self.lpanel.open()
        self.project.set_ref_path(self.lpanel.filename)

    def load_images(self):
        self.all_filled["image"] = True
        self.folder_path = filedialog.askdirectory()
        if self.os_type == 0:
            self.folder_path = self.folder_path.replace("/", "\\")
        if self.folder_path == "":
            logging.warning("No folder path chosen, setting to None")
            self.folder_path = None
            self.all_filled["image"] = False
            return
        self.project.set_images_path(self.folder_path)
        # self.curr_idx = 0
        # self.initialise_configs()
        self.initialise_image_list()
        self.rpanel.open(os.path.join(self.project.data['Image_Folder_Path'],
                                      self.project.data['Images'][self.project.data['curr_img_idx']]['Image_Name']))

    def save_keypoint_number(self):
        self.all_filled["keypoint"] = True
        no_keypts = int(self.key_pts.get())
        self.project.set_number_keypoints(no_keypts)
        self.update_key_point_drop_down(no_keypts)

    def update_key_point_drop_down(self, no_keypts):
        # if int(self.opt_var.get()) == self.key_point_number:
        #     print("same")
        #     return

        self.key_point_drop_down.destroy()
        self.options = [0] + [i for i in range(no_keypts)] + ["All"]
        self.key_point_drop_down = ttk.OptionMenu(self.root, self.opt_var, *self.options,
                                                  command=self.change_keypoint_number, style='blue.TMenubutton')
        self.key_point_drop_down.grid(row=0, column=3, padx=5, pady=(40, 5), sticky="nsew")

    def pop_key_point_drop_down(self, x):
        self.options.remove(x)
        self.key_point_drop_down.destroy()
        self.key_point_drop_down = ttk.OptionMenu(self.root, self.opt_var, *self.options,
                                                  command=self.change_keypoint_number, style='blue.TMenubutton')
        self.key_point_drop_down.grid(row=0, column=3, padx=5, pady=(40, 5), sticky="nsew")

    def save_meta_data(self):
        zoom = self.rpanel.zoomcycle
        pan = {
            "x": self.rpanel.new_origin[0],
            "y": self.rpanel.new_origin[1]
        }
        review_status = self.review_var.get()
        self.project.set_img_metadata(zoom=zoom, pan=pan, flag=review_status)

    def load_meta_data(self):
        zoom, pan, status = self.project.get_img_metadata()
        # if pan is not None:
        #     (x_old, y_old) = self.rpanel.new_origin
        #     self.rpanel.canvas.scan_mark(x_old, y_old)
        #     (x, y) = pan["x"], pan["y"]
        #     self.rpanel.new_origin = (x, y)
        #     self.rpanel.canvas.scan_dragto(x, y, gain=1)
        self.review_var.set(status)
        self.rpanel.zoomcycle = zoom

    def export(self):
        orig_img = self.rpanel.orig_img.copy()
        draw = ImageDraw.Draw(orig_img)
        width, height = orig_img.size
        point_size = min(width, height) // 100
        key_points = self.project.get_img_key_points("All")
        for i in range(0, len(key_points)):
            kp = key_points[i]
            draw.ellipse((kp[0] - point_size, kp[1] - point_size, kp[0] + point_size, kp[1] + point_size),
                         fill=(16, 255, 16), outline='black')
            font = ImageFont.truetype("assets/arial.ttf", 4 * point_size)
            draw.text((kp[0] - point_size, kp[1] - 5 * point_size), str(i), fill=(16, 255, 16), font=font,
                      outline='black')
        filename = filedialog.asksaveasfilename(title="Export image", filetypes=(
            ('JPEG', ('*.jpg', '*.jpeg', '*.jpe')), ('PNG', '*.png'), ('BMP', ('*.bmp', '*.jdib')), ('GIF', '*.gif')))
        orig_img = orig_img.convert('RGB')
        orig_img = orig_img.save(filename)

    def initialise_image_list(self):
        _, img_list = self.project.rescan_img_folder()
        self.project.update_image_list_in_metadata(add_list=img_list)

    def drop_down_grid(self):
        self.drop_down.grid(row=1, column=3, padx=20, pady=20, sticky="e")

    def change_review_status(self, event):
        status = self.review_var.get()
        self.project.set_img_metadata(flag=status)

    def load_project(self):
        pp = filedialog.askopenfilename(initialdir=os.getcwd(), title='Select Project File',
                                        filetypes=(('config files', '*.yaml'), ('All files', '*.*')))
        if self.os_type == 0:
            pp = pp.replace("/", "\\")
        self.project = Project(load_project=pp)
        self.update_key_point_drop_down(self.project.data['num_keypoints'])
        dic = self.project.data['Images'][self.project.data['curr_img_idx']]
        self.lpanel.open(filename=self.project.data['Reference_Image_Path'])
        self.rpanel.open(filename=os.path.join(self.project.data['Image_Folder_Path'], dic['Image_Name']))
        self.load_meta_data()

    def rescan(self):
        del_list, add_list = self.project.rescan_img_folder()
        newWindow = Toplevel(self.root)
        self.newWindow = newWindow
        self.newWindow.title("Folder Re-scan")

        self.newWindow.configure(bg="lightblue")
        ratio = 0.75
        width = int(self.newWindow.winfo_screenwidth() * ratio)
        height = int(self.newWindow.winfo_screenheight() * ratio)
        self.newWindow.geometry(f'{width}x{height}')

        lscrolly = ttk.Scrollbar(master=self.newWindow, orient='vertical')
        lscrollx = ttk.Scrollbar(master=self.newWindow, orient='horizontal')
        rscrolly = ttk.Scrollbar(master=self.newWindow, orient='vertical')
        rsrcollx = ttk.Scrollbar(master=self.newWindow, orient='horizontal')

        lb_left = Listbox(self.newWindow, height=10,
                          width=5,
                          bg="grey",
                          activestyle='dotbox',
                          font="Helvetica", fg='black', yscrollcommand=lscrolly.set, xscrollcommand=lscrollx.set)
        lb_right = Listbox(self.newWindow, height=10,
                           width=5,
                           bg="grey",
                           activestyle='dotbox',
                           font="Helvetica", fg='black', yscrollcommand=rscrolly.set, xscrollcommand=rsrcollx.set)
        label_left = ttk.Label(self.newWindow, text='Deleted Images')
        label_right = ttk.Label(self.newWindow, text='New Images')

        lscrollx.config(command=lb_left.xview)
        lscrolly.config(command=lb_left.yview)
        rsrcollx.config(command=lb_right.xview)
        rscrolly.config(command=lb_right.yview)

        st_left = '%d Images deleted from folder' % len(del_list)
        st_right = '%d New Images found in folder' % len(add_list)

        label_left_b = ttk.Label(self.newWindow, text=st_left)
        label_right_b = ttk.Label(self.newWindow, text=st_right)

        for n in del_list:
            lb_left.insert(END, n)

        for n in add_list:
            lb_right.insert(END, n)

        lbtn = ttk.Button(self.newWindow, text='Delete Data',
                          command=lambda: self.project.update_project(del_list=del_list), style='cyan.TLabel')
        rbtn = ttk.Button(self.newWindow, text='Insert Images',
                          command=lambda: self.project.update_project(add_list=add_list), style='cyan.TLabel')

        label_left.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')
        lb_left.grid(row=2, column=1, padx=5, pady=5, sticky='nsew')
        lscrolly.grid(row=2, column=2, padx=5, pady=5, sticky='nsew')
        lscrollx.grid(row=3, column=1, padx=5, pady=5, sticky='nsew')
        label_left_b.grid(row=4, column=1, padx=5, pady=5, sticky='nsew')
        lbtn.grid(row=5, column=1, padx=5, pady=5, sticky='nsew')

        label_right.grid(row=1, column=3, padx=5, pady=5, sticky='nsew')
        lb_right.grid(row=2, column=3, padx=5, pady=5, sticky='nsew')
        rscrolly.grid(row=2, column=4, padx=5, pady=5, sticky='nsew')
        rsrcollx.grid(row=3, column=3, padx=5, pady=5, sticky='nsew')
        label_right_b.grid(row=4, column=3, padx=5, pady=5, sticky='nsew')
        rbtn.grid(row=5, column=3, padx=5, pady=5, sticky='nsew')

        done = ttk.Button(self.newWindow, text='Done', command=lambda: (logging.info(
            "====================================================\n\nRelevant details of the new project are: \n" + yaml.dump(
                self.project.data, indent=4, sort_keys=False) + "===================================================="),
                                                                        self.newWindow.destroy()), style='cyan.TLabel')
        done.grid(row=6, column=1, columnspan=3, padx=5, pady=5, sticky='nsew')

        self.newWindow.grid_rowconfigure((0, 7), weight=1)
        self.newWindow.grid_columnconfigure((0, 5), weight=1)

    def mouse(self, event):
        x, y = self.key_point_coordinates

        event_x, event_y = event.x, event.y
        event_x = self.rpanel.canvas.canvasx(event_x) // self.rpanel.zoomcycle
        event_y = self.rpanel.canvas.canvasy(event_y) // self.rpanel.zoomcycle
        data = self.project.get_img_key_points(kp='All')
        keypoints_x_list = [d[0] for d in data if not np.isnan(d[0])]
        keypoints_y_list = [d[1] for d in data if not np.isnan(d[1])]
        keypoints_ids = [i for i, d in enumerate(data) if not np.isnan(d[0])]
        if self.key_point_number in keypoints_ids:
            idx = keypoints_ids.index(self.key_point_number)
            keypoints_x_list[idx] = x
            keypoints_y_list[idx] = y
        self.panMode = 1
        if (self.opt_var.get() == "All" and len(self.options) > 1):
            self.panMode = 1
        elif (x - event_x) ** 2 + (y - event_y) ** 2 < self.point_threshold ** 2:
            self.panMode = 0
        elif np.isnan(x) or np.isnan(y):
            self.panMode = 0
            self.last_selected = int(self.opt_var.get())
            self.pop_key_point_drop_down(int(self.opt_var.get()))
        else:
            for idx in range(len(keypoints_ids)):
                if keypoints_ids[idx] == int(self.opt_var.get()):
                    continue
                if (keypoints_x_list[idx] - event_x) ** 2 + (
                        keypoints_y_list[idx] - event_y) ** 2 < self.point_threshold ** 2:
                    self.panMode = 0
                    self.last_selected = self.key_point_number
                    self.opt_var.set(keypoints_ids[idx])
                    self.add_keypoint_to_df()
                    data = self.project.get_img_key_points(kp='All')
                    keypoints_x_list = [d[0] for d in data if not np.isnan(d[0])]
                    keypoints_y_list = [d[1] for d in data if not np.isnan(d[1])]
                    keypoints_ids = [i for i, d in enumerate(data) if not np.isnan(d[0])]
                    self.key_point_coordinates = (event_x, event_y)
                    temp = self.key_point_number
                    self.key_point_number = keypoints_ids[idx]
                    self.change_keypoint_number(self)
                    # self.opt_var.set(str(temp))
                    # self.change_keypoint_number(self)

                    #self.get_key_point(event)
                   
                    return
                    break
        if self.panMode == 1:
            self.rpanel.scroll_start(event)
        else:
            self.get_key_point(event)
   
    def mouse_down(self, event):
        print("mouse held down")
        if not self.rpanel.temp_point_id == np.nan:
            self.rpanel.erase_temp_point()
        if (not self.last_selected == self.key_point_number):
            data = self.project.get_img_key_points(kp='All')
            keypoints_x_list = [d[0] for d in data if not np.isnan(d[0])]
            keypoints_y_list = [d[1] for d in data if not np.isnan(d[1])]
            keypoints_ids = [i for i, d in enumerate(data) if not np.isnan(d[0])]
            idx = keypoints_ids.index(self.last_selected)
            x = keypoints_x_list[idx]
            y = keypoints_y_list[idx]
            self.rpanel.add_temp_point(x, y, self.last_selected)
        if self.panMode == 1:
            self.rpanel.scroll_move(event)
        else:
            self.get_key_point(event)

    def mouse_up(self, event):
        print("MOUSE UP")
        if not self.rpanel.temp_point_id==np.nan:
            self.rpanel.erase_temp_point()
        if (self.last_selected == 0):
            return
        if not self.last_selected == int(self.opt_var.get()):
        
            self.opt_var.set(str(self.last_selected))
            self.change_keypoint_number(self)


    def get_key_point(self, event):
        if (self.opt_var.get() == "All"):
            return
        # else:
        #     self.rpanel.clear_points()
        x, y = self.rpanel.get_point(event, self.key_point_number)
        self.key_point_coordinates = (x, y)

    def add_keypoint_to_df(self):
        x, y = self.key_point_coordinates
        if (not np.isnan(x) and not np.isnan(y)):
            self.project.set_img_key_points(self.key_point_number, x, y)
            logging.debug("Keypoint saved!")

    def check_incomplete(self):
        for kp in self.project.get_img_key_points("All"):
            if np.isnan(kp[0]) or np.isnan(kp[1]):
                logging.warning("All Key-points of the current image have not been annotated!")
                return

    def change_keypoint_number(self, event):
        print("number changed")
        if (self.key_point_number == int(self.opt_var.get())):
            return
        self.add_keypoint_to_df()

        data = self.project.get_img_key_points(kp='All')
        keypoints_x_list = [d[0] for d in data if not np.isnan(d[0])]
        keypoints_y_list = [d[1] for d in data if not np.isnan(d[1])]
        keypoints_ids = [i for i, d in enumerate(data) if not np.isnan(d[0])]
        if (self.opt_var.get() == "All"):
            self.rpanel.show_all_key_points(keypoints_x_list, keypoints_y_list, keypoints_ids)
            return
        else:
            self.rpanel.clear_points()

            data = data[:-1]
            if int(self.opt_var.get()) in keypoints_ids:
                idx = keypoints_ids.index(int(self.opt_var.get()))
                keypoints_x_list[idx] = self.key_point_coordinates[0]
                keypoints_y_list[idx] = self.key_point_coordinates[1]
            # if (not np.isnan(self.key_point_coordinates[0]) and not np.isnan(self.key_point_coordinates[1])): 
            #     keypoints_x_list.append(self.key_point_coordinates[0])
            #     keypoints_y_list.append(self.key_point_coordinates[1])
            #     keypoints_ids.append(-1)
            self.rpanel.show_all_key_points(keypoints_x_list, keypoints_y_list, keypoints_ids)
            if (self.opt_var.get() == "Keypoint"):
                self.key_point_number = 0
            else:

                self.key_point_number = int(self.opt_var.get())
            x, y = self.project.get_img_key_points(self.key_point_number)

            if (not np.isnan(x) and not np.isnan(y)):
                self.key_point_coordinates = (x, y)
                self.rpanel.actual_x = x
                self.rpanel.actual_y = y
                self.rpanel.show_point(x * self.rpanel.zoomcycle, y * self.rpanel.zoomcycle, self.key_point_number)
            else:
                self.key_point_coordinates = (np.nan, np.nan)
                self.rpanel.show_point(x, y, self.key_point_number)

    def change_keypoint_location_change_image(self):
        if (self.opt_var.get() == "All"):
            data = self.project.get_img_key_points(kp='All')
            keypoints_x_list = [d[0] for d in data if not np.isnan(d[0])]
            keypoints_y_list = [d[1] for d in data if not np.isnan(d[1])]
            keypoints_ids = [i for i, d in enumerate(data) if not np.isnan(d[0])]
            self.rpanel.show_all_key_points(keypoints_x_list, keypoints_y_list, keypoints_ids)
            return
        else:
            self.rpanel.clear_points()
            data = self.project.get_img_key_points(kp='All')
            data = data[:-1]
            keypoints_x_list = [d[0] for d in data if not np.isnan(d[0])]
            keypoints_y_list = [d[1] for d in data if not np.isnan(d[1])]
            keypoints_ids = [i for i, d in enumerate(data) if not np.isnan(d[0])]
            # if (not np.isnan(self.key_point_coordinates[0]) and not np.isnan(self.key_point_coordinates[1])):
            #     keypoints_x_list.append(self.key_point_coordinates[0])
            #     keypoints_y_list.append(self.key_point_coordinates[1])
            #     keypoints_ids.append(-1)
            self.rpanel.show_all_key_points(keypoints_x_list, keypoints_y_list, keypoints_ids)
            if (self.opt_var.get() == "Keypoint"):
                self.key_point_number = 0
            else:
                self.key_point_number = int(self.opt_var.get())
            x, y = self.project.get_img_key_points(self.key_point_number)
            if (not np.isnan(x) and not np.isnan(y)):
                self.key_point_coordinates = (x, y)
                self.rpanel.actual_x = x
                self.rpanel.actual_y = y
                self.rpanel.show_point(x * self.rpanel.zoomcycle, y * self.rpanel.zoomcycle, self.key_point_number)
            # else:
            #     self.key_point_coordinates = (np.nan, np.nan)
            #     self.rpanel.show_point(x, y, self.key_point_number)

    def prev_img(self):
        self.check_incomplete()
        self.add_keypoint_to_df()
        self.save_meta_data()
        dic = self.project.get_prev_img()
        if self.rpanel.zimg_id: self.rpanel.canvas.delete(self.rpanel.zimg_id)
        self.rpanel.filename = os.path.join(self.project.data['Image_Folder_Path'], dic['Image_Name'])
        self.rpanel.orig_img = Image.open(self.rpanel.filename)
        self.rpanel.imageWidth, self.rpanel.imageHeight = self.rpanel.orig_img.size
        self.rpanel.img = ImageTk.PhotoImage(self.rpanel.orig_img)
        self.rpanel.canvas.delete(self.rpanel.img_id)
        self.rpanel.img_id = self.rpanel.canvas.create_image(0, 0, image=self.rpanel.img, anchor="nw")
        self.rpanel.canvas.delete(self.rpanel.point_id)
        self.rpanel.canvas.delete(self.rpanel.point_text)
        self.rpanel.initialise()
        self.change_keypoint_location_change_image()
        self.load_meta_data()
        self.rpanel.resize()

    def next_img(self):
        self.check_incomplete()
        self.add_keypoint_to_df()
        self.save_meta_data()
        dic = self.project.get_next_img()
        if self.rpanel.zimg_id: self.rpanel.canvas.delete(self.rpanel.zimg_id)
        self.rpanel.filename = os.path.join(self.project.data['Image_Folder_Path'], dic['Image_Name'])
        self.rpanel.orig_img = Image.open(self.rpanel.filename)
        self.rpanel.imageWidth, self.rpanel.imageHeight = self.rpanel.orig_img.size
        self.rpanel.img = ImageTk.PhotoImage(self.rpanel.orig_img)
        self.rpanel.canvas.delete(self.rpanel.img_id)
        self.rpanel.img_id = self.rpanel.canvas.create_image(0, 0, image=self.rpanel.img, anchor="nw")
        self.rpanel.canvas.delete(self.rpanel.point_id)
        self.rpanel.canvas.delete(self.rpanel.point_text)
        self.rpanel.initialise()
        self.change_keypoint_location_change_image()
        self.load_meta_data()
        self.rpanel.resize()

    def save_progress(self):
        self.add_keypoint_to_df()
        self.project.save_project()


if __name__ == "__main__":
    Rt = tk.Tk()
    UI(Rt)
    Rt.mainloop()
