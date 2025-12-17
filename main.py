# -----------------------------------------------------------------------------
# ELIXIR HUB - Open Source Project
# Copyright (C) 2025 [Libba/ElixirDev]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# -----------------------------------------------------------------------------

import sys
import os
import json
import webbrowser
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QListWidget, 
                             QPushButton, QFrame, QListWidgetItem, QStackedWidget)
from PyQt6.QtCore import Qt

# --- CONFIGURACIÓN VISUAL ---
CARPETA_JSON = "links"
COLOR_ACCENT = "#7b2cbf" # Elixir Purple
COLOR_BG_MAIN = "#000000"
COLOR_BG_SIDE = "#050505"

class ElixirApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ELIXIR | Open Source Edition")
        self.resize(1000, 650)
        self.setMinimumSize(850, 500)
        self.todos_los_items = []
        self.item_actual = None
        self.setup_ui()
        self.aplicar_estilos()
        self.cargar_datos()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # PANEL IZQUIERDO
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(280)
        layout_side = QVBoxLayout(self.sidebar)
        layout_side.setContentsMargins(20, 30, 20, 20)
        layout_side.setSpacing(15)

        lbl_brand = QLabel("ELIXIR")
        lbl_brand.setObjectName("brand_top")
        lbl_brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_side.addWidget(lbl_brand)

        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("Search database...")
        self.buscador.textChanged.connect(self.filtrar_lista)
        layout_side.addWidget(self.buscador)

        self.lista_widget = QListWidget()
        self.lista_widget.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lista_widget.itemClicked.connect(self.abrir_item)
        layout_side.addWidget(self.lista_widget)
        main_layout.addWidget(self.sidebar)

        # PANEL DERECHO
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # Pagina 0: Bienvenida
        self.page_welcome = QFrame()
        self.page_welcome.setObjectName("page_welcome")
        layout_welcome = QVBoxLayout(self.page_welcome)
        layout_welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_big_logo = QLabel("ELIXIR")
        self.lbl_big_logo.setObjectName("big_logo")
        self.lbl_big_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub = QLabel("S ELECT   F I L E")
        lbl_sub.setObjectName("lbl_sub")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_welcome.addWidget(self.lbl_big_logo)
        layout_welcome.addWidget(lbl_sub)
        self.stack.addWidget(self.page_welcome)

        # Pagina 1: Detalle
        self.page_detail = QFrame()
        self.page_detail.setObjectName("page_detail")
        layout_detail = QVBoxLayout(self.page_detail)
        layout_detail.setContentsMargins(50, 40, 50, 50)
        layout_detail.setAlignment(Qt.AlignmentFlag.AlignTop)

        header_layout = QHBoxLayout()
        self.lbl_titulo = QLabel("TITLE")
        self.lbl_titulo.setObjectName("lbl_titulo")
        self.lbl_titulo.setWordWrap(True)
        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("btn_close")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setFixedSize(40, 40)
        self.btn_close.clicked.connect(self.cerrar_detalle)
        header_layout.addWidget(self.lbl_titulo)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_close)
        layout_detail.addLayout(header_layout)

        linea = QFrame()
        linea.setObjectName("linea_accent")
        linea.setFixedHeight(2)
        linea.setFixedWidth(120)
        layout_detail.addWidget(linea)
        layout_detail.addSpacing(20)

        self.lbl_desc = QLabel("Description...")
        self.lbl_desc.setObjectName("lbl_desc")
        self.lbl_desc.setWordWrap(True)
        layout_detail.addWidget(self.lbl_desc)

        self.lbl_creditos = QLabel("Dev: Unknown")
        self.lbl_creditos.setObjectName("lbl_creditos")
        layout_detail.addWidget(self.lbl_creditos)
        layout_detail.addSpacing(40)

        self.btn_action = QPushButton("EXECUTE / DOWNLOAD")
        self.btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_action.setFixedHeight(55)
        self.btn_action.clicked.connect(self.ejecutar_accion)
        layout_detail.addWidget(self.btn_action)
        layout_detail.addStretch()
        self.stack.addWidget(self.page_detail)

    def aplicar_estilos(self):
        estilo = f"""
        QMainWindow {{ background-color: {COLOR_BG_MAIN}; }}
        #sidebar {{ background-color: {COLOR_BG_SIDE}; border-right: 1px solid #151515; }}
        #brand_top {{ font-family: 'Impact'; font-size: 24px; color: #444; letter-spacing: 2px; }}
        QLineEdit {{ background-color: #0f0f0f; border: 1px solid #222; border-radius: 6px; padding: 10px; color: white; font-size: 13px; font-family: 'Segoe UI'; }}
        QLineEdit:focus {{ border: 1px solid {COLOR_ACCENT}; background-color: #120518; }}
        QListWidget {{ border: none; background-color: transparent; outline: none; }}
        QListWidget::item {{ color: #888; padding: 14px 10px; border-bottom: 1px solid #0e0e0e; font-size: 13px; }}
        QListWidget::item:hover {{ background-color: #0e0e0e; color: #ccc; }}
        QListWidget::item:selected {{ background-color: #12021a; color: white; border-left: 2px solid {COLOR_ACCENT}; }}
        #page_welcome {{ background-color: {COLOR_BG_MAIN}; }}
        #big_logo {{ font-family: 'Impact'; font-size: 120px; color: #0f0f0f; }}
        #lbl_sub {{ font-family: 'Arial'; font-size: 14px; color: #333; letter-spacing: 5px; font-weight: bold; }}
        #page_detail {{ background-color: {COLOR_BG_MAIN}; }}
        #lbl_titulo {{ font-family: 'Arial Black'; font-size: 42px; color: white; }}
        #linea_accent {{ background-color: {COLOR_ACCENT}; border: none; }}
        #lbl_desc {{ font-family: 'Segoe UI'; font-size: 16px; color: #aaaaaa; line-height: 1.5; }}
        #lbl_creditos {{ font-family: 'Consolas'; font-size: 12px; color: #555; margin-top: 5px; }}
        #btn_close {{ background-color: transparent; color: #333; font-size: 20px; border: none; font-weight: bold; }}
        #btn_close:hover {{ color: white; background-color: #1a1a1a; border-radius: 20px; }}
        QPushButton {{ background-color: {COLOR_ACCENT}; color: white; border-radius: 6px; font-weight: bold; font-size: 14px; border: none; }}
        QPushButton:hover {{ background-color: #9d4edd; }}
        QPushButton:pressed {{ background-color: #5a189a; }}
        """
        self.setStyleSheet(estilo)

    def cargar_datos(self):
        if not os.path.exists(CARPETA_JSON):
            os.makedirs(CARPETA_JSON)
        self.todos_los_items = []
        try:
            archivos = os.listdir(CARPETA_JSON)
            for archivo in archivos:
                if archivo.endswith(".json"):
                    ruta = os.path.join(CARPETA_JSON, archivo)
                    if os.path.getsize(ruta) == 0: continue
                    try:
                        with open(ruta, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if "name" in data: self.todos_los_items.append(data)
                    except: pass
        except: pass
        self.actualizar_lista(self.todos_los_items)

    def actualizar_lista(self, items):
        self.lista_widget.clear()
        for item in items:
            list_item = QListWidgetItem(item.get("name", "Unknown"))
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self.lista_widget.addItem(list_item)

    def filtrar_lista(self, texto):
        t = texto.lower()
        self.actualizar_lista([i for i in self.todos_los_items if t in i.get("name", "").lower()])

    def abrir_item(self, list_item):
        data = list_item.data(Qt.ItemDataRole.UserRole)
        self.item_actual = data
        self.lbl_titulo.setText(data.get("name", "Error"))
        self.lbl_desc.setText(data.get("descripcion", "No description."))
        self.lbl_creditos.setText(f"// CODE BY: {data.get('creditos', 'Unknown')}")
        self.stack.setCurrentIndex(1)

    def cerrar_detalle(self):
        self.lista_widget.clearSelection()
        self.item_actual = None
        self.stack.setCurrentIndex(0)

    def ejecutar_accion(self):
        if self.item_actual and "link" in self.item_actual:
            webbrowser.open(self.item_actual["link"])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ElixirApp()
    window.show()
    sys.exit(app.exec())