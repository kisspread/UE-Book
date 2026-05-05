# Procedural Content Generation Framework (PCG)

> Visual scripting framework for procedurally populating worlds with content in editor and/or at run-time.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PCG` (Runtime), `PCGCompute` (Runtime), `PCGEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-01-13 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/PCG) | |

## 用途

PCG插件是一个用于程序化内容生成的可视化脚本框架。它允许开发者和设计师通过节点图的方式，在编辑器中或运行时动态地、程序化地填充游戏世界。其核心价值在于将复杂的程序化生成逻辑（如地形装饰、物体散布、规则化布局）抽象为直观的节点，极大地提高了内容创作的效率和可迭代性。PCGCompute模块是该框架的GPU计算后端，负责将PCG图的计算任务卸载到GPU执行，以处理大规模数据（如从Landscape纹理中读取权重、向GPU场景写入实例数据），从而实现高性能的程序化生成。

## 使用场景

-   **大型开放世界内容填充**：你需要在一个巨大的地图上程序化地散布数百万棵树、岩石和草丛，同时保持高性能。使用PCG框架定义散布规则，并利用PCGCompute模块在GPU上并行处理Landscape权重图和实例放置。
-   **基于规则的场景构建**：你需要根据复杂的规则（如“在斜坡上放置A类物体，在平地上放置B类物体，且物体间保持最小距离”）来生成关卡布局。使用PCG的节点图来可视化地定义这些规则。
-   **运行时动态内容生成**：你需要在玩家移动时动态生成周围的环境细节。PCG框架支持运行时执行，可以结合PCGCompute的GPU加速来实时生成内容。
-   **GPU加速的数据处理**：你需要从Landscape的草图（Grass Map）或高度图中快速读取大量像素数据，用于驱动PCG生成逻辑。`FPCGTextureReadbackInterface` 提供了高效的GPU纹理回读能力。

## 蓝图用法

PCGCompute模块主要提供底层的GPU计算接口和着色器，其设计目标是服务于PCG框架的内部运行时，而非直接暴露给蓝图设计师。因此，该模块**没有直接提供 `BlueprintCallable` 或 `BlueprintReadWrite` 的蓝图节点**。蓝图设计师主要通过PCG框架的上层节点（如`PCGGraph`、`PCGComponent`）来间接使用其GPU加速能力。

## C++ 用法

PCGCompute模块提供了用于GPU计算的底层API，主要面向需要扩展PCG框架或进行高性能数据处理的开发者。

### 头文件引入

```cpp
#include "PCGComputeModule.h"
#include "PCGTextureReadback.h"
#include "PCGSceneWriterCS.h" // 内部头文件，用于GPU场景写入
#include "PCGGrassMapUnpackerCS.h" // 内部头文件，用于解包草地贴图
```

### 基本用法

**1. 使用GPU纹理回读接口 (`FPCGTextureReadbackInterface`)**

此接口用于异步地从GPU纹理（如Landscape权重图）中读取数据到CPU内存。

```cpp
// 来源: Engine/Plugins/PCG/Source/PCGCompute/Public/PCGTextureReadback.h
#include "PCGTextureReadback.h"

void ReadbackLandscapeTexture(UTexture2D* LandscapeWeightTexture)
{
    if (!LandscapeWeightTexture || !LandscapeWeightTexture->GetResource())
    {
        return;
    }

    // 准备回读参数
    FPCGTextureReadbackDispatchParams Params;
    Params.SourceTexture = LandscapeWeightTexture->GetResource()->GetTexture2DRHI();
    Params.SourceSampler = TStaticSamplerState<SF_Point, AM_Clamp, AM_Clamp, AM_Clamp>::GetRHI(); // 使用点过滤以精确读取像素
    Params.SourceDimensions = FIntPoint(LandscapeWeightTexture->GetSizeX(), LandscapeWeightTexture->GetSizeY());
    Params.SourceTextureIndex = 0; // 非纹理数组

    // 定义回读完成后的回调
    auto OnReadbackComplete = [](void* OutBuffer, int32 ReadbackWidth, int32 ReadbackHeight)
    {
        // OutBuffer 指向包含纹理数据的内存块
        // 在这里处理读取到的数据，例如填充PCG数据表
        UE_LOG(LogPCGCompute, Log, TEXT("Texture readback complete. Size: %d x %d"), ReadbackWidth, ReadbackHeight);
    };

    // 从游戏线程发起回读（最常用）
    FPCGTextureReadbackInterface::Dispatch_GameThread(Params, OnReadbackComplete);
}
```

**2. 使用GPU场景写入计算着色器 (`FPCGSceneWriterCS`)**

这是一个实验性的计算着色器，用于将实例数据（如变换、自定义数据）高效地写入GPU场景（GPU Scene），是实现大规模实例化渲染的关键。

```cpp
// 来源: Engine/Plugins/PCG/Source/PCGCompute/Internal/PCGSceneWriterCS.h
// 注意：这是一个内部/实验性API，使用时需谨慎。
#include "PCGSceneWriterCS.h"

// 假设你已经有了实例数据缓冲区 (FRDGBufferSRVRef InstanceDataSRV)
void DispatchSceneWriter(FRHICommandListImmediate& RHICmdList, FRDGBuilder& GraphBuilder, uint32 PrimitiveIndex, uint32 NumInstances, FRDGBufferSRVRef InstanceDataSRV)
{
    // 创建着色器参数
    FPCGSceneWriterCS::FParameters* PassParameters = GraphBuilder.AllocParameters<FPCGSceneWriterCS::FParameters>();
    PassParameters->InPrimitiveIndex = PrimitiveIndex;
    PassParameters->InNumInstancesAllocatedInGPUScene = NumInstances;
    PassParameters->InInstanceOffset = 0;
    PassParameters->InInstanceData = InstanceDataSRV;
    // ... 设置其他参数 ...

    // 获取着色器
    TShaderMapRef<FPCGSceneWriterCS> ComputeShader(GetGlobalShaderMap(GMaxRHIFeatureLevel));

    // 添加计算着色器Pass
    FComputeShaderUtils::AddPass(
        GraphBuilder,
        RDG_EVENTName("PCGSceneWriter"),
        ComputeShader,
        PassParameters,
        FIntVector(FMath::DivideAndRoundUp(NumInstances, FPCGSceneWriterCS::NumThreadsPerGroup), 1, 1)
    );
}
```

### 进阶用法

结合`FPCGGrassMapUnpackerCS`和`FPCGTextureReadbackInterface`，可以实现一个完整的从Landscape草地贴图到PCG数据点的处理流程。

1.  **解包草地贴图**：使用`FPCGGrassMapUnpackerCS`计算着色器，将Landscape渲染的打包草地权重纹理解包成独立的、每个Landscape组件对应的权重纹理数组。
2.  **回读解包后的数据**：使用`FPCGTextureReadbackInterface`将解包后的纹理数据从GPU读回CPU。
3.  **生成PCG数据**：在CPU上处理回读的数据，将其转换为PCG框架所需的点（Points）或属性（Attributes）数据，用于后续的生成逻辑。

## Demo 示例

以下是一个最小化的C++示例，演示如何在你的模块中集成PCGCompute的纹理回读功能。

**1. Build.cs 依赖**
```csharp
// YourModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "PCG", // 依赖PCG运行时模块
    "PCGCompute" // 依赖PCGCompute模块
});
```

**2. 头文件 (MyPCGDataProcessor.h)**
```cpp
// MyPCGDataProcessor.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "PCGTextureReadback.h"
#include "MyPCGDataProcessor.generated.h"

UCLASS()
class UMyPCGDataProcessor : public UObject
{
    GENERATED_BODY()

public:
    /** 开始从指定纹理异步读取数据 */
    UFUNCTION(BlueprintCallable, Category = "PCG")
    void StartTextureReadback(UTexture2D* TextureToRead);

private:
    /** 回调函数，处理读取到的数据 */
    void OnTextureDataReceived(void* DataBuffer, int32 Width, int32 Height);
};
```

**3. 源文件 (MyPCGDataProcessor.cpp)**
```cpp
// MyPCGDataProcessor.cpp
#include "MyPCGDataProcessor.h"
#include "PCGComputeModule.h"

void UMyPCGDataProcessor::StartTextureReadback(UTexture2D* TextureToRead)
{
    if (!TextureToRead || !TextureToRead->GetResource())
    {
        UE_LOG(LogPCGCompute, Warning, TEXT("Invalid texture for readback."));
        return;
    }

    FPCGTextureReadbackDispatchParams Params;
    Params.SourceTexture = TextureToRead->GetResource()->GetTexture2DRHI();
    Params.SourceSampler = TStaticSamplerState<SF_Point>::GetRHI();
    Params.SourceDimensions = FIntPoint(TextureToRead->GetSizeX(), TextureToRead->GetSizeY());

    // 绑定成员函数作为回调
    auto Callback = [WeakThis = TWeakObjectPtr<UMyPCGDataProcessor>(this)](void* Buffer, int32 W, int32 H)
    {
        if (WeakThis.IsValid())
        {
            WeakThis->OnTextureDataReceived(Buffer, W, H);
        }
    };

    FPCGTextureReadbackInterface::Dispatch_GameThread(Params, Callback);
    UE_LOG(LogPCGCompute, Log, TEXT("Texture readback dispatched for: %s"), *TextureToRead->GetName());
}

void UMyPCGDataProcessor::OnTextureDataReceived(void* DataBuffer, int32 Width, int32 Height)
{
    // 在这里处理数据，例如将float数据转换为PCG点
    const float* FloatData = static_cast<const float*>(DataBuffer);
    int32 TotalPixels = Width * Height;

    UE_LOG(LogPCGCompute, Log, TEXT("Received %d pixels of data. First value: %f"), TotalPixels, TotalPixels > 0 ? FloatData[0] : 0.0f);

    // ... 后续处理逻辑 ...
}
```

## 模块依赖

PCGCompute模块的依赖主要集中在渲染和GPU计算相关的底层模块。

| 模块 | 用途 |
|---|---|
| `RenderCore` | 提供渲染核心功能，如渲染命令、着色器编译等。 |
| `RHI` | 渲染硬件接口，用于跨平台GPU资源管理和命令提交。 |
| `Projects` | 用于模块和插件信息查询。 |

## 维护状态

### 近期更新

1.  **c5b4ab7f0b73** (2024-05-28): `[PCG] Fix monochrome instances when using PerInstanceRandom MG node`
    *   **解读**：修复了使用`PerInstanceRandom`材质图节点时，实例显示为单色（无颜色变化）的bug。这是一个针对材质实例化功能的修复。
2.  **ef6f359cd1ae** (2024-05-24): `[PCG] Fix generate landscape textures to deal with subtle details with packing - duplicated rows/columns at common boundaries of landscape components and landscape subsections.`
    *   **解读**：修复了在生成Landscape纹理时，由于打包处理导致在Landscape组件和子区块边界处出现重复行/列的细微错误。这提升了地形数据处理的精度。
3.  **e1e56dd68620** (2024-05-23): `[PCG] Add landscape Z offset to height texture to fix missing offset from heights.`
    *   **解读**：在高度纹理中添加了Landscape的Z轴偏移，修复了之前高度数据缺少此偏移量的问题。这是一个数据准确性修复。

### 维护评价

PCGCompute模块作为PCG框架的GPU计算核心，处于**活跃维护**状态。
-   **创建时间**：模块于2022年随PCG框架一同创建，相对较新。
-   **更新频率**：近期（2024年5月）有多次提交，且均为功能修复和改进，而非简单的编译适配，表明开发团队在持续完善其功能。
-   **功能状态**：模块中包含标记为`[EXPERIMENTAL]`的类（如`FPCGSceneWriterCS`），说明其API仍在演进中，未来可能会有变化。
-   **推荐使用**：对于需要高性能GPU加速PCG生成的项目，特别是涉及大规模Landscape数据交互的场景，推荐使用此模块。但需注意其内部API（标记为`Internal`或`Experimental`）的稳定性风险。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/PCG)
-   [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/PCG/Tests)