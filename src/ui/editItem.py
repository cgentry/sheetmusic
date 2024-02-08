"""
User Interface : Generic combo box

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

import logging

from PySide6.QtWidgets import QComboBox

class UiGenericCombo( QComboBox ):
    """Display a combo box with dropdown fox and options

    Args:
        QComboBox (object): QT box
    """

    def __init__(self ,
                 isEditable:bool=True,
                 fill:any=None,
                 current_value:str=None,
                 name:str=None):
        """Setup the combo box

        Args:
            isEditable (bool, optional): Are fields editable.
                Defaults to True.
            fill (any, optional): Fill in with data: dict, list.
                Defaults to None.
            current_value (str, optional): What is the current selection.
                Defaults to None.
            name (str, optional): Wha. to name the option.
                Defaults to None.
        """
        super().__init__()
        self.setEditable( isEditable )
        if name is not None:
            self.setObjectName( name )
        if fill is not None:
            if isinstance( fill, dict ):
                self.fill_dict( fill , current_value )
            elif isinstance( fill, list ):
                self.fill_list( fill, current_value )
            else:
                self.fill_table( fill, current_value )


    def _finish_setup( self ):
        self.setMinimumWidth(200)
        self.setDuplicatesEnabled( False )

    def find_data( self, current:str )->int:
        """Search the combo box for item data

        Args:
            current (str): value to find

        Returns:
            int: Index to item, or -1 if not found
        """
        for i in range( 0, self.count() ) :
            if current == self.itemData( i ):
                return i
        return -1

    def set_current_item( self, current:str=None, add=False):
        """Set the current combo box element

        Args:
            current (str, optional): Value to set. Defaults to None.
            add (bool, optional): Call QComboBox to set or add the item.
                Defaults to False.
        """
        if current is not None and current:
            if add :
                super().setCurrentText( current )
            else:
                idx = self.findText( current )
                if idx < 0:
                    idx = self.find_data( current )
                if idx >= 0:
                    self.setCurrentIndex( idx )

    def fill_dict( self, values:dict, current_value:None ):
        """
            Fill the dropdown box with key/value from dictionary
        """
        try:
            for key, value in values.items() :
                self.addItem( str(key), userData=value )
            if current_value:
                self.set_current_item( str(current_value) )
            self._finish_setup()
        except Exception as err:
            value_list = ",".join( [ str(key) + ":"+ str(value)  for key,value in values.items  ])
            logging.exception( "fill_dict: values: %s currentvalue: %s",
                              value_list ,
                              current_value )
            raise err

    def fill_list( self, values:list , current_value:None ):
        """
            Fill the dropdown box with values from a list
        """
        try:
            self.addItems( values )
            if current_value:
                self.set_current_item( str(current_value) )
            self._finish_setup()
        except Exception as err:
            value_list = ",".join( [ str(x) for x in values ])
            logging.exception( "fill_list: values: %s currentvalue: %s",
                              value_list , str(current_value) )
            raise err

    def fill_table(self, dboject, current_value:str=None):
        """
            Fill the dropdown box with values from the database.
            The input should be the results of an 'execute(...)'
        """
        self.clear()
        rows = dboject.get_all()
        if rows is not None and len(rows) > 0 :
            if isinstance( rows, list ):
                self.addItems( rows )
            else:
                self.addItems( [row['name'] for row in rows])
        self.set_current_item( current_value )
        self._finish_setup()
