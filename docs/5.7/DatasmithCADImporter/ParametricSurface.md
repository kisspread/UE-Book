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
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

DatasmithCADImporter 是 Unreal Engine Datasmith 导入框架的核心组成部分，专门用于处理和转换来自各种专业 CAD（计算机辅助设计）软件的文件。它并非一个独立的导入器，而是一个**底层工具集和转换器库**，为上层的 Datasmith 导入器（如用于 Alias、Rhino、CATIA 等的特定格式导入器）提供支持。

其核心功能是将 CAD 软件中定义的**参数化曲面（Parametric Surface）** 和 **边界表示（B-Rep）** 数据，转换为 Unreal Engine 可以使用的三角化网格（Mesh）数据。它处理了 CAD 数据转换中的复杂问题，如拓扑修复、曲面细分（Tessellation）、UV 映射、法线计算以及不同 CAD 软件间的坐标系和单位转换。

**为什么存在？** CAD 模型通常包含精确的数学曲面定义，而非游戏引擎所需的三角面片。直接导入这些原始数据既不现实也无必要。此插件充当了“翻译官”和“工匠”的角色，将精确的 CAD 设计数据“雕刻”成适合实时渲染和交互的 3D 资产。

## 使用场景

- **工业设计与可视化**：你需要将 Alias、Rhino 等工业设计软件创建的汽车、家电等高精度曲面模型导入 Unreal Engine，用于产品可视化、虚拟评审或营销素材制作。
- **建筑与工程（AEC）**：你需要导入来自 CATIA、SolidWorks、NX 等软件的复杂机械部件或建筑信息模型（BIM），用于数字孪生、施工模拟或运维培训。
- **需要高质量曲面**：你希望导入的模型能尽可能保持原始 CAD 设计的曲面平滑度和细节，而非简单的低多边形近似。
- **动态重新曲面化**：你希望在引擎内根据不同的 LOD 需求或交互事件，动态调整导入模型的网格精度（重新曲面化）。

## 蓝图用法

该插件主要作为底层库，其大部分核心功能通过 C++ API 暴露。蓝图中直接可用的节点较少，主要集中在数据管理层面。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set File` | 为参数化曲面数据对象设置源 CAD 文件路径。 | `UDatasmithParametricSurfaceData` |
| `Set Import Parameters` | 设置导入参数，如坐标系、单位、缩放因子。 | `UDatasmithParametricSurfaceData` |
| `Set Mesh Parameters` | 设置网格参数，如是否需要翻转法线、对称信息。 | `UDatasmithParametricSurfaceData` |
| `Set Last Tessellation Options` | 设置上次使用的曲面细分选项，用于后续重新细分。 | `UDatasmithParametricSurfaceData` |
| `Create Parametric Surface` | 静态函数，创建一个新的 `UDatasmithParametricSurfaceData` 对象。 | `FParametricSurfaceModule` |

### 使用示例（蓝图描述）

1.  **创建数据对象**：使用 `FParametricSurfaceModule::CreateParametricSurface` 节点创建一个 `UDatasmithParametricSurfaceData` 对象。
2.  **配置参数**：依次调用 `Set File`、`Set Import Parameters`、`Set Mesh Parameters` 节点，为该对象配置源文件路径和导入/网格参数。
3.  **关联与使用**：此对象通常由 Datasmith 导入流程内部创建和管理，用于存储与特定静态网格体关联的原始 CAD 数据，以支持后续的重新曲面化操作。在蓝图中直接操作它的场景较少，更多是作为导入过程的数据载体。

## C++ 用法

### 头文件引入

```cpp
#include "ParametricSurfaceModule.h"
#include "DatasmithParametricSurfaceData.h"
```

### 基本用法

该模块的核心是创建和管理 `UDatasmithParametricSurfaceData` 对象，它继承自 `UDatasmithAdditionalData`，用于附加到导入的资产上。

```cpp
// 获取模块实例
FParametricSurfaceModule& ParametricSurfaceModule = FParametricSurfaceModule::Get();

// 创建一个新的参数化曲面数据对象
UDatasmithParametricSurfaceData* SurfaceData = ParametricSurfaceModule.CreateParametricSurface();

// 设置源文件（通常由导入器内部调用）
SurfaceData->SetFile(TEXT("C:/Models/CarBody.alias"));

// 设置导入参数（坐标系、单位等）
CADLibrary::FImportParameters ImportParams;
ImportParams.SetCoordinateSystem(FDatasmithUtils::EModelCoordSystem::ZUp_LeftHanded);
ImportParams.SetMetricUnit(0.01f); // 单位：米
ImportParams.SetScaleFactor(1.0f);
SurfaceData->SetImportParameters(ImportParams);

// 设置网格参数（法线翻转、对称等）
CADLibrary::FMeshParameters MeshParams;
MeshParams.bNeedSwapOrientation = false;
MeshParams.bIsSymmetric = true;
MeshParams.SymmetricOrigin = FVector3f::ZeroVector;
MeshParams.SymmetricNormal = FVector3f::UpVector;
SurfaceData->SetMeshParameters(MeshParams);
```

### 进阶用法：实现自定义 CAD 转换器

`ParametricSurface` 模块定义了 `ICADModelConverter` 接口和 `FCADModelToTechSoftConverterBase` 基类。如果你需要支持一种新的 CAD 格式，可以继承这些类。

```cpp
// 假设要为 “MyCAD” 格式创建转换器
class FMyCADModelConverter : public FCADModelToTechSoftConverterBase
{
public:
    FMyCADModelConverter(CADLibrary::FImportParameters InImportParameters)
        : FCADModelToTechSoftConverterBase(InImportParameters)
    {
    }

    // 实现接口方法
    virtual void InitializeProcess() override
    {
        // 初始化 MyCAD 的读取库
    }

    virtual bool AddGeometry(const CADLibrary::FCADModelGeometry& Geometry) override
    {
        // 将 MyCAD 的几何体数据添加到 TechSoft 内核
        // 这里需要调用 TechSoft API (A3DSDKxxx) 将数据转换为 A3DRiRepresentationItem
        return true;
    }

    // RepairTopology, SaveModel, Tessellate 等方法可继承基类实现或重写
};

// 在导入流程中使用
CADLibrary::FImportParameters ImportParams;
FMyCADModelConverter Converter(ImportParams);
Converter.InitializeProcess();

// 假设从文件中解析出了几何数据
CADLibrary::FCADModelGeometry MyGeometry;
Converter.AddGeometry(MyGeometry);

// 修复拓扑
Converter.RepairTopology();

// 保存模型文件（用于后续可能的重新细分）
TSharedPtr<IDatasmithMeshElement> MeshElement = ...; // 从导入上下文获取
Converter.SaveModel(TEXT("/Game/Imported/MyMesh"), MeshElement);

// 细分曲面
FMeshDescription MeshDescription;
CADLibrary::FMeshParameters MeshParams;
Converter.Tessellate(MeshParams, MeshDescription);

// 将 MeshDescription 应用到 UStaticMesh...
```

## Demo 示例

以下示例展示了如何在 C++ 中创建一个 `UDatasmithParametricSurfaceData` 对象并配置其参数。这模拟了 Datasmith 导入器内部的部分工作流程。

**MyParametricSurfaceUser.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

class UDatasmithParametricSurfaceData;

class FMyParametricSurfaceUser
{
public:
    void SetupParametricSurfaceData();
    
private:
    UPROPERTY()
    TObjectPtr<UDatasmithParametricSurfaceData> SurfaceDataObject;
};
```

**MyParametricSurfaceUser.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MyParametricSurfaceUser.h"
#include "ParametricSurfaceModule.h"
#include "DatasmithParametricSurfaceData.h"
#include "CADOptions.h" // For CADLibrary::FImportParameters, FMeshParameters

void FMyParametricSurfaceUser::SetupParametricSurfaceData()
{
    // 1. 确保模块可用
    if (!FParametricSurfaceModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("ParametricSurface module is not available."));
        return;
    }

    // 2. 创建数据对象
    SurfaceDataObject = FParametricSurfaceModule::Get().CreateParametricSurface();
    if (!SurfaceDataObject)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create ParametricSurfaceData object."));
        return;
    }

    // 3. 设置源文件（示例路径）
    const FString FilePath = FPaths::ProjectContentDir() + TEXT("ImportedModels/EngineBlock.step");
    SurfaceDataObject->SetFile(*FilePath);

    // 4. 配置导入参数
    CADLibrary::FImportParameters ImportParams;
    ImportParams.SetCoordinateSystem(FDatasmithUtils::EModelCoordSystem::YUp_RightHanded);
    ImportParams.SetMetricUnit(0.001f); // 毫米
    ImportParams.SetScaleFactor(100.0f); // 放大100倍
    SurfaceDataObject->SetImportParameters(ImportParams);

    // 5. 配置网格参数
    CADLibrary::FMeshParameters MeshParams;
    MeshParams.bNeedSwapOrientation = true; // 根据模型需要翻转法线
    MeshParams.bIsSymmetric = false;
    SurfaceDataObject->SetMeshParameters(MeshParams);

    // 6. 设置初始细分选项
    FDatasmithTessellationOptions TessOptions;
    TessOptions.ChordTolerance = 0.1f;
    TessOptions.MaxEdgeLength = 10.0f;
    TessOptions.NormalTolerance = 10.0f;
    SurfaceDataObject->SetLastTessellationOptions(TessOptions);

    UE_LOG(LogTemp, Log, TEXT("ParametricSurfaceData object configured for: %s"), *FilePath);
}
```

## 模块依赖

`ParametricSurface` 模块本身依赖较少，但作为 DatasmithCADImporter 的一部分，整个插件依赖于以下关键模块：

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | Datasmith 核心框架，提供场景元素、翻译器接口等。 |
| `CADLibrary` | 提供 CAD 导入的通用工具类、参数结构体（如 `FImportParameters`）。 |
| `TechSoft` | Tech Soft 3D 的 HOOPS Exchange SDK 封装，用于读取和转换多种 CAD 格式。 |
| `CADKernel` | Epic 的内部 CAD 内核，用于拓扑修复和曲面细分。 |
| `MeshDescription` | 用于构建和操作网格数据。 |

## 维护状态

### 近期更新

```
- 4af2fd066dd0 Updating Dev-Release-5.5 from Main at CL #36144969
- af690b62c96d Renamed FMeshConversionContext to FCADMeshConversionContext
- a42d940b5e71 Added retessellation action for meshes imported through Datasmith Interchange from CAD files.
```

- `4af2fd066dd0`: 分支同步更新，无实质性功能改动。
- `af690b62c96d`: 代码重构，将 `FMeshConversionContext` 重命名为 `FCADMeshConversionContext`，提高了代码清晰度。
- `a42d940b5e71`: **重要功能更新**，为通过 Datasmith Interchange 导入的 CAD 网格添加了重新曲面化（Retessellation）操作支持，增强了工作流的灵活性。

### 维护评价

- **年龄**：插件创建于 2019 年，已有约 5 年历史，属于成熟的企业级功能。
- **活跃度**：近期（2025年）仍有功能性更新（如重新曲面化支持）和代码重构，表明该插件处于**活跃维护**状态。
- **稳定性**：作为 Epic 官方维护的企业功能，其稳定性和兼容性有保障。
- **推荐度**：**强烈推荐**。对于需要处理专业 CAD 数据的项目，这是官方提供的标准且强大的解决方案。虽然默认未启用，但一旦启用，它是连接 CAD 设计与 UE 实时引擎的可靠桥梁。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests) (如果存在)