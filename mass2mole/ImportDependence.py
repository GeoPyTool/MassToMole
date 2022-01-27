#coding:utf-8
import webbrowser, sys, os , re, requests, chempy
from chempy import Substance
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QMenu, QSizePolicy, QMessageBox, QWidget, QFileDialog, QAction, QTextEdit, QLineEdit, QApplication, QPushButton, QSlider, QLabel, QHBoxLayout, QVBoxLayout, QProxyStyle, QStyle, qApp, QCheckBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from bs4 import BeautifulSoup

LocationOfMySelf=os.path.dirname(__file__)

#print(LocationOfMySelf, 'Import Denpendence')

_translate = QtCore.QCoreApplication.translate