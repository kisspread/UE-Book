# Avalanche Modifiers Editor

> Compositing, designer and broadcasting tool.
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计修改器编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvalancheModifiersEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheModifiersEditor) | |

## 用途

`AvalancheModifiersEditor` 是 Motion Design（运动设计）插件的一个**编辑器扩展模块**，其核心功能是将 `ActorModifierCore` 系统深度集成到 Motion Design 编辑器的**大纲视图（Outliner）** 中。

这个模块解决了以下问题：
1.  **可视化**：将应用于 Actor 的修改器栈（Modifier Stack）以树状结构直观地展示在大纲视图中，便于查看和管理。
2.  **交互操作**：允许用户通过拖放（Drag & Drop）来重新排序、添加或移动修改器，提供了比传统属性面板更高效的编辑体验。
3.  **上下文管理**：为大纲中的修改器项提供专属的右键上下文菜单，执行复制、删除、启用/禁用等操作。

简而言之，它让你在 Motion Design 的专用编辑器中，能够像管理场景中的 Actor 一样，直观地管理和操控叠加在 Actor 上的视觉效果修改器。

## 使用场景

-   **虚拟制片/广播包装项目**：在 Motion Design 编辑器中，为一个 3D 文字或几何体叠加了多个视觉效果（如扭曲、颜色校正、生成器），需要调整它们的叠加顺序或单独编辑某个效果。
-   **复杂视觉特效设计**：当场景中的 Actor 使用了复杂的修改器栈（例如：克隆 -> 噪波位移 -> 材质动态修改），需要在大纲中一目了然地看到整个效果管线。
-   **快速原型制作**：需要快速地通过拖放方式，在不同 Actor 或修改器栈之间移动或复制修改器，以测试不同的视觉效果组合。

## 蓝图用法

该模块主要提供编辑器内的可视化和交互功能，未发现公开的 `BlueprintCallable` 或 `BlueprintReadWrite` API。其功能主要通过 Motion Design 编辑器的大纲视图界面暴露给用户。

## C++ 用法

此模块为编辑器模块，其核心类主要用于扩展编辑器功能。

### 头文件引入

若要在其他编辑器模块中与此大纲视图交互（通常不常见），可引入以下头文件：
```cpp
// 用于创建自定义大纲项代理
#include “Outliner/AvaOutlinerModifierProxy.h”
#include “Outliner/AvaOutlinerModifier.h”
// 用于处理拖放
#include “Outliner/AvaOutlinerModifierDropHandler.h”
```

### 基本用法

该模块的核心是定义了几种大纲项（Outliner Item）类型来表示修改器。这些类在模块启动时自动注册。

**1. 修改器代理项 (`FAvaOutlinerModifierProxy`)**
此类代表一个 Actor 的根修改器栈。它会自动监听栈内修改器的增删，并动态更新大纲子项。
```cpp
// 这是模块内部注册逻辑的抽象示意，不需直接调用。
// 当一个 Actor 被选中并拥有 ActorModifierCoreStack 时，
// FAvaOutlinerModifierProxy 会自动创建并显示为大纲中的一个节点。
UActorModifierCoreStack* RootStack = GetActorModifierStack(Actor);
// FAvaOutlinerModifierProxy 内部通过 OnModifierAdded/Removed 响应栈的变化。
```
**来源**: `Private/Outliner/AvaOutlinerModifierProxy.h`

**2. 修改器项 (`FAvaOutlinerModifier`)**
此类代表栈中的单个修改器实例。
```cpp
// 同样，此类由 FAvaOutlinerModifierProxy 在 “GetProxiedItems” 中自动创建。
// 它包装了一个 UActorModifierCoreBase 对象。
UActorModifierCoreBase* Modifier = ...;
FAvaOutlinerModifier OutlinerModifier(OutlinerInterface, Modifier);
FText Name = OutlinerModifier.GetDisplayName(); // 获取在大纲中显示的名称
FSlateIcon Icon = OutlinerModifier.GetIcon();   // 获取图标
```
**来源**: `Private/Outliner/AvaOutlinerModifier.h`

**3. 拖放处理器 (`FAvaOutlinerModifierDropHandler`)**
处理将修改器项拖放到大纲中其他位置的操作。
```cpp
// 模块内部逻辑示意。当用户拖动一个 FAvaOutlinerModifier 时，
// FAvaOutlinerModifierDropHandler 的 CanDrop 和 Drop 方法会被调用。
TOptional<EItemDropZone> DropZone = DropHandler.CanDrop(CurrentZone, TargetItem);
if (DropZone)
{
    bool bSuccess = DropHandler.Drop(*DropZone, TargetItem);
}
```
**来源**: `Private/Outliner/AvaOutlinerModifierDropHandler.h`

### 进阶用法：自定义上下文菜单

模块通过 `FAvaOutlinerModifierContextMenu` 静态类扩展大纲的右键菜单。
```cpp
// 在模块启动时，会将 OnExtendOutlinerContextMenu 绑定到大纲菜单的扩展点。
// 当用户在大纲中选中修改器项并右键时，此函数被调用，填充菜单选项。
void FAvaOutlinerModifierContextMenu::OnExtendOutlinerContextMenu(UToolMenu* InToolMenu)
{
    UAvaOutlinerItemsContext* ItemsContext = InToolMenu->FindContext<UAvaOutlinerItemsContext>();
    TSet<TWeakObjectPtr<UObject>> ContextObjects;
    GetContextObjects(ItemsContext, ContextObjects); // 获取选中的修改器对象
    // ... 基于 ContextObjects 填充菜单项
}
```
**来源**: `Private/Outliner/AvaOutlinerModifierContextMenu.h`

## Demo 示例

以下是一个最小示例，展示如何在一个自定义的编辑器工具中，获取当前选中 Actor 的修改器栈信息（**注意**：这仅用于演示概念，实际运行需要 Motion Design 编辑器环境和正确的 Actor 类型）。

**MyModifierInspector.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “ActorModifierCoreStack.h”

class FMyModifierInspector
{
public:
    static void InspectSelectedActorModifiers();
};
```

**MyModifierInspector.cpp**
```cpp
#include “MyModifierInspector.h”
#include “Editor.h”
#include “Engine/Selection.h”

void FMyModifierInspector::InspectSelectedActorModifiers()
{
    // 获取编辑器中选中的第一个 Actor
    USelection* SelectedActors = GEditor->GetSelectedActors();
    AActor* Actor = Cast<AActor>(SelectedActors->GetSelectedObject(0));

    if (!Actor)
    {
        UE_LOG(LogTemp, Warning, TEXT(“No actor selected.”));
        return;
    }

    // 尝试从 Actor 组件或子对象中获取根修改器栈
    // 注意：实际获取方式取决于 Actor 如何集成 ActorModifierCore，此处为示意。
    UActorModifierCoreStack* ModifierStack = nullptr;
    // ... (假设通过某种方式获取到 ModifierStack)

    if (ModifierStack)
    {
        UE_LOG(LogTemp, Log, TEXT(“Found Modifier Stack on Actor: %s”), *Actor->GetName());
        // 获取栈内的修改器数量和类名
        for (UActorModifierCoreBase* Modifier : ModifierStack->GetModifiers())
        {
            UE_LOG(LogTemp, Log, TEXT(“  - Modifier: %s”), *Modifier->GetClass()->GetName());
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT(“Selected Actor has no modifier stack.”));
    }
}
```

## 模块依赖

从 `AvalancheModifiersEditor.Build.cs` 分析，该模块依赖于其运行时对应模块和核心编辑器功能。

| 模块 | 用途 |
|---|---|
| `AvalancheModifiers` | 提供修改器系统的运行时核心实现（ActorModifierCore 等）。 |
| `AvalancheOutliner` | 提供 Motion Design 编辑器大纲视图的基础框架和接口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro... | 将运动设计的相关选项卡（场景设置、大纲）从关卡编辑器主界面移出，归类到独立的编辑器分组中，可能提升了界面整洁度。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde... | 在显示控制工具栏中增加了页面加载选项，并添加了相关功能，可能涉及序列或播放列表的管理。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了一个项目设置，用于强制禁用3D文字和形状的碰撞，解决了特定场景下的交互问题。 |

### 维护评价

**活跃维护**。该模块作为 Motion Design 核心工作流的一部分，仍在持续更新和优化。从最近的提交记录看，开发团队仍在积极改进编辑器的用户体验和功能。虽然该模块创建于2025年5月，但其所属的 Motion Design 插件生态系统正处于活跃发展期，因此推荐在需要进行专业虚拟制片和广播设计工作的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheModifiersEditor)
- [父插件 (Motion Design)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)