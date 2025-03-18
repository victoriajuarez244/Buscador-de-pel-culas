import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, 
                               QTableWidget, QLabel, QTableWidgetItem, QTabWidget)
from pymongo import MongoClient

class GestorPeliculas:
    def __init__(self):
        self.__client = MongoClient('mongodb://localhost:27017/')
        self.__db = self.__client['Peliculas']
        self.__coleccion = self.__db['Pelicula']

    def buscar_por_titulo(self, titulo):
        return list(self.__coleccion.find({"Título": {"$regex": titulo, "$options": "i"}}))

    def buscar_comunes(self, actor1, actor2):
        # Usar expresiones regulares para buscar actores en el campo "Actor Protagonista"
        return list(self.__coleccion.find({
            "Actor Protagonista": {"$regex": f"{actor1}.*{actor2}|{actor2}.*{actor1}", "$options": "i"}
        }))

class CatalogoPeliculas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__gestor = GestorPeliculas()

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
        self.__titulo_line_edit = QLineEdit(self)
        self.__titulo_line_edit.setPlaceholderText("Buscar por título")
        
        self.__buscar_button = QPushButton("Buscar", self)
        self.__buscar_button.clicked.connect(self.__buscar_peliculas)

        self.__resultado_table = QTableWidget(self)
        self.__resultado_table.setColumnCount(7)
        self.__resultado_table.setHorizontalHeaderLabels(["Título", "Año", "Género", "Puntuación", "Actor", "Clasificación", "Sinopsis"])

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Buscar Película por Título"))
        layout.addWidget(self.__titulo_line_edit)
        layout.addWidget(self.__buscar_button)
        layout.addWidget(self.__resultado_table)
        
        self.__pantalla_busqueda.setLayout(layout)

    def __buscar_peliculas(self):
        titulo = self.__titulo_line_edit.text()
        peliculas = self.__gestor.buscar_por_titulo(titulo)

        self.__resultado_table.setRowCount(0)
        for pelicula in peliculas:
            row_position = self.__resultado_table.rowCount()
            self.__resultado_table.insertRow(row_position)
            self.__resultado_table.setItem(row_position, 0, QTableWidgetItem(pelicula["Título"]))
            self.__resultado_table.setItem(row_position, 1, QTableWidgetItem(str(pelicula["Año"])))
            self.__resultado_table.setItem(row_position, 2, QTableWidgetItem(pelicula["Género"]))
            self.__resultado_table.setItem(row_position, 3, QTableWidgetItem(str(pelicula["Puntuación"])))
            self.__resultado_table.setItem(row_position, 4, QTableWidgetItem(", ".join(pelicula["Actor Protagonista"])))
            self.__resultado_table.setItem(row_position, 5, QTableWidgetItem(str(pelicula["Clasificación"])))
            self.__resultado_table.setItem(row_position, 6, QTableWidgetItem(pelicula["Sinopsis"]))

    def __crear_pantalla_comunes(self):
        self.__actor1_line_edit = QLineEdit(self)
        self.__actor1_line_edit.setPlaceholderText("Actor 1")
        
        self.__actor2_line_edit = QLineEdit(self)
        self.__actor2_line_edit.setPlaceholderText("Actor 2")

        self.__buscar_comunes_button = QPushButton("Buscar Películas Comunes", self)
        self.__buscar_comunes_button.clicked.connect(self.__buscar_peliculas_comunes)

        self.__resultado_comunes_table = QTableWidget(self)
        self.__resultado_comunes_table.setColumnCount(7)
        self.__resultado_comunes_table.setHorizontalHeaderLabels(["Título", "Año", "Género", "Puntuación", "Actor", "Clasificación", "Sinopsis"])

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Ingresa dos actores"))
        layout.addWidget(self.__actor1_line_edit)
        layout.addWidget(self.__actor2_line_edit)
        layout.addWidget(self.__buscar_comunes_button)
        layout.addWidget(self.__resultado_comunes_table)
        
        self.__pantalla_comunes.setLayout(layout)

    def __buscar_peliculas_comunes(self):
        actor1 = self.__actor1_line_edit.text().strip()
        actor2 = self.__actor2_line_edit.text().strip()
        
        if not actor1 or not actor2:
            return
        
        peliculas_comunes = self.__gestor.buscar_comunes(actor1, actor2)

        self.__resultado_comunes_table.setRowCount(0)
        for pelicula in peliculas_comunes:
            row_position = self.__resultado_comunes_table.rowCount()
            self.__resultado_comunes_table.insertRow(row_position)
            self.__resultado_comunes_table.setItem(row_position, 0, QTableWidgetItem(pelicula["Título"]))
            self.__resultado_comunes_table.setItem(row_position, 1, QTableWidgetItem(str(pelicula["Año"])))
            self.__resultado_comunes_table.setItem(row_position, 2, QTableWidgetItem(pelicula["Género"]))
            self.__resultado_comunes_table.setItem(row_position, 3, QTableWidgetItem(str(pelicula["Puntuación"])))
            self.__resultado_comunes_table.setItem(row_position, 4, QTableWidgetItem(", ".join(pelicula["Actor Protagonista"])))
            self.__resultado_comunes_table.setItem(row_position, 5, QTableWidgetItem(str(pelicula["Clasificación"])))
            self.__resultado_comunes_table.setItem(row_position, 6, QTableWidgetItem(pelicula["Sinopsis"]))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CatalogoPeliculas()
    window.show()
    sys.exit(app.exec())
