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

from musicutils import toInt


class Bookmark:
    """Class that holds data for each bookmark

    This is a non-dictionary class that acts more of a container. It should contain
    only relevant, usefull data
    """
    __slots__ = ['section', 'name', 'index',
                 'page', 'pagestr', 'endpage', 'found',
                 'end']

    def __init__(self, section="", name="page", index=-1, page="", endpage=0,  found=False, isEndOfList=True):
        self.setSection(section)
        self.setName(name)
        self.setPage(page)
        self.setIndex(index)
        self.setFound(found)
        self.setEndPage(endpage)
        self.setEndOfList(isEndOfList)

    def setSection(self, section) -> None:
        if section is None:
            self.section = section
        else:
            self.section = section.strip()

    def setName(self, name:str='page') -> None:
        if name is None:
            self.name = 'page'
        else:
            self.name = name.strip()

    def setIndex(self, index) -> None:
        self.index = toInt(index)

    def setPage(self, page) -> None:
        """set the page number to an int.

        This will accept strings or ints and save in both the integer and string
        variables
        """
        self.page = toInt(page)
        self.pagestr = str(self.page)

    def setEndPage(self, page) -> None:
        self.endpage = toInt(page)

    def setFound(self, isFound: bool = True) -> None:
        self.found = isFound

    def setEndOfList(self, isEndOfList: bool) -> None:
        self.end = isEndOfList

    def isFound(self) -> bool:
        return self.found

    def isEndOfList(self) -> bool:
        return self.end

    def __str__(self) -> str:
        return "[{}]: Name: '{}' Index: {:d} Page: {} End: {:d}, Found: {}".format(
            self.section, self.name, self.index, self.pagestr, self.endpage, self.found)
