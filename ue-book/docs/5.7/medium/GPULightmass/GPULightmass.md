# GPU Lightmass

> Static lighting building & previewing system using DXR

| 属性 | 值 |
|---|---|
| 中文名 | GPU 光照烘焙 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器设置、蓝图对象） |
| 模块 | `GPULightmass` (UncookedOnly), `GPULightmassEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GPULightmass) | |

## 用途

GPU Lightmass 是虚幻引擎的下一代静态光照烘焙系统，它利用 **DirectX Raytracing (DXR)** 将原本 CPU 上数小时的计算压缩到数分钟甚至实时预览。  
它替代了传统的 *Lightmass（Unreal Lightmass / Swarm）*，提供：

- 全场景完整烘焙（Full Bake）
- 交互式“烘焙你所见”（Bake What You See）模式，可在编辑器移动相机时实时渲染可见的虚拟纹理块
- 支持体积光照贴图（Volumetric Lightmap）
- 辐照度缓存（Irradiance Caching）和首次反弹射线引导（First Bounce Ray Guiding）以提升质量
- 集成 Intel Open Image Denoise (OIDN) 进行降噪
- 静态阴影贴图（Stationary Light Shadows）单独采样

解决的主要问题：**传统 Lightmass 烘焙速度极慢，迭代不便**。GPU Lightmass 使艺术家可以在编辑器内快速看到光照效果并反复调整，显著加速静态光照的迭代工作流。

## 使用场景

- **大型关卡静态光照烘焙** – 传统 Lightmass 可能需要数小时，GPU Lightmass 可在数分钟内完成
- **内饰场景光照迭代** – 使用辐照度缓存和首次反弹射线引导，快速获得物理正确的间接光照
- **户外场景** – 关闭辐照度缓存以加快速度，利用高采样数获得干净环境光
- **预览工作流** – 使用“Bake What You See”模式，仅渲染视口可见区域，调整位置后继续渲染，最后一次性保存
- **体积光照贴图需求** – 为可移动物体、粒子系统等提供动态体积光照

## 蓝图用法

该插件主要通过 **UGPULightmassSettings** 对象暴露设置，该对象在关卡中作为 World Settings 的关联对象被放置（或通过蓝图获取）。  
所有核心属性均为 `BlueprintReadWrite`，因此可直接在蓝图编辑。

### 核心设置（节点：Get / Set Member）

| 节点 / 属性 | 说明 | 类型 |
|---|---|---|
| `GISamples` | 全局光照采样数（每 texel），值越大越干净，推荐与降噪器配合 | `int32` |
| `StationaryLightShadowSamples` | 静态阴影采样数 | `int32` |
| `bUseIrradianceCaching` | 是否启用辐照度缓存（内景推荐） | `bool` |
| `bUseFirstBounceRayGuiding` | 在 IC 开启时，是否使用首次反弹射线引导 | `bool` |
| `IrradianceCacheQuality` | 辐照度缓存质量 | `int32` |
| `DenoisingOptions` | 降噪时机：无 / 完成时 / 交互预览时 | `enum` |
| `Denoiser` | 降噪器选择：Intel OIDN / 简单萤火虫移除 | `enum` |
| `VolumetricLightmapQualityMultiplier` | 体积光照贴图质量倍率 | `int32` |
| `VolumetricLightmapDetailCellSize` | 体积光照贴图最密集区域网格大小（世界单位） | `int32` |
| `bShowProgressBars` | 是否在平铺上显示进度条 | `bool` |
| `Mode` | 烘焙模式：完整烘焙 / 仅烘焙所见 | `enum` |
| `bCompressLightmaps` | 是否压缩光照贴图纹理 | `bool` |

### 获取设置对象

在蓝图中，获取当前世界的 `UGPULightmassSettings` 示例：

```
Get World Settings (World)
  → Cast to UGPULightmassSettings (如果成功)
  → 修改属性
```

或者通过节点 `Get GPULightmass Settings (World)`（需手动注册，默认不提供，但可借助 `Get Subsystem` 或 `Get Default Object`）。

实际使用中，设置对象通常在关卡编辑器的世界设置面板中暴露，无需蓝图手动获取。

## C++ 用法

### 头文件引入

```cpp
#include "GPULightmassModule.h"
#include "GPULightmassSettings.h"
#include "Rendering/StaticLightingSystemInterface.h"
```

### 基本用法

启动 GPU Lightmass 通常由编辑器自动触发。但也可以手动创建：

```cpp
// 在世界初始化后，从模块获取或创建静态光照系统
FGPULightmassModule& GPULightmassModule = FModuleManager::LoadModuleChecked<FGPULightmassModule>("GPULightmass");
UWorld* World = GetWorld();

// 默认设置（会使用用户自定义的或默认的 UGPULightmassSettings）
FGPULightmass* GPULightmass = GPULightmassModule.CreateGPULightmassForWorld(World, nullptr);
// 或传入自定义设置对象
/*
UGPULightmassSettings* MySettings = NewObject<UGPULightmassSettings>();
MySettings->GISamples = 1024;
MySettings->bUseIrradianceCaching = true;
FGPULightmass* GPULightmass = GPULightmassModule.CreateGPULightmassForWorld(World, MySettings);
*/
```

以上代码来源于 `GPULightmassModule.h` 的 `CreateGPULightmassForWorld` 声明。

### 进阶用法

在 `FGPULightmass` 对象中，可以调用 `EditorTick` 来驱动渲染循环（编辑器自动调用）。更细粒度的控制包括：

```cpp
// 开始记录可见瓦片（用于 BakeWhatYouSee 模式）
GPULightmass->StartRecordingVisibleTiles();
// 停止记录并保存
GPULightmass->EndRecordingVisibleTiles();

// 获取体积光照贴图预览数据（用于渲染）
const FPrecomputedVolumetricLightmap* VolLightmap = GPULightmass->GetPrecomputedVolumetricLightmap();
```

（来自 `GPULightmass.h` 的公开接口）

## Demo 示例

以下是一个最小示例，展示如何在编辑器世界初始化时自动启用 GPU Lightmass（通常通过模块的 StartupModule 或 World Subsystem 实现，这里仅用于演示概念）：

**MyGPULightmassSetup.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "GPULightmassSettings.h"
#include "MyGPULightmassSetup.generated.h"

UCLASS()
class UMyGPULightmassSetup : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UPROPERTY()
    UGPULightmassSettings* Settings;
};
```

**MyGPULightmassSetup.cpp**
```cpp
#include "MyGPULightmassSetup.h"
#include "GPULightmassModule.h"
#include "Engine/World.h"
#include "EngineUtils.h"

void UMyGPULightmassSetup::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 获取 GPU Lightmass 模块
    FGPULightmassModule& GPULightmassModule = FModuleManager::LoadModuleChecked<FGPULightmassModule>("GPULightmass");

    // 创建自定义设置
    Settings = NewObject<UGPULightmassSettings>();
    Settings->GISamples = 2048;
    Settings->bUseIrradianceCaching = true;
    Settings->DenoisingOptions = EGPULightmassDenoisingOptions::DuringInteractivePreview;

    // 为当前世界启动 GPU Lightmass
    GPULightmassModule.CreateGPULightmassForWorld(GetWorld(), Settings);
}

void UMyGPULightmassSetup::Deinitialize()
{
    // 模块会自动清理世界关联的静态光照系统
    Super::Deinitialize();
}
```

> **注**：实际使用中，GPULightmass 由编辑器世界设置面板触发，无需手动创建 World Subsystem。此示例仅展示如何通过 C++ 控制。

## 模块依赖

从 Build.cs 推断的核心独特依赖（省略常见模块）：

| 模块 | 用途 |
|---|---|
| `Renderer` | 渲染核心、场景缓冲、GPU 场景管理 |
| `RHI` | 硬件接口抽象、RayTracing 管线 |
| `Landscape` | 地形组件的光照贴图支持 |
| `MeshMaterialShader` | 自定义 GBuffer、光照贴图材质着色器 |
| `RayTracing` | DXR 光线追踪基础设施 |
| `StaticMeshDescription` | 静态网格数据访问 |
| `IntelOIDN` (可选) | Intel Open Image Denoise 集成 |
| `ComputeShader` | 计算着色器（降噪、体积光栅化等） |

> 注：`IntelOIDN` 是条件编译，需在项目设置中启用 `WITH_INTELOIDN=1`。

## 维护状态

### 近期更新

- 2025-11-18 `e716f9a2` [Ray Tracing] Fix a bug in the build instance buffer pass where incorrect GPU scene resources are used
- 2025-09-12 `9bd0ee67` Landscape Editor - Retopologize / XY offset removal (影响到 GPULightmass 的地形支持)
- 2025-09-10 `d4775540` Updated LightmapRenderer to also use MeshBatch.SegmentIndex when setting up bindings
- 2025-09-10 `20d3b102` [HWRT] Fix crash in FRayTracingDynamicGeometryUpdateManager
- 2025-09-02 `b125c860` Fix bug in LightmapRenderer when using RequiresSeparateHitGroupContributionsBuffer

### 维护评价

GPU Lightmass 是一个非常新的插件（约 2025 年创建），但已经经历了多次功能性和修复性更新。  
所属团队（Epic Games）持续维护，包括光线追踪基础设施修复、地形支持优化等。  
目前处于实验性阶段（`IsBetaVersion=true`），可能存在一些边缘情况。  
**推荐使用**，尤其适合寻求快速迭代静态光照的团队。注意需要支持 DXR 的 GPU 和 Windows 64 位系统。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GPULightmass)
- [官方文档](https://docs.unrealengine.com/5.3/en-US/gpu-lightmass-in-unreal-engine/)（参考 UE5.3 最新文档，可能变化）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GPULightmass/Tests)（如果存在）