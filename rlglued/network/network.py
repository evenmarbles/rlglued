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
#  $Revision: 592 $
#  $Date: 2009-02-04 18:24:59 -0500 (Wed, 04 Feb 2009) $
#  $Author: brian@tannerpages.com $
#  $HeadURL: http://rl-glue-ext.googlecode.com/svn/trunk/projects/codecs/Python/src/rlglue/network/Network.py $

#
# The Network class is defined in here
#

import socket
import struct
import time
import StringIO

try:
    import numpy

    numpy_int_type = numpy.dtype('int32').newbyteorder('>')
    numpy_float_type = numpy.dtype('float64').newbyteorder('>')
    numpy_char_type = 'S1'  # numpy.dtype('uint8').newbyteorder('>')
except:
    pass

from rlglued.types import Action
from rlglued.types import Observation
from rlglued.types import AbstractType

# RL-Glue needs to know what type of object is trying to connect.
kExperimentConnection = 1
kAgentConnection = 2
kEnvironmentConnection = 3

kAgentInit = 4      # agent_* start by sending one of these values
kAgentSetup = 5     # to the client to let it know what type of
kAgentStart = 6     # event to respond to
kAgentStep = 7
kAgentEnd = 8
kAgentCleanup = 9
kAgentMessage = 10

kEnvInit = 11
kEnvSetup = 12
kEnvStart = 13
kEnvStep = 14
kEnvCleanup = 15
kEnvMessage = 19

kRLInit = 20
kRLStart = 21
kRLStep = 22
kRLCleanup = 23
kRLReturn = 24
kRLNumSteps = 25
kRLNumEpisodes = 26
kRLEpisode = 27
kRLAgentMessage = 33
kRLEnvMessage = 34

kRLTerm = 35

kLocalHost = "127.0.0.1"
kDefaultPort = 4096
kRetryTimeout = 2

kDefaultBufferSize = 4096
kIntSize = 4
kDoubleSize = 8
kCharSize = 1

kUnknownMessage = "Unknown Message: %s\n"


class Network(object):
    def __init__(self):
        self.sock = None
        self.recv_buffer = StringIO.StringIO('')
        self.send_buffer = StringIO.StringIO('')

        if 'numpy' in globals():
            self.get_AbstractType = self.get_AbstractType_numpy
        else:
            self.get_AbstractType = self.get_AbstractType_list

    def connect(self, host=kLocalHost, port=kDefaultPort, retry_timeout=kRetryTimeout):
        while self.sock is None:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.sock.connect((host, port))
            except socket.error:
                self.sock = None
                time.sleep(retry_timeout)
            else:
                break

    def close(self):
        self.sock.close()

    def send(self):
        self.sock.sendall(self.send_buffer.getvalue())

    def recv(self, size):
        s = ''
        while len(s) < size:
            s += self.sock.recv(size - len(s))
        self.recv_buffer.write(s)
        self.recv_buffer.seek(0)
        return len(s)

    def clear_send_buffer(self):
        self.send_buffer.close()
        self.send_buffer = StringIO.StringIO()

    def clear_recv_buffer(self):
        self.recv_buffer.close()
        self.recv_buffer = StringIO.StringIO()

    def flip_send_buffer(self):
        self.clear_send_buffer()

    def flip_recv_buffer(self):
        self.clear_recv_buffer()

    def get_int(self):
        s = self.recv_buffer.read(kIntSize)
        return struct.unpack("!i", s)[0]

    def get_double(self):
        s = self.recv_buffer.read(kDoubleSize)
        return struct.unpack("!d", s)[0]

    def get_string(self):
        # If you read 0 you get "" not None so that's fine
        length = self.get_int()
        return self.recv_buffer.read(length)

    def get_AbstractType_list(self):
        num_ints = self.get_int()
        num_doubles = self.get_int()
        num_chars = self.get_int()
        return_struct = AbstractType()

        if num_ints > 0:
            s = self.recv_buffer.read(num_ints * kIntSize)
            return_struct.intArray = list(struct.unpack("!%di" % num_ints, s))
        if num_doubles > 0:
            s = self.recv_buffer.read(num_doubles * kDoubleSize)
            return_struct.doubleArray = list(struct.unpack("!%dd" % num_doubles, s))
        if num_chars > 0:
            s = self.recv_buffer.read(num_chars * kCharSize)
            return_struct.charArray = list(struct.unpack("!%dc" % num_chars, s))
        return return_struct

    def get_AbstractType_numpy(self):
        num_ints = self.get_int()
        num_doubles = self.get_int()
        num_chars = self.get_int()
        return_struct = AbstractType()

        if num_ints > 0:
            s = self.recv_buffer.read(num_ints * kIntSize)
            assert kIntSize == 4
            return_struct.intArray = numpy.frombuffer(s,
                                                      dtype=numpy_int_type,
                                                      count=num_ints)
        if num_doubles > 0:
            s = self.recv_buffer.read(num_doubles * kDoubleSize)
            return_struct.doubleArray = numpy.frombuffer(s,
                                                         count=num_doubles,
                                                         dtype=numpy_float_type)
        if num_chars > 0:
            s = self.recv_buffer.read(num_chars * kCharSize)
            return_struct.charArray = numpy.frombuffer(s,
                                                       count=num_chars,
                                                       dtype=numpy_char_type)
        return return_struct

    def get_Observation(self):
        return Observation.from_AbstractType(self.get_AbstractType())

    def get_Action(self):
        return Action.from_AbstractType(self.get_AbstractType())

    def put_int(self, value):
        self.send_buffer.write(struct.pack("!i", value))

    def put_double(self, value):
        self.send_buffer.write(struct.pack("!d", value))

    def put_string(self, value):
        if value is None:
            value = ''
        self.put_int(len(value))
        self.send_buffer.write(value)

    def put_Observation(self, obs):
        self.put_AbstractType(obs)

    def put_Action(self, action):
        self.put_AbstractType(action)

    def put_AbstractType(self, item):
        self.put_int(len(item.intArray))
        self.put_int(len(item.doubleArray))
        self.put_int(len(item.charArray))
        if len(item.intArray) > 0:
            self.send_buffer.write(struct.pack("!%di" % (len(item.intArray)), *item.intArray))
        if len(item.doubleArray) > 0:
            self.send_buffer.write(struct.pack("!%dd" % (len(item.doubleArray)), *item.doubleArray))
        if len(item.charArray) > 0:
            self.send_buffer.write(struct.pack("!%dc" % (len(item.charArray)), *item.charArray))

    def put_RewardObservation(self, reward_observation):
        self.put_int(reward_observation.terminal)
        self.put_double(reward_observation.r)
        self.put_Observation(reward_observation.o)

    def sizeof_AbstractType(self, item):
        size = kIntSize * 3
        int_size = 0
        double_size = 0
        char_size = 0
        if item is not None:
            if item.intArray is not None:
                int_size = kIntSize * len(item.intArray)
            if item.doubleArray is not None:
                double_size = kDoubleSize * len(item.doubleArray)
            if item.charArray is not None:
                char_size = kCharSize * len(item.charArray)
        return size + int_size + double_size + char_size

    def sizeof_Action(self, action):
        return self.sizeof_AbstractType(action)

    def sizeof_Observation(self, observation):
        return self.sizeof_AbstractType(observation)

    def sizeof_RewardObservation(self, reward_observation):
        return kIntSize + kDoubleSize + self.sizeof_Observation(reward_observation.o)
