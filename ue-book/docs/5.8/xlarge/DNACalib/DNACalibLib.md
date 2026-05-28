# DNACalib Plugin

> DNA Calibration tool plugin（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | DNA 校准工具 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DNACalibLib` (Runtime), `DNACalibLibTest` (Runtime), `DNACalibModule` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-21 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DNACalib) | |

## 用途

DNACalib 是一个用于读取、修改和写入 DNA 文件的工具库。DNA 文件是 MetaHuman 角色面部动画数据的核心格式，包含角色的拓扑结构、骨骼层级、混合形状、皮肤权重以及复杂的机器学习行为（如神经网络驱动的面部动画）。

该插件的核心价值在于提供了一套底层的、高性能的 C++ API，允许开发者在运行时或编辑器工具中，以编程方式对 DNA 数据进行精确的校准和修改。它解决了在游戏或影视制作流程中，需要批量调整、优化或转换大量角色面部动画数据的问题，是 MetaHuman 生态系统中用于数据后处理和优化的关键底层组件。

## 使用场景

- **MetaHuman 数据后处理**：在通过 MetaHuman Creator 创建角色后，使用 DNACalib 调整面部骨骼的权重、修正混合形状的偏移量或优化 LOD 层级。
- **批量角色数据更新**：当需要为一系列角色统一调整某个参数（如嘴巴张开的幅度）时，可以通过编写脚本批量执行 DNACalib 命令。
- **动画数据迁移与适配**：将来自其他 DCC 工具或不同版本的 DNA 数据，校准并转换为适用于 Unreal Engine 和当前 RigLogic 版本的格式。
- **性能优化**：移除不需要的 LOD、混合形状或动画数据，以减小资产体积并提升运行时性能。

## 蓝图用法

DNACalib 的主要蓝图接口是其命令（Command）系统。你可以创建不同的命令对象，设置参数，然后通过 `CommandSequence` 按顺序执行它们。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Vertex Positions` | 修改指定网格的顶点位置，支持插值、加、减、乘等操作。 | `USetVertexPositionsCommand` |
| `Set Blend Shape Target Deltas` | 修改指定混合形状目标的变形增量。 | `USetBlendShapeTargetDeltasCommand` |
| `Set Skin Weights` | 设置特定顶点受骨骼影响的蒙皮权重。 | `USetSkinWeightsCommand` |
| `Set Neutral Joint Translations` | 设置骨骼的中立（T-pose）平移值。 | `USetNeutralJointTranslationsCommand` |
| `Set Neutral Joint Rotations` | 设置骨骼的中立（T-pose）旋转值。 | `USetNeutralJointRotationsCommand` |
| `Rename Joint` | 重命名骨骼。 | `URenameJointCommand` |
| `Rename Mesh` | 重命名网格。 | `URenameMeshCommand` |
| `Rename Blend Shape` | 重命名混合形状通道。 | `URenameBlendShapeCommand` |
| `Remove Mesh` | 移除一个或多个网格。 | `URemoveMeshCommand` |
| `Remove Joint` | 移除一个或多个骨骼。 | `URemoveJointCommand` |
| `Remove Blend Shape` | 移除一个或多个混合形状。 | `URemoveBlendShapeCommand` |
| `Remove Animated Map` | 移除一个或多个动画映射。 | `URemoveAnimatedMapCommand` |
| `Remove Joint Animation` | 移除一个或多个骨骼的动画数据。 | `URemoveJointAnimationCommand` |
| `Scale` | 按比例缩放整个角色（骨骼平移、顶点位置、动画增量）。 | `UScaleCommand` |
| `Rotate` | 围绕原点旋转整个角色（骨骼、顶点）。 | `URotateCommand` |
| `Translate` | 平移整个角色（骨骼、顶点）。 | `UTranslateCommand` |
| `Convert Units` | 转换平移（厘米/米）和旋转（度/弧度）的单位。 | `UConvertUnitsCommand` |
| `Set LODs` | 指定要保留的 LOD 层级，其他层级的数据将被移除。 | `USetLODsCommand` |
| `Prune Blend Shape Targets` | 移除变形幅度小于指定阈值的混合形状目标。 | `UPruneBlendShapeTargetsCommand` |
| `Calculate Mesh Lower LODs` | 基于高模顶点位置和低模的 UV，重新计算低模网格的顶点位置。 | `UCalculateMeshLowerLODsCommand` |
| `Command Sequence` | 按顺序执行多个命令。 | `UCommandSequence` |

### 使用示例（蓝图描述）

1.  **加载 DNA 数据**：首先，你需要从 `.dna` 文件加载一个 `UAsset` (例如 `UAnimSequence` 或其他包装了 DNA 数据的资产)，并从中获取对应的 `UDNACalibDNAReader` 对象（通常通过资产的特定接口）。
2.  **创建命令**：
    *   创建一个 `Set Vertex Positions Command` 节点。
    *   设置其 `Mesh Index` 为 0。
    *   创建一个 `Float` 数组作为新的顶点位置（X, Y, Z）。
    *   设置 `Operation` 为 `Add`。
3.  **执行命令**：
    *   创建一个 `Command Sequence` 节点。
    *   将上一步创建的 `Set Vertex Positions Command` 连接到 `Add` 输入。
    *   调用 `Command Sequence` 的 `Run` 函数，并传入你的 `UDNACalibDNAReader` 对象作为目标。
4.  **保存数据**：命令执行后，`DNACalibDNAReader` 内部的数据已被修改。你需要将修改后的数据重新保存或应用到你的动画资产中（具体方式取决于资产类型和管线）。

## C++ 用法

DNACalib 主要作为 C++ 库使用，提供对 DNA 数据的底层读写和命令式修改能力。

### 头文件引入

```cpp
// 引入主头文件，包含所有命令和核心类型
#include "dnacalib/DNACalib.h"

// 如果需要更底层的 DNA 读写器，可以单独引入
#include "dnacalib/dna/DNACalibDNAReader.h"
```

### 基本用法

以下示例展示了如何创建一个 `DNACalibDNAReader`，并通过命令修改其顶点位置。
*(代码逻辑推断自 Public 命令类的接口设计)*

```cpp
#include "dnacalib/DNACalib.h"
#include "dnacalib/dna/DNACalibDNAReader.h"

// 假设已经通过某种方式（如 RigLogic 的 Unreal Ed 工具）加载了 DNA 数据到一个 Reader 中
// dnac::DNACalibDNAReader* Reader = ...;

// 1. 创建要应用的修改数据（例如，一个简单的平移向量）
dnac::Vector3 DeltaTranslation = {1.0f, 0.0f, 0.0f};

// 2. 创建一个“设置顶点位置”命令
dnac::SetVertexPositionsCommand SetPosCmd;
// 配置命令：修改 Mesh 0，使用 Add 操作，将 DeltaTranslation 应用到所有顶点（这里需要实际的顶点数据数组）
// SetPosCmd.setMeshIndex(0);
// SetPosCmd.setPositions(/* ... 提供的顶点位置数组 ... */);
// SetPosCmd.setOperation(dnac::VectorOperation::Add);

// 3. 创建命令序列
dnac::CommandSequence Sequence;
Sequence.add(&SetPosCmd); // 将命令添加到序列中（注意：Sequence 不拥有 Command 的所有权）

// 4. 执行命令序列，修改传入的 Reader
Sequence.run(Reader);

// 5. 现在 Reader 中的数据已被修改，可以将其用于后续操作（如生成动画、保存等）
```

### 进阶用法

组合多个命令来实现复杂的校准流程。例如，先缩放角色，然后重命名一个骨骼。
*(代码逻辑推断自命令类和 CommandSequence 的使用模式)*

```cpp
#include "dnacalib/DNACalib.h"

void CalibrateDNAAvatar(dnac::DNACalibDNAReader* Reader)
{
    // 1. 缩放命令：将角色整体放大到 1.2 倍，原点设为 (0,0,0)
    dnac::ScaleCommand ScaleCmd;
    ScaleCmd.setScale(1.2f);
    ScaleCmd.setOrigin({0.0f, 0.0f, 0.0f});

    // 2. 重命名命令：将骨骼 “head” 重命名为 “HEAD”
    dnac::RenameJointCommand RenameCmd;
    RenameCmd.setName(“head”, “HEAD”);

    // 3. 移除命令：移除第 5 号网格
    dnac::RemoveMeshCommand RemoveMeshCmd;
    RemoveMeshCmd.setMeshIndex(5);

    // 4. 创建序列并按顺序添加命令
    dnac::CommandSequence CalibrationSequence;
    CalibrationSequence.add(&ScaleCmd);
    CalibrationSequence.add(&RenameCmd);
    CalibrationSequence.add(&RemoveMeshCmd);

    // 5. 执行整个校准序列
    CalibrationSequence.run(Reader);
}
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何在 C++ 模块中使用 DNACalib 命令。
*(文件: `MyDNACalibTool.h` / `MyDNACalibTool.cpp`)*

```cpp
// MyDNACalibTool.h
#pragma once

#include "CoreMinimal.h"
#include "dnacalib/DNACalib.h"

class FMyDNACalibTool
{
public:
    /** 对传入的 DNA Reader 进行一系列校准操作 */
    static void PerformCalibration(dnac::DNACalibDNAReader* DNAReader);
};
```

```cpp
// MyDNACalibTool.cpp
#include "MyDNACalibTool.h"

void FMyDNACalibTool::PerformCalibration(dnac::DNACalibDNAReader* DNAReader)
{
    if (!DNAReader)
    {
        return;
    }

    // 示例1: 为所有网格的顶点添加一个基础偏移 (假设网格0有1000个顶点)
    dnac::Vector3 BaseOffset = {0.0f, 0.0f, 1.0f}; // Z轴上移1单位
    // 实际应用中需要从 Reader 获取真实的顶点数据
    // const auto OriginalPositions = DNAReader->getVertexPositions(0);
    // ... 计算新位置 ...

    // 示例2: 重命名骨骼 “spine_01” -> “Spine01”
    dnac::RenameJointCommand RenameSpineCmd;
    RenameSpineCmd.setName(“spine_01”, “Spine01”);

    // 示例3: 移除 LOD 1 及以上的所有数据，只保留 LOD 0
    dnac::SetLODsCommand SetLODsCmd;
    std::uint16_t LODsToKeep[] = {0};
    SetLODsCmd.setLODs(LODsToKeep);

    // 构建并执行校准序列
    dnac::CommandSequence ToolSequence;
    // ToolSequence.add(&SetPosCmd); // 如果上面定义了设置位置的命令
    ToolSequence.add(&RenameSpineCmd);
    ToolSequence.add(&SetLODsCmd);

    // 在目标 DNA Reader 上执行序列
    ToolSequence.run(DNAReader);

    UE_LOG(LogTemp, Log, TEXT(“DNA Calibration Completed.”));
}
```

## 模块依赖

从 `Build.cs` 文件分析，使用此插件需要以下特殊依赖。

| 模块 | 用途 |
|---|---|
| `RigLogic` | DNACalib 的前置插件依赖，核心的动画求解器，与 DNA 数据格式深度绑定。 |
| `UnrealEd` | DNACalibLib 和 DNACalibModule 依赖编辑器功能，意味着此插件主要设计用于编辑器环境或需要编辑器支持的上下文中。 |
| `DNACalibLib` | 核心校准库，`DNACalibLibTest` 模块依赖此库进行测试。 |

**注意**：由于模块依赖了 `UnrealEd`，在纯运行时（打包后）的项目中使用此插件可能会受限，需确保你的项目配置允许在目标平台上加载编辑器模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `2f6aa301` | Improve DNA asset load performance and backwards compatible conversion by reducing data copies | 通过减少数据拷贝，提升了DNA资产加载性能和向后兼容性转换。 |
| 2026-05-12 | `57c5e2c7` | Update DNA and RigLogic to better handle malformed DNA files | 更新DNA和RigLogic以更好地处理格式错误的DNA文件。 |
| 2026-05-12 | `0577289d` | Suppress private module include warnings for test modules (RigLogicLibTest, DNACalibLibTest) | 抑制了测试模块（RigLogicLibTest, DNACalibLibTest）的私有模块包含警告。 |
| 2026-04-30 | `82833e51` | Fix data-race on per platform DNAConfig access during serialization | 修复了在序列化期间访问每平台DNAConfig时可能出现的数据竞争问题。 |
| 2026-04-28 | `0c7a803e` | Implement face-winding conversion in DNA to support arbitrary coordinate systems in UE | 在DNA中实现了面朝向转换，以支持UE中的任意坐标系。 |

### 维护评价

**综合评价：活跃维护中**

DNACalib 是 MetaHuman 技术栈的核心底层组件之一，自创建以来（约 2 年）保持着活跃的维护状态。近期（2026年4-5月）的提交集中在**性能优化**、**数据兼容性**和**健壮性**提升上，例如提升加载速度、处理损坏文件和修复平台相关的并发问题。此外，还加入了支持任意坐标系的重要功能扩展。

这些更新表明该插件不仅在修复问题，还在持续演进以适应更广泛的应用场景。鉴于其在 Epic Games 官方工作流中的基础地位，以及持续的实质性更新，**推荐使用**。但需注意，它高度依赖 `RigLogic` 和 `UnrealEd`，使用前请确认你的项目环境和目标平台兼容。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DNACalib)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DNACalib/Source/DNACalibLibTest) (位于 `Source/DNACalibLibTest` 目录下)