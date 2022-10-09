# This Python file uses the following encoding: utf-8
# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022 by Chrles Gentry
#
# This file is part of Sheetmusic. 

# Sheetmusic is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
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
# See ToolConvert for script control
#
# 22-Sep-2022: Convert to use database

import sys
from os.path import expanduser
from util.toolconvert   import ToolConvert
from dil.preferences    import DilPreferences
from db.keys            import DbKeys, ImportNameSetting
from PySide6.QtCore     import Qt
from PySide6.QtGui      import QImageReader,QFont, QIntValidator
from PySide6.QtWidgets  import (
    QApplication, QButtonGroup,  QCheckBox,
    QComboBox,    QDialog,       QDialogButtonBox,
    QFileDialog,  QGridLayout,   QHBoxLayout,
    QLabel,       QLineEdit,     QMessageBox,
    QPlainTextEdit, QPushButton, QRadioButton,
    QTabWidget,   QTextEdit,     QVBoxLayout,   
    QWidget
)   
from ui.editItem import UiGenericCombo

class UiPreferences(QDialog):
    '''
    This creates a simple grid and populates it with info from the dil/preferences.
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
    _typeDesc = {
        "bmp":  "Bitmap image",
        "jpg":  "JPG Image",
        "tif":  "Tagged Information Format",
        "png":  "Portable Network Graphic",
        }
        
    def __init__(self, parent=None):
        super(UiPreferences, self).__init__(parent)
        self._device_settings['tiff']= self._device_settings['tif']
        self._device_settings['jpeg']= self._device_settings['jpg']
        self._typeDesc["jpeg"] = self._typeDesc["jpg"]
        self._typeDesc["tiff"] = self._typeDesc["tif"]

        self.setWindowTitle("Sheetmusic Preferences")
        self.settings = DilPreferences()
        self.script = ToolConvert()
        mainLayout = QVBoxLayout()

        self.fixedFont = QFont()
        self.fixedFont.setFixedPitch(True)
        self.fixedFont.setStyleHint( QFont.TypeWriter)
        self.fixedFont.setFamily("Courier New")

        self.createTabLayout()
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
        self.states = {}

    def _checkTextChange( self, linefield:QLineEdit , key ):
        if linefield.text() != self.settings.getValue( key ):
            self.states[ key ] = linefield.text()

    def _checkComboChange( self, combobox:QComboBox, key:str):
        if key not in self.states or combobox.currentData() != self.states[ key ]:
            self.states[ key ] = combobox.currentData()

    def getChanges( self ):
        self._checkTextChange( self.txtScriptShell  , DbKeys.SETTING_DEFAULT_SCRIPT )
        self._checkTextChange( self.txtScriptVars   , DbKeys.SETTING_DEFAULT_SCRIPT_VAR )
        #self._checkTextChange( self.textPdfConvert , DbKeys.SETTING_PDF_SCRIPT )

        self._checkComboChange( self.cmbPageBack ,          DbKeys.SETTING_PAGE_PREVIOUS )
        self._checkComboChange( self.cmbPageForward ,       DbKeys.SETTING_PAGE_NEXT )
        self._checkComboChange( self.cmbPreviousBookmark ,  DbKeys.SETTING_BOOKMARK_PREVIOUS )
        self._checkComboChange( self.cmbNextBookmark ,      DbKeys.SETTING_BOOKMARK_NEXT )
        self._checkComboChange( self.cmbFirstPageShown ,    DbKeys.SETTING_FIRST_PAGE_SHOWN )
        self._checkComboChange( self.cmbLastPageShown ,     DbKeys.SETTING_LAST_PAGE_SHOWN )
        
        return self.states

    def setKeys( self ):
        self.cmbPageBack.setCurrentItem(         self.settings.getValue( DbKeys.SETTING_PAGE_PREVIOUS) )
        self.cmbPageForward.setCurrentItem(      self.settings.getValue( DbKeys.SETTING_PAGE_NEXT) )
        self.cmbPreviousBookmark.setCurrentItem( self.settings.getValue( DbKeys.SETTING_BOOKMARK_PREVIOUS) )
        self.cmbNextBookmark.setCurrentItem(     self.settings.getValue( DbKeys.SETTING_BOOKMARK_NEXT) )
        self.cmbFirstPageShown.setCurrentItem(   self.settings.getValue( DbKeys.SETTING_FIRST_PAGE_SHOWN) )
        self.cmbLastPageShown.setCurrentItem(    self.settings.getValue( DbKeys.SETTING_LAST_PAGE_SHOWN) )

    def createTabLayout(self):
        self.tabLayout = QTabWidget()

        self.tabLayout.addTab(self.createFileLayout(),"File Settings")
        self.tabLayout.addTab(self.createBookSettings(), "Book settings" )
        self.tabLayout.addTab(self.createKeyboardLayout(), "Key Modifiers")
        self.tabLayout.addTab(self.createConvertPdfLayout(), "Script")
        self.tabLayout.addTab(self.createShellScriptLayout(), "Script Settings")

        return self.tabLayout

    def labelGrid( self, grid:QGridLayout, labels:list):
        for i, label in enumerate(labels, 0 ):
            if label is None:
                lbl = QLabel( )
                lbl.setText( " " )
                grid.addWidget(lbl , i , 0 )
            elif len( label ) >0 :
                lbl = QLabel( )
                lbl.setText( "<b>{}</b>:".format( label ) )
                lbl.setTextFormat( Qt.RichText )
                grid.addWidget(lbl , i , 0 )

    def createFileLayout(self) ->QWidget:
        labels = ["Sheetmusic directory","Database Directory", "Number of recent files", None, None, None]
        self.widgetFile  = QWidget()
        self.layoutFile  = QGridLayout()
        self.labelGrid( self.layoutFile , labels )
        self.widgetFile.setLayout( self.layoutFile)
        return  self.widgetFile

    def createBookSettings(self)->QWidget:
        labels = ["Book page formatted as","Page layout", None, None, None, None]
        self.widgetBook  = QWidget()
        self.layoutBook = QGridLayout()
        self.labelGrid( self.layoutBook , labels )
        self.widgetBook.setLayout( self.layoutBook)
        return  self.widgetBook

    def createShellScriptLayout(self) ->QWidget:
        labels = ["Command to run", "Command line options",None,"Conversion type", "Import name settings", None, None]
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
        btnBox.addButton( 'Reinitialise' , QDialogButtonBox.ResetRole )
        btnBox.addButton( "Preview"      , QDialogButtonBox.AcceptRole)
        btnBox.clicked.connect(self.actionPdf )

        return btnBox

    def formatDirectory(self , layout:QGridLayout, row:int ):
        '''
            Location of where to store music files

        '''
        hlayout = QHBoxLayout()
        self.lblDefaultDir = QLabel( self.settings.getValue( DbKeys.SETTING_DEFAULT_PATH_MUSIC, DbKeys.VALUE_DEFAULT_DIR) )
        self.lblDefaultDir.setObjectName( DbKeys.SETTING_DEFAULT_PATH_MUSIC )
        self.btnChangeDefaultDir = QPushButton("Change...")
        self.btnResetDefaultDir  = QPushButton("Restore Defaults")

        hlayout.addWidget( self.lblDefaultDir )
        hlayout.addWidget( self.btnChangeDefaultDir )
        hlayout.addWidget( self.btnResetDefaultDir )

        self.btnChangeDefaultDir.pressed.connect( self.actionChangeDefaultDir )
        self.btnResetDefaultDir.pressed.connect(  self.actionResetDefaultDir )

        layout.addLayout( hlayout, row , 1 ,alignment=Qt.AlignLeft)

    def formatDatabaseDir(self , layout:QGridLayout, row:int ):
        hlayout = QHBoxLayout()

        self.lblDbDir = QLabel( self.settings.getDirectoryDB() )
        self.lblDbDir.setObjectName( DbKeys.SETTING_DEFAULT_PATH_MUSIC_DB )
        self.btnChangeDbDir = QPushButton("Change...")
        self.btnResetDbDir  = QPushButton("Restore Defaults")

        hlayout.addWidget( self.lblDbDir )
        hlayout.addWidget( self.btnChangeDbDir )
        hlayout.addWidget( self.btnResetDbDir )

        self.btnChangeDbDir.pressed.connect( self.actionChangeDbDir )
        self.btnResetDbDir.pressed.connect( self.actionResetDbDir )

        layout.addLayout( hlayout, row , 1 ,alignment=Qt.AlignLeft)

    def formatRecentFiles( self, layout:QGridLayout, row:int ):
        values = [ str(x) for x in range(DbKeys.VALUE_RECENT_SIZE_MIN, DbKeys.VALUE_RECENT_SIZE_MAX+1)]
        current = self.settings.getValue( DbKeys.SETTING_MAX_RECENT_SIZE , DbKeys.VALUE_RECENT_SIZE_DEFAULT)
        self.cmbRecentFiles = UiGenericCombo( isEditable=False, fill=values, currentValue=current , name=DbKeys.SETTING_MAX_RECENT_SIZE)
        self.cmbRecentFiles.currentTextChanged.connect( self.actionRecentFiles )
        layout.addWidget( self.cmbRecentFiles, row, 1 )

    def formatFiletype( self, layout:QGridLayout, row:int  )->int:
        self.cmbType = QComboBox()
        self.cmbType.setObjectName(DbKeys.SETTING_FILE_TYPE )
        ftype = self.settings.getValue( DbKeys.SETTING_FILE_TYPE)
        for bvalue in QImageReader.supportedImageFormats() :
            key = bvalue.data().decode()
            if key in self._typeDesc:
                self.cmbType.addItem( "{:4}: {}".format(key, self._typeDesc[key]), userData=key )
        idx = self.cmbType.findData( ftype )
        if idx > -1:
            self.cmbType.setCurrentIndex( idx )
        layout.addWidget( self.cmbType, row, 1)
        self.cmbType.currentIndexChanged.connect(self.actionTypeChanged)
        return row+1

    def formatFileDevice( self ,layout:QGridLayout, row:int )->int:
        self.cmbDevice = QComboBox()
        self.cmbDevice.setObjectName( DbKeys.SETTING_DEFAULT_GSDEVICE )
        layout.addWidget( self.cmbDevice, row, 1)

        ftype = self.settings.getValue( DbKeys.SETTING_DEFAULT_GSDEVICE,DbKeys.SETTING_DEFAULT_GSDEVICE )
        type = self.cmbType.currentData()
        self.cmbDevice.clear()
        for key,value in self._device_settings[type].items():
            self.cmbDevice.addItem("{:4}: {}".format( key, value), userData=key)
        idx = self.cmbDevice.findData( ftype )
        if idx > -1:
            self.cmbDevice.setCurrentIndex( idx )
        self.cmbDevice.currentIndexChanged.connect(self.actionDeviceChanged)
        return row+1

    def formatNameImport(self, layout:QGridLayout, row:int)->int:
        currentValue = self.settings.getValue( DbKeys.SETTING_NAME_IMPORT , DbKeys.VALUE_NAME_IMPORT_FILE_1 )
        self.cmbNameImport = UiGenericCombo( False, ImportNameSetting().forImportName, currentValue, name=DbKeys.SETTING_NAME_IMPORT )
        layout.addWidget( self.cmbNameImport , row, 1 )
        self.cmbNameImport.currentTextChanged.connect(self.actionNameImport )
        return row+1

    def formatReopenLastBook( self , layout:QGridLayout, row:int )->int:
        self.checkReopen = QCheckBox()
        self.checkReopen.setObjectName( DbKeys.SETTING_LAST_BOOK_REOPEN )
        self.checkReopen.setText("Reopen last book")
        self.checkReopen.setCheckable(True)
    
        self.checkReopen.setChecked(self.settings.getValueBool( DbKeys.SETTING_LAST_BOOK_REOPEN, DbKeys.VALUE_REOPEN_LAST ))
        layout.addWidget( self.checkReopen, row, 1)
        self.checkReopen.stateChanged.connect( self.actionReopenLastBook)
        return row+1

    def formatAspectRatio( self , layout:QGridLayout, row:int)->int:
        self.checkAspect = QCheckBox()
        self.checkAspect.setObjectName(DbKeys.SETTING_KEEP_ASPECT )
        self.checkAspect.setText("Keep aspect ratio for pages")
        self.checkAspect.setCheckable(True)
        self.checkAspect.setChecked(self.settings.getValueBool( DbKeys.SETTING_KEEP_ASPECT, DbKeys.VALUE_KEEP_ASPECT))
        layout.addWidget( self.checkAspect, row, 1 )
        self.checkAspect.stateChanged.connect(self.actionAspectRatio )
        return row+1

    def formatLayout(self , layout:QGridLayout, row:int)->int:
        pageLayout = self.settings.getValue(DbKeys.SETTING_PAGE_LAYOUT )
        self.btnOnePage = QRadioButton()
        self.btnOnePage.setText(u"1 page")
        self.btnOnePage.setObjectName(DbKeys.VALUE_PAGES_SINGLE)
        self.btnTwoPage = QRadioButton()
        self.btnTwoPage.setText(u"2 pages")
        self.btnTwoPage.setObjectName(DbKeys.VALUE_PAGES_DOUBLE)
        self.btnBox = QButtonGroup()
        self.btnBox.addButton( self.btnOnePage)
        self.btnBox.addButton(self.btnTwoPage)
        self.btnBox.setExclusive(True)
        if pageLayout == DbKeys.VALUE_PAGES_SINGLE:
            self.btnOnePage.setChecked(True)
        else:
            self.btnTwoPage.setChecked(True)
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.btnOnePage)
        btnLayout.addWidget(self.btnTwoPage)
        layout.addLayout( btnLayout , row,1 )
        return row+1

        self.btnBox.buttonClicked.connect( self.actionLayout)

    def formatScript(self, layout:QGridLayout, row:int )->int:
        self.txtScriptShell = QLineEdit()
        self.txtScriptShell.setObjectName(DbKeys.SETTING_DEFAULT_SCRIPT )
        self.txtScriptShell.setText( self.settings.getValue( DbKeys.SETTING_DEFAULT_SCRIPT) )
        layout.addWidget( self.txtScriptShell, row,1)
        return row+1
        
    def formatScriptVars(self, layout:QGridLayout, row:int)->int:
        self.txtScriptVars  = QLineEdit()
        self.txtScriptVars.setObjectName(DbKeys.SETTING_DEFAULT_SCRIPT_VAR )
        self.txtScriptVars.setText(  self.settings.getValue(DbKeys.SETTING_DEFAULT_SCRIPT_VAR)  )
        layout.addWidget( self.txtScriptVars, row, 1)
        lblHintScriptVar = QLabel()
        lblHintScriptVar.setText("Use a semicolon to separate options, e.g. -c;-d;-e")
        layout.addWidget( lblHintScriptVar, row+1,1 )
        return row+2

    def formatData(self ):
        #
        self.formatDirectory(   self.layoutFile, 0 )
        self.formatDatabaseDir( self.layoutFile, 1 )
        self.formatRecentFiles( self.layoutFile, 2 )
        #
        row = self.formatFiletype( self.layoutBook, 0 )
        row = self.formatLayout(self.layoutBook, row  )
        row = self.formatReopenLastBook( self.layoutBook,row )
        self.formatAspectRatio(self.layoutBook, row )
        #
        row = self.formatScript(self.layoutShellScript, 0 )
        row = self.formatScriptVars(self.layoutShellScript, row )
        row = self.formatFileDevice( self.layoutShellScript, row )
        row = self.formatNameImport( self.layoutShellScript, row )
        #
        self.formatKeyMods( self.layoutKeyboard, 0  )

        self.textPdfConvert.setPlainText( self.script.readRaw() )

    def formatKeyMods(self , layout:QGridLayout, row:int):
        """
            Keymods takes up one tab page
        """
        from keymodifiers import KeyModifiers
        km = KeyModifiers()
        row = 0
        col = 1

        lbl = QLabel()
        lbl.setText("<h3>Page Number Navigation</h3>")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget( lbl, row, 0, 1, 2 , alignment = Qt.AlignCenter)

        row += 1
        self.cmbPageBack = UiGenericCombo( isEditable=False, fill=km.pageBack(), name='pageBack')
        layout.addWidget( self.cmbPageBack, row, col)

        row += 1
        self.cmbPageForward = UiGenericCombo( isEditable=False, fill=km.pageForward() , name='pageForward')
        layout.addWidget( self.cmbPageForward, row, col)

        row += 1
        self.cmbFirstPageShown =  UiGenericCombo( isEditable=False, fill=km.firstPageShown() , name='firstPage')
        layout.addWidget( self.cmbFirstPageShown, row, col)

        row += 1
        self.cmbLastPageShown =  UiGenericCombo( isEditable=False, fill=km.lastPageShown() , name='lastPage')
        layout.addWidget( self.cmbLastPageShown, row, col)

        row += 1
        lbl = QLabel()
        lbl.setText("<h3>Bookmark Navigation</h3>")
        layout.addWidget( lbl, row, 0, 1, 2 , alignment = Qt.AlignCenter)

        row += 1
        self.cmbPreviousBookmark = UiGenericCombo( isEditable=False, fill=km.previousBookmark() , name='cmbPreviousBookmark')
        layout.addWidget( self.cmbPreviousBookmark, row, col)

        row += 1
        self.cmbNextBookmark = UiGenericCombo( isEditable=False, fill=km.nextBookmark() , name='cmbNextBookmark')
        layout.addWidget( self.cmbNextBookmark, row, col)

        ## This will set the keyboard mods to what is stored in the database (if any)
        self.setKeys()

        del km

    def createMainButtons(self):
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Cancel | QDialogButtonBox.Save)
        self.buttons.clicked.connect(self.actionMainButtonClicked)


    def editItem(self, item:QWidget):
        self.settingsTable.blockSignals(True)
        name = item.objectName()
        self.states[ name ] = item.text().strip()
        self.settingsTable.blockSignals(False)

    def editDatabaseDir(self, value ):
        if value != self.settings.getLocationDB( ):
            self.states[  DbKeys.SETTING_DEFAULT_PATH_MUSIC_DB ] = value
        elif DbKeys.SETTING_DEFAULT_PATH_MUSIC_DB in self.states:
                self.states.pop(  DbKeys.SETTING_DEFAULT_PATH_MUSIC_DB )
    
    def actionTextChanged(self):
        if self.textPdfConvert.toPlainText().strip() != self.settings.getValue(DbKeys.SETTING_PDF_SCRIPT ).strip():
            self.states[ DbKeys.SETTING_PDF_SCRIPT] = self.textPdfConvert.toPlainText().strip()

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
            self.textPdfConvert.setPlainText( self.settings.getValue( DbKeys.SETTING_PDF_SCRIPT ))
        elif txt == 'Reinitialise':
            if QMessageBox.AcceptRole == QMessageBox.question( self, "Reset script", "Reset database script to default"):
                from db.setup import Setup
                Setup().RestoreDefaultPdfScript()
                self.textPdfConvert.setPlainText( self.settings.getValue( DbKeys.SETTING_PDF_SCRIPT ))
        elif txt == 'Preview':
            self.actionPdfPreview()
        elif txt == 'Help':
            self.actionHelp()
        else:
            print("???", txt)
    
    def actionChangeDefaultDir(self):
        cdir = self.lblDefaultDir.text()
        newDirName = QFileDialog.getExistingDirectory(
            self,
            "Change Sheetmusic Directory",
            dir=cdir,
            options=QFileDialog.Option.ShowDirsOnly)
        if newDirName:
            self.lblDefaultDir.setText( newDirName )
            self.lblDefaultDir.show()
            self.flagChanged = True
            self.states[ DbKeys.SETTING_DEFAULT_PATH_MUSIC ] = newDirName
        self.btnChangeDefaultDir.setDown( False)

    def actionChangeDbDir(self):
        cdir = self.lblDbDir.text()
        newDirName = QFileDialog.getExistingDirectory(
            self,
            "Change Database Directory",
            dir=cdir,
            options=QFileDialog.Option.ShowDirsOnly)
        if newDirName:
            self.lblDbDir.setText( newDirName )
            self.lblDbDir.show()
            self.flagChanged = True
            self.states[ DbKeys.SETTING_DEFAULT_PATH_MUSIC_DB ] = newDirName
        self.btnChangeDbDir.setDown( False)

    def actionResetDefaultDir(self):
        cdir = expanduser(  DbKeys.VALUE_DEFAULT_DIR)
        self.lblDefaultDir.setText( cdir )
        self.states[DbKeys.SETTING_DEFAULT_PATH_MUSIC] = cdir
        self.flagChanged = True

    def actionResetDbDir(self):
        cdir = DbKeys.VALUE_DEFAULT_DIR
        self.lblDbDir.setText( cdir )
        self.states[DbKeys.SETTING_DEFAULT_PATH_MUSIC_DB] = cdir
        self.flagChanged = True

    def actionTypeChanged(self, value):
        self.states[ DbKeys.SETTING_FILE_TYPE ] = self.cmbType.currentData()
        self.flagChanged = True
        self.formatFileDevice( self.layoutShellScript, 3 )

    def actionDeviceChanged( self, value ):
        self.states[ DbKeys.SETTING_DEFAULT_GSDEVICE] = self.cmbDevice.currentData()
        self.flagChanged = True

    def actionNameImport( self, value ):
        self.states[self.cmbNameImport.objectName() ] = value
        self.flagChanged = True

    def actionRecentFiles( self, value ):
        self.states[ self.cmbRecentFiles.objectName() ] = value
        self.flagChanged = True

    def actionReopenLastBook(self, status):
        '''
        Save the state of the 'ReopenLastBook checkbox '''
        self.states[ DbKeys.SETTING_LAST_BOOK_REOPEN ] = self.checkReopen.isChecked()
        self.flagChanged = True

    def actionAspectRatio( self, status ):
        self.states[ DbKeys.SETTING_KEEP_ASPECT ] = self.checkAspect.isChecked()
        self.flagChanged = True
    
    def actionLayout(self, buttonObject ):
        self.flagChanged = True
        self.states[ DbKeys.SETTING_PAGE_LAYOUT ] = buttonObject.objectName() 

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
    window.formatData()
    window.show()
    sys.exit(app.exec())
