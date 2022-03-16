"""
This module exposes Zip class which creates an in-memory zip object
to avoid disk access

Example:
        zip = Zip()
"""

__copyright__ ="""
Copyright 2021 CyberGIS Center for Advanced Digital and Spatial Studies
"""

__license__ ="""
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import zipfile
from io import BytesIO


class Zip(object):
    """
    An interface that creates an in-memory zip object to 
    avoid disk access

    Attributes:
        in_memory_zip : A BytesIO in-memory file
    """
    def __init__(self):
        """Inits Zip with in_memory_zip"""
        # Create the in-memory file-like object
        self.in_memory_zip = BytesIO()

    def mkdir(self, filedir_in_zip):
        """
        Creates a directory with the name filedir_in_zip

        Args:
            fildir_in_zip(str): Name of the zip_directory

        Returns:
            None
        """
        # Get a handle to the in-memory zip in append mode
        zf = zipfile.ZipFile(self.in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)
        
        # Writes a directory to the in-memory zip
        zf.writestr(filedir_in_zip + '/.placeholder', "b", zipfile.ZIP_DEFLATED)

        # Mark the files as having been created on Windows so that
        # Unix permissions are not inferred as 0000
        for zfile in zf.filelist:
            zfile.create_system = 0

        return self

    def append(self, filename_in_zip, file_contents):
        """
        Appends a file with name filename_in_zip and contents of
        file_contents to the in-memory zip.

        Args:
            filename_in_zip(str): Name of the zip_file
            file_contents(str): Contents that need to be written to the zip_file

        Returns:
            None
        """
        # Get a handle to the in-memory zip in append mode
        zf = zipfile.ZipFile(self.in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)

        # Write the file to the in-memory zip
        zf.writestr(filename_in_zip, file_contents, zipfile.ZIP_DEFLATED)

        # Mark the files as having been created on Windows so that
        # Unix permissions are not inferred as 0000
        for zfile in zf.filelist:
            zfile.create_system = 0

        return self

    def read(self):
        """
        Reads the contents of the in-memory zip.

        Args:
            None
    
        Returns:
            A string with the contents of the in-memory zip
        """
        self.in_memory_zip.seek(0)
        return self.in_memory_zip.read()

    def write(self, filename):
        """
        Writes the in-memory zip to a file
        
        Args:
            filename(str) : Name of the file that needs to be written
        
        Returns:
            None
        """
        f = open(filename, "wb")
        f.write(self.read())
        f.close()
