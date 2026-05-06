# PCG Biome Core

> PCG Biome Creation Tool

| 属性 | 值 |
|---|---|
| 中文名 | PCG 生物群落核心 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PCGBiomeCore` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-15 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGBiomeCore) | |

## 用途

`PCGBiomeCore` 是 UE5 官方推出的实验性插件，旨在为基于 PCG（Procedural Content Generation）的**生物群落（Biome）创建**提供核心框架。它依赖于 `PCG` 和 `PCGGeometryScriptInterop`，通过 PCG 图和几何脚本的结合，实现地形上大规模、规则化的生态系统生成（例如树木、岩石、植被等在不同生物区域内的分布）。当前插件仅包含模块启动代码，尚未公开具体蓝图节点或 C++ 类，其实际功能主要通过内部实现和未来内容扩展提供。

## 使用场景

- 你需要在一个大型开放世界中创建 **多种生物群落**（如森林、沙漠、雪原），并希望使用 PCG 图来自动分布资源。
- 你希望在 PCG 流程中利用 **Geometry Script** 对生成的网格进行变形、合并或雕刻。
- 你正在开发一个实验性的地形生态生成工具，需要底层框架支持 **生物群落权重混合** 和 **规则化放置**。

## 蓝图用法

当前版本（0.2）未公开任何 `BlueprintCallable` 或 `BlueprintReadWrite` 属性/函数。插件核心功能可能以 PCG 节点、蓝图函数库或内容形式提供。请关注后续官方更新。

## C++ 用法

### 头文件引入

```cpp
#include "PCGBiomeCore.h"
```

### 基本用法

插件本身仅提供模块生命周期管理，无公开 API。要使用 PCG 生物群落功能，通常需要结合 PCG 图和 Geometry Script。以下示例展示如何在 C++ 中确保插件被加载：

```cpp
// 在模块 Startup 时加载 PCGBiomeCore 插件
IModuleInterface& PCGBiomeCoreModule = FModuleManager::LoadModuleChecked<FPCGBiomeCoreModule>("PCGBiomeCore");
```

## Demo 示例

因插件未开放具体功能类，无法提供可编译的最小示例。建议参考官方 `PCG` 和 `PCGGeometryScriptInterop` 插件的使用方式，并结合 PCG 图编辑器进行实验。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PCG` | 提供程序化生成图框架 |
| `PCGGeometryScriptInterop` | 提供 PCG 与 Geometry Script 互操作能力 |

## 维护状态

### 近期更新

- 2025-03-28 `8d218026` — PCG Biome Core V2 : updated uplugins version number to reflect biome core and sample major refactor
- 2024-01-15 `79749c91` — PCG Biome Core : adding PCG Biome Core plugin to Engine Experimental plugins

### 维护评价

插件创建于 2024 年 1 月，目前仅发布过版本号更新。无实质性功能提交，也无 bug 修复或文档补充。考虑到它是 **实验性插件**（`IsExperimentalVersion=true`），且最近一次提交仅为版本号变更，可以认为该插件：

- **目前未积极开发**：约 1.5 年内无功能迭代。
- **不推荐生产使用**：实验性、缺少文档和公开 API，未来可能被废弃或重构。
- **推荐用于学习或原型验证**：如果你希望探索 PCG + Biome 的概念，可以启用并尝试从源码中挖掘线索。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGBiomeCore)
- [官方文档](https://docs.unrealengine.com/)（搜索“PCG Biome Core”）