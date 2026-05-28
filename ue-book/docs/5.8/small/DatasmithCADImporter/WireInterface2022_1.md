# Datasmith CAD Importer

> Collection of tools to work with CAD files.（照抄，不翻译）

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

本插件是一个企业级 CAD 文件导入解决方案的核心，作为 Unreal Datasmith 技术栈的一部分。它主要解决将不同 CAD 软件（特别是工业设计和产品可视化领域常用的工具）生成的复杂、高精度模型高效、无损地导入 Unreal Engine 的问题。

`DatasmithCADImporter` 本身是一个聚合插件，包含了用于处理多种 CAD 格式（如 `.wire` (Alias)、`.jt`、`.plmxml`、OpenNurbs (`.3dm`)、TechSoft 等）的翻译器和工具库。本次分析的 `WireInterface2022_1` 模块，是其中一个专门用于解析 **Alias 2022.1** 版本 `.wire` 文件格式的翻译器实现。它负责读取 Alias 的场景图（DAG）、提取几何体（网格、曲面）、处理材质并将其转换为 Unreal Datasmith 能理解的元素，最终实现实时渲染或进一步处理。

其存在价值在于弥合专业 CAD 工业软件与游戏/实时引擎之间的数据鸿沟，让设计师和工程师能直接在 Unreal 中利用其 CAD 资产进行实时可视化、虚拟评审或数字孪生构建。

## 使用场景

- **产品设计与可视化**：汽车、消费品等行业的设计师使用 Autodesk Alias 创建外形，需要将高精度模型导入 Unreal 进行实时渲染、交互式配置或营销材料制作。
- **工业流程仿真**：将 CAD 设计数据集成到基于 Unreal 的培训或仿真系统中。
- **跨软件资产管线**：作为资产管线的一部分，自动将 Alias 设计文件转换为 Unreal 可用的格式。

## 蓝图用法

本模块 (`WireInterface2022_1`) 是一个底层的运行时翻译器，其功能通过 Datasmith 导入流程在后台调用，并不直接暴露给蓝图系统。用户通过 Unreal 编辑器的 **Datasmith 导入器**（`.udatasmith` 或直接支持的格式）间接使用此功能。在导入 `.wire` 文件时，引擎会根据文件版本自动选择对应的 `WireInterface` 模块。

## C++ 用法

本模块的核心是实现 `IWireInterface` 接口，主要由 `FWireTranslatorImpl` 类完成。

### 头文件引入

使用此模块通常不需要直接引入其头文件，而是通过 Datasmith 翻译器框架调用。如需在扩展开发中使用，可引入模块头文件：
```cpp
#include "WireInterfaceModule.h" // FDatasmithWireTranslatorModule
```

### 基本用法

**1. 模块可用性检查与临时目录**
```cpp
// 检查 WireTranslator 模块是否可用
if (FDatasmithWireTranslatorModule::IsAvailable())
{
    // 获取模块实例，通常用于获取临时文件路径等
    FDatasmithWireTranslatorModule& WireModule = FDatasmithWireTranslatorModule::Get();
    FString TempDir = WireModule.GetTempDir();
    UE_LOG(LogTemp, Log, TEXT("Wire translator temp dir: %s"), *TempDir);
}
```

**2. 核心翻译流程 (内部使用逻辑)**
从 `FWireTranslatorImpl` 的接口可以推断其典型使用流程：
```cpp
// 假设已有 IWireInterface 指针 (通常由 Datasmith 根据文件类型创建)
TSharedPtr<IWireInterface> WireTranslator = /* ... */;

// 1. 初始化，传入 .wire 文件路径
bool bInitialized = WireTranslator->Initialize(TEXT("C:/Models/Car.wire"));

// 2. 设置导入选项（单位、曲面细分等）
FWireSettings Options;
Options.TessellationParameters.CurveTolerance = 0.1f;
WireTranslator->SetImportSettings(Options);

// 3. 设置输出路径（用于生成缓存或中间文件）
WireTranslator->SetOutputPath(FPaths::ProjectSavedDir() / TEXT("WireCache"));

// 4. 加载场景，解析模型结构，生成 Datasmith Scene 对象
TSharedPtr<IDatasmithScene> DatasmithScene = MakeShared<FDatasmithScene>();
bool bLoaded = WireTranslator->Load(DatasmithScene);

// 5. 之后，通过 Datasmith 框架将 DatasmithScene 转换为 Unreal 资产
```

### 进阶用法：网格提取

翻译器在后台处理网格时，会调用 `LoadStaticMesh` 方法，该方法内部依赖几何转换器（如 `FAliasModelToCADKernelConverter` 或 `FAliasModelToTechSoftConverter`）将 Alias 的几何数据转换为 `FMeshDescription`。
```cpp
// 简化的内部调用逻辑示意
bool FWireTranslatorImpl::LoadStaticMesh(
    const TSharedPtr<IDatasmithMeshElement> MeshElement,
    FDatasmithMeshElementPayload& OutMeshPayload,
    const FDatasmithTessellationOptions& InTessellationOptions)
{
    // ... 查找对应的几何数据源 (如 FAlDagNodePtr, FBodyNode, FPatchMesh)
    // ... 调用 GetMeshDescription(...) 获取转换后的网格描述
    TOptional<FMeshDescription> MeshDesc = GetMeshDescription(MeshElement, OutMeshPayload);
    if (MeshDesc.IsSet())
    {
        OutMeshPayload.LODs.Add(MeshDesc.GetValue());
        return true;
    }
    return false;
}
```

## Demo 示例

**场景**：模拟一个简单的场景，尝试加载一个 `.wire` 文件。
*注意：这需要项目正确配置了 Datasmith 和 Alias 插件依赖。*

```cpp
// WireDemo.h
#pragma once
#include "CoreMinimal.h"

class FWireDemo
{
public:
    static void RunDemo(const FString& WireFilePath);
};
```

```cpp
// WireDemo.cpp
#include "WireDemo.h"
#include "WireInterfaceModule.h"
#include "IWireInterface.h" // 来自 DatasmithCADTranslator 模块
#include "DatasmithSceneFactory.h"
#include "DatasmithScene.h"

void FWireDemo::RunDemo(const FString& WireFilePath)
{
    // 1. 确保 WireInterface 模块可用
    if (!FDatasmithWireTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("WireInterface module is not available."));
        return;
    }

    // 2. 创建一个 Wire Translator 实例 (通常由 Datasmith 的翻译器工厂自动完成)
    // 这里简化演示，实际中需使用模块管理器根据文件版本创建对应实例
    // TSharedPtr<IWireInterface> Translator = ...;

    // 3. 假设我们已经获得了正确的 IWireInterface 实例
    // (以下代码为逻辑演示，非可直接编译的完整获取过程)

    // 创建一个临时的 Datasmith Scene 来接收数据
    TSharedPtr<IDatasmithScene> NewScene = FDatasmithSceneFactory::CreateScene(TEXT("WireImportDemo"));

    // 初始化翻译器
    // Translator->Initialize(*WireFilePath);

    // 设置选项
    // FWireSettings Settings;
    // Translator->SetImportSettings(Settings);

    // 执行加载
    // bool bSuccess = Translator->Load(NewScene);

    // if (bSuccess)
    // {
    //     UE_LOG(LogTemp, Log, TEXT("Wire file loaded successfully. Scene has %d actors."), NewScene->GetActorsCount());
    //     // 接下来可通过 Datasmith 导入器将 NewScene 转换为 Unreal 资产
    // }
    // else
    // {
    //     UE_LOG(LogTemp, Error, TEXT("Failed to load Wire file: %s"), *WireFilePath);
    // }
}
```

## 模块依赖

从模块构建文件分析，本插件依赖一些特殊的外部库，用于解析特定的 CAD 几何内核。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供用于读取和转换特定 CAD 格式（如 JT）的几何内核库。 |
| `OpenNurbs6` | 用于读取 OpenNurbs (`.3dm`) 格式的几何内核库。 |

此外，所有模块都隐式依赖 `DatasmithCore` 和 `CADLibrary` 等核心 Datasmith 与 CAD 处理模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下，双精度常量截断为单精度浮点数导致的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 添加逻辑，使得即使安装了 Alias 2027，Wire 翻译器仍能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 库更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 DatasmithCAD 缓存的版本标识。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器间具有可移植性。 |

### 维护评价

该插件模块**正处于活跃维护中**。从最近的提交记录（截至2026年5月）来看，更新非常频繁，主要集中在：
1.  **兼容性更新**：持续适配新版本的 Alias 软件（如 Alias 2027），并更新核心依赖库（TechSoft）。
2.  **编译健壮性**：修复了跨编译器的警告和浮点精度问题，表明团队注重代码质量和跨平台支持。
3.  **基础设施更新**：更新缓存版本，可能意味着改进了数据导入或处理的流程。

尽管插件整体创建时间已有约7年，但作为企业级 Datasmith 生态的关键组件，它随着主引擎和依赖库的迭代而持续更新。**推荐使用**，特别是对于需要处理现代版本 Alias `.wire` 文件的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)