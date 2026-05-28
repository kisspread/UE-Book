# Rig Mapper

> A set of animation remapping features

| 属性 | 值 |
|---|---|
| 中文名 | 骨骼映射器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产类型、自定义编辑器） |
| 模块 | `RigMapper` (Runtime), `RigMapperEditor` (UncookedOnly), `RigMapperDeveloper` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-16 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RigMapper) | |

## 用途

RigMapper 是一个**动画曲线重映射工具**，用于将一套动画数据（曲线/通道）通过可配置的节点图定义转换为另一套。它解决的核心问题是：

**不同骨骼绑定（Rig）之间的动画数据转换**。例如：
- 从面部捕捉系统导出的 CSV 动画数据 → 映射到 ControlRig 的控制通道
- 一个角色的 AnimSequence → 重映射到另一个不同骨骼结构的角色
- ControlRig 节录（Section）→ 导出为 CSV 或转换为 AnimSequence

插件提供了一个**可视化节点图编辑器**来定义映射规则，支持以下运算节点：
- **加权求和（Weighted Sum）**：多个输入曲线按权重混合
- **SDK（样条曲线关键帧）**：通过关键帧定义输入输出关系
- **乘法（Multiply）**：多条输入曲线相乘
- **数学运算（Math Op）**：Min/Max/Clamp 等数学操作

## 使用场景

- 你有一个第三方面部捕捉系统导出的 CSV 动画数据，需要导入到 UE 的 ControlRig 中 → 用 RigMapper 定义映射后批量转换
- 你的项目有多个角色使用不同的骨骼绑定，需要共享动画 → 用 RigMapper 将一个角色的 AnimSequence 转换为另一个角色的
- 你需要将现有的 AnimSequence 转换为 ControlRig 的 Level Sequence 节录用于 Sequencer 工作流 → 用 RigMapper 的转换功能
- 你需要将动画数据导出为 CSV 文件用于外部工具处理 → 用 RigMapper 的导出功能

## 蓝图用法

### 核心节点

所有核心蓝图节点位于 `URigMapperEditorSubsystem`（编辑器子系统），分类为 `Editor Scripting|Animation|Rig Mapper`。

#### CSV 转换

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConvertCsv` | 重映射 CSV 文件并输出为另一个 CSV 文件 | `URigMapperEditorSubsystem` |
| `ConvertCsvToAnimSequence` | 从 CSV 导入动画数据到已有的 AnimSequence | `URigMapperEditorSubsystem` |
| `ConvertCsvToAnimSequenceNew` | 从 CSV 导入动画数据并创建新的 AnimSequence 资产 | `URigMapperEditorSubsystem` |
| `ConvertCsvToControlRigSection` | 从 CSV 导入到已有的 ControlRig 节录 | `URigMapperEditorSubsystem` |
| `ConvertCsvToControlRigSectionNew` | 从 CSV 导入并创建新的 Level Sequence 中的 ControlRig 节录 | `URigMapperEditorSubsystem` |

#### AnimSequence 转换

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConvertAnimSequence` | 将一个 AnimSequence 重映射到另一个已有的 AnimSequence | `URigMapperEditorSubsystem` |
| `ConvertAnimSequenceNew` | 将 AnimSequence 重映射并创建新资产 | `URigMapperEditorSubsystem` |
| `ConvertAnimSequenceToCsv` | 将 AnimSequence 导出为 CSV 文件 | `URigMapperEditorSubsystem` |
| `ConvertAnimSequenceToControlRigSection` | 将 AnimSequence 转换到已有的 ControlRig 节录 | `URigMapperEditorSubsystem` |
| `ConvertAnimSequenceToControlRigSectionNew` | 将 AnimSequence 转换并创建新的 Level Sequence | `URigMapperEditorSubsystem` |

#### ControlRig 节录转换

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConvertControlRigSection` | 将 ControlRig 节录重映射到另一个已有节录 | `URigMapperEditorSubsystem` |
| `ConvertControlRigSectionNew` | 将 ControlRig 节录重映射并创建新的 Level Sequence | `URigMapperEditorSubsystem` |
| `ConvertControlRigSectionToCsv` | 将 ControlRig 节录导出为 CSV | `URigMapperEditorSubsystem` |
| `ConvertControlRigSectionToAnimSequence` | 将 ControlRig 节录转换到已有的 AnimSequence | `URigMapperEditorSubsystem` |
| `ConvertControlRigSectionToAnimSequenceNew` | 将 ControlRig 节录转换并创建新 AnimSequence | `URigMapperEditorSubsystem` |

#### 辅助工具

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSequenceFromSection` | 从 ControlRig 节录获取所属的 Level Sequence | `URigMapperEditorSubsystem` |
| `GetSectionsFromSequence` | 从 Level Sequence 获取所有 ControlRig 节录 | `URigMapperEditorSubsystem` |
| `GetAnimSequenceRate` | 获取 AnimSequence 的帧率 | `URigMapperEditorSubsystem` |
| `SetAnimSequenceRate` | 设置 AnimSequence 的帧率 | `URigMapperEditorSubsystem` |

### 使用示例（蓝图描述）

**CSV 转 AnimSequence 的典型蓝图流程**：

1. 获取 `URigMapperEditorSubsystem`（使用 `Get Editor Subsystem` 节点）
2. 创建或获取 `URigMapperDefinition` 资产数组（定义映射规则）
3. 调用 `ConvertCsvToAnimSequenceNew`，传入：
   - InputFile：CSV 文件路径
   - TargetMesh：目标骨骼网格体
   - Definitions：映射定义数组
   - FrameRate：目标帧率（如 30fps）
   - NewAssetPath / NewAssetName：新资产路径和名称
4. 返回值即为创建好的 `UAnimSequence` 资产

**CSV 文件格式要求**：首行必须包含标题 `curve_name, frame_number, value`。

## C++ 用法

### 头文件引入

```cpp
#include "RigMapperEditorSubsystem.h"
#include "RigMapperDefinition.h"  // 映射定义资产
```

### 基本用法

```cpp
// 来源: Public/RigMapperEditorSubsystem.h
// 使用 EditorSubsystem 进行动画数据转换

// 获取编辑器子系统
URigMapperEditorSubsystem* RigMapperSubsystem = GEditor->GetEditorSubsystem<URigMapperEditorSubsystem>();

// 定义 CSV 文件路径
FFilePath InputCsv;
InputCsv.FilePath = TEXT("/Game/Animation/input_face_capture.csv");

FFilePath OutputCsv;
OutputCsv.FilePath = TEXT("/Game/Animation/remapped_output.csv");

// 准备映射定义数组（URigMapperDefinition 资产在编辑器中通过节点图创建）
TArray<URigMapperDefinition*> Definitions;
Definitions.Add(MyDefinitionAsset);

// 重映射 CSV 文件
bool bSuccess = URigMapperEditorSubsystem::ConvertCsv(
    InputCsv,
    OutputCsv,
    Definitions,
    false  // bOutputIntermediateCsvFiles
);
```

### 进阶用法

```cpp
// 来源: Public/RigMapperEditorSubsystem.h
// 将 CSV 数据直接导入为新的 AnimSequence 资产

FFilePath InputCsv;
InputCsv.FilePath = TEXT("/Game/Animation/mocap_data.csv");

// 目标骨骼网格体
USkeletalMesh* TargetMesh = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/Characters/SM_Hero"));

// 映射定义
TArray<URigMapperDefinition*> Definitions;
Definitions.Add(FaceRigDefinition);

// 帧率设置
FFrameRate FrameRate;
FrameRate.Numerator = 30;
FrameRate.Denominator = 1;

// 新资产路径
FDirectoryPath AssetPath;
AssetPath.Path = TEXT("/Game/Animation/Converted");

// 创建新 AnimSequence
UAnimSequence* NewSequence = URigMapperEditorSubsystem::ConvertCsvToAnimSequenceNew(
    InputCsv,
    TargetMesh,
    Definitions,
    FrameRate,
    AssetPath,
    FName("FaceAnim_Converted")
);

// 也可以转换为 ControlRig 节录
TSubclassOf<UControlRig> ControlRigClass = UMyFaceControlRig::StaticClass();

UMovieSceneControlRigParameterSection* CRSection = URigMapperEditorSubsystem::ConvertCsvToControlRigSectionNew(
    InputCsv,
    TargetMesh,
    Definitions,
    FrameRate,
    ControlRigClass,
    AssetPath,
    FName("FaceAnim_CR")
);
```

## Demo 示例

```cpp
// RigMapperExample.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "RigMapperExample.generated.h"

class URigMapperDefinition;
class UAnimSequence;
class USkeletalMesh;

UCLASS()
class URigMapperExample : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    /** 将 CSV 面部捕捉数据转换为 AnimSequence */
    UFUNCTION(BlueprintCallable, Category = "RigMapper Example")
    bool ConvertFaceCaptureToAnimSequence(
        const FString& CsvFilePath,
        USkeletalMesh* TargetMesh,
        URigMapperDefinition* MappingDefinition,
        const FString& OutputPath);
};
```

```cpp
// RigMapperExample.cpp
#include "RigMapperExample.h"
#include "RigMapperEditorSubsystem.h"
#include "RigMapperDefinition.h"
#include "Animation/AnimSequence.h"

bool URigMapperExample::ConvertFaceCaptureToAnimSequence(
    const FString& CsvFilePath,
    USkeletalMesh* TargetMesh,
    URigMapperDefinition* MappingDefinition,
    const FString& OutputPath)
{
    if (!MappingDefinition || !TargetMesh)
    {
        UE_LOG(LogTemp, Error, TEXT("RigMapperExample: 无效的输入参数"));
        return false;
    }

    // 设置输入文件路径
    FFilePath InputFile;
    InputFile.FilePath = CsvFilePath;

    // 准备定义数组
    TArray<URigMapperDefinition*> Definitions;
    Definitions.Add(MappingDefinition);

    // 设置帧率（30fps）
    FFrameRate FrameRate;
    FrameRate.Numerator = 30;
    FrameRate.Denominator = 1;

    // 设置输出路径
    FDirectoryPath AssetPath;
    AssetPath.Path = OutputPath;

    // 执行转换
    UAnimSequence* Result = URigMapperEditorSubsystem::ConvertCsvToAnimSequenceNew(
        InputFile,
        TargetMesh,
        Definitions,
        FrameRate,
        AssetPath,
        FName("ConvertedFaceAnim")
    );

    if (Result)
    {
        UE_LOG(LogTemp, Log, TEXT("RigMapperExample: 成功创建动画资产 %s"), *Result->GetName());
        return true;
    }

    UE_LOG(LogTemp, Error, TEXT("RigMapperExample: 转换失败"));
    return false;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | 插件级依赖，提供 ControlRig 运行时和编辑器支持 |
| `MovieScene` | 处理 Sequencer / Level Sequence 中的 ControlRig 节录 |
| `MovieSceneTracks` | ControlRig 参数节录（UMovieSceneControlRigParameterSection） |
| `SequencerCore` | Level Sequence 相关功能 |
| `RigMapper` | 本插件的核心 Runtime 模块（RigMapperEditor 依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `ab890466` | [RigMapper] Improved RigMapperDefinition logging and testing | 改进映射定义的日志记录和测试覆盖 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 到 float 截断的编译警告 |
| 2026-05-12 | `40287b95` | [RigMapper] Fixed broken automated tests, added missing automated tests, fixed a bug detected by upd | 修复损坏的自动化测试，补充缺失测试，修复更新检测到的 bug |
| 2026-05-12 | `edf81547` | [RigMapper] Made importing inputs/outputs from Control Rig optional in order to reduce clatter | 从 ControlRig 导入输入/输出改为可选，减少界面杂乱 |
| 2026-05-12 | `7268ff8e` | [RigMapper] Fixed a bug with comment nodes not fully enclosing selected rig mapper nodes and not tri | 修复注释节点不能完全包围选中的映射节点的 bug |

### 维护评价

**🟢 活跃维护中**

- **创建时间**：2024 年 9 月，约 2 年前
- **最近更新**：2026 年 5 月 14 日（5 次提交集中在 3 天内），包含 bug 修复、测试改进和 UI 优化
- **维护状态**：非常活跃，近期有密集的功能改进和 bug 修复
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`——表明仍处于实验阶段，API 可能发生变化
- **推荐使用**：如果你的项目有跨骨骼动画映射需求，可以积极试用。但需注意实验性状态，生产环境使用前请充分测试

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RigMapper)
- [官方文档]()（暂无）