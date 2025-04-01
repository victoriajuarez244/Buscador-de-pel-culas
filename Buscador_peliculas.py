import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, 
                               QTableWidget, QLabel, QTableWidgetItem, QTabWidget, QMessageBox)
from pymongo import MongoClient

class Actor:
    def __init__(self, nombre):
        self.__nombre = nombre
        self.__peliculas = []

    def obtener_nombre(self):
        return self.__nombre

    def agregar_pelicula(self, pelicula):
        self.__peliculas.append(pelicula)

    def ha_trabajado_con(self, otro_actor):
        for pelicula in self.__peliculas:
            if pelicula.tiene_actor(otro_actor):
                return True
        return False

class Pelicula:
    def __init__(self, titulo, año, genero, puntuacion, actores, clasificacion, sinopsis):
        self.__titulo = titulo
        self.__año = año
        self.__genero = genero
        self.__puntuacion = puntuacion
        self.__actores = [Actor(actor) for actor in actores]  
        self.__clasificacion = clasificacion
        self.__sinopsis = sinopsis

        for actor in self.__actores:
            actor.agregar_pelicula(self)

    def obtener_datos(self):
        return [self.__titulo, str(self.__año), self.__genero, str(self.__puntuacion), 
                ', '.join([actor.obtener_nombre() for actor in self.__actores]), str(self.__clasificacion), self.__sinopsis]

    def tiene_actor(self, actor):
        return any(a.obtener_nombre() == actor.obtener_nombre() for a in self.__actores)

# Modelo
class GestorPeliculas:
    def __init__(self):
        self.__client = MongoClient('mongodb://localhost:27017/')
        self.__db = self.__client['Peliculas']
        self.__coleccion = self.__db['Pelicula']

    def buscar_por_titulo(self, titulo):
        peliculas = self.__coleccion.find({"Título": {"$regex": titulo, "$options": "i"}})
        return [Pelicula(p['Título'], p['Año'], p['Género'], p['Puntuación'], p['Actor Protagonista'], p['Clasificación'], p['Sinopsis']) for p in peliculas]

    def buscar_comunes(self, actor1, actor2):
        peliculas = self.__coleccion.find({"Actor Protagonista": {"$regex": f"{actor1}.*{actor2}|{actor2}.*{actor1}", "$options": "i"}})
        peliculas_obj = [Pelicula(p['Título'], p['Año'], p['Género'], p['Puntuación'], p['Actor Protagonista'], p['Clasificación'], p['Sinopsis']) for p in peliculas]
        
        comunes = []
        for pelicula in peliculas_obj:
            actor1_obj = next((actor for actor in pelicula._Pelicula__actores if actor.obtener_nombre() == actor1), None)
            actor2_obj = next((actor for actor in pelicula._Pelicula__actores if actor.obtener_nombre() == actor2), None)
            if actor1_obj and actor2_obj and actor1_obj.ha_trabajado_con(actor2_obj):
                comunes.append(pelicula)
        return comunes

# Vista
class VistaCatalogoPeliculas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Catálogo de Películas")
        self.setGeometry(100, 100, 800, 600)

        self.__tabs = QTabWidget(self)
        self.setCentralWidget(self.__tabs)

        self.__pantalla_busqueda = QWidget()
        self.__tabs.addTab(self.__pantalla_busqueda, "Búsqueda por Título")
        self.__crear_pantalla_busqueda()

        self.__pantalla_comunes = QWidget()
        self.__tabs.addTab(self.__pantalla_comunes, "Películas Comunes entre Actores")
        self.__crear_pantalla_comunes()

    def __crear_pantalla_busqueda(self):
        self.titulo_line_edit = QLineEdit(self)
        self.titulo_line_edit.setPlaceholderText("Buscar por título")

        self.buscar_button = QPushButton("Buscar", self)

        self.resultado_table = QTableWidget(self)
        self.resultado_table.setColumnCount(7)
        self.resultado_table.setHorizontalHeaderLabels(["Título", "Año", "Género", "Puntuación", "Actor", "Clasificación", "Sinopsis"])

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Buscar Película por Título"))
        layout.addWidget(self.titulo_line_edit)
        layout.addWidget(self.buscar_button)
        layout.addWidget(self.resultado_table)
        self.__pantalla_busqueda.setLayout(layout)

    def __crear_pantalla_comunes(self):
        self.actor1_line_edit = QLineEdit(self)
        self.actor1_line_edit.setPlaceholderText("Actor 1")

        self.actor2_line_edit = QLineEdit(self)
        self.actor2_line_edit.setPlaceholderText("Actor 2")

        self.buscar_comunes_button = QPushButton("Buscar Películas Comunes", self)

        self.resultado_comunes_table = QTableWidget(self)
        self.resultado_comunes_table.setColumnCount(7)
        self.resultado_comunes_table.setHorizontalHeaderLabels(["Título", "Año", "Género", "Puntuación", "Actor", "Clasificación", "Sinopsis"])

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Ingresa dos actores"))
        layout.addWidget(self.actor1_line_edit)
        layout.addWidget(self.actor2_line_edit)
        layout.addWidget(self.buscar_comunes_button)
        layout.addWidget(self.resultado_comunes_table)

        self.__pantalla_comunes.setLayout(layout)

    def mostrar_resultados(self, table, peliculas):
        table.setRowCount(0)
        for pelicula in peliculas:
            row = table.rowCount()
            table.insertRow(row)
            for col, dato in enumerate(pelicula.obtener_datos()):
                table.setItem(row, col, QTableWidgetItem(dato))

# Controlador
class ControladorCatalogoPeliculas:
    def __init__(self, vista, modelo):
        self.__vista = vista
        self.__modelo = modelo
        self.__vista.buscar_button.clicked.connect(self.buscar_peliculas)
        self.__vista.buscar_comunes_button.clicked.connect(self.buscar_peliculas_comunes)

    def buscar_peliculas(self):
        titulo = self.__vista.titulo_line_edit.text().strip()
        if not titulo:
            QMessageBox.warning(self.__vista, "Advertencia", "Por favor ingrese un título válido.")
            return
        peliculas = self.__modelo.buscar_por_titulo(titulo)
        if peliculas:
            self.__vista.mostrar_resultados(self.__vista.resultado_table, peliculas)
        else:
            QMessageBox.information(self.__vista, "Sin Resultados", "No se encontraron películas para el título proporcionado.")

    def buscar_peliculas_comunes(self):
        actor1 = self.__vista.actor1_line_edit.text().strip()
        actor2 = self.__vista.actor2_line_edit.text().strip()
        if not actor1 or not actor2:
            QMessageBox.warning(self.__vista, "Advertencia", "Por favor ingrese ambos actores.")
            return
        peliculas = self.__modelo.buscar_comunes(actor1, actor2)
        if peliculas:
            self.__vista.mostrar_resultados(self.__vista.resultado_comunes_table, peliculas)
        else:
            QMessageBox.information(self.__vista, "Sin Resultados", "No se encontraron películas comunes entre los actores proporcionados.")

app = QApplication(sys.argv)
modelo = GestorPeliculas()
vista = VistaCatalogoPeliculas()
controlador = ControladorCatalogoPeliculas(vista, modelo)
vista.show()
sys.exit(app.exec())
