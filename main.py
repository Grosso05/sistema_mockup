import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np

class AplicacionMockup:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicación de Mockup")

        # Lista para almacenar cada lienzo y sus datos
        self.lienzos = []

        # Botones generales
        self.boton_reiniciar = tk.Button(root, text="Reiniciar App", command=self.reiniciar_app)
        self.boton_reiniciar.pack()

        # Botón para seleccionar el logo (el mismo para todos los mockups)
        self.boton_logo = tk.Button(root, text="Seleccionar Logo", command=self.seleccionar_logo)
        self.boton_logo.pack()

        # Crear dos botones para seleccionar el mockup de cada lienzo
        self.botones_mockup = []
        for i in range(2):
            boton_mockup = tk.Button(root, text=f"Seleccionar Mockup Lienzo {i+1}", command=lambda i=i: self.seleccionar_mockup(i))
            boton_mockup.pack()
            self.botones_mockup.append(boton_mockup)

        # Botón para colocar el logo en todos los lienzos
        self.boton_colocar_logo = tk.Button(root, text="Colocar Logo en Todos los Lienzos", command=self.colocar_logo_en_todos)
        self.boton_colocar_logo.pack()

    def reiniciar_app(self):
        # Reiniciar la aplicación volviendo a la configuración inicial
        for lienzo in self.lienzos:
            lienzo["mockup"] = None
            lienzo["logo"] = None
            lienzo["puntos_mockup"] = []
            lienzo["canvas"].delete("puntos", "imagen")  # Limpiar el lienzo

            # Restaurar el tamaño original de los lienzos
            lienzo["canvas"].config(width=400, height=300)

            # Eliminar referencias a las imágenes
            lienzo["imagen"] = None

    def capturar_clic(self, evento, lienzo):
        # Capturar los clics del usuario y agregarlos a la lista de puntos del mockup
        x, y = evento.x, evento.y
        lienzo["puntos_mockup"].append((x, y))

        # Dibujar un pequeño círculo en el lienzo para indicar el punto seleccionado
        lienzo["canvas"].create_oval(x-5, y-5, x+5, y+5, fill="red", tags="puntos")

    def seleccionar_mockup(self, indice_lienzo):
        mockup_path = filedialog.askopenfilename(title=f"Seleccionar Mockup Lienzo {indice_lienzo + 1}", filetypes=[("Archivos PNG", "*.png")])

        if mockup_path:
            lienzo = self.lienzos[indice_lienzo]
            lienzo["mockup"] = Image.open(mockup_path).convert("RGBA")
            lienzo["mockup"] = lienzo["mockup"].resize((400, 300))
            self.mostrar_imagen_en_lienzo(lienzo["mockup"], lienzo["canvas"], lienzo["imagen"])

    def seleccionar_logo(self):
        logo_path = filedialog.askopenfilename(title="Seleccionar Logo", filetypes=[("Archivos PNG", "*.png")])

        if logo_path:
            for lienzo in self.lienzos:
                lienzo["logo"] = Image.open(logo_path).convert("RGBA")

    def colocar_logo(self, lienzo):
        if lienzo["mockup"] and lienzo["logo"] and len(lienzo["puntos_mockup"]) == 4:
            # Ajustar el logo a la perspectiva del mockup
            logo_adaptado = self.adaptar_logo_a_perspectiva(lienzo["logo"], lienzo["puntos_mockup"])

            # Crear una nueva imagen con el fondo original y logo ajustado
            resultado = Image.alpha_composite(Image.new("RGBA", lienzo["mockup"].size, (0, 0, 0, 0)), lienzo["mockup"])

            # Pegar el logo ajustado en la imagen resultante
            resultado.paste(logo_adaptado, (0, 0), logo_adaptado)

            # Mostrar la imagen resultante en el lienzo
            self.mostrar_imagen_en_lienzo(resultado, lienzo["canvas"], lienzo["imagen"])

    def colocar_logo_en_todos(self):
        for lienzo in self.lienzos:
            self.colocar_logo(lienzo)

    def adaptar_logo_a_perspectiva(self, imagen, puntos_mockup):
        if len(puntos_mockup) == 4:
            # Puntos de destino en el logo
            puntos_logo = [(0, 0), (imagen.width, 0), (imagen.width, imagen.height), (0, imagen.height)]

            # Calcular la matriz de perspectiva
            matriz_perspectiva = self.calcular_matriz_perspectiva(puntos_logo, puntos_mockup)

            # Aplicar la transformación de perspectiva al logo
            logo_adaptado = self.aplicar_transformacion_perspectiva(imagen, matriz_perspectiva)

            return logo_adaptado

    def calcular_matriz_perspectiva(self, src_points, dst_points):
        # Calcular la matriz de perspectiva utilizando los puntos de origen y destino
        matriz_perspectiva, _ = cv2.findHomography(np.array(src_points), np.array(dst_points))
        return matriz_perspectiva

    def aplicar_transformacion_perspectiva(self, imagen, matriz_perspectiva):
        # Aplicar la transformación de perspectiva a la imagen
        imagen_transformada = cv2.warpPerspective(np.array(imagen), matriz_perspectiva, (imagen.width, imagen.height))
        imagen_transformada = Image.fromarray(cv2.cvtColor(imagen_transformada, cv2.COLOR_BGR2RGBA))
        return imagen_transformada

    def mostrar_imagen_en_lienzo(self, imagen, canvas, imagen_ref):
        # Borrar puntos anteriores del lienzo
        canvas.delete("puntos")
        
        imagen = ImageTk.PhotoImage(imagen)
        canvas.config(width=imagen.width(), height=imagen.height())
        canvas.create_image(0, 0, anchor=tk.NW, image=imagen, tags="imagen")
        canvas.imagen_ref = imagen

        # Actualizar referencia a la imagen actual en el lienzo
        imagen_ref = imagen

    def agregar_lienzo(self, canvas):
        # Agregar el lienzo a la lista con sus datos
        lienzo = {"canvas": canvas, "mockup": None, "logo": None, "puntos_mockup": [], "imagen": None}

        # Agregar la función de clic al lienzo
        canvas.bind("<Button-1>", lambda event, lienzo=lienzo: self.capturar_clic(event, lienzo))

        # Agregar el lienzo a la lista
        self.lienzos.append(lienzo)

if __name__ == "__main__":
    root = tk.Tk()
    aplicacion = AplicacionMockup(root)

    # Crear dos lienzos y agregarlos a la aplicación
    lienzo1 = tk.Canvas(root, width=400, height=300)
    lienzo1.pack()
    aplicacion.agregar_lienzo(lienzo1)

    lienzo2 = tk.Canvas(root, width=400, height=300)
    lienzo2.pack()
    aplicacion.agregar_lienzo(lienzo2)

    root.mainloop()
