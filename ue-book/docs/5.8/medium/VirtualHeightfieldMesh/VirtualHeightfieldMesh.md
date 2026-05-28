# Virtual Heightfield Mesh

> Mesh renderer for virtual texture heightfields（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟高度场网格 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `VirtualHeightfieldMesh` (Runtime), `VirtualHeightfieldMeshEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-22 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualHeightfieldMesh) | |

## 用途

该插件旨在解决超大规模地形的渲染难题。它并非传统的地形编辑器，而是一个专用的渲染器，通过结合 **虚拟纹理 (Virtual Textures)** 和 **高度图 (Heightmap)** 技术，能够高效渲染幅员极其辽阔、细节层次丰富的地形网格。

核心价值在于：
1.  **按需加载**：利用虚拟纹理系统，仅在需要时从磁盘流式加载地形纹理数据，极大降低了内存消耗，使得渲染百平方公里甚至更大范围的地形成为可能。
2.  **无缝细节**：通过 `UHeightfieldMinMaxTexture` 存储每个区域的高度极值，用于精确的视锥体裁剪和遮挡剔除，避免了传统LOD系统中常见的“跳变”问题。
3.  **程序化友好**：高度图数据可以由程序生成或来自真实世界数据，配合虚拟纹理，可以实现动态、可交互的地形外观变化。

## 使用场景

*   **开放世界游戏**：当你需要创建一个巨大、无缝、且具有丰富视觉细节的地图时，例如山地、峡谷或平原。
*   **建筑可视化/仿真**：需要基于真实地理数据（如DEM）构建高精度地形模型，并进行大规模渲染。
*   **影视级场景**：需要程序化生成或加载超大范围地形，并配合动态材质（如季节、天气变化）进行渲染。

## 蓝图用法

该插件提供的蓝图API主要集中在 `UVirtualHeightfieldMeshComponent` 和 `UHeightfieldMinMaxTexture` 两个类中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Virtual Texture Volume` | 获取与此组件关联的运行时虚拟纹理体积 (ARuntimeVirtualTextureVolume)。 | `UVirtualHeightfieldMeshComponent` |
| `Get Virtual Texture` | 获取关联的运行时虚拟纹理对象 (URuntimeVirtualTexture)。 | `UVirtualHeightfieldMeshComponent` |
| `Get Min Max Texture` | 获取用于存储高度极值信息的纹理对象。 | `UVirtualHeightfieldMeshComponent` |
| `Build Texture` | 根据构建描述，在编辑器中重新构建高度极值纹理。 | `UHeightfieldMinMaxTexture` |
| `Initialize Min Max Texture` | [编辑器专用] 用指定的尺寸和数据初始化高度极值纹理。 | `UVirtualHeightfieldMeshComponent` |

### 使用示例（蓝图描述）

1.  **放置组件**：在场景中放置一个 `AVirtualHeightfieldMesh` Actor，或者在任何Actor上添加 `UVirtualHeightfieldMeshComponent` 组件。
2.  **连接数据**：在组件的细节面板中，将 `VirtualTexture` 属性指向场景中已放置的 `ARuntimeVirtualTextureVolume` 资产，该体积应包含你的虚拟纹理高度图数据。
3.  **配置渲染**：调整 `Material`、`Lod0ScreenSize`、`LodDistribution` 等参数以控制地形网格的材质、几何细节和LOD过渡距离。
4.  **构建极值纹理**：在组件的 `HeightfieldBuild` 分类下，设置好 `MinMaxTexture` 资产后，点击 `Build Min Max Texture` 按钮。此操作会从高度图数据中计算并存储每个区域的极值，用于优化渲染。

## C++ 用法

以下用法基于提供的头文件信息推断，适用于需要通过代码控制或扩展该插件的场景。

### 头文件引入

```cpp
#include "VirtualHeightfieldMeshComponent.h"
#include "HeightfieldMinMaxTexture.h"
```

### 基本用法

**创建和配置组件（来自 UVirtualHeightfieldMeshComponent.h）**

```cpp
// 假设在某个Actor或管理类中
UVirtualHeightfieldMeshComponent* HeightfieldComp = NewObject<UVirtualHeightfieldMeshComponent>(this);
HeightfieldComp->RegisterComponent();

// 设置关联的虚拟纹理体积（需要在场景中预先存在）
// 注意：通常通过蓝图编辑器设置更方便，这里展示代码可能性
ARuntimeVirtualTextureVolume* VolumeActor = /* 获取或查找场景中的Volume */;
HeightfieldComp->VirtualTexture = VolumeActor;

// 设置渲染材质
UMaterialInterface* MyTerrainMaterial = /* 加载或创建材质 */;
HeightfieldComp->Material = MyTerrainMaterial;

// 调整LOD参数
HeightfieldComp->Lod0ScreenSize = 0.8f; // 减小值会增加近景几何密度
HeightfieldComp->LodDistribution = 1.8f;
```

**使用高度极值纹理（来自 HeightfieldMinMaxTexture.h）**

```cpp
// 获取组件上的 MinMaxTexture
UHeightfieldMinMaxTexture* MinMaxTex = HeightfieldComp->GetMinMaxTexture();
if (MinMaxTex && MinMaxTex->Texture)
{
    // 可以访问纹理资源
    UTexture2D* HeightMinMaxUTexture = MinMaxTex->Texture;
    
    // 在CPU端访问低Mip层级的数据（用于物理或逻辑计算）
    const TArray<FVector2D>& CPUData = MinMaxTex->TextureData;
    FIntPoint DataSize = MinMaxTex->TextureDataSize;
    // ... 处理数据
}
```

### 进阶用法

**与虚拟纹理系统交互（来自 UVirtualHeightfieldMeshComponent.h 及 SceneProxy.h）**

组件内部通过 `ARuntimeVirtualTextureVolume` 获取 `URuntimeVirtualTexture`，并利用其接口与虚拟纹理分配系统 (`IAllocatedVirtualTexture`) 通信，动态请求所需的纹理页面。`FVirtualHeightfieldMeshSceneProxy` 负责在渲染线程持有这些资源，并驱动顶点工厂 (`FVirtualHeightfieldMeshVertexFactory`) 根据虚拟纹理页面表 (`PageTableTexture`) 来采样高度图 (`HeightTexture`)，从而动态生成地形网格。

**自定义材质表达式节点（来自 HeightfieldMinMaxTextureMaterialExpression.h）**

插件提供了自定义的材质表达式 `UMaterialExpressionHeightfieldMinMaxTexture`。在C++中，你可以创建一个材质，并在材质编辑器（或通过代码）中添加此节点，将其 `MinMaxTexture` 属性指向你的 `UHeightfieldMinMaxTexture` 资产。该节点会在材质中输出对应的纹理对象，用于材质图中的采样，例如用于基于高度的着色或视差遮蔽。

## Demo 示例

以下是一个最小化的C++示例，展示如何创建一个 `UVirtualHeightfieldMeshComponent` 并为其设置材质。

**MyTerrainManager.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "VirtualHeightfieldMeshComponent.h" // 引入组件头文件
#include "MyTerrainManager.generated.h"

UCLASS()
class AMyTerrainManager : public AActor
{
    GENERATED_BODY()

public:
    AMyTerrainManager();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Terrain", meta = (AllowPrivateAccess = "true"))
    TObjectPtr<UVirtualHeightfieldMeshComponent> VirtualHeightfieldComponent;
};
```

**MyTerrainManager.cpp**
```cpp
#include "MyTerrainManager.h"
#include "Runtime/Engine/Classes/Engine/World.h"

AMyTerrainManager::AMyTerrainManager()
{
    PrimaryActorTick.bCanEverTick = false;
    VirtualHeightfieldComponent = CreateDefaultSubobject<UVirtualHeightfieldMeshComponent>(TEXT("VirtualHeightfield"));
    RootComponent = VirtualHeightfieldComponent;
}

void AMyTerrainManager::BeginPlay()
{
    Super::BeginPlay();

    // 在游戏开始时，可以动态配置组件（如果需要）
    // 例如：加载一个材质并设置
    // UMaterialInterface* LoadedMaterial = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Materials/M_Terrain"));
    // if (LoadedMaterial)
    // {
    //     VirtualHeightfieldComponent->Material = LoadedMaterial;
    // }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RuntimeVirtualTexture` | 提供运行时虚拟纹理的核心系统，是本插件实现按需加载和流式传输的基石。 |
| `VirtualHeightfieldMeshEditor` | 提供编辑器内的工具、资产编辑器和菜单项，用于管理高度极值纹理的构建和预览。 |
| （无其他特殊依赖，主要依赖 Unreal 核心的 Rendering 和 Core 模块） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏统一迁移至UE_LOGF格式。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新的材质翻译器相关工作（引擎范围改动）。 |
| 2026-02-03 | `61433296` | Rename FViewMatrices members to follow the <Source>To<Target> pattern for transforms, to reduce ambi... | 重命名 FViewMatrices 成员以遵循源到目标的变换命名模式，减少歧义（引擎范围重构）。 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃了旧版的GPU性能分析器相关宏。 |
| 2025-08-29 | `32884de4` | Changing more uses of RHICreateTexture to RHICmdList.CreateTexture. | 将更多 RHICreateTexture 调用更改为 RHICmdList.CreateTexture（渲染API迁移）。 |

### 维护评价

*   **创建时间**：插件创建于2020年10月，已有约6年历史。
*   **近期更新频率**：最近的提交记录均为**引擎范围的API重构或迁移**（如日志系统、渲染API、命名规范），而非针对 `VirtualHeightfieldMesh` 插件本身的功能增强或bug修复。最近一次实质性的插件专属更新时间不详。
*   **维护状态**：该插件标记为 **实验性 (IsExperimentalVersion = true)** 且 **默认未启用 (EnabledByDefault = false)**。结合其长期无专属功能更新的记录，表明它处于 **“维护不活跃”** 状态。Epic 可能将其视为一个技术验证或特定领域的解决方案，但未积极投入开发资源进行完善。
*   **已知限制**：作为实验性插件，其稳定性、API完整性以及对新UE特性的支持可能无法保证。在生产环境中使用存在风险。
*   **推荐度**：**仅推荐用于技术研究、原型验证或对特定超大地形渲染有强烈需求且愿意承担技术风险的项目**。对于常规项目，UE5 内置的 `Landscape` 系统或 `PCG`（程序化内容生成）框架配合虚拟纹理可能是更稳定、功能更全面的选择。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualHeightfieldMesh)
- 官方文档：无（`.uplugin` 中 `DocsURL` 为空）
- 测试用例：未在插件目录内发现标准测试用例。