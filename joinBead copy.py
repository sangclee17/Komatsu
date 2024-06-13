# coding: shift-jis
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from tkinter.ttk import Separator
import os, sys, importlib
from turtle import width
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

class JoinBeadDialog(basedialog.BaseDialog):
    def __init__(self, master, parent, config, backup):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('ビード合流')
        self.master.resizable(width=False, height=False)
        self.master.attributes('-topmost', True)
        self.master.protocol('WM_DELETE_WINDOW', self.CloseDialog)
        self.config = config
        self.backup = backup

        self.CreateWidgets()

        self.beadEndFace = 'beadEndFace'
        self.stopFace = 'stopFace'
        self.beadCornerFace1 = 'beadCornerFace1'
        self.beadCornerFace2 = 'beadCornerFace2'
        self.groundFace = 'groundFace'
        self.cornerNode1 = 'cornerNode1'
        self.cornerNode2 = 'cornerNode2'

        simlablib.DeleteGroups([self.beadEndFace, self.stopFace, self.beadCornerFace1, self.beadCornerFace2, self.cornerNode1, self.cornerNode2, self.groundFace])

        simlabutil.ClearSelection()       

        simlab.setSelectionFilter('Face')
    
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.nb = ttk.Notebook(self.frmTop)
        self.frmExtendFace = tk.Frame(self.nb)
        self.frmRoundCorner = tk.Frame(self.nb)

        self.nb.add(self.frmExtendFace, text='面延長')
        self.nb.add(self.frmRoundCorner, text='隅処理')
        self.nb.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.CreateNoteBook1()
        self.CreateNoteBook2()
    
    def CreateNoteBook1(self):
        tk.Label(self.frmExtendFace, text='ビード末端面の法線方向に拡張され、ストップ面に結合されます。').pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Frame(self.frmExtendFace, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmSelect = tk.Frame(self.frmExtendFace)
        self.frmSelect.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)

        self.frmFig = tk.Frame(self.frmSelect, width=400)
        self.frmFig.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconExtendFace= ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'extendBeadFace.png')), master=self.frmFig)
        tk.Label(self.frmFig, image=self.iconExtendFace).pack(side=tk.LEFT, anchor=tk.W)

        self.btnBeadEndFace = tk.Button(self.frmFig, text='末端面', command= self.SelectBeadEndFace, width=10)
        self.btnBeadEndFace.place(x=70, y=175)

        self.btnLimitFace = tk.Button(self.frmFig, text='ストップ面', command= self.SelectLimitFace, width=10)
        self.btnLimitFace.place(x=240, y=40)

        tk.Frame(self.frmExtendFace, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmBeadElemInfo = tk.Frame(self.frmExtendFace)
        self.frmBeadElemInfo.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        tk.Label(self.frmBeadElemInfo, text='要素長：').pack(side=tk.LEFT, anchor=tk.W)
        self.entElemSize = tk.Entry(self.frmBeadElemInfo, width=7)
        self.entElemSize.pack(side=tk.LEFT, anchor=tk.W)
        entElemSize = self.config.Get('Bead_Elem_Size')
        self.entElemSize.insert(tk.END, entElemSize)

        self.varRemesh = tk.BooleanVar()
        self.chkRemesh = tk.Checkbutton(self.frmBeadElemInfo, text='　再メッシュ　', variable=self.varRemesh)
        self.chkRemesh.pack(side=tk.LEFT, anchor=tk.W, padx=5)

        self.varMergeBody = tk.BooleanVar()
        self.chkMergeBody = tk.Checkbutton(self.frmBeadElemInfo, text='　ボディマージ　', variable=self.varMergeBody)
        self.chkMergeBody.pack(side=tk.LEFT, anchor=tk.W)
        self.varMergeBody.set(1)

        tk.Frame(self.frmExtendFace, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmCtrl = tk.Frame(self.frmExtendFace)
        self.frmCtrl.pack(side=tk.BOTTOM, anchor=tk.NE, expand=1, fill=tk.X)

        btnWidth = 10
        self.btnExtend = tk.Button(self.frmCtrl, text=' 実行 ', compound=tk.LEFT, command=self.ExtendBeadEndFace, width=10)
        self.btnExtend.pack(side=tk.LEFT, anchor=tk.NW)

        self.btnUndo = tk.Button(self.frmCtrl, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=10)
        self.btnUndo.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo)

        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.LEFT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.E)
    
    def SelectBeadEndFace(self):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        if len(face) != 1:
            messagebox.showinfo('情報','一つの面を選んでください。')
            return
        
        simlablib.DeleteGroups(self.beadEndFace)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, self.beadEndFace)

        self.UpdateButtonFG()
    
    def SelectLimitFace(self):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return

        if len(face) != 1:
            messagebox.showinfo('情報','一つのを選んでください。')
            return
        
        simlablib.DeleteGroups(self.stopFace)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, self.stopFace)

        self.UpdateButtonFG()
    
    def UpdateButtonFG(self):
        groups = [self.beadEndFace, self.stopFace]
        widgets = [self.btnBeadEndFace, self.btnLimitFace]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)
    
    def ExtendBeadEndFace(self):
        endFace = simlab.getEntityFromGroup(self.beadEndFace)
        if not endFace:
            messagebox.showinfo('情報','ビード末端面を選択してください。')
            return
        limitFace = simlab.getEntityFromGroup(self.stopFace)
        if not limitFace:
            messagebox.showinfo('情報','ストップ面を選択してください。')
            return
        
        beadElemSize = self.entElemSize.get()
        if len(beadElemSize) == 0:
            messagebox.showinfo('情報', '要素長を入力してください。')
            return
        
        try:
            beadElemSize = float(beadElemSize)
        except ValueError:
            messagebox.showinfo('情報','要素長で数字を入力してください。')
            return
        else:
            if beadElemSize <= 0:
                messagebox.showinfo('情報','要素長で０より大きい数字を入力してください。')
                return
        
        remeshChecked = self.varRemesh.get()
        bodyMergeChecked = self.varMergeBody.get()
        
        allModelNames = simlab.getAllRootModelNames('FEM')
        if len(allModelNames) > 1:
            messagebox.showinfo('情報','モデル名が複数あります。マージして一個にしてください。')
            return
        elif len(allModelNames) == 0:
            messagebox.showinfo('情報','FEモデルを作成してください。')
            return

        modelName = simlab.getModelName('FEM')

        self.backup.Save('ExtendBeadFace')

        bodyGroup = 'bodyGroup'
        simlablib.DeleteGroups(bodyGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', endFace, 'Body', bodyGroup)
        beadBody = simlab.getBodiesFromGroup(bodyGroup)

        simlablib.DeleteGroups(bodyGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', limitFace, 'Body', bodyGroup)
        stopBody = simlab.getBodiesFromGroup(bodyGroup)


        beadFaceNormal = np.array(simlab.getNormalFromFaceGroup(self.beadEndFace))
        vertexGroup = 'vertexGroup'
        simlablib.DeleteGroups(vertexGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', endFace, 'Vertex', vertexGroup)
        faceVertexes = simlab.getEntityFromGroup(vertexGroup)
        refPt = np.array(simlab.getVertexPositionFromVertexID(modelName,faceVertexes[0]))
        nodeGroup = 'nodeGroup'
        simlablib.DeleteGroups(nodeGroup)
        refNode = getVertexNode(modelName, faceVertexes[0], nodeGroup)

        if beadFaceNormal.size == 0:
            beadFaceNormal = getNormalFromThreePts([simlab.getVertexPositionFromVertexID(modelName, faceVertexes[idx]) for idx in range(3)])
            vertexGroup = 'vertexGroup'
            simlablib.DeleteGroups(vertexGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Face', limitFace, 'Vertex', vertexGroup)
            limitFaceVertexes = simlab.getEntityFromGroup(vertexGroup)
            if np.dot(beadFaceNormal, np.array(simlab.getVertexPositionFromVertexID(modelName, limitFaceVertexes[0]))) - np.dot(beadFaceNormal, refPt) < 0:
                print('opposite Direction')
                beadFaceNormal = -1 * beadFaceNormal
        
        print('beadFaceNormal:{}'.format(beadFaceNormal))

        fromPt = refPt
        toPt = refPt + beadFaceNormal* 2

        dist = getDistanceBetweenFaceAndNode(modelName, limitFace, refNode)
        print('distance:{}'.format(dist))

        beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        extendToLimitFace(modelName, endFace, limitFace, list(fromPt), list(toPt), list(beadFaceNormal), max(int(round(dist/beadElemSize)), 1))
        afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        extrudedBody = list(set(afterBodies) - set(beforeBodies))
        if not extrudedBody:
            messagebox.showinfo('情報','Extrudeのエーラが発生しました。')
            return
               
        simlablib.DeleteSolidElements(modelName, extrudedBody)

        adjBodyGroup = 'Adjacent_Bodies'
        simlablib.DeleteGroups(adjBodyGroup)
        searchAdjacentBodies(modelName, extrudedBody[0], tol=1e-1)
        adjBodies = simlab.getBodiesFromGroup(adjBodyGroup)
        for thisBody in adjBodies:
            joinOverlapFaces(modelName, extrudedBody[0], thisBody, tol=0.1)
        
        simlablib.MergeBodies(modelName, list(beadBody)+ list(extrudedBody))
        
        if bodyMergeChecked:
            simlablib.MergeBodies(modelName, list(beadBody)+ list(stopBody))

        internalFaceGroup = 'Show_Internal_Faces'
        simlablib.DeleteGroups(internalFaceGroup)
        getInternalFaces(modelName, beadBody)
        internalFaces = simlab.getEntityFromGroup(internalFaceGroup)
        if internalFaces:
            simlablib.DeleteEntities(modelName, 'Face', internalFaces)
        
        simlablib.UpdateModel()
        
        if remeshChecked:
            sharedFaceGroup = 'Shared Faces'
            simlablib.DeleteGroups(sharedFaceGroup)
            sharedEntities(modelName, beadBody)

            sharedFaces = simlab.getEntityFromGroup(sharedFaceGroup)
            try:
                aspectRatio = float(self.config.Get('Aspect_Ratio'))
            except ValueError:
                aspectRatio = 10
            remeshFace(modelName, sharedFaces, beadElemSize, aspectRatio, preserveEdge=0)
            # remeshJoinedFace(modelName, list(beadBody)+ list(extrudedBody), beadElemSize, aspectRatio)

        simlab.redisplayEntity('Model', modelName)

        groups = [self.beadEndFace, self.stopFace]
        simlablib.DeleteGroups(groups)
        self.UpdateButtonFG()

    ##########################################
    def CreateNoteBook2(self):
        tk.Label(self.frmRoundCorner, text='ビード面と指定されたノード２点を選択してください。').pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Frame(self.frmRoundCorner, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmSelect2 = tk.Frame(self.frmRoundCorner)
        self.frmSelect2.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)

        self.frmFig2 = tk.Frame(self.frmSelect2, width=400)
        self.frmFig2.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconBeadCorner= ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'beadCorner1.png')), master=self.frmFig2)
        tk.Label(self.frmFig2, image=self.iconBeadCorner).pack(side=tk.LEFT, anchor=tk.W)

        self.btnBeadFace1 = tk.Button(self.frmFig2, text='ビード面１', command= lambda: self.SelectBeadFace(1), width=10)
        self.btnBeadFace1.place(x=40, y=120)

        self.btnBeadFace2 = tk.Button(self.frmFig2, text='ビード面２', command= lambda: self.SelectBeadFace(2), width=10)
        self.btnBeadFace2.place(x=270, y=120)

        self.btnNode1 = tk.Button(self.frmFig2, text='ノード１', command= lambda: self.SelectCornerNode(1), width=7)
        self.btnNode1.place(x=140, y=115)

        self.btnNode2 = tk.Button(self.frmFig2, text='ノード２', command= lambda: self.SelectCornerNode(2), width=7)
        self.btnNode2.place(x=138, y=185)

        self.btnGround = tk.Button(self.frmFig2, text='地面', command=self.SelectGroundFace, width=10)
        self.btnGround.place(x=180, y=230)

        tk.Frame(self.frmRoundCorner, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmBeadInfo2 = tk.Frame(self.frmRoundCorner)
        self.frmBeadInfo2.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
        self.frmBeadElemInfo2 = tk.Frame(self.frmBeadInfo2)
        self.frmBeadElemInfo2.pack(side=tk.LEFT, anchor=tk.W)
        tk.Label(self.frmBeadElemInfo2, text='  要素長：').pack(side=tk.LEFT, anchor=tk.W)
        self.entElemSizeForCorner = tk.Entry(self.frmBeadElemInfo2, width=7)
        self.entElemSizeForCorner.pack(side=tk.LEFT, anchor=tk.W)
        entElemSize = self.config.Get('Bead_Elem_Size')
        self.entElemSizeForCorner.insert(tk.END, entElemSize)

        self.frmR = tk.Frame(self.frmBeadInfo2)
        self.frmR.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        tk.Label(self.frmR, text='  円弧のR：').pack(side=tk.LEFT, anchor=tk.W)
        self.entR = tk.Entry(self.frmR, width=7)
        self.entR.pack(side=tk.LEFT, anchor=tk.W)
        self.entR.insert(tk.END, 15)

        tk.Frame(self.frmRoundCorner, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmCtrl2 = tk.Frame(self.frmRoundCorner)
        self.frmCtrl2.pack(side=tk.BOTTOM, anchor=tk.NE, expand=1, fill=tk.X)

        btnWidth = 10
        self.btnExecuteCorner = tk.Button(self.frmCtrl2, text=' 実行 ', compound=tk.LEFT, command=self.ExecuteCorner, width=10)
        self.btnExecuteCorner.pack(side=tk.LEFT, anchor=tk.NW)

        self.btnUndo2 = tk.Button(self.frmCtrl2, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=10)
        self.btnUndo2.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo2)

        self.btnClose = tk.Button(self.frmCtrl2, text=' 閉じる ', compound=tk.LEFT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.E)
    
    def SelectGroundFace(self):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        if len(face) != 1:
            messagebox.showinfo('情報','一つの面を選んでください。')
            return
        groupName = self.groundFace
        simlablib.DeleteGroups(groupName)
        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, groupName)

        self.UpdateButtonFG2()
    
    def SelectBeadFace(self, num):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        if len(face) != 1:
            messagebox.showinfo('情報','一つの面を選んでください。')
            return
        
        groupName = 'beadCornerFace{}'.format(num)
        simlablib.DeleteGroups(groupName)
        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, groupName)

        self.UpdateButtonFG2()
        
    def SelectCornerNode(self, num):
        node = simlab.getSelectedEntities('NODE')
        if len(node) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        groupName = 'cornerNode{}'.format(num)
        simlablib.DeleteGroups(groupName)
        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Node', node, groupName)
        self.UpdateButtonFG2()
    
    def ExecuteCorner(self):
        face1 = simlab.getEntityFromGroup(self.beadCornerFace1)
        face2 = simlab.getEntityFromGroup(self.beadCornerFace2)
        groundFace = simlab.getEntityFromGroup(self.groundFace)

        node1 = simlab.getEntityFromGroup(self.cornerNode1)
        node2 = simlab.getEntityFromGroup(self.cornerNode2)

        if not face1 or not face2 or not node1 or not node2:
            messagebox.showinfo('情報','二つのビード面とノード4点を登録してください。')
            return
        if not groundFace:
            messagebox.showinfo('情報','地面を選択してください。')
            return

        
        allModelNames = simlab.getAllRootModelNames('FEM')
        if len(allModelNames) > 1:
            messagebox.showinfo('情報','モデル名が複数あります。マージして一個にしてください。')
            return
        elif len(allModelNames) == 0:
            messagebox.showinfo('情報','FEモデルを作成してください。')
            return
        
        beadElemSize = self.entElemSizeForCorner.get()
        if len(beadElemSize) == 0:
            messagebox.showinfo('情報', '要素長を入力してください。')
            return
        
        try:
            beadElemSize = float(beadElemSize)
        except ValueError:
            messagebox.showinfo('情報','要素長で数字を入力してください。')
            return
        else:
            if beadElemSize <= 0:
                messagebox.showinfo('情報','要素長で０より大きい数字を入力してください。')
                return
        
        arcR = self.entR.get()
        if len(arcR) == 0:
            messagebox.showinfo('情報', '円弧のRを入力してください。')
            return
        try:
            arcR = float(arcR)
        except ValueError:
            messagebox.showinfo('情報','円弧のRで数字を入力してください。')
            return
        else:
            if arcR <= 0:
                messagebox.showinfo('情報','円弧のRで０より大きい数字を入力してください。')
                return

        modelName = simlab.getModelName('FEM')

        self.backup.Save('BeadCorner')

        pt1 = np.array(simlab.getNodePositionFromNodeID(modelName, node1[0]))
        pt2 = np.array(simlab.getNodePositionFromNodeID(modelName, node2[0]))

        bodyAssFaceSelected = set()
        bodyGroup = 'bodyGroup'
        for thisFace in list(face1)+list(face2):
            simlablib.DeleteGroups(bodyGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Face', [thisFace], 'Body', bodyGroup)
            thisBody = simlab.getBodiesFromGroup(bodyGroup)
            bodyAssFaceSelected.add(thisBody[0])
        bodyAssFaceSelected = list(bodyAssFaceSelected)

        nodeGroup = 'nodeGroup'
        edgeGroup = 'edgeGroup'
        edgesOnGround = []

        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', groundFace, 'Edge', edgeGroup)
        groundEdges = simlab.getEntityFromGroup(edgeGroup)

        for thisFace in list(face1)+list(face2):
            simlablib.DeleteGroups(edgeGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Face', [thisFace], 'Edge', edgeGroup)
            faceEdges = simlab.getEntityFromGroup(edgeGroup)
            
            intersectingEdges = list(set(faceEdges).intersection(set(groundEdges)))
            if intersectingEdges:
                edgesOnGround.append((thisFace,intersectingEdges))
                # simlablib.DeleteGroups(nodeGroup)
                # simlablib.SelectAssociatedEntities(modelName, 'Edge', [thisEdge], 'Node', nodeGroup)
                # edgeNodes = simlab.getEntityFromGroup(nodeGroup)
                # if node2[0] in edgeNodes and not node1[0] in edgeNodes:
                #     edgesOnGround.append((thisFace,thisEdge))
        
        print(edgesOnGround)

        if len(edgesOnGround) != 2:
            messagebox.showinfo('情報',' ビード面を共有してください。')
            return

        vertexGroup = 'vertexGroup'
        ptsOnEdge = []
        for thisTup in edgesOnGround:
            thisFace, thisEdge = thisTup
            simlablib.DeleteGroups(vertexGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Edge', [thisEdge], 'Vertex', vertexGroup)
            edgeVertexes = simlab.getEntityFromGroup(vertexGroup)

            maxDist = 1e-1
            theVpt = 0
            for thisV in edgeVertexes:
                thisV_pt = simlab.getVertexPositionFromVertexID(modelName, thisV)
                dist = np.linalg.norm(thisV_pt - pt2)
                if dist > maxDist:
                    theVpt = thisV_pt
                    maxDist = dist
            
            v = theVpt - pt2
            pt = pt2 + v/np.linalg.norm(v) * arcR
            ptsOnEdge.append((thisFace, pt))

            # edgeNodes = simlab.getEntityFromGroup(nodeGroup)
            # for thisNode in edgeNodes:
            #     if thisNode in node2:
            #         continue

            #     v = np.array(simlab.getNodePositionFromNodeID(modelName, thisNode)) - pt2
            #     # pt = pt2 + v/np.linalg.norm(v) * dist_12
            #     pt = pt2 + v/np.linalg.norm(v) * arcR
            #     ptsOnEdge.append((thisFace, pt))

            #     break
        
        tup3, tup4 = ptsOnEdge

        print('tup3:{}'.format(tup3))
        print('tup4:{}'.format(tup4))

        faceAssPt3, pt3 = tup3
        faceAssPt4, pt4 = tup4

        
        plane = getNormalFromThreePts([pt2, pt3, pt4])
        if plane is None:
            plane = np.array(simlab.getNormalFromFaceGroup(self.groundFace))
            if plane.size == 0:
                messagebox.showinfo('情報', '直線ビードで平面を定義できません。')
                return

        if np.dot(plane, pt1) - np.dot(plane, pt3) < 0:
            plane = plane * -1

        #print('plane:{}'.format(plane))
        d = np.dot(plane, pt3)

        pt5 = pt1 - plane * (np.dot(plane, pt1) - d)
        print(pt5)
        
        breakEdgeGroup = 'Break_Face_Edges'
        simlablib.DeleteGroups(breakEdgeGroup)

        cuttingPts1 = [pt3, pt1, pt5]
        print('cuttingPts1:{}'.format(cuttingPts1))
        n1 = getNormalFromThreePts(cuttingPts1)
        if np.dot(n1,pt2) - np.dot(n1, pt3) < 0:
            cuttingPts1[1], cuttingPts1[2] = cuttingPts1[2], cuttingPts1[1]
        cuttingPlane1 = simlabutil.Convert3PointsOnPlaneTo4Points(cuttingPts1)
        breakFace(modelName, [faceAssPt3], cuttingPlane1)
        cuttingEdge1 = simlab.getEntityFromGroup(breakEdgeGroup)
        node3 = getNodeByXYZ(modelName, cuttingEdge1, pt3)

        simlablib.DeleteGroups(breakEdgeGroup)
        cuttingPts2 = [pt4, pt1, pt5]
        n2 = getNormalFromThreePts(cuttingPts2)
        if np.dot(n2,pt2) - np.dot(n2, pt4) < 0:
            cuttingPts2[1], cuttingPts2[2] = cuttingPts2[2], cuttingPts2[1]
        cuttingPlane2 = simlabutil.Convert3PointsOnPlaneTo4Points(cuttingPts2)
        breakFace(modelName, [faceAssPt4], cuttingPlane2)
        cuttingEdge2 = simlab.getEntityFromGroup(breakEdgeGroup)
        node4 = getNodeByXYZ(modelName, cuttingEdge2, pt4)
        #print('cuttingEdge1:{}'.format(cuttingEdge1))
        #print('cuttingEdge2:{}'.format(cuttingEdge2))

        print('node3:{}'.format(node3))
        print('node4:{}'.format(node4))

        selectedFaces1 = list(simlab.getEntityFromGroup(self.beadCornerFace1))
        selectedFaces2 = list(simlab.getEntityFromGroup(self.beadCornerFace2))

        facesToExclude = []
        faceOnPlaneGroup = 'Show_Faces'
        simlablib.DeleteGroups(faceOnPlaneGroup)
        getFacesByPlane(modelName, bodyAssFaceSelected, cuttingPlane1, below=1)
        facesBelowPlane = list(simlab.getEntityFromGroup(faceOnPlaneGroup))
        facesToExclude.extend(facesBelowPlane)

        simlablib.DeleteGroups(faceOnPlaneGroup)
        getFacesByPlane(modelName, bodyAssFaceSelected, cuttingPlane2, below=1)
        facesBelowPlane = list(simlab.getEntityFromGroup(faceOnPlaneGroup))
        facesToExclude.extend(facesBelowPlane)

        facesToAlign = list(set(selectedFaces1 + selectedFaces2) - set(facesToExclude))

        faceGroup ='faceGroup'
        simlablib.DeleteGroups(faceGroup)
        simlablib.CreateGroup(modelName, 'Face', facesToAlign, faceGroup)
        if len(facesToAlign) > 1:
            simlablib.MergeFaces(modelName, facesToAlign)
        facesToAlign = simlab.getEntityFromGroup(faceGroup)

        #print('facesToAlign:{}'.format(facesToAlign))

        edgesToAlign = []
        for thisFace in facesToAlign:
            simlablib.DeleteGroups(edgeGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Face', [thisFace], 'Edge', edgeGroup)
            faceEdges = simlab.getEntityFromGroup(edgeGroup)

            for thisEdge in faceEdges:
                if thisEdge in cuttingEdge1 or thisEdge in cuttingEdge2:
                    continue
                simlablib.DeleteGroups(nodeGroup)
                simlablib.SelectAssociatedEntities(modelName, 'Edge', [thisEdge], 'Node', nodeGroup)
                edgeNodes = simlab.getEntityFromGroup(nodeGroup)
                if node1[0] in edgeNodes:
                    continue
                edgesToAlign.append(thisEdge)

        #print('edgesToAlign:{}'.format(edgesToAlign))

        if edgesToAlign:
            # pt6 = (pt3+pt4)/2

            # v_26 = pt6-pt2
            # d_26 = np.linalg.norm(v_26)
            # n_26 = v_26 / d_26

            # pt7 = pt2 + n_26 * d_26 / 2

            v24 = pt4 - pt2
            n24 = v24/ np.linalg.norm(v24)
            pt0 = pt3 + n24 * arcR
            print('pt0:{}'.format(pt0))

            v02 = pt2 - pt0
            n02 = v02/np.linalg.norm(v02)
            pt7 = pt0 + n02 *arcR
            print('pt7:{}'.format(pt7))

            nextNode = simlab.getNextNodeID(modelName)
            createNodeByCoordinate(modelName, list(pt7), nextNode)
            circleNodes = [node3, nextNode, node4]
            radius = getRadiusOfCircle([pt3, pt7, pt4])
            radius = int(radius*10000)/10000
            #print('radius:{}'.format(radius))
            alignCircle(modelName, edgesToAlign, circleNodes, radius)

            if facesToAlign:
                plane1 = simlabutil.Convert3PointsOnPlaneTo4Points([pt3, pt1, pt4])
                alignPlane(modelName, facesToAlign, plane1)

                plane2 = simlabutil.Convert3PointsOnPlaneTo4Points([pt3, pt2, pt4])

                alignEdgePlane(modelName, edgesToAlign, plane2)

            try:
                aspectRatio = float(self.config.Get('Aspect_Ratio'))
            except ValueError:
                aspectRatio = 10
            remeshFace(modelName, facesToAlign, beadElemSize, aspectRatio, preserveEdge=0)
        
        allNodeGroups = simlab.getGroupsWithSubString('NodeGroup',['*'])
        if allNodeGroups:
            simlablib.DeleteGroups(allNodeGroups)
        simlablib.DeleteAllOphanNodes()
        simlablib.DeleteGroups([self.beadCornerFace1, self.beadCornerFace2, self.groundFace])
        self.UpdateButtonFG2()
    
    def UpdateButtonFG2(self):
        groups = [self.beadCornerFace1, self.beadCornerFace2, self.groundFace, self.cornerNode1, self.cornerNode2]
        widgets = [self.btnBeadFace1, self.btnBeadFace2, self.btnGround, self.btnNode1, self.btnNode2]

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
    
    def CloseDialog(self):
        # groups = [self.referenceFace, self.slopeFace, self.projectionFace, self.weldingEdge, self.connectBody]
        # simlablib.DeleteGroups(groups)
        super().CloseDialog()

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

def getNodeByXYZ(modelName, edge, coord):
    nodeGroup = 'nodeGroup'
    simlablib.DeleteGroups(nodeGroup)
    simlablib.SelectAssociatedEntities(modelName, 'Edge', edge, 'Node', nodeGroup)
    edgeNodes = simlab.getEntityFromGroup(nodeGroup)

    minDistance = 1e6
    minNode = None
    for thisNode in edgeNodes:
        pt = np.array(simlab.getNodePositionFromNodeID(modelName, thisNode))

        dist = np.linalg.norm(pt- coord)
        if minDistance > dist:
            minDistance = dist
            minNode = thisNode
    return minNode

def getRadiusOfCircle(threePts):
    p1,p2,p3 = threePts
    n = getNormalFromThreePts(threePts)

    p12 = p2 - p1
    p13 = p3 - p1

    A = np.array([n, p12, p13])
    B = np.array([np.dot(n,p1), np.dot(p12,((p1+p2)/2)), np.dot(p13,((p1+p3)/2))])
    B = B.reshape(len(B),1)
    X = (np.linalg.solve(A, B)).T

    p0 = np.array(X[0])
    v1 = p1 - p0
    radius = np.linalg.norm(v1)
    return radius


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

def alignCircle(modelName, edge, threeNodes, radius):
    AlignCircular=''' <AlignCircular UUID="1AE4B435-C6D2-4b3e-84A7-1589F0D51DF8" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value=""/>
    <Select Value="Select"/>
    <Edge>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edge).strip('()''[]') +'''</Edge>
    </Entities>
    </Edge>
    <Axis Value="Nodes"/>
    <Entity>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Node>'''+ str(threeNodes).strip('()''[]') +'''</Node>
    </Entities>
    </Entity>
    <Radius Value="'''+ str(radius) +'''"/>
    <ProjectMidNodes Value="0"/>
    <OffsetNodes EntityTypes="" Option="0" Value="" ModelIds=""/>
    </AlignCircular>'''
    simlab.execute(AlignCircular)
    # print(AlignCircular)

def alignEdgePlane(modelName, edge, pts):
    pt1, pt2, pt3, pt4 = pts
    AlignPlanar=''' <AlignPlanar UUID="b9175a92-dd76-4c68-b31c-0c20c2afa2c3" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value=""/>
    <Select Value="TargetFace"/>
    <Entities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edge).strip('()''[]') +'''</Edge>
    </Entities>
    </Entities>
    <DeleteZeroAreaElement Value="0"/>
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

def alignPlane(modelName, face, pts):
    pt1, pt2, pt3, pt4 = pts
    AlignPlanar=''' <AlignPlanar UUID="b9175a92-dd76-4c68-b31c-0c20c2afa2c3" CheckBox="ON">
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

def remeshFace(modelName, faces, avgElem, aspectRatio, preserveEdge=1):
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
    <PreserveBoundaryEdges Value="'''+ str(preserveEdge) +'''"/>
    <NumberOfSolidLayersToUpdate Value="3"/>
    <TriOption>
    <GradeFactor Value="1.5"/>
    <MaxAnglePerElem Value="45 deg"/>
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

# def remeshJoinedFace(modelName, bodies, avgElem, aspectRatio):
#     SurfaceLocalRemesh=''' <NewLocalReMesh UUID="83ab93df-8b5e-4a48-a209-07ed417d75bb">
#     <tag Value="-1"/>
#     <Name Value="NewLocalReMesh1"/>
#     <SupportEntities>
#     <Entities>
#     <Model>'''+ modelName +'''</Model>
#     <Body>'''+ str(bodies).replace("'",'"').strip('()''[]') +'''</Body>
#     </Entities>
#     </SupportEntities>
#     <ElemType Value="0"/>
#     <AverageElemSize Value="'''+ str(avgElem) +'''"/>
#     <MinElemSize Value="'''+ str(avgElem/aspectRatio) +'''"/>
#     <PreserveBoundaryEdges Value="0"/>
#     <NumberOfSolidLayersToUpdate Value="3"/>
#     <TriOption>
#     <GradeFactor Value="1.5"/>
#     <MaxAnglePerElem Value="45 deg"/>
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

def joinOverlapFaces(modelName, bodyToBeKept, bodyToBeModiFied, tol=0.1):
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
    <LocalRemesh Value="0"/>
    <ShowOrJoin Value="0"/>
    </Join>'''
    simlab.execute(Join)

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

def getNormalFromThreePts(pts):
    p1,p2,p3 = pts
    p1 = np.array(p1)
    p2 = np.array(p2)
    p3 = np.array(p3)

    v1 = (p2 - p1) / np.linalg.norm(p2 - p1)
    v2 = (p3 - p1) / np.linalg.norm(p3 - p1)
    cp = np.cross(v1,v2)

    
    denum = np.linalg.norm(cp)

    if denum < 1e-3:
        return None

    return cp / np.linalg.norm(cp)

def extendToLimitFace(modelName, faceToExtrude, limitFace, fromPt, toPt, direcV, numLayers):
    Extrude=''' <FEAExtrude gda="" UUID="12B94009-EA6B-483f-BB9B-6305E23B8B9D">
    <tag Value="-1"/>
    <Name Value=""/>
    <Extrude_Option Value="3"/>
    <EntityList Flag="1" Entity="">
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(faceToExtrude).strip('()''[]') +'''</Face>
    </Entities>
    </EntityList>
    <Group Flag="0" Entity="" Value=""/>
    <UseExist Flag="" Entity=""/>
    <DistanceNormalToElem Flag=""/>
    <DistanceDirectionRegion/>
    <DistanceRadialRegion/>
    <DistanceSpherical Flag="" Value=""/>
    <Distance Value="10"/>
    <PlaneRegion/>
    <PlaneNormalToPlane Flag="0"/>
    <PlaneDirectionRegion>
    <RegionObject>
    <PlaneDirection>
        <Pt1 Value="'''+ str(toPt).strip('()''[]') +'''"/>
        <Pt2 Value="'''+ str(fromPt).strip('()''[]') +'''"/>
        <DirectionVector Value="'''+ str(direcV).strip('()''[]') +'''"/>
        <UnitVector Value="0"/>
        <Arbitary Value="1"/>
    </PlaneDirection>
    </RegionObject>
    </PlaneDirectionRegion>
    <SecEntity Entity=""/>
    <SecStrtPt Value=""/>
    <Flip Value=""/>
    <Guide Flag="" Entity=""/>
    <Lmt Entity="">
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(limitFace).strip('()''[]') +'''</Face>
    </Entities>
    </Lmt>
    <NoOfLayers Value="'''+ str(numLayers) +'''"/>
    <EdgeElemType Value=""/>
    <FaceElemType Flag="1" Value="1"/>
    <ParentBody Flag="0"/>
    <Shared Flag="1"/>
    <InFlate Value=""/>
    <GradeFactor Check="0" Value="1.0"/>
    <CreateBodyForSideAndTopFaces Flag=""/>
    <ConnectFace Flag="0"/>
    <Output/>
    </FEAExtrude>'''
    simlab.execute(Extrude)

def getInternalFaces(modelName, body):
    ShowInternalFaces=''' <ShowInternalFaces recordable="0" UUID="72FA71A7-3DA1-43d3-AFC3-C0CB36B4C63D">
    <tag Value="-1"/>
    <Name Value="ShowInternalFaces1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body>'''+ str(body).replace("'",'"').strip('()''[]') +'''</Body>
    </Entities>
    </SupportEntities>
    </ShowInternalFaces>'''
    simlab.execute(ShowInternalFaces)