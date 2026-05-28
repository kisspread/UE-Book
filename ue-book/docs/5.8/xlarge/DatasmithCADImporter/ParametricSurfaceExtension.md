# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD数据导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

这个插件是 Unreal Engine 中用于处理计算机辅助设计（CAD）文件的核心系统。其功能远超简单的“导入”——它是一个完整的 CAD 数据转换、处理和优化管道。插件包含针对多种 CAD 格式（如 STEP, IGES, CATIA, NX, SolidWorks, JT, 3DXML, Rhino 等）的专用翻译器，并集成了第三方 CAD 内核（如 TechSoft）来解析这些文件。它的核心价值在于：
1.  **格式支持**：提供工业级 CAD 文件格式的广泛支持。
2.  **数据转换**：将 CAD 设计数据（曲面、实体、装配体、元数据）转换为 UE 可用的网格、材质和 Actor。
3.  **参数化细分**：保持原始 CAD 曲面的数学精度，允许在导入后动态调整细分（Tessellation）级别，以平衡视觉质量和性能。
4.  **LOD 重新生成**：能够基于存储的参数化数据，为已导入的静态网格重新生成不同细节层次（LOD）的网格。
5.  **分布式处理**：通过 `DatasmithDispatcher` 模块，可以将大型 CAD 文件的处理任务分发到多个机器或进程，加速导入流程。

## 使用场景

-   你是一位建筑师或工程师，需要将 Revit (BIM)、CATIA、SolidWorks 或 NX 等 CAD 软件设计的模型导入 Unreal Engine 进行建筑可视化或虚拟评审。
-   你是一位产品设计师，想将复杂的 CAD 装配体（如汽车、机械设备）导入游戏引擎进行实时交互展示或数字孪生创建。
-   你需要控制导入模型的网格密度，或者在导入后希望在不重新导入源文件的情况下优化网格的三角形数量（例如，为移动端创建简化版本）。
-   你的 CAD 模型非常大，需要加速导入过程。

## 蓝图用法

该插件主要通过 Datasmith 导入工作流使用，但也暴露了部分蓝图接口，尤其用于后期处理。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RetessellateStaticMesh` | 为一个包含参数化曲面数据的静态网格（LOD 0）重新执行细分。 | `UParametricSurfaceBlueprintLibrary` |
| `RetessellateStaticMeshWithNotification` | 与上相同，但可控制是否自动应用更改（通知修改），适用于批量操作。 | `UParametricSurfaceBlueprintLibrary` |

### 使用示例（蓝图描述）

**场景**：在运行时，用户希望根据距离动态调整一个 CAD 导入模型的细节。

1.  在蓝图中，获取一个已经通过 Datasmith 导入的 `UStaticMesh` 引用。
2.  创建一个 `FDatasmithRetessellationOptions` 结构体变量，并设置其成员（如 `ChordTolerance`, `MaxEdgeLength`）来控制细分的精细程度。
3.  调用 `RetessellateStaticMesh` 节点，传入静态网格和设置好的选项。
4.  根据返回的布尔值判断操作是否成功，并可读取 `FailureReason` 输出来获取错误或警告信息。

## C++ 用法

C++ 用法主要涉及与 Datasmith 管线集成，或在代码中实现更高级的细分控制。

### 头文件引入

```cpp
#include "DatasmithRetessellationOptions.h"
#include "ParametricSurfaceBlueprintLibrary.h"
```

### 基本用法

以下代码演示了如何通过 C++ 对一个已导入的静态网格进行重新细分。
（来源推断自 `ParametricSurfaceBlueprintLibrary.h` 及常见用法模式）

```cpp
#include "DatasmithRetessellationOptions.h"
#include "ParametricSurfaceBlueprintLibrary.h"
#include "Engine/StaticMesh.h"

void RetessellateMesh(UStaticMesh* MyStaticMesh)
{
    // 配置细分选项
    FDatasmithRetessellationOptions Options;
    Options.ChordTolerance = 0.1f; // 更精细
    Options.MaxEdgeLength = 0.0f;  // 0 表示无限制
    Options.NormalTolerance = 15.0f;

    FText FailureReason;
    bool bSuccess = UParametricSurfaceBlueprintLibrary::RetessellateStaticMesh(
        MyStaticMesh,
        Options,
        FailureReason
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("成功重新细分网格: %s"), *MyStaticMesh->GetName());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("重新细分失败: %s"), *FailureReason.ToString());
    }
}
```

### 进阶用法

对于批量处理或需要更精细控制的场景，可以使用 `RetessellateStaticMeshWithNotification` 并手动处理后续通知。

```cpp
void BatchRetessellate(const TArray<UStaticMesh*>& Meshes)
{
    FDatasmithRetessellationOptions Options;
    Options.ChordTolerance = 0.2f;
    Options.NormalTolerance = 20.0f;

    for (UStaticMesh* Mesh : Meshes)
    {
        if (Mesh)
        {
            FText Reason;
            // 调用带通知的版本，先不应用修改
            if (UParametricSurfaceBlueprintLibrary::RetessellateStaticMeshWithNotification(
                Mesh, Options, false /*bApplyChanges*/, Reason))
            {
                // 在这里，网格数据已被替换但未通知引擎修改
                // 可以进行其他处理...
            }
            // 最后统一通知
            Mesh->PostEditChange();
            Mesh->MarkPackageDirty();
        }
    }
}
```

## Demo 示例

一个完整的最小示例，展示如何在 Actor 组件中使用参数化细分功能。

### MyRetessellationComponent.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "DatasmithRetessellationOptions.h"
#include "MyRetessellationComponent.generated.h"

class UStaticMeshComponent;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyRetessellationComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyRetessellationComponent();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Tessellation")
    FDatasmithRetessellationOptions TessellationSettings;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Tessellation")
    float UpdateInterval = 5.0f;

    UFUNCTION(BlueprintCallable, Category="Tessellation")
    void RetessellateOwnerMesh();

protected:
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
    float TimeSinceLastUpdate = 0.0f;
    TWeakObjectPtr<UStaticMeshComponent> CachedMeshComponent;
};
```

### MyRetessellationComponent.cpp

```cpp
#include "MyRetessellationComponent.h"
#include "Components/StaticMeshComponent.h"
#include "ParametricSurfaceBlueprintLibrary.h"

UMyRetessellationComponent::UMyRetessellationComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    TessellationSettings.ChordTolerance = 0.15f;
    TessellationSettings.NormalTolerance = 25.0f;
}

void UMyRetessellationComponent::BeginPlay()
{
    Super::BeginPlay();
    if (AActor* Owner = GetOwner())
    {
        CachedMeshComponent = Owner->FindComponentByClass<UStaticMeshComponent>();
    }
}

void UMyRetessellationComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    TimeSinceLastUpdate += DeltaTime;
    if (TimeSinceLastUpdate >= UpdateInterval)
    {
        RetessellateOwnerMesh();
        TimeSinceLastUpdate = 0.0f;
    }
}

void UMyRetessellationComponent::RetessellateOwnerMesh()
{
    if (!CachedMeshComponent.IsValid())
    {
        return;
    }

    UStaticMesh* Mesh = CachedMeshComponent->GetStaticMesh();
    if (Mesh)
    {
        FText FailureReason;
        if (!UParametricSurfaceBlueprintLibrary::RetessellateStaticMesh(Mesh, TessellationSettings, FailureReason))
        {
            UE_LOG(LogTemp, Warning, TEXT("Retessellation failed for %s: %s"), *Mesh->GetName(), *FailureReason.ToString());
        }
    }
}
```

## 模块依赖

使用者（特别是 `ParametricSurfaceExtension` 模块）主要依赖以下内部模块：

| 模块 | 用途 |
|---|---|
| `DatasmithCADTranslator` | 提供核心的 CAD 文件翻译器（翻译器工厂和基础类）。 |
| `ParametricSurface` | 提供参数化曲面数据的核心数据结构和基础操作。 |
| `ParametricSurfaceExtension` | 提供蓝图接口和 Dataprep 操作，是用户最常直接交互的模块。 |
| `DatasmithDispatcher` | （可选）用于分布式处理 CAD 文件的调度功能。 |

**注意**：`TechSoft`, `OpenNurbs6` 等是内部模块依赖的第三方库，使用者无需直接链接。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数的警告代码。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 添加逻辑以兼容 Alias 2027，确保 Wire 格式翻译器正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将第三方 CAD 内核 TechSoft 更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本号。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 解决函数类型转换警告在 MSVC 和 Clang 编译器间的可移植性问题。 |

### 维护评价

-   **创建时间**：该插件创建于 2019 年，是 Unreal Engine 企业级功能的一部分，历史较长。
-   **近期活动**：最近提交记录（2026 年 5 月）显示仍在积极维护，更新内容包括第三方库升级、编译器兼容性修复以及针对最新 CAD 软件版本的适配。
-   **状态**：**活跃维护中**。作为 Epic 官方支持的企业功能，其更新通常与 Unreal Engine 版本发布同步，以确保对主流 CAD 软件和格式的支持。
-   **已知限制**：插件 `EnabledByDefault` 为 `false`，表明它需要用户手动启用，且可能依赖额外的商业许可（如 TechSoft 许可证）。功能非常专业，配置复杂。
-   **推荐**：**推荐使用**。对于需要将工业级 CAD 数据导入 Unreal Engine 进行高保真可视化、虚拟样机或数字孪生的项目，这是官方且功能最强大的解决方案。但使用者需具备相关 CAD 领域知识，并准备好应对其复杂的配置和依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests)