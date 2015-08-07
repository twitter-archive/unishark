# Copyright 2015 Twitter, Inc and other contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import inspect
from os import sep
from traceback import format_exception


class ContextManager(object):
    _shared_state = dict()

    def __init__(self):
        self.__dict__ = self._shared_state
        self._context_dict = dict()

    def get(self, name):
        return self._context_dict[name]

    def set(self, name, context):
        self._context_dict[name] = context


contexts = ContextManager()


def get_module_name(obj):
    return inspect.getsourcefile(type(obj)).split(sep)[-1].rstrip('.py')


def get_long_class_name(obj):
    return '.'.join((get_module_name(obj), get_class_name(obj)))


def get_long_method_name(obj):
    return '.'.join((get_long_class_name(obj), get_method_name(obj)))


def get_method_name(obj):
    return obj.id().split('.')[-1]


def get_class_name(obj):
    return type(obj).__name__


def _is_relevant_tb_level(tb):
    return '__unittest' in tb.tb_frame.f_globals


def _count_relevant_tb_levels(tb):
    length = 0
    while tb and not _is_relevant_tb_level(tb):
        length += 1
        tb = tb.tb_next
    return length


def exc_info_to_string(exc_info):
    """Also see runner.BufferedTestResult"""
    exctype, value, tb = exc_info
    # Skip test runner traceback levels
    while tb and _is_relevant_tb_level(tb):
        tb = tb.tb_next
    if exctype is AssertionError:
        # Skip assert*() traceback levels
        length = _count_relevant_tb_levels(tb)
        msg_lines = format_exception(exctype, value, tb, length)
    else:
        msg_lines = format_exception(exctype, value, tb)
    return ''.join(msg_lines).rstrip()