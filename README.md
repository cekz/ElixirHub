# ELIXIR HUB | Open Source

![License](https://img.shields.io/badge/license-GPLv3-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow.svg)
![Status](https://img.shields.io/badge/status-active-green.svg)

**Elixir Hub** es un gestor de scripts y enlaces centralizado, diseñado con una interfaz moderna en modo oscuro (Dark UI) usando PyQt6. Cuenta con un sistema de auto-actualización inteligente que sincroniza bases de datos JSON y el ejecutable principal desde tu propia infraestructura en la nube.

## 🚀 Características

- **Interfaz Moderna:** Diseño minimalista "Full Black" con acentos púrpuras.
- **Auto-Update System:** El `launcher.py` verifica hash/tamaño de archivos remotos y descarga solo lo necesario.
- **Instalación Silenciosa:** Se instala en `%LOCALAPPDATA%` y crea accesos directos automáticamente.
- **Base de Datos Dinámica:** Lee archivos `.json` locales que se sincronizan desde un almacenamiento remoto.
- **Protección de Fallos:** Manejo de errores si la conexión no está disponible (modo offline).

## 🛠️ Requisitos

- Python 3.10 o superior
- Librerías necesarias:
  ```bash
  pip install PyQt6 winshell pypiwin32 pyinstaller supabase