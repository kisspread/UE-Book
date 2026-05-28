# Interchange Datasmith

> Interchange Importer for Datasmith.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith Interchange导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（参考材质、蓝图资产） |
| 模块 | `DatasmithInterchange` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-09-01 |
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Enterprise/DatasmithInterchange) | |

## 用途

DatasmithInterchange 插件是一个基于 **Interchange 框架** 实现的 Datasmith 文件导入器。它的核心目的是将 Datasmith 场景（`.udatasmith`）中的资产（如网格体、材质、灯光、动画、变体集等）转换为 Interchange 的标准化节点（`UInterchangeBaseNode`），并利用 Interchange 强大的管线（Pipeline）系统进行后续的资产创建工作。

简单来说，它解决了将 Datasmith 导入能力集成到 UE5 新一代资产交换框架（Interchange）中的问题。与传统的 Datasmith 导入器相比，它允许用户利用 Interchange 提供的统一导入设置、管线定制和后处理能力。

## 使用场景

- 你正在使用 Revit、SketchUp、Cinema 4D 等 CAD/BIM/DCC 软件，并通过 Datasmith 导线（Direct Link）或文件导出（.udatasmith）工作流程将大型复杂场景导入到 UE5。
- 你希望使用 Interchange 框架提供的、可定制的、统一的导入管线来处理 Datasmith 文件，以获得更精细的控制和更好的扩展性。
- 你需要在导入过程中自定义材质处理逻辑（例如，根据源软件 Revit、SketchUp 等选择不同的参考材质）。

## 蓝图用法

该插件主要通过其提供的**工厂节点（Factory Node）**、**管线（Pipeline）** 和**管理器（Manager）** 类来工作。这些类大部分都标记为 `BlueprintType` 和 `Experimental`，可以在蓝图中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get / Set CustomLightType` | 获取/设置 Datasmith 区域光节点的灯光类型（点光、线光、面光等） | `UInterchangeDatasmithAreaLightNode` |
| `Get / Set CustomLightShape` | 获取/设置 Datasmith 区域光节点的灯光形状（矩形、圆盘等） | `UInterchangeDatasmithAreaLightNode` |
| `Get / Set CustomDimensions` | 获取/设置 Datasmith 区域光节点的尺寸 | `UInterchangeDatasmithAreaLightNode` |
| `RegisterSelector` | 为特定的源主机（如 “Revit”）注册一个材质选择器 | `FDatasmithReferenceMaterialManager` |
| `GetSelector` | 根据源主机名获取已注册的材质选择器 | `FDatasmithReferenceMaterialManager` |
| `ProcessActor` | `UInterchangeDatasmithAreaLightFactory` 的核心方法，用于处理生成的 Actor | `UInterchangeDatasmithAreaLightFactory` |

### 使用示例（蓝图描述）

1.  **自定义材质处理**：
    *   在一个自定义的蓝图或 C++ 模块中，创建一个继承自 `FDatasmithReferenceMaterialSelector` 的类。
    *   重写 `GetMaterialPath` 函数，根据输入的 `EDatasmithReferenceMaterialType` 返回你项目中对应的材质路径。
    *   在编辑器启动或你的模块加载时，通过 `FDatasmithReferenceMaterialManager::Get().RegisterSelector(TEXT(“YourHost”), MakeShared<FYourCustomMaterialSelector>())` 注册你的选择器。
    *   当导入来自“YourHost”的 Datasmith 文件时，插件会自动调用你注册的选择器来决定使用哪些参考材质。

2.  **访问导入的灯光节点属性**：
    *   在 Interchange 导入管线的后期处理阶段（`ExecutePostImportPipeline`），你可以从 `UInterchangeBaseNodeContainer` 中查找 `UInterchangeDatasmithAreaLightNode` 类型的节点。
    *   通过蓝图节点 `GetCustomIntensity` 或 `GetCustomColor` 来读取或修改该灯光节点的属性，从而影响最终创建的灯光 Actor。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeDatasmithAreaLightNode.h"
#include "InterchangeReferenceMaterials/DatasmithReferenceMaterialManager.h"
#include "InterchangeDatasmithAreaLightFactory.h"
```

### 基本用法

该插件的 API 主要被 Interchange 管线和工厂在内部调用。作为开发者，你更可能通过扩展或配置来使用它。

**注册自定义材质选择器** (来源：`DatasmithReferenceMaterialManager.h` 及其使用示例)：

```cpp
// 假设在你的某个模块的 StartupModule 中
#include "InterchangeReferenceMaterials/DatasmithReferenceMaterialManager.h"
#include "YourCustomMaterialSelector.h" // 你自己的材质选择器头文件

void FYourModule::StartupModule()
{
    // ... 其他初始化代码 ...

    // 注册自定义的材质选择器
    if (UE::DatasmithInterchange::FDatasmithReferenceMaterialManager::Get().IsAvailable())
    {
        UE::DatasmithInterchange::FDatasmithReferenceMaterialManager::Get().RegisterSelector(
            TEXT("MyCustomHost"), // 一个标识你的数据来源的字符串
            MakeShared<FYourCustomMaterialSelector>()
        );
    }
}
```

**在管线中读取灯光节点信息** (来源：`InterchangeDatasmithAreaLightNode.h` 的用法逻辑)：

```cpp
// 在一个自定义管线的 ExecutePostImportPipeline 函数中
void UYourCustomPipeline::ExecutePostImportPipeline(const UInterchangeBaseNodeContainer* InBaseNodeContainer, const FString& NodeKey, UObject* CreatedAsset, bool bIsAReimport)
{
    Super::ExecutePostImportPipeline(InBaseNodeContainer, NodeKey, CreatedAsset, bIsAReimport);

    // 查找特定的 Datasmith 区域光节点
    TArray<UInterchangeDatasmithAreaLightNode*> AreaLightNodes;
    InBaseNodeContainer->GetNodesOfType<UInterchangeDatasmithAreaLightNode>(AreaLightNodes);

    for (UInterchangeDatasmithAreaLightNode* LightNode : AreaLightNodes)
    {
        float Intensity;
        if (LightNode->GetCustomIntensity(Intensity))
        {
            UE_LOG(LogInterchangeDatasmith, Log, TEXT("Found Area Light with Intensity: %f"), Intensity);
            // 可以在此对 Intensity 进行修改，或者记录日志等
        }

        FLinearColor Color;
        if (LightNode->GetCustomColor(Color))
        {
            UE_LOG(LogInterchangeDatasmith, Log, TEXT("Found Area Light with Color: %s"), *Color.ToString());
        }
    }
}
```

### 进阶用法

插件本身提供了一个完整的管线 `UInterchangeDatasmithPipeline`。如果你需要深度定制 Datasmith 的导入行为，可以创建一个继承自它的 C++ 类，并重写 `ExecutePipeline` 和 `ExecutePostImportPipeline` 方法。

## Demo 示例

由于该插件主要作为后台翻译器和管线运行，直接的可运行 Demo 较少。最核心的“用法”体现在如何配置或扩展其材质选择器系统。

**自定义材质选择器示例头文件 (`YourCustomMaterialSelector.h`)：**

```cpp
// YourCustomMaterialSelector.h
#pragma once

#include "InterchangeReferenceMaterials/DatasmithReferenceMaterialSelector.h"
#include "YourCustomMaterialSelector.generated.h"

UCLASS()
class UYourCustomMaterialSelector : public UObject, public UE::DatasmithInterchange::FDatasmithReferenceMaterialSelector
{
	GENERATED_BODY()

public:
	UYourCustomMaterialSelector();

	virtual const TCHAR* GetMaterialPath(EDatasmithReferenceMaterialType MaterialType) const override;

#if WITH_EDITOR
	virtual void PostImportProcess(EDatasmithReferenceMaterialType MaterialType, EDatasmithReferenceMaterialQuality MaterialQuality, UMaterialInstanceConstant* MaterialInstance) const override;
#endif

protected:
	// 你可以在这里存储配置数据，例如材质路径映射表
	UPROPERTY(EditAnywhere, Category = "Material Mapping")
	TMap<EDatasmithReferenceMaterialType, FSoftObjectPath> MaterialPathMap;
};
```

**对应的实现文件 (`YourCustomMaterialSelector.cpp`)：**

```cpp
// YourCustomMaterialSelector.cpp
#include "YourCustomMaterialSelector.h"
#include "Materials/MaterialInstanceConstant.h"

UYourCustomMaterialSelector::UYourCustomMaterialSelector()
{
	bIsValid = true; // 标记为有效选择器
}

const TCHAR* UYourCustomMaterialSelector::GetMaterialPath(EDatasmithReferenceMaterialType MaterialType) const
{
	if (const FSoftObjectPath* FoundPath = MaterialPathMap.Find(MaterialType))
	{
		return *FoundPath->GetAssetPathString();
	}
	// 或者返回一个默认路径
	return TEXT("/Game/Materials/DefaultDatasmithMaterial");
}

#if WITH_EDITOR
void UYourCustomMaterialSelector::PostImportProcess(EDatasmithReferenceMaterialType MaterialType, EDatasmithReferenceMaterialQuality MaterialQuality, UMaterialInstanceConstant* MaterialInstance) const
{
	Super::PostImportProcess(MaterialType, MaterialQuality, MaterialInstance);
	// 在这里对导入的材质实例进行后处理，例如设置特定的标量参数或纹理
	if (MaterialInstance)
	{
		MaterialInstance->SetScalarParameterValueEditorOnly(FName(“CustomParam”), 1.0f);
	}
}
#endif
```

## 模块依赖

从 `DatasmithInterchange.Build.cs` 分析得出，使用此插件的模块需要依赖：

| 模块 | 用途 |
|---|---|
| `CADTools` | 提供 CAD 文件处理的核心工具集 |
| `ParametricSurface` | 处理参数化曲面（如 NURBS）的生成和操作 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `099f7387` | [Interchange] Animation frame alignment and glTF translator frame aligner removed. | 优化了动画帧对齐逻辑，并移除了 glTF 翻译器中多余的帧对齐器。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 `UE_LOG` 迁移为新的格式化版本 `UE_LOGF`。 |
| 2026-04-13 | `05458c60` | [Interchange] Reworking Static and Skeletal Mesh import settings | 重构了静态网格体和骨骼网格体的导入设置，可能涉及管线或UI调整。 |
| 2026-03-04 | `7ceb4698` | Interchange - New Skeletal Mesh Combine Options | 为骨骼网格体导入添加了新的合并选项。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了之前一次全局查找替换带来的错误。 |

### 维护评价

该插件创建于 2022 年 9 月，距今约 4 年，属于实验性（`IsExperimentalVersion: true`）且默认禁用（`EnabledByDefault: false`）的状态。尽管标记为实验性，但从近期的提交记录看（最后一次更新在 2026 年 5 月），**插件仍在被积极维护和迭代**。近期的更新主要集中在动画、网格体导入功能的重构和优化上，表明 Epic Games 仍在持续投入开发。

**总结**：这是一个处于活跃实验阶段的插件。它代表了 Epic Games 将传统 Datasmith 导入流程迁移到更现代、可扩展的 Interchange 框架的努力。对于希望在 Interchange 框架下处理 Datasmith 资产，或者需要深度定制导入过程的高级用户和开发者来说，这是一个值得关注和尝试的组件。但由于其“实验性”状态，其 API 和功能在未来版本中可能会发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Enterprise/DatasmithInterchange)
- 官方文档：暂无（`.uplugin` 中 `DocsURL` 为空）
- 测试用例：在提供的源码信息中未找到明确的测试文件路径。