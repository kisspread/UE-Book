# Cloner Effector

> Niagara based cloner system with various layouts and effector affecting each clone instances

| 属性 | 值 |
|---|---|
| 中文名 | 克隆器与效应器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（Niagara 系统、材质、纹理等） |
| 模块 | `ClonerEffector` (Runtime), `ClonerEffectorEditor` (Runtime), `ClonerEffectorMeshBuilder` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ClonerEffector) | |

## 用途

ClonerEffector 是 Motion Design（运动设计）工作流的核心插件，基于 Niagara 粒子系统构建了一套**高性能网格体克隆系统**。它解决的核心问题是：在虚拟制作场景中快速创建大量重复网格体实例的排列，并通过效应器（Effector）实时控制每个克隆体的变换、颜色和物理行为。

与传统的实例化静态网格体（ISM）或 Niagara 手动搭建不同，该插件提供了：
- **预置布局系统**：Grid、Circle、Cylinder、Sphere、Honeycomb、Line、Spline、Mesh 等数十种排列方式
- **效应器系统**：通过 6 种形状（球体/平面/盒子/无界/径向/环面）和 7 种模式（默认/目标/程序化/推动/步进/裁剪/取消）精确控制克隆体行为
- **扩展架构**：通过可插拔扩展（Extension）为克隆器添加约束、位移、纹理、碰撞、生命周期等效果
- **物理模拟**：支持克隆体间的粒子碰撞、表面碰撞、涡旋力、引力等物理行为
- **Niagara 数据通道**：通过 Niagara Data Channel 将效应器数据高效传递给粒子系统

该插件是从 Experimental 文件夹迁移到 VirtualProduction 的最新 Motion Design 子系统之一。

## 使用场景

- 你在制作虚拟发布会舞台，需要阵列排列大量灯光/屏幕/装饰物体 → 使用 Cloner + Grid/Circle/Honeycomb 布局
- 你需要创建沿样条曲线排列的建筑元素 → 使用 Cloner + Spline 布局
- 你需要克隆体随鼠标移动产生波浪/排斥/吸附效果 → 链接 Effector + Push/Target/Procedural 模式
- 你需要克隆体受到重力、涡旋力、噪声力等物理影响 → 使用 Effector + Force 效果
- 你需要基于纹理图案约束克隆体的出现位置 → 使用 Constraint 扩展 + 纹理约束
- 你需要克隆体随时间渐变消失并缩放 → 使用 Lifetime 扩展
- 你需要克隆体间的碰撞效果 → 使用 Collision 扩展
- 你需要在 Mesh 表面采样点上放置克隆体 → 使用 Mesh 布局（支持顶点/三角面/Socket/骨骼/Section 采样）

## 蓝图用法

### 核心节点 — 克隆器组件（UCEClonerComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetEnabled` / `GetEnabled` | 启用/禁用克隆器 | `UCEClonerComponent` |
| `SetSeed` / `GetSeed` | 设置随机种子 | `UCEClonerComponent` |
| `SetColor` / `GetColor` | 设置克隆体全局颜色 | `UCEClonerComponent` |
| `SetGlobalScale` / `GetGlobalScale` | 设置全局缩放 | `UCEClonerComponent` |
| `SetGlobalRotation` / `GetGlobalRotation` | 设置全局旋转 | `UCEClonerComponent` |
| `SetLayoutName` / `SetLayoutClass` | 切换布局（Grid/Circle/Cylinder 等） | `UCEClonerComponent` |
| `GetActiveLayout` | 获取当前活动布局对象 | `UCEClonerComponent` |
| `GetExtension` | 获取指定类型的扩展实例 | `UCEClonerComponent` |
| `GetActiveExtensions` | 获取所有活动扩展 | `UCEClonerComponent` |
| `GetMeshCount` | 获取当前处理的网格体数量 | `UCEClonerComponent` |
| `GetAttachmentCount` | 获取根附着体数量 | `UCEClonerComponent` |

### 核心节点 — 效应器组件（UCEEffectorComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetEnabled` / `GetEnabled` | 启用/禁用效应器 | `UCEEffectorComponent` |
| `SetMagnitude` / `GetMagnitude` | 设置效应器影响强度 (0-1) | `UCEEffectorComponent` |
| `SetColor` / `GetColor` | 设置效应器颜色 | `UCEEffectorComponent` |
| `SetTypeName` / `SetTypeClass` | 设置效应器形状类型 | `UCEEffectorComponent` |
| `SetModeName` / `SetModeClass` | 设置效应器行为模式 | `UCEEffectorComponent` |
| `GetActiveType` | 获取当前活动的形状类型 | `UCEEffectorComponent` |
| `GetActiveMode` | 获取当前活动的行为模式 | `UCEEffectorComponent` |
| `GetActiveEffects` | 获取所有活动效果 | `UCEEffectorComponent` |

### 核心节点 — 效应器链接与管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LinkEffector` | 将效应器 Actor 链接到克隆器 | `UCEClonerEffectorExtension` |
| `UnlinkEffector` | 断开效应器与克隆器的链接 | `UCEClonerEffectorExtension` |
| `IsEffectorLinked` | 检查效应器是否已链接 | `UCEClonerEffectorExtension` |
| `CreateLinkedEffector` | 创建并链接新效应器（编辑器） | `UCEClonerEffectorExtension` |

### 核心节点 — 布局参数控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCountX/Y/Z` | 设置 Grid 布局三轴数量 | `UCEClonerGridLayout` |
| `SetSpacingX/Y/Z` | 设置 Grid 布局三轴间距 | `UCEClonerGridLayout` |
| `SetCount` / `SetRadius` | 设置 Circle/Sphere 布局数量和半径 | `UCEClonerCircleLayout` / `UCEClonerSphereUniformLayout` |
| `SetBaseCount` / `SetHeight` | 设置 Cylinder 布局底面数量和高度 | `UCEClonerCylinderLayout` |
| `SetCount` / `SetSplineActor` | 设置 Spline 布局数量和样条 Actor | `UCEClonerSplineLayout` |
| `SetCount` / `SetSampleActor` | 设置 Mesh 布局数量和采样 Actor | `UCEClonerMeshLayout` |

### 核心节点 — 工具库

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetClonerLayoutClasses` | 获取所有可用布局类 | `UCEClonerLibrary` |
| `GetClonerLayoutNames` | 获取所有布局名称 | `UCEClonerLibrary` |
| `GetClonerExtensionClasses` | 获取所有克隆器扩展类 | `UCEClonerLibrary` |
| `SetClonerLayoutByClass` | 通过类设置克隆器布局（异步等待） | `UCEClonerLibrary` |
| `SetClonerLayoutByName` | 通过名称设置克隆器布局（异步等待） | `UCEClonerLibrary` |
| `GetEffectorTypeClasses` | 获取所有效应器形状类 | `CEEffectorLibrary` |
| `GetEffectorModeClasses` | 获取所有效应器模式类 | `CEEffectorLibrary` |
| `GetEffectorEffectClasses` | 获取所有效应器效果类 | `CEEffectorLibrary` |

### 使用示例（蓝图描述）

**创建 Grid 克隆器并修改布局参数**：
1. 放置 `ACEClonerActor` 到场景
2. 从组件树获取 `UCEClonerComponent` 引用
3. 调用 `SetLayoutName("Grid")` 设置 Grid 布局
4. 调用 `SetCountX(5)`, `SetCountY(5)`, `SetSpacingX(120)` 设置参数
5. 在克隆器下挂载需要克隆的静态网格体 Actor

**链接 Effector 实现推动效果**：
1. 放置 `ACEEffectorActor` 到场景中克隆器附近
2. 通过 `UCEClonerEffectorExtension` 的 `LinkEffector` 链接效应器
3. 在效应器上调用 `SetTypeName("Sphere")` 设置球形区域
4. 调用 `SetModeName("Push")` 设置推动模式
5. 移动效应器时克隆体会被推动

**通过 Texture 约束克隆体分布**：
1. 克隆器组件获取 `UCEClonerConstraintExtension`
2. 调用 `SetConstraint(Texture)` 启用纹理约束
3. 调用 `SetTextureAsset(YourTexture)` 设置纹理
4. 调用 `SetTextureThreshold(0.5)` 设置阈值
5. 仅亮度超过阈值位置的克隆体会显示

## C++ 用法

### 头文件引入

```cpp
#include "Cloner/CEClonerComponent.h"
#include "Cloner/CEClonerActor.h"
#include "Cloner/Layouts/CEClonerLayoutBase.h"
#include "Cloner/Extensions/CEClonerExtensionBase.h"
#include "Effector/CEEffectorComponent.h"
#include "Effector/CEEffectorActor.h"
#include "Subsystems/CEClonerSubsystem.h"
#include "Subsystems/CEEffectorSubsystem.h"
#include "Utilities/CEClonerLibrary.h"
#include "Utilities/CEEffectorLibrary.h"
```

### 基本用法

```cpp
// 获取克隆器子系统单例
UCEClonerSubsystem* ClonerSubsystem = UCEClonerSubsystem::Get();

// 创建一个带附着体的克隆器
TSet<AActor*> ActorsToClone;
ActorsToClone.Add(MyStaticMeshActor);
UCEClonerComponent* Cloner = ClonerSubsystem->CreateClonerWithActors(
    GetWorld(), ActorsToClone, 
    UCEClonerSubsystem::ECEClonerActionFlags::ShouldSelect
);

// 切换布局并设置参数
Cloner->SetLayoutName(TEXT("Grid"));
// 获取当前布局并修改参数
if (UCEClonerGridLayout* GridLayout = Cast<UCEClonerGridLayout>(Cloner->GetActiveLayout()))
{
    GridLayout->SetCountX(5);
    GridLayout->SetCountY(3);
    GridLayout->SetSpacingX(150.f);
    GridLayout->SetSpacingY(150.f);
}

// 启用/禁用克隆器
Cloner->SetEnabled(true);
Cloner->SetSeed(42);
Cloner->SetColor(FLinearColor::Green);
```

**来源**：`Public/Cloner/CEClonerComponent.h`, `Public/Subsystems/CEClonerSubsystem.h`

### 进阶用法

```cpp
// === 效应器系统 ===

// 获取效应器子系统
UCEEffectorSubsystem* EffectorSubsystem = UCEEffectorSubsystem::Get();

// 创建并配置效应器
UCEEffectorComponent* Effector = NewObject<UCEEffectorComponent>(MyActor);
Effector->SetTypeName(TEXT("Sphere"));
Effector->SetModeName(TEXT("Default"));
Effector->SetMagnitude(0.8f);
Effector->SetColor(FLinearColor::Red);

// 获取效应器上的 Force 效果并配置涡旋力
if (UCEEffectorForceEffect* ForceEffect = Effector->GetExtension<UCEEffectorForceEffect>())
{
    ForceEffect->SetForcesEnabled(true);
    ForceEffect->SetVortexForceEnabled(true);
    ForceEffect->SetVortexForceAmount(500.f);
    ForceEffect->SetVortexForceAxis(FVector::ZAxisVector);
}

// === 克隆器扩展系统 ===

// 获取碰撞扩展并启用粒子碰撞
if (UCEClonerCollisionExtension* CollisionExt = Cloner->GetExtension<UCEClonerCollisionExtension>())
{
    CollisionExt->SetParticleCollisionEnabled(true);
    CollisionExt->SetCollisionGridResolution(64);
    CollisionExt->SetCollisionGridSize(FVector(10000.f));
}

// 获取约束扩展并使用纹理约束
if (UCEClonerConstraintExtension* ConstraintExt = Cloner->GetExtension<UCEClonerConstraintExtension>())
{
    ConstraintExt->SetConstraint(ECEClonerGridConstraint::Texture);
    ConstraintExt->SetTextureAsset(MyTexture);
    ConstraintExt->SetTextureThreshold(0.3f);
}

// === 通过 Data Channel 监听效应器变化 ===
UCEEffectorSubsystem::OnEffectorIdentifierChanged().AddLambda(
    [](UCEEffectorComponent* InEffector, int32 OldId, int32 NewId)
    {
        UE_LOG(LogTemp, Log, TEXT("Effector %s identifier changed: %d -> %d"),
            *InEffector->GetName(), OldId, NewId);
    });

// === 将克隆器仿真转换为静态网格体 ===
ClonerSubsystem->ConvertCloners(
    TSet<UCEClonerComponent*>{Cloner},
    ECEClonerMeshConversion::StaticMesh
);

// === 注册自定义布局 ===
ClonerSubsystem->RegisterLayoutClass(UCEClonerMyCustomLayout::StaticClass());

// === 注册自定义附着树行为 ===
TFunction<TSharedRef<ICEClonerAttachmentTreeBehavior>()> Creator = []()
{
    return MakeShared<FMyCustomAttachmentBehavior>();
};
ClonerSubsystem->RegisterAttachmentTreeBehavior(TEXT("MyCustomBehavior"), Creator);
```

**来源**：`Public/Cloner/Extensions/CEClonerCollisionExtension.h`, `Public/Effector/Effects/CEEffectorForceEffect.h`, `Public/CEClonerEffectorShared.h`

## Demo 示例

```cpp
// ClonerDemoActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "ClonerDemoActor.generated.h"

class UCEClonerComponent;
class ACEEffectorActor;
class UCEClonerEffectorExtension;

UCLASS()
class AClonerDemoActor : public AActor
{
    GENERATED_BODY()
public:
    AClonerDemoActor();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

protected:
    // 克隆器组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    UCEClonerComponent* ClonerComp;

    // 效应器 Actor
    UPROPERTY()
    ACEEffectorActor* EffectorActor;
};
```

```cpp
// ClonerDemoActor.cpp
#include "ClonerDemoActor.h"
#include "Cloner/CEClonerComponent.h"
#include "Cloner/CEClonerActor.h"
#include "Cloner/Layouts/CEClonerGridLayout.h"
#include "Cloner/Layouts/CEClonerCircleLayout.h"
#include "Cloner/Extensions/CEClonerEffectorExtension.h"
#include "Cloner/Extensions/CEClonerMeshRendererExtension.h"
#include "Cloner/Extensions/CEClonerRangeExtension.h"
#include "Cloner/Extensions/CEClonerLifetimeExtension.h"
#include "Effector/CEEffectorActor.h"
#include "Effector/CEEffectorComponent.h"
#include "Effector/Effects/CEEffectorForceEffect.h"
#include "Subsystems/CEClonerSubsystem.h"

AClonerDemoActor::AClonerDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建克隆器组件
    ClonerComp = CreateDefaultSubobject<UCEClonerComponent>(TEXT("ClonerComp"));
    RootComponent = ClonerComp;
}

void AClonerDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 设置 Grid 布局
    ClonerComp->SetLayoutName(TEXT("Grid"));
    if (UCEClonerGridLayout* GridLayout = ClonerComp->GetActiveLayout<UCEClonerGridLayout>())
    {
        GridLayout->SetCountX(4);
        GridLayout->SetCountY(4);
        GridLayout->SetCountZ(1);
        GridLayout->SetSpacingX(120.f);
        GridLayout->SetSpacingY(120.f);
    }

    // 设置随机范围
    if (UCEClonerRangeExtension* RangeExt = ClonerComp->GetExtension<UCEClonerRangeExtension>())
    {
        RangeExt->SetRangeEnabled(true);
        RangeExt->SetRangeOffsetMax(FVector(10.f, 10.f, 5.f));
        RangeExt->SetRangeRotationMax(FRotator(0.f, 15.f, 0.f));
    }

    // 设置生命周期
    if (UCEClonerLifetimeExtension* LifetimeExt = ClonerComp->GetExtension<UCEClonerLifetimeExtension>())
    {
        LifetimeExt->SetLifetimeEnabled(true);
        LifetimeExt->SetLifetimeMin(1.f);
        LifetimeExt->SetLifetimeMax(3.f);
    }

    // 通过子系统创建链接的效应器
    UCEClonerSubsystem* Subsystem = UCEClonerSubsystem::Get();
    TArray<UCEEffectorComponent*> Effectors = Subsystem->CreateLinkedEffectors(
        {ClonerComp},
        UCEClonerSubsystem::ECEClonerActionFlags::ShouldSelect,
        [](UCEEffectorComponent* Effector)
        {
            Effector->SetMagnitude(1.f);
            Effector->SetTypeName(TEXT("Sphere"));
            Effector->SetModeName(TEXT("Push"));
        }
    );

    // 配置效应器的力效果
    if (Effectors.Num() > 0)
    {
        if (UCEEffectorForceEffect* ForceEffect = Effectors[0]->GetExtension<UCEEffectorForceEffect>())
        {
            ForceEffect->SetForcesEnabled(true);
            ForceEffect->SetCurlNoiseForceEnabled(true);
            ForceEffect->SetCurlNoiseForceStrength(200.f);
        }
    }
}

void AClonerDemoActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // 移动效应器以实时影响克隆体
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Niagara` | Niagara 粒子系统，所有布局和效应器的底层驱动 |
| `GeometryCore` | 动态网格体操作，用于克隆器仿真转 Static/Dynamic Mesh |
| `MeshConversion` | 网格体格式转换 |
| `GeometryFramework` | DynamicMesh Actor 支持 |
| `DataDrivenShaderPlatformInfo` | 着色器平台信息查询 |

> 常见依赖（Core, CoreUObject, Engine, Slate, SlateCore 等）已省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `6a7d961a` | Motion Design: fix cloner MIDs getting gc'd on save, causing the mesh renderer to have an array of d | 修复克隆器材质实例在保存时被 GC 回收导致网格渲染器数组损坏的问题 |
| 2026-05-12 | `9d568373` | Motion Design: fixed warning logs when cloner asset isn't generated yet and failing to find a data i | 修复克隆器资产未生成时的警告日志和数据接口查找失败问题 |
| 2026-05-12 | `adfb4114` | Motion Design: fixed cloners spawning default actors while in async loading thread. Instead, these a | 修复克隆器在异步加载线程中生成默认 Actor 的线程安全问题，改为延迟生成 |
| 2026-05-12 | `ae187efa` | Motion Design: fixed motion design scene tree returning potentially null actors. Also added null che | 修复场景树可能返回空 Actor 的问题，增加空指针检查 |

### 维护评价

**活跃维护** — 该插件状态良好，推荐使用。

- **创建时间**：2025 年 5 月从 Experimental 迁移到 VirtualProduction，是 Motion Design 工具链的重要组成部分
- **更新频率**：近期（2026 年 5 月）有密集的 bug 修复更新，包括材质 GC 保护、线程安全、空指针保护等稳定性改进
- **代码质量**：架构设计成熟，采用组件+扩展+子系统的分层模式，支持自定义布局和效应器扩展
- **已知限制**：
  - `IsBetaVersion`/`IsExperimentalVersion` 未明确设置，但从 Experimental 迁移背景看仍属实验性功能
  - 碰撞系统依赖距离场，需要网格体有足够的距离场分辨率
  - 克隆器转 Static Mesh 是重量级操作（`ConvertToStaticMesh` 标注为 heavy operation）
- **推荐度**：✅ 推荐在 Motion Design / Virtual Production 项目中使用，适合需要大量重复网格体排列和动态效果的场景

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ClonerEffector)
- [官方文档]()（暂无）