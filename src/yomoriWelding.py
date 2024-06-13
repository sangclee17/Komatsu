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

class YomoriWeldingDialog(basedialog.BaseDialog):
    def __init__(self, master, parent, config, backup):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('余盛溶接')
        self.master.resizable(width=False, height=False)
        self.master.attributes('-topmost', True)
        self.master.protocol('WM_DELETE_WINDOW', self.CloseDialog)
        self.config = config
        self.backup = backup

        self.refFace1 = 'YomoriWeldingFace1'
        self.cornerNodes = 'YomoriCornerNodes'

        self.loopWEdge = 'YomoriLoopEdge'

        self.CreateWidgets()
    
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.nb = ttk.Notebook(self.frmTop)
        self.frmAngleBead = tk.Frame(self.nb)
        self.frmDonutBead = tk.Frame(self.nb)
        self.frmLoopBead = tk.Frame(self.nb)

        self.nb.add(self.frmAngleBead, text='余盛１')
        self.nb.add(self.frmDonutBead, text='余盛２')
        self.nb.add(self.frmLoopBead, text='ループ')
        self.nb.bind('<<NotebookTabChanged>>', self.ChangeTab)

        self.CreateNoteBook1()
        self.CreateDonutNoteBook()
        self.CreateNoteBook2()

        self.nb.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        groups = [self.refFace1, self.cornerNodes, self.loopWEdge]
        simlablib.DeleteGroups(groups)
    
    def ChangeTab(self, event):
        simlabutil.ClearSelection()

        cid = self.nb.index('current')
        if cid == 0:
            simlab.setSelectionFilter('NODE')
        elif cid == 1:
            simlab.setSelectionFilter('FACE')
        elif cid == 2:
            simlab.setSelectionFilter('EDGELOOP')
    
    def CreateNoteBook2(self):
        tk.Label(self.frmLoopBead, text='エッジを選択してビード情報を入力してください。').pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Frame(self.frmLoopBead, height=5).pack(side=tk.TOP, anchor=tk.CENTER)
        self.frmYomoriLoop = tk.Frame(self.frmLoopBead)        
        self.frmYomoriLoop.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        self.frmLoopFig = tk.Frame(self.frmYomoriLoop, width=400)
        self.frmLoopFig.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconYomoriLoop= ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'yomoriWelding_loop.png')), master=self.frmLoopFig)
        tk.Label(self.frmLoopFig, image=self.iconYomoriLoop).pack(side=tk.LEFT, anchor=tk.W)

        self.btnLoopWEdge = tk.Button(self.frmLoopFig, text='エッジ', command=self.SelectLoopWEdges, width=10)
        self.btnLoopWEdge.place(x=290, y=140)

        tk.Frame(self.frmLoopBead, height=5).pack(side=tk.TOP, anchor=tk.CENTER)
        # tk.Label(self.frmLoopBead, text='ビード断面: ').pack(side=tk.TOP, anchor=tk.NW, padx=5)

        self.frmBeadInfo2 = tk.Frame(self.frmLoopBead)
        self.frmBeadInfo2.pack(side=tk.TOP, anchor=tk.W, expand=1, fill=tk.X, padx=5)
        
        tk.Label(self.frmBeadInfo2, text='ビード断面: ').pack(side=tk.LEFT, anchor=tk.CENTER, padx=5)
        self.frmBeadFig = tk.Frame(self.frmBeadInfo2)
        self.frmBeadFig.pack(side=tk.LEFT, anchor=tk.NW)
        self.iconBeadCrossSection = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'yomoriWelding_radius.png')), master=self.frmBeadFig)
        tk.Label(self.frmBeadFig, image=self.iconBeadCrossSection).pack(side=tk.LEFT, anchor=tk.W)
        
        self.frmBeadInput = tk.Frame(self.frmBeadInfo2)
        self.frmBeadInput.pack(side=tk.LEFT, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        
        tk.Label(self.frmBeadInput, text='ビード情報：').pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Frame(self.frmBeadInput, height=20).pack(side=tk.TOP, anchor=tk.CENTER)
        self.frmBeadRadius = tk.Frame(self.frmBeadInput)
        self.frmBeadRadius.pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Label(self.frmBeadRadius, text=' 半径: ').pack(side=tk.LEFT, anchor=tk.NW)
        self.entLoopBeadRadius = tk.Entry(self.frmBeadRadius, width=7)
        self.entLoopBeadRadius.pack(side=tk.LEFT, anchor=tk.NW)
        yomoriLoopRadius = self.config.Get('Yomori_Loop_Radius')
        self.entLoopBeadRadius.insert(tk.END, yomoriLoopRadius)
        tk.Frame(self.frmBeadInput, height=10).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmLoopBeadElemSize = tk.Frame(self.frmBeadInput)
        self.frmLoopBeadElemSize.pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Label(self.frmLoopBeadElemSize, text=' 要素長: ').pack(side=tk.LEFT, anchor=tk.CENTER)
        self.entLoopBeadElemSize = tk.Entry(self.frmLoopBeadElemSize, width=7)
        self.entLoopBeadElemSize.pack(side=tk.LEFT, anchor=tk.CENTER)
        beadElemSize = self.config.Get('Bead_Elem_Size')
        self.entLoopBeadElemSize.insert(tk.END, beadElemSize)

        tk.Frame(self.frmLoopBead, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmCtrl2 = tk.Frame(self.frmLoopBead)
        self.frmCtrl2.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)

        self.btnLoopWeld = tk.Button(self.frmCtrl2, text=' 作成 ', compound=tk.LEFT, command = self.ExecuteLoopWelding, width=10)
        self.btnLoopWeld.pack(side=tk.LEFT, anchor=tk.NW)        

        self.btnUndo2 = tk.Button(self.frmCtrl2, text=' 戻す ', compound=tk.LEFT, command=self.Undo2, width=10)
        self.btnUndo2.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo)

        self.btnClose = tk.Button(self.frmCtrl2, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=10)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)
    
    def ExecuteLoopWelding(self):
        loopEdge = simlab.getEntityFromGroup(self.loopWEdge)
        if not loopEdge:
            messagebox.showinfo('情報','エッジを選択してください。')
            return
        
        beadRadius = self.entLoopBeadRadius.get()
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
        
        beadElemSize = self.entLoopBeadElemSize.get()
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
        
        allModelNames = simlab.getAllRootModelNames('FEM')
        if len(allModelNames) > 1:
            messagebox.showinfo('情報','モデル名が複数あります。マージして一個にしてください。')
            return
        elif len(allModelNames) == 0:
            messagebox.showinfo('情報','FEモデルを作成してください。')
            return
        
        self.backup.Save('YomoriLoopWelding')
        modelName = simlab.getModelName('FEM')

        simlablib.UpdateModel()
        beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        createCircularBead(modelName, loopEdge, beadRadius, beadElemSize)
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

        sharedFaceGroup = 'Shared Faces'
        simlablib.DeleteGroups(sharedFaceGroup)
        sharedEntities(modelName, [beadName])
        sharedFaces = simlab.getEntityFromGroup(sharedFaceGroup)

        try:
            aspectRatio = float(self.config.Get('Aspect_Ratio'))
        except ValueError:
            aspectRatio = 10

        if sharedFaces:
            if len(sharedFaces) > 1:
                simlablib.MergeFaces(modelName, sharedFaces)
                sharedFaces = simlab.getEntityFromGroup(sharedFaceGroup)
            remeshFace(modelName, sharedFaces, beadElemSize, aspectRatio, preserveBoundaryOn=0)

        meshQualityCleanup(modelName, beadName, aspectRatio)

        # allBides = simlab.getBodiesWithSubString(modelName, ['*'])
        # simlab.showOrHideEntities(allBides, "Show", modelName, 'Body')
        simlab.redisplayEntity('Model', modelName)

        simlablib.DeleteGroups(self.loopWEdge)
        self.UpdateButtonFG2()

    def SelectLoopWEdges(self):
        edge = simlab.getSelectedEntities('EDGE')
        if len(edge) == 0:
            messagebox.showinfo('情報','エッジを選択した後、ボタンを押してください。')
            return
        
        simlablib.DeleteGroups(self.loopWEdge)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Edge', edge, self.loopWEdge)

        self.UpdateButtonFG2()
    
    def UpdateButtonFG2(self):
        groups = [self.loopWEdge]
        widgets = [self.btnLoopWEdge]

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

    def CreateDonutNoteBook(self):
        tk.Label(self.frmDonutBead, text='ドーナツ形状の平面に曲面ビードを作成します。\nビード面を選択してください。').pack(side=tk.TOP, anchor=tk.CENTER)
        self.frmDonutFig = tk.Frame(self.frmDonutBead)
        self.frmDonutFig.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5, pady=5)
        self.frmDonutFigTop = tk.Frame(self.frmDonutFig, width=400)
        self.frmDonutFigTop.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconDonut = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'yomoriWelding2.png')), master=self.frmDonutFigTop)
        tk.Label(self.frmDonutFigTop, image=self.iconDonut).pack(side=tk.TOP, anchor=tk.CENTER)

        self.btnDonutBead = tk.Button(self.frmDonutFigTop, text='ビード面(x1)', command=self.SelectDonutBead, width=10)
        self.btnDonutBead.place(x=110, y=100)

        self.frmDonutYomoriParams = tk.Frame(self.frmDonutBead, padx=5)
        self.frmDonutYomoriParams.pack(side=tk.TOP, anchor=tk.W)
        self.frmDonutBeadHeight = tk.Frame(self.frmDonutYomoriParams)
        self.frmDonutBeadHeight.pack(side=tk.LEFT, anchor=tk.W)
        tk.Label(self.frmDonutBeadHeight, text='高さ：').pack(side=tk.LEFT,anchor=tk.W)
        self.entDonutBeadHeight = tk.Entry(self.frmDonutBeadHeight, width=7)
        self.entDonutBeadHeight.pack(side=tk.LEFT,anchor=tk.W)
        self.entDonutBeadHeight.insert(0, 3.0)

        self.frmDonutBeadLayer = tk.Frame(self.frmDonutYomoriParams)
        self.frmDonutBeadLayer.pack(side=tk.LEFT, anchor=tk.NW, padx=5)
        tk.Label(self.frmDonutBeadLayer, text='ビードレイヤー数: ').pack(side=tk.LEFT, anchor=tk.NW)
        self.entDonutBeadElemLayer= tk.Entry(self.frmDonutBeadLayer, width=7)
        self.entDonutBeadElemLayer.pack(side=tk.LEFT, anchor=tk.NW)
        self.entDonutBeadElemLayer.insert(tk.END, 6)

        tk.Frame(self.frmDonutBead, height=5).pack(side=tk.TOP,anchor=tk.W)

        self.frmDonutBeadCtrl = tk.Frame(self.frmDonutBead,padx=5)
        self.frmDonutBeadCtrl.pack(side=tk.TOP, anchor=tk.CENTER, fill=tk.X, expand=1)

        self.btnDonutWeld = tk.Button(self.frmDonutBeadCtrl, text=' 作成 ', compound=tk.LEFT, command = self.ExecuteDonutYomori, width=10)
        self.btnDonutWeld.pack(side=tk.LEFT, anchor=tk.NW)        

        self.btnDonutYomoriUndo = tk.Button(self.frmDonutBeadCtrl, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=10)
        self.btnDonutYomoriUndo.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnDonutYomoriUndo)

        self.btnDonutYomoriClose = tk.Button(self.frmDonutBeadCtrl, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=10)
        self.btnDonutYomoriClose.pack(side=tk.RIGHT, anchor=tk.NE)

    def ExecuteDonutYomori(self):
        modelName = simlab.getModelName('FEM')
        groupName = 'donutBead'
        donutBeadFace = simlab.getEntityFromGroup(groupName)
        if not donutBeadFace:
            messagebox.showinfo('情報', 'ドーナツビード面を選択してください。')
            return
        
        n = simlab.getNormalFromFaceGroup(groupName)
        if not n:
            messagebox.showinfo('情報', 'ドーナツビード面の法線方向はわかりません。')
            return
        
        beadBodyGroup = 'beadBody'
        simlablib.DeleteGroups(beadBodyGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', donutBeadFace, 'Body', beadBodyGroup)
        beadBody = list(simlab.getBodiesFromGroup(beadBodyGroup))

        
        beadLayers = self.entDonutBeadElemLayer.get()
        if len(beadLayers) == 0:
            messagebox.showinfo('情報', 'ビードレイヤー数を入力してください。')
            return
        try:
            beadLayers = int(beadLayers)
        except ValueError:
            messagebox.showinfo('情報', 'ビードレイヤー数で数字だけを入力してください。')
            return
        
        beadHeight = self.entDonutBeadHeight.get()
        if len(beadHeight) == 0:
            messagebox.showinfo('情報', '余盛ビード高さを入力してください。')
            return
        try:
            beadHeight = float(beadHeight)
        except ValueError:
            messagebox.showinfo('情報', '高さで数字だけを入力してください。')
            return
        
        donutEdgeGroup = 'donutEdges'
        donutEdgeGroups = simlab.getGroupsWithSubString('EdgeGroup',['{}*'.format(donutEdgeGroup)])
        simlablib.DeleteGroups(donutEdgeGroups)

        simlablib.SelectAssociatedEntities(modelName, 'Face', donutBeadFace, 'Edge', donutEdgeGroup)
        donutEdgeGroups = simlab.createGroupsOfConnectedEntities(donutEdgeGroup)

        if len(donutEdgeGroups) != 2:
            messagebox.showinfo('情報', '内側と外側の円弧のエッジを区別できません。ビード面をマージしてからもう一度試してください。')
            return
        
        self.backup.Save('YomoriWelding2')

        edgeGroup1, edgeGroup2 = donutEdgeGroups
        edgeNodeGroup = 'edgeNodes'
        donutEdgeDict = dict()
        for thisGroup in [edgeGroup1, edgeGroup2]:
            simlablib.DeleteGroups(edgeNodeGroup)
            thisEdges = simlab.getEntityFromGroup(thisGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Edge', thisEdges, 'Node', edgeNodeGroup)

            edgeNodes = simlab.getEntityFromGroup(edgeNodeGroup)

            if len(edgeNodes) < 3:
                messagebox.showinfo('情報', 'エッジ ノードの数が 3 未満であるため、円弧情報は不明です。')
                return
            node1, node2, node3 = edgeNodes[:3]
            pt1 = simlab.getNodePositionFromNodeID(modelName, node1)
            pt2 = simlab.getNodePositionFromNodeID(modelName, node2)
            pt3 = simlab.getNodePositionFromNodeID(modelName, node3)

            arcInfo = GetCircleInfoFromThreePoints(pt1, pt2, pt3)

            donutEdgeDict[thisGroup] = ((node1, node2, node3), arcInfo)
        
        # print(donutEdgeDict)
        innerArcGroup = edgeGroup1
        outerArcGroup = edgeGroup2

        innerArcInfo = donutEdgeDict[innerArcGroup]
        outerArcInfo = donutEdgeDict[outerArcGroup]
        innerRad = innerArcInfo[1][1]
        outerRad = outerArcInfo[1][1]

        if innerRad > outerRad:
            innerArcGroup = edgeGroup2
            outerArcGroup = edgeGroup1

            innerArcInfo = donutEdgeDict[innerArcGroup]
            outerArcInfo = donutEdgeDict[outerArcGroup]
        
        p0 = innerArcInfo[1][0]
        r1 = innerArcInfo[1][3]

        outerRad = outerArcInfo[1][1]
        innerRad = innerArcInfo[1][1]

        pt1 = p0 + r1 * innerRad
        pt2 = p0 + r1 * outerRad
        pt3 = (pt1 + pt2) / 2 + beadHeight * np.array(n)
        
        print(pt1)
        print(pt2)
        print(pt3)

        startNode = simlab.getNextNodeID(modelName)
        simlablib.CreateNodeByXYZ(modelName, list(pt1), startNode)

        endNode = simlab.getNextNodeID(modelName)
        simlablib.CreateNodeByXYZ(modelName, list(pt2), endNode)

        byNode = simlab.getNextNodeID(modelName)
        simlablib.CreateNodeByXYZ(modelName, list(pt3), byNode)

        preBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        createEdgeFromNodes(modelName, startNode, endNode, byNode, beadLayers)
        postBodies = simlab.getBodiesWithSubString(modelName, ['*'])

        wireBody = list(set(postBodies) - set(preBodies))

        if not wireBody:
            messagebox.showinfo('情報', 'ワイアボディ作成に失敗しました。')
            return

        wireEdgeGroup = 'wireEdge'
        simlablib.DeleteGroups(wireEdgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Body', wireBody, 'Edge', wireEdgeGroup)

        wireEdge = simlab.getEntityFromGroup(wireEdgeGroup)
        guideEdges = simlab.getEntityFromGroup(innerArcGroup)
        preBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        sweepEdge(modelName, wireEdge, guideEdges)
        postBodies = simlab.getBodiesWithSubString(modelName, ['*'])

        sweepBody = list(set(postBodies) - set(preBodies))

        nodePts = []
        for thisNode in donutEdgeDict[innerArcGroup][0]:
            pt = simlab.getNodePositionFromNodeID(modelName, thisNode)
            nodePts.append(pt)

        fourPts = simlabutil.Convert3PointsOnPlaneTo4Points(nodePts)
        simlablib.DeleteGroups('Show_Edges')
        getEdgesOnPlane(modelName, sweepBody, fourPts)

        edgesOnPlane = simlab.getEntityFromGroup('Show_Edges')

        print('edgesOnPlane:{}'.format(edgesOnPlane))

        if len(edgesOnPlane) != 2:
            messagebox.showinfo('情報', 'スイープ ボディに平面エッジを見つかりません。')
            return

        edge1, edge2 = edgesOnPlane
        createFaceFromEdges(modelName, edge1, edge2)

        bodiesToJoin = beadBody + sweepBody
        joinBodiesOnMatchingFaces(modelName, bodiesToJoin, tol=1)

        simlablib.DeleteGroups('Shared Faces')

        getSharedFace(modelName, bodiesToJoin)

        sharedFace = simlab.getEntityFromGroup('Shared Faces')

        if not sharedFace:
            messagebox.showinfo('情報', 'ボディ結合に失敗しました。')
            return
        
        simlablib.DeleteEntities(modelName, 'Face', sharedFace)

        simlablib.MergeBodies(modelName, bodiesToJoin)
        
        bodiesToShow = simlab.getBodiesWithSubString(modelName, ['*'])

        simlab.redisplayEntity('Body', modelName, bodiesToShow)

        simlablib.DeleteEntities(modelName, 'Body', wireBody)

        self.btnDonutBead.config(fg='black')
    
    def SelectDonutBead(self):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        groupName = 'donutBead'
        simlablib.DeleteGroups(groupName)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, groupName)

        self.btnDonutBead.config(fg='blue')

    def CreateNoteBook1(self):
        tk.Label(self.frmAngleBead, text='長方形の平面に曲面ビードを作成します。\n4つのコーナーノードとビード面を選択してください。').pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Frame(self.frmAngleBead, height=5).pack(side=tk.TOP, anchor=tk.CENTER)
        self.frmFig = tk.Frame(self.frmAngleBead)        
        self.frmFig.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        self.frmYomoriWelding = tk.Frame(self.frmFig, width=400)
        self.frmYomoriWelding.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconYomori = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'yomoriWelding.png')), master=self.frmYomoriWelding)
        tk.Label(self.frmYomoriWelding, image=self.iconYomori).pack(side=tk.LEFT, anchor=tk.W)

        self.btnRefFace1 = tk.Button(self.frmYomoriWelding, text='ビード面', command=self.SelectRefFace, width=10)
        self.btnRefFace1.place(x=215, y=80)

        self.btnCornerNodes = tk.Button(self.frmYomoriWelding, text='ノード（ｘ４）', command=self.SelectCornerNodes, width=10)
        self.btnCornerNodes.place(x=50, y=125)
        # self.btnRefFace2 = tk.Button(self.frmYomoriWelding, text='平面２', command=lambda: self.SelectRefFace(2), width=10)
        # self.btnRefFace2.place(x=280, y=240)

        # self.btnWEdge = tk.Button(self.frmYomoriWelding, text='エッジ', command=self.SelectWEdges, width=10)
        # self.btnWEdge.place(x=270, y=160)

        tk.Frame(self.frmAngleBead, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        tk.Label(self.frmAngleBead, text='ビード情報: ').pack(side=tk.TOP, anchor=tk.NW,padx=5)

        self.frmBeadInfo = tk.Frame(self.frmAngleBead)
        self.frmBeadInfo.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        
        # self.frmBeadInfoDetail = tk.Frame(self.frmBeadInfo)
        # self.frmBeadInfoDetail.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)

        self.frmBeadHeight = tk.Frame(self.frmBeadInfo)
        self.frmBeadHeight.pack(side=tk.LEFT, anchor=tk.NW)
        tk.Label(self.frmBeadHeight, text='高さ: ').pack(side=tk.LEFT, anchor=tk.NW)
        self.entBeadHeight = tk.Entry(self.frmBeadHeight, width=7)
        self.entBeadHeight.pack(side=tk.LEFT, anchor=tk.NW)
        yomoriHeight = self.config.Get('Yomori_height')
        self.entBeadHeight.insert(tk.END, yomoriHeight)

        self.frmBeadLayer = tk.Frame(self.frmBeadInfo)
        self.frmBeadLayer.pack(side=tk.LEFT, anchor=tk.NW, padx=5)
        tk.Label(self.frmBeadLayer, text='要素長: ').pack(side=tk.LEFT, anchor=tk.NW)
        self.entBeadElemSize = tk.Entry(self.frmBeadLayer, width=7)
        self.entBeadElemSize.pack(side=tk.LEFT, anchor=tk.NW)
        beadElemSize = self.config.Get('Bead_Elem_Size')
        self.entBeadElemSize.insert(tk.END, beadElemSize)

        self.frmCutAngle = tk.Frame(self.frmBeadInfo)
        self.frmCutAngle.pack(side=tk.LEFT, anchor=tk.NW)
        tk.Label(self.frmCutAngle, text='端部カット角度: ').pack(side=tk.LEFT, anchor=tk.NW)
        self.entCutAngle = tk.Entry(self.frmCutAngle, width=7)
        self.entCutAngle.pack(side=tk.LEFT, anchor=tk.NW)
        self.entCutAngle.insert(tk.END, 15)

        tk.Frame(self.frmAngleBead, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmCtrl = tk.Frame(self.frmAngleBead)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)

        self.btnWeld = tk.Button(self.frmCtrl, text=' 作成 ', compound=tk.LEFT, command = self.StartWelding, width=10)
        self.btnWeld.pack(side=tk.LEFT, anchor=tk.NW)        

        self.btnUndo = tk.Button(self.frmCtrl, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=10)
        self.btnUndo.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo)

        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=10)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)
    
    def SelectRefFace(self):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        simlablib.DeleteGroups(self.refFace1)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, self.refFace1)

        self.UpdateButtonFG()

    def SelectCornerNodes(self):
        nodes = simlab.getSelectedEntities('NODE')
        if len(nodes) == 0:
            messagebox.showinfo('情報','ノードを選択した後、ボタンを押してください。')
            return
        
        simlablib.DeleteGroups(self.cornerNodes)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Node', nodes, self.cornerNodes)

        self.UpdateButtonFG()
    
    def StartWelding(self):
        beadElemSize = self.entBeadElemSize.get()
        if len(beadElemSize) == 0:
            messagebox.showinfo('情報','要素サイズを入力してください。')
            return
        try:
            beadElemSize = float(beadElemSize)
        except ValueError:
            messagebox.showinfo('情報','要素サイズで数字を入力してください。')
            return
        else:
            if beadElemSize <= 0:
                messagebox.showinfo('情報','要素サイズで０より大きい数字を入力してください。')
                return
        
        beadHeight = self.entBeadHeight.get()
        if len(beadHeight) == 0:
            messagebox.showinfo('情報','高さを入力してください。')
            return
        try:
            beadHeight = float(beadHeight)
        except ValueError:
            messagebox.showinfo('情報','高さで数字を入力してください。')
            return
        else:
            if beadHeight <= 0:
                messagebox.showinfo('情報','高さで０より大きい数字を入力してください。')
                return
        
        cutAngle = self.entCutAngle.get()
        if len(cutAngle) == 0:
            messagebox.showinfo('情報','カット角度を入力してください。')
            return
        try:
            cutAngle = float(cutAngle)
        except ValueError:
            messagebox.showinfo('情報','カット角度で数字を入力してください。')
            return
        else:
            if cutAngle < 0:
                messagebox.showinfo('情報','カット角度で０または正数を入力してください。')
                return
        
        try:
            aspectRatio = float(self.config.Get('Aspect_Ratio'))
        except ValueError:
            aspectRatio = 10

        refFace = simlab.getEntityFromGroup(self.refFace1)
        if not refFace:
            messagebox.showinfo('情報','ビード面を選んで登録してください。')
            return
        n = simlab.getNormalFromFaceGroup(self.refFace1)

        if not n:
            messagebox.showinfo('情報','平面を選択してください。')
            return
        n = np.array(n)

        allModelNames = simlab.getAllRootModelNames('FEM')
        if len(allModelNames) > 1:
            messagebox.showinfo('情報','モデル名が複数あります。マージして一個にしてください。')
            return
        elif len(allModelNames) == 0:
            messagebox.showinfo('情報','FEモデルを作成してください。')
            return

        modelName = simlab.getModelName('FEM')
        self.backup.Save('YomoriWelding1')

        bodyGroup = 'bodyGroup'
        simlablib.DeleteGroups(bodyGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', refFace, 'Body', bodyGroup)
        refBody = list(simlab.getBodiesFromGroup(bodyGroup))
             
        cornerNodes = simlab.getEntityFromGroup(self.cornerNodes)
        if len(cornerNodes) !=4 :
            messagebox.showinfo('情報','コーナーノード４を登録してください。')
            return
        
        p1, p2, p3, p4 = cornerNodes
        pt1 = np.array(simlab.getNodePositionFromNodeID(modelName, p1))
 
        #print('p1:{}'.format(p1))
        distDict = dict()
        for thisP in [p2,p3,p4]:
            thisPt = np.array(simlab.getNodePositionFromNodeID(modelName, thisP))
            dist = np.linalg.norm(pt1-thisPt)
            distDict[thisP] = dist
        nodesSortedByDist = sorted(distDict, key=distDict.get)

        p2, p3, p4 = nodesSortedByDist
        pt2 = np.array(simlab.getNodePositionFromNodeID(modelName, p2))
        pt3 = np.array(simlab.getNodePositionFromNodeID(modelName, p3))
        pt4 = np.array(simlab.getNodePositionFromNodeID(modelName, p4))

        gridCornerNodesInOrder = [p1,p3,p2,p4]

        xlen = np.linalg.norm(pt1 - np.array(simlab.getNodePositionFromNodeID(modelName, p3)))
        xNum = max(int(round(xlen/beadElemSize)),2)
        yNum = 4
        #print('xNum:{}'.format(xNum))
        gridMesh(modelName, refFace, gridCornerNodesInOrder, xNum, yNum)

        beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        createBodyFromFaceShared(modelName, refFace)
        afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        bodyFromFace = list(set(afterBodies) - set(beforeBodies))

        faceGroup = 'faceGroup'
        simlablib.DeleteGroups(faceGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Body', bodyFromFace, 'Face', faceGroup)
        refFaceCopy = simlab.getEntityFromGroup(faceGroup)

        refFaceCopyGroup = 'refFaceCopyGroup'
        simlablib.CreateGroup(modelName, 'Face', refFaceCopy, refFaceCopyGroup)

        nodesOnNewFace = []
        showNodeGroup = 'Show_Nodes'
        for thisPt in [pt1, pt2, pt3, pt4]:
            simlablib.DeleteGroups(showNodeGroup)
            getNodeInSphere(modelName, refFaceCopy, 0.1, list(thisPt))
            nodeInCoord = simlab.getEntityFromGroup(showNodeGroup)
            if nodeInCoord:
                nodesOnNewFace.append(nodeInCoord[0])
        
        p1, p2, p3, p4 = nodesOnNewFace
        gridCornerNodesInOrder = [p1,p3,p2,p4]
        #print('gridCornerNodesInOrder:{}'.format(gridCornerNodesInOrder))

        xlen = np.linalg.norm(pt1 - np.array(simlab.getNodePositionFromNodeID(modelName, p3)))
        xNum = max(int(round(xlen/beadElemSize)),2)
        yNum = 4
        #print('xNum:{}'.format(xNum))
        gridMesh(modelName, refFaceCopy, gridCornerNodesInOrder, xNum, yNum)

        refFaceCopy = simlab.getEntityFromGroup(refFaceCopyGroup)

        nodesAfterGridMesh = []
        showNodeGroup = 'Show_Nodes'
        for thisPt in [pt1, pt2, pt3, pt4]:
            simlablib.DeleteGroups(showNodeGroup)
            getNodeInSphere(modelName, refFaceCopy, 0.1, list(thisPt))
            nodeInCoord = simlab.getEntityFromGroup(showNodeGroup)
            if nodeInCoord:
                nodesAfterGridMesh.append(nodeInCoord[0])
        
        p1, p2, p3, p4 = nodesAfterGridMesh
        nodePair1 = [p1,p2]
        nodePair2 = [p3,p4]
        #print('nodePair1:{}'.format(nodePair1))
        #print('nodePair2:{}'.format(nodePair2))
        
        # seperateBody(modelName, refBody)

        pMid1 = (pt1+pt2) / 2
        pMid2 = (pt3+pt4) / 2
        byNodeId = simlab.getNextNodeID(modelName)
        byNodePt = pMid1 + n * beadHeight
        createNodeByXYZ(modelName, list(byNodePt), byNodeId)

        # center, R, N, V1
        circleInfo = getCircleInfoFromThreePoints(pt1,byNodePt, pt2)
        cPt, rad, _, _ = circleInfo
        axisV = (pMid1 - pMid2)/ np.linalg.norm(pMid1 - pMid2)
        cylinderHeight = np.linalg.norm(pMid1 - pMid2)*2.5
        #print('axisV:{}'.format(axisV))
        #print('cylinderHeight:{}'.format(cylinderHeight))
        #print('cPt:{}'.format(cPt))
        alignCylinder(modelName, refFaceCopy, list(axisV), list(cPt), rad, cylinderHeight)

        simlablib.MergeBodies(modelName, refBody+bodyFromFace)

        refFace = simlab.getEntityFromGroup(self.refFace1)
        # print('refFace:{}'.format(refFace))
        if refFace:
            simlablib.DeleteEntities(modelName, 'Face', refFace)
            simlablib.UpdateModel()
        
        
        nodeEquivalence(modelName, refBody)
        fillFreeEdgesOfBody(modelName, refBody)

        
        if cutAngle > 0:
            rotateAxis = (pt1-pt2)/ np.linalg.norm(pt1-pt2)
            thetaInRadians = np.radians(cutAngle)
            rotationMatrix = getRotationMatrix(rotateAxis, thetaInRadians)
            #print('rotationMatrix:{}'.format(rotationMatrix))
            cuttingPlane = np.dot(rotationMatrix, n)
            
            d = np.dot(cuttingPlane, pt1)

            if (np.dot(cuttingPlane, pt3) - d) > 0:
                #print('recalculate rotation matrix')
                rotateAxis = rotateAxis * -1
                rotationMatrix = getRotationMatrix(rotateAxis, thetaInRadians)
                cuttingPlane = np.dot(rotationMatrix, n)
            
            #print('cuttingPlane:{}'.format(cuttingPlane))

            crossVec = np.cross(cuttingPlane, rotateAxis)
            ptOnPlane = pt1 + crossVec * 10
            #print('ptOnPlane:{}'.format(ptOnPlane))

            pts = simlabutil.Convert3PointsOnPlaneTo4Points([pt1, pt2, ptOnPlane])
            
            breakBody(modelName, refBody, pts)          

            bodies = simlab.getBodiesWithSubString(modelName, ['{}*'.format(refBody[0])])
            
            if not os.path.exists(LOG_DIR):
                os.makedirs(LOG_DIR)
            f_name = os.path.join(LOG_DIR,'bodyVolume.csv')
            if os.path.exists(f_name):
                os.remove(f_name)
            volDict = calculateBodyVolume(modelName, bodies, f_name)
            #print(volDict)
            if volDict:
                refBody = [max(volDict, key=volDict.get)]

                for thisBody in bodies:
                    if thisBody in refBody:
                        continue
                    simlablib.DeleteEntities(modelName, 'Body', [thisBody])
            
            # print('refBody:{}'.format(refBody))
            fillFreeEdgesOfBody(modelName, refBody)

            faceToRemesh = []
            faceGroup = 'Show_Faces'
            simlablib.DeleteGroups(faceGroup)
            getFacesByPlane(modelName, refBody, pts, on=1, above=0, below=0)
            cutFace = simlab.getEntityFromGroup(faceGroup)
            if cutFace:
                for thisFace in cutFace:
                    faceToRemesh.append(thisFace)
            
            ###############
                
            rotateAxis = (pt3-pt4)/ np.linalg.norm(pt3-pt4)
            thetaInRadians = np.radians(cutAngle)
            rotationMatrix = getRotationMatrix(rotateAxis, thetaInRadians)
            #print('rotationMatrix:{}'.format(rotationMatrix))
            cuttingPlane = np.dot(rotationMatrix, n)
            
            d = np.dot(cuttingPlane, pt3)

            if (np.dot(cuttingPlane, pt1) - d) > 0:
                #print('recalculate rotation matrix')
                rotateAxis = rotateAxis * -1
                rotationMatrix = getRotationMatrix(rotateAxis, thetaInRadians)
                cuttingPlane = np.dot(rotationMatrix, n)
            
            #print('cuttingPlane:{}'.format(cuttingPlane))

            crossVec = np.cross(cuttingPlane, rotateAxis)
            ptOnPlane = pt3 + crossVec * 10
            #print('ptOnPlane:{}'.format(ptOnPlane))

            pts = simlabutil.Convert3PointsOnPlaneTo4Points([pt3, pt4, ptOnPlane])
            
            breakBody(modelName, refBody, pts)
            

            bodies = simlab.getBodiesWithSubString(modelName, ['{}*'.format(refBody[0])])
            
            if os.path.exists(f_name):
                os.remove(f_name)
            volDict = calculateBodyVolume(modelName, bodies, f_name)
            #print(volDict)
            if volDict:
                refBody = [max(volDict, key=volDict.get)]

                for thisBody in bodies:
                    if thisBody in refBody:
                        continue
                    simlablib.DeleteEntities(modelName, 'Body', [thisBody])
            
            #print('refBody:{}'.format(refBody))
            fillFreeEdgesOfBody(modelName, refBody)
            faceGroup = 'Show_Faces'
            simlablib.DeleteGroups(faceGroup)
            getFacesByPlane(modelName, refBody, pts, on=1, above=0, below=0)
            cutFace = simlab.getEntityFromGroup(faceGroup)
            if cutFace:
                for thisFace in cutFace:
                    faceToRemesh.append(thisFace)
            
            if faceToRemesh:
                mcName = 'preserveEdgeMC'
                simlablib.DeleteMeshControl(mcName)
                preserveFaceEdgeMC(mcName, modelName, faceToRemesh)
                remeshFace(modelName, faceToRemesh, beadElemSize, aspectRatio, preserveBoundaryOn=0)

        nodeGroups = simlab.getGroupsWithSubString('NodeGroup', ['*'])
        simlablib.DeleteGroups(nodeGroups)
        simlablib.DeleteAllOphanNodes()

        # beadName = refBody[0]
        # adjBodyGroup = 'Adjacent_Bodies'
        # simlablib.DeleteGroups(adjBodyGroup)
        # searchAdjacentBodies(modelName, beadName, tol=1e-1)
        # adjBodies = list(simlab.getBodiesFromGroup(adjBodyGroup))

        # if beadName in adjBodies:
        #     adjBodies.remove(beadName)
        
        # for thisBody in adjBodies:
        #     joinOnOvelappingFaces(modelName, beadName,thisBody)
        
        # if endCut:
        #     refFace = simlab.getEntityFromGroup(self.refFace1)
        #     gridMesh(modelName, refFace, gridCornerNodesInOrder, xNum, yNum)
        
        simlabutil.ClearSelection()
    
    def UpdateButtonFG(self):
        groups = [self.refFace1, self.cornerNodes]
        widgets = [self.btnRefFace1, self.btnCornerNodes]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)
    
    def Undo(self):
        self.backup.Load()
        self.UpdateButtonFG()

        modelName = simlab.getModelName('FEM')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')

    def CloseDialog(self):
        super().CloseDialog()

def getNormalFromThreePts(pts):
    p1,p2,p3 = pts
    p1 = np.array(p1)
    p2 = np.array(p2)
    p3 = np.array(p3)

    v1 = (p2 - p1) / np.linalg.norm(p2 - p1)
    v2 = (p3 - p1) / np.linalg.norm(p3 - p1)
    cp = np.cross(v1,v2)

    return cp / np.linalg.norm(cp)

def angle_between(n1, n2):
    return np.arccos(np.clip(np.dot(n1, n2), -1.0, 1.0))

def createCircleBead(modelName, edge, rad, meshSize):
    CreateWeldBead=''' <CreateWeldBead UUID="094b6bc4-9494-4d67-a17d-ae3d0499f3f7">
    <GuideEdges>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edge).strip('()''[]') +'''</Edge>
    </Entities>
    </GuideEdges>
    <BeadCrossSection Value="Circular"/>
    <BeadRadius Value="'''+ str(rad) +'''"/>
    <BeadEndType Value="Flat"/>
    <CircularMeshSize Value="'''+ str(meshSize) +'''" Check="1"/>
    <CircularNumberOfElements Value="16" Check="0"/>
    <UseExistingMeshInGuideEdge Check="1"/>
    <GuideMeshSize Value="1 mm" Check="0"/>
    </CreateWeldBead>'''
    simlab.execute(CreateWeldBead)

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

def breakBody(modelName, body, pts):
    pt1, pt2, pt3, pt4 = pts
    BreakBody=''' <Break UUID="ccdd6ef0-aaff-4594-850d-886c733cbc2f">
    <tag Value="-1"/>
    <Name Value="Break1"/>
    <Type Value="1"/>
    <PlaneBreak>
    <CreateInternalFace Value="1"/>
    <BreakBodies Value="1"/>
    <CreateSheetBodyFromCutSection Value="0"/>
    <PlanePoints Value=""/>
    <Entity>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(body).replace("'",'"').strip('()''[]') +''',</Body>
    </Entities>
    </Entity>
    <Mode Value="1" value=""/>
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

def getFacesByPlane(modelName, body, pts, on=1, above=0, below=0):
    pt1, pt2, pt3, pt4 = pts
    
    FacesByPlane=''' <FacesByPlane UUID="116fb6e7-2d86-45fb-bbee-bd40e654a0bf">
    <Name Value="Show Faces"/>
    <SupportEntities>
    <Entities>  
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(body).replace("'",'"').strip('()''[]') +'''</Body>
    </Entities>
    </SupportEntities>
    <Option Value="3"/>
    <On Value="'''+ str(on) +'''"/>
    <Above Value="'''+ str(above) +'''"/>
    <Below Value="'''+ str(below) +'''"/>
    <Tolerance Value="0.1 mm"/>
    <CreateGroup Value="1"/>
    <RegionObject>
    <Plane>
    <Finite Value="0"/>
    <Pt1 Value="'''+ str(pt1).strip('()''[]') +'''"/>
    <Pt2 Value="'''+ str(pt2).strip('()''[]') +'''"/>
    <Pt3 Value="'''+ str(pt3).strip('()''[]') +'''"/>
    <Pt4 Value="'''+ str(pt4).strip('()''[]') +'''"/>
    </Plane>
    </RegionObject>
    </FacesByPlane>'''
    simlab.execute(FacesByPlane)

def sameDirection(n1, n2):
    dotProd = np.dot(n1, n2)
    return abs(dotProd - 1.0) < 1e-6

def deleteBodyUnderPlane(modelName, bodies, planePts):

    faceGroup = 'Show_Faces'
    simlablib.DeleteGroups(faceGroup)
    getFacesByPlane(modelName, [bodies[0]], planePts, below=1)
    
    facesOnBody_1 = simlab.getEntityFromGroup(faceGroup)

    simlablib.DeleteGroups(faceGroup)
    getFacesByPlane(modelName, [bodies[1]], planePts, below=1)

    facesOnBody_2 = simlab.getEntityFromGroup(faceGroup)

    if len(facesOnBody_1) > len(facesOnBody_2):
        simlablib.DeleteEntities(modelName, 'Body', [bodies[0]])
        return bodies[0]
    
    simlablib.DeleteEntities(modelName, 'Body', [bodies[1]])
    return bodies[1]

def getFaceVertexPts(modelName, face):
    vertexGroup = 'vertexGroup'
    simlablib.DeleteGroups(vertexGroup)
    simlablib.SelectAssociatedEntities(modelName, 'Face', face, 'Vertex', vertexGroup)
    vertexes = simlab.getEntityFromGroup(vertexGroup)
    vertexPts =[]
    if len(vertexes) < 3:
        return None
    for idx in range(3):    
        vPt = np.array(simlab.getVertexPositionFromVertexID(modelName, vertexes[idx]))
        vertexPts.append(vPt)
    return vertexPts

def joinOnOvelappingFaces(modelName, bodyToBeKept, bodyToBeModiFied, tol= 0.1, remeshOn=1):
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
    <LocalRemesh Value="'''+ str(remeshOn) +'''"/>
    <ShowOrJoin Value="0"/>
    </Join>'''
    simlab.execute(Join)

def remeshFace(modelName, faces, elemSize, aspectRat, preserveBoundaryOn):
    SurfaceLocalRemesh=''' <NewLocalReMesh UUID="83ab93df-8b5e-4a48-a209-07ed417d75bb">
    <tag Value="-1"/>
    <Name Value="NewLocalReMesh2"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(faces).strip('()''[]') +'''</Face>
    </Entities>
    </SupportEntities>
    <ElemType Value="0"/>
    <AverageElemSize Value="'''+ str(elemSize) +'''"/>
    <MinElemSize Value="'''+ str(elemSize/aspectRat) +'''"/>
    <PreserveBoundaryEdges Value="'''+ str(preserveBoundaryOn) +'''"/>
    <NumberOfSolidLayersToUpdate Value="3"/>
    <TriOption>
    <GradeFactor Value="1.5"/>
    <MaxAnglePerElem Value="45 deg"/>
    <CurvatureMinElemSize Value="'''+ str(elemSize/2) +'''"/>
    <AspectRatio Value="'''+ str(aspectRat) +'''"/>
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

def sharedFacesBetweenBodies(modelName, body1, body2):
    SharedEntities=''' <SharedEntities UUID="2dc7ae98-62c3-4926-bbde-d08da48208ad" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value="SharedEntities1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>"'''+ body1 +'''","'''+ body2 +'''",</Body>
    </Entities>
    </SupportEntities>
    <Faces Value="1"/>
    <Edges Value="0"/>
    <Vertices Value="0"/>
    </SharedEntities>'''
    simlab.execute(SharedEntities)

def translateBody(modelName, body, direcV, dist):
    Translation=''' <Translation UUID="26b085e8-d9a3-4baf-95f2-9f3eb75ac454" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>"'''+ body +'''",</Body>
    </Entities>
    </SupportEntities>
    <RegionObject>
    <TranslationDirection>
    <DirectionVector Value="'''+ str(direcV).strip('()''[]') +'''"/>
    </TranslationDirection>
    </RegionObject>
    <UnitVector Value="0"/>
    <Magnitude Value="1"/>
    <DistanceVector Value="'''+ str(dist) +'''"/>
    <CoorId Value="0"/>
    <Copy Value="0"/>
    <WithLBC Value="0"/>
    <No.Of.Copies Value="1"/>
    <LocalCoordinateSystem Value=""/>
    <Output/>
    </Translation>'''
    simlab.execute(Translation)

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

def createCircularBead(modelName, edges, radius, meshSize):
    CreateWeldBead=''' <CreateWeldBead UUID="094b6bc4-9494-4d67-a17d-ae3d0499f3f7">
    <GuideEdges>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edges).strip('()''[]') +'''</Edge>
    </Entities>
    </GuideEdges>
    <BeadCrossSection Value="Circular"/>
    <BeadRadius Value="'''+ str(radius) +'''"/>
    <BeadEndType Value="Round"/>
    <RoundWithinGuideEdge Value="0"/>
    <CircularMeshSize Value="'''+ str(meshSize) +'''" Check="1"/>
    <CircularNumberOfElements Value="16" Check="0"/>
    <UseExistingMeshInGuideEdge Check="1"/>
    <GuideMeshSize Value="1.0" Check="0"/>
    </CreateWeldBead>'''
    simlab.execute(CreateWeldBead)

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

def gridMesh(modelName, face, cornerNodes, num_x, num_y):
    GridMesh=''' <NXMMeshing UUID="2341e120-6484-415c-afd1-88a976436e83">
    <FaceIds>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(face).strip('()''[]') +'''</Face>
    </Entities>
    </FaceIds>
    <CornerNodes>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Node>'''+ str(cornerNodes).strip('()''[]') +'''</Node>
    </Entities>
    </CornerNodes>
    <AnchorNodes/>
    <Option Value="No of Elements"/>
    <XDirection Value="'''+ str(num_x) +'''"/>
    <YDirection Value="'''+ str(num_y) +'''"/>  
    <LocalRemesh Value="0"/>
    <Meshsize Value="0.0"/>
    <Projection Value="0"/>
    <PreserveMesh Value="0"/>
    <ElementType Value="1"/>
    <MergeFace Value="0"/>
    <CadProjection Value=""/>
    <MeshTransition Check="0">
    <TransitionType ReferenceCount="X1" Option="AUTO"/>
    <SeedCount Y2="" X1="" Y1="" X2=""/>
    </MeshTransition>
    <NumberOfSolidLayersToUpdate Value="3"/>
    </NXMMeshing>'''
    simlab.execute(GridMesh)
    #print(GridMesh)

def alignCylinder(modelName, face, axisVector, centerPt, rad, height):
    AlignCylinder=''' <AlignCylinder CheckBox="ON" UUID="5D271AC4-A0CE-411f-9E60-E7B17CB8B1B7">
    <tag Value="-1"/>
    <Name Value=""/>
    <Entities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(face).strip('()''[]') +'''</Face>
    </Entities>
    </Entities>
    <ProjectMidNodes Value="0"/>
    <EntityType Value="1"/>
    <RegionObject>
    <Cylinder>
    <Axis Value="'''+ str(axisVector).strip('()''[]') +'''"/>
    <Center Value="'''+ str(centerPt).strip('()''[]') +'''"/>
    <Radius Value="'''+ str(rad) +'''"/>
    <Height Value="'''+ str(height) +'''"/>
    </Cylinder>
    </RegionObject>
    </AlignCylinder>'''
    simlab.execute(AlignCylinder)

def alignPlanar(modelName, face, pts):
    pt1, pt2, pt3, pt4 = pts
    AlignPlanar=''' <AlignPlanar CheckBox="ON" UUID="b9175a92-dd76-4c68-b31c-0c20c2afa2c3">
    <tag Value="-1"/>
    <Name Value=""/>
    <Select Value="TargetFace"/>
    <Entities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(face).strip('()''[]') +'''</Face>
    </Entities>
    </Entities>
    <DeleteZeroAreaElement Value="1"/>
    <RedoFlag Value=""/>
    <RegionObject>
    <Plane>
    <Finite Value="0"/>
    <Pt1 Value="'''+ str(pt1).strip('()''[]') +'''"/>
    <Pt2 Value="'''+ str(pt2).strip('()''[]') +'''"/>
    <Pt3 Value="'''+ str(pt3).strip('()''[]') +'''"/>
    <Pt4 Value="'''+ str(pt4).strip('()''[]') +'''"/>
    </Plane>
    </RegionObject>
    </AlignPlanar>'''
    simlab.execute(AlignPlanar)

# def breakFace(modelName, face, pts):
#     pt1, pt2, pt3, pt4 = pts
#     BreakBody=''' <Break UUID="ccdd6ef0-aaff-4594-850d-886c733cbc2f">
#     <tag Value="-1"/>
#     <Name Value="Break1"/>
#     <Type Value="1"/>
#     <PlaneBreak>
#     <CreateInternalFace Value="0"/>
#     <BreakBodies Value="1"/>
#     <CreateSheetBodyFromCutSection Value="0"/>
#     <PlanePoints Value=""/>
#     <Entity>
#     <Entities>
#     <Model>'''+ modelName +'''</Model>
#     <Face>'''+ str(face).strip('()''[]') +'''</Face>
#     </Entities>
#     </Entity>
#     <Mode value="" Value="1"/>
#     <RegionObject>
#     <Plane>
#     <Finite Value="0"/>
#     <Pt1 Value="'''+ str(pt1).strip('()''[]') +'''"/>
#     <Pt2 Value="'''+ str(pt2).strip('()''[]') +'''"/>
#     <Pt3 Value="'''+ str(pt3).strip('()''[]') +'''"/>
#     <Pt4 Value="'''+ str(pt4).strip('()''[]') +'''"/>
#     </Plane>
#     </RegionObject>
#     </PlaneBreak>
#     <CylBreak>
#     <CreateInternalFace Value="0"/>
#     <BreakBodies Value="0"/>
#     <Entity Value=""/>
#     <Retain Value=""/>
#     </CylBreak>
#     <BoxBreak>
#     <BreakOption Value="0"/>
#     <Entity Value=""/>
#     </BoxBreak>
#     <PolyBreak>
#     <Mode Value=""/>
#     <TargetEntities Value=""/>
#     <ToolEntities Value=""/>
#     <CreateInternalFace Value="0"/>
#     <BreakBodies Value="0"/>
#     <Entity Value=""/>
#     </PolyBreak>
#     <ConeBreak>
#     <CreateInternalFace Value="0"/>
#     <BreakBodies Value="0"/>
#     <Entity Value=""/>
#     </ConeBreak>
#     <RedoFlag Value=""/>
#     <Output/>
#     </Break>'''
#     simlab.execute(BreakBody)
#     # print(BreakBody)

def getNodeInSphere(modelName, face, rad, ctp, tol = 0.1):
    NodesByRegion=''' <NodesByRegion UUID="ad9db725-dcb3-4f9c-abd7-0e7a8cf64d05">
    <tag Value="-1"/>
    <Name Value="Show Nodes"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(face).strip('()''[]') +'''</Face>
    </Entities>
    </SupportEntities>
    <Option Value="0"/>
    <On Value="1"/>
    <Above Value="0"/>
    <Below Value="1"/>
    <Tolerance Value="'''+ str(tol) +'''"/>
    <MaximumCount Value="5000"/>
    <ShowSurfaceNodes Value="1"/>
    <CreateGroup Value="1"/>
    <RegionObject>
    <Sphere>
    <Center Value="'''+ str(ctp).strip('()''[]') +'''"/>
    <Radius Value="'''+ str(rad) +'''"/>
    </Sphere>
    </RegionObject>
    </NodesByRegion>'''
    simlab.execute(NodesByRegion)

def seperateBody(modelName, body):
    Separate=''' <Separate gda="" CheckBox="ON" UUID="5159E70B-B9FD-4b8b-9116-66D7CA71FF96">
    <tag Value="-1"/>
    <Name Value="Separate1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(body).replace("'",'"').strip('()''[]') +'''</Body>
    </Entities>
    </SupportEntities>
    <Output/>
    </Separate>'''
    simlab.execute(Separate)

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

def getCircleInfoFromThreePoints(pt1,pt2,pt3):

    pt1,pt2,pt3 = map(np.array, [pt1,pt2,pt3])
    
    N = getNormalFromThreePts([pt1,pt2,pt3])
    v12 = pt2 - pt1
    v13 = pt3 - pt1

    A = np.array([N, v12, v13])
    B = np.array([np.dot(N,pt1), np.dot(v12,((pt1+pt2)/2)), np.dot(v13,((pt1+pt3)/2))])
    B = B.reshape(len(B),1)
    X = (np.linalg.solve(A, B)).T

    center = np.array(X[0])
    V1 = pt1 - center
    R = np.linalg.norm(V1)
    return center, R, N, V1

def getRotationMatrix(axis, theta):

    # rotate counterclockwise a vector in a given axis by theta in radians

    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d

    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

def calculateBodyVolume(modelName, bodies, fName):
    CalculateVolume=''' <CalculateVolume UUID="d39d9d77-f4b8-4578-a341-7be7ac69dd47">
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(bodies).replace("'",'"').strip('()''[]') +'''</Body>
    </Entities>
    </SupportEntities>
    <FileName Value="'''+ fName +'''"/>
    </CalculateVolume>'''
    simlab.execute(CalculateVolume)

    volumeDict = dict()
    if not os.path.exists(fName):
        return volumeDict
    
    with open(fName) as f_read:
        for line in f_read:
            line = line.rstrip('\n')
            if not line.rstrip():
                continue
            if line.startswith('#'):
                continue
            spLine = line.split(',')
            bodyName = spLine[0]
            if bodyName in bodies:
                vol = spLine[-1]
                try:
                    vol = float(vol)
                except:
                    pass
                else:
                    volumeDict[bodyName] = vol
    return volumeDict

def createBodyFromFaceShared(modelName, face):
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

def nodeEquivalence(modelName, body, tol=0.1):
    EquivalenceNodes=''' <FemNodeEquivalence UUID="7a5431cd-a2da-4f61-b8ef-9abf3306dd0c">
    <tag Value="-1"/>
    <Name Value="FemNodeEquivalence1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(body).replace("'", '"').strip('()''[]') +'''</Body>
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
    <Tolerance Value="'''+ str(tol) +'''"/>
    <Show Value="" Clicked="0"/>
    <RBECenterOrphanNodeMass Value="0"/>
    <PreserverRbePos Value="1"/>
    <PreserverRbeID Value="1"/>
    <Output/>
    </FemNodeEquivalence>'''
    simlab.execute(EquivalenceNodes)

def fillFreeEdgesOfBody(modelName, body):
    FillHoles=''' <FillHole UUID="E9B9EC99-A6C1-4626-99FF-626F38A8CE4F" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value="FillHole2"/>
    <InputOption Value="Mesh"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(body).replace("'",'"').strip('()''[]') +'''</Body>
    </Entities>
    </SupportEntities>
    <Option Value="0"/>
    <Cylindercal_Face Value="0"/>
    <Single_Face Value="0"/>
    <FillPartialLoop Value="0"/>
    <MeshSize Value="" LocalReMesh="0"/>
    </FillHole>'''
    simlab.execute(FillHoles)

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

def GetCircleInfoFromThreePoints(pt1, pt2, pt3):
        pt1, pt2, pt3 = map(np.array, [pt1, pt2, pt3])

        def NormalDirection(pts):
            p1,p2,p3 = pts
            p1 = np.array(p1)
            p2 = np.array(p2)
            p3 = np.array(p3)

            v1 = (p2 - p1) / np.linalg.norm(p2 - p1)
            v2 = (p3 - p1) / np.linalg.norm(p3 - p1)
            cp = np.cross(v1,v2)

            return cp / np.linalg.norm(cp)

        n = NormalDirection((pt1, pt2, pt3))
        v12 = pt2 - pt1
        v13 = pt3 - pt1

        A = np.array([n, v12, v13])
        B = np.array([np.dot(n,pt1), np.dot(v12,((pt1+pt2)/2)), np.dot(v13,((pt1+pt3)/2))])
        B = B.reshape(len(B),1)
        X = (np.linalg.solve(A, B)).T

        center = np.array(X[0])
        
        r = np.linalg.norm(pt1 - center)
        v_c1 = (pt1 - center) / r

        return center, r, n, v_c1

def createEdgeFromNodes(modelName, startNode, endNode, thirdNode, elemNum):
    CreateEdgeFromNodes=''' <EdgeFromNode UUID="449D18D7-E715-41ce-A640-4AEC18636570" gda="">
    <Name Value="EdgeFromNode2"/>
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
    <Node>'''+ str(thirdNode) +'''</Node>
    </Entities>
    </ThirdNode>
    <NoOfElemChk Value="1"/>
    <NoOfElements Value="'''+ str(elemNum) +'''"/>
    <MeshChk Value="0"/>
    <MeshSize Value="1"/>
    <Radius Value=""/>
    <EquiValence Value="1"/>
    <Output/>
    </EdgeFromNode>'''
    simlab.execute(CreateEdgeFromNodes)

def sweepEdge(modelName, refEdge, guideEdge):
    BasicSweep=''' <BasicSweep UUID="402e0072-ee41-4146-9beb-df148934f541">
    <tag Value="-1"/>
    <EntityList>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(refEdge).strip('()''[]') +'''</Edge>
    </Entities>
    </EntityList>
    <SweepType Value="0"/>
    <SingOrMul Value="0"/>
    <GuideEdgeList>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(guideEdge).strip('()''[]') +'''</Edge>
    </Entities>
    </GuideEdgeList>
    <LayersCheck Value="0"/>
    <NoofLayers Value="0"/>
    <TetExtrude Value="0"/>
    <ElementTypes Value="1"/>
    <RedoFlag Value=""/>
    <Output/>
    </BasicSweep>'''
    simlab.execute(BasicSweep)

def getEdgesOnPlane(modelName, body, pts):
    pt1, pt2, pt3, pt4 = pts
    EdgesByPlane=''' <EdgesByPlane UUID="94ea9e4e-c496-4d6a-950e-66585ed62a28">
    <Name Value="Show Edges"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(body).replace("'", '"').strip('()''[]') +'''</Body>
    </Entities>
    </SupportEntities>
    <Option Value="2"/>
    <On Value="1"/>
    <Above Value="0"/>
    <Below Value="0"/>
    <Tolerance Value="1"/>
    <CreateGroup Value="1"/>
    <RegionObject>
    <Plane>
    <Finite Value="0"/>
    <Pt1 Value="'''+ str(pt1).strip('()''[]') +'''"/>
    <Pt2 Value="'''+ str(pt2).strip('()''[]') +'''"/>
    <Pt3 Value="'''+ str(pt3).strip('()''[]') +'''"/>
    <Pt4 Value="'''+ str(pt4).strip('()''[]') +'''"/>
    </Plane>
    </RegionObject>
    </EdgesByPlane>'''
    simlab.execute(EdgesByPlane)

def createFaceFromEdges(modelName, edge1, edge2):
    CreateFaceFromEdges=''' <FaceUsing2Edges UUID="DDB1E50D-DB65-424c-8E3A-516DD1A7E058" gda="">
    <Name Value="FaceUsing2Edges1"/>
    <tag Value="-1"/>
    <No.OfLayers Value="3"/>
    <EdgeLoop1>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edge1) +'''</Edge>
    </Entities>
    </EdgeLoop1>
    <EdgeLoop2>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edge2) +'''</Edge>
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

def joinBodiesOnMatchingFaces(modelName, bodiesToJoin, tol=1):
    Join=''' <Join CheckBox="ON" UUID="93BDAC5E-9059-42b6-BDC3-EFA346D3DDEC">
    <tag Value="-1"/>
    <Name Value=""/>
    <Pick Value="Join"/>
    <JoinEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(bodiesToJoin).replace("'", '"').strip('()''[]') +'''</Body>
    </Entities>
    </JoinEntities>
    <AlignEntities Value="" ModelIds="" EntityTypes=""/>
    <PreserveEntities Value="" ModelIds="" EntityTypes=""/>
    <Tolerance Value="'''+ str(tol) +'''"/>
    <JoinType Value="GEOM_MATCHING_FACES"/>
    <MeshOrShape Value="Shape"/>
    <MeshOption Value=""/>
    <MeshParam Value=""/>
    <SplitFace Value="1"/>
    <LocalRemesh Value="0"/>
    <ShowOrJoin Value="0"/>
    </Join>'''
    simlab.execute(Join)

def getSharedFace(modelName, bodies):
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
