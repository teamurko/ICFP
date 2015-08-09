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


def _unit_generator(seed, units, limit):
    for index in _unit_index_generator(seed):
        if limit == 0:
            break
        yield units[index % len(units)]
        limit -= 1


MOVES = ['W', 'E', 'SW', 'SE', 'CW', 'CC']

_STATES = {}


class Board(object):
    def __init__(self, width, height, filled_cells):
        self.width = width
        self.height = height
        self.filled_cells = filled_cells
        self.filled = [[False for _ in xrange(self.width)] for _ in xrange(self.height)]
        for cell in self.filled_cells:
            self.filled[cell['y']][cell['x']] = True

    def __deepcopy__(self):
        obj_copy = Board(self.width, self.height, copy.deepcopy(self.filled_cells))
        return obj_copy

    def collides(self, unit):
        for cell in unit.raw_unit['members']:
            if self.filled[cell['y']][cell['x']]:
                return True
        return False


class Unit(object):
    def __init__(self, id, raw_unit):
        self.id = id
        self.raw_unit = raw_unit


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


def _move_unit(unit, move):
    res = copy.deepcopy(unit)
    if move == 'W':
        res['pivot'] = {
            'x': unit['pivot']['x'] - 1,
            'y': unit['pivot']['y']
        }
    elif move == 'E':
        res['pivot'] = {
            'x': unit['pivot']['x'] + 1,
            'y': unit['pivot']['y']
        }
    elif move == 'SW':
        if unit['pivot']['y'] % 2 == 0:
            res['pivot'] = {
                'x': unit['pivot']['x'] - 1,
                'y': unit['pivot']['y'] + 1
            }
        else:
            res['pivot'] = {
                'x': unit['pivot']['x'],
                'y': unit['pivot']['y'] + 1
            }
    elif move == 'SE':
        if unit['pivot']['y'] % 2 == 0:
            res['pivot'] = {
                'x': unit['pivot']['x'],
                'y': unit['pivot']['y'] + 1
            }
        else:
            res['pivot'] = {
                'x': unit['pivot']['x'] + 1,
                'y': unit['pivot']['y'] + 1
            }
    elif move == 'CW':
        res['members'] = _rotate_cw(res['pivot'], res['members'])
    else:
        assert move == 'CC'
        res['members'] = _rotate_cc(res['pivot'], res['members'])
    return res


def place_unit(board, unit_id, raw_unit):
    #stub for now
    pivot_y = 0
    pivot_x = board.width / 2
    raw_unit['pivot'] = {
        'x': pivot_x,
        'y': pivot_y
    }
    return Unit(unit_id, raw_unit)


def next(state, move):
    if state.is_final():
        raise MoveException("Cannot move from final state")
    if not state.is_valid():
        raise MoveException("Cannot move from invalid state")

    unit = _move_unit(self.unit, move)
    if state.board.collides(unit):
        board = copy.deepcopy(state.board)
        board.add_unit(state.unit)
        if state.unit.id + 1 == len(state.units):
            return FinalState(len(_STATES), state, board, move, None)
        unit = place_unit(board, state.unit.id + 1, copy.deepcopy(state.units[state.unit.id + 1]))
        if unit is None:
            return FinalState(len(_STATES), state, board, move, unit)
        return State(len(_STATES), state, board, move, unit)
    return State(len(_STATES), state, board, move, unit)

   
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
