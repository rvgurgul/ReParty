import json
import os


class Config:
    __configs = {}
    __saved = {}

    def __init__(self, path, default_config=None, load_logging=False, delete_old_params=False):
        self.__path = path
        self.__verbose = load_logging
        self.__default = {} if default_config is None else default_config()
        self.__saved[path] = True  # the config was just initialized, so there are no changes to be saved
        if path not in self.__configs:
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        self.__configs[path] = json.load(f)
                        if self.__verbose:
                            print(f"reading config: {self.__configs[self.__path]}")
                except Exception as e:
                    print(e)
                    # with open(path, "a") as f:
                    #     self.__configs[path] = default_config
                    #     json.dump(self.__configs[path], f)
                    #     if self.__verbose:
                    #         print("error reading config, using default:", default_config)
                for key in self.__default:  # Allows newer versions of configs to add properties
                    if key not in self.__configs[path]:
                        if self.__verbose:
                            print(f"+ added new property: '{key}': {self.__default[key]}")
                        self.__configs[path][key] = self.__default[key]
                        self.__saved[path] = False
                if delete_old_params:
                    for key in self.__configs[path]:
                        if key not in self.__default:
                            if self.__verbose:
                                print(f"- removed property: '{key}': {self.__configs[path][key]}")
                            del self.__configs[path][key]
            else:
                if self.__verbose:
                    print("config not found, using default:", default_config)
                self.__configs[path] = self.__default
                self.__saved[path] = False
                self.save()

    def save(self):
        if not self.__saved[self.__path]:
            # built-in functions (such as open), do not work in __del__ for whatever reason, so
            # this must be called manually
            try:
                with open(self.__path, "w") as f:
                    json.dump(self.__configs[self.__path], f, indent=4)
                    if self.__verbose:
                        print("writing config:", self.__configs[self.__path])
            except Exception as e:
                print("ERROR WHILE WRITING CONFIG:", e)

    def is_saved(self):
        return self.__saved[self.__path]

    def __getitem__(self, item):
        return self.__configs[self.__path][item]

    def __setitem__(self, key, value):
        if key in self.__default:
            self.__configs[self.__path][key] = value
            self.__saved[self.__path] = False

    def __delitem__(self, key):
        del self.__configs[self.__path][key]
        self.__saved[self.__path] = False

    def __str__(self):
        return str(self.__configs[self.__path])

    def toggle(self, key):
        if key in self.__configs[self.__path]:
            if type(val := self.__configs[self.__path][key]) == bool:
                val = not val
                self.__configs[self.__path][key] = val
                self.__saved[self.__path] = False
                return val

    def reset_property(self, key):
        self.__configs[self.__path][key] = self.__default[key]

    def reset_to_defaults(self):
        self.__configs[self.__path] = self.__default
        self.__saved[self.__path] = False

