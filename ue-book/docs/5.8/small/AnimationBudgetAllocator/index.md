# Animation Budget Allocator

> Constrains the time taken for animation to run by dynamically throttling skeletal mesh component ticking.

| 属性 | 值 |
|---|---|
| 中文名 | 动画预算分配器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AnimationBudgetAllocator` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-11-15 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AnimationBudgetAllocator) | |

## 用途

此插件的核心作用是解决大量角色骨骼动画同时更新时可能引发的性能问题。在需要大量动画角色的游戏场景中（如开放世界、MMORPG），如果所有角色的动画都以完整帧率运行，可能会导致 CPU 过载和帧率下降。

动画预算分配器通过在运行时动态“节流”骨骼网格组件的动画更新来解决这个问题。它设定了一个动画更新的总时间“预算”（例如每帧 1 毫秒）。系统会根据每个组件的“重要性”（Significance，通常基于与玩家的距离、是否在屏幕内等因素）和当前预算使用情况，动态调整组件的动画更新频率（Tick Rate），或者完全跳过某些低重要性组件的更新。当预算超支时，它甚至可以对某些组件进行“插值”（Interpolate）或执行“减少工作”（Reduced Work）的操作（例如仅更新根骨骼），以在保证基本视觉效果的前提下显著降低性能开销。

## 使用场景

- 你的游戏拥有大量 NPC 或敌人，导致屏幕上有大量骨骼动画角色。
- 你正在开发开放世界游戏，需要在远处渲染大量角色，但希望动态控制其动画质量以节省性能。
- 你遇到了因动画更新导致的 CPU 性能瓶颈，需要一种精细的、动态的动画 LOD（Level of Detail）系统。

## 蓝图用法

蓝图主要通过 `UAnimationBudgetBlueprintLibrary` 提供的静态函数来控制整个系统。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Enable Animation Budget` | 启用或禁用全局动画预算系统。注意：此设置会被全局 CVar `AnimationBudget.Enabled` 覆盖。 | `UAnimationBudgetBlueprintLibrary` |
| `Set Animation Budget Parameters` | 动态设置动画预算系统的各项参数，如总预算、降级策略等。 | `UAnimationBudgetBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **初始化**：在你的游戏模式（GameMode）的 `BeginPlay` 事件中，连接一个 `Enable Animation Budget` 节点，并将 `bEnabled` 设置为 `true`。
2.  **配置参数**：紧接着，使用 `Set Animation Budget Parameters` 节点，并传入一个配置好的 `FAnimationBudgetAllocatorParameters` 结构体（通过 `Make AnimationBudgetAllocatorParameters` 节点创建）。你可以调整 `BudgetInMs`（总预算毫秒数）、`MinQuality`（最低质量）等参数。
3.  **组件配置**：对于你希望受预算系统管理的骨骼网格组件，将其替换为 `USkeletalMeshComponentBudgeted`。在该组件的细节面板中，勾选 `Auto Register With Budget Allocator` 和 `Auto Calculate Significance`。

## C++ 用法

### 头文件引入

```cpp
#include "AnimationBudgetAllocator/Public/IAnimationBudgetAllocator.h"
#include "AnimationBudgetAllocator/Public/SkeletalMeshComponentBudgeted.h"
```

### 基本用法

获取当前世界的预算分配器并注册组件。
```cpp
// 来自文档模板中的 IAnimationBudgetAllocator 接口描述
void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 获取当前世界的动画预算分配器
    IAnimationBudgetAllocator* BudgetAllocator = IAnimationBudgetAllocator::Get(GetWorld());
    if (BudgetAllocator && MyBudgetedSkeletalMeshComponent)
    {
        // 注册组件，使其受预算系统管理
        BudgetAllocator->RegisterComponent(MyBudgetedSkeletalMeshComponent);
        
        // 设置组件的重要性和行为标志
        // bNeverSkip: true=从不跳过更新（如玩家角色）
        // bTickEvenIfNotRendered: true=即使不在屏幕上也尝试更新（如有重要音频通知的网格）
        // bAllowReducedWork: true=允许在超支时执行减少工作的操作
        // bForceInterpolate: true=强制使用插值
        BudgetAllocator->SetComponentSignificance(MyBudgetedSkeletalMeshComponent, 0.8f, false, false, true, false);
    }
}
```

### 进阶用法

自定义重要性计算和处理减少工作的委托。
```cpp
// 来自文档模板中的 USkeletalMeshComponentBudgeted 和 FAnimationBudgetAllocatorParameters
void AMyActor::SetupBudgetedComponent()
{
    // 禁用自动计算重要性，改为手动推送
    MyBudgetedComponent->SetAutoCalculateSignificance(false);
    
    // 绑定“减少工作”的委托。当预算超支时，系统会调用此委托，通知组件减少其工作量。
    MyBudgetedComponent->OnReduceWork().BindLambda([this](USkeletalMeshComponent* Component, bool bReduce)
    {
        if (bReduce)
        {
            // 执行减少工作的逻辑，例如禁用某些非关键的动画通知、简化物理模拟等
            UE_LOG(LogTemp, Log, TEXT("Reducing work for component %s"), *Component->GetName());
        }
        else
        {
            // 恢复完整工作
            UE_LOG(LogTemp, Log, TEXT("Restoring full work for component %s"), *Component->GetName());
        }
    });

    // 自定义重要性计算委托（静态，对所有组件生效）
    USkeletalMeshComponentBudgeted::OnCalculateSignificance().BindLambda(
        [](USkeletalMeshComponentBudgeted* Component, float& OutSignificance, bool& bOutNeverSkip, bool& bOutTickEvenIfNotRendered)
        {
            // 实现你自己的重要性计算逻辑，例如结合距离、视野、游戏状态等
            float DistanceToCamera = FVector::Distance(Component->GetComponentLocation(), GEngine->GetMainSceneComponentLocation(/*...*/));
            OutSignificance = FMath::Clamp(1.0f - (DistanceToCamera / 10000.0f), 0.0f, 1.0f);
            bOutNeverSkip = (OutSignificance > 0.9f); // 非常近的组件永不跳过
        });

    // 动态更新系统参数
    FAnimationBudgetAllocatorParameters Params;
    Params.BudgetInMs = 2.0f; // 设置 2 毫秒的动画预算
    Params.MaxTickRate = 15;  // 限制最大 Tick 频率为 15Hz
    // ... 设置其他参数 ...
    
    IAnimationBudgetAllocator* Allocator = IAnimationBudgetAllocator::Get(GetWorld());
    if (Allocator)
    {
        Allocator->SetParameters(Params);
    }
}
```

## Demo 示例

一个可编译的最小示例，展示如何创建一个受预算管理的角色组件并设置基本参数。

**MyBudgetedCharacter.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyBudgetedCharacter.generated.h"

class USkeletalMeshComponentBudgeted;
struct FAnimationBudgetAllocatorParameters;

UCLASS()
class AMyBudgetedCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyBudgetedCharacter();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation Budget")
    USkeletalMeshComponentBudgeted* BudgetedMeshComponent;
};
```

**MyBudgetedCharacter.cpp**
```cpp
#include "MyBudgetedCharacter.h"
#include "AnimationBudgetAllocator/Public/SkeletalMeshComponentBudgeted.h"
#include "AnimationBudgetAllocator/Public/IAnimationBudgetAllocator.h"
#include "AnimationBudgetAllocator/Public/AnimationBudgetAllocatorParameters.h"

AMyBudgetedCharacter::AMyBudgetedCharacter()
{
    // 用预算管理的骨骼网格组件替换默认的骨骼网格组件
    BudgetedMeshComponent = CreateDefaultSubobject<USkeletalMeshComponentBudgeted>(TEXT("BudgetedMesh"));
    if (GetMesh() && GetMesh()->GetSkeletalMeshAsset())
    {
        BudgetedMeshComponent->SetSkeletalMesh(GetMesh()->GetSkeletalMeshAsset());
    }
    BudgetedMeshComponent->SetupAttachment(RootComponent);
    
    // 关键设置：允许自动注册和自动计算重要性
    BudgetedMeshComponent->SetAutoRegisterWithBudgetAllocator(true);
    BudgetedMeshComponent->SetAutoCalculateSignificance(true);
}

void AMyBudgetedCharacter::BeginPlay()
{
    Super::BeginPlay();

    // 手动获取预算分配器（虽然组件设置了自动注册，但我们可以手动设置参数）
    IAnimationBudgetAllocator* BudgetAllocator = IAnimationBudgetAllocator::Get(GetWorld());
    if (BudgetAllocator)
    {
        // 设置一个更严格的预算，例如 0.5 毫秒
        FAnimationBudgetAllocatorParameters TightBudget;
        TightBudget.BudgetInMs = 0.5f;
        TightBudget.MinQuality = 0.2f; // 允许最低降至 20% 的组件被更新
        BudgetAllocator->SetParameters(TightBudget);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 用于游戏玩法标签系统（通过依赖链引入） |

无特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件内的日志输出迁移到新的 UE_LOGF 宏。 |
| 2026-02-12 | `3c1a3763` | Changes to the anim budgeter: | 对动画预算分配器进行了更新。 |
| 2026-01-26 | `6edd6481` | Optional changes to AnimationBudgetAllocator (disabled by default): | 对动画预算分配器进行了可选的改动（默认禁用）。 |
| 2025-12-01 | `c188d850` | Resubmit Of Anim Info Updates | 重新提交了动画信息更新。 |
| 2025-11-12 | `fd32115b` | [Backout] 46898981 | 回滚了之前的更改。 |

### 维护评价

- **创建时间**：该插件创建于 2018 年，是一个相当成熟的模块。
- **活跃度**：最近提交记录显示，直到 2026 年仍有维护活动，主要是代码质量改进（日志迁移）和一些内部优化。
- **核心功能**：该插件自创建以来核心逻辑稳定，主要用于《堡垒之夜》等需要管理大量角色动画的 Epic 自研项目中。
- **当前状态**：虽然仍在维护，但最近的更新多为小幅度的调整或内部优化，而非重大功能增加。这表明插件功能已相对完备和稳定。
- **建议**：**谨慎使用**。对于新项目，首先评估虚幻引擎内建的动画优化方案（如 Animation Budgeting in World Partition、Nanite for Skeletal Meshes 等）是否能满足需求。如果项目规模巨大且需要精细的动态控制，此插件是一个强大的工具，但请注意它 `EnabledByDefault=false`，需要手动集成和测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AnimationBudgetAllocator)