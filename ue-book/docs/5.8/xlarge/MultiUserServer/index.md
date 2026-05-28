# Multi User Server

> Visualizes the multi-user server

| 属性 | 值 |
|---|---|
| 中文名 | 多用户服务器可视化 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MultiUserServer` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-28 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserServer) | |

## 用途

Multi User Server 插件是 Unreal Multi-User Editing 框架的服务器端可视化组件。它并非提供多人编辑能力本身（那是 `ConcertSyncServer` 等插件的工作），而是为 `UnrealMultiUserSlateServer` 这个独立的服务器可执行程序提供了一个功能完整的 **Slate UI 界面**。其核心目的是让服务器管理员能够**监控、调试和管理**所有连接的客户端、实时会话活动、网络日志和资产包传输状态，解决了服务器端缺乏专用监控工具的问题。

## 使用场景

- 你部署了一个专用的多用户编辑服务器 (`UnrealMultiUserSlateServer.exe`)，需要一个图形界面来查看当前连接的用户列表、他们的网络状态和活动。
- 在多人协作过程中，遇到资产冲突、同步失败或网络延迟问题，需要通过服务器端的日志和包传输视图进行诊断。
- 需要管理会话的存档、恢复或删除，并希望查看与特定活动（如资产修改）相关的历史依赖关系。

## 蓝图用法

此插件主要为独立服务器程序提供 UI，其内部模块 `MultiUserServer` 类型为 `UncookedOnly`，且仅被 `UnrealMultiUserSlateServer` 程序允许加载。因此，它**不包含任何面向编辑器或运行时项目的公共蓝图 API**。其所有功能都通过服务器进程的 Slate 窗口来提供。

## C++ 用法

此插件主要设计为被服务器进程内部使用，对外暴露的接口非常有限。主要的交互点是模块初始化接口。

### 头文件引入

```cpp
#include "IMultiUserServerModule.h"
```

### 基本用法

在服务器进程的主循环初始化之前，通过 `IMultiUserServerModule` 接口注入 Slate UI 的创建逻辑。

**来源文件：** `Source/MultiUserServer/Public/IMultiUserServerModule.h`

```cpp
// 假设在服务器循环的初始化代码中
if (IMultiUserServerModule::IsAvailable())
{
    FConcertSyncServerLoopInitArgs InitArgs;
    // 配置初始化参数...
    
    // 调用插件接口，为其绑定创建 Slate UI 的回调
    IMultiUserServerModule::Get().InitSlateForServer(InitArgs);
}

// 之后，当服务器主循环开始运行时，注册的 UI 创建逻辑会被执行，弹出服务器管理窗口。
```

### 进阶用法：集成到自定义服务器

如果你需要将这个 UI 集成到自定义的服务器程序中，可以参考其模块实现类 `FConcertServerUIModule` 的结构。

**来源文件：** `Source/MultiUserServer/Private/MultiUserServerModule.h` 及相关 `.cpp`

```cpp
// 1. 创建 Slate 应用实例
TSharedRef<SlateApplication> SlateApp = MakeShareable(FSlateApplication::Create());
// 2. 初始化主窗口控制器，传入同步服务器实例
UE::MultiUserServer::FConcertServerWindowInitParams WindowInitParams(SyncServerInstance, LayoutIniPath);
TSharedRef<UE::MultiUserServer::FConcertServerWindowController> WindowController = MakeShared<UE::MultiUserServer::FConcertServerWindowController>(WindowInitParams);
// 3. 创建并显示主窗口
TSharedRef<SWindow> MainWindow = WindowController->CreateWindow();
FSlateApplication::Get().AddWindow(MainWindow);
// 4. 进入服务器主循环，持续处理网络和 Slate 事件
// ...
```

## Demo 示例

以下示例展示了如何在服务器进程中创建和显示 Multi User Server 的管理窗口。

```cpp
// MyServerApp.h
#pragma once
#include "CoreMinimal.h"
#include "ConcertServerWindowController.h"

class FMyServerApp
{
public:
    void Initialize(TSharedRef<IConcertSyncServer> InSyncServer);
    void Run();

private:
    TSharedPtr<UE::MultiUserServer::FConcertServerWindowController> WindowController;
};
```

```cpp
// MyServerApp.cpp
#include "MyServerApp.h"
#include "ConcertSyncServerLoopInitArgs.h"
#include "Framework/Application/SlateApplication.h"
#include "Window/ConcertServerWindowController.h"

void FMyServerApp::Initialize(TSharedRef<IConcertSyncServer> InSyncServer)
{
    // 初始化 Slate（如果服务器程序尚未初始化）
    if (!FSlateApplication::IsInitialized())
    {
        FSlateApplication::Create();
    }

    // 创建窗口控制器参数
    UE::MultiUserServer::FConcertServerWindowInitParams InitParams(InSyncServer, TEXT("MyServerLayout.ini"));
    
    // 创建控制器实例
    WindowController = MakeShared<UE::MultiUserServer::FConcertServerWindowController>(InitParams);
    
    // 生成主窗口
    TSharedRef<SWindow> MainWindow = WindowController->CreateWindow();
    
    // 将窗口添加到 Slate 应用
    FSlateApplication::Get().AddWindow(MainWindow, true);
}

void FMyServerApp::Run()
{
    // 进入服务器主循环，需要持续处理 Slate 和网络事件
    while (IsRunning())
    {
        // 处理网络消息
        // ProcessNetworkMessages();
        
        // 计入 Slate
        if (FSlateApplication::IsInitialized())
        {
            FSlateApplication::Get().PumpMessages();
            FSlateApplication::Get().Tick();
        }
        
        // 其他服务器逻辑...
    }
}
```

## 模块依赖

使用此插件时，你的服务器程序模块需要依赖以下核心 Concert 模块：

| 模块 | 用途 |
|---|---|
| `ConcertSyncCore` | 提供多用户同步的核心数据结构、网络协议和活动定义。 |
| `ConcertSyncServer` | 提供 `IConcertSyncServer` 接口，即同步服务器的核心实现。 |
| `ConcertMain` | 提供 Concert 框架的基础模块和主要类型。 |
| `ConcertSharedSlate` | 提供多个 Concert 插件共享的 Slate UI 工具和组件。 |

**注意**：此插件**不**适用于普通的 Unreal Editor 或游戏项目，它只服务于 `UnrealMultiUserSlateServer` 这一特定服务器程序。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 产生的编译警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正格式化字符串与参数位宽不匹配的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2025-09-30 | `a14f716b` | Multi User Slate Server: Fix crash when closing server while output log is docked. | 修复服务器关闭时，若输出日志窗口处于停靠状态会导致崩溃的问题。 |
| 2025-09-12 | `fd5c41be` | Addressing instances “ignoring return value of function declared with ‘nodiscard’ attribute” issue f | 解决忽略 `[[nodiscard]]` 函数返回值的问题。 |

### 维护评价

该插件处于**实验性（Beta）** 状态。虽然创建时间较早（2022年），但最近的更新（截至2026年）主要集中在**编译警告修复、格式化修正和特定崩溃修复**上，未见新功能的添加。它作为服务器端工具，功能相对独立和稳定。然而，鉴于其 `IsBetaVersion: true` 的状态以及较低的更新频率，**建议在生产环境中谨慎评估和使用**，并充分测试其在当前引擎版本下的稳定性。它主要适用于需要专用服务器监控界面的高级多人协作场景。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserServer)
- 官方文档：无
- 测试用例：未在插件目录内发现独立测试文件，其测试可能集成在 `ConcertSyncServer` 或 `ConcertSyncCore` 的测试中。