from PySide6.QtWidgets import (
        QDialog, 
        QDialogButtonBox ,  QPushButton, QLabel,
        QListWidget ,       QListWidgetItem,  QVBoxLayout
    )
from PySide6.QtCore import Qt

class SelectItems( QDialog ):
    def __init__(self, title:str=None, heading:str=None):
        super().__init__()
        self.dataList = {}
        self._ignoreCheckedItems = False
        self.setDialog(
            self.createTitle(title) ,
            self.createList() ,
            self.createButtonBox() )

        if title is not None:
            self.setWindowTitle( title )
        self.setHeading(heading)
        self.resize( 600,500)


    def setDialog( self, *args ):
        self._dialog_layout = QVBoxLayout()
        for element in args:
            self._dialog_layout.addWidget( element )
        self.setLayout( self._dialog_layout )

    def createTitle(self, heading:str=None)->QLabel:
        self.lblHeading =  QLabel()
        self.setHeading( heading )
        return self.lblHeading

    def createList(self)->QListWidget:
        self.checkList = QListWidget()
        self.checkList.itemClicked.connect( self.actionSelected )
        return self.checkList

    def createButtonBox(self)->QDialogButtonBox:
        self.buttonBox = QDialogButtonBox()
        self.btn_yes = QPushButton('Yes')
        self.btn_no  = QPushButton('No')
        self.buttonBox.addButton( self.btn_yes, QDialogButtonBox.AcceptRole )
        self.buttonBox.addButton( self.btn_no , QDialogButtonBox.RejectRole )
        self.buttonBox.accepted.connect( self.actionAccepted )
        self.buttonBox.rejected.connect( self.actionRejected )
        return self.buttonBox

    def setHeading( self, heading:str ):
        if heading:
            self.lblHeading.setText( heading )

    def setButtonText( self, btn_yes:str='Yes', btn_no:str='No' ):
        self.btn_yes.setText( btn_yes)
        self.btn_no.setText( btn_no)

    def _widgetFromDatum( self, label )->QListWidgetItem:
        lim = QListWidgetItem()
        lim.setText(label)
        lim.setFlags( Qt.ItemIsUserCheckable |Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        lim.setCheckState(Qt.Unchecked)
        return lim

    def _fromList(self, data:list ):
        for index, datum in enumerate( data,0 ):
            self.data[index]=datum
            self.checkList.addItem( self._widgetFromDatum( datum))

    def _fromDict( self,dictionary:dict ):
        index = 0
        for key,value in dictionary.items():
            self.data[index]=value
            self.checkList.addItem( self._widgetFromDatum( key))
            index = index+1

    def setData(self, data):
        """
            Fill in the combo box from either a dictionary or a simple list
            Data that is checked will be returned in 'dataList' as both key 
            and data
            Dictionaries are { display_data : return_value }
        """
        self.data = {}
        if isinstance( data , dict ):
            self._fromDict( data )
        else:
            self._fromList( data )

    def _fillInCheckedItems(self, selectionType ):
        dataList= {}
        for i in range(0, self.checkList.count() ):
            item = self.checkList.item(i)
            if item.checkState() == selectionType :
                dataList[ item.text() ] = self.data[i]
        return dataList

    def getDataList( self )->dict:
        dataList= {}
        for i in range(0, self.checkList.count() ):
            dataList[ self.checkList.item(i).text() ] = self.data[i]
        return dataList

    def getCheckedList(self):
        if self._ignoreCheckedItems :
            return {}
        return self._fillInCheckedItems( Qt.Checked )

    def getUncheckedList(self):
        return ( self.getDataList() if self._ignoreCheckedItems else self._fillInCheckedItems( Qt.Unchecked ) )

    def actionAccepted(self):
        self._ignoreCheckedItems = False
        self.accept()

    def actionRejected(self):
        self._ignoreCheckedItems = True
        self.reject()

    def actionSelected(self, item:QListWidgetItem ):
        if item.checkState() == Qt.Checked :
            item.setCheckState( Qt.Unchecked)
        else:
            item.setCheckState( Qt.Checked )
        item.setSelected( False )
