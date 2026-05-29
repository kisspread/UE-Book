# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity（基于 MassEntity 的大规模代理模拟实现）

| 属性 | 值 |
|---|---|
| 中文名 | 大规模玩法 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `MassEQS` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

**注意**: 本文档仅涵盖 `MassGameplay` 插件中的 `MassEQS` 模块。该插件包含多个其他子模块，完整列表请参考插件源码。

## 用途

`MassGameplay` 插件是 Unreal Engine `MassEntity` 框架在“游戏玩法”层的高级实现。`MassEntity` 本身提供基于数据的、高性能的实体组件系统（ECS）架构，而 `MassGameplay` 在此基础上构建了一整套用于模拟大规模代理（如人群、军队、生物群）的工具和子系统。

本模块 `MassEQS` 的核心用途是**将 Mass Entity 与环境查询系统（EQS）连接起来**。它允许 EQS 查询直接、高效地在成千上万的 Mass Entity 上运行，而无需为每个实体创建传统 Actor。这解决了传统 Actor 模型在处理海量单位时的性能瓶颈，是实现大规模 RTS 单位AI、人群模拟、生态模拟等高级功能的关键。

## 使用场景

- 你正在开发一款即时战略游戏（RTS），需要让数千个单位根据环境（如资源点、敌方位置）进行智能寻路和决策 → 使用 `MassEQS` 进行高效的群体EQS查询。
- 你的开放世界游戏中有大量的NPC（如市民、动物），需要它们根据玩家的位置、任务状态等动态调整行为 → 使用 `MassEQS` 为这些非玩家Mass实体执行条件筛选和目标选择。
- 你在制作一个模拟经营或生存游戏，需要模拟成千上万的虚拟生命（如昆虫、鱼群）对环境变化（食物、威胁）做出反应 → 使用 `MassEQS` 快速筛选出符合条件的实体群。
- 你希望利用 EQS 强大的评分和筛选能力，但目标不是传统的 Actor，而是海量的、轻量的 Mass Entity。

## 蓝图用法

通过 `UMassEQSBlueprintLibrary` 提供一系列蓝图节点，用于在蓝图中与 Mass Entity 的 EQS 结果进行交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SendSignalToEntity` | 向指定的 Mass Entity 发送一个信号。 | `UMassEQSBlueprintLibrary` |
| `GetEnviromentQueryResultAsEntityInfo` | 将一次 EQS 查询的完整结果转换为 `Mass Entity Info` 数组，以便在蓝图中进一步处理。 | `UMassEQSBlueprintLibrary` |
| `EntityToString` | 将 Mass Entity 信息转换为可读的字符串，用于调试。 | `UMassEQSBlueprintLibrary` |
| `GetCachedEntityPosition` | 获取在 EQS 查询时缓存的实体位置。 | `UMassEQSBlueprintLibrary` |
| `GetCurrentEntityPosition` | 获取实体当前的实时位置。 | `UMassEQSBlueprintLibrary` |
| `EntityComparison` | 比较两个 Mass Entity 信息是否相同（用于蓝图中自定义比较逻辑）。 | `UMassEQSBlueprintLibrary` |
| `ContainsEntity` | 检查一个 Mass Entity 信息数组是否包含特定的实体。 | `UMassEQSBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **执行EQS查询并获取Mass实体结果**：
    - 首先，使用标准的“运行环境查询”（`Run Environment Query`）节点执行一个配置好的 EQS。
    - 将该节点的 `Query Instance` 输出引脚连接到 `GetEnviromentQueryResultAsEntityInfo` 节点的输入。
    - 该节点会输出一个 `Mass Entity Info` 蓝图数组（`TArray<FMassEnvQueryEntityInfoBlueprintWrapper>`），包含了所有符合 EQS 条件的 Mass 实体。
2.  **遍历并操作结果中的实体**：
    - 使用 `ForEachLoop` 节点遍历上一步得到的 `Mass Entity Info` 数组。
    - 在循环体内，可以使用 `GetCachedEntityPosition` 获取实体在查询时的位置。
    - 调用 `SendSignalToEntity`，为当前遍历到的实体发送一个预设的信号（例如 `Attack`, `Flee`），触发其行为改变。

## C++ 用法

`MassEQS` 模块通过 `UMassEQSSubsystem` 管理 EQS 请求队列，并提供基类供创建自定义的 Mass 化的 EQS 生成器（Generator）和测试（Test）。

### 头文件引入

```cpp
#include “MassEQS.h”
#include “MassEQSSubsystem.h”
#include “Generators/MassEnvQueryGenerator.h”
#include “MassEQSTypes.h”
```

### 基本用法：查询Mass实体

以下代码片段展示了如何以编程方式运行一个使用了 Mass 生成器的 EQS 查询。

```cpp
// 1. 获取 Mass EQS 子系统
UMassEQSSubsystem* MassEQSSubsystem = GetWorld()->GetSubsystem<UMassEQSSubsystem>();
if (!MassEQSSubsystem) return;

// 2. 构建 EQS 查询模板 (假设 QueryTemplate 已在蓝图/编辑器中创建好，并使用了 UMassEnvQueryGenerator_MassEntityHandles)
UEnvQuery* QueryTemplate = MyEQSAsset;
FEnvQueryRequest QueryRequest(QueryTemplate, this);
QueryRequest.Execute(EEnvQueryRunMode::SingleResult, this, &AMyActor::OnEQSQueryFinished);

// 3. 回调函数中处理结果
void AMyActor::OnEQSQueryFinished(TSharedPtr<FEnvQueryResult> Result)
{
    if (Result && Result->IsSuccessful())
    {
        // 使用 MassEQS 工具函数将结果转换为实体句柄数组
        TArray<FMassEntityHandle> EntityHandles;
        FMassEQSUtils::GetAllAsEntityHandles(*Result, EntityHandles);
        
        // 现在可以对这一群 Mass 实体进行操作了
        // 例如，通过 MassEntityManager 为它们添加或移除 Fragment/Tag
    }
}
```

### 进阶用法：创建自定义Mass EQS生成器

通过继承 `UMassEnvQueryGenerator` 来创建自定义的、能在 Mass 上高效运行的 EQS 生成器。

```cpp
// MyMassEnvQueryGenerator.h
#pragma once
#include “Generators/MassEnvQueryGenerator.h”
#include “MyMassEnvQueryGenerator.generated.h”

UCLASS(meta=(DisplayName=”My Custom Mass Generator”))
class UMyMassEnvQueryGenerator : public UMassEnvQueryGenerator
{
    GENERATED_BODY()

public:
    virtual TUniquePtr<FMassEQSRequestData> GetRequestData(FEnvQueryInstance& QueryInstance) const override;
    virtual UClass* GetRequestClass() const override { return StaticClass(); }
    virtual bool TryAcquireResults(FEnvQueryInstance& QueryInstance) const override;

protected:
    UPROPERTY(EditDefaultsOnly, Category=Generator)
    FAIDataProviderFloatValue MySearchRadius;
};
```

```cpp
// MyMassEnvQueryGenerator.cpp
#include “MyMassEnvQueryGenerator.h”
#include “MassEQSSubsystem.h”
#include “MassEQSUtils.h”

TUniquePtr<FMassEQSRequestData> UMyMassEnvQueryGenerator::GetRequestData(FEnvQueryInstance& QueryInstance) const
{
    // 收集查询上下文（如玩家位置）
    TArray<FVector> ContextLocations;
    QueryInstance.PrepareContext(GetMutableDefault<UMyMassEnvQueryGenerator>(), ContextLocations);
    
    // 创建请求数据包
    auto RequestData = MakeUnique<FMassEQSRequestData_MyCustomType>();
    RequestData->ContextPositions = ContextLocations;
    RequestData->SearchRadius = MySearchRadius.GetValue();
    
    return RequestData;
}

bool UMyMassEnvQueryGenerator::TryAcquireResults(FEnvQueryInstance& QueryInstance) const
{
    // 尝试从子系统获取处理完毕的结果
    auto* MassEQSSubsystem = QueryInstance.World->GetSubsystem<UMassEQSSubsystem>();
    TUniquePtr<FMassEQSRequestData> ResultData = MassEQSSubsystem->TryAcquireResults(MassEQSRequestHandler.RequestHandle);
    
    if (ResultData)
    {
        // 将结果转换为特定类型并填充到 EQS 查询项中
        auto* SpecificResult = FMassEQSUtils::TryAndEnsureCast<FMassEnvQueryResultData_MyCustomType>(ResultData);
        if (SpecificResult)
        {
            for (const FMassEnvQueryEntityInfo& EntityInfo : SpecificResult->GeneratedEntityInfo)
            {
                QueryInstance.AddItemData<FMassEnvQueryEntityInfo>(EntityInfo);
            }
            return true; // 结果就绪
        }
    }
    return false; // 结果尚未准备好
}
```

## Demo 示例

一个最小化的自定义 Mass EQS 生成器示例，用于查找所有拥有 `FTransformFragment` 的实体。

```cpp
// FindAllMassEntitiesGenerator.h
#pragma once
#include “Generators/MassEnvQueryGenerator.h”
#include “FindAllMassEntitiesGenerator.generated.h”

UCLASS(meta=(DisplayName=”Find All Mass Entities”))
class UFindAllMassEntitiesGenerator : public UMassEnvQueryGenerator
{
    GENERATED_BODY()
    
public:
    UFindAllMassEntitiesGenerator();
    
    virtual TUniquePtr<FMassEQSRequestData> GetRequestData(FEnvQueryInstance& QueryInstance) const override;
    virtual UClass* GetRequestClass() const override { return StaticClass(); }
    virtual bool TryAcquireResults(FEnvQueryInstance& QueryInstance) const override;
    
    virtual FText GetDescriptionTitle() const override;
    virtual FText GetDescriptionDetails() const override;
};
```

```cpp
// FindAllMassEntitiesGenerator.cpp
#include “FindAllMassEntitiesGenerator.h”
#include “MassEQSSubsystem.h”
#include “MassEQSUtils.h”
#include “MassEQSTypes.h”

UFindAllMassEntitiesGenerator::UFindAllMassEntitiesGenerator()
{
    // 默认生成器的属性，如 Item Type
    ItemType = UEnvQueryItemType_MassEntityHandle::StaticClass();
}

TUniquePtr<FMassEQSRequestData> UFindAllMassEntitiesGenerator::GetRequestData(FEnvQueryInstance& QueryInstance) const
{
    // 此生成器不需要任何参数，返回基础请求数据
    return MakeUnique<FMassEQSRequestData>();
}

bool UFindAllMassEntitiesGenerator::TryAcquireResults(FEnvQueryInstance& QueryInstance) const
{
    UMassEQSSubsystem* MassEQSSubsystem = QueryInstance.World->GetSubsystem<UMassEQSSubsystem>();
    TUniquePtr<FMassEQSRequestData> ResultData = MassEQSSubsystem->TryAcquireResults(MassEQSRequestHandler.RequestHandle);
    
    if (ResultData)
    {
        // 假设对应的处理器（Processor）已经处理完毕，结果类型是 FMassEnvQueryResultData_MassEntityHandles
        auto* HandlesResult = FMassEQSUtils::TryAndEnsureCast<FMassEnvQueryResultData_MassEntityHandles>(ResultData);
        if (HandlesResult)
        {
            for (const FMassEnvQueryEntityInfo& Info : HandlesResult->GeneratedEntityInfo)
            {
                QueryInstance.AddItemData<FMassEnvQueryEntityInfo>(Info);
            }
            return true;
        }
    }
    return false;
}

FText UFindAllMassEntitiesGenerator::GetDescriptionTitle() const
{
    return FText::FromString(“Find All Mass Entities”);
}

FText UFindAllMassEntitiesGenerator::GetDescriptionDetails() const
{
    return FText::FromString(“Generates all entities that have a Transform fragment.”);
}
```

## 模块依赖

`MassEQS` 模块依赖于以下 Mass 框架及 AI 模块。要在你的项目中使用此模块，需要在你的 `.Build.cs` 中添加相应依赖。

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass 核心框架，提供 ECS 基础。 |
| `MassEntityEditor` | 提供 Mass 实体的编辑器支持。 |
| `MassEQS` | 本模块自身。 |
| `AIModule` | 提供 EQS 环境查询系统的基础架构。 |
| `GameplayTasks` | 提供异步任务框架，用于 EQS 请求。 |

## 维护状态

该模块（以及所属的 `MassGameplay` 插件）处于**实验性**状态，但维护非常活跃。

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚了对 MassAgentComponent 的修改，可能影响代理实体表示。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 修复了在 Actor 就绪前就关闭 ISM（实例化静态网格体）导致的视觉问题。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了在人群中处理非傀儡 Actor（非由 Mass 驱动的 Actor）的逻辑。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复了 LOD 计算器中按查看器计算 LOD 路径的一系列已有 Bug。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M... | 代码重构，将手动计算的标志改用新的引擎宏，提高一致性。 |

### 维护评价

- **状态**：**活跃维护中**。尽管插件的 `IsExperimentalVersion` 标记为 `true`，表明它还未达到正式发布版本，但近期的 git 历史（截至 2026 年 5 月）显示有持续的、实质性的功能改进和 Bug 修复。
- **风险**：作为实验性功能，其 API、行为和内部实现可能会在未来版本中发生变化。
- **推荐**：**推荐用于学习和实验**，尤其是在评估 Mass 框架能力或开发原型时。对于需要长期稳定性的生产项目，需谨慎评估并密切关注版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [官方文档]() （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Tests) (如果存在)