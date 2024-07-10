# Graphic interfaz
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# Multi Thread
import threading
import queue

# Local Language and files management
import locale
import json
import os


class FolderSelectorApp:
    """
    This class represents an application for selecting folders with a graphical interface.

    Inputs:
        - master: The master widget, usually the main application window.
        - function_to_execute: A function to be executed when the "Run" button is clicked.
        - translation_file (optional): path to file with translations

    Methods:
        - create_widgets(): Creates and configures the graphical interface widgets.
        - select_folder(): Opens a file dialog to select a folder and sets the selected folder path.
        - run_function(): Executes the specified function in a separate thread when the "Run" button is clicked.
        - catch_except_thread_function(): Executes the specified function within a thread, catching and handling any exceptions that may occur.
        - check_thread(): Continuously monitors the execution status of the function thread and updates the interface accordingly upon completion.
        - default_function_to_execute(): Default function that search for files in a loop.
        - on_function_complete(): Handles the completion of the executed function and updates the interface accordingly.
    """
    def __init__(self, master, function_to_execute, translation_file='../Common_utils/translations.json'):
        # Set principal components
        self.master = master
        self.function_to_execute = function_to_execute
        self.file_processing_counter = 0
        self.extensions_list = ('.jpg', '.jpeg', '.JPG', '.tiff', '.png', '.PNG')

        # Get Translations from json
        with open(translation_file, "r", encoding="utf-8") as file:
            self.translations = json.load(file)
        
        # Set language
        self.system_locale, _ = locale.getdefaultlocale()
        self.system_locale = self.system_locale[:2]
        if self.system_locale not in self.translations:
            self.system_locale = 'default'
        
        self.translations[self.system_locale]['window_title'] = os.path.basename(os.getcwd())

        # Init variables
        self.master.title(self.translations[self.system_locale]['window_title'])
        # self.master.geometry("380x200")  # Tamaño de la ventana principal
        self.master.resizable(False, False)  # No permitir redimensionamiento de la ventana
        self.selected_folder = tk.StringVar()
        self.processing_text_var = tk.StringVar()
        self.processing_text_var.set(self.translations[self.system_locale]['processing_text'])
        self.que = queue.LifoQueue()

        self.create_widgets()

    def create_widgets(self):
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.select_button = tk.Button(self.main_frame, text=self.translations[self.system_locale]['select_button_text'], command=self.select_folder)
        self.select_button.grid(row=0, column=0, padx=10, pady=5)

        self.run_button = tk.Button(self.main_frame, text=self.translations[self.system_locale]['run_button_text'], command=self.run_function)
        self.run_button.grid(row=0, column=1, padx=10, pady=5)

        self.recursive_var = tk.BooleanVar()
        self.recursive_button = tk.Checkbutton(self.main_frame, text=self.translations[self.system_locale]['recursive_search'], variable=self.recursive_var)
        self.recursive_button.grid(row=1, column=1, padx=0, pady=5)

        self.label = tk.Label(self.main_frame, text=self.translations[self.system_locale]['folder_selected_text'])
        self.label.grid(row=1, column=0, columnspan=1, pady=5)

        self.folder_display = tk.Label(self.main_frame, textvariable=self.selected_folder, wraplength=300, justify=tk.CENTER)
        self.folder_display.config(fg="darkblue")
        self.folder_display.grid(row=2, column=0, columnspan=2, pady=5)

        self.processing_label = tk.Label(self.main_frame, textvariable=self.processing_text_var, wraplength=300, justify=tk.CENTER)
        self.success_label = tk.Label(self.main_frame, text=self.translations[self.system_locale]['success_message'])

    def select_folder(self):
        self.success_label.grid_forget()  # Ocultar el mensaje de éxito
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.selected_folder.set(folder_path)

    def run_function(self):
        self.file_processing_counter = 0
        while not self.que.empty():
            self.que.get_nowait()  # Descarta elementos de la cola si los hay

        # Messages establishment
        self.success_label.grid_forget()  # Ocultar el mensaje de éxito
        selected_folder = self.selected_folder.get()
        if not selected_folder:
            messagebox.showerror(self.translations[self.system_locale]['error_title'], self.translations[self.system_locale]['error_message'])
            return

        self.run_button.config(state=tk.DISABLED)  # Desactivar el botón mientras se ejecuta la función
        self.select_button.config(state=tk.DISABLED)  # Desactivar el botón de selección de carpeta

        # Mostrar mensaje de procesando
        self.processing_label.grid(row=3, column=0, columnspan=2, pady=5)

        # Ejecutar la función en un hilo para evitar bloquear la interfaz gráfica
        thread = threading.Thread(target=self.catch_except_thread_function, args=(selected_folder, self.que, self.recursive_var.get(), self.extensions_list))
        thread.daemon = True
        thread.start()

        # Esperar a que la función termine y luego mostrar el mensaje de éxito o error
        self.master.after(100, lambda: self.check_thread(thread))

    def catch_except_thread_function(self, *args):
        try:
            self.default_function_to_execute(*args)
        except Exception as e:
            print("Exception detected:", e)
            self.que.put(False)

    def check_thread(self, thread):
        if thread.is_alive():
            # Si el hilo aún está vivo, programamos una nueva verificación después de un breve intervalo
            if self.que.empty() == False:
                id_proccesing = self.que.get()
                if id_proccesing == True:
                    self.que.put(True)
                elif id_proccesing == False:
                    self.que.put(False)
                else:
                    file_processing_counter = int(id_proccesing.split('/')[0].strip())
                    if file_processing_counter > self.file_processing_counter:
                        self.processing_text_var.set(self.translations[self.system_locale]['processing_text'] + id_proccesing)
                        self.file_processing_counter = file_processing_counter
            self.master.after(100, lambda: self.check_thread(thread))
        else:
            # Cuando el hilo ha terminado, ejecutamos la función on_function_complete
            self.on_function_complete()

    def default_function_to_execute(self, folder_path, que=None, recursive_search=False, extensions_list=('.jpg', '.jpeg', '.JPG', '.tiff', '.png', '.PNG')):
        # Añadir '_output' al nombre de la carpeta raíz
        root_folder_name = os.path.basename(folder_path)
        root_folder_parent = os.path.dirname(folder_path)
        formatted_root_path = os.path.join(root_folder_parent, root_folder_name + '_output')

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
                    relative_path = os.path.relpath(file_path, folder_path)
                    relative_dir = os.path.dirname(relative_path)
                    formatted_relative_path = os.path.join(formatted_root_path, relative_dir)

                    # Ejecutar función principal
                    try:
                        self.function_to_execute(file_path, formatted_relative_path)
                    except Exception as e:
                        continue

            # Si no es búsqueda recursiva, salir del bucle después de la primera iteración
            if not recursive_search:
                break

        # Set success status
        if bool_check == False and que:
            que.put(False)
        elif bool_check == True and que:
            que.put(True)

    def on_function_complete(self):
        self.run_button.config(state=tk.NORMAL)  # Activar el botón después de que la función haya terminado
        self.select_button.config(state=tk.NORMAL)  # Activar el botón de selección de carpeta después de que la función haya terminado
        self.processing_text_var.set(self.translations[self.system_locale]['processing_text']) # Default processing message
        self.processing_label.grid_forget()  # Ocultar el mensaje de procesando

        # Final message and reiniciate queue
        success = self.que.get()
        if success == True:
            self.success_label.config(text=self.translations[self.system_locale]['success_message'], fg="green")  # Cambiar el color del texto a verde para indicar éxito
            self.success_label.grid(row=3, column=0, columnspan=2, pady=5)
        else:
            self.success_label.config(text=self.translations[self.system_locale]['no_images_message'], fg="red")  # Cambiar el color del texto a rojo para indicar error
            self.success_label.grid(row=3, column=0, columnspan=2, pady=5)
