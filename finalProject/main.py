import copy
import sys

import pygameFunctions as pf
import pelletGenerator as pg
import foragingRobot as fr
import novelty as nv
import geneticController as gc
import settings as st
import postprocessing as pp
import olympicEvents as oe

sys.path.insert(1, '..')
from situsim_extensions.arena import *


# Runs the entirety of each simulation once - launched from run_sim
def runSimOnce(screen_width, controller, animate=True, field_of_view=0.8 * np.pi, left_sensor_angle=np.pi / 3,
               right_sensor_angle=-np.pi / 3, duration=100, generation=0, novelty=False):
    """
    Run the simulation once - in this main loop,
    for only one robot at a time as we evolve populations
    to forage successfully
    :param screen_width: Obviously - the width of the screen
    :param controller: Controller object to put in robot - this is what we're evolving
    :param animate: Boolean to animate simulation
    :param field_of_view: Field of view of sensors
    :param left_sensor_angle: Angle of left sensor on robot body
    :param right_sensor_angle: Angle of right sensor on robot body
    :param duration: Duration of simulation
    :param generation: What generation the simulation is
    :param novelty: Whether or not novelty is being implemented
    :return: List of time steps, list of agents, list of pellets
    """

    # Set robot's starting position and angle
    x = -12
    y = 0
    theta = 0

    # Create a random set of 25 food pellets in a centered, 10x10 space in the arena
    # (using a random seed to maintain consistency in training)
    foodPellets, poisonPellets, allPellets = pg.generateRandomPellets(25, 0, 10, seed=3820)

    # Create a foragingRobot object with the appropriate parameters
    robot = fr.ForagingRobot(x=x, y=y, controller=controller, left_food_sources=foodPellets,
                             right_food_sources=foodPellets, left_poison_sources=poisonPellets,
                             right_poison_sources=poisonPellets,
                             left_food_sensor_angle=left_sensor_angle,
                             right_food_sensor_angle=right_sensor_angle,
                             left_poison_sensor_angle=left_sensor_angle,
                             right_poison_sensor_angle=right_sensor_angle,
                             food_field_of_view=field_of_view, poison_field_of_view=field_of_view,
                             consumables=allPellets, theta=theta, novelty=novelty
                             )
    # Set the controller's novelty - I don't love how this is done, but it works and its fragile now
    robot.controller.nov = novelty
    robot.generation = generation       # Set what generation the robot is
    agents = [robot]                    # Put robot in a list of agents (uses a list to make easily expandable)

    # Create an arena so the robot is confined to the space
    arena = Arena(agents, x_left=-20, x_right=20, y_top=20, y_bottom=-20)

    # only run pygame code if animating the simulation
    if animate:
        screen = pf.setup_pygame_window(screen_width)

    # animation variables
    delay = 0           # can be used to slow animation down
    running = True      # can be used to exit animation early
    paused = False      # can be used to pause simulation/animation

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

            # Step all consumable pellets
            for pellet in allPellets:
                pellet.step(dt)

            arena.step(dt)      # Step arena (needed in case robot hits the wall)

            # increment time variable and store in ts list for plotting later
            t += dt
            ts.append(t)

        # only run pygame code if animating the simulation
        if animate:
            running, paused, delay = pf.pygame_drawsim(screen, agents + allPellets + [arena], screen_width, paused,
                                                       delay)
    # simulation has completed

    # only run pygame code if animating the simulation
    if animate:
        # Quit pygame.
        pygame.display.quit()
        pygame.quit()

    # For the robot, set its behavioral score and fitness score then print relevant values to the terminal
    for robot in agents:
        robot.setBehScore()
        robot.controller.fitness = robot.foodEaten
        print("Score:", robot.behScore, "Foods:", robot.foodEaten, "Poison:", robot.poisonEaten,
              "Energy:", round(robot.energy, 2), "Novelty:", novelty)

    return ts, agents, allPellets


# Main function that actually popSize all the other stuff
def runSim(popSize=1, animate=True, numGoodNovBots=10, numGoodFitBots=10, foodThresh=10):
    """
    Main entry point for the entire program, launches the initial simulation
    to begin evolving the population of robots
    :param foodThresh: How many food pieces a robot has to eat to be considered good
    :param numGoodFitBots: How many good fitness robots you want to compete in the olympics
    :param numGoodNovBots: How many good novelty robots you want to compete in the olympics
    :param popSize: How many robots are in the population for each generation
    :param animate: Whether or not to animate the simulation
    :return: None
    """
    all_robots = []     # A list to hold all of the robots (for postprocessing)
    all_ts = []         # A list to hold all time steps (for postprocessing)

    # Initialize the starting population of robots - each are gp.Individual() objects
    population = gc.createPopulation(popSize)
    # Create a novelty object - does the novelty score calculations and stores the novelty archive
    novelty = nv.Novelty()

    goodBots = []           # Instantiate list to hold all the robots
    nov = True              # Whether or not the population of robots is being judged on fitness or novelty
    g = 0                   # The current generation of robot
    goToOlympics = False    # Boolean that becomes true after population of Olympians is generated - begins Olympics

    field_of_view = 0.8 * np.pi         # Set the field of view for all the robots - unchanging
    left_sensor_angle = np.pi / 3       # Set left and right sensor locations on the robot
    right_sensor_angle = -np.pi / 3
    duration = 100                      # Set the duration of the simulation

    # Test/evolve the population of robots to forage until goToOlympics is True
    while goToOlympics is False:
        print("GENERATION", g)
        g += 1              # Increment generation
        genRobots = []      # Create/reset an empty list to hold just this generation of robots

        # run the simulation the specified number of times - goes through each bot in the population once
        for i in range(popSize):

            # Set the controller to a new one in the list of evolvable controllers
            controller = population[i]

            # if you uncomment this line, only the first run of the simulation will be animated
            animate = animate and i == 0

            # run the simulation once, with the given parameters
            ts, robots, pellets = runSimOnce(screen_width=700, controller=controller, animate=animate,
                                             field_of_view=field_of_view, left_sensor_angle=left_sensor_angle,
                                             right_sensor_angle=right_sensor_angle, duration=duration,
                                             generation=g, novelty=nov)

            genRobots += robots     # Add the new robot(s) to the list of this generation of robots
            all_robots += robots    # Add the new robot(s) to the list of all robots for the whole experiment
            all_ts.append(ts)

        # Do the novelty evaluation on this generation of robots
        novelty.getNoveltyScores(genRobots, g)

        # Evolve the population of controllers using the old population and given parameters
        # Note that an entire population is either evolved on the basis of novelty or fitness
        population = gc.evolve(pop=population, robots=genRobots, mutRate=st.MUT_PB, numParents=st.MU,
                               numChildren=st.LAMBDA, novelty=nov)

        # After evolving the current generation, check if any of them are ready for the olympics
        for robot in genRobots:
            # If any robot met initial olympic qualifications and the team is not yet filled out, make sure it
            # wasn't a fluke by testing it again on the same course with the same controller
            if robot.foodEaten >= foodThresh and len(goodBots) < (numGoodNovBots + numGoodFitBots):
                _, newRobot, _ = runSimOnce(screen_width=700, controller=robot.controller, animate=animate,
                                            field_of_view=field_of_view, left_sensor_angle=left_sensor_angle,
                                            right_sensor_angle=right_sensor_angle, duration=duration,
                                            generation=g, novelty=nov)
                # If a new robot with the same controller succeeds again, add a copy of the controller to the list of
                # goodBots and reset it (method in base class) to wipe its memory
                if newRobot[0].foodEaten >= foodThresh:
                    goodBots.append(copy.deepcopy(robot.controller))
                    goodBots[-1].reset()

        print("Number of good bots:", len(goodBots))

        # If the number of novelty bots for the olympic team has been reached, begin fitness search with a new,
        # randomly generated population
        if nov and len(goodBots) >= numGoodNovBots:
            nov = False
            goodBots = goodBots[:numGoodNovBots]
            population = gc.createPopulation(popSize)
        # If the number of fitness bots for the olympic team has been filled out, stop evolving and start the olympics!
        if not nov and len(goodBots) >= (numGoodNovBots + numGoodFitBots):
            goToOlympics = True

    # Collate lists of all novelty/fitness robots and all olympic-standard novelty/fitness robots for plotting
    novBots = [x for x in all_robots if x.novelty is True]
    fitBots = [x for x in all_robots if x.novelty is False]
    goodNovBots = [x for x in novBots if x.foodEaten >= 10]
    goodFitBots = [x for x in fitBots if x.foodEaten >= 10]

    # Plot the 2D and 3D phase spaces of all the bots
    pp.plotPhaseSpace(novBots, "All Novelty Robots")
    pp.plotPhaseSpace(fitBots, "All Fitness Robots")
    pp.plotPhaseSpace(goodNovBots, "\nAdapted Novelty Robots")
    pp.plotPhaseSpace(goodFitBots, "\nAdapted Fitness Robots")

    pp.plot3DSpace(novBots)
    pp.plot3DSpace(fitBots)
    pp.plot3DSpace(goodNovBots)
    pp.plot3DSpace(goodFitBots)

    # BEGIN THE OLYMPICS!!!
    oe.runEvents(goodBots, field_of_view, left_sensor_angle, right_sensor_angle, duration)


# Run the simulation
if __name__ == "__main__":
    runSim(popSize=20, animate=True, numGoodNovBots=st.NUM_NOV_BOTS,
           numGoodFitBots=st.NUM_FIT_BOTS, foodThresh=st.FOOD_THRESH)
