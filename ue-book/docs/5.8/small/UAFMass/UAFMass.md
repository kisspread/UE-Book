# UAF Mass

> Mass integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | 大规模动画框架集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMass` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2025-11-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMass) | |

## 用途

UAFMass 插件的核心功能是将 UAF (Unreal Animation Framework) 动画系统集成到 Unreal Engine 的 **Mass 实体框架 (Mass Entity Framework)** 中。它旨在解决大规模（成千上万）实体角色动画的性能与管理问题。

通过该插件，开发者可以将传统的、面向单个对象的 UAF 动画系统应用到 Mass 实体上，从而利用 Mass 框架的 ECS (实体-组件-系统) 架构和高度优化的批处理能力，高效地驱动大量 AI 角色或 NPC 的动画状态、运动轨迹和动画图（AnimGraph）。它提供了一套处理器 (Processor) 和特质 (Trait) 来桥接两个系统。

## 使用场景

- **大规模开放世界游戏**：需要驱动海量 NPC 的动画，如城市、战场场景。
- **需要精细动画控制的 AI 角色群体**：例如，一群角色需要基于复杂的行为树或状态机动画，且同时运行时数量巨大。
- **性能优化**：当传统的基于蓝图的动画蓝图在大量实例下出现性能瓶颈时，迁移到 Mass + UAFMass 架构。
- **角色运动轨迹模拟**：需要将角色的移动轨迹、转向等信息实时传递给动画系统，以实现根运动或程序化动画。

## 蓝图用法

UAFMass 主要通过 Mass 实体模板 (Mass Entity Template) 和特质 (Trait) 进行配置，在编辑器中使用。

### 核心配置

| 节点/配置项 | 说明 | 所在类 |
|---|---|---|
| `Mass UAF Trait` | 为 Mass 实体模板添加一个 UAF 动画系统。在 `AssetData` 中指定要运行的 UAF 动画资产。 | `UMassUAFTrait` |
| `Character Trajectory UAF Setup` | 为使用角色轨迹 (Character Trajectory) 的实体配置 UAF 数据映射，例如将轨迹、朝向变量名映射到 UAF 系统。 | `UCharacterTrajectoryUAFTrait` |
| `Mass Phase Processor` (依赖项) | 一个结构体，用于将 UAF 模块的执行（如动画评估）与 Mass 框架的某个处理阶段（如 `PrePhysics`）绑定。 | `FRigVMTrait_ModuleEventDependency_MassPhaseProcessor` |

### 使用示例（蓝图描述）

1.  **创建或编辑一个 Mass Entity Template 资产**。
2.  在该模板的 **Traits** 列表中，添加 `Mass UAF Trait`。
3.  在该 Trait 的详情面板中，通过 `AssetData` 属性选择你预先创建好的 UAF 动画系统资产。
4.  (可选) 如果你的实体需要基于移动轨迹驱动动画，再添加 `Character Trajectory UAF Setup` Trait，并根据需要调整变量名映射。
5.  将此 Mass Entity Template 应用于你的 Spawner（如 `MassSpawner`），运行时即可生成大量受 UAF 动画驱动的实体。

## C++ 用法

UAFMass 主要作为 Mass 处理器 (Processor) 和特质 (Trait) 的提供者。使用者更可能通过配置和继承，而非直接调用大量函数。

### 头文件引入

```cpp
#include "UAFMassModule.h"

// 引入 Mass 框架相关头文件（通常已在 MassGameplay 模块依赖中）
#include "MassEntityTypes.h"
#include "MassProcessor.h"
#include "MassObserverProcessor.h"
```

### 基本用法：理解现有处理器

查看插件提供的核心处理器逻辑，有助于理解集成方式。以下是一个简化后的执行逻辑描述（参考 `Private/Processors/MassUAFProcessor.h` 中的类定义）：

```cpp
// UMassUAFProcessor 是核心执行处理器
// 它配置一个查询，获取具有 FMassUAFFragment 的实体
// 在 Execute 中，它会遍历这些实体，驱动它们关联的 UAF 动画系统执行。
void UMassUAFProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 伪代码逻辑：
    // EntityQuery.ForEachEntityChunk(Context, [&](FMassExecutionContext& Context)
    // {
    //     TConstArrayView<FMassUAFFragment> UAFFragments = Context.GetFragmentView<FMassUAFFragment>();
    //     // 遍历 chunk 中的每个实体
    //     for (int32 i = 0; i < Context.GetNumEntities(); ++i)
    //     {
    //         UE::UAF::FSystemReference& SystemRef = UAFFragments[i].SystemReference;
    //         // ... 调用 UAF 系统接口进行动画更新、变量设置等 ...
    //     }
    // });
}
```

### 进阶用法：创建自定义 UAF 驱动的处理器

你可能会创建一个自定义的 Mass 处理器，用于在特定的游戏逻辑阶段（例如，行为决策后）设置 UAF 系统的输入变量。

```cpp
// 假设我们有一个自定义的片段，用于存储角色想要执行的动作
USTRUCT()
struct FCharacterActionFragment : public FMassFragment
{
    GENERATED_BODY()
    FName DesiredAction;
};

UCLASS()
class UMyUAFActionSetterProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyUAFActionSetterProcessor()
    {
        // 配置此处理器需要的数据
        ExecutionOrder.ExecuteInGroup = TEXT("PreAnimation"); // 在动画更新前执行
    }

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override
    {
        EntityQuery.AddRequirement<FMassUAFFragment>(EMassFragmentAccess::ReadWrite);
        EntityQuery.AddRequirement<FCharacterActionFragment>(EMassFragmentAccess::ReadOnly);
    }

    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override
    {
        // 逻辑：读取角色动作片段，然后设置到关联的 UAF 系统变量中
        EntityQuery.ForEachEntityChunk(Context, [this](FMassExecutionContext& Context)
        {
            TConstArrayView<FCharacterActionFragment> Actions = Context.GetFragmentView<FCharacterActionFragment>();
            TArrayView<FMassUAFFragment> UAFFragments = Context.GetMutableFragmentView<FMassUAFFragment>();

            for (int32 i = 0; i < Context.GetNumEntities(); ++i)
            {
                const FName& Action = Actions[i].DesiredAction;
                UE::UAF::FSystemReference& SystemRef = UAFFragments[i].SystemReference;
                if (SystemRef.IsValid())
                {
                    // 伪代码：通过 UAF 系统接口设置变量
                    SystemRef.SetVariable(TEXT("CurrentAction"), Action);
                }
            }
        });
    }

private:
    FMassEntityQuery EntityQuery;
};
```

## Demo 示例

一个最小的自定义 UAFMass 处理器示例，用于在 UAF 系统初始化后设置一个静态变量。

**MyUAFInitializerProcessor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MassProcessor.h"
#include "MassUAFFragment.h"
#include "MyUAFInitializerProcessor.generated.h"

UCLASS()
class UMyUAFInitializerProcessor : public UMassProcessor
{
	GENERATED_BODY()

public:
	UMyUAFInitializerProcessor();

protected:
	virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
	virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

	FMassEntityQuery EntityQuery;
};
```

**MyUAFInitializerProcessor.cpp**
```cpp
#include "MyUAFInitializerProcessor.h"
// 假设这是你的项目头文件路径
// #include "YourProjectModule.h"

UMyUAFInitializerProcessor::UMyUAFInitializerProcessor()
{
	// 设置执行顺序，确保在 UAF 系统创建后运行
	// ExecutionOrder.ExecuteInGroup = TEXT("PostUAFInit");
}

void UMyUAFInitializerProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
	// 只处理拥有 FMassUAFFragment 的实体
	EntityQuery.AddRequirement<FMassUAFFragment>(EMassFragmentAccess::ReadWrite);
}

void UMyUAFInitializerProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
	EntityQuery.ForEachEntityChunk(Context, [this](FMassExecutionContext& Context)
	{
		TArrayView<FMassUAFFragment> UAFFragments = Context.GetMutableFragmentView<FMassUAFFragment>();

		for (int32 i = 0; i < Context.GetNumEntities(); ++i)
		{
			UE::UAF::FSystemReference& SystemRef = UAFFragments[i].SystemReference;
			if (SystemRef.IsValid())
			{
				// 伪代码：初始化 UAF 系统变量
				SystemRef.SetVariable(TEXT("IsInitialized"), true);
				SystemRef.SetVariable(TEXT("MaxSpeed"), 600.0f);
			}
		}
	});
}
```

## 模块依赖

要使用 `UAFMass` 插件，你的项目模块需要依赖以下 UE 模块：

| 模块 | 用途 |
|---|---|
| `MassGameplay` | Mass 游戏框架的核心，提供实体、处理器、查询等基础。 |
| `MassEntity` | Mass 实体管理器的核心模块（通常作为 MassGameplay 的依赖）。 |
| `UAFCore` | UAF 动画框架的核心模块，提供 UAF 系统的创建和管理接口。 |
| `RigVM` | 可能用于执行 UAF 动画图中的逻辑（如变量设置）。 |
| `GameplayAbilities` (可选) | 如果你的 UAF 系统与 GAS 结合，可能需要此依赖。 |

*(注：根据插件名称和描述推断，实际 Build.cs 可能包含更多特定依赖。)*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `746b6abb` | Move UAF-Mass trajectory bridge into engine UAFMass plugin | 将 UAF 与 Mass 之间的轨迹桥接代码移入引擎插件目录，作为正式功能的一部分。 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | 重构 MassCore 模块头文件路径，使其更整洁，属于 Mass 框架的基础设施调整。 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 将 Mass 核心功能从 MassEntity 模块中提取出来，形成独立的 MassCore 模块。 |
| 2026-03-11 | `1d291fa1` | [Mass] Multi-fragment observer support in UMassObserverProcessor | 为 Mass 观察者处理器添加多片段支持，提升了初始化/销毁处理器的灵活性。 |
| 2026-02-17 | `baf983b4` | [SubmitTool - UAF] Add validators to build and run LowLevelTests for UAF plugins | 为 UAF 插件添加构建和测试验证器，确保代码质量和集成稳定性。 |

### 维护评价

- **实验性状态**：插件在 `.uplugin` 中明确标记为 `IsExperimentalVersion: true`，且默认未启用 (`EnabledByDefault: false`)。这表明它仍处于积极开发和验证阶段，API 和功能可能发生重大变更。
- **活跃开发**：最近 3 个月（截至 2026 年 4 月）有多次提交，内容涉及功能集成（轨迹桥接）、核心框架重构（MassCore 提取）以及测试基础设施完善。开发活动非常频繁。
- **集成度高**：插件不仅添加功能，还紧跟底层 Mass 框架的演进（如 MassCore 模块化），说明维护者致力于保持其与引擎核心的一致性。
- **推荐**：对于正在探索将大规模动画系统迁移到 Mass 架构的项目，该插件是官方提供的核心集成方案，**值得密切关注和在原型中试用**。但由于其**实验性状态和近期可能的 API 变动**，不建议直接用于已上线的、要求稳定性的生产项目。需做好应对 breaking changes 的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMass)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMass/Tests) (推测路径)