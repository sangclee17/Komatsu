# coding: shift-jis
import tkinter as tk
from tkinter.constants import NW
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from tkinter.ttk import Separator
import os, sys, importlib
from typing import ValuesView
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

class FaceMergeDialog(basedialog.BaseDialog):
    def __init__(self, master, parent, config):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('面マージ・分割')
        self.master.resizable(width=False, height=False)
        self.master.attributes('-topmost', True)
        self.master.protocol('WM_DELETE_WINDOW', self.CloseDialog)
        self.config = config

        self.referenceFace = 'faceToSplit'
        self.planeNodes = 'planeNodes'
        self.faceToMerge = 'faceToMerge'

        simlablib.DeleteGroups([self.referenceFace, self.planeNodes, self.faceToMerge])
    
        self.CreateWidgets()
        simlab.setSelectionFilter('Face')

    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)
        
        self.nb = ttk.Notebook(self.frmTop)
        self.frmFaceSplit = tk.Frame(self.nb)
        self.frmFaceSplit2 = tk.Frame(self.nb)
        self.frmFaceMerge = tk.Frame(self.nb)
        self.nb.add(self.frmFaceSplit, text='分割１')
        self.nb.add(self.frmFaceSplit2, text='分割２')
        self.nb.add(self.frmFaceMerge, text='マージ')
        self.nb.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)
        self.nb.bind('<<NotebookTabChanged>>', self.ChangeTab)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)
        self.CreateFaceSplit()
        self.CreateFaceSplit2()
        self.CreateMerge()
    
    
    def CreateFaceSplit(self):
        tk.Label(self.frmFaceSplit, text='分割する面と平面を定義するノード3点を\n選んで登録してください。').pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Frame(self.frmFaceSplit, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmFig = tk.Frame(self.frmFaceSplit, width=400)    
        self.frmFig.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        self.iconFaceSplit = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'faceSplit.png')), master=self.frmFig)
        tk.Label(self.frmFig, image=self.iconFaceSplit).pack(side=tk.TOP, anchor=tk.CENTER)
        
        self.btnFace = tk.Button(self.frmFaceSplit, text='面', command=self.SelectFace, width=10)
        self.btnFace.place(x=86, y=300)

        self.btnNodes = tk.Button(self.frmFaceSplit, text='ノード（ｘ３）', command=self.SelectNodes, width=10)
        self.btnNodes.place(x=80, y=90)

        tk.Frame(self.frmFaceSplit, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmSplitCtrl = tk.Frame(self.frmFaceSplit)
        self.frmSplitCtrl.pack(side=tk.BOTTOM, anchor=tk.NE, expand=1, fill=tk.X, padx=5)

        btnWidth = 10
        self.btnClose = tk.Button(self.frmSplitCtrl, text=' 閉じる ', compound=tk.LEFT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)

        self.btnSplit = tk.Button(self.frmSplitCtrl, text='実行', compound=tk.LEFT, command=self.SplitExecute, width=10)
        self.btnSplit.pack(side=tk.LEFT, anchor=tk.NW)   
    
    def SelectFace(self):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        simlablib.DeleteGroups(self.referenceFace)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, self.referenceFace)

        self.UpdateSplitButtonFG()

    def SelectNodes(self):
        nodes = simlab.simlab.getSelectedEntities('Node')
        if len(nodes) != 3:
            messagebox.showinfo('情報','ノード3点を選択後、ボタンを押してください。')
            return
        
        simlablib.DeleteGroups(self.planeNodes)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Node', nodes, self.planeNodes)

        simlabutil.ClearSelection()

        self.UpdateSplitButtonFG()

    def SplitExecute(self):
        refFace = simlab.getEntityFromGroup(self.referenceFace)        
        if not refFace:
            messagebox.showinfo('情報','分割する面を登録してください。')
            return
        
        planeNodes = simlab.getEntityFromGroup(self.planeNodes)
        if not planeNodes:
            messagebox.showinfo('情報','平面を定義するため、ノード3点を登録してください。')
            return

        allModelNames = simlab.getAllRootModelNames('FEM')
        if len(allModelNames) > 1:
            messagebox.showinfo('情報','モデル名が複数あります。マージして一個にしてください。')
            return
        elif len(allModelNames) == 0:
            messagebox.showinfo('情報','FEモデルを作成してください。')
            return

        modelName = simlab.getModelName('FEM')

        pts_3 = []

        for thisNode in planeNodes:

            thisNodePt = simlab.getNodePositionFromNodeID(modelName, thisNode)
            pts_3.append(thisNodePt)
        
        pnt1, pnt2, pnt3 = pts_3

        xVec = np.array(pnt2) - np.array(pnt1)
        yVec = np.array(pnt3) - np.array(pnt1)
        xnVec = xVec / np.linalg.norm(xVec)
        ynVec = yVec / np.linalg.norm(yVec)

        zVec = np.cross(xnVec, ynVec)
        zVecSize = np.linalg.norm(zVec)
        if zVecSize < 1e-3:
            messagebox.showinfo('情報', '直線から平面を定義できません')
            groups = [self.referenceFace, self.planeNodes]
            simlablib.DeleteGroups(groups)
            self.UpdateSplitButtonFG()
            return

        pts_4 = simlabutil.Convert3PointsOnPlaneTo4Points(pts_3)
        breakFace(modelName, refFace, pts_4)

        groups = [self.referenceFace, self.planeNodes]
        simlablib.DeleteGroups(groups)

        self.UpdateSplitButtonFG()
    
    def CreateFaceSplit2(self):
        tk.Label(self.frmFaceSplit2, text='分割する面と一つの端の要素選んで\n距離を入力してください。').pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Frame(self.frmFaceSplit2, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmFig3 = tk.Frame(self.frmFaceSplit2, width=400)
        self.frmFig3.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        self.iconFaceSplit2 = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'faceSplit2.png')), master=self.frmFig3)
        tk.Label(self.frmFig3, image=self.iconFaceSplit2).pack(side=tk.TOP, anchor=tk.CENTER)

        self.btnFacesToSplit = tk.Button(self.frmFig3, text='面', command=self.SelectSplitFace, width=10)
        self.btnFacesToSplit.place(x=188, y=220)

        self.btnElemSel = tk.Button(self.frmFig3, text='要素', command=self.SelectEndElement, width=10)
        self.btnElemSel.place(x=50, y=30)

        tk.Frame(self.frmFaceSplit2, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmSplitParams = tk.Frame(self.frmFaceSplit2)
        self.frmSplitParams.pack(side=tk.TOP, anchor=tk.NW, padx=5, fill=tk.X)

        tk.Label(self.frmSplitParams, text='方向：').pack(side=tk.LEFT, anchor=tk.W)
        self.entSplitDirec = tk.Entry(self.frmSplitParams, width=18)
        self.entSplitDirec.pack(side=tk.LEFT, anchor=tk.W)
        self.entSplitDirec.insert(tk.END, '0.0,0.0,0.0')

        tk.Frame(self.frmSplitParams, width=5).pack(side=tk.LEFT, anchor=tk.W)

        self.btnRevDirec= tk.Button(self.frmSplitParams, text='<=>', command= self.ReverseDirection ,width=3)
        self.btnRevDirec.pack(side=tk.LEFT, anchor=tk.W)
        
        self.entSplitDist = tk.Entry(self.frmSplitParams, width=10)
        self.entSplitDist.pack(side=tk.RIGHT, anchor=tk.E)
        self.entSplitDist.insert(tk.END, 0)
        tk.Label(self.frmSplitParams, text='距離：').pack(side=tk.RIGHT, anchor=tk.E)

        self.frmSplitCtrl2 = tk.Frame(self.frmFaceSplit2, padx=5, pady=5)
        self.frmSplitCtrl2.pack(side=tk.BOTTOM, anchor=tk.NE, expand=1, fill=tk.X)

        self.btnClose3 = tk.Button(self.frmSplitCtrl2, text=' 閉じる ', compound=tk.LEFT, command=self.CloseDialog, width=10)
        self.btnClose3.pack(side=tk.RIGHT, anchor=tk.NE)

        self.btnSplit2 = tk.Button(self.frmSplitCtrl2, text='実行', command=self.SplitExecute2, width=10)
        self.btnSplit2.pack(side=tk.LEFT, anchor=tk.NW)

    def ReverseDirection(self):
        direcStr = self.entSplitDirec.get()

        direcStr_sp = direcStr.split(',')

        if len(direcStr_sp) != 3:
            messagebox.showinfo('情報', '端の要素を登録して法線方向を定義してください。')
            return
        try:
            x = float(direcStr_sp[0])
            y = float(direcStr_sp[1])
            z = float(direcStr_sp[2])
        except ValueError:
            messagebox.showinfo('情報', '要素の法線方向に数字のみを入力してください。')
            return

        x = -1 * x
        y = -1 * y
        z = -1 * z

        direStr = ','.join(str(int(a*100)/100) for a in [x,y,z])

        self.entSplitDirec.delete(0, tk.END)
        self.entSplitDirec.insert(tk.END, direStr)
    
    def SelectSplitFace(self):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        simlablib.DeleteGroups(self.referenceFace)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, self.referenceFace)

        self.UpdateSplitButtonFG2()

    def SelectEndElement(self):
        elem = simlab.getSelectedEntities('ELEMENT')
        if len(elem) != 1:
            messagebox.showinfo('情報', '端の要素を選択してください。')
            return
        
        groupName = 'splitElement'
        simlablib.DeleteGroups(groupName)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Element', elem, groupName)

        simlablib.DeleteGroups('elemNodes')
        simlablib.SelectAssociatedEntities(modelName, 'Element', elem, 'CornerNode', 'elemNodes')

        nodePts = []

        nodes = simlab.getEntityFromGroup('elemNodes')
        if len(nodes) < 3:
            messagebox.showinfo('情報', '少なくとも三つのノードを持つ要素を選択してください。')
            return
        
        for thisNode in nodes:
            pt = simlab.getNodePositionFromNodeID(modelName, thisNode)
            nodePts.append(pt)
        
        pt1, pt2, pt3 = nodePts

        v12 = np.array(pt2) - np.array(pt1)
        v13 = np.array(pt3) - np.array(pt1)

        crss = np.cross(v12, v13)

        v_direc = list(crss / np.linalg.norm(crss))

        direStr = ','.join(str(int(a*100)/100) for a in v_direc)

        self.entSplitDirec.delete(0, tk.END)
        self.entSplitDirec.insert(tk.END, direStr)

        self.UpdateSplitButtonFG2()

        simlabutil.ClearSelection()

    def UpdateSplitButtonFG2(self):
        groups = [self.referenceFace, 'splitElement']
        widgets = [self.btnFacesToSplit, self.btnElemSel]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)

    def SplitExecute2(self):
        
        direcStr = self.entSplitDirec.get()

        direcStr_sp = direcStr.split(',')

        if len(direcStr_sp) != 3:
            messagebox.showinfo('情報', '端の要素を登録して法線方向を定義してください。')
            return
        try:
            x = float(direcStr_sp[0])
            y = float(direcStr_sp[1])
            z = float(direcStr_sp[2])
        except ValueError:
            messagebox.showinfo('情報', '要素の法線方向に数字のみを入力してください。')
            return
        
        splitDist = self.entSplitDist.get()

        try:
            splitDist = float(splitDist)

        except ValueError:
            messagebox.showinfo('情報', '距離に数字のみを入力してください。')
            return
        
        splitElem = simlab.getEntityFromGroup('splitElement')
        if not splitElem:
            messagebox.showinfo('情報','端の要素を選択してください。')
            return
        
        refFace = simlab.getEntityFromGroup(self.referenceFace)        
        if not refFace:
            messagebox.showinfo('情報','分割する面を登録してください。')
            return
        
        modelName = simlab.getModelName('FEM')

        simlablib.DeleteGroups('elemNodes')
        simlablib.SelectAssociatedEntities(modelName, 'Element', splitElem, 'CornerNode', 'elemNodes')
        nodes = simlab.getEntityFromGroup('elemNodes')

        nodePts = list()

        for thisNode in nodes:
            pt = simlab.getNodePositionFromNodeID(modelName, thisNode)
            if len(nodePts) < 3:
                nodePts.append(pt)
        pt1, pt2, pt3 = nodePts
        
        v_direc = np.array([x,y,z])

        v_unit = v_direc / np.linalg.norm(v_direc)

        pt1 = list(np.array(pt1) + v_unit * splitDist)
        pt2 = list(np.array(pt2) + v_unit * splitDist)
        pt3 = list(np.array(pt3) + v_unit * splitDist)

        fourPts = simlabutil.Convert3PointsOnPlaneTo4Points([pt1, pt2, pt3])

        breakFace(modelName, refFace, fourPts)

        groups = [self.referenceFace, 'splitElement']

        simlablib.DeleteGroups(groups)
        self.UpdateSplitButtonFG2()


    def CreateMerge(self):
        tk.Label(self.frmFaceMerge, text='割れた面をマージしてre-meshします。').pack(side=tk.TOP, anchor=tk.NW, fill=tk.X)
        tk.Frame(self.frmFaceMerge, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmFig2 = tk.Frame(self.frmFaceMerge, width=400)    
        self.frmFig2.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        self.iconFaceMerge = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'mergeFace.png')), master=self.frmFig2)
        tk.Label(self.frmFig2, image=self.iconFaceMerge).pack(side=tk.TOP, anchor=tk.CENTER)

        self.btnFacesToMerge = tk.Button(self.frmFaceMerge, text='面（複数）', command=self.SelectFacesToMerge, width=10)
        self.btnFacesToMerge.place(x=150, y=90)

        tk.Frame(self.frmFaceMerge, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmMeshOption = tk.Frame(self.frmFaceMerge, padx=5)
        self.frmMeshOption.pack(side=tk.TOP, anchor=tk.NW, fill=tk.X, expand=1)

        self.varReMesh = tk.BooleanVar()
        self.chkReMesh = tk.Checkbutton(self.frmMeshOption, text='再メッシュ', variable=self.varReMesh, command=self.ReMeshCallback)
        self.chkReMesh.pack(side=tk.LEFT, anchor=tk.NW)

        self.varPreserveBoundaryEdge = tk.BooleanVar()
        self.chkPreserveBoundaryEdge = tk.Checkbutton(self.frmMeshOption, text='境界エッジ保存', variable=self.varPreserveBoundaryEdge, state=tk.DISABLED)
        self.chkPreserveBoundaryEdge.pack(side=tk.LEFT, anchor=tk.NW)

        Separator(self.frmMeshOption, orient='vertical').pack(side=tk.LEFT, anchor=tk.NW, padx=5)

        tk.Label(self.frmMeshOption, text='要素長：').pack(side=tk.LEFT, anchor=tk.NW)
        self.entReMeshSize = tk.Entry(self.frmMeshOption, width=10)
        self.entReMeshSize.pack(side=tk.LEFT, anchor=tk.NW)
        meshSize = self.config.Get('Average_Elem_Size')
        self.entReMeshSize.insert(tk.END, meshSize)
        self.entReMeshSize.config(state='disabled')

        # tk.Frame(self.frmFaceMerge, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmMergeCtrl = tk.Frame(self.frmFaceMerge, padx=5, pady=5)
        self.frmMergeCtrl.pack(side=tk.BOTTOM, anchor=tk.NE, expand=1, fill=tk.X)

        btnWidth = 10
        self.btnClose2 = tk.Button(self.frmMergeCtrl, text=' 閉じる ', compound=tk.LEFT, command=self.CloseDialog, width=btnWidth)
        self.btnClose2.pack(side=tk.RIGHT, anchor=tk.NE)

        self.btnMerge = tk.Button(self.frmMergeCtrl, text='実行', compound=tk.LEFT, command=self.MergeExecute, width=btnWidth)
        self.btnMerge.pack(side=tk.LEFT, anchor=tk.NW)  

    def ReMeshCallback(self):
        isChecked = self.varReMesh.get()
        if isChecked:
            self.entReMeshSize.config(state='normal')
            self.chkPreserveBoundaryEdge.config(state='normal')
        else:
            self.entReMeshSize.config(state='disabled')
            self.chkPreserveBoundaryEdge.config(state='disabled')
    
    def SelectFacesToMerge(self):
        face = simlab.getSelectedEntities('FACE')
        if len(face) <= 1:
            messagebox.showinfo('情報','２面以上を選択した後、ボタンを押してください。')
            return
        
        simlablib.DeleteGroups(self.faceToMerge)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, self.faceToMerge)

        self.UpdateMegrgeButtonFG()

    def MergeExecute(self):
        refFace = simlab.getEntityFromGroup(self.faceToMerge)        
        if not refFace:
            messagebox.showinfo('情報','マージする面を登録してください。')
            return

        if len(refFace) < 2:
            messagebox.showinfo('情報','2面以上を登録してください。')
            return

        reMeshOn = self.varReMesh.get()
        preserveBoundaryGet = False
        if reMeshOn:
            preserveBoundaryGet = self.varPreserveBoundaryEdge.get()
            try:
                elemSize = float(self.entReMeshSize.get())
            except ValueError:
                messagebox.showinfo('情報','再メッシュ要素長を入力してください。')
                return
            else:
                if elemSize <= 0.0:
                    messagebox.showinfo('情報','再メッシュ要素で0より大きい数字を入力してください。')
                    return

        modelName = simlab.getModelName('FEM')
        MergeFaces=''' <MergeFace UUID="D9D604CE-B512-44e3-984D-DF3E64141F8D">
        <tag Value="-1"/>
        <Name Value="MergeFace4"/>
        <SupportEntities>
        <Entities>
        <Model>'''+ modelName +'''</Model>
        <Face>'''+ str(refFace).strip('()''[]') +'''</Face>
        </Entities>
        </SupportEntities>
        <MergeBoundaryEdges Value="1"/>
        <SplitBoundaryEdges Value="0"/>
        <SplitEdgesBasedon Value="0"/>
        <FeatureAngle Value="45"/>
        <RedoFlag Value=""/>
        </MergeFace>'''
        simlab.execute(MergeFaces)
        preserveBoundary = 1 if preserveBoundaryGet else 0
        if reMeshOn:
            triReMesh(self.faceToMerge, elemSize, preserveBoundary=preserveBoundary)

        simlablib.DeleteGroups(self.faceToMerge)

        self.UpdateMegrgeButtonFG()
    
    def ChangeTab(self, event):
        simlabutil.ClearSelection()

        cid = self.nb.index('current')
        if cid == 0:
            simlab.setSelectionFilter('Face')
            simlablib.DeleteGroups([self.referenceFace, self.planeNodes])
        elif cid == 1:
            simlab.setSelectionFilter('Face')
            simlablib.DeleteGroups(['splitElement', 'faceToSplit'])
        elif cid == 2:
            simlab.setSelectionFilter('Face')
    
    def UpdateMegrgeButtonFG(self):
        groups = [self.faceToMerge]
        widgets = [self.btnFacesToMerge]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)
    
    def UpdateSplitButtonFG(self):
        groups = [self.referenceFace, self.planeNodes]
        widgets = [self.btnFace, self.btnNodes]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)
    
    def CloseDialog(self):
        groups = [self.referenceFace, self.planeNodes]
        simlablib.DeleteGroups(groups)
        super().CloseDialog()

def breakFace(modelName, face, pts):
    pt1, pt2, pt3, pt4 = pts
    BreakBody=''' <Break UUID="ccdd6ef0-aaff-4594-850d-886c733cbc2f">
    <tag Value="-1"/>
    <Name Value="Break1"/>
    <Type Value="1"/>
    <PlaneBreak>
    <CreateInternalFace Value="0"/>
    <BreakBodies Value="1"/>
    <CreateSheetBodyFromCutSection Value="0"/>
    <PlanePoints Value=""/>
    <Entity>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(face).strip('()''[]') +'''</Face>
    </Entities>
    </Entity>
    <Mode value="" Value="1"/>
    <RegionObject>
    <Plane>
    <Finite Value="0"/>
    <Pt1 Value="'''+ str(pt1).strip('()''[]') +'''"/>
    <Pt2 Value="'''+ str(pt2).strip('()''[]') +'''"/>
    <Pt3 Value="'''+ str(pt3).strip('()''[]') +'''"/>
    <Pt4 Value="'''+ str(pt4).strip('()''[]') +'''"/>
    </Plane>
    </RegionObject>
    </PlaneBreak>
    <CylBreak>
    <CreateInternalFace Value="0"/>
    <BreakBodies Value="0"/>
    <Entity Value=""/>
    <Retain Value=""/>
    </CylBreak>
    <BoxBreak>
    <BreakOption Value="0"/>
    <Entity Value=""/>
    </BoxBreak>
    <PolyBreak>
    <Mode Value=""/>
    <TargetEntities Value=""/>
    <ToolEntities Value=""/>
    <CreateInternalFace Value="0"/>
    <BreakBodies Value="0"/>
    <Entity Value=""/>
    </PolyBreak>
    <ConeBreak>
    <CreateInternalFace Value="0"/>
    <BreakBodies Value="0"/>
    <Entity Value=""/>
    </ConeBreak>
    <RedoFlag Value=""/>
    <Output/>
    </Break>'''
    simlab.execute(BreakBody)

def triReMesh(groupName, avgElemSize, aspectRatio = 10, preserveBoundary=1):
    SurfaceLocalRemesh=''' <NewLocalReMesh UUID="83ab93df-8b5e-4a48-a209-07ed417d75bb">
    <tag Value="-1"/>
    <Name Value="NewLocalReMesh1"/>
    <SupportEntities>
    <Group>"'''+ groupName +'''",</Group>
    </SupportEntities>
    <ElemType Value="0"/>
    <AverageElemSize Value="'''+ str(avgElemSize) +'''"/>
    <MinElemSize Value="'''+ str(avgElemSize/aspectRatio) +'''"/>
    <PreserveBoundaryEdges Value="'''+ str(preserveBoundary) +'''"/>
    <NumberOfSolidLayersToUpdate Value="3"/>
    <TriOption>
    <GradeFactor Value="1.5"/>
    <MaxAnglePerElem Value="45"/>
    <CurvatureMinElemSize Value="'''+ str(avgElemSize/2) +'''"/>
    <AspectRatio Value="'''+ str(aspectRatio) +'''"/>
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

