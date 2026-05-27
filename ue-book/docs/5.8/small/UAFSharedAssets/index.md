# UAF Shared Assets

> UAF Default Assets that interact with multiple plugins

| 属性 | 值 |
|---|---|
| 中文名 | UAF 共享资产 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（UAF 浏览器资产配置、共享资产） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFSharedAssets) | |

## 用途

UAFSharedAssets 是一个**纯内容插件**，专门存放需要跨多个独立 UAF 插件引用的共享资产。它解决的核心问题是：当动画资产（如空间查询、姿态搜索配置）需要被多个 UAF 相关插件共同使用时，这些资产没有合适的归属位置。

具体来说，该插件：
- 为 **UAF Browser** 提供标准化的 ST（空间查询）和 Pose Search 资产配置
- 作为 UAF 生态系统中跨插件内容的**中央存放点**
- 避免了资产在多个插件间重复定义的问题

> **UAF** = Unreal Animation Framework（虚幻动画框架），是 Epic 推进中的新一代动画系统架构。

## 使用场景

- 你的项目依赖多个 UAF 相关插件（如动画浏览器、姿态搜索等），需要共享默认资产配置
- 你正在使用 UAF Browser 并需要预配置的 ST / Pose Search 资产
- 你需要在 Tagged Asset Browser 中合并来自不同扩展配置的同名分组

## 蓝图用法

本插件为纯内容插件，不包含 C++ 模块，因此没有可调用的蓝图节点。插件提供的是**资产引用**，供其他 UAF 插件在运行时或编辑器中消费。

### 资产内容

| 资产类型 | 说明 |
|---|---|
| UAF Browser 资产配置 | 包含 ST（空间查询）和 Pose Search 的默认配置 |
| Tagged Asset Browser 扩展配置 | 支持跨插件合并同名分组的内容引用 |

## C++ 用法

本插件无 C++ 模块，不提供编程接口。

## Demo 示例

不适用（纯内容插件，无代码示例）。

## 模块依赖

本插件无代码模块，无需在 Build.cs 中添加依赖。

### 插件依赖

| 插件 | 用途 |
|---|---|
| `Workspace` | 提供 Tagged Asset Browser 等工作区基础设施 |
| UAF 相关插件（名称待确认） | 提供被引用的 UAF 资产定义 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-13 | `5078d880` | Add UAFSharedAssets plugin for content we want to provide that references UAF assets defined in separate, independent, plugins. Use new plugin to add ST / Pose search to UAF Browser asset config. Update Tagged Asset Browser to support merging sections of the same name across extension configs. Add `AppendAfterFilterName` to specify where to merge (Hidden if not extension). Add `bMergeExtensionsPerSection` to allow for merging of same named sections (Enabled by default). | 初始提交：创建 UAF 共享资产插件，为浏览器添加 ST/Pose Search 配置，并更新资产浏览器支持跨扩展配置合并同名分组 |

### 维护评价

- **创建时间**：2026-04-13，极为年轻（约 0 年）
- **更新频率**：仅有初始提交，尚无后续更新记录
- **维护状态**：🆕 **全新插件**，处于实验阶段
- **已知限制**：
  - `IsExperimentalVersion=true`，`Installed=false`——需要手动在插件管理器中启用
  - `.uplugin` 显示被截断，完整插件依赖列表可能未完全展示
  - 作为实验性插件，API 和资产结构可能随 UAF 架构演进而变更
- **推荐程度**：⚠️ 仅建议 UAF 框架的早期采用者和 Epic 内部开发使用，不建议生产项目依赖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFSharedAssets)
- 官方文档：无
- 测试用例：无（纯内容插件）

> **备注**：本插件属于 UAF（Unreal Animation Framework）生态系统的一部分，与 `Engine/Plugins/Experimental/UAF/` 下的其他 UAF 插件协同工作。随着 UAF 框架从实验阶段向正式版演进，该插件的结构和内容可能会有较大变化。