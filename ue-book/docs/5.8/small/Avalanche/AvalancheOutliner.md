# Motion Design

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、编辑器工具） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design（前称 Avalanche）是 Epic 为虚拟制片和广播场景打造的综合性动态设计工具集。它解决的核心问题是：在 Unreal Engine 中以**非线性编辑（NLE）风格**高效创建、编排和播出动态图形（Motion Graphics）内容。

该插件从 Experimental 阶段迁移而来（2025 年 5 月正式搬入 VirtualProduction 目录），提供了以下能力：

- **场景编排**：通过自定义 Outliner 管理复杂的场景层级，支持文件夹分组、颜色标记、Item Proxy（材质代理等）、拖放排序
- **属性动画**：Property Animator + Sequencer 集成，为 Actor 属性提供关键帧动画
- **克隆器与效果器**：ClonerEffector 提供实例化/阵列/粒子效果
- **材质设计器**：Material Designer 提供节点式材质编辑工作流
- **文本与形状**：Text3D 文本生成、AvalancheShapes 矢量形状、SVG 导入
- **遮罩与过渡**：GeometryMask 遮罩系统、AvalancheTransition 场景过渡效果
- **媒体合成**：与 Media IO Framework 和 Media Compositing 联动的媒体播放/合成管线
- **远程控制**：通过 Remote Control 模块实现远程参数控制
- **场景同步**：StormSync 提供多机场景同步
- **渲染输出**：AvalancheMRQ 集成 Movie Render Queue 进行高质量渲染

简而言之，它将 UE5 从"游戏引擎"变为"广播级动态图形设计工具"。

## 使用场景

- 你在制作电视/广播节目包装 → 使用 Motion Design 的克隆器、材质设计器、文本工具快速创建动态图形
- 你需要在虚拟制片场景中管理数百个特效元素的层级 → 使用 AvalancheOutliner 的自定义分组、筛选和排序
- 你想为演出活动创建实时视觉内容 → 使用 Property Animator + Sequencer 做属性动画，通过 Rundown Page 控制播出
- 你需要在多个 Unreal 实例间同步场景状态 → 使用 StormSync 模块
- 你想对 Actor 进行非破坏性修改（镜像、克隆、属性动画） → 使用 ActorModifier + ModifierCore 体系

## 蓝图用法

### 核心节点（AvalancheOutliner 模块）

AvalancheOutliner 模块主要服务于编辑器 UI，蓝图可调用的公开 API 较少，核心交互通过 `UAvaOutlinerSubsystem` 和 `IAvaOutliner` 接口进行。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOrCreateOutliner` | 获取或创建当前 World 的 Outliner 实例 | `UAvaOutlinerSubsystem` |
| `GetOutliner` | 获取当前已存在的 Outliner 实例 | `UAvaOutlinerSubsystem` |
| `OnActorHierarchyChanged` | Actor 层级变化时的广播事件 | `UAvaOutlinerSubsystem` |
| `BroadcastActorHierarchyChanged` | 手动广播 Actor 层级变化通知 | `UAvaOutlinerSubsystem` |

### 核心节点（Avalanche 主模块）

由于主模块信息未在本次提供，以下为基于 .uplugin 描述推断的关键功能区域（需参考各子模块文档）：

| 功能区域 | 关键类/接口 |
|---|---|
| 场景树管理 | `FAvaSceneTree`, `IAvaOutliner` |
| 属性动画 | `AvalanchePropertyAnimator`, Sequencer 集成 |
| 克隆效果器 | `AvalancheEffectors` |
| 材质设计 | `AvalancheMaterial` |
| 文本生成 | `AvalancheText` (Text3D) |
| 形状系统 | `AvalancheShapes` |
| 媒体合成 | `AvalancheMedia` |
| 远程控制 | `AvalancheRemoteControl` |

## C++ 用法

### 头文件引入

```cpp
// AvalancheOutliner 核心接口
#include "IAvaOutliner.h"
#include "IAvaOutlinerModule.h"
#include "AvaOutlinerSubsystem.h"

// Outliner 项目类型
#include "Item/AvaOutlinerItem.h"
#include "Item/AvaOutlinerActor.h"
#include "Item/AvaOutlinerComponent.h"
#include "Item/AvaOutlinerItemProxy.h"

// 筛选器系统
#include "Filters/AvaOutlinerItemTypeFilter.h"
#include "AvaOutlinerDefines.h"
```

### 基本用法：获取 Outliner 实例并操作

```cpp
// 来源: Public/AvaOutlinerSubsystem.h
// 通过 Subsystem 获取或创建 Outliner
UAvaOutlinerSubsystem* OutlinerSubsystem = World->GetSubsystem<UAvaOutlinerSubsystem>();
if (OutlinerSubsystem)
{
    // 需要一个 IAvaOutlinerProvider 实现（通常由编辑器模块提供）
    TSharedRef<IAvaOutliner> Outliner = OutlinerSubsystem->GetOrCreateOutliner(*MyProvider);
    
    // 查找特定 Actor 对应的 Outliner 项目
    FAvaOutlinerItemId ItemId(MyActor);
    FAvaOutlinerItemPtr FoundItem = Outliner->FindItem(ItemId);
    
    if (FoundItem.IsValid())
    {
        // 获取显示名称
        FText DisplayName = FoundItem->GetDisplayName();
    }
}
```

### 基本用法：注册 Item Proxy 工厂

```cpp
// 来源: Public/ItemProxies/AvaOutlinerItemProxyRegistry.h
// 注册自定义 Item Proxy 工厂到模块级别
FAvaOutlinerModule& Module = FAvaOutlinerModule::Get();
FAvaOutlinerItemProxyRegistry& Registry = Module.GetItemProxyRegistry();

// 方法 1: 使用默认工厂注册
Registry.RegisterItemProxyWithDefaultFactory<FMyCustomItemProxy, /*Priority=*/10>();

// 方法 2: 使用自定义工厂类
Registry.RegisterItemProxyFactory<FMyCustomProxyFactory>(/*构造参数*/);

// 取消注册
Registry.UnregisterItemProxyFactory<FMyCustomItemProxy>();
```

### 基本用法：注册筛选器表达式工厂

```cpp
// 来源: Private/AvaOutlinerModule.h
// 注册自定义文本筛选器表达式工厂
FAvaOutlinerModule& Module = FAvaOutlinerModule::Get();
Module.RegisterFilterExpressionFactory<FMyColorFilterExpressionFactory>();

// 注册自定义筛选器建议工厂
Module.RegisterFilterSuggestionFactory<FMyTagSuggestionFactory>();
```

### 进阶用法：自定义 Item 并挂载到 Outliner

```cpp
// 来源: Public/IAvaOutliner.h (FindOrAdd 模板)
// 创建或查找一个 Outliner Item
TSharedRef<FAvaOutlinerActor> ActorItem = Outliner->FindOrAdd<FAvaOutlinerActor>(MyActor);

// 创建 Item Proxy（如材质代理）
TSharedPtr<FAvaOutlinerItemProxy> Proxy = Outliner->GetOrCreateItemProxy<FAvaOutlinerMaterial>(ActorItem);
```

### 进阶用法：注册自定义图标覆盖

```cpp
// 来源: Public/IAvaOutlinerModule.h
IAvaOutlinerModule& Module = IAvaOutlinerModule::Get();

// 为特定 Outliner Item 类型注册图标覆盖
FAvaOutlinerActor& Customization = Module.RegisterOverriddenIcon<FAvaOutlinerActor, FMyActorIconCustomization>(
    MyClass::StaticClass()  // 传递给自定义图标的附加参数
);

// 取消注册
Module.UnregisterOverriddenIcon<FAvaOutlinerActor>(MyClass::StaticClass()->GetFName());
```

## Demo 示例

### 最小示例：自定义 Outliner Item Proxy

```cpp
// MyCustomItemProxy.h
#pragma once

#include "Item/AvaOutlinerItemProxy.h"

class FMyCustomItemProxy : public FAvaOutlinerItemProxy
{
public:
    FMyCustomItemProxy(IAvaOutliner& InOutliner, const FAvaOutlinerItemPtr& InParentItem)
        : FAvaOutlinerItemProxy(InOutliner, InParentItem)
    {
    }

    // 实现代理内容生成逻辑
    virtual void GetProxiedItems(
        const TSharedRef<IAvaOutlinerItem>& InParent,
        TArray<FAvaOutlinerItemPtr>& OutChildren,
        bool bInRecursive) override
    {
        // 根据父项目生成子项目
        // 例如：为某个 Actor 生成代表其材质引用的子节点
    }

    virtual FText GetDisplayName() const override
    {
        return NSLOCTEXT("MyPlugin", "CustomProxy", "Custom Proxy");
    }

    virtual FSlateIcon GetIcon() const override
    {
        return FSlateIcon(FAppStyle::GetAppStyleSetName(), "ClassIcon.Actor");
    }
};
```

```cpp
// MyCustomItemProxyFactory.h
#pragma once

#include "ItemProxies/Factories/AvaOutlinerItemProxyDefaultFactory.h"

// 使用默认工厂模板，优先级为 5
using FMyCustomItemProxyFactory = TAvaOutlinerItemProxyDefaultFactory<FMyCustomItemProxy, 5>;
```

```cpp
// MyModule.cpp - 注册
#include "IAvaOutlinerModule.h"

void FMyModule::StartupModule()
{
    FAvaOutlinerModule& OutlinerModule = FAvaOutlinerModule::Get();
    OutlinerModule.GetItemProxyRegistry().RegisterItemProxyWithDefaultFactory<FMyCustomItemProxy, 5>();
}

void FMyModule::ShutdownModule()
{
    if (IAvaOutlinerModule::IsLoaded())
    {
        FAvaOutlinerModule& OutlinerModule = FAvaOutlinerModule::Get();
        OutlinerModule.GetItemProxyRegistry().UnregisterItemProxyFactory<FMyCustomItemProxy>();
    }
}
```

## 模块依赖

Avalanche 是一个庞大的插件，有 44 个模块。以下是各子模块的**独特依赖**（已省略 Core/Engine/Slate 等标准依赖）。

| 模块 | 用途 |
|---|---|
| `AdvancedRenamer` | 批量重命名 Actor/项目 |
| `CustomDetailsView` | 自定义 Details 面板 |
| `DynamicMaterial` | 动态材质运行时创建 |
| `GeometryCache` | 几何缓存（顶点动画） |
| `GeometryScripting` | 几何脚本操作 |
| `MediaCompositing` | 媒体合成 |
| `MediaIOFramework` | 媒体 I/O 框架 |
| `MeshModelingToolsetExp` | 网格建模工具集（实验性） |
| `RemoteControl` | 远程控制 API |
| `SVGImporter` | SVG 文件导入 |
| `Text3D` | 3D 文本渲染 |
| `ActorModifierCore` | Actor 修改器核心框架 |
| `Sequencer` | 序列器集成（AvalanchePropertyAnimator 依赖） |

**注意**：以上是 `.uplugin` 声明的插件级依赖。各 Build.cs 内的模块级依赖（如 ProceduralMeshComponent、EditorScriptingUtilities 等）需参考各子模块的 Build.cs 文件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将场景设置和 Outliner 标签页移至独立编辑器组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | Rundown 页面模式下新增 MRQ 渲染分析统计 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 播出控制工具栏新增页面加载选项（全部/下一个/选中） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置以强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/解除关联的通知机制 |

### 维护评价

- **活跃维护**：该插件正处于高频迭代期，最近一周内有 5+ 次实质性功能更新
- **状态**：刚从 Experimental 迁移到 VirtualProduction 目录（2025-05-09），标志着 Epic 将其视为正式支持的核心虚拟制片工具
- **规模**：44 个模块、2060 个源文件，是 UE5 最大的插件之一，说明 Epic 对其投入了大量工程资源
- **依赖链复杂**：插件依赖 12+ 个其他插件，这意味着启用 Motion Design 需要一整套工具链支持
- **风险提示**：虽然刚迁移到正式目录，但代码量巨大且仍在快速迭代，API 可能尚未完全稳定
- **推荐使用**：✅ 推荐用于虚拟制片和广播场景，但注意追踪 breaking changes

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/motion-design-in-unreal-engine)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest)