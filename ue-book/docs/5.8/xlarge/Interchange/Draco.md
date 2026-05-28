# Interchange Framework

> The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.

| 属性 | 值 |
|---|---|
| 中文名 | 交换框架 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `InterchangeAnalytics` (Runtime), `InterchangeCommon` (Runtime), `InterchangeDispatcher` (Runtime), `InterchangeExport` (Runtime), `InterchangeFactoryNodes` (Runtime), `InterchangeImport` (Runtime), `InterchangeMessages` (Runtime), `InterchangeNodes` (Runtime), `InterchangeCommonParser` (Runtime), `InterchangeFbxParser` (Runtime), `GLTFCore` (Runtime), `InterchangePipelines` (Runtime), `Draco` (External) |
| 实验性 | 否 |
| 创建时间 | 2022-04-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime) | |

## 用途

Interchange Framework 是 UE5 中替代传统 FBX 导入流程的新一代资产导入/导出框架。它的核心设计理念是将文件解析（Parsing）、数据转换（Pipeline）和资产创建（Factory）三个阶段完全解耦，使开发者可以通过自定义 Pipeline 来控制导入行为，或通过自定义 Parser 来支持新的文件格式。

传统 UE4 的 FBX 导入是单体式设计，所有逻辑耦合在一起难以扩展。Interchange 通过模块化的架构解决了这个问题：
- **Parser** 负责将文件解析为通用的 Interchange 节点图
- **Pipeline** 负责对节点图进行变换和过滤
- **Factory** 负责将处理后的节点图创建为 UE 资产

其中 **Draco** 子模块是 Google 开源的 3D 网格压缩库的集成，用于在 GLTF 等格式的导入导出中处理 Draco 压缩的网格数据。Draco 通过八叉树、边折叠压缩（Edgebreaker）和 rANS 熵编码等技术，将 3D 网格数据压缩到极小的体积，同时保持无损或近无损的质量。

## 使用场景

- 你需要批量导入 FBX/GLTF 资产并自定义导入行为 → 配置 Interchange Pipeline
- 你需要导入包含 Draco 压缩的 GLTF 文件 → Draco 模块自动解压网格
- 你需要导出 UE 资产为 GLTF 格式 → 使用 Interchange Export 系统
- 你需要支持新的 3D 文件格式 → 编写自定义 Parser 模块
- 你需要在导入时过滤/修改网格、材质、动画数据 → 编写自定义 Pipeline
- 你开发一个工具链需要程序化的资产导入导出 → 通过 C++ API 调用 Interchange

## 蓝图用法

Interchange 框架主要面向 C++ 开发，大部分高级操作通过 C++ API 进行。蓝图层面主要用于配置导入/导出设置和触发导入操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ImportAsset` | 触发资产导入流程 | `UInterchangeManager` |
| `ExportAsset` | 触发资产导出流程 | `UInterchangeManager` |
| `GetPipeline` | 获取指定导入 Pipeline | `UInterchangeManager` |
| `SetSceneImportPipeline` | 设置场景级导入 Pipeline | `UInterchangeManager` |

### 使用示例（蓝图描述）

在蓝图中触发 Interchange 导入：

1. 创建一个 `UInterchangeManager` 的引用
2. 调用 `ImportAsset` 节点，传入文件路径字符串
3. 指定目标文件夹路径
4. 可选：传入自定义 Pipeline 类来控制导入行为
5. 等待导入完成回调或使用同步导入模式

对于 Pipeline 配置，可在 Project Settings → Interchange 中设置默认的导入导出 Pipeline。

## C++ 用法

### 头文件引入

```cpp
// Interchange 核心
#include "InterchangeManager.h"
#include "InterchangePipelineBase.h"
#include "InterchangeSourceData.h"
#include "InterchangeTranslatorBase.h"
#include "InterchangeFactoryBase.h"

// 节点系统
#include "InterchangeSceneNode.h"
#include "InterchangeMeshNode.h"
#include "InterchangeMaterialNode.h"
#include "InterchangeTextureNode.h"

// Draco 压缩
#include "draco/mesh/corner_table.h"
#include "draco/mesh/mesh.h"
#include "draco/compression/decode.h"
#include "draco/compression/encode.h"
```

### 基本用法 — 通过 Interchange 导入资产

以下示例展示了如何通过 C++ 触发 Interchange 导入流程（来源：Interchange 框架典型用法）：

```cpp
#include "InterchangeManager.h"
#include "InterchangeSourceData.h"

void ImportAssetWithInterchange(const FString& FilePath)
{
    UInterchangeManager& InterchangeManager = UInterchangeManager::GetInterchangeManager();
    
    // 创建源数据描述
    UInterchangeSourceData* SourceData = InterchangeManager.CreateSourceData(FilePath);
    
    // 配置导入参数
    FInterchangeImportSettings ImportSettings;
    
    // 触发异步导入
    InterchangeManager.ImportAsset(
        TEXT("/Game/ImportedAssets"),
        SourceData,
        ImportSettings
    );
}
```

### 基本用法 — Draco 网格解码

Draco 模块用于解码压缩的 3D 网格数据。以下展示了从缓冲区解码网格的基本流程：

```cpp
#include "draco/mesh/mesh.h"
#include "draco/compression/decode.h"

// 从内存缓冲区解码 Draco 压缩网格
bool DecodeDracoMesh(const uint8_t* Buffer, size_t BufferSize)
{
    draco::DecoderBuffer DecoderBuffer;
    DecoderBuffer.Init(reinterpret_cast<const char*>(Buffer), BufferSize);
    
    // 解码为三角网格
    auto DecodeResult = draco::Decoder().DecodeMeshFromBuffer(&DecoderBuffer);
    if (!DecodeResult.ok())
    {
        UE_LOG(LogTemp, Error, TEXT("Draco decode failed: %s"), 
               UTF8_TO_TCHAR(DecodeResult.status().error_msg_string().c_str()));
        return false;
    }
    
    std::unique_ptr<draco::Mesh> Mesh = std::move(DecodeResult).value();
    
    // 访问网格数据
    const int32 NumFaces = Mesh->num_faces();
    const int32 NumVertices = Mesh->num_points();
    
    // 获取位置属性
    const draco::PointAttribute* PositionAttr = 
        Mesh->GetNamedAttribute(draco::GeometryAttribute::POSITION);
    
    if (PositionAttr)
    {
        for (draco::PointIndex i(0); i < NumVertices; ++i)
        {
            const draco::AttributeValueIndex ValIndex = PositionAttr->mapped_index(i);
            float Position[3];
            PositionAttr->ConvertValue(ValIndex, Position);
            // 处理顶点位置...
        }
    }
    
    // 遍历面数据
    for (draco::FaceIndex fi(0); fi < NumFaces; ++fi)
    {
        const draco::Mesh::Face& Face = Mesh->face(fi);
        // Face[0], Face[1], Face[2] 为三个顶点的 PointIndex
    }
    
    return true;
}
```

### 进阶用法 — CornerTable 网格遍历

Draco 的 `CornerTable` 是其压缩算法的核心数据结构，支持基于角（corner）的网格拓扑遍历：

```cpp
#include "draco/mesh/corner_table.h"
#include "draco/mesh/mesh.h"

// 使用 CornerTable 进行网格拓扑分析
void AnalyzeMeshTopology(const draco::Mesh& Mesh)
{
    // 创建 CornerTable
    auto CornerTablePtr = draco::CreateCornerTableFromPositionAttribute(&Mesh);
    if (!CornerTablePtr)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create corner table"));
        return;
    }
    
    const draco::CornerTable& CT = *CornerTablePtr;
    
    // 遍历所有面的角
    for (draco::FaceIndex fi(0); fi < CT.num_faces(); ++fi)
    {
        draco::CornerIndex FirstCorner = CT.FirstCorner(fi);
        draco::CornerIndex NextCorner = CT.Next(FirstCorner);
        draco::CornerIndex PrevCorner = CT.Previous(FirstCorner);
        
        // 获取顶点索引
        draco::VertexIndex Vert0 = CT.Vertex(FirstCorner);
        draco::VertexIndex Vert1 = CT.Vertex(NextCorner);
        draco::VertexIndex Vert2 = CT.Vertex(PrevCorner);
        
        // 检查对面角（用于检测边界边）
        draco::CornerIndex OppCorner = CT.Opposite(FirstCorner);
        if (OppCorner == draco::kInvalidCornerIndex)
        {
            // FirstCorner 所在的边是边界边
        }
        
        // 使用 SwingLeft/SwingRight 进行一环邻域遍历
        draco::CornerIndex LeftCorner = CT.SwingLeft(FirstCorner);
        draco::CornerIndex RightCorner = CT.SwingRight(FirstCorner);
    }
    
    // 检查顶点的度（valence）和边界状态
    for (draco::VertexIndex vi(0); vi < CT.num_vertices(); ++vi)
    {
        int Valence = CT.Valence(vi);
        bool bIsBoundary = CT.IsOnBoundary(vi);
        
        UE_LOG(LogTemp, Log, TEXT("Vertex %d: valence=%d, boundary=%d"), 
               vi.value(), Valence, bIsBoundary);
    }
}
```

### 进阶用法 — 自定义 Interchange Pipeline

```cpp
#include "InterchangePipelineBase.h"
#include "InterchangeMeshNode.h"
#include "InterchangeSceneNode.h"

// 自定义导入 Pipeline：过滤掉名称包含 "LOD" 的网格节点
UCLASS()
class UMyCustomPipeline : public UInterchangePipelineBase
{
    GENERATED_BODY()
    
public:
    virtual void ExecutePipeline(
        UInterchangeBaseNodeContainer* BaseNodeContainer,
        const TArray<UInterchangeSourceData*>& SourceDatas) override
    {
        // 获取所有网格节点
        TArray<UInterchangeMeshNode*> MeshNodes;
        BaseNodeContainer->IterateNodesOfType<UInterchangeMeshNode>(
            [&MeshNodes](const FString& NodeUid, UInterchangeMeshNode* MeshNode)
            {
                if (!MeshNode->GetDisplayLabel().Contains(TEXT("LOD")))
                {
                    MeshNodes.Add(MeshNode);
                }
            }
        );
        
        // 删除不需要的节点
        for (UInterchangeMeshNode* Node : MeshNodes)
        {
            BaseNodeContainer->RemoveNode(Node->GetUniqueID());
        }
    }
};
```

## Demo 示例

以下是一个完整的最小示例，展示如何使用 Draco 库编码和解码网格：

```cpp
// DracoSimpleExample.h
#pragma once

#include "CoreMinimal.h"

class FDracoSimpleExample
{
public:
    // 编码一个简单的三角形为 Draco 格式
    static TArray<uint8> EncodeSimpleTriangle();
    
    // 解码 Draco 格式的数据
    static bool DecodeDracoBuffer(const TArray<uint8>& EncodedData);
};
```

```cpp
// DracoSimpleExample.cpp
#include "DracoSimpleExample.h"

#include "draco/mesh/mesh.h"
#include "draco/compression/encode.h"
#include "draco/compression/decode.h"
#include "draco/mesh/corner_table.h"

TArray<uint8> FDracoSimpleExample::EncodeSimpleTriangle()
{
    // 创建一个包含 2 个三角形的网格
    draco::Mesh Mesh;
    
    // 添加 4 个顶点位置
    auto PosAttribute = std::make_unique<draco::PointAttribute>();
    PosAttribute->Init(draco::GeometryAttribute::POSITION, 3,
                        draco::DT_FLOAT32, false, 12);
    const int32 PosAttId = Mesh.AddAttribute(std::move(PosAttribute));
    
    // 设置顶点数量
    Mesh.set_num_points(4);
    
    // 写入顶点数据
    const float Vertices[4][3] = {
        {0.0f, 0.0f, 0.0f},
        {1.0f, 0.0f, 0.0f},
        {1.0f, 1.0f, 0.0f},
        {0.0f, 1.0f, 0.0f}
    };
    
    for (int i = 0; i < 4; ++i)
    {
        Mesh.attribute(PosAttId)->SetAttributeValue(
            draco::AttributeValueIndex(i), Vertices[i]);
    }
    
    // 添加 2 个三角形面
    Mesh.AddFace(draco::Mesh::Face({draco::PointIndex(0), draco::PointIndex(1), draco::PointIndex(2)}));
    Mesh.AddFace(draco::Mesh::Face({draco::PointIndex(0), draco::PointIndex(2), draco::PointIndex(3)}));
    
    // 编码
    draco::EncoderBuffer EncodeBuffer;
    draco::Encoder Encoder;
    Encoder.SetSpeedOptions(3, 3); // encoding_speed, decoding_speed
    Encoder.SetAttributeQuantization(draco::GeometryAttribute::POSITION, 11);
    
    const draco::Status EncodeStatus = Encoder.EncodeMeshToBuffer(Mesh, &EncodeBuffer);
    if (!EncodeStatus.ok())
    {
        UE_LOG(LogTemp, Error, TEXT("Draco encode failed: %s"),
               UTF8_TO_TCHAR(EncodeStatus.error_msg_string().c_str()));
        return {};
    }
    
    // 复制到 UE 数组
    TArray<uint8> Result;
    Result.SetNumUninitialized(EncodeBuffer.size());
    FMemory::Memcpy(Result.GetData(), EncodeBuffer.data(), EncodeBuffer.size());
    
    return Result;
}

bool FDracoSimpleExample::DecodeDracoBuffer(const TArray<uint8>& EncodedData)
{
    draco::DecoderBuffer DecoderBuffer;
    DecoderBuffer.Init(reinterpret_cast<const char*>(EncodedData.GetData()),
                       EncodedData.Num());
    
    auto DecodeResult = draco::Decoder().DecodeMeshFromBuffer(&DecoderBuffer);
    if (!DecodeResult.ok())
    {
        UE_LOG(LogTemp, Error, TEXT("Draco decode failed"));
        return false;
    }
    
    std::unique_ptr<draco::Mesh> DecodedMesh = std::move(DecodeResult).value();
    
    UE_LOG(LogTemp, Log, TEXT("Decoded mesh: %d vertices, %d faces"),
           DecodedMesh->num_points(), DecodedMesh->num_faces());
    
    // 创建 CornerTable 进行拓扑分析
    auto CT = draco::CreateCornerTableFromPositionAttribute(DecodedMesh.get());
    if (CT)
    {
        for (draco::VertexIndex vi(0); vi < CT->num_vertices(); ++vi)
        {
            bool bBoundary = CT->IsOnBoundary(vi);
            int Val = CT->Valence(vi);
            UE_LOG(LogTemp, Log, TEXT("  Vertex %d: valence=%d boundary=%s"),
                   vi.value(), Val, bBoundary ? TEXT("true") : TEXT("false"));
        }
    }
    
    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Engine` | 消息模块的依赖 |

Interchange 的大部分模块不依赖特殊模块，仅使用标准 Core/Engine/Slate 等基础模块。Draco 作为外部库自包含。

无特殊依赖（仅标准 Core/Engine/Slate 等及 Engine 模块）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `61d0e791` | USD Pregen: Implement tracking of Skeleton and PhysicsAssets | USD 预生成增加骨骼和物理资产追踪功能 |
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复 UE 5.8 本地化相关编译警告 |
| 2026-05-22 | `8fdd3a89` | [Interchange] Reset existing LODModels for reimport, so that Bone bindings and mappings are updated | 重置 LOD 模型以在重导入时更新骨骼绑定和映射 |
| 2026-05-22 | `3cfa4417` | Reinstated the uFBX parser as experimental | 重新将 uFBX 解析器作为实验性功能启用 |
| 2026-05-19 | `755f95d4` | Interchange: Fix crash by protecting against nullptr objects in the list of imported objects. | 修复导入对象列表中空指针导致的崩溃 |

### 维护评价

Interchange 框架是 **活跃维护** 的核心模块，由 Epic Games 持续投入开发：

- **创建时间**：2022 年，约 4 年历史
- **更新频率**：非常频繁，2026 年 5 月仍在持续更新，涵盖新功能（USD 预生成追踪、uFBX 解析器）、bug 修复（崩溃修复、LOD 重导入）和版本适配（UE 5.8 本地化）
- **维护状态**：🟢 活跃维护中。作为 UE5 的官方资产导入/导出系统，是引擎的核心基础设施
- **已知限制**：部分功能仍处于实验阶段（如 uFBX 解析器）；Draco 模块为第三方库，版本跟随上游
- **推荐使用**：✅ 强烈推荐。如果你需要自定义资产导入导出流程，Interchange 是官方推荐的扩展方案，替代了旧版 FBX 导入管线

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [Draco 官方仓库](https://github.com/google/draco)（第三方库源码参考）