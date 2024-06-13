# coding: shift-jis
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter.ttk import Separator
import os, sys, importlib
from turtle import width
from PIL import Image, ImageTk
from scipy.misc import face
from hwx import simlab
import numpy as np
import math
import importlib

SRC_DIR = os.path.dirname(os.path.realpath(__file__))
IMAGE_DIR = (os.path.join(SRC_DIR, 'images'))
PROJECT_DIR = os.path.join(SRC_DIR, "..")
LOG_DIR = os.path.join(PROJECT_DIR, "log")

if not SRC_DIR in sys.path:
    sys.path.append(SRC_DIR)

import basedialog
import simlablib
import simlabutil
import filletWelding

class IntermittentWeldingDialog(basedialog.BaseDialog):
    def __init__(self, master, parent, config, backup):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('断続溶接')
        self.master.resizable(width=False, height=False)
        self.master.attributes('-topmost', True)
        self.master.protocol('WM_DELETE_WINDOW', self.CloseDialog)
        self.config = config
        self.backup = backup

        self.weldingFace = 'IntermittentWeldingFace'
        self.projectionFace = 'IntermittentProjectionFace'
        self.weldingEdge = 'IntermittentWeldingEdge'

        self.CreateWidgets()

        groups = [self.weldingFace, self.projectionFace, self.weldingEdge]
        simlablib.DeleteGroups(groups)

        self.UpdateButtonFG()

        simlab.setSelectionFilter('Face')
        simlabutil.ClearSelection()
    
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        tk.Label(self.frmTop, text='ビードを作成するエッジと面を選んで登録してください。').pack(side=tk.TOP, anchor=tk.CENTER)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmFig = tk.Frame(self.frmTop)        
        self.frmFig.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
        self.frmIntermittentWelding = tk.Frame(self.frmFig, width=400)
        self.frmIntermittentWelding.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconIntermittentWeld = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'intermittentWelding.png')), master=self.frmIntermittentWelding)
        tk.Label(self.frmIntermittentWelding, image=self.iconIntermittentWeld).pack(side=tk.LEFT, anchor=tk.W)

        self.btnWeldingFace = tk.Button(self.frmIntermittentWelding, text='基準面', command=self.SelectWeldingFace, width=10)
        self.btnWeldingFace.place(x=50, y=45)

        self.btnProjectionFace = tk.Button(self.frmIntermittentWelding, text='投影面', command=self.SelectProjectionFace, width=10)
        self.btnProjectionFace.place(x=75, y=135)

        self.btnWeldingEdge = tk.Button(self.frmIntermittentWelding, text='エッジ', command=self.SelectWeldingEdge, width=10)
        self.btnWeldingEdge.place(x=195, y=120)

        self.frmBeadInfo = tk.Frame(self.frmTop)
        self.frmBeadInfo.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)

        tk.Label(self.frmBeadInfo, text='ビード情報 :').pack(side=tk.TOP, anchor=tk.NW)

        self.frmBeadInfoGrid = tk.Frame(self.frmBeadInfo)
        self.frmBeadInfoGrid.pack(side=tk.TOP, anchor=tk.NW)
        self.frmBeadInfoGrid.grid_columnconfigure((0,1,3,4), weight=1)

        tk.Label(self.frmBeadInfoGrid, text='基準面ビード脚長: ').grid(row=1, column=0)
        self.entWeldingBeadLength = tk.Entry(self.frmBeadInfoGrid, width=7)
        self.entWeldingBeadLength.grid(row=1, column=1)
        bead_thickness = self.config.Get('Bead_Thickness')
        self.entWeldingBeadLength.insert(tk.END, bead_thickness)

        Separator(self.frmBeadInfoGrid, orient='vertical').grid(row=1, column=2, rowspan=2, sticky='nwse',padx=5)

        tk.Label(self.frmBeadInfoGrid, text='投影面ビード脚長: ').grid(row=2, column=0)
        self.entProjectionBeadLength = tk.Entry(self.frmBeadInfoGrid, width=7)
        self.entProjectionBeadLength.grid(row=2, column=1)  
        self.entProjectionBeadLength.insert(tk.END, bead_thickness)

        tk.Label(self.frmBeadInfoGrid, text=' 溶け込み: ').grid(row=1, column=3)
        self.entWeldingAmount = tk.Entry(self.frmBeadInfoGrid, width=7)
        self.entWeldingAmount.grid(row=1, column=4)
        filletGapFilling = self.config.Get('Fillet_Tokekomi')
        self.entWeldingAmount.insert(tk.END, filletGapFilling)
        
        tk.Label(self.frmBeadInfoGrid, text='ビード要素長:').grid(row=2, column=3)
        self.entBeadElemSize = tk.Entry(self.frmBeadInfoGrid, width=7)
        self.entBeadElemSize.grid(row=2, column=4)
        beadElemSize = self.config.Get('Bead_Elem_Size')
        self.entBeadElemSize.insert(tk.END, beadElemSize)

        tk.Label(self.frmBeadInfoGrid, text='末端処理:').grid(row=3, column=0, columnspan=2)
        self.varBeadEndType = tk.IntVar()
        self.varBeadEndType.set(1)
        self.chkBeadEndType1 = tk.Radiobutton(self.frmBeadInfoGrid, text='フラット', variable=self.varBeadEndType, value=1, command=self.EndTypeCheckCallBack)
        self.chkBeadEndType1.grid(row=3, column=3)
        self.chkBeadEndType2 = tk.Radiobutton(self.frmBeadInfoGrid, text='ラウンド', variable=self.varBeadEndType, value=2, command=self.EndTypeCheckCallBack)
        self.chkBeadEndType2.grid(row=3, column=4)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        Separator(self.frmTop, orient='horizontal').pack(fill='x')

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)
        
        self.frmOption = tk.Frame(self.frmTop)
        self.frmOption.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)

        self.frmOptionTop = tk.Frame(self.frmOption)
        self.frmOptionTop.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmOptionTop, text='エッジ分割オプション :').pack(side=tk.TOP, anchor=tk.W)

        self.frmOption1 = tk.Frame(self.frmOption)
        self.frmOption1.pack(side= tk.LEFT, anchor=tk.CENTER)
        self.varOption = tk.IntVar()
        self.varOption.set(1)
        self.chkOPtion1 = tk.Radiobutton(self.frmOption1, text='ピッチ', variable=self.varOption, value=1, command=self.OptionCheckCallBack)
        self.chkOPtion1.pack(side= tk.LEFT, anchor=tk.W)
        self.iconIntermittentWeldOption1 = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'intermittentOption1.png')), master=self.frmOption1)
        tk.Label(self.frmOption1, image=self.iconIntermittentWeldOption1).pack(side=tk.LEFT, anchor=tk.W)

        self.frmOption2 = tk.Frame(self.frmOption)
        self.frmOption2.pack(side= tk.RIGHT, anchor=tk.CENTER)
        self.chkOPtion2 = tk.Radiobutton(self.frmOption2, text='等分', variable=self.varOption, value=2, command=self.OptionCheckCallBack)
        self.chkOPtion2.pack(side= tk.LEFT, anchor=tk.W)
        self.iconIntermittentWeldOption2 = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'intermittentOption2.png')), master=self.frmOption2)
        tk.Label(self.frmOption2, image=self.iconIntermittentWeldOption2).pack(side=tk.LEFT, anchor=tk.W)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmBeadIntermittentInput = tk.Frame(self.frmTop)
        self.frmBeadIntermittentInput.pack(side=tk.TOP, anchor=tk.CENTER, fill=tk.X, padx=5)

        tk.Label(self.frmBeadIntermittentInput, text='INPUT：').grid(row=0, column=0, sticky='nwse')
        Separator(self.frmBeadIntermittentInput, orient='vertical').grid(row=0, column=1, sticky='nwse',padx=5)
        tk.Label(self.frmBeadIntermittentInput, text='長さ：').grid(row=0, column=2, sticky='nwse')
        self.entBeadWidth = tk.Entry(self.frmBeadIntermittentInput, width=7)
        self.entBeadWidth.grid(row=0, column=3)
        intermittentBeadLength = self.config.Get('Intermittent_Bead_Length')
        self.entBeadWidth.insert(tk.END, intermittentBeadLength)

        tk.Label(self.frmBeadIntermittentInput, text=' 個数：').grid(row=0, column=4, sticky='nwse')
        self.entBeadNums = tk.Entry(self.frmBeadIntermittentInput, width=7)
        self.entBeadNums.grid(row=0, column=5)
        intermittentBeadNums = self.config.Get('Intermittent_Number_Of_Beads')
        self.entBeadNums.insert(tk.END, intermittentBeadNums)

        tk.Label(self.frmBeadIntermittentInput, text=' ピッチ：').grid(row=0, column=6, sticky='nwse')
        self.entBeadPitch = tk.Entry(self.frmBeadIntermittentInput, width=7)
        self.entBeadPitch.grid(row=0, column=7)
        intermittentPitchLength = self.config.Get('Intermittent_Pitch_Length')
        self.entBeadPitch.insert(tk.END, intermittentPitchLength)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)

        self.btnWeld = tk.Button(self.frmCtrl, text=' 作成 ', compound=tk.LEFT, command=self.StartWelding, width=10)
        self.btnWeld.pack(side=tk.LEFT, anchor=tk.NW)        

        self.btnUndo = tk.Button(self.frmCtrl, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=10)
        self.btnUndo.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo)

        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=10)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)
    
    def EndTypeCheckCallBack(self):
        endType = self.varBeadEndType.get()
    
    def OptionCheckCallBack(self):
        optionValue = self.varOption.get()

        if optionValue == 2:
            self.entBeadPitch.config(state='disabled')
        else:
            self.entBeadPitch.config(state='normal')

    
    def SelectWeldingFace(self):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        if len(face) != 1:
            messagebox.showinfo('情報','面一つだけを選択してください。')
            return
        
        simlablib.DeleteGroups(self.weldingFace)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, self.weldingFace)

        self.UpdateButtonFG()

    def SelectProjectionFace(self):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        if len(face) != 1:
            messagebox.showinfo('情報','面一つだけを選択してください。')
            return
        
        simlablib.DeleteGroups(self.projectionFace)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, self.projectionFace)

        self.UpdateButtonFG()

    def SelectWeldingEdge(self):
        edge = simlab.getSelectedEntities('EDGE')
        if len(edge) == 0:
            messagebox.showinfo('情報','エッジを選択した後、ボタンを押してください。')
            return
        
        if len(edge) != 1:
            messagebox.showinfo('情報','エッジ一つだけを選択してください。')
            return
        
        simlablib.DeleteGroups(self.weldingEdge)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Edge', edge, self.weldingEdge)

        self.UpdateButtonFG()
    
    def StartWelding(self):        
        wBeadLen = self.entWeldingBeadLength.get()
        try:
            wBeadLen = float(wBeadLen)
        except ValueError:
            messagebox.showinfo('情報','基準面の脚長で数字を入力してください。')
            return
        else:
            if wBeadLen <= 0:
                messagebox.showinfo('情報','基準面の脚長で０より大きい数字を入力してください。')
                return
        
        pBeadLen = self.entProjectionBeadLength.get()
        try:
            pBeadLen = float(pBeadLen)
        except ValueError:
            messagebox.showinfo('情報','投影面の脚長で数字を入力してください。')
            return
        else:
            if pBeadLen <= 0:
                messagebox.showinfo('情報','投影面の脚長で０より大きい数字を入力してください。')
                return
        
        beadElemSize = self.entBeadElemSize.get()
        try:
            beadElemSize = float(beadElemSize)
        except ValueError:
            messagebox.showinfo('情報','メッシュサイズで数字を入力してください。')
            return
        else:
            if beadElemSize <= 0:
                messagebox.showinfo('情報','メッシュサイズで０より大きい数字を入力してください。')
                return
        
        beadWidth = self.entBeadWidth.get()
        try:
            beadWidth = float(beadWidth)
        except ValueError:
            messagebox.showinfo('情報','ビード長さで数字を入力してください。')
            return
        else:
            if beadWidth <= 0:
                messagebox.showinfo('情報','ビード長さで０より大きい数字を入力してください。')
                return
        
        beadNums = self.entBeadNums.get()
        try:
            beadNums = int(beadNums)
        except ValueError:
            messagebox.showinfo('情報','ビード個数で数字を入力してください。')
            return
        else:
            if beadNums < 2:
                messagebox.showinfo('情報','ビード個数で2以上を入力してください。')
                return
        beadPitchState = self.entBeadPitch.cget(key='state')

        if beadPitchState == 'normal':
            beadPitch = self.entBeadPitch.get()
            # print(beadPitch)
            try:
                beadPitch = float(beadPitch)
            except ValueError:
                messagebox.showinfo('情報','ビードピッチで数字を入力してください。')
                return
            else:
                if beadPitch <= 0:
                    messagebox.showinfo('情報','ビードピッチで2以上を入力してください。')
                    return
        
        wAmount = self.entWeldingAmount.get()
        try:
            wAmount = float(wAmount)
        except ValueError:
            messagebox.showinfo('情報','溶け込みで数字を入力してください。')
            return
        else:
            if wAmount < 0.0:
                messagebox.showinfo('情報','溶け込みで正数または０を入力してください。')
                return
        
        wFace = simlab.getEntityFromGroup(self.weldingFace)
        pFace = simlab.getEntityFromGroup(self.projectionFace)
        if not wFace:
            messagebox.showinfo('情報','基準面を登録してください。')
            return
        if not pFace:
            messagebox.showinfo('情報','投影面を登録してください。')
            return

        wEdge = simlab.getEntityFromGroup(self.weldingEdge)
        if not wEdge:
            messagebox.showinfo('情報','エッジを登録してください。')
            return
        
        beadEndTypeGet = self.varBeadEndType.get()
        beadEndType = 'Flat'
        if beadEndTypeGet == 2:
            beadEndType = 'Round'

        allModelNames = simlab.getAllRootModelNames('FEM')
        if len(allModelNames) > 1:
            messagebox.showinfo('情報','モデル名が複数あります。マージして一個にしてください。')
            return
        elif len(allModelNames) == 0:
            messagebox.showinfo('情報','FEモデルを作成してください。')
            return
        
        beadOption = self.varOption.get()
        #print('beadOption:{}'.format(beadOption))
        
        modelName = simlab.getModelName('FEM')
        
        # check if wEdge is from wFace
        faceEdgeGroup = 'faceEdges'
        simlablib.DeleteGroups(faceEdgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', wFace, 'Edge', faceEdgeGroup)
        wFaceEdges = list(simlab.getEntityFromGroup(faceEdgeGroup))
        if not all(thisEdge in wFaceEdges for thisEdge in wEdge):
            messagebox.showinfo('情報','基準面からエッジを選んでください。')
            return
        
        self.backup.Save('IntermittentWelding')

        vertexGroup = 'edgeVertex'
        simlablib.DeleteGroups(vertexGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Edge', wEdge, 'Vertex', vertexGroup)
        edgeVertexes = simlab.getEntityFromGroup(vertexGroup)
        startVertex = edgeVertexes[0]
        vertexNode = getVertexNode(modelName, startVertex)
        startVertexNode = vertexNode[0]

        lastVertex = edgeVertexes[-1]
        vertexNode = getVertexNode(modelName, lastVertex)
        lastVertexNode = vertexNode[0]

        #print('startVertexNode{}'.format(startVertexNode))
        #print('lastVertexNode{}'.format(lastVertexNode))
        
        edgeUniform(modelName, wEdge)

        edgeNodesInOrder, edgeTotalLength = lineUpNodesFromVertexNode(modelName, wEdge, startVertexNode)
        #print('edgeTotalLength:{}'.format(edgeTotalLength))

        if beadOption == 1:
            lengthRequired = beadWidth*beadNums+beadPitch*(beadNums-1)
        elif beadOption == 2:
            lengthRequired = beadWidth*beadNums

        if lengthRequired > edgeTotalLength + 1e-1:
            messagebox.showinfo('情報','エッジが短すぎて、指定されたビードのinputで作成できません')
            return

        lastAddLength = beadWidth
        cuttingLengthList = []
        if beadOption == 1:
            extraLength = (edgeTotalLength - (beadWidth * beadNums + beadPitch * (beadNums-1))) / 2
            if extraLength <= 1e-1:
                messagebox.showinfo('情報','エッジが短すぎて、指定されたビードのinputで作成できません')
                return
            cuttingLengthList = getEdgeCuttingLengthListFromStartNode(beadNums-1, beadWidth, beadPitch)
            cuttingLengthList = [x + extraLength for x in cuttingLengthList]
            cuttingLengthList.insert(0, extraLength)
            lastAddLength = extraLength

        elif beadOption == 2:
            intervalBetweenBeads = ((edgeTotalLength - 2 * beadWidth) - beadWidth * (beadNums-2)) / (beadNums-1)
            if intervalBetweenBeads <= 1e-1:
                messagebox.showinfo('情報','エッジが短すぎて、指定されたビードのinputで作成できません')
                return
            if beadNums > 2:
                cuttingLengthList = getEdgeCuttingLengthListFromStartNode(beadNums-2, beadWidth, intervalBetweenBeads, optionNum=2)
                # print('cuttingLengthList_before:{}'.format(cuttingLengthList))
                cuttingLengthList = [x + beadWidth for x in cuttingLengthList]
                # print('cuttingLengthList_after:{}'.format(cuttingLengthList))
            elif beadNums == 2:
                cuttingLengthList = [edgeTotalLength-beadWidth]
            
            cuttingLengthList.insert(0, beadWidth)
        
        if (cuttingLengthList[-1] + lastAddLength) > edgeTotalLength + 1e-1:
            messagebox.showinfo('情報','エッジが短すぎて、指定されたビードのinputで作成できません')
            return

        #print('cuttingLengthList:{}'.format(cuttingLengthList))

        cuttingCoordinates=[]
        for thisLength in cuttingLengthList:
            indx, dist = getNodeIndexInDistance(modelName, edgeNodesInOrder, thisLength)
            remainDistance = thisLength - dist
            node1 = edgeNodesInOrder[indx]
            # node2 = edgeNodesInOrder[min(indx+1, nodesNum-1)]
            node2 = edgeNodesInOrder[indx+1]
            thisCutCoord = getCoordinateBetwenNodes(modelName, node1, node2, remainDistance)
            cuttingCoordinates.append(thisCutCoord)
            # newNode = simlab.getNextNodeID(modelName)
            # createNodeByCoordinate(modelName, thisCutCoord, newNode)
    
        #print('cuttingCoordinates:{}'.format(cuttingCoordinates))

        mcName = 'hardPoint_mc'
        simlablib.DeleteMeshControl(mcName)
        hardPointMC(modelName, mcName, wEdge, cuttingCoordinates)

        try:
            aspectRatio = float(self.config.Get('Aspect_Ratio'))
        except ValueError:
            aspectRatio = 10

        remeshEdge(modelName, wEdge, beadElemSize, aspectRatio)
        
        nodeGroups = simlab.getGroupsWithSubString('NodeGroup', ['*'])
        simlablib.DeleteGroups(nodeGroups)
        simlablib.DeleteAllOphanNodes()

        bodyGroup = 'bodyGroup'
        simlablib.DeleteGroups(bodyGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', wFace, 'Body', bodyGroup)
        wFaceBody = simlab.getBodiesFromGroup(bodyGroup)

        cuttingNodes = []
        for thisCoord in cuttingCoordinates:
            nodeOnCoord = getNodeOnCoordinate(modelName, wFaceBody, thisCoord, 0.1)
            cuttingNodes.append(nodeOnCoord)

        #print('cuttingNodes:{}'.format(cuttingNodes))

        # splitEdgeByNodes(modelName, wEdge, cuttingNodes)

        if beadOption == 2:
            cuttingNodes.insert(0, startVertexNode)
            cuttingNodes.append(lastVertexNode)

        nodePair = []

        for idx in range(len(cuttingNodes)-1):
            if idx % 2 == 0:
                nodePair.append((cuttingNodes[idx], cuttingNodes[idx+1]))           

        # print('nodePair:{}'.format(nodePair))
        
        importlib.reload(filletWelding)

        underFaceGroup = 'underFaceGroup'
        simlablib.DeleteGroups(underFaceGroup)
        faceGroup = 'faceGroup'
        simlablib.DeleteGroups(faceGroup)
        wEdge = simlab.getEntityFromGroup(self.weldingEdge)
        simlablib.SelectAssociatedEntities(modelName, 'Edge', wEdge, 'Face', faceGroup)
        adjFaces = simlab.getEntityFromGroup(faceGroup)
        facesAssWEdge = getAnyFacesHavingTheEdge(modelName, adjFaces, wEdge)
        wFace = simlab.getEntityFromGroup(self.weldingFace)
        underFace = list(set(facesAssWEdge) - set(wFace))
        simlablib.CreateGroup(modelName, 'Face', underFace, underFaceGroup)

        bodyFace = 'bodyFaces'
        beforeCutEdgeGroup = 'beforeCutEdges'
        beadfaces = []
        for thisPair in nodePair:
            # print('nodePair:{}'.format(thisPair))
            wEdge = simlab.getEntityFromGroup(self.weldingEdge)

            edgesBeforeCut = getWeldingEdge(modelName, wEdge, thisPair)
            if not edgesBeforeCut:
                continue
            simlablib.DeleteGroups(beforeCutEdgeGroup)
            simlablib.CreateGroup(modelName, 'Edge', edgesBeforeCut, beforeCutEdgeGroup)

            splitEdgeByNodes(modelName, edgesBeforeCut, thisPair)
            edgesAfterCut = simlab.getEntityFromGroup(beforeCutEdgeGroup)
            thisEdge = getWeldingEdge(modelName, edgesAfterCut, thisPair)
            if not thisEdge:
                continue

            wFace = list(set(simlab.getEntityFromGroup(self.weldingFace)) -set(beadfaces))
            pFace = list(set(simlab.getEntityFromGroup(self.projectionFace)) - set(beadfaces))
            # print('wEdge:{}'.format(thisEdge))
            # print('wFace:{}'.format(wFace))
            # print('pFace:{}'.format(pFace))

            beadName = filletWelding.getUniqueBeadName(modelName)
            filletWelding.startWelding(modelName, beadName, thisEdge, wFace, pFace, wBeadLen, pBeadLen, wAmount, beadElemSize, weldEndType=beadEndType)
            beadCreationCheck = simlab.getBodiesWithSubString(modelName, [beadName])
            if beadCreationCheck:
                simlablib.DeleteGroups(bodyFace)
                simlablib.SelectAssociatedEntities(modelName, 'Body', [beadName], 'Face', bodyFace)
                thisBeadFace = list(simlab.getEntityFromGroup(bodyFace))
                beadfaces.extend(thisBeadFace)
        
        if not beadfaces:
            messagebox.showinfo('情報','ビード作成に失敗しました。')
            return

        underFaces = simlab.getEntityFromGroup(underFaceGroup)
        if len(underFaces) > 1:
            simlablib.MergeFaces(modelName, underFaces)
        pFaces = simlab.getEntityFromGroup(self.projectionFace)
        if len(pFaces) > 1:
            simlablib.MergeFaces(modelName, pFaces)
        
        groups = [self.weldingFace, self.projectionFace, self.weldingEdge]
        simlablib.DeleteGroups(groups)
        self.UpdateButtonFG()
    
    def Undo(self):
        self.backup.Load()
        self.UpdateButtonFG()

        modelName = simlab.getModelName('CAD')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')
    
    def UpdateButtonFG(self):
        groups = [self.weldingFace, self.projectionFace, self.weldingEdge]
        widgets = [self.btnWeldingFace, self.btnProjectionFace, self.btnWeldingEdge]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)
    
    def CloseDialog(self):
        super().CloseDialog()

def getWeldingEdge(modelName, edges, nodePair):
    wEdgeNodeDict = dict()
    nodeGroup = 'nodeGroup'
    for thisEdge in edges:
        simlablib.DeleteGroups(nodeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Edge', [thisEdge], 'Node', nodeGroup)
        nodes = list(simlab.getEntityFromGroup(nodeGroup))
        wEdgeNodeDict[thisEdge] = nodes
    

    for keyEdge in wEdgeNodeDict:
        edgeNodes = wEdgeNodeDict[keyEdge]
        if all(node in edgeNodes for node in nodePair):
            return [keyEdge]
    
    return []

def getNodeIndexInDistance(modelName, nodes, dist):
    distCount = 0
    
    for idx in range(len(nodes)):
        if idx == len(nodes)-1:
            break
        p0, p1 = nodes[idx], nodes[idx+1]

        pt0 = np.array(simlab.getNodePositionFromNodeID(modelName, p0))
        pt1 = np.array(simlab.getNodePositionFromNodeID(modelName, p1))
        thisDist = np.linalg.norm(pt0-pt1)
        distCount += thisDist
        if distCount > dist:
            distCount -= thisDist
            return (idx, distCount) 

def edgeUniform(modelName, edge):
    AlignRadial=''' <AlignRadial CheckBox="ON" UUID="0FB98645-1050-4d6e-ABE4-B39FFCD70410">
    <tag Value="-1"/>
    <Name Value=""/>
    <Select Value="Select"/>
    <Edge>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edge).strip('()''[]') +'''</Edge>
    </Entities>
    </Edge>
    <ElemEdge EntityTypes="" ModelIds="" Value=""/>
    <InputType Value="0"/>
    <IndexList Value=""/>
    <AnchorNode EntityTypes="" ModelIds="" Value=""/>
    <Axis Value="Nodes"/>
    <Entity EntityTypes="" ModelIds="" Value=""/>
    </AlignRadial>'''
    simlab.execute(AlignRadial)

def getCoordinateBetwenNodes(modelName, node1, node2, dist):
    node1Pt = np.array(simlab.getNodePositionFromNodeID(modelName, node1))
    node2Pt = np.array(simlab.getNodePositionFromNodeID(modelName, node2))

    v_12 = (node2Pt-node1Pt)/np.linalg.norm(node2Pt-node1Pt)

    return list(node1Pt + v_12*dist)

def hardPointMC(modelName, mcName, edge, dataPts):
    strDataPts = []
    for thisDataList in dataPts:
        strDataPts.extend(thisDataList)
    MeshControls=''' <MeshControl isObject="1" CheckBox="ON" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3">
    <tag Value="-1"/>
    <MeshControlName Value="'''+ mcName +'''"/>
    <MeshControlType Value="Hard Points"/>
    <Entities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edge).strip('()''[]') +'''</Edge>
    </Entities>
    </Entities>
    <Reverse EntityTypes="" ModelIds="" Value=""/>
    <MeshColor Value=""/>
    <HardPoints>
    <Geometry Value="3"/>
    <Tolerance Value="0.1"/>
    <DataPoints Value="'''+ str(strDataPts).strip('()''[]') +'''"/>
    <!-- To specify the csv file path , please uncomment out the below line.   -->
    <!--
    <Hard_Points_File Value="D:/Testing/HardPoints.csv" /> 
            -->
    </HardPoints>
    </MeshControl>'''
    simlab.execute(MeshControls)

def remeshEdge(modelName, edge, avgElemSize, aspectRatio):
    SurfaceLocalRemesh=''' <NewLocalReMesh UUID="83ab93df-8b5e-4a48-a209-07ed417d75bb">
    <tag Value="-1"/>
    <Name Value="NewLocalReMesh1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edge).strip('()''[]') +'''</Edge>
    </Entities>
    </SupportEntities>
    <ElemType Value="0"/>
    <AverageElemSize Value="'''+ str(avgElemSize) +'''"/>
    <MinElemSize Value="'''+ str(avgElemSize/aspectRatio) +'''"/>
    <PreserveBoundaryEdges Value="1"/>
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


def lineUpNodesFromVertexNode(modelName, edge, vertexNode):

    nodeGroup = 'edgeNodes'
    simlablib.DeleteGroups(nodeGroup)
    simlablib.SelectAssociatedEntities(modelName, 'Edge', edge, 'Node', nodeGroup)

    edgeNodes = list(simlab.getEntityFromGroup(nodeGroup))

    nodePtDict = dict()

    for thisNode in edgeNodes:
        thisNodePt = np.array(simlab.getNodePositionFromNodeID(modelName, thisNode))
        nodePtDict[thisNode] = thisNodePt
    
    edgeNodes_copy = edgeNodes[:]
    p0 = vertexNode
    edgeNodes_copy.remove(p0)

    nodesOrderedByDistFromVertexNode = []
    nodesOrderedByDistFromVertexNode.append(p0)
    totalDist = 0

    while len(edgeNodes_copy) != 0:
        neighborNode, dist = getClosestNodeFromANodeWithDistance(nodePtDict, edgeNodes_copy, p0)
        totalDist += dist
        nodesOrderedByDistFromVertexNode.append(neighborNode)
        p0 = neighborNode
        edgeNodes_copy.remove(neighborNode)
    
    return nodesOrderedByDistFromVertexNode, totalDist

def getClosestNodeFromANodeWithDistance(nodePtDict, nodeIdList, fromTheNode):
    # make sure the nodeId list have more than 2 elements
    distDict = dict()
    p0 = nodePtDict[fromTheNode]

    for thisNode in nodeIdList:
        thisNodePt = nodePtDict[thisNode]
        this_d = np.linalg.norm(thisNodePt - p0)
        distDict[thisNode] = this_d
    
    closestNodeId = min(distDict, key= distDict.get)

    return closestNodeId, distDict[closestNodeId]

# def getClosestNodeFromANode(nodePtDict, nodeIdList, fromTheNode):
#     # make sure the nodeId list have more than 2 elements
#     distDict = dict()
#     p0 = nodePtDict[fromTheNode]

#     for thisNode in nodeIdList:
#         thisNodePt = nodePtDict[thisNode]
#         this_d = np.linalg.norm(thisNodePt - p0)
#         distDict[thisNode] = this_d
    
#     closestNodeId = min(distDict, key= distDict.get)

#     return closestNodeId

# def getEdgeInfo(modelName, edgeNodes):
#     nodesNum = len(edgeNodes)
#     if nodesNum < 2:
#         return None

#     node1 = edgeNodes[0]
#     node2 = edgeNodes[1]
#     node1Pt = np.array(simlab.getNodePositionFromNodeID(modelName, node1))
#     node2Pt = np.array(simlab.getNodePositionFromNodeID(modelName, node2))
#     unitLength = np.linalg.norm(node2Pt-node1Pt)

#     return (nodesNum, unitLength)

def getVertexNode(modelName, vertex):
    simlablib.DeleteGroups('vertexNode')
    SelectVertexAssociatedEntities=''' <SelectVertexAssociatedEntities UUID="fc2ece8b-b6e8-4d37-8e27-39a13700fbad">
    <InputVertices Values="">
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Vertex>'''+ str(vertex) +''',</Vertex>
    </Entities>
    </InputVertices>
    <Option Value="Nodes"/>
    <Groupname Value="vertexNode"/>
    </SelectVertexAssociatedEntities>'''
    simlab.execute(SelectVertexAssociatedEntities)

    return simlab.getEntityFromGroup('vertexNode')

def getEdgeCuttingLengthListFromStartNode(beadNum, beadWidth, intervalBetweenBeads, optionNum=1):
    #_______|  |____|  |________

    remainder = 0 if optionNum == 2 else 1
    cuttingNums = beadNum * 2 + 1
    cuttingLength = []
    cumulativeLength = 0
    for i in range(cuttingNums):
        if i%2 == remainder:
            cumulativeLength += intervalBetweenBeads
        else:
            cumulativeLength += beadWidth
        cuttingLength.append(cumulativeLength)
    
    return cuttingLength

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

def getNodeOnCoordinate(modelName, body, coord, incrementBy):
    groupName = 'Show_Nodes'
    simlablib.DeleteGroups(groupName)
    nodeFound = False
    rad = 0.1
    while not nodeFound:
        checkNodeInSphere(modelName, body, rad, coord)
        nodeInSphere = simlab.getEntityFromGroup(groupName)
        if nodeInSphere:
            break
        rad += incrementBy
    
    return nodeInSphere[0]

def checkNodeInSphere(modelName, body, rad, ctp, tol = 0.1):
    NodesByRegion=''' <NodesByRegion UUID="ad9db725-dcb3-4f9c-abd7-0e7a8cf64d05">
    <tag Value="-1"/>
    <Name Value="Show Nodes"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(body).replace("'",'"').strip('()''[]') +'''</Body>
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

def splitEdgeByNodes(modelName, edge, nodes):
    SplitEdge=''' <SplitEdge gda="" UUID="7ECA56CA-94D5-4a21-A88D-59707F8568DC">
    <Name Value="SplitEdge1"/>
    <tag Value="-1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edge).strip('()''[]') +'''</Edge>
    </Entities>
    </SupportEntities>
    <NodeOrVertex Check="1">
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Node>'''+ str(nodes).strip('()''[]') +'''</Node>
    </Entities>
    </NodeOrVertex>
    <Angle Check="0" Value="0.0"/>
    <TopoEdge Check="0" Value=""/>
    <Equivalence Value=""/>
    <MidPoint Check="0" Value=""/>
    <Output/>
    </SplitEdge>'''
    simlab.execute(SplitEdge)

def getAnyFacesHavingTheEdge(modelName, faces, theEdge):
    facesHavingTheEdges = set()
    edgeGroup ='edgeGroup'
    for thisFace in faces:
        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', [thisFace], 'Edge', edgeGroup)
        faceEdges = simlab.getEntityFromGroup(edgeGroup)
        if any(thisEdge in theEdge for thisEdge in faceEdges):
            facesHavingTheEdges.add(thisFace)
    
    return list(facesHavingTheEdges)

    






    