# GeneSplicer Plugin

> GeneSplicer plugin for facial animation

| 属性 | 值 |
|---|---|
| 中文名 | 基因拼接器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GeneSplicerLib` (Runtime), `GeneSplicerLibTest` (Runtime), `GeneSplicerModule` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-21 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GeneSplicer) | |

## 用途

GeneSplicer 是 MetaHuman / RigLogic 面部动画管线中的核心拼接工具。它解决了"如何从多个已有的面部 DNA 数据中混合生成新的面部"这一问题。

DNA（Digital Nature Actor）文件存储了完整的面部拓扑、骨骼、混合变形、蒙皮权重和行为逻辑。GeneSplicer 的拼接算法接受多个 DNA Reader 和一组区域权重（Region Affiliation），通过加权混合生成一个全新的 DNA 输出。具体来说，它分别拼接以下六个维度的数据：

| 拼接维度 | 说明 |
|---|---|
| **Neutral Mesh** | 中性姿态下的网格顶点位置 |
| **Blend Shapes** | 混合形状目标（表情变形） |
| **Neutral Joints** | 中性姿态下的关节位移和旋转 |
| **Joint Behavior** | 关节行为矩阵（驱动关系） |
| **Skin Weights** | 蒙皮权重 |
| **Joint Behavior (ML)** | 机器学习驱动的关节行为（神经网络） |

该插件内部使用 SIMD（SSE/AVX）对齐的分块矩阵进行高性能计算，支持按 DNA 索引和网格索引过滤以减少不必要的计算量。它还支持将 GenePool 序列化到流中，以便离线构建和复用。

> **注意**：`Installed: false`，此插件仅在源码构建（Source Build）的引擎中可用，不包含在二进制分发版本中。

## 使用场景

- 你正在基于 MetaHuman 框架创建大量不同外貌的角色 → 用 GeneSplicer 从现有面部 DNA 池中按区域权重混合生成新面部
- 你需要程序化生成面部变体（如不同年龄、体型混合） → 用 GeneSplicer 的区域权重系统精细控制混合比例
- 你需要将多个面部 DNA 的行为逻辑合并 → 用 spliceJointBehavior / spliceBlendShapes 单独拼接特定维度
- 你需要离线预计算基因池以加速运行时拼接 → 用 GenePool 的 dump/load 流式序列化

## 蓝图用法

GeneSplicerLib 是纯 C++ 库，不包含 Blueprint 公开 API。Blueprint 集成由 GeneSplicerModule 提供（源码未在当前分析范围内）。核心拼接逻辑需通过 C++ 调用。

## C++ 用法

### 头文件引入

```cpp
#include "GeneSplicer.h"
#include "SpliceData.h"
#include "GenePool.h"
#include "PoolSpliceParams.h"
#include "GeneSplicerDNAReader.h"  // 输出 DNA Reader
```

### 基本用法

从多个 DNA 创建 GenePool，配置区域权重，执行拼接：

```cpp
// 来源: Public/genesplicer/GeneSplicer.h, Public/genesplicer/splicedata/SpliceData.h

// 1. 假设已有 dna::Reader* deltaArchetype 和一组 dna::Reader* dnas[]
const dna::Reader* deltaArchetype = /* ... */;
const dna::Reader* dnas[] = { dna1, dna2, dna3 };
constexpr uint16_t dnaCount = 3;

// 2. 创建基因池（拷贝所有 DNA 数据到优化的内部结构）
gs4::GenePool genePool(deltaArchetype, dnas, dnaCount, gs4::GenePoolMask::All);

// 3. 创建区域归属数据（从已有 RegionAffiliationReader 加载）
const raf::RegionAffiliationReader* rafReader = /* ... */;

// 4. 创建拼接数据并注册基因池
gs4::SpliceData spliceData;
spliceData.registerGenePool("facePool", rafReader, &genePool);

// 5. 设置基础原型
spliceData.setBaseArchetype(deltaArchetype);

// 6. 配置权重（每个 DNA 对每个区域的权重）
gs4::PoolSpliceParams* params = spliceData.getPoolParams("facePool");
// 权重布局: [DNA0_Region0, DNA0_Region1, DNA1_Region0, DNA1_Region1, ...]
float weights[] = { 0.7f, 0.3f, 0.2f, 0.8f, 0.1f, 0.9f };
params->setSpliceWeights(0, weights, 6);
params->setScale(1.0f);

// 7. 执行拼接
gs4::GeneSplicer splicer(gs4::CalculationType::SSE);
GeneSplicerDNAReader* output = /* 创建输出 Reader */;
splicer.splice(&spliceData, output);
```

### 进阶用法

单独拼接特定维度，以及使用 DNA/Mesh 过滤减少计算量：

```cpp
// 来源: Public/genesplicer/GeneSplicer.h, Public/genesplicer/splicedata/PoolSpliceParams.h

// 仅拼接网格顶点
splicer.spliceNeutralMeshes(&spliceData, output);

// 仅拼接混合变形
splicer.spliceBlendShapes(&spliceData, output);

// 仅拼接关节
splicer.spliceNeutralJoints(&spliceData, output);

// 仅拼接关节行为
splicer.spliceJointBehavior(&spliceData, output);

// 仅拼接蒙皮权重
splicer.spliceSkinWeights(&spliceData, output);

// 设置 DNA 过滤器（只使用部分 DNA 参与拼接）
uint16_t dnaFilter[] = { 0, 2 };  // 只用 DNA 0 和 DNA 2
params->setDNAFilter(dnaFilter, 2);

// 设置网格过滤器（只拼接部分网格）
uint16_t meshFilter[] = { 0 };  // 只拼接第一个网格
params->setMeshFilter(meshFilter, 1);
```

### GenePool 序列化（离线预计算）

```cpp
// 来源: Public/genesplicer/splicedata/GenePool.h

// 保存到流
gs4::GenePool genePool(deltaArchetype, dnas, dnaCount);
BoundedIOStream* outputStream = /* ... */;
genePool.dump(outputStream, gs4::GenePoolMask::All);

// 从流加载（跳过 DNA 数据拷贝）
BoundedIOStream* inputStream = /* ... */;
gs4::GenePool loadedPool(inputStream, gs4::GenePoolMask::All);
```

## Demo 示例

完整的最小拼接示例：

```cpp
// GeneSplicerDemo.h
#pragma once

#include "GeneSplicer.h"
#include "SpliceData.h"
#include "GenePool.h"
#include "PoolSpliceParams.h"

class FGeneSplicerDemo
{
public:
    /** 从多个 DNA Reader 混合生成新面部 */
    static GeneSplicerDNAReader* BlendFaces(
        const dna::Reader* DeltaArchetype,
        const dna::Reader** DNAs,
        uint16 DNACount,
        const raf::RegionAffiliationReader* RAF,
        const float* Weights,
        uint32 WeightCount,
        float Scale = 1.0f);
};
```

```cpp
// GeneSplicerDemo.cpp
#include "GeneSplicerDemo.h"

GeneSplicerDNAReader* FGeneSplicerDemo::BlendFaces(
    const dna::Reader* DeltaArchetype,
    const dna::Reader** DNAs,
    uint16 DNACount,
    const raf::RegionAffiliationReader* RAF,
    const float* Weights,
    uint32 WeightCount,
    float Scale)
{
    // 创建基因池
    gs4::GenePool GenePool(DeltaArchetype, DNAs, DNACount);

    // 创建拼接数据
    gs4::SpliceData SpliceData;
    SpliceData.registerGenePool("pool", RAF, &GenePool);
    SpliceData.setBaseArchetype(DeltaArchetype);

    // 配置权重
    gs4::PoolSpliceParams* Params = SpliceData.getPoolParams("pool");
    Params->setSpliceWeights(0, Weights, WeightCount);
    Params->setScale(Scale);

    // 执行拼接
    gs4::GeneSplicer Splicer(gs4::CalculationType::SSE);
    GeneSplicerDNAReader* Output = /* 创建输出 */;
    Splicer.splice(&SpliceData, Output);

    return Output;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RigLogic` | DNA 数据格式和 RigLogic 面部动画系统 |
| `ControlRig` | Control Rig 动画框架集成 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `2f6aa301` | Improve DNA asset load performance and backwards compatible conversion by reducing data copies | 优化 DNA 资产加载性能，减少数据拷贝以提升向后兼容转换 |
| 2026-05-12 | `57c5e2c7` | Update DNA and RigLogic to better handle malformed DNA files | 改善对格式错误 DNA 文件的容错处理 |
| 2026-05-12 | `0577289d` | Suppress private module include warnings for test modules (RigLogicLibTest, DNACalibLibTest, DNACali | 抑制测试模块的私有模块头文件包含警告 |
| 2026-04-30 | `82833e51` | Fix data-race on per platform DNAConfig access during serialization | 修复序列化时平台 DNAConfig 访问的数据竞争问题 |
| 2026-04-28 | `0c7a803e` | Implement face-winding conversion in DNA to support arbitrary coordinate systems in UE | 实现 DNA 面法线绕序转换以支持 UE 中的任意坐标系 |

### 维护评价

**活跃维护**。GeneSplicer 虽然创建时间较短（约 2 年），但近期更新频率很高（2026 年 4-5 月有多次提交），内容涵盖性能优化、错误修复和新功能（坐标系支持）。该插件是 MetaHuman 管线的核心组件，由 Epic Games 团队维护，预计将持续活跃开发。

需要注意的是：
- `Installed: false`，仅源码构建可用
- 依赖 RigLogic 和 ControlRig 插件
- 测试模块仅支持 Win64 平台
- 核心拼接库是纯 C++，无 Blueprint 公开 API

**推荐使用**：如果你在做 MetaHuman 相关的程序化面部生成工作，这是必选组件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GeneSplicer)
- [官方文档]()（暂无）