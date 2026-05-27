from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random

cameraX = 0
cameraY = 8
cameraZ = 28

lookX = 0
lookY = 2
lookZ = 0

trainPos    = -80
trainSpeed  = 0.35
wheelRotate = 0.0

gateAngle        = -90.0   # -90 = up/open, 0 = horizontal/closed
GATE_CLOSE_START = -25
GATE_OPEN_START  =  18

MAX_SMOKE = 50

class SmokeParticle:
    def __init__(self):
        self.reset(-999)

    def reset(self, trainX):
        self.x     = trainX + 3.5 + random.uniform(-0.3, 0.3)
        self.y     = 4.2 + random.uniform(-0.2, 0.2)
        self.z     = random.uniform(-0.4, 0.4)
        self.vx    = random.uniform(-0.06, -0.01)
        self.vy    = random.uniform(0.04, 0.10)
        self.vz    = random.uniform(-0.03, 0.03)
        self.size  = random.uniform(0.30, 0.55)
        self.age   = 0
        self.maxAge= random.randint(50, 100)
        self.alpha = random.uniform(0.55, 0.80)

    def update(self, trainX):
        self.x    = self.x + self.vx
        self.y    = self.y + self.vy
        self.size = self.size + 0.010
        self.alpha = self.alpha - 0.007
        self.age  = self.age + 1
        if self.age >= self.maxAge or self.alpha <= 0:
            self.reset(trainX)

smokeParticles = [SmokeParticle() for _ in range(MAX_SMOKE)]

random.seed(42)

class Cloud:
    def __init__(self, x, y, z):
        self.x     = x
        self.y     = y
        self.z     = z
        self.speed = random.uniform(0.012, 0.030)
        self.puffs = [
            ( 0.0,  0.0, 0, random.uniform(2.8, 3.4)),
            ( 2.8,  0.5, 0, random.uniform(2.0, 2.6)),
            (-2.8,  0.5, 0, random.uniform(1.8, 2.4)),
            ( 1.2,  1.3, 0, random.uniform(1.5, 2.1)),
            (-1.0,  1.1, 0, random.uniform(1.3, 1.9)),
        ]

    def update(self):
        self.x = self.x + self.speed
        if self.x > 130:
            self.x  = -130
            self.y  = random.uniform(20, 36)
            self.z  = random.uniform(-60, 60)

clouds = [
    Cloud(random.uniform(-110, 110),
          random.uniform(22, 36),
          random.uniform(-55, 55))
    for _ in range(9)
]

TREE_DATA = []
base_positions = [
    (-50, 16), (-35, 18), (-20, 16), (10, 17), (25, 18), (40, 16),
    (55, 17),  (70, 16),  (-60, 20), (60, 20),
    (-50,-16), (-35,-18), (-20,-16), (10,-17), (25,-18), (40,-16),
    (55,-17),  (70,-16),  (-60,-20), (60,-20),
]
for (tx, tz) in base_positions:
    TREE_DATA.append((tx, tz, random.uniform(0.88, 1.14)))


SUN_X, SUN_Y, SUN_Z = 55, 42, -60

fog = False


#  HELPERS

def drawSphere(r, sl=20, st=20):
    glutSolidSphere(r, sl, st)

def drawCylinder(base, top, height, sl=16, st=1):
    q = gluNewQuadric()
    gluCylinder(q, base, top, height, sl, st)
    gluDeleteQuadric(q)

# SKY

def drawSky():
    glDisable(GL_DEPTH_TEST)
    glDepthMask(GL_FALSE)

    glBegin(GL_QUADS)
    # bottom row – horizon colour
    glColor3f(0.65, 0.85, 1.00)
    glVertex3f(-500, -5,  -499)
    glVertex3f( 500, -5,  -499)
    # top row – deep sky colour
    glColor3f(0.22, 0.52, 0.92)
    glVertex3f( 500, 300, -499)
    glVertex3f(-500, 300, -499)
    glEnd()

    glColor3f(0.22, 0.52, 0.92)
    glBegin(GL_QUADS)
    glVertex3f(-500, -5,  -499)
    glVertex3f(-500, -5,   499)
    glVertex3f(-500,  300,  499)
    glVertex3f(-500,  300, -499)

    glVertex3f( 500, -5,   499)
    glVertex3f( 500, -5,  -499)
    glVertex3f( 500,  300, -499)
    glVertex3f( 500,  300,  499)

    glVertex3f(-500, 300,  499)
    glVertex3f( 500, 300,  499)
    glVertex3f( 500, 300, -499)
    glVertex3f(-500, 300, -499)
    glEnd()

    glDepthMask(GL_TRUE)
    glEnable(GL_DEPTH_TEST)

    glPushMatrix()
    glTranslatef(SUN_X, SUN_Y, SUN_Z)

    glDisable(GL_BLEND)

    glColor3f(1.0, 0.85, 0.0)  # strong yellow
    drawSphere(6, 20, 20)

    glPopMatrix()

    # Clouds 
    for cloud in clouds:
        for (px, py, pz, pr) in cloud.puffs:
            glPushMatrix()
            glTranslatef(cloud.x + px, cloud.y + py, cloud.z + pz)
            glColor4f(1.0, 1.0, 1.0, 0.88)
            drawSphere(pr, 14, 14)
            glPopMatrix()

    glDisable(GL_BLEND)


#  GROUND


def drawGround():
    glColor3f(0.26, 0.60, 0.22)
    glBegin(GL_QUADS)
    glVertex3f(-300, -2.0, -300)
    glVertex3f( 300, -2.0, -300)
    glVertex3f( 300, -2.0,  300)
    glVertex3f(-300, -2.0,  300)
    glEnd()


    glColor3f(0.44, 0.41, 0.36)
    glBegin(GL_QUADS)
    glVertex3f(-300, -1.99, -3.8)
    glVertex3f( 300, -1.99, -3.8)
    glVertex3f( 300, -1.99,  3.8)
    glVertex3f(-300, -1.99,  3.8)
    glEnd()


#  TRACK

def drawTrack():
    for side in (-2.0, 2.0):
        # rail web
        glColor3f(0.48, 0.48, 0.50)
        glPushMatrix()
        glTranslatef(0, -1.74, side)
        glScalef(300, 0.22, 0.18)
        glutSolidCube(1)
        glPopMatrix()
        # rail head
        glColor3f(0.72, 0.72, 0.75)
        glPushMatrix()
        glTranslatef(0, -1.63, side)
        glScalef(300, 0.07, 0.26)
        glutSolidCube(1)
        glPopMatrix()

    # sleepers
    for i in range(-100, 101, 3):
        glColor3f(0.36, 0.22, 0.09)
        glPushMatrix()
        glTranslatef(i, -1.93, 0)
        glScalef(0.55, 0.18, 5.6)
        glutSolidCube(1)
        glPopMatrix()


#  ROAD

def drawRoad():
    glColor3f(0.42, 0.42, 0.44)
    glBegin(GL_QUADS)
    glVertex3f(-6, -1.97, -120)
    glVertex3f( 6, -1.97, -120)
    glVertex3f( 6, -1.97,  120)
    glVertex3f(-6, -1.97,  120)
    glEnd()

    # kerbs
    glColor3f(0.80, 0.80, 0.80)
    for kx, sx in ((-6, -1), (6, 1)):
        glBegin(GL_QUADS)
        glVertex3f(kx,           -1.96, -120)
        glVertex3f(kx + sx*0.4,  -1.96, -120)
        glVertex3f(kx + sx*0.4,  -1.96,  120)
        glVertex3f(kx,           -1.96,  120)
        glEnd()

    # centre dashes
    glColor3f(1, 1, 0)
    for i in range(-110, 115, 10):
        glBegin(GL_QUADS)
        glVertex3f(-0.15, -1.965, i)
        glVertex3f( 0.15, -1.965, i)
        glVertex3f( 0.15, -1.965, i+5)
        glVertex3f(-0.15, -1.965, i+5)
        glEnd()


#  WHEEL

def drawDetailedWheel():
    glPushMatrix()
    glRotatef(wheelRotate, 0, 0, 1)

    glColor3f(0.10, 0.10, 0.10)
    glutSolidTorus(0.14, 0.52, 12, 28)

    glColor3f(0.62, 0.62, 0.66)
    drawSphere(0.20, 10, 10)

    glColor3f(0.52, 0.52, 0.55)
    for k in range(6):
        glPushMatrix()
        glRotatef(60*k, 0, 0, 1)
        glTranslatef(0.26, 0, 0)
        glRotatef(90, 0, 1, 0)
        drawCylinder(0.04, 0.04, 0.52, 8)
        glPopMatrix()

    glPopMatrix()


#  TRAIN

def drawTrain():
    glPushMatrix()
    glTranslatef(trainPos, 0, 0)

    # boiler body
    glColor3f(0.80, 0.10, 0.10)
    glPushMatrix()
    glTranslatef(0, 0.3, 0)
    glScalef(7.5, 2.6, 2.9)
    glutSolidCube(1)
    glPopMatrix()

    # cab
    glColor3f(0.65, 0.08, 0.08)
    glPushMatrix()
    glTranslatef(-3.4, 1.5, 0)
    glScalef(2.2, 2.0, 2.9)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(0.40, 0.05, 0.05)
    glPushMatrix()
    glTranslatef(-3.4, 2.7, 0)
    glScalef(2.4, 0.28, 3.1)
    glutSolidCube(1)
    glPopMatrix()

    # cab windows
    glColor3f(0.55, 0.85, 1.0)
    for wz in (-0.85, 0.85):
        glPushMatrix()
        glTranslatef(-4.4, 1.7, wz)
        glScalef(0.08, 0.9, 0.75)
        glutSolidCube(1)
        glPopMatrix()

    # front nose
    glColor3f(0.75, 0.09, 0.09)
    glPushMatrix()
    glTranslatef(4.2, 0.0, 0)
    glScalef(1.2, 2.0, 2.9)
    glutSolidCube(1)
    glPopMatrix()

    # boiler dome
    glColor3f(0.85, 0.75, 0.10)
    glPushMatrix()
    glTranslatef(1.5, 1.8, 0)
    drawSphere(0.65, 16, 16)
    glPopMatrix()

    # chimney
    glColor3f(0.20, 0.20, 0.20)
    glPushMatrix()
    glTranslatef(3.5, 1.6, 0)
    glRotatef(-90, 1, 0, 0)
    drawCylinder(0.28, 0.22, 1.8, 14)
    glTranslatef(0, 0, 1.8)
    drawCylinder(0.38, 0.28, 0.35, 14)
    glPopMatrix()

    # buffer beam
    glColor3f(0.30, 0.30, 0.30)
    glPushMatrix()
    glTranslatef(5.0, -0.9, 0)
    glScalef(0.25, 0.6, 2.9)
    glutSolidCube(1)
    glPopMatrix()

    # headlamp
    glColor3f(1.0, 1.0, 0.6)
    glPushMatrix()
    glTranslatef(4.85, 0.5, 0)
    drawSphere(0.32, 12, 12)
    glPopMatrix()

    # running plate
    glColor3f(0.55, 0.08, 0.08)
    glPushMatrix()
    glTranslatef(-0.5, -0.95, 0)
    glScalef(8.5, 0.22, 3.5)
    glutSolidCube(1)
    glPopMatrix()

    # loco wheels
    for wx in (3.5, 1.5, -0.5, -2.5):
        for wz in (-1.7, 1.7):
            glPushMatrix()
            glTranslatef(wx, -1.55, wz)
            drawDetailedWheel()
            glPopMatrix()

    # connecting rod
    glColor3f(0.60, 0.60, 0.62)
    glPushMatrix()
    glTranslatef(1.5, -1.55, 1.72)
    glScalef(4.2, 0.12, 0.12)
    glutSolidCube(1)
    glPopMatrix()

    # wagon body
    glColor3f(0.18, 0.22, 0.55)
    glPushMatrix()
    glTranslatef(-9.0, 0.1, 0)
    glScalef(5.5, 2.5, 2.85)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(0.13, 0.16, 0.42)
    glPushMatrix()
    glTranslatef(-9.0, 1.5, 0)
    glScalef(5.6, 0.28, 2.95)
    glutSolidCube(1)
    glPopMatrix()

    # wagon windows
    glColor3f(0.55, 0.85, 1.0)
    for wxi in (-7.5, -9.0, -10.5):
        for wz in (-0.8, 0.8):
            glPushMatrix()
            glTranslatef(wxi, 0.3, wz)
            glScalef(0.9, 0.8, 0.07)
            glutSolidCube(1)
            glPopMatrix()

    # wagon wheels
    for wx in (-7.5, -10.5):
        for wz in (-1.7, 1.7):
            glPushMatrix()
            glTranslatef(wx, -1.55, wz)
            drawDetailedWheel()
            glPopMatrix()

    # coupler
    glColor3f(0.40, 0.40, 0.42)
    glPushMatrix()
    glTranslatef(-6.0, -1.0, 0)
    glScalef(1.5, 0.25, 0.25)
    glutSolidCube(1)
    glPopMatrix()

    # ── smoke (world-coords offset inside trainPos push) ──────────────────────
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    for p in smokeParticles:
        local_x = p.x - trainPos
        glColor4f(0.80, 0.80, 0.80, max(0.0, p.alpha))
        glPushMatrix()
        glTranslatef(local_x, p.y, p.z)
        drawSphere(p.size, 10, 10)
        glPopMatrix()
    glDisable(GL_BLEND)

    glPopMatrix()


#  GATE

def drawGateArm(length):
    segments = 8
    seg_len  = length / segments
    for k in range(segments):
        glColor3f(1.0, 0.0, 0.0) if k % 2 == 0 else glColor3f(1.0, 1.0, 1.0)
        glPushMatrix()
        glTranslatef(k * seg_len + seg_len/2, 0, 0)
        glScalef(seg_len, 0.28, 0.28)
        glutSolidCube(1)
        glPopMatrix()
    glColor3f(1.0, 0.95, 0.0)
    glPushMatrix()
    glTranslatef(length, 0, 0)
    drawSphere(0.22, 8, 8)
    glPopMatrix()


def drawGateSide(side_z):
    glPushMatrix()
    glTranslatef(0, -2.0, side_z)

    # post
    glColor3f(0.75, 0.75, 0.78)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    drawCylinder(0.18, 0.16, 5.5, 12)
    glPopMatrix()

    glColor3f(0.50, 0.50, 0.52)
    glPushMatrix()
    glTranslatef(0, 5.5, 0)
    drawSphere(0.22, 8, 8)
    glPopMatrix()

    # signal box
    glColor3f(0.12, 0.12, 0.12)
    glPushMatrix()
    glTranslatef(0, 4.2, 0)
    glScalef(0.5, 1.0, 0.5)
    glutSolidCube(1)
    glPopMatrix()

    # lights
    is_closed = (gateAngle > -45)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(1.0, 0.05, 0.05, 1.0 if is_closed else 0.20)
    glPushMatrix()
    glTranslatef(0.30, 4.45, 0)
    drawSphere(0.18, 8, 8)
    glPopMatrix()
    glColor4f(0.05, 1.0, 0.15, 0.20 if is_closed else 1.0)
    glPushMatrix()
    glTranslatef(0.30, 4.05, 0)
    drawSphere(0.18, 8, 8)
    glPopMatrix()
    glDisable(GL_BLEND)

    # arm
    glTranslatef(0, 5.0, 0)
    glRotatef(gateAngle, 0, 0, 1)
    glTranslatef(0.3, 0, 0)
    drawGateArm(5.5)

    glPopMatrix()


def drawGates():
    glPushMatrix()
    glTranslatef(-6, 0, 0)
    drawGateSide(8)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(6, 0, 0)
    glRotatef(180, 0, 1, 0)
    drawGateSide(-8)
    glPopMatrix()


#  TREE 

def drawTree(x, z, scale=1.0):
    glPushMatrix()
    glTranslatef(x, -2.0, z)
    glScalef(scale, scale, scale)

    glColor3f(0.40, 0.24, 0.08)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    drawCylinder(0.24, 0.16, 4.0, 10)
    glPopMatrix()

    glColor3f(0.14, 0.58, 0.16)
    for (fy, fr) in ((3.5, 2.4), (4.8, 1.9), (5.9, 1.35)):
        glPushMatrix()
        glTranslatef(0, fy, 0)
        drawSphere(fr, 14, 14)
        glPopMatrix()

    glPopMatrix()


#  TELEGRAPH POLE

def drawPole(x, z):
    glPushMatrix()
    glTranslatef(x, -2.0, z)
    glColor3f(0.50, 0.34, 0.14)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    drawCylinder(0.13, 0.09, 7.0, 8)
    glPopMatrix()
    glColor3f(0.46, 0.30, 0.12)
    glPushMatrix()
    glTranslatef(0, 7.0, 0)
    glScalef(0.12, 0.12, 2.5)
    glutSolidCube(1)
    glPopMatrix()
    glColor3f(0.8, 0.8, 0.2)
    for iz in (-0.8, 0.8):
        glPushMatrix()
        glTranslatef(0, 7.1, iz)
        drawSphere(0.11, 6, 6)
        glPopMatrix()
    glPopMatrix()


#  BUILDINGS

def drawBuilding(x, z, w, h, d, r, g, b):
    glColor3f(r, g, b)
    glPushMatrix()
    glTranslatef(x, -2.0 + h/2, z)
    glScalef(w, h, d)
    glutSolidCube(1)
    glPopMatrix()
    glColor3f(r*0.7, g*0.7, b*0.7)
    glPushMatrix()
    glTranslatef(x, -2.0 + h + 0.18, z)
    glScalef(w, 0.35, d)
    glutSolidCube(1)
    glPopMatrix()


#  FOG

def setupFog():
    if fog:
        glEnable(GL_FOG)
        glFogfv(GL_FOG_COLOR, [0.65, 0.82, 0.98, 1.0])
        glFogi(GL_FOG_MODE, GL_EXP2)
        glFogf(GL_FOG_DENSITY, 0.011)
    else:
        glDisable(GL_FOG)


#  DISPLAY

def display():
    glClearColor(0.22, 0.52, 0.92, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(cameraX, cameraY, cameraZ,
              lookX,   lookY,   lookZ,
              0, 1, 0)

    setupFog()
    glShadeModel(GL_SMOOTH)

    drawSky()         
    drawGround()
    drawRoad()
    drawTrack()

    drawBuilding(-55, -42, 8, 14, 7,  0.76, 0.70, 0.62)
    drawBuilding(-42, -40, 6, 10, 6,  0.70, 0.66, 0.58)
    drawBuilding(-65, -44, 7, 18, 8,  0.64, 0.60, 0.56)
    drawBuilding( 50, -42, 9, 12, 7,  0.72, 0.70, 0.63)
    drawBuilding( 65, -44, 6,  8, 6,  0.78, 0.74, 0.66)

    for px in range(-70, 80, 15):
        drawPole(px,  12)
        drawPole(px, -12)

    for (tx, tz, sc) in TREE_DATA:
        drawTree(tx, tz, sc)

    drawGates()
    drawTrain()

    glutSwapBuffers()


#  UPDATE

def update(value):
    global trainPos, wheelRotate, gateAngle

    trainPos    = trainPos + trainSpeed
    wheelRotate = wheelRotate - trainSpeed * 14.0

    if trainPos > 90:
        trainPos = -90

    # gate logic
    if trainPos < GATE_CLOSE_START and trainPos > -90:
        if gateAngle < 0:
            gateAngle = min(gateAngle + 1.6, 0.0)
    elif trainPos > GATE_OPEN_START:
        if gateAngle > -90:
            gateAngle = max(gateAngle - 1.6, -90.0)

    for p in smokeParticles:
        p.update(trainPos)

    for cloud in clouds:
        cloud.update()

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)


#  INPUT

def keyboard(key, x, y):
    global cameraX, cameraY, cameraZ, fog

    if   key == b'w': cameraZ = cameraZ - 1
    elif key == b's': cameraZ = cameraZ + 1
    elif key == b'a': cameraX = cameraX - 1
    elif key == b'd': cameraX = cameraX + 1
    elif key == b'q': cameraY = cameraY + 1
    elif key == b'e': cameraY = cameraY - 1
    elif key == b'f': fog = not fog
    elif key == b'\x1b': exit(0)

    glutPostRedisplay()


def specialKey(key, x, y):
    global lookX, lookY

    if   key == GLUT_KEY_LEFT:  lookX = lookX - 1
    elif key == GLUT_KEY_RIGHT: lookX = lookX + 1
    elif key == GLUT_KEY_UP:    lookY = lookY + 1
    elif key == GLUT_KEY_DOWN:  lookY = lookY - 1

    glutPostRedisplay()


#Mouse Camera Control
mouseDown = False
lastMouseX = 0
lastMouseY = 0

def mouse(button, state, x, y):
    global mouseDown, lastMouseX, lastMouseY

    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            mouseDown = True
            lastMouseX = x
            lastMouseY = y
        else:
            mouseDown = False


def motion(x, y):
    global cameraX, cameraY, lookX, lookY, lastMouseX, lastMouseY

    if mouseDown:
        dx = x - lastMouseX
        dy = y - lastMouseY

        cameraX = cameraX - dx * 0.08
        cameraY = cameraY + dy * 0.08

        lookX = lookX - dx * 0.08
        lookY = lookY + dy * 0.02

        lastMouseX = x
        lastMouseY = y

        glutPostRedisplay()


#  INIT + MAIN

def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1024/720, 0.5, 800)
    glMatrixMode(GL_MODELVIEW)


glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(1024, 720)
glutCreateWindow(b"Advanced 3D Railway Crossing")

init()
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutSpecialFunc(specialKey)
glutMouseFunc(mouse)
glutMotionFunc(motion)
glutTimerFunc(0, update, 0)
glutMainLoop()