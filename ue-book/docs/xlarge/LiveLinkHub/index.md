# Live Link Hub

> LiveLink Hub allows streaming of animated data into Unreal Engine or UEFN

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkHub` (Runtime), `LiveLinkHubEditor` (Runtime), `LiveLinkHubMessaging` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLinkHub) | |

## 用途

LiveLinkHub 是 LiveLink 系统的中心枢纽（Hub），其核心功能是**在多个 Unreal Engine 实例或外部应用程序之间同步和分发动画数据流**。它解决的是分布式动画制作和实时数据共享的问题。通过 Hub，一个数据源（如动捕设备、DCC 软件）可以将数据同时发送给多个接收端（如多个 UE 编辑器、UEFN 实例），实现高效协同。

## 使用场景

- **多机协同动画制作**：在大型虚拟制片或动画项目中，一台机器负责驱动动捕数据，通过 Hub 将数据实时分发给负责不同镜头或角色的多个 UE 工作站。
- **实时动捕数据分发**：将单个动捕演员的表演数据，同时推送给多个用于预览、渲染或游戏逻辑的 UE 实例。
- **跨应用数据同步**：在 UE 与 UEFN（Unreal Editor for Fortnite）或其他支持 LiveLink 的外部应用（如 MotionBuilder）之间建立稳定的数据桥梁。
- **数据录制与回放**：Hub 可以作为数据中转站，方便对流动的 LiveLink 数据进行录制和后期回放。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `LiveLinkHub` | Runtime | 核心运行时模块，包含 Hub 的主体逻辑、数据路由、会话管理和客户端/服务器实现。 |
| `LiveLinkHubEditor` | Runtime | 编辑器集成模块，提供用于配置和监控 Hub 的编辑器 UI、资产和工具。 |
| `LiveLinkHubMessaging` | Runtime | 网络通信层模块，定义了 Hub 与客户端之间通信的专用消息协议和序列化格式。 |

## 蓝图用法

LiveLinkHub 的核心功能主要通过 C++ API 和编辑器界面提供，蓝图可直接调用的节点较少。主要的蓝图交互可能集中在通过 LiveLink 主题（Subject）系统间接使用由 Hub 分发的数据。详细的 API 请参考各子模块文档。

## C++ 用法

LiveLinkHub 的使用涉及启动 Hub 服务、连接客户端以及管理数据流。由于其复杂性，通常通过编辑器工具或配置文件进行设置，而非在游戏运行时代码中直接调用。详细的类结构和接口请参考各子模块文档。

## 模块依赖

LiveLinkHub 插件依赖于 LiveLink 核心系统以及网络通信模块。

| 模块 | 用途 |
|---|---|
| `LiveLink` | LiveLink 核心框架，提供主题、源、角色等基础概念。 |
| `LiveLinkInterface` | LiveLink 的公共接口定义。 |
| `Networking` | 底层网络通信支持。 |
| `Sockets` | 网络套接字支持。 |

## 维护状态

### 近期更新

（待补充：需从 git log 获取最近 3 次 commit）

### 维护评价

该插件创建于 2024 年初，相对年轻。其状态标记为 **Beta 版本** 且 **默认未启用**，表明它仍处于积极开发和测试阶段，功能和 API 可能发生变化。作为 Epic 官方维护的 LiveLink 生态关键组件，预计会持续更新。目前适合用于实验性项目或需要前沿功能的场景，但在生产环境中使用需注意其 Beta 状态可能带来的稳定性风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLinkHub)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLinkHub/Tests)