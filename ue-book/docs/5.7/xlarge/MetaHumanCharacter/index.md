# MetaHuman Creator

> MetaHuman Character Asset Creator and Editor.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaHuman角色资产） |
| 模块 | `MetaHumanCharacter` (Runtime), `MetaHumanCharacterEditor` (Runtime), `MetaHumanCharacterMigrationEditor` (Runtime), `MetaHumanCharacterPalette` (Runtime), `MetaHumanCharacterPaletteEditor` (Runtime), `MetaHumanDefaultEditorPipeline` (Runtime), `MetaHumanDefaultPipeline` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCharacter) | |

## 用途

该插件是 Epic Games 为 Unreal Engine 打造的 MetaHuman 角色创建与编辑的核心工具集。它不仅仅是一个资产导入器，而是一个完整的角色资产生产管线。其核心目的是在引擎内部提供一套工具，用于创建、编辑、组装和管理高度逼真的 MetaHuman 数字人角色资产，包括面部、身体、服装、发型等各个组成部分，并支持将这些资产打包为可复用的“角色调色板”（Character Palette）。

## 使用场景

- **创建全新的 MetaHuman 角色**：你需要从零开始设计一个数字人角色，并希望直接在 UE 编辑器中完成，而不是依赖外部云服务。
- **编辑和定制现有角色**：你已经有一个 MetaHuman 角色，需要调整其面部特征、肤色、发型或服装。
- **管理角色资产库**：你的项目中有多个 MetaHuman 角色，需要高效地管理、复用和共享他们的外观组件（如发型、服装）。
- **迁移旧版资产**：你拥有使用旧版 MetaHuman 工作流创建的角色资产，需要将其迁移到新的、基于调色板的系统中。
- **构建角色创建管线**：作为技术美术或工具开发者，你需要为团队搭建一个标准化的 MetaHuman 角色创建和编辑流程。

## 模块列表

本插件由以下模块组成，共同构成了完整的 MetaHuman 角色创建管线：

| 模块 | 类型 | 一句话总结 | 详细文档 |
|---|---|---|---|
| `MetaHumanCharacter` | Runtime | 核心运行时模块，定义了 MetaHuman 角色资产、调色板等基础数据结构和核心逻辑。 | [MetaHumanCharacter.md](MetaHumanCharacter.md) |
| `MetaHumanCharacterEditor` | Runtime | 编辑器扩展模块，提供角色创建、编辑、预览的 UI 和工具。 | [MetaHumanCharacterEditor.md](MetaHumanCharacterEditor.md) |
| `MetaHumanCharacterPalette` | Runtime | 角色调色板运行时模块，管理角色外观组件（如发型、服装）的集合和资产。 | [MetaHumanCharacterPalette.md](MetaHumanCharacterPalette.md) |
| `MetaHumanCharacterPaletteEditor` | Runtime | 调色板编辑器模块，提供创建、编辑和管理角色调色板资产的工具。 | [MetaHumanCharacterPaletteEditor.md](MetaHumanCharacterPaletteEditor.md) |
| `MetaHumanCharacterMigrationEditor` | Runtime | 迁移工具模块，用于将旧版 MetaHuman 角色资产转换为新的调色板格式。 | [MetaHumanCharacterMigrationEditor.md](MetaHumanCharacterMigrationEditor.md) |
| `MetaHumanDefaultPipeline` | Runtime | 默认处理管线运行时模块，定义了角色资产从创建到最终生成的默认处理流程。 | [MetaHumanDefaultPipeline.md](MetaHumanDefaultPipeline.md) |
| `MetaHumanDefaultEditorPipeline` | Runtime | 默认编辑器管线模块，为编辑器中的角色创建和编辑流程提供默认实现。 | [MetaHumanDefaultEditorPipeline.md](MetaHumanDefaultEditorPipeline.md) |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCharacter)