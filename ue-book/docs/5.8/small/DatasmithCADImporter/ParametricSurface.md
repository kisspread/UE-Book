# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD 工业导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

这是一个工业级 CAD 文件导入插件，解决的核心问题是：**如何将工程 CAD 软件（如 CATIA、NX、SolidWorks、Alias、Rhino、3DExperience 等）创建的参数化曲面模型转换为 Unreal 可渲染的 StaticMesh**。

CAD 模型与游戏引擎模型的根本区别在于：
- CAD 使用 **NURBS 参数化曲面**（精确的数学描述），而 UE 使用 **三角面片网格**（近似的多边形）
- CAD 模型包含复杂的 **拓扑关系**（BRep 边界表示），需要修复才能生成有效网格
- CAD 坐标系、单位、比例因子各不相同，需要统一转换

本插件通过 Tessellation（曲面细分）将参数化几何体转换为三角网格，同时保留材质/图层信息。**注意：必须手动启用**（`EnabledByDefault: false`），因为它是 Enterprise 级功能，需要额外的第三方库（TechSoft、OpenNurbs）支持。

## 使用场景

- 你在做一个建筑可视化项目 → 导入 Revit/ArchiCAD 生成的 CAD 模型到 UE
- 你在做汽车数字展厅 → 导入 CATIA/NX 的汽车零件模型，保留参数化曲面质量
- 你需要对已导入的 CAD 模型重新细分（Retessellate）以调整精度 → 使用 ParametricSurface 模块的重新细分功能
- 你有 Alias/Rhino 的工业设计模型 → 使用 WireInterface 和 OpenNurbs 翻译器导入

## 蓝图用法

本插件主要是运行时翻译器层，不直接暴露蓝图可调用节点。核心交互通过 Datasmith 导入流程完成。

### 核心类

| 类 | 说明 |
|---|---|
| `UDatasmithParametricSurfaceData` | 存储 CAD 参数化曲面的原始数据和细分参数，附加到 StaticMesh 上 |
| `FParametricSurfaceTranslator` | 处理参数化曲面文件的翻译，提供细分选项配置 |
| `ICADModelConverter` | CAD 模型转换器的抽象接口，定义了完整的处理流水线 |

### 使用示例（蓝图描述）

在 Datasmith 导入面板中，当导入 CAD 文件时会自动调用对应的 Translator。如果需要修改细分参数：
1. 导入 CAD 文件后，选中生成的 StaticMesh Asset
2. 在 Details 面板中找到附加的 `Datasmith Parametric Surface Data` 对象
3. 修改 `LastTessellationOptions` 中的 ChordTolerance、MaxEdgeLength 等参数
4. 触发 Retessellate 以使用新参数重新生成网格

## C++ 用法

### 头文件引入

```cpp
#include "ParametricSurfaceModule.h"
#include "ParametricSurfaceTranslator.h"
#include "CADModelConverter.h"
#include "DatasmithParametricSurfaceData.h"
```

### 基本用法

创建一个 ParametricSurface 数据对象并附加到 StaticMesh：

```cpp
#include "ParametricSurfaceModule.h"
#include "DatasmithParametricSurfaceData.h"

// 创建参数化曲面数据
UDatasmithParametricSurfaceData* SurfaceData = FParametricSurfaceModule::CreateParametricSurface();

// 设置源文件
SurfaceData->SetFile(TEXT("C:/Models/engine_block.step"));

// 配置导入参数
CADLibrary::FImportParameters ImportParams;
ImportParams.SetTesselationParameters(
    0.5,    // ChordTolerance (SAG)
    10.0,   // MaxEdgeLength
    15.0,   // NormalTolerance (角度)
    CADLibrary::EStitchingTechnique::StitchingTechnique_Sew
);
SurfaceData->SetImportParameters(ImportParams);
```

*（来源：`Public/DatasmithParametricSurfaceData.h`、`Public/ParametricSurfaceModule.h`）*

### 进阶用法

使用 `ICADModelConverter` 接口完成完整的 CAD 模型转换流水线：

```cpp
#include "CADModelToTechSoftConverterBase.h"
#include "CADLibrary.h"

// 1. 创建转换器实例（由子类 TechSoft 实现）
CADLibrary::FImportParameters ImportParams;
auto Converter = MakeShared<FCADModelToTechSoftConverterBase>(ImportParams);

// 2. 初始化处理环境
Converter->InitializeProcess();

// 3. 设置细分参数
Converter->SetImportParameters(
    0.1,    // ChordTolerance - 越小越精细
    5.0,    // MaxEdgeLength
    10.0,   // NormalTolerance
    CADLibrary::EStitchingTechnique::StitchingTechnique_Sew
);

// 4. 修复拓扑（处理开放边、自相交等问题）
Converter->RepairTopology();

// 5. 保存模型（用于后续重新细分）
FString SavedPath = TEXT("C:/Cache/cad_model.dat");
Converter->SaveModel(*SavedPath, MeshElement);

// 6. 细分（Tessellation）
FMeshDescription MeshDesc;
CADLibrary::FMeshParameters MeshParams;
MeshParams.bNeedSwapOrientation = true;
Converter->Tessellate(MeshParams, MeshDesc);

// 7. 后续可将曲面数据附加到 StaticMesh
FDatasmithMeshElementPayload Payload;
FDatasmithTessellationOptions TessOptions;
Converter->AddSurfaceDataForMesh(*SavedPath, MeshParams, TessOptions, Payload);
```

*（来源：`Public/CADModelConverter.h`、`Public/CADModelToTechSoftConverterBase.h`）*

## Demo 示例

一个完整的 CAD 模型导入器示例：

**MyCADImporter.h**
```cpp
#pragma once

#include "CADModelConverter.h"
#include "ParametricSurfaceTranslator.h"
#include "DatasmithParametricSurfaceData.h"

// 自定义 CAD 翻译器
class FMyCADTranslator : public FParametricSurfaceTranslator
{
public:
    // 初始化细分参数默认值
    virtual void InitCommonTessellationOptions(FDatasmithTessellationOptions& TessOptions) override
    {
        TessOptions.ChordTolerance = 0.1f;
        TessOptions.MaxEdgeLength = 5.0f;
        TessOptions.NormalTolerance = 10.0f;
    }
};

// 自定义模型转换器
class FMyCADModelConverter : public CADLibrary::ICADModelConverter
{
public:
    FMyCADModelConverter(CADLibrary::FImportParameters InParams)
        : ImportParameters(MoveTemp(InParams)) {}

    virtual void InitializeProcess() override;
    virtual bool RepairTopology() override;
    virtual bool SaveModel(const TCHAR* OutputPath, TSharedPtr<IDatasmithMeshElement> MeshElement) override;
    virtual bool Tessellate(const CADLibrary::FMeshParameters& InMeshParameters, FMeshDescription& OutMeshDescription) override;
    virtual void SetImportParameters(double ChordTolerance, double MaxEdgeLength, double NormalTolerance, CADLibrary::EStitchingTechnique StitchingTechnique) override;
    virtual bool AddGeometry(const CADLibrary::FCADModelGeometry& Geometry) override { return false; }
    virtual bool IsSessionValid() override { return true; }
    virtual void AddSurfaceDataForMesh(const TCHAR* InFilePath, const CADLibrary::FMeshParameters& InMeshParameters, const FDatasmithTessellationOptions& InTessellationOptions, FDatasmithMeshElementPayload& OutMeshPayload) const override;

private:
    CADLibrary::FImportParameters ImportParameters;
};
```

**MyCADImporter.cpp**
```cpp
#include "MyCADImporter.h"
#include "ParametricSurfaceModule.h"

void FMyCADModelConverter::InitializeProcess()
{
    // 初始化 TechSoft 或 CADKernel 内核
}

bool FMyCADModelConverter::RepairTopology()
{
    // 修复 BRep 拓扑问题：开放边、退化面等
    return true;
}

bool FMyCADModelConverter::SaveModel(const TCHAR* OutputPath, TSharedPtr<IDatasmithMeshElement> MeshElement)
{
    // 将中间 BRep 模型保存为文件，供后续重新细分
    return true;
}

bool FMyCADModelConverter::Tessellate(const CADLibrary::FMeshParameters& InMeshParameters, FMeshDescription& OutMeshDescription)
{
    // 执行曲面细分，将 NURBS 转为三角网格
    return true;
}

void FMyCADModelConverter::SetImportParameters(double ChordTolerance, double MaxEdgeLength, double NormalTolerance, CADLibrary::EStitchingTechnique StitchingTechnique)
{
    ImportParameters.SetTesselationParameters(ChordTolerance, MaxEdgeLength, NormalTolerance, StitchingTechnique);
}

void FMyCADModelConverter::AddSurfaceDataForMesh(const TCHAR* InFilePath, const CADLibrary::FMeshParameters& InMeshParameters, const FDatasmithTessellationOptions& InTessellationOptions, FDatasmithMeshElementPayload& OutMeshPayload) const
{
    // 将曲面数据关联到 StaticMesh，支持后续重新细分
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TechSoft` | TechSoft 公司的 CAD 内核库，用于解析 CATIA/NX/SolidWorks 等格式 |
| `OpenNurbs6` | 开源 NURBS 库，用于解析 Rhino 的 3DM 文件格式 |
| `DatasmithRuntime` | Datasmith 运行时导入框架 |
| `DatasmithCore` | Datasmith 核心类型定义 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的编译警告 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 兼容 Alias 2027 版本的 Wire 翻译器 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 升级 TechSoft 内核到 2026.3 版本 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新 CAD 缓存格式版本 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复跨编译器（MSVC/Clang）类型转换警告 |

### 维护评价

- **创建时间**：2019 年 10 月，已有约 7 年历史
- **更新频率**：**非常活跃**，最近一次更新在 2026 年 5 月（文档编写时），且持续更新第三方库版本
- **维护状态**：**活跃维护中**，Epic Games 的 Enterprise 团队在持续维护
- **已知限制**：需要手动启用（`EnabledByDefault: false`），依赖 TechSoft 商业库（需要许可证）
- **推荐使用**：✅ 强烈推荐用于工业 CAD 模型导入场景。这是 UE5 中唯一官方支持的 CAD 参数化曲面导入方案，支持格式广泛（CATIA、NX、SolidWorks、Alias、Rhino、3DExperience 等），且持续更新第三方库版本以保持兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)