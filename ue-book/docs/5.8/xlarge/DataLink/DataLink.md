# Motion Design Data Link

> Motion Design Data Link

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计数据链接 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataLink` (Runtime), `DataLinkDataTable` (Runtime), `DataLinkEdGraph` (Runtime), `DataLinkEditor` (Runtime), `DataLinkHttp` (Runtime), `DataLinkJson` (Runtime), `DataLinkJsonEditor` (Runtime), `DataLinkWebSocket` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLink) | |

## 用途

DataLink 是一个**基于节点图的数据处理框架**，专为虚拟制作（Motion Design）场景设计。它解决的核心问题是：如何将来自不同数据源（HTTP、WebSocket、JSON、DataTable）的数据，通过可视化节点图进行采集、转换和传递，最终输出到需要数据的目标。

与蓝图不同，DataLink 的设计哲学是**数据流驱动**而非控制流驱动。每个节点专注于数据的输入/输出，节点之间通过类型兼容的 Pin 连接，数据像流水线一样经过处理后输出结果。系统内置了结果缓存机制（FDataLinkSink），相同输入的节点执行结果会被缓存复用，提高性能。

典型的数据流：
```
数据源节点（HTTP/WebSocket/DataTable）→ 处理节点（字符串构建/JSON解析）→ 输出节点 → 数据消费者
```

## 使用场景

- **虚拟制作现场数据驱动**：实时接收外部设备/服务数据（如运动捕捉系统、灯光控制台），通过数据链路图处理后驱动场景元素
- **Motion Design 参数绑定**：将外部 API 数据（天气、股票、赛事比分等）通过 HTTP/WebSocket 拉取后，经格式化处理推送到 Motion Design 图形元素
- **自定义数据转换管线**：需要将原始 JSON 数据解析、字符串模板替换、DataTable 查询等操作串联执行时
- **可复用的数据处理模板**：利用 Sink 缓存机制，多个相同输入的执行共享缓存结果，适合高频查询场景
- **蓝图友好的数据流节点**：通过 UDataLinkScriptNode 在蓝图中自定义数据处理逻辑，无需 C++ 编码

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Run` | 启动数据链路图执行 | `UDataLinkExecutorObject` |
| `Stop` | 停止正在运行的执行 | `UDataLinkExecutorObject` |
| `IsRunning` | 查询是否正在执行 | `UDataLinkExecutorObject` |
| `Succeed` | 脚本节点通知执行成功并传递输出数据 | `UDataLinkScriptNode` |
| `Succeed (Wildcard)` | 通配符版本，支持任意结构体 | `UDataLinkScriptNode` |
| `Fail` | 脚本节点通知执行失败 | `UDataLinkScriptNode` |
| `Get Input Data` | 获取脚本节点的输入数据 | `UDataLinkScriptNode` |
| `Get Input Data (Wildcard)` | 通配符版本获取输入数据 | `UDataLinkScriptNode` |
| `OnExecute` | 蓝图可实现事件：节点执行时触发 | `UDataLinkScriptNode` |
| `OnStop` | 蓝图可实现事件：节点停止时触发 | `UDataLinkScriptNode` |
| `Initialize` | 处理器初始化事件 | `UDataLinkProcessorBlueprint` |
| `ProcessOutput` | 处理器接收输出数据事件 | `UDataLinkProcessorBlueprint` |
| `Finalize` | 处理器结束事件 | `UDataLinkProcessorBlueprint` |
| `ResetSink` | 重置数据缓存 | `UDataLinkSinkObject` |

### 蓝图代理（委托）

| 委托 | 说明 | 所在类 |
|---|---|---|
| `OnOutputData` | 输出数据就绪时触发 | `UDataLinkExecutorObject` |
| `OnExecutionFinished` | 执行完成/失败时触发 | `UDataLinkExecutorObject` |

### 使用示例（蓝图描述）

**场景 1：蓝图中执行数据链路图**

1. 创建一个 `UDataLinkExecutorObject` 实例
2. 设置 `DataLinkInstance` 属性：指定 `DataLinkGraph` 和 `InputData`
3. 绑定 `OnOutputData` 委托，处理接收到的数据
4. 绑定 `OnExecutionFinished` 委托，处理执行结果
5. 调用 `Run` 节点开始执行
6. 在 `OnOutputData` 回调中通过 `FInstancedStruct` 提取输出数据

**场景 2：自定义蓝图数据处理节点**

1. 创建 `UDataLinkScriptNode` 的蓝图子类
2. 在类默认设置中配置 `InputPins`（名称 + 结构体类型）和 `OutputPin`
3. 实现 `OnExecute` 事件：
   - 调用 `Get Input Data` 获取输入
   - 执行自定义处理逻辑
   - 调用 `Succeed` 传递结果并前进到下一节点
4. 可选：设置 `bPersistExecution = true` 使节点持续推送数据而非一次性完成

## C++ 用法

### 头文件引入

```cpp
#include "DataLinkExecutor.h"
#include "DataLinkExecutorArguments.h"
#include "DataLinkGraph.h"
#include "DataLinkInstance.h"
#include "DataLinkNode.h"
#include "DataLinkSink.h"
```

### 基本用法

**创建并执行一个数据链路图：**

```cpp
// 来源: DataLinkExecutor.h, DataLinkExecutorArguments.h
// 构建执行参数
FDataLinkInstance Instance;
Instance.DataLinkGraph = MyDataLinkGraph;
Instance.InputData.Add(FDataLinkInputData{
    .DisplayName = NSLOCTEXT("MyModule", "Input", "Input"),
    .Data = FInstancedStruct::Make<FMyInputStruct>(MyInputData)
});

// 创建执行器参数
FDataLinkExecutorArguments Args(MoveTemp(Instance));
Args.SetContextObject(this);
Args.SetOnOutputData(FOnDataLinkOutputData::CreateLambda(
    [](const FDataLinkExecutor& InExecutor, FConstStructView InOutputData)
    {
        // 处理输出数据
        const FMyOutputStruct& Output = InOutputData.Get<const FMyOutputStruct>();
    }));
Args.SetOnFinished(FOnDataLinkExecutionFinished::CreateLambda(
    [](const FDataLinkExecutor& InExecutor, EDataLinkExecutionResult InResult)
    {
        UE_LOG(LogDataLink, Log, TEXT("Execution %s"), 
            InResult == EDataLinkExecutionResult::Succeeded ? TEXT("Succeeded") : TEXT("Failed"));
    }));

// 创建并运行
TSharedPtr<FDataLinkExecutor> Executor = FDataLinkExecutor::Create(MoveTemp(Args));
Executor->Run();
```

**实现自定义 C++ 数据节点：**

```cpp
// 来源: DataLinkNode.h, DataLinkPinBuilder.h
UCLASS()
class UMyDataLinkNode : public UDataLinkNode
{
    GENERATED_BODY()

protected:
    virtual void OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const override
    {
        // 定义输入 Pin
        Inputs.Add(TEXT("SourceData"))
            .SetStruct<FMySourceStruct>()
            .SetDisplayName(NSLOCTEXT("MyModule", "SourceData", "Source Data"));
        
        // 定义输出 Pin
        Outputs.Add(TEXT("Result"))
            .SetStruct<FMyResultStruct>()
            .SetDisplayName(NSLOCTEXT("MyModule", "Result", "Result"));
    }

    virtual EDataLinkExecutionReply OnExecute(FDataLinkExecutor& InExecutor) const override
    {
        // 获取输入数据
        const FDataLinkNodeInstance& NodeInstance = InExecutor.GetNodeInstance(this);
        const FMySourceStruct& Input = NodeInstance.GetInputDataViewer().Get<FMySourceStruct>(TEXT("SourceData"));
        
        // 处理数据
        FMyResultStruct Result;
        Result.Value = ProcessData(Input);
        
        // 填充输出并推进执行
        FDataLinkOutputDataViewer& OutputViewer = InExecutor.GetNodeInstanceMutable(this).GetOutputDataViewer();
        OutputViewer.Get<FMyResultStruct>(TEXT("Result")) = Result;
        InExecutor.Next(this);
        
        return EDataLinkExecutionReply::Handled;
    }
};
```

### 进阶用法

**使用 Sink 缓存实现跨执行数据共享：**

```cpp
// 来源: DataLinkSink.h, DataLinkSinkObject.h, IDataLinkSinkProvider.h
// 创建共享 Sink
TSharedPtr<FDataLinkSink> SharedSink = MakeShared<FDataLinkSink>();

// 执行器 A
FDataLinkExecutorArguments ArgsA(InstanceA);
ArgsA.SetSink(SharedSink);
TSharedPtr<FDataLinkExecutor> ExecutorA = FDataLinkExecutor::Create(MoveTemp(ArgsA));
ExecutorA->Run();

// 执行器 B（相同输入会命中缓存）
FDataLinkExecutorArguments ArgsB(InstanceB);
ArgsB.SetSink(SharedSink);
TSharedPtr<FDataLinkExecutor> ExecutorB = FDataLinkExecutor::Create(MoveTemp(ArgsB));
ExecutorB->Run();
```

**在节点内部使用 Sink 缓存：**

```cpp
// 来源: DataLinkSink.h, DataLinkNodeInstance.h
virtual EDataLinkExecutionReply OnExecute(FDataLinkExecutor& InExecutor) const override
{
    const FDataLinkNodeInstance& NodeInstance = InExecutor.GetNodeInstance(this);
    
    // 尝试从缓存获取，命中则直接使用缓存数据
    FInstancedStruct& Cached = Sink->FindOrAddCachedData(NodeInstance);
    if (Cached.IsValid())
    {
        // 缓存命中，直接使用
        return EDataLinkExecutionReply::Handled;
    }
    
    // 缓存未命中，执行计算后存入缓存
    Cached = FInstancedStruct::Make<FMyResultStruct>(ComputeResult());
    InExecutor.Next(this);
    return EDataLinkExecutionReply::Handled;
}
```

## Demo 示例

### 自定义数据节点完整示例

```cpp
// MyDataLinkNode.h
#pragma once

#include "DataLinkNode.h"
#include "MyDataLinkNode.generated.h"

USTRUCT(BlueprintType)
struct FMyNumberInput
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Data Link")
    double Value = 0.0;
};

USTRUCT(BlueprintType)
struct FMyDoubledNumber
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Data Link")
    double Value = 0.0;
};

/**
 * 一个简单的数据链路节点：将输入数值翻倍后输出
 */
UCLASS(DisplayName="Double Number", Category="Math")
class UMyDataLinkDoubleNumber : public UDataLinkNode
{
    GENERATED_BODY()

protected:
    virtual void OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const override
    {
        Inputs.Add(TEXT("Number"))
            .SetStruct<FMyNumberInput>()
            .SetDisplayName(NSLOCTEXT("Demo", "Number", "Number"));
        
        Outputs.Add(TEXT("Result"))
            .SetStruct<FMyDoubledNumber>()
            .SetDisplayName(NSLOCTEXT("Demo", "Result", "Result"));
    }

    virtual EDataLinkExecutionReply OnExecute(FDataLinkExecutor& InExecutor) const override
    {
        const FDataLinkNodeInstance& NodeInstance = InExecutor.GetNodeInstance(this);
        const FMyNumberInput& Input = NodeInstance.GetInputDataViewer().Get<FMyNumberInput>(TEXT("Number"));
        
        FMyDoubledNumber Output;
        Output.Value = Input.Value * 2.0;
        
        FDataLinkOutputDataViewer& OutputViewer = InExecutor.GetNodeInstanceMutable(this).GetOutputDataViewer();
        OutputViewer.Get<FMyDoubledNumber>(TEXT("Result")) = Output;
        
        InExecutor.Next(this);
        return EDataLinkExecutionReply::Handled;
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HTTP` | HTTP 网络请求支持（DataLinkHttp 模块） |
| `WebSockets` | WebSocket 连接支持（DataLinkWebSocket 模块） |
| `Json` | JSON 数据解析与构建（DataLinkJson 模块） |
| `JsonUtilities` | JSON 与 UObject 互转工具（DataLinkJson 模块） |
| `JsonEditorUtilities` | JSON 编辑器工具（DataLinkJsonEditor 模块） |

> 无特殊依赖（仅标准 Core/Engine/Slate 等）的部分：DataLink 核心模块、DataLinkEdGraph、DataLinkDataTable。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 支持 FString 和 UE::FSharedString 两种字符串类型 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏调用 |
| 2026-03-02 | `e97b93d4` | Fixes for CL 51336460 - Remove string duplication in FJsonObject to free memory | 修复 FJsonObject 中的字符串重复问题以释放内存 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 修复 FORT-984709，移除 FJsonObject 字符串重复以优化内存 |
| 2026-02-25 | `ec13ba36` | [Backout] - CL51209244 | 回退变更 CL51209244 |

### 维护评价

- **状态**：🟢 活跃维护中
- **年龄**：约 1 年（2025-08 创建），是一个较新的插件
- **更新频率**：近 3 个月内有多次更新（2026-02 至 2026-04），且包含性能优化（内存去重、字符串重构）和 API 迁移
- **注意事项**：`.uplugin` 标记为 `IsBetaVersion: true`，说明 API 尚未稳定，后续版本可能有破坏性变更
- **迁移背景**：该插件从 Experimental 目录迁移至 VirtualProduction 目录（首次 commit），表明 Epic 将其定位为 Motion Design 的核心数据组件
- **推荐**：✅ 推荐在 Motion Design / 虚拟制作项目中使用，但需注意 Beta 状态意味着接口可能变化。已有的 `UDataLinkRequestProxy` 已在 5.7 标记为废弃，建议使用 `UDataLinkExecutorObject` 替代

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLink)
- 官方文档：暂无
- [核心模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLink/Source/DataLink)