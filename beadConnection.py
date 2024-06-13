# coding: shift-jis
from platform import node
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from tkinter.ttk import Separator
import os, sys, importlib
from PIL import Image, ImageTk
from matplotlib.pyplot import text
from hwx import simlab
import numpy as np

SRC_DIR = os.path.dirname(os.path.realpath(__file__))
IMAGE_DIR = (os.path.join(SRC_DIR, 'images'))
PROJECT_DIR = os.path.join(SRC_DIR, "..")
LOG_DIR = os.path.join(PROJECT_DIR, "log")

if not SRC_DIR in sys.path:
    sys.path.append(SRC_DIR)

import basedialog
import simlablib
import simlabutil

class ConnectBeadDialog(basedialog.BaseDialog):
    def __init__(self, master, parent, config, backup):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('ビード連結')
        self.master.resizable(width=False, height=False)
        self.master.attributes('-topmost', True)
        self.master.protocol('WM_DELETE_WINDOW', self.CloseDialog)
        self.config = config
        self.backup = backup

        self.CreateWidgets()
        simlabutil.ClearSelection()
    
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.nb = ttk.Notebook(self.frmTop)
        self.frmStraightConnect = tk.Frame(self.nb)
        self.frmCurveConnect = tk.Frame(self.nb)
        self.frmRightAngleConnect = tk.Frame(self.nb)
        self.frmAlongEdgeConnect = tk.Frame(self.nb)

        self.nb.add(self.frmStraightConnect, text='直線')
        self.nb.add(self.frmCurveConnect, text='曲面')
        self.nb.add(self.frmRightAngleConnect, text='直角')
        self.nb.add(self.frmAlongEdgeConnect, text= '接続線')
        self.nb.bind('<<NotebookTabChanged>>', self.ChangeTab)

        ##
        self.strBeadFaceGroup = 'strBeadFaces'
        self.strEdgeGroup = 'strEdges'
        self.strUpperFaceGroup = 'strUpperFaces'
        self.strLowerFaceGroup = 'strLowerFaces'
        simlablib.DeleteGroups([self.strBeadFaceGroup, self.strEdgeGroup, self.strUpperFaceGroup, self.strLowerFaceGroup])
        self.CreateNoteBook1()

        self.curBeadFaceGroup = 'curBeadFaces'
        self.curEdgeGroup = 'curEdges'
        self.curCylinderFaceGroup = 'curCylinderFace'
        self.curGroundFaceGroup = 'curGroundFace'
        simlablib.DeleteGroups([self.curBeadFaceGroup, self.curEdgeGroup, self.curCylinderFaceGroup, self.curGroundFaceGroup])
        self.CreateNoteBook2()

        groups = ['angleNode_0', 'angleNode_1', 'angleNode_1_1', 'angleNode_2', 'angleNode_2_1']
        simlablib.DeleteGroups(groups)
        self.CreateNoteBook3()

        self.connectedEdgeGroup = 'connectedEdge'
        self.CreateNoteBook4()
        
        self.nb.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)
    
    def ChangeTab(self, event):
        simlabutil.ClearSelection()

        cid = self.nb.index('current')
        if cid == 0:
            simlab.setSelectionFilter('Face')
        elif cid == 1:
            simlab.setSelectionFilter('Face')
        elif cid == 2:
            simlab.setSelectionFilter('Node')
        elif cid == 3:
            simlab.setSelectionFilter('Edge')
    
    def CreateNoteBook4(self):
        tk.Label(self.frmAlongEdgeConnect, text='接続線を選択してビード情報を入力してください。').pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Frame(self.frmAlongEdgeConnect, height=5).pack(side=tk.TOP, anchor=tk.CENTER)
        self.frmCircularWeld = tk.Frame(self.frmAlongEdgeConnect)        
        self.frmCircularWeld.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        self.frmAnyLineFig = tk.Frame(self.frmCircularWeld, width=400)
        self.frmAnyLineFig.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconAnyLine = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'anyLineConnect.png')), master=self.frmAnyLineFig)
        tk.Label(self.frmAnyLineFig, image=self.iconAnyLine).pack(side=tk.LEFT, anchor=tk.W)

        self.btnConnectedEdge = tk.Button(self.frmAnyLineFig, text='エッジ', command=self.SelectConnectedLine, width=10)
        self.btnConnectedEdge.place(x=180, y=180)

        tk.Frame(self.frmAlongEdgeConnect, height=5).pack(side=tk.TOP, anchor=tk.CENTER)
        # tk.Label(self.frmLoopBead, text='ビード断面: ').pack(side=tk.TOP, anchor=tk.NW, padx=5)

        self.frmCircularBeadInfo = tk.Frame(self.frmAlongEdgeConnect)
        self.frmCircularBeadInfo.pack(side=tk.TOP, anchor=tk.W, expand=1, fill=tk.X, padx=5)   
        tk.Label(self.frmCircularBeadInfo, text='ビード情報：').pack(side=tk.TOP, anchor=tk.NW, padx=5)

        self.frmCircularBeadsEndType = tk.Frame(self.frmCircularBeadInfo)
        self.frmCircularBeadsEndType.pack(side=tk.TOP, anchor=tk.NW, padx=5)
        tk.Label(self.frmCircularBeadsEndType, text='末端処理:').pack(side=tk.LEFT, anchor=tk.NW)
        self.varBeadEndType = tk.IntVar()
        self.varBeadEndType.set(1)
        self.chkBeadEndType1 = tk.Radiobutton(self.frmCircularBeadsEndType, text='フラット', variable=self.varBeadEndType, value=1)
        self.chkBeadEndType1.pack(side=tk.LEFT, anchor=tk.NW)
        self.chkBeadEndType2 = tk.Radiobutton(self.frmCircularBeadsEndType, text='ラウンド', variable=self.varBeadEndType, value=2)
        self.chkBeadEndType2.pack(side=tk.LEFT, anchor=tk.NW)

        self.frmCircularBeadRadElem = tk.Frame(self.frmCircularBeadInfo)
        self.frmCircularBeadRadElem.pack(side=tk.TOP, anchor=tk.NW)

        tk.Label(self.frmCircularBeadRadElem, text=' 半径: ').pack(side=tk.LEFT, anchor=tk.NW)
        self.entCircularBeadRadius = tk.Entry(self.frmCircularBeadRadElem, width=7)
        self.entCircularBeadRadius.pack(side=tk.LEFT, anchor=tk.NW)
        circularBeadRadius = self.config.Get('Connect_Connected_Edge_Bead_Radius')
        self.entCircularBeadRadius.insert(tk.END, circularBeadRadius)

        self.frmCircularBeadElemSize = tk.Frame(self.frmCircularBeadRadElem)
        self.frmCircularBeadElemSize.pack(side=tk.LEFT, anchor=tk.NW)
        tk.Label(self.frmCircularBeadElemSize, text=' 要素長: ').pack(side=tk.LEFT, anchor=tk.CENTER)
        self.entCircularBeadElemSize = tk.Entry(self.frmCircularBeadElemSize, width=7)
        self.entCircularBeadElemSize.pack(side=tk.LEFT, anchor=tk.NW)
        circularBeadElemSize = self.config.Get('Connect_Connected_Edge_Bead_Elem_Size')
        self.entCircularBeadElemSize.insert(tk.END, circularBeadElemSize)

        # self.frmRemeshCircleBead = tk.Frame(self.frmCircularBeadInfo)
        # self.frmRemeshCircleBead.pack(side=tk.LEFT, anchor=tk.CENTER)
        self.varCircularBeadRemesh = tk.BooleanVar()
        self.chkCircularBeadRemesh = tk.Checkbutton(self.frmCircularBeadRadElem, text='　再メッシュ　', variable=self.varCircularBeadRemesh)
        self.chkCircularBeadRemesh.pack(side=tk.LEFT, anchor=tk.NW, padx=5)
        self.varCircularBeadRemesh.set(1)

        tk.Frame(self.frmAlongEdgeConnect, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmCtrl4 = tk.Frame(self.frmAlongEdgeConnect)
        self.frmCtrl4.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)

        self.btnCircularBeadWeld = tk.Button(self.frmCtrl4, text=' 作成 ', compound=tk.LEFT, command = self.ExecuteCircularBeadWeld, width=10)
        self.btnCircularBeadWeld.pack(side=tk.LEFT, anchor=tk.NW)        

        self.btnUndo4 = tk.Button(self.frmCtrl4, text=' 戻す ', compound=tk.LEFT, command=self.Undo4, width=10)
        self.btnUndo4.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo4)

        self.btnClose = tk.Button(self.frmCtrl4, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=10)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)
    
    def SelectConnectedLine(self):
        edge = simlab.getSelectedEntities('EDGE')
        if len(edge) == 0:
            messagebox.showinfo('情報','エッジを選択した後、ボタンを押してください。')
            return
        
        simlablib.DeleteGroups(self.connectedEdgeGroup)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Edge', edge, self.connectedEdgeGroup)

        self.UpdateButtonFG4()
    
    def ExecuteCircularBeadWeld(self):
        connectedEdge = simlab.getEntityFromGroup(self.connectedEdgeGroup)
        if not connectedEdge:
            messagebox.showinfo('情報','エッジを選択してください。')
            return

        beadRadius = self.entCircularBeadRadius.get()
        if len(beadRadius) == 0:
            messagebox.showinfo('情報','ビード半径を入力してください。')
            return
        try:
            beadRadius = float(beadRadius)
        except ValueError:
            messagebox.showinfo('情報','ビード半径で数字を入力してください。')
            return
        else:
            if beadRadius <= 0.0:
                messagebox.showinfo('情報','ビード半径で０より大きい数字を入力してください。')
                return
    
        beadEndTypeGet = self.varBeadEndType.get()
        
        
        beadElemSize = self.entCircularBeadElemSize.get()
        if len(beadElemSize) == 0:
            messagebox.showinfo('情報','ビード要素長を入力してください。')
            return
        try:
            beadElemSize = float(beadElemSize)
        except ValueError:
            messagebox.showinfo('情報','ビード要素長で数字を入力してください。')
            return
        else:
            if beadElemSize <= 0.0:
                messagebox.showinfo('情報','ビード要素長で０より大きい数字を入力してください。')
                return
        
        remeshChecked = self.varCircularBeadRemesh.get()
        
        allModelNames = simlab.getAllRootModelNames('FEM')
        if len(allModelNames) > 1:
            messagebox.showinfo('情報','モデル名が複数あります。マージして一個にしてください。')
            return
        elif len(allModelNames) == 0:
            messagebox.showinfo('情報','FEモデルを作成してください。')
            return
        
        self.backup.Save('ConnectAlongEdge')
        modelName = simlab.getModelName('FEM')

        simlablib.UpdateModel()

        beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        if beadEndTypeGet == 1:
            CreateWeldBead=''' <CreateWeldBead UUID="094b6bc4-9494-4d67-a17d-ae3d0499f3f7">
            <GuideEdges>
            <Entities>  
            <Model>'''+ modelName +'''</Model>
            <Edge>'''+ str(connectedEdge).strip('()''[]') +'''</Edge>
            </Entities>
            </GuideEdges>
            <BeadCrossSection Value="Circular"/>
            <BeadRadius Value="'''+ str(beadRadius) +'''"/>
            <BeadEndType Value="Flat"/>
            <CircularMeshSize Check="1" Value="'''+ str(beadElemSize) +'''"/>
            <CircularNumberOfElements Check="0" Value="2"/>
            <UseExistingMeshInGuideEdge Check="0"/>
            <GuideMeshSize Check="1" Value="'''+ str(beadElemSize) +'''"/>
            </CreateWeldBead>'''
            simlab.execute(CreateWeldBead)
        elif beadEndTypeGet == 2:
            CreateWeldBead=''' <CreateWeldBead UUID="094b6bc4-9494-4d67-a17d-ae3d0499f3f7">
            <GuideEdges>
            <Entities>
            <Model>'''+ modelName +'''</Model>
            <Edge>'''+ str(connectedEdge).strip('()''[]') +'''</Edge>
            </Entities>
            </GuideEdges>
            <BeadCrossSection Value="Circular"/>
            <BeadRadius Value="'''+ str(beadRadius) +'''"/>
            <BeadEndType Value="Round"/>
            <RoundWithinGuideEdge Value="1"/>
            <CircularMeshSize Check="1" Value="'''+ str(beadElemSize) +'''"/>
            <CircularNumberOfElements Check="0" Value="2"/>
            <UseExistingMeshInGuideEdge Check="0"/>
            <GuideMeshSize Check="1" Value="'''+ str(beadElemSize) +'''"/>
            </CreateWeldBead>'''
            simlab.execute(CreateWeldBead)

        afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        beadBody = list(set(afterBodies) - set(beforeBodies))
        if not beadBody:
            messagebox.showinfo('情報','ビード作成に失敗しました。')
            return
        
        beadName = getUniqueBeadName(modelName)
        simlablib.RenameBody(modelName, beadBody, beadName)

        adjBodyGroup = 'Adjacent_Bodies'
        simlablib.DeleteGroups(adjBodyGroup)
        searchAdjacentBodies(modelName, beadName, tol=1e-1)
        adjBodies = list(simlab.getBodiesFromGroup(adjBodyGroup))

        if beadName in adjBodies:
            adjBodies.remove(beadName)
        
        elemGroup = 'penetratingElemGroup'
        simlablib.DeleteGroups(elemGroup)
        showPenetratingElements(modelName, adjBodies, elemGroup)
        peneElems = simlab.getEntityFromGroup(elemGroup)

        bodyGroup = 'bodyGroup'
        simlablib.DeleteGroups(bodyGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Element', peneElems, 'Body', bodyGroup)
        weldBodies = simlab.getBodiesFromGroup(bodyGroup)

        joinBeadWithWeldBodies(modelName, weldBodies, beadName)

        try:
            aspectRatio = float(self.config.Get('Aspect_Ratio'))
        except ValueError:
            aspectRatio = 10

        if remeshChecked:
            sharedFaceGroup = 'Shared Faces'
            simlablib.DeleteGroups(sharedFaceGroup)
            sharedEntities(modelName, [beadName])
            sharedFaces = simlab.getEntityFromGroup(sharedFaceGroup)
            
            if sharedFaces:
                remeshFace(modelName, sharedFaces, beadElemSize, aspectRatio)

        meshQualityCleanup(modelName, beadName, aspectRatio)

        simlab.redisplayEntity('Model', modelName)

        simlablib.DeleteGroups(self.connectedEdgeGroup)
        self.UpdateButtonFG4()

    def UpdateButtonFG4(self):
        groups = [self.connectedEdgeGroup]
        widgets = [self.btnConnectedEdge]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)

    def Undo4(self):
        self.backup.Load()
        self.UpdateButtonFG4()

        modelName = simlab.getModelName('CAD')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')

    def CreateNoteBook3(self):
        tk.Label(self.frmRightAngleConnect, text='ビード表面と三角形の内側ノードを選択してください。').pack(side=tk.TOP, anchor=tk.CENTER)

        tk.Frame(self.frmRightAngleConnect, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmAngleConnect = tk.Frame(self.frmRightAngleConnect)        
        self.frmAngleConnect.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        self.frmAngleFig = tk.Frame(self.frmAngleConnect, width=410)
        self.frmAngleFig.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconAngleConnect = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'rightAngleConnect.png')), master=self.frmAngleFig)
        tk.Label(self.frmAngleFig, image=self.iconAngleConnect).pack(side=tk.LEFT, anchor=tk.W)

        self.btnNode1 = tk.Button(self.frmAngleFig, text='1', command= lambda: self.SelectAngleNode('1'), width=5)
        self.btnNode1.place(x=180, y=60)

        self.btnNode1_1 = tk.Button(self.frmAngleFig, text='1_1', command= lambda: self.SelectAngleNode('1_1'), width=5)
        self.btnNode1_1.place(x=40, y=170)

        self.btnNode2 = tk.Button(self.frmAngleFig, text='2', command= lambda: self.SelectAngleNode('2'), width=5)
        self.btnNode2.place(x=260, y=170)

        self.btnNode2_1 = tk.Button(self.frmAngleFig, text='2_1', command= lambda: self.SelectAngleNode('2_1'), width=5)
        self.btnNode2_1.place(x=180, y=250)

        self.btnNode0 = tk.Button(self.frmAngleFig, text='0', command= lambda: self.SelectAngleNode('0'), width=5)
        self.btnNode0.place(x=150, y=150)

        tk.Frame(self.frmRightAngleConnect, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmAngleBeadElemInfo = tk.Frame(self.frmRightAngleConnect)
        self.frmAngleBeadElemInfo.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)

        self.frmRemeshAngleBead = tk.Frame(self.frmAngleBeadElemInfo)
        self.frmRemeshAngleBead.pack(side=tk.LEFT, anchor=tk.CENTER)

        tk.Label(self.frmRemeshAngleBead, text='要素長：').pack(side=tk.LEFT, anchor=tk.CENTER)
        self.entAngleConnectMeshSize = tk.Entry(self.frmRemeshAngleBead, width=10)
        self.entAngleConnectMeshSize.pack(side=tk.LEFT, anchor=tk.NW)
        self.entAngleConnectMeshSize.insert(tk.END, 5.0)

        self.frmAngleBeadConnection =  tk.Frame(self.frmAngleBeadElemInfo)
        self.frmAngleBeadConnection.pack(side=tk.RIGHT, anchor=tk.E)

        tk.Label(self.frmAngleBeadConnection, text='形状：  ').pack(side=tk.LEFT, anchor=tk.CENTER)

        self.varConnectType = tk.IntVar()
        self.varConnectType.set(1)
        self.chkStraightConnect = tk.Radiobutton(self.frmAngleBeadConnection, text='直線    ', variable=self.varConnectType, value=1)
        self.chkStraightConnect.pack(side=tk.LEFT, anchor=tk.CENTER)
        self.chkRoundConnect = tk.Radiobutton(self.frmAngleBeadConnection, text='ラウンド', variable=self.varConnectType, value=2)
        self.chkRoundConnect.pack(side=tk.LEFT, anchor=tk.CENTER)

        tk.Frame(self.frmRightAngleConnect, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmCtrl3 = tk.Frame(self.frmRightAngleConnect)
        self.frmCtrl3.pack(side=tk.BOTTOM, anchor=tk.NE, expand=1, fill=tk.X)

        btnWidth = 10
        self.btnAngleConnect = tk.Button(self.frmCtrl3, text=' 実行 ', compound=tk.LEFT, command=self.ConnectAngle, width=10)
        self.btnAngleConnect.pack(side=tk.LEFT, anchor=tk.NW)

        self.btnUndo3 = tk.Button(self.frmCtrl3, text=' 戻す ', compound=tk.LEFT, command=self.Undo3, width=10)
        self.btnUndo3.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo3)

        self.btnClose3 = tk.Button(self.frmCtrl3, text=' 閉じる ', compound=tk.LEFT, command=self.CloseDialog, width=btnWidth)
        self.btnClose3.pack(side=tk.RIGHT, anchor=tk.E)
    
    def SelectAngleNode(self, num):
        node = simlab.getSelectedEntities('NODE')
        if len(node) == 0:
            messagebox.showinfo('情報','ノードを選択してください。')
            return
        if len(node) != 1:
            messagebox.showinfo('情報','一つのノードを選択してください。')
            return
        
        groupName = 'angleNode_'
        if num == '1':
            groupName += num
        elif num == '1_1':
            groupName += num
        elif num == '2':
            groupName += num
        elif num == '2_1':
            groupName += num
        elif num == '0':
            groupName += num
        
        simlablib.DeleteGroups(groupName)
        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Node', node, groupName)

        self.UpdateButtonFG3()
    
    def ConnectAngle(self):
        allModelNames = simlab.getAllRootModelNames('FEM')
        if len(allModelNames) > 1:
            messagebox.showinfo('情報','モデル名が複数あります。マージして一個にしてください。')
            return
        elif len(allModelNames) == 0:
            messagebox.showinfo('情報','FEモデルを作成してください。')
            return
        modelName = simlab.getModelName('FEM')

        meshSize = self.entAngleConnectMeshSize.get()
        if len(meshSize) == 0:
            messagebox.showinfo('情報','要素長を入力してください。')
            return
        try:
            meshSize = float(meshSize)
        except ValueError:
            messagebox.showinfo('情報','要素長で数字を入力してください。')
            return
        else:
            if meshSize <= 0:
                messagebox.showinfo('情報','要素長で０より大きい数字を入力してください。')
                return
        
        simlablib.UpdateModel()

        self.backup.Save('ConnectRightAngleBead')
        
        groupNames = ['angleNode_0', 'angleNode_1', 'angleNode_1_1', 'angleNode_2', 'angleNode_2_1']

        beadNodes1 = []
        beadNodes2 = []
        nodeDict = dict()
        for thisGroup in groupNames:
            node = simlab.getEntityFromGroup(thisGroup)
            if not node:
                messagebox.showinfo('情報','指定ノードを登録してください。')
                return
            
            if thisGroup in ['angleNode_1', 'angleNode_2']:
                beadNodes1.append(node[0])
            elif thisGroup in ['angleNode_1_1', 'angleNode_2_1']:
                beadNodes2.append(node[0])
            elif thisGroup == 'angleNode_0':
                beadNodes1.append(node[0])
                beadNodes2.append(node[0])

            nodePt = simlab.getNodePositionFromNodeID(modelName, node[0])
            nodeDict[thisGroup] = (node[0], nodePt)
        
        bodyGroup = 'bodyGroup'
        beadBodySet1 = set()
        for thisNode in beadNodes1:
            simlablib.DeleteGroups(bodyGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Node', [thisNode], 'Body', bodyGroup)
            body = set(simlab.getBodiesFromGroup(bodyGroup))
            if not bool(beadBodySet1):
                beadBodySet1 = body
            else:
                beadBodySet1 = beadBodySet1.intersection(body)
        # print(beadBodySet1)

        beadBodySet2 = set()
        for thisNode in beadNodes2:
            simlablib.DeleteGroups(bodyGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Node', [thisNode], 'Body', bodyGroup)
            body = set(simlab.getBodiesFromGroup(bodyGroup))
            if not bool(beadBodySet2):
                beadBodySet2 = body
            else:
                beadBodySet2 = beadBodySet2.intersection(body)
        
        # print(beadBodySet2)
        
        beadBodiesToMerge = list(beadBodySet1.union(beadBodySet2))

        # print(nodeDict)

        connectType = self.varConnectType.get()
        # print('connectType:{}'.format(connectType))

        node0 = nodeDict['angleNode_0'][0]
        node0_pt = np.array(nodeDict['angleNode_0'][1])

        node1 = nodeDict['angleNode_1'][0]
        node1_pt = np.array(nodeDict['angleNode_1'][1])

        node1_1 = nodeDict['angleNode_1_1'][0]
        node1_1_pt = np.array(nodeDict['angleNode_1_1'][1])

        node2 = nodeDict['angleNode_2'][0]
        node2_pt = np.array(nodeDict['angleNode_2'][1])

        node2_1 = nodeDict['angleNode_2_1'][0]
        node2_1_pt = np.array(nodeDict['angleNode_2_1'][1])

        edgeBodies = dict()
        if connectType == 1:
            dist1 = np.linalg.norm(node1_pt - node1_1_pt)
            numElem = max(int(dist1/meshSize), 3)

            beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            createStraightEdgeFromNode(modelName, node1, node1_1, numElem)
            afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            newBody = list(set(afterBodies) - set(beforeBodies))
            for thisBody in newBody:
                edgeBodies['wireBody1-1_1'] = thisBody

            dist2 = np.linalg.norm(node2_pt - node2_1_pt)
            numElem = max(int(dist2/meshSize), 3)
            beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            createStraightEdgeFromNode(modelName, node2, node2_1, numElem)
            afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            newBody = list(set(afterBodies) - set(beforeBodies))
            for thisBody in newBody:
                edgeBodies['wireBody2-2_1'] = thisBody

        elif connectType == 2:
            midPt1 = (node1_pt + node1_1_pt)/2

            v0_mid1 = midPt1 - node0_pt
            dist0_mid1 = np.linalg.norm(v0_mid1)
            n0_mid1 = v0_mid1 / dist0_mid1
            byPt1 = midPt1 + n0_mid1 * dist0_mid1/4
            byNode1 = simlab.getNextNodeID(modelName)
            createNodeByXYZ(modelName, list(byPt1), byNode1)
            numElem = max(int((dist0_mid1 * 3.14 / 2)/meshSize), 4)
            beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            createArcEdge(modelName, node1, node1_1, byNode1, numElem)
            afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            newBody = list(set(afterBodies) - set(beforeBodies))
            for thisBody in newBody:
                edgeBodies['wireBody1-1_1'] = thisBody

            midPt2 = (node2_pt + node2_1_pt) / 2
            v0_mid2 = midPt2 - node0_pt 
            dist0_mid2 = np.linalg.norm(v0_mid2)
            n0_mid2 = v0_mid2 / dist0_mid2
            byPt2 = midPt2 + n0_mid2 * dist0_mid2/4
            byNode2 = simlab.getNextNodeID(modelName)
            createNodeByXYZ(modelName, list(byPt2), byNode2)
            numElem = max(int((dist0_mid2 * 3.14 / 2)/meshSize), 4)
            beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            createArcEdge(modelName, node2, node2_1, byNode2, numElem)
            afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            newBody = list(set(afterBodies) - set(beforeBodies))
            for thisBody in newBody:
                edgeBodies['wireBody2-2_1'] = thisBody
        
        beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        dist = np.linalg.norm(node1_1_pt - node2_pt)
        numLayer = max(int(dist/meshSize), 3)
        createStraightEdgeFromNode(modelName, node1_1, node2, numLayer)
        afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        newBody = list(set(afterBodies) - set(beforeBodies))
        for thisBody in newBody:
            edgeBodies['wireBody1_1-2'] = thisBody
        
        beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        dist = np.linalg.norm(node1_pt - node0_pt)
        numLayer = max(int(dist/meshSize), 3)
        createStraightEdgeFromNode(modelName, node1, node2_1, numLayer)
        afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        newBody = list(set(afterBodies) - set(beforeBodies))
        for thisBody in newBody:
            edgeBodies['wireBody1-2_1'] = thisBody

        beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        # edgeBodyPair = [('wireBody1-1_1', 'wireBody1_1-0'),('wireBody1-2', 'wireBody1-0'),('wireBody1-1_1', 'wireBody1-2'), ('wireBody1_1-0', 'wireBody1_1-2_1'), ('wireBody2_1-0', 'wireBody2-2_1'),('wireBody1_1-2_1', 'wireBody2-2_1')]
        edgeBodyPair = [('wireBody1-1_1', 'wireBody1-2_1'), ('wireBody2-2_1', 'wireBody1-2_1'), ('wireBody1_1-2', 'wireBody1-1_1'), ('wireBody1_1-2', 'wireBody2-2_1')]

        edgeGroup = 'edgeGroup'
        for thisPair in edgeBodyPair:
            try:
                body1 = edgeBodies[thisPair[0]]
                body2 = edgeBodies[thisPair[1]]
            except KeyError:
                continue
            else:
                body1 = simlab.getBodiesWithSubString(modelName, [body1])
                if not body1:
                    continue

                body2 = simlab.getBodiesWithSubString(modelName, [body2])
                if not body2:
                    continue
            
            simlablib.DeleteGroups(edgeGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Body', body1, 'Edge', edgeGroup)
            edge1 = simlab.getEntityFromGroup(edgeGroup)

            simlablib.DeleteGroups(edgeGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Body', body2, 'Edge', edgeGroup)
            edge2 = simlab.getEntityFromGroup(edgeGroup)
            createFaceFromEdges(modelName, edge1, edge2, 2)

        afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        newBody = list(set(afterBodies) - set(beforeBodies))
        beadName = getUniqueBeadName(modelName)
        if len(newBody) > 1:
            mergeBodies(modelName, newBody, beadName)
        else:
            simlablib.RenameBody(modelName, newBody[0], beadName)

        beadCreated = simlab.getBodiesWithSubString(modelName, [beadName])
        if not beadCreated:
            messagebox.showinfo('情報','ビード作成に失敗しました。')
            return
        # nodeEquivalence(modelName, beadCreated)

        faceGroup = 'faceGroup'
        simlablib.DeleteGroups(faceGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Body', beadCreated, 'Face', faceGroup)
        beadFaces = simlab.getEntityFromGroup(faceGroup)

        nodeEquivalence(modelName, beadCreated)
        remeshFace(modelName, beadFaces, meshSize, 10, preserveBoundary=0)

        nodeEquivalence(modelName, beadCreated)

        adjBodyGroup = 'Adjacent_Bodies'
        simlablib.DeleteGroups(adjBodyGroup)
        searchAdjacentBodies(modelName, beadCreated[0], tol=1e-1)
        adjBodies = simlab.getBodiesFromGroup(adjBodyGroup)
        for thisBody in adjBodies:
            joinOverlapFaces(modelName, beadCreated[0], thisBody, remesh=1)

        if beadBodiesToMerge:
            beadBodiesToMerge.append(beadCreated[0])
            mergeBodies(modelName, beadBodiesToMerge, beadCreated[0])
        
        if edgeBodies:
            simlablib.DeleteEntities(modelName, 'Body', edgeBodies)

        nodeGroups = simlab.getGroupsWithSubString('NodeGroup', ['*'])
        simlablib.DeleteGroups(nodeGroups)
        simlablib.DeleteAllOphanNodes()

        self.UpdateButtonFG3()
    
    def UpdateButtonFG3(self):
        groups = ['angleNode_0', 'angleNode_1', 'angleNode_1_1', 'angleNode_2', 'angleNode_2_1']
        widgets = [self.btnNode0, self.btnNode1, self.btnNode1_1, self.btnNode2, self.btnNode2_1]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)

    def Undo3(self):
        self.backup.Load()
        self.UpdateButtonFG3()

        modelName = simlab.getModelName('CAD')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')

    
    def CreateNoteBook2(self):
        tk.Label(self.frmCurveConnect, text='ビード表面とその間の地面、エッジ、円筒面を選択してください。').pack(side=tk.TOP, anchor=tk.CENTER)

        tk.Frame(self.frmCurveConnect, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmCurConnect = tk.Frame(self.frmCurveConnect)        
        self.frmCurConnect.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        self.frmCurFig = tk.Frame(self.frmCurConnect, width=410)
        self.frmCurFig.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconCurConnect = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'curveConnect.png')), master=self.frmCurFig)
        tk.Label(self.frmCurFig, image=self.iconCurConnect).pack(side=tk.LEFT, anchor=tk.W)

        self.btnCurBeadEndFace = tk.Button(self.frmCurFig, text='ビード表面', command= self.SelectCurBeadEndFaces, width=10)
        self.btnCurBeadEndFace.place(x=200, y=230)

        self.btnCurGroundFace = tk.Button(self.frmCurFig, text='地面', command= self.SelectCurGroundFace, width=10)
        self.btnCurGroundFace.place(x=50, y=230)

        self.btnCurCylinderFace = tk.Button(self.frmCurFig, text='円筒面', command= self.SelectCurCylinderFace, width=10)
        self.btnCurCylinderFace.place(x=120, y=35)

        self.btnCurEdge = tk.Button(self.frmCurFig, text='エッジ', command= self.SelectCurEdges, width=10)
        self.btnCurEdge.place(x=250, y=40)
        
        tk.Frame(self.frmCurConnect, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmCurBeadElemInfo = tk.Frame(self.frmCurConnect)
        self.frmCurBeadElemInfo.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        tk.Label(self.frmCurBeadElemInfo, text='要素長：').pack(side=tk.LEFT, anchor=tk.W)
        self.entCurElemSize = tk.Entry(self.frmCurBeadElemInfo, width=7)
        self.entCurElemSize.pack(side=tk.LEFT, anchor=tk.W)
        entElemSize = self.config.Get('Bead_Elem_Size')
        self.entCurElemSize.insert(tk.END, entElemSize)

        tk.Frame(self.frmCurConnect, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmCtrl2 = tk.Frame(self.frmCurConnect)
        self.frmCtrl2.pack(side=tk.BOTTOM, anchor=tk.NE, expand=1, fill=tk.X)

        btnWidth = 10
        self.btnCurConnect = tk.Button(self.frmCtrl2, text=' 実行 ', compound=tk.LEFT, command=self.ConnectCurve, width=10)
        self.btnCurConnect.pack(side=tk.LEFT, anchor=tk.NW)

        self.btnUndo2 = tk.Button(self.frmCtrl2, text=' 戻す ', compound=tk.LEFT, command=self.Undo2, width=10)
        self.btnUndo2.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo2)

        self.btnClose2 = tk.Button(self.frmCtrl2, text=' 閉じる ', compound=tk.LEFT, command=self.CloseDialog, width=btnWidth)
        self.btnClose2.pack(side=tk.RIGHT, anchor=tk.E)
    
    def SelectCurBeadEndFaces(self):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        simlablib.DeleteGroups(self.curBeadFaceGroup)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, self.curBeadFaceGroup)

        self.UpdateButtonFG2()

    def SelectCurGroundFace(self):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        simlablib.DeleteGroups(self.curGroundFaceGroup)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, self.curGroundFaceGroup)

        self.UpdateButtonFG2()

    def SelectCurCylinderFace(self):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        simlablib.DeleteGroups(self.curCylinderFaceGroup)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, self.curCylinderFaceGroup)

        self.UpdateButtonFG2()
    
    def SelectCurEdges(self):
        edge = simlab.getSelectedEntities('EDGE')
        if len(edge) == 0:
            messagebox.showinfo('情報','エッジを選択した後、ボタンを押してください。')
            return
        
        simlablib.DeleteGroups(self.curEdgeGroup)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Edge', edge, self.curEdgeGroup)

        self.UpdateButtonFG2()
    
    def UpdateButtonFG2(self):
        groups = [self.curBeadFaceGroup, self.curEdgeGroup, self.curCylinderFaceGroup, self.curGroundFaceGroup]
        widgets = [self.btnCurBeadEndFace, self.btnCurEdge, self.btnCurCylinderFace, self.btnCurGroundFace]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)

    def Undo2(self):
        self.backup.Load()
        self.UpdateButtonFG2()

        modelName = simlab.getModelName('CAD')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')
    
    def ConnectCurve(self):
        beadEndsFaces = simlab.getEntityFromGroup(self.curBeadFaceGroup)
        if len(beadEndsFaces) != 2:
            messagebox.showinfo('情報','ビード表面を選択してください。')
            return

        curvEdge = simlab.getEntityFromGroup(self.curEdgeGroup)
        if not curvEdge:
            messagebox.showinfo('情報','エッジを選択してください。')
            return

        cylinderFace = simlab.getEntityFromGroup(self.curCylinderFaceGroup)
        if not cylinderFace:
            messagebox.showinfo('情報','円筒面を選択してください。')
            return

        groundFace = simlab.getEntityFromGroup(self.curGroundFaceGroup)
        if not groundFace:
            messagebox.showinfo('情報','地面を選択してください。')
            return
        
        beadElemSize = self.entCurElemSize.get()
        if len(beadElemSize) == 0:
            messagebox.showinfo('情報', 'ビード要素長を入力してください。')
            return
        try:
            beadElemSize = float(beadElemSize)
        except ValueError:
            messagebox.showinfo('情報','ビード要素長で数字を入力してください。')
            return
        else:
            if beadElemSize <= 0:
                messagebox.showinfo('情報', 'ビード要素長で０より大きい数字を入力してください。')
                return
        
        allModelNames = simlab.getAllRootModelNames('FEM')
        if len(allModelNames) > 1:
            messagebox.showinfo('情報','モデル名が複数あります。マージして一個にしてください。')
            return
        elif len(allModelNames) == 0:
            messagebox.showinfo('情報','FEモデルを作成してください。')
            return
        modelName = simlab.getModelName('FEM')

        self.backup.Save('ConnectCurveBead')

        nodeGroup = 'nodeGroup'
        vertexGroup = 'vertexGroup'
        edgeGroup = 'edgeGroup'
        faceGroup = 'faceGroup'
        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', beadEndsFaces, 'Edge', edgeGroup)
        beadEdges = simlab.getEntityFromGroup(edgeGroup)
        splitEdgeByAngle(modelName, beadEdges)
        beadEdges = simlab.getEntityFromGroup(edgeGroup)

        faceNormalDict = dict()
        for thisFace in beadEndsFaces:
            simlablib.DeleteGroups(faceGroup)
            simlablib.CreateGroup(modelName, 'Face', [thisFace], faceGroup)
            thisNormal = simlab.getNormalFromFaceGroup(faceGroup)
            if not thisNormal:
                messagebox.showinfo('情報','ビードが平面にしてください。')
                return
            faceNormalDict[thisFace] = thisNormal
        
        #print('faceNormalDict:{}'.format(faceNormalDict))
        
        beadFaceVertexNodeDict = dict()
        # allBeadVertexNodes = []
        for thisFace in beadEndsFaces:
            simlablib.DeleteGroups(vertexGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Face', [thisFace], 'Vertex', vertexGroup)
            beadvertexes = simlab.getEntityFromGroup(vertexGroup)
            if len(beadvertexes)!= 3:
                messagebox.showinfo('情報','三角形ビード面を選択してください。')
                return
            beadVertexNodes = []
            for thisVertex in beadvertexes:
                simlablib.DeleteGroups(nodeGroup)
                thisVertexNode = getVertexNode(modelName, thisVertex, nodeGroup)
                beadVertexNodes.append(thisVertexNode[0])
            beadFaceVertexNodeDict[thisFace] = beadVertexNodes
            # allBeadVertexNodes.extend(beadVertexNodes)

        #print('beadFaceVertexNodeDict:{}'.format(beadFaceVertexNodeDict))

        beadFaceKeys = list(beadFaceVertexNodeDict.keys())
        #print('beadFaceKeys:{}'.format(beadFaceKeys))

        beadFaceEdgeIntersectingNodeDict = dict()
        simlablib.DeleteGroups(nodeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Edge', curvEdge, 'Node', nodeGroup)
        edgeNodes = simlab.getEntityFromGroup(nodeGroup)        
        # print('edgeNodes:{}'.format(edgeNodes))
        for thisFace in beadFaceKeys:
            thisFaceVertexNodes = beadFaceVertexNodeDict[thisFace]
            intersectingNode = list(set(thisFaceVertexNodes).intersection(set(edgeNodes)))
            if not intersectingNode:
                messagebox.showinfo('情報','エッジとビード面間に共有ノードが見つかりません。')
                return
            beadFaceEdgeIntersectingNodeDict[thisFace] = intersectingNode[0]
        #print('beadFaceEdgeIntersectingNodeDict:{}'.format(beadFaceEdgeIntersectingNodeDict))

        beadFaceCylinderIntersectingNodeDict = dict()
        for thisBeadFace in beadFaceKeys:
            thisBeadVertexNodes = beadFaceVertexNodeDict[thisBeadFace]
            exceptEdgeNodes = list(set(thisBeadVertexNodes) -set([beadFaceEdgeIntersectingNodeDict[thisFace]]))
            cylinderIntersectingNodes = getIntersectingNodeWithFace(modelName, cylinderFace, exceptEdgeNodes)
            if not cylinderIntersectingNodes:
                messagebox.showinfo('情報', '円筒面と共有するビート節点がありません。')
                return
            beadFaceCylinderIntersectingNodeDict[thisBeadFace] = cylinderIntersectingNodes[0]
        
        #print('beadFaceCylinderIntersectingNodeDict:{}'.format(beadFaceCylinderIntersectingNodeDict))

        beadFaceGroundIntersectingNodeDict = dict()
        for thisBeadFace in beadFaceKeys:
            thisBeadVertexNodes = beadFaceVertexNodeDict[thisBeadFace]
            exceptEdgeNodes = list(set(thisBeadVertexNodes) -set([beadFaceEdgeIntersectingNodeDict[thisFace]]))
            groundIntersectingNodes = getIntersectingNodeWithFace(modelName, groundFace, exceptEdgeNodes)
            if not groundIntersectingNodes:
                messagebox.showinfo('情報','地面と共有するビード節点がありません。')
                return
            beadFaceGroundIntersectingNodeDict[thisBeadFace] = groundIntersectingNodes[0]
        
        #print('beadFaceGroundIntersectingNodeDict:{}'.format(beadFaceGroundIntersectingNodeDict))

        #  p3
        #  
        #  
        #  p1      
        #
        #
        #               p2      p4
        
        # check longestBead
        longestLength = 0
        for thisBeadFace in beadFaceKeys:
            gPt = simlab.getNodePositionFromNodeID(modelName, beadFaceGroundIntersectingNodeDict[thisBeadFace])
            ePt = simlab.getNodePositionFromNodeID(modelName, beadFaceEdgeIntersectingNodeDict[thisBeadFace])
            dist = np.linalg.norm(np.array(ePt) - np.array(gPt))
            if dist > longestLength:
                longestLength = dist
        
        # p1,p2
        nodeCrePtOrderDict = dict()
        for thisBeadFace in beadFaceKeys:
            ePt = np.array(simlab.getNodePositionFromNodeID(modelName, beadFaceEdgeIntersectingNodeDict[thisBeadFace]))
            gPt = np.array(simlab.getNodePositionFromNodeID(modelName, beadFaceGroundIntersectingNodeDict[thisBeadFace]))

            unitV = (gPt-ePt) / np.linalg.norm(gPt-ePt)

            pt = list(ePt + longestLength * unitV)

            nodeCrePtOrderDict[thisBeadFace] = (pt, faceNormalDict[thisBeadFace])
        
        pt1, v1 = nodeCrePtOrderDict[beadFaceKeys[0]]
        #print('pt1:{}'.format(pt1))
        #print('v1:{}'.format(v1))
        pt2, v2 = nodeCrePtOrderDict[beadFaceKeys[1]]
        #print('pt2:{}'.format(pt2))
        #print('v2:{}'.format(v2))

        intersectingPt = getIntersectingPointsOfTwoLines(pt1,v1, pt2, v2)
        if not intersectingPt:
            messagebox.showinfo('情報', 'ビード間の交差点を見つかれません。')
            return
        
        #print('intersectingPt:{}'.format(intersectingPt))
        # intersectingNode = simlab.getNextNodeID(modelName)
        # createNodeByCoordinate(modelName, intersectingPt, intersectingNode)

        midP12 = (np.array(pt1) + np.array(pt2)) / 2

        v5 = np.array(intersectingPt) - midP12
        dist = np.linalg.norm(v5)
        n5 = v5 / dist

        byPt = list(midP12 + dist / 2 * n5)

        byNode = simlab.getNextNodeID(modelName)
        createNodeByCoordinate(modelName, byPt, byNode)
        startNode = beadFaceGroundIntersectingNodeDict[beadFaceKeys[0]]
        endNode = beadFaceGroundIntersectingNodeDict[beadFaceKeys[1]]

        edgebodies = []

        beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        createArcByNodes(modelName, startNode, endNode, byNode, beadElemSize)
        afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        edgeBody = list(set(afterBodies) - set(beforeBodies))
        if not edgeBody:
            messagebox.showinfo('情報','エッジ作成にエーラが発生しました。')
            return
        else:
            edgebodies.extend(edgeBody)
        edgeGroup = 'edgeGroup'
        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Body', edgeBody, 'Edge', edgeGroup)
        arcEdge = simlab.getEntityFromGroup(edgeGroup)

        imprintEdgeOnFaceGroup = 'Imprint_EdgeOn_Face'
        simlablib.DeleteGroups(imprintEdgeOnFaceGroup)

        imprintEdgeOnFace(modelName, arcEdge, groundFace)
        imprintedArcEdges = simlab.getEntityFromGroup(imprintEdgeOnFaceGroup)
        if not imprintedArcEdges:
            messagebox.showinfo('情報','arc エッジimprint 失敗')
            return
        
        beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        createStraightEdgeFromNode2(modelName, beadFaceCylinderIntersectingNodeDict[beadFaceKeys[0]], beadFaceCylinderIntersectingNodeDict[beadFaceKeys[1]])
        afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        edgeBody = list(set(afterBodies) - set(beforeBodies))
        if not edgeBody:
            messagebox.showinfo('情報','エッジ作成にエーラが発生しました。')
            return
        else:
            edgebodies.extend(edgeBody)
        
        edgeGroup = 'edgeGroup'
        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Body', edgeBody, 'Edge', edgeGroup)
        strEdge = simlab.getEntityFromGroup(edgeGroup)

        simlablib.DeleteGroups(imprintEdgeOnFaceGroup)
        imprintEdgeOnFace(modelName, strEdge, cylinderFace)
        imprintedStrEdges = simlab.getEntityFromGroup(imprintEdgeOnFaceGroup)
        if not imprintedStrEdges:
            messagebox.showinfo('情報','arc エッジimprint 失敗')
            return

        closeGapBetwenEdgeAndFace(modelName, curvEdge, groundFace)

        groundFace = simlab.getEntityFromGroup(self.curGroundFaceGroup)
        faceToBody = []
        for thisFace in groundFace:
            simlablib.DeleteGroups(edgeGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Face', [thisFace], 'Edge', edgeGroup)
            faceEdges = simlab.getEntityFromGroup(edgeGroup)
            if any(thisEdge in faceEdges for thisEdge in imprintedArcEdges):
                if any(thisEdge in faceEdges for thisEdge in beadEdges):
                    faceToBody.append(thisFace)
        
        cylinderFace = simlab.getEntityFromGroup(self.curCylinderFaceGroup)
        for thisFace in cylinderFace:
            simlablib.DeleteGroups(edgeGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Face', [thisFace], 'Edge', edgeGroup)
            faceEdges = simlab.getEntityFromGroup(edgeGroup)
            if any(thisEdge in faceEdges for thisEdge in imprintedStrEdges):
                if any(thisEdge in faceEdges for thisEdge in beadEdges):
                    faceToBody.append(thisFace)
        
        mcName = 'preserveEdgeMC2'
        simlablib.DeleteMeshControl(mcName)
        preserveFaceEdgeMC(mcName, modelName, faceToBody)
        
        faceToBody.extend(list(beadEndsFaces))

        if not faceToBody:
            messagebox.showinfo('情報','ビード連結に失敗しました。')
            return

        beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        createBodyFromFaces(modelName, faceToBody)
        afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        newBody = list(set(afterBodies) - set(beforeBodies))
        
        if not newBody:
            messagebox.showinfo('情報','ビード連結に失敗しました。')
            return
        
        beadName = getUniqueBeadName(modelName)
        simlablib.RenameBody(modelName, newBody, beadName)

        sharedFaceGroup = 'Shared Faces'
        simlablib.DeleteGroups(sharedFaceGroup)
        sharedEntities(modelName, [beadName])
        sharedFaces = simlab.getEntityFromGroup(sharedFaceGroup)
        try:
            aspectRatio = float(self.config.Get('Aspect_Ratio'))
        except ValueError:
            aspectRatio = 10
        if sharedFaces:
            remeshFace(modelName, sharedFaces, beadElemSize, aspectRatio, preserveBoundary=0)
        
        distance = getDistanceBetweenTwoEdges(modelName, imprintedStrEdges[0], imprintedArcEdges[0])
        #print('distance:{}'.format(distance))
        numLayers = max(int(round(distance / beadElemSize)),2)
        createFaceFromEdges(modelName, imprintedStrEdges, imprintedArcEdges, numLayers)

        meshQualityCleanup(modelName, beadName, aspectRatio)
        
        nodeGroups = simlab.getGroupsWithSubString('NodeGroup',['*'])
        simlablib.DeleteGroups(nodeGroups)
        simlablib.DeleteAllOphanNodes()
        if edgebodies:
            simlablib.DeleteEntities(modelName, 'Body', edgebodies)

        bodyGroup = 'bodyGroup'
        simlablib.DeleteGroups(bodyGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', beadEndsFaces, 'Body', bodyGroup)
        beadBodies = simlab.getBodiesFromGroup(bodyGroup)
        bodiesToMerge = [beadName] + list(beadBodies)
        if len(bodiesToMerge) > 1:
            simlablib.UpdateModel()
            simlablib.MergeBodies(modelName, bodiesToMerge)


        simlab.redisplayEntity('Model', modelName)
        # allBides = simlab.getBodiesWithSubString(modelName, ['*'])
        # simlab.showOrHideEntities(allBides, "Show", modelName, 'Body')

        simlablib.DeleteGroups([self.curBeadFaceGroup, self.curEdgeGroup, self.curCylinderFaceGroup, self.curGroundFaceGroup])
        self.UpdateButtonFG2()

    def CreateNoteBook1(self):
        tk.Label(self.frmStraightConnect, text='ビード表面とその間の面とエッジを選択してください。').pack(side=tk.TOP, anchor=tk.CENTER)

        tk.Frame(self.frmStraightConnect, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmStrConnect = tk.Frame(self.frmStraightConnect)        
        self.frmStrConnect.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        self.frmStrFig = tk.Frame(self.frmStrConnect, width=410)
        self.frmStrFig.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconStrConnect = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'straightConnect.png')), master=self.frmStrFig)
        tk.Label(self.frmStrFig, image=self.iconStrConnect).pack(side=tk.LEFT, anchor=tk.W)

        self.btnStrBeadEndFace = tk.Button(self.frmStrFig, text='ビード表面', command= self.SelectStrBeadEndFaces, width=10)
        self.btnStrBeadEndFace.place(x=90, y=35)

        self.btnStrUpperFaces = tk.Button(self.frmStrFig, text='上面', command= self.SelectStrUpperFaces, width=10)
        self.btnStrUpperFaces.place(x=250, y=35)

        self.btnStrLowerFaces = tk.Button(self.frmStrFig, text='下面', command= self.SelectStrLowerFaces, width=10)
        self.btnStrLowerFaces.place(x=200, y=230)

        self.btnStrEdge = tk.Button(self.frmStrFig, text='エッジ', command= self.SelectStrEdges, width=10)
        self.btnStrEdge.place(x=40, y=230)
        
        tk.Frame(self.frmStraightConnect, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmStrBeadElemInfo = tk.Frame(self.frmStraightConnect)
        self.frmStrBeadElemInfo.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        tk.Label(self.frmStrBeadElemInfo, text='要素長：').pack(side=tk.LEFT, anchor=tk.W)
        self.entStrElemSize = tk.Entry(self.frmStrBeadElemInfo, width=7)
        self.entStrElemSize.pack(side=tk.LEFT, anchor=tk.W)
        entElemSize = self.config.Get('Bead_Elem_Size')
        self.entStrElemSize.insert(tk.END, entElemSize)

        tk.Frame(self.frmStraightConnect, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmCtrl1 = tk.Frame(self.frmStraightConnect)
        self.frmCtrl1.pack(side=tk.BOTTOM, anchor=tk.NE, expand=1, fill=tk.X)

        btnWidth = 10
        self.btnStrConnect = tk.Button(self.frmCtrl1, text=' 実行 ', compound=tk.LEFT, command=self.ConnectStraight, width=10)
        self.btnStrConnect.pack(side=tk.LEFT, anchor=tk.NW)

        self.btnUndo1 = tk.Button(self.frmCtrl1, text=' 戻す ', compound=tk.LEFT, command=self.Undo1, width=10)
        self.btnUndo1.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo1)

        self.btnClose = tk.Button(self.frmCtrl1, text=' 閉じる ', compound=tk.LEFT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.E)
    
    def SelectStrBeadEndFaces(self):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        simlablib.DeleteGroups(self.strBeadFaceGroup)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, self.strBeadFaceGroup)

        self.UpdateButtonFG1()

    def SelectStrUpperFaces(self):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        simlablib.DeleteGroups(self.strUpperFaceGroup)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, self.strUpperFaceGroup)

        self.UpdateButtonFG1()

    def SelectStrLowerFaces(self):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        simlablib.DeleteGroups(self.strLowerFaceGroup)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, self.strLowerFaceGroup)

        self.UpdateButtonFG1()
    
    def SelectStrEdges(self):
        edge = simlab.getSelectedEntities('EDGE')
        if len(edge) == 0:
            messagebox.showinfo('情報','エッジを選択した後、ボタンを押してください。')
            return
        
        simlablib.DeleteGroups(self.strEdgeGroup)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Edge', edge, self.strEdgeGroup)

        self.UpdateButtonFG1()

    def ConnectStraight(self):
        beadEndsFaces = simlab.getEntityFromGroup(self.strBeadFaceGroup)
        if len(beadEndsFaces) != 2:
            messagebox.showinfo('情報','ビード表面を選択してください。')
            return

        edgesBetweenBeads = simlab.getEntityFromGroup(self.strEdgeGroup)
        if not edgesBetweenBeads:
            messagebox.showinfo('情報','エッジを選択してください。')
            return

        upperFaces = simlab.getEntityFromGroup(self.strUpperFaceGroup)
        if not upperFaces:
            messagebox.showinfo('情報','エッジから上面を選択してください。')
            return

        lowerFaces = simlab.getEntityFromGroup(self.strLowerFaceGroup)
        if not lowerFaces:
            messagebox.showinfo('情報','エッジから下面を選択してください。')
            return
        
        beadElemSize = self.entStrElemSize.get()
        if len(beadElemSize) == 0:
            messagebox.showinfo('情報', 'ビード要素長を入力してください。')
            return
        try:
            beadElemSize = float(beadElemSize)
        except ValueError:
            messagebox.showinfo('情報','ビード要素長で数字を入力してください。')
            return
        else:
            if beadElemSize <= 0:
                messagebox.showinfo('情報', 'ビード要素長で０より大きい数字を入力してください。')
                return
        
        allModelNames = simlab.getAllRootModelNames('FEM')
        if len(allModelNames) > 1:
            messagebox.showinfo('情報','モデル名が複数あります。マージして一個にしてください。')
            return
        elif len(allModelNames) == 0:
            messagebox.showinfo('情報','FEモデルを作成してください。')
            return
        modelName = simlab.getModelName('FEM')

        self.backup.Save('ConnectStraightBead')
        
        nodeGroup = 'nodeGroup'
        vertexGroup = 'vertexGroup'
        edgeGroup = 'edgeGroup'

        bodyGroup = 'bodyGroup'
        simlablib.DeleteGroups(bodyGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', beadEndsFaces, 'Body', bodyGroup)
        beadBodies = simlab.getBodiesFromGroup(bodyGroup)

        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', beadEndsFaces, 'Edge', edgeGroup)
        beadEdges = simlab.getEntityFromGroup(edgeGroup)
        splitEdgeByAngle(modelName, beadEdges)
        beadEdges = simlab.getEntityFromGroup(edgeGroup)

        simlablib.DeleteGroups(vertexGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', beadEndsFaces, 'Vertex', vertexGroup)
        beadvertexes = simlab.getEntityFromGroup(vertexGroup)
        if len(beadvertexes)!= 6:
            messagebox.showinfo('情報','三角形ビード面を選択してください。')
            return

        beadVertexNodes = []
        for thisVertex in beadvertexes:
            simlablib.DeleteGroups(nodeGroup)
            thisVertexNode = getVertexNode(modelName, thisVertex, nodeGroup)
            beadVertexNodes.append(thisVertexNode[0])
        
        #print('beadVertexNodes:{}'.format(beadVertexNodes))

        edgeBodies = []
        simlablib.DeleteGroups(nodeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Edge', edgesBetweenBeads, 'Node', nodeGroup)
        edgeNodes = simlab.getEntityFromGroup(nodeGroup)
        #print('edgeNodes:{}'.format(edgeNodes))
        edge1Nodes = list(set(beadVertexNodes).intersection(set(edgeNodes)))
        #print('edge1Nodes:{}'.format(edge1Nodes))
        if len(edge1Nodes) !=2:
            messagebox.showinfo('情報','エッジとビード面間に共有ノードが見つかりません。')
            return
        beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        createStraightEdgeFromNode2(modelName, edge1Nodes[0], edge1Nodes[1])
        afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        edgeBody = list(set(afterBodies) - set(beforeBodies))
        if not edgeBody:
            messagebox.showinfo('情報','エッジ作成にエーラが発生しました。')
            return
        else:
            edgeBodies.extend(edgeBody)
        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Body', edgeBody, 'Edge', edgeGroup)
        edge1 = simlab.getEntityFromGroup(edgeGroup)

        ##############
        simlablib.DeleteGroups(nodeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', lowerFaces, 'Node', nodeGroup)
        lowerNodes = simlab.getEntityFromGroup(nodeGroup)
        intertsectingNodes = set(lowerNodes).intersection(set(beadVertexNodes))
        edge2Nodes = list(intertsectingNodes -set(edge1Nodes))
        if len(edge2Nodes) != 2:
            messagebox.showinfo('情報','ビード面と下面の共有ノードが見つかりません。')
            return
        #print('edge2Nodes:{}'.format(edge2Nodes))
        beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        createStraightEdgeFromNode2(modelName, edge2Nodes[0], edge2Nodes[1])
        afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        edgeBody = list(set(afterBodies) - set(beforeBodies))
        if not edgeBody:
            messagebox.showinfo('情報','エッジ作成にエーラが発生しました。')
            return
        else:
            edgeBodies.extend(edgeBody)
        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Body', edgeBody, 'Edge', edgeGroup)
        edge2 = simlab.getEntityFromGroup(edgeGroup)

        #############

        simlablib.DeleteGroups(nodeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', upperFaces, 'Node', nodeGroup)
        upperNodes = simlab.getEntityFromGroup(nodeGroup)
        intertsectingNodes = set(upperNodes).intersection(set(beadVertexNodes))
        edge3Nodes = list(intertsectingNodes -set(edge1Nodes))
        if len(edge3Nodes) != 2:
            messagebox.showinfo('情報','ビード面と上面の共有ノードが見つかりません。')
            return
        #print('edge3Nodes:{}'.format(edge3Nodes))
        beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        createStraightEdgeFromNode2(modelName, edge3Nodes[0], edge3Nodes[1])
        afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        edgeBody = list(set(afterBodies) - set(beforeBodies))
        if not edgeBody:
            messagebox.showinfo('情報','エッジ作成にエーラが発生しました。')
            return
        else:
            edgeBodies.extend(edgeBody)
        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Body', edgeBody, 'Edge', edgeGroup)
        edge3 = simlab.getEntityFromGroup(edgeGroup)

        dist = getDistanceBetweenTwoFaces(modelName, beadEndsFaces[0], beadEndsFaces[1])

        numLayers = max(int(round(dist / beadElemSize)),2)
        guideEdges = list(edge1) + list(edge2) + list(edge3)
        beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        sweepFace(modelName, beadEndsFaces[0], guideEdges, numLayers)
        afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        newBody = list(set(afterBodies) - set(beforeBodies))

        if not newBody:
            messagebox.showinfo('情報','ビード表面を再メッシュしてください。')
            return
        
        simlablib.DeleteEntities(modelName, 'Body', edgeBodies)
        
        deleteSolidElements(modelName, newBody)

        modifyElementsToTri(modelName, newBody)

        beadName = getUniqueBeadName(modelName)
        simlablib.RenameBody(modelName, newBody, beadName)

        adjBodyGroup = 'Adjacent_Bodies'
        simlablib.DeleteGroups(adjBodyGroup)
        searchAdjacentBodies(modelName, beadName, tol=1e-1)
        adjBodies = simlab.getBodiesFromGroup(adjBodyGroup)
        for thisBody in adjBodies:
            joinOnOvelappingFaces(modelName, beadName, thisBody)
        
        sharedFaceGroup = 'Shared Faces'
        simlablib.DeleteGroups(sharedFaceGroup)
        sharedEntities(modelName, [beadName])
        sharedFaces = simlab.getEntityFromGroup(sharedFaceGroup)
        try:
            aspectRatio = float(self.config.Get('Aspect_Ratio'))
        except ValueError:
            aspectRatio = 10
        if sharedFaces:
            remeshFace(modelName, sharedFaces, beadElemSize, aspectRatio, preserveBoundary=0)
            meshQualityCleanup(modelName, beadName, aspectRatio)
        
        nodeGroups = simlab.getGroupsWithSubString('NodeGroup', ['*'])
        simlablib.DeleteGroups(nodeGroups)
        simlablib.DeleteAllOphanNodes()

        bodiesToMerge = [beadName] + list(beadBodies)
        if len(bodiesToMerge) > 1:
            simlablib.UpdateModel()
            simlablib.MergeBodies(modelName, bodiesToMerge)

        # allBides = simlab.getBodiesWithSubString(modelName, ['*'])
        # simlab.showOrHideEntities(allBides, "Show", modelName, 'Body')
        simlab.redisplayEntity('Model', modelName)

        simlablib.DeleteGroups([self.strBeadFaceGroup, self.strEdgeGroup, self.strUpperFaceGroup, self.strLowerFaceGroup])
        self.UpdateButtonFG1()

    def UpdateButtonFG1(self):
        groups = [self.strBeadFaceGroup, self.strEdgeGroup, self.strUpperFaceGroup, self.strLowerFaceGroup]
        widgets = [self.btnStrBeadEndFace, self.btnStrEdge, self.btnStrUpperFaces, self.btnStrLowerFaces]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)

    def Undo1(self):
        self.backup.Load()
        self.UpdateButtonFG1()

        modelName = simlab.getModelName('CAD')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')

    def CloseDialog(self):
        super().CloseDialog()

def getUniqueBeadName(modelName):
    beadNamePrefix = 'Weld_Body'
    weldBeads = simlab.getBodiesWithSubString(modelName, ['{}_*'.format(beadNamePrefix)])
    maxId = 0
    for thisBead in weldBeads:
        thisBeadId = thisBead.split('_')[-1]
        try:
            thisBeadId = int(thisBeadId)
        except ValueError:
            pass
        else:
            if thisBeadId > maxId:
                maxId = thisBeadId
    
    return '{}_{}'.format(beadNamePrefix, maxId+1)

def getSharedEdge(modelName, bodies):
    SharedEntities=''' <SharedEntities CheckBox="ON" UUID="2dc7ae98-62c3-4926-bbde-d08da48208ad">
    <tag Value="-1"/>
    <Name Value="SharedEntities1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(bodies).replace("'",'"').strip('()''[]') +'''</Body>
    </Entities>
    </SupportEntities>
    <Faces Value="0"/>
    <Edges Value="1"/>
    <Vertices Value="0"/>
    </SharedEntities>'''
    simlab.execute(SharedEntities)

def sharedEntities(modelName, bodies):
    SharedEntities=''' <SharedEntities CheckBox="ON" UUID="2dc7ae98-62c3-4926-bbde-d08da48208ad">
    <tag Value="-1"/>
    <Name Value="SharedEntities2"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(bodies).replace("'",'"').strip('()''[]') +'''</Body>
    </Entities>
    </SupportEntities>
    <Faces Value="1"/>
    <Edges Value="0"/>
    <Vertices Value="0"/>
    </SharedEntities>'''
    simlab.execute(SharedEntities)

# def remeshFace2(modelName, faces, avgElem, aspectRatio, preserveBoundary=1):
#     SurfaceLocalRemesh=''' <NewLocalReMesh UUID="83ab93df-8b5e-4a48-a209-07ed417d75bb">
#     <tag Value="-1"/>
#     <Name Value="NewLocalReMesh1"/>
#     <SupportEntities>
#     <Entities>
#     <Model>'''+ modelName +'''</Model>
#     <Face>'''+ str(faces).strip('()''[]') +'''</Face>
#     </Entities>
#     </SupportEntities>
#     <ElemType Value="0"/>
#     <AverageElemSize Value="'''+ str(avgElem) +'''"/>
#     <MinElemSize Value="'''+ str(avgElem/aspectRatio) +'''"/>
#     <PreserveBoundaryEdges Value="'''+ str(preserveBoundary) +'''"/>
#     <NumberOfSolidLayersToUpdate Value="3"/>
#     <TriOption>
#     <GradeFactor Value="1.5"/>
#     <MaxAnglePerElem Value="45"/>
#     <CurvatureMinElemSize Value="'''+ str(avgElem/2) +'''"/>
#     <AspectRatio Value="'''+ str(aspectRatio) +'''"/>
#     <AdvancedOptions>
#     <MappedMesh Value="0"/>
#     <MeshPattern Value="0"/>
#     <ReMeshSharedEntity Value="0"/>
#     <CADLocalReMesh Value="0"/>
#     </AdvancedOptions>
#     </TriOption>
#     <QuadOption>
#     <QuadMeshType Value="0"/>
#     <HM_Quad_Mesh Value="0">
#     <AverageElementSize Value="0"/>
#     <MinimumElementSize Value=""/>
#     <AllowQuadMeshTransition Checked=""/>
#     <MaximumDeviation Value=""/>
#     <MaximumAngle Value=""/>
#     <FeatureAngle Value=""/>
#     <VertexAngle Value=""/>
#     <MeshType Value=""/>
#     <AlignedMesh Checked=""/>
#     <ProjectToSelectedEntities Checked=""/>
#     </HM_Quad_Mesh>
#     </QuadOption>
#     </NewLocalReMesh>'''
#     simlab.execute(SurfaceLocalRemesh)
#     print(SurfaceLocalRemesh)

def remeshFace(modelName, faces, avgElem, aspectRatio, preserveBoundary=1):
    SurfaceLocalRemesh=''' <NewLocalReMesh UUID="83ab93df-8b5e-4a48-a209-07ed417d75bb">
    <tag Value="-1"/>
    <Name Value="NewLocalReMesh1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(faces).strip('()''[]') +'''</Face>
    </Entities>
    </SupportEntities>
    <ElemType Value="0"/>
    <AverageElemSize Value="'''+ str(avgElem) +'''"/>
    <MinElemSize Value="'''+ str(avgElem/aspectRatio) +'''"/>
    <PreserveBoundaryEdges Value="'''+ str(preserveBoundary) +'''"/>
    <NumberOfSolidLayersToUpdate Value="3"/>
    <TriOption>
    <GradeFactor Value="1.5"/>
    <MaxAnglePerElem Value="45"/>
    <CurvatureMinElemSize Value="'''+ str(avgElem/2) +'''"/>
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

def fillFreeEdgesOfBody(modelName, body):
    FillHoles=''' <FillHole UUID="E9B9EC99-A6C1-4626-99FF-626F38A8CE4F" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value="FillHole2"/>
    <InputOption Value="Mesh"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>"'''+ body +'''",</Body>
    </Entities>
    </SupportEntities>
    <Option Value="0"/>
    <Cylindercal_Face Value="0"/>
    <Single_Face Value="0"/>
    <FillPartialLoop Value="0"/>
    <MeshSize Value="" LocalReMesh="0"/>
    </FillHole>'''
    simlab.execute(FillHoles)

def joinOnOvelappingFaces(modelName, bodyToBeKept, bodyToBeModiFied, tol= 0.1):
    Join=''' <Join UUID="93BDAC5E-9059-42b6-BDC3-EFA346D3DDEC" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value=""/>
    <Pick Value="Join"/>
    <JoinEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>"'''+ bodyToBeKept +'''","'''+ bodyToBeModiFied +'''",</Body>
    </Entities>
    </JoinEntities>
    <AlignEntities ModelIds="" EntityTypes="" Value=""/>
    <PreserveEntities ModelIds="" EntityTypes="" Value=""/>
    <Tolerance Value="'''+ str(tol) +'''"/>
    <JoinType Value="OVERLAPPING_FACES"/>
    <MeshOrShape Value=""/>
    <MeshOption Value=""/>
    <MeshParam Value=""/>
    <SplitFace Value="1"/>
    <LocalRemesh Value="0"/>
    <ShowOrJoin Value="0"/>
    </Join>'''
    simlab.execute(Join)

def createStraightEdgeFromNode2(modelName, node1, node2):
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
    <EquiValence Value="1"/>
    <Output/>
    </EdgeFromNode>'''
    simlab.execute(CreateEdgeFromNodes)

def getVertexNode(modelName, vertex, groupName):
    SelectVertexAssociatedEntities=''' <SelectVertexAssociatedEntities UUID="fc2ece8b-b6e8-4d37-8e27-39a13700fbad">
    <InputVertices Values="">
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Vertex>'''+ str(vertex) +''',</Vertex>
    </Entities>
    </InputVertices>
    <Option Value="Nodes"/>
    <Groupname Value="'''+ groupName +'''"/>
    </SelectVertexAssociatedEntities>'''
    simlab.execute(SelectVertexAssociatedEntities)

    return simlab.getEntityFromGroup(groupName)

def splitEdgeByAngle(modelName, edge, angle=45):
    SplitEdge=''' <SplitEdge UUID="7ECA56CA-94D5-4a21-A88D-59707F8568DC" gda="">
    <Name Value="SplitEdge1"/>
    <tag Value="-1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edge).strip('()''[]') +'''</Edge>
    </Entities>
    </SupportEntities>
    <NodeOrVertex Check="0" Value=""/>
    <Angle Check="1" Value="'''+ str(angle) +'''"/>
    <TopoEdge Check="0" Value=""/>
    <Equivalence Value=""/>
    <MidPoint Check="0" Value=""/>
    <Output/>
    </SplitEdge>'''
    simlab.execute(SplitEdge)

def sweepFace(modelName, face, guideEdges, numLayers):
    BasicSweep=''' <BasicSweep UUID="402e0072-ee41-4146-9beb-df148934f541">
    <tag Value="-1"/>
    <EntityList>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(face).strip('()''[]') +'''</Face>
    </Entities>
    </EntityList>
    <SweepType Value="2"/>
    <SingOrMul Value="1"/>
    <GuideEdgeList>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(guideEdges).strip('()''[]') +'''</Edge>
    </Entities>
    </GuideEdgeList>
    <LayersCheck Value="1"/>
    <NoofLayers Value="'''+ str(numLayers) +'''"/>
    <TetExtrude Value="0"/>
    <ElementTypes Value="0"/>
    <RedoFlag Value=""/>
    <Output/>
    </BasicSweep>'''
    simlab.execute(BasicSweep)

def getDistanceBetweenTwoFaces(modelName, face1, face2):
    DistanceBetweenTwoEntities=''' <DistanceBetweenTwoEntities UUID="53537c0a-6606-4b36-9a95-c05be32f39fc">
    <SupportEntity1>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(face1).strip('()''[]') +''',</Face>
    </Entities>
    </SupportEntity1>
    <SupportEntity2>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(face2).strip('()''[]') +''',</Face>
    </Entities>
    </SupportEntity2>
    </DistanceBetweenTwoEntities>'''
    
    dist,_,_,_ = simlab.measure(DistanceBetweenTwoEntities)

    if dist:
        return dist[0]

    return None

def deleteSolidElements(modelName, body):
    DeleteSolidElements=''' <DeleteSolidElements UUID="c86ce926-2412-4325-a87f-ee6cb66c4de3" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(body).replace("'",'"').strip('()''[]') +'''</Body>
    </Entities>
    </SupportEntities>
    <Output/>
    </DeleteSolidElements>'''
    simlab.execute(DeleteSolidElements)

def modifyElementsToTri(modelName, body):
    ModifyElements=''' <Modify UUID="28706164-e6e5-4544-b4a9-c052c4b6c60f" CheckBox="ON">
    <Name Value="Modify1"/>
    <tag Value="-1"/>
    <Option Value="QUADTOTRI"/>
    <QuadDominant Value="1"/>
    <Entity>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(body).replace("'",'"').strip('()''[]') +'''</Body>
    </Entities>
    </Entity>
    <IdealQuad Value="0"/>
    <UpdateAssociateRBENodes Value="1"/>
    </Modify>'''
    simlab.execute(ModifyElements)

def searchAdjacentBodies(modelName, body, tol=1e-6):
    SelectAdjacentBodies=''' <SelectAdjacentBodies UUID="078de645-1446-470c-9365-d61a1a5c4f47">
    <InputBodies>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>"'''+ body +'''",</Body>
    </Entities>
    </InputBodies>
    <Tolerance Value="1e-06"/>
    <GroupName Value="Adjacent_Bodies"/>
    </SelectAdjacentBodies>'''
    simlab.execute(SelectAdjacentBodies)

def meshQualityCleanup(modelName, bodyName, aspectRatLimit):
    QualityCheck=''' <QCheck UUID="412da11b-2793-4c07-a058-e49f209f007d">
    <ElementType Value="Tri"/>
    <Option Value="Compute"/>
    <Quality LimitValue="'''+ str(aspectRatLimit) +'''" Name="Aspect Ratio" Condition="G Than Or Eq"/>
    <Quality Name="Edge Length" MinimumLimitValue="0.5" Condition="L Than and G Than Or Eq" MaximumLimitValue="100"/>
    <Quality LimitValue="0.2" Name="Height" Condition="L Than"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>"'''+ bodyName +'''",</Body>
    </Entities>
    </SupportEntities>
    </QCheck>'''
    simlab.execute(QualityCheck)

    QualityCheck=''' <QCheck UUID="412da11b-2793-4c07-a058-e49f209f007d">
    <ElementType Value="Tri"/>
    <Option Value="Cleanup"/>
    <Quality LimitValue="'''+ str(aspectRatLimit) +'''" Name="Aspect Ratio" Condition="G Than Or Eq"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>"'''+ bodyName +'''",</Body>
    </Entities>
    </SupportEntities>
    <CleanupType Value="Modify Element"/>
    <PreserveSurfaceSkew Value="55" Check="0"/>
    </QCheck>'''
    simlab.execute(QualityCheck)

    QualityCheck=''' <QCheck UUID="412da11b-2793-4c07-a058-e49f209f007d">
    <ElementType Value="Tri"/>
    <Option Value="Compute"/>
    <Quality LimitValue="'''+ str(aspectRatLimit) +'''" Name="Aspect Ratio" Condition="G Than Or Eq"/>
    <Quality Name="Edge Length" MinimumLimitValue="0.5" Condition="L Than and G Than Or Eq" MaximumLimitValue="100"/>
    <Quality LimitValue="0.2" Name="Height" Condition="L Than"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>"'''+ bodyName +'''",</Body>
    </Entities>
    </SupportEntities>
    </QCheck>'''
    simlab.execute(QualityCheck)

    UpdateModel=''' <UpdateMTopology UUID="D1F56859-D6DB-4431-8699-7E3BE98DA530">
    <tag Value="-1"/>
    <ModelName Value="'''+ modelName +'''"/>
    </UpdateMTopology>'''
    simlab.execute(UpdateModel)

def getIntersectingNodeWithFace(modelName, face, theNodes):
    nodeGroup='nodeGroup'
    simlablib.DeleteGroups(nodeGroup)
    simlablib.SelectAssociatedEntities(modelName, 'Face', face, 'Node', nodeGroup)

    faceNodes = simlab.getEntityFromGroup(nodeGroup)

    return list(set(faceNodes).intersection(set(theNodes)))

def getIntersectingPointsOfTwoLines(p1,v1,p2,v2):
    p1 = np.array(p1)
    p2 = np.array(p2)
    v1 = np.array(v1)
    v2 = np.array(v2)

    denum = np.linalg.norm(np.cross(v1, v2))
    #print('denum:{}'.format(denum))
    if denum < 1e-3:
        return []

    a = np.linalg.norm(np.cross((p2-p1), v2))/denum

    return list(p1 + a * v1)

def createNodeByCoordinate(modelName, coord, nodeId):
    NodeByXYZ=''' <NodeByXYZ UUID="F200B5A2-D615-4d01-8DE2-25596B3B1EB8">
    <tag Value="-1"/>
    <Name Value=""/>
    <LocalCoordinateSystem Value="0"/>
    <Position Value="'''+ str(coord).strip('()''[]') +'''"/>
    <Node Value="'''+ str(nodeId) +'''"/>
    <UniqueNodeId Value="0"/>
    <ModelName Value="'''+ modelName +'''"/>
    </NodeByXYZ>'''
    simlab.execute(NodeByXYZ)

def createArcByNodes(modelName, startNode, endNode, byNode, meshSize):
    CreateEdgeFromNodes=''' <EdgeFromNode UUID="449D18D7-E715-41ce-A640-4AEC18636570" gda="">
    <Name Value="EdgeFromNode1"/>
    <tag Value="-1"/>
    <Mode Value="2"/>
    <StartNode>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Node>'''+ str(startNode) +'''</Node>
    </Entities>
    </StartNode>
    <EndNode>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Node>'''+ str(endNode) +'''</Node>
    </Entities>
    </EndNode>
    <DefineAxis Value="0"/>
    <Arc Value="1"/>
    <ThirdNode>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Node>'''+ str(byNode) +'''</Node>
    </Entities>
    </ThirdNode>
    <NoOfElemChk Value="0"/>
    <NoOfElements Value="6"/>
    <MeshChk Value="1"/>
    <MeshSize Value="'''+ str(meshSize) +'''"/>
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

def closeGapBetwenEdgeAndFace(modelName, edge, face):
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

def createBodyFromFaces(modelName, face):
    CreateBodyFromFaces=''' <BodyFromFaces UUID="24F7C671-DC40-44e0-9B32-8A22A67F58FA" gda="">
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(face).strip('()''[]') +'''</Face>
    </Entities>
    </SupportEntities>
    <ShareBoundaryEdges Value="1"/>
    <CreateBodyFromFaceOption Value="0"/>
    <CreateBodyForEachGroup Value="false"/>
    <Group Value="" Entity=""/>
    <UseInputBodyName Value="true"/>
    <RedoFlag Value=""/>
    </BodyFromFaces>'''
    simlab.execute(CreateBodyFromFaces)

def preserveFaceEdgeMC(mcName, modelName, faces):
    MeshControls=''' <MeshControl CheckBox="ON" isObject="1" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3">
    <tag Value="-1"/>  
    <MeshControlName Value="'''+ mcName +'''"/>
    <MeshControlType Value="Preserve Entities"/>
    <Entities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(faces).strip('()''[]') +'''</Face>
    </Entities>
    </Entities>
    <Reverse Value="" ModelIds="" EntityTypes=""/>
    <MeshColor Value="255,206,0,"/>
    <BodyMeshControl>
    <ElementType Value="0"/>
    <UseMaxElemSize Value="0"/>
    <AverageElementSize Value="0.0"/>
    <MaxElemSize Value="0.0"/>
    <MinElemSize Value="0.0"/>
    <MaxAnglePerElement Value="45.0"/>
    <CurvatureMinElemSize Value="0.0"/>
    <AspectRatio Value="0.0"/>
    <SurfaceMeshGrading Value="0.0"/>
    <InternalGrading Value="0.0"/>
    <MappedMesh Value="0"/>
    <CoarseMesh Value="0"/>
    <IdentifyFeaturesandMesh Value="0"/>
    </BodyMeshControl>
    <FaceMeshControl>
    <AverageElementSize Value="0.0"/>
    <MergeFace Value="0"/>
    <UseGlobal Value="0"/>
    <MinElemSize Value="0.0"/>
    <MaxAnglePerElement Value="45.0"/>
    <CurvatureMinElemSize Value="0.0"/>
    <AspectRatio Value="0.0"/>
    <SurfaceMeshGrading Value="0.0"/>
    <NoofLayer Value="0"/>
    <Isotropic Value="0"/>
    </FaceMeshControl>
    <EdgeMeshControl>
    <SeedingType Value="0"/>
    <UseNumElemes Value="0"/>
    <AverageElementSize Value="0.0"/>
    <NumElems Value="0"/>
    <DistributeSeeds Value="0"/>
    <RatioOrMinMaxLength Value="0"/>
    <Ratio Value="0.0"/>
    <BiasNumElems Value="0"/>
    <MinSize Value="0.0"/>
    <MaxSize Value="0.0"/>
    </EdgeMeshControl>
    <FilletMeshControl>
    <LengthAlongFillet Valve="0.0"/>
    <MaxAnglePerElement Value="45.0"/>
    <MinElemSize Value="0.0"/>
    <NumElems Value="0"/>
    <AspectRatio Value="0.0"/>
    <MinRadius Value="0.0"/>
    <MaxRadius Value="0.0"/>
    <FltOption Value="0"/>
    </FilletMeshControl>
    <CylinderMeshControl>
    <AxialElemSize Value="0.0"/>
    <CirMeshSeeds Value="0"/>
    <CirElemSize Value="0.0"/>
    <AssignCylRadiusRange Value="0"/>
    <MinRadius Value="0.0"/>
    <MaxRadius Value="0.0"/>
    </CylinderMeshControl>
    <WasherMeshControl>
    <OptionToDefWasher Value="0"/>
    <RatioOfOuterToInnerRadius Value="0.0"/>
    <WasherWidth Value="0.0"/>
    <OuterRadus Value="0.0"/>
    <NumLayers Value="0"/>
    <AssignCirRadiusRange Value="0"/>
    <MinRadius Value="0.0"/>
    <MaxRadius Value="0.0"/>
    <AverageSize Value="0.0" Check="0"/>
    </WasherMeshControl>
    <ValveSeatPocket>
    <CylAxis Value="0.0"/>
    <DiscRadial Value="0.0"/>
    <AngularDiv Value="0.0"/>
    <PreserveChamfer Value="0"/>
    </ValveSeatPocket>
    <RegionMeshControl>
    <RegionType Value="0"/>
    <DefineInsideRegion Value="0"/>
    <AverageElementSize Value="0.0"/>
    <MinElemSize Value="0.0"/>
    <MaxAnglePerElement Value="45.0"/>
    <CurvatureMinElemSize Value="0.0"/>
    <AspectRatio Value="10.0"/>
    <SurfaceMeshGrading Value="0.0"/>
    <BreakOptions Value="0"/>
    <RType Value="0"/>
    <CreateInternalFace Value="0"/>
    <CuboidRegData/>
    <CylinderRegData/>
    <PlaneRegData/>
    <SphereRegData/>
    <ConeRegData/>
    </RegionMeshControl>
    <IncludeMeshControl>
    <RefMesh Value="" ModelIds="" EntityTypes=""/>
    </IncludeMeshControl>
    <ImprintCircle>
    <CentreX Value="0.0"/>
    <CentreY Value="0.0"/>
    <CentreZ Value="0.0"/>
    <Radius Value="1"/>
    <Scale Value="1"/>
    <CircularRadius Value="0.5"/>
    <CircularDivisions Value="20"/>
    </ImprintCircle>
    <IsoLine>
    <UseAxialSize Value="1"/>
    <AxialSize Value="0.0"/>
    <AxialNumElems Value="0"/>
    <UseCirAngle Value="1"/>
    <CirAngle Value="0.0"/>
    <CirNumElems Value="0"/>
    <AspectRatio Value="10"/>
    <MinElemSize Value="0.0"/>
    <MergeFaces Value="0"/>
    <CreateUniformMesh Value="0"/>
    <StartPointPicked Value="0"/>
    <CentreX Value="0.0"/>
    <CentreY Value="0.0"/>
    <CentreZ Value="0.0"/>
    <RevDirection Value="0"/>
    <ExtendLayers Value="0"/>
    </IsoLine>
    <VolumeLayer>
    <InputType Value="0"/>
    <NumTetLayers Value="2.0" Check="0"/>
    <Thickness Value="0.0" Check="0"/>
    <ConcentricLayers Value="0"/>
    </VolumeLayer>
    <SymmetryMeshControl>
    <MasterFace Value="" ModelIds="" EntityTypes=""/>
    <SymmetryFace Value="" ModelIds="" EntityTypes=""/>
    <SymmetryType Value="0"/>
    <MasterPoints Value="" ModelIds="" EntityTypes=""/>
    <SymmetryPoints Value="" ModelIds="" EntityTypes=""/>
    <PointType Value="0"/>
    </SymmetryMeshControl>
    <HardPoints>
    <Geometry Value="0"/>
    <Tolerance Value="0.0"/>
    <DataPoints Value=""/>
    <!-- To specify the csv file path , please uncomment out the below line.   -->
    <!--
    <Hard_Points_File Value="D:/Testing/HardPoints.csv" /> 
            -->
    </HardPoints>
    <PreserveEntities>
    <PreserveType Value="2"/>
    </PreserveEntities>
    <MeshPatterns>
    <MeshPatternType Value="0"/>
    </MeshPatterns>
    <RemoveLogo/>
    <RemoveHoleMeshControl>
    <InputType Value="0"/>
    <AssignHoleRadiusRange Value="0"/>
    <MinRadius Value="0.0"/>
    <MaxRadius Value="0.0"/>
    </RemoveHoleMeshControl>
    <ProximityMeshControl>
    <InputType Value="0"/>
    <ProximityDistance Value="0.0"/>
    <AngleBetweenEntitiesWithInProximity Value="0.0"/>
    <MinimumElemSize Value="0.0"/>
    <MinimumNumLayers Value="0"/>
    </ProximityMeshControl>
    <BoundaryLayer>
    <FirstLayerThickness Value="" Method=""/>
    <TotalNumberOfLayers Value=""/>
    <GrowthMethod Value=""/>
    <GrowthRate Value=""/>
    <LayersWithInitialGrowthRate Value=""/>
    <GrowthRateFactor Value=""/>
    <MaxGrowthRate Value=""/>
    <TerminationPolicy Value=""/>
    <ImprintBLOnAdjacentFaces Value=""/>
    </BoundaryLayer>
    </MeshControl>'''
    simlab.execute(MeshControls)

def getDistanceBetweenTwoEdges(modelName, edge1, edge2):
    DistanceBetweenTwoEntities=''' <DistanceBetweenTwoEntities UUID="53537c0a-6606-4b36-9a95-c05be32f39fc">
    <SupportEntity1>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edge1).strip('()''[]') +''',</Edge>
    </Entities>
    </SupportEntity1>
    <SupportEntity2>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edge2).strip('()''[]') +''',</Edge>
    </Entities>
    </SupportEntity2>
    </DistanceBetweenTwoEntities>'''
    
    dist,_,_,_ = simlab.measure(DistanceBetweenTwoEntities)

    if dist:
        return dist[0]

    return None

def createFaceFromEdges(modelName, edges1, edges2, numLayer):
    CreateFaceFromEdges=''' <FaceUsing2Edges UUID="DDB1E50D-DB65-424c-8E3A-516DD1A7E058" gda="">
    <Name Value="FaceUsing2Edges4"/>
    <tag Value="-1"/>
    <No.OfLayers Value="'''+ str(numLayer) +'''"/>
    <EdgeLoop1>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edges1).strip('()''[]') +'''</Edge>
    </Entities>
    </EdgeLoop1>
    <EdgeLoop2>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edges2).strip('()''[]') +'''</Edge>
    </Entities>
    </EdgeLoop2>
    <FaceOnOneSide Value=""/>
    <FaceOnOtherSide Value=""/>
    <BoundaryEdgeLoop1/>
    <BoundaryEdgeLoop2/>
    <NodeList Value="" ModelIds="" EntityTypes=""/>
    <TriElemOption Value="1"/>
    <UseDirChk Value="0"/>
    <DirPoints Value=""/>
    <Output/>
    </FaceUsing2Edges>'''
    simlab.execute(CreateFaceFromEdges)

def createNonSharedBodyFromFace(modelName, face):
    CreateBodyFromFaces=''' <BodyFromFaces gda="" UUID="24F7C671-DC40-44e0-9B32-8A22A67F58FA">
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(face).strip('()''[]') +'''</Face>
    </Entities>
    </SupportEntities>
    <ShareBoundaryEdges Value="1"/>
    <CreateBodyFromFaceOption Value="2"/>
    <CreateBodyForEachGroup Value="false"/>
    <Group Entity="" Value=""/>
    <UseInputBodyName Value="true"/>
    <RedoFlag Value=""/>
    </BodyFromFaces>'''
    simlab.execute(CreateBodyFromFaces)

def rotateBody(modelName, body, axisPt1, axisPt2):
    Rotation=''' <Rotation CheckBox="ON" gda="" UUID="46af1a6e-103c-4803-9846-7e0579bc1dd9">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(body).replace("'",'"').strip('()''[]') +'''</Body>
    </Entities>
    </SupportEntities>
    <Axis Value="ARBITRARY_AXIS"/>
    <Center Value="0.0000, 0.0000, 0.0000"/>
    <AxisDirection>
    <RegionObject>
    <Axis>
        <Pt1 Value="'''+ str(axisPt1).strip('()''[]') +'''"/>
        <Pt2 Value="'''+ str(axisPt2).strip('()''[]') +'''"/>
    </Axis>
    </RegionObject>
    </AxisDirection>
    <Angle Value="90"/>
    <Pattern Value="1"/>
    <WithLBC Value="0"/>
    <No.Of.Instance Value="1"/>
    <Tolerance Value="0.001"/>
    <Merge Value="0"/>
    <LocalCoordinateSystem Value=""/>
    <Output/>
    </Rotation>'''
    simlab.execute(Rotation)

def nodeEquivalence(modelName, body):
    EquivalenceNodes=''' <FemNodeEquivalence UUID="7a5431cd-a2da-4f61-b8ef-9abf3306dd0c">
    <tag Value="-1"/>
    <Name Value="FemNodeEquivalence1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(body).replace("'",'"').strip('()''[]') +'''</Body>
    </Entities>
    </SupportEntities>
    <FaceNodes Value="0"/>
    <EdgeNodes Value="0"/>
    <VertexNodes Value="0"/>
    <RBERadialNodes Value="0"/>
    <SingleBody Value="1"/>
    <RBECenterBarFreeNode Value="0"/>
    <SmallerNodeId Value="1"/>
    <LargerNodeId Value="0"/>
    <ToMidPosition Value="0"/>
    <Tolerance Value="0.1"/>
    <Show Clicked="0" Value=""/>
    <RBECenterOrphanNodeMass Value="0"/>
    <PreserverRbePos Value="1"/>
    <PreserverRbeID Value="1"/>
    <Output/>
    </FemNodeEquivalence>'''
    simlab.execute(EquivalenceNodes)


def mergeBodies(modelName, bodies, toName):
    MergeBodies=''' <BodyMerge UUID="FA9128EE-5E6C-49af-BADF-4016E5622020" gda="">
    <tag Value="-1"/>
    <Name Value="BodyMerge1"/>
    <SupportEntities>
    <Entities>  
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(bodies).replace("'",'"').strip('()''[]') +'''</Body>
    </Entities>
    </SupportEntities>
    <Delete_Shared_Faces Value="0"/>
    <Output_Body_Name Value="'''+ toName +'''"/>
    <RedoFlag Value=""/>
    <Output/>
    </BodyMerge>'''
    simlab.execute(MergeBodies)

def joinOverlapFaces(modelName, bodyToBeKept, bodyToBeModiFied, tol=0.1, remesh= 0):
    Join=''' <Join UUID="93BDAC5E-9059-42b6-BDC3-EFA346D3DDEC" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value=""/>
    <Pick Value="Join"/>
    <JoinEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>"'''+ bodyToBeKept +'''","'''+ bodyToBeModiFied +'''",</Body>
    </Entities>
    </JoinEntities>
    <AlignEntities EntityTypes="" Value="" ModelIds=""/>
    <PreserveEntities EntityTypes="" Value="" ModelIds=""/>
    <Tolerance Value="'''+ str(tol) +'''"/>
    <JoinType Value="OVERLAPPING_FACES"/>
    <MeshOrShape Value=""/>
    <MeshOption Value=""/>
    <MeshParam Value=""/>
    <SplitFace Value="1"/>
    <LocalRemesh Value="'''+ str(remesh) +'''"/>
    <ShowOrJoin Value="0"/>
    </Join>'''
    simlab.execute(Join)

def showPenetratingElements(modelName, bodies, groupName):
    FixIntersections=''' <Intersection UUID="9b88366a-d021-40ea-a7a4-2ff23f864a2d">
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(bodies).replace("'",'"').strip('()''[]') +'''</Body>
    </Entities>
    </SupportEntities>
    <Intersection Value="0"/>
    <OverlappingSurfaces Value="0"/>
    <SurfaceAndEdgeOverlap Value="0"/>
    <NearbySurfaces_NotOverlapping Value="0"/>
    <PenetratingSurfaces Value="1"/>
    <Tolerance Value="1e-06"/>
    <GrpName Name="'''+ groupName +'''" Check="1"/>
    <Operation Value="Show intersection"/>
    <SkipFaceNormal flag="false"/>
    </Intersection>'''
    simlab.execute(FixIntersections)

def joinBeadWithWeldBodies(modelName, weldBodies, weldBead):
    Weld=''' <Weld UUID="a7c9c5f9-034f-4c51-9151-16ad0c237d3e">
    <WeldBodies>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(weldBodies).replace("'",'"').strip('()''[]') +'''</Body>
    </Entities>
    </WeldBodies>
    <WeldBeadBody>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>"'''+ weldBead +'''",</Body>
    </Entities>
    </WeldBeadBody>
    <NonWeldSideBeadFaces/>
    <CreateWeldHeatZone Check="0"/>
    <LocalRemesh Check="0"/>
    <MeshSize Value="1.12975"/>
    <GradeFactor Value="1.5"/>
    </Weld>'''
    simlab.execute(Weld)

def createArcEdge(modelName, startNode, endNode, byNode, numElems):
    CreateEdgeFromNodes=''' <EdgeFromNode gda="" UUID="449D18D7-E715-41ce-A640-4AEC18636570">
    <Name Value="EdgeFromNode11"/>
    <tag Value="-1"/>
    <Mode Value="2"/>
    <StartNode>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Node>'''+ str(startNode) +''',</Node>
    </Entities>
    </StartNode>
    <EndNode>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Node>'''+ str(endNode) +'''</Node>
    </Entities>
    </EndNode>
    <DefineAxis Value="0"/>
    <Arc Value="1"/>
    <ThirdNode>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Node>'''+ str(byNode) +'''</Node>
    </Entities>
    </ThirdNode>
    <NoOfElemChk Value="1"/>
    <NoOfElements Value="'''+ str(numElems) +'''"/>
    <MeshChk Value="0"/>
    <MeshSize Value="1.0"/>
    <Radius Value=""/>
    <EquiValence Value="0"/>
    <Output/>
    </EdgeFromNode>'''
    simlab.execute(CreateEdgeFromNodes)

def createStraightEdgeFromNode(modelName, node1, node2, numElems):
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
    <NoOfElements Value="'''+ str(numElems) +'''"/>
    <MeshChk Value="0"/>
    <MeshSize Value="1.0"/>
    <Radius Value=""/>
    <EquiValence Value="0"/>
    <Output/>
    </EdgeFromNode>'''
    simlab.execute(CreateEdgeFromNodes)

def createNodeByXYZ(modelName, pt, nodeId):
    NodeByXYZ=''' <NodeByXYZ UUID="F200B5A2-D615-4d01-8DE2-25596B3B1EB8">
    <tag Value="-1"/>
    <Name Value=""/>
    <LocalCoordinateSystem Value="0"/>
    <Position Value="'''+ str(pt).strip('()''[]') +'''"/>
    <Node Value="'''+ str(nodeId) +'''"/>
    <UniqueNodeId Value="0"/>
    <ModelName Value="'''+ modelName +'''"/>
    </NodeByXYZ>'''
    simlab.execute(NodeByXYZ)

def uniformEdgeSeedingMC(mcName, modelName, edges, avgElemSize):
    MeshControls=''' <MeshControl CheckBox="ON" isObject="1" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3">
    <tag Value="-1"/>
    <MeshControlName Value="'''+ mcName +'''"/>
    <MeshControlType Value="Edge"/>
    <Entities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edges).strip('()''[]') +'''</Edge>
    </Entities>
    </Entities>
    <Reverse Values="" ModelIds="" Value="" EntityTypes=""/>
    <MeshColor Value=""/>
    <BodyMeshControl>
    <ElementType Value="0"/>
    <UseMaxElemSize Value="0"/>
    <AverageElementSize Value="0.0"/>
    <MaxElemSize Value="0.0"/>
    <MinElemSize Value="0.0"/>
    <MaxAnglePerElement Value="45.0"/>
    <CurvatureMinElemSize Value="0.0"/>
    <AspectRatio Value="0.0"/>
    <SurfaceMeshGrading Value="0.0"/>
    <InternalGrading Value="0.0"/>
    <MappedMesh Value="0"/>
    <CoarseMesh Value="0"/>
    <IdentifyFeaturesandMesh Value="0"/>
    </BodyMeshControl>
    <FaceMeshControl>
    <AverageElementSize Value="0.0"/>
    <MergeFace Value="0"/>
    <UseGlobal Value="0"/>
    <MinElemSize Value="0.0"/>
    <MaxAnglePerElement Value="45.0"/>
    <CurvatureMinElemSize Value="0.0"/>
    <AspectRatio Value="0.0"/>
    <SurfaceMeshGrading Value="0.0"/>
    <NoofLayer Value="0"/>
    <Isotropic Value="0"/>
    </FaceMeshControl>
    <EdgeMeshControl>
    <SeedingType Value="0"/>
    <UseNumElemes Value="0"/>
    <AverageElementSize Value="'''+ str(avgElemSize) +'''"/>
    <NumElems Value="0"/>
    <DistributeSeeds Value="0"/>
    <RatioOrMinMaxLength Value="0"/>
    <Ratio Value="0"/>
    <BiasNumElems Value="0"/>
    <MinSize Value="0"/>
    <MaxSize Value="0"/>
    </EdgeMeshControl>
    <FilletMeshControl>
    <LengthAlongFillet Valve="0.0"/>
    <MaxAnglePerElement Value="45.0"/>
    <MinElemSize Value="0.0"/>
    <NumElems Value="0"/>
    <AspectRatio Value="0.0"/>
    <MinRadius Value="0.0"/>
    <MaxRadius Value="0.0"/>
    <FltOption Value="0"/>
    </FilletMeshControl>
    <CylinderMeshControl>
    <AxialElemSize Value="0.0"/>
    <CirMeshSeeds Value="0"/>
    <CirElemSize Value="0.0"/>
    <AssignCylRadiusRange Value="0"/>
    <MinRadius Value="0.0"/>
    <MaxRadius Value="0.0"/>
    </CylinderMeshControl>
    <WasherMeshControl>
    <OptionToDefWasher Value="0"/>
    <RatioOfOuterToInnerRadius Value="0.0"/>
    <WasherWidth Value="0.0"/>
    <OuterRadus Value="0.0"/>
    <NumLayers Value="0"/>
    <AssignCirRadiusRange Value="0"/>
    <MinRadius Value="0.0"/>
    <MaxRadius Value="0.0"/>
    <AverageSize Value="0.0" Check="0"/>
    </WasherMeshControl>
    <ValveSeatPocket>
    <CylAxis Value="0.0"/>
    <DiscRadial Value="0.0"/>
    <AngularDiv Value="0.0"/>
    <PreserveChamfer Value="0"/>
    </ValveSeatPocket>
    <RegionMeshControl>
    <RegionType Value="0"/>
    <DefineInsideRegion Value="0"/>
    <AverageElementSize Value="0.0"/>
    <MinElemSize Value="0.0"/>
    <MaxAnglePerElement Value="45.0"/>
    <CurvatureMinElemSize Value="0.0"/>
    <AspectRatio Value="10.0"/>
    <SurfaceMeshGrading Value="0.0"/>
    <BreakOptions Value="0"/>
    <RType Value="0"/>
    <CreateInternalFace Value="0"/>
    <CuboidRegData/>
    <CylinderRegData/>
    <PlaneRegData/>
    <SphereRegData/>
    <ConeRegData/>
    </RegionMeshControl>
    <IncludeMeshControl>
    <RefMesh ModelIds="" Value="" EntityTypes=""/>
    </IncludeMeshControl>
    <ImprintCircle>
    <CentreX Value="0.0"/>
    <CentreY Value="0.0"/>
    <CentreZ Value="0.0"/>
    <Radius Value="1"/>
    <Scale Value="1"/>
    <CircularRadius Value="0.5"/>
    <CircularDivisions Value="20"/>
    </ImprintCircle>
    <IsoLine>
    <UseAxialSize Value="1"/>
    <AxialSize Value="0.0"/>
    <AxialNumElems Value="0"/>
    <UseCirAngle Value="1"/>
    <CirAngle Value="0.0"/>
    <CirNumElems Value="0"/>
    <AspectRatio Value="10"/>
    <MinElemSize Value="0.0"/>
    <MergeFaces Value="0"/>
    <CreateUniformMesh Value="0"/>
    <StartPointPicked Value="0"/>
    <CentreX Value="0.0"/>
    <CentreY Value="0.0"/>
    <CentreZ Value="0.0"/>
    <RevDirection Value="0"/>
    <ExtendLayers Value="0"/>
    </IsoLine>
    <VolumeLayer>
    <InputType Value="0"/>
    <NumTetLayers Value="2.0" Check="0"/>
    <Thickness Value="0.0" Check="0"/>
    <ConcentricLayers Value="0"/>
    </VolumeLayer>
    <SymmetryMeshControl>
    <MasterFace ModelIds="" Value="" EntityTypes=""/>
    <SymmetryFace ModelIds="" Value="" EntityTypes=""/>
    <SymmetryType Value="0"/>
    <MasterPoints ModelIds="" Value="" EntityTypes=""/>
    <SymmetryPoints ModelIds="" Value="" EntityTypes=""/>
    <PointType Value="0"/>
    </SymmetryMeshControl>
    <HardPoints>
    <Geometry Value="0"/>
    <Tolerance Value="0.0"/>
    <DataPoints Value=""/>
    <!-- To specify the csv file path , please uncomment out the below line.   -->
    <!--
    <Hard_Points_File Value="D:/Testing/HardPoints.csv" /> 
            -->
    </HardPoints>
    <PreserveEntities>
    <PreserveType Value="0"/>
    </PreserveEntities>
    <MeshPatterns>
    <MeshPatternType Value="0"/>
    </MeshPatterns>
    <RemoveLogo/>
    <RemoveHoleMeshControl>
    <InputType Value="0"/>
    <AssignHoleRadiusRange Value="0"/>
    <MinRadius Value="0.0"/>
    <MaxRadius Value="0.0"/>
    </RemoveHoleMeshControl>
    <ProximityMeshControl>
    <InputType Value="0"/>
    <ProximityDistance Value="0.0"/>
    <AngleBetweenEntitiesWithInProximity Value="0.0"/>
    <MinimumElemSize Value="0.0"/>
    <MinimumNumLayers Value="0"/>
    </ProximityMeshControl>
    <BoundaryLayer>
    <FirstLayerThickness Method="" Value=""/>
    <TotalNumberOfLayers Value=""/>
    <GrowthMethod Value=""/>
    <GrowthRate Value=""/>
    <LayersWithInitialGrowthRate Value=""/>
    <GrowthRateFactor Value=""/>
    <MaxGrowthRate Value=""/>
    <TerminationPolicy Value=""/>
    <ImprintBLOnAdjacentFaces Value=""/>
    </BoundaryLayer>
    </MeshControl>'''
    simlab.execute(MeshControls)






