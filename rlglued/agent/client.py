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
#  $HeadURL: http://rl-glue-ext.googlecode.com/svn/trunk/projects/codecs/Python/src/rlglue/agent/ClientAgent.py $

import sys

import rlglued.network.network as network


class ClientAgent(object):
    kUnknownMessage = "Unknown Message: "
    network = None
    agent = None

    # (agent) -> void
    def __init__(self, agent):
        self.agent = agent
        self.network = network.Network()

    # () -> void
    def oninit(self):
        taskSpec = self.network.get_string()
        self.agent.init(taskSpec)
        self.network.clear_send_buffer()
        self.network.put_int(network.kAgentInit)
        self.network.put_int(0)  # No data following this header

    # () -> void
    def onsetup(self):
        self.agent.setup()
        self.network.clear_send_buffer()
        self.network.put_int(network.kAgentSetup)
        self.network.put_int(0)  # No data following this header

    # () -> void
    def onstart(self):
        observation = self.network.get_Observation()
        action = self.agent.start(observation)
        size = self.network.sizeof_Action(action)
        self.network.clear_send_buffer()
        self.network.put_int(network.kAgentStart)
        self.network.put_int(size)
        self.network.put_Action(action)

    # () -> void
    def onstep(self):
        reward = self.network.get_double()
        observation = self.network.get_Observation()
        action = self.agent.step(reward, observation)
        size = self.network.sizeof_Action(action)
        self.network.clear_send_buffer()
        self.network.put_int(network.kAgentStep)
        self.network.put_int(size)
        self.network.put_Action(action)

    # () -> void
    def onend(self):
        reward = self.network.get_double()
        converged = self.agent.end(reward)
        self.network.clear_send_buffer()
        self.network.put_int(network.kAgentEnd)
        self.network.put_int(network.kIntSize)
        self.network.put_int(converged if converged is not None else 0)

    # () -> void
    def oncleanup(self):
        self.agent.cleanup()
        self.network.clear_send_buffer()
        self.network.put_int(network.kAgentCleanup)
        self.network.put_int(0)  # No data in this packet

    # () -> void
    def onmessage(self):
        message = self.network.get_string()
        reply = self.agent.message(message)
        self.network.clear_send_buffer()
        self.network.put_int(network.kAgentMessage)
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
        self.network.put_int(network.kAgentConnection)
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
                network.kAgentInit: self.oninit,
                network.kAgentSetup: self.onsetup,
                network.kAgentStart: self.onstart,
                network.kAgentStep: self.onstep,
                network.kAgentEnd: self.onend,
                network.kAgentCleanup: self.oncleanup,
                network.kAgentMessage: self.onmessage}
            if state in switch:
                switch[state]()
            elif state == network.kRLTerm:
                pass
            else:
                sys.stderr.write(network.kUnknownMessage % (str(state)))
                sys.exit(1)

            self.network.send()
