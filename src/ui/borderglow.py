from PySide6.QtCore     import QTimer
class BorderGlow():
    DEFAULT_COLOUR_PALLET = [ '#236dc9','#236dc9','#1c58a1','#174781','#133968','#102e54',
                      '#0d2544','#0b1e37','#09182c','#081424','#07101d','#060d18',
                      '#000000' ]

    def __init__(self):
        
        self.setColours( ) 
        self.border_label = None
        self.border_colour_index = 0

        self.border_timer = QTimer()
        self.setTimerInterval( 75 )
        self.border_timer.setSingleShot(True)
        self.border_timer.timeout.connect(self.onTimer)

    def setTimerInterval(self, t:int)->None:
        self.stopBorderGlow()
        self.timer_interval = t
        self.border_timer.setInterval( self.timer_interval )

    def setColours(self, colours=None)->None:
        if colours is None:
            self.colour_pallet = self.DEFAULT_COLOUR_PALLET
        else:
            self.colour_pallet = colours

    def setBorderObject( self, borderobject=None)->None:
        if borderobject is None:
            self.stopBorderGlow()
        else:
            self.border_label = borderobject

    def startBorderGlow(self, borderobject=None)->None:
        if borderobject is not None:
            self.setBorderObject( borderobject )
        if self.border_label is not None:
            if self.border_colour_index < len( self.colour_pallet ):
                backgroundColour =  "background: {};".format( self.colour_pallet[ self.border_colour_index ] )
                self.border_colour_index = self.border_colour_index+1
                self.border_label.setStyleSheet( backgroundColour )
                self.border_timer.start()
            else:
                self.stopBorderGlow()

    def stopBorderGlow(self):
        self.border_colour_index = 0
        if self.border_label is not None:
            self.border_label.setStyleSheet("")
            self.border_label = None

    def onTimer(self):
        self.startBorderGlow()
