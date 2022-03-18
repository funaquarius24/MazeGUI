from math import floor
import sys
import shutil
from datetime import datetime
import os

from turtle import width
from PyQt6 import QtCore, QtGui, QtWidgets, QtSvgWidgets
import PyQt6
from PyQt6.QtWidgets import QVBoxLayout, QFileDialog 
from PyQt6 import uic
from sklearn import isotonic
from mazemaker.mazemaker import MazeMaker
from renderers import ismoetric

from weave.weave_maze import WeaveMazeGenerator
from pymaze.maze_manager import MazeManager
from colormaze.colormaze import ColorMaze
from maskedmazegen.masked_maze_gen import MaskedMazeGenerator
from manual.manual_maze_gen import ManualMazeGenerator

qtcreator_file  = "assets/ui/mainwindow.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.maze = WeaveMazeGenerator()
        self.maze_style_name = 'weave'
        self.tab_image_ext = 'svg'
        self.currentStyleTab = "Style1"
        self.hide_and_show_butons("Style1")

        ### Media Viewers ###
        self.sceneViewer1 = QtSvgWidgets.QSvgWidget()
        self.sceneViewer1.setGeometry(QtCore.QRect(0,0,800,800))
        self.sceneViewer1.setParent(self.style1Tab)

        self.sceneViewer2 = QtSvgWidgets.QSvgWidget()
        self.sceneViewer2.setGeometry(QtCore.QRect(0,0,800,800))
        self.sceneViewer2.setParent(self.style1Tab)

        self.sceneViewer3 = QtWidgets.QGraphicsView(self.style3Tab)
        self.scene3 = QtWidgets.QGraphicsScene()

        self.sceneViewer4 = QtWidgets.QGraphicsView(self.style4Tab)
        self.scene4 = QtWidgets.QGraphicsScene()

        self.sceneViewer5 = QtSvgWidgets.QSvgWidget()
        self.sceneViewer5.setGeometry(QtCore.QRect(0,0,800,800))
        self.sceneViewer5.setParent(self.style5Tab)

        self.sceneViewerManual = QtWidgets.QGraphicsView(self.manualTab)
        self.sceneManual = QtWidgets.QGraphicsScene()

        ### Media Viewers ###

        ### Layouts ###
        self.style1Layout = QVBoxLayout(self.style1Tab)
        self.style1Layout.addWidget(self.sceneViewer1)

        self.style2Layout = QVBoxLayout(self.style2Tab)
        self.style2Layout.addWidget(self.sceneViewer2)

        self.style3Layout = QVBoxLayout(self.style3Tab)
        self.style3Layout.addWidget(self.sceneViewer3)

        self.style4Layout = QVBoxLayout(self.style4Tab)
        self.style4Layout.addWidget(self.sceneViewer4)

        self.style5Layout = QVBoxLayout(self.style5Tab)
        self.style5Layout.addWidget(self.sceneViewer5)

        self.manualLayout = QVBoxLayout(self.manualTab)
        self.manualLayout.addWidget(self.sceneViewerManual)

        ### Layouts ###

        ### Grid Objects ###
        self.style1_grid_object = None
        self.style2_grid_object = None
        self.style3_grid_object = None
        self.style4_grid_object = None
        self.style5_grid_object = None
        self.manual_grid_object = None

        ### Grid Objects ### 


        self.asset_folder = "assets/test_templates"
        self.destination_folder = "assets"
        self.currently_rendered_file = ""
        self.current_solution_file = ""
        self.mask_file = "mask.png"

        self.floorColorButton.setStyleSheet("QWidget { background-color: #fff}")
        self.floorColorButton.setStyleSheet("QWidget { background-color: #000}")
        self.isometricBackgroundButton.setStyleSheet("QWidget { background-color: #232}")
        self.wall_color = (255, 255, 255)
        self.floor_color = (0, 0, 0)
        self.isometric_background_color = (10, 40, 10)




        # print(dir(self.style1Tab))
        self.connectMazeTabs()

        
        self.connectButtons()
        self.connectMenuOptions()
        self.connectEdits()

    def greetings(self, arg):
        self.widthSpinBox.setValue(10)
        print(arg)

    def connectButtons(self):
        self.saveButton.clicked.connect(self.save)
        self.solveButton.clicked.connect(self.solve)
        self.generateButton.clicked.connect(self.generate)
        self.isometricButton.clicked.connect(self.make_isometric)

        self.floorColorButton.clicked.connect(self.color_picker)
        self.wallColorButton.clicked.connect(self.color_picker)
        self.maskFileDialogButton.clicked.connect(self.select_mask_file)

        self.isometricBackgroundButton.clicked.connect(self.color_picker)
    
    def connectMenuOptions(self):
        self.actionAssetLocation.triggered.connect(self.set_file_locations)
        self.actionSaveLocation.triggered.connect(self.set_file_locations)

    def connectMazeTabs(self):
        self.mazeStyleTab.currentChanged.connect(self.tabChanged)


    def generate(self):
        sender = self.sender()
        # print(dir(self.typeComboBox))
        maze_width = self.widthSpinBox.value()
        # print(maze_width)
        maze_height = self.heightSpinBox.value()
        maze_type = self.typeComboBox.currentText()
        # orietation = self.orientationComboBox.currentText()
        with_loop = self.loopCheckBox.isChecked()
        number_of_maze =self.numberOfMazeSpinBox.value()
        # print(maze_width, maze_height, 20, with_loop)

        if self.currentStyleTab == "Style1":
            print("Reached style1")
            with_curve = False
            if maze_type.lower() == 'curved':
                with_curve = True

            grid = self.maze.render_maze(maze_width, maze_height, density=50, with_loop=with_loop, with_curve=with_curve)
            self.currently_rendered_file = grid
            # print('grid')
            # print(grid)
            self.sceneViewer1.load(grid)
            self.sceneViewer1.show()
        
        if self.currentStyleTab == "Style2":

            print("Reached style2")

            grid = self.maze.render_maze(maze_width, maze_height, cell_size = 1)
            self.currently_rendered_file = grid
            # print('grid')
            # print(grid)
            self.sceneViewer2.load(grid)
            self.sceneViewer2.show()

        if self.currentStyleTab == "Style3":

            print("wall color: ", self.wall_color)

            grid = self.maze.render_maze(maze_width, maze_height, wall_color = self.wall_color, floor_color = self.floor_color, braided = with_loop)
            self.currently_rendered_file = grid
            print('grid')
            print(grid)
            # self.sceneViewer.setPixmap( QtGui.QPixmap(grid))

            self.image = QtGui.QPixmap()
            self.image.load(grid)
            self.image = self.image.scaled(self.style3Tab.width()-20, self.style3Tab.height()-20)
            self.scene3.addPixmap(self.image)
            self.sceneViewer3.setScene(self.scene3)
            self.sceneViewer3.show()
            # self.sceneViewer.render()

        if self.currentStyleTab == "Style4":
            grid = self.maze.render_maze(maze_width, maze_height, mask=self.mask_file)
            self.currently_rendered_file = grid

            print('grid')
            print(grid)

            self.image = QtGui.QPixmap()
            self.image.load(grid)
            self.image = self.image.scaled(self.style4Tab.width()-20, self.style4Tab.height()-20)
            self.scene4.addPixmap(self.image)
            self.sceneViewer4.setScene(self.scene4)
            self.sceneViewer4.show()
            # self.sceneViewer.render()

        if self.currentStyleTab == "Style5":
            print("Reached style5")
            grid = self.maze.render_maze(maze_width, maze_height, mask=self.mask_file)
            self.currently_rendered_file = grid
            print('grid')
            print(grid)
            self.sceneViewer5.load(grid)
            self.sceneViewer5.show()

        if self.currentStyleTab == "Manual":
            grid = self.maze.render_maze(maze_width, maze_height, designed_assets_folder=self.asset_folder)
            self.currently_rendered_file = grid

            print('grid')
            print(grid)

            self.image = QtGui.QPixmap()
            self.image.load(grid)
            self.image = self.image.scaled(self.manualTab.width()-20, self.manualTab.height()-20)
            self.sceneManual.addPixmap(self.image)
            self.sceneViewerManual.setScene(self.sceneManual)
            self.sceneViewerManual.show()
            # self.sceneViewer.render()

    def set_file_locations(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        sender = self.sender()

        if sender.text() == 'Save Location':
            self.destination_folder = file
        elif sender.text() == 'Asset Location':
            self.asset_folder = file

    def select_mask_file(self):
        dialog = QFileDialog()
        # file = str(QFileDialog.getExistingDirectory(self, "Select The Mask File"))
        sender = self.sender()

        # dialog.setFileMode(QFileDialog.AnyFile)

        file = dialog.getOpenFileName(self, "Select The Mask File")
        self.mask_file = file[0]
        self.maskFileEdit.setText(file[0])

    def solve(self):
        filetime = datetime.now().strftime("%Y%m%d-%H%M%S")

        dst_path = self.destination_folder + '/{}'.format(self.maze_style_name)

        file_solution = self.currently_rendered_file[:-4] + "_solution" + self.currently_rendered_file[-4:]
        dst_solution = dst_path + '/maze_solution-{}.{}'.format(filetime, self.tab_image_ext)

        print(file_solution)

        if self.currentStyleTab == "Style1":
            grid = file_solution
            self.sceneViewer1.load(grid)
            self.sceneViewer1.show()
        
        if self.currentStyleTab == "Style2":

            print("Reached style2")

            grid = file_solution
            # print('grid')
            # print(grid)
            self.sceneViewer2.load(grid)
            self.sceneViewer2.show()

        if self.currentStyleTab == "Style3":
            grid = file_solution

            self.image = QtGui.QPixmap()
            self.image.load(grid)
            self.image = self.image.scaled(self.style3Tab.width()-20, self.style3Tab.height()-20)
            self.scene3.addPixmap(self.image)
            self.sceneViewer3.setScene(self.scene3)
            self.sceneViewer3.show()
            # self.sceneViewer.render()

        if self.currentStyleTab == "Style4":
            grid = file_solution

            self.image = QtGui.QPixmap()
            self.image.load(grid)
            self.image = self.image.scaled(self.style4Tab.width()-20, self.style4Tab.height()-20)
            self.scene4.addPixmap(self.image)
            self.sceneViewer4.setScene(self.scene4)
            self.sceneViewer4.show()
            # self.sceneViewer.render()

        if self.currentStyleTab == "Style5":
            grid = file_solution

            self.sceneViewer5.load(grid)
            self.sceneViewer5.show()

        if self.currentStyleTab == "Manual":

            grid = file_solution

            self.image = QtGui.QPixmap()
            self.image.load(grid)
            self.image = self.image.scaled(self.manualTab.width()-20, self.manualTab.height()-20)
            self.sceneManual.addPixmap(self.image)
            self.sceneViewerManual.setScene(self.sceneManual)
            self.sceneViewerManual.show()
            # self.sceneViewer.render()
    
    def save(self):
        filetime = datetime.now().strftime("%Y%m%d-%H%M%S")

        dst_path = self.destination_folder + '/{}'.format(self.maze_style_name)
        os.makedirs(dst_path, exist_ok=True)  # succeeds even if directory exists.
        dst = dst_path + '/maze-{}.{}'.format(filetime, self.tab_image_ext)
        shutil.copy2(self.currently_rendered_file, dst)

        file_solution = self.currently_rendered_file[:-4] + "_solution" + self.currently_rendered_file[-4:]
        dst_solution = dst_path + '/maze_solution-{}.{}'.format(filetime, self.tab_image_ext)
        shutil.copy2(file_solution, dst_solution)

    def make_isometric(self):
        print(self.currently_rendered_file)

        grid = ismoetric.get_isometric(self.currently_rendered_file, self.isometric_background_color)

        if grid is not None:
            self.currently_rendered_file = grid

        self.image = QtGui.QPixmap()
        self.image.load(grid)
        self.image = self.image.scaled(self.manualTab.width()-20, self.manualTab.height()-20)
        self.sceneManual.addPixmap(self.image)
        self.sceneViewerManual.setScene(self.sceneManual)
        self.sceneViewerManual.show()

    def tabChanged(self):
        sender = self.sender()
        print(sender.tabText(sender.currentIndex()))

        tab = sender.tabText(sender.currentIndex())
        self.currentStyleTab = tab
        if tab == "Style1":
            self.maze = WeaveMazeGenerator()
            self.maze_style_name = 'weave'
            self.tab_image_ext = 'svg'
            self.with_solution = True

            # self.sceneViewer1 = QtSvgWidgets.QSvgWidget()
            # self.sceneViewer.setGeometry(QtCore.QRect(0,0,800,800))
            # self.sceneViewer.setParent(self.style1Tab)

            # self.layout = QVBoxLayout(self.style1Tab)
            # self.layout.addWidget(self.sceneViewer)
            
        elif tab == "Style2":
            self.maze = MazeManager()
            self.maze_style_name = 'pymaze'
            self.tab_image_ext = 'svg'
            self.with_solution = False

            # self.sceneViewer = QtSvgWidgets.QSvgWidget()
            # self.sceneViewer.setGeometry(QtCore.QRect(0,0,800,800))
            # self.sceneViewer.setParent(self.style2Tab)

            # self.layout = QVBoxLayout(self.style2Tab)
            # self.layout.addWidget(self.sceneViewer)
        elif tab == "Style3":
            self.maze = ColorMaze()
            self.maze_style_name = 'colormaze'
            self.tab_image_ext = 'png'
            self.with_solution = False

        elif tab == "Style4":
            self.maze = MazeMaker()
            self.maze_style_name = 'mazemaker'
            self.tab_image_ext = 'png'
            self.with_solution = False

        elif tab == "Style5":
            self.maze = MaskedMazeGenerator()
            self.maze_style_name = 'masgedmaze'
            self.tab_image_ext = 'svg'

        elif tab == "Manual":
            self.maze = ManualMazeGenerator()
            self.maze_style_name = 'manualmazegen'
            self.tab_image_ext = 'png'
            self.with_solution = False


            # self.sceneViewer = QtWidgets.QGraphicsView(self.style3Tab)
            # self.scene = QtWidgets.QGraphicsScene()

            # self.layout = QVBoxLayout(self.style3Tab)
            # self.layout.addWidget(self.sceneViewer)
            # self.sceneViewer.setScene(self.scene)
            
            # self.sceneViewer.move(0,0)
            

            # self.sceneViewer = QtWidgets.QGraphicsScene(self)
            # self.sceneViewer.setSceneRect(QtCore.QRectF(0,0,800,800))
            # self.sceneViewer.setParent(self.style2Tab)
            # self.sceneViewer.addPixmap()
            
            # print(dir(QtGui.QPixmap))

            # print(self.style3Tab.height(), self.style3Tab.width())
        self.hide_and_show_butons(tab)

        
        
    
    def connectEdits(self):
        # self.widthSpinBox.
        self.widthSpinBox.valueChanged.connect(self.setValue)
        self.heightSpinBox.valueChanged.connect(self.setValue)
        # self.orientationComboBox.currentTextChanged.connect(self.setValue)
        self.numberOfMazeSpinBox.valueChanged.connect(self.setValue)
        # print(dir(self.typeComboBox))
        self.typeComboBox.addItems(["Straight", "Curved"])
        self.typeComboBox.currentIndexChanged.connect(self.setValue)

    def color_picker(self):
        sender = self.sender()
        print(sender.style())
        color = QtWidgets.QColorDialog.getColor()
        print('color')
        print(sender.text())
        if sender.text() == "Wall Color":
            self.wall_color = color.getRgb()[0:3]
            # print(self.wall_color)
        elif sender.text() == "Floor Color":
            self.floor_color = color.getRgb()[0:3]
        elif sender.text() == "Isometric Background":
            self.isometric_backgrounf_color = color.getRgb()[0:3]
        # print(color.getRgb()[0:3])
        sender.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def setValue(self):
        sender = self.sender()

        self.saveButton.clicked.connect(self.save)
        self.solveButton.clicked.connect(self.solve)
        self.generateButton.clicked.connect(self.generate)
        self.isometricButton.clicked.connect(self.make_isometric)

        self.floorColorButton.clicked.connect(self.color_picker)
        self.wallColorButton.clicked.connect(self.color_picker)
        self.maskFileDialogButton.clicked.connect(self.select_mask_file)

        self.isometricBackgroundButton.clicked.connect(self.color_picker)
    
    def hide_and_show_butons(self, style):
        if style == "Style1":
            self.loopCheckBox.setEnabled(True)
            self.typeComboBox.setEnabled(True)
            self.isometricBackgroundButton.setEnabled(False)
            self.wallColorButton.setEnabled(False)
            self.floorColorButton.setEnabled(False)
            self.maskFileDialogButton.setEnabled(False)
            
            self.isometricButton.setVisible(False)
            
        elif style == "Style2":
            self.loopCheckBox.setEnabled(False)
            self.typeComboBox.setEnabled(False)
            self.isometricBackgroundButton.setEnabled(False)
            self.wallColorButton.setEnabled(False)
            self.floorColorButton.setEnabled(False)
            self.maskFileDialogButton.setEnabled(False)
            

            self.isometricButton.setVisible(False)

        elif style == "Style3":
            self.loopCheckBox.setEnabled(False)
            self.typeComboBox.setEnabled(False)
            self.isometricBackgroundButton.setEnabled(False)
            self.wallColorButton.setEnabled(True)
            self.floorColorButton.setEnabled(True)
            self.maskFileDialogButton.setEnabled(False)
            

            self.isometricButton.setVisible(False)

        elif style == "Style4":
            self.loopCheckBox.setEnabled(False)
            self.typeComboBox.setEnabled(False)
            self.isometricBackgroundButton.setEnabled(False)
            self.wallColorButton.setEnabled(False)
            self.floorColorButton.setEnabled(False)
            self.maskFileDialogButton.setEnabled(True)
            

            self.isometricButton.setVisible(False)

        elif style == "Style5":
            self.loopCheckBox.setEnabled(False)
            self.typeComboBox.setEnabled(False)
            self.isometricBackgroundButton.setEnabled(False)
            self.wallColorButton.setEnabled(False)
            self.floorColorButton.setEnabled(False)
            self.maskFileDialogButton.setEnabled(True)
            

            self.isometricButton.setVisible(False)

        elif style == "Manual":
            self.loopCheckBox.setEnabled(True)
            self.typeComboBox.setEnabled(True)
            self.isometricBackgroundButton.setEnabled(True)
            self.wallColorButton.setEnabled(False)
            self.floorColorButton.setEnabled(False)
            self.maskFileDialogButton.setEnabled(False)
            

            self.isometricButton.setVisible(True)




        


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()