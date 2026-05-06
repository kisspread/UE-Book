# Virtual Heightfield Mesh

> Mesh renderer for virtual texture heightfields

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟高度场网格 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `VirtualHeightfieldMesh` (Runtime), `VirtualHeightfieldMeshEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/VirtualHeightfieldMesh) | |

## 用途

虚拟高度场网格（Virtual Heightfield Mesh）是一个实验性插件，用于将**运行时虚拟纹理（Runtime Virtual Texture）** 中的高度图数据实时渲染为几何网格。它解决了传统地形系统中大规模高度场网格的显存和性能瓶颈问题。

### 核心解决的问题
1. **无限细节的地形渲染**：利用虚拟纹理的分页机制，只加载和渲染视口范围内需要的高度图数据，理论上支持任意大小的地形。
2. **动态 LOD 与遮挡剔除**：通过 MinMax 高度纹理和自定义 LOD 算法，实现高效的多级细节过渡和视锥遮挡查询，减少无效绘制调用。
3. **材质与虚拟纹理无缝集成**：直接使用运行时虚拟纹理中的材质通道，实现地形着色、法线、粗糙度等信息的实时采样，无需额外纹理流送。

### 为什么存在？
在 Unreal Engine 5 中，传统的 LandScape 系统在处理极大世界（如开放世界或特大沙盒地图）时，会遇到内存占用高、加载时间长、LOD 过渡生硬等问题。而运行时虚拟纹理（RVT）本身是一种高效的纹理流送方案，但缺乏将高度图直接转化为可见网格的能力。`VirtualHeightfieldMesh` 填补了这一空缺，使得开发者可以完全基于虚拟纹理构建一个动态、精细、且内存友好的地形系统。

## 使用场景

- **大型开放世界地形**：当你需要创建一个 100km² 以上的可探索地形，且希望拥有从高空到地面近乎无级差的细节时。
- **程序化生成的地形**：如果你使用程序化工具（如 World Machine、Houdini）生成了超高分辨率的高度图，并希望将其直接用作运行时渲染源。
- **需要极高高度精度的场景**：例如峡谷、山脉等具有巨大高度落差的地形，传统网格容易产生走样，而虚拟纹理可以保持精确高度。
- **与 Runtime Virtual Texture Volume 配合**：已有 RVT Volume 并启用了“Height”通道，需要在该区域上快速生成可视网格来替代简单的平面或 Box 代理。

## 蓝图用法

本插件主要通过 `UVirtualHeightfieldMeshComponent` 组件暴露核心功能。由于是实验性插件，蓝图接口较为简练，专注于核心参数的设置与查询。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Virtual Texture Volume` | 返回当前绑定的 `ARuntimeVirtualTextureVolume` 对象，若尚未加载（如来自流式关卡）则返回 `null`。 | `UVirtualHeightfieldMeshComponent` |
| `Get Virtual Texture` | 返回当前绑定 Volume 中的 `URuntimeVirtualTexture` 实例，用于读取高度图数据。 | `UVirtualHeightfieldMeshComponent` |
| `Is MinMax Texture Enabled` | 检查当前虚拟纹理类型是否支持 MinMax 纹理（用于遮挡剔除和 CPU 端高度查询）。仅通道包含“Height”时返回 true。 | `UVirtualHeightfieldMeshComponent` |
| `Get Min Max Texture` | 返回 `UPROPERTY(BlueprintReadOnly)` 中的 `UHeightfieldMinMaxTexture` 对象，可用于进一步 CPU 端分析。 | `UVirtualHeightfieldMeshComponent` |
| `Set Min Max Texture` | 设置一个新的 `UHeightfieldMinMaxTexture`，通常由编辑器构建或从资产库加载。 | `UVirtualHeightfieldMeshComponent` |
| `Build MinMax Texture` | 触发从当前绑定的虚拟纹理高度数据重建 MinMax 纹理的命令（异步过程）。 | `UVirtualHeightfieldMeshComponent` |

### 使用示例（蓝图描述）

**基础设置**：
1. 在关卡中放置一个 `Runtime Virtual Texture Volume`，并将它的 `Material Type` 设置为包含“Height”通道（例如 `WorldHeight`）。
2. 在细节面板中，将该 Volume 的 `Runtime Virtual Texture` 的 `Size` 设为 4096x4096 或更大。
3. 新建一个 `Blueprint Actor`，添加一个 `Virtual Heightfield Mesh Component`。
4. 在该组件下，将 `Virtual Texture` 属性指向第 1 步放置的 Volume。
5. 调整 `LOD 0 Screen Size`、`LOD Distribution` 等参数以获得理想的网格分辨率表现。

**动态隐藏/显示（如用于编辑模式）**：
- 使用 `Set Hidden In Game` 或蓝图自带的 `Set Actor Hidden In Game` 节点控制该 Actor 在运行时是否可见。
- 组件上 `bHiddenInEditor` 属性默认为 true，即默认在编辑器中隐藏，以避免遮挡视角。如需在编辑器下预览，可将该属性设为 false（或通过细节面板取消勾选“Actor Hidden In Editor”）。

## C++ 用法

### 头文件引入

```cpp
#include "VirtualHeightfieldMeshComponent.h"
#include "HeightfieldMinMaxTexture.h"
#include "RuntimeVirtualTextureVolume.h"  // 如果操作 RVT Volume
```

### 基本用法

**在 Actor 上附加组件并绑定虚拟纹理**（典型的初始化流程）：

```cpp
// MyWorldActor.h
#include "VirtualHeightfieldMeshComponent.h"
#include "GameFramework/Actor.h"
#include "MyWorldActor.generated.h"

UCLASS()
class MYMODULE_API AMyWorldActor : public AActor
{
    GENERATED_BODY()

public:
    AMyWorldActor()
    {
        VirtualHeightfieldComponent = CreateDefaultSubobject<UVirtualHeightfieldMeshComponent>(TEXT("VirtualHeightfieldComponent"));
        VirtualHeightfieldComponent->SetWorldTransform(FTransform::Identity);
        VirtualHeightfieldComponent->SetMobility(EComponentMobility::Static);
    }

    void SetVirtualTextureVolume(ARuntimeVirtualTextureVolume* InVolume)
    {
        if (VirtualHeightfieldComponent)
        {
            // 从 SoftObjectPtr 转为 UObject 引用
            VirtualHeightfieldComponent->VirtualTexture = InVolume;
            // 以下为内部依赖，通常自动完成，但也可手动触发重建
            VirtualHeightfieldComponent->BuildMinMaxTexture();
        }
    }

private:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VirtualHeightfield", meta = (AllowPrivateAccess = "true"))
    TObjectPtr<UVirtualHeightfieldMeshComponent> VirtualHeightfieldComponent;
};

// 来源：VirtualHeightfieldMeshComponent.h，Actor 示例参考 VirtualHeightfieldMeshActor.h 和测试代码
```

**检查并启用功能**：

```cpp
// 检查当前 FStaticFeatureLevel 是否支持该插件
if (VirtualHeightfieldMesh::IsEnabled(GMaxRHIFeatureLevel))
{
    // 执行后续渲染逻辑
}
// 来源：VirtualHeightfieldMeshEnable.h
```

### 进阶用法

**手动构建 MinMax 纹理以获得 CPU 端高度数据**：

`UHeightfieldMinMaxTexture` 支持将低分辨率 mip 的高度范围数据复制到 `TextureData` 数组中，以便 CPU 端进行碰撞检测或 AI 导航。

```cpp
#include "HeightfieldMinMaxTexture.h"
#include "Engine/Texture2D.h"

void PerformHeightQuery(const UHeightfieldMinMaxTexture* MinMaxTex, const FVector2D& InUV, float& OutMinHeight, float& OutMaxHeight)
{
    if (!MinMaxTex || MinMaxTex->TextureData.Num() == 0)
    {
        OutMinHeight = 0.0f;
        OutMaxHeight = 0.0f;
        return;
    }

    // TextureData 存储的是 FVector2D 数组，X=Min, Y=Max，按 mip 排列
    // 简化示例：直接取 mip0 对应像素（需要根据 UV 映射到 FIntPoint 坐标）
    int32 PixelX = FMath::FloorToInt(InUV.X * MinMaxTex->TextureDataSize.X);
    int32 PixelY = FMath::FloorToInt(InUV.Y * MinMaxTex->TextureDataSize.Y);
    int32 Index = PixelY * MinMaxTex->TextureDataSize.X + PixelX;

    if (Index < MinMaxTex->TextureData.Num())
    {
        OutMinHeight = MinMaxTex->TextureData[Index].X;
        OutMaxHeight = MinMaxTex->TextureData[Index].Y;
    }
}
// 来源：HeightfieldMinMaxTexture.h
```

**高级渲染参数配置（通过 C++ 修改组件细节属性）**：

```cpp
UVirtualHeightfieldMeshComponent* Comp = ...;

// 设置 LOD 参数以获得更精细的几何
Comp->Lod0ScreenSize = 0.5f;
Comp->Lod0Distribution = 2.0f;
Comp->LodDistribution = 1.5f;
Comp->LodBiasScale = 0.2f;
Comp->NumForceLoadLods = 2;
Comp->NumOcclusionLods = 3;

// 标记需要重新生成相机相关数据
Comp->MarkRenderStateDirty();
// 来源：VirtualHeightfieldMeshComponent.h
```

## Demo 示例

以下是一个最小但完整的模块，展示了如何创建一个包含 `VirtualHeightfieldMeshComponent` 的 Actor，并绑定一个 `RuntimeVirtualTextureVolume`。假设项目已启用该插件和 RVT 相关插件。

**ProjectName.Build.cs** 中添加依赖：
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "VirtualHeightfieldMesh", "RuntimeVirtualTexture" });
```

**MyCustomHeightfieldActor.h**：
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCustomHeightfieldActor.generated.h"

class UVirtualHeightfieldMeshComponent;
class ARuntimeVirtualTextureVolume;

UCLASS()
class YOURMODULE_API AMyCustomHeightfieldActor : public AActor
{
    GENERATED_BODY()

public:
    AMyCustomHeightfieldActor();

    /** 设置绑定的虚拟纹理体积 */
    UFUNCTION(BlueprintCallable, Category = "Heightfield")
    void SetRuntimeVolume(ARuntimeVirtualTextureVolume* InVolume);

    /** 获取目前绑定的虚拟纹理组件 */
    UFUNCTION(BlueprintCallable, Category = "Heightfield")
    UVirtualHeightfieldMeshComponent* GetHeightfieldComponent() const { return HeightfieldComponent; }

private:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Heightfield", meta = (AllowPrivateAccess = "true"))
    TObjectPtr<UVirtualHeightfieldMeshComponent> HeightfieldComponent;
};
```

**MyCustomHeightfieldActor.cpp**：
```cpp
#include "MyCustomHeightfieldActor.h"
#include "VirtualHeightfieldMeshComponent.h"
#include "RuntimeVirtualTextureVolume.h"

AMyCustomHeightfieldActor::AMyCustomHeightfieldActor()
{
    PrimaryActorTick.bCanEverTick = false;

    HeightfieldComponent = CreateDefaultSubobject<UVirtualHeightfieldMeshComponent>(TEXT("HeightfieldComponent"));
    RootComponent = HeightfieldComponent;

    // 设置推荐的默认值
    HeightfieldComponent->Lod0ScreenSize = 1.0f;
    HeightfieldComponent->LodDistribution = 2.0f;
    HeightfieldComponent->NumForceLoadLods = 1;
    HeightfieldComponent->SetHiddenInGame(false);
    HeightfieldComponent->bHiddenInEditor = false; // 可在编辑器中预览
}

void AMyCustomHeightfieldActor::SetRuntimeVolume(ARuntimeVirtualTextureVolume* InVolume)
{
    if (HeightfieldComponent && InVolume)
    {
        HeightfieldComponent->VirtualTexture = InVolume;
        HeightfieldComponent->UpdateBounds();
        HeightfieldComponent->MarkRenderStateDirty();
    }
}
```

**说明**：上述 Demo 假设 `YourModule` 已引用 `VirtualHeightfieldMesh` 和 `RuntimeVirtualTexture`。放置该 Actor 后，调用 `SetRuntimeVolume` 传入场景中已配置好的 RVT Volume，即可实时渲染高度场网格。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RuntimeVirtualTexture` | 提供虚拟纹理的读取、分页及渲染上下文，是本插件渲染数据的来源 |
| `RenderCore` | 提供渲染管线基础类型（FRDGBuilder, FRDGTexture, 着色器参数结构体） |
| `RHI` | 底层硬件接口，用于创建纹理、着色器资源视图等 |
| `Engine` | 标准引擎类型（AActor, UPrimitiveComponent, UTexture2D 等） |
| `Projects` | 用于模块加载和设置访问 |

> 注意：由于 `VirtualHeightfieldMesh` 本身依赖了 `RuntimeVirtualTexture`，使用本插件时项目必须同时启用 `RuntimeVirtualTexture` 和 `VirtualTextures`（项目设置中开启）。

## 维护状态

### 近期更新

| 日期 | Commit Hash | 说明 |
|---|---|---|
| 2025-08-29 | `32884de4` | 将部分 `RHICreateTexture` 调用迁移至 `RHICmdList.CreateTexture`，适配新版 RHI 接口 |
| 2025-07-18 | `462ec4ed` | 修复 V623 警告：`?:` 运算符创建临时对象问题 |
| 2025-06-18 | `08316dbb` | 在 `MaterialResource` 中缓存 `ShaderPlatform`，并从 `ShaderPlatform` 推导 FeatureLevel |
| 2025-04-28 | `5fe685f4` | 运行时虚拟纹理全面改用 `PooledRenderTarget`，不再直接使用底层 RHI Texture |
| 2025-04-23 | `939cc6e5` | 初次提交：使用 FortniteClient 构建目标转换所有文件，添加 `dllstorage` 相关导出宏 |

### 维护评价

- **创建时间**：2025年4月23日（仅约 6 个月）
- **活跃度**：**非常活跃**。几乎每月都有针对渲染管线优化和 API 兼容性的提交，且紧跟 UE5 引擎主分支的 RHI 和 RVT 重构节奏。
- **功能性**：功能完整，支持 LOD、遮挡剔除、MinMax 纹理构建、编辑器内自定义等。但作为 `IsExperimentalVersion=true` 的插件，其公开 API 和内部结构仍可能在未来版本中发生较大变化。
- **推荐程度**：✅ **推荐在实验性项目、技术验证或开放世界原型中使用**。不建议在已上线的、对 API 稳定性要求极高的产品中依赖此插件，因为它尚未脱离实验阶段。

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualHeightfieldMesh)
- [虚幻引擎官方文档 - 运行时虚拟纹理](https://docs.unrealengine.com/5.7/en-US/runtime-virtual-textures-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualHeightfieldMesh/Tests)（如果存在）
- [UHeightfieldMinMaxTexture 源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/VirtualHeightfieldMesh/Source/VirtualHeightfieldMesh/Public/HeightfieldMinMaxTexture.h)
- [UVirtualHeightfieldMeshComponent 源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/VirtualHeightfieldMesh/Source/VirtualHeightfieldMesh/Public/VirtualHeightfieldMeshComponent.h)