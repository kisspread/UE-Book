# Animation Assistant Toolset

> Toolset for Animation Systems

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `AnimationAssistantToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Toolsets/AnimationAssistantToolset) | |

## 用途

AnimationAssistantToolset 是一个面向动画系统的工具集注册插件。它本身不包含复杂的业务逻辑，而是作为 **ToolsetRegistry** 框架下的一个工具集入口，将动画相关的工具（如动画混合器 Anim Mixer）注册到统一的工具集管理系统中。

该插件是 Epic 的 **AI Toolsets** 计划的一部分——一系列用于 AI 驱动的动画和序列编辑的工具集插件。从 git 历史可以看到，Anim Mixer 功能从 SequencerTools 中拆分出来，独立成为此插件，体现了模块化拆分的设计思路。

**为什么存在？** 它为动画系统提供了一个统一的工具集注册点，使得 AI 辅助的动画编辑工具可以通过 ToolsetRegistry 框架被发现和使用，同时与 ControlRig、LevelSequenceEditor 等动画基础设施深度集成。

## 使用场景

- 你需要通过 ToolsetRegistry 框架访问 AI 驱动的动画编辑工具 → 启用此插件
- 你在使用 ControlRig 和 Sequencer 进行动画制作，需要辅助工具集 → 启用此插件
- 你正在构建自定义的 AI 动画工作流 → 此插件提供基础注册框架

## 蓝图用法

该插件源码中未暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。它是一个纯编辑器模块，主要通过 ToolsetRegistry 框架在内部注册工具集，不直接提供蓝图 API。

## C++ 用法

该插件仅包含模块接口定义，无公开的 C++ API 供外部调用。其核心功能是通过 `StartupModule()` / `ShutdownModule()` 生命周期向 ToolsetRegistry 注册动画工具集。

### 头文件引入

```cpp
#include "AnimationAssistantToolset.h"
```

### 基本用法

该插件作为 ToolsetRegistry 的工具集提供者运行，无需用户直接调用其 API。启用插件后，动画工具集将自动注册到工具集系统中。

## Demo 示例

该插件不提供可直接使用的 API，因此无独立的代码示例。其功能通过 ToolsetRegistry 框架自动生效——只需在插件设置中启用即可。

## 模块依赖

该插件依赖以下插件（非模块级依赖，而是插件级依赖）：

| 插件 | 用途 |
|---|---|
| `ControlRig` | 提供控制骨骼动画的运行时和编辑器框架 |
| `ToolsetRegistry` | 提供工具集注册和发现框架 |
| `LevelSequenceEditor` | 提供关卡序列编辑器功能 |
| `SequencerScripting` | 提供 Sequencer 的脚本化 API |

无特殊模块依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

```
- 77af3950 2026-04-10 [EDA] Add SequencerTools toolset with Anim Mixer split into separate plugin
- 8bd8f719 2026-04-10 [Backout] - CL52569948
- e98edc29 2026-04-10 [EDA] Add SequencerTools toolset for AI-driven sequence creation and editing
- aed04419 2026-04-03 [AI Toolsets]: Ensure all toolset plugins are marked as editor only.
- 7f02bd73 2026-04-03 [AI Toolsets]: Move all toolsets to load at post engine init to simplify registration when toolset r
```

### 维护评价

- **状态**: 🆕 新建插件，处于早期开发阶段
- **创建时间**: 2026-04-03，距今不到 1 周
- **活跃度**: 非常活跃，创建后一周内有多次提交，包括功能拆分和回退操作
- **实验性标记**: `IsExperimentalVersion=true`，`Installed=false`，需手动启用
- **已知限制**: 源码极少（仅 2 个文件），功能可能尚未完全实现或大部分逻辑在依赖插件中
- **推荐程度**: ⚠️ **暂不推荐生产使用**。作为实验性插件且刚创建不久，API 和功能可能频繁变动。适合关注 AI 动画工具发展的开发者跟踪了解。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Toolsets/AnimationAssistantToolset)
- 官方文档：无
- 测试用例：无