# Android Fetch Background Download

> An Android plugin for enabling BackgroundHTTP requests to work while the app is backgrounded through use of the Fetch API.

| 属性 | 值 |
|---|---|
| 中文名 | 安卓后台下载 |
| 分类 | BackgroundHTTP |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidFetchBackgroundDownload` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2021-06-22 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/Android/AndroidFetchBackgroundDownload) | |

## 用途

此插件为 Android 平台的 BackgroundHTTP 模块提供了原生实现。它解决的核心问题是：**在 UE 的标准 HTTP 下载中，一旦 Android 应用被用户切换到后台（例如按 Home 键），系统很可能会暂停或终止下载进程**。本插件通过调用 Android 原生的 Fetch API 和 WorkManager，将下载任务委托给系统级别的后台服务，确保即使在游戏或应用不在前台时，下载任务也能持续进行。这对于需要长时间下载大型资源（如游戏更新包、离线内容）的移动应用至关重要。

## 使用场景

- 你的 Android 游戏需要下载一个 2GB 的资源包，但玩家可能会在下载过程中切出游戏。
- 你的应用需要持续同步服务器数据，希望在后台静默完成，不影响用户体验。
- 你需要遵循 Android 系统的后台任务限制和最佳实践（如电池优化、数据使用策略），同时确保下载的可靠性。

## 蓝图用法

此插件主要在后台自动集成到 BackgroundHTTP 模块中，不直接提供面向设计师的蓝图节点。所有后台下载的逻辑由 `FBackgroundHttpManager` 在运行时根据平台自动选择使用此原生实现。开发者在蓝图中使用标准的 `HTTP Request` 节点时，如果目标是 Android 平台且插件启用，下载将自动由后台服务管理。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| *无直接蓝图节点* | 后台下载功能由平台模块自动提供，通过标准 HTTP 接口触发 | `FBackgroundHttpManager` |

## C++ 用法

此插件的使用是隐式的。当 `BackgroundHTTP` 模块加载时，它会通过模块化特性（Modular Feature）机制查找并注册合适的平台实现。在 Android 平台上，本插件会将自身注册为 `IBackgroundHttpModularFeature`，从而接管所有后台 HTTP 请求的管理。

### 头文件引入

通常不需要直接包含本插件的头文件，而是通过 `BackgroundHTTP` 模块的标准接口进行操作。

```cpp
// 使用 BackgroundHTTP 的通用接口
#include "BackgroundHttpManager.h"
```

### 基本用法

开发者无需直接与本插件的类交互。以下示例展示了如何发起一个标准的后台 HTTP 请求，该请求在 Android 上将由本插件的原生服务处理。

```cpp
// 创建并发送一个后台 HTTP 请求
FBackgroundHttpRequestPtr Request = FBackgroundHttpModule::Get().CreateRequest();
Request->SetURL(TEXT("https://example.com/large_asset.pak"));
Request->SetDestinationLocation(FPaths::ProjectSavedDir() / TEXT("Downloads/large_asset.pak"));
Request->ProcessRequest();
```
*来源：基于 BackgroundHTTP 模块的标准用法*

### 进阶用法

本插件的管理器 (`FAndroidPlatformBackgroundHttpManager`) 提供了对后台任务更精细的控制，例如暂停、恢复和取消请求。这些操作通常由内部管理，但可以通过 `FBackgroundHttpManager` 的通用接口访问。

```cpp
// 假设你已经持有一个指向后台管理器的指针
FBackgroundHttpManagerPtr Manager = FBackgroundHttpModule::Get().GetBackgroundHttpManager();
if (Manager)
{
    // 暂停特定的请求
    Manager->PauseRequest(MyRequest);
    
    // 恢复请求
    Manager->ResumeRequest(MyRequest);
    
    // 取消请求
    Manager->CancelRequest(MyRequest);
}
```

## Demo 示例

本插件没有独立的示例。其功能通过 `BackgroundHTTP` 模块的标准 API 进行演示。

## 模块依赖

从 `.Build.cs` 分析，此插件依赖于 `AndroidBackgroundService` 插件提供的 Java 后台服务。

| 模块 | 用途 |
|---|---|
| `AndroidBackgroundService` | 提供 Android 原生的后台任务服务（WorkManager）和 JNI 桥接代码 |
| `BackgroundHTTP` | 提供跨平台的后台 HTTP 下载抽象层和接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `407fca16` | [Mobile][Android] Adding in "onResponse" debug log for AsyncDownloader which will help diagnose prot | 为异步下载器添加响应调试日志，帮助诊断问题 |
| 2026-05-12 | `5453e6f1` | Enable background download statistics for Android | 启用 Android 后台下载统计功能 |
| 2026-04-21 | `0f538bd5` | Properly reporting out-of-diskspace-errors in background downloading in IOS | 修复 iOS 后台下载中磁盘空间不足的错误报告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF |
| 2026-04-09 | `dc686146` | [Android] Fix: Set the StartTime record only when the HTTP request actually starts. | 修复：仅在 HTTP 请求实际启动时才设置 StartTime 记录 |

### 维护评价

- **活跃维护**：最近的更新记录显示该插件在 2026 年仍在持续维护和改进，包括功能增强（启用统计）、错误修复（磁盘空间、启动时间）和日志优化。
- **平台特定**：这是一个高度平台特定的插件，其维护通常与 Android 平台的演进和 Epic 的移动平台策略紧密相关。
- **推荐使用**：如果你的目标平台包含 Android，并且你的应用需要可靠的后台下载功能，**强烈推荐启用此插件**。它是 Epic 官方提供的、解决 Android 后台下载痛点的方案，集成度高且持续维护。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/Android/AndroidFetchBackgroundDownload)
- [官方文档](https://docs.unrealengine.com) (搜索 “Background HTTP”)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/Android/AndroidFetchBackgroundDownload/Tests)