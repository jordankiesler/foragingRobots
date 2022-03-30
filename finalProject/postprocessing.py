import matplotlib.pyplot as plt
import numpy as np
import sys
import settings as st

import geneticController as gc

sys.path.insert(1, '..')
from situsim_extensions.plots2 import *


def do_plots(all_ts, agents, foods_and_poisons):
    """
    plot outputs for all robots - provided package
    :param all_ts: List of lists of time steps - one list for each agent in the list of agents provided
    :param agents: List of agents
    :param foods_and_poisons: List of food and pellet objects for plotting
    :return: Four plots
    """

    plt.rcParams["font.weight"] = "bold"

    plot_all_agents_trajectories(all_ts, agents, foods_and_poisons, draw_agents=False)

    # I didn't use the ones below, but you theoretically could
    # plot_all_robots_motors(all_ts, agents)
    # plot_all_robots_controllers(all_ts, agents)
    # plot_all_robots_sensors(all_ts, agents)

    plt.show()


def plotPhaseSpace(allRobots, title):
    """
    Plot the phase space of the robot in
    2D - first two parameters (velocity spikes vs
    acceleration spikes), but can be whatever you return
    as the first two values in the list in the robot's
    setBehScore() method of ForagingRobot class
    :param allRobots: List of all the robots to plot
    :param title: Portion of the plot title indicating type of robot population
    :return: Scatter plot of all robots' scores in the behavior space
    """
    plt.figure()

    x = [robot.behScore[0] for robot in allRobots]      # Set x-values to first value in behavior score list
    y = [robot.behScore[1] for robot in allRobots]      # Set u-values to second value in behavior score list

    plt.scatter(x, y, c='black', alpha=0.1)             # Scatter plot with slightly transparent dots to see overlap

    plt.title(f"Phase Space of Velocity vs Acceleration Spikes for {title}")
    plt.xlabel("Velocity")
    plt.ylabel("Acceleration")

    # plt.show()


def plot3DSpace(allRobots):
    """
    3D space to see entire behavioral space
    scores for a population of robots
    :param allRobots: list of all robots
    :return: 3D scatter plot of robots' behavioral scores
    """
    x = [robot.behScore[0] for robot in allRobots]
    y = [robot.behScore[1] for robot in allRobots]
    z = [robot.behScore[2] for robot in allRobots]

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.scatter(x, y, z)

    ax.set_xlabel('Velocity Spikes')
    ax.set_ylabel('Acceleration Spikes')
    ax.set_zlabel('Mean Velocity')

    # Showing the above plot
    plt.show()


def plotRobot(robot, ts):
    """
    Plot the robot's average velocity and acceleration on one plot
    and its trajectory in the other
    :param robot: Single robot object
    :param ts: List of time steps associated with robot's adventures
    :return: Two plots
    """
    y = robot.velocities
    x = ts[0:len(robot.velocities)]     # For some reason, robot velocities have one step less than ts list
    dy = np.gradient(y, 0.1)            # Acceleration of robot using velocity (Numerical approximation to derivative)

    plt.figure()                            # Plot robot's velocity and acceleration over time
    plt.plot(x, dy, label="Acceleration")
    plt.plot(x, y, label="Velocity")
    plt.title(f"Robot velocity")
    plt.xlabel("Time")
    plt.ylabel("Velocity")
    plt.ylim(-10, 10)
    plt.legend()

    plt.figure()                            # Plot robot's trajectory
    x = robot.xs
    y = robot.ys
    plt.plot(x, y)
    plt.ylim(-20, 20)                       # Force size plot so we can see robot's trajectory to scale of arena
    plt.xlim(-20, 20)
    plt.title("Robot position")

    plt.show()


def calculateScores(scores):
    """
    Calculate how well a population of robots
    did individually at all the events
    :param scores: A list of lists of scores for all robots per event [[event1Score1, event1Score2], [e2s1, e2s2], etc.]
    :return:
    """
    countedList = [sum([1 if i else 0 for i in x]) for x in scores]
    newCount = [countedList.count(x) for x in range(0, 7)]
    print(countedList, newCount)

    return countedList, newCount


def recordInfo(runNum, fightNov, fightFit, fight2Nov, fight2Fit, circleNov, circleFit, checkNov, checkFit, shiftNov,
               shiftFit, killNov, killFit, noiseNov, noiseFit, trolls):
    # Record all relevant info for a run of the olympics and save it to data____.txt
    # :param ___Nov: The foraging scores of the population of novelty search robots for each event
    # :param ___Fit: The foraging scores of the population of fitness search robots for each event
    # :param runNum: What run number it was (to keep track of trials and associate with plots)
    # :param trolls: List of all the controllers
    # :return: None

    # Text to be saved. I realized after I did it this way I could have probably used some loops but...too late
    text = f"----RUN {runNum}---\n" \
           f"Population Size: {st.MU + st.LAMBDA}\n\n" \
           f"Fight Novelty:\n" \
           f"{fightNov}\n" \
           f"{len([x for x in fightNov if x == 0]), len([x for x in fightNov if 0 < x <= 5]), len([x for x in fightNov if x > 5])}\n" \
           f"Fight Fitness:\n" \
           f"{fightFit}\n" \
           f"{len([x for x in fightFit if x == 0]), len([x for x in fightFit if 0 < x <= 5]), len([x for x in fightFit if x > 5])}\n" \
           f"\nFight 2 Novelty:\n" \
           f"{fight2Nov}\n" \
           f"{len([x for x in fight2Nov if x == 0]), len([x for x in fight2Nov if 0 < x <= 5]), len([x for x in fight2Nov if x > 5])}\n" \
           f"Fight 2 Fitness:\n" \
           f"{fight2Fit}\n" \
           f"{len([x for x in fight2Fit if x == 0]), len([x for x in fight2Fit if 0 < x <= 5]), len([x for x in fight2Fit if x > 5])}\n" \
           f"\nCircle Novelty:\n" \
           f"{circleNov}\n" \
           f"{len([x for x in circleNov if x == 0]), len([x for x in circleNov if 0 < x <= 15]), len([x for x in circleNov if x > 15])}\n" \
           f"Circle Fitness:\n" \
           f"{circleFit}\n" \
           f"{len([x for x in circleFit if x == 0]), len([x for x in circleFit if 0 < x <= 15]), len([x for x in circleFit if x > 15])}\n" \
           f"\nCheck Novelty:\n" \
           f"{checkNov}\n" \
           f"{len([x for x in checkNov if x == 0]), len([x for x in checkNov if 0 < x <= 15]), len([x for x in checkNov if x > 15])}\n" \
           f"Check Fitness:\n" \
           f"{checkFit}\n" \
           f"{len([x for x in checkFit if x == 0]), len([x for x in checkFit if 0 < x <= 15]), len([x for x in checkFit if x > 15])}\n" \
           f"\nShift Novelty:\n" \
           f"{shiftNov}\n" \
           f"{len([x for x in shiftNov if x == 0]), len([x for x in shiftNov if 0 < x <= 15]), len([x for x in shiftNov if x > 15])}\n" \
           f"Shift Fitness:\n" \
           f"{shiftFit}\n" \
           f"{len([x for x in shiftFit if x == 0]), len([x for x in shiftFit if 0 < x <= 15]), len([x for x in shiftFit if x > 15])}\n" \
           f"\nKill Novelty:\n" \
           f"{killNov}\n" \
           f"{len([x for x in killNov if x == 0]), len([x for x in killNov if 0 < x <= 15]), len([x for x in killNov if x > 15])}\n" \
           f"Kill Fitness:\n" \
           f"{killFit}\n" \
           f"{len([x for x in killFit if x == 0]), len([x for x in killFit if 0 < x <= 15]), len([x for x in killFit if x > 15])}\n" \
           f"\nNoise Novelty:\n" \
           f"{noiseNov}\n" \
           f"{len([x for x in noiseNov if x == 0]), len([x for x in noiseNov if 0 < x <= 15]), len([x for x in noiseNov if x > 15])}\n" \
           f"Noise Fitness:\n" \
           f"{noiseFit}\n" \
           f"{len([x for x in noiseFit if x == 0]), len([x for x in noiseFit if 0 < x <= 15]), len([x for x in noiseFit if x > 15])}\n" \
           f"\n\n" \
           f"Controller Scores Novelty:\n" \
           f"{[[y[1] for y in x.allScores] for x in trolls if x.nov is True]}\n" \
           f"{[x.allScores for x in trolls if x.nov is True]}\n" \
           f"{calculateScores([[y[1] for y in x.allScores] for x in trolls if x.nov is True])}\n" \
           f"Controller Scores Fitness:\n" \
           f"{[[y[1] for y in x.allScores] for x in trolls if x.nov is False]}\n" \
           f"{[x.allScores for x in trolls if x.nov is False]} \n\n" \
           f"{calculateScores([[y[1] for y in x.allScores] for x in trolls if x.nov is False])}\n" \
           f"Average Number of Active Nodes:\n" \
           f"Novelty: {gc.calculateAvgActiveNodes([x for x in trolls if x.nov is True])}" \
           f"Fitness: {gc.calculateAvgActiveNodes([x for x in trolls if x.nov is False])}"

    # Save text to a file called dataRoundTwo.txt
    with open("dataRoundTwo.txt", "a+") as file:
        # Move read cursor to the start of file.
        file.seek(0)
        # If file is not empty then append '\n'
        data = file.read(100)
        if len(data) > 0:
            file.write("\n\n")
        # Append text at the end of file
        file.write(text)


if __name__ == '__main__':
    scores = \
        [[0, 0, 7, 12, 0, 0, 0], [4, 7, 23, 1, 2, 0, 4], [0, 0, 3, 2, 9, 0, 0], [0, 0, 17, 11, 15, 0, 7],
         [0, 0, 9, 13, 2, 0, 5], [1, 4, 24, 17, 4, 2, 0], [2, 2, 20, 16, 8, 0, 7], [5, 0, 0, 16, 0, 5, 0],
         [0, 0, 0, 13, 3, 0, 0], [2, 0, 2, 9, 3, 10, 2]]

    calculateScores(scores)
