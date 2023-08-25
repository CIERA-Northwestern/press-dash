'''Object for settings that get modified during use.
'''

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