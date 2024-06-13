# coding: shift-jis
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import os, sys, importlib

from scipy.misc import face
from hwx import simlab

SRC_DIR = os.path.dirname(os.path.realpath(__file__))
IMAGE_DIR = (os.path.join(SRC_DIR, 'images'))
PROJECT_DIR = os.path.join(SRC_DIR, "..")
LOG_DIR = os.path.join(PROJECT_DIR, "log")

if not SRC_DIR in sys.path:
    sys.path.append(SRC_DIR)

import basedialog
import simlablib
import simlabutil

class SplitEdge(basedialog.BaseDialog):
    def __init__(self, master, parent, config):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('�G�b�W����')
        self.master.resizable(width=False, height=False)
        self.master.attributes('-topmost', True)
        self.master.protocol('WM_DELETE_WINDOW', self.CloseDialog)
        self.config = config

        self.CreateWidgets()
        simlabutil.ClearSelection()
        simlab.setSelectionFilter('Edge')
    
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        tk.Label(self.frmTop, text='SimLab����G�b�W��I��ŕ������@�����߂Ă��������B').pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmSplitType = tk.Frame(self.frmTop)
        self.frmSplitType.pack(side=tk.TOP, anchor=tk.CENTER)

        self.varSplitType = tk.IntVar()
        self.varSplitType.set(1)
        self.chkSplitType1 = tk.Radiobutton(self.frmSplitType, text='�m�[�h', variable=self.varSplitType, value=1)
        self.chkSplitType1.grid(row=0, column=0,sticky='w')

        self.chkSplitType2 = tk.Radiobutton(self.frmSplitType, text='�p�x�F�@', variable=self.varSplitType, value=2)
        self.chkSplitType2.grid(row=1, column=0, sticky='w')

        self.entAngle = tk.Entry(self.frmSplitType, width=7)
        self.entAngle.grid(row=1, column=1, sticky='w')
        self.entAngle.insert(tk.END, 45)

        self.chkSplitType3 = tk.Radiobutton(self.frmSplitType, text='���_', variable=self.varSplitType, value=3)
        self.chkSplitType3.grid(row=2, column=0,sticky='w')

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)

        self.btnExecute = tk.Button(self.frmCtrl, text=' ���s ', compound=tk.LEFT, command=self.SplitEdge, width=10)
        self.btnExecute.pack(side=tk.LEFT, anchor=tk.NW)        

        self.btnClose = tk.Button(self.frmCtrl, text=' ���� ', compound=tk.RIGHT, command=self.CloseDialog, width=10)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)
    
    def SplitEdge(self):
        checkedType = self.varSplitType.get()
        # print(checkedType)

        allModelNames = simlab.getAllRootModelNames('FEM')
        if len(allModelNames) > 1:
            messagebox.showinfo('���','���f��������������܂��B�}�[�W���Ĉ�ɂ��Ă��������B')
            return
        elif len(allModelNames) == 0:
            messagebox.showinfo('���','FE���f�����쐬���Ă��������B')
            return

        modelName = simlab.getModelName('FEM')

        edgeSelected = simlab.simlab.getSelectedEntities('Edge')
        if not edgeSelected:
            messagebox.showinfo('���','��������G�b�W��I�����Ă��������B')
            return

        if len(edgeSelected) != 1:
            messagebox.showinfo('���','�G�b�W���I�����Ă��������B')
            return
        
        

        if checkedType == 1:
            nodes = simlab.getSelectedEntities('NODE')
            if not nodes:
                messagebox.showinfo('���','SimLab��ʂ���m�[�h��I�����Ă��������B')
                return
            edgeGroup = 'splitEdgeGroup'
            simlablib.DeleteGroups(edgeGroup)
            simlablib.CreateGroup(modelName, 'Edge',  edgeSelected, edgeGroup)
            splitEdgeByNodes(modelName, edgeSelected, nodes)
        
        elif checkedType == 2:
            angle = self.entAngle.get()
            try:
                angle = float(angle)
            except (ValueError, TypeError):
                messagebox.showinfo('���','�p�x�Ő�������͂��Ă��������B')
                return
            else:
                if angle <= 0:
                    messagebox.showinfo('���', '�p�x��0���傫����������͂��Ă��������B')
                    return
            
            edgeGroup = 'splitEdgeGroup'
            simlablib.DeleteGroups(edgeGroup)
            simlablib.CreateGroup(modelName, 'Edge',  edgeSelected, edgeGroup)            
            splitEdgeByAngle(modelName, edgeSelected, angle)
        
        elif checkedType == 3:
            edgeGroup = 'splitEdgeGroup'
            simlablib.DeleteGroups(edgeGroup)
            simlablib.CreateGroup(modelName, 'Edge',  edgeSelected, edgeGroup)  
            splitEdgeAtMidPoint(modelName, edgeSelected)
        
        # aspectRatio = self.config.Get('Aspect_Ratio')
        
        # edgesAfterSplit = simlab.getEntityFromGroup(edgeGroup)
        # faceGroup = 'faceGroup'
        # simlablib.DeleteGroups(faceGroup)
        # simlablib.SelectAssociatedEntities(modelName, 'Edge', edgesAfterSplit, 'Face', faceGroup)
        # faceAssEdges = simlab.getEntityFromGroup(faceGroup)

        # meshQualityCleanupOnFace(modelName, faceAssEdges, aspectRatio)

        
        simlabutil.ClearSelection()

    def CloseDialog(self):
        super().CloseDialog()

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

def splitEdgeAtMidPoint(modelName, edge):
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
    <Angle Check="0" Value="0.0"/>
    <TopoEdge Check="0" Value=""/>
    <Equivalence Value=""/>
    <MidPoint Check="1">
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edge).strip('()''[]') +'''</Edge>
    </Entities>
    </MidPoint>
    <Output/>
    </SplitEdge>'''
    simlab.execute(SplitEdge)

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