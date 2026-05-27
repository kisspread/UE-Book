# UAF Shared Assets

> UAF Default Assets that interact with multiple plugins

| 属性 | 值 |
|---|---|
| 中文名 | UAF 共享资产 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（UAF 浏览器配置资产、标签资产浏览器配置） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFSharedAssets) | |

## 用途

UAFSharedAssets 是一个**纯内容插件**，没有任何 C++ 模块。它的存在是为了解决 UAF（Unreal Animation Framework）生态中**跨插件资产共享**的问题。

在 UAF 架构中，不同的功能模块被拆分为独立的插件（如 ST/Pose Search、UAF Browser 等），但有些资产需要被多个插件共同使用。UAFSharedAssets 就是这些**跨插件共享资产**的统一存放位置，避免将资产放在任何一个功能插件中造成循环依赖。

具体来说，该插件提供的内容包括：
- **UAF Browser 的资产配置**：将 ST（State Tree）和 Pose Search 相关的资产注册到 UAF Browser 中
- **Tagged Asset Browser 的扩展配置**：为标签资产浏览器提供合并配置支持，允许不同扩展配置中同名的 Section 进行合并显示

## 使用场景

- 你需要在 UAF Browser 中浏览和管理 Pose Search 或 State Tree 相关资产 → 安装此插件即可获得默认配置
- 你开发了一个 UAF 扩展插件，需要向 Tagged Asset Browser 注册新的资产分类，且希望与现有 Section 合并 → 通过 `AppendAfterFilterName` 和 `bMergeExtensionsPerSection` 配置扩展行为
- 多个 UAF 子插件需要共享同一套默认资产配置 → 将共享资产放在此插件中统一管理

## 蓝图用法

无。此插件为纯内容插件，不包含任何 BlueprintCallable 函数或蓝图类。

## C++ 用法

无。此插件不包含任何 C++ 模块，无需引入头文件或编写代码。

## Demo 示例

不适用。此插件为纯内容资产插件，无需编写代码。安装插件后，其提供的资产配置会自动被 UAF Browser 和 Tagged Asset Browser 识别并加载。

## 模块依赖

无特殊依赖。此插件是纯内容插件，不包含代码模块。

但插件层面依赖以下插件（在 .uplugin 的 Plugins 字段中声明）：

| 插件 | 用途 |
|---|---|
| `Workspace` | Tagged Asset Browser 所在的插件，提供资产浏览器基础框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-13 | `5078d880` | Add UAFSharedAssets plugin for content we want to provide that references UAF assets defined in separate, independent, plugins. Use new plugin to add ST / Pose search to UAF Browser asset config. Update Tagged Asset Browser to support merging sections of the same name across extension configs. | 创建插件，添加 ST/Pose Search 到 UAF Browser 配置，支持同名 Section 合并显示 |

### 维护评价

- **创建时间**：2026-04-13，极为新建的插件
- **最近更新**：仅有一次初始提交，尚无后续更新
- **实验性标记**：`IsExperimentalVersion=true`，位于 `Experimental/UAF/` 路径下，明确处于实验阶段
- **默认启用**：`Installed=false`，需要手动启用
- **源码规模**：纯内容插件，0 个代码文件，维护成本低
- **依赖链**：属于 UAF 生态系统的一部分，其生命周期取决于 UAF 框架的整体成熟度

**评价**：这是一个刚创建的实验性纯内容插件，目前仅包含 UAF 生态的共享资产配置。由于 UAF 本身仍处于实验阶段，此插件的稳定性取决于上游框架的演进。建议仅在开发 UAF 相关功能时使用，生产环境需谨慎。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFSharedAssets)
- 官方文档：无