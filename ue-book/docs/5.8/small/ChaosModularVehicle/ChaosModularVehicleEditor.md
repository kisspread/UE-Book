# Chaos Modular Vehicle

> Modular Vehicle Integration（模块化载具集成）

| 属性 | 值 |
|---|---|
| 中文名 | 模块化载具 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、载具动画） |
| 模块 | `ChaosModularVehicle` (Runtime), `ChaosModularVehicleEngine` (Runtime), `ChaosModularVehicleEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-14 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle) | |

## 用途

ChaosModularVehicle 是基于 Chaos 物理引擎的模块化载具系统。与传统载具插件不同，它允许将载具拆分为独立的物理模块（如车身、轮子、引擎等），每个模块可独立配置物理属性和行为。该插件解决了传统载具系统中组件耦合度过高的问题，使载具的物理模拟更加灵活和可定制。

该插件适用于需要复杂载具物理行为的场景，如赛车游戏中的精细调校、载具损坏系统、以及需要动态组合载具部件的沙盒游戏。

## 使用场景

- 你需要一辆可高度自定义物理行为的赛车，独立调整引擎扭矩、悬挂参数
- 你在开发载具损坏系统，需要载具部件可独立模拟物理
- 你在制作沙盒游戏，玩家可以自由组合载具部件
- 你需要精确控制载具在多人游戏中的网络同步行为

## 蓝图用法

该插件主要通过动画蓝图节点和载具配置资产进行蓝图交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AnimNode_ModularVehicleController` | 模块化载具动画控制器节点，用于动画蓝图中驱动载具骨骼 | `UAnimGraphNode_ModularVehicleController` |

### 动画蓝图配置

1. 在载具的动画蓝图中添加 `AnimGraphNode_ModularVehicleController` 节点
2. 该节点只能在 `VehicleAnimInstance` 及其子类中使用
3. 配置节点属性以匹配载具的物理参数

## C++ 用法

### 头文件引入

```cpp
// 模块化载具核心模块
#include "ChaosModularVehicle.h"

// 模块化载具引擎模块
#include "ChaosModularVehicleEngine.h"
```

### 基本用法

使用模块化载具的核心组件设置载具物理模拟。

```cpp
// 设置模块化载具实例
// 来源: Source/ChaosModularVehicle/
UChaosModularVehicleComponent* VehicleComponent = NewObject<UChaosModularVehicleComponent>(OwnerActor);
VehicleComponent->SetupAttachment(RootComponent);
VehicleComponent->RegisterComponent();
```

### 网络同步用法

该插件包含完善的网络物理同步支持，使用 `NetworkPhysicsComponent` 进行权威判断。

```cpp
// 网络模式下判断是否本地控制
// 来源: git commit bd0ef478 - 使用 NetworkPhysicsComponent.IsLocallyControlled
if (NetworkPhysicsComponent->IsLocallyControlled())
{
    // 本地玩家控制的载具，执行输入处理
}
```

## Demo 示例

```cpp
// ModularVehicleExample.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "ModularVehicleExample.generated.h"

UCLASS()
class AModularVehicleExample : public APawn
{
    GENERATED_BODY()

public:
    AModularVehicleExample();

    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    class USkeletalMeshComponent* VehicleMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    class UChaosModularVehicleComponent* ModularVehicle;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    class UChaosModularVehicleEngineComponent* EngineComponent;
};
```

```cpp
// ModularVehicleExample.cpp
#include "ModularVehicleExample.h"
#include "ChaosModularVehicleComponent.h"
#include "ChaosModularVehicleEngineComponent.h"

AModularVehicleExample::AModularVehicleExample()
{
    VehicleMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("VehicleMesh"));
    RootComponent = VehicleMesh;

    ModularVehicle = CreateDefaultSubobject<UChaosModularVehicleComponent>(TEXT("ModularVehicle"));
    ModularVehicle->SetupAttachment(VehicleMesh);

    EngineComponent = CreateDefaultSubobject<UChaosModularVehicleEngineComponent>(TEXT("Engine"));
    EngineComponent->SetupAttachment(VehicleMesh);
}

void AModularVehicleExample::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    // 使用 EnhancedInput 进行输入绑定
}
```

## 模块依赖

该插件依赖以下外部插件：

| 模块/插件 | 用途 |
|---|---|
| `EnhancedInput` | 高级输入系统，用于载具控制输入绑定 |
| `ChaosVehicles` | Chaos 载具基础物理模块（隐式依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `cd96428a` | ChaosModularVehicle: Fix ShowDebug engine torque always reporting 0 | 修复引擎扭矩调试显示始终为 0 的问题 |
| 2026-04-23 | `be90176f` | Modular Vehicle: Fix the vehicle setup for the simplified skeletal mesh case when running networked. | 修复简化骨骼网格体在网络模式下的载具配置 |
| 2026-04-16 | `4ea9aba8` | [NetPhysics] Fix IsLocallyControlled ensure on physics thread in ModularVehicle | 修复物理线程上 IsLocallyControlled 的断言错误 |
| 2026-04-14 | `bd0ef478` | [ModularVehicle] Rely on NetworkPhysicsComponent.IsLocallyControlled from the Modular Vehicle instea | 改用 NetworkPhysicsComponent 判断本地控制 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至新格式 UE_LOGF |

### 维护评价

该插件处于**活跃维护**状态。从提交记录看，近期（2026年4-5月）有密集的功能修复和改进，主要集中在：
- **网络同步优化**：多个提交修复了多人游戏场景下的物理同步问题，说明该插件正在完善多人游戏支持
- **调试工具改进**：修复了调试显示的 bug，便于开发阶段的问题排查
- **代码现代化**：迁移至新的日志宏格式，表明持续跟进引擎更新

**注意事项**：
- 该插件标记为实验性（IsExperimentalVersion=true），默认未启用
- 需要在插件管理器中手动启用
- API 可能在后续版本中发生变化
- 适合早期原型开发和测试，不建议直接用于生产环境

**推荐程度**：⭐⭐⭐（适合探索和原型开发，生产环境需谨慎评估）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle)
- 官方文档：暂无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle/Tests)（如有）