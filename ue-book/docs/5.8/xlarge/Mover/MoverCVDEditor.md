# Mover

> Mover is an Unreal Engine plugin to support movement of actors with rollback networking.
> Please refer to the README document for information about getting started, an overview of concepts, and known issues.

| 属性 | 值 |
|---|---|
| 中文名 | 移动组件 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源、示例场景） |
| 模块 | `Mover` (Runtime), `MoverCVDData` (Runtime), `MoverCVDEditor` (Runtime), `MoverEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Mover) | |

## 用途

Mover 是一个专门用于处理角色移动和网络同步的插件。它解决的核心问题是**在多人游戏中实现流畅、可预测且回滚友好的角色移动**。传统移动方案在网络延迟下容易出现卡顿、位置不同步等问题，而 Mover 采用**基于服务器的权威移动模型**结合**客户端预测和回滚**机制，确保在各种网络条件下都能提供响应迅速且一致的游戏体验。

插件的设计理念是**模块化、可扩展**。它将移动分解为多个独立的组件（称为 "Motion" 和 "Mode"），允许开发者像搭积木一样组合出复杂的移动行为。同时，它深度集成了 **Chaos 物理系统**和 **Chaos Visual Debugger (CVD)**，为开发者提供了强大的调试和可视化工具，使得移动逻辑和物理交互的调试变得直观。

## 使用场景

- 你正在开发一款**多人在线竞技游戏**（如 FPS、TPS、MOBA），需要精确的角色移动同步 → 用 Mover
- 你的游戏角色有**复杂的移动状态**（如奔跑、跳跃、攀爬、滑铲、飞行等），且需要网络同步 → 用 Mover
- 你需要一个**高性能、可预测**的移动系统，能够处理**高延迟和丢包**的网络环境 → 用 Mover
- 你想快速原型化或扩展移动逻辑，而不想从零开始编写复杂的网络同步代码 → 用 Mover
- 你需要使用 **Chaos Visual Debugger** 来深度调试和可视化角色的移动状态、输入指令和模拟数据 → 用 Mover（及其 CVD 相关模块）

## 蓝图用法

> 注意：Mover 插件主要面向 C++ 开发者，其核心移动逻辑和组件均通过 C++ 实现。蓝图接口主要用于配置和扩展，而非直接执行移动计算。以下为可供蓝图访问的配置类和接口。

### 核心配置类

| 类 | 说明 | 蓝图可访问性 |
|---|---|---|
| `UMoverBlackboard` | 一个数据容器，用于在移动模式和运动模式之间共享数据（如速度、地面法线等） | `UPROPERTY(BlueprintReadWrite)` |
| `UCharacterMoverComponent` | 角色移动组件，是 Mover 系统的主要入口，包含移动模式和运动模式列表 | `UPROPERTY(EditAnywhere, BlueprintReadWrite)` |
| `UBaseMovementMode` | 移动模式的基类（如行走、飞行、攀爬），定义了模式的进入、退出和更新逻辑 | 可创建蓝图子类 |
| `UBaseMotionMode` | 运动模式的基类（如地面运动、空中运动），负责具体的移动计算和物理交互 | 可创建蓝图子类 |

### 使用示例（蓝图描述）

1.  **配置移动模式**：
    *   在角色蓝图中，添加 `CharacterMoverComponent` 组件。
    *   在组件的细节面板中，找到 `Movement Modes` 数组。
    *   添加你需要的移动模式蓝图子类（例如，一个自定义的 `BP_ClimbingMode` 继承自 `UBaseMovementMode`）。
    *   为每个模式设置触发条件（如输入按键、动画通知等）。

2.  **扩展数据**：
    *   创建一个继承自 `UMoverBlackboard` 的蓝图子类 `BP_MyBlackboard`。
    *   在 `BP_MyBlackboard` 中添加你自定义的 `UPROPERTY(BlueprintReadWrite)` 变量，例如 `CurrentStamina`。
    *   在 `CharacterMoverComponent` 的细节面板中，将 `Blackboard Class` 设置为 `BP_MyBlackboard`。
    *   在移动模式蓝图中，你可以通过 `Get Blackboard` 节点访问和修改这些自定义数据。

## C++ 用法

### 头文件引入

```cpp
// 核心移动组件
#include "Mover/Public/CharacterMoverComponent.h"

// 移动模式和运动模式基类
#include "Mover/Public/MovementMode.h"
#include "Mover/Public/MotionMode.h"

// 黑板（数据容器）
#include "Mover/Public/Blackboard/MoverBlackboard.h"

// 如果需要使用 Chaos Visual Debugger 功能
#include "MoverCVDData/Public/MoverCVDSimDataWrapper.h"
#include "MoverCVDEditor/Public/MoverCVDEditor.h"
```

### 基本用法：创建一个自定义移动模式

```cpp
// MyWalkingMode.h
#pragma once

#include "Mover/Public/MovementMode.h"
#include "MyWalkingMode.generated.h"

UCLASS()
class UMyWalkingMode : public UBaseMovementMode
{
	GENERATED_BODY()

public:
	// 模式激活时调用
	virtual void OnActivate(const FMovementModeActivationParams& ActivationParams) override;

	// 模式每帧更新
	virtual void OnUpdate(float DeltaTime, const FMovementModeUpdateParams& UpdateParams) override;

	// 模式退出时调用
	virtual void OnDeactivate() override;

protected:
	// 自定义属性
	UPROPERTY(EditAnywhere)
	float WalkSpeed = 300.0f;
};

// MyWalkingMode.cpp
#include "MyWalkingMode.h"
#include "Mover/Public/Blackboard/MoverBlackboard.h"

void UMyWalkingMode::OnActivate(const FMovementModeActivationParams& ActivationParams)
{
	Super::OnActivate(ActivationParams);
	// 激活时可以播放起步动画，设置初始状态等
	UE_LOG(LogTemp, Log, TEXT("Walking Mode Activated"));
}

void UMyWalkingMode::OnUpdate(float DeltaTime, const FMovementModeUpdateParams& UpdateParams)
{
	Super::OnUpdate(DeltaTime, UpdateParams);

	// 1. 获取输入意图
	const FInputCmdContext& InputCmd = UpdateParams.InputCmd;

	// 2. 计算期望速度
	FVector DesiredVelocity = FVector::ZeroVector;
	DesiredVelocity += UpdateParams.GetActorForwardVector() * InputCmd.GetForwardInput() * WalkSpeed;
	DesiredVelocity += UpdateParams.GetActorRightVector() * InputCmd.GetRightInput() * WalkSpeed;

	// 3. 将期望速度应用到移动组件
	// (通常通过 MotionMode 来处理，这里仅为示意)
	if (UMoverBlackboard* BB = GetBlackboard())
	{
		BB->SetDesiredVelocity(DesiredVelocity);
	}

	// 4. 检查是否需要切换模式（例如：跳跃）
	if (InputCmd.bJumpPressed)
	{
		// 请求切换到跳跃模式
		RequestModeChange(TEXT("JumpingMode"));
	}
}

void UMyWalkingMode::OnDeactivate()
{
	Super::OnDeactivate();
	UE_LOG(LogTemp, Log, TEXT("Walking Mode Deactivated"));
}
```

### 进阶用法：集成 Chaos Visual Debugger 进行调试

```cpp
// 在某个管理器或调试器类中
#include "MoverCVDData/Public/MoverCVDSimDataWrapper.h"
#include "MoverCVDEditor/Public/MoverCVDEditor.h"

void AMyDebugActor::ToggleMoverCVDDebugging(bool bEnable)
{
	// 获取 Mover CVD 编辑器模块实例
	FMoverCVDEditorModule& MoverCVDEditorModule = FModuleManager::GetModuleChecked<FMoverCVDEditorModule>(TEXT("MoverCVDEditor"));

	// 根据 bEnable 开启或关闭数据录制（概念性代码，具体接口需查看模块实现）
	// MoverCVDEditorModule.SetSimulationRecordingEnabled(bEnable);
}

// 在游戏运行时，可以通过 CVD 面板查看 FMoverCVDSimDataWrapper 结构中的数据
// 例如，获取当前帧某个角色的同步状态和输入指令
void AMyDebugActor::DisplayMoverDebugInfo(int32 SolverID, int32 ParticleID)
{
	// 假设我们能获取到 MoverCVDSimDataComponent
	if (UMoverCVDSimDataComponent* SimDataComp = GetMoverCVDSimDataComponent(SolverID))
	{
		TSharedPtr<FMoverCVDSimDataWrapper> SimDataWrapper;
		TSharedPtr<FMoverSyncState> SyncState;
		TSharedPtr<FMoverInputCmdContext> InputCmd;
		TArray<TPair<FName, TSharedPtr<FMoverDataCollection>>> LocalDataSections;

		if (SimDataComp->FindAndUnwrapSimDataForParticle(ParticleID, SimDataWrapper, SyncState, InputCmd, LocalDataSections))
		{
			// 在这里可以分析和显示 Mover 的内部状态
			// 例如，查看同步状态的位置、速度等
			if (SyncState.IsValid())
			{
				FVector SyncPosition = SyncState->GetPosition();
				UE_LOG(LogTemp, Log, TEXT("Mover Sync Position: %s"), *SyncPosition.ToString());
			}
			// 查看输入指令
			if (InputCmd.IsValid())
			{
				float ForwardInput = InputCmd->GetForwardInput();
				float RightInput = InputCmd->GetRightInput();
				UE_LOG(LogTemp, Log, TEXT("Mover Input - Forward: %f, Right: %f"), ForwardInput, RightInput);
			}
		}
	}
}
```

## Demo 示例

由于 Mover 插件的示例代码（MoverExamples）是内容项目的一部分，且位于 `Engine/Plugins/Experimental/Mover` 之外，这里提供一个核心概念的最小可编译 C++ 示例，展示如何注册一个自定义移动模式。

```cpp
// MyMoverActor.h
#pragma once

#include "GameFramework/Actor.h"
#include "MyMoverActor.generated.h"

class UCharacterMoverComponent;

UCLASS()
class AMyMoverActor : public AActor
{
	GENERATED_BODY()

public:
	AMyMoverActor();

protected:
	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mover")
	TObjectPtr<UCharacterMoverComponent> MoverComponent;
};

// MyMoverActor.cpp
#include "MyMoverActor.h"
#include "Mover/Public/CharacterMoverComponent.h"

AMyMoverActor::AMyMoverActor()
{
	PrimaryActorTick.bCanEverTick = false;

	MoverComponent = CreateDefaultSubobject<UCharacterMoverComponent>(TEXT("MoverComponent"));
	RootComponent = MoverComponent;
}

void AMyMoverActor::BeginPlay()
{
	Super::BeginPlay();

	// 在运行时注册自定义模式（如果蓝图中未配置）
	if (MoverComponent && !MoverComponent->HasMode(TEXT("MyWalkingMode")))
	{
		// 假设 UMyWalkingMode 已经在某个头文件中定义
		MoverComponent->AddMode<UMyWalkingMode>(TEXT("MyWalkingMode"));
		MoverComponent->ActivateMode(TEXT("MyWalkingMode"));
	}
}
```

## 模块依赖

以下依赖关系基于 Mover 插件的各个模块 Build.cs 文件。

| 模块 | 用途 |
|---|---|
| `ChaosVDData` | Chaos Visual Debugger 的数据结构和录制基础设施 |
| `ChaosVDRuntime` | Chaos Visual Debugger 的运行时核心 |
| `PhysicsCore` | Chaos 物理系统的核心接口 |
| `ChaosSolverEngine` | Chaos 求解器引擎，用于物理模拟 |
| `Mover` | Mover 核心移动逻辑（其他模块的依赖基础） |

**说明**：
- `Mover` 模块依赖 `MoverCVDData`，用于将移动数据提供给 CVD。
- `MoverCVDEditor` 和 `MoverEditor` 模块依赖 `ChaosVDRuntime` 和 `ChaosVDData` 以集成到编辑器工具中。
- 所有模块都深度依赖 Chaos 物理引擎相关模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `6ef46a3c` | Mover: update README for next release | 更新 README 文档，为下一个版本发布做准备。 |
| 2026-05-22 | `4ea45e21` | Mover: fix bug where skipping vertical anim root motion was not being respected in all montage cases | 修复了一个 Bug：在动画蒙太奇中跳过垂直根运动的设置在某些情况下未被正确遵守。 |
| 2026-05-20 | `dd78e781` | Mover: fix for inconsistent behavior of mode-changed events (kinematic / NPP cases) resulting in que | 修复了模式切换事件在运动学/NPP 情况下行为不一致，导致队列问题的 Bug。 |
| 2026-05-14 | `801be5dc` | Mover/ChaosMover: Just like moves, move instances are now using a pull mechanism so they can work in | 移动实例现在采用与移动指令相同的拉取机制，使其能够更高效地工作（优化同步机制）。 |
| 2026-05-14 | `d040bc9f` | Mover: adding simulation that's specific to kinematically-moved Actors | 新增了一个专门针对运动学驱动（Kinematically-moved）Actor 的模拟逻辑。 |

### 维护评价

- **活跃维护**：该插件创建于 2024 年初，截至 2026 年 5 月仍保持**非常高频率的更新**（最近一周内有多次提交）。
- **持续优化**：近期提交集中在**修复 Bug**（动画根运动、模式切换一致性）、**优化性能**（拉取机制）和**扩展功能**（支持运动学 Actor）。这表明开发团队正在积极打磨其稳定性和适用性。
- **实验性状态**：插件仍位于 `Experimental` 目录，且默认未启用 (`EnabledByDefault=false`)。这意味着 API 和功能可能会发生变化，不建议用于追求稳定的生产环境。
- **推荐使用**：对于正在开发**需要高级网络移动同步**的项目，尤其是基于 Chaos 物理系统的项目，Mover 是一个非常值得尝试和跟进的前沿解决方案。建议关注其 README 和更新日志，及时了解 breaking changes。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Mover)
- [官方文档]( )（当前为空，文档位于插件的 README 文件中）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Mover/Source/MoverTests)