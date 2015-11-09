#
# Copyright (C) 2009, Jose Antonio Martin H.
#
# http://rl-glue-ext.googlecode.com/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
#  $Revision: 465 $
#  $Date: 2009-01-28 21:55:32 -0500 (Wed, 28 Jan 2009) $
#  $Author: xjamartinh $
#  $HeadURL: http://rl-glue-ext.googlecode.com/svn/trunk/projects/codecs/Python/src/rlglue/utils/TaskSpecVRLGLUE3.py $

"""
Brian Tanner: The license above is what matters most. I think you can all
take the comments below as non-binding suggestions ;)

This file was written by Jose Antonio Martin H. for the RL-Glue Extensions project.
you are allowed to use it (and see it) fully but subject to the next conditions

1. to not cause damage to any person
2. to not use it to earn money except when you give me the 50%
3. to use it to produce a state of the art RL agent, if not, think a lot and then come back to write a super agent.

This code is a 'parser' for the RL-Glue 3.0 TaskSpec.
It does not make any duplication of information, that is, what you get is always a view of the original string.
This is not the classic state-machine or automata approach to parsing languages so in particular you will se that
the parser is robust to a big set of taskpec string malformations still getting the right information. blablabla


Last modifed 22-1-2009 by Jose Antonio Martin H.
Added enforced parsing error catching.
"""


import sys
import numpy as np

try:
    import psyco

    psyco.full()
except ImportError:
    pass


class TaskSpec:
    def __init__(self, discount_factor=1.0, reward_range=(-1, 1)):
        self.version = "RL-Glue-3.0"
        self.prob_type = "episodic"
        self._discount_factor = discount_factor
        self._act = {}
        self._obs = {}
        self._act_charcount = 0
        self._obs_charcount = 0
        self._reward_range = reward_range
        self._extras = ""

    def to_taskspec(self):
        ts_list = ["VERSION " + self.version,
                   "PROBLEMTYPE " + self.prob_type,
                   "DISCOUNTFACTOR " + str(self._discount_factor)]

        # Observations
        if len(self._obs.keys()) > 0:
            ts_list += ["OBSERVATIONS"]
            if "INTS" in self._obs:
                ts_list += ["INTS"] + self._obs["INTS"]
            if "DOUBLES" in self._obs:
                ts_list += ["DOUBLES"] + self._obs["DOUBLES"]
            if "CHARCOUNT" in self._obs:
                ts_list += ["CHARCOUNT"] + self._obs["CHARCOUNT"]

        # Actions
        if len(self._act.keys()) > 0:
            ts_list += ["ACTIONS"]
            if "INTS" in self._act:
                ts_list += ["INTS"] + self._act["INTS"]
            if "DOUBLES" in self._act:
                ts_list += ["DOUBLES"] + self._act["DOUBLES"]
            if "CHARCOUNT" in self._act:
                ts_list += ["CHARCOUNT"] + self._act["CHARCOUNT"]

        ts_list += ["REWARDS", "(" + str(self._reward_range[0]) + " " + str(self._reward_range[1]) + ")"]
        if self._extras != "":
            ts_list += ["EXTRAS", self._extras]
        return ' '.join(ts_list)

    def set_discount_factor(self, factor):
        self._discount_factor = factor

    def set_continuing(self):
        self.prob_type = "continuing"

    def set_episodic(self):
        self.prob_type = "episodic"

    def set_problem_type_custom(self, prob_type):
        self.prob_type = prob_type

    def add_act(self, range_, repeat=1, type_="INTS"):
        rept = "" if repeat <= 1 else str(repeat) + " "
        self._act.setdefault(type_, []).append("(" + rept + str(range_[0]) + " " + str(range_[1]) + ")")

    def add_obs(self, range_, repeat=1, type_="INTS"):
        rept = "" if repeat <= 1 else str(repeat) + " "
        self._obs.setdefault(type_, []).append("(" + rept + str(range_[0]) + " " + str(range_[1]) + ")")

    def add_int_act(self, range_, repeat=1):
        self.add_act(map(int, range_), repeat, "INTS")

    def add_int_obs(self, range_, repeat=1):
        self.add_obs(map(int, range_), repeat, "INTS")

    def add_double_act(self, range_, repeat=1):
        self.add_act(range_, repeat, "DOUBLES")

    def add_double_obs(self, range_, repeat=1):
        self.add_obs(range_, repeat, "DOUBLES")

    def set_charcount_act(self, charcount):
        self._act["CHARCOUNT"] = [str(charcount)]

    def set_charcount_obs(self, charcount):
        self._obs["CHARCOUNT"] = [str(charcount)]

    def set_reward_range(self, low, high):
        self._reward_range = (low, high)

    def set_extra(self, extra):
        self._extras = extra


class TaskSpecParser:
    """RL-Glue TaskSpec Sparser V3."""
    _w = ["VERSION", "PROBLEMTYPE", "DISCOUNTFACTOR", "OBSERVATIONS", "ACTIONS", "REWARDS", "EXTRA"]
    _v = ["INTS", "DOUBLES", "CHARCOUNT"]
    expected_version = "RL-Glue-3.0"

    @property
    def valid(self):
        return self._valid

    @property
    def taskspec(self):
        return self._ts

    @property
    def version(self):
        """The task spec version.

        Returns
        -------
        str : The task spec version.

        """
        return self._version

    @property
    def problem_type(self):
        if not self._validate():
            return ""
        return self._problem_type

    @property
    def discount_factor(self):
        if not self._validate():
            return ""
        return self._discount_factor

    def __init__(self, ts):
        self._valid = True
        self._last_error = ""
        self._ts = ts

        self._version = self._get_version()

        if self.expected_version != self._version:
            print "Warning: TaskSpec Version is not " + self.expected_version + " but " + self._version
            self._valid = False

        while self._ts.find("  ") != -1:
            self._ts = self._ts.replace("  ", " ")

        self._problem_type = ""
        self._discount_factor = ""

        self._obs_str = ""
        self._int_obs = []
        self._double_obs = []
        self._charcount_obs = 0

        self._num_int_obs = 0
        self._num_double_obs = 0

        self._act_str = ""
        self._int_act = []
        self._double_act = []
        self._charcount_act = 0

        self._num_int_act = 0
        self._num_double_act = 0

        self._reward_range_str = ""
        self._reward_range = []
        self._extra = ""

        pos = []
        r = []
        w = self._w[1:len(self._w)]
        for i, id_ in enumerate(list(w)):
            try:
                pos.append(ts.index(id_))
            except:
                r.append(id_)
                del w[i]

        if len(r) > 0:
            self._last_error = "could not find the keywords: " + ", ".join(r)
            print "Warning: TaskSpec String is invalid: " + self._last_error
            self._valid = False
            return

        sorted_w = sorted(zip(pos, w))
        w = [s[1] for s in sorted_w]

        for i, id_ in enumerate(w):
            if id_ == 'PROBLEMTYPE':
                self._problem_type = self.get_value(i, ts, w)
            elif id_ == 'DISCOUNTFACTOR':
                val = self.get_value(i, ts, w)
                self._discount_factor = float(val) if self._valid else ""
            elif id_ == 'OBSERVATIONS':
                self._obs_str = self._get_vars_str(i, ts, w)
                self._int_obs = self._get_vars_dims(0, self._obs_str)
                self._double_obs = self._get_vars_dims(1, self._obs_str)
                self._charcount_obs = int(self.get_value(2, self._obs_str, self._v))

                self._num_int_obs = len(self._int_obs)
                self._num_double_obs = len(self._double_obs)
            elif id_ == 'ACTIONS':
                self._act_str = self._get_vars_str(i, ts, w)
                self._int_act = self._get_vars_dims(0, self._act_str)
                self._double_act = self._get_vars_dims(1, self._act_str)
                self._charcount_act = int(self.get_value(2, self._act_str, self._v))

                self._num_int_act = len(self._int_act)
                self._num_double_act = len(self._double_act)
            elif id_ == 'REWARDS':
                self._reward_range_str = self.get_value(i, ts, w)
                self._reward_range = self._get_range(self._reward_range_str)
            elif id_ == 'EXTRA':
                self._extra = self.get_value(i, ts, w)

    def _get_version(self):
        a = len(self._w[0]) + 1
        return self._ts[a:self._ts.find(" ", a)]

    def is_episodic(self):
        if not self._validate():
            return ""
        return self._problem_type == "episodic"

    # noinspection PyMethodMayBeStatic
    def is_special(self, max_or_min):
        if not isinstance(max_or_min, basestring):
            return False
        if max_or_min == "UNSPEC" or max_or_min == "NEGINF" or max_or_min == "POSINF":
            return True
        else:
            return False

    def get_act_str(self):
        return self._act_str

    def get_obs_str(self):
        return self._obs_str

    def get_num_int_act(self):
        return self._num_int_act

    def get_num_int_obs(self):
        return self._num_int_obs

    def get_num_double_act(self):
        return self._num_double_act

    def get_num_double_obs(self):
        return self._num_double_obs

    def get_int_act(self):
        return self._int_act

    def get_int_obs(self):
        return self._int_obs

    def get_double_act(self):
        return self._double_act

    def get_double_obs(self):
        return self._double_obs

    def get_charcount_act(self):
        return self._charcount_act

    def get_charcount_obs(self):
        return self._charcount_obs

    def get_reward_range_str(self):
        return self._reward_range_str

    def get_reward_range(self):
        return self._reward_range

    def get_extra(self):
        return self._extra

    def get_value(self, i, ts, w):
        try:
            a = ts.index(w[i]) + len(w[i]) + 1
        except:  # ValueError:
            # raise AttributeError("Malformed TaskSpec String: could not find the "+w[i]+" keyword")
            self._last_error = "could not find the " + w[i] + " keyword"
            print "Warning: Malformed TaskSpec String: " + self._last_error
            self._valid = False
            return ""
        b = None
        if (i + 1) < len(w):
            try:
                b = ts.index(w[i + 1]) - 1
            except:  # ValueError:
                # raise AttributeError("Malformed TaskSpec String: could not find the "+w[i+1]+" keyword")
                self._last_error = "could not find the " + w[i + 1] + " keyword"
                print "Warning: Malformed TaskSpec String: " + self._last_error
                self._valid = False
                return ""

        return ts[a:b].strip()

    def _validate(self):
        if not self._valid:
            print "Warning: TaskSpec String is invalid: " + self._last_error
            return False
        return True

    def _get_var_value(self, i, str_o):
        if not self._validate():
            return ""
        str_r = self.get_value(i, str_o, self._v)
        str_r = str_r.replace(") (", ")#(")
        # Ok I can parse it but this (there is no space or there is an extra space in ranges)
        # should be checked since this means that the taskspec is malformed
        str_r = str_r.replace("( ", "(")
        str_r = str_r.replace(" )", ")")
        str_r = str_r.replace(")(", ")#(")

        parts = str_r.split("#")
        obs = []
        for p in parts:
            obs.extend(self._get_range(p))
        return obs

    def _get_range(self, str_input):
        if not self._validate():
            return ""
        try:
            str_input = str_input.replace("UNSPEC", "'UNSPEC'")
            str_input = str_input.replace("NEGINF", "'NEGINF'")
            str_input = str_input.replace("POSINF", "'POSINF'")
            str_input = str_input.replace(" ", ",")
            r = eval(str_input)
            r = list(r)
            if len(r) == 2:
                if r[0] == 'NEGINF':
                    r[0] = -np.inf
                if r[1] == 'POSINF':
                    r[1] = np.inf
                return [r]

            if r[1] == 'POSINF' or r[2] == 'NEGINF':
                self._last_error = "error occurred while parsing a Range in " + str_input
                raise ValueError("Warning: Malformed TaskSpec String: " + self._last_error)
            if r[1] == 'NEGINF':
                r[1] = -np.inf
            if r[2] == 'POSINF':
                r[2] = np.inf
            out = r[0] * ([[r[1], r[2]]])
            return out

        except:
            self._last_error = "error occurred while parsing a Range in " + str_input
            print "Warning: Malformed TaskSpec String: " + self._last_error
            print sys.exc_info()
            self._valid = False
            return ""

    def _complete_vars(self, str_in):
        if not self._validate():
            return ""
        # forces the vars to have ints doubles and charcount
        if self._v[0] not in str_in:
            str_in = self._v[0] + " (0 0 0) " + str_in
        if self._v[2] not in str_in:
            str_in = str_in.rstrip() + " " + self._v[2] + " 0 "
        if self._v[1] not in str_in:
            i = str_in.find(self._v[2])
            str_in = str_in[0:i] + self._v[1] + " (0 0 0) " + str_in[i:]

        return str_in

    def _get_var_info_range(self, i, ts, w):
        self._validate()
        a = ts.index(w[i])
        b = ts.index(w[i + 1]) + 1
        return ts[a:b]

    def _get_discount_factor(self):
        value = self.get_value(2, self._ts, self._w)
        if not self._validate():
            return ""
        return float(value)

    def _get_vars_str(self, i, ts, w):
        if not self._validate():
            return ""
        str_o = self.get_value(i, ts, w)
        return self._complete_vars(str_o)

    def _get_vars_dims(self, i, str_in):
        if not self._validate():
            return ""
        return self._get_var_value(i, str_in)


def test():
    # you can cut the taskspec by the main words with new line
    ts = "VERSION RL-Glue-3.0 PROBLEMTYPE episodic DISCOUNTFACTOR .7 OBSERVATIONS INTS (NEGINF 1) ( 2 -5 POSINF )" \
         " DOUBLES (2 -1.2 0.5 )(-.07 .07) (UNSPEC 3.3) (0 100.5) CHARCOUNT 32 ACTIONS INTS (5 0 4)" \
         " DOUBLES (-.5 2) (2 7.8 9) (NEGINF UNSPEC) REWARDS (-5.0 5.0) EXTRA some other stuff goes here"

    print ts
    print
    print

    task_spec = TaskSpecParser(ts)
    if task_spec.valid:
        print "======================================================================================================="
        print "Version: [" + task_spec.version + "]"
        print "ProblemType: [" + task_spec.problem_type + "]"
        print "DiscountFactor: [" + str(task_spec.discount_factor) + "]"
        print "======================================================================================================="
        print "\t \t \t \t Observations"
        print "======================================================================================================="
        print "Observations: [" + task_spec.get_obs_str() + "]"
        print "Integers:", task_spec.get_int_obs()
        print "Doubles: ", task_spec.get_double_obs()
        print "Chars:   ", task_spec.get_charcount_obs()
        print "======================================================================================================="
        print "\t \t \t \t Actions"
        print "======================================================================================================"
        print "Actions: [" + task_spec.get_act_str() + "]"
        print "Integers:", task_spec.get_int_act()
        print "Doubles: ", task_spec.get_double_act()
        print "Chars:   ", task_spec.get_charcount_act()
        print "======================================================================================================="
        print "Reward :[" + task_spec.get_reward_range_str() + "]"
        print "Reward Range:", task_spec.get_reward_range()
        print "Extra: [" + task_spec.get_extra() + "]"
        print "remember that by using len() you get the cardinality of lists!"
        print "Thus:"
        print "len(", task_spec.get_double_obs(), ") ==> ", len(
            task_spec.get_double_obs()), " Double Observations"
        print task_spec.is_special("NEGINF")


if __name__ == "__main__":
    test()
