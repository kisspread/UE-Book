# Interchange Pregen Shared Content

> Shared content assets for Interchange pregeneration, usable across multiple projects

| 属性 | 值 |
|---|---|
| 中文名 | 预生成共享内容 |
| 分类 | Content |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（共享资产） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen/Templates/InterchangePregenSharedContent) | |

## 用途

此插件是一个纯内容插件，本身不包含任何代码模块。其核心作用是为 `Interchange` 框架在 `USD` 资产预生成（Pregeneration）流程中，提供一套可跨项目共享的基础资产。这些资产（例如材质、纹理、蓝图模板等）可能作为 USD 导入或处理过程中的默认资源或引用模板，避免在每个项目中重复创建，从而确保 USD 工作流的一致性和效率。

## 使用场景

- **USD 资产管线开发**：在建立基于 USD 的资产导入、转换或渲染管线时，需要一套标准的共享资源（如 PBR 材质球）作为基础，此插件提供了这些预构建的资源。
- **多项目资源共享**：当多个团队或项目需要使用相同的 USD 处理基础设置时，可以依赖此插件来保持一致性，无需手动在每个项目中配置。
- **Interchange 流程定制**：在开发或测试使用 `Interchange` 框架处理 USD 数据的自定义流程时，此插件可作为依赖项，提供流程所需的预定义内容。

## 蓝图用法

此插件为纯内容插件，不包含任何可执行代码模块（如 `.uasset` 形式的蓝图）。因此，**没有可调用的蓝图函数或节点**。

## C++ 用法

此插件为纯内容插件，不包含任何 C++ 模块或头文件。因此，**没有可供引用的 C++ API**。它的用途仅限于作为内容依赖项，供其他包含代码的插件（如 `USDPregen`）或项目使用其资产。

## Demo 示例

不适用。此插件本身即为内容资产的集合，没有需要演示的代码示例。

## 模块依赖

此插件本身无代码模块。根据 `.uplugin` 文件，它**依赖**于以下插件：

| 插件 | 用途 |
|---|---|
| `USDPregen` | 核心依赖。此插件是 `USDPregen` 工作流内容资产的组成部分。 |

## 维护状态

### 近期更新

- `4ba31204` 2026-05-13 — [USD] UsdPregen: Moving the plugin out of restricted and into experimental.
  **解读**：此插件的首次出现即为本次提交。它从受限目录移入实验性目录，标志着其内容和关联工作流（USD 预生成）正从内部开发阶段转向可供更广泛开发者测试的阶段。

### 维护评价

- **创建时间**：2026年5月13日（当前文档生成时间点为2025年3月30日，此为未来日期，表明这是 Epic 内部当前开发分支的快照）。
- **维护频率**：此插件在 `5.8` 分支的 git 历史中仅有一次相关提交，表明它处于非常早期的整合或发布阶段。
- **活跃度**：作为 `USDPregen` 生态系统的一部分，其维护状态跟随主插件。由于刚刚移入实验性目录，预计在 USD 预处理功能趋于稳定前会持续更新。
- **限制**：纯内容插件，功能取决于 `USDPregen` 核心逻辑。资产可能尚在开发中。
- **推荐**：**仅推荐**给正在实验或开发基于 `USDPregen` 和 `Interchange` 的 USD 工作流的开发者。对于常规的项目内容，一般无需引入此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen/Templates/InterchangePregenSharedContent)
- [父插件 USDPregen 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen)