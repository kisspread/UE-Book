# Object Mixer

> Edit any properties of scene objects in a spreadsheet format!

| 属性 | 值 |
|---|---|
| 中文名 | 对象混音器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产，测试资源） |
| 模块 | `ObjectMixerEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-23 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ObjectMixer/ObjectMixer) | |

## 用途

Object Mixer 解决了在大型场景中高效查看和编辑大量同类对象（如灯光、特效、音频组件等）的痛点。它超越了简单的“电子表格”描述，是一个功能强大的**场景对象批量编辑器**。它基于 UE 的场景大纲器（Scene Outliner）扩展，提供了一个可定制的表格视图，让用户能够：
1.  **批量筛选**：通过自定义过滤器（蓝图或C++）快速筛选出场景中特定类型的对象（如所有点光源、所有带有特定标签的Actor）。
2.  **列式查看**：将选定对象的任意属性（如颜色、强度、启用状态）以列的形式显示在表格中，一目了然地进行对比。
3.  **批量编辑**：直接在表格单元格中修改属性值，并支持将修改同步到所有选中的同类对象，极大提高了场景调优和属性设置的效率。

它的核心价值在于将引擎的对象属性编辑系统从传统的“单一对象详情面板”模式，扩展为高效的“批量关系数据管理”模式。

## 使用场景

-   **灯光/材质批量调整**：你需要同时调整场景中所有点光源的颜色和强度，或为所有使用特定材质的Actor设置全局标量参数。
-   **组件属性集中管理**：你希望在一个视图中看到所有场景中AI感知组件的“调试显示”状态，并快速切换它们。
-   **自定义编辑器工具开发**：你正在制作一个游戏原型，需要一个专门的编辑器面板来管理所有“可交互物体”的自定义属性（如交互距离、提示文本）。
-   **场景审查与优化**：你希望快速找出场景中所有启用了碰撞但不需要的静态网格体组件，或所有未烘焙的光照贴图分辨率过高的组件。

## 蓝图用法

### 核心节点

核心功能通过继承 `UObjectMixerBlueprintObjectFilter` 类来实现。在蓝图中创建此类的子类，并重写其事件来定义过滤行为。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetObjectClassesToFilter` | **(必须重写)** 返回要显示在列表中的对象/组件类。例如，返回 `LightComponentBase` 以显示所有灯光。 | `UObjectMixerBlueprintObjectFilter` |
| `GetObjectClassesToPlace` | 返回可以通过“添加”按钮放置到关卡中的Actor类。 | `UObjectMixerBlueprintObjectFilter` |
| `GetColumnsToShowByDefault` | 返回默认显示的属性列名集合（如 `Intensity`）。 | `UObjectMixerBlueprintObjectFilter` |
| `GetColumnsToExclude` | 返回永远不应显示的属性列名集合。 | `UObjectMixerBlueprintObjectFilter` |
| `GetForceAddedColumns` | 强制添加来自父类的属性列，即使指定的类本身没有该属性。 | `UObjectMixerBlueprintObjectFilter` |
| `GetObjectMixerPropertyInheritanceInclusionOptions` | 控制属性搜索的继承范围（是否包含父类或子类属性）。 | `UObjectMixerBlueprintObjectFilter` |
| `GetShowTransientObjects` | 决定是否显示瞬态对象（如序列器生成的可生成对象）。 | `UObjectMixerBlueprintObjectFilter` |
| `ShouldAllowHybridRows` | 决定是否允许混合行（将拥有单个匹配组件的Actor和组件合并为一行）。 | `UObjectMixerBlueprintObjectFilter` |

### 使用示例（蓝图描述）

1.  **创建自定义过滤器**：
    *   在内容浏览器右键，选择 `蓝图类`，父类选择 `Object Mixer Filter (Blueprint)`。
    *   打开该蓝图，在 `事件图表` 中找到 `GetObjectClassesToFilter` 事件。
    *   重写此事件，拖出返回值引脚，连接一个 `Make Array` 节点，数组中填入 `Point Light Component` 和 `Spot Light Component`。
    *   重写 `GetColumnsToShowByDefault`，返回包含 `Intensity` 和 `LightColor` 的数组。

2.  **使用过滤器**：
    *   在编辑器中打开 `Object Mixer` 窗口（通常在 `窗口 -> Object Mixer`）。
    *   在窗口顶部的过滤器下拉菜单中，选择你刚创建的蓝图过滤器。
    *   列表将只显示场景中的点光源和聚光灯，并默认显示“强度”和“颜色”两列。
    *   现在，你可以框选多行，然后直接在“强度”列的单元格中输入新值，或点击颜色列打开颜色拾取器，所选灯光的属性将被批量修改。

## C++ 用法

### 头文件引入

```cpp
#include "ObjectMixerEditorModule.h"
#include "ObjectFilter/ObjectMixerEditorObjectFilter.h"
```

### 基本用法

创建一个原生 C++ 过滤器类，用于过滤和显示自定义游戏对象的属性。

```cpp
// MyGameLightFilter.h
#pragma once
#include "ObjectFilter/ObjectMixerEditorObjectFilter.h"
#include "MyGameLightFilter.generated.h"

UCLASS()
class UMyGameLightFilter : public UObjectMixerObjectFilter
{
    GENERATED_BODY()
public:
    // 返回要过滤的组件类
    virtual TSet<UClass*> GetObjectClassesToFilter() const override
    {
        return { UMyGameLightComponent::StaticClass() };
    }

    // 默认显示的列
    virtual TSet<FName> GetColumnsToShowByDefault() const override
    {
        return { GET_MEMBER_NAME_CHECKED(UMyGameLightComponent, LightIntensity),
                 GET_MEMBER_NAME_CHECKED(UMyGameLightComponent, LightColor) };
    }

    // 决定混合行策略
    virtual bool ShouldAllowHybridRows() const override
    {
        return true; // 允许将只有一个灯光组件的Actor合并显示
    }
};
```

### 进阶用法

结合继承选项和关联Actor，实现复杂的视图逻辑。

```cpp
// AdvancedPropFilter.h
UCLASS()
class UAdvancedPropFilter : public UObjectMixerObjectFilter
{
    GENERATED_BODY()
public:
    virtual TSet<UClass*> GetObjectClassesToFilter() const override
    {
        // 过滤所有继承自AInteractiveActor的类
        return { AInteractiveActor::StaticClass() };
    }

    // 包含父类和直接子类的属性
    virtual EObjectMixerInheritanceInclusionOptions GetObjectMixerPropertyInheritanceInclusionOptions() const override
    {
        return EObjectMixerInheritanceInclusionOptions::IncludeAllParentsAndOnlyImmediateChildren;
    }

    // 将“交互范围”属性强制显示，即使它在父类中
    virtual TSet<FName> GetForceAddedColumns() const override
    {
        return { TEXT("InteractionRadius") };
    }

    // 查找关联的Actor（例如，一个带有多个子Actor的复杂交互装置）
    virtual TArray<AActor*> FindAssociatedActors(AActor* InActor) const override
    {
        TArray<AActor*> AssociatedActors;
        if (AInteractiveActor* InteractiveActor = Cast<AInteractiveActor>(InActor))
        {
            // 假设每个交互Actor都有一个附属的特效Actor
            if (AActor* FXActor = InteractiveActor->GetAssociatedFXActor())
            {
                AssociatedActors.Add(FXActor);
            }
        }
        return AssociatedActors;
    }
};
```

## Demo 示例

以下是一个最小的可编译示例，展示如何创建一个自定义的灯光过滤器。

### MyGameLightFilter.h
```cpp
// MyGameLightFilter.h
#pragma once

#include "CoreMinimal.h"
#include "ObjectFilter/ObjectMixerEditorObjectFilter.h"
#include "MyGameLightFilter.generated.h"

UCLASS()
class UMyGameLightFilter : public UObjectMixerObjectFilter
{
    GENERATED_BODY()

public:
    virtual TSet<UClass*> GetObjectClassesToFilter() const override;
    virtual TSet<FName> GetColumnsToShowByDefault() const override;
    virtual bool ShouldAllowHybridRows() const override;
};
```

### MyGameLightFilter.cpp
```cpp
// MyGameLightFilter.cpp
#include "MyGameLightFilter.h"

#include "Components/PointLightComponent.h"
#include "Components/SpotLightComponent.h"

TSet<UClass*> UMyGameLightFilter::GetObjectClassesToFilter() const
{
    return { UPointLightComponent::StaticClass(), USpotLightComponent::StaticClass() };
}

TSet<FName> UMyGameLightFilter::GetColumnsToShowByDefault() const
{
    // 注意：直接使用父类 ULightComponentBase 的属性名
    return { GET_MEMBER_NAME_CHECKED(ULightComponentBase, Intensity),
             GET_MEMBER_NAME_CHECKED(ULightComponentBase, LightColor) };
}

bool UMyGameLightFilter::ShouldAllowHybridRows() const
{
    return true;
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。ObjectMixerEditor 模块的依赖主要来自其作为编辑器插件的基础需求，如 `UnrealEd`、`SceneOutliner` 等。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `c19c7e83` | [ContentBrowser] New Add Menu Misc Menu | 内容浏览器新增菜单项迁移。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移至 UE_LOGF。 |
| 2026-03-06 | `91677cb5` | EditorUsability : GlobalCommands | 编辑器全局命令可用性改进。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了错误的查找替换后的第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚了之前的提交 CL51314860。 |

### 维护评价

-   **活跃维护**：插件自2022年创建，最近在2026年4月仍有更新，表明 Epic Games 团队仍在积极维护。
-   **功能稳定**：虽然标记为实验性（`IsBetaVersion: true`），但其核心架构和API已相当成熟，广泛应用于 Epic 的项目（如《Fortnite》和《UEFN》）中。
-   **推荐使用**：对于需要批量编辑场景对象属性的项目，Object Mixer 是一个极其强大且高效的工具，强烈推荐使用。其“实验性”状态更多是API层面可能还有细微调整的提示，并非功能不稳定。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ObjectMixer/ObjectMixer)
-   官方文档: 无
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ObjectMixer/ObjectMixer/Tests)