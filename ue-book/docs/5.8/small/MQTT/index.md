# MQTT

> MQTT broker and client

| 属性 | 值 |
|---|---|
| 中文名 | 消息队列遥测传输 |
| 分类 | IOT |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MQTTCore` (Runtime), `MQTTCoreEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT) | |

## 用途

该插件为 Unreal Engine 5 提供了 **MQTT** 协议的集成支持。MQTT 是一种轻量级的发布/订阅消息传输协议，专为低带宽、高延迟或不稳定的网络环境设计，常用于物联网 (IoT) 设备与服务器之间的通信。此插件允许开发者在 UE5 项目中实现 MQTT 客户端或 broker 功能，用于连接外部 MQTT 服务（如 Mosquitto、HiveMQ）或设备，实现实时数据交换和设备控制。

## 使用场景

- **物联网应用开发**：在 UE5 中构建可视化 IoT 仪表盘或控制面板，连接并监控真实的传感器、执行器等设备。
- **分布式系统通信**：游戏或应用需要与后端服务、其他客户端实例或微服务进行松耦合、实时的消息传递。
- **实时数据流**：从 MQTT broker 订阅实时数据流（如股票行情、设备状态更新），并在游戏或应用 UI 中可视化。
- **跨网络设备控制**：通过公网上的 MQTT broker，远程控制位于不同网络环境下的 Unreal 应用或嵌入式设备。

## 模块列表

- **MQTTCore** (Runtime)
  核心运行时模块，负责 MQTT 协议的实现，包括连接管理、消息发布/订阅、数据包解析等。
- **MQTTCoreEditor** (Editor)
  编辑器集成模块，可能提供与 MQTT 相关的编辑器工具、资产类型或调试功能。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统宏更新，不影响功能。 |
| 2026-01-30 | `52a87df5` | Fixed a crash that occurred when receiving MQTT packets with payloads =128 bytes due to incorrect va | 修复了一个因载荷大小计算错误导致接收128字节MQTT数据包时崩溃的严重问题。 |
| 2025-06-11 | `afdf8d75` | Replace some usages of FORCEINLINE with inline in Online modules. | 将部分 `FORCEINLINE` 替换为 `inline`，属于代码规范化。 |
| 2025-05-09 | `163c5cc4` | [MQTT] Removed platform restrictions | 移除了MQTT插件的平台限制，使其可在更多平台上使用。 |
| 2025-02-13 | `ec3fb596` | Replaced `IsValid(this)` under the rest of Engine/. | 引擎范围内代码清理，替换对象有效性检查宏。 |

### 维护评价

- **活跃度**：插件自2022年创建以来持续有更新，最近一次实质性功能/修复更新在2026年1月，表明仍在维护中。
- **实验性警告**：插件被标记为 `IsExperimentalVersion=true` 且默认禁用，这意味着它可能尚未经过充分测试，API 不稳定，或未来可能发生重大变更。生产环境使用需谨慎评估风险。
- **推荐度**：如果你的项目有明确的 MQTT 协议集成需求，并且可以接受实验性插件的潜在风险，此插件是官方提供的一个基础选择。建议从子模块文档了解具体 API 用法。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT)
- [MQTTCore 模块文档](MQTTCore.md)
- [MQTTCoreEditor 模块文档](MQTTCoreEditor.md)