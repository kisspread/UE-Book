# UAF State Tree

> StateTree integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF状态树 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器集成） |
| 模块 | `UAFStateTreeEditor` (Runtime), `UAFStateTree` (Runtime), `UAFStateTreeUncookedOnly` (Runtime), `UAFStateTreeTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree) | |

## 用途

本插件是 **Unreal Animation Framework (UAF)** 与 **StateTree** 状态机的桥梁。它将状态树的强大逻辑控制能力引入UAF的动画蓝图工作流程中，主要解决在动画编辑器（特别是UAF的“工作空间”编辑器）中直接编辑、预览和调试驱动动画逻辑的状态机的需求。它为`UAnimNextStateTree`资产提供了完整的编辑器支持（资产定义、工厂、自定义Schema和宿主），使得动画师和开发者可以在UAF的上下文中，像编辑蓝图状态机一样，通过可视化界面来构建复杂的动画状态转换逻辑。

## 使用场景

-   你需要为角色或载具定义一套复杂、分层的动画状态逻辑（如待机、奔跑、跳跃、特殊攻击的切换与混合），并希望在UAF的工作流内进行可视化管理。
-   你正在使用UAF的动画蓝图，并希望利用状态树的事件驱动、条件判断和子树复用等高级功能来驱动动画状态的转换，而不是仅依赖传统的动画蓝图状态机。
-   你希望状态机的编辑和调试能集成到UAF的“工作空间”编辑器界面中，方便与其他动画资产（如动画层、动画图）一起编辑和预览。

## 蓝图用法

当前插件主要提供编辑器侧的集成功能，其核心逻辑通过C++和Editor扩展实现。蓝图层面，它主要提供 `UAnimNextStateTree` 资产类型的创建和在UAF工作空间中的打开能力。具体的蓝图节点（如控制状态机运行）通常属于UAF和StateTree运行时核心功能。

### 核心资产

| 资产/类 | 说明 |
|---|---|
| `UAnimNextStateTree` | UAF系统下的状态树资产。双击可在集成的状态树编辑器中打开进行编辑。 |

### 使用示例（蓝图描述）

在内容浏览器中，通过“动画 > 动画框架”类别可以创建“UAF状态树”资产。创建后，将其赋值给UAF动画蓝图中的相应属性，或在UAF工作空间编辑器中作为关联文档打开，即可开始编辑状态逻辑。状态树的节点和转换在专门的编辑器标签页中配置。

## C++ 用法

主要涉及对状态树编辑器宿主和编译处理器的扩展，适用于需要深度定制UAF编辑器集成或添加自定义编译逻辑的场景。

### 头文件引入

```cpp
#include “UAFStateTreeEditorModule.h”
#include “AnimNextStateTreeEditorHost.h”
// 需依赖 UAFStateTreeEditor 模块
```

### 基本用法：实现编辑器宿主 (Editor Host)

`FAnimNextStateTreeEditorHost` 是连接UAF工作空间编辑器和状态树编辑器的核心。你需要实现自己的宿主来管理状态树资产的获取和编辑器视图的集成。

```cpp
// 来自 Private/AnimNextStateTreeEditorHost.h
// 创建一个编辑器宿主，用于在Workspace编辑器中承载状态树
class FMyCustomStateTreeHost : public FAnimNextStateTreeEditorHost
{
public:
    // 初始化宿主，绑定到Workspace编辑器
    void Setup(TWeakPtr<UE::Workspace::IWorkspaceEditor> InWorkspaceEditor)
    {
        Init(InWorkspaceEditor);
    }
    
    // 根据当前Workspace文档获取对应的状态树资产
    // 通常由 Workspace 编辑器调用
    virtual UStateTree* GetStateTree() const override
    {
        // 这里会返回与当前聚焦文档关联的 UAnimNextStateTree
        return FAnimNextStateTreeEditorHost::GetStateTree();
    }
    
    // 可重写以控制是否显示编译按钮等UI元素
    virtual bool ShouldShowCompileButton() const override
    {
        return true;
    }
};
```

### 进阶用法：集成自定义编译处理器

`FStateTreeAssetCompilationHandler` 用于在Workspace编辑器中触发状态树的编译并跟踪编译状态。

```cpp
// 来自 Private/StateTreeAssetCompilationHandler.h
// 假设你有一个 UAnimNextStateTree 资产的指针 StateTreeAsset
FStateTreeAssetCompilationHandler CompilationHandler(StateTreeAsset);
CompilationHandler.Initialize(); // 绑定内部委托

// 当需要在Workspace编辑器中编译该资产时
TSharedRef<UE::Workspace::IWorkspaceEditor> WorkspaceEditor = ...;
CompilationHandler.Compile(WorkspaceEditor, StateTreeAsset);

// 查询编译状态
UE::UAF::Editor::ECompileStatus Status = CompilationHandler.GetCompileStatus(WorkspaceEditor, StateTreeAsset);
if (Status == UE::UAF::Editor::ECompileStatus::Success)
{
    // 编译成功
}
```

## Demo 示例

以下示例展示了如何在一个简单的编辑器模块中，实例化一个`FAnimNextStateTreeEditorHost`并将其与Workspace编辑器关联。这通常是UAF状态树编辑器内部发生的过程。

**MyStateTreeEditorIntegration.h**
```cpp
#pragma once

#include “AnimNextStateTreeEditorHost.h”
#include “Workspace/IWorkspaceEditor.h”

class FMyStateTreeEditorIntegration
{
public:
    // 初始化并绑定到Workspace编辑器
    void Initialize(TWeakPtr<UE::Workspace::IWorkspaceEditor> InWeakEditor);
    
    // 获取编辑器宿主，用于提供给状态树编辑器
    TSharedRef<FAnimNextStateTreeEditorHost> GetEditorHost() const { return EditorHost.ToSharedRef(); }

private:
    TSharedPtr<FAnimNextStateTreeEditorHost> EditorHost;
    TWeakPtr<UE::Workspace::IWorkspaceEditor> WeakWorkspaceEditor;
};
```

**MyStateTreeEditorIntegration.cpp**
```cpp
#include “MyStateTreeEditorIntegration.h”

void FMyStateTreeEditorIntegration::Initialize(TWeakPtr<UE::Workspace::IWorkspaceEditor> InWeakEditor)
{
    WeakWorkspaceEditor = InWeakEditor;
    
    // 创建状态树编辑器宿主实例
    EditorHost = MakeShared<FAnimNextStateTreeEditorHost>();
    
    // 将宿主初始化并绑定到当前的Workspace编辑器
    // 这样宿主就能感知当前文档变化，并管理状态树资产
    if (TSharedPtr<UE::Workspace::IWorkspaceEditor> Editor = WeakWorkspaceEditor.Pin())
    {
        EditorHost->Init(InWeakEditor);
    }
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `UAF` | 底层动画框架模块 |
| `StateTree` | 状态树运行时和编辑器核心模块 |
| `StateTreeEditor` | 状态树编辑器UI和逻辑 |
| `Workspace` | UAF的工作空间编辑器框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移到UE_LOGF，进行日志系统现代化更新。 |
| 2026-04-13 | `6f1ea925` | State Tree: Updated state tree reference struct details to show the display name of the struct rathe | 更新状态树引用结构体细节面板，以显示结构体的显示名称而非内部名称，提升编辑器易读性。 |
| 2026-04-13 | `5078d880` | Add UAFSharedAssets plugin for content we want to provide that references UAF assets defined in sepa | 新增UAFSharedAssets插件，用于管理跨多个UAF插件共享的资产引用。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 将GetComponent函数重命名为GetOrAddComponent，使其名称更准确地反映其“存在则获取，不存在则创建”的实际功能。 |
| 2026-03-31 | `4e41a45f` | Fix crash attempting to manually create UAF ST by hiding UAF ST Schema | 修复一个崩溃问题：隐藏了UAF状态树的Schema，以防止用户通过错误路径手动创建资产导致的崩溃。 |

### 维护评价

该插件于 **2025年6月** 创建，是一个较新的实验性插件。从近期提交记录看，**维护非常活跃**（最近更新在2026年4月）。更新内容集中在编辑器UI优化、资产创建流程修复、模块化重构以及日志系统迁移，表明它处于积极的开发和打磨阶段。

**主要优势**：
1.  **活跃开发**：最近一个月有多次实质性提交。
2.  **深度集成**：为UAF工作流量身打造状态树编辑体验。
3.  **实验性但稳定**：虽然标记为实验性，但近期修复了关键崩溃问题，稳定性在提升。

**注意事项**：
1.  **实验性**：API和功能未来可能会有较大变动。
2.  **默认未启用**：需要在项目设置中手动启用“UAF State Tree”插件。
3.  **依赖关系**：依赖UAF和StateTree等插件，需确保这些插件已正确启用。

**推荐使用**：如果你已在使用UAF动画框架，并且需要状态树提供的强大逻辑控制能力，那么强烈推荐启用和试用此插件。它是连接这两个强大系统的官方桥梁，尽管是实验性状态，但已具备完整的编辑器功能且维护积极。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree/Tests)