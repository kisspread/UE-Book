# Unreal Animation Framework (UAF)

> Framework for defining functional data flow for animation systems

| 属性 | 值 |
|---|---|
| 中文名 | 虚幻动画框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产、测试数据） |
| 模块 | `UAF` (Runtime), `UAFEditor` (Runtime), `UAFTestData` (Runtime), `UAFUncookedOnly` (Runtime), `UAFTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF) | |

## 用途
UAF (Unreal Animation Framework) 旨在为 Unreal Engine 提供一个基于**函数式数据流**的新动画系统框架。它并非直接修改或替换现有的传统动画蓝图系统，而是提供一个并行的、更模块化和高性能的架构选择。该框架的核心思想是将动画数据的生产、转换和消耗定义为一系列可组合的“任务”，通过有向无环图 (DAG) 进行连接和执行。这旨在解决复杂动画逻辑的调试、可重用性和性能问题，特别适用于需要高度程序化控制和复杂动画融合的角色动画。

## 使用场景
*   **复杂角色动画**：当你的角色拥有多层运动状态（如奔跑中射击、攀爬时对话）且需要清晰的逻辑分离时。
*   **动画驱动游戏逻辑**：当动画状态需要直接影响游戏玩法（如通过动画通知精确触发伤害、武器抛壳）。
*   **程序化动画**：需要大量算法（如IK、物理模拟）与骨骼动画深度结合的场景。
*   **高性能批量动画更新**：需要处理大量NPC或生物的动画，追求比传统蓝图节点图更高执行效率的场景。
*   **开发新动画工具或插件**：当需要一个强大、可扩展的底层动画数据流框架来构建自定义工具时。

## 蓝图用法
> **重要提示**：此框架处于**实验性**阶段，API 和功能可能不完整且会发生重大变化。请勿用于生产环境。

UAF 的蓝图接口主要围绕其核心组件 `UUAFComponent` 展开。该组件负责管理和驱动附加到 Actor 上的 UAF 动画图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create UAF Component` | 创建并返回一个 UAF 组件实例，用于在蓝图中动态添加动画图管理能力。 | `UUAFComponent` |
| `Set Animation Graph` | 为 UAF 组件设置一个要执行的动画图资产（`UUAFAnimationGraph`）。 | `UUAFComponent` |
| `Start Animation Graph` | 启动当前设置的动画图执行。 | `UUAFComponent` |
| `Stop Animation Graph` | 停止当前动画图的执行。 | `UUAFComponent` |
| `Set Variable` (Float, Bool, Vector...) | 在运行时修改动画图中定义的输入变量值，用于驱动参数化动画。 | `UUAFComponent` |
| `Get Variable` (Float, Bool, Vector...) | 获取动画图中当前定义的变量值。 | `UUAFComponent` |

### 使用示例（蓝图描述）
1.  在你的角色蓝图（例如 `BP_PlayerCharacter`）中，添加一个 `UUAFComponent` 组件。
2.  通过“Set Animation Graph”节点，将一个预先创建好的 UAF 动画图资产（例如 `AGP_PlayerLocomotion`）分配给该组件。
3.  在角色蓝图的“Event BeginPlay”中，调用“Start Animation Graph”节点来启动动画。
4.  在动画更新过程中，通过“Set Variable (Float)”节点，将从输入系统或游戏逻辑获取的数值（如“Speed”）传递给动画图，以驱动混合状态。
5.  （进阶）创建一个函数，监听游戏事件（如“武器开火”），并调用“Set Variable (Bool)”或“Trigger Event”节点来通知动画图播放特定的蒙太奇或状态。

## C++ 用法
> **重要提示**：此框架处于**实验性**阶段，API 不稳定，依赖关系可能变化。

### 头文件引入
```cpp
#include "UAFComponent.h"
#include "UAFAnimationGraph.h"
#include "UAFSubsystem.h" // 如果需要通过子系统访问功能
```

### 基本用法
创建并初始化一个 UAF 组件，为其设置动画图。
```cpp
// 在 Actor 的头文件 (.h) 中声明组件
UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation")
TObjectPtr<UUAFComponent> UAFComponent;

// 在 Actor 的构造函数 (.cpp) 中创建并注册组件
AMyCharacter::AMyCharacter()
{
    // 创建组件并附加到根组件（或网格体组件）
    UAFComponent = CreateDefaultSubobject<UUAFComponent>(TEXT("UAFComponent"));
    UAFComponent->SetupAttachment(RootComponent);
}

// 在某个初始化函数（如 BeginPlay）中设置并启动动画图
void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    if (UAFComponent)
    {
        // 加载或获取动画图资产
        UUAFAnimationGraph* AnimGraph = LoadObject<UUAFAnimationGraph>(nullptr, TEXT("/Game/Characters/AG_Player"));
        if (AnimGraph)
        {
            UAFComponent->SetAnimationGraph(AnimGraph);
            UAFComponent->StartAnimationGraph();
        }
    }
}
```
*（来源：基于模块 `UAF` 的典型组件使用模式推断）*

### 进阶用法
在运行时与动画图交互，设置变量和处理动画事件。
```cpp
// 在角色移动组件的速度变化时，更新 UAF 动画图的速度变量
void AMyCharacter::OnMovementUpdated(float DeltaSeconds, const FVector& OldLocation, const FVector& OldVelocity)
{
    Super::OnMovementUpdated(DeltaSeconds, OldLocation, OldVelocity);

    if (UAFComponent)
    {
        float CurrentSpeed = GetCharacterMovement()->Velocity.Size();
        // 假设动画图中有一个名为 “Speed” 的 Float 变量
        UAFComponent->SetVariableFloat(FName(TEXT("Speed")), CurrentSpeed);
    }
}

// 处理来自动画图的事件（例如，一个动画通知触发）
// 这通常需要在 UAFComponent 的某个委托或事件回调中实现
// void AMyCharacter::HandleUAFEvent(FName EventName) { ... }
```
*（来源：基于变量设置 API 和动画事件系统的一般用法模式推断）*

## Demo 示例
> **注意**：这是一个展示核心概念的简化骨架，实际实现需要完整的 UAF 动画图资产。

```cpp
// MyAnimDemoCharacter.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyAnimDemoCharacter.generated.h"

class UUAFComponent;
class UUAFAnimationGraph;

UCLASS()
class AMyAnimDemoCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyAnimDemoCharacter();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation")
    TObjectPtr<UUAFComponent> UAFComponent;

private:
    // 用于存储动画图资产的指针
    UPROPERTY()
    TObjectPtr<UUAFAnimationGraph> LoadedAnimGraph;
};
```

```cpp
// MyAnimDemoCharacter.cpp
#include "MyAnimDemoCharacter.h"
#include "UAFComponent.h"
#include "UAFAnimationGraph.h"

AMyAnimDemoCharacter::AMyAnimDemoCharacter()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建 UAF 组件
    UAFComponent = CreateDefaultSubobject<UUAFComponent>(TEXT("UAFComponent"));
    UAFComponent->SetupAttachment(GetMesh()); // 假设附加到网格体
}

void AMyAnimDemoCharacter::BeginPlay()
{
    Super::BeginPlay();

    // 硬编码加载一个动画图资产（在实际项目中应从资产引用加载）
    LoadedAnimGraph = LoadObject<UUAFAnimationGraph>(nullptr, TEXT("/Game/UAF/Examples/AG_Demo"));
    if (LoadedAnimGraph && UAFComponent)
    {
        UAFComponent->SetAnimationGraph(LoadedAnimGraph);
        UAFComponent->StartAnimationGraph();
        UE_LOG(LogTemp, Log, TEXT("UAF Animation Graph started."));
    }
}

void AMyAnimDemoCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 简单示例：根据按键更新动画图变量
    if (UAFComponent)
    {
        bool bIsRunning = GetVelocity().Size() > 300.f;
        UAFComponent->SetVariableBool(FName(TEXT("bIsRunning")), bIsRunning);
    }
}
```

## 模块依赖
以下是使用 UAF 插件时，你的项目模块需要显式添加的**非标准**依赖。标准依赖如 Core, Engine 等无需列出。

| 模块 | 用途 |
|---|---|
| `LiveCoding` | 用于支持动画图的实时代码编辑与热重载功能（UAF 核心和 UncookedOnly 模块依赖）。 |
| `UAF` | **核心依赖**。提供所有基础的运行时框架类（组件、动画图、任务等）。 |
| `UAFEditor` | 仅编辑器依赖。提供用于创建、编辑和调试 UAF 动画图的自定义资产编辑器和工具。 |
| `UAFTestData` | 测试依赖。包含插件功能验证所需的测试资产和蓝图。 |
| `UAFUncookedOnly` | 编译依赖。包含仅在编辑器和开发版本中需要、不应打包到发布版的代码（如详细日志、特定调试功能）。 |
| `UAFTests` | 测试依赖。包含插件的自动化测试用例。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `eeaff753` | UAF: Introduce optional tick dependency between the UAF Component targeting a ACharacters mesh compo | 引入了 UAF 组件与角色网格体组件间的可选 Tick 依赖，优化执行顺序。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 解决了跨编译器（MSVC/Clang）的函数类型转换警告可移植性问题。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了格式化函数中作用域枚举使用不当导致输出乱码的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式化字符串中 32/64 位说明符与参数不匹配的问题。 |
| 2026-04-24 | `523ac953` | Fix incorrect quaternion attribute type usage | 修复了四元数属性类型使用错误的问题。 |

### 维护评价
**UAF 是一个全新的、处于积极实验阶段的框架。**

*   **活跃开发**：从首次提交（2025-06）至今约1年，最近几个月（2026-04/05）仍有持续的功能性更新和重要的bug修复，表明该项目处于**活跃维护**状态。
*   **实验性警告**：`.uplugin` 中明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`。这意味着其 API 和架构可能发生**重大且不兼容的变更**，稳定性未得到保证。
*   **推荐使用建议**：
    *   **学习与研究**：非常适合用于研究 UE5 未来动画系统的可能方向，或学习函数式动画数据流的设计模式。
    *   **实验项目**：可用于个人实验项目、原型开发或GameJam。
    *   **生产项目**：**强烈不建议**在正式发布的生产项目中使用，除非你有充分的资源来应对未来可能的大规模重构，并接受其固有的不稳定性。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF)
- [官方文档]() （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/Tests)