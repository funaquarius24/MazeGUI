from PyQt5.QtCore import QFile, QSize, Qt
from PyQt5 import QtSvg
from PyQt5.QtGui import QBrush, QColor, QImage, QPainter, QPixmap, QPen
from PyQt5.QtWidgets import (QActionGroup, QApplication, QFileDialog,
        QGraphicsItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView, QLabel,
        QMainWindow, QMenu, QMessageBox, QWidget)
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget
from PyQt5.QtSvg import QGraphicsSvgItem
import sys

app = QApplication(sys.argv) 

widget = QLabel()
widget.setGeometry(50,200,500,500)
renderer =  QtSvg.QSvgRenderer('test.svg')
widget.resize(renderer.defaultSize())
painter = QPainter(widget)
painter.restore()
renderer.render(painter)
widget.show()

sys.exit(app.exec_())