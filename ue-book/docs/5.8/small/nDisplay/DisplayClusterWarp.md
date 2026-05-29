# DisplayClusterWarp

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 显示器集群扭曲映射 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `DisplayClusterWarp` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途
`DisplayClusterWarp` 模块是 nDisplay 插件的核心子模块之一，专门负责处理投影几何的扭曲（Warp）与混合（Blend）计算。它解决了在多显示器、投影映射和沉浸式环境（如 VR/CAVE）中，如何根据非标准的屏幕几何形状（例如曲面、不规则形状）正确渲染画面，使得图像在这些屏幕上看起来是连贯且不失真的问题。其核心功能是读取标准的 MPCDI 校准文件、PFM 文件或直接使用 UE 中的网格体作为几何源，计算出正确的投影矩阵和视锥体，从而实现像素级别的精确映射和混合。

## 使用场景
- 你需要构建一个由多台投影机组成的曲面屏幕或 CAVE 系统，需要进行像素级精确的投影校正和边缘融合。
- 你正在使用基于 MPCDI 或 PFM 格式的第三方硬件校准软件（如 Scalable Display Technologies）的结果来驱动 UE 内的渲染。
- 你希望在编辑器内直接使用一个静态网格体或程序化网格体的几何形状作为投影表面，并实时预览扭曲效果。

## 蓝图用法
本模块主要提供底层的 C++ 接口，供 nDisplay 的其他系统（如投影策略）调用。直接暴露给蓝图的接口集中在特定的组件和数据结构上。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `NDisplay Frustum Fit View Point` | 一个可生成的场景组件，用于定义投影视点，并配置“视锥体适配”策略。 | `UDisplayClusterInFrustumFitCameraComponent` |
| `FDisplayClusterWarpGeometryPFM` | 一个蓝图结构体，用于以类似 PFM 格式存储一个可扭曲的 3D 顶点网格。 | `FDisplayClusterWarpGeometryPFM` |
| `FDisplayClusterWarpGeometryOBJ` | 一个蓝图结构体，用于以类似 OBJ 格式存储一个可扭曲的 3D 网格（包含顶点、法线、UV 和三角形索引）。 | `FDisplayClusterWarpGeometryOBJ` |
| `EDisplayClusterWarpCameraProjectionMode` | 枚举，定义了相机投影是“适配”（Fit）几何体还是“填充”（Fill）几何体。 | `EDisplayClusterWarpCameraProjectionMode` |
| `EDisplayClusterWarpCameraViewTarget` | 枚举，定义了视锥体适配时相机的目标朝向是“几何中心”还是“匹配视点”。 | `EDisplayClusterWarpCameraViewTarget` |

### 使用示例（蓝图描述）
1.  **配置视点**：在你的 `ADisplayClusterRootActor` 或任何 `AActor` 上，添加一个 `UDisplayClusterInFrustumFitCameraComponent` 组件。
2.  **设置投影模式**：在组件的细节面板中，找到 **Frustum Fit** 分类。
    - 勾选 **Enable Frustum Fit** 以启用该策略。
    - 选择 **Frustum Fit Mode**（`EDisplayClusterWarpCameraProjectionMode`），决定是让整个几何体适配进相机视锥（`Fit`），还是让相机视锥填满几何体（`Fill`）。
    - 选择 **Frustum Fit Target**（`EDisplayClusterWarpCameraViewTarget`），决定相机朝向是基于几何中心还是匹配到你放置组件的位置。
3.  **获取几何数据**：通过 C++ 或其他 nDisplay 系统，你可以创建一个 `FDisplayClusterWarpBlend` 对象，然后调用 `ExportWarpMapGeometry` 方法将当前的扭曲几何数据导出到 `FDisplayClusterWarpGeometryOBJ` 蓝图结构体中，用于调试或后续处理。

## C++ 用法
该模块的核心 API 是工厂模式，用于创建 `IDisplayClusterWarpBlend` 接口实例。实际计算逻辑封装在这些实例内部。

### 头文件引入
```cpp
#include "DisplayClusterWarp/Public/IDisplayClusterWarp.h"
#include "DisplayClusterWarp/Public/IDisplayClusterWarpBlend.h"
#include "DisplayClusterWarp/Public/Containers/DisplayClusterWarpInitializer.h"
```

### 基本用法
从 MPCDI 文件创建扭曲混合接口。
（来源：`Public/IDisplayClusterWarp.h` 及 `Private/DisplayClusterWarpModule.h`）
```cpp
// 获取 DisplayClusterWarp 模块接口
IDisplayClusterWarp& WarpModule = IDisplayClusterWarp::Get();

// 准备从 MPCDI 文件创建的初始化参数
FDisplayClusterWarpInitializer_MPCDIFile InitParams;
InitParams.MPCDIFileName = TEXT("Path/To/Your/calibration.mpcdi");
InitParams.BufferId = TEXT("buffer_name");
InitParams.RegionId = TEXT("region_name");

// 创建 WarpBlend 实例
TSharedPtr<IDisplayClusterWarpBlend> WarpBlendInterface = WarpModule.Create(InitParams);

if (WarpBlendInterface.IsValid())
{
    // 成功创建，可以使用 WarpBlendInterface 进行后续操作
    // 例如，在合适的时机调用其接口方法
}
```

### 进阶用法
使用自定义网格体作为扭曲几何源。
（来源：`Public/IDisplayClusterWarp.h` 及 `Public/Containers/DisplayClusterWarpInitializer.h`）
```cpp
IDisplayClusterWarp& WarpModule = IDisplayClusterWarp::Get();

// 假设你已经有一个 UStaticMeshComponent 指针：MyWarpMeshComp
FDisplayClusterWarpInitializer_StaticMesh MeshInitParams;
MeshInitParams.WarpMeshComponent = MyWarpMeshComp;
MeshInitParams.OriginComponent = MyWarpMeshComp->GetOwner()->GetRootComponent(); // 设置原点组件
MeshInitParams.StaticMeshComponentLODIndex = 0; // 使用指定 LOD 级别

TSharedPtr<IDisplayClusterWarpBlend> MeshWarpBlend = WarpModule.Create(MeshInitParams);

if (MeshWarpBlend.IsValid())
{
    // 使用网格体初始化的 WarpBlend 接口
    // 它会读取网格体的顶点数据来计算扭曲
}
```

## Demo 示例
一个创建基于网格的扭曲混合对象并获取其 AABB 的最小示例。
**DisplayClusterWarpDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "DisplayClusterWarpDemo.generated.h"

class UStaticMeshComponent;
class IDisplayClusterWarpBlend;

UCLASS()
class UDisplayClusterWarpDemo : public UObject
{
	GENERATED_BODY()

public:
    /** 在提供的网格体组件上初始化一个扭曲混合对象，并获取其包围盒 */
    void InitializeWithMeshComponent(UStaticMeshComponent* MeshComponent);

private:
    TSharedPtr<IDisplayClusterWarpBlend> CurrentWarpBlend;
};
```
**DisplayClusterWarpDemo.cpp**
```cpp
#include "DisplayClusterWarpDemo.h"
#include "DisplayClusterWarp/Public/IDisplayClusterWarp.h"
#include "DisplayClusterWarp/Public/Containers/DisplayClusterWarpInitializer.h"
#include "Components/StaticMeshComponent.h"

void UDisplayClusterWarpDemo::InitializeWithMeshComponent(UStaticMeshComponent* MeshComponent)
{
    if (!MeshComponent || !IDisplayClusterWarp::IsAvailable())
    {
        return;
    }

    IDisplayClusterWarp& WarpModule = IDisplayClusterWarp::Get();

    // 设置初始化参数
    FDisplayClusterWarpInitializer_StaticMesh InitParams;
    InitParams.WarpMeshComponent = MeshComponent;
    // 假设网格组件的拥有者 Actor 的根组件作为原点
    InitParams.OriginComponent = MeshComponent->GetOwner()->GetRootComponent();

    // 创建实例
    CurrentWarpBlend = WarpModule.Create(InitParams);

    if (CurrentWarpBlend.IsValid())
    {
        // 为了进行几何计算，通常需要更新几何上下文
        const float WorldScale = 1.0f; // 世界缩放因子
        CurrentWarpBlend->UpdateGeometryContext(WorldScale);

        // 获取几何上下文以访问 AABB 等信息
        const FDisplayClusterWarpGeometryContext& GeomContext = CurrentWarpBlend->GetGeometryContext();
        const FBox& WarpAABB = GeomContext.AABBox.GetBox();

        UE_LOG(LogTemp, Log, TEXT("Warp Blend AABB Min: %s, Max: %s"),
            *WarpAABB.Min.ToString(), *WarpAABB.Max.ToString());
    }
}
```

## 模块依赖
本模块在构建时依赖以下非通用模块。在你的项目或模块的 `.Build.cs` 文件中，如果需要链接或使用 `DisplayClusterWarp` 的类型，需要添加对应的依赖。

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 提供编辑器功能支持，如属性编辑、场景组件预览等。 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为电影图表和nDisplay添加了对EXR多层输出的支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 将电影渲染管线中的WarpBlendAlpha模式合并到通用的WarpBlend功能中。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了混合现实生成器中的拓扑感知相机命名问题，并修复了MPCDI/ICVFX着色器中的不透明度混合。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 使输出帧编码回退路径能够正确处理非默认的DisplayGamma值。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当GUI纹理尺寸小于视口尺寸时出现的闪烁问题。 |

### 维护评价
- **活跃维护**：该模块在最近6个月内（2026年5月）有多次实质性功能更新和问题修复，涵盖了核心渲染管线、电影渲染、混合现实等多个方面。
- **成熟度高**：作为自2018年就存在的企业级功能，其架构非常成熟和稳定。
- **推荐使用**：是构建专业级多显示/投影系统（如虚拟制片、CAVE、大型投影映射）不可或缺的核心模块。建议结合最新的UE版本和文档使用。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- 官方文档：(无)