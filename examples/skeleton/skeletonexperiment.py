# 
# Copyright (C) 2008, Brian Tanner
# 
# http://rl-glue-ext.googlecode.com/
#
# Licensed under the Apache License, Version 2.0 (the "License"
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

import rlglued.rlglue as rlglue

which_episode = 0


def run_episode(obj, step_limit):
    global which_episode
    terminal = obj.run_episode(step_limit)
    total_steps = obj.num_steps()
    total_reward = obj.reward_return()

    print "Episode " + str(which_episode) + "\t " + str(total_steps) + " steps \t" + str(
        total_reward) + " total reward\t " + str(terminal) + " natural end"

    which_episode += 1


# Main Program starts here
rl_glue = rlglue.RLGlue()

print "\n\nExperiment starting up!"
task_spec = rl_glue.init()
print "RL_init called, the environment sent task spec: " + task_spec

print "\n\n----------Sending some sample messages----------"

# Talk to the agent and environment a bit...*/
responseMessage = rl_glue.agent_message("what is your name?")
print "Agent responded to \"what is your name?\" with: " + responseMessage

responseMessage = rl_glue.agent_message("If at first you don't succeed; call it version 1.0")
print "Agent responded to \"If at first you don't succeed; call it version 1.0  \" with: " + responseMessage + "\n"

responseMessage = rl_glue.env_message("what is your name?")
print "Environment responded to \"what is your name?\" with: " + responseMessage
responseMessage = rl_glue.env_message("If at first you don't succeed; call it version 1.0")
print "Environment responded to \"If at first you don't succeed; call it version 1.0  \" with: " + responseMessage

print "\n\n----------Running a few episodes----------"
run_episode(rl_glue, 100)
run_episode(rl_glue, 100)
run_episode(rl_glue, 100)
run_episode(rl_glue, 100)
run_episode(rl_glue, 100)
run_episode(rl_glue, 1)
# Remember that stepLimit of 0 means there is no limit at all!*/
run_episode(rl_glue, 0)
rl_glue.cleanup()

print "\n\n----------Stepping through an episode----------"
# We could also start over and do another experiment */
task_spec = rl_glue.init()

# We could run one step at a time instead of one episode at a time */
# Start the episode */
start_response = rl_glue.start()

first_obs = start_response.o.intArray[0]
first_act = start_response.a.intArray[0]
print "First observation and action were: " + str(first_obs) + " and: " + str(first_act)

# Run one step */
stepResponse = rl_glue.step()

# Run until the episode ends*/
while stepResponse.terminal != 1:
    stepResponse = rl_glue.step()
# if (stepResponse.terminal != 1)
# Could optionally print state,action pairs */
# printf("(%d,%d) ",stepResponse.o.intArray[0],stepResponse.a.intArray[0])*/

print "\n\n----------Summary----------"

totalSteps = rl_glue.num_steps()
totalReward = rl_glue.reward_return()
print "It ran for " + str(totalSteps) + " steps, total reward was: " + str(totalReward)
rl_glue.cleanup()
