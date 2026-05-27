# PCG Primitives

> PCG Primitives and Examples Library for World Building

| 属性 | 值 |
|---|---|
| 中文名 | PCG 图元库 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（PCG 图元蓝图资产与世界构建示例） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGPrimitives) | |

## 用途

这是一个**纯内容插件**，为 UE5 的 PCG（Procedural Content Generation，程序化内容生成）框架提供预置的图元（Primitives）和世界构建示例资产。

插件本身不包含任何 C++ 代码，而是打包了一系列可直接使用的 PCG 图表资产、生成器预设和示例配置，帮助开发者快速上手 PCG 系统进行程序化世界构建。它依赖 PCG 核心生态系统中的多个模块（PCG、PCGGeometryScriptInterop、PCGBiomeCore、PCGBiomeSample、PCGExternalDataInterop），说明其提供的资产覆盖了几何脚本互操作、生物群落生成和外部数据导入等多种 PCG 工作流。

**核心价值**：避免从零开始搭建 PCG 图表，直接使用 Epic 官方提供的图元库作为起点或参考。

## 使用场景

- 你正在使用 PCG 框架进行程序化世界构建，需要预置的图元节点和示例作为参考 → 启用此插件
- 你需要快速搭建生物群落（Biome）相关的 PCG 图表 → 此插件提供了与 PCGBiomeCore/PCGBiomeSample 配合使用的示例资产
- 你想学习 PCG 系统的最佳实践 → 此插件的示例资产可作为学习模板
- 你需要将外部数据源接入 PCG 流程 → 依赖 PCGExternalDataInterop，说明包含相关示例

## 蓝图用法

此插件为纯内容插件，不包含 C++ 模块，因此没有自定义蓝图节点。使用方式为直接在 PCG 图表编辑器中引用此插件提供的图元资产和示例。

### 核心资产

插件启用后，其内容资产将出现在 Content Browser 中，通常位于 `Plugins/PCG Primitives/` 目录下。可在 PCG 图表中通过以下方式使用：

1. **在 PCG 图表中添加图元节点**：右键 → 搜索插件提供的生成器或过滤器
2. **引用示例配置**：直接拖拽示例 PCG 图表到场景中
3. **修改示例参数**：根据项目需求调整 PCG 节点的参数和属性

## C++ 用法

不适用。此插件为纯内容插件，无 C++ 模块和源码文件。

## Demo 示例

不适用。此插件本身就是示例库，所有示例资产随插件一同提供。启用插件后即可在 Content Browser 中查看和使用。

**推荐工作流**：

1. 在 Plugins 面板中启用 `PCG Primitives`
2. 在 Content Browser 中导航到插件内容目录
3. 浏览提供的 PCG 图表示例，了解图元的使用方式
4. 复制示例到项目 Content 目录中进行修改和扩展

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PCG` | PCG 核心框架，程序化内容生成的基础系统 |
| `PCGGeometryScriptInterop` | PCG 与 Geometry Script 的互操作，支持程序化网格处理 |
| `PCGBiomeCore` | 生物群落生成核心模块 |
| `PCGBiomeSample` | 生物群落示例资产 |
| `PCGExternalDataInterop` | PCG 外部数据源互操作支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `d2353f53` | PCG Primitives plugins: small friendly name tweak to match other PCG data plugins. | 调整插件显示名称以与其他 PCG 数据插件保持一致 |
| 2026-04-27 | `8f1b41e9` | PCG Primitives: moved the PCG_Primitives plugin into public facing plugins/experimental folder. | 将 PCG 图元插件从内部目录迁移至公开的 experimental 文件夹 |

### 维护评价

- **创建时间**：2026-04-27，是一个非常新的插件
- **当前状态**：实验性（IsExperimentalVersion = true），默认未安装（Installed = false）
- **最近活动**：2026-05-12 有命名规范调整，表明仍在积极维护中
- **已知限制**：
  - 标记为实验性，API 和内容可能随版本变化
  - 默认未安装，需手动启用
  - 强依赖多个 PCG 子插件，缺少任何一个可能导致功能不完整
- **推荐度**：✅ 推荐使用。作为 Epic 官方提供的 PCG 示例库，是学习和快速原型开发的优秀资源。但需注意实验性标签，生产环境使用需谨慎评估。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGPrimitives)
- [PCG 核心插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG)