# GeneSplicer Plugin v9.8.2

> GeneSplicer plugin for facial animation（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GeneSplicerLib` (Runtime), `GeneSplicerLibTest` (Runtime), `GeneSplicerModule` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GeneSplicer) | |

## 用途

GeneSplicer 是一个用于程序化生成和混合角色面部动画（DNA数据）的插件。它解决的核心问题是：如何基于一组已有的角色面部DNA数据（来自不同个体），通过加权混合（拼接）的方式，生成一个全新的、具有混合特征的面部DNA数据。这使得开发者能够高效地创建大量面部变体，而无需为每个变体手动制作动画数据。该插件依赖于 `RigLogic` 和 `ControlRig` 插件，表明其设计用于高级的角色动画系统。

## 使用场景

- 你需要为游戏中的NPC或玩家角色创建大量不同的面部外观和动画变体。
- 你正在开发一个角色创建系统，允许玩家通过滑块混合不同面部特征（如眼睛形状、鼻子高度）来定制角色。
- 你需要在动画制作流程中，基于多个参考角色的DNA数据，程序化生成一个中间状态或混合状态的角色面部动画。
- 你希望将来自不同DNA数据源（例如，不同年龄、性别的角色）的面部动画特征进行融合。

## 蓝图用法

GeneSplicer 提供了丰富的蓝图接口，主要通过 `UGeneSplicerBP`、`USpliceData`、`UPoolSpliceParams`、`UGenePoolAsset` 和 `URegionAffiliationAsset` 等类暴露功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Gene Pool` | 从DNA文件夹和原型路径创建基因池资产。 | `UGeneSplicerBP` |
| `Create Archetype` | 从DNA文件夹和区域归属资产创建原型资产。 | `UGeneSplicerBP` |
| `Splice` | 执行拼接操作，根据拼接数据生成最终的DNA。 | `UGeneSplicerBP` |
| `Register Gene Pool` | 将一个基因池资产注册到拼接数据中，并关联区域归属。 | `USpliceData` |
| `Set Splice Weights` | 设置指定基因池的拼接权重。 | `USpliceData` |
| `Set Archetype` | 设置拼接数据的基础原型DNA路径。 | `USpliceData` |
| `Set Skeletal Mesh Component` | 设置目标骨骼网格体组件，用于最终应用生成的动画。 | `USpliceData` |
| `Register To Splice Data` | 将池拼接参数注册到指定的拼接数据对象中。 | `UPoolSpliceParams` |
| `Set Splice Weights` | 设置池拼接参数的权重。 | `UPoolSpliceParams` |
| `Get DNA Count` | 获取基因池中包含的DNA数量。 | `UGenePoolAsset` |
| `Get Region Count` | 获取区域归属资产中的区域数量。 | `URegionAffiliationAsset` |

### 使用示例（蓝图描述）

1.  **创建基因池**：使用 `Create Gene Pool` 节点，输入DNA文件夹路径、原型DNA路径和输出路径，生成一个 `UGenePoolAsset`。
2.  **准备拼接数据**：
    - 创建一个 `USpliceData` 对象。
    - 使用 `Set Archetype` 设置一个基础原型DNA。
    - 使用 `Set Skeletal Mesh Component` 指定要应用动画的骨骼网格体。
    - 对于每个要混合的基因池，调用 `Register Gene Pool` 将其注册到 `SpliceData` 中，并传入对应的 `UGenePoolAsset` 和 `URegionAffiliationAsset`。
3.  **设置权重**：使用 `Set Splice Weights` 节点，为每个注册的基因池设置其DNA的混合权重数组。
4.  **执行拼接**：最后，调用 `Splice` 节点，传入配置好的 `USpliceData` 对象，即可生成混合后的面部动画数据并应用到目标骨骼网格体上。

## C++ 用法

### 头文件引入

```cpp
#include "GeneSplicer.h"
#include "SpliceData.h"
#include "GenePool.h"
#include "GeneSplicerDNAReader.h"
#include "RegionAffiliationReader.h"
```

### 基本用法

以下示例展示了如何创建一个基因池并执行一次完整的拼接操作。

```cpp
// 假设已有DNA文件路径和原型DNA路径
FString DNADirectory = TEXT("/Game/DNAs/Characters");
FString ArchetypeDNAPath = TEXT("/Game/DNAs/Archetype.dna");
FString GenePoolOutputPath = TEXT("/Game/GenePools/MyGenePool.gp");

// 1. 创建基因池 (通常在编辑器工具或初始化时完成)
// 使用 GeneSplicerLib 模块中的函数，此处为概念示例
// FGenePool::CreateFromDirectory(DNADirectory, ArchetypeDNAPath, GenePoolOutputPath);

// 2. 加载或创建基因池和区域归属数据
TSharedPtr<FGenePool> GenePool = MakeShared<FGenePool>(GenePoolOutputPath);
FRegionAffiliationReader RegionAffiliationReader(TEXT("/Game/RAFs/MyRAF.raf"));

// 3. 准备拼接数据
FSpliceData SpliceData;
// 注册基因池，并关联区域归属
SpliceData.RegisterGenePool(TEXT("MainPool"), RegionAffiliationReader, GenePool);
// 设置基础原型
TSharedPtr<IDNAReader> BaseArchetype = /* 从文件或内存加载原型DNA */;
SpliceData.SetBaseArchetype(BaseArchetype);

// 4. 设置拼接权重
TSharedPtr<FPoolSpliceParams> PoolParams = SpliceData.GetPoolParams(TEXT("MainPool"));
TArray<float> Weights = {0.5f, 0.3f, 0.2f}; // 假设基因池中有3个DNA
PoolParams->SetSpliceWeights(0, Weights);

// 5. 创建输出DNA读取器和拼接器
FGeneSplicerDNAReader OutputDNA(BaseArchetype.Get());
FGeneSplicer GeneSplicer(FGeneSplicer::ECalculationType::SSE);

// 6. 执行拼接
GeneSplicer.Splice(SpliceData, OutputDNA);

// 此时 OutputDNA 包含了混合后的面部动画数据，可以用于驱动骨骼网格体。
```

### 进阶用法

GeneSplicer 允许进行部分拼接，例如只混合网格体或只混合关节行为。

```cpp
// ... 接上文，假设 SpliceData 和 OutputDNA 已准备好 ...

FGeneSplicer GeneSplicer(FGeneSplicer::ECalculationType::Scalar);

// 仅拼接中性网格体（顶点位置）
GeneSplicer.SpliceNeutralMeshes(SpliceData, OutputDNA);

// 仅拼接混合变形（BlendShapes）
GeneSplicer.SpliceBlendShapes(SpliceData, OutputDNA);

// 仅拼接中性关节（Neutral Joints）
GeneSplicer.SpliceNeutralJoints(SpliceData, OutputDNA);

// 仅拼接关节行为（Joint Behavior）
GeneSplicer.SpliceJointBehavior(SpliceData, OutputDNA);

// 仅拼接蒙皮权重（Skin Weights）
GeneSplicer.SpliceSkinWeights(SpliceData, OutputDNA);
```

## Demo 示例

以下是一个最小化的C++示例，演示了如何使用GeneSplicer的核心流程。

**GeneSplicerDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GeneSplicerDemo.generated.h"

class FGeneSplicer;
class FSpliceData;
class FGeneSplicerDNAReader;

UCLASS()
class AGeneSplicerDemo : public AActor
{
	GENERATED_BODY()
	
public:	
	AGeneSplicerDemo();

protected:
	virtual void BeginPlay() override;

public:	
	virtual void Tick(float DeltaTime) override;

private:
	void PerformSplicing();

	UPROPERTY(EditAnywhere, Category = "GeneSplicer")
	FString DNADirectory;

	UPROPERTY(EditAnywhere, Category = "GeneSplicer")
	FString ArchetypeDNAPath;

	UPROPERTY(EditAnywhere, Category = "GeneSplicer")
	FString GenePoolPath;

	UPROPERTY(EditAnywhere, Category = "GeneSplicer")
	FString RegionAffiliationPath;

	UPROPERTY(EditAnywhere, Category = "GeneSplicer")
	USkeletalMeshComponent* TargetMesh;

	TUniquePtr<FGeneSplicer> GeneSplicer;
	TSharedPtr<FSpliceData> SpliceData;
	TSharedPtr<FGeneSplicerDNAReader> OutputDNA;
};
```

**GeneSplicerDemo.cpp**
```cpp
#include "GeneSplicerDemo.h"
#include "GeneSplicer.h"
#include "SpliceData.h"
#include "GenePool.h"
#include "GeneSplicerDNAReader.h"
#include "RegionAffiliationReader.h"

AGeneSplicerDemo::AGeneSplicerDemo()
{
	PrimaryActorTick.bCanEverTick = false;
	TargetMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("TargetMesh"));
	RootComponent = TargetMesh;
}

void AGeneSplicerDemo::BeginPlay()
{
	Super::BeginPlay();
	PerformSplicing();
}

void AGeneSplicerDemo::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
}

void AGeneSplicerDemo::PerformSplicing()
{
	// 1. 初始化基因池和区域归属
	TSharedPtr<FGenePool> GenePool = MakeShared<FGenePool>(GenePoolPath);
	FRegionAffiliationReader RAFReader(RegionAffiliationPath);

	// 2. 初始化拼接数据
	SpliceData = MakeShared<FSpliceData>();
	SpliceData->RegisterGenePool(TEXT("PrimaryPool"), RAFReader, GenePool);

	// 3. 设置基础原型 (假设从ArchetypeDNAPath加载)
	// TSharedPtr<IDNAReader> BaseArchetype = LoadDNAFromFile(ArchetypeDNAPath);
	// SpliceData->SetBaseArchetype(BaseArchetype);

	// 4. 设置权重 (示例：均匀混合前两个DNA)
	TSharedPtr<FPoolSpliceParams> Params = SpliceData->GetPoolParams(TEXT("PrimaryPool"));
	if (Params.IsValid() && Params->GetDNACount() >= 2)
	{
		TArray<float> Weights = {0.5f, 0.5f};
		Params->SetSpliceWeights(0, Weights);
	}

	// 5. 创建输出DNA和拼接器
	// OutputDNA = MakeShared<FGeneSplicerDNAReader>(BaseArchetype.Get());
	GeneSplicer = MakeUnique<FGeneSplicer>(FGeneSplicer::ECalculationType::SSE);

	// 6. 执行拼接
	if (SpliceData.IsValid() && OutputDNA.IsValid())
	{
		GeneSplicer->Splice(*SpliceData, *OutputDNA);
		// 此时 OutputDNA 包含混合后的数据，可以用于更新 TargetMesh 的动画。
		UE_LOG(LogTemp, Log, TEXT("Splicing completed successfully."));
	}
}
```

## 模块依赖

要使用 GeneSplicer 插件，你的项目或模块需要依赖以下插件：

| 模块 | 用途 |
|---|---|
| `RigLogic` | 提供底层的DNA数据读写和行为逻辑，是GeneSplicer的核心依赖。 |
| `ControlRig` | 用于将生成的DNA数据应用到骨骼网格体动画系统中。 |

## 维护状态

### 近期更新

- 2025-10-03 f93356208172 Fix unacceptable words in GS engine wrapper #rb none
- 2025-09-15 ea76c1ecb047 Move GeneSplicer into public plugins folder #rb violeta.vukobrat

### 维护评价

- **创建时间**：2024年10月，是一个相对较新的插件。
- **最近更新**：最近两次提交（2025年9月和10月）均为维护性更新，包括代码规范修复和目录结构调整，表明插件仍在被维护。
- **活跃度**：虽然更新频率不高，但近期有活动，且没有废弃标记。
- **已知限制**：插件默认未启用（`Installed: false`），需要用户手动在项目设置中启用。它强依赖于 `RigLogic` 和 `ControlRig` 插件。
- **推荐使用**：**推荐**。对于需要程序化生成和混合角色面部动画的项目，这是一个功能强大且由Epic官方维护的解决方案。尽管文档和示例可能较少，但其API设计清晰，适合集成到专业的动画工作流中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GeneSplicer)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GeneSplicer/Source/GeneSplicerLibTest) (GeneSplicerLibTest 模块)