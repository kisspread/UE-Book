# Skeletal Merging

> Provides Blueprint functionality to perform runtime Skeletal Mesh merging

| 属性 | 值 |
|---|---|
| 中文名 | 骨骼合并 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SkeletalMerging` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-01-06 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SkeletalMerging) | |

## 用途

Skeletal Merging 插件的核心功能是提供**运行时**合并骨骼网格体（Skeletal Mesh）和骨架（Skeleton）的蓝图接口。它解决的主要问题是：在游戏运行时，动态地将多个独立的骨骼网格体组合成一个整体，或者将多个骨架的骨骼结构、插槽、动画曲线等数据合并到一个新的骨架中。

这在需要动态组装角色部件（如装备、武器、载具部件）或合并来自不同来源的动画数据时非常有用，而无需在编辑器中预先烘焙好所有内容。

**注意**：该插件**默认未启用**，需要在项目的插件设置中手动启用。

## 使用场景

- **角色换装系统**：在游戏中，玩家动态装备不同的护甲、武器或服装部件时，将这些部件对应的骨骼网格体合并为一个整体，以提高渲染性能和动画同步性。
- **载具组装**：组装一个由多个可分离部件（如车门、车轮）组成的载具，每个部件都是独立的骨骼网格体，运行时合并为一个。
- **动画数据整合**：当有多个使用不同骨架的动画资产需要在同一个角色上播放时，可以先合并这些骨架的结构（包括动画曲线、插槽等），然后应用动画。

## 蓝图用法

该插件主要通过 `USkeletalMergingLibrary` 蓝图函数库暴露功能，提供两个核心的静态蓝图函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Merge Meshes` | 将多个骨骼网格体合并为一个。 | `USkeletalMergingLibrary` |
| `Merge Skeletons` | 将多个骨架的结构和相关数据（插槽、虚拟骨骼等）合并为一个新骨架。 | `USkeletalMergingLibrary` |

### 使用示例（蓝图描述）

**合并骨骼网格体示例：**
1. 创建一个 `FSkeletalMeshMergeParams` 结构体变量。
2. 设置其中的 `MeshesToMerge` 数组，填入你想要合并的 `USkeletalMesh` 对象引用。
3. 可选：设置 `StripTopLODS` 来丢弃一些高精度LOD以优化性能，或指定 `Skeleton` 来使用一个已有的骨架。
4. 调用 `Merge Meshes` 节点，传入参数结构体，获取返回的合并后 `USkeletalMesh`。
5. 可以将此网格体设置给某个 `USkeletalMeshComponent`。

**合并骨架示例：**
1. 创建一个 `FSkeletonMergeParams` 结构体变量。
2. 在 `SkeletonsToMerge` 数组中填入需要合并的 `USkeleton` 对象引用。
3. 根据需要设置布尔选项，例如是否合并插槽（`bMergeSockets`）、虚拟骨骼（`bMergeVirtualBones`）等。
4. 调用 `Merge Skeletons` 节点，传入参数结构体，获取返回的合并后 `USkeleton`。

## C++ 用法

该插件的 C++ 用法与蓝图类似，直接调用静态函数。

### 头文件引入

```cpp
#include "SkeletalMergingLibrary.h"
```

### 基本用法

从源码中的函数声明和结构体定义提取的典型用法。

```cpp
// 合并骨骼网格体
#include "SkeletalMergingLibrary.h"

// 假设你有一个包含多个 USkeletalMesh* 的数组 MeshesToCombine
FSkeletalMeshMergeParams MergeParams;
MergeParams.MeshesToMerge = MeshesToCombine; // TArray<USkeletalMesh*>
MergeParams.bNeedsCpuAccess = true; // 如果需要CPU访问（例如粒子发射）

USkeletalMesh* MergedMesh = USkeletalMergingLibrary::MergeMeshes(MergeParams);
if (MergedMesh)
{
    // 使用合并后的网格体
    SkeletalMeshComponent->SetSkeletalMesh(MergedMesh);
}
```

### 进阶用法

结合合并骨架和自定义映射的示例。

```cpp
// 合并骨架，并保留特定数据
#include "SkeletalMergingLibrary.h"

FSkeletonMergeParams SkeletonMergeParams;
SkeletonMergeParams.SkeletonsToMerge.Add(SkeletonA);
SkeletonMergeParams.SkeletonsToMerge.Add(SkeletonB);
SkeletonMergeParams.bMergeSockets = true;       // 合并插槽
SkeletonMergeParams.bMergeVirtualBones = false;  // 不合并虚拟骨骼
SkeletonMergeParams.bCheckSkeletonsCompatibility = true; // 检查兼容性

USkeleton* NewSkeleton = USkeletalMergingLibrary::MergeSkeletons(SkeletonMergeParams);

// 可以在之后的网格体合并中指定这个新生成的骨架
FSkeletalMeshMergeParams MeshMergeParams;
MeshMergeParams.MeshesToMerge = ...;
MeshMergeParams.Skeleton = NewSkeleton; // 使用合并后的骨架
MeshMergeParams.bSkeletonBefore = true; // 在合并前使用此骨架

USkeletalMesh* FinalMesh = USkeletalMergingLibrary::MergeMeshes(MeshMergeParams);
```

## Demo 示例

一个最小可运行示例，展示如何在运行时合并两个角色部件的网格体。

**MyCharacter.h**
```cpp
// MyCharacter.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyCharacter.generated.h"

class USkeletalMesh;
struct FSkeletalMeshMergeParams;

UCLASS()
class MYGAME_API AMyCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	AMyCharacter();

	virtual void BeginPlay() override;

	// 需要合并的两个网格体（可在蓝图中设置）
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Merging")
	USkeletalMesh* MeshPartA;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Merging")
	USkeletalMesh* MeshPartB;

	// 合并后的网格体
	UPROPERTY()
	USkeletalMesh* CombinedMesh;
};
```

**MyCharacter.cpp**
```cpp
// MyCharacter.cpp
#include "MyCharacter.h"
#include "SkeletalMergingLibrary.h"
#include "Components/SkeletalMeshComponent.h"

AMyCharacter::AMyCharacter()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AMyCharacter::BeginPlay()
{
	Super::BeginPlay();

	if (MeshPartA && MeshPartB)
	{
		FSkeletalMeshMergeParams Params;
		Params.MeshesToMerge.Add(MeshPartA);
		Params.MeshesToMerge.Add(MeshPartB);
		// 可选参数，例如需要CPU访问
		Params.bNeedsCpuAccess = false;

		// 在运行时合并网格体
		CombinedMesh = USkeletalMergingLibrary::MergeMeshes(Params);

		if (CombinedMesh)
		{
			// 将合并后的网格体设置给角色的主网格体组件
			GetMesh()->SetSkeletalMesh(CombinedMesh);
			UE_LOG(LogTemp, Log, TEXT("Skeletal meshes merged successfully."));
		}
		else
		{
			UE_LOG(LogTemp, Error, TEXT("Failed to merge skeletal meshes."));
		}
	}
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。该插件的模块 `SkeletalMerging` 依赖于引擎核心模块，但根据插件规模，这些依赖都是标准的，无需使用者额外配置。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到 `UE_LOGF`。 |
| 2025-04-23 | `939cc6e5` | Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv | 为Fortnite客户端构建目标调整，确保导出符号使用正确的DLL存储声明。 |
| 2024-06-26 | `a783fefa` | Add functionality to add named virtual bones to a Skeleton. Fix SkeletalMergingLibrary virtual bone | 增加向骨架添加命名虚拟骨骼的功能，并修复了SkeletalMergingLibrary中的虚拟骨骼相关代码。 |
| 2024-05-13 | `dc23af1c` | Allow AddCurveMetaData to skip recording new transactions. | 允许 `AddCurveMetaData` 函数在添加曲线元数据时跳过记录新的撤销事务，优化性能。 |
| 2023-05-15 | `da92084a` | Optimized out more private modules includes and dependencies. | 优化了头文件包含，减少了不必要的私有模块依赖。 |

### 维护评价

- **维护状态**：**维护中**。该插件自2022年创建以来，持续有更新，最近一次实质性功能更新在2024年6月（增加虚拟骨骼功能），并在2025年和2026年进行了内部工具链和日志系统的适配更新。
- **活跃度**：更新频率约为每1-2年一次，属于低频率但持续的维护状态，符合一个特定功能的Runtime插件的维护预期。
- **推荐使用**：**推荐**。该插件功能明确，由Epic Games维护，代码质量有保障。对于需要在运行时合并骨骼网格体或骨架的项目，这是一个官方且可靠的解决方案。由于其默认未启用，使用前需手动激活。

**注意**：该插件的 `EnabledByDefault` 为 `false`，这意味着创建项目时不会自动启用。在使用前，必须前往 `编辑 -> 插件` 菜单，搜索 `Skeletal Merging` 并启用它，然后重启编辑器。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SkeletalMerging)
- 官方文档：无（.uplugin 中 DocsURL 为空）