# 
# Copyright (C) 2007, Mark Lee
# 
# http://rl-glue-ext.googlecode.com/
#
# Licensed under the Apache License, Version 2.0 (the "License");
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

from rlglued.environment.environment import Environment
from rlglued.environment import loader as environment_loader
from rlglued.types import Observation
from rlglued.types import Reward_observation_terminal


# /**
#  *  This is a very simple environment with discrete observations corresponding to states labeled {0,1,...,19,20}
#     The starting state is 10.
# 
#     There are 2 actions = {0,1}.  0 decrements the state, 1 increments the state.
# 
#     The problem is episodic, ending when state 0 or 20 is reached, giving reward -1 or +1, respectively.
#     The reward is 0 on all other steps.
#  * @author Brian Tanner
#  */

class SkeletonEnvironment(Environment):

    def __init__(self):
        self.current_state = 10

    def init(self):
        return "VERSION RL-Glue-3.0 PROBLEMTYPE episodic DISCOUNTFACTOR 1.0 OBSERVATIONS INTS (0 20) " \
               " ACTIONS INTS (0 1)  REWARDS (-1.0 1.0)  EXTRA SkeletonEnvironment(Python) by Brian Tanner."

    def start(self):
        self.current_state = 10

        return_obs = Observation()
        return_obs.intArray = [self.current_state]

        return return_obs

    def step(self, action):
        episode_over = 0
        reward = 0

        if action.intArray[0] == 0:
            self.current_state -= 1
        if action.intArray[0] == 1:
            self.current_state += 1

        if self.current_state <= 0:
            self.current_state = 0
            reward = -1
            episode_over = 1

        if self.current_state >= 20:
            self.current_state = 20
            reward = 1
            episode_over = 1

        obs = Observation()
        obs.intArray = [self.current_state]

        return_ro = Reward_observation_terminal()
        return_ro.r = reward
        return_ro.o = obs
        return_ro.terminal = episode_over

        return return_ro

    def cleanup(self):
        pass

    def message(self, msg):
        if msg == "what is your name?":
            return "my name is SkeletonEnvironment, Python edition!"
        else:
            return "I don't know how to respond to your message"


if __name__ == "__main__":
    environment_loader.load_environment(SkeletonEnvironment())
