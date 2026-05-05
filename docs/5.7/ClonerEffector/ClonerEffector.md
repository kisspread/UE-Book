# Cloners and Effectors

> Niagara based cloner system with various layouts and effector affecting each clone instances

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Niagara 系统资产、材质模板） |
| 模块 | `ClonerEffector` (Runtime), `ClonerEffectorEditor` (Runtime), `ClonerEffectorMeshBuilder` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-06 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/ClonerEffector) | |

## 用途

ClonerEffector 是一个基于 Niagara 粒子系统的**大规模实例克隆与效果控制插件**，专为虚拟制片和 Motion Design 场景设计。它解决的核心问题是：**如何高效地将一个或多个 Actor 的网格体克隆成成百上千个实例，并通过 Effector（效应器）对这些实例施加空间变换、剔除、延迟等动态效果**。

与手动放置 Actor 或使用 HISM（层级静态网格实例）不同，ClonerEffector 提供了：

- **声明式布局系统**：通过预设的布局（线性、网格、球形、样条线、网格表面采样等）自动排列克隆实例
- **Effector 效应器系统**：通过空间形状（盒体、球体、环面、径向等）定义影响区域，配合模式（偏移、推动、剔除、步进、目标跟踪等）和效果（延迟弹簧）对克隆实例施加变换
- **Niagara 驱动**：底层使用 Niagara 粒子系统实现高性能渲染，支持 GPU 加速
- **附件树系统**：自动将附加到 Cloner Actor 的子 Actor 层级烘焙为网格并合并，作为克隆源

本质上，这是 Cinema 4D 的 MoGraph 克隆器/效应器系统在 UE5 中的等价物。

## 使用场景

- 你在制作 Motion Design 动态图形 → 用 Cloner 创建大量几何体排列，用 Effector 控制动画
- 你需要在虚拟制片场景中快速填充大量重复元素（椅子、灯具、装饰物）→ 用 Cloner 的 Grid/Line 布局
- 你需要让一组物体沿样条线排列 → 用 Spline 布局
- 你需要让物体在球面上均匀分布 → 用 SphereUniform 布局
- 你需要让物体跟随某个目标移动并产生延迟弹簧效果 → 用 Effector 的 Target 模式 + Delay 效果
- 你需要根据空间区域隐藏或移除部分克隆实例 → 用 Effector 的 Cull 模式

## 蓝图用法

### 核心节点 — Cloner 布局管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetClonerLayoutClasses` | 获取所有可用的布局类 | `UCEClonerLibrary` |
| `GetClonerLayoutNames` | 获取所有布局名称 | `UCEClonerLibrary` |
| `GetClonerLayoutName` | 从布局类获取布局名称 | `UCEClonerLibrary` |
| `GetClonerLayoutClass` | 从布局名称获取布局类 | `UCEClonerLibrary` |
| `SetClonerLayoutByClass` | 通过类设置 Cloner 的活跃布局（异步等待加载完成） | `UCEClonerLibrary` |
| `SetClonerLayoutByName` | 通过名称设置 Cloner 的活跃布局（异步等待加载完成） | `UCEClonerLibrary` |
| `GetClonerExtensionClasses` | 获取所有可用的扩展类 | `UCEClonerLibrary` |

### 核心节点 — Effector 管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetEffectorModeClasses` | 获取所有可用的模式类 | `UCEffectorLibrary` |
| `GetEffectorTypeClasses` | 获取所有可用的类型（形状）类 | `UCEffectorLibrary` |
| `GetEffectorTypeNames` | 获取所有类型名称 | `UCEffectorLibrary` |
| `GetEffectorEffectClasses` | 获取所有可用的效果类 | `UCEffectorLibrary` |

### 核心节点 — Cloner 扩展

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetProgress` / `GetProgress` | 控制克隆实例的可见进度（0~1） | `UCEClonerProgressExtension` |
| `SetInvertProgress` / `GetInvertProgress` | 反转进度行为 | `UCEClonerProgressExtension` |
| `SetDeltaStepEnabled` | 启用/禁用增量步进 | `UCEClonerStepExtension` |
| `SetDeltaStepPosition` / `SetDeltaStepRotation` / `SetDeltaStepScale` | 设置每个克隆实例间的增量变换 | `UCEClonerStepExtension` |
| `SetLifetimeEnabled` | 启用克隆实例生命周期 | `UCEClonerLifetimeExtension` |
| `SetLifetimeMin` / `SetLifetimeMax` | 设置生命周期范围 | `UCEClonerLifetimeExtension` |
| `LinkEffector` / `UnlinkEffector` | 链接/断开 Effector Actor | `UCEClonerEffectorExtension` |
| `IsEffectorLinked` | 检查 Effector 是否已链接 | `UCEClonerEffectorExtension` |
| `GetEffectorCount` | 获取已链接的 Effector 数量 | `UCEClonerEffectorExtension` |

### 核心节点 — 布局参数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCount` / `GetCount` | 设置克隆实例数量 | `UCEClonerLineLayout` / `UCEClonerGrid3DLayout` 等 |
| `SetSpacing` / `GetSpacing` | 设置实例间距 | `UCEClonerLineLayout` |
| `SetAxis` / `GetAxis` | 设置排列轴向 | `UCEClonerLineLayout` |
| `SetRadius` / `GetRadius` | 设置球形半径 | `UCEClonerSphereUniformLayout` / `UCEClonerSphereRandomLayout` |
| `SetSplineActor` / `GetSplineActor` | 设置样条线 Actor | `UCEClonerSplineLayout` |
| `SetSampleActor` / `GetSampleActor` | 设置网格采样 Actor | `UCEClonerMeshLayout` |
| `SetOrientMesh` / `GetOrientMesh` | 设置是否朝向法线方向 | `UCEClonerSplineLayout` / `UCEClonerSphereUniformLayout` |

### 核心节点 — Effector 类型（形状）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetInnerExtent` / `SetOuterExtent` | 设置盒体内部/外部范围 | `UCEEffectorBoxType` |
| `SetInnerRadius` / `SetOuterRadius` | 设置球体内部/外部半径 | `UCEEffectorSphereType` |
| `SetPlaneSpacing` | 设置平面影响间距 | `UCEEffectorPlaneType` |
| `SetRadialAngle` / `SetRadialMinRadius` / `SetRadialMaxRadius` | 设置径向角度和半径范围 | `UCEEffectorRadialType` |
| `SetTorusRadius` / `SetTorusInnerRadius` / `SetTorusOuterRadius` | 设置环面参数 | `UCEEffectorTorusType` |
| `SetInvertType` / `GetInvertType` | 反转影响区域（影响外部而非内部） | `UCEEffectorBoundType` |
| `SetEasing` / `GetEasing` | 设置权重缓动函数 | `UCEEffectorBoundType` |

### 核心节点 — Effector 模式（行为）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetOffset` / `SetRotation` / `SetScale` | 设置偏移变换 | `UCEEffectorOffsetMode` |
| `SetPushDirection` / `SetPushStrength` | 设置推动方向和强度 | `UCEEffectorPushMode` |
| `SetBehavior` / `SetScale` | 设置剔除行为（Kill/Hide）和缩放 | `UCEEffectorCullMode` |
| `SetStepPosition` / `SetStepRotation` / `SetStepScale` | 设置步进插值变换 | `UCEEffectorStepMode` |
| `SetTargetActor` / `GetTargetActor` | 设置目标跟踪 Actor | `UCEEffectorTargetMode` |
| `SetPattern` / `SetFrequency` / `SetPan` | 设置程序化噪声模式 | `UCEEffectorProceduralMode` |

### 核心节点 — Effector 效果

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetDelayEnabled` | 启用延迟效果 | `UCEEffectorDelayEffect` |
| `SetDelayInDuration` / `SetDelayOutDuration` | 设置延迟进入/退出时长 | `UCEEffectorDelayEffect` |
| `SetDelaySpringFrequency` / `SetDelaySpringFalloff` | 设置弹簧频率和衰减 | `UCEEffectorDelayEffect` |

### 使用示例（蓝图描述）

**创建线性克隆并用 Effector 控制：**

1. 在场景中放置一个 Actor，添加 `CEClonerComponent`
2. ClonerComponent 默认使用 Line 布局，设置 `Count=20`、`Spacing=150`
3. 将要克隆的静态网格 Actor 作为 Cloner Actor 的子级附加
4. 在场景中放置另一个 Actor，添加 `CEEffectorComponent`
5. 在 Cloner 的 Effector 扩展中调用 `LinkEffector`，传入 Effector Actor
6. 在 Effector 上设置 Type 为 Sphere（球形影响区域），Mode 为 Offset（偏移模式）
7. 调整 Sphere 的 `OuterRadius` 和 Offset 的 `Position`，观察克隆实例被推动

**使用异步节点切换布局：**

1. 获取 ClonerComponent 引用
2. 调用 `SetClonerLayoutByName`，传入布局名称如 `"SphereUniform"`
3. 通过 Latent 节点的输出引脚获取 `bOutSuccess` 和 `OutLayout`
4. 对返回的 Layout 对象设置参数（如 `SetCount`、`SetRadius`）

## C++ 用法

### 头文件引入

```cpp
#include "Cloner/CEClonerComponent.h"
#include "Cloner/Layouts/CEClonerLineLayout.h"
#include "Cloner/Layouts/CEClonerGrid3DLayout.h"
#include "Cloner/Extensions/CEClonerEffectorExtension.h"
#include "Effector/CEEffectorComponent.h"
#include "Effector/Types/CEEffectorSphereType.h"
#include "Effector/Modes/CEEffectorOffsetMode.h"
#include "Effector/Effects/CEEffectorDelayEffect.h"
#include "Utilities/CEClonerLibrary.h"
#include "Utilities/CEEffectorLibrary.h"
```

### 基本用法 — 获取布局类和设置布局

```cpp
// 获取所有可用的 Cloner 布局类
TSet<TSubclassOf<UCEClonerLayoutBase>> LayoutClasses;
UCEClonerLibrary::GetClonerLayoutClasses(LayoutClasses);

// 从布局名称获取布局类
TSubclassOf<UCEClonerLayoutBase> LineLayoutClass;
UCEClonerLibrary::GetClonerLayoutClass(FName("Line"), LineLayoutClass);

// 获取布局名称
FName LayoutName;
UCEClonerLibrary::GetClonerLayoutName(LineLayoutClass, LayoutName);
// LayoutName == "Line"
```

### 基本用法 — 配置 Effector 类型和模式

```cpp
// 获取所有可用的 Effector 类型
TSet<TSubclassOf<UCEEffectorTypeBase>> TypeClasses;
UCEffectorLibrary::GetEffectorTypeClasses(TypeClasses);

// 获取所有可用的 Effector 模式
TSet<TSubclassOf<UCEEffectorModeBase>> ModeClasses;
UCEffectorLibrary::GetEffectorModeClasses(ModeClasses);

// 获取所有可用的 Effector 效果
TSet<TSubclassOf<UCEEffectorEffectBase>> EffectClasses;
UCEffectorLibrary::GetEffectorEffectClasses(EffectClasses);
```

### 进阶用法 — 通过 C++ 链接 Effector 并配置效果

```cpp
// 假设已有 UCEClonerComponent* ClonerComp 和 AActor* EffectorActor

// 链接 Effector 到 Cloner
UCEClonerEffectorExtension* EffectorExt = ClonerComp->GetExtension<UCEClonerEffectorExtension>();
if (EffectorExt)
{
    EffectorExt->LinkEffector(EffectorActor);
    
    // 检查链接状态
    bool bLinked = EffectorExt->IsEffectorLinked(EffectorActor);
    int32 Count = EffectorExt->GetEffectorCount();
}

// 配置 Effector 的球形影响区域
// UCEEffectorSphereType* SphereType = EffectorComp->GetType<UCEEffectorSphereType>();
// SphereType->SetInnerRadius(100.f);
// SphereType->SetOuterRadius(500.f);
// SphereType->SetEasing(ECEClonerEasing::EaseInOut);
// SphereType->SetInvertType(false);

// 配置 Effector 的偏移模式
// UCEEffectorOffsetMode* OffsetMode = EffectorComp->GetMode<UCEEffectorOffsetMode>();
// OffsetMode->SetOffset(FVector(0.f, 0.f, 200.f));
// OffsetMode->SetRotation(FRotator(0.f, 45.f, 0.f));
// OffsetMode->SetScale(FVector(1.5f));
```

### 进阶用法 — 配置 Cloner 扩展

```cpp
// 设置克隆进度
UCEClonerProgressExtension* ProgressExt = ClonerComp->GetExtension<UCEClonerProgressExtension>();
if (ProgressExt)
{
    ProgressExt->SetProgress(0.75f);  // 75% 的实例可见
    ProgressExt->SetInvertProgress(false);
}

// 设置增量步进
UCEClonerStepExtension* StepExt = ClonerComp->GetExtension<UCEClonerStepExtension>();
if (StepExt)
{
    StepExt->SetDeltaStepEnabled(true);
    StepExt->SetDeltaStepPosition(FVector(0.f, 0.f, 10.f));
    StepExt->SetDeltaStepRotation(FRotator(0.f, 5.f, 0.f));
    StepExt->SetDeltaStepScale(FVector(0.02f, 0.02f, 0.02f));
}

// 设置生命周期
UCEClonerLifetimeExtension* LifetimeExt = ClonerComp->GetExtension<UCEClonerLifetimeExtension>();
if (LifetimeExt)
{
    LifetimeExt->SetLifetimeEnabled(true);
    LifetimeExt->SetLifetimeMin(0.5f);
    LifetimeExt->SetLifetimeMax(2.0f);
    LifetimeExt->SetLifetimeScaleEnabled(true);
}
```

## Demo 示例

### 最小示例 — 创建带 Effector 的线性克隆

```cpp
// ClonerEffectorDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ClonerEffectorDemo.generated.h"

class UCEClonerComponent;
class UCEClonerLineLayout;
class UCEEffectorComponent;

UCLASS()
class AClonerEffectorDemo : public AActor
{
    GENERATED_BODY()

public:
    AClonerEffectorDemo();

    virtual void BeginPlay() override;

    /** Cloner 组件 */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Demo")
    TObjectPtr<UCEClonerComponent> ClonerComponent;

    /** Effector Actor 引用 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Demo")
    TWeakObjectPtr<AActor> EffectorActor;
};
```

```cpp
// ClonerEffectorDemo.cpp
#include "ClonerEffectorDemo.h"
#include "Cloner/CEClonerComponent.h"
#include "Cloner/Layouts/CEClonerLineLayout.h"
#include "Cloner/Extensions/CEClonerEffectorExtension.h"
#include "Cloner/Extensions/CEClonerStepExtension.h"

AClonerEffectorDemo::AClonerEffectorDemo()
{
    ClonerComponent = CreateDefaultSubobject<UCEClonerComponent>(TEXT("Cloner"));
    RootComponent = ClonerComponent;
}

void AClonerEffectorDemo::BeginPlay()
{
    Super::BeginPlay();

    // 配置线性布局
    if (UCEClonerLineLayout* LineLayout = Cast<UCEClonerLineLayout>(
        ClonerComponent->GetActiveLayout()))
    {
        LineLayout->SetCount(15);
        LineLayout->SetSpacing(120.f);
        LineLayout->SetAxis(ECEClonerAxis::X);
    }

    // 链接 Effector
    if (EffectorActor.IsValid())
    {
        if (UCEClonerEffectorExtension* EffectorExt = 
            ClonerComponent->GetExtension<UCEClonerEffectorExtension>())
        {
            EffectorExt->LinkEffector(EffectorActor.Get());
        }
    }

    // 启用增量步进效果
    if (UCEClonerStepExtension* StepExt = 
        ClonerComponent->GetExtension<UCEClonerStepExtension>())
    {
        StepExt->SetDeltaStepEnabled(true);
        StepExt->SetDeltaStepRotation(FRotator(0.f, 10.f, 0.f));
    }
}
```

## 模块依赖

从源码分析，该插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `Niagara` | 底层粒子系统驱动克隆实例渲染 |
| `DynamicMesh` | 动态网格操作，用于烘焙和合并附件网格 |
| `GeometryCore` | 几何体处理核心库 |
| `GeometryFramework` | 几何体框架，UDynamicMesh 支撑 |
| `MeshConversion` | 网格格式转换（StaticMesh ↔ DynamicMesh） |
| `MeshDescription` | 网格描述数据结构 |
| `StaticMeshDescription` | 静态网格描述扩展 |
| `RenderCore` | 渲染核心（材质标志检查） |
| `MotionDesign` | Motion Design 框架集成（可视化器、开发者设置） |

## 维护状态

### 近期更新

```
- 8bde3a35d214 MotionDesign : ClonerEffector - Fixed skipping materials causing simulation to not be up to date with new materials
- e9f41910b466 MotionDesign : ClonerEffector - Added metadata to only refresh children in details view when changed property has the metadata "RefreshPropertyView"
- 62918a4c847d MotionDesign : ClonerEffector - Fixed access violation in ClonerEffector plugin cause a crash - Improved mesh conversion system
```

三条 commit 均为 bug 修复和稳定性改进：修复材质跳过导致模拟不同步的问题、优化 Details 面板刷新逻辑、修复访问违规崩溃并改进网格转换系统。

### 维护评价

- **创建时间**：2024 年 2 月，约 1.5 年历史，属于较新的插件
- **维护状态**：活跃维护中，近期有实质性 bug 修复
- **架构成熟度**：高度模块化，采用扩展（Extension）+ 布局（Layout）+ 类型（Type）+ 模式（Mode）+ 效果（Effect）的组合式架构，扩展性良好
- **已知限制**：
  - `Installed: false`，需要手动在插件列表中启用
  - 依赖 MotionDesign 模块，可能与 Avalon/Motion Design 工具链绑定
  - 底层依赖 Niagara，需要确保项目启用了 Niagara 插件
  - 材质需要设置 Niagara Usage Flag 才能正确渲染
- **推荐程度**：✅ 推荐用于虚拟制片和 Motion Design 场景。对于纯游戏运行时场景，需评估 Niagara 开销

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/ClonerEffector)
- 官方文档（无）