# Interchange Framework

> The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.

| 属性 | 值 |
|---|---|
| 中文名 | 交换框架 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `InterchangeCommon` (Runtime), `InterchangeDispatcher` (Runtime), `InterchangeExport` (Runtime), `InterchangeFactoryNodes` (Runtime), `InterchangeImport` (Runtime), `InterchangeMessages` (Runtime), `InterchangeNodes` (Runtime), `InterchangeCommonParser` (Runtime), `InterchangeFbxParser` (Runtime), `GLTFCore` (Runtime), `InterchangePipelines` (Runtime), `Draco` (External) |
| 实验性 | 否 |
| 创建时间 | 2025-10-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime) | |

---

## 用途

Interchange Dispatcher 是 Interchange 框架的调度核心模块。它负责管理导入任务的队列、分发任务到外部 Worker 进程（`InterchangeWorker`），并通过 Socket 进行进程间通信（IPC）。其核心作用是**将耗时的文件解析（如 FBX、GLTF）从主线程/主进程中剥离，放入隔离的子进程执行**，从而：

- 避免第三方 SDK（如 FBX SDK）的线程安全问题
- 防止复杂解析造成编辑器卡顿
- 支持任务状态查询与结果异步回调

该模块是 Interchange 导入管道的**底层基础设施**，通常不需要用户直接调用，而是由 `InterchangeImport` 或 `InterchangePipelines` 高层模块间接使用。

---

## 使用场景

- **自定义导入器**：当实现新的文件格式时，可以利用 Dispatcher 创建对应的 Task，并启动 Worker 进程处理，无需关心跨进程通信细节。
- **批量资源导入**：可以同时启动多个 Worker 进程并行处理任务，提高导入吞吐量。
- **编辑器扩展**：若需要将资源预处理逻辑运行在独立进程中，可参考 Dispatcher 的 Worker 模式。

---

## 蓝图用法

`InterchangeDispatcher` 模块不提供任何 `BlueprintCallable` 或 `BlueprintReadWrite` 属性，所有 API 均为 C++ 内部使用。如需在蓝图中集成 Interchange 导入流程，请使用 `InterchangeImport` 模块提供的蓝图节点（如 `Import Asset` 等）。

---

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeDispatcher.h"
#include "InterchangeDispatcherTask.h"
#include "InterchangeDispatcherNetworking.h"
```

### 基本用法

以下示例展示如何创建一个 Dispatcher、添加任务并等待完成。

```cpp
// 来源：InterchangeDispatcher.h 及测试用例
using namespace UE::Interchange;

// 1. 创建 Dispatcher（指定结果文件夹和 Worker 数量）
FString ResultFolder = FPaths::ProjectSavedDir() / TEXT("InterchangeResults");
FInterchangeDispatcher Dispatcher(ResultFolder, 1);
Dispatcher.StartProcess();

// 2. 定义一个任务（JSON 描述）
FString TaskJson = TEXT("{\"CmdID\":\"LoadSource\",\"TranslatorID\":\"FBX\",\"SourceFilename\":\"/path/to/file.fbx\"}");
int32 TaskIndex = Dispatcher.AddTask(TaskJson);

// 3. 等待所有任务完成
Dispatcher.WaitAllTaskToCompleteExecution();

// 4. 获取任务状态
ETaskState State;
FString JsonResult;
TArray<FString> Messages;
Dispatcher.GetTaskState(TaskIndex, State, JsonResult, Messages);

// 5. 清理
Dispatcher.TerminateProcess();
```

### 进阶用法：自定义任务与委托回调

可以通过 `FJsonLoadSourceCmd` 及其子类（如 `FJsonFBXLoadSourceCmd`）构建带参 JSON，并注册任务完成委托。

```cpp
// 来源：InterchangeDispatcherTask.h, FBX/InterchangeDispatcherFBXTasks.h
using namespace UE::Interchange;

// 构建 FBX 源加载命令
FJsonFBXLoadSourceCmd FBXCmd(
    TEXT("FBX"),
    SourceFilePath,
    true,   // bConvertScene
    false,  // bForceFrontXAxis
    true,   // bConvertSceneUnit
    false   // bKeepFbxNamespace
);
FString JsonDesc = FBXCmd.ToJson();

// 注册任务完成回调
FInterchangeDispatcherTaskCompleted OnCompleted = [](int32 TaskIdx)
{
    UE_LOG(LogTemp, Log, TEXT("Task %d completed!"), TaskIdx);
};

int32 TaskIdx = Dispatcher.AddTask(JsonDesc, OnCompleted);
Dispatcher.StartProcess();
Dispatcher.WaitAllTaskToCompleteExecution();
```

### 网络通信层（低级）

`FNetworkNode` / `FNetworkServerNode` / `FNetworkClientNode` 提供了基于 TCP Socket 的通信基类，可用于自定义 IPC 协议。

```cpp
// 服务器端
FNetworkServerNode Server;
Server.Accept(TEXT("MyWorker"), 3.0);

// 发送命令
TArray<uint8> Buffer;
// ... 序列化 ICommand 到 Buffer
Server.SendMessage(Buffer, 1.0);

// 接收结果
TArray<uint8> OutBuffer;
Server.ReceiveMessage(OutBuffer, 5.0);
```

---

## Demo 示例

以下是一个完整的控制台应用示例（要求 Engine 编译时包含 Interchange 插件）。

**DispatcherDemo.h**

```cpp
#pragma once
#include "CoreMinimal.h"
#include "InterchangeDispatcher.h"
#include "InterchangeDispatcherTask.h"

class FDispatcherDemo
{
public:
    void Run();
};
```

**DispatcherDemo.cpp**

```cpp
#include "DispatcherDemo.h"
#include "Misc/Paths.h"
#include "InterchangeCommands.h"

using namespace UE::Interchange;

void FDispatcherDemo::Run()
{
    FString ResultFolder = FPaths::ProjectSavedDir() / TEXT("DemoResults");
    FInterchangeDispatcher Dispatcher(ResultFolder, 2); // 启动2个Worker

    Dispatcher.StartProcess();

    // 创建三个模拟任务
    for (int32 i = 0; i < 3; ++i)
    {
        FString Json = FString::Printf(TEXT("{\"CmdID\":\"TestTask\",\"Index\":%d}"), i);
        Dispatcher.AddTask(Json);
    }

    // 等待所有任务执行完毕
    Dispatcher.WaitAllTaskToCompleteExecution();

    // 检查结果
    for (int32 i = 0; i < 3; ++i)
    {
        ETaskState State;
        FString Result, Messages;
        Dispatcher.GetTaskState(i, State, Result, Messages);
        UE_LOG(LogTemp, Log, TEXT("Task %d State=%d Result=%s"), i, (int32)State, *Result);
    }

    Dispatcher.TerminateProcess();
}
```

**注意**：实际运行时需要 Worker 进程（`InterchangeWorker`）存在，该示例侧重于 API 使用方式。

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Sockets` | TCP Socket 通信（网络节点间传输命令） |
| `Json` | 任务描述与结果的 JSON 序列化 |
| `Projects` | 查找 Worker 进程路径（通过 `FModuleManager`） |
| `InterchangeCore` | 任务基类、命令定义（位于 `InterchangeCommon` 模块） |

编译目标需在 `Build.cs` 中加上：
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "InterchangeCore" });
PrivateDependencyModuleNames.AddRange(new string[] { "Sockets", "Json", "Projects" });
```

---

## 维护状态

### 近期更新

- 2025-12-18 `93cfc06e` Fixed editor hanging when level reimporting a file containing skeletal meshes
- 2025-10-23 `0158cf6a` [Interchange] Removing unintended LOD specialization from named LOD Groups.
- 2025-10-21 `63c630c0` [Interchange] Fixing missing animation sequence import for LevelSequence on StaticMesh imported with
- 2025-10-17 `765b3a10` Fixed compilation error with NonUnity InterchangeWorker
- 2025-10-17 `2c91170f` Replaced use of /InterchangeAssets/Materials/PhongSurfaceMaterial.PhongSurfaceMaterial with /Interch

### 维护评价

该模块创建于 2025-10-17，目前处于积极开发中。修复提交频繁，涉及崩溃、序列化和 LOD 问题。插件仍标记为「非实验性」但版本号仅为 `1.0`，说明其 API 尚未稳定。**推荐使用**，但需注意后续版本可能存在较大变动。建议在项目配置中锁定引擎版本。

---

## 相关链接

- [源码根目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime)
- [Interchange 官方文档](https://docs.unrealengine.com/5.7/en-US/interchange-framework/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Tests)