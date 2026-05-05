# Warp Utils

> PFM/MPCDI generation & visualization

| 属性 | 值 |
|---|---|
| 分类 | Misc |
| 默认启用 | ❌ `EnabledByDefault: false` |
| 包含内容 | ✅ `CanContainContent: true` |
| 模块 | PFMExporter (Runtime, Win64 only), WarpUtils (Runtime) |
| 创建时间 | 2019-07-18 |
| 年龄标签 | 👴 老古董（约7年） |
| Beta 版本 | ⚠️ `IsBetaVersion: true` |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/WarpUtils) | |

## 用途

WarpUtils 用于生成和导出 **PFM（Portable Float Map）** 文件，服务于 nDisplay 多投影仪系统的几何校正（warp）和色彩校正（blend）流程。

PFM 文件存储的是每个像素对应的 3D 世界坐标（XYZ float），投影系统读取后可以将画面精确地投射到不规则的屏幕表面（如弧幕、CAVE 系统）。Plugin 提供两种 PFM 生成方式：

1. **基于数学计算**（WarpUtils 模块）：根据瓦片网格参数（行列数、角度、尺寸）直接计算 3D 坐标并写入 PFM
2. **基于 GPU 渲染**（PFMExporter 模块）：将 Static Mesh 的 UV 映射通过 GPU shader 转换为 PFM 坐标

Plugin 的 `IsBetaVersion: true` 且 `EnabledByDefault: false`，属于 Epic 内部/实验性工具。

## 使用场景

- 你正在搭建 **nDisplay 多屏投影系统**（CAVE、弧幕、LED 墙）→ 需要 PFM 文件来描述每个投影仪的几何映射
- 你有一个 **3D 建模的屏幕几何体**（Static Mesh），想把它的 UV 导出为 PFM → 用 `ExportPFM`
- 你需要按网格参数 **程序化生成 PFM**（例如多列弧幕投影）→ 用 `GeneratePFM`
- 你有自定义的顶点数据，想直接 **写入 PFM 文件** → 用 `SavePFM`

## 蓝图用法

Plugin 提供两个蓝图函数库，节点按功能分组如下：

### PFM 保存与生成（WarpUtilsBlueprintLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Save PFM` | 将顶点数组保存为 PFM 文件。NaN 坐标表示无效像素 | `UWarpUtilsBlueprintLibrary` |
| `Save PFM Extended` | 同上，额外接受布尔有效性标记数组（false → 写入 NaN） | `UWarpUtilsBlueprintLibrary` |
| `Generate PFM` | 根据瓦片网格参数程序化生成 PFM 文件 | `UWarpUtilsBlueprintLibrary` |
| `Generate PFM Extended` | 同上，额外支持每个瓦片的有效性标记 | `UWarpUtilsBlueprintLibrary` |

### Mesh 导出（PFMExporter）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PFMExporter Module API` | 获取 PFMExporter 模块接口引用 | `UPFMExporterBlueprintLib` |
| `Export Static Mesh to PFM file` | 将 StaticMesh 的 UV 通道导出为 PFM 文件 | `IPFMExporterBlueprintAPI` |

### 使用示例

**场景 A：程序化生成弧幕 PFM**

1. 在关卡中放置一个 Actor 作为 PFM Origin（投影原点）
2. 添加 BeginPlay 事件
3. 连接 `Generate PFM` 节点：
   - File: 输出路径，如 `D:\pfm\my_warp.pfm`
   - StartLocation/StartRotation: 起始位置和朝向
   - PFMOrigin: 关卡中放置的原点 Actor 引用
   - TilesHorizontal/TilesVertical: 列数/行数（如 5 列 × 1 行）
   - ColumnAngle: 每列之间的夹角（如 30.0 度）
   - TileSize: 每个瓦片的物理尺寸
   - TilePixels: 每个瓦片的像素分辨率
   - AddMargin: 是否在像素边缘添加半像素边距

**场景 B：从 Static Mesh 导出 PFM**

1. 在关卡中放置 Static Mesh（已配置好 UV 映射，UV 0-1 范围代表屏幕表面）
2. 可选放置一个 SceneComponent 作为投影原点
3. 调用 `PFMExporter Module API` 获取接口引用
4. 调用 `Export Static Mesh to PFM file`：
   - SrcMesh: StaticMeshComponent 引用
   - Origin: 原点组件（留空则使用 Mesh 的父组件）
   - Width/Height: 输出 PFM 分辨率
   - FileName: 输出文件路径

## C++ 用法

### 头文件引入

```cpp
// WarpUtils 模块 - PFM 保存/生成
#include "Blueprints/WarpUtilsBlueprintLibrary.h"

// PFMExporter 模块 - Mesh 导出
#include "IPFMExporter.h"
#include "Blueprints/IPFMExporterBlueprintAPI.h"
```

### 基本用法：保存 PFM 文件

```cpp
// 将顶点数据保存为 PFM
TArray<FVector> Vertices;
// ... 填充顶点数据，数量必须 == Width * Height
// 坐标为投影原点空间下的 3D 位置
// 使用 FVector(NAN, NAN, NAN) 标记无效像素

FString FilePath = TEXT("D:/pfm/output.pfm");
int Width = 1920;
int Height = 1080;

bool bSuccess = UWarpUtilsBlueprintLibrary::SavePFM(FilePath, Width, Height, Vertices);
```

> 来源: `WarpUtilsBlueprintLibrary.cpp` — `SavePFM()`

### 基本用法：从 Static Mesh 导出 PFM

```cpp
// 通过模块接口直接导出（C++ 层面）
if (IPFMExporter::IsAvailable())
{
    UStaticMesh* Mesh = MyMeshComponent->GetStaticMesh();
    FMatrix MeshToOrigin = /* 计算 mesh 到原点的变换矩阵 */;
    
    IPFMExporter::Get().ExportPFM(
        &Mesh->GetLODForExport(0),
        MeshToOrigin,
        1920, 1080,
        TEXT("D:/pfm/mesh_export.pfm")
    );
}
```

> 来源: `PFMExporterModule.cpp` — `FPFMExporterModule::ExportPFM()`

### 进阶用法：带有效性标记的 PFM 生成

```cpp
// 标记部分瓦片为无效（例如投影重叠区域不需要的区域）
TArray<bool> TileFlags;
TileFlags.SetNum(5);  // 5 个瓦片
TileFlags[0] = true;
TileFlags[1] = true;
TileFlags[2] = false;  // 这个瓦片输出 NaN
TileFlags[3] = true;
TileFlags[4] = true;

UWarpUtilsBlueprintLibrary::GeneratePFMEx(
    TEXT("D:/pfm/cave_warp.pfm"),
    FVector::ZeroVector,                    // 起始位置
    FRotator::ZeroRotator,                  // 起始旋转
    MyOriginActor,                          // PFM 原点
    5, 1,                                   // 5列1行
    30.0f,                                  // 每列夹角 30°
    200.0f, 150.0f,                         // 瓦片物理尺寸 (cm)
    512, 384,                               // 瓦片像素分辨率
    true,                                   // 添加半像素边距
    TileFlags                               // 瓦片有效性标记
);
```

> 来源: `WarpUtilsBlueprintLibrary.cpp` — `GeneratePFMEx()`

## Demo 示例

### 最小可编译示例：运行时生成 PFM

```cpp
// MyPFMGenerator.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyPFMGenerator.generated.h"

UCLASS()
class AMyPFMGenerator : public AActor
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category = "PFM")
    AActor* PFMOrigin;

    UPROPERTY(EditAnywhere, Category = "PFM")
    FString OutputPath = TEXT("D:/pfm/warp.pfm");

    UFUNCTION(BlueprintCallable, Category = "PFM")
    void GenerateWarpPFM()
    {
        // 3列弧幕，每列 45° 角
        TArray<bool> Flags = { true, true, true };
        
        bool bOK = UWarpUtilsBlueprintLibrary::GeneratePFMEx(
            OutputPath,
            FVector::ZeroVector,
            FRotator::ZeroRotator,
            PFMOrigin,
            3, 1,           // 3 列, 1 行
            45.0f,          // 列间夹角
            300.f, 200.f,   // 瓦片尺寸 (cm)
            1024, 768,      // 像素分辨率
            false,          // 无边距
            Flags
        );

        UE_LOG(LogTemp, Log, TEXT("PFM generation: %s"), bOK ? TEXT("Success") : TEXT("Failed"));
    }
};
```

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "WarpUtils"    // 使用 WarpUtils 蓝图库
});

// 如果需要使用 PFMExporter（Mesh 导出功能）
PrivateDependencyModuleNames.Add("PFMExporter");
```

**注意：** PFMExporter 模块仅支持 Win64 平台（`PlatformAllowList: ["Win64"]`），因为它依赖 GPU RHI 渲染管线读取 Static Mesh 数据。

## 模块依赖

### WarpUtils 模块（你的模块需要依赖的）

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础库 |
| `CoreUObject` | UObject 系统（私有依赖） |
| `Engine` | Actor/Component 系统（私有依赖） |

### PFMExporter 模块（你的模块需要依赖的）

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | StaticMesh / LOD 资源访问 |
| `RenderCore` | 渲染核心（私有依赖） |
| `RHI` | RHI 纹理/Buffer 操作（私有依赖） |
| `Projects` | 插件路径查找（私有依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-08-29 | `32884de` | Changing more uses of RHICreateTexture to RHICmdList.CreateTexture | RHI API 迁移，将旧的全局纹理创建函数改为 CommandList 方式，无功能变化 |
| 2025-01-21 | `42de2ff` | Merging RHI CreateBuffer refactor to Main | RHI Buffer 创建方式重构为 FRHIBufferInitializer，大规模引擎级重构，无功能变化 |
| 2024-02-22 | `0120309` | Deprecate FRHITexture2D/3D/Cube 系列 | 引擎级 RHI 纹理类型废弃标记，影响 PFMExporter 的纹理创建代码 |

### 维护评价

- **年龄**：约 7 年（2019 年创建）
- **Beta 状态**：`IsBetaVersion: true`，10 年来从未毕业为正式版
- **更新模式**：最近 3 次更新全部是引擎级 RHI API 迁移适配，非功能性更新。Plugin 本身的功能代码自创建后基本没有变化
- **平台限制**：PFMExporter 仅限 Win64，表明这是一个面向特定硬件环境的工具
- **测试用例**：未找到任何测试文件
- **文档**：`.uplugin` 的 `DocsURL` 为空，无官方文档

⚠️ **警告**：该 Plugin 超过 5 年没有实质性功能更新。最近的改动仅为适配引擎 RHI API 变化，不涉及新功能或 Bug 修复。它属于 nDisplay 投影校正的专用工具，仅在搭建 CAVE/弧幕投影系统时才有用。

**建议**：如果你的项目确实需要 PFM 文件用于投影校正，可以使用，但需注意它是 Beta 状态且仅支持 Win64。对于新的 nDisplay 项目，建议检查 Epic 是否提供了更新的替代方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/WarpUtils)
- [官方文档](https://docs.unrealengine.com/)（无专用文档，参考 nDisplay 相关文档）
- [nDisplay 文档](https://docs.unrealengine.com/en-US/ProductionPipelines/ProductionPipelines/VirtualProduction/nDisplay/)
