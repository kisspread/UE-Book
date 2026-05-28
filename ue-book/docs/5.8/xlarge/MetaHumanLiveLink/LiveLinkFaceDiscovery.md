# MetaHuman Live Link

> Live Link sources and associated utilities for streaming real time MetaHuman animation data.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman实时链接 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产， 示例动画） |
| 模块 | `LiveLinkFaceDiscovery` (Runtime), `LiveLinkFaceSource` (Runtime), `LiveLinkFaceSourceEditor` (Runtime), `MetaHumanLiveLinkSource` (Runtime), `MetaHumanLiveLinkSourceEditor` (Runtime), `MetaHumanLocalLiveLinkSource` (Runtime), `MetaHumanLocalLiveLinkSourceEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanLiveLink) | |

## 用途

MetaHuman Live Link 插件的核心功能是建立 Epic Games 的 MetaHuman Creator 应用程序与 Unreal Engine 5 之间的实时数据链接。它主要用于从外部设备（如 iPhone 上的 Live Link Face 应用）或本地已录制的表演数据中，实时流式传输面部及身体动画数据到引擎中的 MetaHuman 角色上。

该插件解决了从创建、预览到直播表演的完整工作流程中，实时驱动高保真数字人角色的关键问题。它允许用户无需复杂的录制和重定向流程，即可在编辑器内实时预览动画效果，或在虚拟直播中实现与真人表演同步的 MetaHuman 互动。

## 使用场景

*   **虚拟直播与表演**：使用配备 Live Link Face 的 iPhone 或其他设备，在直播软件（如 OBS）中实时驱动 MetaHuman 角色的面部表情和头部动作，用于虚拟主播、新闻播报或在线会议。
*   **实时动画预览**：动画师在 Maya 或 Blender 等 DCC 软件中调整动画时，可以通过网络实时预览动画在 UE5 中 MetaHuman 角色上的最终效果，加速迭代过程。
*   **本地表演回放**：将已录制好的表演数据（如 `.mha` 文件）作为本地源，在 UE5 中回放并驱动角色，用于动画审查或场景编排。
*   **多角色驱动**：通过网络同时连接和驱动多个 MetaHuman 角色，适用于复杂的对话场景或群组表演。
*   **性能与效果测试**：快速测试不同动画数据在 MetaHuman 渲染管线中的性能和最终视觉表现。

## 蓝图用法

由于该插件的蓝图功能主要通过 Live Link 系统实现，以下节点为通用操作：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start` | 启动设备发现，开始在网络中搜索运行 Live Link Face 的设备 | `FLiveLinkFaceDiscovery` |
| `Stop` | 停止设备发现过程 | `FLiveLinkFaceDiscovery` |
| `OnServersUpdated` | 委托，当发现的设备列表更新时触发，传入当前所有发现的设备信息 | `FLiveLinkFaceDiscovery` |

### 使用示例（蓝图描述）

1.  **发现并连接设备**：
    *   创建一个 `FLiveLinkFaceDiscovery` 实例（在蓝图中可能通过某个管理类暴露）。
    *   调用 `Start` 函数开始扫描。
    *   绑定 `OnServersUpdated` 委托。当委托触发时，从传入的 `Servers` 集合中获取目标设备的 `Address` 和 `ControlPort`。
    *   使用这些信息，通过 UE 的 Live Link 面板或蓝图节点添加一个新的 Live Link 源，选择 MetaHuman 或 Face 类型，输入设备地址和端口进行连接。
2.  **驱动 MetaHuman**：
    *   在场景中放置一个 `MetaHuman` 角色。
    *   在其 `AnimGraph` 的 `Live Link Pose` 节点中，选择已连接的 Live Link 源。
    *   运行游戏或关卡，角色将实时接收并应用来自外部设备的动画数据。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkFaceDiscovery.h"
```

### 基本用法

从 `Public/LiveLinkFaceDiscovery.h` 中提取的设备发现核心逻辑。

```cpp
// 创建一个发现实例，默认每3秒刷新一次，设备离线超时6秒
FLiveLinkFaceDiscovery Discovery(3.0, 6.0);

// 绑定设备列表更新回调
Discovery.OnServersUpdated.BindLambda([](const TSet<FLiveLinkFaceDiscovery::FServer>& Servers)
{
    // 在游戏线程处理更新的设备列表
    for (const FLiveLinkFaceDiscovery::FServer& Server : Servers)
    {
        UE_LOG(LogTemp, Log, TEXT("发现设备: %s (IP: %s, 端口: %d)"), *Server.Name, *Server.Address, Server.ControlPort);
    }
});

// 开始发现
Discovery.Start();

// ... 在应用退出或不再需要时停止发现
Discovery.Stop();
```

### 进阶用法

结合 Live Link 系统，在发现设备后建立连接。这通常由编辑器模块（如 `MetaHumanLiveLinkSourceEditor`）封装，但核心流程如下：

```cpp
#include "LiveLinkFaceDiscovery.h"
#include "ILiveLinkClient.h"
#include "Roles/LiveLinkAnimationRole.h"

// 假设已通过某种方式获取到 LiveLinkClient 实例
ILiveLinkClient* LiveLinkClient = ...;

FLiveLinkFaceDiscovery Discovery;
Discovery.OnServersUpdated.BindLambda([LiveLinkClient](const TSet<FLiveLinkFaceDiscovery::FServer>& Servers)
{
    // 查找第一个可用的服务器
    if (const FLiveLinkFaceDiscovery::FServer* Server = Servers.CreateIterator())
    {
        // 使用服务器的地址和端口创建 Live Link 连接参数
        // 具体创建源的方式取决于 LiveLinkFaceSource 模块的实现
        // 伪代码：
        // FProviderHandle Handle = LiveLinkClient->CreateSource(...);
        // LiveLinkClient->SetSubjectRole(Handle, ULiveLinkAnimationRole::StaticClass());
        UE_LOG(LogTemp, Log, TEXT("尝试连接至 %s"), *Server->Address);
    }
});
Discovery.Start();
```

## Demo 示例

一个最小的 C++ 模块，演示如何初始化并使用设备发现功能。

```cpp
// MetaHumanLiveLinkDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMetaHumanLiveLinkDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<FLiveLinkFaceDiscovery> FaceDiscovery;
    FDelegateHandle OnServersUpdatedHandle;
};

// MetaHumanLiveLinkDemo.cpp
#include "MetaHumanLiveLinkDemo.h"
#include "LiveLinkFaceDiscovery.h"

#define LOCTEXT_NAMESPACE "FMetaHumanLiveLinkDemoModule"

void FMetaHumanLiveLinkDemoModule::StartupModule()
{
    // 创建发现对象
    FaceDiscovery = MakeShared<FLiveLinkFaceDiscovery>(2.0f, 5.0f); // 2秒刷新，5秒超时

    // 绑定回调
    OnServersUpdatedHandle = FaceDiscovery->OnServersUpdated.AddLambda(
        [](const TSet<FLiveLinkFaceDiscovery::FServer>& Servers)
        {
            UE_LOG(LogTemp, Display, TEXT("MetaHumanLiveLinkDemo: 发现 %d 个设备。"), Servers.Num());
            for (const auto& Server : Servers)
            {
                UE_LOG(LogTemp, Display, TEXT("  - %s (%s)"), *Server.Name, *Server.Address);
            }
        }
    );

    // 开始发现
    FaceDiscovery->Start();
    UE_LOG(LogTemp, Log, TEXT("MetaHumanLiveLinkDemo 模块已启动，开始扫描设备。"));
}

void FMetaHumanLiveLinkDemoModule::ShutdownModule()
{
    if (FaceDiscovery.IsValid())
    {
        FaceDiscovery->Stop();
        FaceDiscovery->OnServersUpdated.Remove(OnServersUpdatedHandle);
        FaceDiscovery.Reset();
    }
    UE_LOG(LogTemp, Log, TEXT("MetaHumanLiveLinkDemo 模块已关闭。"));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMetaHumanLiveLinkDemoModule, MetaHumanLiveLinkDemo)
```

## 模块依赖

从各模块的 `Build.cs` 分析，该插件依赖于 Unreal Engine 的 Live Link 框架以及用于编辑器界面的组件。

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 核心框架，提供源、主体、角色等基础结构 |
| `LiveLinkComponents` | 提供在蓝图中使用 Live Link 数据的组件 |
| `EditorWidgets` | （仅 `MetaHumanLocalLiveLinkSourceEditor`）提供自定义编辑器控件 |
| `UnrealEd` | （仅 `MetaHumanLocalLiveLinkSourceEditor`）提供编辑器扩展功能 |
| `PropertyEditor` | （仅 `MetaHumanLocalLiveLinkSourceEditor`）用于自定义属性面板 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `9bee2cb0` | [MHA] Expose detection thresholds for body | 暴露身体动画检测阈值参数 |
| 2026-05-14 | `988b3911` | [MHA] Face animation sequence export changes for combined solve | 为组合求解器修改面部动画序列导出功能 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数的警告 |
| 2026-05-12 | `8bf9ba92` | [MetaHumanLiveLink] Use AvfMedia for FileMediaSource bundles on Apple platforms | 在苹果平台为文件媒体源使用AVFoundation媒体 |
| 2026-05-12 | `fa06fada` | New ADA model | 更新ADA（动画驱动架构）模型 |

### 维护评价

*   **活跃维护**：该插件创建时间较新（2025年2月），并且从最近的提交记录（2026年5月）看，维护非常活跃。更新内容涉及功能增强（暴露新参数、修改导出）、平台兼容性优化（Apple平台媒体）以及底层动画模型的更新。
*   **状态**：作为 MetaHuman 官方工具链的核心部分，该插件由 Epic Games 直接维护，稳定性与持续更新有保障。
*   **推荐**：**强烈推荐**。对于任何涉及 MetaHuman 实时动画驱动的工作流，此插件都是不可或缺的官方工具。其活跃的开发确保了与最新引擎版本和动画技术的兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanLiveLink)
- [官方文档]() (文档链接待补充，请查阅 Epic 官方 MetaHuman 文档或 UE5 插件文档页面)
- [测试用例]() (测试文件路径待确认)