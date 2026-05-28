# MetaHuman Character Creator

> MetaHuman Character Asset Creator and Editor.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 角色创建器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（角色资产、编辑器工具） |
| 模块 | `MetaHumanCharacter` (Runtime), `MetaHumanCharacterEditor` (Runtime), `MetaHumanCharacterMigrationEditor` (Runtime), `MetaHumanCharacterPalette` (Runtime), `MetaHumanCharacterPaletteEditor` (Runtime), `MetaHumanDefaultEditorPipeline` (Runtime), `MetaHumanDefaultPipeline` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter) | |

## 用途

本插件是 **MetaHuman 角色创建工具链的核心**。它不仅仅是一个资产查看器，而是一个完整的、用于在虚幻编辑器内创建、编辑和管理高保真 MetaHuman 角色的 **Runtime 和 Editor 框架**。它解决了从 DNA 数据到可驱动骨骼网格体资产（Skeletal Mesh）的 **全管线转换、预览与编辑** 问题，并提供了可扩展的编辑器工具（调色板、迁移、默认管道）来支持专业的数字人制作工作流。插件默认未启用，表明其主要面向专业 MetaHuman 创作流程。

## 使用场景

- **创建数字人类**：你作为角色美术或技术美术，需要使用 MetaHuman 技术从零开始创建或修改一个高保真数字人类角色。
- **资产管线集成**：你需要将 MetaHuman 的 DNA 数据（如来自 MetaHuman Creator）转换为可在游戏中驱动的骨骼、动画和材质资产。
- **批量角色管理**：你需要使用“调色板”（Palette）功能来系统化管理和应用不同角色部位（如面部、发型、服装）的资产。
- **虚拟制片与影视**：你为影视或虚拟制片项目工作，需要快速生成和编辑逼真的数字人类演员。

## 蓝图用法

详细的蓝图 API 分布在各个子模块中（见“模块列表”）。核心的蓝图可调用函数通常用于：
- **资产创建与更新**：从 DNA 或现有数据生成/更新 MetaHuman 角色资产。
- **编辑器交互**：通过蓝图控制编辑器窗口（如角色预览窗口）的行为。
- **调色板操作**：管理角色部件的集合。

## C++ 用法

详细的 C++ API 分布在各个子模块中。开发者通常会：
- 引入 `MetaHumanCharacter` 模块头文件来访问核心数据结构和管理器。
- 使用 `MetaHumanCharacterEditor` 模块中的类来扩展编辑器功能。
- 通过 `MetaHumanDefaultPipeline` 来定义或覆盖默认的角色资产处理逻辑。

## 模块列表

本插件由以下模块组成，每个模块负责管线的一个环节：

1.  **`MetaHumanCharacter`** (Runtime): 核心运行时模块，定义 MetaHuman 角色的核心数据结构（如 DNA）、资产类型和基础管理器。
2.  **`MetaHumanCharacterEditor`** (Runtime): 核心编辑器模块，提供用于创建、编辑、预览 MetaHuman 角色资产的编辑器工具、窗口和命令。
3.  **`MetaHumanCharacterMigrationEditor`** (Runtime): 用于将旧版或外部格式的 MetaHuman 数据迁移到当前框架版本的编辑器工具。
4.  **`MetaHumanCharacterPalette`** (Runtime): 定义“调色板”资产，用于组织和管理可互换的角色部件（如面部、身体、服装）集合。
5.  **`MetaHumanCharacterPaletteEditor`** (Runtime): 用于在编辑器中创建和编辑“调色板”资产的工具。
6.  **`MetaHumanDefaultPipeline`** (Runtime): 定义默认的资产处理管道，描述如何将 MetaHuman 角色数据转换为最终的 Skeletal Mesh、材质等资产。
7.  **`MetaHumanDefaultEditorPipeline`** (Runtime): 定义默认的编辑器内处理管道，扩展 `MetaHumanDefaultPipeline`，添加编辑器特有的预览、调试等功能。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `95d906ba` | [UEMHC] Checking for Asset Registry filter validity before using it | 修复资产注册表过滤器使用前的有效性检查，提升稳定性 |
| 2026-05-26 | `7f10fbf1` | [MetaHuman] Titan v9.0.8 | 集成 MetaHuman 核心库 Titan 更新至 v9.0.8 |
| 2026-05-26 | `efb27122` | [UEMHC] Duplicate face/body DNA when duplicating archetype skel meshes | 修复在复制原型骨骼网格体时，复制相关DNA数据的逻辑 |
| 2026-05-26 | `909bc538` | [MHC] Use safer weak pointers for captured objects in MHC preview delegates | 在预览委托中使用更安全的弱指针，防止崩溃 |
| 2026-05-26 | `cfa3dac6` | [MetaHuman] Titan v9.0.7 | 集成 MetaHuman 核心库 Titan 更新至 v9.0.7 |

### 维护评价

该插件**处于活跃维护状态**。它于 2025 年 3 月创建，最新更新记录显示至 2026 年 5 月仍有频繁的功能更新、Bug 修复和核心库（Titan）集成。作为 MetaHuman 技术栈的官方核心插件，由 Epic Games 团队维护，其稳定性和功能演进有保障。`IsBetaVersion: true` 表明其 API 和功能可能仍在调整中，但基于近期密集的提交，可以认为正在向成熟产品迭代。**推荐**需要在虚幻引擎中深度集成 MetaHuman 工作流的项目使用，但需注意其 API 可能随版本变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter/Tests) (如果存在)