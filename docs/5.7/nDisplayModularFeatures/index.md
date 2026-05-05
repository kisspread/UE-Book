# nDisplay Modular Features

> Modular Features for nDisplay

| 属性 | 值 |
|---|---|
| 分类 | Misc |
| 默认启用 | Hidden (需手动启用) |
| 包含内容 | true |
| 模块 | DisplayClusterLightCardExtender (Runtime), DisplayClusterModularFeaturesEditor (Editor) |
| 创建时间 | 2022-09-05 |
| 年龄标签 | 🆕 (≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/nDisplayModularFeatures) | |

## 用途

nDisplayModularFeatures 是 nDisplay 生态系统的模块化扩展框架，提供两个核心能力：

1. **Light Card 舞台演员扩展系统** — 为 nDisplay 的 In-Camera VFX (ICVFX) 工作流中的 Light Card 提供一个基于球面坐标（经度/纬度/距离）的定位接口。Light Card 是放置在 LED Volume 内的虚拟光源和平面，用于在 LED 墙上产生反射、高光或环境照明。本 plugin 定义了 `IDisplayClusterStageActor` 接口，让 Light Card 使用球面坐标系而非世界坐标系进行定位，同时支持 Sequencer 动画同步。

2. **媒体初始化器模块化接口** — 为 nDisplay 的媒体 Tile 配置（如 tiled media output）提供 `IDisplayClusterModularFeatureMediaInitializer` 接口，支持 ICVFX 相机、Viewport 和 Backbuffer 的媒体源/输出初始化，涵盖单播/多播、本地/远程等流传播模式。

本质上，这个 plugin 是一个**接口定义层**——它本身不包含具体实现，而是为其他模块（如 nDisplay 主插件、第三方扩展）提供标准化的扩展点。

## 使用场景

- 你在做 **Virtual Production / LED Volume 拍摄**，需要在 nDisplay 的 ICVFX 相机面板中管理 Light Card 的位置 → 使用 `IDisplayClusterStageActor` 接口
- 你需要为 nDisplay 的 Light Card **添加自定义组件或属性** → 实现 `IDisplayClusterLightCardActorExtender` Modular Feature
- 你在开发 **nDisplay 媒体 Tile 配置**工具，需要初始化 tiled media source/output → 实现 `IDisplayClusterModularFeatureMediaInitializer` 接口
- 你需要让 Light Card 的位置与 **Sequencer 动画** 保持同步 → 使用 `IDisplayClusterLightCardExtenderModule::GetOnSequencerTimeChanged()`

## 蓝图用法

本 plugin 主要是 C++ 接口层，没有直接暴露蓝图节点。但 `FDisplayClusterPositionalParams` 结构体标记了 `BlueprintType`，可在蓝图中使用：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FDisplayClusterPositionalParams` | 球面坐标参数结构体，可在蓝图中读写 | `FDisplayClusterPositionalParams` |

`FDisplayClusterPositionalParams` 的属性均标记为 `EditAnywhere, BlueprintReadWrite`：

| 属性 | 类型 | 说明 | 约束 |
|---|---|---|---|
| `DistanceFromCenter` | `double` | 距离原点的距离 | 无 |
| `Longitude` | `double` | 经度 (度) | 0–360 |
| `Latitude` | `double` | 纬度 (度) | -90–90 |
| `Spin` | `double` | 自旋 (度) | -360–360 |
| `Pitch` | `double` | 俯仰 (度) | -360–360 |
| `Yaw` | `double` | 偏航 (度) | -360–360 |
| `RadialOffset` | `double` | 径向偏移 | 无 |
| `Scale` | `FVector2D` | XY 缩放 | 默认 (1, 1) |

## C++ 用法

### 头文件引入

```cpp
// Light Card 舞台演员接口
#include "StageActor/IDisplayClusterStageActor.h"
#include "StageActor/DisplayClusterPositionalParams.h"

// Light Card 扩展器接口
#include "IDisplayClusterLightCardActorExtender.h"
#include "IDisplayClusterLightCardExtenderModule.h"

// 媒体初始化器接口（编辑器模块）
#include "IDisplayClusterModularFeatureMediaInitializer.h"
```

### 基本用法 — 球面坐标定位

`IDisplayClusterStageActor` 接口让 Actor 使用球面坐标系定位在 nDisplay 舞台上。下面演示如何通过经纬度设置 Light Card 位置：

```cpp
// 假设你的 Actor 实现了 IDisplayClusterStageActor
// 来源: IDisplayClusterStageActor.cpp - SetPositionalParams()
void SetLightCardPosition(IDisplayClusterStageActor* StageActor)
{
    FDisplayClusterPositionalParams Params;
    Params.Longitude = 45.0;           // 东偏北 45°
    Params.Latitude = 15.0;            // 仰角 15°
    Params.DistanceFromCenter = 500.0; // 距离原点 500cm
    Params.Spin = 0.0;
    Params.Pitch = 0.0;
    Params.Yaw = 0.0;
    Params.RadialOffset = 0.0;
    Params.Scale = FVector2D(1.0, 1.0);

    StageActor->SetPositionalParams(Params);
    StageActor->UpdateStageActorTransform(); // 应用到 Actor Transform
}
```

### 基本用法 — 坐标转换

`IDisplayClusterStageActor` 提供了球面坐标与世界 Transform 之间的静态转换函数：

```cpp
// 来源: IDisplayClusterStageActor.cpp - PositionalParamsToActorTransform()
// 球面参数 → 世界 Transform
FTransform WorldTransform = IDisplayClusterStageActor::PositionalParamsToActorTransform(
    Params, OriginTransform);

// 来源: IDisplayClusterStageActor.cpp - TransformToPositionalParams()
// 世界 Transform → 球面参数
FDisplayClusterPositionalParams RecoveredParams =
    IDisplayClusterStageActor::TransformToPositionalParams(
        WorldTransform, OriginTransform, /*RadialOffset=*/ 0.0);
```

### 进阶用法 — 实现 Light Card Actor 扩展器

通过注册 `IDisplayClusterLightCardActorExtender` Modular Feature，可以为 Light Card 添加自定义组件：

```cpp
#include "IDisplayClusterLightCardActorExtender.h"
#include "Components/ActorComponent.h"

class FMyLightCardExtender : public IDisplayClusterLightCardActorExtender
{
public:
    static void Register()
    {
        // 注册为 Modular Feature
        IModularFeatures::Get().RegisterModularFeature(
            IDisplayClusterLightCardActorExtender::ModularFeatureName,
            &Instance);
    }

    // 来源: IDisplayClusterLightCardActorExtender.h
    virtual FName GetExtenderName() const override { return TEXT("MyCustomExtender"); }
    virtual TSubclassOf<UActorComponent> GetAdditionalSubobjectClass() override
    {
        return UMyCustomComponent::StaticClass();
    }

#if WITH_EDITOR
    virtual FName GetCategory() const override { return TEXT("MyCategory"); }
    virtual bool ShouldShowSubcategories() const override { return true; }
#endif

private:
    static FMyLightCardExtender Instance;
};
```

### 进阶用法 — Sequencer 时间同步

在编辑器中监听 Sequencer 的时间变化，同步 Light Card 位置：

```cpp
#include "IDisplayClusterLightCardExtenderModule.h"

void SubscribeToSequencerChanges()
{
    if (IDisplayClusterLightCardExtenderModule::IsAvailable())
    {
        auto& Module = IDisplayClusterLightCardExtenderModule::Get();
        // 来源: IDisplayClusterLightCardExtenderModule.h
        Module.GetOnSequencerTimeChanged().AddLambda(
            [](TWeakPtr<ISequencer> Sequencer)
            {
                // Sequencer 时间已改变，更新 Light Card 位置
                // 注意：Sequencer 关闭时也会触发此回调
            });
    }
}
```

### 进阶用法 — 实现媒体初始化器

为 nDisplay 的 tiled media 提供自定义初始化逻辑：

```cpp
#include "IDisplayClusterModularFeatureMediaInitializer.h"

class FMyMediaInitializer : public IDisplayClusterModularFeatureMediaInitializer
{
public:
    // 来源: IDisplayClusterModularFeatureMediaInitializer.h
    virtual bool IsMediaObjectSupported(const UObject* MediaObject) override
    {
        // 返回是否支持此媒体对象类型
        return Cast<UMyMediaSource>(MediaObject) != nullptr;
    }

    virtual bool AreMediaObjectsCompatible(
        const UObject* MediaSource, const UObject* MediaOutput) override
    {
        return true; // 检查兼容性
    }

    virtual bool GetSupportedMediaPropagationTypes(
        const UObject* MediaSource, const UObject* MediaOutput,
        EMediaStreamPropagationType& OutPropagationTypes) override
    {
        OutPropagationTypes = EMediaStreamPropagationType::LocalUnicast
                            | EMediaStreamPropagationType::Multicast;
        return true;
    }

    virtual void InitializeMediaObjectForTile(
        UObject* MediaObject, const FMediaObjectOwnerInfo& OwnerInfo,
        const FIntPoint& TilePos) override
    {
        // 为 tiled media output 初始化指定 tile 位置
    }

    virtual void InitializeMediaObjectForFullFrame(
        UObject* MediaObject, const FMediaObjectOwnerInfo& OwnerInfo) override
    {
        // 为 full frame media 初始化
    }
};
```

## Demo 示例

一个最小的自定义 Stage Actor 实现：

```cpp
// MyStageActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "StageActor/IDisplayClusterStageActor.h"
#include "StageActor/DisplayClusterPositionalParams.h"
#include "MyStageActor.generated.h"

UCLASS()
class AMyStageActor : public AActor, public IDisplayClusterStageActor
{
    GENERATED_BODY()

public:
    AMyStageActor();

    // IDisplayClusterStageActor 纯虚函数实现
    virtual void SetLongitude(double InValue) override { PositionalParams.Longitude = InValue; }
    virtual double GetLongitude() const override { return PositionalParams.Longitude; }
    virtual void SetLatitude(double InValue) override { PositionalParams.Latitude = InValue; }
    virtual double GetLatitude() const override { return PositionalParams.Latitude; }
    virtual void SetDistanceFromCenter(double InValue) override { PositionalParams.DistanceFromCenter = InValue; }
    virtual double GetDistanceFromCenter() const override { return PositionalParams.DistanceFromCenter; }
    virtual void SetSpin(double InValue) override { PositionalParams.Spin = InValue; }
    virtual double GetSpin() const override { return PositionalParams.Spin; }
    virtual void SetPitch(double InValue) override { PositionalParams.Pitch = InValue; }
    virtual double GetPitch() const override { return PositionalParams.Pitch; }
    virtual void SetYaw(double InValue) override { PositionalParams.Yaw = InValue; }
    virtual double GetYaw() const override { return PositionalParams.Yaw; }
    virtual void SetRadialOffset(double InValue) override { PositionalParams.RadialOffset = InValue; }
    virtual double GetRadialOffset() const override { return PositionalParams.RadialOffset; }
    virtual void SetOrigin(const FTransform& InOrigin) override { Origin = InOrigin; }
    virtual FTransform GetOrigin() const override { return Origin; }
    virtual void SetScale(const FVector2D& InScale) override { PositionalParams.Scale = InScale; }
    virtual FVector2D GetScale() const override { return PositionalParams.Scale; }
    virtual void GetPositionalProperties(FPositionalPropertyArray& OutPropertyPairs) const override {}

private:
    UPROPERTY()
    FDisplayClusterPositionalParams PositionalParams;
    FTransform Origin;
};
```

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "DisplayClusterLightCardExtender"
});
```

## 模块依赖

### DisplayClusterLightCardExtender (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | Actor/Component 基础 |
| `Sequencer` | (仅 Editor) Sequencer 时间同步 |
| `UnrealEd` | (仅 Editor) 编辑器 Gizmo 更新 |

### DisplayClusterModularFeaturesEditor (Editor)

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 基础引擎功能 |
| `UnrealEd` | 编辑器模块支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-26 | `a0ff1f062bb1` | [nDisplay] In-Camera VFX panel makes level dirty | 修复 ICVFX 面板导致关卡被标记为 dirty 的问题，影响 stage actor 交互 |
| 2024-07-31 | `1dd0608a9213` | nDisplay: Propagate RadialOffset changes from LC level instance to ICVFX panel proxy | RadialOffset 参数从 level instance 代理同步到 ICVFX 面板，与 `FDisplayClusterPositionalParams.RadialOffset` 直接相关 |
| 2024-05-15 | `8b89d9f4770e` | [nDisplay] Media tiles configuration dialog for ICVFX cameras | 新增 ICVFX 相机的媒体 Tile 配置对话框，与 `IDisplayClusterModularFeatureMediaInitializer` 接口配合使用 |

### 维护评价

- **创建时间**: 2022 年 9 月，至今约 3.6 年
- **维护状态**: **维护中** — 最近一次更新在 2025 年 9 月（约 7 个月前），是功能修复
- **更新频率**: 低频但持续，每年有 1-2 次实质性更新
- **Beta 状态**: `.uplugin` 标记 `IsBetaVersion=true`，且 `Hidden=true`，说明这是一个实验性内部插件
- **接口稳定性**: 作为接口定义层，API 较稳定，近期更新主要是 bug 修复和增量功能
- **推荐**: 此 plugin 是 nDisplay Virtual Production 工作流的基础设施。如果你在开发 nDisplay 扩展或 Light Card 相关功能，需要依赖此 plugin；如果只是使用 nDisplay 的标准功能，通常不需要直接接触此 plugin。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/nDisplayModularFeatures)
- [IDisplayClusterStageActor 源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/nDisplayModularFeatures/Source/DisplayClusterLightCardExtender/Public/StageActor/IDisplayClusterStageActor.h)
- [IDisplayClusterModularFeatureMediaInitializer 源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/nDisplayModularFeatures/Source/DisplayClusterModularFeaturesEditor/Public/IDisplayClusterModularFeatureMediaInitializer.h)
