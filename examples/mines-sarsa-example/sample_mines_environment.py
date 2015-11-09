# 
# Copyright (C) 2009, Brian Tanner
# 
# http://rl-glue-ext.googlecode.com/
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#  $Revision: 999 $
#  $Date: 2009-02-09 11:39:12 -0500 (Mon, 09 Feb 2009) $
#  $Author: brian@tannerpages.com $
#  $HeadURL: http://rl-library.googlecode.com/svn/trunk/projects/packages/examples/mines-sarsa-python/sample_mines_environment.py $

import random
from rlglued.environment.environment import Environment
from rlglued.environment import loader as environment_loader
from rlglued.types import Observation
from rlglued.types import Reward_observation_terminal


# This is a very simple discrete-state, episodic grid world that has
# exploding mines in it.  If the agent steps on a mine, the episode
# ends with a large negative reward.
# 
# The reward per step is -1, with +10 for exiting the game successfully
# and -100 for stepping on a mine.


# TO USE THIS Environment [order doesn't matter]
# NOTE: I'm assuming the Python codec is installed an is in your Python path
#   -  Start the rl_glue executable socket server on your computer
#   -  Run the SampleSarsaAgent and SampleExperiment from this or a
#   different codec (Matlab, Python, Java, C, Lisp should all be fine)
#   -  Start this environment like:
#   $> python sample_mines_environment.py

class MinesEnvironment(Environment):
    WORLD_FREE = 0
    WORLD_OBSTACLE = 1
    WORLD_MINE = 2
    WORLD_GOAL = 3

    def __init__(self):
        self.rand_generator = random.Random()
        self.fixed_start_state = False
        self.start_row = 1
        self.start_col = 1

        self.agent_row = 0
        self.agent_col = 0

        self.currentState = 10

        self.map = None

    def init(self):
        self.map = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 1, 1],
                    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

        # The Python task spec parser is not yet able to build task specs programmatically
        return "VERSION RL-Glue-3.0 PROBLEMTYPE episodic DISCOUNTFACTOR 1 OBSERVATIONS INTS (0 107) ACTIONS INTS (0 3)" \
               " REWARDS (-100.0 10.0) EXTRA SampleMinesEnvironment(C/C++) by Brian Tanner."

    def start(self):
        if self.fixed_start_state:
            state_valid = self.set_agent_state(self.start_row, self.start_col)
            if not state_valid:
                print "The fixed start state was NOT valid: " + str(int(self.start_row)) + "," + str(int(self.start_row))
                self.set_random_state()
        else:
            self.set_random_state()

        return_obs = Observation()
        return_obs.intArray = [self.calculate_flat_state()]

        return return_obs

    def step(self, action):
        # Make sure the action is valid
        assert len(action.intArray) == 1, "Expected 1 integer action."
        assert action.intArray[0] >= 0, "Expected action to be in [0,3]"
        assert action.intArray[0] < 4, "Expected action to be in [0,3]"

        self.update_position(action.intArray[0])

        obs = Observation()
        obs.intArray = [self.calculate_flat_state()]

        return_ro = Reward_observation_terminal()
        return_ro.r = self.calculate_reward()
        return_ro.o = obs
        return_ro.terminal = self.check_current_terminal()

        return return_ro

    def cleanup(self):
        pass

    def message(self, msg):
        # Message Description
        # 'set-random-start-state'
        # Action: Set flag to do random starting states (the default)
        if msg.startswith("set-random-start-state"):
            self.fixed_start_state = False
            return "Message understood.  Using random start state."

        # Message Description
        # 'set-start-state X Y'
        # Action: Set flag to do fixed starting states (row=X, col=Y)
        if msg.startswith("set-start-state"):
            split_string = msg.split(" ")
            self.start_row = int(split_string[1])
            self.start_col = int(split_string[2])
            self.fixed_start_state = True
            return "Message understood.  Using fixed start state."

        # Message Description
        # 'print-state'
        # Action: Print the map and the current agent location
        if msg.startswith("print-state"):
            self.print_state()
            return "Message understood.  Printed the state."

        return "SamplesMinesEnvironment(Python) does not respond to that message."

    def set_agent_state(self, row, col):
        self.agent_row = row
        self.agent_col = col

        return self.check_valid(row, col) and not self.check_terminal(row, col)

    def set_random_state(self):
        num_rows = len(self.map)
        num_cols = len(self.map[0])
        start_row = self.rand_generator.randint(0, num_rows - 1)
        start_col = self.rand_generator.randint(0, num_cols - 1)

        while not self.set_agent_state(start_row, start_col):
            start_row = self.rand_generator.randint(0, num_rows - 1)
            start_col = self.rand_generator.randint(0, num_cols - 1)

    def check_valid(self, row, col):
        valid = False
        num_rows = len(self.map)
        num_cols = len(self.map[0])

        if num_rows > row >= 0 and num_cols > col >= 0:
            if self.map[row][col] != self.WORLD_OBSTACLE:
                valid = True
        return valid

    def check_terminal(self, row, col):
        if self.map[row][col] == self.WORLD_GOAL or self.map[row][col] == self.WORLD_MINE:
            return True
        return False

    def check_current_terminal(self):
        return self.check_terminal(self.agent_row, self.agent_col)

    def calculate_flat_state(self):
        num_rows = len(self.map)
        return self.agent_col * num_rows + self.agent_row

    def update_position(self, action):
        # When the move would result in hitting an obstacles, the agent simply doesn't move
        new_row = self.agent_row
        new_col = self.agent_col

        if action == 0:  # move down
            new_col = self.agent_col - 1

        if action == 1:  # move up
            new_col = self.agent_col + 1

        if action == 2:  # move left
            new_row = self.agent_row - 1

        if action == 3:  # move right
            new_row = self.agent_row + 1

        # Check if new position is out of bounds or inside an obstacle
        if self.check_valid(new_row, new_col):
            self.agent_row = new_row
            self.agent_col = new_col

    def calculate_reward(self):
        if self.map[self.agent_row][self.agent_col] == self.WORLD_GOAL:
            return 10.0
        if self.map[self.agent_row][self.agent_col] == self.WORLD_MINE:
            return -100.0
        return -1.0

    def print_state(self):
        num_rows = len(self.map)
        num_cols = len(self.map[0])
        print "Agent is at: " + str(self.agent_row) + "," + str(self.agent_col)
        print "Columns:0-10                10-17"
        print "Col    ",
        for col in range(0, num_cols):
            print col % 10,

        for row in range(0, num_rows):
            print
            print "Row: " + str(row) + " ",
            for col in range(0, num_cols):
                if self.agent_row == row and self.agent_col == col:
                    print "A",
                else:
                    if self.map[row][col] == self.WORLD_GOAL:
                        print "G",
                    if self.map[row][col] == self.WORLD_MINE:
                        print "M",
                    if self.map[row][col] == self.WORLD_OBSTACLE:
                        print "*",
                    if self.map[row][col] == self.WORLD_FREE:
                        print " ",
        print


if __name__ == "__main__":
    environment_loader.load_environment(MinesEnvironment())
