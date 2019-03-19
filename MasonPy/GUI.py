# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 14:01:40 2017

@author: Administrator
"""
import sys
import matplotlib.pyplot as plt
import numpy as np
import importlib.util
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMessageBox, QAction, QMenu, QLineEdit, QComboBox, QDialogButtonBox, QMainWindow, QLabel, QGridLayout, QWidget, QPushButton, QCheckBox, QWidget, QApplication, QInputDialog, QVBoxLayout, QFormLayout, QHBoxLayout, QGraphicsLineItem, QStyleOptionGraphicsItem, QDialog
from PyQt5.QtCore import QSize, Qt, QMimeData, QRect, QPoint, QPointF, QLineF, QLine
from PyQt5.QtGui import QDrag, QPen, QPainter, QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
import random

import CompileList, SetModule, FrameworkDebugger
AllFile = SetModule.getFile()
for i in AllFile:
    exec('from '+ i + ' import*')

leftwidget = QWidget()
leftlayout = QVBoxLayout()
rightwidget = QWidget()
label = QLabel()
linemode = 0
paintarray = []
linearray = []                                          #(startbutton, endbutton, linetype, linename)
linetype = 'true'
linenum = 0
figure = plt.figure()
errormsg = ''

buttonlist = []

class Process_Button(QPushButton):
    global buttonlist
    
    inputline = []
    dragable = 0
    string = 'a'
    next_index = 'null'
    nodenum = 0
    position = QPoint()
    mode = 'process'
    ExtremePoint = 0
    parameter_name = []
    parameter_value = []
    
    def __init__(self, title, parent):
        super().__init__(title, parent)
        
        self.parameter_name = []
        self.parameter_value = []
        if title != 'Start' and title != 'End':
            t = eval(title + '()')
            self.parameter_name = t.AllVariables
            for i in range(len(self.parameter_name)):
                self.parameter_value.append(eval('t.' + self.parameter_name[i]))
            
    def mouseMoveEvent(self, e):

        if e.buttons() != Qt.RightButton:
            return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() + self.rect().topLeft())
        
        dropAction = drag.exec_(Qt.MoveAction)

    def mousePressEvent(self, e):
        global linemode
        global paintarray
        
        if linemode == 1:
            if e.buttons() == Qt.LeftButton:
                paintarray.append(self)
            
            #print(self.position)
        else :
            if e.buttons() == Qt.RightButton:
                for button in buttonlist:
                    if button.dragable == 1:
                        button.dragable = 0
                self.dragable = 1
            else:
                self.showdialog()
            
            QPushButton.mousePressEvent(self, e)
    
    def showdialog(self):
        inputlist, result = ProcessDialog(self.parameter_name, self.parameter_value).getdata(self.parameter_name, self.parameter_value)
        if result == 1:
            self.parameter_value = inputlist
        
class Decision_Button(QPushButton):
    global buttonlist
   
    inputline = []
    dragable = 0
    string = 'b'
    true_index = 'null'
    false_index = 'null'
    nodenum = 0
    position = QPoint()
    mode = 'Decision'
    compare_num = 0.0
    compare_stuff = " "
    compare_symbol = " "
    parameter = []
  
    def __init__(self, title, parent):
        super().__init__(title, parent)
        

    def mouseMoveEvent(self, e):

        if e.buttons() != Qt.RightButton:
            return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() + self.rect().topLeft())

        dropAction = drag.exec_(Qt.MoveAction)
        

    def mousePressEvent(self, e):
        global linemode
        global paintarray
        global linearray
        
        if linemode == 1:
            if e.buttons() == Qt.LeftButton:
                paintarray.append(self)
        else :
            if e.buttons() == Qt.RightButton:
                for button in buttonlist:
                    if button.dragable == 1:
                        button.dragable = 0
                self.dragable = 1
                
            else:
                for i in linearray:
                    if i[1].string == self.string and i[1].nodenum == self.nodenum:
                        if not self.parameter:
                            if hasattr(i[0], 'parameter_name'):
                                self.parameter = i[0].parameter_name
                            else:
                                self.parameter = i[0].parameter
                        else:
                            if hasattr(i[0], 'parameter_name'):
                                self.parameter = list(set(self.parameter) & set(i[0].parameter_name))
                            else:
                                self.parameter = list(set(self.parameter) & set(i[0].parameter))
                
                if not self.parameter:
                    self.errordialog()
                else:
                    self.showdialog()
      
            QPushButton.mousePressEvent(self, e)
    
    def showdialog(self):
        dia = DecisionDialog(self.parameter)
        mod, compare, num, result = dia.getdata(self.parameter)
        if result == 1:
            self.compare_num = float(num)
            self.compare_stuff = mod
            self.compare_symbol = compare
            self.setText(self.compare_stuff + '  '+ self.compare_symbol + ' ' + str(self.compare_num))
            self.string = "Check_" + self.compare_stuff
    
    def errordialog(self):
        dia = QMessageBox.warning(self, "error", "Require a fuction connected ahead.", QMessageBox.Close) 
        
class Loop_Button(QPushButton):
    global buttonlist
    
    inputline = []
    dragable = 0
    string = 'a'
    cont_index = 'null'
    break_index = 'null'
    nodenum = 0
    loop_time = 200
    position = QPoint()
    mode = 'Loop'
    compare_num = None
    compare_stuff = None
    compare_symbol = None
    parameter = []
    
    def __init__(self, title, parent):
        super().__init__(title, parent)

    def mouseMoveEvent(self, e):

        if e.buttons() != Qt.RightButton:
            return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() + self.rect().topLeft())
        
        dropAction = drag.exec_(Qt.MoveAction)

    def mousePressEvent(self, e):
        global linemode
        global paintarray
        
        if linemode == 1:
            if e.buttons() == Qt.LeftButton:
                paintarray.append(self)
        else :
            if e.buttons() == Qt.RightButton:
                for button in buttonlist:
                    if button.dragable == 1:
                        button.dragable = 0
                self.dragable = 1
                
            else:
                pos = e.pos()
 
                topRight = self.rect().topRight()
                bottomRight = self.rect().bottomRight()
     
                hotspotTopLeft = QtCore.QPoint(topRight.x()-25, topRight.y())
     
                hotspotRect = QtCore.QRect(hotspotTopLeft, bottomRight)
                
                if hotspotRect.contains(pos):
                    QtWidgets.QPushButton.mousePressEvent(self, e)
                else:
                    self.blockSignals(True)
                    
                    for i in linearray:
                        if i[1].string == self.string and i[1].nodenum == self.nodenum:
                            if not self.parameter:
                                if hasattr(i[0], 'parameter_name'):
                                    self.parameter = i[0].parameter_name
                                else:
                                    self.parameter = i[0].parameter
                            else:
                                if hasattr(i[0], 'parameter_name'):
                                    self.parameter = list(set(self.parameter) & set(i[0].parameter_name))
                                else:
                                    self.parameter = list(set(self.parameter) & set(i[0].parameter))
                
                    if not self.parameter:
                        self.showdialog()
                    else:
                        self.showdecisiondialog()
                    QtWidgets.QPushButton.mousePressEvent(self, e)
                    self.blockSignals(False)
    
    def showdialog(self):
        temp, result = QInputDialog.getInt(self, 'Loop Time', 'Loop Time:')
        if result == True:
            self.loop_time = temp
            self.setText('Loop ' + str(self.loop_time) + ' times')
    def showdecisiondialog(self):
        dia = loopdialog(self.parameter)
        mod, compare, num, times, result = dia.getdata(self.parameter)
        if result == 1:
            if times.strip() == '':
                if mod != 'Parameter..' and compare != 'Symbal..' and num.strip() != '':
                    try:
                        self.compare_num = float(num.strip())
                        self.compare_stuff = mod
                        self.compare_symbol = compare
                        self.setText(self.compare_stuff + ' '+ self.compare_symbol + ' ' + str(self.compare_num))
                    except ValueError:
                        self.errordialog4()
                else:
                    self.errordialog()
            else:
                if mod != 'Parameter..' and compare != 'Symbal..' and num.strip() != '':
                    try:
                        self.compare_num = float(num.strip())
                        self.compare_stuff = mod
                        self.compare_symbol = compare
                    except ValueError:
                        self.errordialog4()
                        return
                    try:
                        self.loop_time = int(times.strip())
                    except ValueError:
                        self.errordialog3()
                        return
                    self.setText(self.compare_stuff + ' '+ self.compare_symbol + ' ' + str(self.compare_num) + ' or ' + 'Loop ' + str(self.loop_time) + ' times.')
                else:
                    try:
                        self.loop_time = int(times.strip())
                    except ValueError:
                        self.errordialog3()
                        return
                    self.setText('Loop ' + str(self.loop_time) + ' times.')
    def errordialog(self):
        dia = QMessageBox.warning(self, "error", "At least complete one statement.", QMessageBox.Close) 
    def errordialog2(self):
        dia = QMessageBox.warning(self, "error", "Loop times can't less then 0.", QMessageBox.Close)
    def errordialog3(self):
        dia = QMessageBox.warning(self, "error", "Please input int for loop times.", QMessageBox.Close)  
    def errordialog4(self):
        dia = QMessageBox.warning(self, "error", "Please input float for compare value.", QMessageBox.Close)           

class Loop_end(QPushButton):
    global buttonlist
    
    inputline = []
    dragable = 0
    string = 'a'
    next_index = 'null'
    nodenum = 0
    position = QPoint()
    mode = 'Loop_end'
    ExtremePoint = 0
    
    def __init__(self, title, parent):
        super().__init__(title, parent)
        
    def mouseMoveEvent(self, e):

        if e.buttons() != Qt.RightButton:
            return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() + self.rect().topLeft())
        
        dropAction = drag.exec_(Qt.MoveAction)

    def mousePressEvent(self, e):
        global linemode
        global paintarray
        
        if linemode == 1:
            if e.buttons() == Qt.LeftButton:
                paintarray.append(self)
            
            #print(self.position)
        else :
            if e.buttons() == Qt.RightButton:
                for button in buttonlist:
                    if button.dragable == 1:
                        button.dragable = 0
                self.dragable = 1
            
            QPushButton.mousePressEvent(self, e)

class ProcessDialog(QDialog):
    def __init__(self, paremeter_name, parameter_value, parent = None):
        super().__init__()
        
        self.layout = QVBoxLayout(self)
        self.label_layout = QVBoxLayout(self)
        self.edit_layout = QVBoxLayout(self)
        self.upside_layout = QHBoxLayout(self)
        self.input_edit_list = []
        
        for i in range(len(paremeter_name)):
            self.label = QLabel(paremeter_name[i], self)
            self.label_layout.addWidget(self.label)
            self.input = QLineEdit(str(parameter_value[i]), self)
            self.input_edit_list.append(self.input)
            self.edit_layout.addWidget(self.input)
        self.upside_layout.addLayout(self.label_layout)
        self.upside_layout.addLayout(self.edit_layout)
        
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        
        self.layout.addLayout(self.upside_layout)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.label_layout)
       
    def getdata(parent = None, paremeter_name = [], parameter_value = []):
        dialog = ProcessDialog(paremeter_name, parameter_value, parent)
        inputlist = []
        result = dialog.exec_()
        for i in range(len(paremeter_name)):
            inputlist.append(dialog.input_edit_list[i].text())
        return (inputlist, result)
        
class DecisionDialog(QDialog):
    def __init__(self, parameter, parent = None):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.layout2 = QHBoxLayout(self)
        
        self.combo = QComboBox()
        
        for i in range(len(parameter)):
            self.combo.addItem(parameter[i])
        
        self.combo2 = QComboBox()
        self.combo2.addItem(">")
        self.combo2.addItem(">=")
        self.combo2.addItem("=")
        self.combo2.addItem("<=")
        self.combo2.addItem("<")
        
        self.inputnum = QLineEdit()
        
        self.layout2.addWidget(self.combo)
        self.layout2.addWidget(self.combo2)
        self.layout2.addWidget(self.inputnum)
        
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        
        self.layout.addLayout(self.layout2)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def getdata(parent = None, parameter = []):
        dialog = DecisionDialog(parameter, parent)
        result = dialog.exec_()
        mode = dialog.combo.currentText()
        compare = dialog.combo2.currentText()
        num = dialog.inputnum.text()
        return (mode, compare, num, result)

class loopdialog(QDialog):
    def __init__(self, parameter, parent = None):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.decision_layout = QHBoxLayout(self)
        self.times_layout = QHBoxLayout(self)
        
        self.label = QLabel('At least choose one statement:', self)
        self.label2 = QLabel('and/or', self)
        self.combo = QComboBox()
        
        self.combo.addItem("Parameter..")
        for i in range(len(parameter)):
            self.combo.addItem(parameter[i])
        
        self.combo2 = QComboBox()
        self.combo2.addItem("Symbal..")
        self.combo2.addItem(">")
        self.combo2.addItem(">=")
        self.combo2.addItem("=")
        self.combo2.addItem("<=")
        self.combo2.addItem("<")
        
        self.inputnum = QLineEdit()
        self.decision_layout.addWidget(self.combo)
        self.decision_layout.addWidget(self.combo2)
        self.decision_layout.addWidget(self.inputnum)
        
        self.time_label = QLabel('Loop Time:', self)
        self.timeinput = QLineEdit()
        self.times_layout.addWidget(self.time_label)
        self.times_layout.addWidget(self.timeinput)
        
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        
        self.layout.addWidget(self.label)
        self.layout.addLayout(self.decision_layout)
        self.layout.addWidget(self.label2)
        self.layout.addLayout(self.times_layout)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)
    
    def getdata(parent = None, parameter = []):
        dialog = loopdialog(parameter, parent)
        result = dialog.exec_()
        mode = dialog.combo.currentText()
        compare = dialog.combo2.currentText()
        num = dialog.inputnum.text()
        times = dialog.timeinput.text()
        return (mode, compare, num, times, result)    
    
class rightcanvas(QWidget):
    
    def __init__(self):
        super().__init__()
    
        global figure
        global errormsg
        
        button_widget = QWidget()
        layout2 = QtWidgets.QHBoxLayout()
        button_widget.setLayout(layout2)
        wind_check = QCheckBox('Wind_Speed', self)
        wind_check.setCheckState(QtCore.Qt.Checked)
        wind_check.stateChanged.connect(self.wind_show)
        rpm_check = QCheckBox('RPM', self)
        rpm_check.setCheckState(QtCore.Qt.Checked)
        rpm_check.stateChanged.connect(self.rpm_show)
        power_check = QCheckBox('Power', self)
        power_check.setCheckState(QtCore.Qt.Checked)
        power_check.stateChanged.connect(self.power_show)
        
        layout2.addWidget(wind_check)
        layout2.addWidget(rpm_check)
        layout2.addWidget(power_check)
        
        
# =============================================================================
#         self.button1 = QtWidgets.QPushButton('fresh')
#         self.button1.clicked.connect(self.paintEvent)
#         
# =============================================================================
#        self.axes = figure.add_subplot(111)
#        self.axes.hold(False)
        
#        data = [random.random() for i in range(25)]
#        self.axes.plot(data, '*-')
        
        self.canvas = FigureCanvas(figure)
        
        self.errorlabel = QLabel(errormsg)
        
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.canvas, 0 , 0, 10, 1)
        layout.addWidget(button_widget, 10, 0)
        layout.addWidget(self.errorlabel, 12, 0)
        
        self.setLayout(layout)
        
    def paintEvent(self, e):
        self.canvas.draw()
        
    def mouseReleaseEvent(self, e):
        self.repaint()
    def wind_show(self, state):
        #HelloWindow.draw_fig(state == QtCore.Qt.Checked, )
        if state == QtCore.Qt.Checked:
            HelloWindow.isPaintWindSpeed = True
            HelloWindow.draw_fig(HelloWindow.isPaintWindSpeed, HelloWindow.isPaintRPM, HelloWindow.isPaintPower)
            self.canvas.draw()
        else:
            HelloWindow.isPaintWindSpeed = False
            HelloWindow.draw_fig(HelloWindow.isPaintWindSpeed, HelloWindow.isPaintRPM, HelloWindow.isPaintPower)
            self.canvas.draw()
    def rpm_show(self, state):
        if state == QtCore.Qt.Checked:
            HelloWindow.isPaintRPM = True
            HelloWindow.draw_fig(HelloWindow.isPaintWindSpeed, HelloWindow.isPaintRPM, HelloWindow.isPaintPower)
            self.canvas.draw()
        else:
            HelloWindow.isPaintRPM = False
            HelloWindow.draw_fig(HelloWindow.isPaintWindSpeed, HelloWindow.isPaintRPM, HelloWindow.isPaintPower)
            self.canvas.draw()
    def power_show(self, state):
        if state == QtCore.Qt.Checked:
            HelloWindow.isPaintPower = True
            HelloWindow.draw_fig(HelloWindow.isPaintWindSpeed, HelloWindow.isPaintRPM, HelloWindow.isPaintPower)
            self.canvas.draw()
        else:
            HelloWindow.isPaintPower = False
            HelloWindow.draw_fig(HelloWindow.isPaintWindSpeed, HelloWindow.isPaintRPM, HelloWindow.isPaintPower)
            self.canvas.draw()
        
        
class Example(QWidget):
    
    def __init__(self):
        super().__init__()

        self.initUI()
        
        
    def initUI(self):

        self.setAcceptDrops(True)
        
        global buttonlist
        
     #   self.button = Process_Button('Start', self)
      #  self.button.string = 'Start'
       # self.button.next_inda = 'null'
        #self.button.move(100, 65)

     #   buttonlist.append(self.button)
        self.setGeometry(300, 300, 280, 150)
        
    def paintEvent(self, e):
        global linemode
        global paintarray
        global linearray
        global linetype
        global linenum
        
        painter = QPainter(self)
        
        if linetype == 'true':
            pen = QPen(Qt.green, 3)
        if linetype == 'false':
            pen = QPen(Qt.red, 3)
            
        painter.setPen(pen)
        
        for i in range(len(linearray)) :
            if linearray[i][2] == 'true':
                pen=QPen(Qt.green, 3)
                painter.setPen(pen)
                s = linearray[i][1].position.x()
                endpos = QPoint(s + linearray[i][1].width()/2, linearray[i][1].position.y())
                startpos = QPoint(linearray[i][0].position.x() + linearray[i][0].width()/2, linearray[i][0].position.y() + linearray[i][0].height()) 
                painter.drawLine(startpos, endpos)
                x = QLineF(endpos, startpos)
                x.setLength(10)
                y = QLineF(x.p2(), endpos)
                x1 = y.normalVector()
                x1.setLength(x1.length() * 0.5)
                x2 = x1.normalVector().normalVector()
                p1 = y.p2()
                p2 = x1.p2()
                p3 = x2.p2()
                painter.drawLine(p2, p1)
                painter.drawLine(p3, p1)
                
                
            if linearray[i][2] == 'false':
                pen = QPen(Qt.red, 3)
                painter.setPen(pen)
                s = linearray[i][1].position.x()
                endpos = QPoint(s + linearray[i][1].width()/2, linearray[i][1].position.y())
                startpos = QPoint(linearray[i][0].position.x() + linearray[i][0].width()/2, linearray[i][0].position.y() + linearray[i][0].height()) 
                painter.drawLine(startpos, endpos)
                x = QLineF(endpos, startpos)
                x.setLength(10)
                y = QLineF(x.p2(), endpos)
                x1 = y.normalVector()
                x1.setLength(x1.length() * 0.5)
                x2 = x1.normalVector().normalVector()
                p1 = y.p2()
                p2 = x1.p2()
                p3 = x2.p2()
                painter.drawLine(p2, p1)
                painter.drawLine(p3, p1)
        
        if linemode == 1:
            if len(paintarray) == 2:
                linename = 'line_' + str(linenum)
                linearray.append([paintarray[0], paintarray[1], linetype, linename])
                linenum = linenum + 1
                x = painter.drawLine(paintarray[0].position, paintarray[1].position)
                paintarray = []
                self.repaint()

    def dragEnterEvent(self, e):
      
        e.accept()
        
    def dragMoveEvent(self, e):

        global buttonlist
        position = e.pos()
        x = position.x()+200
        y = position.y()+30
        position2 = QPoint(x, y)
        
        for button in buttonlist:
            if button.dragable == 1:
                button.move(position2)
                button.position = position
        
        e.setDropAction(Qt.MoveAction)
        e.accept()
        self.repaint()
        
# =============================================================================
#     def dropEvent(self, e):
# 
#         global buttonlist
#         
#         for button in buttonlist:
#             if button.dragable == 1:
#                 button.dragable = 0
#         
#         e.setDropAction(Qt.MoveAction)
#         e.accept()
#         
# =============================================================================
    def mouseReleaseEvent(self, e):
        self.repaint()
    
class HelloWindow(QMainWindow):
    isPaintWindSpeed = True
    isPaintRPM       = True
    isPaintPower     = True 
    def __init__(self):
        super().__init__()
        
        
        QMainWindow.__init__(self)
  
        centralWidget = QWidget(self)          
        self.setCentralWidget(centralWidget)  
        
        self.setWindowTitle("Wind turbine control system") 
        
        
        self.setleftwidget()
        self.setrightwidget()
        
        finallayout = QHBoxLayout()
        finallayout.addWidget(leftwidget)
        finallayout.addWidget(rightwidget)
        
        centralWidget.setLayout(finallayout)                                   #set final layout
        
        toolbarBox = QtWidgets.QToolBar(self)
        toolbarBox.setFixedWidth(180)
        toolbarBox.setMovable(False)
        self.addToolBar(QtCore.Qt.LeftToolBarArea, toolbarBox)
        
        add_Start_action = toolbarBox.addAction('Start')
        add_Start_action.triggered.connect(self.add_Start)
        add_End_action = toolbarBox.addAction('End')
        add_End_action.triggered.connect(self.add_End)
        
# =============================================================================
#         with open('PrintTest.py', encoding = 'utf8') as f:                      #import function.py
#             for line in f:
#                 cleanline = line.strip()
#                 if cleanline.find("class ") != -1:
#                     temp = cleanline.split()
#                     temp = temp[1].split('(')
#                     add_function_action = toolbarBox.addAction(temp[0])
#                     add_function_action.triggered.connect(lambda checked, string = temp[0]:self.add_Process(string))
#                     
# =============================================================================
        moduleclass = SetModule.getClass()
        moduleclass.remove('ExtremePointMode')
        moduleclass.remove('originalMode')
        moduleclass.remove('Decide')
        moduleclass.remove('Loop')
        for i in range(len(moduleclass)):
            add_function_action = toolbarBox.addAction(moduleclass[i])
            add_function_action.triggered.connect(lambda checked, string = moduleclass[i]:self.add_Process(string))
# =============================================================================
#         
#         add_ThreePhaseShortCircuit_action = toolbarBox.addAction('mode_ThreePhaseShortCircuit')
#         add_ThreePhaseShortCircuit_action.triggered.connect(self.add_ThreePhaseShortCircuit)
#                 
#         add_MaxPower_action = toolbarBox.addAction('mode_MaxPower')
#         add_MaxPower_action.triggered.connect(self.add_MaxPower)
#         
#         add_MaxTorqueCurrent_action = toolbarBox.addAction('mode_MaxTorqueCurrent')
#         add_MaxTorqueCurrent_action.triggered.connect(self.add_MaxTorqueCurrent)
#         
#         add_MaxTorqueCurrent_MagBrake_action = toolbarBox.addAction('mode_MaxTorqueCurrent_MagBrake')
#         add_MaxTorqueCurrent_MagBrake_action.triggered.connect(self.add_MaxTorqueCurrent_MagBrake)
#         
#         add_ThreePhaseShortCircuit_MagBrake_action = toolbarBox.addAction('mode_ThreePhaseShortCircuit_MagBrake')
#         add_ThreePhaseShortCircuit_MagBrake_action.triggered.connect(self.add_ThreePhaseShortCircuit_MagBrake)
#         
# =============================================================================
        add_decision_action = toolbarBox.addAction('Decision')
        add_decision_action.triggered.connect(self.add_Decision)
        
        add_Loop_action = toolbarBox.addAction('Loop')
        add_Loop_action.triggered.connect(self.add_Loop)
        
        add_line_action = toolbarBox.addAction('true line')
        add_line_action.triggered.connect(self.add_line)
        
        add_fline_action = toolbarBox.addAction('false line')
        add_fline_action.triggered.connect(self.add_false_line)
        
        menu = self.menuBar().addMenu('File')
        read_action = menu.addAction('Import')
        read_action.triggered.connect(self.Read_File)
        write_action = menu.addAction('Export')
        write_action.triggered.connect(self.Write_File)
        
        add_draw_action = self.menuBar().addAction('draw')
        add_draw_action.triggered.connect(self.start_draw)
        
        menu_changefigure = self.menuBar().addMenu('Figure')
        RPM_action = menu_changefigure.addAction('RPM')
        RPM_action.triggered.connect(self.show_WindSpeed)
        WindSpeed_action = menu_changefigure.addAction('WindSpeed')
        WindSpeed_action.triggered.connect(self.show_WindSpeed)
        
    
    
    def setleftwidget(self):                                        #set work area layout
        global leftwidget
        global leftlayout
        global buttonlist
        
        leftwidget = Example()
        
       # leftwidget.setLayout(leftlayout)
    
    def setrightwidget(self):                                       #set drow area layout
        global rightwidget
        global label
        global windspeed
        global figure
        global errormsg

        #rightlowlayout = QVBoxLayout()
        #self.canvas.draw()
        
        #self.toolbar = NavigationToolbar(self.canvas, self)
        #self.toolbar.hide()
        
        #label.setText("1235497")
        #right_low_widget = QWidget()
        #right_low_widget.setLayout(rightlowlayout)
        rightwidget = rightcanvas()
        
        #rightlayout = QVBoxLayout()
        
        #rightlayout.addWidget(label)
        
        #rightwidget.setLayout(rightlayout)
        
    def Write_File(self):
        global buttonlist
        
        self.full_buttonlist()

        f = open('windele.txt', 'w')
        for i in buttonlist:
            if i.mode == 'process':
                if i.ExtremePoint == 0:                                         #write 'Mode_' + i.string + str(i.nodenum), i.string, i.inputline, [i.next_index]
                    f.write('Mode_' + i.string + str(i.nodenum) + ' ')
                    f.write(i.string+' ')
                    f.write('[')
                    for j in i.inputline:
                        f.write(j+',')
                    f.write('] ')
                    f.write('[' + i.next_index + ']')
                else:
                    if i.string == 'End':                                       #write i.string+str(i.nodenum), 'ExtremePointMode', i.inputline, []
                        f.write(i.string + str(i.nodenum) + ' ')
                        f.write('ExtremePointMode ')
                        f.write('[')
                        for j in i.inputline:
                           f.write(j+',')
                        f.write('] ')
                        f.write('[]')
                    else:                                                       #write i.string, 'ExtremePointMode', i.inputline, [i.next_index]
                        f.write(i.string + ' ')
                        f.write('ExtremePointMode ')
                        f.write('[')
                        for j in i.inputline:
                           f.write(j+',')
                        f.write('] ')
                        f.write('[')
                        f.write(i.next_index)
                        f.write(']')

            elif i.mode == 'Decision':                                          #write i.string+str(i.nodenum), 'Decide', i.inputline, [i.true_index, i.false_index], [i.compare_stuff, i.compare_num, i.compare_symbol]
                f.write(i.string + str(i.nodenum) + ' ')
                f.write('Decide ')
                f.write('[')
                for j in i.inputline:
                    f.write(j+',')
                f.write('] ')
                f.write('[' + i.true_index + ',' + i.false_index + '] ')
                f.write('[' + i.compare_stuff + ',' + str(i.compare_num) + ',' + i.compare_symbol + ']')
                
            elif i.mode == 'Loop':                                              #write i.string+str(i.nodenum), i.string, i.inputline, [i.cont_index, i.break_index], [0, i.loop_time]
                f.write(i.string + str(i.nodenum) + ' ')
                f.write(i.string + ' ')
                f.write('[')
                for j in i.inputline:
                    f.write(j+',')
                f.write('] ')
                f.write('[' + i.cont_index + ',' + i.break_index + '] ')
                f.write('[0,' + str(i.loop_time) + ']')
            f.write('\n')
        f.close()
            
    def Read_File(self):
        global linearray
        global buttonlist
        
        linearray = []
        buttonlist = []
        count = 1                                   #number of string line being imported in file
        true_line_added = 'false'                   #check if line is in linearray
        false_line_added = 'false'
        
        null_button = Process_Button('123', self)
        
        f = open('windele.txt', 'r')    
        for line in f:
            temp = line.strip().split(' ')
            if(temp[0] == 'Start'):
                exec("self.add_"+temp[0]+"()")
                buttonlist[0].string = temp[0]
                buttonlist[0].next_index = temp[4]
                linearray.append([buttonlist[0],null_button,'true',temp[4]])
                
                if(len(temp[5]) != 2):
                    input_line = temp[5][1:-2].split(',')
                    for j in input_line:
                        for i in linearray:
                            if j == i[3]:
                                i[1] = buttonlist[0]
                                true_line_added = 'true'
                        if(true_line_added == 'false'):
                            linearray.append([null_button,buttonlist[0],'null',j])
                        true_line_added = 'false'
                                    
            else:
                if(temp[0] == 'Comparisongreater'):
                    exec("self.add_Decision()")
                    compare = '>'
                    
                elif(temp[0] == 'Comparisongreaterorequal'):
                    exec("self.add_Decision()")
                    compare = '>='
                elif(temp[0] == 'Loop'):
                    exec("self.add_Loop()")
                else:
                    name = temp[0].split('_')
                    exe_name = ''
                    for i in name:
                        if(i!='Mode'):
                            exe_name = exe_name + '_' + i
                    exec("self.add_Process(temp[0])")
                
                if(temp[1] == 'process'):
                    buttonlist[count].next_index = temp[4]
                    
                    for i in linearray:
                        if temp[4] == i[3]:
                            i[0] = buttonlist[count]
                            i[2] = 'true'
                            true_line_added = 'true'
                    if(true_line_added == 'false'):
                        if(temp[4] != 'null'):
                            linearray.append([buttonlist[count],null_button,'true',temp[4]])
                    true_line_added = 'false'
                    
                    if(len(temp[5]) != 2):
                        input_line = temp[5][1:-2].split(',')
                        for j in input_line:
                            for i in linearray:
                                if j == i[3]:
                                    i[1] = buttonlist[count]
                                    true_line_added = 'true'
                            if(true_line_added == 'false'):
                                linearray.append([null_button,buttonlist[count],'null',j])
                            true_line_added = 'false'
                        
                    count += 1
                    
                if(temp[1] == 'decision'):
                    buttonlist[count].string = temp[0]
                    buttonlist[count].true_index = temp[4]
                    buttonlist[count].false_index = temp[5]
                    buttonlist[count].compare_stuff = temp[7]
                    buttonlist[count].compare_num = float(temp[8])
                    buttonlist[count].setText(buttonlist[count].compare_stuff + '  '+ compare + ' ' + str(buttonlist[count].compare_num))
                    
                    for i in linearray:
                        if temp[4] == i[3]:
                            i[0] = buttonlist[count]
                            i[2] = 'true'
                            true_line_added = 'true'
                        if temp[5] == i[3]:
                            i[0] = buttonlist[count]
                            i[2] = 'false'
                            false_line_added = 'true'
                    if(true_line_added == 'false'):
                        if(temp[4] != 'null'):
                            linearray.append([buttonlist[count],null_button,'true',temp[4]])
                    if(false_line_added == 'false'):
                        if(temp[5] != 'null'):
                            linearray.append([buttonlist[count],null_button,'false',temp[5]])
                    true_line_added = 'false'
                    false_line_added = 'false'
                    
                    if(len(temp[6]) != 2):
                        input_line = temp[6][1:-2].split(',')
                        for j in input_line:
                            for i in linearray:
                                if j == i[3]:
                                    i[1] = buttonlist[count]
                                    true_line_added = 'true'
                            if(true_line_added == 'false'):
                                linearray.append([null_button,buttonlist[count],'null',j])
                            true_line_added = 'false'
                        
                    count += 1
                    
                if(temp[1] == 'loop'):
                    buttonlist[count].string = temp[0]
                    buttonlist[count].cont_index = temp[4]
                    buttonlist[count].break_index = temp[5]
                    buttonlist[count].loop_time = temp[7]
                    buttonlist[count].setText('Loop ' + str(buttonlist[count].loop_time) + ' times')
                    
                    for i in linearray:
                        if temp[4] == i[3]:
                            i[0] = buttonlist[count]
                            i[2] = 'true'
                            true_line_added = 'true'
                        if temp[5] == i[3]:
                            i[0] = buttonlist[count]
                            i[2] = 'false'
                            false_line_added = 'true'
                    if(true_line_added == 'false'):
                        if(temp[4]!='null'):
                            linearray.append([buttonlist[count],null_button,'true',temp[4]])
                    if(false_line_added == 'false'):
                        if(temp[4]!='null'):
                            linearray.append([buttonlist[count],null_button,'false',temp[4]])
                    true_line_added = 'false'
                    false_line_added = 'false'
                    
                    if(len(temp[6]) != 2):
                        input_line = temp[6][1:-2].split(',')
                        for j in input_line:
                            for i in linearray:
                                if j == i[3]:
                                    i[1] = buttonlist[count]
                                    true_line_added = 'true'
                            if(true_line_added == 'false'):
                                linearray.append([null_button,buttonlist[count],'null',j])
                            true_line_added = 'false'

                    count += 1
        f.close()    
        
    def add_button(self):
        global leftlayout
        global leftwidget
        global buttonlist
        
        leftwidget.button0 = Process_Button('123', self)
        buttonlist.append(leftwidget.button0)
    
    def add_Start(self):
        global leftlayout
        global leftwidget
        global buttonlist
        
        leftwidget.button0 = Process_Button('Start', self)
        leftwidget.button0.setStyleSheet("background-color: Gray")
        leftwidget.button0.string = 'Start'
        leftwidget.button0.ExtremePoint = 1
        buttonlist.append(leftwidget.button0)
        leftwidget.button0.setGeometry(240, 30, 210, 30)
        leftwidget.button0.position.setX(240)
        leftwidget.button0.position.setY(30)
        leftwidget.button0.show()
        
    def add_End(self):
        global leftlayout
        global leftwidget
        global buttonlist
        count = 0
        
        leftwidget.button = Process_Button('End', self)
        leftwidget.button.setStyleSheet("background-color: Gray")
        leftwidget.button.string = 'End'
        leftwidget.button.ExtremePoint = 1
        for i in buttonlist:
            if i.mode == 'process':
                count = count + 1
        leftwidget.button.nodenum = count
        buttonlist.append(leftwidget.button)
        leftwidget.button.setGeometry(240, 30, 210, 30)
        leftwidget.button.position.setX(240)
        leftwidget.button.position.setY(30)
        leftwidget.button.show()
    
    def add_Process(self, name):
        global leftlayout
        global leftwidget
        global buttonlist
        count = 0
        if name == False:        
            leftwidget.button = Process_Button('Process', self)
            leftwidget.button.string = 'Process'
        else:
            leftwidget.button = Process_Button(name, self)
            leftwidget.button.string = name
        leftwidget.button.setStyleSheet("background-color: DodgerBlue")
        for i in buttonlist:
            if i.mode == 'process':
                count = count + 1
        leftwidget.button.nodenum = count
        buttonlist.append(leftwidget.button)
        leftwidget.button.setGeometry(240, 30, 210, 30)
        leftwidget.button.position.setX(240)
        leftwidget.button.position.setY(30)
        leftwidget.button.show()
    
    def add_Decision(self):
        global leftlayout
        global leftwidget
        global buttonlist
        count = 0
        leftwidget.button = Decision_Button('Decision', self)
        leftwidget.button.string = 'Decision'
        for i in buttonlist:
            if i.mode == 'Decision':
                count = count + 1
        leftwidget.button.nodenum = count
        buttonlist.append(leftwidget.button)
        leftwidget.button.setGeometry(240, 30, 210, 30)
        leftwidget.button.position.setX(240)
        leftwidget.button.position.setY(30)
        leftwidget.button.show()
    
    def add_Loop(self):
        global leftlayout
        global leftwidget
        global buttonlist
        global figure
        count = 0
        
        leftwidget.button = Loop_Button('Loop', self)
        leftwidget.button.setText('Loop ' + str(leftwidget.button.loop_time) + ' times')
        leftwidget.button.string = 'Loop'
        for i in buttonlist:
            if i.string == 'Loop':
                count = count + 1
        leftwidget.button.nodenum = count
        menu = QMenu(self)
        end_action = QAction(menu)
        end_action.setText("add end point")
        menu.addAction(end_action)
        end_action.triggered.connect(lambda checked, string = leftwidget.button.string + str(leftwidget.button.nodenum):self.add_Loop_end(string))
        leftwidget.button.setMenu(menu)
        leftwidget.button.setStyleSheet("QPushButton::menu-indicator{image:none;}")
        leftwidget.button.setStyleSheet("background-color: Orange")
        buttonlist.append(leftwidget.button)
        leftwidget.button.setGeometry(240, 30, 210, 30)
        leftwidget.button.position.setX(240)
        leftwidget.button.position.setY(30)
        leftwidget.button.show()
        #leftlayout.addWidget(leftwidget.button)
        
    def add_Loop_end(self, Loop_name):                                                      #insert name of loop will be ended
        global leftlayout
        global leftwidget
        global buttonlist
        global figure
        count = 0
        
        leftwidget.button = Loop_end('Loop End', self)
        leftwidget.button.string = Loop_name + 'end'
        for i in buttonlist:
            if i.mode == 'Loop_end':
                count = count + 1
        leftwidget.button.nodenum = count
        buttonlist.append(leftwidget.button)
        leftwidget.button.setGeometry(240, 30, 210, 30)
        leftwidget.button.position.setX(240)
        leftwidget.button.position.setY(30)
        leftwidget.button.show()
        
    def add_line(self):
        global linemode
        global paintarray
        global linetype
        global buttonlist
        
        if linemode == 0:
            linemode = 1
            linetype = 'true'
            for i in buttonlist:
                if i.dragable == True:
                    i.dragable = False
        else :
            if linetype == 'false':
                linetype = 'true'
                paintarray = []
            else:
                linemode = 0
                paintarray = []
                
    def add_false_line(self):
        global linemode
        global paintarray
        global linetype
        global buttonlist
        
        if linemode == 0:
            linemode = 1
            linetype = 'false'
            for i in buttonlist:
                if i.dragable == True:
                    i.dragable = False
        else :
            if linetype == 'true':
                linetype = 'false'
                paintarray = []
            else:
                linemode = 0
                paintarray = []
    
    def show_RPM(self):
        if(self.start_draw.isPaintRPM == True):
            self.start_draw.isPaintRPM = False
        else:
            self.start_draw.isPaintRPM = True
    def show_WindSpeed(self):
        if(self.start_draw.isPaintWindSpeed == True):
            self.start_draw.isPaintWindSpeed = False
        else:
            self.start_draw.isPaintWindSpeed = True
    def show_Power(self):
        if(self.start_draw.isPaintPower == True):
            self.start_draw.isPaintPower = False
        else:
            self.start_draw.isPaintPower = True
            
    def full_buttonlist(self):
        global buttonlist
        global linearray
        
        for i in buttonlist:
            a = []
            if i.mode == 'process': 
                for j in range(len(linearray)):
                    if linearray[j][1].string == i.string and linearray[j][1].nodenum == i.nodenum:
                        a.append(linearray[j][3])
                    if linearray[j][0].string == i.string and linearray[j][0].nodenum == i.nodenum:           #找線
                        i.next_index = linearray[j][3]
    
            if i.mode == 'Decision': 
                for j in range(len(linearray)):
                    if linearray[j][1].string == i.string and linearray[j][1].nodenum == i.nodenum:
                        a.append(linearray[j][3])
                    if linearray[j][0].string == i.string and linearray[j][0].nodenum == i.nodenum:           #找線
                        
                        if linearray[j][2] == 'true':
                            i.true_index = linearray[j][3]
                                
                        else:
                            i.false_index = linearray[j][3]
                            
            if i.mode == 'Loop': 
                for j in range(len(linearray)):
                    if linearray[j][1].string == i.string and linearray[j][1].nodenum == i.nodenum:
                        a.append(linearray[j][3])
                    if linearray[j][0].string == i.string and linearray[j][0].nodenum == i.nodenum:           #找線
                        
                        if linearray[j][2] == 'true':
                            i.cont_index = linearray[j][3]
                                
                        else:
                            i.break_index = linearray[j][3]
            i.inputline = a
            
    def start_draw(self):
        global buttonlist
        global linearray
        global figure
        
        
        finallist = []
        
# =============================================================================
#         for i in buttonlist:
#             a = []
#             if i.mode == 'process': 
#                 for j in range(len(linearray)):
#                     if linearray[j][1].string == i.string and linearray[j][1].nodenum == i.nodenum:
#                         a.append(linearray[j][3])
#                     if linearray[j][0].string == i.string and linearray[j][0].nodenum == i.nodenum:           #找線
#                         i.next_index = linearray[j][3]
#     
#             if i.mode == 'decision': 
#                 for j in range(len(linearray)):
#                     if linearray[j][1].string == i.string and linearray[j][1].nodenum == i.nodenum:
#                         a.append(linearray[j][3])
#                     if linearray[j][0].string == i.string and linearray[j][0].nodenum == i.nodenum:           #找線
#                         
#                         if linearray[j][2] == 'true':
#                             i.true_index = linearray[j][3]
#                                 
#                         else:
#                             i.false_index = linearray[j][3]
#                             
#             if i.mode == 'loop': 
#                 for j in range(len(linearray)):
#                     if linearray[j][1].string == i.string and linearray[j][1].nodenum == i.nodenum:
#                         a.append(linearray[j][3])
#                     if linearray[j][0].string == i.string and linearray[j][0].nodenum == i.nodenum:           #找線
#                         
#                         if linearray[j][2] == 'true':
#                             i.cont_index = linearray[j][3]
#                                 
#                         else:
#                             i.break_index = linearray[j][3]
#             i.inputline = a
# =============================================================================
        self.full_buttonlist()
        for i in buttonlist:
            if i.mode == 'process':
                if i.ExtremePoint == 0:
                    pac = ["Mode_" + i.string + str(i.nodenum), i.string, i.inputline, [i.next_index]]
                else:
                    if i.string == 'End':
                        pac = [i.string+str(i.nodenum), 'ExtremePointMode', i.inputline, []]
                    else:
                        pac = [i.string, 'ExtremePointMode', i.inputline, [i.next_index]]
            if i.mode == 'Decision': 
                pac = [i.string+str(i.nodenum), 'Decide', i.inputline, [i.true_index, i.false_index], [i.compare_stuff, i.compare_num, i.compare_symbol]]
            if i.mode == 'Loop':
                pac = [i.string+str(i.nodenum), i.string, i.inputline, [i.cont_index, i.break_index], [i.compare_stuff, i.compare_num, i.compare_symbol], i.loop_time]
            finallist.append(pac)
# =============================================================================
#         f = open('list_useinunitest.txt', 'w')
#         for i in range(0, len(buttonlist)):
#             if(i == len(buttonlist)-1):
#                 if buttonlist[i].mode == 'process':
#                     f.write("['")
#                     f.write(buttonlist[i].string+str(buttonlist[i].nodenum))
#                     f.write("', ")
#                     f.write("'")
#                     f.write(buttonlist[i].string)
#                     f.write("', [")
#                     if(len(buttonlist[i].inputline) != 0):
#                         for count in range(0, len(buttonlist[i].inputline)):
#                             if (count == len(buttonlist[i].inputline)-1):
#                                 f.write("'")
#                                 f.write(buttonlist[i].inputline[count])
#                                 f.write("'")
#                             else:
#                                 f.write("'")
#                                 f.write(buttonlist[i].inputline[count])
#                                 f.write("', ")
#                     f.write("], ['")
#                     f.write(buttonlist[i].next_index)
#                     f.write("']]")
#                                 
#                 if buttonlist[i].mode == 'decision': 
#                     f.write("['")
#                     f.write(buttonlist[i].string+str(buttonlist[i].nodenum))
#                     f.write("', ")
#                     f.write("'")
#                     f.write(buttonlist[i].string)
#                     f.write("', [")
#                     if(len(buttonlist[i].inputline) != 0):
#                         for count in range(0, len(buttonlist[i].inputline)):
#                             if (count == len(buttonlist[i].inputline)-1):
#                                 f.write("'")
#                                 f.write(buttonlist[i].inputline[count])
#                                 f.write("'")
#                             else:
#                                 f.write("'")
#                                 f.write(buttonlist[i].inputline[count])
#                                 f.write("', ")
#                     f.write("], ['")
#                     f.write(buttonlist[i].true_index)
#                     f.write("', ")
#                     f.write("'")
#                     f.write(buttonlist[i].false_index)
#                     f.write("']]")
#                         
#                 if buttonlist[i].mode == 'loop':
#                     f.write("['")
#                     f.write(buttonlist[i].string+str(buttonlist[i].nodenum))
#                     f.write("', ")
#                     f.write("'")
#                     f.write(buttonlist[i].string)
#                     f.write("', [")
#                     if(len(buttonlist[i].inputline) != 0):
#                         for count in range(0, len(buttonlist[i].inputline)):
#                             if (count == len(buttonlist[i].inputline)-1):
#                                 f.write("'")
#                                 f.write(buttonlist[i].inputline[count])
#                                 f.write("'")
#                             else:
#                                 f.write("'")
#                                 f.write(buttonlist[i].inputline[count])
#                                 f.write("', ")
#                     f.write("], ['")
#                     f.write(buttonlist[i].cont_index)
#                     f.write("', ")
#                     f.write("'")
#                     f.write(buttonlist[i].break_index)
#                     f.write("'], ")
#                     f.write("0, ")
#                     f.write(str(buttonlist[i].loop_time))
#                     f.write("]")
#             else:    
#                 if buttonlist[i].mode == 'process':
#                     f.write("['")
#                     f.write(buttonlist[i].string+str(buttonlist[i].nodenum))
#                     f.write("', ")
#                     f.write("'")
#                     f.write(buttonlist[i].string)
#                     f.write("', [")
#                     if(len(buttonlist[i].inputline) != 0):
#                         for count in range(0, len(buttonlist[i].inputline)):
#                             if (count == len(buttonlist[i].inputline)-1):
#                                 f.write("'")
#                                 f.write(buttonlist[i].inputline[count])
#                                 f.write("'")
#                             else:
#                                 f.write("'")
#                                 f.write(buttonlist[i].inputline[count])
#                                 f.write("', ")
#                     f.write("], ['")
#                     f.write(buttonlist[i].next_index)
#                     f.write("']],\n")
#                                 
#                 if buttonlist[i].mode == 'decision': 
#                     f.write("['")
#                     f.write(buttonlist[i].string+str(buttonlist[i].nodenum))
#                     f.write("', ")
#                     f.write("'")
#                     f.write(buttonlist[i].string)
#                     f.write("', [")
#                     if(len(buttonlist[i].inputline) != 0):
#                         for count in range(0, len(buttonlist[i].inputline)):
#                             if (count == len(buttonlist[i].inputline)-1):
#                                 f.write("'")
#                                 f.write(buttonlist[i].inputline[count])
#                                 f.write("'")
#                             else:
#                                 f.write("'")
#                                 f.write(buttonlist[i].inputline[count])
#                                 f.write("', ")
#                     f.write("], ['")
#                     f.write(buttonlist[i].true_index)
#                     f.write("', ")
#                     f.write("'")
#                     f.write(buttonlist[i].false_index)
#                     f.write("']],\n")
#                         
#                 if buttonlist[i].mode == 'loop':
#                     f.write("['")
#                     f.write(buttonlist[i].string+str(buttonlist[i].nodenum))
#                     f.write("', ")
#                     f.write("'")
#                     f.write(buttonlist[i].string)
#                     f.write("', [")
#                     if(len(buttonlist[i].inputline) != 0):
#                         for count in range(0, len(buttonlist[i].inputline)):
#                             if (count == len(buttonlist[i].inputline)-1):
#                                 f.write("'")
#                                 f.write(buttonlist[i].inputline[count])
#                                 f.write("'")
#                             else:
#                                 f.write("'")
#                                 f.write(buttonlist[i].inputline[count])
#                                 f.write("', ")
#                     f.write("], ['")
#                     f.write(buttonlist[i].cont_index)
#                     f.write("', ")
#                     f.write("'")
#                     f.write(buttonlist[i].break_index)
#                     f.write("'], ")
#                     f.write("0, ")
#                     f.write(str(buttonlist[i].loop_time))
#                     f.write("],\n")
# =============================================================================
        
        errormsg = FrameworkDebugger.TestErrorRaise(finallist)
        
        if errormsg  != '':
            rightwidget.errorlabel.setText(errormsg)
        else:
            CompileList.execBlockChart(finallist)
        
# =============================================================================
#         isPaintWindSpeed = True
#         isPaintRPM       = True
#         isPaintPower     = True 
# =============================================================================
        #figure = Paint.PaintDiagram("Wind Turbine Control System", "Time (s)", "WindSpeed (m/s)", "RPM", "Power   ( W )", Parameter.TimeSeries,  isPaintWindSpeed, Parameter.WindSpeed, isPaintRPM, Parameter.RPM, isPaintPower, Parameter.Power)
        #print('print figure',figure)


            HelloWindow.draw_fig(HelloWindow.isPaintWindSpeed, HelloWindow.isPaintRPM, HelloWindow.isPaintPower)
# =============================================================================
#         str_ylabel_2 = "RPM"
#         str_ylabel_3 = "Power   ( W )"
#         y2X10  = [i*10 for i in Parameter.RPM]
#      
#         ax1 = figure.add_subplot(111) #(dpi  (16*80)*(9*80) = 1240*720)
#         if isPaintRPM is True:
#             ax1.plot(Parameter.TimeSeries , y2X10, label = str_ylabel_2, color='b')
#             str_ylabel_2 = str_ylabel_2 + "     X  10" + "\n"
#         else:
#             str_ylabel_2 = ""
#         
#         if isPaintPower is True:
#             ax1.plot(Parameter.TimeSeries, Parameter.Power, label = str_ylabel_3, color='r')
#             str_ylabel_3 = str_ylabel_3 + "\n"
#         else:
#             str_ylabel_3 = ""
#          
#      
#         ax1.set_title("Wind Turbine Control System")
#         ax1.set_ylim(min(min(y2X10), min(Parameter.Power)),max(max(y2X10), max(Parameter.Power)))
#         ax1.set_xlabel("Time (s)")
#         ax1.set_ylabel(str_ylabel_2 + str_ylabel_3)
#         ax1.legend(loc=2) # upper left
#         ax1.set_xlim(min(Parameter.TimeSeries), max(Parameter.TimeSeries))
#     
#         if isPaintWindSpeed is True:  
#             ax2 = ax1.twinx()
#             ax2.plot(Parameter.TimeSeries, Parameter.WindSpeed, label = "WindSpeed (m/s)", color='g')
#             ax2.set_xlim(min(Parameter.TimeSeries), max(Parameter.TimeSeries))
#             ax2.set_ylim(min(Parameter.WindSpeed),max(Parameter.WindSpeed))
#             ax2.set_ylabel("WindSpeed (m/s)")
#             ax2.legend(loc=1) # upper right
# =============================================================================
            
#        plt.savefig("123")
        
        #ExportData.ExportExcelData(Parameter.TimeSeries, Parameter.WindSpeed, Parameter.RPM, Parameter.Power, Parameter.CpStack, Parameter.eff_gStack, Parameter.ModeStack)
        
        
# =============================================================================
#         for i in finallist:
#             print(i)
# =============================================================================
    def draw_fig(isPaintWindSpeed, isPaintRPM, isPaintPower):
        global figure
        
        figure.clf()
        
        str_ylabel_2 = "RPM"
        #str_ylabel_3 = "Power   ( W )"
        #y2X10  = [i*10 for i in Parameter.RPM]
     
        ax1 = figure.add_subplot(111) #(dpi  (16*80)*(9*80) = 1240*720)
        if isPaintRPM is True:
            ax1.plot([0,1],[0,2])
            str_ylabel_2 = str_ylabel_2 + "     X  10" + "\n"
        else:
            str_ylabel_2 = ""
        
# =============================================================================
#         if isPaintPower is True:
#             ax1.plot(Parameter.TimeSeries, Parameter.Power, label = str_ylabel_3, color='r')
#             str_ylabel_3 = str_ylabel_3 + "\n"
#         else:
#             str_ylabel_3 = ""
#          
#      
#         ax1.set_title("Wind Turbine Control System")
#         ax1.set_ylim(min(min(y2X10), min(Parameter.Power)),max(max(y2X10), max(Parameter.Power)))
#         ax1.set_xlabel("Time (s)")
#         ax1.set_ylabel(str_ylabel_2 + str_ylabel_3)
#         ax1.legend(loc=2) # upper left
#         ax1.set_xlim(min(Parameter.TimeSeries), max(Parameter.TimeSeries))
#     
#         if isPaintWindSpeed is True:  
#             ax2 = ax1.twinx()
#             ax2.plot(Parameter.TimeSeries, Parameter.WindSpeed, label = "WindSpeed (m/s)", color='g')
#             ax2.set_xlim(min(Parameter.TimeSeries), max(Parameter.TimeSeries))
#             ax2.set_ylim(min(Parameter.WindSpeed),max(Parameter.WindSpeed))
#             ax2.set_ylabel("WindSpeed (m/s)")
#             ax2.legend(loc=1) # upper right        
#         plt.savefig("123")
# =============================================================================
 
if __name__ == "__main__":
    def run_app():
        app = QApplication(sys.argv)
        mainWin = HelloWindow()
        mainWin.setMinimumWidth(1200)
        mainWin.setMinimumHeight(500)
        mainWin.show()
        sys.exit(app.exec_())
    run_app()
    