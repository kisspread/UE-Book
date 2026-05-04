# GeneSplicer Plugin v9.8.2

> GeneSplicer plugin for facial animation

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GeneSplicerLib` (Runtime), `GeneSplicerLibTest` (Runtime), `GeneSplicerModule` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GeneSplicer) | |

## 用途

GeneSplicer 是一个**面部动画基因拼接系统**，用于将多个 DNA（Digital Normalized Anatomy）数据源按权重混合，生成全新的面部动画数据。

它解决的核心问题是：当你有多个角色的面部 DNA 数据时，如何通过加权混合（splicing）创造出一个全新的、融合了多个角色特征的面部动画资产。这在角色定制系统（Character Customization）中非常有用——例如玩家捏脸系统需要将多个预设面孔混合成新面孔。

GeneSplicer 的工作原理：
1. 将多个 DNA 数据加载到 **GenePool**（基因池）中
2. 通过 **Region Affiliation**（区域归属）数据定义每个 DNA 对不同面部区域的影响权重
3. 使用 **SpliceData** 配置拼接参数（权重、缩放、过滤器）
4. 调用 **GeneSplicer** 引擎执行拼接，输出一个新的 **GeneSplicerDNAReader**

拼接支持的数据类型包括：中性网格（NeutralMeshes）、混合变形（BlendShapes）、蒙皮权重（SkinWeights）、中性关节（NeutralJoints）和关节行为（JointBehavior）。

该插件依赖 **RigLogic** 和 **ControlRig** 插件，与 MetaHuman 管线深度集成。

## 使用场景

- 你在做一个角色定制/捏脸系统，需要混合多个预设面孔 → 用 GeneSplicer
- 你需要批量生成大量面部变体用于 NPC 群体 → 用 GeneSplicer + GenePool
- 你需要在运行时动态混合面部动画数据 → 用 GeneSplicer 的 SSE/AVX 优化路径
- 你有 Region Affiliation 数据需要读写（JSON 或二进制格式）→ 用 RAF 模块

## 蓝图用法

GeneSplicer 主要是 C++ 库，不直接暴露蓝图节点。其 UE 集成通过 GeneSplicerModule 和 ControlRig 间接提供蓝图访问。

## C++ 用法

### 头文件引入

```cpp
#include "genesplicer/GeneSplicer.h"
#include "genesplicer/splicedata/SpliceData.h"
#include "genesplicer/splicedata/GenePool.h"
#include "genesplicer/splicedata/PoolSpliceParams.h"
#include "genesplicer/GeneSplicerDNAReader.h"
```

### 基本用法：完整拼接流程

以下展示如何将多个 DNA 混合成一个新的面部动画：

```cpp
#include "genesplicer/GeneSplicer.h"
#include "genesplicer/splicedata/SpliceData.h"
#include "genesplicer/splicedata/GenePool.h"
#include "genesplicer/splicedata/PoolSpliceParams.h"
#include "genesplicer/GeneSplicerDNAReader.h"

using namespace gs4;

// 假设已有 dna::Reader* baseArchetype（基础原型 DNA）
// 假设已有 dna::Reader* deltaArchetype（增量原型 DNA）
// 假设已有 dna::Reader* dnas[]（多个源 DNA）
// 假设已有 raf::RegionAffiliationReader* rafData（区域归属数据）

// 1. 创建 GenePool，加载所有源 DNA
GenePool genePool(deltaArchetype, dnas, dnaCount, GenePoolMask::All);

// 2. 创建 SpliceData 并注册基因池
SpliceData spliceData;
spliceData.setBaseArchetype(baseArchetype);
spliceData.registerGenePool("facePool", rafData, &genePool);

// 3. 配置拼接权重
PoolSpliceParams* poolParams = spliceData.getPoolParams("facePool");
// 设置每个 DNA 在每个区域的权重（区域数 × DNA 数）
poolParams->setSpliceWeights(0, weights, regionCount * dnaCount);
poolParams->setScale(1.0f);

// 4. 创建输出 DNA Reader
GeneSplicerDNAReader* output = GeneSplicerDNAReader::create(baseArchetype);

// 5. 执行拼接
GeneSplicer splicer(CalculationType::SSE);
splicer.splice(&spliceData, output);

// output 现在包含拼接后的面部动画数据
// 使用完毕后释放
GeneSplicerDNAReader::destroy(output);
```

### 进阶用法：选择性拼接与过滤

```cpp
using namespace gs4;

// 只拼接特定数据类型
GeneSplicer splicer(CalculationType::AVX);
splicer.spliceBlendShapes(&spliceData, output);   // 只拼接混合变形
splicer.spliceNeutralMeshes(&spliceData, output);  // 只拼接中性网格
splicer.spliceNeutralJoints(&spliceData, output);  // 只拼接中性关节
splicer.spliceJointBehavior(&spliceData, output);  // 只拼接关节行为
splicer.spliceSkinWeights(&spliceData, output);    // 只拼接蒙皮权重

// 使用 DNA 过滤器，只让部分 DNA 参与拼接
PoolSpliceParams* poolParams = spliceData.getPoolParams("facePool");
std::uint16_t dnaFilter[] = {0, 2, 5};  // 只使用第 0、2、5 号 DNA
poolParams->setDNAFilter(dnaFilter, 3);

// 使用网格过滤器，只拼接特定网格
std::uint16_t meshFilter[] = {0};  // 只拼接第一个网格
poolParams->setMeshFilter(meshFilter, 1);

// 清除过滤器
poolParams->clearFilters();
```

### 进阶用法：GenePool 序列化

```cpp
using namespace gs4;

// 从 DNA 创建 GenePool 并导出到文件（加速后续加载）
GenePool genePool(deltaArchetype, dnas, dnaCount, GenePoolMask::All);

// 导出到二进制流
trio::FileStream* outStream = trio::FileStream::create("gene_pool.bin", trio::FileStream::Write);
genePool.dump(outStream, GenePoolMask::All);
trio::FileStream::destroy(outStream);

// 从文件加载 GenePool（跳过耗时的 DNA 解析）
trio::FileStream* inStream = trio::FileStream::create("gene_pool.bin", trio::FileStream::Read);
GenePool loadedPool(inStream, GenePoolMask::All);
trio::FileStream::destroy(inStream);

// 使用 GenePoolMask 只加载需要的部分
GenePool partialPool(deltaArchetype, dnas, dnaCount, 
    GenePoolMask::BlendShapes | GenePoolMask::NeutralMeshes);
```

### 进阶用法：Region Affiliation 数据读写

```cpp
#include "raf/RegionAffiliationBinaryStreamReader.h"
#include "raf/RegionAffiliationJSONStreamReader.h"
#include "raf/RegionAffiliationBinaryStreamWriter.h"
#include "raf/RegionAffiliationJSONStreamWriter.h"

using namespace raf;

// 从 JSON 文件读取区域归属数据
trio::FileStream* jsonStream = trio::FileStream::create("raf.json", trio::FileStream::Read);
RegionAffiliationJSONStreamReader* jsonReader = 
    RegionAffiliationJSONStreamReader::create(jsonStream);
jsonReader->read();

// 查询区域信息
std::uint16_t regionCount = jsonReader->getRegionCount();
for (std::uint16_t i = 0; i < regionCount; i++) {
    StringView name = jsonReader->getRegionName(i);
    // 使用区域名称...
}

// 查询顶点区域归属
std::uint16_t meshCount = jsonReader->getMeshCount();
for (std::uint16_t m = 0; m < meshCount; m++) {
    std::uint32_t vertCount = jsonReader->getVertexCount(m);
    for (std::uint32_t v = 0; v < vertCount; v++) {
        auto indices = jsonReader->getVertexRegionIndices(m, v);
        auto affiliations = jsonReader->getVertexRegionAffiliation(m, v);
        // 使用归属数据...
    }
}

// 查询关节区域归属
std::uint16_t jointCount = jsonReader->getJointCount();
for (std::uint16_t j = 0; j < jointCount; j++) {
    auto indices = jsonReader->getJointRegionIndices(j);
    auto affiliations = jsonReader->getJointRegionAffiliation(j);
}

// 清理
RegionAffiliationJSONStreamReader::destroy(jsonReader);
trio::FileStream::destroy(jsonStream);

// 从二进制文件读取（更快）
trio::FileStream* binStream = trio::FileStream::create("raf.bin", trio::FileStream::Read);
RegionAffiliationBinaryStreamReader* binReader = 
    RegionAffiliationBinaryStreamReader::create(binStream);
binReader->read();
// ... 使用方式相同
RegionAffiliationBinaryStreamReader::destroy(binReader);
trio::FileStream::destroy(binStream);
```

## Demo 示例

### 完整的 GeneSplicer 拼接示例

```cpp
// GeneSplicerDemo.h
#pragma once

#include "CoreMinimal.h"

class FDnaAsset;

class GENEPLICERDEMO_API FGeneSplicerDemo
{
public:
    /** 从多个 DNA 文件混合生成新的面部动画 */
    static bool BlendFaces(
        const FString& BaseArchetypePath,
        const FString& DeltaArchetypePath,
        const TArray<FString>& DnaPaths,
        const FString& RafPath,
        const TArray<float>& Weights,
        const FString& OutputPath
    );
};
```

```cpp
// GeneSplicerDemo.cpp
#include "GeneSplicerDemo.h"

#include "genesplicer/GeneSplicer.h"
#include "genesplicer/splicedata/SpliceData.h"
#include "genesplicer/splicedata/GenePool.h"
#include "genesplicer/splicedata/PoolSpliceParams.h"
#include "genesplicer/GeneSplicerDNAReader.h"
#include "genesplicer/CalculationType.h"

#include "raf/RegionAffiliationBinaryStreamReader.h"

#include <dna/BinaryStreamReader.h>
#include <trio/streams/FileStream.h>

using namespace gs4;
using namespace raf;

// 辅助：从文件创建 DNA Reader
static dna::BinaryStreamReader* LoadDNA(const FString& Path)
{
    std::string StdPath = TCHAR_TO_UTF8(*Path);
    trio::FileStream* stream = trio::FileStream::create(StdPath.c_str(), trio::FileStream::Read);
    if (!stream) return nullptr;
    dna::BinaryStreamReader* reader = dna::BinaryStreamReader::create(stream);
    reader->read();
    trio::FileStream::destroy(stream);
    return reader;
}

bool FGeneSplicerDemo::BlendFaces(
    const FString& BaseArchetypePath,
    const FString& DeltaArchetypePath,
    const TArray<FString>& DnaPaths,
    const FString& RafPath,
    const TArray<float>& Weights,
    const FString& OutputPath)
{
    // 1. 加载基础原型和增量原型
    dna::BinaryStreamReader* baseArch = LoadDNA(BaseArchetypePath);
    dna::BinaryStreamReader* deltaArch = LoadDNA(DeltaArchetypePath);
    if (!baseArch || !deltaArch)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load archetype DNAs"));
        return false;
    }

    // 2. 加载所有源 DNA
    const std::uint16_t DnaCount = static_cast<std::uint16_t>(DnaPaths.Num());
    TArray<dna::BinaryStreamReader*> DnaReaders;
    TArray<const dna::Reader*> DnaReaderPtrs;
    DnaReaders.SetNum(DnaCount);
    DnaReaderPtrs.SetNum(DnaCount);
    
    for (int32 i = 0; i < DnaPaths.Num(); i++)
    {
        DnaReaders[i] = LoadDNA(DnaPaths[i]);
        DnaReaderPtrs[i] = DnaReaders[i];
    }

    // 3. 加载区域归属数据
    std::string RafStdPath = TCHAR_TO_UTF8(*RafPath);
    trio::FileStream* rafStream = trio::FileStream::create(RafStdPath.c_str(), trio::FileStream::Read);
    RegionAffiliationBinaryStreamReader* rafReader = 
        RegionAffiliationBinaryStreamReader::create(rafStream);
    rafReader->read();
    trio::FileStream::destroy(rafStream);

    // 4. 创建 GenePool
    GenePool genePool(deltaArch, DnaReaderPtrs.GetData(), DnaCount);

    // 5. 配置 SpliceData
    SpliceData spliceData;
    spliceData.setBaseArchetype(baseArch);
    spliceData.registerGenePool("main", rafReader, &genePool);

    // 6. 设置权重
    PoolSpliceParams* params = spliceData.getPoolParams("main");
    params->setSpliceWeights(0, Weights.GetData(), Weights.Num());

    // 7. 创建输出并执行拼接
    GeneSplicerDNAReader* output = GeneSplicerDNAReader::create(baseArch);
    
    GeneSplicer splicer(CalculationType::SSE);
    splicer.splice(&spliceData, output);

    // 8. 导出结果（此处省略具体写入逻辑）
    // output 可通过 dna::BinaryStreamWriter 写入文件

    // 9. 清理
    GeneSplicerDNAReader::destroy(output);
    RegionAffiliationBinaryStreamReader::destroy(rafReader);
    for (auto* reader : DnaReaders)
    {
        dna::BinaryStreamReader::destroy(reader);
    }
    dna::BinaryStreamReader::destroy(deltaArch);
    dna::BinaryStreamReader::destroy(baseArch);

    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RigLogic` (Plugin) | DNA 数据格式和 RigLogic 面部动画求解器 |
| `ControlRig` (Plugin) | 运行时控制绑定系统集成 |

无特殊模块依赖（仅标准 Core/Engine/Slate 等及上述插件依赖）。

## 维护状态

### 近期更新

```
- 3527b50c480a Fix usage of unacceptable words #rb none
- ea76c1ecb047 Move GeneSplicer into public plugins folder #rb violeta.vukobrat
```

### 维护评价

- **创建时间**：2024-10-21，约 1 年前
- **版本号**：9.8.2，说明该库在 Epic 内部已有较长的开发历史（主版本号为 9），是成熟算法的 UE 集成
- **近期活动**：仅有 2 次 commit，均为仓库整理性质（移动到公开目录、修复命名），无功能性更新
- **状态**：该插件刚从 Epic 内部迁移到公开仓库，属于**初始公开阶段**。核心算法库（GeneSplicerLib）以预编译 C++ 库形式提供，源码不完全开放
- **依赖关系**：强依赖 RigLogic 和 ControlRig，与 MetaHuman 管线绑定较深
- **推荐**：如果你在使用 MetaHuman 或 RigLogic 管线做角色定制，这是官方推荐的面部混合方案。但作为新公开的插件，社区文档和示例较少，建议参考源码中的测试用例学习用法

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GeneSplicer)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GeneSplicer/Source/GeneSplicerLibTest)

---

## 子模块文档索引

本插件为 xlarge 规模（249 个源文件），按功能划分为以下子模块：

| 子模块 | 说明 | 文档 |
|---|---|---|
| **GeneSplicer Core** | 核心拼接引擎：GeneSplicer、SpliceData、GenePool、PoolSpliceParams | [GeneSplicerCore.md](GeneSplicerCore.md) |
| **RAF (Region Affiliation)** | 区域归属数据读写：JSON/二进制格式的顶点和关节区域归属 | [RegionAffiliation.md](RegionAffiliation.md) |
| **GeneSplicerModule** | UE 运行时模块集成 | [GeneSplicerModule.md](GeneSplicerModule.md) |
| **GeneSplicerEditor** | 编辑器工具集成 | [GeneSplicerEditor.md](GeneSplicerEditor.md) |

---

# GeneSplicer Core 子模块

> 核心拼接算法和数据结构

## 核心类

### `gs4::GeneSplicer`

无状态的拼接算法封装器。支持三种计算模式：

| 计算类型 | 说明 |
|---|---|
| `CalculationType::Scalar` | 标量实现，兼容性最好 |
| `CalculationType::SSE` | SSE 向量化实现（默认） |
| `CalculationType::AVX` | AVX 向量化实现，性能最优 |

**构造函数**：
```cpp
explicit GeneSplicer(CalculationType calculationType = CalculationType::SSE, MemoryResource* memRes = nullptr);
```

**拼接方法**：

| 方法 | 说明 |
|---|---|
| `splice()` | 执行所有拼接器（完整拼接） |
| `spliceNeutralMeshes()` | 只拼接中性网格 |
| `spliceBlendShapes()` | 只拼接混合变形 |
| `spliceNeutralJoints()` | 只拼接中性关节位置 |
| `spliceJointBehavior()` | 只拼接关节行为 |
| `spliceSkinWeights()` | 只拼接蒙皮权重 |

### `gs4::SpliceData`

拼接输入数据容器，管理基因池注册和基础原型设置。

**关键方法**：

| 方法 | 说明 |
|---|---|
| `setBaseArchetype()` | 设置基础原型 DNA（提供中性值作为拼接基准） |
| `registerGenePool()` | 注册基因池及其区域归属数据 |
| `unregisterGenePool()` | 注销基因池 |
| `getPoolParams()` | 获取已注册基因池的拼接参数 |

### `gs4::GenePool`

优化的 DNA 数据集合，用于高效拼接。支持从 DNA Reader 数组构建或从流加载。

**GenePoolMask**（位掩码，控制加载哪些数据）：

| 掩码值 | 说明 |
|---|---|
| `NeutralMeshes` (1) | 中性网格 |
| `BlendShapes` (2) | 混合变形 |
| `SkinWeights` (4) | 蒙皮权重 |
| `NeutralJoints` (8) | 中性关节 |
| `JointBehavior` (16) | 关节行为 |
| `All` (31) | 全部 |

**关键方法**：

| 方法 | 说明 |
|---|---|
| 构造函数（DNA 数组） | 从 DNA Reader 数组创建 |
| 构造函数（流） | 从二进制流加载（跳过 DNA 解析） |
| `dump()` | 将 GenePool 导出到流 |
| `getDNACount()` | 获取 DNA 数量 |
| `getDNAName()` | 获取指定 DNA 名称 |
| `getDNAGender()` | 获取指定 DNA 性别 |

### `gs4::PoolSpliceParams`

每个基因池的拼接参数配置。

**关键方法**：

| 方法 | 说明 |
|---|---|
| `setSpliceWeights()` | 设置 DNA 在各区域的拼接权重 |
| `setDNAFilter()` | 过滤参与拼接的 DNA 子集 |
| `setMeshFilter()` | 过滤参与拼接的网格子集 |
| `clearFilters()` | 清除所有过滤器 |
| `setScale()` | 设置拼接缩放因子 |

**权重布局说明**（来自源码注释）：

假设有 2 个区域、4 个 DNA，权重数组为一维展平格式：

```
         Region-0  Region-1
DNA-0    w[0]      w[1]
DNA-1    w[2]      w[3]
DNA-2    w[4]      w[5]
DNA-3    w[6]      w[7]
```

调用 `setSpliceWeights(dnaStartIndex=1, weights=[0.1, 0.9, 0.4, 0.5], count=4)` 后：

```
         Region-0  Region-1
DNA-0    0.0       0.0
DNA-1    0.1       0.9
DNA-2    0.4       0.5
DNA-3    0.0       0.0
```

### `gs4::GeneSplicerDNAReader`

拼接输出的 DNA Reader，同时实现 `dna::Reader` 和 `dna::Writer` 接口。

```cpp
// 创建（从基础原型初始化静态数据）
static GeneSplicerDNAReader* create(const dna::Reader* reader, MemoryResource* memRes = nullptr);
// 释放
static void destroy(GeneSplicerDNAReader* instance);
```

---

# Region Affiliation 子模块

> RAF（Region Affiliation Framework）区域归属数据的读写

## 概述

Region Affiliation 定义了每个顶点和关节与不同面部区域的关联程度（0.0-1.0）。这是 GeneSplicer 进行区域化混合的关键数据。

## 类层次结构

### 读取端

```
JointRegionAffiliationReader    VertexRegionAffiliationReader
         \                              /
          \                            /
           RegionAffiliationReader
                    |
    RegionAffiliationStreamReader
           /                \
RegionAffiliationJSON    RegionAffiliationBinary
  StreamReader             StreamReader
```

### 写入端

```
JointRegionAffiliationWriter    VertexRegionAffiliationWriter
         \                              /
          \                            /
           RegionAffiliationWriter
                    |
    RegionAffiliationStreamWriter
           /                \
RegionAffiliationJSON    RegionAffiliationBinary
  StreamWriter             StreamWriter
```

## 关键读取接口

### `RegionAffiliationReader`

| 方法 | 说明 |
|---|---|
| `getRegionCount()` | 获取区域总数 |
| `getRegionName(regionIndex)` | 获取区域名称 |
| `getMeshCount()` | 获取网格数量 |
| `getVertexCount(meshIndex)` | 获取指定网格的顶点数 |
| `getVertexRegionIndices(mesh, vertex)` | 获取顶点关联的区域索引列表 |
| `getVertexRegionAffiliation(mesh, vertex)` | 获取顶点的区域归属权重 |
| `getJointCount()` | 获取关节数量 |
| `getJointRegionIndices(joint)` | 获取关节关联的区域索引列表 |
| `getJointRegionAffiliation(joint)` | 获取关节的区域归属权重 |

## 工厂方法

所有 StreamReader/Writer 通过静态 `create()`/`destroy()` 工厂方法管理生命周期：

```cpp
// JSON 读取
auto* reader = RegionAffiliationJSONStreamReader::create(stream);
reader->read();
// ... 使用
RegionAffiliationJSONStreamReader::destroy(reader);

// 二进制读取
auto* reader = RegionAffiliationBinaryStreamReader::create(stream);
reader->read();
// ...
RegionAffiliationBinaryStreamReader::destroy(reader);

// JSON 写入（可配置缩进）
auto* writer = RegionAffiliationJSONStreamWriter::create(stream, 4u);
// ... 填充数据
writer->write();
RegionAffiliationJSONStreamWriter::destroy(writer);

// 二进制写入
auto* writer = RegionAffiliationBinaryStreamWriter::create(stream);
// ... 填充数据
writer->write();
RegionAffiliationBinaryStreamWriter::destroy(writer);
```

---

# GeneSplicerModule 子模块

> UE 运行时模块集成层

GeneSplicerModule 是将 GeneSplicerLib C++ 库集成到 UE 模块系统中的运行时模块。加载阶段为 `Default`。

---

# GeneSplicerEditor 子模块

> 编辑器工具集成

GeneSplicerEditor 提供编辑器内的 GeneSplicer 工具支持，依赖 UnrealEd 模块。