# DNACalib Plugin

> DNA Calibration tool plugin

| 属性 | 值 |
|---|---|
| 中文名 | DNA校准工具 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DNACalibLib` (Runtime), `DNACalibLibTest` (Runtime), `DNACalibModule` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-21 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DNACalib) | |

## 用途

DNACalib 是一个用于校准和后处理 DNA 资产的工具库。DNA 文件是 MetaHuman 和基于 RigLogic 的数字人系统中驱动面部动画的核心数据。该插件并非运行时播放组件，而是一个底层的数据处理工具集。

它解决的核心问题是：如何以编程方式修改、清理或转换从 DCC 工具（如 Maya）导出的 DNA 数据。典型的应用场景包括：
*   **调整动画数据**：修改混合形状（BlendShape）的目标权重、关节行为映射表或动画贴图（AnimatedMap）的曲线参数。
*   **优化数据结构**：删除未使用的 LOD 级别、通道或网格，以减小资产包体大小和运行时内存占用。
*   **数据兼容性转换**：修复不同版本 DNA 文件格式的兼容性问题。
*   **程序化生成**：通过组合多个命令（Command）来批量处理或程序化生成 DNA 数据。

它依赖于 `RigLogic` 插件，并提供了底层的 C++ API 用于 DNA 数据的精细操作。

## 使用场景

*   你在使用 MetaHuman 或自定义数字人管线，发现从 DCC 导出的面部动画某些表情过渡不够自然，需要微调混合形状的权重或关节群（Joint Group）的插值数据。
*   你的项目需要支持多个 LOD 级别的数字人，希望移除低 LOD 中不需要的混合形状通道或网格数据以提升性能。
*   你正在开发自动化工具链，需要批量修复大量 DNA 资产的已知问题（如法线朝向、坐标系等）。
*   你需要将旧版本格式的 DNA 文件转换为最新版本，以利用新特性或保证引擎兼容性。

## 蓝图用法

该插件主要提供底层的 C++ 库（`DNACalibLib`），并未封装公开的 `BlueprintCallable` 函数或类。所有 DNA 数据的校准和处理均需通过 C++ 代码调用 `DNACalibLib` 模块中定义的命令（Command）来实现。

## C++ 用法

### 头文件引入

```cpp
// 引入 DNACalibLib 的核心命令头文件
#include "DNACalibLib/DNACalibLib.h"
```

### 基本用法

DNACalib 的使用模式是“命令”模式。你需要创建特定的命令对象，配置其参数，然后将命令应用到一个 `dna::Reader` 对象（DNA 数据的内存表示）上。以下示例演示了如何修改一个混合形状的目标顶点偏移量。

```cpp
// 假设 `sourceDna` 是一个从文件加载的、有效的 `dna::Reader` 对象
// 来源：测试用例框架和命令头文件的综合模式

#include "DNACalibLib/DNACalibLib.h"
#include "DNAReader.h" // 假设这是你的DNA数据读取器

// 1. 准备要修改的数据
// 例如，我们要为网格索引0的混合形状通道索引0，设置新的顶点偏移值
uint16_t meshIndex = 0;
uint16_t blendShapeChannelIndex = 0;

// 准备新的目标顶点索引和对应的XYZ偏移量
dnac::ConstArrayView<uint32_t> newTargetVertexIndices = { /* 顶点索引列表 */ };
dnac::ConstArrayView<float> newDeltaXs = { /* X偏移量列表 */ };
dnac::ConstArrayView<float> newDeltaYs = { /* Y偏移量列表 */ };
dnac::ConstArrayView<float> newDeltaZs = { /* Z偏移量列表 */ };

// 2. 创建并配置命令
dnac::SetBlendShapeTargetDeltasCommand setDeltasCmd;
setDeltasCmd.setMeshIndex(meshIndex);
setDeltasCmd.setBlendShapeChannelIndex(blendShapeChannelIndex);
setDeltasCmd.setTargetVertexIndices(newTargetVertexIndices);
setDeltasCmd.setTargetDeltas(newDeltaXs, newDeltaYs, newDeltaZs);

// 3. 将命令应用到DNA数据
setDeltasCmd.run(*sourceDna); // sourceDna 是一个可修改的 dna::MutableStreamStore 或类似对象
```

### 进阶用法

你可以按顺序组合多个命令来完成复杂的校准流程。以下伪代码展示了清理流程：先移除未使用的LOD，再调整关节行为，最后优化数据。

```cpp
// 来源：基于测试用例中多个命令头的组合使用模式

// 清理命令：移除LOD 1（假设只保留LOD 0）
dnac::RemoveLODCommand removeLOD1Cmd;
removeLOD1Cmd.setLODIndex(1);

// 调整命令：为关节索引2，在关节群索引0中，设置新的行为权重
dnac::SetJointGroupValuesCommand setJointWeightCmd;
setJointWeightCmd.setJointGroupIndex(0);
setJointWeightCmd.setJointIndex(2);
setJointWeightCmd.setValues({0.8f, 0.2f}); // 新的输入/输出权重

// 优化命令：压缩/量化数据
dnac::ClearBlendShapesCommand clearUnusedBSCmd;
// ... 配置参数以标识哪些是未使用的

// 按顺序执行命令
removeLOD1Cmd.run(*dnaData);
setJointWeightCmd.run(*dnaData);
clearUnusedBSCmd.run(*dnaData);

// 现在 `dnaData` 已经被按需校准和优化
```

## Demo 示例

一个最小的、可编译的示例，演示如何使用 `DNACalibLib` 修改 DNA 数据中的混合形状目标。

```cpp
// MyDNACalibExample.h
#pragma once

#include "CoreMinimal.h"

// 前向声明，实际使用时需要包含完整头文件
namespace dna { class Reader; }

class FMyDNACalibExample
{
public:
    // 示例函数：修改给定DNA数据中的第一个混合形状
    static void ModifyFirstBlendShape(dna::Reader* InDNAToModify);
};
```

```cpp
// MyDNACalibExample.cpp
#include "MyDNACalibExample.h"
#include "DNACalibLib/DNACalibLib.h" // 包含所有DNACalibLib命令
// 注意：实际的 `dna::Reader` 头文件来自 RigLogic 插件，需正确配置依赖

void FMyDNACalibExample::ModifyFirstBlendShape(dna::Reader* InDNAToModify)
{
    if (!InDNAToModify)
    {
        return;
    }

    // 假设我们要修改第一个网格(index 0)的第一个混合形状通道(index 0)
    const uint16_t TargetMeshIndex = 0;
    const uint16_t TargetBlendShapeChannelIndex = 0;

    // 创建命令来清除该混合形状的目标数据
    dnac::ClearBlendShapeTargetDeltasCommand clearCmd;
    clearCmd.setMeshIndex(TargetMeshIndex);
    clearCmd.setBlendShapeChannelIndex(TargetBlendShapeChannelIndex);
    clearCmd.run(*InDNAToModify); // 假设 run 接受一个可写的 DNA 对象引用

    // 准备新的顶点数据
    // 例如，让第一个顶点(索引0)沿Z轴移动1个单位
    const dnac::ConstArrayView<uint32_t> NewVertexIndices = {0};
    const dnac::ConstArrayView<float> NewDeltasX = {0.0f};
    const dnac::ConstArrayView<float> NewDeltasY = {0.0f};
    const dnac::ConstArrayView<float> NewDeltasZ = {1.0f};

    // 创建命令来设置新的混合形状目标偏移
    dnac::SetBlendShapeTargetDeltasCommand setDeltasCmd;
    setDeltasCmd.setMeshIndex(TargetMeshIndex);
    setDeltasCmd.setBlendShapeChannelIndex(TargetBlendShapeChannelIndex);
    setDeltasCmd.setTargetVertexIndices(NewVertexIndices);
    setDeltasCmd.setTargetDeltas(NewDeltasX, NewDeltasY, NewDeltasZ);
    setDeltasCmd.run(*InDNAToModify);

    UE_LOG(LogTemp, Log, TEXT("Successfully modified blend shape at mesh %d, channel %d."), TargetMeshIndex, TargetBlendShapeChannelIndex);
}
```

## 模块依赖

要使用 DNACalib 的核心功能，你的模块需要链接 `DNACalibLib`。

| 模块 | 用途 |
|---|---|
| `DNACalibLib` | 包含所有用于校准和修改 DNA 数据的 C++ 命令类 |
| `RigLogic` | DNACalib 的运行时基础，提供 DNA 数据结构和 RigLogic 系统集成 |

## 维护状态

该插件相对较新，但由 Epic 核心数字人团队（MetaHuman 相关）维护，更新活跃。

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `2f6aa301` | Improve DNA asset load performance and backwards compatible conversion by reducing data copies | 通过减少数据拷贝优化DNA资产加载性能并改进向后兼容转换 |
| 2026-05-12 | `57c5e2c7` | Update DNA and RigLogic to better handle malformed DNA files | 更新DNA和RigLogic以更好地处理格式错误的DNA文件 |
| 2026-05-12 | `0577289d` | Suppress private module include warnings for test modules (RigLogicLibTest, DNACalibLibTest, DNACali | 抑制测试模块（如DNACalibLibTest）的私有模块包含警告 |
| 2026-04-30 | `82833e51` | Fix data-race on per platform DNAConfig access during serialization | 修复序列化期间按平台访问DNAConfig的数据竞争问题 |
| 2026-04-28 | `0c7a803e` | Implement face-winding conversion in DNA to support arbitrary coordinate systems in UE | 在DNA中实现面片缠绕顺序转换以支持UE中的任意坐标系 |

### 维护评价

*   **活跃维护**：最近6个月内有多个功能性更新和错误修复，表明该插件处于核心开发路径上。
*   **核心团队支持**：由 Epic Games 创建并维护，与 MetaHuman 管线深度集成。
*   **推荐使用**：对于需要程序化处理 DNA 数据的项目（特别是涉及 MetaHuman 或自定义 RigLogic 数字人），此插件是官方推荐的工具。默认禁用（`Installed: false`）表明它并非每个项目都需要，但在需要时应主动启用。
*   **注意事项**：作为底层工具库，API 可能随 RigLogic 版本更新而变化。使用前需确保与项目使用的 RigLogic 插件版本兼容。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DNACalib)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DNACalib/Source/DNACalibLibTest/Private/dnactests)