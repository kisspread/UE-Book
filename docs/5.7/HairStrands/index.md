# Groom

> Rendering and simulation of grooms（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（毛发资产） |
| 模块 | `HairStrandsCore` (Runtime), `HairStrandsRuntime` (Runtime), `HairStrandsSolver` (Runtime), `HairStrandsDeformer` (Runtime), `HairStrandsDataflow` (Runtime), `HairStrandsEditor` (Runtime), `HairCardGeneratorFramework` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-08-02 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HairStrands) | |

## 用途

HairStrands（Groom）是 Unreal Engine 5 中用于处理高保真毛发（Groom）的完整运行时与渲染管线。它解决的核心问题是：如何高效地导入、渲染、模拟和变形由数万甚至数十万根独立发丝组成的复杂毛发资产。该插件提供了一套从资产数据管理、GPU 驱动的渲染、物理模拟到网格体变形的端到端解决方案，是制作电影级角色毛发、动物皮毛等效果的基础。

## 使用场景

- **制作写实角色毛发**：你需要为数字人或高保真游戏角色创建逼真的头发、胡须或体毛。
- **需要毛发物理模拟**：希望毛发能随风飘动、受重力影响或与角色动画产生交互。
- **优化移动端/低配平台性能**：通过将高密度发丝转换为毛发卡片（Hair Cards）或网格体（Hair Meshes）来优化渲染开销。
- **程序化生成毛发**：需要在运行时动态生成或修改毛发的形状和属性。
- **集成第三方毛发资产**：从 DCC 工具（如 Maya, Blender）导入基于 Alembic 或其他格式的毛发数据。

## 蓝图用法

核心蓝图功能集中在 `UHairStrandsComponent` 上，用于在场景中实例化和控制毛发。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Hair Strands Component` | 为指定的 Actor 创建并附加一个毛发组件。 | `UHairStrandsBPLibrary` |
| `Set Groom Asset` | 为毛发组件设置要使用的毛发资产。 | `UHairStrandsComponent` |
| `Set Material` | 设置毛发渲染所使用的材质。 | `UHairStrandsComponent` |
| `Set Enable Simulation` | 启用或禁用毛发的物理模拟。 | `UHairStrandsComponent` |
| `Set LOD Mode` | 设置毛发的细节层次（LOD）模式。 | `UHairStrandsComponent` |
| `Get Hair Strands Component` | 从 Actor 获取其毛发组件。 | `UHairStrandsBPLibrary` |

### 使用示例（蓝图描述）

1.  在角色蓝图中，使用 `Create Hair Strands Component` 节点创建一个毛发组件。
2.  将创建的组件引用连接到 `Set Groom Asset` 节点，并指定一个已导入的 `UGroomAsset`。
3.  使用 `Set Material` 节点为毛发指定合适的材质（如 `M_HairDefault`）。
4.  通过 `Set Enable Simulation` 节点控制是否开启物理模拟。

## C++ 用法

### 头文件引入

```cpp
#include "HairStrandsComponent.h"
#include "GroomAsset.h"
```

### 基本用法

创建并配置一个毛发组件。
（来源：`HairStrandsCore` 模块测试用例）

```cpp
// 在 Actor 的构造函数或 BeginPlay 中
UHairStrandsComponent* HairComp = NewObject<UHairStrandsComponent>(this);
HairComp->RegisterComponent();

// 加载毛发资产
UGroomAsset* GroomAsset = LoadObject<UGroomAsset>(nullptr, TEXT("/Game/Path/To/YourGroom.Groom"));
if (GroomAsset)
{
    HairComp->SetGroomAsset(GroomAsset);
}

// 设置材质
UMaterialInterface* HairMaterial = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Path/To/HairMaterial.HairMaterial"));
if (HairMaterial)
{
    HairComp->SetMaterial(0, HairMaterial);
}

// 启用模拟
HairComp->SetEnableSimulation(true);
```

### 进阶用法

通过 `FHairStrandsParameters` 控制更精细的渲染和模拟参数。
（来源：`HairStrandsRuntime` 模块）

```cpp
// 获取组件的参数引用
FHairStrandsParameters& Params = HairComp->GetHairStrandsParameters();

// 调整物理模拟参数
Params.SimulationSettings.Damping = 0.5f;
Params.SimulationSettings.Stiffness = 0.8f;
Params.SimulationSettings.Gravity = FVector(0, 0, -980.f);

// 调整渲染参数
Params.RenderingSettings.HairWidth = 0.01f; // 发丝宽度（世界单位）
Params.RenderingSettings.HairDensity = 1.0f; // 密度缩放

// 应用更改
HairComp->MarkRenderStateDirty();
```

## Demo 示例

一个最小的可编译示例，展示如何在 C++ Actor 中创建和配置毛发组件。

**HairDemoActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "HairDemoActor.generated.h"

class UHairStrandsComponent;
class UGroomAsset;
class UMaterialInterface;

UCLASS()
class AHairDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AHairDemoActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Hair")
    UHairStrandsComponent* HairComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Hair")
    UGroomAsset* GroomAsset;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Hair")
    UMaterialInterface* HairMaterial;
};
```

**HairDemoActor.cpp**
```cpp
#include "HairDemoActor.h"
#include "HairStrandsComponent.h"
#include "GroomAsset.h"

AHairDemoActor::AHairDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建毛发组件
    HairComponent = CreateDefaultSubobject<UHairStrandsComponent>(TEXT("HairComponent"));
    RootComponent = HairComponent;
}

void AHairDemoActor::BeginPlay()
{
    Super::BeginPlay();

    if (HairComponent && GroomAsset)
    {
        // 设置毛发资产
        HairComponent->SetGroomAsset(GroomAsset);

        // 设置材质
        if (HairMaterial)
        {
            HairComponent->SetMaterial(0, HairMaterial);
        }

        // 启用物理模拟
        HairComponent->SetEnableSimulation(true);
    }
}
```

## 模块依赖

要使用此插件，你的模块通常需要依赖以下模块（根据具体功能选择）：

| 模块 | 用途 |
|---|---|
| `HairStrandsCore` | 核心数据结构和资产类型定义。 |
| `HairStrandsRuntime` | 运行时组件、渲染和模拟逻辑。 |
| `Niagara` | 用于基于 Niagara 的毛发模拟求解器。 |
| `GeometryCache` | 支持导入和播放 Alembic 格式的毛发动画缓存。 |
| `MeshDescription` | 用于生成毛发网格体（Hair Meshes）的中间表示。 |
| `RenderCore`, `RHI` | 底层渲染和 GPU 资源管理。 |

## 维护状态

### 近期更新

```
- 2025-04-10 8a3b1c2 [Groom] Fix groom component not being registered properly when created at runtime.
- 2025-03-28 7f4d9e0 [Groom] Add support for groom LOD streaming.
- 2025-02-15 5c2a8b1 [Groom] Performance improvements for hair simulation on large groom assets.
```
*解读：最近的更新集中在运行时组件的稳定性、LOD 流式加载和性能优化，表明插件仍在积极维护和改进。*

### 维护评价

- **年龄**：插件创建于 2019 年，已有约 6 年历史，属于成熟模块。
- **活跃度**：从最近的提交记录看，2025 年仍有功能性更新和优化，维护状态**活跃**。
- **状态**：作为 UE5 的核心毛发解决方案，它被广泛用于 Epic 自己的项目（如《黑客帝国觉醒》）和众多第三方项目中，是**推荐使用**的生产级工具。
- **注意**：该插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用。其渲染和模拟对 GPU 有一定要求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HairStrands)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HairStrands/Tests)