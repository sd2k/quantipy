import unittest
import os.path
import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal
import test_helper
import copy

from operator import lt, le, eq, ne, ge, gt

from pandas.core.index import Index
__index_symbol__ = {
    Index.union: ',',
    Index.intersection: '&',
    Index.difference: '~',
    Index.sym_diff: '^'
}

from collections import defaultdict, OrderedDict
from quantipy.core.stack import Stack
from quantipy.core.chain import Chain
from quantipy.core.link import Link
from quantipy.core.cluster import Cluster
from quantipy.core.builds.excel.excel_painter import ExcelPainter
from quantipy.core.view_generators.view_mapper import ViewMapper
from quantipy.core.view_generators.view_maps import QuantipyViews
from quantipy.core.view import View
from quantipy.core.helpers import functions
from quantipy.core.helpers.functions import load_json
from quantipy.core.tools.dp.prep import (
    frange,
    frequency,
    crosstab
)
from quantipy.core.tools.dp.query import request_views
from quantipy.core.tools.view.query import get_dataframe

class TestBankedChains(unittest.TestCase):

    def setUp(self):
        self.path = './tests/'
#         self.path = ''
        project_name = 'Example Data (A)'

        # Load Example Data (A) data and meta into self
        name_data = '%s.csv' % (project_name)
        path_data = '%s%s' % (self.path, name_data)
        self.data = pd.DataFrame.from_csv(path_data)
        
        name_meta = '%s.json' % (project_name)
        path_meta = '%s%s' % (self.path, name_meta)
        self.meta = load_json(path_meta)

        # Variables by type for Example Data A
        self.dk = 'Example Data (A)'
        self.fk = 'no_filter'
        self.single = ['gender', 'locality', 'ethnicity', 'religion', 'q1']
        self.delimited_set = ['q2', 'q3', 'q8', 'q9']
        self.q5 = ['q5_1', 'q5_2', 'q5_3', 'q5_4', 'q5_5', 'q5_6']
        self.x_vars = self.q5
        self.y_vars = ['@', 'gender', 'locality', 'q2', 'q3']        
        self.views = ['cbase', 'counts']
        self.weights = [None, 'weight_a']
        self.text_key = 'en-GB'
        
        self.stack = get_stack(
            self, self.meta, self.data,
            self.x_vars, self.y_vars, 
            self.views, self.weights)
    
    def test_verify_banked_chain(self):
        
        views_ref = request_views(
            self.stack, 
            weight=None, 
            nets=False,
            descriptives=['median', 'mean', 'stddev'],
            coltests=True, 
            mimic="askia", 
            sig_levels=['low', 'mid', 'high']
        )
        
        chains = {
            xk: self.stack.get_chain(
                x=xk, y=self.y_vars, 
                views=views_ref['get_chain']['c'])
            for xk in self.x_vars
        }
         
        #### test correct specifiction definitions    
        specs = []   
        specs.append({
            'name': 'q5_means',
            'type': 'banked-chain',
            'text': {'en-GB': 'Mean summary q5'},
            'bases': True,
            'view': 'x|mean|x:y|||descriptives',
            'items': [
                {'chain': chains[cname], 'text': {'en-GB': '{}: mean'.format(cname)}}
                for cname in self.q5]})
        specs.append({
            'name': 'q5_means',
            'type': 'banked-chain',
            'text': {'en-GB': 'Mean summary q5'},
            'bases': True,
            'items': [
                {
                    'chain': chains[cname], 
                    'view': 'x|mean|x:y|||descriptives',
                    'text': {'en-GB': '{}: mean'.format(cname)}
                }
                for cname in self.q5]})
        for i, spec in enumerate(specs):
#             print i
            is_banked = Cluster()._verify_banked_chain_spec(spec)
            self.assertTrue(is_banked)
        
        #### test chain object
        is_banked = Cluster()._verify_banked_chain_spec(chains['q5_1'])
        self.assertFalse(is_banked)
        
        #### test missing required objects in the definition
        specs = []
        specs.append({
            'type': 'banked-chain',
            'text': {'en-GB': 'Mean summary q5'},
            'bases': True,
            'view': 'x|mean|x:y|||descriptives',
            'items': [
                {'chain': chains[cname], 'text': {'en-GB': '{}: mean'.format(cname)}}
                for cname in self.q5]})
        specs.append({
            'name': 'q5_means',
            'text': {'en-GB': 'Mean summary q5'},
            'bases': True,
            'view': 'x|mean|x:y|||descriptives',
            'items': [
                {'chain': chains[cname], 'text': {'en-GB': '{}: mean'.format(cname)}}
                for cname in self.q5]})
        specs.append({
            'name': 'q5_means',
            'type': 'banked-chain',
            'bases': True,
            'view': 'x|mean|x:y|||descriptives',
            'items': [
                {'chain': chains[cname], 'text': {'en-GB': '{}: mean'.format(cname)}}
                for cname in self.q5]})
        specs.append({
            'name': 'q5_means',
            'type': 'banked-chain',
            'text': {'en-GB': 'Mean summary q5'},
            'view': 'x|mean|x:y|||descriptives',
            'items': [
                {'chain': chains[cname], 'text': {'en-GB': '{}: mean'.format(cname)}}
                for cname in self.q5]})
        specs.append({
            'name': 'q5_means',
            'type': 'banked-chain',
            'text': {'en-GB': 'Mean summary q5'},
            'bases': True,
            'items': [
                {'chain': chains[cname], 'text': {'en-GB': '{}: mean'.format(cname)}}
                for cname in self.q5]})
        specs.append({
            'name': 'q5_means',
            'type': 'banked-chain',
            'text': {'en-GB': 'Mean summary q5'},
            'bases': True,
            'view': 'x|mean|x:y|||descriptives'})
        specs.append({
            'name': 'q5_means',
            'type': 'banked-chain',
            'text': {'en-GB': 'Mean summary q5'},
            'bases': True,
            'view': 'x|mean|x:y|||descriptives',
            'items': [
                {'chain': chains[cname], 'text': {}}
                for cname in self.q5]})
        specs.append({
            'name': 'q5_means',
            'type': 'banked-chain',
            'text': {'en-GB': 'Mean summary q5'},
            'bases': True,
            'view': 'x|mean|x:y|||descriptives',
            'items': [
                {'chain': chains[cname]}
                for cname in self.q5]})
        specs.append({
            'name': 'q5_means',
            'type': 'banked-chain',
            'text': {'en-GB': 'Mean summary q5'},
            'bases': True,
            'view': 'x|mean|x:y|||descriptives',
            'items': [
                {'text': {'en-GB': '{}: mean'.format(cname)}}
                for cname in self.q5]})
        for i, spec in enumerate(specs):
#             print i
            is_banked = Cluster()._verify_banked_chain_spec(spec)
            self.assertFalse(is_banked)
            
        #### test incorrect types for required objects in the definition
        specs = []
        specs.append({
            'name': 1,
            'type': 'banked-chain',
            'text': {'en-GB': 'Mean summary q5'},
            'bases': True,
            'view': 'x|mean|x:y|||descriptives',
            'items': [
                {'chain': chains[cname], 'text': {'en-GB': '{}: mean'.format(cname)}}
                for cname in self.q5]})
        specs.append({
            'name': 'q5_means',
            'type': 1,
            'text': {'en-GB': 'Mean summary q5'},
            'bases': True,
            'view': 'x|mean|x:y|||descriptives',
            'items': [
                {'chain': chains[cname], 'text': {'en-GB': '{}: mean'.format(cname)}}
                for cname in self.q5]})
        specs.append({
            'name': 'q5_means',
            'type': 'banked-chain',
            'text': 1,
            'bases': True,
            'view': 'x|mean|x:y|||descriptives',
            'items': [
                {'chain': chains[cname], 'text': {'en-GB': '{}: mean'.format(cname)}}
                for cname in self.q5]})
        specs.append({
            'name': 'q5_means',
            'type': 'banked-chain',
            'text': {'en-GB': 1},
            'bases': True,
            'view': 'x|mean|x:y|||descriptives',
            'items': [
                {'chain': chains[cname], 'text': {'en-GB': '{}: mean'.format(cname)}}
                for cname in self.q5]})
        specs.append({
            'name': 'q5_means',
            'type': 'banked-chain',
            'text': {'en-GB': 'Mean summary q5'},
            'bases': 1,
            'view': 'x|mean|x:y|||descriptives',
            'items': [
                {'chain': chains[cname], 'text': {'en-GB': '{}: mean'.format(cname)}}
                for cname in self.q5]})
        specs.append({
            'name': 'q5_means',
            'type': 'banked-chain',
            'text': {'en-GB': 'Mean summary q5'},
            'bases': True,
            'view': 1,
            'items': [
                {'chain': chains[cname], 'text': {'en-GB': '{}: mean'.format(cname)}}
                for cname in self.q5]})
        specs.append({
            'name': 'q5_means',
            'type': 'banked-chain',
            'text': {'en-GB': 'Mean summary q5'},
            'bases': True,
            'view': 'x|mean|x:y|||descriptives',
            'items': 1})
        specs.append({
            'name': 'q5_means',
            'type': 'banked-chain',
            'text': {'en-GB': 'Mean summary q5'},
            'bases': True,
            'view': 'x|mean|x:y|||descriptives',
            'items': [
                {'chain': chains[cname], 'text': 1}
                for cname in self.q5]})
        specs.append({
            'name': 'q5_means',
            'type': 'banked-chain',
            'text': {'en-GB': 'Mean summary q5'},
            'bases': True,
            'view': 'x|mean|x:y|||descriptives',
            'items': [
                {'chain': chains[cname], 'text': {'en-GB': 1}}
                for cname in self.q5]})
        specs.append({
            'name': 'q5_means',
            'type': 'banked-chain',
            'text': {'en-GB': 'Mean summary q5'},
            'bases': True,
            'view': 'x|mean|x:y|||descriptives',
            'items': [
                {'chain': 1, 'text': {'en-GB': '{}: mean'.format(cname)}}
                for cname in self.q5]})
        for i, spec in enumerate(specs):
#             print i
            is_banked = Cluster()._verify_banked_chain_spec(spec)
            self.assertFalse(is_banked)
              
    def test_means_summary(self):
    
        ################## Unweighted
         
        views_ref = request_views(
            self.stack, 
            weight=None, 
            nets=False,
            descriptives=['median', 'mean', 'stddev'],
            coltests=True, 
            mimic="askia", 
            sig_levels=['low', 'mid', 'high'])
         
        chains = {
            xk: self.stack.get_chain(
                x=xk, y=self.y_vars, 
                views=views_ref['get_chain']['c'])
            for xk in self.x_vars}
         
        ## Unweighted, mean only        
        spec = {
            'name': 'q5_means',
            'type': 'banked-chain',
            'text': {'en-GB': 'Mean summary q5'},
            'bases': True,
            'view': 'x|mean|x:y|||descriptives',
            'items': [
                {'chain': chains[cname], 'text': {'en-GB': '{}: mean'.format(cname)}}
                for cname in self.q5]}
  
        banked_chain = Cluster().bank_chains(
            spec, text_key=self.text_key)
         
        ## Unweighted, median + mean + stddev
        median = 'x|median|x:y|||descriptives'
        mean = 'x|mean|x:y|||descriptives'
        mean_test_high = 'x|tests.means.askia.01|x:y|||askia tests'
        mean_test_medium = 'x|tests.means.askia.05|x:y|||askia tests'
        mean_test_low = 'x|tests.means.askia.10|x:y|||askia tests'
        stddev = 'x|stddev|x:y|||descriptives'
         
        labels = {
            median: '{}: median',
            mean: '{}: mean',
            mean_test_high: '{}: 99%',
            mean_test_medium: '{}: 95%',
            mean_test_low: '{}: 90%',
            stddev: '{}: stddev'}
        
        view_keys = [
            median, 
            mean, 
            mean_test_high, 
            mean_test_medium, 
            mean_test_low, 
            stddev]
         
        spec = {
            'name': 'q5_distribution',
            'type': 'banked-chain',
            'text': {'en-GB': 'Distribution summary q5'},
            'bases': True,
            'items': [
                {
                    'chain': chains[cname], 
                    'view': view_key, 
                    'text': {'en-GB': labels[view_key].format(cname)}}
                for cname in self.q5
                for view_key in view_keys
            ]
        }
 
        banked_chain = Cluster().bank_chains(
            spec, text_key=self.text_key)
         
        
# ##################### Helper functions #####################

def index_items(col, values, all=False):
    """
    Return a correctly formed list of tuples to matching an index.
    """
     
    items = [
        (col, str(i))
        for i in values
    ]
     
    if all: items = [(col, 'All')] + items
     
    return items

def str_index_values(index):
    """
    Make sure level 1 of the multiindex are all strings
    """
    values = index.values.tolist()
    values = zip(*[zip(*values)[0], [str(i) for i in zip(*values)[1]]])
    return values
        
def confirm_index_columns(self, df, expected_x, expected_y):
    """
    Confirms index and columns are as expected.
    """    
#     global COUNTER
    
    actual_x = str_index_values(df.index)
    actual_y = str_index_values(df.columns)
    
    self.assertEqual(actual_x, expected_x)
    self.assertEqual(actual_y, expected_y)
    
#     COUNTER = COUNTER + 2
#     print COUNTER
       
def get_stack(self, meta, data, xks, yks, views, weights):
  
    stack = Stack('test')
    stack.add_data('test', data, meta)
    stack.add_link(x=xks, y=yks, views=views, weights=weights)

    # Add two basic net
    net_views = ViewMapper(
        template={
            'method': QuantipyViews().frequency,
            'kwargs': {'iterators': {'rel_to': [None, 'y']}}})    
    net_views.add_method(
        name='Net 1-3',
        kwargs={'logic': [1, 2, 3], 'text': {'en-GB': '1-3'}})    
    net_views.add_method(
        name='Net 4-6',
        kwargs={'logic': [4, 5, 6], 'text': {'en-GB': '4-6'}})         
    stack.add_link(x=xks, y=yks, views=net_views, weights=weights)
    
    # Add block net  
    net_views.add_method(
        name='Block net',
        kwargs={
            'logic': [
                {'bn1': [1, 2]},
                {'bn2': [2, 3]},
                {'bn3': [1, 3]}]})
    stack.add_link(x=xks, y=yks, views=net_views.subset(['Block net']), weights=weights)
    
    # Add NPS
    ## TO DO
    
    # Add standard deviation
    desc_views = ViewMapper(
        template = {
            'method': QuantipyViews().descriptives,
            'kwargs': {'iterators': {'stats': ['mean', 'median', 'stddev']}}})
            
    desc_views.add_method(name='descriptives')        
    stack.add_link(x=xks, y=yks, views=desc_views, weights=weights)

    # Add tests
    test_views = ViewMapper(
        template={
            'method': QuantipyViews().coltests,
            'kwargs': {
                'mimic': 'askia',
                'iterators': {
                    'metric': ['props', 'means'],
                    'level': ['low', 'mid', 'high']
                }
            }
        }
    )        
    test_views.add_method('askia tests')
    stack.add_link(x=xks, y=yks, views=test_views)        

    return stack
       