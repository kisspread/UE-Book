# ConcertInsightsClient

> Extends status bar so you can start a synchronized trace on all connected Concert endpoints.

| 属性 | 值 |
|---|---|
| 分类 | Networking |
| 默认启用 | true（但 Hidden=true，不在插件浏览器中显示） |
| 实验性 | IsExperimentalVersion = true |
| 包含内容 | true |
| 模块 | ConcertInsightsClient (Editor) |
| 创建时间 | 2024-05-06 |
| 年龄标签 | 🆕 (< 2 年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsClient) | |

## 用途

ConcertInsightsClient 是 Unreal Insights 分析工具与 Multi-User Editing (Concert) 系统的集成桥梁。它的核心功能是：**在 Multi-User 会话中，一键对所有连接的编辑器端点发起同步的 Unreal Insights Trace（性能追踪）**。

想象这个场景：你的团队有 5 台机器同时连接到一个 Multi-User 会话进行关卡编辑。你想分析所有端点的性能数据，但不想逐台机器去手动配置 Unreal Insights 的 Trace 设置。ConcertInsightsClient 就是为此而生——它在编辑器状态栏添加了一个 "Multi User" 按钮，通过这个按钮可以一键启动/停止所有端点的同步追踪。

### 为什么存在

Unreal Insights 的 Trace 功能原本是单机使用的，Multi-User Editing 也是独立的多人协作系统。这个 plugin 填补了两者之间的空白，让团队可以在 Multi-User 会话中方便地进行分布式性能分析。

## 使用场景

- **多人协作性能调试**：多人同时编辑时，需要从所有参与者的机器上收集性能数据来分析卡顿、延迟等问题
- **远程性能监控**：指定一个 Trace Store 的 IP 地址，让所有端点的 Trace 数据集中发送到同一个目标
- **分布式 Trace 录制**：在 Multi-User 会话中一键启动所有端点的 Trace 录制到本地文件

## 蓝图用法

此 plugin 没有暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。它是一个纯编辑器 UI 插件，所有功能通过编辑器状态栏的菜单操作。

## C++ 用法

此 plugin 的设计目标是零配置自动运行。作为 Editor 模块，它在引擎启动后自动在状态栏添加 Multi-User 控件。公共 API 非常精简，主要供其他模块检查模块状态。

### 头文件引入

```cpp
#include "IConcertInsightsClientModule.h"
```

### 基本用法

检查模块是否已加载（来源：`IConcertInsightsClientModule.h`）：

```cpp
// 检查模块是否可用
if (UE::ConcertInsightsClient::IConcertInsightsClientModule::IsAvailable())
{
    // 获取模块实例
    UE::ConcertInsightsClient::IConcertInsightsClientModule& Module =
        UE::ConcertInsightsClient::IConcertInsightsClientModule::Get();
}
```

### 设置类

Plugin 提供了一个设置类，用于配置同步 Trace 的目标地址（来源：`ConcertInsightsClientSettings.h`）：

```cpp
#include "ConcertInsightsClientSettings.h"

// 获取设置实例
UConcertInsightsClientSettings* Settings = UConcertInsightsClientSettings::Get();

// 修改 Trace 目标 IP（默认为 "localhost"）
Settings->SynchronizedTraceDestinationIP = TEXT("192.168.1.100");
Settings->SaveConfig();
```

设置存储在 `EditorPerProjectUserSettings` 配置文件中，每个项目独立保存。

## Demo 示例

此 plugin 不提供编程 API 示例——它是完全自动的 UI 扩展。以下是如何通过 UI 使用的步骤：

1. 插件默认启用且隐藏，无需手动激活（如需检查，可在 `DefaultEngine.ini` 中确认插件未被禁用）
2. 连接到 Multi-User 会话
3. 在编辑器底部状态栏找到 "Multi User" 按钮（左侧有绿色/灰色圆点指示连接状态）
4. 点击下拉箭头，展开菜单
5. 如需修改 Trace 目标 IP，在 "Destination IP" 输入框中填写（默认 `localhost`，支持 IPv4 地址格式如 `192.168.1.100`）
6. 点击 "Start synchronized trace" 开始同步追踪
7. 所有连接的端点将同时开始 Trace
8. 再次点击 "Stop synchronized trace" 停止

## 内部架构

### 状态栏扩展

Plugin 启动时（`PostEngineInit`）执行两个关键操作：

1. **添加 Multi-User 状态栏控件**（`ExtendEditorStatusBarWithMultiUserWidget`）：在 `LevelEditor.StatusBar.ToolBar` 菜单的最前面插入 `SMultiUserStatusBar` 组件
2. **注册 Insights 扩展菜单**（`ExtendMultiUserStatusBarWithInsights`）：向 `MultiUser.StatusBarMenu` 添加 "Tracing" 区段，包含启动/停止同步 Trace 的选项和 IP 配置控件

### Trace 控制流程

`FClientTraceControls` 继承自 `ConcertInsightsCore::FTraceControls`，负责：

- 监听 Multi-User 会话的启动/停止事件
- 将本地编辑器的 Trace 设置（目标类型、目标地址）转换为同步 Trace 参数
- 过滤端点列表，排除自身（避免向自己发送请求）
- 将当前会话的 Endpoint ID 和显示名称附加到 Trace 初始化参数中

### Trace 目标类型

根据编辑器的 Trace 设置，支持两种目标：
- **TraceStore (Network)**：通过网络发送到 Trace Store 服务器，使用 `SynchronizedTraceDestinationIP` 配置的地址
- **File**：录制到本地文件

> **注意**：使用 Network 目标时，所有端点会使用同一个 IP 地址（即发起者设置的 IP）。如果各机器的 Trace Store 地址不同（例如使用 `localhost` 时），需要手动配置为实际的网络 IP。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础功能（公共依赖） |
| `ConcertInsightsCore` | Concert Insights 核心功能，提供 FTraceControls 基类和同步 Trace 协议 |
| `ConcertSharedSlate` | Concert 共享 UI 组件 |
| `ConcertSyncClient` | Multi-User 同步客户端，用于获取会话信息 |
| `CoreUObject` | UObject 系统（设置类支持） |
| `EditorTraceUtilities` | 编辑器 Trace 工具，获取当前 Trace 目标设置 |
| `Engine` | 引擎核心 |
| `Slate` / `SlateCore` | UI 框架 |
| `ToolMenus` | 菜单扩展系统 |

### Plugin 依赖

| Plugin | 用途 |
|---|---|
| `ConcertInsightsCore` | 提供同步 Trace 的协议和基础设施 |
| `ConcertSharedSlate` | Concert UI 共享组件 |
| `ConcertSyncClient` | Multi-User 客户端功能 |
| `TraceUtilities` | Unreal Insights Trace 工具 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-03-06 | `742b5d3a` | 移除 void 返回函数中不恰当的 `UE_LIFETIMEBOUND` 使用 — 代码质量修复，不影响功能 |
| 2024-05-13 | `ee845008` | 修复重复的本地化 key — 修复国际化 bug |
| 2024-05-09 | `490e7aae` | 修复在 Slate 未初始化时（如运行 Commandlet）添加状态栏控件导致的崩溃 — 关键 bug 修复，解决了 Build Engine Localization 构建农场的阻断问题 |

### 维护评价

- **年龄**：约 2 年（2024-05 创建），属于 🆕 较新 plugin
- **更新频率**：低频维护，最近一次更新在 2025-03，距今约 1 年
- **状态**：稳定维护中，代码改动主要是 bug 修复和代码质量改进
- **实验性**：`.uplugin` 中 `IsExperimentalVersion = true`，`Hidden = true`，表明 Epic 仍在实验阶段
- **已知限制**：
  - 使用 Network 目标时，所有端点使用同一个 Trace Store IP，跨机器场景下 `localhost` 不适用
  - 代码中有 `TODO DP` 注释表明此问题已被注意到但未解决
- **推荐程度**：如果你的团队使用 Multi-User Editing 并需要分布式性能分析，值得启用。但需注意它仍标记为实验性功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsClient)
- [ConcertInsightsCore](../ConcertInsightsCore/) — 同步 Trace 核心模块（本文档依赖的底层实现）
- [Concert（Multi-User Editing）](https://docs.unrealengine.com/5.0/en-US/multi-user-editing-in-unreal-engine/) — 官方 Multi-User 编辑文档
