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
#
#  $Revision: 446 $
#  $Date: 2009-01-22 22:20:21 -0500 (Thu, 22 Jan 2009) $
#  $Author: brian@tannerpages.com $
#  $HeadURL: http://rl-glue-ext.googlecode.com/svn/trunk/projects/codecs/Python/src/rlglue/types.py $


import copy


class AbstractType(object):
    def __init__(self, num_ints=None, num_doubles=None, num_chars=None):
        self.intArray = []
        self.doubleArray = []
        self.charArray = []
        if num_ints is not None:
            self.intArray = [0] * num_ints
        if num_doubles is not None:
            self.doubleArray = [0.0] * num_doubles
        if num_chars is not None:
            self.charArray = [''] * num_chars

    def same_as(self, other):
        return self.intArray == other.intArray and \
               self.doubleArray == other.doubleArray and \
               self.charArray == other.charArray

    # this coolness added by btanner sept 30/2008
    # it allows the subclasses to be used like myAction=Action.fromAbstractType(someAbstractType)
    @classmethod
    def from_AbstractType(cls, abstract_type):
        ret_struct = cls()
        ret_struct.intArray = copy.deepcopy(abstract_type.intArray)
        ret_struct.doubleArray = copy.deepcopy(abstract_type.doubleArray)
        ret_struct.charArray = copy.deepcopy(abstract_type.charArray)
        return ret_struct


class Action(AbstractType):
    def __init__(self, num_ints=None, num_doubles=None, num_chars=None):
        AbstractType.__init__(self, num_ints, num_doubles, num_chars)


class Observation(AbstractType):
    def __init__(self, num_ints=None, num_doubles=None, num_chars=None):
        AbstractType.__init__(self, num_ints, num_doubles, num_chars)


class Observation_action(object):
    def __init__(self, observation=None, action=None):
        if observation is not None:
            self.o = observation
        else:
            self.o = Observation()
        if action is not None:
            self.a = action
        else:
            self.a = Action()


class Reward_observation_terminal(object):
    def __init__(self, reward=None, observation=None, terminal=None):
        if reward is not None:
            self.r = reward
        else:
            self.r = 0.0
        if observation is not None:
            self.o = observation
        else:
            self.o = Observation()
        if terminal is not None:
            self.terminal = terminal
        else:
            self.terminal = False


class Reward_observation_action_terminal(object):
    def __init__(self, reward=None, observation=None, action=None, terminal=None, converged=None):
        if reward is not None:
            self.r = reward
        else:
            self.r = 0.0
        if observation is not None:
            self.o = observation
        else:
            self.o = Observation()
        if action is not None:
            self.a = action
        else:
            self.a = Action()
        if terminal is not None:
            self.terminal = terminal
        else:
            self.terminal = False
        if converged is not None:
            self.converged = converged
        else:
            self.converged = 0
