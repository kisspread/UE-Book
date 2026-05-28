# Interchange Editor

> The Interchange Editor plugin exposes the Interchange import framework and pipelines to Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器管道 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeEditor` (Runtime), `InterchangeEditorPipelines` (Runtime), `InterchangeEditorUtilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-02-14 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor) | |

## 用途

InterchangeEditorPipelines 模块是 Interchange 导入框架的编辑器端扩展，其核心功能是将 Interchange 的翻译器（Translator）和管道（Pipeline）系统暴露给 Unreal Editor。它主要解决在编辑器中配置和管理资产导入流程的问题，为用户和开发者提供了定制化导入规则的工具。

具体来说，它提供了：
1.  **导入配置 UI**：在导入资产时弹出管道配置对话框，允许用户选择、配置和预览导入管道。
2.  **资产定义**：为 Interchange 蓝图管道和 Python 管道资产提供编辑器内的显示、创建和编辑支持。
3.  **细节面板自定义**：为 `UInterchangePipelineBase` 和 `UInterchangeBaseNode` 等核心对象提供高度定制的“细节”（Details）面板，以便直观地查看和编辑其复杂属性。
4.  **特殊管道实现**：包含如 `UInterchangeCardsPipeline`（用于控制导入资产类型的开关）和 `UInterchangeGraphInspectorPipeline`（用于场景图检查）等编辑器专用管道。

## 使用场景

-   你正在开发一个需要支持自定义资产格式导入的游戏或工具，并希望在编辑器中提供一个图形化界面让用户调整导入参数。
-   你需要为团队制定一套标准化的资产导入流程，并希望将这套流程打包成可配置的导入管道预设。
-   你使用 Interchange 框架从 FBX、glTF 等格式导入资产，并希望更精细地控制特定翻译器（如 glTF 或 MaterialX）的导入行为。
-   你需要调试或检查 Interchange 导入过程中生成的节点图和属性，使用 `SInterchangeGraphInspectorWindow` 来可视化。

## 蓝图用法

本模块主要提供编辑器端的管道创建基类和配置逻辑，蓝图用法侧重于创建编辑器专用的蓝图管道。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 创建“编辑器蓝图管道” | 创建一个仅在编辑器中有效的 Interchange 蓝图管道资产。 | `UInterchangeEditorBlueprintPipelineBaseFactory` |
| 创建“蓝图管道” | 创建一个标准的 Interchange 蓝图管道资产。 | `UInterchangeBlueprintPipelineBaseFactory` |
| 创建“Python 管道” | 创建一个 Interchange Python 管道资产。 | `UInterchangePythonPipelineAssetFactory` |

### 使用示例（蓝图描述）

1.  在内容浏览器中右键，选择“创建高级资产” -> “Interchange” -> “Interchange Blueprint”。
2.  在弹出的子菜单中，可以选择创建“Interchange Blueprint Pipeline”或“Interchange Editor Blueprint Pipeline”。
3.  创建后，打开该蓝图资产，在“我的蓝图”面板中覆盖 `Execute Pipeline` 事件图，即可开始用蓝图节点实现自定义的导入逻辑。

## C++ 用法

由于该模块主要为编辑器提供 UI 和流程，其 C++ 接口多用于扩展或深度定制编辑器行为。

### 头文件引入

```cpp
#include "InterchangeEditorPipelinesModule.h"
// 对于需要使用特定管道的场景
#include "InterchangeCardsPipeline.h"
#include "InterchangeGraphInspectorPipeline.h"
```

### 基本用法

以下示例展示了如何通过模块接口检查模块是否可用。
(基于 `IInterchangeEditorPipelinesModule` 接口设计)

```cpp
// 检查InterchangeEditorPipelines模块是否已加载
if (IInterchangeEditorPipelinesModule::IsAvailable())
{
    // 获取模块单例并执行操作
    IInterchangeEditorPipelinesModule& EditorPipelinesModule = IInterchangeEditorPipelinesModule::Get();
    // ... 可以调用模块提供的额外接口（如果未来扩展）
}
```

### 进阶用法

要创建自定义的编辑器专用管道，应继承自 `UInterchangeEditorPipelineBase`。
(基于 `UInterchangeEditorPipelineBase` 类定义)

```cpp
// MyEditorPipeline.h
#pragma once
#include "InterchangeEditorBlueprintPipelineBase.h"
#include "MyEditorPipeline.generated.h"

UCLASS(BlueprintType, MinimalAPI)
class UMyEditorPipeline : public UInterchangeEditorPipelineBase
{
    GENERATED_BODY()

public:
    // 覆盖执行函数，实现自定义的编辑器端导入处理逻辑
    virtual void ExecutePipeline(UInterchangeBaseNodeContainer* BaseNodeContainer, const TArray<UInterchangeSourceData*>& SourceDatas, const FString& ContentBasePath) override;

    // 此管道不支持重新导入
    virtual bool SupportReimport() const override { return false; }

    // 此管道必须在游戏线程执行
    virtual bool CanExecuteOnAnyThread(EInterchangePipelineTask PipelineTask) override
    {
        return false;
    }
};
```

```cpp
// MyEditorPipeline.cpp
#include "MyEditorPipeline.h"

void UMyEditorPipeline::ExecutePipeline(UInterchangeBaseNodeContainer* BaseNodeContainer, const TArray<UInterchangeSourceData*>& SourceDatas, const FString& ContentBasePath)
{
    Super::ExecutePipeline(BaseNodeContainer, SourceDatas, ContentBasePath);

    // 在这里添加你的自定义编辑器端导入逻辑
    // 例如，基于节点类型过滤或修改节点属性
}
```

## Demo 示例

一个最小的自定义编辑器专用管道示例。

**头文件 (MyCustomEditorPipeline.h)**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "InterchangeEditorBlueprintPipelineBase.h"
#include "MyCustomEditorPipeline.generated.h"

/**
 * 一个自定义的编辑器专用管道示例，仅在编辑器导入资产时执行。
 */
UCLASS(BlueprintType, MinimalAPI)
class UMyCustomEditorPipeline : public UInterchangeEditorPipelineBase
{
	GENERATED_BODY()

public:
	UMyCustomEditorPipeline();

protected:
	/** 管道核心执行逻辑 */
	virtual void ExecutePipeline(UInterchangeBaseNodeContainer* BaseNodeContainer, const TArray<UInterchangeSourceData*>& SourceDatas, const FString& ContentBasePath) override;

public:
	/** 自定义属性，可在细节面板中编辑 */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Custom Settings")
	bool bShouldApplyCustomRule = true;

	/** 自定义属性，可在细节面板中编辑 */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Custom Settings")
	float CustomScaleFactor = 1.0f;
};
```

**实现文件 (MyCustomEditorPipeline.cpp)**
```cpp
#include "MyCustomEditorPipeline.h"
#include "InterchangeImportTest.h"

UMyCustomEditorPipeline::UMyCustomEditorPipeline()
{
	// 设置管道的显示名称
	FriendlyName = TEXT("我的自定义编辑器管道");
}

void UMyCustomEditorPipeline::ExecutePipeline(UInterchangeBaseNodeContainer* BaseNodeContainer, const TArray<UInterchangeSourceData*>& SourceDatas, const FString& ContentBasePath)
{
	// 首先调用父类的执行逻辑
	Super::ExecutePipeline(BaseNodeContainer, SourceDatas, ContentBasePath);

	if (!bShouldApplyCustomRule)
	{
		return;
	}

	// 示例：遍历所有节点，找到网格体节点并应用自定义缩放
	TArray<UInterchangeBaseNode*> AllNodes;
	BaseNodeContainer->GetAllNodes(AllNodes);

	for (UInterchangeBaseNode* Node : AllNodes)
	{
		if (Node->GetTypeName() == UInterchangeMeshNode::StaticClass()->GetFName())
		{
			// 对网格体节点应用自定义缩放（仅为演示逻辑）
			UE_LOG(LogInterchangeImportTest, Log, TEXT("Applying custom scale %f to mesh node: %s"), CustomScaleFactor, *Node->GetUniqueID());
			// 实际应用需要修改节点属性，例如通过 Attribute 系统
		}
	}
}
```

## 模块依赖

从模块的 `.Build.cs` 文件分析，本模块主要依赖 Interchange 核心模块和标准的编辑器、资产系统模块。

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 框架的核心运行时模块。 |
| `InterchangeImport` | Interchange 导入功能和翻译器的核心实现。 |
| `InterchangeExport` | (可能被依赖) Interchange 导出功能。 |
| `AssetDefinition` | 提供 UAssetDefinition 相关功能，用于自定义资产在内容浏览器中的显示。 |

*注：此插件的依赖绝大多数为 UE 核心模块（如 Core, Engine, Slate）和 Interchange 自身模块，无特殊第三方依赖。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `099f7387` | [Interchange] Animation frame alignment and glTF translator frame aligner removed. | 移除了动画帧对齐功能以及 glTF 翻译器的帧对齐器。 |
| 2026-04-22 | `cc360b1e` | Add accessor to InterchangeEditorScriptLibrary that returns actors in a level instance without loading the level. | 为编辑器脚本库添加了一个访问器，用于在不加载关卡的情况下获取关卡实例中的 Actor。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-04-13 | `05458c60` | [Interchange] Reworking Static and Skeletal Mesh import settings. | 重构静态和骨骼网格体的导入设置。 |
| 2026-03-28 | `b7011d12` | [Interchange] Removing `bImportIfMaterialNotFound` from material pipeline. | 从材质管道中移除了 `bImportIfMaterialNotFound` 属性。 |

### 维护评价

-   **活跃维护**：插件在近 6 个月内有多次功能性更新（如重构导入设置、移除过时功能），表明仍在积极开发和维护中。
-   **稳定**：作为 UE 官方资产导入框架（Interchange）的编辑器部分，它是引擎的核心功能之一，长期支持有保障。
-   **演进中**：从 commit 历史看，API 和功能在不断调整（如移除动画帧对齐、修改材质管道），使用时需注意版本差异。
-   **推荐使用**：对于需要自定义导入流程的项目，此模块是必须依赖和使用的标准工具，建议采用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor)
-   [官方文档](https://docs.unrealengine.com/5.0/en-US/interchange-in-unreal-engine/) (Interchange 整体文档)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Tests) (注意：Interchange 的测试用例通常位于独立的 `Tests` 插件目录下，与 Editor 插件同级)