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
# 
# $Revision: 999 $
# $Date: 2009-02-09 11:39:12 -0500 (Mon, 09 Feb 2009) $
# $Author: brian@tannerpages.com $
# $HeadURL: http://rl-library.googlecode.com/svn/trunk/projects/packages/examples/mines-sarsa-python/sample_experiment.py $
#



import math
import rlglued.rlglue as rlgue


# TO USE THIS Experiment [order doesn't matter]
# NOTE: I'm assuming the Python codec is installed an is in your Python path
#   -  Start the rl_glue executable socket server on your computer
#   -  Run the SampleSarsaAgent and SampleMinesEnvironment from this or a
#   different codec (Matlab, Python, Java, C, Lisp should all be fine)
#   -  Start this environment like:
#   $> python sample_experiment.py

# Experiment program that does some of the things that might be important when
# running an experiment.  It runs an agent on the environment and periodically
# asks the agent to "freeze learning": to stop updating its policy for a number
# of episodes in order to get an estimate of the quality of what has been learned
# so far.
#
# The experiment estimates statistics such as the mean and standard deviation of
# the return gathered by the policy and writes those to a comma-separated value file
# called results.csv.
#
# This experiment also shows off some other features that can be achieved easily
# through the RL-Glue env/agent messaging system by freezing learning (described
# above), having the environment start in specific starting states, and saving
# and loading the agent's value function to/from a binary data file.


# This function will freeze the agent's policy and test it after every 25 episodes.
def offline_demo(obj):
    statistics = []
    this_score = evaluate_agent(obj)
    print_score(0, this_score)
    statistics.append(this_score)

    for i in range(0, 20):
        for j in range(0, 25):
            obj.run_episode(0)
        this_score = evaluate_agent(obj)
        print_score((i + 1) * 25, this_score)
        statistics.append(this_score)

    save_result_to_cvs(statistics, "results.csv")


def print_score(after_episodes, score_tuple):
    print "%d\t\t%.2f\t\t%.2f" % (after_episodes, score_tuple[0], score_tuple[1])


#
# Tell the agent to stop learning, then execute n episodes with his current
# policy.  Estimate the mean and variance of the return over these episodes.
#
def evaluate_agent(obj):
    reward_sum = 0
    sum_of_squares = 0
    n = 10

    obj.agent_message("freeze learning")
    for i in range(0, n):
        # We use a cutoff here in case the
        # policy is bad and will never end an episode
        obj.run_episode(5000)
        this_return = obj.reward_return()
        reward_sum += this_return
        sum_of_squares += this_return ** 2

    mean = reward_sum / n
    variance = (sum_of_squares - n * mean * mean) / (n - 1.0)
    standard_dev = math.sqrt(variance)

    obj.agent_message("unfreeze learning")
    return mean, standard_dev


def save_result_to_cvs(statistics, filename):
    f = open(filename, "_w")
    f.write("#Results from sample_experiment.py.  First line is means, second line is standard deviations.\n");

    for thisEntry in statistics:
        f.write("%.2f, " % thisEntry[0])
    f.write("\n")

    for thisEntry in statistics:
        f.write("%.2f, " % thisEntry[1])
    f.write("\n")

    f.close()


#
# Just do a single evaluateAgent and print it
#
def single_evaluation(obj):
    this_score = evaluate_agent(obj)
    print_score(0, this_score)


rl_glue = rlgue.RLGlue()

print "Starting offline demo\n----------------------------\nWill alternate learning for 25 episodes, then freeze policy and evaluate for 10 episodes.\n"
print "After Episode\tMean Return\tStandard Deviation\n-------------------------------------------------------------------------"
rl_glue.init()
offline_demo(rl_glue)

print "\nNow we will save the agent's learned value function to a file...."

rl_glue.agent_message("save_policy results.dat")

print "\nCalling RL_cleanup and RL_init to clear the agent's memory..."

rl_glue.cleanup()
rl_glue.init()

print "Evaluating the agent's default policy:\n\t\tMean Return\tStandardDeviation\n------------------------------------------------------"
single_evaluation(rl_glue)

print "\nLoading up the value function we saved earlier."
rl_glue.agent_message("load_policy results.dat")

print "Evaluating the agent after loading the value function:\n\t\tMean Return\tStandardDeviation\n------------------------------------------------------"
single_evaluation(rl_glue)

print "Telling the environment to use fixed start state of 2,3."
rl_glue.env_message("set-start-state 2 3")
rl_glue.start()
print "Telling the environment to print the current state to the screen."
rl_glue.env_message("print-state")
print "Evaluating the agent a few times from a fixed start state of 2,3:\n\t\tMean Return\tStandardDeviation\n-------------------------------------------"
single_evaluation(rl_glue)

print "Evaluating the agent again with the random start state:\n\t\tMean Return\tStandardDeviation\n-----------------------------------------------------"
rl_glue.env_message("set-random-start-state")
single_evaluation(rl_glue)

rl_glue.cleanup()
print "\nProgram Complete."
