'''VetCond App
===============

The main module that starts the experiment.
'''

from functools import partial
from os.path import join, dirname, isdir

from cplcom.moa.app import ExperimentApp, run_app as run_cpl_app

from kivy.properties import ObjectProperty
from kivy.resources import resource_add_path
from kivy.uix.behaviors.knspace import knspace
from kivy.garden.filebrowser import FileBrowser
from kivy.lang import Builder

import vet_cond.stages

__all__ = ('ConditioningApp', 'run_app')


class ConditioningApp(ExperimentApp):
    '''The app which runs the experiment.
    '''

    def __init__(self, **kwargs):
        super(ConditioningApp, self).__init__(**kwargs)
        resource_add_path(join(dirname(__file__), 'data'))
        resource_add_path(join(dirname(dirname(__file__)), 'media'))
        Builder.load_file(join(dirname(__file__), 'Experiment.kv'))
        Builder.load_file(join(dirname(__file__), 'display.kv'))
        self.data_directory = join(dirname(__file__), 'data')

    def set_json_file(self, path, selection, filename):
        '''Sets the json config file when selected from the file browser.
        '''
        if not isdir(path) or not filename:
            return
        self.json_config_path = join(path, filename)

    def clean_up_root_stage(self):
        super(ConditioningApp, self).clean_up_root_stage()
        knspace.gui_start_stop.state = 'normal'

run_app = partial(run_cpl_app, ConditioningApp)
'''The function that starts the experiment GUI and the entry point for
the main script.
'''

if __name__ == '__main__':
    run_app()
