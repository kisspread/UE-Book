# Inline Material Instance

> Allows creation and modification of materials within the property editor

| 属性 | 值 |
|---|---|
| 中文名 | 内联材质实例 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `InlineMaterialInstanceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/InlineMaterialInstance) | |

## 用途

该插件从 VirtualProductionUtilities 中拆分出来，提供在属性编辑器（Property Editor）中直接创建和修改材质实例的能力。核心解决的问题是：用户在编辑 Actor 属性时，无需跳转到材质编辑器，即可在细节面板中内联地管理动态材质实例——包括创建动态材质、修改参数、回退到原始材质、重置参数到默认值等操作。对于虚拟制片工作流中频繁调试材质参数的场景，这大幅减少了上下文切换。

## 使用场景

- 你在虚拟制片场景中需要快速调整 Actor 的材质参数（如颜色、粗糙度），不想每次都打开材质编辑器 → 用 InlineMaterialInstance
- 你需要在属性面板中一键创建动态材质实例，然后立即修改参数 → 用 InlineMaterialInstance
- 你需要将运行时修改的材质参数拷贝回原始材质实例 → 用 InlineMaterialInstance

## 蓝图用法

该插件主要通过编辑器 UI（Slate Widget）提供功能，不暴露蓝图节点。功能完全集成在细节面板中，用户通过按钮操作完成材质内联编辑。

### 核心界面操作

| 操作 | 说明 | 所在类 |
|---|---|---|
| 创建动态材质 | 在当前材质槽位创建动态材质实例 | `SMaterialDynamicView` |
| 回退材质 | 将材质槽位回退到原始材质 | `SMaterialDynamicView` |
| 重置参数 | 将参数重置为原始实例材质的默认值 | `SMaterialDynamicView` |
| 拷贝到原始材质 | 将修改后的参数拷贝回原始材质实例 | `SMaterialDynamicView` |
| 查看参数面板 | 在树状视图中展示并编辑动态材质参数 | `SMaterialDynamicParametersPanelWidget` |

### 使用方式

1. 选中一个拥有材质组件的 Actor
2. 在细节面板的材质属性区域，插件会提供内联的材质编辑界面
3. 点击「创建动态材质」按钮生成可编辑的动态材质实例
4. 在参数面板中直接修改材质参数（颜色、标量、纹理等）
5. 可随时「回退」或「重置」，也可将修改「拷贝回」原始材质

## C++ 用法

该插件以编辑器 Slate Widget 为主，C++ 用法集中在自定义 Widget 扩展场景。

### 头文件引入

```cpp
#include "Widgets/SMaterialDynamicWidgets.h"
#include "Widgets/SMaterialDynamicParametersPanelWidget.h"
```

### 基本用法

创建材质动态视图，用于在属性面板中内联编辑材质。

```cpp
// 来源: Source/InlineMaterialInstanceEditor/Private/Widgets/SMaterialDynamicWidgets.h

// 创建材质动态视图 Widget
TSharedRef<SMaterialDynamicView> MaterialView = SNew(SMaterialDynamicView);

// 在构造时传入材质项视图和当前组件
// SMaterialDynamicView::Construct 需要 FMaterialItemView 和 UActorComponent
TSharedPtr<FMaterialItemView> MaterialItemView = /* 获取材质项视图 */;
UActorComponent* Component = /* 获取当前组件 */;

MaterialView->Construct(
    SMaterialDynamicView::FArguments(),
    MaterialItemView.ToSharedRef(),
    Component
);
```

### 进阶用法

使用参数面板 Widget 展示并刷新动态材质实例的参数。

```cpp
// 来源: Source/InlineMaterialInstanceEditor/Private/Widgets/SMaterialDynamicParametersPanelWidget.h

// 创建参数面板
TSharedRef<SMaterialDynamicParametersPanelWidget> ParamPanel =
    SNew(SMaterialDynamicParametersPanelWidget)
    .InMaterialInstance(MyMaterialInstance);

// 后续更新实例时刷新参数面板
ParamPanel->UpdateInstance(NewMaterialInstance);
```

## Demo 示例

以下展示如何在自定义细节面板扩展中使用 `SMaterialDynamicView` 和 `SMaterialDynamicParametersPanelWidget`。

### InlineMaterialDemoWidget.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class UActorComponent;
class UMaterialInstance;
class SMaterialDynamicView;
class SMaterialDynamicParametersPanelWidget;

class SInlineMaterialDemoWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SInlineMaterialDemoWidget) {}
    SLATE_ARGUMENT(UActorComponent*, OwnerComponent)
    SLATE_ARGUMENT(UMaterialInstance*, TargetMaterial)
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<SMaterialDynamicView> DynamicView;
    TSharedPtr<SMaterialDynamicParametersPanelWidget> ParamsPanel;
};
```

### InlineMaterialDemoWidget.cpp

```cpp
#include "InlineMaterialDemoWidget.h"
#include "Widgets/SMaterialDynamicWidgets.h"
#include "Widgets/SMaterialDynamicParametersPanelWidget.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SSplitter.h"

void SInlineMaterialDemoWidget::Construct(const FArguments& InArgs)
{
    UActorComponent* Component = InArgs._OwnerComponent;
    UMaterialInstance* Material = InArgs._TargetMaterial;

    ChildSlot
    [
        SNew(SSplitter)
        .Orientation(Orient_Vertical)
        // 上半部分：材质动态视图（包含操作按钮）
        + SSplitter::Slot()
        [
            SAssignNew(DynamicView, SMaterialDynamicView)
            // 实际构造需要 FMaterialItemView，此处为简化示例
        ]
        // 下半部分：参数面板（参数树形列表）
        + SSplitter::Slot()
        [
            SAssignNew(ParamsPanel, SMaterialDynamicParametersPanelWidget)
            .InMaterialInstance(Material)
        ]
    ];
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MaterialList` | 材质列表数据结构，提供 FMaterialItemView 等类型 |

其余均为标准编辑器依赖（Slate、PropertyEditor、DetailCustomizations 等），无其他特殊依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-16 | `1843d288` | Virtual Production Inline Material Editor: Added max height to the parameter list to avoid SListView | 为参数列表添加最大高度限制，避免 SListView 布局溢出 |
| 2025-10-16 | `aeaf7289` | Added widget validation to the Inline Material Instance plugin | 添加 Widget 验证逻辑，增强插件健壮性 |
| 2024-08-28 | `fd8f5962` | [InlineMaterialInstance] Split feature from VirtualProductionUtilities | 从 VirtualProductionUtilities 中拆分为独立插件 |

### 维护评价

- **创建时间**：2024 年 8 月，属于较新的插件
- **更新频率**：最近一次功能性更新在 2025 年 10 月，集中修复了 UI 布局和 Widget 验证问题
- **维护状态**：活跃维护中，近期有实质性的 UI 改进
- **注意事项**：该插件标记为 **Beta**（`IsBetaVersion=true`）且 **默认未启用**（`Installed=false`），API 和行为可能会发生变化
- **推荐**：适合在虚拟制片工作流中尝试使用，但不建议在生产环境中作为核心依赖，需关注后续版本变动

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/InlineMaterialInstance)
- 官方文档（暂无）
- 原始拆分来源：`Engine/Plugins/VirtualProductionUtilities`