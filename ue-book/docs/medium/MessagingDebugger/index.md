# Messaging Debugger

> Provides a visual debugger for the messaging sub-system.

| 属性 | 值 |
|---|---|
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MessagingDebugger` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Messaging/MessagingDebugger) | |

## 用途

Messaging Debugger 是 UE5 消息总线（Message Bus）系统的可视化调试工具。它提供了一个编辑器内的 DockTab 面板，让你可以像使用 IDE 调试器一样调试消息系统：查看消息历史、检查端点、设置断点、单步执行消息分发。

这个插件解决的核心问题是：消息系统是异步解耦的，传统的断点调试无法追踪"谁发了什么消息、谁收到了、什么时候处理的"。Messaging Debugger 通过 `IMessageTracer` 接口拦截并记录所有消息流，提供完整的可视化追踪。

## 使用场景

- 你在开发分布式编辑器工具（如 Unreal Insights、Session Frontend），消息收发行为不符合预期 → 用 Messaging Debugger 查看消息流向
- 你需要排查某个 Endpoint 是否正确注册、消息是否被投递到预期的接收者 → 查看 Endpoints 面板和 Message Details
- 你需要在多节点环境下（如 PIE 多实例）验证消息是否正确路由 → 每个 Message Bus 实例会生成独立的调试标签页
- 你想了解某个消息类型的订阅者数量和分发状态 → 查看 Types 面板和 Dispatch State 表格

## 蓝图用法

本插件不暴露 BlueprintCallable 接口。它是一个纯编辑器工具，通过 **Window → Developer Tools → Messaging Debugger** 菜单打开。

## C++ 用法

本插件不提供公共 C++ API。所有类均位于 `Private/` 目录下，属于 Editor-only 工具。如果需要在代码中与消息追踪系统交互，应直接使用 `Messaging` 模块的 `IMessageTracer` 接口。

### 头文件引入

本插件无需引入头文件——它是一个自包含的编辑器调试工具。

如需通过代码访问消息追踪器：

```cpp
#include "IMessagingModule.h"
#include "IMessageBus.h"
#include "IMessageTracer.h"
```

### 通过代码访问 Tracer

```cpp
// 获取所有已注册的消息总线
TArray<TSharedRef<IMessageBus, ESPMode::ThreadSafe>> AllBuses = IMessagingModule::Get().GetAllBuses();

for (const auto& Bus : AllBuses)
{
    // 获取该 Bus 的 Tracer
    TSharedRef<IMessageTracer, ESPMode::ThreadSafe> Tracer = Bus->GetTracer();
    
    // Tracer 记录了所有经过该 Bus 的消息
    // Messaging Debugger 的所有 UI 面板都基于 Tracer 的数据构建
}
```

## 架构概览

插件采用 MVVM 架构，主要组件如下：

### 核心类

| 类 | 文件 | 职责 |
|---|---|---|
| `FMessagingDebuggerModule` | `MessagingDebuggerModule.cpp` | 模块入口，注册 NomadTabSpawner，管理 Bus 生命周期 |
| `FMessagingDebuggerModel` | `MessagingDebuggerModel.h` | 视图模型，管理选中状态和可见性过滤 |
| `FMessagingDebuggerCommands` | `MessagingDebuggerCommands.h` | UI 命令定义（Break/Continue/Step/Stop 等） |
| `SMessagingDebugger` | `SMessagingDebugger.h` | 主窗口 Widget，承载所有子面板 |

### UI 面板

| 面板 | 类 | 功能 |
|---|---|---|
| **Endpoints** | `SMessagingEndpoints` | 显示所有已注册的消息端点列表 |
| **Endpoint Details** | `SMessagingEndpointDetails` | 选中端点的详细信息（地址、收发消息数） |
| **History** | `SMessagingHistory` | 消息历史列表，支持实时滚动和过滤 |
| **Message Details** | `SMessagingMessageDetails` | 选中消息的详细信息（时间戳、过期时间、发送线程、分发状态） |
| **Message Data** | `SMessagingMessageData` | 消息内容的结构化查看（编辑器下用 DetailsView，非编辑器用文本框） |
| **Types** | `SMessagingTypes` | 消息类型汇总，显示各类型的出现次数 |
| **Breakpoints** | `SMessagingBreakpoints` | 消息断点管理面板 |
| **Interceptors** | `SMessagingInterceptors` | 已注册的消息拦截器列表 |
| **Graph** | `SMessagingGraph` | 消息交互图（预留，当前未实现） |
| **Toolbar** | `SMessagingDebuggerToolbar` | 调试控制工具栏（Start/Stop/Break/Continue/Step） |

### 调试命令与快捷键

| 命令 | 快捷键 | 说明 |
|---|---|---|
| Break | `Alt+Pause` | 在下一条消息处中断 |
| Continue | `F5` | 继续执行 |
| Step | `F10` | 单步执行当前消息 |
| Stop | `Shift+F5` | 停止调试器 |
| Clear History | — | 清空消息历史 |
| Start | — | 启动调试器 |

### 过滤系统

插件提供三种过滤器，均基于 `FMessagingDebuggerModel` 的可见性状态：

- **`FMessagingDebuggerEndpointFilter`**：按端点过滤消息
- **`FMessagingDebuggerMessageFilter`**：按消息属性过滤
- **`FMessagingDebuggerTypeFilter`**：按消息类型过滤

过滤器通过 `SetEndpointVisibility()` / `SetTypeVisibility()` 控制，触发 `OnMessageVisibilityChanged` 事件通知 UI 刷新。

### Tab 管理

模块为每个已注册的 `IMessageBus` 创建独立的文档标签页。当新的 Bus 启动时自动创建标签页，Bus 关闭时自动移除。这在 PIE 多实例场景下尤其有用——每个世界实例通常有自己的消息总线。

## Demo 示例

本插件不提供可编程 API，无法通过代码创建 Demo。使用方式：

1. 在编辑器中启用插件：**Edit → Plugins → Messaging Debugger** → 启用并重启
2. 打开调试面板：**Window → Developer Tools → Messaging Debugger**
3. 在工具栏点击 **Start** 开始捕获消息
4. 在 History 面板中浏览消息流，点击某条消息查看详情
5. 在 Endpoints 面板中查看参与通信的端点
6. 使用 Break/Step/Continue 控制消息处理流程

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础功能 |
| `CoreUObject` | UObject 系统 |
| `InputCore` | 输入系统（快捷键绑定） |
| `Serialization` | 序列化支持 |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心 |
| `PropertyEditor` | 属性编辑器（仅编辑器构建，用于 Message Data 面板） |
| `WorkspaceMenuStructure` | 工作区菜单结构（仅编辑器构建，注册到 Developer Tools 分类） |

内部依赖（`PrivateIncludePathModuleNames`）：

| 模块 | 用途 |
|---|---|
| `Messaging` | 消息总线核心，提供 `IMessageTracer`、`IMessageBus` 等接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-03-13 | `b059f7b` | Fix trivial unreachable code warnings | 编译警告修复，无功能变更 |
| 2024-11-26 | `68ae0fe` | [Spatial Metrics Profiler] Refactor to support loading plugins properly | 重构 SpatialMetricsProfiler 的插件加载机制，MessagingDebugger 作为其依赖插件被涉及 |
| 2024-05-01 | `a2b5613` | Slate: Deprecate SListView::ItemHeight | Slate 框架 API 变更适配，无功能变更 |

### 维护评价

- **创建时间**：2014 年 3 月，与 UE4 同期，是最早的编辑器工具之一
- **最近更新频率**：过去 2 年有 3 次提交，全部是编译修复或框架适配，**无实质性功能更新**
- **维护状态**：**维护不活跃**——该插件已基本定型，Epic 没有投入新功能开发
- **Beta 标记**：`.uplugin` 中 `IsBetaVersion: true`，说明 Epic 从未将其标记为正式版
- **默认关闭**：`EnabledByDefault: false`，需要手动启用
- **推荐程度**：对于需要调试消息系统的开发者仍然有用，但应注意 Graph 面板（`SMessagingGraph`）中的 `SGraphEditor` 已被注释掉，说明该功能从未完成。插件整体稳定但功能有限

⚠️ 该插件标记为 Beta，且超过 10 年没有实质性功能更新。它作为底层调试工具仍然可用，但不要期待新功能或快速的 bug 修复。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Messaging/MessagingDebugger)
- [Messaging 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/Messaging)
