import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
from epub_processor import procesar_epub
class EpubSummarizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Resumidor de EPUBs")
        self.root.geometry("600x400")

        # Variables
        self.archivo_epub = tk.StringVar()
        self.archivo_salida = tk.StringVar()

        # Crear interfaz
        self.crear_widgets()

    def crear_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Botones y campos
        ttk.Button(main_frame, text="Seleccionar EPUB", command=self.seleccionar_epub).grid(row=0, column=0, pady=5)
        ttk.Label(main_frame, textvariable=self.archivo_epub).grid(row=0, column=1, pady=5)

        ttk.Button(main_frame, text="Seleccionar Destino", command=self.seleccionar_destino).grid(row=1, column=0, pady=5)
        ttk.Label(main_frame, textvariable=self.archivo_salida).grid(row=1, column=1, pady=5)

        ttk.Button(main_frame, text="Procesar", command=self.procesar).grid(row=2, column=0, columnspan=2, pady=20)

        # Barra de progreso
        self.progreso = ttk.Progressbar(main_frame, length=300, mode='indeterminate')
        self.progreso.grid(row=3, column=0, columnspan=2, pady=10)

    def seleccionar_epub(self):
        filename = filedialog.askopenfilename(filetypes=[("EPUB files", "*.epub")])
        self.archivo_epub.set(filename)

    def seleccionar_destino(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        self.archivo_salida.set(filename)

    def procesar(self):
        if not self.archivo_epub.get() or not self.archivo_salida.get():
            messagebox.showerror("Error", "Selecciona archivos de entrada y salida")
            return

        self.progreso.start()
        try:
            ruta_completa = os.path.abspath(self.archivo_salida.get())
            procesar_epub(self.archivo_epub.get(), ruta_completa)
            
            # Mostrar mensaje con la ruta y abrir la carpeta
            messagebox.showinfo("Éxito", f"Archivo guardado en:\n{ruta_completa}")
            os.startfile(os.path.dirname(ruta_completa))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante el procesamiento: {str(e)}")
        finally:
            self.progreso.stop()
if __name__ == "__main__":
    root = tk.Tk()
    app = EpubSummarizerGUI(root)
    root.mainloop()
