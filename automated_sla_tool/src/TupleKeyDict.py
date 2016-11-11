class TupleKeyDict(object):
    def __init__(self):
        self.__dict = {}

    def __setitem__(self, key, value):
        if type(key) is not tuple:
            return
        p_key = key[0]
        s_key = key[1]
        try:
            self.__dict[p_key][s_key] = value
        except KeyError:
            self.__dict[p_key] = {s_key: value}
            # self.__dict[p_key][s_key] = value
        # try:
        #     self.__dict[p_key][s_key] += value
        # except KeyError:
        #     try:
        #         self.__dict[p_key][s_key] = value
        #     except KeyError:
        #         self.__dict[p_key] = {s_key: None}
        #         self.__dict[p_key][s_key] = value

    def __getitem__(self, key):
        try:
            return_val = self.__dict[key]
        except KeyError:
            p_key = key[0]
            s_key = key[1]
            return_val = self.__dict[p_key][s_key]
        return return_val

    def __str__(self):
        return "\n".join(['K:{0} v:{1}'.format(k, v) for (k, v) in self.__dict.items()])

    def items(self):
        return self.__dict.items()

    def values(self):
        return self.__dict.values()

    def get_dict(self):
        return self.__dict