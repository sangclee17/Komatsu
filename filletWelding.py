# coding: shift-jis
import tkinter as tk
import tkinter.messagebox as messagebox
import os, sys
from tkinter.ttk import Separator
from PIL import Image, ImageTk
from hwx import simlab
import numpy as np
import math
import itertools

SRC_DIR = os.path.dirname(os.path.realpath(__file__))
IMAGE_DIR = (os.path.join(SRC_DIR, 'images'))
PROJECT_DIR = os.path.join(SRC_DIR, "..")
LOG_DIR = os.path.join(PROJECT_DIR, "log")

if not SRC_DIR in sys.path:
    sys.path.append(SRC_DIR)

import basedialog
import simlablib
import simlabutil

class FilletWeldingDialog(basedialog.BaseDialog):
    def __init__(self, master, parent, config, backup):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('隅肉溶接')
        self.master.resizable(width=False, height=False)
        self.master.attributes('-topmost', True)
        self.master.protocol('WM_DELETE_WINDOW', self.CloseDialog)
        self.config = config
        self.backup = backup

        self.weldingFace = 'FilletWeldingFace'
        self.projectionFace = 'FilletProjectionFace'
        self.weldingEdge = 'FilletWeldingEdge'

        self.CreateWidgets()

        simlablib.DeleteGroups([self.projectionFace, self.weldingEdge])

        edgeGroups = simlab.getGroupsWithSubString('EdgeGroup',['{}*'.format(self.weldingEdge)])
        simlablib.DeleteGroups(edgeGroups)
        simlablib.DeleteGroups([self.weldingFace, self.projectionFace])

        self.UpdateButtonFG()

        simlabutil.ClearSelection()

        simlab.setSelectionFilter('Face')
    
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        tk.Label(self.frmTop, text='エッジ、面を選択してビード情報を入力してください。').pack(side=tk.TOP, anchor=tk.CENTER)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmFig = tk.Frame(self.frmTop)        
        self.frmFig.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        self.frmFilletWeld = tk.Frame(self.frmFig, width=400)
        self.frmFilletWeld.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconFilletWeld = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'filletWelding.png')), master=self.frmFilletWeld)
        tk.Label(self.frmFilletWeld, image=self.iconFilletWeld).pack(side=tk.LEFT, anchor=tk.W)

        self.iconClearSelection = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'delete-24.png')), master=self.frmFilletWeld)
        self.bntClearSelection = tk.Button(self.frmFilletWeld, image=self.iconClearSelection, command=self.ClearSelection)
        self.bntClearSelection.place(x=5, y=210)

        self.btnWeldingFace = tk.Button(self.frmFilletWeld, text='基準面', command=self.SelectWeldingFace, width=10)
        self.btnWeldingFace.place(x=250, y=95)

        self.btnProjectionFace = tk.Button(self.frmFilletWeld, text='投影面', command=self.SelectProjectionFace, width=10)
        self.btnProjectionFace.place(x=250, y=170)

        self.btnWeldingEdge = tk.Button(self.frmFilletWeld, text='エッジ', command=self.SelectWeldingEdge, width=10)
        self.btnWeldingEdge.place(x=70, y=50)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmBeadInfo = tk.Frame(self.frmTop)
        self.frmBeadInfo.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        tk.Label(self.frmBeadInfo, text='ビード情報 :').pack(side=tk.TOP, anchor=tk.NW)

        self.frmBeadEndType = tk.Frame(self.frmBeadInfo)
        self.frmBeadEndType.pack(side=tk.TOP, anchor=tk.NW, fill=tk.X)
        self.frmBeadEndType.grid_columnconfigure((0,1,2), weight=1)
        tk.Label(self.frmBeadEndType, text='末端処理:').grid(row=0, column=0, sticky='nw')
        self.varBeadEndType = tk.IntVar()
        self.varBeadEndType.set(1)
        self.chkBeadEndType1 = tk.Radiobutton(self.frmBeadEndType, text='フラット', variable=self.varBeadEndType, value=1)
        self.chkBeadEndType1.grid(row=0, column=1,sticky='nwse')
        self.chkBeadEndType2 = tk.Radiobutton(self.frmBeadEndType, text='ラウンド', variable=self.varBeadEndType, value=2)
        self.chkBeadEndType2.grid(row=0, column=2,sticky='nwse')

        self.frmBeadInfoGrid = tk.Frame(self.frmBeadInfo)
        self.frmBeadInfoGrid.pack(side=tk.TOP, anchor=tk.NW)
        self.frmBeadInfoGrid.grid_columnconfigure((0,1,3,4), weight=1)

        self.varCoverWholeFace1 = tk.BooleanVar()
        self.chkAllFace1 = tk.Checkbutton(self.frmBeadInfoGrid, text='基準面全体', variable=self.varCoverWholeFace1, command=self.CoverWholeFace1Callback)
        self.chkAllFace1.grid(row=0, column=0, sticky='nw')

        self.varCornerRound = tk.BooleanVar()
        self.chkCornerRound = tk.Checkbutton(self.frmBeadInfoGrid, text='角部ラウンド', variable=self.varCornerRound)
        self.chkCornerRound.grid(row=0, column=1, sticky='nw', columnspan=3)

        tk.Label(self.frmBeadInfoGrid, text='基準面ビード脚長: ').grid(row=2, column=0)
        self.entWeldingBeadLength = tk.Entry(self.frmBeadInfoGrid, width=7)
        self.entWeldingBeadLength.grid(row=2, column=1)
        bead_thickness = self.config.Get('Bead_Thickness')
        self.entWeldingBeadLength.insert(tk.END, bead_thickness)

        Separator(self.frmBeadInfoGrid, orient='vertical').grid(row=2, column=2, rowspan=2, sticky='nwse',padx=5)

        tk.Label(self.frmBeadInfoGrid, text='投影面ビード脚長: ').grid(row=3, column=0)
        self.entProjectionBeadLength = tk.Entry(self.frmBeadInfoGrid, width=7)
        self.entProjectionBeadLength.grid(row=3, column=1)  
        self.entProjectionBeadLength.insert(tk.END, bead_thickness)

        tk.Label(self.frmBeadInfoGrid, text=' 溶け込み: ').grid(row=2, column=3)
        self.entWeldingAmount = tk.Entry(self.frmBeadInfoGrid, width=7)
        self.entWeldingAmount.grid(row=2, column=4)
        filletGapFilling = self.config.Get('Fillet_Tokekomi')
        self.entWeldingAmount.insert(tk.END, filletGapFilling)
        
        tk.Label(self.frmBeadInfoGrid, text='ビード要素長:').grid(row=3, column=3)
        self.entBeadElemSize = tk.Entry(self.frmBeadInfoGrid, width=7)
        self.entBeadElemSize.grid(row=3, column=4)
        beadElemSize = self.config.Get('Bead_Elem_Size')
        self.entBeadElemSize.insert(tk.END, beadElemSize)

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
    
    def ClearSelection(self):
        edgeGroups = simlab.getGroupsWithSubString('EdgeGroup',['{}*'.format(self.weldingEdge)])
        simlablib.DeleteGroups(edgeGroups)
        simlablib.DeleteGroups([self.weldingFace, self.projectionFace])
        self.UpdateButtonFG()
    
    def CoverWholeFace1Callback(self):
        isChecked = self.varCoverWholeFace1.get()
        if isChecked:
            self.entWeldingBeadLength.config(state='disabled')
        else:
            self.entWeldingBeadLength.config(state='normal')
    
    def SelectWeldingFace(self):
        wFaces = list(simlab.getEntityFromGroup(self.weldingFace))
        face = list(simlab.getSelectedEntities('FACE'))
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        wFaces.extend(face)
        simlablib.DeleteGroups(self.weldingFace)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', wFaces, self.weldingFace)

        self.UpdateButtonFG()

    def SelectProjectionFace(self):
        pFaces = list(simlab.getEntityFromGroup(self.projectionFace))

        face = list(simlab.getSelectedEntities('FACE'))
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        pFaces.extend(face)
        simlablib.DeleteGroups(self.projectionFace)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', pFaces, self.projectionFace)

        self.UpdateButtonFG()

    def SelectWeldingEdge(self):
        wEdges = list(simlab.getEntityFromGroup(self.weldingEdge))

        edge = list(simlab.getSelectedEntities('EDGE'))
        if len(edge) == 0:
            messagebox.showinfo('情報','エッジを選択した後、ボタンを押してください。')
            return
        
        wEdges.extend(edge)
        simlablib.DeleteGroups(self.weldingEdge)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Edge', wEdges, self.weldingEdge)

        self.UpdateButtonFG()
    
    def StartWelding(self):        
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
        
        wBeadLen = 0
        beadAllOnWFace = self.varCoverWholeFace1.get()
        if not beadAllOnWFace:
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
        allModelNames = simlab.getAllRootModelNames('FEM')
        if len(allModelNames) > 1:
            messagebox.showinfo('情報','モデル名が複数あります。マージして一個にしてください。')
            return
        elif len(allModelNames) == 0:
            messagebox.showinfo('情報','FEモデルを作成してください。')
            return
        
        chkCornerRound = self.varCornerRound.get()
        
        beadEndTypeGet = self.varBeadEndType.get()
        beadEndType = 'Flat'
        if beadEndTypeGet == 2:
            beadEndType = 'Round'

        modelName = simlab.getModelName('FEM')
        wFaces = simlab.getEntityFromGroup(self.weldingFace)
        pFace = simlab.getEntityFromGroup(self.projectionFace)
        wEdges = simlab.getEntityFromGroup(self.weldingEdge)
        if not wFaces:
            messagebox.showinfo('情報','基準面を登録してください。')
            return
        if not pFace:
            messagebox.showinfo('情報','投影面を登録してください。')
            return
        if not wEdges:
            messagebox.showinfo('情報','エッジを登録してください。')
            return
        
        # check if all wEdges are from wFaces
        faceEdgeGroup = 'faceEdges'
        simlablib.DeleteGroups(faceEdgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', wFaces, 'Edge', faceEdgeGroup)
        wFaceEdges = list(simlab.getEntityFromGroup(faceEdgeGroup))
        if not all(thisEdge in wFaceEdges for thisEdge in wEdges):
            messagebox.showinfo('情報','基準面からエッジを選んでください。')
            return
        
        self.backup.Save('FilletWelding')

        wEdgeGroups = simlab.createGroupsOfConnectedEntities(self.weldingEdge)

        bodyFace = 'bodyFaces'
        beadfaces = []

        try:
            limitDistance = float(self.config.Get('Fillet_Gap_Limit'))
        except ValueError:
            limitDistance = 3.0
        
        try:
            aspectRatio = float(self.config.Get('Aspect_Ratio'))
        except ValueError:
            aspectRatio = 10
        
        underFaceGroup = 'underFaceGroup'
        simlablib.DeleteGroups(underFaceGroup)
        faceGroup = 'faceGroup'

        for thisGroup in wEdgeGroups:
            simlablib.UpdateModel()
            wEdges = simlab.getEntityFromGroup(thisGroup)
            wFaces = list(set(simlab.getEntityFromGroup(self.weldingFace)) -set(beadfaces))
            pFaces = list(set(simlab.getEntityFromGroup(self.projectionFace)) - set(beadfaces))

            wFaces = getWeldingFaceFromWEdges(modelName, wFaces, wEdges)
            if not wFaces:
                continue

            beadName = getUniqueBeadName(modelName)

            simlablib.DeleteGroups(faceGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Edge', wEdges, 'Face', faceGroup)
            adjFaces = simlab.getEntityFromGroup(faceGroup)
            facesAssWEdge = getAnyFacesHavingTheEdge(modelName, adjFaces, wEdges)

            thisUnderFace = list(set(facesAssWEdge) - set(wFaces))

            if thisUnderFace:
                underFaces = list(simlab.getEntityFromGroup(underFaceGroup))
                simlablib.DeleteGroups(underFaceGroup)
                simlablib.CreateGroup(modelName, 'Face', list(set(underFaces + thisUnderFace)), underFaceGroup)

            startWelding(modelName, beadName, wEdges, wFaces, pFaces, wBeadLen, pBeadLen, wAmount, beadElemSize, beadEndType, gapDistanceLimit=limitDistance, aspectRatio=aspectRatio, cornerRoundChked = chkCornerRound)

            beadCreationChecked = simlab.getBodiesWithSubString(modelName, [beadName])
            if beadCreationChecked:
                simlablib.DeleteGroups(bodyFace)
                simlablib.SelectAssociatedEntities(modelName, 'Body', [beadName], 'Face', bodyFace)
                thisBeadFace = list(simlab.getEntityFromGroup(bodyFace))
                beadfaces.extend(thisBeadFace)
        
        underFaces = simlab.getEntityFromGroup(underFaceGroup)
        if len(underFaces) > 1:
            simlablib.MergeFaces(modelName, underFaces)
        pFaces = simlab.getEntityFromGroup(self.projectionFace)
        if len(pFaces) > 1:
            simlablib.MergeFaces(modelName, pFaces)
        
        if not beadfaces:
            messagebox.showinfo('情報','ビード作成に失敗しました。')
            return

        edgeGroups = simlab.getGroupsWithSubString('EdgeGroup',['{}*'.format(self.weldingEdge)])
        simlablib.DeleteGroups(edgeGroups)
        simlablib.DeleteGroups([self.weldingFace, self.projectionFace])
        self.UpdateButtonFG()

        simlabutil.ClearSelection()

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
        edgeGroups = simlab.getGroupsWithSubString('EdgeGroup',['{}*'.format(self.weldingEdge)])
        simlablib.DeleteGroups(edgeGroups)
        simlablib.DeleteGroups([self.weldingFace, self.projectionFace])

        super().CloseDialog()

def getWeldingFaceFromWEdges(modelName, allFaces, wEdges):
    wFaces = []
    edgeGroup = 'edgeGroup'
    simlablib.DeleteGroups(edgeGroup)
    for thisFace in allFaces:
        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', [thisFace], 'Edge', edgeGroup)
        faceEdges = simlab.getEntityFromGroup(edgeGroup)
        if any(thisEdge in wEdges for thisEdge in faceEdges):
            wFaces.append(thisFace)
    
    return wFaces

def getWFaceFromEdge(modelName, wFaces, theEdge):
    faceEdgeGroup = 'faceEdges'
    for thisFace in wFaces:
        simlablib.DeleteGroups(faceEdgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', [thisFace], 'Edge', faceEdgeGroup)
        faceEdges = list(simlab.getEntityFromGroup(faceEdgeGroup))
        if theEdge in faceEdges:
            return [thisFace]
    return []

def startWelding(modelName, beadName, wEdge, wFace, pFace, wBeadLen, pBeadLen, wAmount, beadElemSize, weldEndType, gapDistanceLimit=3.0, aspectRatio = 10, cornerRoundChked=False):
    # print(modelName, beadName, wEdge, wFace, pFace, wBeadLen, pBeadLen, wAmount, beadElemSize, weldEndType, gapDistanceLimit)

    wFaceGroup = 'wFaceGroup'
    pFaceGroup = 'pFaceGroup'

    simlablib.DeleteGroups(wFaceGroup)
    simlablib.CreateGroup(modelName, 'Face', wFace, wFaceGroup)
    simlablib.DeleteGroups(pFaceGroup)
    simlablib.CreateGroup(modelName, 'Face', pFace, pFaceGroup)
    

    ##############################################################################

    faceGroup = 'faceGroup'
    edgeGroup = 'edgeGroup'
    nodeGroup = 'nodeGroup'
    vertexGroup = 'vertexGroup'

    wEdgeVertexes = getEdgeVertexes(modelName, wEdge)
    IsLoopEdge = checkLoopEdge(modelName, wEdge)

    #print('IsLoopEdge:{}'.format(IsLoopEdge))
    ###################################################################################
    # From 2 to 3
   
    simlablib.DeleteGroups(faceGroup)
    simlablib.SelectAssociatedEntities(modelName, 'Edge', wEdge, 'Face', faceGroup)
    adjFaces = simlab.getEntityFromGroup(faceGroup)
    facesAssWEdge = getAnyFacesHavingTheEdge(modelName, adjFaces, wEdge)
    faceUnder12 = list(set(facesAssWEdge) - set(wFace))

    imprintEdgeOnFaceGroup = 'Imprint_EdgeOn_Face'
    simlablib.DeleteGroups(imprintEdgeOnFaceGroup)
    imprintEdgeOnFace(modelName, wEdge, pFace)
    imprintedWEdge = simlab.getEntityFromGroup(imprintEdgeOnFaceGroup)
    # print('imprintedWEdge:{}'.format(imprintedWEdge))
    if not imprintedWEdge:
        print('Fail to imprint the welding edge on proj face.')
        return
    
    imprintedWEdgeGroup = 'imprintedWEdgeGroup'
    simlablib.DeleteGroups(imprintedWEdgeGroup)
    simlablib.CreateGroup(modelName, 'Edge', imprintedWEdge, imprintedWEdgeGroup)
    
    pFaces = simlab.getEntityFromGroup(pFaceGroup)
    pFacesAssImprintedWEdge = getAnyFacesHavingTheEdge(modelName, pFaces, imprintedWEdge)
    #print('pFacesAssImprintedWEdge:{}'.format(pFacesAssImprintedWEdge))
    simlablib.DeleteGroups(pFaceGroup)
    simlablib.CreateGroup(modelName, 'Face', pFacesAssImprintedWEdge, pFaceGroup)
    
    wEdgeNodes = getEdgeNodes(modelName, wEdge)
    skimaGap = getMinDistanceBetweenNodeAndEdge(modelName, imprintedWEdge, wEdgeNodes[0])
    # print('skimaGap:{}'.format(skimaGap))

    simlablib.DeleteGroups(faceGroup)
    simlablib.CreateGroup(modelName, 'Face', faceUnder12, faceGroup)

    edgesBefore = getFaceEdges(modelName, faceUnder12)
    if wAmount > 0.0:
        createEdgeByOffset(modelName, faceUnder12, wEdge, wAmount, 1)
    else:
        createEdgeByOffset(modelName, faceUnder12, wEdge, beadElemSize, 1)

    faceUnder12 = simlab.getEntityFromGroup(faceGroup)

    face2_3 = getAnyFacesHavingTheEdge(modelName, faceUnder12, wEdge)

    if not face2_3:
        print('Fail to create face2_3 by edge offset')
        return

    ###################################################################################
    # From 1 to 2

    newFace1_2 = False
    if wBeadLen == 0.0:
        faceEdges = getFaceEdges(modelName, wFace)
        face1_2 = wFace
        edge1 = getFaceEdgeNotAssociatedWithRefEdge(modelName, faceEdges, wEdgeVertexes)

    else:
        if wBeadLen <= skimaGap:
            print('reference bead length less than gap lenth error')
            # print('隙間より大きい基準面脚長を入力してください。')
            return

        wFaceOffsetDistance = int((wBeadLen - skimaGap) * 100)/100

        edgesBefore = getFaceEdges(modelName, wFace)
        createEdgeByOffset(modelName, wFace, wEdge, wFaceOffsetDistance, 1)
        wFace = simlab.getEntityFromGroup(wFaceGroup)
        edgesAfter = getFaceEdges(modelName, wFace)
        newEdges = list(set(edgesAfter) - set(edgesBefore))
        if not newEdges:
            face1_2 = wFace
        else:
            face1_2 = getAnyFacesHavingTheEdge(modelName, wFace, wEdge)
    
        if not face1_2:
            print('error: Fail to create edges on wFace by edge offset')
            return

        faceEdges = getFaceEdges(modelName, face1_2)
        edge1 = getFaceEdgeNotAssociatedWithRefEdge(modelName, faceEdges, wEdgeVertexes)
        newFace1_2 = True
    
    splitNodePtsOnFace12 = []
    face1_2Round = False
    if weldEndType.lower() == 'round' and not IsLoopEdge and newFace1_2 and wBeadLen != 0.0:
        face12Group = 'face1_2'
        simlablib.DeleteGroups(face12Group)
        simlablib.CreateGroup(modelName, 'Face', face1_2, face12Group)

        endVertexesLow = getStartAndEndEdgeVertexes(modelName, wEdge, wEdgeVertexes)
        #print('endVertexesLow:{}'.format(endVertexesLow))

        edge1Vertexes = getEdgeVertexes(modelName, edge1)
        endVertexesTop = getStartAndEndEdgeVertexes(modelName, edge1, edge1Vertexes)

        vertexPair = getConnectedEdgeVertexPair(modelName, endVertexesTop, endVertexesLow)

        #print('vertexPair:{}'.format(vertexPair))      

        vertexNodePair = []
        # p0, p1, p2 
        for thisPair in vertexPair:
            v0, v1 = thisPair
            
            simlablib.DeleteGroups(nodeGroup)
            vertexNode = getVertexNode(modelName, v0, nodeGroup)
            p0 =  vertexNode[0]
            nodesInOrder = lineUpNodesFromVertexNode(modelName, edge1, p0)
            indx, dist = getNodeIndexInDistance(modelName, nodesInOrder, wFaceOffsetDistance)

            remainDistance = wFaceOffsetDistance - dist

            p2_pt = getCoordinateBetwenNodes(modelName, nodesInOrder[indx], nodesInOrder[indx+1], remainDistance)
            # print('p2_pt:{}'.format(p2_pt))
            p2 = simlab.getNextNodeID(modelName)

            createNodeByXYZ(modelName, p2_pt, p2)

            simlablib.DeleteGroups(nodeGroup)
            vertexNode = getVertexNode(modelName, v1, nodeGroup)
            p1 = vertexNode[0]

            vertexNodePair.append((p0,p1,p2))

        # print('vertexNodePair:{}'.format(vertexNodePair))
        
        edgeBodies = []
        for thisPair in vertexNodePair:
            p0,p1,p2 = thisPair

            pt0 = np.array(simlab.getNodePositionFromNodeID(modelName, p0))
            pt1 = np.array(simlab.getNodePositionFromNodeID(modelName, p1))
            pt2 = np.array(simlab.getNodePositionFromNodeID(modelName, p2))

            print('pt0:{}'.format(pt0))
            print('pt1:{}'.format(pt1))
            print('pt2:{}'.format(pt2))

            v0_12 = (pt1+pt2)/2 - pt0
            n0_12 = v0_12 / np.linalg.norm(v0_12)
            dist = wFaceOffsetDistance * math.sqrt(2) - wFaceOffsetDistance
            byNode_pt = pt0 + n0_12*dist

            # byNode_pt = pt0 + ((pt1+pt2)/2 - pt0) / 2
            # print('byNode_pt:{}'.format(byNode_pt))
            
            p3 = simlab.getNextNodeID(modelName)

            createNodeByXYZ(modelName, list(byNode_pt), p3)

            # n10 = (pt0 - pt1) / np.linalg.norm(pt0 - pt1)
            # pt2 + n10 * np.linalg.norm(pt0 - pt1)

            splitNodePtsOnFace12.append([list(pt2), list(pt2 + pt1 - pt0)])

            # nextNode = simlab.getNextNodeID(modelName)
            # createNodeByXYZ(modelName, list(pt1), nextNode)

            # nextNode = simlab.getNextNodeID(modelName)
            # createNodeByXYZ(modelName, list(pt2), nextNode)

            beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            # createArcEdge(modelName, p1, p2, p3, math.floor(wFaceOffsetDistance*math.pi/2/4))
            createArcEdge(modelName, p1, p2, p3, 8)
            afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            newBody = list(set(afterBodies) - set(beforeBodies))
            for thisBody in newBody:
                edgeBodies.append(thisBody)

        if edgeBodies:
            simlablib.DeleteGroups(edgeGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Body', edgeBodies, 'Edge', edgeGroup)
            arcEdges = simlab.getEntityFromGroup(edgeGroup)

            imprintEdgeOnFaceGroup = 'Imprint_EdgeOn_Face'
            simlablib.DeleteGroups(imprintEdgeOnFaceGroup)

            imprintEdgeOnFace(modelName, arcEdges, face1_2)
            imprintedArcEdges = simlab.getEntityFromGroup(imprintEdgeOnFaceGroup)
            #print('imprintedArcEdges:{}'.format(imprintedArcEdges))
            
            allWFaces = simlab.getEntityFromGroup(face12Group)
            face1_2 = getAnyFacesHavingTheEdge(modelName, allWFaces, wEdge)

            simlablib.DeleteEntities(modelName, 'Body', edgeBodies)

            face1_2Round = True
    
    # print('splitNodePtsOnFace12:{}'.format(splitNodePtsOnFace12))

    # print('edge1:{}'.format(edge1))
    #print('face1_2:{}'.format(face1_2))
    bodiesToMerge = []
    beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
    createBodyFromFaces(modelName, face1_2)
    afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
    newWBody = list(set(afterBodies) -set(beforeBodies))
    for thisBody in newWBody:
        bodiesToMerge.append(thisBody)
    
    faceEdges = getFaceEdges(modelName, face2_3)
    edgesToImprint = list(set(faceEdges)-set(wEdge))
    edge3 = getFaceEdgeNotAssociatedWithRefEdge(modelName, faceEdges, wEdgeVertexes)
    # print('edgesToImprint:{}'.format(edgesToImprint))

    simlablib.DeleteGroups(imprintEdgeOnFaceGroup)
    pFace = simlab.getEntityFromGroup(pFaceGroup)
    # print('pFace:{}'.format(pFace))
    imprintEdgeOnFace(modelName, edgesToImprint, pFace)

    imprintedEdge2_3 = simlab.getEntityFromGroup(imprintEdgeOnFaceGroup)
    #print('imprintedEdge2_3:{}'.format(imprintedEdge2_3))
    if not imprintedEdge2_3:
        print('Fail to imprint edge 2_3 on proj face.')
        return
    
    simlablib.DeleteGroups(edgeGroup)
    simlablib.CreateGroup(modelName, 'Edge', imprintedEdge2_3, edgeGroup)
    splitEdgeByAngle(modelName, imprintedEdge2_3)
    imprintedEdge2_3 = simlab.getEntityFromGroup(edgeGroup)
    #print('imprintedEdge2_3:{}'.format(imprintedEdge2_3))
    imprintedWEdge = simlab.getEntityFromGroup(imprintedWEdgeGroup)
    imprintedEdgesOnPFace = list(imprintedEdge2_3) + list(imprintedWEdge)
    # print('imprintedEdgesOnPFace:{}'.format(imprintedEdgesOnPFace))

    allPFaces = simlab.getEntityFromGroup(pFaceGroup)
    #print('allPFaces:{}'.format(allPFaces))
    faceEdgeDict = dict()
    for thisFace in allPFaces:
        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', [thisFace], 'Edge', edgeGroup)
        faceEdges = simlab.getEntityFromGroup(edgeGroup)
        leftOverEdges = list(set(faceEdges) - set(imprintedEdgesOnPFace))
        faceEdgeDict[thisFace] = len(leftOverEdges)
    #print('faceEdgeDict:{}'.format(faceEdgeDict))

    sortedEdges = [thisTup[0] for thisTup in sorted(faceEdgeDict.items(), key=lambda x: x[1])]

    face4_5 = sortedEdges[:len(wEdge)]
    # print('face4_5:{}'.format(face4_5))
        
    if not face4_5:
        print('Fail to create face4_5 on pFace')
        return

    # From 2 to 5
    if wAmount > 0.0:
        imprintedWEdgeVertexes = getEdgeVertexes(modelName, imprintedWEdge)
        faceEdges = getFaceEdges(modelName, face4_5)
        edge4 = getFaceEdgeNotAssociatedWithRefEdge(modelName, faceEdges, imprintedWEdgeVertexes)
        
        # print('face2_3:{}'.format(face2_3))
        # beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        # createBodyFromFaces(modelName, face2_3)
        # afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        # newBody = list(set(afterBodies) - set(beforeBodies))
        # for thisBody in newBody:
        #     bodiesToMerge.append(thisBody)
        
        # print('skimaGap:{}'.format(skimaGap))
        # print('gapDistanceLimit:{}'.format(gapDistanceLimit))

        if skimaGap > gapDistanceLimit:
            beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            createBodyFromFaces(modelName, face2_3)
            afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            newBody = list(set(afterBodies) - set(beforeBodies))
            for thisBody in newBody:
                bodiesToMerge.append(thisBody)

            beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            createFaceFromEdges(modelName, edge3, edge4, max(int(round(skimaGap/beadElemSize)), 1))
            afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            newBody = list(set(afterBodies) - set(beforeBodies))
            for thisBody in newBody:
                bodiesToMerge.append(thisBody)
            
            beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            createBodyFromFaces(modelName, face4_5)
            afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            newBody = list(set(afterBodies) - set(beforeBodies))
            for thisBody in newBody:
                bodiesToMerge.append(thisBody)
        else:
            allPFaces = list(simlab.getEntityFromGroup(pFaceGroup))
            # print('allPFaces:{}'.format(allPFaces))
            facesToJoin = allPFaces+face2_3
            # print('facesToJoin:{}'.format(facesToJoin))
            joinTol = max(skimaGap, 0.1)
            joinOverlappingFaces(modelName, facesToJoin, joinTol)
            
            # print('edgesToImprint:{}'.format(edgesToImprint))
            allPFaces = simlab.getEntityFromGroup(pFaceGroup)
            closeGapBetwenEdgeAndFace(modelName, edgesToImprint, allPFaces)
            afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            newBody = list(set(afterBodies) - set(beforeBodies))
            for thisBody in newBody:
                bodiesToMerge.append(thisBody)

            allPFaces = simlab.getEntityFromGroup(pFaceGroup)
            allWFaces = simlab.getEntityFromGroup(wFaceGroup)

            intersectingEdge = getIntersectingEdgeOfTwoFaces(modelName, allPFaces, allWFaces)
            wEdge = intersectingEdge
            imprintedWEdge = intersectingEdge
        
        # beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        # createBodyFromFaces(modelName, face4_5)
        # afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        # newBody = list(set(afterBodies) - set(beforeBodies))
        # for thisBody in newBody:
        #     bodiesToMerge.append(thisBody)
        
        # print('face4_5:{}'.format(face4_5))

    else:
        # From 2 to 5
        allPFaces = simlab.getEntityFromGroup(pFaceGroup)

        beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        closeGapBetwenEdgeAndFace(modelName, wEdge, allPFaces)
        afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        newBody = list(set(afterBodies) - set(beforeBodies))
        for thisBody in newBody:
            bodiesToMerge.append(thisBody)

        allWFaces = simlab.getEntityFromGroup(wFaceGroup)
        if newBody:
            simlablib.DeleteGroups(faceGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Body', newBody, 'Face', faceGroup)
            newBodyFaces = simlab.getEntityFromGroup(faceGroup)
            imprintedWEdge = getIntersectingEdgeOfTwoFaces(modelName, newBodyFaces, allPFaces)
            wEdge = getIntersectingEdgeOfTwoFaces(modelName, newBodyFaces, allWFaces)
        else:
            intersectingEdge = getIntersectingEdgeOfTwoFaces(modelName, allPFaces, allWFaces)
            wEdge = intersectingEdge
            imprintedWEdge = intersectingEdge

    ###################################################################################
    # From 5 to 6
    allPFaces = simlab.getEntityFromGroup(pFaceGroup)
    outerPFace = list(set(allPFaces) - set(face4_5))
    # print('outerPFace:{}'.format(outerPFace))

    simlablib.DeleteGroups(faceGroup)
    simlablib.CreateGroup(modelName, 'Face', outerPFace, faceGroup)

    edgesBefore = getFaceEdges(modelName, outerPFace)
    # print('imprintedWEdge:{}'.format(imprintedWEdge))
    createEdgeByOffset(modelName, outerPFace, imprintedWEdge, pBeadLen, 1)
    outerPFace = simlab.getEntityFromGroup(faceGroup)

    # print('outerPFace:{}'.format(outerPFace))

    face5_6 = getAnyFacesHavingTheEdge(modelName, outerPFace, imprintedWEdge)
  
    faceEdges = getFaceEdges(modelName, face5_6)

    imprintedWEdgeVertexes= getEdgeVertexes(modelName, imprintedWEdge)
    
    edge6 = getFaceEdgeNotAssociatedWithRefEdge(modelName, faceEdges, imprintedWEdgeVertexes)
    simlablib.DeleteGroups(edgeGroup)
    simlablib.CreateGroup(modelName, 'Edge', edge6, edgeGroup)
    splitEdgeByAngle(modelName, edge6)
    edge6 = simlab.getEntityFromGroup(edgeGroup)

    # print('face5_6:{}'.format(face5_6))
    # print('edge6:{}'.format(edge6))
    if face5_6 is None:
        print('Fail to create a face5_6 by edge offset')
        return

    splitNodePtsOnFace56 = []
    face5_6Round = False
    if weldEndType.lower() == 'round' and not IsLoopEdge:
        face5_6Group = 'face5_6'
        simlablib.DeleteGroups(face5_6Group)
        simlablib.CreateGroup(modelName, 'Face', [face5_6], face5_6Group)

        endVertexesLow = getStartAndEndEdgeVertexes(modelName, imprintedWEdge, imprintedWEdgeVertexes)
        #print('endVertexesLow:{}'.format(endVertexesLow))

        edge6Vertexes = getEdgeVertexes(modelName, edge6)
        endVertexesTop = getStartAndEndEdgeVertexes(modelName, edge6, edge6Vertexes)

        vertexPair = getConnectedEdgeVertexPair(modelName, endVertexesTop, endVertexesLow)
        #print('vertexPair:{}'.format(vertexPair))

        vertexNodePair = []
        # p0, p1, p2 
        for thisPair in vertexPair:
            v0, v1 = thisPair
            
            simlablib.DeleteGroups(nodeGroup)
            vertexNode = getVertexNode(modelName, v0, nodeGroup)
            p0 =  vertexNode[0]
            nodesInOrder = lineUpNodesFromVertexNode(modelName, edge6, p0)
            indx, dist = getNodeIndexInDistance(modelName, nodesInOrder, pBeadLen)

            remainDistance = pBeadLen - dist

            p2_pt = getCoordinateBetwenNodes(modelName, nodesInOrder[indx], nodesInOrder[indx+1], remainDistance)

            p2 = simlab.getNextNodeID(modelName)

            createNodeByXYZ(modelName, p2_pt, p2)

            simlablib.DeleteGroups(nodeGroup)
            vertexNode = getVertexNode(modelName, v1, nodeGroup)
            p1 = vertexNode[0]

            vertexNodePair.append((p0,p1,p2))
        #print('vertexNodePair:{}'.format(vertexNodePair))

        edgeBodies = []
        for thisPair in vertexNodePair:
            p0,p1,p2 = thisPair

            pt0 = np.array(simlab.getNodePositionFromNodeID(modelName, p0))
            pt1 = np.array(simlab.getNodePositionFromNodeID(modelName, p1))
            pt2 = np.array(simlab.getNodePositionFromNodeID(modelName, p2))

            v0_12 = (pt1+pt2)/2 - pt0
            n0_12 = v0_12 / np.linalg.norm(v0_12)
            dist = pBeadLen * math.sqrt(2) - pBeadLen
            byNode_pt = pt0 + n0_12*dist

            # byNode_pt = pt0 + ((pt1+pt2)/2 - pt0)/2
            # print('byNode_pt:{}'.format(byNode_pt))
            
            p3 = simlab.getNextNodeID(modelName)

            createNodeByXYZ(modelName, list(byNode_pt), p3)
            splitNodePtsOnFace56.append([list(pt2), list(pt2 + pt1 - pt0)])

            beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            
            # createArcEdge(modelName, p1, p2, p3, math.floor(pBeadLen*math.pi/2/4))
            createArcEdge(modelName, p1, p2, p3, 8)

            afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            newBody = list(set(afterBodies) - set(beforeBodies))
            for thisBody in newBody:
                edgeBodies.append(thisBody)

        if edgeBodies:
            simlablib.DeleteGroups(edgeGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Body', edgeBodies, 'Edge', edgeGroup)
            arcEdges = simlab.getEntityFromGroup(edgeGroup)

            imprintEdgeOnFaceGroup = 'Imprint_EdgeOn_Face'
            simlablib.DeleteGroups(imprintEdgeOnFaceGroup)
            imprintEdgeOnFace(modelName, arcEdges, face5_6)
            # imprintedArcEdges = simlab.getEntityFromGroup(imprintEdgeOnFaceGroup)
            #print('imprintedArcEdges:{}'.format(imprintedArcEdges))

            allPFaces = simlab.getEntityFromGroup(face5_6Group)
            face5_6 = getAnyFacesHavingTheEdge(modelName, allPFaces, imprintedWEdge)

            face5_6Round = True

            simlablib.DeleteEntities(modelName, 'Body', edgeBodies)
    
    # print('splitNodePtsOnFace56:{}'.format(splitNodePtsOnFace56))
    
    if cornerRoundChked:
        intersectingCornerEdgesOnFace5_6 = []
        if len(face5_6) > 1:
            for face1, face2 in itertools.combinations(face5_6, 2):
                intersectingEdges = getIntersectingEdgeOfTwoFaces(modelName, [face1], [face2])
                if intersectingEdges:
                    intersectingCornerEdgesOnFace5_6.extend(intersectingEdges)
        # print('intersectingCornerEdgesOnFace5_6:{}'.format(intersectingCornerEdgesOnFace5_6))

        face5_6Edges = getFaceEdges(modelName, face5_6)
        if not face5_6Round:
            simlablib.DeleteGroups(edgeGroup)
            simlablib.CreateGroup(modelName, 'Edge', face5_6Edges, edgeGroup)
            splitEdgeByAngle(modelName, face5_6Edges)
            face5_6Edges = simlab.getEntityFromGroup(edgeGroup)
            
            imprintedWEdgeVertexes = getEdgeVertexes(modelName, imprintedWEdge)
            edge6 = getFaceEdgeNotAssociatedWithRefEdge(modelName, face5_6Edges, imprintedWEdgeVertexes)
        else:
            edge6 = list(set((set(face5_6Edges) -set(imprintedWEdge))) -set(intersectingCornerEdgesOnFace5_6))

        cornerNodeEdgeDict = dict()
        for thisCornerEdge in intersectingCornerEdgesOnFace5_6:
            for thisEdge in edge6:
                intersectingNode = getIntersectingNodeOfTwoEdges(modelName, [thisCornerEdge], [thisEdge])
                if intersectingNode:
                    keyNode = intersectingNode[0]
                    closestNodeFromKeyNode = getClosestEdgeNodeFrom(modelName, [thisEdge], keyNode)
                    if keyNode in cornerNodeEdgeDict:
                        cornerNodeEdgeDict[keyNode].append(closestNodeFromKeyNode)
                    else:
                        cornerNodeEdgeDict[keyNode] = [closestNodeFromKeyNode]

        # print('cornerNodeEdgeDict:{}'.format(cornerNodeEdgeDict))

        edgeBodies = []
        for thisKeyNode in cornerNodeEdgeDict:
            # print('thisKeyNode:{}'.format(thisKeyNode))
            cornerNodes = cornerNodeEdgeDict[thisKeyNode]
            if len(cornerNodes) != 2:
                continue
            pt0 = np.array(simlab.getNodePositionFromNodeID(modelName, thisKeyNode))
            p1_, p2_ = cornerNodes
            pt1_ = np.array(simlab.getNodePositionFromNodeID(modelName, p1_))
            n01 = (pt1_ - pt0) / np.linalg.norm(pt1_ - pt0)
            pt1 = pt0 + n01 * pBeadLen

            pt2_ = np.array(simlab.getNodePositionFromNodeID(modelName, p2_))
            n02 = (pt2_ - pt0) /  np.linalg.norm(pt2_ - pt0)
            pt2 = pt0 + n02 * pBeadLen

            pt3 = (pt1 + pt2) / 2
            n03 = (pt3 - pt0) / np.linalg.norm(pt3 - pt0)
            pt4 = pt0 + n03 *  np.linalg.norm(pt3 - pt0) / 2

            n10 = -1 * n01

            dotPro = np.dot(n10, n02)
            # print('dotPro:{}'.format(dotPro))
            if dotPro < 0.5:
                startNodeId = simlab.getNextNodeID(modelName)
                createNodeByXYZ(modelName, list(pt1), startNodeId)
                endNodeId = simlab.getNextNodeID(modelName)
                createNodeByXYZ(modelName, list(pt2), endNodeId)
                byNodeId = simlab.getNextNodeID(modelName)
                createNodeByXYZ(modelName, list(pt4), byNodeId)
                beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
                # createArcEdge(modelName, startNodeId, endNodeId, byNodeId, np.linalg.norm(pt1-pt2)/math.sqrt(2)*3.14/2/6)
                createArcEdge(modelName, startNodeId, endNodeId, byNodeId, 8)
                afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
                newBody = list(set(afterBodies) - set(beforeBodies))
                for thisBody in newBody:
                    edgeBodies.append(thisBody)
        if edgeBodies:
            face5_6Group = 'face5_6'
            simlablib.DeleteGroups(face5_6Group)
            simlablib.CreateGroup(modelName, 'Face', [face5_6], face5_6Group)

            simlablib.DeleteGroups(edgeGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Body', edgeBodies, 'Edge', edgeGroup)
            arcEdges = simlab.getEntityFromGroup(edgeGroup)

            imprintEdgeOnFaceGroup = 'Imprint_EdgeOn_Face'
            simlablib.DeleteGroups(imprintEdgeOnFaceGroup)
            imprintEdgeOnFace(modelName, arcEdges, face5_6)
            # imprintedArcEdges = simlab.getEntityFromGroup(imprintEdgeOnFaceGroup)
            #print('imprintedArcEdges:{}'.format(imprintedArcEdges))

            allPFaces = simlab.getEntityFromGroup(face5_6Group)
            face5_6 = getAnyFacesHavingTheEdge(modelName, allPFaces, imprintedWEdge)

            simlablib.DeleteEntities(modelName, 'Body', edgeBodies)
    
    # print('face1_2:{}'.format(face1_2))
    # print('face5_6:{}'.format(face5_6))

    beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
    createBodyFromFaces(modelName, face5_6)
    afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
    newPBody = list(set(afterBodies) - set(beforeBodies))
    for thisBody in newPBody:
        bodiesToMerge.append(thisBody)

    if bodiesToMerge:
        if face1_2Round and face5_6Round:
            simlablib.DeleteGroups(faceGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Body', bodiesToMerge, 'Face', faceGroup)
            beadFaces = simlab.getEntityFromGroup(faceGroup)
            wFaces = simlab.getEntityFromGroup(wFaceGroup)
            facesToMerge = list(set(wFaces) - set(beadFaces))
            simlablib.MergeFaces(modelName, facesToMerge)

            pFaces = simlab.getEntityFromGroup(faceGroup)
            pFaces = simlab.getEntityFromGroup(pFaceGroup)
            facesToMerge = list(set(pFaces) - set(beadFaces))
            simlablib.MergeFaces(modelName, facesToMerge)
        

        simlablib.UpdateModel()
        mergeBodies(modelName, bodiesToMerge, beadName)
        newBead = simlab.getBodiesWithSubString(modelName, [beadName])
        if not newBead:
            return
        
        # simlablib.DeleteGroups(edgeGroup)
        # simlablib.SelectAssociatedEntities(modelName, 'Face', face1_2, 'Edge', edgeGroup)
        # faceEdges = simlab.getEntityFromGroup(edgeGroup)
        # mcName1 = 'edgeMeshControl_1'
        # simlablib.DeleteMeshControl(mcName1)
        # uniformEdgeSeedingMC(mcName1, modelName, faceEdges, beadElemSize)

        # simlablib.DeleteGroups(edgeGroup)
        # simlablib.SelectAssociatedEntities(modelName, 'Face', face5_6, 'Edge', edgeGroup)
        # faceEdges = simlab.getEntityFromGroup(edgeGroup)
        # mcName2 = 'edgeMeshControl_2'
        # simlablib.DeleteMeshControl(mcName2)
        # uniformEdgeSeedingMC(mcName2, modelName, faceEdges, beadElemSize)

        mcName = 'preserveEdgeMC'
        simlablib.DeleteMeshControl(mcName)
        preserveFaceEdgeMC(mcName, modelName, list(face1_2)+list(face5_6))
        simlablib.DeleteGroups(faceGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Body', newBead, 'Face', faceGroup)
        beadFaces = simlab.getEntityFromGroup(faceGroup)
        # print('beadFaces:{}'.format(beadFaces))
        remeshFace(modelName, beadFaces, beadElemSize, aspectRatio, preserveBoundary=0)


    # print('imprintedWEdge:{}'.format(imprintedWEdge))
    # print('edge6:{}'.format(edge6))
    # print('edge1:{}'.format(edge1))
    #print('face5_6:{}'.format(face5_6))
    
    # print('wEdge:{}'.format(wEdge))

    # print('face5_6:{}'.format(face5_6))


    allNodeGroups = simlab.getGroupsWithSubString('NodeGroup', ['*'])
    simlablib.DeleteGroups(allNodeGroups)
    simlablib.DeleteAllOphanNodes()

    intersectingCornerEdgesOnFace1_2 = []
    if len(face1_2) > 1:
        for face1, face2 in itertools.combinations(face1_2, 2):
            intersectingEdges = getIntersectingEdgeOfTwoFaces(modelName, [face1], [face2])
            if intersectingEdges:
                intersectingCornerEdgesOnFace1_2.extend(intersectingEdges)
    
    face1_2Edges = getFaceEdges(modelName, face1_2)
    # print('face1_2Edges:{}'.format(face1_2Edges))
    
    if not face1_2Round:
        simlablib.DeleteGroups(edgeGroup)
        simlablib.CreateGroup(modelName, 'Edge', face1_2Edges, edgeGroup)
        splitEdgeByAngle(modelName, face1_2Edges)
        
        wEdgeVertexes = getEdgeVertexes(modelName, wEdge)
        # print('wEdgeVertexes:{}'.format(wEdgeVertexes))
        face1_2Edges = simlab.getEntityFromGroup(edgeGroup)
        edge1 = getFaceEdgeNotAssociatedWithRefEdge(modelName, face1_2Edges, wEdgeVertexes)
    else:
        edge1 = list(set((set(face1_2Edges) -set(wEdge))) -set(intersectingCornerEdgesOnFace1_2))

    intersectingCornerEdgesOnFace5_6 = []
    if len(face5_6) > 1:
        for face1, face2 in itertools.combinations(face5_6, 2):
            intersectingEdges = getIntersectingEdgeOfTwoFaces(modelName, [face1], [face2])
            if intersectingEdges:
                intersectingCornerEdgesOnFace5_6.extend(intersectingEdges)
    
    face5_6Edges = getFaceEdges(modelName, face5_6)
    if not face5_6Round:
        simlablib.DeleteGroups(edgeGroup)
        simlablib.CreateGroup(modelName, 'Edge', face5_6Edges, edgeGroup)
        splitEdgeByAngle(modelName, face5_6Edges)
        face5_6Edges = simlab.getEntityFromGroup(edgeGroup)
        
        imprintedWEdgeVertexes = getEdgeVertexes(modelName, imprintedWEdge)
        edge6 = getFaceEdgeNotAssociatedWithRefEdge(modelName, face5_6Edges, imprintedWEdgeVertexes)
    else:
        edge6 = list(set((set(face5_6Edges) -set(imprintedWEdge))) -set(intersectingCornerEdgesOnFace5_6))

    
    # print('edge1:{}'.format(edge1))
    # print('edge6:{}'.format(edge6))

    newBeadFace = []
    simlablib.DeleteGroups('bodyFaces')
    simlablib.SelectAssociatedEntities(modelName, 'Body', [beadName], 'Face', 'bodyFaces')
    preBodyFaces = simlab.getEntityFromGroup('bodyFaces')
    
    if edge1 and edge6:
        alignUniformEdgeNode(modelName, edge1)
        alignUniformEdgeNode(modelName, edge6)
        if wBeadLen == 0.0:
            if not os.path.exists(LOG_DIR):
                os.makedirs(LOG_DIR)
            f_name = os.path.join(LOG_DIR,'faceArea.csv')
            if os.path.exists(f_name):
                os.remove(f_name)
            
            faceArea = getFaceArea(modelName, face1_2, f_name)

            simlablib.DeleteGroups(nodeGroup)
            vertexNode = getVertexNode(modelName, wEdgeVertexes[0], nodeGroup)
            p0 =  vertexNode[0]

            totalEdgeLength = getEdgeTotalLength(modelName, wEdge, p0)

            #print('faceArea:{}'.format(faceArea))
            #print('totalEdgeLength:{}'.format(totalEdgeLength))

            wFaceLength = faceArea/ totalEdgeLength

            #print('wFaceLength:{}'.format(wFaceLength))

            createFaceFromEdges(modelName, edge1, edge6, max(int(round(math.sqrt(wFaceLength*wFaceLength+pBeadLen*pBeadLen)/beadElemSize)),2))
        else:
            createFaceFromEdges(modelName, edge1, edge6, max(int(round(math.sqrt(wBeadLen*wBeadLen+pBeadLen*pBeadLen)/beadElemSize)),2))

        fillHoleGroup = 'Fill_Hole_Faces'
        simlablib.DeleteGroups(fillHoleGroup)
        fillFreeEdgesOfBody(modelName, beadName)
    
    
    if splitNodePtsOnFace12 and splitNodePtsOnFace56:
        simlablib.DeleteGroups('bodyFaces')
        simlablib.SelectAssociatedEntities(modelName, 'Body', [beadName], 'Face', 'bodyFaces')
        postBodyFaces = simlab.getEntityFromGroup('bodyFaces')
        newBeadFace = list(set(postBodyFaces) - set(preBodyFaces))
        
        n_g1, n_g2 = splitNodePtsOnFace12
        n_g1_a, n_g1_b = n_g1
        n_g2_a, n_g2_b = n_g2

        n_g3, n_g4 = splitNodePtsOnFace56
        n_g3_a, n_g3_b = n_g3
        n_g4_a, n_g4_b = n_g4

        planeA = []
        planeB = []
        if np.linalg.norm(np.array(n_g1_b) - np.array(n_g3_b)) < 1e-1:
            # print('#1')
            planeA = [n_g1_a, n_g1_b, n_g3_a]
            planeB = [n_g2_a, n_g2_b, n_g4_a]
        elif np.linalg.norm(np.array(n_g1_b) - np.array(n_g4_b)) < 1e-1:
            # print('#2')
            planeA = [n_g1_a, n_g1_b, n_g4_a]
            planeB = [n_g2_a, n_g2_b, n_g3_a]
        
        elif np.linalg.norm(np.array(n_g2_b) - np.array(n_g3_b)) < 1e-1:
            # print('#3')
            planeA = [n_g2_a, n_g2_b, n_g3_a]
            planeB = [n_g1_a, n_g1_b, n_g4_a]
        
        elif np.linalg.norm(np.array(n_g2_b) - np.array(n_g4_b)) < 1e-1:
            # print('#4')
            planeA = [n_g2_a, n_g2_b, n_g4_a]
            planeB = [n_g1_a, n_g1_b, n_g3_a]
        
        # print('planeA:{}'.format(planeA))
        # print('planeB:{}'.format(planeB))
        
        simlablib.DeleteGroups('newBeadFace')
        simlablib.CreateGroup(modelName, 'Face', newBeadFace, 'newBeadFace')
        splitFaceByAngle(modelName, newBeadFace, 45)
        
        breakFaceEdges = []
        if planeA and planeB:

            for thisPlane in [planeA, planeB]:
                refPt = thisPlane[0]
                
                newBeadFace = simlab.getEntityFromGroup('newBeadFace')

                refNodeId = getNodeOnCoordinate(modelName, newBeadFace, refPt, 0.1)
                if refNodeId is None:
                    continue
                # print('refPt:{}'.format(refPt))
                # print('refNodId:{}'.format(refNodeId))

                faceAssRefNodeId = None
                for thisFace in newBeadFace:
                    simlablib.DeleteGroups('faceNodes')
                    simlablib.SelectAssociatedEntities(modelName, 'Face', thisFace, 'Node', 'faceNodes')
                    faceNodes = list(simlab.getEntityFromGroup('faceNodes'))
                    if refNodeId in faceNodes:
                        faceAssRefNodeId = thisFace
                
                if faceAssRefNodeId is None:
                    continue

                # print('faceAssRefNodeId:{}'.format(faceAssRefNodeId))
                # print('plane:{}'.format(thisPlane))
                
                simlablib.DeleteGroups('Break_Face_Edges')
                fourPts = simlabutil.Convert3PointsOnPlaneTo4Points(thisPlane)
                cutFaceOnPlane(modelName, [faceAssRefNodeId], fourPts)

                edgeCut = list(simlab.getEntityFromGroup('Break_Face_Edges'))
                breakFaceEdges += edgeCut
        
        if breakFaceEdges:
            edgeRemesh(modelName, breakFaceEdges, beadElemSize)
            allNodeGroups = simlab.getGroupsWithSubString('NodeGroup', ['*'])
            simlablib.DeleteGroups(allNodeGroups)
            simlablib.DeleteAllOphanNodes()

    simlab.redisplayEntity('Model', modelName)


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

def edgeRemesh(modelName, edge, avgElemSize, aspectRatio=10):
    SurfaceLocalRemesh=''' <NewLocalReMesh UUID="83ab93df-8b5e-4a48-a209-07ed417d75bb">
    <tag Value="-1"/>
    <Name Value="NewLocalReMesh3"/>
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
    <MaxAnglePerElem Value="45 deg"/>
    <CurvatureMinElemSize Value="'''+ str(avgElemSize / 2) +'''"/>
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
        
def getEdgeAssociatedWithVertex(modelName, vertex, groupName):
    SelectVertexAssociatedEntities=''' <SelectVertexAssociatedEntities UUID="fc2ece8b-b6e8-4d37-8e27-39a13700fbad">
    <InputVertices Values="">
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Vertex>'''+ str(vertex).strip('()''[]') +'''</Vertex>
    </Entities>
    </InputVertices>
    <Option Value="Edges"/>
    <Groupname Value="'''+ groupName +'''"/>
    </SelectVertexAssociatedEntities>'''
    simlab.execute(SelectVertexAssociatedEntities)

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
    <MeshSize Value="1"/>
    <Radius Value=""/>
    <EquiValence Value="1"/>
    <Output/>
    </EdgeFromNode>'''
    simlab.execute(CreateEdgeFromNodes)

# def createArcEdge(modelName, startNode, endNode, byNode, meshSize):
#     CreateEdgeFromNodes=''' <EdgeFromNode gda="" UUID="449D18D7-E715-41ce-A640-4AEC18636570">
#     <Name Value="EdgeFromNode11"/>
#     <tag Value="-1"/>
#     <Mode Value="2"/>
#     <StartNode>
#     <Entities>
#     <Model>'''+ modelName +'''</Model>
#     <Node>'''+ str(startNode) +''',</Node>
#     </Entities>
#     </StartNode>
#     <EndNode>
#     <Entities>
#     <Model>'''+ modelName +'''</Model>
#     <Node>'''+ str(endNode) +'''</Node>
#     </Entities>
#     </EndNode>
#     <DefineAxis Value="0"/>
#     <Arc Value="1"/>
#     <ThirdNode>
#     <Entities>
#     <Model>'''+ modelName +'''</Model>
#     <Node>'''+ str(byNode) +'''</Node>
#     </Entities>
#     </ThirdNode>
#     <NoOfElemChk Value="0"/>
#     <NoOfElements Value="1"/>
#     <MeshChk Value="1"/>
#     <MeshSize Value="'''+ str(meshSize) +'''"/>
#     <Radius Value=""/>
#     <EquiValence Value="1"/>
#     <Output/>
#     </EdgeFromNode>'''
#     simlab.execute(CreateEdgeFromNodes)

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

def imprintEdgeOnFace(modelName, edges, face, remeshOn=0):
    ImprintEdgesonFaces=''' <ImprintEdgeOnFace pixmap="imprintedgeonface" UUID="26bb695d-621b-4ba9-996e-11d409dfe332">
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(face).strip('()''[]') +'''</Face>
    <Edge>'''+ str(edges).strip('()''[]') +'''</Edge>
    </Entities>
    </SupportEntities>
    <CloseGap Value="0"/>
    <UseDirection Value="0"/>
    <DirectionPoint Value="0,0,0"/>
    <LocalRemesh Value="'''+ str(remeshOn) +'''"/>
    </ImprintEdgeOnFace>'''
    simlab.execute(ImprintEdgesonFaces)

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

def getNodeOnCoordinate(modelName, face, coord, incrementBy):
    groupName = 'Show_Nodes'
    simlablib.DeleteGroups(groupName)
    nodeFound = False
    rad = 0.11
    counter = 0
    while not nodeFound:
        if counter == 10:
            return None
        checkNodeInSphere(modelName, face, rad, coord)
        nodeInSphere = simlab.getEntityFromGroup(groupName)
        if nodeInSphere:
            break
        rad += incrementBy
        counter += 1
    
    return nodeInSphere[0]

def checkNodeInSphere(modelName, face, rad, ctp, tol = 0.01):
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
    <On Value="0"/>
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

def getEdgeTotalLength(modelName, edge, vertexNode):
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
        totalDist+= dist
        # print('edgeNodes_copy:{}'.format(edgeNodes_copy))
        # print('neighborNode:{}'.format(neighborNode))
        nodesOrderedByDistFromVertexNode.append(neighborNode)
        p0 = neighborNode
        edgeNodes_copy.remove(neighborNode)
    
    return totalDist


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

    while len(edgeNodes_copy) != 0:
        neighborNode = getClosestNodeFromANode(nodePtDict, edgeNodes_copy, p0)        
        # print('edgeNodes_copy:{}'.format(edgeNodes_copy))
        # print('neighborNode:{}'.format(neighborNode))
        nodesOrderedByDistFromVertexNode.append(neighborNode)
        p0 = neighborNode
        edgeNodes_copy.remove(neighborNode)
    
    return nodesOrderedByDistFromVertexNode

def alignUniformEdgeNode(modelName, edge):
    AlignRadial=''' <AlignRadial UUID="0FB98645-1050-4d6e-ABE4-B39FFCD70410" CheckBox="ON">
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

def imprintCircle(modelName, face, centerPt, rad, numNodes):
    x, y, z = centerPt
    ImprintCircle=''' <ImprintCircle UUID="b97b1d66-a483-4201-9ae1-05f95fad3cde">
    <tag Value="-1"/>
    <RedoFlag Value=""/>
    <Output/>
    <Imprint>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(face).strip('()''[]') +'''</Face>
    </Entities>
    </SupportEntities>
    <Center_X Value="'''+ str(x) +'''"/>
    <Center_Y Value="'''+ str(y) +'''"/>
    <Center_Z Value="'''+ str(z) +'''"/>
    <Radius Value="'''+ str(rad) +'''"/>
    <Nodes Value="'''+ str(numNodes) +'''"/>
    </Imprint>
    </ImprintCircle>'''
    simlab.execute(ImprintCircle)

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

def createEdgeByOffset(modelName, face, edge, offsetDistance, numLayers):
    CreateEdgeByEdgeOffset=''' <EdgeOffset UUID="6d4a36ce-1c18-456d-a3cb-910cb85efdb5" gda="">
    <Name Value="EdgeOffset1"/>
    <Faces>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(face).strip('()''[]') +'''</Face>
    </Entities>
    </Faces>
    <Edges>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edge).strip('()''[]') +'''</Edge>
    </Entities>
    </Edges>
    <GuideEdge Value="" ModelIds="" EntityTypes=""/>
    <OffsetDistance Value="'''+ str(offsetDistance) +'''"/>
    <OffsetOption Value="Selected Edges"/>
    <Direction Value="0"/>
    <MoveGuideEdge Value="0"/>
    <ExistingMesh Value="0"/>
    <LayerOption Value="Tri"/>
    <NoOfLayers Value="'''+ str(numLayers) +'''"/>
    <EdgeAtVertices Value="1"/>
    <LocalRemesh Value="0"/>
    <MeshSize Value=""/>
    <FloatingEdge_DirectionPt1 Value="0"/>
    <FloatingEdge_DirectionPt2 Value="0"/>
    <Output/>
    </EdgeOffset>'''
    simlab.execute(CreateEdgeByEdgeOffset)


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

def getDistanceBetweenFaceAndNode(modelName, face, node):
    DistanceBetweenTwoEntities=''' <DistanceBetweenTwoEntities UUID="53537c0a-6606-4b36-9a95-c05be32f39fc">
    <SupportEntity1>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(face).strip('()''[]') +''',</Face>
    </Entities>
    </SupportEntity1>
    <SupportEntity2>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Node>'''+ str(node).strip('()''[]') +''',</Node>
    </Entities>
    </SupportEntity2>
    </DistanceBetweenTwoEntities>'''
    
    dist,_,_,_ = simlab.measure(DistanceBetweenTwoEntities)

    if dist:
        return dist[0]

    return None

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

def getClosestNodeFromANode(nodePtDict, nodeIdList, fromTheNode):
    # make sure the nodeId list have more than 2 elements
    distDict = dict()
    p0 = nodePtDict[fromTheNode]

    for thisNode in nodeIdList:
        thisNodePt = nodePtDict[thisNode]
        this_d = np.linalg.norm(thisNodePt - p0)
        distDict[thisNode] = this_d
    
    closestNodeId = min(distDict, key= distDict.get)

    return closestNodeId

def getFaceEdges(modelName, face):
    edgeGroup='edgeGroup'
    simlablib.DeleteGroups(edgeGroup)
    simlablib.SelectAssociatedEntities(modelName, 'Face', face, 'Edge', edgeGroup)
    faceEdges = simlab.getEntityFromGroup(edgeGroup)
    return faceEdges

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

def checkLoopEdge(modelName, edge):
    vertexGroup = 'vertexGroup'
    simlablib.DeleteGroups(vertexGroup)

    simlablib.SelectAssociatedEntities(modelName, 'Edge', edge, 'Vertex', vertexGroup)
    edgesVertex = simlab.getEntityFromGroup(vertexGroup)

    return len(edgesVertex) == len(edge)

def getFaceEdgeNotAssociatedWithRefEdge(modelName, faceEdges, refEdgeVertexes):
    edgeGroup = 'edgeGroup'
    simlablib.DeleteGroups(edgeGroup)
    SelectVertexAssociatedEntities=''' <SelectVertexAssociatedEntities UUID="fc2ece8b-b6e8-4d37-8e27-39a13700fbad">
    <InputVertices Values="">
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Vertex>'''+ str(refEdgeVertexes).strip('()''[]') +'''</Vertex>
    </Entities>
    </InputVertices>
    <Option Value="Edges"/>
    <Groupname Value="'''+ edgeGroup +'''"/>
    </SelectVertexAssociatedEntities>'''
    simlab.execute(SelectVertexAssociatedEntities)

    edgesAssociatedWithRefVertexes = simlab.getEntityFromGroup(edgeGroup)

    return list(set(faceEdges)-set(edgesAssociatedWithRefVertexes))

def getStartAndEndEdgeVertexes(modelName, edges, edgeVertexes):
    edgeGroup = 'edgeGroup'
    endVertexes = []

    for thisVertex in edgeVertexes:
        simlablib.DeleteGroups(edgeGroup)
        SelectVertexAssociatedEntities=''' <SelectVertexAssociatedEntities UUID="fc2ece8b-b6e8-4d37-8e27-39a13700fbad">
        <InputVertices Values="">
        <Entities>
        <Model>'''+ modelName +'''</Model>
        <Vertex>'''+ str(thisVertex) +'''</Vertex>
        </Entities>
        </InputVertices>
        <Option Value="Edges"/>
        <Groupname Value="'''+ edgeGroup +'''"/>
        </SelectVertexAssociatedEntities>'''
        simlab.execute(SelectVertexAssociatedEntities)
        edgesAssociatedWithVertex = simlab.getEntityFromGroup(edgeGroup)

        intersectingEdges = list(set(edges).intersection(set(edgesAssociatedWithVertex)))
        if len(intersectingEdges) == 1:
            endVertexes.append(thisVertex)
    
    return endVertexes

def getEdgeVertexes(modelName, edge):
    vertexGroup = 'vertexGroup'
    simlablib.DeleteGroups(vertexGroup)
    simlablib.SelectAssociatedEntities(modelName, 'Edge', edge, 'Vertex', vertexGroup)
    edgeVertexes = simlab.getEntityFromGroup(vertexGroup)
    return edgeVertexes

def getConnectedEdgeVertexPair(modelName, vertexes1, vertexes2):
    vertexPair = [] 
    edgeGroup = 'edgeGroup'
    vertexGroup = 'vertexGroup'
    for thisVertex in vertexes1:
        simlablib.DeleteGroups(edgeGroup)
        getEdgeAssociatedWithVertex(modelName, [thisVertex], edgeGroup)
        edgeV = simlab.getEntityFromGroup(edgeGroup)
        for thisEdge in edgeV:
            simlablib.DeleteGroups(vertexGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Edge', [thisEdge], 'Vertex', vertexGroup)
            linkedVertexes = simlab.getEntityFromGroup(vertexGroup)
            intersectingVertex = list(set(linkedVertexes).intersection(set(vertexes2)))
            if intersectingVertex:
                vertexPair.append([thisVertex,intersectingVertex[0]])
                break
    
    return vertexPair

def getFaceArea(modelName, face, fName):
    CalculateArea=''' <CalculateArea UUID="e77c854e-2658-4034-a3a4-1b46b72e4770">
    <InputEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(face).strip('()''[]') +''',</Face>
    </Entities>
    </InputEntities>
    <FileName Value="'''+fName+'''"/>
    </CalculateArea>'''
    simlab.execute(CalculateArea)

    area = 0
    if not os.path.exists(fName):
        return area
    
    with open(fName) as f_read:
        for line in f_read:
            line = line.rstrip('\n')
            if not line.rstrip():
                continue
            if line.startswith('Total Area'):
                spLine = line.split(',')
                area = spLine[-1]
                try:
                    area = float(area)
                except:
                    area = 0
    
    return area

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

def getIntersectingEdgeOfTwoFaces(modelName, face1, face2):
    edgeGroup = 'edgeGroup'
    simlablib.DeleteGroups(edgeGroup)
    simlablib.SelectAssociatedEntities(modelName, 'Face', face1, 'Edge', edgeGroup)

    faceEdges1 = simlab.getEntityFromGroup(edgeGroup)

    simlablib.DeleteGroups(edgeGroup)
    simlablib.SelectAssociatedEntities(modelName, 'Face', face2, 'Edge', edgeGroup)

    faceEdges2 = simlab.getEntityFromGroup(edgeGroup)

    return list(set(faceEdges1).intersection(set(faceEdges2)))

def getMinDistanceBetweenNodeAndEdge(modelName, edges, refNode):
    edgeNodes = getEdgeNodes(modelName, edges)
    refNodePt = np.array(simlab.getNodePositionFromNodeID(modelName, refNode))

    minDistance = 1e6
    for thisNode in edgeNodes:
        nodePt = np.array(simlab.getNodePositionFromNodeID(modelName, thisNode))

        dist = np.linalg.norm(refNodePt - nodePt)

        if dist < minDistance:
            minDistance = dist
    
    return minDistance

def getEdgeNodes(modelName, edges):
    nodeGroup = 'nodeGroup'
    simlablib.DeleteGroups(nodeGroup)
    simlablib.SelectAssociatedEntities(modelName, 'Edge', edges, 'Node', nodeGroup)
    edgeNodes = simlab.getEntityFromGroup(nodeGroup)

    return edgeNodes

def getIntersectingNodeOfTwoEdges(modelName, edge1, edge2):
    nodeGroup = 'nodeGroup'
    simlablib.DeleteGroups(nodeGroup)
    simlablib.SelectAssociatedEntities(modelName, 'Edge', edge1, 'Node', nodeGroup)
    edgeNode1 = simlab.getEntityFromGroup(nodeGroup)

    simlablib.DeleteGroups(nodeGroup)
    simlablib.SelectAssociatedEntities(modelName, 'Edge', edge2, 'Node', nodeGroup)
    edgeNode2 = simlab.getEntityFromGroup(nodeGroup)
    
    return list(set(edgeNode1).intersection(set(edgeNode2)))

def getClosestEdgeNodeFrom(modelName, refEdge, fromNode):
    nodeGroup = 'nodeGroup'
    simlablib.DeleteGroups(nodeGroup)
    simlablib.SelectAssociatedEntities(modelName, 'Edge', refEdge, 'Node', nodeGroup)
    edgeNodes = simlab.getEntityFromGroup(nodeGroup)
    fromPt = np.array(simlab.getNodePositionFromNodeID(modelName, fromNode))

    minDistance = 1e6
    minDistanceNode = 0
    for thisNode in edgeNodes:
        if thisNode == fromNode:
            continue
        toPt = np.array(simlab.getNodePositionFromNodeID(modelName, thisNode))
        dist = np.linalg.norm(fromPt-toPt)
        if dist < minDistance:
            minDistance = dist
            minDistanceNode = thisNode
    
    return minDistanceNode

def imprintEdgesOnEdges(modelName, edges1, edge2, tol= 1.0e-6):
    ImprintEdgesonEdges=''' <ImprintEdgeOnEdge pixmap="imprintedgeonedge" UUID="08d266da-5c20-4892-935f-058c7e9f6739">
    <tag Value="-1"/>
    <InputEdges>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edges1).strip('()''[]') +'''</Edge>
    </Entities>
    </InputEdges>
    <TargetEdges>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edge2).strip('()''[]') +'''</Edge>
    </Entities>
    </TargetEdges>
    <Tolerance Value="'''+ str(tol) +'''"/>
    </ImprintEdgeOnEdge>'''
    simlab.execute(ImprintEdgesonEdges)

def joinOverlappingFaces(modelName, facesToJoin, tol):
    Join=''' <Join UUID="93BDAC5E-9059-42b6-BDC3-EFA346D3DDEC" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value=""/>
    <Pick Value="Join"/>
    <JoinEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(facesToJoin).strip('()''[]') +'''</Face>
    </Entities>
    </JoinEntities>
    <AlignEntities ModelIds="" Value="" EntityTypes=""/>
    <PreserveEntities ModelIds="" Value="" EntityTypes=""/>
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

def splitEdgeByNodes(modelName, edge, nodes):
    SplitEdge=''' <SplitEdge gda="" UUID="7ECA56CA-94D5-4a21-A88D-59707F8568DC">
    <Name Value="SplitEdge3"/>
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
    <Angle Value="0.0" Check="0"/>
    <TopoEdge Value="" Check="0"/>
    <Equivalence Value=""/>
    <MidPoint Value="" Check="0"/>
    <Output/>
    </SplitEdge>'''
    simlab.execute(SplitEdge)

def getNodeOnPt(modelName, face, ctPt, rad = 0.2):
    groupName = 'Show_Nodes'
    simlablib.DeleteGroups(groupName)

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
    <On Value="0"/>
    <Above Value="0"/>
    <Below Value="1"/>
    <Tolerance Value="0.037501"/>
    <MaximumCount Value="5000"/>
    <ShowSurfaceNodes Value="1"/>
    <CreateGroup Value="1"/>
    <RegionObject>
    <Sphere>
    <Center Value="'''+ str(ctPt).strip('()''[]') +'''"/>
    <Radius Value="'''+ str(rad) +'''"/>
    </Sphere>
    </RegionObject>
    </NodesByRegion>'''
    simlab.execute(NodesByRegion)

    nodeId = simlab.getEntityFromGroup(groupName)
    
    if nodeId:
        return nodeId[0]
    
    return None

def cutFaceOnPlane(modelName, face, pts):
    pt1, pt2, pt3, pt4 = pts
    BreakBody=''' <Break UUID="ccdd6ef0-aaff-4594-850d-886c733cbc2f">
    <tag Value="-1"/>
    <Name Value="Break1"/>
    <Type Value="1"/>
    <PlaneBreak>
    <CreateInternalFace Value="0"/>
    <BreakBodies Value="0"/>
    <CreateSheetBodyFromCutSection Value="0"/>
    <PlanePoints Value=""/>
    <Entity>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(face).strip('()''[]') +'''</Face>
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

def splitFaceByAngle(modelName, face, angle):
    SplitFace=''' <FEASplitFace UUID="F67108F4-D1EB-4fc9-9333-8B181405C673">
    <tag Value="-1"/>
    <Name Value="FEASplitFace1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(face).strip('()''[]') +'''</Face>
    </Entities>
    </SupportEntities>
    <FeatureAngle Value="'''+ str(angle) +'''"/>
    <Option Value="0"/>
    <CreateFloatingEdges Value="0"/>
    </FEASplitFace>'''
    simlab.execute(SplitFace)
