# Tweening Utils

> Algorithms and widgets useful for inbetweening.

| 属性 | 值 |
|---|---|
| 中文名 | 补间工具 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器控件） |
| 模块 | `TweeningUtils` (Runtime), `TweeningUtilsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-12-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/TweeningUtils) | |

## 用途

TweeningUtils 从动画系统的补间（Tweening）逻辑中提取出通用的数学算法和编辑器控件，封装为独立插件。其核心目的是为动画曲线编辑器（Curve Editor）和其他需要关键帧中间值（Inbetweening）的工具提供可复用的混合（Blending）函数库。

在动画制作中，动画师经常需要对一组连续关键帧进行"推拉"操作——例如将某段曲线变平、变陡、平移或平滑化。这些操作的数学逻辑被本插件集中管理，使得 Curve Editor、ControlRig 等不同工具可以共享同一套补间算法，避免代码重复。

## 使用场景

- 你正在开发自定义动画曲线编辑工具，需要对选中的关键帧进行批量混合操作 → 使用 Blend_* 系列函数
- 你需要在 Curve Editor 中实现"Smooth"或"Ease"功能来平滑动画曲线 → 依赖本插件的 Blend_SmoothRough 和 Blend_Ease
- 你需要在 ControlRig 或其他动画工具中集成补间滑块控件 → 使用 TweeningUtilsEditor 模块提供的 STweenSlider 控件
- 你需要对动画曲线进行时间偏移（Time Offset）效果 → 使用 Blend_OffsetTime 实现相位移动

## 蓝图用法

本插件主要面向 C++ 开发者，核心算法均为纯数学函数，未暴露蓝图节点。编辑器控件 STweenSlider 为 Slate 控件，不直接在蓝图中使用。

如需在蓝图中使用类似功能，建议通过 UBlueprintFunctionLibrary 包装所需的混合函数。

## C++ 用法

### 头文件引入

```cpp
#include "Math/KeyBlendingFunctions.h"
```

### 核心混合函数

所有函数位于 `UE::TweeningUtils` 命名空间，接受一个 `BlendValue`（范围 [-1.0, 1.0]）以及关键帧坐标信息（FVector2d，X=时间，Y=值），返回混合后的新 Y 值。

| 函数 | 说明 |
|---|---|
| `Blend_ControlsToTween` | BlendValue -1/1 时将所有关键帧线性插值到范围前/后关键帧的高度 |
| `Blend_PushPull` | BlendValue -1/1 时平滑或夸大曲线中的凹谷和山峰 |
| `Blend_Neighbor` | 使用线性插值将关键帧逐步移向范围前/后关键帧的高度 |
| `Blend_Relative` | 等距移动所有关键帧，使最左/最右关键帧对齐范围边界 |
| `Blend_Ease` | 使用平滑 S 曲线将关键帧逐步插值到范围前/后关键帧的高度 |
| `Blend_SmoothRough` | 压缩或拉伸相邻关键帧间距，-1 平滑化，1 增大跳变 |
| `Blend_OffsetTime` | 不改变 X 值而是通过重算 Y 值实现曲线的相位偏移效果 |

### 基本用法

```cpp
// BlendValue 为混合强度，范围 [-1.0, 1.0]
// 负值向左偏移效果，正值向右
double BlendValue = 0.5;

// 当前关键帧及其上下文（X=时间, Y=值）
FVector2d BeforeBlendRange(0.0, 100.0);   // 混合范围前一个关键帧
FVector2d FirstBlended(1.0, 120.0);       // 混合范围内第一个关键帧
FVector2d Current(2.0, 150.0);            // 当前正在混合的关键帧
FVector2d LastBlended(3.0, 130.0);        // 混合范围内最后一个关键帧
FVector2d AfterBlendRange(4.0, 110.0);    // 混合范围后一个关键帧

// 使用 Push-Pull 混合：正值夸大曲线变化
double NewY = UE::TweeningUtils::Blend_PushPull(
    BlendValue, BeforeBlendRange, Current, AfterBlendRange
);
// Current.Y 将被更新为 NewY
```

### 进阶用法：时间偏移混合

```cpp
double BlendValue = 0.3;

FVector2d FirstBlended(1.0, 120.0);
FVector2d LastBlended(5.0, 130.0);
FVector2d BeforeBlendRange(0.0, 100.0);
FVector2d AfterBlendRange(6.0, 110.0);
FVector2d Current(3.0, 150.0);

// 提供一个评估函数，用于在偏移后的 X 处求值
auto EvaluateCurve = [](double X) -> double
{
    // 这里是你的曲线求值逻辑
    // 例如从 FRichCurve 采样
    return FMath::Sin(X) * 50.0 + 100.0;
};

// 时间偏移混合：不改变关键帧时间，通过重算 Y 值模拟曲线相位移动
double NewY = UE::TweeningUtils::Blend_OffsetTime(
    BlendValue, Current, FirstBlended, LastBlended,
    BeforeBlendRange, AfterBlendRange,
    EvaluateCurve,
    true  // 允许外推
);
```

### 与 Curve Editor 集成

本插件还提供了 CVar 来控制 Ease 混合的精细行为：

```cpp
// 控制 Ease 混合的 S 曲线斜率
// Tweening.Ease.SlopeExponent — 斜率指数
// Tweening.Ease.SlopeMultiplier — 斜率乘数
```

这些 CVar 可在运行时通过控制台调整，便于动画师微调混合效果。

## Demo 示例

以下展示如何对一组连续关键帧应用 Smooth-Rough 混合：

```cpp
// KeyBlendExample.h
#pragma once
#include "Math/KeyBlendingFunctions.h"

class FKeyBlendExample
{
public:
    /** 对选中的关键帧应用平滑化混合 */
    static void ApplySmoothBlend(TArray<FVector2d>& InOutKeys, double BlendValue);
};
```

```cpp
// KeyBlendExample.cpp
#include "KeyBlendExample.h"

void FKeyBlendExample::ApplySmoothBlend(TArray<FVector2d>& InOutKeys, double BlendValue)
{
    if (InOutKeys.Num() < 3)
    {
        return; // 至少需要 3 个关键帧（前、当前、后）
    }

    // 临时保存原始 Y 值，避免混合过程中的迭代依赖
    TArray<double> OriginalY;
    OriginalY.Reserve(InOutKeys.Num());
    for (const FVector2d& Key : InOutKeys)
    {
        OriginalY.Add(Key.Y);
    }

    // 对中间的关键帧逐个应用混合
    for (int32 i = 1; i < InOutKeys.Num() - 1; ++i)
    {
        FVector2d BeforeCurrent(InOutKeys[i - 1].X, OriginalY[i - 1]);
        FVector2d Current(InOutKeys[i].X, OriginalY[i]);
        FVector2d AfterCurrent(InOutKeys[i + 1].X, OriginalY[i + 1]);

        // SmoothRough: 负值平滑，正值锐化
        InOutKeys[i].Y = UE::TweeningUtils::Blend_SmoothRough(
            BlendValue, BeforeCurrent, Current, AfterCurrent
        );
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

核心混合函数仅使用 `FVector2d`、`TFunctionRef` 等基础数学类型，不依赖动画模块。TweeningUtilsEditor 模块可能依赖 Slate 控件相关模块，但这些属于常见依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `fe0c9ae2` | AIE: Time offset now handles pre and post infinity extrapolation | 时间偏移混合现在支持前后无限外推处理 |
| 2026-04-13 | `08a29230` | Tweening Utils: Improve parameters for easing tween function based on animator feedback. | 根据动画师反馈改进 Ease 补间函数的参数 |
| 2026-04-13 | `d90a7355` | Curve Editor: Fix tweening not flattening user tangents when tweening exactly 1 key. | 修复恰好选中 1 个关键帧时补间未展平用户切线的问题 |
| 2026-04-09 | `eae4d14e` | Curve Editor: Add Tweening.Ease.SlopeExponent and Tweening.Ease.SlopeMultiplier CVars to better cont... | 添加控制 Ease 补间 S 曲线斜率的 CVar 参数 |

### 维护评价

**活跃维护中** 🟢

- **创建时间**：2024-12-10，插件非常年轻（约 1 年）
- **更新频率**：活跃，最近 1 个月内有多次实质性更新
- **更新内容**：涵盖功能增强（CVar 参数、外推支持）、bug 修复（单关键帧切线）、代码质量改进（浮点警告修复）
- **维护团队**：Epic Games 官方维护，与 Curve Editor 和 ControlRig 等核心动画工具紧密集成
- **推荐使用**：✅ 推荐。作为动画曲线补间功能的底层库，设计清晰、职责单一，是 Curve Editor 补间功能的基础设施

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/TweeningUtils)
- [首次提交](https://github.com/EpicGames/UnrealEngine/commit/611c3d730ae4fc8032ee4e6261156228d5dffaa7)