"""
stanCode Breakout Project
Adapted from Eric Roberts's Breakout by
Sonja Johnson-Yu, Kylie Jue, Nick Bowman, 
and Jerry Liao.

This program, based on the brick-breaking game, has added a scoreboard, lives on the window.
In addition to regular bricks, red bricks have also been added.
If the ball touch the red bricks, score will be added 5, and the special event will occur.
If the count of removed bricks is multiples of 3, then add the block paddle in the window,
or reset the position and horizontal speed of the block paddle.
"""
from campy.graphics.gwindow import GWindow
from campy.graphics.gobjects import GOval, GRect, GLabel
from campy.graphics.gimage import GImage
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
BLOCK_PADDLE_MAX_DX = 8  # Maximum horizontal speed of the block paddle


class BreakoutGraphics:
    """
    This class handle breakout graphics.
    """
    def __init__(self, ball_radius=BALL_RADIUS, paddle_width=PADDLE_WIDTH, paddle_height=PADDLE_HEIGHT,
                 paddle_offset=PADDLE_OFFSET, brick_rows=BRICK_ROWS, brick_cols=BRICK_COLS, brick_width=BRICK_WIDTH,
                 brick_height=BRICK_HEIGHT, brick_offset=BRICK_OFFSET, brick_spacing=BRICK_SPACING, title='Breakout',
                 lives=3):
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
        self.paddle = None
        self.paddle_offset = paddle_offset
        self.__create_paddle(paddle_width, paddle_height)

        # Default initial velocity for the ball
        self.__dx = 0
        self.__dy = 0

        # Center a filled ball in the graphical window
        self.ball = GOval(ball_radius*2, ball_radius*2)
        self.init_ball()
        self.ball.filled = True
        self.window.add(self.ball)

        # Initialize our mouse listeners
        onmouseclicked(self.__handle_click)
        onmousemoved(self.__handle_paddle)

        # Draw bricks
        self.red_bricks = []
        self.brick_width = brick_width
        self.brick_height = brick_height
        self.brick_offset = brick_offset
        self.brick_spacing = brick_spacing
        self.__brick_rows = brick_rows
        self.__brick_cols = brick_cols
        self.__draw_bricks()

        # Draw the scoreboard
        self.__score = 0
        self.scoreboard = GLabel(f'Score: {self.__score}')
        self.scoreboard.font = 'Helvetica-18-bold'
        self.window.add(self.scoreboard, x=10, y=self.window.height-5)

        # Create lives
        self.lives_arr = []
        self.__init_lives(lives)

        # Create block paddle
        self.block_paddle = GRect(paddle_width, paddle_height)
        self.block_paddle.filled = True
        self.block_paddle.fill_color = 'green'
        self.block_paddle.color = 'green'
        self.__block_paddle_dx = 0

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

    def is_block_paddle_need_turn_around(self):
        """
        Check if the block paddle is on the right or left side of the window.
        :return: (Bool) True is the block paddle need to turn around, False is not.
        """
        return self.block_paddle.x <= 0 or self.block_paddle.x + self.block_paddle.width >= self.window.width

    def change_block_paddle_dy(self):
        """
        Change the horizontal speed of the block paddle.
        """
        self.__block_paddle_dx = -self.__block_paddle_dx

    def get_block_paddle_dx(self):
        """
        The getter of the block_paddle_dx attribute.
        :return: The horizontal speed of the block paddle.
        """
        return self.__block_paddle_dx

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
                y = self.ball.y if j == 0 else self.ball.y + self.ball.height
                obj = self.window.get_object_at(x, y)
                obj_arr.append(obj)

        # Handle the ball hit the object.
        for index, obj in enumerate(obj_arr):
            if obj is not None and not self.__is_scoreboard_or_lives(obj):
                self.__handle_ball_hit(index, obj)
                break

    def is_ball_leaves_window(self):
        """
        Check if the ball leaves the bottom of the window.
        :return: (Bool) True if the ball leaves the bottom of the window, False is not.
        """
        return self.ball.y >= self.window.height

    def is_game_win(self):
        """
        Check if the user win the game.
        The winning condition is that when the user remove all the bricks.
        :return: (Bool) True if the user win the game, False is not.
        """
        return self.__remove_bricks_count == self.__brick_rows * self.__brick_cols

    def is_ball_on_x_side(self):
        """
        Check if the ball on the right or left side of the window.
        :return: (Bool) True if the ball on the right or left side of the window, False is not.
        """
        return self.ball.x <= 0 or self.ball.x + self.ball.width >= self.window.width

    def is_ball_on_y_side(self):
        """
        Check if the ball on the top of the window.
        :return: (Bool) True if the ball on the top of the window, False is not.
        """
        return self.ball.y <= 0

    def show_game_result(self, is_win):
        """
        Show the game result in the window.
        :param is_win: (Bool) True is the user win the game, False is user lose the game.
        """
        self.window.remove(self.ball)

        bgc = GRect(self.window.width / 2, 100)
        bgc.filled = True
        result_text = GLabel('You Win !!')
        result_text.font = 'Helvetica-18-bold'
        if is_win:
            bgc.fill_color = 'yellow'
            bgc.color = 'yellow'
        else:
            bgc.fill_color = 'blue'
            bgc.color = 'blue'
            result_text.text = 'Game over !'
            result_text.color = 'white'

        self.window.add(bgc, x=(self.window.width - bgc.width) / 2, y=(self.window.height - bgc.height) / 2)
        self.window.add(result_text, x=(self.window.width - result_text.width) / 2,
                        y=(self.window.height + result_text.height) / 2 + 5)

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

    def remove_a_live(self, lives):
        """
        Replace the solid heart with a hollow heart in the window.
        :param lives: (int) Current lives.
        """
        heart_removed = GImage('image/heart_removed.png')
        heart = self.lives_arr[lives]
        self.window.add(heart_removed, x=heart.x, y=heart.y)
        self.window.remove(heart)
        self.lives_arr[lives] = heart_removed

    def __create_paddle(self, paddle_width, paddle_height):
        """
        Create a paddle in the window.
        :param paddle_width: Width of the paddle. (in pixel)
        :param paddle_height: Height of the paddle. (in pixel)
        """
        self.paddle = GRect(paddle_width, paddle_height)
        self.paddle.filled = True
        paddle_x = (self.window.width - self.paddle.width) / 2
        paddle_y = self.window.height - (self.paddle.height + self.paddle_offset)
        self.window.add(self.paddle, x=paddle_x, y=paddle_y)

    def __init_lives(self, lives):
        """
        To Add picture of lives in the window.
        :param lives: The initial lives of the game.
        """
        spacing = 10

        for i in range(lives):
            heart = GImage('image/heart.png')
            self.window.add(heart, x=self.window.width-(spacing+heart.width)*(i+1),
                            y=self.window.height-(spacing+heart.height))
            self.lives_arr.append(heart)

    def __is_scoreboard_or_lives(self, obj):
        """
        Check object is scoreboard or lives or not.
        :param obj: GObject
        :return: (Bool) True is scoreboard or lives, False is not.
        """
        if obj == self.scoreboard:
            return True
        for heart in self.lives_arr:
            if obj == heart:
                return True
        return False

    def __handle_ball_hit(self, index, obj):
        """
        Handle the ball hit the object.

        if the ball hit the paddle, the ball will bounce back.

        if the ball hit the normal brick, the score will be added 1,
        the brick will be disappeared, and the ball will bounce back.

        if the ball hit the red brick, the score will be added 5, and a special event will occur.

        :param obj: (GObject) Can not be None. The object touched by the ball.
        """
        if obj == self.paddle:
            if self.__dy > 0:
                self.change_y_direction()
        elif obj == self.block_paddle:
            # The ball hit the bottom of the block paddle.
            if index == 0 or index == 2:
                if self.__dy < 0:
                    self.change_y_direction()
            # The ball hit the top of the block paddle.
            if index == 1 or index == 3:
                if self.__dy > 0:
                    self.change_y_direction()
        else:
            if self.__is_red_bricks(obj):
                self.__update_score(5)
                self.__process_special_event(obj)
            else:
                self.__update_score(1)
            self.window.remove(obj)
            self.__remove_bricks_count += 1
            # If the count of removed bricks is multiples of 3,
            # then reset the position and horizontal speed of the block paddle.
            if self.__remove_bricks_count > 0 and self.__remove_bricks_count % 3 == 0:
                self.__set_block_paddle()
            self.change_y_direction()

    def __update_score(self, score):
        """
        Updates the score.
        :param score: (int) The score to add.
        """
        self.__score += score
        self.scoreboard.text = f'Score: {self.__score}'

    def __is_red_bricks(self, obj):
        """
        Check the object is red brick.
        :param obj: GObject
        :return: (Bool) True if the object is red brick, False is not.
        """
        for brick in self.red_bricks:
            if obj == brick:
                return True
        return False

    def __process_special_event(self, obj):
        """
        Processes the special event.
        The paddle becomes longer or shorter, or the velocity of the ball becomes faster.
        :param obj: (GObject) One of the red bricks.
        """
        # Remove current red bricks
        for brick in self.red_bricks:
            if obj == brick:
                self.red_bricks.remove(brick)
                break

        # Processes the special event.
        idx = len(self.red_bricks)
        if idx == -1:
            return
        elif idx == 2:
            # The paddle becomes longer.
            self.window.remove(self.paddle)
            self.__create_paddle(self.paddle.width+50, self.paddle.height)
        elif idx == 1:
            # The paddle becomes shorter.
            self.window.remove(self.paddle)
            self.__create_paddle(self.paddle.width-80, self.paddle.height)
        elif idx == 0:
            # The velocity of the ball becomes faster.
            if self.__dx < 0:
                self.__dx -= 5
            else:
                self.__dx += 5
            self.__dy -= 5

    def __set_block_paddle(self):
        """
        Set the position and horizontal speed of the block paddle.
        """
        self.__block_paddle_dx = random.randint(1, BLOCK_PADDLE_MAX_DX)
        y = random.randint(int(self.window.height/2), self.paddle.y - 10)
        x = random.randint(0, self.window.width - self.block_paddle.width)
        self.block_paddle.x = x
        self.block_paddle.y = y
        if self.__remove_bricks_count == 3:
            self.window.add(self.block_paddle)

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
            self.__dx = random.randint(2, MAX_X_SPEED)
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

    def __draw_bricks(self):
        """
        Draw bricks in the window.
        """
        brick = None
        color_arr = ['#222222', '#444444', '#666666', '#999999', '#bbbbbb']

        # Get random position of red bricks.
        random_pair = []
        for i in range(3):
            random_row = random.randint(0, self.__brick_rows - 1)
            random_col = random.randint(0, self.__brick_cols - 1)

            # If there are duplicate items in the list, generate a new one.
            if i == 1:
                while (random_row, random_col) == random_pair[0]:
                    random_row = random.randint(0, self.__brick_rows - 1)
                    random_col = random.randint(0, self.__brick_cols - 1)
            elif i == 2:
                while (random_row, random_col) == random_pair[0] or (random_row, random_col) == random_pair[1]:
                    random_row = random.randint(0, self.__brick_rows - 1)
                    random_col = random.randint(0, self.__brick_cols - 1)

            random_pair.append((random_row, random_col))

        # Draw bricks in the window.
        for i in range(self.__brick_rows):
            # Each two rows of bricks use the same color.
            color = color_arr[int(i / 2)]
            # Get the y position of current brick.
            if i == 0:
                brick_y = self.brick_offset
            else:
                brick_y = brick.y + brick.height + self.brick_spacing

            for j in range(self.__brick_cols):
                # Get the x position of current brick.
                if j == 0:
                    brick_x = 0
                else:
                    brick_x = brick.x + brick.width + self.brick_spacing

                # Create a brick, and add it into the window.
                brick = GRect(self.brick_width, self.brick_height, x=brick_x, y=brick_y)
                brick.filled = True
                if len(random_pair) > 0:
                    for pair in random_pair:
                        if i == pair[0] and j == pair[1]:
                            brick.fill_color = 'red'
                            brick.color = 'red'
                            self.red_bricks.append(brick)
                            random_pair.remove(pair)
                            break
                        else:
                            brick.fill_color = color
                            brick.color = color
                else:
                    brick.fill_color = color
                    brick.color = color
                self.window.add(brick)
