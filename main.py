from IPython import embed

rows = 'ABCDEFGHI'
cols = '123456789'
out = []

def cross(a, b):
    return [s+t for s in a for t in b]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def render_margin():
    """
    Prints a margin with a buffer space prior and post to it.
    Used for styling purposes.
    """
    print('         ')
    print('---------------------------------------------------------------')
    print('         ')

def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def grid_values(grid):
    """
    Sets the values for the Sudoku grid based on the given grid input.
    If there is no value for a box it sets it to all possible values it
    can have.
    """
    ou = {}
    input = grid
    for r in row_units:
        ss = input[0:9]
        input = input[9:]
        for idx, n in enumerate(ss):
            if n == '.':
                ou[r[idx]] = '123456789'
            else:
                ou[r[idx]] = n
    return ou


def singles(values):
    """
    Retrieves all boxes with a single value.
    """
    singles = {}
    for v in values:
        box = values[v]
        if len(box) == 1:
            singles[v] = box
    return singles

def multi_values(values):
    """
    Retrieves a dicitonary of boxes that have more than a single value
    """
    multis = {}
    for v in values:
        box = values[v]
        if len(box) > 1:
            multis[v] = int(box)
    return multis

def eliminate(values):
    """
    Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    single = singles(values)
    for v in single:
        val = single[v]
        for p in peers[v]:
            values[p] = values[p].replace(val, '')
    return values


def only_choice(values):
    """
    Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        for d in '123456789':
            dplaces = [box for box in unit if d in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = d
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    """

    single = singles(values)
    multis = dict(set(values.items()) - set(single.items()))

    for m in multis: # dictionary of non singles boxes
        # if this box contains two values
        if len(values[m]) == 2:
            for unit in units[m]: # one list from units
                # remove the unit in question
                uniq_unit = list(unit)
                uniq_unit.remove(m)
                # for each element in the unit
                for u in uniq_unit:
                    # if another box has equal values
                    if values[u] == values[m]:
                        uniq_unit.remove(u)
                        # for each values in our reference box
                        for d in values[m]:
                            for other in uniq_unit:
                                if values[other].find(d) >= 0:
                                    values[other] = values[other].replace(d, '')

    # to extend this we can compare if three values and three equal boxes in unit, etc
    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy
        eliminate(values)

        # Use the Only Choice Strategy
        only_choice(values)

        # Use the Naked Twins Strategy
        naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


# Depth first search for the hardest Sudokus
def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

"""
Execution
"""
# Easy Sudoku
# grid = '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..'
# values = grid_values(grid)

# Hard Sudoku
grid2 = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
values = grid_values(grid2)

print('\nOriginal')
render_margin()
display(values)
render_margin()

print('Reduced')
render_margin()
display(reduce_puzzle(values))
render_margin()

print('Depth First Search Solution')
values = search(values)

render_margin()
display(values)
render_margin()
