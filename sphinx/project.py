# -*- coding: utf-8 -*-
"""
    sphinx.project
    ~~~~~~~~~~~~~~

    Utility function and classes for Sphinx projects.

    :copyright: Copyright 2007-2018 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import os
from typing import TYPE_CHECKING

from sphinx.locale import __
from sphinx.util import get_matching_files
from sphinx.util import logging
from sphinx.util.matching import compile_matchers
from sphinx.util.osutil import SEP, relpath

if TYPE_CHECKING:
    from typing import Dict, List, Set  # NOQA

logger = logging.getLogger(__name__)
EXCLUDE_PATHS = ['**/_sources', '.#*', '**/.#*', '*.lproj/**']  # type: List[unicode]


class Project(object):
    """A project is source code set of Sphinx document."""

    def __init__(self, srcdir, source_suffix):
        # type: (unicode, Dict[unicode, unicode]) -> None
        #: Source directory.
        self.srcdir = srcdir

        #: source_suffix. Same as :confval:`source_suffix`.
        self.source_suffix = source_suffix

        #: The name of documents belongs to this project.
        self.docnames = set()  # type: Set[unicode]

    def restore(self, other):
        # type: (Project) -> None
        """Take over a result of last build."""
        self.docnames = other.docnames

    def discover(self, exclude_paths=[]):
        # type: (List[unicode]) -> Set[unicode]
        """Find all document files in the source directory and put them in
        :attr:`docnames`.
        """
        self.docnames = set()
        excludes = compile_matchers(exclude_paths + EXCLUDE_PATHS)
        for filename in get_matching_files(self.srcdir, excludes):  # type: ignore
            docname = self.path2doc(filename)
            if docname:
                if os.access(os.path.join(self.srcdir, filename), os.R_OK):
                    self.docnames.add(docname)
                else:
                    logger.warning(__("document not readable. Ignored."), location=docname)

        return self.docnames

    def path2doc(self, filename):
        # type: (unicode) -> unicode
        """Return the docname for the filename if the file is document.

        *filename* should be absolute or relative to the source directory.
        """
        if filename.startswith(self.srcdir):
            filename = relpath(filename, self.srcdir)
        for suffix in self.source_suffix:
            if filename.endswith(suffix):
                return filename[:-len(suffix)]

        # the file does not have docname
        return None

    def doc2path(self, docname, basedir=True):
        # type: (unicode, bool) -> unicode
        """Return the filename for the document name.

        If *basedir* is True, return as an absolute path.
        Else, return as a relative path to the source directory.
        """
        docname = docname.replace(SEP, os.path.sep)
        basename = os.path.join(self.srcdir, docname)
        for suffix in self.source_suffix:
            if os.path.isfile(basename + suffix):
                break
        else:
            # document does not exist
            suffix = list(self.source_suffix)[0]

        if basedir:
            return basename + suffix
        else:
            return docname + suffix
