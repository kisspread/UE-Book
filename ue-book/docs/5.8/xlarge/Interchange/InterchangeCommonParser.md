# Interchange Common Parser

> 提供通用的动画曲线数据结构和工具函数，作为 Interchange 框架中数据解析层的基础组件。

| 属性 | 值 |
|---|---|
| 中文名 | 通用解析器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeCommonParser` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 N 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime/Source/Parsers/CommonParser) | |

## 用途

**InterchangeCommonParser** 模块是 **Interchange Framework** 的核心数据定义层之一。它不直接执行文件解析或资产创建，而是为动画曲线（Animation Curve）相关的数据传输定义了一套标准化的、与引擎解耦的数据结构。

它的核心作用是：
1.  **统一数据表示**：定义 `FInterchangeCurveKey`、`FInterchangeCurve`、`FInterchangeStepCurve` 等结构体，作为从各种格式（如 FBX、glTF）的**翻译器 (Translator)** 向引擎**工厂节点 (Factory Nodes)** 传递动画关键帧数据的“通用语言”。
2.  **提供序列化支持**：为这些数据结构实现自定义的序列化功能（`Serialize` 和重载的 `<<` 运算符），确保数据能够在 Interchange 管道的不同阶段（可能运行在不同进程或线程）中安全地传递。
3.  **封装引擎转换**：通过 `ToRichCurve`、`ToRichCurveKey` 等函数，将 Interchange 的通用数据结构高效地转换为 UE 引擎内部的 `FRichCurve` 等类型，隔离了转换逻辑。

**为什么存在？** 传统的资产导入器（如 FBX 导入器）通常与特定文件格式紧密耦合。Interchange 框架旨在创建一个可扩展的系统，其中 `InterchangeCommonParser` 提供的通用数据结构是实现“一次翻译，多处使用”的关键，允许相同的动画数据被用于导入、预览、USD 处理等多种场景，而无需每次都重新解析原始文件。

## 使用场景

- **开发自定义文件格式导入插件**：你需要解析一种新格式（如自定义骨骼动画格式）并将其导入 UE。你的翻译器应将解析出的关键帧数据填充到 `FInterchangeCurve` 结构体中，然后通过 Interchange 节点图传递给引擎。
- **扩展或调试 Interchange 动画管线**：当需要跟踪或修改通过 Interchange 框架传输的动画曲线数据时，理解这些核心结构体是必要的。
- **理解 Interchange 框架内部机制**：作为学习 Interchange 框架数据流的一部分，本模块是理解数据如何从“外部世界”进入“UE 引擎世界”的基础。

## 蓝图用法

该模块主要提供 C++ 层面的数据结构和枚举，用于管道和翻译器之间的数据交换。在蓝图中，这些结构体**不会**直接作为可调用的节点暴露。

蓝图中的交互通常发生在更高层级，例如：
- 通过 **Interchange Pipeline Configuration** 蓝图配置导入管线的行为。
- 在 **Interchange Graph** 蓝图资产中使用其他 Interchange 模块提供的蓝图节点来处理资产。

本模块定义的 `EInterchangeCurveInterpMode` 等枚举可能会在配置插值行为的蓝图属性中可见。

### 核心结构体

| 结构体/枚举 | 说明 | 头文件 |
|---|---|---|
| `EInterchangeCurveInterpMode` | 定义曲线关键帧之间的插值模式（线性、常数、立方、无）。 | `InterchangeCommonAnimationPayload.h` |
| `EInterchangeCurveTangentMode` | 定义立方插值模式下切线的控制方式（自动、用户、断裂、无）。 | `InterchangeCommonAnimationPayload.h` |
| `EInterchangeCurveTangentWeightMode` | 定义切线权重模式（无权重、仅到达权重、仅离开权重、双权重）。 | `InterchangeCommonAnimationPayload.h` |
| `FInterchangeCurveKey` | 存储单个动画关键帧的全部数据（时间、值、插值模式、切线信息等）。 | `InterchangeCommonAnimationPayload.h` |
| `FInterchangeCurve` | 存储一条由多个 `FInterchangeCurveKey` 组成的动画曲线。 | `InterchangeCommonAnimationPayload.h` |
| `FInterchangeStepCurve` | 存储阶跃型曲线数据，支持多种值类型（浮点、布尔、字节等）。 | `InterchangeCommonAnimationPayload.h` |

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeCommonAnimationPayload.h"
```

### 基本用法

将外部解析的动画关键帧数据封装到 Interchange 数据结构中。
```cpp
// 来源: InterchangeCommonAnimationPayload.h

// 创建一个关键帧
FInterchangeCurveKey Key;
Key.Time = 1.5f;
Key.Value = 45.0f;
Key.InterpMode = EInterchangeCurveInterpMode::Cubic;
Key.TangentMode = EInterchangeCurveTangentMode::Auto;

// 将关键帧添加到曲线
FInterchangeCurve MyCurve;
MyCurve.Keys.Add(Key);

// ... 添加更多关键帧 ...

// 将 Interchange 曲线转换为 UE 引擎的 FRichCurve
FRichCurve EngineCurve;
MyCurve.ToRichCurve(EngineCurve);
```

### 进阶用法

使用 `FInterchangeStepCurve` 处理阶跃型动画，并移除冗余数据以优化。
```cpp
// 来源: InterchangeCommonAnimationPayload.h
FInterchangeStepCurve StepCurve;

// 设置关键帧时间
StepCurve.KeyTimes = {0.0f, 0.5f, 1.0f, 1.5f};

// 填充浮点值
StepCurve.FloatKeyValues = {10.0f, 10.0f, 20.0f, 20.0f};

// 移除相邻且值相同的关键帧（例如，前两个10.0f和后两个20.0f）
StepCurve.RemoveRedundantKeys(0.001f); // 阈值

// 处理后的曲线可能只包含 0.0f, 1.0f 时刻的值
```

## Demo 示例

以下是一个模拟翻译器（Translator）处理动画数据的简化示例。
```cpp
// MyAnimationTranslator.h
#pragma once

#include "InterchangeCommonAnimationPayload.h"

class FMyAnimationTranslator
{
public:
    // 假设这是从外部文件解析出的原始动画数据
    struct FRawBoneTrack
    {
        TArray<float> Times;
        TArray<FQuat> Rotations;
    };

    // 将原始数据转换为 Interchange 格式
    static FInterchangeCurve ConvertRotationTrackToInterchangeCurve(const FRawBoneTrack& Track, EAxis::Type Axis)
    {
        FInterchangeCurve Curve;
        Curve.Keys.Reserve(Track.Times.Num());

        for (int32 i = 0; i < Track.Times.Num(); ++i)
        {
            FInterchangeCurveKey Key;
            Key.Time = Track.Times[i];
            Key.Value = Track.Rotations[i].GetComponentForAxis(Axis); // 示例：获取绕某轴的分量
            Key.InterpMode = EInterchangeCurveInterpMode::Cubic;
            Key.TangentMode = EInterchangeCurveTangentMode::Auto; // 自动计算切线
            Curve.Keys.Add(Key);
        }
        return Curve;
    }
};
```
```cpp
// MyAnimationTranslator.cpp
#include "MyAnimationTranslator.h"
// ... 其他 #include ...

// 模拟使用
void SimulateTranslation()
{
    FMyAnimationTranslator::FRawBoneTrack RawTrack;
    RawTrack.Times = {0.0f, 0.5f};
    RawTrack.Rotations = {FQuat::Identity, FQuat(FRotator(0, 90, 0))};

    // 转换为 Interchange 可识别的曲线
    FInterchangeCurve TranslationReadyCurve = FMyAnimationTranslator::ConvertRotationTrackToInterchangeCurve(
        RawTrack, EAxis::Z // 假设提取 Yaw 旋转
    );

    // 接下来，这个 TranslationReadyCurve 会被传递给 Interchange 节点图
}
```

## 模块依赖

无特殊依赖（仅标准 Core/CoreUObject 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `61d0e791` | USD Pregen: Implement tracking of Skeleton and PhysicsAssets | 为USD预生成实现了对骨骼和物理资产的跟踪功能。 |
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复了针对UE 5.8的本地化警告。 |
| 2026-05-22 | `8fdd3a89` | [Interchange] Reset existing LODModels for reimport, so that Bone bindings and mappings are updated | [Interchange] 在重新导入时重置现有的LOD模型，以确保骨骼绑定和映射得到更新。 |
| 2026-05-22 | `3cfa4417` | Reinstated the uFBX parser as experimental | 恢复uFBX解析器为实验性功能。 |
| 2026-05-19 | `755f95d4` | Interchange: Fix crash by protecting against nullptr objects in the list of imported objects. | 修复了因导入对象列表中存在空指针而导致的崩溃问题。 |

### 维护评价

- **维护状态**：**活跃维护中**。从 Git 历史看，该模块在 2026 年 5 月仍有频繁且重要的更新，涉及功能新增（USD 支持）、兼容性修复（UE 5.8）和关键稳定性问题（崩溃修复）。
- **实验性**：根据 `.uplugin` 元数据中 `IsBetaVersion` 字段（虽然未完整显示，但上下文提示为 `true`），该插件整体仍处于 **Beta/实验性** 阶段。这意味着其 API 和功能可能在未来版本中发生变化。
- **推荐度**：作为 Epic 官方推出的下一代资产互操作框架的核心组成部分，Interchange 是未来的发展方向。虽然处于实验性阶段，但对于需要高度可定制化导入/导出流程的项目，或者开发自定义资产管线的团队来说，**值得投入研究和使用**。在生产环境中采用前，需要做好应对 API 变更和潜在问题的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime/Source/Parsers/CommonParser)
- 官方文档：暂无专属文档。
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime/Tests)（Interchange 框架的通用测试，可能覆盖本模块）