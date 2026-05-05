# DNACalib Plugin v6.12.2

> DNA Calibration tool plugin

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DNACalibLib` (Runtime), `DNACalibLibTest` (Runtime), `DNACalibModule` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DNACalib) | |

---

## 用途

DNACalib 是一个 **DNA 数据校准/后处理工具库**，用于在运行时对 MetaHuman 使用的 DNA（Digital Native Asset）数据进行程序化修改。

DNA 是 MetaHuman 面部动画系统（RigLogic）的核心数据格式，包含骨骼（joints）、混合变形（blend shapes）、蒙皮权重（skin weights）、网格（meshes）、LOD 等信息。DNACalib 提供了一套**命令模式（Command Pattern）**架构，允许你对 DNA 数据执行各种变换操作：

- **几何变换**：平移、旋转、缩放骨骼和顶点
- **数据裁剪**：移除不需要的骨骼、网格、混合变形、动画映射
- **重命名**：批量重命名骨骼、网格、混合变形通道
- **数据设置**：直接设置顶点位置、蒙皮权重、中性姿态等
- **LOD 管理**：设置 LOD 级别、重新计算低 LOD 网格
- **单位转换**：在不同长度/角度单位间转换

**为什么存在**：MetaHuman 从 MetaHuman Creator 导出的 DNA 数据可能不完全匹配你的项目需求——比例不对、有多余的骨骼、命名不一致、LOD 需要调整等。DNACalib 让你可以在导入 UE 后、运行时动态地对 DNA 做这些调整，而不需要回到 DCC 工具重新导出。

## 使用场景

- 你导入了一个 MetaHuman 但需要**缩放**到不同体型 → 用 `ScaleCommand`
- 你的项目只需要面部动画，不需要身体骨骼 → 用 `RemoveJointCommand` 裁剪
- DNA 中的骨骼命名与你的动画蓝图不匹配 → 用 `RenameJointCommand` 批量重命名
- 你需要将厘米单位的 DNA 转换为米单位 → 用 `ConvertUnitsCommand`
- 你想清除所有混合变形数据，只保留骨骼驱动 → 用 `ClearBlendShapesCommand`
- 你需要对顶点位置做程序化修改（如修正穿模）→ 用 `SetVertexPositionsCommand`
- 你想组合多个操作一次性执行 → 用 `CommandSequence`

## 蓝图用法

**本插件不提供蓝图接口。** DNACalib 是一个纯 C++ 库，所有 API 都在 `dnac` 命名空间下，没有 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。需要在 C++ 代码中使用。

## C++ 用法

### 头文件引入

引入所有命令的统一头文件：

```cpp
#include "dnacalib/DNACalib.h"
```

或按需引入单个命令：

```cpp
#include "dnacalib/commands/TranslateCommand.h"
#include "dnacalib/commands/ScaleCommand.h"
#include "dnacalib/commands/CommandSequence.h"
#include "dnacalib/dna/DNACalibDNAReader.h"
```

### 核心概念

DNACalib 的架构基于三个核心类：

| 类 | 职责 |
|---|---|
| `dnac::Command` | 抽象命令基类，所有操作都继承它 |
| `dnac::DNACalibDNAReader` | 可变 DNA 读取器，继承自 `dna::Reader`，命令在此对象上执行 |
| `dnac::CommandSequence` | 命令序列，按顺序执行多个命令 |

**基本工作流**：
1. 创建 `DNACalibDNAReader`（从现有 DNA 数据复制或新建）
2. 创建所需的命令对象
3. 调用 `command.run(reader)` 执行单个命令，或用 `CommandSequence` 批量执行
4. 使用修改后的 DNA 数据

### 基本用法 — 单个命令

```cpp
#include "dnacalib/DNACalib.h"

using namespace dnac;

// 假设已有 dna::Reader* sourceDNA 从文件加载

// 1. 创建可变 DNA 副本
DNACalibDNAReader* reader = DNACalibDNAReader::create(sourceDNA);

// 2. 平移所有根骨骼和顶点
TranslateCommand translateCmd;
translateCmd.setTranslation({10.0f, 0.0f, 5.0f});  // X=10, Y=0, Z=5
translateCmd.run(reader);

// 3. 缩放（从原点缩放 2 倍）
ScaleCommand scaleCmd;
scaleCmd.setScale(2.0f);
scaleCmd.setOrigin({0.0f, 0.0f, 0.0f});
scaleCmd.run(reader);

// 4. 使用修改后的 reader...

// 5. 清理
DNACalibDNAReader::destroy(reader);
```

### 基本用法 — 命令序列

```cpp
#include "dnacalib/DNACalib.h"

using namespace dnac;

DNACalibDNAReader* reader = DNACalibDNAReader::create(sourceDNA);

// 创建多个命令
TranslateCommand translateCmd({0.0f, 0.0f, -90.0f});
ScaleCommand scaleCmd(100.0f, {0.0f, 0.0f, 0.0f});  // 厘米转米的反向操作
ConvertUnitsCommand convertCmd(TranslationUnit::cm, RotationUnit::degrees);

// 组合成序列
CommandSequence sequence;
sequence.add(&translateCmd);
sequence.add(&scaleCmd);
sequence.add(&convertCmd);

// 一次性执行所有命令
sequence.run(reader);

DNACalibDNAReader::destroy(reader);
```

### 进阶用法 — 条件命令

```cpp
#include "dnacalib/DNACalib.h"

using namespace dnac;

DNACalibDNAReader* reader = DNACalibDNAReader::create(sourceDNA);

// 只在 DNA 包含混合变形时才清除它们
ClearBlendShapesCommand clearCmd;

// 定义条件：检查 blend shape 数量是否大于 0
auto condition = [](Command* cmd, DNACalibDNAReader* output) -> bool {
    return output->getBlendShapeChannelCount() > 0;
};

ConditionalCommand<decltype(clearCmd), decltype(condition)> conditionalCmd;
conditionalCmd.setCommand(&clearCmd);
conditionalCmd.setCondition(condition);
conditionalCmd.run(reader);

DNACalibDNAReader::destroy(reader);
```

### 进阶用法 — 裁剪与重命名流水线

```cpp
#include "dnacalib/DNACalib.h"

using namespace dnac;

DNACalibDNAReader* reader = DNACalibDNAReader::create(sourceDNA);

// 1. 只保留 LOD 0 和 LOD 1
SetLODsCommand lodsCmd;
std::uint16_t lods[] = {0, 1};
lodsCmd.setLODs(ConstArrayView<std::uint16_t>(lods, 2));
lodsCmd.run(reader);

// 2. 移除指定索引的骨骼
RemoveJointCommand removeJointCmd;
std::uint16_t jointsToRemove[] = {5, 12, 18};
removeJointCmd.setJointIndices(ConstArrayView<std::uint16_t>(jointsToRemove, 3));
removeJointCmd.run(reader);

// 3. 重命名骨骼
RenameJointCommand renameCmd;
renameCmd.setName("old_joint_name", "new_joint_name");
renameCmd.run(reader);

// 4. 重命名网格
RenameMeshCommand renameMeshCmd;
renameMeshCmd.setName(0, "face_mesh_renamed");
renameMeshCmd.run(reader);

// 5. 修剪微小混合变形目标
PruneBlendShapeTargetsCommand pruneCmd;
pruneCmd.setThreshold(0.001f);  // 移除绝对值 <= 0.001 的 delta
pruneCmd.run(reader);

DNACalibDNAReader::destroy(reader);
```

### 进阶用法 — 修改顶点位置与蒙皮权重

```cpp
#include "dnacalib/DNACalib.h"

using namespace dnac;

DNACalibDNAReader* reader = DNACalibDNAReader::create(sourceDNA);

// 修改网格 0 的顶点位置（加法操作，带权重遮罩）
std::uint16_t meshIndex = 0;
float newXPositions[] = {0.1f, 0.2f, 0.3f};
float newYPositions[] = {0.0f, 0.0f, 0.0f};
float newZPositions[] = {0.0f, 0.0f, 0.0f};
float masks[] = {1.0f, 0.5f, 0.0f};  // 第三个顶点不受影响

SetVertexPositionsCommand setPosCmd(
    meshIndex,
    ConstArrayView<float>(newXPositions, 3),
    ConstArrayView<float>(newYPositions, 3),
    ConstArrayView<float>(newZPositions, 3),
    ConstArrayView<float>(masks, 3),
    VectorOperation::Add
);
setPosCmd.run(reader);

// 修改单个顶点的蒙皮权重
float weights[] = {0.6f, 0.4f};
std::uint16_t jointIndices[] = {2, 5};

SetSkinWeightsCommand setWeightsCmd(
    meshIndex,
    42,  // vertex index
    ConstArrayView<float>(weights, 2),
    ConstArrayView<std::uint16_t>(jointIndices, 2)
);
setWeightsCmd.run(reader);

DNACalibDNAReader::destroy(reader);
```

## Demo 示例

以下是一个完整的最小示例，展示如何加载 DNA、执行校准命令、保存结果：

**DNACalibExample.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FDNACalibExample
{
public:
    /** 对 DNA 数据执行基本校准流程 */
    static void CalibrateDNA(const uint8* DNASourceData, uint64 DataSize, 
                             const TCHAR* OutputPath);
};
```

**DNACalibExample.cpp**
```cpp
#include "DNACalibExample.h"
#include "dnacalib/DNACalib.h"
#include "dnacalib/dna/DNACalibDNAReader.h"

// DNA 流相关
#include <dna/BinaryStreamReader.h>
#include <dna/BinaryStreamWriter.h>
#include <trio/streams/MemoryStream.h>

using namespace dnac;

void FDNACalibExample::CalibrateDNA(
    const uint8* DNASourceData, uint64 DataSize, const TCHAR* OutputPath)
{
    // 1. 从内存创建 DNA 读取器
    //    （实际使用中需要通过 trio::MemoryStream 包装原始数据）
    //    这里假设已有 dna::BinaryStreamReader* sourceReader
    
    // 2. 创建可变 DNA 副本
    DNACalibDNAReader* reader = DNACalibDNAReader::create(sourceReader);
    if (!reader)
    {
        return;
    }

    // 3. 定义校准命令
    // 缩放：将模型放大 1.5 倍
    ScaleCommand scaleCmd(1.5f, {0.0f, 0.0f, 0.0f});

    // 平移：向上移动 10 单位
    TranslateCommand translateCmd({0.0f, 0.0f, 10.0f});

    // 转换单位：厘米 → 米
    ConvertUnitsCommand convertCmd(
        TranslationUnit::cm, RotationUnit::degrees);

    // 修剪微小 blend shape delta
    PruneBlendShapeTargetsCommand pruneCmd(0.0001f);

    // 4. 组合成序列并执行
    CommandSequence sequence;
    sequence.add(&scaleCmd);
    sequence.add(&translateCmd);
    sequence.add(&convertCmd);
    sequence.add(&pruneCmd);
    sequence.run(reader);

    // 5. 此时 reader 中的数据已被修改
    //    可以通过 dna::Reader 接口读取修改后的数据
    //    例如获取关节数量：
    std::uint16_t jointCount = reader->getJointCount();
    UE_LOG(LogTemp, Log, TEXT("校准后骨骼数量: %d"), jointCount);

    // 6. 清理
    DNACalibDNAReader::destroy(reader);
}
```

## 命令参考

### 变换命令

| 命令类 | 说明 |
|---|---|
| `TranslateCommand` | 平移中性骨骼和顶点位置。只需平移根骨骼，变换会传播到子骨骼 |
| `RotateCommand` | 绕指定原点旋转中性骨骼和顶点位置（角度制） |
| `ScaleCommand` | 按因子缩放中性骨骼、顶点位置和动画 delta |
| `ConvertUnitsCommand` | 在不同长度单位（cm/m 等）和角度单位（degrees/radians）间转换 |

### 数据设置命令

| 命令类 | 说明 |
|---|---|
| `SetVertexPositionsCommand` | 修改指定网格的顶点位置，支持 Interpolate/Add/Subtract/Multiply 操作和权重遮罩 |
| `SetBlendShapeTargetDeltasCommand` | 修改混合变形目标的 delta 值，支持按顶点索引精确控制 |
| `SetSkinWeightsCommand` | 设置单个顶点的蒙皮权重（关节索引 + 权重值） |
| `SetNeutralJointTranslationsCommand` | 直接设置所有中性骨骼的平移值 |
| `SetNeutralJointRotationsCommand` | 直接设置所有中性骨骼的旋转值 |
| `SetLODsCommand` | 指定保留的 LOD 级别，移除不在指定 LOD 中的骨骼/混合变形/动画映射/网格 |

### 移除命令

| 命令类 | 说明 |
|---|---|
| `RemoveJointCommand` | 按索引移除骨骼（支持单个或批量） |
| `RemoveMeshCommand` | 按索引移除网格 |
| `RemoveBlendShapeCommand` | 按索引移除混合变形通道 |
| `RemoveAnimatedMapCommand` | 按索引移除动画映射 |
| `RemoveJointAnimationCommand` | 移除指定骨骼的动画数据（保留骨骼本身） |

### 重命名命令

| 命令类 | 说明 |
|---|---|
| `RenameJointCommand` | 按索引或旧名称重命名骨骼 |
| `RenameMeshCommand` | 按索引或旧名称重命名网格 |
| `RenameBlendShapeCommand` | 按索引或旧名称重命名混合变形通道 |
| `RenameAnimatedMapCommand` | 按索引或旧名称重命名动画映射 |

### 工具命令

| 命令类 | 说明 |
|---|---|
| `ClearBlendShapesCommand` | 清除所有混合变形数据（target deltas + 动画数据），使 DNA 变为"纯骨骼"模式 |
| `PruneBlendShapeTargetsCommand` | 修剪绝对值小于等于阈值的 blend shape target delta |
| `CalculateMeshLowerLODsCommand` | 基于高 LOD 网格的顶点位置和低 LOD 网格的纹理坐标，重新计算低 LOD 网格的顶点位置 |

### 组合工具

| 命令类 | 说明 |
|---|---|
| `CommandSequence` | 按添加顺序依次执行多个命令。持有命令指针但不拥有所有权 |
| `ConditionalCommand<TCommand, TCondition>` | 仅在条件满足时执行命令。通过 `makeConditional()` 工厂函数创建 |

### 向量操作枚举

`VectorOperation` 枚举用于 `SetVertexPositionsCommand` 和 `SetBlendShapeTargetDeltasCommand`：

| 值 | 计算公式 |
|---|---|
| `Interpolate` | `new = old * (1 - weight) + set * weight` |
| `Add` | `new = old + (set * weight)` |
| `Subtract` | `new = old - (set * weight)` |
| `Multiply` | `new = old * (set * weight)` |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RigLogic` (插件依赖) | 提供底层 DNA 数据结构（`dna::Reader` 等）和 RigLogic 面部动画系统 |
| `UnrealEd` | DNACalibLib 和 DNACalibModule 的构建依赖（编辑器功能支持） |

> **注意**：DNACalibLibTest 模块仅在 Win64 平台可用，用于内部自动化测试。

## 维护状态

### 近期更新

```
- a39b1867f9f5 Disabled iwyu support for DNACalid lib
- 914f2d844019 Move DNACalib under public plugins folder and add DNACalib2 under restricted folder #rb violeta.vukobrat
```

第一条禁用了 IWYU（Include What You Use）支持，可能是为了兼容性。第二条将 DNACalib 从内部/受限目录迁移到公开插件目录，同时在受限目录添加了 DNACalib2（暗示有新版本在开发中）。

### 维护评价

- **创建时间**：2024-10-21，非常新的插件
- **版本号**：6.12.2，说明这是一个成熟版本（经历了大量迭代）
- **维护状态**：活跃维护中。作为 MetaHuman 生态系统的核心工具，由 Epic Games 维护
- **已知限制**：
  - 纯 C++ API，无蓝图支持
  - 测试模块仅限 Win64
  - 依赖 RigLogic 插件
  - DNACalib2 已在受限目录出现，未来可能被替代
- **推荐使用**：✅ 推荐。如果你需要在运行时程序化修改 MetaHuman DNA 数据，这是官方推荐的工具。但需注意 DNACalib2 的存在可能意味着未来会有 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DNACalib)
- [RigLogic 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic)（依赖项）