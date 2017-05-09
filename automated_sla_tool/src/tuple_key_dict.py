from automated_sla_tool.src.type_decorator import TypeDecorator


class TupleKeyDict(object):
    def __init__(self):
        self.__dict = {}

    @TypeDecorator(tuple, a_idx=1)
    def __setitem__(self, key, value):
        p_key = key[0]
        s_key = key[1]
        try:
            self.__dict[p_key][s_key] = value
        except KeyError:
            self.__dict[p_key] = {s_key: value}

    def __getitem__(self, key):
        return self.__dict[key[0]][key[1]]

    def __str__(self):
        return "\n".join(['K:{0} v:{1}'.format(k, v) for (k, v) in self.__dict.items()])

    def items(self):
        return self.__dict.items()

    def values(self):
        return self.__dict.values()

    def get_dict(self):
        return self.__dict
