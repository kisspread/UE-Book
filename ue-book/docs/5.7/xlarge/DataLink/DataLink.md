# Motion Design Data Link

> （Description 字段为空，基于源码分析）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataLink` (Runtime), `DataLinkDataTable` (Runtime), `DataLinkEdGraph` (UncookedOnly), `DataLinkEditor` (Runtime), `DataLinkHttp` (Runtime), `DataLinkJson` (Runtime), `DataLinkJsonEditor` (Runtime), `DataLinkWebSocket` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink) | |

## 用途

DataLink 是一个**基于节点图的数据处理框架**，专为 Motion Design（虚拟制片）场景设计。它解决的核心问题是：**如何将来自不同数据源（HTTP API、WebSocket、JSON 文件、DataTable）的数据，通过可视化的节点图进行转换、处理，并最终输出到目标系统**。

与蓝图不同，DataLink 的节点图是**编译时确定的、不可变的执行模型**——节点本身不持有状态，所有运行时数据通过 `FDataLinkExecutor` 管理的输入/输出数据视图传递。这使得同一张图可以被安全地并发执行，且支持数据缓存（Sink）机制来避免重复计算。

典型应用场景：
- 从远程 API 拉取数据，经过格式转换后驱动 Motion Design UI 元素
- 通过 WebSocket 实时接收数据流，经过节点图处理后更新场景状态
- 将 JSON 配置文件解析为结构化数据，供虚拟制片流水线使用

## 使用场景

- 你在做虚拟制片项目，需要从外部 API 获取实时数据驱动 Motion Design 元素 → 用 DataLink + DataLinkHttp
- 你需要通过 WebSocket 接收实时数据流并处理 → 用 DataLink + DataLinkWebSocket
- 你想用可视化节点图定义数据转换逻辑，而不是写硬编码的蓝图 → 用 DataLinkEdGraph 编辑器
- 你需要在蓝图中创建自定义数据处理节点 → 用 `UDataLinkScriptNode` 蓝图节点系统
- 你需要缓存节点输出以避免重复计算 → 用 `FDataLinkSink` 缓存机制

## 模块总览

本插件由 8 个模块组成，按职责可分为 4 层：

| 层级 | 模块 | 类型 | 职责 |
|---|---|---|---|
| **核心** | `DataLink` | Runtime | 节点基类、执行器、图编译、数据查看器 |
| **数据源** | `DataLinkHttp` | Runtime | HTTP 请求数据源节点 |
| | `DataLinkWebSocket` | Runtime | WebSocket 实时数据源节点 |
| | `DataLinkJson` | Runtime | JSON 解析/序列化节点 |
| | `DataLinkDataTable` | Runtime | DataTable 数据源节点 |
| **编辑器** | `DataLinkEdGraph` | UncookedOnly | 可视化节点图编辑器 |
| | `DataLinkEditor` | Runtime | 编辑器集成（属性面板等） |
| | `DataLinkJsonEditor` | Runtime | JSON 相关编辑器支持 |

## 核心概念

### 数据流模型

```
输入数据 → [Input Nodes] → [中间节点] → [Output Node] → 输出数据
                ↑                              ↓
          FDataLinkInputDataViewer    FDataLinkOutputDataViewer
```

- **FDataLinkInstance**：描述一次执行的完整配置（图 + 输入数据）
- **FDataLinkExecutor**：执行引擎，管理节点实例化、数据传递、生命周期
- **FDataLinkSink**：缓存层，根据节点类 + 输入数据哈希缓存输出，避免重复计算
- **FDataLinkNodeInstance**：单个节点在一次执行中的运行时实例

### 节点（Node）

每个节点继承自 `UDataLinkNode`，通过以下虚函数定义行为：

| 虚函数 | 用途 |
|---|---|
| `OnBuildPins` | 定义输入/输出引脚及其结构体类型 |
| `OnExecute` | 执行逻辑，从输入数据视图读取，向输出数据视图写入 |
| `OnStop` | 强制停止时的清理逻辑 |
| `OnBuildMetadata` | 编辑器显示名称和提示文本 |
| `OnFixupNode` | 编译后数据修正 |

### 引脚（Pin）

引脚通过 `FDataLinkPinBuilder` 构建，每个引脚有：
- `Name`：唯一标识符
- `DisplayName`：显示名称
- `Struct`：数据类型（`UScriptStruct*`）
- `LinkedNode` / `LinkedIndex`：连接信息

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Run` | 启动数据链接图执行 | `UDataLinkExecutorObject` |
| `Stop` | 停止当前执行 | `UDataLinkExecutorObject` |
| `IsRunning` | 查询是否正在执行 | `UDataLinkExecutorObject` |
| `ResetSink` | 重置数据缓存 | `UDataLinkSinkObject` |
| `Succeed` | 蓝图节点：标记执行成功并输出数据 | `UDataLinkScriptNode` |
| `Succeed (Wildcard)` | 蓝图节点：通配符版本的成功输出 | `UDataLinkScriptNode` |
| `Fail` | 蓝图节点：标记执行失败 | `UDataLinkScriptNode` |
| `Get Input Data` | 蓝图节点：获取输入数据 | `UDataLinkScriptNode` |
| `Get Input Data (Wildcard)` | 蓝图节点：通配符版本的输入获取 | `UDataLinkScriptNode` |
| `GetContextObject` | 获取执行上下文对象 | `UDataLinkProcessorBlueprint` |

### 使用示例（蓝图描述）

**创建并执行数据链接：**

1. 创建 `UDataLinkExecutorObject` 实例（可通过 Spawn Actor 或 Create Object 节点）
2. 设置 `DataLinkInstance` 属性：指定 `DataLinkGraph` 和 `InputData`
3. 绑定 `OnOutputData` 委托以接收输出数据
4. 绑定 `OnExecutionFinished` 委托以获知执行完成
5. 调用 `Run` 节点开始执行

**创建自定义蓝图节点：**

1. 创建 `UDataLinkScriptNode` 的蓝图子类
2. 在 `Class Defaults` 中配置 `InputPins` 和 `OutputPin`
3. 实现 `OnExecute` 事件：使用 `Get Input Data` 获取输入，使用 `Succeed` 输出结果
4. 在节点图编辑器中选择该蓝图节点类

**创建输出处理器：**

1. 创建 `UDataLinkProcessorBlueprint` 的蓝图子类
2. 实现 `Initialize`、`ProcessOutput`、`Finalize` 事件
3. 将处理器实例传入 `FDataLinkExecutorArguments::SetOutputProcessors`

## C++ 用法

### 头文件引入

```cpp
#include "DataLinkExecutor.h"
#include "DataLinkExecutorArguments.h"
#include "DataLinkInstance.h"
#include "DataLinkGraph.h"
#include "DataLinkNode.h"
#include "DataLinkPinBuilder.h"
#include "DataLinkOutputDataViewer.h"
#include "DataLinkInputDataViewer.h"
```

### 基本用法：执行数据链接图

```cpp
// 构造执行实例
FDataLinkInstance Instance;
Instance.DataLinkGraph = MyGraph;  // UDataLinkGraph*

// 设置输入数据
FDataLinkInputData& InputEntry = Instance.InputData.AddDefaulted_GetRef();
InputEntry.DisplayName = FText::FromString(TEXT("MyInput"));
InputEntry.Data.InitializeAs(FMyInputStruct::StaticStruct());
FMyInputStruct& InputData = InputEntry.Data.GetMutable<FMyInputStruct>();
InputData.Value = TEXT("Hello");

// 创建执行器参数
FDataLinkExecutorArguments Args(MoveTemp(Instance));
Args.SetContextObject(this)
    .SetOnOutputData(FOnDataLinkOutputData::CreateLambda(
        [](const FDataLinkExecutor& InExecutor, FConstStructView InOutputData)
        {
            // 处理输出数据
            if (const FMyOutputStruct* Output = InOutputData.GetPtr<FMyOutputStruct>())
            {
                // 使用输出数据
            }
        }))
    .SetOnFinished(FOnDataLinkExecutionFinished::CreateLambda(
        [](const FDataLinkExecutor& InExecutor, EDataLinkExecutionResult InResult)
        {
            // 执行完成
        }));

// 创建并运行执行器
TSharedPtr<FDataLinkExecutor> Executor = FDataLinkExecutor::Create(MoveTemp(Args));
Executor->Run();
```

### 自定义节点实现

```cpp
// MyDataLinkNode.h
#pragma once
#include "DataLinkNode.h"
#include "MyDataLinkNode.generated.h"

UCLASS(MinimalAPI, DisplayName="My Custom Node", Category="Custom")
class UMyDataLinkNode : public UDataLinkNode
{
    GENERATED_BODY()

protected:
    virtual void OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const override
    {
        // 定义输入引脚
        Inputs.Add(UE::DataLink::InputDefault)
            .SetDisplayName(NSLOCTEXT("MyNode", "Input", "Input"))
            .SetStruct<FMyInputStruct>();

        // 定义输出引脚
        Outputs.Add(UE::DataLink::OutputDefault)
            .SetDisplayName(NSLOCTEXT("MyNode", "Output", "Output"))
            .SetStruct<FMyOutputStruct>();
    }

    virtual EDataLinkExecutionReply OnExecute(FDataLinkExecutor& InExecutor) const override
    {
        // 获取节点实例（包含输入/输出数据视图）
        const FDataLinkNodeInstance& NodeInstance = InExecutor.GetNodeInstance(this);
        const FDataLinkInputDataViewer& InputViewer = NodeInstance.GetInputDataViewer();

        // 读取输入
        const FMyInputStruct& Input = InputViewer.Get<FMyInputStruct>(UE::DataLink::InputDefault);

        // 写入输出
        FDataLinkOutputDataViewer& OutputViewer = 
            InExecutor.GetNodeInstanceMutable(this).GetOutputDataViewer();
        FMyOutputStruct& Output = OutputViewer.Get<FMyOutputStruct>(UE::DataLink::OutputDefault);
        Output.Result = ProcessData(Input);

        // 通知执行器继续下一个节点
        InExecutor.Next(this);
        return EDataLinkExecutionReply::Handled;
    }

#if WITH_EDITOR
    virtual void OnBuildMetadata(FDataLinkNodeMetadata& Metadata) const override
    {
        Metadata.SetDisplayName(NSLOCTEXT("MyNode", "DisplayName", "My Custom Node"))
                .SetTooltipText(NSLOCTEXT("MyNode", "Tooltip", "Processes custom data"));
    }
#endif
};
```

### 进阶用法：带 Sink 缓存的执行

```cpp
// 创建共享 Sink 用于跨执行缓存
TSharedPtr<FDataLinkSink> SharedSink = MakeShared<FDataLinkSink>();

// 第一次执行 - 计算并缓存
{
    FDataLinkExecutorArguments Args(FDataLinkInstance{MyGraph, InputData});
    Args.SetSink(SharedSink);
    auto Executor = FDataLinkExecutor::Create(MoveTemp(Args));
    Executor->Run();
}

// 第二次执行 - 相同输入将命中缓存
{
    FDataLinkExecutorArguments Args(FDataLinkInstance{MyGraph, InputData});
    Args.SetSink(SharedSink);  // 复用同一 Sink
    auto Executor = FDataLinkExecutor::Create(MoveTemp(Args));
    Executor->Run();
}
```

### 进阶用法：带输出处理器的执行

```cpp
// 自定义处理器
UCLASS()
class UMyDataProcessor : public UDataLinkProcessor
{
    GENERATED_BODY()

protected:
    virtual void OnInitialize(const FDataLinkExecutor& InExecutor) override
    {
        // 执行开始前的初始化
    }

    virtual void OnProcessOutput(const FDataLinkExecutor& InExecutor, FConstStructView InOutputDataView) override
    {
        // 处理每次输出的数据
        if (const FMyOutputStruct* Data = InOutputDataView.GetPtr<FMyOutputStruct>())
        {
            ApplyToScene(*Data);
        }
    }

    virtual void OnFinalize(const FDataLinkExecutor& InExecutor, EDataLinkExecutionResult InResult) override
    {
        // 执行结束后的清理
    }
};

// 使用处理器
UMyDataProcessor* Processor = NewObject<UMyDataProcessor>();
FDataLinkExecutorArguments Args(MyInstance);
Args.SetOutputProcessors({Processor});
auto Executor = FDataLinkExecutor::Create(MoveTemp(Args));
Executor->Run();
```

## Demo 示例

### 自定义数据链接节点

```cpp
// DemoNode.h
#pragma once
#include "DataLinkNode.h"
#include "StructUtils/InstancedStruct.h"
#include "DemoNode.generated.h"

USTRUCT(BlueprintType)
struct FDemoInput
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString SourceText;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 RepeatCount = 1;
};

USTRUCT(BlueprintType)
struct FDemoOutput
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString ResultText;
};

UCLASS(DisplayName="Demo Repeater", Category="Demo")
class UDemoRepeaterNode : public UDataLinkNode
{
    GENERATED_BODY()

protected:
    virtual void OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const override
    {
        Inputs.Add(UE::DataLink::InputDefault)
            .SetDisplayName(NSLOCTEXT("Demo", "Input", "Input"))
            .SetStruct<FDemoInput>();

        Outputs.Add(UE::DataLink::OutputDefault)
            .SetDisplayName(NSLOCTEXT("Demo", "Output", "Output"))
            .SetStruct<FDemoOutput>();
    }

    virtual EDataLinkExecutionReply OnExecute(FDataLinkExecutor& InExecutor) const override
    {
        const FDataLinkNodeInstance& NodeInstance = InExecutor.GetNodeInstance(this);
        const FDemoInput& Input = NodeInstance.GetInputDataViewer().Get<FDemoInput>(UE::DataLink::InputDefault);

        FDataLinkOutputDataViewer& OutputViewer = 
            InExecutor.GetNodeInstanceMutable(this).GetOutputDataViewer();
        FDemoOutput& Output = OutputViewer.Get<FDemoOutput>(UE::DataLink::OutputDefault);

        FString Result;
        for (int32 i = 0; i < Input.RepeatCount; ++i)
        {
            Result += Input.SourceText;
        }
        Output.ResultText = MoveTemp(Result);

        InExecutor.Next(this);
        return EDataLinkExecutionReply::Handled;
    }

#if WITH_EDITOR
    virtual void OnBuildMetadata(FDataLinkNodeMetadata& Metadata) const override
    {
        Metadata.SetDisplayName(NSLOCTEXT("Demo", "Name", "Demo Repeater"))
                .SetTooltipText(NSLOCTEXT("Demo", "Tip", "Repeats input text N times"));
    }
#endif
};
```

```cpp
// DemoUsage.cpp
#include "DataLinkExecutor.h"
#include "DataLinkExecutorArguments.h"
#include "DataLinkInstance.h"
#include "DataLinkGraph.h"
#include "DemoNode.h"

void UDemoComponent::RunDemoGraph()
{
    // 假设 MyGraph 已在编辑器中配置好，包含 DemoRepeaterNode
    FDataLinkInstance Instance;
    Instance.DataLinkGraph = MyGraph;

    // 设置输入
    FDataLinkInputData& Input = Instance.InputData.AddDefaulted_GetRef();
    Input.DisplayName = FText::FromString(TEXT("DemoInput"));
    Input.Data.InitializeAs(FDemoInput::StaticStruct());
    FDemoInput& InputData = Input.Data.GetMutable<FDemoInput>();
    InputData.SourceText = TEXT("Hello");
    InputData.RepeatCount = 3;

    FDataLinkExecutorArguments Args(MoveTemp(Instance));
    Args.SetContextObject(this)
        .SetOnOutputData(FOnDataLinkOutputData::CreateUObject(this, &UDemoComponent::OnDataReceived))
        .SetOnFinished(FOnDataLinkExecutionFinished::CreateUObject(this, &UDemoComponent::OnFinished));

    Executor = FDataLinkExecutor::Create(MoveTemp(Args));
    Executor->Run();
}

void UDemoComponent::OnDataReceived(const FDataLinkExecutor& InExecutor, FConstStructView InData)
{
    if (const FDemoOutput* Output = InData.GetPtr<FDemoOutput>())
    {
        UE_LOG(LogTemp, Log, TEXT("Result: %s"), *Output->ResultText);
        // 输出: "HelloHelloHello"
    }
}

void UDemoComponent::OnFinished(const FDataLinkExecutor& InExecutor, EDataLinkExecutionResult InResult)
{
    UE_LOG(LogTemp, Log, TEXT("Execution %s"), 
        InResult == EDataLinkExecutionResult::Succeeded ? TEXT("Succeeded") : TEXT("Failed"));
}
```

## 模块依赖

从各模块的 Build.cs 分析，以下是该插件**独特**的依赖关系：

| 模块 | 用途 |
|---|---|
| `StructUtils` | `FInstancedStruct` / `FStructView` / `FConstStructView`，核心数据容器 |
| `GraphEditor` | 节点图编辑器 UI（DataLinkEdGraph 模块） |
| `HTTP` | HTTP 请求支持（DataLinkHttp 模块） |
| `WebSockets` | WebSocket 连接支持（DataLinkWebSocket 模块） |
| `Json` | JSON 解析/序列化（DataLinkJson 模块） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

```
- 1d7d2cdb2f20 Add missing include from some no-PCH configurations, including explicit include for GCObject.h which will be removed from StrongObjectPtr.h
- 94f961385e8e Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction
```

- `94f961385e8e`：从 Experimental 目录迁移到 VirtualProduction 目录，标志着插件进入更成熟的阶段
- `1d7d2cdb2f20`：修复 PCH 配置下的编译问题，属于编译兼容性修复

### 维护评价

- **创建时间**：2025-04-22，非常新的插件（不到 1 年）
- **状态**：`IsBetaVersion=true`，仍处于 Beta 阶段
- **活跃度**：近期有从 Experimental 迁出的活动，表明 Epic 正在积极推进该插件的成熟化
- **已知限制**：
  - Beta 状态，API 可能在后续版本中发生变化
  - `UDataLinkRequestProxy` 已在 5.7 标记为废弃，应使用 `UDataLinkExecutorObject` 替代
  - 288 个源文件的大型插件，学习曲线较陡
- **推荐度**：如果你在做 Motion Design / 虚拟制片项目且需要外部数据集成，这是官方推荐的方案。但需注意 Beta 状态，生产环境使用需谨慎评估稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink)
- 官方文档（无）
- 测试用例（未在插件目录内发现独立测试文件）