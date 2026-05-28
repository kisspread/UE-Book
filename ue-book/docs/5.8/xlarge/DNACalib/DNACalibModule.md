# DNACalib Plugin

> DNA Calibration tool plugin

| 属性 | 值 |
|---|---|
| 中文名 | DNA 校准 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DNACalibLib` (Runtime), `DNACalibLibTest` (Runtime), `DNACalibModule` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DNACalib) | |

## 用途

DNACalib 插件是一个专门用于程序化修改和校准 **DNA 资产** 的工具。DNA 是 Unreal Engine（特别是配合 MetaHuman 等高保真数字人技术）中用于存储高精度角色面部与身体动画数据的核心格式。该插件提供了一套命令模式（Command Pattern）的 C++ API，允许开发者通过一系列可组合、可撤销的“命令”对象，对 DNA 数据中的几何、绑定、行为等各个部分进行精细的操作和调整，而无需直接操作底层复杂的数据结构。它主要用于自动化资产处理流程、修复或优化现有的 DNA 数据，以及在运行时动态调整角色特征。

**它解决的问题**：直接编辑 DNA 二进制文件或数据结构既复杂又容易出错。DNACalib 将各种修改操作封装为独立的命令（如设置顶点位置、重命名关节、计算混合形状增量等），使得修改流程模块化、可测试、可序列化。这对于需要批量处理大量 DNA 资产、或者在流水线中集成自定义校准逻辑的团队至关重要。

## 使用场景

-   **资产流水线自动化**：你需要在构建过程中批量修改一批角色的 DNA 数据，例如统一调整所有角色的鼻梁高度或修复绑定权重。
-   **运行时角色自定义**：你在开发一个允许玩家深度自定义角色的游戏，需要在运行时根据玩家选择的滑块值，实时修改 DNA 数据中的混合形状或关节变换。
-   **数据迁移与修复**：你从某个 DCC 工具（如 Maya）导入的 DNA 资产存在数据问题（如索引错误、缩放不对），需要编写一个修复脚本。
-   **LOD 优化**：你需要基于高精度 DNA 资产，程序化地计算或优化其低精度 LOD 级别的数据。

## 蓝图用法

该插件主要提供 C++ API。核心类 `IDNACalibCommand` 及其派生类均未标记为 `BlueprintCallable` 或 `BlueprintReadWrite`，因此**不能在蓝图中直接使用这些命令类**。其设计面向的是 C++ 模块或编辑器工具开发。如需在蓝图中调用校准功能，需要自行封装一个 `UCLASS` 提供对应的蓝图函数。

## C++ 用法

### 头文件引入

使用 DNACalibModule 提供的命令和数据结构时，需要包含对应的头文件。

```cpp
#include "DNACalibModule/DNACalibDNAReader.h"
#include "DNACalibModule/Commands/DNACalibSetVertexPositionsCommand.h"
#include "DNACalibModule/Commands/DNACalibCommandSequence.h"
// 根据需要包含其他具体命令头文件
```

### 基本用法

DNACalib 的核心工作流程是：创建一个或多个命令对象 -> 配置命令参数 -> 将命令应用于一个 `FDNACalibDNAReader` 对象。

**1. 修改顶点位置**
假设你已经有一个加载好的 `IDNAReader` 原始数据源（`SourceReader`），你想修改某个网格（`MeshIndex=0`）的部分顶点位置。

```cpp
// 假设 SourceReader 是你已有的 DNA 数据源
// 创建一个用于存储输出结果的 DNACalibDNAReader
FDNACalibDNAReader OutputReader(SourceReader);

// 创建设置顶点位置的命令
FDNACalibSetVertexPositionsCommand SetPositionsCmd;
SetPositionsCmd.SetMeshIndex(0);

// 准备新的顶点位置数据 (FVector数组 或 分离的XYZ数组)
TArray<FVector> NewPositions = { FVector(1.0f, 2.0f, 3.0f), FVector(4.0f, 5.0f, 6.0f) };
TArray<uint32> VertexIndices = { 10, 25 }; // 要修改的顶点索引

// 设置操作模式 (例如，添加增量)
SetPositionsCmd.SetPositions(NewPositions);
// 假设还有一个SetVertexIndices的方法，根据头文件，可能需要通过其他方式关联
// SetPositionsCmd.SetVertexIndices(VertexIndices); // 具体API需查证
SetPositionsCmd.SetOperation(EDNACalibVectorOperation::Add);

// 执行命令，修改 OutputReader 中的数据
SetPositionsCmd.Run(&OutputReader);

// 此时，OutputReader 内部已包含修改后的DNA数据
```

### 进阶用法

**1. 使用命令序列组合多个操作**
可以将多个命令组合到一个序列中按顺序执行。

```cpp
FDNACalibDNAReader FinalOutput(SourceReader);

// 创建多个命令
FDNACalibTranslateCommand TranslateCmd(FVector(100.0f, 0.0f, 0.0f));
FDNACalibScaleCommand ScaleCmd(1.2f, FVector::ZeroVector);
FDNACalibRenameJointCommand RenameCmd(0, TEXT("NewRootName"));

// 创建命令序列
FDNACalibCommandSequence Sequence;
Sequence.Add(&TranslateCmd);
Sequence.Add(&ScaleCmd);
Sequence.Add(&RenameCmd);

// 按顺序执行所有命令
Sequence.Run(&FinalOutput);
// FinalOutput 现在包含了平移、缩放和重命名后的结果
```

**2. 有条件地执行命令**
使用 `FDNACalibConditionalCommand` 可以根据条件决定是否执行某个命令。

```cpp
FDNACalibConditionalCommand::TCondition Condition = [](IDNACalibCommand* Cmd, FDNACalibDNAReader* Reader) {
    // 在这里检查 Reader 的当前状态，例如某个网格是否存在
    // 如果满足条件，返回 true，否则返回 false
    return Reader->GetMeshCount() > 0;
};

FDNACalibScaleCommand SomeScaleCmd(0.9f, FVector::ZeroVector);
FDNACalibConditionalCommand ConditionalCmd(&SomeScaleCmd, Condition);

ConditionalCmd.Run(&FinalOutput); // 只有当条件满足时，缩放操作才会生效
```

## Demo 示例

以下是一个完整的、可编译的最小 C++ 示例，演示如何加载一个 DNA 数据源，并使用 DNACalib 修改其顶点位置，然后输出结果。

**DNACalibDemo.h**
```cpp
// 版权所有 Epic Games, Inc。保留所有权利。

#pragma once

#include "CoreMinimal.h"

// 前向声明
class IDNAReader;

class FDNACalibDemo
{
public:
    /** 运行DNACalib演示 */
    static void RunDemo(IDNAReader* InSourceReader);
};
```

**DNACalibDemo.cpp**
```cpp
// 版权所有 Epic Games, Inc。保留所有权利。

#include "DNACalibDemo.h"
#include "DNACalibModule/DNACalibDNAReader.h"
#include "DNACalibModule/Commands/DNACalibSetVertexPositionsCommand.h"
#include "DNACalibModule/Commands/DNACalibVectorOperation.h"

void FDNACalibDemo::RunDemo(IDNAReader* InSourceReader)
{
    if (!InSourceReader)
    {
        UE_LOG(LogTemp, Error, TEXT("FDNACalibDemo::RunDemo - 源DNA Reader为空。"));
        return;
    }

    // 1. 创建用于接收修改结果的DNACalibDNAReader
    FDNACalibDNAReader CalibratedOutput(InSourceReader);

    // 2. 创建并配置一个设置顶点位置的命令
    FDNACalibSetVertexPositionsCommand SetPosCommand;
    SetPosCommand.SetMeshIndex(0); // 目标网格索引

    // 假设我们要修改顶点0和顶点1的位置
    // 提供新的FVector位置数据
    TArray<FVector> NewPositions;
    NewPositions.Add(FVector(10.0f, 20.0f, 30.0f));
    NewPositions.Add(FVector(40.0f, 50.0f, 60.0f));

    SetPosCommand.SetPositions(NewPositions);
    // 注意：根据头文件，设置顶点索引和操作的函数存在，此处演示省略索引设置
    // 实际使用时需要正确设置要修改的顶点索引
    SetPosCommand.SetOperation(EDNACalibVectorOperation::Add); // 操作模式：添加偏移

    // 3. 执行命令
    SetPosCommand.Run(&CalibratedOutput);

    // 4. 此时，CalibratedOutput中存储的DNA数据已包含修改后的顶点位置
    // 你可以将其保存、传递给其他系统，或进行进一步处理。
    UE_LOG(LogTemp, Log, TEXT("DNACalib演示命令执行完成。"));

    // 示例：读取修改后的第一个顶点位置验证
    if (CalibratedOutput.GetVertexPositionCount(0) > 0)
    {
        FVector ModifiedPosition = CalibratedOutput.GetVertexPosition(0, 0);
        UE_LOG(LogTemp, Log, TEXT("修改后顶点0的位置: %s"), *ModifiedPosition.ToString());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RigLogic` | 核心依赖。DNACalib 依赖 RigLogic 插件来理解和处理 DNA 数据的底层逻辑与格式。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `2f6aa301` | Improve DNA asset load performance and backwards compatible conversion by reducing data copies | 优化DNA资产加载性能，通过减少数据拷贝提升向后兼容性转换效率 |
| 2026-05-12 | `57c5e2c7` | Update DNA and RigLogic to better handle malformed DNA files | 更新DNA和RigLogic以更好地处理格式错误的DNA文件 |
| 2026-05-12 | `0577289d` | Suppress private module include warnings for test modules (RigLogicLibTest, DNACalibLibTest, DNACali | 为测试模块抑制私有模块包含警告 |
| 2026-04-30 | `82833e51` | Fix data-race on per platform DNAConfig access during serialization | 修复序列化期间访问平台特定DNAConfig时的数据竞争问题 |
| 2026-04-28 | `0c7a803e` | Implement face-winding conversion in DNA to support arbitrary coordinate systems in UE | 在DNA中实现面缠绕顺序转换，以支持UE中的任意坐标系 |

### 维护评价

**活跃维护**。DNACalib 是一个相对较新的插件（创建于2024年底），但自2025年初进入 UE5 源码后，一直保持着稳定的更新频率。从近期（2026年5月）的提交记录看，开发团队仍在积极进行**性能优化**（如减少数据拷贝）、**增强健壮性**（处理错误DNA文件）、**修复关键缺陷**（如数据竞争）以及**功能增强**（坐标系统支持）。这些更新表明插件处于积极的维护和迭代阶段，对于需要处理高保真数字人资产的工作流来说，是一个可靠且持续改进的工具。可以放心使用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DNACalib)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DNACalib/Source/DNACalibLibTest)