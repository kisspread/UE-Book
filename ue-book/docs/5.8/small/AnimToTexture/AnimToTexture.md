# AnimToTexture

> Converts SkeletalMesh Animations into Textures

| 属性 | 值 |
|---|---|
| 中文名 | 动画烘焙纹理 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、示例蓝图） |
| 模块 | `AnimToTexture` (Runtime), `AnimToTextureEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-03-09 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AnimToTexture) | |

## 用途

`AnimToTexture` 插件的核心目标是解决大量实例化静态网格体的动画播放性能问题。它将骨骼网格体（SkeletalMesh）的动画数据烘焙到纹理中，然后让一个对应的静态网格体（StaticMesh）在材质中读取这些纹理数据，从而在顶点着色器中重现动画。

这个插件存在的主要意义是：
1.  **性能优化**：相比于传统的骨骼动画（Skinned Mesh），这种方法无需在CPU端进行复杂的蒙皮计算，而是将计算转移到GPU，非常适合渲染大量同类型但动画不同步的物体（如人群、森林、大量怪物）。
2.  **支持实例化渲染**：通过与 `UInstancedStaticMeshComponent` 配合，可以实现海量实例的动画播放。
3.  **数据资产驱动**：所有烘焙配置和输出信息都封装在一个 `UAnimToTextureDataAsset` 中，便于管理和调用。

简而言之，当你需要渲染成千上万个带有独立动画的相同模型时，传统骨骼动画的性能开销会变得无法接受，此时 `AnimToTexture` 提供了一个高效的GPU驱动动画方案。

## 使用场景

-   你正在开发一个大型战略游戏或MMO，需要在场景中放置成千上万的树木、草丛，并希望它们能随风摆动，且摆动效果各异。
-   你制作了一个僵尸或虫群游戏，需要同屏渲染大量同类型但处于不同动画状态的敌人。
-   你需要为一片森林或草地生成随风摇曳的动画，但不想为每棵树或每根草都使用独立的骨骼网格体和动画蓝图。

## 蓝图用法

蓝图用法主要围绕 `UAnimToTextureDataAsset` 数据资产的配置和 `UAnimToTextureInstancePlaybackLibrary` 函数库的调用展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetupInstancedMeshComponent` | 为 `UInstancedStaticMeshComponent` 分配实例并初始化用于存储动画播放数据的 `CustomData`。`bAutoPlay` 参数决定了后续是使用 `AutoPlayData` 还是 `FrameData`。 | `UAnimToTextureInstancePlaybackLibrary` |
| `BatchUpdateInstancesAutoPlayData` | 批量更新所有实例的变换（Transform）和自动播放数据（`FAnimToTextureAutoPlayData`）。适用于引擎时间驱动动画的场景。 | `UAnimToTextureInstancePlaybackLibrary` |
| `BatchUpdateInstancesFrameData` | 批量更新所有实例的变换（Transform）和帧数据（`FAnimToTextureFrameData`）。适用于需要精确控制动画帧的场景。 | `UAnimToTextureInstancePlaybackLibrary` |
| `UpdateInstanceAutoPlayData` / `UpdateInstanceFrameData` | 更新单个实例的自动播放数据或帧数据。 | `UAnimToTextureInstancePlaybackLibrary` |
| `GetAutoPlayDataFromDataAsset` | 根据 `DataAsset` 和动画索引，生成用于播放的 `AutoPlayData`。 | `UAnimToTextureInstancePlaybackLibrary` |
| `GetFrameDataFromDataAsset` | 根据 `DataAsset`、动画索引和时间，计算当前帧和前一帧，生成 `FrameData`（支持运动模糊）。 | `UAnimToTextureInstancePlaybackLibrary` |
| `GetIndexFromAnimSequence` | 在 `DataAsset` 的动画序列列表中查找指定动画序列的索引。 | `UAnimToTextureDataAsset` |
| `Get Static Mesh` / `Get Skeletal Mesh` | 获取数据资产中关联的静态/骨骼网格体。 | `UAnimToTextureDataAsset` |

### 使用示例（蓝图描述）

1.  **烘焙准备**：
    *   创建 `UAnimToTextureDataAsset`。
    *   在数据资产详情中，设置 `SkeletalMesh`（源动画模型）、`StaticMesh`（目标静态模型）以及需要烘焙的 `AnimSequences`（动画序列列表）。
    *   根据需求配置 `Mode`（Vertex 或 Bone）、`Precision`、纹理尺寸等参数。
    *   通过编辑器工具（在 `UAnimToTextureEditor` 模块中）执行烘焙操作，生成位置、旋转等纹理。

2.  **运行时播放（自动播放模式）**：
    *   获取一个 `UInstancedStaticMeshComponent`。
    *   调用 `SetupInstancedMeshComponent` 节点，传入组件和实例数量，`bAutoPlay` 设为 `true`。
    *   在每帧或需要更新时，调用 `GetAutoPlayDataFromDataAsset` 获取某个动画的播放参数（可设置 `TimeOffset` 和 `PlayRate` 实现差异化）。
    *   调用 `BatchUpdateInstancesAutoPlayData` 更新所有实例，传入对应的 `Transform` 数组和 `AutoPlayData` 数组。

3.  **运行时播放（手动控制帧模式）**：
    *   同样先调用 `SetupInstancedMeshComponent`，`bAutoPlay` 设为 `false`。
    *   在每帧更新时，调用 `GetFrameDataFromDataAsset`，传入当前游戏时间，获取 `FrameData`。
    *   调用 `BatchUpdateInstancesFrameData` 更新所有实例。

## C++ 用法

C++ 用法与蓝图流程类似，但提供了更精细的控制和调试能力。

### 头文件引入

```cpp
#include "AnimToTextureDataAsset.h"
#include "AnimToTextureInstancePlaybackHelpers.h"
```

### 基本用法

以下示例展示了如何配置和触发纹理烘焙（通常在编辑器工具或命令行中执行）。

```cpp
// 假设已创建 UAnimToTextureDataAsset 指针 DataAsset
UAnimToTextureDataAsset* DataAsset = ...;

// 1. 配置数据资产
DataAsset->SkeletalMesh = SkeletalMeshPath; // 设置源骨骼网格体
DataAsset->StaticMesh = StaticMeshPath;     // 设置目标静态网格体
DataAsset->Mode = EAnimToTextureMode::Bone; // 使用骨骼模式
DataAsset->Precision = EAnimToTexturePrecision::SixteenBits; // 使用16位精度

// 添加动画序列
FAnimToTextureAnimSequenceInfo AnimInfo;
AnimInfo.AnimSequence = SomeAnimSequence;
AnimInfo.bEnabled = true;
DataAsset->AnimSequences.Add(AnimInfo);

// 2. 执行烘焙 (通常由编辑器模块中的函数完成，此处仅为示意)
// AnimToTextureUtils::BakeAnimations(DataAsset);

// 3. 在材质中，需要使用插件提供的材质函数读取烘焙的纹理数据。
```

*来源：基于 `UAnimToTextureDataAsset` 类的属性定义。*

### 进阶用法

以下示例展示了如何在运行时使用实例化组件播放烘焙的动画。

```cpp
#include "Components/InstancedStaticMeshComponent.h"

// 在Actor的BeginPlay中初始化
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    UInstancedStaticMeshComponent* ISMComp = FindComponentByClass<UInstancedStaticMeshComponent>();
    if (ISMComp && AnimDataAsset)
    {
        // 1. 初始化组件，分配CustomData空间
        UAnimToTextureInstancePlaybackLibrary::SetupInstancedMeshComponent(ISMComp, NumInstances, true);
        
        // 2. 为每个实例准备播放数据
        TArray<FAnimToTextureAutoPlayData> AutoPlayDataArray;
        TArray<FTransform> TransformArray;
        for (int32 i = 0; i < NumInstances; ++i)
        {
            FAnimToTextureAutoPlayData AutoPlayData;
            // 从DataAsset获取基础动画数据
            UAnimToTextureInstancePlaybackLibrary::GetAutoPlayDataFromDataAsset(AnimDataAsset, 0, AutoPlayData);
            // 添加随机偏移，实现动画不同步
            AutoPlayData.TimeOffset = FMath::FRandRange(0.f, 10.f);
            AutoPlayDataArray.Add(AutoPlayData);
            
            TransformArray.Add(FTransform(FVector(i * 200.f, 0, 0))); // 随机放置
        }

        // 3. 批量更新
        UAnimToTextureInstancePlaybackLibrary::BatchUpdateInstancesAutoPlayData(ISMComp, AutoPlayDataArray, TransformArray);
    }
}

// 在每帧更新中 (例如在Tick函数里)
void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // AutoPlayData使用引擎时间，通常无需每帧更新Transform和Data。
    // 如果需要更新Transform（如物体移动），则再次调用BatchUpdateInstances...。
}
```

*来源：基于 `UAnimToTextureInstancePlaybackLibrary` 类的公有函数。*

## Demo 示例

**注意**：此插件主要功能是数据烘焙（Editor）和运行时播放（Runtime），完整的Demo通常包含编辑器工具调用和材质设置，以下为最小化的运行时C++示例头文件和源文件。

### MyAnimatedISMCube.h

```cpp
// 版权 Epic Games, Inc. 保留所有权利。

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AnimToTextureDataAsset.h"
#include "MyAnimatedISMCube.generated.h"

class UInstancedStaticMeshComponent;
struct FAnimToTextureAutoPlayData;

UCLASS()
class MYPROJECT_API AMyAnimatedISMCube : public AActor
{
	GENERATED_BODY()
	
public:	
	AMyAnimatedISMCube();

protected:
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaTime) override;

private:
	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UInstancedStaticMeshComponent> InstancedMeshComponent;

	UPROPERTY(EditAnywhere, Category="Animation")
	TObjectPtr<UAnimToTextureDataAsset> AnimDataAsset;

	UPROPERTY(EditAnywhere, Category="Animation")
	int32 NumInstances = 100;

	UPROPERTY(EditAnywhere, Category="Animation")
	int32 AnimIndex = 0;

	UPROPERTY(Transient)
	TArray<FAnimToTextureAutoPlayData> InstanceAutoPlayData;
};
```

### MyAnimatedISMCube.cpp

```cpp
// 版权 Epic Games, Inc. 保留所有权利。

#include "MyAnimatedISMCube.h"
#include "AnimToTextureInstancePlaybackHelpers.h"
#include "Components/InstancedStaticMeshComponent.h"

AMyAnimatedISMCube::AMyAnimatedISMCube()
{
	PrimaryActorTick.bCanEverTick = true;

	InstancedMeshComponent = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("InstancedMesh"));
	RootComponent = InstancedMeshComponent;
}

void AMyAnimatedISMCube::BeginPlay()
{
	Super::BeginPlay();

	if (AnimDataAsset)
	{
		// 设置静态网格体资产
		InstancedMeshComponent->SetStaticMesh(AnimDataAsset->GetStaticMesh());

		// 1. 初始化组件和CustomData
		if (UAnimToTextureInstancePlaybackLibrary::SetupInstancedMeshComponent(InstancedMeshComponent, NumInstances, true))
		{
			// 2. 为每个实例生成初始播放数据
			InstanceAutoPlayData.SetNum(NumInstances);
			TArray<FTransform> InstanceTransforms;
			InstanceTransforms.Reserve(NumInstances);

			for (int32 i = 0; i < NumInstances; ++i)
			{
				// 获取基础自动播放数据
				UAnimToTextureInstancePlaybackLibrary::GetAutoPlayDataFromDataAsset(AnimDataAsset, AnimIndex, InstanceAutoPlayData[i]);
				// 随机时间偏移，使动画错开
				InstanceAutoPlayData[i].TimeOffset = FMath::FRandRange(0.0f, 5.0f);
				
				// 随机放置实例
				FTransform NewTransform(FRotator::ZeroRotator, FVector(FMath::FRandRange(-500.0f, 500.0f), FMath::FRandRange(-500.0f, 500.0f), 0.0f));
				InstanceTransforms.Add(NewTransform);
			}

			// 3. 批量设置实例数据
			UAnimToTextureInstancePlaybackLibrary::BatchUpdateInstancesAutoPlayData(InstancedMeshComponent, InstanceAutoPlayData, InstanceTransforms);
		}
	}
}

void AMyAnimatedISMCube::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// 对于AutoPlay模式，引擎时间驱动动画，通常无需每帧更新CustomData。
	// 如果需要更新实例的Transform（例如移动物体），则需调用BatchUpdateInstancesAutoPlayData。
	// 此处为演示目的，每帧重新应用一次数据（实际项目中应避免）。
	if (AnimDataAsset && InstancedMeshComponent)
	{
		TArray<FTransform> CurrentTransforms;
		for (int32 i = 0; i < InstancedMeshComponent->GetNumRenderInstances(); ++i)
		{
			FTransform OutTransform;
			InstancedMeshComponent->GetInstanceTransform(i, OutTransform, true);
			CurrentTransforms.Add(OutTransform);
		}
		UAnimToTextureInstancePlaybackLibrary::BatchUpdateInstancesAutoPlayData(InstancedMeshComponent, InstanceAutoPlayData, CurrentTransforms);
	}
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RenderCore` | 处理纹理创建、读写等底层图形操作。 |
| `ImageWriteQueue` | 将烘焙的纹理数据异步写入磁盘文件。 |
| `MeshDescription` | 提供网格体顶点、三角形等数据结构的访问和操作接口，用于烘焙过程中的网格体数据处理。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移至UE_LOGF，统一日志格式。 |
| 2025-10-07 | `dcc26116` | - Fixed up plugins that have both Base and Default ini files, and one plugin (WebSocketNetworking) t... | 修复了包含Base和Default INI文件的插件配置问题（此插件可能受影响）。 |
| 2025-08-08 | `7213adb2` | [AnimToTexture] Added SkeletalMesh MeshDescription functions. (not used) | 为骨骼网格体添加了MeshDescription相关函数，但当前未在插件主逻辑中使用。 |
| 2025-08-07 | `1aee06f6` | [AnimToTexture] Fixed Baking RigidBodies | 修复了烘焙刚体（RigidBodies）动画时的错误。 |
| 2025-08-06 | `785cdd6d` | Fixup API macro usage | 修正了`UE_API`宏的使用方式，确保API导出正确。 |

### 维护评价

`AnimToTexture` 插件处于 **活跃维护** 状态。
-   **创建时间**：约3年前，是UE5中相对较新的功能。
-   **更新频率**：近半年（2025年8月至2026年4月）有多次实质性提交，主要集中在 **bug修复**（刚体烘焙、配置文件、API宏）和 **功能增强**（添加MeshDescription函数）。
-   **维护状态**：作者（Epic Games）仍在持续改进和修复问题，最近一次更新是代码规范优化（日志宏迁移）。
-   **已知限制**：插件被标记为 **实验性**（`IsExperimentalVersion=true`），意味着API和功能可能在未来版本中发生不兼容的变化。目前描述为“实验性”，可能尚未经过大规模生产环境验证。
-   **推荐使用**：**谨慎推荐**。如果你有明确的“海量实例化动画物体”性能需求，并且能够接受实验性插件可能带来的未来维护成本和兼容性风险，那么这是一个强大且高效的解决方案。建议密切关注其后续版本更新。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AnimToTexture)
-   官方文档：（无）
-   测试用例：（无独立测试用例，功能验证依赖编辑器工具和蓝图示例）