# RigLogic Plugin

> RigLogic Plugin for Facial Animation

| 属性 | 值 |
|---|---|
| 中文名 | 面部动画系统 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `RigLogicLib` (Runtime), `RigLogicModule` (Runtime), `RigLogicEditor` (Runtime), `RigLogicDeveloper` (Runtime), `RigLogicLibTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-07-20 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic) | |

## 用途

RigLogic 插件是一个专业级的数字人面部动画驱动系统。它的核心作用是解析和执行一种称为 “DNA” 的专有数据格式，该格式包含了驱动角色骨骼（尤其是面部）所需的所有数据，如骨骼定义、关节拓扑、动画行为（包括传统行为、RBF 求解器和机器学习行为）以及几何数据。插件的主要目的是为 AAA 级游戏、虚拟人和电影预览提供高性能、高保真的面部和身体动画解决方案，能够直接从商业 DCC 工具（如 Maya， 通过 Metahuman 技术）导出的资产驱动角色。

## 使用场景

-   **创建逼真的数字人或虚拟偶像**：使用从外部 DCC 工具（如 Maya）生成并转换为 DNA 格式的角色资产，通过 `URigLogicComponent` 驱动其复杂的面部表情和骨骼动画。
-   **集成 MetaHuman 角色**：直接使用 MetaHuman Creator 生成的角色，因为 MetaHuman 的内部动画驱动就基于 RigLogic 系统。
-   **高性能动画计算**：需要在运行时进行大量骨骼混合、RBF 求解和神经网络推断以生成自然面部动画的场景。
-   **需要 LOD 的动画系统**：RigLogic 支持完整的 LOD 机制，可以在不同细节级别下调整动画计算的复杂度，优化性能。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetDNA` | 为组件设置要使用的 DNA 资产，这是驱动动画的第一步。 | `URigLogicComponent` |
| `UpdateFace` | 根据当前的控制值（GUI 或 Raw）计算并应用面部动画到骨骼网格体。 | `URigLogicComponent` |
| `UpdateJoints` | 根据当前的控制值计算所有相关关节的变换（平移、旋转、缩放）。 | `URigLogicComponent` |
| `SetControlValue` / `GetControlValue` | 设置或获取一个具体的 GUI 控制器（如 “BrowDownL”）的浮点数值。 | `URigLogicComponent` |
| `SetControlValues` | 批量设置多个 GUI 控制器的值。 | `URigLogicComponent` |
| `GetJointIndexByName` | 通过关节名称查询其在骨骼层级中的索引。 | `URigLogicComponent` |
| `SetLOD` | 设置当前用于计算动画的细节级别（LOD）。 | `URigLogicComponent` |

### 使用示例（蓝图描述）
1.  **初始化角色**：在角色的蓝图中，添加一个 `URigLogicComponent` 组件。在角色初始化时（如 `BeginPlay`），调用 `SetDNA` 节点并传入加载好的 `UDNAAsset` 资产。
2.  **驱动动画**：在事件图表中，例如在 `Tick` 或一个自定义的动画更新事件中，首先根据玩家的输入或游戏逻辑调用 `SetControlValue` 设置眼睛、嘴巴、眉毛等控制器的值。然后调用 `UpdateFace` 或 `UpdateJoints` 节点来计算并应用动画。
3.  **查询关节信息**：如果需要对某个特定关节进行操作（例如附加一个粒子效果），可以使用 `GetJointIndexByName` 先获取其索引。

## C++ 用法

### 头文件引入

```cpp
#include “RigLogicModule.h”
// 通常，更直接的访问是通过 RigLogicComponent
#include “Components/RigLogicComponent.h”
```

### 基本用法
以下是一个在 C++ Actor 中创建和驱动 RigLogic 组件的基本示例。

```cpp
// MyRigLogicActor.h
#pragma once
#include “GameFramework/Actor.h”
#include “MyRigLogicActor.generated.h”

class URigLogicComponent;

UCLASS()
class AMyRigLogicActor : public AActor
{
    GENERATED_BODY()

public:
    AMyRigLogicActor();

protected:
    virtual void BeginPlay() override;

    virtual void Tick(float DeltaTime) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = “Animation”)
    URigLogicComponent* RigLogicComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = “Animation”)
    UDNAAsset* DNAAsset;
};
```

```cpp
// MyRigLogicActor.cpp
#include “MyRigLogicActor.h”
#include “Components/RigLogicComponent.h”
#include “DNAAsset.h”

AMyRigLogicActor::AMyRigLogicActor()
{
    PrimaryActorTick.bCanEverTick = true;
    RigLogicComponent = CreateDefaultSubobject<URigLogicComponent>(TEXT(“RigLogic”));
    RootComponent = RigLogicComponent;
}

void AMyRigLogicActor::BeginPlay()
{
    Super::BeginPlay();
    if (DNAAsset)
    {
        RigLogicComponent->SetDNA(DNAAsset);
    }
}

void AMyRigLogicActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 示例：根据一些游戏逻辑设置控制值
    float BrowDownValue = FMath::Sin(GetWorld()->GetTimeSeconds()) * 0.5f + 0.5f;
    RigLogicComponent->SetControlValue(TEXT(“BrowDownL”), BrowDownValue);
    RigLogicComponent->SetControlValue(TEXT(“BrowDownR”), BrowDownValue);

    // 执行动画计算
    RigLogicComponent->UpdateJoints();
    RigLogicComponent->UpdateFace();
}
```

### 进阶用法
RigLogic 提供了更底层的 `RigLogic::RigInstance` 访问，用于需要更精细控制（如自定义内存分配、LOD 策略）的场景。

```cpp
#include “RigLogic/RigInstance.h”
#include “DNAReader.h”

// 假设已有一个有效的 dna::Reader* (来自 DNA 资产)
const dna::Reader* DnaReader = ...; // 从 UDNAAsset 获取
const rl4::Configuration Config = ...; // 根据需求配置

// 1. 创建 RigLogic 实例
rl4::RigLogic* RigLogic = rl4::RigLogic::create(DnaReader, Config);

// 2. 创建一个 Rig 实例 (代表一个具体角色)
rl4::RigInstance* RigInstance = RigLogic->createInstance();

// 3. 设置输入控制值
const std::uint16_t ControlIndex = RigLogic->getControlIndexByName(“BrowDownL”); // 伪代码，需自行查找
RigInstance->setControlValue(ControlIndex, 1.0f);

// 4. 计算所有行为 (Joints, ML, RBF 等)
RigLogic->calculate(RigInstance);

// 5. 从实例获取结果 (例如关节变换)
ConstArrayView<float> JointValues = RigInstance->getJointValues();
// ... 处理 JointValues ...

// 6. 清理
RigLogic->destroy(RigInstance);
rl4::RigLogic::destroy(RigLogic);
```

## Demo 示例

这是一个最小的可编译 Actor 示例，展示如何通过组件使用 RigLogic。

```cpp
// RigLogicDemoActor.h
#pragma once
#include “GameFramework/Actor.h”
#include “RigLogicDemoActor.generated.h”

class URigLogicComponent;
class UDNAAsset;

UCLASS()
class ARigLogicDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ARigLogicDemoActor();

    UPROPERTY(VisibleAnywhere)
    URigLogicComponent* RigLogicComp;

    UPROPERTY(EditAnywhere, Category = “DNA”)
    UDNAAsset* MyDNAAsset;

protected:
    virtual void BeginPlay() override;
};
```

```cpp
// RigLogicDemoActor.cpp
#include “RigLogicDemoActor.h”
#include “Components/RigLogicComponent.h”

ARigLogicDemoActor::ARigLogicDemoActor()
{
    RigLogicComp = CreateDefaultSubobject<URigLogicComponent>(TEXT(“RigLogicComponent”));
}

void ARigLogicDemoActor::BeginPlay()
{
    Super::BeginPlay();
    if (MyDNAAsset)
    {
        RigLogicComp->SetDNA(MyDNAAsset);
        // DNA 加载后，可以立即进行一次计算来应用中性姿势
        RigLogicComp->UpdateJoints();
    }
}
```

## 模块依赖

要使用 RigLogic 插件，你的模块需要依赖 `RigLogicModule`。

| 模块 | 用途 |
|---|---|
| `SkeletalMeshUtilitiesCommon` | 提供骨骼网格体相关的通用工具函数。 |
| `RHI` | 渲染硬件接口，用于底层图形资源访问（可能用于 GPU 计算）。 |
| `RenderCore` | 渲染核心模块，提供渲染线程相关的基础结构。 |
| `AssetRegistry` | 资产注册表，用于管理和发现资产。 |
| `UnrealEd`, `EditorFramework` | 仅编辑器相关，用于插件的编辑器功能（如资产预览、自定义编辑器）。 |
| `MessageLog` | 用于在编辑器中显示日志和警告信息。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `de0806c7` | Fix RigLogic NaN output from TwistSwing/RBF when ControlAttributeCurves overwrites driver-joint quat | 修复当 ControlAttributeCurves 覆盖驱动关节四元数时，TwistSwing/RBF 产生 NaN 输出的问题 |
| 2026-05-13 | `52da7ee0` | Fix quaternion joints evaluator test in case no rotation support is compiled in for the zyx sequence | 修复在未编译 zyx 旋转顺序支持时四元数关节求值器测试失败的问题 |
| 2026-05-13 | `27f94d1b` | Fix RigLogic ML Joints initialization of rotation adapter in the absence of coordinate system conver | 修复在没有坐标系转换的情况下 ML Joints 旋转适配器的初始化问题 |
| 2026-05-13 | `4b5d4e7d` | Notify dependent AnimNode_RigLogic instances when RigRuntimeContext is reinitialized due to config c | 当配置更改导致 RigRuntimeContext 重新初始化时，通知依赖的 AnimNode_RigLogic 实例 |
| 2026-05-12 | `9006d42c` | Implement identical integration tests for all three RigLogic runtime integrations, AnimNode RigLogic | 为三种 RigLogic 运行时集成（AnimNode RigLogic...）实现相同的集成测试 |

### 维护评价

- **活跃维护**：该插件最近一次更新（修复 NaN 问题）发生在 2026 年 5 月，表明它仍在积极维护中，并专注于修复运行时关键 Bug 和提升稳定性。
- **成熟度高**：插件创建于 2020 年，经过多年发展，已成为 Unreal Engine 中驱动 MetaHuman 等数字人角色的核心技术，代码量庞大且经过严格测试。
- **无已知重大问题**：近期提交历史主要是 Bug 修复和测试完善，没有迹象表明插件已废弃或存在重大架构缺陷。
- **推荐使用**：如果你的项目需要驱动高保真、基于 DNA 数据的数字人面部或身体动画，RigLogic 是官方推荐且成熟的选择。对于简单的卡通角色，可能过于复杂。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic)
- [官方文档]() (插件内部未提供 DocsURL)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic/Source/RigLogicLibTest)