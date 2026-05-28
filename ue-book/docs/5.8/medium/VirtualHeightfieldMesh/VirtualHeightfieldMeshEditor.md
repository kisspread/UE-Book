# Virtual Heightfield Mesh

> Mesh renderer for virtual texture heightfields（用于虚拟纹理高度图的网格渲染器）

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟高度场网格 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（高度场纹理资产、材质模板） |
| 模块 | `VirtualHeightfieldMesh` (Runtime), `VirtualHeightfieldMeshEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-22 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualHeightfieldMesh) | |

## 用途

Virtual Heightfield Mesh 插件的核心功能是为虚拟纹理（Virtual Texture）技术提供高效的高度场渲染方案。它主要解决以下问题：

1.  **大规模地形的高度场渲染**：传统高度场渲染在处理超大范围地形时，会面临内存占用过高和渲染性能瓶颈。该插件通过虚拟纹理技术，将高度场数据进行流式加载和按需渲染，显著降低内存消耗并提升渲染效率。
2.  **与虚拟纹理系统的集成**：它将高度场数据（如地形高度图）作为虚拟纹理进行管理，可以利用虚拟纹理系统的流式传输、分页和LOD（Level of Detail）机制，实现高度场的细节层次自适应渲染。
3.  **优化的网格生成**：插件包含一个自定义的网格渲染器组件 (`UVirtualHeightfieldMeshComponent`)，能够根据当前视角和虚拟纹理的可用性，动态生成和更新渲染高度场所需的网格，避免渲染整个巨大的静态网格。

简单来说，这个插件让你能够使用虚拟纹理技术来渲染一个巨大的、细节丰富的高度场（例如地形），而无需一次性加载整个庞大的高度图到内存中。

## 使用场景

-   你在开发一个开放世界游戏或大型景观项目，需要渲染一个远超传统内存限制的高度场地形 → 使用此插件将高度场数据作为虚拟纹理流式加载。
-   你已经使用了虚拟纹理（Runtime Virtual Texturing）来处理大型纹理，并希望将地形高度信息也纳入同一套流式加载和渲染管理框架中。
-   你需要为高度场地形实现视距相关的细节层次（LOD），并且希望利用虚拟纹理系统已有的LOD机制来简化管理。

## 蓝图用法

该插件的核心功能主要通过 `UVirtualHeightfieldMeshComponent` 组件暴露给蓝图。由于提供的源码分析主要针对编辑器模块，运行时组件的具体蓝图节点需查阅 `VirtualHeightfieldMesh` 模块的公开头文件。通常，该组件会提供以下类型的节点：

### 核心节点（基于组件功能推断）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetHeightfieldTexture` | 设置组件使用的目标高度场虚拟纹理资源。 | `UVirtualHeightfieldMeshComponent` |
| `RebuildMesh` | 根据当前虚拟纹理状态强制重新生成渲染网格。 | `UVirtualHeightfieldMeshComponent` |

### 使用示例（蓝图描述）

1.  在你的 Actor 蓝图中，添加一个 `VirtualHeightfieldMeshComponent`。
2.  在组件的细节面板中，指定一个类型为 `UHeightfieldMinMaxTexture` 的资产作为其高度场源。这个资产包含了用于流式加载的高度场金字塔数据。
3.  （可选）通过蓝图设置其他参数，如网格分辨率、LOD 偏移等。
4.  当游戏运行时，该组件将自动根据摄像机位置，从虚拟纹理系统请求所需分辨率的高度场数据，并生成对应的网格进行渲染。

## C++ 用法

### 头文件引入

```cpp
#include "VirtualHeightfieldMeshComponent.h"
// 如果需要在编辑器扩展中交互
#include "VirtualHeightfieldMeshEditorModule.h"
```

### 基本用法

创建和配置一个 `UVirtualHeightfieldMeshComponent`。

```cpp
// 来源：通常在你的 Actor 或 Component 中
// 1. 创建组件实例
UVirtualHeightfieldMeshComponent* HeightfieldComponent = NewObject<UVirtualHeightfieldMeshComponent>(this);
HeightfieldComponent->AttachToComponent(GetRootComponent(), FAttachmentTransformRules::KeepRelativeTransform);
HeightfieldComponent->RegisterComponent();

// 2. 加载并设置高度场纹理资产
UHeightfieldMinMaxTexture* HeightfieldTexture = LoadObject<UHeightfieldMinMaxTexture>(nullptr, TEXT("/Game/Path/To/MyHeightfieldTexture"));
HeightfieldComponent->SetHeightfieldTexture(HeightfieldTexture);

// 3. 可以调用函数手动触发网格重建（通常在编辑器或特定情况下需要）
HeightfieldComponent->RebuildMesh();
```

### 进阶用法

在编辑器工具中检查高度场纹理的状态。

```cpp
// 来源：编辑器工具或自定义编辑器面板
#include "VirtualHeightfieldMeshEditorModule.h"

// 获取编辑器模块接口
IVirtualHeightfieldMeshEditorModule& EditorModule = FModuleManager::Get().LoadModuleChecked<IVirtualHeightfieldMeshEditorModule>("VirtualHeightfieldMeshEditor");

// 检查组件关联的高度场纹理是否已构建 MinMax 数据（用于流式加载）
UVirtualHeightfieldMeshComponent* MyComponent = /* ... */;
if (EditorModule.HasMinMaxHeightTexture(MyComponent))
{
    UE_LOG(LogTemp, Log, TEXT("高度场纹理已包含流式加载所需的 MinMax 数据。"));
}

// 如果需要手动重建 MinMax 数据（通常在源高度图更新后）
bool bSuccess = EditorModule.BuildMinMaxHeightTexture(MyComponent);
if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("高度场纹理 MinMax 数据重建完成。"));
}
```

## Demo 示例

一个最小的示例，展示如何在自定义 Actor 中使用 `UVirtualHeightfieldMeshComponent`。

```cpp
// MyHeightfieldActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyHeightfieldActor.generated.h"

class UVirtualHeightfieldMeshComponent;
class UHeightfieldMinMaxTexture;

UCLASS()
class AMyHeightfieldActor : public AActor
{
    GENERATED_BODY()
public:
    AMyHeightfieldActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    UVirtualHeightfieldMeshComponent* HeightfieldMeshComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Heightfield")
    UHeightfieldMinMaxTexture* HeightfieldTextureAsset;

    virtual void OnConstruction(const FTransform& Transform) override;
};
```

```cpp
// MyHeightfieldActor.cpp
#include "MyHeightfieldActor.h"
#include "VirtualHeightfieldMeshComponent.h"
#include "HeightfieldMinMaxTexture.h" // 假设此头文件定义了资产类

AMyHeightfieldActor::AMyHeightfieldActor()
{
    // 创建高度场网格组件
    HeightfieldMeshComponent = CreateDefaultSubobject<UVirtualHeightfieldMeshComponent>(TEXT("HeightfieldMesh"));
    RootComponent = HeightfieldMeshComponent;
}

void AMyHeightfieldActor::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);

    // 在构造或编辑器中指定资产后，设置纹理
    if (HeightfieldTextureAsset && HeightfieldMeshComponent)
    {
        HeightfieldMeshComponent->SetHeightfieldTexture(HeightfieldTextureAsset);
    }
}
```

## 模块依赖

从 `VirtualHeightfieldMeshEditor` 模块的 `Build.cs` 推断，其主要依赖如下：

| 模块 | 用途 |
|---|---|
| `VirtualHeightfieldMesh` | 运行时核心模块，包含组件和渲染逻辑。 |
| `RHI`, `RenderCore` | 提供渲染硬件接口和核心渲染功能。 |
| `VirtualTexturing` | 虚拟纹理系统的核心依赖。 |
| `AssetTools`, `ContentBrowser` | 用于编辑器中的资产创建和管理。 |

对于 `VirtualHeightfieldMesh` 运行时模块，其依赖应包括 `VirtualTexturing`，`RHI`，`RenderCore` 等。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 UE_LOG 迁移为 UE_LOGF，统一日志格式。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 材质转换器相关的新工作。 |
| 2026-02-03 | `61433296` | Rename FViewMatrices members to follow the <Source>To<Target> pattern for transforms, to reduce ambiguity. | 重命名 FViewMatrices 成员，使其遵循 <源>到<目标> 的变换命名模式，减少歧义。 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃旧的 GPU 分析器相关宏。 |
| 2025-08-29 | `32884de4` | Changing more uses of RHICreateTexture to RHICmdList.CreateTexture. | 将更多的 RHICreateTexture 调用改为 RHICmdList.CreateTexture，以适配新的 RHI 命令列表接口。 |

### 维护评价

-   **创建时间**：约 6 年前创建，属于 UE5 早期实验性插件。
-   **近期更新**：最近的提交集中在 **引擎底层重构**（日志、材质系统、矩阵命名、GPU分析器、RHI接口）的适配，而非插件功能本身的开发。这表明该插件在**被动维护**，以保持与引擎最新变化的兼容性。
-   **活跃度**：插件自创建以来一直标记为 `IsExperimentalVersion=true`，且默认未启用（`EnabledByDefault=false`）。从 Git 历史看，最近两年没有看到新功能或关键 bug 修复的提交，主要都是引擎级的“大扫除”。
-   **已知限制**：作为实验性功能，API 和功能可能不稳定，不适合用于需要长期维护的商业化核心功能。
-   **推荐使用**：**谨慎使用**。如果你正在研究虚拟纹理与高度场结合的技术，或者需要一个快速原型验证，可以尝试。但对于生产项目，建议评估其稳定性和长期支持情况，或考虑基于其思路实现自己的方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualHeightfieldMesh)
-   官方文档：无 (`DocsURL` 为空)
-   测试用例：未在插件目录内发现标准自动化测试文件。