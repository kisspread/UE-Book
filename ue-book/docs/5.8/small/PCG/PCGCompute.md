# Procedural Content Generation Framework (PCG)

> Visual scripting framework for procedurally populating worlds with content in editor and/or at run-time.

| 属性 | 值 |
|---|---|
| 中文名 | 程序化内容生成框架 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质、节点模板） |
| 模块 | `PCG` (Runtime), `PCGCompute` (Runtime), `PCGEditor` (Runtime), `PCGTests` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG) | |

## 用途

PCG（Procedural Content Generation Framework）是 UE5 的核心程序化内容生成系统。它提供了一个**节点图式的可视化脚本框架**，允许开发者通过连接不同功能节点来定义规则，在编辑器中或运行时程序化地填充游戏世界内容。

PCG 解决的核心问题是：**大规模、可控的程序化场景布置**。与手动放置 Actor 或简单的随机散布不同，PCG 提供了基于图（Graph）的规则系统，支持条件过滤、密度控制、地形适配、碰撞检测等高级功能，使美术和设计师能够快速创建复杂的自然环境、城市布局、植被分布等。

该插件于 2024 年 1 月从实验阶段正式毕业（由 commit `5744168b` 可见 `[PCG] Move the plugin out of experimental`），标志着 Epic 将其作为正式生产功能推出。

## 使用场景

- 你需要在开放世界中程序化地散布植被、岩石、建筑废墟等 → 用 PCG Graph
- 你需要根据地形坡度、高度、材质等条件过滤物体放置 → 用 PCG 的采样和过滤节点
- 你需要在运行时动态生成场景内容（如 Roguelike 关卡） → 用 PCG 的运行时生成模式
- 你需要 GPU 加速的大规模实例生成和光线追踪采样 → 用 PCGCompute 模块
- 你需要将网格烘焙到纹理（用于地形绘制、草地密度图等） → 用 PCGCompute 的 UnwrapMesh 功能

## 蓝图用法

PCG 的蓝图接口主要通过 `UPCGSubsystem`、`UPCGGraph` 等核心类暴露。由于 PCG 是节点图编辑器驱动的系统，大部分交互通过 PCG Graph Editor 完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreatePCGGraph` | 创建新的 PCG 图资源 | `UPCGGraph` |
| `ExecuteGraph` | 执行 PCG 图生成内容 | `UPCGSubsystem` |
| `GetPCGSubsystem` | 获取当前世界的 PCG 子系统 | `UPCGSubsystem` |

### 使用示例（蓝图描述）

典型蓝图工作流：
1. 在场景中放置一个 `PCG Component` Actor
2. 创建一个 `PCG Graph` 资产，双击打开图编辑器
3. 在图中添加 Surface Sampler → Filter → Static Mesh Spawner 节点
4. 连接节点定义采样表面、过滤条件、输出网格体
5. 在 PCG Component 上指定该 Graph，点击 Generate

## C++ 用法

PCGCompute 模块提供底层 GPU 计算功能，用于高性能场景生成。

### 头文件引入

```cpp
#include "PCGComputeModule.h"
#include "PCGTextureReadback.h"
#include "PCGUnwrapMesh.h"
#include "PCGTextureDownsample.h"
#include "PCGDilate.h"
```

### 基本用法

**纹理回读（Texture Readback）** — 将 GPU 纹理数据读回 CPU：

```cpp
// 来源: Public/PCGTextureReadback.h
FPCGTextureReadbackDispatchParams Params;
Params.SourceTexture = MyTexture->GetResource()->GetTexture2DRHI();
Params.SourceSampler = TStaticSamplerState<SF_Point, AM_Clamp, AM_Clamp>::GetRHI();
Params.SourceDimensions = FIntPoint(1024, 1024);
Params.SourceTextureIndex = 0;
Params.OutputFormat = PF_FloatRGBA;

FPCGTextureReadbackInterface::Dispatch(Params, [](void* OutBuffer, int32 Width, int32 Height) {
    // 在回调中处理回读的像素数据
    FFloat16Color* Pixels = static_cast<FFloat16Color*>(OutBuffer);
    for (int32 i = 0; i < Width * Height; ++i) {
        // 处理每个像素...
    }
});
```

**纹理降采样（Texture Downsample）** — 对纹理进行 GPU 加速的降采样：

```cpp
// 来源: Internal/PCGTextureDownsample.h
FRDGBuilder& GraphBuilder = /* ... */;
PCGTextureDownsample::FParams Params;
Params.Texture = InputTexture;
Params.Sampler = TStaticSamplerState<SF_Bilinear>::GetRHI();
Params.SliceIndex = 0;
Params.NumSlices = 1;
Params.Mode = EPCGTextureDownsampleMode::Average;

PCGTextureDownsample::DownsampleTexture(GraphBuilder, Params);
```

### 进阶用法

**网格展开到纹理（Mesh Unwrap）** — 将 3D 网格三角形投影到 UV 空间的纹理上：

```cpp
// 来源: Internal/PCGUnwrapMesh.h
FRDGBuilder& GraphBuilder = /* ... */;
FRDGTextureRef OutputTexture = /* ... */;
const FStaticMeshLODResources& LOD = MyMesh->GetRenderData()->LODResources[0];

PCGUnwrapMesh::FUnwrapParams UnwrapParams;
UnwrapParams.InitFromLOD(LOD);
UnwrapParams.Attribute = PCGUnwrapMesh::EMeshAttribute::Mask;
UnwrapParams.Resolution = FIntPoint(512, 512);

if (PCGUnwrapMesh::ValidateParams(UnwrapParams))
{
    PCGUnwrapMesh::AddUnwrapMeshPass(GraphBuilder, OutputTexture, UnwrapParams);
}
```

**纹理膨胀（Dilate）** — 将有效数据向外扩展，填充未覆盖区域：

```cpp
// 来源: Internal/PCGDilate.h
FRDGBuilder& GraphBuilder = /* ... */;
FRDGTextureRef Texture = /* ... */;

// 每次迭代将有效像素（alpha==1）向外扩展一个像素
// 多次迭代可覆盖更大的空洞区域
PCGDilate::AddDilatePass(GraphBuilder, Texture, /*Iterations=*/8);
```

## Demo 示例

一个完整的纹理回读示例，从 GPU 读取纹理数据并保存为图像：

```cpp
// PCGTextureReadbackExample.h
#pragma once

#include "CoreMinimal.h"

class FPCGTextureReadbackExample
{
public:
    /** 从 GPU 读回纹理数据并执行回调处理 */
    static void ReadbackTexture(UTexture2D* SourceTexture);
};
```

```cpp
// PCGTextureReadbackExample.cpp
#include "PCGTextureReadbackExample.h"
#include "PCGTextureReadback.h"
#include "Engine/Texture2D.h"

void FPCGTextureReadbackExample::ReadbackTexture(UTexture2D* SourceTexture)
{
    if (!SourceTexture || !SourceTexture->GetResource())
    {
        UE_LOG(LogPCGCompute, Warning, TEXT("无效的源纹理"));
        return;
    }

    FPCGTextureReadbackDispatchParams Params;
    Params.SourceTexture = SourceTexture->GetResource()->GetTexture2DRHI();
    Params.SourceSampler = TStaticSamplerState<SF_Point, AM_Clamp, AM_Clamp>::GetRHI();
    Params.SourceDimensions = FIntPoint(SourceTexture->GetSizeX(), SourceTexture->GetSizeY());
    Params.SourceTextureIndex = 0;
    Params.OutputFormat = PF_FloatRGBA;

    FPCGTextureReadbackInterface::Dispatch(Params, [](void* OutBuffer, int32 Width, int32 Height) {
        if (!OutBuffer)
        {
            UE_LOG(LogPCGCompute, Error, TEXT("纹理回读失败：缓冲区为空"));
            return;
        }

        UE_LOG(LogPCGCompute, Log, TEXT("纹理回读成功：%dx%d"), Width, Height);

        // 处理像素数据
        const FFloat16Color* Pixels = static_cast<const FFloat16Color*>(OutBuffer);
        for (int32 Y = 0; Y < Height; ++Y)
        {
            for (int32 X = 0; X < Width; ++X)
            {
                const FFloat16Color& Pixel = Pixels[Y * Width + X];
                // 对像素进行处理...
            }
        }
    });
}
```

## 模块依赖

从 Build.cs 和头文件分析，PCGCompute 模块依赖以下底层渲染模块：

| 模块 | 用途 |
|---|---|
| `RenderCore` | RDG（Render Dependency Graph）渲染图构建 |
| `RHI` | RHI 纹理、缓冲区、采样器等硬件抽象层 |
| `Renderer` | 场景渲染、光线追踪、GPU Scene 管理 |
| `ShaderCore` | 全局着色器编译框架 |

无特殊依赖（仅标准 Core/Engine/Slate 等基础模块 + 渲染管线模块）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `1cd8cea5` | [PCG] Fixed potential crash when building the landscape cache, when some entries can't be resolved. | 修复构建地形缓存时因条目无法解析导致的崩溃 |
| 2026-05-26 | `788faf05` | [PCG] Optimize FPCGComponentVisualizer | 优化 PCG 组件可视化器性能 |
| 2026-05-26 | `0532b644` | [PCG] Fix crash with null objects with accessors | 修复访问器中空对象导致的崩溃 |
| 2026-05-26 | `82ca98ed` | [PCG] Optimized & cached metadata size computation, but gated on a flag w/ TLS backing so the normal | 优化并缓存元数据大小计算，通过 TLS 标志控制 |
| 2026-05-26 | `585bbecb` | [PCG] Fixed editor update performance issue related to manual edit (+ a double update) and inspectio | 修复编辑器中手动编辑相关的更新性能问题 |

### 维护评价

PCG 是 Epic **重点维护的活跃插件**。从 git 历史来看：

- **活跃维护**：2026 年 5 月仍有密集的 bug 修复和性能优化提交
- **成熟度高**：已于 2024 年初从实验阶段毕业，是正式生产级功能
- **持续改进**：近期提交集中在崩溃修复和性能优化，表明已进入稳定期但仍积极维护
- **功能规模大**：1472 个源文件，包含运行时、计算、编辑器、测试四个模块，是 UE5 中规模最大的插件之一

**推荐使用**：PCG 是 UE5 中程序化内容生成的官方标准方案，适合所有需要程序化场景布置的项目。GPU 计算模块（PCGCompute）为大规模生成提供硬件加速支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [PCGCompute 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG/Source/PCGCompute)

---

# PCG Compute 模块文档

> PCG 的 GPU 计算模块，提供光线追踪、纹理回读、网格展开、草地地图解包等 GPU 加速功能。

| 属性 | 值 |
|---|---|
| 中文名 | PCG GPU 计算模块 |
| 分类 | Runtime |
| 默认启用 | ✅ 是（随 PCG 插件启用） |
| 包含内容 | ❌ 无 |
| 模块 | `PCGCompute` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG/Source/PCGCompute) | |

## 模块用途

PCGCompute 是 PCG 框架的 GPU 计算后端，负责将 PCG 图中的计算密集型操作卸载到 GPU 执行。该模块包含以下核心 GPU 功能：

1. **纹理回读（Texture Readback）** — 将 GPU 端纹理数据安全地传回 CPU，支持异步回调
2. **网格展开（Mesh Unwrap）** — 将 3D 网格三角形按 UV 通道投影到纹理空间，用于烘焙法线、位置等属性
3. **草地地图解包（Grass Map Unpacker）** — 从打包的草地纹理中解包出地形高度图和草地密度图
4. **场景写入器（Scene Writer）** — 将 PCG 生成的实例数据通过 Compute Shader 写入 GPU Scene
5. **光线追踪采样（Ray Trace）** — 使用硬件光线追踪从场景中采样几何信息
6. **光线追踪 UV 缓存（Ray Tracing UV Cache）** — 缓存网格 UV 数据以加速光线追踪中的坐标查询
7. **纹理降采样（Texture Downsample）** — GPU 加速的纹理降采样（支持平均值、最小值、最大值、求和模式）
8. **纹理膨胀（Dilate）** — 将有效像素数据向外扩展以填充空洞区域

## 核心 API

### 纹理回读接口

```cpp
// FPCGTextureReadbackInterface - 线程安全的纹理回读 API
static void Dispatch(const FPCGTextureReadbackDispatchParams& Params, 
                     const TFunction<void(void* OutBuffer, int32 Width, int32 Height)>& AsyncCallback);
static void Dispatch_GameThread(...);  // 仅游戏线程调用
static void Dispatch_RenderThread(...); // 仅渲染线程调用
```

### 网格展开接口

```cpp
// PCGUnwrapMesh - 将网格烘焙到纹理
bool AddUnwrapMeshPass(FRDGBuilder& GraphBuilder, FRDGTextureRef OutputTexture, const FUnwrapParams& Params);
```

支持两种属性输出：
- `EMeshAttribute::LocalPosition` — 输出局部空间顶点位置（RGB=位置，A=覆盖标记）
- `EMeshAttribute::Mask` — 输出覆盖掩码（所有通道写 1）

### 光线追踪接口

```cpp
// PCGRayTrace - 硬件加速光线追踪采样
void RenderPCGRayTraceInline(FRDGBuilder& GraphBuilder, const FPCGRayTraceParams& InParams);
```

### 纹理处理接口

```cpp
// 降采样
void DownsampleTexture(FRDGBuilder& GraphBuilder, FParams& InParams);

// 膨胀（多次迭代可覆盖更大空洞）
bool AddDilatePass(FRDGBuilder& GraphBuilder, FRDGTextureRef OutputTexture, int32 Iterations);
```

### GPU Scene 写入

`FPCGSceneWriterCS` 是一个 Compute Shader，负责将 PCG 生成的实例数据写入 UE 的 GPU Scene 系统，支持：
- 自定义浮点数据（CustomFloatData）
- 实例剔除（通过 CullingCells）
- 种子控制（Seed）

## 使用场景

- 你的 PCG 图需要采样 3D 网格表面来确定物体放置位置 → 使用 RayTrace 采样
- 你需要将网格烘焙到纹理用于地形绘制 → 使用 Mesh Unwrap
- 你需要高效地生成数万个实例 → 使用 Scene Writer Compute Shader 直接写入 GPU Scene
- 你的地形系统需要草地密度图 → 使用 Grass Map Unpacker
- 你需要将 GPU 计算结果传回 CPU 做后续逻辑 → 使用 Texture Readback