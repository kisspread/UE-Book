# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、着色器、配置模板） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterMedia` (Runtime), `SharedMemoryMedia` (Runtime), `DisplayClusterWarp` (Runtime) 等 29 个模块 |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 的**集群同步渲染**插件，用于在多台 PC 上驱动多个显示输出，实现高分辨率、多投影的沉浸式视觉体验。它解决的核心问题是：**如何让多台机器上的多个视口以精确同步的方式渲染同一场景**。

插件包含 29 个子模块，覆盖了从配置管理、投影变换、Warp/Blend 校正、媒体帧同步、到序列器离线渲染的完整链路。具体能力包括：

- **集群渲染同步**：通过以太网屏障（Ethernet Barrier）或 VBlank 同步策略，确保多台 PC 的渲染帧精确对齐
- **投影校正**：支持 MPCDI 格式的投影配置，实现多投影仪的几何校正与边缘融合
- **Warp & Blend**：支持自定义网格变形（Mesh Warp）和 Alpha 混合，适配各种投影面（平面、曲面、穹顶等）
- **媒体输入/输出**：通过共享内存（Shared Memory）在多进程/多机之间高效传输帧数据
- **虚拟制片支持**：LED Volume（LED 虚拟墙）的 ICVFX（In-Camera VFX）渲染，包含 Light Card 编辑器
- **离线渲染**：与 MoviePipeline 集成，支持多视口 EXR 多图层输出
- **远程控制**：通过 Remote Control API 对集群进行运行时参数调控
- **Multi-User 编辑**：在多用户编辑环境中保持 nDisplay 状态同步

## 使用场景

- 你正在搭建 **LED 虚拟墙**（Virtual Production）用于影视拍摄 → 用 nDisplay 配置 LED 面板的投影映射与同步
- 你需要驾驶/飞行**模拟器**的多屏幕环绕视图 → 用 nDisplay 配置多视口投影与几何校正
- 你在构建**CAVE 沉浸式环境**（多面投影房间）→ 用 nDisplay 管理多 PC 集群渲染
- 你需要在多台机器上**精确同步**渲染同一场景用于测试或演示 → 用 nDisplay 的同步策略
- 你想用 MoviePipeline **离线渲染**多视角 EXR 序列帧 → 用 nDisplay 的 MoviePipeline 集成
- 你需要**投影仪边缘融合**和几何畸变校正 → 用 nDisplay 的 MPCDI/WarpBlend 功能

## 蓝图用法

nDisplay 核心运行时模块提供了丰富的蓝图 API，以下是按功能分组的主要节点：

### 集群节点管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Nodes` | 获取集群中所有节点配置信息 | `UDisplayClusterBlueprintAPI` |
| `Get Node ID` | 获取当前节点的 ID | `UDisplayClusterBlueprintAPI` |
| `Get Node Role` | 获取当前节点角色（Primary/Secondary/Backup） | `UDisplayClusterBlueprintAPI` |
| `Is Primary` | 判断当前是否为主节点 | `UDisplayClusterBlueprintAPI` |

### 视口控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Viewports` | 获取所有视口列表 | `UDisplayClusterBlueprintAPI` |
| `Get Viewport By ID` | 按 ID 获取特定视口 | `UDisplayClusterBlueprintAPI` |
| `Set Viewport Render Mode` | 设置视口渲染模式 | `UDisplayClusterBlueprintAPI` |

### 同步控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Sync Barrier Wait` | 在同步屏障处等待所有节点到达 | `UDisplayClusterBlueprintAPI` |
| `Get Sync Policy` | 获取当前使用的同步策略 | `UDisplayClusterBlueprintAPI` |

### 运行时配置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Cluster Config` | 获取当前集群配置对象 | `UDisplayClusterConfiguration` |
| `Get Scene Root Component` | 获取 nDisplay 场景根组件 | `UDisplayClusterRootActor` |

### 使用示例（蓝图描述）

1. **判断主节点执行逻辑**：使用 `Get Node Role` → Branch → 主节点执行特殊逻辑（如 UI 输出、控制台命令）
2. **运行时切换视口**：使用 `Get Viewport By ID` → 调用视口参数修改 → 触发重新配置
3. **ICVFX Light Card 操控**：在蓝图中引用 `ADisplayClusterLightCardActor`，修改其 Transform 来控制虚拟光源位置

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterRootActor.h"
#include "DisplayClusterConfigurationTypes.h"
#include "DisplayClusterBlueprintAPI.h"
#include "IDisplayClusterShaders.h"
```

### 基本用法 - 获取集群配置

```cpp
// 获取 nDisplay 根 Actor 并读取集群配置
ADisplayClusterRootActor* RootActor = /* 从场景获取 */;
if (RootActor)
{
    UDisplayClusterConfigurationData* ConfigData = RootActor->GetConfigData();
    if (ConfigData)
    {
        // 遍历所有节点配置
        for (const auto& NodePair : ConfigData->Cluster->Nodes)
        {
            const FDisplayClusterConfigurationClusterNode& Node = NodePair.Value;
            UE_LOG(LogTemp, Log, TEXT("Node: %s, WindowCount: %d"),
                *NodePair.Key, Node.Windows.Num());
        }
    }
}
```

### 基本用法 - 共享内存媒体

```cpp
// 创建共享内存媒体输出（用于进程间帧数据传输）
USharedMemoryMediaOutput* MediaOutput = NewObject<USharedMemoryMediaOutput>();
MediaOutput->SetUniqueName(TEXT("MySharedMemOutput"));
// 配置分辨率等参数后调用 CreateMediaCapture 创建采集器
```

### 进阶用法 - 自定义同步策略

```cpp
// 实现自定义同步策略需要继承 UDisplayClusterMediaSynchronizationPolicy
// 然后通过工厂注册到编辑器，如 DisplayClusterMediaEditor 模块中的:
// - UDisplayClusterMediaSynchronizationPolicyEthernetBarrierFactory
// - UDisplayClusterMediaSynchronizationPolicyVblankFactory
```

## Demo 示例

以下是一个最小化的 nDisplay 集群节点角色检测示例：

### DisplayClusterDemoActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DisplayClusterDemoActor.generated.h"

UCLASS()
class ADisplayClusterDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ADisplayClusterDemoActor();

    virtual void BeginPlay() override;

    // 蓝图可调用：获取当前节点 ID
    UFUNCTION(BlueprintCallable, Category = "nDisplay Demo")
    FString GetCurrentNodeId() const;

    // 蓝图可调用：判断是否为主节点
    UFUNCTION(BlueprintPure, Category = "nDisplay Demo")
    bool IsPrimaryNode() const;

protected:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "nDisplay Demo")
    bool bShowDebugInfo = true;
};
```

### DisplayClusterDemoActor.cpp

```cpp
#include "DisplayClusterDemoActor.h"
#include "DisplayClusterRootActor.h"
#include "DisplayClusterConfigurationTypes.h"
#include "DisplayClusterBlueprintAPI.h"
#include "IDisplayCluster.h"

ADisplayClusterDemoActor::ADisplayClusterDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ADisplayClusterDemoActor::BeginPlay()
{
    Super::BeginPlay();

    if (bShowDebugInfo)
    {
        UE_LOG(LogTemp, Log, TEXT("nDisplay Demo - Current Node: %s, IsPrimary: %s"),
            *GetCurrentNodeId(),
            IsPrimaryNode() ? TEXT("YES") : TEXT("NO"));
    }
}

FString ADisplayClusterDemoActor::GetCurrentNodeId() const
{
    IDisplayCluster* DisplayCluster = IDisplayCluster::Get();
    if (DisplayCluster)
    {
        return DisplayCluster->GetNodeId();
    }
    return TEXT("Unknown");
}

bool ADisplayClusterDemoActor::IsPrimaryNode() const
{
    IDisplayCluster* DisplayCluster = IDisplayCluster::Get();
    if (DisplayCluster)
    {
        return DisplayCluster->GetClusterRole() == EDisplayClusterNodeRole::Primary;
    }
    return false;
}
```

## DisplayClusterMediaEditor 模块说明

当前分析的 `DisplayClusterMediaEditor` 模块是 nDisplay 的**编辑器资产工厂**模块，为以下资产类型提供编辑器集成（新建菜单、资产定义）：

| 工厂类 | 创建的资产类型 |
|---|---|
| `USharedMemoryMediaOutputFactory` | `USharedMemoryMediaOutput` — 共享内存媒体输出 |
| `USharedMemoryMediaSourceFactory` | `USharedMemoryMediaSource` — 共享内存媒体输入源 |
| `UDisplayClusterMediaOutputSynchronizationPolicyEthernetBarrierFactory` | 以太网屏障同步策略 |
| `UDisplayClusterMediaOutputSynchronizationPolicyVblankFactory` | VBlank 垂直同步策略 |

以及资产定义 `UAssetDefinition_SharedMemoryMediaOutput`，将共享内存输出归类到 "Media Sources + Outputs" 资产分类中。

## 模块依赖

nDisplay 的独特依赖如下（已省略常见 Core/Engine/Slate 依赖）：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | Direct3D 12 渲染硬件接口，用于共享内存媒体的 GPU 帧传输 |
| `ScalableMPCDI` (External) | 第三方 MPCDI 投影校正格式库，用于投影映射配置解析 |
| `MediaUtils` | UE 媒体框架工具，用于媒体输出/输入基础架构 |
| `DisplayClusterShaders` | nDisplay 专用着色器（WarpBlend、ICVFX 等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 添加 EXR 多图层输出支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并 WarpBlendAlpha 模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 摄像机命名和 MPCDI/ICVFX 着色器不透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复非默认 DisplayGamma 在帧编码回退时的处理 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口时的闪烁问题 |

### 维护评价

**活跃维护** ✅

nDisplay 是 Epic Games 的**战略级功能模块**，服务于 Virtual Production（虚拟制片）和大型沉浸式体验市场。从 git 历史看：

- **持续活跃**：近期（2026 年 5 月）仍有密集的功能更新和 Bug 修复
- **不断演进**：与 MovieGraph（新版 MoviePipeline）、ICVFX 着色器等新系统持续集成
- **成熟稳定**：自 2018 年创建以来已迭代 8 年，架构成熟
- **企业级定位**：`EnabledByDefault=false` 表明面向专业用户，非默认启用
- **规模庞大**：1351 个源文件、29 个子模块，覆盖渲染、投影、同步、媒体、编辑器的完整栈

**推荐使用**：如果你的项目涉及多显示输出、LED 虚拟墙、模拟器或多投影校正，nDisplay 是唯一且必需的官方方案。由于其复杂性，建议先阅读官方文档和示例项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/DisplayCluster/)（虚幻引擎官方 nDisplay 文档）