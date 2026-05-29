# Apex Destruction

> APEX implementation of destruction（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | APEX破坏 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ApexDestruction` (Runtime), `ApexDestructionEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2017-07-26 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ApexDestruction) | |

## 用途

这是一个基于已废弃的 NVIDIA APEX PhysX SDK 实现的可破坏物体（Destructible Mesh）系统。它允许艺术家将静态网格体（Static Mesh）预破碎为多个“块”（chunks），并在运行时通过施加伤害（Damage）或冲击力（Impact）来模拟真实的物理破碎效果。该插件是 UE4 时代（Chaos 物理系统出现前）用于实现物体破坏效果的核心方案。

**重要提示**：此插件已在 UE 4.26 版本被标记为**废弃 (Deprecated)**，官方推荐使用全新的基于 Chaos 物理引擎的 **Chaos Destruction** 系统来替代。本文档仅作为历史参考和现有遗留项目的维护指南。

## 使用场景

- 你需要在游戏中实现可破坏的墙体、掩体、玻璃等静态物体。
- 你正在维护一个基于 UE4 并使用了 APEX Destructible 特性的老项目，尚未迁移到 Chaos Destruction。
- （不推荐）出于特殊原因，必须使用基于 APEX 的破坏系统。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Apply Damage` | 在指定位置施加点状伤害，触发物体破碎。 | `UDestructibleComponent` |
| `Apply Radius Damage` | 在指定位置施加范围伤害，影响半径内所有碎片。 | `UDestructibleComponent` |
| `On Component Fracture` | 组件级碎片事件，当任意碎片被破坏时触发。 | `UDestructibleComponent` |
| `On Actor Fracture` | Actor级碎片事件，与 `On Component Fracture` 类似。 | `ADestructibleActor` |

### 使用示例（蓝图描述）

1.  **创建可破坏物体**：
    *   在 Content Browser 中，基于一个静态网格体资产，右键选择 `Create Destructible Mesh`。这将打开 Destructible Mesh 编辑器，用于设置破碎参数。
    *   将创建的 `DestructibleMesh` 资产拖拽到场景中，会自动创建一个 `ADestructibleActor`。

2.  **触发破坏**：
    *   从另一个 Actor（如子弹）的 `Event Hit` 节点，获取碰撞的组件并尝试转换为 `DestructibleComponent`。
    *   调用 `Apply Damage` 节点，输入伤害量（`Damage Amount`）、命中位置（`Hit Location`）和冲击方向（`Impulse Dir`）。
    *   或者，调用 `Apply Radius Damage` 节点，输入伤害源点、伤害半径和伤害量，模拟爆炸效果。

3.  **监听破碎事件**：
    *   选中场景中的 `ADestructibleActor`，在 Details 面板中为 `On Actor Fracture` 事件创建自定义事件。
    *   在该事件中可以实现破碎后生成粒子特效、音效或游戏逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "DestructibleComponent.h"
#include "DestructibleActor.h"
```

### 基本用法

对可破坏组件施加点状伤害。
（来源：`Source/ApexDestruction/Public/DestructibleComponent.h`）

```cpp
// 假设你有一个 UDestructibleComponent 指针 DestructibleComp
if (DestructibleComp)
{
    FVector HitLocation = GetActorLocation(); // 伤害作用点
    FVector ImpulseDir = FVector::UpVector;   // 碎片飞散方向
    float ImpulseStrength = 500.0f;           // 冲击力大小
    
    // 施加 50 点伤害
    DestructibleComp->ApplyDamage(50.0f, HitLocation, ImpulseDir, ImpulseStrength);
}
```

### 进阶用法

绑定碎片事件回调。
（来源：`Source/ApexDestruction/Public/DestructibleComponent.h`）

```cpp
// 在拥有 UDestructibleComponent 的 Actor 的 BeginPlay 中绑定事件
void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    
    if (UDestructibleComponent* DestructibleComp = FindComponentByClass<UDestructibleComponent>())
    {
        // 绑定组件级碎片事件
        DestructibleComp->OnComponentFracture.AddDynamic(this, &AMyActor::HandleFracture);
    }
}

// 事件处理函数
void AMyActor::HandleFracture(const FVector& HitPoint, const FVector& HitDirection)
{
    // HitPoint - 破碎发生的精确位置
    // HitDirection - 导致破碎的冲击方向
    // 在此播放破碎音效、生成碎片粒子等
    UE_LOG(LogTemp, Log, TEXT("物体在 %s 处破碎！"), *HitPoint.ToString());
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何创建一个简单的可破坏物体并施加伤害。

**MyDestructibleActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDestructibleActor.generated.h"

class UDestructibleComponent;

UCLASS()
class AMyDestructibleActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyDestructibleActor();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable)
    void TakeDamageAtLocation(FVector HitLocation, float DamageAmount);

private:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, meta = (AllowPrivateAccess = "true"))
    UDestructibleComponent* DestructibleComponent;
};
```

**MyDestructibleActor.cpp**
```cpp
#include "MyDestructibleActor.h"
#include "DestructibleComponent.h"

AMyDestructibleActor::AMyDestructibleActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建并设置破坏组件为根组件
    DestructibleComponent = CreateDefaultSubobject<UDestructibleComponent>(TEXT("DestructibleComp"));
    RootComponent = DestructibleComponent;
    
    // 注意：DestructibleMesh 资产需要在蓝图或编辑器中设置，这里无法在构造函数中直接分配。
}

void AMyDestructibleActor::BeginPlay()
{
    Super::BeginPlay();
}

void AMyDestructibleActor::TakeDamageAtLocation(FVector HitLocation, float DamageAmount)
{
    if (DestructibleComponent)
    {
        // 计算一个从命中点向上偏移的方向作为冲击方向
        FVector ImpulseDir = (GetActorLocation() - HitLocation).GetSafeNormal() + FVector(0, 0, 0.5f);
        ImpulseDir.Normalize();
        
        // 应用伤害
        DestructibleComponent->ApplyDamage(DamageAmount, HitLocation, ImpulseDir, 1000.0f);
    }
}
```

## 模块依赖

该插件依赖于已废弃的 APEX PhysX 库。对于普通使用者，在项目 `.Build.cs` 中添加对 `ApexDestruction` 模块的依赖即可。

| 模块 | 用途 |
|---|---|
| `ApexDestruction` | 运行时破坏效果核心功能 |
| `PhysX` / `APEX` | (底层依赖，通常通过 `ApexDestruction` 间接引入) NVIDIA APEX 物理破坏库 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至新的 UE_LOGF 格式。 |
| 2025-10-14 | `5f7283a0` | Copying a deleted file over that RoboMerge/p4 got confused about | 复制一个因版本控制混淆而被删除的文件。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件配置文件从 `Base*.ini` 重命名为 `Default*.ini`。 |
| 2025-07-14 | `8c4cad91` | - Changed all WITH_EDITORONLY_DATA properties... | 为 `StaticMesh` 中所有 `WITH_EDITORONLY_DATA` 属性添加访问器。 |
| 2024-11-23 | `04a0ec79` | Fix errors with latest compiler | 修复最新编译器下的错误。 |

### 维护评价

**维护状态：可能废弃 / 仅限维护性更新**

- **创建时间**：8 年前，是 UE4 时代的遗留产物。
- **最近更新频率**：最近 3 年的提交均为编译错误修复、文件重命名、日志格式迁移等**维护性工作**，**没有任何新功能开发**。
- **活跃度**：所有相关类和结构体（如 `UDestructibleComponent`, `FDestructibleParameters`）均已在 UE 4.26 中被明确标记为 `UE_DEPRECATED`。
- **官方立场**：Epic 官方已停止维护此插件，并强烈推荐使用 **Chaos Destruction** 作为其替代品。
- **推荐度**：**不推荐用于新项目**。仅建议在维护无法立即迁移的旧项目时参考。新项目应直接使用 Chaos Destruction 系统。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ApexDestruction)
- [官方文档]()：无（已废弃，无新文档）
- [测试用例]()：插件目录内未发现专用测试用例。