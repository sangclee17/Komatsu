# coding: shift-jis
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import os, sys, importlib
from hwx import simlab

SRC_DIR = os.path.dirname(os.path.realpath(__file__))
IMAGE_DIR = (os.path.join(SRC_DIR, 'images'))
PROJECT_DIR = os.path.join(SRC_DIR, "..")
LOG_DIR = os.path.join(PROJECT_DIR, "log")

if not SRC_DIR in sys.path:
    sys.path.append(SRC_DIR)

import basedialog
import simlablib
import simlabutil

class FillGapDialog(basedialog.BaseDialog):
    def __init__(self, master, parent):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('ギャップ埋め')
        self.master.resizable(width=False, height=False)
        self.master.attributes('-topmost', True)
        self.master.protocol('WM_DELETE_WINDOW', self.CloseDialog)

        self.CreateWidgets()
        simlabutil.ClearSelection()

        simlab.setSelectionFilter('Edge')
    
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        tk.Label(self.frmTop, text='SimLab画面がらエッジと面を選択してください。').pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)

        self.btnExcute = tk.Button(self.frmCtrl, text=' 実行 ', compound=tk.LEFT, command=self.fillGapExecute, width=10)
        self.btnExcute.pack(side=tk.LEFT, anchor=tk.NW)        

        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=10)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)
    
    def fillGapExecute(self):
        edge = simlab.getSelectedEntities('EDGE')
        if not edge:
            messagebox.showinfo('情報','エッジを選択してください。')
            return
        
        face = simlab.getSelectedEntities('FACE')
        if not face:
            messagebox.showinfo('情報','面を選んでください。')
            return
        
        allModelNames = simlab.getAllRootModelNames('FEM')
        if len(allModelNames) > 1:
            messagebox.showinfo('情報','モデル名が複数あります。マージして一個にしてください。')
            return
        elif len(allModelNames) == 0:
            messagebox.showinfo('情報','FEモデルを作成してください。')
            return

        modelName = simlab.getModelName('FEM')
        
        ImprintEdgesonFaces=''' <ImprintEdgeOnFace pixmap="imprintedgeonface" UUID="26bb695d-621b-4ba9-996e-11d409dfe332">
        <SupportEntities>
        <Entities>
        <Model>'''+ modelName +'''</Model>
        <Face>'''+ str(face).strip('()''[]') +'''</Face>
        <Edge>'''+ str(edge).strip('()''[]') +'''</Edge>
        </Entities>
        </SupportEntities>
        <CloseGap Value="1"/>
        <UseDirection Value="0"/>
        <DirectionPoint Value="0,0,0"/>
        <LocalRemesh Value="0"/>
        </ImprintEdgeOnFace>'''
        simlab.execute(ImprintEdgesonFaces)

    def CloseDialog(self):
        super().CloseDialog()