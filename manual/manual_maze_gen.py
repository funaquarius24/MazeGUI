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
# from venv import create
import itertools

from weave.Maze import Maze
from renderers.svg import render

from docopt import docopt
from os import walk
import numpy as np

from PIL import Image, ImageDraw
from math import floor


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
        os.makedirs('assets/manualmazegen/', exist_ok=True)  # succeeds even if directory exists.
        self.designed_assets_folder = 'assets/test_templates/'
        self.temp_file_name = 'assets/temp_manual/temp.png'
        self.temp_solution_file_name = 'assets/temp_manual/temp_solution.png'
        self.save_folder = 'assets/manualmazegen/'

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
        sofar = self.search(grid, (0, 0),  [(0, 0)], 0)
        # print('Solution ->', sofar)
        return sofar

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
        
        if 'solution_assets_folder' in kwargs:
            self.solution_asset_folder = kwargs['solution_assets_folder']
        else:
            self.solution_asset_folder = None

        if 'multiple' in kwargs:
            multiple = kwargs['multiple']
            maze_number = kwargs['maze_number']
            save_file_name = self.save_folder + 'maze-{}.png'.format(maze_number)
            save_solution_file_name = self.save_folder + 'maze-{}_solution.png'.format(maze_number)
        else:
            multiple = False

            save_file_name = self.temp_file_name
            save_solution_file_name = self.temp_solution_file_name

        # filenames = next(walk(self.designed_assets_folder), (None, None, []))[2]  # [] if no file
        grid = self.create_maze( width, height, density, add_a_loop)
        solution = self.find_solution(grid)

        im = self.create_assets_image(grid)
        
        im.save(save_file_name)

        im_solution = self.create_solution_assets_image(im, grid, self.solution_asset_folder, solution)
        im_solution.save(save_solution_file_name)
        return save_file_name

    def create_assets_image(self, grid):
        save_file_name = self.temp_file_name
        f = []
        for (dirpath, dirnames, filenames) in walk(self.designed_assets_folder):
            f.extend(filenames)
            break

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
        im_template = filemap[0]
        sub_width = im_template.size[0] // 3
        sub_height = im_template.size[1] // 3
        basewidth = sub_width

        if not 100 in filemap:
            im_start = Image.new("RGB", (floor(sub_width), floor(sub_height)), (220, 20, 20))
        else:
            if filemap[100].size[0] != sub_width or filemap[100].size[1] != sub_height:
                wpercent = (basewidth/float(filemap[100].size[0]))
                hsize = int((float(filemap[100].size[1])*float(wpercent)))
                # im_start = filemap[100].crop((sub_width, sub_width, sub_height*2, sub_height*2))
                im_start = filemap[100].resize((basewidth,hsize), Image.ANTIALIAS)
            else:
                im_start = filemap[100]
        if not 200 in filemap:
            im_end = Image.new("RGB", (floor(sub_width), floor(sub_height)), (20, 20, 220))
        else:
            if filemap[200].size[0] != sub_width or filemap[200].size[1] != sub_height:
                wpercent = (basewidth/float(filemap[200].size[0]))
                hsize = int((float(filemap[200].size[1])*float(wpercent)))
                # im_end = filemap[200].crop((sub_width, sub_width, sub_height*2, sub_height*2))
                im_end = filemap[200].resize((basewidth,hsize), Image.ANTIALIAS)
            else:
                im_end = filemap[200]


        
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
                coord = (j * asset_dim[1], i * asset_dim[0])
                
                to_paste = filemap[np_grid[i, j]]
                if i == 0 and j == 0:
                    tmp_paste = to_paste.copy()
                    tmp_paste.paste(im_start, (sub_width, sub_height))
                    im.paste(tmp_paste, coord)
                elif i == dim[0] - 1 and j == dim[1] - 1:
                    tmp_paste = to_paste.copy()
                    tmp_paste.paste(im_end, (sub_width, sub_height))
                    im.paste(tmp_paste, coord)
                else:
                    im.paste(to_paste, coord)

        im.save(save_file_name)
        return im

    def direction(self, dx, dy):
        if (dx == 0):
            return 'b' if dy < 0 else 't'
        return 'r' if dx < 0 else 'l'

    def pairwise(self, iterable):
        "s -> (s0, s1), (s1, s2), (s2, s3), ..."
        a, b = itertools.tee(iterable)
        next(b, None)
        return zip(a, b)


    def threes(self, iterator):
        "s -> (s0, s1, s2), (s1, s2, s3), (s2, s3, 4), ..."
        a, b, c = itertools.tee(iterator, 3)
        next(b, None)
        next(c, None)
        next(c, None)
        return zip(a, b, c)
    
    def create_solution_assets_image(self, im, grid, solution_folder_name, solution=None):

        if solution_folder_name is None:
            print("No solution folder selected!")
            return
        save_file_name = self.temp_file_name
        # print(solution_folder_name)
        f = []
        for (dirpath, dirnames, filenames) in walk(self.designed_assets_folder):
            f.extend(filenames)
            break

        f_solution = []
        for (dirpath, dirnames, solution_filenames) in walk(solution_folder_name):
            f_solution.extend(solution_filenames)
            break
        
        
        filemap = {}
        for i in range(len(filenames)):
            try:
                number = int(filenames[i][:-4])
                filemap[number] = Image.open(os.path.join(self.designed_assets_folder, filenames[i]))
            except ValueError:
                continue

        if len(f_solution) == 0:
            print("No solution files found!")
            return
        solution_filemap = {}
        for i in range(len(solution_filenames)):
            try:
                # print("started")
                
                filename_full = solution_filenames[i][:-4]
                filename_split = filename_full.split('_')
                filename_number = filename_split[0]
                number = int(filename_number)
                # print("number: ", number)
                if len(filename_split) > 1:
                    # if number == 15:
                        # print('reached1')
                    filename_direction = filename_split[1]
                    if not number in solution_filemap:
                        solution_filemap[number] = {}
                    solution_filemap[number][filename_direction] = Image.open(os.path.join(solution_folder_name, solution_filenames[i]))
                    # print(solution_filemap[number])
                else:
                    # if number == 15:
                    #     print('reached')
                    solution_filemap[number] = Image.open(os.path.join(solution_folder_name, solution_filenames[i]))
              
            except ValueError:
                continue
            
        # print(solution_filemap)
        
        if not 19 in filemap:
            filemap[19] = filemap[15]
        if not 28 in filemap:
            filemap[28] = filemap[15]

        if not 19 in solution_filemap:
            solution_filemap[19] = solution_filemap[15]
        if not 28 in solution_filemap:
            solution_filemap[28] = solution_filemap[15]
        

        # print(filemap)
        im_template = filemap[0]
        sub_width = im_template.size[0] // 3
        sub_height = im_template.size[1] // 3
        basewidth = sub_width


        
        np_grid = np.array(grid)
        dim = np_grid.shape

        TILES = {'tb': 's', 'tr': 'se', 'tl': 'sw', 'lt': 'sw', 'rt': 'se',
                  'bt': 's', 'br': 'ne', 'bl': 'nw', 'lb': 'nw', 'rb': 'ne',
                  'lr': 'w', 'rl': 'w'
                  }

        

        # im.show()
        asset_dim = solution_filemap[0].size
        # print(solution)
        # print(np_grid)
        # print('asset_dim: ', asset_dim)

        visited = [] # keep a list of the coordinates of all visited bridges
        
        for i, [prev, curr, head] in enumerate(self.threes(solution)):

            from_d = self.direction(curr[0] - prev[0], curr[1] - prev[1])
            to_d = self.direction(curr[0] - head[0], curr[1] - head[1])
            direction = from_d + to_d
            # print('direction: ', direction)

            dx = (prev[0] - curr[0]) // 2
            dy = (prev[1] - curr[1]) // 2
            # print('dx: {}  dy: {}'.format(dx, dy))
            # coordinates = ((dx + curr[0]) * self.S, (dy + curr[1]) * self.S)
            # print('coordinates: ', coordinates)
            prev_tile = grid[dy + curr[1]][dx + curr[0]]
            # print("prev tile: ", prev_tile)
            # print("coordinate: ", ((dy + curr[1]), (dx + curr[0])))
            # print("curr: ", curr)

            prev_coord_row_col = ((dx + curr[0]) ,  (dy + curr[1]))
            if dx == 1 or dx == -1:
                if prev_tile == 19 or prev_tile == 28:
                    coord = ((dx + curr[0]) * asset_dim[1], (dy + curr[1]) * asset_dim[0] )
                    if prev_coord_row_col in visited:
                        tmp_to_paste = solution_filemap[prev_tile]['a']
                    else:
                        tmp_to_paste = solution_filemap[prev_tile]['w']
                        visited.append(prev_coord_row_col)
                        
                    tmp_paste = tmp_to_paste.copy()
                    im.paste(tmp_paste, coord)

            if dy == 1 or dy == -1:
                if prev_tile == 19 or prev_tile == 28:
                    coord = ((dx + curr[0]) * asset_dim[1], (dy + curr[1]) * asset_dim[0] )
                    if prev_coord_row_col in visited:
                        tmp_to_paste = solution_filemap[prev_tile]['a']
                    else:
                        tmp_to_paste = solution_filemap[prev_tile]['s']
                        visited.append(prev_coord_row_col)
                    
                    # coord = ((dy + curr[0]) * asset_dim[0], (dx + curr[1]) * asset_dim[1])
                    tmp_paste = tmp_to_paste.copy()
                    im.paste(tmp_paste, coord)
                    
                    
                

            # if dy == 1 or dy == -1:
            #     if prev_tile == 19 and not self.faint:
            #         self.t3(*coordinates)
            #     elif prev_tile == 28:
            #         self.th(*coordinates)

            if i == 0:
                # Do for the first tile          
                coord = (0, 0)
                number = np_grid[0, 0]
                tmp_to_paste = solution_filemap[number]
                if not isinstance(tmp_to_paste, dict):
                    tmp_paste = tmp_to_paste.copy()
                    im.paste(tmp_paste, coord)
                else:
                    for elem in tmp_to_paste.keys():
                        tmp_paste = tmp_to_paste[elem].copy()
                        im.paste(tmp_paste, coord)
            # curr = prev
            coord = (curr[0] * asset_dim[0], curr[1] * asset_dim[0])
            number = np_grid[curr[1], curr[0]]
            tmp_to_paste = solution_filemap[number]

            if not isinstance(tmp_to_paste, dict):
                # print('curr0: ', curr)
                
                # print('number0: ', number)
                # print('i 0 : ', i)
                tmp_paste = tmp_to_paste.copy()
                im.paste(tmp_paste, coord)
            else:
                # print('tmp to paste: ', tmp_to_paste.keys())
                # print('curr: ', curr)
                
                # print('number: ', number)
                # print('i : ', i)
                
                direction = from_d + to_d
                # print('direction: ', direction)
                
                direction_tile = TILES[direction]
                # print('direction_tile: ', direction_tile)

                # if direction_tile not in tmp_to_paste.keys():
                #     print("is direction in prev: ", solution_filemap[prev_tile])
                
                tmp_paste = solution_filemap[number][direction_tile].copy()
                # for elem in tmp_to_paste.keys():
                #     tmp_paste = tmp_to_paste[elem].copy()
                im.paste(tmp_paste, coord)


            # print([prev, curr, head])
            # print('fromd: ', from_d)
            # print('to_d: ', to_d)
            # print("i: ", i)

            # coord = 
            
        # im.show()
        
        return im
         




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
