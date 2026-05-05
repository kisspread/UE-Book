# Motion Design Scene State Data Link Bridge

> Scene State Tasks that execute Data Link Graphs

| 属性 | 值 |
|---|---|
| 分类 | VirtualProduction |
| 默认启用 | false (需手动启用) |
| 包含内容 | true |
| 模块 | SceneStateDataLink (Runtime), SceneStateDataLinkEditor (Editor) |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕 |
| Beta | ⚠️ IsBetaVersion=true |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneStateDataLink) | |

## 用途

SceneStateDataLink 是 **SceneState**（场景状态机系统）和 **DataLink**（数据链路图执行系统）之间的桥接插件。

- **SceneState** 是 UE5 VirtualProduction 中的状态机框架，用于管理场景中的状态转换和任务执行（类似于行为树中的 Task 概念）。每个状态可以包含多个 Task，Task 可以异步执行并在完成后通知状态机。
- **DataLink** 是一个基于节点图的数据获取/处理管线框架。它通过 `UDataLinkGraph` 资产定义数据流（输入 → 处理节点 → 输出），支持从 HTTP、JSON、DataTable、WebSocket 等多种数据源获取和转换数据。

**SceneStateDataLink 解决的问题**：在 SceneState 的状态执行过程中，需要通过 DataLink 图来获取外部数据，并将结果写回到状态的属性中。例如：进入某个场景状态时，通过 HTTP 请求获取远程配置，然后将配置数据应用到场景参数上。

插件提供了一个名为 **"Run Data Link"** 的 SceneState Task，它在状态激活时执行指定的 DataLinkGraph，获取输出数据，然后将结果写入到指定的属性引用（OutputTarget）中。

## 使用场景

- 你的场景使用 SceneState 管理状态转换，同时需要在某个状态中从外部数据源（HTTP、JSON 等）拉取数据 → 用 SceneStateDataLink
- 你有一个 DataLinkGraph 负责获取实时数据（如远程 API 配置），需要在 Motion Design 场景状态机中触发执行 → 用 SceneStateDataLink
- 你需要将 DataLink 图的输出结果自动写入到 SceneState 的绑定属性中 → 用 SceneStateDataLink

## 蓝图用法

本插件没有暴露 `BlueprintCallable` 函数。它完全基于 UE 的 **USTRUCT Task 系统**工作——在 SceneState 蓝图编辑器中以 Task 节点的形式使用。

### 核心 Task 节点

| Task | 显示名称 | 分类 | 说明 |
|---|---|---|---|
| `FSceneStateRunDataLinkTask` | Run Data Link | Data Link | 执行一个 DataLinkGraph 并将输出写入属性引用 |

### Task 实例属性

在 SceneState 编辑器中添加 "Run Data Link" Task 后，可配置以下属性：

| 属性 | 类型 | 说明 |
|---|---|---|
| DataLinkGraph | `UDataLinkGraph*` | 要执行的数据链路图资产 |
| InputData | `TArray<FDataLinkInputData>` | 图的输入数据数组（根据图的输入引脚自动同步） |
| OutputTarget | `FSceneStatePropertyReference` | 输出结果写入的目标属性引用（必须是 struct 类型，且与图的输出类型匹配） |

### 使用步骤（编辑器操作描述）

1. 确保 **SceneState** 和 **DataLink** 插件已启用
2. 启用 **SceneStateDataLink** 插件
3. 创建一个 **DataLinkGraph** 资产，定义你的数据获取管线（包含输入引脚和输出节点）
4. 在 SceneState 蓝图编辑器中，选中一个状态，添加 Task → 选择 **"Run Data Link"**
5. 在 Task 的属性面板中：
   - 设置 **DataLinkGraph** 为你创建的图资产
   - **InputData** 数组会根据图的输入引脚自动更新，为每个输入填入数据
   - 设置 **OutputTarget** 属性引用，指向要写入结果的 struct 属性
6. 当状态机进入该状态且 Task 的前置条件满足时，DataLink 图会自动执行
7. 图执行完成后，输出数据会自动复制到 OutputTarget 指定的属性中

## C++ 用法

### 头文件引入

```cpp
#include "SceneStateRunDataLinkTask.h"
```

### 核心类结构

```cpp
// Task 实例数据 —— 存储运行时的可变数据
USTRUCT()
struct FSceneStateDataLinkRequestTaskInstance : public FSceneStateTaskInstance
{
    GENERATED_BODY()

    // 创建 DataLink 实例（用于执行器）
    FDataLinkInstance CreateDataLinkInstance() const;

    // 要执行的 DataLink 图
    UPROPERTY(EditAnywhere, Category="Data Link", meta=(NoBinding))
    TObjectPtr<UDataLinkGraph> DataLinkGraph;

    // 输入数据（类型由 DataLinkGraph 决定）
    UPROPERTY(EditAnywhere, EditFixedSize, Category="Data Link",
              meta=(EditFixedOrder, NoBindingSelfOnly))
    TArray<FDataLinkInputData> InputData;

    // 输出目标属性引用（必须是 struct 类型，且与图输出匹配）
    UPROPERTY(EditAnywhere, Category="Data Link", meta=(RefType="AnyStruct"))
    FSceneStatePropertyReference OutputTarget;

    // 运行时：执行器句柄
    TSharedPtr<FDataLinkExecutor> Executor;
};

// Task 定义 —— 不可变的逻辑定义
USTRUCT(DisplayName="Run Data Link", Category="Data Link")
struct FSceneStateRunDataLinkTask : public FSceneStateTask
{
    GENERATED_BODY()
    using FInstanceDataType = FSceneStateDataLinkRequestTaskInstance;

    // 编辑器：返回实例类型、构建实例
    virtual const UScriptStruct* OnGetTaskInstanceType() const override;
    virtual void OnBuildTaskInstance(UObject* InOuter, FStructView InTaskInstance) const override;

    // 运行时：启动 Task 时创建并运行 DataLink 执行器
    virtual void OnStart(const FSceneStateExecutionContext& InContext,
                         FStructView InTaskInstance) const override;

    // 运行时：停止 Task 时中止执行器
    virtual void OnStop(const FSceneStateExecutionContext& InContext,
                        FStructView InTaskInstance,
                        ESceneStateTaskStopReason InStopReason) const override;

    // 回调：DataLink 输出数据时，解析 OutputTarget 并复制数据
    static void OnOutputData(const FDataLinkExecutor& InExecutor,
                             FConstStructView InOutputDataView,
                             UE::SceneState::FTaskExecutionContext InTaskContext);

    // 回调：DataLink 执行完成时，标记 Task 完成
    static void OnFinished(const FDataLinkExecutor& InExecutor,
                           EDataLinkExecutionResult InExecutionResult,
                           UE::SceneState::FTaskExecutionContext InTaskContext);
};
```

### 执行流程

当 SceneState 激活包含此 Task 的状态时，执行顺序如下：

1. **OnStart** 被调用
   - 从 TaskInstance 创建 `FDataLinkInstance`（包含 DataLinkGraph + InputData）
   - 通过 `FDataLinkExecutor::Create()` 创建执行器，设置上下文对象、输出回调和完成回调
   - 调用 `Executor->Run()` 开始执行图
2. **OnOutputData** 回调（异步）
   - 验证 OutputTarget 是否可解析（通过 `ResolveProperty`）
   - 验证目标属性是否为 struct 类型
   - 验证目标 struct 类型与图输出 struct 类型匹配
   - 通过 `CopyScriptStruct` 将输出数据复制到目标属性
3. **OnFinished** 回调（异步）
   - 调用 `FinishTask()` 标记 Task 完成，通知状态机
4. **OnStop**（如果被强制停止）
   - 停止执行器并重置引用

### 编辑器模块

Editor 模块为 `FSceneStateDataLinkRequestTaskInstance` 注册了自定义的 Property Details：

```cpp
// SceneStateDataLinkEditorModule.cpp
PropertyEditorModule.RegisterCustomPropertyTypeLayout(
    FSceneStateDataLinkRequestTaskInstance::StaticStruct()->GetFName(),
    FOnGetPropertyTypeCustomizationInstance::CreateStatic(
        &FRequestTaskInstanceDetails::MakeInstance));
```

自定义 Details 面板的作用：
- 当用户切换 DataLinkGraph 时，自动同步 InputData 数组（调用 `UE::DataLink::SetInputData`）
- 当图被重新编译时，自动更新 InputData
- 为 InputData 和 OutputTarget 设置正确的 BindingId，使 SceneState 绑定系统正常工作

## Demo 示例

### 最小 C++ 示例：自定义 SceneState Task（参考模式）

以下示例展示如何参考 SceneStateDataLink 的模式来创建自己的 Task：

```cpp
// MyCustomTask.h
#pragma once
#include "Tasks/SceneStateTask.h"
#include "Tasks/SceneStateTaskInstance.h"
#include "MyCustomTask.generated.h"

USTRUCT()
struct FMyCustomTaskInstance : public FSceneStateTaskInstance
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere)
    float Duration = 1.0f;

    float Elapsed = 0.f;
};

USTRUCT(DisplayName="My Custom Task", Category="Custom")
struct FMyCustomTask : public FSceneStateTask
{
    GENERATED_BODY()
    using FInstanceDataType = FMyCustomTaskInstance;

protected:
#if WITH_EDITOR
    virtual const UScriptStruct* OnGetTaskInstanceType() const override
    {
        return FInstanceDataType::StaticStruct();
    }
#endif

    virtual void OnStart(const FSceneStateExecutionContext& InContext,
                         FStructView InTaskInstance) const override
    {
        // 启动逻辑
    }

    virtual void OnStop(const FSceneStateExecutionContext& InContext,
                        FStructView InTaskInstance,
                        ESceneStateTaskStopReason InStopReason) const override
    {
        // 清理逻辑
    }
};
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "SceneState",
    "SceneStateBinding",
});
```

## 模块依赖

### SceneStateDataLink (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 反射系统 |
| `DataLink` | DataLink 图执行框架 |
| `Engine` | 引擎基础功能 |
| `SceneState` | SceneState 状态机框架 |
| `SceneStateBinding` | SceneState 属性绑定系统 |

### SceneStateDataLinkEditor (Editor)

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 反射系统 |
| `DataLink` | DataLink 图类型（用于 Details 定制） |
| `Engine` | 引擎基础功能 |
| `PropertyEditor` | 编辑器属性面板自定义 |
| `SceneStateBlueprintEditor` | SceneState 蓝图编辑器集成 |
| `SceneStateDataLink` | 运行时模块（本插件） |

### Plugin 依赖

| 插件 | 说明 |
|---|---|
| **SceneState** | 提供状态机框架、Task 基类、属性绑定系统 |
| **DataLink** | 提供 DataLinkGraph、DataLinkExecutor、数据流节点图 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-08-27 | `f25e96ca` | Motion Design: set the scene state and data link plugins to beta | 将插件标记为 Beta 版本，表明功能基本完成但 API 可能变更 |
| 2025-08-27 | `94f96138` | Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction | 从 Experimental 分类迁移到 VirtualProduction 分类，标志着从实验阶段进入 Beta |

### 维护评价

- **创建时间**：2025-08-27（~8 个月前），非常新的插件
- **更新频率**：仅 2 次 commit（均在创建当天），均为结构性调整而非功能更新
- **Beta 状态**：`IsBetaVersion=true`，API 和功能可能发生变化
- **定位**：这是 SceneState 和 DataLink 两个大型系统的桥接插件，代码量极小（仅 8 个源文件），功能单一明确
- **生态关联**：AvalancheDataLink 和 AvalancheSceneState 是更上层的 Motion Design 集成插件，SceneStateDataLink 是底层桥接
- **风险提示**：⚠️ Beta 阶段的插件，依赖的 SceneState 和 DataLink 本身也是 Beta，整体生态尚不稳定

**推荐**：如果你已经在使用 SceneState + DataLink 的组合，这个插件是必需的桥接。但由于整体生态仍处于 Beta 阶段，建议在非生产环境中试用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneStateDataLink)
- [SceneState 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState)
- [DataLink 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink)
- [AvalancheDataLink（上层集成）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/AvalancheDataLink)
- [AvalancheSceneState（上层集成）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/AvalancheSceneState)
