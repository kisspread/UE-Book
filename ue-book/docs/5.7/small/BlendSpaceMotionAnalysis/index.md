# Blendspace Motion Analysis

> Allows analysis of locomotion/root motion properties in blend spaces

| 属性 | 值 |
|---|---|
| 分类 | BlendSpace |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | BlendSpaceMotionAnalysis (Editor) |
| 创建时间 | 2021-05-22 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Animation/BlendSpaceMotionAnalysis) | |

## 用途

BlendSpaceMotionAnalysis 为 BlendSpace 提供运动分析功能，能够自动从动画序列中计算 Root Motion 和 Locomotion（骨盆/足部运动）的速度、方向等数值，用于填充 BlendSpace 的采样点坐标。

在 UE 的 BlendSpace 编辑器中，你可以指定一个"分析函数"来自动计算每个动画在各轴上的采样值。这个 plugin 注册了两个分析函数：

- **RootMotion** — 基于动画的根运动（Root Motion Transform）计算位移速度/方向
- **Locomotion** — 基于指定骨骼（如脚踝）的运动轨迹计算实际行走速度/方向，通过高度加权算法过滤掉空中帧，仅保留地面接触时段的速度

两者的关键区别：RootMotion 直接使用根骨骼的位移，适合使用根运动驱动的角色；Locomotion 分析特定骨骼的运动，适合不用根运动但需要根据脚步运动自动计算 BlendSpace 参数的场景。

## 使用场景

- 你有一个包含各种方向和速度移动动画的 BlendSpace，需要自动计算每个动画的 Speed/Direction 值来放置采样点 → 在 BlendSpace 编辑器中选择 RootMotion 或 Locomotion 分析函数
- 你的角色使用根运动（Root Motion）驱动移动 → 用 RootMotion 分析
- 你的角色不用根运动，而是从动画中提取脚步运动信息 → 用 Locomotion 分析，指定脚踝骨骼
- 你需要分析上坡/下坡角度 → 使用 ForwardSlope 或 RightwardSlope 轴类型

## 蓝图用法

此 plugin 不暴露任何 BlueprintCallable 函数。它是一个纯 Editor 模块，通过 `IModularFeatures` 向 BlendSpace 编辑器注册分析功能，仅在编辑器的 BlendSpace 属性面板中使用。

## C++ 用法

### 头文件引入

```cpp
#include "BlendSpaceMotionAnalysis.h"
#include "RootMotionAnalysis.h"
#include "LocomotionAnalysis.h"
```

### 基本用法

该 plugin 通过 Modular Feature 系统注册，通常不需要直接调用。核心入口是 `FBlendSpaceMotionAnalysisFeature`，它实现了 `IBlendSpaceAnalysisFeature` 接口：

```cpp
// plugin 启动时自动注册（BlendSpaceMotionAnalysis.cpp:96）
IModularFeatures::Get().RegisterModularFeature(
    IBlendSpaceAnalysisFeature::GetModuleFeatureName(), 
    &BlendSpaceMotionAnalysisFeature);
```

BlendSpace 编辑器在需要分析动画时，会通过此接口调用：

```cpp
// 创建分析属性对象
UAnalysisProperties* Props = Feature->MakeAnalysisProperties(Outer, TEXT("RootMotion"));

// 计算某个动画的采样值
float Result;
bool bSuccess = Feature->CalculateSampleValue(
    Result, BlendSpace, Props, Animation, RateScale);
```

### 进阶用法

#### RootMotion 分析的轴类型 (`EAnalysisRootMotionAxis`)

| 枚举值 | 说明 | 输出单位 |
|---|---|---|
| `Speed` | 根运动位移的总速度（标量） | cm/s |
| `Direction` | 根运动方向角度 | 度(°) |
| `ForwardSpeed` | 沿角色面朝方向的速度分量 | cm/s |
| `RightwardSpeed` | 沿角色右侧方向的速度分量 | cm/s |
| `UpwardSpeed` | 沿角色上方方向的速度分量 | cm/s |
| `ForwardSlope` | 前进方向的坡度角 | 度(°) |
| `RightwardSlope` | 右侧方向的坡度角 | 度(°) |

#### Locomotion 分析的轴类型 (`EAnalysisLocomotionAxis`)

与 RootMotion 相同的 7 种轴类型，但计算方式不同：Locomotion 通过分析指定骨骼的实际运动轨迹来推算速度，并使用高度加权算法过滤空中帧。

#### 配置属性

**URootMotionAnalysisProperties** 继承自 `ULinearAnalysisPropertiesBase`（定义于 `Persona` 模块的 `BlendSpaceAnalysis.h`）：

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `FunctionAxis` | `EAnalysisRootMotionAxis` | Speed | 分析的轴类型 |
| `BoneSocket` | `FBoneSocketTarget` | — | 分析所用的骨骼/Socket（继承自基类） |
| `Space` | `EAnalysisSpace` | World | 分析空间：World/Fixed/Changing/Moving（继承自基类） |
| `SpaceBoneSocket` | `FBoneSocketTarget` | — | 定义分析空间的骨骼（当 Space 非 World 时使用） |
| `StartTimeFraction` | `float` | 0.0 | 分析起始时间比例（0~1） |
| `EndTimeFraction` | `float` | 1.0 | 分析结束时间比例（0~1） |
| `CharacterFacingAxis` | `EAnalysisLinearAxis` | PlusY | 角色面朝方向的轴 |
| `CharacterUpAxis` | `EAnalysisLinearAxis` | PlusZ | 角色上方方向的轴 |

**ULocomotionAnalysisProperties** 继承自 `UAnalysisProperties`：

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `FunctionAxis` | `EAnalysisLocomotionAxis` | Speed | 分析的轴类型 |
| `PrimaryBoneSocket` | `FBoneSocketTarget` | — | 主要分析骨骼（如左脚踝） |
| `SecondaryBoneSocket` | `FBoneSocketTarget` | — | 次要分析骨骼（如右脚踝） |
| `CharacterFacingAxis` | `EAnalysisLinearAxis` | PlusY | 角色面朝方向的轴 |
| `CharacterUpAxis` | `EAnalysisLinearAxis` | PlusZ | 角色上方方向的轴 |

**关于 EAnalysisSpace 的说明：**

| 枚举值 | 说明 |
|---|---|
| `World` | 在世界空间中分析（相对于角色根骨骼） |
| `Fixed` | 使用动画第一帧时骨骼/Socket 的空间 |
| `Changing` | 使用当前帧的骨骼空间，但假设该空间不移动 |
| `Moving` | 使用当前帧的骨骼空间，速度也相对于该运动空间 |

Locomotion 分析支持两个骨骼输入（Primary + Secondary），结果取两者的平均值，适合同时使用左右脚踝来获得更准确的步行速度。注意 Locomotion 分析不支持 `Space` 属性（固定为 World 空间）。

## Demo 示例

此 plugin 没有独立的运行时功能，不需要编写代码集成。使用方式：

1. 在项目中启用 BlendSpaceMotionAnalysis 插件（默认已启用）
2. 打开 BlendSpace 资产编辑器
3. 在采样点的分析属性中，选择分析函数为 `RootMotion` 或 `Locomotion`
4. 如果选择 Locomotion，配置 PrimaryBoneSocket（如 `foot_l`）和可选的 SecondaryBoneSocket（如 `foot_r`）
5. 根据角色朝向配置 CharacterFacingAxis（默认 +Y）和 CharacterUpAxis（默认 +Z）
6. 点击"Regenerate"按钮，插件会自动分析所有动画并计算采样值

## 模块依赖

从 Build.cs 的 `PrivateDependencyModuleNames` 提取（均为私有依赖，使用者无需额外声明）：

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心功能 |
| `Persona` | 动画编辑器/Persona 模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-05-30 | `20572801` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types | 编译器兼容性修复，调整 DLL 导出标记位置，无功能变化 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings | 编译警告修复，无功能变化 |
| 2025-02-05 | `e39d80b7` | Fix for crash when using a negative axis for angular velocity analysis in persona blend space editor; Deprecated templated parameter for AnalysisProperties | **实质性更新**：修复负轴分析时的崩溃，同时重构 API 用强类型替代模板参数 |

### 维护评价

- **创建时间**: 2021 年 5 月，已超过 5 年
- **最近更新**: 2025 年 2 月有一次实质性功能修复，之后均为编译层面的维护
- **维护状态**: 维护中 — 功能稳定，偶有 bug 修复
- **模块类型**: Editor only，不影响运行时包体
- **推荐使用**: ✅ 推荐。作为 BlendSpace 内置分析功能的扩展，稳定可靠。默认启用，无需额外配置。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Animation/BlendSpaceMotionAnalysis)
- 官方文档: 无（.uplugin 中 DocsURL 为空）
- 测试用例: 未发现独立测试文件
