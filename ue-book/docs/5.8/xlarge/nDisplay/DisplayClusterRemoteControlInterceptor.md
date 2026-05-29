# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 多屏同步渲染系统 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源、第三方库） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterProjection` (Runtime), `SharedMemoryMedia` (Runtime), `ScalableMPCDI` (External) 等共29个模块 |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个完整的集群渲染解决方案，用于在多个物理显示设备上同步渲染单个虚幻引擎场景。它解决的核心问题是：**如何将一个 UE 场景分割成多个视口，并在多个联网的 PC 上进行精确同步渲染，以形成一个统一的、无缝的大画面或立体视觉环境**。

主要应用场景包括：
1.  **多屏幕设置**：驾驶模拟器、天文馆、CAVE 系统等由多个物理屏幕组成一个大画面的环境。
2.  **立体视觉渲染**：使用多个 PC 分别渲染左眼和右眼画面，实现 VR/立体显示。
3.  **大范围投影**：将一个场景投影到复杂的非平面表面（如圆柱形、穹顶）上。

`DisplayClusterRemoteControlInterceptor` 模块是该系统的一个关键组件，它负责**拦截并通过集群同步虚幻引擎的远程控制（Remote Control）命令**，确保集群中所有节点在执行资产修改、函数调用等操作时保持状态一致。

## 使用场景

- 你正在搭建一个由 **3 台显示器组成的驾驶模拟器**，需要让画面在三台 PC 上同步渲染，形成环绕视野 → 使用 nDisplay 配置和同步渲染。
- 你需要一个 **CAVE（洞穴自动虚拟环境）系统**，用多面投影墙构建沉浸式空间 → 使用 nDisplay 配置投影和集群同步。
- 你有一个 **圆柱形投影幕**，需要将引擎画面正确映射到曲面上 → 使用 nDisplay 的投影和变形（Warp）功能。
- 你需要通过 **Remote Control** 从中央控制机修改集群中所有节点的资产属性，且要求所有节点同步生效 → 使用 `DisplayClusterRemoteControlInterceptor` 模块拦截并同步这些命令。

## 蓝图用法

`DisplayClusterRemoteControlInterceptor` 模块本身不直接暴露蓝图节点，它作为系统服务在底层运行。nDisplay 的主要蓝图交互通过其主模块 `DisplayCluster` 提供的工具和组件完成。以下是一些相关的高级操作节点（位于其他模块）：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Cluster Node` | 创建并配置一个集群节点 | `UDisplayClusterBlueprintAPI` |
| `Start Cluster` | 启动 nDisplay 集群 | `UDisplayClusterBlueprintAPI` |
| `Stop Cluster` | 停止 nDisplay 集群 | `UDisplayClusterBlueprintAPI` |
| `Get Cluster Node` | 获取当前或指定的集群节点信息 | `UDisplayClusterBlueprintAPI` |

### 使用示例（蓝图描述）

1.  **启动一个简单的双节点集群**：
    - 在你的游戏模式或 Level Blueprint 中，使用 `Create Cluster Node` 节点两次，分别命名为 “PC_主视口” 和 “PC_副视口”。
    - 为每个节点配置其负责渲染的屏幕区域（Viewport）和网络地址。
    - 调用 `Start Cluster` 节点，即可在两台 PC 上同步启动游戏。

2.  **通过 Remote Control 修改材质参数并同步**：
    - 在集群运行时，通过 Remote Control 面板修改一个材质实例的标量参数。
    - `DisplayClusterRemoteControlInterceptor` 会自动拦截此命令，将其序列化并通过集群事件系统广播。
    - 集群中的所有其他节点接收到该事件后，会同步应用相同的材质参数修改，确保所有屏幕画面一致。

## C++ 用法

### 头文件引入

```cpp
#include "IDisplayCluster.h"
#include "DisplayClusterRemoteControlInterceptor.h"
```

### 基本用法

从 `DisplayClusterRemoteControlInterceptor` 的实现中，我们可以看到其核心是拦截并处理远程控制命令。以下是其处理函数的基本结构（源自 `DisplayClusterRemoteControlInterceptor.h`）：

```cpp
// 来自 Source/DisplayClusterRemoteControlInterceptor/Private/DisplayClusterRemoteControlInterceptor.h

// 拦截器实现了 IRemoteControlInterceptionFeatureInterceptor 接口
class FDisplayClusterRemoteControlInterceptor : public IRemoteControlInterceptionFeatureInterceptor
{
public:
    // 当远程控制想要设置对象属性时被调用
    virtual ERCIResponse SetObjectProperties(FRCIPropertiesMetadata& InProperties) override;
    // 当远程控制想要重置对象属性时被调用
    virtual ERCIResponse ResetObjectProperties(FRCIObjectMetadata& InObject) override;
    // 当远程控制想要调用函数时被调用
    virtual ERCIResponse InvokeCall(FRCIFunctionMetadata& InFunction) override;
    // 当远程控制想要设置预设控制器时被调用
    virtual ERCIResponse SetPresetController(FRCIControllerMetadata& InController) override;

private:
    // 集群事件处理器，负责将拦截到的命令通过集群二进制事件广播
    void OnClusterEventBinaryHandler(const FDisplayClusterClusterEventBinary& Event);
    // 将命令数据入队，在下一个引擎 Tick 发送
    void QueueInterceptEvent(const FName& InterceptEventType, const FName& InUniquePath, TArray<uint8>&& InBuffer);
};
```

### 进阶用法

如果你想在自定义模块中**监听或模拟** nDisplay 的集群事件（用于同步自定义数据），可以参照 `DisplayClusterRemoteControlInterceptor` 使用集群事件系统：

```cpp
// 简化示例，展示如何监听集群二进制事件
FOnClusterEventBinaryListener MyListener;
MyListener.BindLambda([](const FDisplayClusterClusterEventBinary& Event)
{
    // 处理来自其他节点的同步数据
    if (Event.EventCategory == FName(TEXT("MyCustomSyncCategory")))
    {
        // 解析 Event.EventData 缓冲区
        // 同步自定义的游戏状态
    }
});

// 注册监听器
if (IDisplayCluster* DisplayClusterAPI = IDisplayCluster::Get())
{
    DisplayClusterAPI->GetClusterManager()->AddClusterEventBinaryListener(MyListener);
}

// 在需要的时候，发送自定义同步事件
TArray<uint8> CustomData;
// ... 填充 CustomData ...
FDisplayClusterClusterEventBinary MyEvent(FName(TEXT("MyCustomSyncCategory")), true /*bIsSystemEvent*/);
MyEvent.EventData = CustomData;
DisplayClusterAPI->GetClusterManager()->EmitClusterEventBinary(MyEvent, true /*bPrimaryOnly*/);
```

## Demo 示例

以下是一个极简的 **自定义集群事件发送/接收器** 的头文件和实现文件框架，演示了如何像 `DisplayClusterRemoteControlInterceptor` 一样使用集群事件系统进行数据同步。此示例**不**包含完整的 nDisplay 集群配置，仅聚焦于事件同步代码。

**MyClusterSyncComponent.h**
```cpp
// 版权所有 Epic Games, Inc。保留所有权利。

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "IDisplayClusterClusterManager.h"
#include "MyClusterSyncComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UMyClusterSyncComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyClusterSyncComponent();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    /** 处理来自其他节点的同步事件 */
    void OnClusterEventBinary(const FDisplayClusterClusterEventBinary& Event);

    /** 发送自定义同步数据到集群 */
    void SendSyncData(const FString& Message);

private:
    FOnClusterEventBinaryListener ClusterEventListener;
    FDelegateHandle ClusterEventDelegateHandle;
};
```

**MyClusterSyncComponent.cpp**
```cpp
// 版权所有 Epic Games, Inc。保留所有权利。

#include "MyClusterSyncComponent.h"
#include "IDisplayCluster.h"

UMyClusterSyncComponent::UMyClusterSyncComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyClusterSyncComponent::BeginPlay()
{
    Super::BeginPlay();

    // 绑定事件监听
    ClusterEventListener.BindUObject(this, &UMyClusterSyncComponent::OnClusterEventBinary);
    if (IDisplayCluster* DC = IDisplayCluster::Get())
    {
        if (IDisplayClusterClusterManager* ClusterMgr = DC->GetClusterManager())
        {
            ClusterEventDelegateHandle = ClusterMgr->AddClusterEventBinaryListener(ClusterEventListener);
        }
    }

    // 仅主节点发送一次示例数据
    if (IDisplayCluster* DC = IDisplayCluster::Get())
    {
        if (DC->GetClusterManager()->IsPrimary())
        {
            SendSyncData(TEXT("Hello from primary node!"));
        }
    }
}

void UMyClusterSyncComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 取消事件监听
    if (IDisplayCluster* DC = IDisplayCluster::Get())
    {
        if (IDisplayClusterClusterManager* ClusterMgr = DC->GetClusterManager())
        {
            ClusterMgr->RemoveClusterEventBinaryListener(ClusterEventDelegateHandle);
        }
    }
    Super::EndPlay(EndPlayReason);
}

void UMyClusterSyncComponent::OnClusterEventBinary(const FDisplayClusterClusterEventBinary& Event)
{
    // 检查是否是我们的自定义事件类别
    if (Event.EventCategory == FName(TEXT("MyProjectSync")))
    {
        // 从二进制数据中反序列化字符串
        FMemoryReader Reader(Event.EventData);
        FString ReceivedMessage;
        Reader << ReceivedMessage;
        UE_LOG(LogTemp, Log, TEXT("Received cluster sync message: %s"), *ReceivedMessage);
    }
}

void UMyClusterSyncComponent::SendSyncData(const FString& Message)
{
    // 序列化数据到二进制缓冲区
    TArray<uint8> Buffer;
    FMemoryWriter Writer(Buffer);
    Writer << Message;

    // 创建集群事件
    FDisplayClusterClusterEventBinary SyncEvent(FName(TEXT("MyProjectSync")), true /*bIsSystemEvent*/);
    SyncEvent.EventData = Buffer;

    // 仅由主节点广播给所有其他节点
    if (IDisplayCluster* DC = IDisplayCluster::Get())
    {
        DC->GetClusterManager()->EmitClusterEventBinary(SyncEvent, true /*bPrimaryOnly*/);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心逻辑，管理集群、同步和渲染 |
| `DisplayClusterConfiguration` | 处理 nDisplay 的配置数据（.ndisplay 文件） |
| `DisplayClusterProjection` | 负责投影变形、几何校正等功能 |
| `DisplayClusterMedia` | 处理媒体输出（如 SDI、NDI）的捕获和传输 |
| `SharedMemoryMedia` | 使用共享内存进行高效的媒体帧传输 |
| `ScalableMPCDI` | （第三方）用于处理 MPCDI 格式的投影数据 |
| `DisplayClusterRemoteControlInterceptor` | 拦截并同步 Remote Control 命令 |

**注意**：许多子模块（如 `DisplayClusterEditor`, `DisplayClusterConfigurator`）是编辑器专用，用于配置和调试。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为影片渲染图（MovieGraph）添加了 EXR 多图层支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 影片渲染管线：合并了WarpBlendAlpha模式到WarpBlend模式 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了MRG中的拓扑感知相机命名和MPCDI/ICVFX着色器的不透明Alpha问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码回退时遵守非默认的DisplayGamma设置 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当GUI纹理尺寸小于视口尺寸时出现的闪烁问题 |

### 维护评价

**活跃维护中**。nDisplay 是 Epic Games 用于其大型沉浸式项目（如虚拟制片、主题公园）的核心技术之一。从近期提交记录来看，开发团队仍在**非常活跃地**进行功能增强（如 EXR 多图层、影片渲染管线集成）和 Bug 修复。尽管该插件已存在约 8 年，但其复杂性和在虚拟制片等新兴领域的应用使其保持着持续的更新。它是一个成熟且得到官方支持的专业级解决方案。

**推荐使用**：如果你需要构建多屏幕同步渲染系统，nDisplay 是官方且功能完备的首选方案。但请注意，其配置和调试相对复杂，需要一定的学习成本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- 官方文档：无（.uplugin 中未提供 DocsURL）
- 测试用例：无（`.uplugin` 中未提供测试文件路径，但 `DisplayClusterTests` 模块包含相关测试代码）