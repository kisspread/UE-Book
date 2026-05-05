# DMX Pixel Mapping

> Tools set for map LED digital pixel strip or fixture arrays regardless of shape or size

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `DMXPixelMappingBlueprintGraph` (Runtime), `DMXPixelMappingCore` (Runtime), `DMXPixelMappingEditor` (Runtime), `DMXPixelMappingEditorWidgets` (Runtime), `DMXPixelMappingRenderer` (Runtime), `DMXPixelMappingRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping) | |

## 用途

DMX Pixel Mapping 插件提供了一套完整的工具集，用于将 DMX 信号（来自灯光控制台或软件）精确地映射到各种形状和尺寸的 LED 数字像素条或灯具阵列上。它解决了在虚拟制作（Virtual Production）、现场演出、建筑照明等场景中，需要将复杂的灯光控制信号驱动到大量独立可控的 LED 像素点的核心问题。该插件允许用户在 Unreal Engine 中直观地设计像素布局、分配 DMX 地址，并实时预览灯光效果，是连接数字灯光控制与物理 LED 设备的关键桥梁。

## 使用场景

-   **虚拟制作 LED 墙**：你需要将虚拟场景的灯光或视频内容，通过 DMX 协议输出到构成 LED 墙的成千上万个像素点上。
-   **现场演出灯光设计**：你在设计一个包含复杂 LED 矩阵、像素条或异形灯具的舞台灯光秀，需要在引擎中预编程和模拟效果。
-   **建筑立面照明**：你需要控制覆盖在建筑表面的大量 LED 灯具，实现动态的灯光动画或信息显示。
-   **任何需要将 DMX 信号映射到二维或三维像素阵列的场景**。

## 蓝图用法

**重要提示**：根据提供的头文件（如 `SDMXPixelMappingComponentBox.h`），本模块 (`DMXPixelMappingEditorWidgets`) 中的 Slate 控件类已在 UE 5.1 中被标记为 `UE_DEPRECATED`。官方注释指出：“Pixel Mapping Editor Widgets are no longer supported and to be implemented per view. See SDMXPixelMappingOutputComponent for an example.” 这意味着这些旧的编辑器控件已不再推荐使用，新的实现方式应参考 `SDMXPixelMappingOutputComponent` 等视图类。因此，以下列出的节点主要用于理解旧有 API，**不建议在新项目中使用**。

### 核心节点（已废弃）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetLocalSize` | 设置组件控件的本地尺寸 | `SDMXPixelMappingComponentBox` |
| `SetIDText` | 设置组件上显示的 ID 文本 | `SDMXPixelMappingComponentBox` |
| `SetBorderColor` | 设置组件边框的颜色 | `SDMXPixelMappingComponentBox` |
| `RebuildGrid` | 根据参数重建网格布局 | `SDMXPixelMappingScreenComponentBox` |
| `AddToCanvas` | 将组件控件添加到画布中 | `FDMXPixelMappingComponentWidget` |
| `SetPosition` | 设置组件在画布中的位置 | `FDMXPixelMappingComponentWidget` |
| `SetSize` | 设置组件及其标签的尺寸 | `FDMXPixelMappingComponentWidget` |
| `SetLabelText` | 设置组件的标签文本 | `FDMXPixelMappingComponentWidget` |

### 使用示例（蓝图描述 - 已废弃）

1.  **创建组件控件**：在蓝图中创建一个 `FDMXPixelMappingComponentWidget` 对象。它内部会自动创建并管理一个 `SDMXPixelMappingComponentBox`（显示组件边框和ID）和一个 `SDMXPixelMappingComponentLabel`（显示标签文本）。
2.  **添加到画布**：获取或创建一个 `SConstraintCanvas`（Slate 画布控件），然后调用 `AddToCanvas` 节点，将组件控件添加到画布中，并指定 Z 轴顺序。
3.  **设置属性**：使用 `SetPosition` 设置组件在画布上的坐标，使用 `SetSize` 设置其大小，使用 `SetLabelText` 和 `SetIDText` 设置显示的文本，使用 `SetColor` 设置颜色。
4.  **对于网格组件**：如果使用 `SDMXPixelMappingScreenComponentBox`，可以通过 `RebuildGrid` 节点，传入一个 `FDMXPixelMappingScreenComponentGridParams` 结构体来定义网格的行列数、像素格式、地址显示等参数，从而快速生成一个像素网格预览。

## C++ 用法

**重要提示**：以下代码示例基于已废弃的 `DMXPixelMappingEditorWidgets` 模块中的类。它们展示了旧的编辑器控件用法，仅供参考。新的开发应遵循 Epic 在 UE 5.1+ 中推荐的新架构。

### 头文件引入

```cpp
#include "SDMXPixelMappingComponentBox.h"
#include "SDMXPixelMappingComponentLabel.h"
#include "DMXPixelMappingComponentWidget.h"
#include "SDMXPixelMappingScreenComponentBox.h"
```

### 基本用法

创建一个简单的组件控件并设置其属性。

```cpp
// 来源：基于 SDMXPixelMappingComponentBox.h 和 DMXPixelMappingComponentWidget.h 的 API 推断

// 1. 创建一个组件控件包装器
TSharedPtr<FDMXPixelMappingComponentWidget> MyComponentWidget = MakeShared<FDMXPixelMappingComponentWidget>();

// 2. 假设我们有一个 Slate 画布 (SConstraintCanvas)
TSharedRef<SConstraintCanvas> MyCanvas = SNew(SConstraintCanvas);

// 3. 将组件添加到画布
MyComponentWidget->AddToCanvas(MyCanvas, 0.0f); // ZOrder = 0

// 4. 设置组件属性
MyComponentWidget->SetPosition(FVector2D(100.f, 50.f));
MyComponentWidget->SetSize(FVector2D(200.f, 150.f));
MyComponentWidget->SetLabelText(FText::FromString(TEXT("My Fixture")));
MyComponentWidget->SetIDVisibility(true);
MyComponentWidget->SetColor(FLinearColor::Green);
```

### 进阶用法

创建一个像素网格屏幕组件，并动态更新其参数。

```cpp
// 来源：基于 SDMXPixelMappingScreenComponentBox.h 的 API 推断

// 1. 创建屏幕组件控件
TSharedPtr<SDMXPixelMappingScreenComponentBox> ScreenBox = SNew(SDMXPixelMappingScreenComponentBox)
    .NumXCells(10)
    .NumYCells(5)
    .Distribution(EDMXPixelMappingDistribution::TopLeftToRight)
    .PixelFormat(EDMXCellFormat::PF_RGB)
    .bShowAddresses(true)
    .bShowUniverse(false)
    .LocalUniverse(1)
    .StartAddress(1);

// 2. 将其包装在 FDMXPixelMappingComponentWidget 中以便管理
TSharedPtr<FDMXPixelMappingComponentWidget> ScreenWidget = MakeShared<FDMXPixelMappingComponentWidget>(ScreenBox);

// 3. 添加到画布并设置位置
ScreenWidget->AddToCanvas(MyCanvas, 1.0f);
ScreenWidget->SetPosition(FVector2D(300.f, 100.f));

// 4. 动态更新网格参数
FDMXPixelMappingScreenComponentGridParams NewGridParams;
NewGridParams.NumXCells = 20;
NewGridParams.NumYCells = 10;
NewGridParams.StartAddress = 17; // 从地址17开始
NewGridParams.bShowAddresses = true;
NewGridParams.bShowUniverse = true;
NewGridParams.LocalUniverse = 2;

ScreenBox->RebuildGrid(NewGridParams);
```

## Demo 示例

一个最小的、展示如何创建并使用已废弃的 `FDMXPixelMappingComponentWidget` 的示例。

**MyPixelMappingWidgetDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class FDMXPixelMappingComponentWidget;
class SConstraintCanvas;

class SMyPixelMappingWidgetDemo : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyPixelMappingWidgetDemo) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<FDMXPixelMappingComponentWidget> DemoComponent;
    TSharedPtr<SConstraintCanvas> DemoCanvas;
};
```

**MyPixelMappingWidgetDemo.cpp**
```cpp
#include "MyPixelMappingWidgetDemo.h"
#include "DMXPixelMappingComponentWidget.h"
#include "Widgets/Layout/SConstraintCanvas.h"

void SMyPixelMappingWidgetDemo::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SAssignNew(DemoCanvas, SConstraintCanvas)
    ];

    // 创建一个组件控件
    DemoComponent = MakeShared<FDMXPixelMappingComponentWidget>();

    // 将其添加到画布
    DemoComponent->AddToCanvas(DemoCanvas.ToSharedRef(), 0.0f);

    // 设置基本属性
    DemoComponent->SetPosition(FVector2D(50.f, 50.f));
    DemoComponent->SetSize(FVector2D(150.f, 100.f));
    DemoComponent->SetLabelText(FText::FromString(TEXT("Demo Pixel")));
    DemoComponent->SetIDVisibility(true);
    DemoComponent->SetColor(FLinearColor::Blue);
}
```

## 模块依赖

基于 `DMXPixelMappingEditorWidgets` 模块的常见依赖模式推断。要使用此插件的特定功能，你的模块可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `DMXPixelMappingCore` | 像素映射的核心数据结构和逻辑 |
| `DMXRuntime` | DMX 协议运行时支持 |
| `DMXBlueprintGraph` | DMX 相关的蓝图节点支持 |
| `Slate`, `SlateCore` | 用于构建编辑器 UI 控件 |

## 维护状态

### 近期更新

```
- ed12aec9a262 DMX: Remove any uses of FORCEINLINE, replace with inline where appropriate
- ba2aa76a2b3e Fixing compile errors after enabling TObjectPtr's GC barrier
- bbc37aa2f5e6 [Engine/Plugins] * Another batch iwyu updates to reduce number of includes used in files
```
*   `ed12aec9a262`: 代码规范清理，将 `FORCEINLINE` 替换为 `inline`。
*   `ba2aa76a2b3e`: 修复了启用 `TObjectPtr` GC 屏障后产生的编译错误。
*   `bbc37aa2f5e6`: 批量更新头文件包含（IWYU），以减少不必要的依赖。

### 维护评价

该插件创建于 2020 年，已有约 5 年历史。从最近的提交记录看，更新主要集中在**编译修复、代码规范和依赖清理**等维护性工作上，没有发现新功能的添加。特别是 `DMXPixelMappingEditorWidgets` 模块中的核心控件类在 UE 5.1 中已被标记为废弃，这表明 Epic 可能正在重构或已经用新的实现方式替代了这部分旧代码。

**综合评价**：插件整体处于**维护状态**，核心功能（如 `DMXPixelMappingRuntime`, `DMXPixelMappingRenderer`）可能仍然稳定可用，但编辑器 UI 部分（`DMXPixelMappingEditorWidgets`）已明确废弃。对于新项目，应优先使用 UE 5.1+ 版本，并关注 Epic 官方文档或示例中关于新像素映射编辑器视图（如 `SDMXPixelMappingOutputComponent`）的用法。不建议在新代码中依赖本文档中描述的已废弃的编辑器控件 API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping/Tests)