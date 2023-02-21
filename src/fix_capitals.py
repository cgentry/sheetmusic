import os
import re

class FindOccurances( ):

    def __init__(self ):
        self.definitions = {}
        self.re_definition = re.compile( '\s*def\s*(([a-z]+)([A-Z][a-z]+)([A-Z]*[a-z]*))[(]' )

    def search_dir(self, directory:str)->list:
        for root, dirs, files in os.walk( directory ):
            for file in files:
                if file.endswith( '.py'):
                    self.search_file( os.path.join( dir , file ))

    def search_file( self, path ):
        with open( path ) as f:
            for line in f.readlines():
                if self.re_definition.findall( )

