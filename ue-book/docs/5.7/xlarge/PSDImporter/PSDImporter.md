# PSD Importer

> (无描述)

| 属性 | 值 |
|---|---|
| 中文名 | PSD 导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质实例、静态网格体） |
| 模块 | `PSDImporterEditor` (Editor), `PSDImporter` (Runtime), `PSDImporterCore` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PSDImporter) | |

## 用途

PSD Importer 是一个实验性插件，用于将 Adobe Photoshop `.psd` 文件导入到 Unreal Engine 中，并自动将 PSD 的图层结构转换为场景中的层级平面网格（Quad）布局。每个图层会生成一个独立的纹理（层纹理），并保留图层的位置、大小、混合模式、可见性等属性，同时支持图层蒙版和裁剪组。导入后，可在编辑器中直接调整图层的深度偏移、半透明排序优先级等参数，适合用于 2D 场景、UI 原型、界面布局或背景层的快速搭建。

主要解决以下问题：

- 手动从 PSD 导出每个图层为单独图片，再导入 UE 并摆放位置，过程繁琐且容易出错。
- 需要保留 PSD 的图层结构信息（层级、坐标、混合模式、蒙版等）以供后续动态调整。
- 希望将 2D 设计稿直接转化为 3D 世界中的立体层次效果（通过深度偏移实现伪 3D 分层）。

## 使用场景

- **2D 游戏场景搭建**：将 PSD 场景设计稿（如背景、前景、角色立绘）导入 UE，自动生成对应深度层次的平面，减少手动摆放工作量。
- **UI 原型快速迭代**：设计师在 PSD 中调整界面布局后，开发者一键导入更新，保持设计与实现一致性。
- **过场动画背景**：利用图层深度偏移营造纵深感，再用半透明排序控制渲染顺序。
- **概念美术参考**：将多层美术稿导入场景，方便在 3D 视角下查看构图和层次。

## 蓝图用法

插件提供 `UPSDDocument` 对象用于在蓝图中访问 PSD 文档的元数据（名称、尺寸、图层列表）。图层信息存储在结构体 `FPSDFileLayer` 中，可通过数组索引或名称查询单个图层。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Document Name` | 返回 PSD 文档的原始名称（非资产重命名后的名称） | `UPSDDocument` |
| `Get Size` | 返回文档分辨率（像素，`FIntPoint`） | `UPSDDocument` |
| `Get Layers` | 返回所有图层的数组 (`TArray<FPSDFileLayer>`) | `UPSDDocument` |
| `Were Layers Resized On Import` | 返回导入时图层是否被强制缩放到文档大小 | `UPSDDocument` |

此外，`APSDQuadActor`（PSD 层根 Actor）和 `APSDQuadMeshActor`（单个层 Actor）暴露了运行时修改属性（深度偏移、半透明排序）的蓝图可调用函数。

### 使用示例（蓝图）

1. **获取导入的 PSD 文档信息**  
   - 在关卡中放置一个 `APSDQuadActor`（通过内容浏览器拖入 PSD 导入资产会自动生成此 Actor）。  
   - 使用 `Get PSD Document` 节点获取其关联的 `UPSDDocument`。  
   - 连接 `Get Layers` 获取所有图层数据，遍历数组或按索引访问 `FPSDFileLayer` 的 `Id.Name` 等属性。

2. **运行时调整层深度**  
   - 获取场景中 `APSDQuadActor` 引用，调用 `Set Layer Depth Offset` 节点设置层间间隔距离（单位：世界单位）。  
   - 调用 `Set Base Translucent Sort Priority` 节点设置第一层的排序优先级（数字越大越靠前渲染）。

3. **重置单个层属性**  
   - 获取场景中 `APSDQuadMeshActor` 引用，调用 `Reset Quad Texture` 或 `Reset Quad Position` 等节点将对应属性恢复为导入时的原始值。

## C++ 用法

### 头文件引入

```cpp
#include "PSDDocument.h"          // UPSDDocument
#include "PSDQuadActor.h"         // APSDQuadActor
#include "PSDQuadMeshActor.h"     // APSDQuadMeshActor
#include "PSDFile.h"              // FPSDFileLayer, FPSDFileLayerId
#include "PSDLayerTextureUserData.h" // UPSDLayerTextureUserData
```

### 基本用法

```cpp
// 从 APSDQuadActor 获取 PSD 文档
APSDQuadActor* QuadActor = ...; // 获取场景中的 APSDQuadActor 实例
UPSDDocument* Doc = QuadActor->GetPSDDocument();

if (Doc)
{
    // 读取文档名称和尺寸
    const FString& DocName = Doc->GetDocumentName();
    const FIntPoint& DocSize = Doc->GetSize();

    // 获取所有图层
    const TArray<FPSDFileLayer>& Layers = Doc->GetLayers();
    for (const FPSDFileLayer& Layer : Layers)
    {
        UE_LOG(LogTemp, Log, TEXT("Layer: %s, Index: %d"),
            *Layer.Id.Name, Layer.Id.Index);
    }
}
```
*来源：`PSDDocument.h`*

### 进阶用法

```cpp
// 创建 APSDQuadActor 并手动设置 PSD 文档（仅在编辑器内）
#if WITH_EDITOR
UWorld* World = ...; // 获取当前 Editor World
APSDQuadActor* NewQuadActor = World->SpawnActor<APSDQuadActor>();

// 设置 PSD 文档（需要在导入后调用）
NewQuadActor->SetPSDDocument(*MyPSDDocumentInstance);
NewQuadActor->InitComplete(); // 完成初始化，生成子层网格

// 之后可以手动添加单个层网格
APSDQuadMeshActor* MeshActor = ...;
NewQuadActor->AddQuadMesh(*MeshActor);
#endif
```
*来源：`PSDQuadActor.h`*

```cpp
// 遍历所有子层网格
APSDQuadActor* QuadActor = ...;
TArray<APSDQuadMeshActor*> Meshes = QuadActor->GetQuadMeshes();
for (APSDQuadMeshActor* Mesh : Meshes)
{
    if (Mesh)
    {
        // 获取层信息
        const FPSDFileLayer* Layer = Mesh->GetLayer();
        if (Layer)
        {
            // 检查层是否可见且有效
            if (Layer->bVisible && Layer->Bounds.Area() > 0)
            {
                // 操作材质参数（自定义材质使用参数名）
                // 见 UE::PSDImporter::LayerTextureParameterName 等常量
            }
        }

        // 重置位置
        Mesh->ResetQuadPosition();
    }
}
```
*来源：`PSDQuadMeshActor.h`*

## Demo 示例

以下是一个最小 C++ 示例，展示如何通过代码在运行时修改已导入 PSD 场景的层深度偏移。

### MyPSDDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyPSDDemo.generated.h"

class APSDQuadActor;

UCLASS()
class AMyPSDDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyPSDDemo();

    virtual void Tick(float DeltaTime) override;

    UFUNCTION(BlueprintCallable, Category = "PSD Demo")
    void AdjustLayerDepth(float NewOffset);

private:
    UPROPERTY()
    TWeakObjectPtr<APSDQuadActor> QuadActor;

    const float TargetDepth = 2.0f;
};
```

### MyPSDDemo.cpp

```cpp
#include "MyPSDDemo.h"
#include "PSDQuadActor.h"
#include "PSDQuadMeshActor.h"
#include "Engine/World.h"

AMyPSDDemo::AMyPSDDemo()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickGroup = TG_PrePhysics;
}

void AMyPSDDemo::BeginPlay()
{
    Super::BeginPlay();

    // 查找场景中已有的 APSDQuadActor（通过标签或直接 Get 第一个）
    TArray<AActor*> FoundActors;
    UGameplayStatics::GetAllActorsOfClass(GetWorld(), APSDQuadActor::StaticClass(), FoundActors);
    if (FoundActors.Num() > 0)
    {
        QuadActor = Cast<APSDQuadActor>(FoundActors[0]);
    }
}

void AMyPSDDemo::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 示例：根据时间动态调整层深度
    if (QuadActor.IsValid())
    {
        float Offset = TargetDepth * FMath::Sin(GetWorld()->GetTimeSeconds());
        QuadActor->SetLayerDepthOffset(Offset);
    }
}

void AMyPSDDemo::AdjustLayerDepth(float NewOffset)
{
    if (QuadActor.IsValid())
    {
        QuadActor->SetLayerDepthOffset(NewOffset);
    }
}
```

**说明**：此示例演示了在游戏运行时通过 `APSDQuadActor` 的 `SetLayerDepthOffset` 动态改变层间间隔，实现呼吸或推拉效果。

## 模块依赖

插件本身依赖 `GeometryMask`（用于支持几何体掩码功能，如层蒙版和裁剪组的渲染）。使用本插件的其他模块在 `Build.cs` 中需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `PSDImporterCore` | 提供核心 PSD 解析、纹理生成、坐标转换等基础功能 |
| `PSDImporterEditor` | 提供编辑器导入工厂、资产类型注册、Actor 工厂等编辑时功能 |
| `GeometryMask` | 支持图层蒙版（Mask）和裁剪组（Clipping Group）的着色器绑定 |

通常仅需在项目模块的 `PublicDependencyModuleNames` 中添加 `"PSDImporter"` 即可（它会自动引入 `PSDImporterCore`），若需使用编辑器功能则额外添加 `"PSDImporterEditor"`。

**注意**：由于插件为实验性，需手动在 `.uproject` 的 `Plugins` 列表中启用：
```json
{
    "Name": "PSDImporter",
    "Enabled": true
}
```

## 维护状态

### 近期更新

| 日期 | Hash | Commit 解读 |
|---|---|---|
| 2025-07-15 | `bafe5da2` | 静默不正确的 V1051 警告（代码质量改进） |
| 2025-06-05 | `00f9a7c0` | 添加 PSD SDK 的 Windows Arm64 库 + 构建辅助批处理文件 |
| 2025-05-15 | `41b521d3` | 修复导入 16 位和 32 位 PSD 文件时的工作正确性 |
| 2025-05-15 | `708e8190` | 隐藏 Quad Actor 的 `AdjustForViewDistance` 属性（因其不够友好） |
| 2025-05-15 | `c35a5c0e` | 导入含特殊字符的图层时对名称进行清理 |

### 维护评价

- **创建时间**：2025-05-15（距今约 2 个月）
- **更新频率**：创建初期活跃，最近一个月仍有修复和优化
- **功能成熟度**：基础功能（PSD 解析、层纹理生成、四平面布局）完备，已修复多个重要问题（16/32 位支持、特殊字符处理）
- **已知限制**：仍处于实验性阶段，仅支持 Win64 平台；部分属性（如 `AdjustForViewDistance`）因设计不友好被隐藏
- **推荐使用**：适合对 2D 导入工作流有强烈需求的团队，但建议在非生产环境下充分测试，并注意平台限制。随着 Epic 的持续迭代，预计会逐步稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PSDImporter)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/PSDImporter/)（暂未提供，插件未公开）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PSDImporter/Source/PSDImporter/Tests)（若有）