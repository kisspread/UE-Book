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
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

Datasmith CAD Importer 是一套企业级工具链，其核心功能远超一个简单的 CAD 文件导入器。它并非直接将 `.stp` 或 `.igs` 文件拖入引擎，而是作为 Datasmith 工作流的**后端处理引擎**，专注于解决将高精度、参数化的工业 CAD 数据（来自 SolidWorks, CATIA, Alias, NX, etc.）转换为 Unreal Engine 可用资产时遇到的核心挑战。

这个插件的存在是为了解决：
1.  **几何体转换**：将 B-Rep 等精确几何表示转换为 UE 可处理的网格（Mesh），支持高级细分曲面（如 `ParametricSurface`）。
2.  **数据结构解析**：解析复杂的 CAD 文件结构（如 `DatasmithPLMXMLTranslator` 处理 PLM XML），保留产品结构、元数据和装配关系。
3.  **多格式兼容**：通过 `DatasmithOpenNurbsTranslator`、`DatasmithWireTranslator` 及大量的 `WireInterface` 模块，支持以插件化的方式接入众多 CAD 格式版本。
4.  **大规模导入优化**：通过 `DatasmithDispatcher` 实现多进程/多线程的并行处理，将庞大的 CAD 文件分解为任务分发给外部“工人进程”处理，避免主编辑器卡顿或崩溃。

简单来说，它是 UE 中专业 CAD 数据导入流程的“大脑”和“调度中心”，确保数据从专业设计软件到实时引擎的旅程尽可能准确和高效。

## 使用场景

- **建筑、工程与施工（AEC）可视化**：你需要将 Revit 或 ArchiCAD 的 BIM 数据（通常通过 IFC 格式）导入 UE 用于建筑可视化或数字孪生。此插件提供了处理其复杂结构和几何体的底层能力。
- **汽车与工业设计审查**：设计师使用 Alias 或 CATIA 创建了 A 级曲面模型，你需要将其导入 UE 进行实时渲染和设计评审。`ParametricSurface` 模块专门处理此类高精度曲面。
- **产品配置器与培训系统**：你拥有大量来自 SolidWorks 或 NX 的装配体，需要将其转换为交互式 3D 产品配置器或培训模拟器。`DatasmithDispatcher` 确保了大量零件的高效处理。
- **需要支持特定 CAD 版本**：如果你的工作流依赖某个特定年份的 CAD 软件版本（如 CATIA V5-6R2017），该插件通过不同版本的 `WireInterface` 模块提供兼容性支持。

## 蓝图用法

基于提供的源码分析，`DatasmithDispatcher` 模块主要提供底层运行时任务调度和网络通信功能，其核心类（如 `FDatasmithDispatcher`, `FDatasmithWorkerHandler`）**并未暴露为 BlueprintCallable**。此插件的典型使用入口是通过 Datasmith 的导入 UI（如 `.udatasmith` 文件导入流程）或上层 C++ API 间接调用。

在蓝图层面，开发者通常不会直接操作此插件中的节点，而是与更高层的 `Datasmith` 或 `DatasmithContent` 模块交互（例如，配置导入设置或处理导入后的资产）。

## C++ 用法

此插件主要用于引擎内部和 Datasmith 工作流集成。直接使用其 API 通常涉及构建自定义导入管线或扩展现有格式支持。以下是基于源码的框架性用法示例。

### 头文件引入

由于插件包含多个模块，引用头文件取决于你需要使用的具体功能。例如：
```cpp
#include "DatasmithDispatcher.h"
#include "DatasmithDispatcherTask.h"
// 可能需要包含 CADLibrary 中的相关类型
#include "CADLibrary/Public/CADFileDescriptor.h"
#include "CADLibrary/Public/ImportParameters.h"
```

### 基本用法 (任务调度框架)

以下代码展示了如何使用 `DatasmithDispatcher` 创建任务队列并启动处理流程的框架。

*（概念性示例，基于 `Public/DatasmithDispatcher.h` 和 `Public/DatasmithDispatcherTask.h` 中的类定义）*

```cpp
#include "DatasmithDispatcher.h"
#include "CADLibrary/Public/ImportParameters.h"
#include "CADLibrary/Public/CADFileDescriptor.h"

void ImportCADFiles()
{
    // 1. 准备导入参数
    CADLibrary::FImportParameters ImportParams;
    // ... 配置 ImportParams，如缩放、公差等

    // 2. 准备文件映射表（用于存储 CAD 源文件到 Unreal 缓存文件的映射）
    TMap<uint32, FString> FileToSceneMap;
    TMap<uint32, FString> FileToGeomMap;

    // 3. 创建 Dispatcher 实例
    FString CacheDir = FPaths::ProjectSavedDir() / TEXT("CADCache");
    DatasmithDispatcher::FDatasmithDispatcher Dispatcher(ImportParams, CacheDir, FileToSceneMap, FileToGeomMap);

    // 4. 添加 CAD 文件任务
    // 假设我们有一个 .stp 文件描述
    CADLibrary::FFileDescriptor FileDesc;
    FileDesc.FilePath = TEXT("/path/to/model.step");
    // ... 设置其他属性
    CADLibrary::EMesher Mesher = CADLibrary::EMesher::Default; // 选择网格化器

    Dispatcher.AddTask(FileDesc, Mesher);

    // 5. 可选：配置并行 worker 数量
    Dispatcher.SetWorkerCount(4); // 使用 4 个外部进程并行处理

    // 6. 启动处理 (bWithProcessor=true 会启用外部进程)
    Dispatcher.Process(true);

    // 7. 检查是否完成
    while (!Dispatcher.IsOver())
    {
        // 可以在此处理其他逻辑或等待
        FPlatformProcess::Sleep(0.1f);
    }

    // 8. 处理完成，使用 FileToSceneMap 和 FileToGeomMap 中的结果
    // ... 将解析后的几何体和场景图数据转换为 UE StaticMesh 等资产
}
```

### 进阶用法 (自定义 Worker)

要创建一个自定义的“工人进程”（Worker），需要实现 `ICommand` 接口并建立网络通信。`DatasmithDispatcher` 模块已经封装了 `FNetworkServerNode` 和 `FNetworkClientNode` 用于主进程与工人进程间的通信。

```cpp
// 在自定义的工人进程项目中
#include "DatasmithCommands.h"
#include "DatasmithDispatcherNetworking.h"

void WorkerMain()
{
    // 连接到主进程（Dispatcher）提供的端口
    DatasmithDispatcher::FNetworkClientNode ClientNode;
    bool bConnected = ClientNode.Connect(TEXT("MyWorker"), ServerPort, 10.0);

    if (!bConnected) return;

    DatasmithDispatcher::FCommandQueue CommandQueue;
    CommandQueue.SetNetworkInterface(&ClientNode);

    // 1. 首先接收导入参数
    auto ParamsCommand = CommandQueue.GetNextCommand(60.0);
    if (ParamsCommand && ParamsCommand->GetType() == DatasmithDispatcher::ECommandId::ImportParams)
    {
        auto* ImportParamsCmd = static_cast<DatasmithDispatcher::FImportParametersCommand*>(ParamsCommand.Get());
        CADLibrary::FImportParameters ImportParams = ImportParamsCmd->ImportParameters;
        // 初始化自己的导入器...
    }

    // 2. 循环等待任务
    while (true)
    {
        auto Command = CommandQueue.GetNextCommand(60.0);
        if (!Command) break;

        if (Command->GetType() == DatasmithDispatcher::ECommandId::RunTask)
        {
            auto* RunTaskCmd = static_cast<DatasmithDispatcher::FRunTaskCommand*>(Command.Get());
            // 获取任务信息: RunTaskCmd->JobFileDescription, RunTaskCmd->Mesher, RunTaskCmd->JobIndex

            // **执行实际的 CAD 文件解析和转换**
            // ... 使用 CADInterfaces, CADTools 等模块处理文件

            // 3. 任务完成后，发送完成命令回主进程
            DatasmithDispatcher::FCompletedTaskCommand CompletedCmd;
            CompletedCmd.ProcessResult = CADLibrary::ECADParsingResult::Success;
            // ... 填充 ExternalReferences, SceneGraphFileName, GeomFileName

            CommandQueue.SendCommand(CompletedCmd, 5.0);
        }
        else if (Command->GetType() == DatasmithDispatcher::ECommandId::Terminate)
        {
            break; // 收到终止指令，退出循环
        }
    }
}
```

## Demo 示例

一个演示如何启动 `DatasmithDispatcher` 处理单个 CAD 文件的最小框架。

**MyCADImporter.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyCADImporter
{
public:
    void StartImport(const FString& CADFilePath);
};
```

**MyCADImporter.cpp**
```cpp
#include "MyCADImporter.h"
#include "DatasmithDispatcher.h"
#include "CADLibrary/Public/ImportParameters.h"
#include "CADLibrary/Public/CADFileDescriptor.h"

void FMyCADImporter::StartImport(const FString& CADFilePath)
{
    // 配置导入参数 (示例参数)
    CADLibrary::FImportParameters ImportParams;
    ImportParams.ScaleFactor = 100.0f; // 示例：将厘米转换为米
    // ... 更多参数设置

    // 创建文件映射缓存
    TMap<uint32, FString> SceneMap;
    TMap<uint32, FString> GeomMap;

    // 确定缓存路径
    const FString CacheDir = FPaths::ConvertRelativePathToFull(
        FPaths::ProjectSavedDir() / TEXT("DatasmithCADImporterCache"));

    // 创建 Dispatcher
    DatasmithDispatcher::FDatasmithDispatcher Dispatcher(ImportParams, CacheDir, SceneMap, GeomMap);

    // 创建文件描述符
    CADLibrary::FFileDescriptor FileDesc;
    FileDesc.FilePath = FPaths::ConvertRelativePathToFull(CADFilePath);

    // 添加任务 (假设使用默认网格化器)
    Dispatcher.AddTask(FileDesc, CADLibrary::EMesher::Default);

    // 设置 worker 数量 (使用所有可用核心，但至少留1个给主线程)
    Dispatcher.SetWorkerCount(FMath::Max(1, FPlatformMisc::NumberOfCores() - 1));

    UE_LOG(LogTemp, Log, TEXT("Starting CAD import for: %s"), *CADFilePath);

    // 启动处理 (true = 启用外部进程)
    Dispatcher.Process(true);

    // 简单轮询等待完成 (实际项目中应使用异步方式)
    while (!Dispatcher.IsOver())
    {
        FPlatformProcess::Sleep(0.5f);
    }

    UE_LOG(LogTemp, Log, TEXT("CAD import finished. %d scene files, %d geometry files generated."),
        SceneMap.Num(), GeomMap.Num());

    // 此时 SceneMap 和 GeomMap 中包含了中间结果文件路径。
    // 接下来通常需要另一个步骤（可能由上层 Datasmith 流程完成）将这些中间文件
    // 转换为最终的 UStaticMesh, USkeletalMesh 等资产。
}
```
**注意**：这是一个高度简化的演示。实际生产环境中，CAD 导入流程的初始化、错误处理、进度回调以及将中间文件（`.udsmesh`, `.udsscene`）转化为引擎资产的过程要复杂得多，通常由 `DatasmithCADTranslator` 等模块与 `Datasmith Runtime` 协同完成。

## 模块依赖

使用此插件时，你的项目或模块需要链接以下独特的依赖（除了标准 Core/Engine 模块外）：

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供对多种 CAD 格式（如 DWG, STEP, IGES）的底层解析支持，是 `CADInterfaces` 的核心依赖。 |
| `OpenNurbs6` | 提供对 Rhino 3DM 文件格式的解析支持，是 `DatasmithOpenNurbsTranslator` 的核心依赖。 |
| `CADLibrary` | 本插件的核心数据类型和工具库，定义了 `FFileDescriptor`, `FImportParameters`, `EMesher` 等关键结构。 |
| `DatasmithRuntime` | 上层 Datasmith 运行时，负责协调整个导入流程并最终将数据转换为 UE 资产。此插件的翻译器模块通常被其调用。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数引发的警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增强了 Wire 翻译器的兼容性，即使安装了 Alias 2027 也能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将核心的 CAD 解析库 TechSoft 更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 DatasmithCAD 的缓存版本格式。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器间可移植。 |

### 维护评价

- **创建时间**：插件于 2019 年 10 月创建，已有约 6 年历史。
- **活跃程度**：**非常活跃**。从 Git 历史看，在 2026 年 5 月仍有密集的更新，包括核心依赖库（TechSoft）升级、新版本 CAD 软件（Alias 2027）兼容性增强、编译警告修复以及缓存格式更新。这表明 Epic Games 持续投入资源维护此企业级插件，以跟上行业 CAD 软件的发展。
- **已知限制**：此插件默认**未启用**（`EnabledByDefault: false`），需要在项目设置或插件管理器中手动启用。其功能依赖第三方库（TechSoft, OpenNurbs）。
- **推荐使用**：**强烈推荐**。对于需要将专业 CAD 数据导入 UE 进行实时可视化的 AEC、汽车、工业制造等领域项目，这是官方提供的、功能最全面且持续维护的解决方案。尽管它是一个“老古董”插件，但其持续活跃的维护状态确保了其与最新技术栈的兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests) (如果存在)