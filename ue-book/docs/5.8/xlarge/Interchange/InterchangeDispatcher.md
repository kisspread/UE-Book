# Interchange Dispatcher

> The Interchange Dispatcher module handles task scheduling, worker process management, and inter-process communication for the Interchange Framework. It orchestrates the parsing of asset files (e.g., FBX, GLTF) by delegating work to external "InterchangeWorker" processes, enabling parallel and fault-tolerant import/export operations.

| 属性 | 值 |
|---|---|
| 中文名 | 交换调度器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeDispatcher` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-01-27 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime/Source/Dispatcher) | |

## 用途

`InterchangeDispatcher` 是 Interchange 框架的核心调度引擎。它解决的核心问题是**资产导入/导出的并行化与进程隔离**。

为什么存在？
1.  **并行处理**：资产解析（如 FBX、GLTF 解析）是 CPU 密集型操作。Dispatcher 将任务分发给多个独立的 `InterchangeWorker` 子进程并行执行，充分利用多核 CPU，显著提升大型项目或批量导入的效率。
2.  **稳定性与隔离**：将解析工作放在子进程中运行，即使某个文件的解析导致崩溃，也只会使该 Worker 进程终止，而不会影响主编辑器进程，提高了编辑器的稳定性。
3.  **可扩展性**：Dispatcher 定义了标准化的任务（`FTask`）和通信协议（`ICommand`），使得为新的文件格式添加解析支持（只需实现一个新的 Translator 和 Worker 即可）变得清晰和模块化。

## 使用场景

-   **游戏项目资产导入**：在导入包含数百个 FBX 模型、材质和动画的大型资产包时，Dispatcher 会自动启动多个 Worker 进程，将任务并行化，缩短等待时间。
-   **构建管线自动化**：在命令行工具或构建脚本中调用 Interchange 进行批量资产导出时，Dispatcher 管理的进程池可以高效完成任务。
-   **自定义资产格式支持**：如果你开发了新的 3D 格式（如 `.myformat`），需要在 Unreal 中导入，你可以实现一个对应的 Translator 和 Worker，Dispatcher 会无缝地将其纳入任务调度体系。

## 蓝图用法

`InterchangeDispatcher` 模块本身是一个底层 C++ 调度模块，不直接暴露给蓝图。它的功能被上层的 `InterchangeImport` 和 `InterchangeExport` 模块封装，通过 `UInterchangePipelineBase` 和 `UInterchangeTranslatorBase` 等类在蓝图中体现。

### 核心节点（来自上层封装）

你通常通过以下蓝图可调用的资产导入/导出流程间接使用 Dispatcher：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Import Scene` / `Import Asset` | 发起资产导入请求，内部会由 Dispatcher 调度任务。 | `UInterchangeBlueprintPipelineBase` 等 |
| `Export To File` | 发起资产导出请求，内部会由 Dispatcher 调度任务。 | `UInterchangeBlueprintPipelineBase` 等 |
| `Set Pipeline` | 为导入/导出操作指定数据处理管线（Pipeline），管线定义了如何处理 Dispatcher 返回的解析结果。 | `UInterchangeFactoryBase` |

**说明**：在蓝图中，你主要与 `Pipeline` 和 `Translator` 类交互，配置导入/导出选项。Dispatcher 的任务调度、进程管理完全在后台自动进行，对蓝图用户透明。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeDispatcher.h"
#include "InterchangeDispatcherTask.h"
```

### 基本用法（从源码提取）

使用 Dispatcher 的基本流程是：创建实例、添加任务、启动处理、等待完成。

```cpp
// 来源：Engine/Plugins/Interchange/Runtime/Source/Dispatcher/Public/InterchangeDispatcher.h
void ExampleUseDispatcher()
{
    // 1. 指定结果文件的存储目录，并创建 Dispatcher 实例
    // WorkerCount=1 表示启动1个外部Worker进程。设为0则Dispatcher自动决定数量。
    FString ResultFolder = FPaths::ProjectIntermediateDir() / TEXT("InterchangeResults");
    UE::Interchange::FInterchangeDispatcher Dispatcher(ResultFolder, /*WorkerCount=*/2);

    // 2. 创建一个任务描述。通常由 Translator 生成。
    // 这里用一个简化的 FBX 加载任务 JSON 作为示例。
    UE::Interchange::FJsonFBXLoadSourceCmd LoadCmd(
        TEXT("MyFBXTranslator"), // Translator ID
        TEXT("C:/Assets/Model.fbx"), // 源文件路径
        true, // bConvertScene
        false, // bForceFrontXAxis
        true, // bConvertSceneUnit
        false, // bKeepFbxNamespace
        false // bConsiderClusterBeforePoseForMeshBindPose
    );
    FString TaskJson = LoadCmd.ToJson();

    // 3. 添加任务到 Dispatcher。可以绑定一个回调。
    int32 TaskIndex = Dispatcher.AddTask(TaskJson, FInterchangeDispatcherTaskCompleted::CreateLambda([](int32 Index){
        UE_LOG(LogTemp, Log, TEXT("Task %d completed!"), Index);
    }));

    // 4. 启动 Dispatcher，它会开始连接 Worker 进程并分发任务
    Dispatcher.StartProcess();

    // 5. 主线程可以继续做其他事情，或者等待所有任务完成
    // 注意：在实际的游戏线程中，应避免阻塞，可以通过轮询 Dispatcher.IsOver() 或依赖回调
    Dispatcher.WaitAllTaskToCompleteExecution();

    // 6. 查询特定任务的结果
    UE::Interchange::ETaskState State;
    FString JsonResult;
    TArray<FString> Messages;
    Dispatcher.GetTaskState(TaskIndex, State, JsonResult, Messages);

    if (State == UE::Interchange::ETaskState::ProcessOk)
    {
        // 使用解析结果（JsonResult）创建资产工厂节点等
        UE_LOG(LogTemp, Log, TEXT("Task %d succeeded, result JSON length: %d"), TaskIndex, JsonResult.Len());
    }
    else
    {
        // 处理错误
        UE_LOG(LogTemp, Error, TEXT("Task %d failed."), TaskIndex);
    }
}
```

### 进阶用法

可以继承 `FInterchangeDispatcher` 来实现自定义的 Worker 管理策略，或者监听 Worker 进程事件。

```cpp
// 来源：Engine/Plugins/Interchange/Runtime/Source/Dispatcher/Public/InterchangeDispatcher.h
class FMyCustomDispatcher : public UE::Interchange::FInterchangeDispatcher
{
public:
    using FInterchangeDispatcher::FInterchangeDispatcher;

    // 重写以获取 Worker 应用程序的路径
    virtual const TCHAR* GetWorkerApplicationName() override
    {
        return TEXT("MyCustomInterchangeWorker");
    }

    // 重写以在进程异常终止时进行自定义处理
    virtual void StopProcess(bool bBlockUntilTerminated) override
    {
        // 自定义清理逻辑
        UE_LOG(LogMyCategory, Warning, TEXT("Custom Dispatcher is stopping workers..."));
        FInterchangeDispatcher::StopProcess(bBlockUntilTerminated);
    }
};
```

## Demo 示例

一个最小可编译示例，展示如何使用 `InterchangeDispatcher` 模拟一个任务的提交和完成。

**MyDispatcherDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "InterchangeDispatcher.h"

class FMyDispatcherDemo
{
public:
    static void RunDemo();

private:
    static void OnTaskCompleted(int32 TaskIndex);
};
```

**MyDispatcherDemo.cpp**
```cpp
#include "MyDispatcherDemo.h"
#include "InterchangeDispatcherTask.h"
#include "FBX/InterchangeDispatcherFBXTasks.h"

void FMyDispatcherDemo::RunDemo()
{
    // 使用项目中间目录作为结果文件夹
    FString ResultFolder = FPaths::ProjectIntermediateDir() / TEXT("InterchangeDispatcherDemo");
    IFileManager::Get().MakeDirectory(*ResultFolder);

    // 创建 Dispatcher（使用1个 Worker）
    UE::Interchange::FInterchangeDispatcher Dispatcher(ResultFolder, 1);

    // 构建一个 FBX 加载任务的 JSON 命令
    UE::Interchange::FJsonFBXLoadSourceCmd FbxCmd(
        TEXT("DemoFBXTranslator"),
        TEXT("C:/TestAssets/Cube.fbx"),
        true, false, true, false, false
    );
    FString TaskJson = FbxCmd.ToJson();

    // 添加任务，并绑定回调
    int32 TaskIdx = Dispatcher.AddTask(TaskJson,
        FInterchangeDispatcherTaskCompleted::CreateStatic(&FMyDispatcherDemo::OnTaskCompleted));

    // 启动处理
    Dispatcher.StartProcess();

    // 在实际应用中，这里应该是一个非阻塞的循环，检查 Dispatcher 状态。
    // 为示例简洁，直接等待完成。
    Dispatcher.WaitAllTaskToCompleteExecution();

    // 查询结果
    UE::Interchange::ETaskState State;
    FString Result;
    TArray<FString> Msgs;
    Dispatcher.GetTaskState(TaskIdx, State, Result, Msgs);

    if (State == UE::Interchange::ETaskState::ProcessOk)
    {
        UE_LOG(LogTemp, Display, TEXT("Demo Succeeded! Result JSON:\n%s"), *Result.Left(500)); // 只打印前500字符
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Demo Failed. Messages:"));
        for (const FString& Msg : Msgs)
        {
            UE_LOG(LogTemp, Error, TEXT("  %s"), *Msg);
        }
    }

    // Dispatcher 在析构时会自动终止所有 Worker 进程
}

void FMyDispatcherDemo::OnTaskCompleted(int32 TaskIndex)
{
    UE_LOG(LogTemp, Display, TEXT("Dispatcher callback: Task %d has completed."), TaskIndex);
}
```

## 模块依赖

从模块命名和头文件包含关系推断，`InterchangeDispatcher` 模块依赖以下核心模块。要使用此模块，你的 `Build.cs` 需要包含这些依赖：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、字符串、日志 |
| `CoreUObject` | 对象系统，用于 `UObject` 交互（如命令序列化） |
| `Engine` | 引擎核心，访问 `FSocket` 等网络功能 |
| `Sockets` | 底层的套接字网络通信 |
| `InterchangeCommon` | 提供共享的 Interchange 类型和工具 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `61d0e791` | USD Pregen: Implement tracking of Skeleton and PhysicsAssets | 为USD预生成实现了骨骼和物理资产跟踪功能。 |
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复了针对UE 5.8版本的本地化警告。 |
| 2026-05-22 | `8fdd3a89` | [Interchange] Reset existing LODModels for reimport, so that Bone bindings and mappings are updated | [Interchange] 在重新导入时重置已存在的LOD模型，以便更新骨骼绑定和映射。 |
| 2026-05-22 | `3cfa4417` | Reinstated the uFBX parser as experimental | 恢复了实验性的 uFBX 解析器。 |
| 2026-05-19 | `755f95d4` | Interchange: Fix crash by protecting against nullptr objects in the list of imported objects. | Interchange：通过防止导入对象列表中的空指针对象来修复崩溃。 |

### 维护评价

`InterchangeDispatcher` 模块是 Interchange 框架的活跃核心组件。

-   **活跃维护**：从 Git 历史看，最近几个月持续有功能性更新和 Bug 修复（如崩溃修复、新功能集成、解析器恢复），表明其处于**积极维护和开发**中。
-   **稳定性**：代码中包含对崩溃、连接失败等异常情况的处理逻辑（如 `FInterchangeWorkerHandler::EWorkerErrorState`），并且有版本兼容性检查（`DispatcherCommandVersion`），体现了对稳定性的重视。
-   **成熟度**：作为 Epic Games 官方主推的下一代资产导入导出框架的核心部分，其设计（任务队列、进程池、网络通信）是成熟和专业的。
-   **推荐使用**：**强烈推荐**使用。它是 Unreal Engine 未来资产处理的标准方向，性能优越，稳定性好。如果你需要处理复杂的资产导入导出，或者开发自定义的资产格式支持，基于 Interchange 和 Dispatcher 进行开发是最佳选择。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime/Source/Dispatcher)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/interchange-framework-in-unreal-engine/)（Interchange 框架整体文档）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime/Tests)