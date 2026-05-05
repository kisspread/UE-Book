# Remote Control API

> A suite of tools for controlling the Unreal Engine, both in Editor or at Runtime via a webserver. This allows users to control Unreal Engine remotely through HTTP or WebSockets requests. This functionality allows developers to control Unreal through 3rd party party applications and web services.

| 属性 | 值 |
|---|---|
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControl` (Runtime), `RemoteControlCommon` (Runtime), `RemoteControlLogic` (Runtime), `RemoteControlMultiUser` (Runtime), `RemoteControlProtocol` (Runtime), `RemoteControlProtocolWidgets` (Runtime), `RemoteControlUI` (Runtime), `WebRemoteControl` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-07 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl) | |

## 用途

Remote Control API 是一个功能强大的远程控制框架，其核心目的是**将 Unreal Engine 的内部状态和功能通过标准的网络协议（HTTP/WebSocket）暴露出来**。它解决的核心问题是：如何让外部应用程序（如自定义控制面板、Web 应用、自动化脚本、其他 DCC 工具）能够安全、高效地与运行中的 Unreal Engine 实例进行双向通信和控制。

它不仅仅是一个简单的 Web 服务器，而是一个完整的生态系统，包含了协议抽象、逻辑处理、多用户同步、编辑器 UI 和 Web 服务器实现。这使得开发者可以专注于构建控制逻辑，而无需从头搭建复杂的网络通信和状态同步基础设施。

## 使用场景

- **虚拟制片 (Virtual Production)**：在片场，灯光师、导演可以通过平板电脑上的自定义 Web 界面，实时调整场景中的灯光参数、摄像机位置或后期处理效果。
- **自动化测试与 CI/CD**：编写脚本通过 HTTP API 自动化测试游戏流程、验证资产加载或执行性能基准测试，集成到持续集成流水线中。
- **外部工具集成**：将 Unreal Engine 作为渲染或模拟后端，由外部的 CAD 软件、数据可视化工具或自研编辑器通过 WebSocket 发送指令并接收实时状态更新。
- **多用户协作与监控**：在同一个项目会话中，多个用户可以通过各自的远程客户端查看和控制引擎状态，适用于评审、调试或分布式协作场景。
- **自定义编辑器扩展**：在编辑器内构建复杂的自定义面板或工具，通过 Remote Control API 与引擎核心数据交互，实现深度定制化工作流。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `RemoteControl` | Runtime | **核心模块**，定义了远程控制暴露（Exposed Entities）的基础框架和管理器。 |
| `RemoteControlCommon` | Runtime | **公共模块**，包含所有模块共享的数据类型、枚举和接口定义。 |
| `RemoteControlLogic` | Runtime | **逻辑模块**，实现了远程控制的核心业务逻辑，如处理函数调用、属性访问和事件触发。 |
| `RemoteControlMultiUser` | Runtime | **多用户模块**，负责在多用户编辑（MUE）会话中同步远程控制的状态和操作。 |
| `RemoteControlProtocol` | Runtime | **协议抽象模块**，定义了通信协议的抽象接口，支持扩展不同的传输协议。 |
| `RemoteControlProtocolWidgets` | Runtime | **协议UI模块**，提供了用于在编辑器中配置和可视化不同协议（如 WebSocket）的控件。 |
| `RemoteControlUI` | Runtime | **编辑器UI模块**，实现了 Remote Control Panel 等编辑器内的用户界面。 |
| `WebRemoteControl` | Runtime | **Web服务器模块**，基于 HTTP 和 WebSocket 协议的具体实现，是外部访问的主要入口点。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl/Tests)