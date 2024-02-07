"""
stanCode Breakout Project
Adapted from Eric Roberts's Breakout by
Sonja Johnson-Yu, Kylie Jue, Nick Bowman,
and Jerry Liao.
"""

from campy.gui.events.timer import pause
from breakoutgraphics import BreakoutGraphics

FRAME_RATE = 10         # 100 frames per second
NUM_LIVES = 3			# Number of attempts


def main():
    """
    This main function control the animation of the game.
    """
    # Create an instance of graphics
    graphics = BreakoutGraphics()
    # Number of attempts
    lives = NUM_LIVES

    # The animation loop
    while True:
        graphics.ball.move(graphics.get_dx(), graphics.get_dy())
        graphics.handle_ball_hit_obj()

        if graphics.is_ball_leaves_window():
            graphics.init_ball()
            # If the ball leaves the bottom of the window, then decrease one attempt.
            lives -= 1
            # If attempts are equal to 0, then game over.
            if lives == 0:
                break
        elif graphics.is_game_win():
            graphics.init_ball()
            break
        elif graphics.is_ball_on_x_side():
            graphics.change_x_direction()
        elif graphics.is_ball_on_y_side():
            graphics.change_y_direction()

        pause(FRAME_RATE)


if __name__ == '__main__':
    main()
