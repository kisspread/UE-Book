# GeneSplicer Plugin

> GeneSplicer plugin for facial animation

| 属性 | 值 |
|---|---|
| 中文名 | 基因剪接器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GeneSplicerLib` (CPlusPlus), `GeneSplicerLibTest` (Runtime), `GeneSplicerModule` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-21 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GeneSplicer) | |

## 用途

GeneSplicer 插件用于数字人类面部动画的**程序化生成与混合**。其核心功能是将多个 DNA 资产（描述一个数字人类角色面部结构与动画规则的数据集合）按照指定的权重进行“基因剪接”，从而生成一个新的 DNA 资产。这解决了动画资产创作中的多样性问题，允许开发者从少数几个基础角色（原型）快速衍生出大量外观、动画行为相似但各具特色的变体，极大地提升了角色制作的效率与扩展性。

## 使用场景

-   你需要为一个游戏创建大量外表相似但细节（如脸型、眼睛大小、皱纹等）不同的 NPC 角色。
-   你已经制作了几个高质量的数字人类基础模型，希望以此为基础，通过调整参数程序化地生成一系列衍生角色。
-   你希望在运行时动态混合不同角色的特征，以实现角色外观的自定义或进化。
-   你需要一个工具来管理、存储和查询用于生成混合角色的基因池数据。

## 蓝图用法

插件提供了一套完整的蓝图 API，用于管理基因池、设置混合参数并执行剪接。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Gene Pool` | 从指定文件夹读取 DNA 文件并创建基因池资产。 | `UGeneSplicerBP` |
| `Create Archetype` | 基于一组 DNA 文件和区域亲和力数据创建基础原型（Archetype）。 | `UGeneSplicerBP` |
| `Splice` | 根据 `SpliceData` 中的配置执行核心的基因剪接计算。 | `UGeneSplicerBP` |
| `Register Gene Pool` | 将一个 `GenePoolAsset` 注册到剪接数据中，并为其设置名称。 | `USpliceData` |
| `Set Splice Weights` | 为指定名称的基因池设置混合权重。 | `USpliceData` |
| `Set Archetype` | 设置用于剪接的基准原型 DNA 文件路径。 | `USpliceData` |
| `Set Skeletal Mesh Component` | 将剪接输出与一个 `SkeletalMeshComponent` 关联，用于将结果应用到网格体。 | `USpliceData` |
| `Get DNACount` | 获取已注册基因池中包含的 DNA 数量。 | `UPoolSpliceParams` |

### 使用示例（蓝图描述）

1.  **创建基因池资产**：在蓝图中调用 `Create Gene Pool` 节点，传入包含 `.dna` 文件的文件夹路径、原型 DNA 文件路径以及输出路径，生成 `UGenePoolAsset`。
2.  **配置剪接数据**：
    -   创建一个 `USpliceData` 对象。
    -   调用 `Register Gene Pool`，为上一步创建的基因池指定一个名称（如 “MainPool”）。
    -   调用 `Set Splice Weights`，通过 `DNAStartIndex` 和 `Weights` 数组定义每个源 DNA 对最终结果的贡献程度。
    -   调用 `Set Archetype` 指定基础原型。
    -   调用 `Set Skeletal Mesh Component` 关联场景中的骨骼网格体组件。
3.  **执行剪接**：调用核心的 `Splice` 节点，传入配置好的 `USpliceData`。插件将根据权重混合所有 DNA 数据，生成一个新的面部动画配置，并将其应用到关联的 `SkeletalMeshComponent` 上。

## C++ 用法

### 头文件引入

```cpp
#include "GeneSplicer.h"
#include "GenePool.h"
#include "SpliceData.h"
#include "GeneSplicerDNAReader.h"
#include "RegionAffiliationReader.h"
```

### 基本用法

以下示例展示了如何从文件加载基因池并执行一次剪接，获取结果数据。
（代码逻辑基于源码 `Public/GeneSplicer.h` 和 `Public/SpliceData.h` 推断）

```cpp
// 假设已有一个 DNA 资产路径
const FString ArchetypePath = TEXT("Path/To/Archetype.dna");
const FString GenePoolPath = TEXT("Path/To/GenePool.bin");

// 1. 创建基因池 (FGenePool) 从文件
FGenePool GenePool(GenePoolPath, EGenePoolMask::All);

// 2. 准备剪接数据容器 (FSpliceData)
FSpliceData SpliceData;

// 3. 准备区域亲和力数据 (FRegionAffiliationReader)，用于精细控制不同面部区域的混合
FRegionAffiliationReader RegionAffiliation(TEXT("Path/To/Raf.bin"));

// 4. 注册基因池到剪接数据，并指定名称和区域亲和力
SpliceData.RegisterGenePool(TEXT("FacePool"), RegionAffiliation, MakeShareable(&GenePool));

// 5. 设置基准原型
// 注意：需要从 IDNAReader 加载，此处简化为示意
TSharedPtr<IDNAReader> BaseArchetype = LoadDNAArchetype(ArchetypePath);
SpliceData.SetBaseArchetype(BaseArchetype);

// 6. 获取池参数并设置混合权重
TSharedPtr<FPoolSpliceParams> PoolParams = SpliceData.GetPoolParams(TEXT("FacePool"));
if (PoolParams.IsValid())
{
    TArray<float> Weights = {0.3f, 0.7f}; // 示例：两个DNA的权重
    PoolParams->SetSpliceWeights(0, Weights); // 从第0个DNA开始设置权重
}

// 7. 创建基因剪接器并执行剪接
FGeneSplicer Splicer(FGeneSplicer::ECalculationType::SSE); // 使用SSE向量化实现
FGeneSplicerDNAReader OutputDNA(BaseArchetype.Get()); // 用原型初始化输出容器
Splicer.Splice(SpliceData, OutputDNA); // 执行完整剪接

// 8. 现在 OutputDNA 中包含了混合后的所有数据（顶点、关节、混合形状等）
// 可以用于进一步处理或应用到骨骼网格体。
```

### 进阶用法

可以单独控制不同部分的剪接，例如仅混合中性网格体或仅混合关节行为。

```cpp
// ... 继承上面的设置步骤 ...

FGeneSplicer Splicer(FGeneSplicer::ECalculationType::SSE);
FGeneSplicerDNAReader OutputDNA(BaseArchetype.Get());

// 仅混合中性网格体（用于改变基础脸型）
Splicer.SpliceNeutralMeshes(SpliceData, OutputDNA);

// 或仅混合关节行为（用于改变表情动画）
Splicer.SpliceJointBehavior(SpliceData, OutputDNA);
```

## Demo 示例

一个完整的最小示例，展示如何设置并执行一次剪接操作。
**文件：GeneSplicerDemo.h**
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

private:
	void RunGeneSpliceDemo();

	// 资源路径
	UPROPERTY(EditAnywhere, Category = "GeneSplicer Demo")
	FString GenePoolFilePath = TEXT("/Game/Demo/GenePool.bin");

	UPROPERTY(EditAnywhere, Category = "GeneSplicer Demo")
	FString ArchetypeFilePath = TEXT("/Game/Demo/Archetype.dna");

	UPROPERTY(EditAnywhere, Category = "GeneSplicer Demo")
	FString RegionAffiliationFilePath = TEXT("/Game/Demo/Raf.bin");
};
```

**文件：GeneSplicerDemo.cpp**
```cpp
#include "GeneSplicerDemo.h"
#include "GeneSplicer.h"
#include "GenePool.h"
#include "SpliceData.h"
#include "GeneSplicerDNAReader.h"
#include "RegionAffiliationReader.h"

AGeneSplicerDemo::AGeneSplicerDemo()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AGeneSplicerDemo::BeginPlay()
{
	Super::BeginPlay();
	RunGeneSpliceDemo();
}

void AGeneSplicerDemo::RunGeneSpliceDemo()
{
	// 1. 从文件加载基因池
	FGenePool GenePool(GenePoolFilePath, EGenePoolMask::All);
	if (GenePool.GetDNACount() == 0)
	{
		UE_LOG(LogTemp, Error, TEXT("GeneSplicerDemo: Failed to load Gene Pool."));
		return;
	}

	// 2. 加载区域亲和力数据
	FRegionAffiliationReader RegionAffiliation(RegionAffiliationFilePath);

	// 3. 初始化剪接数据
	FSpliceData SpliceData;
	SpliceData.RegisterGenePool(TEXT("DemoPool"), RegionAffiliation, MakeShareable(&GenePool));

	// 4. (可选) 加载并设置基准原型。如果没有，可以使用基因池中的第一个DNA作为基准。
	// 此处假设不设置，使用基因池默认行为。
	// TSharedPtr<IDNAReader> BaseArchetype = ...;
	// SpliceData.SetBaseArchetype(BaseArchetype);

	// 5. 设置混合权重 (例如，50%来自第一个DNA，50%来自第二个)
	TSharedPtr<FPoolSpliceParams> PoolParams = SpliceData.GetPoolParams(TEXT("DemoPool"));
	if (PoolParams.IsValid() && PoolParams->GetDNACount() >= 2)
	{
		TArray<float> Weights;
		Weights.SetNum(PoolParams->GetDNACount());
		Weights[0] = 0.5f;
		Weights[1] = 0.5f;
		PoolParams->SetSpliceWeights(0, Weights);
	}

	// 6. 执行剪接
	FGeneSplicer Splicer(FGeneSplicer::ECalculationType::SSE);
	FGeneSplicerDNAReader OutputDNA(nullptr); // 输出将被填充
	Splicer.Splice(SpliceData, OutputDNA);

	UE_LOG(LogTemp, Log, TEXT("GeneSplicerDemo: Splice completed. Output mesh count: %d"), OutputDNA.GetMeshCount());
	// 在此之后，OutputDNA 包含了混合后的完整DNA数据，可以用于动画蓝图、渲染或保存。
}
```

## 模块依赖

从 Build.cs 分析，`GeneSplicerModule` 模块具有以下依赖。

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 用于实现编辑器特定的功能，如资产的自定义序列化、版本控制和工厂类。 |
| `MessageLog` | 用于在编辑器中向用户报告操作状态、警告和错误信息。 |

**注意**：使用该插件进行运行时剪接（如上述C++示例）通常只需链接 `GeneSplicerModule`。如果需要编辑器功能（如自定义资产编辑器），则需要额外链接 `GeneSplicerEditor`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `2f6aa301` | Improve DNA asset load performance and backwards compatible conversion by reducing data copies | 优化DNA资产加载性能与向后兼容性转换，减少数据拷贝 |
| 2026-05-12 | `57c5e2c7` | Update DNA and RigLogic to better handle malformed DNA files | 更新DNA与RigLogic以更好地处理格式错误的DNA文件 |
| 2026-05-12 | `0577289d` | Suppress private module include warnings for test modules (RigLogicLibTest, DNACalibLibTest, DNACali | 抑制测试模块的私有模块包含警告 |
| 2026-04-30 | `82833e51` | Fix data-race on per platform DNAConfig access during serialization | 修复序列化期间平台特定DNAConfig访问的数据竞争问题 |
| 2026-04-28 | `0c7a803e` | Implement face-winding conversion in DNA to support arbitrary coordinate systems in UE | 在DNA中实现面缠绕顺序转换，以支持UE中的任意坐标系 |

### 维护评价

该插件创建于2024年10月，**年龄约2年**，属于相对较新的插件。从近期提交记录来看，它在**2026年5月仍有密集的功能性更新和错误修复**，表明该插件正处于**活跃维护**期。更新内容集中在性能优化、兼容性增强、错误处理和底层依赖库（RigLogic）的同步更新，说明开发团队在持续改进其核心功能与稳定性。插件未标记为实验性（`IsBetaVersion=false`），但默认未启用（`Installed=false`），需要用户手动开启。

**推荐使用**。对于需要程序化生成或混合数字人类面部动画的项目，这是一个由Epic官方维护、功能明确且仍在持续更新的工具。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GeneSplicer)
-   [官方文档]() （暂无）
-   [测试用例]() （位于 `GeneSplicerLibTest` 模块，用于验证核心剪接算法）