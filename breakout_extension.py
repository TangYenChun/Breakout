"""
stanCode Breakout Project
Adapted from Eric Roberts's Breakout by
Sonja Johnson-Yu, Kylie Jue, Nick Bowman,
and Jerry Liao.

This extension version was adapted by Bella.
This version, based on the brick-breaking game, has added a scoreboard, lives on the window.
In addition to regular bricks, red bricks have also been added.
If the ball touch the red bricks, score will be added 5, and the special event will occur.
If the count of removed bricks is multiples of 3, then add the block paddle in the window,
or reset the position and horizontal speed of the block paddle.
"""

from campy.gui.events.timer import pause
from breakoutgraphics_extension import BreakoutGraphics

FRAME_RATE = 10         # 100 frames per second
NUM_LIVES = 3			# Number of attempts


def main():
    """
    This main function control the animation of the game.
    """
    # Create an instance of graphics
    graphics = BreakoutGraphics(lives=NUM_LIVES)
    # Number of attempts
    lives = NUM_LIVES

    # The animation loop
    while True:
        graphics.ball.move(graphics.get_dx(), graphics.get_dy())
        if graphics.is_block_paddle_need_turn_around():
            graphics.change_block_paddle_dy()
        graphics.block_paddle.move(graphics.get_block_paddle_dx(), 0)
        graphics.handle_ball_hit_obj()

        if graphics.is_ball_leaves_window():
            graphics.init_ball()
            # If the ball leaves the bottom of the window, then decrease one attempt.
            lives -= 1
            graphics.remove_a_live(lives)
            # If attempts are equal to 0, then game over.
            if lives == 0:
                graphics.init_ball()
                graphics.show_game_result(False)
                break
        elif graphics.is_game_win():
            graphics.init_ball()
            graphics.show_game_result(True)
            break
        elif graphics.is_ball_on_x_side():
            graphics.change_x_direction()
        elif graphics.is_ball_on_y_side():
            graphics.change_y_direction()

        pause(FRAME_RATE)


if __name__ == '__main__':
    main()
