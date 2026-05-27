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
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT) | |

## 用途

为 Unreal Engine 提供完整的 MQTT 协议支持，包含**客户端**与**Broker（消息代理）** 功能。MQTT 是物联网（IoT）领域最常用的轻量级消息传输协议，该插件让 UE5 能够直接与各类 IoT 设备、消息中间件进行双向通信，无需外部依赖。

**默认未启用且标记为实验性**，需在项目设置中手动启用，API 可能在未来版本中发生变化。

## 使用场景

- 你需要从 UE5 连接到外部 MQTT Broker（如 Mosquitto、AWS IoT Core）接收传感器数据 → 使用 MQTT 客户端订阅主题
- 你需要在 UE 内部搭建一个轻量 MQTT Broker，供多个客户端实例通信 → 使用 MQTT Broker 功能
- 你在做数字孪生或工业可视化项目，需要实时接收设备状态推送 → 用 MQTT 订阅主题并解析 JSON payload
- 你需要将 UE 场景中的事件发布到 IoT 平台 → 使用 MQTT 客户端发布消息

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`MQTTCore`](MQTTCore.md) | Runtime | 核心运行时模块，包含 MQTT 客户端/Broker 实现、连接管理、消息收发 API |
| [`MQTTCoreEditor`](MQTTCoreEditor.md) | Editor | 编辑器模块，提供编辑器内 MQTT 连接调试与配置支持 |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `JsonBlueprintUtilities` | JSON 数据的蓝图序列化/反序列化，用于 MQTT 消息 payload 处理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至 UE_LOGF 新接口 |
| 2026-01-30 | `52a87df5` | Fixed a crash that occurred when receiving MQTT packets with payloads =128 bytes due to incorrect va | 修复接收 128 字节 payload 时的崩溃问题 |
| 2025-06-11 | `afdf8d75` | Replace some usages of FORCEINLINE with inline in Online modules. | 将 FORCEINLINE 替换为 inline，代码规范化 |
| 2025-05-09 | `163c5cc4` | [MQTT] Removed platform restrictions | 移除平台限制，扩展可用平台范围 |
| 2025-02-13 | `ec3fb596` | Replaced `IsValid(this)` under the rest of Engine/. | 替换 IsValid(this) 调用，代码规范化 |

### 维护评价

- **实验性插件**：标记为 `IsExperimentalVersion=true`，未默认启用，API 不保证稳定
- **活跃维护中**：最近一次更新距今不到一个月（2026-04），且近期有实质性 bug 修复（payload 崩溃问题）
- **平台限制已解除**：2025-05 移除了平台限制，说明插件正逐步走向成熟
- **存在已知风险**：实验性状态意味着未来版本可能调整 API 或移除该插件
- **推荐程度**：⭐⭐⭐ 适合原型开发和 IoT 项目评估，生产环境需谨慎评估稳定性

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT)
- [MQTTCore 模块文档](MQTTCore.md)
- [MQTTCoreEditor 模块文档](MQTTCoreEditor.md)