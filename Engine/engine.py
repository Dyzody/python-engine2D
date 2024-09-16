import sys
import time
import math
import pygame
import threading

PlayerAccelerationTime = 10
PlayerSpeed = 2
PlayerJump = 1 / 4

#Only for surface collision
#not used for default collision logic
Default_Collision_Buffer = 1

Globalgravity = 1 / 20000
GravityTime = 0.1

Default_Density = 2

WIDTH, HEIGHT = 1000, 500
FPS = 24
pygame.init()
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 200, 0)
BROWN = (150, 75, 0)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Engine")
clock = pygame.time.Clock()

Players = []
Boxes = []
Welds = []

class nil():
    def __init__(self):
        self.nil = []

none = nil()

class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x + other.x, self.y + other.y)
        else:
            raise TypeError("Unsupported operand type. Vector2D can only be added to another Vector2D.")

    def __sub__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x - other.x, self.y - other.y)
        else:
            raise TypeError("Unsupported operand type. Vector2D can only be subtracted from another Vector2D.")

    def __truediv__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x / other.x, self.y / other.y)
        elif isinstance(other, (int, float)):
            return Vector2D(self.x / other, self.y / other)
        else:
            raise TypeError("Unsupported operand type. Vector2D can only be divided element-wise by another Vector2D or a scalar.")

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vector2D(self.x * other, self.y * other)
        else:
            raise TypeError("Unsupported operand type. Vector2D can only be multiplied by a scalar.")

    __rmul__ = __mul__

    def get_length(self):
        return math.sqrt(self.x*self.x + self.y*self.y)
    
    def showInText(self):
        return f"X:{self.x} Y:{self.y}"

    def vectorclamp(self, Vector):
        if Vector.x > 0:
            if self.x > Vector.x:
                self.x = Vector.x
        else:
            if self.x < Vector.x:
                self.x = Vector.x
        if Vector.y > 0:
            if self.y > Vector.y:
                self.y = Vector.y
        else:
            if self.y < Vector.y:
                self.y = Vector.y

    def __eq__(self, other):
        if isinstance(other, Vector2D):
            return self.x == other.x and self.y == other.y
        return False
    
    def __lt__(self, other):
        if isinstance(other, Vector2D):
            return self.get_length() < other.get_length()
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, Vector2D):
            return self.get_length() > other.get_length()
        return NotImplemented

class VectorTween:
    def __init__(self, TweenLength, Object, Attr, InputVector, ResultingVector, TweenStyle):
        self.Object = Object
        self.Attr = Attr
        self.InputVector = InputVector
        self.CurrentVector = InputVector
        self.TweenLength = TweenLength
        self.ResultingVector = ResultingVector
        self.TweenStyle = TweenStyle
        self.steps = 100
        self.currentstep = 0
    def play(self):
        def animate():
            delay = self.TweenLength / self.steps

            for i in range(self.steps):
                t = i / self.steps
                self.currentstep = i+1
                if self.TweenStyle == "Linear":
                    self.linear_interpolation(t)

                setattr(self.Object, self.Attr, self.CurrentVector)
                print(f"Step {i+1}: {self.CurrentVector.showInText()}")

                time.sleep(delay)

        # Create a thread and start the animation
        animation_thread = threading.Thread(target=animate)
        animation_thread.start()

    def linear_interpolation(self, t):
        # Linear interpolation between InputVector and ResultingVector
        self.CurrentVector += (self.ResultingVector - self.InputVector) / self.steps

def normalizeVector(Vector, length):
    current_magnitude = math.sqrt(Vector.x**2 + Vector.y**2)
        
    if current_magnitude == 0:
        return Vector2D(0, 0)
        
    scale_factor = length / current_magnitude
    normalized_x = Vector.x * scale_factor
    normalized_y = Vector.y * scale_factor
    normalized_vector = Vector2D(normalized_x, normalized_y)
    return normalized_vector

def getaverageVector(Vec1, Vec2):
    averageX = (Vec1.x + Vec2.x)/2
    averageY = (Vec1.y + Vec2.y)/2

    averageVector = Vector2D(averageX, averageY)
    return averageVector

#vec1 = Vector2D(10, 0)
#vec2 = Vector2D(1, 1)
#print(normalizeVector(vec1, 10).showInText())
#print(normalizeVector(vec2, 1).showInText())

class mouse:
    def __init__(self):
        self.initialized = True
        #Relative Position
        self.pos = Vector2D(0, 0)
        #Real Position
        self.truepos = Vector2D(0, 0)
        self.movementdifference = Vector2D(0, 0)
        self.LeftDown = False
        self.RightDown = False

        self.LeftPos1 = Vector2D(0,0)
        self.LeftPos2 = Vector2D(0, 0)
        self.RightPos1 = Vector2D(0,0)
        self.RightPos2 = Vector2D(0,0)

playermouse = mouse()
cameraOffset = Vector2D(0,0)

class Box:
    def getSize(self):
        return self.size.x * self.size.y
    def __init__(self, Name, Density, RespectGravity, CanCollide, Moveable, Color, pos, size, priority, IgnoreBorderX, IgnoreBorderY, Visible):
        self.Name = Name
        self.RespectGravity = RespectGravity
        self.CanCollide = CanCollide
        self.IgnoreBorderX = IgnoreBorderX
        self.IgnoreBorderY = IgnoreBorderY
        self.Moveable = Moveable
        self.Color = Color
        self.pos = pos
        self.weldoffset = Vector2D(0, 0)
        self.size = size
        self.Density = Density
        self.Mass = self.getSize() * Density
        self.grounded = False
        self.groundObject = none
        self.accel = Vector2D(0, 0)
        self.Force = 0
        self.Colliders = []
        self.SurfaceColliders = []
        self.CanAccelerate = True
        self.Visible = Visible
        Boxes.insert(priority, self)
    def changePriority(self, priority):
        Boxes.remove(self)
        Boxes.insert(self, priority)
    def setMass(self, Mass):
        sz = self.getSize()
        Density = Mass/sz
        self.Density = Density
        self.Mass = self.getSize()*Density
    def Logic(self):
        self.Force = self.Mass * self.accel.get_length()

def quickbox(pos, size, gravity, collision, Visible):
    return Box("QuickBox", Default_Density, gravity, collision, True, BLUE, pos, size, 1, True, False, Visible)

class Weld:
        def __init__(self, Obj1, Obj2):
            Welds.insert(1, self)
            self.Obj1 = Obj1
            self.Obj2 = Obj2
        def main(self):
            vec = Vector2D(self.Obj1.pos.x + self.Obj2.weldoffset.x, 
                           self.Obj1.pos.y - self.Obj2.weldoffset.y)
            self.Obj2.pos = vec
        
class Player:
        def __init__(self, Name, PlrBox, maxhealth, health, left, right, up, down):
            Players.insert(1, self)
            #self.OwnBox = Box(Name=Name,RespectGravity=RespectGravity, CanCollide=CanCollide, Moveable=Moveable, Color=Color, 
            #                pos=pos, size=size, priority=priority, IgnoreBorderX=IgnoreBorderX, IgnoreBorderY=IgnoreBorderY)
            self.Name = Name
            self.OwnBox = PlrBox
            self.maxhealth = maxhealth
            self.health = health
            self.left = left
            self.right = right
            self.up = up
            self.down = down
            self.grounded = False
            self.modifiedspeed = PlayerSpeed

        def main(self):
            keys = pygame.key.get_pressed()
            self.OwnBox.accel.x = 0
            
            if not self.OwnBox.RespectGravity:
                self.OwnBox.accel.y = 0

            #print(pygame.K_a)

            if keys[self.up] and self.OwnBox.grounded and self.OwnBox.RespectGravity:
                self.OwnBox.accel.y = PlayerJump
                #print("Jump")
                #print(f"Y acceleration = {Player.accel.y}")
            if keys[self.up] and self.OwnBox.accel.y <= PlayerSpeed and not self.OwnBox.RespectGravity:
                self.OwnBox.accel.y += PlayerSpeed/PlayerAccelerationTime
                #print("Up")
            if keys[self.left] and self.OwnBox.accel.x >= -PlayerSpeed:
                self.OwnBox.accel.x -= PlayerSpeed/PlayerAccelerationTime
                #print("Left")
            if keys[self.right] and self.OwnBox.accel.x <= PlayerSpeed:
                self.OwnBox.accel.x += PlayerSpeed/PlayerAccelerationTime
                #print("Right")
            if keys[self.down] and self.OwnBox.accel.y >= -PlayerSpeed and not self.OwnBox.RespectGravity:
                self.OwnBox.accel.y -= PlayerSpeed/PlayerAccelerationTime 
                #print("Down")
                #accelerate(Player, PlayerSpeed, 0, 1)
            
            #normalize movement Vector to adjust diagonal speed
            #only if player doesn't care for gravity
            
            #print(self.OwnBox.accel.showInText())

            if not self.OwnBox.RespectGravity:
                #print(normalizeVector(self.OwnBox.accel, 0.1).showInText())
                self.OwnBox.accel = normalizeVector(self.OwnBox.accel, PlayerSpeed/PlayerAccelerationTime)

            #print("Listening to input: Player1")
                
class collection():
    def autoweld(self):
        for current in self.otherboxes:
            print(f"Welding {self.primarybox.Name} to {current.Name}")
            Weld(self.primarybox, current)
    def __init__(self, primarybox, otherboxes, weldnow):
        self.primarybox = primarybox
        self.otherboxes = otherboxes

        if weldnow:
            self.autoweld()

def IsColliding(Object, Collider, Buffer):
    if Object == Collider:
        return False

    return (
        (Object.pos.x < Collider.pos.x + Collider.size.x + Buffer) and
        (Object.pos.x + Object.size.x > Collider.pos.x - Buffer) and
        (Object.pos.y < Collider.pos.y + Collider.size.y + Buffer) and
        (Object.pos.y + Object.size.y > Collider.pos.y - Buffer)
    )

def GetCollidingRectangles(Rec, IgnoreCanCollide, Buffer):
    returnRects = []

    for BoxObject in Boxes:
        if BoxObject != Rec:
            if IsColliding(Rec, BoxObject, Buffer) and IgnoreCanCollide:
                returnRects.insert(1, BoxObject)
            elif IsColliding(Rec, BoxObject, Buffer) and Rec.CanCollide and BoxObject.CanCollide:
                returnRects.insert(1, BoxObject)
    
    return returnRects

def HandleCollision(Object):
    Colliders = GetCollidingRectangles(Object, False, 0)
    SurfaceColliders = GetCollidingRectangles(Object, False, Default_Collision_Buffer)
    #for cll in Colliders:
        #print(f"{Object.Name} is colliding with {cll.Name}!")
    
    Object.Colliders = Colliders
    Object.SurfaceColliders = SurfaceColliders

    for Collider in Colliders:
        if Object != Collider:
            
            #top / bottom of the collider

            from_top = (Object.pos.y + Object.size.y - 1 <= Collider.pos.y + abs(Object.accel.y))
            from_bottom = (Object.pos.y - 1 >= Collider.pos.y + Collider.size.y - abs(Object.accel.y))
            #from_left = (Object.pos.x + Object.size.x <= Collider.pos.x + abs(Object.accel.x))
            #from_right = (Object.pos.x >= Collider.pos.x + Collider.size.x - abs(Object.accel.x))

            if from_top:
                if Object.Moveable:
                    Object.pos.y = Collider.pos.y - Object.size.y
                else:
                    Collider.pos.y += 1
                Object.groundObject = Collider
                Object.grounded = True
                Collider.accely = 0

            elif from_bottom:
                if Object.Moveable:
                    Object.pos.y = Collider.pos.y + Collider.size.y
                    Collider.pos += Object.accel
                else:
                    print("Not Moveable2")
                Object.accel = Vector2D(0, 0)
            else:
                if Object.Moveable:
                    Object.pos -= Object.accel
                Object.accel = Vector2D(0, 0)

def BoxFrom2Mousepos(pos1, pos2):
    box_pos = (pos1 + pos2) / Vector2D(2, 2)
    box_size = Vector2D(abs(pos2.x - pos1.x), abs(pos2.y - pos1.y))
    
    Box(Name="MouseBox", Density=Default_Density, RespectGravity=True,
        CanCollide=True, Moveable=True, Color=BLUE, pos=box_pos, size=box_size, priority=1, IgnoreBorderX=True, IgnoreBorderY=False)

def BoxToScreen(BoxToDraw):
    NewDraw = pygame.draw.rect(screen, BoxToDraw.Color, (BoxToDraw.pos.x + cameraOffset.x, BoxToDraw.pos.y+cameraOffset.y, 
        BoxToDraw.size.x, BoxToDraw.size.y))
    return NewDraw

def Render():
    screen.fill(BLACK)
    for BoxToDraw in Boxes:
        HandleCollision(BoxToDraw)
        
        if not BoxToDraw.Visible:
            continue
        BoxToScreen(BoxToDraw=BoxToDraw)
        

    pygame.display.flip()

def exit():
    pygame.quit()
    sys.exit()


#Player_1 = Player(Name="Plr1", RespectGravity=False,CanCollide=True, Moveable=True, Color=BLUE,
#                   pos=Vector2D(10, 500), size=Vector2D(40, 20), priority=1, maxhealth=100, health=100,
#                    left=pygame.K_LEFT, right=pygame.K_RIGHT, up=pygame.K_UP, down=pygame.K_DOWN, IgnoreBorderX=True, IgnoreBorderY=True)

#Player_2 = Player(Name="Plr2", RespectGravity=True, CanCollide=True, Moveable=True, Color=BLUE,
#                     pos=Vector2D(100, 500), size=Vector2D(10, 20), priority=1, maxhealth=100, health=100,
#                     left=pygame.K_a, right=pygame.K_d, up=pygame.K_SPACE, down=pygame.K_s, IgnoreBorderX=True, IgnoreBorderY=False)


Plr1Box = Box(Name="Player1",Density=Default_Density, RespectGravity=False, CanCollide=True, Moveable=True, Color=BLUE,
              pos=Vector2D(10, 400), size=Vector2D(40, 20), priority=1, IgnoreBorderX=True, IgnoreBorderY=True, Visible=True)
Plr2Box = Box(Name="Player2",Density=Default_Density, RespectGravity=True, CanCollide=True, Moveable=True, Color=BLUE,
              pos=Vector2D(100, 500), size=Vector2D(10, 20), priority=1, IgnoreBorderX=True, IgnoreBorderY=False, Visible=True)

Plr2Head = Box(Name="Player2Head",Density=0, RespectGravity=True, CanCollide=True, Moveable=True, Color=BLUE,
              pos=Vector2D(0, 0), size=Vector2D(20, 5), priority=1, IgnoreBorderX=False, IgnoreBorderY=False, Visible=True)

Plr2Head.weldoffset = Vector2D(-5, 10)

tweenbox1 = quickbox(pos=Plr2Box.pos - Vector2D(0, 100), size=Vector2D(10, 10), gravity=False, collision=False, Visible=True)

VectorTween(1, tweenbox1, "pos", tweenbox1.pos, tweenbox1.pos + Vector2D(100, -100), "Linear").play()
#VectorTween(10, tweenbox3, "pos", tweenbox3.pos, tweenbox3.pos + Vector2D(100, 0), "SlowDown").play()

#Neck = Weld(Plr2Box, Plr2Head)

Player2Col = collection(Plr2Box, [Plr2Head], True)

Player_1 = Player(Name="Player1", PlrBox=Plr1Box, health=100, maxhealth=100, 
                  left=pygame.K_LEFT, right=pygame.K_RIGHT, up=pygame.K_UP, down=pygame.K_DOWN)
Player_2 = Player(Name="Player2", PlrBox=Plr2Box, health=100, maxhealth=100, 
                 left=pygame.K_a, right=pygame.K_d, up=pygame.K_SPACE, down=pygame.K_s)


#Obstacle = Box("Box1", True, True, True, WHITE, Vector2D(450, 600), Vector2D(100, 40), 2, True, False)
Obstacle = Box(Name="Box1", Density=Default_Density, RespectGravity=True, CanCollide=True, Moveable=True, Color=WHITE, 
               pos=Vector2D(450, 400), size=Vector2D(100, 40), priority=1, IgnoreBorderX=False, IgnoreBorderY=False, Visible=True)
Obstacle2 = Box("Box2", Default_Density, True, True, True, WHITE, Vector2D(100, 200), Vector2D(50, 55), 4, False, False, True)



isRunning = True

while isRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
        elif event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            MVect = Vector2D(x, y)
            playermouse.movementdifference = playermouse.pos-MVect
            playermouse.pos = MVect
            playermouse.truepos = playermouse.pos-cameraOffset
            #print(f"Mouse Movement dif {playermouse.movementdifference.showInText()}")
            #print(f"Mouse moved to {MVect.showInText()}")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            playermouse.LeftDown = True
            playermouse.LeftPos1 = playermouse.pos
            playermouse.LeftPos1T = playermouse.truepos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            playermouse.LeftDown = False
            playermouse.LeftPos2 = playermouse.pos
            playermouse.LeftPos2T = playermouse.truepos
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            playermouse.RightDown = True
            playermouse.RightPos1 = playermouse.pos
            playermouse.RightPos1T = playermouse.truepos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            playermouse.RightDown = False
            playermouse.RightPos2 = playermouse.pos
            playermouse.RightPos2T = playermouse.truepos
            BoxFrom2Mousepos(playermouse.RightPos1T, playermouse.RightPos2T)


    if playermouse.LeftDown:
        cameraOffset.x -= playermouse.movementdifference.x * 0.8
        playermouse.movementdifference.x = 0
        #print(f"offset {cameraOffset.showInText()}")

    #print(f"Plr1: {Player_1.OwnBox.accel.showInText()}")
    #print(f"Plr2: {Player_2.OwnBox.accel.showInText()}")

    for CurrentPlayer in Players:
        CurrentPlayer.main()
        HandleCollision(CurrentPlayer.OwnBox)
        #print(CurrentPlayer.Name)
        #HandleCollision(CurrentPlayer.OwnBox)
        #print(f"Acceleration X = {CurrentPlayer.OwnBox.accel.x}, Acceleration Y = {CurrentPlayer.OwnBox.accel.y}")
        #print(CurrentPlayer.OwnBox.accel.y)
        #print(f"X: {CurrentPlayer.OwnBox.pos.x} Y: {CurrentPlayer.OwnBox.pos.y}")
        #print(CurrentPlayer.OwnBox.grounded)
        #print(CurrentPlayer.OwnBox.groundObject)
        #print(f"{CurrentPlayer.OwnBox.Name} is colliding with {Cll.Name}!")

    #for Cll in Player_2.OwnBox.Colliders:
        
        #if Cll == Player_2.OwnBox: continue
        #Cll.Color = BROWN
        #print(Cll.Name)

    #for collider in Player_2.OwnBox.SurfaceColliders:
        #print(collider.Name)
        #collider.Color = GREEN

    for boxob in Boxes:
        boxob.Color = WHITE
        boxob.Logic()
        #print(f"{boxob.Name} | {boxob.Force}")

    for collider in Player_2.OwnBox.SurfaceColliders:
        #print(collider.Name)
        collider.Color = GREEN

    #if IsColliding(Player_2.OwnBox, Obstacle2, Default_Collision_Buffer):
    #    Obstacle2.Color = BROWN
    #else:
    #    Obstacle2.Color = WHITE

    for BoxObject in Boxes:
        if BoxObject.RespectGravity and BoxObject.Moveable:
           if not BoxObject.grounded:
                BoxObject.accel.y -= Globalgravity/GravityTime
                #print(f"Pulling Down {BoxObject}!")
           elif BoxObject.grounded and BoxObject.accel.y < 0:
                BoxObject.accel.y = 0
           #print(BoxObject.grounded)
        
        if BoxObject.Moveable:
            BoxObject.pos.y -= BoxObject.accel.y
            BoxObject.pos.x += BoxObject.accel.x

    for BoxObject in Boxes:
        
        if not BoxObject.IgnoreBorderX:
            BoxObject.pos.x = max(0, min(WIDTH - BoxObject.size.x, BoxObject.pos.x))
        
        if not BoxObject.IgnoreBorderY:
            BoxObject.pos.y = max(0, min(HEIGHT - BoxObject.size.y, BoxObject.pos.y))
        
        if BoxObject.pos.y >= HEIGHT-BoxObject.size.y:
            if not BoxObject.IgnoreBorderY:
                BoxObject.grounded = True
            #print("Grounded")
        else:
            BoxObject.grounded = False
            BoxObject.groundObject = none

        #print(f"{BoxObject.Name} = X: {BoxObject.pos.x} | Y: {BoxObject.pos.y}")
        
    for current_weld in Welds:
        current_weld.main()

    Render()

exit()