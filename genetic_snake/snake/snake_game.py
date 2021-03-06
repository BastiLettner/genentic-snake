# implements the snake game

import numpy as np
import os
import pygame
import time
import gin
import logging
from .snake import Snake
from .snake_environment import AppleGenerator, LANDSCAPE_OBJECTS

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


@gin.configurable
class SnakeGame(object):

    """ Represents the snake game. Includes planting apple, counting scores and moving the snake """

    def __init__(self,
                 snake,
                 seed=0,
                 v=logging.INFO,
                 max_steps_per_apple=1000,
                 render=False
                 ):
        """
        Construct a snake game.

        Args:
            snake(Snake): The snake
            v(int): Log level
            max_steps_per_apple(int): The max number of steps to find an apple. If apple is found counter gets reset
            render(bool): Display the game
        """
        self.snake = snake
        self.score = 0
        self.num_steps = 0
        self.seed = seed
        self.apple_generator = AppleGenerator(self.snake.landscape.size, seed=np.random.randint(0, 10000))
        self.logger = logging.getLogger("SnakeGame")
        self.logger.setLevel(level=v)
        self._steps_since_last_apple = 0
        self._max_steps_per_apple = max_steps_per_apple
        self._render = render
        if self._render:
            self.display, self.images = self._init_display()

    def play(self):
        """ Play a snake game. """

        self.plant_next_apple()
        current_snake_size = self.snake.size
        self.logger.debug(self.snake.landscape)
        if self._render:
            self.render()
            time.sleep(0.02)
        while self.snake.is_alive and self._steps_since_last_apple < self._max_steps_per_apple:

            self.snake.move()
            if current_snake_size != self.snake.size:  # snake ate apple
                self.plant_next_apple()
                self._steps_since_last_apple = 0
                current_snake_size = self.snake.size
            self.num_steps += 1
            self._steps_since_last_apple += 1
            self.score = len(self.snake.body) - 3  # three is the initial size
            self.logger.debug(self.snake.landscape)
            if self._render:
                self.render()
                time.sleep(0.01)
        self.logger.debug("Snake died after {} steps, reaching a score of {}".format(self.num_steps, self.score))
        return self.score

    def plant_next_apple(self):
        """ Plants a new apple """
        successful_plant = self.snake.landscape.plant_apple(self.apple_generator.__next__())
        while not successful_plant:
            successful_plant = self.snake.landscape.plant_apple(self.apple_generator.__next__())

    def render(self):
        self.display.fill((0, 0, 0))
        for loc, code in self.snake.landscape.world.items():
            x = loc.x
            y = loc.y
            self.display.blit(self.images[LANDSCAPE_OBJECTS[code]], (32*x, 32*y))
        pygame.display.flip()
        pygame.event.get()

    def _init_display(self):
        pygame.init()
        window_width = 32 * self.snake.landscape.size[0]
        window_height = 32 * self.snake.landscape.size[1]
        display_surf = pygame.display.set_mode((window_width, window_height))
        path = os.path.join(FILE_PATH, "..", "..", "images")
        snake_surf = pygame.image.load(
            path + "/snake.png"
        ).convert()
        apple_surf = pygame.image.load(
            path + "/apple.png"
        ).convert()
        blank_surf = pygame.image.load(
            path + "/blank.png"
        ).convert()

        images = {
            "meadow": blank_surf,
            "apple": apple_surf,
            "snake": snake_surf
        }

        return display_surf, images
