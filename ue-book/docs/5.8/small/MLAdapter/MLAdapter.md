# ML Adapter

> A framework for training and utilizing machine learning agents in games. Creates an RPC interface through which an external process can query game state and control in-game actors. Once trained, agents can be run in-engine via neural networks loaded from ONNX models.

| 属性 | 值 |
|---|---|
| 中文名 | 机器学习适配器 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MLAdapter` (Runtime), `MLAdapterTestSuite` (DeveloperTool) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-12 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MLAdapter) | |

## 用途

MLAdapter 是 UE5 内置的**机器学习训练与推理框架**，其核心解决的问题是：如何让外部 Python 训练程序与游戏世界进行双向通信。

该插件通过 RPC（远程过程调用）接口在 UE 游戏进程和外部 ML 训练进程之间建立桥梁：

1. **观测（Observation）**：外部进程通过传感器（Sensor）获取游戏状态，如角色位置、摄像机画面、AI 感知信息等
2. **行动（Action）**：外部进程通过执行器（Actuator）向游戏发送控制指令，如按键输入、摄像机旋转等
3. **推理（Inference）**：训练完成后，可将 ONNX 模型直接加载到引擎中，由 `UMLAdapterAgent_Inference` 进行本地推理，无需外部进程

其设计思想类似于 OpenAI Gym 的空间（Space）概念，提供了 `Discrete`、`MultiDiscrete`、`Box`、`Tuple` 等数值空间定义，方便与主流 ML 框架对接。

## 使用场景

- 你需要**训练 AI 智能体**来控制游戏角色 → 使用 MLAdapter 的 RPC 接口配合 Python 训练脚本
- 你已经有一个**训练好的 ONNX 模型**，想在引擎中直接运行推理 → 使用 `UMLAdapterAgent_Inference` 配合 `UMLAdapterNoRPCManager`
- 你需要**采集游戏数据**用于离线训练 → 使用 `UMLAdapterLocalDataCollectionSession`
- 你需要自定义**传感器**（如读取特定游戏属性）或**执行器**（如执行自定义动作） → 继承 `UMLAdapterSensor` / `UMLAdapterActuator`
- 你在做**Gameplay Abilities 相关的 ML 训练** → 使用内置的 `UMLAdapterSensor_Attribute` 读取 GAS 属性

## 蓝图用法

MLAdapter 的传感器、执行器和代理类均为 `Blueprintable`，支持通过蓝图子类化进行扩展。大多数核心 API 为 C++ 虚函数，蓝图层面主要用于**配置**而非直接调用。

### 核心可配置属性

#### Agent 属性（在蓝图代理子类中配置）

| 属性 | 说明 | 类型 |
|---|---|---|
| `Sensors` | 代理拥有的传感器列表（EditInlineNew） | `TArray<UMLAdapterSensor*>` |
| `Actuators` | 代理拥有的执行器列表（EditInlineNew） | `TArray<UMLAdapterActuator*>` |
| `AvatarClass` | 此代理可控制的 Actor 类 | `TSubclassOf<AActor>` |
| `bEnableActionDuration` | 是否启用动作持续时间限制 | `bool` |
| `ActionDurationSeconds` | 动作持续时间（秒） | `float` |

#### Settings 属性（在 Project Settings → MLAdapter 中配置）

| 属性 | 说明 | 类型 |
|---|---|---|
| `ManagerClass` | 自定义 Manager 类 | `FSoftClassPath` |
| `SessionClass` | 自定义 Session 类 | `FSoftClassPath` |
| `DefaultAgentClass` | 默认代理类 | `FSoftClassPath` |
| `DefaultRPCServerPort` | RPC 服务器默认端口 | `uint16` (默认 15151) |

### 蓝图扩展方式

1. **创建自定义传感器蓝图**：新建 `UMLAdapterSensor` 的蓝图子类，在 `ConstructSpaceDef` 中定义观测空间，在 `GetObservations` 中输出观测数据
2. **创建自定义执行器蓝图**：新建 `UMLAdapterActuator` 的蓝图子类，在 `ConstructSpaceDef` 中定义动作空间，在 `DigestInputData` 中接收数据，在 `Act` 中执行动作
3. **创建自定义代理蓝图**：新建 `UMLAdapterAgent` 的蓝图子类，通过 EditInlineNew 在编辑器中直接配置传感器和执行器组合

## C++ 用法

### 头文件引入

```cpp
#include "MLAdapterModule.h"
#include "Managers/MLAdapterManager.h"
#include "Sessions/MLAdapterSession.h"
#include "Agents/MLAdapterAgent.h"
#include "Sensors/MLAdapterSensor.h"
#include "Actuators/MLAdapterActuator.h"
#include "MLAdapterSpace.h"
```

### 基本用法：获取 Manager 并启动 RPC 服务器

```cpp
// 确保 Manager 已初始化
if (UMLAdapterManager::IsReady())
{
    UMLAdapterManager& Manager = UMLAdapterManager::Get();
    
    // 启动 RPC 服务器，监听 15151 端口
    Manager.StartServer(15151, EMLAdapterServerMode::AutoDetect);
    
    // 获取当前 session（会自动创建）
    UMLAdapterSession& Session = Manager.GetSession();
    
    // 添加一个代理
    FMLAdapter::FAgentID AgentID = Session.AddAgent();
    
    // 检查代理是否就绪（已分配 avatar）
    bool bReady = Session.IsAgentReady(AgentID);
}
```

### 基本用法：自定义传感器

```cpp
// MySensor.h
#include "Sensors/MLAdapterSensor.h"

UCLASS(Blueprintable)
class UMySensor : public UMLAdapterSensor
{
    GENERATED_BODY()
public:
    // 定义观测空间
    virtual TSharedPtr<FMLAdapter::FSpace> ConstructSpaceDef() const override
    {
        // 返回一个 3 维连续空间，范围 [-1, 1]
        return FMLAdapter::FSpace_Box::Vector3D();
    }
    
    // 执行感知
    virtual void SenseImpl(const float DeltaTime) override
    {
        AActor* Avatar = GetAvatar();
        if (Avatar)
        {
            CachedLocation = Avatar->GetActorLocation();
        }
    }
    
    // 输出观测数据
    virtual void GetObservations(FMLAdapterMemoryWriter& Ar) override
    {
        FScopeLock Lock(&ObservationCS);
        Ar << CachedLocation;
    }
    
private:
    FVector CachedLocation;
};
```

### 进阶用法：自定义执行器

```cpp
// MyActuator.h
#include "Actuators/MLAdapterActuator.h"

UCLASS(Blueprintable)
class UMyActuator : public UMLAdapterActuator
{
    GENERATED_BODY()
public:
    // 定义动作空间：2 维连续空间（如移动方向 X/Y）
    virtual TSharedPtr<FMLAdapter::FSpace> ConstructSpaceDef() const override
    {
        return MakeShareable(new FMLAdapter::FSpace_Box({ 2 }, -1.f, 1.f));
    }
    
    // 从外部接收动作数据
    virtual void DigestInputData(FMLAdapterMemoryReader& ValueStream) override
    {
        FScopeLock Lock(&ActionCS);
        ValueStream << MoveDirection;
    }
    
    // 执行动作
    virtual void Act(const float DeltaTime) override
    {
        FScopeLock Lock(&ActionCS);
        APawn* Pawn = GetPawnAvatar();
        if (Pawn)
        {
            FVector Movement(MoveDirection.X, MoveDirection.Y, 0.f);
            Pawn->AddMovementInput(Movement, DeltaTime);
        }
    }
    
private:
    FVector2D MoveDirection = FVector2D::ZeroVector;
};
```

### 进阶用法：注册自定义类到 Librarian

```cpp
// 在你的模块 StartupModule 中注册自定义类
void FMyModule::StartupModule()
{
    if (UMLAdapterManager::IsReady())
    {
        UMLAdapterManager& Manager = UMLAdapterManager::Get();
        Manager.RegisterSensorClass(UMySensor::StaticClass());
        Manager.RegisterActuatorClass(UMyActuator::StaticClass());
    }
    else
    {
        // Manager 可能还未初始化，绑定到 PostInit 委托
        UMLAdapterManager::OnPostInit.AddLambda([]()
        {
            UMLAdapterManager::Get().RegisterSensorClass(UMySensor::StaticClass());
            UMLAdapterManager::Get().RegisterActuatorClass(UMyActuator::StaticClass());
        });
    }
}
```

## Demo 示例

以下是一个最小可编译的自定义传感器示例，用于读取代理 Avatar 的朝向信息：

### MyDirectionSensor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Sensors/MLAdapterSensor.h"
#include "MyDirectionSensor.generated.h"

UCLASS(Blueprintable)
class MYGAME_API UMyDirectionSensor : public UMLAdapterSensor
{
    GENERATED_BODY()

public:
    UMyDirectionSensor(const FObjectInitializer& ObjectInitializer = FObjectInitializer::Get());

protected:
    virtual TSharedPtr<FMLAdapter::FSpace> ConstructSpaceDef() const override;
    virtual void OnAvatarSet(AActor* Avatar) override;
    virtual void SenseImpl(const float DeltaTime) override;
    virtual void GetObservations(FMLAdapterMemoryWriter& Ar) override;

private:
    FVector ForwardVector;
    FVector RightVector;
};
```

### MyDirectionSensor.cpp

```cpp
#include "MyDirectionSensor.h"
#include "GameFramework/Actor.h"

UMyDirectionSensor::UMyDirectionSensor(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
}

TSharedPtr<FMLAdapter::FSpace> UMyDirectionSensor::ConstructSpaceDef() const
{
    // 6 维连续空间：Forward(3) + Right(3)
    return MakeShareable(new FMLAdapter::FSpace_Box({ 6 }, -1.f, 1.f));
}

void UMyDirectionSensor::OnAvatarSet(AActor* Avatar)
{
    Super::OnAvatarSet(Avatar);
    ForwardVector = FVector::ZeroVector;
    RightVector = FVector::ZeroVector;
}

void UMyDirectionSensor::SenseImpl(const float DeltaTime)
{
    AActor* Avatar = GetAvatar();
    if (Avatar)
    {
        ForwardVector = Avatar->GetActorForwardVector();
        RightVector = Avatar->GetActorRightVector();
    }
}

void UMyDirectionSensor::GetObservations(FMLAdapterMemoryWriter& Ar)
{
    FScopeLock Lock(&ObservationCS);
    Ar << ForwardVector;
    Ar << RightVector;
}
```

## 内置传感器与执行器

### 传感器列表

| 类名 | 说明 | 观测内容 |
|---|---|---|
| `UMLAdapterSensor_Camera` | 摄像机传感器 | 截取指定分辨率的游戏画面 |
| `UMLAdapterSensor_Movement` | 运动传感器 | 角色位置和速度（绝对或相对） |
| `UMLAdapterSensor_AIPerception` | AI 感知传感器 | 感知系统检测到的目标信息（距离、方向等） |
| `UMLAdapterSensor_Input` | 输入传感器 | 玩家输入状态（键位/轴） |
| `UMLAdapterSensor_EnhancedInput` | 增强输入传感器 | Enhanced Input 系统的动作状态 |
| `UMLAdapterSensor_Attribute` | 属性传感器 | Gameplay Abilities System 的属性值 |

### 执行器列表

| 类名 | 说明 | 动作空间 |
|---|---|---|
| `UMLAdapterActuator_Camera` | 摄像机旋转执行器 | 旋转角度（Rotator 或 Vector 模式） |
| `UMLAdapterActuator_EnhancedInput` | 增强输入执行器 | 向 TrackedActions 注入输入值 |
| `UMLAdapterActuator_InputKey` | 按键输入执行器 | 直接注入按键事件（Discrete 或 MultiBinary） |

### 推理代理

| 类名 | 说明 |
|---|---|
| `UMLAdapterAgent_Inference` | 内置神经网络推理的代理，加载 `UNNEModelData` 进行本地前向推理 |
| `UMLAdapterNoRPCManager` | 不启动 RPC 服务器的 Manager，适用于纯推理场景 |

## 空间定义系统

MLAdapter 提供了与 OpenAI Gym 类似的空间定义系统，用于描述传感器的观测空间和执行器的动作空间：

| 空间类型 | C++ 类 | 说明 |
|---|---|---|
| 离散空间 | `FMLAdapter::FSpace_Discrete` | 可数个离散值（如按键：按下/松开） |
| 多离散空间 | `FMLAdapter::FSpace_MultiDiscrete` | 多个独立的离散范围 |
| 连续空间 | `FMLAdapter::FSpace_Box` | 连续范围（如位置、速度） |
| 元组空间 | `FMLAdapter::FSpace_Tuple` | 多个子空间的组合 |

## 模块依赖

插件本身依赖 `RPCLib`、`GameplayAbilities`、`EnhancedInput`。使用该插件时，你的模块需依赖：

| 模块 | 用途 |
|---|---|
| `MLAdapter` | 核心框架（Agent/Session/Manager） |
| `GameplayAbilities` | 使用 `UMLAdapterSensor_Attribute` 时需要 |
| `EnhancedInput` | 使用 `UMLAdapterSensor_EnhancedInput` / `UMLAdapterActuator_EnhancedInput` 时需要 |
| `NNE` | 使用 `UMLAdapterAgent_Inference` 时需要（ONNX 推理） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新的 UE_LOGF 格式 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复上一次错误替换的问题 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退一次有问题的提交 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复引擎初始化委托 API 变更导致的注册问题 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复 printf 格式说明符警告 |

### 维护评价

⚠️ **维护不活跃，谨慎使用**

该插件创建于 2021 年 4 月，由 UE4ML 更名而来。标记为**实验性**且**默认不启用**。近期的提交全部为编译修复和 API 适配（日志宏迁移、委托签名变更等），**没有任何功能性更新**。

关键风险点：
- 插件被标记为 `IsExperimentalVersion = true`，Epic 未承诺长期维护
- `EnabledByDefault = false`，需手动在插件管理器中启用
- 依赖 `RPCLib`（第三方 RPC 库），可能存在版本兼容问题
- NNE（Neural Network Engine）推理接口可能随版本变化

该插件仍可作为 ML 训练的基础框架使用，但建议：
- 不要在生产环境中重度依赖
- 关注 UE 版本升级时的编译兼容性
- 考虑在 Python 端做好降级方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MLAdapter)
- 官方文档：无（`.uplugin` 中 `DocsURL` 为空）