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
#  $Revision: 1011 $
#  $Date: 2009-02-12 00:29:54 -0500 (Thu, 12 Feb 2009) $
#  $Author: brian@tannerpages.com $
#  $HeadURL: http://rl-library.googlecode.com/svn/trunk/projects/packages/examples/mines-sarsa-python/sample_sarsa_agent.py $

import copy
import pickle
from rlglued.agent.agent import Agent
from rlglued.agent import loader as agent_loader
from rlglued.types import Action
from rlglued.types import Observation
from rlglued.utils import taskspecvrlglue3
from random import Random


# This is a very simple Sarsa agent for discrete-action, discrete-state
# environments.  It uses epsilon-greedy exploration.
# 
# We've made a decision to store the previous action and observation in 
# their raw form, as structures.  This code could be simplified and you
# could store them just as ints.


# TO USE THIS Agent [order doesn't matter]
# NOTE: I'm assuming the Python codec is installed an is in your Python path
#   -  Start the rl_glue executable socket server on your computer
#   -  Run the SampleMinesEnvironment and SampleExperiment from this or a
#   different codec (Matlab, Python, Java, C, Lisp should all be fine)
#   -  Start this agent like:
#   $> python sample_sarsa_agent.py

class SarsaAgent(Agent):
    def __init__(self):
        self.randGenerator = Random()
        self.lastAction = Action()
        self.lastObservation = Observation()
        self.sarsa_stepsize = 0.1
        self.sarsa_epsilon = 0.1
        self.sarsa_gamma = 1.0
        self.numStates = 0
        self.numActions = 0
        self.value_function = None

        self.policyFrozen = False
        self.exploringFrozen = False

    def init(self, task_spec_string):
        task_spec = taskspecvrlglue3.TaskSpecParser(task_spec_string)
        if task_spec.valid:
            assert len(task_spec.get_int_obs()) == 1, "expecting 1-dimensional discrete observations"
            assert len(task_spec.get_double_obs()) == 0, "expecting no continuous observations"
            assert not task_spec.is_special(
                task_spec.get_int_obs()[0][0]), " expecting min observation to be a number not a special value"
            assert not task_spec.is_special(
                task_spec.get_int_obs()[0][1]), " expecting max observation to be a number not a special value"
            self.numStates = task_spec.get_int_obs()[0][1] + 1

            assert len(task_spec.get_int_act()) == 1, "expecting 1-dimensional discrete actions"
            assert len(task_spec.get_double_act()) == 0, "expecting no continuous actions"
            assert not task_spec.is_special(
                task_spec.get_int_act()[0][0]), " expecting min action to be a number not a special value"
            assert not task_spec.is_special(
                task_spec.get_int_act()[0][1]), " expecting max action to be a number not a special value"
            self.numActions = task_spec.get_int_act()[0][1] + 1

            self.value_function = [self.numActions * [0.0] for i in range(self.numStates)]

        else:
            print "Task Spec could not be parsed: " + task_spec_string

        self.lastAction = Action()
        self.lastObservation = Observation()

    def egreedy(self, state):
        if not self.exploringFrozen and self.randGenerator.random() < self.sarsa_epsilon:
            return self.randGenerator.randint(0, self.numActions - 1)

        return self.value_function[state].index(max(self.value_function[state]))

    def start(self, observation):
        state = observation.intArray[0]
        action = self.egreedy(state)
        return_action = Action()
        return_action.intArray = [action]

        self.lastAction = copy.deepcopy(return_action)
        self.lastObservation = copy.deepcopy(observation)

        return return_action

    def step(self, reward, observation):
        state = observation.intArray[0]
        last_state = self.lastObservation.intArray[0]
        last_action = self.lastAction.intArray[0]

        action = self.egreedy(state)

        Q_sa = self.value_function[last_state][last_action]
        Q_sprime_aprime = self.value_function[state][action]

        new_Q_sa = Q_sa + self.sarsa_stepsize * (reward + self.sarsa_gamma * Q_sprime_aprime - Q_sa)

        if not self.policyFrozen:
            self.value_function[last_state][last_action] = new_Q_sa

        return_action = Action()
        return_action.intArray = [action]

        self.lastAction = copy.deepcopy(return_action)
        self.lastObservation = copy.deepcopy(observation)

        return return_action

    def end(self, reward):
        last_state = self.lastObservation.intArray[0]
        last_action = self.lastAction.intArray[0]

        Q_sa = self.value_function[last_state][last_action]

        new_Q_sa = Q_sa + self.sarsa_stepsize * (reward - Q_sa)

        if not self.policyFrozen:
            self.value_function[last_state][last_action] = new_Q_sa

    def cleanup(self):
        pass

    def save_value_function(self, filename):
        f = open(filename, "w")
        pickle.dump(self.value_function, f)
        f.close()

    def load_value_function(self, filename):
        f = open(filename, "r")
        self.value_function = pickle.load(f)
        f.close()

    def message(self, mssg):

        # Message Description
        # 'freeze learning'
        # Action: Set flag to stop updating policy
        #
        if mssg.startswith("freeze learning"):
            self.policyFrozen = True
            return "message understood, policy frozen"

        # Message Description
        # unfreeze learning
        # Action: Set flag to resume updating policy
        #
        if mssg.startswith("unfreeze learning"):
            self.policyFrozen = False
            return "message understood, policy unfrozen"

        # Message Description
        # freeze exploring
        # Action: Set flag to stop exploring (greedy actions only)
        #
        if mssg.startswith("freeze exploring"):
            self.exploringFrozen = True
            return "message understood, exploring frozen"

        # Message Description
        # unfreeze exploring
        # Action: Set flag to resume exploring (e-greedy actions)
        #
        if mssg.startswith("unfreeze exploring"):
            self.exploringFrozen = False
            return "message understood, exploring frozen"

        # Message Description
        # save_policy FILENAME
        # Action: Save current value function in binary format to
        # file called FILENAME
        #
        if mssg.startswith("save_policy"):
            split_string = mssg.split(" ")
            self.save_value_function(split_string[1])
            print "Saved."
            return "message understood, saving policy"

        # Message Description
        # load_policy FILENAME
        # Action: Load value function in binary format from
        # file called FILENAME
        #
        if mssg.startswith("load_policy"):
            split_string = mssg.split(" ")
            self.load_value_function(split_string[1])
            print "Loaded."
            return "message understood, loading policy"

        return "SampleSarsaAgent(Python) does not understand your message."


if __name__ == "__main__":
    agent_loader.load_agent(SarsaAgent())
