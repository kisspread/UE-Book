# Rig Mapper

> A set of animation remapping features

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RigMapper` (Runtime), `RigMapperEditor` (UncookedOnly), `RigMapperDeveloper` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-16 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/RigMapper) | |

## 用途

RigMapper 是一个**面部动画曲线重映射**插件，用于将一组输入动画曲线（如面部捕捉数据）通过数学变换映射为另一组输出曲线（如目标角色的 ControlRig 控制值）。

核心解决的问题：**不同面部骨骼/绑定系统之间的动画数据转换**。当你从一个面部捕捉系统（如 iPhone ARKit）获取的曲线名称和范围，与目标角色 ControlRig 的曲线名称和范围不一致时，RigMapper 提供了一个数据驱动的映射方案，而不是硬编码转换逻辑。

插件的设计基于一个**有向无环图（DAG）节点计算模型**：输入 → 特征节点（加权求和、SDK分段线性、乘法） → 输出。支持多层链式定义，即第一层的输出可以作为第二层的输入。

## 使用场景

- 你有 iPhone ARKit 的面部捕捉 CSV 数据，需要映射到 MetaHuman 的 ControlRig → 用 RigMapper 的 CSV 转换功能
- 你需要将一个角色的面部动画重定向到另一个不同绑定的角色 → 用 RigMapper Definition 定义映射规则
- 你需要在动画蓝图中实时进行曲线重映射 → 用 AnimGraph 中的 RigMapper 节点
- 你使用 IK Retargeter 做全身重定向，同时需要处理面部曲线 → 用 RigMapper Op（IKRetargeter 集成）
- 你需要批量转换大量动画序列中的面部曲线数据 → 用 EditorSubsystem 的批量转换 API

## 蓝图用法

### 核心节点 — Definition 管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadFromJsonFile` | 从 JSON 文件加载映射定义 | `URigMapperDefinition` |
| `LoadFromJsonString` | 从 JSON 字符串加载映射定义 | `URigMapperDefinition` |
| `ExportAsJsonString` | 将定义导出为 JSON 字符串 | `URigMapperDefinition` |
| `ExportAsJsonFile` | 将定义导出为 JSON 文件 | `URigMapperDefinition` |
| `Validate` | 验证定义是否有效（所有引用的输入都存在） | `URigMapperDefinition` |
| `IsDefinitionValid` | 检查定义是否通过验证 | `URigMapperDefinition` |
| `Empty` | 清空定义的所有数据 | `URigMapperDefinition` |

### 核心节点 — Linked Definitions（链式定义）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BakeDefinitions` | 将多个链式定义烘焙为单个合并定义 | `URigMapperLinkedDefinitions` |
| `Validate` | 验证链式定义的有效性 | `URigMapperLinkedDefinitions` |

### 核心节点 — 编辑器批量转换

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConvertCsv` | CSV → CSV 重映射 | `URigMapperEditorSubsystem` |
| `ConvertCsvToAnimSequence` | CSV → 已有 AnimSequence | `URigMapperEditorSubsystem` |
| `ConvertCsvToAnimSequenceNew` | CSV → 新建 AnimSequence | `URigMapperEditorSubsystem` |
| `ConvertCsvToControlRigSection` | CSV → 已有 ControlRig Section | `URigMapperEditorSubsystem` |
| `ConvertCsvToControlRigSectionNew` | CSV → 新建 ControlRig Section | `URigMapperEditorSubsystem` |
| `ConvertAnimSequence` | AnimSequence → 已有 AnimSequence | `URigMapperEditorSubsystem` |
| `ConvertAnimSequenceNew` | AnimSequence → 新建 AnimSequence | `URigMapperEditorSubsystem` |
| `ConvertAnimSequenceToCsv` | AnimSequence → CSV 文件 | `URigMapperEditorSubsystem` |
| `ConvertAnimSequenceToControlRigSection` | AnimSequence → ControlRig Section | `URigMapperEditorSubsystem` |
| `ConvertAnimSequenceToControlRigSectionNew` | AnimSequence → 新建 ControlRig Section | `URigMapperEditorSubsystem` |
| `ConvertControlRigSection` | ControlRig Section → 已有 Section | `URigMapperEditorSubsystem` |
| `ConvertControlRigSectionNew` | ControlRig Section → 新建 Section | `URigMapperEditorSubsystem` |
| `ConvertControlRigSectionToCsv` | ControlRig Section → CSV | `URigMapperEditorSubsystem` |
| `ConvertControlRigSectionToAnimSequence` | ControlRig Section → AnimSequence | `URigMapperEditorSubsystem` |
| `ConvertControlRigSectionToAnimSequenceNew` | ControlRig Section → 新建 AnimSequence | `URigMapperEditorSubsystem` |

### 使用示例（蓝图描述）

**CSV 转 AnimSequence 示例：**
1. 创建 `URigMapperDefinition` 资产并加载 JSON 映射文件
2. 调用 `ConvertCsvToAnimSequenceNew`，传入 CSV 文件路径、目标 SkeletalMesh、Definition 数组、帧率、输出路径
3. 函数返回新建的 `UAnimSequence*`

**实时动画蓝图示例：**
1. 在 AnimGraph 中添加 "Rig Mapper" 节点
2. 连接 Source Pose 输入
3. 在节点属性中设置 `Definitions` 数组（一个或多个 `URigMapperDefinition`）
4. 调整 `Alpha` 控制混合程度（1.0 = 完全替换，0.0 = 保持原始）

## C++ 用法

### 头文件引入

```cpp
#include "RigMapperDefinition.h"
#include "RigMapperProcessor.h"
#include "RigMapper.h"
```

### 基本用法 — 创建 Definition 并评估

从测试用例提取（`RigMapperTests.cpp`）：

```cpp
// 创建 Definition 资产
URigMapperDefinition* Definition = NewObject<URigMapperDefinition>(
    GetTransientPackage(), NAME_None, RF_Transient);

// 定义输入曲线名称
Definition->Inputs = { TEXT("EyeBlinkLeft"), TEXT("EyeBlinkRight"), TEXT("JawOpen") };

// 添加加权求和特征：output = 0.5 * EyeBlinkLeft + 0.5 * EyeBlinkRight
FRigMapperWsFeature WSFeature(TEXT("BlinkCombined"));
WSFeature.Inputs.Add(TEXT("EyeBlinkLeft"), 0.5);
WSFeature.Inputs.Add(TEXT("EyeBlinkRight"), 0.5);
Definition->Features.WeightedSums.Add(WSFeature);

// 添加 SDK（分段线性）特征：对 JawOpen 做范围重映射
FRigMapperSdkFeature SDKFeature(TEXT("JawRemapped"));
SDKFeature.Input = TEXT("JawOpen");
SDKFeature.Keys = { {0.0, 0.0}, {0.5, 0.6}, {1.0, 1.0} };  // In→Out 键值对
Definition->Features.SDKs.Add(SDKFeature);

// 添加乘法特征：两个输入相乘
FRigMapperMultiplyFeature MultFeature(TEXT("MultiplyTest"));
MultFeature.Inputs = { TEXT("EyeBlinkLeft"), TEXT("JawOpen") };
Definition->Features.Multiply.Add(MultFeature);

// 定义输出映射：输出曲线名 → 特征名
Definition->Outputs.Add(TEXT("ctrl_blink"), TEXT("BlinkCombined"));
Definition->Outputs.Add(TEXT("ctrl_jaw"), TEXT("JawRemapped"));
Definition->Outputs.Add(TEXT("ctrl_mult"), TEXT("MultiplyTest"));

// 验证
Definition->Validate();
```

### 基本用法 — 使用 Processor 批量评估

```cpp
// 从 Definition 创建 Processor
FRigMapperProcessor Processor(Definition);

// 准备输入
TArray<FName> InputNames = Processor.GetInputNames();
FRigMapperProcessor::FPoseValues InputValues;
InputValues.Add(0.25);  // EyeBlinkLeft
InputValues.Add(0.4);   // EyeBlinkRight
InputValues.Add(0.75);  // JawOpen

// 评估单帧
FRigMapperProcessor::FPoseValues OutputValues;
bool bSuccess = Processor.EvaluateFrame(InputNames, InputValues, OutputValues);

// 获取输出曲线名称
TArray<FName> OutCurveNames;
Processor.EvaluateFrame(InputNames, InputValues, OutCurveNames, OutputValues);
```

### 进阶用法 — 多层链式评估

来自测试用例 `CreateValidRigMapperDefinitions1()` 的链式定义模式：

```cpp
// 第一层：原始输入 → 中间特征
TArray<URigMapperDefinition*> Definitions;
Definitions.Add(Definition1);  // 输入: InputVal1-5, 输出: OutputVal1-6
Definitions.Add(Definition2);  // 输入: OutputVal1-6（第一层的输出）, 输出: 最终结果

// 使用 Processor 一次性处理多层
FRigMapperProcessor Processor(Definitions);

// 评估时会自动将第一层的输出传递给第二层的输入
FRigMapperProcessor::FPoseValues FinalOutput;
Processor.EvaluateFrame(InputNames, InputValues, FinalOutput);
```

### 进阶用法 — 直接使用 FRigMapper（底层 API）

```cpp
using namespace FacialRigMapping;

FRigMapper RigMapper;
RigMapper.LoadDefinition(Definition);

// 设置输入值
RigMapper.SetDirty();  // 重置缓存，必须在每次评估前调用
RigMapper.SetDirectValue(FName("EyeBlinkLeft"), 0.5);
RigMapper.SetDirectValue(FName("EyeBlinkRight"), 0.3);
RigMapper.SetDirectValue(FName("JawOpen"), 0.8);

// 获取输出
TMap<FName, double> Outputs = RigMapper.GetOutputValues();
// Outputs["ctrl_blink"] == 0.4 (0.5*0.5 + 0.3*0.5)
```

## Demo 示例

### Build.cs 依赖

```csharp
// Runtime 模块依赖
PublicDependencyModuleNames.AddRange(new string[] {
    "RigMapper"
});
```

### 最小示例 — 动画蓝图中使用

```cpp
// MyAnimInstance.h
#pragma once
#include "Animation/AnimInstance.h"
#include "RigMapperProcessor.h"
#include "MyAnimInstance.generated.h"

UCLASS()
class UMyAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Rig Mapper")
    TObjectPtr<URigMapperDefinition> FaceDefinition;

    // 在动画蓝图中调用
    UFUNCTION(BlueprintCallable, Category = "Rig Mapper")
    void RemapFaceCurves(UPARAM(ref) FBlendedCurve& InOutCurves);

private:
    FRigMapperProcessor Processor;
    bool bInitialized = false;
};
```

```cpp
// MyAnimInstance.cpp
#include "MyAnimInstance.h"

void UMyAnimInstance::RemapFaceCurves(FBlendedCurve& InOutCurves)
{
    if (!FaceDefinition) return;

    if (!bInitialized)
    {
        Processor = FRigMapperProcessor(FaceDefinition);
        bInitialized = true;
    }

    if (!Processor.IsValid()) return;

    // 收集输入曲线值
    const TArray<FName>& InputNames = Processor.GetInputNames();
    FRigMapperProcessor::FPoseValues InputValues;
    InputValues.SetNum(InputNames.Num());

    for (int32 i = 0; i < InputNames.Num(); ++i)
    {
        float Value = InOutCurves.Get(InputNames[i]);
        InputValues[i] = Value;
    }

    // 评估
    FRigMapperProcessor::FPoseValues OutputValues;
    Processor.EvaluateFrame(InputNames, InputValues, OutputValues);

    // 写回输出曲线
    const TArray<FName>& OutputNames = Processor.GetOutputNames();
    for (int32 i = 0; i < OutputNames.Num(); ++i)
    {
        if (OutputValues[i].IsSet())
        {
            InOutCurves.Set(OutputNames[i], OutputValues[i].GetValue());
        }
    }
}
```

## JSON 定义格式

RigMapper 支持从 JSON 文件加载定义。格式如下：

```json
{
    "inputs": ["EyeBlinkLeft", "EyeBlinkRight", "JawOpen"],
    "features": {
        "BlinkCombined": {
            "type": "weighted_sum",
            "input_features": ["EyeBlinkLeft", "EyeBlinkRight"],
            "params": {
                "weights": [0.5, 0.5],
                "min": 0.0,
                "max": 1.0
            }
        },
        "JawRemapped": {
            "type": "sdk",
            "input_features": ["JawOpen"],
            "params": {
                "in_val": [0.0, 0.5, 1.0],
                "out_val": [0.0, 0.6, 1.0]
            }
        },
        "MultiplyTest": {
            "type": "multiply",
            "input_features": ["EyeBlinkLeft", "JawOpen"]
        }
    },
    "outputs": {
        "ctrl_blink": "BlinkCombined",
        "ctrl_jaw": "JawRemapped",
        "ctrl_mult": "MultiplyTest"
    },
    "null_outputs": ["UnusedOutput"]
}
```

### 特征类型说明

| 类型 | JSON type 值 | 说明 |
|---|---|---|
| **Weighted Sum** | `weighted_sum` | 加权求和：output = Σ(input_i × weight_i)，可设置 min/max 范围 |
| **SDK (分段线性)** | `sdk` | 分段线性插值：基于输入值在键值对之间线性插值 |
| **Multiply** | `multiply` | 乘法：output = input_1 × input_2 × ... × input_n |

### Null Outputs

`null_outputs` 中列出的输出曲线在当前层不会被设置值，但在链式定义中可以被后续层引用（作为 passthrough）。这在你需要将某个中间值传递到下一层但不在当前层输出时很有用。

## 模块依赖

### RigMapper（Runtime）

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（DataAsset 等） |
| `ControlRig` | ControlRig 集成 |
| `AnimationCore` | 动画核心类型 |
| `Json` | JSON 解析（Definition 加载/导出） |

### RigMapperEditor（UncookedOnly）

| 模块 | 用途 |
|---|---|
| `RigMapper` | Runtime 模块 |
| `UnrealEd` | 编辑器框架 |
| `GraphEditor` | Definition 可视化编辑器 |
| `AnimGraph` | 动画图节点支持 |
| `BlueprintGraph` | 蓝图集成 |
| `Sequencer` | Sequencer/LevelSequence 集成 |
| `AssetTools` | 资产类型注册 |
| `Slate` / `SlateCore` | UI 框架 |

### RigMapperOp（Runtime，独立插件）

| 模块 | 用途 |
|---|---|
| `RigMapper` | Runtime 模块 |
| `IKRig` | IK Retargeter 集成 |

## 编辑器功能

### Definition 资产编辑器

双击 `URigMapperDefinition` 资产会打开专用编辑器，包含：
- **Graph 面板**：节点图可视化，显示 Input → Features → Output 的关系
- **Structure 面板**：树形结构显示所有输入、特征、输出
- **Details 面板**：属性编辑

支持从 JSON 文件导入定义，也支持在编辑器中手动创建和编辑。

### RigMapper AnimGraph 节点

在动画蓝图中使用 "Rig Mapper" 节点：
- **Source Pose**：输入姿态
- **Definitions**：映射定义数组（支持多层链式）
- **Alpha**：混合权重（0-1），用于在原始曲线和映射曲线之间插值
- **LOD Threshold**：LOD 阈值，超过此 LOD 级别时节点停止评估

### Skeletal Mesh 覆盖

可以通过在 SkeletalMesh 上添加 `URigMapperDefinitionUserData` 来覆盖 AnimGraph 节点中设置的定义。这允许同一个动画蓝图在不同 SkeletalMesh 上使用不同的映射规则。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-09-09 | `2024999a` | 将 RigMapper Op 拆分为独立插件 RigMapperOp，集成到 IKRetargeter Op Stack |
| 2025-06-24 | `255edf13` | 修复 Subsystem 中的若干转换函数 bug |
| 2025-07-10 | `9803c443` | 添加 UE_INLINE_GENERATED_CPP_BY_NAME（代码整理） |

### 维护评价

- **创建时间**：2024-09-16，约 1.6 年前
- **活跃度**：活跃维护中。2025 年有多次功能性更新（RigMapperOp 拆分、Subsystem bug 修复）
- **实验性状态**：标记为 `IsExperimentalVersion=true`，`EnabledByDefault=false`，需要手动启用
- **代码质量**：代码结构清晰，有完整的自动化测试（`RigMapperTests.cpp`，约 1300 行），覆盖了 Definition 验证、JSON 导入导出、多层链式评估、Processor 批量处理等核心功能
- **已知限制**：
  - 标记为实验性，API 可能变化
  - `EvaluateFrames_Interp` 方法尚未实现（代码中有 `// todo`）
  - 骨骼变换支持尚未完成（代码中有 `// todo: handle bones`）
  - 依赖 ControlRig 插件
- **推荐**：✅ 推荐用于面部动画曲线重映射场景。虽然是实验性插件，但功能完整，测试覆盖充分，且 Epic 在持续维护

## 相关链接

- [源码 — RigMapper](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/RigMapper)
- [源码 — RigMapperOp](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/RigMapperOp)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/Animation/RigMapper/Source/RigMapperDeveloper/Private/Tests/RigMapperTests.cpp)
