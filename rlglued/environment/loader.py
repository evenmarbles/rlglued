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
#  $HeadURL: http://rl-glue-ext.googlecode.com/svn/trunk/projects/codecs/Python/src/rlglue/environment/EnvironmentLoader.py $

import sys
import os
import rlglued.network.network as network
from client import ClientEnvironment

from rlglued.versions import get_svn_codec_version
from rlglued.versions import get_codec_version


def load_environment(env):
    svn_version = get_svn_codec_version()
    codec_version = get_codec_version()
    client = ClientEnvironment(env)

    host_string = os.getenv("RLGLUED_HOST")
    port_string = os.getenv("RLGLUED_PORT")

    host = network.kLocalHost
    if host_string is not None:
        host = host_string

    try:
        port = int(port_string)
    except TypeError:
        port = network.kDefaultPort

    print "RL-Glue Python Environment Codec Version: " + codec_version + " (Build " + svn_version + ")"
    print "\tConnecting to " + host + " on port " + str(port) + "..."
    sys.stdout.flush()

    client.connect(host, port, network.kRetryTimeout)
    print "\t Environment Codec Connected"

    client.run_event_loop()
    client.close()


def load_environment_like_script():
    # Assumes you've already done the checking that the number of args and such is good
    env_module = __import__(sys.argv[1])
    env_class = getattr(env_module, sys.argv[1])
    env = env_class()

    load_environment(env)
