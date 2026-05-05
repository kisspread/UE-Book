# Dataprep Editor

> A tool to simplify creation and execution of data preparation pipelines from within the Unreal Editor.

| 属性 | 值 |
|---|---|
| 分类 | Dataprep |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `DataprepCore` (Runtime), `DataprepEditor` (Runtime), `DataprepEditorScriptingUtilities` (Runtime), `DataprepLibraries` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-11-22 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DataprepEditor) | |

## 用途

Dataprep Editor 是一个企业级数据准备框架，旨在解决从外部（特别是 CAD、BIM 等专业格式）导入数据后，需要进行大量手动清理、优化和转换的痛点。它提供了一个可视化的、基于节点的编辑器（Visual Dataprep），允许用户创建可重复使用的数据处理管道（Recipe）。

其核心架构包含三个部分：
1.  **生产者 (Producer)**：负责将外部数据（如 Datasmith 文件）导入到临时的“数据准备环境”中。
2.  **配方 (Recipe)**：由一系列“操作 (Action)”组成。每个操作通常包含一个或多个“过滤器 (Filter)”来选择环境中的对象子集，以及一个或多个“操作 (Operation)”来修改这些对象（如删除、合并、设置材质、优化网格等）。
3.  **消费者 (Consumer)**：将处理后的数据准备环境输出为持久化资产（如标准的 Datasmith 场景资产）。

该插件使得非程序员（如技术美术、数据工程师）也能通过图形化界面构建复杂的数据导入和优化流程，并将这些流程保存为资产，在项目中重复使用或通过脚本批量执行。

## 使用场景

- **建筑、工程、施工 (AEC) 行业**：导入大型 Revit 或 Navisworks 模型后，自动清理隐藏对象、合并相同材质、优化几何体、设置碰撞体等。
- **产品设计与制造**：处理从 SolidWorks、CATIA 等软件导入的复杂装配体，进行层级简化、LOD 生成。
- **影视与虚拟制片**：准备来自 CAD 软件的场景资产，确保其符合虚幻引擎的性能和渲染要求。
- **任何需要批量、标准化处理外部 3D 数据的流程**：将手动、重复的数据清理工作自动化。

## 蓝图用法

蓝图功能主要通过 `UEditorDataprepAssetLibrary` 静态函数库暴露，分类为 `Editor Scripting | Dataprep Asset`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExecuteDataprep` | 执行一个完整的 Dataprep 资产（运行生产者、配方、消费者）。 | `UEditorDataprepAssetLibrary` |
| `GetProducersCount` | 获取 Dataprep 资产中生产者的数量。 | `UEditorDataprepAssetLibrary` |
| `GetProducer` | 通过索引获取 Dataprep 资产中的一个生产者。 | `UEditorDataprepAssetLibrary` |
| `RemoveProducer` | 从 Dataprep 资产中移除指定索引的生产者。 | `UEditorDataprepAssetLibrary` |
| `AddProducer` | 向 Dataprep 资产添加一个新的生产者（会触发编辑器 UI 流程）。 | `UEditorDataprepAssetLibrary` |
| `GetConsumer` | 获取 Dataprep 资产的消费者。 | `UEditorDataprepAssetLibrary` |
| `SetConsumer` | 设置 Dataprep 资产的消费者。 | `UEditorDataprepAssetLibrary` |
| `GetActionsCount` | 获取 Dataprep 资产配方中的操作数量。 | `UEditorDataprepAssetLibrary` |
| `GetAction` | 通过索引获取配方中的一个操作。 | `UEditorDataprepAssetLibrary` |
| `RemoveAction` | 从配方中移除指定索引的操作。 | `UEditorDataprepAssetLibrary` |
| `AddAction` | 向配方添加一个新的操作。 | `UEditorDataprepAssetLibrary` |
| `SetEditorProperty` | **重要**：用于设置 Dataprep 操作中可参数化对象的属性，以确保与编辑器状态同步。 | `UEditorDataprepAssetLibrary` |

### 使用示例（蓝图描述）

1.  **执行现有资产**：
    - 创建一个 `ExecuteDataprep` 节点。
    - 将你的 `UDataprepAsset` 资产引用连接到 `DataprepAssetInterface` 引脚。
    - 为 `LogReportingMethod` 和 `ProgressReportingMethod` 选择合适的枚举值（如 `StandardLog`）。
    - 执行该节点即可运行整个数据准备流程。

2.  **通过脚本修改配方**：
    - 使用 `GetActionsCount` 和 `GetAction` 循环遍历现有操作。
    - 使用 `RemoveAction` 删除不需要的操作。
    - 使用 `AddAction` 添加新的操作。
    - 对于新操作中的过滤器或操作对象，使用 `SetEditorProperty` 来设置其具体参数（例如，设置一个“删除”操作要删除的对象名称）。

## C++ 用法

### 头文件引入

```cpp
#include "EditorDataprepAssetLibrary.h"
#include "DataprepAsset.h"
#include "DataprepContentProducer.h"
#include "DataprepContentConsumer.h"
```

### 基本用法

以下示例展示了如何在 C++ 中执行一个已有的 Dataprep 资产。

```cpp
// 假设你已经有一个 UDataprepAsset* 指针 DataprepAsset
#include "EditorDataprepAssetLibrary.h"

void ExecuteMyDataprepAsset(UDataprepAsset* DataprepAsset)
{
    if (DataprepAsset)
    {
        // 使用标准日志记录，不报告进度
        bool bSuccess = UEditorDataprepAssetLibrary::ExecuteDataprep(
            DataprepAsset,
            EDataprepReportMethod::StandardLog,
            EDataprepReportMethod::NoFeedback
        );

        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("Dataprep asset executed successfully."));
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Dataprep asset execution failed."));
        }
    }
}
```

### 进阶用法

以下示例展示了如何以编程方式构建一个简单的 Dataprep 配方。

```cpp
#include "EditorDataprepAssetLibrary.h"
#include "DataprepAsset.h"
#include "DataprepActionAsset.h"
#include "DataprepOperations.h" // 假设包含具体操作类的头文件

void BuildSimpleDataprepRecipe(UDataprepAsset* DataprepAsset)
{
    if (!DataprepAsset) return;

    // 1. 清空现有配方（可选）
    int32 ActionCount = UEditorDataprepAssetLibrary::GetActionsCount(DataprepAsset);
    for (int32 i = ActionCount - 1; i >= 0; --i)
    {
        UEditorDataprepAssetLibrary::RemoveAction(DataprepAsset, i);
    }

    // 2. 添加一个新操作
    UDataprepActionAsset* NewAction = UEditorDataprepAssetLibrary::AddAction(DataprepAsset);
    if (NewAction)
    {
        // 3. 为操作添加步骤（过滤器和操作）
        // 注意：实际添加步骤的 API 可能更复杂，这里为示意。
        // 通常需要创建 UDataprepFilter 和 UDataprepOperation 的子类实例并添加到 Action 中。
        // 例如：
        // UDataprepFilterByType* FilterByType = NewObject<UDataprepFilterByType>(NewAction);
        // NewAction->AddStep(FilterByType);
        //
        // UDataprepOperationDelete* DeleteOp = NewObject<UDataprepOperationDelete>(NewAction);
        // NewAction->AddStep(DeleteOp);

        // 4. 使用 SetEditorProperty 设置操作参数（关键步骤）
        // 假设我们有一个名为 “ObjectNameToDelete” 的属性
        // UEditorDataprepAssetLibrary::SetEditorProperty(DeleteOp, “ObjectNameToDelete”, “OldMesh_01”);
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何创建一个 Dataprep 资产并执行它。

**MyDataprepDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDataprepDemo.generated.h"

class UDataprepAsset;

UCLASS()
class AMyDataprepDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyDataprepDemo();

    UPROPERTY(EditAnywhere, Category = "Dataprep")
    UDataprepAsset* DataprepAssetToRun;

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "Dataprep")
    void RunDataprepPipeline();
};
```

**MyDataprepDemo.cpp**
```cpp
#include "MyDataprepDemo.h"
#include "EditorDataprepAssetLibrary.h"
#include "DataprepAsset.h"

AMyDataprepDemo::AMyDataprepDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDataprepDemo::RunDataprepPipeline()
{
    if (DataprepAssetToRun)
    {
        UE_LOG(LogTemp, Log, TEXT("Starting Dataprep execution..."));
        bool bSuccess = UEditorDataprepAssetLibrary::ExecuteDataprep(
            DataprepAssetToRun,
            EDataprepReportMethod::StandardLog,
            EDataprepReportMethod::SameFeedbackAsEditor
        );

        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("Dataprep pipeline completed successfully."));
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Dataprep pipeline failed."));
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No Dataprep asset assigned."));
    }
}
```

## 模块依赖

从 `DataprepEditorScriptingUtilities.Build.cs` 分析，该模块依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `DataprepCore` | Dataprep 的核心运行时逻辑，包括资产定义、操作、过滤器等基础类。 |
| `DatasmithContent` | 提供 Datasmith 相关的内容类型和资产支持。 |
| `DatasmithImporter` | 提供 Datasmith 文件的导入功能，是 `DataprepContentProducer` 的基础。 |
| `DatasmithExporter` | 提供 Datasmith 的导出功能，可能与消费者相关。 |
| `MeshDescription` | 用于处理和优化网格几何体数据。 |
| `MeshMergeUtilities` | 提供网格合并的工具函数。 |
| `MeshReductionInterface` | 提供网格减面（LOD 生成）的接口。 |
| `MeshUtilities` | 通用的网格处理工具。 |
| `RawMesh` | 处理原始网格数据的模块。 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格相关的通用工具。 |
| `StaticMeshDescription` | 静态网格的特定描述和处理。 |

## 维护状态

### 近期更新

```
- 7ce67da71ab9 [Engine/Plugins] * Another batch iwyu updates to reduce number of includes used in files
- 01b7c9f4f5f5 Merge UE5/RES @ 15958325 to UE5/Main This represents UE4/Main @ 15913390 and Dev-PerfTest @ 15913304
- ba1bb3d2d019 Removed all source code related to BP from Dataprep core and editor code
```

**解读**：
1.  `7ce67da71ab9` (2024-10-03): 一次全引擎范围的 IWYU (Include What You Use) 更新，旨在减少头文件依赖，属于代码维护和优化。
2.  `01b7c9f4f5f5` (2024-09-15): 一次分支合并，将 RES 分支的改动合并到主分支，属于常规的版本集成。
3.  `ba1bb3d2d019` (2021-08-20): **重要更新**。移除了 Dataprep 核心和编辑器代码中所有与蓝图 (BP) 相关的源代码。这表明插件的架构发生了重大变化，可能简化了代码库，但也意味着早期版本中可能存在的蓝图扩展点被移除。

### 维护评价

Dataprep Editor 是一个功能完整的企业级工具，但其维护状态需要谨慎看待。

- **创建时间**：2019年底，已有约5年历史。
- **最近更新**：最近的实质性更新（移除蓝图代码）发生在2021年8月。此后的更新主要是全引擎范围的维护性提交（如IWYU、分支合并），没有针对该插件本身的功能增强或Bug修复。
- **活跃度**：**维护不活跃**。超过2年没有针对该插件的功能性更新。
- **已知限制**：作为“Enterprise”插件，其主要面向特定行业（AEC）。默认禁用 (`EnabledByDefault: false`)，需要用户手动启用。从代码移除蓝图支持来看，其可扩展性可能主要限于C++。
- **推荐使用**：如果你的项目**强烈依赖**从CAD/BIM等专业格式导入数据，并且需要标准化的处理流程，那么这个插件仍然是一个有价值的选择，因为它提供了成熟的、可视化的解决方案。但是，你应该意识到它可能不会获得新功能，并且在未来的引擎版本中可能存在兼容性风险。对于新的、非专业数据导入需求，建议评估其他更活跃维护的方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DataprepEditor)
- [官方文档]() (无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DataprepEditor/Tests) (路径推断)