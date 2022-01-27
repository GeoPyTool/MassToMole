#!/usr/bin/python3
# coding:utf-8
import sys, os

print(sys.path)

LocationOfMySelf = os.path.dirname(__file__)
sys.path.append(LocationOfMySelf)
# print(LocationOfMySelf,' init')

from ImportDependence import *
from CustomClass import *

sign = '''
@author: cycleuser
# Create Date: 2022-01-27
# Modify Date: 2022-01-27
A tool to calculate from mass percetange to mole percentage.
# prerequisite:
#   based on Python 3.x
#   need pandas,chempy,pyqt5
    Any issues or improvements please contact cycleuser@cycleuser.org
    or Open An Issue at GitHub:https://github.com/cycleuser/MassToMole/issues
'''

t = 'You are using MassToMole ' + version + ', released on' + date + '\n' + sign
_translate = QtCore.QCoreApplication.translate

from CustomClass import TableViewer


# Create a custom "QProxyStyle" to enlarge the QMenu icons
# -----------------------------------------------------------
class MyProxyStyle(QProxyStyle):
    pass

    def pixelMetric(self, QStyle_PixelMetric, option=None, widget=None):

        if QStyle_PixelMetric == QStyle.PM_SmallIconSize:
            return 24
        else:
            return QProxyStyle.pixelMetric(self, QStyle_PixelMetric, option, widget)


class Ui_MainWindow(QtWidgets.QMainWindow):
    raw = pd.DataFrame(index=[], columns=[])  # raw is initialized as a blank DataFrame
    Standard = {}  # Standard is initialized as a blank Dict
    Language = ''
    app = QtWidgets.QApplication(sys.argv)
    myStyle = MyProxyStyle('Fusion')  # The proxy style should be based on an existing style,
    # like 'Windows', 'Motif', 'Plastique', 'Fusion', ...
    app.setStyle(myStyle)
    trans = QtCore.QTranslator()
    talk = ''
    targetversion = '0'
    DataLocation = ''
    ChemResult = pd.DataFrame()
    AutoResult = pd.DataFrame()
    TotalResult = []

    def __init__(self):

        super(Ui_MainWindow, self).__init__()
        self.setObjectName('MainWindow')
        self.resize(800, 600)

        self.setAcceptDrops(True)

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate('MainWindow', u'MassToMole'))
        self.setWindowIcon(QIcon(LocationOfMySelf + '/png'))
        self.talk = _translate('MainWindow', 'You are using MassToMole ') + version + '\n' + _translate('MainWindow',
                                                                                                       'released on ') + date

        self.model = PandasModel(self.raw)

        self.main_widget = QWidget(self)

        self.tableView = CustomQTableView(self.main_widget)
        self.tableView.setObjectName('tableView')
        self.tableView.setSortingEnabled(True)

        self.vbox = QVBoxLayout()

        self.vbox.addWidget(self.tableView)

        self.main_widget.setLayout(self.vbox)
        self.setCentralWidget(self.main_widget)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 22))
        self.menubar.setNativeMenuBar(False)
        self.menubar.setObjectName('menubar')

        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName('menuFile')

        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName('menuHelp')

        self.menuLanguage = QtWidgets.QMenu(self.menubar)
        self.menuLanguage.setObjectName('menuLanguage')

        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName('statusbar')
        self.setStatusBar(self.statusbar)

        self.actionOpen = QtWidgets.QAction(QIcon(LocationOfMySelf + '/open.png'), u'Open', self)
        self.actionOpen.setObjectName('actionOpen')
        self.actionOpen.setShortcut('Ctrl+O')

        self.actionClose = QtWidgets.QAction(QIcon(LocationOfMySelf + '/close.png'), u'Close', self)
        self.actionClose.setObjectName('actionClose')
        self.actionClose.setShortcut('Ctrl+N')

        self.actionMagic = QtWidgets.QAction(QIcon(LocationOfMySelf + '/Magic.png'), u'Set', self)
        self.actionMagic.setObjectName('actionMagic')
        self.actionMagic.setShortcut('Ctrl+M')

        self.actionSave = QtWidgets.QAction(QIcon(LocationOfMySelf + '/save.png'), u'Save', self)
        self.actionSave.setObjectName('actionSave')
        self.actionSave.setShortcut('Ctrl+S')

        self.actionQuit = QtWidgets.QAction(QIcon(LocationOfMySelf + '/quit.png'), u'Quit', self)
        self.actionQuit.setObjectName('actionQuit')
        self.actionQuit.setShortcut('Ctrl+Q')

        self.actionWeb = QtWidgets.QAction(QIcon(LocationOfMySelf + '/forum.png'), u'English Forum', self)
        self.actionWeb.setObjectName('actionWeb')

        self.actionGoGithub = QtWidgets.QAction(QIcon(LocationOfMySelf + '/github.png'), u'GitHub', self)
        self.actionGoGithub.setObjectName('actionGoGithub')

        self.actionVersionCheck = QtWidgets.QAction(QIcon(LocationOfMySelf + '/update.png'), u'Version', self)
        self.actionVersionCheck.setObjectName('actionVersionCheck')

        self.actionCnS = QtWidgets.QAction(QIcon(LocationOfMySelf + '/cns.png'), u'Simplified Chinese', self)
        self.actionCnS.setObjectName('actionCnS')

        self.actionCnT = QtWidgets.QAction(QIcon(LocationOfMySelf + '/cnt.png'), u'Traditional Chinese', self)
        self.actionCnT.setObjectName('actionCnT')

        self.actionEn = QtWidgets.QAction(QIcon(LocationOfMySelf + '/en.png'), u'English', self)
        self.actionEn.setObjectName('actionEn')

        self.actionLoadLanguage = QtWidgets.QAction(QIcon(LocationOfMySelf + '/lang.png'), u'Load Language', self)
        self.actionLoadLanguage.setObjectName('actionLoadLanguage')

        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionClose)
        self.menuFile.addAction(self.actionMagic)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionQuit)


        self.menuHelp.addAction(self.actionWeb)
        self.menuHelp.addAction(self.actionGoGithub)
        self.menuHelp.addAction(self.actionVersionCheck)

        self.menuLanguage.addAction(self.actionCnS)
        self.menuLanguage.addAction(self.actionCnT)
        self.menuLanguage.addAction(self.actionEn)
        self.menuLanguage.addAction(self.actionLoadLanguage)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addSeparator()

        
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menubar.addSeparator()

        
        self.menubar.addAction(self.menuLanguage.menuAction())
        self.menubar.addSeparator()

        

        self.actionOpen.triggered.connect(self.getDataFile)
        self.actionClose.triggered.connect(self.clearDataFile)
        self.actionMagic.triggered.connect(self.Magic)
        self.actionSave.triggered.connect(self.saveDataFile)
        self.actionQuit.triggered.connect(QApplication.quit)

        self.actionWeb.triggered.connect(self.goDiscussion)
        self.actionGoGithub.triggered.connect(self.goGitHub)
        self.actionVersionCheck.triggered.connect(self.checkVersion)

        self.actionCnS.triggered.connect(self.to_ChineseS)
        self.actionCnT.triggered.connect(self.to_ChineseT)
        self.actionEn.triggered.connect(self.to_English)
        self.actionLoadLanguage.triggered.connect(self.to_LoadLanguage)

        self.ReadConfig()
        self.trans.load(LocationOfMySelf + '/' + self.Language)
        self.app.installTranslator(self.trans)
        self.retranslateUi()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.talk = _translate('MainWindow', 'You are using MassToMole ') + version + '\n' + _translate('MainWindow',
                                                                                                       'released on ') + date + '\n'

        self.menuFile.setTitle(_translate('MainWindow', u'Data File'))
        self.menuHelp.setTitle(_translate('MainWindow', u'Help'))
        self.menuLanguage.setTitle(_translate('MainWindow', u'Language'))
        self.actionOpen.setText(_translate('MainWindow', u'Open Data'))
        self.actionClose.setText(_translate('MainWindow', u'Close Data'))
        self.actionMagic.setText(_translate('MainWindow', u'Calculate'))
        self.actionSave.setText(_translate('MainWindow', u'Save Data'))
        self.actionQuit.setText(_translate('MainWindow', u'Quit App'))

        self.actionVersionCheck.setText(_translate('MainWindow', u'Check Update'))
        self.actionWeb.setText(_translate('MainWindow', u'English Forum'))
        self.actionGoGithub.setText(_translate('MainWindow', u'Github'))

        self.actionCnS.setText(u'简体中文')
        self.actionCnT.setText(u'繁體中文')
        self.actionEn.setText(u'English')
        self.actionLoadLanguage.setText(_translate('MainWindow', u'Load Language'))

    def goGitHub(self):
        webbrowser.open('https://github.com/cycleuser/MassToMole/')

    def goDiscussion(self):
        webbrowser.open('https://github.com/cycleuser/MassToMole/discussions')

    def checkVersion(self):

        # reply = QMessageBox.information(self, 'Version', self.talk)

        _translate = QtCore.QCoreApplication.translate

        url = 'https://github.com/cycleuser/MassToMole/-/raw/main/mass2mole/CustomClass.py'

        r = 0
        try:
            r = requests.get(url, allow_redirects=True)
            r.raise_for_status()
            NewVersion = 'self.target' + r.text.splitlines()[0]

        except requests.exceptions.ConnectionError as err:
            print(err)
            r = 0
            buttonReply = QMessageBox.information(self, _translate('MainWindow', u'NetWork Error'),
                                                  _translate('MainWindow',
                                                             'You are using MassToMole ') + version + '\n' + 'Net work unavailable.')
            NewVersion = "targetversion = '0'"

        except requests.exceptions.HTTPError as err:
            print(err)
            r = 0
            buttonReply = QMessageBox.information(self, _translate('MainWindow', u'NetWork Error'),
                                                  _translate('MainWindow',
                                                             'You are using MassToMole ') + version + '\n' + 'Net work unavailable.')
            NewVersion = "targetversion = '0'"

        exec(NewVersion)
        print('web is', self.targetversion)
        print(NewVersion)

        self.talk = _translate('MainWindow', 'Version Online is ') + self.targetversion + '\n' + _translate(
            'MainWindow', 'You are using MassToMole ') + version + '\n' + _translate('MainWindow',
                                                                                    'released on ') + date + '\n'

        if r != 0:

            print('now is', version)
            if (version < self.targetversion):

                buttonReply = QMessageBox.question(self, _translate('MainWindow', u'Version'),
                                                   self.talk + _translate('MainWindow',
                                                                          'New version available.\n Download and update?'),
                                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if buttonReply == QMessageBox.Yes:
                    print('Yes clicked.')
                    # QApplication.quit
                    # pip.main(['install', 'MassToMole', '--upgrade --no-cache-dir'])

                    # self.UpDate

                    webbrowser.open('https://github.com/chinageology/MassToMole/blob/master/Download.md')
                else:
                    print('No clicked.')
            else:
                buttonReply = QMessageBox.information(self, _translate('MainWindow', u'Version'),
                                                      self.talk + _translate('MainWindow',
                                                                             'This is the latest version.'))

    def ReadConfig(self):
        if (os.path.isfile('config.ini')):

            try:
                with open('config.ini', 'rt') as f:
                    try:
                        data = f.read()
                    except:
                        data = 'Language = \'en\''
                        pass

                    print(data)
                    try:
                        print("self." + data)
                        exec("self." + data)
                    except:
                        pass
                    print(self.Language)


            except():
                pass

    def WriteConfig(self, text=LocationOfMySelf + '/en'):
        try:
            with open('config.ini', 'wt') as f:
                f.write(text)
        except():
            pass

    def to_ChineseS(self):

        self.trans.load(LocationOfMySelf + '/cns')
        self.app.installTranslator(self.trans)
        self.retranslateUi()

        self.WriteConfig('Language = \'cns\'')

    def to_ChineseT(self):

        self.trans.load(LocationOfMySelf + '/cnt')
        self.app.installTranslator(self.trans)
        self.retranslateUi()

        self.WriteConfig('Language = \'cnt\'')

    def to_English(self):

        self.trans.load(LocationOfMySelf + '/en')
        self.app.installTranslator(self.trans)
        self.retranslateUi()
        self.WriteConfig('Language = \'en\'')

    def to_LoadLanguage(self):

        _translate = QtCore.QCoreApplication.translate
        fileName, filetype = QFileDialog.getOpenFileName(self, _translate('MainWindow', u'Choose Language File'),
                                                         '~/',
                                                         'Language Files (*.qm)')  # 设置文件扩展名过滤,注意用双分号间隔

        print(fileName)

        self.trans.load(fileName)
        self.app.installTranslator(self.trans)
        self.retranslateUi()

    def ErrorEvent(self, text=''):

        if (text == ''):
            reply = QMessageBox.information(self, _translate('MainWindow', 'Warning'), _translate('MainWindow',
                                                                                                  'Your Data mismatch this Function.\n Some Items missing?\n Or maybe there are blanks in items names?\n Or there are nonnumerical value？'))
        else:
            reply = QMessageBox.information(self, _translate('MainWindow', 'Warning'), _translate('MainWindow',
                                                                                                  'Your Data mismatch this Function.\n Error infor is:') + text)

    def clearDataFile(self):
        self.raw = pd.DataFrame()
        self.model = PandasModel(self.raw)
        self.tableView.setModel(self.model)

    def getDataFile(self, CleanOrNot=True):
        _translate = QtCore.QCoreApplication.translate

        DataFileInput, filetype = QFileDialog.getOpenFileName(self, _translate('MainWindow', u'Choose Data File'),
                                                              '~/',
                                                              'CSV Files (*.csv);;Excel Files (*.xlsx);;Excel 2003 Files (*.xls)')  # 设置文件扩展名过滤,注意用双分号间隔
        # #print(DataFileInput,filetype)

        self.DataLocation = DataFileInput
        print(self.DataLocation)

        if ('csv' in DataFileInput):
            self.raw = pd.read_csv(DataFileInput, engine='python')
        elif ('xls' in DataFileInput):
            self.raw = pd.read_excel(DataFileInput,engine='openpyxl')
        # #print(self.raw)

        if len(self.raw) > 0:
            self.model = PandasModel(self.raw)
            # print(self.model._df)

            self.tableView.setModel(self.model)
            self.model = PandasModel(self.raw)
            # print(self.model._df)

            flag = 0
            ItemsAvalibale = self.model._df.columns.values.tolist()
            ItemsToTest = ['Label', 'Marker', 'Color', 'Size', 'Alpha', 'Style', 'Width']
            for i in ItemsToTest:
                if i not in ItemsAvalibale:
                    # print(i)
                    flag = flag + 1

            if flag == 0:
                pass
                # reply = QMessageBox.information(self, _translate('MainWindow', 'Ready'), _translate('MainWindow', 'Everything fine and no need to set up.'))

            else:
                pass
                # self.SetUpDataFile()

    def getFileName(self, list=['C:/Users/Fred/Documents/GitHub/Writing/元素数据/Ag.xlsx']):
        result = []
        for i in list:
            result.append(i.split("/")[-1].split(".")[0])
        return (result)

    def saveDataFile(self):

        # if self.model._changed == True:
        # print('changed')
        # #print(self.model._df)

        DataFileOutput, ok2 = QFileDialog.getSaveFileName(self, _translate('MainWindow', u'Save Data File'),
                                                          'C:/',
                                                          'CSV Files (*.csv);;Excel Files (*.xlsx)')  # 数据文件保存输出

        dftosave = self.model._df

        # self.model._df.reset_index(drop=True)

        if "Label" in dftosave.columns.values.tolist():
            dftosave = dftosave.set_index('Label')

        if (DataFileOutput != ''):

            dftosave.reset_index(drop=True)

            if ('csv' in DataFileOutput):
                dftosave.to_csv(DataFileOutput, sep=',', encoding='utf-8')

            elif ('xls' in DataFileOutput):

                dftosave.to_excel(DataFileOutput, encoding='utf-8')


    def Magic(self):

        if (len(self.model._df) <= 0):
            self.getDataFile()
            pass

        if (len(self.model._df) > 0):
            #self.model._df = self.model._df.fillna(0)

            raw = self.model._df 
            
            raw = raw.set_index('Label') # Label 这一列是用来做样品备注的，就当作索引了
            item_list = raw.columns.tolist()
            type_list = [] # 数据类型，质量分数、ppm、ppb等等
            clean_item_list = [] # 只保留化学式，去掉多余字符
            mass_reciprocal_list = [] # 对应化学式的摩尔质量的倒数，如果不是化学式就为0
            mole_sum_list = [] # 每一个样品的总摩尔数，用来计算各分量摩尔比

            for i in item_list:
                type_tmp = 0.0
                mass_tmp = 0.0
                item_tmp =''
                if 'wt%' in i :
                    type_tmp = 1.0/100
                    item_tmp = i.replace("wt%", "")
                elif 'ppm' in i :
                    type_tmp = 1.0/1000000
                    item_tmp = i.replace("ppm", "")
                elif 'ppb' in i :
                    type_tmp = 1.0/1000000000
                    item_tmp = i.replace("ppb", "")
                else:
                    pass
                
                for k in ['(',')','[',']']:
                    item_tmp = item_tmp.replace(k, "")
                
                try: 
                    mass_tmp = 1.0/(Substance.from_formula(item_tmp).mass)
                except:
                    pass

                mass_reciprocal_list.append(mass_tmp)
                clean_item_list.append(item_tmp)
                type_list.append(type_tmp)

            # print(mass_reciprocal_list,clean_item_list,type_list)

            mole_df = raw * type_list # 将数据从不同尺度质量分数统一化到总和设为1下的质量分数
            mole_df = mole_df * mass_reciprocal_list # 将数据从质量分数换算到摩尔数
            mole_df.columns = clean_item_list # 重新设置各列标签

            mole_sum_list = mole_df.sum(axis = 1).tolist() # 总摩尔数
            def reverse(n): return 1.0/n
            x=list(map(reverse,mole_sum_list))

            # mole_df = mole_df * x # 换算成摩尔分数

            # print(raw,'\n', type_list,'\n',mole_df,'\n',x)

            values_raw = np.matrix(mole_df.values)
            sum_r = np.matrix(x).T
            result = np.multiply( values_raw , sum_r)
            print(np.shape(mole_df),np.shape(result))

            result_df = pd.DataFrame(result)
            result_df.columns = clean_item_list # 重新设置各列标签
            result_df['Label'] = raw.index.tolist() # 添加 Label 这一列
            result_df = result_df.set_index('Label') # Label 这一列是用来做样品备注的，就当作索引了

            self.model._df = result_df 
            self.model = PandasModel(self.model._df)
            self.tableView.setModel(self.model)
            reply = QMessageBox.information(self, _translate('MainWindow', 'Ready'),
                                            _translate('MainWindow', 'Mole/% has been calculated.'))

def main():
    import sys

    app = QtWidgets.QApplication(sys.argv)
    trans = QtCore.QTranslator()
    # trans.load('cn')  # 没有后缀.qm
    app.installTranslator(trans)
    mainWin = Ui_MainWindow()
    mainWin.retranslateUi()
    mainWin.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
