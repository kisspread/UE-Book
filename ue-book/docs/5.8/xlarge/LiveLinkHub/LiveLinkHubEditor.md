# Live Link Hub

> LiveLink Hub allows streaming of animated data into Unreal Engine or UEFN（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接中枢 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkHub` (Runtime), `LiveLinkHubEditor` (Runtime), `LiveLinkHubMessaging` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkHub) | |

## 用途

基于源码分析，此插件并非独立的数据流传输核心，而是作为**编辑器与独立 LiveLink Hub 应用程序之间的集成桥梁**。其主要功能是：
1.  **状态监控**：在 Unreal Engine 编辑器底部状态栏显示与 LiveLink Hub 应用程序的连接状态、已连接的数据源和主题列表。
2.  **快速启动**：提供工具函数，用于检测本地是否安装了独立的 LiveLink Hub 应用程序，并能够直接从编辑器内启动它。

它解决了用户在编辑器内无法直观了解远端 Hub 连接情况，以及需要手动切换到操作系统去启动 Hub 程序的不便问题。

## 使用场景

- 你正在使用独立的 LiveLink Hub 应用程序来集中管理来自多个设备（如 iPhone、摄像头、动作捕捉系统）的实时动画数据流，并希望 Unreal Engine 编辑器能直观显示连接状态。
- 你希望从编辑器内部快速启动 LiveLink Hub 应用程序，而无需在操作系统中手动寻找并打开它。
- 你正在开发一个需要依赖实时外部动画数据的场景（如虚拟制片、实时预览），并需要监控数据链路的健康状况。

## 蓝图用法

此插件的蓝图 API 较为有限，主要提供了启动和检测 LiveLink Hub 应用程序的功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindLiveLinkHubInstallation` | 检查 Epic Games Launcher 是否安装了 LiveLink Hub，并获取其安装信息。 | `UE::LiveLinkHubLauncherUtils` |
| `OpenLiveLinkHub` | 启动本地安装的 LiveLink Hub 可执行文件。 | `UE::LiveLinkHubLauncherUtils` |

### 使用示例（蓝图描述）

**场景：一键启动 LiveLink Hub**
1.  在蓝图中，使用 `Find Live Link Hub Installation` 节点。将其 `Success` 引脚连接到一个分支节点。
2.  如果 `Success` 为 `True`，则调用 `Open Live Link Hub` 节点来启动应用程序。
3.  如果 `Success` 为 `False`，可以连接一个消息节点提示用户前往 Epic Games Store 安装。

**注意**：状态栏组件 `SLiveLinkHubEditorStatusBar` 是 C++ 实现的 Slate 控件，其显示逻辑（图标颜色、连接状态、主题列表）是自动的，无需通过蓝图手动控制。只要与 Hub 建立连接，它便会自动出现在编辑器状态栏。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkHubLauncherUtils.h"
```

### 基本用法

此插件的主要 C++ 公开 API 位于 `LiveLinkHubLauncherUtils.h` 中，用于与独立 Hub 应用交互。

```cpp
// 来源: Public/LiveLinkHubLauncherUtils.h
// 用于检测并启动 LiveLink Hub 应用程序。
UE::LiveLinkHubLauncherUtils::FInstalledApp HubInfo;
bool bInstalled = UE::LiveLinkHubLauncherUtils::FindLiveLinkHubInstallation(HubInfo);

if (bInstalled)
{
    UE_LOG(LogTemp, Log, TEXT("找到 LiveLink Hub，版本: %s，路径: %s"), *HubInfo.AppVersion, *HubInfo.InstallLocation);
    
    // 启动应用程序
    UE::LiveLinkHubLauncherUtils::OpenLiveLinkHub();
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("未找到 LiveLink Hub 安装。"));
}
```

### 进阶用法

插件的编辑器扩展模块 `LiveLinkHubEditor` 主要通过模块接口 `FLiveLinkHubEditorModule` 进行管理，通常在插件启动时自动注册状态栏。开发者如果需要自定义，可以关注模块的 `StartupModule` 和 `ShutdownModule`。

```cpp
// 来源: Private/LiveLinkHubEditorModule.h
// 插件模块会自动执行以下操作：
// 1. 在 `StartupModule` 中，通过 `OnPostEngineInit` 回调注册状态栏扩展。
// 2. 在 `ShutdownModule` 中，注销状态栏扩展。
// 自定义连接状态检查逻辑可能需要继承或修改 `SLiveLinkHubEditorStatusBar`。
```

## Demo 示例

一个最小化的、展示如何检测并启动 LiveLink Hub 的 C++ 示例。

```cpp
// MyLiveLinkHubLauncher.h
#pragma once
#include "CoreMinimal.h"

class FMyLiveLinkHubLauncher
{
public:
    /** 检查并尝试启动 LiveLink Hub */
    static void TryLaunchLiveLinkHub();
};

// MyLiveLinkHubLauncher.cpp
#include "MyLiveLinkHubLauncher.h"
#include "LiveLinkHubLauncherUtils.h"
#include "HAL/PlatformProcess.h"

void FMyLiveLinkHubLauncher::TryLaunchLiveLinkHub()
{
    UE::LiveLinkHubLauncherUtils::FInstalledApp AppInfo;
    if (UE::LiveLinkHubLauncherUtils::FindLiveLinkHubInstallation(AppInfo))
    {
        UE_LOG(LogTemp, Display, TEXT("正在启动 LiveLink Hub..."));
        UE::LiveLinkHubLauncherUtils::OpenLiveLinkHub();
    }
    else
    {
        // 可以引导用户打开商店页面，商店页面 URI 可从 ULiveLinkHubEditorSettings 获取
        UE_LOG(LogTemp, Warning, TEXT("LiveLink Hub 未安装。"));
    }
}
```

## 模块依赖

要使用此插件，你的模块通常不需要直接依赖它，因为它的主要功能是扩展编辑器 UI。如果你需要在自己的工具中集成其启动功能，则需要依赖 `LiveLinkHubEditor` 模块。

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心 LiveLink 客户端/框架，用于与 Hub 建立通信和状态管理。 |
| `LiveLinkInterface` | LiveLink 的接口定义，包括源、主体等关键数据结构。 |
| `Settings` | 用于处理编辑器设置（`ULiveLinkHubEditorSettings`）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `54cbb9f8` | Ensure a transient MediaProfile always exists from startup | 确保启动时始终存在一个临时媒体配置文件 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-05-13 | `1e2d2efc` | Removed delegate pattern for transient profile creation (simplified to direct NewObject in MediaProfile) | 移除了临时配置文件创建的委托模式，简化为直接 NewObject |
| 2026-05-13 | `be3a46dd` | Fix use of recording directories nested inside the content folder. | 修复了在内容文件夹内嵌套使用录制目录的问题 |
| 2026-05-12 | `ded7015a` | LiveLinkHub - Fix not being able to connect to a client if auto-connect is disabled | 修复在禁用自动连接时无法连接到客户端的问题 |

### 维护评价

该插件仍处于**活跃维护**状态。创建于 2024 年初，属于较新的插件。近期的提交记录（截至 2026 年）表明其仍在持续进行功能完善和问题修复，尤其是围绕连接性、录制路径和配置文件管理的改进。

**重要提示**：
- 该插件在 `.uplugin` 中标记为 `IsBetaVersion: true`，且 `EnabledByDefault: false`，表明它仍处于**实验性/Beta 阶段**。
- API 和功能可能在未来版本中发生变化。
- 目前推荐用于原型验证和特定工作流测试，不建议作为生产环境的核心稳定依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkHub)
- 官方文档链接为空，暂无独立官方文档。
- 测试用例路径未在提供信息中明确，通常位于 `Engine/Plugins/Animation/LiveLinkHub/Tests` 目录下（需自行验证）。