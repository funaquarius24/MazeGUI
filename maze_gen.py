#!/usr/bin/env python
from PIL import Image, ImageDraw
from time import perf_counter
import random
import os
import glob
import imageio
import shutil


class Cell:
    """Create grid cell."""
    def __init__(self, row_index, column_index, rows, columns):
        """
        Initiate grid cell.
        row_index: cell row index.
        column_index: cell column index.
        rows: number of rows in grid.
        columns: number of columns in grid.
        """
        if row_index >= rows or row_index < 0:
            raise ValueError(f'Expected a row index in range(0, {rows}) exclusive, got {row_index}')
        if column_index >= columns or column_index < 0:
            raise ValueError(f'Expected a column index in range(0, {columns} exclusive, got {column_index}')
        self.row = row_index
        self.column = column_index
        self.rows = rows
        self.columns = columns
        self.linked_cells = []

    def neighbors(self, grid):
        """Return North, South, East, West neighbor cells."""
        neighbors = []
        north = self.row - 1, self.column
        if north[0] < 0:
            north = 0
            neighbors.append(0)
        if north:
            neighbors.append(grid[north[0]][north[1]])
        south = self.row + 1, self.column
        if south[0] >= self.rows:
            south = 0
            neighbors.append(0)
        if south:
            neighbors.append(grid[south[0]][south[1]])
        east = self.row, self.column + 1
        if east[1] >= self.columns:
            east = 0
            neighbors.append(0)
        if east:
            neighbors.append(grid[east[0]][east[1]])
        west = self.row, self.column - 1
        if west[1] < 0:
            west = 0
            neighbors.append(0)
        if west:
            neighbors.append(grid[west[0]][west[1]])
        return neighbors

    def link(self, other, grid):
        """Link 2 unconnected cells."""
        if self in other.linked_cells or other in self.linked_cells:
            raise ValueError(f'{self} and {other} are already connected.')
        if self.columns != other.columns or self.rows != other.rows:
            raise ValueError('Cannot connect cells in different grids.')
        if self not in other.neighbors(grid) or other not in self.neighbors(grid):
            raise ValueError(f'{self} and {other} are not neighbors and cannot be connected.')
        if not isinstance(other, Cell):
            raise TypeError(f'Cannot link Cell to {type(other)}.')
        self.linked_cells.append(other)
        other.linked_cells.append(self)

    def unlink(self, other):
        """Unlink 2 connected cells."""
        if self not in other.linked_cells or other not in self.linked_cells:
            raise ValueError(f'{self} and {other} are not connected.')
        self.linked_cells.remove(other)
        other.linked_cells.remove(self)

    def coordinates(self):
        """Return cell (row, column)."""
        return self.row, self.column

    def is_linked(self, other):
        """Return True if 2 cells are linked."""
        return other in self.linked_cells

    def __str__(self):
        """Cell display."""
        return f'Cell{self.coordinates()}'

    def __repr__(self):
        """Cell representation."""
        return f'Cell{self.coordinates()}'


class Maze:
    """
    Generate a maze using different algorithms:
    - Binary Tree Algorithm.
    - Sidewinder Algorithm.
    - Aldous-Broder Algorithm.
    - Wilson Algorithm.
    - Hunt And Kill Algorithm.
    - Recursive Backtracker Algorithm.
    """
    def __init__(self, rows, columns, width, height, line_width=5, line_color='black', background_color='white'):
        """
        Initiate maze variables:
        rows: number of rows in initial grid.
        columns: number of columns in initial grid.
        width: width of the frame(s).
        height: height of the frame(s).
        line_width: width of grid/maze lines.
        line_color: color of grid/maze lines.
        background_color: color of the grid/maze background (cells/path)
        """
        if width % columns != 0:
            raise ValueError(f'Width: {width} not divisible by number of columns: {columns}.')
        if height % rows != 0:
            raise ValueError(f'Height: {height} not divisible by number of {rows}.')
        self.rows = rows
        self.columns = columns
        self.width = width
        self.height = height
        self.line_width = line_width
        self.line_color = line_color
        self.background_color = background_color
        self.cell_width = width // columns
        self.cell_height = height // rows
        self.drawing_constant = line_width // 2
        self.path = '/Users/emadboctor/Desktop/New code folder September 7 2019/Mazes for programmers/Maze test/'
        # self.path = input('Enter path to folder to save maze creation GIF: ').rstrip()
        self.configurations = {
            'b': self._binary_tree_configuration(),
            's': self._side_winder_configuration(),
            'ab': self._aldous_broder_configuration(),
            'w': self._wilson_configuration(),
            'hk': self._hunt_and_kill_configuration(),
            'rb': self._recursive_back_tracker_configuration()
        }
        self.algorithm_names = {'b': 'BINARY TREE', 's': 'SIDEWINDER', 'ab': 'ALDOUS BRODER', 'w': 'WILSON',
                                'hk': 'HUNT AND KILL', 'rb': 'RECURSIVE BACKTRACKER'}

    def _make_grid_image(self):
        """Initiate maze initial grid image."""
        grid = Image.new('RGB', (self.width, self.height), self.background_color)
        for x in range(0, self.width, self.cell_width):
            x0, y0, x1, y1 = x, 0, x, self.height
            column = (x0, y0), (x1, y1)
            ImageDraw.Draw(grid).line(column, self.line_color, self.line_width)
        for y in range(0, self.height, self.cell_height):
            x0, y0, x1, y1 = 0, y, self.width, y
            row = (x0, y0), (x1, y1)
            ImageDraw.Draw(grid).line(row, self.line_color, self.line_width)
        x_end = (0, self.height - self.drawing_constant),\
                (self.width - self.drawing_constant, self.height - self.drawing_constant)
        y_end = (self.width - self.drawing_constant, 0), (self.width - self.drawing_constant, self.height)
        ImageDraw.Draw(grid).line(x_end, self.line_color, self.line_width)
        ImageDraw.Draw(grid).line(y_end, self.line_color, self.line_width)
        return grid

    def _create_maze_cells(self):
        """Return maze cells."""
        return [[Cell(row, column, self.rows, self.columns) for column in range(self.columns)]
                for row in range(self.rows)]

    def _get_dead_ends(self, maze):
        """
        maze: A 2D list containing finished maze configuration.
        Return dead end cells in current maze configuration.
        """
        return {cell for row in maze for cell in row if len(cell.linked_cells) == 1 and
                str(cell) != str(maze[-1][-1])}

    def _binary_tree_configuration(self):
        """Return binary tree maze configuration."""
        maze_cells = self._create_maze_cells()
        modified_cells = []
        for row in range(self.rows):
            for column in range(self.columns):
                current_cell = maze_cells[row][column]
                north, south, east, west = current_cell.neighbors(maze_cells)
                to_link = random.choice('nw')
                if not north and not west:
                    continue
                if to_link == 'n' and north:
                    current_cell.link(north, maze_cells)
                    modified_cells.append((current_cell, north))
                if to_link == 'w' and west:
                    current_cell.link(west, maze_cells)
                    modified_cells.append((current_cell, west))
                if to_link == 'n' and not north:
                    current_cell.link(west, maze_cells)
                    modified_cells.append((current_cell, west))
                if to_link == 'w' and not west:
                    current_cell.link(north, maze_cells)
                    modified_cells.append((current_cell, north))
        dead_ends = self._get_dead_ends(maze_cells)
        return modified_cells, dead_ends

    def _side_winder_configuration(self):
        """Return sidewinder algorithm maze configuration."""
        maze_cells = self._create_maze_cells()
        checked_cells = []
        modified_cells = []
        for row in range(self.rows):
            for column in range(self.columns):
                current_cell = maze_cells[row][column]
                north, south, east, west = current_cell.neighbors(maze_cells)
                if row == 0 and east:
                    east_cell = maze_cells[row][column + 1]
                    current_cell.link(east_cell, maze_cells)
                    modified_cells.append((current_cell, east_cell))
                if row != 0:
                    checked_cells.append(current_cell)
                    to_link = random.choice('ne')
                    if to_link == 'e' and east:
                        east_cell = maze_cells[row][column + 1]
                        current_cell.link(east_cell, maze_cells)
                        modified_cells.append((current_cell, east_cell))
                    if to_link == 'n' or (to_link == 'e' and not east):
                        random_cell = random.choice(checked_cells)
                        checked_cells.clear()
                        random_cell_coordinates = random_cell.coordinates()
                        random_cell_north_neighbor = maze_cells[random_cell_coordinates[0] - 1][
                            random_cell_coordinates[1]]
                        random_cell.link(random_cell_north_neighbor, maze_cells)
                        modified_cells.append((random_cell, random_cell_north_neighbor))
        dead_ends = self._get_dead_ends(maze_cells)
        return modified_cells, dead_ends

    def _aldous_broder_configuration(self):
        """Return Aldous Broder algorithm maze configuration."""
        maze_cells = self._create_maze_cells()
        modified_cells = []
        starting_cell = maze_cells[random.choice(range(self.rows))][random.choice(range(self.columns))]
        visited = set()
        run = [starting_cell]
        while len(visited) < self.rows * self.columns:
            current_cell = run[-1]
            visited.add(current_cell)
            random_neighbor = random.choice([
             neighbor for neighbor in current_cell.neighbors(maze_cells) if neighbor])
            if random_neighbor not in visited:
                visited.add(random_neighbor)
                run.append(random_neighbor)
                current_cell.link(random_neighbor, maze_cells)
                modified_cells.append((current_cell, random_neighbor))
            if random_neighbor in visited:
                run.clear()
                run.append(random_neighbor)
        dead_ends = self._get_dead_ends(maze_cells)
        return modified_cells, dead_ends

    def _wilson_configuration(self):
        """Return Wilson algorithm maze configuration."""
        maze_cells = self._create_maze_cells()
        unvisited = {cell for row in maze_cells for cell in row}
        starting_cell = random.choice(list(unvisited))
        unvisited.remove(starting_cell)
        visited = {starting_cell}
        path = [random.choice(list(unvisited))]
        unvisited.remove(path[-1])
        modified_cells = []
        while unvisited:
            current_cell = path[-1]
            new_cell = random.choice([neighbor for neighbor in current_cell.neighbors(maze_cells) if neighbor])
            if new_cell in path and new_cell not in visited:
                to_erase_from = path.index(new_cell)
                del path[to_erase_from + 1:]
            if new_cell in visited:
                for cell in path:
                    visited.add(cell)
                    if cell in unvisited:
                        unvisited.remove(cell)
                path.append(new_cell)
                for index in range(len(path) - 1):
                    path[index].link(path[index + 1], maze_cells)
                    modified_cells.append((path[index], path[index + 1]))
                path.clear()
                if unvisited:
                    path.append(random.choice(list(unvisited)))
            if new_cell not in path and new_cell not in visited:
                path.append(new_cell)
        dead_ends = self._get_dead_ends(maze_cells)
        return modified_cells, dead_ends

    def _hunt_and_kill_configuration(self):
        """Return hunt and kill algorithm maze configuration."""
        maze_cells = self._create_maze_cells()
        unvisited = [cell for row in maze_cells for cell in row]
        starting_cell = random.choice(list(unvisited))
        visited = [starting_cell]
        unvisited.remove(starting_cell)
        run = [starting_cell]
        modified_cells = []
        while unvisited:
            current_cell = run[-1]
            valid_neighbors = [neighbor for neighbor in current_cell.neighbors(maze_cells) if neighbor in unvisited]
            if valid_neighbors:
                next_cell = random.choice(valid_neighbors)
                current_cell.link(next_cell, maze_cells)
                modified_cells.append((current_cell, next_cell))
                visited.append(next_cell)
                unvisited.remove(next_cell)
                run.append(next_cell)
            if not valid_neighbors:
                for cell in unvisited:
                    valid_neighbors = [neighbor for neighbor in cell.neighbors(maze_cells) if neighbor in visited]
                    if valid_neighbors:
                        choice = random.choice(valid_neighbors)
                        cell.link(choice, maze_cells)
                        modified_cells.append((cell, choice))
                        unvisited.remove(cell)
                        visited.append(cell)
                        run.append(cell)
                        break
        dead_ends = self._get_dead_ends(maze_cells)
        return modified_cells, dead_ends

    def _recursive_back_tracker_configuration(self):
        """Return recursive backtracker maze configuration."""
        maze_cells = self._create_maze_cells()
        unvisited = [cell for row in maze_cells for cell in row]
        starting_cell = random.choice(unvisited)
        unvisited.remove(starting_cell)
        run = [starting_cell]
        modified = []
        while run:
            current_cell = run[-1]
            valid_neighbors = [neighbor for neighbor in current_cell.neighbors(maze_cells) if neighbor in unvisited]
            if valid_neighbors:
                next_cell = random.choice(valid_neighbors)
                current_cell.link(next_cell, maze_cells)
                modified.append((current_cell, next_cell))
                unvisited.remove(next_cell)
                run.append(next_cell)
            if not valid_neighbors:
                run.pop()
        dead_ends = self._get_dead_ends(maze_cells)
        return modified, dead_ends

    def produce_maze_image(self, configuration):
        """
        configuration: a string representing the algorithm:
        'b': Binary Tree Algorithm.
        's': Sidewinder Algorithm.
        'ab': Aldous Broder Algorithm.
        'w': Wilson Algorithm.
        'hk': Hunt And Kill Algorithm.
        'rb': Recursive Backtracker Algorithm.
        Return maze image according to specified configuration.
        """
        if configuration not in self.configurations:
            raise ValueError(f'Invalid configuration {configuration}')
        cells, dead_ends = self.configurations[configuration]
        maze = self._make_grid_image()
        linked_cells = {cell.coordinates(): [linked.coordinates() for linked in cell.linked_cells]
                        for row in cells for cell in row}
        for row in range(self.rows):
            for column in range(self.columns):
                current_cell_coordinates = (row, column)
                if (row, column + 1) in linked_cells[current_cell_coordinates]:
                    x0 = (column + 1) * self.cell_width
                    y0 = (row * self.cell_height) + (self.line_width - 2)
                    x1 = x0
                    y1 = y0 + self.cell_height - (self.line_width + 1)
                    wall = (x0, y0), (x1, y1)
                    ImageDraw.Draw(maze).line(wall, self.background_color, self.line_width)
                if (row + 1, column) in linked_cells[current_cell_coordinates]:
                    x0 = column * self.cell_width + self.line_width - 2
                    y0 = (row + 1) * self.cell_height
                    x1 = x0 + self.cell_width - (self.line_width + 1)
                    y1 = y0
                    wall = (x0, y0), (x1, y1)
                    ImageDraw.Draw(maze).line(wall, self.background_color, self.line_width)
        x_end = (0, self.height - self.drawing_constant),\
                (self.width - self.drawing_constant, self.height - self.drawing_constant)
        y_end = (self.width - self.drawing_constant, 0), (self.width - self.drawing_constant, self.height)
        ImageDraw.Draw(maze).line(x_end, self.line_color, self.line_width)
        ImageDraw.Draw(maze).line(y_end, self.line_color, self.line_width)
        number_of_dead_ends = len(dead_ends)
        total_cells = self.rows * self.columns
        dead_end_percentage = 100 * (number_of_dead_ends / total_cells)
        print(f'{round(dead_end_percentage, 2)}% dead ends: {number_of_dead_ends} out of {total_cells} cells.')
        return maze

    def produce_maze_visualization(self, frame_speed, configuration):
        """
        ** NOTE: Works on Unix systems only.
        Create a GIF for maze being created by respective specified configuration.
        frame_speed: speed in ms.
        configuration: a string representing the algorithm:
        'b': Binary Tree Algorithm.
        's': Sidewinder Algorithm.
        'ab': Aldous Broder Algorithm.
        'w': Wilson Algorithm.
        'hk': Hunt And Kill Algorithm.
        'rb': Recursive Backtracker Algorithm.
        """
        if configuration not in self.configurations:
            raise ValueError(f'Invalid configuration {configuration}')
        print('GIF creation started ...')
        os.chdir(self.path)
        maze_image = self._make_grid_image()
        cells, dead_ends = self.configurations[configuration]
        count = 0
        for cell1, cell2 in cells:
            cell1_coordinates = cell1.coordinates()
            cell2_coordinates = cell2.coordinates()
            if cell1_coordinates[0] == cell2_coordinates[0]:
                column = min(cell1_coordinates[1], cell2_coordinates[1])
                x0 = (column + 1) * self.cell_width
                row = cell1_coordinates[0]
                y0 = (row * self.cell_height) + (self.line_width - 2)
                x1 = x0
                y1 = y0 + self.cell_height - (self.line_width + 1)
                wall = (x0, y0), (x1, y1)
                ImageDraw.Draw(maze_image).line(wall, self.background_color, self.line_width)
                y_end = (self.width - self.drawing_constant, 0), (self.width - self.drawing_constant, self.height)
                ImageDraw.Draw(maze_image).line(y_end, self.line_color, self.line_width)
                maze_image.save(self.path + str(count) + '.png', 'png')
                count += 1
            # Remove horizontal walls
            if cell1_coordinates[1] == cell2_coordinates[1]:
                column = cell1_coordinates[1]
                x0 = column * self.cell_width + self.line_width - 2
                row = min(cell1_coordinates[0], cell2_coordinates[0])
                y0 = (row + 1) * self.cell_height
                x1 = x0 + self.cell_width - (self.line_width + 1)
                y1 = y0
                wall = (x0, y0), (x1, y1)
                ImageDraw.Draw(maze_image).line(wall, self.background_color, self.line_width)
                x_end = (0, self.height - self.drawing_constant), \
                        (self.width - self.drawing_constant, self.height - self.drawing_constant)
                ImageDraw.Draw(maze_image).line(x_end, self.line_color, self.line_width)
                maze_image.save(self.path + str(count) + '.png', 'png')
                count += 1
        maze_name = ' '.join(
            [self.algorithm_names[configuration], str(self.rows), 'x', str(self.columns), self.background_color,
             'x', self.line_color, 'maze', str(random.randint(10 ** 6, 10 ** 8))]
        )
        os.mkdir(maze_name)
        for file in os.listdir(self.path):
            if file.endswith('.png'):
                shutil.move(file, maze_name)
        os.chdir(maze_name)
        frames = glob.glob('*.png')
        frames.sort(key=lambda x: int(x.split('.')[0]))
        frames = [imageio.imread(frame) for frame in frames]
        imageio.mimsave(self.path + str(maze_name) + '.gif', frames, 'GIF', duration=frame_speed)
        print(f'Creation of {self.algorithm_names[configuration]} {count} frames GIF successful.')
        number_of_dead_ends = len(dead_ends)
        total_cells = self.rows * self.columns
        dead_end_percentage = (number_of_dead_ends / total_cells) * 100
        print(f'{round(dead_end_percentage, 2)}% dead ends: {number_of_dead_ends} out of {total_cells} cells.')


if __name__ == '__main__':
    start_time = perf_counter()
    the_test1 = Maze(50, 100, 1000, 500)
    the_test1.produce_maze_image('rb').show()
    end_time = perf_counter()
    print(f'Time: {end_time - start_time} seconds.')