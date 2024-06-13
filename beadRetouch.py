# coding: shift-jis
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from tkinter.ttk import Separator
import os, sys
from PIL import Image, ImageTk
from hwx import simlab
import numpy as np
import math


SRC_DIR = os.path.dirname(os.path.realpath(__file__))
IMAGE_DIR = (os.path.join(SRC_DIR, 'images'))
PROJECT_DIR = os.path.join(SRC_DIR, "..")
LOG_DIR = os.path.join(PROJECT_DIR, "log")

if not SRC_DIR in sys.path:
    sys.path.append(SRC_DIR)

import basedialog
import simlablib
import simlabutil

class BeadRetouchDialog(basedialog.BaseDialog):
    def __init__(self, master, parent, backup):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('ビード修正')
        self.master.resizable(width=False, height=False)
        self.master.attributes('-topmost', True)
        self.master.protocol('WM_DELETE_WINDOW', self.CloseDialog)
        self.backup = backup

        self.CreateWidgets()
    
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.nb = ttk.Notebook(self.frmTop)
        self.frmCollapseFace = tk.Frame(self.nb, padx=5, pady=5)

        self.nb.add(self.frmCollapseFace, text='面引き')
        self.nb.bind('<<NotebookTabChanged>>', self.ChangeTab)

        self.CreateNoteBook1()

        self.nb.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        groupsToDelete = ['retouchFace', 'preserveEdge']
        simlablib.DeleteGroups(groupsToDelete)
    
    def ChangeTab(self, event):
        simlabutil.ClearSelection()

        cid = self.nb.index('current')
        if cid == 0:
            simlab.setSelectionFilter('FACE')

    def CreateNoteBook1(self):
        tk.Label(self.frmCollapseFace, text='溶接部分に折られた面を広げる機能です。\n対象面と固定エッジを選択してください。').pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmRetouchFig = tk.Frame(self.frmCollapseFace)
        self.frmRetouchFig.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, pady=5)
        self.frmRetouchFigTop = tk.Frame(self.frmRetouchFig, width=400)
        self.frmRetouchFigTop.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconRetouch = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'faceRetouch.png')), master=self.frmRetouchFigTop)
        tk.Label(self.frmRetouchFigTop, image=self.iconRetouch).pack(side=tk.TOP, anchor=tk.CENTER)

        self.btnRetouchFaceSel = tk.Button(self.frmRetouchFigTop, text='対象面', width=10, command= self.SelectRetouchFace)
        self.btnRetouchFaceSel.place(x=220, y=170)

        self.btnRetouchEdgeToKeep = tk.Button(self.frmRetouchFigTop, text='固定エッジ',width=10, command=self.SelectPreserveEdge)
        self.btnRetouchEdgeToKeep.place(x=120, y=45)

        self.frmRetouchParam = tk.Frame(self.frmCollapseFace)
        self.frmRetouchParam.pack(side=tk.TOP, anchor=tk.CENTER, fill=tk.X)

        self.chkRemeshValue = tk.BooleanVar(value=False)
        self.chkRemesh = tk.Checkbutton(self.frmRetouchParam, text='リーメッシュ', command=self.remeshClicked, variable=self.chkRemeshValue)
        self.chkRemesh.pack(side=tk.LEFT, anchor=tk.W)

        tk.Label(self.frmRetouchParam, text=' 要素長：').pack(side=tk.LEFT, anchor=tk.W)

        self.entRemeshElemSize = tk.Entry(self.frmRetouchParam, width=5)
        self.entRemeshElemSize.pack(side=tk.LEFT, anchor=tk.W)
        self.entRemeshElemSize.config(state='readonly')

        tk.Frame(self.frmCollapseFace, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmRetouchCtrl = tk.Frame(self.frmCollapseFace)
        self.frmRetouchCtrl.pack(side=tk.TOP, anchor=tk.CENTER, fill=tk.X, expand=1)

        self.btnRetouchExecute = tk.Button(self.frmRetouchCtrl, text='実行', command=self.ExecuteRetouch, width=10)
        self.btnRetouchExecute.pack(side=tk.LEFT, anchor=tk.NW)

        self.btnRetouchUndo = tk.Button(self.frmRetouchCtrl, text='戻す', command=self.Undo, width=10)
        self.btnRetouchUndo.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnRetouchUndo)

        self.btnRetouchClose = tk.Button(self.frmRetouchCtrl, text='閉じる', command=self.CloseDialog, width=10)
        self.btnRetouchClose.pack(side=tk.RIGHT,anchor=tk.NE)
    
    def remeshClicked(self):
        if self.chkRemeshValue.get():
            self.entRemeshElemSize.config(state='normal')
            self.entRemeshElemSize.insert(0, 4.0)
        else:
            self.entRemeshElemSize.delete(0, tk.END)
            self.entRemeshElemSize.config(state='readonly')
    
    def SelectPreserveEdge(self):
        edge = simlab.getSelectedEntities('EDGE')
        if len(edge) == 0:
            messagebox.showinfo('情報', 'SimLab画面からエッジを選択して、固定エッジボタンを押してください。')
            return
        modelName = simlab.getModelName('FEM')
        groupName = 'preserveEdge'
        simlablib.DeleteGroups(groupName)
        simlablib.CreateGroup(modelName, 'Edge', edge, groupName)

        self.UpdateButton()

    def SelectRetouchFace(self):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報', '面を選択して、対象面のボタンを押してください。')
            return
        modelName = simlab.getModelName('FEM')
        groupName = 'retouchFace'
        simlablib.DeleteGroups(groupName)
        simlablib.CreateGroup(modelName, 'Face', face, groupName)

        self.UpdateButton()

    def ExecuteRetouch(self):
        
        modelName = simlab.getModelName('FEM')

        retouchFace = simlab.getEntityFromGroup('retouchFace')
        if not retouchFace:
            messagebox.showinfo('情報', '対象面を登録してください。')
            return
        
        preserveEdges = simlab.getEntityFromGroup('preserveEdge')
        if not preserveEdges:
            messagebox.showinfo('情報', '固定エッジを登録してください。')
            return
        
        remesh = False
        if self.chkRemeshValue.get():
            remesh = True
            remeshElemSize = self.entRemeshElemSize.get()

            if len(remeshElemSize) == 0:
                messagebox.showinfo('情報', 'リーメッシュの要素長を入力してください。')
                return
            
            try:
                remeshElemSize = float(remeshElemSize)
            except ValueError:
                messagebox.showinfo('情報', 'リーメッシュの要素長で数字だけを入力してください。')
                return
        
        self.backup.Save('CollapseThinFace')
        
        collapseThinFaces(modelName, retouchFace, preserveEdges)

        if not remesh:
            return
        
        retouchFace = simlab.getEntityFromGroup('retouchFace')

        if not retouchFace:
            return
        
        reMeshFace(modelName, retouchFace, remeshElemSize)

        simlablib.DeleteGroups(['retouchFace', 'preserveEdge'])

        self.UpdateButton()        


    def UpdateButton(self):
        groups = ['retouchFace', 'preserveEdge']
        widgets = [self.btnRetouchFaceSel, self.btnRetouchEdgeToKeep]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)

    def Undo(self):
        self.backup.Load()
        self.UpdateButton()

        modelName = simlab.getModelName('FEM')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')

    def CloseDialog(self):
        super().CloseDialog()

def collapseThinFaces(modelName, faces, edges):
    CollapseThinFaces=''' <RemoveThinFaces gda="" UUID="bc643a92-bbd9-48c1-b58c-a0a6b763dfa8">
    <Name Value=""/>
    <tag Value="-1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(faces).strip('()''[]') +'''</Face>
    <Edge>'''+ str(edges).strip('()''[]') +'''</Edge>
    </Entities>
    </SupportEntities>
    <MidLine Value="0"/>
    <PreservedEdges Value="1"/>
    <Output/>
    </RemoveThinFaces>'''
    simlab.execute(CollapseThinFaces)

def reMeshFace(modelName, face, elemSize, preserveBoundaryEdge = 0):
    SurfaceLocalRemesh=''' <NewLocalReMesh UUID="83ab93df-8b5e-4a48-a209-07ed417d75bb">
    <tag Value="-1"/>
    <Name Value="NewLocalReMesh3"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(face).strip('()''[]') +'''</Face>
    </Entities>
    </SupportEntities>
    <ElemType Value="0"/>
    <AverageElemSize Value="'''+ str(elemSize) +'''"/>
    <MinElemSize Value="'''+ str(elemSize/10) +'''"/>
    <PreserveBoundaryEdges Value="'''+ str(preserveBoundaryEdge) +'''"/>
    <NumberOfSolidLayersToUpdate Value="3"/>
    <TriOption>
    <GradeFactor Value="1.5"/>
    <MaxAnglePerElem Value="45"/>
    <CurvatureMinElemSize Value="2"/>
    <AspectRatio Value="10"/>
    <AdvancedOptions>
    <MappedMesh Value="0"/>
    <MeshPattern Value="0"/>
    <ReMeshSharedEntity Value="0"/>
    <CADLocalReMesh Value="0"/>
    </AdvancedOptions>
    </TriOption>
    <QuadOption>
    <QuadMeshType Value="0"/>
    <HM_Quad_Mesh Value="0">
    <AverageElementSize Value="0"/>
    <MinimumElementSize Value=""/>
    <AllowQuadMeshTransition Checked=""/>
    <MaximumDeviation Value=""/>
    <MaximumAngle Value=""/>
    <FeatureAngle Value=""/>
    <VertexAngle Value=""/>
    <MeshType Value=""/>
    <AlignedMesh Checked=""/>
    <ProjectToSelectedEntities Checked=""/>
    </HM_Quad_Mesh>
    </QuadOption>
    </NewLocalReMesh>'''
    simlab.execute(SurfaceLocalRemesh)


