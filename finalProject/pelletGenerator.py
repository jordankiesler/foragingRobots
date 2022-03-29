import sys
import foragingRobot as FR

# This formatting allows imports to be used both in terminal and from IDE (PyCharm)
sys.path.insert(1, '..')
sys.path.insert(1, '../situsim_extensions')
from situsim_v1_2 import *


def generatePellets(pelletType, num, spacing, xStart, yStart):
    """
    Generate pellets placed in a horizontal row (consumables)
    :param pelletType: Poison, food, or water (enum from foragingRobot.py)
    :param num: How many pellets
    :param spacing: How far apart each pellet is
    :param xStart:  x-location of first pellet
    :param yStart: y-location of first pellet
    :return: list of pellet stimulus objects, list of pellet objects
    """
    pellets = []

    for x in range(xStart, xStart + (num * spacing), spacing):
        pell = FR.Consumable(x, yStart, quantity=num, recovery_time=1e2, real_type=pelletType, apparent_type=pelletType)
        pellets.append(pell)

    return [x.stimulus for x in pellets], pellets


def generateRandomPellets(food_num, poison_num, scale, brightness=3, seed=None):
    """
    Generate randomly placed pellets
    :param food_num: How many food pellets
    :param poison_num: How many poison pellets
    :param scale: Left/right/top/bottom bounds of pellet placement
    :param brightness: How bright the pellets are (how easily robot can find them) - defaults to 3
    :param seed: Random seed, for replicability (defaults to none)
    :return: List of food stimulus objects, list of pellet stimulus objects, list of all food and poison objects
    """

    # Stimuli are stored separately as the light source objects which the robot can see
    # Consumable objects are what the robots actually eat/interact with, hence the two different lists
    foods_and_poisons = []   # list of all food and poison objects
    foods_stimuli = []       # list of LightSources attached to food consumables, used by the robot's food sensors
    poisons_stimuli = []     # list of LightSources attached to poison consumables, used by the robot's poison sensors

    # generate food items
    for i in range(food_num):
        x = random_in_interval(-scale, scale, seed)
        y = random_in_interval(-scale, scale, seed)
        food = FR.Consumable(x, y, radius=0.5, recovery_time=1e2, quantity=5)
        food.stimulus.brightness = brightness
        foods_and_poisons.append(food)
        foods_stimuli.append(food.stimulus)

    # generate poison items
    for i in range(poison_num):
        x = random_in_interval(-scale, scale, seed)
        y = random_in_interval(-scale, scale, seed)
        poison = FR.Consumable(x, y, radius=0.5, recovery_time=1e2, quantity=5, real_type=FR.Consumables.poison)
        foods_and_poisons.append(poison)
        poisons_stimuli.append(poison.stimulus)

    return foods_stimuli, poisons_stimuli, foods_and_poisons


def generateCircleOfPellets(food_num, poison_num, food_radius, poison_radius):
    """
    Generate circles of food and poison pellets
    :param food_num: How many food pellets
    :param poison_num: How many poison pellets
    :param food_radius: Radius of the circle of food pellets (centered at origin)
    :param poison_radius: Radius of the circle of poison pellets (centered at origin)
    :return: List of food stimulus objects, list of pellet stimulus objects, list of all food and poison objects
    """

    foods_and_poisons = []  # list of all food and poison objects
    foods_stimuli = []      # list of LightSources attached to food consumables, used by the robot's food sensors
    poisons_stimuli = []    # list of LightSources attached to food consumables, used by the robot's poison sensors

    # generate food items
    for i in range(food_num):
        # Use math to set x and y values of food pellets in a circle
        a = i * 2 * np.pi / food_num
        food = FR.Consumable(food_radius * np.cos(a), food_radius * np.sin(a), radius=0.5, recovery_time=1e2, quantity=5)
        foods_and_poisons.append(food)
        foods_stimuli.append(food.stimulus)

    # generate poison items
    for i in range(poison_num):
        # Use math to set x and y values of food pellets in a circle
        a = i * 2 * np.pi / poison_num
        poison = FR.Consumable(poison_radius * np.cos(a), poison_radius * np.sin(a), radius=0.5, recovery_time=1e2,
                               quantity=5, real_type=FR.Consumables.poison)
        foods_and_poisons.append(poison)
        poisons_stimuli.append(poison.stimulus)

    return foods_stimuli, poisons_stimuli, foods_and_poisons
