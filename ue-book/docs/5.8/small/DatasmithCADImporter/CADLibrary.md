# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

该插件是 Unreal Engine Datasmith 生态系统的一部分，核心功能是将各类 CAD（计算机辅助设计）文件格式转换为 UE 内部可渲染的网格数据（`FMeshDescription`）。它不仅仅是一个简单的格式转换器，更是一套处理 CAD 模型拓扑、几何精度、材质映射及网格修复的完整工具链。

**它解决的问题**：工业设计软件（如 SolidWorks， CATIA）和建筑信息模型（BIM）软件生成的模型具有高精度的参数化曲面（NURBS）和复杂的拓扑结构，直接导入 UE 会丢失精度或产生破损的网格。本插件通过一系列算法（如曲面细分、拓扑修复、法线修正）将 CAD 数据“翻译”成适合实时渲染的三角面片模型。

## 使用场景

- **建筑可视化**：将来自 Revit， ArchiCAD 或其他 BIM 软件的建筑模型导入 Unreal Engine，用于制作建筑漫游动画或 VR 体验。
- **工业仿真与培训**：将工厂设备、汽车零件等高精度 CAD 模型导入 UE，构建数字孪生或操作培训应用。
- **产品设计预览**：设计师可以直接在 UE 中查看和交互由 CAD 软件创建的产品原型，进行实时渲染和评审。

## 蓝图用法

本插件的核心转换功能主要在 C++ 层实现，用于集成到 Datasmith 导入流水线中。在 `Public/` 头文件中，未发现直接标记为 `BlueprintCallable` 的工具函数。其主要使用方式是作为 Datasmith 文件导入过程中的一个内部翻译器模块。

## C++ 用法

该插件主要提供 C++ API，供引擎内部的导入器或高级插件开发者调用。以下示例基于提供的 `CADLibrary` 模块源码。

### 头文件引入

```cpp
// 引入 CAD 库工具类
#include "CADKernelTools.h"
#include "CADMeshDescriptionHelper.h"
```

### 基本用法

以下示例展示了如何使用 `FCADKernelTools` 对一个 CAD 实体进行细分，并将结果写入 `FMeshDescription`。

```cpp
// 来源: Public/CADKernelTools.h
// 假设已有一个来自 CADKernel 库的拓扑形状实体 `CADEntity`
// 以及导入参数 `ImportParams` 和网格参数 `MeshParams`

#include "CADKernelTools.h"

// 创建网格转换上下文
CADLibrary::FMeshConversionContext ConversionContext(ImportParams, MeshParams);

// 准备输出的 MeshDescription
FMeshDescription& MeshDescription = /* ... */;

// 调用细分函数
bool bSuccess = CADLibrary::FCADKernelTools::Tessellate(*CADEntity, ConversionContext, MeshDescription);

if (bSuccess)
{
    // 细分成功， MeshDescription 中已包含转换后的网格数据
}
```

### 进阶用法

在将 CAD 模型转换为 `FMeshDescription` 后，通常需要为其应用材质。`CADLibrary` 命名空间提供了辅助函数。

```cpp
// 来源: Public/CADMeshDescriptionHelper.h

#include "CADMeshDescriptionHelper.h"

// 1. 从 CAD 材质创建 UE PBR 材质元素
TSharedPtr<IDatasmithUEPbrMaterialElement> UEMaterial =
    CADLibrary::CreateUEPbrMaterialFromMaterial(InCADMaterial, DatasmithScene);

// 2. 在 MeshDescription 中启用 CAD 面片分组（PolyTriGroup）属性，
//    这允许将多个三角形组合成一个逻辑面（CAD拓扑面），便于材质分配。
TPolygonAttributesRef<int32> PatchGroupAttr =
    CADLibrary::EnableCADPatchGroups(MeshDescription);

// 3. 之后，可以遍历多边形并根据其 PatchGroupID 设置对应的材质槽名。
```

## Demo 示例

以下是一个最小的、可编译的 C++ 示例，演示了如何调用核心转换流程。注意，此代码依赖于完整的 Datasmith CAD 导入环境（如 `CADKernel` 库已初始化）。

```cpp
// MyCADProcessor.h
#pragma once

#include "CoreMinimal.h"
#include "CADKernelTools.h"
#include "CADMeshDescriptionHelper.h"

namespace CADKernel { class FTopologicalShapeEntity; }

class FMyCADProcessor
{
public:
    static bool ProcessCADEntity(UE::CADKernel::FTopologicalShapeEntity& CADEntity,
                                 const CADLibrary::FImportParameters& ImportParams,
                                 const CADLibrary::FMeshParameters& MeshParams,
                                 FMeshDescription& OutMesh)
    {
        // 1. 创建转换上下文
        CADLibrary::FMeshConversionContext Context(ImportParams, MeshParams);

        // 2. 调用 Tessellate 进行几何转换
        return CADLibrary::FCADKernelTools::Tessellate(CADEntity, Context, OutMesh);
    }
};
```

```cpp
// MyCADProcessor.cpp
#include "MyCADProcessor.h"
// 确保链接了 CADLibrary 模块 (在你的模块 Build.cs 中)
```

## 模块依赖

要使用此插件的功能（特别是 `CADLibrary`），你的模块需要链接以下依赖：

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供与 TechSoft 3D 模型库的接口，用于读取和解析多种 CAD 文件格式（如 STEP， IGES）。 |
| `OpenNurbs6` | 用于处理 Rhino 的 3DM 文件格式，特别是 NURBS 曲面数据。 |

*注：`Core`, `CoreUObject`, `Engine` 等标准依赖已省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量隐式转换为浮点数导致的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 新增兼容逻辑，确保即使安装了 Alias 2027， Wire 格式转换器也能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将核心依赖库 TechSoft 更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 DatasmithCAD 缓存的版本号。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间更具可移植性。 |

### 维护评价

该插件是 Unreal Engine 企业版功能的重要组成部分，**处于活跃维护状态**。
- **活跃维护**：最近一次实质性更新（TechSoft 升级、兼容性修复）就在几天前（2026-05-13），表明 Epic Games 持续投入资源维护其与最新 CAD 软件版本和编译器的兼容性。
- **重要性**：作为 Datasmith 用于工业 CAD 数据导入的关键后端，其稳定性与性能对相关行业用户至关重要。
- **推荐使用**：如果你的项目需要从 CAD 软件（特别是支持 STEP/IGES 格式）导入高精度模型，并且已购买/获得了 Unreal Engine 的企业版授权，那么这是官方推荐的、经过验证的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests) (基于插件结构推测)