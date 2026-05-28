# Animation Sharing

> Plugin to create Shared Animation systems using the Leader-Follower pose functionality

| 属性 | 值 |
|---|---|
| 中文名 | 动画共享 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产，如动画蓝图、状态处理器、设置资产） |
| 模块 | `AnimationSharing` (Runtime), `AnimationSharingEd` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-01-08 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/AnimationSharing) | |

## 用途

Animation Sharing 插件旨在解决大量相同或相似动画角色同时播放动画时的性能问题。它通过“Leader-Follower”（领导者-跟随者）姿势系统，让少量“领导者”角色运行完整的动画蓝图和动画序列，而让大量“跟随者”角色通过共享骨骼网格体组件和动画数据来重现相同的动画效果。

该插件的核心是 `UAnimationSharingManager`，它为每个配置的骨架（Skeleton）创建一个共享实例（`UAnimSharingInstance`），并管理一组预分配的、用于驱动不同动画状态的 `USkeletalMeshComponent`。当场景中有成百上千个使用相同动画状态机逻辑的NPC（如人群、士兵、动物群）时，使用此插件可以显著降低CPU的动画蓝图计算、动画采样和混合开销。

## 使用场景

- **大规模人群模拟**：游戏中需要渲染大量使用相同或相似动画集的NPC，例如城市街道、集会现场、战场等。
- **性能优化**：当动画蓝图或动画序列的采样成本成为瓶颈时，希望通过共享来减少计算量。
- **控制动画状态**：需要根据游戏逻辑（如距离、重要性）动态控制哪些角色播放完整动画，哪些角色使用简化的、共享的动画。
- **平台适配**：需要根据不同平台（主机、PC）的性能，动态调整动画共享的强度（如是否启用混合、最大并发混合数等）。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Animation Sharing Manager` | 获取当前世界的动画共享管理器实例，如果未创建则返回 `None`。 | `UAnimationSharingManager` |
| `Create Animation Sharing Manager` | 使用指定的 `AnimationSharingSetup` 资产，在当前世界中创建并初始化一个动画共享管理器。 | `UAnimationSharingManager` |
| `Register Actor with Skeleton` (BP) | 将一个 Actor 注册到动画共享系统中，需要指定其对应的 `USkeleton`。 | `UAnimationSharingManager` |
| `Animation Sharing Enabled` | 返回动画共享系统在当前世界是否已启用。 | `UAnimationSharingManager` |
| `Set Leader Components Visibility` | 设置所有用于驱动动画的“领导者”骨骼网格体组件的可见性（主要用于调试）。 | `UAnimationSharingManager` |

### 使用示例（蓝图描述）

1.  **初始化**：在游戏模式或关卡蓝图中，使用 `Create Animation Sharing Manager` 节点。需要传入一个预先创建好的 `UAnimationSharingSetup` 资产（在内容浏览器中右键创建）。
2.  **注册角色**：当需要动画共享的 Actor 被生成（Spawn）后，调用 `Register Actor with Skeleton (BP)` 节点，将该 Actor 和它使用的骨架（Skeleton Asset）注册到系统。`UAnimationSharingSetup` 中必须包含对应骨架的配置。
3.  **状态处理**：在 `UAnimationSharingSetup` 资产中，为每个骨架配置“动画状态”（`FAnimationStateEntry`）。你通常需要派生一个 `UAnimationSharingStateProcessor` 的蓝图子类，重写 `Process Actor State` 函数，来根据 Actor 的游戏逻辑（如速度、是否在空中）决定其当前应处于哪个动画状态（一个枚举值）。
4.  **可选配置**：在 Setup 资产中调整 `Scalability Settings`，例如设置在不同平台上是否启用状态间的混合过渡（`Use Blend Transitions`）、混合的重要性阈值（`Blend Significance Value`）等。

## C++ 用法

### 头文件引入

```cpp
#include "AnimationSharingManager.h"
#include "AnimationSharingSetup.h"
#include "AnimationSharingTypes.h"
```

### 基本用法

以下代码演示了如何在 C++ 中初始化动画共享系统并注册一个 Actor。

```cpp
// 在合适的地方（如 GameMode::InitGame 或自定义管理器中）
#include "AnimationSharingManager.h"
#include "AnimationSharingSetup.h"

// 1. 获取或创建动画共享管理器
UAnimationSharingManager* AnimSharingManager = UAnimationSharingManager::GetAnimationSharingManager(GetWorld());
if (!AnimSharingManager)
{
    // 假设 SetupAsset 是一个编辑器中创建的 UAnimationSharingSetup* 变量
    const UAnimationSharingSetup* SetupAsset = LoadObject<UAnimationSharingSetup>(nullptr, TEXT("/Game/Path/To/YourAnimSharingSetup"));
    if (SetupAsset)
    {
        UAnimationSharingManager::CreateAnimationSharingManager(GetWorld(), SetupAsset);
        AnimSharingManager = UAnimationSharingManager::GetAnimationSharingManager(GetWorld());
    }
}

// 2. 注册一个 Actor
if (AnimSharingManager && MyActor && MySkeleton)
{
    AnimSharingManager->RegisterActorWithSkeleton(MyActor, MySkeleton, FUpdateActorHandle()); // 通常不需要自定义代理
}
```

*来源参考：`AnimationSharingManager.h` 中 `GetAnimationSharingManager`, `CreateAnimationSharingManager`, `RegisterActorWithSkeleton` 的函数声明。*

### 进阶用法

你可以通过 `UAnimationSharingManager` 的指针访问更多控制功能：

```cpp
// 更新某个已注册 Actor 的重要性值（通常由 SignificanceManager 驱动）
uint32 ActorHandle = ...; // 从注册时或内部数据结构中获取
float NewSignificance = 0.5f;
AnimSharingManager->UpdateSignificanceForActorHandle(ActorHandle, NewSignificance);

// 手动卸载所有角色（例如在关卡卸载前）
AnimSharingManager->UnregisterAllActors();

// 调试：打印当前动画共享系统的内部状态到日志
AnimSharingManager->LogData();
```

## Demo 示例

一个最小化的 C++ 类，用于在场景中创建动画共享管理器并注册一个测试 Actor。

```cpp
// AnimSharingDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AnimSharingDemoActor.generated.h"

class UAnimationSharingSetup;
class UAnimationSharingManager;

UCLASS()
class AAnimSharingDemoActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AAnimSharingDemoActor();

protected:
	virtual void BeginPlay() override;

public:	
	/** 要使用的动画共享设置资产 */
	UPROPERTY(EditAnywhere, Category = "Animation Sharing")
	TObjectPtr<UAnimationSharingSetup> SharingSetup;

	/** 需要注册到共享系统的测试 Actor 的类 */
	UPROPERTY(EditAnywhere, Category = "Animation Sharing")
	TSubclassOf<AActor> TestActorClass;

private:
	UPROPERTY(Transient)
	TObjectPtr<UAnimationSharingManager> CachedManager;

	void SpawnAndRegisterTestActors();
};
```

```cpp
// AnimSharingDemoActor.cpp
#include "AnimSharingDemoActor.h"
#include "AnimationSharingManager.h"
#include "AnimationSharingSetup.h"
#include "Engine/World.h"

AAnimSharingDemoActor::AAnimSharingDemoActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AAnimSharingDemoActor::BeginPlay()
{
	Super::BeginPlay();

	if (GetWorld()->IsGameWorld() && SharingSetup)
	{
		// 创建动画共享管理器
		bool bSuccess = UAnimationSharingManager::CreateAnimationSharingManager(GetWorld(), SharingSetup);
		if (bSuccess)
		{
			CachedManager = UAnimationSharingManager::GetAnimationSharingManager(GetWorld());
			if (CachedManager)
			{
				// 延迟一帧注册测试角色，确保管理器完全初始化
				GetWorldTimerManager().SetTimerForNextTick(this, &AAnimSharingDemoActor::SpawnAndRegisterTestActors);
			}
		}
	}
}

void AAnimSharingDemoActor::SpawnAndRegisterTestActors()
{
	if (TestActorClass && CachedManager)
	{
		FActorSpawnParameters SpawnParams;
		SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

		// 生成并注册几个测试角色
		for (int32 i = 0; i < 10; ++i)
		{
			FVector SpawnLocation = GetActorLocation() + FVector(100.f * i, 0.f, 0.f);
			AActor* SpawnedActor = GetWorld()->SpawnActor<AActor>(TestActorClass, SpawnLocation, FRotator::ZeroRotator, SpawnParams);
			if (SpawnedActor)
			{
				// 注意：这里需要知道 SpawnedActor 的骨架，通常通过其 SkeletalMeshComponent 获取
				// USkeleton* ActorSkeleton = SpawnedActor->FindComponentByClass<USkeletalMeshComponent>()->GetSkeletalMeshAsset()->GetSkeleton();
				// CachedManager->RegisterActorWithSkeleton(SpawnedActor, ActorSkeleton);
			}
		}
	}
}
```

## 模块依赖

从 `AnimationSharing.Build.cs` 的依赖分析，使用此插件的主要模块需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `SignificanceManager` | 插件运行时依赖，用于根据 Actor 的重要性值决定动画更新的优先级。 |
| `TargetPlatform` | 用于获取当前平台的信息，以应用 `FPerPlatformBool/Float/Int` 定义的平台特定设置。 |

**说明**：你的项目模块如果需要直接调用 `UAnimationSharingManager` 的 C++ 接口，需要在 `.Build.cs` 文件中添加对 `AnimationSharing` 模块的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件代码中的日志宏从旧式 `UE_LOG` 迁移到新的 `UE_LOGF`。 |
| 2025-11-11 | `ca342f27` | Ensure that Additive and Blend components have their LOD forced to 0, otherwise it will be impacted | 修复了附加动画和混合组件的LOD（细节层次）未被强制设置为0的问题，避免被自动LOD影响动画效果。 |
| 2025-11-06 | `c51e7614` | Fixed issue with additive instances not taking into account actor running an on-demand state or bein | 修复了附加动画实例在计算时未正确考虑 Actor 当前处于“按需”（On-Demand）动画状态或正在混合中的问题。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 代码格式化：将插件中的默认析构函数 `{}` 改为使用 `= default`。 |
| 2025-10-27 | `e5a984c3` | Add per platform option in animsharing for sending curves during blends. | 功能增强：在动画共享的可扩展性设置中，新增了按平台控制“在混合期间是否发送曲线”的选项（`RequireCurvesDuringBlends`）。 |

### 维护评价

- **年龄与活跃度**：该插件创建于2019年，距今已超过6年。从提交记录看，在2025年底至2026年初仍有持续的功能修复和代码改进，表明它处于 **活跃维护** 状态，并非废弃插件。
- **维护方**：由 Epic Games 官方创建和维护，质量有保障。
- **功能完整性**：该插件功能明确且较为完整，专注于解决特定性能问题。近期更新集中在修复边缘情况和增强平台适配性。
- **推荐使用**：**推荐**在需要进行大规模动画角色优化的项目中使用。由于其久经考验且官方维护，稳定性和兼容性较好。对于新项目，如果预计会有大量相似动画角色，建议在项目初期就规划并集成此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/AnimationSharing)
- 官方文档：暂无（`.uplugin` 中 `DocsURL` 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/AnimationSharing/Tests) (路径推测，具体以仓库为准)