# Datasmith CAD Importer

> Collection of tools to work with CAD files.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 数据精炼 CAD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

DatasmithCADImporter 是一个为企业级工作流设计的插件，其核心用途是将复杂的工业CAD（计算机辅助设计）文件高效、准确地转换为虚幻引擎可以使用的资产。它解决的根本问题是：主流CAD软件（如 CATIA, NX, SolidWorks, Alias 等）生成的专有文件格式（如 .catpart, .prt, .sldprt, .wire）通常无法被游戏引擎直接导入。这些格式包含精确的参数化几何体、装配层级、材质和元数据。

该插件通过一个**分布式处理架构**来解决这个问题。它并非在编辑器主线程中直接解析庞大的CAD文件（这可能导致编辑器卡死），而是通过 `DatasmithDispatcher` 模块将CAD文件分割成多个任务，然后派遣给独立的**外部工作进程**（Worker Process）进行处理。这些工作进程利用专门的库（如 TechSoft, OpenNurbs）解析CAD几何和拓扑，将其转换为通用网格（Mesh），最后将结果传回引擎进行组装。这种架构提高了导入速度和稳定性。

## 使用场景

- **汽车设计**：你需要将 Alias 或 CATIA 设计的车身、内饰模型导入虚幻引擎，用于制作实时配置器或虚拟展示。
- **工业机械可视化**：你的公司使用 SolidWorks 或 NX 设计复杂的机械设备，你需要将它们导入虚幻引擎创建交互式维护手册或培训模拟。
- **建筑信息模型（BIM）**：你需要导入基于 .wire 格式（如来自 MicroStation）的精确建筑模型，用于设计评审或数字孪生项目。
- **需要处理大型装配体**：你面对的 CAD 装配体包含成千上万个零件，需要一个能自动管理任务分配和容错（如崩溃重启）的稳健导入流程。

## 蓝图用法

从提供的 `DatasmithDispatcher` 模块源码分析，该模块主要提供 C++ 运行时功能，用于驱动导入任务的调度和执行。其核心逻辑（如 `FDatasmithDispatcher`, `FDatasmithWorkerHandler`）并非直接暴露给蓝图使用。该插件的蓝图接口主要体现在更上层的 `DatasmithCADTranslator` 模块中，该模块负责与虚幻引擎的资产导入框架集成。

在蓝图编辑器中，您通常不会直接使用 `DatasmithDispatcher` 中的节点。而是通过标准的虚幻引擎**内容浏览器**或**Datasmith 导入工具栏**来触发CAD文件的导入。导入过程会自动在后台调用 `DatasmithDispatcher` 的调度逻辑。

### 核心节点（C++层面概念）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddTask` | 向调度器添加一个CAD文件处理任务 | `DatasmithDispatcher::FDatasmithDispatcher` |
| `Process` | 启动或继续任务处理，可指定是否在当前进程中处理（`bWithProcessor`） | `DatasmithDispatcher::FDatasmithDispatcher` |
| `IsOver` | 检查所有任务是否已完成 | `DatasmithDispatcher::FDatasmithDispatcher` |

### 使用示例（蓝图描述）

由于 `DatasmithDispatcher` 不直接暴露蓝图节点，典型的使用方式是通过编辑器界面或 C++ 代码启动导入流程。蓝图中可能通过 `Import Asset` 等标准节点间接触发，但底层调度对用户不可见。

## C++ 用法

以下示例展示了如何使用 `DatasmithDispatcher` 模块在 C++ 中手动调度 CAD 文件转换任务。这在编写自定义导入工具或批处理脚本时非常有用。

### 头文件引入

```cpp
#include "DatasmithDispatcher.h"
#include "CADLibrary/Public/CADFileDescriptor.h" // FFileDescriptor
#include "CADLibrary/Public/CADImportParameters.h" // FImportParameters
#include "CADLibrary/Public/CADLibraryTypes.h" // EMesher
```

### 基本用法：初始化调度器并添加任务

以下代码演示了创建调度器实例、配置导入参数、添加一个文件任务并启动处理流程。

```cpp
// 来源：基于 Public/DatasmithDispatcher.h 中类接口的用法推断
void StartCADImport()
{
    // 1. 准备导入参数（例如网格精度、单位等）
    CADLibrary::FImportParameters ImportParams;
    ImportParams.Mesher = CADLibrary::EMesher::SpatialGeometry; // 选择网格化算法
    // ... 设置其他参数

    // 2. 准备输出映射（文件哈希到 Unreal 文件路径的映射）
    TMap<uint32, FString> CADFileToUnrealFileMap;
    TMap<uint32, FString> CADFileToUnrealGeomMap;

    // 3. 创建缓存目录路径
    const FString CacheDir = FPaths::ProjectSavedDir() / TEXT("DatasmithCADCache");

    // 4. 初始化调度器
    DatasmithDispatcher::FDatasmithDispatcher Dispatcher(
        ImportParams,
        CacheDir,
        CADFileToUnrealFileMap,
        CADFileToUnrealGeomMap
    );

    // 5. 添加一个CAD文件任务
    // FFileDescriptor 包含了源文件的路径、格式等信息
    CADLibrary::FFileDescriptor FileDesc(TEXT("C:/Models/engine_block.catpart"));
    Dispatcher.AddTask(FileDesc, ImportParams.Mesher);

    // 6. 启动处理（true 表示在后台进程处理）
    Dispatcher.Process(true);

    // 7. (可选) 在循环中检查状态，或使用回调等待完成
    while (!Dispatcher.IsOver())
    {
        FPlatformProcess::Sleep(0.1f);
    }

    // 8. 处理完成后，CADFileToUnrealFileMap 等映射表将被填充，
    //    可以利用这些映射在虚幻引擎中创建对应的 Static Mesh 资产。
}
```

### 进阶用法：理解任务状态与错误处理

`DatasmithDispatcher` 通过 `FTask` 和 `ETaskState` 来跟踪每个文件的处理状态。在更复杂的实现中，你可能需要监控这些状态。

```cpp
// 来源：基于 Public/DatasmithDispatcherTask.h 和 Public/DatasmithDispatcher.h
void MonitorDispatcher(DatasmithDispatcher::FDatasmithDispatcher& Dispatcher)
{
    // 假设你通过某种方式访问到了任务池（实际为私有成员，此处为概念示例）
    // 核心是理解 ETaskState 的状态流转：UnTreated -> Processing -> Completed/Failed。

    // 在 Dispatcher.Process() 之后，任务由工作线程处理。
    // 你可以通过 Dispatcher.SetTaskState() 来查询（概念上）状态，但主要状态更新由内部完成。
    // 处理结果会反映在 CADFileToUnrealFileMap 等映射中，或通过消息日志（LogMessages）输出。

    // 检查是否所有任务都成功完成
    if (Dispatcher.IsOver())
    {
        UE_LOG(LogTemp, Log, TEXT("CAD导入任务全部完成。"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("CAD导入任务可能部分失败。"));
        // 可以记录 Dispatcher 内部的日志消息
        // Dispatcher.LogMessages(/* Some warnings array */);
    }
}
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何在虚幻引擎模块中使用 `DatasmithDispatcher`。

### MyCADImporter.h

```cpp
// MyCADImporter.h
#pragma once

#include "CoreMinimal.h"

class FMyCADImporter
{
public:
    void ImportCADFiles(const TArray<FString>& FilePaths);
};
```

### MyCADImporter.cpp

```cpp
// MyCADImporter.cpp
#include "MyCADImporter.h"
#include "DatasmithDispatcher.h"
#include "CADLibrary/Public/CADFileDescriptor.h"
#include "CADLibrary/Public/CADImportParameters.h"

void FMyCADImporter::ImportCADFiles(const TArray<FString>& FilePaths)
{
    if (FilePaths.Num() == 0)
    {
        return;
    }

    // 基本的导入参数设置
    CADLibrary::FImportParameters ImportParams;
    ImportParams.Mesher = CADLibrary::EMesher::SpatialGeometry;

    // 映射表将存储结果
    TMap<uint32, FString> FileMap;
    TMap<uint32, FString> GeomMap;
    FString CachePath = FPaths::ProjectSavedDir() / TEXT("CustomCADCache");

    // 创建调度器
    DatasmithDispatcher::FDatasmithDispatcher Dispatcher(ImportParams, CachePath, FileMap, GeomMap);

    // 为每个文件路径创建一个任务并添加到调度器
    for (const FString& FilePath : FilePaths)
    {
        CADLibrary::FFileDescriptor FileDesc(FilePath);
        // 使用哈希作为任务索引的一部分
        Dispatcher.AddTask(FileDesc, ImportParams.Mesher);
    }

    // 启动导入流程，使用外部工作进程（true）
    UE_LOG(LogTemp, Log, TEXT("开始导入 %d 个CAD文件..."), FilePaths.Num());
    Dispatcher.Process(true);

    // 轮询等待完成（在实际项目中，建议使用异步回调）
    while (!Dispatcher.IsOver())
    {
        FPlatformProcess::Sleep(0.5f);
    }

    UE_LOG(LogTemp, Log, TEXT("CAD导入完成。生成了 %d 个映射条目。"), FileMap.Num());

    // 此时，FileMap 和 GeomMap 中包含了中间缓存文件的路径。
    // 下一步通常是使用这些路径和原始文件描述符，在虚幻引擎中创建真正的 StaticMesh 资产。
    // 这部分逻辑通常由上层的 DatasmithCADTranslator 或自定义的资产处理逻辑完成。
}
```

## 模块依赖

从各模块的 `Build.cs` 文件分析，使用 `DatasmithCADImporter` 插件需要依赖以下外部库和模块。你的项目模块需要在 `Build.cs` 中添加相应的引用。

| 模块 | 用途 |
|---|---|
| `TechSoft` | `CADInterfaces` 模块的依赖。TechSoft 是一个商业 CAD 数据交换内核库，用于读取 CATIA, NX, SolidWorks 等多种 CAD 格式。**注意**：这是外部商业库，使用需要相应许可。 |
| `OpenNurbs6` | `DatasmithOpenNurbsTranslator` 模块的依赖。OpenNurbs 是开源库，用于读写 Rhino 3DM 文件格式。 |
| `DatasmithCADImporter` | 插件的核心聚合模块，引入其他所有子模块。 |
| `CADLibrary` | 提供通用的 CAD 数据结构（如 `FFileDescriptor`, `FImportParameters`）和工具函数。 |
| `DatasmithRuntime` | 插件可能依赖 Datasmith 的运行时库来创建资产和场景。 |

*特殊依赖说明*：该插件重度依赖第三方库（如 TechSoft, OpenNurbs）。确保你的虚幻引擎构建环境已正确配置这些库的二进制文件和头文件路径。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work  even if Alias 2027 is installed | 更新 Wire 格式翻译器逻辑，以兼容 Alias 2027 版本。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将第三方 CAD 内核库 TechSoft 更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本号，可能涉及缓存格式变化。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 解决函数类型转换警告在 MSVC 和 Clang 编译器之间的可移植性问题。 |

### 维护评价

- **活跃维护**：该插件在最近几天（2026年5月）仍有功能性更新（如支持新版 Alias、更新核心 TechSoft 库）和编译兼容性修复，表明它处于**活跃维护**状态。
- **企业级定位**：作为 Unreal Engine 的企业功能之一，其更新节奏可能与大型工业客户的反馈和合作伙伴软件更新同步。
- **推荐使用**：对于有明确 CAD 文件导入需求的工业可视化、建筑或汽车项目，**强烈推荐使用**。它是虚幻引擎官方支持的、最成熟的工业 CAD 导入解决方案。但需注意，该插件默认未启用 (`EnabledByDefault: false`)，需要在项目设置中手动启用，并且依赖外部商业库 TechSoft。
- **潜在限制**：对极新版本 CAD 格式的支持可能需要等待插件更新。大规模装配体导入的性能和稳定性仍需根据具体项目测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests)