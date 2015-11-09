# 
# Copyright (C) 2008, Brian Tanner
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

import copy
from random import Random

from rlglued.agent.agent import Agent
from rlglued.agent import loader as agent_loader
from rlglued.types import Action
from rlglued.types import Observation


class SkeletonAgent(Agent):
    def __init__(self):
        self.rand_generator = Random()
        self.last_action = Action()
        self.last_observation = Observation()

    def init(self, task_spec):
        # See the sample_sarsa_agent in the mines-sarsa-example project for how to parse the task spec
        self.last_action = Action()
        self.last_observation = Observation()

    def start(self, observation):
        # Generate random action, 0 or 1
        int_action = self.rand_generator.randint(0, 1)
        return_action = Action()
        return_action.intArray = [int_action]

        last_action = copy.deepcopy(return_action)
        last_observation = copy.deepcopy(observation)

        return return_action

    def step(self, reward, observation):
        # Generate random action, 0 or 1
        int_action = self.rand_generator.randint(0, 1)
        return_action = Action()
        return_action.intArray = [int_action]

        last_action = copy.deepcopy(return_action)
        last_observation = copy.deepcopy(observation)

        return return_action

    def end(self, reward):
        pass

    def cleanup(self):
        pass

    def message(self, msg):
        if msg == "what is your name?":
            return "my name is SkeletonAgent, Python edition!"
        else:
            return "I don't know how to respond to your message"


if __name__ == "__main__":
    agent_loader.load_agent(SkeletonAgent())
