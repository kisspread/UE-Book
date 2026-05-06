# Nanite Displaced Mesh

> Asset and component types that provide a basic pre-displacement pipeline for Nanite meshes

| 属性 | 值 |
|---|---|
| 中文名 | Nanite 位移网格 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `NaniteDisplacedMesh` (Runtime), `NaniteDisplacedMeshEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-07 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NaniteDisplacedMesh) | |

## 用途

该插件为 Nanite 网格体提供了一条**预位移管道**。它允许用户通过一个或多个高度图（位移贴图）在离线时对基础 StaticMesh 进行顶点位移，生成一个新的、烘焙好的 Nanite 网格体。这样，原本需要实时位移的复杂地形或细节可以通过预计算方式纳入 Nanite 的 LOD 系统，获得更好的性能与视觉质量。

核心价值：
- 将位移效果**固化**到 Nanite 网格体几何中，无需在运行时执行顶点纹理采样或曲面细分。
- 同时支持多个位移贴图叠加，实现丰富的地形细节或装饰性浮雕。
- 借助 Nanite 的自动 LOD 管理，实现极高精度的几何细节而无需担心三角形数量。

该插件目前属于**实验性版本（0.1）**，功能正在迭代中。

## 使用场景

- **地形细节**：使用一张或多个位移贴图对基础地形网格进行预位移，产生真实的凹凸、沟壑、悬崖等细节，之后以 Nanite 网格体形式渲染。
- **岩石 / 悬崖**：对低多边形岩石模型应用位移贴图，生成高多边形细节，利用 Nanite 高效渲染。
- **建筑装饰**：在墙面、浮雕或装饰性物体上预应用位移贴图，代替昂贵的曲面细分或视差映射。
- **性能优化**：将原本需要曲面细分阶段的应用场景替换为预位移，减少 GPU 计算负载。

## 蓝图用法

### 核心节点

该插件将主要数据暴露为两种蓝图结构体，并提供了一个组件类 `UNaniteDisplacedMeshComponent`。

| 节点 / 属性 | 说明 | 所在类 / 结构 |
|---|---|---|
| `DisplacedMesh` | 指定关联的 `UNaniteDisplacedMesh` 资产（蓝图读写） | `UNaniteDisplacedMeshComponent` |
| `DisplacementMaps` | 位移贴图数组，每个元素包含纹理、幅度和中心值 | `FNaniteDisplacedMeshParams` |
| `BaseMesh` | 用作位移基础的 StaticMesh | `FNaniteDisplacedMeshParams` |
| `RelativeError` | 位移后网格的相对误差（控制 LOD 精度） | `FNaniteDisplacedMeshParams` |
| 创建 `Nanite Displaced Mesh` 资产 | 通过内容浏览器右键菜单新建 | `UNaniteDisplacedMesh`（资产工厂） |

#### 使用示例（蓝图描述）

1. **创建位移网格资产**：
   - 在内容浏览器中右键 → “Miscellaneous” → “Nanite Displaced Mesh”。
   - 在新资产上打开详情面板，设置 `Base Mesh`（StaticMesh）、`Displacement Maps`（添加元素并指定纹理、调整 Magnitude 和 Center）。

2. **在关卡中使用**：
   - 在任意 Actor 中添加 `Nanite Displaced Mesh Component`（蓝图节点：`Add Component` → 搜索 “Nanite Displaced Mesh”）。
   - 设置组件的 `Displaced Mesh` 属性为上一步创建的资产。
   - 该组件会自动加载并渲染预位移后的 Nanite 网格体。

3. **运行时修改位移参数（不可重烘焙）**：
   - 组件上的 `DisplacedMesh` 属性可在蓝图中修改，但修改后**不会**触发重新烘焙（烘焙发生在编辑器或烹饪阶段）。运行时只能切换不同已烘焙的资产。

## C++ 用法

### 头文件引入

```cpp
#include "NaniteDisplacedMesh.h"           // UNaniteDisplacedMesh 及参数结构体
#include "NaniteDisplacedMeshComponent.h" // 组件
#include "NaniteDisplacedMeshAlgo.h"      // 离线位移算法（编辑器可用）
```

### 基本用法

创建一个 `UNaniteDisplacedMesh` 对象并设置参数，然后使用组件显示它（通常在编辑器脚本或工具中完成）。

*来源：* 推断自公有 API 及编辑器模块（NaniteDisplacedMeshEditor）行为。

```cpp
// 在编辑器工具蓝图中或 C++ 编辑命令中

UNaniteDisplacedMesh* DisplacedMesh = NewObject<UNaniteDisplacedMesh>();
DisplacedMesh->Params.BaseMesh = MyBaseStaticMesh;
DisplacedMesh->Params.RelativeError = 0.03f;
DisplacedMesh->Params.DisplacementMaps.Add({
    .Texture = MyDisplacementTexture,
    .Magnitude = 5.0f,
    .Center = 0.0f
});

// 触发异步烘焙（插件内部自动在编辑器中对资产进行预编译）
// 烹饪时也会自动执行
```

然后使用组件：

```cpp
UNaniteDisplacedMeshComponent* Comp = CreateDefaultSubobject<UNaniteDisplacedMeshComponent>(TEXT("MyDisplacedMesh"));
Comp->DisplacedMesh = DisplacedMesh;
// 组件会在 OnRegister 时自动绑定 Nanite 资源
```

### 进阶用法

在编辑器工具或自动化测试中，可直接调用 `DisplaceNaniteMesh` 函数进行离线位移（仅编辑器可用）。

*来源：* `Public/NaniteDisplacedMeshAlgo.h`，位于 `Engine/Plugins/Experimental/NaniteDisplacedMesh/Source/NaniteDisplacedMesh/Public/NaniteDisplacedMeshAlgo.h`

```cpp
#if WITH_EDITOR
#include "NaniteDisplacedMeshAlgo.h"
#include "StaticMeshAttributes.h"
#include "MeshDescription.h"

// 假设已有 FNaniteDisplacedMeshParams Params 和 MeshDescription
FMeshBuildVertexData Verts;
TArray<uint32> Indexes;
TArray<int32> MaterialIndexes;
FBounds3f VertexBounds;

bool bSuccess = DisplaceNaniteMesh(
    Params,
    NumTextureCoord, // 通常从 BaseMesh 获取
    Verts,
    Indexes,
    MaterialIndexes,
    VertexBounds,
    EDisplaceNaniteMeshOptions::IgnoreNonNormalizedDisplacementUVs
);
// 成功后，可用 Verts/Indexes 构建新的 FStaticMeshRenderData
#endif
```

**注意：** 此函数在运行时不可用，标记了 `WITH_EDITOR`。

## Demo 示例

以下是一个最小化的 Actor 类，在编辑器中创建并显示一个预位移网格。

### MyDisplacedActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDisplacedActor.generated.h"

class UNaniteDisplacedMeshComponent;
class UNaniteDisplacedMesh;

UCLASS()
class AMYDisplacedActor : public AActor
{
    GENERATED_BODY()

public:
    AMYDisplacedActor();

protected:
    virtual void OnConstruction(const FTransform& Transform) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Displaced Mesh")
    UNaniteDisplacedMeshComponent* DisplacedMeshComponent;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Displaced Mesh")
    UNaniteDisplacedMesh* DisplacedMeshAsset;
};
```

### MyDisplacedActor.cpp

```cpp
#include "MyDisplacedActor.h"
#include "NaniteDisplacedMeshComponent.h"
#include "NaniteDisplacedMesh.h"

AMyDisplacedActor::AMyDisplacedActor()
{
    PrimaryActorTick.bCanEverTick = false;
    DisplacedMeshComponent = CreateDefaultSubobject<UNaniteDisplacedMeshComponent>(TEXT("DisplacedMeshComponent"));
    RootComponent = DisplacedMeshComponent;
}

void AMyDisplacedActor::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);

    if (DisplacedMeshComponent && DisplacedMeshAsset)
    {
        DisplacedMeshComponent->DisplacedMesh = DisplacedMeshAsset;
    }
}
```

**说明**：将 `DisplacedMeshAsset` 设置为已创建的 `UNaniteDisplacedMesh` 资产，在编辑视口中即可看到渲染结果。烹饪（Cook）时该资产会自动烘焙为 Nanite 网格体。

## 模块依赖

**当前模块（NaniteDisplacedMesh，Runtime）** 的依赖（基于头文件分析）：

| 模块 | 用途 |
|---|---|
| `Nanite` | 提供 `Nanite::FResources`、`Nanite::FPageStreamingState` 等核心类型 |
| `StaticMeshDescription` / `StaticMesh` | 基础网格体描述与渲染数据 |
| `RenderCore` | 渲染资源与命令同步（`FRenderCommandFence`） |
| `Engine` | 游戏对象、组件基类 |

**编辑器模块（NaniteDisplacedMeshEditor，Editor）** 额外依赖：`UnrealEd`、`AssetTools`、`PropertyEditor` 等标准编辑器模块。

> **注意**：以上依赖不包含 Core、CoreUObject、Slate 等引擎通用模块（已在模板中省略）。使用时，你的模块只需额外添加 `Nanite`、`StaticMesh`、`RenderCore` 等即可（若已包含 Engine 则通常已涵盖大多数，但 Nanite 需显式列出）。

## 维护状态

### 近期更新

- 2025-09-29 `32dcdf1c` — Cooker: SkipOnlyEditorOnly: Nanite: Mark that the NaniteDisplacedMesh package loads are editor-only
- 2025-09-12 `f89d77ef` — Additional non-unity fixes from removing GCObject.h from StrongObjectPtr.h
- 2025-08-22 `d82d12d8` — Enable Geometry::TAdaptiveTessellator for Nanite tessellation
- 2025-08-07 `45c08907` — [Backout] - CL44647866
- 2025-08-07 `f7c6b9f6` — Enable Geometry::TAdaptiveTessellator for Nanite tessellation

### 维护评价

- **创建时间**：2025-08-07（约 1 个月）
- **近期更新频率**：每月至少 2-3 次提交，包含功能更新（启用自适应细分器）和烹饪优化。
- **活跃程度**：**活跃维护**，处于实验性阶段，功能在积极开发中。
- **已知问题**：
  - 当前版本（0.1）为 Beta，API 可能不稳定。
  - 位移参数修改后需要重新烘焙资产（编辑器或烹饪触发）。
- **推荐使用**：适合在**实验性项目**中尝试 Nanite 预位移管道的开发者；不建议用于生产级项目，直到版本稳定。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NaniteDisplacedMesh)
- [官方文档](https://docs.unrealengine.com/5.7/zh-CN/nanite-displaced-mesh/)（如有）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NaniteDisplacedMesh/Tests)