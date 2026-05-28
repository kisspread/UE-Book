# UAF Warping

> Framework for animation and pose warping for UAF.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | UAF扭曲 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFWarping` (Runtime), `UAFWarpingTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFWarping) | |

## 用途

UAFWarping 是 UAF (Unified Animation Framework) 动画框架的扭曲（Warping）扩展。它提供了一个运行时框架和具体的动画节点，用于在动画蓝图（AnimGraph）中实现姿态扭曲和动画扭曲操作，主要解决角色动画与运动轨迹、目标位置或速度的对齐问题。例如，让角色在快速转向时，其动画（如脚的着地位置）能平滑地过渡到匹配新的运动方向。

## 使用场景

- **目标追踪动画**：当角色需要快速转向并移动至某个目标点时，确保角色的动画（如迈步）能自然对齐目标方向。
- **速度匹配扭曲**：根据角色的实际移动速度，动态调整动画播放速率或姿态，使动画表现更符合物理运动。
- **动画/姿态混合修正**：在动画图中，对特定姿态或动画序列进行基于逻辑（如朝向、位移）的扭曲和修正。

## 蓝图用法

核心的扭曲逻辑主要通过 AnimGraph 中的自定义动画节点（AnimNode）实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `WarpToTarget` | 根据输入的目标位置和速度信息，扭曲当前的动画姿态，使其朝向和位移匹配目标。 | `UAnimNode_WarpToTargetNode` |

### 使用示例（蓝图描述）

1.  在您的动画蓝图（AnimGraph）中，找到 `UAF Warping` 分类。
2.  添加 `Warp To Target` 节点。
3.  将您的基础运动动画输出（如 State Machine 的输出）连接到该节点的输入姿态。
4.  通过蓝图逻辑或事件，持续向该节点提供最新的 `TargetLocation`（目标位置）和 `Velocity`（速度）信息。这些信息可以来自 AI 控制器、角色移动组件或玩家输入计算。
5.  将扭曲后的姿态连接到最终的动画输出（Output Pose）。

## C++ 用法

此插件的核心功能通过 AnimGraph 节点提供，C++ 中通常用于自定义或扩展这些节点的行为，或直接实例化它们。

### 头文件引入

```cpp
#include "AnimNodes/AnimNode_WarpToTargetNode.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建并配置一个 `UAnimNode_WarpToTargetNode` 实例（通常用于自定义 AnimNode 子类或测试中）。
*来源文件：* `Engine/Plugins/Experimental/UAF/UAFWarping/Tests/Private/AnimGraph/AnimGraphNodes/WarpToTargetNodeTest.cpp`

```cpp
// 在自定义 AnimNode 或测试环境中
UAnimNode_WarpToTargetNode* WarpNode = NewObject<UAnimNode_WarpToTargetNode>();

// 设置基本属性（属性名和类型需参考头文件定义）
WarpNode->TargetLocation = FVector(500.f, 0.f, 0.f);
WarpNode->Velocity = FVector(100.f, 0.f, 0.f);
WarpNode->WarpingStrength = 1.0f;

// 评估节点前需要先初始化
WarpNode->Initialize_AnyThread(FAnimationInitializeContext(/* ... */));
// 然后在动画更新流程中进行评估
WarpNode->Evaluate_AnyThread(FPoseContext(/* ... */));
```

### 进阶用法

可以结合测试用例了解更复杂的参数配置和行为验证。测试用例通常以 BDD (行为驱动开发) 风格编写，清晰展示了不同输入（目标位置、速度、强度）下节点的预期输出和行为。

## Demo 示例

一个最小的、展示 `WarpToTargetNode` 基本创建和使用的 C++ 示例。
*注意：此示例为概念演示，实际应用需集成到 AnimGraph 评估流程中。*

### WarpDemoActor.h
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AnimNodes/AnimNode_WarpToTargetNode.h"
#include "WarpDemoActor.generated.h"

UCLASS()
class AWarpDemoActor : public AActor
{
	GENERATED_BODY()

public:
	AWarpDemoActor();

protected:
	virtual void BeginPlay() override;

private:
	UPROPERTY()
	TObjectPtr<UAnimNode_WarpToTargetNode> WarpNode;
};
```

### WarpDemoActor.cpp
```cpp
#include "WarpDemoActor.h"

AWarpDemoActor::AWarpDemoActor()
{
	PrimaryActorTick.bCanEverTick = true;
}

void AWarpDemoActor::BeginPlay()
{
	Super::BeginPlay();

	// 创建扭曲节点实例
	WarpNode = NewObject<UAnimNode_WarpToTargetNode>();
	if (WarpNode)
	{
		// 配置目标参数
		WarpNode->TargetLocation = GetActorLocation() + FVector(1000.f, 0.f, 0.f);
		WarpNode->Velocity = GetActorForwardVector() * 200.f;
		WarpNode->WarpingStrength = 0.8f;

		// 注意：在实际项目中，需要将此节点正确地集成到动画蓝图的图中。
		// 此处仅为演示对象的创建和配置。
		UE_LOG(LogTemp, Log, TEXT("UAF Warping Node Created and Configured."));
	}
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UAFAnimNode` | 提供基础的 UAF 动画节点支持。 |
| `AnimGraphRuntime` | 动画图运行时核心模块，用于 AnimNode 的评估。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `b604d5ca` | Handle empty value bundle in modifier AnimOps | 处理动画操作中值为空的情况，增强鲁棒性。 |
| 2026-04-14 | `7b3fe3c2` | Use FPoseValueBundle in AnimOp value bundle evaluator | 在动画操作值评估器中使用新的 FPoseValueBundle 结构。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-04-09 | `153328f9` | UAFWarping - WarpToTargetNode | 新增了 WarpToTargetNode 核心扭曲动画节点。 |
| 2026-04-06 | `0b5bc2d3` | UAFWarping - small code cleanup | 小型代码清理和优化。 |

### 维护评价

UAFWarping 是一个非常新的插件（创建于 2025 年 6 月），目前处于 **活跃的实验性开发阶段**。
- **优点**：近期有密集的功能性提交（如新增核心 `WarpToTargetNode` 节点），表明 Epic 正在积极开发和完善它。
- **注意事项**：作为实验性插件 (`IsExperimentalVersion=true`)，其 API 和功能可能不稳定，不建议在关键项目中直接依赖。它依赖于同样可能处于实验状态的 UAF 插件套件。
- **推荐**：适合用于学习 UAF 框架、原型开发或参与 UE5 动画系统前沿技术的调研。密切关注其更新，因为 API 可能发生 Breaking Changes。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFWarping)
- [官方文档]()(无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/UAF/UAFWarping/Tests)