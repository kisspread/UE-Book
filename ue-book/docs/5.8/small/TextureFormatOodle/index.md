# Oodle Texture

> Deprecated Oodle Texture plugin, now built into Engine

| 属性 | 值 |
|---|---|
| 中文名 | 纹理压缩Oodle |
| 分类 | Compression |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | 无（纯内容插件） |
| 实验性 | 否 |
| 创建时间 | 2021-04-08 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/TextureFormatOodle) | |

## 用途

该插件最初用于为 Unreal Engine 引入 Oodle 纹理压缩支持，这是一个高性能的第三方纹理压缩算法。根据其元数据和最近的 Git 历史记录，该插件的功能已**完全内置**到 Unreal Engine 的核心模块中。此插件目录的存在主要是为了向后兼容性或历史记录，当前版本的 `TextureFormatOodle.uplugin` 本身不包含任何可执行代码或模块，是一个“空壳”插件。开发者无需关心或使用此插件，纹理压缩功能（包括 Oodle）现在由引擎原生提供。

## 使用场景

由于此插件已被弃用且功能内置，**不推荐在任何新项目或新场景中主动使用此插件**。
- 如果你在一个非常旧的 UE5 项目中看到对 `TextureFormatOodle` 的引用，并且在升级后遇到问题，可以检查项目插件列表并**手动禁用**此插件。
- 你更应该在引擎的 **Project Settings -> Platforms -> Android/iOS/Windows** 等平台的纹理压缩设置中，直接选择使用 **Oodle** 作为纹理压缩格式。

## 蓝图用法

此插件不包含任何模块，因此没有提供任何蓝图节点、函数或资产。

### 核心节点

无。

### 使用示例（蓝图描述）

不适用。

## C++ 用法

此插件不包含任何模块，因此没有可供 C++ 代码引用的头文件或 API。

### 头文件引入

不适用。

### 基本用法

不适用。

### 进阶用法

不适用。

## Demo 示例

不适用。此插件不包含任何代码示例。

## 模块依赖

此插件不包含任何模块，因此没有依赖关系。纹理压缩（包括 Oodle）的功能已由引擎核心模块（如 `ImageWrapper` 等）提供。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-13 | `a29d7b59` | TextureFormatOodle.uplugin: Json format fix. | 修复 `.uplugin` 文件的 JSON 格式。 |
| 2026-01-14 | `08303025` | TextureFormatOodle.uplugin remove DeprecatedEngineVersion for now | 移除了 `DeprecatedEngineVersion` 字段。 |
| 2026-01-14 | `dca3b205` | TextureFormatOodle changes from a Plugin to a built-in Engine Module | **关键变更**：将功能从插件形式转换为内置引擎模块。 |
| 2025-12-10 | `df259862` | Enable Oodle 2.9.15 in UE | 更新启用的 Oodle 库至 2.9.15 版本。 |
| 2025-12-09 | `3b584e03` | [Backout] - CL49085465 | 回退了某个更改列表。 |

### 维护评价

**不活跃维护 / 已废弃**

1.  **创建与转型**：插件创建于 2021 年。根据 2026 年 1 月的关键提交 `dca3b205`，其功能已正式内置到引擎中。
2.  **当前状态**：插件目录下的 `.uplugin` 文件仅剩“外壳”，`Modules` 数组为空，`Installed` 为 `false`。其存在的意义仅为历史兼容或作为引擎内部迁移的标记。
3.  **更新内容**：近期提交仅为配置文件格式的维护性修改，无实质性功能更新。
4.  **结论与建议**：**此插件已正式废弃**。开发者不应在新项目中启用它。所有 Oodle 纹理压缩相关的功能应通过引擎内置设置使用。此文档旨在说明其历史背景和当前状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/TextureFormatOodle)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/texture-compression-and-cooking-in-unreal-engine/)（关于纹理压缩的通用文档，其中包含 Oodle）