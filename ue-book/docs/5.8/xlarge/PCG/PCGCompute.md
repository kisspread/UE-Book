# Procedural Content Generation Framework (PCG)

> Visual scripting framework for procedurally populating worlds with content in editor and/or at run-time.

| 属性 | 值 |
|---|---|
| 中文名 | 程序化内容生成框架 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `PCG` (Runtime), `PCGCompute` (Runtime), `PCGEditor` (Runtime), `PCGTests` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG) | |

## 用途

PCG（Procedural Content Generation Framework）是 Unreal Engine 5 的**程序化内容生成框架**，提供基于节点图的可视化脚本系统，用于在编辑器中和/或运行时程序化地填充世界内容。

本插件从 UE5 早期的 **Experimental** 状态毕业，正式成为引擎的一部分（首个 commit 为 `[PCG] Move the plugin out of experimental`）。它解决了以下核心问题：

1. **大规模世界内容填充**：在开放世界场景中，手动放置数以万计的植被、岩石、建筑装饰等物件极其低效。PCG 通过规则驱动的程序化方式自动生成这些内容。
2. **GPU 加速的实例化放置**：PCGCompute 模块将核心计算卸载到 GPU，利用 Compute Shader 实现高性能的实例写入（`FPCGSceneWriterCS`）、地形草地解包（`FPCGGrassMapUnpackerCS`）、纹理回读（`FPCGTextureReadbackInterface`）等操作。
3. **运行时程序化生成**：不同于仅在编辑器中烘焙的方案，PCG 支持运行时动态生成内容，适用于动态加载的世界分区（World Partition）场景。
4. **可复用的生成规则**：通过 PCG Graph（节点图资产）定义生成规则，支持复用、组合和参数化调整。

PCGCompute 模块是 PCG 的 GPU 计算后端，提供了以下关键 GPU 能力：
- **纹理回读**（`FPCGTextureReadbackInterface`）：从 GPU 读取纹理数据到 CPU，用于采样地形高度图、SDF 等
- **网格展开**（`PCGUnwrapMesh`）：将 3D 网格的三角形光栅化到 UV 空间的纹理上，实现逐纹素的网格属性查询
- **光线追踪**（`PCGRayTrace`）：利用硬件光线追踪在场景表面采样，获取位置和法线信息
- **纹理处理**：下采样（`PCGTextureDownsample`）和膨胀（`PCGDilate`）等后处理操作
- **GPU 场景写入**（`FPCGSceneWriterCS`）：直接将实例数据写入 GPU Scene，实现零 CPU 开销的大规模实例化

## 使用场景

- 你在制作开放世界游戏，需要程序化地在地形上放置草地、岩石、树木等 → 使用 PCG Graph 定义分布规则
- 你需要基于高度图、坡度等地形属性控制物体放置密度 → PCG 的 Surface Sampler + Density Filter 节点组合
- 你需要在运行时动态加载区域时程序化生成内容 → PCG 支持运行时执行
- 你需要高性能地处理大量实例的放置（数十万级别） → PCGCompute 的 GPU Compute Shader 后端
- 你需要将网格几何信息烘焙到纹理上（如 Coverage Mask） → PCGCompute 的 Mesh Unwrap 功能
- 你需要通过 GPU 光线追踪获取场景表面信息 → PCGCompute 的 Ray Trace 模块

## 蓝图用法

PCGCompute 模块本身不直接暴露 Blueprint API——它是 PCG 框架的 GPU 计算后端，由 PCG 核心模块在 Graph 执行时内部调用。

PCG 的蓝图接口主要在 **PCG（核心模块）** 中，通过 `UPCGBlueprintHelpers` 和 `UPCGSubsystem` 等类暴露。以下为 PCGCompute 提供支持的关键能力：

### 核心能力（由 PCGCompute 驱动）

| 能力 | 说明 | 对应 PCGCompute 类 |
|---|---|---|
| GPU 表面采样 | 通过光线追踪在场景表面上采样点 | `PCGRayTrace` |
| 纹理数据回读 | 将 GPU 纹理数据读回 CPU 用于 PCG 节点 | `FPCGTextureReadbackInterface` |
| 大规模实例写入 | 直接通过 Compute Shader 写入 GPU Scene | `FPCGSceneWriterCS` |
| 地形草地解包 | 解包压缩的草地地图数据 | `FPCGGrassMapUnpackerCS` |
| 网格覆盖检测 | 将网格展开到纹理空间，检测纹素覆盖 | `PCGUnwrapMesh` |

### 使用示例（蓝图描述）

在 PCG Graph 蓝图中，PCGCompute 的能力被封装在高层节点中：
1. 添加 **Surface Sampler** 节点 → 内部使用 PCGCompute 的 Ray Trace 和 Texture Readback 获取表面点
2. 添加 **Static Mesh Spawner** 节点并启用 GPU 实例化 → 内部使用 PCGCompute 的 Scene Writer 将实例直接写入 GPU Scene
3. 添加 **Landscape Grass Spawner** 节点 → 内部使用 PCGCompute 的 Grass Map Unpacker 解包地形数据

## C++ 用法

PCGCompute 模块提供的是底层 GPU 计算 API，主要用于 PCG 框架内部。以下是各子系统的 C++ 用法。

### 头文件引入

```cpp
// 纹理回读
#include "PCGTextureReadback.h"

// 网格展开
#include "PCGUnwrapMesh.h"

// 纹理下采样
#include "PCGTextureDownsample.h"

// 纹理膨胀
#include "PCGDilate.h"

// 光线追踪
#include "PCGRayTrace.h"

// 光线追踪 UV 缓存
#include "PCGRayTracingUVCacheUtils.h"
```

### 基本用法：纹理回读

从 GPU 纹理读取像素数据到 CPU 内存，支持 `UTexture2D` 和 `UTexture2DArray`。

```cpp
#include "PCGTextureReadback.h"
#include "Engine/Texture2D.h"

// 设置回读参数
FPCGTextureReadbackDispatchParams ReadbackParams;
ReadbackParams.SourceTexture = MyTexture->GetResource()->GetTexture2DRHI();
ReadbackParams.SourceSampler = TStaticSamplerState<SF_Point, AM_Clamp, AM_Clamp>::GetRHI();
ReadbackParams.SourceDimensions = FIntPoint(MyTexture->GetSizeX(), MyTexture->GetSizeY());
ReadbackParams.SourceTextureIndex = 0; // 纹理数组索引，单纹理为 0
ReadbackParams.OutputFormat = PF_FloatRGBA; // 使用浮点格式保留精度

// 调度回读（可在任意线程调用）
FPCGTextureReadbackInterface::Dispatch(ReadbackParams,
    [](void* OutBuffer, int32 ReadbackWidth, int32 ReadbackHeight)
    {
        // 回调在渲染线程执行，OutBuffer 包含像素数据
        const FFloat16Color* PixelData = static_cast<const FFloat16Color*>(OutBuffer);
        for (int32 Y = 0; Y < ReadbackHeight; ++Y)
        {
            for (int32 X = 0; X < ReadbackWidth; ++X)
            {
                const FFloat16Color& Pixel = PixelData[Y * ReadbackWidth + X];
                // 处理像素数据...
            }
        }
    });
```

> 来源：`Source/PCGCompute/Public/PCGTextureReadback.h`

### 基本用法：纹理下采样

支持 Average、Min、Max、Sum 四种聚合模式的纹理下采样。

```cpp
#include "PCGTextureDownsample.h"

// 在 RDG Pass 中执行下采样
void MyDownsampleFunction(FRDGBuilder& GraphBuilder, FRDGTextureRef SourceTexture)
{
    PCGTextureDownsample::FParams DownsampleParams;
    DownsampleParams.Texture = SourceTexture;
    DownsampleParams.Sampler = TStaticSamplerState<SF_Bilinear>::GetRHI();
    DownsampleParams.SliceIndex = 0;
    DownsampleParams.NumSlices = 1;
    DownsampleParams.Mode = EPCGTextureDownsampleMode::Average; // 也可选 Min/Max/Sum

    PCGTextureDownsample::DownsampleTexture(GraphBuilder, DownsampleParams);
}
```

> 来源：`Source/PCGCompute/Internal/PCGTextureDownsample.h`

### 基本用法：纹理膨胀

将有效像素（alpha == 1）向外扩张，填充未覆盖区域。常用于消除纹理接缝。

```cpp
#include "PCGDilate.h"

// 在 RDG 上下文中执行膨胀
void MyDilateFunction(FRDGBuilder& GraphBuilder, FRDGTextureRef Texture)
{
    // 每次迭代向外扩张 1 个像素，多次迭代可覆盖更大空洞
    const int32 Iterations = 4;
    PCGDilate::AddDilatePass(GraphBuilder, Texture, Iterations);
}
```

> 来源：`Source/PCGCompute/Internal/PCGDilate.h`

### 进阶用法：网格 UV 展开到纹理

将静态网格的三角形在 UV 空间中光栅化到纹理上，实现逐纹素的网格属性查询（如位置、覆盖掩码）。

```cpp
#include "PCGUnwrapMesh.h"
#include "Engine/StaticMesh.h"

// 从 LOD 资源初始化展开参数
void UnwrapMeshToTexture(FRDGBuilder& GraphBuilder, UStaticMesh* Mesh)
{
    const FStaticMeshLODResources& LOD = Mesh->GetRenderData()->LODResources[0];

    // 准备展开参数
    PCGUnwrapMesh::FUnwrapParams UnwrapParams;
    UnwrapParams.InitFromLOD(LOD); // 从 LOD 资源自动提取缓冲区信息
    UnwrapParams.UVChannelIndex = 0;
    UnwrapParams.Attribute = PCGUnwrapMesh::EMeshAttribute::Mask; // 只写覆盖掩码
    UnwrapParams.Resolution = FIntPoint(256, 256);

    // 验证参数
    if (!PCGUnwrapMesh::ValidateParams(UnwrapParams))
    {
        UE_LOG(LogPCGCompute, Error, TEXT("Invalid unwrap parameters"));
        return;
    }

    // 创建目标纹理
    FRDGTextureDesc OutputDesc = FRDGTextureDesc::Create2D(
        UnwrapParams.Resolution, PF_R8, FClearValueBinding::Black, TexCreate_RenderTargetable | TexCreate_UAV);
    FRDGTextureRef OutputTexture = GraphBuilder.CreateTexture(OutputDesc, TEXT("PCGUnwrapMask"));

    // 添加展开 Pass（在 UV 空间中光栅化三角形）
    PCGUnwrapMesh::AddUnwrapMeshPass(GraphBuilder, OutputTexture, UnwrapParams);

    // OutputTexture 现在包含每个纹素的覆盖信息
}
```

> 来源：`Source/PCGCompute/Internal/PCGUnwrapMesh.h`

### 进阶用法：光线追踪表面采样

利用硬件光线追踪从场景中采样表面数据，支持获取 UV 坐标用于后续网格属性查询。

```cpp
#include "PCGRayTrace.h"

#if RHI_RAYTRACING
void TraceSurfacePoints(FRDGBuilder& GraphBuilder, const FSceneInterface* Scene, const FSceneView* View, int32 NumPoints)
{
    // 创建输出缓冲区
    FRDGBufferDesc PackedDataDesc = FRDGBufferDesc::CreateBufferDesc(
        sizeof(uint32) * PCGRaytraceConstants::RAY_TRACE_PACKED_BUFFER_STRIDE_UINTS, NumPoints);
    FRDGBufferRef PackedDataBuffer = GraphBuilder.CreateBuffer(PackedDataDesc, TEXT("PCGRayTraceOutput"));

    // 设置光线追踪参数
    FPCGRayTraceParams RayTraceParams;
    RayTraceParams.Scene = Scene;
    RayTraceParams.View = View;
    RayTraceParams.NumRays = NumPoints;
    RayTraceParams.bNeedsUVData = true;  // 需要 UV 数据用于后续网格属性查询
    RayTraceParams.TexCoordsChannelIndex = 0;
    RayTraceParams.PackedDataUAV = GraphBuilder.CreateUAV(PackedDataDesc, PackedDataBuffer);

    // 执行内联光线追踪
    PCGRayTrace::RenderPCGRayTraceInline(GraphBuilder, RayTraceParams);

    // PackedDataBuffer 中每条射线包含 12 个 uint32 的打包数据
    // RAY_CULLED (-1) 表示射线未命中任何表面
}
#endif
```

> 来源：`Source/PCGCompute/Internal/PCGRayTrace.h`

### 进阶用法：启用光线追踪 UV 缓存

为场景预构建光线追踪 UV 缓存，避免每次查询都执行完整的光线追踪。

```cpp
#include "PCGRayTracingUVCacheUtils.h"

// 在游戏线程中请求启用 UV 缓存
void EnablePCGRayTracingUVCache(FSceneInterface* SceneInterface)
{
    // 异步构建缓存（基于场景中所有已有 Primitive）
    // 如果已启用或光线追踪不可用则为空操作
    PCGRayTracingUVCache::RequestEnable_GameThread(SceneInterface);
}
```

> 来源：`Source/PCGCompute/Internal/PCGRayTracingUVCacheUtils.h`

## Demo 示例

以下示例展示如何使用 PCGCompute 的纹理回读和下采样 API，实现从 GPU 纹理中读取高度图数据并进行处理：

### MyPCGComputeExample.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyPCGComputeExample.generated.h"

UCLASS(ClassGroup=(PCG), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyPCGComputeExample : public UActorComponent
{
    GENERATED_BODY()

public:
    /** 触发纹理回读并获取高度数据 */
    UFUNCTION(BlueprintCallable, Category = "PCG|Compute")
    void ReadbackHeightmap(UTexture2D* HeightmapTexture);

    /** 获取上次回读的高度值（供蓝图查询） */
    UFUNCTION(BlueprintPure, Category = "PCG|Compute")
    float GetHeightAtUV(FVector2D UV) const;

private:
    /** 回读数据缓冲区 */
    TArray<float> HeightData;
    FIntPoint DataDimensions = FIntPoint::ZeroValue;
    bool bDataReady = false;
};
```

### MyPCGComputeExample.cpp

```cpp
#include "MyPCGComputeExample.h"
#include "PCGTextureReadback.h"
#include "PCGTextureDownsample.h"
#include "Engine/Texture2D.h"
#include "RenderGraphUtils.h"

void UMyPCGComputeExample::ReadbackHeightmap(UTexture2D* HeightmapTexture)
{
    if (!HeightmapTexture || !HeightmapTexture->GetResource())
    {
        UE_LOG(LogTemp, Warning, TEXT("Invalid heightmap texture"));
        return;
    }

    FPCGTextureReadbackDispatchParams Params;
    Params.SourceTexture = HeightmapTexture->GetResource()->GetTexture2DRHI();
    Params.SourceSampler = TStaticSamplerState<SF_Point, AM_Clamp, AM_Clamp>::GetRHI();
    Params.SourceDimensions = FIntPoint(HeightmapTexture->GetSizeX(), HeightmapTexture->GetSizeY());
    Params.SourceTextureIndex = 0;
    Params.OutputFormat = PF_FloatRGBA;

    // 捕获 this 指针用于回调
    FPCGTextureReadbackInterface::Dispatch(Params,
        [WeakThis = TWeakObjectPtr<UMyPCGComputeExample>(this)](
            void* OutBuffer, int32 ReadbackWidth, int32 ReadbackHeight)
        {
            if (!WeakThis.IsValid()) return;

            UMyPCGComputeExample* Self = WeakThis.Get();
            Self->DataDimensions = FIntPoint(ReadbackWidth, ReadbackHeight);
            Self->HeightData.SetNum(ReadbackWidth * ReadbackHeight);

            const FFloat16Color* Pixels = static_cast<const FFloat16Color*>(OutBuffer);
            for (int32 i = 0; i < ReadbackWidth * ReadbackHeight; ++i)
            {
                Self->HeightData[i] = Pixels[i].R.GetFloat();
            }
            Self->bDataReady = true;
        });
}

float UMyPCGComputeExample::GetHeightAtUV(FVector2D UV) const
{
    if (!bDataReady || HeightData.Num() == 0) return 0.0f;

    // 双线性插值采样
    float U = FMath::Clamp(UV.X, 0.0f, 1.0f) * (DataDimensions.X - 1);
    float V = FMath::Clamp(UV.Y, 0.0f, 1.0f) * (DataDimensions.Y - 1);
    int32 X0 = FMath::FloorToInt(U), Y0 = FMath::FloorToInt(V);
    int32 X1 = FMath::Min(X0 + 1, DataDimensions.X - 1);
    int32 Y1 = FMath::Min(Y0 + 1, DataDimensions.Y - 1);
    float FracX = U - X0, FracY = V - Y0;

    float H00 = HeightData[Y0 * DataDimensions.X + X0];
    float H10 = HeightData[Y0 * DataDimensions.X + X1];
    float H01 = HeightData[Y1 * DataDimensions.X + X0];
    float H11 = HeightData[Y1 * DataDimensions.X + X1];

    return FMath::BiLerp(H00, H10, H01, H11, FracX, FracY);
}
```

## 模块依赖

PCGCompute 是 PCG 框架的 GPU 计算后端，主要依赖渲染子系统。

| 模块 | 用途 |
|---|---|
| `RenderCore` | RDG（Render Dependency Graph）框架，构建 GPU Pass |
| `Renderer` | GPU Scene 管理，光线追踪场景支持 |
| `RHICore` | RHI 核心接口，全局着色器基础设施 |
| `Landscape` | 地形草地地图数据结构（Grass Map Unpacker 依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `1cd8cea5` | [PCG] Fixed potential crash when building the landscape cache, when some entries can't be resolved. | 修复地形缓存构建时部分条目无法解析导致的崩溃 |
| 2026-05-26 | `788faf05` | [PCG] Optimize FPCGComponentVisualizer | 优化 PCG 组件可视化器性能 |
| 2026-05-26 | `0532b644` | [PCG] Fix crash with null objects with accessors | 修复空对象访问器导致的崩溃 |
| 2026-05-26 | `82ca98ed` | [PCG] Optimized & cached metadata size computation, but gated on a flag w/ TLS backing so the normal | 优化并缓存元数据大小计算，通过标志位控制 |
| 2026-05-26 | `585bbecb` | [PCG] Fixed editor update performance issue related to manual edit (+ a double update) and inspection | 修复编辑器手动编辑相关的更新性能问题及双重更新 |

### 维护评价

PCG 是 Unreal Engine 5 中**最重要的新系统之一**，处于**高度活跃维护**状态：

- **创建时间**：2024 年 1 月从 Experimental 移出，正式成为引擎标配组件
- **更新频率**：极高——仅最近一次提交批次就有 5 个相关 commit，涵盖崩溃修复、性能优化等
- **开发投入**：由 Epic Games 核心团队维护，持续投入大量工程资源
- **模块规模**：1472 个源文件的超大型插件，包含 4 个子模块（核心、计算、编辑器、测试）
- **已知限制**：PCGCompute 中的光线追踪功能需要硬件支持（`RHI_RAYTRACING`），不支持软件光追回退

**推荐使用**：PCG 是 Epic 官方主推的程序化内容生成方案，建议所有需要程序化世界的项目使用。PCGCompute 模块作为其 GPU 加速后端，会在启用 PCG 时自动加载，无需手动管理。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG/Tests)