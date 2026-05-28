# Mover Integrations

> Mover Integrations is a Unreal Engine plugin acting as an umbrella to cover a variety of modules supporting Mover's integration with other plugins, such as animation, AI, and other gameplay systems.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Mover集成桥梁 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MoverIntegrations` (Runtime), `MoverMassIntegration` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-07 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MoverIntegrations) | |

## 用途

MoverIntegrations 是一个**实验性的桥梁型插件**，其核心目的是为了让 Unreal Engine 的 **Mover** 系统能够与其他框架和插件进行集成。它本身不实现复杂的游戏逻辑，而是作为一个“集成中心”，包含多个子模块，用于处理 Mover 与特定外部系统（如 Mass 实体框架、动画系统、AI 系统等）之间的数据转换和协同工作。它解决的是 Mover 系统在扩展性和与其他系统并行工作时的集成问题。

## 使用场景

- 你在构建一个基于 **Mass 实体框架（Mass Entity Framework）** 的开放世界游戏，并希望大量 AI 或物理实体能够使用 **Mover** 系统进行移动。
- 你需要让 **Mass 实体** 中的“能力（Fragment）”与 **Mover** 组件中的“运动模式/设置”能够相互理解和转换。
- 你计划为 Mover 系统开发针对特定动画系统或 AI 行为树的集成模块。

## 蓝图用法

此插件主要为 C++ 集成提供基础，其子模块 `MoverMassIntegration` 提供了关键的翻译器（Translators）类，这些类可能暴露少量蓝图可用的接口用于调试或初始设置。具体蓝图节点需参阅子模块文档。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| *（需参阅子模块 `MoverMassIntegration` 文档获取具体函数）* | 用于在 Mass 实体和 Mover 组件之间转换移动状态和输入 | `UMoverMassTranslator` 等 |

## C++ 用法

此插件的价值主要体现在 C++ 层面，为 Mass 和 Mover 的深度集成提供底层支持。

### 头文件引入

```cpp
#include "MoverIntegrationsModule.h"
#include "MoverMassTranslator.h" // 来自 MoverMassIntegration 模块
```

### 基本用法

在你自己的游戏模块中，使用 `MoverMassIntegration` 模块提供的翻译器来同步 Mass 实体和 Mover 组件的状态。

```cpp
// 假设你有一个 Mass 实体处理器，需要处理带有移动能力的实体
void UMyMassProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // ... 获取实体和 Mover 组件数据 ...

    // 使用翻译器将 Mass 实体的移动意图（如速度）转换为 Mover 能识别的输入
    FMoverDataCollectionInput Input;
    UMoverMassTranslator::TranslateMassToMoverInput(MassVelocity, OtherMassData, Input);

    // 将转换后的输入应用到 Mover 组件
    if (MoverComponent)
    {
        MoverComponent->ApplyMovementInput(Input);
    }
}
```
*(示例逻辑基于集成原理推断，具体 API 请参阅 `MoverMassIntegration` 模块文档)*

## Demo 示例

一个最小的示例，展示如何在 Mass 实体处理器中使用 Mover 集成。

### MyMoverMassProcessor.h
```cpp
#pragma once
#include "MassProcessor.h"
#include "MyMoverMassProcessor.generated.h"

UCLASS()
class UMyMoverMassProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

### MyMoverMassProcessor.cpp
```cpp
#include "MyMoverMassProcessor.h"
#include "MoverMassTranslator.h"
#include "MoverComponent.h"

void UMyMoverMassProcessor::ConfigureQueries()
{
    // 查询拥有 Mover 组件和特定移动能力（Fragment）的实体
    EntityQuery.AddRequirement<FMoverComponent>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMyMovementDesireFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.RegisterWithProcessor(*this);
}

void UMyMoverMassProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        // ... 获取实体数据数组 ...
        TConstArrayView<FMyMovementDesireFragment> DesiresList = Context.GetFragmentView<FMyMovementDesireFragment>();
        TArrayView<FMoverComponent*> MoverComponentsList = Context.GetMutableFragmentView<FMoverComponent>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            if (MoverComponentsList[i])
            {
                // 使用翻译器转换数据
                FMoverDataCollectionInput Input;
                UMoverMassTranslator::TranslateMassToMoverInput(DesiresList[i].DesiredVelocity, Input);

                // 应用到 Mover
                MoverComponentsList[i]->ApplyMovementInput(Input);
            }
        }
    });
}
```

## 模块依赖

使用 `MoverMassIntegration` 模块需要依赖以下关键模块：

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass 实体框架核心，提供实体管理和处理器基类。 |
| `Mover` | Mover 系统本身，提供移动组件和数据结构。 |
| `MassMovement` | Mass 框架中与移动相关的片段（Fragment）和处理器。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c61e2782` | [Mass] Add Mover input-component bridge to MoverMassIntegration plugin | 为 MoverMassIntegration 插件添加了 Mover 输入组件桥接功能。 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 从 MassEntity 中抽离出 MassCore 模块，这是 Mass 框架的重构。 |
| 2025-06-10 | `675fd5ae` | CIS issue#936427: Compile errors in EngineRuntimeTests.h, MoverMassTranslators.h and MoverMassTransl | 修复了编译错误，主要是针对测试和翻译器文件的修正。 |
| 2025-05-07 | `1207fa81` | Mover: Adding UE5 Mover-Mass translators along with a Mover Integrations plugin to house various int | 插件创建提交，加入了 Mover-Mass 翻译器。 |

### 维护评价

**活跃维护中**。该插件于 2025 年 5 月创建，至今约 1 年，属于较新的实验性插件。从提交历史看，在 **2026 年仍有实质性更新**（如添加输入组件桥接），表明 Epic Games 对其仍在积极开发和维护中，旨在完善 Mover 与 Mass 等系统的集成。作为 `IsBetaVersion=true` 的实验性插件，其 API 和功能在未来版本中可能会发生变化，建议仅在实验项目或特定集成需求中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MoverIntegrations)
- [官方文档]()(暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MoverIntegrations/Tests) *(如果存在)*