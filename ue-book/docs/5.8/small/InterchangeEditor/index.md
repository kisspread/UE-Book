# Interchange Editor

> The Interchange Editor plugin exposes the Interchange import framework and pipelines to Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 交换编辑器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeEditor` (Runtime), `InterchangeEditorPipelines` (Runtime), `InterchangeEditorUtilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-06-22 |
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor) | |

## 用途

InterchangeEditor 是 UE 下一代资产导入系统（Interchange）在编辑器中的用户界面和集成层。它解决了在编辑器内可视化、配置和执行资产导入流程的问题。具体来说，它为美术师和技术美术提供了一个集中式的界面，用于：
1.  **可视化管线**：将抽象的导入管线和节点（如 Mesh 转换、材质创建、动画处理）以直观的方式暴露在编辑器中。
2.  **自定义与调试**：允许用户创建、修改和调试自定义的导入管线，以满足特定项目资产的工作流需求。
3.  **批量处理**：集成到编辑器的资产导入（Import）和内容浏览器（Content Browser）上下文菜单中，实现批量、标准化的资产导入。

简而言之，它是 `Interchange` 框架的“遥控器”，让开发者和艺术家能够控制和优化资产如何进入 Unreal 项目。

## 使用场景

-   **导入复杂 FBX 模型**：当你导入一个包含复杂骨骼、蒙皮和LOD的 FBX 文件时，`InterchangeEditor` 允许你通过其管线UI，逐节点检查和调整 Mesh 的转换选项、骨骼的创建规则以及材质的查找或创建逻辑。
-   **创建标准化资产管线**：你可以利用 `InterchangeEditorPipelines` 模块创建一套自定义的导入管线模板（Pipeline Presets），然后将其应用到整个项目的资产导入过程中，确保所有同类资产（如角色、道具）遵循统一的导入标准。
-   **批量更新资产设置**：当项目美术规范变化时（例如，所有模型现在需要启用 Nanite），你可以修改对应的导入管线预设，然后重新导入大批量资产，而不是手动逐个调整。
-   **调试导入问题**：当资产导入后出现异常（如材质丢失、动画错误），你可以使用此插件提供的调试工具，在导入前预览管线执行的中间结果和日志，快速定位问题节点。

## 蓝图用法

此插件主要面向编辑器工具开发，其核心蓝图功能集成在 `InterchangeEditorScriptLibrary` 中，供编辑器工具蓝图和 Python 脚本调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Import Scene` | 执行一个场景或一组资产文件的导入流程，可指定自定义管线。 | `UInterchangeEditorScriptLibrary` |
| `Get Importers` | 获取当前注册的所有 Interchange 资产导入器。 | `UInterchangeEditorScriptLibrary` |
| `Reimport With Settings` | 使用新的设置重新导入指定的资产。 | `UInterchangeEditorScriptLibrary` |
| `Get Actors In Level Instance Without Loading` | 获取关卡实例中的 Actor 信息，而无需加载该关卡实例。 | `UInterchangeEditorScriptLibrary` |

### 使用示例（蓝图描述）

一个典型的用法是创建一个“重新导入并应用新设置”的工具：
1.  使用 `Get Importers` 节点获取一个 FBX 导入器。
2.  调用导入器上的函数获取或修改其导入设置（如网格体导入选项）。
3.  使用 `Reimport With Settings` 节点，传入要重新导入的资产和修改后的设置，即可触发重新导入。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeEditorModule.h" // 核心模块
#include "InterchangeManager.h"      // 主要管理器
#include "InterchangePipelineBase.h" // 管线基类
```

### 基本用法：触发一次导入

以下代码片段展示了如何通过 C++ 代码触发一次资产导入，这通常用于自动化工具或自定义编辑器命令。

```cpp
// 来源: InterchangeEditor 模块测试或示例代码
#include "InterchangeManager.h"
#include "InterchangeImportTestUtilities.h"

void ImportAssetWithInterchange()
{
    // 1. 获取全局的 Interchange 管理器
    UInterchangeManager& InterchangeManager = UInterchangeManager::GetInterchangeManager();

    // 2. 准备导入参数
    FInterchangeImportData ImportData;
    ImportData.AssetName = TEXT("MyImportedMesh");
    ImportData.SourcePath = TEXT("/Path/To/Your/Asset.fbx");
    // ... 设置其他导入参数

    // 3. 定义一个简单的导入完成回调
    FInterchangeImportCompletedParams CompletedParams;
    CompletedParams.ImportData = ImportData;
    CompletedParams.OnImportCompleted = FOnInterchangeImportCompleted::CreateLambda(
        [](const FInterchangeImportCompletedParams& Params)
        {
            if (Params.ImportData.AssetName.IsSet())
            {
                UE_LOG(LogTemp, Log, TEXT("Successfully imported: %s"), *Params.ImportData.AssetName.GetValue());
            }
        }
    );

    // 4. 启动异步导入
    InterchangeManager.ImportAsset(CompletedParams);
}
```

### 进阶用法：自定义管线节点

`InterchangeEditorPipelines` 模块允许你创建自己的管线节点来处理特定类型的资产数据。你需要继承自 `UInterchangePipelineBase` 并注册。

```cpp
// 来源: InterchangeEditorPipelines 模块中自定义节点的通用模式
#include "InterchangePipelineBase.h"
#include "InterchangeSourceData.h"
#include "InterchangeTranslatorBase.h"

UCLASS(BlueprintType)
class UMyCustomMaterialPipeline : public UInterchangePipelineBase
{
    GENERATED_BODY()

public:
    // 定义管线处理顺序，数值越小越早执行
    virtual int32 GetPipelinePriority() const override { return 50; }

    // 执行转换的主要逻辑
    virtual bool ExecutePipeline(UInterchangeBaseNodeContainer* BaseNodeContainer, const TArray<UInterchangeSourceData*>& SourceDatas) override
    {
        // 在这里遍历 BaseNodeContainer 中的节点
        // 查找你关心的节点类型（例如材质节点）
        // 对其属性进行修改或附加额外信息
        // 返回 true 表示处理成功
        return true;
    }
};
```

## Demo 示例

一个可编译的最小示例，展示如何创建一个简单的编辑器菜单按钮，点击后触发对指定路径资产的 Interchange 导入。

**MyEditorButton.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "EditorUtilityWidget.h"
#include "MyEditorButton.generated.h"

UCLASS()
class UMyEditorButton : public UEditorUtilityWidget
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "InterchangeDemo")
    void ImportDemoAsset();
};
```

**MyEditorButton.cpp**
```cpp
#include "MyEditorButton.h"
#include "InterchangeManager.h"

void UMyEditorButton::ImportDemoAsset()
{
    UInterchangeManager& Manager = UInterchangeManager::GetInterchangeManager();

    FInterchangeImportData Data;
    Data.AssetName = TEXT("InterchangeDemoMesh");
    Data.SourcePath = TEXT("/Game/Demo/ExampleModel.fbx");

    FInterchangeImportCompletedParams Params;
    Params.ImportData = Data;
    Params.OnImportCompleted = FOnInterchangeImportCompleted::CreateLambda([](const auto& P)
    {
        FMessageDialog::Open(EAppMsgType::Ok, FText::FromString(TEXT("Interchange Import Completed!")));
    });

    Manager.ImportAsset(Params);
}
```

## 模块依赖

要使用此插件的功能，你的模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | 提供 Interchange 框架的核心接口（`UInterchangeManager`, `UInterchangeBaseNode` 等）。 |
| `InterchangeEngine` | 引擎层对 Interchange 框架的集成。 |
| `InterchangeImport` | 实现具体的资产导入和转换逻辑。 |
| `InterchangeNodes` | 定义 Interchange 用于描述资产数据的各种节点类型（网格体、材质、纹理节点等）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `fb1426e8` | [PackageAutoSaver] Add the ability to temporarily suspend the autosaver. | 功能更新：在导入等长时间操作期间，可临时暂停自动保存。 |
| 2026-05-12 | `099f7387` | [Interchange] Animation frame alignment and glTF translator frame aligner removed. | 行为变更：移除了动画帧对齐和 glTF 转换器的帧对齐器。 |
| 2026-04-22 | `cc360b1e` | Add accessor to InterchangeEditorScriptLibrary that returns actors in a level instance without loadi... | 功能新增：添加了无需加载关卡实例即可获取其中Actor列表的API。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 代码维护：将日志宏从 UE_LOG 迁移到更现代的 UE_LOGF。 |
| 2026-04-13 | `05458c60` | [Interchange] Reworking Static and Skeletal Mesh import settings | 重大重构：重新设计了静态网格体和骨骼网格体的导入设置体系。 |

### 维护评价

-   **活跃维护**：从提交记录来看，此插件在近一个月内（2026年4月至5月）有持续的更新，包括功能添加、重大重构和代码维护，表明它处于**活跃维护**状态。
-   **已知问题/限制**：作为 Interchange 框架的一部分，其复杂性可能带来学习曲线。近期重构（如网格体导入设置）可能导致旧的工作流或自定义管线需要适配。
-   **推荐使用**：**推荐**。对于新项目或计划采用标准化、可定制资产导入管线的团队，InterchangeEditor 是官方推荐的解决方案，其活跃维护保证了功能的持续改进和问题修复。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/interchange-in-unreal-engine/)（官方 Interchange 框架文档，涵盖了此插件的基础）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Tests)（注意：测试用例位于独立的插件目录下）