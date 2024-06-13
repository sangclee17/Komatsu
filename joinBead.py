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

        self.beadCornerFace = 'beadCornerFace'
        self.groundFace = 'groundFace'
        self.cornerNode = 'cornerNode'

        self.threeBeadFaces = 'threeBeadFaces'

        simlablib.DeleteGroups([self.beadEndFace, self.stopFace, self.beadCornerFace, self.cornerNode, self.groundFace, self.threeBeadFaces])

        simlabutil.ClearSelection()       

        simlab.setSelectionFilter('Face')
    
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.nb = ttk.Notebook(self.frmTop)
        self.frmExtendFace = tk.Frame(self.nb)
        self.frmRoundCorner = tk.Frame(self.nb)
        self.frmThreeBeads = tk.Frame(self.nb)
        
        self.nb.add(self.frmExtendFace, text='面延長')
        self.nb.add(self.frmRoundCorner, text='隅処理')
        self.nb.add(self.frmThreeBeads, text='合流面')
        self.nb.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.CreateNoteBook1()
        self.CreateNoteBook2()
        self.CreateNoteBook3()
    
    def CreateNoteBook3(self):
        tk.Label(self.frmThreeBeads, text='ビード間合流する面を選択してください。').pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Frame(self.frmThreeBeads, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmThreeBeadsSelect = tk.Frame(self.frmThreeBeads)
        self.frmThreeBeadsSelect.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
        self.frmFig3 = tk.Frame(self.frmThreeBeadsSelect, width=400)
        self.frmFig3.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconThreeBeads= ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'threeBeadsMerge.png')), master=self.frmFig3)
        tk.Label(self.frmFig3, image=self.iconThreeBeads).pack(side=tk.LEFT, anchor=tk.W)

        self.btnThreeBeadsFace= tk.Button(self.frmFig3, text='合流面', command= self.SelectMergeFace, width=10)
        self.btnThreeBeadsFace.place(x=60, y=115)

        tk.Frame(self.frmThreeBeads, height=5).pack(side=tk.TOP, anchor=tk.CENTER)
        self.frmBeadElemInfo3 = tk.Frame(self.frmThreeBeads)
        self.frmBeadElemInfo3.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        tk.Label(self.frmBeadElemInfo3, text='要素長：').pack(side=tk.LEFT, anchor=tk.W)
        self.entElemSizeForThree = tk.Entry(self.frmBeadElemInfo3, width=7)
        self.entElemSizeForThree.pack(side=tk.LEFT, anchor=tk.W)
        entElemSize = self.config.Get('Bead_Elem_Size')
        self.entElemSizeForThree.insert(tk.END, entElemSize)

        tk.Frame(self.frmThreeBeads, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmCtrl3 = tk.Frame(self.frmThreeBeads)
        self.frmCtrl3.pack(side=tk.BOTTOM, anchor=tk.NE, expand=1, fill=tk.X)

        btnWidth = 10
        self.btnMergeFace = tk.Button(self.frmCtrl3, text=' 実行 ', compound=tk.LEFT, command=self.CreateMergeFace, width=10)
        self.btnMergeFace.pack(side=tk.LEFT, anchor=tk.NW)

        self.btnUndo3 = tk.Button(self.frmCtrl3, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=10)
        self.btnUndo3.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo3)

        self.btnClose = tk.Button(self.frmCtrl3, text=' 閉じる ', compound=tk.LEFT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.E)

    
    def SelectMergeFace(self):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        simlablib.DeleteGroups(self.threeBeadFaces)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, self.threeBeadFaces)

        self.UpdateButtonFG3()

    def CreateMergeFace(self):
        mergeFaces = simlab.getEntityFromGroup(self.threeBeadFaces)
        if not mergeFaces:
            messagebox.showinfo('情報','合流面を選択してください。')
            return
        
        beadElemSize = self.entElemSizeForThree.get()
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
        
        allModelNames = simlab.getAllRootModelNames('FEM')
        if len(allModelNames) > 1:
            messagebox.showinfo('情報','モデル名が複数あります。マージして一個にしてください。')
            return
        elif len(allModelNames) == 0:
            messagebox.showinfo('情報','FEモデルを作成してください。')
            return

        modelName = simlab.getModelName('FEM')

        self.backup.Save('MergeInThreeWay')

        bodyGroup = 'bodyGroup'
        simlablib.DeleteGroups(bodyGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', mergeFaces, 'Body', bodyGroup)
        bodyAssMergeFaces = list(simlab.getBodiesFromGroup(bodyGroup))

        beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        createBodyFromFaces(modelName, mergeFaces)
        afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        newBody = list(set(afterBodies) -set(beforeBodies))
        
        if not newBody:
            messagebox.showinfo('情報','合流面作成に失敗しました。')
            return
        
        sharedFaceGroup = 'Shared Faces'
        simlablib.DeleteGroups(sharedFaceGroup)
        sharedEntities(modelName, newBody)
        entitiesShared = list(simlab.getEntityFromGroup(sharedFaceGroup))

        try:
            aspectRatio = float(self.config.Get('Aspect_Ratio'))
        except ValueError:
            aspectRatio = 10

        if entitiesShared:
            remeshFace(modelName, entitiesShared, beadElemSize, aspectRatio, preserveEdge=0 )

        # Fill_Hole_Faces
        fillHoleGroup = 'Fill_Hole_Faces'
        simlablib.DeleteGroups(fillHoleGroup)
        fillFreeEdgesOfBody(modelName, newBody[0])

        filledFace = simlab.getEntityFromGroup(fillHoleGroup)
        if filledFace:
            remeshFace(modelName, filledFace, beadElemSize, aspectRatio, preserveEdge=1)

        bodiesToMerge = []
        internalFaces = set()
        faceGroup = 'faceGroup'
        for thisBody in bodyAssMergeFaces:
            if thisBody.startswith('Weld_Body'):
                bodiesToMerge.append(thisBody)
                simlablib.DeleteGroups(faceGroup)
                simlablib.SelectAssociatedEntities(modelName, 'Body', [thisBody], 'Face', faceGroup)
                bodyFaces = simlab.getEntityFromGroup(faceGroup)
                dupfaces = set(bodyFaces).intersection(set(entitiesShared))
                for thisFace in dupfaces:
                    internalFaces.add(thisFace)

        # internalFaces = list(internalFaces)

        
        bodiesToMerge.append(newBody[0])

        beadName = getUniqueBeadName(modelName)

        if bodiesToMerge:
            mergeBodies(modelName, bodiesToMerge, beadName)
            internalFaceGroup = 'Show_Internal_Faces'
            simlablib.DeleteGroups(internalFaceGroup)
            getInternalFaces(modelName, [beadName])
            intFaces = simlab.getEntityFromGroup(internalFaceGroup)
            for thisFace in intFaces:
                internalFaces.add(thisFace)

        internalFaces = list(internalFaces)
        if internalFaces:
            # #print('internalFaces:{}'.format(internalFaces))
            simlablib.DeleteEntities(modelName, 'Face', internalFaces)

        simlablib.DeleteGroups([self.threeBeadFaces])

        self.UpdateButtonFG3()
        simlab.redisplayEntity('Model', modelName)

    def UpdateButtonFG3(self):
        groups = [self.threeBeadFaces]
        widgets = [self.btnThreeBeadsFace]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)

    
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
        self.varRemesh.set(1)

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
                #print('opposite Direction')
                beadFaceNormal = -1 * beadFaceNormal
        
        #print('beadFaceNormal:{}'.format(beadFaceNormal))

        fromPt = refPt
        toPt = refPt + beadFaceNormal* 2

        dist = getDistanceBetweenFaceAndNode(modelName, limitFace, refNode)
        #print('distance:{}'.format(dist))

        beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        extendToLimitFace(modelName, endFace, limitFace, list(fromPt), list(toPt), list(beadFaceNormal), max(int(round(dist/beadElemSize)), 1))
        afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
        extrudedBody = list(set(afterBodies) - set(beforeBodies))
        if not extrudedBody:
            messagebox.showinfo('情報','Extrudeのエーラが発生しました。')
            return
        
        simlablib.DeleteSolidElements(modelName, extrudedBody)

        # print('extrudedBody:{}'.format(extrudedBody))

        adjBodyGroup = 'Adjacent_Bodies'
        simlablib.DeleteGroups(adjBodyGroup)
        searchAdjacentBodies(modelName, extrudedBody[0], tol=1e-1)
        adjBodies = simlab.getBodiesFromGroup(adjBodyGroup)
        sharedFaceGroup = 'Shared Faces'
        simlablib.DeleteGroups(sharedFaceGroup)
        for thisBody in adjBodies:
            if thisBody in stopBody:                
                joinOverlapFaces(modelName, extrudedBody[0], thisBody, tol=0.1)

                SharedEntities=''' <SharedEntities UUID="2dc7ae98-62c3-4926-bbde-d08da48208ad" CheckBox="ON">
                <tag Value="-1"/>
                <Name Value="SharedEntities1"/>
                <SupportEntities>
                <Entities>
                <Model>'''+ modelName +'''</Model>
                <Body>"'''+ extrudedBody[0] +'''","'''+ thisBody +'''",</Body>
                </Entities>
                </SupportEntities>
                <Faces Value="1"/>
                <Edges Value="0"/>
                <Vertices Value="0"/>
                </SharedEntities>'''
                simlab.execute(SharedEntities)

                sharedFaces = simlab.getEntityFromGroup(sharedFaceGroup)

                if sharedFaces:
                    simlablib.DeleteEntities(modelName, 'Face', sharedFaces)
            else:
                joinOverlapFaces(modelName, extrudedBody[0], thisBody, tol=0.1)
        
        simlablib.MergeBodies(modelName, list(beadBody)+ list(extrudedBody))
        
        if bodyMergeChecked:
            simlablib.MergeBodies(modelName, list(beadBody)+ list(stopBody))
        
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
        self.iconBeadCorner= ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'beadCorner.png')), master=self.frmFig2)
        tk.Label(self.frmFig2, image=self.iconBeadCorner).pack(side=tk.LEFT, anchor=tk.W)

        self.btnBeadCornerFace = tk.Button(self.frmFig2, text='ビード面', command= self.SelectBeadFace, width=10)
        self.btnBeadCornerFace.place(x=80, y=40)

        self.btnCornerNode = tk.Button(self.frmFig2, text='ノード', command = self.SelectCornerNode, width=7)
        self.btnCornerNode.place(x=190, y=185)

        self.btnGround = tk.Button(self.frmFig2, text='地面', command=self.SelectGroundFace, width=10)
        self.btnGround.place(x=80, y=220)

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
    
    def SelectBeadFace(self):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
               
        groupName = self.beadCornerFace
        simlablib.DeleteGroups(groupName)
        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, groupName)

        self.UpdateButtonFG2()
        
    def SelectCornerNode(self):
        node = simlab.getSelectedEntities('NODE')
        if len(node) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        groupName = self.cornerNode
        simlablib.DeleteGroups(groupName)
        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Node', node, groupName)
        self.UpdateButtonFG2()
    
    def ExecuteCorner(self):
        beadFace = simlab.getEntityFromGroup(self.beadCornerFace)
        if not beadFace:
            messagebox.showinfo('情報','ビード面を選択してください。')
            return

        cornerNode = simlab.getEntityFromGroup(self.cornerNode)
        if not cornerNode:
            messagebox.showinfo('情報','コーナーノードを選択してください。')
            return

        groundFace = simlab.getEntityFromGroup(self.groundFace)
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

        cornerPt = np.array(simlab.getNodePositionFromNodeID(modelName, cornerNode[0]))

        nodeGroup = 'nodeGroup'
        edgeGroup = 'edgeGroup'
        edgesOnGround = set()

        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', groundFace, 'Edge', edgeGroup)
        groundEdges = simlab.getEntityFromGroup(edgeGroup)

        for thisFace in list(beadFace):
            simlablib.DeleteGroups(edgeGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Face', [thisFace], 'Edge', edgeGroup)
            faceEdges = simlab.getEntityFromGroup(edgeGroup)
            
            intersectingEdges = set(faceEdges).intersection(set(groundEdges))
            for thisEdge in intersectingEdges:
                edgesOnGround.add(thisEdge)

        edgesOnGround = list(edgesOnGround)
        # if len(edgesOnGround) < 2:
        #     messagebox.showinfo('情報','地面のビードエッジを分けてください')
        #     return
        edgesOnGroundGroupName = 'edgesOnGround'
        simlablib.DeleteGroups(edgesOnGroundGroupName)
        simlablib.CreateGroup(modelName, 'Edge', edgesOnGround, edgesOnGroundGroupName)
        #print(edgesOnGround)

        vertexGroup = 'vertexGroup'

        simlablib.DeleteGroups(vertexGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Edge', edgesOnGround, 'Vertex', vertexGroup)
        edgeVertexes = simlab.getEntityFromGroup(vertexGroup)

        vertexDict = dict()

        for thisV in edgeVertexes:
            thisV_pt = simlab.getVertexPositionFromVertexID(modelName, thisV)
            dist = np.linalg.norm(thisV_pt - cornerPt)
            vertexDict[thisV] = dist
        

        sortedVertexList = sorted(vertexDict, key=vertexDict.get)

        vert1 = sortedVertexList[-1]
        simlablib.DeleteGroups(nodeGroup)
        vert1Node = getVertexNode(modelName, vert1, nodeGroup)
        vert1Pt = np.array(simlab.getVertexPositionFromVertexID(modelName, vert1))

        vert2 = sortedVertexList[-2]
        simlablib.DeleteGroups(nodeGroup)
        vert2Node = getVertexNode(modelName, vert2, nodeGroup)
        vert2Pt = np.array(simlab.getVertexPositionFromVertexID(modelName, vert2))

        v1 = vert1Pt - cornerPt
        n1 = v1 / np.linalg.norm(v1)

        v2 = vert2Pt - cornerPt
        n2 = v2 / np.linalg.norm(v2)

        n3 = (n1+n2)/np.linalg.norm(n1+n2)

        pt1 = cornerPt + n1 * arcR
        pt2 = cornerPt + n2 * arcR
        pt0 = pt1 + n2 * arcR

        pt3 = pt0 - n3 * arcR

        nodeNum1 = simlab.getNextNodeID(modelName)
        createNodeByCoordinate(modelName, list(pt1), nodeNum1)
        nodeNum2 = simlab.getNextNodeID(modelName)
        createNodeByCoordinate(modelName, list(pt2), nodeNum2)

        nodeNum3 = simlab.getNextNodeID(modelName)
        createNodeByCoordinate(modelName, list(pt3), nodeNum3)

        edgesOnGround = simlab.getEntityFromGroup(edgesOnGroundGroupName)
        edge1 = getClosestEdgeFromXYZ(modelName, edgesOnGround, list(pt1))
        splitEdgeByNodes(modelName, edge1, [nodeNum1])

        edgesOnGround = simlab.getEntityFromGroup(edgesOnGroundGroupName)
        edge2 = getClosestEdgeFromXYZ(modelName, edgesOnGround, list(pt2))
        splitEdgeByNodes(modelName, edge2, [nodeNum2])


        edgesOnGround = simlab.getEntityFromGroup(edgesOnGroundGroupName)
        edgesToAlign = []
        for thisEdge in edgesOnGround:
            simlablib.DeleteGroups(nodeGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Edge', [thisEdge], 'Node', nodeGroup)
            edgeNodes = simlab.getEntityFromGroup(nodeGroup)
            if vert1Node[0] in edgeNodes or vert2Node[0] in edgeNodes:
                continue
            edgesToAlign.append(thisEdge)
        
        #print('edgesToAlign:{}'.format(edgesToAlign))

        radius = getRadiusOfCircle([pt1, pt2, pt3])
        radius = int(radius*10000)/10000
        #print('radius:{}'.format(radius))
        circleNodes = [nodeNum1, nodeNum3, nodeNum2]
        alignCircle(modelName, edgesToAlign, circleNodes, radius)

        try:
            aspectRatio = float(self.config.Get('Aspect_Ratio'))
        except ValueError:
            aspectRatio = 10
        remeshFace(modelName, beadFace, beadElemSize, aspectRatio, preserveEdge=0)

        allNodeGroups = simlab.getGroupsWithSubString('NodeGroup',['*'])
        if allNodeGroups:
            simlablib.DeleteGroups(allNodeGroups)
        simlablib.DeleteAllOphanNodes()
        simlablib.DeleteGroups([self.beadCornerFace, self.cornerNode, self.groundFace])
        self.UpdateButtonFG2()
       
    
    def UpdateButtonFG2(self):
        groups = [self.beadCornerFace, self.groundFace, self.cornerNode]
        widgets = [self.btnBeadCornerFace, self.btnGround, self.btnCornerNode]

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

def getClosestEdgeFromXYZ(modelName, edges, coord):
    edgeDict = dict()
    for thisEdge in edges:
        minDistance = 1e6
        minNode = None
        nodeGroup = 'nodeGroup'
        simlablib.DeleteGroups(nodeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Edge', [thisEdge], 'Node', nodeGroup)
        edgeNodes = simlab.getEntityFromGroup(nodeGroup)
        for thisNode in edgeNodes:
            pt = np.array(simlab.getNodePositionFromNodeID(modelName, thisNode))
            dist = np.linalg.norm(pt- coord)
            if minDistance > dist:
                minDistance = dist
                minNode = thisNode
        
        edgeDict[thisEdge] = minDistance
    sortedDict = sorted(edgeDict, key=edgeDict.get)
    return sortedDict[0]

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