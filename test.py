ConnectWeldBeads=''' <ConnectWeldBeads UUID="476bfdad-f99d-4cbb-a9f9-e8db96cea404">
  <EndCirclesBead1>
   <Entities>
    <Model>WeldCap.gda</Model>
    <Edge>6688,6692,6698,6702,</Edge>
   </Entities>
  </EndCirclesBead1>
  <EndCirclesBead2>
   <Entities>
    <Model>WeldCap.gda</Model>
    <Edge>7113,7119,7121,7123,</Edge>
   </Entities>
  </EndCirclesBead2>
  <NumberOfElementLayers Value="10"/>
  <LenghtOfP0-P1 Value="5"/>
  <LenghtOfP2-P3 Value="7"/>
 </ConnectWeldBeads>''';
simlab.execute(ConnectWeldBeads);

Revolve=''' <FEARevolve UUID="AF802B42-CD64-41a1-B964-52906F7AA888" gda="">
  <tag Value="-1"/>
  <Name Value="FEARevolve11"/>
  <DirNode>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Node>6149,13774,14383,14382,</Node>
   </Entities>
  </DirNode>
  <FirstEntity>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Face>309,</Face>
   </Entities>
  </FirstEntity>
  <SecondEntity>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Face>503,</Face>
   </Entities>
  </SecondEntity>
  <RowIndex Value=""/>
  <LimitFaces Value=""/>
  <Model Value=""/>
  <layers Value="8"/>
  <elementtype Value="0"/>
  <revolvetype Value="1"/>
  <GuideEdge Value=""/>
  <Output/>
  <RegionObject>
   <Axis>
    <Pt1 Value="62.000000000000,643.730000000000,58.599986604789,"/>
    <Pt2 Value="62.000000000000,643.730000000000,98.600415248660,"/>
   </Axis>
  </RegionObject>
 </FEARevolve>''';
simlab.execute(Revolve);

# Extrude between face entities

# 1. Mapping faces to be connected
FaceUsingBasicMapMesh=''' <FaceUsingBasicMapMesh UUID="e7a3cb06-08c2-458c-a8ad-de947583ded8">
  <tag Value="-1"/>
  <ReferenceFaces>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Face>389,</Face>
   </Entities>
  </ReferenceFaces>
  <TargetFaces>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Face>309,</Face>
   </Entities>
  </TargetFaces>
  <ConnectedFaces Value=""/>
  <ReferenceEdges>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Edge>585,365,</Edge>
   </Entities>
  </ReferenceEdges>
  <TargetEdges>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Edge>611,283,</Edge>
   </Entities>
  </TargetEdges>
  <BackUpFaces Value=""/>
  <UndoOption Value=""/>
 </FaceUsingBasicMapMesh>''';
simlab.execute(FaceUsingBasicMapMesh);

Extrude=''' <FEAExtrude UUID="12B94009-EA6B-483f-BB9B-6305E23B8B9D" gda="">
  <tag Value="-1"/>
  <Name Value=""/>
  <Extrude_Option Value="2"/>
  <EntityList Flag="1" Entity="">
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Face>389,</Face>
   </Entities>
  </EntityList>
  <Group Flag="0" Value="" Entity=""/>
  <UseExist Flag="" Entity=""/>
  <DistanceNormalToElem Flag=""/>
  <DistanceDirectionRegion/>
  <DistanceRadialRegion/>
  <DistanceSpherical Flag="" Value=""/>
  <Distance Value="10"/>
  <PlaneRegion/>
  <PlaneNormalToPlane Flag=""/>
  <PlaneDirectionRegion/>
  <SecEntity Entity="">
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Face>711,</Face>
   </Entities>
  </SecEntity>
  <SecStrtPt>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Node>15190,15189,15590,15591,</Node>
   </Entities>
  </SecStrtPt>
  <Flip Value=""/>
  <Guide Flag="1" Entity="">
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Edge>585,</Edge>
   </Entities>
  </Guide>
  <Lmt Entity=""/>
  <NoOfLayers Value="3"/>
  <EdgeElemType Value=""/>
  <FaceElemType Flag="1" Value="1"/>
  <ParentBody Flag="0"/>
  <Shared Flag="1"/>
  <InFlate Value=""/>
  <GradeFactor Value="1.0" Check="0"/>
  <CreateBodyForSideAndTopFaces Flag=""/>
  <ConnectFace Flag=""/>
  <Output/>
 </FEAExtrude>''';
simlab.execute(Extrude);

DeleteSolidElements=''' <DeleteSolidElements UUID="c86ce926-2412-4325-a87f-ee6cb66c4de3" CheckBox="ON">
  <tag Value="-1"/>
  <Name Value=""/>
  <SupportEntities>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Body>"SLBody_2",</Body>
   </Entities>
  </SupportEntities>
  <Output/>
 </DeleteSolidElements>''';
simlab.execute(DeleteSolidElements);

AlignCylinder=''' <AlignCylinder UUID="5D271AC4-A0CE-411f-9E60-E7B17CB8B1B7" CheckBox="ON">
  <tag Value="-1"/>
  <Name Value=""/>
  <Entities>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Face>748,</Face>
   </Entities>
  </Entities>
  <ProjectMidNodes Value="0"/>
  <EntityType Value="1"/>
  <RegionObject>
   <Cylinder>
    <Axis Value="0.000000000000,0.000000000000,-1.000000000000,"/>
    <Center Value="62.000000000000,643.730000000000,78.600200926724,"/>
    <Radius Value="5.172538290708"/>
    <Height Value="40.000428643870"/>
   </Cylinder>
  </RegionObject>
 </AlignCylinder>''';
simlab.execute(AlignCylinder);

AlignCircular=''' <AlignCircular UUID="1AE4B435-C6D2-4b3e-84A7-1589F0D51DF8" CheckBox="ON">
  <tag Value="-1"/>
  <Name Value=""/>
  <Select Value="Select"/>
  <Edge>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Edge>742,</Edge>
   </Entities>
  </Edge>
  <Axis Value="ArcEdge"/>
  <Entity>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Edge>683,</Edge>
   </Entities>
  </Entity>
  <Radius Value="2.50969"/>
  <ProjectMidNodes Value="0"/>
  <OffsetNodes EntityTypes="" ModelIds="" Option="0" Value=""/>
 </AlignCircular>''';
simlab.execute(AlignCircular);

AlignCircular=''' <AlignCircular UUID="1AE4B435-C6D2-4b3e-84A7-1589F0D51DF8" CheckBox="ON">
  <tag Value="-1"/>
  <Name Value=""/>
  <Select Value="Select"/>
  <Edge>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Edge>726,</Edge>
   </Entities>
  </Edge>
  <Axis Value="Nodes"/>
  <Entity>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Node>15590,15556,15190,</Node>
   </Entities>
  </Entity>
  <Radius Value="2.28451"/>
  <ProjectMidNodes Value="0"/>
  <OffsetNodes EntityTypes="" ModelIds="" Option="0" Value=""/>
 </AlignCircular>''';
simlab.execute(AlignCircular);

Join=''' <Join UUID="93BDAC5E-9059-42b6-BDC3-EFA346D3DDEC" CheckBox="ON">
  <tag Value="-1"/>
  <Name Value=""/>
  <Pick Value="Join"/>
  <JoinEntities>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Body>"SLBody_2","SLBody_1",</Body>
   </Entities>
  </JoinEntities>
  <AlignEntities EntityTypes="" ModelIds="" Value=""/>
  <PreserveEntities EntityTypes="" ModelIds="" Value=""/>
  <Tolerance Value="0.0979872"/>
  <JoinType Value="OVERLAPPING_FACES"/>
  <MeshOrShape Value="Shape"/>
  <MeshOption Value=""/>
  <MeshParam Value=""/>
  <SplitFace Value="1"/>
  <LocalRemesh Value="0"/>
  <ShowOrJoin Value="1"/>
 </Join>''';
simlab.execute(Join);

Join=''' <Join UUID="93BDAC5E-9059-42b6-BDC3-EFA346D3DDEC" CheckBox="ON">
  <tag Value="-1"/>
  <Name Value=""/>
  <Pick Value="Join"/>
  <JoinEntities>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Body>"SLBody_2","SLBody_1",</Body>
   </Entities>
  </JoinEntities>
  <AlignEntities EntityTypes="" ModelIds="" Value=""/>
  <PreserveEntities EntityTypes="" ModelIds="" Value=""/>
  <Tolerance Value="0.0979872"/>
  <JoinType Value="OVERLAPPING_FACES"/>
  <MeshOrShape Value="Shape"/>
  <MeshOption Value=""/>
  <MeshParam Value=""/>
  <SplitFace Value="1"/>
  <LocalRemesh Value="0"/>
  <ShowOrJoin Value="0"/>
 </Join>''';
simlab.execute(Join);

Join=''' <Join UUID="93BDAC5E-9059-42b6-BDC3-EFA346D3DDEC" CheckBox="ON">
  <tag Value="-1"/>
  <Name Value=""/>
  <Pick Value="Join"/>
  <JoinEntities>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Body>"SLBody_2","Box1",</Body>
   </Entities>
  </JoinEntities>
  <AlignEntities EntityTypes="" ModelIds="" Value=""/>
  <PreserveEntities EntityTypes="" ModelIds="" Value=""/>
  <Tolerance Value="0.113228"/>
  <JoinType Value="OVERLAPPING_FACES"/>
  <MeshOrShape Value="Shape"/>
  <MeshOption Value=""/>
  <MeshParam Value=""/>
  <SplitFace Value="1"/>
  <LocalRemesh Value="0"/>
  <ShowOrJoin Value="0"/>
 </Join>''';
simlab.execute(Join);

QualityCheck=''' <QCheck UUID="412da11b-2793-4c07-a058-e49f209f007d">
  <ElementType Value="Tri"/>
  <Option Value="Compute"/>
  <Quality Condition="G Than Or Eq" LimitValue="10" Name="Aspect Ratio"/>
  <Quality Condition="L Than and G Than Or Eq" MinimumLimitValue="0.5" Name="Edge Length" MaximumLimitValue="100"/>
  <Quality Condition="L Than" LimitValue="0.2" Name="Height"/>
  <SupportEntities>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Body>"SLBody_2",</Body>
   </Entities>
  </SupportEntities>
 </QCheck>''';
simlab.execute(QualityCheck);

QualityCheck=''' <QCheck UUID="412da11b-2793-4c07-a058-e49f209f007d">
  <ElementType Value="Tri"/>
  <Option Value="Cleanup"/>
  <Quality Condition="G Than Or Eq" LimitValue="10" Name="Aspect Ratio"/>
  <SupportEntities>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Body>"SLBody_2",</Body>
   </Entities>
  </SupportEntities>
  <CleanupType Value="Modify Element"/>
  <PreserveSurfaceSkew Value="55" Check="0"/>
 </QCheck>''';
simlab.execute(QualityCheck);

QualityCheck=''' <QCheck UUID="412da11b-2793-4c07-a058-e49f209f007d">
  <ElementType Value="Tri"/>
  <Option Value="Compute"/>
  <Quality Condition="G Than Or Eq" LimitValue="10" Name="Aspect Ratio"/>
  <Quality Condition="L Than and G Than Or Eq" MinimumLimitValue="0.5" Name="Edge Length" MaximumLimitValue="100"/>
  <Quality Condition="L Than" LimitValue="0.2" Name="Height"/>
  <SupportEntities>
   <Entities>
    <Model>Box_Mesh1.gda</Model>
    <Body>"SLBody_2",</Body>
   </Entities>
  </SupportEntities>
 </QCheck>''';
simlab.execute(QualityCheck);

import numpy as np
import math

def NormalDirection(pts):
    p1,p2,p3 = pts
    p1 = np.array(p1)
    p2 = np.array(p2)
    p3 = np.array(p3)

    v1 = (p1 - p2) / np.linalg.norm(p1 - p2)
    v2 = (p3 - p2) / np.linalg.norm(p3 - p2)
    cp = np.cross(v1,v2)

    return cp / np.linalg.norm(cp)

def getCircleInfo(refCoords):
    refCoords = np.array(refCoords)
    assert len(refCoords) > 2
    p1,p2,p3 = refCoords[:3]
    n = NormalDirection((p1,p2,p3))

    p12 = p2 - p1
    p13 = p3 - p1

    A = np.array([n, p12, p13])
    B = np.array([np.dot(n,p1), np.dot(p12,((p1+p2)/2)), np.dot(p13,((p1+p3)/2))])
    B = B.reshape(len(B),1)
    X = (np.linalg.solve(A, B)).T

    p0 = np.array(X[0])
    v1 = p1 - p0
    radius = np.linalg.norm(v1)
    angle = 0
    for idx in range(len(refCoords)):
        if idx == len(refCoords) - 1:
            break
        v_a = refCoords[idx] - p0
        v_b = refCoords[idx + 1] - p0  
        angleInRad = angleBetweenVector(v_a, v_b)
        angle += angleInRad * 180 / math.pi

    return p0, radius, n, v1, angle
  
def angleBetweenVector(v1, v2, acute = True):
    angle = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    if acute:
        return angle
    else:
        return 2 * np.pi - angle