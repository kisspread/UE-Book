# Motion Design Data Link

> （Description 为空，基于源码分析补充）一个用于 Motion Design 的数据流处理框架，提供节点图编辑器，用于连接、转换和路由来自不同源（如 JSON、HTTP、WebSocket）的数据，以驱动实时动画和可视化。

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataLink` (Runtime), `DataLinkDataTable` (Runtime), `DataLinkEdGraph` (Runtime), `DataLinkEditor` (Runtime), `DataLinkHttp` (Runtime), `DataLinkJson` (Runtime), `DataLinkJsonEditor` (Runtime), `DataLinkWebSocket` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink) | |

## 用途

DataLink 是一个**数据流处理框架**，专为 Motion Design（运动设计）工作流设计。它解决的核心问题是：**如何将来自外部或内部的各种实时数据（如 JSON API 响应、WebSocket 消息、结构化数据）经过一系列转换和处理后，驱动 Unreal Engine 中的动画、材质参数或任何可蓝图化的属性**。

它通过一个**可视化节点图编辑器**（DataLinkEdGraph）来实现。用户可以在编辑器中创建数据流图，图中的每个节点代表一个数据处理步骤（如解析 JSON、转换数据类型、过滤数据），节点之间通过引脚（Pin）连接，形成数据管道。这使得复杂的、数据驱动的动画逻辑变得直观且易于维护。

## 使用场景

- **实时数据可视化**：从外部 API（如天气、股票、IoT 传感器）获取 JSON 数据，通过 DataLink 解析后，实时更新场景中物体的位置、颜色或材质。
- **数据驱动动画**：将结构化数据（如来自 DataTable 或自定义结构体）转换为动画曲线或关键帧，驱动角色或物体的动画。
- **外部系统集成**：通过 WebSocket 或 HTTP 节点，与外部控制软件（如 TouchDesigner、Processing）进行双向通信，实现交互式装置或现场演出控制。
- **复杂数据转换**：需要将一种数据格式（如嵌套的 JSON）映射到另一种格式（如 UE 的 FStruct）时，使用自定义映射节点进行精确控制。

## 蓝图用法

DataLink 的核心功能通过其节点图编辑器暴露，但其底层节点（`UDataLinkNode` 子类）也提供了蓝图可用的接口，主要用于在运行时动态创建和执行数据流。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `String to JSON` | 将字符串解析为 JSON 对象。 | `UDataLinkStringToJson` |
| `Struct to JSON` | 将 UE 结构体序列化为 JSON 对象。 | `UDataLinkJsonFromStruct` |
| `JSON to Struct` | 将 JSON 对象反序列化为指定的 UE 结构体，支持自定义映射。 | `UDataLinkJsonToStruct` |

### 使用示例（蓝图描述）

1.  **创建数据流执行器**：在蓝图中，你需要先获取或创建一个 `UDataLinkExecutor` 对象，它是驱动整个数据流图执行的引擎。
2.  **构建节点图**：虽然通常在编辑器中可视化构建，但理论上可以通过蓝图动态创建 `UDataLinkNode` 的实例并连接它们的引脚（`FDataLinkPin`）。
3.  **执行数据流**：调用 `UDataLinkExecutor` 的执行函数，传入初始数据（例如，一个包含 JSON 字符串的 `FString`）。执行器会按照节点图的拓扑顺序依次调用每个节点的 `OnExecute` 函数。
4.  **获取结果**：执行完成后，可以从输出引脚获取处理后的数据（如一个 `FJsonObject` 或一个填充好的 `FStructView`）。

## C++ 用法

### 头文件引入

```cpp
#include "DataLinkNode.h"
#include "DataLinkExecutor.h"
#include "DataLinkJsonUtils.h"
#include "DataLinkJsonToStruct.h"
```

### 基本用法

以下示例展示了如何使用 `UDataLinkJsonToStruct` 节点将 JSON 字符串转换为自定义结构体。

```cpp
// 假设已有自定义结构体
USTRUCT(BlueprintType)
struct FMyData
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite)
    FString Name;

    UPROPERTY(BlueprintReadWrite)
    int32 Value;
};

// 在某个函数中
void ConvertJsonToStruct()
{
    // 1. 准备 JSON 字符串
    FString JsonString = TEXT("{\"Name\": \"Test\", \"Value\": 42}");

    // 2. 创建 JSON to Struct 节点实例
    UDataLinkJsonToStruct* JsonToStructNode = NewObject<UDataLinkJsonToStruct>();

    // 3. 配置节点（通常在编辑器属性面板完成，这里演示代码配置）
    // 注意：实际使用中，OutputStruct 和 CustomMapping 通常在资产中预设。
    // JsonToStructNode->OutputStruct = FMyData::StaticStruct();

    // 4. 创建执行器并运行（简化示例，实际需要构建完整的节点图）
    // UDataLinkExecutor* Executor = NewObject<UDataLinkExecutor>();
    // ... 将 JsonToStructNode 添加到执行器的节点图中 ...
    // Executor->Execute(/* 初始输入数据 */);
}
```

### 进阶用法

使用 `UE::DataLinkJson::FindJsonValue` 工具函数从复杂的嵌套 JSON 中提取特定字段。

```cpp
#include "DataLinkJsonUtils.h"
#include "Dom/JsonObject.h"

void ExtractNestedJsonValue()
{
    // 假设有一个复杂的 JSON 对象
    FString ComplexJson = TEXT("{\"A\": {\"B\": [{\"C\": \"FoundIt\"}]}}");
    TSharedPtr<FJsonObject> JsonObject;
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(ComplexJson);
    FJsonSerializer::Deserialize(Reader, JsonObject);

    if (JsonObject.IsValid())
    {
        // 使用点分隔路径访问嵌套值和数组元素
        TSharedPtr<FJsonValue> FoundValue = UE::DataLinkJson::FindJsonValue(JsonObject.ToSharedRef(), TEXT("A.B[0].C"));

        if (FoundValue.IsValid() && FoundValue->Type == EJson::String)
        {
            FString Result = FoundValue->AsString(); // Result == "FoundIt"
            UE_LOG(LogTemp, Log, TEXT("Found value: %s"), *Result);
        }
    }
}
```

## Demo 示例

一个最小的自定义 DataLink 节点示例，该节点将输入的整数乘以2后输出。

**MyDoubleNode.h**
```cpp
#pragma once

#include "DataLinkNode.h"
#include "MyDoubleNode.generated.h"

UCLASS(MinimalAPI, Category="Math", DisplayName="Double Integer")
class UMyDoubleNode : public UDataLinkNode
{
    GENERATED_BODY()

protected:
    //~ Begin UDataLinkNode
    virtual void OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const override;
    virtual EDataLinkExecutionReply OnExecute(FDataLinkExecutor& InExecutor) const override;
    //~ End UDataLinkNode
};
```

**MyDoubleNode.cpp**
```cpp
#include "MyDoubleNode.h"

void UMyDoubleNode::OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const
{
    // 定义输入引脚：一个整数
    Inputs.Add(TEXT("Input")).AsType<int32>();
    // 定义输出引脚：一个整数
    Outputs.Add(TEXT("Output")).AsType<int32>();
}

EDataLinkExecutionReply UMyDoubleNode::OnExecute(FDataLinkExecutor& InExecutor) const
{
    // 从输入引脚获取值
    const int32* InputValue = InExecutor.GetData<int32>(TEXT("Input"));
    if (!InputValue)
    {
        return EDataLinkExecutionReply::Unhandled;
    }

    // 计算结果
    const int32 Result = (*InputValue) * 2;

    // 将结果设置到输出引脚
    InExecutor.SetData(TEXT("Output"), Result);

    return EDataLinkExecutionReply::Handled;
}
```

## 模块依赖

DataLink 插件由多个模块组成，彼此之间存在依赖关系。对于使用者（在自己的模块中使用 DataLink 功能），主要依赖如下：

| 模块 | 用途 |
|---|---|
| `DataLink` | 核心运行时框架，提供 `UDataLinkNode`、`UDataLinkExecutor` 等基类和核心数据结构。 |
| `DataLinkJson` | 提供 JSON 相关的节点（如 `String to JSON`, `JSON to Struct`）和工具函数。 |
| `DataLinkHttp` | 提供 HTTP 请求节点，用于从 Web API 获取数据。 |
| `DataLinkWebSocket` | 提供 WebSocket 通信节点，用于实时双向数据流。 |
| `DataLinkDataTable` | 提供与 DataTable 集成的节点。 |
| `DataLinkEdGraph` | （编辑器/UncookedOnly）提供节点图编辑器的 UI 和逻辑。 |
| `DataLinkEditor` | （编辑器）提供编辑器集成和资产类型。 |
| `DataLinkJsonEditor` | （编辑器）提供 JSON 相关节点的编辑器自定义。 |

## 维护状态

### 近期更新

```
- 2025-04-22 94f961385e8e Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction
```
*解读：这是将插件从 `Experimental` 目录迁移到 `VirtualProduction` 目录的提交，标志着其重要性提升，但功能本身可能已存在一段时间。*

### 维护评价

- **创建时间**：插件于 2025 年 4 月创建，非常年轻。
- **更新频率**：目前仅有一条记录在案的提交，是关于目录迁移。这表明插件可能刚从实验阶段转入正式分类，**功能本身可能已相对稳定，但后续的活跃开发和维护情况尚不明确**。
- **实验性状态**：`.uplugin` 中 `IsBetaVersion` 为 `true`，明确标记为**实验性功能**。
- **推荐使用**：**谨慎推荐**。该插件提供了强大且直观的数据流处理能力，非常适合 Motion Design 工作流。但由于其**实验性标签**和**极短的公开历史**，在生产环境中使用前需要充分测试，并做好应对未来 API 变更或功能调整的准备。建议关注后续的更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink)
- 官方文档：暂无
- 测试用例：暂无公开路径