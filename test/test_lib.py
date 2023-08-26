'''Tests for root_dash_lib
'''
import copy
import os
import unittest

import numpy as np
import pandas as pd

from root_dash_lib.dash_builder import DashBuilder
from .lib_for_tests import press_user_utils, grants_user_utils


def copy_config(root_config_fp, config_fp):
    '''Copy the config file from the root directory to the test data directory.
    Commonly used in setting up tests, so defined here.

    Args:
        root_config_fp (str): Filepath for the config file
            in the root directory.
        config_fp (str): Filepath for the config file
            in the test data directory.
    '''

    # Copy and edit config
    with open(root_config_fp, 'r', encoding='UTF-8') as file:
        config_text = file.read()
    config_text = config_text.replace('../data', '.')
    config_text = config_text.replace('./', '')
    with open(config_fp, 'w', encoding='UTF-8') as file:
        file.write(config_text)


def standard_setup(self, user_utils=None):
    '''Common function for setting up the data
    '''

    # Get filepath info
    test_dir = os.path.abspath(os.path.dirname(__file__))
    self.root_dir = os.path.dirname(test_dir)
    self.data_dir = os.path.join(
        self.root_dir, 'test_data', 'test_data_complete',
    )
    root_config_fp = os.path.join(self.root_dir, 'test', 'config.yml')
    self.config_fp = os.path.join(self.data_dir, 'config.yml')

    copy_config(root_config_fp, self.config_fp)

    self.group_by = 'Research Topics'

    self.builder = DashBuilder(self.config_fp, user_utils)
    self.data, self.config = \
        self.builder.prep_data(self.builder.config)


class TestPrepData(unittest.TestCase):
    '''This tests the setup for press data.
    '''

    def setUp(self):

        # Get filepath info
        test_dir = os.path.abspath(os.path.dirname(__file__))
        self.root_dir = os.path.dirname(test_dir)
        self.data_dir = os.path.join(
            self.root_dir, 'test_data', 'test_data_complete'
        )
        root_config_fp = os.path.join(self.root_dir, 'test', 'config.yml')
        self.config_fp = os.path.join(self.data_dir, 'config.yml')
        copy_config(root_config_fp, self.config_fp)

    def tearDown(self):
        if os.path.isfile(self.config_fp):
            os.remove(self.config_fp)

    def test_constructor(self):
        '''Does the constructor work?
        '''

        builder = DashBuilder(self.config_fp)

        assert builder.config['primary_id_column'] == 'index'

    def test_load_data(self):
        '''Does load_data at least run?'''

        builder = DashBuilder(self.config_fp)
        raw_df, config = builder.data_handler.load_data(builder.config)

    def test_preprocess_data(self):
        '''Does preprocess data at least run?'''

        builder = DashBuilder(self.config_fp)
        preprocessed_df, config = builder.prep_data(builder.config)

    def test_changes_propagate(self):
        '''We have a config object that's passed around.
        Let's double check that if it's edited in DataHandler
        that Aggregator's version is also changed.
        '''
        builder = DashBuilder(self.config_fp, press_user_utils)
        builder_val_before = copy.copy(builder.config['page_title'])
        agg_val_before = copy.copy(builder.agg.config['page_title'])
        builder.prep_data(builder.config)
        builder_val_after = copy.copy(builder.config['page_title'])
        agg_val_after = copy.copy(builder.agg.config['page_title'])

        assert builder_val_before == agg_val_before
        assert builder_val_before != builder_val_after
        assert builder_val_after == agg_val_after

    def test_consistent_original_and_preprocessed(self):
        '''Are the raw and preprocessed dataframes consistent?
        This checks the user utils more than anything,
        and also whether or not we can recover the raw data
        from the pre-processed data.
        '''

        builder = DashBuilder(self.config_fp)
        data, config = builder.prep_data(builder.config)

        groupby_column = 'Research Topics'

        test_df = data['preprocessed'].copy()
        test_df['dup_col'] = \
            test_df['id'].astype(str) + test_df[groupby_column]
        test_df = test_df.drop_duplicates(subset='dup_col', keep='first')
        grouped = test_df.groupby('id')
        actual = grouped[groupby_column].apply('|'.join)

        missing = data['cleaned'].loc[np.invert(data['cleaned'].index.isin(actual.index))]
        assert len(missing) == 0

        not_equal = actual != data['cleaned'][groupby_column]
        assert not_equal.sum() == 0
        np.testing.assert_array_equal(
            actual,
            data['cleaned'][groupby_column]
        )


class TestRecategorize(unittest.TestCase):

    def setUp(self):
        standard_setup(self)

    def tearDown(self):
        if os.path.isfile(self.config_fp):
            os.remove(self.config_fp)

    def test_recategorize_data_per_grouping(self):

        # Test Dataset
        data = {
            'id': [1, 1, 2, 2, 3],
            'Press Types': [
                'Northwestern Press', 'CIERA Press', 'External Press',
                'CIERA Press', 'CIERA Press',
            ],
            'Year': [2015, 2015, 2014, 2014, 2015, ],
        }
        df = pd.DataFrame(data)

        new_categories = {
            'Northwestern Press (Inclusive)': (
                "'Northwestern Press' | ( 'Northwestern Press' & 'CIERA Press')"
            )
        }

        df = self.builder.data_handler.recategorize_data_per_grouping(
            df,
            'Press Types',
            new_categories
        )

        # Build up expected data
        expected = pd.DataFrame(
            data={
                'id': [1, 2, 3, ],
                'Press Types': [
                    'Northwestern Press (Inclusive)', 'Other', 'CIERA Press',
                ],
                'Year': [2015, 2014, 2015],
            },
        )
        expected.set_index('id', inplace=True)

        pd.testing.assert_series_equal(expected['Press Types'], df)

    def test_recategorize_data_per_grouping_realistic(self):

        group_by = 'Research Topics'
        cleaned_df = self.data['cleaned']
        recategorized_df = self.builder.data_handler.recategorize_data_per_grouping(
            self.data['preprocessed'],
            group_by,
            self.builder.config['new_categories'][group_by],
            False,
        )

        # Check that compact objects is right
        not_included_groups = [
            'Stellar Dynamics & Stellar Populations',
            'Exoplanets & The Solar System',
            'Galaxies & Cosmology',
            'N/A',
        ]
        for group in not_included_groups:
            is_group = cleaned_df[group_by].str.contains(group)
            is_compact = recategorized_df == 'Compact Objects'
            assert (is_group.values & is_compact.values).sum() == 0

        # Check that none of the singles categories shows up in other
        for group in pd.unique(self.data['preprocessed'][group_by]):
            is_group = cleaned_df[group_by] == group
            is_other = recategorized_df == 'Other'
            is_bad = (is_group.values & is_other.values)
            n_matched = is_bad.sum()
            # compare bad ids, good for debugging
            if n_matched > 0:
                bad_ids_original = cleaned_df.index[is_bad]
                bad_ids_recategorized = recategorized_df.index[is_bad]
                np.testing.assert_allclose(
                    bad_ids_original, bad_ids_recategorized
                )
            assert n_matched == 0

    def test_recategorize_data(self):

        recategorized = self.builder.data_handler.recategorize_data(
            self.data['preprocessed'],
            self.builder.config['new_categories'],
            True,
        )
        cleaned_df = self.data['cleaned']

        # Check that NU Press inclusive is right
        group_by = 'Press Types'
        expected = (
            (cleaned_df[group_by] == 'CIERA Stories|Northwestern Press') |
            (cleaned_df[group_by] == 'Northwestern Press|CIERA Stories') |
            (cleaned_df[group_by] == 'Northwestern Press')
        )
        actual = recategorized[group_by] == 'Northwestern Press (Inclusive)'
        np.testing.assert_allclose(
            actual.values,
            expected.values,
        )

        # Check that compact objects is right
        group_by = 'Research Topics'
        not_included_groups = [
            'Stellar Dynamics & Stellar Populations',
            'Exoplanets & The Solar System',
            'Galaxies & Cosmology',
            'N/A',
        ]
        for group in not_included_groups:
            is_group = cleaned_df[group_by].str.contains(group)
            is_compact = recategorized[group_by] == 'Compact Objects'
            assert (is_group.values & is_compact.values).sum() == 0

        # Check that none of the singles categories shows up in other
        for group in pd.unique( self.data['preprocessed'][group_by] ):
            is_group = cleaned_df[group_by] == group
            is_other = recategorized[group_by] == 'Other'
            is_bad = (is_group.values & is_other.values)
            n_matched = is_bad.sum()
            # compare bad ids, good for debugging
            if n_matched > 0:
                bad_ids_original = cleaned_df.index[is_bad]
                bad_ids_recategorized = recategorized.loc[is_bad, 'id']
                np.testing.assert_allclose(
                    bad_ids_original, bad_ids_recategorized
                )
            assert n_matched == 0

    def test_recategorize_data_rename(self):

        new_categories = self.builder.config['new_categories']
        new_categories['Also Research Topics [Research Topics]'] = {
            'Compact Objects': (
                "only ('Life & Death of Stars' | 'Gravitational Waves & Multi-Messenger Astronomy' | 'Black Holes & Dead Stars' )"
            ),
            'Cosmological Populations': (
                "only ('Galaxies & Cosmology' | 'Stellar Dynamics & Stellar Populations' )"
            ),
        }
        recategorized_df = self.builder.data_handler.recategorize_data(
            self.data['preprocessed'],
            new_categories,
            True,
        )
        is_bad = recategorized_df['Also Research Topics'] != \
            recategorized_df['Research Topics']
        n_bad = is_bad.sum()
        assert n_bad == 0

        # Check that this still works for columns with similar names 
        new_categories['Also Research Topics (with parenthesis) [Research Topics]'] = {
            'Compact Objects': (
                "only ('Life & Death of Stars' | 'Gravitational Waves & Multi-Messenger Astronomy' | 'Black Holes & Dead Stars' )"
            ),
            'Cosmological Populations': (
                "only ('Galaxies & Cosmology' | 'Stellar Dynamics & Stellar Populations' )"
            ),
        }
        recategorized_df = self.builder.data_handler.recategorize_data(
            self.data['preprocessed'],
            new_categories,
            True,
        )
        is_bad = recategorized_df['Also Research Topics (with parenthesis)'] != \
            recategorized_df['Research Topics']
        n_bad = is_bad.sum()
        assert n_bad == 0


class TestFilterData(unittest.TestCase):

    def setUp(self):
        standard_setup(self)

    def tearDown(self):
        if os.path.isfile(self.config_fp):
            os.remove(self.config_fp)

    def test_filter_data( self ):

        search_str = ''
        categorical_filters = {
            'Research Topics': [ 'Galaxies & Cosmology', ],
            'Press Types': [ 'External Press', ],
            'Categories': [ 'Science', 'Event', ],
        }
        range_filters = {
            'Year': [ 2016, 2023 ], 
            'Press Mentions': [ 0, 10 ], 
        }

        selected = self.builder.data_handler.filter_data(
            self.data['preprocessed'],
            { 'Title': search_str, },
            categorical_filters,
            range_filters
        )

        assert np.invert( selected['Research Topics'] == 'Galaxies & Cosmology' ).sum() == 0
        assert np.invert( selected['Press Types'] == 'External Press' ).sum() == 0
        assert np.invert( ( selected['Categories'] == 'Science' ) | ( selected['Categories'] == 'Event' ) ).sum() == 0
        assert np.invert( ( 2016 <= selected['Year'] ) & ( selected['Year'] <= 2023 ) ).sum() == 0
        assert np.invert( ( 0 <= selected['Press Mentions'] ) & ( selected['Press Mentions'] <= 10 ) ).sum() == 0

    
class TestAggregate( unittest.TestCase ):

    def setUp( self ):
        standard_setup( self )

    def tearDown( self ):
        if os.path.isfile( self.config_fp ):
            os.remove( self.config_fp )

    def test_count( self ):

        selected_df = self.data['preprocessed']

        counts = self.builder.agg.count(
            selected_df,
            'Year',
            'id',
            self.group_by
        )
        total = self.builder.agg.count(
            selected_df,
            'Year',
            'id',
        )

        test_year = 2015
        test_group = 'Galaxies & Cosmology'
        expected = len( pd.unique(
            selected_df.loc[(
                ( selected_df['Year'] == test_year ) &
                ( selected_df[self.group_by] == test_group )
            ),'id']
        ) )
        assert counts.loc[test_year,test_group] == expected

        # Total count
        test_year = 2015
        expected = len( pd.unique(
            selected_df.loc[(
                ( selected_df['Year'] == test_year )
            ),'id']
        ) )
        assert total.loc[test_year][0] == expected

    ###############################################################################

    def test_sum_press_mentions( self ):

        selected_df = self.data['preprocessed']
        weighting = 'Press Mentions'

        sums = self.builder.agg.sum(
            selected_df,
            'Year',
            weighting,
            self.group_by,
        )
        total = self.builder.agg.sum(
            selected_df,
            'Year',
            weighting,
        )

        test_year = 2015
        test_group = 'Galaxies & Cosmology'
        subselected = selected_df.loc[(
            ( selected_df['Year'] == test_year ) &
            ( selected_df[self.group_by] == test_group )
        )]
        subselected = subselected.drop_duplicates( subset='id' )
        subselected = subselected.replace( 'N/A', 0, )
        expected = subselected['Press Mentions'].sum()
        assert sums.loc[test_year,test_group] == expected

        # Total count
        test_year = 2015
        subselected = selected_df.loc[(
            ( selected_df['Year'] == test_year )
        )]
        subselected = subselected.drop_duplicates( subset='id' )
        subselected = subselected.replace( 'N/A', 0, )
        expected = subselected['Press Mentions'].sum()
        assert total.loc[test_year][0] == expected

    ###############################################################################

    def test_sum_press_mentions_nonzero( self ):

        selected_df = self.data['preprocessed']
        weighting = 'Press Mentions'

        sums = self.builder.agg.sum(
            selected_df,
            'Year',
            weighting,
            self.group_by,
        )
        totals = self.builder.agg.sum(
            selected_df,
            'Year',
            weighting,
        )

        # Non-zero test
        test_year = 2021
        test_group = 'Gravitational Waves & Multi-Messenger Astronomy'
        subselected = selected_df.loc[(
            ( selected_df['Year'] == test_year ) &
            ( selected_df[self.group_by] == test_group )
        )]
        subselected = subselected.drop_duplicates( subset='id' )
        subselected = subselected.replace( 'N/A', 0 )
        expected = subselected['Press Mentions'].sum()
        assert expected > 0
        assert sums.loc[test_year,test_group] == expected

        # Total count
        test_year = 2021
        subselected = selected_df.loc[(
            ( selected_df['Year'] == test_year )
        )]
        subselected = subselected.drop_duplicates( subset='id' )
        subselected = subselected.replace( 'N/A', 0 )
        expected = subselected['Press Mentions'].sum()
        assert totals.loc[test_year][0] == expected

###############################################################################

class TestStreamlit( unittest.TestCase ):

    def setUp( self ):
        standard_setup(self, press_user_utils)

    def tearDown( self ):
        if os.path.isfile( self.config_fp ):
            os.remove( self.config_fp )

    ###############################################################################

    def test_base_page( self ):

        import root_dash_lib.pages.base_page as base_page

        base_page.main( self.config_fp )

        # Set the environment variable to signal the app to stop
        os.environ["STOP_STREAMLIT"] = "1"

        del os.environ["STOP_STREAMLIT"]

###############################################################################

class TestStreamlitGrants( unittest.TestCase ):

    def setUp( self ):

        # Get filepath info
        test_dir = os.path.abspath( os.path.dirname( __file__ ) )
        self.root_dir = os.path.dirname( test_dir )
        self.data_dir = os.path.join( self.root_dir, 'test_data', 'test_data_mock_grants_and_proposals', )
        root_config_fp = os.path.join( self.root_dir, 'test', 'config_grants.yml' )
        self.config_fp = os.path.join( self.data_dir, 'config.yml' )

        copy_config( root_config_fp, self.config_fp )

        self.builder = DashBuilder( self.config_fp, grants_user_utils ) 

    def tearDown( self ):
        if os.path.isfile( self.config_fp ):
            os.remove( self.config_fp )

    ###############################################################################

    def test_base_page( self ):

        self.builder.add_page( 'base_page' )

        self.builder.run()

        # Set the environment variable to signal the app to stop
        os.environ["STOP_STREAMLIT"] = "1"

        del os.environ["STOP_STREAMLIT"]


