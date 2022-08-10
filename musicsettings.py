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

import os
from os.path import expanduser
from musicutils import toBool
from ui.main import UiMain

from PySide6.QtCore import QByteArray, QSettings, QSysInfo
from PySide6.QtGui import QKeySequence

app_version = "0.5.0"
ForceResetSettings = False

class MSet():
    """
    Class contains all of the settings for labels. They are split into
    'group' and 'key'. Static functions have been defined that will 
    help in forming the joined group/key values 
    """
    VALUE_DEFAULT_DIR  = "~/sheetmusic"
    VALUE_PAGES_SINGLE = "1page"
    VALUE_PAGES_DOUBLE = "2pages"
    VALUE_FILETYPE     = 'png'
    VALUE_DEFAULT_REOPEN= True
    VALUE_GSDEVICE     =  'png16m'

    VALUE_DEFAULT_SCRIPT       = '/bin/bash'
    VALUE_DEFAULT_SCRIPT_VAR   = '-c' 
    VALUE_SPLIT_SCRIPT_VAR     = ';'              ## Split script variables with this char
    VALUE_DEFAULT_ASPECT       = 'true'

    SETTING_GROUP_DEFAULT      = 'setting'
    SETTING_DEFAULT_PATH       = 'directoryPath'  ## property can be changed by user
    SETTING_DEFAULT_TYPE       = 'fileType'       ## property can be changed by user
    SETTING_DEFAULT_GSDEVICE   = 'gsdevice'
    SETTING_DEFAULT_LAYOUT     = 'layout'         ## property can be changed by user
    SETTING_DEFAULT_OPEN_LAST  = 'reopen'    
    SETTING_DEFAULT_SCRIPT     = 'script'         ## What we will run for conversion
    SETTING_DEFAULT_SCRIPT_VAR = 'scriptvar'      ## What 'extra' variables we will run
    SETTING_DEFAULT_ASPECT     = 'aspectRatio'    ## Keep aspect ratio when resizing

    SETTING_GROUP_LASTFILE     = 'lastfile'
    SETTING_LAST_PAGE          = 'pageNumber'       ## TODO: Move to config
    SETTING_LAST_BOOK          = 'directoryPath'    ## Last file opened.
    
    SETTING_GROUP_WINDOW       = 'mainWindow'      ## SECTION for these settings:
    SETTING_WIN_GEOMETRY       = 'geometry'
    SETTING_WIN_STATE          = 'state'
    SETTING_WIN_POS            = 'position'
    SETTING_WIN_SIZE           = 'size'
    SETTING_WIN_ISMAX          = 'ismaximized'
    SETTING_WIN_STATUS_ENABLED = 'statusbar'

    SETTING_GROUP_KEYS          = 'keys'
    SETTING_PAGE_PREVIOUS       = 'previousPage'
    SETTING_PAGE_NEXT           = 'nextPage'
    SETTING_FIRST_PAGE_SHOWN    = 'pageShownFirst'
    SETTING_LAST_PAGE_SHOWN     = 'pageShownLast'
    SETTING_BOOKMARK_PREVIOUS   = 'previousBookmark'
    SETTING_BOOKMARK_NEXT       = 'nextBookmark'

    def byWindow( keyname:str) -> str:
        return MSet.SETTING_GROUP_WINDOW + "/" + keyname
    
    def byDefault( keyname:str)->str:
        return MSet.SETTING_GROUP_DEFAULT + "/" + keyname

    def byFile( keyname: str )->str:
        return MSet.SETTING_GROUP_LASTFILE + "/" + keyname

    def byKey( keyname: str )->str:
        return MSet.SETTING_GROUP_KEYS + "/" + keyname 

    def scriptVarSplit( script_vars:str , *extras):
        x= script_vars.split( MSet.VALUE_SPLIT_SCRIPT_VAR )
        for i in range(0,len(x) ):
            x[i] = x[i].strip()
        for extra in extras :
            x.append(extra)
        return x


    def defaultSettings():
        """ Return the initial, default settings"""
        return {
            'lastfile/pageNumber'   : '',
            'lastfile/directoryPath': '',
            'setting/directoryPath' : MSet.VALUE_DEFAULT_DIR,
            'setting/fileType'      : MSet.VALUE_FILETYPE,
            'setting/layout'        : MSet.VALUE_PAGES_SINGLE,
            'setting/reopen'        : MSet.VALUE_DEFAULT_REOPEN,
            'setting/gsdevice'      : MSet.VALUE_GSDEVICE,
            'setting/script'        : MSet.VALUE_DEFAULT_SCRIPT,
            'setting/scriptvar'     : MSet.VALUE_DEFAULT_SCRIPT_VAR,
            'window/windowGeometry' : QByteArray()
}
## end class MSet


class MusicSettings(QSettings):

    DEFAULT_ORG = 'OrganMonkey project'
    DEFAULT_APP = 'SheetMusic'
    TEST_APP    = 'SheetMusic_Test'

    def __init__(self, org=DEFAULT_ORG, app=DEFAULT_APP, reset=False):
        super().__init__(org, app)
        if ForceResetSettings or reset:
            self.clear()
        defaultSettings = MSet.defaultSettings()
        for key in defaultSettings:
            if not self.contains(key):
                value = defaultSettings[key]
                if 'directory' in key and value:
                    value = os.path.expanduser(value)
                self.setValue(key, value)
        self.sync()

    def deleteSettings(self):
        self.clear()
        fpath = self.fileName()
        if QSysInfo.productType() != 'windows':
            os.rmdir( fpath )

    def saveMainWindow(self, win):
        '''
        Save window attributes as settings.
        Called when window moved, resized, or closed.
        '''
        self.beginGroup(MSet.SETTING_GROUP_WINDOW)
        self.setValue(
            MSet.SETTING_WIN_GEOMETRY, win.saveGeometry())
        self.setValue(
            MSet.SETTING_WIN_STATE, win.saveState())
        self.setValue(
            MSet.SETTING_WIN_ISMAX, win.isMaximized())
        if not win.isMaximized() == True:
            self.setValue(MSet.SETTING_WIN_POS, win.pos())
            self.setValue(MSet.SETTING_WIN_SIZE, win.size())
        self.endGroup()

    def restoreMainWindow(self, win):
        '''
        Read window attributes from settings,
        using current attributes as defaults (if settings not exist.)

        Called at QMainWindow initialization, before show().
        '''

        self.beginGroup(MSet.SETTING_GROUP_WINDOW)
        isWindowMaximized = toBool(
            self.value(MSet.SETTING_WIN_ISMAX, win.isMaximized()))
        # No need for toPoint, etc. : PySide converts types
        win.restoreGeometry(self.value(
            MSet.SETTING_WIN_GEOMETRY, win.saveGeometry()))
        win.restoreState(self.value(
            MSet.SETTING_WIN_STATE, win.saveState()))
        win.move(self.value(MSet.SETTING_WIN_POS, win.pos()))
        win.resize(self.value(
            MSet.SETTING_WIN_SIZE, win.size()))
        if isWindowMaximized:
            win.showMaximized()

        self.endGroup()
    
    def restoreShortcuts( self, win:UiMain ):
        self.beginGroup( MSet.SETTING_GROUP_KEYS )
        previous_page = self.value(MSet.SETTING_PAGE_PREVIOUS )
        next_page = self.value(MSet.SETTING_PAGE_NEXT )
        previous_bookmark = self.value(MSet.SETTING_BOOKMARK_PREVIOUS)
        next_bookmark = self.value(MSet.SETTING_BOOKMARK_NEXT)
        first_page = self.value(MSet.SETTING_FIRST_PAGE_SHOWN)
        last_page = self.value(MSet.SETTING_LAST_PAGE_SHOWN )
        self.endGroup()

        if previous_page:
            win.actionUp.setShortcut( QKeySequence.fromString(previous_page ) )
        if next_page:
            win.actionDown.setShortcut( QKeySequence.fromString(next_page ))
        if previous_bookmark:
            win.actionPreviousBookmark.setShortcut( QKeySequence.fromString(previous_bookmark))
        if next_bookmark:
            win.actionNextBookmark.setShortcut( QKeySequence.fromString(next_bookmark))
        if first_page:
            win.actionFirstPage.setShortcut( QKeySequence.fromString(first_page ))
        if last_page:
            win.actionLastPage.setShortcut( QKeySequence.fromString(last_page ))
        