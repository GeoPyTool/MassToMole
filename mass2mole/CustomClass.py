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

    Minerals = ['Quartz',
                'Zircon',
                'K2SiO3',
                'Anorthite',
                'Na2SiO3',
                'Acmite',
                'Diopside',
                'Sphene',
                'Hypersthene',
                'Albite',
                'Orthoclase',
                'Wollastonite',
                'Olivine',
                'Perovskite',
                'Nepheline',
                'Leucite',
                'Larnite',
                'Kalsilite',
                'Apatite',
                'Halite',
                'Fluorite',
                'Anhydrite',
                'Thenardite',
                'Pyrite',
                'Magnesiochromite',
                'Chromite',
                'Ilmenite',
                'Calcite',
                'Na2CO3',
                'Corundum',
                'Rutile',
                'Magnetite',
                'Hematite',
                'Q',
                'A',
                'P',
                'F', ]

    Calced = ['Fe3+/(Total Fe) in rock',
              'Mg/(Mg+Total Fe) in rock',
              'Mg/(Mg+Fe2+) in rock',
              'Mg/(Mg+Fe2+) in silicates',
              'Ca/(Ca+Na) in rock',
              'Plagioclase An content',
              'Differentiation Index']
    DataWeight = {}
    DataVolume = {}
    DataBase = {}
    DataCalced = {}
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

        self.pie_button = QPushButton('&Pie')
        self.pie_button.clicked.connect(self.MyPie)

        self.bar_button = QPushButton('&Bar')
        self.bar_button.clicked.connect(self.MyBar)

        self.tableView = CustomQTableView(self.main_frame)
        self.tableView.setObjectName('tableView')
        self.tableView.setSortingEnabled(True)

        self.vbox = QVBoxLayout()

        self.vbox.addWidget(self.tableView)
        self.hbox = QHBoxLayout()

        for w in [self.save_button, self.pie_button, self.bar_button]:
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


    def MyPie(self):
        try:
            self.MyPiepop = Pie(df=self.df)
            self.MyPiepop.Magic()
            self.MyPiepop.show()
        except Exception as e:
            self.ErrorEvent(text=repr(e))

    def MyBar(self):
        try:
            self.MyBarpop = Bar(df=self.df)
            self.MyBarpop.Magic()
            self.MyBarpop.show()
        except Exception as e:
            self.ErrorEvent(text=repr(e))

class AppForm(QMainWindow):
    cmap_trained_data= ListedColormap(['#FFAAAA', '#AAFFAA', '#AAAAFF'])

    model = LinearDiscriminantAnalysis()
    color_list=[]
    result = pd.DataFrame()
    Para = pd.DataFrame()
    _df = pd.DataFrame()
    _df_back = pd.DataFrame()
    data_to_test = pd.DataFrame()
    data_to_test_location = ''
    begin_result = pd.DataFrame()
    load_result = pd.DataFrame()

    kernel_list = ['linear', 'rbf', 'sigmoid', 'poly']
    clf = svm.SVC(C=1.0, kernel='linear', probability=True)
    _changed = False

    xlabel = r'$SiO_2 wt\%$'
    ylabel = r'$Na_2O + K_2O wt\%$'
    reference = 'Print the reference here.'
    ItemNames = ['Foidolite',
                 'Peridotgabbro',
                 'Foid Gabbro',
                 'Foid Monzodiorite',
                 'Foid Monzosyenite',
                 'Foid Syenite',
                 'Gabbro Bs',
                 'Gabbro Ba',
                 'Monzogabbro',
                 'Monzodiorite',
                 'Monzonite',
                 'Syenite',
                 'Quartz Monzonite',
                 'Gabbroic Diorite',
                 'Diorite',
                 'Granodiorite',
                 'Granite',
                 'Quartzolite',
                 ]

    LocationAreas = [ [[41, 3], [37, 3], [35, 9], [37, 14], [52.5, 18], [52.5, 14], [48.4, 11.5], [45, 9.4], [41, 7]],
                     [[41, 0], [41, 3], [45, 3], [45, 0]],
                     [[41, 3], [41, 7], [45, 9.4], [49.4, 7.3], [45, 5], [45, 3]],
                     [[45, 9.4], [48.4, 11.5], [53, 9.3], [49.4, 7.3]],
                     [[48.4, 11.5], [52.5, 14], [57.6, 11.7], [53, 9.3]],
                     [[52.5, 14], [52.5, 18], [57, 18], [63, 16.2], [61, 13.5], [57.6, 11.7]],
                     [[45, 0], [45, 2], [52, 5], [52, 0]],
                     [[45, 2], [45, 5], [52, 5]],
                     [[45, 5], [49.4, 7.3], [52, 5]],
                     [[49.4, 7.3], [53, 9.3], [57, 5.9], [52, 5]],
                     [[53, 9.3], [57.6, 11.7], [61, 8.6], [63, 7], [57, 5.9]],
                     [[57.6, 11.7], [61, 13.5], [63, 16.2], [71.8, 13.5], [61, 8.6]],
                     [[61, 8.6], [71.8, 13.5], [69, 8], [63, 7]],
                     [[52, 0], [52, 5], [57, 5.9], [57, 0]],
                     [[57, 0], [57, 5.9], [63, 7], [63, 0]],
                     [[63, 0], [63, 7], [69, 8], [77.3, 0]],
                     [[77.3, 0], [69, 8], [71.8, 13.5], [85.9, 6.8], [87.5, 4.7]],
                     [[77.3, 0], [87.5, 4.7], [90, 4.7], [90, 0]],
                     ]

    AreasHeadClosed = []
    SelectDic = {}
    AllLabel = []
    IndexList = []
    LabelList = []
    TypeList = []
    Standard = ''
    FileName_Hint = ''
    WholeResult = {}
    OutPutCheck = True
    OutPutTitle = 'Blank Title'
    OutPutData = pd.DataFrame()
    OutPutFig = Figure((8.0, 8.0))
    itemstocheck = ['SiO2', 'K2O', 'Na2O']
    title = 'TAS (total alkali–silica) diagram Volcanic/Intrusive (Wilson et al. 1989)'

    def __init__(self, parent=None, df=pd.DataFrame()):
        QWidget.__init__(self, parent)
        self.setWindowTitle(self.title)


        self.FileName_Hint = ''
        self._df = df
        self._df_back = df
        if (len(df) > 0):
            self._changed = True
            # print('DataFrame recieved to AppForm')

        self.AllLabel = []

        for i in range(len(self._df)):
            tmp_label = self._df.at[i, 'Label']
            if tmp_label not in self.AllLabel:
                self.AllLabel.append(tmp_label)

        for i in range(len(self.LocationAreas)):
            tmpi = self.LocationAreas[i] + [self.LocationAreas[i][0]]
            tmppath = path.Path(tmpi)
            self.AreasHeadClosed.append(tmpi)
            patch = patches.PathPatch(tmppath, facecolor='orange', lw=0.3, alpha=0.3)
            self.SelectDic[self.ItemNames[i]] = tmppath

        self.create_main_frame()
        self.create_status_bar()





    def CleanDataFile(self, raw=pd.DataFrame(),
                      checklist=['质量', '分数', '百分比', ' ', 'ppm', 'ma', 'wt', '%', '(', ')', '（', '）', '[', ']', '【',
                                 '】']):

        for i in checklist:
            raw = raw.rename(columns=lambda x: x.replace(i, ''))


        for i in raw.dtypes.index:
            if raw.dtypes[i] != float and raw.dtypes[i] != int and i not in ['Marker', 'Color', 'Size', 'Alpha',
                                                                             'Style', 'Width', 'Label'] and i not in self.itemstocheck:
                print(raw.dtypes[i], i, 'droped')
                raw = raw.drop(i, 1)

        for i in raw.columns.values.tolist():
            if i == '':
                raw = raw.drop(i, 1)

        raw = raw.dropna(axis=1, how='all')

        # Columns = raw.columns.values.tolist()
        # Rows = raw.index.values.tolist()

        for i in raw.index.values.tolist():
            if type(raw.at[i, 'Label']) == str:
                if 'tandard' in raw.at[i, 'Label']:
                    print('Your Self Defined Standard is at the line No.', i)
                    self.Standard = raw.loc[i]
                    raw = raw.drop(i)

        raw = raw.reset_index(drop=True)

        return (raw)
        print(raw.columns.values.tolist())

    def Check(self):

        row = self._df.index.tolist()
        col = self._df.columns.tolist()
        itemstocheck = self.itemstocheck
        checklist = list((set(itemstocheck).union(set(col))) ^ (set(itemstocheck) ^ set(col)))
        if len(checklist) == len(itemstocheck):
            self.OutPutCheck = True
        else:
            self.OutPutCheck = False
        return (self.OutPutCheck)

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

    def OldErrorEvent(self):
        _translate = QtCore.QCoreApplication.translate
        reply = QMessageBox.information(self, _translate('MainWindow', 'Warning'), _translate('MainWindow',
                                                                                              'Your Data mismatch this Function.\n Some Items missing?\n Or maybe there are blanks in items names?\n Or there are nonnumerical value？'))

    def ErrorEvent(self, text=''):

        _translate = QtCore.QCoreApplication.translate

        if (text == ''):
            reply = QMessageBox.information(self, _translate('MainWindow', 'Warning'), _translate('MainWindow',
                                                                                                  'Your Data mismatch this Function.\n Some Items missing?\n Or maybe there are blanks in items names?\n Or there are nonnumerical value？'))
        else:
            reply = QMessageBox.information(self, _translate('MainWindow', 'Warning'), _translate('MainWindow',
                                                                                                  'Your Data mismatch this Function.\n Error infor is:') + text)

    def DrawLine(self, l=[(41, 0), (41, 3), (45, 3)], color='grey', linewidth=0.5, linestyle='-', linelabel='',
                 alpha=0.5):
        x = []
        y = []
        for i in l:
            x.append(i[0])
            y.append(i[1])

        self.axes.plot(x, y, color=color, linewidth=linewidth, linestyle=linestyle, label=linelabel, alpha=alpha)
        return (x, y)

    def DrawLogLine(self, l=[(41, 0), (41, 3), (45, 3)], color='grey', linewidth=0.5, linestyle='-', linelabel='',
                    alpha=0.5):
        x = []
        y = []
        for i in l:
            x.append(math.log(i[0], 10))
            y.append(math.log(i[1], 10))

        self.axes.plot(x, y, color=color, linewidth=linewidth, linestyle=linestyle, label=linelabel, alpha=alpha)
        return (x, y)

    def save_plot(self):
        file_choices = 'pdf Files (*.pdf);;SVG Files (*.svg);;PNG Files (*.png)'

        path = QFileDialog.getSaveFileName(self,
                                           'Save file', '',
                                           file_choices)
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)

    def save_plot_quitely(self, path='~/', name='Target'):
        self.canvas.print_figure(path + name + '.pdf', dpi=self.dpi)
        self.canvas.print_figure(path + name + '.png', dpi=self.dpi)

    def stateval(self, data=np.ndarray):
        # print(type(data),data)
        dict = {'min': min(data), 'max': max(data), 'median': nanmedian(data), 'mean': nanmean(data), 'ptp': ptp(data),
                'var': nanvar(data), 'std': nanstd(data), 'cv': nanmean(data) / nanstd(data)}

        return (dict)

    def create_main_frame(self):
        self.main_frame = QWidget()
        self.dpi = 128
        self.fig = Figure((8.0, 8.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        self.axes = self.fig.add_subplot(111)
        # Create the navigation toolbar, tied to the canvas
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        # Other GUI controls
        self.save_button = QPushButton('&Save')
        self.save_button.clicked.connect(self.saveImgFile)

        self.draw_button = QPushButton('&Reset')
        self.draw_button.clicked.connect(self.TAS)

        self.legend_cb = QCheckBox('&Legend')
        self.legend_cb.setChecked(True)
        self.legend_cb.stateChanged.connect(self.TAS)  # int

        self.tag_cb = QCheckBox('&Tag')
        self.tag_cb.setChecked(True)
        self.tag_cb.stateChanged.connect(self.TAS)  # int

        self.more_cb = QCheckBox('&More')
        self.more_cb.setChecked(True)
        self.more_cb.stateChanged.connect(self.TAS)  # int

        self.detail_cb = QCheckBox('&Detail')
        self.detail_cb.setChecked(True)
        self.detail_cb.stateChanged.connect(self.TAS)  # int

        slider_label = QLabel('Location:')
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 5)
        self.slider.setValue(1)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.valueChanged.connect(self.TAS)  # int

        #
        # Layout with box sizers
        #
        self.hbox = QHBoxLayout()

        for w in [self.save_button, self.draw_button, self.detail_cb, self.tag_cb, self.more_cb,
                  self.legend_cb, slider_label, self.slider]:
            self.hbox.addWidget(w)
            self.hbox.setAlignment(w, Qt.AlignVCenter)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.mpl_toolbar)
        self.vbox.addWidget(self.canvas)
        self.vbox.addLayout(self.hbox)
        self.textbox = GrowingTextEdit(self)
        self.textbox.setText(self.reference)

        self.vbox.addWidget(self.textbox)
        self.main_frame.setLayout(self.vbox)
        self.setCentralWidget(self.main_frame)

    def create_status_bar(self):
        self.status_text = QLabel("Click Save button to save.")
        self.statusBar().addWidget(self.status_text, 1)

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def exportScene(self):
        ImgFileOutput, ok2 = QFileDialog.getSaveFileName(self,
                                                         '文件保存',
                                                         'C:/',
                                                         'PNG Files (*.png)')  # 设置文件扩展名过滤,注意用双分号间隔

        pix = QtWidgets.QWidget.grab(self.canvas)
        # pix.save("./capture.png", "PNG")
        pix.save(ImgFileOutput)

    def OLDsaveImgFile(self):
        ImgFileOutput, ok2 = QFileDialog.getSaveFileName(self,
                                                         '文件保存',
                                                         'C:/',
                                                         'pdf Files (*.pdf);;SVG Files (*.svg);;PNG Files (*.png)')  # 设置文件扩展名过滤,注意用双分号间隔

        if (ImgFileOutput != ''):
            self.canvas.print_figure(ImgFileOutput, dpi=300)
            # self.canvas.print_raw(ImgFileOutput, dpi=300)

    def saveImgFile(self):
        ImgFileOutput, ok2 = QFileDialog.getSaveFileName(self,
                                                         '文件保存',
                                                         'C:/' + self.FileName_Hint,
                                                         'pdf Files (*.pdf);;SVG Files (*.svg);;PNG Files (*.png)')  # 设置文件扩展名过滤,注意用双分号间隔

        if (ImgFileOutput != ''):
            self.canvas.print_figure(ImgFileOutput, dpi=300)
            # self.canvas.print_raw(ImgFileOutput, dpi=300)

    def getDataFiles(self, limit=6):
        print('get Multiple Data Files  called \n')
        DataFilesInput, filetype = QFileDialog.getOpenFileNames(self, u'Choose Data File',
                                                                '~/',
                                                                'CSV Files (*.csv);;Excel Files (*.xlsx);;Excel 2003 Files (*.xls)')  # 设置文件扩展名过滤,注意用双分号间隔
        # print(DataFileInput,filetype)

        DataFramesList = []

        if len(DataFilesInput) >= 1:
            for i in range(len(DataFilesInput)):
                if i < limit:
                    if ('csv' in DataFilesInput[i]):
                        DataFramesList.append(pd.read_csv(DataFilesInput[i]),engine='python')
                    elif ('xls' in DataFilesInput[i]):
                        DataFramesList.append(pd.read_excel(DataFilesInput[i]),engine='openpyxl')
                else:
                    # self.ErrorEvent(text='You can only open up to 6 Data Files at a time.')
                    pass

        return (DataFramesList, DataFilesInput)

    def getDataFile(self, CleanOrNot=True):
        _translate = QtCore.QCoreApplication.translate

        DataFileInput, filetype = QFileDialog.getOpenFileName(self, _translate('MainWindow', u'Choose Data File'),
                                                              '~/',
                                                              'CSV Files (*.csv);;Excel Files (*.xlsx);;Excel 2003 Files (*.xls)')  # 设置文件扩展名过滤,注意用双分号间隔
        print(DataFileInput)

        raw_input_data = pd.DataFrame()



        if ('csv' in DataFileInput):
            raw_input_data = pd.read_csv(DataFileInput, engine='python')
        elif ('xls' in DataFileInput):
            raw_input_data = pd.read_excel(DataFileInput,engine='openpyxl')

        if len(raw_input_data) > 0:
            return (raw_input_data, DataFileInput)
        else:
            return ('Blank')

    def getFileName(self, list=['C:/Users/Fred/Documents/GitHub/Writing/元素数据/Ag.xlsx']):
        result = []
        for i in list:
            result.append(i.split("/")[-1].split(".")[0])
        print(result)
        return (result)

    def Key_Func(self):
        pass

    def loadDataToTest(self):
        TMP = self.getDataFile()
        if TMP != 'Blank':
            self.data_to_test = TMP[0]
            self.data_to_test_location = TMP[1]
        self.Key_Func()

    def saveDataFile(self):

        # if self.model._changed == True:
        # print('changed')
        # print(self.model._df)

        DataFileOutput, ok2 = QFileDialog.getSaveFileName(self,
                                                          '文件保存',
                                                          'C:/' + self.FileName_Hint,
                                                          'Excel Files (*.xlsx);;CSV Files (*.csv)')  # 数据文件保存输出

        if "Label" in self.model._df.columns.values.tolist():
            self.model._df = self.model._df.set_index('Label')

        if (DataFileOutput != ''):

            if ('csv' in DataFileOutput):
                self.model._df.to_csv(DataFileOutput, sep=',', encoding='utf-8')

            elif ('xls' in DataFileOutput):
                self.model._df.to_excel(DataFileOutput, encoding='utf-8')

    def saveResult(self):

        self.result.reset_index
        DataFileOutput, ok2 = QFileDialog.getSaveFileName(self,
                                                          '文件保存',
                                                          'C:/',
                                                          'Excel Files (*.xlsx);;CSV Files (*.csv)')  # 数据文件保存输出

        if (DataFileOutput != ''):

            if ('csv' in DataFileOutput):

                # DataFileOutput = DataFileOutput[0:-4]

                self.result.to_csv(DataFileOutput, sep=',', encoding='utf-8')
                # self.result.to_csv(DataFileOutput + '.csv', sep=',', encoding='utf-8')

            elif ('xlsx' in DataFileOutput):

                # DataFileOutput = DataFileOutput[0:-5]

                self.result.to_excel(DataFileOutput, encoding='utf-8')

                # self.result.to_excel(DataFileOutput + '.xlsx', encoding='utf-8')

    def savePara(self):

        self.Para.reset_index
        DataFileOutput, ok2 = QFileDialog.getSaveFileName(self,
                                                          '文件保存',
                                                          'C:/',
                                                          'Excel Files (*.xlsx);;CSV Files (*.csv)')  # 数据文件保存输出

        if (DataFileOutput != ''):

            if ('csv' in DataFileOutput):

                # DataFileOutput = DataFileOutput[0:-4]

                self.Para.to_csv(DataFileOutput, sep=',', encoding='utf-8')
                # self.Para.to_csv(DataFileOutput + '.csv', sep=',', encoding='utf-8')

            elif ('xlsx' in DataFileOutput):

                # DataFileOutput = DataFileOutput[0:-5]

                self.Para.to_excel(DataFileOutput, encoding='utf-8')

                # self.Para.to_excel(DataFileOutput + '.xlsx', encoding='utf-8')

    def showResult(self):

        self.result.reset_index

        self.resultpop = TableViewer(df=self.result, title='Results')
        self.resultpop.show()

    def showPara(self):

        self.Para.reset_index

        self.parapop = TableViewer(df=self.Para, title='Parameters')
        self.parapop.show()

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

    def GetResult(self):
        self.WholeResult = {'Check': True, 'Title': self.OutPutTitle, 'Data': self.OutPutData, 'Fig': self.OutPutFig}
        return (self.WholeResult)

    def DropUseless(self, df=pd.DataFrame(), droplist=['Q (Mole)', 'A (Mole)', 'P (Mole)', 'F (Mole)',
                                                       'Q (Mass)', 'A (Mass)', 'P (Mass)', 'F (Mass)']):
        for t in droplist:
            if t in df.columns.values:
                df = df.drop(t, 1)
        return (df)

    def ReduceSize(self, df=pd.DataFrame):

        m = ['Number', 'Tag', 'Index', 'Name', 'Author', 'DataType', 'Marker', 'Color', 'Size', 'Alpha',
                       'Style', 'Width']

        for i in m:
            if i in df.columns.values:
                df = df.drop(i, 1)
        df = df.loc[:, (df != 0).any(axis=0)]
        return (df)

    def Slim(self, df=pd.DataFrame()):

        ItemsAvalibale = df.columns.values.tolist()
        if 'Label' in ItemsAvalibale:
            df = df.set_index('Label')

        df = df.dropna(axis=1, how='all')

        ItemsToTest = ['Number', 'Tag','Type', 'Index', 'Name', 'Author', 'DataType', 'Marker', 'Color', 'Size', 'Alpha',
                       'Style', 'Width']

        for i in ItemsToTest:
            if i in ItemsAvalibale:
                df = df.drop(i, 1)

        df = df.apply(pd.to_numeric, errors='coerce')
        # df = df.dropna(axis='columns')
        df = df.dropna(axis='rows')

        return (df)

    def relation(self, data1=np.ndarray, data2=np.ndarray):
        data = array([data1, data2])
        dict = {'cov': cov(data, bias=1), 'corrcoef': corrcoef(data)}
        return (dict)

    def Hsim_Distance(self, a=[1, 2], b=[5, 6, 7, 8]):
        tmp = []
        result = 0
        for i in range(min(len(a), len(b))):
            tmp.append(1.0 / (1 + np.abs(a[i] - b[i])))

        # print(tmp)
        result = np.sum(tmp) / (min([len(a), len(b)]))
        return (result)

    def Close_Distance(self, a=[1, 2, 3, 4], b=[5, 6, 7, 8]):
        tmp = []
        result = 0
        for i in range(min([len(a), len(b)])):
            tmp.append(np.power(np.e, -np.abs(a[i] - b[i])))

        # print(tmp)
        result = np.sum(tmp) / (min([len(a), len(b)]))
        return (result)

    def runMLP(self):

        try:
            n = len(self.trained_result)

            # n 是PCA后得到的训练集的样本数
            # 用训练集中样本的维度作为输入层神经元个数
            # 用训练集中样本的类别标签数作为输出层神经元个数
            # m 是根据上面参考文献得到的经验公式，作为隐藏神经元层数

            m = int((4 * n ** 2 + 3) / (n ** 2 - 8))
            input_size = len(self.trained_result.T)
            output_size = len(set(self.result_to_fit.index))
            alpha = 2  # 2-10

            # if (2<=m<=10):
            #     alpha = m  # 2-10
            # else:
            #     alpha = 5
            # n_h 是得到的隐藏层的每一层神经元个数
            n_h = int(n / (alpha * (input_size + output_size)))

            hidden_layer_tuple = (n_h,) * m

            self.MLP = MLPClassifier(solver='lbfgs', alpha=1e-5,
                                     hidden_layer_sizes=hidden_layer_tuple,
                                     random_state=1)

            try:
                self.MLP.fit(self.trained_result, self.result_to_fit.index)
                self.coefs_ = self.MLP.coefs_
                self.intercepts_ = self.MLP.intercepts_
                self.MLP_params = self.MLP.get_params(deep=True)

            except Exception as e:
                self.ErrorEvent(text=repr(e))

            Z = self.MLP.predict(self.trained_data_to_test)

            Z2 = self.MLP.predict_proba(self.trained_data_to_test)
            proba_df = pd.DataFrame(Z2)
            proba_df.columns = self.MLP.classes_

            proba_list = []
            for i in range(len(proba_df)):
                proba_list.append(round(max(proba_df.iloc[i]) + 0.001, 2))
            predict_result = pd.concat(
                [self.data_to_test['Label'], pd.DataFrame({'Classification': Z}),
                 pd.DataFrame({'Confidence probability': proba_list})],
                axis=1)
            # print(predict_result)

            self.predictpop = TableViewer(df=predict_result,
                                          title=self.description + ' MLP Predict Result')
            self.predictpop.show()
        except Exception as e:
            self.ErrorEvent(text=repr(e))

class PlotModel(FigureCanvas):
    _df = pd.DataFrame()
    _changed = False

    def __init__(self, parent=None, width=100, height=100, dpi=100, description=''
                 , tag='', xlabel=r'$X$', ylabel=r'$Y$', xlim=(30, 90), ylim=(0, 20)):

        self.fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = self.fig.add_subplot(111, xlabel=xlabel + '\n' + description, ylabel=ylabel, xlim=xlim, ylim=ylim)

        FigureCanvas.__init__(self, self.fig)

        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def DrawLine(self, l=[(41, 0), (41, 3), (45, 3)], color='grey', linewidth=0.5, linestyle='-', linelabel='',
                 alpha=0.5):
        x = []
        y = []
        for i in l:
            x.append(i[0])
            y.append(i[1])

        self.axes.plot(x, y, color=color, linewidth=linewidth, linestyle=linestyle, label=linelabel, alpha=alpha)
        return (x, y)

    def TAS(self, df=pd.DataFrame(), Left=35, Right=79, X0=30, X1=90, X_Gap=7, Base=0,
            Top=19, Y0=1, Y1=19, Y_Gap=19, FontSize=12, xLabel=r'$SiO_2 wt\%$', yLabel=r'$na_2O + K_2O wt\%$'):

        PointLabels = []
        x = []
        y = []

        self.DrawLine([(41, 0), (41, 3), (45, 3)])
        self.DrawLine([(45, 0), (45, 3), (45, 5), (49.4, 7.3), (53, 9.3), (57.6, 11.7), (61, 13.5), (63, 16.2)], )
        self.DrawLine([(52, 5), (57, 5.9), (63, 7), (69, 8), (71.8, 13.5), (61, 8.6)])
        self.DrawLine([(45, 2), (45, 5), (52, 5), (45, 2)])
        self.DrawLine(
            [(69, 8), (77.3, 0), (87.5, 4.7), (85.9, 6.8), (71.8, 13.5), (63, 16.2), (57, 18), (52.5, 18), (37, 14),
             (35, 9), (37, 3), (41, 3)])

        self.DrawLine([(63, 0), (63, 7), (57.6, 11.7), (52.5, 14), (52.5, 18)])
        self.DrawLine([(57, 0), (57, 5.9), (53, 9.3), (48.4, 11.5)])
        self.DrawLine([(52, 0), (52, 5), (49.4, 7.3), (45, 9.4)])
        self.DrawLine([(41, 3), (41, 7), (45, 9.4)])

        self.DrawLine([(45, 9.4), (48.4, 11.5), (52.5, 14)])
        self.DrawLine([(41.75, 1), (52.5, 5)])
        # self.DrawLine([(45.85, 2.75), (46.85, 3.0), (50.0, 4.0), (53.1, 5.0), (55.0, 5.8), (55.6, 6.0), (60.0, 6.8),(61.5, 7.0), (65.0, 7.35), (70.0, 7.85), (71.6, 8.0), (75.0, 8.3), (76.4, 8.4)])
        # self.DrawLine([(39.8, 0.35), (65.6, 9.7)])
        # self.DrawLine([(39.2, 0.0), (40.0, 0.4), (43.2, 2.0), (45.0, 2.8), (48.0, 4.0), (50.0, 4.75), (53.7, 6.0),(55.0, 6.4), (60.0, 8.0), (65.0, 8.8)])
        Labels = [u'F', u'Pc', u'U1', u'Ba', u'Bs', u'S1', u'U2', u'O1', u'S2', u'U3', u'O2', u'S3', u'Ph', u'O3', u'T',
                  u'Td', u'R', u'Q', u'S/N/L']
        Locations = [(39, 10), (43, 1.5), (44, 6), (47.5, 3.5), (49.5, 1.5), (49, 6), (49, 9.5), (54, 3), (53, 7),
                     (53, 12),
                     (60, 4),
                     (57, 8.5), (57, 14), (67, 5), (65, 12), (67, 9), (75, 9), (85, 1), (55, 18.5)]
        description = 'TAS (total alkali–silica) diagram (after Wilson et al. 1989).\nF Foidite, Ph Phonolite, Pc Pocrobasalt,\nU1 Tephrite (ol < 10%) Basanite(ol > 10%), U2 Phonotephrite, U3 Tephriphonolite,\nBa alkalic basalt,Bs subalkalic baslt, S1 Trachybasalt, S2 Basaltic Trachyandesite, S3 Trachyandesite,\nO1 Basaltic Andesite, O2 Andesite, O3 Dacite,  \nT Trachyte , Td Trachydacite , R Rhyolite, Q Silexite \n S/N/L Sodalitite/Nephelinolith/Leucitolith'
        tag = 'tas-Wilson1989-volcano'

        if (len(df) > 0):

            for i in range(len(df)):
                TmpLabel = ''
                if (df.at[i, 'Label'] in PointLabels or df.at[i, 'Label'] == ''):
                    TmpLabel = ''
                else:
                    PointLabels.append(df.at[i, 'Label'])
                    TmpLabel = df.at[i, 'Label']

                x.append(df.at[i, 'SiO2'])
                y.append(df.at[i, 'Na2O'] + df.at[i, 'K2O'])
                Size = df.at[i, 'Size']
                Color = df.at[i, 'Color']

                # print(Color, df.at[i, 'SiO2'], (df.at[i, 'Na2O'] + df.at[i, 'K2O']))

                Alpha = df.at[i, 'Alpha']
                Marker = df.at[i, 'Marker']
                Label = TmpLabel

                self.axes.scatter(df.at[i, 'SiO2'], (df.at[i, 'Na2O'] + df.at[i, 'K2O']), marker=df.at[i, 'Marker'],
                                  s=df.at[i, 'Size'], color=df.at[i, 'Color'], alpha=df.at[i, 'Alpha'], label=TmpLabel)

            # self.axes.savefig('tas.png', dpi=300, bbox_inches='tight')
            # self.axes.savefig('tas.svg', dpi=300, bbox_inches='tight')
            # self.axes.savefig('tas.pdf', dpi=300, bbox_inches='tight')
            # self.axes.savefig('tas.eps', dpi=300, bbox_inches='tight')
            # self.axes.show()

            self.draw()

    def TASv(self, df=pd.DataFrame(), Left=35, Right=79, X0=30, X1=90, X_Gap=7, Base=0,
             Top=19, Y0=1, Y1=19, Y_Gap=19, FontSize=12, xlabel=r'$SiO_2 wt\%$', ylabel=r'$na_2O + K_2O wt\%$',
             width=12, height=12, dpi=300, xlim=(30, 90), ylim=(0, 20)):

        PointLabels = []
        x = []
        y = []

        Labels = [u'F', u'Pc', u'U1', u'Ba', u'Bs', u'S1', u'U2', u'O1', u'S2', u'U3', u'O2', u'S3', u'Ph', u'O3', u'T',
                  u'Td', u'R', u'Q', u'S/N/L']
        Locations = [(39, 10), (43, 1.5), (44, 6), (47.5, 3.5), (49.5, 1.5), (49, 6), (49, 9.5), (54, 3), (53, 7),
                     (53, 12),
                     (60, 4),
                     (57, 8.5), (57, 14), (67, 5), (65, 12), (67, 9), (75, 9), (85, 1), (55, 18.5)]

        X_offset = -6
        Y_offset = 3

        TagNumber = min(len(Labels), len(Locations))

        for k in range(TagNumber):
            self.axes.annotate(Labels[k], Locations[k], xycoords='data', xytext=(X_offset, Y_offset),
                               textcoords='offset points',
                               fontsize=8, color='grey', alpha=0.8)

        self.DrawLine([(41, 0), (41, 3), (45, 3)])
        self.DrawLine([(45, 0), (45, 3), (45, 5), (49.4, 7.3), (53, 9.3), (57.6, 11.7), (61, 13.5), (63, 16.2)], )
        self.DrawLine([(52, 5), (57, 5.9), (63, 7), (69, 8), (71.8, 13.5), (61, 8.6)])
        self.DrawLine([(45, 2), (45, 5), (52, 5), (45, 2)])
        self.DrawLine(
            [(69, 8), (77.3, 0), (87.5, 4.7), (85.9, 6.8), (71.8, 13.5), (63, 16.2), (57, 18), (52.5, 18), (37, 14),
             (35, 9), (37, 3), (41, 3)])

        self.DrawLine([(63, 0), (63, 7), (57.6, 11.7), (52.5, 14), (52.5, 18)])
        self.DrawLine([(57, 0), (57, 5.9), (53, 9.3), (48.4, 11.5)])
        self.DrawLine([(52, 0), (52, 5), (49.4, 7.3), (45, 9.4)])
        self.DrawLine([(41, 3), (41, 7), (45, 9.4)])

        self.DrawLine([(45, 9.4), (48.4, 11.5), (52.5, 14)])
        # self.DrawLine([(41.75, 1), (52.5, 5)])
        # self.DrawLine([(45.85, 2.75), (46.85, 3.0), (50.0, 4.0), (53.1, 5.0), (55.0, 5.8), (55.6, 6.0), (60.0, 6.8),(61.5, 7.0), (65.0, 7.35), (70.0, 7.85), (71.6, 8.0), (75.0, 8.3), (76.4, 8.4)])
        # self.DrawLine([(39.8, 0.35), (65.6, 9.7)])
        # self.DrawLine([(39.2, 0.0), (40.0, 0.4), (43.2, 2.0), (45.0, 2.8), (48.0, 4.0), (50.0, 4.75), (53.7, 6.0),(55.0, 6.4), (60.0, 8.0), (65.0, 8.8)])
        Labels = [u'F', u'Pc', u'U1', u'Ba', u'Bs', u'S1', u'U2', u'O1', u'S2', u'U3', u'O2', u'S3', u'Ph', u'O3', u'T',
                  u'Td', u'R', u'Q', u'S/N/L']
        Locations = [(39, 10), (43, 1.5), (44, 6), (47.5, 3.5), (49.5, 1.5), (49, 6), (49, 9.5), (54, 3), (53, 7),
                     (53, 12),
                     (60, 4),
                     (57, 8.5), (57, 14), (67, 5), (65, 12), (67, 9), (75, 9), (85, 1), (55, 18.5)]
        description = 'TAS (total alkali–silica) diagram (after Wilson et al. 1989).\nF Foidite, Ph Phonolite, Pc Pocrobasalt,\nU1 Tephrite (ol < 10%) Basanite(ol > 10%), U2 Phonotephrite, U3 Tephriphonolite,\nBa alkalic basalt,Bs subalkalic baslt, S1 Trachybasalt, S2 Basaltic Trachyandesite, S3 Trachyandesite,\nO1 Basaltic Andesite, O2 Andesite, O3 Dacite,  \nT Trachyte , Td Trachydacite , R Rhyolite, Q Silexite \n S/N/L Sodalitite/Nephelinolith/Leucitolith'
        tag = 'tas-Wilson1989-volcano'

        if (len(df) > 0):

            for i in range(len(df)):
                TmpLabel = ''
                if (df.at[i, 'Label'] in PointLabels or df.at[i, 'Label'] == ''):
                    TmpLabel = ''
                else:
                    PointLabels.append(df.at[i, 'Label'])
                    TmpLabel = df.at[i, 'Label']

                x.append(df.at[i, 'SiO2'])
                y.append(df.at[i, 'Na2O'] + df.at[i, 'K2O'])
                Size = df.at[i, 'Size']
                Color = df.at[i, 'Color']

                # print(Color, df.at[i, 'SiO2'], (df.at[i, 'Na2O'] + df.at[i, 'K2O']))

                Alpha = df.at[i, 'Alpha']
                Marker = df.at[i, 'Marker']
                Label = TmpLabel

                self.axes.scatter(df.at[i, 'SiO2'], (df.at[i, 'Na2O'] + df.at[i, 'K2O']), marker=df.at[i, 'Marker'],
                                  s=df.at[i, 'Size'], color=df.at[i, 'Color'], alpha=df.at[i, 'Alpha'], label=TmpLabel,
                                  edgecolors='black')

            xLabel = r'$SiO_2 wt\%$' + '\n' + description
            yLabel = r'$na_2O + K_2O wt\%$'
            # self.axes.xlabel(xLabel, fontsize=12)

            self.draw()

LocationOfMySelf = os.path.dirname(__file__)

# print(LocationOfMySelf,'Custom Bass Classes')