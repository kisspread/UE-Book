# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、材质模板） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterWarp` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 中用于驱动复杂多显示器、多投影仪和 LED 墙渲染的核心系统。它远不止是简单的“多PC同步渲染”，而是一个完整的虚拟制片（Virtual Production）和沉浸式体验解决方案。

**核心解决的问题：**
1.  **同步集群渲染**：协调多台计算机（节点）同步渲染同一场景的不同部分，确保画面无缝拼接。
2.  **投影与几何校正**：处理非平面屏幕（如曲面、穹顶、LED墙）的投影变形、边缘融合和几何校正（Warping & Blending）。
3.  **ICVFX（摄像机内视觉特效）**：为 LED 墙虚拟制片提供完整支持，包括实时预览、色彩管理、媒体输入/输出以及与摄像机运动的同步。
4.  **色彩管理**：提供精细的色彩分级（Color Grading）工具，确保整个显示墙的色彩一致性。
5.  **媒体集成**：支持从外部设备（如摄像机）捕获视频流，并将其作为纹理实时显示在场景中。

**为什么存在：** 传统的单机渲染无法满足大型沉浸式体验（如主题公园游乐设施、驾驶模拟器）和虚拟制片（如《曼达洛人》使用的 LED 墙）对超高分辨率、低延迟和精确几何校正的需求。nDisplay 通过分布式渲染和专业的投影校正技术解决了这些挑战。

## 使用场景

-   **虚拟制片 (ICVFX)**：你在使用 LED 墙进行拍摄，需要将 Unreal 场景实时渲染到巨大的 LED 屏幕上，并与物理摄像机完美同步，实现“所见即所得”的拍摄效果。
-   **大型沉浸式体验**：你在开发一个穹顶影院、多面 CAVE 系统或主题公园黑暗骑乘项目，需要将画面精确投射到复杂的几何表面上。
-   **驾驶/飞行模拟器**：你需要为模拟器构建一个环绕式的多通道视景系统，要求极低的延迟和帧同步。
-   **大型活动与展览**：你需要用多台投影仪拼接出一个超宽或异形的画面，并进行边缘融合和几何校正。

## 蓝图用法

nDisplay 提供了丰富的蓝图接口，主要用于控制运行时行为和监听集群事件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Root Actor` | 获取当前世界中的 nDisplay 根 Actor | `IDisplayClusterGameManager` |
| `On Cluster Event Json` | 接收来自集群的 JSON 格式事件（蓝图可实现事件） | `IDisplayClusterClusterEventListener` |
| `On Cluster Event Binary` | 接收来自集群的二进制格式事件（蓝图可实现事件） | `IDisplayClusterClusterEventListener` |
| `Set Visualization Scale` | 设置 nDisplay 组件的可视化比例（编辑器内） | `IDisplayClusterComponent` |
| `Set Visualization Enabled` | 启用或禁用 nDisplay 组件的可视化（编辑器内） | `IDisplayClusterComponent` |

### 使用示例（蓝图描述）

1.  **监听集群事件**：
    -   创建一个蓝图 Actor，实现 `IDisplayClusterClusterEventListener` 接口。
    -   在事件图表中，右键添加 `On Cluster Event Json` 事件节点。
    -   连接该事件，在事件触发时解析 `Event` 结构体中的 `Category` 和 `Name` 等字段，执行相应逻辑（例如，根据主节点发送的指令切换场景）。

2.  **同步组件**：
    -   将 `UDisplayClusterSceneComponentSyncThis` 组件添加到需要跨集群同步的 Actor 上。
    -   该组件会自动处理其所属 Actor 的 Transform 同步。

## C++ 用法

### 头文件引入

```cpp
#include "IDisplayClusterGameManager.h"
#include "IDisplayClusterClusterEventListener.h"
#include "Components/DisplayClusterSceneComponentSyncThis.h"
```

### 基本用法

**获取 nDisplay 根 Actor**
```cpp
// 来源：IDisplayClusterGameManager.h
if (IDisplayClusterGameManager* GameMgr = IDisplayCluster::Get().GetGameManager())
{
    ADisplayClusterRootActor* RootActor = GameMgr->GetRootActor();
    if (RootActor)
    {
        // 与根 Actor 交互
    }
}
```

**实现集群事件监听器**
```cpp
// 来源：IDisplayClusterClusterEventListener.h
UCLASS()
class AMyClusterListener : public AActor, public IDisplayClusterClusterEventListener
{
    GENERATED_BODY()

public:
    // 实现蓝图可实现事件
    UFUNCTION(BlueprintImplementableEvent, Category = "NDisplay")
    void OnClusterEventJson(const FDisplayClusterClusterEventJson& Event);

    UFUNCTION(BlueprintImplementableEvent, Category = "NDisplay")
    void OnClusterEventBinary(const FDisplayClusterClusterEventBinary& Event);
};
```

### 进阶用法

**自定义渲染设备工厂**
```cpp
// 来源：IDisplayClusterRenderDeviceFactory.h
class FMyRenderDeviceFactory : public IDisplayClusterRenderDeviceFactory
{
public:
    virtual TSharedPtr<IDisplayClusterRenderDevice, ESPMode::ThreadSafe> Create(const FString& InDeviceType) override
    {
        // 根据 InDeviceType 返回你的自定义渲染设备实例
        return MakeShared<FMyCustomRenderDevice>();
    }
};

// 在模块启动时注册
IDisplayClusterRenderDeviceFactory* MyFactory = new FMyRenderDeviceFactory();
IDisplayCluster::Get().RegisterRenderDeviceFactory(TEXT("MyDeviceType"), MyFactory);
```

## Demo 示例

一个最小的 nDisplay 集群事件监听器示例。

**MyClusterListener.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IDisplayClusterClusterEventListener.h"
#include "MyClusterListener.generated.h"

UCLASS()
class AMyClusterListener : public AActor, public IDisplayClusterClusterEventListener
{
    GENERATED_BODY()

public:
    AMyClusterListener();

protected:
    virtual void BeginPlay() override;

public:
    // IDisplayClusterClusterEventListener 接口实现
    UFUNCTION(BlueprintCallable, Category = "NDisplay")
    void OnClusterEventJson(const FDisplayClusterClusterEventJson& Event);

    UFUNCTION(BlueprintCallable, Category = "NDisplay")
    void OnClusterEventBinary(const FDisplayClusterClusterEventBinary& Event);
};
```

**MyClusterListener.cpp**
```cpp
#include "MyClusterListener.h"
#include "DisplayClusterClusterEvent.h"

AMyClusterListener::AMyClusterListener()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyClusterListener::BeginPlay()
{
    Super::BeginPlay();
    // 注意：监听器的注册通常由 nDisplay 系统自动处理，当 Actor 实现了接口时。
    // 你也可以手动注册，但通常不需要。
}

void AMyClusterListener::OnClusterEventJson(const FDisplayClusterClusterEventJson& Event)
{
    UE_LOG(LogTemp, Log, TEXT("Received JSON Cluster Event - Category: %s, Name: %s"), *Event.Category, *Event.Name);
    // 在此处处理 JSON 事件
}

void AMyClusterListener::OnClusterEventBinary(const FDisplayClusterClusterEventBinary& Event)
{
    UE_LOG(LogTemp, Log, TEXT("Received Binary Cluster Event"));
    // 在此处处理二进制事件
}
```

**Build.cs 依赖**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "DisplayCluster" // nDisplay 核心模块
});
```

## 模块依赖

要使用 nDisplay 的核心功能，你的模块通常需要依赖以下模块。已省略常见的 Core、Engine 等依赖。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心运行时逻辑，包含游戏管理器、组件、同步等。 |
| `DisplayClusterConfiguration` | 处理 nDisplay 配置资产（.ndisplay）的加载和解析。 |
| `DisplayClusterProjection` | 负责投影策略（如 MPCDI、简单平面投影）的实现。 |
| `DisplayClusterShaders` | 包含 nDisplay 使用的自定义着色器和渲染通道。 |
| `DisplayClusterWarp` | 实现几何校正（Warping）和边缘融合（Blending）功能。 |
| `DisplayClusterMedia` | 处理媒体输入/输出，如从摄像机捕获视频。 |
| `DisplayClusterMoviePipeline` | 为 Movie Render Queue 提供 nDisplay 支持。 |
| `DisplayClusterMultiUser` | 支持多用户编辑（Concert）下的 nDisplay 同步。 |
| `DisplayClusterOperator` | 提供操作员界面（Operator UI）功能。 |
| `DisplayClusterColorGrading` | 提供高级色彩分级工具。 |
| `DisplayClusterLightCardEditor` | 提供灯光卡（Light Card）编辑器功能。 |
| `DisplayClusterEditor` | nDisplay 编辑器工具和资产类型。 |
| `DisplayClusterConfigurator` | nDisplay 配置器编辑器工具。 |
| `DisplayClusterDetails` | nDisplay 细节面板自定义。 |
| `DisplayClusterMediaEditor` | 媒体相关的编辑器工具。 |
| `DisplayClusterMoviePipelineEditor` | Movie Render Queue 相关的编辑器工具。 |
| `DisplayClusterRemoteControlInterceptor` | 与 Remote Control 插件集成。 |
| `DisplayClusterReplication` | 处理 nDisplay 属性的网络复制。 |
| `DisplayClusterScenePreview` | 提供场景预览功能。 |
| `DisplayClusterStageMonitoring` | 舞台监控工具。 |
| `DisplayClusterTests` | nDisplay 自动化测试。 |
| `SharedMemoryMedia` | 基于共享内存的高性能媒体传输。 |
| `SharedMemoryMediaEditor` | 共享内存媒体的编辑器工具。 |
| `ScalableMPCDI` | 第三方 MPCDI 库集成。 |

## 维护状态

### 近期更新

1.  **`6c4d23dbb718` (2024-07-19)**: [nDisplay] Fixed transition states management for nDisplay media
    -   **解读**：修复了 nDisplay 媒体（如摄像机输入）在状态转换时的管理问题，提升了稳定性。
2.  **`d104d2cf1888` (2024-07-19)**: [nDisplay] Removed the unnecessary workaround for ICVFX camera media sub-objects
    -   **解读**：清理了 ICVFX 摄像机媒体子对象的旧代码，修复了在 Take Recorder 复制 NDC 实例时可能导致的崩溃。
3.  **`63e6dc525c5f` (2024-07-19)**: [nDisplay] Fixed crash while closing nD node after "exit" console command
    -   **解读**：修复了一个特定场景下的崩溃问题（使用 `exit` 控制台命令关闭 nDisplay 节点时）。

### 维护评价

-   **创建时间**：2018 年，是 UE 中相对成熟的系统。
-   **最近更新频率**：最近的提交集中在 2024 年 7 月，均为 Bug 修复和稳定性改进，没有新功能添加。这表明该插件已进入**稳定维护期**。
-   **活跃维护**：是。作为 Epic Games 虚拟制片战略的核心组件，nDisplay 仍在被积极维护和修复，以确保其在生产环境中的可靠性。
-   **已知问题或限制**：由于其复杂性，配置和调试 nDisplay 系统需要专业知识。对硬件（如支持 Genlock 的 GPU）和网络有特定要求。
-   **推荐使用**：**强烈推荐**用于任何涉及多显示器、投影校正或虚拟制片（ICVFX）的专业项目。对于简单的多窗口显示，可能过于复杂。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/nDisplay)
-   [官方文档](https://docs.unrealengine.com/5.7/en-US/nDisplay-in-unreal-engine/)