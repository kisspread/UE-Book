# PhysicsControl

> Physically control static and skeletal meshes through the Physics Control Component and the Rigid Body With Control animation graph node.

| 属性 | 值 |
|---|---|
| 中文名 | 物理控制 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画蓝图节点、调试界面资产） |
| 模块 | `PhysicsControl` (Runtime), `PhysicsControlUncookedOnly` (UncookedOnly), `PhysicsControlEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PhysicsControl) | |

## 用途

该插件提供了一种新的物理控制机制，允许开发者通过专用的**物理控制组件（Physics Control Component）**和**动画蓝图节点（Rigid Body With Control）**，在角色/物体的物理模拟与动画控制之间实现精细的混合。它旨在替代或增强传统的 ragdoll 和布娃娃系统，让开发者能够：

- 对骨骼网格体的特定身体部位施加物理力（如风力、击打、拖动），同时保持其他部位的动画驱动。
- 动态切换物理控制与动画混合，支持局部物理模拟。
- 通过控制配置（Control Profiles）和应用掩码，灵活调整不同骨骼的控制行为。

该插件目前处于 Beta 阶段，是“Ch5 运动学倡议”的一部分，用于原型开发。

## 使用场景

- **角色受击反馈**：角色受到攻击时，将受击部位切换为物理模拟，产生自然的碰撞和抖动效果，随后平滑恢复动画。
- **动态物理道具**：让角色的武器或配件跟随物理模拟，同时保留角色身体动画的完整性。
- **环境交互**：角色与场景物体（如绳索、布料）通过物理控制组件进行交互，例如角色伸手推开物体。
- **混合动画调试**：在开发阶段，通过“操作器查看器”标签页可视化控制组、身体修饰器和约束状态，辅助调试物理控制行为。

## 蓝图用法

该插件主要提供 **Animation Blueprint 节点** 和 **Physics Control Component** 的蓝图接口。由于组件 API 较多，此处仅列出最核心的节点和函数。

### 动画蓝图节点

在动画蓝图中添加 **Rigid Body With Control** 节点（位于 `Physics` 类别下），用于将物理控制嵌入动画流程。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Rigid Body With Control` | 对骨骼网格体应用物理控制，可设置身体修饰器、控制集、约束等参数 | `UAnimGraphNode_RigidBodyWithControl` |

节点属性（在细节面板中编辑）：
- **Body Modifiers**：定义哪些身体（骨骼）参与物理模拟。
- **Controls**：定义施加的力或运动控制（如目标位置、力大小）。
- **Constraint Profiles**：定义关节约束剖面。
- **Control Profiles**：定义控制集的快速切换。

### 物理控制组件（UPhysicsControlComponent）

该组件可在蓝图或 C++ 中附加到 Actor 上使用。常用蓝图函数（需搜索 `PhysicsControl` 相关节点）：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetControlProfile` | 按名称应用控制配置文件（可设置是否传入掩码） | `UPhysicsControlComponent` |
| `AddControl` | 添加一个身体控制（如目标空间、刚度、阻尼等） | `UPhysicsControlComponent` |
| `RemoveControl` | 移除指定控制 | `UPhysicsControlComponent` |
| `GetPhysicalAnimationComponent` | 获取指向物理动画组件的引用（用于传统物理动画混合） | `UPhysicsControlComponent` |

**使用示例（蓝图）**：
1. 在角色蓝图中添加一个 `Physics Control Component`。
2. 在事件图表中调用 `Add Control`，指定骨骼名称（如 `pelvis`）和控制参数。
3. 在动画蓝图中使用 `Rigid Body With Control` 节点，并设置其 `Body Modifiers` 引用同一骨骼。
4. 运行游戏后，该骨骼将受到物理控制。

## C++ 用法

### 头文件引入

```cpp
#include "PhysicsControlComponent.h"          // 运行时组件
#include "AnimNode_RigidBodyWithControl.h"    // 动画节点
```

### 基本用法

**创建物理控制组件**（通常由 Actor 自动创建）：

```cpp
// 在 Actor 的构造函数中
UPhysicsControlComponent* PhysicsControlComp = CreateDefaultSubobject<UPhysicsControlComponent>(TEXT("PhysicsControl"));
```

**添加身体控制**（代码来自测试用例 `PhysicsControlTest.cpp`）：

```cpp
// 为指定骨骼添加弹簧-阻尼控制
FName BoneName = TEXT("hand_r");
FPhysicsControlData ControlData;
ControlData.Strength = 100.0f;
ControlData.DampingRatio = 0.5f;

FPhysicsControlSettings ControlSettings;
UPhysicsControlComponent* Comp = ...;
Comp->AddControl(BoneName, ControlData, ControlSettings);
```

**应用控制配置文件**（来自 git commit `Support using a mask when invoking control profiles`）：

```cpp
// 应用名为 "PushProfile" 的控制剖面，仅影响指定躯干
TArray<FName> MaskBones = { TEXT("spine_01"), TEXT("spine_02") };
Comp->SetControlProfile(TEXT("PushProfile"), MaskBones);
```

### 进阶用法

**在动画蓝图中自定义 `Rigid Body With Control` 节点**（需继承 `FAnimNode_RigidBodyWithControl`）：

```cpp
// AnimNodeMyRigidBody.h
#pragma once
#include "AnimNode_RigidBodyWithControl.h"
#include "AnimNodeMyRigidBody.generated.h"

USTRUCT()
struct FAnimNodeMyRigidBody : public FAnimNode_RigidBodyWithControl
{
    GENERATED_BODY()
    // 添加自定义逻辑...
};
```

然后在动画蓝图节点类中注册：

```cpp
UCLASS()
class UAnimGraphNode_MyRigidBody : public UAnimGraphNode_RigidBodyWithControl
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, Category = Settings)
    FAnimNodeMyRigidBody Node;
    // ...
};
```

**访问操作器查看器界面**（用于编辑器调试）：

```cpp
// 通过 IPhysicsControlOperatorViewerInterface
if (auto* Viewer = IModularFeatures::Get().GetModularFeature<IPhysicsControlOperatorViewerInterface>(IPhysicsControlOperatorViewerInterface::GetModularFeatureName()))
{
    Viewer->OpenOperatorNamesTab();  // 打开控件/修饰器名称查看器
}
```

## Demo 示例

以下是一个最小 C++ 示例，展示如何在 Actor 中使用物理控制组件控制角色右手。

**MyPhysicsActor.h**:
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "PhysicsControlComponent.h"
#include "MyPhysicsActor.generated.h"

UCLASS()
class AMyPhysicsActor : public AActor
{
    GENERATED_BODY()
public:
    AMyPhysicsActor();

    UFUNCTION(BlueprintCallable, Category = "PhysicsControl")
    void ApplyForceToHand();

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    UPhysicsControlComponent* PhysicsControlComp;
};
```

**MyPhysicsActor.cpp**:
```cpp
#include "MyPhysicsActor.h"

AMyPhysicsActor::AMyPhysicsActor()
{
    PrimaryActorTick.bCanEverTick = true;
    PhysicsControlComp = CreateDefaultSubobject<UPhysicsControlComponent>(TEXT("PhysicsControl"));
}

void AMyPhysicsActor::ApplyForceToHand()
{
    if (!PhysicsControlComp) return;

    FName BoneName = TEXT("hand_r");
    // 创建一个简单的施力控制
    FPhysicsControlData ControlData;
    ControlData.Strength = 500.0f;
    ControlData.DampingRatio = 0.3f;
    ControlData.TeleportDistanceThreshold = 100.0f;
    ControlData.TeleportRotationThreshold = 45.0f;

    FPhysicsControlTarget TargetData;
    TargetData.TargetLocation = FVector(0, 0, 0); // 相对位置（在动画空间）
    TargetData.TargetOrientation = FQuat::Identity;
    TargetData.bApplyControlPoint = false;

    PhysicsControlComp->AddControl(
        BoneName,
        ControlData,
        FPhysicsControlSettings(),
        TargetData,
        NAME_None,
        NAME_None
    );
}
```

在动画蓝图中，使用 `Rigid Body With Control` 节点并引用同一骨骼 `hand_r`，即可在运行时通过调用 `ApplyForceToHand` 触发物理响应。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimGraphRuntime` | 提供动画蓝图运行时支撑 |
| `Chaos` | 物理引擎核心，用于刚体模拟 |
| `Ragdoll` | 布娃娃系统基础（被该插件增强） |
| `PhysicsControl` (自身) | 运行时模块，所有其他模块依赖它 |

其他常见依赖（Core, Engine, Slate 等）已省略。

## 维护状态

### 近期更新

- 2025-11-18 `bfe41435` 将插件标记为 Beta 版本
- 2025-09-26 `e040cfab` 禁用 RigidBodyWithControl 在测试/发布下的诊断日志，降低日志级别为 Verbose
- 2025-09-23 `7b7ebe09` 支持调用控制配置文件时使用掩码
- 2025-09-23 `4e0fa71d` 在所有函数中支持控制/修饰器/集合名称，整理文档，无行为变化
- 2025-09-23 `4bdb12a5` 对齐 RigidBodyWithControl 的 KinematicTargetSpace 与 PhysicsControl 其他部分

### 维护评价

该插件创建于 2025 年 9 月，至今不到半年，但已有多次功能性更新（添加掩码支持、对齐功能、Beta 标记）。开发活跃，团队正在积极完善。当前为 Beta 阶段，API 可能还会变动，但已可用于原型开发。推荐在项目中使用时注意锁定引擎版本，并关注后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PhysicsControl)
- [官方文档](https://docs.unrealengine.com/5.4/en-US/physics-control-in-unreal-engine/)（暂未提供专用页面，可使用通用物理控制参考）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PhysicsControl/Tests)