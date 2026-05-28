# Chaos Modular Vehicle

> Modular Vehicle Integration（基于 Chaos 物理引擎的模块化车辆集成系统）

| 属性 | 值 |
|---|---|
| 中文名 | 模块化车辆 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、车辆模板） |
| 模块 | `ChaosModularVehicle` (Runtime), `ChaosModularVehicleEngine` (Runtime), `ChaosModularVehicleEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-14 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle) | |

## 用途

Chaos Modular Vehicle 是一个基于 **Chaos 物理引擎**构建的**模块化车辆仿真系统**。它将车辆的物理模拟拆分为独立的模块（如车身、轮子、悬挂、引擎等），每个模块通过 `SimModuleIndex` 在几何集合（GeometryCollection）中进行索引和管理，再通过模拟树（SimTree）组织模块间的物理关系。

与传统的单体车辆组件（如 ChaosVehicleMovementComponent）不同，该插件采用**组合式架构**：开发者可以自由搭配不同的物理模块来组装车辆，而不是被固定在预设的车辆类型上。这使得在同一套框架下能覆盖从简单轿车到复杂载具（如卡车、装甲车）的各种需求。

该插件默认**未启用**（`Installed: false`）且标记为**实验性**（`IsExperimentalVersion: true`），说明 Epic 仍在迭代该功能，API 可能发生变动。

## 使用场景

- 你需要实现一个**可自定义模块化组合**的车辆系统（如赛车游戏中玩家自定义底盘+引擎+悬挂）
- 你需要基于 **Chaos 物理**（而非旧的 PhysX）进行车辆模拟
- 你的项目需要**网络同步**的车辆物理模拟（近期提交多次修复网络相关问题）
- 你需要一个支持**简化骨骼网格体**的车辆方案（近期提交修复了该场景的网络设置）

## 蓝图用法

该插件当前提供的头文件以 C++ 数据结构为主，核心的 BlueprintCallable 节点主要分布在 `ChaosModularVehicleEngine` 模块中（未在当前分析范围内展示）。基于现有源码，关键的公开 API 如下：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `NewModularSimulationCollection` | 从 TransformCollection 创建新的模块化模拟集合 | `FModularSimCollection` |
| `GenerateSimTree` | 生成模块间的模拟层级树结构 | `FModularSimCollection` |
| `Get` | 获取 ChaosModularVehicle 模块单例 | `IChaosModularVehiclePlugin` |
| `IsAvailable` | 检查模块是否已加载就绪 | `IChaosModularVehiclePlugin` |

### 使用示例（蓝图描述）

在使用前，需要在项目设置中手动启用 `ChaosModularVehicle` 插件。车辆组装流程大致如下：

1. 创建一个 `ModularSimCollection` 作为车辆的物理基础
2. 为各个模块节点设置 `SimModuleIndex`，指向对应的模拟模块
3. 调用 `GenerateSimTree` 构建模拟树
4. 通过引擎模块配置驱动力矩等参数

## C++ 用法

### 头文件引入

```cpp
#include "ChaosModularVehicle/ModularSimCollection.h"
#include "ChaosModularVehicle/ChaosModularVehiclePlugin.h"
```

### 基本用法

基于 `ModularSimCollection.h` 的 API，创建和初始化模块化模拟集合：

```cpp
// 引用自 Engine/Plugins/Experimental/ChaosModularVehicle/Source/ChaosModularVehicle/Public/ChaosModularVehicle/ModularSimCollection.h

#include "ChaosModularVehicle/ModularSimCollection.h"

// 方式一：从已有的 TransformCollection 创建模块化模拟集合
FTransformCollection* BaseTransformCollection = /* 从某处获取的基础变换集合 */ ;
FModularSimCollection* SimCollection = FModularSimCollection::NewModularSimulationCollection(*BaseTransformCollection);

// 方式二：创建空的模块化模拟集合
FModularSimCollection* EmptySimCollection = FModularSimCollection::NewModularSimulationCollection();

// 初始化（创建后必须调用）
FModularSimCollection::Init(EmptySimCollection);

// 为变换节点关联模拟模块
// SimModuleIndex 存储在 TransformGroup 中，每个索引对应一个独立的物理模拟模块
const int32 WheelModuleIndex = 0;
const int32 BodyModuleIndex = 1;
EmptySimCollection->SimModuleIndex[0] = WheelModuleIndex;
EmptySimCollection->SimModuleIndex[1] = BodyModuleIndex;

// 生成模拟树，建立模块间的物理层级关系
EmptySimCollection->GenerateSimTree();
```

### 进阶用法

检查模块可用性并安全获取单例：

```cpp
// 引用自 Engine/Plugins/Experimental/ChaosModularVehicle/Source/ChaosModularVehicle/Public/ChaosModularVehicle/ChaosModularVehiclePlugin.h

#include "ChaosModularVehicle/ChaosModularVehiclePlugin.h"

// 安全使用模式：先检查模块是否加载
if (IChaosModularVehiclePlugin::IsAvailable())
{
    IChaosModularVehiclePlugin& Module = IChaosModularVehiclePlugin::Get();
    // 进行模块操作...
}

// 使用 Chaos 序列化支持
// FModularSimCollection 支持通过 FChaosArchive 进行序列化
// Chaos::FChaosArchive& Ar = /* 获取归档器 */;
// Ar << *SimCollection;  // 序列化/反序列化
```

## Demo 示例

一个完整的最小示例，演示如何创建模块化模拟集合并配置模拟树：

```cpp
// ModularVehicleDemo.h
#pragma once

#include "CoreMinimal.h"
#include "ChaosModularVehicle/ModularSimCollection.h"

class FModularVehicleDemo
{
public:
    /** 创建一个包含两个模块（车身+轮子）的简单车辆 */
    static FModularSimCollection* CreateSimpleVehicle();

    /** 从基础变换集合创建模块化车辆 */
    static FModularSimCollection* CreateVehicleFromTransforms(const FTransformCollection& Base);
};
```

```cpp
// ModularVehicleDemo.cpp
#include "ModularVehicleDemo.h"
#include "ChaosModularVehicle/ChaosModularVehiclePlugin.h"

FModularSimCollection* FModularVehicleDemo::CreateSimpleVehicle()
{
    // 创建空的模块化模拟集合
    FModularSimCollection* Collection = FModularSimCollection::NewModularSimulationCollection();
    if (!Collection)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create ModularSimCollection"));
        return nullptr;
    }

    // 初始化集合，分配内部数据结构
    FModularSimCollection::Init(Collection);

    // 为各变换节点分配模拟模块索引
    // 索引值对应不同的物理模块（车身、轮子等）
    // 具体索引含义由 ChaosModularVehicleEngine 模块定义
    if (Collection->SimModuleIndex.Num() > 0)
    {
        Collection->SimModuleIndex[0] = 0; // 第一个节点关联模块 0
    }

    // 构建模拟树，确定模块间的父子关系和物理交互
    Collection->GenerateSimTree();

    return Collection;
}

FModularSimCollection* FModularVehicleDemo::CreateVehicleFromTransforms(const FTransformCollection& Base)
{
    return FModularSimCollection::NewModularSimulationCollection(Base);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 车辆输入控制（插件级依赖） |
| `Chaos` / `ChaosSolverEngine` | Chaos 物理引擎核心（ChaosModularVehicleEngine 隐含依赖） |

> 无其他特殊依赖（仅标准 Core/Engine/Chaos 等）。三个内部模块之间的依赖关系为：`ChaosModularVehicleEngine` 依赖 `ChaosModularVehicle`，`ChaosModularVehicleEditor` 依赖前两者。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `cd96428a` | ChaosModularVehicle: Fix ShowDebug engine torque always reporting 0 | 修复调试显示中引擎扭矩始终为零的问题 |
| 2026-04-23 | `be90176f` | Modular Vehicle: Fix the vehicle setup for the simplified skeletal mesh case when running networked. | 修复简化骨骼网格体在网络模式下的车辆初始化问题 |
| 2026-04-16 | `4ea9aba8` | [NetPhysics] Fix IsLocallyControlled ensure on physics thread in ModularVehicle | 修复物理线程上 IsLocallyControlled 断言失败的问题 |
| 2026-04-14 | `bd0ef478` | [ModularVehicle] Rely on NetworkPhysicsComponent.IsLocallyControlled from the Modular Vehicle instead | 改用 NetworkPhysicsComponent 的 IsLocallyControlled 判断本地控制状态 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 将 UE_LOG 迁移为 UE_LOGF 宏 |

### 维护评价

**活跃维护中** ✅

该插件虽然标记为实验性，但维护状态非常活跃：

- **创建时间**：2023 年 11 月，至今约 2 年，属于较新的插件
- **更新频率**：近一个月内有多次实质性提交（2026 年 4-5 月），且集中在网络同步和物理线程安全性等核心功能上
- **发展方向**：近期提交围绕**网络物理同步**进行大量修复，表明 Epic 正在将其推向多人游戏场景的生产级质量
- **风险提示**：仍标记为 `IsExperimentalVersion: true`，API 和行为可能会随版本变更；`Installed: false` 意味着需要手动启用

**建议**：适合在实验性项目或内部原型中试用，暂时不建议作为生产环境的核心车辆方案，但值得关注其发展进度。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle)
- 官方文档（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle/Tests)（如存在）