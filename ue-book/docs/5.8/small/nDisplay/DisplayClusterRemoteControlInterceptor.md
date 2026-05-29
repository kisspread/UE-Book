# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 多PC集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（可能包含测试资产和配置示例） |
| 模块 | `DisplayCluster` (Runtime) 等，共29个模块 |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个专业级的渲染解决方案，用于将 Unreal Engine 的渲染输出分布到多台计算机（集群）驱动的多个物理显示设备上，并保持它们之间的精确同步。它主要解决以下问题：

1.  **超宽视野渲染**：为穹顶影院、LED 摄影墙、CAVE 系统等提供超过单台 PC 性能极限的超高分辨率或超广角视野。
2.  **精确同步**：确保集群中所有节点的渲染状态（摄像机、动画、物理）完全同步，画面无撕裂或延迟。
3.  **灵活的视口与投影**：支持为每个显示设备定义独立的视口（Viewport），并应用复杂的投影校正（如变形、融合、MPCDI），以适配各种曲面或异形屏幕。
4.  **远程控制与生产管理**：提供编辑器工具和运行时接口，用于配置、监控和控制整个渲染集群。

简而言之，当单台 PC 无法满足显示需求时，nDisplay 负责将任务拆分、分发、同步并最终合成出完整的视觉画面。

## 使用场景

- **虚拟制片（Virtual Production）**：构建 LED 摄影墙（Volume），用于实时背景渲染，需要多台渲染节点驱动高分辨率的 LED 面板。
- **穹幕/CAVE 仿真训练**：用于飞行模拟器、驾驶模拟器等需要 360° 或超广角沉浸式环境的场合。
- **大型艺术装置/主题公园**：驱动复杂的多投影仪或无缝拼接的大型显示墙。
- **高分辨率科研可视化**：用于天文、流体动力学等需要超高分辨率呈现的科学数据可视化。

## 蓝图用法

nDisplay 的蓝图 API 主要围绕**运行时配置的加载、节点状态查询和集群事件发送**。其核心蓝图类位于 `UDisplayClusterConfiguration` 和相关的子系统中。需要注意的是，许多核心的同步和渲染逻辑在 C++ 底层处理，蓝图更多用于初始化和事件交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Active Cluster Node Id` | 获取当前运行此代码的 nDisplay 集群节点的唯一标识符（ID）。 | `UDisplayClusterSubsystem` |
| `Is Primary Node` | 判断当前节点是否为主节点（Primary），主节点通常负责逻辑和控制。 | `UDisplayClusterSubsystem` |
| `Send Cluster Event` | 向集群中的其他节点广播一个自定义事件，用于跨节点同步逻辑触发。 | `UDisplayClusterSubsystem` |
| `Get Cluster Event` | （在事件调度器中）监听来自集群中其他节点的自定义事件。 | `UDisplayClusterSubsystem` |
| `Set Cluster Event` | 设置一个可由蓝图触发的集群事件，供其他节点监听。 | `UDisplayClusterSubsystem` |

### 使用示例（蓝图描述）

1.  **在 BeginPlay 中初始化 nDisplay 子系统**：
    -   使用 `Get Display Cluster Subsystem` 节点获取子系统引用。
    -   调用 `Is Primary Node` 判断角色。主节点（Director）可负责游戏逻辑，其他节点（Render）主要进行渲染。
2.  **发送同步事件**：
    -   在主节点上，当游戏状态改变（如玩家进入新区域），调用 `Send Cluster Event` 发送一个携带“区域ID”的事件。
    -   所有节点（包括主节点自身）通过 `On Cluster Event` 事件监听该事件，并根据“区域ID”更新自己的环境资源（如加载不同光照或模型），保证集群状态一致。
3.  **查询节点信息**：
    -   使用 `Get Active Cluster Node Id` 获取本节点 ID，用于加载针对该特定显示设备的配置文件（如投影矩阵）。

## C++ 用法

nDisplay 的 C++ API 非常丰富，主要分为**配置加载、视图管理、投影控制、集群通信**等模块。以下示例展示了其核心的集群事件拦截和处理机制，这是 `DisplayClusterRemoteControlInterceptor` 模块的主要功能。

### 头文件引入

```cpp
// 核心集群管理
#include "DisplayClusterRootActor.h"
#include "DisplayClusterSubsystem.h"
// 集群通信与事件
#include "IDisplayClusterClusterManager.h"
#include "DisplayClusterClusterEvent.h"
// 远程控制拦截（针对本模块）
#include "DisplayClusterRemoteControlInterceptor.h"
```

### 基本用法：监听集群事件

这是一个最简单的监听集群二进制事件的示例，展示如何在运行时接收来自其他节点的命令或数据。
*（来源: 私有头文件 `DisplayClusterRemoteControlInterceptor.h` 中的 `OnClusterEventBinaryHandler` 逻辑推断）*

```cpp
// 假设您已在一个 Actor 或 Subsystem 的类中
void AMyClass::SetupClusterEventListener()
{
    // 获取集群管理器
    IDisplayClusterClusterManager* ClusterManager = IDisplayCluster::Get().GetClusterMgr();
    if (ClusterManager)
    {
        // 创建一个二进制事件监听器，并绑定到我们的处理函数
        FOnClusterEventBinaryListener Listener;
        Listener.BindUObject(this, &AMyClass::HandleClusterBinaryEvent);
        
        // 注册监听器
        ClusterManager->AddClusterEventBinaryListener(Listener);
    }
}

// 事件处理函数
void AMyClass::HandleClusterBinaryEvent(const FDisplayClusterClusterEventBinary& Event)
{
    // 根据事件类别或类型进行解析和处理
    UE_LOG(LogTemp, Log, TEXT("Received binary event. Category: %s, Type: %s, Data size: %d"),
        *Event.Category.ToString(), *Event.Type.ToString(), Event.EventData.Num());
    
    // 示例：如果这是一个“重置对象属性”的指令
    if (Event.Type == FName("ResetObjectProperties"))
    {
        // 反序列化 Event.EventData 中的缓冲区，获取对象路径并执行重置
        // OnReplication_ResetObjectProperties(Event.EventData);
    }
}
```

### 进阶用法：实现自定义的远程控制拦截器

`DisplayClusterRemoteControlInterceptor` 模块展示了如何实现一个完整的拦截器，用于捕获和处理来自外部远程控制系统的指令，并在 nDisplay 集群中进行复制和执行。
*（综合 `DisplayClusterRemoteControlInterceptor.h` 和 `DisplayClusterRemoteControlInterceptorModule.h` 分析）*

```cpp
// 1. 定义拦截器类，实现 IRemoteControlInterceptionFeatureInterceptor 接口
class FMyCustomRemoteControlInterceptor : public IRemoteControlInterceptionFeatureInterceptor
{
public:
    // 实现接口要求的方法，处理来自 Remote Control 的指令
    virtual ERCIResponse SetObjectProperties(FRCIPropertiesMetadata& InProperties) override
    {
        // 自定义逻辑：检查是否有权限，或者根据集群状态决定是否允许
        if (ShouldApplyChange())
        {
            // 序列化指令，通过集群二进制事件广播给其他节点
            // QueueInterceptEvent(...);
            return ERCIResponse::Success;
        }
        return ERCIResponse::Rejected;
    }
    // ... 实现其他接口方法 (ResetObjectProperties, InvokeCall, SetPresetController)

private:
    bool ShouldApplyChange()
    {
        // 例如：只在主节点上执行决策，然后复制
        return IDisplayCluster::Get().GetClusterMgr()->IsPrimary();
    }
};

// 2. 在模块启动时注册拦截器
void FDisplayClusterRemoteControlInterceptorModule::StartupModule()
{
    // 检查 CVar 配置，决定是否启用拦截
    if (CVarInterceptOnPrimaryOnly.GetValueOnGameThread())
    {
        // 创建拦截器实例
        Interceptor = MakeUnique<FMyCustomRemoteControlInterceptor>();
        // 向远程控制系统注册此拦截器
        FRemoteControlInterception::Get().RegisterInterceptor(Interceptor.Get());
    }
}
```

## Demo 示例

以下示例演示了如何创建一个简单的 Actor，用于在 nDisplay 集群的主节点上接收用户输入，并广播一个自定义事件让所有节点切换显示内容。

### MyNDisplaySyncActor.h
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyNDisplaySyncActor.generated.h"

class UDisplayClusterSubsystem;

UCLASS()
class AMyNDisplaySyncActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    // 处理输入并发送集群事件
    UFUNCTION(BlueprintCallable)
    void SwitchContent(bool bShowContentA);

    // 处理接收到的集群切换事件
    void HandleContentSwitchEvent(const FDisplayClusterClusterEventString& Event);

private:
    UPROPERTY()
    FOnClusterEventListenerString SwitchEventListener;

    UPROPERTY()
    UDisplayClusterSubsystem* ClusterSubsystem = nullptr;

    // 当前显示的内容状态
    bool bIsContentAVisible = true;
};
```

### MyNDisplaySyncActor.cpp
```cpp
#include "MyNDisplaySyncActor.h"
#include "DisplayClusterSubsystem.h"
#include "IDisplayClusterClusterManager.h"
#include "Kismet/GameplayStatics.h"

void AMyNDisplaySyncActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取子系统
    ClusterSubsystem = UDisplayClusterSubsystem::Get(this);
    if (ClusterSubsystem)
    {
        // 注册集群字符串事件监听器
        SwitchEventListener.BindUObject(this, &AMyNDisplaySyncActor::HandleContentSwitchEvent);
        IDisplayCluster::Get().GetClusterMgr()->AddClusterEventListenerString(SwitchEventListener);
    }
}

void AMyNDisplaySyncActor::SwitchContent(bool bShowContentA)
{
    // 确保只在主节点上执行逻辑
    if (ClusterSubsystem && ClusterSubsystem->IsPrimaryNode())
    {
        // 更新本地状态
        bIsContentAVisible = bShowContentA;
        // 构造要广播的事件数据
        FDisplayClusterClusterEventString Event;
        Event.Category = TEXT("ContentSwitch");
        Event.Type = bShowContentA ? TEXT("ShowA") : TEXT("ShowB");
        Event.Name = TEXT("MainDisplay");
        // 通过集群管理器发送事件
        IDisplayCluster::Get().GetClusterMgr()->DispatchClusterEventString(Event, true);
    }
}

void AMyNDisplaySyncActor::HandleContentSwitchEvent(const FDisplayClusterClusterEventString& Event)
{
    if (Event.Type == TEXT("ShowA"))
    {
        bIsContentAVisible = true;
        // 在此节点执行显示内容 A 的逻辑，例如加载资源、设置材质参数等
        UE_LOG(LogTemp, Log, TEXT("Node %s: Switching to Content A"), *ClusterSubsystem->GetActiveClusterNodeId());
    }
    else if (Event.Type == TEXT("ShowB"))
    {
        bIsContentAVisible = false;
        // 执行显示内容 B 的逻辑
        UE_LOG(LogTemp, Log, TEXT("Node %s: Switching to Content B"), *ClusterSubsystem->GetActiveClusterNodeId());
    }
}
```

## 模块依赖

nDisplay 插件的模块众多，且存在大量内部依赖。从使用者的角度看，如果只是希望在自己的项目模块中**使用 nDisplay 的功能**（如查询节点状态、发送事件），通常只需要依赖其核心运行时模块。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 的核心运行时模块，提供集群管理、视口控制、渲染同步等基础功能。 |

（注意：许多 `DisplayCluster*Editor` 模块属于编辑器工具链，在打包后不会包含。`DisplayClusterRemoteControlInterceptor` 等模块是功能插件，根据需要选择依赖。）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 nDisplay 的 Movie Graph（MRG）添加了 EXR 多层支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 将 nDisplay 电影管线中的“WarpBlendAlpha”模式合并进“WarpBlend”模式。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了 MRG 中拓扑感知摄像机命名问题；修复了 MPCDI/ICVFX 着色器中的不透明 alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback |  nDisplay：在输出帧编码的回退路径中，现在能正确使用非默认的显示 Gamma 设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时的闪烁问题。 |

### 维护评价

- **活跃维护**：该插件由 Epic Games 官方维护，属于 Unreal Engine 的核心技术组件。从 git 日志看，最近更新非常频繁（多个提交在 2026 年 5 月），且修复内容涉及核心渲染管线、着色器和编辑器集成，表明其仍在**积极开发和维护中**。
- **功能完整**：nDisplay 已非常成熟，是虚拟制片和大型显示项目的标准解决方案。
- **建议**：尽管是成熟插件，但由于其复杂的分布式架构和对特定硬件的依赖，在使用前务必进行充分的原型测试。推荐用于有明确多屏/集群渲染需求的中大型项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/ndisplay-in-unreal-engine/)（Unreal Engine 官方 nDisplay 文档入口）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)