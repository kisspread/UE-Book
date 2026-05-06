# Draco

> A wrapper for the Draco 3D geometry compression library, integrated within the Unreal Engine Interchange Framework.

| 属性 | 值 |
|---|---|
| 中文名 | Draco 压缩库 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无（纯第三方库） |
| 模块 | `Draco` (External) |
| 实验性 | 否 |
| 创建时间 | 2021-03-22（基于 Interchange 引入 Draco 的首次提交） |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/google/draco) | |

> 注意：Draco 是 Google 维护的开源库，Unreal Engine 将其作为第三方模块嵌入 Interchange 插件，用于支持 draco 格式的几何压缩。本模块不提供直接的蓝图/C++ API，所有 Draco 功能通过 Interchange 导入管线暴露。

## 用途

Draco 是一个 3D 几何网格和点云压缩库，旨在显著减小 3D 模型文件大小，同时保持高质量。在 UE5 Interchange 框架中，Draco 模块用于解码 `.drc`（Draco 压缩格式）文件，支持带/不带顶点属性的网格解压，包括位置、法线、颜色、纹理坐标等。

**主要功能**：
- 解码 Draco 压缩的网格（.drc 格式）
- 支持可选解码参数（如量化方式、属性类型）
- 与 Interchange 导入管线深度集成，自动识别 `.drc` 文件并转换为 UE 内部数据结构

## 使用场景

- 你需要在游戏中加载 Draco 压缩的 3D 模型（常见于 Google 的 3D 仓库、ARCore 等）
- 你希望减小资产包体大小，使用 Draco 压缩算法优化传输和存储
- 你的内容管线已使用 Draco 工具（如 `draco_encoder`）压缩模型文件

## 蓝图用法

**本模块不提供蓝图可调用接口。** Draco 解码由 Interchange 内部自动完成，无需用户编写蓝图逻辑。

## C++ 用法

如果你需要直接使用 Draco 库进行自定义解码（例如在编辑器工具或运行时插件中），可以参考以下示例。

### 头文件引入

```cpp
#include "draco/compression/decode.h"
#include "draco/mesh/mesh.h"
#include "draco/core/decoder_buffer.h"
```

### 基本用法

以下示例从 `TArray<uint8>` 中解码一个 Draco 压缩的网格 `DracoMesh`。

```cpp
#include "draco/compression/decode.h"
#include "draco/core/decoder_buffer.h"
#include "Containers/Array.h"

// 假设已从文件或网络读取压缩数据到 DataBuffer
TArray<uint8> CompressedData;

// 创建 draco 解码器
draco::Decoder decoder;

// 创建输入缓冲区
draco::DecoderBuffer buffer;
buffer.Init(CompressedData.GetData(), CompressedData.Num());

// 解码为网格
std::unique_ptr<draco::Mesh> mesh = decoder.DecodeMeshFromBuffer(&buffer).value();
if (!mesh)
{
    // 解码失败处理
    return;
}

// 现在可以访问网格数据（示例：获取顶点数）
int32 NumVertices = mesh->num_points();
int32 NumFaces = mesh->num_faces();

// 获取位置属性（id=0 固定为位置）
const draco::PointAttribute* posAtt = mesh->GetNamedAttribute(draco::GeometryAttribute::POSITION);
if (posAtt)
{
    // 遍历顶点，读取位置
    for (draco::PointIndex i(0); i < mesh->num_points(); ++i)
    {
        draco::Vector3f pos;
        posAtt->ConvertValue(posAtt->mapped_index(i), &pos[0]);
        // 使用 pos[0], pos[1], pos[2]
    }
}
```

> 来源：参考 Draco 官方示例及 UE 中 `InterchangeFbxParser`（未提供源码）。

### 进阶用法

如果需要自定义解码选项（如设置量化、属性重排序），可以创建 `draco::DecoderOptions` 并在解码前设置：

```cpp
draco::DecoderOptions options;
options.SetQuantizationBits(draco::GeometryAttribute::POSITION, 11); // 位置 11bit
options.SetQuantizationBits(draco::GeometryAttribute::NORMAL, 8);    // 法线 8bit

draco::Decoder decoder;
auto result = decoder.DecodeMeshFromBuffer(options, &buffer);
```

## Demo 示例

以下是一个完整的 C++ 示例，演示如何在 UE 插件或模块中使用 Draco 解码 `.drc` 文件并提取顶点数据。

### MyDracoDecoder.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Containers/Array.h"

#include "draco/compression/decode.h"
#include "draco/mesh/mesh.h"
#include "draco/core/decoder_buffer.h"

/**
 * 简单的 Draco 网格解码器
 */
struct FMyDracoDecoder
{
    /** 从压缩数据解码并返回顶点位置数组 */
    static bool DecodePositions(const TArray<uint8>& CompressedData, TArray<FVector3f>& OutPositions)
    {
        draco::Decoder decoder;
        draco::DecoderBuffer buffer;
        buffer.Init(CompressedData.GetData(), CompressedData.Num());

        std::unique_ptr<draco::Mesh> mesh = decoder.DecodeMeshFromBuffer(&buffer).value();
        if (!mesh)
            return false;

        const draco::PointAttribute* posAtt = mesh->GetNamedAttribute(draco::GeometryAttribute::POSITION);
        if (!posAtt)
            return false;

        OutPositions.Reserve(mesh->num_points());
        for (draco::PointIndex i(0); i < mesh->num_points(); ++i)
        {
            draco::Vector3f pos;
            posAtt->ConvertValue(posAtt->mapped_index(i), &pos[0]);
            OutPositions.Add(FVector3f(pos[0], pos[1], pos[2]));
        }
        return true;
    }
};
```

### MyDracoDecoder.cpp（略，仅需包含头文件中的内联实现）

> 注意：实际使用时需要确保项目模块添加了 `Draco` 私有依赖（见下一节）。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础容器、字符串等 |
| `Math` | 3D 向量类型（如需使用 `FVector`） |
| `Draco` | 本模块自身（外部库，无需附加依赖） |

## 维护状态

Draco 模块作为第三方库集成，其维护主要跟随 Google Draco 官方版本更新。UE 仓库中的 Draco 模块更新不频繁，通常只在主版本升级时同步。

### 近期更新（Interchange 模块相关提交）

以下提交来自 Interchange 插件仓库，并非 Draco 库本身的更新，但体现了与 Draco 相关的整合调整：

- 2025-12-18 [`93cfc06e`] Fixed editor hanging when level reimporting a file containing skeletal meshes
- 2025-10-23 [`0158cf6a`] [Interchange] Removing unintended LOD specialization from named LOD Groups.
- 2025-10-21 [`63c630c0`] [Interchange] Fixing missing animation sequence import for LevelSequence on StaticMesh imported with Draco geometry
- 2025-10-17 [`765b3a10`] Fixed compilation error with NonUnity InterchangeWorker
- 2025-10-17 [`2c91170f`] Replaced use of /InterchangeAssets/Materials/PhongSurfaceMaterial with /Interchange...

### 维护评价

Draco 库本身由 Google 积极维护（最新版本 ~1.5.0）。Unreal Engine 中的 Draco 模块保持了与官方版本的同步，并已稳定运行多年。已知限制：
- 仅支持解码，不提供编码（如需编码请使用官方 `draco_encoder` 工具）
- 在运行时解码少量网格性能良好，但不推荐用于高频实时流式传输

**推荐使用**：如果你已有 Draco 压缩的资产，Interchange 的集成是最简单的方式；如果需要自定义解码，可参考上述 C++ 示例。

## 相关链接

- [Draco 官方仓库](https://github.com/google/draco)
- [Interchange 插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange)
- [Draco 文档](https://google.github.io/draco/)