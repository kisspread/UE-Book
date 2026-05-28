# Live Link Hub

> LiveLink Hub allows streaming of animated data into Unreal Engine or UEFN

| 属性 | 值 |
|---|---|
| 中文名 | 动画数据流中枢 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkHub` (Runtime), `LiveLinkHubEditor` (Runtime), `LiveLinkHubMessaging` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkHub) | |

## 用途

Live Link Hub 是一个独立的动画数据流中枢应用程序或进程，其核心设计是将动画数据的**生产者**（如动捕设备、虚拟摄像机、自定义动画软件）与**消费者**（如虚幻引擎实例、UEFN 应用）解耦。

它解决的问题是：当有多个动画数据源需要同时供给多个引擎实例时，传统的点对点 LiveLink 连接会变得复杂且难以管理。Live Link Hub 充当一个中心服务器/代理，负责接收、管理、路由和录制来自多个源的动画数据流，从而简化复杂的实时动画数据传输网络拓扑。

## 使用场景

- **多源汇聚**：你同时使用来自面部动捕、身体动捕和手部动捕的多个数据流，需要将它们汇聚到一个中枢，再统一分发给一个或多个引擎实例。
- **集中管理**：在一个大型的虚拟制片或多显示器渲染环境中，需要从一个中心点控制所有动画数据流的连接、断开和参数调整。
- **数据录制与回放**：你需要在数据流传输的同时，录制原始动画数据，以便在没有原始数据源的设备上进行回放和调试。
- **网络优化**：作为网络中的一个优化节点，处理数据压缩、协议转换等，减轻最终引擎实例的负载。

## 蓝图用法

LiveLinkHub 主要是一个独立运行时组件，其蓝图交互通常通过 `LiveLinkHubEditor` 模块提供的编辑器面板进行配置和监控，而非直接在游戏逻辑中大量使用蓝图节点。核心的蓝图/编辑器功能集中在连接管理和数据流控制上。

### 核心节点（编辑器内）

| 节点 | 说明 | 所在类 |
|---|---|---|
| 连接管理面板 | 可视化添加、删除、配置 Live Link 源和主题 | `LiveLinkHubEditor` 模块 UI |
| 数据录制控制 | 启动/停止动画数据流录制，并指定保存路径 | `LiveLinkHubEditor` 模块 UI |
| 客户端连接监控 | 查看当前连接到此 Hub 的引擎客户端列表及状态 | `LiveLinkHubEditor` 模块 UI |

### 使用示例（蓝图描述）

LiveLinkHub 的使用通常不涉及在游戏蓝图中连接节点，而是通过其提供的独立编辑器应用程序或编辑器内停靠面板（`LiveLinkHubEditor`）进行操作。流程如下：
1.  启动 LiveLinkHub 应用程序或启用插件后，在虚幻编辑器的“窗口”菜单中打开“Live Link Hub”面板。
2.  在面板中点击“添加源”按钮，配置外部动画数据源（如 Vicon、OptiTrack 服务器）。
3.  在“客户端”或“主题”管理区域，为目标虚幻引擎实例（作为消费者）配置订阅的主题。
4.  通过面板上的控制按钮管理数据流（播放、停止、录制）。

## C++ 用法

LiveLinkHub 的 C++ 接口主要用于**集成**，即将 Live Link Hub 的核心功能嵌入到自定义的独立应用程序中。

### 头文件引入

```cpp
// 用于创建和管理 Hub 实例
#include "LiveLinkHub.h"

// 用于消息序列化与网络通信
#include "LiveLinkHubMessages.h"

// （可选）用于编辑器面板集成
#include "LiveLinkHubEditorModule.h"
```

### 基本用法

创建一个基本的 Live Link Hub 实例并启动其服务。
(来源: 模块概述 `LiveLinkHub.md`)

```cpp
#include "LiveLinkHub.h"
#include "Modules/ModuleManager.h"

// 确保 LiveLinkHub 模块已加载
ILiveLinkHubModule& LiveLinkHubModule = FModuleManager::Get().LoadModuleChecked<ILiveLinkHubModule>(TEXT("LiveLinkHub"));

// 获取 Hub 实例
TSharedPtr<ILiveLinkHub> LiveLinkHub = LiveLinkHubModule.GetLiveLinkHub();

// 配置并启动 Hub（具体配置参数需参考模块文档）
LiveLinkHub->Configure(/* Configuration parameters */);
LiveLinkHub->Start();
```

### 进阶用法

通过 `LiveLinkHubMessaging` 模块自定义数据序列化，实现对专有数据格式的支持。
(概念来源于模块职责划分)

```cpp
#include "ILiveLinkHubMessaging.h"

// 假设有一个自定义的 FMyAnimationData 类型
class FMyAnimationDataSerializer : public ILiveLinkHubMessageSerializer
{
public:
    virtual TArray<uint8> Serialize(const FLiveLinkSubjectFrame& InFrame) override
    {
        // 实现自定义数据序列化逻辑
        // 将 FMyAnimationData 转换为字节流
    }
    virtual bool Deserialize(const TArray<uint8>& InData, FLiveLinkSubjectFrame& OutFrame) override
    {
        // 实现自定义数据反序列化逻辑
        // 将字节流解析回 FMyAnimationData
    }
};

// 注册自定义序列化器
// LiveLinkHubModule.GetLiveLinkHub()->RegisterSerializer(TEXT("MyDataFormat"), MakeShared<FMyAnimationDataSerializer>());
```

## Demo 示例

以下是一个最小化、可编译的 C++ 示例，演示如何在自己的程序模块中初始化并获取 Live Link Hub 实例。
```cpp
// MyLiveLinkHost.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyLiveLinkHost
{
public:
    void Initialize();
    void Shutdown();

private:
    // 保持对 Hub 实例的引用，生命周期管理
    TSharedPtr<class ILiveLinkHub> LiveLinkHubInstance;
};
```

```cpp
// MyLiveLinkHost.cpp
#include "MyLiveLinkHost.h"
#include "LiveLinkHub.h" // LiveLinkHub 模块的公开头文件

void FMyLiveLinkHost::Initialize()
{
    // 1. 加载 LiveLinkHub 模块
    ILiveLinkHubModule& LiveLinkHubModule = FModuleManager::Get().LoadModuleChecked<ILiveLinkHubModule>(TEXT("LiveLinkHub"));

    // 2. 获取或创建 Hub 实例
    LiveLinkHubInstance = LiveLinkHubModule.GetLiveLinkHub();
    check(LiveLinkHubInstance.IsValid());

    // 3. （可选）进行配置，如设置监听端口
    // LiveLinkHubInstance->SetPort(12345);

    // 4. 启动 Hub 服务，开始监听连接和数据流
    if (LiveLinkHubInstance->Start())
    {
        UE_LOG(LogTemp, Log, TEXT("Live Link Hub 已成功启动。"));
    }
}

void FMyLiveLinkHost::Shutdown()
{
    if (LiveLinkHubInstance.IsValid())
    {
        LiveLinkHubInstance->Stop();
        LiveLinkHubInstance.Reset();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 核心框架，定义主题、角色、数据帧等基础类型和接口。 |
| `LiveLinkInterface` | Live Link 的接口定义模块，用于客户端和服务器之间的约定。 |
| `Networking` | 提供网络通信基础，用于 Hub 与数据源及客户端之间的连接。 |
| `MediaUtils` | 可能用于处理媒体流相关的计时、缓冲和同步。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `54cbb9f8` | Ensure a transient MediaProfile always exists from startup | 确保启动时始终存在一个临时的 MediaProfile，提升稳定性。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 常量截断为 float 的编译器警告。 |
| 2026-05-13 | `1e2d2efc` | Removed delegate pattern for transient profile creation (simplified to direct NewObject in MediaProf... | 简化了临时配置文件的创建逻辑，移除了委托模式。 |
| 2026-05-13 | `be3a46dd` | Fix use of recording directories nested inside the content folder. | 修复在 Content 文件夹内嵌套录制目录时可能存在的问题。 |
| 2026-05-12 | `ded7015a` | LiveLinkHub - Fix not being able to connect to a client if auto-connect is disabled | 修复了在禁用自动连接时无法手动连接到客户端的 Bug。 |

### 维护评价

LiveLinkHub 是一个较新（约1年）且处于**实验性/测试阶段**的插件。从近期提交记录看，开发团队正在**积极维护**，近期活动频繁，主要集中在**功能完善、代码优化和 Bug 修复**上（如修复连接问题、改进数据录制、解决编译警告）。由于其 `IsBetaVersion: true` 和 `EnabledByDefault: false` 的状态，表明它仍在迭代和验证中，可能尚未达到完全稳定。**推荐在评估和实验性项目中使用**，但在追求稳定性的生产环境中需谨慎评估，并做好跟进更新的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkHub)
- [官方文档]() （`.uplugin` 中 DocsURL 为空，暂无）
- [子模块文档](./LiveLinkHub.md)、[子模块文档](./LiveLinkHubEditor.md)、[子模块文档](./LiveLinkHubMessaging.md)