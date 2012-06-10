# eldomain is a Emacs Lisp domain for the Sphinx documentation tool.
# Copyright (C) 2012 Takafumi Arakaki

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from os import path
import subprocess
import json

from sphinxcontrib.cldomain import CLDomain, doc_strings, args


def index_package(emacs, package, prefix, pre_load, extra_args=[]):
    """Call an external lisp program that will return a dictionary of
    doc strings for all public symbols."""
    lisp_script = path.join(path.dirname(path.realpath(__file__)),
                            "eldomain.el")
    command = [emacs, "-Q", "-batch", "-l", pre_load,
               "--eval", '(setq eldomain-prefix "{0}")'.format(prefix),
               "-l", lisp_script] + extra_args
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = proc.communicate()
    if proc.poll() != 0:
        raise RuntimeError(
            "Error while executing '{0}'.\n\n"
            "STDOUT:\n{1}\n\nSTDERR:\n{2}\n".format(
                ' '.join(command), stdout, stderr))
    lisp_data = json.loads(stdout)
    doc_strings[package] = {}

    # FIXME: support using same name for function/variable/face
    for key in ['face', 'variable', 'function']:
        for data in lisp_data[key]:
            doc_strings[package][data['name'].upper()] = data['doc']

    args[package] = {}

    for data in lisp_data['function']:
        args[package][data['name'].upper()] = data['arg']


def load_packages(app):
    emacs = app.config.emacs_executable
    # `app.confdir` will be ignored if `elisp_pre_load` is an absolute path
    pre_load = path.join(app.confdir, app.config.elisp_pre_load)
    for (name, prefix) in app.config.lisp_packages.iteritems():
        index_package(emacs, name.upper(), prefix, pre_load)


def setup(app):
    # monkey patch cldomain
    import sphinxcontrib.cldomain
    sphinxcontrib.cldomain.load_packages = load_packages

    app.add_domain(CLDomain)
    app.add_config_value('emacs_executable', 'emacs', 'env')
    app.add_config_value('elisp_pre_load', 'conf.el', 'env')
    app.add_config_value('lisp_packages', {}, 'env')
    app.connect('builder-inited', load_packages)
