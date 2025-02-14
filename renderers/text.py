# -*- coding: utf-8 -*-
from __future__ import print_function


def render(grid, options):

    TILES = {0: ('   ',
                 '   '),

             1: ('│ │',
                 '└─┘'),

             2: ('┌─┐',
                 '│ │'),

             3: ('│ │',
                 '│ │'),

             4: ('┌──',
                 '└──'),

             5: ('│ └',
                 '└──'),

             6: ('┌──',
                 '│ ┌'),

             7: ('│ └',
                 '│ ┌'),

             8: ('──┐',
                 '──┘'),

             9: ('┘ │',
                 '──┘'),

            10: ('──┐',
                 '┐ │'),

            11: ('┘ │',
                 '┐ │'),

            12: ('───',
                 '───'),

            13: ('┘ └',
                 '───'),

            14: ('───',
                 '┐ ┌'),

            15: ('┘ └',
                 '┐ ┌'),

            19: ('┤ ├',
                 '┤ ├'),

            28: ('┴─┴',
                 '┬─┬')}

    # top left corner
    #print "\x1B[H"
    print('Start' + ' ' * len(grid[0]) * 2)

    
    te = ""
    for z, row in enumerate(grid):

        print(''.join([TILES[r][0] for r in row]))
        print(''.join([TILES[r][1] for r in row]),  end="")

        te += ''.join([TILES[r][0] for r in row])
        te += '\n'
        te += ''.join([TILES[r][1] for r in row])
        te += '\n'

        # bottom right corner ?
        print('End' if z == len(grid) - 1 else '')

    print()

    return te
