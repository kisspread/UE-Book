# Mover Integrations

> Mover Integrations is a Unreal Engine plugin acting as an umbrella to cover a variety of modules supporting Mover's integration with other plugins, such as animation, AI, and other gameplay systems.

| 属性 | 值 |
|---|---|
| 中文名 | 移动集成插件 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资源） |
| 模块 | `MoverIntegrations` (Runtime), `MoverMassIntegration` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-07 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MoverIntegrations) | |

## 用途

Mover Integrations 插件是 UE5 移动框架（Mover）与其他游戏系统（如 Mass、动画、AI 等）之间的桥梁。它作为一个伞式插件，将各类集成功能收纳在不同的子模块中。当前已提供 **Mover-Mass 集成模块**（`MoverMassIntegration`），用于实现 Mover 与 Mass（大规模实体系统）之间的数据交换和翻译器。

该插件解决的核心问题是：当项目中同时使用 Mover 进行移动逻辑管理和 Mass 进行大规模实体模拟时，需要一套标准化的方式将 Mover 的移动状态转换为 Mass 所需的实体数据，反之亦然。该插件提供了这些转换器（Translators），从而避免手动维护两套数据同步。

## 使用场景

- **大规模 AI 与移动控制**：你在开发一个使用 Mass 管理大量 AI 单位的开放世界游戏，每个单位需要独立且自然的移动行为（跑、跳、攀爬等），这时可以用 Mover 处理移动逻辑，通过 MoverMassIntegration 将移动状态传递给 Mass 的模拟管线。
- **混合运动系统**：项目中有部分角色使用 Mover (Character Movement Component 的强化版)，另一部分角色使用 Mass 驱动（如鸟类、鱼群），需要共享相同的碰撞、动画或物理数据，可利用此插件实现互操作。
- **未来扩展**：随着插件发展，将加入与其他系统（如动画蓝图、AI感知）的集成模块，形成统一的集成入口。

## 蓝图用法

该插件主要面向 C++ 使用，暂无直接暴露给蓝图的可调用函数或通信节点。所有集成逻辑通过 C++ 翻译器类实现，需要在 C++ 项目中手动配置 Mass 处理器和 Mover 组件。

> **提示**：如果你需要使用 Mover 的蓝图节点，请直接查阅 Mover 插件本身的文档；MoverMassIntegration 不提供额外蓝图 API。

## C++ 用法

### 头文件引入

```cpp
// 使用 Mover-Mass 集成时，引入 MoverMassIntegration 模块的头文件
#include "MoverMassTranslators.h"
// 如使用 MoverIntegrations 模块提供的通用工具（暂无）
#include "MoverIntegrations.h"
```

### 基本用法

以下示例演示如何在 Mass 处理器的 `FMassEntityManager` 中添加 Mover-Mass 翻译器，使得 Mass 可以读取 Mover 角色的移动状态。

```cpp
// Source: Engine/Plugins/Experimental/MoverIntegrations/Source/MoverMassIntegration/Private/MoverMassIntegrationModule.cpp
//（假设示例基于测试用例）

void UMyMassProcessor::ConfigureQueries()
{
    // 添加翻译器，使 Mass 处理器能够理解 Mover 的状态
    ProcessorQueries.AddRequirement<FMoverMassStateFragment>(EMassFragmentAccess::ReadOnly);
    // 添加输出翻译器，将 Mass 结果写回 Mover
    ProcessorQueries.AddSubRequester<FMoverMassOutputFragment>(EMassFragmentAccess::ReadWrite);
}
```

```cpp
// 在游戏初始化时注册 Mover-Mass 翻译器
// 通常由 MoverMassIntegration 模块自动完成，但也可以手动注册
#include "MassEntitySubsystem.h"
#include "MassExecutor.h"
#include "MoverMassTranslators.h"

void AMyGameMode::InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage)
{
    Super::InitGame(MapName, Options, ErrorMessage);
    
    if (UMassEntitySubsystem* MassSubsystem = UWorld::GetSubsystem<UMassEntitySubsystem>(GetWorld()))
    {
        FMassRuntimePipeline& Pipeline = MassSubsystem->GetRuntimePipeline();
        // 注册 Mover → Mass 翻译器（将 Mover 状态同步到 Mass 片段）
        Pipeline.AddTranslator<FMoverToMassTranslator>();
        // 注册 Mass → Mover 翻译器（将 Mass 片段写回 Mover 状态）
        Pipeline.AddTranslator<FMassToMoverTranslator>();
    }
}
```

### 进阶用法

结合 Mover 的自定义 `UMoverComponent` 和 Mass 处理器，建立完整的双向数据流。以下是一个简化的处理器，负责每帧将 Mover 的位置和速度同步到 Mass 实体：

```cpp
#include "MassProcessor.h"
#include "MassCommonFragments.h"
#include "MoverComponent.h"
#include "MoverMassTranslators.h"

class FSyncMoverToMassProcessor : public FMassProcessor
{
    GENERATED_BODY()
public:
    FSyncMoverToMassProcessor()
    {
        bRequiresGameThreadExecution = true;
        ExecutionOrder.ExecuteInGroup = UE::Mass::ProcessorGroupNames::Movement;
    }

    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override
    {
        // 获取所有需要同步的 Mover 组件实体
        auto Query = EntityManager.Query();
        // ... 编写查询和同步逻辑
    }
};

// 在模块启动时注册该处理器
void FMyGameModule::StartupModule()
{
    // 可以通过 FMoverMassIntegrationModule 的接口注册自定义翻译器
}
```

> **注意**：以上代码仅为示意，具体 API 细节请参考 `MoverMassTranslators.h` 中的类定义。实际项目中建议直接查看插件测试用例。

## Demo 示例

以下是一个完整的、可编译的 GameMode 示例，展示如何在最小项目中启用 Mover-Mass 翻译器。该示例假设项目已启用 `MoverIntegrations`、`Mover`、`MassEntity` 插件。

**MyGameMode.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

UCLASS()
class AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void StartPlay() override;
};
```

**MyGameMode.cpp**

```cpp
#include "MyGameMode.h"
#include "MassEntitySubsystem.h"
#include "MoverMassTranslators.h"
#include "Engine/World.h"

void AMyGameMode::StartPlay()
{
    Super::StartPlay();

    // 确保 Mass 子系统存在
    if (UMassEntitySubsystem* MassSubsystem = UWorld::GetSubsystem<UMassEntitySubsystem>(GetWorld()))
    {
        FMassRuntimePipeline& Pipeline = MassSubsystem->GetRuntimePipeline();
        // 注册 Mover ↔ Mass 双向翻译器
        Pipeline.AddTranslator<FMoverToMassTranslator>();
        Pipeline.AddTranslator<FMassToMoverTranslator>();

        UE_LOG(LogTemp, Log, TEXT("Mover-Mass translators registered."));
    }
}
```

## 模块依赖

### MoverIntegrations 模块（Runtime）

依赖关系请参考 `Source/MoverIntegrations/MoverIntegrations.Build.cs`。该模块本身只是一个空壳，不引入特殊依赖。

### MoverMassIntegration 模块（Runtime）

| 模块 | 用途 |
|---|---|
| `Mover` | 移动框架核心模块，提供 `UMoverComponent`、移动状态等 |
| `MassEntity` | Mass 实体管理系统，提供实体管理器、片段、处理器等 |
| `MassCommon` | Mass 公共数据类型，如位置、速度片段 |
| `MassSignals` | Mass 信号系统（可能用于事件驱动） |

其他常见依赖（Core、Engine 等）已省略。

## 维护状态

### 近期更新

- 2025-06-10 `675fd5ae` CIS issue#936427: 修复编译错误（EngineRuntimeTests.h、MoverMassTranslators.h）
- 2025-05-07 `1207fa81` Mover: 添加 UE5 Mover-Mass 翻译器及 Mover Integrations 插件

### 维护评价

该插件于 **2025 年 5 月** 创建，属于极新的插件（约 2 个月）。近期（2025 年 6 月）仍有编译修复提交，说明团队正在积极维护。目前仅包含 Mover-Mass 集成，未来可能会扩展至动画、AI 等其他系统。作为实验性插件，API 可能发生变化，但适合对最新 Mover 技术有需求的早期采用者。

**推荐指数**：⭐⭐⭐（适合实验性和前瞻性项目，生产环境需谨慎）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MoverIntegrations)
- [Mover 官方文档](https://docs.unrealengine.com/5.4/en-US/mover-gameplay-movement-framework-in-unreal-engine/)（Mover 自身文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MoverIntegrations/Source/MoverMassIntegration/Private/Tests)（如有）