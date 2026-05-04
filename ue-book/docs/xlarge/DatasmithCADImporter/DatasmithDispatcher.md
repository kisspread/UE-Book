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
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

DatasmithCADImporter 是一个企业级插件，其核心功能是将各种 CAD（计算机辅助设计）文件格式（如 CATIA, NX, SolidWorks, STEP, IGES 等）导入到 Unreal Engine 中。它不仅仅是简单的文件格式转换，而是一个完整的 CAD 数据处理管线。

**`DatasmithDispatcher` 模块**是这个管线中的**任务调度与进程管理核心**。它解决的主要问题是：处理大型、复杂的 CAD 模型非常耗时且可能不稳定。为了不阻塞主编辑器线程并提高导入效率，该模块将 CAD 文件的解析和网格化（Meshing）任务分发给独立的外部工作进程（Worker Process）来执行。它通过网络套接字（Socket）与这些外部进程通信，管理任务队列、监控进程状态、处理进程崩溃并自动重启，从而实现高效、稳定的并行 CAD 文件处理。

## 使用场景

- **建筑、汽车、工业设计等领域**：需要将大型、高精度的 CAD 模型（如整车、整栋建筑、复杂机械）导入 UE 进行实时可视化、虚拟评审或数字孪生构建。
- **需要批量导入 CAD 文件**：当项目包含数十甚至数百个 CAD 零件时，使用 `DatasmithDispatcher` 的多进程并行处理能力可以显著缩短总导入时间。
- **导入过程需要高稳定性**：对于可能因格式复杂或文件损坏而导致解析器崩溃的 CAD 文件，该模块的进程隔离和自动重启机制可以保证主编辑器的稳定性。

## 蓝图用法

`DatasmithDispatcher` 模块主要作为底层运行时库，其功能通过 Datasmith 导入流程在内部调用，**没有直接暴露给蓝图的 `BlueprintCallable` 函数或属性**。用户通过标准的 Datasmith 导入对话框（文件 -> 导入到关卡）来使用其功能，无需在蓝图中直接操作此模块。

## C++ 用法

本模块的 API 主要面向引擎内部的 Datasmith 导入系统开发者，用于集成和扩展 CAD 导入流程。

### 头文件引入

```cpp
#include "DatasmithDispatcher.h"
#include "DatasmithDispatcherTask.h"
```

### 基本用法

核心类是 `FDatasmithDispatcher`，用于管理任务队列和工作进程。

```cpp
// 来源: Engine/Plugins/Enterprise/DatasmithCADImporter/Source/DatasmithDispatcher/Public/DatasmithDispatcher.h

// 1. 准备导入参数和缓存路径
CADLibrary::FImportParameters ImportParams;
FString CacheDir = FPaths::ProjectSavedDir() / TEXT("CADImportCache");
TMap<uint32, FString> FileMap, GeomMap;

// 2. 创建调度器实例
DatasmithDispatcher::FDatasmithDispatcher Dispatcher(ImportParams, CacheDir, FileMap, GeomMap);

// 3. 设置工作进程数量（可选）
Dispatcher.SetWorkerCount(4); // 使用4个工作进程

// 4. 添加需要处理的CAD文件任务
CADLibrary::FFileDescriptor FileDesc;
FileDesc.FilePath = TEXT("/path/to/model.CATPart");
Dispatcher.AddTask(FileDesc, CADLibrary::EMesher::Default);

// 5. 启动处理流程（bWithProcessor=true 表示使用外部进程）
Dispatcher.Process(true);

// 6. 检查是否完成
while (!Dispatcher.IsOver())
{
    // 可以在此处执行其他逻辑或等待
    FPlatformProcess::Sleep(0.1f);
}
```

### 进阶用法

可以自定义任务状态和处理流程。

```cpp
// 来源: Engine/Plugins/Enterprise/DatasmithCADImporter/Source/DatasmithDispatcher/Public/DatasmithDispatcherTask.h

// 获取下一个待处理的任务
TOptional<DatasmithDispatcher::FTask> NextTask = Dispatcher.GetNextTask();
if (NextTask.IsSet())
{
    // 手动处理任务（例如在自定义的本地处理逻辑中）
    // ... 处理逻辑 ...
    
    // 更新任务状态
    Dispatcher.SetTaskState(NextTask->Index, DatasmithDispatcher::ETaskState::Succeed);
}

// 将处理后的CAD文件映射到Unreal缓存文件
CADLibrary::FFileDescriptor ProcessedFile;
FString UnrealSceneFile = TEXT("/path/to/unreal_scene.usd");
FString UnrealGeomFile = TEXT("/path/to/unreal_geom.usd");
Dispatcher.LinkCTFileToUnrealCacheFile(ProcessedFile, UnrealSceneFile, UnrealGeomFile);
```

## Demo 示例

以下是一个最小化的示例，展示如何在 C++ 中使用 `DatasmithDispatcher` 来调度一个 CAD 文件处理任务。

**MyCADImporter.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "DatasmithDispatcher.h"

class FMyCADImporter
{
public:
    void ImportCADFile(const FString& CADFilePath);
    
private:
    TUniquePtr<DatasmithDispatcher::FDatasmithDispatcher> Dispatcher;
};
```

**MyCADImporter.cpp**
```cpp
#include "MyCADImporter.h"
#include "CADData.h"
#include "CADOptions.h"

void FMyCADImporter::ImportCADFile(const FString& CADFilePath)
{
    // 准备参数
    CADLibrary::FImportParameters ImportParams;
    FString CacheDir = FPaths::ProjectSavedDir() / TEXT("MyCADCache");
    TMap<uint32, FString> CADToUnrealFileMap;
    TMap<uint32, FString> CADToUnrealGeomMap;

    // 创建调度器
    Dispatcher = MakeUnique<DatasmithDispatcher::FDatasmithDispatcher>(
        ImportParams, CacheDir, CADToUnrealFileMap, CADToUnrealGeomMap);

    // 创建文件描述符
    CADLibrary::FFileDescriptor FileDesc;
    FileDesc.FilePath = CADFilePath;

    // 添加任务并启动处理
    Dispatcher->AddTask(FileDesc, CADLibrary::EMesher::Default);
    Dispatcher->Process(true); // 使用外部进程

    // 简单轮询等待完成（实际项目中应使用异步或回调）
    while (!Dispatcher->IsOver())
    {
        FPlatformProcess::Sleep(0.5f);
        UE_LOG(LogTemp, Log, TEXT("Importing CAD file..."));
    }

    UE_LOG(LogTemp, Log, TEXT("CAD import completed for: %s"), *CADFilePath);
}
```

## 模块依赖

本插件的模块依赖较为复杂，且高度依赖于 Epic 的专有库。以下是 `DatasmithDispatcher` 模块及整个插件的关键依赖：

| 模块 | 用途 |
|---|---|
| `CADLibrary` | 提供 CAD 数据结构（`FFileDescriptor`, `FImportParameters`）、枚举和通用工具函数。 |
| `CADData` | 定义 CAD 数据的核心类型（如 `ECADParsingResult`）。 |
| `TechSoft` | **关键依赖**。Epic 的专有 CAD 转换库，用于解析各种 CAD 格式。 |
| `OpenNurbs6` | 用于解析 Rhino 的 3DM 文件格式。 |
| `DatasmithCore` | Datasmith 的核心框架，提供场景图、材质等基础结构。 |

**注意**：由于依赖 `TechSoft` 等专有库，此插件通常无法在标准的 Unreal Engine 源码版本中编译，需要 Epic 提供的特定二进制文件或源码访问权限。

## 维护状态

### 近期更新

```
- 3fb1655bff06 Fixed crash when loading specific CATProduct file - Temporarily worked around the bug from TechSoft - Updated worker and plugin to use the newly added TechSoft binaries.
  * 修复了加载特定 CATProduct 文件时的崩溃问题，临时解决了 TechSoft 库的 bug，并更新了工作进程和插件以使用新版本的 TechSoft 二进制文件。
- 9d3e9979d5ec Issue 542235 : Back out CL 35420560
  * 回滚了某个变更（CL 35420560），可能与特定问题（Issue 542235）相关。
- 3b0464de916d Made sure ensure is disabled when compiling the CADWorker
  * 确保在编译 CADWorker（外部工作进程）时禁用了 `ensure` 宏，可能为了提高发布版本的稳定性或避免不必要的断言。
```

### 维护评价

- **活跃维护**：从最近的提交记录看，该模块仍在被积极维护和修复问题（如崩溃修复、依赖更新）。
- **企业级插件**：作为 `Enterprise` 分类下的插件，其维护优先级和稳定性通常高于实验性插件。
- **依赖复杂**：高度依赖 `TechSoft` 等专有库，这意味着其更新和问题修复可能受制于第三方库的发布周期。
- **推荐使用**：对于需要将专业 CAD 数据引入 Unreal Engine 的企业用户（如建筑、汽车、工业设计），这是官方推荐且功能完整的解决方案。对于个人或小型项目，如果不需要处理复杂 CAD 格式，可能无需启用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests) (如果存在)