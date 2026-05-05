# Chaos Outfit Asset

> Outfit Asset plugin to create and assemble outfits made of Cloth Assets.

| 属性 | 值 |
|---|---|
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Dataflow 节点） |
| 模块 | `ChaosOutfitAssetDataflowNodes` (Runtime), `ChaosOutfitAssetEditor` (Runtime), `ChaosOutfitAssetEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosOutfitAsset) | |

## 用途

ChaosOutfitAsset 插件提供了一个基于 Dataflow 的服装资产编辑系统。它解决了服装资产的模块化组合问题，允许用户通过可视化的节点图（Dataflow Graph）来组装、查询和修改由多个布料资产（Cloth Assets）构成的服装（Outfit）。其核心价值在于将服装的创建流程数据化、节点化，使得服装的组装过程更加灵活、可编程，并能与 Chaos 布料模拟系统深度集成，特别适合需要动态调整服装组合或进行程序化服装生成的场景。

## 使用场景

- **角色定制系统**：你需要为一个角色创建多套可切换的服装，每套服装由上衣、裤子、鞋子等独立的布料部件组成。使用此插件，你可以通过 Dataflow 图将各个部件组合成完整的服装资产。
- **服装资产流水线**：你的美术团队需要批量处理和组装服装资产。通过编写 Dataflow 图，可以自动化地将多个布料资产合并、筛选尺码，并输出最终的服装资产。
- **程序化服装生成**：你希望根据角色的身体尺寸（如身高、胸围）动态生成或适配服装。插件中的 `FilterSizedOutfit` 等节点可以根据目标身体网格体自动选择合适的服装尺码。

## 蓝图用法

此插件的核心功能通过 **Dataflow 图** 实现，而非传统的蓝图函数调用。你需要在 Dataflow 编辑器中使用插件提供的专用节点来构建服装处理逻辑。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeOutfit` | 将多个布料资产（或服装资产）组合成一个新的服装。 | `FChaosOutfitAssetMakeOutfitNode` |
| `MakeSizedOutfit` | 创建一个包含多个尺码的服装，每个尺码对应一组布料资产和身体参考。 | `FChaosOutfitAssetMakeSizedOutfitNode` |
| `MergeOutfits` | 将多个服装合并为一个服装。 | `FChaosOutfitAssetMergeOutfitsNode` |
| `FilterSizedOutfit` | 从一个包含多尺码的服装中，根据指定的尺码名称或目标身体网格体，筛选出单一尺码的服装。 | `FChaosOutfitAssetFilterSizedOutfitNode` |
| `GetOutfitClothCollections` | 从服装中提取其包含的布料集合（Cloth Collections），可指定 LOD 级别。 | `FChaosGetOutfitClothCollectionsNode` |
| `GetOutfitBodyParts` | 从服装中提取其包含的身体部件骨骼网格体。 | `FChaosGetOutfitBodyPartsNode` |
| `OutfitQuery` | 查询服装的属性，例如是否包含有效的服装部件或有效的尺码。 | `FChaosOutfitAssetOutfitQueryNode` |
| `OutfitAssetTerminal` | Dataflow 图的终端节点，用于将处理完成的服装数据输出为 `UChaosOutfitAsset` 资产。 | `FChaosOutfitAssetTerminalNode` |

### 使用示例（Dataflow 图描述）

1.  **创建基础服装**：
    - 使用 `GetClothAsset` 节点获取一个或多个 `UChaosClothAsset` 资产。
    - 将它们连接到 `MakeOutfit` 节点的输入引脚。
    - `MakeOutfit` 节点的输出即为一个组合好的 `UChaosOutfit` 对象。

2.  **创建多尺码服装并筛选**：
    - 使用 `MakeSizedOutfit` 节点，为每个尺码（如 S, M, L）配置对应的布料资产和身体参考网格体。
    - 将输出的服装连接到 `FilterSizedOutfit` 节点。
    - 在 `FilterSizedOutfit` 节点上设置 `SizeName`（如 “M”）或连接一个 `TargetBody` 骨骼网格体，即可得到对应尺码的服装。

3.  **输出为资产**：
    - 将最终处理好的 `UChaosOutfit` 连接到 `OutfitAssetTerminal` 节点的 `Outfit` 输入。
    - 在 Dataflow 资产编辑器中编译并保存，即可生成一个 `UChaosOutfitAsset`。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosOutfitAsset/OutfitAsset.h"
#include "ChaosOutfitAsset/Outfit.h"
#include "ChaosClothAsset/ClothAsset.h"
```

### 基本用法

以下代码展示了如何在 C++ 中创建一个简单的服装资产并添加布料部件。此用法通常用于程序化生成或测试。

```cpp
// 假设已有一个 UChaosClothAsset* ClothAsset 指针
// 创建一个新的服装资产
UChaosOutfitAsset* OutfitAsset = NewObject<UChaosOutfitAsset>();

// 获取资产内部的服装对象（运行时数据）
UChaosOutfit* Outfit = OutfitAsset->GetOutfit();
if (Outfit)
{
    // 将布料资产添加到服装中
    // 注意：实际添加逻辑可能更复杂，涉及尺码和身体部件的关联
    // 此处仅为示意，具体API需参考源码
    Outfit->AddClothAsset(ClothAsset);
}

// 保存资产
FAssetRegistryModule::AssetCreated(OutfitAsset);
OutfitAsset->MarkPackageDirty();
```

### 进阶用法

结合 Dataflow 节点进行操作。通常，更复杂的服装组装逻辑会通过 Dataflow 图完成，但在 C++ 中可以调用图的评估过程。

```cpp
// 假设你有一个已经配置好的 Dataflow 图资产 (UDataflowAsset*)
// 并且图中包含 OutfitAssetTerminal 节点
UDataflowAsset* DataflowGraph = ...;

// 创建上下文并评估图，这将触发所有节点的 Evaluate 函数
UE::Dataflow::FContext Context;
DataflowGraph->Evaluate(Context);

// 从终端节点获取生成的服装资产
// 具体获取方式取决于图的结构和终端节点的实现
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何创建一个服装资产并为其添加一个布料资产。

**MyOutfitGenerator.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyOutfitGenerator.generated.h"

class UChaosClothAsset;
class UChaosOutfitAsset;

UCLASS(BlueprintType)
class UMyOutfitGenerator : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Outfit")
    UChaosOutfitAsset* GenerateOutfitFromCloth(UChaosClothAsset* InClothAsset);
};
```

**MyOutfitGenerator.cpp**
```cpp
#include "MyOutfitGenerator.h"
#include "ChaosOutfitAsset/OutfitAsset.h"
#include "ChaosOutfitAsset/Outfit.h"
#include "ChaosClothAsset/ClothAsset.h"

UChaosOutfitAsset* UMyOutfitGenerator::GenerateOutfitFromCloth(UChaosClothAsset* InClothAsset)
{
    if (!InClothAsset)
    {
        return nullptr;
    }

    // 创建新的服装资产
    UChaosOutfitAsset* NewOutfitAsset = NewObject<UChaosOutfitAsset>(GetTransientPackage(), NAME_None, RF_Public | RF_Standalone);
    if (!NewOutfitAsset)
    {
        return nullptr;
    }

    // 获取内部服装对象并添加布料资产
    UChaosOutfit* Outfit = NewOutfitAsset->GetOutfit();
    if (Outfit)
    {
        // 注意：这是一个简化的示意。真实的 AddClothAsset 可能需要更多参数（如LOD索引、身体部件类型等）。
        // 请参考 UChaosOutfit 类的实际接口。
        Outfit->AddClothAsset(InClothAsset);
    }

    // 标记资产为已修改
    NewOutfitAsset->MarkPackageDirty();
    return NewOutfitAsset;
}
```

## 模块依赖

要使用此插件的功能，你的模块需要依赖以下模块（除了常见的 Core, Engine 等）：

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | 提供核心的布料资产 (`UChaosClothAsset`) 类型。 |
| `Dataflow` | 提供 Dataflow 节点图框架，是本插件所有节点的基础。 |
| `GeometryCollection` | 提供 `FManagedArrayCollection` 等数据结构，用于存储布料集合数据。 |
| `MeshResizing` | 提供 RBF 插值 (`FMeshResizingRBFInterpolationData`) 等功能，用于服装尺码适配。 |

## 维护状态

### 近期更新

- 2026-04-22 `11dbcfb1` [Chaos Outfit Asset] Moved tthe ChaosOutfitAsset plugin out of Experimental and made it Beta.

### 维护评价

- **创建时间**：2026年4月，是一个非常新的插件。
- **维护状态**：**实验性/早期开发**。插件被标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，表明 Epic Games 正在积极开发和测试此功能，但尚未将其作为稳定特性默认启用。
- **推荐使用**：**谨慎推荐**。适合用于项目原型开发、技术预研或内部工具链构建。不建议在需要高度稳定性的生产项目中直接使用，因为其 API 和功能在未来版本中可能会有较大变动。建议密切关注引擎更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosOutfitAsset)
- [官方文档]() (暂无)
- [测试用例]() (暂未在提供信息中发现明确的测试文件路径)