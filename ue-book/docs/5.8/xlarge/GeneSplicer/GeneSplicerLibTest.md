# GeneSplicer Plugin

> GeneSplicer plugin for facial animation

| 属性 | 值 |
|---|---|
| 中文名 | 基因拼接器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GeneSplicerLib` (Runtime), `GeneSplicerLibTest` (Runtime), `GeneSplicerModule` (Runtime), `GeneSplicerEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GeneSplicer) | |

## 用途

GeneSplicer 是一个用于**面部动画 DNA 数据拼接（Splicing）**的底层 C++ 库插件。它解决的核心问题是：如何将多个不同角色的 DNA（Digital Normalized Asset）面部数据进行混合、融合和拼接，生成新的、具有混合特征的面部动画数据。

DNA 是 MetaHuman 技术栈中的标准化面部数据格式，包含网格顶点位置、BlendShape 目标、骨骼权重、关节约束行为等。GeneSplicer 通过以下机制实现"基因拼接"：

- **RawGenes 提取**：从 DNA Reader 中提取中性姿态网格（Neutral Meshes）、BlendShape 目标、皮肤权重、关节中性变换和关节行为数据
- **GenePool 构建**：将多个 DNA 的数据以 Tiled/Block 方式打包到内存池中，实现 SIMD 友好的数据布局（XYZBlock、VBlock 等）
- **Splice 执行**：基于区域亲和（Region Affiliation）和权重对多个 DNA 的数据进行混合拼接

该插件是 MetaHuman 面部动画管线的核心底层组件，依赖 RigLogic 和 ControlRig 插件。

## 使用场景

- 你在做 MetaHuman 相关的面部动画混合系统，需要将多个面部资产的 DNA 数据融合为新角色
- 你需要在运行时动态拼接不同角色的面部 BlendShape、关节行为和皮肤权重
- 你在构建面向影视/游戏的面部动画 Pipeline，需要高性能的 DNA 数据处理
- 你需要对多个 DNA 数据源进行加权混合，生成中间状态的面部表现

## 蓝图用法

该插件 **没有暴露 BlueprintCallable 接口**（`CanContainContent: false`），是一个纯 C++ 库。所有操作均通过 C++ API 完成。

## C++ 用法

### 头文件引入

```cpp
// 核心库 API（公共头文件）
#include "GeneSplicerLibTest.h"  // 测试模块

// DNA 标准接口
#include "Reader.h"    // dna::Reader - DNA 数据读取接口
#include "Writer.h"    // dna::Writer - DNA 数据写入接口
```

### 核心概念

GeneSplicer 基于 DNA（Digital Normalized Asset）标准工作。核心数据类型包括：

| 概念 | 说明 |
|---|---|
| `dna::Reader` | DNA 数据的只读接口，提供网格、骨骼、BlendShape、关节行为等数据访问 |
| `dna::Writer` | DNA 数据的写入接口 |
| `RegionAffiliationReader` | 区域亲和数据读取接口，定义顶点和关节与区域的关联权重 |
| `RawGenes` | 从 DNA 中提取的原始"基因"数据集合 |
| `FixtureReader` | 用于测试的 DNA Reader 模拟实现 |

### 基本用法 — DNA Reader 接口

DNA Reader 是访问面部动画数据的核心接口。以下展示了如何从 Reader 中读取各种面部数据：

```cpp
// 来源：Private/gstests/FixtureReader.h 和 Private/gstests/Assertions.h
// DNA Reader 提供以下核心数据访问：

// 1. 读取网格数据
std::uint16_t meshCount = reader->getMeshCount();
std::uint32_t vertexCount = reader->getVertexPositionCount(meshIndex);

// 获取顶点位置（逐顶点方式）
dna::Position pos = reader->getVertexPosition(meshIndex, vertexIndex);

// 获取顶点位置（批量方式，SIMD 友好）
ConstArrayView<float> posXs = reader->getVertexPositionXs(meshIndex);
ConstArrayView<float> posYs = reader->getVertexPositionYs(meshIndex);
ConstArrayView<float> posZs = reader->getVertexPositionZs(meshIndex);

// 2. 读取 BlendShape 目标数据
std::uint16_t bsTargetCount = reader->getBlendShapeTargetCount(meshIndex);
std::uint32_t deltaCount = reader->getBlendShapeTargetDeltaCount(meshIndex, bsIndex);
dna::Delta delta = reader->getBlendShapeTargetDelta(meshIndex, bsIndex, deltaIndex);
ConstArrayView<std::uint32_t> vertexIndices = reader->getBlendShapeTargetVertexIndices(meshIndex, bsIndex);

// 3. 读取关节中性姿态
std::uint16_t jointCount = reader->getJointCount();
dna::Vector3 translation = reader->getNeutralJointTranslation(jointIdx);
dna::Vector3 rotation = reader->getNeutralJointRotation(jointIdx);

// 4. 读取皮肤权重
ConstArrayView<float> weights = reader->getSkinWeightsValues(meshIndex, vertexIndex);
ConstArrayView<std::uint16_t> jointIndices = reader->getSkinWeightsJointIndices(meshIndex, vertexIndex);

// 5. 读取关节行为（Joint Behavior）数据
std::uint16_t jointGroupCount = reader->getJointGroupCount();
ConstArrayView<std::uint16_t> outputIndices = reader->getJointGroupOutputIndices(jointGroupIndex);
ConstArrayView<std::uint16_t> inputIndices = reader->getJointGroupInputIndices(jointGroupIndex);
ConstArrayView<float> values = reader->getJointGroupValues(jointGroupIndex);
ConstArrayView<std::uint16_t> lods = reader->getJointGroupLODs(jointGroupIndex);
```

### 进阶用法 — 区域亲和（Region Affiliation）

区域亲和系统定义了顶点和关节与不同面部区域的关联权重，这是 DNA 拼接的核心机制：

```cpp
// 来源：Private/gstests/splicedata/MockedRegionAffiliationReader.h
// 区域亲和 Reader 接口：

class RegionAffiliationReader {
public:
    // 获取网格数量
    std::uint16_t getMeshCount() const;
    
    // 获取指定网格的顶点数
    std::uint32_t getVertexCount(std::uint16_t meshIndex) const;
    
    // 获取顶点所属的区域索引（一个顶点可以属于多个区域）
    ConstArrayView<std::uint16_t> getVertexRegionIndices(std::uint16_t meshIndex, 
                                                          std::uint32_t vertexIndex) const;
    
    // 获取顶点在各区域的亲和度权重
    ConstArrayView<float> getVertexRegionAffiliation(std::uint16_t meshIndex, 
                                                      std::uint32_t vertexIndex) const;
    
    // 获取关节数量
    std::uint16_t getJointCount() const;
    
    // 获取关节所属的区域索引
    ConstArrayView<std::uint16_t> getJointRegionIndices(std::uint16_t jointIndex) const;
    
    // 获取关节在各区域的亲和度权重
    ConstArrayView<float> getJointRegionAffiliation(std::uint16_t jointIndex) const;
    
    // 获取区域总数
    std::uint16_t getRegionCount() const;
};
```

### 进阶用法 — RawGenes 提取

RawGenes 是从 DNA 中提取的标准化数据集合，用于拼接计算：

```cpp
// 来源：Private/gstests/Assertions.h 中的 assertRawGenes 函数

// RawGenes 提供以下数据访问：
// rawGenes.getMeshCount()       - 网格数量
// rawGenes.getVertexCount(idx)  - 指定网格的顶点数
// rawGenes.getSkinWeightsCount(idx) - 皮肤权重数量
// rawGenes.getJointCount()      - 关节数量

// 获取中性姿态网格数据（SIMD 友好的批量布局）
ConstArrayView<RawVector3Vector> neutralMeshes = rawGenes.getNeutralMeshes();

// 获取 BlendShape 目标数据
VariableWidthMatrix<RawBlendShapeTarget> blendShapeTargets = rawGenes.getBlendShapeTargets();

// 获取皮肤权重数据
ConstArrayView<Vector<RawVertexSkinWeights>> skinWeights = rawGenes.getSkinWeights();

// 获取关节中性变换（Translation/Rotation）
RawVector3Vector translations = rawGenes.getNeutralJoints(JointAttribute::Translation);
RawVector3Vector rotations = rawGenes.getNeutralJoints(JointAttribute::Rotation);

// 获取关节行为数据
ConstArrayView<RawJointGroup> jointGroups = rawGenes.getJointGroups();
```

### 进阶用法 — GenePool 数据布局

GenePool 将多个 DNA 的数据以 Tiled/Block 方式打包，实现高效内存访问：

```cpp
// 来源：Private/gstests/Assertions.h 中的 Pool 相关断言

// 中性网格使用 XYZTiledMatrix<16u> 布局
// 每个 Block 包含 16 个 DNA 的 XYZ 数据
ConstArrayView<XYZTiledMatrix<16u>> neutralMeshPoolData;

// 关节使用类似的 Tiled 布局
XYZTiledMatrix<16u> neutralJointPoolTranslations;
XYZTiledMatrix<16u> neutralJointPoolRotations;

// BlendShape 使用 VariableWidthMatrix + AlignedVariableWidthMatrix 布局
VariableWidthMatrix<VariableWidthMatrix<std::uint16_t>> dnaIndices;
VariableWidthMatrix<AlignedVariableWidthMatrix<XYZBlock<BlockSize>>> deltas;

// 皮肤权重使用 TiledMatrix2D<16u> 布局
VariableWidthMatrix<TiledMatrix2D<16u>> skinWeightPoolValues;

// 关节行为使用 SingleJointBehavior 结构
ConstArrayView<SingleJointBehavior> jointBehaviorValues;
```

### 进阶用法 — 拼接权重配置

```cpp
// 来源：Private/gstests/Fixtures.h
// 拼接权重定义了各 DNA 在最终结果中的贡献比例

namespace canonical {
    extern const Vector<float> spliceWeights;
    // 示例：{ 0.3f, 0.7f } 表示两个 DNA 分别贡献 30% 和 70%
}
```

## Demo 示例

以下展示如何实现一个自定义的 DNA Reader，这是使用 GeneSplicer 的基础：

```cpp
// MyCustomDNAReader.h
#pragma once

#include "Reader.h"

class FMyCustomDNAReader : public dna::Reader
{
public:
    // === 头信息 ===
    std::uint16_t getFileFormatGeneration() const override { return 2; }
    std::uint16_t getFileFormatVersion() const override { return 1; }
    
    // === 描述信息 ===
    StringView getName() const override { return {"MyCharacter", 11ul}; }
    Archetype getArchetype() const override { return {}; }
    std::uint16_t getLODCount() const override { return 1; }
    TranslationUnit getTranslationUnit() const override { return {}; }
    RotationUnit getRotationUnit() const override { return {}; }
    CoordinateSystem getCoordinateSystem() const override { return {}; }
    RotationSequence getRotationSequence() const override { return {}; }
    FaceWindingOrder getFaceWindingOrder() const override { return {}; }

    // === 定义数据 ===
    std::uint16_t getMeshCount() const override { return 1; }
    std::uint16_t getJointCount() const override { return static_cast<std::uint16_t>(Joints.size()); }
    std::uint16_t getBlendShapeChannelCount() const override { return 0; }
    StringView getMeshName(std::uint16_t /*meshIndex*/) const override { return {"Face", 4ul}; }
    StringView getJointName(std::uint16_t /*index*/) const override { return {"Root", 4ul}; }
    
    // === 几何数据 ===
    std::uint32_t getVertexPositionCount(std::uint16_t /*meshIndex*/) const override 
    { 
        return static_cast<std::uint32_t>(VertexPositions.size()); 
    }
    
    dna::Position getVertexPosition(std::uint16_t /*meshIndex*/, std::uint32_t vertexIndex) const override
    {
        return VertexPositions[vertexIndex];
    }
    
    // === 关节数据 ===
    dna::Vector3 getNeutralJointTranslation(std::uint16_t index) const override
    {
        return JointTranslations[index];
    }
    
    dna::Vector3 getNeutralJointRotation(std::uint16_t index) const override
    {
        return JointRotations[index];
    }
    
    // === 皮肤权重 ===
    ConstArrayView<float> getSkinWeightsValues(std::uint16_t /*meshIndex*/, 
                                                std::uint32_t vertexIndex) const override
    {
        return ConstArrayView<float>{SkinWeights[vertexIndex]};
    }
    
    ConstArrayView<std::uint16_t> getSkinWeightsJointIndices(std::uint16_t /*meshIndex*/,
                                                              std::uint32_t vertexIndex) const override
    {
        return ConstArrayView<std::uint16_t>{SkinWeightJointIndices[vertexIndex]};
    }
    
    // ... 其他接口方法需要实现（大部分可返回空值/零值）

    // 数据存储
    Vector<dna::Position> VertexPositions;
    Vector<dna::Vector3> JointTranslations;
    Vector<dna::Vector3> JointRotations;
    Vector<std::vector<float>> SkinWeights;
    Vector<std::vector<std::uint16_t>> SkinWeightJointIndices;
    std::uint16_t Joints = 1;
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RigLogic` | 底层面部动画求解器，提供 DNA 数据的标准处理能力 |
| `ControlRig` | UE5 控制绑定系统，用于驱动面部骨骼 |
| `MessageLog` | 编辑器消息日志（GeneSplicerModule 依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `2f6aa301` | Improve DNA asset load performance and backwards compatible conversion by reducing data copies | 优化 DNA 资产加载性能，减少数据拷贝实现向后兼容转换 |
| 2026-05-12 | `57c5e2c7` | Update DNA and RigLogic to better handle malformed DNA files | 改进对格式错误的 DNA 文件的处理能力 |
| 2026-05-12 | `0577289d` | Suppress private module include warnings for test modules (RigLogicLibTest, DNACalibLibTest, DNACali | 抑制测试模块的私有模块包含警告 |
| 2026-04-30 | `82833e51` | Fix data-race on per platform DNAConfig access during serialization | 修复序列化期间平台 DNAConfig 访问的数据竞争问题 |
| 2026-04-28 | `0c7a803e` | Implement face-winding conversion in DNA to support arbitrary coordinate systems in UE | 实现 DNA 面朝向转换，支持 UE 中任意坐标系 |

### 维护评价

**活跃维护** — 该插件于 2024 年 10 月从 Epic 内部仓库移入公开插件目录，属于较新的 MetaHuman 基础设施组件。

- **创建时间**：2024-10-21（约 1 年）
- **更新频率**：近期（2026 年 4-5 月）有多次功能性更新，包括性能优化、数据竞争修复和坐标系支持
- **维护状态**：活跃维护中，作为 MetaHuman 技术栈的核心组件持续迭代
- **注意事项**：
  - 该插件 **默认未启用**（`Installed: false`），需要手动在项目中启用
  - 依赖 RigLogic 和 ControlRig 插件，确保这些依赖已启用
  - 当前公开的主要是测试模块代码（GeneSplicerLibTest），核心库 GeneSplicerLib 的公共头文件数量有限
  - 该插件为纯 C++ 库，无蓝图接口，面向高级用户

**推荐使用**：如果你在开发 MetaHuman 相关的面部动画系统，该插件是官方推荐的 DNA 数据拼接解决方案。但由于其底层定位和复杂的 DNA 数据模型，建议配合 MetaHuman 文档和示例项目使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GeneSplicer)
- [RigLogic 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic)
- [DNA 标准参考](https://docs.unrealengine.com/en-US/Animating-Characters-and-Objects/MetaHumans/)