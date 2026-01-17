# 【UE5】최대 메모리 최적화 실전: Chaos 메모리

【UE5】최대 메모리 최적화 실전: Chaos 메모리 - Zhihu
![](https://zhuanlan.zhihu.com/p/694741394)
[](https://www.zhihu.com/)[](https://www.zhihu.com/signin?next=%2Ffollow)[](https://www.zhihu.com/signin?next=%2F)[](https://www.zhihu.com/signin?next=%2Fhot)[](https://www.zhihu.com/signin?next=%2Fcolumn-square)[](https://www.zhihu.com/signin?next=%2Fring-feeds)[](https://www.zhihu.com/consult)[](https://www.zhihu.com/education/learning)​[직답](https://zhida.zhihu.com/)모드 전환로그인/등록[UE5] 메모리 피크 최적화 실전: 카오스 메모리모드 전환
![【UE5】内存峰值优化实战：Chaos内存](Resources/chaos_01.jpg)

# 
[](https://www.zhihu.com/people/70-52-20-9-17)[](https://www.zhihu.com/people/70-52-20-9-17)

![](Resources/chaos_02.jpg)
Physics의 메모리 오버헤드 분포

  
대형 게임 지도를 구축할 때, 물리 시스템의 메모리 점유는 개발자들이 직면해야 할 도전 과제 중 하나입니다.이 기사에서는 물리적 시스템의 메모리 할당을 심층적으로 분석하고 개발자가 메모리 사용을 최적화하는 데 도움이 되는 효과적인 메모리 피크 최적화 전략을 제공합니다.
##   
ChaosTrimesh

###   
메모리 할당 시기

  
Chaos의 소스 코드에서 우리는 ChaosTrimesh에서 메모리 할당을 하는 곳을 볼 수 있습니다.
```
//ChaosDerivedDataReader.cpp
{LLM_SCOPE(ELLMTag::ChaosTrimesh);ChaosAr<<TrimeshImplicitObjects<<UVInfo<<FaceRemap;}
```

  
이 코드는 Trimesh Implicit Objects, UVInfo 및 FaceRemap의 세 가지 주요 메모리 할당 부분을 다룹니다.메모리 분석을 개선하기 위해 다음과 같이 세 가지 메모리 할당 영역을 추적하기 위해 소스 코드를 수정하는 것이 좋습니다.
```
{
    LLM_SCOPE(ELLMTag::ChaosTrimesh);
    LLM_SCOPE_BYNAME(TEXT("Physics/TrimeshImplicitObjects"));
    ChaosAr << TrimeshImplicitObjects;
}
{
    LLM_SCOPE_BYNAME(TEXT("Physics/UVInfo"));
    ChaosAr << UVInfo;
}
{
    LLM_SCOPE_BYNAME(TEXT("Physics/FaceRemap"));
    ChaosAr << FaceRemap;
}
```

  
이렇게 소스를 수정하면 메모리 분석 도구에서 메모리 할당의 세 가지 측면을 더 명확하게 식별할 수 있습니다.
###   
TrimeshImplicitObjects

  
**전치 지식**

  
Chaos TriMeshes는 일반적으로 복잡한 충돌 모델을 처리하는 데 사용됩니다.UE5에서 ChaosTrimesh와 ChaosConvex는 일반적으로 UStatic Mesh가 로드될 때 메모리를 사전 할당합니다.이 과정은 주로 바디셋업에서 일어난다.cpp的FinishCreatingPhysicsMeshes_Chaos方法中。구체적인 물리기하체의 충돌구축 과정은[ChaosInterfaceUtils](https://zhida.zhihu.com/search?content_id=242517317&content_type=Article&match_order=1&q=ChaosInterfaceUtils&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3Njg4MjI4MDcsInEiOiJDaGFvc0ludGVyZmFjZVV0aWxzIiwiemhpZGFfc291cmNlIjoiZW50aXR5IiwiY29udGVudF9pZCI6MjQyNTE3MzE3LCJjb250ZW50X3R5cGUiOiJBcnRpY2xlIiwibWF0Y2hfb3JkZXIiOjEsInpkX3Rva2VuIjpudWxsfQ.I9yHoPh4fWpgot8omQgkf5OyTOYuzmRn-d-qFppRJAw&zhida_source=entity)에 있다[](https://zhida.zhihu.com/search?content_id=242517317&content_type=Article&match_order=1&q=ChaosInterfaceUtils&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3Njg4MjI4MDcsInEiOiJDaGFvc0ludGVyZmFjZVV0aWxzIiwiemhpZGFfc291cmNlIjoiZW50aXR5IiwiY29udGVudF9pZCI6MjQyNTE3MzE3LCJjb250ZW50X3R5cGUiOiJBcnRpY2xlIiwibWF0Y2hfb3JkZXIiOjEsInpkX3Rva2VuIjpudWxsfQ.I9yHoPh4fWpgot8omQgkf5OyTOYuzmRn-d-qFppRJAw&zhida_source=entity).cpp에서 구현됩니다.
```
// ChaosInterfaceUtils.cpp
// void CreateGeometry
constboolbMakeComplexGeometry=(CollisionTraceType!=CTF_UseSimpleAsComplex)||(SimpleShapeCount==0);
```

  
bMake Complex Geometry==true인 경우 복잡한 충돌, 즉 Trimesh Implicit Objects가 생성됩니다.  
게임은 쿡의 경우 프로젝트 설정 및 staticMesh 상의 설정에 따라 이 부분의 정보를 쿡의 실제 패키지에 넣을지 여부를 결정합니다.
```
// BodySetup.cpp
void UBodySetup::GetCookInfo(FCookBodySetupInfo& OutCookInfo, EPhysXMeshCookFlags InCookFlags) const
```

  

Complex Collision Mesh가 지정되면 이를 복합 충돌 메쉬로 사용하고, 그렇지 않으면 LODFor Collision이 지정한 LOD를 복합 충돌 메쉬로 사용합니다.
```
// StaticMesh.cpp
// bool UStaticMesh::GetPhysicsTriMeshDataCheckComplex
const int32 UseLODIndex = bInUseAllTriData ? 0 : FMath::Clamp(LODForCollision, 0, GetRenderData()->LODResources.Num()-1);

FStaticMeshLODResources& LOD = GetRenderData()->LODResources[UseLODIndex];
```

  

  
Nanite의 경우 NaniteMesh는 LOD가 없고 FallbackMesh를 사용합니다(FallbackMesh는 Nanite를 지원하지 않는 시스템에서 이 Mesh로 렌더링하는 것을 의미합니다).마지막으로 Cook할 때 Chaos는 이 mesh를 단순화하고 불필요한 꼭짓점을 제거하기 위해 몇 가지 청소 작업을 수행하지만, 그렇게 간단하지는 않습니다.
```
// ChaosDerivedDataUtil.cpp
void CleanTrimesh(TArray<FVector3f>& InOutVertices, TArray<int32>& InOutIndices, TArray<int32>* OutOptFaceRemap, TArray<int32>* OutOptVertexRemap)
```

  
주로 반복되는 정점을 찾고 병합하고 AABB 트리와 같은 공간 가속 구조를 사용하여 공간에서 가까운 정점을 빠르게 찾고 반복으로 간주되는 임계값 WeldThreshold Sq를 설정하여 얼마나 먼 정점이 반복으로 간주되어야 하는지 결정하고 마지막으로 각 유일한 정점에 새로운 인덱스를 할당하고 모든 반복 정점을 이 새로운 인덱스에 매핑합니다.

  
**어떻게 최적화할 것인가**

  
Complex 충돌이 필요 없는 항목에서 ProjectSetting->Engine->Physics->Simulation->DefaultShapeComplexity 이 옵션을 UseSimpleCollisionAsComplex로 변경하면 TrimeshImplicitObjects 이 부분의 메모리 할당을 바로 제거할 수 있습니다.프로젝트에 Complex 충돌이 필요한 경우 각 StaticMesh->Collision->Collision Complexity에 이 속성을 별도로 설정해야 합니다.
###   
UVInfo

  
**전치 지식**
```
/** UV information for BodySetup, only created if UPhysicsSettings::bSupportUVFromHitResults */
struct FBodySetupUVInfo
{
    /** Index buffer, required to go from face index to UVs */
    TArray<int32> IndexBuffer;
    /** Vertex positions, used to determine barycentric co-ords */
    TArray<FVector> VertPositions;
    /** UV channels for each vertex */
    TArray< TArray<FVector2D> > VertUVs;

    friend FArchive& operator<<(FArchive& Ar, FBodySetupUVInfo& UVInfo)
    {
       Ar << UVInfo.IndexBuffer;
       Ar << UVInfo.VertPositions;
       Ar << UVInfo.VertUVs;

       return Ar;
    }

    /** Get resource size of UV info */
    void GetResourceSizeEx(FResourceSizeEx& CumulativeResourceSize) const;

    void FillFromTriMesh(const FTriMeshCollisionData& TriMeshCollisionData);
};
```

  
충돌 감지 시 충돌 지점 대 실제 메쉬의 UV를 복원하기 위해 다양한 정보를 저장한다.
```
// StaticMesh.cpp
// bool UStaticMesh::GetPhysicsTriMeshDataCheckComplex
bool bCopyUVs = bSupportPhysicalMaterialMasks || UPhysicsSettings::Get()->bSupportUVFromHitResults; // See if we should copy UVs

// If copying UVs, allocate array for storing them
if (bCopyUVs)
{
    CollisionData->UVs.AddZeroed(LOD.GetNumTexCoords());
}

```

쿡의 정보에서 실제 게임 이용을 위한 충돌을 구축한 곳이다.

  
**어떻게 최적화할 것인가**
```
/** 
 *  Try and find the UV for a collision impact. Note this ONLY works if 'Support UV From Hit Results' is enabled in Physics Settings.
 */
UFUNCTION(BlueprintPure, Category = "Collision")
static ENGINE_API bool FindCollisionUV(const struct FHitResult& Hit, int32 UVChannel, FVector2D& UV);
```

  
UVInfo의 경우 프로젝트가 충돌 감지 결과를 통해 UV 좌표를 찾는 기능(예:**FindCollision UV**)에 의존하지 않는 경우 프로젝트 설정에서 해당 지원 옵션을 꺼서 불필요한 메모리 소비를 줄일 수 있습니다.ProjectSetting->Engine->Physics->Optimization->SupportUVFromHitResults 하지만 구체적인 mesh에 bSupportPhysicalMaterialMasks가 체크되어 있다면 실제 실행 시 해당 Mesh의 UV 정보가 생성됩니다.
###   
FaceRemap

  
**전치 지식**
```
/** Additional face remap table, if available. Used for determining face index mapping from collision mesh to static mesh, for use with physical material masks */
TArray<int32> FaceRemap;

```

  
일반적으로 충돌 감지를 위해 3D 모델을 물리적 엔진으로 가져올 때 모델의 기하학적 데이터는 실행 시 성능을 향상시키기 위해 쿡에 의해 최적화된 형식으로 변환됩니다.이 과정에서 UV 좌표와 면의 인덱스와 같은 일부 원시 모델 데이터는 충돌 탐지에 필요하지 않기 때문에 폐기될 수 있습니다.  
그러나 어떤 경우에는 이러한 데이터를 유지하는 것이 유용합니다.예를 들어 충돌 쿼리 결과에서 물리적 재료 기반 physical material masks를 지원해야 하는 경우 원래 모델의 UV 좌표 및 면 인덱스에 액세스해야 합니다.physical material masks는 개발자가 장면 쿼리의 각 면에 대한 재료 유형을 정의할 수 있도록 하여 재료의 물리적 특성(예: 마찰, 탄성)을 기반으로 충돌 반응을 미세 조정할 수 있습니다.  
FaceRemap 테이블은 최적화된 mesh 데이터와 원시 모델 데이터 간의 매핑을 설정하는 데 사용됩니다.FaceRemap을 지원할 때 물리적 메시는 장면 쿼리에서 물리적 재질을 지원하기 위해 UV 좌표와 면중량 매핑 테이블을 저장합니다.이는 최적화되더라도 원래의 면 인덱스와 해당 UV 좌표를 이 매핑 테이블을 통해 여전히 되찾을 수 있으며, 더 복잡한 상호 작용 효과를 달성하는 데 사용할 수 있음을 의미합니다.

  
**어떻게 최적화할 것인가**

  
FaceRemap은 특정 StaticMesh에서 bSupportPhysicalMaterialMasks를 선택한 경우에만 생성되며 일반 프로젝트에는 오버헤드가 없습니다.
##   
[ChaosGeometry](https://zhida.zhihu.com/search?content_id=242517317&content_type=Article&match_order=1&q=ChaosGeometry&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3Njg4MjI4MDcsInEiOiJDaGFvc0dlb21ldHJ5IiwiemhpZGFfc291cmNlIjoiZW50aXR5IiwiY29udGVudF9pZCI6MjQyNTE3MzE3LCJjb250ZW50X3R5cGUiOiJBcnRpY2xlIiwibWF0Y2hfb3JkZXIiOjEsInpkX3Rva2VuIjpudWxsfQ.0_ki_N5S6ubKBe3G9icXQ9bNa7kiwZ3meczfxKycqn0&zhida_source=entity)

###   
메모리 할당 시기

```
// PhysInterface_Chaos.cpp
void FPhysInterface_Chaos::AddGeometry(FPhysicsActorHandle& InActor, const FGeometryAddParams& InParams, TArray<FPhysicsShapeHandle>* OutOptShapes)
{
    TRACE_CPUPROFILER_EVENT_SCOPE(FPhysInterface_Chaos::AddGeometry);
    LLM_SCOPE(ELLMTag::ChaosGeometry);
    TArray<TUniquePtr<Chaos::FImplicitObject>> Geoms;
    Chaos::FShapesArray Shapes;
    ChaosInterface::CreateGeometry(InParams, Geoms, Shapes);
    ...
}
```

  
지도를 로드하는 동안 Chaos 물리 시스템은 각 물체에 해당하는 충돌체를 생성하며, ChaosGeometry와 관련된 메모리 할당은 바로 이 단계에서 발생합니다.
```
// ChaosInterfaceUtils.cpp
    void CreateGeometry(const FGeometryAddParams& InParams, TArray<TUniquePtr<Chaos::FImplicitObject>>& OutGeoms, Chaos::FShapesArray& OutShapes)
    {
       LLM_SCOPE(ELLMTag::ChaosGeometry);
       const FVector& Scale = InParams.Scale;
       TArray<TUniquePtr<Chaos::FImplicitObject>>& Geoms = OutGeoms;
       Chaos::FShapesArray& Shapes = OutShapes;

       ECollisionTraceFlag CollisionTraceType = InParams.CollisionTraceType;
       ...
}
```

  
CreateGeometry 함수 내부에서 Chaos 엔진은 각 기본 기하학적 형상(구체, 큐브, 캡슐, 원추형 캡슐 등)에 대해 ImplicitObjects를 구성합니다.FImplicit Object에는 구체의 위치와 반지름과 같은 모양에 대한 실제 기하학적 데이터가 포함되어 있습니다.
```
// ChaosInterfaceUtils.cpp
for (const FKSphereElem& SphereElem : InParams.Geometry->SphereElems)
{
    const FKSphereElem ScaledSphereElem = SphereElem.GetFinalScaled(Scale, InParams.LocalTransform);
    const float UseRadius = FMath::Max(ScaledSphereElem.Radius, UE_KINDA_SMALL_NUMBER);
    auto ImplicitSphere = MakeUnique<Chaos::TSphere<Chaos::FReal, 3>>(ScaledSphereElem.Center, UseRadius);
    TUniquePtr<Chaos::FPerShapeData> NewShape = NewShapeHelper(MakeSerializable(ImplicitSphere), Shapes.Num(), (void*)SphereElem.GetUserData(), SphereElem.GetCollisionEnabled());
    Shapes.Emplace(MoveTemp(NewShape));
    Geoms.Emplace(MoveTemp(ImplicitSphere));
}
```

  
구형 충돌 생성을 예로 들면 class TSphere final:public FImplicit Object에서 Chaos는 모든 구형 기하 요소(FKSphere Elem)를 순회하고 각 요소에 대해 해당 Chaos:FPerShape Data 및 Chaos:TSphere를 생성한 다음 해당 모양 및 기하학적 컬렉션에 추가하여 Chaos 물리적 엔진에 사용할 수 있습니다.

  
**최적화 제안**

  
장면에서 총 충돌체 수를 줄이거나 더 복잡한 볼록한 패키지 기하학을 대체하기 위해 간단한 기하학을 사용하는 것이 가장 간단하고 효과적인 전략입니다.이렇게 하면 메모리 점유율을 줄일 수 있을 뿐만 아니라 물리적 시뮬레이션의 계산 효율성도 높일 수 있습니다.
##   
[ChaosUpdate](https://zhida.zhihu.com/search?content_id=242517317&content_type=Article&match_order=1&q=ChaosUpdate&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3Njg4MjI4MDcsInEiOiJDaGFvc1VwZGF0ZSIsInpoaWRhX3NvdXJjZSI6ImVudGl0eSIsImNvbnRlbnRfaWQiOjI0MjUxNzMxNywiY29udGVudF90eXBlIjoiQXJ0aWNsZSIsIm1hdGNoX29yZGVyIjoxLCJ6ZF90b2tlbiI6bnVsbH0.PLdiag8toR8ydkDx5ge0v6HaN-sgfFvvFuWdhtqIE48&zhida_source=entity)

  
LLM_SCOPE(ELLMTag::ChaosUpdate)로 표기된 곳을 통해 ChaosUpdate가 메모리를 할당하는 코드는 모두 PhysicsSolverBase에 있음을 알 수 있습니다.cpp. 대부분의 메모리 할당 오버헤드는 지오메트리마다 쉐이프 인스턴스를 만듭니다.
```
// ShapeInstance.cpp 
CHAOS_API static TUniquePtr<FShapeInstance> Make(int32 InShapeIdx, TSerializablePtr<FImplicitObject> InGeometry);
```

###   
기술적 배경

```
class FShapeInstance : public FPerShapeData
{
    ...
    union FMaterialUnion
{
    FMaterialUnion() : MaterialHandle() {}    // Default to single-shape mode
    ~FMaterialUnion() {}                  // Destruction handled by FShapeInstance

    FMaterialHandle MaterialHandle;             // Set if we have only 1 material, no masks etc
    FMaterialData* MaterialData;            // Set if we have multiple materials or any masks
};
FCollisionData CollisionData;
mutable FMaterialUnion Material;

// FPerShapeData
EPerShapeDataType Type : 2;
uint32 bIsSingleMaterial : 1;   // For use by FShapeInstance (here because the space is available for free)
uint32 ShapeIdx : 29;
FShapeDirtyFlags DirtyFlags;    // For use by FShapeInstanceProxy as there's 4 bytes of padding here
TSerializablePtr<FImplicitObject> Geometry;
TAABB<FReal, 3> WorldSpaceInflatedShapeBounds;
    ...
}

struct FCollisionData
{
    FCollisionFilterData QueryData;
    FCollisionFilterData SimData;
    void* UserData;
    EChaosCollisionTraceFlag CollisionTraceType;
    uint8 bSimCollision : 1;
    uint8 bQueryCollision : 1;
    uint8 bIsProbe : 1;
    ...    
}

```

  
Chaos는 계산 복잡성을 줄이기 위해 객체의 물리적 행동을 가장 간소화된 방식으로 처리하는 것을 목표로 합니다.이 프레임워크에서는 구체와 큐브와 같은 간단한 기하학적 형태가 선호되는 처리 장치가 되었습니다.이 방법은 효율적이지만 더 복잡한 물체를 처리하는 데 한계가 있습니다.  
현실 세계의 다양한 물체를 보다 정확하게 시뮬레이션하기 위해 Chaos는 ConvexMesh 개념을 도입했습니다.단순한 구면이든 삼각형으로 구성된 복잡한 격자이든 간에, 그것들은 ConvexMesh, 즉 우리의 3D 기하학적 표현의 기초입니다.  
기술적 수준에서 ConvexMesh는 FImplicit Object 및 그 하위 클래스, FPerShape Data의 두 가지 주요 데이터 유형으로 표시됩니다.FImplicit Object는 주로 형상의 기본 기하학적 데이터를 담고 있으며, 예를 들어 구체의 경우 구심의 위치와 구의 반지름 등의 정보를 포함할 것입니다.FPerShape Data는 물리적 재료 및 충돌 반응 채널과 같은 순수한 기하학적 정보가 아닌 모양에 대한 다른 중요한 속성을 포함합니다.
###   
최적화 제안

  
여기와 ChaosGeometry는 유사하며, 충돌 시 다른 정보에 속합니다. ChaosUpdate의 메모리가 너무 높으면 장면 내 충돌체 총수가 너무 많다는 것을 의미합니다.
##   
ChaosAcceleration

###   
기술적 배경

  
LLM_SCOPE(ELLMTag::ChaosAcceleration)로 표기된 곳을 통해 ChaosAcceleration 할당 메모리의 코드는 모두 PBDRigidsEvolution임을 알 수 있습니다.cpp, 이 부분의 메모리는 공간 가속 구조(Spatial Acceleration)를 구성하는 데 사용됩니다.
```
// ISpatialAcceleration.h
using SpatialAccelerationType = uint8;  //see ESpatialAcceleration. Projects can add their own custom types by using enum values higher than ESpatialAcceleration::Unknown
enum class ESpatialAcceleration : SpatialAccelerationType
{
    BoundingVolume,
    AABBTree,
    AABBTreeBV,
    Collection,
    Unknown,
    //For custom types continue the enum after ESpatialAcceleration::Unknown
};

```

  

  
UE5에는 위의 가속 구조가 있으며 실제 프로젝트에서 대부분의 메모리는 AABBTree를 구성하는 데 사용됩니다.AABBTree는 강체의 추가, 삭제 또는 강체의 상태(위치, 회전 등)가 변경될 때 업데이트됩니다.이는 AABB 트리의 구조가 리지드 바디의 AABB(축 정렬로 상자를 둘러싸는 것)에 따라 달라지며, 리지드 바디의 상태가 변경되면 AABB 트리의 구조에 영향을 미칠 수 있기 때문입니다.  
새로운 강체가 세계에 추가되고 AABBTree가 아직 업데이트되지 않은 경우 충돌 감지는 이러한 새로운 강체를 독립적인 개체(DirtyElements)로 처리합니다.이것은 충돌 감지 중에 트리에 없는 이러한 강체가 추가로 고려된다는 것을 의미합니다.이 접근 방식은 나무 구조가 업데이트되지 않은 경우에도 새로 추가된 강체가 충돌 검출에 참여할 수 있도록 합니다.트리 구조가 업데이트되면 이러한 캐시의 리지드는 새로운 트리 구조에 통합되고 주 스레드의 AABB 트리로 업데이트됩니다.  
이진 트리는 균형 트리인지 여부를 고려해야 하며, 균형 트리가 아닌 경우 빈번한 추가 및 삭제 후 쿼리 효율성이 연쇄 테이블로 퇴화될 수 있습니다.그러나 실제 개발에서는 균형 작업을 위해 노드를 삽입할 때마다 발생하는 시간 소모도 받아들이기 어려우며, Chaos에서는 이 내용을 처리하기 위해 절충 방법을 사용합니다.

  

```
//AABBTree.h
// Chaos查找插入位置的方法：
int32 FindBestSibling(const TAABB<T, 3>& InNewBounds, bool& bOutAddToLeaf)
```

  

  
최적의 삽입 위치를 찾는 이 방법은 휴리스틱 방법을 기반으로 하며 나무의 균형을 보장하지 않습니다.따라서 이 방법으로 구성된 트리는 반드시 평형 이진 트리가 아닙니다.대신, 휴리스틱 평가를 기반으로 한 거의 최적의 이진 트리이며, 이러한 트리는 실제 적용에서 충분히 잘 작동할 수 있지만 이진 트리의 균형을 엄격하게 보장하지는 않습니다.

  

```
template <typename TPayloadType, bool bComputeBounds = true, typename T = FReal>
struct TAABBTreeLeafArray : public TBoundsWrapperHelper<TPayloadType, T, bComputeBounds>
{
...
    TArray<TPayloadBoundsElement<TPayloadType, T>> Elems;
    bool bDirtyLeaf = false;
...
}
```

  

  
TAABBTree의 비잎 노드는 TAABBTree Node로, 부자 노드를 포함하는 인덱스를 제외하고 주요 정보는 두 어린이 노드의 AABB 둘러싸기 상자입니다.
```
template <typename TPayloadType, bool bComputeBounds = true, typename T = FReal> struct TAABBTreeLeafArray : public TBoundsWrapperHelper<TPayloadType, T, bComputeBounds> { ...     TArray<TPayloadBoundsElement<TPayloadType, T>> Elems;     bool bDirtyLeaf = false; ... }
```

  
TAABBTree의 잎 노드에는 TAABBTreeLeafArray <FAccelerationStructureHandle>이라는 배열이 포함되어 있습니다.
```
class FAccelerationStructureHandle
{
...
    FGeometryParticle* ExternalGeometryParticle;
    FGeometryParticleHandle* GeometryParticleHandle;
    
    FUniqueIdx CachedUniqueIdx;
    FCollisionFilterData UnionQueryFilterData;
    FCollisionFilterData UnionSimFilterData;
    bool bCanPrePreFilter;
...
}
template <typename T, int d>
class TGeometryParticle
{
...
    TChaosProperty<FParticlePositionRotation, EChaosProperty::XR> MXR;
    TChaosProperty<FParticleNonFrequentData,EChaosProperty::NonFrequentData> MNonFrequentData;
    void* MUserData;
    
    FShapeInstanceProxyArray MShapesArray;
...
}
class FParticleNonFrequentData
{
    ...
    TSharedPtr<const FImplicitObject,ESPMode::ThreadSafe> MGeometry;
    FUniqueIdx MUniqueIdx;
    FSpatialAccelerationIdx MSpatialIdx;
    FParticleID MParticleID;
    EResimType MResimType;
    bool MEnabledDuringResim;
    ...
}
```

  
FAcceleration Structure Handle 클래스에서 각 잎 노드는 변위, 회전, 기하학적 포인터 및 기타 관련 물리적 및 충돌 속성을 포함하는 하나 이상의 FGeometryParticle 인스턴스를 연관시킵니다.
###   
최적화 제안

  
강체 위치와 회전의 변화는 AABBTree의 재구성으로 이어지며**Chaos Acceleration**메모리를 최적화하는 핵심은 게임 세계에서 각 프레임이 움직이는 충돌체를 줄이는 것입니다.
##   
AncientValley实战

###   
프로젝트 다운로드 & & 패키지

![](Resources/chaos_03.jpg)

먼저 EpicGameLauncher에서 AncientValley 항목을 다운로드하십시오.
![](Resources/chaos_04.jpg)

프로젝트를 연 후 패키지, 대상 플랫폼 Windows를 선택하고 콘솔 명령(필요한 경우)을 쉽게 입력할 수 있도록 development 패키지를 사용합니다.  
편집기 아래에서도 메모리 분석을 할 수 있지만, 대부분은 의미가 없습니다. 편집기 아래에는 많은 리소스가 로드되기 때문에 실제 게임에서는 사용되지 않을 수 있습니다.
###   
메모리 분석 시작 준비

![](Resources/chaos_05.jpg)

압축이 완료된 후 오른쪽 클릭으로 바로 가기 만들기  

![](Resources/chaos_06.jpg)

목표 뒤 빈칸에 시작항 파라미터를 넣어 메모리 분석을 진행합니다. 여기서 제가 추천하는 파라미터는  
-trace=default,memory,metadata,assetmetadata,loadtime -tracehost=XXXXX -llm  
그 중 XXXX는 본 기기의 IP 주소를 대체합니다.  
그리고 언리얼 인사이트를 켜는 선에서 이 exe를 실행하면 메모리 분석이 시작되고 boss를 치고 나가시면 됩니다.
###   
메모리 분석

![](Resources/chaos_07.jpg)

빨간색 상자의 A를 LLM Total의 가장 높은 지점까지 드래그하고 Rule은 ActiveAllocs를 선택하고 Run Query를 클릭합니다.
![](Resources/chaos_08.jpg)

여기 위에 있는 Hierarchy를 살짝 돌려서 태그로 먼저 하고 Package로.
![](Resources/chaos_09.jpg)

이 프로젝트의 Physics는 주로 ChaosTrimesh에 사용된다는 것을 알 수 있습니다.
![](Resources/chaos_10.jpg)

패키지별로 정렬하시면 펼쳐보시면 구체적인 자산명을 보실 수 있습니다.
###   
문제를 해결하다.

![](Resources/chaos_11.jpg)

위에서 언급한 프로젝트의 사전 설정을 UseSimpleAsComplex로 변경하고, 구체적인 자산은 복잡한 충돌을 사용하여 여전히 복잡한 충돌을 사용한 후 패키징하여 테스트할 수 있습니다.
![](Resources/chaos_12.jpg)

프로젝트를 볼 수 있는 Physics 메모리 피크는 392MB에서 84.3MB까지다.ChaosTrimesh 부분은 317MB에서 9.5MB로 변경되었습니다.
## 마지막이다

이 글은 분량이 제한되어 있어, 독자들이 UE5 프로젝트에서 메모리 피크를 최적화하는 데 도움이 되기를 바랍니다.읽어주셔서 감사합니다, 이 내용들이 도움이 되었으면 좋겠습니다.
##   
참고 자료

  
[https://itscai.us/blog/post/ue-physics-framework/](https://link.zhihu.com/?target=https%3A//itscai.us/blog/post/ue-physics-framework/)편집: 2024-04-2618:52・광둥[UE5](https://www.zhihu.com/topic/23617766)[게임 성능 최적화](https://www.zhihu.com/topic/21326368)[메모리 최적화](https://www.zhihu.com/topic/19973988)