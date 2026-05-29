# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADLibrary` (Runtime), `DatasmithCADTranslator` (Runtime), `ParametricSurface` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约7年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

该插件并非一个简单的单一文件导入器，而是一个**企业级 CAD 数据处理工具集**。其核心目的是将各类专业 CAD（计算机辅助设计）和 BIM（建筑信息模型）软件（如 CATIA、SOLIDWORKS、JT、IGES、STEP、IFC 等）生成的复杂工程模型数据，精确、高效地转换并优化为 Unreal Engine 可用的静态网格体和资产。

它主要解决 CAD 模型导入后面临的关键问题：
1.  **几何精度与拓扑**：CAD 模型使用参数化曲面（如 NURBS），而 UE 使用多边形网格。此插件包含复杂的细分曲面算法，能将高精度曲面转换为可用的多边形网格。
2.  **数据优化与轻量化**：原始 CAD 数据可能包含大量冗余信息。插件通过重新网格化、LOD 生成等功能，在保持视觉精度的同时大幅减少多边形数量，提升运行时性能。
3.  **格式兼容性**：通过一系列“翻译器”模块（如 `DatasmithCADTranslator`、`DatasmithOpenNurbsTranslator`）支持广泛的 CAD 格式。
4.  **后期处理与重拓扑**：如 `ParametricSurfaceExtension` 模块所示，提供了在 UE 内对已导入网格进行重新网格化的能力，允许用户在引擎内调整网格密度和精度。

## 使用场景

-   你正在为工业设计或产品可视化项目导入 SOLIDWORKS 或 CATIA 的装配体文件，并需要保持零部件的精确几何形状。
-   你在进行建筑（AEC）或工程可视化，需要从 Revit、ArchiCAD 或其他 BIM 软件导入模型（IFC 格式），并希望自动优化模型以用于实时渲染。
-   你接收到的客户或供应商数据是通用的 CAD 格式（如 STEP、IGES、JT），需要将其转换为游戏引擎可用的资产。
-   你需要在 Unreal Editor 中对已经导入的、但网格过于密集的 CAD 模型进行**重新网格化**，以降低其复杂度，而不必返回到原 CAD 软件。

## 蓝图用法

### 核心节点

该插件主要提供运行时功能，但 `ParametricSurfaceExtension` 模块暴露了一个关键的蓝图函数库，用于后期处理。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RetessellateStaticMesh` | 对包含参数化曲面数据的静态网格体的 LOD 0 进行重新网格化。返回操作是否成功，并输出失败原因。 | `UParametricSurfaceBlueprintLibrary` |

### 使用示例（蓝图描述）

在蓝图中，你可以获取一个通过 Datasmith 导入的 `UStaticMesh` 资产引用，然后调用 `RetessellateStaticMesh` 节点。
1.  将你的静态网格体变量连接到 `StaticMesh` 输入引脚。
2.  创建一个 `FDatasmithRetessellationOptions` 结构体（包含弦公差、法线公差等参数），并连接到 `TessellationSettings` 输入引脚。
3.  节点的返回值 `bool` 表示成功与否，`FailureReason (FText)` 输出引脚会提供错误详情。
4.  此操作会就地修改目标网格体的几何数据。

## C++ 用法

### 头文件引入

使用重新网格化功能需要包含对应的函数库头文件。
```cpp
#include "ParametricSurfaceBlueprintLibrary.h"
```

### 基本用法

以下代码演示如何从 C++ 调用蓝图函数库中的重新网格化功能。
```cpp
// 假设你已经获得了一个 UStaticMesh* 指针，例如从资产加载或组件获取。
UStaticMesh* MyCADMesh = ...;

// 配置细分曲面参数
FDatasmithRetessellationOptions TessellationOptions;
TessellationOptions.ChordTolerance = 0.5f; // 弦公差（厘米），值越小，网格越密
TessellationOptions.NormalTolerance = 20.f; // 法线公差（度），值越小，曲面越平滑处网格越密

// 执行重新网格化
FText FailureReason;
bool bSuccess = UParametricSurfaceBlueprintLibrary::RetessellateStaticMesh(MyCADMesh, TessellationOptions, FailureReason);

if (!bSuccess)
{
    UE_LOG(LogTemp, Warning, TEXT("CAD Mesh Retessellation Failed: %s"), *FailureReason.ToString());
}
```
*（此用法基于 `Public/ParametricSurfaceBlueprintLibrary.h` 中的函数声明推断）*

## Demo 示例

一个完整的最小示例，展示如何在 Actor 中对组件所使用的静态网格体进行重新网格化。
```cpp
// MyCADActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCADActor.generated.h"

class UStaticMeshComponent;

UCLASS()
class AMyCADActor : public AActor
{
    GENERATED_BODY()

public:
    AMyCADActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere)
    UStaticMeshComponent* MeshComp;

    void RetessellateMyMesh();
};

// MyCADActor.cpp
#include "MyCADActor.h"
#include "Components/StaticMeshComponent.h"
#include "ParametricSurfaceBlueprintLibrary.h"

AMyCADActor::AMyCADActor()
{
    PrimaryActorTick.bCanEverTick = false;
    MeshComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MeshComp"));
    RootComponent = MeshComp;
}

void AMyCADActor::BeginPlay()
{
    Super::BeginPlay();
    RetessellateMyMesh();
}

void AMyCADActor::RetessellateMyMesh()
{
    if (UStaticMesh* Mesh = MeshComp->GetStaticMesh())
    {
        FDatasmithRetessellationOptions Options;
        Options.ChordTolerance = 0.3f;

        FText Reason;
        if (UParametricSurfaceBlueprintLibrary::RetessellateStaticMesh(Mesh, Options, Reason))
        {
            UE_LOG(LogTemp, Log, TEXT("Successfully retessellated mesh: %s"), *Mesh->GetName());
            // 重新网格化后，网格体已更新，渲染将自动反映变化。
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Failed to retessellate mesh %s: %s"), *Mesh->GetName(), *Reason.ToString());
        }
    }
}
```

## 模块依赖

要使用此插件的核心功能（特别是 CAD 文件导入），你的项目或模块可能需要链接到插件暴露的库。对于 `ParametricSurfaceExtension` 模块的功能，通常通过引用插件本身即可。

从模块名称推断，此插件独特且关键的依赖包括：
| 模块 | 用途 |
|---|---|
| `TechSoft` | TechSoft 3D 的 CAD 内核库，用于读取和解析多种 CAD 格式。 |
| `OpenNurbs6` | OpenNurbs 库，用于处理 Rhino 的 .3dm 文件和其他基于 NURBS 的几何数据。 |
| `DatasmithRuntime` | Datasmith 核心运行时库，提供数据导入和转换的基础框架。 |
| `MeshConversion` | 网格体转换工具库，用于处理几何数据在不同表示之间的转换。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量被截断为浮点数导致的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加了逻辑，使 Wire 翻译器在安装了 Alias 2027 的情况下也能工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 库更新到了 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间可移植。 |

### 维护评价

DatasmithCADImporter 是一个**活跃维护中**的企业级插件。
-   **创建时间**：约 7 年前（2019 年），属于 Unreal Engine 中较早出现的 CAD 解决方案之一。
-   **更新频率**：近期（2026 年 5 月）仍有密集提交，内容涵盖**编译兼容性修复、核心依赖库升级（TechSoft）、以及针对特定 CAD 软件（Alias）的兼容性改进**，表明 Epic 团队在持续进行维护和功能适配。
-   **稳定性**：作为运行时插件，其代码变更更注重兼容性和稳定性，而非激进的新功能。
-   **已知限制**：`EnabledByDefault=false`，需要用户手动在项目设置中启用，这暗示了其资源消耗和特定用途的性质。
-   **推荐**：**强烈推荐**给任何需要将专业 CAD 数据引入 Unreal Engine 的工业可视化、数字孪生、AEC 或汽车设计领域的项目。对于纯游戏开发，通常不需要此插件。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests)