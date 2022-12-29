# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys

from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PyQt5 import QtWidgets, uic


app = QtWidgets.QApplication([])
widget = uic.loadUi("mainwindow.ui")
widget.show()
sys.exit(app.exec_())
