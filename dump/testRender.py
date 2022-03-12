from PyQt6.QtWidgets import (QWidget, QHBoxLayout, 
        QLabel, QApplication)
from PyQt6.QtGui import QPixmap, QPainter
import sys
from PyQt5.QtSvg import QSvgWidget

app = QApplication(sys.argv) 

widget = QLabel()
widget.setGeometry(50,200,500,500)
renderer =  QSvgWidget.QSvgRenderer('Zeichen_123.svg')
widget.resize(renderer.defaultSize())
painter = QPainter(widget)
painter.restore()
renderer.render(painter)
widget.show()

sys.exit(app.exec_())