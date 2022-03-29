import sys

# path to folder which contains situsim_v1_2
sys.path.insert(1, '..')
from situsim_v1_2 import *


# the implementation of this sensor is a bit odd, but it is here for use by HungryRobots, which may want to adapt their
# behaviours depending on how close to death (hungry) they are. in general, an organism or human machine will not have
# direct knowledge of its energy level, and some kind of sensor(s) will need to be used to apprehend it.

# the reason i don't especially like the implementation of this is that the robot's energy level is a property of the
# robot, and the sensor detects that property for use in the robot's controller. technically, this results in a circular
# reference, which I would normally avoid, but for now it works as desired, so it will be fixed in later implementations
# but is fine for now.

# the advantage of implementing this as a Sensor is that we can attach different kinds of NoiseSources to it, to model
# various kinds of imperfect sensing
class RobotEnergySensor(Sensor):

    # construct energy sensor
    def __init__(self, robot, x, y, noisemaker=None):
        super().__init__(x=x, y=y)

        # sensor activation. this variable is updated in and returned from the step method. it is stored separately in
        # case you want to access it multiple times between simulation steps, although that is unlikely to be necessary
        self.activation = 0

        # for plotting and analysis, a sensor keeps a complete record of its activation over time
        self.activations = [self.activation]

        self.noisemaker = noisemaker
        self.robot = robot

    # step sensor
    def step(self, dt):
        super().step(dt)
        self.activation = self.robot.energy  # get robot's energy level

        # add noise, if a noisemaker is implemented
        if self.noisemaker is not None:
            self.activation += self.noisemaker.step(dt)

        self.activations.append(self.activation)  # store sensor activation

        return self.activation  # return sensor activation


# a subclass of Robot, which can sense and consume food and poison objects (Consumables), and which gains and loses
# energy in those two cases. An energy level sensor is implemented, but not used. the reason for implementing this is:
# the energy level might make a good choice for essential variable (if you want to use one), and it could be made one
# of the inputs to a controller, however, for biological agents in particular but human-made ones too, it is not
# possible to have perfect knowledge of internal states such as energy levels. Therefore, it would be more interesting
# if the input to the controller came from a sensor with some level and type of noise applied to it
class ForagingRobot(Robot):
    # construct robot
    def __init__(self, x, y, controller,
                 left_food_sources, right_food_sources,
                 left_poison_sources, right_poison_sources,
                 consumables, radius=1, theta=0,
                 initial_energy=100,
                 left_food_sensor_angle=np.pi / 4, right_food_sensor_angle=-np.pi / 4,
                 left_food_noisemaker=None, right_food_noisemaker=None,
                 food_field_of_view=2 * np.pi,
                 left_poison_sensor_angle=np.pi / 4, right_poison_sensor_angle=-np.pi / 4,
                 left_poison_noisemaker=None, right_poison_noisemaker=None,
                 poison_field_of_view=2 * np.pi,
                 decay_rate=0.1, decay_rate2=0.001,
                 max_speed=1, energy_sensor_noisemaker=None,
                 left_motor_noisemaker=None, right_motor_noisemaker=None,
                 left_motor_max_speed=2, right_motor_max_speed=2,
                 left_motor_inertia=0, right_motor_inertia=0,
                 left_motor_reversed=False, right_motor_reversed=False,
                 novelty=False      # Whether or not the robot is implementing novelty search
                 ):
        self.novelty = novelty      # Set self.novelty to parameter (boolean T/F robot implements novelty search)
        self.left_poison_sensor_angle = left_poison_sensor_angle
        self.right_poison_sensor_angle = right_poison_sensor_angle

        # construct left poison sensor. At this point, dummy positions are given for light sensors.
        # They will be fixed when the super constructor is called
        self.left_poison_sensor = LightSensor(light_sources=left_poison_sources, x=x, y=y,
                                              noisemaker=left_poison_noisemaker,
                                              field_of_view=poison_field_of_view)
        self.right_poison_sensor = LightSensor(light_sources=right_poison_sources, x=x, y=y,
                                               noisemaker=right_poison_noisemaker,
                                               field_of_view=poison_field_of_view)

        # there is a circular reference between robot and sensor - not ideal, but seems okay here
        self.energy_sensor = RobotEnergySensor(robot=self, x=x, y=y, noisemaker=energy_sensor_noisemaker)

        self.consumables = consumables  # a list of consumables which will affect this Robot

        self.behScore = 0               # Robot's score in the behavioral space (for novelty search)
        self.generation = 0             # What generation the robot is (for analysis purposes)
        self.foodEaten = 0              # How many food pellets the robot's eaten
        self.poisonEaten = 0            # How many poison pellets the robot's eaten

        # call Robot constructor. The LightSensors already implemented in Robot function as food sensors
        super().__init__(x=x, y=y, controller=controller,
                         radius=radius, theta=theta,
                         left_light_sources=left_food_sources,
                         right_light_sources=right_food_sources,
                         left_sensor_angle=left_food_sensor_angle,
                         right_sensor_angle=right_food_sensor_angle,
                         left_sensor_noisemaker=left_food_noisemaker,
                         right_sensor_noisemaker=right_food_noisemaker,
                         field_of_view=food_field_of_view,
                         left_motor_noisemaker=left_motor_noisemaker,
                         right_motor_noisemaker=right_motor_noisemaker,
                         left_motor_max_speed=left_motor_max_speed,
                         right_motor_max_speed=right_motor_max_speed,
                         left_motor_inertia=left_motor_inertia,
                         right_motor_inertia=right_motor_inertia,
                         left_motor_reversed=left_motor_reversed,
                         right_motor_reversed=right_motor_reversed
                         )

        self.left_sensor.color = 'darkgreen'  # set food sensor colours. poison sensor colours are left at default- red
        self.right_sensor.color = 'darkgreen'
        self.energy_sensor.color = 'yellow'     # set energy level sensor
        # If the robot uses novelty, make it's food sensors purple (for visual ID during animation)
        if novelty:
            self.right_poison_sensor.color = 'purple'
            self.left_poison_sensor.color = 'purple'
        # If the robot uses fitness, make its food sensors yellow (for visual ID during animation)
        elif not novelty:
            self.right_poison_sensor.color = 'yellow'
            self.left_poison_sensor.color = 'yellow'

        self.energy = initial_energy            # set initial energy level
        self.energies = [initial_energy]        # store energy level
        self.decay_rate = decay_rate            # rate at which energy decays when used by motors
        self.decay_rate2 = decay_rate2          # rate at which energy decays even if the motors are inactive

    # Method to keep the sensors attached to the bot
    def update_sensor_positions(self):
        super().update_sensor_positions()  # call Robot update method to update positions and angles for food sensors

        # update positions and angles for poison sensors
        self.left_poison_sensor.x = self.state[0] + (
                    self.radius * np.cos(self.state[2] + self.left_poison_sensor_angle))
        self.left_poison_sensor.y = self.state[1] + (
                    self.radius * np.sin(self.state[2] + self.left_poison_sensor_angle))
        self.left_poison_sensor.theta = self.thetas[-1] + self.left_poison_sensor_angle

        self.right_poison_sensor.x = self.state[0] + (
                    self.radius * np.cos(self.state[2] + self.right_poison_sensor_angle))
        self.right_poison_sensor.y = self.state[1] + (
                    self.radius * np.sin(self.state[2] + self.right_poison_sensor_angle))
        self.right_poison_sensor.theta = self.thetas[-1] + self.right_poison_sensor_angle

        # update position of energy sensor
        self.energy_sensor.x = self.state[0]
        self.energy_sensor.y = self.state[1]

    # step robot
    def step(self, dt):
        super().step(dt)  # call Robot's step function. note that the control method (below) gets called from there
        for consumable in self.consumables:
            if np.linalg.norm([self.x - consumable.x, self.y - consumable.y]) < consumable.radius+1 and not consumable.depleted:
                quantity = consumable.consume()
                if consumable.real_type == Consumables.food:
                    self.energy += quantity
                    self.foodEaten += 1
                elif consumable.real_type == Consumables.poison:
                    self.energy -= quantity
                    self.poisonEaten += 1
                # print('Energy: ' + str(self.energy))
        self.energies.append(self.energy)

    # this is separated from the step method as it is easier to override in any subclasses of Robot than step, which
    # should be the same for all Robots
    def control(self, dt):
        # update all sensor measurements
        left_food_activation = self.left_sensor.step(dt)
        right_food_activation = self.right_sensor.step(dt)
        left_poison_activation = self.left_poison_sensor.step(dt)
        right_poison_activation = self.right_poison_sensor.step(dt)
        energy_activation = self.energy_sensor.step(dt)

        # get motor speeds from controller
        left_speed, right_speed = self.controller.step([left_food_activation, right_food_activation,
                                                        left_poison_activation, right_poison_activation,
                                                        energy_activation], dt)

        # update energy. the faster the robot's wheels turn, the quicker it loses energy
        self.energy -= np.abs(left_speed) * dt * self.decay_rate
        self.energy -= np.abs(right_speed) * dt * self.decay_rate
        self.energy -= dt * self.decay_rate2    # some energy is lost even if the robot does not move
        self.energy = max(self.energy, 0)       # prevent energy falling below zero

        # if energy is zero, stop the motors
        if self.energy > 0:
            return left_speed, right_speed
        else:
            return 0, 0

    def setBehScore(self):
        """
        Set the robot's behavioral score - used to determine it's novelty score
        List of format [# of velocity spikes, # of acceleration spikes, mean velocity]
        :return: None
        """
        y = self.velocities
        vSpike = (abs(np.diff(y)) > 0.2)
        dy = np.gradient(y, 0.1)
        aSpike = (abs(np.diff(dy)) > 0.2)
        self.behScore = [vSpike.sum(), aSpike.sum(), np.mean(y)]

    # draw robot in the specified matplotlib axes
    def draw(self, ax):
        # call draw from super to draw Robot
        super().draw(ax)

        # the code that follows is just for drawing the additional pair of sensors
        self.left_poison_sensor.draw(ax)
        self.right_poison_sensor.draw(ax)

        self.draw_fov(self.left_poison_sensor, ax)
        self.draw_fov(self.right_poison_sensor, ax)

    # draw robot in a pygame display
    def pygame_draw(self, screen, scale, shiftx, shifty):
        # call draw from super to draw Robot
        super().pygame_draw(screen, scale, shiftx, shifty)

        # the code that follows is just for drawing the additional pair of sensors
        self.left_poison_sensor.pygame_draw(screen, scale, shiftx, shifty)
        self.right_poison_sensor.pygame_draw(screen, scale, shiftx, shifty)

        self.pygame_draw_fov(self.left_poison_sensor, screen, scale, shiftx, shifty)
        self.pygame_draw_fov(self.right_poison_sensor, screen, scale, shiftx, shifty)


# using an enum probably makes less sense in Python than it does in some other languages, as Python allows you to do
# pretty much anything you like to a variable, at any time you like, but the general idea is to use an enum to define
# and stick to a finite and constant set of values
class Consumables(Enum):
    food = 0
    poison = 1
    water = 2


# A consumable object, which can be placed in the environment, can be food, water or poison, and can be detected by
# LightSensors as it has a LightSource attached.
class Consumable(System):

    # construct consumable
    def __init__(self, x, y, radius=0.5, quantity=10, recovery_time=10, real_type=Consumables.food,
                 apparent_type=Consumables.food):
        super().__init__(x, y)  # call System constructor, to allow for the possibility that a Consumable will move
        self.stimulus = LightSource(x=x, y=y, brightness=3)  # construct LightSource
        self.quantity = quantity  # quantity determines how much of an effect consuming the item has on a HungryRobot

        # when an item is consumed, it can reappear when the recovery time expires. if you don't want it to recover,
        # then just make this time longer than your simulation duration
        self.recovery_time = recovery_time

        # initially, a Consumable is not depleted. When it is consumed,
        # it is depleted and will be invisible until (and if) it recovers
        self.depleted = False

        self.time_since_consumed = 0        # used to track time to recover
        self.radius = radius                # this is the radius within which a HungryRobot will consume it

        # conceptually, a consumable has a real and an apparent type. the apparent type is what it "looks" like, but the
        # real_type determines the effect it has. In the current implementation, apparent_type is unused, as it is the
        # stimulus which belongs to a Consumable which is passed to a Sensor - the Sensor simply detects what it
        # detects, and it is the business of the Controller to interpret it
        self.apparent_type = apparent_type
        self.real_type = real_type

    # step consumable. Consumables are stepped in order to implement recovery from depletion
    def step(self, dt):
        super().step(dt)  # call System step method, to allow for the possibility that a Consumable will move
        if self.depleted:  # if the Consumable has been depleted, then wait for recovery_time to replenish and make it detectable again
            if self.time_since_consumed >= self.recovery_time:  # if consumable has reached recovery_time
                self.depleted = False                           # replenish consumable
                self.stimulus.is_on = True                      # make consumable detectable again
            else:
                self.time_since_consumed += dt                  # increment time since consumable was depleted

    # when a HungryRobot passes within the Consumable's radius, it calls this method so that the resource is depleted
    def consume(self):
        if self.depleted:  # if already depleted, return zero
            return 0
        else:  # if not already depleted, return the quantity - determines how much of an effect will be had on the bot
            self.depleted = True            # set to depleted
            self.stimulus.is_on = False     # turn LightSource off, to make the Consumable invisible
            self.time_since_consumed = 0
            return self.quantity

    # draw consumable in the specified matplotlib axes
    def draw(self, ax):
        self.set_color()
        alpha = 1
        if self.depleted:   # Draws depleted items as outlines
            alpha = 0.3
        ax.add_artist(mpatches.Circle((self.x, self.y), self.radius, color=self.color, alpha=alpha))
        ax.plot(self.x, self.y, 'k.')

    def set_color(self):
        if self.real_type == Consumables.food:
            self.color = 'darkgreen'
        elif self.real_type == Consumables.water:
            self.color = 'blue'
        elif self.real_type == Consumables.poison:
            self.color = 'darkred'

    # draw consumable in a pygame display
    def pygame_draw(self, screen, scale, shiftx, shifty):
        self.set_color()
        width = 0
        if self.depleted:
            width = 2
        pygame.draw.circle(screen, center=(scale * self.x + shiftx, scale * self.y + shifty), color=self.color,
                           width=width, radius=scale * self.radius)
