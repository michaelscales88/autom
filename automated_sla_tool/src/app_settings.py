from configobj import ConfigObj, ConfigObjError, flatten_errors
from json import dumps
from validate import Validator
from os.path import join, dirname
from functools import reduce
from time import sleep


# http://www.voidspace.org.uk/python/articles/configobj.shtml <- this has examples of configspec
# TODO add config writer interface E.g. adding clients, modify settings, etc
# TODO 2 make this class "static" so that it could produce settings dictionaries for multiple instances
class AppSettings(ConfigObj):

    def __init__(self, app=None, file_name=None):
        self._app = app if app else file_name
        if hasattr(self._app, '__module__') or isinstance(self._app, str):  # figure out how to use isclass here
            try:
                # TODO this param list should be mutable E.g. **kwargs
                super().__init__(infile=self.settings_file,
                                 configspec=self.config_spec_file,
                                 create_empty=True,
                                 file_error=True)
            except (ConfigObjError, IOError) as e:

                # TODO Give this menu options for fixing the issues. Opt 1: Show the configspec to fix.
                # TODO at least show the configspec file name that is missing
                print('Could not read {f_name}\n'
                      '{error}'.format(f_name=self.settings_file,
                                       error=e))
            else:
                self.init_and_validate()
        else:
            sleep(.5)
            raise SystemError('No application or settings for AppSettings')

    @property
    def f_name(self):
        return self._app if isinstance(self._app, str) else self._app.__class__.__name__

    @property
    def settings_file(self):
        return join(self.settings_directory, '{f_name}.ini'.format(f_name=self.f_name))

    @property
    def config_spec_file(self):
        return join(self.settings_directory, '{f_name}ConfigSpec.ini'.format(f_name=self.f_name))

    @property
    def settings_directory(self):
        return join(dirname(dirname(__file__)), 'settings')

    def setting(self, *keys, rtn_val=()):
        try:
            rtn_val = reduce(dict.__getitem__, keys, self)
        except (KeyError, TypeError):
            print('Could not find settings: {settings}'.format(settings=keys))
        return rtn_val

    def init_and_validate(self):
        for section_list, key, val in flatten_errors(self, self.validate(Validator())):
            # TODO add write capability to correct errors and update config file
            if key:
                print('The "{failed_key}" key in the section '
                      '"{failed_section}" failed validation'.format(failed_key=key,
                                                                    failed_section=': '.join(section_list))
                      )
                print(val)
            else:
                # TODO 2: Get the missing section key or use the configspec to add a default which requires user input
                print('The {section_w_o_key} section '
                      'is missing a required setting.'.format(section_w_o_key=': '.join(section_list))
                      )
                print(val)
        else:
            print('Settings validated for: {f_name}'.format(f_name=self.f_name))
            self.apply_keyword_format()
            self.apply_custom_format(lvl=self)

    # TODO this is not working as intended. should go to nth depth, but is going to n - 1
    def __iter__(self, v=None):
        print('inside __iter__')
        for kvl, vvl in (v if v else self).items():
            if hasattr(vvl, 'items'):
                self.__iter__(v=vvl)
            else:
                yield kvl, vvl

    def apply_custom_format(self, lvl=None):
        for k, v in lvl.items():
            if hasattr(v, 'items'):
                self.apply_custom_format(lvl=v)
            else:
                try:
                    lvl[k] = v.format(**self.setting('Keyword Formats', rtn_val={}))
                except (AttributeError, KeyError):
                    pass

    def apply_keyword_format(self):
        try:
            if self._app.interval:
                for k, v in self.setting('Keyword Formats', rtn_val={}).items():
                    self['Keyword Formats'][k] = self._app.interval.strftime(v)
        except AttributeError:
            pass  # For tests without a parent ( no interval )

    def __str__(self):
        print('Settings for {f_name}'.format(f_name=self.f_name))
        return dumps(self, indent=4)
