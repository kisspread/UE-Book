# nDisplay Launch

> Launch local nDisplay nodes with ease.

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay启动器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器UI资产） |
| 模块 | `DisplayClusterLaunchEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-04-07 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/DisplayClusterLaunch) | |

## 用途

这个插件是 nDisplay 多节点渲染系统的本地启动工具。它解决的核心问题是：在虚拟制片开发过程中，开发者需要在本地快速启动和管理多个 nDisplay 渲染节点，而无需依赖外部工具如 Switchboard。

插件提供了编辑器工具栏集成，让用户可以通过一个菜单直接选择 nDisplay 配置、指定要启动的节点、关联控制台变量资产，并一键启动所有节点进程。同时集成了 Multi-User (Concert) 会话支持，能在启动 nDisplay 节点时自动处理 Concert 服务器的查找和连接。

**注意**：此插件默认禁用且为 Beta 状态，需要在插件管理器中手动启用。

## 使用场景

- 你正在开发 LED Volume 或 CAVE 虚拟制片项目，需要在本地工作站上测试多节点 nDisplay 渲染 → 用此插件一键启动本地节点
- 你需要快速切换不同的 nDisplay 配置或节点组合进行调试 → 通过工具栏菜单选择配置和节点
- 你使用 Multi-User 编辑环境进行虚拟制片协作 → 启动时自动连接或创建 Concert 会话
- 你需要在 nDisplay 节点上应用特定的控制台变量或性能分析配置 → 在项目设置中配置预设和额外参数
- 你想启用 Unreal Insights 追踪来分析 nDisplay 渲染性能 → 在项目设置中配置 Insights 参数

## 蓝图用法

此插件不暴露 BlueprintCallable 函数，所有功能通过编辑器工具栏菜单和项目设置面板交互。

### 核心交互方式

| 交互 | 说明 |
|---|---|
| 工具栏按钮 | 点击后弹出 nDisplay 配置、节点和 Console Variables 选择菜单 |
| 项目设置 | 在 `项目设置 → nDisplay Launch Settings` 中配置启动参数 |

### 工具栏菜单功能

1. **选择 nDisplay 配置**：列出当前世界中所有 `ADisplayClusterRootActor`，可选择要启动的配置
2. **选择节点**：勾选要启动的渲染节点，主节点会特殊标记
3. **Console Variables 资产**：关联 `ConsoleVariablesAsset` 以应用预设变量
4. **选项菜单**：包含启动选项（如关闭编辑器、连接 Multi-User 等）

### 项目设置说明

| 设置项 | 说明 |
|---|---|
| Close Editor on Launch | 启动时关闭编辑器以优化性能 |
| Connect to Multi-User | 自动连接或创建 Concert 会话 |
| Unreal Insights | 启用性能追踪，支持 Stat Named Events |
| Console Variables Preset | 默认应用的控制台变量资产 |
| Additional Console Variables | 额外控制台变量（覆盖预设） |
| Additional Console Commands | 额外控制台命令 |
| Command Line Arguments | 附加命令行参数 |
| Logging | 日志文件名和日志级别配置 |

## C++ 用法

此插件主要作为编辑器工具使用，不提供面向外部模块的公共 API。但可通过模块单例调用核心功能。

### 头文件引入

```cpp
#include "DisplayClusterLaunchEditorModule.h"
```

### 基本用法

```cpp
// 获取模块实例并启动 nDisplay 进程
// 来源: DisplayClusterLaunchEditorModule.h
FDisplayClusterLaunchEditorModule& LaunchModule = FDisplayClusterLaunchEditorModule::Get();

// 启动 nDisplay 节点（会先进行完整性检查，然后异步获取 Concert 参数）
LaunchModule.TryLaunchDisplayClusterProcess();

// 终止所有活跃的 nDisplay 进程
LaunchModule.TerminateActiveDisplayClusterProcesses();

// 打开项目设置面板
FDisplayClusterLaunchEditorModule::OpenProjectSettings();
```

### 进阶用法

```cpp
// 获取模块引用后，可以通过项目设置类查看当前配置
// 来源: DisplayClusterLaunchEditorProjectSettings.h
const UDisplayClusterLaunchEditorProjectSettings* Settings = GetDefault<UDisplayClusterLaunchEditorProjectSettings>();

if (Settings)
{
    // 检查是否配置了 Multi-User 连接
    bool bUseMultiUser = Settings->bConnectToMultiUser;
    
    // 检查是否启动时关闭编辑器
    bool bCloseEditor = Settings->bCloseEditorOnLaunch;
    
    // 获取额外控制台变量
    const TSet<FString>& AdditionalCVars = Settings->AdditionalConsoleVariables;
    const TSet<FString>& AdditionalCmds = Settings->AdditionalConsoleCommands;
    
    // 获取日志配置
    const FString& LogFile = Settings->LogFileName;
    const TArray<FDisplayClusterLaunchLoggingConstruct>& LogConfig = Settings->Logging;
}
```

## Demo 示例

以下是一个自定义编辑器按钮触发 nDisplay 启动的最小示例：

```cpp
// MyNDisplayHelper.h
#pragma once

#include "CoreMinimal.h"

class FMyNDisplayHelper
{
public:
    /** 一键启动 nDisplay 并打印状态 */
    static void LaunchNDisplayWithStatus();
    
    /** 安全终止所有 nDisplay 进程 */
    static void SafelyTerminateAll();
};
```

```cpp
// MyNDisplayHelper.cpp
#include "MyNDisplayHelper.h"
#include "DisplayClusterLaunchEditorModule.h"
#include "DisplayClusterLaunchEditorLog.h"

void FMyNDisplayHelper::LaunchNDisplayWithStatus()
{
    UE_LOG(LogDisplayClusterLaunchEditor, Display, TEXT("正在启动 nDisplay 节点..."));
    
    FDisplayClusterLaunchEditorModule& Module = FDisplayClusterLaunchEditorModule::Get();
    
    // 启动会先验证配置有效性，再处理 Concert 参数，最后启动进程
    Module.TryLaunchDisplayClusterProcess();
    
    UE_LOG(LogDisplayClusterLaunchEditor, Display, TEXT("nDisplay 启动请求已发送"));
}

void FMyNDisplayHelper:: SafelyTerminateAll()
{
    UE_LOG(LogDisplayClusterLaunchEditor, Display, TEXT("正在终止所有 nDisplay 进程..."));
    
    FDisplayClusterLaunchEditorModule::Get().TerminateActiveDisplayClusterProcesses();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心功能，提供 `ADisplayClusterRootActor` 和配置数据 |
| `Concert` / `ConcertClient` | Multi-User 编辑支持，用于 Concert 会话管理和服务器发现 |
| `ConsoleVariablesEditorRuntime` | 控制台变量资产支持，用于关联 `ConsoleVariablesAsset` |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复打印格式化占位符错误 |
| 2025-10-09 | `1d4d3982` | Specify the SupportedPlatformTargets in the DisplayClusterLaunch plugin to prevent it from getting i | 明确指定支持的平台目标 |
| 2025-10-07 | `96352708` | Renaming Base<Plugin>.ini to Default<Plugin>.ini | 重命名配置文件命名规范 |
| 2025-09-03 | `65d9e8d9` | [nDisplay] Added few more CVars to the DisplayClusterLauncher launch command line | 新增更多控制台变量到启动命令行 |

### 维护评价

- **创建时间**：2022 年 4 月，作为 UE5 虚拟制片工具链的一部分
- **Beta 状态**：插件标记为 `IsBetaVersion=true`，且 `EnabledByDefault=false`，说明 Epic 认为该功能尚未完全稳定
- **更新频率**：近期（2025-2026）有持续维护，主要是工程性修复（日志迁移、格式化修复、平台声明规范化），功能性更新较少
- **源码规模**：仅 6 个文件，功能聚焦，维护负担轻
- **已知限制**：仅支持 Win64 和 Linux 平台；作为 Beta 产品，API 可能变动

**综合评价**：此插件仍在维护中但处于 Beta 阶段，适合虚拟制片团队在开发环境中使用。不建议在生产环境的关键流程中强依赖此插件的特定行为。如果你主要使用 Switchboard 进行 nDisplay 管理，此插件可作为本地快速测试的补充工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/DisplayClusterLaunch)
- 官方文档（暂无）