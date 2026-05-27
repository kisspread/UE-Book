# Chaos Modular Vehicle

> Modular Vehicle Integration（模块化载具集成）

| 属性 | 值 |
|---|---|
| 中文名 | 模块化载具 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、输入修饰器） |
| 模块 | `ChaosModularVehicle` (Runtime), `ChaosModularVehicleEngine` (Runtime), `ChaosModularVehicleEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-14 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle) | |

## 用途

ChaosModularVehicle 是基于 Chaos 物理引擎构建的**模块化载具仿真系统**。与传统载具插件（如 ChaosVehicle）将所有功能封装在单个组件中不同，本插件采用"可组合"的模块化架构：载具由多个独立的仿真模块（轮子、悬挂、引擎、变速箱、底盘、气动翼面、推进器等）组装成**树形结构**运行。

这套系统解决了以下核心问题：

- **高度可定制**：每个模块独立运作，可通过拼接不同模块构建汽车、飞机、气垫船、气球载具等任意构型
- **物理线程异步仿真**：仿真代码在物理线程运行，不阻塞游戏线程
- **网络预测与回滚**：内建网络物理支持，支持输入插值、状态回滚和重模拟
- **骨架网格动画**：模块输出自动驱动骨骼动画，适配动画蓝图

## 使用场景

- 你需要从零组装一辆汽车（引擎+变速箱+离合器+轮子+悬挂+底盘）→ 给 Actor 添加对应 SimComponent 并挂载到 ClusterUnion
- 你需要制作飞行器（气动翼面+方向舵+升降舵+推进器）→ 使用 Aerofoil/Thruster 组件组合
- 你需要多人同步的载具 → 依赖 NetworkPhysicsComponent 实现输入预测和状态回滚
- 你需要模块化载具支持热插拔组件（如战斗中拆卸轮子）→ 利用 ClusterUnion 的动态 AddComponent 机制

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetInputBool` | 设置布尔型控制输入（如手刹） | `UModularVehicleBaseComponent` |
| `SetInputInteger` | 设置整数型控制输入（如档位） | `UModularVehicleBaseComponent` |
| `SetInputAxis1D` | 设置一维轴输入（如油门、转向） | `UModularVehicleBaseComponent` |
| `SetInputAxis2D` | 设置二维轴输入（如摇杆） | `UModularVehicleBaseComponent` |
| `SetInputAxis3D` | 设置三维轴输入（如推力方向） | `UModularVehicleBaseComponent` |
| `SetGearInput` | 直接设置当前档位 | `UModularVehicleBaseComponent` |
| `GetCurrentGear` | 获取当前实际档位 | `UModularVehicleBaseComponent` |
| `IsReversing` | 是否在倒车 | `UModularVehicleBaseComponent` |
| `SetLocallyControlled` | 标记为本地控制 | `UModularVehicleBaseComponent` |
| `SetInputProducerClass` | 替换输入生产者类（用于 AI 或回放） | `UModularVehicleBaseComponent` |
| `AddActorsToIgnore` | 添加悬挂射线检测忽略的 Actor | `UModularVehicleBaseComponent` |
| `RemoveActorsToIgnore` | 移除忽略列表中的 Actor | `UModularVehicleBaseComponent` |

### 事件

| 事件 | 说明 | 所在类 |
|---|---|---|
| `OnModuleAdded` | 模块被添加到仿真树时触发 | `UModularVehicleBaseComponent` |
| `OnModuleRemoved` | 模块从仿真树移除时触发 | `UModularVehicleBaseComponent` |
| `OnWheelTouchChange` | 轮子接触/离开地面时触发 | `UVehicleSimWheelComponent` |
| `OnGearChange` | 档位变化时触发 | `UVehicleSimTransmissionComponent` |

### 使用示例（蓝图描述）

**搭建一辆简单汽车：**

1. 创建 `AModularVehicleClusterPawn`（已包含 ClusterUnionVehicleComponent + ModularVehicleBaseComponent）
2. 给 Pawn 添加静态网格组件作为车身，添加到 ClusterUnion
3. 添加 4 个 `UVehicleSimWheelComponent`（子组件），设置 WheelRadius、FrictionMultiplier 等
4. 添加 4 个 `UVehicleSimSuspensionComponent`（子组件），设置弹簧参数
5. 添加 1 个 `UVehicleSimEngineComponent`，设置扭矩曲线
6. 添加 1 个 `UVehicleSimTransmissionComponent`，设置齿比数组
7. 在 `InputConfig` 数组中配置输入映射（名称→类型）
8. 通过 EnhancedInput Action 的回调调用 `SetInputAxis1D("Throttle", Value)` 驱动载具

**输入平滑：**

在 EnhancedInput 的 Action 映射上添加 `UInputModifier_ModularVehicleSmooth` 修饰器，设置 `RiseRate` 控制输入响应速度，模拟传统载具的惯性感。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosModularVehicle/ModularVehicleBaseComponent.h"
#include "ChaosModularVehicle/VehicleSimWheelComponent.h"
#include "ChaosModularVehicle/VehicleSimEngineComponent.h"
#include "ChaosModularVehicle/VehicleSimSuspensionComponent.h"
#include "ChaosModularVehicle/VehicleSimTransmissionComponent.h"
#include "ChaosModularVehicle/InputProducer.h"
```

### 基本用法

以下代码演示如何在 C++ 中设置载具输入：

```cpp
// 在控制器或 Pawn 的 Tick 中调用
// 来源：Public/ChaosModularVehicle/ModularVehicleBaseComponent.h

if (UModularVehicleBaseComponent* VehicleComp = GetVehicleSimulationComponent())
{
    // 设置油门输入（1D 轴）
    VehicleComp->SetInputAxis1D(FName("Throttle"), ThrottleValue);

    // 设置转向输入
    VehicleComp->SetInputAxis1D(FName("Steer"), SteerValue);

    // 设置手刹（布尔值）
    VehicleComp->SetInputBool(FName("Handbrake"), bHandbrake);

    // 直接换挡
    VehicleComp->SetGearInput(2);

    // 获取当前档位
    int32 CurrentGear = VehicleComp->GetCurrentGear();
}
```

### 进阶用法

**自定义输入生产者（用于 AI 或回放）：**

```cpp
// 来源：Public/ChaosModularVehicle/InputProducer.h
// UVehiclePlaybackInputProducer 用于录制回放，UVehicleRandomInputProducer 用于随机输入测试

// 创建随机输入生产者（AI 场景）
VehicleComp->SetInputProducerClass(UVehicleRandomInputProducer::StaticClass());

// 创建回放输入生产者
VehicleComp->SetInputProducerClass(UVehiclePlaybackInputProducer::StaticClass());
```

**监听模块事件：**

```cpp
// 来源：Public/ChaosModularVehicle/ModularVehicleBaseComponent.h
// Native 委托（高性能，无蓝图开销）

VehicleComp->OnModuleAddedNativeEvent.AddLambda(
    [](const FName& SimType, int Guid, int TreeIndex)
    {
        UE_LOG(LogTemp, Log, TEXT("Module added: %s, GUID: %d, TreeIndex: %d"),
            *SimType.ToString(), Guid, TreeIndex);
    });

VehicleComp->OnModuleRemovedNativeEvent.AddLambda(
    [](const FName& SimType, int Guid, int TreeIndex)
    {
        UE_LOG(LogTemp, Log, TEXT("Module removed: %s, GUID: %d"), *SimType.ToString(), Guid);
    });
```

## Demo 示例

**最小可编译的自定义载具 Pawn：**

```cpp
// MyModularVehicle.h
#pragma once

#include "CoreMinimal.h"
#include "ChaosModularVehicle/ModularVehicleClusterPawn.h"
#include "MyModularVehicle.generated.h"

UCLASS()
class AMyModularVehicle : public AModularVehicleClusterPawn
{
    GENERATED_BODY()

public:
    AMyModularVehicle();

    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
    virtual void Tick(float DeltaTime) override;

protected:
    UPROPERTY(EditAnywhere, Category = "Input")
    float ThrottleValue = 0.f;

    UPROPERTY(EditAnywhere, Category = "Input")
    float SteeringValue = 0.f;
};
```

```cpp
// MyModularVehicle.cpp
#include "MyModularVehicle.h"
#include "ChaosModularVehicle/ModularVehicleBaseComponent.h"
#include "EnhancedInputComponent.h"
#include "InputAction.h"

AMyModularVehicle::AMyModularVehicle()
{
    // VehicleSimComponent 和 ClusterUnionVehicleComponent
    // 已由父类 AModularVehicleClusterActor 创建
}

void AMyModularVehicle::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    // 假设已在蓝图中绑定 InputAction
    // 通过 EnhancedInputComponent 绑定输入
    if (auto* EIC = Cast<UEnhancedInputComponent>(PlayerInputComponent))
    {
        // 绑定油门和转向后，在回调中调用：
        // VehicleSimComponent->SetInputAxis1D(FName("Throttle"), Value);
        // VehicleSimComponent->SetInputAxis1D(FName("Steer"), Value);
    }
}

void AMyModularVehicle::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (VehicleSimComponent)
    {
        // 持续推送输入
        VehicleSimComponent->SetInputAxis1D(FName("Throttle"), ThrottleValue);
        VehicleSimComponent->SetInputAxis1D(FName("Steer"), SteeringValue);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心（仿真模块树、约束、物理代理） |
| `ChaosSolverEngine` | Chaos 求解器（物理场景管理） |
| `PhysicsCore` | 物理核心类型和接口 |
| `NetworkPhysics` | 网络物理预测/回滚框架（FNetworkPhysicsData 基类） |
| `ClusterUnion` | 集群联合体（动态组装物理体） |
| `EnhancedInput` | 插件级依赖，输入系统（InputModifier 支持） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `cd96428a` | ChaosModularVehicle: Fix ShowDebug engine torque always reporting 0 | 修复调试显示中引擎扭矩始终为 0 的问题 |
| 2026-04-23 | `be90176f` | Modular Vehicle: Fix the vehicle setup for the simplified skeletal mesh case when running networked. | 修复联网时简化骨骼网格载具配置问题 |
| 2026-04-16 | `4ea9aba8` | [NetPhysics] Fix IsLocallyControlled ensure on physics thread in ModularVehicle | 修复物理线程上 IsLocallyControlled 断言失败 |
| 2026-04-14 | `bd0ef478` | [ModularVehicle] Rely on NetworkPhysicsComponent.IsLocallyControlled from the Modular Vehicle instead | 改用 NetworkPhysicsComponent 判断本地控制状态 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到 UE_LOGF 格式 |

### 维护评价

- **活跃维护**：最近 1 个月内有多次功能性修复和改进，处于活跃开发阶段
- **网络物理集成完善**：近期重点修复联网场景下的本地控制判断和骨骼网格同步问题
- **实验性标记仍在**：`IsExperimentalVersion=true`，API 可能在后续版本中变动
- **依赖增强**：依赖 EnhancedInput、NetworkPhysics、ClusterUnion 等较新系统，整体技术栈现代化
- **推荐使用**：适合需要高度定制化载具仿真的项目，但需注意实验性状态，生产环境需谨慎评估稳定性

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle)
- [官方文档](https://epicgames.com)（暂无专项文档）