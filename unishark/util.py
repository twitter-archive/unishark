__author__ = 'Ying Ni <yni@twitter.com>'


import inspect


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
    return inspect.getsourcefile(type(obj)).split('/')[-1][:-3]


def get_long_class_name(obj):
    return '.'.join((get_module_name(obj), get_class_name(obj)))


def get_long_method_name(obj):
    return '.'.join((get_long_class_name(obj), get_method_name(obj)))


def get_method_name(obj):
    return obj.id().split('.')[-1]


def get_class_name(obj):
    return type(obj).__name__