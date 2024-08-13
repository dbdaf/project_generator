# Copyright 2015 0xc0170
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import copy
import logging
import subprocess

from os.path import basename,join, normpath, dirname, exists
from .tool import Tool, Exporter
from .cmake import CMake
from .gccarm import MakefileGccArm
from ..util import SOURCE_KEYS

logger = logging.getLogger('progen.tools.csolution')

class csolution(CMake):

    file_types = {'cpp': 1, 'c': 1, 's': 1, 'obj': 1, 'lib': 1, 'h': 1}
    def __init__(self, workspace, env_settings):
        super(csolution, self).__init__(workspace, env_settings)
        self.logging = logging
        self.workspace['preprocess_linker_file'] = True

    @staticmethod
    def get_toolnames():
        return ['csolution']

    @staticmethod
    def get_toolchain():
        return 'armclang'

    def _expand_one_file(self, source, new_data, extension):
        return {'path': source, 'name': basename(source), 'type': str(self.file_types[extension.lower()])}

    def export_project(self):
        """ Processes groups and misc options specific for eclipse, and run generator """
        output = copy.deepcopy(self.generated_project)
        data_for_make = self.workspace.copy()

        expanded_dic = self.workspace.copy()
        expanded_dic['rel_path'] = data_for_make['output_dir']['rel_path']
        groups = self._get_groups(expanded_dic)
        expanded_dic['groups'] = {}
        for group in groups:
            expanded_dic['groups'][group] = []
        self._iterate(self.workspace, expanded_dic)

        # delete default group
        if 'default' in expanded_dic['groups']:
            del expanded_dic['groups']['default']

        # Project file
        project_path, output['files']['cproj'] = self.gen_file_jinja(
            'csolution.cproject.yml.tmpl', expanded_dic, expanded_dic['name']+'.cproject.yml', data_for_make['output_dir']['path'])
        project_path, output['files']['proj_file'] = self.gen_file_jinja(
            'csolution.csolution.yml.tmpl', expanded_dic, expanded_dic['name']+'.csolution.yml', data_for_make['output_dir']['path'])
        return output

    def get_workspace_template(self):
        return 'cmakelist_armclang_workspace.tmpl'
