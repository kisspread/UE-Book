# Avalanche

> Compositing, designer and broadcasting tool. Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（预设动画、材质、蓝图资产） |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime) 等共 43 个模块 |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche（运动设计）是一个功能极其强大的实时图形设计与广播制作插件套件。它不仅仅是一个简单的动画工具，而是提供了一套完整的、面向虚拟制片（Virtual Production）和直播（Broadcast）的内容创建与控制工作流。其核心价值在于将复杂的图形动画、场景管理、材质编辑、特效、远程控制和播出管理集成到一个统一的编辑器环境中，让设计师和工程师能够在UE内高效地制作、预演和输出用于LED墙、电视直播、体育赛事等场景的高质量动态图形（Motion Graphics）。

## 使用场景

-   **虚拟制片 LED 墙内容创作**：你需要为一块巨大的LED墙设计和播放复杂的实时图形、动画和过渡效果。
-   **电视直播与赛事转播**：在直播环境中，需要快速创建和修改比分牌、选手信息、动态Logo、图文包等实时图形元素。
-   **动态广告与品牌内容**：制作可交互的、数据驱动的数字广告牌或品牌展示内容。
-   **实时演出与音乐会视觉**：设计并控制音乐会、舞台剧的现场实时视觉特效和投影内容。

## 蓝图用法

由于 Avalance 是一个庞大的设计套件，其蓝图接口分布在其众多子模块中。对于 `AvalanchePropertyAnimatorEditor` 模块，它主要扩展了运动设计编辑器的“大纲视图”，因此其蓝图功能主要体现在编辑器交互而非运行时逻辑。

### 核心节点

基于 `AvalanchePropertyAnimatorEditor` 模块的分析，其主要提供编辑器扩展功能，而非运行时蓝图节点。其核心交互体现在运动设计大纲视图（Outliner）中对 `PropertyAnimator` 的管理。

### 使用示例（蓝图描述）

在运动设计编辑器的大纲视图中：
1.  为一个Actor添加 `UPropertyAnimatorCoreComponent`。
2.  在该组件下，你可以添加、删除或配置各种 `UPropertyAnimatorCoreBase` 属性动画器。
3.  `AvalanchePropertyAnimatorEditor` 模块使得这些动画器能够像子Actor一样在大纲中显示为独立条目。
4.  你可以直接在大纲中拖拽、删除这些动画器项，或者右键调出上下文菜单进行操作。
5.  所有这些编辑器交互背后的逻辑，由该模块中的 `FAvaPropertyAnimatorEditorOutliner`、`FAvaPropertyAnimatorEditorOutlinerProxy` 等类实现。

## C++ 用法

本模块的核心是扩展运动设计大纲视图（`IAvaOutliner`），允许 `PropertyAnimator` 对象在大纲中被管理。

### 头文件引入

```cpp
#include "AvaPropertyAnimatorEditorModule.h"
// 通常使用模块内的类，如 Outliner 相关的类
#include "Outliner/AvaPropertyAnimatorEditorOutliner.h"
```

### 基本用法

该模块主要提供编辑器扩展，使用者（开发者）很少直接调用其API，而是通过编辑器UI进行交互。了解其工作方式可以从理解大纲项的继承关系开始。

```cpp
// 模拟创建一个大纲项的场景（通常在模块内部发生，此处仅为示例）
// 需要一个有效的 IAvaOutliner 引用和一个 UPropertyAnimatorCoreBase 对象
// FAvaPropertyAnimatorEditorOutliner* NewItem = new FAvaPropertyAnimatorEditorOutliner(Outliner, MyPropertyAnimator);
```
*（注：以上代码为概念性示例，展示了该模块核心类的构造方式。实际使用由编辑器框架驱动。）*

### 进阶用法

该模块通过委托扩展大纲视图的功能，例如右键菜单。开发者可以通过了解 `FAvaPropertyAnimatorEditorOutlinerContextMenu` 来理解如何为自定义项添加上下文菜单。

```cpp
// 上下文菜单的扩展通过静态函数实现，由编辑器菜单系统调用
// 具体实现在 .cpp 文件中，例如为选中的动画器添加自定义操作
void FAvaPropertyAnimatorEditorOutlinerContextMenu::OnExtendOutlinerContextMenu(UToolMenu* InToolMenu)
{
    // 获取上下文对象（如选中的动画器）
    // 添加菜单项（如重置、复制、粘贴预设等）
}
```

## Demo 示例

由于该模块是一个编辑器扩展，没有独立的运行时行为示例。其功能通过运动设计编辑器的UI展现。一个展示其集成效果的最小C++示例是模拟查询大纲中的属性动画器项：

```cpp
// AvaPropertyAnimatorDemo.h
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "AvaPropertyAnimatorDemo.generated.h"

class IAvaOutliner;
class FAvaPropertyAnimatorEditorOutliner;

UCLASS()
class UAvaPropertyAnimatorDemoSubsystem : public UEditorSubsystem
{
    GENERATED_BODY()
public:
    // 一个函数，用于演示如何访问与PropertyAnimator相关的大纲项
    void ListPropertyAnimatorsInAvaOutliner();

private:
    // 辅助函数：递归查找大纲项
    void FindAnimatorItems(const TArray<FAvaOutlinerItemPtr>& InItems, TArray<FAvaPropertyAnimatorEditorOutliner*>& OutFound);
};

// AvaPropertyAnimatorDemo.cpp
#include "AvaPropertyAnimatorDemo.h"
#include "AvaPropertyAnimatorEditorOutliner.h"
#include "AvaOutlinerSubsystem.h" // 假设存在一个全局访问点

void UAvaPropertyAnimatorDemoSubsystem::ListPropertyAnimatorsInAvaOutliner()
{
    // 获取运动设计大纲子系统（这是一个概念性接口）
    // UAvaOutlinerSubsystem* AvaOutlinerSubsystem = GEditor->GetEditorSubsystem<UAvaOutlinerSubsystem>();
    // if (!AvaOutlinerSubsystem) return;
    //
    // TArray<FAvaOutlinerItemPtr> RootItems = AvaOutlinerSubsystem->GetRootItems();
    // TArray<FAvaPropertyAnimatorEditorOutliner*> AnimatorItems;
    // FindAnimatorItems(RootItems, AnimatorItems);
    //
    // UE_LOG(LogTemp, Log, TEXT("Found %d Property Animator items in the Ava Outliner."), AnimatorItems.Num());
    // for (FAvaPropertyAnimatorEditorOutliner* Item : AnimatorItems)
    // {
    //     if (UPropertyAnimatorCoreBase* Animator = Item->GetPropertyAnimator())
    //     {
    //         UE_LOG(LogTemp, Log, TEXT("  - Animator: %s"), *Animator->GetName());
    //     }
    // }
    // 注意：此代码为概念演示，实际运行依赖于完整的Avalanche编辑器环境。
}

void UAvaPropertyAnimatorDemoSubsystem::FindAnimatorItems(const TArray<FAvaOutlinerItemPtr>& InItems, TArray<FAvaPropertyAnimatorEditorOutliner*>& OutFound)
{
    // 实现递归查找逻辑...
    // for (const FAvaOutlinerItemPtr& Item : InItems)
    // {
    //     if (FAvaPropertyAnimatorEditorOutliner* AnimatorItem = StaticCast<FAvaPropertyAnimatorEditorOutliner*>(Item.Get()))
    //     {
    //         OutFound.Add(AnimatorItem);
    //     }
    //     FindAnimatorItems(Item->GetChildren(), OutFound);
    // }
}
```
*（注：上述示例代码中的 `IAvaOutlinerSubsystem` 为假设的接口，用于说明工作原理。实际实现需要参考Avalanche Outliner模块的完整源码。）*

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AvalancheOutliner` | 提供运动设计大纲视图的基础框架（`IAvaOutliner`, `FAvaOutlinerItem` 等） |
| `PropertyAnimatorCore` | 提供属性动画器的核心运行时类（`UPropertyAnimatorCoreBase`, `UPropertyAnimatorCoreComponent`） |
| `ToolMenus` | 用于扩展编辑器上下文菜单 |
| `Slate`, `SlateCore` | 构建编辑器UI元素（大纲项图标、文本等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将场景设置和大纲面板从主编辑器选项卡移至独立窗口组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 使用播出单页面设置时增加了MRQ（Movie Render Queue）使用分析 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在演出控制工具栏增加了页面加载选项（全部、下一个、已选） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 增加了项目设置，可强制禁用Text3D和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口：优化了客户端关联/解除关联时的通知代码 |

### 维护评价

Avalanche（运动设计）插件是 **活跃维护** 的。尽管它于 2025 年 5 月才从实验性分支迁移至正式发布状态，但自创建以来，其开发非常活跃，近期（2026年5月）几乎每天都有功能性更新和优化，涉及工作流改进、新功能添加和性能调整。作为 Epic Games 官方在虚拟制片领域的重量级产品，其维护投入有保障。对于需要专业运动设计和广播解决方案的用户，**强烈推荐使用**。需要注意的是，由于其庞大的规模和对其他插件的依赖（如 Media Compositing, Remote Control, Text3D 等），使用者需要对整个生态系统有一定的了解。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest)