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


from functools import wraps


def data_driven(*list_of_dicts, **dict_of_lists):
    def decorator(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            if list_of_dicts:
                for params in list_of_dicts:
                    if type(params) is not dict:
                        raise TypeError('%r is not a dict.' % params)
                    kwargs.update(params)
                    method(*args, **kwargs)
                return
            if dict_of_lists:
                values_list = dict_of_lists.values()
                for values in values_list:
                    if type(values) is not list:
                        raise TypeError('%r is not a list.' % values)
                min_len = min(map(len, values_list))
                for i in range(min_len):
                    params = dict()
                    for key in dict_of_lists:
                        values = dict_of_lists[key]
                        params[key] = values[i]
                    kwargs.update(params)
                    method(*args, **kwargs)
                return
        return wrapper
    return decorator