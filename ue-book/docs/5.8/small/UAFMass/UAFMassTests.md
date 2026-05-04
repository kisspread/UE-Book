# UAF Mass

> Mass integration for UAF.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMass` (Runtime), `UAFMassTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFMass) | |

## 用途

UAFMass 插件的核心目的是将 Unreal Animation Framework (UAF) 的动画能力集成到 Mass 框架中。它解决的是大规模实体（如人群、生物群、军队）的动画性能问题。通过 Mass 的实体组件系统 (ECS) 架构，该插件允许成千上万的实体共享动画状态、资源和计算逻辑，从而避免为每个实体单独实例化和驱动完整的动画蓝图，显著降低 CPU 开销，实现高效的大规模动画模拟。

## 使用场景

- 你需要在 RTS 或模拟游戏中同时渲染和动画化成百上千个单位。
- 你在开发一个开放世界游戏，需要为远处的大量 NPC 或生物提供轻量级动画。
- 你正在构建一个需要大规模人群模拟的体验（如体育场、城市街道），并希望保持流畅的帧率。
- 你希望利用 Mass 框架的高性能数据处理能力来管理动画状态和更新。

## 蓝图用法

该插件主要通过 Mass 的 Trait 和 Processor 系统工作，蓝图节点通常用于配置和触发。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Animation Trait` | 为 Mass 实体添加动画能力，使其能够参与 UAF 动画系统。 | `UMassAnimationTrait` |
| `Set Animation State` | 设置或更改实体的动画状态（例如，从“行走”切换到“攻击”）。 | `UMassAnimationProcessor` |
| `Update Animation` | 在 Mass 处理器中驱动动画更新，通常由系统自动调用。 | `UMassAnimationProcessor` |

### 使用示例（蓝图描述）

1.  **为实体添加动画能力**：在创建 Mass 实体的蓝图中，使用 `Add Animation Trait` 节点。你需要提供一个 `UAnimationAsset` 或动画状态机作为输入。
2.  **控制动画状态**：在游戏逻辑中，当需要改变实体行为时（例如，玩家下达攻击命令），获取目标实体的 `MassEntityHandle`，然后调用 `Set Animation State` 节点，传入新的状态标识符。
3.  **系统自动更新**：`UMassAnimationProcessor` 会作为 Mass 系统的一部分，在每帧自动处理所有带有动画 Trait 的实体，根据其当前状态和游戏时间更新动画。

## C++ 用法

### 头文件引入

```cpp
#include "MassAnimationTrait.h"
#include "MassAnimationProcessor.h"
```

### 基本用法

以下示例展示了如何在 C++ 中为 Mass 实体配置动画能力。

```cpp
// 假设你已经有一个 FMassEntityHandle EntityHandle
// 和一个 UAnimationAsset* MyAnimationAsset

// 1. 获取实体的 Fragment 视图
FMassEntityView EntityView(EntitySubsystem, EntityHandle);

// 2. 添加或获取动画 Fragment
FAnimationFragment& AnimFragment = EntityView.AddFragment_GetRef<FAnimationFragment>();

// 3. 配置动画数据
AnimFragment.AnimationAsset = MyAnimationAsset;
AnimFragment.PlayRate = 1.0f;
AnimFragment.bLooping = true;
```

### 进阶用法

结合 Mass 的命令模式来批量更改动画状态。

```cpp
// 创建一个命令来设置多个实体的动画状态
FMassCommandBuffer CommandBuffer;

for (const FMassEntityHandle& Handle : EntitiesToChange)
{
    CommandBuffer.PushCommand<FMassAnimationSetStateCommand>(Handle, NewAnimationStateID);
}

// 将命令提交给 Mass 系统执行
EntitySubsystem.DeferPushCommand(MoveTemp(CommandBuffer));
```

## Demo 示例

一个最小示例，展示如何创建一个带有动画能力的 Mass 实体。

**MyMassAnimationEntity.h**
```cpp
#pragma once
#include "MassEntityTypes.h"
#include "MassAnimationTrait.h"

UCLASS()
class UMyMassAnimationEntity : public UMassEntityConfigBase
{
    GENERATED_BODY()
public:
    UMyMassAnimationEntity();
};
```

**MyMassAnimationEntity.cpp**
```cpp
#include "MyMassAnimationEntity.h"
#include "MassEntityTemplateRegistry.h"

UMyMassAnimationEntity::UMyMassAnimationEntity()
{
    // 添加动画 Trait，使其成为实体模板的一部分
    AddTrait<UMassAnimationTrait>();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MassGameplay` | Mass 框架的核心游戏逻辑模块，提供实体、处理器和命令系统。 |
| `UAF` | Unreal Animation Framework 核心模块，提供动画资产、状态机和评估器。 |

## 维护状态

### 近期更新

- 2026-04-23 `746b6abb` Move UAF-Mass trajectory bridge into engine UAFMass plugin
- 2026-04-01 `58888966` [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames
- 2026-03-30 `161605b0` [Mass] Extract MassCore module from MassEntity
- 2026-03-11 `1d291fa1` [Mass] Multi-fragment observer support in UMassObserverProcessor
- 2026-02-17 `baf983b4` [SubmitTool - UAF] Add validators to build and run LowLevelTests for UAF plugins

### 维护评价

- **创建时间**：2026-02-17（此日期为未来时间，可能为文档占位符或测试数据，实际创建时间应更早）。
- **维护状态**：**实验性**。该插件位于 `Experimental` 目录下，且 `IsExperimentalVersion=true`，`EnabledByDefault=false`。这表明它仍处于早期开发或验证阶段，API 和功能可能不稳定，不建议在生产环境中直接使用。
- **推荐使用**：仅推荐用于技术预研、原型开发或学习 Mass 框架与动画系统集成的原理。在正式项目中使用前，需评估其稳定性和长期维护风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFMass)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFMass/Tests)