# Gameplay State Tree

> StateTree for AI/Gameplay Behaviors

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayStateTreeModule` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-05-02 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameplayStateTree) | |

## 用途

GameplayStateTree 是将 UE5 的 StateTree 状态机框架集成到 Gameplay 系统中的桥梁插件。它解决的核心问题是：**如何让 StateTree 在 AI 控制器、行为树和一般 Actor 上实际运行起来**。

StateTree 本身（`StateTree` 插件）只是一个通用的状态机执行引擎，不含任何游戏逻辑。GameplayStateTree 则提供了：
- **Component 层**：`UStateTreeComponent` 和 `UStateTreeAIComponent`，作为 Actor 上的 BrainComponent 运行 StateTree
- **Schema 层**：`UStateTreeComponentSchema` 和 `UStateTreeAIComponentSchema`，定义 StateTree 可以访问哪些上下文数据（Actor、Pawn、AIController、组件、子系统等）
- **Task/Condition 基类**：AI 专用的 StateTree Task 和 Condition 基类
- **行为树桥接**：`UBTTask_RunStateTree` 和 `UBTTask_RunDynamicStateTree`，让 StateTree 可以作为行为树节点执行
- **内置 Task**：`MoveTo`（导航移动）和 `RunEnvQuery`（EQS 查询）
- **蓝图工具函数**：一键在 Actor 上启动 StateTree

简而言之，如果没有这个插件，StateTree 只是一个独立的状态机库；有了它，StateTree 才能真正融入 UE 的 AI/Gameplay 体系。

## 使用场景

- 你在做 AI，想用 StateTree 替代或补充行为树 → 用 `UStateTreeAIComponent` 挂在 AIController 上
- 你有一个非 AI 的 Actor 也需要状态机逻辑（如关卡机关、NPC 对话系统） → 用 `UStateTreeComponent`
- 你想在现有行为树中嵌入一段 StateTree 逻辑 → 用 `UBTTask_RunStateTree` 节点
- 你需要在运行时动态切换行为树中执行的 StateTree → 用 `UBTTask_RunDynamicStateTree`
- 你想在 StateTree 中做 EQS 环境查询 → 用 `FStateTreeRunEnvQueryTask`
- 你想在 StateTree 中做 AI 导航移动 → 用 `FStateTreeMoveToTask`
- 你想快速在蓝图中给任意 Actor 启动一个 StateTree → 用 `RunStateTree` 蓝图函数

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetStateTree` | 设置要运行的 StateTree 资产（运行中不可改） | `UStateTreeComponent` |
| `SetStateTreeReference` | 设置带参数的 StateTree 引用 | `UStateTreeComponent` |
| `AddLinkedStateTreeOverrides` | 添加链接 StateTree 的覆盖 | `UStateTreeComponent` |
| `RemoveLinkedStateTreeOverrides` | 移除链接 StateTree 的覆盖 | `UStateTreeComponent` |
| `SetStartLogicAutomatically` | 设置是否在 BeginPlay 自动启动 | `UStateTreeComponent` |
| `SendStateTreeEvent` | 向运行中的 StateTree 发送事件 | `UStateTreeComponent` |
| `GetStateTreeRunStatus` | 获取当前运行状态 | `UStateTreeComponent` |
| `RunStateTree` | 在指定 Actor 上启动 StateTree（自动创建组件） | `UGameplayStateTreeBlueprintFunctionLibrary` |

### 事件

| 事件 | 说明 | 所在类 |
|---|---|---|
| `OnStateTreeRunStatusChanged` | StateTree 运行状态变化时触发 | `UStateTreeComponent` |

### 使用示例（蓝图描述）

**示例 1：在 AI 角色上使用 StateTree**

1. 打开你的 AIController 蓝图
2. 添加组件 → 搜索 `State Tree AI Component`
3. 在组件的 Details 面板中，设置 `State Tree Ref` 为你创建的 StateTree 资产
4. 确保 `Start Logic Automatically` 勾选（默认勾选），AI 开始执行时 StateTree 自动运行

**示例 2：蓝图中动态启动 StateTree**

1. 使用 `RunStateTree` 节点，传入目标 Actor 和 StateTree 资产
2. 该函数会自动查找或创建 `UStateTreeComponent`，设置资产并启动
3. 返回 bool 表示是否成功启动

**示例 3：向运行中的 StateTree 发送事件**

1. 获取 Actor 上的 `StateTreeComponent` 引用
2. 调用 `Send State Tree Event`，传入 `GameplayTag` 和可选的 Payload
3. StateTree 中配置了对应事件触发器的 State 会被激活

## C++ 用法

### 头文件引入

```cpp
#include "Components/StateTreeComponent.h"
#include "Components/StateTreeAIComponent.h"
#include "Components/StateTreeComponentSchema.h"
#include "Components/StateTreeAIComponentSchema.h"
#include "Tasks/StateTreeMoveToTask.h"
#include "Tasks/StateTreeRunEnvQueryTask.h"
#include "BehaviorTree/Tasks/BTTask_RunStateTree.h"
```

### 基本用法：自定义 StateTree Component

`UStateTreeComponent` 继承自 `UBrainComponent`，可以被继承以自定义上下文数据收集逻辑。

```cpp
// 源码：Components/StateTreeComponent.h
// UStateTreeComponent 关键成员：

// 设置 StateTree（运行中不可更改）
void SetStateTree(UStateTree* StateTree);
void SetStateTreeReference(FStateTreeReference StateTreeReference);

// 链接 StateTree 覆盖
void AddLinkedStateTreeOverrides(const FGameplayTag StateTag, FStateTreeReference StateTreeReference);
void RemoveLinkedStateTreeOverrides(const FGameplayTag StateTag);

// 控制逻辑
void SetStartLogicAutomatically(bool bInStartLogicAutomatically);
void SendStateTreeEvent(const FGameplayTag Tag, const FConstStructView Payload, const FName Origin);

// 查询状态
EStateTreeRunStatus GetStateTreeRunStatus() const;

// 状态变化委托
FStateTreeRunStatusChanged OnStateTreeRunStatusChanged;
```

### 进阶用法：Schema 与外部数据

Schema 定义了 StateTree 能访问的上下文。`UStateTreeComponentSchema` 提供 Actor 上下文；`UStateTreeAIComponentSchema` 额外提供 AIController 上下文，并将 Actor 默认绑定到受控 Pawn。

```cpp
// 源码：Components/StateTreeComponentSchema.cpp
// CollectExternalData 自动解析以下类型的外部数据：
// - AActor 子类 → Owner Actor（AI 场景下为 Pawn）
// - UActorComponent 子类 → Actor 上的组件
// - UWorldSubsystem 子类 → 世界子系统
// - APawn 子类 → 受控 Pawn
// - AAIController 子类 → AI 控制器

// 可以通过继承 Schema 自定义上下文数据：
// override SetContextData() 来注入自定义数据
```

### 进阶用法：行为树中嵌入 StateTree

```cpp
// 源码：BehaviorTree/Tasks/BTTask_RunStateTree.h
// UBTTask_RunStateTree 在行为树中执行 StateTree
// 使用 StateTreeAIComponentSchema，保证 AIController 可用

// 关键属性：
// StateTreeRef - 要执行的 StateTree
// Interval - 更新间隔（默认 0.01s）
// RandomDeviation - 随机偏差

// 源码：BehaviorTree/Tasks/BTTask_RunDynamicStateTree.h
// UBTTask_RunDynamicStateTree 允许运行时动态设置 StateTree
// 通过 InjectionTag 标识，运行时调用 SetDynamicStateTree() 注入
```

### 进阶用法：自定义 AI Task

```cpp
// 源码：Tasks/StateTreeAITask.h
// AI Task 基类层次：
// FStateTreeTaskBase
//   └─ FStateTreeAITaskBase          (AI 专用基类)
//       └─ FStateTreeAIActionTaskBase (物理动作基类)
//           └─ FStateTreeMoveToTask   (移动任务)

// 自定义 AI Task 只需继承 FStateTreeAITaskBase
// 实现 EnterState / Tick / ExitState
// 需要使用 StateTreeAIComponentSchema 的 StateTree 才能使用
```

## Demo 示例

### 最小示例：C++ 中为 Actor 添加 StateTree Component

**Build.cs 依赖：**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "GameplayStateTreeModule",
    "StateTreeModule",
    "AIModule"  // 如果使用 AI 功能
});
```

**MyAIController.h：**
```cpp
#pragma once

#include "AIController.h"
#include "MyAIController.generated.h"

class UStateTreeAIComponent;

UCLASS()
class AMyAIController : public AAIController
{
    GENERATED_BODY()

public:
    AMyAIController();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UStateTreeAIComponent> StateTreeComponent;
};
```

**MyAIController.cpp：**
```cpp
#include "MyAIController.h"
#include "Components/StateTreeAIComponent.h"

AMyAIController::AMyAIController()
{
    // 创建 StateTree AI 组件
    StateTreeComponent = CreateDefaultSubobject<UStateTreeAIComponent>(TEXT("StateTreeComponent"));
    // StateTree 在 Details 面板中设置，或通过代码设置：
    // StateTreeComponent->SetStateTree(MyStateTreeAsset);
}
```

### 动态 StateTree 注入示例

```cpp
// 在任意位置，通过 GameplayTag 注入 StateTree 到行为树
FStateTreeReference NewRef;
NewRef.SetStateTree(MyStateTreeAsset);

UBTTask_RunDynamicStateTree::SetDynamicStateTree(
    *BehaviorTreeComponent,
    FGameplayTag::RequestGameplayTag(TEXT("AI.Combat")),
    NewRef,
    FSetContextDataDelegate(),  // 可选的上下文设置委托
    0.1f,   // interval
    0.02f   // random deviation
);
```

## 模块依赖

从 `GameplayStateTreeModule.Build.cs` 的 `PublicDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `AIModule` | AI 控制器、行为树、AI Task 框架 |
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Actor、Component 等） |
| `GameplayTags` | GameplayTag 系统，用于事件和动态 StateTree 注入 |
| `GameplayTasks` | GameplayTask 框架（AITask_MoveTo 依赖） |
| `NavigationSystem` | 导航系统（MoveTo 任务依赖） |
| `PropertyBindingUtils` | StateTree 属性绑定工具 |
| `StateTreeModule` | StateTree 核心引擎 |

插件还依赖另一个插件：`StateTree`。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-09-23 | `adc3fb1` | 使用只读上下文验证 StateTree 引用，避免在验证阶段修改实例数据 |
| 2025-09-03 | `f226185` | 为 `FContextDataSetter` 添加 `UE_API` 导出宏，使其可被外部模块使用 |
| 2025-08-26 | `e772ef1` | 修复 StateTreeComponent 在重入场景下 running 标志未正确设置的问题 |

### 维护评价

- **创建时间**：2022 年 5 月，约 4 年历史
- **最后更新**：2025 年 9 月，距今约 8 个月，有实质性 bug 修复和 API 改进
- **活跃度**：活跃维护中。最近的更新集中在稳定性和 API 公开性上，说明该插件已进入成熟期
- **默认启用**：否（`EnabledByDefault=false`），需要在项目设置中手动启用
- **推荐程度**：**推荐使用**。这是 UE5 官方的 StateTree 运行时集成方案，是使用 StateTree 做 AI/游戏逻辑的必经之路。如果你要用 StateTree，就必须用这个插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameplayStateTree)
- [StateTree 核心插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/StateTree)
- 官方文档（无，.uplugin 中 DocsURL 为空）
