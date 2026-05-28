# Concert Insights Client

> Extends status bar so you can start a synchronized trace on all connected Concert endpoints.

| 属性 | 值 |
|---|---|
| 中文名 | 会话跟踪客户端 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConcertInsightsClient` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-06 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsClient) | |

## 用途

这个插件是 Unreal Insights 性能分析工具的扩展，专门用于解决**多用户（Multi-User）协作会话**下的分布式性能跟踪问题。它的核心价值在于，当你在一个 Concert（多用户）会话中与团队成员协作时，可以一键启动对所有连接端点（包括服务器和客户端）的同步性能追踪。

它解决的问题是：传统的性能追踪只针对单个实例，而多用户会话中问题可能源于不同机器间的交互或负载，需要同时收集所有参与者的性能数据并关联分析。

## 使用场景

- **多人在线编辑同一场景时性能出现卡顿**：你怀疑是网络同步或特定客户端操作导致的瓶颈，需要同时分析服务器和所有客户端的性能数据。
- **分布式任务处理**：在多个 Unreal 实例协同处理大型任务（如烘焙、渲染）时，需要监控整体性能和瓶颈分布。
- **调试网络相关的复杂行为**：当行为在单机下无法复现，但在多用户会话中出现时，需要跨机器追踪以定位问题根源。

## 蓝图用法

**注意**：此插件主要作为编辑器内的开发工具，通过状态栏菜单进行交互，**没有提供可直接在蓝图中调用的节点**。其核心功能是通过 C++ 模块和 Slate UI 扩展实现的。

### 核心交互方式

用户通过扩展后的编辑器状态栏菜单操作：

1.  **开始同步追踪**：一键向所有连接的 Concert 端点发送指令，同时开始 Unreal Insights 追踪。
2.  **配置追踪目标**：可设置同步追踪数据的汇总服务器 IP 地址（默认 `localhost`）。

## C++ 用法

### 头文件引入

```cpp
#include "IConcertInsightsClientModule.h"
```

### 基本用法

**获取模块实例（用于检查模块是否可用）**

```cpp
// 检查模块是否加载
if (UE::ConcertInsightsClient::IConcertInsightsClientModule::IsAvailable())
{
    // 获取模块引用
    UE::ConcertInsightsClient::IConcertInsightsClientModule& InsightsClientModule = UE::ConcertInsightsClient::IConcertInsightsClientModule::Get();
    // 通常不需要直接操作模块，主要功能通过 UI 触发
}
```
*来源：`IConcertInsightsClientModule.h`*

### 进阶用法（面向插件开发者）

此插件的设计模式清晰，展示了如何扩展编辑器状态栏和集成到 Unreal Insights。

**1. 理解模块职责**
`IConcertInsightsClientModule` 是模块接口，其实现 `FConcertInsightsClientModule` 在启动时执行了以下关键操作（由代码推断）：
- 初始化 `FClientTraceControls` 对象，用于管理本地追踪状态和会话连接。
- 在引擎初始化完成后，扩展编辑器状态栏，添加多用户追踪控件。

**2. 扩展状态栏（参考插件内部实现）**
插件内部使用 `SMultiUserStatusBar` 和 `SEditTraceDestinationWidget` 来构建 UI。核心逻辑在 `StatusBarExtension.h` 中声明的 `ExtendMultiUserStatusBarWithInsights` 函数，它将追踪菜单注入到多用户状态栏。

## Demo 示例

由于此插件是编辑器工具，以下示例展示如何在你自己的编辑器模块中，参考其模式来扩展状态栏或实现类似功能。

**场景**：创建一个简单的编辑器模块，在状态栏添加一个按钮来输出日志。

```cpp
// MyStatusBarExtension.h
#pragma once
#include "CoreMinimal.h"

namespace MyExtension
{
    void AddCustomButtonToStatusBar();
}
```

```cpp
// MyStatusBarExtension.cpp
#include "MyStatusBarExtension.h"
#include "Framework/Docking/TabManager.h"
#include "StatusBarSubsystem.h"

void MyExtension::AddCustomButtonToStatusBar()
{
    // 注意：状态栏扩展的 API 可能随版本变化，此处为示例逻辑
    FStatusBarModule& StatusBarModule = FModuleManager::LoadModuleChecked<FStatusBarModule>("StatusBar");
    // 这里仅为演示思路，实际扩展方式请参考引擎源码或 ConcertInsightsClient 的实现
    UE_LOG(LogTemp, Log, TEXT("StatusBar extension point reached. In a real plugin, a Slate widget would be added here."));
}
```

**模块启动函数**：
```cpp
// MyModule.cpp
#include "MyStatusBarExtension.h"

void FMyModule::StartupModule()
{
    // 确保在引擎完全初始化后再扩展UI
    FCoreDelegates::OnPostEngineInit.AddLambda([]()
    {
        MyExtension::AddCustomButtonToStatusBar();
    });
}
```
*注意：这是一个高度简化的示例。实际的状态栏扩展需要深入使用 `Slate` 和 `StatusBarSubsystem` API，并严格遵循 ConcertInsightsClient 中的模式。*

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件作为开发工具，其核心依赖是引擎内置的 `Concert` 和 `UnrealInsights` 相关模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复上次错误的查找替换后，重新提交代码修改。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚提交 CL51314860 的改动。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 适配引擎 API 变更，将弃用的委托访问方式更新为新方法，以修复注册问题。 |
| 2025-03-06 | `742b5d3a` | Remove inappropriate use of UE_LIFETIMEBOUND from void returning functions | 清理代码，移除 void 函数上不合适的 UE_LIFETIMEBOUND 宏。 |
| 2024-05-13 | `ee845008` | Fix duplicate loca keys | 修复重复的本地化键值问题。 |

### 维护评价

- **创建时间**：2024年5月，是一个相对较新的插件。
- **维护频率**：近期（2026年2月）有活跃的维护和适配性更新，表明它跟随引擎主线（ue5-main）进行开发。
- **状态**：**实验性（IsExperimentalVersion=true）**，且默认隐藏（Hidden=true），说明它可能尚未稳定，API 和功能可能发生变化，不建议在生产环境中依赖。
- **推荐使用**：适合**高级用户和插件开发者**研究多用户性能追踪的实现，或需要在特定版本（匹配引擎主线）中进行分布式性能分析。对于普通项目，建议等待其正式发布或转为稳定插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsClient)
- [官方文档]( （无） )