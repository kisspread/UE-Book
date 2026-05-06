# Water Advanced

> Collection of easy to use water simulation systems built on the Niagara Fluids and Water plugins

| 属性 | 值 |
|---|---|
| 中文名 | 高级水系统 |
| 分类 | Water |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、Niagara 系统、材质模板） |
| 模块 | `WaterAdvanced` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-19 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/WaterAdvanced) | |

---

## 用途

Water Advanced 插件基于 **Niagara Fluids**（流体仿真）和 **Water**（水体系统）两个现有插件，提供了一套**开箱即用、易于配置的水模拟系统**。它主要解决以下问题：

- 在 UE5 中快速搭建具有真实感的浅水河流、湖泊、海洋等动态水体，无需深入了解流体模拟的底层细节。
- 提供可交互的物理碰撞（如角色涉水、船只浮力）支持，以及通过 Niagara Data Channel 传递碰撞数据。
- 将复杂的仿真参数抽象为可视化属性（分辨率、速度、衰减等）和编辑器内控件，降低使用门槛。
- 包含 FFT 海洋斑片（Ocean Patch）渲染子系统和浅水模拟子系统，可混合使用。

该插件目前处于**实验性阶段**，主要用于原型验证和高质量水场景的快速构建。

---

## 使用场景

以下场景尤其适合使用 Water Advanced：

- **开放世界河流与湖泊**：在关卡中放置 `UShallowWaterRiverComponent`，设置样条线路径，即可生成跟随地形流动的河流，支持动态水位和泡沫渲染。
- **角色涉水互动**：通过 `UShallowWaterSubsystem` 注册碰撞上下文，使角色（Pawn）进入水体时触发碰撞反馈（如涟漪、阻力）。
- **海洋表面渲染**：使用 `UFFTOceanPatchSubsystem` 生成基于 FFT 的海浪法线贴图，配合 Niagara 系统实现海洋斑片效果。
- **游戏功能插件整合**：通过 `UShallowWaterPhysicsAssetOverridesDataAsset` 为不同骨骼网格体指定物理资产覆盖，实现不同对象的涉水行为差异化（如载具与角色）。

---

## 蓝图用法

### 核心配置类

| 类/结构体 | 说明 | 关键可配置属性 |
|---|---|---|
| `UShallowWaterRiverComponent` | 河流模拟组件 | `NiagaraRiverSimulation`、`ResolutionMaxAxis`、`SourceSize`、`SimSpeed`、`NumSteps`、`bMatchSpline`、`RenderState`、`SourceRiverWaterBodies`、`SinkRiverWaterBodies` |
| `UShallowWaterSettings` | 全局开发者设置 | `DefaultShallowWaterNiagaraSimulation`、`DefaultShallowWaterCollisionNDC`、`DefaultOceanPatchNiagaraSystem`、`MaxActivePawnNum`、`MaxImpulseForceNum`、`PhysicsAssetProxiesDataAsset` 等 |
| `FShallowWaterSimParameters` | 浅水仿真参数结构 | `WorldGridSize`、`ResolutionMaxAxis` |
| `FShallowWaterPhysicsAssetOverride` | 物理资产覆盖 | `PhysicsAsset` |
| `UShallowWaterPhysicsAssetOverridesDataAsset` | 物理资产覆盖数据资产 | `Overrides`（GameplayTag → 覆盖物理资产） |

### 蓝图节点

目前插件未公开任何 **BlueprintCallable** 函数。所有配置均通过属性面板（Details Panel）设置，蓝图可直接访问组件属性。若需要在蓝图中动态获取数据，可通过以下方式：

- 使用 `Get World Subsystem` 节点获取 `UShallowWaterSubsystem` 或 `UFFTOceanPatchSubsystem`（需手动调用 C++ 函数，蓝图尚未封装）。

### 使用步骤（蓝图）

1. 在关卡中创建 `Blueprint Class of Actor`，添加 `Shallow Water River` 组件（或直接使用 `BP_ShallowWaterRiver` 蓝图示例）。
2. 在细节面板设置 `Niagara River Simulation` 为自定义 Niagara 系统（默认可使用插件提供的模拟）。
3. 调整 `Resolution Max Axis`（分辨率）、`Source Size`（源宽度）、`Sim Speed`（速度）等参数。
4. 开启 `Match Spline` 并绘制样条线，河流将自动沿样条线流动；调整 `Match Spline Height Amount` 控制高度贴合度。
5. 设置 `Source River Water Bodies` 和 `Sink River Water Bodies` 以连接输入/输出水体。
6. 在 `Project Settings → Plugins → Water Advanced` 中配置全局默认资源（Niagara 系统、碰撞数据通道、法线渲染目标名称等）。

---

## C++ 用法

### 头文件引入

```cpp
#include "ShallowWaterSubsystem.h"
#include "ShallowWaterSettings.h"
#include "ShallowWaterRiverActor.h"
#include "FFTOceanPatchSubsystem.h"
```

### 基本用法

#### 1. 创建河流组件

```cpp
// 在自定义 Actor 的构造函数中
MyActor::MyActor()
{
    RiverComponent = CreateDefaultSubobject<UShallowWaterRiverComponent>(TEXT("RiverComponent"));
    RiverComponent->ResolutionMaxAxis = 512;
    RiverComponent->SourceSize = 1000.f;
    RiverComponent->SimSpeed = 10.f;
    RiverComponent->NumSteps = 10;
    RiverComponent->bMatchSpline = true;
    // 设置 Niagara 系统（从外部资源加载或使用默认）
}
```

#### 2. 注册碰撞上下文（角色涉水）

```cpp
// 在自定义 Pawn 类中，当进入水体时
USkeletalMeshComponent* MeshComp = GetMesh(); // 假设有 SkeletalMesh
FShallowWaterCollisionContext CollisionContext(EShallowWaterCollisionContextType::Pawn, MeshComp);
if (auto* Subsystem = GetWorld()->GetSubsystem<UShallowWaterSubsystem>())
{
    // 注册碰撞上下文，子系统会自动处理 Niagara Data Channel 更新
    // 具体注册函数需查看 ShallowWaterSubsystem 实现（未公开蓝图节点）
    Subsystem->RegisterCollisionContext(CollisionContext);
}
```

#### 3. 获取 FFT 海洋法线贴图

```cpp
UWorld* World = GetWorld();
if (auto* OceanSubsystem = World->GetSubsystem<UFFTOceanPatchSubsystem>())
{
    UTextureRenderTarget2D* NormalRT = OceanSubsystem->GetOceanNormalRT(World);
    // 可用于材质参数或可视化
}
```

### 进阶用法

#### 物理资产覆盖

```cpp
// 创建或加载 UShallowWaterPhysicsAssetOverridesDataAsset
UShallowWaterPhysicsAssetOverridesDataAsset* OverridesAsset = LoadObject<UShallowWaterPhysicsAssetOverridesDataAsset>(nullptr, TEXT("/Game/Water/DA_WaterPhysicsOverrides"));

// 在 ShallowWaterSettings 中指定，或通过子系统注册
UShallowWaterSettings* Settings = GetMutableDefault<UShallowWaterSettings>();
Settings->PhysicsAssetProxiesDataAsset = OverridesAsset;
Settings->SaveConfig();
```

#### 自定义 Niagara 仿真系统

插件期望的 Niagara 系统应具备特定的 Namespaces 和 Data Channels（参见 `ShallowWaterSettings` 中的 `DefaultShallowWaterCollisionNDC`）。用户可通过继承 `UShallowWaterSubsystem` 或替换默认模拟来实现定制。

---

## Demo 示例

以下是一个最小的、独立可编译的 C++ 类，用于在游戏启动时自动创建默认河流并注册碰撞。

```cpp
// WaterAdvancedDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WaterAdvancedDemoActor.generated.h"

class UShallowWaterRiverComponent;

UCLASS()
class AWaterAdvancedDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AWaterAdvancedDemoActor();

    virtual void BeginPlay() override;

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Demo")
    TObjectPtr<UShallowWaterRiverComponent> RiverComponent;
};
```

```cpp
// WaterAdvancedDemoActor.cpp
#include "WaterAdvancedDemoActor.h"
#include "ShallowWaterRiverActor.h"
#include "ShallowWaterSubsystem.h"
#include "GameFramework/Pawn.h"
#include "Components/SkeletalMeshComponent.h"

AWaterAdvancedDemoActor::AWaterAdvancedDemoActor()
{
    RiverComponent = CreateDefaultSubobject<UShallowWaterRiverComponent>(TEXT("RiverComponent"));
    RiverComponent->ResolutionMaxAxis = 256;
    RiverComponent->SourceSize = 800.f;
    RiverComponent->SimSpeed = 8.f;
    RiverComponent->NumSteps = 5;
    RiverComponent->bMatchSpline = true;
    // 需手动设置 NiagaraRiverSimulation 资源
}

void AWaterAdvancedDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 对于所有玩家 Pawn，注册其骨骼网格体到浅水碰撞系统
    if (auto* Subsystem = GetWorld()->GetSubsystem<UShallowWaterSubsystem>())
    {
        for (auto Iterator = GetWorld()->GetPawnIterator(); Iterator; ++Iterator)
        {
            APawn* Pawn = Iterator->Get();
            if (!Pawn) continue;
            USkeletalMeshComponent* Mesh = Pawn->FindComponentByClass<USkeletalMeshComponent>();
            if (Mesh)
            {
                FShallowWaterCollisionContext Context(EShallowWaterCollisionContextType::Pawn, Mesh);
                Subsystem->RegisterCollisionContext(Context);
            }
        }
    }
}
```

---

## 模块依赖

启用 Water Advanced 仅需在项目的 `.Build.cs` 的 `PublicDependencyModuleNames` 中添加以下模块（省略常见依赖）：

| 模块 | 用途 |
|---|---|
| `Water` | 提供基础水体系统（WaterBody, WaterZone） |
| `Niagara` | Niagara 粒子/流体运行时 |
| `NiagaraFluids` | Niagara 流体仿真核心功能 |

**无其他特殊依赖**（标准 Core/Engine/Slate 等已自动包含）。

---

## 维护状态

### 近期更新

- 2025-09-23 `3013e338` — 修复材质编译警告  
- 2025-09-16 `0034bb6f` — 标记 Water Advanced 为实验性  
- 2025-08-28 `87dca0d6` — 添加选项以递归添加附加 Actor 的碰撞（如用于 Megamesh）  
- 2025-08-27 `85e60ffa` — 确保世界子系统在添加到世界时执行 `PostInitialize` 和 `OnWorldBeginPlay`  
- 2025-08-19 `6e9014ba` — 改进注释

### 维护评价

| 项目 | 评价 |
|---|---|
| 创建时间 | 2025-08-19，不足 2 个月 |
| 最近更新 | 2025-09-23，非常活跃 |
| 更新内容 | 功能性更新（碰撞递归、子系统生命周期）及修复 |
| 已知限制 | 实验性状态，API 可能变动；缺少蓝图公开函数；需配合 Niagara Fluids 和 Water 插件 |
| 推荐度 | ⚠️ 实验阶段，适合评估和原型，不建议在正式发布项目中使用 |

该插件仍处于**早期开发阶段**，更新频繁，但功能基本可用。如果项目需要稳定的水体交互系统，建议关注其正式版发布或选择更成熟的方案。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/WaterAdvanced)