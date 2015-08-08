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
        yield units[index]
        limit -= 1


MOVES = ['W', 'E', 'SW', 'SE', 'CW', 'CC', 'NU']  # last is 'next unit'


class Board(object):
    def __init__(self, width, height, filled_cells):
        self.width = width
        self.height = height
        self.filled_cells = filled_cells


class Unit(object):
    def __init__(self, id, raw_unit):
        self.id = id
        self.raw_unit = raw_unit


class State(object):
    def __init__(self, prev_state, move, unit):
        self.prev_state = prev_state
        self.move = move
        self.unit = unit
        self.units = prev_state.units
   
    def is_init(self):
        return self.unit is None

    def has_prev(self):
        return not self.is_init()

    def is_final(self):
        return False

    def is_valid(self):
        return True

    def as_final(self):
        return FinalState(self.prev_state, move, unit)

    def history(self):
        state = self.prev_state
        units = []
        while not state.is_init():
            if not units or units[-1].id != state.unit.id:
                units.append(state.unit)
            state = state.prev_state
        assert state.is_init()
        units.reverse()
        return (state.board, units)


class InitState(State):
    def __init__(self, board, units):
        self.board = board
        self.units = units
        self.unit = None

    @property
    def unit(self):
        raise StateException("Initial state does not have unit")

    def history(self):
        return (self.board, [])


class FinalState(State):
    def is_final(self):
        return True


class InvalidState(State):
    def is_valid(self):
        return False


def next(state, move):
    if self.state.is_final():
        raise StateException("Cannot move from final state")
    if not self.state.is_valid():
        raise StateException("Cannot move from invalid state")
       
   
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
    move_monkey = MoveMonkey(InitState(init_board, units))

