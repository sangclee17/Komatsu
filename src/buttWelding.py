# coding: shift-jis
import tkinter as tk
import tkinter.messagebox as messagebox
import os, sys
from PIL import Image, ImageTk
from filletWelding import getEdgeNodes
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

class ButtWeldingDialog(basedialog.BaseDialog):
    def __init__(self, master, parent, config, backup):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('突合せ溶接')
        self.master.resizable(width=False, height=False)
        self.master.attributes('-topmost', True)
        self.master.protocol('WM_DELETE_WINDOW', self.CloseDialog)
        self.config = config
        self.backup = backup

        self.refFace1 = 'ButtWeldingRefFace1'
        self.refFace2 = 'ButtWeldingRefFace2'
        self.bottomEdge = 'ButtWeldingBottomEdge'

        self.limitDistance = 1e-1

        self.CreateWidgets()

        groups = [self.refFace1, self.refFace2, self.bottomEdge]
        simlablib.DeleteGroups(groups)

        self.UpdateButtonFG()
        simlabutil.ClearSelection()

        simlab.setSelectionFilter('Face')
    
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)
        tk.Label(self.frmTop, text='対象面１と対象面２からそれぞれの下端エッジを選択してください。').pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmTop, text='裏当て面は自動検索され、作成されたビードと節点共有します。').pack(side=tk.TOP, anchor=tk.NW)
        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmFig = tk.Frame(self.frmTop)        
        self.frmFig.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        self.frmButtWelding = tk.Frame(self.frmFig, width=400)
        self.frmButtWelding.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconButtWelding= ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'buttWelding.png')), master=self.frmButtWelding)
        tk.Label(self.frmButtWelding, image=self.iconButtWelding).pack(side=tk.LEFT, anchor=tk.W)

        self.btnRefFace1 = tk.Button(self.frmButtWelding, text='対象面１', command=lambda: self.SelectRefFace(1), width=10)
        self.btnRefFace1.place(x=35, y=98)

        self.btnRefFace2 = tk.Button(self.frmButtWelding, text='対象面２', command=lambda: self.SelectRefFace(2), width=10)
        self.btnRefFace2.place(x=280, y=60)

        self.btnBottomEdge = tk.Button(self.frmButtWelding, text='エッジ', command=self.SelectBottomEdges, width=10)
        self.btnBottomEdge.place(x=220, y=200)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmBeadInfo = tk.Frame(self.frmTop)
        self.frmBeadInfo.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)

        self.frmBeadLayer = tk.Frame(self.frmBeadInfo)
        self.frmBeadLayer.pack(side=tk.TOP, anchor=tk.NW)

        tk.Label(self.frmBeadLayer, text='ビード要素サイズ: ').pack(side=tk.LEFT, anchor=tk.NW)
        self.entBeadElemSize = tk.Entry(self.frmBeadLayer, width=7)
        self.entBeadElemSize.pack(side=tk.LEFT, anchor=tk.NW)
        beadElemSize = self.config.Get('Bead_Elem_Size')
        self.entBeadElemSize.insert(tk.END, beadElemSize)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)

        self.btnWeld = tk.Button(self.frmCtrl, text=' 作成 ', compound=tk.LEFT, command = self.StartWelding, width=10)
        self.btnWeld.pack(side=tk.LEFT, anchor=tk.NW)        

        self.btnUndo = tk.Button(self.frmCtrl, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=10)
        self.btnUndo.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo)

        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=10)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)
    
    def SelectRefFace(self, num):
        face = simlab.getSelectedEntities('FACE')
        if len(face) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押してください。')
            return
        
        faceGroupName = None
        if num == 1:
            faceGroupName = self.refFace1
        elif num == 2:
            faceGroupName = self.refFace2

        simlablib.DeleteGroups(faceGroupName)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', face, faceGroupName)

        self.UpdateButtonFG()

    def SelectBottomEdges(self):
        edgesRegistered = set(simlab.getEntityFromGroup(self.bottomEdge))

        edge = simlab.getSelectedEntities('EDGE')
        if len(edge) == 0:
            messagebox.showinfo('情報','エッジを選択した後、ボタンを押してください。')
            return        

        for thisEdge in edge:
            edgesRegistered.add(thisEdge)

        edgesToRegistered = list(edgesRegistered)
        if edgesToRegistered:
            simlablib.DeleteGroups(self.bottomEdge)
            modelName = simlab.getModelName('FEM')
            simlablib.CreateGroup(modelName, 'Edge', edgesToRegistered, self.bottomEdge)

        self.UpdateButtonFG()

    def StartWelding(self):
        beadElemSize = self.entBeadElemSize.get()
        try:
            beadElemSize = float(beadElemSize)
        except ValueError:
            messagebox.showinfo('情報','要素サイズで数字を入力してください。')
            return
        else:
            if beadElemSize <= 0:
                messagebox.showinfo('情報','要素サイズで０より大きい数字を入力してください。')
                return
        face1 = list(simlab.getEntityFromGroup(self.refFace1))
        face2 = list(simlab.getEntityFromGroup(self.refFace2))
        if not face1 or not face2:
            messagebox.showinfo('情報','対象面を選んで登録してください。')
            return
        
        bottomEdges = simlab.getEntityFromGroup(self.bottomEdge)
        if len(bottomEdges) == 0:
            messagebox.showinfo('情報','対象面１と対象面２からそれぞれの下端エッジを選択してください。')
            return
        
        allModelNames = simlab.getAllRootModelNames('FEM')
        if len(allModelNames) > 1:
            messagebox.showinfo('情報','モデル名が複数あります。マージして一個にしてください。')
            return
        elif len(allModelNames) == 0:
            messagebox.showinfo('情報','FEモデルを作成してください。')
            return

        modelName = simlab.getModelName('FEM')

        try:
            aspectRatio = float(self.config.Get('Aspect_Ratio'))
        except ValueError:
            aspectRatio = 10

        self.backup.Save('ButtWelding')

        edgeGroup = 'edgeGroup'
        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', face1, 'Edge', edgeGroup)
        face1Edges = simlab.getEntityFromGroup(edgeGroup)

        bottomEdges1 = list(set(face1Edges).intersection(set(bottomEdges)))
        if not bottomEdges1:
            messagebox.showinfo('情報','対象面１から下端エッジを選択してください。')
            return
        #print('bottomEdges1:{}'.format(bottomEdges1))
        bottomEdge1Vertexes = getEdgeVertexes(modelName, bottomEdges1)
        #print('bottomEdge1Vertexes:{}'.format(bottomEdge1Vertexes))
        bottomEdge1EndVertexes = getStartAndEndEdgeVertexes(modelName, bottomEdges1, bottomEdge1Vertexes)
        #print('bottomEdge1EndVertexes:{}'.format(bottomEdge1EndVertexes))
        bottomEdge1Endnodes = []
        for thisV in bottomEdge1EndVertexes:
            nodeGroup = 'nodeGroup'
            simlablib.DeleteGroups(nodeGroup)
            vNode = getVertexNode(modelName, thisV, nodeGroup)
            if vNode:
                bottomEdge1Endnodes.append(vNode[0])
        
        #print('bottomEdge1Endnodes:{}'.format(bottomEdge1Endnodes))

        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', face2, 'Edge', edgeGroup)
        face2Edges = simlab.getEntityFromGroup(edgeGroup)

        bottomEdges2 = list(set(face2Edges).intersection(set(bottomEdges)))
        #print('bottomEdges2:{}'.format(bottomEdges2))
        if not bottomEdges2:
            messagebox.showinfo('情報','対象面２から下端エッジを選択してください。')
            return
        
        bottomEdge2Vertexes = getEdgeVertexes(modelName, bottomEdges2)
        #print('bottomEdge2Vertexes:{}'.format(bottomEdge2Vertexes))
        bottomEdge2EndVertexes = getStartAndEndEdgeVertexes(modelName, bottomEdges2, bottomEdge2Vertexes)
        #print('bottomEdge2EndVertexes:{}'.format(bottomEdge2EndVertexes))
        bottomEdge2Endnodes = []
        for thisV in bottomEdge2EndVertexes:
            nodeGroup = 'nodeGroup'
            simlablib.DeleteGroups(nodeGroup)
            vNode = getVertexNode(modelName, thisV, nodeGroup)
            if vNode:
                bottomEdge2Endnodes.append(vNode[0])
        #print('bottomEdge2Endnodes:{}'.format(bottomEdge2Endnodes))

        bottomEdge1Nodes = getEdgeNodes(modelName, bottomEdges1)
        refBottomNode1 = bottomEdge1Nodes[0]
        #print('refBottomNode1:{}'.format(refBottomNode1))
        mindisNode, minDistBottom = getClosestEdgeNodeAndDistanceFrom(modelName, bottomEdges2, refBottomNode1)

        #print('mindisNode:{}'.format(mindisNode))
        #print('minDistBottom:{}'.format(minDistBottom))
        bodiesToMerge = []
        boidesConnectingBottomEdges = []
        if minDistBottom <= self.limitDistance:
            ImprintEdgesonEdges=''' <ImprintEdgeOnEdge UUID="08d266da-5c20-4892-935f-058c7e9f6739" pixmap="imprintedgeonedge">
            <tag Value="-1"/>
            <InputEdges>
            <Entities>
            <Model>'''+ modelName +'''</Model>
            <Edge>'''+ str(bottomEdges1).strip('()''[]') +''',</Edge>
            </Entities>
            </InputEdges>
            <TargetEdges>
            <Entities>
            <Model>'''+ modelName +'''</Model>
            <Edge>'''+ str(bottomEdges2).strip('()''[]') +''',</Edge>
            </Entities>
            </TargetEdges>
            <Tolerance Value="'''+ str(self.limitDistance) +'''"/>
            </ImprintEdgeOnEdge>'''
            simlab.execute(ImprintEdgesonEdges)
        else:
            beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            createFaceFromEdges(modelName, bottomEdges1, bottomEdges2, max(int(round(minDistBottom/beadElemSize)), 2))
            afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            newBody = list(set(afterBodies) - set(beforeBodies))
            for thisBody in newBody:
                bodiesToMerge.append(thisBody)
                boidesConnectingBottomEdges.append(thisBody)

        # merge faces if more than one
        if len(face1) > 1:
            face1 = list(simlab.getEntityFromGroup(self.refFace1))
            simlablib.MergeFaces(modelName, face1)
            face1 = list(simlab.getEntityFromGroup(self.refFace1))
        
        if len(face2) > 1:
            face2 = list(simlab.getEntityFromGroup(self.refFace2))
            simlablib.MergeFaces(modelName, face2)
            face2 = list(simlab.getEntityFromGroup(self.refFace2))
        
        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', face1, 'Edge', edgeGroup)
        face1Edges = simlab.getEntityFromGroup(edgeGroup)

        simlablib.DeleteGroups(edgeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', face2, 'Edge', edgeGroup)
        face2Edges = simlab.getEntityFromGroup(edgeGroup)

        nodeGroup = 'nodeGroup'
        
        intersectingEdgesBetweenFace12 = []
        if boidesConnectingBottomEdges:
            simlablib.DeleteGroups(edgeGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Body', boidesConnectingBottomEdges, 'Edge', edgeGroup)
            newEdges = simlab.getEntityFromGroup(edgeGroup)
            intersectingEdge1 = list(set(face1Edges).intersection(set(newEdges)))
            intersectingEdgesBetweenFace12.extend(intersectingEdge1)

            intersectingEdge2 = list(set(face2Edges).intersection(set(newEdges)))
            intersectingEdgesBetweenFace12.extend(intersectingEdge2)
        else:
            intersectingEdgesBetweenFace12 = list(set(face1Edges).intersection(set(face2Edges)))
        
        for thisFace in face1+face2:
            beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            createBodyFromFaces(modelName, thisFace)
            afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            newBody = list(set(afterBodies) - set(beforeBodies))
            for thisBody in newBody:
                bodiesToMerge.append(thisBody)
        
        #print('intersectingEdgesBetweenFace12:{}'.format(intersectingEdgesBetweenFace12))
        simlablib.UpdateModel()
        
        if bodiesToMerge:
            beadName = getUniqueBeadName(modelName)
            mergeBodies(modelName, bodiesToMerge, beadName)
        
        beadCreated = simlab.getBodiesWithSubString(modelName, [beadName])
        if not beadCreated:
            messagebox.showinfo('情報','ビード作成に失敗しました。')
            return
        
        sharedFaceGroup = 'Shared Faces'
        simlablib.DeleteGroups(sharedFaceGroup)
        sharedEntities(modelName, [beadName])
        entitiesShared = list(simlab.getEntityFromGroup(sharedFaceGroup))
        if entitiesShared:
            mcName = 'preserveEdgeMC'
            simlablib.DeleteMeshControl(mcName)
            preserveFaceEdgeMC(mcName, modelName, list(face1)+list(face2))
            remeshFace(modelName, entitiesShared, beadElemSize, aspectRatio, preserveBoundary=0)

        face1Edges = getFaceEdges(modelName, face1)
        face2Edges = getFaceEdges(modelName, face2)

        edges1ToFace = []
        edges2ToFace = []
        intersectingEdgeNodes = getEdgeNodes(modelName, intersectingEdgesBetweenFace12)
        
        for thisEdge in face1Edges:

            simlablib.DeleteGroups(nodeGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Edge', [thisEdge], 'Node', nodeGroup)
            nodeEdges = simlab.getEntityFromGroup(nodeGroup)
            intersectingNodes = list(set(nodeEdges).intersection(set(intersectingEdgeNodes)))
            if not intersectingNodes:
                edges1ToFace.append(thisEdge)
        
        for thisEdge in face2Edges:
            simlablib.DeleteGroups(nodeGroup)
            simlablib.SelectAssociatedEntities(modelName, 'Edge', [thisEdge], 'Node', nodeGroup)
            nodeEdges = simlab.getEntityFromGroup(nodeGroup)
            intersectingNodes = list(set(nodeEdges).intersection(set(intersectingEdgeNodes)))
            if not intersectingNodes:
                edges2ToFace.append(thisEdge)


        #print('edges1ToFace:{}'.format(edges1ToFace))
        #print('edges2ToFace:{}'.format(edges2ToFace))


        upperEdge1Nodes = getEdgeNodes(modelName, edges1ToFace)
        refUpperNode1 = upperEdge1Nodes[0]
        #print('refUpperNode1:{}'.format(refUpperNode1))
        #print('edges2ToFace:{}'.format(edges2ToFace))
        mindisNode, minDistUpper = getClosestEdgeNodeAndDistanceFrom(modelName, edges2ToFace, refUpperNode1)
        #print('minDistUpper:{}'.format(minDistUpper))

        if minDistUpper <= self.limitDistance:
            ImprintEdgesonEdges=''' <ImprintEdgeOnEdge UUID="08d266da-5c20-4892-935f-058c7e9f6739" pixmap="imprintedgeonedge">
            <tag Value="-1"/>
            <InputEdges>
            <Entities>
            <Model>'''+ modelName +'''</Model>
            <Edge>'''+ str(edges1ToFace).strip('()''[]') +''',</Edge>
            </Entities>
            </InputEdges>
            <TargetEdges>
            <Entities>
            <Model>'''+ modelName +'''</Model>
            <Edge>'''+ str(edges2ToFace).strip('()''[]') +''',</Edge>
            </Entities>
            </TargetEdges>
            <Tolerance Value="'''+ str(self.limitDistance) +'''"/>
            </ImprintEdgeOnEdge>'''
            simlab.execute(ImprintEdgesonEdges)
        else:
            beforeBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            createFaceFromEdges(modelName, edges1ToFace, edges2ToFace, max(int(round(minDistUpper/beadElemSize)), 2))
            afterBodies = simlab.getBodiesWithSubString(modelName, ['*'])
            newBody = list(set(afterBodies) - set(beforeBodies))
            for thisBody in newBody:
                bodiesToMerge.append(thisBody)

        #print('bodiesToMerge:{}'.format(bodiesToMerge))
        
        fillFreeEdgesOfBody(modelName, beadName)

        bodyGroup = 'bodyGroup'
        simlablib.DeleteGroups(bodyGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Face', list(face1)+list(face2), 'Body', bodyGroup)
        bodiesFromRefFaces = simlab.getBodiesFromGroup(bodyGroup)
        
        bodyGroup = 'Adjacent_Bodies'
        simlablib.DeleteGroups(bodyGroup)
        searchAdjacentBodies(modelName, beadName, tol=1e-1)
        adjBodies = simlab.getBodiesFromGroup(bodyGroup)

        adjBodies = list((set(adjBodies) - set(bodiesFromRefFaces))-set([beadName]))
        #print('adjBodies:{}'.format(adjBodies))
        facesToRemesh= []
        for thisBody in adjBodies:
   
            joinOnOvelappingFaces(modelName, beadName, thisBody)
            sharedFaceGroup = 'Shared Faces'
            simlablib.DeleteGroups(sharedFaceGroup)
            sharedEntities(modelName, [beadName,thisBody])
            sharedFaces = list(simlab.getEntityFromGroup(sharedFaceGroup))
            if sharedFaces:
                facesToRemesh.extend(sharedFaces)
        if facesToRemesh:
            remeshFace(modelName, facesToRemesh, beadElemSize, aspectRatio, preserveBoundary=0)

        meshQualityCleanup(modelName, beadName, aspectRatio)
        simlab.redisplayEntity('Model', modelName)
        
        groups = [self.refFace1, self.refFace2, self.bottomEdge]
        simlablib.DeleteGroups(groups)
        self.UpdateButtonFG()

    def Undo(self):
        self.backup.Load()
        self.UpdateButtonFG()

        modelName = simlab.getModelName('CAD')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')

    def UpdateButtonFG(self):
        groups = [self.refFace1, self.refFace2, self.bottomEdge]
        widgets = [self.btnRefFace1, self.btnRefFace2, self.btnBottomEdge]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)
    
    def CloseDialog(self):
        super().CloseDialog()

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
    # print(MergeBodies)

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

def getFarthestEdgeFromPlane(modelName, faceEdges, n, d):
    tempDict = dict()
    vertexPositionDict, edgeVeretexDict = getFaceVertexesAndPosition(modelName, faceEdges)

    for thisEdge in edgeVeretexDict:
        vertexes = edgeVeretexDict[thisEdge]

        allDist = [] 

        for thisV in vertexes:
            dist = abs(np.dot(n, vertexPositionDict[thisV]) - d)
            allDist.append(dist)
        
        avgDist = sum(allDist)/ len(allDist)

        tempDict[thisEdge] = avgDist
    
    sortedDict = sorted(tempDict, key=tempDict.get)
    return sortedDict[-1]
    
def getFaceVertexesAndPosition(modelName, faceEdges):
    vertexGroup = 'vertexGroup'
    verDict = dict()
    edgeDict = dict()

    for thisEdge in faceEdges:
        simlablib.DeleteGroups(vertexGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Edge', [thisEdge], 'Vertex', vertexGroup)
        thisEdgeVertexes = simlab.getEntityFromGroup(vertexGroup)
        for thisVertex in thisEdgeVertexes:
            v_pt = np.array(simlab.getVertexPositionFromVertexID(modelName, thisVertex))
            verDict[thisVertex] = v_pt

        edgeDict[thisEdge] = thisEdgeVertexes

    return verDict, edgeDict

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

def getNormalFromThreePts(pts):

    p1,p2,p3 = pts
    p1 = np.array(p1)
    p2 = np.array(p2)
    p3 = np.array(p3)

    v1 = (p2 - p1) / np.linalg.norm(p2 - p1)
    v2 = (p3 - p1) / np.linalg.norm(p3 - p1)
    cp = np.cross(v1,v2)

    return cp / np.linalg.norm(cp)

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

def joinOnOvelappingFaces(modelName, bodyToBeKept, bodyToBeModiFied, tol= 0.1, remesh=0):
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
    <LocalRemesh Value="'''+ str(remesh) +'''"/>
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

def createFaceFromEdges(modelName, edges1, edges2, numLayers):
    CreateFaceFromEdges=''' <FaceUsing2Edges UUID="DDB1E50D-DB65-424c-8E3A-516DD1A7E058" gda="">
    <Name Value=""/>
    <tag Value="-1"/>
    <No.OfLayers Value="'''+ str(numLayers) +'''"/>
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

def getClosestEdgeNodeAndDistanceFrom(modelName, refEdge, fromNode):
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
    
    return minDistanceNode, minDistance

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