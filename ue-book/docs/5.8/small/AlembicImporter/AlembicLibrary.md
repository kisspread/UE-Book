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

Alembic Importer 插件用于将 Alembic (.abc) 格式的 3D 动画和几何数据导入到 Unreal Engine 中。Alembic 是一种开放的、行业标准的计算机图形数据交换格式，广泛应用于影视特效和游戏开发中，用于在不同的 DCC（数字内容创建）软件之间交换复杂的动画网格、几何缓存和骨骼网格。

这个插件的核心价值在于它不仅仅是一个简单的文件加载器，而是一个强大的数据处理管道。它能够处理来自 Maya、3ds Max 等 DCC 工具导出的、包含复杂拓扑变化、变形动画和精确时间信息的 Alembic 文件，并将其转换为 UE5 中可用的静态网格体（Static Mesh）、几何缓存（Geometry Cache）或包含变形目标（Morph Targets）的骨骼网格体（Skeletal Mesh）。它解决了在专业动画/特效制作流程与实时游戏引擎之间进行高效、高保真度资产导入的关键问题。

## 使用场景

-   **影视级角色或生物动画导入**：你从 Maya 中导出了一个带有复杂面部动画和布料模拟的角色 Alembic 序列 → 使用此插件将其作为几何缓存或带有变形目标的骨骼网格体导入，保留原始动画细节。
-   **复杂的特效序列**：你有一个使用 Houdini 或 Bifrost 制作的流体、粒子或刚体破碎模拟的 Alembic 序列 → 导入为几何缓存，以在游戏或实时项目中播放。
-   **需要高精度几何缓存的场景**：你需要一个精确记录顶点位置随时间变化的序列（如可变形的物理对象）→ 将其导入为几何缓存资产。
-   **DCC 工具与 UE5 的动画协作**：动画师在 DCC 软件中完成动画后，可以通过导出 Alembic 文件并使用此插件，将动画无缝地带入 UE5 环境中进行预览、光照设置或进一步开发。

## 蓝图用法

此插件主要作为编辑器导入功能存在，其核心设置（`UAbcImportSettings` 及其子结构体）定义了丰富的参数，这些参数通常在编辑器导入对话框中设置。蓝图可以通过这些数据结构来预配置或修改导入行为。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UAbcImportSettings::Get()` | 获取 Alembic 导入设置的单例实例 | `UAbcImportSettings` |
| `ImportType` (属性) | 获取或设置导入类型（静态网格、几何缓存、骨骼） | `UAbcImportSettings` |
| `SamplingSettings` (属性) | 获取或设置动画采样相关配置 | `UAbcImportSettings` |
| `CompressionSettings` (属性) | 获取或设置骨骼网格体导入的压缩（PCA）配置 | `UAbcImportSettings` |
| `GeometryCacheSettings` (属性) | 获取或设置几何缓存特定的配置 | `UAbcImportSettings` |
| `ConversionSettings` (属性) | 获取或设置坐标系转换预设（如 Maya、3ds Max） | `UAbcImportSettings` |

### 使用示例（蓝图描述）

虽然通常不通过蓝图节点直接导入，但你可以通过蓝图获取并修改 `UAbcImportSettings` 的实例，以实现自动化导入流程。例如：
1.  使用 `UAbcImportSettings::Get()` 节点获取设置实例。
2.  使用 `Set Members in AbcImportSettings` 节点，将 `ImportType` 设置为 `GeometryCache`。
3.  通过访问 `GeometryCacheSettings` 子属性，设置 `bFlattenTracks` 和 `MotionVectors` 等参数。
4.  最终，这些配置好的设置对象可以被传递给底层的 C++ 导入函数。

## C++ 用法

### 头文件引入

```cpp
#include "AbcImporter.h"
#include "AbcImportSettings.h"
```

### 基本用法

以下示例展示了如何在 C++ 中使用 `FAbcImporter` 来导入一个 Alembic 文件。这模拟了编辑器内部调用的过程。
（来源：基于 `Public/AbcImporter.h` 中的 API 设计）

```cpp
#include "AbcImporter.h"
#include "AbcImportSettings.h"
#include "GeometryCache/GeometryCache.h"
#include "UObject/SavePackage.h"

void ImportAlembicFileAsGeometryCache()
{
    // 1. 创建导入器实例
    FAbcImporter Importer;

    // 2. 打开并解析 Alembic 文件，获取基础信息
    const FString AbcFilePath = TEXT("/Game/Assets/MyAnimation.abc");
    EAbcImportError OpenError = Importer.OpenAbcFileForImport(AbcFilePath);
    if (OpenError != AbcImportError_NoError)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open Alembic file: %s"), *AbcFilePath);
        return;
    }

    // 3. 获取或配置导入设置 (这里假设使用默认设置)
    UAbcImportSettings* ImportSettings = UAbcImportSettings::Get();
    // 例如，确保是几何缓存模式
    ImportSettings->ImportType = EAlembicImportType::GeometryCache;

    // 4. 导入轨道数据（动画采样，多线程处理）
    const int32 NumThreads = FPlatformMisc::NumberOfCores();
    EAbcImportError ImportError = Importer.ImportTrackData(NumThreads, ImportSettings);
    if (ImportError != AbcImportError_NoError)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to import track data from Alembic file."));
        return;
    }

    // 5. 将数据导入为 UGeometryCache 资产
    // 假设我们有一个包用于保存资产
    UPackage* Package = CreatePackage(*TEXT("/Game/MyImportedGeometryCache"));
    UGeometryCache* GeometryCache = Importer.ImportAsGeometryCache(Package, RF_Public | RF_Standalone);
    if (GeometryCache)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully imported GeometryCache: %s"), *GeometryCache->GetName());
        // 6. 标记包为已修改并保存（可选）
        Package->MarkPackageDirty();
        FSavePackageArgs SaveArgs;
        SaveArgs.TopLevelFlags = EObjectFlags::RF_Public | EObjectFlags::RF_Standalone;
        UPackage::SavePackage(Package, GeometryCache, *FPackageName::LongPackageNameToFilename(Package->GetName(), FPackageName::GetAssetPackageExtension()), SaveArgs);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create GeometryCache from Alembic file."));
    }
}
```

### 进阶用法

`FAbcFile` 类提供了更底层的控制，例如逐帧读取和处理。
（来源：基于 `Public/AbcFile.h` 的 API 设计）

```cpp
#include "AbcFile.h"
#include "GeometryCache/GeometryCacheMeshData.h"

void ProcessAbcFrameByFrame()
{
    FAbcFile AbcFile(TEXT("/Game/Assets/ComplexSimulation.abc"));
    if (AbcFile.Open() != AbcImportError_NoError) return;

    // 使用自定义设置导入（可选）
    UAbcImportSettings* Settings = UAbcImportSettings::Get();
    Settings->SamplingSettings.SamplingType = EAlembicSamplingType::PerXFrames;
    Settings->SamplingSettings.FrameSteps = 2; // 每隔一帧采样
    AbcFile.Import(Settings);

    // 遍历帧并处理数据
    const int32 StartFrame = AbcFile.GetStartFrameIndex();
    const int32 EndFrame = AbcFile.GetEndFrameIndex();

    // 使用回调函数进行多线程帧处理
    AbcFile.ProcessFrames([](int32 FrameIndex, FAbcFile* InAbcFile)
    {
        FGeometryCacheMeshData FrameMeshData;
        // 使用并发读取索引 (ReadIndex) 0
        FAbcUtilities::GetFrameMeshData(*InAbcFile, FrameIndex, FrameMeshData, 0);
        // ... 在此处处理每一帧的 MeshData
    }, EFrameReadFlags::None);

    // 获取整个动画序列的边界信息
    const FBoxSphereBounds& TotalBounds = AbcFile.GetArchiveBounds();
    UE_LOG(LogTemp, Log, TEXT("Animation bounds: %s"), *TotalBounds.ToString());
}
```

## Demo 示例

以下是一个简单的命令行工具 (Commandlet) 示例，演示了如何使用 Alembic Importer API 进行基本导入。此代码模拟了 `Private/AlembicTestCommandlet.h` 中测试命令的部分逻辑。

**MyAlembicImportCommandlet.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "MyAlembicImportCommandlet.generated.h"

UCLASS()
class UMyAlembicImportCommandlet : public UCommandlet
{
    GENERATED_BODY()

public:
    virtual int32 Main(const FString& Params) override;
};
```

**MyAlembicImportCommandlet.cpp**
```cpp
#include "MyAlembicImportCommandlet.h"
#include "AbcImporter.h"
#include "AbcImportSettings.h"
#include "Misc/PackageName.h"
#include "UObject/SavePackage.h"

int32 UMyAlembicImportCommandlet::Main(const FString& Params)
{
    // 解析命令行参数获取 .abc 文件路径
    TArray<FString> Tokens;
    TArray<FString> Switches;
    ParseCommandLine(*Params, Tokens, Switches);
    if (Tokens.Num() == 0)
    {
        UE_LOG(LogTemp, Error, TEXT("Usage: MyAlembicImportCommandlet <path_to_abc_file>"));
        return 1;
    }
    const FString AbcFilePath = Tokens[0];

    // 创建导入器并打开文件
    FAbcImporter Importer;
    EAbcImportError Error = Importer.OpenAbcFileForImport(AbcFilePath);
    if (Error != AbcImportError_NoError)
    {
        UE_LOG(LogTemp, Error, TEXT("Error opening ABC file: %d"), static_cast<int32>(Error));
        return 1;
    }

    // 使用默认设置导入轨道数据
    UAbcImportSettings* Settings = UAbcImportSettings::Get();
    Settings->ImportType = EAlembicImportType::GeometryCache; // 设置为几何缓存
    Error = Importer.ImportTrackData(FPlatformMisc::NumberOfCores(), Settings);
    if (Error != AbcImportError_NoError)
    {
        UE_LOG(LogTemp, Error, TEXT("Error importing track data: %d"), static_cast<int32>(Error));
        return 1;
    }

    // 创建包并导入资产
    FString BaseName = FPaths::GetBaseFilename(AbcFilePath);
    FString PackageName = FPaths::Combine(TEXT("/Game/Imported"), BaseName);
    UPackage* Package = CreatePackage(*PackageName);

    // 根据设置的导入类型执行导入
    TArray<UObject*> ImportedObjects;
    switch (Settings->ImportType)
    {
    case EAlembicImportType::StaticMesh:
        ImportedObjects = Importer.ImportAsStaticMesh(Package, RF_Public | RF_Standalone);
        break;
    case EAlembicImportType::GeometryCache:
        if (UGeometryCache* Cache = Importer.ImportAsGeometryCache(Package, RF_Public | RF_Standalone))
        {
            ImportedObjects.Add(Cache);
        }
        break;
    case EAlembicImportType::Skeletal:
        ImportedObjects = Importer.ImportAsSkeletalMesh(Package, RF_Public | RF_Standalone);
        break;
    }

    if (ImportedObjects.Num() > 0)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully imported %d asset(s) from: %s"), ImportedObjects.Num(), *AbcFilePath);
        // 保存包
        FSavePackageArgs SaveArgs;
        SaveArgs.TopLevelFlags = RF_Public | RF_Standalone;
        UPackage::SavePackage(Package, nullptr, *FPackageName::LongPackageNameToFilename(PackageName, FPackageName::GetAssetPackageExtension()), SaveArgs);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No assets were imported from: %s"), *AbcFilePath);
    }

    return 0;
}
```

## 模块依赖

要在你的项目或插件中使用 AlembicImporter 的 C++ API，你需要链接 `AlembicLibrary` 模块。

| 模块 | 用途 |
|---|---|
| `AlembicLibrary` | Alembic Importer 的核心运行时库，包含文件解析、数据转换和导入逻辑 |
| `MeshUtilities` | 用于法线、切线计算等网格工具函数 |
| `SkeletalMesh` | 用于骨骼网格体的构建和相关数据结构 |

*注：`GeometryCache` 模块是插件的依赖项，但其本身也是一个独立的运行时插件。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了32位与64位格式化说明符不匹配的编译器警告/错误。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将过时的 UE_LOG 宏迁移到新的 UE_LOGF 宏。 |
| 2026-02-27 | `8ce7ca27` | AlembicImporter: Fixed import failure when it couldn't retrieve velocities even though those should | 修复了在应该能读取速度但失败时导致的导入错误。 |
| 2026-02-25 | `74e86b93` | Alembic Import: Fixed out of bounds access (potentially due to negative times). | 修复了潜在的由负时间值引起的数组越界访问问题。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复了不可达代码的错误。 |

### 维护评价

Alembic Importer 是一个**处于活跃维护状态**的插件。
- **年龄**：创建于 2022 年，属于相对较新的插件。
- **更新频率**：从提交历史看，在 2026 年仍有规律的功能性修复和改进，特别是针对编译器兼容性、稳定性和错误处理。
- **维护内容**：近期更新集中在修复 bug、提升代码健壮性和适配引擎 API 的演进（如日志宏迁移），表明开发团队仍在关注其质量。
- **依赖**：它依赖于外部的 Alembic 库，但 Epic Games 将其从实验版正式发布，说明其稳定性已得到认可。
- **推荐**：对于需要导入 Alembic 格式动画资产的工作流程，此插件是官方提供的标准且可靠的解决方案，推荐使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter/Source/AlembicLibrary/Private/AlembicTestCommandlet.h) (注意：此为 Commandlet 测试，非标准单元测试)