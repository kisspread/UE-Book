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

Chaos Cloth 是 Unreal Engine 5 的官方布料模拟系统，基于 Chaos 物理引擎构建。它从 `Experimental` 阶段正式毕业，取代了旧版的 Apex 布料系统。该插件为角色和物体提供了高性能、高质量的实时布料模拟能力，支持复杂的布料动力学、碰撞检测、风力交互、浮力效果（通过依赖的 `Buoyancy` 和 `Water` 插件）以及缓存和回放功能（通过依赖的 `ChaosCaching` 插件）。其主要目标是让艺术家和开发者能够创建逼真的服装、旗帜、帆布等动态织物效果。

## 使用场景

- **角色服装**：为游戏角色（如披风、裙摆、围巾）添加真实的动态物理效果。
- **环境物件**：模拟旗帜、窗帘、遮阳篷等受风力或运动影响的场景元素。
- **载具与道具**：为车辆帆布、背包等附加柔性物体添加物理。
- **影视与过场动画**：制作电影级别的布料模拟，用于高品质的过场动画或预渲染序列。
- **海洋模拟**：结合 Water 和 Buoyancy 插件，实现船帆、漂浮织物等与水体交互的效果。

## 蓝图用法

基于提供的源码信息，ChaosClothEditor 模块主要提供编辑器内的可视化调试和自定义功能，没有公开的蓝图节点。布料模拟的配置和操作主要在编辑器界面（如布料资产编辑器）和 C++ 侧完成。

### 核心节点

*（无公开的蓝图可调用函数）*

## C++ 用法

ChaosClothEditor 模块主要用于扩展布料资产编辑器，提供调试绘制和自定义属性界面。使用者通常不会直接在游戏逻辑中调用此模块，而是通过 ChaosCloth 运行时模块进行布料模拟的初始化和管理。

### 头文件引入

```cpp
#include "ChaosClothEditor/ChaosClothEditorModule.h"
#include "ChaosClothEditor/ChaosSimulationEditorExtender.h"
```

### 基本用法（编辑器扩展）

以下代码展示了如何通过 `FSimulationEditorExtender` 自定义布料模拟编辑器的调试绘制选项。

*（来源：`Private/ChaosClothEditor/ChaosSimulationEditorExtender.h`）*

```cpp
// 在自定义的编辑器扩展中，重写调试绘制函数以显示额外信息
void FMySimulationEditorExtender::DebugDrawSimulation(const IClothingSimulationInterface* Simulation, USkeletalMeshComponent* OwnerComponent, FPrimitiveDrawInterface* PDI)
{
    // 调用父类绘制默认内容
    FSimulationEditorExtender::DebugDrawSimulation(Simulation, OwnerComponent, PDI);
    
    // 绘制自定义的调试信息，例如布料锚点或约束
    // ... 你的自定义绘制代码 ...
}
```

## Demo 示例

由于 ChaosCloth 是引擎级的物理系统，其“使用示例”更侧重于如何在项目中设置和配置布料资产，而非直接编写代码。一个典型的 C++ 集成示例如下：

```cpp
// MyActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()
public:
    AMyActor();

    // 布料模拟组件通常附加在 SkeletalMeshComponent 上，无需直接创建。
    // 此处演示如何通过代码影响布料模拟。
    
    /** 模拟突然的风力冲击 */
    UFUNCTION(BlueprintCallable, Category = "Cloth")
    void ApplyWindGust(FVector WindVelocity, float Duration);

protected:
    // 布料模拟组件引用，通常在蓝图或编辑器中设置
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Cloth")
    TObjectPtr<USkeletalMeshComponent> SkeletalMeshComp;
};
```

```cpp
// MyActor.cpp
#include "MyActor.h"
#include "ChaosCloth/ChaosClothSimulation.h" // 需要包含 ChaosCloth 运行时模块头文件

AMyActor::AMyActor()
{
    SkeletalMeshComp = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("SkeletalMesh"));
    RootComponent = SkeletalMeshComp;
}

void AMyActor::ApplyWindGust(FVector WindVelocity, float Duration)
{
    if (SkeletalMeshComp && SkeletalMeshComp->GetClothingSimulation())
    {
        // 获取 Chaos 布料模拟接口
        if (auto* ChaosSim = static_cast<Chaos::FClothingSimulation*>(SkeletalMeshComp->GetClothingSimulation()))
        {
            // 通过模拟接口施加外力（具体 API 需查看 ChaosCloth 运行时模块文档）
            // ChaosSim->AddForce(WindVelocity, Duration);
        }
    }
}
```

## 模块依赖

从插件的 `.uplugin` 文件及 `ChaosClothEditor` 模块的构建文件推断，使用此插件需要以下特殊依赖：

| 模块 | 用途 |
|---|---|
| `ChaosCaching` | 提供布料模拟状态的缓存与回放功能，用于动画序列录制。 |
| `Buoyancy` | 提供浮力模拟，使布料能与水体交互。 |
| `Water` | 提供水体系统，与 Buoyancy 配合实现水面交互。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数时产生的警告。 |
| 2026-04-23 | `85f3a947` | [Chaos Cloth] Clamp SolverLOD in ChaosClothingSimulationSolver to prevent out of bound crash when so | [混沌布料] 在求解器中限制 SolverLOD，以防止越界崩溃。 |
| 2026-04-21 | `9322be91` | Minor cloth debug draw improvements: | 布料调试绘制的小改进。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 UE_LOG 迁移为 UE_LOGF。 |
| 2026-03-31 | `0d36bcd0` | Chaos Cloth : | 混沌布料相关改动（提交信息不完整）。 |

### 维护评价

Chaos Cloth 插件是 UE5 官方推荐的布料解决方案，处于**活跃维护**状态。
- **创建时间**：2024年3月，是相对较新的系统。
- **近期更新**：在2026年仍有频繁的错误修复和稳定性改进，表明 Epic 持续投入维护。
- **状态**：作为从 `Experimental` 毕业的官方模块，它已被集成到引擎的核心物理管线中，不太可能被弃用。
- **推荐度**：**强烈推荐**用于新项目。它是当前 UE5 中功能最完整、性能最优且未来有保障的布料模拟方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth)
- 官方文档 (DocsURL 字段为空，建议参考 Unreal Engine 官方文档站的布料模拟章节)