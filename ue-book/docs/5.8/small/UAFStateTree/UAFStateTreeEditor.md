# UAF State Tree

> StateTree integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | 动画框架状态树 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `UAFStateTree` (Runtime), `UAFStateTreeEditor` (Runtime), `UAFStateTreeUncookedOnly` (Runtime), `UAFStateTreeTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree) | |

## 用途

UAF State Tree 插件为 Unreal Animation Framework (UAF) 提供了与状态树 (StateTree) 系统的深度集成。它的核心目的是为 UAF 定义的动画资产（如 `UAnimNextStateTree`）提供完整的编辑器支持，包括资产的创建、定义、可视化编辑、编译和调试工作流。通过将 UAF 的动画资产与状态树的逻辑编辑能力相结合，该插件使得动画师和开发者能够在编辑器中直观地构建和编辑复杂的动画状态机与转换逻辑，而无需编写大量蓝图或 C++ 代码。

## 使用场景

- 你正在使用 Unreal Animation Framework (UAF) 构建角色动画，并且需要管理复杂的动画状态（例如待机、行走、奔跑、攻击之间的切换逻辑）。
- 你希望利用状态树提供的强大可视化编辑器来设计动画状态机，而不是在蓝图中使用繁杂的状态图表节点。
- 你需要为自定义的 UAF 动画资产（继承自 UAnimNextStateTree）提供完整的编辑器内资产创建、编辑和编译流程。

## 蓝图用法

此插件主要为编辑器提供运行时和工具支持，其核心功能并非通过蓝图节点暴露给游戏逻辑。它的蓝图“用法”主要体现在编辑器内的资产操作和配置上。

### 核心资产操作

| 操作 | 说明 |
|---|---|
| **创建 UAF State Tree 资产** | 在内容浏览器的 `Animation` 分类下，通过 `Animation Framework` 子菜单创建名为 “UAF State Tree” 的新资产。 |
| **编辑状态树** | 双击资产会打开集成的状态树编辑器，其中包含专为 UAF 动画资产设计的 Schema，支持状态的添加、连接和转换规则设置。 |
| **资产编译** | 在状态树编辑器中或通过资产右键菜单，可以编译状态树资产以更新其逻辑。 |

### 使用示例（蓝图描述）

1.  **创建资产**：在内容浏览器中右键 -> `Animation` -> `Animation Framework` -> `UAF State Tree`。输入名称并保存。
2.  **编辑逻辑**：双击新创建的资产，打开状态树编辑器。在此编辑器中，你可以像编辑普通状态树一样添加状态、设置转换（允许 Reactivation）、并关联 UAF 提供的动画任务或查询。
3.  **在角色蓝图中使用**：在角色的 `AnimInstance` 蓝图中，你需要引用并驱动这个 `UAnimNextStateTree` 资产，具体的连接方式取决于你的 UAF 动画图设置。

## C++ 用法

此插件主要提供编辑器和资产系统的底层支持，开发者通常在 C++ 层面进行扩展或集成，而非直接调用其 API 进行游戏逻辑开发。

### 头文件引入

```cpp
// 若需要扩展编辑器功能
#include "IAnimNextStateTreeEditorModule.h"
```

### 基本用法（模块接口）

此插件通过标准的模块接口与其他编辑器功能交互。

```cpp
// 来源: Source/UAFStateTreeEditor/Public/IAnimNextStateTreeEditorModule.h
// 获取编辑器模块实例（用于需要与编辑器深度集成的插件）
IAnimNextStateTreeEditorModule& EditorModule = FModuleManager::LoadModuleChecked<IAnimNextStateTreeEditorModule>("UAFStateTreeEditor");
```

### 进阶用法（编辑器宿主扩展）

以下代码片段展示了插件内部如何为自定义资产实现状态树编辑器宿主，这为理解其内部架构和可能的扩展点提供了参考。

```cpp
// 来源: Source/UAFStateTreeEditor/Private/AnimNextStateTreeEditorHost.h
// 在Workspace（工作区）环境中，为UAnimNextStateTree资产提供状态树编辑能力。
class FAnimNextStateTreeEditorHost : public IStateTreeEditorHost
{
public:
    // 初始化宿主，并绑定到Workspace编辑器
    void Init(const TWeakPtr<UE::Workspace::IWorkspaceEditor>& InWeakWorkspaceEditor);

    // 实现IStateTreeEditorHost接口，提供状态树编辑器所需的数据和回调
    virtual UStateTree* GetStateTree() const override;
    // ... 其他接口实现
};
```

## Demo 示例

一个最简单的、展示如何创建和使用此插件提供的模块接口的示例。请注意，实际应用主要通过编辑器UI完成。

**AnimNextStateTreeEditorDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"

// 假设我们有一个需要与UAF状态树编辑器交互的自定义编辑器工具
class FMyCustomAnimTool
{
public:
    void Initialize();
    void Shutdown();
};
```

**AnimNextStateTreeEditorDemo.cpp**
```cpp
#include "AnimNextStateTreeEditorDemo.h"
#include "IAnimNextStateTreeEditorModule.h"

void FMyCustomAnimTool::Initialize()
{
    // 检查UAFStateTree编辑器模块是否加载，以决定是否启用相关编辑功能
    if (FModuleManager::Get().IsModuleLoaded("UAFStateTreeEditor"))
    {
        // 可以在此注册自定义的资产动作、细节面板自定义等
        UE_LOG(LogTemp, Log, TEXT("UAF State Tree Editor module is available. Enabling advanced animation editing features."));
    }
}

void FMyCustomAnimTool::Shutdown()
{
    // 清理工作
}
```

## 模块依赖

从代码中引用的类型分析，你的项目模块如果需要与 UAF State Tree 的运行时或编辑器部分交互，可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `AnimNextRuntime` | UAF 的核心运行时模块，提供 `UAnimNextStateTree` 等资产类 |
| `StateTree` | 状态树核心运行时模块 |
| `StateTreeEditorModule` | 状态树编辑器模块，用于实现编辑器集成 |
| `Workspace` | 工作区框架，用于构建集成的资产编辑器环境 |
| `UAFStateTree` | 本插件的运行时模块 |
| `UAFStateTreeEditor` | 本插件的编辑器模块 |

**注意**：`UAFStateTreeTests` 模块仅用于测试，不应被游戏模块依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统升级，使用更新的日志宏。 |
| 2026-04-13 | `6f1ea925` | State Tree: Updated state tree reference struct details to show the display name of the struct rathe | 优化状态树引用结构的细节面板显示。 |
| 2026-04-13 | `5078d880` | Add UAFSharedAssets plugin for content we want to provide that references UAF assets defined in sepa | 引入共享资产插件，为跨插件的UAF资产提供支持。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 接口重命名，`GetComponent` 更名为 `GetOrAddComponent` 以更准确反映其行为。 |
| 2026-03-31 | `4e41a45f` | Fix crash attempting to manually create UAF ST by hiding UAF ST Schema | 修复了手动创建UAF状态树资产时可能发生的崩溃，隐藏了相关Schema。 |

### 维护评价

UAF State Tree 是一个 **实验性 (Experimental)** 插件，最近在 2026 年 4 月仍有多次活跃更新，涉及日志优化、UI改进、架构调整和关键Bug修复。这表明 Epic 正在积极开发和维护它。

**优势**：作为 Unreal Animation Framework (UAF) 官方状态树集成组件，它得到了 Epic 的直接支持，并且更新频繁，意味着它紧跟 UAF 和状态树框架的最新发展。
**风险**：由于是实验性功能，其API和实现可能会在未来版本中发生重大变化，不建议在追求长期稳定性的商业项目核心逻辑中深度依赖。
**建议**：适合用于技术预研、原型开发或作为内部工具链的一部分。如果决定采用，请做好跟进版本更新的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree/Tests)