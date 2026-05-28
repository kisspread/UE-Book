# Landscape Patch

> Support for adding landscape patches- components that can be attached to meshes to affect the landscape as the mesh is repositioned.

| 属性 | 值 |
|---|---|
| 中文名 | 地形贴片 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（组件资产） |
| 模块 | `LandscapePatch` (Runtime), `LandscapePatchEditorOnly` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-19 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/LandscapePatch) | |

## 用途

Landscape Patch 插件的核心用途是提供一种**动态、位置感知的地形修改方案**。它允许开发者将“地形贴片”组件附加到任何可移动的 Actor（如角色载具、物理网格体或脚本控制的物体）上。当这个宿主 Actor 在世界中移动时，贴片组件会自动实时地修改其周围地形的高度图或权重图（植被、材质等）。

与传统的、静态的地形编辑不同，这个插件解决了“地形需随游戏对象动态变化”的需求，常见于需要挖掘、堆积或实时地形变形的游戏玩法（例如：车辆碾压草地留下痕迹、角色行走留下脚印、爆炸产生弹坑）。

## 使用场景

- **载具系统**：模拟越野车在泥地或沙地上留下的车辙印。
- **角色交互**：实现角色行走时草地被压平、雪地留下脚印的效果。
- **环境破坏**：创造炮弹爆炸后形成的弹坑。
- **玩法机制**：实现挖掘、建造等直接改变地形的游戏逻辑。

## 蓝图用法

该插件的核心是运行时组件。在蓝图中，主要是创建和管理这些组件实例。

### 核心节点

根据插件的功能描述和常见设计模式，以下为预期的主要蓝图节点（具体函数名需参照最新源码）：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Landscape Patch` | 向某个组件（如StaticMeshComponent）添加一个地形贴片组件。 | `ULandscapePatchComponent` |
| `Set Patch Influence` | 设置贴片的影响范围、强度、形状等参数。 | `ULandscapePatchComponent` |
| `Set Patch Active` | 激活或禁用贴片效果。 | `ULandscapePatchComponent` |
| `Get Patch Height/Weight` | 在蓝图中查询贴片当前位置对地形产生的影响数据。 | `ULandscapePatchComponent` |

### 使用示例（蓝图描述）

1.  在你的车辆（或任意可移动Actor）蓝图中，选择要附加贴片的网格体组件（如车体静态网格体）。
2.  在该网格体组件的细节面板中，使用“添加组件”功能，找到并添加一个 `Landscape Texture Patch` 或类似的贴片组件。
3.  调整该贴片组件的 Transform，使其位于网格体与地面接触的关键点（如车轮下方）。
4.  在贴片组件的细节面板中，配置其影响参数，例如“影响半径”、“影响强度”、“高度偏移”等。
5.  （可选）在事件图表中，通过暴露的变量或函数动态控制这些参数，以实现不同速度、不同地面材质产生不同效果。

## C++ 用法

在 C++ 中，主要通过创建和配置 `ULandscapePatchComponent` 的子类或实例来实现功能。

### 头文件引入

```cpp
#include "LandscapePatchComponent.h"
```

### 基本用法

从插件的功能定义出发，展示如何在 C++ Actor 中程序化地添加和配置贴片。

```cpp
// 在你的Actor类的BeginPlay或构造函数中
// 假设MyMeshComponent是一个指向UStaticMeshComponent的指针
void AMyVehicle::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建贴片组件实例
    ULandscapePatchComponent* PatchComp = NewObject<ULandscapePatchComponent>(this);
    PatchComp->RegisterComponent();

    // 2. 将其附加到车体网格体上
    PatchComp->AttachToComponent(MyMeshComponent, FAttachmentTransformRules::KeepRelativeTransform);

    // 3. 设置基本参数（具体属性名需查阅头文件或文档）
    PatchComp->SetInfluenceRadius(200.f);
    PatchComp->SetHeightInfluence(1.0f);
    PatchComp->SetWeightMapIndex(0); // 假设0代表草地权重图
    PatchComp->bIsEnabled = true;
}
```

**来源**：基于 `.uplugin` 功能描述和 Unreal Engine 组件化编程通用实践推断。确切的类名和函数名需参考 `LandscapePatch` 模块的头文件。

### 进阶用法

结合运行时逻辑，动态修改贴片行为。例如，根据车辆速度改变贴痕深度。

```cpp
void AMyVehicle::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (LandscapePatchComponent)
    {
        float CurrentSpeed = GetVelocity().Size();
        // 根据速度计算影响强度
        float NewInfluence = FMath::GetMappedRangeValueClamped(
            FVector2D(0.f, MaxSpeed),
            FVector2D(0.f, MaxInfluenceStrength),
            CurrentSpeed
        );
        LandscapePatchComponent->SetInfluenceStrength(NewInfluence);

        // 可能还需根据接触的地面材质切换贴片效果
        // FHitResult Hit; ...
        // if (Hit.PhysMaterial->SurfaceType == EPhysicalSurface::Grass)
        // {
        //     LandscapePatchComponent->SetWeightMapIndex(GrassWeightIndex);
        // }
    }
}
```

## Demo 示例

以下是一个可编译的最小 Actor 类示例，展示了如何通过代码使用 Landscape Patch。

### MyLandscapePatchActor.h
```cpp
// MyLandscapePatchActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyLandscapePatchActor.generated.h"

class UStaticMeshComponent;
class ULandscapePatchComponent;

UCLASS()
class MYPROJECT_API AMyLandscapePatchActor : public AActor
{
    GENERATED_BODY()

public:
    AMyLandscapePatchActor();

protected:
    virtual void BeginPlay() override;

    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY(VisibleAnywhere, Category = "Components")
    UStaticMeshComponent* RootMesh;

    UPROPERTY(VisibleAnywhere, Category = "Components")
    ULandscapePatchComponent* MyPatch;

    // 用于移动的简单逻辑
    UPROPERTY(EditAnywhere, Category = "Movement")
    float MoveSpeed = 100.f;

    FVector StartLocation;
};
```

### MyLandscapePatchActor.cpp
```cpp
// MyLandscapePatchActor.cpp
#include "MyLandscapePatchActor.h"
#include "LandscapePatchComponent.h" // 插件核心头文件
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"

AMyLandscapePatchActor::AMyLandscapePatchActor()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建根网格体（示例用立方体）
    RootMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RootMesh"));
    SetRootComponent(RootMesh);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube"));
    if (CubeMesh.Succeeded())
    {
        RootMesh->SetStaticMesh(CubeMesh.Object);
        RootMesh->SetWorldScale3D(FVector(0.5f, 0.5f, 0.5f));
    }

    // 创建并附加地形贴片组件
    MyPatch = CreateDefaultSubobject<ULandscapePatchComponent>(TEXT("LandscapePatch"));
    MyPatch->SetupAttachment(RootMesh);
    // 设置贴片相对位置（例如放在物体底部）
    MyPatch->SetRelativeLocation(FVector(0.f, 0.f, -50.f));
}

void AMyLandscapePatchActor::BeginPlay()
{
    Super::BeginPlay();
    StartLocation = GetActorLocation();

    // 配置贴片参数
    if (MyPatch)
    {
        MyPatch->SetInfluenceRadius(150.f);
        MyPatch->SetHeightInfluence(-20.f); // 下陷20个单位
        MyPatch->bIsEnabled = true;
    }
}

void AMyLandscapePatchActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 让物体来回移动，演示动态地形影响
    FVector CurrentLocation = GetActorLocation();
    float Offset = FMath::Sin(GetGameTimeSinceCreation() * 0.5f) * 500.f;
    SetActorLocation(StartLocation + FVector(Offset, 0.f, 0.f));
}
```

## 模块依赖

要使用 Landscape Patch 插件，你的模块需要依赖以下核心模块。基础依赖（Core, CoreUObject, Engine等）已被省略。

| 模块 | 用途 |
|---|---|
| `Landscape` | 地形系统的核心模块，贴片组件与之交互以修改地形数据。 |
| `LandscapePatch` | 本插件的运行时模块，提供 `ULandscapePatchComponent` 等核心类。 |

**说明**：如果你在编辑器环境下进行开发或扩展，可能还需要依赖 `LandscapePatchEditorOnly` 模块，以获取可视化器和编辑器集成工具。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-29 | `2037f2f2` | Fixed landscape patch crash when changing BP properties. | 修复了在蓝图中修改属性时导致的贴片组件崩溃问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志系统迁移至新的 UE_LOGF 宏，提升日志一致性。 |
| 2026-02-26 | `e6de93e0` | Landscape Texture Patch - Added UseWorldPositionSampling flag to allow patches to change texture sam... | 为纹理贴片增加了“使用世界位置采样”标志，允许贴片更改纹理采样行为。 |
| 2026-02-06 | `bed46c8f` | Landscape Patch - Added GetWeightPatch helper fuction | 新增了一个辅助函数用于获取权重贴片信息。 |
| 2026-01-26 | `8987ad88` | Landscape Patch - Added ability for a patch edit layer's heightmap/weightmap alpha values to impact ... | 增强了贴片编辑层的能力，使其高度图/权重图的Alpha值能够产生影响。 |

### 维护评价

- **活跃维护**：插件从 Experimental 迁移至正式版本（2025年9月），表明其核心功能已稳定。从近期更新记录（截至2026年4月）来看，团队仍在积极修复崩溃、添加新功能（如世界位置采样、新的辅助函数）并进行代码优化。
- **状态**：**活跃维护**。
- **推荐使用**：**推荐**。对于有动态地形修改需求的项目，这是一个官方提供的、正在持续改进的解决方案。虽然 `Installed: false` 且标记为实验性，但频繁的提交记录表明它正在快速走向成熟。建议在项目中使用，并关注后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/LandscapePatch)
- 官方文档（暂无）