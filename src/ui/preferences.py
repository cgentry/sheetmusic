# This Python file uses the following encoding: utf-8
# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022,2023 by Chrles Gentry
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
# 22-Sep-2022: Convert to use database

import sys
import logging
from os.path import expanduser
from qdil.preferences    import DilPreferences
from qdb.keys            import DbKeys, ImportNameSetting
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
from ui.editItem    import UiGenericCombo
from util.toollist  import GenerateEditList
from util.toollist  import ToolScript

class UiPreferences(QDialog):
    '''
    This creates a simple grid and populates it with info from the qdil/preferences.
    '''

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
    _resolution = {
        "300":  "High resolution; largest size and best resolution (may cause display errors)",
        "200":  "Medium resolution; good size and resolution",
        "150":  "Lowest resolution; smallest size and average resolution"
    }
        
    def __init__(self, parent=None):
        super(UiPreferences, self).__init__(parent)
        self._device_settings['tiff']= self._device_settings['tif']
        self._device_settings['jpeg']= self._device_settings['jpg']
        self._typeDesc["jpeg"] = self._typeDesc["jpg"]
        self._typeDesc["tiff"] = self._typeDesc["tif"]

        self.setWindowTitle("Sheetmusic Preferences")
        self.settings = DilPreferences()
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
        #self.tabLayout.addTab(self.createConvertPdfLayout(), "Script")
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
        labels = ["Sheetmusic directory","Database Directory", "Number of recent files", "Editor", None, None]
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
        labels = ["Command to run", "Command line options",None,"Conversion type", "Resolution","Import name settings", None]
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

    def formatDirectory(self , layout:QGridLayout, row:int )->int:
        '''
            Location of where to store music files

        '''
        # Create and add Default path to music options
        self.lblSheetmusicDir = QLabel( self.settings.getValue( DbKeys.SETTING_DEFAULT_PATH_MUSIC, DbKeys.VALUE_DEFAULT_DIR) )
        self.lblSheetmusicDir.setObjectName( DbKeys.SETTING_DEFAULT_PATH_MUSIC )
        self.btn_change_sheetmusic_dir = QPushButton("Change...")
        self.btn_reset_sheetmusic_dir  = QPushButton("Restore Defaults")

        self.btn_change_sheetmusic_dir.pressed.connect( self.action_change_sheetmusic_dir )
        self.btn_reset_sheetmusic_dir.pressed.connect(  self.action_reset_sheetmusic_dir )

        hlayout = QHBoxLayout()
        hlayout.addWidget( self.lblSheetmusicDir )
        hlayout.addWidget( self.btn_change_sheetmusic_dir )
        hlayout.addWidget( self.btn_reset_sheetmusic_dir )

        layout.addLayout( hlayout, row , 1 ,alignment=Qt.AlignLeft)
        row += 1
        return row
    
    def formatUserScriptDir( self, layout:QGridLayout, row:int )->int:

        # create and add User Script path to music options
        self.label_user_script_dir = QLabel( self.settings.getValue( DbKeys.SETTING_PATH_USER_SCRIPT, DbKeys.VALUE_DEFAULT_USER_SCRIPT_DIR) )
        self.label_user_script_dir.setObjectName( DbKeys.SETTING_DEFAULT_PATH_MUSIC )
        self.btn_change_user_script_dir = QPushButton("Change...")
        self.btn_reset_user_script_dir  = QPushButton("Restore Defaults")

        self.btn_change_user_script_dir.pressed.connect( self.action_change_user_script_dir )
        self.btn_reset_user_script_dir.pressed.connect(  self.action_reset_user_script_dir )

        hlayout = QHBoxLayout()
        hlayout.addWidget( self.label_user_script_dir )
        hlayout.addWidget( self.label_user_script_dir )
        hlayout.addWidget( self.btn_reset_user_script_dir )

        layout.addLayout( hlayout, row , 1 ,alignment=Qt.AlignLeft)
        row += 1
        return row


    def formatDatabaseDir(self , layout:QGridLayout, row:int )->int:
        hlayout = QHBoxLayout()

        self.lbl_database_dir = QLabel( self.settings.getDirectoryDB() )
        self.lbl_database_dir.setObjectName( DbKeys.SETTING_DEFAULT_PATH_MUSIC_DB )
        self.btn_change_database_dir = QPushButton("Change...")
        self.btn_reset_database_dir  = QPushButton("Restore Defaults")

        hlayout.addWidget( self.lbl_database_dir )
        hlayout.addWidget( self.btn_change_database_dir )
        hlayout.addWidget( self.btn_reset_database_dir )

        self.btn_change_database_dir.pressed.connect( self.action_change_database_dir )
        self.btn_reset_database_dir.pressed.connect(  self.action_reset_database_dir )

        layout.addLayout( hlayout, row , 1 ,alignment=Qt.AlignLeft)
        row += 1
        return row

    def formatRecentFiles( self, layout:QGridLayout, row:int )->int:
        values = [ str(x) for x in range(DbKeys.VALUE_RECENT_SIZE_MIN, DbKeys.VALUE_RECENT_SIZE_MAX+1)]
        current = self.settings.getValue( DbKeys.SETTING_MAX_RECENT_SIZE , DbKeys.VALUE_RECENT_SIZE_DEFAULT)
        self.cmbRecentFiles = UiGenericCombo( isEditable=False, fill=values, currentValue=current , name=DbKeys.SETTING_MAX_RECENT_SIZE)
        self.cmbRecentFiles.currentTextChanged.connect( self.action_recent_files )
        layout.addWidget( self.cmbRecentFiles, row, 1 )
        row += 1
        return row

    def formatEditor( self, layout:QGridLayout, row:int )->int:
        edlist = GenerateEditList()
        values = edlist.list()
        fill_list = {"None": "" }
        for key, value in values.items():
            fill_list[ key ] = value.path()

                
        current = self.settings.getValue( DbKeys.SETTING_PAGE_EDITOR , "None" )
        
        self.cmbEditor = UiGenericCombo( isEditable=False, fill=fill_list, currentValue=current , name=DbKeys.SETTING_PAGE_EDITOR )
        self.cmbEditor.currentIndexChanged.connect(self.action_editor_changed)
        layout.addWidget( self.cmbEditor, row, 1 )
        
        row += 1
        return row
    
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
        self.cmbType.currentIndexChanged.connect(self.action_type_changed)
        return row+1
    
    def formatResolution( self, layout:QGridLayout, row:int )->int:
        self.cmbRes = QComboBox()
        self.cmbRes.setObjectName(DbKeys.SETTING_FILE_RES )
        fres = self.settings.getValue( DbKeys.SETTING_FILE_RES, default=DbKeys.VALUE_FILE_RES)
        for key, desc in self._resolution.items() :
            self.cmbRes.addItem( "{:4}: {}".format(key, desc), userData=key ) 
        idx = self.cmbRes.findData( fres )
        if idx > -1:
            self.cmbRes.setCurrentIndex( idx )
        layout.addWidget( self.cmbRes, row, 1)
        self.cmbRes.currentIndexChanged.connect(self.action_res_changed)
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
        self.cmbDevice.currentIndexChanged.connect(self.action_device_changed)
        return row+1

    def formatNameImport(self, layout:QGridLayout, row:int)->int:
        currentValue = self.settings.getValue( DbKeys.SETTING_NAME_IMPORT , DbKeys.VALUE_NAME_IMPORT_FILE_1 )
        self.cmbNameImport = UiGenericCombo( False, ImportNameSetting().forImportName, currentValue, name=DbKeys.SETTING_NAME_IMPORT )
        layout.addWidget( self.cmbNameImport , row, 1 )
        self.cmbNameImport.currentTextChanged.connect(self.action_name_import )
        return row+1

    def formatReopenLastBook( self , layout:QGridLayout, row:int )->int:
        self.checkReopen = QCheckBox()
        self.checkReopen.setObjectName( DbKeys.SETTING_LAST_BOOK_REOPEN )
        self.checkReopen.setText("Reopen last book")
        self.checkReopen.setCheckable(True)
    
        self.checkReopen.setChecked(self.settings.getValueBool( DbKeys.SETTING_LAST_BOOK_REOPEN, DbKeys.VALUE_REOPEN_LAST ))
        layout.addWidget( self.checkReopen, row, 1)
        self.checkReopen.stateChanged.connect( self.action_reopen_last_book)
        return row+1

    def formatAspectRatio( self , layout:QGridLayout, row:int)->int:
        self.checkAspect = QCheckBox()
        self.checkAspect.setObjectName(DbKeys.SETTING_KEEP_ASPECT )
        self.checkAspect.setText("Keep aspect ratio for pages")
        self.checkAspect.setCheckable(True)
        self.checkAspect.setChecked(self.settings.getValueBool( DbKeys.SETTING_KEEP_ASPECT, DbKeys.VALUE_KEEP_ASPECT))
        layout.addWidget( self.checkAspect, row, 1 )
        self.checkAspect.stateChanged.connect(self.action_aspect_ratio )
        return row+1

    def formatSmartPages( self, layout:QGridLayout, row:int)->int:
        self.checkSmartPages = QCheckBox()
        self.checkSmartPages.setObjectName(DbKeys.SETTING_SMART_PAGES )
        self.checkSmartPages.setText("Use smart page display( 1,2 -> 3,2 -> 3,4)")
        self.checkSmartPages.setCheckable(True)
        self.checkSmartPages.setChecked(self.settings.getValueBool( DbKeys.SETTING_SMART_PAGES, DbKeys.VALUE_SMART_PAGES))
        layout.addWidget( self.checkSmartPages, row, 1 )
        self.checkSmartPages.stateChanged.connect(self.action_smart_pages )
        return row+1

    def formatLayout(self , layout:QGridLayout, row:int)->int:
        pageLayout = self.settings.getValue(DbKeys.SETTING_PAGE_LAYOUT )
        self.btnOnePage = QRadioButton()
        self.btnOnePage.setText(u"1 page")
        self.btnOnePage.setObjectName(DbKeys.VALUE_PAGES_SINGLE)
        self.btnTwoPage = QRadioButton()
        self.btnTwoPage.setText(u"2 pages, side-by-side")
        self.btnTwoPage.setObjectName(DbKeys.VALUE_PAGES_SIDE_2)
        self.btnTwoPage.setText(u"2 pages, stacked")
        self.btnTwoPage.setObjectName(DbKeys.VALUE_PAGES_STACK_2)
        self.btnTwoPage.setText(u"3 pages, side-by-side")
        self.btnTwoPage.setObjectName(DbKeys.VALUE_PAGES_SIDE_3)
        self.btnTwoPage.setText(u"3 pages, stacked")
        self.btnTwoPage.setObjectName(DbKeys.VALUE_PAGES_STACK_3)
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

        self.btnBox.buttonClicked.connect( self.action_layout)

    def formatScript(self, layout:QGridLayout, row:int )->int:
        self.txtScriptShell = QLineEdit()
        self.txtScriptShell.setObjectName(DbKeys.SETTING_DEFAULT_SCRIPT )
        self.txtScriptShell.setText( self.settings.getValue( DbKeys.SETTING_DEFAULT_SCRIPT) )
        layout.addWidget( self.txtScriptShell, row,1)
        return row+1
        
    def formatScriptVars(self, layout:QGridLayout, row:int)->int:
        """ create the inputs for the script runner (system shell) and parms to pass to the runner"""
        self.txtScriptVars  = QLineEdit()
        self.txtScriptVars.setObjectName(DbKeys.SETTING_DEFAULT_SCRIPT_VAR )
        self.txtScriptVars.setText(  self.settings.getValue(DbKeys.SETTING_DEFAULT_SCRIPT_VAR)  )
        layout.addWidget( self.txtScriptVars, row, 1)
        lblHintScriptVar = QLabel()
        lblHintScriptVar.setText("Use a semicolon to separate options, e.g. -c;-d;-e")
        layout.addWidget( lblHintScriptVar, row+1,1 )
        return row+2

    def formatData(self ):
        """ Format all the directory inputs: music, database, scripts, etc."""
        #
        row = self.formatDirectory(   self.layoutFile, 0 )
        row = self.formatDatabaseDir( self.layoutFile, row )
        row = self.formatRecentFiles( self.layoutFile, row )
        row = self.formatEditor(      self.layoutFile, row )
        #
        row = self.formatFiletype( self.layoutBook, 0 )
        row = self.formatLayout(self.layoutBook, row  )
        row = self.formatReopenLastBook( self.layoutBook,row )
        row = self.formatAspectRatio(self.layoutBook, row )
        row = self.formatSmartPages( self.layoutBook, row )
        #
        row = self.formatScript(self.layoutShellScript, 0 )
        row = self.formatScriptVars(self.layoutShellScript, row )
        row = self.formatFileDevice( self.layoutShellScript, row )
        row = self.formatResolution( self.layoutShellScript, row )
        row = self.formatNameImport( self.layoutShellScript, row )
        row = self.formatUserScriptDir( self.layoutShellScript, row )
        #
        self.formatKeyMods( self.layoutKeyboard, 0  )

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
        self.buttons.clicked.connect(self.action_main_button_clicked)


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
    
    def action_help(self):
        helpLayout = QVBoxLayout()
        helpDlg = QDialog()
        helpDlg.setMinimumHeight(500)

        def action_help_close(self):
            helpDlg.reject()

        helpPdf = QTextEdit()
        helpPdf.setText(self._helpPdfCmd)
        helpPdf.setReadOnly(True)
        helpPdf.setMinimumWidth(500)
        
        helpLayout.addWidget( helpPdf)
        btnPdf = QPushButton("Close")
        helpLayout.addWidget( btnPdf)
        btnPdf.clicked.connect( action_help_close )
        
        helpDlg.setLayout( helpLayout )
        helpDlg.exec()
      
    def action_change_sheetmusic_dir(self):
        cdir = self.lblSheetmusicDir.text()
        new_directory_name = QFileDialog.getExistingDirectory(
            self,
            "Change Sheetmusic Directory",
            dir=cdir,
            options=QFileDialog.Option.ShowDirsOnly)
        if new_directory_name:
            self.lblSheetmusicDir.setText( new_directory_name )
            self.lblSheetmusicDir.show()
            self.flagChanged = True
            self.states[ DbKeys.SETTING_DEFAULT_PATH_MUSIC ] = new_directory_name
        self.btn_change_sheetmusic_dir.setDown( False)

    def action_change_user_script_dir(self):
        cdir = self.label_user_script_dir.text()
        new_directory_name = QFileDialog.getExistingDirectory(
            self,
            "Change User Script Directory",
            dir=cdir,
            options=QFileDialog.Option.ShowDirsOnly)
        if new_directory_name:
            self.label_user_script_dir.setText( new_directory_name )
            self.label_user_script_dir.show()
            self.flagChanged = True
            self.states[ DbKeys.SETTING_PATH_USER_SCRIPT ] = new_directory_name
        self.btnChangeUserScriptDir.setDown( False)

    def action_change_database_dir(self):
        cdir = self.lbl_database_dir.text()
        new_directory_name = QFileDialog.getExistingDirectory(
            self,
            "Change Database Directory",
            dir=cdir,
            options=QFileDialog.Option.ShowDirsOnly)
        if new_directory_name:
            self.lbl_database_dir.setText( new_directory_name )
            self.lbl_database_dir.show()
            self.flagChanged = True
            self.states[ DbKeys.SETTING_DEFAULT_PATH_MUSIC_DB ] = new_directory_name
        self.btn_change_database_dir.setDown( False)

    def action_reset_sheetmusic_dir(self):
        cdir = expanduser(  DbKeys.VALUE_DEFAULT_DIR)
        self.lblSheetmusicDir.setText( cdir )
        self.states[DbKeys.SETTING_DEFAULT_PATH_MUSIC] = cdir
        self.flagChanged = True

    def action_reset_database_dir(self):
        cdir = DbKeys.VALUE_DEFAULT_DIR
        self.lbl_database_dir.setText( cdir )
        self.states[DbKeys.SETTING_DEFAULT_PATH_MUSIC_DB] = cdir
        self.flagChanged = True

    def action_reset_user_script_dir(self):
        new_directory_name = expanduser( DbKeys.VALUE_DEFAULT_USER_SCRIPT_DIR )
        self.label_user_script_dir.setText( new_directory_name )
        self.flagChanged = True
        self.states[ DbKeys.SETTING_PATH_USER_SCRIPT ] = new_directory_name


    def action_editor_changed(self, value ):
        self.states[ DbKeys.SETTING_PAGE_EDITOR ] = self.cmbEditor.currentText()
        self.states[ DbKeys.SETTING_PAGE_EDITOR_SCRIPT ] = self.cmbEditor.currentData()
        print("Changed!")
        self.flagChanged = True

    def action_type_changed(self, value):
        self.states[ DbKeys.SETTING_FILE_TYPE ] = self.cmbType.currentData()
        self.flagChanged = True
        self.formatFileDevice( self.layoutShellScript, 3 )

    def action_res_changed(self, value):
        newVal = self.cmbRes.currentData()
        if newVal is not None:
            self.states[ DbKeys.SETTING_FILE_RES ] = self.cmbRes.currentData() 
            self.flagChanged = True
        #self.formatFileDevice( self.layoutShellScript, 3 )

    def action_device_changed( self, value ):
        self.states[ DbKeys.SETTING_DEFAULT_GSDEVICE] = self.cmbDevice.currentData()
        self.flagChanged = True

    def action_name_import( self, value ):
        self.states[self.cmbNameImport.objectName() ] = value
        self.flagChanged = True

    def action_recent_files( self, value ):
        self.states[ self.cmbRecentFiles.objectName() ] = value
        self.flagChanged = True

    def action_reopen_last_book(self, status):
        '''Save the state of the 'ReopenLastBook checkbox '''

        self.states[ DbKeys.SETTING_LAST_BOOK_REOPEN ] = self.checkReopen.isChecked()
        self.flagChanged = True

    def action_aspect_ratio( self, status ):
        self.states[ DbKeys.SETTING_KEEP_ASPECT ] = self.checkAspect.isChecked()
        self.flagChanged = True

    def action_smart_pages( self, status ):
        self.states[ DbKeys.SETTING_SMART_PAGES ]= self.checkSmartPages.isChecked()
        self.flagChanged = True
    
    def action_layout(self, buttonObject ):
        self.flagChanged = True
        self.states[ DbKeys.SETTING_PAGE_LAYOUT ] = buttonObject.objectName() 

    def action_main_button_clicked(self, btn):
        if btn.text() == "Save" and self.flagChanged:
            self.accept()
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
