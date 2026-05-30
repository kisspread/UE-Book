# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、Shader、配置模板） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 的**多机集群同步渲染系统**，用于将一个虚幻场景的渲染输出同步分配到多台 PC 控制的多块屏幕上，实现超大视场角的沉浸式显示。

核心解决的问题：
- **LED 虚拟摄影棚（LED Volume）**：将虚拟场景精准投射到 LED 墙面上，配合摄像机追踪实现虚实融合
- **CAVE 沉浸室**：多面投影构成的沉浸式环境（通常 3-6 面）
- **穹顶/球幕投影**：天文馆、飞行模拟器等曲面投影场景
- **多屏拼接**：超宽视角的驾驶模拟器、主题乐园骑乘设施
- **ICVFX（In-Camera VFX）**：电影级虚拟制片的核心技术，摄像机在 LED 墙前拍摄时，墙上的画面随摄像机视角实时更新

系统采用 **Master-Node 架构**：一台主机（Master）运行游戏逻辑并协调渲染，多台渲染节点（Node）各自渲染负责的屏幕区域，通过集群网络同步帧数据。

**重要**：该插件默认关闭（`EnabledByDefault: false`），需要在项目设置中手动启用。

## 使用场景

- 你在搭建 **LED 虚拟摄影棚**，需要让多台渲染 PC 同步输出到 LED 墙的不同区域 → 用 nDisplay
- 你在建造 **CAVE 沉浸式环境**，多面投影需要精确拼接和变形校正 → 用 nDisplay + Warp/Blend
- 你正在做 **飞行/驾驶模拟器**，需要超大视场角的多屏同步渲染 → 用 nDisplay
- 你在做 **虚拟制片**，需要将 Unreal 画面实时输出到 LED Volume → 用 nDisplay
- 你需要在 **多台 PC 间同步渲染**，确保各屏画面时间一致 → 用 nDisplay Cluster 同步机制
- 你需要对投影仪的 **畸变和边缘融合**进行精确校正 → 用 DisplayClusterWarp + MPCDI
- 你需要将 nDisplay 画面 **录制为 EXR 序列**用于后期合成 → 用 DisplayClusterMoviePipeline

## 模块架构

该插件由 29 个模块组成，按功能可分为以下几层：

### 核心层
| 模块 | 职责 |
|---|---|
| `DisplayCluster` | 主模块，集群通信、帧同步、渲染协调 |
| `DisplayClusterConfiguration` | 配置数据模型（.ndisplay 配置文件解析） |
| `DisplayClusterProjection` | 投影映射计算（视锥矩阵、立体投影） |
| `DisplayClusterWarp` | 网格变形（Warp）和边缘融合（Blend），MPCDI 支持 |
| `DisplayClusterShaders` | nDisplay 专用 Shader（后处理、WarpBlend、合成） |
| `DisplayClusterReplication` | 集群帧数据网络复制 |

### 媒体层
| 模块 | 职责 |
|---|---|
| `DisplayClusterMedia` | 媒体输入输出（DeckLink 等硬件采集卡集成） |
| `SharedMemoryMedia` | 共享内存媒体传输（低延迟 GPU 直传） |
| `DisplayClusterColorGrading` | 多屏幕色彩校正与 LUT 管理 |

### 编辑器层
| 模块 | 职责 |
|---|---|
| `DisplayClusterEditor` | 编辑器集成、PIE 支持、引擎设置覆盖 |
| `DisplayClusterConfigurator` | .ndisplay 配置文件的可视化编辑器 |
| `DisplayClusterOperator` | 运行时操作面板（集群状态监控、调试） |
| `DisplayClusterLightCardEditor` | 灯光卡片编辑器（虚拟灯光遮罩） |
| `DisplayClusterMonitor` / `Editor` | 集群健康监控 |
| `DisplayClusterDetails` | 细节面板扩展 |
| `DisplayClusterScenePreview` | 场景预览窗口 |

### 扩展层
| 模块 | 职责 |
|---|---|
| `DisplayClusterMoviePipeline` | Movie Render Queue 集成，支持多屏 EXR 输出 |
| `DisplayClusterMultiUser` | 多用户编辑协作支持 |
| `DisplayClusterStageMonitoring` | Unreal Insights 阶段性能监控 |
| `DisplayClusterRemoteControlInterceptor` | Remote Control API 拦截器 |
| `DisplayClusterMessageInterception` | 集群消息拦截 |
| `DisplayClusterFillDerivedDataCache` | DDC 预填充工具 |
| `DisplayClusterTests` | 自动化测试 |

## 蓝图用法

> 由于 nDisplay 源码规模极大（1351 文件），此处仅列出最高频使用的蓝图 API。完整 API 请查阅源码。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetClusterMgr` | 获取集群管理器实例 | `UDisplayClusterBlueprintAPI` |
| `GetGameViewportSize` | 获取当前视口尺寸 | `UDisplayClusterBlueprintAPI` |
| `GetRootActor` | 获取当前世界的 nDisplay 根 Actor | `UDisplayClusterBlueprintAPI` |

### nDisplay 根 Actor

nDisplay 使用 `ADisplayClusterRootActor` 作为场景中的配置载体：
1. 在场景中放置一个 `DisplayClusterRootActor`
2. 在 Details 面板中指定 `.ndisplay` 配置文件
3. 配置文件中定义了屏幕拓扑、投影方式、Warp/Blend 数据

### 配置文件

`.ndisplay` 文件是 nDisplay 的核心配置，定义：
- **Cluster 节点**：Master 和各个 Node 的 IP、端口
- **Viewports**：每台机器上渲染的屏幕区域
- **Projection**：投影类型（简单平面、MPCDI、mesh warp 等）
- **Warp/Blend**：变形网格和融合区数据

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterRootActor.h"
#include "DisplayClusterBlueprintAPI.h"
#include "DisplayClusterModule.h"
#include "IDisplayCluster.h"
```

### 基本用法：获取集群接口

```cpp
// 获取 nDisplay 模块接口
IDisplayCluster* DisplayCluster = FModuleManager::GetModulePtr<IDisplayCluster>("DisplayCluster");

if (DisplayCluster && DisplayCluster->IsModuleInitialized())
{
    // 获取集群管理器
    IDisplayClusterClusterManager* ClusterMgr = DisplayCluster->GetClusterMgr();
    
    // 判断当前是否为 Master 节点
    bool bIsMaster = ClusterMgr->IsMaster();
    
    // 获取当前节点 ID
    FString NodeId = ClusterMgr->GetNodeId();
}
```

### 进阶用法：监听集群事件

```cpp
// 在集群启动后执行自定义初始化
IDisplayCluster* DC = FModuleManager::GetModulePtr<IDisplayCluster>("DisplayCluster");
if (DC)
{
    DC->GetClusterMgr()->OnClusterEvent().AddLambda(
        [](const FDisplayClusterClusterEventJson& Event)
        {
            // 处理集群事件
            UE_LOG(LogTemp, Log, TEXT("Cluster event: %s = %s"), 
                *Event.Category, *Event.Type);
        }
    );
}
```

### 编辑器集成：PIE 模式

从 `UDisplayClusterEditorEngine` 可以看出，nDisplay 在编辑器中支持 Play-In-Editor：

```cpp
// DisplayClusterEditorEngine 会在 PIE 开始/结束时触发回调
// OnBeginPIE: 初始化 nDisplay 集群会话
// OnEndPIE: 清理集群资源

// 自定义 PIE 钩子（参考 DisplayClusterEditorEngine 的实现模式）
FEditorDelegates::BeginPIE.AddLambda([](bool bIsSimulating) 
{
    // nDisplay PIE 启动逻辑
});
```

### 基本用法：配置类访问

```cpp
#include "DisplayClusterEditorSettings.h"

// 读取 nDisplay 编辑器设置
const UDisplayClusterEditorSettings* Settings = GetDefault<UDisplayClusterEditorSettings>();
if (Settings && Settings->bEnabled)
{
    // nDisplay 已启用，集群复制可用
    bool bClusterReplication = Settings->bClusterReplicationEnabled;
}
```

## DisplayClusterEditor 模块详解

这是 nDisplay 的**编辑器集成模块**，负责将 nDisplay 无缝嵌入 Unreal Editor 工作流。

### 核心类

#### `UDisplayClusterEditorEngine`

继承自 `UUnrealEdEngine`，是 nDisplay 的**自定义编辑器引擎**。当 nDisplay 启用时替换默认引擎类，提供以下能力：

| 方法 | 说明 |
|---|---|
| `Init()` | 引擎初始化时注入 nDisplay 逻辑 |
| `PreExit()` | 引擎退出前清理集群资源 |
| `StartPlayInEditorSession()` | 拦截 PIE 启动，初始化 nDisplay 集群 |
| `LoadMap()` | 拦截地图加载，处理 nDisplay 场景配置 |
| `Tick()` | 每帧更新 nDisplay 状态 |
| `OnBeginPIE()` | PIE 开始回调，激活集群会话 |
| `OnEndPIE()` | PIE 结束回调，停用集群会话 |

关键状态标志：
- `bIsActivePIE`：当前是否在 PIE 模式
- `bIsNDisplayPIE`：当前 PIE 是否使用 nDisplay
- `SessionFrameCounter`：会话帧计数器

#### `UDisplayClusterEditorSettings`

存储在 `Engine.ini` 中的全局编辑器设置：

| 属性 | 类型 | 说明 |
|---|---|---|
| `bEnabled` | `bool` | 启用 nDisplay 引擎覆盖（需重启编辑器） |
| `bClusterReplicationEnabled` | `bool` | 启用集群复制 NetDriver 替换（需重启编辑器） |

### 模块生命周期

```
FDisplayClusterEditorModule::StartupModule()
  └─ RegisterSettings()    // 注册 UDisplayClusterEditorSettings 到编辑器设置面板

FDisplayClusterEditorModule::ShutdownModule()
  └─ UnregisterSettings()  // 注销设置面板
```

## Demo 示例

以下是一个最小化的 nDisplay 场景设置示例，演示如何通过 C++ 访问 nDisplay 集群：

```cpp
// MyNDisplayActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyNDisplayActor.generated.h"

UCLASS()
class AMyNDisplayActor : public AActor
{
    GENERATED_BODY()

public:
    AMyNDisplayActor();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    /** 获取当前集群节点信息并打印 */
    UFUNCTION(BlueprintCallable, Category = "nDisplay Demo")
    FString GetClusterInfo() const;

private:
    IDisplayCluster* DisplayClusterModule = nullptr;
};
```

```cpp
// MyNDisplayActor.cpp
#include "MyNDisplayActor.h"
#include "DisplayClusterModule.h"
#include "IDisplayCluster.h"
#include "Cluster/IDisplayClusterClusterManager.h"

AMyNDisplayActor::AMyNDisplayActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyNDisplayActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取 nDisplay 模块
    DisplayClusterModule = FModuleManager::GetModulePtr<IDisplayCluster>("DisplayCluster");
    
    if (DisplayClusterModule && DisplayClusterModule->IsModuleInitialized())
    {
        UE_LOG(LogTemp, Log, TEXT("nDisplay is initialized"));
        
        IDisplayClusterClusterManager* ClusterMgr = DisplayClusterModule->GetClusterMgr();
        if (ClusterMgr)
        {
            UE_LOG(LogTemp, Log, TEXT("Cluster Node: %s, IsMaster: %d"),
                *ClusterMgr->GetNodeId(), ClusterMgr->IsMaster());
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("nDisplay is not available in this session"));
    }
}

void AMyNDisplayActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    
    // 可在此处查询集群状态或发送集群事件
}

FString AMyNDisplayActor::GetClusterInfo() const
{
    if (!DisplayClusterModule || !DisplayClusterModule->IsModuleInitialized())
    {
        return TEXT("nDisplay not available");
    }

    IDisplayClusterClusterManager* ClusterMgr = DisplayClusterModule->GetClusterMgr();
    if (!ClusterMgr)
    {
        return TEXT("No cluster manager");
    }

    return FString::Printf(TEXT("Node: %s | Master: %s"),
        *ClusterMgr->GetNodeId(),
        ClusterMgr->IsMaster() ? TEXT("Yes") : TEXT("No"));
}
```

## 模块依赖

nDisplay 是一个重度依赖编辑器的插件，多个模块标记了 `UnrealEd` 依赖。以下列出其**独特依赖**：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | Direct3D 12 渲染硬件接口，用于 GPU 共享内存传输和低延迟媒体 |
| `UnrealEd` | 编辑器框架（广泛使用，PIE、设置面板、Details 面板等） |
| `EditorWidgets` | 编辑器 UI 组件 |
| `LevelEditor` | 关卡编辑器集成 |
| `ScalableMPCDI` (External) | 第三方 MPCDI 格式支持库，用于标准化投影校正数据交换 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support | MovieRenderGraph 新增 nDisplay 多层 EXR 输出支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 影片管线中合并 WarpBlendAlpha 模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 摄像机命名和 MPCDI/ICVFX Shader 透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复非默认 DisplayGamma 下输出帧编码的伽马值处理 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理小于视口尺寸时的画面闪烁 |

### 维护评价

- **维护状态**：🟢 **活跃维护中**
- **创建时间**：2018 年（UE4 4.20 时代），已有 8 年历史
- **更新频率**：非常活跃，近期（2026 年 5 月）有多次功能性更新
- **更新内容**：涵盖 MovieRenderGraph 集成、Shader 修复、色彩管理改进等
- **Epic 支持**：由 Epic Games 官方维护，是 Unreal 的**旗舰企业级功能**之一
- **已知限制**：
  - 默认关闭，需手动启用
  - 需要多台 PC 和网络环境才能发挥完整功能
  - Windows/Linux 限定，不支持主机平台
  - 模块间大量编译器依赖，编译时间较长
- **推荐程度**：⭐⭐⭐⭐⭐ 如果你做虚拟制片或多屏渲染，这是**必用**的插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/RenderingAndGraphics/nDisplay/Overview/)