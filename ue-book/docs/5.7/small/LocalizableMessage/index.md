# Localizable Message

> Utility for a text message that can be replicated. It supports parameter resolution for the client.

| 属性 | 值 |
|---|---|
| 中文名 | 本地化消息 |
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `LocalizableMessage` (Runtime), `LocalizableMessageBlueprint` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-11-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LocalizableMessage) | |

## 总体用途

**Localizable Message** 提供一种可复制的文本消息机制，支持将带参数的格式化文本从服务器传输到客户端，并在客户端进行本地化参数解析。它解决了联网游戏中需要动态构造并传输本地化文本（如角色名称、物品数量等参数化消息）时的难题，避免手动拼接字符串导致的本地化断裂和网络复制冗余。

## 模块列表

| 模块 | 一句话总结 | 文档 |
|---|---|---|
| `LocalizableMessage` (Runtime) | 核心模块：定义 `FLocalizableMessage` 数据结构及序列化、参数解析逻辑 | [查看详情](LocalizableMessage.md) |
| `LocalizableMessageBlueprint` (Runtime) | 蓝图扩展：提供蓝图节点用于构造、比较、复制本地化消息对象 | [查看详情](LocalizableMessageBlueprint.md) |

## 使用场景

- 服务器广播击杀公告，其中包含玩家昵称（需客户端本地化显示）
- HUD 显示带有动态数值（伤害、金币数量）的提示文本
- 多语言环境下，各类系统消息（任务完成、技能冷却）的参数化表述
- 需要将 `FText` 与格式化参数通过网络可靠传输的任何场景

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LocalizableMessage)
- [LocalizableMessage 模块文档](LocalizableMessage.md)
- [LocalizableMessageBlueprint 模块文档](LocalizableMessageBlueprint.md)