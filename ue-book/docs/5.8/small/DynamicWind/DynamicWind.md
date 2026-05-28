# Dynamic Wind

> Extremely experimental dynamic wind support for Nanite foliage.

| 属性 | 值 |
|---|---|
| 中文名 | 动态风力 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DynamicWind` (Runtime), `DynamicWindEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DynamicWind) | |

## 用途

该插件为 **Nanite 植被**（Nanite Foliage）提供动态风力效果支持。其核心是通过一个基于场景的子系统和GPU计算，为使用了 `UDynamicWindSkeletalData` 的骨骼网格体提供实时、高效的风动画模拟，从而让树木、草地、灌木等植被在风力作用下产生自然、动态的摇曳效果。它解决的关键问题是：在启用Nanite的高性能渲染管线下，如何高效地实现大规模植被的动态风效果。

## 使用场景

- **开放世界游戏中的树木与植被**：你有一个需要大规模树木和草地，并且启用了 Nanite 的项目，希望它们能随风摆动，增强场景的沉浸感和真实感。
- **需要精细风力控制的场景**：你希望风不是简单、全局、一致的，而是能根据风力方向、速度、纹理（用于模拟湍流）以及植被自身结构（如树干、树枝）产生差异化的动画。
- **追求性能与视觉平衡**：传统骨骼动画对大量植被开销巨大，此插件旨在利用GPU为 Nanite 植被提供高效的风动画解决方案。

## 蓝图用法

此插件的核心蓝图接口位于 `UDynamicWindSubsystem` 子系统中，用于在游戏运行时控制和查询风力状态。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Update Wind Parameters` | 更新当前世界动态风力的模拟参数（如风向、风速、中心点、纹理等）。 | `UDynamicWindSubsystem` |
| `Get Blended Wind Amplitude` | 获取当前经过混合处理的风力强度值。 | `UDynamicWindSubsystem` |

### 使用示例（蓝图描述）

1.  **获取子系统**：在任意蓝图（如 `PlayerController` 或 `GameMode`）中，使用 `Get World Subsystem` 节点，类选择 `UDynamicWindSubsystem`，以获取该子系统的实例。
2.  **设置风力参数**：创建一个 `FDynamicWindParameters` 结构体变量，在其中设置你想要的 `Wind Direction`、`Wind Speed`、`Simulation Center`（风力影响的中心）等属性。然后将该结构体连到 `Update Wind Parameters` 节点的 `Parameters` 引脚上。
3.  **周期性更新**：为了模拟风力的变化（如风速波动），你可以在 `Event Tick` 或自定义的定时器中，周期性地修改 `FDynamicWindParameters` 中的值（例如随机扰动 `WindSpeed` 或 `WindAmplitude`），并调用 `Update Wind Parameters` 进行更新。

## C++ 用法

### 头文件引入

```cpp
#include "DynamicWindSubsystem.h"
#include "DynamicWindParameters.h"
```

### 基本用法

获取子系统并更新风力参数。

```cpp
// 在某个 Actor 或 PlayerController 的 BeginPlay 或 Tick 函数中
#include "DynamicWindSubsystem.h"
#include "DynamicWindParameters.h"

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取动态风力子系统
    if (UDynamicWindSubsystem* WindSubsystem = GetWorld()->GetSubsystem<UDynamicWindSubsystem>())
    {
        // 设置新的风力参数
        FDynamicWindParameters WindParams;
        WindParams.WindDirection = FVector(1.0f, 0.0f, 0.0f); // 设置风向
        WindParams.WindSpeed = 20.0f; // 设置风速
        WindParams.SimulationCenter = GetActorLocation(); // 将模拟中心设置在当前Actor位置

        // 应用风力参数
        WindSubsystem->UpdateWindParameters(WindParams);
    }
}
```
*来源文件: `Public/DynamicWindSubsystem.h`, `Public/DynamicWindParameters.h`*

### 进阶用法

在 Tick 中动态调整风力，模拟阵风效果。

```cpp
void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (UDynamicWindSubsystem* WindSubsystem = GetWorld()->GetSubsystem<UDynamicWindSubsystem>())
    {
        // 查询当前混合后的风力强度
        float CurrentAmplitude = WindSubsystem->GetBlendedWindAmplitude();

        // 基于某种逻辑（如噪声函数或时间）计算新的振幅
        float NewAmplitude = FMath::Sin(GetWorld()->GetTimeSeconds() * 0.5f) * 0.5f + 0.8f;

        // 仅当振幅变化显著时更新，避免每帧调用UpdateWindParameters
        if (FMath::Abs(NewAmplitude - CurrentAmplitude) > 0.05f)
        {
            FDynamicWindParameters WindParams = CurrentWindParams; // 保留其他参数
            WindParams.WindAmplitude = NewAmplitude;
            WindSubsystem->UpdateWindParameters(WindParams);
            CurrentWindParams = WindParams;
        }
    }
}
```

## Demo 示例

一个最小化的 Actor 示例，用于在游戏中创建并控制一个动态风力源。

**DynamicWindSourceActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DynamicWindSourceActor.generated.h"

class UDynamicWindSubsystem;

UCLASS()
class ADynamicWindSourceActor : public AActor
{
	GENERATED_BODY()

public:
	ADynamicWindSourceActor();

protected:
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaTime) override;

	/** 风力强度变化的速度 */
	UPROPERTY(EditAnywhere, Category = "DynamicWind")
	float WindChangeSpeed = 0.3f;

	/** 风力的基准速度 */
	UPROPERTY(EditAnywhere, Category = "DynamicWind")
	float BaseWindSpeed = 15.0f;

private:
	UPROPERTY()
	TObjectPtr<UDynamicWindSubsystem> CachedWindSubsystem;

	float CurrentWindAmplitude = 0.0f;
};
```

**DynamicWindSourceActor.cpp**
```cpp
#include "DynamicWindSourceActor.h"
#include "DynamicWindSubsystem.h"
#include "DynamicWindParameters.h"

ADynamicWindSourceActor::ADynamicWindSourceActor()
{
	PrimaryActorTick.bCanEverTick = true;
}

void ADynamicWindSourceActor::BeginPlay()
{
	Super::BeginPlay();
	// 缓存子系统指针以提高性能
	CachedWindSubsystem = GetWorld()->GetSubsystem<UDynamicWindSubsystem>();
}

void ADynamicWindSourceActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (CachedWindSubsystem)
	{
		// 使用正弦函数模拟自然的风力强度波动
		CurrentWindAmplitude = FMath::Sin(GetWorld()->GetTimeSeconds() * WindChangeSpeed) * 0.4f + 0.8f;

		FDynamicWindParameters WindParams;
		WindParams.WindDirection = GetActorForwardVector(); // 使用Actor朝向作为风向
		WindParams.WindSpeed = BaseWindSpeed;
		WindParams.WindAmplitude = CurrentWindAmplitude;
		WindParams.SimulationCenter = GetActorLocation();

		CachedWindSubsystem->UpdateWindParameters(WindParams);
	}
}
```

## 模块依赖

此插件的 `DynamicWind` (Runtime) 模块除了标准核心依赖外，还需要以下模块：

| 模块 | 用途 |
|---|---|
| `SkeletalMeshComponents` | 用于处理骨骼网格体相关的功能。 |
| `Engine` | UE 核心引擎模块。 |
| `RenderCore` | 提供渲染核心功能，如 ByteAddressBuffer。 |
| `Renderer` | 核心渲染器，用于与场景和渲染线程交互。 |

*依赖关系来源: `Source/DynamicWind/DynamicWind.Build.cs`*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `8b5eabf3` | FastGeo: Support GPU animated instanced skinned meshes. | 支持GPU动画的实例化蒙皮网格，可能扩展了动态风力的应用范围。 |
| 2026-04-14 | `b1c9fc96` | Fixed dynamic wind ES31 compilation error not supporting bit fields in structured buffers. | 修复了在ES3.1环境下因结构化缓冲区不支持位域而导致的编译错误。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移至UE_LOGF，属于内部维护性更新。 |
| 2026-04-09 | `39e82b40` | Refactored ASTP to support layers and blend spaces. | 重构了动画系统转换提供器(ASTP)以支持层和混合空间，这可能影响了风动画的混合逻辑。 |
| 2026-04-02 | `ac7816b3` | Implement dynamic wind for GPU skin and unified bone indices which both use a bone map. | 实现了对使用骨骼映射的GPU蒙皮和统一骨骼索引的动态风力支持，是一项重要功能扩展。 |

### 维护评价

- **创建时间**：插件于2025年8月创建，至今约1年。
- **活跃度**：从git历史看，在2026年4月至5月期间有**非常活跃的功能更新和bug修复**，包括对新渲染特性的支持（FastGeo， GPU Skin）、ES3.1兼容性修复以及核心逻辑重构。
- **状态**：插件仍处于**实验性**阶段（`IsExperimentalVersion: true`， `EnabledByDefault: false`），但正在被积极开发和完善。
- **推荐**：**可以关注和试用**。该插件针对的是Nanite植被风动画这一高级且前沿的渲染需求，虽然标记为实验性且默认禁用，但近期更新表明它正在被主动推进。对于需要此功能的项目，建议在开发分支中进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DynamicWind)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DynamicWind/Tests) (插件内可能包含测试目录)