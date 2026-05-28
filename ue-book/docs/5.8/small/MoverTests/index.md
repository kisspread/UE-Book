# MoverTests

> Series of test content for the Mover system.

| 属性 | 值 |
|---|---|
| 中文名 | Mover测试 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产、示例类） |
| 模块 | `MoverTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MoverTests) | |

## 用途

这是一个**纯测试插件**，其目的不是向最终用户或开发者提供功能，而是为 `Mover` 移动系统提供一系列自动化测试和验证内容。它包含了用于测试 Mover 系统核心功能（如自定义分层移动、网络同步、预测回滚等）的资产和 C++ 类。该插件的代码和资产主要服务于引擎开发团队，确保 Mover 系统的稳定性和正确性。

## 使用场景

- **Mover 系统开发者**：需要为 Mover 的核心逻辑（如移动预测、分层移动、黑板交互）编写或运行自动化测试。
- **游戏项目质量保证（QA）**：需要在包含 Mover 系统的项目中，运行一组预定义的测试用例以验证移动功能。
- **学习 Mover 内部实现**：希望查看一个完整的、自包含的测试实现示例，以理解如何编写自定义的 `FLayeredMoveBase`。

## 蓝图用法

此插件的核心功能是 C++ 测试类，不直接为游戏蓝图设计。它暴露的结构体 `FTestCustomLayeredMove` 主要在 C++ 测试代码中实例化和使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无 | 此插件不提供独立的蓝图函数库 | - |

### 使用示例（蓝图描述）

由于这是一个测试插件，通常不会在游戏蓝图中直接使用。其 `FTestCustomLayeredMove` 结构体可以通过“Make Literal Struct”节点在蓝图中创建，但其主要用途是在 C++ 测试代码中。

## C++ 用法

该插件的 C++ 用法主要体现在编写测试用例，用于验证 Mover 组件和自定义移动逻辑。

### 头文件引入

```cpp
#include "TestCustomLayeredMoves.h"
```

### 基本用法

以下示例展示了如何在测试中创建并应用一个自定义的分层移动（`FTestCustomLayeredMove`）。此模式模拟了一个“发射”效果。
*(注：以下代码灵感来源于插件提供的测试结构体，实际使用需结合具体的 `UMoverComponent` 实例)*
```cpp
// 假设你有一个指向 UMoverComponent 的指针
UMoverComponent* MoverComp = /* ... */;

// 创建一个自定义分层移动的实例
FTestCustomLayeredMove LaunchMove;
LaunchMove.LaunchVelocity = FVector(0, 0, 1000.f); // 以1000 cm/s的速度向上发射
LaunchMove.MixMode = EMoveMixMode::Override; // 覆盖当前速度

// 将其应用到 Mover 组件上
if (MoverComp)
{
    MoverComp->ApplyLayeredMove(LaunchMove);
}
```

### 进阶用法

在自动化测试中，你可能会组合使用分层移动和 Mover 的黑板系统来验证复杂的行为序列。
```cpp
// 在测试函数中
{
    // 1. 模拟角色启动一个自定义移动
    FTestCustomLayeredMove MoveA;
    MoveA.LaunchVelocity = FVector::ForwardVector * 500.f;
    MoverComp->ApplyLayeredMove(MoveA);

    // 2. 立即应用另一个强制切换移动模式的移动
    FTestCustomLayeredMove MoveB;
    MoveB.ForceMovementMode = FName(“Flying”);
    MoveB.LaunchVelocity = FVector::UpVector * 200.f;
    MoverComp->ApplyLayeredMove(MoveB);

    // 3. 推进模拟时间，观察 Mover 组件如何处理这些叠加的移动
    // (这通常在自动化测试的 Tick 或给定函数中完成)
    // Verify that the final movement mode and velocity match expectations...
}
```

## Demo 示例

一个展示如何定义和应用自定义分层移动的最小 C++ 示例。
*(注：此示例假设你已有一个包含 `UMoverComponent` 的 Actor)*
```cpp
// MyTestMoverActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyTestMoverActor.generated.h"

class UMoverComponent;
struct FTestCustomLayeredMove;

UCLASS()
class AMyTestMoverActor : public AActor
{
    GENERATED_BODY()

public:
    AMyTestMoverActor();

    UFUNCTION(BlueprintCallable, Category = “Test”)
    void LaunchUpward();

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = “Movement”)
    TObjectPtr<UMoverComponent> MoverComponent;
};

// MyTestMoverActor.cpp
#include “MyTestMoverActor.h”
#include “MoverComponent.h”
#include “TestCustomLayeredMoves.h”

AMyTestMoverActor::AMyTestMoverActor()
{
    MoverComponent = CreateDefaultSubobject<UMoverComponent>(TEXT(“MoverComp”));
    RootComponent = MoverComponent; // 简化示例，实际可能需要 SceneComponent
}

void AMyTestMoverActor::LaunchUpward()
{
    if (MoverComponent)
    {
        FTestCustomLayeredMove LaunchMove;
        LaunchMove.LaunchVelocity = FVector(0.f, 0.f, 1500.f); // 向上发射
        MoverComponent->ApplyLayeredMove(LaunchMove);
    }
}
```

## 模块依赖

此插件依赖于其他 Mover 相关插件和测试框架。

| 模块 | 用途 |
|---|---|
| `Mover` | 要测试的核心移动系统插件 |
| `MoverExamples` | 提供测试可能用到的示例移动模式或资产 |
| `RuntimeTests` | 提供运行时自动化测试的基础框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-02-10 | `75cf6ee4` | Mover: supporting prediction on the rollback blackboard, with dedicated slot in the circular buffer | Mover：在回滚黑板上支持预测，在循环缓冲区中分配专用槽位。 |
| 2026-02-06 | `cca897b3` | [Backout] - CL50608996 | [回滚] - 回退了变更列表 50608996 的更改。 |
| 2026-02-06 | `0f92df41` | Mover: supporting prediction on the rollback blackboard, with dedicated slot in the circular buffer | Mover：在回滚黑板上支持预测，在循环缓冲区中分配专用槽位。（首次尝试，后被回滚） |
| 2025-06-27 | `a55f7404` | Mover: fix layered move timestamp conversions, including fix for broken multi-jump due to rounding | Mover：修复分层移动时间戳转换问题，包括因四舍五入导致的多段跳跃失效。 |

### 维护评价

- **状态**：**活跃维护中**。
- **分析**：该插件作为核心系统 `Mover` 的测试套件，随着 Mover 系统的演进（如添加预测回滚支持）而同步更新。最近的更新集中在 2026 年初，与 Mover 核心的功能增强和 Bug 修复紧密相关。虽然插件本身标记为实验性（`IsExperimentalVersion=true`），但其作为测试资产，维护频率与底层系统一致，表明其重要性。
- **结论**：**推荐用于参考和学习 Mover 系统的测试方法**。不推荐直接用于游戏项目。由于其与实验性的 Mover 系统绑定，使用前需确保项目环境与该插件的要求（特别是依赖的 `Mover` 和 `MoverExamples` 插件版本）匹配。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MoverTests)
- [官方文档]() (无)
- [测试用例]() (测试内容即本插件自身)