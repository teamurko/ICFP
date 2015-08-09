import sys
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import math
import json
import lib

sqrt_3 = math.sqrt(3.0)

cell_display_index = None

def display_cell():
    global cell_display_index
    if cell_display_index is None:
        cell_display_index = gl.glGenLists(1);
        gl.glNewList(cell_display_index, gl.GL_COMPILE);
        gl.glPushMatrix();
        gl.glScale(0.9, 0.9, 1.0);
        gl.glBegin(gl.GL_TRIANGLE_FAN)
        gl.glVertex3f( 0.0, 0.0, 0.0);
        gl.glVertex3f( 0.0, 1.0, 0.0);
        gl.glVertex3f( sqrt_3 / 2.0, 0.5, 0.0);
        gl.glVertex3f( sqrt_3 / 2.0, -0.5, 0.0);
        gl.glVertex3f( 0.0, -1.0, 0.0);
        gl.glVertex3f( -sqrt_3 / 2.0, -0.5, 0.0);
        gl.glVertex3f( -sqrt_3 / 2.0, 0.5, 0.0);
        gl.glVertex3f(  0.0,  1.0, 0.0);
        gl.glEnd();
        gl.glPopMatrix();
        gl.glEndList();
    gl.glCallList(cell_display_index)



def display_game_state(game_state):
    # using [0, 1] x [0, 1]
    game_state_height = game_state.board.height
    game_state_width = game_state.board.width
    cell_size = min(1.0 / (0.5 + 1.5 * game_state_height), 1.0 / (sqrt_3 / 2 + sqrt_3 * game_state_width))

    def set_ij(i, j):
        if i % 2 == 0:
            gl.glTranslate((j + 0.5) * sqrt_3, -0.5 + 1.5 * (game_state_height - i), 0.0)
        else:
            gl.glTranslate((j + 1.0) * sqrt_3, -0.5 + 1.5 * (game_state_height - i), 0.0)

    gl.glScale(cell_size, cell_size, 1.0);
    for i in xrange(game_state_height):
        gl.glPushMatrix();
        set_ij(i, 0)
        for j in xrange(game_state_width):
            if game_state.board.filled[i][j]:
                gl.glColor(0.7, 0.7, 0.3)
            else:
                gl.glColor(0.3, 0.3, 0.3)
            display_cell()
            gl.glTranslate(sqrt_3, 0.0, 0.0)
        gl.glPopMatrix()

    gl.glColor(0.8, 0.3, 0.3)
    raw_unit = game_state.unit.raw_unit
    shiftx = raw_unit['pivot']['x']
    shifty = raw_unit['pivot']['y']
    for cell in raw_unit['members']:
        gl.glPushMatrix()
        set_ij(shifty + cell['y'], shiftx + cell['x'])
        display_cell()
        gl.glPopMatrix()


# class GameState (object):
#     def __init__(self):
#         self._x = 0
#         self._y = 0

#     def width(self):
#         return 5

#     def height(self):
#         return 10

#     def is_empty(self, i, j):
#         return not (
#             (i == 8 and j == 0) or
#             (i == 8 and j == 1) or
#             (i == 8 and j == 4) or
#             (i == 9 and j == 0) or
#             (i == 9 and j == 1) or
#             (i == 9 and j == 3) or
#             (i == 9 and j == 4))

#     def cursor(self):
#         return [(self._y + 1, self._x + 2), (self._y + 1, self._x + 4)]


#     def modify(self, action): # Stub instead of full functional state update
#         if action == 'left':
#             self._x -= 1
#         elif action == 'right':
#             self._x += 1
#         elif action == 'up':
#             self._y -= 1
#         elif action == 'down':
#             self._y += 1


# game_state = GameState()


def display():
    gl.glClearColor(0.0, 0.0, 0.0, 0.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    gl.glDisable(gl.GL_CULL_FACE)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

    gl.glTranslate(-1.0, -1.0, 0.0)
    gl.glScale(2.0, 2.0, 1.0)
    display_game_state(game_state)
    glut.glutSwapBuffers()


def reshape(width, height):
    gl.glViewport(0, 0, width, height)
    gl.glMatrixMode(gl.GL_PROJECTION);
    gl.glLoadIdentity();


def keyboard( key, x, y ):
    if key == '\033':
        sys.exit( )

def special_input(key, x, y):
    # if key == glut.GLUT_KEY_LEFT:
    #     game_state.modify('left')
    #     glut.glutPostRedisplay()
    # elif key == glut.GLUT_KEY_RIGHT:
    #     game_state.modify('right')
    #     glut.glutPostRedisplay()
    # elif key == glut.GLUT_KEY_UP:
    #     game_state.modify('up')
    #     glut.glutPostRedisplay()
    # elif key == glut.GLUT_KEY_DOWN:
    #     game_state.modify('down')
    #     glut.glutPostRedisplay()
    pass

task_spec = json.loads(open(sys.argv[1]).read())

units = list(lib._unit_generator(
    task_spec['sourceSeeds'][0],
    task_spec['units'],
    limit=task_spec['sourceLength']))

init_board = lib.Board(task_spec['width'], task_spec['height'], task_spec['filled'])
init_unit = lib.place_unit(init_board, 0, units[0])
game_state = lib.InitState(init_board, init_unit, units)


glut.glutInit()
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)
glut.glutCreateWindow('Honeycomb board visualisation')
glut.glutReshapeWindow(800,800)
glut.glutReshapeFunc(reshape)
glut.glutDisplayFunc(display)
glut.glutKeyboardFunc(keyboard)
glut.glutSpecialFunc(special_input)
glut.glutMainLoop()
