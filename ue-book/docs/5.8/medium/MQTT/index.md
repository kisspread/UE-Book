# MQTT

> MQTT broker and client

| 属性 | 值 |
|---|---|
| 中文名 | MQTT 协议 |
| 分类 | IOT |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MQTTCore` (Runtime), `MQTTCoreEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-08 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT) | |

## 用途

MQTT 插件为 Unreal Engine 提供完整的 MQTT 协议支持，包含 Broker（消息代理）和 Client（客户端）两套实现。MQTT 是物联网（IoT）领域最常用的消息传输协议，采用发布/订阅模式，具有轻量、低带宽开销的特点。

该插件解决了 UE5 项目中与 IoT 设备、外部传感器或其他 MQTT 服务通信的需求，适用于需要与智能家居、工业控制系统、实时数据采集系统等场景对接的项目。

## 使用场景

- 你在做一个智能家居展示应用，需要读取传感器数据 → 用 MQTT 订阅传感器 Topic
- 你需要控制外部 IoT 设备（灯光、电机等）→ 用 MQTT Client 发布控制指令
- 你在做一个工业数字孪生项目，需要接收 PLC 数据 → 用 MQTT 连接工业网关
- 你想在 UE 内部搭建一个消息中转服务 → 用内置的 MQTT Broker

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [MQTTCore](MQTTCore.md) | Runtime | 核心运行时模块，提供 MQTT Broker 和 Client 实现、消息收发、连接管理 |
| [MQTTCoreEditor](MQTTCoreEditor.md) | Editor | 编辑器扩展模块，提供 MQTT 相关的编辑器工具和资产类型支持 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT)
- [MQTTCore 模块文档](MQTTCore.md)
- [MQTTCoreEditor 模块文档](MQTTCoreEditor.md)