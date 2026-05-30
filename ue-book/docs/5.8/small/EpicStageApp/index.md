# Epic Stage App

> Enables remote connections from the Epic Stage App（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 舞台应用连接 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容类型待确认） |
| 模块 | `EpicStageApp` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-06-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/EpicStageApp) | |

## 用途

该插件为 Unreal Engine 提供了一个通过 WebSocket 与 Epic Stage App（一个移动端虚拟制片应用）进行通信的后端服务。其核心功能是支持从移动设备远程控制 nDisplay 渲染集群，并实时预览渲染结果。它允许用户在移动应用上操控虚拟场景中的灯光、演员位置等元素，并将操作实时反馈到引擎端的 nDisplay 预览渲染中。

简单来说，它解决了在虚拟制片现场，导演或灯光师通过 iPad 等移动设备远程、直观地操控 LED 墙上显示内容的需求。

## 使用场景

- 你在使用 nDisplay 进行虚拟制片拍摄，需要让现场导演通过 iPad 实时调整虚拟场景中的灯光或演员位置。
- 你需要一个移动界面来远程创建、移动或复制场景中的光卡（Light Card）等对象，并希望这些操作能即时反映在 LED 墙的渲染画面上。
- 你在开发一个自定义的虚拟制片控制面板应用，需要一个标准的 WebSocket API 与 Unreal Engine 交互。

## 蓝图用法

该插件主要通过其公开的函数库和设置类与蓝图交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get API Version` | 获取当前 Epic Stage App API 的语义化版本字符串。 | `UStageAppFunctionLibrary` |
| `Get Remote Control Web Interface Port` | 获取用于访问此引擎实例远程控制 Web 接口的端口号。 | `UStageAppFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **查询API版本**：创建一个简单的UI，使用 `Get API Version` 节点获取版本号并显示在文本上，用于诊断或显示。
2.  **获取连接端口**：在应用启动时，使用 `Get Remote Control Web Interface Port` 节点获取端口号，并将其展示给用户或用于自动连接移动应用。
3.  **配置发现设置**：在项目设置（Project Settings -> Plugins -> Epic Stage App）中，可以配置 `Discovery Endpoint` 和 `Discovery Port`，用于局域网内的应用自动发现。

## C++ 用法

该插件的主要功能通过 WebSocket 路由处理，在 C++ 中直接调用的机会较少。其公开 API 集中在 `UStageAppFunctionLibrary` 中。

### 头文件引入

```cpp
#include "StageAppLibrary.h"
```

### 基本用法

```cpp
// 获取 Epic Stage App 的 API 版本
FString APIVersion = UStageAppFunctionLibrary::GetAPIVersion();
UE_LOG(LogTemp, Log, TEXT("Epic Stage App API Version: %s"), *APIVersion);

// 获取远程控制 Web 接口的端口号
int32 WebPort = UStageAppFunctionLibrary::GetRemoteControlWebInterfacePort();
UE_LOG(LogTemp, Log, TEXT("Remote Control Web Interface Port: %d"), WebPort);
```

### 进阶用法

该插件的核心逻辑位于私有类 `FStageAppRouteHandler` 中，它通过 `IWebRemoteControlModule` 注册了一系列 WebSocket 路由来处理来自移动应用的请求。这些路由包括：
- 创建/销毁 nDisplay 预览渲染器 (`PreviewRendererCreate`, `PreviewRendererDestroy`)
- 配置渲染器设置 (`PreviewRendererConfigure`)
- 执行预览渲染 (`PreviewRender`)
- 操控舞台演员（开始/移动/结束拖拽，创建/复制演员） (`PreviewActorDragBegin`, `PreviewActorCreate`, `ActorsDuplicate`)

开发者通常不需要直接调用这些内部类，而是通过已有的 WebSocket 协议与插件交互。如果你需要扩展插件功能（例如添加新的消息类型），你需要修改 `FStageAppRouteHandler` 类。

## Demo 示例

一个可编译的最小示例，用于获取并打印 Epic Stage App 的 API 版本和连接端口。

**头文件 (StageAppDemo.h):**
```cpp
// StageAppDemo.h
#pragma once

#include "CoreMinimal.h"

class FStageAppDemo
{
public:
    static void PrintStageAppInfo();
};
```

**源文件 (StageAppDemo.cpp):**
```cpp
// StageAppDemo.cpp
#include "StageAppDemo.h"
#include "StageAppLibrary.h"

void FStageAppDemo::PrintStageAppInfo()
{
    // 调用插件公开的蓝图函数库
    FString Version = UStageAppFunctionLibrary::GetAPIVersion();
    int32 Port = UStageAppFunctionLibrary::GetRemoteControlWebInterfacePort();

    UE_LOG(LogTemp, Display, TEXT("=== Epic Stage App Info ==="));
    UE_LOG(LogTemp, Display, TEXT("API Version: %s"), *Version);
    UE_LOG(LogTemp, Display, TEXT("Web Interface Port: %d"), Port);
    UE_LOG(LogTemp, Display, TEXT("==========================="));
}
```

## 模块依赖

根据 `.uplugin` 文件中的 `Plugins` 字段，使用此插件需要以下其他插件处于启用状态：

| 模块 | 用途 |
|---|---|
| `RemoteControl` | 提供 WebSocket 远程控制框架和 API，是本插件通信的基础。 |
| `nDisplay` | 提供分布式渲染（LED 墙）和预览渲染的核心功能。 |
| `nDisplayModularFeatures` | nDisplay 的模块化功能扩展。 |
| `DiscoveryBeaconReceiver` | 提供局域网设备自动发现机制，使移动应用能找到引擎实例。 |

此外，插件的 `Build.cs` 文件可能还依赖 `ImageWrapper` 模块用于压缩预览图像（从源码推断）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了用于格式化函数的强类型枚举，以解决可能产生的无用输出问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移为 UE_LOGF。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 在修复错误的查找替换后，进行第二次尝试。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 撤销提交 CL51314860 的更改。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 将引擎初始化后的委托从 `OnPostEngineInit` 改为 `GetOnPostEngineInit()`，以修复注册缺失问题。 |

### 维护评价

该插件创建于 2022 年，属于虚拟制作领域的较新功能。从近期提交记录来看（最新到 2026 年 4 月），插件仍在积极维护中，近期的更新主要涉及代码健壮性修复（如枚举格式化、日志宏迁移、初始化时序修正），表明 Epic 内部仍在使用和迭代此功能。

**主要特点与限制：**
- **实验性**：插件标记为 `IsBetaVersion=true`，说明其 API 或功能可能在未来的引擎版本中发生变化。
- **强依赖**：严重依赖于 `RemoteControl` 和 `nDisplay` 插件，需要整个虚拟制作工作流的支持。
- **平台限制**：仅支持 Windows 和 Linux 平台（从 `PlatformAllowList` 得知）。

**推荐度**：如果你正在进行使用 nDisplay 的虚拟制片项目，并且需要从移动设备进行远程控制和预览，那么此插件是官方提供的核心解决方案，值得使用。但需注意其实验性状态，并关注后续版本的更新说明。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/EpicStageApp)
- [官方文档]() (暂无)
- [测试用例]() (插件目录内未发现标准测试文件)