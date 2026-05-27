# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产， 模拟资产） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

## 用途

Chaos Cloth Asset 插件提供了一个基于 2D 图案的布料模拟资产工作流。它不仅仅是一个模拟组件，而是一个**完整的布料资产创建、编辑和模拟生态系统**，旨在替代传统的骨骼布料。它的核心在于将布料定义为可编辑的“资产”，其中包含从 2D 图案（Pattern）转换为 3D 三角网格（Tessellation）、物理模拟属性（Stiffness, Damping等）、以及约束（Constraints）的所有数据。这使得美术和设计人员可以在引擎内直接创建、迭代和预览复杂的布料效果，而无需依赖外部 DCC 工具进行繁琐的资产准备。

## 使用场景

*   **角色服装与纺织品模拟**：为游戏中的角色制作逼真、物理准确的斗篷、裙子、衬衫、旗帜等动态布料。
*   **需要精确控制布料行为的项目**：当需要对布料的拉伸、弯曲、碰撞等行为进行精细调整时，此插件的资产化工作流提供了比传统组件属性更直观和强大的控制。
*   **从设计到模拟的流程**：适合将 2D 图案设计（如服装版型）直接导入引擎，并实时预览其在 3D 模型上的动态效果，加速迭代。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Cloth Asset` | 为 `UClothComponent` 指定一个 `UChaosClothAsset` 来定义其布料形态和物理属性。 | `UChaosClothComponent` |
| `Reset Simlulation` | 重置当前布料的模拟状态，使其回到初始位置。 | `UChaosClothComponent` |
| `Reimport` | 重新导入布料资产，用于在编辑器中应用资产属性的更改。 | `UChaosClothAsset` |

### 使用示例（蓝图描述）

1.  在场景中放置一个带有骨骼网格体（Skeletal Mesh）的角色。
2.  为其添加一个 `ChaosClothComponent`。
3.  在蓝图构造脚本或运行时，通过 `Set Cloth Asset` 节点，将一个创建好的 `ChaosClothAsset`（通常包含在资产编辑器中配置的图案和物理设置）分配给该组件。
4.  当游戏开始或需要重置时，可以调用 `Reset Simulation` 节点。
5.  组件会基于分配的资产自动进行布料模拟，并与角色的骨骼动画交互。

## C++ 用法

### 头文件引入

```cpp
#include “ChaosClothAsset/ChaosClothAsset.h”
#include “ChaosClothAssetEngine/ChaosClothComponent.h”
```

### 基本用法

以下示例展示了如何在 C++ 中为一个骨骼网格体组件创建并应用布料资产。

```cpp
// 1. 创建一个 ChaosClothAsset
UChaosClothAsset* ClothAsset = NewObject<UChaosClothAsset>(GetTransientPackage(), TEXT(“MyClothAsset”));
// 注意：实际的资产编辑和配置通常在编辑器中进行，此处为概念性代码

// 2. 获取或创建 ChaosClothComponent
UChaosClothComponent* ClothComponent = GetOwner()->FindComponentByClass<UChaosClothComponent>();
if (!ClothComponent)
{
    ClothComponent = NewObject<UChaosClothComponent>(GetOwner());
    ClothComponent->RegisterComponent();
}

// 3. 将资产应用到组件
ClothComponent->SetClothAsset(ClothAsset);

// 4. (可选) 在需要时重置模拟
ClothComponent->ResetSimulation();
```

## Demo 示例

一个最小化的、运行时应用布料资产的组件示例。

**MyClothActor.h**
```cpp
#pragma once
#include “GameFramework/Actor.h”
#include “MyClothActor.generated.h”

class UChaosClothComponent;
class UChaosClothAsset;

UCLASS()
class AMyClothActor : public AActor
{
    GENERATED_BODY()

public:
    AMyClothActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere)
    UChaosClothComponent* ClothComponent;

    UPROPERTY(EditAnywhere, Category = “Cloth”)
    UChaosClothAsset* ClothAsset;
};
```

**MyClothActor.cpp**
```cpp
#include “MyClothActor.h”
#include “ChaosClothAssetEngine/ChaosClothComponent.h”

AMyClothActor::AMyClothActor()
{
    PrimaryActorTick.bCanEverTick = false;
    ClothComponent = CreateDefaultSubobject<UChaosClothComponent>(TEXT(“ClothComp”));
    RootComponent = ClothComponent;
}

void AMyClothActor::BeginPlay()
{
    Super::BeginPlay();
    if (ClothAsset)
    {
        ClothComponent->SetClothAsset(ClothAsset);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | Chaos 布料模拟的核心运行时库。 |
| `GeometryCache` | 用于处理和优化几何体缓存，可能用于模拟结果的处理。 |
| `Dataflow` | 提供数据流图编辑框架，用于布料资产节点的创建和配置。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Blueprint | 修复了蓝图编辑器中布料组件的“在编辑器中模拟”状态和资产引用无法保存的问题。 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable. | 优化了并行布料模拟的性能等待时机，将其移至最后一个可降级的任务组。 |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefershBoneMapping for ClothAssetSKMClothingAsset. | 为基于 Chaos Cloth 资产的服装实现了骨骼映射刷新功能，确保与骨骼网格体的正确关联。 |
| 2026-05-22 | `e98c5896` | [Chaos Cloth Asset] Refresh the editor-only Asset alias after a duplicate or paste of an actor. | 修复了在编辑器中复制或粘贴包含布料资产的 Actor 后，资产别名引用失效的问题。 |
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理了布料资产转换器的代码。 |

### 维护评价

*   **积极维护**：该插件自 2024 年初从 Experimental 文件夹移出并标记为 Beta 以来，一直得到 Epic 的持续开发和维护。从近期提交记录看，**最近一周内有多个功能性更新和 Bug 修复**，维护非常活跃。
*   **功能趋于完善**：早期的提交主要是模块重组和基础架构建立。近期的更新则集中在**修复编辑器集成问题、优化模拟性能以及完善资产工作流**，表明其正从核心功能开发转向稳定性和可用性优化。
*   **推荐使用**：对于需要高级布料模拟的新项目，这是一个强烈推荐的、代表未来方向的解决方案。尽管它默认未启用，且标记为 Beta，但其活跃的维护状态和与最新引擎功能（如 Dataflow）的深度集成，表明其已具备生产使用的基础。需要注意其 API 和资产格式可能随着 Beta 期的推进而发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
- [官方文档](）（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset/Tests) （推测路径）