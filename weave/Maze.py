# from Exception import NotImplmentedError

from distutils.log import error


class Maze:
    def __init__(self, width = 10, height = 10, type = "straight", numberOfMaze = 1):
        self.width = width
        self.height = height
        self.type = type
        self.numberOfMaze = numberOfMaze

    def createMaze(self):
        raise error

    def render_maze(self):
        raise error
