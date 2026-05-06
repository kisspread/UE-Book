# Json Blueprint Utilities

> Json functionality for Blueprint.

| 属性 | 值 |
|---|---|
| 中文名 | Json蓝图工具集 |
| 分类 | Blueprints |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图节点资产、类型定义） |
| 模块 | `JsonBlueprintUtilities` (Runtime), `JsonBlueprintGraph` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-21 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/JsonBlueprintUtilities) | |

## 总体用途

让蓝图直接读写、解析和生成 **Json 格式数据**，无需编写 C++ 代码。从源码看，它封装了 `JsonObject`、`JsonValue` 等原生类型，并提供蓝图可调用的静态函数和自定义 pin 类型，解决“蓝图无法直观操作 Json”的问题。

与常规 Json 库不同，此插件**专注于蓝图端**，使非程序员也能在关卡蓝图或角色蓝图中自由构建 Json 字符串。

## 使用场景

- **数据存档**：将游戏当前状态（玩家属性、世界变量）序列化为 Json 字符串并保存至文件。
- **Web API 集成**：拼接请求体、解析返回的 Json 数据。
- **配置文件**：读取外部 `.json` 配置文件，驱动游戏参数。
- **调试/测试**：在蓝图环境中快速验证 Json 数据格式。

## 模块列表

| 模块 | 类型 | 一句话总结 | 详细文档 |
|---|---|---|---|
| `JsonBlueprintUtilities` | Runtime | 核心运行时库，提供所有蓝图可调用的 Json 静态函数 | [JsonBlueprintUtilities.md](JsonBlueprintUtilities.md) |
| `JsonBlueprintGraph` | UncookedOnly | 编辑器模块，为蓝图节点提供类型化 Pin、自定义图形节点 | [JsonBlueprintGraph.md](JsonBlueprintGraph.md) |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/JsonBlueprintUtilities)
- [JsonBlueprintUtilities 模块文档](JsonBlueprintUtilities.md)
- [JsonBlueprintGraph 模块文档](JsonBlueprintGraph.md)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/JsonBlueprintUtilities/Tests)（在插件内部或 Engine/Tests 下）

## 文档入口

这是汇总文档，各模块的详细 API、使用示例和维护状态请参见对应子模块文档。

- **核心蓝图节点**：详见 [JsonBlueprintUtilities.md](JsonBlueprintUtilities.md)
- **编辑器自定义图形**：详见 [JsonBlueprintGraph.md](JsonBlueprintGraph.md)

---

> ⚠️ **实验性插件**：该插件在 `.uplugin` 中标记为 `IsBetaVersion=true`，默认不启用。需要在插件管理器手动开启后使用。API 可能在后续版本发生变更。