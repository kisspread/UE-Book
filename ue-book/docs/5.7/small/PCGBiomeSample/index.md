# PCG Biome Sample

> PCG Biome Sample Plugin

| 属性 | 值 |
|---|---|
| 中文名 | PCG 生物群落样本 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例内容、PCG 图表、预设资产） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-07 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGBiomeSample) | |

## 用途

**PCG Biome Sample** 是 Epic Games 为 PCG（程序化内容生成）系统提供的 **生物群落示例内容包**。它展示了如何利用 **PCG Biome Core** 框架实现不同生物群落的程序化生成逻辑，包括地形适配、植被分布、岩石摆放等常见环境构建任务。插件本身不包含 C++ 代码，而是通过蓝图资产（PCG 图表、材质、静态网格体等）提供可直接使用的示范，帮助开发者快速理解 PCG Biome 设计模式并复制到自己的项目中。

## 使用场景

- 你需要快速搭建程序化生成的自然环境（森林、草原、山地等）。
- 你正在学习 PCG Biome Core 框架，需要一个完整的参考实现。
- 你想在自己的项目中使用预定义的生物群落规则，减少重复设计工作量。

## 蓝图用法

此插件为纯内容插件，不包含任何可调用的蓝图函数或类。所有功能通过放置到关卡中的 PCG 图表或使用 PCG 组件来触发。使用方式：

1. 在项目设置中启用该插件（需要同时启用 `PCG` 和 `PCGBiomeCore`）。
2. 在内容浏览器中浏览 `Plugins/PCGBiomeSample/Content` 目录，找到可用的示例图表。
3. 将图表拖入关卡，或作为 PCG 组件附加到关卡 Actor 上运行。

## C++ 用法

无。此插件不提供任何 C++ 类、函数或模块，无需头文件引入。

## Demo 示例

由于没有 C++ 源码，最小示例为在蓝图中引用插件的资产：

1. 创建一个新关卡。
2. 添加一个 `PCGVolume` Actor。
3. 在 `PCGComponent` 中指定使用 `PCGBiomeSample` 内的某个图表（例如`BiomeForest`）。
4. 运行模拟，观察程序化生成结果。

## 模块依赖

**使用者**的模块（假设为 `MyModule`）如果需要引用此插件中的内容，必须在 `.Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `PCGBiomeCore` | 生物群落核心框架，提供基础类和解算器 |
| `PCG` | 程序化内容生成系统运行时库 |

> 注意：`PCGBiomeSample` 本身是内容插件，不产生模块依赖，但被依赖的两个插件必须启用。

## 维护状态

### 近期更新

- 2025-03-28 `8d218026` PCG Biome Core V2 : updated uplugins version number to reflect biome core and sample major refactor  
- 2024-06-27 `5e4a560d` PCG Biome Sample: added PCG plugin dependency to BiomeSample as well (was depending on BiomeCore bef  
- 2024-02-07 `7d78cbd1` PCG BiomeSample Plugin: Moved from Restricted/NotForLicensees to Experimental

### 维护评价

- **创建时间**：约 1 年前，属于较新的插件。
- **近期活动**：最后一次实质性更新在 2024-06（增加依赖），而 2025-03 仅为版本号变更，表明核心内容已稳定。
- **活跃度**：当前处于维护状态，但更新频率较低。
- **适用性**：推荐用于学习 PCG Biome 工作流和快速原型设计，但由于标记为实验性，不建议在正式产品中直接依赖，应考虑自行定制。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGBiomeSample)
- [官方文档（PCG 概述）](https://docs.unrealengine.com/5.7/en-US/procedural-content-generation/)
- 测试用例：此插件无独立测试；底层 PCG 测试位于 `Engine/Plugins/Experimental/PCG/Source/PCGTests/`