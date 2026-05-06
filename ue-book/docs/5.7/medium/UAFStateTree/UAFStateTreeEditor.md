# UAF State Tree

> StateTree integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF状态树集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFStateTree` (Runtime), `UAFStateTreeEditor` (Runtime), `UAFStateTreeUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-30 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFStateTree) | |

## 用途

UAF State Tree 是 **UAF（Unreal Animation Framework）** 与 **StateTree** 系统的深度集成插件。它允许开发者将状态树（StateTree）作为动画决策和状态管理的核心组件，嵌入到 UAF 的动画图中，从而构建复杂、动态的动画行为逻辑。

该插件解决了以下问题：
- 在 UAF 动画框架中需要一套强大的、可编辑的层次化状态机（但不限于状态机）来驱动动画过渡。
- 利用 StateTree 的灵活性和运行时效率，替代传统的 AnimBlueprint 状态机或部分复杂 BlendSpace 逻辑。
- 为动画师提供可视化编辑（通过 StateTree 编辑器）来定义动画状态、条件和动作，并直接与 UAF 的数据模型挂钩。

> ⚠️ 本插件目前处于**实验性**阶段，API 和功能可能会在后续版本中发生较大变化，不建议直接用于生产项目。

## 使用场景

- 你在使用 UAF 构建次世代动画系统，需要一种可扩展的状态机逻辑来控制角色动画混合。
- 你需要将动画状态与游戏逻辑（如 AI、交互）通过 StateTree 共享条件/任务进行协同。
- 你希望动画师可以在 StateTree 编辑器中直接创建和调整动画状态图，而无需工程师大量介入。
- 你正在开发需要复杂分层状态管理（如战斗、运动、攀爬等）的项目，并且已经引入 UAF。

## 蓝图用法

由于该插件主要面向编辑器集成和 C++ 扩展，当前模块中**没有公开的 BlueprintCallable 函数或 BlueprintReadWrite 属性**。所有功能通过 UAF 的动画图节点、StateTree 任务/条件及编辑器操作暴露。

### 核心节点（动画图上下文）

以下节点在 UAF 动画图中可用（需在 UAF 拥有蓝图节点的情况下）：

| 节点 | 说明 | 所在模块 |
|---|---|---|
| `EvaluateStateTree` | 在动画图中评估一个 UAnimNextStateTree 资产，驱动后续动画输出 | `UAFStateTree` (Runtime) |

> 详细节点和参数请查阅 UAF 动画图节点的官方文档。

### 编辑器操作（内容浏览器）

在内容浏览器中右键 → **动画** → **动画框架** 类别下，可以创建 **UAF State Tree** 资产。双击该资产将打开 StateTree 编辑器，其中宿主环境为 UAF 动画框架。

## C++ 用法

### 头文件引入

```cpp
#include "IAnimNextStateTreeEditorModule.h"   // 编辑器模块接口
#include "AnimNextStateTree.h"                // 核心资产类（运行时）
```

### 基本用法

**1. 在 C++ 中创建 UAF State Tree 资产**

```cpp
// 使用工厂类在内容包内创建
UAnimNextStateTree* NewTree = NewObject<UAnimNextStateTree>(
    InPackage,
    UAnimNextStateTree::StaticClass(),
    *AssetName,
    RF_Standalone | RF_Public
);
NewTree->Modify();
// 后续可设置 StateTree 数据、添加状态等
```

**2. 在 UAF 动画节点中绑定 StateTree**

在自定义 UAF 动画节点（继承自 `UAnimNextNode`）中，持有 `UAnimNextStateTree` 的引用，并在评估时调用其运行时模型：

```cpp
// 假设节点类中有一个成员 UAnimNextStateTree* StateTreeAsset;
void FMyAnimNode::Evaluate(FAnimNextEvaluationContext& Context) const
{
    if (StateTreeAsset && StateTreeAsset->GetStateTree())
    {
        // 获取底层 StateTree 实例并执行
        UStateTree* ST = StateTreeAsset->GetStateTree();
        // ... 通过 Context 调用 StateTree 的 Tick/TickState 等
    }
}
```

**3. 编辑器集成（自定义宿主）**

继承 `IStateTreeEditorHost` 并将自己注册为编辑器宿主，可以参考 `FAnimNextStateTreeEditorHost` 的实现。

### 进阶用法

**编译与状态监听**

```cpp
// 从 UAF 的 AssetCompilationHandler 派生，处理 StateTree 的编译
class FMyCompilationHandler : public UE::UAF::Editor::FAssetCompilationHandler
{
public:
    virtual void Compile(TSharedRef<Workspace::IWorkspaceEditor> InEditor, UObject* InAsset) override
    {
        if (UAnimNextStateTree* Tree = Cast<UAnimNextStateTree>(InAsset))
        {
            // 执行编译逻辑，最终调用 UStateTree 的编译
        }
    }
};
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何在 C++ 中创建并利用 UAF State Tree 资产。

### MyAnimNode.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "AnimNextNode.h"
#include "AnimNextStateTree.h"
#include "MyAnimNode.generated.h"

UCLASS()
class UMyAnimNode : public UAnimNextNode
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "StateTree")
    TObjectPtr<UAnimNextStateTree> StateTreeAsset;

    // UAnimNextNode interface
    virtual void Evaluate(UE::AnimNext::FAnimNextEvaluationContext& Context) const override;
};
```

### MyAnimNode.cpp

```cpp
#include "MyAnimNode.h"
#include "StateTree.h"

void UMyAnimNode::Evaluate(UE::AnimNext::FAnimNextEvaluationContext& Context) const
{
    if (!StateTreeAsset)
        return;

    UStateTree* StateTree = StateTreeAsset->GetStateTree();
    if (!StateTree)
        return;

    // 假设 StateTree 有运行实例（实际使用中需创建 FStateTreeInstanceData）
    // 这里仅演示如何获取资产并触发评估
    // Context 通常提供 DeltaTime、骨骼姿势等输入
    // StateTree->Tick(...); // 伪代码
}
```

### 创建资产（在模块 StartupModule 中演示）

```cpp
// 在某个模块的 Startup 中执行一次
void FMyModule::StartupModule()
{
    // 查找或者创建资产路径
    UPackage* Package = CreatePackage(TEXT("/Game/MyStateTree"));
    UAnimNextStateTree* NewTree = NewObject<UAnimNextStateTree>(
        Package,
        UAnimNextStateTree::StaticClass(),
        FName("NewUAFStateTree"),
        RF_Standalone | RF_Public
    );
    NewTree->Modify();
    // 可以设置 StateTree 的默认状态等（通过 UStateTree 的 API）
    // ...
    Package->MarkPackageDirty();
}
```

## 模块依赖

要使用本插件的功能，您的模块（Build.cs）需要添加以下依赖。**标准依赖（Core, Engine 等）已省略**，只列出特殊项。

| 模块 | 用途 |
|---|---|
| `StateTree` | 核心状态树运行时，提供状态机/行为树结构 |
| `StateTreeEditor` |（编辑器模块）提供 StateTree 编辑器 UI 和编译 |
| `UAF` | Unreal Animation Framework 运行时，本插件为其提供集成 |
| `UAFEditor` |（编辑器模块）提供 UAF 编辑器基础及资产编译支持 |

> 完整依赖链请查看 `UAFStateTree.Build.cs`、`UAFStateTreeEditor.Build.cs`。

## 维护状态

### 近期更新

- 2025-09-23 `9a934fb4` Fix UAF leaking callbacks causing UAF state tree selection to be cleared.
- 2025-08-28 `9273c535` Add missing IUpdate propagation to StateTree
- 2025-08-15 `031b08ff` UAF StateTree autocomplete on graph timeline complete
- 2025-08-01 `7aace74a` Downgrade check to ensure on statetree failure
- 2025-07-30 `3ac8187c` UAF Read/Write Variable in Function Fixes

### 维护评价

- **创建时间**：2025年7月（约2个月前），属于**全新**项目。
- **更新频率**：高，几乎每周都有功能性更新或 Bug 修复。
- **活跃度**：非常活跃，Epic 正积极迭代。
- **已知问题**：实验性，可能存在不稳定 API 和缺少文档。
- **推荐使用**：如果已经在使用 UAF 并需要 StateTree 集成，可以试用并提供反馈；不适用于正式生产环境，请关注后续稳定版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFStateTree)
- 官方文档：暂无（DocsURL 为空）
- 测试用例：未提供（可关注 `Engine/Plugins/Experimental/UAF/UAFStateTree/Tests` 目录）