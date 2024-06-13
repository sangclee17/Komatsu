# coding: shift-jis

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import os, sys, importlib
from hwx import simlab
import time

SRC_DIR = os.path.dirname(os.path.realpath(__file__))
IMAGE_DIR = (os.path.join(SRC_DIR, 'images'))
PROJECT_DIR = os.path.join(SRC_DIR, "..")
LOG_DIR = os.path.join(PROJECT_DIR, "log")

if not SRC_DIR in sys.path:
    sys.path.append(SRC_DIR)

import basedialog
import simlablib

class Mesh2dDialog(basedialog.BaseDialog):
    def __init__(self, master, parent, config):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('表面メッシュ')
        self.master.resizable(width=False, height=False)
        self.master.attributes('-topmost', True)
        self.master.protocol('WM_DELETE_WINDOW', self.CloseDialog)
        self.config = config

        self.CreateWidgets()
    
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        try:
            avgElem = float(self.config.Get('Average_Elem_Size'))
        except (ValueError,KeyError):
            avgElem = 10.0
        
        try:
            triAspectRatio = float(self.config.Get('Aspect_Ratio'))
        except (ValueError,KeyError):
            triAspectRatio = 10.0
        
        try:
            angle = float(self.config.Get('Max_Angle_Per_Elem'))
        except (ValueError,KeyError):
            angle = 45
        
        self.frmMeshSetting = tk.Frame(self.frmTop)
        self.frmMeshSetting.pack(side=tk.TOP, anchor=tk.NW)
        self.frmMeshSetting.columnconfigure((0,2),weight=1)

        tk.Label(self.frmMeshSetting, text='平均要素長：').grid(row=0, column=0, sticky='nw')
        tk.Frame(self.frmMeshSetting, width=40).grid(row=0, column=1, sticky='nwse')
        self.entAvgElemSize = tk.Entry(self.frmMeshSetting, width=10)
        self.entAvgElemSize.insert(tk.END, avgElem)
        self.entAvgElemSize.grid(row=0, column=2, sticky='nwse')

        tk.Label(self.frmMeshSetting, text='アスペクト比：').grid(row=1, column=0, sticky='nw')
        self.entTriAspectRatio = tk.Entry(self.frmMeshSetting, width=10)
        self.entTriAspectRatio.insert(tk.END, triAspectRatio)
        self.entTriAspectRatio.grid(row=1, column=2, sticky='nwse')

        tk.Label(self.frmMeshSetting, text='要素あたりの最大角度：').grid(row=2, column=0, sticky='nw')
        self.entAngle = tk.Entry(self.frmMeshSetting, width=10)
        self.entAngle.insert(tk.END, angle)
        self.entAngle.grid(row=2, column=2, sticky='nwse')

        self.frmMeshCleanUp = tk.Frame(self.frmTop)
        self.frmMeshCleanUp.pack(side=tk.TOP, anchor=tk.NW)
        self.chkMeshCleanUp = tk.BooleanVar()
        self.chkMeshCleanUp.set(True)
        self.chkBtnMeshCleanUP = tk.Checkbutton(self.frmMeshCleanUp, text='アスペクト比でメッシュクリーンアップ', variable = self.chkMeshCleanUp)
        self.chkBtnMeshCleanUP.pack(side=tk.LEFT, anchor=tk.NW)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.btnMeshStart = tk.Button(self.frmTop, text='実行', width=10, command=self.StartSurfaceMesh)
        self.btnMeshStart.pack(side=tk.LEFT, anchor=tk.NW)

        self.btnClose = tk.Button(self.frmTop, text='閉じる', width=10, command=self.CloseDialog)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NW)

    def StartSurfaceMesh(self):
        try:
            avgElemSize = float(self.entAvgElemSize.get())
        except ValueError:
            tk.messagebox.showinfo('情報','メッシュ平均要素で数字を入力してください。')
            return
        else:
            if avgElemSize <= 0:
                tk.messagebox.showinfo('情報','メッシュ平均要素で０より大きい数字を入力してください。')
                return
        
        try:
            aspectRatio = float(self.entTriAspectRatio.get())
        except ValueError:
            tk.messagebox.showinfo('情報','アスペクト比で数字を入力してください。')
            return
        else:
            if aspectRatio <= 0:
                tk.messagebox.showinfo('情報','アスペクト比で０より大きい数字を入力してください。')
                return
        
        try:
            angle = float(self.entAngle.get())
        except ValueError:
            tk.messagebox.showinfo('情報','要素当たりの最大角度で数字を入力してください。')
            return
        else:
            if angle <= 0:
                tk.messagebox.showinfo('情報','要素当たりの最大角度で数字を入力してください。')
                return
        
        meshCleanUpON = self.chkMeshCleanUp.get()

        allModelNames = simlab.getAllRootModelNames('CAD')
        if len(allModelNames) > 1:
            messagebox.showinfo('情報','CADモデルが複数あります。マージして一個にしてください。')
            return
        elif len(allModelNames) == 0:
            messagebox.showinfo('情報','CADモデルをインポイしてください。')
            return

        modelName = simlab.getModelName('CAD')

        surfaceTriMesh(modelName, avgElemSize, angle, aspectRatio)

        modelName = simlab.getModelName('FEM')

        if not modelName:
            messagebox.showinfo('情報','メッシュ失敗しました。')
            return
        
        if meshCleanUpON:
            meshQualityCleanup(modelName, aspectRatio)
        
    
    def CloseDialog(self):
        super().CloseDialog()

def surfaceTriMesh(modelName, avgElemSize, anglePerElem, aspectRatio):
    SurfaceMesh=''' <SurfaceMesh UUID="08df0ff6-f369-4003-956c-82781326c876">
    <tag Value="-1"/>
    <SurfaceMeshType Value="Tri"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body></Body>
    </Entities>
    </SupportEntities>
    <Tri>
    <ElementType Value="Tri3"/>
    <AverageElementSize Value="'''+ str(avgElemSize) +'''" Checked="1"/>
    <MaximumElementSize Value="14.14 mm" Checked="0"/>
    <MinimumElementSize Value="'''+ str(avgElemSize/aspectRatio) +'''"/>
    <GradeFactor Value="1.5"/>
    <MaximumAnglePerElement Value="'''+ str(anglePerElem) +'''"/>
    <CurvatureMinimumElementSize Value="'''+ str(avgElemSize/2) +'''"/>
    <AspectRatio Value="'''+ str(aspectRatio) +'''"/>
    <IdentifyFeaturesAndMesh Checked="1"/>
    <AdvancedOptions>
    <ImprintMeshing Checked="0"/>
    <BetterGeometryApproximation Checked="0"/>
    <CoarseMesh Checked="0"/>
    <CoarseMesh_UseExistingNodes Checked="0"/>
    <CreateNewMeshModel Checked="1"/>
    <UserDefinedModelName Value=""/>
    <Tri6WithStraightEdges Checked="0"/>
    <ImproveSkewAngle Value="0"/>
    <MappedMesh Value="0"/>
    <MeshPattern Value="0"/>
    </AdvancedOptions>
    </Tri>
    </SurfaceMesh>'''
    simlab.execute(SurfaceMesh)

def meshQualityCleanup(modelName, aspectRatLimit):
    QualityCheck=''' <QCheck UUID="412da11b-2793-4c07-a058-e49f209f007d">
    <ElementType Value="Tri"/>
    <Option Value="Compute"/>
    <Quality LimitValue="'''+ str(aspectRatLimit) +'''" Name="Aspect Ratio" Condition="G Than Or Eq"/>
    <Quality Name="Edge Length" MinimumLimitValue="0.5" Condition="L Than and G Than Or Eq" MaximumLimitValue="100"/>
    <Quality LimitValue="0.2" Name="Height" Condition="L Than"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body></Body>
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
    <Body></Body>
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
    <Body></Body>
    </Entities>
    </SupportEntities>
    </QCheck>'''
    simlab.execute(QualityCheck)

    UpdateModel=''' <UpdateMTopology UUID="D1F56859-D6DB-4431-8699-7E3BE98DA530">
    <tag Value="-1"/>
    <ModelName Value="'''+ modelName +'''"/>
    </UpdateMTopology>'''
    simlab.execute(UpdateModel)