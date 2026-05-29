# Control Flows

> Tool to cleanly implement Asynchronous Operations

| 属性 | 值 |
|---|---|
| 中文名 | 异步流程控制 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ControlFlows` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-08 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ControlFlows) | |

## 用途

ControlFlows 提供了一套**声明式、可链式调用的异步操作队列系统**，用于将复杂的异步/同步操作流程以清晰、可读的方式串联起来。

**解决的核心问题**：在 UE 项目中，一个完整业务流程往往需要分多步执行，涉及同步调用、异步等待、条件分支、并发执行、循环等。传统做法依赖大量回调嵌套或分散的 `Delegate` 绑定，导致代码可读性极差——需要不断 "Alt+G" 跳转才能理解一个流程的全貌。ControlFlows 将这些步骤以**队列方式线性排列**，每一步可以是同步函数、异步等待、子流程、分支、并发或循环，通过 `QueueStep` 自动根据函数签名推断类型。

**为什么存在**：该插件主要服务于 **LiveLinkHub**（`SupportedPrograms` 中指定），用于在 LiveLink 数据管线中编排复杂的异步数据获取、处理和分发流程。它是一个纯 C++ 运行时工具，不暴露任何蓝图 API。

## 使用场景

- 你需要按顺序执行多个异步步骤（如：连接设备 → 获取骨骼数据 → 应用校准） → 用 `QueueStep` / `QueueWait`
- 一个流程需要根据条件走不同分支 → 用 `BranchFlow` / `SwitchFlow`
- 需要同时执行多个并行子流程并等待全部完成 → 用 `ForkFlow` / `SplitFlow`
- 需要在流程中插入条件循环（while/do-while）→ 用 `Loop`
- 你希望将复杂的回调地狱重构为线性可读的流程 → 用 `FControlFlow` + `QueueStep`
- 你需要管理多个流程的生命周期（查找、停止、重置）→ 用 `FControlFlowStatics`

## 蓝图用法

该插件为**纯 C++ 模块**，不包含任何 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。所有 API 均为 C++ 模板和 SharedPtr 体系，无法在蓝图中使用。

## C++ 用法

### 头文件引入

```cpp
#include "ControlFlow.h"
#include "ControlFlowManager.h"
```

### 基本用法：队列式流程

最基础的用法是创建一个 `FControlFlow`，依次添加步骤，最后调用 `ExecuteFlow()`。

```cpp
// 来源: Source/ControlFlows/Public/ControlFlow.h 中的示例注释

struct FMyFlowClass : public TSharedFromThis<FMyFlowClass>
{
    typedef FMyFlowClass ThisClass;

    FMyFlowClass() : MyPurpose(MakeShared<FControlFlow>(TEXT("MyPurpose"))) {}

    void RunMyPurpose()
    {
        MyPurpose
            .QueueStep(this, &ThisClass::Construct)   // 同步函数，自动推断为 QueueFunction
            .QueueStep(this, &ThisClass::DoWork)       // 同步
            .QueueStep(this, &ThisClass::Destruct)     // 同步
            .ExecuteFlow();  // 必须调用，否则流程不会执行
    }

private:
    void Construct();
    void DoWork();
    void Destruct();

    TSharedRef<FControlFlow> MyPurpose;
};
```

### 进阶用法：异步等待（QueueWait）

当函数的第一个参数为 `FControlFlowNodeRef` 时，`QueueStep` 会自动推断为异步等待模式。流程会暂停，直到调用 `FlowHandle->ContinueFlow()`。

```cpp
void FMyFlowClass::FetchData(FControlFlowNodeRef FlowHandle)
{
    // 发起异步请求
    SomeAsyncCallback.BindLambda([FlowHandle]()
    {
        FlowHandle->ContinueFlow();  // 异步完成后继续流程
    });
}

// 使用：
MyPurpose
    .QueueStep(this, &ThisClass::FetchData)   // 自动识别为 QueueWait
    .QueueStep(this, &ThisClass::ProcessData)  // FetchData 完成后才执行
    .ExecuteFlow();
```

### 进阶用法：分支（BranchFlow）

```cpp
void FMyFlowClass::DecideBranch(TSharedRef<FControlFlowBranch> Branch)
{
    int32 Result = SomeCondition ? 0 : 1;

    Branch->AddOrGetBranch(0)
        .QueueStep(this, &ThisClass::BranchA_Step1)
        .QueueStep(this, &ThisClass::BranchA_Step2);

    Branch->AddOrGetBranch(1)
        .QueueStep(this, &ThisClass::BranchB_Step1);

    return Result;  // 返回要执行的分支 key
}

// 使用：
MyPurpose
    .BranchFlow(this, &ThisClass::DecideBranch)
    .QueueStep(this, &ThisClass::AfterBranch)
    .ExecuteFlow();
```

### 进阶用法：并发执行（ForkFlow）

```cpp
void FMyFlowClass::SetupConcurrent(TSharedRef<FConcurrentControlFlows> Concurrent)
{
    Concurrent->AddOrGetFlow(0)
        .QueueStep(this, &ThisClass::TaskA)
        .QueueStep(this, &ThisClass::TaskB);

    Concurrent->AddOrGetFlow(1)
        .QueueStep(this, &ThisClass::TaskC);
    // 两条流并发执行，全部完成后才继续主流程
}

// 使用：
MyPurpose
    .ForkFlow(this, &ThisClass::SetupConcurrent)
    .QueueStep(this, &ThisClass::AfterAllComplete)
    .ExecuteFlow();
```

### 进阶用法：条件循环（Loop）

```cpp
void FMyFlowClass::RunPollingLoop(TSharedRef<FConditionalLoop> Loop)
{
    // CheckConditionFirst: while(CHECK) { ... }
    // RunLoopFirst: do { ... } while(CHECK)
    Loop->RunLoopFirst()
        .QueueStep(this, &ThisClass::PollOnce);

    // 每次循环结束时返回条件
    return bShouldContinue ? EConditionalLoopResult::RunLoop : EConditionalLoopResult::LoopFinished;
}

// 使用：
MyPurpose
    .Loop(this, &ThisClass::RunPollingLoop)
    .QueueStep(this, &ThisClass::AfterLoop)
    .ExecuteFlow();
```

### 进阶用法：通过 FControlFlowStatics 管理流程生命周期

`FControlFlowStatics` 提供静态方法，通过 `OwningObject + FlowId` 管理流程的创建、查找、停止：

```cpp
// 来源: Source/ControlFlows/Public/ControlFlowManager.h

// 创建（如果已存在则 Reset）
FControlFlow& Flow = FControlFlowStatics::Create(this, TEXT("MyFlow"));
Flow.QueueStep(this, &ThisClass::Step1)
    .ExecuteFlow();

// 查找或创建
FControlFlow& Flow = FControlFlowStatics::FindOrCreate(this, TEXT("MyFlow"), /*bResetIfFound=*/true);

// 查询运行状态
bool bRunning = FControlFlowStatics::IsRunning(this, TEXT("MyFlow"));

// 停止流程
FControlFlowStatics::StopFlow(this, TEXT("MyFlow"));
```

## Demo 示例

以下是一个完整的最小示例，展示同步步骤、异步等待、分支和循环的组合使用：

**MyFlowExample.h**

```cpp
#pragma once

#include "ControlFlow.h"
#include "CoreMinimal.h"

class FMyFlowExample : public TSharedFromThis<FMyFlowExample>
{
public:
    FMyFlowExample();
    void Run();

private:
    // 同步步骤
    void Initialize();
    void Finalize();

    // 异步步骤
    void FetchDataAsync(FControlFlowNodeRef FlowHandle);

    // 分支决策
    int32 DecidePath(TSharedRef<FControlFlowBranch> Branch);

    // 分支内的步骤
    void PathA();
    void PathB();

    // 循环
    EConditionalLoopResult PollLoop(TSharedRef<FConditionalLoop> Loop);
    void PollOnce();

    TSharedRef<FControlFlow> MainFlow;
    int32 PollCounter = 0;
};
```

**MyFlowExample.cpp**

```cpp
#include "MyFlowExample.h"
#include "ControlFlowBranch.h"
#include "ControlFlowConditionalLoop.h"

FMyFlowExample::FMyFlowExample()
    : MainFlow(MakeShared<FControlFlow>(TEXT("MyFlowExample")))
{
}

void FMyFlowExample::Run()
{
    MainFlow
        .QueueStep(this, &FMyFlowExample::Initialize)
        .QueueStep(this, &FMyFlowExample::FetchDataAsync)       // 异步等待
        .BranchFlow(this, &FMyFlowExample::DecidePath)           // 条件分支
        .Loop(this, &FMyFlowExample::PollLoop)                   // 条件循环
        .QueueStep(this, &FMyFlowExample::Finalize)
        .ExecuteFlow();
}

void FMyFlowExample::Initialize()
{
    UE_LOG(LogTemp, Log, TEXT("Flow initialized"));
}

void FMyFlowExample::FetchDataAsync(FControlFlowNodeRef FlowHandle)
{
    UE_LOG(LogTemp, Log, TEXT("Fetching data asynchronously..."));
    // 模拟异步：下一帧继续
    AsyncTask(ENamedThreads::GameThread, [FlowHandle]()
    {
        UE_LOG(LogTemp, Log, TEXT("Data fetched, continuing flow"));
        FlowHandle->ContinueFlow();
    });
}

int32 FMyFlowExample::DecidePath(TSharedRef<FControlFlowBranch> Branch)
{
    Branch->AddOrGetBranch(0)
        .QueueStep(this, &FMyFlowExample::PathA);

    Branch->AddOrGetBranch(1)
        .QueueStep(this, &FMyFlowExample::PathB);

    return 0; // 选择 Path A
}

void FMyFlowExample::PathA()
{
    UE_LOG(LogTemp, Log, TEXT("Taking path A"));
}

void FMyFlowExample::PathB()
{
    UE_LOG(LogTemp, Log, TEXT("Taking path B"));
}

EConditionalLoopResult FMyFlowExample::PollLoop(TSharedRef<FConditionalLoop> Loop)
{
    Loop->RunLoopFirst()
        .QueueStep(this, &FMyFlowExample::PollOnce);

    PollCounter++;
    return PollCounter < 3
        ? EConditionalLoopResult::RunLoop
        : EConditionalLoopResult::LoopFinished;
}

void FMyFlowExample::PollOnce()
{
    UE_LOG(LogTemp, Log, TEXT("Polling iteration %d"), PollCounter);
}

void FMyFlowExample::Finalize()
{
    UE_LOG(LogTemp, Log, TEXT("Flow completed!"));
}
```

## 模块依赖

该插件的 `ControlFlows.Build.cs` 仅依赖标准 Core/Engine 模块，无特殊依赖。

无特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到 UE_LOGF 新格式 |
| 2026-02-06 | `2e5bdf72` | [Backout] - CL50512664 | 回退一次提交，恢复之前的代码状态 |
| 2026-02-04 | `3d85750f` | [ControlFlow] Make sure current node is valid during step complete notification | 修复步骤完成通知时当前节点可能无效的运行时 bug |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 全引擎析构函数语法现代化 |
| 2025-06-26 | `a358aec2` | [ControlFlows] Cache Parent.Pin() early to shorten call stacks, eliminate weak-ptr race window & ext | 缓存 Parent 弱指针避免竞态，缩短调用栈 |

### 维护评价

ControlFlows 创建于 2021 年 9 月，至今约 5 年。从 git 历史看，该插件**持续获得维护**：

- **2025-2026 年仍有实质性修复**：包括运行时 bug 修复（节点有效性检查、弱指针竞态）和代码现代化（析构函数规范化、日志宏迁移）
- **回退操作**说明仍有活跃开发和问题修复过程
- 该插件虽然标记为实验性路径（`Experimental/`），但 `.uplugin` 中 `IsBetaVersion` 和 `IsExperimentalVersion` 均为 `false`
- `Installed: false` 表示**需要手动启用**才能使用

**推荐使用**：适合需要在 C++ 中编排复杂异步流程的项目，特别是与 LiveLink 管线集成的场景。注意这是一个纯 C++ 工具，无蓝图支持，且处于 Experimental 目录下，未来可能有 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ControlFlows)
- [官方文档]()（无）