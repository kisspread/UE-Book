# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD导入工具集 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

该插件是 **Datasmith 管线的核心 CAD 处理组件**。它不仅仅是一个简单的导入器，而是提供了一个完整的、面向工业级 CAD 数据（如 STEP、JT、CATIA、SolidWorks 等）的处理管线。其主要解决以下问题：
1.  **解析与翻译**：将复杂的、参数化的 CAD 模型（包含精确的 B-Rep 曲面和装配结构）转换为 Unreal Engine 可以高效处理的三角形网格和资产数据。
2.  **网格细分与优化**：通过集成 CADKernel 和 TechSoft 等核心库，提供可控的网格细分（Tessellation）参数（如弦高公差、法线角度），并将细分结果缓存以提升后续导入速度。
3.  **几何缝合与修复**：提供缝合（Sew）和修复（Heal）功能，处理 CAD 模型中常见的几何缺陷，如间隙、重叠面等，以生成水密的（Watertight）网格，这对物理碰撞和正确渲染至关重要。
4.  **材质与显示属性管理**：提取和映射 CAD 软件中定义的材质、颜色和图层显示信息到 UE 的材质系统。
5.  **进程外处理**：通过 `DatasmithDispatcher` 模块支持将繁重的 CAD 解析和细分工作分发到独立的外部进程（Worker），避免阻塞编辑器主线程，提升用户体验和稳定性。

## 使用场景

- **建筑设计与工程（AEC）**：你需要将使用 Revit、ArchiCAD 或其他 BIM 软件创建的模型导入到 UE 中进行可视化、虚拟评审或制作交互式体验。
- **产品设计与制造**：你是一名汽车或消费品设计师，需要将 CATIA V5/V6、SolidWorks、Creo (Pro/E) 或 Siemens NX 的复杂装配体导入 UE 进行实时渲染、VR 展示或制作技术文档。
- **数字孪生**：你需要构建物理资产的精确数字副本，这些资产的原始数据通常存在于各种 CAD 和 PLM 系统中。
- **虚拟制片**：你需要将详细的工业设备或车辆模型导入到虚拟场景中，这些模型最初是为工程目的在 CAD 软件中设计的。

**注意**：由于插件 `EnabledByDefault = false`，使用前需要在项目设置中手动启用 `DatasmithCADImporter` 插件。

## 蓝图用法

根据提供的 `CADTools` 模块核心头文件（`CADData.h`, `CADOptions.h`）分析，该模块主要提供底层的 **数据结构和枚举定义**，以及一些核心的序列化/反序列化函数。这些 API 主要面向 C++ 开发，用于构建更上层的导入器和工具。**在公共头文件中未发现 `UFUNCTION(BlueprintCallable)` 标记的函数**，因此其功能主要在引擎底层和编辑器工具中实现，不直接暴露给蓝图。

### 核心节点（概念）

| 节点（概念） | 说明 | 所在类（概念） |
|---|---|---|
| 数据结构 | `FBodyMesh`, `FTessellationData`, `FCADMaterial` 等，用于存储 CAD 模型的几何、拓扑和材质信息。 | `CADLibrary` |
| 文件描述 | `FFileDescriptor`，用于封装 CAD 文件的路径、格式、缓存路径等元数据。 | `CADLibrary` |
| 导入参数 | `FImportParameters`，控制细分质量（弦高、角度）、缝合技术、网格引擎（CADKernel/TechSoft）等。 | `CADLibrary` |
| 序列化工具 | `SerializeBodyMeshSet`, `DeserializeBodyMeshFile`，用于将细分后的网格数据保存到缓存文件或从缓存加载。 | `CADLibrary` |

### 使用示例（蓝图描述）
虽然该模块的核心功能不直接蓝图化，但通过 Datasmith 导入器使用时，你可以在**编辑器导入设置面板**中调整相关的 CAD 导入选项（这些选项背后调用的就是 `FImportParameters` 中定义的参数），从而影响导入结果的质量和性能。

## C++ 用法

该插件的核心逻辑和数据结构通过 `CADTools` 模块提供。

### 头文件引入

```cpp
#include "CADToolsModule.h"
// 包含核心数据结构和类型定义
#include "CADData.h"
// 包含导入参数和选项定义
#include "CADOptions.h"
```

### 基本用法

以下示例展示了如何使用 `CADLibrary` 中定义的基础数据结构和文件描述符。
*代码基于 `Public/CADData.h` 分析。*

```cpp
using namespace CADLibrary;

// 1. 创建一个文件描述符来描述要导入的 CAD 文件
FString CADFilePath = TEXT("D:/Models/Engine.step");
FFileDescriptor FileDesc(*CADFilePath);
// 可以指定一个配置或特定的根目录（如果文件被移动过）
// FFileDescriptor FileDesc(*CADFilePath, TEXT("Default"), TEXT("D:/BackupModels"));

// 检查文件格式
if (FileDesc.GetFileFormat() == ECADFormat::STEP)
{
    UE_LOG(LogTemp, Log, TEXT("这是一个 STEP 文件。"));
}

// 获取用于加载的最终路径（优先使用缓存路径，如果没有则用源文件路径）
const FString& PathToLoad = FileDesc.GetPathOfFileToLoad();

// 2. 理解网格数据结构
// FBodyMesh 表示一个实体的完整网格
FBodyMesh BodyMesh(123); // BodyID 来自 CAD 系统

// 添加一个面（FTessellationData）到实体网格中
FTessellationData FaceData;
FaceData.PositionArray.Add(FVector3f(0, 0, 0));
FaceData.PositionArray.Add(FVector3f(100, 0, 0));
FaceData.PositionArray.Add(FVector3f(0, 100, 0));
FaceData.NormalArray.Add(FVector3f::UpVector);
FaceData.NormalArray.Add(FVector3f::UpVector);
FaceData.NormalArray.Add(FVector3f::UpVector);
FaceData.VertexIndices = {0, 1, 2};
FaceData.PatchId = 0;
BodyMesh.Faces.Add(FaceData);

// 设置该实体使用的材质
FCADMaterial NewMaterial;
NewMaterial.MaterialName = TEXT("Plastic_Blue");
NewMaterial.Diffuse = FColor::Blue;
// 根据材质属性生成一个唯一的材质标识符 (UId)
FMaterialUId MatUId = BuildMaterialUId(NewMaterial);
BodyMesh.MaterialSet.Add(MatUId);

// 3. 序列化/反序列化（用于缓存）
FString CacheFolder = FPaths::ProjectSavedDir() / TEXT("CADCache");
FString CacheFile = CacheFolder / TEXT("MyBodyMesh.bin");
// 保存网格数据到缓存文件
SerializeBodyMeshSet(*CacheFile, {BodyMesh});

// 之后，可以从缓存快速加载，跳过复杂的 CAD 解析和细分过程
TArray<FBodyMesh> LoadedBodies;
DeserializeBodyMeshFile(*CacheFile, LoadedBodies);
```

### 进阶用法

以下示例展示了如何配置导入参数，这些参数通常由更上层的 Datasmith 导入器框架传递给 CAD 处理管线。
*代码基于 `Public/CADOptions.h` 分析。*

```cpp
#include "CADOptions.h"

using namespace CADLibrary;

// 配置 CAD 导入参数
FImportParameters ImportParams;
// 设置细分质量
ImportParams.SetTesselationParameters(
    0.1,   // ChordTolerance: 弦高公差（单位通常与模型一致），值越小网格越精细
    0.0,   // MaxEdgeLength: 最大边长限制，0表示不限制
    15.0,  // MaxNormalAngle: 最大法线角度（度），控制相邻面法线差异
    EStitchingTechnique::StitchingSew // 选择缝合技术
);

// 选择细分网格引擎
ImportParams.SetTesselationParameters(0.1, 0.0, 15.0, EStitchingTechnique::StitchingSew, EMesher::CADKernel);

// 设置坐标系统
ImportParams.SetModelCoordinateSystem(FDatasmithUtils::EModelCoordSystem::ZUp_RightHanded);

// 可以调整一些静态全局设置来影响行为
FImportParameters::bGEnableCADCache = true; // 启用缓存
FImportParameters::bGOverwriteCache = false; // 不覆盖现有缓存
FImportParameters::GStitchingTolerance = 0.01f; // 设置缝合容差

// 获取哈希值，用于判断缓存是否有效
uint32 ParamsHash = ImportParams.GetHash();

// 构建缓存文件路径示例
uint32 FileHash = 0x12345678; // 通常由文件内容计算得出
FString CachePath = FPaths::ProjectSavedDir() / TEXT("CADCache");
FString CadCacheFile = BuildCadCachePath(*CachePath, FileHash);
FString MeshCacheFile = BuildCacheFilePath(*CachePath, TEXT("bodies"), BodyHash, EMesher::CADKernel);

// 序列化参数（通常由分发器用于传递给外部工作者进程）
TArray<uint8> ParamData;
FMemoryWriter Writer(ParamData);
Writer << ImportParams;
// ParamData 现在可以发送给 CADWorker 进程
```

## Demo 示例

一个简单的 C++ 代码示例，展示如何使用 `CADLibrary` 的数据结构和工具函数来模拟一个基本的 CAD 网格处理流程。

**MyCADProcessor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "CADData.h"
#include "CADOptions.h"

class FMyCADProcessor
{
public:
    // 模拟处理一个 CAD 文件并生成网格
    static TArray<CADLibrary::FBodyMesh> ProcessCADFile(const FString& FilePath);
    
    // 使用自定义参数进行处理
    static TArray<CADLibrary::FBodyMesh> ProcessCADFileWithParams(
        const FString& FilePath,
        const CADLibrary::FImportParameters& Params);

private:
    static void GenerateSimpleCubeMesh(CADLibrary::FBodyMesh& OutBodyMesh, const CADLibrary::FColor& Color);
};
```

**MyCADProcessor.cpp**
```cpp
#include "MyCADProcessor.h"
#include "Misc/Paths.h"
#include "HAL/PlatformFilemanager.h"

TArray<CADLibrary::FBodyMesh> FMyCADProcessor::ProcessCADFile(const FString& FilePath)
{
    // 使用默认参数
    CADLibrary::FImportParameters DefaultParams;
    return ProcessCADFileWithParams(FilePath, DefaultParams);
}

TArray<CADLibrary::FBodyMesh> FMyCADProcessor::ProcessCADFileWithParams(
    const FString& FilePath,
    const CADLibrary::FImportParameters& Params)
{
    TArray<CADLibrary::FBodyMesh> ResultMeshes;

    // 1. 创建文件描述符
    CADLibrary::FFileDescriptor FileDesc(*FilePath);

    // 2. 检查文件格式和缓存
    if (FileDesc.GetFileFormat() == CADLibrary::ECADFormat::STEP)
    {
        UE_LOG(LogTemp, Log, TEXT("开始处理 STEP 文件: %s"), *FilePath);

        // 3. 模拟生成网格（实际应调用 CAD 解析和细分库）
        CADLibrary::FBodyMesh BodyMesh(1); // 模拟一个 Body ID
        CADLibrary::FColor Color(0, 128, 255, 255); // 蓝色
        GenerateSimpleCubeMesh(BodyMesh, Color);
        
        // 4. 设置材质
        CADLibrary::FCADMaterial Material;
        Material.MaterialName = TEXT("Generated_Blue_Metal");
        Material.Diffuse = Color;
        Material.Shininess = 0.8f;
        CADLibrary::FMaterialUId MatId = CADLibrary::BuildMaterialUId(Material);
        BodyMesh.MaterialSet.Add(MatId);

        ResultMeshes.Add(BodyMesh);

        // 5. 应用导入参数（示例：调整细分公差，这里仅打印）
        UE_LOG(LogTemp, Log, TEXT("使用细分弦高公差: %f"), Params.GetChordTolerance());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("不支持的 CAD 格式: %s"), *FilePath);
    }

    return ResultMeshes;
}

void FMyCADProcessor::GenerateSimpleCubeMesh(CADLibrary::FBodyMesh& OutBodyMesh, const CADLibrary::FColor& Color)
{
    // 定义一个立方体的顶点和面（简化示例）
    TArray<FVector3f> CubeVertices = {
        FVector3f(-50, -50, -50), FVector3f( 50, -50, -50), FVector3f( 50,  50, -50), FVector3f(-50,  50, -50),
        FVector3f(-50, -50,  50), FVector3f( 50, -50,  50), FVector3f( 50,  50,  50), FVector3f(-50,  50,  50)
    };
    
    // 填充 FBodyMesh 的顶点数组
    OutBodyMesh.VertexArray = CubeVertices;

    // 为立方体的6个面创建 FTessellationData
    for (int32 FaceIndex = 0; FaceIndex < 6; ++FaceIndex)
    {
        CADLibrary::FTessellationData FaceData;
        // 设置面的图层和颜色（简化）
        FaceData.ColorUId = CADLibrary::BuildColorUId(Color);
        
        // 定义面的三角形索引（每个面两个三角形）
        TArray<int32> Indices;
        switch (FaceIndex) {
        case 0: // 底面 (-Z)
            Indices = {0, 2, 1, 0, 3, 2}; break;
        case 1: // 顶面 (+Z)
            Indices = {4, 5, 6, 4, 6, 7}; break;
        case 2: // 前面 (-Y)
            Indices = {0, 1, 5, 0, 5, 4}; break;
        case 3: // 后面 (+Y)
            Indices = {2, 3, 7, 2, 7, 6}; break;
        case 4: // 左面 (-X)
            Indices = {0, 4, 7, 0, 7, 3}; break;
        case 5: // 右面 (+X)
            Indices = {1, 2, 6, 1, 6, 5}; break;
        }

        FaceData.VertexIndices = Indices;
        // 为顶点添加法线（这里简化为每个面统一法线）
        FVector3f FaceNormal = (FaceIndex % 2 == 0) ? FVector3f::DownVector : FVector3f::UpVector;
        if (FaceIndex >= 4) FaceNormal = (FaceIndex == 4) ? FVector3f::LeftVector : FVector3f::RightVector;
        for (int32 i = 0; i < FaceData.VertexIndices.Num(); ++i)
        {
            FaceData.NormalArray.Add(FaceNormal);
            FaceData.TexCoordArray.Add(FVector2f(0, 0)); // 简化 UV
        }

        OutBodyMesh.Faces.Add(FaceData);
    }
    OutBodyMesh.TriangleCount = 12; // 6面 * 2三角形
}
```

## 模块依赖

从各模块的 `Build.cs` 分析，该插件依赖以下**独特**的模块（已过滤掉 Core, CoreUObject, Engine 等通用模块）：

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供对 TechSoft 3D InterOp 库的封装，用于解析多种工业 CAD 格式（如 STEP, JT, CATIA 等）。是 `CADInterfaces` 模块的核心依赖。 |
| `OpenNurbs6` | 提供 OpenNURBS 库的封装，专门用于解析和读取 Rhinoceros 3D (.3dm) 文件格式。是 `DatasmithOpenNurbsTranslator` 模块的核心依赖。 |
| `DatasmithCore` | Datasmith 的核心库，提供基础数据类型、工具函数和框架接口。 |
| `CADKernel` | Unreal Engine 自研的 CAD 几何处理内核，用于进行高精度的曲面细分、网格缝合与修复。是 `CADKernelSurface` 模块的基础。 |
| `DatasmithContent` | 提供 Datasmith 特有的内容资产类型，如 `UDatasmithAssetImportData`。 |
| `MeshConversion` | 提供网格数据格式转换的工具函数。 |
| `MeshDescription` | 定义 `FMeshDescription` 数据结构，是 UE 中表示网格的通用中间格式。 |
| `StaticMeshDescription` | 与 `MeshDescription` 配合，用于构建静态网格资产。 |
| `Json` | 用于解析配置或元数据中的 JSON 数据。 |
| `RHI` | 渲染硬件接口，某些网格数据处理可能需要。 |

**说明**：由于该插件包含多个子模块，具体依赖会随模块不同而变化。以上列表汇总了插件范围内出现的关键、非常见依赖。实际开发中，如果你基于某个特定子模块（如 `CADTools`）进行开发，应检查其对应的 `.Build.cs` 文件以获取精确依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量隐式转换为浮点数导致的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增强了 Wire 格式翻译器的兼容性，使其在安装了 Alias 2027 的环境下也能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 升级了核心的 TechSoft 第三方库到 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 DatasmithCAD 缓存的版本标识，可能意味着缓存格式变更。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复了函数类型转换警告，使其在 MSVC 和 Clang 编译器下表现一致。 |

### 维护评价

**活跃维护**。
该插件创建于 2019 年，虽然已有近 7 年历史（属于“老古董”级别），但**维护状态非常活跃**。从近期提交记录（2026年5月）可以看出：
1.  **持续的兼容性维护**：不断更新以支持最新的 CAD 软件版本（如 Alias 2027）。
2.  **第三方库更新**：核心依赖库 TechSoft 保持更新（2026.3版本）。
3.  **代码质量改进**：修复编译器警告，提升跨平台编译的兼容性。
4.  **功能演进**：缓存版本的更新暗示底层数据处理管线仍在改进。

作为 Unreal Engine 官方 Enterprise 插件的一部分，DatasmithCADImporter 是处理工业 CAD 数据导入的**事实标准**和关键组件。它得到了 Epic Games 的持续投入和支持，**非常推荐在需要将专业 CAD 数据导入 UE 的项目中使用**。需要注意的是，由于它默认禁用且模块众多，在项目配置和首次使用时需要一定的设置工作。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)