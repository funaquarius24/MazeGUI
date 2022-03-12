import sys
from PyQt6.QtWidgets import (QApplication, QWidget
, QLineEdit, QTextBrowser, QPushButton, QVBoxLayout)
from PyQt6.QtGui import QFont

class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.grid = ""

    def initUI(self):
        self.le = QLineEdit()
        self.le.returnPressed.connect(self.append_text)

        self.tb = QTextBrowser()
        self.tb.setAcceptRichText(True)
        self.tb.setOpenExternalLinks(True)

        self.clear_btn = QPushButton('Clear')
        self.clear_btn.pressed.connect(self.clear_text)

        vbox = QVBoxLayout()
        vbox.addWidget(self.le, 0)
        vbox.addWidget(self.tb, 1)
        vbox.addWidget(self.clear_btn, 2)

        self.setLayout(vbox)

        self.setWindowTitle('QTextBrowser')
        self.setGeometry(300, 300, 300, 300)
        self.show()

        from weave_maze import WeaveMazeGenerator
        self.maze = WeaveMazeGenerator()
        self.grid = self.maze.render_maze(20, 20, 20, False)
        print('grid')
        print(self.grid)
        self.append_text()

    def append_text(self):
        font = QFont()
        font.setStyleHint(QFont.StyleHint.Monospace)
        text = self.le.setFont(font)
        self.tb.append(self.grid)
        self.le.clear()

    def clear_text(self):
        self.tb.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec())