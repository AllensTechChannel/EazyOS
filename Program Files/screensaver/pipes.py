import tkinter
import random

class RandomBall():
    '''
    The class that defines the ball in motion

    '''
    def __init__(self, canvas, scrnwidth, scrnheight):
        self.canvas = canvas
#     '''
#          canvas: canvas, all content should be presented on the canvas, here is passed in through this variable
#          scrnwidth/scrnheight screen width and height
#     '''
    
        #  The position where the ball appears is random, where the position indicates the center of the circle
        #  xpos represents the x coordinate of the position
        self.xpos = random.randint(10, int(scrnwidth)-20)
        #  ypos represents the y coordinate of the position
        self.ypos = random.randint(10, int(scrnheight)-20)


        #  Define the speed of the ball
        #  Simulate movement: constantly erase the original painting, and then repaint it in a new place
        #  Here xvelocity simulates movement in the x-axis direction
        self.xvelocity = random.randint(4,12)
        #  Similarly, the yvelocity simulation is movement in the y-axis direction
        self.yvelocity = random.randint(4,12)

        #  Define the size of the screen
        self.scrnwidth = scrnwidth
        #  Define the height of the screen
        self.scrnheight = scrnheight

        #  Random ball size
        #  The size of the ball here is expressed by radius
        self.radius = random.randint(20,120)

        #  Define color
        #  RGB notation: three numbers, the value of each number is between 0-255, indicating the size of the three colors of red, green and blue
        #  In some systems, English words can also be used between them, such as red, green
        #  Use lambda expressions here
        c = lambda : random.randint(0, 255)
        self.color = '#%02x%02x%02x'%(c(), c(), c())
    
    def create_ball(self):
        '''
                 Use the variable value defined by the constructor to draw a ball on the canvas
        '''
        #tkinter does not draw a circle function
        #  There is only one function for drawing an ellipse, two coordinates need to be defined to draw an ellipse
        #  To draw an ellipse inside the rectangle, we only need to define the upper left corner and the lower right corner of the rectangle.
        #  The method of the two coordinates of the sphere is, if the coordinates of the center of the circle are known, the coordinates of the center of the circle can be obtained by subtracting the radius
        #  The coordinates of the center of the circle plus the radius can find the coordinates of the lower right corner
        x1 = self.xpos - self.radius
        y1 = self.ypos - self.radius
        x2 = self.xpos + self.radius
        y2 = self.ypos + self.radius
        
        #  If there are two more object coordinates, you can draw a circle
        #  fill represents the fill color
        #  outline represents the outer border color
        self.item = self.canvas.create_oval(x1, y1, x2, y2, \
                                           fill = self.color, \
                                           outline = self.color)
    def move_ball(self):
        #  Need to control the ball when moving the ball
        #  After each movement, the ball has a new coordinate
        self.xpos += self.xvelocity
        self.ypos += self.yvelocity
        #  Or self.xpos *= -1
        
        #  Then determine whether to hit the wall
        #  You have to look back when you hit the wall
        #  Algorithm judgment after hitting the wall
        if self.xpos + self.radius >= self.scrnwidth or \
        self.xpos - self.radius <= 0:
            self.xvelocity = -self.xvelocity
        if self.ypos + self.radius >= self.scrnheight or \
        self.ypos - self.radius <= 0:
            self.yvelocity = -self.yvelocity
            
        #Move the picture on the canvas
        self.canvas.move(self.item, self.xvelocity, self.yvelocity)
    
    
    

class ScreenSaver():
    '''
         Define the class of the screensaver
         Can be activated
    '''
    #  Define randomly generated balls?
    
    
    def __init__(self):
        self.balls = []
        #  Random number of balls each time
        self.num_balls = random.randint(6, 20)
        
        self.root = tkinter.Tk()
        #  Cancel border
        self.root.overrideredirect(1)
        #  Make a transparent window
        self.root.attributes('-alpha', 0.3)
        
        #  Any mouse movement needs to be popular
        self.root.bind('<Motion>', self.myquit)
        #  Press any keyboard to exit the screen saver
        self.root.bind('<Key>', self.myquit)
        #  Get screen size specifications
        w,h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        
        #  Create the canvas, including the ownership and specifications of the canvas
        self.canvas = tkinter.Canvas(self.root, width=w, height=h)
        self.canvas.pack()
        
        #  Draw ball on canvas
        for i in range(self.num_balls):
            ball = RandomBall(self.canvas, scrnwidth=w, scrnheight=h)
            ball.create_ball()
            self.balls.append(ball)
            
        self.run_screen_saver()
        self.root.mainloop()
        
    def run_screen_saver(self):
        for ball in self.balls:
            ball.move_ball()
            
            #after is to start a function after 200 milliseconds, the function to be started is the second parameter
        self.canvas.after(50,self.run_screen_saver)
    
    def myquit(self, e):
        #  Here is just a processing mechanism that uses time
        #  Don't actually care about the type of time
        self.root.destroy()
            
            
            
if __name__=="__main__":
    ScreenSaver()