# coding: shift-jis
from multiprocessing.sharedctypes import Value
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter.ttk import Separator
import os, sys, importlib
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

class GrooveWeldingDialog(basedialog.BaseDialog):
    def __init__(self, master, parent, config, backup):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('開先溶接')
        self.master.resizable(width=False, height=False)
        self.master.attributes('-topmost', True)
        self.master.protocol('WM_DELETE_WINDOW', self.CloseDialog)
        self.config = config
        self.backup = backup

        self.referenceFace = 'GrooveWeldingRefFace'
        self.slopeFace = 'GrooveWeldingSlopeFace'
        self.projectionFace = 'GrooveProjectionFace'
        self.weldingEdge = 'GrooveWeldingEdge'
        self.connectBody = 'GrooveWeldingConnectBody'

        self.CreateWidgets()

        edgeGroups = simlab.getGroupsWithSubString('EdgeGroup', ['{}*'.format(self.weldingEdge)])
        faceGroups = simlab.getGroupsWithSubString('FaceGroup', ['{}*'.format(self.slopeFace)])
        simlablib.DeleteGroups(edgeGroups)
        simlablib.DeleteGroups(faceGroups)
        simlablib.DeleteGroups(self.referenceFace)
        simlablib.DeleteGroups(self.projectionFace)

        self.UpdateButtonFG()

        simlabutil.ClearSelection()       

        simlab.setSelectionFilter('Face')
    
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        tk.Label(self.frmTop, text='エッジ、面を選択してビード情報を入力してください。\n共有節点オプション：「別ボディ」').pack(side=tk.TOP, anchor=tk.CENTER)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmFig = tk.Frame(self.frmTop)        
        self.frmFig.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        self.frmGrooveWeld = tk.Frame(self.frmFig, width=400)
        self.frmGrooveWeld.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconFilletWeld = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'grooveWelding.png')), master=self.frmGrooveWeld)
        tk.Label(self.frmGrooveWeld, image=self.iconFilletWeld).pack(side=tk.LEFT, anchor=tk.W)

        self.iconClearSelection = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'delete-24.png')), master=self.frmGrooveWeld)
        self.bntClearSelection = tk.Button(self.frmGrooveWeld, image=self.iconClearSelection, command=self.ClearSelection)
        self.bntClearSelection.place(x=5, y=280)

        self.btnRefFace = tk.Button(self.frmGrooveWeld, text='基準面', command=self.SelectRefFace, width=10)
        self.btnRefFace.place(x=25, y=40)

        self.btnSlopeFace = tk.Button(self.frmGrooveWeld, text='斜面', command=self.SelectSlopeFace, width=10)
        self.btnSlopeFace.place(x=130, y=20)

        self.btnProjectionFace = tk.Button(self.frmGrooveWeld, text='対面', command=self.SelectProjectionFace, width=10)
        self.btnProjectionFace.place(x=250, y=40)

        self.btnWeldingEdge = tk.Button(self.frmGrooveWeld, text='エッジ', command=self.SelectWeldingEdge, width=10)
        self.btnWeldingEdge.place(x=95, y=160)

        self.btnConnectBody = tk.Button(self.frmGrooveWeld, text='別ボディ', command= self.SelectConnectBody, width=10)
        self.btnConnectBody.place(x=95, y=225)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmBeadInfo = tk.Frame(self.frmTop)
        self.frmBeadInfo.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)

        tk.Label(self.frmBeadInfo, text='ビード脚長情報 :').pack(side=tk.TOP, anchor=tk.NW)
        self.frmBeadFig = tk.Frame(self.frmBeadInfo)
        self.frmBeadFig.pack(side=tk.LEFT, anchor=tk.NW)
        self.iconBead = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'grooveBeadLength.png')), master=self.frmBeadFig)
        tk.Label(self.frmBeadFig, image=self.iconBead).pack(side=tk.LEFT, anchor=tk.W)

        self.frmBeadSpec = tk.Frame(self.frmBeadInfo)
        self.frmBeadSpec.pack(side=tk.LEFT, anchor=tk.NW)
        self.frmBeadSpec1 = tk.Frame(self.frmBeadSpec)
        self.frmBeadSpec1.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmBeadSpec1, text='d_x : 対面の垂直方向への距離').pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmBeadSpec1, text='d_y : 斜面が対面に投影点からの距離').pack(side=tk.TOP, anchor=tk.NW)

        tk.Frame(self.frmBeadSpec, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmBeadSpec2 = tk.Frame(self.frmBeadSpec)
        self.frmBeadSpec2.pack(side=tk.TOP, anchor=tk.NW)

        tk.Label(self.frmBeadSpec2, text='d_x : ').grid(row=0, column=0)
        self.entFace1Thickness = tk.Entry(self.frmBeadSpec2, width=7)
        self.entFace1Thickness.grid(row=0, column=1)
        bead_thickness = self.config.Get('Bead_Thickness')
        self.entFace1Thickness.insert(tk.END, bead_thickness)

        tk.Label(self.frmBeadSpec2, text='d_y : ').grid(row=1, column=0)
        self.entFace2Thickness = tk.Entry(self.frmBeadSpec2, width=7)
        self.entFace2Thickness.grid(row=1, column=1)
        self.entFace2Thickness.insert(tk.END, 0)

        Separator(self.frmBeadSpec2, orient='vertical').grid(row=0, column=2, rowspan= 2, sticky='nwse',padx=5)

        self.varSlopeFace = tk.BooleanVar()
        self.chkAllSlopeFace = tk.Checkbutton(self.frmBeadSpec2, text='斜面全体', variable=self.varSlopeFace, command=self.AllSlopeFaceCallback)
        self.chkAllSlopeFace.grid(row=0, column=3)

        tk.Label(self.frmBeadSpec2, text='ビード要素長: ').grid(row=1, column=3)
        self.entBeadElemSize = tk.Entry(self.frmBeadSpec2, width=7)
        self.entBeadElemSize.grid(row=1, column=4)
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
    
    def AllSlopeFaceCallback(self):
        isChecked = self.varSlopeFace.get()
        if isChecked:
            self.entFace1Thickness.config(state='disabled')
        else:
            self.entFace1Thickness.config(state='normal')
    
    def SelectRefFace(self):
        refFaces = list(simlab.getEntityFromGroup(self.referenceFace))
        face = list(simlab.getSelectedEntities('FACE'))
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        refFaces.extend(face)
            
        simlablib.DeleteGroups(self.referenceFace)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', refFaces, self.referenceFace)

        self.UpdateButtonFG()

    def SelectSlopeFace(self):
        slopeFaces = list(simlab.getEntityFromGroup(self.slopeFace))
        face = list(simlab.getSelectedEntities('FACE'))
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        slopeFaces.extend(face)
        
        simlablib.DeleteGroups(self.slopeFace)
        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', slopeFaces, self.slopeFace)

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
        edges = list(simlab.getSelectedEntities('EDGE'))
        if len(edges) == 0:
            messagebox.showinfo('情報','エッジを選択した後、ボタンを押してください。')
            return
        
        wEdges.extend(edges)
        simlablib.DeleteGroups(self.weldingEdge)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Edge', wEdges, self.weldingEdge)

        self.UpdateButtonFG()
    
    def SelectConnectBody(self):
        body = simlab.getSelectedBodies()
        if len(body) == 0:
            messagebox.showinfo('情報','ボディを選択した後、ボタンを押してください。')
            return
        
        simlablib.DeleteGroups(self.connectBody)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Body', body, self.connectBody)

        self.UpdateButtonFG()

    def UpdateButtonFG(self):
        groups = [self.referenceFace, self.slopeFace, self.projectionFace, self.weldingEdge, self.connectBody]
        widgets = [self.btnRefFace, self.btnSlopeFace, self.btnProjectionFace, self.btnWeldingEdge, self.btnConnectBody]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)

    def Undo(self):
        self.backup.Load()
        self.UpdateButtonFG()

        modelName = simlab.getModelName('CAD')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')
    
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
        
        d_x = 0.0
        face1ThicknessWidgetState = self.entFace1Thickness.cget(key='state')
        if face1ThicknessWidgetState == 'normal':
            d_x = self.entFace1Thickness.get()
            try:
                d_x = float(d_x)
            except ValueError:
                messagebox.showinfo('情報','d_xの値で数字だけを入力してください。')
                return
            else:
                if d_x <= 0.0:
                    messagebox.showinfo('情報','d_xの値で０より大きい数字を入力してください。')
                    return

        d_y = self.entFace2Thickness.get()
        try:
            d_y = float(d_y)
        except ValueError:
            messagebox.showinfo('情報','d_yの値で数字だけを入力してください。')
            return
        else:
            if d_y < 0.0:
                messagebox.showinfo('情報','d_yの値で正の数または０を入力してください。')
                return
        
        allModelNames = simlab.getAllRootModelNames('FEM')
        if len(allModelNames) > 1:
            messagebox.showinfo('情報','モデル名が複数あります。マージして一個にしてください。')
            return
        elif len(allModelNames) == 0:
            messagebox.showinfo('情報','FEモデルを作成してください。')
            return

        modelName = simlab.getModelName('FEM')

        refFace = simlab.getEntityFromGroup(self.referenceFace)
        sFace = simlab.getEntityFromGroup(self.slopeFace)
        pFace = simlab.getEntityFromGroup(self.projectionFace)
        wEdge = simlab.getEntityFromGroup(self.weldingEdge)
        connectBody = simlab.getBodiesFromGroup(self.connectBody)
        if not refFace:
            messagebox.showinfo('情報','基準面を登録してください。')
            return
        if not sFace:
            messagebox.showinfo('情報','斜面を登録してください。')
            return
        if not pFace:
            messagebox.showinfo('情報','対面を登録してください。')
            return
        if not wEdge:
            messagebox.showinfo('情報','エッジを登録してください。')
            return
        
        vertexGroup = 'vertexGroup'
        # check if wEdge is from slope face
        edgeGroup = 'edgeGroup'
        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', sFace, 'Edge', edgeGroup)
        slopeFaceEdges = list(simlab.getEntityFromGroup(edgeGroup))
        if not all(thisEdge in slopeFaceEdges for thisEdge in wEdge):
            messagebox.showinfo('情報','斜面からエッジを選んでください。')
            return

        try:
            aspectRatio = float(self.config.Get('Aspect_Ratio'))
        except ValueError:
            aspectRatio = 10

        self.backup.Save('GrooveWelding')

        wEdgeGroups = simlab.createGroupsOfConnectedEntities(self.weldingEdge)
        sFaceGroups = simlab.createGroupsOfConnectedEntities(self.slopeFace)

        beadfaces = []

        for thisGroup in wEdgeGroups:
            wEdges = simlab.getEntityFromGroup(thisGroup)
            sFaces = searchFacesFromGroupsWithEdge(modelName, sFaceGroups, wEdges)
            if not sFaces:
                continue
            sFaceEdges = getFaceEdges(modelName, sFaces)
            pFaces = simlab.getEntityFromGroup(self.projectionFace)
            refEdges, refFaces = getIntersectingRefEdgeAndFace(modelName, sFaceEdges, refFace)
            if refEdges and refFaces:
                beadName = getUniqueBeadName(modelName)
                startWelding(modelName, beadName, wEdges, sFaces, refEdges, refFaces, pFaces, beadElemSize, d_x, d_y, connectBody, aspectRatio=aspectRatio)

        self.ClearSelection()
    
    def ClearSelection(self):
        edgeGroups = simlab.getGroupsWithSubString('EdgeGroup', ['{}*'.format(self.weldingEdge)])
        faceGroups = simlab.getGroupsWithSubString('FaceGroup', ['{}*'.format(self.slopeFace)])
        simlablib.DeleteGroups(edgeGroups)
        simlablib.DeleteGroups(faceGroups)
        simlablib.DeleteGroups(self.referenceFace)
        simlablib.DeleteGroups(self.projectionFace)
        self.UpdateButtonFG()


    def CloseDialog(self):
        edgeGroups = simlab.getGroupsWithSubString('EdgeGroup', ['{}*'.format(self.weldingEdge)])
        faceGroups = simlab.getGroupsWithSubString('FaceGroup', ['{}*'.format(self.slopeFace)])
        simlablib.DeleteGroups(edgeGroups)
        simlablib.DeleteGroups(faceGroups)
        simlablib.DeleteGroups(self.referenceFace)
        simlablib.DeleteGroups(self.projectionFace)
        super().CloseDialog()

def startWelding(modelName, beadName, wEdges, sFaces, refEdges, refFaces, pFaces, beadElemSize, d_x, d_y, connectBody, aspectRatio = 10):
    #print(modelName, beadName, wEdges, sFaces, refEdges, refFaces, pFaces, beadElemSize, d_x, d_y, connectBody)
    
    sFaceGroup = 'sFacegroup'
    refFaceGroup = 'refFaceGroup'
    simlablib.DeleteGroups(sFaceGroup)
    simlablib.CreateGroup(modelName, 'Face', sFaces, sFaceGroup)
    simlablib.DeleteGroups(refFaceGroup)
    simlablib.CreateGroup(modelName, 'Face', refFaces, refFaceGroup)

    tempPFaceGroup = 'tempPFace'
    simlablib.DeleteGroups(tempPFaceGroup)
    simlablib.CreateGroup(modelName, 'Face', pFaces, tempPFaceGroup)

    faceGroup = 'faceGroup'
    edgeGroup = 'edgeGroup'
    nodeGroup = 'nodeGroup'

    bodiesToMerge = []

    beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
    closeGapBetwenEdgeAndFace(modelName, wEdges, pFaces)
    afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
    newBody = list(set(afterBodies) - set(beforeBodies))

    if newBody:
        simlablib.DeleteGroups(faceGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Body', newBody, 'Face', faceGroup)
        bodyFaces = simlab.getEntityFromGroup(faceGroup)
        wEdges = getIntersectingEdgeOfTwoFaces(modelName, sFaces, bodyFaces)
        imprintedWEdge = getIntersectingEdgeOfTwoFaces(modelName, bodyFaces, pFaces)
        for thisBody in newBody:
            bodiesToMerge.append(thisBody)
    else:
        sharedWEdge = getIntersectingEdgeOfTwoFaces(modelName, sFaces, pFaces)
        wEdges = sharedWEdge
        imprintedWEdge = sharedWEdge
    
    # print('wEdges:{}'.format(wEdges))
    # print('imprintedWEdge:{}'.format(imprintedWEdge))

    pFaces = list(simlab.getEntityFromGroup(tempPFaceGroup))
    pFacesAssImprintedWEdge = getAnyFacesHavingTheEdge(modelName, pFaces, imprintedWEdge)
    simlablib.DeleteGroups(tempPFaceGroup)
    simlablib.CreateGroup(modelName, 'Face', pFacesAssImprintedWEdge, tempPFaceGroup)

    # slope faces more than 1 are merged
    if len(sFaces) > 1:
        simlablib.MergeFaces(modelName, sFaces)
        sFaces = list(simlab.getEntityFromGroup(sFaceGroup))
  
    refFaces = simlab.getEntityFromGroup(refFaceGroup)
    refEdges = getIntersectingEdgeOfTwoFaces(modelName, refFaces, sFaces)

    imprintedEdgesOnPFace = []
    imprintEdgeGroup = 'Imprint_EdgeOn_Face'
    simlablib.DeleteGroups(imprintEdgeGroup)
    
    sFaceEdges = getFaceEdges(modelName, sFaces)
    edgesToImprint1 = list(set(sFaceEdges)-set(refEdges + imprintedWEdge))
    simlablib.UpdateModel()
    #print('edgesToImprint1:{}'.format(edgesToImprint1))

    imprintEdgeOnFace(modelName, edgesToImprint1, pFaces)
    imprintedEdges1OnPFace = list(simlab.getEntityFromGroup(imprintEdgeGroup))
    if not imprintedEdges1OnPFace:
        print('Fail to imprint edges1 on pFace')
        return
    
    #print('imprintedEdges1OnPFace:{}'.format(imprintedEdges1OnPFace))

    imprintedEdgesOnPFace.extend(imprintedEdges1OnPFace)
    simlablib.DeleteGroups(edgeGroup)
    simlablib.CreateGroup(modelName, 'Edge', imprintedEdgesOnPFace, edgeGroup)
    splitEdgeByAngle(modelName, imprintedEdgesOnPFace)
    imprintedEdgesOnPFace = list(simlab.getEntityFromGroup(edgeGroup))

    pFaces = list(simlab.getEntityFromGroup(tempPFaceGroup))
    # print('pFaces:{}'.format(pFaces))
    # print('refEdges:{}'.format(refEdges))

    simlablib.DeleteGroups(imprintEdgeGroup)
    # simlablib.UpdateModel()
    imprintEdgeOnFace(modelName, refEdges, pFaces)
    imprintedRefEdge = list(simlab.getEntityFromGroup(imprintEdgeGroup))
    if not imprintedRefEdge:
        print('Fail to imprint refEdge on pFace')
        return
    # print('imprintedRefEdge:{}'.format(imprintedRefEdge))

    imprintedRefEdgeNodes = getEdgeNodes(modelName, imprintedRefEdge)
    limitDistTop = getMinDistanceBetweenNodeAndEdge(modelName, refEdges, imprintedRefEdgeNodes[0])
    #  getDistanceBetweenTwoEdges(modelName, imprintedRefEdge[0], refEdges[0])
    #print('limitDistTop:{}'.format(limitDistTop))

    imprintedEdgesOnPFace.extend(imprintedRefEdge)
    pFaces = list(simlab.getEntityFromGroup(tempPFaceGroup))
    # print('pFaces:{}'.format(pFaces))

    imprintedEdgesOnPFace = imprintedEdgesOnPFace+imprintedWEdge
    # print('imprintedEdgesOnPFace:{}'.format(imprintedEdgesOnPFace))

    faceEdgeDict = dict()
    for thisFace in pFaces:
        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', [thisFace], 'Edge', edgeGroup)
        faceEdges = simlab.getEntityFromGroup(edgeGroup)
        leftOverEdges = list(set(faceEdges) - set(imprintedEdgesOnPFace))
        faceEdgeDict[thisFace] = len(leftOverEdges)

    # print('faceEdgeDict:{}'.format(faceEdgeDict))

    # imprintedSFaceOnPFace = min(faceEdgeDict, key=faceEdgeDict.get)
    # print('imprintedSFaceOnPFace:{}'.format(imprintedSFaceOnPFace))
    sortedEdges = [thisTup[0] for thisTup in sorted(faceEdgeDict.items(), key=lambda x: x[1])]

    imprintedSFaceOnPFace = sortedEdges[:len(wEdges)]
    # print('imprintedEdgesOnPFace:{}'.format(imprintedEdgesOnPFace))

    if not imprintedSFaceOnPFace:
        print('Fail to create a face on pFace')
        return

    if d_y == 0.0:
        pFace = imprintedSFaceOnPFace
        
        edgesTopOnPFace = imprintedRefEdge

        mcName = 'preserveEdgeMC'
        simlablib.DeleteMeshControl(mcName)
        preserveFaceEdgeMC(mcName, modelName, pFace)

    if d_y > 0:
        tempPFaces = simlab.getEntityFromGroup(tempPFaceGroup)

        outsidePFace = list(set(tempPFaces) - set(imprintedSFaceOnPFace))

        simlablib.DeleteGroups(tempPFaceGroup)
        simlablib.CreateGroup(modelName, 'Face', outsidePFace, tempPFaceGroup)

        outsideEdges_before = getFaceEdges(modelName, outsidePFace)
        
        # alignUniformEdgeNode(modelName, imprintedRefEdge)
        createEdgeByOffset(modelName, outsidePFace, imprintedRefEdge, d_y, 1)

        outsidePFace = simlab.getEntityFromGroup(tempPFaceGroup)
        outsideEdges_after = getFaceEdges(modelName, outsidePFace)

        # print('outsideEdges_before:{}'.format(outsideEdges_before))
        # print('outsideEdges_after:{}'.format(outsideEdges_after))
        if set(outsideEdges_before) == set(outsideEdges_after):
            pFace = imprintedSFaceOnPFace
            edgesTopOnPFace = imprintedRefEdge
        else:
            extendedFace = getFaceHavingAnyTheEdge(modelName, outsidePFace, imprintedRefEdge)
            #print('extendedFace:{}'.format(extendedFace))

            imprintedRefEdgeVertexes = getEdgeVertexes(modelName, imprintedRefEdge)
            faceEdges = getFaceEdges(modelName, extendedFace)
            edgesTopOnPFace = getFaceEdgeNotAssociatedWithRefEdge(modelName, faceEdges, imprintedRefEdgeVertexes)
            #print('edgesTopOnPFace:{}'.format(edgesTopOnPFace))
            pFace = imprintedSFaceOnPFace + extendedFace

    # print('edgesTopOnPFace:{}'.format(edgesTopOnPFace))
    # print('pFace:{}'.format(pFace))

    beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
    createBodyFromFaces(modelName, pFace)
    afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
    newPBody = list(set(afterBodies) - set(beforeBodies))
    for thisBody in newPBody:
        bodiesToMerge.append(thisBody)
    
    mcName = 'preserveEdgeMC'
    simlablib.DeleteMeshControl(mcName)
    preserveFaceEdgeMC(mcName, modelName, pFace)

    if d_x <= limitDistTop or d_x == 0.0:
        d_x = limitDistTop
        beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        createBodyFromFaces(modelName, sFaces)
        afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        newPBody = list(set(afterBodies) - set(beforeBodies))
        for thisBody in newPBody:
            bodiesToMerge.append(thisBody)
        
        rFace = sFaces
        edgesTopOnRFace = refEdges

    elif d_x > limitDistTop:
        offsetDist = d_x - limitDistTop

        refEdges_before = getFaceEdges(modelName, refFaces)
        #print('refEdges_before:{}'.format(refEdges_before))

        tempRefFaceGroup = 'tempRefFaceGroup'
        simlablib.DeleteGroups(tempRefFaceGroup)
        simlablib.CreateGroup(modelName, 'Face', refFaces, tempRefFaceGroup)
        # print('refFaces:{}'.format(refFaces))
        # print('refEdges:{}'.format(refEdges))

        createEdgeByOffset(modelName, refFaces, refEdges, offsetDist, 1)

        refFaces = simlab.getEntityFromGroup(tempRefFaceGroup)
        refEdges_after = getFaceEdges(modelName, refFaces)
        #print('refEdges_after:{}'.format(refEdges_after))

        if set(refEdges_after) == set(refEdges_before):
            rFace = sFaces
            edgesTopOnRFace = refEdges

        else:
            #print('newEdgesCreated')
            extendedFace = getFaceHavingAnyTheEdge(modelName, refFaces, refEdges)
            faceEdges = getFaceEdges(modelName, extendedFace)

            rFace = extendedFace + list(sFaces)

            refEdgeVertexes = getEdgeVertexes(modelName, refEdges)
            edgesTopOnRFace = getFaceEdgeNotAssociatedWithRefEdge(modelName, faceEdges, refEdgeVertexes)
    
    # print('edgesTopOnRFace:{}'.format(edgesTopOnRFace))

    # print('rFace:{}'.format(rFace))  
    beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
    createBodyFromFaces(modelName, rFace)
    afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
    newPBody = list(set(afterBodies) - set(beforeBodies))
    for thisBody in newPBody:
        bodiesToMerge.append(thisBody)
    
    mcName = 'preserveEdgeMC2'
    simlablib.DeleteMeshControl(mcName)
    preserveFaceEdgeMC(mcName, modelName, rFace)

    if bodiesToMerge:
        simlablib.UpdateModel()
        mergeBodies(modelName, bodiesToMerge, beadName)
        sharedFaceGroup = 'Shared Faces'
        simlablib.DeleteGroups(sharedFaceGroup)
        sharedEntities(modelName, [beadName])
        entitiesShared = list(simlab.getEntityFromGroup(sharedFaceGroup))
        if entitiesShared:
            remeshFace(modelName, entitiesShared, beadElemSize, aspectRatio, preserveBoundary=0)
            remeshFace(modelName, entitiesShared, beadElemSize, aspectRatio, preserveBoundary=0)

    allNodeGroups = simlab.getGroupsWithSubString('NodeGroup',['*'])
    simlablib.DeleteGroups(allNodeGroups)
    simlablib.DeleteAllOphanNodes()

    # print('edgesTopOnPFace:{}'.format(edgesTopOnPFace))
    # print('edgesTopOnRFace:{}'.format(edgesTopOnRFace))

    alignUniformEdgeNode(modelName, edgesTopOnPFace)
    alignUniformEdgeNode(modelName, edgesTopOnRFace)
    numLayers = max(int(round(d_x / beadElemSize)),2)
    createFaceFromEdges(modelName, edgesTopOnPFace, edgesTopOnRFace, numLayers)
    
    fillHoleGroup = 'Fill_Hole_Faces'
    simlablib.DeleteGroups(fillHoleGroup)
    fillFreeEdgesOfBody(modelName, beadName)

    for thisBody in connectBody:
        joinOnOvelappingFaces(modelName, beadName, thisBody)

    meshQualityCleanup(modelName, beadName, aspectRatio)

    simlab.redisplayEntity('Model', modelName)

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


def getDistanceBetweenEdgeAndNode(modelName, edge, node):
    DistanceBetweenTwoEntities=''' <DistanceBetweenTwoEntities UUID="53537c0a-6606-4b36-9a95-c05be32f39fc">
    <SupportEntity1>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edge).strip('()''[]') +''',</Edge>
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
    # Imprint_EdgeOn_Face

def getMiddleNode(modelName, edge, vertexNode):
    nodeGroup = 'edgeNodes'
    simlablib.DeleteGroups(nodeGroup)
    simlablib.SelectAssociatedEntities(modelName, 'Edge', edge, 'Node', nodeGroup)

    edgeNodes = list(simlab.getEntityFromGroup(nodeGroup))

    middleEdgeNum = int(len(edgeNodes)/2)

    nodePtDict = dict()

    for thisNode in edgeNodes:
        thisNodePt = np.array(simlab.getNodePositionFromNodeID(modelName, thisNode))
        nodePtDict[thisNode] = thisNodePt
    
    edgeNodes_copy = edgeNodes[:]

    counter = 0
    p0 = vertexNode

    while counter != middleEdgeNum:

        closestNodeInfo = getClosestNodeID(nodePtDict, edgeNodes_copy, p0)
        neighborNode= closestNodeInfo
        # print(neighborNode)
        p0 = neighborNode
        edgeNodes_copy.remove(neighborNode)

        counter += 1
    
    return p0

def getClosestNodeID(nodePtDict, nodeIdList, fromTheNode):

    # make sure the nodeId list have more than 2 elements
    distDict = dict()
    p0 = nodePtDict[fromTheNode]

    for thisNode in nodeIdList:
        thisNodePt = nodePtDict[thisNode]
        this_d = np.linalg.norm(thisNodePt - p0)
        distDict[thisNode] = this_d
    
    closestNodeId = min(distDict, key= distDict.get)

    
    return closestNodeId

def searchFacesFromGroupsWithEdge(modelName, faceGroups, edgesGiven):
    edgeGroup = 'edgeGroup'
    for thisGroup in faceGroups:
        faces = simlab.getEntityFromGroup(thisGroup)
        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', faces, 'Edge', edgeGroup)
        faceEdges = simlab.getEntityFromGroup(edgeGroup)
        if all(thisEdge in faceEdges for thisEdge in edgesGiven):
            return faces
    return []

def getIntersectingRefEdgeAndFace(modelName, edgesGiven, refFaces):
    edgeGroup = 'edgeGroup'

    intersectingFaces = []
    intersectingEdges = []

    for thisFace in refFaces:
        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', [thisFace], 'Edge', edgeGroup)
        faceEdges = simlab.getEntityFromGroup(edgeGroup)
        overlappedEdge = list(set(edgesGiven).intersection(set(faceEdges)))
        if overlappedEdge:
            intersectingEdges.extend(overlappedEdge)
            intersectingFaces.append(thisFace)
    
    return list(set(intersectingEdges)), list(set(intersectingFaces))

def getFaceEdges(modelName, face):
    edgeGroup='edgeGroup'
    simlablib.DeleteGroups(edgeGroup)
    simlablib.SelectAssociatedEntities(modelName, 'Face', face, 'Edge', edgeGroup)
    faceEdges = simlab.getEntityFromGroup(edgeGroup)
    return faceEdges

def getEdgeNodes(modelName, edges):
    nodeGroup = 'nodeGroup'
    simlablib.DeleteGroups(nodeGroup)
    simlablib.SelectAssociatedEntities(modelName, 'Edge', edges, 'Node', nodeGroup)
    edgeNodes = simlab.getEntityFromGroup(nodeGroup)

    return edgeNodes

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

def getFaceHavingOnlyTheEdge(modelName, faces, theEdge):
    facesHavingTheEdges = []
    edgeGroup ='edgeGroup'
    for thisFace in faces:
        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', [thisFace], 'Edge', edgeGroup)
        faceEdges = simlab.getEntityFromGroup(edgeGroup)
        if all(thisEdge in theEdge for thisEdge in faceEdges):
            facesHavingTheEdges.append(thisFace)
    
    return facesHavingTheEdges

def getFaceHavingAnyTheEdge(modelName, faces, theEdge):
    facesHavingTheEdges = []
    edgeGroup ='edgeGroup'
    for thisFace in faces:
        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', [thisFace], 'Edge', edgeGroup)
        faceEdges = simlab.getEntityFromGroup(edgeGroup)
        if any(thisEdge in theEdge for thisEdge in faceEdges):
            facesHavingTheEdges.append(thisFace)
    
    return facesHavingTheEdges

def getEdgeVertexes(modelName, edge):
    vertexGroup = 'vertexGroup'
    simlablib.DeleteGroups(vertexGroup)
    simlablib.SelectAssociatedEntities(modelName, 'Edge', edge, 'Vertex', vertexGroup)
    edgeVertexes = simlab.getEntityFromGroup(vertexGroup)
    return edgeVertexes

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

# def getSharedEdge(modelName, bodies):
#     SharedEntities=''' <SharedEntities CheckBox="ON" UUID="2dc7ae98-62c3-4926-bbde-d08da48208ad">
#     <tag Value="-1"/>
#     <Name Value="SharedEntities1"/>
#     <SupportEntities>
#     <Entities>
#     <Model>'''+ modelName +'''</Model>
#     <Body>'''+ str(bodies).replace("'",'"').strip('()''[]') +'''</Body>
#     </Entities>
#     </SupportEntities>
#     <Faces Value="0"/>
#     <Edges Value="1"/>
#     <Vertices Value="0"/>
#     </SharedEntities>'''
#     simlab.execute(SharedEntities)

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
