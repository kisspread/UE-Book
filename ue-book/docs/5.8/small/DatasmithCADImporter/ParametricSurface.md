# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith CAD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

Datasmith CAD Importer 是一个企业级插件，其核心功能是**将多种计算机辅助设计（CAD）文件格式（如 Alias、Rhino、OpenNurbs、PLMXML、Wire 格式等）转换并导入到 Unreal Engine 中**。它并非一个简单的格式转换器，而是一个**完整的 CAD 数据处理管线**。

该插件存在的目的是解决工业设计、建筑、汽车制造等领域中，将复杂的 CAD 模型（通常包含精确的参数化曲面/NURBS 数据）高效、准确地转换为游戏引擎可用的三角化网格（Static Mesh）的难题。它通过一系列专用的转换器（Translator）和底层库（如 TechSoft、OpenNurbs6）来实现这一目标，并支持对导入过程进行精细控制，如曲面细分（Tessellation）参数、拓扑修复等。

## 使用场景

- 你需要将汽车公司的 Alias 或 Rhino 模型导入到 Unreal Engine 中进行实时渲染或可视化。
- 你正在使用 Catia、NX、Creo 等 CAD 软件生成 PLMXML 格式的数据，并希望将其集成到 UE 项目中。
- 你的工作流程依赖于 TechSoft 的 ACIS 或 OpenNurbs 等几何内核，需要将基于这些内核的模型导入引擎。
- 你需要对导入的 CAD 模型进行重新曲面细分（Retessellation），以平衡模型精度和性能。
- 你正在开发一个需要处理多种 CAD 数据格式的工业或建筑可视化应用。

## 模块架构概览

本插件由多个相互协作的模块组成，形成一个完整的数据处理流水线。下表概述了各模块的核心职责。

| 模块名 | 类型 | 核心职责 |
|---|---|---|
| `CADInterfaces` | Runtime | 提供与底层 CAD 几何内核（如 TechSoft）交互的接口和抽象层。 |
| `CADLibrary` | Runtime | 提供通用的 CAD 数据模型和工具库，如导入参数 (`FImportParameters`)、网格参数 (`FMeshParameters`) 等。 |
| `CADKernelSurface` | Runtime | (基于分析推测) 可能与 CADKernel 算法库集成，用于处理 NURBS 曲面。 |
| `ParametricSurface` | Runtime | **核心模块之一**。定义了存储和处理参数化曲面数据（NURBS）的资产 (`UDatasmithParametricSurfaceData`) 及转换器基类。 |
| `ParametricSurfaceExtension` | Runtime | (基于分析推测) 可能为 `ParametricSurface` 模块提供扩展功能。 |
| `DatasmithCADTranslator` | Runtime | CAD 文件格式的通用翻译器框架，协调各种专用翻译器。 |
| `DatasmithDispatcher` | Runtime | 负责调度和管理导入/转换任务，可能支持多进程或后台处理。 |
| `DatasmithOpenNurbsTranslator` | Runtime | 专门处理 OpenNurbs (.3dm) 文件格式的翻译器。 |
| `DatasmithPLMXMLTranslator` | Runtime | 专门处理 PLMXML 文件格式的翻译器。 |
| `DatasmithWireTranslator` | Runtime | 专门处理 Wire (Alias) 文件格式的翻译器。 |
| `WireInterface20XX_X` | Runtime | 多个版本的 Wire 格式接口库，确保与不同版本的 Alias 软件兼容。 |
| `CADTools` | Runtime | (基于分析推测) 可能包含 CAD 相关的编辑器工具或辅助功能。 |

## ParametricSurface 模块详解

此模块是处理参数化曲面（主要是 NURBS）数据的核心，负责定义数据结构、接口以及与底层几何内核的交互。

### 核心类与接口

1.  **`UDatasmithParametricSurfaceData`**
    *   **类型**: `UObject` (资产)
    *   **作用**: 一个**数据容器**，用于存储一个网格（Mesh）对应的原始参数化曲面数据（如 NURBS 控制点、权重等）。它继承自 `UDatasmithAdditionalData`，可以作为附加资产挂在 `UStaticMesh` 上。
    *   **关键成员**:
        *   `RawData`: 存储序列化的原始 CAD 曲面数据。
        *   `SceneParameters` (`FParametricSceneParameters`): 存储坐标系、单位、缩放等场景参数。
        *   `MeshParameters` (`FParametricMeshParameters`): 存储与网格生成相关的参数，如是否需要翻转法线、对称信息等。
        *   `LastTessellationOptions` (`FDatasmithTessellationOptions`): 存储上一次曲面细分所用的参数，方便重新细分。
    *   **核心方法**:
        *   `SetFile(const TCHAR* FilePath)`: 从文件加载原始曲面数据。
        *   `SetImportParameters/SetMeshParameters`: 设置导入和网格参数。
        *   `Tessellate(UStaticMesh& StaticMesh, ...)`: **核心功能**，对存储的参数化曲面执行重新细分，生成 `StaticMesh` 的网格数据。

2.  **`ICADModelConverter` (接口)**
    *   **作用**: 定义了将 CAD 模型（一个或多个实体）转换为引擎可识别网格数据的**标准流程接口**。
    *   **核心流程**:
        1.  `InitializeProcess()`: 初始化转换会话。
        2.  `AddGeometry(const FCADModelGeometry& Geometry)`: 向转换器添加一个几何实体。
        3.  `RepairTopology()`: 修复几何体的拓扑错误（如裂缝、重叠面）。
        4.  `SaveModel(...)`: 将修复后的模型保存为中间文件（用于后续重新细分）。
        5.  `Tessellate(...)`: 将当前模型细分，并输出 `FMeshDescription`。
        6.  `AddSurfaceDataForMesh(...)`: 将原始参数化曲面数据与一个已生成的 `StaticMesh` 关联起来。

3.  **`FCADModelToTechSoftConverterBase`**
    *   **作用**: `ICADModelConverter` 接口的一个**基类实现**，专门为 **TechSoft** 几何内核（如 ACIS）提供支持。它封装了与 TechSoft 库交互的通用逻辑。
    *   **职责**: 管理 TechSoft 的会话句柄（`A3DRiRepresentationItem`）、执行拓扑修复、调用 TechSoft 的细分函数。

4.  **`FParametricSurfaceTranslator`**
    *   **作用**: 一个继承自 `IDatasmithTranslator` 的**基类**，为处理包含参数化曲面数据的 CAD 文件提供通用支持。
    *   **核心功能**: 管理通用的曲面细分选项 (`FDatasmithTessellationOptions`)，并提供 `InitCommonTessellationOptions` 虚函数让子类（如特定格式的翻译器）定制这些选项。

5.  **`FParametricSceneParameters` / `FParametricMeshParameters`**
    *   **作用**: 两个简单的 `USTRUCT`，分别用于序列化存储场景级（坐标系、单位）和网格级（法线方向、对称性）的参数。

### 蓝图用法

本模块主要作为底层数据处理和导入管线的一部分，不直接提供高级蓝图节点。其功能通常由 `DatasmithCADTranslator` 等更上层的模块在导入过程中内部调用。

### C++ 用法

#### 头文件引入

```cpp
#include "ParametricSurfaceModule.h"
#include "DatasmithParametricSurfaceData.h"
#include "CADModelConverter.h" // ICADModelConverter 接口
```

#### 基本用法：检查模块状态

```cpp
// 检查 ParametricSurface 模块是否可用并已加载
if (FParametricSurfaceModule::IsAvailable())
{
    UE_LOG(LogTemp, Log, TEXT("ParametricSurface Module is loaded and ready."));
    
    // (高级用法) 创建一个空白的参数化曲面数据资产
    UDatasmithParametricSurfaceData* NewSurfaceData = FParametricSurfaceModule::CreateParametricSurface();
    if (NewSurfaceData)
    {
        // 可以在这里设置数据，或用于自定义导入流程
    }
}
```
*来源：`ParametricSurfaceModule.h`*

#### 进阶用法：实现一个自定义的 CAD 模型转换器

假设你要为一个新的 CAD 格式创建转换器，你可以继承 `ICADModelConverter` 接口（或从 `FCADModelToTechSoftConverterBase` 派生，如果底层使用 TechSoft）。

```cpp
// MyCustomCADConverter.h
#pragma once
#include "CADModelConverter.h"

class FMyCustomCADConverter : public CADLibrary::ICADModelConverter
{
public:
    FMyCustomCADConverter(CADLibrary::FImportParameters InImportParameters);
    
    // 实现 ICADModelConverter 接口
    virtual void InitializeProcess() override;
    virtual bool RepairTopology() override;
    virtual bool SaveModel(const TCHAR* OutputPath, TSharedPtr<IDatasmithMeshElement> MeshElement) override;
    virtual bool Tessellate(const CADLibrary::FMeshParameters& InMeshParameters, FMeshDescription& OutMeshDescription) override;
    virtual void SetImportParameters(double ChordTolerance, double MaxEdgeLength, double NormalTolerance, CADLibrary::EStitchingTechnique StitchingTechnique) override;
    virtual bool AddGeometry(const CADLibrary::FCADModelGeometry& Geometry) override;
    virtual bool IsSessionValid() override;
    virtual void AddSurfaceDataForMesh(const TCHAR* InFilePath, const CADLibrary::FMeshParameters& InMeshParameters, const FDatasmithTessellationOptions& InTessellationOptions, FDatasmithMeshElementPayload& OutMeshPayload) const override;

private:
    CADLibrary::FImportParameters ImportParameters;
    // ... 内部状态，如模型数据库句柄
};

// MyCustomCADConverter.cpp
#include "MyCustomCADConverter.h"
// 包含你的 CAD 格式库头文件

FMyCustomCADConverter::FMyCustomCADConverter(CADLibrary::FImportParameters InImportParameters)
    : ImportParameters(InImportParameters)
{
}

void FMyCustomCADConverter::InitializeProcess()
{
    // 初始化你的 CAD 格式库会话
}

bool FMyCustomCADConverter::Tessellate(const CADLibrary::FMeshParameters& InMeshParameters, FMeshDescription& OutMeshDescription)
{
    // 使用你的 CAD 库和 ImportParameters 中的细分参数（ChordTolerance等）将模型细分
    // 将细分结果（顶点、三角形）填充到 OutMeshDescription 中
    // 返回 true 表示成功
    return true;
}

// ... 其他方法的实现
```
*来源：`CADModelConverter.h` 及对 `FCADModelToTechSoftConverterBase` 的分析*

### Demo 示例

由于本模块主要是数据处理和转换框架，其演示通常体现在**完整的导入流程**中。以下是一个概念性的示例，展示如何在自定义的翻译器中使用 `FParametricSurfaceTranslator`。

```cpp
// MySpecialCADTranslator.h
#pragma once
#include "ParametricSurfaceTranslator.h"

class FMySpecialCADTranslator : public FParametricSurfaceTranslator
{
public:
    // 重写基类方法，提供该格式特有的细分选项默认值
    virtual void InitCommonTessellationOptions(FDatasmithTessellationOptions& TessellationOptions) override
    {
        // 为这种特殊格式调整默认的曲面细分精度
        TessellationOptions.ChordTolerance = 0.1f; // 更高的精度
        TessellationOptions.MaxEdgeLength = 10.0f;
    }
    
    // ... 实现 IDatasmithTranslator 的其他必要方法，如 Translate
};
```

## 模块依赖

以下是从各模块 `Build.cs` 中提取的**关键、非标准依赖**（忽略了 Core, CoreUObject, Engine 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `TechSoft` | 用于访问 TechSoft 的 ACIS 几何内核，进行 CAD 模型的几何运算、拓扑修复和曲面细分。 |
| `OpenNurbs6` | 用于读写 OpenNurbs (.3dm) 文件格式。 |
| `CADLibrary` | 提供跨多个 CAD 模块共享的数据结构（如 `FImportParameters`, `FMeshParameters`）和工具。 |
| `CADInterfaces` | 提供与底层 CAD 库交互的抽象接口，被 `CADLibrary` 和各转换器依赖。 |
| `DatasmithCore` | Datasmith 框架的核心，提供 `IDatasmithTranslator`、`FDatasmithMeshElementPayload` 等基础类型。 |

**注意**：各 `WireInterface` 模块对应不同版本的 Alias Wire 格式支持库，它们是该插件能够兼容多版本 Alias 软件的关键。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数可能产生的警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加逻辑，确保即使安装了 Alias 2027，Wire 翻译器也能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 库更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本格式。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间具有可移植性。 |

### 维护评价

**维护状态：活跃维护中。**

该插件自 2019 年创建以来，持续得到维护和更新。从最近的提交记录可以看出：
1.  **更新频繁**：在 2026 年 5 月仍有密集的提交，修复编译警告、更新依赖库、确保与最新版 CAD 软件（如 Alias 2027）的兼容性。
2.  **核心功能稳定**：更新主要围绕底层依赖（TechSoft, OpenNurbs）的升级、兼容性修复和编译优化，表明核心导入功能已稳定，维护重点是保持与技术生态的同步。
3.  **企业级支持**：作为 Epic 官方的企业版插件，其质量和支持力度有保障。

**建议**：该插件是处理 CAD 数据到 Unreal Engine 的权威解决方案。如果你的工作流涉及工业 CAD 格式，这是必须启用的插件。需要注意它**默认未启用**，且依赖特定的第三方库（TechSoft, OpenNurbs6），这些库的许可证可能需要单独获取（通常随 Unreal Enterprise 订阅提供）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) (通常插件内部包含测试代码)