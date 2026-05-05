# Groom

> Rendering and simulation of grooms（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（毛发资产、材质、蓝图） |
| 模块 | `HairStrandsCore` (Runtime), `HairStrandsRuntime` (Runtime), `HairStrandsDeformer` (Runtime), `HairStrandsSolver` (Runtime), `HairStrandsEditor` (Runtime), `HairStrandsDataflow` (Runtime), `HairCardGeneratorFramework` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-08-02 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HairStrands) | |

## 用途

HairStrands（Groom）插件为 Unreal Engine 提供了一套完整的、端到端的毛发（Groom）解决方案。它不仅仅是一个渲染组件，而是一个涵盖了从资产导入、LOD 生成、运行时渲染、物理模拟到编辑器工具的完整系统。其核心目标是让开发者能够在游戏中实现电影级质量的毛发效果，包括数万根独立发丝的渲染、动态光照、阴影以及基于物理的毛发模拟（如风吹、角色运动时的飘动）。

该插件解决了传统基于纹理和多边形网格的毛发渲染方法在细节和动态表现上的不足，通过基于发丝的渲染（Strand-based）技术，实现了更高的视觉保真度。

## 使用场景

-   你正在开发一个需要高保真角色外观的 3A 级角色扮演游戏或叙事驱动型游戏 → 使用 Groom 系统为角色创建逼真的头发、胡须和体毛。
-   你需要制作电影级的过场动画或虚拟制片内容 → 利用 Groom 的渲染和模拟功能，获得与离线渲染器相媲美的毛发效果。
-   你的项目包含需要与环境进行物理交互的毛发（如风吹、角色快速移动） → 使用 HairStrandsSolver 模块进行实时物理模拟。
-   你需要为不同平台或性能需求优化毛发表现 → 利用内置的 LOD 系统和 Hair Card 生成框架，在发丝渲染和基于网格的卡片渲染之间进行权衡。

## 蓝图用法

由于插件规模庞大，蓝图 API 分布在多个模块中。以下按功能分组列出核心节点。

### 核心资产与管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Load Groom` | 从资产路径异步加载一个 `UGroomAsset`。 | `UGroomAsset` |
| `Get Groom LOD` | 获取 Groom 资产中指定 LOD 级别的数据。 | `UGroomAsset` |
| `Set Groom Component` | 将 Groom 资产分配给一个 Groom 组件。 | `UGroomComponent` |

### 渲染与材质

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Hair Material` | 为 Groom 组件的指定组设置材质。 | `UGroomComponent` |
| `Set Hair Shadow Material` | 设置用于深度/阴影通道的材质。 | `UGroomComponent` |
| `Set Hair Debug Material` | 设置用于调试可视化的材质。 | `UGroomComponent` |

### 物理模拟

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Simulation Enabled` | 启用或禁用指定 Groom 组件的物理模拟。 | `UGroomComponent` |
| `Set Gravity Vector` | 设置影响毛发模拟的重力方向。 | `UGroomComponent` |
| `Add External Force` | 为模拟中的毛发添加一个外力（如风）。 | `UGroomComponent` |

### 使用示例（蓝图描述）

1.  **基础设置**：在角色蓝图中，添加一个 `Groom Component`。在组件的细节面板中，将你的 `UGroomAsset` 指定给 `Groom` 属性。
2.  **材质覆盖**：要覆盖默认材质，使用 `Set Hair Material` 节点。将 `Groom Component` 引用作为目标，指定要覆盖的组索引（Group Index）和新的材质实例。
3.  **启用物理**：在角色的事件图表中，使用 `Set Simulation Enabled` 节点，在游戏开始时启用模拟。可以使用 `Add External Force` 节点，根据风向或角色速度动态施加力。

## C++ 用法

### 头文件引入

```cpp
#include "GroomAsset.h"
#include "GroomComponent.h"
#include "HairStrandsCore.h"
```

### 基本用法

以下示例展示了如何在 C++ 中加载 Groom 资产并将其应用到组件。
*（来源：基于 `HairStrandsCore` 模块的典型使用模式）*

```cpp
// 在角色类的头文件中
UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Groom")
UGroomComponent* GroomComponent;

UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Groom")
TSoftObjectPtr<UGroomAsset> GroomAssetPtr;

// 在角色类的构造函数中
GroomComponent = CreateDefaultSubobject<UGroomComponent>(TEXT("Groom"));
GroomComponent->SetupAttachment(GetMesh()); // 附加到骨骼网格体

// 在 BeginPlay 或资产加载回调中
if (!GroomAssetPtr.IsNull())
{
    UGroomAsset* LoadedGroom = GroomAssetPtr.LoadSynchronous();
    if (LoadedGroom)
    {
        GroomComponent->SetGroomAsset(LoadedGroom);
    }
}
```

### 进阶用法

动态控制毛发模拟参数。
*（来源：基于 `HairStrandsSolver` 模块的 API）*

```cpp
// 假设 GroomComponent 已初始化并拥有资产
if (GroomComponent && GroomComponent->GetGroomAsset())
{
    // 启用物理模拟
    GroomComponent->SetSimulationEnabled(true);

    // 设置全局风力影响（需要自定义实现或使用组件接口）
    // 通常通过材质参数或物理资产配置，但也可以直接操作求解器数据
    // 例如，通过修改 GroomComponent 的物理资产（UHairStrandsPhysicsAsset）中的约束参数。

    // 在 Tick 中动态施加力
    void AMyCharacter::Tick(float DeltaTime)
    {
        Super::Tick(DeltaTime);

        // 计算一个基于角色速度的“风”力
        FVector CharacterVelocity = GetVelocity();
        FVector WindForce = CharacterVelocity.GetSafeNormal() * CharacterVelocity.Size() * WindStrengthMultiplier;

        // 将力传递给毛发模拟系统（具体API可能涉及直接访问求解器或通过组件接口）
        // GroomComponent->AddForce(WindForce); // 伪代码，实际API请查阅文档
    }
}
```

## Demo 示例

一个最小的可编译示例，展示如何创建一个带有 Groom 的 Actor。
*（注意：此示例假设你已经有一个 `UGroomAsset` 资产）*

**GroomActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GroomActor.generated.h"

class UGroomComponent;
class UGroomAsset;

UCLASS()
class AGroomActor : public AActor
{
    GENERATED_BODY()

public:
    AGroomActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    USceneComponent* SceneRoot;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    UGroomComponent* GroomComp;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Groom")
    TSoftObjectPtr<UGroomAsset> GroomAssetToLoad;
};
```

**GroomActor.cpp**
```cpp
#include "GroomActor.h"
#include "GroomComponent.h"
#include "GroomAsset.h"

AGroomActor::AGroomActor()
{
    PrimaryActorTick.bCanEverTick = false;

    SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
    RootComponent = SceneRoot;

    GroomComp = CreateDefaultSubobject<UGroomComponent>(TEXT("Groom"));
    GroomComp->SetupAttachment(SceneRoot);
}

void AGroomActor::BeginPlay()
{
    Super::BeginPlay();

    // 异步加载 Groom 资产
    if (!GroomAssetToLoad.IsNull())
    {
        UGroomAsset* LoadedAsset = GroomAssetToLoad.LoadSynchronous();
        if (LoadedAsset)
        {
            GroomComp->SetGroomAsset(LoadedAsset);
            UE_LOG(LogTemp, Log, TEXT("Groom asset loaded and assigned successfully."));
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Failed to load Groom asset."));
        }
    }
}
```

## 模块依赖

从各模块的 `Build.cs` 文件分析，使用此插件的核心功能（如 `HairStrandsCore`）通常需要以下依赖。省略了常见的 Core, Engine 等。

| 模块 | 用途 |
|---|---|
| `RenderCore` | 底层渲染资源和命令。 |
| `RHI` | 渲染硬件接口，用于 GPU 计算和资源管理。 |
| `Projects` | 插件和模块管理。 |
| `HairStrandsCore` | 核心数据结构和资产定义，是其他模块的基础。 |
| `HairStrandsRuntime` | 运行时渲染逻辑。 |
| `HairStrandsDeformer` | 用于驱动毛发动画的变形器。 |
| `HairStrandsSolver` | 物理模拟求解器。 |
| `HairStrandsDataflow` | 数据流处理，可能用于程序化生成或修改毛发数据。 |
| `HairCardGeneratorFramework` | 毛发卡片生成框架接口。 |

## 维护状态

### 近期更新

```
- 08bc754e441a Replace some usages of FORCEINLINE with inline in Metahuman modules.
- 2739c3d30ebc Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n
- 551073eb4dfa - Fixed monolithic editor link issue #rb trivial #jria none #p4v-preflight-copy 18309096 #preflight 61a4e42f2e4ffe18981b942b
```

**解读**：
1.  `08bc754e441a`: 代码风格清理，将 `FORCEINLINE` 替换为 `inline`，主要影响 MetaHuman 相关模块。属于维护性更新。
2.  `2739c3d30ebc`: 使用工具自动更新头文件，确保 DLL 导出符号正确。属于构建系统维护。
3.  `551073eb4dfa`: 修复了单体编辑器（Monolithic Editor）的链接问题。这是一个重要的构建兼容性修复。

### 维护评价

-   **创建时间**：插件创建于 2019 年，已有约 5 年历史，是 UE 中毛发系统的主力方案。
-   **最近更新频率**：从提供的 3 条提交记录看，近期更新主要是**维护性和构建修复**，而非新功能开发。这表明该插件已进入**成熟稳定期**。
-   **活跃维护**：是。Epic Games 仍在维护此插件，以确保其与引擎新版本的兼容性和构建稳定性。
-   **已知问题或限制**：作为 `EnabledByDefault: false` 的插件，需要用户手动启用。其庞大的模块结构和对渲染管线的深度集成，意味着调试和自定义可能较为复杂。性能开销较大，需要针对目标平台进行仔细优化。
-   **推荐使用**：**推荐**。对于需要高质量、动态毛发效果的项目，HairStrands (Groom) 是 UE 内置的唯一且功能完整的解决方案。虽然学习曲线较陡峭且性能成本高，但其效果是传统方法无法比拟的。建议参考官方文档和 MetaHuman 项目中的示例进行学习。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HairStrands)
-   [官方文档](https://docs.unrealengine.com/5.7/en-US/hair-strands-and-grooms-in-unreal-engine/) (UE5 官方文档)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HairStrands/Tests) (如果存在)