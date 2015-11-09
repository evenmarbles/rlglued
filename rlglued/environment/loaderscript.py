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
#  $HeadURL: http://rl-glue-ext.googlecode.com/svn/trunk/projects/codecs/Python/src/rlglue/environment/EnvironmentLoaderScript.py $

import sys
import rlglued.network.network as network
import loader as env_loader


def main():
    usage = "PYTHONPATH=<Path to RLGlued> python -c 'import rlglued.environment.loader_script' <Environment>"

    env_vars = "The following environment variables are used by the environment to control its function:\n" + \
               "RLGLUED_HOST  : If set the agent will use this ip or hostname to connect to rather than " + \
               network.kLocalHost + "\n" + \
               "RLGLUED_PORT  : If set the agent will use this port to connect on rather than " + \
               str(network.kDefaultPort) + "\n"

    if len(sys.argv) < 2:
        print usage
        print env_vars
        sys.exit(1)

    env_loader.load_environment_like_script()


if __name__ == '__main__':
    main()
