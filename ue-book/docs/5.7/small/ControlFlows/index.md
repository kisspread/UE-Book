# ControlFlows

> Tool to cleanly implement Asynchronous Operations

| 属性 | 值 |
|---|---|
| 中文名 | 异步操作编排 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无（纯代码插件） |
| 模块 | `ControlFlows` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-11-01 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ControlFlows) | |

---

## 用途

**ControlFlows 解决的问题**：在 UE5 C++ 游戏中，经常需要编排一系列异步操作（如加载资源、等待动画、网络请求、UI 过渡等）。传统做法往往导致回调嵌套、状态分散、代码难以阅读和维护。ControlFlows 提供了一个轻量级的流式任务队列系统，通过链式调用（`QueueStep` / `QueueWait` / `QueueControlFlow` 等）将同步和异步步骤组织成线性流程，并支持条件分支、并发分流、循环等控制结构，从而大幅提高代码的可读性和可维护性。

**为什么存在？**：UE 自带的 `Async` 系统和 `Latent` 函数仅能处理简单等待；复杂的游戏逻辑（如新手引导、Boss 战阶段）需要更高级的编排工具。ControlFlows 不是蓝图节点，而是纯 C++ 库，专为需要高度可控和类型安全的游戏逻辑开发者设计。

---

## 使用场景

- **游戏流程管理器**：如加载 - 初始化 - 播放开场动画 - 显示主菜单 - 进入关卡，每一步都有异步等待和条件判断。
- **Boss 战阶段脚本**：A 阶段攻击 → 等待 Boss 血量 < 50% → B 阶段（可并行召唤小怪）→ 获胜/失败处理。
- **用户交互引导**：显示提示 → 等待玩家输入 → 执行反馈 → 下一步，全部线性但可随时取消。
- **网络请求序列**：认证 → 获取用户数据 → 缓存 → 更新 UI，每一步需要等待响应。

---

## 蓝图用法

**该插件未提供蓝图节点。** `FControlFlow` 及其相关类均为纯 C++ 类（未标记 `UCLASS`），BlueprintCallable 函数不存在。

**如何钩连蓝图？**：建议在 C++ 中编写一个封装蓝图函数库，将 `FControlFlow` 的创建、执行、完成回调暴露为蓝图节点。例如定义一个 `UAsyncAction_StartControlFlow`。本插件本身不包含此类封装。

---

## C++ 用法

### 头文件引入

```cpp
#include "ControlFlow.h"
#include "ControlFlowManager.h"   // 若使用 FControlFlowStatics
#include "ControlFlowBranch.h"
#include "ControlFlowConcurrency.h"
#include "ControlFlowConditionalLoop.h"
```

### 基本用法

#### 1. 创建并运行一个简单顺序流

```cpp
// Source: ControlFlow.h 注释中的 Example Class 改编

struct FMyFlowClass : public TSharedFromThis<FMyFlowClass>
{
    using ThisClass = FMyFlowClass;

    FMyFlowClass()
        : MyPurpose(MakeShared<FControlFlow>(TEXT("MyPurpose")))
    {}

    void Run()
    {
        // 链式添加步骤：同步函数、异步等待、子流
        MyPurpose
            .QueueStep(this, &ThisClass::DoStepA)           // 普通同步函数
            .QueueStep(this, &ThisClass::DoWaitStep)         // 需要手动 ContinueFlow 的异步函数
            .QueueControlFlow(this, &ThisClass::DoSubFlow)   // 使用子流
            .QueueFlowTermination();                         // 标记结束
    }

    void DoStepA()
    {
        UE_LOG(LogTemp, Log, TEXT("Step A executed"));
    }

    void DoWaitStep(FControlFlowNodeRef FlowHandle)
    {
        // 模拟异步操作，例如 2 秒后继续
        FTimerHandle TimerHandle;
        GWorld->GetTimerManager().SetTimer(TimerHandle, [FlowHandle]()
        {
            FlowHandle->ContinueFlow();   // 必须调用，否则流挂起
        }, 2.0f, false);
    }

    void DoSubFlow(TSharedRef<FControlFlow> SubFlow)
    {
        SubFlow->QueueStep(this, &ThisClass::DoStepSub);
        SubFlow->QueueFlowEnd();
    }

    void DoStepSub()
    {
        UE_LOG(LogTemp, Log, TEXT("Sub-step executed"));
    }

private:
    TSharedRef<FControlFlow> MyPurpose;
};

// 使用方式
auto Instance = MakeShared<FMyFlowClass>();
Instance->Run();
```

#### 2. 使用 FControlFlowStatics 进行生命周期管理

```cpp
// 在类内部创建并管理流（自动销毁）

UCLASS()
class UMyManager : public UObject
{
    GENERATED_BODY()
public:
    void StartFlow()
    {
        FControlFlow& Flow = FControlFlowStatics::Create(this, TEXT("MyFlowID"));
        Flow
            .QueueStep(this, &UMyManager::Step1)
            .QueueStep(this, &UMyManager::Step2)
            .QueueFlowTermination();
    }

    void Step1() { /* ... */ }
    void Step2() { /* ... */ }
};
```

### 进阶用法

#### 分支流程

```cpp
/*
 * BranchFlow: 根据返回值选择分支 (int32 -> 0, 1, 2...)
 */
Flow
    .QueueStep(this, &ThisClass::DetermineBranch)       // 返回 int32
    .BranchFlow([this](TSharedRef<FControlFlowBranch> Branch)
    {
        Branch->AddOrGetBranch(0, TEXT("BranchA"))
            .QueueStep(this, &ThisClass::BranchA_Step1)
            .QueueFlowEnd();

        Branch->AddOrGetBranch(1, TEXT("BranchB"))
            .QueueStep(this, &ThisClass::BranchB_Step1)
            .QueueFlowEnd();
    })
    .QueueFlowTermination();
```

#### 并发执行

```cpp
/*
 * ForkFlow: 多个子流同时执行，全部完成后才继续主流程
 * EConcurrentExecution::Default 按顺序但可设置 Random / Parallel
 */
Flow
    .ForkFlow([this](TSharedRef<FConcurrentControlFlows> Fork)
    {
        Fork->AddOrGetProng(0, TEXT("Prong1"))
            .QueueStep(this, &ThisClass::Prong1_Step);

        Fork->AddOrGetProng(1, TEXT("Prong2"))
            .QueueStep(this, &ThisClass::Prong2_Step);
    })
    .QueueFlowTermination();
```

#### 条件循环

```cpp
/*
 * Loop: 使用 FConditionalLoop
 * RunLoopFirst() / CheckConditionFirst() 控制循环类型
 * Lambda 返回 EConditionalLoopResult::RunLoop 继续循环，LoopFinished 结束
 */
Flow
    .Loop([this](TSharedRef<FConditionalLoop> Loop)
    {
        Loop->CheckConditionFirst()
            .QueueStep(this, &ThisClass::DoLoopBody)
            .QueueFlowTermination();   // 必须终止内部流
    })
    .QueueFlowTermination();
```

---

## Demo 示例

以下示例展示一个最小化的完整类，可在任何 Actor 或 UObject 中使用。

```cpp
// MyFlowActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ControlFlow.h"
#include "MyFlowActor.generated.h"

UCLASS()
class AMYFLOWACTOR : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    void StartFlow();

    // 步骤回调
    void StepA();
    void StepB(FControlFlowNodeRef FlowHandle);  // 异步等待
    void StepC(TSharedRef<FControlFlow> SubFlow);
    void StepD();
    void FlowCompleted();

private:
    TSharedPtr<FControlFlow> Flow;
};
```

```cpp
// MyFlowActor.cpp
#include "MyFlowActor.h"
#include "ControlFlowTask.h"

void AMYFLOWACTOR::BeginPlay()
{
    Super::BeginPlay();
    StartFlow();
}

void AMYFLOWACTOR::StartFlow()
{
    Flow = MakeShared<FControlFlow>(TEXT("MyDemoFlow"));
    Flow
        .QueueStep(this, &ThisClass::StepA)
        .QueueStep(this, &ThisClass::StepB)   // 异步等待
        .QueueControlFlow(this, &ThisClass::StepC)
        .QueueStep(this, &ThisClass::StepD)
        .QueueFlowTermination();               // 必须调用，否则流不会启动

    Flow->OnComplete().BindUObject(this, &ThisClass::FlowCompleted);
    Flow->ExecuteFlow();
}

void AMYFLOWACTOR::StepA()
{
    UE_LOG(LogTemp, Log, TEXT("StepA executed"));
}

void AMYFLOWACTOR::StepB(FControlFlowNodeRef FlowHandle)
{
    UE_LOG(LogTemp, Log, TEXT("StepB start, waiting 1 second..."));
    FTimerHandle TimerHandle;
    GetWorld()->GetTimerManager().SetTimer(TimerHandle, [FlowHandle]()
    {
        FlowHandle->ContinueFlow();
    }, 1.0f, false);
}

void AMYFLOWACTOR::StepC(TSharedRef<FControlFlow> SubFlow)
{
    SubFlow->QueueStep(this, &ThisClass::StepD);
    SubFlow->QueueFlowEnd();
}

void AMYFLOWACTOR::StepD()
{
    UE_LOG(LogTemp, Log, TEXT("StepD executed"));
}

void AMYFLOWACTOR::FlowCompleted()
{
    UE_LOG(LogTemp, Log, TEXT("Flow completed!"));
}
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/CoreUObject/Engine 等） | |

该插件的 Build.cs 仅依赖常见的 UE 核心模块，无需额外的第三方库。

---

## 维护状态

### 近期更新

- 2025-06-26 a358aec2 - [ControlFlows] Cache Parent.Pin() early to shorten call stacks, eliminate weak-ptr race window & ext
- 2025-06-10 1be7adc4 - Replace some usages of FORCEINLINE with inline in GameplayFramework modules.
- 2025-03-21 32ba43f6 - Fixing assert/bug with Parallel Control Flow Execution
- 2024-11-10 66e9bb39 - Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base
- 2024-11-01 56264268 - Replacing forward declare with include

### 维护评价

- **创建时间**：2024-11-01，约 1 年。
- **更新频率**：自创建以来有 4 次实质性更新（修复并发 bug、优化性能、清理代码），最后一次为 2025-06，表明仍在维护。
- **是否活跃**：是。最近的提交修复了弱指针竞争条件和并行执行断言问题，显示开发者积极维护。
- **已知问题**：从提交历史看，并行并发控制存在 assert/bug，已被修复；弱指针竞争窗口也有改进。目前较为稳定。
- **推荐使用**：✅ 推荐。该插件功能完善，适合需要复杂异步编排的 C++ 项目。注意它目前是实验性插件（位于 `Experimental` 目录），默认未启用，需要手动在模块中引用。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ControlFlows)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/)（无专用文档，可参考通用实验性插件说明）
- 无独立测试用例目录，头文件中注释包含了完整示例