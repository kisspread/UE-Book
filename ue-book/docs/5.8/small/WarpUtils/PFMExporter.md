# Warp Utils

> PFM/MPCDI generation & visualization（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 投影映射工具 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `PFMExporter` (Runtime), `WarpUtils` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-07-18 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WarpUtils) | |

## 用途

WarpUtils 插件主要用于支持 nDisplay 高级可视化集群环境，特别是处理多投影仪融合（Warp & Blend）的场景。其核心功能是将场景中静态网格体的几何数据，基于指定的UV坐标作为屏幕空间映射，导出为 PFM（Point Field Mesh）格式的文件。生成的 PFM 文件包含了网格体顶点在三维空间中的精确位置，可以被外部投影校正软件读取，用于生成精确的投影映射和几何校正数据。此外，插件也支持 MPCDI（Multi-Projector Common Data Interface）标准，这是用于多投影仪系统配置和数据交换的通用格式。

简单来说，这个插件解决了从虚幻引擎场景中精确导出用于物理环境投影校正（如穹顶、CAVE、复杂曲面）所需的几何数据的问题。

## 使用场景

-   你正在搭建一个多投影仪融合的 CAVE（Cave Automatic Virtual Environment）或穹顶影院系统，需要将虚幻引擎中制作的场景，精确地映射到物理空间的曲面屏幕上。
-   你需要为投影校正软件（如 Scalable Display、Warpalizer 等）提供从引擎视角生成的精确几何网格数据，以进行像素级对齐和边缘融合。
-   你的项目涉及建筑投影、舞台视觉或复杂的沉浸式体验，其中虚拟内容的渲染需要与非平面的物理展示表面完美契合。

## 蓝图用法

该插件主要通过蓝图接口暴露功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Export Static Mesh to PFM file` | 将静态网格体组件导出为PFM文件 | `IPFMExporterBlueprintAPI` |
| `PFMExporter Module API` | 获取PFM导出功能的蓝图接口实例 | `UPFMExporterBlueprintLib` |

### 使用示例（蓝图描述）

1.  **获取API**：首先使用“PFMExporter Module API”节点获取插件的蓝图接口引用。
2.  **调用导出**：将获取到的接口引用连接到“Export Static Mesh to PFM file”节点。为该节点指定：
    *   `Src Mesh`：你场景中需要导出的`UStaticMeshComponent`组件。该网格体需要包含一个UV通道，其UV范围0到1将被映射为最终PFM文件的屏幕空间坐标。
    *   `Origin`（可选）：一个场景组件，用于定义导出坐标系的原点。如果不指定，则使用`Src Mesh`组件的父级或世界原点。
    *   `Width` 和 `Height`：设置输出PFM纹理的分辨率，这决定了投影映射的精度。
    *   `File Name`：输出的PFM文件的路径和名称。
3.  **执行**：该节点返回一个布尔值，指示导出是否成功。

## C++ 用法

### 头文件引入

```cpp
// 包含模块接口
#include "IPFMExporter.h"

// 包含蓝图接口（如果需要通过蓝图API调用）
#include "Blueprints/IPFMExporterBlueprintAPI.h"
```

### 基本用法

通过模块接口直接调用 C++ API。
**来源：** `Source/PFMExporter/Public/IPFMExporter.h`

```cpp
// 确保 PFMExporter 模块可用
if (IPFMExporter::IsAvailable())
{
    // 获取模块引用
    IPFMExporter& PFMExporterModule = IPFMExporter::Get();

    // 准备导出参数
    // 1. 获取静态网格体的LOD资源数据 (FStaticMeshLODResources)
    // 2. 计算网格体到原点的变换矩阵 (FMatrix MeshToOrigin)
    // 3. 设置PFM分辨率
    // 4. 设置输出文件名

    // 调用导出函数
    bool bSuccess = PFMExporterModule.ExportPFM(
        SrcMeshLODResources,  // const FStaticMeshLODResources*
        MeshToOriginMatrix,   // const FMatrix&
        1920,                 // int PFMWidth
        1080,                 // int PFMHeight
        TEXT("/Game/Output/projector_warp.pfm") // const FString&
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("PFM file exported successfully."));
    }
}
```

### 进阶用法

使用蓝图接口实现，使其可以在蓝图或非绑定上下文中使用。
**来源：** `Source/PFMExporter/Public/Blueprints/IPFMExporterBlueprintAPI.h`, `Source/PFMExporter/Private/Blueprints/PFMExporterBlueprintAPIImpl.h`

```cpp
// 使用蓝图接口的实现类
UPFMExporterAPIImpl* PFMExporterAPI = NewObject<UPFMExporterAPIImpl>();

// 获取需要导出的静态网格体组件
UStaticMeshComponent* MeshComp = /* ... */;

// 定义原点（例如，某个CAVE环境的中心点）
USceneComponent* CaveOrigin = /* ... */;

// 调用蓝图接口函数
bool bExported = PFMExporterAPI->ExportPFM(
    MeshComp,    // UStaticMeshComponent*
    CaveOrigin,  // USceneComponent*
    1024,        // int Width
    768,         // int Height
    TEXT("CaveScreen_Warp.pfm") // const FString&
);
```

## Demo 示例

一个通过C++调用PFM导出功能的最小示例。

**MyPFMExporter.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IPFMExporter.h"
#include "MyPFMExporter.generated.h"

UCLASS()
class AMyPFMExporter : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category="PFM Export")
    UStaticMeshComponent* TargetMesh;

    UPROPERTY(EditAnywhere, Category="PFM Export")
    int32 ExportWidth = 1920;

    UPROPERTY(EditAnywhere, Category="PFM Export")
    int32 ExportHeight = 1080;

    UPROPERTY(EditAnywhere, Category="PFM Export")
    FString ExportFilePath = TEXT("/Game/PFM_Export/output.pfm");

    UFUNCTION(BlueprintCallable, CallInEditor, Category="PFM Export")
    bool ExportTargetMeshToPFM();
};
```

**MyPFMExporter.cpp**
```cpp
#include "MyPFMExporter.h"
#include "StaticMeshResources.h" // For FStaticMeshLODResources

bool AMyPFMExporter::ExportTargetMeshToPFM()
{
    if (!TargetMesh || !TargetMesh->GetStaticMesh())
    {
        UE_LOG(LogTemp, Error, TEXT("TargetMesh is invalid."));
        return false;
    }

    // 检查模块可用性
    if (!IPFMExporter::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("PFMExporter module is not available."));
        return false;
    }

    // 获取网格体渲染数据
    const FStaticMeshLODResources& LODResource = TargetMesh->GetStaticMesh()->GetRenderData()->LODResources[0];

    // 计算从网格体空间到导出原点（这里用Actor自身）的变换矩阵
    const FMatrix& MeshToOrigin = TargetMesh->GetComponentTransform().ToMatrixWithScale().Inverse();

    // 调用模块API导出
    IPFMExporter& Exporter = IPFMExporter::Get();
    return Exporter.ExportPFM(
        &LODResource,
        MeshToOrigin,
        ExportWidth,
        ExportHeight,
        ExportFilePath
    );
}
```

## 模块依赖

该插件的模块依赖比较特殊，`PFMExporter` 作为 Runtime 模块，却依赖了通常仅在编辑器中存在的模块。

| 模块 | 用途 |
|---|---|
| `EditorFramework` | 提供编辑器框架基础支持 |
| `UnrealEd` | 提供静态网格体资源编辑和数据访问接口，用于读取LOD资源 |

**说明**：由于 `PFMExporter` 模块依赖 `UnrealEd`，这意味着它只能在编辑器环境下运行，不能用于打包后的游戏程序（Runtime）。它主要是一个编辑器期的工具。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新的UE_LOGF格式。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 为即将到来的头文件清理工作预先添加缺失的include。 |
| 2025-08-29 | `32884de4` | Changing more uses of RHICreateTexture to RHICmdList.CreateTexture. | 继续将过时的RHI纹理创建函数迁移至命令列表的新API。 |
| 2025-01-21 | `42de2ffc` | Merging RHI CreateBuffer refactor to Main. | 合并RHI缓冲区创建重构到主分支。 |
| 2024-02-22 | `01203093` | Deprecate: | 标记某些功能为废弃。 |

### 维护评价

-   **创建时间**：创建于2019年，已有约7年历史。
-   **更新频率与内容**：最近的提交都是引擎底层RHI（渲染硬件接口）和日志系统的API迁移，属于被动维护以保证在新引擎版本中能编译通过。没有任何新功能或用户体验改进的提交。
-   **活跃度**：**维护不活跃**。插件本身的功能已经基本固化，最近几年没有实质性功能更新。最后一次可能涉及功能调整的提交在2024年2月标记为“Deprecate:”，暗示可能有功能被移除或标记为过时。
-   **已知限制**：
    1.  **运行时不可用**：由于依赖 `UnrealEd`，该插件无法在打包后的游戏或应用中运行。
    2.  **实验性**：插件被标记为 `IsBetaVersion = true`，意味着API和功能可能不稳定。
    3.  **平台限制**：`PFMExporter` 模块仅限 Win64 平台。
-   **推荐使用**：仅推荐在 **编辑器环境** 下，用于专业的 nDisplay 多投影仪系统集成或类似的高端可视化项目。对于常规游戏开发或非投影映射相关的需求，无需使用此插件。由于其长期无功能更新且为Beta状态，使用时需做好应对API变动的准备。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WarpUtils)
-   [官方文档]() (无)