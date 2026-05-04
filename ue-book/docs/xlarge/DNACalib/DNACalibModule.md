# DNACalib Plugin v6.12.2

> DNA Calibration tool plugin

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DNACalibLib` (Runtime), `DNACalibLibTest` (Runtime), `DNACalibModule` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DNACalib) | |

## 用途

DNACalib 是一个用于**校准和修改 DNA 数据**的工具插件。DNA（Digital Normalized Anatomy）是 MetaHuman 框架中描述角色面部骨骼、网格、混合形状和动画行为的核心数据格式。

该插件解决的核心问题是：**在运行时或编辑器中对 DNA 数据进行程序化修改**。具体包括：

- **几何变换**：对 DNA 中的顶点位置、关节位置进行平移、旋转、缩放
- **拓扑修改**：移除/重命名网格、关节、混合形状、动画映射
- **LOD 管理**：设置 LOD 层级、计算低层级 LOD 网格
- **权重调整**：修改蒙皮权重、混合形状目标增量
- **数据优化**：修剪低于阈值的混合形状目标、清除混合形状

它采用**命令模式（Command Pattern）**设计，所有操作都封装为 `IDNACalibCommand` 的子类，可以通过 `FDNACalibCommandSequence` 组合成复杂的校准流水线。

## 使用场景

- 你在使用 MetaHuman 角色，需要在不同项目间**适配面部骨骼结构**（移除/重命名关节）
- 你需要将 DNA 数据**缩放到不同比例**（如从厘米制转为米制）
- 你需要**优化 DNA 数据**，移除不需要的 LOD、混合形状或动画映射以减小文件体积
- 你需要**程序化修改顶点位置**或蒙皮权重来修正面部变形问题
- 你需要在两个 DNA 之间**计算顶点位置差异**用于增量校准
- 你需要**批量重命名** DNA 中的网格、关节或混合形状以匹配新的命名规范

## 蓝图用法

DNACalibModule 主要面向 C++ 使用，头文件中未暴露 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。但 `EDNACalibVectorOperation` 枚举标记了 `BlueprintType`，可在蓝图中使用。

### 核心枚举

| 枚举值 | 说明 |
|---|---|
| `EDNACalibVectorOperation::Interpolate` | 插值操作 |
| `EDNACalibVectorOperation::Add` | 加法操作 |
| `EDNACalibVectorOperation::Subtract` | 减法操作 |
| `EDNACalibVectorOperation::Multiply` | 乘法操作 |

## C++ 用法

### 头文件引入

```cpp
// 核心接口
#include "DNACalibCommand.h"
#include "DNACalibDNAReader.h"

// 各命令头文件（按需引入）
#include "Commands/DNACalibCommandSequence.h"
#include "Commands/DNACalibScaleCommand.h"
#include "Commands/DNACalibTranslateCommand.h"
#include "Commands/DNACalibRotateCommand.h"
#include "Commands/DNACalibSetLODsCommand.h"
#include "Commands/DNACalibSetVertexPositionsCommand.h"
#include "Commands/DNACalibSetBlendShapeTargetDeltasCommand.h"
#include "Commands/DNACalibSetSkinWeightsCommand.h"
#include "Commands/DNACalibSetNeutralJointTranslationsCommand.h"
#include "Commands/DNACalibSetNeutralJointRotationsCommand.h"
#include "Commands/DNACalibRemoveMeshCommand.h"
#include "Commands/DNACalibRemoveJointCommand.h"
#include "Commands/DNACalibRemoveBlendShapeCommand.h"
#include "Commands/DNACalibRemoveAnimatedMapCommand.h"
#include "Commands/DNACalibRemoveJointAnimationCommand.h"
#include "Commands/DNACalibRenameMeshCommand.h"
#include "Commands/DNACalibRenameJointCommand.h"
#include "Commands/DNACalibRenameBlendShapeCommand.h"
#include "Commands/DNACalibRenameAnimatedMapCommand.h"
#include "Commands/DNACalibClearBlendShapesCommand.h"
#include "Commands/DNACalibPruneBlendShapeTargetsCommand.h"
#include "Commands/DNACalibCalculateMeshLowerLODsCommand.h"
#include "Commands/DNACalibComputeVertexPositionDeltasCommand.h"
#include "Commands/DNACalibConditionalCommand.h"
#include "Commands/DNACalibVectorOperation.h"
```

### 基本用法

所有命令遵循统一模式：创建命令 → 配置参数 → 调用 `Run()` 应用到 `FDNACalibDNAReader`。

```cpp
// 假设已有 IDNAReader* SourceDNA 作为输入
FDNACalibDNAReader Output(SourceDNA);

// 1. 缩放 DNA 数据（以原点为中心放大 2 倍）
FDNACalibScaleCommand ScaleCmd(2.0f, FVector::ZeroVector);
ScaleCmd.Run(&Output);

// 2. 平移 DNA 数据
FDNACalibTranslateCommand TranslateCmd(FVector(10.0f, 0.0f, 0.0f));
TranslateCmd.Run(&Output);

// 3. 旋转 DNA 数据（绕原点旋转 90 度）
FDNACalibRotateCommand RotateCmd(FVector(0.0f, 90.0f, 0.0f), FVector::ZeroVector);
RotateCmd.Run(&Output);
```

### 进阶用法：命令序列

使用 `FDNACalibCommandSequence` 将多个命令组合为一个流水线：

```cpp
FDNACalibDNAReader Output(SourceDNA);

// 创建命令序列
FDNACalibCommandSequence Sequence;

// 添加缩放命令
FDNACalibScaleCommand ScaleCmd(0.01f, FVector::ZeroVector); // 厘米转米
Sequence.Add(&ScaleCmd);

// 添加 LOD 设置命令
TArray<uint16> LODs = {0, 1, 2};
FDNACalibSetLODsCommand LODCmd(LODs);
Sequence.Add(&LODCmd);

// 添加移除不需要的网格命令
TArray<uint16> MeshIndices = {3, 4};
FDNACalibRemoveMeshCommand RemoveMeshCmd(MeshIndices);
Sequence.Add(&RemoveMeshCmd);

// 一次性执行所有命令
Sequence.Run(&Output);
```

### 进阶用法：条件执行

使用 `FDNACalibConditionalCommand` 包装命令，仅在条件满足时执行：

```cpp
FDNACalibConditionalCommand::TCondition Condition = 
    [](IDNACalibCommand* Cmd, FDNACalibDNAReader* Reader) -> bool
    {
        // 仅当网格数量大于 2 时执行
        return Reader->GetMeshCount() > 2;
    };

FDNACalibRemoveMeshCommand RemoveCmd(2);
FDNACalibConditionalCommand CondCmd(&RemoveCmd, Condition);
CondCmd.Run(&Output);
```

### 进阶用法：修改顶点位置

```cpp
// 为网格 0 的所有顶点添加偏移
TArray<FVector> Offsets;
Offsets.SetNum(VertexCount);
for (auto& V : Offsets)
{
    V = FVector(0.0f, 0.0f, 1.0f); // Z 方向上移 1 单位
}

FDNACalibSetVertexPositionsCommand VertCmd(
    0,  // MeshIndex
    Offsets,
    EDNACalibVectorOperation::Add  // 加法操作
);
VertCmd.Run(&Output);

// 使用遮罩（Masks）控制哪些顶点受影响
TArray<float> Masks;
Masks.SetNum(VertexCount);
for (int32 i = 0; i < VertexCount; ++i)
{
    Masks[i] = (i < VertexCount / 2) ? 1.0f : 0.0f; // 仅前半部分顶点
}

FDNACalibSetVertexPositionsCommand MaskedVertCmd(
    0, Offsets, Masks, EDNACalibVectorOperation::Add
);
MaskedVertCmd.Run(&Output);
```

### 进阶用法：计算两个 DNA 之间的顶点差异

```cpp
// 比较两个 DNA 读取器，计算差异并应用到输出
FDNACalibComputeVertexPositionDeltasCommand DeltasCmd(ReaderA, ReaderB);
DeltasCmd.Run(&Output);
```

## Demo 示例

以下是一个完整的最小示例，展示如何使用 DNACalib 对 DNA 数据进行校准流水线处理：

```cpp
// DNACalibExample.h
#pragma once

#include "CoreMinimal.h"

class IDNAReader;

class FDNACalibExample
{
public:
    /** 对 DNA 数据执行完整的校准流程 */
    static void CalibrateDNA(IDNAReader* SourceDNA);
};
```

```cpp
// DNACalibExample.cpp
#include "DNACalibExample.h"

#include "DNACalibDNAReader.h"
#include "DNACalibCommandSequence.h"
#include "Commands/DNACalibScaleCommand.h"
#include "Commands/DNACalibTranslateCommand.h"
#include "Commands/DNACalibSetLODsCommand.h"
#include "Commands/DNACalibRemoveMeshCommand.h"
#include "Commands/DNACalibRemoveJointCommand.h"
#include "Commands/DNACalibRenameJointCommand.h"
#include "Commands/DNACalibPruneBlendShapeTargetsCommand.h"
#include "Commands/DNACalibSetVertexPositionsCommand.h"
#include "Commands/DNACalibVectorOperation.h"

void FDNACalibExample::CalibrateDNA(IDNAReader* SourceDNA)
{
    // 创建输出 DNA 读取器（基于源 DNA 的副本）
    FDNACalibDNAReader Output(SourceDNA);

    // 构建校准命令序列
    FDNACalibCommandSequence Pipeline;

    // 步骤 1: 缩放（厘米制转米制）
    FDNACalibScaleCommand ScaleCmd(0.01f, FVector::ZeroVector);
    Pipeline.Add(&ScaleCmd);

    // 步骤 2: 平移到世界原点
    FDNACalibTranslateCommand TranslateCmd(FVector(0.0f, 0.0f, -170.0f));
    Pipeline.Add(&TranslateCmd);

    // 步骤 3: 仅保留 LOD 0 和 LOD 1
    TArray<uint16> DesiredLODs = {0, 1};
    FDNACalibSetLODsCommand LODCmd(DesiredLODs);
    Pipeline.Add(&LODCmd);

    // 步骤 4: 移除不需要的网格
    TArray<uint16> MeshToRemove = {2, 3};
    FDNACalibRemoveMeshCommand RemoveMeshCmd(MeshToRemove);
    Pipeline.Add(&RemoveMeshCmd);

    // 步骤 5: 移除不需要的关节
    TArray<uint16> JointsToRemove = {50, 51, 52};
    FDNACalibRemoveJointCommand RemoveJointCmd(JointsToRemove);
    Pipeline.Add(&RemoveJointCmd);

    // 步骤 6: 重命名关节以匹配目标骨架
    FDNACalibRenameJointCommand RenameJointCmd(
        TEXT("old_joint_name"), TEXT("new_joint_name")
    );
    Pipeline.Add(&RenameJointCmd);

    // 步骤 7: 修剪低影响的混合形状目标
    FDNACalibPruneBlendShapeTargetsCommand PruneCmd(0.001f);
    Pipeline.Add(&PruneCmd);

    // 执行整个流水线
    Pipeline.Run(&Output);

    // Output 现在包含校准后的 DNA 数据
    UE_LOG(LogTemp, Log, TEXT("Calibrated DNA: %s, Meshes: %d, Joints: %d"),
        *Output.GetName(), Output.GetMeshCount(), Output.GetJointCount());
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RigLogic` | DNA 运行时求解器，提供 `IDNAReader` 等核心接口 |
| `DNACalibLib` | DNACalib 核心算法库（C++ 实现层） |

## 维护状态

### 近期更新

```
- 7240ae2a7328 [DNACalib] Remove FMessageLog as a dependency from DNACalibModule
- 2057280165b3 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 1/n
- 914f2d844019 Move DNACalib under public plugins folder and add DNACalib2 under restricted folder #rb violeta.vukobrat
```

- `7240ae2a7328`：移除了对 FMessageLog 的依赖，简化模块依赖关系
- `2057280165b3`：批量修复 DLL 导出标记（dllstorage），确保符号正确导出
- `914f2d844019`：将 DNACalib 从受限文件夹迁移到公开插件文件夹，同时在受限文件夹中创建 DNACalib2

### 维护评价

DNACalib 是一个**较新的插件**（2024 年 10 月创建），目前处于**活跃维护**状态。从 commit 历史可以看出：

1. **正在经历架构演进**：DNACalib2 已在受限文件夹中创建，暗示当前版本可能在未来被替代
2. **代码质量持续改进**：最近的提交集中在依赖清理和 DLL 导出修复
3. **依赖 RigLogic 插件**：作为 MetaHuman 工具链的一部分，与 Epic 的数字人类技术栈紧密绑定
4. **默认未启用**（`Installed: false`）：需要手动在项目设置中启用

**推荐使用**：如果你在开发 MetaHuman 相关的工具或需要程序化修改 DNA 数据，这是一个官方支持的可靠选择。但需注意 DNACalib2 的存在，未来可能有 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DNACalib)
- [RigLogic 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic)（依赖插件）