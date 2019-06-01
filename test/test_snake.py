# Test the snake and its components

import os
import unittest
import numpy as np
from genetic_snake.snake.snake import Snake
from genetic_snake.util import Coordinate
from genetic_snake.snake.snake_brain import BinaryNeuralNetwork


class TestSnake(unittest.TestCase):

    """ Test the snake """

    def test_creation(self):
        """ Test that the snake is correctly place in the landscape. """
        snake = Snake()
        self.assertEqual(snake.size, 3)
        self.assertTrue(snake.is_alive)
        self.assertEqual(snake.landscape.world[Coordinate(0, 0)], 1)
        self.assertEqual(snake.landscape.world[Coordinate(1, 0)], 1)
        self.assertEqual(snake.landscape.world[Coordinate(2, 0)], 1)


class TestSnakeAction(unittest.TestCase):

    """ Test the snake actions """

    def test_take_action_left(self):
        """ Test take action left. Snake should be dead afterwards """
        snake = Snake()
        snake.act(0)  # move left
        self.assertEqual(snake.landscape.world[Coordinate(0, 0)], 0)
        self.assertEqual(snake.landscape.world[Coordinate(1, 0)], 1)
        self.assertEqual(snake.landscape.world[Coordinate(2, 0)], 1)
        self.assertFalse(snake.is_alive)

    def test_take_action_right(self):
        """ Test take action right. Snake should be alive afterwards """
        snake = Snake()
        snake.act(1)  # move right
        self.assertEqual(snake.landscape.world[Coordinate(0, 0)], 0)
        self.assertEqual(snake.landscape.world[Coordinate(1, 0)], 1)
        self.assertEqual(snake.landscape.world[Coordinate(2, 0)], 1)
        self.assertEqual(snake.landscape.world[Coordinate(3, 0)], 1)
        self.assertTrue(snake.is_alive)

    def test_take_action_up(self):
        """ Test take action up. Snake should be dead afterwards"""
        snake = Snake()
        snake.act(2)  # move up
        self.assertEqual(snake.landscape.world[Coordinate(0, 0)], 1)
        self.assertEqual(snake.landscape.world[Coordinate(1, 0)], 1)
        self.assertEqual(snake.landscape.world[Coordinate(2, 0)], 1)
        self.assertFalse(snake.is_alive)

    def test_take_action_down(self):
        """ Test take action up. Snake should be alive afterwards"""
        snake = Snake()
        snake.act(3)  # move down
        self.assertEqual(snake.landscape.world[Coordinate(0, 0)], 0)
        self.assertEqual(snake.landscape.world[Coordinate(1, 0)], 1)
        self.assertEqual(snake.landscape.world[Coordinate(2, 0)], 1)
        self.assertEqual(snake.landscape.world[Coordinate(2, 1)], 1)
        self.assertTrue(snake.is_alive)

    def test_eat_apple(self):
        """ Test that the snake increases in size when eating the apple"""
        snake = Snake()
        snake.landscape.plant_apple(Coordinate(3, 0))
        snake.act(1)  # move into the apple
        self.assertEqual(snake.landscape.world[Coordinate(0, 0)], 1)
        self.assertEqual(snake.landscape.world[Coordinate(1, 0)], 1)
        self.assertEqual(snake.landscape.world[Coordinate(2, 0)], 1)
        self.assertEqual(snake.landscape.world[Coordinate(3, 0)], 1)
        self.assertEqual(len(snake.body), 4)


class TestSnakeSensor(unittest.TestCase):

    """ Test the snake sensors """

    def test_distance_sensor(self):
        """ Test the sensor measuring distance """
        snake = Snake()
        snake.landscape.plant_apple(Coordinate(5, 0))
        perception = snake.sense()
        vision = perception["DistanceSensor"].tolist()
        expected_vision = [1/13, 1/3, 0, 1/3, 0, 1, 1/15, 0, 0, 1, 0, 0, 1/13, 0, 0, 1/3, 0, 0, 1, 0, 0, 1, 0, 0]
        for v, v_ in zip(vision, expected_vision):
            self.assertAlmostEqual(v, v_)

        snake.act(3)  # move down
        perception = snake.sense()
        vision = perception["DistanceSensor"].tolist()
        expected_vision = [1/13, 0, 0, 1/3, 0, 0, 1/14, 0, 0, 1/2, 0, 1, 1/13, 0, 0, 1/3, 0, 0, 1/2, 0, 0, 1/2, 0, 1]
        for v, v_ in zip(vision, expected_vision):
            self.assertAlmostEqual(v, v_)


class TestBinaryNN(unittest.TestCase):

    """ Test the binary Neural Network """

    def test_build(self):
        """ The the correct construction of weight and bias """
        brain = BinaryNeuralNetwork(
            hidden=(32, 32),
            state_size=10,
            action_size=3,
            activations=np.tanh
        )
        self.assertEqual(len(brain.weights), 3)
        self.assertEqual(len(brain.bias), 3)
        self.assertEqual(brain.weights["layer1-kernel"].shape, (32, 10))
        self.assertEqual(brain.bias["layer1-bias"].shape, (32, ))
        self.assertEqual(brain.weights["layer2-kernel"].shape, (32, 32))
        self.assertEqual(brain.bias["layer2-bias"].shape, (32, ))
        self.assertEqual(brain.weights["layer3-kernel"].shape, (3, 32))
        self.assertEqual(brain.bias["layer3-bias"].shape, (3, ))

        # check initialization of kernels
        for _, kernel in brain.weights.items():
            kernel_shape_x, kernel_shape_y = kernel.shape
            for i in range(kernel_shape_x):
                for j in range(kernel_shape_y):
                    self.assertTrue(kernel[i, j] in [1.0, -1.0])

    def tearDown(self):
         if os.path.isfile("test.h5"):
            os.remove("test.h5")

    def test_save_and_restore(self):
        """ Test saving and restoring """

        brain = BinaryNeuralNetwork(
            hidden=(32, 32),
            state_size=10,
            action_size=3,
            activations=np.tanh
        )

        brain.save(name="test")

        restored_brain = BinaryNeuralNetwork(
            hidden=(32, 32),
            state_size=10,
            action_size=3,
            activations=np.tanh,
            restore="test"
        )

        np.testing.assert_array_equal(brain.weights["layer1-kernel"], restored_brain.weights["layer1-kernel"])
        np.testing.assert_array_equal(brain.weights["layer2-kernel"], restored_brain.weights["layer2-kernel"])
        np.testing.assert_array_equal(brain.weights["layer3-kernel"], restored_brain.weights["layer3-kernel"])
        np.testing.assert_array_equal(brain.bias["layer1-bias"], restored_brain.bias["layer1-bias"])
        np.testing.assert_array_equal(brain.bias["layer2-bias"], restored_brain.bias["layer2-bias"])
        np.testing.assert_array_equal(brain.bias["layer3-bias"], restored_brain.bias["layer3-bias"])

    def test_decide(self):
        """ Test forward pass """

        brain = BinaryNeuralNetwork(
            hidden=(32, 32),
            state_size=10,
            action_size=3,
            activations=np.tanh
        )
        action = brain.decide(reason={"vision": np.arange(10)})
        self.assertTrue(isinstance(action, int))
        self.assertTrue(action in [0, 1, 2])



if __name__ == '__main__':
    unittest.main()