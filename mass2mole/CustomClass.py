version="0.0.1"

date = '2022-1-17'

dpi = 64
# coding:utf-8

from ImportDependence import *


# from TableViewer import TableViewer
from cycler import cycler

# Create cycler object. Use any styling from above you please
monochrome = (cycler('color', ['k']) * cycler('linestyle', ['-', '--', ':', '=.']) * cycler('marker', ['^',',', '.']))


class GrowingTextEdit(QtWidgets.QTextEdit):

    def __init__(self, *args, **kwargs):
        super(GrowingTextEdit, self).__init__(*args, **kwargs)
        self.document().contentsChanged.connect(self.sizeChange)

        self.heightMin = 0
        self.heightMax = 8

    def sizeChange(self):
        docHeight = self.document().size().height()
        if self.heightMin <= docHeight <= self.heightMax:
            self.setMinimumHeight(docHeight)

class PandasModel(QtCore.QAbstractTableModel):
    _df = pd.DataFrame()
    _changed = False

    def __init__(self, df=pd.DataFrame(), parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self._df = df
        self._changed = False

        self._filters = {}
        self._sortBy = []
        self._sortDirection = []

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if orientation == QtCore.Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError,):
                return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return self._df.index.tolist()[section]
            except (IndexError,):
                return QtCore.QVariant()

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            try:
                row = index.row()
                col = index.column()
                name = self._struct[col]['name']
                return self._data[row][name]
            except:
                pass
        elif role == QtCore.Qt.CheckStateRole:
            return None

        return QtCore.QVariant(str(self._df.iloc[index.row(), index.column()]))

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    '''
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        row = index.row()
        col = index.column()
        name = self._struct[col]['name']
        self._data[row][name] = value
        self.emit(QtCore.SIGNAL('dataChanged()'))
        return True
    '''

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        if hasattr(value, 'toPyObject'):
            # PyQt4 gets a QVariant
            value = value.toPyObject()
        else:
            # PySide gets an unicode
            dtype = self._df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        # self._df.set_value(row, col, value)
        self._df.at[row, col] = value
        self._changed = True
        # self.emit(QtCore.SIGNAL('dataChanged()'))
        return True

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]

        index = self._df.index.tolist()
        self.layoutAboutToBeChanged.emit()

        # self._df.sort_values(colname, ascending=order == QtCore.Qt.AscendingOrder, inplace=True)
        # self._df.reset_index(inplace=True, drop=True)

        try:
            self._df.sort_values(colname, ascending=order == QtCore.Qt.AscendingOrder, inplace=True)
        except:
            pass
        try:
            self._df.reset_index(inplace=True, drop=True)
        except:
            pass

        self.layoutChanged.emit()

class CustomQTableView(QtWidgets.QTableView):
    df = pd.DataFrame()

    def __init__(self, *args):
        super().__init__(*args)

        self.resize(800, 600)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers |
                             QtWidgets.QAbstractItemView.DoubleClicked)

    def keyPressEvent(self, event):  # Reimplement the event here
        return

class TableViewer(QMainWindow):
    addon = 'Name Author DataType Label Marker Color Size Alpha Style Width TOTAL total LOI loi'

    raw = pd.DataFrame()
    result = pd.DataFrame()
    Para = pd.DataFrame()
    _df = pd.DataFrame()
    data_to_test = pd.DataFrame()
    data_to_test_location = ''
    begin_result = pd.DataFrame()
    load_result = pd.DataFrame()

    def __init__(self, parent=None, df=pd.DataFrame(), title='Statistical Result'):
        QMainWindow.__init__(self, parent)
        self.setAcceptDrops(True)
        self.setWindowTitle(title)
        self.df = df
        self.create_main_frame()
        self.create_status_bar()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [(u.toLocalFile()) for u in event.mimeData().urls()]
        for f in files:
            print(f)

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def resizeEvent(self, evt=None):

        w = self.width()
        h = self.height()
        '''
        if h<=360:
            h=360
            self.resize(w,h)
        if w<=640:
            w = 640
            self.resize(w, h)
        '''

        step = (w * 94 / 100) / 5
        foot = h * 3 / 48

    def ErrorEvent(self, text=''):

        _translate = QtCore.QCoreApplication.translate

        if (text == ''):
            reply = QMessageBox.information(self, _translate('MainWindow', 'Warning'), _translate('MainWindow',
                                                                                                  'Your Data mismatch this Function.\n Some Items missing?\n Or maybe there are blanks in items names?\n Or there are nonnumerical value？'))
        else:
            reply = QMessageBox.information(self, _translate('MainWindow', 'Warning'), _translate('MainWindow',
                                                                                                  'Your Data mismatch this Function.\n Error infor is:') + text)

    def create_main_frame(self):

        self.resize(800, 600)
        self.main_frame = QWidget()

        self.save_button = QPushButton('&Save')
        self.save_button.clicked.connect(self.saveDataFile)

        self.tableView = CustomQTableView(self.main_frame)
        self.tableView.setObjectName('tableView')
        self.tableView.setSortingEnabled(True)

        self.vbox = QVBoxLayout()

        self.vbox.addWidget(self.tableView)
        self.hbox = QHBoxLayout()

        for w in [self.save_button, ]:
            self.hbox.addWidget(w)

        self.vbox.addLayout(self.hbox)

        self.main_frame.setLayout(self.vbox)
        self.setCentralWidget(self.main_frame)

        self.model = PandasModel(self.df)
        self.tableView.setModel(self.model)

    def create_status_bar(self):
        self.status_text = QLabel("Click Save button to save.")
        self.statusBar().addWidget(self.status_text, 1)

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def saveDataFile(self):

        # if self.model._changed == True:
        # print('changed')
        # print(self.model._df)

        DataFileOutput, ok2 = QFileDialog.getSaveFileName(self,
                                                          '文件保存',
                                                          'C:/',
                                                          'Excel Files (*.xlsx);;CSV Files (*.csv)')  # 数据文件保存输出

        if "Label" in self.model._df.columns.values.tolist():
            self.model._df = self.model._df.set_index('Label')

        if (DataFileOutput != ''):

            if ('csv' in DataFileOutput):
                self.model._df.to_csv(DataFileOutput, sep=',', encoding='utf-8')

            elif ('xls' in DataFileOutput):
                self.model._df.to_excel(DataFileOutput, encoding='utf-8')

    def create_action(self, text, slot=None, shortcut=None,
                      icon=None, tip=None, checkable=False,
                      signal='triggered()'):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(':/%s.png' % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action



LocationOfMySelf = os.path.dirname(__file__)

# print(LocationOfMySelf,'Custom Bass Classes')