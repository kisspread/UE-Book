# Chaos Modular Vehicle

> Modular Vehicle Integration

| 属性 | 值 |
|---|---|
| 中文名 | 模块化车辆 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图/物理资源） |
| 模块 | `ChaosModularVehicle` (Runtime), `ChaosModularVehicleEngine` (Runtime), `ChaosModularVehicleEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosModularVehicle) | |

---

## 用途

Chaos Modular Vehicle 是 Epic Games 开发的实验性车辆物理插件，基于 Chaos 物理引擎实现 **模块化车辆集成**。传统的车辆系统（如 PhysX 的 Vehicle）将整车视为一个整体进行模拟，而本插件允许将车辆分解为多个独立的物理模拟模块（如车轮、悬挂、车身、传动部件等），每个模块独立控制、碰撞和约束，通过组合形成完整的车辆。

主要解决的问题：
- 支持**模块化拆解**：车轮、悬挂、底盘等可独立定义和替换，便于实现损坏、变形、部件分离等效果。
- 利用 Chaos 的**碰撞和约束系统**：实现更真实的力反馈和物理行为（如悬挂压缩、轮胎抓地力）。
- 提供**可扩展的模拟数据集合**：`FModularSimCollection` 继承自 `FGeometryCollection`，可直接与 Chaos 几何集合系统集成，方便复用破坏、动态碎片等功能。

适用场景：
- 制作需要**高度物理真实感**的载具游戏（赛车、越野、战斗载具）。
- 需要**部件级损坏**（车轮爆胎、悬挂断裂、引擎脱落）。
- 希望基于 Chaos 构建**自定义车辆物理**，不愿受传统 Vehicle 系统限制。

---

## 使用场景

- 你在开发一款赛车游戏，需要精确的悬挂力学和轮胎摩擦模拟 → 使用本插件构建车辆部件。
- 在战斗游戏中实现可破坏载具，车轮被打掉后车辆失去控制 → 利用模块独立模拟。
- 需要与 Chaos 破坏系统联动，车辆受撞击后车身部件分离 → 直接使用几何集合功能。

---

## 蓝图用法

> **说明**：当前插件处于实验阶段，公开的蓝图可调用接口较少。以下基于提供的头文件分析，实际 API 可能随版本更新。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get ChaosModularVehicle` | 获取插件实例（仅供 C++ 调用，蓝图无暴露） | `IChaosModularVehiclePlugin` |

**注意事项**：
- 蓝图中直接使用的节点可能位于 `ChaosModularVehicleEngine` 模块中（该模块未提供头文件）。
- 推荐使用 C++ 进行车辆组件的创建和配置。

### 使用示例（蓝图描述）

1. 在 BeginPlay 中调用 `Chaos Modular Vehicle` 相关函数（需通过 C++ 封装或插件提供的蓝图节点）。
2. 将 `ModularSimCollection` 数据资产赋予车辆 Actor 的物理模拟组件。

*当前无公开的蓝图示例，建议参考插件自带的蓝图资源（若存在）。*

---

## C++ 用法

### 头文件引入

```cpp
#include "ChaosModularVehicle/ChaosModularVehiclePlugin.h"   // 插件模块访问
#include "ChaosModularVehicle/ModularSimCollection.h"        // 模拟集合
```

### 基本用法

#### 获取插件模块单例

```cpp
IChaosModularVehiclePlugin& VehiclePlugin = IChaosModularVehiclePlugin::Get();
if (IChaosModularVehiclePlugin::IsAvailable())
{
    // 执行初始化逻辑
}
```
*来源：`ChaosModularVehiclePlugin.h`*

#### 创建模块化模拟集合（FModularSimCollection）

`FModularSimCollection` 是车辆模块化模拟的核心数据结构，继承自 `FGeometryCollection`，用于存储各模块的索引和属性。

```cpp
// 从已有的基础变换集合创建
FTransformCollection BaseCollection = CreateBaseCollection(); // 假设已有
FModularSimCollection* SimCollection = FModularSimCollection::NewModularSimulationCollection(BaseCollection);

// 直接创建空集合
FModularSimCollection* EmptySimCollection = FModularSimCollection::NewModularSimulationCollection();

// 初始化
FModularSimCollection::Init(SimCollection);

// 访问模块索引（每个变换节点对应的模拟模块 ID）
TManagedArray<int32>& SimIndex = SimCollection->SimModuleIndex; // 通过 SimModuleIndex 属性
int32 WheelIndex = SimIndex[0]; // 获取第一个变换节点的模块 ID

// 生成模拟树（将几何集合的树结构映射为模拟树）
SimCollection->GenerateSimTree();
```
*来源：`ModularSimCollection.h`*

### 进阶用法

结合 Chaos 物理场景注册模块化车辆模拟。以下从 Git 历史中的修复信息推测的典型流程：

```cpp
// 1. 初始化物理场景
FPhysScene* PhysScene = GetWorld()->GetPhysicsScene();

// 2. 创建模块化车辆 Actor，并添加 Chaos 车辆模拟组件
// （需使用 ChaosModularVehicleEngine 模块中的组件，当前头文件未提供）

// 3. 在物理场景注册时，设置正确的求解器时间倍率（避免浮点精度丢失）
// 参考 commit：b8b21b7a "Fixes a few cases where physics solver time was being cached as a 32-bit float"
// 建议在 PreDefault 阶段使用 ChaosModularVehicle::RegisterForPhysicsTick() 等接口

// 4. 注意线程安全：所有物理模拟应在游戏线程外完成
// 参考 commit: 50f458c9 "ModularVehicle: Threading issue fix"
```

---

## Demo 示例

由于插件处于实验阶段且未提供公开的测试用例，以下为基于头文件的**最小 C++ 示例**，展示如何创建并初始化一个模块化模拟集合。

```cpp
// DemoModularVehicleActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ChaosModularVehicle/ModularSimCollection.h"
#include "DemoModularVehicleActor.generated.h"

UCLASS()
class ADemoModularVehicleActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
};

// DemoModularVehicleActor.cpp
#include "DemoModularVehicleActor.h"
#include "ChaosModularVehicle/ChaosModularVehiclePlugin.h"

void ADemoModularVehicleActor::BeginPlay()
{
    Super::BeginPlay();

    // 确认插件可用
    if (IChaosModularVehiclePlugin::IsAvailable())
    {
        // 创建模拟集合
        FModularSimCollection* SimCollection = FModularSimCollection::NewModularSimulationCollection();
        if (SimCollection)
        {
            FModularSimCollection::Init(SimCollection);
            SimCollection->GenerateSimTree();
            // 后续可将其赋值给 Chaos 车辆组件
        }
    }
}
```

---

## 模块依赖

> 基于 `ChaosModularVehicle` 模块的 Build.cs 分析（未提供文件，以下根据当前头文件和插件功能推断）。

| 模块 | 用途 |
|---|---|
| `ChaosSolverEngine` | Chaos 物理求解器引擎 |
| `GeometryCollectionEngine` | 几何集合数据管理（FGeometryCollection 基类） |
| `ChaosCore` | Chaos 底层数学和数据结构 |
| `EnhancedInput` | 插件依赖的输入系统（可选，用于车辆操控） |

**注意**：实际依赖请以最终生成的 `Build.cs` 为准。若未依赖上述模块，可通过 `PublicDependencyModuleNames` 自行添加。

---

## 维护状态

### 近期更新

| 日期 | 哈希 | 说明 |
|---|---|---|
| 2025-08-20 | `d07f96e3` | 潜在崩溃修复 |
| 2025-08-19 | `750fd0ee` | 修正无效 NetToken 哈希和初始化问题 |
| 2025-08-14 | `38822c46` | 移除不必要的模块依赖 |
| 2025-07-28 | `b8b21b7a` | 修复物理求解器时间被缓存为 32 位浮点导致精度丢失的问题 |
| 2025-07-28 | `50f458c9` | 修复线程安全问题 |

### 维护评价

- **创建时间**：2025-07-28，距今约 1 个月。
- **更新频率**：非常活跃，过去一个月内有多项修复和清理。
- **活跃程度**：积极维护中，Epic 持续投入开发。
- **已知问题**：实验阶段，可能存在 API 不稳定、线程安全风险、数据类型精度问题等（均已修复记录）。
- **推荐度**：如果您正在基于 Chaos 开发自定义车辆物理，可以尝试引入，但需注意后续可能随引擎版本升级而大幅变动。建议仅在开发分支中使用，并保持与源码同步。

---

## 相关链接

- [源码仓库（Tree）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosModularVehicle)
- [官方文档](https://docs.unrealengine.com/)（当前无专门文档）
- [插件模块头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/ChaosModularVehicle/Source/ChaosModularVehicle/Public/ChaosModularVehicle/ChaosModularVehiclePlugin.h)
- [测试与示例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosModularVehicle/Tests)（若存在）