# Serialization Utils

> Utilities for serialization (xml, json, etc) with extended functionality.

| 属性 | 值 |
|---|---|
| 中文名 | 序列化工具 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `JsonSerialization` (Runtime), `XmlSerialization` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SerializationUtils) | |

## 总体用途

Serialization Utils 是一个实验性插件，提供增强的 JSON 和 XML 序列化功能。不同于引擎内置的序列化方案，它封装了更灵活的数据读写接口，支持扩展属性、注释、自定义节点类型等高级特性，适用于需要在游戏或工具中精细化处理 JSON/XML 数据的场景。

## 模块列表

| 模块 | 一句话总结 | 详细文档 |
|---|---|---|
| `JsonSerialization` (Runtime) | 提供 JSON 文件的读写、查询、修改功能，支持 JSON 对象/数组等标准操作，以及非标准扩展（如注释、多文档）。 | [JsonSerialization.md](JsonSerialization.md) |
| `XmlSerialization` (Runtime) | 提供 XML 文档的解析、生成、遍历功能，支持节点属性、CDATA、命名空间等标准 XML 特性，并允许通过回调自定义处理逻辑。 | [XmlSerialization.md](XmlSerialization.md) |

## 使用场景

- 你需要读写带注释的自定义 JSON 配置文件（引擎默认 `FJsonObject` 无法保留注释）。
- 你需要解析或生成结构复杂的 XML 数据，例如 SVG 路径、游戏关卡元数据。
- 你正在开发需要序列化/反序列化非标准数据格式的工具或管线（如本地化文件、预制体定义）。
- 你希望在 C++ 中同时处理 JSON 和 XML 并复用相同的访问模式（插件提供了统一的数据模型抽象）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SerializationUtils)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/json-and-xml-serialization-in-unreal-engine)（无专用文档，可参考通用序列化指南）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SerializationUtils/Source)（单元测试内嵌于各模块源码中）