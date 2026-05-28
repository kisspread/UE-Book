# Water Advanced

> Collection of easy to use water simulation systems built on the Niagara Fluids and Water plugins

| 属性 | 值 |
|---|---|
| 中文名 | 高级水域模拟 |
| 分类 | Water |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `WaterAdvanced` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-04-15 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/WaterAdvanced) | |

## 用途

WaterAdvanced 是一个基于 Niagara Fluids 和 Water 插件构建的**高级水域交互模拟系统**。它解决的核心问题是：在已有的 Water 插件（水体渲染/高度图）和 Niagara Fluids（流体模拟）之上，提供一套开箱即用的**浅水物理交互**方案。

具体功能包括：
- **浅水模拟子系统（Shallow Water Subsystem）**：自动追踪玩家 Pawn 和其他碰撞体与水体的交互，将碰撞信息通过 Niagara Data Channel 传递给流体模拟，实现角色在水面行走时产生波纹、冲击波等效果
- **河流模拟组件（Shallow Water River Component）**：为河流水体提供基于 Niagara 的实时或烘焙流体模拟，支持源/汇水体连接、底部轮廓捕获、多材质渲染状态切换（实时/烘焙/调试）
- **FFT 海洋法线补丁（FFT Ocean Patch Subsystem）**：为海洋水面提供 FFT 生成的法线贴图，可被河流模拟共享使用
- **物理资产覆盖（Physics Asset Overrides）**：允许通过 GameplayTag 为不同角色/车辆指定不同的物理资产碰撞体，以调整水面交互效果

简单来说：**Water 插件画水面，Niagara Fluids 做流体模拟，WaterAdvanced 负责让角色真正"踩"进水面并产生物理反馈。**

## 使用场景

- 你在做一个开放世界游戏，需要角色走过浅水区域时产生波纹和水花 → 用 BasicShallowWaterSubsystem
- 你需要河流水体有真实的流动、漩涡和岸边泡沫效果 → 用 ShallowWaterRiver Actor
- 你的游戏有船只、车辆等不同载具需要与水面交互 → 通过 PhysicsAssetOverrides 配置不同碰撞体
- 你需要射击、投掷物等在水面产生冲击波 → 用 RegisterImpact 蓝图节点
- 你需要海洋表面有高质量的法线细节用于河流模拟过渡 → 用 FFTOceanPatchSubsystem

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterImpact` | 注册一个水面冲击（位置、速度、半径），产生波纹效果 | `UShallowWaterSubsystem` |
| `SetWaterBodyMIDParameters` | 手动为指定水体设置材质实例参数 | `UShallowWaterSubsystem` |
| `SetPaused` | 暂停/恢复河流模拟 | `UShallowWaterRiverComponent` |
| `GetAllOverlappingWaterBodiesAndUpdateCollisionTrackers` | 获取当前所有与碰撞体重叠的水体并更新追踪器 | `UShallowWaterSubsystem` |
| `AddCollisionTrackerForActor` | 为自定义 Actor 添加水面碰撞追踪（用于鱼饵、原木等漂浮物） | `UShallowWaterSubsystem` |
| `RemoveCollisionTrackerForActor` | 移除指定 Actor 的碰撞追踪器 | `UShallowWaterSubsystem` |

### 使用示例

**1. 注册水面冲击效果**

当手雷爆炸或角色跳入水中时，调用 RegisterImpact：
```
[事件] → RegisterImpact
  ImpactPosition: 爆炸位置（世界坐标）
  ImpactVelocity: 冲击方向速度
  ImpactRadius: 影响半径
```

**2. 追踪漂浮物的水面交互**

当鱼饵/木头等物体落入水中时：
```
[Actor Begin Overlap with Water] → AddCollisionTrackerForActor
  CollisionTrackerActor: 漂浮物 Actor
  MaxLifespan: 60（秒）
  
[Actor Destroyed] → RemoveCollisionTrackerForActor
  CollisionTrackerActor: 同一个 Actor
```

**3. 河流模拟暂停控制**

```
[按钮点击] → SetPaused
  bPause: true
```

## C++ 用法

### 头文件引入

```cpp
#include "ShallowWaterSubsystem.h"
#include "ShallowWaterRiverActor.h"
#include "ShallowWaterPhysicsAssetOverridesDataAsset.h"
```

### 基本用法

**注册水面冲击（来自 ShallowWaterSubsystem.h）**

```cpp
// 获取浅水子系统
UShallowWaterSubsystem* ShallowWaterSubsystem = GetWorld()->GetSubsystem<UShallowWaterSubsystem>();

// 当子弹命中水面时注册冲击
if (ShallowWaterSubsystem)
{
    FVector ImpactPosition = HitResult.ImpactPoint;
    FVector ImpactVelocity = HitResult.ImpactNormal * -1000.0f;
    float ImpactRadius = 50.0f;
    
    ShallowWaterSubsystem->RegisterImpact(ImpactPosition, ImpactVelocity, ImpactRadius);
}
```

**为漂浮物体添加碰撞追踪**

```cpp
// 来自 ShallowWaterSubsystem.h
// 假设你的鱼饵 Actor 类有一个引用到 ShallowWaterSubsystem
UShallowWaterSubsystem* Subsystem = GetWorld()->GetSubsystem<UShallowWaterSubsystem>();

// 鱼饵落入水中时开始追踪
Subsystem->AddCollisionTrackerForActor(this, 60.0f);

// 鱼饵被销毁时移除追踪
Subsystem->RemoveCollisionTrackerForActor(this);
```

### 进阶用法

**自定义浅水子系统（继承 UShallowWaterSubsystem）**

```cpp
// 来自 ShallowWaterSubsystem.h - 这是一个抽象基类，需要继承实现
// BasicShallowWaterSubsystem 是最简单的实现示例

UCLASS(Blueprintable, Transient)
class UMyGameShallowWaterSubsystem : public UShallowWaterSubsystem
{
    GENERATED_BODY()

public:
    UMyGameShallowWaterSubsystem();

    virtual bool ShouldCreateSubsystem(UObject* Outer) const override
    {
        // 只在游戏世界中创建
        return Super::ShouldCreateSubsystem(Outer);
    }

    virtual bool IsShallowWaterAllowedToInitialize() const override
    {
        // 可以通过 Game Feature Plugin 控制是否激活
        return Super::IsShallowWaterAllowedToInitialize();
    }

    // 自定义车辆标签返回，用于区分不同类型载具
    virtual FGameplayTagContainer GetVehicleTags(FShallowWaterCollisionContext Context) const override;

    // 自定义碰撞上下文获取逻辑（例如：驾驶船只时返回船的 SKM）
    virtual TOptional<FShallowWaterCollisionContext> GetCollisionContextFromPawn(APawn* InPawn) const override;

    // 自定义子弹碰撞通道
    virtual ECollisionChannel GetImpactCollisionChannel() override
    {
        return ECC_GameTraceChannel1; // 自定义通道
    }
};
```

**通过数据资产覆盖物理碰撞体**

```cpp
// 来自 ShallowWaterSubsystem.h
// 为 Game Feature Plugin 注册自定义的物理资产覆盖
const UShallowWaterPhysicsAssetOverridesDataAsset* MyOverrides = LoadObject<UShallowWaterPhysicsAssetOverridesDataAsset>(
    nullptr, TEXT("/Game/DataAssets/DA_MyWaterPhysicsOverrides"));

if (ShallowWaterSubsystem && MyOverrides)
{
    ShallowWaterSubsystem->RegisterPhysicsAssetProxiesDataAsset(MyOverrides);
}
```

## Demo 示例

**自定义浅水子系统头文件**

```cpp
// MyShallowWaterSubsystem.h
#pragma once

#include "CoreMinimal.h"
#include "ShallowWaterSubsystem.h"
#include "MyShallowWaterSubsystem.generated.h"

UCLASS(Blueprintable, Transient)
class MYGAME_API UMyShallowWaterSubsystem : public UShallowWaterSubsystem
{
    GENERATED_BODY()

public:
    UMyShallowWaterSubsystem();

    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual bool IsShallowWaterAllowedToInitialize() const override;
    virtual float GetColliderMaxRange() const override;
    virtual TArray<APawn*> GetPawnsInRange(const bool bShouldSortBySignificance = false) const override;
};
```

**自定义浅水子系统实现**

```cpp
// MyShallowWaterSubsystem.cpp
#include "MyShallowWaterSubsystem.h"
#include "GameFeaturesSubsystem.h"

UMyShallowWaterSubsystem::UMyShallowWaterSubsystem()
{
}

bool UMyShallowWaterSubsystem::ShouldCreateSubsystem(UObject* Outer) const
{
    // 检查 Game Feature Plugin 是否激活
    return Super::ShouldCreateSubsystem(Outer);
}

bool UMyShallowWaterSubsystem::IsShallowWaterAllowedToInitialize() const
{
    return Super::IsShallowWaterAllowedToInitialize();
}

float UMyShallowWaterSubsystem::GetColliderMaxRange() const
{
    // 自定义碰撞检测范围（厘米）
    return 15000.0f;
}

TArray<APawn*> UMyShallowWaterSubsystem::GetPawnsInRange(const bool bShouldSortBySignificance) const
{
    // 可以自定义哪些 Pawn 参与水面交互
    return Super::GetPawnsInRange(bShouldSortBySignificance);
}
```

**注册水面冲击的 Actor 组件**

```cpp
// WaterImpactComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "WaterImpactComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYGAME_API UWaterImpactComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UWaterImpactComponent();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Water Impact")
    float ImpactRadius = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Water Impact")
    float ImpactStrength = 2000.0f;

    UFUNCTION(BlueprintCallable, Category = "Water Impact")
    void TriggerWaterImpact(FVector Position, FVector Direction);

    // 用于漂浮物：开始追踪水面交互
    UFUNCTION(BlueprintCallable, Category = "Water Impact")
    void StartWaterTracking();

    // 用于漂浮物：停止追踪
    UFUNCTION(BlueprintCallable, Category = "Water Impact")
    void StopWaterTracking();
};
```

```cpp
// WaterImpactComponent.cpp
#include "WaterImpactComponent.h"
#include "ShallowWaterSubsystem.h"

UWaterImpactComponent::UWaterImpactComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UWaterImpactComponent::TriggerWaterImpact(FVector Position, FVector Direction)
{
    UWorld* World = GetWorld();
    if (!World) return;

    UShallowWaterSubsystem* Subsystem = World->GetSubsystem<UShallowWaterSubsystem>();
    if (!Subsystem) return;

    FVector Velocity = Direction.GetSafeNormal() * ImpactStrength;
    Subsystem->RegisterImpact(Position, Velocity, ImpactRadius);
}

void UWaterImpactComponent::StartWaterTracking()
{
    UWorld* World = GetWorld();
    if (!World) return;

    UShallowWaterSubsystem* Subsystem = World->GetSubsystem<UShallowWaterSubsystem>();
    if (!Subsystem) return;

    AActor* Owner = GetOwner();
    if (Owner)
    {
        Subsystem->AddCollisionTrackerForActor(Owner, 60.0f);
    }
}

void UWaterImpactComponent::StopWaterTracking()
{
    UWorld* World = GetWorld();
    if (!World) return;

    UShallowWaterSubsystem* Subsystem = World->GetSubsystem<UShallowWaterSubsystem>();
    if (!Subsystem) return;

    AActor* Owner = GetOwner();
    if (Owner)
    {
        Subsystem->RemoveCollisionTrackerForActor(Owner);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Niagara` | Niagara 粒子系统，用于水面波纹/流体模拟 |
| `NiagaraFluids` | Niagara 流体模拟插件，提供浅水/FFT 海洋模拟能力 |
| `Water` | 核心水体插件，提供 WaterBody/WaterZone 等基础设施 |
| `GameplayTags` | 用于物理资产覆盖的标签系统 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `e8cf76b3` | Fix to not tick on server (PIE or in packaged build) | 修复服务端（PIE 或打包后）误执行 Tick 的问题 |
| 2026-04-30 | `662b54c8` | expose SceneCaptureLODDistanceFactor on Niagara DI | 在 Niagara Data Interface 上暴露场景捕获 LOD 距离因子 |
| 2026-04-28 | `e1f9e83e` | only populate bottom contour on newly created SW River actors when in game thread | 仅在游戏线程中为新创建的河流 Actor 填充底部轮廓数据 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 格式化日志宏 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 在即将到来的头文件清理之前补充 include 引用 |

### 维护评价

- **状态**：活跃维护中
- **创建时间**：2024-04-15，从 Restricted 状态迁移到 Experimental
- **最近更新**：最近 3 个月内有多次实质性更新，包括 bug 修复（服务端 Tick 修复、线程安全修复）和功能增强（LOD 因子暴露）
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需手动在插件设置中启用
- **API 稳定性**：版本号 0.1，API 尚不稳定，可能随版本更新发生 breaking changes
- **推荐使用**：适合实验性项目或预生产阶段使用。如果需要稳定的水面交互方案，建议等待该插件毕业到正式版。底层依赖的 Water 和 NiagaraFluids 插件均为成熟模块，核心架构是可靠的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/WaterAdvanced)
- [官方文档]()（暂无）