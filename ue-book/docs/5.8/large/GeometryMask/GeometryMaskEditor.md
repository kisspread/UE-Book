# Geometry Mask

> （.uplugin Description 为空）

| 属性 | 值 |
|---|---|
| 中文名 | 几何遮罩 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产） |
| 模块 | `GeometryMask` (Runtime), `GeometryMaskEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/GeometryMask) | |

## 用途

GeometryMask 是一套基于几何体的遮罩系统，专为虚拟制作（Virtual Production）和 Motion Design 工作流设计。

该插件解决的核心问题是：**如何使用几何体形状定义 Alpha 遮罩，用于虚拟与真实元素的合成（Compositing）**。

系统以"画布"（Canvas）为核心概念，每张画布由一个 `FGeometryMaskCanvasId` 标识，底层使用 `UTextureRenderTarget2DArray` 存储遮罩数据（通过切片索引区分不同遮罩）。写入端（Writer）将几何体渲染为遮罩，读取端（Reader）在材质中采样遮罩进行合成。编辑器模块提供了可视化预览工具和控制台命令，方便调试。

**注意**：该插件最初位于 `Engine/Plugins/Experimental/` 目录，于 2025-05 随 Motion Design 体系一起迁移至 `Engine/Plugins/VirtualProduction/`。5.8 版本中已废弃颜色通道（Color Channel）管理功能。

## 使用场景

- 你在做虚拟制作，需要用 3D 几何体遮挡或裁剪虚拟画面 → 用 GeometryMask
- 你在 Motion Design 中需要基于几何形状的遮罩效果 → 用 GeometryMask
- 你需要多个遮罩画布，分别控制不同区域的合成 → 用多个 GeometryMaskCanvas
- 你需要在编辑器中实时预览遮罩效果 → 使用 GeometryMaskEditor 的可视化工具

## 蓝图用法

核心蓝图 API 位于 Runtime 模块（`GeometryMask`），编辑器模块主要提供 Slate 控件和控制台命令。基于头文件分析，编辑器模块的公开 API 主要是 C++ 侧的 Slate 控件，不暴露蓝图节点。

### 核心节点

以下为从编辑器模块头文件中提取的公开 Slate 控件：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCanvasId` | 设置预览目标画布 ID | `SGeometryMaskCanvasPreview` |
| `GetCanvasId` | 获取当前引用的画布 ID | `SGeometryMaskCanvasPreview` |
| `GetCanvasName` | 获取当前画布名称 | `SGeometryMaskCanvasPreview` |
| `SetInvert` | 设置是否反转遮罩显示 | `SGeometryMaskCanvasPreview` |
| `SetSolidBackground` | 设置是否使用纯色背景 | `SGeometryMaskCanvasPreview` |
| `SetOpacity` | 设置整体不透明度乘数 | `SGeometryMaskCanvasPreview` |
| `SetPaddingFrameVisiblity` | 设置内边距框是否可见 | `SGeometryMaskCanvasPreview` |
| `GetCanvas` | 获取当前引用的 UGeometryMaskCanvas 对象 | `SGeometryMaskCanvasPreview` |
| `GetAspectRatio` | 获取画布宽高比 | `SGeometryMaskCanvasPreview` |

### 使用示例（蓝图描述）

在编辑器 C++ 中创建画布预览控件：

```cpp
// 创建画布预览控件并指定画布 ID
SNew(SGeometryMaskCanvasPreview)
    .CanvasId(MyCanvasId)
    .Invert(false)
    .SolidBackground(true)
    .Opacity(1.0f)
```

编辑器控制台命令（在编辑器控制台中输入）：
- 显示可视化器标签页
- 暂停遮罩系统
- 冲刷（Flush）遮罩数据

## C++ 用法

### 头文件引入

```cpp
#include "GeometryMaskCanvasPreview.h"  // SGeometryMaskCanvasPreview
#include "GeometryMaskTypes.h"          // FGeometryMaskCanvasId
```

### 基本用法 — 画布预览控件

基于 `Public/Widgets/SGeometryMaskCanvasPreview.h`：

```cpp
// 创建一个画布预览 Slate 控件
TSharedRef<SGeometryMaskCanvasPreview> PreviewWidget =
    SNew(SGeometryMaskCanvasPreview)
        .CanvasId(FGeometryMaskCanvasId(TEXT("MyCanvas")))
        .Invert(false)
        .SolidBackground(true)
        .Opacity(1.0f);

// 动态切换画布
PreviewWidget->SetCanvasId(FGeometryMaskCanvasId(TEXT("AnotherCanvas")));

// 设置显示选项
PreviewWidget->SetInvert(true);
PreviewWidget->SetOpacity(0.5f);
PreviewWidget->SetSolidBackground(false);
PreviewWidget->SetPaddingFrameVisiblity(true);
```

### 基本用法 — 画布列表 ViewModel

基于 `Private/ViewModels/GMECanvasListViewModel.h`：

```cpp
// 创建画布列表 ViewModel（MVVM 模式）
TSharedRef<FGMECanvasListViewModel> CanvasListVM = FGMECanvasListViewModel::Create();

// 监听变更事件
CanvasListVM->OnChanged().AddLambda([this]()
{
    // 刷新 UI，获取最新的画布列表
    TArray<TSharedPtr<IGMETreeNodeViewModel>> Children;
    CanvasListVM->GetChildren(Children);
    // 更新列表显示...
});
```

### 进阶用法 — 画布项 ViewModel

基于 `Private/ViewModels/GMECanvasItemViewModel.h`：

```cpp
// 创建单个画布项 ViewModel，需要传入 UGeometryMaskCanvas 的弱引用
TSharedPtr<FGMECanvasItemViewModel> CanvasItemVM = 
    FGMECanvasItemViewModel::Create(WeakCanvas);

// 获取画布信息
FGeometryMaskCanvasId Id = CanvasItemVM->GetCanvasId();
FName Name = CanvasItemVM->GetCanvasName();
const FText& Info = CanvasItemVM->GetCanvasInfo();
const UTexture* Texture = CanvasItemVM->GetCanvasTexture();
float MemoryMB = CanvasItemVM->GetMemoryUsage();
```

## Demo 示例

```cpp
// GeometryMaskDemoWidget.h
#pragma once

#include "Widgets/SCompoundWidget.h"
#include "GeometryMaskTypes.h"

class SGeometryMaskCanvasPreview;

class SGeometryMaskDemoWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SGeometryMaskDemoWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<SGeometryMaskCanvasPreview> CanvasPreview;
};
```

```cpp
// GeometryMaskDemoWidget.cpp
#include "GeometryMaskDemoWidget.h"
#include "Widgets/SGeometryMaskCanvasPreview.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Text/STextBlock.h"

void SGeometryMaskDemoWidget::Construct(const FArguments& InArgs)
{
    FGeometryMaskCanvasId DemoCanvasId = FGeometryMaskCanvasId(TEXT("DemoCanvas"));

    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(4.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("Geometry Mask Preview")))
        ]
        + SVerticalBox::Slot()
        .FillHeight(1.0f)
        .Padding(4.0f)
        [
            SNew(SBox)
            .MinDesiredWidth(256.0f)
            .MinDesiredHeight(256.0f)
            [
                SAssignNew(CanvasPreview, SGeometryMaskCanvasPreview)
                    .CanvasId(DemoCanvasId)
                    .Invert(false)
                    .SolidBackground(true)
                    .Opacity(1.0f)
                    .PaddingFrameVisibility(true)
            ]
        ]
    ];
}
```

## 模块依赖

由于 Build.cs 内容未提供，基于头文件 include 分析，该插件依赖以下模块：

| 模块 | 用途 |
|---|---|
| `GeometryMask` | Runtime 核心模块，提供 UGeometryMaskCanvas 等运行时类型 |
| `Slate`, `SlateCore` | Slate 控件框架（编辑器 UI） |
| `UMG` | UMG 相关支持 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `11b5ce93` | Motion Design: clarified masking deprecation messages + exposed GetRenderTargetSliceIndex so that c | 澄清遮罩废弃提示信息，并公开 GetRenderTargetSliceIndex 接口 |
| 2026-04-29 | `3b158778` | Motion Design: fixed issue where a mask input modifier primitives remains hidden even after removing | 修复遮罩输入修改器图元在移除后仍然隐藏的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup | 在即将到来的头文件清理前补充 include |
| 2026-03-16 | `386c6e0b` | Motion Design: added geometry mask writer to decouple masking logic from actor component. Mask Write | 新增几何遮罩写入器，将遮罩逻辑从 Actor 组件中解耦 |

### 维护评价

- **创建时间**：2025-05-09（约 1 年前），从 Experimental 迁移至 VirtualProduction
- **更新频率**：最近 2 个月内有 5 次提交，更新频繁，属于**活跃维护**状态
- **近期重点**：正在解耦遮罩写入逻辑（Mask Writer）、废弃旧的颜色通道系统、暴露新 API（GetRenderTargetSliceIndex）
- **架构演进**：正在从 Actor Component 内嵌逻辑转向独立的 Writer/Reader 解耦架构，属于积极重构期
- **已知限制**：颜色通道功能已在 5.8 废弃，相关接口标记为 `UE_DEPRECATED`
- **推荐程度**：✅ 推荐使用。作为 Virtual Production 核心工具链的一部分，由 Epic 官方维护，活跃度高

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/GeometryMask)
- 官方文档（无，.uplugin DocsURL 为空）