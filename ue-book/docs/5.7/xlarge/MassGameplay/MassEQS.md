# Mass EQS

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MassActors` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSignals` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassEQS 是 MassGameplay 插件中的一个模块，其核心功能是将 Unreal Engine 的环境查询系统（EQS）与 Mass Entity 框架集成。它解决的核心问题是：如何让 EQS 能够高效地查询和评估由 Mass 系统管理的成千上万的实体（如 NPC、单位、物体）。

传统的 EQS 查询通常基于 Actor 或场景中的静态物体，当面对海量实体时，性能开销巨大。MassEQS 通过将 EQS 的生成器（Generator）和测试（Test）请求异步发送到 Mass 处理器（Processor）中执行，利用 Mass 的高性能数据处理能力来完成查询，从而实现了对大规模实体的高效 AI 决策和空间感知。

## 使用场景

- **大规模 RTS 游戏**：你需要为成百上千的单位寻找攻击目标、移动路径或资源点。
- **开放世界游戏**：你需要让大量 NPC 感知周围的玩家、其他 NPC 或兴趣点，并做出反应。
- **群体模拟**：你需要基于实体标签（Tags）或属性（Traits）对海量实体进行筛选和排序。
- **性能敏感的 AI 系统**：你的 AI 需要频繁进行空间查询，但传统的 Actor-based EQS 成为性能瓶颈。

## 蓝图用法

MassEQS 提供了一个蓝图函数库 `UMassEQSBlueprintLibrary`，用于在蓝图中处理 EQS 查询返回的 Mass 实体信息。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Send Signal To Entity` | 向指定的 Mass 实体发送一个信号（FName）。 | `UMassEQSBlueprintLibrary` |
| `Get Cached Entity Position` | 获取 EQS 查询时缓存的实体位置。 | `UMassEQSBlueprintLibrary` |
| `Get Current Entity Position` | 获取实体的实时位置（需要查询 Mass 实体管理器）。 | `UMassEQSBlueprintLibrary` |
| `Entity Comparison` | 比较两个 `FMassEnvQueryEntityInfoBlueprintWrapper` 是否代表同一实体。 | `UMassEQSBlueprintLibrary` |
| `Contains Entity` | 检查一个实体信息数组中是否包含特定实体。 | `UMassEQSBlueprintLibrary` |
| `Get Environment Query Result As Entity Info` | 将 EQS 查询结果（`UEnvQueryInstanceBlueprintWrapper`）转换为 `FMassEnvQueryEntityInfoBlueprintWrapper` 数组。 | `UMassEQSBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **获取 EQS 结果中的 Mass 实体**：
    *   使用 `Run Environment Query` 节点执行一个配置了 `Mass Entity Handles` 生成器的 EQS 查询。
    *   将查询结果（`UEnvQueryInstanceBlueprintWrapper`）连接到 `Get Environment Query Result As Entity Info` 节点。
    *   输出的 `TArray<FMassEnvQueryEntityInfoBlueprintWrapper>` 即为查询到的 Mass 实体列表。

2.  **向查询到的实体发送信号**：
    *   遍历上一步得到的实体信息数组。
    *   对每个元素使用 `Send Signal To Entity` 节点，并传入一个信号名称（如 `“Attack”`）。
    *   该信号将通过 `UMassSignalSubsystem` 发送给对应的 Mass 实体，触发其信号处理器。

## C++ 用法

MassEQS 的核心是允许你创建自定义的 EQS 生成器和测试，这些生成器和测试的工作将被委托给 Mass 处理器异步执行。

### 头文件引入

```cpp
#include “MassEQS.h”
#include “MassEQSTypes.h”
#include “MassEQSSubsystem.h”
#include “Generators/MassEnvQueryGenerator.h”
#include “Tests/MassEnvQueryTest.h”
```

### 基本用法

要创建一个自定义的 Mass EQS 生成器，你需要继承 `UMassEnvQueryGenerator` 并实现几个关键虚函数。

```cpp
// MyMassEQSGenerator.h
#pragma once
#include “Generators/MassEnvQueryGenerator.h”
#include “MyMassEQSGenerator.generated.h”

UCLASS()
class UMyMassEQSGenerator : public UMassEnvQueryGenerator
{
    GENERATED_BODY()
public:
    // 实现 IMassEQSRequestInterface
    virtual TUniquePtr<FMassEQSRequestData> GetRequestData(FEnvQueryInstance& QueryInstance) const override;
    virtual UClass* GetRequestClass() const override { return StaticClass(); }
    virtual bool TryAcquireResults(FEnvQueryInstance& QueryInstance) const override;
};

// MyMassEQSGenerator.cpp
#include “MyMassEQSGenerator.h”
#include “MassEQSSubsystem.h”

TUniquePtr<FMassEQSRequestData> UMyMassEQSGenerator::GetRequestData(FEnvQueryInstance& QueryInstance) const
{
    // 1. 收集 EQS 查询的上下文信息（如查询中心位置）
    TArray<FVector> ContextLocations;
    // ... 从 QueryInstance 获取上下文位置 ...

    // 2. 创建并返回包含查询参数的请求数据
    return MakeUnique<FMassEQSRequestData_MyCustom>(ContextLocations, /* 其他参数 */);
}

bool UMyMassEQSGenerator::TryAcquireResults(FEnvQueryInstance& QueryInstance) const
{
    // 1. 尝试从 MassEQSSubsystem 获取处理结果
    UMassEQSSubsystem* MassEQSSubsystem = UWorld::GetSubsystem<UMassEQSSubsystem>(QueryInstance.World);
    TUniquePtr<FMassEQSRequestData> ResultData = MassEQSSubsystem->TryAcquireResults(MassEQSRequestHandler.GetRequestHandle());

    if (ResultData)
    {
        // 2. 将结果数据转换为具体的类型
        FMassEQSResultData_MyCustom* MyResult = FMassEQSUtils::TryAndEnsureCast<FMassEQSResultData_MyCustom>(ResultData);
        if (MyResult)
        {
            // 3. 将结果（如实体信息列表）填充到 QueryInstance 的 Items 中
            for (const FMassEnvQueryEntityInfo& EntityInfo : MyResult->GeneratedEntityInfo)
            {
                QueryInstance.AddItemData<UEnvQueryItemType_MassEntityHandle>(EntityInfo);
            }
            return true; // 结果获取成功
        }
    }
    return false; // 结果尚未就绪
}
```

### 进阶用法

创建一个自定义的 Mass EQS 测试，用于根据实体标签进行过滤。

```cpp
// MyMassEQSTest.h
#pragma once
#include “Tests/MassEnvQueryTest.h”
#include “MyMassEQSTest.generated.h”

UCLASS()
class UMyMassEQSTest : public UMassEnvQueryTest
{
    GENERATED_BODY()
public:
    virtual TUniquePtr<FMassEQSRequestData> GetRequestData(FEnvQueryInstance& QueryInstance) const override;
    virtual UClass* GetRequestClass() const override { return StaticClass(); }
    virtual bool TryAcquireResults(FEnvQueryInstance& QueryInstance) const override;

protected:
    UPROPERTY(EditAnywhere, Category = “Test”)
    TArray<FInstancedStruct> RequiredTags;
};

// MyMassEQSTest.cpp
#include “MyMassEQSTest.h”
#include “MassEQSSubsystem.h”
#include “MassEntityTypes.h”

TUniquePtr<FMassEQSRequestData> UMyMassEQSTest::GetRequestData(FEnvQueryInstance& QueryInstance) const
{
    // 1. 获取当前查询实例中待测试的实体句柄列表
    TArray<FMassEntityHandle> EntityHandles;
    // ... 从 QueryInstance.Items 中提取 EntityHandles ...

    // 2. 创建请求数据，包含待测试的实体和测试参数（标签）
    return MakeUnique<FMassEQSRequestData_MyTest>(EntityHandles, RequiredTags);
}

bool UMyMassEQSTest::TryAcquireResults(FEnvQueryInstance& QueryInstance) const
{
    UMassEQSSubsystem* MassEQSSubsystem = UWorld::GetSubsystem<UMassEQSSubsystem>(QueryInstance.World);
    TUniquePtr<FMassEQSRequestData> ResultData = MassEQSSubsystem->TryAcquireResults(MassEQSRequestHandler.GetRequestHandle());

    if (ResultData)
    {
        FMassEQSResultData_MyTest* MyResult = FMassEQSUtils::TryAndEnsureCast<FMassEQSResultData_MyTest>(ResultData);
        if (MyResult)
        {
            // 1. 遍历查询实例中的所有项
            for (FEnvQueryInstance::ItemIterator It(this, QueryInstance); It; ++It)
            {
                // 2. 获取该项对应的实体句柄
                const FMassEnvQueryEntityInfo& EntityInfo = UEnvQueryItemType_MassEntityHandle::GetValue(It.GetRawData());
                // 3. 在结果映射中查找该实体是否通过测试
                const bool* bPassed = MyResult->ResultMap.Find(EntityInfo.EntityHandle);
                if (bPassed)
                {
                    // 4. 根据测试结果设置该项的分数
                    It.SetScore(TestPurpose, FilterType, *bPassed ? 1.0f : 0.0f);
                }
            }
            return true;
        }
    }
    return false;
}
```

## Demo 示例

以下是一个最小化的自定义 Mass EQS 生成器示例，它查询指定半径内的所有 Mass 实体。

**MyRadiusMassEntityGenerator.h**
```cpp
#pragma once
#include “Generators/MassEnvQueryGenerator.h”
#include “DataProviders/AIDataProvider.h”
#include “MyRadiusMassEntityGenerator.generated.h”

UCLASS(meta=(DisplayName=”My Radius Mass Entity Generator”))
class UMyRadiusMassEntityGenerator : public UMassEnvQueryGenerator
{
    GENERATED_BODY()
public:
    UMyRadiusMassEntityGenerator();
    virtual TUniquePtr<FMassEQSRequestData> GetRequestData(FEnvQueryInstance& QueryInstance) const override;
    virtual UClass* GetRequestClass() const override { return StaticClass(); }
    virtual bool TryAcquireResults(FEnvQueryInstance& QueryInstance) const override;

protected:
    UPROPERTY(EditDefaultsOnly, Category=Generator)
    FAIDataProviderFloatValue SearchRadius;

    UPROPERTY(EditAnywhere, Category=Generator)
    TSubclassOf<UEnvQueryContext> SearchCenter;
};
```

**MyRadiusMassEntityGenerator.cpp**
```cpp
#include “MyRadiusMassEntityGenerator.h”
#include “MassEQSSubsystem.h”
#include “MassEQSTypes.h”
#include “EnvironmentQuery/Contexts/EnvQueryContext_Querier.h”

UMyRadiusMassEntityGenerator::UMyRadiusMassEntityGenerator()
{
    SearchCenter = UEnvQueryContext_Querier::StaticClass();
    SearchRadius.DefaultValue = 1000.0f;
}

TUniquePtr<FMassEQSRequestData> UMyRadiusMassEntityGenerator::GetRequestData(FEnvQueryInstance& QueryInstance) const
{
    TArray<FVector> ContextPositions;
    if (!QueryInstance.PrepareContext(SearchCenter, ContextPositions))
    {
        return nullptr;
    }

    float Radius = 0.0f;
    SearchRadius.GetValue(Radius);

    // 复用引擎内置的请求数据结构
    return MakeUnique<FMassEQSRequestData_MassEntityHandles>(ContextPositions, Radius);
}

bool UMyRadiusMassEntityGenerator::TryAcquireResults(FEnvQueryInstance& QueryInstance) const
{
    UMassEQSSubsystem* MassEQSSubsystem = UWorld::GetSubsystem<UMassEQSSubsystem>(QueryInstance.World);
    TUniquePtr<FMassEQSRequestData> ResultData = MassEQSSubsystem->TryAcquireResults(MassEQSRequestHandler.GetRequestHandle());

    if (ResultData)
    {
        // 尝试转换为实体句柄生成器的结果类型
        FMassEnvQueryResultData_MassEntityHandles* HandlesResult = FMassEQSUtils::TryAndEnsureCast<FMassEnvQueryResultData_MassEntityHandles>(ResultData);
        if (HandlesResult)
        {
            // 将结果添加到查询实例
            for (const FMassEnvQueryEntityInfo& EntityInfo : HandlesResult->GeneratedEntityInfo)
            {
                QueryInstance.AddItemData<UEnvQueryItemType_MassEntityHandle>(EntityInfo);
            }
            return true;
        }
    }
    return false;
}
```

## 模块依赖

要使用 MassEQS 模块，你的项目模块需要依赖以下内容：

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass 实体框架的核心，提供实体管理、处理器等基础功能。 |
| `EnvironmentQuerySystem` | Unreal Engine 的环境查询系统（EQS）核心模块。 |
| `MassEQS` | 本模块，提供 Mass 与 EQS 集成的类型、接口和子系统。 |
| `MassGameplay` | （可选）如果使用 MassGameplay 提供的其他功能（如信号、表示等）。 |

## 维护状态

### 近期更新

```
- accbcce541ed Fixup API macros
- e18cf0fed800 PR #13735: Export types from MassEQS
- 0ebe081b7ad3 [MassGameplay] * Fixed non unity compile errors
```

### 维护评价

MassEQS 模块作为实验性功能，仍在积极维护中。最近的提交记录显示，Epic 团队仍在修复编译问题并改进 API（如导出类型）。该模块创建于 2021 年，年龄约 4 年，属于较新的实验性功能。由于其依赖的 MassEntity 框架是 UE5 的核心新特性，MassEQS 的长期支持前景良好。**推荐在需要高性能大规模 AI 查询的项目中使用，但需注意其“实验性”状态，API 可能在未来版本中发生变化。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay/Source/MassEQS)
- [官方文档]()（暂无）
- [测试用例]()（暂未在提供的信息中发现）