import argparse
import enum
import itertools
import os
from select import select
import sys
from collections import namedtuple
from random import choice, seed
import matplotlib.pyplot as plt

import numpy as np
from PIL import Image, ImageDraw


class Stack:
    def __init__(self):
        self._list = []

    def push(self, value):
        self._list.append(value)

    def pop(self):
        return self._list.pop()

    def __len__(self):
        return len(self._list)


class Direction(enum.IntEnum):
    N = 0
    E = 1
    S = 2
    W = 3


class Mapping:
    direction_to_step = {Direction.N: (0, -1),
                         Direction.E: (1, 0),
                         Direction.S: (0, 1),
                         Direction.W: (-1, 0)}

    step_to_direction = {value: key for key, value in direction_to_step.items()}


class CellIndex(namedtuple("Cell", ("x", "y"))):
    def __add__(self, other):
        return CellIndex(x=self.x + other[0], y=self.y + other[1])

    def __sub__(self, other):
        return self.x - other.x, self.y - other.y


class Cell:
    def __init__(self):
        self.visited = False
        self.walls = [True]*4

    def remove_wall(self, direction):
        self.walls[direction.value] = False

    def __repr__(self):
        return f"Cell({self.walls}, visited={self.visited})"


class MazeMaker:
    def __init__(self, width=10, height=10, mask=None):
        """
        :param width: Number of cells in horizontal direction
        :param height: Number of cells in vertical direction
        :param mask: Bool array where False marks cells that are not visited by the algorithm
        """
        self.width = int(width)
        self.height = int(height)
        self.cell_grid = np.array([Cell() for _ in range(height * width)]).reshape((height, width))
        self.mask = mask

        self.maze = None

        os.makedirs("assets/temp_mazemaker/", exist_ok=True)  # succeeds even if directory exists.
        os.makedirs("assets/mazemaker/", exist_ok=True)  # succeeds even if directory exists.
        self.temp_folder_name = "assets/temp_mazemaker/"
        self.save_folder_name = "assets/mazemaker/"

    def get_neighbour_cell_indices(self, cell_index):
        """
        Return the indices of all neighbour cells of cell_index that lie within the grid
        """
        stencil = ((0, 1), (0, -1), (1, 0), (-1, 0))
        neighbour_cell_indices = [cell_index + diff for diff in stencil]
        neighbour_cell_indices = [cell_index for cell_index in neighbour_cell_indices if self.index_in_grid(cell_index)]
        return neighbour_cell_indices

    def index_in_grid(self, cell_index):
        return 0 <= cell_index.x < self.width and 0 <= cell_index.y < self.height

    def get_unvisited_neighbours(self, cell_index):
        neighbour_cell_indices = self.get_neighbour_cell_indices(cell_index)
        unvisited_cells = [index for index in neighbour_cell_indices if self.get_cell(index).visited is False]
        # TODO inherit from Maze to implement masked maze and override this function
        unvisited_cells = [index for index in unvisited_cells if self.get_mask(index) == True]
        return unvisited_cells

    def set_visited(self, cell_index):
        self.get_cell(cell_index).visited = True

    def remove_walls(self, start_cell_index, end_cell_index):
        direction_to = Mapping.step_to_direction[end_cell_index - start_cell_index]
        direction_from = Mapping.step_to_direction[start_cell_index - end_cell_index]
        self.get_cell(start_cell_index).remove_wall(direction_to)
        self.get_cell(end_cell_index).remove_wall(direction_from)

    def move(self, start_cell_index, end_cell_index):
        self.set_visited(end_cell_index)
        self.remove_walls(start_cell_index, end_cell_index)

    def get_cell(self, cell_index):
        return self.cell_grid[cell_index.y, cell_index.x]

    def get_mask(self, cell_index):
        """Return the mask value at cell_index """
        if self.mask is not None:
            return self.mask[cell_index.y, cell_index.x]
        # return True (allowed cell) if no mask was set
        else:
            return True

    def set_cell_props(self, width, height, mask):
        self.width = int(width)
        self.height = int(height)
        self.cell_grid = np.array([Cell() for _ in range(height * width)]).reshape((height, width))
        self.mask = mask

    def generate_maze(self, width, height, output_filename, cell_size_pixels=5, line_width_pixels=1, start_cell_index=None, mask=None):
        self.set_cell_props(width, height, mask)

        stack = Stack()
        current_cell_index = start_cell_index
        self.set_visited(current_cell_index)
        while True:
            # print("reached")
            unvisited_cells = self.get_unvisited_neighbours(current_cell_index)
            # if the current cell has any neighbours which have not been visited
            if len(unvisited_cells) > 0:
                # choose one random unvisited neighbour and travel there
                chosen_cell_index = choice(unvisited_cells)
                stack.push(current_cell_index)
                self.move(current_cell_index, chosen_cell_index)
                current_cell_index = chosen_cell_index
            elif len(stack) > 0:
                # if all neighbours have been visited backtrack to the previous cell
                current_cell_index = stack.pop()
            else:
                break
        plotter = MazeVisualizerPIL(self, cell_size_pixels, line_width_pixels)
        plotter.plot_walls()
        plotter.save_plot(output_filename)

        

        return output_filename

    def render_maze(self, width, height, **kwargs):
        if 'output_filename' in kwargs:
            output_filename = kwargs['output_filename']
        else:
            output_filename = self.temp_folder_name + 'temp_generate.png'
        if 'mask' in kwargs:
            mask = kwargs['mask']
            try:
                img = Image.open(mask)
            except IOError:
                sys.exit(f"Can't open mask image {mask}.")
            mask = np.asarray(img, dtype=bool)
            # arguments["mask"] = mask
            width = img.size[0]
            height = img.size[1]

            start_cell_index = CellIndex(width // 2 , height // 2 )
        if 'multiple' in kwargs:
            multiple = kwargs['multiple']
            maze_number = kwargs['maze_number']
            output_filename = self.save_folder_name + 'maze-{}.png'.format(maze_number)
        else:
            multiple = False
        
        if 'cell_size_pixels' in kwargs:
            cell_size_pixels = kwargs['cell_size_pixels']
        else:
            cell_size_pixels = 10

        line_width_pixels = int(cell_size_pixels / 5)


        generate_result =  self.generate_maze(width, height, output_filename, cell_size_pixels=cell_size_pixels, line_width_pixels=line_width_pixels, start_cell_index = start_cell_index, mask = mask)
        
        
        
        return generate_result

class MazeVisualizerPIL:
    def __init__(self, maze, cell_size_pixels, line_width_pixels):
        self.maze = maze
        self.cell_size_pixels = cell_size_pixels
        self._init_plot()
        self.fill_color = 0
        self.line_width = line_width_pixels

    def _init_plot(self):
        width = self.maze.width*self.cell_size_pixels+1
        height = self.maze.height*self.cell_size_pixels+1
        self.img = Image.new(mode="L", size=(width, height), color=255)
        self.draw = ImageDraw.Draw(self.img)

    def plot_walls(self):
        for hor_index, ver_index in itertools.product(range(self.maze.width), range(self.maze.height)):
            top_left_pixel = (hor_index*self.cell_size_pixels, ver_index*self.cell_size_pixels)
            top_right_pixel = ((hor_index+1)*self.cell_size_pixels, ver_index*self.cell_size_pixels)
            bottom_left_pixel = (hor_index*self.cell_size_pixels, (ver_index+1)*self.cell_size_pixels)
            bottom_right_pixel = ((hor_index+1)*self.cell_size_pixels, (ver_index+1)*self.cell_size_pixels)
            if not self.maze.get_mask(CellIndex(x=hor_index, y=ver_index)):
                self.draw.rectangle((top_left_pixel, bottom_right_pixel), outline=self.fill_color, fill=self.fill_color)
            cell = self.maze.get_cell(CellIndex(x=hor_index, y=ver_index))
            if cell.visited is True:
                if cell.walls[Direction.N]:
                    self.draw.line((top_left_pixel, top_right_pixel), self.fill_color, self.line_width)
                if cell.walls[Direction.E]:
                    self.draw.line((top_right_pixel, bottom_right_pixel), self.fill_color, self.line_width)
                if cell.walls[Direction.S]:
                    self.draw.line((bottom_right_pixel, bottom_left_pixel), self.fill_color, self.line_width)
                if cell.walls[Direction.W]:
                    self.draw.line((top_left_pixel, bottom_left_pixel), self.fill_color, self.line_width)


    def save_plot(self, filename):
        self.img.save(filename)


