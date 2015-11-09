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

import sys

import rlglued.network.network as network


class ClientEnvironment(object):
    kUnknownMessage = "Unknown Message: "
    network = None
    env = None

    # (agent) -> void
    def __init__(self, environment):
        self.env = environment
        self.network = network.Network()

    # () -> void
    def oninit(self):
        task_spec = self.env.init()
        self.network.clear_send_buffer()
        self.network.put_int(network.kEnvInit)
        self.network.put_int(len(task_spec) + 4)  # Also including the length put in by putString
        self.network.put_string(task_spec)

    # () -> void
    def onsetup(self):
        self.env.setup()
        self.network.clear_send_buffer()
        self.network.put_int(network.kEnvSetup)
        self.network.put_int(0)  # No data following this header

    # () -> void
    def onstart(self):
        observation = self.env.start()
        size = self.network.sizeof_Observation(observation)
        self.network.clear_send_buffer()
        self.network.put_int(network.kEnvStart)
        self.network.put_int(size)
        self.network.put_Observation(observation)

    # () -> void
    def onstep(self):
        action = self.network.get_Action()
        reward_observation = self.env.step(action)
        size = self.network.sizeof_RewardObservation(reward_observation)
        self.network.clear_send_buffer()
        self.network.put_int(network.kEnvStep)
        self.network.put_int(size)
        self.network.put_RewardObservation(reward_observation)

    # () -> void
    def oncleanup(self):
        self.env.cleanup()
        self.network.clear_send_buffer()
        self.network.put_int(network.kEnvCleanup)
        self.network.put_int(0)  # No data in this packet

    # () -> void
    def onmessage(self):
        message = self.network.get_string()
        reply = self.env.message(message)
        self.network.clear_send_buffer()
        self.network.put_int(network.kEnvMessage)
        if reply is None:
            # Brian Tanner added payload even for empty message (IE: send that the size is 0)
            self.network.put_int(4)
            self.network.put_int(0)
        else:
            # Brian Tanner, added 4 to the payload size because we putString sends the string AND its size
            self.network.put_int(len(reply) + 4)
            self.network.put_string(reply)

    # (string, int, int) -> void
    def connect(self, host, port, timeout):
        self.network.connect(host, port, timeout)
        self.network.clear_send_buffer()
        self.network.put_int(network.kEnvironmentConnection)
        self.network.put_int(0)  # No body to this packet
        self.network.send()

    # () -> void
    def close(self):
        self.network.close()

    # () -> void
    def run_event_loop(self):
        state = 0

        while state != network.kRLTerm:
            self.network.clear_recv_buffer()
            recv_size = self.network.recv(8) - 8  # We may have received the header and part of the payload
            # We need to keep track of how much of the payload was recv'd
            state = self.network.get_int()
            data_size = self.network.get_int()

            remaining = data_size - recv_size
            if remaining < 0:
                print("Remaining was less than 0!")
                remaining = 0

            amount_received = self.network.recv(remaining)

            # Already read the header, discard it
            self.network.get_int()
            self.network.get_int()

            switch = {
                network.kEnvInit: self.oninit,
                network.kEnvSetup: self.onsetup,
                network.kEnvStart: self.onstart,
                network.kEnvStep: self.onstep,
                network.kEnvCleanup: self.oncleanup,
                network.kEnvMessage: self.onmessage}
            if state in switch:
                switch[state]()
            elif state == network.kRLTerm:
                pass
            else:
                sys.stderr.write(network.kUnknownMessage % (str(state)))
                sys.exit(1)

            self.network.send()
