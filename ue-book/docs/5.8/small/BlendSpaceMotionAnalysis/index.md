# Blendspace Motion Analysis

> Allows analysis of locomotion/root motion properties in blend spaces

| 属性 | 值 |
|---|---|
| 中文名 | 混合空间运动分析 |
| 分类 | BlendSpace |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `BlendSpaceMotionAnalysis` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2021-05-22 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/BlendSpaceMotionAnalysis) | |

## 用途

该插件为 UE5 的混合空间编辑器提供了一套内置的运动分析工具。它解决了在混合空间中根据动画的实际运动特性（如速度、方向、坡度）来设置和调整参数时，缺乏量化数据支持的问题。插件通过分析动画序列中骨骼或根骨骼的位移和旋转，自动计算出运动属性，帮助用户精确地将动画映射到混合空间的坐标轴上，从而创建更准确、更符合物理规律的混合空间，尤其适用于创建角色移动的混合空间。

## 使用场景

- 你正在为角色的移动（行走、奔跑、冲刺）创建一个混合空间，需要根据动画的实际移动速度（米/秒）来设置混合空间的“速度”参数轴。
- 你需要基于根运动（Root Motion）动画的位移方向来设置混合空间的“方向”参数轴，以实现更平滑的转向混合。
- 你希望分析动画在特定骨骼（如脚部）上的运动轨迹，以实现足迹匹配或更复杂的动画混合逻辑。
- 你在编辑混合空间时，希望有一个自动化的工具来预览和确认每个样本点的运动数据，而不是依赖手动估算。

## 蓝图用法

此插件主要提供编辑器工具和用于构建自定义分析功能的 C++ API，其核心功能集成在混合空间编辑器的右键菜单中，而非暴露为蓝图节点。以下是从源码中提取的、可用于自定义分析逻辑的核心类和函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CalculateLocomotion` | 根据动画和属性计算运动速度/方向。 | `ULocomotionAnalysisProperties` |
| `CalculateRootMotion` | 根据动画和属性计算根运动速度/方向。 | `URootMotionAnalysisProperties` |

### 使用示例（蓝图描述）

由于此插件的核心功能主要在 C++ 层和编辑器扩展中实现，在蓝图中直接使用其分析节点并不常见。典型的工作流程是在混合空间编辑器界面中，右键选择样本点，然后选择“分析运动”或“分析根运动”子菜单。该插件提供的 `CalculateLocomotion` 和 `CalculateRootMotion` C++ 函数是这些编辑器菜单项背后的实现基础。

## C++ 用法

### 头文件引入

```cpp
#include "LocomotionAnalysis.h"
#include "RootMotionAnalysis.h"
```

### 基本用法

以下示例展示了如何配置并执行一次运动分析。此逻辑通常被插件自身的编辑器 UI 调用，但你也可以在自定义的编辑器工具或自动化脚本中调用。

```cpp
// 来源于引擎源码对插件功能的调用逻辑
#include "LocomotionAnalysis.h"
#include "Animation/AnimSequence.h"
#include "BlendSpace/BlendSpace.h"

// 假设已有有效的 BlendSpace 和 Animation 指针
UBlendSpace* MyBlendSpace = ...;
UAnimSequence* MyAnimation = ...;

// 1. 创建并配置分析属性
ULocomotionAnalysisProperties* AnalysisProps = NewObject<ULocomotionAnalysisProperties>();
AnalysisProps->FunctionAxis = EAnalysisLocomotionAxis::Speed;
AnalysisProps->PrimaryBoneSocket.BoneName = FName("pelvis"); // 设置要分析的主要骨骼
AnalysisProps->CharacterFacingAxis = EAnalysisLinearAxis::PlusX;

// 2. 执行计算
float ResultSpeed = 0.f;
float RateScale = 1.f; // 动画播放速率
bool bSuccess = CalculateLocomotion(ResultSpeed, *MyBlendSpace, AnalysisProps, *MyAnimation, RateScale);

if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("计算出的运动速度: %f"), ResultSpeed);
    // 在这里可以将 ResultSpeed 设置为混合空间样本点的坐标值
}
```

### 进阶用法

该插件允许通过继承 `UAnalysisProperties` 基类来创建自定义的运动分析函数。你可以定义自己的分析轴（例如，分析特定骨骼在某一轴向上的位移），然后实现计算逻辑。

```cpp
// 自定义分析属性类（概念示例）
UCLASS()
class UCustomFootstepAnalysisProperties : public UAnalysisProperties
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category = "Custom")
    FName AnkleBoneName = FName("ankle_l");

    UPROPERTY(EditAnywhere, Category = "Custom")
    EAnalysisLinearAxis StepHeightAxis = EAnalysisLinearAxis::PlusZ;
};

// 自定义分析函数
bool CalculateCustomFootstep(float& Result, const UBlendSpace& BlendSpace, const UCustomFootstepAnalysisProperties* Props, const UAnimSequence& Anim, float RateScale)
{
    // 在这里实现基于特定脚踝骨骼在Z轴向上的位移分析
    // ... 你的计算逻辑 ...
    Result = ...;
    return true;
}

// 之后，可以将此自定义函数注册到混合空间编辑器的分析菜单中（需要额外的编辑器扩展代码）。
```

## Demo 示例

此插件没有独立的可运行Demo，其主要体现为编辑器功能。最小的使用示例就是在混合空间编辑器中对一个样本点执行右键菜单操作。

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Editor 等）。此插件的 `Build.cs` 依赖项为常见的运行时和编辑器模块，未引用其他独特的第三方或高级插件模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏UE_LOG迁移为UE_LOGF，属于代码现代化维护。 |
| 2025-05-30 | `20572801` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 修正头文件导出标记，确保符号在正确的类上，是编译兼容性修复。 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复轻微的、无法到达的代码警告，提升代码整洁度。 |
| 2025-02-05 | `e39d80b7` | Fix for crash when using a negative axis for angular velocity analysis in persona blend space editor | 修复在角色混合空间编辑器中使用负数轴进行角速度分析时的崩溃问题。 |

### 维护评价

- **创建时间**：约4年前，属于较新的插件。
- **更新频率**：最近一年有多次维护性更新，主要集中在代码修复、编译警告处理和宏迁移上。
- **维护状态**：**维护中**。Epic Games 仍在对其进行基本的维护和质量保障工作，但自创建以来没有新增重大功能。
- **已知问题/限制**：无特别记录的问题。其功能专注于运动分析，范围明确。
- **推荐使用**：✅ **推荐使用**。如果你的工作流程涉及大量混合空间的制作，尤其是基于运动数据的混合空间，此插件能提供极大的便利和准确性。它是官方支持的工具，集成度好，稳定可靠。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/BlendSpaceMotionAnalysis)
- [官方文档](https://docs.unrealengine.com/)（此插件没有独立文档页面，其功能在混合空间编辑器相关文档中提及）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/BlendSpaceMotionAnalysis/Tests)（如果存在）