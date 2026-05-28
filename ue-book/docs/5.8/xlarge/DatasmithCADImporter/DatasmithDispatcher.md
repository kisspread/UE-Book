# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD 文件导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

DatasmithCADImporter 是 UE5 的 CAD 文件导入基础设施，用于将各种工业 CAD 格式（如 STEP、IGES、JT、CATIA、SolidWorks、Rhino 等）转换为 UE 可用的几何体和场景数据。

该插件的核心设计思路是**多进程并行导入**：由于 CAD 文件解析计算量极大且第三方 CAD 库（如 TechSoft、OpenNurbs）可能存在稳定性问题，插件采用"分发器 + 外部工作进程"架构。主引擎进程通过 TCP Socket 将 CAD 文件解析任务分发给独立的外部子进程，子进程崩溃不会影响主引擎，且可以自动重启重试。

**默认未启用**：这是一个企业级功能插件，需要在项目设置中手动启用，且依赖外部商业 CAD 库（TechSoft）。

## 使用场景

- 你在做一个建筑可视化项目，需要导入 Revit/BIM 模型 → 通过 Datasmith 流水线自动调用此插件解析 CAD 几何
- 你在做一个工业数字孪生项目，需要导入 CATIA/NX/SolidWorks 的 3D 模型 → 启用此插件后通过 Datasmith Importer 导入
- 你需要导入 Rhino（.3dm）文件 → 依赖 `DatasmithOpenNurbsTranslator` 模块
- 你需要导入 PLMXML 格式的工程数据 → 依赖 `DatasmithPLMXMLTranslator` 模块
- 你需要处理大型 CAD 装配体（数百个零件）→ 此插件的多进程分发器会自动并行解析，显著加速导入

## 蓝图用法

该插件不暴露蓝图 API。所有功能在 Datasmith 导入流水线内部自动调用，用户通过 Datasmith Importer 的标准导入流程触发，无需直接操作蓝图节点。

## C++ 用法

DatasmithDispatcher 模块主要作为内部基础设施被 Datasmith 导入流水线调用。以下是基于源码的关键用法说明。

### 头文件引入

```cpp
#include "DatasmithDispatcher.h"
#include "DatasmithCommands.h"
#include "DatasmithDispatcherNetworking.h"
#include "DatasmithWorkerHandler.h"
#include "DatasmithDispatcherTask.h"
```

### 基本用法：创建分发器并处理任务

基于 `Public/DatasmithDispatcher.h` 中 `FDatasmithDispatcher` 的接口：

```cpp
#include "DatasmithDispatcher.h"

// 准备导入参数和缓存路径
CADLibrary::FImportParameters ImportParameters;
FString CacheDir = FPaths::ProjectSavedDir() / TEXT("DatasmithCADCache");

// 用于存储 CAD 文件到 Unreal 缓存文件的映射
TMap<uint32, FString> CADFileToUnrealFileMap;
TMap<uint32, FString> CADFileToUnrealGeomMap;

// 创建分发器实例
DatasmithDispatcher::FDatasmithDispatcher Dispatcher(
    ImportParameters,
    CacheDir,
    CADFileToUnrealFileMap,
    CADFileToUnrealGeomMap
);

// 添加 CAD 文件任务
CADLibrary::FFileDescriptor FileDesc(TEXT("/path/to/model.step"));
Dispatcher.AddTask(FileDesc, CADLibrary::EMesher::Default);

// 使用外部进程方式处理（默认行为）
Dispatcher.Process(/*bWithProcessor=*/ true);

// 等待所有任务完成
while (!Dispatcher.IsOver())
{
    FPlatformProcess::Sleep(0.1f);
}
```

### 进阶用法：自定义工作进程数量

```cpp
// 设置工作进程数量（默认由 CADLibrary::GMaxImportThreads 控制）
Dispatcher.SetWorkerCount(4);
```

### 进阶用法：命令通信协议

分发器通过序列化的命令对象与工作进程通信。可用的命令类型定义在 `DatasmithCommands.h` 中：

```cpp
using namespace DatasmithDispatcher;

// 创建命令
TSharedPtr<ICommand> PingCmd = CreateCommand(ECommandId::Ping);
TSharedPtr<ICommand> TerminateCmd = CreateCommand(ECommandId::Terminate);

// 序列化命令为字节缓冲（用于 Socket 传输）
TArray<uint8> Buffer;
SerializeCommand(*PingCmd, Buffer);

// 从字节缓冲反序列化
TSharedPtr<ICommand> Received = DeserializeCommand(Buffer);
if (Received.IsValid() && Received->GetType() == ECommandId::RunTask)
{
    FRunTaskCommand* RunTask = static_cast<FRunTaskCommand*>(Received.Get());
    // RunTask->JobFileDescription 包含 CAD 文件描述
    // RunTask->Mesher 指定网格化方式
}
```

### 进阶用法：网络通信层

如果需要构建类似的 IPC 通信，可以复用 `FNetworkServerNode` / `FNetworkClientNode`：

```cpp
// 服务端（主引擎进程）
DatasmithDispatcher::FNetworkServerNode Server;
int32 Port = Server.GetListeningPort();
// 等待客户端连接
bool bConnected = Server.Accept(TEXT("CADWorker"), 6.0);

// 客户端（工作进程）
DatasmithDispatcher::FNetworkClientNode Client;
bool bOk = Client.Connect(TEXT("CADWorker"), Port, 3.0);

// 使用 FCommandQueue 管理命令收发
DatasmithDispatcher::FCommandQueue CommandQueue;
CommandQueue.SetNetworkInterface(&Server);
CommandQueue.SendCommand(*PingCmd, 1.0);
TSharedPtr<ICommand> Response = CommandQueue.GetNextCommand(1.0);
```

## 模块依赖

从各模块 Build.cs 分析的特殊依赖：

| 模块 | 用途 |
|---|---|
| `TechSoft` | 第三方商业 CAD 内核库，用于解析 STEP/IGES/JT/CATIA 等工业格式（通过 CADInterfaces 模块依赖） |
| `OpenNurbs6` | Rhino 的开源 NURBS 库，用于解析 .3dm 文件（通过 DatasmithOpenNurbsTranslator 模块依赖） |
| `DatasmithContent` | Datasmith 内容资产类型定义 |
| `DatasmithCore` | Datasmith 核心数据结构 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的截断警告 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 兼容 Alias 2027 已安装时的 Wire 翻译器工作 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 升级 TechSoft CAD 库到 2026.3 版本 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新 DatasmithCAD 缓存版本格式 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 提升 MSVC 和 Clang 编译器间的类型转换警告兼容性 |

### 维护评价

- **活跃维护**：最近一次更新在 2026-05-13，更新非常频繁
- 该插件是 Epic 企业级 Datasmith 工具链的核心组成部分，持续获得技术更新（TechSoft 库升级、新 CAD 格式支持）
- 多版本 WireInterface 模块的维护模式说明 Epic 随 CAD 库版本迭代持续适配
- **推荐使用**：如果你需要在 UE5 中导入工业 CAD 文件，这是官方唯一支持的方案。但注意需要手动启用，且可能需要额外的 CAD 库许可证（TechSoft）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)