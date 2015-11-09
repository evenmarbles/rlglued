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
#  $Revision: 473 $
#  $Date: 2009-01-29 22:50:12 -0500 (Thu, 29 Jan 2009) $
#  $Author: brian@tannerpages.com $
#  $HeadURL: http://rl-glue-ext.googlecode.com/svn/trunk/projects/codecs/Python/src/rlglue/RLGlue.py $

import sys
import os

import rlglued.network.network as network
from rlglued.types import Observation_action
from rlglued.types import Reward_observation_action_terminal

from rlglued.versions import get_svn_codec_version
from rlglued.versions import get_codec_version


class RLGlue(object):
    def __init__(self):
        self._network = None

    # () -> void
    def force_connection(self):
        if self._network is None:
            svn_version = get_svn_codec_version()
            codec_version = get_codec_version()

            host_string = os.getenv("RLGLUED_HOST")
            port_string = os.getenv("RLGLUED_PORT")

            host = network.kLocalHost
            if host_string is not None:
                host = host_string

            try:
                port = int(port_string)
            except TypeError:
                port = network.kDefaultPort

            print "RL-Glue Python Experiment Codec Version: " + codec_version + " (Build " + svn_version + ")"
            print "\tConnecting to " + host + " on port " + str(port) + "..."
            sys.stdout.flush()

            self._network = network.Network()
            self._network.connect(host, port)
            self._network.clear_send_buffer()
            self._network.put_int(network.kExperimentConnection)
            self._network.put_int(0)
            self._network.send()

    # (int) -> void
    def do_standard_recv(self, state):
        self._network.clear_recv_buffer()
        recv_size = self._network.recv(8) - 8

        glue_state = self._network.get_int()
        data_size = self._network.get_int()
        remaining = data_size - recv_size

        if remaining < 0:
            remaining = 0

        remaining_received = self._network.recv(remaining)

        # Already read the header, so discard it
        self._network.get_int()
        self._network.get_int()

        if glue_state != state:
            sys.stderr.write(
                "Not synched with server. glueState = " + str(glue_state) + " but should be " + str(state) + "\n")
            sys.exit(1)

    # (int) -> void
    def do_call_with_no_params(self, state):
        self._network.clear_send_buffer()
        self._network.put_int(state)
        self._network.put_int(0)
        self._network.send()

    # Brian Tanner... need to make this return a string
    # () -> string
    def init(self):
        self.force_connection()
        self.do_call_with_no_params(network.kRLInit)
        self.do_standard_recv(network.kRLInit)
        # Brian Tanner added
        task_spec = self._network.get_string()
        return task_spec

    # () -> Observation_action
    def start(self):
        self.do_call_with_no_params(network.kRLStart)
        self.do_standard_recv(network.kRLStart)
        obsact = Observation_action()
        obsact.o = self._network.get_Observation()
        obsact.a = self._network.get_Action()
        return obsact

    # () -> Reward_observation_action_terminal
    def step(self):
        self.do_call_with_no_params(network.kRLStep)
        self.do_standard_recv(network.kRLStep)
        roat = Reward_observation_action_terminal()
        roat.terminal = self._network.get_int()
        roat.r = self._network.get_double()
        roat.o = self._network.get_Observation()
        roat.a = self._network.get_Action()
        return roat

    # () -> void
    def cleanup(self):
        self.do_call_with_no_params(network.kRLCleanup)
        self.do_standard_recv(network.kRLCleanup)

    # (string) -> string
    def agent_message(self, msg):
        if msg is None:
            msg = ""
        self.force_connection()
        self._network.clear_send_buffer()
        self._network.put_int(network.kRLAgentMessage)
        # Payload Size
        self._network.put_int(len(msg) + 4)
        self._network.put_string(msg)
        self._network.send()
        self.do_standard_recv(network.kRLAgentMessage)
        response = self._network.get_string()
        return response

    # (string) -> string
    def env_message(self, msg):
        if msg is None:
            msg = ""
        self.force_connection()
        self._network.clear_send_buffer()
        self._network.put_int(network.kRLEnvMessage)
        # Payload Size
        self._network.put_int(len(msg) + 4)
        self._network.put_string(msg)
        self._network.send()
        self.do_standard_recv(network.kRLEnvMessage)
        response = self._network.get_string()
        return response

    # () -> double
    def reward_return(self):
        self.do_call_with_no_params(network.kRLReturn)
        self.do_standard_recv(network.kRLReturn)
        reward = self._network.get_double()
        return reward

    # () -> int
    def num_steps(self):
        self.do_call_with_no_params(network.kRLNumSteps)
        self.do_standard_recv(network.kRLNumSteps)
        nsteps = self._network.get_int()
        return nsteps

    # () -> int
    def num_episodes(self):
        self.do_call_with_no_params(network.kRLNumEpisodes)
        self.do_standard_recv(network.kRLNumEpisodes)
        nepisodes = self._network.get_int()
        return nepisodes

    # Brian Tanner needs to make this return an int
    # (int) -> int
    def run_episode(self, nsteps):
        self._network.clear_send_buffer()
        self._network.put_int(network.kRLEpisode)
        self._network.put_int(network.kIntSize)
        self._network.put_int(nsteps)
        self._network.send()
        self.do_standard_recv(network.kRLEpisode)
        # Brian Tanner added
        exit_status = self._network.get_int()
        converged = self._network.get_int()
        return exit_status, converged


class RLGlueLocal(object):
    def __init__(self, env, agent):
        self._env = env
        self._agent = agent

        self._episode_count = 0
        self._step_count = 0
        self._total_reward = 0.0
        self._prevact = None

    def init(self):
        self._episode_count = 0
        self._step_count = 0
        self._total_reward = 0.0
        self._prevact = None

        task_spec_response = self._env.init()
        self._agent.init(task_spec_response)
        return task_spec_response

    def setup(self):
        self._env.setup()
        self._agent.setup()

    def start(self):
        self._step_count = 1
        self._total_reward = 0.0
        self._prevact = None

        obsact = Observation_action()
        obsact.o = self._env.start()
        obsact.a = self._agent.start(obsact.o)

        self._prevact = obsact.a
        return obsact

    def step(self):
        if self._prevact is None:
            self.start()

        rot = self._env.step(self._prevact)

        roat = Reward_observation_action_terminal()
        roat.o = rot.o
        roat.r = rot.r
        roat.terminal = rot.terminal

        self._total_reward += rot.r

        if rot.terminal == 1:
            self._episode_count += 1
            converged = self._agent.end(rot.r)
            roat.converged = converged if converged is not None else 0
            self._prevact = None
        else:
            self._step_count += 1
            self._prevact = self._agent.step(rot.r, rot.o)
            roat.a = self._prevact

        return roat

    def cleanup(self):
        self._agent.cleanup()
        self._env.cleanup()

    def agent_message(self, message):
        self._agent.message(message if message is not None else '')

    def env_message(self, message):
        self._env.message(message if message is not None else '')

    def reward_return(self):
        return self._total_reward

    def num_steps(self):
        return self._step_count

    def num_episodes(self):
        return self._episode_count

    def run_episode(self, num_steps):
        exit_status = 0
        converged = 0

        self.setup()
        self.start()
        while exit_status != 1:
            step_response = self.step()
            if 0 < num_steps <= self._step_count:
                break
            exit_status = step_response.terminal
            converged = step_response.converged
        return exit_status, converged


