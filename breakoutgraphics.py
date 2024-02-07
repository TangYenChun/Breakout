"""
stanCode Breakout Project
Adapted from Eric Roberts's Breakout by
Sonja Johnson-Yu, Kylie Jue, Nick Bowman, 
and Jerry Liao.
"""
from campy.graphics.gwindow import GWindow
from campy.graphics.gobjects import GOval, GRect, GLabel
from campy.gui.events.mouse import onmouseclicked, onmousemoved
import random

BRICK_SPACING = 5      # Space between bricks (in pixels). This space is used for horizontal and vertical spacing
BRICK_WIDTH = 40       # Width of a brick (in pixels)
BRICK_HEIGHT = 15      # Height of a brick (in pixels)
BRICK_ROWS = 10        # Number of rows of bricks
BRICK_COLS = 10        # Number of columns of bricks
BRICK_OFFSET = 50      # Vertical offset of the topmost brick from the window top (in pixels)
BALL_RADIUS = 10       # Radius of the ball (in pixels)
PADDLE_WIDTH = 75      # Width of the paddle (in pixels)
PADDLE_HEIGHT = 15     # Height of the paddle (in pixels)
PADDLE_OFFSET = 50     # Vertical offset of the paddle from the window bottom (in pixels)
INITIAL_Y_SPEED = 7    # Initial vertical speed for the ball
MAX_X_SPEED = 5        # Maximum initial horizontal speed for the ball


class BreakoutGraphics:
    """
    This class handle breakout graphics.
    """
    def __init__(self, ball_radius=BALL_RADIUS, paddle_width=PADDLE_WIDTH, paddle_height=PADDLE_HEIGHT,
                 paddle_offset=PADDLE_OFFSET, brick_rows=BRICK_ROWS, brick_cols=BRICK_COLS, brick_width=BRICK_WIDTH,
                 brick_height=BRICK_HEIGHT, brick_offset=BRICK_OFFSET, brick_spacing=BRICK_SPACING, title='Breakout'):
        """
        Initialize the breakout graphics, to create a graphical window, a paddle,
        a ball at the center of the window, and bricks.

        All parameters can also be specified, but will default to reasonable values.

        :param ball_radius: Radius of the ball (in pixels)
        :param paddle_width: Width of the paddle (in pixels)
        :param paddle_height: Height of the paddle (in pixels)
        :param paddle_offset: Vertical offset of the paddle from the window bottom (in pixels)
        :param brick_rows: Number of rows of bricks
        :param brick_cols: Number of columns of bricks
        :param brick_width: Width of a brick (in pixels)
        :param brick_height: Height of a brick (in pixels)
        :param brick_offset: Vertical offset of the topmost brick from the window top (in pixels)
        :param brick_spacing: Space between bricks (in pixels). This space is used for horizontal and vertical spacing
        :param title: The title of the window
        """
        self.__is_ball_moving = False
        self.__remove_bricks_count = 0

        # Create a graphical window, with some extra space
        window_width = brick_cols * (brick_width + brick_spacing) - brick_spacing
        window_height = brick_offset + 3 * (brick_rows * (brick_height + brick_spacing) - brick_spacing)
        self.window = GWindow(width=window_width, height=window_height, title=title)

        # Create a paddle
        grey = '#999999'
        self.paddle = GRect(paddle_width, paddle_height)
        self.paddle.filled = True
        self.paddle.fill_color = grey
        self.paddle.color = grey
        paddle_x = (self.window.width-self.paddle.width)/2
        paddle_y = self.window.height-(self.paddle.height+paddle_offset)
        self.window.add(self.paddle, x=paddle_x, y=paddle_y)

        # Default initial velocity for the ball
        self.__dx = 0
        self.__dy = 0

        # Center a filled ball in the graphical window
        self.ball = GOval(ball_radius*2, ball_radius*2)
        self.init_ball()
        self.ball.filled = True
        self.ball.fill_color = grey
        self.ball.color = grey
        self.window.add(self.ball)

        # Initialize our mouse listeners
        onmouseclicked(self.__handle_click)
        onmousemoved(self.__handle_paddle)

        # Draw bricks
        self.__brick_rows = brick_rows
        self.__brick_cols = brick_cols
        self.__draw_bricks(brick_width, brick_height, brick_offset, brick_spacing)

    def init_ball(self):
        """
        Initialize the movement state, position, and velocity of the ball.
        """
        self.__is_ball_moving = False
        self.ball.x = (self.window.width - self.ball.width) / 2
        self.ball.y = (self.window.height - self.ball.height) / 2
        self.__dx = 0
        self.__dy = 0

    def get_dx(self):
        """
        The getter of the dx attribute
        :return: x velocity
        """
        return self.__dx

    def get_dy(self):
        """
        The getter of the dy attribute
        :return: y velocity
        """
        return self.__dy

    def handle_ball_hit_obj(self):
        """
        This method is called every single loop, it will check if the ball touched the object,
        and call method: __handle_ball_hit to Handle the ball hit the object.
        """
        obj_arr = []

        # Get the objects touched by the four corners of the ball.
        for i in range(2):
            x = self.ball.x
            if i == 1:
                x += self.ball.width

            for j in range(2):
                y = self.ball.y
                if j == 1:
                    y += self.ball.height
                obj = self.window.get_object_at(x, y)
                obj_arr.append(obj)

        # Handle the ball hit the object.
        for obj in obj_arr:
            if obj is not None:
                self.__handle_ball_hit(obj)
                break

    def __handle_ball_hit(self, obj):
        """
        Handle the ball hit the object.
        if the ball hit the brick, the brick will be disappeared, and the ball will bounce back.
        if the ball hit the paddle, the ball will bounce back.
        :param obj: Can not be None. The object touched by the ball.
        """
        if obj == self.paddle:
            if self.__dy > 0:
                # The ball hides the left or right side of paddle.
                if self.ball.x + self.ball.width <= self.paddle.x or self.ball.x >= self.paddle.x + self.paddle.width:
                    self.change_x_direction()
                else:
                    self.change_y_direction()
        else:
            self.window.remove(obj)
            self.__remove_bricks_count += 1
            self.change_y_direction()

    def is_ball_leaves_window(self):
        """
        Check if the ball leaves the bottom of the window.
        :return: True if the ball leaves the bottom of the window, False is not.
        """
        return self.ball.y >= self.window.height

    def is_game_win(self):
        """
        Check if the user win the game.
        The winning condition is that when the user remove all the bricks.
        :return: True if the user win the game, False is not.
        """
        return self.__remove_bricks_count == self.__brick_rows * self.__brick_cols

    def is_ball_on_x_side(self):
        """
        Check if the ball on the right or left side of the window.
        :return: True if the ball on the right or left side of the window, False is not.
        """
        return self.ball.x <= 0 or self.ball.x + self.ball.width >= self.window.width

    def is_ball_on_y_side(self):
        """
        Check if the ball on the top of the window.
        :return: True if the ball on the top of the window, False is not.
        """
        return self.ball.y <= 0

    def change_x_direction(self):
        """
        Change the x direction of the ball.
        """
        self.__dx = -self.__dx

    def change_y_direction(self):
        """
        Change the y direction of the ball.
        """
        self.__dy = -self.__dy

    def __handle_click(self, event):
        """
        Handle the mouse click.
        if the ball is not moving, the method will be executed.
        This method set the random velocity within the reasonable range of the ball.
        :param event: mouse click event
        """
        if not self.__is_ball_moving:
            self.__is_ball_moving = True
            self.__dy = INITIAL_Y_SPEED
            self.__dx = random.randint(1, MAX_X_SPEED)
            if random.random() > 0.5:
                self.__dx = -self.__dx

    def __handle_paddle(self, event):
        """
        Handle the moving of the paddle.
        Let the paddle move horizontally with the mouse position, ensuring it does not move out of the window.
        :param event: mouse move event
        """
        self.paddle.x = event.x - self.paddle.width/2

        # If mouse out of the window.
        if self.paddle.x <= 0:
            self.paddle.x = 0
        elif self.paddle.x + self.paddle.width >= self.window.width:
            self.paddle.x = self.window.width-self.paddle.width

    def __draw_bricks(self, width, height, offset, spacing):
        """
        Draw bricks in the window.

        :param width: Width of a brick
        :param height: Height of a brick
        :param offset: Vertical offset of the topmost brick from the window top
        :param spacing: Space between bricks. This space is used for horizontal and vertical spacing
        """
        brick = None
        color_arr = ['#f28179', '#f2f279', '#99f279', '#79d6f2', '#b697f0']
        for i in range(self.__brick_rows):
            # Each two rows of bricks use the same color.
            color = color_arr[int(i / 2)]
            # Get the y position of current brick.
            if i == 0:
                brick_y = offset
            else:
                brick_y = brick.y + brick.height + spacing

            for j in range(self.__brick_cols):
                # Get the x position of current brick.
                if j == 0:
                    brick_x = 0
                else:
                    brick_x = brick.x + brick.width + spacing
                # Create a brick, and add it into the window.
                brick = GRect(width, height, x=brick_x, y=brick_y)
                brick.filled = True
                brick.fill_color = color
                brick.color = color
                self.window.add(brick)
