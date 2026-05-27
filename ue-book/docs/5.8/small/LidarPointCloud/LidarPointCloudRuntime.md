# LiDAR Point Cloud Support

> Adds support for importing, processing and rendering of LiDAR Point Clouds.

| 属性 | 值 |
|---|---|
| 中文名 | 激光点云 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板、示例资产） |
| 模块 | `LidarPointCloudRuntime` (Runtime), `LidarPointCloudEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-01-28 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud) | |

## 用途

LiDAR（激光雷达）扫描产生的点云数据是建筑信息模型（BIM）、数字孪生、地理信息系统（GIS）和影视虚拟制片（Virtual Production）等领域的核心数据格式。原始点云动辄数千万甚至数十亿个点，UE5 原生不支持直接使用此类数据。

本插件解决以下核心问题：

- **导入与解析**：自动识别 LAS/LAZ、E57、XYZ/TXT/PTS 等常见激光扫描格式，将原始数据解析为引擎可识别的点结构体（`FLidarPointCloudPoint`）
- **八叉树空间索引**：将无组织的点数据构建为八叉树（`FLidarPointCloudOctree`），支持空间查询、LOD 渐进加载和动态流送
- **GPU 渲染**：通过自定义顶点工厂（`FLidarPointCloudVertexFactory`）和专用 Shader 实现大规模点云的高效渲染，支持光照衰减、高程着色、分类着色、碰撞检测等
- **LOD 管理**：全局 LOD 管理器（`FLidarPointCloudLODManager`）根据视口信息和点预算自动选择可见节点，确保在不超出 GPU 预算的前提下最大化细节

## 使用场景

- **数字孪生 / 智慧城市** → 导入建筑或市政设施的激光扫描数据，在 UE5 中重建实景三维场景
- **影视虚拟制片** → 在 LED Volume 或绿幕场景中使用扫描点云作为背景环境
- **建筑可视化** → 将实测点云与 BIM 模型叠加对比，用于施工验证或竣工记录
- **考古 / 文化遗产** → 三维扫描古建筑或遗址，生成可在引擎中交互浏览的点云资产
- **自动驾驶仿真** → 使用 LiDAR 传感器输出的点云数据进行回放或合成训练
- **点云编辑工具开发** → 基于组件级 API 构建自定义的点云编辑、裁剪或标注工具

## 蓝图用法

本插件大量暴露了 `BlueprintCallable` 和 `BlueprintPure` 函数，分布在三个主要类中。

### 核心节点

#### 查询与射线检测

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetNumPoints` | 获取点云总点数 | `ULidarPointCloud` |
| `GetNumVisiblePoints` | 获取可见点数量 | `ULidarPointCloud` |
| `HasPointsInSphere` | 判断球形区域内是否存在点 | `ULidarPointCloud`, `ULidarPointCloudComponent` |
| `HasPointsInBox` | 判断盒形区域内是否存在点 | `ULidarPointCloud`, `ULidarPointCloudComponent` |
| `LineTraceSingle` | 单点射线检测，返回命中的第一个点 | `ULidarPointCloud`, `ULidarPointCloudComponent` |
| `LineTraceMulti` | 多点射线检测，返回所有命中点 | `ULidarPointCloud`, `ULidarPointCloudComponent` |

#### 点集获取

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetPointsAsCopies` | 获取点副本数组（支持世界/局部坐标） | `ULidarPointCloud` |
| `GetPointsInSphereAsCopies` | 获取球形区域内点的副本 | `ULidarPointCloud`, `ULidarPointCloudComponent` |
| `GetPointsInBoxAsCopies` | 获取盒形区域内点的副本 | `ULidarPointCloud`, `ULidarPointCloudComponent` |

#### 可见性控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetVisibilityOfPointsInSphere` | 设置球形区域内点的可见性 | `ULidarPointCloud`, `ULidarPointCloudComponent` |
| `SetVisibilityOfPointsInBox` | 设置盒形区域内点的可见性 | `ULidarPointCloud`, `ULidarPointCloudComponent` |
| `SetVisibilityOfFirstPointByRay` | 设置射线命中的第一个点的可见性 | `ULidarPointCloud`, `ULidarPointCloudComponent` |
| `SetVisibilityOfPointsByRay` | 设置射线命中的所有点的可见性 | `ULidarPointCloud`, `ULidarPointCloudComponent` |
| `HideAll` / `UnhideAll` | 隐藏/显示全部点 | `ULidarPointCloud` |

#### 颜色修改

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplyColorToAllPoints` | 为所有点应用颜色 | `ULidarPointCloud` |
| `ApplyColorToPointsInSphere` | 为球形区域内点应用颜色 | `ULidarPointCloud`, `ULidarPointCloudComponent` |
| `ApplyColorToPointsInBox` | 为盒形区域内点应用颜色 | `ULidarPointCloud`, `ULidarPointCloudComponent` |
| `ApplyColorToPointsByRay` | 为射线命中的点应用颜色 | `ULidarPointCloud`, `ULidarPointCloudComponent` |

#### 数据编辑

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InsertPoint` / `InsertPoints` | 向八叉树中插入单个/批量点 | `ULidarPointCloud` |
| `RemovePoint` | 移除指定点 | `ULidarPointCloud` |
| `RemovePointsInSphere` | 移除球形区域内点 | `ULidarPointCloud`, `ULidarPointCloudComponent` |
| `RemovePointsInBox` | 移除盒形区域内点 | `ULidarPointCloud`, `ULidarPointCloudComponent` |

#### 碰撞

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BuildCollision` | 使用当前碰撞设置构建碰撞网格 | `ULidarPointCloud` |
| `RemoveCollision` | 移除碰撞网格 | `ULidarPointCloud` |
| `HasCollisionData` | 检查是否已构建碰撞 | `ULidarPointCloud` |

#### 坐标与变换

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetLocationOffset` | 设置点云的位置偏移 | `ULidarPointCloud` |
| `CenterPoints` | 将点云居中（偏移归零） | `ULidarPointCloud` |
| `RestoreOriginalCoordinates` | 恢复原始坐标 | `ULidarPointCloud` |
| `IsCentered` | 检查点云是否已居中 | `ULidarPointCloud` |

#### 蓝图库函数（`ULidarPointCloudBlueprintLibrary`）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LineTraceSingle` (Static) | 对场景中的点云执行射线检测 | `ULidarPointCloudBlueprintLibrary` |
| `LineTraceMulti` (Static) | 对场景中的点云执行多点射线检测 | `ULidarPointCloudBlueprintLibrary` |
| `NormalFromVector` | 将 Vector 设置为法线 | `ULidarPointCloudBlueprintLibrary` |
| `Conv_LidarPointCloudNormalToVector` | 法线转 Vector（自动转换节点） | `ULidarPointCloudBlueprintLibrary` |
| `Conv_VectorToLidarPointCloudNormal` | Vector 转法线（自动转换节点） | `ULidarPointCloudBlueprintLibrary` |

#### 从文件创建（ASCII 格式）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreatePointCloudFromFile` (ASCII) | 从 ASCII 文本文件异步创建点云资产 | `ULidarPointCloudFileIO_ASCII` |

### 使用示例

**射线检测并修改命中区域颜色**：

```
1. 获取场景中的 ULidarPointCloudComponent 引用（如通过 "Get Component By Class"）
2. 调用 LineTraceMulti（Origin=玩家摄像机位置, Direction=摄像机前向, Radius=5.0）
3. 将返回的 OutHits 数组传入 ForEachLoop
4. 对循环中的每个点，调用 ApplyColorToPointsInSphere（Center=点.Location, Radius=2.0, NewColor=红色）
```

**动态隐藏/显示区域**：

```
1. 使用 SphereTrace 获得玩家瞄准的世界位置
2. 右键点击 → SetVisibilityOfPointsInSphere（bNewVisibility=false, Center=命中位置, Radius=100）
3. 左键点击 → SetVisibilityOfPointsInSphere（bNewVisibility=true, Center=命中位置, Radius=100）
```

**组件外观配置**：

```
ULidarPointCloudComponent 属性面板：
  - PointSize = 3.0（调整点大小）
  - ScalingMethod = PerNodeAdaptive（推荐的自适应缩放）
  - ColorSource = Classification（使用分类着色）
  - ClassificationColors: Map<int32, FLinearColor>（自定义分类颜色映射）
  - GapFillingStrength = 0.035（弥合点间缝隙）
  - bUseFrustumCulling = true（启用视锥裁剪）
```

## C++ 用法

### 头文件引入

```cpp
#include "LidarPointCloud.h"
#include "LidarPointCloudComponent.h"
#include "LidarPointCloudActor.h"
#include "LidarPointCloudShared.h"
#include "LidarPointCloudSettings.h"
#include "IO/LidarPointCloudFileIO.h"
#include "IO/LidarPointCloudFileIO_LAS.h"
#include "Meshing/LidarPointCloudMeshing.h"
```

### 基本用法

**创建点云资产并插入点**：

```cpp
// 创建一个新的点云资产
ULidarPointCloud* PointCloud = NewObject<ULidarPointCloud>();

// 设置边界并初始化
FBox Bounds(FVector(-1000, -1000, -500), FVector(1000, 1000, 500));
PointCloud->Initialize(Bounds);

// 插入单个点
FLidarPointCloudPoint Point(FVector(100.0f, 200.0f, 50.0f), 255, 128, 64, 255, 0);
PointCloud->InsertPoint(Point, ELidarPointCloudDuplicateHandling::SelectFirst, true, FVector::ZeroVector);

// 批量插入点
TArray<FLidarPointCloudPoint> Points;
for (int32 i = 0; i < 10000; ++i)
{
    Points.Add(FLidarPointCloudPoint(
        FVector(FMath::RandRange(-500.f, 500.f), FMath::RandRange(-500.f, 500.f), FMath::RandRange(-100.f, 100.f)),
        FColor::MakeRandomColor()
    ));
}

// 批量插入（多线程）
FThreadSafeBool bCancelled = false;
PointCloud->InsertPoints(
    Points.GetData(), Points.Num(),
    ELidarPointCloudDuplicateHandling::Ignore,
    true, FVector::ZeroVector,
    &bCancelled,
    [](float Progress) { UE_LOG(LogTemp, Log, TEXT("Insert progress: %.1f%%"), Progress * 100.f); }
);
```

**射线检测**：

```cpp
// 单点射线检测
FLidarPointCloudPoint* HitPoint = PointCloud->LineTraceSingle(
    FLidarPointCloudRay(CameraLocation, CameraDirection),
    5.0f,    // 半径
    true     // 仅检测可见点
);

if (HitPoint)
{
    UE_LOG(LogTemp, Log, TEXT("Hit point at: %s"), *FVector(HitPoint->Location).ToString());
}

// 多点射线检测
TArray<FLidarPointCloudPoint> HitPoints;
bool bHit = PointCloud->LineTraceMulti(
    FLidarPointCloudRay(CameraLocation, CameraDirection),
    5.0f,
    true,
    true,    // 返回世界坐标
    HitPoints
);
```

**空间查询**：

```cpp
// 球形区域查询
TArray<FLidarPointCloudPoint*> SpherePoints;
FSphere QuerySphere(FVector::ZeroVector, 500.0f);
PointCloud->GetPointsInSphere(SpherePoints, QuerySphere, true);

// 盒形区域查询
TArray<FLidarPointCloudPoint*> BoxPoints;
FBox QueryBox(FVector(-100, -100, -100), FVector(100, 100, 100));
PointCloud->GetPointsInBox(BoxPoints, QueryBox, true);
```

**在组件上操作点云**：

```cpp
// 在 Actor 中使用组件
ALidarPointCloudActor* Actor = GetWorld()->SpawnActor<ALidarPointCloudActor>();
ULidarPointCloudComponent* Component = Actor->GetPointCloudComponent();

// 设置点云资产
Component->SetPointCloud(MyPointCloud);

// 调整外观
Component->PointSize = 3.0f;
Component->ScalingMethod = ELidarPointCloudScalingMethod::PerNodeAdaptive;
Component->ColorSource = ELidarPointCloudColorationMode::Classification;

// 组件级射线检测（自动处理组件变换）
FLidarPointCloudPoint ComponentHitPoint;
bool bComponentHit = Component->LineTraceSingle(
    WorldOrigin, WorldDirection, 5.0f, true, ComponentHitPoint
);
```

### 进阶用法

**从文件导入点云**：

```cpp
// 使用 LAS 文件处理器导入
TSharedPtr<FLidarPointCloudImportSettings> Settings = 
    ULidarPointCloudFileIO::GetImportSettings(TEXT("scan.las"));

FLidarPointCloudImportResults Results;
bool bSuccess = ULidarPointCloudFileIO::Import(
    TEXT("/Path/To/scan.las"), Settings, Results
);

if (bSuccess)
{
    ULidarPointCloud* ImportedCloud = Results.PointCloud;
    UE_LOG(LogTemp, Log, TEXT("Imported %lld points"), ImportedCloud->GetNumPoints());
}

// 异步重导入
FLidarPointCloudAsyncParameters AsyncParams;
AsyncParams.bUseAsync = true;
AsyncParams.ProgressCallback = [](float Progress) {
    UE_LOG(LogTemp, Log, TEXT("Reimport: %.0f%%"), Progress * 100.f);
};
ImportedCloud->Reimport(AsyncParams);
```

**构建碰撞并导出网格**：

```cpp
// 设置碰撞精度
PointCloud->MaxCollisionError = 5.0f;

// 构建碰撞（带完成回调）
PointCloud->BuildCollision([](bool bSuccess) {
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Collision built successfully"));
    }
});

// 构建静态网格缓冲区（可用于导出为 StaticMesh）
LidarPointCloudMeshing::FMeshBuffers MeshBuffers;
PointCloud->BuildStaticMeshBuffers(10.0f, &MeshBuffers, FTransform::Identity);

// 创建 StaticMesh 资产
UStaticMesh* Mesh = NewObject<UStaticMesh>();
FMeshDescription MeshDescription;
// ... 将 MeshBuffers 转换为 MeshDescription 并构建 Mesh
```

**使用裁剪体积（`ALidarClippingVolume`）**：

```cpp
// 在场景中放置裁剪体积，用于选择性隐藏/显示点云区域
ALidarClippingVolume* ClipVolume = GetWorld()->SpawnActor<ALidarClippingVolume>();
ClipVolume->bEnabled = true;
ClipVolume->Mode = ELidarClippingVolumeMode::ClipInside;  // 隐藏体积内的点
ClipVolume->Priority = 10;
```

**批量空间操作（ExecuteAction 模式）**：

```cpp
// 对球形区域内的所有可见点执行操作
PointCloud->ExecuteActionOnPointsInSphere(
    [](FLidarPointCloudPoint* Point)
    {
        // 着色：根据高程映射颜色
        float HeightRatio = (Point->Location.Z + 100.0f) / 200.0f;
        HeightRatio = FMath::Clamp(HeightRatio, 0.0f, 1.0f);
        Point->Color = FLinearColor(HeightRatio, 0.5f, 1.0f - HeightRatio).ToFColor(false);
    },
    FSphere(FVector::ZeroVector, 1000.0f),
    true  // 仅处理可见点
);
```

**异步计算法线**：

```cpp
// 使用编