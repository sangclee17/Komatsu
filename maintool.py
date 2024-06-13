# coding: shift-jis
import tkinter as tk
from tkinter.ttk import Separator
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import sys, os
from PIL import Image, ImageTk
import win32gui
import importlib
from hwx import simlab

## global
SRC_DIR = os.path.dirname(os.path.realpath(__file__))
IMAGE_DIR = (os.path.join(SRC_DIR, 'images'))
PROJECT_DIR = os.path.join(SRC_DIR, "..")
LOG_DIR = os.path.join(PROJECT_DIR, "log")

if not SRC_DIR in sys.path:
    sys.path.append(SRC_DIR)

import history
import backup
import importCAD
import configreader
import mesh2d
import filletWelding
import faceMergeSplit
import straightLine
import grooveWelding
import buttWelding
import intermittentWelding
import yomoriWelding
import splitEdge
import projectEdge
import joinBead
import beadConnection
import fillGap
import splitCircumference
import beadRetouch

## Main Tool Widget
class MainTool(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.config = configreader.ConfigReader()
        self.backup = backup.ModelBackup(self.config)
        self.dialog = None

        # dialog attribute
        self.master.title('溶接モデリング')
        self.master.resizable(width=False, height=False)
        self.master.attributes("-topmost", True)
        self.master.protocol("WM_DELETE_WINDOW", self.CloseDialog)
        _, _, (x,y) = win32gui.GetCursorInfo()
        self.master.wm_geometry("+%d+%d" % (x, y))
    
        self.CreateWidgets()
        self.CreateUtilityWidget()

        importlib.reload(history)
        self.history = history.MenuHistory(self)
    
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.frmTop.grid_columnconfigure((4,5), weight=1)
        btnWidth = 15

        # draw lines
        Separator(self.frmTop, orient='vertical').grid(row=0, column=1, sticky='nwse',padx=5)
        Separator(self.frmTop, orient='horizontal').grid(row=1, column=0, sticky='nwse',pady=5)
        Separator(self.frmTop, orient='vertical').grid(row=0, column=3, sticky='nwse',padx=5)
        Separator(self.frmTop, orient='horizontal').grid(row=1, column=2, columnspan=6, sticky='nwse',pady=5)

        Separator(self.frmTop, orient='vertical').grid(row=2, column=1, rowspan=11, sticky='nwse',padx=5)
        Separator(self.frmTop, orient='vertical').grid(row=2, column=3, rowspan=4, sticky='nwse',padx=5)
        Separator(self.frmTop, orient='horizontal').grid(row=6, column=2, columnspan=6, sticky='nwse',pady=5)

        Separator(self.frmTop, orient='vertical').grid(row=7, column=3, rowspan=3, sticky='nwse',padx=5)
        Separator(self.frmTop, orient='horizontal').grid(row=10, column=2, columnspan=6, sticky='nwse',pady=5)
        Separator(self.frmTop, orient='vertical').grid(row=11, column=3, rowspan=2, sticky='nwse',padx=5)


        tk.Label(self.frmTop,text='CAD:').grid(row=0, column=0, sticky='wn')

        CADRow = 0
        self.btnCADImport = tk.Button(self.frmTop, text='CADインポート', width=btnWidth, command=self.ImportCAD)
        self.btnCADImport.grid(row=CADRow, column=4, sticky='nwse')

        self.btnMesh2d = tk.Button(self.frmTop, text='表面メッシュ', width=btnWidth, command=self.CreateMesh2d)
        self.btnMesh2d.grid(row=CADRow, column=5, sticky='nwse')

        PreLineRow = 2
        tk.Label(self.frmTop,text='FEM:').grid(row=PreLineRow, column=0, sticky='wn')
        tk.Label(self.frmTop,text='Pre:').grid(row=PreLineRow, column=2, sticky='wn')

        self.btnLineStraight = tk.Button(self.frmTop, text= '直線作成', width=btnWidth, command=self.CreateStraightLine)
        self.btnLineStraight.grid(row=PreLineRow, column=4, sticky='nwse')

        self.btnSplitEdge = tk.Button(self.frmTop, text= 'エッジ長さ分割', width=btnWidth, command=self.SplitEdge)
        self.btnSplitEdge.grid(row=PreLineRow, column=5, sticky='nwse')

        self.btnProjectEdge = tk.Button(self.frmTop, text='エッジ投影', width=btnWidth, command=self.projectEdge)
        self.btnProjectEdge.grid(row=PreLineRow+1, column=4, sticky='nwse')

        self.btnCircumEdge = tk.Button(self.frmTop, text='円周分割', width=btnWidth, command=self.SplitCircumEdge)
        self.btnCircumEdge.grid(row=PreLineRow+1, column=5, sticky='nwse')

        PreFaceRow = 5

        self.btnfaceMergeSplit = tk.Button(self.frmTop,text='面マージ・分割',width=btnWidth, command=self.FaceMergeSplit)
        self.btnfaceMergeSplit.grid(row=PreFaceRow, column=4, sticky='nwse')

        self.btnFillGap = tk.Button(self.frmTop, text='ギャップ埋め', width=btnWidth, command=self.FillGap)
        self.btnFillGap.grid(row=PreFaceRow, column=5, sticky='nwse')

        weldTypeRow = 7
        tk.Label(self.frmTop,text='溶接:').grid(row=weldTypeRow, column=2, columnspan=3, sticky='wn')

        self.btnFilletWelding = tk.Button(self.frmTop, text='隅肉', width=btnWidth, command=self.FilletWelding)
        self.btnFilletWelding.grid(row=weldTypeRow, column=4, sticky='nwse')

        self.btnGrooveWelding = tk.Button(self.frmTop, text='開先', width=btnWidth, command=self.GrooveWelding)
        self.btnGrooveWelding.grid(row=weldTypeRow, column=5, sticky='nwse')

        self.btnButtWelding = tk.Button(self.frmTop, text='突合せ', width=btnWidth, command=self.ButtWelding)
        self.btnButtWelding.grid(row=weldTypeRow+1, column=4, sticky='nwse')

        self.btnIntermittentWelding = tk.Button(self.frmTop, text='断続', width=btnWidth, command=self.IntermittentWeld)
        self.btnIntermittentWelding.grid(row=weldTypeRow+1, column=5, sticky='nwse')

        self.btnYomoriWelding = tk.Button(self.frmTop, text='余盛', width=btnWidth, command=self.YomoriWelding)
        self.btnYomoriWelding.grid(row=weldTypeRow+2, column=4, sticky='nwse')

        PostConnectRow = 11
        tk.Label(self.frmTop, text='Post:').grid(row=PostConnectRow, column=2, sticky='wn')

        self.btnBeadConnect = tk.Button(self.frmTop, text='連結', width=btnWidth, command=self.ConnectBeads)
        self.btnBeadConnect.grid(row=PostConnectRow, column=4, sticky='nwse')

        self.btnJoinBead = tk.Button(self.frmTop, text='合流', width=btnWidth, command=self.JoinBead)
        self.btnJoinBead.grid(row=PostConnectRow, column=5, sticky='nwse')

        self.btnBeadRetouch = tk.Button(self.frmTop, text='ビード修正', width=btnWidth, command=self.RetouchBead)
        self.btnBeadRetouch.grid(row=PostConnectRow+1, column=4, sticky='nwse')
    
    def CreateUtilityWidget(self):
        
        self.frmUtil = tk.Frame(self.frmTop)
        self.frmUtil.grid(row=12, column=0, rowspan=2, sticky='nwse')
        self.iconEraser = ImageTk.PhotoImage(file=os.path.join(IMAGE_DIR, 'eraser.png'))
        self.btnEraser = tk.Button(self.frmUtil, image=self.iconEraser, command=self.DeleteHistories)
        self.btnEraser.pack(side=tk.TOP, anchor=tk.SW)

        self.iconUndo = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'undo-16.png')))
        self.btnUndo = tk.Button(self.frmUtil, image=self.iconUndo, command=self.Undo)
        self.btnUndo.pack(side=tk.TOP, anchor=tk.SW)
        self.backup.Append(self.btnUndo)
    
    def ImportCAD(self):
        self.CloseChildDialog()
        self.AddToHistory('ImportCAD')
        importlib.reload(importCAD)

        self.dialog = tk.Toplevel()
        app = importCAD.ImportDialog(master=self.dialog, parent=self.master)
        app.mainloop()
    
    def CreateMesh2d(self):
        self.CloseChildDialog()
        self.AddToHistory('Mesh2d')
        importlib.reload(mesh2d)

        self.dialog = tk.Toplevel()
        app = mesh2d.Mesh2dDialog(master=self.dialog, parent=self.master, config=self.config)
        app.mainloop()
    
    def FillGap(self):
        self.CloseChildDialog()
        self.AddToHistory('FillGap')
        importlib.reload(fillGap)

        self.dialog = tk.Toplevel()
        app = fillGap.FillGapDialog(master=self.dialog, parent=self.master)
        app.mainloop()
    
    def FilletWelding(self):
        self.CloseChildDialog()
        self.AddToHistory('FilletWelding')
        importlib.reload(filletWelding)

        self.dialog = tk.Toplevel()
        app = filletWelding.FilletWeldingDialog(master=self.dialog, parent=self.master, config=self.config, backup=self.backup)
        app.mainloop()
    
    def CreateStraightLine(self):
        self.CloseChildDialog()
        self.AddToHistory('StraightLine')
        importlib.reload(straightLine)

        self.dialog = tk.Toplevel()
        app = straightLine.StraightLineDialog(master=self.dialog, parent=self.master)
        app.mainloop()
    
    def SplitEdge(self):
        self.CloseChildDialog()
        self.AddToHistory('SplitEdge')
        importlib.reload(splitEdge)

        self.dialog = tk.Toplevel()
        app = splitEdge.SplitEdge(master=self.dialog, parent=self.master, config=self.config)
        app.mainloop()

    def projectEdge(self):
        self.CloseChildDialog()
        self.AddToHistory('ProjectEdge')
        importlib.reload(projectEdge)

        self.dialog = tk.Toplevel()
        app = projectEdge.ProjectEdge(master=self.dialog, parent=self.master)
        app.mainloop()
    
    def SplitCircumEdge(self):
        self.CloseChildDialog()
        self.AddToHistory('SplitCircumference')
        importlib.reload(splitCircumference)

        self.dialog = tk.Toplevel()
        app = splitCircumference.SplitCircumferenceDialog(master=self.dialog, parent=self.master, config=self.config)
        app.mainloop()
        
    def FaceMergeSplit(self):
        self.CloseChildDialog()
        self.AddToHistory('FaceMergeSplit')
        importlib.reload(faceMergeSplit)

        self.dialog = tk.Toplevel()
        app = faceMergeSplit.FaceMergeDialog(master=self.dialog, parent=self.master, config=self.config)
        app.mainloop()

    def GrooveWelding(self):
        self.CloseChildDialog()
        self.AddToHistory('GrooveWelding')
        importlib.reload(grooveWelding)

        self.dialog = tk.Toplevel()
        app = grooveWelding.GrooveWeldingDialog(master=self.dialog, parent=self.master, config=self.config, backup=self.backup)
        app.mainloop()

    def ButtWelding(self):
        self.CloseChildDialog()
        self.AddToHistory('ButtWelding')
        importlib.reload(buttWelding)

        self.dialog = tk.Toplevel()
        app = buttWelding.ButtWeldingDialog(master=self.dialog, parent=self.master, config=self.config, backup=self.backup)
        app.mainloop()

    def IntermittentWeld(self):
        self.CloseChildDialog()
        self.AddToHistory('IntermittentWelding')
        importlib.reload(intermittentWelding)

        self.dialog = tk.Toplevel()
        app = intermittentWelding.IntermittentWeldingDialog(master=self.dialog, parent=self.master, config=self.config, backup=self.backup)
        app.mainloop()

    def YomoriWelding(self):
        self.CloseChildDialog()
        self.AddToHistory('YomoriWelding')
        importlib.reload(yomoriWelding)

        self.dialog = tk.Toplevel()
        app = yomoriWelding.YomoriWeldingDialog(master=self.dialog, parent=self.master, config=self.config, backup=self.backup)
        app.mainloop()

    def ConnectBeads(self):
        self.CloseChildDialog()
        self.AddToHistory('ConnectBeads')
        importlib.reload(beadConnection)

        self.dialog = tk.Toplevel()
        app = beadConnection.ConnectBeadDialog(master=self.dialog, parent=self.master, config=self.config, backup=self.backup)
        app.mainloop()

    def JoinBead(self):
        self.CloseChildDialog()
        self.AddToHistory('JoinBead')
        importlib.reload(joinBead)

        self.dialog = tk.Toplevel()
        app = joinBead.JoinBeadDialog(master=self.dialog, parent=self.master, config=self.config, backup=self.backup)
        app.mainloop()
    
    def RetouchBead(self):
        self.CloseChildDialog()
        self.AddToHistory('BeadRetouch')
        importlib.reload(beadRetouch)

        self.dialog = tk.Toplevel()
        app = beadRetouch.BeadRetouchDialog(master=self.dialog, parent=self.master, backup=self.backup)
        app.mainloop()


    def AddToHistory(self, enumType):
        self.history.Add(enumType)
    
    def DeleteHistories(self):
        self.history.DeleteAll()

    
    
    def Undo(self):
        self.backup.Load()

    def CloseChildDialog(self):
        try:
            self.dialog.destroy()
        except:
            pass
    
    def CloseDialog(self):
        self.CloseChildDialog()
        try:
            self.master.destroy()
        except:
            pass
