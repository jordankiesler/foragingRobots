import matplotlib.pyplot as plt
import numpy as np
import sys
import settings as st

sys.path.insert(1, '..')
from situsim_v1_2 import *
from situsim_extensions.plots2 import *

import geneticController as gc



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
    plt.ylabel("Velocity, Acceleration")
    plt.ylim(-10, 10)
    plt.legend()

    plt.figure()                            # Plot robot's trajectory
    x = robot.xs
    y = robot.ys
    plt.plot(x, y)
    plt.ylim(-20, 20)                       # Force size plot so we can see robot's trajectory to scale of arena
    plt.xlim(-20, 20)
    plt.title("Robot Trajectory")
    plt.xlabel("x")
    plt.ylabel("y")

    plt.show()


def calculateScores(scores):
    """
    Calculate how well a population of robots
    did individually at all the events
    :param scores: A list of lists of scores for all robots per event [[event1Score1, event1Score2], [e2s1, e2s2], etc.]
    :return:
    """
    countedList = [sum([1 if i else 0 for i in x]) for x in scores]
    newCount = [countedList.count(x) for x in range(0, 8)]
    print(countedList, newCount)

    return countedList, newCount


def plotBarChart():
    """
    Plot bar chart of summary values for run 6
    :return: bar chart
    """

    plt.title("Performance of Novelty vs Fitness-Evolved Controllers\nwith Binary Performance Metric for a Single Run")

    X = ['Foraging\nCompetition I', 'Foraging\nCompetition II', 'Circle of Pellets', 'Shifted Sensors', 'Left Sensor\nElimination', 'Controller Noise']
    novelty = [0.4, 0.7, 0.45, 0.75, 0.20, 0.7]
    fitness = [0.3, 0.4, 0.4, 0.8, 0.175, 0.6]

    X_axis = np.arange(len(X))

    plt.bar(X_axis - 0.2, novelty, 0.4, label='Novelty')
    plt.bar(X_axis + 0.2, fitness, 0.4, label='Fitness')

    plt.xticks(X_axis, X)
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Percent Successful")
    plt.legend(loc="upper left")

    plt.tight_layout()

    plt.show()


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
           f"Population Size: {st.LAMBDA}\n\n" \
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
           f"{calculateScores([[y[1] for y in x.allScores] for x in trolls if x.nov is True])}\n\n" \
           f"Controller Scores Fitness:\n" \
           f"{[[y[1] for y in x.allScores] for x in trolls if x.nov is False]}\n" \
           f"{[x.allScores for x in trolls if x.nov is False]} \n" \
           f"{calculateScores([[y[1] for y in x.allScores] for x in trolls if x.nov is False])}\n\n" \
           f"Average Number of Active Nodes:\n" \
           f"Novelty: {gc.calculateAvgActiveNodes([x for x in trolls if x.nov is True])}" \
           f"Fitness: {gc.calculateAvgActiveNodes([x for x in trolls if x.nov is False])}"

    # Save text to a file
    with open("newData.txt", "a+") as file:
        # Move read cursor to the start of file.
        file.seek(0)
        # If file is not empty then append '\n'
        data = file.read(100)
        if len(data) > 0:
            file.write("\n\n")
        # Append text at the end of file
        file.write(text)


if __name__ == '__main__':

    plotBarChart()
