# Groom

> Rendering and simulation of grooms

| 属性 | 值 |
|---|---|
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Groom 资产） |
| 模块 | `HairStrandsCore` (Runtime), `HairStrandsRuntime` (Runtime), `HairStrandsDeformer` (Runtime), `HairStrandsSolver` (Runtime), `HairStrandsEditor` (Runtime), `HairStrandsDataflow` (Runtime), `HairCardGeneratorFramework` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-08-02 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HairStrands) | |

## 用途

HairStrands 插件（在引擎中常被称为 Groom 插件）的核心功能是处理、渲染和模拟基于发丝（Strands）的毛发资产，即 **Groom**。它解决了在虚幻引擎中实现电影级数字人类和生物角色毛发效果的完整工作流问题。

该插件主要解决以下问题：
1.  **资产导入与管理**：提供从 DCC 工具（如 Maya、Houdini）导入 Alembic (.abc) 格式的 Groom 资产的功能，并将其转换为引擎内部的 `UGroomAsset`。
2.  **高质量渲染**：实现了基于发丝的实时渲染技术，包括发丝的光照、阴影、透明度和抗锯齿，以达到接近离线渲染的质量。
3.  **物理模拟**：集成了物理模拟系统，用于模拟毛发的动态行为，如风吹、角色运动时的飘动和碰撞。
4.  **性能优化**：提供了多种优化手段，如发丝的 LOD（Level of Detail）、发丝到卡片（Cards）或网格体（Meshes）的转换，以适应不同平台和性能需求。
5.  **运行时流送**：管理 Groom 缓存（GroomCache）数据的流送，支持大规模毛发资产的按需加载。

## 使用场景

-   **数字人类角色制作**：当你需要为游戏角色或影视角色创建逼真的头发、眉毛、睫毛和胡须时。
-   **生物角色制作**：为动物、奇幻生物等角色制作毛发、皮毛或羽毛。
-   **需要毛发物理效果**：希望毛发能随风飘动、在角色运动时产生自然的惯性摆动，并与身体或其他物体发生碰撞。
-   **优化毛发渲染性能**：在主机或中低端 PC 上，需要将高精度的发丝数据转换为更高效的卡片或网格体表示形式。
-   **使用 MetaHuman 框架**：MetaHuman Creator 生成的数字人类资产默认使用 Groom 系统来处理头发。

## 蓝图用法

Groom 系统的蓝图 API 主要集中在 `UGroomBlueprintLibrary` 和 `UGroomComponent` 上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Groom` | 从资产创建并返回一个 `UGroomComponent`。 | `UGroomBlueprintLibrary` |
| `Set Groom Asset` | 为 `UGroomComponent` 设置一个 `UGroomAsset`。 | `UGroomComponent` |
| `Set Physics Asset` | 为 Groom 设置用于碰撞检测的物理资产。 | `UGroomComponent` |
| `Set Enable Simulation` | 启用或禁用 Groom 的物理模拟。 | `UGroomComponent` |
| `Set Stiffness` | 设置毛发模拟的刚度。 | `UGroomComponent` |
| `Set Damping` | 设置毛发模拟的阻尼。 | `UGroomComponent` |
| `Set Hair Length Scale` | 缩放毛发的长度。 | `UGroomComponent` |
| `Set Hair Width` | 设置毛发的宽度。 | `UGroomComponent` |
| `Set LOD Mode` | 设置 Groom 的 LOD 模式（如自动、强制卡片等）。 | `UGroomComponent` |
| `Reset Simulation` | 重置毛发的物理模拟状态。 | `UGroomComponent` |

### 使用示例（蓝图描述）

1.  **创建基础 Groom**：
    -   使用 `Create Groom` 节点，传入一个 `UGroomAsset` 引用，即可在场景中生成一个带有毛发的组件。
    -   将返回的 `UGroomComponent` 附加到角色的骨骼网格体组件（如头部骨骼）上。

2.  **配置物理模拟**：
    -   在 `UGroomComponent` 的细节面板中，或通过蓝图调用 `Set Enable Simulation` 开启模拟。
    -   使用 `Set Stiffness` 和 `Set Damping` 节点调整毛发的软硬和摆动衰减。
    -   使用 `Set Physics Asset` 指定一个简化的碰撞体，用于毛发与身体的碰撞。

3.  **性能优化**：
    -   使用 `Set LOD Mode` 节点，根据距离或平台设置不同的 LOD 策略，例如在远处自动切换为卡片渲染。

## C++ 用法

### 头文件引入

```cpp
#include "GroomAsset.h"
#include "GroomComponent.h"
#include "GroomBlueprintLibrary.h"
```

### 基本用法

创建和配置一个 Groom 组件。

```cpp
// 假设在 Actor 的 BeginPlay 中
void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    // 1. 加载 Groom 资产
    UGroomAsset* GroomAsset = LoadObject<UGroomAsset>(nullptr, TEXT("/Game/Characters/Hair/Hero_Hair.Hero_Hair"));
    if (!GroomAsset) return;

    // 2. 创建 Groom 组件
    UGroomComponent* GroomComp = NewObject<UGroomComponent>(this);
    GroomComp->SetGroomAsset(GroomAsset);
    GroomComp->SetEnableSimulation(true); // 启用模拟

    // 3. 附加到角色头部骨骼
    GroomComp->AttachToComponent(GetMesh(), FAttachmentTransformRules::SnapToTargetNotIncludingScale, TEXT("head"));

    // 4. 注册组件
    GroomComp->RegisterComponent();
}
```

### 进阶用法

动态调整毛发参数和处理流送。

```cpp
// 动态调整毛发外观和物理参数
void AMyCharacter::UpdateGroomAppearance(float NewWidth, float NewStiffness)
{
    if (UGroomComponent* Groom = FindComponentByClass<UGroomComponent>())
    {
        // 设置发丝宽度
        Groom->SetHairWidth(NewWidth);
        // 设置物理刚度
        Groom->SetStiffness(NewStiffness);
        // 重置模拟以应用新参数
        Groom->ResetSimulation();
    }
}

// 监听 Groom 缓存流送状态（需要包含 HairStrandsRuntime 模块头文件）
// #include "GroomCacheStreamingManager.h"
void AMyCharacter::CheckGroomStreamingStatus()
{
    // 获取流送管理器并查询特定 GroomCache 的状态
    // FGroomCacheStreamingManager& StreamingManager = FGroomCacheStreamingManager::Get();
    // ... 查询逻辑
}
```

## Demo 示例

一个最小的 Actor 示例，展示如何在 C++ 中创建和配置 Groom。

**MyGroomActor.h**
```cpp
// MyGroomActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyGroomActor.generated.h"

class UGroomAsset;
class UGroomComponent;

UCLASS()
class MYPROJECT_API AMyGroomActor : public AActor
{
    GENERATED_BODY()

public:
    AMyGroomActor();

protected:
    virtual void BeginPlay() override;

    // 在编辑器中指定 Groom 资产
    UPROPERTY(EditAnywhere, Category = "Groom")
    UGroomAsset* GroomAsset;

    // Groom 组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Groom")
    UGroomComponent* GroomComponent;
};
```

**MyGroomActor.cpp**
```cpp
// MyGroomActor.cpp
#include "MyGroomActor.h"
#include "GroomAsset.h"
#include "GroomComponent.h"

AMyGroomActor::AMyGroomActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建根组件
    USceneComponent* Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    SetRootComponent(Root);

    // 创建 Groom 组件
    GroomComponent = CreateDefaultSubobject<UGroomComponent>(TEXT("Groom"));
    GroomComponent->SetupAttachment(Root);
}

void AMyGroomActor::BeginPlay()
{
    Super::BeginPlay();

    // 如果资产已设置，则应用
    if (GroomAsset)
    {
        GroomComponent->SetGroomAsset(GroomAsset);
        // 启用模拟并设置一些默认参数
        GroomComponent->SetEnableSimulation(true);
        GroomComponent->SetStiffness(0.5f);
        GroomComponent->SetDamping(0.3f);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HairStrandsCore` | Groom 资产、组件和核心数据结构的定义。 |
| `HairStrandsRuntime` | 运行时功能，如 Groom 缓存流送管理。 |
| `HairStrandsDeformer` | Groom 的变形器，用于驱动发丝动画。 |
| `HairStrandsSolver` | 物理求解器，用于毛发模拟计算。 |
| `HairStrandsDataflow` | 与 Dataflow 框架集成，用于程序化生成和处理 Groom。 |
| `HairCardGeneratorFramework` | 将发丝数据转换为卡片（Cards）或网格体（Meshes）的框架。 |
| `Niagara` | 用于基于发丝的粒子效果（如发梢的粒子）。 |
| `RenderCore`, `RHI` | 底层渲染和图形硬件接口。 |

## 维护状态

### 近期更新

```
- f50c54b933bf 2025-04-15 Moved the GroomCache streamer registration to its own runtime module since HairStrandsCore uses the PostConfigInit, which happens before the RHI is initialized, but FStreamingManagerCollection has a dependency on the RHI. This is needed to support remote MRQ, which uses -game.
```
*解读：这是一个重要的架构修复，将 GroomCache 流送器的注册从 `HairStrandsCore` 移到了 `HairStrandsRuntime`，以解决初始化顺序依赖问题，确保在远程 Movie Render Queue (MRQ) 等场景下正常工作。*

### 维护评价

-   **创建时间**：该插件于 2019 年创建，是 UE4 时代为数字人类项目（如《黑客帝国觉醒》）开发的核心技术之一。
-   **维护状态**：**活跃维护中**。尽管插件本身已较为成熟，但 Epic 仍在持续修复 bug、优化性能并适配新引擎特性（如 Nanite、Lumen）和新的工作流（如 Dataflow）。
-   **已知限制**：
    1.  默认未启用 (`EnabledByDefault: false`)，需要在项目设置中手动启用。
    2.  对 GPU 性能要求较高，尤其是在开启高质量渲染和物理模拟时。
    3.  从 DCC 工具导入的工作流相对复杂，需要特定的导出设置。
-   **推荐使用**：**强烈推荐**用于任何需要电影级毛发效果的项目，特别是数字人类和高质量生物角色。它是目前 UE 内置的最强大、最完整的毛发解决方案。对于性能敏感的项目，需要仔细利用其 LOD 和卡片转换功能进行优化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HairStrands)
- [官方文档]() (暂无直接链接，可参考引擎文档中的 “Groom” 或 “Hair Strands” 章节)
- [测试用例]() (测试文件通常位于 `Engine/Tests/` 目录下，或插件内部的 `Tests` 文件夹)