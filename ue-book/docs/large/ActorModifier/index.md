# Actor Modifier

> Actual implementation of modifiers for actors based on ActorModifierCore plugin

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ActorModifier` (Runtime), `ActorModifierEditor` (Editor), `ActorModifierLayout` (Runtime), `ActorModifierRendering` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-08 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/ActorModifier) | |

## 用途

ActorModifier 是 UE5 Motion Design 系统的核心插件之一，基于 [ActorModifierCore](../ActorModifierCore/index.md) 框架，提供了**实际可用的 Actor 修改器（Modifier）实现**。

该插件解决的核心问题是：**如何以声明式、可堆叠的方式对场景中的 Actor 进行布局变换和渲染效果修改**。

与传统的蓝图 Tick 或 C++ 每帧手动更新不同，Modifier 系统提供了：
- **响应式更新**：当 Actor 变换、子节点结构或渲染状态发生变化时自动触发重新计算
- **状态管理**：自动保存/恢复 Actor 的原始 Transform 和可见性状态，避免多个 Modifier 之间的冲突
- **声明式布局**：通过属性驱动，修改属性即可自动重新排列场景

## 模块架构

```
ActorModifier (Runtime)
├── Types              ← 轴向、对齐等基础枚举和结构体
├── Extensions         ← 场景树、变换、渲染状态的监听扩展
├── Shared             ← 跨 Modifier 共享的 Transform/Visibility 状态管理
└── Utilities          ← 边界计算、LookAt 旋转等工具函数

ActorModifierLayout (Runtime)
├── GridArrange        ← 2D 网格排列
├── RadialArrange      ← 环形排列
├── Justify            ← 对齐/分布
├── AlignBetween       ← 加权平均位置
├── SplinePath         ← 沿样条路径移动
├── AutoFollow         ← 自动跟随目标 Actor
└── LookAt             ← 朝向目标 Actor

ActorModifierRendering (Runtime)
└── HoldoutComposite   ← Alpha Holdout 合成渲染

ActorModifierEditor (Editor)
├── Customizations     ← 对齐方式等属性的自定义编辑器 UI
└── Styles             ← 编辑器样式
```

## 类继承关系

```
UActorModifierCoreBase (来自 ActorModifierCore)
├── UActorModifierAttachmentBaseModifier    ← 带子 Actor 追踪的基类
│   ├── UActorModifierArrangeBaseModifier   ← 布局排列基类
│   │   ├── UActorModifierGridArrangeModifier
│   │   ├── UActorModifierRadialArrangeModifier
│   │   └── UActorModifierJustifyModifier
│   ├── UActorModifierAutoFollowModifier
│   ├── UActorModifierLookAtModifier
│   └── UActorModifierHoldoutCompositeModifier
├── UActorModifierAlignBetweenModifier
└── UActorModifierSplinePathModifier
```

## 使用场景

- 你在做 Motion Design（动态图形）项目，需要将一组 Actor 自动排列成网格 → 用 **GridArrange**
- 你需要将物体排成环形（如转盘菜单、仪表盘刻度） → 用 **RadialArrange**
- 你需要沿样条线放置物体（如沿路径排列灯柱） → 用 **SplinePath**
- 你需要一个 Actor 跟随另一个 Actor 的边界位置（如标签跟随物体） → 用 **AutoFollow**
- 你需要 Actor 始终朝向另一个 Actor（如摄像头跟踪） → 用 **LookAt**
- 你需要物体在两个或多个参考 Actor 之间按权重定位 → 用 **AlignBetween**
- 你需要将物体按边界对齐（类似 CSS Flexbox 的 justify） → 用 **Justify**
- 你需要在虚拟制作中创建 holdout 遮罩效果 → 用 **HoldoutComposite**

## 蓝图用法

### 布局 Modifier 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCount` / `GetCount` | 设置网格行列数 | `UActorModifierGridArrangeModifier` |
| `SetSpread` / `GetSpread` | 设置网格间距 | `UActorModifierGridArrangeModifier` |
| `SetStartCorner` | 设置网格起始角 | `UActorModifierGridArrangeModifier` |
| `SetCount` / `GetCount` | 设置环形元素数量 | `UActorModifierRadialArrangeModifier` |
| `SetRings` / `GetRings` | 设置环数 | `UActorModifierRadialArrangeModifier` |
| `SetInnerRadius` | 设置内环半径 | `UActorModifierRadialArrangeModifier` |
| `SetOuterRadius` | 设置外环半径 | `UActorModifierRadialArrangeModifier` |
| `SetStartAngle` / `SetEndAngle` | 设置角度范围 | `UActorModifierRadialArrangeModifier` |
| `SetOrient` | 是否朝向中心 | `UActorModifierRadialArrangeModifier` |
| `SetHorizontalAlignment` | 水平对齐方式 | `UActorModifierJustifyModifier` |
| `SetVerticalAlignment` | 垂直对齐方式 | `UActorModifierJustifyModifier` |
| `SetHorizontalAnchor` | 水平锚点偏移 | `UActorModifierJustifyModifier` |

### 跟踪/朝向 Modifier 节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetReferenceActor` | 设置参考 Actor | `UActorModifierAutoFollowModifier` |
| `SetFollowedAxis` | 设置跟随轴向 | `UActorModifierAutoFollowModifier` |
| `SetProgress` | 设置跟随进度 (0-100%) | `UActorModifierAutoFollowModifier` |
| `SetReferenceActor` | 设置朝向目标 | `UActorModifierLookAtModifier` |
| `SetOrientationAxis` | 设置朝向轴 | `UActorModifierLookAtModifier` |
| `SetFlipAxis` | 翻转朝向方向 | `UActorModifierLookAtModifier` |

### 样条/对齐 Modifier 节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSplineActor` | 设置样条 Actor | `UActorModifierSplinePathModifier` |
| `SetSampleMode` | 采样模式（百分比/距离/时间/点） | `UActorModifierSplinePathModifier` |
| `SetProgress` | 百分比进度 | `UActorModifierSplinePathModifier` |
| `SetOrient` | 是否沿样条切线朝向 | `UActorModifierSplinePathModifier` |
| `AddReferenceActor` | 添加加权参考 Actor | `UActorModifierAlignBetweenModifier` |
| `RemoveReferenceActor` | 移除参考 Actor | `UActorModifierAlignBetweenModifier` |
| `SetIncludeChildren` | 是否包含子 Actor | `UActorModifierHoldoutCompositeModifier` |

### 使用示例（蓝图描述）

**场景：将 6 个方块排成 2×3 网格**

1. 创建一个父 Actor（如空 Actor），在其下放置 6 个 StaticMesh Actor
2. 为父 Actor 添加 `UActorModifierGridArrangeModifier` 组件
3. 设置 `Count = (3, 2)`（3 列 2 行）
4. 设置 `Spread = (120, 120)` 表示每个方向间距 120 单位
6 个方块会自动排列成网格，后续增删子 Actor 会自动重新排列

**场景：物体沿样条线移动**

1. 创建包含 SplineComponent 的 Actor
2. 为目标 Actor 添加 `UActorModifierSplinePathModifier`
3. 设置 `SplineActor` 指向样条 Actor
4. 设置 `SampleMode = Percentage`
5. 动态修改 `Progress` 值，目标 Actor 会沿样条线移动

## C++ 用法

### 头文件引入

```cpp
// 核心模块
#include "ActorModifierTypes.h"
#include "Modifiers/ActorModifierArrangeBaseModifier.h"
#include "Modifiers/ActorModifierAttachmentBaseModifier.h"

// Layout 模块
#include "Modifiers/ActorModifierGridArrangeModifier.h"
#include "Modifiers/ActorModifierRadialArrangeModifier.h"
#include "Modifiers/ActorModifierJustifyModifier.h"
#include "Modifiers/ActorModifierAlignBetweenModifier.h"
#include "Modifiers/ActorModifierSplinePathModifier.h"
#include "Modifiers/ActorModifierAutoFollowModifier.h"
#include "Modifiers/ActorModifierLookAtModifier.h"

// Rendering 模块
#include "Modifiers/ActorModifierHoldoutCompositeModifier.h"

// 工具类
#include "Utilities/ActorModifierActorUtils.h"
#include "Extensions/ActorModifierSceneTreeUpdateExtension.h"
#include "Extensions/ActorModifierTransformUpdateExtension.h"
#include "Extensions/ActorModifierRenderStateUpdateExtension.h"
```

### 基本用法 — 编程式操作 Modifier

```cpp
// 获取已附加到 Actor 上的 GridArrange Modifier
UActorModifierGridArrangeModifier* GridModifier = Actor->FindComponentByClass<UActorModifierGridArrangeModifier>();
if (GridModifier)
{
    // 修改网格大小
    GridModifier->SetCount(FIntPoint(4, 3));
    // 修改间距
    GridModifier->SetSpread(FVector2D(100.f, 100.f));
    // 设置起始角
    GridModifier->SetStartCorner(EActorModifierGridArrangeCorner2D::TopLeft);
}
```

### 进阶用法 — 使用 ActorUtils 工具函数

```cpp
#include "Utilities/ActorModifierActorUtils.h"

// 计算一组 Actor 的组合边界
TSet<TWeakObjectPtr<AActor>> Actors;
Actors.Add(Actor1);
Actors.Add(Actor2);

FTransform ReferenceTransform = FTransform::Identity;
FBox CombinedBounds = UE::ActorModifier::ActorUtils::GetActorsBounds(Actors, ReferenceTransform);

// 检查 Actor 是否可见
bool bVisible = UE::ActorModifier::ActorUtils::IsActorVisible(MyActor);

// 计算 LookAt 旋转
FRotator LookAtRotation = UE::ActorModifier::ActorUtils::FindLookAtRotation(
    EyePosition, TargetPosition, EActorModifierAxis::X, false);
```

### 进阶用法 — 自定义 Modifier 继承

```cpp
// 继承 ArrangeBaseModifier 来创建自定义布局 Modifier
UCLASS(BlueprintType)
class UMyCustomArrangeModifier : public UActorModifierArrangeBaseModifier
{
    GENERATED_BODY()

protected:
    virtual void OnModifierCDOSetup(FActorModifierCoreMetadata& InMetadata) override
    {
        // 设置 Modifier 的显示名称和分类
        InMetadata.SetName(TEXT("MyCustomArrange"));
        InMetadata.SetCategory(TEXT("MyModifiers"));
    }

    virtual void Apply() override
    {
        // 获取子 Actor 列表
        // 执行自定义布局逻辑
        // 使用 UActorModifierTransformShared 保存/恢复 Transform
    }
};
```

## Demo 示例

### Build.cs 依赖

```csharp
// 如果只需要使用 Layout Modifier
PublicDependencyModuleNames.AddRange(new string[]
{
    "ActorModifier",
    "ActorModifierLayout",
    "ActorModifierCore",
    "Core"
});
```

### 最小示例 — 自动跟随 Modifier

```cpp
// MyFollowActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyFollowActor.generated.h"

class UActorModifierAutoFollowModifier;

UCLASS()
class AMyFollowActor : public AActor
{
    GENERATED_BODY()

public:
    AMyFollowActor();

    UPROPERTY(VisibleAnywhere)
    USceneComponent* Root;

    UPROPERTY(VisibleAnywhere)
    UActorModifierAutoFollowModifier* FollowModifier;

    UFUNCTION(BlueprintCallable)
    void SetFollowTarget(AActor* Target);
};
```

```cpp
// MyFollowActor.cpp
#include "MyFollowActor.h"
#include "Modifiers/ActorModifierAutoFollowModifier.h"

AMyFollowActor::AMyFollowActor()
{
    Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    RootComponent = Root;

    // 创建自动跟随 Modifier
    FollowModifier = CreateDefaultSubobject<UActorModifierAutoFollowModifier>(TEXT("FollowModifier"));
}

void AMyFollowActor::SetFollowTarget(AActor* Target)
{
    if (FollowModifier && Target)
    {
        FActorModifierSceneTreeActor Ref;
        Ref.ReferenceContainer = EActorModifierReferenceContainer::Other;
        Ref.ReferenceActorWeak = Target;
        FollowModifier->SetReferenceActor(Ref);
    }
}
```

## 核心扩展机制

### Extensions（扩展接口）

Modifier 通过实现以下三个扩展接口来响应外部变化：

| 接口 | 回调函数 | 触发时机 |
|---|---|---|
| `IActorModifierSceneTreeUpdateHandler` | `OnSceneTreeTrackedActorChanged` | 跟踪的 Actor 发生变化 |
| | `OnSceneTreeTrackedActorChildrenChanged` | 子 Actor 集合变化 |
| | `OnSceneTreeTrackedActorDirectChildrenChanged` | 直接子 Actor 顺序变化 |
| | `OnSceneTreeTrackedActorParentChanged` | 父 Actor 变化 |
| | `OnSceneTreeTrackedActorRearranged` | Actor 重排 |
| `IActorModifierTransformUpdateHandler` | `OnTransformUpdated` | Actor Transform 更新 |
| `IActorModifierRenderStateUpdateHandler` | `OnRenderStateUpdated` | 渲染状态变化 |
| | `OnActorVisibilityChanged` | Actor 可见性变化 |

### Shared Objects（共享状态）

当多个 Modifier 同时操作同一个 Actor 时，共享对象确保原始状态只保存一次：

| 共享类 | 管理内容 |
|---|---|
| `UActorModifierTransformShared` | Actor 的原始 Transform（位置/旋转/缩放） |
| `UActorModifierVisibilityShared` | Actor 的原始可见性（编辑器/游戏） |

### FActorModifierSceneTreeActor

用于指定参考 Actor 的结构体，支持多种定位方式：

| ReferenceContainer | 说明 |
|---|---|
| `Previous` | 使用层级中的上一个 Actor |
| `Next` | 使用层级中的下一个 Actor |
| `First` | 使用层级中的第一个 Actor |
| `Last` | 使用层级中的最后一个 Actor |
| `Other` | 使用用户指定的 Actor |

## 模块依赖

### ActorModifier（Runtime）

| 模块 | 用途 |
|---|---|
| `ActorModifierCore` | Modifier 框架核心（基类、元数据、共享对象等） |
| `Core` | 基础引擎模块 |
| `CoreUObject` | UObject 系统（私有） |
| `Engine` | 引擎核心（私有） |

### ActorModifierLayout（Runtime）

| 模块 | 用途 |
|---|---|
| `ActorModifier` | 核心 Modifier 基类和类型 |
| `ActorModifierCore` | Modifier 框架 |
| `Core` | 基础引擎模块 |
| `Engine` | 引擎核心（私有） |

### ActorModifierRendering（Runtime）

| 模块 | 用途 |
|---|---|
| `ActorModifier` | 核心 Modifier 基类和类型 |
| `ActorModifierCore` | Modifier 框架 |
| `CompositeCore` | 合成渲染子系统（私有） |
| `Engine` | 引擎核心（私有） |

### ActorModifierEditor（Editor）

| 模块 | 用途 |
|---|---|
| `ActorModifier` | 核心 Modifier 基类（私有） |
| `ActorModifierCore` | Modifier 框架（私有） |
| `ActorModifierLayout` | Layout Modifier 类（私有） |
| `ClonerEffectorEditor` | 编辑器 UI 支持（私有） |
| `Projects` | 项目信息（私有） |
| `Slate` / `SlateCore` | UI 框架（私有） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-09-23 | `96a6d8a` | **Bug 修复**：修复了 Justify Modifier 在容器旋转时不工作的 bug |
| 2025-09-23 | `df329aa` | **里程碑**：移除了 Motion Design 插件的 Beta 标签，表示正式发布 |
| 2025-09-12 | `8406696` | **编译修复**：添加缺失的头文件以修复非 Unity 构建错误 |
| 2025-07-14 | `6a76760` | **新功能**：添加 Holdout Composite Modifier，支持单独通道渲染后合成 |
| 2025-06-10 | `4e2c563` | **增强**：添加 FilterActorByComponentClass 指定符，SplinePath 支持循环 |
| 2025-05-27 | `d68af2c` | **本地化**：为 Modifier 添加操作栈/菜单的本地化支持 |
| 2025-05-08 | `d53ec51` | **创建**：从 Experimental 迁移到 VirtualProduction 目录 |

### 维护评价

- **创建时间**：2025-05-08（约 1 年前）
- **活跃程度**：**活跃维护** — 近 6 个月内有功能性更新、Bug 修复和新 Modifier 添加
- **Beta 已移除**：2025-09-23 正式移除 Beta 标签，表明 Epic 认为该插件已稳定
- **依赖关系**：依赖 ActorModifierCore（框架）和 ClonerEffector（运动设计系统），属于 Motion Design 生态的一部分
- **无测试用例**：插件目录内未发现自动化测试文件
- **推荐使用**：✅ 推荐用于 Motion Design / Virtual Production 场景。如果你在做动态图形或需要声明式 Actor 布局系统，这是官方推荐的方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/ActorModifier)
- [ActorModifierCore 插件](../ActorModifierCore/index.md)（Modifier 框架核心）
- [ClonerEffector 插件](../ClonerEffector/index.md)（运动设计生态系统）
- [CompositeCore 插件](../CompositeCore/index.md)（HoldoutComposite 的依赖）
