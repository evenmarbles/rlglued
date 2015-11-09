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
#  $Revision: 446 $
#  $Date: 2009-01-22 22:20:21 -0500 (Thu, 22 Jan 2009) $
#  $Author: brian@tannerpages.com $
#  $HeadURL: http://rl-glue-ext.googlecode.com/svn/trunk/projects/codecs/Python/src/rlglue/agent/Agent.py $


class Agent(object):
    # (string) -> void
    def init(self, task_spec):
        pass

    # () -> void
    def setup(self):
        pass

    # (Observation) -> Action
    def start(self, observation):
        pass

    # (double, Observation) -> Action
    def step(self, reward, observation):
        pass

    # (double) -> int
    def end(self, reward):
        pass

    # () -> void
    def cleanup(self):
        pass

    # (string) -> string
    def message(self, msg):
        pass
