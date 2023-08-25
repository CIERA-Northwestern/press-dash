'''Module for handling data.
'''
import types

import numpy as np
import pandas as pd


class DataHandler:
    '''Class for handling data.
    The data is loaded and pre-processed at initialization.

    Args:
        config (dict): The config dictionary.
        user_utils (module): User-customized module for data loading
    '''

    def __init__(self, config: dict, user_utils: types.ModuleType):
        self.config = config
        self.user_utils = user_utils

        # Container for dataframes
        self.data = {}

    def load_data(self, config: dict) -> (pd.DataFrame, dict):
        '''Load the data using the stored config and user_utils.

        This is one of the only functions where we allow the config
        to be modified. In general the on-the-fly settings are
        kept elsewhere.

        Returns:
            raw_df: The data.
            config: The config file. This will also be stored at self.config
        
        Side Effects:
            self.data['raw']: Data stored.
            self.config: Possible updates to the stored config file.
        '''
        raw_df, config = self.user_utils.load_data(config)

        self.data['raw'] = raw_df
        self.config = config

        return raw_df, config

    def clean_data(
            self,
            raw_df: pd.DataFrame,
            config: dict,
    ) -> (pd.DataFrame, dict):
        '''Clean the data using the stored config and user_utils.

        This is one of the only functions where we allow the config
        to be modified. In general the on-the-fly settings are
        kept elsewhere.

        Args:
            raw_df: The loaded data.

        Returns:
            cleaned_df: The preprocessed data.
            config: The config file. This will also be stored at self.config
        
        Side Effects:
            self.data['cleaned']: Data stored.
            self.config: Possible updates to the stored config file.
        '''
        cleaned_df, config = self.user_utils.clean_data(
            raw_df, config
        )

        self.data['cleaned'] = cleaned_df
        self.config = config

        return cleaned_df, config

    def preprocess_data(
            self,
            cleaned_df: pd.DataFrame,
            config: dict,
    ) -> (pd.DataFrame, dict):
        '''Preprocess the data using the stored config and user_utils.
        This is one of the only functions where we allow the config
        to be modified. In general the on-the-fly settings are
        kept elsewhere.

        Args:
            cleaned_df: The loaded data.

        Returns:
            preprocessed_df: The preprocessed data.
            config: The config file. This will also be stored at self.config
        
        Side Effects:
            self.data['preprocessed']: Data stored.
            self.config: Possible updates to the stored config file.
        '''
        preprocessed_df, config = self.user_utils.preprocess_data(
            cleaned_df, config
        )

        self.data['preprocessed'] = preprocessed_df
        self.config = config

        return preprocessed_df, config

    def recategorize_data_per_grouping(
        self,
        df: pd.DataFrame,
        groupby_column: dict,
        new_cat_per_g: dict,
        combine_single_categories: bool = False,
    ) -> pd.DataFrame:
        '''The actual function doing most of the recategorizing.

        Args:
            df: The dataframe containing the data to recategorize.
                Typically preprocessed.
            groupby_column: The category to group the data by,
                e.g. 'Research Topics'.
            new_categories_per_grouping: The new categories to use
                for this specific grouping.
            combine_single_categories: If True, instead of leaving
                undefined singly-tagged entries alone,
                group them all into an "Other" category.

        Returns:
            recategorized_df (pd.Series): The new categories.
        '''

        # Get the formatted data used for the categories
        dummies = pd.get_dummies(df[groupby_column])
        dummies['id'] = df['id']
        dummies_grouped = dummies.groupby('id')
        bools = dummies_grouped.sum() >= 1
        n_cats = bools.sum(axis='columns')
        if bools.values.max() > 1:
            raise ValueError(
                'Categorization cannot proceed---'
                'At least one category shows up multiple times'
                'for a single ID.'
            )

        # Setup return arr
        base_categories = bools.columns
        recat_dtype = np.array(new_cat_per_g.keys()).dtype
        recategorized_df = np.full(
            len(bools), fill_value='Other', dtype=recat_dtype,
        )
        recategorized_df = pd.Series(
            recategorized_df, index=bools.index, name=groupby_column
        )

        # Do all the single-category entries
        # These will be overridden if any are a subset of a new category
        if not combine_single_categories:
            bools_singles = bools.loc[n_cats == 1]
            for base_category in base_categories:
                is_base_cat = bools_singles[base_category].values
                base_cat_inds = bools_singles.index[is_base_cat]
                recategorized_df.loc[base_cat_inds] = base_category

        # Loop through and do the recategorization
        for category_key, category_definition in new_cat_per_g.items():
            # Replace the definition with something that can be evaluated
            not_included_cats = []
            for base_category in base_categories:
                if base_category not in category_definition:
                    not_included_cats.append(base_category)
                    continue
                category_definition = category_definition.replace(
                    "'{}'".format(base_category),
                    "row['{}']".format(base_category)
                )
            # Handle the not-included categories
            if 'only' in category_definition:
                category_definition = (
                    '(' + category_definition + ') &'
                    '( not ( ' + ' | '.join(
                        ["row['{}']".format(cat) for cat in not_included_cats]
                    ) + ' ) )'
                )
                category_definition = category_definition.replace('only', '')
            is_new_cat = bools.apply(
                lambda row: eval(category_definition), axis='columns'
            )
            recategorized_df[is_new_cat] = category_key
            
        return recategorized_df
