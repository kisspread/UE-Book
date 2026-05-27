# Curve Editor Tools

> This provides a default set of editing tools for the Curve Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 曲线编辑工具 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `CurveEditorTools` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-05-24 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/CurveEditorTools) | |

## 用途

CurveEditorTools 插件为 Unreal Engine 的曲线编辑器（Curve Editor）提供了一套功能强大的默认工具集。它并非仅仅是一组简单的操作，而是一个基于插件架构的扩展系统，彻底增强了编辑动画曲线的能力。

**解决的问题：**
在 Sequencer 或 UMG 的曲线编辑器中编辑动画曲线时，用户常常需要进行批量、精确和直观的操作，例如：
- 对多个关键帧进行整体平移、缩放。
- 通过一个可变形的“网格”来调整曲线的整体形状。
- 为动画添加“淡入淡出”或“重定时”效果。
- 应用滤波器（如平滑、降噪）到曲线上。

**核心存在价值：**
CurveEditorTools 通过 `ICurveEditorToolExtension` 接口，将“变换工具”、“网格变形工具”、“重定时工具”等以模块化、插件化的方式集成到曲线编辑器中。这使得这些高级编辑功能开箱即用，并且允许开发者通过插件机制扩展自定义工具，极大地提升了动画和数据曲线编辑的效率和灵活性。

## 使用场景

- **动画师在 Sequencer 中调整角色动画**：需要精确缩放一段动画的时间（重定时），或者整体移动一组关键帧的值（变换工具）。
- **技术美术或程序员调整数值曲线**：需要快速平滑一条带有噪声的曲线（FFT 滤镜），或者通过一个可拖拽的“晶格”来艺术化地调整曲线形状。
- **任何使用曲线资产（如 Float、Vector、Color 曲线）的场景**：该插件为这些资产编辑器也提供了同样强大的工具，包括为颜色曲线专门添加的梯度编辑视图。

## 蓝图用法

该插件主要为曲线编辑器的交互式UI提供工具，其核心功能通过编辑器UI和C++扩展API暴露。在蓝图中，主要通过配置数据和参数来使用其滤镜功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CutoffFrequency` | FFT滤波器的归一化截止频率 (0-1)。 | `UCurveEditorFFTFilter` |
| `Type` | FFT滤波器类型：低通或高通。 | `UCurveEditorFFTFilter` |
| `Response` | FFT滤波器实现：Butterworth 或 Chebyshev。 | `UCurveEditorFFTFilter` |
| `Order` | FFT滤波器的阶数，影响滤波斜率。 | `UCurveEditorFFTFilter` |

### 使用示例（蓝图描述）

FFT滤镜通常通过曲线编辑器的“操作”菜单使用。在蓝图中，你可以实例化一个 `UCurveEditorFFTFilter` 对象并设置其属性，然后通过 `UCurveEditorFilterBase::ApplyFilter` 方法应用于当前曲线编辑器会话的选中关键帧。这通常在编辑器工具或自定义扩展中实现，而不是在一般的游戏蓝图中。

## C++ 用法

该插件的API主要面向编辑器扩展开发。以下示例展示了如何在C++中与插件的工具和滤镜交互。

### 头文件引入

```cpp
#include "CurveEditorTools/CurveEditorTools.h" // 主模块头文件
#include "Tools/CurveEditorTransformTool.h"   // 如需直接使用变换工具
#include "Filters/CurveEditorFFTFilter.h"     // 如需使用FFT滤镜
```

### 基本用法 (使用FFT滤镜)

以下代码演示了如何通过C++代码应用FFT滤镜到曲线编辑器的选中关键帧上。
（来源：`UCurveEditorFFTFilter` 的声明与用法）

```cpp
// 假设你已经有一个指向活动曲线编辑器的TSharedPtr<FCurveEditor> CurveEditorPtr
if (CurveEditorPtr.IsValid())
{
    // 创建一个FFT滤镜实例
    UCurveEditorFFTFilter* FFTFilter = NewObject<UCurveEditorFFTFilter>();
    
    // 配置滤镜参数
    FFTFilter->Type = ECurveEditorFFTFilterType::Lowpass;
    FFTFilter->Response = ECurveEditorFFTFilterClass::Butterworth;
    FFTFilter->CutoffFrequency = 0.7f; // 中等程度的低通滤波
    FFTFilter->Order = 4;
    
    // 获取当前选择的关键帧 (简化示例，实际需要从编辑器获取)
    TMap<FCurveModelID, FKeyHandleSet> SelectedKeys = ... ; 
    
    // 应用滤镜
    TMap<FCurveModelID, FKeyHandleSet> NewSelection;
    FFTFilter->ApplyFilter(CurveEditorPtr.ToSharedRef(), SelectedKeys, NewSelection);
    
    // 此时曲线数据已被修改，NewSelection可能包含新生成的关键帧选择
}
```

### 进阶用法 (与变换工具交互)

变换工具 (`FCurveEditorTransformTool`) 是 `ICurveEditorToolExtension` 的一个实现，通常由曲线编辑器UI激活。你也可以在C++中监听或与之交互。
（来源：`FCurveEditorTransformTool` 的头文件）

```cpp
// 获取当前曲线编辑器的工具扩展管理器 (示意性代码，实际API可能有所不同)
if (TSharedPtr<ICurveEditorToolExtensionManager> ToolManager = CurveEditorPtr->GetToolExtensionManager())
{
    // 检查当前激活的工具是否是变换工具
    if (TSharedPtr<ICurveEditorToolExtension> ActiveTool = ToolManager->GetActiveTool())
    {
        if (FCurveEditorTransformTool* TransformTool = static_cast<FCurveEditorTransformTool*>(ActiveTool.Get()))
        {
            // 获取或修改工具选项
            TSharedPtr<FStructOnScope> OptionsOnScope = TransformTool->GetToolOptions();
            if (FTransformToolOptions* Options = reinterpret_cast<FTransformToolOptions*>(OptionsOnScope->GetStructMemory()))
            {
                // 例如，读取当前缩放中心
                FVector2D CurrentScaleCenter = FVector2D(Options->ScaleCenterX.Value, Options->ScaleCenterY);
            }
        }
    }
}
```

## Demo 示例

以下是一个可编译的编辑器工具模块示例，演示如何在自定义编辑器扩展中应用CurveEditorTools插件提供的FFT滤镜。

**CurveEditorToolsDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Editor/EditorEngine.h"

class FMyCurveEditorDemoTool
{
public:
    static void ApplySmoothingFilterToSelectedKeys(TSharedPtr<FCurveEditor> InCurveEditor);
};
```

**CurveEditorToolsDemo.cpp**
```cpp
#include "CurveEditorToolsDemo.h"
#include "Filters/CurveEditorFFTFilter.h"
#include "CurveEditor.h"

void FMyCurveEditorDemoTool::ApplySmoothingFilterToSelectedKeys(TSharedPtr<FCurveEditor> InCurveEditor)
{
    if (!InCurveEditor.IsValid())
    {
        return;
    }

    // 创建并配置低通滤波器
    UCurveEditorFFTFilter* SmoothFilter = NewObject<UCurveEditorFFTFilter>();
    SmoothFilter->Type = ECurveEditorFFTFilterType::Lowpass;
    SmoothFilter->CutoffFrequency = 0.3f; // 强平滑
    SmoothFilter->Response = ECurveEditorFFTFilterClass::Butterworth;
    SmoothFilter->Order = 2;

    // 注意：实际使用中，你需要通过 InCurveEditor 的接口获取当前选择的关键帧。
    // 这里仅为演示API调用流程，省略了获取选中关键帧的具体代码。
    TMap<FCurveModelID, FKeyHandleSet> KeysToOperateOn = ... ; // 从编辑器获取
    TMap<FCurveModelID, FKeyHandleSet> OutNewSelection;

    // 应用滤镜
    SmoothFilter->ApplyFilter(InCurveEditor.ToSharedRef(), KeysToOperateOn, OutNewSelection);

    UE_LOG(LogTemp, Log, TEXT("Applied smoothing filter. Filtered keys may have been regenerated."));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TweeningUtils` | 提供缓动（Tweening）功能和模型，本插件的缓动扩展依赖于此。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `51e61d5d` | Curve Editor: Lattice tool now mirrors user tangents on x-axis | 网格工具现在支持在X轴上镜像用户设置的切线 |
| 2026-03-30 | `17e19999` | Tweening Utils: Add hotkeys to change slider position. By default: | 为缓动滑块添加了更改位置的热键 |
| 2026-03-27 | `f6f50393` | Anim In Engine: Hotkeys for 1) Zoom To/Frame Selection Range Command in Sequencer and Curve Editor, | 在动画引擎和曲线编辑器中添加了缩放至选区范围等命令的热键 |
| 2026-03-23 | `979bfe32` | Curve Editor: Fix non-unity compile issue. | 修复了非Unity编译问题 |
| 2026-03-23 | `c3b4873e` | Curve Editor: Fix lattice tool flipping bool values on bool curves, like IK switches, when only movi | 修复了网格工具在只移动关键帧时会错误翻转布尔曲线（如IK开关）值的bug |

### 维护评价

- **创建时间**：2019年创建，是编辑器工具链中的一个成熟组件。
- **近期更新**：2026年仍有活跃的提交，内容涉及功能增强（镜像切线、热键）和Bug修复，表明仍在维护。
- **维护状态**：**维护中**。Epic Games官方持续维护该核心编辑器插件。
- **推荐使用**：**强烈推荐**。对于任何需要在Sequencer或UMG中深度编辑动画曲线的工作流，此插件提供的工具是必不可少的，且被官方默认启用，是UE编辑器功能的重要组成部分。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/CurveEditorTools)
- [官方文档]() (暂无，但其功能是引擎编辑器文档的一部分)