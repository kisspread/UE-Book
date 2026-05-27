# Alembic Importer

> Support importing Alembic files

| 属性 | 值 |
|---|---|
| 中文名 | Alembic 导入器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AlembicImporter` (Editor), `AlembicLibrary` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-01-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter) | |

## 用途

Alembic 是影视和视觉特效行业中广泛使用的开放交换格式（`.abc` 文件），用于在不同 DCC 工具（如 Maya、3ds Max、Houdini、Blender 等）之间传递复杂的几何体和动画数据。本插件为 Unreal Engine 提供了完整的 Alembic 文件导入能力，支持将 Alembic 文件导入为三种资产类型：

- **静态网格体（StaticMesh）**：仅导入第一帧作为静态模型
- **几何体缓存（GeometryCache）**：导入完整的顶点动画序列，适用于翻书动画、流体模拟缓存等
- **骨骼网格体（SkeletalMesh）**：通过 PCA（主成分分析）压缩将逐帧顶点动画转换为形态目标（Morph Target），结合骨骼动画实现高效存储

插件的核心价值在于将 DCC 工具中制作的复杂动画数据（如角色面部表情、布料模拟、刚体碎裂等）无缝引入 Unreal Engine，同时提供了多种压缩和优化选项来平衡文件大小与动画质量。

## 使用场景

- 你在 Maya/3ds Max/Houdini 中制作了角色面部动画，需要导入 UE5 → 用 GeometryCache 或 SkeletalMesh 导入
- 你有流体模拟、布料模拟的缓存数据需要在引擎中播放 → 用 GeometryCache 导入
- 你需要将 DCC 中制作的复杂形变动画压缩为形态目标 → 用 SkeletalMesh 导入并启用 PCA 压缩
- 你从其他软件导出了带有多材质槽的模型 → 导入时自动识别 FaceSet 并映射材质槽
- 你需要保留 DCC 中的顶点速度数据用于运动模糊 → 在 GeometryCache 设置中启用 Motion Vectors 导入

## 蓝图用法

本插件主要是编辑器导入功能，不提供运行时蓝图节点。所有交互通过编辑器的文件导入对话框和导入设置面板完成。

### 导入设置

导入 `.abc` 文件时会弹出设置对话框，所有设置均可在蓝图类 `UAbcImportSettings` 中访问：

| 设置项 | 说明 | 所在结构体 |
|---|---|---|
| `ImportType` | 导入类型：StaticMesh / GeometryCache / Skeletal | `UAbcImportSettings` |
| `SamplingSettings` | 帧采样设置（逐帧/每N帧/每N秒） | `FAbcSamplingSettings` |
| `CompressionSettings` | PCA 压缩设置（百分比/固定基数/不压缩） | `FAbcCompressionSettings` |
| `NormalGenerationSettings` | 法线生成设置（硬边角度阈值、平滑组） | `FAbcNormalGenerationSettings` |
| `MaterialSettings` | 材质设置（自动创建/查找材质） | `FAbcMaterialSettings` |
| `StaticMeshSettings` | 静态网格体设置（合并网格、光照图UV） | `FAbcStaticMeshSettings` |
| `GeometryCacheSettings` | 几何体缓存设置（展平轨道、运动向量） | `FAbcGeometryCacheSettings` |
| `ConversionSettings` | 坐标转换预设（Maya/3ds Max/自定义） | `FAbcConversionSettings` |

### 使用示例（导入流程）

1. 在内容浏览器中右键 → **Import** → 选择 `.abc` 文件
2. 在弹出的 **Alembic Import Options** 对话框中选择导入类型
3. 根据导入类型调整对应设置（采样、压缩、法线等）
4. 点击 **Import** 完成导入
5. 导入后可在资产的 **Import Settings** 面板中修改设置并重新导入

## C++ 用法

### 头文件引入

```cpp
#include "AbcImporter.h"
#include "AbcImportSettings.h"
#include "AbcFile.h"
```

### 基本用法

使用 `FAbcImporter` 打开 Alembic 文件并导入为不同类型的资产：

```cpp
#include "AbcImporter.h"
#include "AbcImportSettings.h"

// 创建导入器实例
FAbcImporter Importer;

// 打开 Alembic 文件
const FString FilePath = TEXT("/Game/Assets/character_anim.abc");
const EAbcImportError OpenResult = Importer.OpenAbcFileForImport(FilePath);

if (OpenResult == AbcImportError_NoError)
{
    // 获取导入设置
    UAbcImportSettings* Settings = UAbcImportSettings::Get();
    Settings->ImportType = EAlembicImportType::GeometryCache;
    Settings->SamplingSettings.SamplingType = EAlembicSamplingType::PerFrame;

    // 导入轨道数据
    const EAbcImportError ImportResult = Importer.ImportTrackData(4, Settings);

    if (ImportResult == AbcImportError_NoError)
    {
        // 导入为 GeometryCache
        UObject* Parent = GetTransientPackage();
        UGeometryCache* GeometryCache = Importer.ImportAsGeometryCache(Parent, RF_NoFlags);
    }
}
```

*来源：`Public/AbcImporter.h`*

### 进阶用法

直接使用底层 `FAbcFile` API 进行帧级控制和并发读取：

```cpp
#include "AbcFile.h"
#include "AbcImportSettings.h"
#include "AbcUtilities.h"

// 创建并打开 AbcFile
FAbcFile AbcFile(TEXT("/path/to/animation.abc"));
EAbcImportError Error = AbcFile.Open();

if (Error == AbcImportError_NoError)
{
    // 配置导入设置
    UAbcImportSettings* Settings = UAbcImportSettings::Get();
    Settings->ImportType = EAlembicImportType::GeometryCache;
    AbcFile.Import(Settings);

    // 获取帧范围信息
    const int32 StartFrame = AbcFile.GetStartFrameIndex();
    const int32 EndFrame = AbcFile.GetEndFrameIndex();
    const float SecondsPerFrame = AbcFile.GetSecondsPerFrame();

    // 并发处理帧数据（最多 8 个并发读取）
    AbcFile.ProcessFrames(
        [](int32 FrameIndex, FAbcFile* File)
        {
            // 每帧的回调处理
        },
        EFrameReadFlags::PositionAndNormalOnly,
        nullptr // 可选的 SlowTask 用于显示进度
    );

    // 或者手动读取单帧数据
    AbcFile.ReadFrame(StartFrame, EFrameReadFlags::None, 0 /*并发索引*/);

    FGeometryCacheMeshData MeshData;
    FAbcUtilities::GetFrameMeshData(AbcFile, StartFrame, MeshData, 0);

    // 清理帧数据
    AbcFile.CleanupFrameData(0);
}
```

*来源：`Public/AbcFile.h`、`Public/AbcUtilities.h`*

## Demo 示例

以下示例展示如何通过 C++ 代码以编程方式导入 Alembic 文件为几何体缓存：

```cpp
// AbcImportDemo.h
#pragma once

#include "CoreMinimal.h"

class UGeometryCache;

class FAbcImportDemo
{
public:
    /** 将指定的 Alembic 文件导入为 GeometryCache */
    static UGeometryCache* ImportAlembicAsGeometryCache(const FString& AbcFilePath, UObject* InParent);
};
```

```cpp
// AbcImportDemo.cpp
#include "AbcImportDemo.h"
#include "AbcImporter.h"
#include "AbcImportSettings.h"
#include "GeometryCache.h"

UGeometryCache* FAbcImportDemo::ImportAlembicAsGeometryCache(const FString& AbcFilePath, UObject* InParent)
{
    // 1. 创建导入器并打开文件
    FAbcImporter Importer;
    const EAbcImportError OpenError = Importer.OpenAbcFileForImport(AbcFilePath);
    if (OpenError != AbcImportError_NoError)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open Alembic file: %s"), *AbcFilePath);
        return nullptr;
    }

    // 2. 配置导入参数
    UAbcImportSettings* Settings = UAbcImportSettings::Get();
    Settings->ImportType = EAlembicImportType::GeometryCache;
    Settings->SamplingSettings.SamplingType = EAlembicSamplingType::PerFrame;
    Settings->SamplingSettings.FrameSteps = 1;
    Settings->ConversionSettings.Preset = EAbcConversionPreset::Maya;
    Settings->GeometryCacheSettings.bFlattenTracks = true;
    Settings->GeometryCacheSettings.MotionVectors = EAbcGeometryCacheMotionVectorsImport::NoMotionVectors;

    // 3. 导入轨道数据
    const EAbcImportError ImportError = Importer.ImportTrackData(4, Settings);
    if (ImportError != AbcImportError_NoError)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to import track data from: %s"), *AbcFilePath);
        return nullptr;
    }

    // 4. 执行导入
    UGeometryCache* GeometryCache = Importer.ImportAsGeometryCache(InParent, RF_NoFlags);
    if (GeometryCache)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully imported GeometryCache from: %s"), *AbcFilePath);
    }

    return GeometryCache;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryCache` | 几何体缓存资产类型，Alembic 动画数据的目标存储格式 |
| `MeshDescription` | 网格体描述数据结构，用于构建静态网格体 |
| `Eigen`（第三方） | 线性代数库，用于 PCA/SVD 压缩算法 |
| `Alembic`（第三方） | Alembic SDK，用于解析 `.abc` 文件格式 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 将 UE_LOG 迁移到新的 UE_LOGF 宏 |
| 2026-02-27 | `8ce7ca27` | AlembicImporter: Fixed import failure when it couldn't retrieve velocities even though those should | 修复无法获取顶点速度时导致导入失败的问题 |
| 2026-02-25 | `74e86b93` | Alembic Import: Fixed out of bounds access (potentially due to negative times) | 修复因负时间值导致的数组越界访问 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复不可达代码错误 |

### 维护评价

**活跃维护**。该插件从 2022 年初由 Experimental 迁移到正式版，近年来持续有实质性更新，包括：

- 2026 年 2-4 月间连续修复了多个导入稳定性问题（顶点速度获取失败、负时间越界、格式说明符等）
- 正在进行代码现代化工作（UE_LOG → UE_LOGF 迁移）
- 修复了跨平台编译问题

作为引擎默认启用的核心导入插件，维护状态良好。建议使用最新引擎版本以获得最稳定的导入体验。已知限制包括：导入大型 Alembic 文件时可能消耗较多内存和时间，PCA 压缩对拓扑变化的网格体不适用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/)