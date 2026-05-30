# Switchboard

> Launcher/Installer for the Switchboard application.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟制片调度器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Python 脚本、配置模板） |
| 模块 | `SwitchboardCommon` (Runtime), `SwitchboardEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Switchboard) | |

## 用途

Switchboard 是 Unreal Engine 虚拟制片（Virtual Production）工作流中的**集群管理与设备调度工具**。它解决的核心问题是：在 nDisplay 多机渲染、Live Link 多源输入、Media Profile 媒体管理等复杂场景下，如何统一管理和协调多个远程节点（PC、渲染集群）的进程启停、设备配置和同步录制。

此插件本身是 Switchboard Python 应用程序的**引擎端辅助组件**，主要负责：
- 在引擎侧提供与 Switchboard 交互的通用功能（连接通信、监听器管理）
- 在编辑器内嵌入 Switchboard 控制面板，实现编辑器内直接操作集群
- 管理 Switchboard Listener 的自启动（Autolaunch）配置，确保远程节点在系统启动后自动运行监听服务

与 nDisplay 插件（负责渲染配置）和 Live Link 插件（负责数据传输）不同，Switchboard 专注于**运维层面**——即"谁来启动这些服务、如何发现和管理远程节点、如何协调多台机器的工作"。

## 使用场景

- 你搭建了一个 nDisplay 多机渲染集群（如 LED Volume 拍摄） → 用 Switchboard 统一管理各渲染节点的启停和配置
- 你需要在虚拟制片场景中协调多个 Live Link 源和录制设备 → 用 Switchboard 集中调度
- 你希望远程节点开机后自动启动监听服务，无需人工干预 → 用 Switchboard Listener Autolaunch
- 你想在 UE 编辑器内直接管理 Switchboard 连接，而非切换到外部 Python 窗口 → 启用此插件

## 蓝图用法

此插件以编辑器工具和 Python 后端为主，不提供传统意义上的蓝图节点。其核心交互通过**编辑器内嵌面板**完成。

### 编辑器面板功能

| 功能 | 说明 | 模块 |
|---|---|---|
| Switchboard 面板 | 在编辑器内打开 Switchboard 控制界面，管理远程节点 | `SwitchboardEditor` |
| 设备管理 | 配置和监控 nDisplay 节点、Live Link 设备、媒体源 | `SwitchboardEditor` |
| 进程控制 | 通过编辑器面板启动/停止远程节点上的 Unreal 实例 | `SwitchboardEditor` |

### C++ API（SwitchboardCommon）

虽然此插件不以蓝图 API 为主，但 `SwitchboardCommon` 模块导出了一些 C++ 函数供引擎内部使用：

| 函数 | 说明 | 所在命名空间 |
|---|---|---|
| `GetInvocation` | 获取当前 Switchboard Listener 的自启动调用参数 | `UE::SwitchboardListener::Autolaunch` |
| `GetInvocationExecutable` | 获取自启动调用的可执行文件路径 | `UE::SwitchboardListener::Autolaunch` |
| `SetInvocation` | 设置 Switchboard Listener 的自启动调用参数 | `UE::SwitchboardListener::Autolaunch` |
| `RemoveInvocation` | 移除 Switchboard Listener 的自启动配置 | `UE::SwitchboardListener::Autolaunch` |

> 注意：以上 Autolaunch API 仅在定义了 `SWITCHBOARD_LISTENER_AUTOLAUNCH` 预处理宏时可用。

## C++ 用法

### 头文件引入

```cpp
#include "SwitchboardListenerAutolaunch.h"
```

### 基本用法

以下代码展示如何管理 Switchboard Listener 的自启动配置：

```cpp
// 来源: Engine/Plugins/VirtualProduction/Switchboard/Source/SwitchboardCommon/Public/SwitchboardListenerAutolaunch.h

#if SWITCHBOARD_LISTENER_AUTOLAUNCH

#include "SwitchboardListenerAutolaunch.h"

void ManageSwitchboardAutolaunch(FLogCategoryBase& LogCategory)
{
    namespace Autolaunch = UE::SwitchboardListener::Autolaunch;

    // 获取当前自启动配置
    FString CurrentInvocation = Autolaunch::GetInvocation(LogCategory);
    if (!CurrentInvocation.IsEmpty())
    {
        UE_LOG(LogTemp, Log, TEXT("Current autolaunch: %s"), *CurrentInvocation);
    }

    // 获取自启动可执行文件路径
    FString Executable = Autolaunch::GetInvocationExecutable(LogCategory);
    UE_LOG(LogTemp, Log, TEXT("Listener executable: %s"), *Executable);

    // 设置新的自启动调用参数
    FString NewInvocation = TEXT("path/to/switchboard_listener.exe --port 29880");
    bool bSuccess = Autolaunch::SetInvocation(NewInvocation, LogCategory);
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Autolaunch configured successfully"));
    }

    // 如需移除自启动配置
    // Autolaunch::RemoveInvocation(LogCategory);
}

#endif // SWITCHBOARD_LISTENER_AUTOLAUNCH
```

### 进阶用法

```cpp
#if SWITCHBOARD_LISTENER_AUTOLAUNCH

// 在引擎启动时检查并确保 Listener 自启动状态正确
void EnsureListenerAutolaunch()
{
    FLogCategoryBase& LogCategory = LogTemp;

    namespace Autolaunch = UE::SwitchboardListener::Autolaunch;

    // 查询当前状态
    FString ExistingInvocation = Autolaunch::GetInvocation(LogCategory);
    FString ExpectedExecutable = Autolaunch::GetInvocationExecutable(LogCategory);

    if (ExistingInvocation.IsEmpty())
    {
        // 首次配置：设置自启动
        UE_LOG(LogTemp, Log, TEXT("No autolaunch configured. Setting up..."));
        Autolaunch::SetInvocation(ExpectedExecutable, LogCategory);
    }
    else if (!ExistingInvocation.Contains(ExpectedExecutable))
    {
        // 路径变更：更新配置
        UE_LOG(LogTemp, Log, TEXT("Autolaunch path changed. Updating..."));
        Autolaunch::SetInvocation(ExpectedExecutable, LogCategory);
    }
}

#endif
```

## Demo 示例

此插件主要通过编辑器面板和 Python 后端运作，C++ 层面的使用场景集中在 Listener 自启动管理。以下为最小化使用示例：

### SwitchboardAutolaunchHelper.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "SwitchboardListenerAutolaunch.h"

// 自动启动管理辅助类
class FSwitchboardAutolaunchHelper
{
public:
    /** 检查并配置 Switchboard Listener 自启动 */
    static void EnsureAutolaunch();

    /** 移除自启动配置 */
    static void DisableAutolaunch();

private:
    static FLogCategoryBase& GetLogCategory();
};
```

### SwitchboardAutolaunchHelper.cpp

```cpp
#include "SwitchboardAutolaunchHelper.h"

#if SWITCHBOARD_LISTENER_AUTOLAUNCH

FLogCategoryBase& FSwitchboardAutolaunchHelper::GetLogCategory()
{
    return LogTemp;
}

void FSwitchboardAutolaunchHelper::EnsureAutolaunch()
{
    FLogCategoryBase& Log = GetLogCategory();
    namespace Autolaunch = UE::SwitchboardListener::Autolaunch;

    FString Executable = Autolaunch::GetInvocationExecutable(Log);
    FString Current = Autolaunch::GetInvocation(Log);

    if (Current.IsEmpty())
    {
        UE_LOG(LogTemp, Log, TEXT("Configuring Switchboard Listener autolaunch: %s"), *Executable);
        Autolaunch::SetInvocation(Executable, Log);
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("Switchboard Listener autolaunch already configured: %s"), *Current);
    }
}

void FSwitchboardAutolaunchHelper::DisableAutolaunch()
{
    FLogCategoryBase& Log = GetLogCategory();
    namespace Autolaunch = UE::SwitchboardListener::Autolaunch;

    Autolaunch::RemoveInvocation(Log);
    UE_LOG(LogTemp, Log, TEXT("Switchboard Listener autolaunch removed"));
}

#else

void FSwitchboardAutolaunchHelper::EnsureAutolaunch()
{
    UE_LOG(LogTemp, Warning, TEXT("SWITCHBOARD_LISTENER_AUTOLAUNCH not defined"));
}

void FSwitchboardAutolaunchHelper::DisableAutolaunch()
{
    UE_LOG(LogTemp, Warning, TEXT("SWITCHBOARD_LISTENER_AUTOLAUNCH not defined"));
}

#endif
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OpenSSL` | SSL/TLS 通信支持，用于 Switchboard 与远程节点间的加密通信 |
| `LaunchDaemonMessages` | 跨进程通信消息定义，用于引擎与外部 Switchboard 应用间的 IPC |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `75168502` | Switchboard - Fix unhandled PermissionError in Save Logs zip cleanup. | 修复保存日志 zip 清理时未处理的权限错误 |
| 2026-05-12 | `769529af` | Switchboard: Fix host vs remote platform handling for Linux nodes. | 修复 Linux 节点的本机与远程平台判断问题 |
| 2026-05-12 | `603cb935` | Allow users to specify which plugins are enabled for Live Link Hub on launch. | 允许用户指定 Live Link Hub 启动时启用的插件 |
| 2026-04-28 | `7c48f485` | Switchboard - add renamed MediaProfile module classname to MEDIAPROFILE_CLASS_NAMES so Media Profile | 将重命名的 MediaProfile 模块类名添加到 MEDIAPROFILE_CLASS_NAMES 以适配媒体配置文件 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏从 UE_LOG 到 UE_LOGF |

### 维护评价

- **活跃维护**：最近 1 个月内有多次实质性更新（2026-04 至 2026-05），涵盖 bug 修复、新功能添加和代码现代化
- **状态**：持续迭代中，团队在积极维护
- **实验性标记**：`.uplugin` 中 `IsBetaVersion=true` 且 `EnabledByDefault=false`，说明此插件仍处于 beta 阶段，API 和功能可能发生变化
- **版本**：0.1，进一步确认其 beta 状态
- **推荐程度**：如果你的虚拟制片工作流需要管理多机 nDisplay 集群，Switchboard 是官方推荐的方案。尽管仍标记为 beta，但 Epic 的 Virtual Production 团队持续投入维护。建议在生产环境中谨慎使用，关注版本更新带来的 breaking changes。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Switchboard)
- 官方文档（无外部文档链接，参考 .uplugin DocsURL 为空）
- 关联插件：[nDisplay](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/nDisplay)、[Live Link](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink)