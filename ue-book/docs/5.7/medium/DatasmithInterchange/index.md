# Datasmith Interchange

> Interchange Importer for Datasmith.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith 交换导入 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、参考材质） |
| 模块 | `DatasmithInterchange` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Enterprise/DatasmithInterchange) | |

## 用途

**Datasmith Interchange** 是 UE5 新一代导入管线 **Interchange** 框架下的 **Datasmith 场景导入器**。它利用 Interchange 标准架构（Translator → Pipeline → Factory）来替代传统的 Datasmith 导入路径，提供统一的资产导入体验。主要解决：

- 将 `.udatasmith` 文件或其他 Datasmith 支持格式（如 FBX、CAD 文件）通过 Interchange 框架导入到 UE 项目
- 支持 Datasmith 独有的场景元素：区域光（Area Lights）、贴花（Decals）、IES 纹理、材质引用系统、变体集等
- 提供可插拔的材质选择器（Reference Material Selector），适配不同 DCC 来源（C4D、Revit、SketchUp、CityEngine 等）
- 与现有的 Interchange 通用管线（材质、网格、动画）无缝集成

该插件是实验性的，用于逐步替换旧版 Datasmith 导入器，未来将作为标准导入流程。

## 使用场景

- 你正在使用 **Interchange 框架** 构建自定义导入工具链，需要支持 Datasmith 专用的场景元素（如区域光、IES 纹理）
- 你需要将来自 Cinema 4D、Revit、SketchUp、CityEngine 等软件的 FBX 或 CAD 文件导入 UE，并保留原始材质引用和光照特征
- 你需要在运行时导入 `.udatasmith` 文件（例如用于建筑可视化或产品配置的实时场景加载）
- 你希望利用 Interchange 的异步导入、外部源缓存、统一设置面板等功能来优化导入流程

## 蓝图用法

该插件主要提供 Interchange 翻译器、管线以及自定义工厂节点的 BlueprintCallable 接口。最常用的蓝图形参是与区域光属性和材质引用相关的节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Custom Light Type` | 获取区域光类型（Point、Spot、Rect 等） | `UInterchangeDatasmithAreaLightNode` |
| `Set Custom Light Type` | 设置区域光类型 | `UInterchangeDatasmithAreaLightNode` |
| `Get Custom Light Shape` | 获取区域光形状（Rectangle、Sphere、Cylinder 等） | `UInterchangeDatasmithAreaLightNode` |
| `Set Custom Light Shape` | 设置区域光形状 | `UInterchangeDatasmithAreaLightNode` |
| `Get Custom Dimensions` | 获取区域光尺寸 | `UInterchangeDatasmithAreaLightNode` |
| `Set Custom Dimensions` | 设置区域光尺寸 | `UInterchangeDatasmithAreaLightNode` |
| `Get Custom Intensity` | 获取光源强度 | `UInterchangeDatasmithAreaLightFactoryNode` |
| `Set Custom Intensity` | 设置光源强度 | `UInterchangeDatasmithAreaLightFactoryNode` |
| `Get Custom Intensity Units` | 获取光源强度单位（Lumens、Candelas、EV 等） | `UInterchangeDatasmithAreaLightFactoryNode` |
| `Set Custom Intensity Units` | 设置光源强度单位 | `UInterchangeDatasmithAreaLightFactoryNode` |
| `Get Custom Color` | 获取光源颜色 | `UInterchangeDatasmithAreaLightFactoryNode` |
| `Set Custom Color` | 设置光源颜色 | `UInterchangeDatasmithAreaLightFactoryNode` |
| `Get Custom Temperature` | 获取光源色温 | `UInterchangeDatasmithAreaLightFactoryNode` |
| `Set Custom Temperature` | 设置光源色温 | `UInterchangeDatasmithAreaLightFactoryNode` |

> 以上节点均属于 Datasmith 特有属性，用于在 Interchange 节点容器中读写区域光参数。

### 使用示例（蓝图描述）

1. **导入带区域光的 Datasmith 场景**：使用标准的 Interchange 导入（如 `Import Translated Assets` 节点），插件会自动创建 `UInterchangeDatasmithAreaLightNode` 节点。你在 Post Import 管道中可以通过 `Get Custom Light Type` 等节点获取原始场景中的灯光属性，并进一步修改。
2. **自定义材质映射**：在 `UInterchangeDatasmithPipeline` 中，你可以通过 `MaterialPipeline` 子对象访问 `UInterchangeDatasmithMaterialPipeline`，该管线在导入过程中调用相应的材质选择器（如 `FDatasmithRevitMaterialSelector`）将 DCC 材质映射到 UE 材质实例。无直接蓝图节点，但可以通过修改管线设置类（如禁用 `bCreateMaterialReferencesFolders`）来影响行为。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeDatasmithTranslator.h"     // 翻译器
#include "InterchangeDatasmithPipeline.h"       // 管线
#include "InterchangeDatasmithAreaLightNode.h"  // 区域光节点
#include "InterchangeDatasmithAreaLightFactoryNode.h" // 区域光工厂节点
#include "InterchangeReferenceMaterials/DatasmithReferenceMaterialManager.h" // 材质选择器管理
```

### 基本用法

从测试用例或源码片段提取典型用法：

```cpp
// 示例：通过 Interchange 框架导入 Datasmith 场景
// 来源：InterchangeDatasmithTranslator.cpp (简化)

#include "InterchangeDatasmithTranslator.h"
#include "InterchangeDatasmithPipeline.h"
#include "InterchangeManager.h"

void ImportDatasmithSceneWithInterchange()
{
    UInterchangeManager& InterchangeManager = UInterchangeManager::GetInterchangeManager();

    // 创建源数据，指向 .udatasmith 文件
    UInterchangeSourceData* SourceData = InterchangeManager.CreateSourceData(TEXT("/Game/MyScene.udatasmith"));
    if (!SourceData)
    {
        return;
    }

    // 可选：创建并设置自定义翻译器设置
    UInterchangeDatasmithTranslatorSettings* TranslatorSettings = NewObject<UInterchangeDatasmithTranslatorSettings>();
    TranslatorSettings->DatasmithOption = NewObject<UDatasmithImportOptions>();
    // ... 设置 DatasmithImportOptions 参数

    // 创建导入资产参数
    FImportAssetParameters Params;
    Params.ReimportAsset = nullptr;
    Params.bIsAutomated = false;

    // 启动异步导入（通常在编辑器环境下）
    InterchangeManager.ImportAsync(TEXT("/Game/ImportedScenes"), SourceData, Params);
}
```

### 进阶用法

使用自定义管线处理区域光属性：

```cpp
// 在自定义管线中处理区域光节点
// 来源：InterchangeDatasmithLevelPipeline.cpp (部分)

void UInterchangeDatasmithLevelPipeline::SetupAreaLight(
    UInterchangeDatasmithAreaLightFactoryNode* AreaLightFactoryNode,
    const UInterchangeDatasmithAreaLightNode* AreaLightNode) const
{
    // 从 AreaLightNode 获取原始场景的 Datasmith 属性
    EDatasmithAreaLightActorType LightType;
    if (AreaLightNode->GetCustomLightType(LightType))
    {
        // 将类型复制到工厂节点，以便后续创建 Actor
        AreaLightFactoryNode->SetCustomLightType(LightType);
    }

    EDatasmithAreaLightActorShape Shape;
    if (AreaLightNode->GetCustomLightShape(Shape))
    {
        AreaLightFactoryNode->SetCustomLightShape(Shape);
    }

    FVector2D Dimensions;
    if (AreaLightNode->GetCustomDimensions(Dimensions))
    {
        AreaLightFactoryNode->SetCustomDimensions(Dimensions);
    }

    // 颜色、强度等属性
    FLinearColor Color;
    if (AreaLightNode->GetCustomColor(Color))
    {
        AreaLightFactoryNode->SetCustomColor(Color);
    }

    // 注：更多属性可在完整头文件中找到
}
```

## Demo 示例

一个最小 C++ 示例，展示如何通过自定义 Interchange 管线处理 Datasmith 区域光材质。

### MyDatasmithPipeline.h

```cpp
#pragma once

#include "InterchangeDatasmithPipeline.h"
#include "MyDatasmithPipeline.generated.h"

UCLASS()
class UMyDatasmithPipeline : public UInterchangeDatasmithPipeline
{
    GENERATED_BODY()

protected:
    virtual void ExecutePipeline(UInterchangeBaseNodeContainer* BaseNodeContainer,
        const TArray<UInterchangeSourceData*>& SourceDatas,
        const FString& ContentBasePath) override;
};
```

### MyDatasmithPipeline.cpp

```cpp
#include "MyDatasmithPipeline.h"
#include "InterchangeDatasmithAreaLightNode.h"
#include "InterchangeDatasmithAreaLightFactoryNode.h"
#include "InterchangeManager.h"

void UMyDatasmithPipeline::ExecutePipeline(UInterchangeBaseNodeContainer* BaseNodeContainer,
    const TArray<UInterchangeSourceData*>& SourceDatas,
    const FString& ContentBasePath)
{
    // 先执行父类逻辑（常规导入）
    Super::ExecutePipeline(BaseNodeContainer, SourceDatas, ContentBasePath);

    // 遍历所有区域光节点，调整其强度为两倍
    TArray<UInterchangeDatasmithAreaLightNode*> AreaLightNodes;
    BaseNodeContainer->IterateNodes([&](const FString& NodeUid, UInterchangeBaseNode* Node)
    {
        if (UInterchangeDatasmithAreaLightNode* AreaLightNode = Cast<UInterchangeDatasmithAreaLightNode>(Node))
        {
            AreaLightNodes.Add(AreaLightNode);
        }
    });

    for (UInterchangeDatasmithAreaLightNode* AreaLightNode : AreaLightNodes)
    {
        float Intensity;
        if (AreaLightNode->GetCustomIntensity(Intensity))
        {
            AreaLightNode->SetCustomIntensity(Intensity * 2.0f);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | 提供 Interchange 框架基础类型和节点容器 |
| `InterchangeEngine` | Interchange 管理器和导入接口 |
| `DatasmithCore` | Datasmith 场景元素定义（IDatasmithScene, EDatasmithReferenceMaterialType 等） |
| `DatasmithImporter` | 传统 Datasmith 导入器基础（UDatasmithImportOptions 等） |
| `DatasmithTranslator` | Datasmith 翻译器通用接口 |
| `MeshPaint` | 可选，与 Datasmith 附加数据交互 |

> 提示：运行时环境可能还需要 `InterchangePipelines`（通用管线）和 `InterchangeFactoryNodes`。这些在官方插件中作为公共依赖自动引入。

## 维护状态

### 近期更新

- 2025-12-18 `3f562d0e` — Fixed crash when Interchange stack names have been modified.
- 2025-07-18 `462ec4ed` — Fix warning V623: Consider inspecting the '?:' operator. A temporary object is being created.
- 2025-07-16 `cbceee9f` — [Interchange] Bug fix for FindFactoryNodeByUniqueID in Datasmith Utils.
- 2025-05-01 `07e44ca8` — [Interchange] UInterchangeBaseNode setup calls streamlining.
- 2025-04-23 `b62a7465` — [Interchange] Updating Analytics tracking for Translators.

### 维护评价

| 项目 | 评价 |
|---|---|
| 创建时间 | 2025-04-23，距今约 1 年 |
| 最近更新 | 2025-12-18（约 4 个月前），有实质性 bug 修复 |
| 活跃度 | 中等，虽然更新频率不高但每次都有修复或改进 |
| 实验性 | 标记为 `IsExperimentalVersion=true`，API 和架构可能变化 |
| 推荐度 | 👍 建议在 Interchange 框架项目中试用，但避免在生产旧版 Datasmith 导入的任务中完全替代；适合需要 Datasmith 特有元素的新项目 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Enterprise/DatasmithInterchange)
- [Interchange 框架文档 (UE 官方)](https://docs.unrealengine.com/5.3/en-US/interchange-framework-in-unreal-engine/)
- [测试用例（部分）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Enterprise/DatasmithInterchange/Tests)