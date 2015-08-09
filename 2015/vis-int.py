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
    unit = game_state.unit
    for cell in unit.members:
        gl.glPushMatrix()
        set_ij(unit.pivot.y + cell.y, unit.pivot.x + cell.x)
        display_cell()
        gl.glPopMatrix()


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
    global game_state
    if key == glut.GLUT_KEY_LEFT:
        game_state = lib.next(game_state, 'W')
        glut.glutPostRedisplay()
    elif key == glut.GLUT_KEY_RIGHT:
        game_state = lib.next(game_state, 'E')
        glut.glutPostRedisplay()
    elif key == glut.GLUT_KEY_UP:
        game_state = lib.next(game_state, 'SE')
        glut.glutPostRedisplay()
    elif key == glut.GLUT_KEY_DOWN:
        game_state = lib.next(game_state, 'SW')
        glut.glutPostRedisplay()


task_spec = json.loads(open(sys.argv[1]).read())

units = list(lib._unit_generator(
    task_spec['sourceSeeds'][0],
    task_spec['units'],
    limit=task_spec['sourceLength']))

init_board = lib.Board(task_spec['width'], task_spec['height'], map(lib.Cell.parse, task_spec['filled']))
init_unit = lib.place_unit(init_board, units[0])
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
