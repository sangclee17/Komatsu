# coding: shift-jis
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import os, sys, importlib
from PIL import Image, ImageTk
import numpy as np
from hwx import simlab
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

class SplitCircumferenceDialog(basedialog.BaseDialog):
    def __init__(self, master, parent, config):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('円周分割')
        self.master.resizable(width=False, height=False)
        self.master.attributes('-topmost', True)
        self.master.protocol('WM_DELETE_WINDOW', self.CloseDialog)
        self.config = config

        self.circumEdge = 'CircumferenceEdge'
        self.refNode = 'RefNode'
        
        simlabutil.ClearSelection()
        simlab.setSelectionFilter('Edge')
        self.CreateWidgets()
    
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        tk.Label(self.frmTop, text='円周エッジと基準ノードを選択してください。').pack(side=tk.TOP, anchor=tk.CENTER)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmFig = tk.Frame(self.frmTop)        
        self.frmFig.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
        self.frmSplitCircum = tk.Frame(self.frmFig, width=400)
        self.frmSplitCircum.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconSplitCircum = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'splitCircumference.png')), master=self.frmSplitCircum)
        tk.Label(self.frmSplitCircum, image=self.iconSplitCircum).pack(side=tk.LEFT, anchor=tk.W)

        self.btnCircumEdge = tk.Button(self.frmSplitCircum, text='円周エッジ', command=self.SelectCircumference, width=10)
        self.btnCircumEdge.place(x=95, y=95)

        self.btnRefNode = tk.Button(self.frmSplitCircum, text='基準ノード', command=self.SelectReferenceNode, width=10)
        self.btnRefNode.place(x=170, y=210)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmSplitAngle = tk.Frame(self.frmTop)
        self.frmSplitAngle.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)
        tk.Label(self.frmSplitAngle, text='分割角度 :').pack(side=tk.LEFT, anchor=tk.NW)

        self.entSplitAngle = tk.Entry(self.frmSplitAngle, width=7)
        self.entSplitAngle.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entSplitAngle.insert(tk.END, 45)
        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)

        self.btnWeld = tk.Button(self.frmCtrl, text=' 実行 ', compound=tk.LEFT, command=self.SplitCircumference, width=10)
        self.btnWeld.pack(side=tk.LEFT, anchor=tk.NW)

        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=10)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)
    
    def SelectCircumference(self):
        edge = simlab.getSelectedEntities('EDGE')
        
        if len(edge) == 0:
            messagebox.showinfo('情報','エッジを選択した後、ボタンを押してください。')
            return
 
        simlablib.DeleteGroups(self.circumEdge)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Edge', edge, self.circumEdge)

        self.UpdateButtonFG()

    def SelectReferenceNode(self):
        node = simlab.getSelectedEntities('NODE')

        if len(node) == 0:
            messagebox.showinfo('情報','ノードを選択した後、ボタンを押してください。')
            return
        
        if len(node) > 1:
            messagebox.showinfo('情報','ノード一つを選択してください。')
            return
 
        simlablib.DeleteGroups(self.refNode)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Node', node, self.refNode)

        self.UpdateButtonFG()
    
    def SplitCircumference(self):
        splitAngle = self.entSplitAngle.get()
        if len(splitAngle) == 0:
            messagebox.showinfo('情報','分割角度を入力してください。')
            return
        try:
            splitAngle = float(splitAngle)
        except ValueError:
            messagebox.showinfo('情報','分割角度で数字を入力してください。')
            return
        else:
            if splitAngle <= 0:
                messagebox.showinfo('情報','分割角度で０より大きい数字を入力してください。')
                return
        
        circumEdge = simlab.getEntityFromGroup(self.circumEdge)
        if not circumEdge:
            messagebox.showinfo('情報','円周エッジを選択してください。')
            return
        
        refNode = simlab.getEntityFromGroup(self.refNode)
        if not refNode:
            messagebox.showinfo('情報','基準ノードを選択してください。')
            return
        
        
        allModelNames = simlab.getAllRootModelNames('FEM')
        if len(allModelNames) > 1:
            messagebox.showinfo('情報','モデル名が複数あります。マージして一個にしてください。')
            return
        elif len(allModelNames) == 0:
            messagebox.showinfo('情報','FEモデルを作成してください。')
            return
        
        simlablib.UpdateModel()

        modelName = simlab.getModelName('FEM')

        bodyGroup = 'bodyGroup'
        simlablib.DeleteGroups(bodyGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Node', refNode, 'Body', bodyGroup)
        refBody = simlab.getBodiesFromGroup(bodyGroup)

        
        nodeGroup = 'nodeGroup'
        simlablib.DeleteGroups(nodeGroup)
        simlablib.SelectAssociatedEntities(modelName, 'Edge', circumEdge, 'Node', nodeGroup)
        circumeEdgeNodes = simlab.getEntityFromGroup(nodeGroup)

        if len(circumeEdgeNodes) < 3:
            messagebox.showinfo('情報','円周エッジのノードが３以下です。')
            return
        
        circleNodes = circumeEdgeNodes[:3]

        circlePts = []
        for thisNode in circleNodes:
            nodePt = np.array(simlab.getNodePositionFromNodeID(modelName, thisNode))
            circlePts.append(nodePt)
        
        #print('circlePts:{}'.format(circlePts))

        circleInfo = getCircleInfoFromThreePoints(circlePts)
        if not circleInfo:
            messagebox.showinfo('情報','円の中心を取れません。')
            return
        cPt, n, rad = circleInfo
        refNodePt = np.array(simlab.getNodePositionFromNodeID(modelName, refNode[0]))

        v1 = refNodePt - cPt
        n1 = v1 / np.linalg.norm(v1)

        v2 = np.cross(v1, n)
        n2 = v2 / np.linalg.norm(v2)

        splitNums = int(360 / splitAngle)

        t = np.linspace(0, 2 * math.pi, splitNums + 1)

        traj = []
        for ti in t :
            traj_i = cPt + rad * (math.cos(ti) * n1 + math.sin(ti) * n2)
            traj.append(traj_i)
        
        # print('traj:{}'.format(traj))
        # return
        splitNodes = []
        for thisCoord in traj[:-1]:
            nodeId = simlab.getNextNodeID(modelName)
            createNodeByCoordinate(modelName, list(thisCoord), nodeId)
            splitNodes.append(nodeId)

        if splitNodes:        
            splitEdgeByNodes(modelName, circumEdge, splitNodes)        
        
            # centerNode = getNodeOnCoordinate(modelName, refBody, list(cPt), incrementBy=0.2)

            # faceGroup = 'faceGroup'
            # simlablib.DeleteGroups(faceGroup)
            # simlablib.SelectAssociatedEntities(modelName, 'Node', centerNode, 'Face', faceGroup)

            # faceInside = simlab.getEntityFromGroup(faceGroup)

            # print('faceInside:{}'.format(faceInside))

            # try:
            #     aspectRatio = float(self.config.Get('Aspect_Ratio'))
            # except ValueError:
            #     aspectRatio = 10
            
            # if not faceInside:
            #     messagebox.showinfo('情報', '内側の面が見つかりません。')
            #     return

            # meshQualityCleanupOnFace(modelName, faceInside, aspectRatio)

            allNodeGroups = simlab.getGroupsWithSubString('NodeGroup',['*'])
            simlablib.DeleteGroups(allNodeGroups)
            simlablib.DeleteAllOphanNodes()

            splitEdges = simlab.getEntityFromGroup(self.circumEdge)
            vertexGroup = 'vertexGroup'
            if len(splitEdges) > splitNums:
                vertDistDict = dict()
                for thisEdge in splitEdges:
                    simlablib.DeleteGroups(vertexGroup)
                    simlablib.SelectAssociatedEntities(modelName, 'Edge', [thisEdge], 'Vertex', vertexGroup)
                    edgeVertexes = simlab.getEntityFromGroup(vertexGroup)
                    if len(edgeVertexes) == 2:
                        vPt1 = np.array(simlab.getVertexPositionFromVertexID(modelName, edgeVertexes[0]))
                        vPt2 = np.array(simlab.getVertexPositionFromVertexID(modelName, edgeVertexes[1]))

                        dist = np.linalg.norm(vPt2 - vPt1)
                        vertDistDict[thisEdge] = dist
                #print('vertDistDict:{}'.format(vertDistDict))

                # edgesToMerge = []
                sortedSplitEdges = sorted(vertDistDict, key=vertDistDict.get)
                #print('sortedSplitEdges:{}'.format(sortedSplitEdges))
                edgesToMerge= sortedSplitEdges[:2]


                # splitLength = rad * np.radians(splitAngle)
                # print('splitLength:{}'.format(splitLength))

                # edgesToMerge = []
                # for key in vertDistDict:
                #     vertDist = vertDistDict[key]
                #     if abs(splitLength - vertDist) > 1:
                #         edgesToMerge.append(key)

                if len(edgesToMerge) > 1:
                    #print('edgesToMerge:{}'.format(edgesToMerge))
                    MergeEdges=''' <MergeEdge gda="" UUID="C9CBBE68-5593-453b-9C95-2B3F550906EA">
                    <SupportEntities>
                    <Entities>
                    <Model>'''+ modelName +'''</Model>
                    <Edge>'''+ str(edgesToMerge).strip('()''[]') +'''</Edge>
                    </Entities>
                    </SupportEntities>
                    </MergeEdge>'''
                    simlab.execute(MergeEdges)
                
        simlablib.DeleteGroups([self.circumEdge, self.refNode])
        self.UpdateButtonFG()

    def UpdateButtonFG(self):
        groups = [self.circumEdge, self.refNode]
        widgets = [self.btnCircumEdge, self.btnRefNode]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)

    def CloseDialog(self):
        simlablib.DeleteGroups([self.circumEdge, self.refNode])
        super().CloseDialog()

def getCircleInfoFromThreePoints(pts):
    n = getNormalFromThreePts(pts)
    if n is None:
        return ()

    p1,p2,p3 = pts
    
    v12 = p2 - p1
    v13 = p3 - p1

    A = np.array([n, v12, v13])
    B = np.array([np.dot(n,p1), np.dot(v12,((p1+p2)/2)), np.dot(v13,((p1+p3)/2))])
    B = B.reshape(len(B),1)
    X = (np.linalg.solve(A, B)).T

    cPt = np.array(X[0])
    v1 = p1 - cPt
    rad = np.linalg.norm(v1)
    
    return cPt, n, rad

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

def meshQualityCleanupOnFace(modelName, faces, aspectRatLimit):

    QualityCheck=''' <QCheck UUID="412da11b-2793-4c07-a058-e49f209f007d">
    <ElementType Value="Tri"/>
    <Option Value="Compute"/>
    <Quality LimitValue="'''+ str(aspectRatLimit) +'''" Condition="G Than Or Eq" Name="Aspect Ratio"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(faces).strip('()''[]') +'''</Face>
    </Entities>
    </SupportEntities>
    </QCheck>'''
    meshQuality = simlab.computeMeshQualities(QualityCheck)

    QualityCheck=''' <QCheck UUID="412da11b-2793-4c07-a058-e49f209f007d">
    <ElementType Value="Tri"/>
    <Option Value="Cleanup"/>
    <Quality LimitValue="'''+ str(aspectRatLimit) +'''" Condition="G Than Or Eq" Name="Aspect Ratio"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(faces).strip('()''[]') +'''</Face>
    </Entities>
    </SupportEntities>
    <CleanupType Value="Modify Element"/>
    <PreserveSurfaceSkew Value="55" Check="0"/>
    </QCheck>'''
    meshQuality = simlab.cleanupMeshQualities(QualityCheck)

    QualityCheck=''' <QCheck UUID="412da11b-2793-4c07-a058-e49f209f007d">
    <ElementType Value="Tri"/>
    <Option Value="Compute"/>
    <Quality LimitValue="'''+ str(aspectRatLimit) +'''" Condition="G Than Or Eq" Name="Aspect Ratio"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(faces).strip('()''[]') +'''</Face>
    </Entities>
    </SupportEntities>
    </QCheck>'''
    meshQuality = simlab.computeMeshQualities(QualityCheck)


    UpdateModel=''' <UpdateMTopology UUID="D1F56859-D6DB-4431-8699-7E3BE98DA530">
    <tag Value="-1"/>
    <ModelName Value="'''+ modelName +'''"/>
    </UpdateMTopology>'''
    simlab.execute(UpdateModel)

def getNodeOnCoordinate(modelName, body, coord, incrementBy):
    groupName = 'Show_Nodes'
    simlablib.DeleteGroups(groupName)
    nodeFound = False
    rad = 1
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