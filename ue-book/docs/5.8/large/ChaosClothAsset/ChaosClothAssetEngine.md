# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，材质模板） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

## 用途

ChaosClothAsset 插件是基于 **Chaos 物理引擎**的下一代服装/布料资产管理系统。它旨在解决传统布料模拟（如基于 APEX 的系统）在资产创建工作流、性能和可控性方面的限制。

**核心价值**：
1.  **数据流驱动**：与 Unreal 的 `Dataflow` 系统深度集成，通过节点图的方式生成和修改布料资产数据，使布料创作流程更加可控和可视化。
2.  **基于图案 (Pattern-Based)**：支持从 2D 布料图案定义生成 3D 布料网格，更贴近真实的服装设计流程。
3.  **多资产支持**：不仅支持单件布料资产 (`UChaosClothAsset`)，还支持包含多块布料的套装资产 (`UChaosOutfitAsset`，属于同一基类)，便于管理复杂角色服装。
4.  **高性能模拟**：利用 `ChaosCloth` 插件进行高性能物理模拟，并支持多线程、LOD 管理、碰撞源等高级特性。
5.  **蓝图友好**：提供了丰富的蓝图接口，允许在运行时动态调整布料模拟参数。

**存在原因**：作为 Epic 推动的下一代物理布料解决方案，它取代了旧有的实验性系统，并逐渐集成到引擎的核心布料工作流中，旨在为游戏和实时应用提供更强大、更易用的布料模拟工具。

## 使用场景

-   **制作角色服装模拟**：为游戏角色创建动态的斗篷、裙子、衣袖、旗帜等布料部件。
-   **需要美术友好的布料工作流**：美术或技术美术希望通过可视化的数据流图（Dataflow）来构建和调试布料资产，而非纯粹通过代码或属性面板。
-   **需要管理复杂服装套装**：角色的一套服装（如上衣、裤子、外套）由多个独立的布料模拟部分组成，需要一个统一的资产（Outfit）进行管理。
-   **需要高性能 Chaos 物理布料**：项目要求使用引擎内置的高性能 Chaos 物理系统进行布料模拟，并希望获得最新特性和优化。
-   **需要运行时动态控制布料**：希望通过蓝图在游戏运行时切换布料外观、调整物理参数或处理交互。

## 蓝图用法

蓝图 API 主要集中在 `UChaosClothComponent` 和 `UChaosClothAssetInteractor` 上。

### 核心组件

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Asset` | 设置该组件使用的布料或套装资产。 | `UChaosClothComponent` |
| `Get Asset` | 获取当前使用的布料或套装资产。 | `UChaosClothComponent` |
| `Get Cloth Outfit Interactor` | 获取用于读写运行时布料模拟参数的交互器（Interactor）。可通过 `ModelIndex` 或 `ClothSimulationModelName` 指定具体模型。 | `UChaosClothComponent` |
| `Force Next Update Teleport` | 强制在下一帧将布料传送至骨骼新位置，保持当前姿势。 | `UChaosClothComponent` |
| `Force Next Update Teleport And Reset` | 强制在下一帧传送并重置布料姿势。 | `UChaosClothComponent` |
| `Suspend Simulation` | 暂停模拟，布料保持最后姿态。 | `UChaosClothComponent` |
| `Resume Simulation` | 恢复模拟。 | `UChaosClothComponent` |
| `Set Simulate In Editor` | 设置是否在编辑器中运行模拟（仅编辑器）。 | `UChaosClothComponent` |
| `Reset Rest Lengths With Morph Target` | 使用指定的 Morph Target 重置布料静止长度。 | `UChaosClothComponent` |
| `Add Collision Source` | 添加一个外部碰撞源（其他骨骼网格体组件+其物理资产）。 | `UChaosClothComponent` |
| `Reset Collision Sources` | 移除所有外部碰撞源。 | `UChaosClothComponent` |

### 参数交互器 (Interactor)

通过 `Get Cloth Outfit Interactor` 获取的 `UChaosClothAssetInteractor` 对象，用于读取和修改布料的物理模拟参数（如刚度、阻尼、重力缩放等）。参数以 `FName` 为键。

| 节点 | 说明 |
|---|---|
| `Get All Property Names` | 获取所有可用的参数名称。 |
| `Get Float Property Value` | 获取浮点参数值。 |
| `Set Float Property Value` | 设置浮点参数值（所有LOD或指定LOD）。 |
| `Get Weighted Float Property Value` | 获取加权浮点参数的低值和高值（`FVector2D`）。 |
| `Set Weighted Float Property Value` | 设置加权浮点参数的低值和高值。 |
| `Get Int Property Value` | 获取整型参数值。 |
| `Set Int Property Value` | 设置整型参数值。 |

### 使用示例（蓝图描述）

**示例1：基本布料组件设置**
1.  在角色蓝图中添加一个 `Chaos Cloth Component`。
2.  通过 `Set Asset` 节点，将一个已创建的 `Cloth Asset` 或 `Outfit Asset` 指定给该组件。
3.  组件注册后，会自动开始模拟。可以通过 `Set Enable Simulation` 节点动态开关模拟。

**示例2：运行时修改布料属性**
1.  通过 `Get Cloth Outfit Interactor` 获取交互器。
2.  使用 `Get All Property Names` 查看可修改的参数。
3.  使用 `Set Float Property Value`，将 `PropertyName` 设置为如 `"AnimDriveStiffness"` (动画驱动刚度)，`Value` 设置为所需数值，`LODIndex` 设为 -1 以影响所有LOD。

## C++ 用法

C++ 接口主要通过 `UChaosClothComponent`、`UChaosClothAsset`、`UChaosClothAssetInteractor` 以及底层的 `FClothSimulationProxy` 来实现。

### 头文件引入

```cpp
// 主要资产和组件
#include "ChaosClothAsset/ClothAsset.h"
#include "ChaosClothAsset/ClothComponent.h"

// 用于操作运行时参数
#include "ChaosClothAsset/ClothAssetInteractor.h"

// 底层模拟代理（高级用法）
#include "ChaosClothAsset/ClothSimulationProxy.h"
```

### 基本用法

**创建和设置布料资产组件 (源自组件使用逻辑)**

```cpp
// 假设你已经有一个 UChaosClothAsset* ClothAsset 指针
// 在 Actor 或 Component 的构造函数或初始化函数中

UChaosClothComponent* ClothComp = NewObject<UChaosClothComponent>(YourActor);
ClothComp->SetAsset(ClothAsset); // 设置布料资产
ClothComp->RegisterComponent(); // 注册组件以开始模拟
```

**运行时获取并修改布料参数 (源自 UChaosClothAssetInteractor 接口)**

```cpp
// 获取交互器
UChaosClothAssetInteractor* Interactor = ClothComp->GetClothOutfitInteractor(0);
if (Interactor)
{
    // 设置动画驱动刚度
    Interactor->SetFloatPropertyValue(FName("AnimDriveStiffness"), /*LODIndex=*/-1, 0.8f);
    
    // 获取重力缩放值
    float GravityScale = Interactor->GetFloatPropertyValue(FName("GravityScale"), 0, 1.0f);
    
    // 设置加权参数（如风速）
    Interactor->SetWeightedFloatPropertyValue(FName("WindVelocityWeight"), -1, FVector2D(0.0f, 100.0f));
}
```

### 进阶用法

**通过 C++ 驱动 Dataflow 构建 (源自 UChaosClothAsset::Build 和 UChaosClothAssetBase 的 Dataflow 接口)**

```cpp
// 此过程通常由编辑器工具或自定义构建管线触发。
// 1. 准备数据（通常由 Dataflow 节点图生成）
TArray<TSharedRef<const FManagedArrayCollection>> ClothCollections;
// ... 填充 ClothCollections 数据 ...

// 2. 构建资产
UChaosClothAsset* ClothAsset = ...;
FText ErrorText, VerboseText;
ClothAsset->Build(ClothCollections, nullptr, &ErrorText, &VerboseText);
if (!ErrorText.IsEmpty())
{
    UE_LOG(LogTemp, Error, TEXT("ClothAsset Build Failed: %s"), *ErrorText.ToString());
}
```

**添加外部碰撞源 (源自 UChaosClothComponent::AddCollisionSource)**

```cpp
// 假设你有一个参考骨骼网格体组件（如角色本体）和它的物理资产
USkinnedMeshComponent* SourceBodyComponent = ...;
UPhysicsAsset* SourcePhysicsAsset = ...;

ClothComp->AddCollisionSource(SourceBodyComponent, SourcePhysicsAsset, true); // true 表示只使用胶囊体和球体碰撞
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何创建一个带有 ChaosClothComponent 的 Actor，并设置一个布料资产。

### ChaosClothDemoActor.h
```cpp
// ChaosClothDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ChaosClothDemoActor.generated.h"

class UChaosClothComponent;
class UChaosClothAsset;

UCLASS(Blueprintable)
class AChaosClothDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AChaosClothDemoActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Cloth")
    TObjectPtr<UChaosClothComponent> ClothComponent;

    // 在编辑器或蓝图中指定布料资产
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cloth")
    TObjectPtr<UChaosClothAsset> ClothAsset;
};
```

### ChaosClothDemoActor.cpp
```cpp
// ChaosClothDemoActor.cpp
#include "ChaosClothDemoActor.h"
#include "ChaosClothAsset/ClothAsset.h"
#include "ChaosClothAsset/ClothComponent.h"

AChaosClothDemoActor::AChaosClothDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建并设置布料组件
    ClothComponent = CreateDefaultSubobject<UChaosClothComponent>(TEXT("ClothComp"));
    RootComponent = ClothComponent;
}

void AChaosClothDemoActor::BeginPlay()
{
    Super::BeginPlay();

    if (ClothAsset && ClothComponent)
    {
        // 设置布料资产并开始模拟
        ClothComponent->SetAsset(ClothAsset);
        
        // 可选：在蓝图中更常通过属性面板设置，这里演示C++设置
        // ClothComponent->SetEnableSimulation(true);
    }
}
```

## 模块依赖

要使用 `ChaosClothAsset` 插件，你的项目模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | 核心布料资产类定义（UChaosClothAsset 等）。 |
| `ChaosClothAssetEngine` | 运行时组件和交互器（UChaosClothComponent, UChaosClothAssetInteractor）。 |
| `ChaosCloth` | 底层的 Chaos 物理布料模拟引擎。 |
| `Dataflow` | 数据流框架，用于布料资产构建管线。 |
| `GeometryCache` | 几何体缓存，布料资产中可能用于存储中间数据。 |

*注意：你的项目需要先启用 `ChaosClothAsset`、`ChaosCloth`、`Dataflow` 和 `GeometryCache` 插件。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Blueprint operations. | 修复蓝图操作（如复制粘贴）后布料组件的“在编辑器中模拟”设置和资产指针丢失的问题。 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable. | 优化性能：将并行布料模拟的等待操作从帧末尾移至更晚的 `TG_LastDemotable` 阶段，减少主线程阻塞。 |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefershBoneMapping for ClothAssetSKMClothingAsset. | 为通过骨骼网格体系统使用的布料资产实现骨骼映射刷新功能，修复潜在绑定问题。 |
| 2026-05-22 | `e98c5896` | [Chaos Cloth Asset] Refresh the editor-only Asset alias after a duplicate or paste of an actor. | 修复复制或粘贴包含布料组件的Actor后，编辑器专用的资产引用（Alias）未正确刷新的问题。 |
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产到骨骼网格体的转换器代码，属于内部优化。 |

### 维护评价

-   **创建时间**：创建于 2024 年 3 月，至今约 1 年多，属于相对较新的系统。
-   **活跃度**：**非常活跃**。从提交记录看，近一周内（截至2026年5月底）有多次实质性的功能修复和优化提交，表明 Epic 的核心开发团队正在积极维护和迭代此插件。
-   **状态**：`.uplugin` 文件中 `IsBetaVersion=true` 且 `EnabledByDefault=false`，明确标记为 **Beta** 状态。这意味着 API 和功能可能会有变动，但已是官方推荐的下一代解决方案。
-   **推荐使用**：**强烈推荐用于新项目**，特别是对布料模拟有高质量要求的项目。由于处于 Beta 阶段，使用前应充分测试，并关注版本更新日志。它是替代旧实验性布料系统的官方路径。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
-   [官方文档]() (当前为空，参考引擎文档中的“Cloth Simulation”和“ChaosCloth”部分)
-   [测试用例]() (引擎内通常位于 `Engine/Tests/` 或插件内 `Source/` 目录，需具体查找)