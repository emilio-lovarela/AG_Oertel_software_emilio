#!/usr/bin/env python3

# Graphic interfaz
import tkinter as tk

# System packages
import csv
import os
import sys
sys.path.append('../Common_utils')

# Date and time packages
from datetime import datetime

# Base interfaz class
from interfaz_base import FolderSelectorApp


class CustomFolderSelectorApp(FolderSelectorApp):
    """
    Modified FolderSelector with a check button
    """
    def create_widgets(self):
        super().create_widgets()  # Llama al método create_widgets de la clase base
        self.extensions_list = ('.csv', '.CSV')

    def default_function_to_execute(self, folder_path, que=None, recursive_search=False, extensions_list=('.csv', '.CSV')):
        # Añadir '_output' al nombre de la carpeta raíz
        root_folder_name = os.path.basename(folder_path)
        root_folder_parent = os.path.dirname(folder_path)
        formatted_root_path = os.path.join(root_folder_parent, root_folder_name + '_output')
        os.makedirs(formatted_root_path, exist_ok=True)

        # Calcular el número total de archivos a procesar
        total_files = 0
        for current_root, _, files in os.walk(folder_path):
            # Si no es búsqueda recursiva, no descender a subdirectorios
            if not recursive_search and current_root != folder_path:
                break

            # Filtrar archivos por extensión
            files = [file for file in files if file.lower().endswith(extensions_list)]
            total_files += len(files)

        # Recorrer las carpetas y archivos
        bool_check = False
        if total_files > 0:
            # Escribir los resultados en un nuevo archivo CSV
            today = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_file_path = os.path.join(formatted_root_path, 'Eye_csv_data_' + today + '.csv')
            with open(output_file_path, mode='w', newline='') as output_csvfile:
                csvwriter = csv.writer(output_csvfile, delimiter=',') # Use , or ;
                header_csv = ['ID', 'Eye', 'Color']

                # Iterate over csv files
                counter = 0
                for current_root, _, files in os.walk(folder_path):
                    # Si no es búsqueda recursiva, no descender a subdirectorios
                    if not recursive_search and current_root != folder_path:
                        break

                    # Filtrar archivos por extensión
                    files = [file for file in files if file.lower().endswith(extensions_list)]
                    n_files = len(files)

                    if n_files > 0:
                        bool_check = True
                        for file in files:
                            # Set process status
                            counter += 1
                            id_processing = ' ' + str(counter) + ' / ' + str(total_files)
                            if que:
                                que.put(id_processing)

                            # Set paths
                            file_path = os.path.join(current_root, file)

                            # Ejecutar función principal
                            try:
                                list_to_csv = self.function_to_execute(file_path)
                            except Exception as e:
                                continue

                            # Add header to csv output file
                            if counter == 1:
                                enum_number = max(len(item) for item in list_to_csv) - 3
                                header_csv.extend([enum_counter for enum_counter in range(1, enum_number)])
                                csvwriter.writerow(header_csv)

                            # Add lines to csv output file
                            for item in list_to_csv:
                                csvwriter.writerow(item)

                    # Si no es búsqueda recursiva, salir del bucle después de la primera iteración
                    if not recursive_search:
                        break

        # Set success status
        if bool_check == False and que:
            que.put(False)
        elif bool_check == True and que:
            que.put(True)



def convert_multiple_csv_to_one(file_path):
    # Lista de colores
    filename = os.path.basename(file_path).replace('.csv', '').replace('.CSV', '').replace('_data', '')
    colors = ['red', 'red', 'blue', 'blue', 'white', 'white']
    od_os = ['OD', 'OS']
    result = []

    with open(file_path, mode='r', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        
        # Saltar la primera línea (encabezado)
        next(csvreader)
        
        # Inicializar el alternador y el índice de color
        od_os_index = 0
        color_index = 0

        for row in csvreader:
            current_od_os = od_os[od_os_index % 2]
            current_color = colors[color_index % len(colors)]
            
            # Crear la lista con los tres elementos
            new_row = [filename, current_od_os, current_color] + row
            
            # Agregar la fila resultante a la lista de resultados
            result.append(new_row)
            
            # Actualizar los índices
            od_os_index += 1
            color_index += 1

    return result



def main():
    root = tk.Tk()
    app = CustomFolderSelectorApp(root, convert_multiple_csv_to_one)
    root.mainloop()


if __name__ == "__main__":
    main()
