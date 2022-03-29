import numpy as np
import sys
import pelletGenerator as pg
import postprocessing as pp
import pygameFunctions as pf
import foragingRobot as fr

sys.path.insert(1, '..')
from situsim_extensions.arena import *


def runEvents(controllers, field_of_view, left_sensor_angle, right_sensor_angle, duration):
    """
    Run all olympic events for the
    novelty and fitness robots
    :param duration: int - how long the simulation lasts
    :param right_sensor_angle: in radians, the angle location of the robot's right sensor
    :param left_sensor_angle: in radians, the angle location of the robot's left sensor
    :param field_of_view: in radians, the field of view of each robot's sensors
    :param controllers: A list of controllers - assumes portion of them are fitness-based and portion are novelty-based
    :return: None
    """

    runNumber = 0       # Run number - manually set for each trial - saves to data.txt to distinguish data

    all_robots = []     # A list to hold all of the robots (for postprocessing)
    all_ts = []         # A list to hold all time steps (for postprocessing)

    """
    -------------------------------------------------------------------------------------------------------------------
    Begin the first foraging competition event, where all robots are placed in an arena with 25 food pellets
    and must duke it out. All parameters are same to that of training except a new random seed and they're run together. 
    -------------------------------------------------------------------------------------------------------------------
    """

    print("\n\n------------BEGINNING OF FIGHT----------\n\n")

    animate = True      # Whether or not to animate the fight

    # run the simulation once, with the given parameters
    ts, robots, pellets = runFightSim(screen_width=700, controller=controllers, animate=animate,
                                      field_of_view=field_of_view, left_sensor_angle=left_sensor_angle,
                                      right_sensor_angle=right_sensor_angle, duration=duration, generation=0)

    all_robots += robots                    # Add the new robot(s) to the list of all robots for the whole experiment
    for robot in range(len(all_robots)):    # Must be done b/c provided plot pkg assumes each robot has own time series
        all_ts.append(ts)

    # Print each robot's score and whether it was novel
    for robot in all_robots:
        print("Food eaten:", robot.foodEaten, "Novelty:", robot.novelty)

    # Separate novel and fitness bots from each other for postprocessing
    fightNov = [x.foodEaten for x in all_robots if x.novelty]
    fightFit = [x.foodEaten for x in all_robots if not x.novelty]

    # Run all the plots for all the bots for this event
    pp.do_plots(all_ts, all_robots, pellets)

    """
    -------------------------------------------------------------------------------------------------------------------
    Begin the second foraging competition event, where all robots are placed in an arena with 50 food pellets spread out
    over the entire arena and must duke it out. 
    
    Note: A lot of the code is similar but just resetting, so I'm not going to comment all of it each time. Yeah, yeah,
    I probably could've condensed this but it was simpler to do it this way so here we are. 
    ------------------------------------------------------------------------------------------------------------------- 
    """

    print("\n\n------------BEGINNING OF FIGHT 2----------\n\n")
    all_robots = []
    all_ts = []
    (x.reset() for x in controllers)        # Reset all the controllers (needed to plot correctly each time)

    # run the simulation once, with the given parameters
    ts, robots, pellets = runFightSim2(screen_width=700, controller=controllers, animate=animate,
                                       field_of_view=field_of_view, left_sensor_angle=left_sensor_angle,
                                       right_sensor_angle=right_sensor_angle, duration=duration, generation=0)

    all_robots += robots  # Add the new robot(s) to the list of all robots for the whole experiment
    for robot in range(len(all_robots)):  # Must be done b/c provided plot pkg assumes each robot has own time series
        all_ts.append(ts)

    for robot in all_robots:
        print("Food eaten:", robot.foodEaten, "Novelty:", robot.novelty)

    fight2Nov = [x.foodEaten for x in all_robots if x.novelty]
    fight2Fit = [x.foodEaten for x in all_robots if not x.novelty]

    pp.do_plots(all_ts, all_robots, pellets)

    """
    -------------------------------------------------------------------------------------------------------------------
    Begin the third event, where the pellets are arranged in a circle with the robot at the origin instead of randomly.
    From this event onward, the robots compete one at a time instead of all at once like in the foraging competitions
    -------------------------------------------------------------------------------------------------------------------
    """

    print("\n\n------------BEGINNING OF CIRCLE PELLETS----------\n\n")

    all_robots = []
    all_ts = []
    animate = False

    for troll in controllers:
        troll.reset()           # Reset the current controller to default values (doesn't affect evolved portion)

        # run the simulation once, with the given parameters
        ts, robots, pellets = runCircleSim(screen_width=700, controller=troll, animate=animate,
                                           field_of_view=field_of_view, left_sensor_angle=left_sensor_angle,
                                           right_sensor_angle=right_sensor_angle, duration=duration, generation=0)

        all_robots += robots  # Add the new robot(s) to the list of all robots for the whole experiment
        all_ts.append(ts)

    for robot in all_robots:
        print("Food eaten:", robot.foodEaten, "Novelty:", robot.novelty)

    circleNov = [x.foodEaten for x in all_robots if x.novelty]
    circleFit = [x.foodEaten for x in all_robots if not x.novelty]

    pp.do_plots(all_ts, all_robots, pellets)

    """
    -------------------------------------------------------------------------------------------------------------------
    Begin the fourth event, which is identical to training except with a new random seed. Sort of a 'control' event
    -------------------------------------------------------------------------------------------------------------------
    """

    print("\n\n------------BEGINNING OF CHECK SIM----------\n\n")

    all_robots = []
    all_ts = []
    animate = False

    for troll in controllers:
        troll.reset()

        # run the simulation once, with the given parameters
        ts, robots, pellets = runCheckSim(screen_width=700, controller=troll, animate=animate,
                                          field_of_view=field_of_view, left_sensor_angle=left_sensor_angle,
                                          right_sensor_angle=right_sensor_angle, duration=duration, generation=0)

        all_robots += robots  # Add the new robot(s) to the list of all robots for the whole experiment
        all_ts.append(ts)

    for robot in all_robots:
        print("Food eaten:", robot.foodEaten, "Novelty:", robot.novelty)

    checkNov = [x.foodEaten for x in all_robots if x.novelty]
    checkFit = [x.foodEaten for x in all_robots if not x.novelty]

    pp.do_plots(all_ts, all_robots, pellets)

    """
    -------------------------------------------------------------------------------------------------------------------
    Begin the fifth event, where the left and right sensors of every robot are shifted three times more inward than
    standard - placed on same course as training but with new random seed  
    -------------------------------------------------------------------------------------------------------------------
    """

    print("\n\n------------BEGINNING OF SENSOR SHIFT----------\n\n")

    all_robots = []  # A list to hold all of the robots (for postprocessing)
    all_ts = []  # A list to hold all time steps (for postprocessing)
    animate = False

    field_of_view = 0.8 * np.pi
    left_sensor_angle = np.pi / 9
    right_sensor_angle = -np.pi / 9

    for troll in controllers:
        troll.reset()

        # run the simulation once, with the given parameters
        ts, robots, pellets = runSensorShiftSim(screen_width=700, controller=troll, animate=animate,
                                                field_of_view=field_of_view, left_sensor_angle=left_sensor_angle,
                                                right_sensor_angle=right_sensor_angle, duration=duration, generation=0)

        all_robots += robots  # Add the new robot(s) to the list of all robots for the whole experiment
        all_ts.append(ts)

    for robot in all_robots:
        print("Food eaten:", robot.foodEaten, "Novelty:", robot.novelty)

    shiftNov = [x.foodEaten for x in all_robots if x.novelty]
    shiftFit = [x.foodEaten for x in all_robots if not x.novelty]

    pp.do_plots(all_ts, all_robots, pellets)

    """
    -------------------------------------------------------------------------------------------------------------------
    Begin the sixth event, where the left sensor of every robot is effectively killed - 
    placed on same course as training but with new random seed  
    -------------------------------------------------------------------------------------------------------------------
    """

    print("\n\n------------BEGINNING OF LEFT SENSOR DEATH----------\n\n")

    all_robots = []  # A list to hold all of the robots (for postprocessing)
    all_ts = []  # A list to hold all time steps (for postprocessing)
    animate = False

    field_of_view = 0.8 * np.pi
    left_sensor_angle = np.pi / 3
    right_sensor_angle = -np.pi / 3

    for troll in controllers:
        troll.reset()

        # run the simulation once, with the given parameters
        ts, robots, pellets = runSensorKillSim(screen_width=700, controller=troll, animate=animate,
                                               field_of_view=field_of_view, left_sensor_angle=left_sensor_angle,
                                               right_sensor_angle=right_sensor_angle, duration=duration, generation=0)

        all_robots += robots  # Add the new robot(s) to the list of all robots for the whole experiment
        all_ts.append(ts)

    for robot in all_robots:
        print("Food eaten:", robot.foodEaten, "Novelty:", robot.novelty)

    killNov = [x.foodEaten for x in all_robots if x.novelty]
    killFit = [x.foodEaten for x in all_robots if not x.novelty]

    pp.do_plots(all_ts, all_robots, pellets)

    """
    -------------------------------------------------------------------------------------------------------------------
    Begin the seventh and final event, where noise is introduced into the controller outputs. Likely won't use this
    one much in evaluation, noise was either too low to have much effect or too high for robot to cope at all. 
    Tested values at 1 and lower were too low and at 5 were too high for brown noise
    -------------------------------------------------------------------------------------------------------------------
    """

    print("\n\n------------BEGINNING OF NOISE----------\n\n")

    all_robots = []
    all_ts = []
    animate = True

    for troll in controllers:
        troll.reset()

        # run the simulation once, with the given parameters
        ts, robots, pellets = runNoiseSim(screen_width=700, controller=troll, animate=animate,
                                          field_of_view=field_of_view, left_sensor_angle=left_sensor_angle,
                                          right_sensor_angle=right_sensor_angle, duration=duration, generation=0)

        animate = False
        all_robots += robots  # Add the new robot(s) to the list of all robots for the whole experiment
        all_ts.append(ts)

    for robot in all_robots:
        print("Food eaten:", robot.foodEaten, "Novelty:", robot.novelty)

    noiseNov = [x.foodEaten for x in all_robots if x.novelty]
    noiseFit = [x.foodEaten for x in all_robots if not x.novelty]

    pp.do_plots(all_ts, all_robots, pellets)

    pp.recordInfo(runNumber, fightNov, fightFit, fight2Nov, fight2Fit, circleNov, circleFit, checkNov, checkFit,
                  shiftNov, shiftFit, killNov, killFit, noiseNov, noiseFit, controllers)


"""
I considered trying to put these event simulations into a for loop or some such of a cleaner implementation, but given
the breadth of variables that needed to change, I just made each its own function. To paraphrase Mark Twain, if I'd 
had more time I'd have written shorter code. Briefer comments here since the simulations are very similar to the 
well-commented one in main.py, and each other, and the descriptions of the events are in the runEvents function above. 
"""


# Compete all robots in the same arena with 25 randomly placed food pellets in a 20x20 space (same as training)
def runFightSim(screen_width, controller, animate=True, field_of_view=0.8 * np.pi, left_sensor_angle=np.pi / 3,
                right_sensor_angle=-np.pi / 3, duration=100, generation=0):
    # Set robot's starting position and angle
    x = -12
    y = 0
    theta = 0

    foodPellets, poisonPellets, allPellets = pg.generateRandomPellets(25, 0, 10)
    agents = []

    # create robots from all the controllers to compete in same arena
    for troll in controller:
        robot = fr.ForagingRobot(x=x, y=y, controller=troll, left_food_sources=foodPellets,
                                 right_food_sources=foodPellets, left_poison_sources=poisonPellets,
                                 right_poison_sources=poisonPellets,
                                 left_food_sensor_angle=left_sensor_angle,
                                 right_food_sensor_angle=right_sensor_angle,
                                 left_poison_sensor_angle=left_sensor_angle,
                                 right_poison_sensor_angle=right_sensor_angle,
                                 food_field_of_view=field_of_view, poison_field_of_view=field_of_view,
                                 consumables=allPellets, theta=theta, novelty=troll.nov
                                 )
        robot.generation = generation
        agents.append(robot)

    arena = Arena(agents, x_left=-20, x_right=20, y_top=20, y_bottom=-20)

    # only run pygame code if animating the simulation
    if animate:
        screen = pf.setup_pygame_window(screen_width)

    # animation variables
    delay = 0  # can be used to slow animation down
    running = True  # can be used to exit animation early
    paused = False  # can be used to pause simulation/animation

    # prepare simulation time variables
    t = 0
    ts = [t]
    dt = 0.1
    # begin simulation main loop
    while t < duration and running:

        # only move simulation forwards in time if not paused
        if not paused:

            # step all robots
            for agent in agents:
                agent.step(dt)

            for pellet in allPellets:
                pellet.step(dt)

            arena.step(dt)

            # increment time variable and store in ts list for plotting later
            t += dt
            ts.append(t)

        # only run pygame code if animating the simulation
        if animate:
            running, paused, delay = pf.pygame_drawsim(screen, agents + allPellets + [arena], screen_width, paused,
                                                       delay)

    # only run pygame code if animating the simulation
    if animate:
        # Quit pygame.
        pygame.display.quit()
        pygame.quit()

    # Iterate through the list of agents, recording all their scores
    for i in range(len(agents)):
        controller[i].allScores.append(['fight', agents[i].foodEaten])

    return ts, agents, allPellets


# Compete all robots in the same arena with 50 randomly placed food pellets in the entire arena space (40x40)
def runFightSim2(screen_width, controller, animate=True, field_of_view=0.8 * np.pi, left_sensor_angle=np.pi / 3,
                 right_sensor_angle=-np.pi / 3, duration=100, generation=0):
    # Set robot's starting position and angle
    x = -12
    y = 0
    theta = 0

    foodPellets, poisonPellets, allPellets = pg.generateRandomPellets(50, 0, 20)
    agents = []

    # create robot
    for troll in controller:
        robot = fr.ForagingRobot(x=x, y=y, controller=troll, left_food_sources=foodPellets,
                                 right_food_sources=foodPellets, left_poison_sources=poisonPellets,
                                 right_poison_sources=poisonPellets,
                                 left_food_sensor_angle=left_sensor_angle,
                                 right_food_sensor_angle=right_sensor_angle,
                                 left_poison_sensor_angle=left_sensor_angle,
                                 right_poison_sensor_angle=right_sensor_angle,
                                 food_field_of_view=field_of_view, poison_field_of_view=field_of_view,
                                 consumables=allPellets, theta=theta, novelty=troll.nov
                                 )
        robot.generation = generation
        agents.append(robot)

    arena = Arena(agents, x_left=-20, x_right=20, y_top=20, y_bottom=-20)

    # only run pygame code if animating the simulation
    if animate:
        screen = pf.setup_pygame_window(screen_width)

    # animation variables
    delay = 0  # can be used to slow animation down
    running = True  # can be used to exit animation early
    paused = False  # can be used to pause simulation/animation

    # prepare simulation time variables
    t = 0
    ts = [t]
    dt = 0.1
    # begin simulation main loop
    while t < duration and running:

        # only move simulation forwards in time if not paused
        if not paused:

            # step all robots
            for agent in agents:
                agent.step(dt)

            for pellet in allPellets:
                pellet.step(dt)

            arena.step(dt)

            # increment time variable and store in ts list for plotting later
            t += dt
            ts.append(t)

        # only run pygame code if animating the simulation
        if animate:
            running, paused, delay = pf.pygame_drawsim(screen, agents + allPellets + [arena], screen_width, paused,
                                                       delay)

    # only run pygame code if animating the simulation
    if animate:
        # Quit pygame.
        pygame.display.quit()
        pygame.quit()

    for i in range(len(agents)):
        controller[i].allScores.append(['fight2', agents[i].foodEaten])

    return ts, agents, allPellets


# One robot at a time, pellets are placed in a circle with robot at the origin instead of randomly placed
# There are 25 pellets at a radius of 10 away from the origin
def runCircleSim(screen_width, controller, animate=True, field_of_view=0.8 * np.pi, left_sensor_angle=np.pi / 3,
                 right_sensor_angle=-np.pi / 3, duration=100, generation=0):
    # Set robot's starting position and angle
    x = 0
    y = 0
    theta = 0

    foodPellets, poisonPellets, allPellets = pg.generateCircleOfPellets(25, 0, 10, 0)

    # create robot
    robot = fr.ForagingRobot(x=x, y=y, controller=controller, left_food_sources=foodPellets,
                             right_food_sources=foodPellets, left_poison_sources=poisonPellets,
                             right_poison_sources=poisonPellets,
                             left_food_sensor_angle=left_sensor_angle,
                             right_food_sensor_angle=right_sensor_angle,
                             left_poison_sensor_angle=left_sensor_angle,
                             right_poison_sensor_angle=right_sensor_angle,
                             food_field_of_view=field_of_view, poison_field_of_view=field_of_view,
                             consumables=allPellets, theta=theta, novelty=controller.nov
                             )
    robot.generation = generation
    agents = [robot]

    arena = Arena(agents, x_left=-20, x_right=20, y_top=20, y_bottom=-20)

    # only run pygame code if animating the simulation
    if animate:
        screen = pf.setup_pygame_window(screen_width)

    # animation variables
    delay = 0  # can be used to slow animation down
    running = True  # can be used to exit animation early
    paused = False  # can be used to pause simulation/animation

    # prepare simulation time variables
    t = 0
    ts = [t]
    dt = 0.1
    # begin simulation main loop
    while t < duration and running:

        # only move simulation forwards in time if not paused
        if not paused:

            # step all robots
            for agent in agents:
                agent.step(dt)

            for pellet in allPellets:
                pellet.step(dt)

            arena.step(dt)

            # increment time variable and store in ts list for plotting later
            t += dt
            ts.append(t)

        # only run pygame code if animating the simulation
        if animate:
            running, paused, delay = pf.pygame_drawsim(screen, agents + allPellets + [arena], screen_width, paused,
                                                       delay)

    # only run pygame code if animating the simulation
    if animate:
        # Quit pygame.
        pygame.display.quit()
        pygame.quit()

    controller.allScores.append(['circle', robot.foodEaten])

    return ts, agents, allPellets


# Run a control check of the sim identical to training but with a different random seed for pellet generation
def runCheckSim(screen_width, controller, animate=True, field_of_view=0.8 * np.pi, left_sensor_angle=np.pi / 3,
                right_sensor_angle=-np.pi / 3, duration=100, generation=0):
    # Set robot's starting position and angle
    x = -12
    y = 0
    theta = 0

    # Lower "brightness" of pellet by half
    foodPellets, poisonPellets, allPellets = pg.generateRandomPellets(25, 0, 10, seed=2020)

    # create robot
    robot = fr.ForagingRobot(x=x, y=y, controller=controller, left_food_sources=foodPellets,
                             right_food_sources=foodPellets, left_poison_sources=poisonPellets,
                             right_poison_sources=poisonPellets,
                             left_food_sensor_angle=left_sensor_angle,
                             right_food_sensor_angle=right_sensor_angle,
                             left_poison_sensor_angle=left_sensor_angle,
                             right_poison_sensor_angle=right_sensor_angle,
                             food_field_of_view=field_of_view, poison_field_of_view=field_of_view,
                             consumables=allPellets, theta=theta, novelty=controller.nov
                             )
    robot.generation = generation
    agents = [robot]

    arena = Arena(agents, x_left=-20, x_right=20, y_top=20, y_bottom=-20)

    # only run pygame code if animating the simulation
    if animate:
        screen = pf.setup_pygame_window(screen_width)

    # animation variables
    delay = 0  # can be used to slow animation down
    running = True  # can be used to exit animation early
    paused = False  # can be used to pause simulation/animation

    # prepare simulation time variables
    t = 0
    ts = [t]
    dt = 0.1
    # begin simulation main loop
    while t < duration and running:

        # only move simulation forwards in time if not paused
        if not paused:

            # step all robots
            for agent in agents:
                agent.step(dt)

            for pellet in allPellets:
                pellet.step(dt)

            arena.step(dt)

            # increment time variable and store in ts list for plotting later
            t += dt
            ts.append(t)

        # only run pygame code if animating the simulation
        if animate:
            running, paused, delay = pf.pygame_drawsim(screen, agents + allPellets + [arena], screen_width, paused,
                                                       delay)

    # only run pygame code if animating the simulation
    if animate:
        # Quit pygame.
        pygame.display.quit()
        pygame.quit()

    robot.controller.allScores.append(['check', robot.foodEaten])

    return ts, agents, allPellets


# Shift both sensors inwards from pi/3 to pi/9 (given in function parameters) and run on same course as training but
# with a new random seed
def runSensorShiftSim(screen_width, controller, animate=True, field_of_view=0.8 * np.pi, left_sensor_angle=np.pi / 3,
                      right_sensor_angle=-np.pi / 3, duration=100, generation=0):
    # Set robot's starting position and angle
    x = -12
    y = 0
    theta = 0

    foodPellets, poisonPellets, allPellets = pg.generateRandomPellets(25, 0, 10, seed=2020)

    # create robot
    robot = fr.ForagingRobot(x=x, y=y, controller=controller, left_food_sources=foodPellets,
                             right_food_sources=foodPellets, left_poison_sources=poisonPellets,
                             right_poison_sources=poisonPellets,
                             left_food_sensor_angle=left_sensor_angle,
                             right_food_sensor_angle=right_sensor_angle,
                             left_poison_sensor_angle=left_sensor_angle,
                             right_poison_sensor_angle=right_sensor_angle,
                             food_field_of_view=field_of_view, poison_field_of_view=field_of_view,
                             consumables=allPellets, theta=theta, novelty=controller.nov
                             )
    robot.generation = generation
    agents = [robot]

    arena = Arena(agents, x_left=-20, x_right=20, y_top=20, y_bottom=-20)

    # only run pygame code if animating the simulation
    if animate:
        screen = pf.setup_pygame_window(screen_width)

    # animation variables
    delay = 0  # can be used to slow animation down
    running = True  # can be used to exit animation early
    paused = False  # can be used to pause simulation/animation

    # prepare simulation time variables
    t = 0
    ts = [t]
    dt = 0.1
    # begin simulation main loop
    while t < duration and running:

        # only move simulation forwards in time if not paused
        if not paused:

            # step all robots
            for agent in agents:
                agent.step(dt)

            for pellet in allPellets:
                pellet.step(dt)

            arena.step(dt)

            # increment time variable and store in ts list for plotting later
            t += dt
            ts.append(t)

        # only run pygame code if animating the simulation
        if animate:
            running, paused, delay = pf.pygame_drawsim(screen, agents + allPellets + [arena], screen_width, paused,
                                                       delay)

    # only run pygame code if animating the simulation
    if animate:
        # Quit pygame.
        pygame.display.quit()
        pygame.quit()

    controller.allScores.append(['shift', robot.foodEaten])

    return ts, agents, allPellets


# Kill the left sensor by feeding it an empty list of food sources to seek and run the robots on the same course as
# training but with a new random seed for pellet generation
def runSensorKillSim(screen_width, controller, animate=True, field_of_view=0.8 * np.pi, left_sensor_angle=np.pi / 3,
                     right_sensor_angle=-np.pi / 3, duration=100, generation=0):
    # Set robot's starting position and angle
    x = -12
    y = 0
    theta = 0

    foodPellets, poisonPellets, allPellets = pg.generateRandomPellets(25, 0, 10, seed=2020)

    # create robot
    robot = fr.ForagingRobot(x=x, y=y, controller=controller, left_food_sources=[],
                             right_food_sources=foodPellets, left_poison_sources=poisonPellets,
                             right_poison_sources=poisonPellets,
                             left_food_sensor_angle=left_sensor_angle,
                             right_food_sensor_angle=right_sensor_angle,
                             left_poison_sensor_angle=left_sensor_angle,
                             right_poison_sensor_angle=right_sensor_angle,
                             food_field_of_view=field_of_view, poison_field_of_view=field_of_view,
                             consumables=allPellets, theta=theta, novelty=controller.nov
                             )
    robot.generation = generation
    agents = [robot]

    arena = Arena(agents, x_left=-20, x_right=20, y_top=20, y_bottom=-20)

    # only run pygame code if animating the simulation
    if animate:
        screen = pf.setup_pygame_window(screen_width)

    # animation variables
    delay = 0  # can be used to slow animation down
    running = True  # can be used to exit animation early
    paused = False  # can be used to pause simulation/animation

    # prepare simulation time variables
    t = 0
    ts = [t]
    dt = 0.1
    # begin simulation main loop
    while t < duration and running:

        # only move simulation forwards in time if not paused
        if not paused:

            # step all robots
            for agent in agents:
                agent.step(dt)

            for pellet in allPellets:
                pellet.step(dt)

            arena.step(dt)

            # increment time variable and store in ts list for plotting later
            t += dt
            ts.append(t)

        # only run pygame code if animating the simulation
        if animate:
            running, paused, delay = pf.pygame_drawsim(screen, agents + allPellets + [arena], screen_width, paused,
                                                       delay)

    # only run pygame code if animating the simulation
    if animate:
        # Quit pygame.
        pygame.display.quit()
        pygame.quit()

    controller.allScores.append(['kill', robot.foodEaten])

    return ts, agents, allPellets


# Add brown noise to the controller for both the left and right side, then run the robots on the same course as training
# but with a new random seed for pellet generation
def runNoiseSim(screen_width, controller, animate=True, field_of_view=0.8 * np.pi, left_sensor_angle=np.pi / 3,
                right_sensor_angle=-np.pi / 3, duration=100, generation=0):
    # Set robot's starting position and angle
    x = -12
    y = 0
    theta = 0

    # Lower "brightness" of pellet by half
    foodPellets, poisonPellets, allPellets = pg.generateRandomPellets(25, 0, 10, seed=2020)

    controller.left_noisemaker = BrownNoiseSource(5)
    controller.right_noisemaker = BrownNoiseSource(5)

    # create robot
    robot = fr.ForagingRobot(x=x, y=y, controller=controller, left_food_sources=foodPellets,
                             right_food_sources=foodPellets, left_poison_sources=poisonPellets,
                             right_poison_sources=poisonPellets,
                             left_food_sensor_angle=left_sensor_angle,
                             right_food_sensor_angle=right_sensor_angle,
                             left_poison_sensor_angle=left_sensor_angle,
                             right_poison_sensor_angle=right_sensor_angle,
                             food_field_of_view=field_of_view, poison_field_of_view=field_of_view,
                             consumables=allPellets, theta=theta, novelty=controller.nov,
                             )
    robot.generation = generation
    agents = [robot]

    arena = Arena(agents, x_left=-20, x_right=20, y_top=20, y_bottom=-20)

    # only run pygame code if animating the simulation
    if animate:
        screen = pf.setup_pygame_window(screen_width)

    # animation variables
    delay = 0  # can be used to slow animation down
    running = True  # can be used to exit animation early
    paused = False  # can be used to pause simulation/animation

    # prepare simulation time variables
    t = 0
    ts = [t]
    dt = 0.1
    # begin simulation main loop
    while t < duration and running:

        # only move simulation forwards in time if not paused
        if not paused:

            # step all robots
            for agent in agents:
                agent.step(dt)

            for pellet in allPellets:
                pellet.step(dt)

            arena.step(dt)

            # increment time variable and store in ts list for plotting later
            t += dt
            ts.append(t)

        # only run pygame code if animating the simulation
        if animate:
            running, paused, delay = pf.pygame_drawsim(screen, agents + allPellets + [arena], screen_width, paused,
                                                       delay)

    # only run pygame code if animating the simulation
    if animate:
        # Quit pygame.
        pygame.display.quit()
        pygame.quit()

    controller.allScores.append(['noise', robot.foodEaten])

    return ts, agents, allPellets
