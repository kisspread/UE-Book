# Chaos Cloth

> Adds Chaos Cloth modules.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosCloth` (Runtime), `ChaosClothEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth) | |

## 用途

ChaosCloth 插件提供了一套基于 Chaos 物理引擎的布料模拟系统。它的核心是替代传统的布料模拟方案，利用 UE5 主推的 Chaos 物理引擎来实现更稳定、高性能的布料模拟。这个插件从实验模块升级为核心模块，标志着 Chaos 布料系统已成为 UE5 中布料物理模拟的主流解决方案。它允许开发者为角色服装、旗帜、窗帘等添加基于物理的真实动态效果，并支持与 Chaos 引擎的其他部分（如水体、碰撞）进行交互。

## 使用场景

-   **角色服装模拟**：为游戏或虚拟角色的衣物、头发、飘带等添加基于物理的真实飘动和碰撞效果。
-   **环境布料**：模拟窗帘、旗帜、篷布等在风力或物体作用下的动态表现。
-   **与水体交互**：利用插件对 Water 插件的依赖，实现布料（如船只帆布、漂流物）与水体的真实物理交互。
-   **需要缓存的模拟**：结合 ChaosCaching 插件，可以缓存布料模拟结果，用于回放或性能优化场景。

## 蓝图用法

布料模拟主要在运行时通过 `SkeletalMeshComponent` 驱动。开发者通常在编辑器中为骨骼网格体设置好布料资产和约束后，在蓝图中主要通过组件属性控制其行为。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Cloth Simulating` | 在骨骼网格体组件上启用或禁用布料模拟 | `USkeletalMeshComponent` |
| `Set Cloth Max Distance Scale` | 动态调整布料的最大距离约束缩放 | `USkeletalMeshComponent` |

**使用示例**：
在角色蓝图中，获取其 `SkeletalMeshComponent`，然后调用 `Set Cloth Simulating` 节点来在特定时机（如游戏开始、角色换装后）启用布料物理。

## C++ 用法

核心工作流是创建并管理一个 `ChaosClothingSimulation` 实例，并将其与 `SkeletalMeshComponent` 的动画系统集成。

### 头文件引入

```cpp
#include "ChaosCloth/ChaosClothingSimulation.h"
#include "ChaosCloth/ChaosClothingSimulationFactory.h"
```

### 基本用法

创建一个布料模拟工厂并初始化模拟器。
```cpp
// 创建布料模拟器工厂
TUniquePtr<FChaosClothingSimulationFactory> ClothingFactory = MakeUnique<FChaosClothingSimulationFactory>();

// 根据骨骼网格体组件创建模拟器实例
FChaosClothingSimulation* ClothingSimulation = static_cast<FChaosClothingSimulation*>(ClothingFactory->CreateClothingSimulation());
if (ClothingSimulation)
{
    // 初始化模拟器，绑定到具体的网格体
    ClothingSimulation->Initialize(/* SkeletalMeshComponent */);
    // 在动画更新中驱动模拟
    ClothingSimulation->Simulate(/* DeltaTime */);
}
```
*(注：实际使用中，UE5 的动画系统会自动管理模拟器的生命周期，开发者主要关注配置和微调。)*

## Demo 示例

一个最小化的 C++ 示例，展示如何为一个 `SkeletalMeshComponent` 配置基本的布料模拟。
```cpp
// MyCharacter.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyCharacter.generated.h"

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere)
    USkeletalMeshComponent* ClothMeshComponent;
};

// MyCharacter.cpp
#include "MyCharacter.h"
#include "Components/SkeletalMeshComponent.h"

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    // 假设 ClothMeshComponent 已经在构造函数中创建并设置了带有布料资产的骨骼网格体
    if (ClothMeshComponent)
    {
        // 在运行时启用布料模拟
        ClothMeshComponent->SetComponentTickEnabled(true); // 确保组件 Tick 开启
        // 布料的启用通常由资产配置决定，此处为演示蓝图中常用的控制方式
        // 在蓝图中，更常见的是调用函数或设置变量来控制模拟的开关和参数
    }
}
```

## 模块依赖

ChaosCloth 依赖于 Chaos 物理引擎及其核心模块。

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心模块，提供粒子、约束、求解器等基础物理模拟能力。 |
| `ChaosCore` | Chaos 引擎的核心数据结构和工具。 |
| `PhysicsCore` | 提供物理资产、物理材质等抽象接口。 |
| `ClothingSystemRuntimeCommon` | 提供布料系统运行时的通用接口和基类。 |
| `GeometryCollectionEngine` | 与几何体集合（如破碎）系统交互，用于布料与破碎物体的碰撞。 |
| `Water` | 用于实现布料与水体物理的交互。 |
| `ChaosCaching` | 用于缓存和回放 Chaos 物理模拟（包括布料）的结果。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数产生的警告代码。 |
| 2026-04-23 | `85f3a947` | [Chaos Cloth] Clamp SolverLOD in ChaosClothingSimulationSolver to prevent out of bound crash when so | 在求解器中限制 SolverLOD 等级，防止发生越界崩溃。 |
| 2026-04-21 | `9322be91` | Minor cloth debug draw improvements: | 布料调试绘制功能的微小改进。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-03-31 | `0d36bcd0` | Chaos Cloth : | 布料相关的维护性提交。 |

### 维护评价

ChaosCloth 插件自 2024 年 3 月从 Experimental 提升为核心插件，目前处于**活跃维护**状态。从近期提交记录可以看出，开发团队在持续进行**性能优化**（如严格浮点模式优化）、**稳定性修复**（如防止越界崩溃）以及**工具改进**（如调试绘制、日志系统升级）。作为 Chaos 物理体系的关键一环，它得到了 Epic 的官方支持。该插件已取代旧的布料方案，是当前 UE5 项目中实现高质量布料物理的**推荐选择**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth/Tests)