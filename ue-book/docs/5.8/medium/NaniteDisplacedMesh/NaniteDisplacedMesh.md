# Nanite Displaced Mesh

> Asset and component types that provide a basic pre-displacement pipeline for Nanite meshes

| 属性 | 值 |
|---|---|
| 中文名 | Nanite 位移网格 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产类型、编辑器工具） |
| 模块 | `NaniteDisplacedMesh` (Runtime), `NaniteDisplacedMeshEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-05-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NaniteDisplacedMesh) | |

## 用途

该插件为 Nanite 网格提供**离线预位移（pre-displacement）管线**。核心解决的问题是：Nanite 网格本身不支持运行时顶点位移（Tessellation/Displacement），因此需要在资产构建阶段，将位移贴图（Displacement Map）烘焙到 Nanite 网格的顶点数据中。

插件的完整工作流程：
1. 指定一个基础静态网格（BaseMesh）作为输入
2. 配置一张或多张位移贴图（Displacement Map），控制 UV 采样通道、幅度、中心值等参数
3. 系统在编辑器/烘焙阶段对基础网格进行细分（tessellation），然后应用位移，生成最终的 Nanite 资产
4. 结果通过 `UNaniteDisplacedMeshComponent` 渲染

该插件处于实验阶段（Beta），默认不启用，需要手动在插件管理器中启用后才能使用。

## 使用场景

- 你需要在 Nanite 网格上实现地形般的效果（如岩石表面细节、侵蚀纹理），但 Nanite 不支持运行细分曲面 → 用 NaniteDisplacedMesh 预先烘焙位移
- 你有一个低多边形的 Nanite 静态网格，想通过高度贴图增加几何细节而不增加手动建模工作量 → 配置 DisplacementMap 后自动生成高精度 Nanite 网格
- 你是程序化内容生成管线的一部分，需要在烘焙阶段自动生成位移网格 → 通过 `bIsEditable = false` 标记资产为工具生成，防止手工修改

## 蓝图用法

该插件提供一个蓝图可生成的组件 `UNaniteDisplacedMeshComponent`，以及资产类型 `UNaniteDisplacedMesh`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DisplacedMesh` (属性) | 指向 NaniteDisplacedMesh 资产，定义位移参数 | `UNaniteDisplacedMeshComponent` |
| `Parameters` (属性) | 位移参数：基础网格、细分精度、位移贴图列表 | `UNaniteDisplacedMesh` |
| `bIsEditable` (属性) | 标记资产是否可手动编辑（工具生成时设为 false） | `UNaniteDisplacedMesh` |

### 使用示例（蓝图描述）

1. **创建 NaniteDisplacedMesh 资产**：在内容浏览器右键 → Rendering → Nanite Displaced Mesh，创建资产
2. **配置参数**：打开资产，设置 `BaseMesh`（一个 Nanite 静态网格），调整 `RelativeError`（细分精度，0.01~1.0，值越小网格越密），添加 `DisplacementMaps`（指定纹理、幅度、中心值、UV 通道）
3. **放置组件**：在 Actor 上添加 `NaniteDisplacedMeshComponent`，将 `DisplacedMesh` 属性指向创建的资产
4. 组件会自动使用 Nanite 渲染位移后的网格

### 位移贴图参数说明

| 参数 | 说明 |
|---|---|
| `Texture` | 位移纹理（高度图） |
| `Magnitude` | 位移强度，0 表示无位移 |
| `Center` | 位移中心值（纹理值映射的零点偏移） |
| `UVChannel` | 采样位移纹理使用的 UV 通道（0-7） |
| `MaskUVChannel` | 遮罩 UV 通道，-1 表示不应用遮罩 |

## C++ 用法

### 头文件引入

```cpp
#include "NaniteDisplacedMesh.h"
#include "NaniteDisplacedMeshComponent.h"
#include "NaniteDisplacedMeshAlgo.h"
```

### 基本用法

配置位移参数并通过算法函数应用位移：

```cpp
#include "NaniteDisplacedMeshAlgo.h"
#include "NaniteDisplacedMesh.h"

// 配置位移贴图
FNaniteDisplacedMeshDisplacementMap DisplacementMap;
DisplacementMap.Texture = MyHeightTexture;      // UTexture2D*
DisplacementMap.Magnitude = 50.0f;               // 位移幅度
DisplacementMap.Center = 0.5f;                   // 中心偏移
DisplacementMap.UVChannel = 0;                   // 采样 UV 通道

// 配置位移参数
FNaniteDisplacedMeshParams Params;
Params.BaseMesh = MyStaticMesh;                  // 基础 Nanite 静态网格
Params.RelativeError = 0.03f;                    // 细分精度
Params.DisplacementMaps.Add(DisplacementMap);

// 应用位移到网格数据
FMeshBuildVertexData Verts;
TArray<uint32> Indexes;
TArray<int32> MaterialIndexes;
FBounds3f VertexBounds;

bool bSuccess = UE::NaniteDisplacedMesh::DisplaceNaniteMesh(
    Params,
    Verts,
    Indexes,
    MaterialIndexes,
    VertexBounds
);
```

### 进阶用法

使用自定义位移选项，并处理异步编译：

```cpp
// 使用忽略非归一化 UV 的选项
using namespace UE::NaniteDisplacedMesh;

bool bSuccess = DisplaceNaniteMesh(
    Params,
    Verts,
    Indexes,
    MaterialIndexes,
    VertexBounds,
    EDisplacementOptions::IgnoreNonNormalizedDisplacementUVs  // UV 超出 [0,1] 范围时忽略位移
);
```

监听位移网格资产的渲染数据变化（编辑器中）：

```cpp
#if WITH_EDITOR
// 注册回调，当位移网格重新构建完成时通知
auto OnRebuild = UNaniteDisplacedMesh::FOnRebuild::CreateLambda([]()
{
    // 处理渲染数据更新
    UE_LOG(LogNaniteDisplacedMesh, Log, TEXT("Displaced mesh rendering data rebuilt"));
});

FDelegateHandle Handle = MyDisplacedMesh->RegisterOnRenderingDataChanged(OnRebuild);

// 取消注册
MyDisplacedMesh->UnregisterOnRenderingDataChanged(Handle);
#endif
```

## Demo 示例

### NaniteDisplacedMeshActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NaniteDisplacedMeshActor.generated.h"

class UNaniteDisplacedMeshComponent;
class UNaniteDisplacedMesh;

UCLASS(BlueprintType, Blueprintable)
class ANaniteDisplacedMeshActor : public AActor
{
    GENERATED_BODY()

public:
    ANaniteDisplacedMeshActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UNaniteDisplacedMeshComponent> DisplacedMeshComponent;

    /** 配置位移网格资产 */
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Displacement")
    TObjectPtr<UNaniteDisplacedMesh> DisplacedMeshAsset;

    /** 运行时动态调整位移幅度的倍率 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Displacement")
    float DisplacementScale = 1.0f;
};
```

### NaniteDisplacedMeshActor.cpp

```cpp
#include "NaniteDisplacedMeshActor.h"
#include "NaniteDisplacedMeshComponent.h"
#include "NaniteDisplacedMesh.h"

ANaniteDisplacedMeshActor::ANaniteDisplacedMeshActor()
{
    DisplacedMeshComponent = CreateDefaultSubobject<UNaniteDisplacedMeshComponent>(TEXT("DisplacedMesh"));
    RootComponent = DisplacedMeshComponent;
}
```

## 模块依赖

由于 Build.cs 内容未提供，以下依赖基于源码中的 `#include` 和 Nanite 渲染模块的典型依赖推断：

| 模块 | 用途 |
|---|---|
| `NaniteCore` | Nanite 核心渲染数据结构（FResources、FMeshDataSectionArray） |
| `RenderCore` | 渲染核心基础设施（FRenderCommandFence 等） |
| `MeshDescription` | 网格构建数据结构（FMeshBuildVertexData） |
| `DerivedDataCache` | DDC 异步缓存派生数据 |
| `AssetRegistry` | 资产编译管理器 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `dcfc273f` | [Nanite] Merging //UE5/Dev-NaniteResearch to Main (//UE5/Main) | 合并 Nanite 研究分支到主线 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符匹配问题 |
| 2026-04-20 | `61ad5fea` | Nanite Displaced Mesh Editor \| When cooking ignore editor only and NeverCook levels and assets | 烘焙时跳过编辑器专用和 NeverCook 关卡 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为新式 UE_LOGF 宏 |
| 2025-10-20 | `bbe63845` | [Nanite Displaced Mesh] Fix mesh with single UV channel not having any displacement when using custo | 修复单 UV 通道网格使用自定义位移时无效的问题 |

### 维护评价

该插件处于**活跃维护**状态。最近一次更新在 2026 年 5 月，近 1 个月内有多次实质性提交，包括从 Nanite 研究分支合并功能、烘焙流程优化、平台兼容性修复和代码现代化（UE_LOGF 迁移）。尽管插件标记为实验性（Beta）且默认不启用，但从提交频率看仍被 Epic 团队积极维护。2025 年 10 月还有功能性 bug 修复，说明该插件仍在被实际使用。

**注意事项**：
- 该插件仍为实验性功能，API 可能在未来版本中变更
- 默认不启用，需手动在插件管理器中开启
- 部分 API（如旧版 `EDisplaceNaniteMeshOptions::Type`）已在 5.7 标记为废弃

**推荐**：如果你需要在 Nanite 网格上实现预位移效果，该插件是目前唯一的官方解决方案，可以在实验性项目中使用，但需要注意 API 稳定性风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NaniteDisplacedMesh)
- 官方文档（无）
- [运行时模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NaniteDisplacedMesh/Source/NaniteDisplacedMesh)
- [编辑器模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NaniteDisplacedMesh/Source/NaniteDisplacedMeshEditor)