# Interchange Editor

> The Interchange Editor plugin exposes the Interchange import framework and pipelines to Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | Interchange 编辑器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeEditor` (Runtime), `InterchangeEditorPipelines` (Runtime), `InterchangeEditorUtilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2015-08-20 |
| 年龄标签 | 👴 老古董（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor) | |

## 用途

InterchangeEditor 是一个**编辑器专属插件**，其核心作用是将 `Interchange` 框架（一个模块化、可扩展的资产导入/导出系统）的用户交互界面完整地暴露给 Unreal Editor。它不仅仅是一个简单的 API 暴露，而是一整套**可视化导入流程配置系统**。

它解决了以下问题：
1.  **可视化配置复杂导入流程**：允许用户在导入资产时，通过一个完整的对话框（`SInterchangePipelineConfigurationDialog`）实时配置、选择、启用或禁用不同的导入管道（Pipelines），并直观地看到每个资产类型的导入统计（通过资产卡片）。
2.  **检查与调试中间数据**：提供了一个图检查器（`SInterchangeGraphInspectorWindow`），允许用户在导入前检查源文件被解析后的中间表示（`UInterchangeBaseNodeContainer`），理解导入图的结构，从而诊断导入问题。
3.  **创建与管理自定义管道**：为创建蓝图（`UInterchangeEditorBlueprintPipelineBase`）、Python 以及 C++ 形式的自定义导入管道提供了工厂、资产定义和基础类，使开发者能够轻松扩展导入功能。
4.  **统一编辑器内的导入体验**：为 `Import`、`Reimport` 以及场景导入提供了统一的、可配置的对话框和后端逻辑。

简单来说，`InterchangeCore` 是引擎，“`InterchangeEditor`” 就是引擎的“驾驶舱”和“仪表盘”，为美术师和技术美术师提供控制和观察导入流程的界面。

## 使用场景

*   你需要从 FBX、glTF、USD 等格式导入一个复杂的 3D 模型，并希望**在导入前精确控制**网格体、材质、动画、LOD 等各个方面的处理方式。
*   你的项目有自定义的资产类型或特殊的导入需求，需要编写一个**特定的导入管道**（Pipeline），并通过可视化界面进行配置和测试。
*   你在导入资产时遇到了问题（例如材质丢失、动画错位），需要**查看源文件被解析后的内部图结构**，以确定是翻译器（Translator）还是管道（Pipeline）的环节出了错。
*   你需要在蓝图或 Python 脚本中，以程序化的方式触发一次带有特定配置的导入流程。

## 蓝图用法

此插件主要用于编辑器功能，蓝图交互主要集中在**创建自定义导入管道**上。

### 核心类

| 类 | 说明 |
|---|---|
| `UInterchangeEditorBlueprintPipelineBase` | 创建**编辑器专属**蓝图管道的基类。由此派生的蓝图只能在编辑器内使用，可用于定义额外的导入后处理逻辑或覆盖默认设置。 |
| `UInterchangeGraphInspectorPipeline` | 一个特殊的管道，专门用于驱动图检查器窗口的预览。它标记为不支持重导入。 |
| `UInterchangeCardsPipeline` | 由默认导入对话框内部使用，用于根据用户的资产卡片选择来启用或禁用特定的工厂节点。 |
| `UInterchangePipelineConfigurationGeneric` | 管道配置对话框的蓝图扩展点。通常通过 C++ 重写 `ShowPipelineDialog_Internal` 来提供自定义的导入对话框。 |

### 使用示例（蓝图描述）

1.  **创建自定义蓝图管道**:
    *   在内容浏览器右键，选择 **`Interchange` -> `Interchange Blueprint` -> `Interchange Editor Blueprint Pipeline`**。
    *   打开创建的蓝图资产，其父类已经是 `UInterchangeEditorBlueprintPipelineBase`。
    *   你可以重写 `ExecutePipeline` 等函数，在蓝图中添加逻辑。例如，在 `ExecutePipeline` 中遍历 `BaseNodeContainer` 中的节点，根据某些条件修改它们的属性。
    *   编译并保存。此蓝图资产现在会出现在自定义导入管道的选择列表中。

2.  **程序化触发带配置的导入**（通过蓝图或 Python 调用 `Interchange` 模块的函数，此插件为这些函数提供了 UI 前置层）。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeEditorPipelinesModule.h"
#include "InterchangeEditorBlueprintPipelineBase.h"
```

### 基本用法

**1. 检查模块可用性**
```cpp
// 来源: Public/InterchangeEditorPipelinesModule.h
if (IInterchangeEditorPipelinesModule::IsAvailable())
{
    // 模块已加载，可以安全使用
    IInterchangeEditorPipelinesModule& EditorPipelinesModule = IInterchangeEditorPipelinesModule::Get();
}
```

**2. 创建一个编辑器专属的 C++ 管道类**
```cpp
// 来源: Public/InterchangeEditorBlueprintPipelineBase.h
UCLASS()
class UMyImportPipeline : public UInterchangeEditorPipelineBase
{
    GENERATED_BODY()

public:
    virtual void ExecutePipeline(UInterchangeBaseNodeContainer* BaseNodeContainer, 
                                const TArray<UInterchangeSourceData*>& SourceDatas, 
                                const FString& ContentBasePath) override
    {
        Super::ExecutePipeline(BaseNodeContainer, SourceDatas, ContentBasePath);
        
        // 在此处添加你的自定义导入逻辑
        // 遍历 BaseNodeContainer 中的节点，进行处理或过滤
    }
    
    virtual bool SupportReimport() const override
    {
        // 你的管道是否需要支持重导入
        return true;
    }
};
```

### 进阶用法

**自定义管道配置对话框**
你可以通过继承 `UInterchangePipelineConfigurationGeneric` 并重写 `ShowPipelineDialog_Internal` 来完全接管导入对话框的创建逻辑，实现高度定制化的 UI。

## Demo 示例

以下是一个最小的编辑器专属管道示例，它在导入时为所有静态网格体节点强制添加一个自定义属性。

**头文件 (MyForceAttributePipeline.h):**
```cpp
#pragma once

#include "InterchangeEditorBlueprintPipelineBase.h"
#include "MyForceAttributePipeline.generated.h"

UCLASS(BlueprintType)
class UMyForceAttributePipeline : public UInterchangeEditorPipelineBase
{
    GENERATED_BODY()

public:
    UMyForceAttributePipeline();

protected:
    virtual void ExecutePipeline(UInterchangeBaseNodeContainer* BaseNodeContainer,
                                 const TArray<UInterchangeSourceData*>& SourceDatas,
                                 const FString& ContentBasePath) override;

    virtual bool SupportReimport() const override { return true; }
};
```

**源文件 (MyForceAttributePipeline.cpp):**
```cpp
#include "MyForceAttributePipeline.h"
#include "InterchangeStaticMeshFactoryNode.h"

UMyForceAttributePipeline::UMyForceAttributePipeline()
{
    PipelineDisplayName = NSLOCTEXT("MyImportPipeline", "PipelineName", "Force Custom Attribute");
}

void UMyForceAttributePipeline::ExecutePipeline(UInterchangeBaseNodeContainer* BaseNodeContainer,
                                                const TArray<UInterchangeSourceData*>& SourceDatas,
                                                const FString& ContentBasePath)
{
    // 必须调用父类方法
    Super::ExecutePipeline(BaseNodeContainer, SourceDatas, ContentBasePath);

    if (!BaseNodeContainer)
    {
        return;
    }

    // 遍历所有节点
    TArray<UInterchangeNode*> AllNodes;
    BaseNodeContainer->GetNodes(AllNodes);

    for (UInterchangeNode* Node : AllNodes)
    {
        // 检查是否为静态网格体工厂节点
        UInterchangeStaticMeshFactoryNode* StaticMeshNode = Cast<UInterchangeStaticMeshFactoryNode>(Node);
        if (StaticMeshNode)
        {
            // 强制添加或修改一个自定义布尔属性
            const UE::Interchange::FAttributeKey CustomAttributeKey = UE::Interchange::FAttributeKey(TEXT("bImportedByCustomPipeline"));
            StaticMeshNode->AddCustomAttribute<bool>(CustomAttributeKey, true);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 框架的核心模块，定义了节点、容器、管道基类等。 |
| `InterchangePipelines` | 提供了一系列通用的导入管道（如网格体、纹理、材质管道）。 |
| `AssetDefinition` | 用于定义自定义资产类型在编辑器中的显示方式和工厂。 |

*无其他特殊依赖（仅标准 Core/Engine/Slate 等）*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `099f7387` | [Interchange] Animation frame alignment and glTF translator frame aligner removed. | 移除了动画帧对齐功能和 glTF 翻译器的帧对齐器。 |
| 2026-04-22 | `cc360b1e` | Add accessor to InterchangeEditorScriptLibrary that returns actors in a level instance without loading assets. | 在编辑器脚本库中添加了一个访问器，用于返回关卡实例中的 Actor 而无需加载资产。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF。 |
| 2026-04-13 | `05458c60` | [Interchange] Reworking Static and Skeletal Mesh import settings. | 对静态网格体和骨骼网格体的导入设置进行了重构。 |

### 维护评价

**活跃维护**。
- **年龄**：插件历史较长（约11年），但一直处于持续开发和优化中。
- **近期活动**：最近数月有多次实质性更新，包括功能重构（网格体导入设置）、功能增删（动画帧对齐）、以及内部优化（日志宏迁移），表明核心团队仍在积极维护。
- **推荐度**：**强烈推荐使用**。作为 Unreal Engine 官方标准的导入框架，Interchange 及其编辑器部分正在逐步取代旧的 FBX 导入管线。对于新项目，使用此框架是面向未来的选择。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor)
- 官方文档：暂无特定文档，但引擎文档中关于“Interchange”的部分均与此相关。
- 测试用例：测试用例通常位于 `Engine/Tests/` 目录下与 `Interchange` 相关的项目中。