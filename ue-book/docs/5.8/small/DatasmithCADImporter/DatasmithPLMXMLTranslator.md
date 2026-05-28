# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD文件工具集 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

这个插件是 UE5 Datasmith 框架中用于导入专业 CAD（计算机辅助设计）文件的核心工具集。它并非一个独立的格式处理器，而是提供了一整套基础设施、库和翻译器模块，用于解析来自不同 CAD 软件（如 CATIA, SolidWorks, NX, Inventor, PLMXML 等）的复杂几何体和场景结构，并将其转换为 Unreal Engine 可使用的静态网格、材质和场景层级数据。

它主要解决以下问题：
1.  **格式繁杂**：工业 CAD 软件格式众多，且通常包含复杂的参数化曲面、装配体和产品结构（BOM），UE 原生无法直接读取。
2.  **几何转换**：将 CAD 格式中的精确几何表示（B-Rep, 参数化曲面）转换为游戏引擎所需的三角面片（Polygon）网格。
3.  **场景映射**：解析 CAD 文件中的装配体层级、组件实例、材料属性等信息，并正确映射到 UE 的 Actor/Component 结构。

该插件默认禁用 (`EnabledByDefault: false`)，因为它依赖外部的第三方商业库（如 TechSoft, OpenNurbs）来处理核心的 CAD 文件解析，这些库需要用户自行获取并配置。

## 使用场景

-   你需要将来自 SolidWorks、CATIA、NX、Inventor 等 CAD 软件的三维模型（`.sldprt`, `.catpart`, `.prt`, `.ipt` 等）导入到 Unreal Engine 中进行可视化、培训或数字孪生项目。
-   你拥有 PLMXML 格式的产品生命周期管理数据，需要将其中的产品结构、几何和元数据完整地导入引擎。
-   你需要导入复杂的、包含参数化曲面（NURBS）的 CAD 模型，而不是简单的网格文件。
-   你的项目属于汽车、航空、建筑或工业制造领域，需要处理上游设计部门提供的原始 CAD 数据。

## 蓝图用法

此插件主要作为 Datasmith 导入流程的底层引擎存在，其核心功能（解析 CAD 文件、转换几何）均在 C++ 层实现，**没有直接暴露给蓝图使用的函数节点**。

用户通过 **Datasmith 导入器**（`File -> Import`）或 **Datasmith Scene Actor**（蓝图中）来使用该插件的能力。在导入文件时，如果文件格式受支持，UE 会自动调用此插件中对应的翻译器模块。

### 核心节点

无。所有操作都在导入过程中由引擎自动调用。

### 使用示例（蓝图描述）

1.  在内容浏览器中，右键选择 `Import`。
2.  浏览并选择一个支持的 CAD 文件（如 `.catproduct`, `.sldasm`）。
3.  在弹出的 Datasmith 导入选项中，可以配置网格化参数（细分精度、光滑组等），这些选项会传递给底层的 CAD 翻译器。
4.  导入完成后，场景和网格资产将出现在内容浏览器中，可以像普通资产一样拖拽到关卡中使用。

## C++ 用法

### 头文件引入

由于插件模块众多，你需要根据具体需求引入。通常，使用者与 Datasmith 翻译器交互，而不是直接调用底层 CAD 接口。

```cpp
// 引入 PLMXML 翻译器模块
#include "DatasmithPlmXmlTranslatorModule.h"
```

### 基本用法

以下示例展示了如何在 C++ 中检查 `DatasmithPLMXMLTranslator` 模块是否可用并获取其引用。这通常用于在程序化导入流程中验证功能是否就绪。
（来源：`Source/DatasmithPLMXMLTranslator/Public/DatasmithPlmXmlTranslatorModule.h`）

```cpp
#include "DatasmithPlmXmlTranslatorModule.h"

// 检查 PLMXML 翻译器模块是否已加载
if (IDatasmithPlmXmlTranslatorModule::IsAvailable())
{
    // 获取模块引用，通常用于触发其注册过程或访问高级功能
    IDatasmithPlmXmlTranslatorModule& PlmXmlModule = IDatasmithPlmXmlTranslatorModule::Get();
    // 此处模块引用可用于进一步操作，但其主要作用是确保模块被加载，使翻译器对 Datasmith 可见。
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("DatasmithPLMXMLTranslator module is not available."));
}
```

### 进阶用法

插件的核心是 `IDatasmithTranslator` 接口的各种实现。`FDatasmithPlmXmlTranslator` 是其中一个实现，展示了标准翻译器的生命周期。
（来源：`Source/DatasmithPLMXMLTranslator/Private/DatasmithPlmXmlTranslator.h`）

```cpp
// 假设你有一个 FDatasmithPlmXmlTranslator 的实例 (Translator)
// 这通常由 Datasmith 导入管理器内部创建和管理。

// 1. 初始化翻译器并查询其能力
FDatasmithTranslatorCapabilities Capabilities;
Translator->Initialize(Capabilities);

// 2. 检查源文件是否支持
FDatasmithSceneSource Source;
Source.SetSourceFile(TEXT("C:/Models/Assembly.plmxml"));
if (!Translator->IsSourceSupported(Source))
{
    return; // 文件不受支持
}

// 3. 加载场景
TSharedRef<IDatasmithScene> Scene = MakeShared<FDatasmithScene>();
if (!Translator->LoadScene(Scene))
{
    return; // 加载失败
}

// 4. (可选) 获取并设置导入选项
TArray<TObjectPtr<UDatasmithOptionsBase>> ImportOptions;
Translator->GetSceneImportOptions(ImportOptions);
// 修改选项...
Translator->SetSceneImportOptions(ImportOptions);

// 5. 遍历场景中的网格元素并加载它们
for (int32 i = 0; i < Scene->GetMeshesCount(); ++i)
{
    TSharedRef<IDatasmithMeshElement> MeshElement = Scene->GetMesh(i);
    FDatasmithMeshElementPayload MeshPayload;
    if (Translator->LoadStaticMesh(MeshElement, MeshPayload))
    {
        // 使用 MeshPayload 中的网格数据创建 UStaticMesh 等资产
    }
}

// 6. 使用完毕后卸载
Translator->UnloadScene();
```

## Demo 示例

以下是一个展示如何使用 `DatasmithPLMXMLTranslator` 模块的最小示例。注意，这主要用于理解模块接口，实际项目中通常由引擎的导入流程自动完成。

**DatasmithPlmXmlDemoActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "DatasmithPlmXmlDemoActor.generated.h"

UCLASS()
class ADatasmithPlmXmlDemoActor : public AActor
{
	GENERATED_BODY()
public:
	ADatasmithPlmXmlDemoActor();

	// 要导入的 PLMXML 文件路径
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Datasmith Demo")
	FFilePath PlmXmlFile;

	// 尝试加载 PLMXML 场景
	UFUNCTION(BlueprintCallable, Category = "Datasmith Demo")
	bool LoadPlmXmlScene();

private:
	// 存储加载的场景
	TSharedPtr<IDatasmithScene> LoadedScene;
};
```

**DatasmithPlmXmlDemoActor.cpp**
```cpp
#include "DatasmithPlmXmlDemoActor.h"
#include "DatasmithPlmXmlTranslatorModule.h"
#include "DatasmithPlmXmlTranslator.h" // 注意：这是私有头文件，此处仅为演示

ADatasmithPlmXmlDemoActor::ADatasmithPlmXmlDemoActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

bool ADatasmithPlmXmlDemoActor::LoadPlmXmlScene()
{
	if (!PlmXmlFile.FilePath.IsEmpty() && IDatasmithPlmXmlTranslatorModule::IsAvailable())
	{
		// 创建翻译器实例
		TSharedRef<FDatasmithPlmXmlTranslator> Translator = MakeShared<FDatasmithPlmXmlTranslator>();
		
		// 初始化
		FDatasmithTranslatorCapabilities Caps;
		Translator->Initialize(Caps);

		// 设置源并检查
		FDatasmithSceneSource Source;
		Source.SetSourceFile(PlmXmlFile.FilePath);
		if (!Translator->IsSupported(Source))
		{
			UE_LOG(LogTemp, Error, TEXT("File not supported: %s"), *PlmXmlFile.FilePath);
			return false;
		}

		// 加载场景
		LoadedScene = MakeShared<FDatasmithScene>();
		if (!Translator->LoadScene(LoadedScene.ToSharedRef()))
		{
			UE_LOG(LogTemp, Error, TEXT("Failed to load scene from: %s"), *PlmXmlFile.FilePath);
			return false;
		}

		UE_LOG(LogTemp, Log, TEXT("Successfully loaded PLMXML scene with %d meshes"), LoadedScene->GetMeshesCount());
		
		// 注意：此演示未实际创建 UStaticMesh 资产。实际应用需使用 FDatasmithSceneExporter 或类似工具。
		// 记得在适当时机调用 Translator->UnloadScene();
		return true;
	}
	return false;
}
```

## 模块依赖

要使用此插件，你的项目模块通常需要依赖 **Datasmith** 核心模块。具体需要哪些取决于你交互的层面。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 底层 CAD 文件读取库（需要单独配置） |
| `OpenNurbs6` | 底层 OpenNurbs 库，用于读取 Rhino 文件格式 |
| `DatasmithCore` | Datasmith 核心场景、元素和翻译器接口定义 |
| `DatasmithTranslator` | 翻译器基类和导入管理器 |
| `DatasmithDispatcher` | 多进程/线程调度，用于并行处理 CAD 网格 |

**简化依赖**：如果你的模块只需要触发导入流程或与导入后的资产交互，通常只需依赖 `DatasmithCore` 和 `DatasmithRuntime`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增强 Wire 翻译器兼容性，支持 Alias 2027。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将核心 CAD 库 TechSoft 升级至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 CAD 缓存的版本号。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复跨编译器（MSVC/Clang）的类型转换警告，提高代码可移植性。 |

### 维护评价

-   **活跃维护**：作为 Epic Games 官方支持的企业级功能（Enterprise 标签），该插件一直处于持续的维护和功能增强中。从 Git 历史看，更新非常频繁（最近更新在 2026 年 5 月）。
-   **核心依赖更新**：维护工作紧跟其底层第三方库（如 TechSoft）的更新，确保对新版本 CAD 软件格式的支持。
-   **代码质量**：近期提交集中于编译警告修复、跨编译器兼容性提升和依赖版本升级，表明代码库处于健康、持续改进的状态。
-   **注意事项**：该插件**默认禁用** (`EnabledByDefault: false`)，且依赖外部商业库（TechSoft, OpenNurbs），用户需要自行获取这些库并正确配置才能使用。这是其使用门槛。
-   **推荐使用**：对于有工业 CAD 导入需求的项目，这是 **官方推荐且唯一受支持** 的解决方案。如果你需要处理专业的 CAD 格式，这是必须启用的插件。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例]（暂无公开测试用例路径）

---
# Datasmith PLMXML Translator

> （子模块文档）专门处理 PLMXML 格式文件的 Datasmith 翻译器模块。

| 属性 | 值 |
|---|---|
| 中文名 | PLMXML翻译器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithPLMXMLTranslator` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Source/DatasmithPLMXMLTranslator) | |

## 用途

`DatasmithPLMXMLTranslator` 模块是 `DatasmithCADImporter` 插件中的一个专用翻译器。它的唯一职责是解析 **PLMXML** 格式文件。PLMXML 是一种基于 XML 的开放标准，常用于在 PLM（产品生命周期管理）系统（如 Siemens Teamcenter）中交换产品结构、几何、元数据和 3D 视图信息。

此模块的作用是将 PLMXML 文件中的数据转换为 Datasmith 能够理解的通用场景（`IDatasmithScene`）和网格（`IDatasmithMeshElement`）数据，从而驱动整个导入流程。

## 使用场景

-   你的数据来源于 Teamcenter 等 PLM 系统，导出格式为 `.plmxml`。
-   你需要将 PLMXML 中定义的完整产品 BOM（物料清单）结构、组件实例、变换以及关联的 CAD 几何体一起导入到 Unreal Engine。
-   你需要保留 PLMXML 中携带的属性信息（如零件号、材料名称、自定义元数据）。

## 蓝图用法

无直接蓝图 API。该模块作为服务提供者，当用户通过标准 Datasmith 导入界面选择一个 `.plmxml` 文件时，会自动被引擎调用。

## C++ 用法

### 头文件引入

```cpp
// 引入模块接口以检查可用性
#include "DatasmithPlmXmlTranslatorModule.h"
```

### 基本用法

检查模块是否已加载并就绪。这是确保翻译器对 Datasmith 导入系统可见的关键。
（来源：`Source/DatasmithPLMXMLTranslator/Public/DatasmithPlmXmlTranslatorModule.h`）

```cpp
// 在任何依赖 PLMXML 导入功能的代码之前检查
if (!IDatasmithPlmXmlTranslatorModule::IsAvailable())
{
    // 模块未加载，可能是插件被禁用或依赖库缺失
    UE_LOG(LogTemp, Error, TEXT("DatasmithPLMXMLTranslator module is not loaded. Cannot import PLMXML files."));
    return;
}

// 模块已就绪，现在可以通过 Datasmith 导入路径使用
```

### 进阶用法

直接与翻译器类交互，控制导入过程。这通常由 Datasmith 的导入管理器 (`FDatasmithSceneImporter`) 内部完成。
（来源：`Source/DatasmithPLMXMLTranslator/Private/DatasmithPlmXmlTranslator.h`）

```cpp
// 假设我们手动模拟导入过程（仅供理解）
#include "DatasmithPlmXmlTranslator.h"

TSharedRef<FDatasmithPlmXmlTranslator> Translator = MakeShared<FDatasmithPlmXmlTranslator>();

// 初始化
FDatasmithTranslatorCapabilities Capabilities;
Translator->Initialize(Capabilities);

// 配置源
FDatasmithSceneSource Source;
Source.SetSourceFile(TEXT("/Game/Path/To/MyModel.plmxml"));

// 加载场景描述
TSharedRef<IDatasmithScene> Scene = MakeShared<FDatasmithScene>();
if (Translator->LoadScene(Scene))
{
    // 场景已加载，现在可以查询网格
    for (int32 i = 0; i < Scene->GetMeshesCount(); ++i)
    {
        TSharedRef<IDatasmithMeshElement> Mesh = Scene->GetMesh(i);
        FDatasmithMeshElementPayload Payload;
        
        // 按需加载每个网格的几何数据
        if (Translator->LoadStaticMesh(Mesh, Payload))
        {
            // Payload 中包含顶点、索引、材质槽等数据
            // 用于创建真正的 UStaticMesh 资产
        }
    }
    
    // 清理
    Translator->UnloadScene();
}
```

## Demo 示例

一个完整的、聚焦于 PLMXML 导入的最小示例。

**PlmXmlImporterHelper.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class IDatasmithScene;
class IDatasmithMeshElement;

class FPlmXmlImporterHelper
{
public:
    // 尝试从 PLMXML 文件导入一个简单的场景摘要
    static bool ImportSceneSummary(const FString& PlmXmlFilePath, FString& OutSummary);
    
private:
    static void ProcessScene(const TSharedRef<IDatasmithScene>& Scene, FString& OutSummary);
};
```

**PlmXmlImporterHelper.cpp**
```cpp
#include "PlmXmlImporterHelper.h"
#include "DatasmithPlmXmlTranslatorModule.h"
#include "DatasmithPlmXmlTranslator.h"
#include "IDatasmithSceneElements.h"

bool FPlmXmlImporterHelper::ImportSceneSummary(const FString& PlmXmlFilePath, FString& OutSummary)
{
    if (!IDatasmithPlmXmlTranslatorModule::IsAvailable())
    {
        OutSummary = TEXT("Translator module not available.");
        return false;
    }

    TSharedRef<FDatasmithPlmXmlTranslator> Translator = MakeShared<FDatasmithPlmXmlTranslator>();
    FDatasmithTranslatorCapabilities Caps;
    Translator->Initialize(Caps);

    FDatasmithSceneSource Source;
    Source.SetSourceFile(PlmXmlFilePath);

    if (!Translator->IsSourceSupported(Source))
    {
        OutSummary = FString::Printf(TEXT("File not supported: %s"), *PlmXmlFilePath);
        return false;
    }

    TSharedRef<IDatasmithScene> Scene = MakeShared<FDatasmithScene>();
    if (!Translator->LoadScene(Scene))
    {
        OutSummary = TEXT("Failed to load scene.");
        return false;
    }

    ProcessScene(Scene, OutSummary);
    Translator->UnloadScene();
    return true;
}

void FPlmXmlImporterHelper::ProcessScene(const TSharedRef<IDatasmithScene>& Scene, FString& OutSummary)
{
    int32 ActorCount = Scene->GetActorsCount();
    int32 MeshCount = Scene->GetMeshesCount();

    OutSummary = FString::Printf(
        TEXT("PLMXML Scene Loaded:\n  Actors: %d\n  Meshes: %d\n\nFirst few meshes:\n"),
        ActorCount, MeshCount
    );

    for (int32 i = 0; i < FMath::Min(MeshCount, 5); ++i)
    {
        TSharedRef<IDatasmithMeshElement> Mesh = Scene->GetMesh(i);
        OutSummary += FString::Printf(TEXT("  - %s\n"), *Mesh->GetName());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TechSoft` | PLMXML 文件的底层解析依赖于 TechSoft 库 |
| `DatasmithCore` | 提供 `IDatasmithScene`, `IDatasmithTranslator` 等基础接口 |
| `DatasmithDispatcher` | 可能用于并行加载 PLMXML 中引用的网格数据 |

## 维护状态

该模块与主插件 `DatasmithCADImporter` 的维护状态完全同步。近期更新（如 TechSoft 库升级、编译修复）均适用于此模块。作为官方维护的企业级组件，它保持着稳定的更新节奏以确保与最新版本 CAD 软件的兼容性。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Source/DatasmithPLMXMLTranslator)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例]（暂无公开测试用例路径）