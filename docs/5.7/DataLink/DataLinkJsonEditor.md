# Motion Design Data Link - DataLinkJsonEditor

> （无描述）

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataLinkJsonEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink/Source/DataLinkJsonEditor) | |

## 用途

`DataLinkJsonEditor` 是 `DataLinkJson` 模块的编辑器扩展。它为基于 JSON 的数据链接提供了编辑器端的支持，包括自定义的图表节点、资产编辑器界面以及相关的编辑器工具。其主要目的是在 Motion Design 工作流中，让设计师和开发者能够在编辑器内可视化地创建、编辑和调试 JSON 数据流，从而驱动场景中的动态内容。

## 使用场景

- 你在使用 Motion Design 系统，需要从外部 JSON 数据源（如 API 响应、配置文件）获取数据来驱动场景中的元素（如文本、材质参数、动画）。
- 你需要一个可视化的节点图表来设计数据获取、解析和转换的逻辑，而不是编写纯代码。
- 你希望为自定义的 JSON 数据处理逻辑创建可复用的编辑器节点，以便在 Motion Design 图表中使用。

## 蓝图用法

作为编辑器模块，其主要功能通过 C++ API 和编辑器自定义界面暴露。蓝图中可直接使用的节点较少，核心逻辑通常封装在自定义的图表节点中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute` | 执行数据链接节点，处理输入并生成输出。 | `UDataLinkJsonNode` (及其子类) |

### 使用示例（蓝图描述）

在 Motion Design 的数据链接图表中，你可以：
1. 从节点面板拖拽一个 `DataLinkJson` 类别的节点（例如 `Parse Json`）到图表中。
2. 将该节点的输入引脚连接到数据源（如一个 HTTP 请求节点的输出）。
3. 配置节点的属性（如要解析的 JSON 字段路径）。
4. 将节点的输出引脚连接到需要数据的场景元素（如一个文本组件）。

## C++ 用法

### 头文件引入

```cpp
#include "DataLinkJsonEditor.h"
// 通常还需要引入基类头文件
#include "DataLinkEdGraph/Nodes/DataLinkEdNode.h"
```

### 基本用法

创建一个自定义的 JSON 数据处理节点。这通常涉及继承 `UDataLinkJsonNode` 或相关的编辑器节点类。

```cpp
// MyJsonProcessorNode.h
#pragma once
#include "DataLinkJson/Nodes/DataLinkJsonNode.h"
#include "MyJsonProcessorNode.generated.h"

UCLASS()
class UMyJsonProcessorNode : public UDataLinkJsonNode
{
    GENERATED_BODY()

public:
    // 定义节点的输入输出引脚
    virtual void AllocateDefaultPins() override;

    // 核心处理逻辑
    virtual void Execute(const UDataLinkEdNode* InEdNode, const FDataLinkNodeContext& InContext) const override;

    // 节点在编辑器中的显示名称
    virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override;
};
```

```cpp
// MyJsonProcessorNode.cpp
#include "MyJsonProcessorNode.h"

void UMyJsonProcessorNode::AllocateDefaultPins()
{
    // 创建输入引脚
    CreatePin(EGPD_Input, FName("JsonInput"), FName("JSON"));
    // 创建输出引脚
    CreatePin(EGPD_Output, FName("ProcessedOutput"), FName("Result"));
}

void UMyJsonProcessorNode::Execute(const UDataLinkEdNode* InEdNode, const FDataLinkNodeContext& InContext) const
{
    // 从输入引脚获取 JSON 数据
    const TSharedPtr<FJsonValue>& InputJsonValue = InContext.GetInputValue<FJsonValue>(FName("JsonInput"));

    if (InputJsonValue.IsValid())
    {
        // 执行你的自定义 JSON 处理逻辑
        // 例如：提取特定字段、转换格式等
        TSharedPtr<FJsonValue> ProcessedValue = /* ... 你的处理逻辑 ... */;

        // 将结果设置到输出引脚
        InContext.SetOutputValue(FName("ProcessedOutput"), ProcessedValue);
    }
}

FText UMyJsonProcessorNode::GetNodeTitle(ENodeTitleType::Type TitleType) const
{
    return NSLOCTEXT("MyNodes", "ProcessorNodeTitle", "My JSON Processor");
}
```

### 进阶用法

结合 `DataLinkEdGraph` 模块，为你的自定义节点创建配套的编辑器图表节点类，以实现更丰富的编辑器交互（如自定义外观、右键菜单、属性面板）。

```cpp
// MyJsonProcessorEdNode.h
#pragma once
#include "DataLinkEdGraph/Nodes/DataLinkEdNode.h"
#include "MyJsonProcessorEdNode.generated.h"

UCLASS()
class UMyJsonProcessorEdNode : public UDataLinkEdNode
{
    GENERATED_BODY()

public:
    // 关联到运行时节点类
    virtual UClass* GetNodeClass() const override;

    // 自定义节点在图表中的外观（颜色、图标等）
    virtual FLinearColor GetNodeTitleColor() const override;
    virtual FSlateIcon GetIconAndTint(FLinearColor& OutColor) const override;
};
```

## Demo 示例

一个最小的自定义 JSON 数据过滤节点。

```cpp
// DataLinkJsonFilterNode.h
#pragma once
#include "DataLinkJson/Nodes/DataLinkJsonNode.h"
#include "DataLinkJsonFilterNode.generated.h"

UCLASS()
class UDataLinkJsonFilterNode : public UDataLinkJsonNode
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Filter")
    FString FieldPath;

    virtual void AllocateDefaultPins() override;
    virtual void Execute(const UDataLinkEdNode* InEdNode, const FDataLinkNodeContext& InContext) const override;
    virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override;
};
```

```cpp
// DataLinkJsonFilterNode.cpp
#include "DataLinkJsonFilterNode.h"
#include "Dom/JsonValue.h"

void UDataLinkJsonFilterNode::AllocateDefaultPins()
{
    CreatePin(EGPD_Input, FName("InJson"), FName("JSON"));
    CreatePin(EGPD_Output, FName("OutValue"), FName("Value"));
}

void UDataLinkJsonFilterNode::Execute(const UDataLinkEdNode* InEdNode, const FDataLinkNodeContext& InContext) const
{
    const TSharedPtr<FJsonValue>& JsonValue = InContext.GetInputValue<FJsonValue>(FName("InJson"));
    if (JsonValue.IsValid() && !FieldPath.IsEmpty())
    {
        // 简单的字段路径查找（例如 “data.name”）
        TArray<FString> PathSegments;
        FieldPath.ParseIntoArray(PathSegments, TEXT("."));

        TSharedPtr<FJsonValue> CurrentValue = JsonValue;
        for (const FString& Segment : PathSegments)
        {
            if (CurrentValue.IsValid() && CurrentValue->Type == EJson::Object)
            {
                const TSharedPtr<FJsonObject>* ObjectPtr;
                if (CurrentValue->TryGetObject(ObjectPtr))
                {
                    CurrentValue = (*ObjectPtr)->TryGetField(Segment);
                }
                else
                {
                    CurrentValue.Reset();
                    break;
                }
            }
            else
            {
                CurrentValue.Reset();
                break;
            }
        }

        InContext.SetOutputValue(FName("OutValue"), CurrentValue);
    }
}

FText UDataLinkJsonFilterNode::GetNodeTitle(ENodeTitleType::Type TitleType) const
{
    return NSLOCTEXT("DataLinkJson", "FilterNodeTitle", "Filter JSON Field");
}
```

## 模块依赖

从 `DataLinkJsonEditor.Build.cs` 分析，该模块依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `DataLinkJson` | 提供 JSON 数据链接的运行时核心功能和节点基类。 |
| `DataLinkEdGraph` | 提供数据链接图表编辑器的基础框架和节点类。 |
| `DataLinkEditor` | 提供数据链接编辑器的通用工具和界面。 |

## 维护状态

### 近期更新

```
- 94f961385e8e Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction
```
*解读：该模块随整个 DataLink 插件从实验性目录迁移至正式的虚拟制作目录，标志着其功能趋于稳定，并被整合到核心的 Motion Design 工作流中。*

### 维护评价

- **创建时间**：2025年4月，非常新。
- **最近更新**：仅有一次迁移记录，表明模块刚完成架构调整。
- **活跃度**：作为新迁移的模块，预计会随着 Motion Design 系统的开发而持续更新。
- **已知问题/限制**：标记为 `IsBetaVersion=true`，属于测试阶段，API 和功能可能发生变化。
- **推荐使用**：适用于正在使用或评估 Motion Design 数据链接功能的项目。由于是 Beta 版本，不建议在追求稳定性的生产环境中直接依赖，但非常适合用于原型开发和功能探索。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink/Source/DataLinkJsonEditor)
- [官方文档]() (无)
- [测试用例]() (未在提供的路径中找到)