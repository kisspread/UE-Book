# Chaos Modular Vehicle Examples

> Modular Vehicle Example Assets

| 属性 | 值 |
|---|---|
| 中文名 | 模块化载具示例 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例资产） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-06 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicleExamples) | |

## 用途

这个插件是 Epic Games 提供的**模块化载具（Modular Vehicle）示例资产包**。它本身不包含 C++ 代码或新的蓝图功能，而是一系列预先构建好的蓝图资产、物理资产和网格体，旨在演示如何使用 UE5 的 Chaos 物理系统和 Mover 运动框架来构建可高度定制和模块化的载具。

插件的核心价值在于提供一个**学习和原型设计**的起点。通过分析其提供的资产，开发者可以理解如何：
1.  **解构载具**：将一个传统载具拆分为独立的物理模块（如车轮、悬挂、车身框架）。
2.  **组合模块**：利用 `ChaosMover` 和 `Mover` 框架，将各个模块的运动逻辑和物理模拟组合成一个协调的整体。
3.  **蓝图化配置**：了解如何在不编写 C++ 代码的情况下，通过蓝图调整和配置模块化载具的属性与行为。

它解决的问题是：**为复杂的、基于物理的模块化载具系统提供一个官方的、可运行的参考实现，降低开发者的入门门槛。**

## 使用场景

*   **你需要开发一个全新的、物理行为复杂的载具系统**：可以直接克隆本插件中的示例资产，替换模型和材质，并修改其蓝图逻辑来快速启动。
*   **你需要高度可定制的载具**：希望玩家或设计师能够像拼积木一样，通过更换不同的车轮、引擎模块或车身部件来改变载具性能。本插件的架构是绝佳的参考。
*   **你想学习 Chaos 模块化载具的实现原理**：通过阅读和调试插件中的蓝图资产，可以深入理解 `ChaosMover` 如何与各个物理模块交互。
*   **你想将现有的传统载具迁移到模块化架构**：本插件展示了目标架构的样子，可以作为迁移和重构的蓝图。

## 蓝图用法

本插件本身不定义新的蓝图节点。其价值在于提供的**示例蓝图资产**。开发者应直接在引擎内容浏览器中找到本插件（`/Game/Plugins/ChaosModularVehicleExamples`）并分析其中的蓝图。

### 核心资产（建议查看）

| 资产名称 | 类型 | 说明 |
|---|---|---|
| `BP_ModularVehicle_Base` | 蓝图类 | 模块化载具的基类蓝图，展示了核心组件的组织方式。 |
| `BP_Wheel_...` | 蓝图类 | 各种模块化车轮的蓝图，展示了车轮如何作为独立模块存在。 |
| `BP_Chassis_...` | 蓝图类 | 模块化车身/底盘的蓝图。 |
| `P_VehiclePhysics_...` | 物理资产 | 与模块化组件关联的物理资产，定义了碰撞和质量分布。 |

### 使用示例（蓝图描述）

1.  **创建自定义载具**：
    *   在内容浏览器中，右键 `BP_ModularVehicle_Base` 并选择“创建子类”。
    *   打开你的子类蓝图，在组件面板中，你会看到它已经包含了若干 `ChaosMoverComponent` 子对象。
    *   通过“添加组件”并关联逻辑，或替换现有组件的静态网格体/蓝图类，来构建你的载具。
2.  **替换车轮**：
    *   在载具蓝图中，找到表示车轮的组件。
    *   将其 `Wheel` 属性（或类似属性）从示例中的 `BP_Wheel_Default` 改为你自定义的 `BP_Wheel_Offroad`。

## C++ 用法

作为纯内容插件，它不提供新的 C++ API。C++ 开发者可以：
1.  **加载并实例化示例资产**：在游戏模式或自定义管理器中，使用资产路径加载并生成插件中的示例载具，用于测试。
2.  **为示例载具创建 C++ 子类**：继承插件提供的蓝图基类，在 C++ 中实现更底层的、性能敏感的控制逻辑。

### 头文件引入

```cpp
// 加载资产所需的通用头文件
#include "Engine/AssetManager.h"
#include "Engine/StreamableManager.h"
#include "UObject/SoftObjectPath.h"
```

### 基本用法

```cpp
// 在某个 Actor（如 GameMode 或自定义管理器）中，异步加载并生成一个插件中的示例载具。
// 这可以帮助你快速在关卡中测试模块化载具的行为。

// 假设我们已知示例载具蓝图的软引用路径
FSoftObjectPath ModularVehicleAssetPath(TEXT("/Game/Plugins/ChaosModularVehicleExamples/Vehicles/BP_ModularVehicle_Example.BP_ModularVehicle_Example_C"));

// 使用 StreamableManager 异步加载
UAssetManager& AssetManager = UAssetManager::Get();
FStreamableManager& StreamableManager = AssetManager.GetStreamableManager();

TSharedPtr<FStreamableHandle> Handle = StreamableManager.RequestAsyncLoad(
    ModularVehicleAssetPath,
    FStreamableDelegate::CreateLambda([this, ModularVehicleAssetPath]() {
        // 加载完成回调
        if (UClass* VehicleClass = Cast<UClass>(ModularVehicleAssetPath.ResolveObject()))
        {
            // 在场景中生成载具
            FActorSpawnParameters SpawnParams;
            GetWorld()->SpawnActor<AActor>(VehicleClass, FVector(0, 0, 100), FRotator::ZeroRotator, SpawnParams);
            UE_LOG(LogTemp, Log, TEXT("Successfully spawned modular vehicle from example plugin."));
        }
    })
);
```

## Demo 示例

以下是一个完整的、可编译的 C++ 示例，展示如何为插件提供的示例载具创建一个简单的 C++ 子类，以添加自定义输入控制。

**注意**：此示例假设你已经在项目中启用了 `ChaosModularVehicleExamples` 插件。

**MyModularVehicle.h**
```cpp
// MyModularVehicle.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "MyModularVehicle.generated.h"

// 前置声明，实际类型取决于插件基类，可能是 APawn 或自定义基类
class UChaosMoverComponent;

UCLASS()
class YOURPROJECT_API AMyModularVehicle : public APawn
{
    GENERATED_BODY()

public:
    AMyModularVehicle();

    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

protected:
    virtual void BeginPlay() override;

    // 假设插件的基类中有一个关键的 Mover 组件，我们需要获取它
    // 具体属性名和类型需要查看 BP_ModularVehicle_Base 蓝图确定
    // UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Vehicle")
    // UChaosMoverComponent* MoverComponent;

    void ApplySteering(float Value);
    void ApplyThrottle(float Value);
};
```

**MyModularVehicle.cpp**
```cpp
// MyModularVehicle.cpp
#include "MyModularVehicle.h"
#include "ChaosMoverComponent.h" // 需要包含 ChaosMover 模块的头文件

AMyModularVehicle::AMyModularVehicle()
{
    PrimaryActorTick.bCanEverTick = true;
    // 创建或查找根组件，具体做法取决于你继承的蓝图基类结构
}

void AMyModularVehicle::BeginPlay()
{
    Super::BeginPlay();
    // 在这里获取指向蓝图中配置好的 MoverComponent 的指针
    // MoverComponent = FindComponentByClass<UChaosMoverComponent>();
}

void AMyModularVehicle::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    PlayerInputComponent->BindAxis("MoveRight", this, &AMyModularVehicle::ApplySteering);
    PlayerInputComponent->BindAxis("MoveForward", this, &AMyModularVehicle::ApplyThrottle);
}

void AMyModularVehicle::ApplySteering(float Value)
{
    // 将输入传递给物理模块
    // if (MoverComponent)
    // {
    //     MoverComponent->SetSteeringInput(Value);
    // }
}

void AMyModularVehicle::ApplyThrottle(float Value)
{
    // if (MoverComponent)
    // {
    //     MoverComponent->SetThrottleInput(Value);
    // }
}
```

## 模块依赖

由于本插件是纯内容插件，其依赖项体现在 `.uplugin` 文件中声明的**插件依赖**，而非 C++ 模块依赖。要使用本插件的示例资产，你的项目必须启用以下插件：

| 插件 | 用途 |
|---|---|
| `Mover` | UE5 的通用运动框架，用于处理载具的运动逻辑。 |
| `ChaosMover` | 针对 Chaos 物理系统定制的 Mover 实现，是本示例中载具物理模拟的核心。 |

**在你的项目中启用 `ChaosModularVehicleExamples` 时，引擎会自动提示你启用这两个必需插件。**

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-11-28 | `50bfd3e5` | Update modular vehicle examples to use mover plugin | 更新模块化载具示例，使其适配并使用 Mover 插件框架。 |
| 2024-02-06 | `c28bbea3` | New modular vehicle example assets plugin | 初始提交，创建模块化载具示例资产插件。 |

### 维护评价

*   **创建时间**：约 2 年前（2024-02-06）。
*   **更新频率**：非常低，仅 2 次提交。最近一次更新在约一年前，内容是适配新的 `Mover` 插件，属于功能性的维护更新。
*   **维护状态**：**维护不活跃**。作为实验性的示例内容插件，其更新频率与 UE5 引擎底层运动/物理框架的重大变化绑定。
*   **已知问题/限制**：标记为实验性（`IsBetaVersion: true`）且默认不启用，表明其 API 和资产结构可能在未来版本中发生变化。它是学习资源，而非稳定可生产用的组件。
*   **推荐使用**：**强烈推荐用于学习和原型设计**。它是理解 UE5 Chaos 模块化载具概念的官方最佳范例。**不推荐直接用于最终发布产品**，应将其作为灵感来源和架构参考，构建自己的载具系统。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicleExamples)
*   [官方文档]() （此插件没有对应的官方文档页面）
*   [测试用例]() （此插件没有附带自动化测试用例）