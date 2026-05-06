# Inline Material Instance

> Allows creation and modification of materials within the property editor

| 属性 | 值 |
|---|---|
| 中文名 | 内联材质实例 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `InlineMaterialInstanceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/InlineMaterialInstance) | |

## 用途

此插件允许在**属性编辑器**（Details Panel）中直接创建和修改材质的**动态实例**（Dynamic Material Instance），无需打开单独的材质编辑器。它从 `VirtualProductionUtilities` 拆分而来，专为虚拟制作工作流设计，使美术和设计师能在场景中快速调整材质参数，即时查看效果。

核心功能包括：
- 为材质插槽添加“创建动态材质实例”按钮
- 提供动态材质参数面板，列出所有可调参数
- 支持重置参数、还原为原始材质、复制参数到原始材质实例

## 使用场景

- **虚拟制片**：场地面板中频繁调整材质颜色、粗糙度、发光等属性，热切换不需要重新编译。
- **快速调参**：在关卡蓝图中或直接选中 Actor 后，在细节面板实时修改材质参数，适合调试和迭代。
- **设计师友好**：无需打开材质编辑器界面，直接在属性面板完成所有操作，降低使用门槛。

## 蓝图用法

此插件为**纯编辑器扩展**，不提供任何 `BlueprintCallable` 函数。所有功能通过 Slate UI 按钮和鼠标交互完成，无法在蓝图图表中调用。

## C++ 用法

### 头文件引入

```cpp
#include "Widgets/SMaterialDynamicView.h"
#include "Widgets/SMaterialDynamicParametersPanelWidget.h"
```

### 基本用法

这两个 Widget 可用于自定义编辑器界面，例如添加到材质编辑器或资产查看器中。

**创建动态材质参数面板：**

```cpp
// 在 Slate 界面构建时创建
SAssignNew(DynamicParametersPanel, SMaterialDynamicParametersPanelWidget)
    .InMaterialInstance(MyMaterialInstance);

// 当材质实例变更时调用
DynamicParametersPanel->UpdateInstance(NewMaterialInstance);
```

**为材质插槽添加动态视图（配合 FMaterialItemView 使用）：**

```cpp
// 假设你已有 FMaterialItemView 的引用和当前组件
TSharedRef<SMaterialDynamicView> DynamicView = 
    SNew(SMaterialDynamicView, MaterialItemView.ToSharedRef(), CurrentComponent);
// 将此 Widget 插入到材质列表的对应条目中即可显示按钮
```

### 进阶用法

`SMaterialDynamicView` 会自动根据当前材质类型显示不同的操作按钮：
- 如果材质是 `UMaterialInstanceDynamic`，显示“重置参数”和“还原为原始材质”按钮
- 如果材质是普通材质实例，显示“创建动态实例”按钮
- 支持复制动态参数到原始静态实例

`SMaterialDynamicParametersPanelWidget` 内部使用 `IPropertyRowGenerator` 生成参数控件树，并可刷新。

> **源码来源**：`Source/InlineMaterialInstanceEditor/Private/Widgets/SMaterialDynamicWidgets.h`、`Source/InlineMaterialInstanceEditor/Private/Widgets/SMaterialDynamicParametersPanelWidget.h`

## Demo 示例

以下示例展示如何在自定义编辑器模块的 Slate 组件中使用内联材质参数面板（需要项目依赖此插件）。

**MyCustomWidget.h**
```cpp
#pragma once
#include "Widgets/SCompoundWidget.h"
#include "Widgets/SMaterialDynamicParametersPanelWidget.h"

class UMaterialInstance;
class SMaterialDynamicParametersPanelWidget;

class SMyCustomWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyCustomWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);
    void SetMaterialInstance(UMaterialInstance* NewInstance);

private:
    TSharedPtr<SMaterialDynamicParametersPanelWidget> ParameterPanel;
};
```

**MyCustomWidget.cpp**
```cpp
#include "MyCustomWidget.h"
#include "UMG.h"

void SMyCustomWidget::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        [
            SAssignNew(ParameterPanel, SMaterialDynamicParametersPanelWidget)
            .InMaterialInstance(nullptr)
        ]
    ];
}

void SMyCustomWidget::SetMaterialInstance(UMaterialInstance* NewInstance)
{
    if (ParameterPanel.IsValid())
    {
        ParameterPanel->UpdateInstance(NewInstance);
    }
}
```

> 实际使用时需确保 `InlineMaterialInstanceEditor` 模块已启用，并在 Build.cs 中添加依赖。

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖 | 仅标准引擎公共依赖（Core, Slate, PropertyEditor, MaterialList 等） |

> 此插件需要的依赖均在引擎核心和编辑器模块中，使用前确保项目启用了 `Editor` 模块类型。

## 维护状态

### 近期更新

- 2025-10-16 `9df31589` Virtual Production Inline Material Editor: Added max height to the parameter list to avoid SListView overflow
- 2025-10-16 `2e1d613f` Added widget validation to the Inline Material Instance plugin
- 2024-08-28 `fd8f5962` [InlineMaterialInstance] Split feature from VirtualProductionUtilities

### 维护评价

插件创建于 2024 年 8 月，目前仍处于**实验性**阶段（`IsBetaVersion=true`），但最近两次提交均在 2025 年 10 月，表明项目仍在**活跃维护**。更新内容为功能增强（限制参数列表高度）和稳定性改进（添加 Widget 验证），无明显已知问题。由于功能稳定且针对特定工作流，可以安全使用，但请留意其实验性标签，未来 API 可能存在变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/InlineMaterialInstance)
- [官方文档](https://docs.unrealengine.com/5.7/ProductionPipelines/VirtualProduction/)（此为虚拟制作文档，插件功能内联其中）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/InlineMaterialInstance/Tests)（未直接提供，可通过源码路径查找）