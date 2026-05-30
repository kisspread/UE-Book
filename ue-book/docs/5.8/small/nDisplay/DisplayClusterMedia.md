# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、编辑器工具） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterWarp` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterMoviePipeline` (Runtime), 等共 29 个模块 |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 中用于**多机同步集群渲染**的核心系统，专门解决"一台计算机无法满足渲染需求"的场景。它允许多台 PC 协同工作，将一个大型场景同步渲染并输出到多个显示器、投影仪或 LED 墙上，支持单目和立体（stereo）模式。

**核心能力包括：**

- **多节点同步渲染**：多台 PC 各自渲染场景的不同视角/区域，通过网络同步保持帧对齐
- **投影与几何校正**：支持多种投影模式（平面、圆柱、MPCDI warp 等），处理投影仪的几何变形和边缘融合
- **ICVFX 虚拟摄影机**：为 LED Volume 拍摄（虚拟制片）提供内嵌摄影机（Inner Camera）支持，处理 LED 屏上的虚拟背景渲染
- **媒体捕获与输入**：将渲染结果通过媒体框架输出（如 SDI/NDI），或将外部媒体源输入到视口中
- **色彩管理**：支持 OpenColorIO（OCIO）色彩空间转换和 PQ 色调映射
- **多用户协作**：支持多用户同时操作同一 nDisplay 配置
- **影片渲染队列集成**：与 MovieRenderQueue 深度集成，支持集群化的离线渲染

## 使用场景

- **LED Volume 虚拟制片**：你正在搭建一个 LED 影棚，需要用多台机器驱动 LED 墙实时渲染虚拟背景 → 使用 nDisplay 配合 ICVFX 组件
- **多投影仪 CAVE 系统**：你有一个 4 面 CAVE 沉浸式环境，每面墙由一台 PC + 投影仪驱动 → 使用 nDisplay 配置集群节点和投影策略
- **超宽屏环幕**：你需要在 3 台 PC 上同步渲染一个 180° 环幕画面 → 使用 nDisplay 的多节点配置和 warp/blend
- **多机离线渲染**：你有一个复杂的电影级场景，单机渲染太慢，想用多台机器并行渲染不同帧 → 使用 nDisplay + MovieRenderQueue 集群模式
- **SDI/NDI 视频输出**：你需要将引擎画面实时输出到广播级 SDI 设备 → 使用 DisplayClusterMedia 模块

## 蓝图用法

nDisplay 的蓝图 API 主要通过 `ADisplayClusterRootActor` 暴露，控制集群的运行时行为。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Cluster Node ID` | 获取当前集群节点的 ID | `UDisplayClusterBlueprintAPI` |
| `Get Viewport ID` | 获取当前视口 ID | `UDisplayClusterBlueprintAPI` |
| `Is Primary Node` | 判断当前节点是否为主节点 | `UDisplayClusterBlueprintAPI` |
| `Get Cluster Node Count` | 获取集群中的节点总数 | `UDisplayClusterBlueprintAPI` |
| `Set Cluster Event Listener` | 设置集群事件监听 | `UDisplayClusterBlueprintAPI` |
| `Barrier Timeout` | 设置以太网屏障同步超时（ms） | `UDisplayClusterMediaOutputSynchronizationPolicyEthernetBarrierBase` |
| `Margin (ms)` | 设置 V-blank 同步容差（ms） | `UDisplayClusterMediaOutputSynchronizationPolicyThresholdBase` |

### 使用示例（蓝图描述）

1. **判断当前节点是否为主节点**：
   - 从任意事件（如 BeginPlay）拉线 → 搜索 `Is Primary Node` → 分支判断 → 主节点执行特定逻辑（如控制 UI）

2. **配置媒体同步策略**：
   - 在 DisplayCluster 配置资产中，选择 Viewport 的 Media Output 同步策略
   - 选择 `Ethernet Barrier` 或 `V-blank` 策略
   - 设置 `Barrier Timeout (ms)`（1-10000）和 `Margin (ms)`（1-20）

## C++ 用法

nDisplay 的 C++ 用法主要涉及媒体捕获/输入系统和同步策略的配置。核心模块 `DisplayClusterMedia` 提供了完整的媒体管线抽象。

### 头文件引入

```cpp
#include "DisplayClusterMediaModule.h"
#include "DisplayClusterMediaCaptureBase.h"
#include "DisplayClusterMediaInputBase.h"
#include "DisplayClusterMediaHelpers.h"
```

### 基本用法

**媒体 ID 生成**（来自 `DisplayClusterMediaHelpers.h`）：

```cpp
#include "DisplayClusterMediaHelpers.h"

// 为视口生成唯一的媒体 ID
FString MediaId = DisplayClusterMediaHelpers::MediaId::GenerateMediaId(
    DisplayClusterMediaHelpers::MediaId::EMediaDeviceType::Output,
    DisplayClusterMediaHelpers::MediaId::EMediaOwnerType::Viewport,
    TEXT("Node1"),        // 集群节点 ID
    TEXT("MyNDisplay"),   // DCRA（DisplayCluster Root Actor）名称
    TEXT("VP_001"),       // 视口名称
    0                     // 索引
);

// 为 ICVFX 摄影机生成媒体 ID
FString CameraMediaId = DisplayClusterMediaHelpers::MediaId::GenerateMediaId(
    DisplayClusterMediaHelpers::MediaId::EMediaDeviceType::Input,
    DisplayClusterMediaHelpers::MediaId::EMediaOwnerType::ICVFXCamera,
    TEXT("Node1"),
    TEXT("MyNDisplay"),
    TEXT("Camera_001"),
    0
);
```

**生成 ICVFX 视口名称和 Tile 视口名称**：

```cpp
// 为 ICVFX 摄影机生成内部视口 ID
FString ICVFXViewportName = DisplayClusterMediaHelpers::GenerateICVFXViewportName(
    TEXT("Node1"), TEXT("Camera_001")
);

// 为分块（Tile）视口生成名称
FString TileViewportName = DisplayClusterMediaHelpers::GenerateTileViewportName(
    TEXT("VP_001"), FIntPoint(1, 0)  // 第 2 列第 1 行的 Tile
);

// 为 ICVFX 摄影机的 Tile 生成名称
FString ICVFXTileName = DisplayClusterMediaHelpers::GenerateICVFXTileViewportName(
    TEXT("Node1"), TEXT("Camera_001"), FIntPoint(2, 1)
);
```

### 进阶用法

**纹理拷贝与缩放**（渲染线程操作）：

```cpp
#include "DisplayClusterMediaHelpers.h"

// 在渲染线程上将源纹理缩放拷贝到目标纹理
void MyCustomRenderPass(FRHICommandListImmediate& RHICmdList)
{
    FRHITexture* SrcTexture = /* ... */;
    FRHITexture* DstTexture = /* ... */;
    FIntRect SrcRect(FIntPoint::ZeroValue, FIntPoint(1920, 1080));
    FIntRect DstRect(FIntPoint::ZeroValue, FIntPoint(3840, 2160));

    DisplayClusterMediaHelpers::ResampleTexture_RenderThread(
        RHICmdList, SrcTexture, DstTexture, SrcRect, DstRect
    );
}
```

**验证 Tile 布局**：

```cpp
// 检查 Tile 布局是否有效（最大 4x4）
FIntPoint TileLayout(2, 2);
FIntPoint MaxLayout(4, 4);
bool bValid = DisplayClusterMediaHelpers::IsValidLayout(TileLayout, MaxLayout);

// 检查 Tile 坐标是否在布局范围内
FIntPoint TilePos(1, 1);
bool bValidCoord = DisplayClusterMediaHelpers::IsValidTileCoordinate(TilePos, TileLayout);
```

## Demo 示例

以下示例展示如何在自定义模块中查询 nDisplay 的集群状态：

```cpp
// MyNDisplayHelper.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyNDisplayHelper.generated.h"

UCLASS()
class UMyNDisplayHelper : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    /** 检查当前节点是否为主节点，并返回节点信息 */
    UFUNCTION(BlueprintCallable, Category = "nDisplay Helper")
    bool GetClusterInfo(FString& OutNodeId, int32& OutNodeCount, bool& bOutIsPrimary) const;

    /** 为视口生成媒体 ID 并打印到日志 */
    UFUNCTION(BlueprintCallable, Category = "nDisplay Helper")
    void LogViewportMediaId(const FString& NodeId, const FString& DCRAName, const FString& ViewportName) const;
};
```

```cpp
// MyNDisplayHelper.cpp
#include "MyNDisplayHelper.h"
#include "DisplayClusterMediaHelpers.h"
#include "DisplayClusterBlueprintAPI.h"
#include "DisplayClusterRootActor.h"
#include "IDisplayCluster.h"
#include "IDisplayClusterClusterManager.h"

bool UMyNDisplayHelper::GetClusterInfo(FString& OutNodeId, int32& OutNodeCount, bool& bOutIsPrimary) const
{
    IDisplayCluster* DC = IDisplayCluster::Get();
    if (!DC)
    {
        return false;
    }

    IDisplayClusterClusterManager* ClusterMgr = DC->GetClusterMgr();
    if (!ClusterMgr)
    {
        return false;
    }

    OutNodeId = ClusterMgr->GetNodeId();
    bOutIsPrimary = ClusterMgr->IsPrimary();
    OutNodeCount = ClusterMgr->GetNodesAmount();

    return true;
}

void UMyNDisplayHelper::LogViewportMediaId(const FString& NodeId, const FString& DCRAName, const FString& ViewportName) const
{
    // 生成输出媒体 ID
    const FString OutputId = DisplayClusterMediaHelpers::MediaId::GenerateMediaId(
        DisplayClusterMediaHelpers::MediaId::EMediaDeviceType::Output,
        DisplayClusterMediaHelpers::MediaId::EMediaOwnerType::Viewport,
        NodeId, DCRAName, ViewportName, 0
    );

    // 生成输入媒体 ID
    const FString InputId = DisplayClusterMediaHelpers::MediaId::GenerateMediaId(
        DisplayClusterMediaHelpers::MediaId::EMediaDeviceType::Input,
        DisplayClusterMediaHelpers::MediaId::EMediaOwnerType::Viewport,
        NodeId, DCRAName, ViewportName, 0
    );

    UE_LOG(LogTemp, Log, TEXT("Viewport '%s' Output MediaID: %s"), *ViewportName, *OutputId);
    UE_LOG(LogTemp, Log, TEXT("Viewport '%s' Input  MediaID: %s"), *ViewportName, *InputId);
}
```

## 模块依赖

由于 nDisplay 包含 29 个模块，以下列出各子模块的**特有依赖**（非标准 Core/Engine/Slate 等已被省略）：

| 模块 | 用途 |
|---|---|
| `DisplayClusterMedia` | 依赖 `D3D12RHI`（DirectX 12 渲染接口，用于 GPU 纹理共享） |
| `DisplayClusterProjection` | 依赖 `UnrealEd`（投影配置编辑器支持） |
| `DisplayClusterWarp` | 依赖 `UnrealEd`（Warp/Blend 编辑器支持） |
| `DisplayClusterShaders` | 依赖 `UnrealEd`（自定义着色器编辑器支持） |
| `DisplayCluster` | 依赖 `UnrealEd`、`EditorWidgets`、`LevelEditor`（主模块编辑器集成） |
| `DisplayClusterRemoteControlInterceptor` | 依赖 `UnrealEd`（远程控制拦截器） |
| `DisplayClusterScenePreview` | 依赖 `UnrealEd`（场景预览） |
| `SharedMemoryMedia` | 依赖 `D3D12RHI`（共享内存媒体传输） |
| `ScalableMPCDI` | External 第三方库（MPCDI 投影校正格式支持） |

**使用者最常依赖的模块**：`DisplayCluster`、`DisplayClusterConfiguration`、`DisplayClusterProjection`、`DisplayClusterShaders`

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MovieGraph 和 nDisplay 添加 EXR 多层渲染输出支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 将 MoviePipeline 中的 WarpBlendAlpha 模式合并到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知的摄影机命名，以及 MPCDI/ICVFX 着色器中的不透明 alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码回退路径中正确处理非默认的 DisplayGamma 值 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**活跃维护中** ✅

nDisplay 是 Epic Games 的**旗舰企业级功能**，持续获得高频更新和功能增强：

- **高频更新**：最近 5 次提交全部集中在 10 天内（2026-05-16 至 2026-05-26），表明开发非常活跃
- **功能持续演进**：不断添加新特性（EXR 多层、MovieGraph 集成、WarpBlend 优化）
- **企业级支持**：由 Epic Games 官方维护，是虚拟制片（Virtual Production）和 LED Volume 的核心基础设施
- **跨平台支持**：同时支持 Win64 和 Linux
- **注意事项**：此插件**默认未启用**（`EnabledByDefault: false`），需在项目设置中手动启用；由于涉及多机同步、投影校正等专业领域，学习曲线较陡
- **推荐度**：如果你的工作涉及 LED Volume、CAVE 系统、多投影仪拼接或多机集群渲染，这是**必选插件**；普通游戏开发无需使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/RenderingAndGraphics/nDisplay/)（UE 官方 nDisplay 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)