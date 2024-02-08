"""
User Interface : Border Glow

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

from PySide6.QtCore     import QTimer
class BorderGlow():
    """BorderGlow will set the border colour and then cycle throug them
    as time elapases.
    """
    DEFAULT_COLOUR_PALLET = [ '#236dc9','#236dc9','#1c58a1','#174781','#133968','#102e54',
                      '#0d2544','#0b1e37','#09182c','#081424','#07101d','#060d18',
                      '#000000' ]

    def __init__(self):

        self.set_colours( )
        self.border_label = None
        self.border_colour_index = 0

        self.border_timer = QTimer()
        self.set_interval_timer( 75 )
        self.border_timer.setSingleShot(True)
        self.border_timer.timeout.connect(self.on_timer)

    def set_interval_timer(self, t:int)->None:
        """ set the interval timer in msec """
        self.stop()
        self.timer_interval = t
        self.border_timer.setInterval( self.timer_interval )

    def set_colours(self, colours:list[str]=None)->None:
        """Set what colours we should cycle through

        Args:
            colours (list, optional): List of strings
                defining the colours to use (in RGB Hex).
                Defaults to None. (use built in colours)
        """
        if colours is None:
            self.colour_pallet = self.DEFAULT_COLOUR_PALLET
        else:
            self.colour_pallet = colours

    def set_border_object( self, borderobject=None)->None:
        """ Save what object should be 'glowing' """
        if borderobject is None:
            self.stop()
        else:
            self.border_label = borderobject

    def start(self, borderobject=None)->None:
        """ Decide if the border should glow or not"""
        if borderobject is not None:
            self.set_border_object( borderobject )
        if self.border_label is not None:
            if self.border_colour_index < len( self.colour_pallet ):
                bc = self.colour_pallet[ self.border_colour_index ]
                background =  f"background: {bc};"
                self.border_colour_index = self.border_colour_index+1
                self.border_label.setStyleSheet( background )
                self.border_timer.start()
            else:
                self.stop()

    def stop(self):
        """ Stop the timer and reset border"""
        self.border_colour_index = 0
        if self.border_label is not None:
            self.border_label.setStyleSheet("background: black;")
            self.border_label = None

    def on_timer(self):
        """ When the timer ends, restart timer"""
        self.start()
