# Virtual Heightfield Mesh

> Mesh renderer for virtual texture heightfields

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟高度场网格 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质表达式、资产类型） |
| 模块 | `VirtualHeightfieldMesh` (Runtime), `VirtualHeightfieldMeshEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-22 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualHeightfieldMesh) | |

## 用途

该插件提供了一个专门为**虚拟纹理（Virtual Texture）** 驱动的**高度场（Heightfield）** 设计的网格渲染器。它解决了使用传统静态网格体渲染大面积、高细节地形时遇到的性能和内存瓶颈问题。

核心思想是将地形的高度数据存储为虚拟纹理中的一页（Tile），并根据摄像机的距离和视角，动态地使用不同精度的几何体（LOD）来渲染这些“页”。这种方式避免了为整个地形创建和加载一个巨大的静态网格体，而是按需加载和渲染当前可见区域的细节，特别适合超大规模地形。

## 使用场景

- 你正在开发一个开放世界游戏，需要渲染一个面积巨大（例如 16km x 16km）且细节丰富的地形。
- 你希望地形系统能高效地与 **Runtime Virtual Texture (RVT)** 系统集成，利用虚拟纹理的流式加载和 mipmap 管理机制。
- 你需要地形能够根据摄像机距离自动切换几何体细节（LOD），并且希望这种切换与虚拟纹理的页加载逻辑紧密结合，以最小化视觉上的“Pop-in”现象。
- 你希望在编辑器中只看到用于生成虚拟纹理的源几何体（如 Landscape Actor），而在游戏中只看到最终渲染的高度场网格，以优化编辑器性能。

## 蓝图用法

插件主要提供了一个用于放置和配置高度场网格的 Actor 和组件，以及一个用于构建 MinMax 纹理的资产类型。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Virtual Texture Volume` | 获取与此组件关联的 RuntimeVirtualTextureVolume Actor。 | `UVirtualHeightfieldMeshComponent` |
| `Get MinMax Texture` | 获取用于加速遮挡剔除和 LOD 计算的 MinMax 纹理资产。 | `UVirtualHeightfieldMeshComponent` |
| `Is MinMax Texture Enabled` | 检查当前虚拟纹理类型是否支持 MinMax 纹理优化。 | `UVirtualHeightfieldMeshComponent` |

### 使用示例（蓝图描述）

1.  **放置 Actor**：在关卡中放置一个 `AVirtualHeightfieldMesh` Actor。它自带一个 `UVirtualHeightfieldMeshComponent`。
2.  **关联虚拟纹理**：在组件的 `Heightfield` 分类下，将 `Virtual Texture` 属性指向场景中已经设置好的 `ARuntimeVirtualTextureVolume` Actor。这个 Volume 定义了地形虚拟纹理的边界和数据源。
3.  **配置材质**：在组件的 `Rendering` 分类下，为 `Material` 属性指定一个材质。此材质应使用 `Runtime Virtual Texture Sample` 节点来采样颜色和法线，并可以使用专门的 `MaterialExpressionHeightfieldMinMaxTexture` 节点来访问 MinMax 纹理数据。
4.  **构建 MinMax 纹理**：在 `HeightfieldBuild` 分类下，点击 `Build MinMax Texture` 按钮（在编辑器中）。这将生成一个 `UHeightfieldMinMaxTexture` 资产，用于优化遮挡剔除。
5.  **调整 LOD**：通过 `Rendering` 分类下的 `LOD 0 Screen Size`、`LOD Distribution` 等参数，控制几何体的细分程度和 LOD 切换距离。

## C++ 用法

该插件的 C++ API 主要围绕 `UVirtualHeightfieldMeshComponent` 的创建、配置和查询。

### 头文件引入

```cpp
#include "VirtualHeightfieldMeshComponent.h"
#include "HeightfieldMinMaxTexture.h"
```

### 基本用法

获取组件关联的虚拟纹理资源，并查询其配置。

```cpp
// 假设已经有一个指向 UVirtualHeightfieldMeshComponent 的指针 (HeightfieldComp)
if (HeightfieldComp)
{
    // 1. 获取关联的 RVT Volume Actor
    ARuntimeVirtualTextureVolume* RVTVolume = HeightfieldComp->GetVirtualTextureVolume();
    if (RVTVolume)
    {
        UE_LOG(LogTemp, Log, TEXT("RVT Volume found: %s"), *RVTVolume->GetName());
    }

    // 2. 获取并检查 MinMax 纹理
    UHeightfieldMinMaxTexture* MinMaxTex = HeightfieldComp->GetMinMaxTexture();
    if (HeightfieldComp->IsMinMaxTextureEnabled() && MinMaxTex && MinMaxTex->Texture)
    {
        UE_LOG(LogTemp, Log, TEXT("MinMax Texture is set: %s"), *MinMaxTex->Texture->GetName());
    }

    // 3. 读取 LOD 参数
    float LOD0ScreenSize = HeightfieldComp->GetLod0ScreenSize();
    float LODDistribution = HeightfieldComp->GetLodDistribution();
    int32 ForceLoadLODs = HeightfieldComp->GetNumForceLoadLods();
    UE_LOG(LogTemp, Log, TEXT("LOD0 Size: %f, Distribution: %f, ForceLoadLODs: %d"), LOD0ScreenSize, LODDistribution, ForceLoadLODs);
}
```

### 进阶用法

在编辑器中，通过代码触发 MinMax 纹理的构建过程。

```cpp
#if WITH_EDITOR
// 在构建管道或自定义编辑器工具中使用
if (UHeightfieldMinMaxTexture* MinMaxTextureAsset = /* 加载或创建 UHeightfieldMinMaxTexture 资产 */)
{
    // 构建一个 FHeightfieldMinMaxTextureBuildDesc 描述结构体
    FHeightfieldMinMaxTextureBuildDesc BuildDesc;
    // ... 配置 BuildDesc 的成员，例如 SourceTexture 等 ...

    // 调用构建函数
    MinMaxTextureAsset->BuildTexture(BuildDesc);

    // 构建完成后，通知所有引用此纹理的组件进行更新
    VirtualHeightfieldMesh::NotifyComponents(MinMaxTextureAsset);
}
#endif
```

## Demo 示例

一个最小化的组件设置示例，演示如何在 C++ Actor 中创建和配置一个虚拟高度场网格组件。

**VirtualHeightfieldMeshDemoActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "VirtualHeightfieldMeshDemoActor.generated.h"

class UVirtualHeightfieldMeshComponent;
class UHeightfieldMinMaxTexture;

UCLASS()
class AVirtualHeightfieldMeshDemoActor : public AActor
{
	GENERATED_BODY()

public:
	AVirtualHeightfieldMeshDemoActor();

protected:
	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Demo")
	TObjectPtr<UVirtualHeightfieldMeshComponent> HeightfieldMeshComponent;

	// 用于测试的 MinMax 纹理资产（通常在编辑器中设置）
	UPROPERTY(EditAnywhere, Category = "Demo")
	TObjectPtr<UHeightfieldMinMaxTexture> MinMaxTextureAsset;
};
```

**VirtualHeightfieldMeshDemoActor.cpp**
```cpp
#include "VirtualHeightfieldMeshDemoActor.h"
#include "VirtualHeightfieldMeshComponent.h"
#include "HeightfieldMinMaxTexture.h"

AVirtualHeightfieldMeshDemoActor::AVirtualHeightfieldMeshDemoActor()
{
	HeightfieldMeshComponent = CreateDefaultSubobject<UVirtualHeightfieldMeshComponent>(TEXT("HeightfieldMesh"));
	RootComponent = HeightfieldMeshComponent;

	// 设置默认材质
	static ConstructorHelpers::FObjectFinder<UMaterialInterface> DefaultMaterial(TEXT("/VirtualHeightfieldMesh/MI_DefaultHeightfield"));
	if (DefaultMaterial.Succeeded())
	{
		HeightfieldMeshComponent->Material = DefaultMaterial.Object;
	}
}

void AVirtualHeightfieldMeshDemoActor::BeginPlay()
{
	Super::BeginPlay();

	// 在运行时设置 MinMax 纹理
	if (MinMaxTextureAsset)
	{
		// 注意：通常 MinMax 纹理在编辑器阶段构建好，运行时直接使用。
		// 这里仅为演示在运行时获取并检查。
		UE_LOG(LogTemp, Log, TEXT("Using MinMax Texture: %s"), *MinMaxTextureAsset->GetName());
	}

	// 配置 LOD 参数
	HeightfieldMeshComponent->Lod0ScreenSize = 0.5f; // 让 LOD0 覆盖更大的屏幕范围
	HeightfieldMeshComponent->LodDistribution = 2.2f; // 更平缓的 LOD 切换
}
```

## 模块依赖

该插件的核心依赖围绕着虚拟纹理和渲染系统。

| 模块 | 用途 |
|---|---|
| `RenderCore` | 提供渲染核心功能，如 RHI 命令、Render Graph (RDG) 等。 |
| `RHI` | 抽象渲染硬件接口。 |
| `VirtualTexture` | 虚拟纹理系统的核心，用于管理和流式传输虚拟纹理页。 |
| `Renderer` | UE 的渲染器，包含材质编译、场景代理等。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新的材质转换器工作（相关改动）。 |
| 2026-02-03 | `61433296` | Rename FViewMatrices members to follow the &lt;Source&gt;To&lt;Target&gt; pattern for transforms, to reduce ambi | 重命名 FViewMatrices 成员以遵循"源到目标"的变换模式，减少歧义。 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃旧的 GPU 性能分析器相关宏。 |
| 2025-08-29 | `32884de4` | Changing more uses of RHICreateTexture to RHICmdList.CreateTexture. | 将更多 RHICreateTexture 的用法改为 RHICmdList.CreateTexture。 |

### 维护评价

该插件创建于 2020 年，距今已有约 6 年，属于**老古董**级别。从最近的 Git 提交记录来看，其更新主要是**引擎范围的底层重构和现代化适配**（如日志宏迁移、RHI 接口变更、废弃旧 API），而不是针对虚拟高度场网格本身的新功能开发或重大问题修复。

它目前仍标记为 **Experimental（实验性）** 且 **默认未启用**，这意味着 Epic 可能将其视为一个功能原型或技术演示，而非一个稳定、完全支持的生产就绪功能。虽然它仍然能够编译和运行，但其维护状态可被评价为**不活跃维护**。

**建议**：如果你正在评估是否在新项目中使用此插件，请谨慎。它可能在未来的引擎版本中被修改或移除，并且可能缺少一些边缘情况的处理。它更适合作为一个高级参考或用于原型验证。对于生产环境，考虑使用更成熟、文档更完善的地形解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualHeightfieldMesh)
- [官方文档]() (无)
- [测试用例]() (插件目录内未发现独立测试文件)