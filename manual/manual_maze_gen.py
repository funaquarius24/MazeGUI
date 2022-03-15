#!/usr/bin/env python
'''

Maze.

An implementation of a "weave" maze generator. Weave mazes are those
with passages that pass both over and under other passages. The
technique used in this program was described by Robin Houston,
and works by first decorating the blank grid with the over/under
crossings, and then using Kruskal's algorithm to fill out the rest
of the grid. (Kruskal's is very well-suited to this approach, since
it treats the cells as separate sets and joins them together.)

Please note: this program was oringally ported from
https://gist.github.com/856138

Usage:
  maze -h
  maze pdf FILENAME [-W WIDTH] [-H HEIGHT] [-p PAGE_SIZE] [-d DENSITY] [-S] [-L] [-O ORIENTATION] [-i MAZE_ID]
  maze text [-W WIDTH] [-H HEIGHT] [-p PAGE_SIZE] [-d DENSITY] [-L] [-i MAZE_ID]
  maze canvas [-W WIDTH] [-H HEIGHT] [-p PAGE_SIZE] [-d DENSITY] [-L] [-f FILENAME] [-i MAZE_ID]
  maze javascript [-W WIDTH] [-H HEIGHT] [-p PAGE_SIZE] [-d DENSITY]  [-L] [-f FILENAME] [-i MAZE_ID]
  maze svg [-W WIDTH] [-H HEIGHT] [-p PAGE_SIZE] [-d DENSITY] [-S] [-L] [-f FILENAME] [-i MAZE_ID]
  maze data [-W WIDTH] [-H HEIGHT] [-p PAGE_SIZE] [-d DENSITY] [-S] [-L] [-i MAZE_ID]

Options:
  -h, --help                    Show this help message and exit

  -W --width WIDTH              Number of cells wide [default: 21]
  -H --height HEIGHT            Number of cells high [default: 30]

  -d --density DENSITY          Density of under/overs [default: 50]

  -L                            Enable a loop

  -S                            Draw with straight lines instead of curves

  -p PAGE_SIZE                  Page size, (A4 or Letter) [default: A4]
  -O --orientation ORIENTATION  Orientation, P=portrait, L=landscape [default: P]

  -i --maze_id MAZE_ID          Text used to identify which maze otherwise a random maze will be generated

Examples:

maze pdf my_new_maze.pdf

'''

from ast import arg
import sys
import os
from time import sleep
import uuid
from random import randint, seed, shuffle
from venv import create

from weave.Maze import Maze
from renderers.svg import render

from docopt import docopt
from os import walk
import numpy as np


# constants to aid with describing the passage directions
N, S, E, W, U = 0x1, 0x2, 0x4, 0x8, 0x10
DX = {E: 1, W: -1, N: 0, S: 0}
DY = {E: 0, W: 0, N: -1, S: 1}
OPPOSITE = {E: W, W: E, N: S, S: N}


#

class ManualMazeGenerator():
    def __init__(self) -> None:
        Maze.__init__(self)
        self.path_exists = False
        os.makedirs("assets/temp_manual/", exist_ok=True)  # succeeds even if directory exists.
        self.designed_assets_folder = 'assets/test_templates/'
        self.temp_file_name = 'assets/temp_manual/temp.png'

    def create_maze(self, width, height, density, add_a_loop):
        # structures to hold the maze
        grid = [[0 for x in range(width)] for x in range(height)]
        sets = [[Tree() for x in range(width)] for y in range(height)]

        # build the list of edges
        edges = []
        for y in range(height):
            for x in range(width):
                if y > 0:
                    edges.append([x, y, N])
                if x > 0:
                    edges.append([x, y, W])

        shuffle(edges)

        # build the over/under locations
        for cy in range(height - 2):
            cy += 1
            for cx in range(width - 2):
                cx += 1

                if randint(0, 99) < density:
                    continue

                nx, ny = cx, cy - 1
                wx, wy = cx - 1, cy
                ex, ey = cx + 1, cy
                sx, sy = cx, cy + 1

                if (grid[cy][cx] != 0 or
                        sets[ny][nx].connected(sets[sy][sx]) or
                        sets[ey][ex].connected(sets[wy][wx])):
                    continue

                sets[ny][nx].connect(sets[sy][sx])
                sets[ey][ex].connect(sets[wy][wx])

                if randint(0, 1) == 0:
                    grid[cy][cx] = E | W | U
                else:
                    grid[cy][cx] = N | S | U

                grid[ny][nx] |= S
                grid[wy][wx] |= E
                grid[ey][ex] |= W
                grid[sy][sx] |= N

                edges[:] = [(x, y, d) for (x, y, d) in edges if not (
                        (x == cx and y == cy) or
                        (x == ex and y == ey and d == W) or
                        (x == sx and y == sy and d == N)
                )]

        # Kruskal's algorithm
        while edges:
            x, y, direction = edges.pop()
            nx, ny = x + DX[direction], y + DY[direction]

            set1, set2 = sets[y][x], sets[ny][nx]

            if not set1.connected(set2):
                set1.connect(set2)
                grid[y][x] |= direction
                grid[ny][nx] |= OPPOSITE[direction]

        # add in a loop, I just replace a under/over with a cross
        if add_a_loop:
            # find all the crossing, if any
            candiates = []
            for cy in range(height - 2):
                cy += 1
                for cx in range(width - 2):
                    cx += 1
                    if grid[cy][cx] in (U | N | S, U | E | W):
                        candiates.append((cy, cx))

            # change just one of them to a crossing, e.g. create a loop
            if len(candiates):
                shuffle(candiates)
                cy, cx = candiates[0]
                grid[cy][cx] = N | S | W | E

        return grid

    def get_moves(self, grid, coordinate, cell):
        # for a given position, return all the posible coordinate moves
        moves = []

        y = coordinate[1]
        x = coordinate[0]
        if cell & W == W:
            inc = -1
            # if the next cell is an under or over cell, jump over it
            while grid[y][x+inc] in (19, 28): # could be more than one in a row
                inc -= 1
            moves.append((inc, 0))
        if cell & E == E:
            inc = 1
            while grid[y][x+inc] in (19, 28):
                inc += 1
            moves.append((inc, 0))
        if cell & N == N:
            inc = -1
            while grid[y+inc][x] in (19, 28):
                inc -= 1
            moves.append((0, inc))
        if cell & S == S:
            inc = 1
            while grid[y+inc][x] in (19, 28):
                inc += 1
            moves.append((0, inc))
        return moves

    def search(self, grid, coordinate, sofar, depth):
        cell = grid[coordinate[1]][coordinate[0]]

        for move in self.get_moves(grid, coordinate, cell):
            new_coordinate = (coordinate[0] + move[0], coordinate[1] + move[1])

            # if are back to where we where, then are in a loop
            if new_coordinate in sofar:
                continue

            new_so_far = [s for s in sofar]
            new_so_far.append(new_coordinate)

            # are we at the end already?
            if new_coordinate[0] == len(grid[0])-1 and new_coordinate[1] == len(grid)-1:
                return new_so_far

            solution = self.search(grid, new_coordinate, new_so_far, depth + 1)
            if solution:
                return solution
    def find_solution(self, grid):
        sofar = self.search(self, grid, (0, 0),  [(0, 0)], 0)
        print('Solution ->', sofar)

    def maze(self, args):
        width = int(args['--width'])
        height = int(args['--height'])
        density = int(args['--density'])


        # allow the same maze to be generated
        maze_id = args.get('--maze_id', None)
        if maze_id is None:
            maze_id = uuid.uuid4()
        seed(f"{maze_id}")

        filename = args['FILENAME']

        add_a_loop = args['-L']

        if args['-p'] not in ('A4', 'a4', 'Letter', 'letter'):
            print('Page size can only be A4 or Letter')
            print("e.g.  -p A4")
            print("You had -p", args['-p'])
            exit(-1)

        use_A4 = True if args['-p'] == 'A4' else False

        dislay_to_screen = args['text']
        generate_canvas_js = args['canvas']
        generate_js = args['javascript']
        generate_svg = args['svg']
        generate_data = args['data']
        generate_pdf = args['pdf']

        if generate_data:
            filename = "maze.pdf"

        # render options
        render_options = {'filename': filename,
                        'draw_with_curves': not args['-S'],
                        'use_A4': use_A4,
                        'landscape': args['--orientation'] == 'L',
                        'width': width,
                        'height': height}

        grid = self.create_maze(width, height, density, add_a_loop)

        # solution = find_solution(grid)

        return_data = {'maze_id': f"{maze_id}"}

        
        # to screen
        dislay_to_screen = True
        print("reached")
        if dislay_to_screen:
            try:
                from renderers.text import render
            except ImportError:
                from maze.renderers.text import render  # NOQA

            render(grid, render_options)

        
        return return_data

    def render_maze(self, width, height, **kwargs): #, density=50, add_a_loop=50, with_curve=False):
        if 'density' in kwargs:
            density = kwargs['density']
        else:
            density = 50
        if 'with_loop' in kwargs:
            add_a_loop = kwargs['with_loop']
        else:
            add_a_loop = False
        if 'with_curve' in kwargs:
            with_curve = kwargs['with_curve']

        if 'designed_assets_folder' in kwargs:
            self.designed_assets_folder = kwargs['designed_assets_folder']

        save_file_name = self.temp_file_name

        # filenames = next(walk(self.designed_assets_folder), (None, None, []))[2]  # [] if no file
        f = []
        for (dirpath, dirnames, filenames) in walk(self.designed_assets_folder):
            f.extend(filenames)
            break
        
        from PIL import Image
        import imageio 
        filemap = {}
        for i in range(len(filenames)):
            try:
                number = int(filenames[i][:-4])
                filemap[number] = Image.open(os.path.join(self.designed_assets_folder, filenames[i]))
            except ValueError:
                continue
            
            
        
        if not 19 in filemap:
            filemap[19] = filemap[15]
        if not 28 in filemap:
            filemap[28] = filemap[15]

        # print(filemap)


        grid = self.create_maze( width, height, density, add_a_loop)
        np_grid = np.array(grid)
        dim = np_grid.shape

        # print(np_grid)

        # try:
        #     from renderers.text import render
        # except ImportError:
        #     from maze.renderers.text import render  # NOQA

        # render(grid, None)

        
        asset_dim = filemap[0].size
        im = Image.new("RGBA", (dim[0] * asset_dim[0], dim[1]*asset_dim[1]), None)
        for i in range(dim[0]):
            for j in range(dim[1]):
                # print(np_grid[i, j])
                to_paste = filemap[np_grid[i, j]]
                coord = (j * asset_dim[1], i * asset_dim[0])
                im.paste(to_paste, coord)
                

        im.save(save_file_name)
        return save_file_name




class Tree(object):
    _children_for_parent = {}
    _parent_for_child = {}

    def __init__(self):
        Tree._children_for_parent[self] = set()
        Tree._parent_for_child[self] = self

    def connected(self, tree):
        return (Tree._parent_for_child[self] ==
                Tree._parent_for_child[tree])

    def connect(self, tree):
        # find root objs
        new_parent = Tree._parent_for_child[self]
        tree_patent = Tree._parent_for_child[tree]

        # move parent
        Tree._children_for_parent[new_parent].add(tree_patent)

        # move children
        children = Tree._children_for_parent[tree_patent]
        Tree._children_for_parent[new_parent] |= children
        Tree._children_for_parent[tree_patent] = set()

        # move parent for child keys too
        for child in Tree._children_for_parent[new_parent]:
            Tree._parent_for_child[child] = new_parent


if __name__ == "__main__":

    # if len(sys.argv) == 1:
    #     print(__doc__)
    #     exit()

    args = {}

    # seed(0)
    maze = WeaveMazeGenerator()
    maze.maze(docopt(__doc__, argv="text -W 50 -H 50 -f test.svg"))

#
