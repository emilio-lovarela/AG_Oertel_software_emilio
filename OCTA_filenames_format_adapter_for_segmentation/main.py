# Graphic interfaz
import tkinter as tk

# Standar system packages
import os
import shutil
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

        # Agregar un pequeño diccionario con las traducciones
        translations = {
                "de": {
                    "two_folders_text": "Zwei Ordner Format"
                },
                "es": {
                    "two_folders_text": "Formato Dos Carpetas"
                },
                "default": {
                    "two_folders_text": "Two Folders Format"
                }
            }

        # Agregar check button
        self.recursive_var = tk.BooleanVar()
        self.recursive_button = tk.Checkbutton(self.main_frame, text=translations[self.system_locale]['two_folders_text'], variable=self.recursive_var)
        self.recursive_button.grid(row=1, column=1, padx=0, pady=5)

    def default_function_to_execute(self, folder_path, que=None, two_folders_format=False, extensions_list=('.jpg', '.jpeg', '.JPG', '.tiff', '.png', '.PNG')):
        """
        Formats file names and organizes folders for use OCTA segentation tool.
        
        Parameters:
            folder_path (str): Path of the source folder.
            que (queue.Queue, optional): Processing queue to report progress. Default is None.
            two_folders_format (bool, optional): Indicates whether a two-folder format will be used.
        """

        # Añadir '_output' al nombre de la carpeta raíz
        root_folder_name = os.path.basename(folder_path)
        root_folder_parent = os.path.dirname(folder_path)
        formatted_root_path = os.path.join(root_folder_parent, root_folder_name + '_output')

        # Recorrer cada carpeta dentro de la carpeta dada
        bool_check = False
        root = folder_path
        files = os.listdir(folder_path)
        files = [file for file in files if file.lower().endswith(extensions_list)] # Comprobar si el archivo es una imagen por su extensión
        n_files = len(files)
        
        # Aplly changes to image filenames
        if n_files > 0:
            bool_check = True
            for counter, file in enumerate(files):
                # Set process status
                id_processing = ' ' + str(counter + 1) + ' / ' + str(n_files)
                if que:
                    que.put(id_processing)

                # Set paths
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, folder_path)
                relative_dir = os.path.dirname(relative_path)
                formatted_relative_path = os.path.join(formatted_root_path, relative_dir)

                # Generate the final filename
                try:
                    out_filename, depth_octa = generate_output_filename(file, two_folders_format)
                    if two_folders_format == True:
                        formatted_relative_path = os.path.join(formatted_relative_path, depth_octa)
                    out_filename = os.path.join(formatted_relative_path, out_filename)

                    # Copiar el archivo a la carpeta formateada
                    os.makedirs(formatted_relative_path, exist_ok=True)
                    shutil.copy(file_path, out_filename)
                except Exception as e:
                    continue

        # Set sucess status
        if bool_check == False and que:
            que.put(False)
        elif bool_check == True and que:
            que.put(True)


def generate_output_filename(filename, two_folders_format):
    """
    Generates output file names with correct format.
    
    Parameters:
        filename (str): Input file name.
        two_folders_format (bool): Indicates whether a two-folder format will be used.
    
    Returns:
        output_filename (str): Formatted output file name.
        depth_octa (str): Depth label, if applicable.
    """
    output_filename = ""
    
    # Extraer el penúltimo número de la secuencia
    components = filename.split('_')
    if len(components) > 1:
        output_filename += components[0] + '_' + components[1]
    
    # Comprobar la existencia del patrón '_OD_'
    if '_OD_' in filename.upper():
        output_filename += '_OD'
    # Comprobar la existencia del patrón '_OS_'
    elif '_OS_' in filename.upper():
        output_filename += '_OS'
    else:
        # Si no existe ninguno de los patrones anteriores, añadir '_NA_'
        output_filename += '_NA'
    
    # Comprobar la existencia de 'Superfiziell' o 'Tief'
    depth_octa = ''
    if 'Superfiziell'.upper() in filename.upper():
        if two_folders_format == True:
            depth_octa = 'SVC'
        else:
            # output_filename += '_Superfiziell'
            output_filename += '_SVC'
    elif 'Tief'.upper() in filename.upper():
        if two_folders_format == True:
            depth_octa = 'DVC'
        else:
            # output_filename += '_Tief'
            output_filename += '_DVC'

    # Añadir la extensión original del fichero
    _, extension = os.path.splitext(filename)
    output_filename += extension
    
    return output_filename, depth_octa



def main():
    root = tk.Tk()
    app = CustomFolderSelectorApp(root, None)
    root.mainloop()

if __name__ == "__main__":
    main()