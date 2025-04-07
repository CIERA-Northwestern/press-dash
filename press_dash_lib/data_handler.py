'''Module for handling data: Loading, transforming, extracting, etc.
'''
import copy
import re
import types
from typing import Tuple

import numpy as np
import pandas as pd


class DataHandler:
    '''Class for handling data.

    Args:
        config: The config dictionary.
        user_utils: User-customized module for data loading
    '''

    def __init__(self, config: dict, user_utils: types.ModuleType):
        self.config = config
        self.user_utils = user_utils

    def load_data(self, config: dict) -> Tuple[pd.DataFrame, dict]:
        '''Load the data using the stored config and user_utils.

        This is one of the only functions where we allow the config
        to be modified. In general the on-the-fly settings are
        kept elsewhere.

        Returns:
            raw_df: The data.
            config: The config file. This will also be stored at self.config
        '''
        raw_df, config = self.user_utils.load_data(config)

        return raw_df, config

    def clean_data(
            self,
            raw_df: pd.DataFrame,
            config: dict,
    ) -> Tuple[pd.DataFrame, dict]:
        '''Clean the data using the stored config and user_utils.

        This is one of the only functions where we allow the config
        to be modified. In general the on-the-fly settings are
        kept elsewhere.

        Args:
            raw_df: The loaded data.

        Returns:
            cleaned_df: The preprocessed data.
            config: The config file. This will also be stored at self.config
        '''
        return self.user_utils.clean_data(
            raw_df, config
        )

    def preprocess_data(
            self,
            cleaned_df: pd.DataFrame,
            config: dict,
    ) -> Tuple[pd.DataFrame, dict]:
        '''Preprocess the data using the stored config and user_utils.
        This is one of the only functions where we allow the config
        to be modified. In general the on-the-fly settings are
        kept elsewhere.

        Args:
            cleaned_df: The loaded data.

        Returns:
            preprocessed_df: The preprocessed data.
            config: The config file. This will also be stored at self.config
        '''
        return self.user_utils.preprocess_data(
            cleaned_df, config
        )
    

    # Recategorization stuff
    # v
    '''
    def recategorize_data_per_grouping(
        self,
        preprocessed_df: pd.DataFrame,
        groupby_column: dict,
        new_cat_per_g: dict,
        combine_single_categories: bool = False,
    ) -> pd.Series:
        The actual function doing most of the recategorizing.

        Args:
            preprocessed_df: The dataframe containing the data to recategorize.
            groupby_column: The category to group the data by,
                e.g. 'Research Topics'.
            new_categories_per_grouping: The new categories to use
                for this specific grouping.
            combine_single_categories: If True, instead of leaving
                undefined singly-tagged entries alone,
                group them all into an "Other" category.

        Returns:
            recategorized_series: The new categories.
        

        # Get the formatted data used for the categories
        dummies = pd.get_dummies(preprocessed_df[groupby_column])
        dummies['Title'] = preprocessed_df['Title']
        dummies_grouped = dummies.groupby('Title')
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
        recategorized_series = np.full(
            len(bools), fill_value='Other', dtype=recat_dtype,
        )
        recategorized_series = pd.Series(
            recategorized_series, index=bools.index, name=groupby_column
        )

        # Do all the single-category entries
        # These will be overridden if any are a subset of a new category
        if not combine_single_categories:
            bools_singles = bools.loc[n_cats == 1]
            for base_category in base_categories:
                is_base_cat = bools_singles[base_category].values
                base_cat_inds = bools_singles.index[is_base_cat]
                recategorized_series.loc[base_cat_inds] = base_category

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
                    '(not (' + ' | '.join(
                        ["row['{}']".format(cat) for cat in not_included_cats]
                    ) + '))'
                )
                category_definition = category_definition.replace('only', '')

            is_new_cat = bools.apply(
                lambda row: eval(category_definition), axis='columns'
            )
            recategorized_series[is_new_cat] = category_key
            
        return recategorized_series

    def recategorize_data(
            self,
            preprocessed_df: pd.DataFrame,
            new_categories: dict = None,
            recategorize: bool = True,
            combine_single_categories: bool = False,
        ) -> pd.DataFrame:
        'Recategorize the data, i.e. combine existing categories into new ones.
        The end result is one category per article, so no articles are double-counted.
        However, if the new categories are ill-defined they can contradict one another
        and lead to inconsistencies.

        Args:
            preprocessed_df: The dataframe containing the original data.
            new_categories: The new categories to use.
            recategorize: Whether to recategorize the data. Included for caching.
            combine_single_categories: If True, instead of leaving
                undefined singly-tagged entries alone,
                group them all into an "Other" category.

        Returns:
            recategorized: The dataframe containing the recategorized data.
                One entry per article.
        

        # We include the automatic return to help with data caching.
        if not recategorize:
            return preprocessed_df

        if new_categories is None:
            new_categories = self.config.get('new_categories', 0)
        
        # Get the condensed data frame
        # This is probably dropping stuff that shouldn't be dropped!!!!!!!
        recategorized = preprocessed_df.drop_duplicates(subset='Title', keep='first')
        recategorized = recategorized.set_index('Title')

        for groupby_column, new_categories_per_grouping in new_categories.items():

            # Look for columns that are re-definitions of existing columns
            # This regex looks for anything in front of anything else in brackets
            search = re.findall(r'(.*?)\s\[(.+)\]', groupby_column)
            if len(search) == 0:
                new_column = groupby_column
            elif len(search) == 1:
                new_column, groupby_column = search[0]
            else:
                raise KeyError('New categories cannot have multiple sets of brackets.')


            recategorized_groupby = self.recategorize_data_per_grouping(
                preprocessed_df,
                groupby_column,
                copy.deepcopy(new_categories_per_grouping),
                combine_single_categories
            )

            recategorized[new_column] = recategorized_groupby

        recategorized.reset_index(inplace=True)

        return recategorized
'''
    def filter_data(
        self,
        preprocessed_df: pd.DataFrame,
        filters: dict,
    ) -> pd.DataFrame:
        '''Filter what data shows up in the dashboard.

        Args:
            recategorized_df: The dataframe containing the data.
            categorical_filters (dict): How categories are filtered.

        Returns:
            selected_df: The dataframe containing the selected data.
        '''
        # Initialized
        is_included = np.ones(len(preprocessed_df), dtype=bool)
        categorical_filters = filters['categorical']

        # Categories filter
        for cat_filter_col, selected_cats in categorical_filters.items():
            is_included = is_included & preprocessed_df[cat_filter_col].isin(selected_cats)

        selected_df = preprocessed_df.loc[is_included]

        return selected_df