# MetaHuman Crowd

> Support for crowds of MetaHumans（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据资产） |
| 模块 | `MetaHumanCrowd` (Runtime), `MetaHumanCrowdEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCrowd) | |

## 用途

MetaHuman Crowd 插件旨在解决将高保真度的 MetaHuman 角色用于大规模人群场景时面临的性能和管理挑战。单个 MetaHuman 角色包含复杂的面部骨骼、毛发和服装系统，直接复制数百或数千个实例会导致严重的性能瓶颈。

该插件提供了一套完整的编辑器管线（Editor Pipeline），用于：
1.  **构建优化资产**：将多个 MetaHuman 角色的头部、身体、服装和毛发资产合并、优化（如启用 Nanite、移除未使用骨骼、优化实例化），并生成适合人群渲染的低分辨率 LOD 网格。
2.  **统一骨骼绑定**：将所有角色部件重新绑定到一个共享的骨架上，这是使用实例化骨骼网格体组件（ISMK）高效渲染人群的前提。
3.  **动画烘焙与合并**：将面部动画（通过 RigLogic 后处理动画蓝图）和身体动画烘焙并合并到统一的骨架上，生成可用于人群的动画序列。
4.  **服装适配与身体几何合并**：将服装适配到不同体型，并将可见的身体部分（如手臂）合并到服装网格中，减少绘制调用。

其核心目标是让开发者能够以可接受的性能开销，在场景中部署大量外观各异的 MetaHuman 角色。

## 使用场景

-   **开放世界游戏**：你需要在城市街道、广场或体育场中填充大量背景 NPC，这些 NPC 需要有不同的外观（服装、发型），但不需要像主角那样高的面部细节。
-   **影视与虚拟制片**：你需要在虚拟场景中快速生成大量背景群众演员，用于预览或最终渲染。
-   **任何需要大规模人群模拟的场景**：例如策略游戏中的士兵、模拟城市中的市民等，同时要求角色具有较高的视觉质量。

## 蓝图用法

该插件的核心功能通过编辑器管线资产进行配置，大部分操作在编辑器内完成。蓝图中主要涉及对管线资产属性的配置。

### 核心配置属性

| 属性 | 说明 | 所在类 |
|---|---|---|
| `ActorFaceLODs` | 为 Actor 网格（近距离）指定面部 LOD 索引。 | `UMetaHumanCrowdEditorPipeline` |
| `ActorBodyLODs` | 为 Actor 网格指定身体/服装 LOD 索引。 | `UMetaHumanCrowdEditorPipeline` |
| `InstancedFaceLODs` | 为实例化网格（远距离人群）指定面部 LOD 索引。 | `UMetaHumanCrowdEditorPipeline` |
| `InstancedBodyLODs` | 为实例化网格指定身体/服装 LOD 索引。 | `UMetaHumanCrowdEditorPipeline` |
| `TargetSkeleton` | 指定所有网格将绑定到的共享骨架。 | `UMetaHumanCrowdEditorPipeline` |
| `AnimationConfig` | 指定动画配置数据资产，定义要烘焙和合并的动画。 | `UMetaHumanCrowdEditorPipeline` |
| `OutfitResizeDataflowAsset` | 指定用于将服装调整到不同体型的 Dataflow 资产。 | `UMetaHumanCrowdEditorPipeline` |
| `bApplyHiddenFaceMaps` | 是否根据服装的隐藏面部贴图移除被遮挡的身体几何。 | `UMetaHumanCrowdEditorPipeline` |
| `FaceMesh` | （可选）提供预构建的面部网格，跳过运行时生成。 | `UMetaHumanCrowdCharacterEditorPipeline` |
| `BodyMesh` | （可选）提供预构建的身体网格。 | `UMetaHumanCrowdCharacterEditorPipeline` |
| `CompatibleBody` | 指定与此角色身体兼容的另一个角色，允许头部互换。 | `UMetaHumanCrowdCharacterEditorPipeline` |

### 使用示例（蓝图描述）

1.  **创建管线资产**：在内容浏览器中右键，选择 `Miscellaneous` -> `Data Asset`，然后选择 `MetaHumanCrowdEditorPipeline` 类。
2.  **配置管线**：打开创建的资产，在细节面板中设置 `TargetSkeleton`（指向你项目中的共享骨架），配置 `ActorFaceLODs`、`InstancedBodyLODs` 等 LOD 索引。
3.  **创建动画配置**：创建一个 `MetaHumanCrowdAnimationConfig` 数据资产，在其中定义 `AnimationsToBake` 数组，为每个条目指定面部和/或身体动画序列。
4.  **关联动画配置**：回到 `MetaHumanCrowdEditorPipeline` 资产，将上一步创建的动画配置资产赋值给 `AnimationConfig` 属性。
5.  **构建集合**：在 MetaHuman 集合编辑器中，选择使用此管线进行构建。管线将自动处理资产的优化、合并和动画烘焙。

## C++ 用法

该插件主要通过编辑器管线类进行扩展和配置。以下示例展示了如何在 C++ 中创建和配置管线。

### 头文件引入

```cpp
#include "Item/MetaHumanCrowdEditorPipeline.h"
#include "MetaHumanCrowdAnimationConfig.h"
```

### 基本用法

创建并配置一个 `UMetaHumanCrowdEditorPipeline` 实例。
```cpp
// 创建管线实例
UMetaHumanCrowdEditorPipeline* CrowdPipeline = NewObject<UMetaHumanCrowdEditorPipeline>();

// 配置LOD设置
CrowdPipeline->ActorFaceLODs = {2, 3};
CrowdPipeline->InstancedBodyLODs = {2, 3};

// 设置目标骨架 (假设已有一个有效的 USkeleton* SharedSkeleton)
CrowdPipeline->TargetSkeleton = SharedSkeleton;

// 启用隐藏面部贴图应用
CrowdPipeline->bApplyHiddenFaceMaps = true;
```

### 进阶用法

创建动画配置并将其与管线关联。
```cpp
// 创建动画配置资产
UMetaHumanCrowdAnimationConfig* AnimConfig = NewObject<UMetaHumanCrowdAnimationConfig>();

// 设置面部根骨骼名称（通常为“head”）
AnimConfig->FaceRootBoneName = FName("head");

// 添加要烘焙的动画条目
FMetaHumanCrowdBakeAnimationData AnimData;
AnimData.Name = FName("Idle");
AnimData.FaceAnimSequence = FaceIdleAnimSequence; // UAnimSequence*
AnimData.BodyAnimSequence = BodyIdleAnimSequence; // UAnimSequence*
AnimConfig->AnimationsToBake.Add(AnimData);

// 将动画配置关联到管线
CrowdPipeline->AnimationConfig = AnimConfig;
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何创建并配置一个 MetaHuman Crowd 管线。

**MyCrowdManager.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyCrowdManager.generated.h"

class UMetaHumanCrowdEditorPipeline;
class UMetaHumanCrowdAnimationConfig;
class USkeleton;

UCLASS(BlueprintType)
class MYPROJECT_API UMyCrowdManager : public UObject
{
	GENERATED_BODY()

public:
	/** 初始化并配置人群管线 */
	UFUNCTION(BlueprintCallable, Category = "MetaHuman Crowd")
	void InitializeCrowdPipeline(USkeleton* InSharedSkeleton);

	/** 获取配置好的管线实例，用于构建集合 */
	UFUNCTION(BlueprintCallable, Category = "MetaHuman Crowd")
	UMetaHumanCrowdEditorPipeline* GetCrowdPipeline() const;

private:
	UPROPERTY()
	TObjectPtr<UMetaHumanCrowdEditorPipeline> CrowdPipeline;

	UPROPERTY()
	TObjectPtr<UMetaHumanCrowdAnimationConfig> AnimationConfig;
};
```

**MyCrowdManager.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MyCrowdManager.h"
#include "Item/MetaHumanCrowdEditorPipeline.h"
#include "MetaHumanCrowdAnimationConfig.h"

void UMyCrowdManager::InitializeCrowdPipeline(USkeleton* InSharedSkeleton)
{
	if (!InSharedSkeleton)
	{
		UE_LOG(LogTemp, Error, TEXT("SharedSkeleton is null."));
		return;
	}

	// 创建管线实例
	CrowdPipeline = NewObject<UMetaHumanCrowdEditorPipeline>(this);

	// 基础配置
	CrowdPipeline->TargetSkeleton = InSharedSkeleton;
	CrowdPipeline->ActorFaceLODs = {2, 3};
	CrowdPipeline->ActorBodyLODs = {1};
	CrowdPipeline->InstancedFaceLODs = {4, 6};
	CrowdPipeline->InstancedBodyLODs = {2, 3};
	CrowdPipeline->bApplyHiddenFaceMaps = true;

	// 创建并配置动画
	AnimationConfig = NewObject<UMetaHumanCrowdAnimationConfig>(this);
	AnimationConfig->FaceRootBoneName = FName("head");

	// 假设我们有预加载的动画资产
	// FMetaHumanCrowdBakeAnimationData WalkAnimData;
	// WalkAnimData.Name = FName("Walk");
	// WalkAnimData.FaceAnimSequence = LoadObject<UAnimSequence>(nullptr, TEXT("/Game/Anims/Face_Walk"));
	// WalkAnimData.BodyAnimSequence = LoadObject<UAnimSequence>(nullptr, TEXT("/Game/Anims/Body_Walk"));
	// AnimationConfig->AnimationsToBake.Add(WalkAnimData);

	CrowdPipeline->AnimationConfig = AnimationConfig;

	UE_LOG(LogTemp, Log, TEXT("MetaHuman Crowd Pipeline initialized."));
}

UMetaHumanCrowdEditorPipeline* UMyCrowdManager::GetCrowdPipeline() const
{
	return CrowdPipeline;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCharacter` | 核心 MetaHuman 角色资产和编辑器管线基础类。 |
| `MetaHumanPalette` | 角色调色板系统，用于管理角色变体（头部、身体、服装、毛发）。 |
| `MetaHumanGeometryRemoval` | 处理隐藏面部贴图（Hidden Face Maps）和几何移除。 |
| `Dataflow` | 用于服装尺寸调整的 Dataflow 图执行框架。 |
| `ChaosOutfitAsset` | 服装资产系统，包含身体测量数据。 |
| `RigLogic` | MetaHuman 面部动画驱动系统。 |

## 维护状态

### 近期更新

- 2026-04-24 `56296dcc` The MetaHuman Crowd pipeline now does most of its processing on Mesh Descriptions and builds skeleta
- 2026-04-24 `8d3ed3d0` [MHCrowd] Add missing plugin dependencies
- 2026-04-24 `16907471` [MHCrowd] Add in experimental UAF support example for MH Crowds
- 2026-04-23 `a0e976cb` [MHCrowd] Fix for animation merging
- 2026-04-21 `227124bc` [MHCrowd] Add MetaHuman Mass classes to the MHCrowd plugin

### 维护评价

-   **创建时间**：2026-04-21（非常新的插件）。
-   **状态**：标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，表明这是一个处于实验阶段、需要手动启用的功能。
-   **活跃度**：作为 MetaHuman 工具链的关键组成部分，预计会随着 MetaHuman SDK 的更新而持续维护。
-   **推荐**：**谨慎推荐**。该插件功能强大，是解决 MetaHuman 人群性能问题的官方方案。但由于其“实验性”标签，在生产环境中使用前应进行充分测试，并关注 Epic Games 的官方更新和文档。它适合那些需要在项目中集成大规模 MetaHuman 人群，并愿意跟进实验性功能的开发者。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCrowd)
-   [官方文档]() （暂无，可关注 MetaHuman 官方文档更新）
-   [测试用例]() （暂未在提供信息中发现）