# Texture Format Oodle

> Deprecated Oodle Texture plugin, now built into Engine

| 属性 | 值 |
|---|---|
| 中文名 | 纹理 Oodle 压缩插件 |
| 分类 | Compression |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | 无（纯内容插件） |
| 实验性 | 否 |
| 创建时间 | 2021-04-08 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/TextureFormatOodle) | |

## 用途

这个插件最初是为了将 Oodle 压缩库集成到虚幻引擎的纹理处理管线中，用于高性能的纹理压缩。然而，根据插件自身的描述和近年来的提交记录，此插件**已完全废弃**。其核心压缩功能现在已经**内置**到虚幻引擎的核心模块（如 `ImageWrapper`、`TextureCompressor`）中。这个插件文件目前仅作为一个**向后兼容的占位符**存在，以确保旧项目能正常加载。

## 使用场景

**在当前的虚幻引擎版本中，您不应该使用或依赖此插件。**

*   **如果您在旧项目（UE5 早期版本）中看到它被启用**：您可以安全地**禁用**它，因为引擎内置模块已经提供了相同的功能。
*   **如果您是新项目**：此插件默认处于禁用状态，您无需做任何操作。纹理压缩（包括 Oodle）将自动由引擎内部处理。

## 蓝图用法

由于此插件已废弃且不包含任何实际代码或资产，它**不提供任何蓝图节点**。

## C++ 用法

由于此插件已废弃且不包含任何实际代码或资产，它**不提供任何 C++ API**。

## Demo 示例

此插件已废弃，不包含任何可演示的功能或资产。

## 模块依赖

无（纯内容插件）。

## 维护状态

### 近期更新

此插件在近期仅有维护性更新，目的是确保其作为废弃占位符的兼容性，并逐步清理历史信息。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-13 | `a29d7b59` | TextureFormatOodle.uplugin: Json format fix. | 修复 .uplugin 文件的 JSON 格式问题。 |
| 2026-01-14 | `08303025` | TextureFormatOodle.uplugin remove DeprecatedEngineVersion for now | 暂时移除 .uplugin 中的 `DeprecatedEngineVersion` 字段。 |
| 2026-01-14 | `dca3b205` | TextureFormatOodle changes from a Plugin to a built-in Engine Module | 明确宣告此插件功能已转变为引擎内置模块。 |
| 2025-12-10 | `df259862` | Enable Oodle 2.9.15 in UE | 在引擎中启用 Oodle 2.9.15 版本（引擎内置功能更新）。 |
| 2025-12-09 | `3b584e03` | [Backout] - CL49085465 | 回退了编号为 CL49085465 的提交。 |

### 维护评价

*   **状态**：**已废弃 / 已内置**。
*   **分析**：此插件自创建以来，其核心功能（Oodle 纹理压缩）逐步并最终被完全整合到虚幻引擎的运行时核心中。从提交历史看，最后一次涉及插件功能本身的实质性提交可以追溯到较早时期。近期的提交仅限于清理和格式修复。
*   **推荐**：**强烈建议不要启用此插件**。它的存在仅为向后兼容。请直接使用虚幻引擎内置的纹理压缩功能，引擎会在需要时自动使用 Oodle。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/TextureFormatOodle)
*   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/)

**注意**：此插件没有提供官方文档链接，因为它已被官方标记为废弃并内置到引擎中。相关功能的文档应查阅虚幻引擎的通用纹理压缩或 `ImageWrapper` 模块文档。