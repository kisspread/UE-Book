# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 集群显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、测试资源） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 中用于**大规模、高保真度虚拟制作**的核心渲染插件。它解决的核心问题是：如何将同一个虚拟场景的渲染输出**精确、同步地**分配到由多台 PC（节点）驱动的**复杂物理显示拓扑**上（如多面 LED 墙、穹顶、多投影仪系统），以实现沉浸式视觉体验。

当前文档聚焦的 `DisplayClusterMonitorEditor` 模块，是 nDisplay 插件中的一个**编辑器工具集**。它解决了一个具体的运维问题：在由多个渲染节点组成的复杂集群中，如何**远程、实时地监控、诊断和调试**每个节点及其视口的渲染状态、媒体流和性能。它为技术总监或系统集成工程师提供了一个统一的控制面板，无需物理访问每台机器，即可掌握整个渲染农场的健康状况和输出画面。

## 使用场景

- 你在搭建一个由多面 LED 墙组成的虚拟摄影棚 → 你需要使用 nDisplay 配置显示集群，并通过 `DisplayClusterMonitorEditor` 在控制室集中监控所有墙的实时画面和状态。
- 你的渲染集群包含数十个节点，偶尔会出现节点无响应或画面不同步 → 你需要使用集群监控器快速定位问题节点，并远程重启其观察会话。
- 你需要在编辑器中同时查看所有渲染节点的“后缓冲”、“UI层”、“特定视口”或“ICVFX相机”的实时输出，以便进行色彩校正或构图检查 → 使用 `DisplayClusterMonitorEditor` 的多视口网格视图功能。

## 蓝图用法

`DisplayClusterMonitorEditor` 模块主要提供 C++ 和 Slate UI 接口，其核心功能（如集群发现、会话管理）并未直接暴露为蓝图节点。控制和集成主要通过 C++ API 完成。

### 核心节点

（此模块功能主要通过 C++ API 和编辑器 UI 提供，无标准蓝图节点）

## C++ 用法

### 头文件引入

```cpp
#include "IClusterMonitorController.h"
#include "IClusterObservable.h"
```

### 基本用法

获取集群监控控制器并启动通信。
```cpp
// 假设在某个自定义管理器类中
#include "IClusterMonitorController.h"

class FMyClusterMonitor
{
public:
    void Initialize()
    {
        // 获取或创建监控控制器实例（具体获取方式取决于模块实现，此处为示意）
        ClusterMonitorController = IClusterMonitorController::Get(); 
        
        if (ClusterMonitorController.IsValid())
        {
            // 启动与集群节点的消息总线通信，开始发现可观测对象（视口、后缓冲等）
            ClusterMonitorController->StartCommunication();
            
            // 绑定事件委托
            ClusterMonitorController->OnObservableJoined().AddRaw(this, &FMyClusterMonitor::HandleObservableJoined);
            ClusterMonitorController->OnObservableTimeout().AddRaw(this, &FMyClusterMonitor::HandleObservableTimeout);
        }
    }
    
    void Cleanup()
    {
        if (ClusterMonitorController.IsValid())
        {
            ClusterMonitorController->StopCommunication();
        }
    }

private:
    void HandleObservableJoined(const TSharedRef<IClusterObservable>& Observable)
    {
        UE_LOG(LogTemp, Log, TEXT("新可观测对象已加入: %s, 类型: %s"), 
            *Observable->GetName(), 
            *UEnum::GetValueAsString(Observable->GetType()));
    }
    
    void HandleObservableTimeout(const TSharedRef<IClusterObservable>& Observable)
    {
        UE_LOG(LogWarning, Log, TEXT("可观测对象超时无响应: %s"), *Observable->GetName());
    }

    TSharedPtr<IClusterMonitorController> ClusterMonitorController;
};
```

### 进阶用法

启动对特定可观测对象的观察会话，并控制其媒体播放。
```cpp
void StartMonitoringViewport(const FGuid& ViewportObservableId)
{
    if (!ClusterMonitorController.IsValid())
    {
        return;
    }

    // 1. 请求启动对该视口的观察会话（这将创建媒体连接）
    ClusterMonitorController->RequestSessionStart(ViewportObservableId);
    
    // 2. 稍后，获取该可观测对象以检查会话状态或控制播放
    TSharedPtr<IClusterObservable> Observable = ClusterMonitorController->GetObservable(ViewportObservableId);
    if (Observable.IsValid())
    {
        // 等待会话激活后，可以进行控制
        Observable->OnSessionStateChanged().AddLambda([](IClusterObservable::ESessionState NewState) {
            if (NewState == IClusterObservable::ESessionState::Active)
            {
                UE_LOG(LogTemp, Log, TEXT("观察会话已激活，可以开始播放。"));
            }
        });
        
        // 假设会话已激活，播放媒体流
        Observable->Play();
    }
}

void StopAllMonitoring()
{
    if (ClusterMonitorController.IsValid())
    {
        // 停止所有活动的观察会话
        ClusterMonitorController->RequestAllSessionsStop();
    }
}
```

## Demo 示例

这是一个演示如何在自定义编辑器工具中集成集群监控功能的最小示例。

**MyClusterMonitorTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "IClusterMonitorController.h"

class FMyClusterMonitorTool
{
public:
    void Initialize();
    void Shutdown();
    
    /** 打印当前集群状态摘要 */
    void PrintClusterStatus();

private:
    void OnObservableJoined(const TSharedRef<IClusterObservable>& Observable);
    void OnSessionStarted(const TSharedRef<IClusterObservable>& Observable);

    TSharedPtr<IClusterMonitorController> MonitorController;
};
```

**MyClusterMonitorTool.cpp**
```cpp
#include "MyClusterMonitorTool.h"
#include "IClusterObservable.h"

void FMyClusterMonitorTool::Initialize()
{
    // 获取监控控制器（实际获取逻辑可能涉及模块查找或工厂方法）
    // MonitorController = ... 
    
    if (MonitorController)
    {
        MonitorController->StartCommunication();
        MonitorController->OnObservableJoined().AddRaw(this, &FMyClusterMonitorTool::OnObservableJoined);
        MonitorController->OnSessionStarted().AddRaw(this, &FMyClusterMonitorTool::OnSessionStarted);
        
        UE_LOG(LogTemp, Log, TEXT("集群监控工具已初始化并开始通信。"));
    }
}

void FMyClusterMonitorTool::Shutdown()
{
    if (MonitorController)
    {
        MonitorController->StopCommunication();
        MonitorController.Reset();
    }
}

void FMyClusterMonitorTool::PrintClusterStatus()
{
    if (!MonitorController) return;

    UE_LOG(LogTemp, Log, TEXT("=== 集群监控状态 ==="));
    UE_LOG(LogTemp, Log, TEXT("已发现可观测对象数量: %d"), MonitorController->GetObservablesNum());
    UE_LOG(LogTemp, Log, TEXT("活动观察会话数量: %d"), MonitorController->GetActiveSessionsNum());
    UE_LOG(LogTemp, Log, TEXT("无响应节点数量: %d"), MonitorController->GetUnresponsiveNodesNum());
}

void FMyClusterMonitorTool::OnObservableJoined(const TSharedRef<IClusterObservable>& Observable)
{
    UE_LOG(LogTemp, Log, TEXT("监控到新可观测对象: '%s' (ID: %s)"), 
        *Observable->GetName(), 
        *Observable->GetId().ToString());
}

void FMyClusterMonitorTool::OnSessionStarted(const TSharedRef<IClusterObservable>& Observable)
{
    UE_LOG(LogTemp, Log, TEXT("可观测对象 '%s' 的观察会话已启动。"), *Observable->GetName());
    
    // 可以在此处开始记录性能数据或触发自动化测试
}
```

## 模块依赖

从 Build.cs 的依赖分析，`DisplayClusterMonitorEditor` 模块的特殊依赖如下：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 提供编辑器框架、菜单、标签页注册等基础功能 |

其他依赖均为标准模块（如 Core, CoreUObject, Engine, Slate 等），无需特别说明。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 在 MovieGraph 和 nDisplay 中增加了对 EXR 多图层输出的支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 重构了电影渲染管线中的混合模式，将 WarpBlendAlpha 合并入 WarpBlend。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了 MRG 中拓扑感知相机命名问题以及 MPCDI/ICVFX 着色器中的不透明 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了在输出帧编码回退路径中未正确应用非默认 DisplayGamma 的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时出现的闪烁问题。 |

### 维护评价

nDisplay 是 UE5 中用于**虚拟制作**的核心生产级插件，自 2018 年创建以来持续获得 Epic Games 的官方维护和功能更新。

- **活跃维护**：尽管插件本身已有 8 年历史，但从近期提交记录（最近更新在 2026 年 5 月）可以看出，它仍在被**非常活跃地开发**。近期的更新集中在渲染管线优化、着色器修复和与 MovieGraph 的深度集成上。
- **功能完整**：插件包含 28 个子模块，覆盖了从配置、渲染、投影、媒体处理到编辑器工具和监控的完整工作流。
- **推荐使用**：对于任何涉及 **LED 虚拟摄影棚、多投影仪系统或复杂多屏渲染** 的项目，nDisplay 是**官方且推荐**的解决方案。`DisplayClusterMonitorEditor` 模块是管理大型 nDisplay 集群不可或缺的运维工具。
- **已知限制**：插件**默认未启用**（`EnabledByDefault: false`），需要在项目设置中手动启用。其架构复杂，学习曲线较陡峭，更适合有经验的团队。

**结论**：这是一个**生产就绪、积极维护**的专业级插件，尽管创建时间较早，但仍在持续演进，无任何废弃迹象。强烈推荐在相关场景中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/VirtualProduction/nDisplay/Overview/)（UE5 文档站内的 nDisplay 专页）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)