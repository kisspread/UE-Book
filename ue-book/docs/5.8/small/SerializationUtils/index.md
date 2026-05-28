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
| 创建时间 | 2024-01-29 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SerializationUtils) | |

## 用途

提供 JSON 和 XML 序列化的扩展工具集。UE5 内置的 JSON/XML 序列化功能相对基础，此插件在此基础上提供更丰富的功能支持，包括更高效的内存管理（减少字符串拷贝）、FJsonObject 与 FString/UE::FSharedString 的双模式支持等，适用于需要高性能序列化的场景。

## 模块一览

| 模块 | 类型 | 说明 |
|---|---|---|
| **JsonSerialization** | Runtime | JSON 序列化与反序列化工具，支持高效的内存管理 |
| **XmlSerialization** | Runtime | XML 序列化与反序列化工具 |

详见各子模块文档：[JsonSerialization](JsonSerialization.md) · [XmlSerialization](XmlSerialization.md)

## 使用场景

- 你需要将游戏配置导出为 JSON 或 XML 格式 → 用此插件替代基础的 JsonUtilities
- 你有大量序列化数据需要处理，关注内存和性能 → 利用 FJsonObject 的优化（减少字符串拷贝）
- 你需要统一的序列化接口同时支持 JSON 和 XML 两种格式
- 你在做存档系统，需要序列化复杂对象到标准格式文件

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 支持 FString 和 FSharedString |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 字符串拷贝以释放内存 |
| 2026-02-25 | `ec13ba36` | [Backout] - CL51209244 | 回退之前的改动 |
| 2026-02-25 | `af0dfacf` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 字符串拷贝以释放内存 |

### 维护评价

该插件创建于 2024 年初，距今约 2 年。从近期提交记录看，2026 年初有多次活跃更新，集中在 **性能优化**（减少字符串拷贝）和 **代码重构**（支持 FSharedString），表明该插件仍处于积极开发中。更新频率约为每月 1-2 次，属于正常维护节奏。

⚠️ **注意**：此插件标记为 `IsExperimentalVersion = true` 且未默认安装，API 可能发生破坏性变更。建议仅在非生产环境或可接受 API 变动的项目中使用。

**推荐程度**：⭐⭐⭐（对性能有要求的序列化场景推荐尝试，但需做好 API 变更准备）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SerializationUtils)