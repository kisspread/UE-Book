# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith CAD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `CADInterfaces` (Runtime), `CADLibrary` (Runtime), `DatasmithDispatcher` (Runtime), `ParametricSurface` (Runtime), `WireInterface2026_0` (Runtime) 等共 21 个模块 |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

该插件是 UE5 Datasmith 生态系统中的核心 CAD 导入引擎。它并非直接提供简单的文件导入功能，而是一套完整的 **CAD 文件处理与转换框架**。其主要目标是解决将复杂的工业 CAD 模型（来自 CATIA, SolidWorks, JT, STEP 等数十种格式）高效、准确地转换为 UE 可用的网格、材质和场景层次结构的问题。

**核心功能包括**：
1.  **格式解析**：为众多 CAD 格式提供专门的翻译器（Translator）。
2.  **几何处理**：通过 `CADKernel` 或 `TechSoft` 等后端对 CAD 几何体进行曲面细分（Tessellation），将其转换为三角形网格。
3.  **数据管理**：定义了一套通用的中间数据结构（如 `FBodyMesh`, `FTessellationData`），用于在不同 CAD 格式和最终的 UE 资产之间传递数据。
4.  **缓存系统**：支持对导入过程的结果进行缓存，避免重复计算，加速后续导入。
5.  **多进程分发**：通过 `DatasmithDispatcher` 模块，可以将 CAD 处理任务分发到独立的子进程（CADWorker）中执行，提高稳定性和资源利用率。
6.  **集成 Datasmith**：作为 Datasmith 导入流程的一部分，将处理后的数据无缝集成到 Datasmith 场景和资产中。

简单来说，**你不需要直接使用此插件，而是通过 Datasmith 导入 `.udatasmith` 文件或 `.dwg` 等格式文件时，在后台自动调用它来完成核心的 CAD 到网格的转换工作。**

## 使用场景

-   **工业设计可视化**：您使用 CATIA, Siemens NX, SolidWorks 或 Creo 等软件设计了复杂的机械产品，希望将其导入 UE5 进行实时渲染、产品配置或虚拟展示。
-   **建筑信息模型（BIM）**：您有从 Revit, ArchiCAD 或通过 DWG/DGN 格式导出的建筑模型，需要将其带入 UE5 创建建筑可视化、数字孪生或施工模拟。
-   **CAE 仿真可视化**：您需要将来自 ANSYS, ABAQUS 或其他 CAD 系统的复杂几何模型导入 UE，用于仿真结果的后处理展示。
-   **需要高保真转换**：标准 FBX/OBJ 导入器无法满足您对 CAD 模型拓扑、材质和装配体结构保持原样的需求。

## 蓝图用法

此插件主要作为底层服务被 Datasmith 和引擎的文件导入管线调用，**不提供面向设计师的直接蓝图节点**。其核心类和函数均为 C++ 接口，供其他模块（如 `DatasmithCore`， `DatasmithImporter`）调用。

### 核心节点（C++ API 概览）

以下函数虽标记为 `CADTOOLS_API`，但通常不直接在游戏逻辑蓝图中使用：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCleanFilenameAndExtension` | 从完整路径中获取清理后的文件名和扩展名 | `CADLibrary` (全局函数) |
| `GetExtension` | 获取文件路径的扩展名 | `CADLibrary` (全局函数) |
| `BuildColorUId` | 根据 `FColor` 创建一个唯一的材质/颜色标识符 | `CADLibrary` (全局函数) |
| `BuildMaterialUId` | 根据 `FCADMaterial` 结构创建一个唯一的材质标识符 | `CADLibrary` (全局函数) |
| `SerializeBodyMeshSet` | 将一组 `FBodyMesh` 序列化到文件 | `CADLibrary` (全局函数) |
| `DeserializeBodyMeshFile` | 从文件反序列化一组 `FBodyMesh` | `CADLibrary` (全局函数) |

**使用示例（蓝图描述）**
在蓝图中，你更可能通过“文件导入”或“Datasmith 导入”节点间接触发此插件的功能。直接调用上述 C++ 函数需要创建 C++ 类或在插件中扩展蓝图库，这非常罕见。

## C++ 用法

此插件的 C++ 用法主要面向需要扩展 CAD 格式支持或自定义导入流程的开发者。以下是基于核心头文件 `CADData.h` 的典型用法示例。

### 头文件引入

```cpp
#include "CADTools/CADData.h"
#include "CADTools/CADOptions.h"
```

### 基本用法

1.  **描述一个 CAD 文件**：使用 `FFileDescriptor` 来管理 CAD 文件的路径、格式和缓存。

```cpp
// (来源：根据 CADData.h 中 FFileDescriptor 类设计的示例)
using namespace CADLibrary;

// 描述一个要导入的 SolidWorks 文件
FFileDescriptor SWFileDescriptor(
    TEXT("D:/Models/Engine.sldprt"), // 源文件路径
    TEXT("Default"),                 // 配置 (SolidWorks 的配置名)
    TEXT("D:/Models")                // 根文件夹 (用于查找相关装配体)
);

// 检查文件格式
if (SWFileDescriptor.GetFileFormat() == ECADFormat::SOLIDWORKS)
{
    UE_LOG(LogTemp, Log, TEXT("正在处理 SolidWorks 文件: %s"), *SWFileDescriptor.GetFileName());
}

// 可以为该文件指定缓存路径，避免重复转换
SWFileDescriptor.SetCacheFile(TEXT("C:/UECache/UEx1234abcd.prc"));
```

2.  **设置导入参数**：使用 `FImportParameters` 控制网格化的精度和算法。

```cpp
// (来源：根据 CADOptions.h 中 FImportParameters 类设计的示例)
FImportParameters ImportParams;

// 设置网格化参数：弦高公差0.1，最大边长100，最大法线角15度
ImportParams.SetTesselationParameters(0.1, 100.0, 15.0, EStitchingTechnique::StitchingSew);

// 选择网格化后端 (默认是 TechSoft，也可以指定 CADKernel)
// ImportParams.SetTesselationParameters(0.1, 100.0, 15.0, EStitchingTechnique::StitchingSew, EMesher::CADKernel);

// 应用全局控制参数
FImportParameters::bGEnableCADCache = true; // 启用缓存
FImportParameters::GStitchingTolerance = 0.001f; // 设置缝合容差
```

3.  **处理网格数据**：`FBodyMesh` 是转换后的核心输出，包含顶点、面片和材质信息。

```cpp
// (来源：根据 CADData.h 中 FBodyMesh, FTessellationData 结构设计的示例)
// 假设通过某个转换器获得了 FBodyMesh
FBodyMesh ConvertedMesh;
ConvertedMesh.BodyID = 1001; // 来自 CAD 文件的 Body ID

// 检查网格信息
UE_LOG(LogTemp, Log, TEXT("Body %u: 顶点数 %d, 面片数 %d, 三角面数 %u"),
    ConvertedMesh.BodyID,
    ConvertedMesh.VertexArray.Num(),
    ConvertedMesh.Faces.Num(),
    ConvertedMesh.TriangleCount);

// 遍历每个面片（FTessellationData）
for (const FTessellationData& Face : ConvertedMesh.Faces)
{
    // 检查面片的材质和颜色标识符
    if (Face.MaterialUId)
    {
        // 此面片使用了特定材质
    }
    if (Face.ColorUId)
    {
        // 此面片使用了特定颜色
    }
}

// 将处理后的网格集合序列化到文件，用于缓存
TArray<FBodyMesh> MeshSet;
MeshSet.Add(ConvertedMesh);
CADLibrary::SerializeBodyMeshSet(TEXT("C:/UECache/body_meshes.bin"), MeshSet);
```

### 进阶用法

结合文件描述符、导入参数和网格数据，可以模拟一个简单的导入流程：

```cpp
// (综合示例)
FFileDescriptor FileDesc(TEXT("D:/Assemblies/MainAssembly.stp"));
FImportParameters Params;
Params.SetTesselationParameters(0.5, 500.0, 20.0, EStitchingTechnique::StitchingHeal);

// 1. 检查缓存
FString CachePath = CADLibrary::BuildCadCachePath(TEXT("/Cache"), FileDesc.GetDescriptorHash());
if (FPaths::FileExists(CachePath) && FImportParameters::bGEnableCADCache)
{
    // 从缓存加载
    TArray<FBodyMesh> CachedMeshes;
    CADLibrary::DeserializeBodyMeshFile(*CachePath, CachedMeshes);
    // ... 处理加载的网格
}
else
{
    // 2. 无缓存，调用实际的 CAD 转换器（此处为示意，实际由翻译器模块处理）
    // FCADTranslatorInterface* Translator = GetTranslatorForFormat(FileDesc.GetFileFormat());
    // Translator->ProcessFile(FileDesc, Params);
    // ... 获取结果 TArray<FBodyMesh> ResultMeshes;

    // 3. 保存到缓存
    // CADLibrary::SerializeBodyMeshSet(*CachePath, ResultMeshes);
}
```

## Demo 示例

以下是一个最小化的 C++ 类，演示如何在 Actor 中存储和展示从 CAD 数据结构转换而来的基础网格信息。

**CADInfoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CADTools/CADData.h"
#include "CADInfoActor.generated.h"

UCLASS()
class ACADInfoActor : public AActor
{
	GENERATED_BODY()

public:
	ACADInfoActor();

	virtual void BeginPlay() override;

	// 用于在编辑器中展示 CAD 模型的基本信息
	UFUNCTION(BlueprintCallable, Category = "CAD Info")
	void LoadCADMeshFromFile(const FString& FilePath);

private:
	// 存储的网格数据
	CADLibrary::FBodyMesh CurrentMesh;
};
```

**CADInfoActor.cpp**
```cpp
#include "CADInfoActor.h"

ACADInfoActor::ACADInfoActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void ACADInfoActor::BeginPlay()
{
	Super::BeginPlay();
	// 这里可以加载预置的CAD数据或进行其他初始化
}

void ACADInfoActor::LoadCADMeshFromFile(const FString& FilePath)
{
	// 模拟加载过程（实际应通过 Datasmith 或 CADTranslator 模块）
	// 本示例仅演示数据结构的使用
	CADLibrary::FFileDescriptor Desc(FilePath);

	// 填充一些示例数据
	CurrentMesh.BodyID = 1;
	CurrentMesh.VertexArray.Add(FVector3f(0, 0, 0));
	CurrentMesh.VertexArray.Add(FVector3f(100, 0, 0));
	CurrentMesh.VertexArray.Add(FVector3f(0, 100, 0));

	CADLibrary::FTessellationData Face;
	Face.PositionIndices = {0, 1, 2};
	Face.NormalArray = {FVector3f(0, 0, 1), FVector3f(0, 0, 1), FVector3f(0, 0, 1)};
	CurrentMesh.Faces.Add(Face);
	CurrentMesh.TriangleCount = 1;

	UE_LOG(LogTemp, Warning, TEXT("从 %s 加载的 CAD 网格：顶点数 %d， 面数 %d"),
		*Desc.GetFileName(),
		CurrentMesh.VertexArray.Num(),
		CurrentMesh.Faces.Num());
}
```

## 模块依赖

`CADTools` 模块作为核心数据模块，被其他所有模块依赖。以下是此插件**独特且关键的依赖**：

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供对众多 CAD 格式（JT, STEP, IGES 等）的解析和曲面细分能力。是插件的默认网格化后端。 |
| `OpenNurbs6` | 为 `DatasmithOpenNurbsTranslator` 模块提供对 Rhino 3DM 文件格式的支持。 |
| `DatasmithCore` | 提供 Datasmith 场景、资产和工具的基础定义，是此插件的数据输出目标。 |

**注意**：要正常使用此插件，你的项目通常还需要依赖 `DatasmithImporter` 模块来触发整个导入流程。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数时产生的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加逻辑，确保 Wire 格式翻译器在安装了 Alias 2027 的环境下仍能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 库更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本标识。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器间可移植，提升代码兼容性。 |

### 维护评价

**活跃维护**。该插件作为 UE5 企业版和专业工作流的核心组件，持续得到 Epic Games 的维护和更新。
-   **年龄**：约 6 年，属于成熟组件。
-   **更新频率**：最近一次更新在几天前（2026-05-13），并且近期有多次提交，包括功能兼容性增强（Alias 2027）、依赖库升级（TechSoft）和代码质量改进（编译警告）。
-   **状态**：明确处于**活跃维护**状态。它不是一个已废弃的功能，而是连接工业 CAD 软件与 Unreal Engine 的关键桥梁。
-   **推荐使用**：对于任何需要处理专业 CAD 数据的工作流，此插件是**推荐且必需**的。默认禁用（`EnabledByDefault: false`）是因为它体积较大且依赖特定的第三方库（如 TechSoft），用户需要根据项目需求在插件管理器中手动启用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)