# Animation Data

> Animation Data

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | AnimationData (UncookedOnly) |
| 创建时间 | 2022-06-10 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/AnimationData) | |

## 用途

AnimationData plugin 为 `UAnimSequence` 提供了一套基于 **Sequencer / MovieScene** 的动画数据模型替代实现。默认情况下，UE5 的动画序列使用原始骨骼关键帧数据（raw keyframe data）存储动画，而此 plugin 将动画数据替换为由 **ControlRig** 和 **MovieScene** 驱动的表示方式。

核心思路：将骨骼动画的位移/旋转/缩放关键帧映射为 ControlRig 的 Transform 控制器，将动画曲线映射为 MovieScene 的 Float Channel。这样做的好处是：

- 动画数据可以复用 Sequencer 的关键帧编辑基础设施（曲线编辑器、时间轴等）
- ControlRig 提供了统一的骨骼控制框架，便于混合程序化动画
- 支持通过 Sequencer 的 MovieScene 通道进行精确的帧率和插值控制

此 plugin 仅在编辑器中生效（`UncookedOnly`），打包时不会包含在内。动画数据会在保存/打包时回写为传统格式。

## 使用场景

- 你在编辑器中编辑 UAnimSequence，希望使用 Sequencer 风格的曲线编辑器来调整骨骼关键帧 → 启用此 plugin 后，AnimSequence 的数据模型自动切换为 Sequencer-based
- 你需要将 ControlRig 的程序化动画与关键帧动画在同一数据模型中统一管理 → 此 plugin 将骨骼动画存储为 ControlRig 控制器数据
- 你的团队使用 Sequencer 工作流，希望动画编辑体验与 Sequencer 保持一致 → 此 plugin 提供了桥接

## 蓝图用法

此 plugin 没有暴露 `BlueprintCallable` 函数。它通过 `IAnimationDataModels` Modular Feature 注册自身，在编辑器启动时自动替换 UAnimSequence 的数据模型。用户无需在蓝图中直接操作。

数据模型的修改通过 `IAnimationDataController` 接口完成（即 `UAnimSequencerController`），但该接口主要供引擎内部和 C++ 代码使用。

## C++ 用法

### 头文件引入

```cpp
#include "AnimSequencerDataModel.h"
#include "AnimSequencerController.h"
```

### 基本用法

此 plugin 的核心是 `UAnimationSequencerDataModel`（实现 `IAnimationDataModel`）和 `UAnimSequencerController`（实现 `IAnimationDataController`）。通常不需要直接实例化它们，引擎会通过 Modular Feature 自动选择。

获取动画序列的数据模型：

```cpp
// 获取 AnimSequence 的数据模型（启用 AnimationData plugin 后返回的是 UAnimationSequencerDataModel）
UAnimSequence* AnimSeq = /* ... */;
TScriptInterface<IAnimationDataModel> DataModel = AnimSeq->GetDataModel();
IAnimationDataController* Controller = DataModel->GetController();

// 通过 Controller 修改骨骼关键帧
TArray<FVector> Positions = { FVector(0, 0, 0), FVector(10, 0, 0) };
TArray<FQuat> Rotations = { FQuat::Identity, FQuat::Identity };
TArray<FVector> Scales = { FVector::OneVector, FVector::OneVector };
Controller->SetBoneTrackKeys(FName("spine_01"), Positions, Rotations, Scales);
```

### 进阶用法

**查询骨骼变换**：从数据模型中按帧号或帧时间采样骨骼变换：

```cpp
// 按帧号查询
FFrameNumber FrameNum(10);
FTransform BoneTransform = DataModel->GetBoneTrackTransform(FName("spine_01"), FrameNum);

// 按帧时间插值查询
FFrameTime FrameTime(10, 0.5f); // 第 10 帧和第 11 帧之间
FTransform InterpTransform = DataModel->EvaluateBoneTrackTransform(
    FName("spine_01"), FrameTime, EAnimInterpolationType::Linear);
```

**操作动画曲线**：添加和设置 Float 曲线关键帧：

```cpp
FAnimationCurveIdentifier CurveId(FName("MyCurve"), ERawCurveTrackTypes::RCT_Float);
Controller->AddCurve(CurveId);

TArray<FRichCurveKey> Keys;
Keys.Add(FRichCurveKey(0.0f, 0.0f));
Keys.Add(FRichCurveKey(1.0f, 1.0f));
Controller->SetCurveKeys(CurveId, Keys);
```

**Bracket 操作**（批量事务）：

```cpp
Controller->OpenBracket(FText::FromString("Batch Edit"));
// ... 多次修改操作 ...
Controller->CloseBracket();
```

## Demo 示例

此 plugin 不需要直接使用——它是引擎内部组件。如果你想在自己的模块中访问动画数据模型：

```cpp
// MyAnimModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "AnimGraphRuntime",
    "MovieSceneTools",
});
```

```cpp
// MyAnimHelper.h
#pragma once
#include "Animation/AnimSequence.h"
#include "Animation/AnimData/IAnimationDataModel.h"

class FMyAnimHelper
{
public:
    static FTransform GetBoneTransformAtFrame(UAnimSequence* Seq, FName BoneName, int32 Frame)
    {
        if (!Seq) return FTransform::Identity;
        TScriptInterface<IAnimationDataModel> Model = Seq->GetDataModel();
        if (!Model) return FTransform::Identity;
        return Model->GetBoneTrackTransform(BoneName, FFrameNumber(Frame));
    }
};
```

## 模块依赖

使用者需要在 Build.cs 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心模块 |
| `AnimGraphRuntime` | 动画图运行时（数据模型的公共依赖） |
| `MovieSceneTools` | MovieScene 工具（数据模型的公共依赖） |

> 注意：此 plugin 本身还依赖 `ControlRig`、`Sequencer`、`AnimationDataController` 等模块，但这些都是私有依赖，使用者不需要直接引用。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-10-03 | `e44cd25` | 修复动画自动化测试中的时间初始化错误 | 修复 Transform 曲线键值初始化问题，属于测试稳定性修复 |
| 2025-09-29 | `af9dc55` | 修复之前提交中的错误返回值 | Bug 修复，trivial 级别 |
| 2025-09-29 | `698d5aa` | 修复 MovieScene 曲线通道的崩溃断言 | 修复评估/修改竞争条件，添加缺失的 scope lock |

### 维护评价

- **创建时间**：2022 年 6 月，约 4 年历史
- **最近更新**：2025 年 10 月，近期有活跃的 bug 修复
- **维护状态**：**活跃维护** — 近期有多次稳定性修复，表明 Epic 仍在积极使用和维护此 plugin
- **已知限制**：
  - 仅支持 `UAnimSequence`（不支持 `UAnimComposite` 等其他动画资产类型）
  - 模块类型为 `UncookedOnly`，仅在编辑器中可用
  - 依赖 `ControlRig` plugin
- **推荐使用**：✅ 推荐。这是 UE5 动画系统的核心基础设施之一，用于将 AnimSequence 的数据模型迁移到 Sequencer 架构。虽然用户通常不需要直接操作它，但理解其存在有助于理解 UE5 动画编辑的工作原理。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/AnimationData)
- 官方文档（无）
