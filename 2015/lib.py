import copy

class StateException(Exception):
    pass

class MoveException(Exception):
    pass


def _unit_index_generator(seed):
    yield seed
    mod = 2 ** 32
    x = seed
    while True:
        x = (1103515245 * x + 12345) % mod
        yield x


def _unit_generator(seed, raw_units, limit):
    count = 0
    for index in _unit_index_generator(seed):
        if limit == 0:
            break
        yield Unit.parse(count, raw_units[index % len(raw_units)])
        count += 1
        limit -= 1


MOVES = ['W', 'E', 'SW', 'SE', 'CW', 'CC']

_STATES = {}


class Cell(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def parse(json_data):
        return Cell(json_data['x'], json_data['y'])

    def moved(self, direction):
        if direction == 'W':
            return Cell(self.x - 1, self.y)
        elif direction == 'E':
            return Cell(self.x + 1, self.y)
        elif direction == 'SW':
            if self.y % 2 == 0:
                return Cell(self.x - 1, self.y + 1)
            else:
                return Cell(self.x, self.y + 1)
        elif direction == 'SE':
            if self.y % 2 == 0:
                return Cell(self.x, self.y + 1)
            else:
                return Cell(self.x + 1, self.y + 1)

    def rotated(self, pivot):
        raise NotImplementedError()        


class Board(object):
    def __init__(self, width, height, filled_cells):
        self.width = width
        self.height = height
        self.filled_cells = filled_cells
        self.filled = [[False for _ in xrange(self.width)] for _ in xrange(self.height)]
        for cell in self.filled_cells:
            self.filled[cell.y][cell.x] = True

    def __deepcopy__(self, memo):
        obj_copy = Board(self.width, self.height, copy.deepcopy(self.filled_cells))
        return obj_copy

    def collides(self, unit):
        for cell in unit.members:
            if self.filled[cell.y][cell.x]:
                return True
            if cell.x < 0 or cell.x >= self.width or cell.y < 0 or cell.y >= self.height:
                return True
        return False


class Unit(object):
    def __init__(self, id, pivot, members):
        self.id = id
        self.pivot = pivot
        self.members = members

    def moved(self, direction):
        members = []
        for cell in self.members:
            members.append(
                Cell(self.pivot.x + cell.x, self.pivot.y + cell.y).moved(direction))
        pivot = self.pivot.moved(direction)

        members = [Cell(cell.x - pivot.x, cell.y - pivot.y) for cell in members]
        return Unit(self.id, pivot, members)

    @staticmethod
    def parse(id, json_data):
        return Unit(
            id,
            Cell.parse(json_data['pivot']),
            map(Cell.parse, json_data['members'])
        )
        
    
class State(object):
    def __init__(self, id, prev_state, board, move, unit):
        self.id = id
        self.prev_state = prev_state
        self.board = board
        self.move = move
        self.unit = unit
        self.units = prev_state.units
        _STATES[self.id] = self
   
    def is_init(self):
        return False

    def has_prev(self):
        return not self.is_init()

    def is_final(self):
        return False

    def is_valid(self):
        return True

    def as_final(self):
        return FinalState(len(_STATES), self.prev_state, self.board, self.move, self.unit)


class InitState(State):
    def __init__(self, board, unit, units):
        self.id = 0
        self.board = board
        self.unit = unit
        self.units = units
        _STATES[self.id] = self

    def is_init(self):
        return True


class FinalState(State):
    def is_final(self):
        return True


class InvalidState(State):
    def is_valid(self):
        return False


def _rotate_cw(origin, cells):
    raise NotImplementedError()


def _rotate_cc(origin, cells):
    raise NotImplementedError()


def place_unit(board, unit):
    #stub for now
    pivot_y = 0
    pivot_x = board.width / 2
    return Unit(unit.id, Cell(pivot_x, pivot_y), unit.members)


def next(state, move):
    if state.is_final():
        raise MoveException("Cannot move from final state")
    if not state.is_valid():
        raise MoveException("Cannot move from invalid state")

    unit = state.unit.moved(move)
    if state.board.collides(unit):
        board = copy.deepcopy(state.board)
        board.add_unit(state.unit)
        if state.unit.id + 1 == len(state.units):
            return FinalState(len(_STATES), state, board, move, None)
        unit = place_unit(board, copy.deepcopy(state.units[state.unit.id + 1]))
        if unit is None:
            return FinalState(len(_STATES), state, board, move, unit)
        return State(len(_STATES), state, board, move, unit)
    return State(len(_STATES), state, copy.deepcopy(state.board), move, unit)

   
class MoveMonkey(object):
    def __init__(self, init_state):
        self.state = init_state
        self.history = [init_state]

    def next(self, move):
        next_state = next(self.state, move)
        self.history.append(state)
        self.state = next_state

    def rollback(self):
        if len(self.history) == 1:
            raise MoveException("Cannot rollback beyond init state")
        self.state = self.history[-1]
        self.history.pop()
       

def solve(task_spec, end_time):
    result_list = []
    seeds = task_spec['sourceSeeds']
    if len(seeds) > 1:
        for seed in seeds:
            task_spec['sourceSeeds'] = [seed]
            result_list.extend(solve(task_spec, end_time))
        return
    units = list(_unit_generator(
                    seeds[0],
                    task_spec['units'],
                    limit=task_spec['sourceLength']))
    init_board = Board(task_spec['width'], task_spec['height'], task_spec['filled'])
    init_unit = place_unit(init_board, 0, units[0])
    move_monkey = MoveMonkey(InitState(init_board, units))
