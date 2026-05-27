# UAF State Tree

> StateTree integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF状态树 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（模块） |
| 模块 | `UAFStateTree` (Runtime), `UAFStateTreeEditor` (Runtime), `UAFStateTreeUncookedOnly` (Runtime), `UAFStateTreeTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree) | |

## 用途

UAFStateTree 是 Unreal Animation Framework (UAF) 与 StateTree 状态机系统的集成插件。它解决了在 UAF 动画框架中使用 StateTree 来管理和驱动复杂动画状态逻辑的问题。通过这个插件，开发者可以将 StateTree 强大的状态机能力应用于 UAF 的动画资产和角色控制，从而实现更清晰、可维护的动画状态转换和逻辑。

## 使用场景

- 你正在使用 **UAF (Unreal Animation Framework)** 开发角色动画系统，需要管理复杂的动画状态（如移动、攻击、技能、交互等）。
- 你需要一个可视化、可复用的状态机来驱动角色的动画行为，而不是在蓝图或C++中编写大量的状态切换逻辑。
- 你希望利用 StateTree 的**数据驱动、可复用任务节点**等特性来构建模块化的动画逻辑。

## 模块列表

本插件包含以下模块，各司其职：

| 模块 | 类型 | 说明 |
|---|---|---|
| `UAFStateTree` | Runtime | 核心运行时模块，包含 UAF 与 StateTree 集成的核心逻辑、任务、评估器和Schema。 |
| `UAFStateTreeEditor` | Runtime | 编辑器扩展模块，提供用于编辑和可视化 UAF StateTree 资产的自定义工具和界面。 |
| `UAFStateTreeUncookedOnly` | Runtime | 仅在编辑器和开发环境中加载的模块，包含仅用于资产处理和烘焙前的功能。 |
| `UAFStateTreeTests` | Runtime | 自动化测试模块，包含用于验证 UAFStateTree 功能的测试用例。 |

## 蓝图用法

### 核心节点

由于本插件是状态机集成框架，其蓝图节点主要围绕**状态树任务**和**评估器**展开。具体的节点取决于你定义的StateTree Schema和资产。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOrAddComponent` | 获取或创建与UAF StateTree关联的组件。 | `UAFStateTreeComponent` (示例) |
| 其他任务节点 | 各种用于驱动UAF动画行为的自定义StateTree任务。 | `USMStateTreeTask*` (各种任务类) |

*注：详细的蓝图节点列表需参考 `UAFStateTree` 模块的具体文档。*

### 使用示例（蓝图描述）

1.  **创建StateTree资产**：在内容浏览器中右键创建新的 `StateTree` 资产，并选择与UAF相关的Schema（例如 `UAF State Tree Schema`）。
2.  **编辑状态机**：双击打开StateTree资产，在可视化编辑器中添加状态、转换和任务。
3.  **添加UAF任务**：从节点面板拖拽与UAF相关的任务节点（如播放动画蒙太奇、等待动画通知、更新移动等）到状态树中。
4.  **分配给角色**：在角色蓝图中，添加一个 `UAFStateTreeComponent` 组件，并将编辑好的StateTree资产分配给它。
5.  **运行**：运行游戏，角色将根据StateTree中定义的逻辑驱动其动画状态。

## C++ 用法

### 头文件引入

```cpp
#include "UAFStateTree/UAFStateTreeModule.h" // 核心模块接口
```

### 基本用法

以下是一个概念性示例，展示如何在C++中启动或获取一个UAF StateTree组件。

```cpp
// (概念性示例 - 需结合具体类实现)
#include "Components/ActorComponent.h"
#include "UAFStateTreeComponent.h" // 假设的组件头文件

class AMyCharacter : public ACharacter
{
protected:
    UPROPERTY()
    UAFStateTreeComponent* StateTreeComponent;

    virtual void BeginPlay() override
    {
        Super::BeginPlay();
        // 获取或创建UAF StateTree组件
        StateTreeComponent = GetOrAddComponent<UAFStateTreeComponent>();
        if (StateTreeComponent)
        {
            // 启动状态树（StateTree资产通常在蓝图或构造时设置）
            StateTreeComponent->StartLogic();
        }
    }
};
```

### 进阶用法

进阶用法通常涉及编写自定义的 **StateTree任务（Task）** 或 **评估器（Evaluator）** 来扩展UAF的功能。

1.  **自定义任务**：继承自 `USMStateTreeTask` (或相关基类)，重写其进入（`Enter`）、退出（`Exit`）和Tick（`Tick`）函数。
2.  **集成UAF数据**：在任务中访问和操作 `UAF` 相关的组件（如动画组件、移动组件）。
3.  **注册任务**：通过 `UAFStateTree` 模块提供的注册机制，将你的自定义任务注册到可用的StateTree节点列表中。

*注：具体API和最佳实践请参考 `UAFStateTreeTests` 中的测试用例以及 `UAFStateTree` 和 `UAFStateTreeEditor` 模块的源代码。*

## 模块依赖

要使用此插件，你的项目或模块需要依赖以下独特的模块（除常见的 Core, Engine 等外）：

| 模块 | 用途 |
|---|---|
| `UAF` | Unreal Animation Framework 核心模块，提供基础的动画框架和组件。 |
| `StateTree` | UE5 的状态树系统核心，提供状态机框架、Schema、任务等基础功能。 |
| `GameplayAbilities` | （可能依赖）如果UAF StateTree需要与Gameplay Ability System交互。 |

*具体依赖关系请参考各模块的 `.Build.cs` 文件。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，统一日志格式。 |
| 2026-04-13 | `6f1ea925` | State Tree: Updated state tree reference struct details to show the display name of the struct rathe | State Tree：更新了状态树引用结构体的详细信息，优先显示结构体的显示名称。 |
| 2026-04-13 | `5078d880` | Add UAFSharedAssets plugin for content we want to provide that references UAF assets defined in sepa | 新增 UAFSharedAssets 插件，用于提供引用其他插件中定义的UAF资产的内容。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 将 GetComponent 函数重命名为 GetOrAddComponent，以更准确地匹配其功能（获取或添加组件）。 |
| 2026-03-31 | `4e41a45f` | Fix crash attempting to manually create UAF ST by hiding UAF ST Schema | 修复了一个尝试手动创建UAF状态树时可能发生的崩溃，方法是隐藏UAF状态树的Schema。 |

### 维护评价

- **活跃维护**：插件创建于2025年6月，至2026年4月仍有持续更新。
- **更新频率**：最近一个月内有多次提交，内容涉及功能增强（如重命名API、修复崩溃）、模块化改进（新增共享资产插件）和日志规范化。
- **实验性状态**：`.uplugin` 中标记为 `IsExperimentalVersion=true`，且默认不启用 (`EnabledByDefault=false`)，表明这是一个正在积极开发中的实验性功能。
- **推荐使用**：**适合希望尝鲜和测试UAF与StateTree集成的开发者**。不建议在追求稳定的生产项目中直接使用，但可用于原型开发和功能验证。请密切关注后续更新和API变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree)
- [官方文档]() (待补充)