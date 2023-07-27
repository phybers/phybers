import sys
from PyQt5 import QtGui, QtWidgets, uic, QtCore
from .WindowController import WindowController

def main():
    app = QtWidgets.QApplication(sys.argv)
    fiber = WindowController()
    fiber.show()

    sys.exit(app.exec_())
