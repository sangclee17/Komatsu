﻿# SimLab ver. 2019.2
from hwx import simlab, gui
import os, sys, traceback, csv
import numpy as np
import tempfile

LOGFNAME = "sl_error.txt"
def log_message(func):
    def wrapper(*args, **kwargs):
        logDir = os.path.join(os.path.dirname(__file__), 'log')
        if not os.path.isdir(logDir):
            os.mkdir(logDir)
        result = func(*args, **kwargs)
        logFile = os.path.join(logDir, LOGFNAME)
        with open(logFile, "a") as f:
            f.write(result)
        return result

    return wrapper

@log_message
def logging(s):
    return "{}\n".format(s)

def ImportFile(filePath, params = None):
    '''
        brief Imports SimLab database file and ParaSolid file. Other format files are not implemented.
        Args:
            filePath (str): File path
            params: Import parameter dictionary

        returns:
            Nothing

    '''
    try:
        path, ext = os.path.splitext(filePath)
        ext = ext.lower()
        Import = ''

        # SimLab Database
        if ext == '.slb':
            ImportSlb=''' <ImportSlb CheckBox="ON" UUID="C806F6DF-56FA-4134-9AD1-1010BF292183" gda="">
            <tag Value="1"/>
            <Name Value="''' + filePath + '''"/>
            <FileName Value="''' + filePath + '''"/>
            <ImportOrOpen Value="1"/>
            <Output/>
            </ImportSlb>'''
            simlab.execute(ImportSlb)
        # Parasolid
        elif ext in ['.x_t', '.xmt_txt', '.x_b']:
            # default
            Imprint = 0
            SaveGeometryInDatabase = 1
            ImportAssemblyStructure = 1

            # arguments
            if params != None:
                if 'Imprint' in params.keys():
                    Imprint = params['Imprint']
                if 'SaveGeometryInDatabase' in params.keys():
                    SaveGeometryInDatabase = params['SaveGeometryInDatabase']
                if 'ImportAssemblyStructure' in params.keys():
                    ImportAssemblyStructure = params['ImportAssemblyStructure']

            # SaveGeometryInDatabase, ImportAssemblyStructure need Imprint=0
            if int(Imprint) == 1:
                SaveGeometryInDatabase = 0
                ImportAssemblyStructure = 0

            ImportParasolid=''' <ImportParasolid CheckBox="ON" Type="Parasolid" UUID="400d622c-e74a-4f87-bc0b-af51659b9b6d" gda="">
            <tag Value="1"/>
            <FileName widget="LineEdit" HelpStr="File name to be imported." Value="''' + filePath + '''"/>
            <Units HelpStr="Units to which this file is to be imported into" Value="MilliMeter"/>
            <SolidBodyType Value="1"/>
            <SheetBodyType Value="0"/>
            <WireBodyType Value="0"/>
            <GeneralBodyType Value="0"/>
            <ImportasFacets Value="0"/>
            <Imprint Value="''' + str(Imprint) + '''"/>
            <Groups Value="0"/>
            <Merge Value="0"/>
            <ImportAssemblyStructure Value="''' + str(ImportAssemblyStructure) + '''"/>
            <SaveGeometryInDatabase Value="''' + str(SaveGeometryInDatabase) + '''"/>
            <FileCount value="0" Value="0"/>
            <Output widget="NULL"/>
            <ImportOption Value="1"/>
            <TransXmlFileName Value=""/>
            <TransOutFileName Value=""/>
            </ImportParasolid>'''
            simlab.execute(ImportParasolid)

        # step file
        elif ext in ['.stp']:
            STEP_Import=''' <STEP_Import CheckBox="ON" Type="STEP" gda="" UUID="e88f2fcc-2430-4e47-9455-78b4dea9b064">
            <FileName Value="'''+ filePath +'''" widget="LineEdit" HelpStr="File name to be imported."/>
            <Method Value="Convert to Parasolid"/>
            <BodyName Value="1"/>
            <ReadPartName Value="0"/>
            <SketchWireframe Value="0"/>
            <Groups Value="0"/>
            <Imprint Value="0"/>
            <Facets Value="0"/>
            <AssemblyStructure Value="0"/>
            <SaveGeometryInDatabase Value="0"/>
            </STEP_Import>'''
            simlab.execute(STEP_Import)

        else:
            raise ValueError('There is no implementation.') 
    except:
        logging(traceback.format_exc())
    return

def ExportSlb(filePath):
    '''
        Export SimLab data file.
        Args:
            filePath: File path
    '''
    try:
        ExportSlb=''' <ExportSlb UUID="a155cd6e-8ae6-4720-8ab4-1f50d4a34d1c">
        <tag Value="-1"/>
        <Name Value=""/>
        <Option Value="1"/>
        <FileName Value="''' + filePath + '''"/>
        </ExportSlb>'''
        simlab.execute(ExportSlb)
    except:
        logging(traceback.format_exc())
    return


def ExportParasolid(filePath):
    '''
        Export Parasolid file.
        Args:
            filePath: File path
    '''
    try:
        ExportParasolid=''' <ExportParasolid UUID="b1db9c88-8712-4830-a89c-3a3ec6a205a6" CheckBox="ON">
        <tag Value="-1"/>
        <Name Value=""/>
        <SupportEntities>
        <Entities>
            <Model>$Geometry</Model>
            <Body></Body>
        </Entities>
        </SupportEntities>
        <FileName Value="''' + filePath + '''"/>
        <ExportType Value="5"/>
        </ExportParasolid>'''
        simlab.execute(ExportParasolid)
    except:
        logging(traceback.format_exc())
    return

def CreateModel(modelName):
    '''
        Creates new model. If you specify the name 'modelName', model named 'modelName.gda' will be created.
        Args:
            modelName: Model name
    
    '''
    try:
        CreateModel=''' <Model UUID="C0B952E0-94B0-428c-80D0-93DC94A4DD83" gda="">
        <Name Value="''' +  modelName + '''"/>
        <tag Value="-1"/>
        <Output/>
        </Model>'''
        simlab.execute(CreateModel)
    except:
        logging(traceback.format_exc())
    return

def DeleteModel(modelName):
    '''
        Deletes model
        Args:
            modelName: Model name

    '''
    try:
        DeleteModel=''' <DeleteModel CheckBox="ON" updategraphics="0" UUID="AE031126-6421-4633-8FAE-77C8DE10C18F">
        <ModelName Value="''' +  modelName + '''"/>
        </DeleteModel>'''
        simlab.execute(DeleteModel)
    except:
        logging(traceback.format_exc())
    return

def RenameModel(fromName, toName):
    '''
        Changes the name of model
        Args:
            fromName: current model name
            toName: new name
    '''
    try:
        RenameModelQuuid=''' <RenameModelQuuid CheckBox="ON" UUID="895c167e-fcf4-44dc-98cb-47e2328c7733">
        <tag Value="-1"/>
        <Name Value=""/>
        <ModelId Value=""/>
        <ModelName Value="''' + fromName + '''"/>
        <NewName Value="''' + toName + '''"/>
        <Output/>
        </RenameModelQuuid>'''
        simlab.execute(RenameModelQuuid)
    except:
        logging(traceback.format_exc())
    return

def UpdateFeatures(modelType):
    modelName = simlab.getModelName(modelType)
    UpdateAttributes=''' <UpdateFeature UUID="68cd70e3-d5ba-4cdd-9449-9ca866be5e01" CheckBox="ON" gda="">
    <tag Value="-1"/>
    <Name Value="UpdateFeature3"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Body></Body>
    </Entities>
    </SupportEntities>
    <Output/>
    </UpdateFeature>'''
    simlab.execute(UpdateAttributes)

def DeleteBodies(modelName, bodies):
    '''
        Delete bodies specified
        Args:
            modelName: model name
            bodies: Body list or typle
    '''
    DeleteEntities(modelName, 'Body', bodies)

def RenameBody(modelName, currentBodyName, newBodyName):
    '''
        Rename the name of the body
        Args:
            modelName: Model name
            currentBodyName: body name to be renmaed
            newBodyName: new body name
    '''
    try:
        RenameBody=''' <RenameBody CheckBox="ON" UUID="78633e0d-3d2f-4e9a-b075-7bff122772d8">
        <SupportEntities>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Body>''' + str(currentBodyName).replace("'",'"').strip("()""[]") + '''</Body>
        </Entities>
        </SupportEntities>
        <NewName Value="''' + newBodyName + '''"/>
        <Output/>
        </RenameBody>'''
        simlab.execute(RenameBody)
    except:
        logging(traceback.format_exc())
    return

def MergeBodies(modelName, bodies):
    '''
        Merge multiple bodies into the first body
        Args:
            modelName: model name
            bodies: body name list or tuple
    '''
    try:
        bodies = str(bodies).replace("'",'"')
        bodies = str(bodies).strip("[]""()")

        BodyMergeRightClick=''' <BodyMergeRightClick CheckBox="ON" UUID="7d2fbe6f-4dd7-4848-8cb5-f8be2d72c418">
        <tag Value="-1"/>
        <ModelId Value=""/>
        <BodyId>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Body>''' + bodies + ''',</Body>
        </Entities>
        </BodyId>
        <Output/>
        </BodyMergeRightClick>'''
        simlab.execute(BodyMergeRightClick)
    except:
        logging(traceback.format_exc())
    return

def MergeEdges(modelName, edges):

    MergeEdges=''' <MergeEdge UUID="C9CBBE68-5593-453b-9C95-2B3F550906EA" gda="">
    <Name Value="MergeEdge16"/>
    <tag Value="-1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edges).strip("()""[]") +'''</Edge>
    </Entities>
    </SupportEntities>
    <Output/>
    </MergeEdge>'''
    simlab.execute(MergeEdges)


def TranslateBodies(modelName, bodies, direction, distance):
    '''
        Translate bodies in parallel
        Args:
            bodies: body name in list or tuple
            direction: normal direction to be headed. e.g. [1,0,0]
            distance: distance to be moved in parallel
    '''
    try:
        bodies = str(bodies).replace("'",'"')
        bodies = str(bodies).strip("[]""()")

        direction = str(direction).strip("[]""()")
        distance = str(distance)

        Transform=''' <Transform UUID="604b2194-5dd2-4701-beb2-6784d03c5535">
        <Operation Value="Translate"/>
        <SupportEntities>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Body>''' + bodies + ''',</Body>
        </Entities>
        </SupportEntities>
        <TranslationVector Value="''' +  direction + ''',"/>
        <Distance Value="''' + distance + '''"/>
        </Transform>'''
        simlab.execute(Transform)
    except:
        logging(traceback.format_exc())
    return

def RotateBodies(modelName, bodies, center, rotationAxis, angle):
    '''
        Rotate bodies
        Args:
            modelName: model name
            bodies: body name in list or tuple
            center: the center of the body [0,0,0]
            rotationAxis: the axis of the rotation e.g. [0,0,1]
            angle: angle to rotate in degree
    ''' 
    try:
        bodies = str(bodies).replace("'",'"')
        bodies = str(bodies).strip("[]""()")

        center = str(center).strip("[]""()")
        rotationAxis = str(rotationAxis).strip("[]""()")
        angle = str(angle)

        Transform=''' <Transform UUID="604b2194-5dd2-4701-beb2-6784d03c5535">
        <Operation Value="Rotate"/>
        <SupportEntities>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Body>''' + bodies + ''',</Body>
        </Entities>
        </SupportEntities>
        <Center Value="''' + center + ''',"/>
        <RotationAxis Value="''' + rotationAxis + ''',"/>
        <Angle Value="''' + angle + '''"/>
        </Transform>'''
        simlab.execute(Transform)
    except:
        logging(traceback.format_exc())
    return


def CreateGroup(modelName, entityType, entities, groupName, duplication=0, colorRGB='255,206,0'):
    '''
        Creates a group in type, 'Body', 'Face', 'Edge', 'Vertex', 'Element'.
        Creating empty groups is not allowed
        Args:
            modelName: Model name
            entityType: Entity type such as 'Body', 'Face', 'Edge', 'Vertex', 'Element'
            entities: Entity list or tuple
            groupName: Group name
            duplication: Whether to allow selected entities in only one group. 1:Only one, 0:Multiple 
            colorRGB: Color R, G, B
    '''
    try:
        entities = str(entities).replace("'",'"')
        entities = str(entities).strip("[]""()")
        entityType = entityType.lower()
        keyDict = {
            'body': 'Body',
            'face': 'Face',
            'edge': 'Edge',
            'vertex': 'Vertex',
            'element': 'Element',
            'node': 'Node',
        }
        key = keyDict[entityType]

        CreateGroup=''' <CreateGroup CheckBox="OFF" isObject="4" UUID="899db3a6-bd69-4a2d-b30f-756c2b2b1954">
        <tag Value="-1"/>
        <Name OldValue="" Value="''' + groupName + '''"/>
        <SupportEntities>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <''' + key + '''>''' + entities + ''',</''' + key + '''>
        </Entities>
        </SupportEntities>
        <Type Value="''' + key + '''"/>
        <Color Value="'''+ colorRGB + ''',"/>
        <Dup Value="''' + str(duplication) + '''"/>
        </CreateGroup>'''
        simlab.execute(CreateGroup)
    except:
        logging(traceback.format_exc())
    return


def CreateEmptyGroup(entityType, groupName, colorRGB='255,206,0'):
    '''
        Creates a empty group of the specified type of Body, Face, Edge, Vertex, Element

        Args:
            entityType: Entity type, such as 'Body', 'Face', 'Edge', 'Vertex', 'Element'
            groupName: Group name
            colorRGB: Color R, G, B
    '''
    try:
        entityType = entityType.lower()
        keyDict = {
            'body': 'Body',
            'face': 'Face',
            'edge': 'Edge',
            'vertex': 'Vertex',
            'element': 'Element',
            'node': 'Node',
        }
        key = keyDict[entityType]

        CreateGroup=''' <CreateGroup CheckBox="OFF" isObject="4" UUID="899db3a6-bd69-4a2d-b30f-756c2b2b1954">
        <tag Value="-1"/>
        <Name Value="''' + groupName + '''" OldValue=""/>
        <SupportEntities/>
        <Type Value="''' + key + '''"/>
        <Color Value="'''+ colorRGB + ''',"/>
        <Dup Value="0"/>
        </CreateGroup>'''
        simlab.execute(CreateGroup)
    except:
        logging(traceback.format_exc())
    return


def DeleteGroups(groups):
    '''
        Deletes the groups
        Args:
            groups: groups in list or tuple
    '''
    DeleteEntities('', 'Group', groups)


def RenameGroup(fromName, toName):
    '''
        Change the name of the group
        Args:
            fromName: current name
            toName: a new group name 
    '''
    try:
        RenameGroupControl=''' <RenameGroupControl CheckBox="ON" UUID="d3addb85-3fd0-4972-80af-e699f96e9045">
        <tag Value="-1"/>
        <Name Value="''' + fromName + '''"/>
        <NewName Value="''' + toName + '''"/>
        <Output/>
        </RenameGroupControl>'''
        simlab.execute(RenameGroupControl)
    except:
        logging(traceback.format_exc())
    return


def DeleteEntities(modelName, entityType, entities):
    '''
        Deletes entities of the specified type. type = 'Body', 'Face', 'Edge', 'Element', 'Group'
        Args:
            modelName: model name
            entityType: Entity type such as  'Body', 'Face', 'Edge', 'Element', 'Group'
            entities: Comma separated string such as ('Body-1','Body-2'), or IDs list or tuple such as (1,2,3) or [1,2,3]
    '''
    try:
        entities = str(entities).replace("'",'"')
        entities = str(entities).strip("[]""()")
        DeleteEntity = ''
        entityType = entityType.lower()

        if entityType == "body":
            DeleteEntity=''' <DeleteEntity CheckBox="ON" UUID="BF2C866D-8983-4477-A3E9-2BBBC0BC6C2E">
            <tag Value="-1"/>
            <Name Value=""/>
            <SupportEntities>
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Body>''' + entities + ''',</Body>
            </Entities>
            </SupportEntities>
            </DeleteEntity>'''
        elif entityType == "face":
            DeleteEntity=''' <DeleteEntity CheckBox="ON" UUID="BF2C866D-8983-4477-A3E9-2BBBC0BC6C2E">
            <tag Value="-1"/>
            <Name Value=""/>
            <SupportEntities>
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Face>''' + entities + ''',</Face>
            </Entities>
            </SupportEntities>
            </DeleteEntity>'''
        elif entityType == "edge":
            DeleteEntity = ''' <DeleteEdge UUID="c316a39d-9c78-4c85-9028-5ece6886aeb8">
            <SupportEntities>
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Edge>''' + entities + ''',</Edge>
            </Entities>
            </SupportEntities>
            </DeleteEdge>'''
        elif entityType == "element":
            DeleteEntity=''' <DeleteElement CheckBox="ON" UUID="8d996aff-8ed7-4e5e-9637-b4f75ded7c2c">
            <tag Value="-1"/>
            <Name Value=""/>
            <SupportEntities>
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Element>''' + entities + ''',</Element>
            </Entities>
            </SupportEntities>
            <FreeEdgeDisplay Value="0"/>
            <NonManifoldDisplay Value="0"/>
            </DeleteElement>'''
        elif entityType == "group":
            entities = str(entities).replace('"','')
            DeleteEntity=''' <DeleteGroupControl CheckBox="ON" UUID="2a3b5834-9708-4b03-871c-6d05623667bd">
            <tag Value="-1"/>
            <Name Value="''' + entities + ''',"/>
            <Output/>
            </DeleteGroupControl>'''
        else:
            raise ValueError('There is no implementation.') 
        simlab.execute(DeleteEntity)
    except:
        logging(traceback.format_exc())
    return

def AvailableNodeID(modelName, baseNodeID=1):
    '''
        get node Id that can be created
        Args:
            modelName
            baseNodeID
        return:
            unique node Id
    '''
    nodeID = baseNodeID
    while len(simlab.getNodePositionFromNodeID(modelName, nodeID)) != 0:
        nodeID += 1
    return nodeID

def CreateNodeByXYZ(modelName, xyz, uniqueNodeID=""):
    '''
        Creates a node at the specified coordinates
        Args:
            xyz: coordinate. e.g. [0.0, 1.0, 2.0]
            uniqueNodeId: node ID. If it is empty, the simlab will decide
    '''
    try:
        xyz = str(xyz).strip("[]""()")
        uniqueNodeID = str(uniqueNodeID)

        uniqueFlag = '0'
        if uniqueNodeID != "":
            uniqueFlag = '1'

        NodeByXYZ=''' <NodeByXYZ UUID="F200B5A2-D615-4d01-8DE2-25596B3B1EB8">
        <tag Value="-1"/>
        <Name Value=""/>
        <LocalCoordinateSystem Value="0"/>
        <Position Value="''' + xyz + '''"/>
        <Node Value="''' + uniqueNodeID + '''"/>
        <UniqueNodeId Value="''' + uniqueFlag + '''"/>
        <ModelName Value="''' + modelName + '''"/>
        </NodeByXYZ>'''
        simlab.execute(NodeByXYZ)
    except:
        logging(traceback.format_exc())
    return


def CreateNodeByArc(modelName, entityType, entities, uniqueNodeID=""):
    '''
        Create nodes at the center of the given arc
        Args:
            entityType: 'Edge' or 'Node'
            entities:  If entityType is 'Edge', ID of arc edge. 
                    If entityType is 'Node', IDs of 3 nodes on arc
            uniqueNodeID: node ID. Simlab will decide if left empty
    '''
    try:
        entityType = entityType.lower()
        entities = str(entities).strip("[]""()")
        uniqueNodeID = str(uniqueNodeID)

        uniqueFlag = '0'
        if uniqueNodeID != "":
            uniqueFlag = '1'

        NodeByArc=''' <NodeByArc UUID="24DF232A-C273-4155-93E7-290E5812B00C" pixmap="block">
        <tag Value="-1"/>
        <Name Value=""/>
        <SupportEntities>
        <Entities>
            <Model>''' + modelName + '''</Model>'''

        if entityType == 'edge':
            NodeByArc +='''
            <Edge>''' +  entities + ''',</Edge>
            </Entities>
            </SupportEntities>
            <Option Value="Arc"/>'''
        elif entityType == 'node':
            NodeByArc +='''
            <Node>''' +  entities + ''',</Node>
            </Entities>
            </SupportEntities>
            <Option Value="Three Nodes"/>'''
        else:
            raise ValueError('There is no implementation.') 
        
        NodeByArc +='''
        <Node Value="''' + uniqueNodeID + '''"/>
        <UniqueNodeId Value="''' + uniqueFlag + '''"/>
        <ModelName Value="''' + modelName + '''"/>
        </NodeByArc>'''
        simlab.execute(NodeByArc)
    except:
        logging(traceback.format_exc())
    return

def CreateNodeByCentroid(modelName, entityType, entities, uniqueNodeID=""):
    '''
        Creates nodes at the centroid of specified face or body.
        Args:
            modelName: Model name
            entityType: 'Face' or 'Body'
            entities: entities
            uniqueNodeID: node id. Simlab will decide if left empty
    '''
    try:
        entityType = entityType.lower()
        entities = str(entities).replace("'",'"')
        entities = str(entities).strip("[]""()")
        uniqueNodeID = str(uniqueNodeID)

        uniqueFlag = '0'
        if uniqueNodeID != "":
            uniqueFlag = '1'

        NodeByCentroid =''' <NodeByCentroid UUID="22f9ea65-1492-478d-a42a-95b405b3532d" pixmap="block">
        <tag Value="-1"/>
        <Name Value=""/>
        <SupportEntities>
        <Entities>
            <Model>''' + modelName + '''</Model>'''

        if entityType == 'face':
            NodeByCentroid +='''
            <Face>''' +  entities + ''',</Face>'''
        elif entityType == 'body':
            NodeByCentroid +='''
            <Body>''' +  entities + ''',</Body>'''
        else:
            raise ValueError('There is no implementation.') 

        NodeByCentroid +='''
        </Entities>
        </SupportEntities>
        <Node Value="''' + uniqueNodeID + '''"/>
        <UniqueNodeId Value="''' + uniqueFlag + '''"/>
        <ModelName Value="''' + modelName + '''"/>
        </NodeByCentroid>'''
        simlab.execute(NodeByCentroid)
    except:
        logging(traceback.format_exc())
    return

def DeleteAllOphanNodes():
    '''
        Delete all orphan nodes
    '''
    try:
        DeleteOrphanNodes=''' <DeleteOrphanNode UUID="16A3F8AE-EDAB-4988-9006-7FCB3952F161">
        <tag Value="-1"/>
        <Name Value="DeleteOrphanNode1"/>
        <SupportEntities EntityTypes="" ModelIds="" Value=""/>
        <All Value="1"/>
        <Selected Value="0"/>
        <UnSelected Value="0"/>
        </DeleteOrphanNode>'''
        simlab.execute(DeleteOrphanNodes)
    except:
        logging(traceback.format_exc())
    return

def DeleteSelectedOphanNodes(modelName, selectedNodes, reverse=False):
    '''
        Delete selected orphan nodes
        Args:
            modelName: model name
            selectedNodes: node ids in list or tuple
            reverse: False-> delete the selected nodes
                    True -> delete the unselected nodes        
    '''
    try:
        selectedNodes = str(selectedNodes).strip("[]""()")        
        if reverse:
            selected = '0'
            unSelected = '1'
        else:
            selected = '1'
            unSelected = '0'

        DeleteOrphanNodes=''' <DeleteOrphanNode UUID="16A3F8AE-EDAB-4988-9006-7FCB3952F161">
        <tag Value="-1"/>
        <Name Value="DeleteOrphanNode7"/>
        <SupportEntities>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Node>''' + selectedNodes + ''',</Node>
        </Entities>
        </SupportEntities>
        <All Value="0"/>
        <Selected Value="''' + selected + '''"/>
        <UnSelected Value="''' + unSelected + '''"/>
        </DeleteOrphanNode>'''
        simlab.execute(DeleteOrphanNodes)
    except:
        logging(traceback.format_exc())
    return

def SelectAssociatedEntities(modelName, fromEntityType, fromEntities, toEntityType, groupName):
    '''
        Finds the associated entities from the selected entities and create a group
        Args:
            modelName: Model name
            fromEntityType: a type of the selected eneity, 'Body', 'Face', 'Edge', 'Element', 'Node'
            fromEntities: list or tuple of the selected entities
            toEntityType: Entity type to search (see note:)
            
            The combination of associated entities.
            - fromEntityType = Body    : toEntityType = Body, Face, Edge, Vertex, Node, 2DElement, 3DElement
            - fromEntityType = Face    : toEntityType = Body, Edge, Vertex, Node, Element
            - fromEntityType = Edge    : toEntityType = Face, Vertex, Node
            - fromEntityType = Element : toEntityType = Body, Face, CornerNode, MidNode
            - fromEntityType = Node    : toEntityType = Body, Face, 2DElement, 3DElement
            
            groupName: Group name
    '''
    try:
        fromEntities = str(fromEntities).replace("'",'"')
        fromEntities = str(fromEntities).strip("[]""()")

        fromEntityType = fromEntityType.lower()
        toEntityType = toEntityType.lower()
        keyDict = {
            'body': 'Bodies',
            'face': 'Faces',
            'edge': 'Edges',
            'vertex': 'Vertex',
            'node': 'Nodes',
            'element': 'Elements',
            '2delement': '2DElements',
            '3delement': '3DElements',
            'cornernode': 'Cornernodes',
            'midnode': 'Mid-nodes',
        }
        toEntityKey = keyDict[toEntityType]

        if fromEntityType == 'body':
            SelectBodyAssociatedEntities=''' <SelectBodyAssociatedEntities UUID="f3c1adc7-fbac-4d30-9b29-9072f36f1ad4">
            <InputBody Values="">
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Body>''' + fromEntities + ''',</Body>
            </Entities>
            </InputBody>
            <Option Value="''' + toEntityKey + '''"/>
            <Groupname Value="''' + groupName + '''"/>
            </SelectBodyAssociatedEntities>'''
            simlab.execute(SelectBodyAssociatedEntities)
        elif fromEntityType == 'face':
            SelectFaceAssociatedEntities=''' <SelectFaceAssociatedEntities UUID="4128ad97-7527-4dad-9746-470cfa135434">
            <InputFaces Values="">
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Face>''' + fromEntities + ''',</Face>
            </Entities>
            </InputFaces>
            <Option Value="''' + toEntityKey + '''"/>
            <Groupname Value="''' + groupName + '''"/>
            </SelectFaceAssociatedEntities>'''
            simlab.execute(SelectFaceAssociatedEntities)
        elif fromEntityType == 'edge':
            SelectEdgeAssociatedEntities=''' <SelectEdgeAssociatedEntities UUID="551fdd5b-6a8c-4a30-8ab0-fbaf9257343e">
            <InputEdges Values="">
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Edge>''' + fromEntities + ''',</Edge>
            </Entities>
            </InputEdges>
            <Option Value="''' + toEntityKey + '''"/>
            <Groupname Value="''' + groupName + '''"/>
            </SelectEdgeAssociatedEntities>'''
            simlab.execute(SelectEdgeAssociatedEntities)
        elif fromEntityType == 'element':
            SelectElementAssociatedEntities=''' <SelectElementAssociatedEntities UUID="7062f057-0e48-4ccc-ad73-e60584e8ff26">
            <InputElement Values="">
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Element>''' + fromEntities + ''',</Element>
            </Entities>
            </InputElement>
            <Option Value="''' + toEntityKey + '''"/>
            <Groupname Value="''' + groupName + '''"/>
            </SelectElementAssociatedEntities>'''
            simlab.execute(SelectElementAssociatedEntities)
        elif fromEntityType == 'node':
            SelectNodeAssociatedEntities=''' <SelectNodeAssociatedEntities UUID="6731d198-667e-49c9-8612-c7d980368508">
            <InputNodes Values="">
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Node>''' + fromEntities + ''',</Node>
            </Entities>
            </InputNodes>
            <Option Value="''' + toEntityKey + '''"/>
            <Groupname Value="''' + groupName + '''"/>
            </SelectNodeAssociatedEntities>'''
            simlab.execute(SelectNodeAssociatedEntities)
            # print(SelectNodeAssociatedEntities)
        else:
            raise ValueError('There is no implementation.') 
    except:
        # print(SelectNodeAssociatedEntities)
        pass
        logging(traceback.format_exc())
    return


def SelectAdjacentFaces(modelName, fromFaces, groupName):
    '''
        Select faces next to specified faces
        Args:
            modelName: model name
            fromFaces: list or tuple
            groupName: group name
    '''
    try:
        fromFaces = str(fromFaces).replace("'",'')
        fromFaces = str(fromFaces).replace('"','')
        fromFaces = str(fromFaces).strip("[]""()")

        SelectAdjacent=''' <SelectAdjacent recordable="0" UUID="06104eca-3dbf-45af-a99c-953c8fe0f4e4">
        <tag Value="-1"/>
        <Name Value=""/>
        <SupportEntities>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Face>''' + fromFaces + ''',</Face>
        </Entities>
        </SupportEntities>
        <NoofLayer Value="1"/>
        <VisiblesFaceOnly Value="0"/>
        <SelectAdjacent Value="1"/>
        <CreateGroup Name="''' + groupName + '''" Value="1"/>
        </SelectAdjacent>'''
        simlab.execute(SelectAdjacent)
    except:
        logging(traceback.format_exc())
    return

def FindNodesByPlane(modelName, fromEntityType, fromEntities, pointsOnPlane, 
    onPlane=1, above=1, below=0, tolerance=0.01, maximumNodes=1000000, showSurfaceNodes=1):
    '''
        Finds nodes on the plane or above/below from the specified entities. The result is in 'Show_Nodes' group.
        Args:
            modelName Model name.
            fromEntityType: the targeted entity type such as 'Body', 'Face', 'Group'
            fromEntities: list or tuple of the targeted entities.
            pointsOnPlane: 3 points on plane.
            onPlane: Whether to find nodes on the plane. 1:Find, 0:Do not find.
            above: Whether to find the above side of the plane. 1:Find, 0:Do not find.
            below: Whether to find the below side of the plane. 1:Find, 0:Do not find.
            tolerance: Tolerance.
            maximumNodes: Maximum number of nodes to search.
            showSurfaceNodes: Maximum number of nodes to search. 1:Only surface, 0:Include internal nodes in the solid body.
        Setting both above and below to 1 at the same time is not allowed.
    '''
    try:
        fromEntities = str(fromEntities).replace("'",'"')
        fromEntities = str(fromEntities).strip("[]""()")
        fromEntityType = fromEntityType.lower()

        p1, p2, p3 = pointsOnPlane
        p1 = str(p1).strip("[]""()")
        p2 = str(p2).strip("[]""()")
        p3 = str(p3).strip("[]""()")

        onPlane = str(onPlane)
        above = str(above) 
        below = str(below)
        tolerance = str(tolerance)
        maximumNodes = str(maximumNodes)
        showSurfaceNodes = str(showSurfaceNodes)

        NodesByRegion=''' <NodesByRegion UUID="ad9db725-dcb3-4f9c-abd7-0e7a8cf64d05">
        <tag Value="-1"/>
        <Name Value="Show Nodes"/>
        <SupportEntities>'''

        if fromEntityType == 'group':
            NodesByRegion +='''
            <Group>''' + fromEntities + ''',</Group>'''
        elif fromEntityType == 'face':
            NodesByRegion +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Face>''' + fromEntities + ''',</Face>
            </Entities>'''
        elif fromEntityType == 'body':
            NodesByRegion +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Body>''' + fromEntities + ''',</Body>
            </Entities>'''
        else:
            raise ValueError('There is no implementation.') 

        NodesByRegion +='''
        </SupportEntities>
        <Option Value="0"/>
        <RegionData Type="0">
            <PlaneData Value="''' + p1 + ''',''' + p2 + ''',''' + p3 + '''"/>
        </RegionData>
        <On Value="''' + onPlane + '''"/>
        <Above Value="''' + above + '''"/>
        <Below Value="''' + below + '''"/>
        <Tolerance Value="''' + tolerance + '''"/>
        <MaximumCount Value="''' + maximumNodes + '''"/>
        <ShowSurfaceNodes Value="''' + showSurfaceNodes + '''"/>
        <CreateGroup Value="1"/>
        </NodesByRegion>'''
        simlab.execute(NodesByRegion)
    except:
        logging(traceback.format_exc())
    return

def FindElementsByPlane(modelName, fromEntityType, fromEntities, pointsOnPlane, 
    onPlane=1, above=1, below=0, tolerance=0.01, maximumNodes=1000000):
    '''
        Finds elements on the plane or above/below from the specified entities. The result is in 'Show_Elements' group.
        Args:
            modelName: Model name
            fromEntityType: the targeted entity, such as 'Body', 'Face', 'Group'
            fromEntities: list or tuple of the targeted entity.
            pointsOnPlane: 3 points on plane.
            onPlane: Whether to find nodes on the plane. 1:Find, 0:Do not find.
            above: Whether to find the above side of the plane. 1:Find, 0:Do not find.
            below: Whether to find the below side of the plane. 1:Find, 0:Do not find.
            tolerance: Tolerance.
            maximumNodes: Maximum number of nodes to search.
        Setting both above and below to 1 at the same time is not allowed.
    '''
    try:
        fromEntities = str(fromEntities).replace("'",'"')
        fromEntities = str(fromEntities).strip("[]""()")
        fromEntityType = fromEntityType.lower()

        p1, p2, p3 = pointsOnPlane
        p1 = str(p1).strip("[]""()")
        p2 = str(p2).strip("[]""()")
        p3 = str(p3).strip("[]""()")

        onPlane = str(onPlane)
        above = str(above) 
        below = str(below)
        tolerance = str(tolerance)
        maximumNodes = str(maximumNodes)

        ShowElements=''' <ShowElements UUID="ebeb3013-454b-418a-9393-9d69ce183847">
        <tag Value="-1"/>
        <Name Value="Show Elements"/>
        <SupportEntities>'''

        if fromEntityType == 'group':
            ShowElements +='''
            <Group>''' + fromEntities + ''',</Group>'''
        elif fromEntityType == 'face':
            ShowElements +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Face>''' + fromEntities + ''',</Face>
            </Entities>'''
        elif fromEntityType == 'body':
            ShowElements +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Body>''' + fromEntities + ''',</Body>
            </Entities>'''
        else:
            raise ValueError('There is no implementation.') 

        ShowElements +='''
        </SupportEntities>
        <Option Value="1"/>
        <RegionData Type="Plane">
            <PlaneData Value="''' + p1 + ''',''' + p2 + ''',''' + p3 + '''"/>
        </RegionData>
        <On Value="''' + onPlane + '''"/>
        <Above Value="''' + above + '''"/>
        <Below Value="''' + below + '''"/>
        <Tolerance Value="''' + tolerance + '''"/>
        <MaximumCount Value="''' + maximumNodes + '''"/>
        <CreateGroup Value="1"/>
        </ShowElements>'''
        simlab.execute(ShowElements)
    except:
        logging(traceback.format_exc())
    return


def FindFacesByPlane(modelName, fromEntityType, fromEntities, pointsOnPlane, 
    onPlane=1, above=1, below=0, tolerance=0.01):
    '''
        Finds faces on the plane or above/below from the specified entities. The result is in 'Show_Faces' group.
        Args:
            modelName: Model name.
            fromEntityType: the targeted entity type, such as 'Body', 'Face', 'Group'
            fromEntities: list or tuple of the targeted entity
            pointsOnPlane: 3 points on plane.
            onPlane: Whether to find nodes on the plane. 1:Find, 0:Do not find.
            above: Whether to find the above side of the plane. 1:Find, 0:Do not find.
            below Whether to find the below side of the plane. 1:Find, 0:Do not find.
            tolerance Tolerance.
        Setting both above and below to 1 at the same time is not allowed.
    '''
    try:
        fromEntities = str(fromEntities).replace("'",'"')
        fromEntities = str(fromEntities).strip("[]""()")
        fromEntityType = fromEntityType.lower()

        p1, p2, p3 = pointsOnPlane
        p1 = str(p1).strip("[]""()")
        p2 = str(p2).strip("[]""()")
        p3 = str(p3).strip("[]""()")

        onPlane = str(onPlane)
        above = str(above) 
        below = str(below)
        tolerance = str(tolerance)

        FacesByPlane=''' <FacesByPlane UUID="116fb6e7-2d86-45fb-bbee-bd40e654a0bf">
        <Name Value="Show Faces"/>
        <SupportEntities>'''

        if fromEntityType == 'group':
            FacesByPlane +='''
            <Group>''' + fromEntities + ''',</Group>'''
        elif fromEntityType == 'face':
            FacesByPlane +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Face>''' + fromEntities + ''',</Face>
            </Entities>'''
        elif fromEntityType == 'body':
            FacesByPlane +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Body>''' + fromEntities + ''',</Body>
            </Entities>'''
        else:
            raise ValueError('There is no implementation.') 

        FacesByPlane +='''
        </SupportEntities>
        <Option Value="3"/>
        <RegionData Type="Plane">
            <PlaneData Value="''' + p1 + ''',''' + p2 + ''',''' + p3 + '''"/>
        </RegionData>
        <On Value="''' + onPlane + '''"/>
        <Above Value="''' + above + '''"/>
        <Below Value="''' + below + '''"/>
        <Tolerance Value="''' + tolerance + '''"/>
        <CreateGroup Value="1"/>
        </FacesByPlane>'''
        simlab.execute(FacesByPlane)
    except:
        logging(traceback.format_exc())
    return

def FindEdgesByPlane(modelName, bodies, pointsOnPlane, onPlane=1, above=1, below=0, tolerance=0.01):
    '''
        Finds edges on the plane or above/below from the specified entities. The result is in 'Show_Edges' group.
        Args:
            modelName: Model name.
            bodies: list or tuple
            pointsOnPlane: 3 points on plane.
            onPlane: Whether to find nodes on the plane. 1:Find, 0:Do not find.
            above: Whether to find the above side of the plane. 1:Find, 0:Do not find.
            below: Whether to find the below side of the plane. 1:Find, 0:Do not find.
            tolerance: Tolerance.
            Setting both above and below to 1 at the same time is not allowed.
    '''
    try:
        bodies = str(bodies).replace("'",'"')
        bodies = str(bodies).strip("[]""()")

        p1, p2, p3 = pointsOnPlane
        p1 = str(p1).strip("[]""()")
        p2 = str(p2).strip("[]""()")
        p3 = str(p3).strip("[]""()")

        onPlane = str(onPlane)
        above = str(above) 
        below = str(below)
        tolerance = str(tolerance)

        EdgesByPlane=''' <EdgesByPlane UUID="94ea9e4e-c496-4d6a-950e-66585ed62a28">
        <Name Value="Show Edges"/>
        <SupportEntities>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Body>''' + bodies + ''',</Body>
        </Entities>
        </SupportEntities>
        <Option Value="2"/>
        <RegionData Type="Plane">
            <PlaneData Value="''' + p1 + ''',''' + p2 + ''',''' + p3 + '''"/>
        </RegionData>
        <On Value="''' + onPlane + '''"/>
        <Above Value="''' + above + '''"/>
        <Below Value="''' + below + '''"/>
        <Tolerance Value="''' + tolerance + '''"/>
        <CreateGroup Value="1"/>
        </EdgesByPlane>'''
        simlab.execute(EdgesByPlane)
    except:
        logging(traceback.format_exc())
    return

def FindBodiesByPlane(modelName, bodies, pointsOnPlane, onPlane=1, above=1, below=0, tolerance=0.01):
    '''
        Finds bodies on the plane or above/below from the specified entities. The result is in 'Show_Edges' group.
        Args:
            modelName: Model name.
            bodies: bodies in list or tuple
            pointsOnPlane: 3 points on plane.
            onPlane: Whether to find nodes on the plane. 1:Find, 0:Do not find.
            above: Whether to find the above side of the plane. 1:Find, 0:Do not find.
            below: Whether to find the below side of the plane. 1:Find, 0:Do not find.
            tolerance: Tolerance.
            Setting both above and below to 1 at the same time is not allowed
    '''
    try:
        bodies = str(bodies).replace("'",'"')
        bodies = str(bodies).strip("[]""()")

        p1, p2, p3 = pointsOnPlane
        p1 = str(p1).strip("[]""()")
        p2 = str(p2).strip("[]""()")
        p3 = str(p3).strip("[]""()")

        onPlane = str(onPlane)
        above = str(above) 
        below = str(below)
        tolerance = str(tolerance)

        BodiesByPlane=''' <BodiesByPlane UUID="57a2e1ef-0e4b-4496-bd11-b57cd7c63c1b">
        <Name Value="Show Bodies"/>
        <SupportEntities>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Body>''' + bodies + ''',</Body>
        </Entities>
        </SupportEntities>
        <Option Value="4"/>
        <RegionData Type="Plane">
            <PlaneData Value="''' + p1 + ''',''' + p2 + ''',''' + p3 + '''"/>
        </RegionData>
        <On Value="''' + onPlane + '''"/>
        <Above Value="''' + above + '''"/>
        <Below Value="''' + below + '''"/>
        <Tolerance Value="''' + tolerance + '''"/>
        </BodiesByPlane>'''
        simlab.execute(BodiesByPlane)
    except:
        logging(traceback.format_exc())
    return

def FindNodesByCylinder(modelName, fromEntityType, fromEntities, topPoint, bottomPoint, radius, 
    onCylinder=1, outside=1, inside=0, tolerance=0.01, maximumNodes=1000000, showSurfaceNodes=1):
    '''
        Finds nodes on the cylinder or outside/inside from the specified entities. The result is in 'Show_Nodes' group.
        Args:
            modelName Model name.
            fromEntityType: Entity type of search source such as 'Body', 'Face', 'Group'
            fromEntities: Entities list or tuple of search source.
            topPoint: top point of cylinder axis. Example [1.0, 0.0, 2.0].
            bottomPoint: bottom point of cylinder axis.
            radius: radius of cylinder.
            onCylinder: Whether to find nodes on the cylinder. 1:Find, 0:Do not find.
            above: Whether to find the outside of the cylinder. 1:Find, 0:Do not find.
            below: Whether to find the inside of the cylinder. 1:Find, 0:Do not find.
            tolerance: Tolerance.
            maximumNodes: Maximum number of nodes to search.
            showSurfaceNodes: Maximum number of nodes to search. 1:Only surface, 0:Include internal nodes in the solid body.
        Setting both above and below to 1 at the same time is not allowed
    '''
    try:
        fromEntities = str(fromEntities).replace("'",'"')
        fromEntities = str(fromEntities).strip("[]""()")
        fromEntityType = fromEntityType.lower()

        topPoint = str(topPoint).strip("[]""()")
        bottomPoint = str(bottomPoint).strip("[]""()")
        radius = str(radius)

        onCylinder = str(onCylinder)
        outside = str(outside) 
        inside = str(inside)
        tolerance = str(tolerance)
        maximumNodes = str(maximumNodes)
        showSurfaceNodes = str(showSurfaceNodes)

        NodesByRegion=''' <NodesByRegion UUID="ad9db725-dcb3-4f9c-abd7-0e7a8cf64d05">
        <tag Value="-1"/>
        <Name Value="Show Nodes"/>
        <SupportEntities>'''

        if fromEntityType == 'group':
            NodesByRegion +='''
            <Group>''' + fromEntities + ''',</Group>'''
        elif fromEntityType == 'face':
            NodesByRegion +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Face>''' + fromEntities + ''',</Face>
            </Entities>'''
        elif fromEntityType == 'body':
            NodesByRegion +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Body>''' + fromEntities + ''',</Body>
            </Entities>'''
        else:
            raise ValueError('There is no implementation.') 

        NodesByRegion+='''
        </SupportEntities>
        <Option Value="0"/>
        <RegionData Type="Cylinder">
        <CylinderData>
            <TopPoints Value="''' + topPoint + '''"/>
            <BottomPoints Value="''' + bottomPoint + '''"/>
            <Radius Value="''' + radius + '''"/>
        </CylinderData>
        </RegionData>
        <On Value="''' + onCylinder + '''"/>
        <Above Value="''' + outside + '''"/>
        <Below Value="''' + inside + '''"/>
        <Tolerance Value="''' + tolerance + '''"/>
        <MaximumCount Value="''' + maximumNodes + '''"/>
        <ShowSurfaceNodes Value="''' + showSurfaceNodes + '''"/>
        <CreateGroup Value="1"/>
        </NodesByRegion>'''
        simlab.execute(NodesByRegion)
    except:
        logging(traceback.format_exc())
    return

def FindNodesBySphere(modelName, fromEntityType, fromEntities, sphereCenter, radius, 
    onSphere=0, outside=0, inside=1, tolerance=0.01, maximumNodes=1000000, showSurfaceNodes=1):
    try:
        fromEntities = str(fromEntities).replace("'",'"')
        fromEntities = str(fromEntities).strip("[]""()")
        fromEntityType = fromEntityType.lower()

        sphereCenter = str(sphereCenter).strip("[]""()")
        radius = str(radius)
        onSphere = str(onSphere)
        outside = str(outside) 
        inside = str(inside)
        tolerance = str(tolerance)
        maximumNodes = str(maximumNodes)
        showSurfaceNodes = str(showSurfaceNodes)

        NodesByRegion=''' <NodesByRegion UUID="ad9db725-dcb3-4f9c-abd7-0e7a8cf64d05">
        <tag Value="-1"/>
        <Name Value="Show Nodes"/>
        <SupportEntities>'''

        if fromEntityType == 'group':
            NodesByRegion +='''
            <Group>''' + fromEntities + ''',</Group>'''
        elif fromEntityType == 'face':
            NodesByRegion +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Face>''' + fromEntities + ''',</Face>
            </Entities>'''
        elif fromEntityType == 'body':
            NodesByRegion +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Body>''' + fromEntities + ''',</Body>
            </Entities>'''
        else:
            raise ValueError('There is no implementation.') 

        NodesByRegion+='''
        </SupportEntities>
        <Option Value="0"/>
        <RegionData Type="Sphere">
        <SphereData>
        <SphereCenter Value="'''+ sphereCenter +'''"/>
        <Radius Value="'''+ radius +'''"/>
        </SphereData>
        </RegionData>
        <On Value="'''+ onSphere +'''"/>
        <Above Value="'''+ outside +'''"/>
        <Below Value="'''+ inside +'''"/>
        <Tolerance Value="'''+ tolerance +'''"/>
        <MaximumCount Value="'''+ maximumNodes +'''"/>
        <ShowSurfaceNodes Value="'''+ showSurfaceNodes +'''"/>
        <CreateGroup Value="1"/>
        </NodesByRegion>'''
        simlab.execute(NodesByRegion)
        # print(NodesByRegion)
    except:
        # print(NodesByRegion)
        logging(traceback.format_exc())
    return

def FindElementsByCylinder(modelName, fromEntityType, fromEntities, topPoint, bottomPoint, radius,
    onCylinder=1, outside=1, inside=0, tolerance=0.01, maximumNodes=1000000):
    '''
        Finds elements on the cylinder or outside/inside from the specified entities. The result is in 'Show_Elements' group.
        Args:
            modelName: Model name.
            fromEntityType: Entity type of search source such as 'Body', 'Face', 'Group'
            fromEntities: Entities list or tuple of search source.
            topPoint: top point of cylinder axis. Example [1.0, 0.0, 2.0].
            bottomPoint: bottom point of cylinder axis.
            radius: radius of cylinder.
            onCylinder: Whether to find nodes on the cylinder. 1:Find, 0:Do not find.
            above: Whether to find the outside of the cylinder. 1:Find, 0:Do not find.
            below: Whether to find the inside of the cylinder. 1:Find, 0:Do not find.
            tolerance: Tolerance.
            maximumNodes: Maximum number of nodes to search.
            showSurfaceNodes: Maximum number of nodes to search. 1:Only surface, 0:Include internal nodes in the solid body.
        Setting both outside and inside to 1 at the same time is not allowed
    '''
    try:
        fromEntities = str(fromEntities).replace("'",'"')
        fromEntities = str(fromEntities).strip("[]""()")
        fromEntityType = fromEntityType.lower()

        topPoint = str(topPoint).strip("[]""()")
        bottomPoint = str(bottomPoint).strip("[]""()")
        radius = str(radius)

        onCylinder = str(onCylinder)
        outside = str(outside) 
        inside = str(inside)
        tolerance = str(tolerance)
        maximumNodes = str(maximumNodes)

        ShowElements=''' <ShowElements UUID="ebeb3013-454b-418a-9393-9d69ce183847">
        <tag Value="-1"/>
        <Name Value="Show Elements"/>
        <SupportEntities>'''

        if fromEntityType == 'group':
            ShowElements +='''
            <Group>''' + fromEntities + ''',</Group>'''
        elif fromEntityType == 'face':
            ShowElements +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Face>''' + fromEntities + ''',</Face>
            </Entities>'''
        elif fromEntityType == 'body':
            ShowElements +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Body>''' + fromEntities + ''',</Body>
            </Entities>'''
        else:
            raise ValueError('There is no implementation.') 

        ShowElements +='''
        </SupportEntities>
        <Option Value="1"/>
        <RegionData Type="Cylinder">
        <CylinderData>
            <TopPoints Value="''' + topPoint + '''"/>
            <BottomPoints Value="''' + bottomPoint + '''"/>
            <Radius Value="''' + radius + '''"/>
        </CylinderData>
        </RegionData>
        <On Value="''' + onCylinder + '''"/>
        <Above Value="''' + outside + '''"/>
        <Below Value="''' + inside + '''"/>
        <Tolerance Value="''' + tolerance + '''"/>
        <MaximumCount Value="''' + maximumNodes + '''"/>
        <CreateGroup Value="1"/>
        </ShowElements>'''
        simlab.execute(ShowElements)
    except:
        logging(traceback.format_exc())
    return


def FillHoles(modelName, entityType, entities, ignoreEdges=[], meshSize=0.0):
    '''
        Fills holes
        Args:
            modelName: Model name.
            entityType: Entity type. 'Body', 'Face', 'Edge'
            entities: Entities list or tuple.
            ignoreEdges: When entityType is Face, you can specify edges to ignore. Specify in the edge ID list.
            meshSize: If meshSize is not 0, remesh locally with given average elem size.
    '''
    try :
        entityType = entityType.lower()
        entities = str(entities).replace("'",'"')
        entities = str(entities).strip("[]""()")
        ignoreEdges = str(ignoreEdges.copy()).strip("[]""()")

        if meshSize != 0.0:
            localReMesh = '1'
            meshSize = str(meshSize)
        else:
            localReMesh = '0'
            meshSize = ''

        FillHoles=''' <FillHole CheckBox="ON" UUID="E9B9EC99-A6C1-4626-99FF-626F38A8CE4F">
        <tag Value="-1"/>
        <Name Value="FillHole3"/>
        <SupportEntities>
        <Entities>'''

        if entityType == 'body':
            FillHoles += '''
            <Model>''' + modelName + '''</Model>
            <Body>''' + entities + ''',</Body>'''
            option = '0'
        elif entityType == 'face':
            FillHoles += '''
            <Model>''' + modelName + '''</Model>
            <Face>''' + entities + ''',</Face>'''
            if len(ignoreEdges) != '':
                FillHoles += '''
                <Edge>''' + ignoreEdges + ''',</Edge>'''
            option = '1'
        elif entityType == 'edge':
            FillHoles += '''
            <Model>''' + modelName + '''</Model>
            <Edge>''' + entities + ''',</Edge>'''
            option = '2'
        else:
            raise ValueError('There is no implementation.')            

        FillHoles += '''
        </Entities>
        </SupportEntities>
        <Option Value="''' + option + '''"/>
        <Cylindercal_Face Value="0"/>
        <Single_Face Value="0"/>
        <RetainAllLoops Value="0"/>
        <FillLoopAsSeperateBody Value="0"/>
        <FillPartialLoop Value="0"/>
        <MeshSize LocalReMesh="''' + localReMesh + '''" Value="''' + meshSize + '''"/>
        </FillHole>'''
        simlab.execute(FillHoles)
    except:
        logging(traceback.format_exc())
    return

def RemoveHoles(modelName, entityType, entities, remesh=1):
    '''
        Create 'Imprint Circle' mesh control
        Args:
            modelName: Model name.
            entityType: Entity type. 'Body', 'Face'
            entities: Entities list or tuple.
            remesh: Rmesh flag. 1 or 0
    '''
    try :
        entityType = entityType.lower()
        entities = str(entities).replace("'",'"')
        entities = str(entities).strip("[]""()")

        RemoveHole = ''' <ConnectHole UUID="8393e3d3-a92c-4a40-8cc0-803b4cf2169e">
        <RibOptionType Value="0"/>
        <Entity>
        <Entities>'''

        if entityType == 'body':
            RemoveHole += '''
            <Model>T75_TOPASSY_21229_190129_imprint1_SM.gda</Model>
            <Body>''' + entities + ''',</Body>'''
        elif entityType == 'face':
            RemoveHole += '''
            <Model>''' + modelName + '''</Model>
            <Face>''' + entities + ''',</Face>'''
        else:
            raise ValueError('There is no implementation.')            

        RemoveHole += '''</Entities>
        </Entity>
        <AllRadius Value="1"/>
        <MinRadius Value="0"/>
        <MaxRadius Value="0"/>
        <LocalReMesh Value="''' + str(remesh) + '''"/>
        </ConnectHole>'''
        simlab.execute(RemoveHole)
    except:
        logging(traceback.format_exc())
    return

def MeshControl_ImprintCircle(modelName, controlName, faces, center, radius, scale=1.0, circularDivisions=20):
    '''
        Create 'Imprint Circle' mesh control.
        Args:
            modelName: Model name.
            controlName: Mesh control name.
            faces: Faces to assign mesh control. e.g. [1,2,3] or (4,5,6) or 7
            center: Coordinate of circle center. e.g. [0,0,0]
            radius: Circle radius.
            scale: Scale factor for radius. Imprint circular radius =  radius x scale
            circularDivisions: Number of element divisions of a circle
    '''
    try:
        faces = str(faces).strip("[]""()")
        x, y, z = center
        x = str(x)
        y = str(y)
        z = str(z)
        circleRadius = str(radius * scale)
        radius = str(radius)
        scale = str(scale)
        circularDivisions = str(circularDivisions)

        MeshControls=''' <MeshControl CheckBox="ON" isObject="1" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3">
        <tag Value="-1"/>
        <MeshControlName Value="''' + controlName + '''"/>
        <MeshControlType Value="Imprint Circle"/>
        <Entities>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Face>''' + faces + ''',</Face>
        </Entities>
        </Entities>
        <Reverse EntityTypes="" ModelIds="" Value=""/>
        <MeshColor Value=""/>
        <ImprintCircle>
            <CentreX Value="''' + x + '''"/>
            <CentreY Value="''' + y + '''"/>
            <CentreZ Value="''' + z + '''"/>
            <Radius Value="''' + radius + '''"/>
            <Scale Value="''' + scale + '''"/>
            <CircularRadius Value="''' + circleRadius + '''"/>
            <CircularDivisions Value="''' + circularDivisions + '''"/>
        </ImprintCircle>
        <RemoveLogo/>
        </MeshControl>'''
        simlab.execute(MeshControls)
    except:
        logging(traceback.format_exc())
    return

def MeshControl_RegionByPlane(modelName, controlName, entityType, entities, pointsOnPlane):
    '''
        Create 'Region' mesh control by plane.
        Args:
            modelName: Model name.
            controlName: Mesh control name.
            entityType: Entity type. 'Body', 'Face', 'Group'
            entities: Entity IDs list or tuple. e.g. [1,2,3], ['Body1'], ['Face_Group1','Face_Group2']
            pointsOnPlane: 4 Points on plane. e.g [[1,1,0],[-1,1,0],[-1,-1,0],[1,-1,0]]
    '''
    try:
        entityType = entityType.lower()
        entities = str(entities).replace("'",'"')
        entities = str(entities).strip("[]""()")

        p1, p2, p3, p4 = pointsOnPlane
        p1 = str(p1).strip("[]""()")
        p2 = str(p2).strip("[]""()")
        p3 = str(p3).strip("[]""()")
        p4 = str(p4).strip("[]""()")

        MeshControls =''' <MeshControl CheckBox="ON" isObject="1" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3">
        <tag Value="-1"/>
        <MeshControlName Value="''' + controlName + '''"/>
        <MeshControlType Value="Region"/>
        <Entities>'''

        if entityType == 'group':
            MeshControls +='''
            <Group>''' + entities + ''',</Group>'''
        elif entityType == 'face':
            MeshControls +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Face>''' + entities + ''',</Face>
            </Entities>'''
        elif entityType == 'body':
            MeshControls +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Body>''' + entities + ''',</Body>
            </Entities>'''
        else:
            raise ValueError('There is no implementation to delete the specified type.')

        MeshControls +='''
        </Entities>
        <Reverse EntityTypes="" ModelIds="" Value=""/>
        <MeshColor Value=""/>
        <RegionMeshControl>
        <RegionType Value="2"/>
        <DefineInsideRegion Value="0"/>
        <AverageElementSize Value="0"/>
        <MinElemSize Value="0"/>
        <MaxAnglePerElement Value="45"/>
        <CurvatureMinElemSize Value="0"/>
        <AspectRatio Value="10"/>
        <SurfaceMeshGrading Value="1.5"/>
        <BreakOptions Value="1"/>
        <RType Value="546"/>
        <CreateInternalFace Value="0"/>
        <CuboidRegData/>
        <CYlRegData/>
        <PlaneRegData>
            <Plane PlanePoints="''' + p1 + ''',''' + p2 + ''',''' + p3 + ''',''' + p4 + ''',"/>
        </PlaneRegData>
        <SphereRegData/>
        <ConeRegData/>
        </RegionMeshControl>
        </MeshControl>'''
        simlab.execute(MeshControls)
    except:
        logging(traceback.format_exc())
    return


def MeshControl_RegionByCylinder(modelName, controlName, entityType, entities, topPoint, bottomPoint, radius, averageElementSize,
    minElemSize=None, curvatureMinElemSize=None, height=None):
    '''
        Create 'Region' mesh control by plane.
        Args:
            modelName: Model name.
            controlName: Mesh control name.
            entityType: Entity type. 'Body', 'Face', 'Group'
            entities: Entity IDs list or tuple. e.g. [1,2,3], ['Body1'], ['Face_Group1','Face_Group2']
            topPoint: Top point of cylinder center axis
            bottomPoint: Top point of cylinder center axis
            radius: Radius of cylinder
            averageElementSize: Average element size
            minElemSize: Minimum mesh size. If minElemSize is None, thminElemSizeis is "0.1 x averageElementSize" same as GUI
            curvatureMinElemSize: Curvature Minimum Element Size. If curvatureMinElemSize is None, curvatureMinElemSize is "0.5 x averageElementSize" same as GUI
            height: Height of cylinder. If height is None, height is distance between topPoint and bottomPoint.
    '''
    try:
        entityType = entityType.lower()
        entities = str(entities).replace("'",'"')
        entities = str(entities).strip("[]""()")

        top = np.array(topPoint)
        bottom = np.array(bottomPoint)
        vec = bottom - top
        center = (top + bottom) * 0.5
        distance = np.linalg.norm(vec)
        axis = vec / distance

        if minElemSize == None:
            minElemSize = averageElementSize * 0.1
        if curvatureMinElemSize == None:
            curvatureMinElemSize = averageElementSize * 0.5
        if height == None:
            height = distance

        axis = str(list(axis)).strip("[]")    
        center = str(list(center)).strip("[]")
        radius = str(radius)
        height = str(height)
        averageElementSize = str(averageElementSize)   
        minElemSize = str(minElemSize)   
        curvatureMinElemSize = str(curvatureMinElemSize)   
        
        MeshControls = ''' <MeshControl CheckBox="ON" isObject="1" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3">
        <tag Value="-1"/>
        <MeshControlName Value="''' + controlName + '''"/>
        <MeshControlType Value="Region"/>
        <Entities>'''

        if entityType == 'group':
            MeshControls +='''
            <Group>''' + entities + ''',</Group>'''
        elif entityType == 'face':
            MeshControls +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Face>''' + entities + ''',</Face>
            </Entities>'''
        elif entityType == 'body':
            MeshControls +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Body>''' + entities + ''',</Body>
            </Entities>'''
        else:
            raise ValueError('There is no implementation to delete the specified type.')

        MeshControls += '''
        </Entities>
        <Reverse EntityTypes="" ModelIds="" Value=""/>
        <MeshColor Value=""/>
        <RegionMeshControl>
        <RegionType Value="1"/>
        <DefineInsideRegion Value="1"/>
        <AverageElementSize Value="'''+ averageElementSize +'''"/>
        <MinElemSize Value="''' + minElemSize + '''"/>
        <MaxAnglePerElement Value="45"/>
        <CurvatureMinElemSize Value="''' + curvatureMinElemSize + '''"/>
        <AspectRatio Value="10"/>
        <SurfaceMeshGrading Value="1.5"/>
        <BreakOptions Value="1"/>
        <RType Value="164"/>
        <CreateInternalFace Value="0"/>
        <CuboidRegData/>
        <CYlRegData>
            <Cyl CylPoints="''' + axis + ',' + center + ',' + radius + ',' + height + ''',"/>
        </CYlRegData>
        <PlaneRegData/>
        <SphereRegData/>
        <ConeRegData/>
        </RegionMeshControl>
        </MeshControl>'''
        simlab.execute(MeshControls)
    except:
        logging(traceback.format_exc())
    return

def SurfaceMeshTri(modelName, entityType, entities, elementType, averageElementSize, aspectRatio = 10):
    '''
        Create triangle surface mesh.
        Args:
            modelName: Model name.
            entityType: Entity type. 'Body', 'Face', 'Group'
            entities: Entity IDs list or tuple. e.g. [1,2,3], ['Body1'], ['Face_Group1','Face_Group2']
            elementType: Element type. 'Tri3', 'Tri6'
            averageElementSize: Average element size
            aspectRatio: aspectRatio set 10 by default
        
        minElem = averageElementSize/ aspectRatio
        curvatureMinimumElementSize = averageElementSize / 2
    '''
    try:
        entityType = entityType.lower()
        entities = str(entities).replace("'",'"')
        entities = str(entities).strip("[]""()")

        
        minimumElementSize = str(averageElementSize / aspectRatio)
        curvatureMinimumElementSize = str(averageElementSize/2)
        averageElementSize = str(averageElementSize)
        aspectRatio = str(aspectRatio)
          

        SurfaceMesh=''' <SurfaceMesh UUID="08df0ff6-f369-4003-956c-82781326c876">
        <tag Value="-1"/>
        <SurfaceMeshType Value="Tri"/>
        <SupportEntities>'''

        if entityType == 'group':
            SurfaceMesh +='''
            <Group>''' + entities + ''',</Group>'''
        elif entityType == 'face':
            SurfaceMesh +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Face>''' + entities + ''',</Face>
            </Entities>'''
        elif entityType == 'body':
            SurfaceMesh +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Body>''' + entities + ''',</Body>
            </Entities>'''
        else:
            raise ValueError('There is no implementation to delete the specified type.')

        SurfaceMesh += '''
        </SupportEntities>
        <Tri>
        <ElementType Value="''' + elementType + '''"/>
        <AverageElementSize Value="'''+ averageElementSize + '''" Checked="1"/>
        <MaximumElementSize Value="4.242" Checked="0"/>
        <MinimumElementSize Value="''' + minimumElementSize + '''"/>
        <GradeFactor Value="1.5"/>
        <MaximumAnglePerElement Value="45"/>
        <CurvatureMinimumElementSize Value="''' + curvatureMinimumElementSize + '''"/>
        <AspectRatio Value="'''+ aspectRatio +'''"/>
        <AdvancedOptions>
            <IdentifyFeaturesAndMesh Checked="0"/>
            <ImprintMeshing Checked="0"/>
            <BetterGeometryApproximation Checked="0"/>
            <CoarseMesh Checked="0"/>
            <CoarseMesh_UseExistingNodes Checked="0"/>
            <CreateMeshInNewModel Checked="1"/>
            <UserDefinedModelName Value=""/>
            <Tri6WithStraightEdges Checked="0"/>
            <ImproveSkewAngle Value="0"/>
            <MappedMesh Value="0"/>
            <MeshPattern Value="0"/>
        </AdvancedOptions>
        </Tri>
        </SurfaceMesh>'''
        simlab.execute(SurfaceMesh)
    except:
        logging(traceback.format_exc())
    return

def SurfaceMeshSLQuad(modelName, entityType, entities, averageElementSize, minimumElementSize=None):
    '''
        Create SL Quad surface mesh
        Args:
            modelName: Model name.
            entityType: Entity type. 'Body', 'Face', 'Group'
            entities: Entity IDs list or tuple. e.g. [1,2,3], ['Body1'], ['Face_Group1','Face_Group2']
            averageElementSize: Average mesh size.
            minimumElementSize: Minimum mesh size. If minimumElementSize is None, minimumElementSize is "0.1 x maximumElementSize" same as GUI.
    '''
    try:
        entityType = entityType.lower()
        entities = str(entities).replace("'",'"')
        entities = str(entities).strip("[]""()")

        if minimumElementSize == None:
            minimumElementSize = averageElementSize * 0.1
        
        averageElementSize = str(averageElementSize)   
        minimumElementSize = str(minimumElementSize)

        SurfaceMesh=''' <SurfaceMesh UUID="08df0ff6-f369-4003-956c-82781326c876">
        <tag Value="-1"/>
        <SurfaceMeshType Value="Quad"/>
        <SupportEntities>'''

        if entityType == 'group':
            SurfaceMesh +='''
            <Group>''' + entities + ''',</Group>'''
        elif entityType == 'face':
            SurfaceMesh +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Face>''' + entities + ''',</Face>
            </Entities>'''
        elif entityType == 'body':
            SurfaceMesh +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Body>''' + entities + ''',</Body>
            </Entities>'''
        else:
            raise ValueError('There is no implementation to delete the specified type.')

        SurfaceMesh += '''
        </SupportEntities>
        <Quad Type="SLQuad">
        <AverageElementSize Value="''' + averageElementSize + '''"/>
        <MinimumElementSize Value="''' + minimumElementSize + '''"/>
        <MeshType Value="QuadDominant"/>
        <ProjectToSelectedEntities Checked=""/>
        </Quad>
        </SurfaceMesh>'''
        simlab.execute(SurfaceMesh)
    except:
        logging(traceback.format_exc())
    return


def SurfaceMeshHMQuad(modelName, entityType, entities, maximumElementSize, minimumElementSize=None, maximumDeviation=None):
    '''
        Create HM quad surface mesh. This option works based on the “Edge deviation” method of Hyper Mesh.
        Args:
            modelName: Model name.
            entityType: Entity type. 'Body', 'Face', 'Group'
            entities: Entity IDs list or tuple. e.g. [1,2,3], ['Body1'], ['Face_Group1','Face_Group2']
            maximumElementSize: Maximum mesh size.
            minimumElementSize: Minimum mesh size. If minimumElementSize is None, minimumElementSize is "0.1 x maximumElementSize" same as GUI.
            maximumDeviation: Maximum deviation. If maximumDeviation is None, maximumDeviation is "0.2 x maximumElementSize" same as GUI.
    '''
    try:
        entityType = entityType.lower()
        entities = str(entities).replace("'",'"')
        entities = str(entities).strip("[]""()")

        if minimumElementSize == None:
            minimumElementSize = maximumElementSize * 0.1
        if maximumDeviation == None:
            maximumDeviation = maximumElementSize * 0.5
        
        maximumElementSize = str(maximumElementSize)   
        minimumElementSize = str(minimumElementSize)   
        maximumDeviation = str(maximumDeviation)   

        SurfaceMesh=''' <SurfaceMesh UUID="08df0ff6-f369-4003-956c-82781326c876">
        <tag Value="-1"/>
        <SurfaceMeshType Value="Quad"/>
        <SupportEntities>'''

        if entityType == 'group':
            SurfaceMesh +='''
            <Group>''' + entities + ''',</Group>'''
        elif entityType == 'face':
            SurfaceMesh +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Face>''' + entities + ''',</Face>
            </Entities>'''
        elif entityType == 'body':
            SurfaceMesh +='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Body>''' + entities + ''',</Body>
            </Entities>'''
        else:
            raise ValueError('There is no implementation to delete the specified type.')

        SurfaceMesh += '''
        </SupportEntities>
        <Quad Type="HMQuad">
        <MaximumElementSize Value="''' + maximumElementSize + '''"/>
        <MinimumElementSize Value="''' + minimumElementSize + '''"/>
        <MaximumDeviation Value="''' + maximumDeviation + '''"/>
        <MaximumAngle Value="45"/>
        <MeshType Value="Mixed"/>
        <FeatureAngle Value="45"/>
        <VertexAngle Value="45"/>
        <AlignedMesh Checked="1"/>
        <ProjectToSelectedEntities Checked="0"/>
        </Quad>
        </SurfaceMesh>'''
        simlab.execute(SurfaceMesh)
    except:
        logging(traceback.format_exc())
    return

def VolumeMesh(modelName, entityType, entities, elementType, averageElemSize):
    '''
        Create volume mesh.
        Args:
            modelName: Model name.
            entityType: Entity type. 'Body', 'Group'
            entities: Entity list or tuple. e.g. ['Body1'], ['Body_Group1', 'Body_Group2'] 
            elementType: Element type. 'Tet4', 'Tet10'
            averageElemSize: Average element size.
    '''
    try:
        entityType = entityType.lower()
        entities = str(entities).replace("'",'"')
        entities = str(entities).strip("[]""()")
        averageElemSize = str(averageElemSize)

        VolumeMesh=''' <VolumeMesher UUID="83822e68-12bb-43b9-b2ac-77e0b9ea5149">
        <tag Value="-1"/>
        <Name Value="VolumeMesher1"/>
        <SupportEntities>'''

        if entityType == 'body':
            VolumeMesh+='''
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Body>''' + entities + ''',</Body>
            </Entities>'''
        elif entityType == 'group':
            VolumeMesh+='''
            <Group>''' + entities + ''',</Group>'''
        else:
            raise ValueError('There is no implementation to delete the specified type.')

        VolumeMesh += '''
        </SupportEntities>
        <MeshType Value="''' + elementType + '''"/>
        <AverageElemSize Value="''' + averageElemSize + '''"/>
        <MinimumElementSize Value="0"/>
        <AspectRatio Value="0"/>
        <MaxElemSize Value="0" Checked="0"/>
        <InternalGrading Value="2"/>
        <MinQuality Value="0.1"/>
        <LinearQuality Value="0"/>
        <MaxQuality Value="1"/>
        <QuadMinQuality Value="0.001"/>
        <QuadQuality Value="0"/>
        <QuadMaxQuality Value="1"/>
        <CadBody Value="0"/>
        <NumberofLayers Value="1" Checked="1"/>
        <LayerThickness Value="0" Checked="0"/>
        <EndFaces/>
        <AdvancedOptions>
        <MeshDensity Value="0"/>
        <CreateVol Value="0"/>
        <OutputModelName Value=""/>
        <Assembly Value="0"/>
        <PreserveFaceMesh Value="0"/>
        <MeshAsSingleBody Value="0"/>
        <Retain2DSurfaceBodies Value="0"/>
        <PreserveSurfaceSkew Value="55" Checked="0"/>
        <MixedMesh Value="0"/>
        </AdvancedOptions>
        </VolumeMesher>'''
        simlab.execute(VolumeMesh)
    except:
        logging(traceback.format_exc())
    return

def DeleteSolidElements(modelName, bodies):
    '''
        Create volume mesh.
        modelName: Model name.
        bodies: Body list or tuple. e.g. ['Body1'], ['Body_Group1', 'Body_Group2']
    '''
    try:
        bodies = str(bodies).replace("'",'"')
        bodies = str(bodies).strip("[]""()")

        DeleteSolidElements=''' <DeleteSolidElements CheckBox="ON" UUID="c86ce926-2412-4325-a87f-ee6cb66c4de3">
        <tag Value="-1"/>
        <Name Value=""/>
        <SupportEntities>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Body>''' + bodies + ''',</Body>
        </Entities>
        </SupportEntities>
        <Output/>
        </DeleteSolidElements>'''
        simlab.execute(DeleteSolidElements)
    except:
        logging(traceback.format_exc())
    return


def CreateRBE(modelName, rbeName, slaveEtityType, slaveEntityList, masterNodeID, ignoreMidNodes=0, radiusLimit=0.0):
    '''
        Create RBE elements.
        Args:
            modelName: Model name.
            rbeName: RBE name.
            slaveEtityType: Slave entity type. e.g. 'Face'
            slaveEntityList: Slave entities list or tuple. e.g [1, 2, 3]
            masterNodeID: Master node ID.
            ignoreMidNodes: Whether to ignore mid nodes. 0: Do not ignore. 1: Ignore
            radiusLimit: Limit radius to create RBE. If RadiusLimit is 0, This function is OFF.        
    '''
    try:
        slaveEtityType = slaveEtityType.lower()
        slaveEntityList = str(slaveEntityList).replace("'",'"')
        slaveEntityList = str(slaveEntityList).strip("[]""()")

        masterNodeList = [masterNodeID]
        masterNodeList = str(masterNodeList).replace("'",'"')
        masterNodeList = str(masterNodeList).strip("[]""()")

        masterNodeID = str(masterNodeID)

        radiusLimitCheck = 0
        if radiusLimit != 0.0:
            radiusLimitCheck == 1

        CreateRBE=''' <RBE CheckBox="ON" UUID="27FFA2F5-6388-4d38-A5FA-6DCC883C1094">
        <tag Value="-1"/>
        <Name Value="'''+rbeName+'''"/>
        <InputEntities>
        <Entities>'''

        if slaveEtityType == 'face':
            CreateRBE += '''
            <Model>'''+modelName+'''</Model>
            <Face>'''+slaveEntityList+''',</Face>'''
        elif slaveEtityType == 'edge':
            CreateRBE += '''
            <Model>'''+modelName+'''</Model>
            <Edge>'''+slaveEntityList+''',</Edge>'''
        elif slaveEtityType == 'body':
            CreateRBE += '''
            <Model>'''+modelName+'''</Model>
            <Body>'''+slaveEntityList+''',</Body>'''
        else:
            raise ValueError('There is no implementation to delete the specified type.')

        CreateRBE += '''
        </Entities>
        </InputEntities>
        <Group Value=""/>
        <CenterSupportNodes>
        <Entities>
            <Model>'''+modelName+'''</Model>
            <Node>'''+masterNodeList+''',</Node>
        </Entities>
        </CenterSupportNodes>
        <CenterSupportEdges EntityTypes="" ModelIds="" Value=""/>
        <BodyAllNodes Value="1"/>
        <BodyFewNodes Value="0"/>
        <CenterNodeId Value="'''+masterNodeID+'''"/>
        <ConnectionType Value="0"/>
        <RadiusLimit Check="''' + str(radiusLimitCheck) + '''" Value="''' + str(radiusLimit) + '''"/>
        <CenterNodeSupport Value="1"/>
        <IgnoreMidNodes Value="''' + str(ignoreMidNodes) + '''"/>
        <CreateRBE_eachRegion Value="0"/>
        <Output/>
        </RBE>'''
        simlab.execute(CreateRBE)
    except:
        logging(traceback.format_exc())
    return

def ManualRBE(modelName, rbeName, independentNodeID, dependentNodeList):
    '''
        Create RBE elements by manual.
        Args:
            modelName: Model name.
            rbeName: RBE name.
            independentNodeID: independent node ID
            dependentNodeList: dependent nodes list or tuple. e.g [1,2,3]
    '''
    try:
        masterID = str(independentNodeID)
        slaveList = str(dependentNodeList).replace("'",'"')
        slaveList = str(slaveList).strip("[]""()")

        ManualRBE=''' <ManualRBE CheckBox="ON" UUID="80E2032A-27AE-493a-9162-844BD2CC0823">
        <tag Value="-1"/>
        <Name Value="''' + rbeName + '''"/>
        <Independent>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Node>''' + masterID + ''',</Node>
        </Entities>
        </Independent>
        <Dependent>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Node>''' + slaveList + ''',</Node>
        </Entities>
        </Dependent>
        <Type Value="Nodes"/>
        <Output/>
        </ManualRBE>'''
        simlab.execute(ManualRBE)
    except:
        logging(traceback.format_exc())
    return


def CreateBar(modelName, barName, startNodeID, endNodeID ):
    '''
        Create BAR elements.
        Args:
            modelName: Model name.
            barName: BAR name.
            startNodeID: start node ID
            endNodeID: end node ID
    '''
    try:
        startNodeID = str(startNodeID)
        endNodeID = str(endNodeID)

        CreateBar=''' <Bar CheckBox="ON" UUID="741D7A3A-1CD4-4051-ABBA-CD1603D1C545">
        <tag Value="-1"/>
        <Name Value="''' + barName + '''"/>
        <SupportEntities>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Node>''' + startNodeID + ''',''' + endNodeID + ''',</Node>
        </Entities>
        </SupportEntities>
        <Output/>
        </Bar>'''
        simlab.execute(CreateBar)
    except:
        logging(traceback.format_exc())
    return


def BooleanDifference(groupType, group1, group2, resultGroup):
    '''
        Takes difference of boolean arithmetic operation.
        Args:
            groupType: Group type. e.g. 'Face'
            group1: Name of group1.
            group2: Name of group2.
            resultGroup Name of result group
    '''
    try:
        BooleanGroup=''' <BooleanGroup UUID="5da8b41c-208b-4968-a282-9763c2258878">
        <tag Value="-1"/>
        <Name Value=''' + '"' + resultGroup + '"'  + '''/>
        <Type Value="''' + groupType + '''"/>
        <UseExtisingGroup Value=""/>
        <Operation Value="Difference"/>
        <GroupList1 Value=''' + '"' + group1 + ',"'  + '''/>
        <GroupList2 Value=''' + '"' + group2 + ',"'  + '''/>
        </BooleanGroup>'''
        simlab.execute(BooleanGroup)
    except:
        logging(traceback.format_exc())
    return

def BooleanIntersection(groupType, group1, group2, resultGroup):
    '''
        Takes intersection of boolean arithmetic operation.
        Args:
            groupType: Group type.
            group1: Name of group1.
            group2: Name of group2.
            resultGroup: Name of result group
    '''
    try:
        BooleanGroup=''' <BooleanGroup UUID="5da8b41c-208b-4968-a282-9763c2258878">
        <tag Value="-1"/>
        <Name Value=''' + '"' + resultGroup + '"'  + '''/>
        <Type Value="''' + groupType + '''"/>
        <UseExtisingGroup Value=""/>
        <Operation Value="Intersection"/>
        <GroupList1 Value=''' + '"' + group1 + ',"'  + '''/>
        <GroupList2 Value=''' + '"' + group2 + ',"'  + '''/>
        </BooleanGroup>'''
        simlab.execute(BooleanGroup)
    except:
        logging(traceback.format_exc())
    return


def BooleanUnion(groupType, group1, group2, resultGroup):
    '''
        Takes union of boolean arithmetic operation.
        Args:
            groupType: Group type.
            group1: Name of group1.
            group2: Name of group2.
            resultGroup: Name of result group
    '''
    try:
        BooleanGroup=''' <BooleanGroup UUID="5da8b41c-208b-4968-a282-9763c2258878">
        <tag Value="-1"/>
        <Name Value=''' + '"' + resultGroup + '"'  + '''/>
        <Type Value="''' + groupType + '''"/>
        <UseExtisingGroup Value=""/>
        <Operation Value="Union"/>
        <GroupList1 Value=''' + '"' + group1 + ',"'  + '''/>
        <GroupList2 Value=''' + '"' + group2 + ',"'  + '''/>
        </BooleanGroup>'''
        simlab.execute(BooleanGroup)
    except:
        logging(traceback.format_exc())
    return

def CreateMaterial_SolidMetalIsotropic(materialName, materialID, density=7.8e-9, youngs_modulus=208000, poissons_ratio=0.30):
    '''
        Creates a material (Solid, Metal, Isotropic).
        Args:
            materialName: Material name
            materialID: Material ID
            density: Density
            youngs_modulus: Youngs modulus
            poissons_ratio: Poissons ratio
    '''
    try:
        materialID = str(materialID)
        density = str(density)
        youngs_modulus = str(youngs_modulus)
        poissons_ratio = str(poissons_ratio)

        Material=''' <Material UUID="dd7920e8-5d0f-477b-bc7e-037a04a7ed03">
        <tag Value="-1"/>
        <Name Value="''' + materialName + '''"/>
        <MaterialId Value="''' + materialID + '''"/>
        <Category Value="Solid"/>
        <Class Value="Metal"/>
        <Model Value="Isotropic"/>
        <TableData>
        <Mechanical_Properties>
            <Elastic>
            <ITEM DISPLAYNAME="Density" KEY="Density">
            <COLUMN DATATYPE="DOUBLE" VALUE="''' + density + '''"/>
            </ITEM>
            <ITEM DISPLAYNAME="Youngs_modulus" KEY="Youngs_modulus">
            <COLUMN DATATYPE="DOUBLE" VALUE="''' + youngs_modulus + '''"/>
            <COLUMN DATATYPE="FIELD_TABLE" VALUE="none"/>
            </ITEM>
            <ITEM DISPLAYNAME="Poissons_ratio" KEY="Poissons_ratio">
            <COLUMN DATATYPE="DOUBLE" VALUE="''' + poissons_ratio + '''"/>
            <COLUMN DATATYPE="FIELD_TABLE" VALUE="none"/>
            </ITEM>
            <ITEM DISPLAYNAME="Shear_modulus" KEY="Shear_modulus"/>
            <ITEM DISPLAYNAME="Thermal_Expansion" KEY="Thermal_Expansion">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
            <COLUMN DATATYPE="FIELD_TABLE" VALUE="none"/>
            </ITEM>
            <ITEM DISPLAYNAME="Reference_Temperature" KEY="Reference_Temperature">
            <COLUMN DATATYPE="DOUBLE" VALUE="20"/>
            </ITEM>
            <ITEM DISPLAYNAME="Damping_coefficient" KEY="Damping_coefficient"/>
            <ITEM DISPLAYNAME="Stress_Tension" KEY="Stress_Tension">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.00"/>
            </ITEM>
            <ITEM DISPLAYNAME="Stress_Compression" KEY="Stress_Compression">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.00"/>
            </ITEM>
            <ITEM DISPLAYNAME="Stress_Shear" KEY="Stress_Shear">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.00"/>
            </ITEM>
            <ITEM DISPLAYNAME="Mat_Cord_Sys" KEY="Mat_Cord_Sys">
            <COLUMN DATATYPE="DOUBLE" VALUE="0"/>
            </ITEM>
            </Elastic>
            <Plastic>
            <ITEM DISPLAYNAME="Yield_Stress" KEY="Yield_Stress">
            <COLUMN DATATYPE="FIELD_TABLE" VALUE="none"/>
            </ITEM>
            <ITEM DISPLAYNAME="Yield_Criterion" KEY="Yield_Criterion">
            <COLUMN DATATYPE="INDEX" INDEX="0" LIST="VMISES"/>
            </ITEM>
            <ITEM DISPLAYNAME="Hardening_Param" KEY="Hardening_Param">
            <COLUMN DATATYPE="DOUBLE" VALUE="1.00"/>
            </ITEM>
            <ITEM DISPLAYNAME="Work_Hardening_Slope" KEY="Work_Hardening_Slope">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.1"/>
            </ITEM>
            <ITEM DISPLAYNAME="Hardening_Rule" KEY="Hardening_Rule">
            <COLUMN DATATYPE="INDEX" INDEX="0" LIST="Isotropic Hardening"/>
            <COLUMN DATATYPE="DOUBLE" VALUE="0.15"/>
            </ITEM>
            <ITEM DISPLAYNAME="Initial_yield_point" KEY="Initial_yield_point">
            <COLUMN DATATYPE="DOUBLE" VALUE="208000"/>
            </ITEM>
            </Plastic>
            <Visco_Plastic>
            <ITEM DISPLAYNAME="Creep_Temperature_Exponent" KEY="Creep_Temperature_Exponent"/>
            <ITEM DISPLAYNAME="Creep_Stress_Exponent" KEY="Creep_Stress_Exponent"/>
            <ITEM DISPLAYNAME="Creep_Strain_Exponent" KEY="Creep_Strain_Exponent"/>
            <ITEM DISPLAYNAME="Creep_Time_Exponent" KEY="Creep_Time_Exponent"/>
            </Visco_Plastic>
        </Mechanical_Properties>
        <Thermal_Properties>
            <ITEM DISPLAYNAME="Thermal_conductivity" KEY="Thermal_conductivity">
            <COLUMN DATATYPE="DOUBLE" VALUE="4.98100E-02"/>
            <COLUMN DATATYPE="FIELD_TABLE" VALUE="none"/>
            </ITEM>
            <ITEM DISPLAYNAME="Heat_capacity" KEY="Heat_capacity">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.5"/>
            <COLUMN DATATYPE="FIELD_TABLE" VALUE="none"/>
            </ITEM>
            <ITEM DISPLAYNAME="Free_Convection" KEY="Free_Convection">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.00"/>
            </ITEM>
            <ITEM DISPLAYNAME="Dynamic_Viscosity" KEY="Dynamic_Viscosity">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.00"/>
            </ITEM>
            <ITEM DISPLAYNAME="Heat_Generation" KEY="Heat_Generation">
            <COLUMN DATATYPE="DOUBLE" VALUE="1.00"/>
            </ITEM>
            <ITEM DISPLAYNAME="Reference_Enthalpy" KEY="Reference_Enthalpy">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.00"/>
            </ITEM>
            <ITEM DISPLAYNAME="TCH" KEY="TCH">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.00"/>
            </ITEM>
            <ITEM DISPLAYNAME="TDELTA" KEY="TDELTA">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.00"/>
            </ITEM>
            <ITEM DISPLAYNAME="QLAT" KEY="QLAT">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.00"/>
            </ITEM>
        </Thermal_Properties>
        <Fatigue_Properties>
            <Static_parameters>
            <ITEM DISPLAYNAME="Fatigue_computation_method" KEY="Fatigue_computation_method">
            <COLUMN DATATYPE="INDEX" INDEX="0" LIST="Stress Life"/>
            </ITEM>
            <ITEM DISPLAYNAME="Yield_Strength" KEY="Yield_Strength"/>
            <ITEM DISPLAYNAME="Ultimate_Tensile_Strength" KEY="Ultimate_Tensile_Strength"/>
            <ITEM DISPLAYNAME="Units" KEY="Units">
            <COLUMN DATATYPE="INDEX" INDEX="0" LIST="MPa"/>
            </ITEM>
            </Static_parameters>
            <Stress_Life_parameters>
            <ITEM DISPLAYNAME="Fatigue_strength_coefficient" KEY="Fatigue_strength_coefficient_stress"/>
            <ITEM DISPLAYNAME="First_Fatigue_strength_Exponent" KEY="First_Fatigue_strength_Exponent"/>
            <ITEM DISPLAYNAME="Endurance_Cycle_Limit_or_Transition_Point" KEY="Endurance_Cycle_Limit_or_Transition_Point">
            <COLUMN DATATYPE="DOUBLE" VALUE="1000.0"/>
            </ITEM>
            <ITEM DISPLAYNAME="Second_Fatigue_strength_Exponent" KEY="Second_Fatigue_strength_Exponent">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
            </ITEM>
            <ITEM DISPLAYNAME="Fatigue_Limit" KEY="Fatigue_Limit"/>
            <ITEM DISPLAYNAME="Standard_Error_of_Log" KEY="Standard_Error_of_Log">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
            </ITEM>
            <ITEM DISPLAYNAME="Findley_Constant" KEY="Findley_Constant">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.3"/>
            </ITEM>
            <ITEM DISPLAYNAME="Region_Layer" KEY="Region_Layer_stress">
            <COLUMN DATATYPE="INDEX" INDEX="0" LIST="Worst"/>
            </ITEM>
            <ITEM DISPLAYNAME="Material_Surface_Finish" KEY="Material_Surface_Finish_Stress">
            <COLUMN DATATYPE="INDEX" INDEX="0" LIST="None"/>
            <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
            </ITEM>
            <ITEM DISPLAYNAME="Material_Surface_Treatment" KEY="Material_Surface_Treatment_Stress">
            <COLUMN DATATYPE="INDEX" INDEX="0" LIST="None"/>
            <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
            </ITEM>
            <ITEM DISPLAYNAME="Fatigue_Strength_Reduction_Factor" KEY="Fatigue_Strength_Reduction_Factor_Stress">
            <COLUMN DATATYPE="DOUBLE" VALUE="1.0"/>
            </ITEM>
            </Stress_Life_parameters>
            <Strain_Life_parameters>
            <ITEM DISPLAYNAME="Fatigue_strength_coefficient" KEY="Fatigue_strength_coefficient_strain"/>
            <ITEM DISPLAYNAME="Fatigue_strength_exponent" KEY="Fatigue_strength_exponent"/>
            <ITEM DISPLAYNAME="Fatigue_ductility_exponent" KEY="Fatigue_ductility_exponent"/>
            <ITEM DISPLAYNAME="Fatigue_ductility_coefficient" KEY="Fatigue_ductility_coefficient"/>
            <ITEM DISPLAYNAME="Cyclic_strain_hardening_exponent" KEY="Cyclic_strain_hardening_exponent"/>
            <ITEM DISPLAYNAME="Cyclic_strength_coefficient" KEY="Cyclic_strength_coefficient"/>
            <ITEM DISPLAYNAME="Reversal_Limit_Of_Endurance" KEY="Reversal_Limit_Of_Endurance">
            <COLUMN DATATYPE="DOUBLE" VALUE="2.0E8"/>
            </ITEM>
            <ITEM DISPLAYNAME="Standard_Error_of_Log_Elastic" KEY="Standard_Error_of_Log_Elastic">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
            </ITEM>
            <ITEM DISPLAYNAME="Standard_Error_of_Log_Plastic" KEY="Standard_Error_of_Log_Plastic">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
            </ITEM>
            <ITEM DISPLAYNAME="Shear_Fatigue_Strength_coefficient" KEY="Shear_Fatigue_Strength_coefficient"/>
            <ITEM DISPLAYNAME="Shear_Fatigue_Ductility_coefficient" KEY="Shear_Fatigue_Ductility_coefficient"/>
            <ITEM DISPLAYNAME="Shear_Fatigue_Strength_exponent" KEY="Shear_Fatigue_Strength_exponent"/>
            <ITEM DISPLAYNAME="Shear_Fatigue_Ductility_exponent" KEY="Shear_Fatigue_Ductility_exponent"/>
            <ITEM DISPLAYNAME="Strength_coefficient_factor" KEY="Strength_coefficient_factor">
            <COLUMN DATATYPE="DOUBLE" VALUE="1.2"/>
            </ITEM>
            <ITEM DISPLAYNAME="Exponent_coefficient_factor" KEY="Exponent_coefficient_factor">
            <COLUMN DATATYPE="DOUBLE" VALUE="1.0"/>
            </ITEM>
            <ITEM DISPLAYNAME="Maximum_Strain_value" KEY="Maximum_Strain_value">
            <COLUMN DATATYPE="DOUBLE" VALUE="1.002"/>
            </ITEM>
            <ITEM DISPLAYNAME="Fatemi_Socie_Constant" KEY="Fatemi_Socie_Constant">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.3"/>
            </ITEM>
            <ITEM DISPLAYNAME="Brown_Miller_Constant" KEY="Brown_Miller_Constant">
            <COLUMN DATATYPE="DOUBLE" VALUE="1.0"/>
            </ITEM>
            <ITEM DISPLAYNAME="Region_Layer" KEY="Region_Layer_strain">
            <COLUMN DATATYPE="INDEX" INDEX="0" LIST="Worst"/>
            </ITEM>
            <ITEM DISPLAYNAME="Material_Surface_Finish" KEY="Material_Surface_Finish_Strain">
            <COLUMN DATATYPE="INDEX" INDEX="0" LIST="None"/>
            <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
            </ITEM>
            <ITEM DISPLAYNAME="Material_Surface_Treatment" KEY="Material_Surface_Treatment_Strain">
            <COLUMN DATATYPE="INDEX" INDEX="0" LIST="None"/>
            <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
            </ITEM>
            <ITEM DISPLAYNAME="Fatigue_Strength_Reduction_Factor" KEY="Fatigue_Strength_Reduction_Factor_Strain">
            <COLUMN DATATYPE="DOUBLE" VALUE="1.0"/>
            </ITEM>
            </Strain_Life_parameters>
            <Factor_of_Safety>
            <ITEM DISPLAYNAME="Torsion_fatigue_limit" KEY="Torsion_fatigue_limit">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
            <COLUMN DATATYPE="FIELD_TABLE" VALUE="none"/>
            </ITEM>
            <ITEM DISPLAYNAME="Hydrostatic_stress_sensitivity" KEY="Hydrostatic_stress_sensitivity"/>
            <ITEM DISPLAYNAME="Safe_zone_angle" KEY="Safe_zone_angle">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
            </ITEM>
            <ITEM DISPLAYNAME="Shear_Threshold_Safezone" KEY="Shear_Threshold_Safezone">
            <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
            </ITEM>
            <ITEM DISPLAYNAME="Region_Layer" KEY="Region_Layer">
            <COLUMN DATATYPE="INDEX" INDEX="0" LIST="Worst"/>
            </ITEM>
            </Factor_of_Safety>
        </Fatigue_Properties>
        </TableData>
        </Material>'''
        simlab.execute(Material)
    except:
        logging(traceback.format_exc())
    return

def CreateProperty_SolidIsotropic(propertyName, propertyID, materialName, modelName, bodies):
    '''
        Creates a property (Solid, Isotropic).
        Args:
            propertyName: Property name
            propertyID: Property ID
            materialName: Material name
            modelName: Model name
            bodies: Body list or tuple e.g. ['Body 1']
    '''
    try:
        propertyID = str(propertyID)
        bodies = str(bodies).replace("'",'"')
        bodies = str(bodies).strip("[]""()")

        AnalysisProperty=''' <Property UUID="FAABD80A-7FA2-4d2a-961B-BFA06A361A4C">
        <tag Value="-1"/>
        <Name Value="''' + propertyName + '''"/>
        <Dimension Value="Solid"/>
        <Type Value="Isotropic"/>
        <ID Value="3"/>
        <Material Value="''' + materialName + '''"/>
        <SupportEntities>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Body>"''' + bodies + '''",</Body>
        </Entities>
        </SupportEntities>
        <UseExistingPropertyCheck Value="0"/>
        <CoordSystem Value=""/>
        <TableData>
        <WriteMaterial Type="2" Value="1"/>
        <Abaqus_Element_Type Type="3" Value="0"/>
        <OptiStruct_Explicit_Element_Type Type="3" Value="0"/>
        <Ansys_Element_Type Type="3" Value="0"/>
        </TableData>
        <Composite/>
        </Property>'''
        simlab.execute(AnalysisProperty)
    except:
        logging(traceback.format_exc())
    return

def CreateFixedConstraint(constraintName, modelName, entityType, entities, Tx=1, Ty=1, Tz=1, Rx=1, Ry=1, Rz=1):
	try:
		entityType = entityType.lower()
		entities = str(entities).replace("'",'"')
		entities = str(entities).strip("[]""()")
		Tx = str(Tx)
		Ty = str(Ty)
		Tz = str(Tz)
		Rx = str(Rx)
		Ry = str(Ry)
		Rz = str(Rz)

		FixedConstraint=''' <Fixed BCType="Constraint" isObject="2" UUID="f5ecfc0a-a238-477c-928c-e81c22353a69">
		<tag Value="-1"/>
		<Name Value="''' + constraintName + '''"/>
		<FixedEntities>'''

		if entityType == 'group':
			FixedConstraint += '''
			<Group>''' + entities + ''',</Group>'''
		elif entityType == 'face':
			FixedConstraint += '''
			<Entities>
			<Model>''' + modelName + '''</Model>
			<Face>''' + entities + ''',</Face>
			</Entities>'''
		elif entityType == 'edge':
			FixedConstraint += '''
			<Entities>
			<Model>''' + modelName + '''</Model>
			<Edge>''' + entities + ''',</Edge>
			</Entities>'''
		elif entityType == 'node':
			FixedConstraint += '''
			<Entities>
			<Model>''' + modelName + '''</Model>
			<Node>''' + entities + ''',</Node>
			</Entities>'''
		else:
			raise ValueError('There is no implementation to delete the specified type.')

		params = Tx + Ty + Tz + Rx + Ry + Rz

		FixedConstraint += '''
		</FixedEntities>
		<CoordinateAxisID Value="Global" Index="0"/>
		<UseParameter Value="0"/>
		<Parameter Value="''' + params + '''"/>
		<Tx Value="''' + Tx + '''"/>
		<Ty Value="''' + Ty + '''"/>
		<Tz Value="''' + Tz + '''"/>
		<Rx Value="''' + Rx + '''"/>
		<Ry Value="''' + Ry + '''"/>
		<Rz Value="''' + Rz + '''"/>
		</Fixed>'''
		simlab.execute(FixedConstraint)
	except:
		logging(traceback.format_exc())
	return

def CreateView(viewName, viewSetup='Current View', axis=[1,0,0], angle=0, center=[0,0,0]):
    '''
        Creates a view.
        Args:
            viewName View name
            viewSetup: Setup type of view. 'Current View', 'Front X (Front)', 'Back X (Rear)', 'Front Y (Left)', 'Back Y (Right)', 'Front Z (Bottom)', 'Back Z (Top)' 
            axis: Rotation axis
            angle: Rotation angle
            center: Rotation center
    '''
    try:
        axis = str(axis.copy()).strip("[]""()")
        angle = str(angle)
        center = str(center.copy()).strip("[]""()")

        CreateView=''' <CreateView UUID="9221c466-e4f6-47ea-99a0-82324c846844">
        <ViewName Value="''' + viewName + '''"/>
        <Co-ordinateID Value="Global"/>
        <ViewSetup Value="''' + viewSetup + '''"/>
        <Axis Value="''' + axis + ''',"/>
        <Angle Value="''' + angle + '''"/>
        <Center Value="''' + center + '''"/>
        </CreateView>'''
        simlab.execute(CreateView)
    except:
        logging(traceback.format_exc())
    return


def DeleteView(views):
    '''
        Deletes views.
        views: View name list or tuple.
    '''
    try:
        views = str(views).replace("'",'')
        views = str(views).replace('"','')
        views = str(views).strip("[]""()")

        DeleteView=''' <DeleteView UUID="773c9b04-6607-44d4-bf48-d4a010eed38d">
        <ViewNames Value="''' + views + ''',"/>
        </DeleteView>'''
        simlab.execute(DeleteView)
    except:
        logging(traceback.format_exc())
    return


def CaptureImage(filePath):
    '''
        Capture image. Export image file of 3D view.
        Args:
            filePath File path. The supported formats are 'JPG (*. Jpg)', 'Bitmap (*. Bmp)', 'PNG (*. Png)', 'XPM (*. Xpm)'.
    '''
    try:
        path, ext = os.path.splitext(filePath)
        ext = ext.lower()

        extDict = {
            '.jpg': 'JPG (*. Jpg)',
            '.jpeg': 'JPG (*. Jpg)',
            '.bmp' : 'Bitmap (*. Bmp)',
            '.png' : 'PNG (*. Png)',
            '.xpm' : 'XPM (*. Xpm)',
        }
        selectedFilter = extDict[ext]

        CaptureImage=''' <CaptureImage UUID="0f5d1037-5f97-4798-b622-f8eb8e6cb793">
        <FileName Value="''' + filePath + '''"/>
        <SelectedFilter Value="''' + selectedFilter + '''"/>
        <CoordinateDisplay Value="ON"/>
        </CaptureImage>'''
        simlab.execute(CaptureImage)
    except:
        logging(traceback.format_exc())
    return

def AddIntParameters(name, value):
    '''
        Add parameter. [integer]
        Args:
            name: Parameter name.
            value: Parameter value.
    '''
    SimLabParameters=''' <Parameters UUID="67a54923-dbd3-4d54-931b-2405601ba45f">
        <ParamInfo Name="''' + name + '''" Value="'''+ str(value) + '''" Type="integer"/>
        </Parameters>'''
    simlab.execute(SimLabParameters)

def AddRealParameters(name, value):
    '''
        Add parameter. [real]
        name: Parameter name.
        value: Parameter value. 
    '''
    SimLabParameters=''' <Parameters UUID="67a54923-dbd3-4d54-931b-2405601ba45f">
        <ParamInfo Name="''' + name + '''" Value="'''+ str(value) + '''" Type="real"/>
        </Parameters>'''
    simlab.execute(SimLabParameters)


def AddStringParameters(name, value):
    '''
        Add parameter. [string]
        Args:
            name Parameter name.
            value Parameter value. 
    '''
    SimLabParameters=''' <Parameters UUID="67a54923-dbd3-4d54-931b-2405601ba45f">
        <ParamInfo Name="''' + name + '''" Value="'''+ value+ '''" Type="string"/>
        </Parameters>'''
    simlab.execute(SimLabParameters)

def DeleteParameters(name):
    '''
        Delete parameter. [integer], [real], [string]
        Args:
            name. Parameter name.
    '''
    DeleteParameters=''' <DeleteParameters UUID="57a0affc-2283-4c6b-9da2-f4b5de469440">
        <ParameterNames Value="''' + name + '''"/>
        <!-- If Value attribute is empty,it deletes all global parameters. -->
        </DeleteParameters>'''
    simlab.execute(DeleteParameters)


def DeleteMeshQuality(name):
    '''
        Delete mesh quality.
        Args:
            name. Mesh Quality name.
    '''
    DeleteMeshQuality=''' <DeleteMeshQuality UUID="d8275fe1-2e7c-4709-9367-b91da165930c">
        <Name Value="''' + name + '''"/>
        </DeleteMeshQuality>'''
    simlab.execute(DeleteMeshQuality)

def DeleteMeshControl(name):
    '''
        Delete mesh ctrl.
        Args:
            name. Mesh Ctrl name.
    '''
    DeleteMeshControl=''' <DeleteMeshControl UUID="c801afc7-a3eb-4dec-8bc1-8ac6382d4c6e" CheckBox="ON">
        <Name Value="''' + name + '''"/>
        </DeleteMeshControl>'''
    simlab.execute(DeleteMeshControl)


def RemoveChamfer(removableFaces, planarFaces):
    '''
        Remove chamfer faces
        Args:
            removableFaces Removable Faces
            planarFaces Adjacent planar faces
    '''
    try:
        modelName = simlab.getModelName('FEM')
        removableFaces = str(removableFaces).strip("[]""()")
        planarFaces = str(planarFaces).strip("[]""()")

        RemoveChamfer=''' <RemoveFace UUID="6b5c72d1-a95c-41f1-9b10-89b92f99cd49" gda="">
        <tag Value="-1"/>
        <RemovableFace>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Face>''' + removableFaces + ''',</Face>
        </Entities>
        </RemovableFace>
        <PlanarFace>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Face>''' + planarFaces + ''',</Face>
        </Entities>
        </PlanarFace>
        <Collapse Value="1"/>
        </RemoveFace>'''
        simlab.execute(RemoveChamfer)
    except:
        logging(traceback.format_exc())
    return

def GetAdjacentFacesToLimitFaces(modelName, guideFaces, limitFaces, groupName, breakAngle=0, angle=45):
    '''
        Get ajacent faces to limit faces
        Args:
            modelName: model name
            guideFaces: guide faces
            limitFaces: limit faces
            groupName: Group name of result
            BreakAngle: Break angle
            Angle: Angle
    '''
    try:
        guideFaces = str(guideFaces).strip("[]""()")
        limitFaces = str(limitFaces).strip("[]""()")

        ShowAdjacent=''' <ShowAdjacent gda="" clearSelection="1" UUID="EEDC5B06-8DC9-4754-AA76-F9E32643765A">
        <Name Value=""/>
        <tag Value="-1"/>
        <Show Value="0"/>
        <Select Value="1"/>
        <CheckVisibleFaces Value="1"/>
        <SupportEntities EntityTypes="" ModelIds="" Value=""/>
        <PickFaceType Value="GuideFaces"/>
        <GuideFaces>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Face>''' + guideFaces + ''',</Face>
        </Entities>
        </GuideFaces>
        <LimitFaces>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Face>''' + limitFaces + ''',</Face>
        </Entities>
        </LimitFaces>
        <AddPlanarFacestoLimitFaces Value="0"/>
        <AddCylindricalFacestoLimitFaces Value="0"/>
        <UptoNonManifoldEdges Value="0"/>
        <BreakAngle Value="''' + str(breakAngle) + '''"/>
        <Angle Value="''' + str(angle) + '''"/>
        <NoOfLayers Value="234"/>
        <PlanePoints Value=""/>
        <CreateGroup Value="1" Name="''' + groupName + '''"/>
        </ShowAdjacent>'''
        simlab.execute(ShowAdjacent)
    except:
        logging(traceback.format_exc())
    return


def UpdateModel():
    '''
        Update Model
    '''
    modelNm = simlab.getModelName("FEM")
    UpdateModel=''' <UpdateMTopology UUID="D1F56859-D6DB-4431-8699-7E3BE98DA530">
    <tag Value="-1"/>
    <ModelName Value='''+ modelNm +'''/>
    </UpdateMTopology>'''
    simlab.execute(UpdateModel)


def CalculateOverallCOGAndMassFromBodies(bodies):
    '''
        Calculate overall COG and mass from bodies
        Args:
            bodies Bodies for calustation. Property must be assigned.
        Returns:
            mass, cog. e.g. [1, [2,3,4]]. If calustation failed, an empty list is returned.
    '''
    result = []
    try:
        modelName = simlab.getModelName('FEM')
        bodies = str(bodies).replace("'",'"')
        bodies = str(bodies).strip("[]""()")

        _, tmpfile = tempfile.mkstemp()

        ExportMassProperties=''' <ExportMassProperties UUID="0fd1f4ae-0e76-4125-a915-ef18f37b0e08">
        <tag Value="-1"/>
        <SupportEntities>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Body>''' + bodies + ''',</Body>
        </Entities>
        </SupportEntities>
        <FileName Value="''' + tmpfile + '''"/>
        <CoordID Value="Global"/>
        </ExportMassProperties>'''
        simlab.execute(ExportMassProperties)

        if os.path.isfile(tmpfile):
            with open(tmpfile) as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) < 9:
                        continue

                    name, mass, cog = row[0], row[5], row[6:9]
                    if name != 'Overall Values':
                        continue

                    mass = float(mass)
                    cogX = float(cog[0])
                    cogY = float(cog[1])
                    cogZ = float(cog[2])
                    result = [mass, [cogX, cogY, cogZ]]
            try:
                os.remove(tmpfile)
            except:
                pass
    except:
        logging(traceback.format_exc())

    return result


def JoinFaces(entityType, entities, joinType, tolerance, loaclRemesh=1):
    '''
        Calculate overall COG and mass from bodies
        Args:
            entityType: Entity type such as 'Body', 'Face'
            entities: Entity list or tuple
            joinType: Plane, Cylinder, PartialCylinder, GeneralFace, GeomMatching
            tolerance: Tolerance
            loaclRemesh: RoaclRemesh ON/OFF, 1 or 0.
    '''
    try:
        modelName = simlab.getModelName('FEM')
        entities = str(entities).replace("'",'"')
        entities = str(entities).strip("[]""()")

        entityType = entityType.lower()
        entityDict = {
            'body': 'Body',
            'face': 'Face',
        }
        entityKey = entityDict[entityType]

        joinType = joinType.lower()
        joinDict = {
            'plane': 'GEOM_PLANAR_FACES',
            'cylinder': 'CYLINDRICAL_FACES|CONICAL_FACES|ADV_DISC_FACES',
            'partialcylinder': 'ADV_PART_CYL_FACES|ADV_PART_CONE_FACES',
            'generalface': 'GENERAL_FACES',
            'geommatching': 'GEOM_MATCHING_FACES',
        }
        joinKey = joinDict[joinType]

        Join=''' <Join UUID="93BDAC5E-9059-42b6-BDC3-EFA346D3DDEC" CheckBox="ON">
        <tag Value="-1"/>
        <Name Value=""/>
        <Pick Value="Join"/>
        <JoinEntities>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <''' + entityKey + '''>''' + entities + ''',</''' + entityKey + '''>
        </Entities>
        </JoinEntities>
        <AlignEntities ModelIds="" EntityTypes="" Value=""/>
        <PreserveEntities ModelIds="" EntityTypes="" Value=""/>
        <Tolerance Value="''' + str(tolerance) + '''"/>
        <JoinType Value="''' + joinKey + '''"/>
        <MeshOrShape Value="Shape"/>
        <MeshOption Value="Auto"/>
        <MeshParam Value=""/>
        <SplitFace Value="1"/>
        <LocalRemesh Value="''' + str(loaclRemesh) + '''"/>
        </Join>'''
        simlab.execute(Join)
    except:
        logging(traceback.format_exc())
    return


def BreakBody(modelName, bodies, points, createFace=1, breakBodies=1):
    '''
        Break bodies
        Args:
            modelName: Model name
            bodies: Bodies for dividing
            points: 4 points on plane
            createFace: Creating face=1
            breakBodies: Break bodies=1
    '''
    try:
        bodies = str(bodies).replace("'",'"')
        bodies = str(bodies).strip("[]""()")

        p1, p2, p3, p4 = points
        p1 = str(p1).strip("[]""()")
        p2 = str(p2).strip("[]""()")
        p3 = str(p3).strip("[]""()")
        p4 = str(p4).strip("[]""()")

        BreakBody=''' <Break UUID="ccdd6ef0-aaff-4594-850d-886c733cbc2f">
        <tag Value="-1"/>
        <Name Value="Break1"/>
        <Type Value="1"/>
        <PlaneBreak>
        <CreateFace Value="''' + str(createFace) + '''"/>
        <BreakBodies Value="''' + str(breakBodies) + '''"/>
        <PlanePoints Value=""/>
        <Entity>
            <Entities>
            <Model>''' + modelName + '''</Model>
            <Body>''' + bodies + ''',</Body>
            </Entities>
        </Entity>
        <Mode Value="1" value=""/>
        <PlaneLstData>
            <Plane PlanePoints="''' + p1 + ''',''' + p2 + ''',''' + p3 + ''',''' + p4 + ''',"/>
        </PlaneLstData>
        </PlaneBreak>
        <CylBreak>
        <CreateFace Value="0"/>
        <BreakBodies Value="0"/>
        <CylPoints Value=""/>
        <Entity Value=""/>
        <Retain Value=""/>
        </CylBreak>
        <BoxBreak>
        <BreakOption Value="0"/>
        <BoxPoints Value=""/>
        <Entity Value=""/>
        </BoxBreak>
        <PolyBreak>
        <Mode Value=""/>
        <Points Value=""/>
        <TargetEntities Value=""/>
        <ToolEntities Value=""/>
        <CreateFace Value="0"/>
        <BreakBodies Value="0"/>
        <Entity Value=""/>
        </PolyBreak>
        <ConeBreak>
        <CreateFace Value="0"/>
        <BreakBodies Value="0"/>
        <ConePoints Value=""/>
        <Entity Value=""/>
        <TopRadius Value=""/>
        <BottomRadius Value=""/>
        </ConeBreak>
        <Output/>
        </Break>'''
        simlab.execute(BreakBody)
    except:
        logging(traceback.format_exc())
    return

def MergeFaces(modelName, faces):
    '''
        Break bodies
        Args:
            modelName: Model name
            faces: Faces
    '''
    try:
        faces = str(faces).strip("[]""()")

        MergeFaces=''' <MergeFace UUID="D9D604CE-B512-44e3-984D-DF3E64141F8D">
        <tag Value="-1"/>
        <Name Value="MergeFace1"/>
        <SupportEntities>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Face>''' + str(faces) + ''',</Face>
        </Entities>
        </SupportEntities>
        <MergeBoundaryEdges Value="1"/>
        <SplitBoundaryEdges Value="0"/>
        <SplitEdgesBasedon Value="0"/>
        <FeatureAngle Value="45"/>
        </MergeFace>'''
        simlab.execute(MergeFaces)
    except:
        logging(traceback.format_exc())
    return

def GetUniqueId(keyNm):
    coordinateID = 1
    if simlab.isParameterPresent(keyNm):
        coordinateID = simlab.getIntParameter('$'+keyNm) + 1
    AddIntParameters(keyNm, coordinateID)
    return coordinateID

def GetParameter(key, valueType):
    """
        valueType: "int", "double", "string"
    """
    if not simlab.isParameterPresent(key):
        return None
    
    if valueType == "int": return simlab.getIntParameter("$"+key)
    elif valueType == "double": return simlab.getDoubleParameter("$"+key)
    elif valueType == "string": return simlab.getStringParameter("$"+key)

def CreateRectangleFace(originCoord, x_length, y_length, x_noOfElem, y_noOfElem):
    CreateRectangleFace=''' <RectanglarFace UUID="6656CAB3-652F-4cda-9D35-422E64A404FB" gda="">
    <Name Value="RectanglarFace31"/>
    <tag Value="-1"/>
    <Element_type Value="Tri3"/>
    <x_length Value="'''+ str(x_length) +'''"/>
    <y_length Value="'''+ str(y_length) +'''"/>
    <x_no.ofElements Value="'''+ str(x_noOfElem) +'''"/>
    <y_no.ofElements Value="'''+ str(y_noOfElem) +'''"/>
    <Origin Value="'''+ str(originCoord).strip("()""[]") +'''"/>
    <MeshOption Value="0"/>
    <XMeshSize Value="1"/>
    <YMeshSize Value="1"/>
    <PlaneXYPoints Value="0,0,0,0,0,0"/>
    <ParentBodyOption Value="0"/>
    <BodyId Value=""/>
    <ModelId value=""/>
    <Output/>
    </RectanglarFace>'''
    simlab.execute(CreateRectangleFace)

def CreateArcEdgeFromNodes(modelName, startNoId, endNoId, middleNoId, noOfElem = 0, meshSize = 0):
    '''
        Args: 
            modelName
            startNoId
            endNoId
            middleNoId
            noOfElem
            meshSize
    '''
    if not noOfElem and not meshSize:
        return
    if noOfElem:
        NoOfElemChk = 1
        MeshChk = 0
    elif meshSize:
        MeshChk = 1
        NoOfElemChk = 0

    CreateEdgeFromNodes=''' <EdgeFromNode UUID="449D18D7-E715-41ce-A640-4AEC18636570" gda="">
    <Name Value="EdgeFromNode14"/>
    <tag Value="-1"/>
    <Mode Value="2"/>
    <StartNode>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Node>'''+ str(startNoId) +''',</Node>
    </Entities>
    </StartNode>
    <EndNode>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Node>'''+ str(endNoId) +''',</Node>
    </Entities>
    </EndNode>
    <DefineAxis Value="0"/>
    <Arc Value="1"/>
    <ThirdNode>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Node>'''+ str(middleNoId) +''',</Node>
    </Entities>
    </ThirdNode>
    <NoOfElemChk Value="'''+ str(NoOfElemChk) +'''"/>
    <NoOfElements Value="'''+ str(noOfElem) +'''"/>
    <MeshChk Value="'''+ str(MeshChk) +'''"/>
    <MeshSize Value="'''+ str(meshSize) +'''"/>
    <Point1 Value=""/>
    <Point2 Value=""/>
    <Radius Value=""/>
    <EquiValence Value="1"/>
    <Output/>
    </EdgeFromNode>'''
    simlab.execute(CreateEdgeFromNodes)

def CreateStraightEdgeFromNodes(modelName, startNoId, endNoId, noOfElem = 0, meshSize = 0):
    if not noOfElem and not meshSize:
        return
    if noOfElem:
        NoOfElemChk = 1
        MeshChk = 0
    elif meshSize:
        MeshChk = 1
        NoOfElemChk = 0
    CreateEdgeFromNodes=''' <EdgeFromNode UUID="449D18D7-E715-41ce-A640-4AEC18636570" gda="">
    <Name Value="EdgeFromNode5"/>
    <tag Value="-1"/>
    <Mode Value="1"/>
    <StartNode>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Node>'''+ str(startNoId) +'''</Node>
    </Entities>
    </StartNode>
    <EndNode>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Node>'''+ str(endNoId) +'''</Node>
    </Entities>
    </EndNode>
    <DefineAxis Value="0"/>
    <Arc Value="0"/>
    <ThirdNode Value=""/>
    <NoOfElemChk Value="'''+ str(NoOfElemChk) +'''"/>
    <NoOfElements Value="'''+ str(noOfElem) +'''"/>
    <MeshChk Value="'''+ str(MeshChk) +'''"/>
    <MeshSize Value="'''+ str(meshSize) +'''"/>
    <Point1 Value=""/>
    <Point2 Value=""/>
    <Radius Value=""/>
    <EquiValence Value="1"/>
    <Output/>
    </EdgeFromNode>'''
    simlab.execute(CreateEdgeFromNodes)

def TransferBodies(modelNm, destinationModel, bodies = ""):
    TransferBodies=''' <TransferBodies UUID="25823352-f737-4a92-a54d-7c7c2e4c60f2">
    <Input>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodies).replace("'",'"').strip("()") +'''</Body>
    </Entities>
    </Input>
    <DestinationModel Value="'''+ destinationModel +'''"/>
    <DestinationSubModel Value=""/>
    </TransferBodies>'''
    simlab.execute(TransferBodies)

def BasicSingleSweep(modelName,faceId,edgeId):
    '''
        Args: 
            modelName
            faceId
            edgeId
    '''
    BasicSweep=''' <BasicSweep UUID="402e0072-ee41-4146-9beb-df148934f541">
    <tag Value="-1"/>
    <EntityList>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(faceId).strip("()""[]") +'''</Face>
    </Entities>
    </EntityList>
    <SweepType Value="0"/>
    <SingOrMul Value="0"/>
    <GuideEdgeList>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edgeId).strip("()""[]") +'''</Edge>
    </Entities>
    </GuideEdgeList>
    <LayersCheck Value="0"/>
    <NoofLayers Value="0"/>
    <TetExtrude Value="0"/>
    <ElementTypes Value="0"/>
    <Output/>
    </BasicSweep>'''
    simlab.execute(BasicSweep)

def BasicMultipleSweep(modelName,faceId,edgeId):
    BasicSweep=''' <BasicSweep UUID="402e0072-ee41-4146-9beb-df148934f541">
    <tag Value="-1"/>
    <EntityList>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Face>'''+ str(faceId).strip("()""[]") +'''</Face>
    </Entities>
    </EntityList>
    <SweepType Value="2"/>
    <SingOrMul Value="1"/>
    <GuideEdgeList>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Edge>'''+ str(edgeId).strip("()""[]") +'''</Edge>
    </Entities>
    </GuideEdgeList>
    <LayersCheck Value="0"/>
    <NoofLayers Value="0"/>
    <TetExtrude Value="0"/>
    <ElementTypes Value="0"/>
    <Output/>
    </BasicSweep>'''
    simlab.execute(BasicSweep)
    # print(BasicSweep)

# if __name__ == '__main__':
#     print("Load SimLabLib") 