# UAF Mass

> Mass integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | 大规模动画集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMass` (Runtime), `UAFMassTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-11-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMass) | |

## 用途

UAFMass 插件解决了 **UAF 动画系统**与 **Mass 实体框架**之间的集成问题。它允许在基于 Mass 框架构建的系统中高效地驱动和管理大量实体的动画。核心功能是为 UAF 引入 Mass 处理阶段事件依赖性，使得动画更新可以作为 Mass 处理流水线的一部分，从而实现高性能的大规模实体动画计算。

## 使用场景

- 你正在构建一个需要成千上万 NPC（如 RTS 游戏单位、人群模拟）的项目，并且使用了 Mass 框架进行实体管理。为了让这些实体拥有符合逻辑的动画表现，你需要将 UAF 动画系统与 Mass 的更新循环同步。
- 你希望动画决策（如状态机更新、动画蒙太奇触发）能够响应 Mass 处理阶段（如 `PrePhysics`、`PostPhysics`），以确保动画与移动、伤害等系统精确同步。

## 蓝图用法

**注意**：由于未提供具体头文件内容，以下节点为基于模块 `UAFMass` 和 `UAFMassTests` 命名的**推测性示例**，旨在展示可能的集成方式。实际 API 请参考最新引擎源码。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Mass Entity Animation` | 为指定的 Mass 实体设置初始动画状态或参数。 | `UAFMassAnimComponent` (推测) |
| `Query Mass Animation State` | 查询当前 Mass 实体的动画状态信息。 | `UAFMassAnimSubsystem` (推测) |
| `Register Mass Animation Processor` | 向 Mass 框架注册一个自定义的、基于 UAF 的动画处理器。 | `UAFMassAnimModule` (推测) |

### 使用示例（蓝图描述）

1.  **初始化**：在你的 Mass `EntityConfig` 资产中，添加一个自定义的 Fragment（例如 `FAFAnimFragment`），用于存储动画相关的数据。
2.  **设置动画**：在实体生成后，通过类似 `Set Mass Entity Animation` 的节点，根据实体类型为其设置合适的动画资产或状态机参数。
3.  **处理更新**：动画处理器（Processor）会在 Mass 指定的处理阶段被调用，它读取实体的动画片段，并驱动底层的动画实例更新。

## C++ 用法

### 头文件引入

```cpp
#include “UAFMass.h”
// 可能需要引入具体的类头文件，例如：
#include “UAFMassAnimProcessor.h”
```

### 基本用法

基于模块类型和测试模块的存在，典型的用法可能涉及创建与 Mass 处理阶段绑定的动画处理器。

```cpp
// 示例：一个自定义的动画处理器（概念代码，非实际编译通过的代码）
// 来源：基于 UAFMass (Runtime) 模块功能推测

#include “MassProcessor.h”
#include “UAFMassAnimProcessor.h” // 假设存在此头文件

class FMyCustomAnimProcessor : public FMassProcessor
{
public:
    FMyCustomAnimProcessor()
    {
        // 声明此处理器需要查询的 Fragment
        ExecutionFlags = (int32)EProcessorExecutionFlags::All;
        // 设置处理阶段，例如 PostPhysics
        ProcessingPhase = EMassProcessingPhase::PostPhysics;
    }

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override
    {
        // 配置查询，指定需要哪些 Fragment
        EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
        EntityQuery.AddRequirement<FAFAnimFragment>(EMassFragmentAccess::ReadWrite); // 自定义的动画 Fragment
    }

    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override
    {
        // 执行动画更新逻辑
        EntityQuery.ForEachEntityChunk(EntityManager, Context, [](FMassExecutionContext& Context)
        {
            // 获取动画片段并进行更新
            // ...
        });
    }
};
```

### 进阶用法

结合 UAF 的特性（如动画状态机、蒙太奇），可能需要自定义 Mass Fragment 来保存更复杂的动画状态，并在处理器中调用 UAF 的内部 API 进行驱动。这通常需要在 UAFMass 模块提供的基础上进行扩展。

## Demo 示例

以下是一个假设的、用于演示集成概念的最小代码示例。

**`MyMassAnimEntity.h`**
```cpp
#pragma once

#include “MassEntityTypes.h”
// 包含 UAFMass 提供的基础动画 Fragment 头文件
#include “UAFMassAnimFragment.h”

// 自定义的、包含 UAF 动画引用的 Fragment
USTRUCT()
struct FMyAnimFragment : public FMassFragment
{
    GENERATED_BODY()

    // 持有对动画资产的引用
    UPROPERTY(EditAnywhere, Category = “Animation”)
    TObjectPtr<UAnimSequence> AnimAsset;

    // 持有动画时间或其他状态
    float AnimTime = 0.0f;
};
```

**`MyMassAnimProcessor.cpp`**
```cpp
#include “MyMassAnimEntity.h”
#include “MassExecutionContext.h”
#include “UAFMass.h” // 引入 UAFMass 模块接口

class FMyAnimProcessor : public FMassProcessor
{
public:
    FMyAnimProcessor()
    {
        ProcessingPhase = EMassProcessingPhase::PostPhysics;
        bAutoRegisterWithProcessingPhases = true; // 自动注册到处理阶段
    }

    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override
    {
        EntityQuery.AddRequirement<FMyAnimFragment>(EMassFragmentAccess::ReadWrite);
        EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
    }

    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override
    {
        EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
        {
            const int32 NumEntities = Context.GetNumEntities();
            auto AnimFragmentView = Context.GetMutableFragmentView<FMyAnimFragment>();
            const auto TransformView = Context.GetFragmentView<FTransformFragment>();

            for (int32 i = 0; i < NumEntities; ++i)
            {
                FMyAnimFragment& AnimFragment = AnimFragmentView[i];
                // 更新动画时间
                AnimFragment.AnimTime += Context.GetDeltaTimeSeconds();
                // 这里可以调用 UAFMass 提供的工具函数，基于 AnimAsset 和 AnimTime
                // 来驱动实体的视觉表现（例如更新骨骼网格体组件）。
                // 调用示意: UAFMassAnimUtils::UpdateEntityAnimation(Context.GetEntity(i), AnimFragment);
            }
        });
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MassGameplay` | Mass 实体框架核心游戏功能，是 UAFMass 存在的基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `746b6abb` | Move UAF-Mass trajectory bridge into engine UAFMass plugin | 将 UAF-Mass 的移动轨迹桥接功能移入此引擎插件。 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | 适配 MassCore 模块头文件目录结构变更。 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 适配 Mass 框架从 MassEntity 中提取 MassCore 模块的重构。 |
| 2026-03-11 | `1d291fa1` | [Mass] Multi-fragment observer support in UMassObserverProcessor | 适配 Mass 框架的更新，支持多 Fragment 观察者。 |
| 2026-02-17 | `baf983b4` | [SubmitTool - UAF] Add validators to build and run LowLevelTests for UAF plugins | 为 UAF 相关插件（包括此插件）添加构建和测试验证器。 |

### 维护评价

- **创建时间**：非常新，创建于 2025 年 11 月。
- **近期更新频率**：自 2026 年 2 月起有持续更新，但多为**架构适配和重构**（如跟随 MassCore 目录结构、Mass 框架重构），而非密集的功能新增。
- **维护状态**：处于**早期实验性开发**阶段。功能通过随 Mass 框架和 UAF 系统的迭代而演进。
- **已知问题/限制**：作为实验性插件，其 API 和架构可能随引擎版本大幅变动。默认未启用。
- **推荐使用**：适用于需要前沿技术集成、愿意承担 API 变动风险的项目。**生产环境使用需谨慎**，建议密切关注官方更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMass)
- [官方文档]() （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMass/Tests)