# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 的**集群渲染（Clustered Rendering）**系统，用于将一个 UE 场景的画面实时分发到多台 PC 上进行同步渲染，最终在多屏幕/多投影仪环境中拼接出一幅完整的超宽或立体视觉画面。

它解决的核心问题是：**单台 PC 无法驱动超高分辨率或多通道投影的渲染需求**。典型场景包括：

- **LED 虚拟摄影棚（Virtual Production / ICVFX）**：摄影机对着巨大的 LED 墙拍摄，墙上的画面由多台渲染节点实时同步生成
- **CAVE / Powerwall 沉浸式显示**：多面投影的沉浸式空间（每面墙一台 PC 负责渲染）
- **大型环幕/穹顶投影**：天文馆、模拟器等需要 360° 环绕投影的场景
- **多机同步立体渲染**：为左眼/右眼分别由不同 PC 渲染，实现被动立体显示

nDisplay 通过配置文件（.ndisplay）定义显示拓扑（哪些 PC、哪些屏幕、投影方式），在运行时自动进行帧同步、网络复制、投影变形（Warp/Blend）和色彩校正，让多台机器看起来就像一台机器渲染了一整面墙。

> ⚠️ 此插件默认未启用（`EnabledByDefault: false`），需要在插件管理器中手动开启。

## 使用场景

- 你在搭建 **LED 虚拟摄影棚**（ICVFX Stage）→ 用 nDisplay 配合 nDisplay 配置器定义 LED 墙的拓扑和投影
- 你需要在**多台 PC** 上同步渲染同一个场景并拼接显示 → 用 nDisplay 的集群复制功能
- 你做的是**飞行/驾驶模拟器**，需要多通道环幕投影 → 用 nDisplay 配合投影变形（Warp/Blend）
- 你需要用 **Movie Pipeline** 离线渲染多机位/超高分辨率画面 → 用 nDisplay 的 MoviePipeline 集成
- 你有 CAVE / Powerwall 等**沉浸式显示系统** → 用 nDisplay 定义多面投影拓扑

## 蓝图用法

nDisplay 的蓝图 API 主要围绕 **nDisplay Root Actor** 展开，通过放置 `ADisplayClusterRootActor` 到场景中，并在编辑器中配置其 .ndisplay 配置文件来驱动整个集群渲染。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Root Actor` | 从当前世界获取 nDisplay 根 Actor | `UDisplayClusterBlueprintAPI` |
| `Get Cluster Info` | 获取当前集群节点信息（是主节点还是从节点） | `UDisplayClusterBlueprintAPI` |
| `Start Session` | 启动 nDisplay 渲染会话 | `UDisplayClusterBlueprintAPI` |
| `Stop Session` | 停止 nDisplay 渲染会话 | `UDisplayClusterBlueprintAPI` |
| `Set Cluster Sync` | 设置集群同步参数 | `ADisplayClusterRootActor` |

### 使用示例

在场景中放置 `ADisplayClusterRootActor`，在其 Details 面板中加载 `.ndisplay` 配置文件。配置文件定义了：
1. **Cluster** — 集群节点列表（主节点 IP、从节点 IP）
2. **Screen** — 每个节点负责渲染的屏幕/视口
3. **Projection** — 投影类型（平面、MPCDI、Mesh、EasyBlend 等）
4. **Warp & Blend** — 边缘融合和几何校正

蓝图中可通过 `GetDisplayClusterRootActor` 获取实例，然后调用运行时 API 控制渲染行为。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterModule.h"
#include "DisplayClusterRootActor.h"
#include "IDisplayCluster.h"
```

### 基本用法

**获取 nDisplay 模块接口，查询集群状态**：

```cpp
// 来源: DisplayClusterEditor/Public/DisplayClusterEditorEngine.h
#include "IDisplayCluster.h"

// 获取 nDisplay 模块单例
IPDisplayCluster* DisplayCluster = IPDisplayCluster::Get();
if (DisplayCluster && DisplayCluster->IsModuleInitialized())
{
    // 检查当前节点是否为集群主节点（Primary / master）
    bool bIsPrimary = DisplayCluster->IsPrimary();
    
    // 获取集群节点 ID
    FString NodeId = DisplayCluster->GetNodeId();
    
    UE_LOG(LogTemp, Log, TEXT("Node %s, Primary: %s"), *NodeId, bIsPrimary ? TEXT("Yes") : TEXT("No"));
}
```

**在编辑器中查找 nDisplay Root Actor**：

```cpp
// 来源: DisplayClusterEditor/Public/DisplayClusterEditorEngine.h
ADisplayClusterRootActor* FindDisplayClusterRootActor(UWorld* InWorld)
{
    if (!InWorld) return nullptr;

    for (TActorIterator<ADisplayClusterRootActor> It(InWorld); It; ++It)
    {
        return *It; // 场景中通常只有一个 Root Actor
    }
    return nullptr;
}
```

### 进阶用法

**监听 PIE 会话的开始和结束（编辑器集成）**：

```cpp
// 来源: DisplayClusterEditor/Public/DisplayClusterEditorEngine.h
// UDisplayClusterEditorEngine 演示了如何在编辑器中集成 nDisplay PIE 逻辑

// 注册 PIE 开始/结束回调
FDelegateHandle BeginPIEDelegate = FEditorDelegates::BeginPIE.AddUObject(this, &ThisClass::OnBeginPIE);
FDelegateHandle EndPIEDelegate = FEditorDelegates::EndPIE.AddUObject(this, &ThisClass::OnEndPIE);

void OnBeginPIE(const bool bSimulate)
{
    bIsActivePIE = true;
    // nDisplay PIE 会话启动时的处理逻辑
    UE_LOG(LogDisplayClusterEditorEngine, Log, TEXT("nDisplay PIE session started"));
}

void OnEndPIE(const bool bSimulate)
{
    bIsActivePIE = false;
    UE_LOG(LogDisplayClusterEditorEngine, Log, TEXT("nDisplay PIE session ended"));
}
```

**通过编辑器设置控制 nDisplay 行为**：

```cpp
// 来源: DisplayClusterEditor/Private/Settings/DisplayClusterEditorSettings.h
#include "DisplayClusterEditorSettings.h"

// 获取 nDisplay 编辑器设置
const UDisplayClusterEditorSettings* Settings = GetDefault<UDisplayClusterEditorSettings>();
if (Settings->bEnabled)
{
    // nDisplay 已启用，某些引擎类和设置已被覆盖
    UE_LOG(LogDisplayClusterEditor, Log, TEXT("nDisplay is active, engine overrides enabled"));
}

if (Settings->bClusterReplicationEnabled)
{
    // 集群复制已启用，NetDriver 被替换为 DisplayClusterNetDriver
    UE_LOG(LogDisplayClusterEditor, Log, TEXT("Cluster replication enabled"));
}
```

## Demo 示例

**最小编辑器模块注册示例（展示 nDisplay Editor 模块结构）**：

```cpp
// MyNDisplayEditorHelper.h
#pragma once

#include "CoreMinimal.h"
#include "IDisplayCluster.h"
#include "DisplayClusterRootActor.h"

class FMyNDisplayEditorHelper
{
public:
    /** 初始化 nDisplay 连接 */
    void Initialize()
    {
        // 获取 nDisplay 模块
        IPDisplayCluster* DCModule = IPDisplayCluster::Get();
        if (!DCModule || !DCModule->IsModuleInitialized())
        {
            UE_LOG(LogTemp, Warning, TEXT("nDisplay module is not initialized"));
            return;
        }

        bInitialized = true;
        UE_LOG(LogTemp, Log, TEXT("nDisplay connection established, NodeId: %s"), 
            *DCModule->GetNodeId());
    }

    /** 在指定世界中查找 Root Actor 并获取配置 */
    ADisplayClusterRootActor* GetRootActor(UWorld* World) const
    {
        if (!World) return nullptr;

        for (TActorIterator<ADisplayClusterRootActor> It(World); It; ++It)
        {
            return *It;
        }
        return nullptr;
    }

    /** 检查当前是否为主节点 */
    bool IsPrimaryNode() const
    {
        IPDisplayCluster* DCModule = IPDisplayCluster::Get();
        return DCModule && DCModule->IsPrimary();
    }

private:
    bool bInitialized = false;
};
```

```cpp
// MyNDisplayEditorHelper.cpp
#include "MyNDisplayEditorHelper.h"

// 所有逻辑已在头文件中内联实现
```

## 模块依赖

以下是从各模块 Build.cs 提取的**特殊依赖**（非 Core/Engine/Slate 等常见模块）：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器扩展功能（多个模块依赖） |
| `EditorWidgets` | 编辑器自定义控件 |
| `LevelEditor` | 关卡编辑器集成 |
| `D3D12RHI` | Direct3D 12 渲染硬件接口（Media/SharedMemoryMedia 模块依赖） |
| `ScalableMPCDI` | 第三方 MPCDI 投影格式库（External 类型） |

> 注意：nDisplay 包含 29 个子模块，涵盖核心运行时、编辑器 UI、投影变形、色彩分级、媒体输出、集群监控、Movie Pipeline 集成等功能。使用时根据具体需求引入对应模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | Movie Pipeline 新增多层 EXR 输出支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并 WarpBlendAlpha 模式到统一的 WarpBlend 模式 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知摄像机命名及 MPCDI 着色器不透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时支持非默认 DisplayGamma 设置 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**⭐ 活跃维护中**

- **创建时间**：2018 年 6 月（约 8 年历史），最初为 UE4 4.20 引入的企业级功能
- **最近更新频率**：非常活跃，最近一周内有多次提交（截至 2026-05-26）
- **更新内容**：持续的功能增强（EXR 多层支持、着色器改进）和 Bug 修复，表明这是 Epic **重点维护的核心功能**
- **适用场景**：虚拟制片（Virtual Production）是 Epic 的战略方向，nDisplay 是其中的关键基础设施
- **注意事项**：
  - 默认未启用（`EnabledByDefault: false`），需手动开启
  - 29 个子模块，架构复杂，学习曲线较陡
  - 需要多台 PC 和投影/LED 硬件配合使用
  - 仅支持 Win64 和 Linux 平台

**推荐使用**：如果你在做虚拟制片、沉浸式显示或多通道投影项目，nDisplay 是唯一选择，且 Epic 持续投入维护。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/RenderingAndGraphics/nDisplay/Overview/)（虚幻引擎官方 nDisplay 文档）