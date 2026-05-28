# ChaosVehiclesPlugin

> Chaos Vehicle Integration（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 混沌载具插件 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosVehicles` (Runtime), `ChaosVehiclesEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosVehiclesPlugin) | |

## 用途

本插件为 Unreal Engine 5 的 **Chaos 物理系统** 提供了一套完整的车辆模拟解决方案。它不仅仅是基础的车辆物理，而是包含了一整套用于创建、调试和动画化基于 Chaos 物理的载具的编辑器工具、动画蓝图节点和运行时组件。其核心目的是取代旧的 PhysX Vehicle 插件，为开发者提供更现代、与 UE5 Chaos 物理引擎深度集成的载具开发工具链。

## 使用场景

- 你正在开发一款赛车或模拟驾驶游戏，需要高度可定制且物理真实的车辆模拟（悬挂、传动、轮胎摩擦等）。
- 你需要将车辆的骨骼网格体（Skeletal Mesh）动画与物理模拟的车轮位置同步（例如，车轮在凹凸路面上的独立运动）。
- 你的项目已经在使用 Chaos 物理系统，并希望载具物理与其他物理对象（如可破坏物）保持一致和协调。
- 你需要一个集成的编辑器工具来创建和配置车辆资产，而不是通过纯蓝图或 C++ 代码硬编码所有参数。

## 蓝图用法

本插件主要提供的是**动画蓝图节点**和**资产编辑功能**，而非通用的运行时蓝图函数。其核心运行时逻辑通常通过 C++ 组件（如 `UChaosVehicleMovementComponent`，位于 `ChaosVehicles` 模块中）驱动。

### 核心动画蓝图节点

这些节点可以在动画蓝图中用于驱动车辆骨骼网格体的车轮。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StageCoachWheelController` | 高级车轮控制器，允许更精细的动画控制，适用于复杂的悬挂动画。 | `UAnimGraphNode_StageCoachWheelController` |
| `WheelController` | 标准车轮控制器，将物理模拟的车轮位置和旋转应用到骨骼网格体上。 | `UAnimGraphNode_WheelController` |

### 使用示例（蓝图描述）

1.  打开你的车辆**动画蓝图**。
2.  在动画图表（AnimGraph）中，右键搜索“Wheel Controller”或“Stage Coach Wheel Controller”。
3.  添加节点，并将其连接到动画状态机的最终输出姿势（Final Animation Pose）之前。
4.  配置节点的细节面板（Details Panel），通常需要设置目标骨骼名称以匹配你的车轮骨骼。
5.  在运行时，该节点会从关联的 `UChaosVehicleMovementComponent` 读取物理数据，驱动车轮骨骼的旋转和位置。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosVehiclesEditorPlugin.h" // 用于编辑器插件的单例访问
#include "AnimGraphNode_WheelController.h" // 如果需要扩展或操作动画节点
```

### 基本用法

访问编辑器插件的单例，通常用于模块初始化和命令注册。

```cpp
// 来源: Public/ChaosVehiclesEditorPlugin.h
// 获取编辑器插件单例，用于访问编辑器扩展功能
if (IChaosVehiclesEditorPlugin::IsAvailable())
{
    IChaosVehiclesEditorPlugin& EditorPlugin = IChaosVehiclesEditorPlugin::Get();
    // 在此可以调用 EditorPlugin 提供的编辑器功能接口
}
```

### 进阶用法

自定义动画节点或资产类型。

```cpp
// 来源: Public/AnimGraphNode_WheelController.h
// 在代码中实例化或检查动画节点类型
UAnimGraphNode_WheelController* WheelControllerNode = NewObject<UAnimGraphNode_WheelController>();
if (WheelControllerNode)
{
    // 配置节点属性，例如要控制的骨骼名称
    // WheelControllerNode->Node.SomeProperty = ...;
}
```

## Demo 示例

一个在 C++ 中初始化车辆组件的最小示例。这假设你已经有了一个包含车轮骨骼的 SkeletalMeshComponent。

```cpp
// MyVehicle.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "MyVehicle.generated.h"

class USkeletalMeshComponent;
class UChaosVehicleMovementComponent;

UCLASS()
class AMyVehicle : public APawn
{
    GENERATED_BODY()

public:
    AMyVehicle();

    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    USkeletalMeshComponent* VehicleMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    UChaosVehicleMovementComponent* VehicleMovement;
};
```

```cpp
// MyVehicle.cpp
#include "MyVehicle.h"
#include "ChaosVehicles/Public/ChaosVehicleMovementComponent.h" // 需根据实际路径调整
#include "Components/SkeletalMeshComponent.h"

AMyVehicle::AMyVehicle()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建骨骼网格体组件
    VehicleMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("VehicleMesh"));
    RootComponent = VehicleMesh;

    // 创建并附加Chaos车辆运动组件
    VehicleMovement = CreateDefaultSubobject<UChaosVehicleMovementComponent>(TEXT("VehicleMovement"));
    VehicleMovement->SetIsReplicated(true); // 启用网络复制
    VehicleMovement->UpdatedComponent = VehicleMesh; // 将运动应用到网格体
}

void AMyVehicle::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    // 绑定输入轴到车辆运动组件的油门和转向
    PlayerInputComponent->BindAxis("Throttle", this, &UChaosVehicleMovementComponent::SetThrottleInput);
    PlayerInputComponent->BindAxis("Steer", this, &UChaosVehicleMovementComponent::SetSteeringInput);
    // 注意：UChaosVehicleMovementComponent 的绑定函数签名可能需要包装。
    // 通常更佳实践是使用 APlayerController 或 Pawn 的函数来处理输入并调用 VehicleMovement->SetThrottleInput 等。
}
```

## 模块依赖

从模块类型和用途推断，使用者通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `ChaosVehicles` | 车辆运动组件、物理模拟核心逻辑 |
| `ChaosVehiclesEditor` | 编辑器工具、资产类型、动画蓝图节点 |
| `Chaos` / `ChaosSolverEngine` | Chaos 物理引擎核心 |
| `AnimGraphRuntime` | 运行时动画图支持，用于车轮控制器节点 |
| `PhysicsAssetEditor` | （可能）用于物理资产编辑，与车辆碰撞体相关 |

**注意**：`ChaosVehiclesEditor` 是 `UncookedOnly` 类型，意味着它仅在编辑器中可用，不会被打包到最终游戏中。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数产生的编译器警告。 |
| 2026-05-12 | `400ae955` | OG Vehicle Plugin - Fix automatic transmission stuck in neutral when RPM exceeds ChangeUpRPM | 修复当转速超过升档转速时，自动变速箱卡在空挡的bug。 |
| 2026-05-12 | `6d7bcebe` | Fix UE-376288: Add HasEngine() checks before GetEngine() calls | 修复UE-376288问题：在调用GetEngine()前添加HasEngine()检查，防止空指针。 |
| 2026-04-30 | `194ad803` | Simple crash bug fix in original vehicle plugin | 修复原始车辆插件中的一个简单崩溃bug。 |
| 2026-04-23 | `97afe1bb` | [NetPhysics] Feature: Adaptive resim coalescing + MergeData semantics | [网络物理]功能：自适应重模拟合并及数据合并语义，提升网络物理同步效率。 |

### 维护评价

**ChaosVehiclesPlugin 处于“活跃维护”的实验性阶段。**
- **年龄与状态**：插件已存在约5年，但从未脱离 `Experimental` 分类，且默认未启用。
- **活跃度**：近期（2026年4-5月）有持续的代码提交，主要针对bug修复和网络物理功能增强，表明 Epic 仍在内部使用和维护此插件。
- **已知问题**：作为实验性插件，其API和功能可能在未来的引擎版本中发生重大更改或被移除。
- **推荐建议**：如果你的项目需要高度定制的Chaos车辆物理，并且愿意承担实验性功能的风险（如API不稳定、文档缺乏），可以谨慎使用并密切关注引擎更新。对于生产项目，建议评估其稳定性和长期支持状态。由于其为实验性插件，官方文档可能不完整，主要参考源代码和社区实践。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosVehiclesPlugin)
- [官方文档]()（暂无）
- [测试用例]()（未在提供的插件目录中发现标准测试文件，测试可能集成在引擎全局测试套件中）