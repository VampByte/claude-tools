"""Instalador de claude-tools: python instalar.py"""
import sys

if sys.version_info < (3, 10):
    sys.exit("Hace falta Python 3.10 o superior (winget install Python.Python.3.13).")

from installer.menu import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
