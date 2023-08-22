import sys
from PyQt5 import QtWidgets
from .WindowController import WindowController

def main():
    app = QtWidgets.QApplication(sys.argv)
    fiber = WindowController()
    fiber.show()
    return app.exec_()
