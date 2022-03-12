from PyQt6 import QtCore, QtGui, QtWidgets, QtSvg, QtSvgWidgets
import sys


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # self.openGLWidget = QSvgWidget('C:/Windows/Temp/tubesheetsvgpreview.svg')
        # self.openGLWidget = QSvgWidget.(self.centralwidget)
        # self.openGLWidget.setGeometry(QtCore.QRect(29, 19, 741, 521))
        # self.openGLWidget.setObjectName("openGLWidget")


        print(dir(QtSvgWidgets.QSvgWidget))
        self.viewer = QtSvgWidgets.QSvgWidget()
        self.viewer.load('test.svg')
        self.viewer.setGeometry(0,0,600,600)
        self.viewer.show()

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())