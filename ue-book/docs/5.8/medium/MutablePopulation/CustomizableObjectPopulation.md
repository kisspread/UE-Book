# MutablePopulation

> Extend the Mutable plugin to support Population assets.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 可变人口 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（人口资产、人口类资产） |
| 模块 | `CustomizableObjectPopulation` (Runtime), `CustomizableObjectPopulationEditor` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2024-09-13 |
| 年龄标签 | 🏛️ 文物（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MutablePopulation) | |

## 用途

该插件是对 [Mutable](https://docs.unrealengine.com/5.8/en-US/mutable-in-unreal-engine/) 插件的功能扩展。Mutable 本身专注于管理和生成单个可定制对象（Customizable Object， CO）的实例变体。而 **MutablePopulation** 引入了“人口”（Population）的概念，允许开发者定义一个由多个“人口类”（Population Class）组成的规则集。每个“人口类”关联一个基础的可定制对象，并定义了生成该类实例时各个参数（如布尔值、选项、浮点数范围、颜色等）的随机化采样规则。

**核心解决的问题**：当游戏需要生成大量外观不同但符合特定规则的角色、道具或环境元素（例如，一个城镇里的所有市民，每个市民的体型、肤色、发型、服装都不同）时，手动创建每个实例是不现实的。MutablePopulation 允许开发者通过配置“人口”和“人口类”资产，由系统基于这些规则批量生成大量具有随机化但合理变异的可定制对象实例。

## 使用场景

- **开放世界NPC生成**：为一个大型开放世界游戏快速生成成百上千个外貌各异的NPC。你可以定义几个“人口类”（如“男性市民”、“女性市民”、“守卫”），并为每个类设置不同的外观参数随机范围（身高、体型、发色等）。
- **多样化道具实例化**：在场景中放置大量外观略有不同的同类道具，例如不同磨损程度的箱子、颜色略有差异的垃圾桶，以增加环境真实感。
- **程序化内容生成**：结合规则，自动创建符合美术风格和设计约束的大量角色或物体，用于原型设计或最终内容。

## 蓝图用法

该插件的核心蓝图功能围绕 `UCustomizableObjectPopulation` 资产展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GeneratePopulation` | 根据人口资产定义，使用随机种子批量生成一组可定制对象实例。 | `UCustomizableObjectPopulation` |
| `RegeneratePopulation` | 使用一个已知的种子，重新生成完全相同的一组实例（用于重现性测试或网络同步）。 | `UCustomizableObjectPopulation` |

### 使用示例（蓝图描述）

1.  **创建人口资产**：在内容浏览器中，右键 -> Miscellaneous -> Data Asset，选择 `CustomizableObjectPopulation` 类型。
2.  **配置人口类**：在该人口资产的细节面板中，为 `ClassWeights` 数组添加元素。每个元素关联一个 `CustomizableObjectPopulationClass` 资产，并设置其生成权重（`ClassWeight`）。
3.  **配置人口类**：为每个 `CustomizableObjectPopulationClass` 资产关联一个基础 `CustomizableObject`，并为其 `Characteristics` 数组定义各种参数约束（如“肤色”的曲线采样、“发型”的选项采样等）。
4.  **蓝图生成**：在角色生成逻辑的蓝图图表中，获取你创建的人口资产引用。使用“Make Literal Customizable Object Population”节点或直接引用资产变量。连接到 `GeneratePopulation` 节点，指定要生成的实例数量（`NumInstancesToGenerate`）和一个随机种子（或使用默认随机种子）。将 `OutInstances` 输出连接到一个数组变量，后续可以遍历这些实例并将其附加到对应的Actor组件上进行渲染和模拟。

## C++ 用法

### 头文件引入

```cpp
#include "MuCOP/CustomizableObjectPopulation.h"
```

### 基本用法

从 `UCustomizableObjectPopulation::GeneratePopulation` 的签名可以推断用法。
（来源文件：`Public/MuCOP/CustomizableObjectPopulation.h`）

```cpp
#include "MuCOP/CustomizableObjectPopulation.h"
#include "CustomizableObjectInstance.h"

// 假设 PopulationAsset 是已加载的 UCustomizableObjectPopulation* 对象
void GenerateCharacters()
{
    if (!PopulationAsset || !PopulationAsset->IsValidPopulation())
    {
        UE_LOG(LogTemp, Warning, TEXT("Invalid Population Asset"));
        return;
    }

    TArray<UCustomizableObjectInstance*> GeneratedInstances;
    int32 SeedUsed = PopulationAsset->GeneratePopulation(GeneratedInstances, 50);

    if (SeedUsed >= 0)
    {
        UE_LOG(LogTemp, Log, TEXT("Generated 50 instances with seed: %d"), SeedUsed);
        // 处理生成的实例，例如附加到场景中的Actor上
        for (UCustomizableObjectInstance* Instance : GeneratedInstances)
        {
            // 使用实例...
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to generate population"));
    }
}

// 使用种子重新生成相同的集合
void RegenerateCharacters(int32 PreviousSeed)
{
    TArray<UCustomizableObjectInstance*> SameInstances;
    bool bSuccess = PopulationAsset->RegeneratePopulation(PreviousSeed, SameInstances, 50);
    // bSuccess 为 true 时，SameInstances 包含与之前种子相同配置的实例
}
```

### 进阶用法

理解采样器（Sampler）系统有助于编写更精细的控制逻辑。`FCustomizableObjectPopulationGeneratorPrivate` 内部包含了各种采样器（布尔、选项、浮点、曲线等）来控制参数的随机化。虽然这些主要通过资产编辑器配置，但了解其存在有助于调试和扩展。
（参考文件：`Public/MuCOP/CustomizableObjectPopulationSamplers.h`, `Public/MuCOP/CustomizableObjectPopulationGeneratorPrivate.h`）

## Demo 示例

以下是一个最小可编译示例，演示如何在C++中创建并使用人口对象来生成实例。

**MyCharacterGenerator.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCharacterGenerator.generated.h"

class UCustomizableObjectPopulation;
class UCustomizableObjectInstance;

UCLASS()
class AMyCharacterGenerator : public AActor
{
    GENERATED_BODY()

public:
    AMyCharacterGenerator();

    // 在编辑器或运行时中设置这个资产
    UPROPERTY(EditAnywhere, Category = "Population")
    TObjectPtr<UCustomizableObjectPopulation> PopulationAsset;

    // 生成的实例数量
    UPROPERTY(EditAnywhere, Category = "Population")
    int32 NumToGenerate = 10;

    // 使用的随机种子，-1 表示随机
    UPROPERTY(EditAnywhere, Category = "Population")
    int32 Seed = -1;

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "Population")
    void GeneratePopulation();

private:
    UPROPERTY()
    TArray<TObjectPtr<UCustomizableObjectInstance>> GeneratedInstances;
};
```

**MyCharacterGenerator.cpp**
```cpp
#include "MyCharacterGenerator.h"
#include "MuCOP/CustomizableObjectPopulation.h"
#include "CustomizableObjectInstance.h"

AMyCharacterGenerator::AMyCharacterGenerator()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyCharacterGenerator::GeneratePopulation()
{
    if (!PopulationAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT("PopulationAsset is not set."));
        return;
    }

    // 清理旧实例（如果有）
    GeneratedInstances.Empty();

    int32 FinalSeed = Seed;
    if (FinalSeed == -1)
    {
        FinalSeed = FMath::RandRange(0, TNumericLimits<int32>::Max());
    }

    // 调用插件核心函数生成实例
    FinalSeed = PopulationAsset->GeneratePopulation(GeneratedInstances, NumToGenerate);

    if (FinalSeed >= 0)
    {
        UE_LOG(LogTemp, Log, TEXT("Generated %d instances with seed %d."), GeneratedInstances.Num(), FinalSeed);
        // 此处可将实例附加到场景组件，或进行下一步处理
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to generate population. Check asset validity."));
    }
}
```

## 模块依赖

要使用此插件，你的模块通常需要依赖 `Mutable` 插件（核心），以及可能的 `CustomizableObjectPopulation` 模块。具体依赖如下：

| 模块 | 用途 |
|---|---|
| `Mutable` | 提供底层的可定制对象系统，是此插件的基础。 |
| `CustomizableObjectPopulation` | 提供人口资产、人口类、采样器等核心运行时类。 |

**注意**：`CustomizableObjectPopulation` 模块自身在构建时依赖 `UnrealEd`、`DerivedDataCache`、`EditorStyle`、`MessageLog`。这意味着，如果你需要在游戏运行时（Runtime）中使用人口生成功能，你需要确保你的游戏模块正确链接了这些模块（通常在打包后会由插件处理）。在编辑器模块中则无此顾虑。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-29 | `f35985aa` | Fix Customizable Object Editor viewport orbit/pan broken with new gizmos | 修复了在新版操作手柄下，可定制对象编辑器视口旋转/平移功能失效的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到 `UE_LOGF`（可能指特定上下文或改进的日志宏）。 |
| 2026-03-25 | `6dcf9bb4` | [Mutable] Fix CO Instances not updating. | [Mutable] 修复可定制对象实例不更新的问题。 |
| 2026-01-22 | `ad8a0de1` | Update BuildVersionSettings that are out of date | 更新过时的构建版本设置。 |
| 2026-01-13 | `5e60b0a5` | [Mutable] Allow components having the same name. | [Mutable] 允许组件具有相同名称。 |

### 维护评价

- **状态**：**活跃维护中**。该插件创建于2024年9月，最近一次更新在2026年4月，近期有持续的提交，包括功能修复、代码迁移和底层依赖修复。
- **实验性**：该插件明确标记为 `IsExperimentalVersion = true` 且 `EnabledByDefault = false`。这意味着它功能可能不稳定，API 随时可能改变，不建议在生产环境中直接使用。它是从主 Mutable 插件中分离出来的独立实验性功能模块。
- **推荐度**：适合进行**原型开发、技术预研或内部工具制作**。若要在正式项目中使用，需要自行承担实验性功能的风险，并密切关注上游更新和破坏性变更。对于需要大量程序化生成个性化角色的项目，这是一个非常有潜力的工具，但需要等待其发展为稳定版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MutablePopulation)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/mutable-in-unreal-engine/) (Mutable 母插件文档，此插件扩展了其功能)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/MutablePopulation/) (未在提供的文件列表中明确指明独立测试文件位置，需查看源码目录结构)