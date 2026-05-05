# Motion Design Data Link

> （Description 字段为空）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DataLink` (Runtime), `DataLinkDataTable` (Runtime), `DataLinkEdGraph` (Runtime), `DataLinkEditor` (Runtime), `DataLinkHttp` (Runtime), `DataLinkJson` (Runtime), `DataLinkJsonEditor` (Runtime), `DataLinkWebSocket` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink) | |

## 用途

DataLink 是一个用于虚拟制作（Virtual Production）的数据连接和处理框架。它提供了一个统一的架构，用于从各种外部数据源（如 HTTP API、WebSocket、JSON 文件、DataTable）获取数据，并将其转换、路由到引擎内的各个系统（如材质、蓝图、动画）。其核心是建立一个可扩展的“数据管线”，使得实时数据能够驱动场景中的元素，非常适合需要动态数据输入的虚拟制片、广播图形和交互式体验。

## 使用场景

- 你需要在虚拟制片现场，实时接收来自外部控制系统（如媒体服务器、传感器、自定义软件）的数据，并用它来控制场景中的灯光、材质参数或动画状态。
- 你需要构建一个数据驱动的广播图形系统，数据源可能是实时的 JSON API 或 WebSocket 消息。
- 你需要将来自不同格式（HTTP、JSON、DataTable）的数据统一处理，并映射到引擎内的不同目标。
- 你需要一个可视化的编辑器来设计和调试复杂的数据流。

## 蓝图用法

DataLink 插件主要通过其核心运行时模块暴露蓝图接口，用于创建和管理数据连接。编辑器模块则提供了可视化的图表编辑工具。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Data Link Source` | 创建一个数据源实例（如 HTTP、WebSocket）。 | `UDataLinkSubsystem` |
| `Create Data Link Target` | 创建一个数据目标实例，用于接收和处理数据。 | `UDataLinkSubsystem` |
| `Connect Source to Target` | 将数据源连接到数据目标，建立数据流。 | `UDataLinkSubsystem` |
| `Send Data` | 向指定的数据目标发送数据。 | `UDataLinkTarget` |
| `On Data Received` | 数据目标接收到数据时的委托。 | `UDataLinkTarget` |

*更详细的蓝图 API 请参考各子模块文档，特别是 [DataLink](DataLink.md) 和 [DataLinkEdGraph](DataLinkEdGraph.md)。*

### 使用示例（蓝图描述）

1.  在 BeginPlay 中，使用 `Create Data Link Source` 节点并选择 `DataLinkHttp` 类型，配置好 URL。
2.  使用 `Create Data Link Target` 节点创建一个目标，例如一个自定义的蓝图目标。
3.  使用 `Connect Source to Target` 将两者连接。
4.  在目标蓝图的 `On Data Received` 事件中，解析传入的数据（可能是 JSON），并用它来设置场景中某个 Actor 的材质参数。

## C++ 用法

C++ 用法主要涉及创建自定义的数据源、数据目标或数据处理器，以扩展 DataLink 的功能。

### 头文件引入

```cpp
#include "DataLinkSubsystem.h"
#include "DataLinkSource.h"
#include "DataLinkTarget.h"
```

### 基本用法

创建一个简单的自定义数据目标，用于接收数据。

```cpp
// MyDataLinkTarget.h
#pragma once
#include "DataLinkTarget.h"
#include "MyDataLinkTarget.generated.h"

UCLASS(BlueprintType)
class UMyDataLinkTarget : public UDataLinkTarget
{
    GENERATED_BODY()
public:
    // 重写此函数以处理接收到的数据
    virtual void OnDataReceived(const FDataLinkData& Data) override;
};

// MyDataLinkTarget.cpp
#include "MyDataLinkTarget.h"

void UMyDataLinkTarget::OnDataReceived(const FDataLinkData& Data)
{
    // 处理数据，例如打印日志或更新游戏状态
    UE_LOG(LogTemp, Log, TEXT("DataLink Target Received Data: %s"), *Data.ToString());
}
```

*更多基础用法示例请参考 [DataLink](DataLink.md) 模块文档。*

### 进阶用法

结合 `DataLinkJson` 模块，创建一个能解析特定 JSON 结构并驱动材质参数的数据处理器。

```cpp
// 需要依赖 DataLinkJson 模块
#include "DataLinkJsonProcessor.h"

UCLASS()
class UMyJsonMaterialProcessor : public UDataLinkJsonProcessor
{
    GENERATED_BODY()
public:
    virtual void ProcessJsonData(const TSharedPtr<FJsonObject>& JsonObject) override
    {
        // 从 JSON 对象中提取值
        if (TSharedPtr<FJsonValue> Value = JsonObject->TryGetField(TEXT("EmissiveIntensity")))
        {
            float Intensity = Value->AsNumber();
            // 应用到材质参数
            // ...
        }
    }
};
```

*更复杂的组合用法请参考 [DataLinkHttp](DataLinkHttp.md)、[DataLinkWebSocket](DataLinkWebSocket.md) 和 [DataLinkJson](DataLinkJson.md) 模块文档。*

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何创建一个自定义的数据源，该数据源每秒生成一个随机数并发送给连接的目标。

```cpp
// MyRandomDataSource.h
#pragma once
#include "DataLinkSource.h"
#include "MyRandomDataSource.generated.h"

UCLASS(BlueprintType)
class UMyRandomDataSource : public UDataLinkSource
{
    GENERATED_BODY()
public:
    virtual void Activate() override;
    virtual void Deactivate() override;

private:
    FTimerHandle TimerHandle;
    void GenerateRandomData();
};

// MyRandomDataSource.cpp
#include "MyRandomDataSource.h"
#include "DataLinkData.h"
#include "Engine/World.h"
#include "TimerManager.h"

void UMyRandomDataSource::Activate()
{
    Super::Activate();
    // 每秒触发一次
    GetWorld()->GetTimerManager().SetTimer(TimerHandle, this, &UMyRandomDataSource::GenerateRandomData, 1.0f, true);
}

void UMyRandomDataSource::Deactivate()
{
    GetWorld()->GetTimerManager().ClearTimer(TimerHandle);
    Super::Deactivate();
}

void UMyRandomDataSource::GenerateRandomData()
{
    // 创建一个简单的数据包
    FDataLinkData Data;
    Data.SetValue(FMath::RandRange(0.0f, 1.0f));
    // 广播给所有连接的目标
    BroadcastData(Data);
}
```

## 模块依赖

要使用此插件，你的模块通常需要依赖核心的 `DataLink` 模块。根据你使用的具体功能，可能还需要依赖其他模块。

| 模块 | 用途 |
|---|---|
| `DataLink` | 核心运行时框架，提供数据源、目标、子系统等基础类。 |
| `DataLinkHttp` | 提供基于 HTTP 请求的数据源实现。 |
| `DataLinkWebSocket` | 提供基于 WebSocket 连接的数据源实现。 |
| `DataLinkJson` | 提供 JSON 数据解析和处理功能。 |
| `DataLinkDataTable` | 提供将 DataTable 作为数据源的功能。 |
| `DataLinkEdGraph` | 提供可视化的数据流图表编辑器（仅编辑器）。 |
| `DataLinkEditor` | 提供编辑器工具和资产类型支持。 |
| `DataLinkJsonEditor` | 提供 JSON 数据相关的编辑器工具。 |

*具体依赖关系请参考各子模块的 `Build.cs` 文件。*

## 维护状态

### 近期更新

由于这是一个新创建的插件（创建于 2025 年 4 月），且标记为实验性（Beta），其维护状态和更新历史尚不明确。目前没有可用的 git log 信息。

### 维护评价

- **创建时间**：2025-04-22，非常新的插件。
- **状态**：**实验性 (Beta)**。这意味着 API 可能不稳定，功能可能不完整，并且未来可能会有重大更改。
- **推荐度**：适合在虚拟制作项目中进行**早期评估和原型开发**。不建议在需要长期稳定支持的生产环境中直接依赖。建议密切关注其后续版本更新和文档完善情况。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests/VirtualProduction/DataLink) (路径为推测，可能位于 `Engine/Tests/` 下)