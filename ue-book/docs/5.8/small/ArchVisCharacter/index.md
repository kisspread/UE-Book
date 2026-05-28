# ArchVis Character

> A controllable character tuned for architectural applications

| 属性 | 值 |
|---|---|
| 中文名 | 建筑可视化角色 |
| 分类 | Gameplay |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ArchVisCharacter` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2015-07-10 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ArchVisCharacter) | |

## 用途

ArchVisCharacter 插件为建筑可视化（Architectural Visualization）项目提供了一个专门优化过的第一人称角色控制器。它解决了标准游戏角色控制器在建筑漫游场景中移动和视角旋转“过于游戏化”的问题。

该插件的核心价值在于通过 `UArchVisCharMovementComponent` 对移动和旋转进行了精细的物理模拟：
*   **平滑旋转**：引入了旋转加速度、减速度和最大速度的概念，使视角转动（Pitch/Yaw）像物理摆轮一样平滑过渡，而非瞬间响应。
*   **移动约束**：提供了可调的行走摩擦、速度和加速度参数，让角色的前后左右移动感觉更沉稳、更符合建筑漫览的节奏。
*   **视角限制**：能够设置俯仰角的上下限（`MinPitch`/`MaxPitch`），防止用户看向不合理的位置。
*   **输入抽象**：将移动和视角控制映射到可自定义的输入轴名称上，方便与不同输入方案（如VR手柄、体感设备）集成。

简单来说，它让你能在建筑漫游项目中轻松获得一个“漫步”体验，而不是一个“跑酷”体验。

## 使用场景

*   你正在制作建筑可视化、室内设计预览或房地产展示项目，需要一个平滑、可控的第一人称视角来漫游场景。
*   你需要对角色的移动速度、转向手感和视角范围进行精细调整，以匹配项目的沉浸感要求。
*   你的项目需要支持非传统的输入设备（如飞行摇杆、VR控制器），并需要灵活映射输入轴。

## 蓝图用法

该插件的 `AArchVisCharacter` 和 `UArchVisCharMovementComponent` 类的大部分属性均为 `EditDefaultsOnly`，这意味着它们主要通过**蓝图类的默认值**或**实例的细节面板**进行配置，而不是通过运行时蓝图节点动态修改。

### 核心属性配置

在蓝图中，你通常通过创建 `AArchVisCharacter` 的子类来配置以下参数：

| 属性 | 说明 | 所在类 |
|---|---|---|
| `LookUpAxisName` | 绑定直接上下看的输入轴（如鼠标Y轴） | `AArchVisCharacter` |
| `TurnAxisName` | 绑定直接左右转的输入轴（如鼠标X轴） | `AArchVisCharacter` |
| `MoveForwardAxisName` | 绑定前后移动的输入轴 | `AArchVisCharacter` |
| `MoveRightAxisName` | 绑定左右移动的输入轴 | `AArchVisCharacter` |
| `MouseSensitivityScale_Pitch` | 调整鼠标上下看的敏感度 | `AArchVisCharacter` |
| `MouseSensitivityScale_Yaw` | 调整鼠标左右转的敏感度 | `AArchVisCharacter` |
| `RotationalAcceleration` | 控制视角转向的加速快慢 | `UArchVisCharMovementComponent` |
| `RotationalDeceleration` | 控制视角转向的减速快慢 | `UArchVisCharMovementComponent` |
| `MaxRotationalVelocity` | 设置视角转向的最大速度 | `UArchVisCharMovementComponent` |
| `MinPitch` / `MaxPitch` | 限制俯仰角的范围（单位：度） | `UArchVisCharMovementComponent` |
| `WalkingSpeed` | 角色的基础行走速度 | `UArchVisCharMovementComponent` |
| `WalkingAcceleration` | 角色行走时的加速度 | `UArchVisCharMovementComponent` |
| `WalkingFriction` | 行走时的摩擦力（影响停止后的滑行距离） | `UArchVisCharMovementComponent` |

### 使用示例（蓝图描述）

1.  在内容浏览器中，右键创建一个蓝图类，父类选择 `ArchVis Character`。
2.  打开该蓝图类，在“类默认值”面板中找到 “ArchVis Controls” 分类。
3.  根据你的输入设置（项目设置 -> 输入），填写对应的 `AxisName`（例如 `MouseY`, `MouseX`, `W`, `D`）。
4.  调整 `MouseSensitivityScale` 的值来改变鼠标灵敏度。
5.  在组件列表中选择 `CharacterMovement (Inherited)` 组件，在细节面板中调整 `Walking Speed`、`Walking Friction` 等移动参数。
6.  最后，调整 `Rotational Acceleration`、`MinPitch` 和 `MaxPitch` 来获得你想要的视角转动感觉和约束。
7.  将这个蓝图类设置为你的玩家控制器（Player Controller）所使用的 Pawn 类。

## C++ 用法

### 头文件引入

```cpp
#include "ArchVisCharacter.h"
#include "ArchVisCharMovementComponent.h"
```

### 基本用法

你可以直接使用 `AArchVisCharacter` 作为你的玩家角色基类，或创建子类进行扩展。主要操作是配置其属性。
**来源文件**: `ArchVisCharacter.h`, `ArchVisCharMovementComponent.h`

```cpp
// 在你的自定义角色类的构造函数中设置输入轴和灵敏度
AMyArchVisCharacter::AMyArchVisCharacter(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    // 配置输入轴名称（应与你的项目输入设置匹配）
    LookUpAxisName = TEXT("MouseY");
    TurnAxisName = TEXT("MouseX");
    MoveForwardAxisName = TEXT("MoveForward"); // 通常是‘W’键
    MoveRightAxisName = TEXT("MoveRight");     // 通常是‘D’键
    
    // 配置鼠标灵敏度
    MouseSensitivityScale_Pitch = 1.0f;
    MouseSensitivityScale_Yaw = 1.0f;
    
    // 获取并配置移动组件参数
    if (UArchVisCharMovementComponent* ArchVisMovement = GetArchVisCharMoveComponent())
    {
        ArchVisMovement->WalkingSpeed = 600.0f;
        ArchVisMovement->WalkingFriction = 8.0f;
        ArchVisMovement->MinPitch = -45.0f;
        ArchVisMovement->MaxPitch = 45.0f;
        
        // 设置更平缓的转向
        ArchVisMovement->RotationalAcceleration = FRotator(0, 180, 0); // 180度/秒^2
        ArchVisMovement->RotationalDeceleration = FRotator(0, 180, 0);
        ArchVisMovement->MaxRotationalVelocity = FRotator(0, 360, 0); // 最大360度/秒
    }
}
```

### 进阶用法

你可以继承 `AArchVisCharacter` 和 `UArchVisCharMovementComponent` 来添加自定义逻辑。

```cpp
// MyCustomMovementComponent.h
UCLASS()
class UMyCustomMovementComponent : public UArchVisCharMovementComponent
{
    GENERATED_BODY()
public:
    // 重写 PhysWalking 来添加自定义移动逻辑（如爬坡辅助）
    virtual void PhysWalking(float DeltaTime, int32 Iterations) override;
};

// MyArchVisCharacter.h
UCLASS()
class AMyArchVisCharacter : public AArchVisCharacter
{
    GENERATED_BODY()
public:
    AMyArchVisCharacter(const FObjectInitializer& ObjectInitializer);
    
    // 重写 SetupPlayerInputComponent 来绑定额外的输入动作（如跳跃）
    virtual void SetupPlayerInputComponent(UInputComponent* InputComponent) override;
    
protected:
    // 重写 MoveForward 来添加自定义移动行为（如冲刺）
    virtual void MoveForward(float Val) override;
};

// MyArchVisCharacter.cpp
AMyArchVisCharacter::AMyArchVisCharacter(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer.SetDefaultSubobjectClass<UMyCustomMovementComponent>(ACharacter::CharacterMovementComponentName))
{
    // ... 其他配置
}

void AMyArchVisCharacter::SetupPlayerInputComponent(UInputComponent* InputComponent)
{
    Super::SetupPlayerInputComponent(InputComponent);
    // 绑定额外的输入，例如跳跃
    InputComponent->BindAction("Jump", IE_Pressed, this, &ACharacter::Jump);
}

void AMyArchVisCharacter::MoveForward(float Val)
{
    // 调用父类实现，或在此处添加自定义逻辑，如检查是否允许移动
    if (Val != 0.0f)
    {
        Super::MoveForward(Val);
    }
}
```

## Demo 示例

一个最小的可编译角色类示例。

**头文件 (MyVisCharacter.h):**
```cpp
// Fill out your copyright notice in the Description page of Project Settings.
#pragma once
#include "CoreMinimal.h"
#include "ArchVisCharacter.h"
#include "MyVisCharacter.generated.h"

UCLASS()
class AMyVisCharacter : public AArchVisCharacter
{
    GENERATED_BODY()

public:
    AMyVisCharacter(const FObjectInitializer& ObjectInitializer);
};
```

**源文件 (MyVisCharacter.cpp):**
```cpp
// Fill out your copyright notice in the Description page of Project Settings.
#include "MyVisCharacter.h"
#include "ArchVisCharMovementComponent.h"

AMyVisCharacter::AMyVisCharacter(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    // 使用默认的输入轴名称 (需要确保在项目设置中已配置)
    // 覆盖一些移动参数以适应更快的漫游
    if (UArchVisCharMovementComponent* Movement = GetArchVisCharMoveComponent())
    {
        Movement->WalkingSpeed = 800.0f;
        Movement->WalkingAcceleration = 2048.0f;
        Movement->RotationalAcceleration = FRotator(0, 270, 0);
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

*   该插件的模块 `ArchVisCharacter` 的 `Build.cs` 文件未列出非常见的依赖项，其功能主要建立在 `Engine` 和 `CoreUObject` 模块中的 `ACharacter` 和 `UCharacterMovementComponent` 基础之上。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie... | 为源文件添加了宏以改善编译性能，是引擎级维护更新。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i... | 进行了全局的API导出标记更新，是引擎级构建系统维护。 |
| 2024-11-28 | `be437642` | Created missing Get/Set functions for the following member variables: | 为成员变量补充了缺失的Get/Set函数，改善了API完整性。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件的通用性更新。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新了供应商链接以使用安全协议（HTTPS），无功能改动。 |

### 维护评价

**维护不活跃**。

该插件创建于2015年，是一个相对老的组件。从提交历史看，**最后一次可能的功能性更新可以追溯到2016年左右**。过去几年（2022-2025）的提交记录全部是**引擎级的维护性更新**，如宏添加、导出标记修正、链接协议升级等，**没有针对该插件自身功能的改进或bug修复**。

这表明该插件处于一种“稳定但不再开发”的状态。它功能完整且经过了多年验证，适合用于需求简单的建筑漫游项目。但由于长期没有实质性更新，其内部实现可能没有采用最新引擎特性，且遇到问题时获得官方支持的可能性较低。

**推荐**：如果你的需求与该插件提供的功能高度匹配（平滑的建筑漫游控制），可以放心使用。如果需要更现代、功能更丰富的角色控制器（如更好的移动预测、网络支持），建议评估 `EnhancedInput` 和自定义 `CharacterMovementComponent` 的方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ArchVisCharacter)
- [官方文档]() (无)