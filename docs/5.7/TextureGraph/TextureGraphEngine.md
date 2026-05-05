# Texture Graph

> Texture creation tool using graphs.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质、着色器） |
| 模块 | `TextureGraph` (Runtime), `TextureGraphEditor` (Runtime), `TextureGraphEngine` (Runtime), `TextureGraphInsight` (Runtime), `TextureGraphInsightEditor` (Runtime), `Continuable` (External), `Function2` (External) |
| 实验性 | 否 |
| 创建时间 | 2023-12-20 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/TextureGraph) | |

## 用途

TextureGraph 是 UE5 内置的节点式纹理创建与处理框架，允许开发者和美术人员在编辑器内通过可视化图（Graph）工作流程序化生成纹理，无需依赖外部工具（如 Substance Designer）。

从源码架构来看，它远不止一个简单的"图编辑器"，而是一套完整的纹理处理引擎，包含以下核心子系统：

- **设备抽象层（Device）**：统一的硬件抽象，支持 FX（UE 着色器）、OpenCL、内存、压缩内存、磁盘缓存、远程设备等多种后端
- **变换系统（Transform）**：以 `BlobTransform` 为基类的各种纹理操作节点（纯色、数组网格、直方图、缩略图等）
- **任务/服务架构（Job/Service）**：异步任务调度系统，包含哈希计算、MinMax 统计、MipMap 生成、直方图计算等空闲服务
- **材质集成（FxMat）**：基于 UE 材质系统的渲染管线，支持 FX 材质、蓝图材质、缩略图材质等
- **Mix 系统**：高层级的纹理图容器（`UMix`/`UMixInterface`），管理更新周期和资源生命周期
- **3D 网格烘焙**：支持将纹理烘焙到 3D 网格上（法线、AO、空间 UV 等），包含程序化网格和编辑器场景网格
- **分块处理（Tile）**：将大纹理拆分为 Tile 进行处理，支持超大分辨率纹理
- **遮罩系统**：丰富的遮罩类型（绘制、固体、图像、噪声、图案、法线、曲率等）和修改器

## 使用场景

- 你需要在 UE5 编辑器内程序化创建纹理，不想切换到外部工具 → 用 TextureGraph
- 你需要将纹理烘焙到 3D 网格上（法线贴图、AO 贴图等） → 用 TextureGraph 的 `RenderMesh` 和 `MeshDetails` 系统
- 你需要创建复杂的纹理遮罩用于材质分层 → 用 TextureGraph 的遮罩系统（`MaskType`、`MaskModifierType`）
- 你需要 GPU 加速的大规模纹理处理 → 用 TextureGraph 的 FX/OpenCL 设备后端
- 你需要创建纹理图集或数组网格 → 用 `T_ArrayGrid`
- 你需要在运行时动态生成纹理并缓存到磁盘 → 用 `Device_Disk` 的缓存系统
- 你需要分析纹理数据（直方图、MinMax 统计） → 用 `HistogramService`、`MinMaxService`

## 蓝图用法

TextureGraph 的核心处理逻辑（Transform、Job、Device 等）均为纯 C++ API，不直接暴露给蓝图。蓝图可访问的类型有限：

### 蓝图可访问类型

| 类型 | 说明 | 所在头文件 |
|---|---|---|
| `UMix` | 可蓝图化的 Mix 类（UCLASS(Blueprintable, BlueprintType)），纹理图的核心容器 | `Model/Mix/Mix.h` |
| `EBlendModes` | 混合模式枚举（Copy、Add、Subtract、Multiply、Divide、Difference、Max、Min、Step、Overlay） | `2D/BlendModes.h` |
| `TextureType` | 纹理类型枚举（Diffuse、Specular、Normal、Displacement、AO 等） | `2D/TextureType.h` |
| `TextureContent` | 纹理内容类型枚举（Asset、PaintMask、SolidMask、NoiseMask 等） | `2D/TextureContent.h` |
| `MaskType` | 遮罩类型枚举（Paint、Solid、Image、Noise、Pattern、Normal、Curvature、PositionGradient） | `2D/Mask/MaskEnums.h` |
| `MaskModifierType` | 遮罩修改器枚举（Brightness、Clamp、Invert、Normalize、GradientRemap、Posterize、Scatter） | `2D/Mask/MaskEnums.h` |

> **注意**：要充分利用 TextureGraph 的功能，需要通过 C++ 进行开发。蓝图主要用于配置 Mix 参数和选择混合模式/遮罩类型。

## C++ 用法

### 头文件引入

```cpp
// 核心引擎
#include "TextureGraphEngine.h"

// 纹理变换节点
#include "Transform/Expressions/T_FlatColorTexture.h"
#include "Transform/Expressions/T_ArrayGrid.h"
#include "Transform/Utility/T_TextureHistogram.h"
#include "Transform/Utility/T_FinaliseBlob.h"
#include "Transform/Utility/T_PrepareResources.h"
#include "Transform/Mix/T_InvalidateTiles.h"
#include "Transform/Layer/T_Thumbnail.h"

// 设备系统
#include "Device/Mem/Device_Mem.h"
#include "Device/Disk/Device_Disk.h"
#include "Device/MemCM/Device_MemCM.h"
#include "Device/Null/Device_Null.h"

// Mix 系统
#include "Model/Mix/Mix.h"
#include "Model/Mix/MixInterface.h"

// 任务服务
#include "Job/HistogramService.h"
#include "Job/MinMaxService.h"
#include "Job/MipMapService.h"
#include "Job/BlobHasherService.h"

// 材质系统
#include "FxMat/FxMaterial.h"
#include "FxMat/RenderMaterial_FX_MinMax.h"
#include "FxMat/RenderMaterial_Thumbnail.h"

// 3D 网格
#include "3D/RenderMesh_Procedural.h"
#include "3D/RenderMesh_EditorScene.h"
#include "3D/MeshDetails/MeshDetails_SpatialUV.h"

// 调试
#include "Profiling/RenderDoc/RenderDocManager.h"
```

### 基本用法 — 创建纯色纹理

```cpp
// 来源: Transform/Expressions/T_FlatColorTexture.h
#include "Transform/Expressions/T_FlatColorTexture.h"

// 定义输出描述符（默认 Byte 格式）
BufferDescriptor Desc = T_FlatColorTexture::GetFlatColorDesc(
    TEXT("MyRedTexture"),
    BufferFormat::Byte
);

// 创建红色纯色纹理
FLinearColor RedColor(1.0f, 0.0f, 0.0f, 1.0f);
TiledBlobPtr RedTexture = T_FlatColorTexture::Create(
    nullptr,    // MixUpdateCyclePtr，独立创建时可为 nullptr
    Desc,       // 输出描述符
    RedColor,   // 颜色
    0           // TargetId
);
```

### 基本用法 — 获取设备实例

```cpp
// 来源: Device/Mem/Device_Mem.h, Device/Disk/Device_Disk.h
#include "Device/Mem/Device_Mem.h"
#include "Device/Disk/Device_Disk.h"

// 获取内存设备（CPU 端纹理处理）
Device_Mem* MemDevice = Device_Mem::Get();

// 获取磁盘设备（纹理缓存）
Device_Disk* DiskDevice = Device_Disk::Get();

// 设置缓存目录
DiskDevice->SetBaseDirectory(
    FPaths::ProjectSavedDir() / TEXT("TextureGraphCache"),
    true  // 迁移已有缓存
);

// 获取缓存文件路径
FString CachePath = DiskDevice->GetCacheFilename(HashValue);
```

### 进阶用法 — 创建纹理数组网格

```cpp
// 来源: Transform/Expressions/T_ArrayGrid.h
#include "Transform/Expressions/T_ArrayGrid.h"

// 准备输入纹理数组
TArray<TiledBlobPtr> InputTextures;
InputTextures.Add(TextureA);
InputTextures.Add(TextureB);
InputTextures.Add(TextureC);
InputTextures.Add(TextureD);

// 定义输出描述符
BufferDescriptor OutputDesc;
OutputDesc.Width = 2048;
OutputDesc.Height = 2048;
OutputDesc.Format = BufferFormat::Byte;

// 创建 2x2 网格排列，黑色背景
TiledBlobPtr GridTexture = T_ArrayGrid::Create(
    Cycle,                  // MixUpdateCyclePtr
    OutputDesc,             // 输出描述符（引用传递）
    InputTextures,          // 输入纹理数组
    2,                      // NumRows
    2,                      // NumCols
    FLinearColor::Black,    // BackgroundColor
    0                       // TargetId
);
```

### 进阶用法 — 使用直方图和 MinMax 服务

```cpp
// 来源: Transform/Utility/T_TextureHistogram.h, Job/HistogramService.h
#include "Transform/Utility/T_TextureHistogram.h"
#include "Job/HistogramService.h"

// 方式一：直接创建直方图变换
TiledBlobPtr Histogram = T_TextureHistogram::Create(
    Cycle,
    SourceTexture,  // 源纹理
    0               // TargetId
);

// 方式二：通过服务创建（异步）
TiledBlobPtr Histogram = T_TextureHistogram::CreateOnService(
    Mix,            // UMixInterface*
    SourceTexture,
    0
);

// 使用 HistogramService 管理批量直方图任务
HistogramServicePtr Service = std::make_shared<HistogramService>();
Service->AddHistogramJob(Cycle, std::move(JobObj), TargetID, Mix);
Service->CaptureNextBatch();  // 捕获下一批次
```

### 进阶用法 — 使用 Job 变换链

```cpp
// 来源: Transform/Utility/T_FinaliseBlob.h, Transform/Utility/T_PrepareResources.h
#include "Transform/Utility/T_FinaliseBlob.h"
#include "Transform/Utility/T_PrepareResources.h"
#include "Transform/Mix/T_InvalidateTiles.h"

// 准备资源
JobPtr PrepareJob = T_PrepareResources::Create(Cycle, PreviousJob);

// 最终化 Blob
JobPtr FinaliseJob = T_FinaliseBlob::Create(Cycle, PrepareJob);

// 使指定 TargetId 的 Tile 失效（触发重新计算）
T_InvalidateTiles::Create(Cycle, TargetId);
```

### 进阶用法 — 3D 网格烘焙

```cpp
// 来源: 3D/RenderMesh_Procedural.h, 3D/MeshDetails/MeshDetails_SpatialUV.h
#include "3D/RenderMesh_Procedural.h"
#include "3D/MeshDetails/MeshDetails_SpatialUV.h"

// 创建程序化网格
MeshLoadInfo LoadInfo;
RenderMesh_ProceduralPtr ProceduralMesh = std::make_shared<RenderMesh_Procedural>(LoadInfo);
ProceduralMesh->Tesselation() = 64;  // 设置细分级别

// 异步加载网格
ProceduralMesh->Load();

// 计算空间 UV 详情
MeshInfo* Mesh = /* 获取网格信息 */;
MeshDetails_SpatialUV SpatialUV(Mesh);
MeshDetailsPAsync Result = SpatialUV.Calculate();
```

### 进阶用法 — RenderDoc 调试集成

```cpp
// 来源: Profiling/RenderDoc/RenderDocManager.h
#include "Profiling/RenderDoc/RenderDocManager.h"

// 创建 RenderDoc 管理器
TextureGraphEditor::RenderDocManagerPtr RenderDoc = 
    std::make_unique<TextureGraphEditor::RenderDocManager>();
RenderDoc->Initialize();

// 捕获下一批次的 GPU �