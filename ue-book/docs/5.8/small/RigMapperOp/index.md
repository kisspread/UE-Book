# RigMapper Op

> Experimental Retarget Op for re-mapping curves using RigMapper Definitions

| 属性 | 值 |
|---|---|
| 中文名 | 骨骼映射操作 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（重定向操作蓝图资产） |
| 模块 | `RigMapperOp` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-09 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RigMapperOp) | |

## 用途

RigMapperOp 插件是 UE5 动画重定向系统（IK Retargeter）中的一个实验性扩展操作。它解决了一个特定问题：在动画重定向过程中，如何利用 `RigMapper` 插件定义的映射规则，对动画曲线进行高效的批量重映射。

这个插件的核心价值在于，它将 `RigMapper` 的强大映射能力与 `IKRig` 的重定向流程无缝集成。具体来说，它允许动画师或技术美术（TA）在编辑器中创建一个 `URigMapperDefinition` 资产，定义源骨骼/曲线到目标骨骼/曲线的复杂映射逻辑（例如，基于表达式、脚本或预设）。然后，在 `IK Retargeter` 的流程中添加一个 `RigMapper Op`，即可在重定向时自动应用这些规则，从而实现曲线（例如，变形目标、材质参数、自定义动画属性）的智能转换。

它存在的必要性是为了解决标准重定向流程中曲线映射能力不足的问题，提供了一个可扩展、可脚本化的高级解决方案。

## 使用场景

- 你正在为两个面部骨骼结构完全不同的角色制作面部动画重定向，需要通过自定义表达式将源角色的 `BlendShape` 曲线（如 `MouthOpen`）映射到目标角色完全不同命名的 `BlendShape`（如 `Jaw_Down`），并同时控制多个相关曲线 → 使用 `RigMapper Op` 并配置一个 `URigMapperDefinition` 资产来处理这种复杂映射。
- 你的项目需要将同一套动画资产应用到多个不同美术标准的角色上，每个角色都有自己的曲线命名和逻辑 → 为每个角色创建不同的 `URigMapperDefinition`，并在其 `IK Retargeter` 流程中选用对应的 `RigMapper Op`。
- 你希望将 `RigMapper` 的映射逻辑通过蓝图或 Python 脚本动态生成或修改，然后用于实时或批量的动画处理 → `RigMapper Op` 提供了蓝图/Python 控制器（`UIKRetargetRigMapperOpController`）用于在运行时调整设置。

## 蓝图用法

由于 `RigMapperOp` 是一个 `IK Retargeter` 操作，它主要通过编辑器内的 `IK Retargeter` 资产进行配置，而不是直接拖拽到蓝图图表中使用。其蓝图用法主要体现在通过 `UIKRetargetRigMapperOpController` 和 `UIKRetargetRigMapperUserDataOpController` 控制器类来动态读写操作设置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Settings` | 获取当前单定义 RigMapper 操作的设置结构体 | `UIKRetargetRigMapperOpController` |
| `Set Settings` | 设置单定义 RigMapper 操作的设置 | `UIKRetargetRigMapperOpController` |
| `Get Settings` | 获取当前 UserData RigMapper 操作的设置结构体 | `UIKRetargetRigMapperUserDataOpController` |
| `Set Settings` | 设置 UserData RigMapper 操作的设置 | `UIKRetargetRigMapperUserDataOpController` |

### 使用示例（蓝图描述）

1.  **获取并修改设置**：在一个动画蓝图或编辑器工具蓝图中，你可以获取到代表 `IK Retargeter` 中某个 `RigMapper Op` 的控制器对象（通常通过其他节点或脚本获取）。然后，拖拽该控制器对象，调用其 `Get Settings` 节点，得到一个 `FIKRetargetRigMapperOpSettings` 结构体。你可以修改该结构体中的 `Definition` 字段（指定新的 `URigMapperDefinition` 资产）或 `bCopyAllSourceCurves` 选项，然后通过 `Set Settings` 节点将修改后的结构体应用回去。
2.  **动态覆盖定义**：如果操作设置中 `bOverrideFromUserDataDefinitions` 为 `true`，则在运行时，操作会尝试从目标骨骼网格体的 `UserData` 中查找 `URigMapperDefinitionUserData` 资产，并用其中的定义数组覆盖编辑器中设置的单个 `Definition`。这个过程是自动的，无需蓝图干预，但你可以通过 `Set Settings` 动态切换这个开关。

## C++ 用法

`RigMapperOp` 的 C++ 用法主要围绕 `FIKRetargetRigMapperOp` 这个操作结构体和 `FRigMapperOpHelper` 辅助类。在运行时，你需要创建和配置这些结构体，并将其注册到 `IK Retargeter` 处理器中。

### 头文件引入

```cpp
#include "RigMapperOp.h"
#include "IKRig/Retargeter/IKRetargeter.h" // 用于 FIKRetargetProcessor 等
#include "RigMapper/RigMapperDefinition.h" // 用于 URigMapperDefinition
```

### 基本用法

以下示例展示了如何在代码中设置一个使用单个 `RigMapperDefinition` 的重定向操作。

*(来源：基于 `RigMapperOp.h` 中 `FIKRetargetRigMapperOp` 的接口推断)*

```cpp
// 假设我们已经有了一个 FIKRetargetProcessor 实例 (Processor)
// 以及源骨骼和目标骨骼信息 (SourceSkeleton, TargetSkeleton)

// 1. 创建一个 RigMapper Op 设置
FIKRetargetRigMapperOpSettings OpSettings;
OpSettings.Definition = LoadObject<URigMapperDefinition>(nullptr, TEXT("/Game/RigMapperDefs/FaceRigMapper.FaceRigMapper"));
OpSettings.bCopyAllSourceCurves = false; // 不复制所有源曲线，只复制重映射后的

// 2. 创建一个 RigMapper Op 实例
FIKRetargetRigMapperOp RigMapperOp;

// 3. 初始化操作 (这会内部调用 Helper.InitializeRigMapping)
FInstancedStruct ParentOp; // 假设父操作
FIKRigLogger Log;
bool bSuccess = RigMapperOp.Initialize(
    Processor,
    SourceSkeleton,
    TargetSkeleton,
    ParentOp.GetPtr<FIKRetargetOpBase>(),
    Log
);

// 4. 将操作注册到处理器中 (实际流程由 IK Retargeter 框架管理，此处仅为示意)
// Processor.AddOp(RigMapperOp);
```

### 进阶用法

`RigMapperOp` 同时支持从目标网格体的 `UserData` 动态加载定义数组。这对于处理多个变体或需要运行时切换的场景很有用。

*(来源：基于 `FIKRetargetRigMapperUserDataOp` 和 `FRigMapperOpHelper::GetUserDataFromMesh` 推断)*

```cpp
// 使用 UserData 版本的操作
FIKRetargetRigMapperUserDataOp UserDataOp;
FIKRetargetRigMapperUserDataOpSettings UserDataOpSettings;
// UserDataOpSettings 没有 Definition 字段，它将完全依赖目标网格体的 UserData。

// 初始化并运行
FIKRigLogger Log;
UserDataOp.Initialize(Processor, SourceSkeleton, TargetSkeleton, ParentOp, Log);

// 在运行时，如果目标网格体更改，可以检查是否需要重新初始化
USkeletalMesh* NewTargetMesh = ...;
TArray<URigMapperDefinition*> CurrentDefinitions = UserDataOp.GetDefinitionsToLoad(NewTargetMesh);
if (UserDataOp.Helper.CheckReInit(CurrentDefinitions))
{
    // 需要重新初始化
    UserDataOp.Initialize(...);
}
```

## Demo 示例

一个最小的示例，展示如何在 C++ 中使用 `FRigMapperOpHelper` 手动处理一组曲线的重映射，而不通过完整的 `IK Retargeter` 框架。

### RigMapperDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "RigMapper/RigMapperProcessor.h"
#include "RigMapperOp.h" // 包含 FRigMapperOpHelper

class FRigMapperDemo
{
public:
    FRigMapperDemo();
    ~FRigMapperDemo();

    void DemoRemapCurves();

private:
    // 模拟源曲线和目标曲线
    TArray<FName> SourceCurveNames;
    TArray<float> SourceCurveValues;

    TArray<FName> TargetCurveNames;
    TArray<float> TargetCurveValues;

    // RigMapper 辅助器
    FRigMapperOpHelper Helper;
};
```

### RigMapperDemo.cpp

```cpp
#include "RigMapperDemo.h"
#include "RigMapper/RigMapperDefinition.h"

FRigMapperDemo::FRigMapperDemo()
{
    // 初始化模拟数据
    SourceCurveNames = { "source_mouth_open", "source_jaw_right" };
    SourceCurveValues = { 0.5f, 0.2f };

    TargetCurveNames = { "target_mouth_open", "target_jaw_x" };
    TargetCurveValues = { 0.0f, 0.0f };
}

FRigMapperDemo::~FRigMapperDemo()
{
}

void FRigMapperDemo::DemoRemapCurves()
{
    // 假设我们已经加载了一个 URigMapperDefinition
    URigMapperDefinition* Definition = LoadObject<URigMapperDefinition>(nullptr, TEXT("/Game/DemoMapping.DemoMapping"));
    if (!Definition)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load RigMapperDefinition"));
        return;
    }

    // 1. 初始化辅助器
    TArray<URigMapperDefinition*> Definitions = { Definition };
    if (!Helper.InitializeRigMapping(Definitions))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize RigMapperOpHelper"));
        return;
    }

    // 2. 准备输入和输出数据结构
    FRigMapperProcessor::FPoseValues InputValues;
    FRigMapperProcessor::FPoseValues OutputValues;
    // 为输入值分配空间 (这里简化了，实际需要根据定义的输入名称填充)
    InputValues.SetNum(SourceCurveNames.Num());
    for (int32 i = 0; i < SourceCurveNames.Num(); ++i)
    {
        InputValues[i].Name = SourceCurveNames[i];
        InputValues[i].Value = SourceCurveValues[i];
    }

    // 3. 调用 Helper 进行求值
    // 注意：实际使用中，你需要将动画上下文中的曲线数据转换为这种格式
    FBlendedCurve InCurve; // 需要根据你的上下文填充
    FBlendedCurve OutCurve;
    Helper.EvaluateRigMapping(InCurve, OutCurve);

    // 4. (对于批处理) 或者使用 ProcessAnimSequenceCurves 处理整个动画序列的曲线数据
    // FIKRetargetCurvesOpBase::FCurveData CurveMetaData;
    // FIKRetargetCurvesOpBase::FFrameValues FrameValues;
    // ... 填充元数据和帧数据 ...
    // FIKRetargetCurvesOpBase::FCurveData OutMetaData;
    // FIKRetargetCurvesOpBase::FFrameValues OutFrameValues;
    // Helper.ProcessAnimSequenceCurves(CurveMetaData, FrameValues, OutMetaData, OutFrameValues, false);

    UE_LOG(LogTemp, Log, TEXT("RigMapper curve remapping demo completed. Helper is valid: %s"), Helper.IsValid() ? TEXT("True") : TEXT("False"));
}
```

## 模块依赖

该插件本身模块依赖较少，但其功能强依赖于两个外部插件。在你的项目或模块的 `Build.cs` 文件中，你需要添加对 `RigMapperOp` 模块的依赖，并且该模块会自动拉取其插件依赖。

| 模块 | 用途 |
|---|---|
| `RigMapper` | 提供核心的 `URigMapperDefinition` 资产和 `FRigMapperProcessor` 映射处理器 |
| `IKRig` | 提供动画重定向框架，`IK Retargeter`、操作基类和曲线处理接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-12-18 | `ebd376bb` | [IKRig] Moved curve manipulation specific operations into a new abstract IKRetargetCurveOpBase struc | 将曲线操作移入新的抽象基类，可能影响RigMapperOp的继承关系 |
| 2025-12-15 | `b545af5b` | BuildHealth: RigMapperOp deprecation warnings disabled | 禁用了该插件的弃用警告，表明API仍不稳定 |
| 2025-12-15 | `acd4aecb` | IKRetargeter RigMapperOp refactoring | 对RigMapperOp进行了重构，可能改进了内部实现 |
| 2025-09-09 | `05dac013` | [RigMapper] second part of moving RigMapper Op into separate plugin | 插件创建初始提交，从RigMapper中分离出来 |

### 维护评价

**实验性插件，活跃开发中**。该插件创建于 2025 年 9 月，最近在 2025 年 12 月仍有重构和适配上游 `IKRig` 框架改动的提交。它明确标记为 `IsExperimentalVersion = true` 且默认未启用（`Installed = false`），表明其 API 和功能仍在快速迭代和试验阶段。

**优势**：
- 解决了高级曲线映射的实际需求。
- 与 Epic 官方的 `IKRig` 和 `RigMapper` 插件紧密集成，质量有保障。
- 持续维护，紧跟上游依赖（如 `IKRig`）的变更。

**风险与限制**：
- 作为实验性插件，其公共 API 可能在未来版本中发生 breaking changes。
- 依赖于两个同样可能变化的实验性插件（`RigMapper`, `IKRig`），增加了不确定性。
- 文档和社区资源几乎为零，学习曲线陡峭。

**推荐使用**：如果你的项目已经使用了 `IKRig` 和 `RigMapper`，并且迫切需要它们之间的桥梁来处理曲线重映射，那么可以谨慎尝试。对于生产项目，建议密切关注其版本更新日志，并做好应对 API 变更的准备。对于新项目，如果曲线映射需求不是特别复杂，可以考虑先使用 `IKRig` 自带的简单曲线操作或自行编写逻辑。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RigMapperOp)
- [官方文档](https://docs.unrealengine.com) （.uplugin 中未提供特定文档链接）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RigMapperOp/Tests) （推测路径，未在信息中确认）