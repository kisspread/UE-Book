# Multi User Server

> Visualizes the multi-user server

| 属性 | 值 |
|---|---|
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MultiUserServer` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-28 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserServer) | |

## 用途

Multi User Server 是 Concert 多用户协作系统的**独立服务器可视化程序**。它不是编辑器插件，而是为 `UnrealMultiUserSlateServer` 这个独立可执行程序提供完整的 Slate UI 界面。

该插件解决的核心问题是：多用户协作服务器需要一个可视化的管理界面，让运维人员或开发者能够：
- 监控已连接的客户端节点及其状态
- 查看各节点的发送窗口大小（反映网络性能）
- 浏览服务器活动日志和事务记录
- 管理服务器配置（如日志开关）
- 直观地观察多人协作的实时状态

没有这个插件，多用户服务器只能以无头模式运行，缺乏可视化监控能力。

## 使用场景

- 你在团队中使用 UE5 多用户编辑功能，需要一个独立的服务器程序来协调多个编辑器实例之间的同步 → 使用 UnrealMultiUserSlateServer（由本插件提供 UI）
- 你需要监控多人协作服务器的运行状态、查看连接的客户端列表和网络性能指标 → 启动 Multi User Slate Server
- 你需要在不打开编辑器的情况下运行多用户协作服务器 → 本插件为独立服务器程序提供界面

## 蓝图用法

本插件不提供蓝图接口。它是面向独立服务器程序的 Slate UI 模块，所有交互通过服务器窗口的原生 UI 完成。

## C++ 用法

### 头文件引入

```cpp
#include "IMultiUserServerModule.h"
```

### 基本用法

本插件的核心 API 仅一个接口方法，用于在服务器循环初始化前注册 Slate UI 的创建回调：

```cpp
// 获取模块实例
IMultiUserServerModule& MultiUserServerModule = IMultiUserServerModule::Get();

// 在服务器循环初始化前设置 Slate UI 回调
// InitArgs 包含服务器循环的初始化参数
FConcertSyncServerLoopInitArgs InitArgs;
MultiUserServerModule.InitSlateForServer(InitArgs);
```

### 检查模块可用性

```cpp
if (IMultiUserServerModule::IsAvailable())
{
    IMultiUserServerModule& Module = IMultiUserServerModule::Get();
    // 模块已加载，可以安全使用
}
```

### 进阶用法

本插件作为 `UnrealMultiUserSlateServer` 程序的 UI 层，通常不被外部代码直接调用。其内部通过 Concert 框架的回调机制，在服务器启动时自动创建 Slate 窗口并注册各类监控视图。自定义扩展通常需要：

1. 继承或修改服务器窗口的 Slate 布局
2. 通过 `ConcertSyncServer` 模块的 API 获取服务器状态数据
3. 使用 `ConcertSharedSlate` 中的共享 UI 组件构建自定义视图

## Demo 示例

本插件不适用于常规的 Actor/Component 示例。其使用方式是作为独立服务器程序的一部分被加载：

```cpp
// 服务器程序入口（简化示意）
#include "IMultiUserServerModule.h"
#include "ConcertSyncServerLoop.h"

// 服务器启动流程
void StartMultiUserServer()
{
    // 1. 检查模块是否可用
    if (!IMultiUserServerModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("MultiUserServer module not available"));
        return;
    }

    // 2. 初始化 Slate UI
    FConcertSyncServerLoopInitArgs InitArgs;
    IMultiUserServerModule::Get().InitSlateForServer(InitArgs);

    // 3. 启动服务器循环（Slate UI 将在循环中渲染）
    // FConcertSyncServerLoop::Run(InitArgs);
}
```

> **注意**：实际使用中，你只需编译并运行 `UnrealMultiUserSlateServer` 目标程序，本插件会自动加载并提供完整的服务器管理界面。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ConcertMain` | Concert 多用户协作核心框架 |
| `ConcertSharedSlate` | Concert 共享 Slate UI 组件库（客户端/服务器通用控件） |
| `ConcertSyncCore` | Concert 同步核心逻辑（事务、活动、资产同步） |
| `ConcertSyncServer` | Concert 服务器端同步实现 |

## 维护状态

### 近期更新

```
- d14749865d4f Multi User Slate Server: Fix crash when closing server while output log is docked.
  → 修复了服务器关闭时输出日志面板处于停靠状态导致的崩溃
- ce6ff392ddca Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue for FTSTicker::RemoveTicker usage.
  → 修复编译警告：FTSTicker::RemoveTicker 的 nodiscard 返回值处理
- b96876b1939a Add support for displaying the window size in our client UI view. This helps us see how big of a send window nodes have. The bigger the send window the better the performance of the nodes.
  → 新增客户端 UI 视图中的窗口大小显示，用于监控节点网络性能
```

### 维护评价

- **创建时间**：2022 年 3 月，约 3 年历史
- **维护状态**：**活跃维护中** — 近期有功能性更新（窗口大小监控）和稳定性修复（崩溃修复）
- **实验性标记**：`IsBetaVersion=true`，`EnabledByDefault=false`，`Hidden=true` — 仍处于 Beta 阶段
- **特殊限制**：仅在 `UnrealMultiUserSlateServer` 独立程序中可用，不适用于编辑器或游戏运行时
- **推荐程度**：如果你使用 UE5 多用户编辑功能并需要独立的可视化服务器管理界面，这是必需组件。但由于仍标记为 Beta，生产环境使用需注意稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserServer)
- [ConcertMain 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertMain)
- [ConcertSyncServer 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertSyncServer)
- [ConcertSharedSlate 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertSharedSlate)