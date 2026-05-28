# Dataprep Editor

> A tool to simplify creation and execution of data preparation pipelines from within the Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 数据准备编辑器 |
| 分类 | Dataprep |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产、操作蓝图、测试资源） |
| 模块 | `DataprepCore` (Runtime), `DataprepEditor` (Runtime), `DataprepEditorScriptingUtilities` (Runtime), `DataprepLibraries` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-11-22 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DataprepEditor) | |

## 用途

Dataprep 插件是一个**数据准备和清理的管道系统**，旨在解决从外部数据源（如 FBX、OBJ、CSV 等）导入资产时的标准化和优化问题。它允许用户在编辑器中创建一个可视化的处理流程，对导入的资产（如网格体、材质、纹理）和关卡中的 Actor 进行批量、自动化的修改、筛选和优化，从而确保导入的数据符合项目的规范和性能要求。

其核心解决的是**大规模资产导入的“脏数据”问题**：通过定义一系列规则（过滤器、操作），可以自动移除不需要的面、简化材质、重命名、添加元数据等，替代了繁琐的人工检查和修改。

## 使用场景

- **建筑可视化或工业设计**：从 CAD 或其他 DCC 软件导入复杂的模型，需要自动清理隐藏面、优化材质命名并生成 LOD。
- **游戏资产管线**：批量导入角色或道具，需要统一设置碰撞、调整纹理格式、移除未使用的骨骼或顶点。
- **数据驱动内容生成**：从数据库或 CSV 文件导入参数，用于批量生成或修改关卡中的 Actor 和资产属性。
- **自动化资产打包**：在构建或导出前，通过运行一个 Dataprep 管道来确保所有资产处于最优状态。

## 蓝图用法

在蓝图中，Dataprep 主要通过 `UDataprepAssetInterface` 及其相关类进行交互，用于程序化地创建、配置和执行数据准备管道。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute` | 执行一个 Dataprep 动作（包含一组操作步骤） | `UDataprepActionAsset` |
| `Get Actions` | 获取 Dataprep 资产中包含的所有动作列表 | `UDataprepAsset` |
| `Add Action` | 向 Dataprep 资产中添加一个新的动作 | `UDataprepAsset` |
| `Set Consumer` | 设置管道的输出消费者（例如 FBX 导出器） | `UDataprepAssetInterface` |
| `Set Level Name` | 设置消费者输出的目标关卡名称 | `UDataprepContentConsumer` |
| `Set Target Content Folder` | 设置消费者输出资产的目标文件夹路径 | `UDataprepContentConsumer` |
| `Log Info` | 在操作执行过程中记录一条信息日志 | `UDataprepOperation` |
| `Begin Work / ReportProgress / EndWork` | 管理操作执行时的进度报告 | `UDataprepOperation` |

### 使用示例（蓝图描述）

1. **执行现有管道**：获取一个 `UDataprepAsset` 对象引用，调用 `Execute` 节点即可运行其定义好的完整管道。
2. **程序化创建管道**：
   - 使用 `Make Dataprep Asset` 节点或 `Spawn Actor`（如果资产在世界中）创建一个新的 `UDataprepAsset`。
   - 调用 `Add Action` 节点添加动作。
   - 获取动作后，使用 `Add Step` 系列节点向动作中添加过滤器和操作步骤。
   - 通过 `Set Consumer` 设置输出，例如使用 `FBX Exporter` 消费者。
   - 最后调用整个资产的 `Execute` 节点。

## C++ 用法

### 头文件引入

```cpp
#include "DataprepAsset.h"
#include "DataprepActionAsset.h"
#include "DataprepContentConsumer.h"
// 根据需要引入具体的操作或过滤器头文件
```

### 基本用法

以下示例展示如何在 C++ 中创建并执行一个简单的 Dataprep 管道。

```cpp
// 来源：基于 DataprepCore 和 DataprepLibraries 模块的核心功能推断
#include "DataprepAsset.h"
#include "DataprepActionAsset.h"
#include "Factories/DataprepFBXConsumer.h" // 假设使用FBX消费者

void ExecuteSimpleDataprepPipeline()
{
    // 1. 创建或获取一个 Dataprep 资产
    UDataprepAsset* DataprepAsset = NewObject<UDataprepAsset>();
    
    // 2. 添加一个动作（Action）
    UDataprepActionAsset* Action = DataprepAsset->GetAction(DataprepAsset->AddAction());
    
    // 3. 向动作中添加一个操作步骤（例如，一个简单的重命名操作）
    // 假设我们有一个名为 UMyRenameOperation 的自定义操作
    int32 StepIndex = Action->AddStep(UMyRenameOperation::StaticClass());
    
    // 4. 设置管道的消费者（输出）
    UDataprepContentConsumer* Consumer = DataprepAsset->SetConsumer(UDataprepFBXConsumer::StaticClass());
    Consumer->SetTargetContentFolder(TEXT("/Game/ExportedAssets"));
    
    // 5. 执行整个管道
    // 注意：需要提供一个上下文，包含要处理的资产和世界
    FDataprepConsumerContext Context;
    Context.SetAssets(/* 要处理的资产数组 */);
    // ... 设置其他上下文信息
    
    // 调用资产的完整执行流程（生产 -> 操作 -> 消费）
    // FDataprepCoreUtils::ExecuteDataprep(DataprepAsset, Logger, Reporter);
}
```

### 进阶用法

结合参数化系统和批处理，可以实现更灵活的管道。

```cpp
// 来源：基于 DataprepParameterization 和 DataprepAssetInstance 的功能推断
#include "DataprepAsset.h"
#include "DataprepAssetInstance.h"
#include "Parameterization/DataprepParameterization.h"

void AdvancedParameterizedPipeline()
{
    // 1. 获取或创建一个主 Dataprep 资产 (Parent)
    UDataprepAsset* ParentAsset = ...;
    
    // 2. 创建该资产的多个实例，每个实例可以有不同的参数覆盖
    UDataprepAssetInstance* Instance1 = NewObject<UDataprepAssetInstance>();
    Instance1->SetParent(ParentAsset);
    
    // 3. 访问实例的参数化对象，并修改参数值
    UObject* ParamObj = Instance1->GetParameterizationObject();
    // 通过反射或属性句柄找到特定参数并设置新值...
    
    // 4. 使用不同的输入（如不同的源文件）执行实例
    // 为 Instance1 设置新的生产者（输入）
    UDataprepAssetProducers* Producers = Instance1->GetProducers();
    Producers->AddProducerAutomated(UInterchangeFileProducer::StaticClass());
    // 配置新生产者的文件路径...
    
    // 5. 执行该实例
    // FDataprepCoreUtils::ExecuteDataprep(Instance1, Logger, Reporter);
    
    // 对 Instance2 重复步骤 2-5，但使用不同的参数和输入，实现批处理。
}
```

## Demo 示例

以下是一个最小、完整的 C++ 示例，演示如何在编辑器工具或命令行中创建并执行一个 Dataprep 管道。

**DataprepDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FDataprepDemo
{
public:
    /** 创建并执行一个示例 Dataprep 管道 */
    static void RunDemo();
};
```

**DataprepDemo.cpp**
```cpp
#include "DataprepDemo.h"
#include "DataprepAsset.h"
#include "DataprepActionAsset.h"
#include "DataprepContentConsumer.h"
#include "DataprepCoreUtils.h"
#include "DataprepEditorScriptingUtilities.h" // 用于辅助功能
#include "ContentConsumer/DataprepContentConsumer.h" // 基类头文件

// 假设的自定义操作，用于演示
class UDemoPrintOperation : public UDataprepOperation
{
    GENERATED_BODY()
    
    virtual void OnExecution_Implementation(const FDataprepContext& InContext) override
    {
        // 在输出日志中打印处理的资产数量
        UE_LOG(LogTemp, Log, TEXT("DemoPrintOperation executed on %d objects."), InContext.Objects.Num());
        for (UObject* Obj : InContext.Objects)
        {
            UE_LOG(LogTemp, Log, TEXT(" - Processing: %s"), *Obj->GetName());
        }
    }
};

void FDataprepDemo::RunDemo()
{
    // 创建临时的 Dataprep 资产
    UDataprepAsset* DataprepAsset = NewObject<UDataprepAsset>(GetTransientPackage(), TEXT("DemoDataprepAsset"));
    
    // 添加一个动作
    UDataprepActionAsset* Action = DataprepAsset->GetAction(DataprepAsset->AddAction());
    Action->SetLabel(TEXT("Demo Action"));
    
    // 向动作添加一个操作步骤
    Action->AddStep(UDemoPrintOperation::StaticClass());
    
    // 设置一个简单的消费者（这里使用一个模拟的“打印”消费者，实际项目中替换为真实消费者）
    UDataprepContentConsumer* Consumer = DataprepAsset->SetConsumer(UDataprepContentConsumer::StaticClass());
    Consumer->SetTargetContentFolder(TEXT("/Game/DemoOutput"));
    
    // 准备一些要处理的示例对象（这里用 Actor 为例）
    TArray<UObject*> ObjectsToProcess;
    // 在实际环境中，这里应该从世界中收集对象或加载资产
    // ObjectsToProcess.Add(SomeActor);
    
    // 创建日志和进度报告器
    auto Logger = MakeShared<FDataprepCoreUtils::FDataprepLogger>();
    auto Reporter = MakeShared<FDataprepCoreUtils::FDataprepProgressTextReporter>();
    
    // 执行管道
    bool bSuccess = FDataprepCoreUtils::ExecuteDataprep(DataprepAsset, Logger, Reporter);
    
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Dataprep pipeline executed successfully."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Dataprep pipeline execution failed."));
    }
    
    // 清理临时资产 (在实际项目中应妥善管理资产生命周期)
    DataprepAsset->MarkAsGarbage();
}
```

**注意**：此示例需要在 Editor 模块或具有相应权限的模块中运行，且 `UDemoPrintOperation` 需要事先注册。`Build.cs` 中需要依赖 `DataprepCore` 和 `DataprepLibraries` 模块。

## 模块依赖

要使用 Dataprep 功能，你的模块需要依赖以下**独特**的模块：

| 模块 | 用途 |
|---|---|
| `Interchange` | 提供底层的数据交换框架，Dataprep 生产者（如 FBX 导入）依赖此模块 |
| `InterchangeCore` | Interchange 框架的核心模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数导致的编译器警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，统一日志系统 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd | 废弃了带 `bIncludeNestedObjects` 布尔参数的 `GetObjects*` 和 `ForEachObjectWithOuter` 系列函数，引入新API |
| 2026-03-23 | `42dfe52f` | -Consolidate PreviewFeatureLevelChanged and PreviewPlatformChanged into a single PreviewShaderPlatfo | 将预览功能级别和预览平台变更事件整合为单一的预览着色器平台变更事件 |
| 2026-03-05 | `a3b601d8` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_5`. Delete header files that now | 移除受 `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_5` 保护的头文件包含，并删除已废弃的头文件 |

### 维护评价

Dataprep 插件创建于 2019 年，是一个相对成熟的**老古董**级插件。从近期的提交记录来看，该插件**仍处于维护中**，但更新主要是**编译器兼容性修复**（警告消除、日志迁移）和**API 清理**（废弃旧函数），**并未看到新的功能特性或重大性能改进**。这表明 Epic 可能将其视为一个稳定但非活跃开发中的工具。

- **优点**：对于需要标准化资产导入流程的项目（尤其是企业或工业应用）仍然有价值。
- **限制/注意事项**：
    1. **默认未启用**：需要在项目设置中手动启用。
    2. **UI 较为复杂**：对于新手，构建可视化的处理管道有一定学习曲线。
    3. **更新偏维护性**：可能无法快速支持最新的数据格式或 DCC 工具特性。
- **推荐**：如果你的项目有**复杂且重复的资产导入和清理需求**，Dataprep 仍然是一个值得考虑的自动化解决方案。对于简单的导入需求，可能使用引擎自带的导入对话框或简单的 Python/脚本就足够了。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DataprepEditor)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/dataprep-in-unreal-engine/) (注：文档链接来自 .uplugin 信息，此处为假设链接，实际应以 Epic 官方文档为准)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DataprepEditor/Tests)