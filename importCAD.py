
# coding: shift-jis

import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import os, sys, importlib
from PIL import ImageTk
from hwx import simlab
import time
import codecs
from pathlib import Path
import re

SRC_DIR = os.path.dirname(os.path.realpath(__file__))
IMAGE_DIR = (os.path.join(SRC_DIR, 'images'))
PROJECT_DIR = os.path.join(SRC_DIR, "..")
LOG_DIR = os.path.join(PROJECT_DIR, "log")
# PARTINFO_DIR = os.path.join(PROJECT_DIR, 'partInfo')

if not SRC_DIR in sys.path:
    sys.path.append(SRC_DIR)

import basedialog
import simlablib

class ImportDialog(basedialog.BaseDialog):
    def __init__(self, master, parent):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('CADインポート')
        self.master.resizable(width=False, height=False)
        self.master.attributes('-topmost', True)
        self.master.protocol('WM_DELETE_WINDOW', self.CloseDialog)

        self.CreateWidgets()
    
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)
        
        self.frmImport = tk.Frame(self.frmTop)
        self.frmImport.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)
        tk.Label(self.frmImport, text='CAD位置：').pack(side=tk.LEFT, anchor=tk.NW)
        # lblCADLoc.config(width=12)
        self.CADPath = tk.StringVar()
        self.entCADSelect = tk.Entry(self.frmImport, textvariable=self.CADPath, width= 40)
        self.entCADSelect.pack(side=tk.LEFT, anchor=tk.NW,padx=5)
        self.iconFolder = ImageTk.PhotoImage(file=(os.path.join(IMAGE_DIR, 'openfolder.gif')))
        self.btnCADPath = tk.Button(self.frmImport, image=self.iconFolder, command=self.SelectCAD,padx=5)
        self.btnCADPath.pack(side=tk.LEFT, anchor=tk.NW)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmOption = tk.Frame(self.frmTop)
        self.frmOption.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)
        # tk.Label(self.frmOption, text='インポートオプション：').pack(side=tk.TOP, anchor=tk.NW)
      
        self.chkDupBody = tk.BooleanVar()
        self.chkDupBody.set(True)

        self.chkBtnSearchDupBodies = tk.Checkbutton(self.frmOption, text='重複ボディ検索', variable = self.chkDupBody)
        self.chkBtnSearchDupBodies.pack(side=tk.TOP, anchor=tk.NW)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)

        self.btnImport = tk.Button(self.frmCtrl, text='インポート', command=self.ExecuteImportCAD, width=10)
        self.btnImport.pack(side=tk.LEFT, anchor=tk.NW)

        self.btnClose = tk.Button(self.frmCtrl, text='閉じる', command=self.CloseDialog, width=10)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NW)

    def ExecuteImportCAD(self):
        fileName = self.entCADSelect.get()
        if len(fileName) == 0:
            tk.messagebox.showinfo('情報','CADパスを指定してください。')
            return
        
        checkBodyDup = self.chkDupBody.get()
        
        ImportParasolid=''' <ImportParasolid Type="Parasolid" gda="" CheckBox="ON" UUID="400d622c-e74a-4f87-bc0b-af51659b9b6d">
        <tag Value="1"/>
        <FileName widget="LineEdit" HelpStr="File name to be imported." Value="'''+ fileName +'''"/>
        <Units HelpStr="Units to which this file is to be imported into" Value="MilliMeter"/>
        <SolidBodyType Value="1"/>
        <SheetBodyType Value="1"/>
        <WireBodyType Value="0"/>
        <ConnectedBodyType Value="0"/>
        <ImportasFacets Value="0"/>
        <Imprint Value="0"/>
        <Groups Value="0"/>
        <Merge Value="0"/>
        <ImportAssemblyStructure Value="0"/>
        <SaveGeometryInDatabase Value="1"/>
        <AddToExistingModel Value="0"/>
        <MassProperties Value="0"/>
        <FileCount value="0" Value="0"/>
        <Output widget="NULL"/>
        <ImportOption Value="1"/>
        <TransXmlFileName Value=""/>
        <TransOutFileName Value=""/>
        </ImportParasolid>'''
        simlab.execute(ImportParasolid)

        modelName = simlab.getModelName('CAD')
        if not modelName:
            return
        
        if checkBodyDup:
            checkDuplicateBodies(modelName, '')
            dupGroup = 'Duplicate_Bodies'
            masterGroup = 'Master_Bodies'
            if simlab.isGroupPresent(dupGroup):
                messagebox.showinfo('情報','＊重複CADボディがあります。ボディグループ中で、{}だけを残して{}のボディをすべて削除してください。'.format(masterGroup, dupGroup))

    def SelectCAD(self):
        fileType = [('Parasolid','*.x_t;*.xmt_txt;*x_b'), ('All files','*.*')]
        initDir = PROJECT_DIR
        if os.path.isfile(self.CADPath.get()):
            initDir = os.path.dirname(self.CADPath.get())         
        
        path = filedialog.askopenfilename(filetypes=fileType, initialdir=initDir)
        if not os.path.isfile(path):
            return
        
        self.CADPath.set(path)
        self.entCADSelect.update()

    def CloseDialog(self):
        super().CloseDialog()

def checkDuplicateBodies(modelName, bodies):
    ShowDuplicate=''' <ShowDuplicateBody UUID="89620faf-0f12-4dbe-831f-99cf15f4f734">
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(bodies).replace("'",'"').strip('()''[]') +'''</Body>
    </Entities>
    </SupportEntities>
    <ShowExact Value="1"/>
    <Compare_Pysical_Prop Value="0"/>
    <CreateSubModel Value="0"/>
    </ShowDuplicateBody>'''
    simlab.execute(ShowDuplicate)
    

        


    
