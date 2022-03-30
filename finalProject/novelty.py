import random
import numpy as np


# A class for doing/storing the novelty metric stuff
class Novelty:

    def __init__(self):

        self.allBehScores = []          # List to hold lists of the behavioral scores of every generation
        self.allNoveltyScores = []      # List to hold lists of the novelty scores of every generation
        self.behArchive = []            # List to hold all the behavioral scores used for the archive

    def getNoveltyScores(self, pop, generation):
        """
        Get the novelty scores for every controller
        in a population
        :param pop: Population of robots
        :param generation: Generation number - just for human interest
        :return: None
        """

        currentBehScores = [robot.behScore for robot in pop]  # Fetch the behavioral scores of all the robots
        combinedScores = []     # Instantiate a list to hold the combined scores
        k = 3                   # Set the k-value for how many k-nearest neighbors are considered

        # For every robot in the population, calculate its novelty score
        for r in range(len(pop)):
            euclideanScores = []      # Instantiate a list to hold euclidean distances of every score from current robot
            currentBehScores = [robot.behScore for robot in pop]    # Reset the current list of scores
            robotScore = currentBehScores.pop(r)                    # Remove the score of the current robot and save
            allScores = currentBehScores + self.behArchive          # Reset allScores list w/o current robot's

            # For every score in the list, calculate its euclidean distance to the current score of interest, robotScore
            # Functions that did this for me weren't working, so we went old fashioned - currently takes 3-element lists
            for score in allScores:
                dist = abs((robotScore[0] - score[0])**2 + (robotScore[1] - score[1])**2 + (robotScore[2] - robotScore[2]**2))
                # Add the euclidean distance of every point from the current point of interest into a list
                euclideanScores.append(dist)

            # Sort the list of scores and take the first k and put them in a list (smallest values)
            closestScores = (sorted(euclideanScores))[0:k]

            # Do the sparseness equation to determine the robot's novelty score - the mean of the score's distance from
            # it's k-nearest neighbors (defined as abs value of distance)
            novelty = np.mean(closestScores)

            pop[r].controller.novelty = novelty             # Set the controller's novelty score
            combinedScores.append([robotScore, novelty])    # Append the robot's score and novelty (for archive update)

        # Update the archive with the list of combined scores
        self.updateArchive(combinedScores)
        # Add all of the behavioral scores for this generation to the list of all behavioral scores
        self.allBehScores.append(currentBehScores)
        # Add all the novelty scores for this generation to the list of all novelty scores
        self.allNoveltyScores.append([robot.controller.novelty for robot in pop])

        # Print relevant values to the terminal
        # print(f"ROBOT SCORES,  generation {generation}:")
        # print("Behavior scores:", currentBehScores)
        # print("Novelty scores:", [round(robot.controller.novelty, 3) for robot in pop])
        # print("Archive Scores:", [[x[0], x[1], round(x[2], 2)] for x in self.behArchive])

    def updateArchive(self, combinedScores):
        """
        Update the archive to randomly include
        only the most novel new genotypes
        :param combinedScores: List of lists containing a generation's worth of [behavioral score, novelty score]
        :return: None
        """

        for score in combinedScores:
            # If the novelty score was greater than 5, add the beahvior associated with it to the archive with a
            # 50% probability (prevents archive from getting too large and search space from getting too constrained)
            if score[1] > 5 and random.random() < 0.5:
                self.behArchive.append(score[0])
