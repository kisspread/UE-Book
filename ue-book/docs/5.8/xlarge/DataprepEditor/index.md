# Dataprep Editor

> A tool to simplify creation and execution of data preparation pipelines from within the Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 数据准备编辑器 |
| 分类 | Dataprep |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产） |
| 模块 | `DataprepCore` (Runtime), `DataprepEditor` (Runtime), `DataprepEditorScriptingUtilities` (Runtime), `DataprepLibraries` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-11-22 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DataprepEditor) | |

## 用途

Dataprep Editor 是一个用于**数据预处理**的可视化编辑器插件。它允许用户在 Unreal Editor 内创建、编辑和执行一系列数据准备操作（例如，清理、修复、转换、优化），形成一个可重复使用的“数据准备流水线”。其核心目的是在将外部数据（如 CAD、BIM、FBX 等资产）导入引擎前，进行自动化、规范化的处理，避免重复的手动操作，提高工作流效率和资产质量。

## 使用场景

- **建筑/工程/建筑可视化 (AEC) 工作流**：处理从 Revit、SketchUp、AutoCAD 等软件导入的复杂模型，需要自动化进行几何体清理、材质合并、LOD 生成等操作。
- **工业/制造业数据导入**：处理来自 SolidWorks、CATIA、NX 等 CAD 软件的大型、高精度装配体，需要进行面片修复、单位转换、命名规范整理等。
- **批量资产处理**：需要对大量已导入的资产执行相同的标准化操作，例如统一设置碰撞、物理材质或生成特定的 UV 通道。
- **自定义数据转换流水线**：创建自定义的节点来执行特定的数据转换逻辑，并将其集成到标准的导入流程中。

## 模块概览

| 模块 | 用途简介 |
|---|---|
| `DataprepCore` | 核心库，定义数据准备操作 (`DataprepOperation`)、资产代理 (`DataprepAssetProxy`) 等基础类型和逻辑。 |
| `DataprepEditor` | 编辑器 UI 模块，提供可视化流水线编辑器、操作库浏览器、预览窗口等用户界面。 |
| `DataprepEditorScriptingUtilities` | 蓝图脚本工具库，提供用于通过蓝图控制 Dataprep Editor 和执行操作的函数。 |
| `DataprepLibraries` | 预置操作库，包含一系列内置的数据准备操作，如几何体修改、材质处理、蓝图生成等。 |

## 蓝图用法

通过 `DataprepEditorScriptingUtilities` 模块，可以在蓝图中自动化数据准备流程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateDataprepEditor` | 创建并打开一个 Dataprep 编辑器实例。 | `UDataprepEditorScriptingUtilities` |
| `ExecuteDataprepAsset` | 对指定的 `UDataprepAsset` 执行其定义的全部操作。 | `UDataprepEditorScriptingUtilities` |
| `ExecuteOperation` | 执行单个 `UDataprepOperation` 操作。 | `UDataprepEditorScriptingUtilities` |

### 使用示例（蓝图描述）

1.  在 BeginPlay 事件中，调用 `CreateDataprepEditor` 节点，传入一个 `UDataprepAsset` 资产引用。
2.  该节点返回一个编辑器实例对象。
3.  调用 `ExecuteDataprepAsset` 节点，传入相同的 `UDataprepAsset`，即可触发其预设的处理流程。

## C++ 用法

在 C++ 中，通常需要引用 `DataprepCore` 模块来访问核心类型，并可选地引用 `DataprepEditor` 或 `DataprepLibraries` 来使用编辑器功能或内置操作。

### 头文件引入

```cpp
#include "DataprepAsset.h" // 核心资产
#include "DataprepOperation.h" // 核心操作基类
// 根据需要引入特定操作或编辑器工具
// #include "DataprepEditorModule.h"
// #include "Operations/DataprepStaticMeshOperation.h"
```

### 基本用法

程序化创建和执行一个简单的数据准备流水线。

```cpp
// 假设已有 UDataprepAsset* DataprepAsset
// 获取或创建一个操作实例
UDataprepOperation* MyOperation = NewObject<UMyCustomOperation>(DataprepAsset);
// 配置操作参数...
MyOperation->SetSomeParameter(Value);

// 将操作添加到流水线（假设资产支持此方法）
DataprepAsset->AddOperation(MyOperation);

// 执行整个流水线
FString ErrorMessage;
if (DataprepAsset->Execute(ErrorMessage))
{
    UE_LOG(LogTemp, Log, TEXT("Dataprep pipeline executed successfully."));
}
else
{
    UE_LOG(LogTemp, Error, TEXT("Dataprep pipeline failed: %s"), *ErrorMessage);
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何引用并执行一个已存在的 Dataprep 资产。

**MyActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

class UDataprepAsset;

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

    UPROPERTY(EditAnywhere, Category="Dataprep")
    UDataprepAsset* DataprepAssetToRun;

    UFUNCTION(BlueprintCallable, Category="Dataprep")
    void RunDataPrepPipeline();
};
```

**MyActor.cpp**
```cpp
#include "MyActor.h"
#include "DataprepAsset.h"

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyActor::RunDataPrepPipeline()
{
    if (DataprepAssetToRun)
    {
        FString Error;
        if (DataprepAssetToRun->Execute(Error))
        {
            UE_LOG(LogTemp, Log, TEXT("Pipeline executed successfully."));
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Pipeline execution failed: %s"), *Error);
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No DataprepAsset assigned."));
    }
}
```

## 模块依赖

要使用此插件，你的模块需要在 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `DataprepCore` | 必须，提供数据准备的核心类型和执行逻辑。 |
| `DataprepEditor` | 可选，仅当你需要访问编辑器特有功能（如 UI 工具）时依赖。 |
| `DataprepEditorScriptingUtilities` | 可选，仅当你需要通过蓝图或 C++ 调用编辑器自动化脚本时依赖。 |
| `DataprepLibraries` | 可选，依赖它可以使用所有内置的数据准备操作。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数产生的警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 宏迁移到新的 UE_LOGF 宏。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. | 废弃了接受 `bIncludeNestedObjects` 参数的 `GetObjects*`/`ForEachObjectWithOuter` 函数。 |
| 2026-03-23 | `42dfe52f` | -Consolidate PreviewFeatureLevelChanged and PreviewPlatformChanged into a single PreviewShaderPlatformChanged delegate. | 将预览特性等级和预览平台变更事件合并为单一的预览着色器平台变更委托。 |
| 2026-03-05 | `a3b601d8` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_5`. Delete header files that now | 移除受 `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_5` 宏保护的头文件包含，并删除了现已过时的头文件。 |

### 维护评价

该插件创建于 2019 年，已有约 6 年历史，属于 `Enterprise` 类别的官方插件。从 Git 历史看，**它仍在被 Epic Games 积极维护**，最近一次实质性代码更新在 2026 年 5 月。近期的更新主要集中在**代码现代化**（迁移日志宏、废弃旧接口）和**编译器警告修复**上，这表明其核心功能已相对稳定，维护重点转向了与引擎新版本保持兼容和代码质量。

**综合评价：推荐使用**。作为官方提供的企业级数据导入预处理工具，它在特定领域（如 AEC）是刚需。尽管需要手动启用 (`EnabledByDefault: false`)，但其功能完整，维护状态良好，适合有相关数据处理需求的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DataprepEditor)
- 官方文档 (`.uplugin` 中的 `DocsURL` 为空，请参考引擎内置文档或社区资源)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/DataprepEditor) (可能位于 `Engine/Tests` 目录下)