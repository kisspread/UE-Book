# Smart Objects

> Support for ambient life populating the game world

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据资产、行为定义） |
| 模块 | `SmartObjectsModule` (Runtime), `SmartObjectsEditorModule` (Runtime), `SmartObjectsTestSuite` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SmartObjects) | |

> ⚠️ **需要手动启用**：此插件默认未启用（`EnabledByDefault: false`），需在项目设置中手动开启。

---

## 用途

Smart Objects 插件提供了一套**结构化的游戏世界交互框架**，用于管理 AI 角色与游戏世界中可交互对象之间的关系。

核心解决的问题：在开放世界或复杂场景中，多个 AI 角色需要发现、预约、使用和释放世界中的交互点（如长椅、门、车辆、工作台等），同时避免多个角色争抢同一个交互点。本质上，这是一个**交互点预约管理系统**。

具体功能包括：

- **定义交互点**：通过 `USmartObjectDefinition` 数据资产定义智能对象的槽位（Slots）、行为、条件和注解
- **空间索引**：使用哈希网格（Hash Grid）或八叉树（Octree）高效查找附近的智能对象
- **预约与占用**：支持优先级驱动的 Claim → Use → Release 生命周期
- **条件验证**：通过 World Conditions、标签查询和碰撞检测控制槽位可用性
- **入口注解**：定义槽位的进入/退出位置，支持导航验证
- **EQS 集成**：与环境查询系统集成，供行为树驱动的 AI 使用
- **属性绑定**：支持参数化定义，同一定义可在不同实例上表现不同

## 使用场景

- **开放世界游戏**：NPC 自动寻找长椅坐下、在摊位前排队、使用健身器材等
- **AI 日程系统**：NPC 根据时间/状态寻找合适的交互点（去厨房做饭、去床铺睡觉）
- **多 Agent 竞争**：多个 AI 角色同时寻找有限的交互资源，系统自动处理优先级和冲突
- **行为树驱动的 AI**：通过 EQS 查询 + Blackboard 集成，在行为树中无缝使用
- **需要参数化的交互**：同一类型的智能对象定义，通过参数在不同实例上表现不同（如不同难度的工作台）

## 核心概念

### 智能对象层次结构

```
USmartObjectDefinition (数据资产)
├── 参数 (Parameters) — 可绑定的属性
├── 标签 (Activity Tags, User Tags)
├── World Conditions (可用性条件)
├── 行为定义 (Behavior Definitions)
└── Slots (槽位)
    ├── 槽位标签
    ├── 槽位条件
    └── Annotations (注解)
        ├── Entrance (入口位置)
        ├── Slot User Collision (碰撞检测)
        └── Slot Link (槽位链接)
```

### 运行时生命周期

```
1. 注册 (Register)     → SmartObjectComponent 注册到 Subsystem
2. 发现 (Find)         → 通过空间查询找到可用的 Smart Object
3. 预约 (Claim)        → 获取 ClaimHandle，槽位状态变为 Claimed
4. 使用 (Use)          → 开始交互，槽位状态变为 Occupied
5. 释放 (Release)      → 交互完成，槽位状态恢复为 Free
```

### 关键句柄类型

| 句柄 | 说明 |
|---|---|
| `FSmartObjectHandle` | 智能对象实例的唯一标识 |
| `FSmartObjectSlotHandle` | 槽位的唯一标识 |
| `FSmartObjectClaimHandle` | 预约句柄（对象 + 槽位 + 用户） |
| `FSmartObjectUserHandle` | 用户标识 |

### 槽位状态

| 状态 | 说明 |
|---|---|
| `Free` | 可用，可被预约 |
| `Claimed` | 已预约但交互尚未开始 |
| `Occupied` | 交互进行中 |

## 蓝图用法

### 核心节点

#### 智能对象管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Smart Object` | 将 Actor 的智能对象添加到模拟系统 | `USmartObjectBlueprintFunctionLibrary` |
| `Remove Smart Object` | 从模拟系统移除 Actor 的智能对象 | `USmartObjectBlueprintFunctionLibrary` |
| `Add Or Remove Smart Object` | 根据布尔值添加或移除 | `USmartObjectBlueprintFunctionLibrary` |
| `Add Multiple Smart Objects` | 批量添加多个 Actor 的智能对象 | `USmartObjectBlueprintFunctionLibrary` |
| `Remove Multiple Smart Objects` | 批量移除多个 Actor 的智能对象 | `USmartObjectBlueprintFunctionLibrary` |

#### 预约句柄操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is Valid (Smart Object Claim Handle)` | 检查预约句柄是否有效 | `USmartObjectBlueprintFunctionLibrary` |
| `Smart Object Claim Handle_Invalid` | 返回无效的预约句柄 | `USmartObjectBlueprintFunctionLibrary` |
| `Get Value As SO Claim Handle` | 从 Blackboard 获取预约句柄 | `USmartObjectBlueprintFunctionLibrary` |
| `Set Value As SO Claim Handle` | 将预约句柄写入 Blackboard | `USmartObjectBlueprintFunctionLibrary` |

#### 组件访问

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Definition` | 获取智能对象定义（含参数） | `USmartObjectComponent` |
| `Set Definition` | 设置智能对象定义 | `USmartObjectComponent` |
| `Get Validation Filter` | 获取用户的验证过滤器 | `USmartObjectUserComponent` |

### 使用示例（蓝图描述）

**场景：AI 角色寻找并使用附近的长椅**

1. **世界中放置长椅 Actor**：添加 `SmartObjectComponent`，设置 `SmartObjectDefinition`（定义一个"坐下"槽位，带 Entrance 注解）
2. **AI 角色添加 `SmartObjectUserComponent`**
3. **在行为树中**：
   - 使用 EQS Generator "Smart Objects" 查询附近可用的智能对象
   - 获取查询结果中的 `SmartObjectHandle` 和 `SlotHandle`
   - 调用 Subsystem 的 `ClaimSmartObject` 节点预约槽位
   - 将 `ClaimHandle` 存入 Blackboard（使用 `SO Claim Handle` 键类型）
   - 导航到入口位置
   - 调用 `UseSmartObject` 开始交互
   - 交互完成后调用 `ReleaseSmartObject` 释放

## C++ 用法

### 头文件引入

```cpp
#include "SmartObjectSubsystem.h"
#include "SmartObjectComponent.h"
#include "SmartObjectDefinition.h"
#include "SmartObjectUserComponent.h"
#include "SmartObjectRequestTypes.h"
#include "SmartObjectRuntime.h"
```

### 基本用法 — 查询并预约智能对象

```cpp
// 获取 SmartObject 子系统
USmartObjectSubsystem* Subsystem = GetWorld()->GetSubsystem<USmartObjectSubsystem>();

// 构建查询请求
FSmartObjectRequest Request;
Request.QueryBox = FBox(MyLocation - FVector(500.f), MyLocation + FVector(500.f));
Request.Filter.UserTags = MyUserTags;
Request.Filter.ActivityRequirements = FGameplayTagQuery::MakeQuery_MatchNoTags(); // 无特殊要求
Request.Filter.bShouldEvaluateConditions = true;

// 执行查询
TArray<FSmartObjectRequestResult> Results;
if (Subsystem->FindSmartObjects(Request, Results) && Results.Num() > 0)
{
    const FSmartObjectRequestResult& BestResult = Results[0];
    
    // 预约槽位
    FSmartObjectClaimHandle ClaimHandle = Subsystem->ClaimSmartObject(
        BestResult.SmartObjectHandle, 
        BestResult.SlotHandle, 
        UserActor
    );
    
    if (ClaimHandle.IsValid())
    {
        // 获取入口位置用于导航
        FSmartObjectSlotEntranceHandle EntranceHandle;
        Subsystem->GetEntranceHandle(ClaimHandle, EntranceHandle);
        FVector EntranceLocation = Subsystem->GetSlotEntranceLocation(EntranceHandle);
        
        // 导航到入口位置后，开始交互
        Subsystem->UseSmartObject(ClaimHandle);
        
        // ... 执行交互逻辑 ...
        
        // 交互完成，释放
        Subsystem->ReleaseSmartObject(ClaimHandle);
    }
}
```

### 进阶用法 — 自定义 World Condition

```cpp
// 自定义条件：检查用户是否持有特定物品
USTRUCT(meta=(DisplayName="Has Required Item"))
struct FSmartObjectWorldConditionHasItem : public FSmartObjectWorldConditionBase
{
    GENERATED_BODY()

    using FStateType = FSmartObjectWorldConditionHasItemState;

protected:
    virtual bool Initialize(const UWorldConditionSchema& Schema) override;
    virtual FWorldConditionResult IsTrue(const FWorldConditionContext& Context) const override;

    FWorldConditionContextDataRef UserActorRef;

public:
    UPROPERTY(EditAnywhere, Category="Default")
    FGameplayTag RequiredItemTag;
};
```

### 进阶用法 — 自定义 Behavior Definition

```cpp
// 自定义行为定义，绑定到特定的交互逻辑
UCLASS()
class USmartObjectBehaviorDefinition_Sit : public USmartObjectBehaviorDefinition
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category="Sit")
    UAnimMontage* SitDownMontage;

    UPROPERTY(EditAnywhere, Category="Sit")
    UAnimMontage* StandUpMontage;

    UPROPERTY(EditAnywhere, Category="Sit")
    float SitDuration = 0.f;
};
```

## Demo 示例

### 智能对象 Actor

```cpp
// SmartObjectBench.h
#pragma once

#include "GameFramework/Actor.h"
#include "SmartObjectBench.generated.h"

class USmartObjectComponent;

UCLASS()
class ASmartObjectBench : public AActor
{
    GENERATED_BODY()

public:
    ASmartObjectBench();

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "SmartObject")
    TObjectPtr<USmartObjectComponent> SmartObjectComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UStaticMeshComponent> MeshComponent;
};
```

```cpp
// SmartObjectBench.cpp
#include "SmartObjectBench.h"
#include "SmartObjectComponent.h"
#include "Components/StaticMeshComponent.h"

ASmartObjectBench::ASmartObjectBench()
{
    MeshComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;

    SmartObjectComponent = CreateDefaultSubobject<USmartObjectComponent>(TEXT("SmartObject"));
    SmartObjectComponent->SetupAttachment(RootComponent);
}
```

### AI 角色使用智能对象

```cpp
// SmartObjectUser.h
#pragma once

#include "GameFramework/Character.h"
#include "SmartObjectUser.generated.h"

class USmartObjectUserComponent;

UCLASS()
class ASmartObjectUser : public ACharacter
{
    GENERATED_BODY()

public:
    ASmartObjectUser();

    UFUNCTION(BlueprintCallable, Category = "SmartObject")
    bool FindAndUseNearbySmartObject();

    UFUNCTION(BlueprintCallable, Category = "SmartObject")
    void StopUsingSmartObject();

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "SmartObject")
    TObjectPtr<USmartObjectUserComponent> SmartObjectUserComponent;

private:
    FSmartObjectClaimHandle CurrentClaimHandle;
};
```

```cpp
// SmartObjectUser.cpp
#include "SmartObjectUser.h"
#include "SmartObjectUserComponent.h"
#include "SmartObjectSubsystem.h"
#include "SmartObjectRequestTypes.h"

ASmartObjectUser::ASmartObjectUser()
{
    SmartObjectUserComponent = CreateDefaultSubobject<USmartObjectUserComponent>(TEXT("SmartObjectUser"));
}

bool ASmartObjectUser::FindAndUseNearbySmartObject()
{
    USmartObjectSubsystem* Subsystem = GetWorld()->GetSubsystem<USmartObjectSubsystem>();
    if (!Subsystem) return false;

    // 在角色周围 1000 单位内查找
    const FVector Location = GetActorLocation();
    const float SearchRadius = 1000.f;
    
    FSmartObjectRequest Request;
    Request.QueryBox = FBox(Location - FVector(SearchRadius), Location + FVector(SearchRadius));
    Request.Filter.UserTags = FGameplayTagContainer();
    Request.Filter.bShouldEvaluateConditions = true;

    TArray<FSmartObjectRequestResult> Results;
    if (!Subsystem->FindSmartObjects(Request, Results) || Results.Num() == 0)
    {
        return false;
    }

    // 预约第一个可用结果
    CurrentClaimHandle = Subsystem->ClaimSmartObject(
        Results[0].SmartObjectHandle,
        Results[0].SlotHandle,
        this
    );

    if (CurrentClaimHandle.IsValid())
    {
        Subsystem->UseSmartObject(CurrentClaimHandle);
        return true;
    }

    return false;
}

void ASmartObjectUser::StopUsingSmartObject()
{
    if (CurrentClaimHandle.IsValid())
    {
        USmartObjectSubsystem* Subsystem = GetWorld()->GetSubsystem<USmartObjectSubsystem>();
        if (Subsystem)
        {
            Subsystem->ReleaseSmartObject(CurrentClaimHandle);
        }
        CurrentClaimHandle.Invalidate();
    }
}
```

## 子模块文档索引

本插件为 xlarge 规模（212 个源文件），按功能划分为以下子模块：

| 子模块 | 说明 | 关键类/文件 |
|---|---|---|
| **Core** | 子系统、组件、定义、运行时类型 | `SmartObjectSubsystem`, `SmartObjectComponent`, `SmartObjectDefinition`, `SmartObjectRuntime` |
| **Annotations** | 槽位注解（入口、碰撞、链接） | `SmartObjectSlotEntranceAnnotation`, `SmartObjectAnnotation_SlotUserCollision`, `SmartObjectSlotLinkAnnotation` |
| **World Conditions** | 可用性条件系统 | `SmartObjectWorldConditionBase`, `SmartObjectWorldConditionSchema`, 各种 TagQuery 条件 |
| **EQS Integration** | 环境查询系统集成 | `EnvQueryGenerator_SmartObjects`, `EnvQueryItemType_SmartObject` |
| **Spatial Partitioning** | 空间索引（哈希网格、八叉树） | `SmartObjectHashGrid`, `SmartObjectOctree` |
| **Property Binding** | 参数化定义与属性绑定 | `SmartObjectBindingCollection`, `SmartObjectDefinitionPropertyBinding` |
| **Debug Rendering** | 调试可视化 | `SmartObjectDebugSceneProxy`, `SmartObjectRenderingComponent`, `GameplayDebuggerCategory_SmartObject` |
| **Settings** | 插件设置 | `SmartObjectSettings` |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 标签系统（Activity Tags、User Tags、TagQuery） |
| `StructUtils` | FInstancedStruct、FStructView、FPropertyBag |
| `WorldConditions` | World Condition 框架（槽位可用性条件） |
| `AIModule` | EQS 集成（EnvQueryGenerator）、Blackboard 集成 |
| `NavigationSystem` | 导航查询（入口位置验证） |
| `PropertyBinding` | 属性绑定框架（参数化定义） |

## 维护状态

### 近期更新

```
- 44d2e9a4dabe [State Tree][Property Binding] Introduced output binding feature. Target property reversely bound to source property will write back to the source property instead of copying from the source property, at the end of each node processing scope(EnterState, Tick, ExitState). Property can only be reversely bound to state or global parameters. Only allow output property to be reversely bound as a clear UX to the user is being figured out.
- 429d4cdf005d [DebugDraw] fixed debug draw helper and updated SmartObject visualization to fix issues with scaled DPI
- 00424427aec8 [SmartObject] update bindings to refresh batches after removing some for specific targets #rb none
```

三条近期提交均涉及功能增强和 Bug 修复：属性绑定的输出绑定特性、调试绘制的 DPI 缩放修复、以及绑定刷新逻辑优化。

### 维护评价

- **活跃维护**：近期有实质性的功能更新（属性绑定新特性）和 Bug 修复
- **版本状态**：版本号仍为 0.1，表明 API 可能尚未完全稳定
- **默认未启用**：`EnabledByDefault: false`，说明 Epic 将其视为可选/实验性功能
- **持续演进**：从 2021 年创建至今，经历了多次重大重构（如 SmartObjectCollection 被标记为 Deprecated，替换为 SmartObjectPersistentCollection）
- **推荐使用**：✅ 推荐用于需要 AI 交互管理的项目，但需注意 API 可能随版本更新而变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SmartObjects)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SmartObjects/Source/SmartObjectsTestSuite)