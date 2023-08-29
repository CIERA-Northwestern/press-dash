'''Object for settings that get modified during use.
'''
import copy
import inspect
import types

class Settings:
    '''Main settings object.

    Args:
        config: The config dictionary.
    '''

    def __init__(self, config: dict):

        self.config = config
        self.common = {
            'data': {},
            'filters': {},
            'view': {},
        }
        self.local = {}

    def get_local_settings(
        self, 
        local_key: str, 
        common_to_include: list[str] = ['data', 'filters', 'view']
    ) -> dict:
        '''Get the full local settings, including global defaults.

        Args:
            local_key: Local key to use.
            common_to_include: What global settings to incorporate.
        '''

        local_dict = copy.deepcopy(self.local.get(local_key, {}))
        for common_key in common_to_include:
            local_dict.update(self.common[common_key])

        return local_dict

    def get_local_global_and_unset(
        self,
        function: types.FunctionType,
        local_key: str = None,
        common_to_include: list[str] = ['data', 'filters', 'view']
        accounted_for: list[str] = [ 'self', 'kwarg' ]
    ):

        local_keys = set(self.local.get(local_key, {}).keys())

        common_keys = set()
        for common_key in common_to_include:
            common_keys = common_keys.union(set(self.common[common_key].keys()))
        common_keys -= local_keys

        function_args = set(inspect.signature(function).parameters)
        unset_keys = function_args - local_keys.union(common_keys)

        return local_keys, common_keys, unset_keys

        
