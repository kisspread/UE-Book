# QUIC Messaging

> Adds a QUIC based transport layer to the messaging sub-system for sending and receiving messages between networked computers and devices.

| 属性 | 值 |
|---|---|
| 中文名 | QUIC 消息传输 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `QuicMessaging` (Runtime), `QuicMessagingTransport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-10-11 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/QuicMessaging) | |

## 总体用途

该插件为 UE 内置的消息传递子系统（Messaging Subsystem）添加了基于 **QUIC 协议** 的传输层实现。QUIC（Quick UDP Internet Connections）是一种基于 UDP 的多路复用、低延迟、自带加密的传输协议，适合需要快速建立连接、高吞吐量、多流的网络通信场景。通过此插件，用户可以利用 QUIC 的特性在游戏、编辑器、服务器和外部设备之间发送/接收消息，替代传统的 TCP 或 UDP 传输方式。

## 模块列表

| 模块 | 说明 | 模块文档 |
|---|---|---|
| `QuicMessaging` (Runtime) | 核心模块，定义消息传输层接口、QUIC 会话管理、端点连接与消息路由。 | [QuicMessaging](QuicMessaging.md) |
| `QuicMessagingTransport` (Runtime) | QUIC 传输协议的具体实现，处理连接建立、数据发送/接收、流控制与加密。 | [QuicMessagingTransport](QuicMessagingTransport.md) |

## 使用场景

- **多用户实时协作**：如 LiveLinkHub、多用户编辑、共同审阅，需要低延迟、可靠的多流数据传输。
- **游戏网络通信**：构建自定义服务器/客户端消息通道，支持快速重连和弱网络优化。
- **工具与设备通信**：连接外部控制台、VR/AR 设备、或第三方应用，使用 QUIC 的 0-RTT 握手减少延迟。
- **高性能日志/监控**：将引擎运行时的状态、指标通过可靠且低开销的管道发送到外部分析系统。

## 维护状态

从近期的 Git 提交看（2023-10 创建，2025-09 仍有修复 warning 和 unreachable code 的提交），插件处于 **活跃维护** 状态。适合在实验性项目中试用，随着 UE 版本升级该插件有较高概率得到持续改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/QuicMessaging)
- [QuicMessaging 模块文档](QuicMessaging.md)
- [QuicMessagingTransport 模块文档](QuicMessagingTransport.md)