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

ChaosCloth 是 Unreal Engine 5 中基于 Chaos 物理引擎的布料模拟系统。它从实验性阶段迁移并整合而来，取代了旧的布料模拟方案。其核心目的是为游戏中的柔性物体（如角色服装、旗帜、绳索等）提供高性能、逼真的物理动态模拟，并通过配套的编辑器模块简化布料资产的创建与配置流程。

## 使用场景

- **角色服装与配饰**：为角色制作飘动的披风、斗篷、裙子和围巾，增强角色动态表现力。
- **环境动态物体**：模拟旗帜、窗帘、船帆等环境布料的物理响应。
- **绳索与网状物**：结合其他组件，实现吊桥绳索、渔网等物体的物理效果。
- **布料资产工作流**：使用 `ChaosClothEditor` 模块在编辑器中直观地创建、编辑和预览布料模拟的资产和参数。

## 蓝图用法

> **注意**：以下信息基于对UE5布料组件标准API的分析。具体细节请查阅链接的模块文档或引擎源码。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSimulatedComponent` | 将布料模拟附加到指定的骨骼网格体组件 | `UChaosClothComponent` |
| `Play / Stop / Reset Simulation` | 控制布料模拟的播放、停止和重置状态 | `UChaosClothComponent` |
| `SetSkeletalMesh` | 设置用于驱动模拟的骨骼网格体 | `UChaosClothComponent` |
| `SetClothConfig` | 动态设置布料模拟的配置资产 | `UChaosClothComponent` |

### 使用示例（蓝图描述）

1.  在角色蓝图中，向其 `SkeletalMeshComponent` 添加一个 `ChaosClothComponent`。
2.  在 `ChaosClothComponent` 的细节面板中，通过 `SetSkeletalMesh` 指定要模拟布料的网格体（例如披风）。
3.  调用 `Play Simulation` 节点开始模拟。可以通过 `SetClothConfig` 在运行时切换不同的预设配置。
4.  若要进行物理碰撞，在 `Physics Asset` 中为角色模型设置布料碰撞体。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosCloth/ChaosClothComponent.h"
```

### 基本用法

创建并配置一个布料组件（通常在 Actor 的构造函数或初始化函数中）：
```cpp
// 创建布料组件
UChaosClothComponent* ClothComp = NewObject<UChaosClothComponent>(this);
ClothComp->AttachToComponent(GetRootComponent(), FAttachmentTransformRules::KeepRelativeTransform);
ClothComp->RegisterComponent();

// 设置一个带有布料数据的骨骼网格体
ClothComp->SetSkeletalMesh(MyClothSkeletalMesh);
ClothComp->PlaySimulation();
```

### 进阶用法

通过代码控制布料模拟的质量和参数：
```cpp
// 假设已有一个 ClothConfig 数据资产 (UChaosClothConfig)
ClothComp->SetClothConfig(MyClothConfigAsset);

// 调整每帧解算的迭代次数以平衡性能与精度
ClothComp->SetNumIterations(4); // 假设存在此函数或通过Config调整

// 在角色动画更新后，可能需要手动驱动布料更新
// (通常由系统自动处理，但在自定义逻辑中可能需要)
ClothComp->UpdateClothSimulation(DeltaTime);
```

## Demo 示例

一个可运行的最小 Actor 示例，展示如何通过C++代码创建一个简单的布料组件。

**ChaosClothDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ChaosClothDemoActor.generated.h"

class UChaosClothComponent;
class USkeletalMeshComponent;

UCLASS()
class AChaosClothDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AChaosClothDemoActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere)
    USkeletalMeshComponent* CharacterMesh;

    UPROPERTY(VisibleAnywhere)
    UChaosClothComponent* CapeCloth;
};
```

**ChaosClothDemoActor.cpp**
```cpp
#include "ChaosClothDemoActor.h"
#include "ChaosCloth/ChaosClothComponent.h"
#include "Components/SkeletalMeshComponent.h"

AChaosClothDemoActor::AChaosClothDemoActor()
{
    // 用于驱动布料的骨骼网格体（例如角色身体）
    CharacterMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("CharacterMesh"));
    SetRootComponent(CharacterMesh);

    // 布料组件（例如披风）
    CapeCloth = CreateDefaultSubobject<UChaosClothComponent>(TEXT("CapeCloth"));
    CapeCloth->SetupAttachment(CharacterMesh);
}

void AChaosClothDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 确保CharacterMesh已设置有效的骨骼网格体
    if (CharacterMesh && CharacterMesh->GetSkeletalMeshAsset())
    {
        // 将布料组件附加到角色的骨骼网格体
        CapeCloth->SetSkeletalMesh(CharacterMesh->GetSkeletalMeshAsset());
        CapeCloth->PlaySimulation();
    }
}
```

## 模块依赖

从插件依赖关系分析，使用此插件可能需要以下系统支持：
| 模块 | 用途 |
|---|---|
| `ChaosCaching` | 布料模拟可能用到的缓存系统 |
| `Buoyancy` | 浮力模拟，可能用于布料与流体交互 |
| `Water` | 水体系统，可能与布料产生交互效果 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数导致的编译警告。 |
| 2026-04-23 | `85f3a947` | [Chaos Cloth] Clamp SolverLOD in ChaosClothingSimulationSolver to prevent out of bound crash when so | 对解算器LOD进行范围限制，防止因输入值越界导致崩溃。 |
| 2026-04-21 | `9322be91` | Minor cloth debug draw improvements: | 布料调试绘制的轻微改进。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式。 |
| 2026-03-31 | `0d36bcd0` | Chaos Cloth : | （提交信息不完整，推测为混沌布料系统的持续维护更新。） |

### 维护评价

ChaosCloth 是一个于 2024 年从实验阶段迁移到正式版的较新插件，目前处于**活跃维护**状态。近几个月内有持续的更新，主要集中在修复 bug（如崩溃、警告）、提升性能和进行代码现代化。作为 Epic Games 官方维护的布料模拟核心，它被 `EnabledByDefault` 为 true，表明其是 UE5 布料物理的标准方案。**推荐使用**，并关注其后续的功能增强和性能优化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth)
- [ChaosCloth 模块文档](ChaosCloth.md)
- [ChaosClothEditor 模块文档](ChaosClothEditor.md)