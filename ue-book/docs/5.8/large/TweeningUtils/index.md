# Tweening Utils

> Algorithms and widgets useful for inbetweening.

| 属性 | 值 |
|---|---|
| 中文名 | 补间工具 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `TweeningUtils` (Runtime), `TweeningUtilsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-12-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/TweeningUtils) | |

## 用途

TweeningUtils 是一个专注于动画**补间（Tweening / Inbetweening）**的算法与编辑器工具插件。它的核心目的是将原本分散在各处的补间计算逻辑抽取为独立模块，为 Curve Editor 和 ControlRig 等工具提供统一的补间能力。

具体来说，它解决以下问题：

- **关键帧之间的平滑插值**：提供多种缓动（Easing）算法，让动画师在 Curve Editor 中对选中的关键帧进行平滑过渡
- **补间参数的可视化调节**：通过 `STweenSlider` 控件，动画师可以直观地调整补间强度
- **可扩展的补间函数框架**：通过 CVar 系统暴露参数（如 `Tweening.Ease.SlopeExponent`、`Tweening.Ease.SlopeMultiplier`），方便高级用户微调缓动曲线形状

该插件最初是为了向 Curve Editor 引入补间功能而从现有代码中重构出来的，后续逐步扩展为一个独立的动画辅助工具集。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `TweeningUtils` | Runtime | 核心补间算法库，包含缓动函数、补间数学计算等可运行时使用的基础逻辑 |
| `TweeningUtilsEditor` | Editor | 编辑器集成模块，提供 `STweenSlider` 等 Slate 控件，将补间能力嵌入 Curve Editor 工具栏 |

## 使用场景

- 你在 Curve Editor 中选中了多个关键帧，想在它们之间创建平滑的过渡效果 → 用 TweeningUtils 的缓动功能
- 你在开发自定义动画编辑工具，需要补间插值算法 → 依赖 `TweeningUtils` Runtime 模块的数学函数
- 你需要在自己的编辑器面板中提供一个补间强度滑块 → 使用 `STweenSlider` 控件
- 你是高级动画 TD，需要通过 CVar 精确控制缓动曲线的斜率和指数 → 通过控制台变量调整补间参数

## 蓝图用法

> 该插件主要面向 C++ 和编辑器 Slate 控件层，蓝图可用的公开 API 较少。补间逻辑主要通过编辑器工具栏中的 STweenSlider 控件触发。

如需在运行时使用补间算法，请参考 C++ 用法章节。

## C++ 用法

### 头文件引入

```cpp
// 补间算法核心
#include "TweeningUtils.h"

// 编辑器侧补间控件（仅在编辑器模块中使用）
#include "STweenSlider.h"
```

### 基本用法

使用 Runtime 模块提供的缓动函数对数值进行补间：

```cpp
// 获取补间后的插值结果（伪代码，实际 API 请参考模块文档）
// 典型流程：在两个关键帧之间根据补间进度 [0,1] 计算插值
float Alpha = 0.5f; // 补间进度
float Result = TweeningUtils::EasingFunction(Alpha);
```

### 进阶用法

通过 CVar 调整缓动曲线参数（来自近期提交）：

```cpp
// 可通过控制台变量微调缓动行为
// Tweening.Ease.SlopeExponent — 控制缓动斜率指数
// Tweening.Ease.SlopeMultiplier — 控制缓动斜率乘数
// 这些参数基于动画师反馈优化，可提供更精细的曲线控制
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译警告 |
| 2026-05-12 | `fe0c9ae2` | AIE: Time offset now handles pre and post infinity extrapolation | 时间偏移现在支持无穷外推模式 |
| 2026-04-13 | `08a29230` | Tweening Utils: Improve parameters for easing tween function based on animator feedback. | 根据动画师反馈优化缓动函数参数 |
| 2026-04-13 | `d90a7355` | Curve Editor: Fix tweening not flattening user tangents when tweening exactly 1 key. | 修复在仅补间1个关键帧时未正确展平用户切线的问题 |
| 2026-04-09 | `eae4d14e` | Curve Editor: Add Tweening.Ease.SlopeExponent and Tweening.Ease.SlopeMultiplier CVars to better cont | 为 Curve Editor 新增缓动斜率指数和乘数控制台变量 |

### 维护评价

**🟢 活跃维护中**

- 插件创建于 2024 年 12 月，非常年轻（约 1 年），处于快速迭代阶段
- 近期更新频繁（2026 年 4-5 月有多次实质性提交），涵盖功能优化、Bug 修复和动画师反馈驱动的参数调整
- 从 commit 记录可以看出，该插件与 Curve Editor 深度集成，正在持续完善用户体验
- 作为从现有代码重构出来的独立模块，架构清晰，维护质量较高
- **推荐使用**：这是 Epic 官方维护的动画补间基础设施，适合需要在 Curve Editor 或自定义工具中使用补间功能的项目

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/TweeningUtils)
- [Runtime 模块文档](TweeningUtils.md)
- [Editor 模块文档](TweeningUtilsEditor.md)