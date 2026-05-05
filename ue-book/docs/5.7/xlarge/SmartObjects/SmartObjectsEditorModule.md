# Smart Objects

> Support for ambient life populating the game world

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `SmartObjectsModule` (Runtime), `SmartObjectsEditorModule` (Runtime), `SmartObjectsTestSuite` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SmartObjects) | |

## 用途

Smart Objects 插件为游戏世界中的“智能对象”提供了一套完整的运行时和编辑器框架。它解决的核心问题是：**如何让游戏中的 AI 角色（或玩家）能够发现、评估并使用散布在世界中的各种交互点（如椅子、武器架、工作台、载具座位等）**。

该插件不仅仅是一个简单的交互系统，它提供了一个数据驱动的、可扩展的架构，用于定义：
1.  **智能对象定义 (Smart Object Definition)**：描述一个交互点包含哪些“插槽”（Slot），每个插槽可以容纳什么类型的角色，以及交互时需要满足的条件。
2.  **智能对象集合 (Smart Object Collection)**：在世界中收集和管理所有智能对象组件的实例，便于 AI 高效查询。
3.  **运行时查询与占用**：AI 可以查询附近可用的智能对象，并“占用”一个插槽进行交互，防止多个角色同时使用同一个位置。

其目标是支持“环境生命”（Ambient Life），让 NPC 能够自主地在世界中寻找并使用合适的设施，从而增强世界的沉浸感和动态性。

## 使用场景

-   **开放世界游戏**：NPC 需要自主寻找座位、床铺、工作台、商店柜台等。
-   **潜行或战术游戏**：敌人需要寻找掩体、武器补给点或警戒位置。
-   **模拟经营游戏**：顾客需要寻找空闲的收银台、座位或娱乐设施。
-   **任何需要 AI 与复杂环境进行结构化交互的场景**。

## 蓝图用法

Smart Objects 的运行时蓝图 API 主要集中在 `SmartObjectsModule` 中，用于查询和操作智能对象。编辑器模块 (`SmartObjectsEditorModule`) 提供资产编辑和世界构建工具。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Find Smart Objects` | 在指定区域内查找可用的智能对象。 | `USmartObjectSubsystem` |
| `Use Smart Object` | 让一个 Actor 尝试使用一个智能对象的特定插槽。 | `USmartObjectSubsystem` |
| `Release Smart Object` | 释放一个被占用的智能对象插槽。 | `USmartObjectSubsystem` |
| `Get Smart Object Definition` | 获取一个智能对象组件的定义数据。 | `USmartObjectComponent` |

### 使用示例（蓝图描述）

1.  **AI 寻找座位**：
    -   在 AI 的行为树或蓝图中，调用 `Find Smart Objects` 节点。
    -   设置查询参数，如 `SmartObjectTag` (例如 “Seat”)、`QueryRadius` 和 `Actor` (AI自身)。
    -   从返回的结果中选择一个合适的智能对象。
    -   调用 `Use Smart Object` 节点，传入选中的智能对象和 AI 角色。
    -   AI 移动到目标位置并执行交互（如坐下动画）。
    -   交互完成后，调用 `Release Smart Object`。

2.  **放置智能对象**：
    -   在场景中放置一个 `SmartObjectComponent`。
    -   在其细节面板中，指定一个 `SmartObjectDefinition` 资产。
    -   该定义资产在专用的 Smart Object 编辑器中创建，用于配置插槽、条件和行为。

## C++ 用法

### 头文件引入

```cpp
// 运行时模块 - 用于查询和操作智能对象
#include "SmartObjectSubsystem.h"
#include "SmartObjectComponent.h"
#include "SmartObjectDefinition.h"

// 编辑器模块 - 用于自定义编辑器工具或构建流程
#include "SmartObjectsEditorModule.h"
```

### 基本用法

以下代码展示了如何在 C++ 中查询并使用一个智能对象。

```cpp
// 假设在某个 AAIController 或类似类中
void AMyAIController::FindAndUseSmartObject()
{
    // 1. 获取世界中的智能对象子系统
    USmartObjectSubsystem* SmartObjectSubsystem = GetWorld()->GetSubsystem<USmartObjectSubsystem>();
    if (!SmartObjectSubsystem)
    {
        return;
    }

    // 2. 定义查询参数
    FSmartObjectRequest Request;
    Request.Filter.SmartObjectTag = FGameplayTag::RequestGameplayTag(TEXT("SmartObject.Seat"));
    Request.Filter.bShouldCheckCollision = true;
    Request.QueryRadius = 1000.0f;
    Request.Requestor = GetPawn();

    // 3. 执行查询
    FSmartObjectRequestResult Result;
    if (SmartObjectSubsystem->FindSmartObject(Request, Result))
    {
        // 4. 使用找到的智能对象
        FSmartObjectClaimHandle ClaimHandle = SmartObjectSubsystem->ClaimSmartObject(Result.SmartObjectHandle, Result.SlotHandle, GetPawn());
        if (ClaimHandle.IsValid())
        {
            // 开始交互逻辑，例如移动到位置并播放动画
            StartInteractionWithSmartObject(ClaimHandle);
        }
    }
}

void AMyAIController::ReleaseCurrentSmartObject(FSmartObjectClaimHandle ClaimHandle)
{
    USmartObjectSubsystem* SmartObjectSubsystem = GetWorld()->GetSubsystem<USmartObjectSubsystem>();
    if (SmartObjectSubsystem && ClaimHandle.IsValid())
    {
        SmartObjectSubsystem->ReleaseSmartObjectClaim(ClaimHandle);
    }
}
```

### 进阶用法

可以结合 Gameplay Ability System (GAS) 或自定义行为树任务来使用 Smart Objects，实现更复杂的 AI 行为。

```cpp
// 自定义行为树任务节点
UCLASS()
class UBTTask_FindAndUseSmartObject : public UBTTaskNode
{
    GENERATED_BODY()

    virtual EBTNodeResult::Type ExecuteTask(UBehaviorTreeComponent& OwnerComp, uint8* NodeMemory) override
    {
        AAIController* Controller = OwnerComp.GetAIOwner();
        if (!Controller) return EBTNodeResult::Failed;

        // ... 类似上面的查询逻辑 ...
        // 查询成功后，将 ClaimHandle 存储在黑板中，并返回 InProgress
        // 在任务结束或中断时，调用 ReleaseSmartObjectClaim
    }
};
```

## Demo 示例

一个最小化的 C++ 示例，展示如何创建一个可交互的智能对象组件。

```cpp
// MyInteractiveActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "SmartObjectComponent.h"
#include "MyInteractiveActor.generated.h"

UCLASS()
class AMyInteractiveActor : public AActor
{
    GENERATED_BODY()

public:
    AMyInteractiveActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "SmartObject")
    TObjectPtr<USmartObjectComponent> SmartObjectComponent;

    // 可以添加其他组件，如静态网格体
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UStaticMeshComponent> MeshComponent;
};
```

```cpp
// MyInteractiveActor.cpp
#include "MyInteractiveActor.h"
#include "SmartObjectDefinition.h"

AMyInteractiveActor::AMyInteractiveActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建根组件和网格体
    MeshComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;

    // 创建并附加智能对象组件
    SmartObjectComponent = CreateDefaultSubobject<USmartObjectComponent>(TEXT("SmartObject"));
    SmartObjectComponent->SetupAttachment(RootComponent);

    // 在编辑器中，你需要为这个组件的 Definition 属性指定一个 USmartObjectDefinition 资产。
    // 该资产定义了交互的插槽、条件和行为。
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 用于通过标签系统对智能对象进行分类和过滤。 |
| `GameplayTasks` | 可能用于实现与智能对象交互相关的异步任务。 |
| `AIModule` | 核心 AI 框架，Smart Objects 通常与 AI 控制器和行为树结合使用。 |
| `EditorFramework` | (编辑器模块依赖) 提供编辑器框架支持。 |
| `UnrealEd` | (编辑器模块依赖) 提供 Unreal 编辑器核心功能，用于资产编辑器和构建工具。 |

## 维护状态

### 近期更新

-   `a2e75189887d` Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup using LyraEditor win64 development as target)
-   `2739c3d30ebc` Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n
-   `f57e1f6aa544` Remove legacy viewport toolbar usage in viewports with explicit support for the new toolbar system.

### 维护评价

Smart Objects 插件创建于 2021 年，是一个相对较新的系统。从最近的提交记录来看，**近期更新主要是代码维护性和编译兼容性修复**（如添加内联生成宏、更新头文件导出宏、移除旧版视口工具栏），**没有发现重大的新功能添加或架构变更**。

该插件默认未启用 (`EnabledByDefault: false`)，表明它可能仍处于积极开发或需要用户主动集成的阶段。考虑到其解决的核心问题（AI 环境交互）在现代游戏开发中非常重要，且 Epic 官方在 Lyra 等示例项目中使用了它，可以认为它是一个**有潜力但需要关注后续发展的功能**。

**建议**：如果你的项目需要复杂的 AI 环境交互，可以评估并使用此插件。但需注意，由于默认未启用且近期无重大功能更新，在集成前应充分测试其稳定性和是否满足项目需求。建议关注后续版本更新。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SmartObjects)
-   [官方文档]() (暂无)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SmartObjects/Source/SmartObjectsTestSuite)