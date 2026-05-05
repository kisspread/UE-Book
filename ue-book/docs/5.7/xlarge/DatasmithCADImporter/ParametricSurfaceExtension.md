# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

本插件是 Unreal Engine Datasmith 工作流的核心组成部分，专门用于处理和导入各类 CAD（计算机辅助设计）文件格式。它不仅仅是一个简单的格式转换器，而是一个完整的 CAD 数据处理管线。其核心价值在于能够将复杂的、参数化的 CAD 模型（如来自 CATIA, NX, SolidWorks, STEP, IGES 等格式）转换为适合实时渲染和交互的网格数据，同时尽可能保留原始模型的拓扑结构和元数据。它解决了 CAD 软件与游戏引擎之间在数据格式、精度和性能需求上的巨大鸿沟。

## 使用场景

-   **工业设计与制造可视化**：你需要将汽车、飞机、机械零件等精密 CAD 模型导入 Unreal Engine，用于制作产品展示、装配说明或虚拟培训。
-   **建筑、工程与施工 (AEC)**：你需要导入来自 Revit, ArchiCAD 或其他 BIM 软件的复杂建筑模型，并在引擎中进行实时可视化、碰撞检测或虚拟现实漫游。
-   **CAD 模型优化**：你导入的 CAD 模型在引擎中显示效果不佳（面数过高、破面、法线错误），需要使用本插件提供的工具（如重新网格化）进行优化。
-   **批量资产处理**：你需要对多个已导入的 CAD 资产进行统一的网格质量调整或后处理。

## 蓝图用法

本插件主要通过 `UParametricSurfaceBlueprintLibrary` 和 `UParametricRetessellateAction` 提供蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RetessellateStaticMesh` | 对包含参数化曲面数据的静态网格的 LOD 0 进行重新网格化。 | `UParametricSurfaceBlueprintLibrary` |
| `RetessellateStaticMeshWithNotification` | 与上一节点功能相同，但允许控制是否触发编辑器通知。 | `UParametricSurfaceBlueprintLibrary` |
| `ApplyOnAssets` | 在内容浏览器中右键点击资产时，执行重新网格化操作。 | `UParametricRetessellateAction` |
| `ApplyOnActors` | 在场景中右键点击 Actor 时，执行重新网格化操作。 | `UParametricRetessellateAction` |

### 使用示例（蓝图描述）

1.  **在蓝图中重新网格化单个资产**：
    *   获取一个 `UStaticMesh` 对象的引用（例如，通过资产引用或场景中的组件）。
    *   创建一个 `FDatasmithRetessellationOptions` 结构体变量，并设置所需的网格化参数（如弦高、法线角度等）。
    *   调用 `RetessellateStaticMesh` 节点，将静态网格和选项作为输入。
    *   检查返回的布尔值和 `FailureReason` 文本以确认操作是否成功。

2.  **在编辑器中批量处理资产**：
    *   在内容浏览器中选中一个或多个通过 Datasmith 导入的 CAD 资产。
    *   右键点击，在出现的上下文菜单中找到由 `UParametricRetessellateAction` 注册的“重新网格化”选项。
    *   点击后会弹出一个选项窗口（使用 `UParametricRetessellateActionOptions`），允许你调整网格化参数。
    *   确认后，插件将对所有选中的资产执行重新网格化操作。

## C++ 用法

### 头文件引入

```cpp
#include "ParametricSurfaceBlueprintLibrary.h"
#include "ParametricRetessellateAction.h"
```

### 基本用法

以下代码演示了如何在 C++ 中调用重新网格化功能。

```cpp
// 假设你已经有一个 UStaticMesh* 指针指向一个已导入的 CAD 网格
UStaticMesh* MyCADMesh = ...;

// 设置网格化参数
FDatasmithRetessellationOptions TessellationOptions;
TessellationOptions.ChordTolerance = 0.1f; // 设置弦高公差
TessellationOptions.MaxEdgeLength = 100.0f; // 设置最大边长

// 调用重新网格化函数
FText FailureReason;
bool bSuccess = UParametricSurfaceBlueprintLibrary::RetessellateStaticMesh(MyCADMesh, TessellationOptions, FailureReason);

if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("重新网格化成功。"));
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("重新网格化失败: %s"), *FailureReason.ToString());
}
```

### 进阶用法

在需要精细控制编辑器通知的场景下，可以使用带通知控制的版本。

```cpp
// 在批量处理或自动化脚本中，可能不希望为每个资产都弹出通知
bool bApplyChanges = false; // 暂不应用更改通知
FText FailureReason;

bool bSuccess = UParametricSurfaceBlueprintLibrary::RetessellateStaticMeshWithNotification(
    MyCADMesh,
    TessellationOptions,
    bApplyChanges,
    FailureReason
);

// ... 在所有资产处理完毕后，手动调用编辑器通知或刷新
if (bSuccess)
{
    // 手动触发资产数据更新
    MyCADMesh->PostEditChange();
    MyCADMesh->MarkPackageDirty();
}
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何在 Actor 组件中触发重新网格化。

**MyCADRetessellatorComponent.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyCADRetessellatorComponent.generated.h"

class UStaticMeshComponent;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyCADRetessellatorComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyCADRetessellatorComponent();

    UFUNCTION(BlueprintCallable, Category = "CAD Tools")
    void RetessellateAttachedMesh();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere)
    UStaticMeshComponent* TargetMeshComponent;
};
```

**MyCADRetessellatorComponent.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MyCADRetessellatorComponent.h"
#include "ParametricSurfaceBlueprintLibrary.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"

UMyCADRetessellatorComponent::UMyCADRetessellatorComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyCADRetessellatorComponent::BeginPlay()
{
    Super::BeginPlay();
    // 尝试获取同 Actor 上的第一个 StaticMeshComponent
    TargetMeshComponent = GetOwner()->FindComponentByClass<UStaticMeshComponent>();
}

void UMyCADRetessellatorComponent::RetessellateAttachedMesh()
{
    if (!TargetMeshComponent)
    {
        UE_LOG(LogTemp, Warning, TEXT("未找到目标 StaticMeshComponent。"));
        return;
    }

    UStaticMesh* Mesh = TargetMeshComponent->GetStaticMesh();
    if (!Mesh)
    {
        UE_LOG(LogTemp, Warning, TEXT("StaticMeshComponent 上没有 StaticMesh。"));
        return;
    }

    FDatasmithRetessellationOptions Options;
    Options.ChordTolerance = 0.5f; // 使用一个较大的公差进行快速重网格化

    FText FailureReason;
    if (UParametricSurfaceBlueprintLibrary::RetessellateStaticMesh(Mesh, Options, FailureReason))
    {
        UE_LOG(LogTemp, Log, TEXT("网格 '%s' 重新网格化成功。"), *Mesh->GetName());
        // 可能需要通知组件网格已更新
        TargetMeshComponent->SetStaticMesh(Mesh);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("网格 '%s' 重新网格化失败: %s"), *Mesh->GetName(), *FailureReason.ToString());
    }
}
```

## 模块依赖

本模块 (`ParametricSurfaceExtension`) 的独特依赖如下。使用此插件功能时，你的模块需要链接这些库。

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | 提供 Datasmith 导入框架、资产类型和基础操作接口。 |
| `ParametricSurface` | 提供核心的参数化曲面数据处理和网格化算法。 |
| `DatasmithContent` | 提供 Datasmith 特有的资产类型（如 `UDatasmithStaticMesh`）和选项结构体。 |

## 维护状态

### 近期更新

-   `af690b62c96d` Renamed FMeshConversionContext to FCADMeshConversionContext
    *   *解读：内部重构，重命名了网格转换上下文类，表明代码在持续优化和整理。*
-   `a42d940b5e71` Added retessellation action for meshes imported through Datasmith Interchange from CAD files.
    *   *解读：功能更新，为通过 Datasmith Interchange 导入的 CAD 网格添加了重新网格化操作，扩展了插件的适用范围。*
-   `6a8b1d34f54f` Fix editor crash after retesselation
    *   *解读：重要的 Bug 修复，解决了重新网格化后可能导致编辑器崩溃的问题。*

### 维护评价

**维护中**。该插件创建于 2019 年，属于企业级功能，有较长的历史。从近期的 git 提交记录来看，它仍在被积极维护和更新，包括功能增强（如支持 Interchange 导入的网格）和关键的稳定性修复。作为 Datasmith 工作流的核心组件，它不太可能被废弃。对于需要处理 CAD 数据的项目，这是一个可靠且推荐使用的插件。需要注意的是，它默认未启用（`EnabledByDefault: false`），需要在项目设置中手动开启。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests)