from datetime import date
from pathlib import Path

import os
import yaml
import pandas as pd
import numpy as np

class Project:
    def __init__(self, project_name=None, folder_path=None, im_folder_path=None, ref_im_path=None, csv_path=None, num_keypoints=None, load_project=None):
        if not load_project is None :
            self.name = os.path.basename(load_project)[:-5]
            self.folder = os.path.dirname(load_project)
            self.data = None
            with open(load_project) as f:
                self.data = yaml.load(f, Loader=yaml.FullLoader)
            self.annot = pd.read_csv(self.data['CSV_Path'])
        elif project_name is None:
            self.data = {'Project_Name': 'Untitled_Project', 'Image_Folder_Path': None, 'CSV_Path': None, 'Reference_Image_Path': None, 'num_keypoints': None, 'curr_img_idx': 0, 'Images': []}
            self.name = 'Untitled_Project'
            self.folder = None
            return
        else :
            self.name = project_name
            self.folder = folder_path
            self.data = {'Project_Name': project_name, 'Image_Folder_Path': im_folder_path, 'CSV_Path': csv_path, 'Reference_Image_Path': ref_im_path, 'num_keypoints': num_keypoints, 'Images': [], 'curr_img_idx': 0}
            lst = []
            for i in range(num_keypoints):
                lst += ["KP_"+str(i)+"_x", "KP_"+str(i)+"_y"]
            self.annot = pd.DataFrame(columns=['Image_Name']+lst)
        # Data format is: 
        # {
        #   Project_Name : Untitled_Project
        #   Image_Folder_Path: abc/xyz/
        #   CSV_Path: pqr/uvw.csv
        #   Reference_Image_Path: ijk/mno.png
        #   num_keypoints: 10
        #   curr_img_idx: 0
        #   Images:
        #        - {
        #           Image_Name: abra.png
        #           Zoomcycle: 1.0
        #           Pan: {
        #                  x: 0, 
        #                  y: 0
        #               }
        #           Review_Status: To be reviewed    # options = [To be reviewed, Mislabeled, Reviewed]
        #           }
        #        - {...}
        #        - {...}
        # }
    def set_root_path(self, path):
        self.folder = path

    def set_images_path(self, path):
        self.data['Image_Folder_Path'] = path
    
    def set_ref_path(self, path):
        self.data['Reference_Image_Path'] = path

    def set_number_keypoints(self, n):
        self.data['num_keypoints'] = n

    def set_name(self, name):
        self.name = name
        self.data['Project_Name'] = name

    def init_csv_path(self, name):
        self.data['CSV_Path'] = os.path.join(self.folder, name+'.csv')

    def save_project(self):
        p = os.path.join(self.folder, self.name+'.yaml')
        self.annot.to_csv(self.data['CSV_Path'], index=False)
        with open(p, 'w') as f:
            yaml.dump(self.data, f, sort_keys=False)
    
    def init_single_image(self, image_path):
        #setting defaults
        dict = {
            "Image_Name": image_path,
            "Zoomcycle": 1.0,
            "Pan": {"x": 0, "y": 0},
            "Review_Status":  "To be reviewed",
        }
        self.data["Images"].append(dict)

    def init_annotations(self):
        lst = []
        for i in range(self.data['num_keypoints']):
            lst += ["KP_"+str(i)+"_x", "KP_"+str(i)+"_y"]
        self.annot = pd.DataFrame(columns=['Image_Name']+lst)

    def rescan_img_folder(self):
        del_im_list = []
        img_list = []
        for _, _, ims in os.walk(self.data['Image_Folder_Path']):
            images = []
            for filename in ims:
                if filename.endswith(('.jpg', '.png', '.jpeg', '.bmp')):
                    images.append(filename)
            img_list.extend(images)
        for im in self.data['Images']:
            if not im['Image_Name'] in img_list:
                del_im_list.append(im['Image_Name'])
            else:
                img_list.remove(im['Image_Name'])
        return del_im_list, img_list

    def update_image_list_in_metadata(self, del_list=[], add_list=[]):
        ls = [im for im in self.data['Images']]
        for im in ls:
            if im['Image_Name'] in del_list:
               self.data['Images'].remove(im)
               #del_list.remove(im['Image_Name'])
        
        for img in add_list:
            self.data['Images'].append({'Image_Name': img, 'Zoomcycle': 1.0, 'Pan': {"x": 0, "y": 0}, 'Review_Status': "To be reviewed"})
        
    def update_image_list_in_csv(self, del_list=[], add_list=[]):
        if len(del_list) != 0:
            self.annot.drop(self.annot[self.annot['Image_Name'].map(lambda x: x in del_list)].index, inplace=True)
        if len(add_list) != 0:
            self.annot = self.annot.append(pd.DataFrame(add_list, columns=['Image_Name']), ignore_index=True)

    def update_project(self, del_list=[], add_list=[]):
        self.update_image_list_in_metadata(del_list=del_list, add_list=add_list)
        self.update_image_list_in_csv(del_list=del_list, add_list=add_list)

    def get_img_metadata(self, img_name=None):
        if img_name is None:
            dic = self.data['Images'][self.data['curr_img_idx']]
            return dic['Zoomcycle'], dic['Pan'], dic['Review_Status']
        for im in self.data['Images']:
            if im['Image_Name'] == img_name:
                return im['Zoomcycle'], im['Pan'], im['Review_Status']
        return None, None, None
    
    def get_img_key_points(self, kp, img_name=None):
        if img_name is None:
            img_name = self.data['Images'][self.data['curr_img_idx']]['Image_Name']
        cond = self.annot['Image_Name']==img_name
        if type(kp) == int:
            return self.annot.loc[cond, "KP_"+str(kp)+"_x"].iloc[0], self.annot.loc[cond, "KP_"+str(kp)+"_y"].iloc[0]
        elif type(kp) == list:
            coord = []
            for i in kp:
                coord.append((self.annot.loc[cond, "KP_"+str(i)+"_x"].iloc[0], self.annot.loc[cond, "KP_"+str(i)+"_y"].iloc[0]))
            return coord
        elif kp == 'All':
            coord = []
            for i in range(self.data['num_keypoints']):
                coord.append((self.annot.loc[cond, "KP_"+str(i)+"_x"].iloc[0], self.annot.loc[cond, "KP_"+str(i)+"_y"].iloc[0]))
            return coord
        else:
            return None

    def set_img_key_points(self, idx, x, y, img_name=None):
        if img_name is None:
            img_name = self.data['Images'][self.data['curr_img_idx']]['Image_Name']
        cond = self.annot['Image_Name']==img_name
        if type(idx) == int: # Assume y is int too
            self.annot.loc[cond, ["KP_"+str(idx)+"_x", "KP_"+str(idx)+"_y"]] = x, y
        elif type(idx) == list:
            for i, p in enumerate(idx):
                self.annot.loc[cond, ["KP_"+str(p)+"_x", "KP_"+str(p)+"_y"]] = x[i], y[i]
    
    def set_img_metadata(self, img_name=None, zoom=None, pan=None, flag=None):
        if img_name is None:
            dic = self.data['Images'][self.data['curr_img_idx']]
            if not zoom is None:
                dic['Zoomcycle']= zoom
            if not pan is None:
                dic['Pan'] = pan
            if not flag is None:
                dic['Review_Status'] = flag
            return
        for im in self.data['Images']:
            if im['Image_Name'] == img_name:
                if not zoom is None:
                    im['Zoomcycle'] = zoom
                if not pan is None:
                    im['Pan'] = pan
                if not flag is None:
                    im['Review_Status'] = flag
                return
    
    def change_num_key_points(self, num_kp):
        if num_kp == self.data['num_keypoints']:
            return
        elif num_kp > self.data['num_keypoints']:
            for i in range(self.data['num_keypoints'], num_kp):
                self.annot["KP_"+str(i)+"_x"] = np.nan
                self.annot["KP_"+str(i)+"_y"] = np.nan
        else:
            for i in range(num_kp, self.data['num_keypoints']):
                del self.annot["KP_"+str(i)+"_x"]
                del self.annot["KP_"+str(i)+"_y"]
        self.data['num_keypoints'] = num_kp       

    def get_next_img(self):
        n = len(self.data['Images'])
        self.data['curr_img_idx'] = (self.data['curr_img_idx'] + 1) % n
        return self.data['Images'][self.data['curr_img_idx']]

    def get_prev_img(self):
        n = len(self.data['Images'])
        self.data['curr_img_idx'] = (self.data['curr_img_idx'] - 1 + n) % n
        return self.data['Images'][self.data['curr_img_idx']]

    def get_curr_img_name(self):
        return self.data['Images'][self.data['curr_img_idx']]["Image_Name"]