'''Object for settings that get modified during use.
'''
import copy
import inspect
import json
import types
from typing import Tuple

import streamlit as st

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

    def download_button(
        self,
        st_loc = st,
        label: str = 'Download settings in JSON format.',
        file_name: str = 'dash_settings.json',
    ):
        '''Download the settings as a json.

        Args:
            st_loc: Where to place. Defaults to st, as opposed to st.sidebar.
            label: Label seen by the user for the button.
            file_name: What to save the downloaded file as.
        '''

        # Get dict to save
        combined_settings = {
            'common': self.common,
            'local': self.local,
            'config': self.config,
        }
        json_string = json.dumps(combined_settings)

        # Download
        st_loc.download_button(
            label=label,
            file_name=file_name,
            mime="application/json",
            data=json_string,
        )

    def upload_button(
        self,
        st_loc = st,
        label: str = (
            'Upload settings in JSON format.\n'
            'A settings download button is at the bottom.'
        ),
    ) -> dict:
        '''Upload the settings and overwrite the class's values.

        Args:
            st_loc: Where to place. Defaults to st, as opposed to st.sidebar.
            label: Label seen by the user for the button.

        Returns
            combined_settings: All settings combined into a dict.
        '''

        # Upload
        file_content = st_loc.file_uploader(label=label, type='json')
        if file_content is None:
            return None
        combined_settings = json.load(file_content)
        
        # Store appropriately
        self.common = combined_settings['common']
        self.local = combined_settings['local']
        self.config = combined_settings['config']

        # Return
        return combined_settings

    def get_settings(
        self, 
        local_key: str = None, 
        common_to_include: list[str] = ['data', 'filters', 'view']
    ) -> dict:
        '''Get the full local settings, including global defaults.

        Args:
            local_key: Local key to use, if given.
            common_to_include: What global settings to incorporate.

        Returns:
            settings_dict: The combination of settings used.
        '''

        settings_dict = {}
        for common_key in common_to_include:
            settings_dict.update(self.common[common_key])
        if local_key is not None:
            settings_dict.update(self.local[local_key])

        return settings_dict

    def get_local_global_and_unset(
        self,
        function: types.FunctionType,
        local_key: str = None,
        common_to_include: list[str] = ['data', 'filters', 'view'],
        accounted_for: list[str] = ['self', 'kwarg', 'df', 'total', 'categories'],
    ) -> Tuple[list[str], list[str], list[str]]:

        local_opt_keys = list(self.local.get(local_key, {}).keys())

        common_opt_keys = set()
        for common_key in common_to_include:
            common_opt_keys = common_opt_keys.union(set(self.common[common_key].keys()))
        common_opt_keys -= set(local_opt_keys)
        common_opt_keys = list(common_opt_keys)

        unset_opt_keys = [
            arg for arg in inspect.signature(function).parameters
            if not ((arg in local_opt_keys) | (arg in common_opt_keys) | (arg in accounted_for))
       ]

        return local_opt_keys, common_opt_keys, unset_opt_keys

        
