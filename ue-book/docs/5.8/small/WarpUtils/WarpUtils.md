# Warp Utils

> PFM/MPCDI generation & visualization

| 属性 | 值 |
|---|---|
| 中文名 | 扭曲工具 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码模块） |
| 模块 | `PFMExporter` (Runtime), `WarpUtils` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2019-07-18 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WarpUtils) | |

## 用途

Warp Utils 是 Unreal Engine nDisplay 功能的底层支持插件，核心用途是生成和处理用于多屏幕投影校正的 **PFM (Portable Float Map)** 文件，以及处理 **MPCDI (Multi-Projector Common Data Interchange)** 格式数据。它解决了在虚拟摄影棚、穹顶投影、多通道渲染等复杂显示设置中，需要精确计算和存储每个投影仪像素所对应的世界空间坐标的网格数据（warp mesh）的问题。通过生成这些 PFM 网格文件，nDisplay 系统能够精确地将虚拟场景扭曲、融合并投影到物理屏幕上，实现无缝的多屏拼接效果。

## 使用场景

- **nDisplay 虚拟摄影棚搭建**：为由多个投影仪组成的环形或穹顶屏幕环境生成精确的像素映射文件。
- **多屏幕投影校准**：需要为每个投影仪计算从屏幕空间到世界空间的映射关系，以实现几何校正（warp）和边缘融合（blend）。
- **自定义投影设备集成**：将非标准的投影布局或自定义形状的投影屏幕数据导出为通用的 PFM 格式，供外部工具或硬件使用。

## 蓝图用法

该插件的主要功能通过蓝图函数库 `UWarpUtilsBlueprintLibrary` 暴露，专注于 PFM 文件的保存与生成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Save PFM` | 将预制的顶点数据（`TArray<FVector>`）保存到指定路径的 PFM 文件。 | `UWarpUtilsBlueprintLibrary` |
| `Save PFM Extended` | `Save PFM` 的扩展版本，增加了 Tiles 有效性标志数组，用于处理无效（NaN）像素。 | `UWarpUtilsBlueprintLibrary` |
| `Generate PFM` | 根据起始位置、旋转、相机参数、网格布局等参数，自动生成 PFM 文件。这是最常用的动态生成节点。 | `UWarpUtilsBlueprintLibrary` |
| `Generate PFM Extended` | `Generate PFM` 的扩展版本，同样增加了 Tiles 有效性标志数组。 | `UWarpUtilsBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **动态生成 PFM 文件**：
    在蓝图中，调用 `Generate PFM` 节点。你需要提供一个用于描述生成起始状态的 `AActor` (PFMOrigin)，设置其位置和旋转作为 `StartLocation` 和 `StartRotation`。接着配置水平和垂直方向的瓦片数量 (`TilesHorizontal`, `TilesVertical`)、每个瓦片在世界空间中的尺寸 (`TileSizeHorizontal`, `TileSizeVertical`) 以及每个瓦片对应的像素分辨率 (`TilePixelsHorizontal`, `TilePixelsVertical`)。最后指定输出文件路径 (`File`)。该节点会自动完成射线追踪和坐标计算，并将结果保存为 PFM 文件。
2.  **保存自定义顶点数据**：
    如果你已通过其他算法计算好了一组 `FVector` 数组（每个向量代表一个像素在世界空间的位置），可以直接调用 `Save PFM` 节点，并指定网格的宽高 (`TexWidth`, `TexHeight`) 和顶点数据 (`Vertices`) 进行保存。

## C++ 用法

该插件的核心功能已高度封装在蓝图函数库中，C++ 中的直接使用场景较少，主要是作为模块存在。主要的交互是通过蓝图完成的。

### 头文件引入

```cpp
// 如果你的代码需要引用该模块的类或接口，需要确保你的模块在 .Build.cs 中依赖 “WarpUtils” 模块。
// 引入蓝图库的头文件
#include "WarpUtilsBlueprintLibrary.h"
```

### 基本用法

通常在 C++ 中，你不需要直接调用这些函数，因为它们主要是为蓝图设计的。但了解其调用方式有助于调试或理解其底层逻辑。以下是模拟蓝图 `Generate PFM` 功能的等效 C++ 调用示例：

```cpp
// 假设在你的某个游戏逻辑类中
#include "WarpUtilsBlueprintLibrary.h"

void AMyActor::CreateWarpMeshData()
{
    // 参数准备
    FString OutputPath = FPaths::ProjectSavedDir() / TEXT("ExportedPFM/MyPFM.pfm");
    FVector StartLoc = GetActorLocation();
    FRotator StartRot = GetActorRotation();
    const AActor* OriginActor = this; // 当前Actor作为原点
    int32 TilesH = 8;
    int32 TilesV = 6;
    float ColumnAngle = 10.0f;
    float TileSizeH = 100.0f;
    float TileSizeV = 80.0f;
    int32 TilePixelsH = 256;
    int32 TilePixelsV = 256;
    bool bAddMargin = true;

    // 调用蓝图函数库的静态函数
    bool bSuccess = UWarpUtilsBlueprintLibrary::GeneratePFM(
        OutputPath,
        StartLoc, StartRot, OriginActor,
        TilesH, TilesV, ColumnAngle,
        TileSizeH, TileSizeV, TilePixelsH, TilePixelsV,
        bAddMargin
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("PFM file generated successfully at: %s"), *OutputPath);
    }
}
```

## Demo 示例

以下是一个最小的 Actor 示例，用于在游戏开始时自动生成一个 PFM 文件。

```cpp
// MyWarpGenerator.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyWarpGenerator.generated.h"

UCLASS()
class AMyWarpGenerator : public AActor
{
	GENERATED_BODY()
	
public:	
	AMyWarpGenerator();

protected:
	virtual void BeginPlay() override;

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Warp Settings")
    FString OutputFileName = TEXT("DefaultPFM.pfm");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Warp Settings")
    int32 TilesHorizontal = 4;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Warp Settings")
    int32 TilesVertical = 3;
};
```

```cpp
// MyWarpGenerator.cpp
#include "MyWarpGenerator.h"
#include "WarpUtilsBlueprintLibrary.h"
#include "Kismet/GameplayStatics.h"

AMyWarpGenerator::AMyWarpGenerator()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyWarpGenerator::BeginPlay()
{
    Super::BeginPlay();

    // 构造输出路径
    FString FullPath = FPaths::ProjectSavedDir() / TEXT("WarpOutput") / OutputFileName;
    
    // 准备一些默认参数
    float TileSize = 500.0f;
    int32 TileResolution = 128;
    
    // 调用蓝图库函数生成 PFM
    bool bSuccess = UWarpUtilsBlueprintLibrary::GeneratePFM(
        FullPath,
        GetActorLocation(), GetActorRotation(), this,
        TilesHorizontal, TilesVertical, 0.0f, // 列角度为0
        TileSize, TileSize,
        TileResolution, TileResolution,
        true // 添加边距
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Warning, TEXT("Warp data generated: %s"), *FullPath);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to generate warp data."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EditorFramework` | 提供编辑器框架功能，PFMExporter 模块可能用于编辑器内的数据导出。 |
| `UnrealEd` | 提供编辑器功能，PFMExporter 模块用于在编辑器环境下生成文件。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到 UE_LOGF 新格式，属于代码维护性更新。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 在进行头文件清理前补充必要的 `#include`，预防编译错误，属于预防性维护。 |
| 2025-08-29 | `32884de4` | Changing more uses of RHICreateTexture to RHICmdList.CreateTexture. | 将 RHI 纹理创建函数从旧接口迁移到基于 RHI 命令列表的新接口，属于渲染 API 适配性更新。 |
| 2025-01-21 | `42de2ffc` | Merging RHI CreateBuffer refactor to Main. | 将 RHI 缓冲区创建的重构合并到主分支，是底层图形 API 的重大调整。 |
| 2024-02-22 | `01203093` | Deprecate: | 标记了废弃，可能是某个 API 或功能。 |

### 维护评价

该插件自 2019 年创建，已运行约 7 年。虽然创建时间较长，但从 git 历史看，**最近两年内仍有持续的、实质性的更新**，主要集中在适配 Unreal Engine 渲染后端（RHI）的 API 变更和内部代码维护上（如日志宏迁移）。这表明它**仍在维护中**，以确保与最新引擎版本的兼容性。

然而，需要注意的是，该插件的 `.uplugin` 标记了 `IsBetaVersion: true` 且 `EnabledByDefault: false`，表明它**仍处于实验性/测试阶段**，并非生产就绪的核心功能。其 `Installed: false` 也进一步印证了这一点。它主要是为 `nDisplay` 这个更复杂系统提供底层支持。

**推荐使用情况**：如果你正在开发或调试 `nDisplay` 多屏投影系统，或需要生成精确的 PFM 映射网格文件，该插件是必需的底层工具。对于普通的单屏游戏开发，无需关心此插件。鉴于其 Beta 状态，在生产环境中使用时需谨慎，并做好测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WarpUtils)