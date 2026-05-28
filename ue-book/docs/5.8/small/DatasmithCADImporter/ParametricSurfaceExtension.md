# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

本插件是Datasmith框架的一部分，专门用于处理和导入各类CAD（计算机辅助设计）文件格式。它不仅仅是简单的格式转换，而是一个完整的CAD数据处理工具集。其主要解决以下问题：

1.  **格式支持**：提供对众多主流CAD软件格式的翻译和解析能力，包括但不限于 CATIA, SOLIDWORKS, NX, STEP, IGES, JT, 3DXML 等。通过不同的 `WireInterface` 模块支持不同年份版本的CAD软件。
2.  **数据转换与优化**：将CAD软件的精确几何体（如NURBS曲面、参数化表面）转换为适用于实时渲染引擎（UE）的三角网格（多边形）。这个过程称为“曲面细分”（Tessellation），插件提供了精细的控制参数来平衡精度与性能。
3.  **拓扑保持**：在转换过程中，努力保持原始CAD模型的结构树、层级和材质信息，便于在UE中进行进一步的处理和组装。
4.  **后处理集成**：提供蓝图和编辑器操作，允许在导入后或在工作流中对网格进行重新曲面化，以适应不同的LOD（细节层次）或性能需求。

## 使用场景

-   **建筑、工程和施工**：导入来自Revit, CATIA, NX等软件的复杂BIM模型或机械零件，用于建筑可视化、虚拟样机评审。
-   **制造业与产品设计**：将SOLIDWORKS, SolidEdge等设计的精密零件和装配体导入UE，用于创建交互式产品配置器或培训模拟。
-   **汽车与运输**：导入高精度的汽车A级曲面（A-Surface）或工程部件进行虚拟展示、风洞模拟可视化。
-   **优化现有资产**：当你在UE中已有一个由CAD导入的静态网格，但希望调整其多边形数量或拓扑结构以适应移动端或VR性能要求时，可以使用此插件的重新曲面化功能。

## 蓝图用法

蓝图功能主要由 `ParametricSurfaceExtension` 模块提供。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RetessellateStaticMesh` | 对包含参数化曲面数据的静态网格（LOD 0）进行重新曲面化，并自动处理编辑器通知。 | `UParametricSurfaceBlueprintLibrary` |
| `RetessellateStaticMeshWithNotification` | 同上，但可选择是否自动应用编辑器更改通知，允许调用者控制后处理流程。 | `UParametricSurfaceBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **基本重新曲面化**：
    *   在蓝图中，获取一个已导入的 `UStaticMesh` 资产引用（例如，通过 `Get Static Mesh Asset` 节点）。
    *   创建一个 `FDatasmithRetessellationOptions` 结构体变量，并设置所需的参数（如 `ChordTolerance`, `MaxEdgeLength`, `NormalTolerance`）。
    *   调用 `RetessellateStaticMesh` 节点，将静态网格和选项结构体作为输入。
    *   检查返回的 `Bool` 值以判断是否成功，并使用 `FailureReason` 输出获取失败详情或警告信息。

2.  **批量处理（在编辑器工具中）**：
    *   在编写编辑器工具或编辑器工具蓝图时，可以使用 `RetessellateStaticMeshWithNotification` 节点。
    *   将 `bApplyChanges` 参数设为 `false`，以避免为每个网格触发单独的编辑器重绘，从而提高批量处理效率。
    *   在循环处理完所有网格后，手动调用编辑器刷新函数来一次性应用所有更改。

## C++ 用法

### 头文件引入

```cpp
#include "ParametricSurfaceExtension/ParametricSurfaceBlueprintLibrary.h"
```

### 基本用法

在C++代码中，可以直接调用蓝图库中的静态函数。
```cpp
// 假设你已经有了一个指向 UStaticMesh 的指针 MyStaticMeshPtr
UStaticMesh* MyStaticMeshPtr = /* ... */;

// 配置重新曲面化选项
FDatasmithRetessellationOptions Options;
Options.ChordTolerance = 0.5f; // 设置更大的容差以减少多边形数
Options.MaxEdgeLength = 0.0f;  // 0 表示不限制
Options.NormalTolerance = 15.0f;

// 执行重新曲面化
FText FailureReason;
bool bSuccess = UParametricSurfaceBlueprintLibrary::RetessellateStaticMesh(MyStaticMeshPtr, Options, FailureReason);

if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Successfully retessellated mesh: %s"), *MyStaticMeshPtr->GetName());
}
else
{
    UE_LOG(LogTemp, Error, TEXT("Failed to retessellate mesh: %s, Reason: %s"), *MyStaticMeshPtr->GetName(), *FailureReason.ToString());
}
```
*(代码逻辑基于 `ParametricSurfaceBlueprintLibrary.h` 中的函数签名推断)*

### 进阶用法

在批量处理工具中，可能需要更精细的控制，以避免编辑器UI卡顿。
```cpp
// 批量处理一个静态网格数组
TArray<UStaticMesh*> MeshesToProcess = /* ... */;

FDatasmithRetessellationOptions Options;
// ... 配置 Options ...

FText OverallWarning;
for (UStaticMesh* Mesh : MeshesToProcess)
{
    FText Reason;
    // 使用“带通知”版本，并明确指定不应用编辑器更改
    bool bOk = UParametricSurfaceBlueprintLibrary::RetessellateStaticMeshWithNotification(
        Mesh,
        Options,
        false, // bApplyChanges = false， 延迟编辑器更新
        Reason
    );

    if (!bOk)
    {
        UE_LOG(LogTemp, Warning, TEXT("Mesh '%s': %s"), *Mesh->GetName(), *Reason.ToString());
    }
    else if (!Reason.IsEmpty())
    {
        // 收集警告信息
        OverallWarning = FText::Format(NSLOCTEXT("MyTool", "BatchWarn", "{0}\n{1}"), OverallWarning, Reason);
    }
}

// 批量处理完成后，刷新编辑器以显示所有更改
if (GEditor)
{
    // 假设你正在编辑器上下文中运行
    FEditorSupportTools::RequestAssetRefresh();
    // 或者更直接的：GEditor->RedrawLevelEditingViewports();
}
```

## Demo 示例

以下示例展示了一个简单的编辑器命令，用于对当前选中的第一个静态网格资产进行重新曲面化。

**MyRetessellateCommand.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class FMyRetessellateCommand
{
public:
    static void Execute();
};
```

**MyRetessellateCommand.cpp**
```cpp
#include "MyRetessellateCommand.h"
#include "ParametricSurfaceExtension/ParametricSurfaceBlueprintLibrary.h"
#include "Engine/StaticMesh.h"
#include "AssetRegistry/AssetData.h"
#include "Editor.h"

void FMyRetessellateCommand::Execute()
{
    // 获取内容浏览器中选中的资产
    TArray<FAssetData> SelectedAssets;
    GEditor->GetContentBrowserSelections(SelectedAssets);

    for (const FAssetData& AssetData : SelectedAssets)
    {
        if (AssetData.GetClass() == UStaticMesh::StaticClass())
        {
            UStaticMesh* StaticMesh = Cast<UStaticMesh>(AssetData.GetAsset());
            if (StaticMesh)
            {
                FDatasmithRetessellationOptions Options;
                Options.ChordTolerance = 0.3f; // 一个中等精度的默认值

                FText FailureReason;
                if (UParametricSurfaceBlueprintLibrary::RetessellateStaticMesh(StaticMesh, Options, FailureReason))
                {
                    UE_LOG(LogTemp, Display, TEXT("Retessellated '%s' successfully."), *StaticMesh->GetName());
                }
                else
                {
                    UE_LOG(LogTemp, Error, TEXT("Failed to retessellate '%s': %s"), *StaticMesh->GetName(), *FailureReason.ToString());
                }
                // 本示例仅处理第一个找到的静态网格
                break;
            }
        }
    }
}
```
*(这是一个概念性示例，展示了如何集成该插件的功能。实际注册为编辑器命令需要额外的代码。)*

## 模块依赖

使用者需要在其模块的 `.Build.cs` 文件中添加以下依赖。注意，大部分依赖是运行时 `CADLibrary` 的传递性依赖，使用者通常只需直接依赖 `DatasmithRuntime`。

| 模块 | 用途 |
|---|---|
| `DatasmithRuntime` | 核心的Datasmith导入和运行时功能，是使用本插件功能的主要入口点。 |
| `TechSoft` | 被 `CADInterfaces` 模块依赖，用于支持特定的CAD格式（如CATIA, NX, SOLIDWORKS等）。 |
| `OpenNurbs6` | 被 `DatasmithOpenNurbsTranslator` 依赖，用于解析Rhino (.3dm) 等使用OpenNURBS格式的文件。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数时产生的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增强了Wire翻译器的兼容性，使其即使在安装了Alias 2027的环境中也能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 更新了TechSoft库至2026.3版本，可能带来新的格式支持或稳定性改进。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了DatasmithCAD缓存版本，可能涉及缓存格式变更或性能优化。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在MSVC和Clang编译器之间更具可移植性，属于代码健壮性改进。 |

### 维护评价

本插件处于 **积极维护** 状态。
*   **活跃度**：最近的提交记录（2026年5月）显示，开发团队仍在持续进行改进和错误修复。
*   **更新内容**：近期更新主要集中在**编译器警告修复、第三方库版本升级（TechSoft）、以及提升与最新CAD软件（如Alias 2027）的兼容性**。这些更新表明插件在追求稳定性和兼容性。
*   **推荐使用**：作为Unreal Engine企业版功能的一部分，且持续得到更新，对于需要处理CAD数据的项目（特别是建筑、工程、制造领域），**推荐使用**。但需注意该插件默认未启用，需要手动在插件管理器中激活。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)