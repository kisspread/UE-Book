# Interchange Editor

> The Interchange Editor plugin exposes the Interchange import framework and pipelines to Unreal Editor.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 交互编辑器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeEditor` (Runtime), `InterchangeEditorPipelines` (Runtime), `InterchangeEditorUtilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | unknown |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor) | |

## 用途

Interchange Editor 插件为 Unreal Editor 提供了一个用于配置和管理资产导入过程的图形化界面和框架。它本身不处理具体的文件格式解析，而是作为核心 Interchange 框架的编辑器端扩展，解决了以下问题：

1.  **统一配置界面**：为所有使用 Interchange 框架的资产导入提供一个统一的对话框 (`SInterchangePipelineConfigurationDialog`)，用于在导入前预览、配置和调整导入管线（Pipelines）。
2.  **可视化检查**：提供图检查器 (`SInterchangeGraphInspectorWindow`)，允许开发者直观地查看和调试由翻译器（Translator）生成的中间数据图（BaseNodeContainer）。
3.  **管线定制**：支持创建和使用蓝图（Blueprint）或 Python 脚本编写的自定义导入管线，实现高度可定制的导入逻辑。
4.  **资产分类管理**：通过“资产卡”(`SInterchangeAssetCard`) 的UI，让用户在导入前可以按资产类型（如静态网格、骨骼网格）选择性启用或禁用导入。

该插件是连接用户操作（导入文件）与底层 Interchange 导入引擎的桥梁，是编辑器工作流的核心组成部分。

## 使用场景

-   **从外部格式（如 FBX、glTF）导入资产时**，在弹出的导入对话框中看到的所有管线选项、冲突信息和预览功能，都由 Interchange Editor 插件提供。
-   **需要为特定项目定制资产导入流程时**，可以通过此插件创建自定义的蓝图管线（`UInterchangeEditorBlueprintPipelineBase`），并在导入对话框中选择它们。
-   **开发或调试新的 Interchange 翻译器或管线时**，可以使用图检查器窗口来查看翻译器输出的节点树和属性，以便定位问题。
-   **在编辑器脚本或工具中集成导入功能时**，可以通过此插件提供的接口（如 `UInterchangePipelineConfigurationGeneric`）来调用配置对话框。

## 蓝图用法

此插件的大部分功能通过编辑器UI暴露，核心节点和类主要用于C++扩展。通过蓝图可用的主要是其暴露的配置对话框。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ShowPipelineDialog_Internal` | 显示导入管线配置对话框的底层实现。通常通过更高层的 `UInterchangePipelineConfigurationGeneric` 类间接使用。 | `UInterchangePipelineConfigurationGeneric` |

### 使用示例（蓝图描述）

在蓝图中，通常不直接调用导入对话框，而是通过 `UInterchangeEditorSubsystem` 或直接在内容浏览器中拖拽文件触发。自定义管线可以通过创建基于 `UInterchangeEditorBlueprintPipelineBase` 的蓝图资产来实现，然后在导入对话框的“管线堆栈”下拉菜单中选择。

## C++ 用法

### 头文件引入

```cpp
// 引入自定义管线基类
#include “InterchangeEditorBlueprintPipelineBase.h”
// 引入管线配置对话框类
#include “PipelineConfiguration/InterchangePipelineConfigurationGeneric.h”
```

### 基本用法

创建一个自定义的编辑器专用导入管线。

```cpp
// MyPipeline.h
#pragma once

#include “InterchangeEditorBlueprintPipelineBase.h”
#include “MyPipeline.generated.h”

UCLASS()
class UMyCustomImportPipeline : public UInterchangeEditorPipelineBase
{
	GENERATED_BODY()

public:
	// 定义可配置的导入属性
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = “Import Settings”)
	bool bImportMaterial = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = “Import Settings”)
	float UniformScale = 1.0f;

protected:
	// 重写执行管线的核心函数
	virtual void ExecutePipeline(UInterchangeBaseNodeContainer* BaseNodeContainer, const TArray<UInterchangeSourceData*>& SourceDatas, const FString& ContentBasePath) override
	{
		// 在此处添加自定义的节点处理逻辑
		// 例如：遍历所有网格节点，应用缩放
		// BaseNodeContainer->GetNodes(…);
	}
};
```

### 进阶用法

通过代码直接触发带自定义参数的导入配置对话框。

```cpp
// 假设我们有一个源数据和一个默认的管线堆栈
UInterchangeSourceData* SourceData = ...; // 获取或创建源数据
TArray<FInterchangeStackInfo> PipelineStacks = ...; // 准备管线堆栈

// 创建配置参数
FPipelineConfigurationDialogParams DialogParams;
DialogParams.SourceData = SourceData;
DialogParams.PipelineStacks = PipelineStacks;
DialogParams.bReimport = false;

// 获取配置器并显示对话框
if (UInterchangePipelineConfigurationGeneric* Configuration = UInterchangePipelineConfigurationGeneric::StaticClass()->GetDefaultObject<UInterchangePipelineConfigurationGeneric>())
{
	EInterchangePipelineConfigurationDialogResult Result = Configuration->ShowPipelineDialog(DialogParams);
	if (Result == EInterchangePipelineConfigurationDialogResult::Import)
	{
		// 用户点击了导入，使用 DialogParams.OutPipelines 中的管线继续导入流程
	}
}
```
*(注：`ShowPipelineDialog` 为 `UInterchangePipelineConfigurationBase` 的公共接口，此处用 `Generic` 类的实例调用)*

## Demo 示例

一个最小的自定义编辑器管线，它会在导入时记录一条日志。

```cpp
// SimpleEditorPipeline.h
#pragma once

#include “InterchangeEditorBlueprintPipelineBase.h”
#include “SimpleEditorPipeline.generated.h”

UCLASS()
class USimpleEditorPipeline : public UInterchangeEditorPipelineBase
{
	GENERATED_BODY()

protected:
	virtual void ExecutePipeline(UInterchangeBaseNodeContainer* BaseNodeContainer, const TArray<UInterchangeSourceData*>& SourceDatas, const FString& ContentBasePath) override
	{
		UE_LOG(LogTemp, Log, TEXT(“SimpleEditorPipeline: Executing with %d source datas.”), SourceDatas.Num());
		// 这里可以调用父类默认行为，或完全自定义
		Super::ExecutePipeline(BaseNodeContainer, SourceDatas, ContentBasePath);
	}
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Interchange` | 核心的资产导入框架和中间数据表示（BaseNode, Translator等）。 |
| `InterchangeCore` | 可能包含 `UInterchangePipelineBase` 等核心类。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `099f7387` | [Interchange] Animation frame alignment and glTF translator frame aligner removed. | 移除了动画帧对齐和glTF翻译器的帧对齐器功能。 |
| 2026-04-22 | `cc360b1e` | Add accessor to InterchangeEditorScriptLibrary that returns actors in a level instance without loading it. | 为脚本库添加了访问器，可在不加载关卡实例的情况下获取其中的Actor。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-04-13 | `05458c60` | [Interchange] Reworking Static and Skeletal Mesh import settings | 重构了静态网格和骨骼网格的导入设置。 |

### 维护评价

该插件是 UE5 Interchange 资产导入流程的核心编辑器组件，处于**活跃维护**状态。近期提交显示 Epic 正在持续对其进行优化和清理（如日志宏迁移、功能移除、设置重构），以确保其稳定性和与新框架的兼容性。

由于其作为基础设施的角色，预计会跟随引擎长期维护。虽然近期没有增加颠覆性的新功能，但持续的维护表明它是健康且可靠的。**强烈推荐**在基于 Interchange 框架开发项目时使用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor)
- [官方文档]() (无)
- [测试用例]() (未提供路径)