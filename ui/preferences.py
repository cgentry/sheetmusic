# This Python file uses the following encoding: utf-8
# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022 by Chrles Gentry
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This will display MusicSettings and allow them to be changed. It does not
# open, or save, settings. The caller can get the information by calling
# getChanges() which will return either None or a dictionary/list of changes
#
# If the settings for the script are changed, that will be handled by the
# class 'ToolConvert'.

import sys
from os.path import expanduser
from musicsettings import MusicSettings, MSet
from util.toolconvert import ToolConvert

from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QCheckBox,
    QComboBox, QDialog, QDialogButtonBox, 
    QFileDialog, QGridLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPlainTextEdit, 
    QPushButton, QRadioButton, QTabWidget, 
    QTextEdit, QVBoxLayout, QWidget )   
from PySide6.QtCore import Qt
from PySide6.QtGui import QImageReader,QFont

class UiPreferences(QDialog):
    '''
    This creates a simple grid and populates it with info from musicfile.py
    '''

    _tool_script_pdf = "convert-pdf.smc"
    _device_settings = {
        'png':{ 'png16m'  : "24-bit RGB color", 
                'pnggray' : "Grayscale"},
        'jpg':{ 'jpeg'    : "Standard JPEG",
                'jpeggray': "Grayscale JPEG"},
        'bmp':{ 'bmp16m'  : '24-bit RGB color',
                'bmpgray' : 'Grayscale'},
        'tif':{ 'tiff24nc': '24-bit RGB color',
                'tiffgray': 'Grayscale'},
        }

    def __init__(self, parent=None):
        super(UiPreferences, self).__init__(parent)
        self.setWindowTitle("Sheetmusic Preferences")
        self.script = ToolConvert()
        mainLayout = QVBoxLayout()

        self.fixedFont = QFont()
        self.fixedFont.setFixedPitch(True)
        self.fixedFont.setStyleHint( QFont.TypeWriter)
        self.fixedFont.setFamily("Courier New")

        self.formatTabs()
        self.createMainButtons()
        
        mainLayout.addWidget(self.tabLayout)
        mainLayout.addWidget(self.buttons)
        self.setLayout(mainLayout)
        self.clear()

    def clear(self):
        '''
        Setup and clear any variables used by modules
        '''
        self.flagChanged = False
        self.textChanged = False
        self.states = {}

    def getChanges( self ):
        changes = {}
        if self.textChanged:
            self.script.writeRaw( self.textPdfConvert.toPlainText().strip() )
        if self.flagChanged:
            changes = { "settings": self.states, "scriptChanged": self.textChanged }
        changes["keys"] ={
            MSet.SETTING_PAGE_PREVIOUS      : self.cmbPageBack.currentData(),
            MSet.SETTING_PAGE_NEXT          : self.cmbPageForward.currentData() ,
            MSet.SETTING_BOOKMARK_PREVIOUS  : self.cmbPreviousBookmark.currentData() ,
            MSet.SETTING_BOOKMARK_NEXT      : self.cmbNextBookmark.currentData() ,
            MSet.SETTING_FIRST_PAGE_SHOWN   : self.cmbFirstPageShown.currentData(),
            MSet.SETTING_LAST_PAGE_SHOWN    : self.cmbLastPageShown.currentData(),
        }
        return changes

    def setKeys( self ):
        self.settings.beginGroup( MSet.SETTING_GROUP_KEYS)
        #
        val = self.settings.value( MSet.SETTING_PAGE_PREVIOUS)
        if val:
            self.cmbPageBack.setCurrentIndex( self.cmbPageBack.findData( val ))
        #
        val = self.settings.value( MSet.SETTING_PAGE_NEXT)
        if val:
            self.cmbPageForward.setCurrentIndex( self.cmbPageForward.findData( val ))
        #
        val = self.settings.value( MSet.SETTING_BOOKMARK_PREVIOUS)
        if val:
            self.cmbPreviousBookmark.setCurrentIndex( self.cmbPreviousBookmark.findData( val ))
        #
        val = self.settings.value( MSet.SETTING_BOOKMARK_NEXT)
        if val:
            self.cmbNextBookmark.setCurrentIndex( self.cmbNextBookmark.findData( val ))
        #
        val = self.settings.value( MSet.SETTING_FIRST_PAGE_SHOWN)
        if val:
            self.cmbFirstPageShown.setCurrentIndex( self.cmbFirstPageShown.findData( val ))
        #
        val = self.settings.value( MSet.SETTING_LAST_PAGE_SHOWN)
        if val:
            self.cmbLastPageShown.setCurrentIndex( self.cmbLastPageShown.findData( val ))

        self.settings.endGroup()


    def formatTabs(self):
        self.tabLayout = QTabWidget()

        self.tabLayout.addTab(self.createFileLayout(),"File Settings")
        self.tabLayout.addTab(self.createKeyboardLayout(), "Key Modifiers")
        self.tabLayout.addTab(self.createConvertPdfLayout(), "Script")
        self.tabLayout.addTab(self.createShellScriptLayout(), "Script Settings")

        return self.tabLayout

    def labelGrid( self, grid:QGridLayout, labels):
        for i in range(0,len(labels)):
            if len(labels[i]) >0 :
                lbl = QLabel( )
                lbl.setText( "<b>{}</b>:".format(labels[i]) )
                lbl.setTextFormat( Qt.RichText )
                grid.addWidget(lbl , i , 0 )

    def createFileLayout(self) ->QWidget:
        labels = ["Default directory","Filetype","Conversion","Layout"]
        self.widgetFile  = QWidget()
        self.layoutFile = QGridLayout()
        self.labelGrid( self.layoutFile , labels )
        self.widgetFile.setLayout( self.layoutFile)
        return  self.widgetFile

    def createShellScriptLayout(self) ->QWidget:
        labels = ["Command to run", "Command line options"]
        self.widgetShellScript  = QWidget()
        self.layoutShellScript = QGridLayout()
        self.labelGrid( self.layoutShellScript , labels )
        self.widgetShellScript.setLayout( self.layoutShellScript)

        return self.widgetShellScript

    def createKeyboardLayout(self)->QWidget:
        labels = [
            ""
            , "Previous Page"
            , "Next Page"
            , "First Page"
            , "Last Page"
            , ""
            , "Previous Bookmark"
            , "Next Bookmark"
             ]
        self.widgetKeyboard  = QWidget()
        self.layoutKeyboard = QGridLayout()
        self.labelGrid( self.layoutKeyboard , labels )
        self.widgetKeyboard.setLayout( self.layoutKeyboard)
        return  self.widgetKeyboard

    def createConvertPdfLayout(self)->QWidget:
        self.textPdfConvert = QPlainTextEdit()
        self.widgetPdfConvert = QWidget()
        self.layoutPdfConvert = QVBoxLayout()
        self.layoutPdfConvert.addWidget(self.textPdfConvert)
        self.layoutPdfConvert.addWidget( self.btnPdfConvert() )

        self.textPdfConvert.setFont( self.fixedFont )
        self.widgetPdfConvert.setLayout( self.layoutPdfConvert)
        self.textPdfConvert.textChanged.connect( self.actionTextChanged )
        return self.widgetPdfConvert

    def btnPdfConvert(self) -> QDialogButtonBox:
        btnBox = QDialogButtonBox()
        btnBox.addButton( QDialogButtonBox.Help)
        btnBox.addButton( QDialogButtonBox.RestoreDefaults )
        btnBox.addButton( "Preview" , QDialogButtonBox.AcceptRole)
        btnBox.clicked.connect(self.actionPdf )

        return btnBox
    
    def actionTextChanged(self):
        self.textChanged = True

    def actionHelp(self):
        helpLayout = QVBoxLayout()
        helpDlg = QDialog()
        helpDlg.setMinimumHeight(500)

        def actionHelpClose(self):
            helpDlg.reject()

        helpPdf = QTextEdit()
        helpPdf.setText(self._helpPdfCmd)
        helpPdf.setReadOnly(True)
        helpPdf.setMinimumWidth(500)
        
        helpLayout.addWidget( helpPdf)
        btnPdf = QPushButton("Close")
        helpLayout.addWidget( btnPdf)
        btnPdf.clicked.connect( actionHelpClose )
        
        helpDlg.setLayout( helpLayout )
        helpDlg.exec()
    

    def actionPdfPreview(self):
        #   {{source}}   Location of PDF to convert
        #   {{target}}   File Setting ; Default Directory
        #   {{name}}     Name for book. Prompted when run
        #   {{type}}     File Setting ; Filetype
        #   {{device}}   GS setting for 'Filetype'
        #                for PNG this should be 'png16m'
        #   {{debug}}    Set to 'echo' if debug is turned on
        txt = self.script.expandScript(
            self.settings,
            self.textPdfConvert.toPlainText().strip(),
            "/directory/of/book.pdf" )
        if txt != "":
            previewDlg = QDialog()
            previewDlg.setMinimumHeight(500)

            def previewActionClose(self):
                previewDlg.reject()
            previewLayout = QVBoxLayout()

            txtPreview = QTextEdit()
            txtPreview.setText(txt)
            txtPreview.setReadOnly(True)
            txtPreview.setMinimumWidth(500)
            txtPreview.setMinimumHeight(500)
            txtPreview.setFont( self.fixedFont )
            previewLayout.addWidget( txtPreview)

            btnPreview = QPushButton("Close")
            previewLayout.addWidget( btnPreview)
            btnPreview.clicked.connect( previewActionClose )

            previewDlg.setLayout( previewLayout )
            previewDlg.exec()

    def actionPdf(self, button):
        txt = button.text().strip()
        if txt == 'Restore Defaults':
            self.textPdfConvert.setPlainText(self.script.default())
        elif txt == 'Preview':
            self.actionPdfPreview()
        elif txt == 'Help':
            self.actionHelp()
        else:
            print("???", txt)
    
    def formatDirectory(self, settingObject:MusicSettings ):
        '''
        Setup values from the MusicSettings object. 

        MusicSettings contains all the values previously set. 
        These include directory, filetype and default layout.
        '''
        dir = settingObject.value(MSet.byDefault(MSet.SETTING_DEFAULT_PATH),MSet.VALUE_DEFAULT_DIR)
        
        hlayout = QHBoxLayout()

        self.lblDefaultDir = QLabel( dir )
        self.btnChangeDefaultDir = QPushButton("Change...")
        self.btnResetDefaultDir  = QPushButton("Restore Defaults")

        hlayout.addWidget( self.lblDefaultDir )
        hlayout.addWidget( self.btnChangeDefaultDir )
        hlayout.addWidget( self.btnResetDefaultDir )

        self.btnChangeDefaultDir.pressed.connect( self.actionChangeDefaultDir )
        self.btnResetDefaultDir.pressed.connect( self.actionResetDefaultDir )

        self.layoutFile.addLayout( hlayout, 0, 1 ,alignment=Qt.AlignLeft)

    def formatFiletype( self, settingObject ):
        typeDesc = {
            "bmp":  "Bitmap image",
            "jpg":  "JPG Image",
            "tif":  "Tagged Information Format",
            "png":  "Portable Network Graphic",
        }
        typeDesc["jpeg"] = typeDesc["jpg"]
        typeDesc["tiff"] = typeDesc["tif"]
        self.cmbType = QComboBox()
        self.cmbDevice = QComboBox()
        ftype = settingObject.value(MSet.byDefault(MSet.SETTING_DEFAULT_TYPE) )
        for bvalue in QImageReader.supportedImageFormats() :
            key = bvalue.data().decode()
            if key in typeDesc:
                self.cmbType.addItem( "{:4}: {}".format(key, typeDesc[key]), userData=key )
        idx = self.cmbType.findData( ftype )
        if idx > -1:
            self.cmbType.setCurrentIndex( idx )
        self.layoutFile.addWidget( self.cmbType, 1, 1)
        self.layoutFile.addWidget( self.cmbDevice, 2, 1)
        self.cmbType.currentIndexChanged.connect(self.actionTypeChanged)
        self.cmbDevice.currentIndexChanged.connect(self.actionDeviceChanged)
        self.formatFileDevice()

    def formatFileDevice( self ):
        self._device_settings['tiff']= self._device_settings['tif']
        self._device_settings['jpeg']= self._device_settings['jpg']
        ftype = self.settings.value(MSet.byDefault(MSet.SETTING_DEFAULT_GSDEVICE),"" )
        type = self.cmbType.currentData()
        self.cmbDevice.clear()
        for key,value in self._device_settings[type].items():
            self.cmbDevice.addItem("{:4}: {}".format( key, value), userData=key)
        idx = self.cmbDevice.findData( ftype )
        if idx > -1:
            self.cmbDevice.setCurrentIndex( idx )


    def formatReopenLastBook( self, settingObject ):
        self.checkReopen = QCheckBox()
        self.checkReopen.setText("Reopen last book")
        self.checkReopen.setCheckable(True)
        if settingObject.value(MSet.byDefault(MSet.SETTING_DEFAULT_OPEN_LAST)):
            self.checkReopen.setChecked(True)
        self.layoutFile.addWidget( self.checkReopen, 4,1)
        self.checkReopen.stateChanged.connect( self.actionReopenLastBook)

    def formatAspectRatio( self, settingObject ):
        self.checkAspect = QCheckBox()
        self.checkAspect.setText("Keep aspect ratio for pages")
        self.checkAspect.setCheckable(True)
        if settingObject.value(MSet.byDefault( MSet.SETTING_DEFAULT_ASPECT )):
            self.checkAspect.setChecked(True)
        self.layoutFile.addWidget( self.checkAspect, 5, 1 )
        self.checkAspect.stateChanged.connect(self.actionAspectRatio )

    def formatLayout(self, settingObject ):
        layout = settingObject.value(MSet.byDefault(MSet.SETTING_DEFAULT_LAYOUT))
        self.btnOnePage = QRadioButton()
        self.btnOnePage.setText(u"1 page")
        self.btnOnePage.setObjectName(MSet.VALUE_PAGES_SINGLE)
        self.btnTwoPage = QRadioButton()
        self.btnTwoPage.setText(u"2 pages")
        self.btnTwoPage.setObjectName(MSet.VALUE_PAGES_DOUBLE)
        self.btnBox = QButtonGroup()
        self.btnBox.addButton( self.btnOnePage)
        self.btnBox.addButton(self.btnTwoPage)
        self.btnBox.setExclusive(True)
        if layout == MSet.VALUE_PAGES_SINGLE:
            self.btnOnePage.setChecked(True)
        else:
            self.btnTwoPage.setChecked(True)
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.btnOnePage)
        btnLayout.addWidget(self.btnTwoPage)
        self.layoutFile.addLayout( btnLayout , 3,1 )

        self.btnBox.buttonClicked.connect( self.actionLayout)

    def formatScript(self, settings ):
        self.txtScriptShell = QLineEdit()
        self.txtScriptVars  = QLineEdit()
        self.txtScriptShell.setText( self.settings.value( 
                    MSet.byDefault( MSet.SETTING_DEFAULT_SCRIPT), 
                    MSet.VALUE_DEFAULT_SCRIPT) )
        self.txtScriptVars.setText( self.settings.value( 
                        MSet.byDefault( MSet.SETTING_DEFAULT_SCRIPT_VAR), 
                        MSet.VALUE_DEFAULT_SCRIPT_VAR) )
        lblHintScriptVar = QLabel()
        lblHintScriptVar.setText("Use a semicolon to separate options, e.g. -c;-d;-e")
        
        self.layoutShellScript.addWidget( self.txtScriptShell, 0,1)
        self.layoutShellScript.addWidget( self.txtScriptVars, 1, 1)
        self.layoutShellScript.addWidget( lblHintScriptVar, 2,1 )

    def formatData(self, settingObject ):
        self.settings = settingObject
        self.script.setPath( settingObject )
        self.formatDirectory( settingObject)
        self.formatFiletype( settingObject )
        self.formatReopenLastBook( settingObject )
        self.formatAspectRatio(settingObject)
        self.formatLayout( settingObject)
        self.formatScript( settingObject )
        self.formatKeyMods( settingObject )

        self.textPdfConvert.setPlainText( self.script.readRaw(default=False) )

    def _addKeyToCombo( self, combo:QComboBox, dataToAdd):
        for description,value in dataToAdd:
            combo.addItem( str(description), userData=value )

    def formatKeyMods(self, settingObject ):
        from keymodifiers import KeyModifiers
        km = KeyModifiers()
        mods = km.getMods()
        del km
        row = 0
        col = 1

        lbl = QLabel()
        lbl.setText("<h3>Page Number Navigation</h3>")
        lbl.setAlignment(Qt.AlignCenter)
        self.layoutKeyboard.addWidget( lbl, row, 0, 1, 2 , alignment = Qt.AlignCenter)

        row += 1
        self.cmbPageBack = QComboBox()
        self._addKeyToCombo( self.cmbPageBack, mods["page-back"].items())
        self.layoutKeyboard.addWidget( self.cmbPageBack, row, col)

        row += 1
        self.cmbPageForward = QComboBox()
        self._addKeyToCombo( self.cmbPageForward, mods["page-forward"].items())
        self.layoutKeyboard.addWidget( self.cmbPageForward, row, col)

        row += 1
        self.cmbFirstPageShown = QComboBox()
        self._addKeyToCombo( self.cmbFirstPageShown, mods["first-page-shown"].items())
        self.layoutKeyboard.addWidget( self.cmbFirstPageShown, row, col)

        row += 1
        self.cmbLastPageShown = QComboBox()
        self._addKeyToCombo( self.cmbLastPageShown, mods["last-page-shown"].items())
        self.layoutKeyboard.addWidget( self.cmbLastPageShown, row, col)

        row += 1
        lbl = QLabel()
        lbl.setText("<h3>Bookmark Navigation</h3>")
        self.layoutKeyboard.addWidget( lbl, row, 0, 1, 2 , alignment = Qt.AlignCenter)

        row += 1
        self.cmbPreviousBookmark = QComboBox()
        self._addKeyToCombo( self.cmbPreviousBookmark, mods["previous-bookmark"].items())
        self.layoutKeyboard.addWidget( self.cmbPreviousBookmark, row, col)

        row += 1
        self.cmbNextBookmark = QComboBox()
        self._addKeyToCombo( self.cmbNextBookmark, mods["next-bookmark"].items())
        self.layoutKeyboard.addWidget( self.cmbNextBookmark, row, col)

        self.setKeys()


        
    def createMainButtons(self):
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Cancel | QDialogButtonBox.Save)
        self.buttons.clicked.connect(self.actionMainButtonClicked)

    def editItem(self, item):
        self.settingsTable.blockSignals(True)
        if item.text() != self.changes[item.row()]:
            self.changes[item.row()] = item.text()
        self.flagChanged = True
        self.settingsTable.blockSignals(False)

    def actionChangeDefaultDir(self):
        cdir = self.lblDefaultDir.text()
        newDirName = QFileDialog.getExistingDirectory(
            self,
            "Change Default SheetMusic Directory",
            dir=cdir,
            options=QFileDialog.Option.ShowDirsOnly)
        if newDirName:
            self.lblDefaultDir.setText( newDirName )
            self.lblDefaultDir.show()
            self.flagChanged = True
            self.states[MSet.byDefault(MSet.SETTING_DEFAULT_PATH)] = newDirName
        self.btnChangeDefaultDir.setDown( False)

    def actionResetDefaultDir(self):
        cdir = expanduser( MSet.VALUE_DEFAULT_DIR)
        self.lblDefaultDir.setText( cdir )
        self.states[MSet.byDefault(MSet.SETTING_DEFAULT_PATH)] = cdir
        self.flagChanged = True

    def actionTypeChanged(self, value):
        self.states[MSet.byDefault(MSet.SETTING_DEFAULT_TYPE)] = self.cmbType.currentData()
        self.flagChanged = True
        self.formatFileDevice()

    def actionDeviceChanged( self, value ):
        self.states[MSet.byDefault(MSet.SETTING_DEFAULT_GSDEVICE)] = self.cmbDevice.currentData()
        self.flagChanged = True

    def actionReopenLastBook(self, status):
        '''
        Save the state of the 'ReopenLastBook checkbox '''
        self.states[MSet.byDefault(MSet.SETTING_DEFAULT_OPEN_LAST)] = self.checkReopen.isChecked()
        self.flagChanged = True

    def actionAspectRatio( self, status ):
        self.states[MSet.byDefault(MSet.SETTING_DEFAULT_ASPECT)] = self.checkAspect.isChecked()
        self.flagChanged = True
    
    def actionLayout(self, buttonObject ):
        self.flagChanged = True
        self.states[MSet.byDefault(MSet.SETTING_DEFAULT_LAYOUT)] = buttonObject.objectName() 

    def actionMainButtonClicked(self, btn):
        if btn.text() == "Save" and self.flagChanged:
            self.accept()
            self.done(self.Accepted)
        else:
            self.reject()

    _helpPdfCmd = """<h1>Script</h1>
The script that comes with the system is based on UNIX/LINUX/MacOS rather
than Windows. You may enter a Windows script, and one may be provided in the future.
In the script, you have several 'variables' you can insert:
<ul>
<li>{{source}}}&nbsp;-&nbsp;This is the complete file path to the PDF. You will be prompted before the script is run.</li>
<li>{{target}}&nbsp;-&nbsp;This value is from the File Setting ; Default Directory</li>
<li>{{name}}}&nbsp;-&nbsp;Name for book. Prompted when run/<li>
<li>{{type}}}&nbsp;-&nbsp;This value is from the File Setting ; Filetype in preferences. </li>
<li>{{device}}}&nbsp;-&nbsp;GhostScript setting for 'Filetype'. For PNG this should be 'png16m'. This is changed dpending upon the Filetype you select.</li>
<li>{{debug}}}&nbsp;-&nbsp;Set to 'echo' if debug is turned on</li>
</ul>
<p>
The program will do a string replacement for each of these values. They must match <i>exactly</i>.
When the script is run, you will be able to run this in debug mode.
</p><p>
The script will be stored in the default music directory as 'convert-pdf.smc'. You can edit this with
any editor. If you change the music directory, the script will need to be moved manually to the new
location
</p>
"""
    

if __name__ == "__main__":
    app = QApplication()
    settings = MusicSettings()
    window = UiPreferences()
    window.formatData(settings)
    window.show()
    sys.exit(app.exec())
