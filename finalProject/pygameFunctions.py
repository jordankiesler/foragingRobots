import pygame
import numpy as np
import time


def setup_pygame_window(screenWidth):
    """
    Initialize the pygame window for simulation animation
    :param screenWidth: How wide the simulation screen is
    :return: the pygame window
    """
    # initialise pygame and set parameters
    pygame.init()
    screen = pygame.display.set_mode([screenWidth, screenWidth])
    pygame.display.set_caption("SituSim")

    return screen


# draw SituSim systems in pygame window
def pygame_drawsim(screen, systems, width, paused, delay):
    """
    Function to update the simulation every frame,
    if it is animated
    :param screen: pygame window
    :param systems: list - all the system objects from the situsim library to update graphically
    :param width: int - width of screen
    :param paused: boolean - animation is paused
    :param delay: boolean- animation implements a delay
    :return: boolean if animation is running, boolean if animation is paused, float delay value
    """
    running = True

    # Check for user interaction to quit, pause, or change speed of animation
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_UP:
                delay -= 1
            elif event.key == pygame.K_DOWN:
                delay += 1

    delay = np.max([delay, 0])      # If user changed the delay value, don't let the delay become negative

    time.sleep(delay / 100)         # Slow the animation using the time.sleep() function if there's a delay

    screen.fill('black')

    # initial scale factor and offsets for converting simulation coordinates
    # to pygame animation display coordinates
    pygame_x_offset = width / 2
    pygame_y_offset = width / 2

    # find extremes of system trajectories for resizing animation window
    max_xs = []
    max_ys = []
    for system in systems:
        if system.has_position:
            max_xs.append(max(np.abs(system.xs)))
            max_ys.append(max(np.abs(system.ys)))

    # reset scale according to where systems are and have been
    pygame_scale = width / (2 * max(max(max_xs), max(max_ys)) + 1)

    # draw all systems
    for system in systems:
        system.pygame_draw(screen, scale=pygame_scale, shiftx=pygame_x_offset, shifty=pygame_y_offset)

    # flip the pygame display
    screen.blit(pygame.transform.flip(screen, False, True), (0, 0))
    # update the pygame display
    pygame.display.update()

    return running, paused, delay
