__author__ = 'Ying Ni <yni@twitter.com>'


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