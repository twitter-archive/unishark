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
import concurrent.futures
import sys
import threading
from unishark.util import exc_info_to_string
from unishark.runner import out
from unishark.exception import MultipleErrors


def data_driven(*list_of_dicts, **dict_of_lists):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if list_of_dicts:
                for params in list_of_dicts:
                    if type(params) is not dict:
                        raise TypeError('%r is not a dict.' % params)
                    kwargs.update(params)
                    func(*args, **kwargs)
                return
            if dict_of_lists:
                values_list = dict_of_lists.values()
                for values in values_list:
                    if type(values) is not list:
                        raise TypeError('%r is not a list.' % values)
                keys = dict_of_lists.keys()
                for values in zip(*values_list):
                    params = dict(zip(keys, values))
                    kwargs.update(params)
                    func(*args, **kwargs)
                return
        return wrapper
    return decorator


def multi_threading_data_driven(max_workers, *list_of_dicts, **dict_of_lists):
    if type(max_workers) is not int:
        raise TypeError('max_workers is not an integer.')
    if max_workers <= 0:
        raise ValueError('max_workers <= 0.')

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if list_of_dicts:
                for params in list_of_dicts:
                    if type(params) is not dict:
                        raise TypeError('%r is not a dict.' % params)
                with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
                    futures = []
                    for params in list_of_dicts:
                        kwargs.update(params)
                        futures.append(executor.submit(_fn_with_traceback, func, *args, **kwargs))
                    _handle_futures(futures)
                return
            if dict_of_lists:
                values_list = dict_of_lists.values()
                for values in values_list:
                    if type(values) is not list:
                        raise TypeError('%r is not a list.' % values)
                values_groups = list(zip(*values_list))
                with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
                    futures = []
                    keys = dict_of_lists.keys()
                    for values in values_groups:
                        params = dict(zip(keys, values))
                        kwargs.update(params)
                        futures.append(executor.submit(_fn_with_traceback, func, *args, **kwargs))
                    _handle_futures(futures)
                return
        return wrapper
    return decorator


def _fn_with_traceback(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
        return threading.current_thread().ident, None
    except Exception:
        return threading.current_thread().ident, exc_info_to_string(sys.exc_info())


def _handle_futures(futures):
    results = list(map(lambda x: x.result(), concurrent.futures.as_completed(futures)))
    idents = list(map(lambda r: r[0], results))
    for ident in idents:
        if ident in out.buff_dict:
            buff = out.buff_dict.pop(ident)
            out.write(buff.getvalue())
            buff.seek(0)
            buff.truncate()
            out.buff_queue.append(buff)
    exc_info_strs = list(filter(lambda e: e is not None, list(map(lambda r: r[1], results))))
    if exc_info_strs:
        raise MultipleErrors(exc_info_strs)