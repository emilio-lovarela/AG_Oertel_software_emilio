#!/usr/bin/env python3

# Graphic interfaz
import tkinter as tk

# Array and image managment
import numpy as np
import cv2

# System packages
from pydicom import dcmread
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
        self.extensions_list = ('.DCM', '.dcm')


def extract_segmentations_from_dcm_folders(file_path, formatted_relative_path):
    # Crear carpeta si no existe
    os.makedirs(formatted_relative_path, exist_ok=True)

    # Leer el archivo DICOM
    ds = dcmread(file_path, force=True)
    
    # Diccionario de segmentaciones y sus nombres correspondientes
    segmentations = {
        0x1530: 'faz',  # Segmentacion faz
        0x1535: 'DVC',  # Segmentacion deep
        0x1540: 'SVC'   # Segmentacion sup
    }
    
    for idx, (tag, name) in enumerate(segmentations.items()):
        # Obtener el valor de segmentación
        img = ds[0x0073, tag].value
        
        # Convertir el valor a una matriz de numpy
        img = np.frombuffer(img, dtype=np.int8).reshape((512, 512)) * 255

        # Construir el nombre del archivo
        filename = os.path.basename(file_path)
        filename = filename.split('.')[0]
        filename = f"{filename}_{name}.png"
        filename = os.path.join(formatted_relative_path, filename)
        
        # Guardar la imagen
        cv2.imwrite(filename, img)
        print(f'Image saved - {filename}')


def main():
    root = tk.Tk()
    app = CustomFolderSelectorApp(root, extract_segmentations_from_dcm_folders)
    root.mainloop()


if __name__ == "__main__":
    main()