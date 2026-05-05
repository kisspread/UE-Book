# Control Rig

> Framework for animation driven by user controls.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、形状库） |
| 模块 | `ControlRig` (Runtime), `ControlRigDeveloper` (Runtime), `ControlRigEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-02-08 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ControlRig) | |

## 用途

ControlRig 是一个用于创建程序化、可交互动画的运行时框架。它解决的核心问题是：**如何让动画师和技术美术师在不编写 C++ 代码的情况下，构建复杂的、可重用的动画逻辑，并在运行时高效执行。**

它通过提供一个基于节点的可视化编程环境（Rig Graph），让用户能够：
1.  **定义动画控制层级**：创建骨骼、控件（Controls）、空物体（Nulls）等元素，并定义它们之间的父子关系和约束。
2.  **编写动画逻辑**：使用数学节点、IK/FK 求解器、物理模拟节点等，构建驱动骨骼运动的逻辑图。
3.  **运行时驱动**：将构建好的 Control Rig 资产附加到骨骼网格体上，在游戏或实时应用中执行这些逻辑，实现动态的、可交互的动画效果。

它本质上是一个**动画领域的可视化脚本系统**，其底层由 **RigVM** 虚拟机驱动，确保了执行效率。

## 使用场景

-   **角色动画**：为角色创建复杂的 IK/FK 混合系统、程序化呼吸/眨眼动画、基于物理的头发/布料模拟、以及响应游戏状态（如受伤、持枪）的动画变形。
-   **载具与机械**：驱动车辆悬挂系统、机械臂的关节运动、机器人角色的程序化动画。
-   **电影与虚拟制片**：在 Sequencer 中实时预览和调整复杂的动画效果，或用于虚拟摄像机的稳定和跟踪。
-   **工具开发**：创建自定义的动画工具，例如批量重定向工具、动画数据清理工具等。

## 蓝图用法

ControlRig 的蓝图 API 主要集中在运行时对 Control Rig 实例的操控上。`ControlRigDeveloper` 模块主要提供编辑器和蓝图编译相关的功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetHierarchy` | 获取 Control Rig 实例的层次结构（URigHierarchy），用于查询和操作骨骼、控件等元素。 | `IControlRigAssetInterface` |
| `GetRigVMClient` | 获取 RigVM 客户端，用于与底层虚拟机交互。 | `IControlRigAssetInterface` |
| `FindControlRigAssetInterface` | 从一个 UObject 获取其 IControlRigAssetInterface 接口。 | `IControlRigAssetInterface` (静态) |

### 使用示例（蓝图描述）

1.  **获取并操控 Control Rig**：
    *   在角色蓝图中，获取附加的 `ControlRigComponent`。
    *   从该组件获取 `ControlRig` 对象。
    *   通过 `GetHierarchy` 节点获取其层次结构。
    *   使用 `URigHierarchy` 的蓝图函数（如 `SetTransform`, `SetControlValue`）来设置特定骨骼或控件的变换或值。

2.  **响应动画事件**：
    *   在 Control Rig 蓝图中，可以使用 `Begin Execution` 和 `Forwards Solve` 等事件节点来定义动画逻辑的执行时机。
    *   通过 `Get Animation Value` 等节点从动画蓝图获取输入数据。

## C++ 用法

ControlRig 的 C++ 用法主要涉及在运行时创建、配置和驱动 Control Rig 实例。

### 头文件引入

```cpp
#include "ControlRig.h"
#include "Rigs/RigHierarchy.h"
```

### 基本用法

```cpp
// 假设你已经有了一个 UControlRig* ControlRigInstance
// 通常通过 UControlRigComponent 或 UControlRigSubsystem 获取

// 1. 获取层次结构并查询元素
if (URigHierarchy* Hierarchy = ControlRigInstance->GetHierarchy())
{
    // 查找名为 “spine_01” 的骨骼
    const FRigElementKey BoneKey(“spine_01”, ERigElementType::Bone);
    if (FRigBoneElement* Bone = Hierarchy->Find<FRigBoneElement>(BoneKey))
    {
        // 获取其当前变换
        FTransform BoneTransform = Hierarchy->GetGlobalTransform(Bone->GetIndex());
        UE_LOG(LogTemp, Log, TEXT(“Bone %s Transform: %s”), *BoneKey.Name.ToString(), *BoneTransform.ToString());
    }

    // 查找名为 “ik_foot_l” 的控件
    const FRigElementKey ControlKey(“ik_foot_l”, ERigElementType::Control);
    if (FRigControlElement* Control = Hierarchy->Find<FRigControlElement>(ControlKey))
    {
        // 设置控件的值（例如，一个向量类型的 IK 目标位置）
        FVector IKTargetLocation(100.f, 0.f, 0.f);
        Hierarchy->SetControlValue(Control->GetIndex(), FRigControlValue::Make(FRigControlValueStorage(IKTargetLocation)));
    }
}

// 2. 执行一帧 Control Rig 逻辑
// 通常由动画系统（如 UControlRigComponent）自动调用，但也可以手动触发
ControlRigInstance->Execute(EControlRigState::Update);
```

### 进阶用法

```cpp
// 监听 Control Rig 的事件
ControlRigInstance->OnControlRigInitialized.AddLambda([](UControlRig* InControlRig)
{
    UE_LOG(LogTemp, Log, TEXT(“Control Rig %s Initialized”), *InControlRig->GetName());
});

// 在动画蓝图中，通过 FAnimNode_ControlRig 节点集成
// 这通常在编辑器中配置，但理解其原理有助于调试
// FAnimNode_ControlRig 会持有 UControlRig 实例，并在动画更新时调用其 Evaluate 方法。
```

## Demo 示例

一个最小的 C++ 示例，展示如何创建一个简单的 Control Rig 并设置其骨骼变换。

**MyControlRigDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include “MyControlRigDemo.generated.h”

class UControlRig;
class USkeletalMeshComponent;

UCLASS()
class AMyControlRigDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyControlRigDemo();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USkeletalMeshComponent> MeshComponent;

    UPROPERTY()
    TObjectPtr<UControlRig> ControlRigInstance;

    float RunningTime;
};
```

**MyControlRigDemo.cpp**
```cpp
#include “MyControlRigDemo.h”
#include “ControlRig.h”
#include “Rigs/RigHierarchy.h”
#include “Components/SkeletalMeshComponent.h”

AMyControlRigDemo::AMyControlRigDemo()
{
    PrimaryActorTick.bCanEverTick = true;
    MeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT(“Mesh”));
    RootComponent = MeshComponent;
    RunningTime = 0.f;
}

void AMyControlRigDemo::BeginPlay()
{
    Super::BeginPlay();

    // 假设你已经在编辑器中为 MeshComponent 设置了一个带有 ControlRig 的动画蓝图
    // 或者通过代码创建并初始化一个 ControlRig 实例
    // 这里演示从组件获取（如果动画蓝图中使用了 ControlRig 节点）
    // ControlRigInstance = ... 获取方式取决于你的设置
}

void AMyControlRigDemo::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    RunningTime += DeltaTime;

    if (ControlRigInstance && ControlRigInstance->GetHierarchy())
    {
        URigHierarchy* Hierarchy = ControlRigInstance->GetHierarchy();
        const FRigElementKey BoneKey(“spine_01”, ERigElementType::Bone);

        if (FRigBoneElement* Bone = Hierarchy->Find<FRigBoneElement>(BoneKey))
        {
            // 创建一个简单的正弦波运动
            FVector Offset(0.f, 0.f, FMath::Sin(RunningTime * 2.f) * 10.f);
            FTransform CurrentTransform = Hierarchy->GetGlobalTransform(Bone->GetIndex());
            CurrentTransform.AddToTranslation(Offset);
            Hierarchy->SetGlobalTransform(Bone->GetIndex(), CurrentTransform);
        }
    }
}
```

## 模块依赖

从头文件和模块类型推断，使用 `ControlRig` 模块需要以下独特依赖：

| 模块 | 用途 |
|---|---|
| `RigVM` | ControlRig 的底层虚拟机，负责执行节点图逻辑。 |
| `ControlRigDeveloper` | 提供 Control Rig 蓝图编译、图表模式、资产接口等开发时功能。 |
| `ControlRigEditor` | 提供 Control Rig 编辑器界面、图表编辑、细节面板自定义等。 |
| `AnimationCore` | 提供核心动画数学和约束功能。 |
| `AnimGraphRuntime` | 提供动画蓝图节点运行时支持。 |

## 维护状态

### 近期更新

-   2025-10-03 a54e6421c3dc 修复旧版 RigVM 参数在加载时丢失公共状态的问题
-   2025-09-15 16462964d114 Control Rig: 在加载/修补期间使用命名空间路径查找元素时暂停警告
-   2025-08-20 71816b0bf1ba Control Rig: 修复验证 Rig 模块时的崩溃问题

### 维护评价

**综合评价：活跃维护，核心功能稳定。**

-   **创建时间**：2017年创建，已有8年历史，是UE动画系统的核心组件之一。
-   **更新频率**：从近期提交看，更新非常频繁（最近一次在2025年10月），主要集中在**Bug修复、稳定性提升和兼容性改进**上。
-   **活跃度**：作为 Epic 官方维护的核心动画框架，处于**高度活跃维护**状态。
-   **已知限制**：由于其复杂性和功能强大，学习曲线较陡峭。对于非常简单的动画需求，可能显得过于重量级。
-   **推荐使用**：**强烈推荐**用于任何需要复杂、可交互、程序化动画的项目。它是UE中实现高级动画效果的首选工具。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ControlRig)
-   [官方文档](https://docs.unrealengine.com/5.7/en-US/control-rig-in-unreal-engine/) (UE5 官方文档)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ControlRig/Tests) (如果存在)