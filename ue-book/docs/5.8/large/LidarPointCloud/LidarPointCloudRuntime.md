# LiDAR Point Cloud Support

> Adds support for importing, processing and rendering of LiDAR Point Clouds.

| 属性 | 值 |
|---|---|
| 中文名 | 激光雷达点云 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板、导入器等） |
| 模块 | `LidarPointCloudRuntime` (Runtime), `LidarPointCloudEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-01-28 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud) | |

## 用途

此插件为 UE5 提供完整的激光雷达（LiDAR）点云数据工作流支持。它解决的核心问题是：**如何在游戏引擎中高效地导入、存储、处理和渲染大规模点云数据**。

激光雷达扫描通常产生数百万到数十亿个 3D 空间点，每个点带有位置、颜色、强度、法线和分类信息。传统的网格化方法无法直接处理这类数据，因此该插件通过以下技术路线解决性能问题：

1. **八叉树（Octree）空间索引**：将点云数据组织成层次化的八叉树结构，支持高效的空间查询、LOD 和视锥体裁剪
2. **多线程数据流**：支持按需加载节点数据（Streaming），避免一次性将所有点加载到内存
3. **全局 LOD 管理器**：跨所有点云实例统一管理点预算（Point Budget），根据屏幕占比动态选择要渲染的节点
4. **GPU 端渲染**：通过自定义 Vertex Factory 和 Structured Buffer 将点数据直接传递到 GPU，支持点精灵（Sprite）和光线追踪
5. **可扩展的文件 IO**：通过 Handler 模式支持 LAS/LAZ、E57、ASCII（XYZ/TXT/PTS）等主流点云格式

简而言之：这个插件让你能在 UE5 场景中像放置网格体一样放置和交互激光雷达扫描数据，并以合理的帧率渲染数百万个点。

## 使用场景

- **建筑/BIM 可视化**：导入激光雷达扫描的建筑现场数据，在 UE5 中做施工进度对比或竣工验收
- **自动驾驶仿真**：将道路环境的点云数据导入引擎，用于自动驾驶算法测试和场景重建
- **数字孪生**：将工厂、城市等大型设施的激光雷达扫描结果用于实时可视化
- **地形与环境建模**：导入无人机激光雷达扫描的地形数据，用于开放世界游戏的地形参考
- **考古与文化遗产**：对历史建筑或遗址进行激光扫描后，在引擎中做虚拟漫游
- **影视虚拟制片**：将实景扫描的点云用于虚拟场景搭建和实景匹配

## 蓝图用法

该插件在 `ULidarPointCloud`、`ULidarPointCloudComponent`、`ALidarPointCloudActor` 和 `ALidarBPLibrary` 中暴露了大量 BlueprintCallable/BlueprintPure 函数。

### 核心节点

#### 资产查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetNumPoints` | 获取点云总点数 | `ULidarPointCloud` |
| `GetNumVisiblePoints` | 获取当前可见点数 | `ULidarPointCloud` |
| `GetNumNodes` | 获取八叉树节点数 | `ULidarPointCloud` |
| `GetNumLODs` | 获取 LOD 层级数 | `ULidarPointCloud` |
| `GetEstimatedPointSpacing` | 获取估算的点间距 | `ULidarPointCloud` |
| `GetDataSize` | 获取点云占用内存（MB） | `ULidarPointCloud` |
| `GetBounds` | 获取点云包围盒 | `ULidarPointCloud` |
| `IsFullyLoaded` | 是否所有节点已持久加载到内存 | `ULidarPointCloud` |
| `IsOptimizedForDynamicData` | 是否为动态数据优化模式 | `ULidarPointCloud` |

#### 空间查询（点云资产级别）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `HasPointsInSphere` | 球体内是否存在点 | `ULidarPointCloud` |
| `HasPointsInBox` | 盒体内是否存在点 | `ULidarPointCloud` |
| `HasPointsByRay` | 射线是否经过任何点 | `ULidarPointCloud` |
| `GetPointsAsCopies` | 获取所有点的副本 | `ULidarPointCloud` |
| `GetPointsInSphereAsCopies` | 获取球体内点的副本 | `ULidarPointCloud` |
| `GetPointsInBoxAsCopies` | 获取盒体内点的副本 | `ULidarPointCloud` |
| `LineTraceSingle` | 单点射线检测 | `ULidarPointCloud` |
| `LineTraceMulti` | 多点射线检测 | `ULidarPointCloud` |

#### 空间查询（组件级别，自动处理世界坐标变换）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `HasPointsInSphere` | 组件空间中的球体查询 | `ULidarPointCloudComponent` |
| `HasPointsInBox` | 组件空间中的盒体查询 | `ULidarPointCloudComponent` |
| `HasPointsByRay` | 组件空间中的射线查询 | `ULidarPointCloudComponent` |
| `GetPointsInSphereAsCopies` | 获取组件空间中球体内点副本 | `ULidarPointCloudComponent` |
| `GetPointsInBoxAsCopies` | 获取组件空间中盒体内点副本 | `ULidarPointCloudComponent` |
| `LineTraceSingle` | 组件空间中的单点射线检测 | `ULidarPointCloudComponent` |
| `LineTraceMulti` | 组件空间中的多点射线检测 | `ULidarPointCloudComponent` |

#### 全局静态函数（Library，无需引用资产）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetPointsInSphereAsCopies` | 通过 WorldContext 获取球体内点 | `ALidarBPLibrary` |
| `GetPointsInBoxAsCopies` | 通过 WorldContext 获取盒体内点 | `ALidarBPLibrary` |
| `LineTraceSingle` | 全局单点射线检测 | `ALidarBPLibrary` |
| `LineTraceMulti` | 全局多点射线检测 | `ALidarBPLibrary` |

#### 可见性控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetVisibilityOfPointsInSphere` | 设置球体内点的可见性 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `SetVisibilityOfPointsInBox` | 设置盒体内点的可见性 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `SetVisibilityOfFirstPointByRay` | 设置射线命中的第一个点的可见性 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `SetVisibilityOfPointsByRay` | 设置射线命中的所有点的可见性 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `HideAll` | 隐藏所有点 | `ULidarPointCloud` |
| `UnhideAll` | 显示所有点 | `ULidarPointCloud` |

#### 颜色操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplyColorToAllPoints` | 给所有点上色 | `ULidarPointCloud` |
| `ApplyColorToPointsInSphere` | 给球体内点上色 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `ApplyColorToPointsInBox` | 给盒体内点上色 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `ApplyColorToFirstPointByRay` | 给射线命中的第一个点上色 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `ApplyColorToPointsByRay` | 给射线命中的所有点上色 | `ULidarPointCloud` / `ULidarPointCloudComponent` |

#### 点操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InsertPoint` | 向八叉树插入单个点 | `ULidarPointCloud` |
| `InsertPoints` | 向八叉树批量插入点（多线程） | `ULidarPointCloud` |
| `RemovePoint` | 删除指定点 | `ULidarPointCloud` |
| `RemovePointsInSphere` | 删除球体内所有点 | `ULidarPointCloudComponent` |
| `RemovePointsInBox` | 删除盒体内所有点 | `ULidarPointCloudComponent` |
| `RemoveFirstPointByRay` | 删除射线命中的第一个点 | `ULidarPointCloudComponent` |
| `RemovePointsByRay` | 删除射线命中的所有点 | `ULidarPointCloudComponent` |

#### 碰撞

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BuildCollision` | 使用当前设置构建碰撞网格 | `ULidarPointCloud` |
| `BuildCollisionWithCallback` | 异步构建碰撞（Latent） | `ULidarPointCloud` |
| `RemoveCollision` | 移除碰撞网格 | `ULidarPointCloud` |
| `HasCollisionData` | 是否有碰撞数据 | `ULidarPointCloud` |
| `SetOptimalCollisionError` | 设置最优碰撞误差 | `ULidarPointCloud` |

#### 数据管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Reimport` | 从原始文件重新导入（Latent） | `ULidarPointCloud` |
| `Export` | 导出到文件 | `ULidarPointCloud` |
| `LoadAllNodes` | 持久加载所有节点到内存 | `ULidarPointCloud` |
| `Initialize` | 用新边界重新初始化（清空数据） | `ULidarPointCloud` |
| `CenterPoints` | 居中点云 | `ULidarPointCloud` |
| `RestoreOriginalCoordinates` | 恢复原始坐标 | `ULidarPointCloud` |
| `SetLocationOffset` | 设置偏移量 | `ULidarPointCloud` |
| `SetOptimizedForDynamicData` | 切换动态数据优化模式 | `ULidarPointCloud` |
| `RefreshBounds` | 重新计算点边界 | `ULidarPointCloud` |
| `RefreshRendering` | 刷新渲染数据 | `ULidarPointCloud` |
| `MarkPointVisibilityDirty` | 标记可见性已变更 | `ULidarPointCloud` |

#### 组件属性

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetPointCloud` | 设置引用的点云资产 | `ULidarPointCloudComponent` / `ALidarPointCloudActor` |
| `GetPointCloud` | 获取引用的点云资产 | `ULidarPointCloudComponent` / `ALidarPointCloudActor` |
| `SetPointShape` | 设置点精灵形状（圆形/方形） | `ULidarPointCloudComponent` |
| `GetPointShape` | 获取当前点精灵形状 | `ULidarPointCloudComponent` |
| `ApplyRenderingParameters` | 应用颜色调整参数到材质 | `ULidarPointCloudComponent` |

#### 类型转换

| 节点 | 说明 | 所在类 |
|---|---|---|
| `NormalFromVector` | Vector → LidarPointCloudNormal | `ALidarBPLibrary` |
| `Normal to Vector`（自动转换） | LidarPointCloudNormal → Vector | `ALidarBPLibrary` |
| `Vector to Normal`（自动转换） | Vector → LidarPointCloudNormal | `ALidarBPLibrary` |

#### 文件导入（蓝图 API）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Lidar Point Cloud From File (ASCII)` | 从 ASCII 文件创建点云资产（Latent） | `ULidarPointCloudFileIO_ASCII` |

### 使用示例（蓝图描述）

**基本放置与渲染：**
1. 在内容浏览器中右键 → Import → 选择 .las/.e57/.xyz 文件
2. 在场景中放置 `ALidarPointCloudActor`，或在任意 Actor 上添加 `ULidarPointCloudComponent`
3. 在组件的 Details 面板中将 `PointCloud` 属性设置为导入的资产
4. 调整 `PointSize`（点大小）、`ColorSource`（颜色来源：原始颜色/分类/高度渐变/强度）等外观属性

**射线检测交互：**
1. 获取玩家控制器 → Get Hit Result Under Cursor
2. 将 Hit 的 Location 作为 Origin，将 `(0,0,-1)` 作为 Direction
3. 连接到 `ULidarPointCloudComponent::LineTraceSingle`，设置 Radius（如 5.0）和 bVisibleOnly=true
4. 用 Out Hit 的 Color 字段做 UI 显示，或用 Location 做后续逻辑

**运行时动态修改点云：**
1. 调用 `SetVisibilityOfPointsInSphere(false, Location, 100.0)` 隐藏指定区域的点
2. 调用 `MarkPointVisibilityDirty()` 通知渲染更新
3. 或调用 `ApplyColorToPointsInSphere(FColor::Red, Location, 100.0, true)` 高亮区域

**从 ASCII 文件动态创建（蓝图）：**
1. 使用 `ULidarPointCloudFileIO_ASCII::CreatePointCloudFromFile` Latent 节点
2. 配置 `Columns` 结构体（LocationX/Y/Z 的列索引，颜色列索引等）
3. 设置 `RGBRange` 以正确映射强度/颜色值
4. 等待 `AsyncMode` 返回 Success 后获取 `PointCloud` 输出引脚

## C++ 用法

### 头文件引入

```cpp
#include "LidarPointCloud.h"
#include "LidarPointCloudComponent.h"
#include "LidarPointCloudActor.h"
#include "LidarPointCloudOctree.h"
#include "LidarPointCloudShared.h"
#include "IO/LidarPointCloudFileIO.h"
#include "IO/LidarPointCloudFileIO_LAS.h"
#include "IO/LidarPointCloudFileIO_ASCII.h"
#include "Meshing/LidarPointCloudMeshing.h"
```

### 基本用法

从源码中提取的典型使用模式：

```cpp
// 创建点云资产并插入点
ULidarPointCloud* PointCloud = NewObject<ULidarPointCloud>();

// 初始化八叉树边界
FBox Bounds(FVector(-5000, -5000, -5000), FVector(5000, 5000, 5000));
PointCloud->Initialize(Bounds);

// 创建单个点
FLidarPointCloudPoint Point(FVector3f(100.f, 200.f, 300.f), 1.0f, 0.5f, 0.2f, 1.0f);

// 插入点，处理重复方式为忽略
PointCloud->InsertPoint(Point, ELidarPointCloudDuplicateHandling::Ignore, true, FVector::ZeroVector);

// 批量插入点（多线程）
TArray<FLidarPointCloudPoint> Points;
for (int32 i = 0; i < 100000; ++i)
{
    Points.Add(FLidarPointCloudPoint(
        FVector3f(FMath::RandRange(-5000.f, 5000.f),
                  FMath::RandRange(-5000.f, 5000.f),
                  FMath::RandRange(-5000.f, 5000.f)),
        FMath::RandRange(0.f, 1.f),  // R
        FMath::RandRange(0.f, 1.f),  // G
        FMath::RandRange(0.f, 1.f),  // B
        1.0f                          // A
    ));
}
PointCloud->InsertPoints(Points, ELidarPointCloudDuplicateHandling::SelectFirst, true, FVector::ZeroVector);
```

### 射线检测

```cpp
// 单点射线检测
FVector Origin = FVector(0, 0, 1000);
FVector Direction = FVector(0, 0, -1);
float Radius = 5.0f;
bool bVisibleOnly = true;

FLidarPointCloudPoint HitPoint;
bool bHit = PointCloud->LineTraceSingle(Origin, Direction, Radius, bVisibleOnly, HitPoint);
if (bHit)
{
    UE_LOG(LogTemp, Log, TEXT("Hit point at: %s"), *HitPoint.Location.ToString());
}

// 多点射线检测
TArray<FLidarPointCloudPoint> Hits;
bool bAnyHit = PointCloud->LineTraceMulti(Origin, Direction, Radius, bVisibleOnly, true, Hits);
```

### 空间查询

```cpp
// 查询球体内的点
TArray<FLidarPointCloudPoint> SpherePoints;
PointCloud->GetPointsInSphereAsCopies(SpherePoints, 
    FSphere(FVector(0, 0, 0), 100.0f), true, true);

// 查询盒体内的点
TArray<FLidarPointCloudPoint> BoxPoints;
PointCloud->GetPointsInBoxAsCopies(BoxPoints, 
    FBox(FVector(-50, -50, -50), FVector(50, 50, 50)), true, true);
```

### 碰撞构建

```cpp
// 设置碰撞精度并构建
PointCloud->MaxCollisionError = 10.0f;
PointCloud->BuildCollision([](bool bSuccess)
{
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Collision built successfully"));
    }
});

// 或使用蓝图 Latent 版本（C++ 中通过 FLatentActionInfo 调用）
```

### 法线计算

```cpp
// 先加载所有节点
PointCloud->LoadAllNodes();

// 计算法线
// NormalsQuality: 1-100（越高越精确但越慢）
// NormalsNoiseTolerance: 0.0+（越高越抗噪但可能丢失细节）
PointCloud->NormalsQuality = 50;
PointCloud->NormalsNoiseTolerance = 0.0f;
// 触发重算（通过 PostEditChangeProperty 或手动流程）
```

### 数据流控制

```cpp
// 动态数据优化模式（适合实时流数据，如无人机实时扫描）
PointCloud->SetOptimizedForDynamicData(true);

// 持久加载所有节点到内存（避免按需流式加载的延迟）
if (!PointCloud->IsFullyLoaded())
{
    PointCloud->LoadAllNodes();
}

// 中心化点云（避免大坐标精度问题）
PointCloud->CenterPoints();

// 恢复原始坐标
PointCloud->RestoreOriginalCoordinates();
```

### 文件 IO

```cpp
// 导入 LAS 文件
FString Filename = TEXT("/path/to/scan.las");
TSharedPtr<FLidarPointCloudImportSettings> ImportSettings = 
    ULidarPointCloudFileIO::GetImportSettings(Filename);
FLidarPointCloudImportResults Results;
bool bSuccess = ULidarPointCloudFileIO::Import(Filename, ImportSettings, Results);

// 查询支持的格式
TArray<FString> ImportExtensions = ULidarPointCloudFileIO::GetSupportedImportExtensions();
TArray<FString> ExportExtensions = ULidarPointCloudFileIO::GetSupportedExportExtensions();

// 导出
PointCloud->Export(TEXT("/path/to/output.las"));
```

## Demo 示例

### 最小完整示例：加载点云并渲染

**MyLidarActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LidarPointCloudActor.h"
#include "MyLidarActor.generated.h"

UCLASS()
class AMyLidarActor : public ALidarPointCloudActor
{
    GENERATED_BODY()

public:
    AMyLidarActor();

    /** 创建并填充测试点云 */
    UFUNCTION(BlueprintCallable, Category = "Lidar Demo")
    void CreateTestPointCloud(int32 NumPoints = 100000);

    /** 对鼠标点击位置做射线检测 */
    UFUNCTION(BlueprintCallable, Category = "Lidar Demo")
    bool TraceFromCamera(FVector WorldLocation, FVector WorldDirection, FLidarPointCloudPoint& OutHit);

    /** 高亮指定区域的点 */
    UFUNCTION(BlueprintCallable, Category = "Lidar Demo")
    void HighlightArea(FVector Center, float Radius);

    /** 清除高亮 */
    UFUNCTION(BlueprintCallable, Category = "Lidar Demo")
    void ClearHighlights();
};
```

**MyLidarActor.cpp**

```cpp
#include "MyLidarActor.h"
#include "LidarPointCloud.h"
#include "LidarPointCloudComponent.h"
#include "LidarPointCloudShared.h"

AMyLidarActor::AMyLidarActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyLidarActor::CreateTestPointCloud(int32 NumPoints)
{
    ULidarPointCloud* PC = GetPointCloud();
    if (!PC)
    {
        PC = NewObject<ULidarPointCloud>(GetTransientPackage(), TEXT("TestCloud"));
        GetPointCloudComponent()->SetPointCloud(PC);
    }

    // 初始化边界
    const float HalfSize = 5000.0f;
    FBox Bounds(FVector(-HalfSize), FVector(HalfSize));
    PC->Initialize(Bounds);

    // 生成随机点
    TArray<FLidarPointCloudPoint> Points;
    Points.Reserve(NumPoints);
    for (int32 i = 0; i < NumPoints; ++i)
    {
        float X = FMath::RandRange(-HalfSize, HalfSize);
        float Y = FMath::RandRange(-HalfSize, HalfSize);
        // 创建地形形状：高度基于距离中心的远近
        float Dist = FMath::Sqrt(X * X + Y * Y);
        float Z = FMath::Sin(Dist * 0.001f) * 500.0f + FMath::RandRange(-10.f, 10.f);

        float R = FMath::Clamp((Z + 500.f) / 1000.f, 0.f, 1.f);
        float G = FMath::Clamp(1.f - FMath::Abs(Z) / 500.f, 0.f, 1.f);
        float B = FMath::Clamp((-Z + 500.f) / 1000.f, 0.f, 1.f);

        Points.Add(FLidarPointCloudPoint(FVector3f(X, Y, Z), R, G, B, 1.0f));
    }

    // 插入点（自动处理重复）
    PC->InsertPoints(Points, ELidarPointCloudDuplicateHandling::Ignore, true, FVector::ZeroVector);

    UE_LOG(LogTemp, Log, TEXT("Created point cloud with %lld points"), PC->GetNumPoints());
}

bool AMyLidarActor::TraceFromCamera(FVector WorldLocation, FVector WorldDirection, FLidarPointCloudPoint& OutHit)
{
    ULidarPointCloudComponent* Comp = GetPointCloudComponent();
    if (!Comp) return false;

    return Comp->LineTraceSingle(WorldLocation, WorldDirection, 5.0f, true, OutHit);
}

void AMyLidarActor::HighlightArea(FVector Center, float Radius)
{
    ULidarPointCloudComponent* Comp = GetPointCloudComponent();
    if (!Comp) return;

    // 将区域内的点设为红色
    Comp->ApplyColorToPointsInSphere(FColor::Red, Center, Radius, true);
}

void AMyLidarActor::ClearHighlights()
{
    ULidarPointCloud* PC = GetPointCloud();
    if (!PC) return;

    // 恢复原始颜色（重新导入或使用存储的原始颜色）
    PC->Reimport(FVector::ZeroVector); // 简化示意
}
```

## 模块依赖

### LidarPointCloudRuntime

从 `LidarPointCloudRuntime.Build.cs` 分析，该模块的核心依赖：

| 模块 | 用途 |
|---|---|
| `MeshDescription` | 静态网格体生成（Meshing） |
| `RenderCore` | 自定义顶点工厂、渲染缓冲区 |
| `RHI` | GPU 资源管理（SRV、UniformBuffer） |
| `RayTracing` | 光线追踪几何体支持 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

### LidarPointCloudEditor

编辑器模块额外依赖：

| 模块 | 用途 |
|---|---|
| `AssetTools` | 资产导入/导出集成 |
| `ContentBrowser` | 内容浏览器扩展 |

无其他特殊依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联通知逻辑 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退之前的改动 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口客户端关联通知重构（与上面相关） |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 光线追踪动态几何参数更新，统一网格批次所有权 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |

### 维护评价

**活跃维护中。** 该插件创建于 2020 年初，作为 Epic Games 企业级（Enterprise）插件持续维护。近期更新（2026 年 4-5 月）显示仍在跟随引擎核心渲染系统的变更（如光线追踪接口调整、视口系统重构），并修复平台兼容性问题。

**优点：**
- 由 Epic Games 官方维护，代码质量有保障
- 功能完善：导入、编辑、渲染、碰撞、LOD 全流程覆盖
- 支持主流点云格式（LAS/LAZ、E57、ASCII）
- 自定义渲染管线，支持光线追踪
- 纹理数据流式加载，适合大数据集

**注意事项：**
- 默认未启用（`EnabledByDefault=false`），需在 Project Settings → Plugins 中手动启用
- 处理超大规模点云（数十亿点）时需关注内存和流式加载设置
- `bOptimizedForDynamicData` 模式禁用 LOD 管线，适合实时流但影响运行时性能
- E57 格式支持依赖外部库（`LIBE57SUPPORTED` 宏），可能需要额外编译配置
- 建议在 Project Settings 中配置 `ULidarPointCloudSettings`（八叉树参数、流式加载超时、线程批处理大小等）

**推荐使用：** ✅ 推荐。适合任何需要在 UE5 中处理激光雷达点云数据的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）