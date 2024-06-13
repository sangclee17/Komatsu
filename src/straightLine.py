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

class StraightLineDialog(basedialog.BaseDialog):
    def __init__(self, master, parent):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('直線作成')
        self.master.resizable(width=False, height=False)
        self.master.attributes('-topmost', True)
        self.master.protocol('WM_DELETE_WINDOW', self.CloseDialog)

        self.CreateWidgets()
        simlabutil.ClearSelection()
        simlab.setSelectionFilter('Node')
    
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        tk.Label(self.frmTop, text='SimLab画面から、二つのノードと面を選択してください。').pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)

        self.btnExcute = tk.Button(self.frmCtrl, text=' 実行 ', compound=tk.LEFT, command=self.CreateStraightLine, width=10)
        self.btnExcute.pack(side=tk.LEFT, anchor=tk.NW)        

        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=10)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)
    
    def CreateStraightLine(self):
        nodeSelected = simlab.getSelectedEntities('NODE')
        if len(nodeSelected) != 2:
            messagebox.showinfo('情報','ノード2点を選択してください。')
            return
        
        face = simlab.getSelectedEntities('FACE')
        if not face:
            messagebox.showinfo('情報','直線が付けられる面を選んでください。')
            return
        
        allModelNames = simlab.getAllRootModelNames('FEM')
        if len(allModelNames) > 1:
            messagebox.showinfo('情報','モデル名が複数あります。マージして一個にしてください。')
            return
        elif len(allModelNames) == 0:
            messagebox.showinfo('情報','FEモデルを作成してください。')
            return

        modelName = simlab.getModelName('FEM')

        node1, node2 = nodeSelected

        beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        createStraightEdgeFromNode(modelName, node1, node2)
        afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        edgeBody = list(set(afterBodies) - set(beforeBodies))
        if not edgeBody:
            messagebox.showinfo('情報','エッジ作成にエーラが発生しました。')
            return
        
        edgeGroup = 'edgeGroup'
        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Body', edgeBody, 'Edge', edgeGroup)
        edgeToImprint = simlab.getEntityFromGroup(edgeGroup)
        imprintEdgeOnFace(modelName, edgeToImprint, face)

        if edgeBody:
            simlablib.DeleteEntities(modelName, 'Body', edgeBody)

        simlabutil.ClearSelection()

        simlab.setSelectionFilter('Node')

    def CloseDialog(self):
        super().CloseDialog()

def createStraightEdgeFromNode(modelName, node1, node2):
    CreateEdgeFromNodes=''' <EdgeFromNode gda="" UUID="449D18D7-E715-41ce-A640-4AEC18636570">
    <Name Value="EdgeFromNode1"/>
    <tag Value="-1"/>
    <Mode Value="1"/>
    <StartNode>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Node>'''+ str(node1) +'''</Node>
    </Entities>
    </StartNode>
    <EndNode>
    <Entities>  
    <Model>'''+ modelName +'''</Model>
    <Node>'''+ str(node2) +'''</Node>
    </Entities>
    </EndNode>
    <DefineAxis Value="0"/>
    <Arc Value="0"/>
    <ThirdNode Value=""/>
    <NoOfElemChk Value="1"/>
    <NoOfElements Value="1"/>
    <MeshChk Value="0"/>
    <MeshSize Value="1.0"/>
    <Radius Value=""/>
    <EquiValence Value="0"/>
    <Output/>
    </EdgeFromNode>'''
    simlab.execute(CreateEdgeFromNodes)

def imprintEdgeOnFace(modelName, edge, face):
    ImprintEdgesonFaces=''' <ImprintEdgeOnFace pixmap="imprintedgeonface" UUID="26bb695d-621b-4ba9-996e-11d409dfe332">
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(face).strip('()''[]') +'''</Face>
    <Edge>'''+ str(edge).strip('()''[]') +'''</Edge>
    </Entities>
    </SupportEntities>
    <CloseGap Value="0"/>
    <UseDirection Value="0"/>
    <DirectionPoint Value="0,0,0"/>
    <LocalRemesh Value="0"/>
    </ImprintEdgeOnFace>'''
    simlab.execute(ImprintEdgesonFaces)