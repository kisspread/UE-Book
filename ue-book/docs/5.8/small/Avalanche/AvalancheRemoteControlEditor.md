# Avalanche (Motion Design)

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheMedia` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), 等共 44 个模块 |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche（Motion Design）是 UE5 虚拟制作流程中的**动态设计与合成工具集**，面向广播级实时图形（broadcast graphics）和虚拟场景设计场景。它将原本分散在 Experimental 目录下的多个插件（ActorModifier、ClonerEffector、Material Designer、GeometryMask、PropertyAnimator、StormSync 等）统一整合为一个完整的虚拟制作解决方案。

该插件解决的核心问题：
- **合成与设计**：提供类似 After Effects 的图层式合成工作流，在 UE5 关卡编辑器内直接完成动态图形设计
- **广播级输出**：通过集成 Media IO 和 Movie Render Queue，支持从编辑器直接输出到广播设备或渲染最终序列
- **远程控制**：与 Remote Control 系统深度集成，支持通过外部控制器实时操纵场景参数
- **场景资产化**：通过 SceneRig、SceneTree 等系统将复杂的场景组合打包为可复用的资产

## 使用场景

- 你在做电视节目的实时图形包装 → 用 Motion Design 设计动态标题、lower third 等图形元素
- 你需要为虚拟演播室设计复杂的场景过渡效果 → 用 AvalancheTransition 和 PropertyAnimator
- 你要将 UE5 场景通过 NDI/SDI 输出到转播系统 → 用 AvalancheMedia 的媒体输出能力
- 你需要通过硬件调光台或远程设备控制场景参数 → 用 AvalancheRemoteControl 集成
- 你要批量创建/管理大量相似对象（如粒子阵列、广告牌矩阵）→ 用 ClonerEffector 和 AvalancheEffectors

## 蓝图用法

本模块（AvalancheRemoteControlEditor）主要提供编辑器端的 Remote Control 集成，核心功能以属性定制和大纲菜单形式暴露，而非传统蓝图节点。

### 核心功能

| 功能 | 说明 | 所在类 |
|---|---|---|
| RC 控制器选择器 | 属性面板中为 RemoteControl 控制器 ID 提供下拉选择 UI | `SAvaRCControllerPicker` |
| 追踪器组件展示 | 在 Motion Design 大纲中显示 RemoteControl 追踪器组件 | `FAvaOutlinerRCTrackerComponent` |
| 大纲右键菜单 | 为含 RC 组件的 Actor 添加"取消暴露属性"、"添加/移除追踪器"菜单项 | `FAvaOutlinerRCComponentsContextMenu` |
| 控制器 ID 属性定制 | 自动为 `FAvaRCControllerId` 类型属性应用自定义编辑器 UI | `FAvaRCControllerIdCustomization` |

### 使用示例（编辑器操作）

1. **在大纲中管理 Remote Control 追踪器**：选中一个 Actor → 右键 → 菜单中出现 Remote Control 相关选项（添加追踪器 / 移除追踪器 / 取消暴露所有属性）
2. **选择 RC 控制器**：在含 `FAvaRCControllerId` 属性的细节面板中，会显示一个下拉框，列出当前关卡中可用的 Remote Control 控制器名称

## C++ 用法

### 头文件引入

```cpp
#include "AvalancheRemoteControlEditorModule.h"
```

### 基本用法：属性类型定制注册

```cpp
// 注册自定义属性类型布局（在模块 StartupModule 中自动执行）
// 来源: Private/AvalancheRemoteControlEditorModule.h

void FAvalancheRemoteControlEditorModule::RegisterCustomizations()
{
    // 为 FAvaRCControllerId 类型注册自定义属性编辑器
    CustomPropertyTypeLayouts.Add(FAvaRCControllerId::StaticStruct()->GetFName());

    PropertyModule.RegisterCustomPropertyTypeLayout(
        FAvaRCControllerId::StaticStruct()->GetFName(),
        FOnGetPropertyTypeCustomizationInstance::CreateStatic(
            &FAvaRCControllerIdCustomization::MakeInstance
        )
    );
}
```

### 进阶用法：扩展大纲项代理

```cpp
// 为 RemoteControl Tracker Component 创建大纲代理项
// 来源: Private/Outliner/AvaOutlinerRCTrackerComponentProxy.h

// 在大纲注册时，为 URemoteControlTrackerComponent 创建代理
FAvaOutlinerRCTrackerComponentProxy Proxy(Outliner, ParentItem);

// 获取实际的追踪器组件
URemoteControlTrackerComponent* Tracker = Proxy.GetTrackerComponent();

// 监听被追踪 Actor 的变化
// OnTrackedActorsChanged 会在 Actor 被追踪/取消追踪时触发
```

### 进阶用法：上下文菜单扩展

```cpp
// 扩展大纲右键菜单，为含 RC 组件的 Actor 添加操作
// 来源: Private/Outliner/AvaOutlinerRCComponentsContextMenu.h

// 注册菜单扩展
UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("AvalancheOutliner.ContextMenu");
Menu->AddDynamicSection("RemoteControlComponents",
    FNewToolMenuDelegate::CreateStatic(
        &FAvaOutlinerRCComponentsContextMenu::OnExtendOutlinerContextMenu
    )
);

// 菜单项执行示例：取消暴露选中 Actor 的所有 RC 属性
FAvaOutlinerRCComponentsContextMenu::ExecuteUnexposeAllPropertiesAction(SelectedActors);
```

## Demo 示例

```cpp
// MyRCWidget.h
#pragma once

#include "Widgets/SCompoundWidget.h"
#include "AvalancheRemoteControlEditorModule.h"

// 自定义 Slate 控件，嵌入 RC 控制器选择器
class SMyRCConfigWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyRCConfigWidget) {}
        SLATE_ARGUMENT(TSharedPtr<IPropertyHandle>, ControllerIdProperty)
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs)
    {
        ChildSlot
        [
            SNew(SVerticalBox)
            + SVerticalBox::Slot()
            .AutoHeight()
            .Padding(4.0f)
            [
                SNew(STextBlock)
                .Text(FText::FromString(TEXT("Remote Control Controller")))
            ]
            + SVerticalBox::Slot()
            .AutoHeight()
            .Padding(4.0f)
            [
                // 使用插件提供的控制器选择器控件
                SNew(SAvaRCControllerPicker, InArgs._ControllerIdProperty)
            ]
        ];
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RemoteControl` | Unreal Remote Control 核心运行时，提供控制器暴露与追踪机制 |
| `RemoteControlAPI` | Remote Control 的编程接口层 |
| `AvalancheOutliner` | Motion Design 专用大纲系统，提供自定义大纲项代理框架 |
| `AvalancheCore` | Motion Design 核心库，定义通用类型与工具函数 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将场景设置和大纲标签页移入独立分组，优化编辑器布局 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 使用 Rundown 页面设置时新增 MRQ 分析数据采集 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 演播控制工具栏新增页面加载选项（全部/下一个/选中） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/断开通知逻辑，减少重复代码 |

### 维护评价

Motion Design 是 Epic 正在**活跃维护**的虚拟制作核心工具。该插件从 Experimental 迁移至 VirtualProduction 目录仅约一年，但代码量已达 2060 个源文件（44 个模块），发展极为迅速。近期更新频率很高（2026 年 5 月有多次密集提交），涵盖功能新增、UI 优化和性能改进。

**推荐使用**：对于虚拟制作、广播图形、实时合成类项目，这是 Epic 官方推荐的解决方案。注意该插件依赖链较长（Remote Control、Text3D、SVG Importer 等），启用时需确保依赖插件均已就绪。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest)