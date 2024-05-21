#!/usr/bin/env python3

# Graphic interfaz
import tkinter as tk

# Data parser
import construct as c

# Array and image managment
import numpy as np
import cv2

# System packages
import os
import sys
sys.path.append('../Common_utils')

# Base interfaz class
from interfaz_base import FolderSelectorApp


class CustomFolderSelectorApp(FolderSelectorApp):
    """
    Modified FolderSelector with a check button
    """
    def create_widgets(self):
        super().create_widgets()  # Llama al método create_widgets de la clase base
        self.extensions_list = ('.E2E', '.e2e')


class StructureParser(object):
    
    def __init__(self, f):

        self.define_structure_constructs()
        self.define_data_constructs()

        self.f = f
        self.parse_directory()
        self.define_knowledge()


    def define_structure_constructs(self):
        self.header_construct = c.Struct(
            'magic' / c.PaddedString(12, 'ascii'),
            'version' / c.Int32ul,
            'padding' / c.Bytes(20) # 18 ones, and 2 zeros
        )
        self.directory_construct = c.Struct(
            'magic' / c.PaddedString(12, 'ascii'),
            'version' / c.Int32ul,
            'padding' / c.Bytes(20), # 18 ones, and 2 zeros
            'num_entries' / c.Int32ul,
            'last' / c.Int32ul, 
            'prev' / c.Int32ul,
            'id' / c.Int32ul,
        )
        self.direntry_construct = c.Struct(
            'position' / c.Int32ul,
            'start' / c.Int32ul,
            'size' / c.Int32ul,
            'padding' / c.Bytes(4), # 4 zeros
            'patient_id' / c.Int32ul,
            'study_id' / c.Int32ul,
            'series_id' / c.Int32ul,
            'slice_id' / c.Int32ul,
            'indicator' / c.Int16ul,
            'unknown1' / c.Int16ul,
            'type' / c.Int32ul,
            'id' / c.Bytes(4) 
        )
        
    def define_data_constructs(self):
        self.unknown_0x3b_construct = c.Struct(
            'padding' / c.Bytes(12),
            'unknown1' / c.Int16ul,
            'laterality' / c.PaddedString(1,'u8'),
            'unknown2' / c.Array(12, c.Int8ul),
            )
        
    def define_knowledge(self):
        self.knowledge = {
            '0x3b':         {'info': '(??) Series data L/R 0x3b?',
                              'parse': self.unknown_0x3b_construct.parse},
            '0x2760':       { 'info': '(+) OCTA image',
                              'parse': self.read_rgba_image,
                              'key': lambda x: 'octa image'},
            '0x2761':       { 'info': '(+) OCTA image',
                              'parse': self.read_rgba_image,
                              'key': lambda x: 'octa image'},
            '0x2762':       { 'info': '(+) OCTA image',
                              'parse': self.read_rgba_image,
                              'key': lambda x: 'octa image'},
        }


    def parse_directory(self):
        self.header = self.header_construct.parse_stream(self.f)
        self.directory = []

        maindir = self.directory_construct.parse_stream(self.f)
        prev = maindir.last

        entry_count = 0
        while prev != 0:
            self.f.seek(prev)
            thisdir = self.directory_construct.parse_stream(self.f)
            entries = []
            
            for i in range(thisdir.num_entries):
                thisentry = self.direntry_construct.parse_stream(self.f)
                if thisentry.type > 0 :
                    entries.append(thisentry)
                    entry_count += 1
                    
            self.directory.extend(reversed(entries))
            prev = thisdir.prev
            
        self.directory.reverse()
    

    def get_knowledge(self, t):
        return self.knowledge.get(hex(t), {'info':f"Unknown ({hex(t)})"})


    def get_actual_id(self, item_id):
        if item_id == ~(-1<<32):
            return None
        return item_id
    

    def get_deepth_name(self, entry):
        if hex(entry.type) == '0x2760':
            deep_name = 'SVC'
        if hex(entry.type) == '0x2761':
            deep_name = 'DVC'
        if hex(entry.type) == '0x2762':
            deep_name = 'AVC'
        return deep_name


    def read_rgba_image(self, data):
        # Parse image
        rgba_image_construct = c.Struct('raster' / c.Bytes(len(data)))
        im = rgba_image_construct.parse(data)
        cols, rows = 512, 512
        # print(len(data))
        img = np.zeros((rows, cols, 3), dtype=np.uint8)
        ct = 0

        # Fill image
        for i in range(rows):
            for j in range(cols):
                for k in range(3):
                    img[i,j,k] = int(data[ct+k])
                ct += 4
        
        # Move error displacement image
        displacement = 15 # 14 16
        img_f = np.zeros((rows, cols, 3), dtype=np.uint8)
        img_f[:,:-displacement,:] = img[:, displacement:, :]
        img_f[:, -displacement:,:] = img[:, :displacement, :]

        im.raster = img_f
        return im
    

    def save(self, output_folder, hexcodes):
        # Iterate over directories avoiding unnecesary data
        for i in range(len(self.directory)):
            entry = self.directory[i]
            if hex(entry.type) not in hexcodes:
                continue

            # Get ids
            patient_id = self.get_actual_id(entry.patient_id)
            study_id = self.get_actual_id(entry.study_id)
            series_id = self.get_actual_id(entry.series_id)
                             
            # Get knowledge and parse data
            kl = self.get_knowledge(entry.type)
            self.f.seek(entry.start)
            entry_data = self.f.read(entry.size)
            item = dict()
            item_data = kl['parse'](entry_data)
            
            # Get laterality and OCTA images
            if hex(entry.type) == '0x3b':
                laterality = item_data['laterality']
                laterality = 'OD' if laterality == 'R' else 'OS'
            else:
                item['data'] = {}
                for k, v in item_data.items():
                    if k == 'raster':
                        deep_name = self.get_deepth_name(entry)
                        filename = f"{patient_id}_{study_id}_{series_id}_{deep_name}_{laterality}.png"
                        filename = os.path.join(output_folder, filename)
                        cv2.imwrite(filename, v)
                        print(f'Image saved - {filename}')



def extract_OCTA_from_e2e_folder(file_path, formatted_relative_path):
    # Crear carpeta si no existe
    os.makedirs(formatted_relative_path, exist_ok=True)

    # Ejecutar función principal
    with open(file_path, 'rb') as f:
        e2efile = StructureParser(f)
        e2efile.save(formatted_relative_path, ['0x3b', '0x2760', '0x2761', '0x2762'])


def main():
    root = tk.Tk()
    app = CustomFolderSelectorApp(root, extract_OCTA_from_e2e_folder)
    root.mainloop()


if __name__ == "__main__":
    main()