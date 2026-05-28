# Alembic Importer

> Support importing Alembic files

| 属性 | 值 |
|---|---|
| 中文名 | ABC导入器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AlembicImporter` (Editor), `AlembicLibrary` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-01-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter) | |

## 用途

AlembicImporter 插件的核心功能是将来自DCC软件（如 Autodesk Maya、3ds Max、Houdini 等）导出的 Alembic (`.abc`) 格式文件导入到 Unreal Engine 5 中。它不仅仅是一个简单的模型导入器，而是专注于处理复杂的、随时间变化的 3D 数据。

**它解决的主要问题包括：**
1.  **复杂动画导入**：处理顶点动画（如布料、流体、角色变形）、矩阵动画（刚体变换序列）和拓扑变化的网格。
2.  **高效压缩与存储**：使用主成分分析（PCA/SVD）技术压缩动画数据，将其转换为骨骼网格的变形目标（Morph Targets）序列，以实现高效存储和播放。
3.  **标准化工作流**：为从各种 DCC 软件导入动画资产提供了一个统一的、可配置的接口，处理了不同软件间的坐标系、缩放和法线计算差异。
4.  **几何缓存创建**：能够直接将 Alembic 动画数据导入为引擎的 `GeometryCache` 资产，适用于高质量、轻量级的流式播放。

其存在意义在于弥补了标准 FBX 导入器在处理大量动态顶点数据时的局限性，为影视、广告和游戏开发中的复杂特效与动画提供了关键的支持管道。

## 使用场景

-   **角色动画**：从 Maya 导出使用蒙皮和变形器制作的角色表情动画，导入为包含变形目标的骨骼网格。
-   **特效序列**：将 Houdini 生成的爆炸、烟雾等粒子流体模拟结果（为网格序列）导入引擎，使用几何缓存进行播放。
-   **刚体模拟**：导入来自模拟软件（如 Bullet, PhysX）的复杂刚体动态结果。
-   **建筑可视化**：导入包含复杂构件动画（如开合的门窗、移动的家具）的场景。
-   **自定义工具链**：当标准的 FBX 流程无法满足项目对拓扑变化或超大数据量的需求时。

## 蓝图用法

此插件的蓝图交互主要集中在导入配置上，核心的导入执行过程通常在编辑器导入对话框或 C++ 中完成。

### 核心配置节点

由于导入设置 `UAbcImportSettings` 及其包含的子结构体（如 `FAbcCompressionSettings`, `FAbcGeometryCacheSettings`）是 `BlueprintReadWrite` 的，蓝图主要用于在导入前**动态生成或修改**这些配置对象。但请注意，直接触发导入的函数 `FAbcImporter::ImportAsXxx` 并非蓝图可调用，它们是编辑器导入流程的一部分。

| 节点/类 | 说明 | 用法 |
|---|---|---|
| `UAbcImportSettings` | ABC导入的总配置对象 | 在蓝图中创建实例，并设置其属性以自定义导入行为。 |
| `EAlembicImportType` | 枚举，指定导入类型 | 设置为 `StaticMesh`, `GeometryCache` 或 `Skeletal`。 |
| `FAbcCompressionSettings` | 控制骨骼网格动画的PCA压缩 | 设置压缩基准计算方式、百分比或固定数量。 |
| `FAbcGeometryCacheSettings` | 几何缓存专用设置 | 控制是否合并轨迹、运动向量导入、压缩精度等。 |
| `FAbcSamplingSettings` | 动画采样设置 | 控制按帧、按时间步长或每X帧采样，以及起止帧范围。 |

### 使用示例（蓝图描述）

1.  **动态生成导入配置**：
    - 创建一个 `Make Literal AbcImportSettings` 节点。
    - 通过该节点的输出引脚，连接到一系列 `Set Xxx Settings` 节点，修改 `ImportType`、`CompressionSettings.PercentageOfTotalBases` 等属性。
    - 最终将配置好的 `UAbcImportSettings` 对象传递给其他工具或存储。

2.  **在编辑器工具中使用**：
    - 蓝图编辑器工具（Editor Utility Widget 或 Editor Utility Blueprint）可以使用此插件的配置类来构建自定义的导入UI。
    - 例如，创建一个下拉菜单选择 `EAlembicImportType`，并根据选择隐藏或显示不同的配置面板。

## C++ 用法

### 头文件引入

```cpp
#include "AbcImporter.h" // 核心导入器类
#include "AbcImportSettings.h" // 导入设置
#include "AbcFile.h" // ABC文件处理类
```

### 基本用法

以下代码展示了如何编程式地打开一个 Alembic 文件并将其导入为几何缓存资产。

```cpp
// 来源于 AbcImporter.h 和实际编辑器导入逻辑
#include "AbcImporter.h"
#include "AbcImportSettings.h"
#include "AbcFile.h"
#include "GeometryCache/GeometryCache.h"

void ImportAbcAsGeometryCache(const FString& FilePath, UObject* Parent)
{
    // 1. 创建导入器实例
    FAbcImporter AbcImporter;

    // 2. 打开 ABC 文件进行预处理（读取元数据、帧范围等）
    EAbcImportError OpenError = AbcImporter.OpenAbcFileForImport(FilePath);
    if (OpenError != AbcImportError_NoError)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open ABC file: %s"), *FilePath);
        return;
    }

    // 3. 配置导入设置（通常从用户界面获取）
    UAbcImportSettings* Settings = NewObject<UAbcImportSettings>();
    Settings->ImportType = EAlembicImportType::GeometryCache;
    Settings->GeometryCacheSettings.bFlattenTracks = true; // 合并为单条轨迹
    Settings->GeometryCacheSettings.MotionVectors = EAbcGeometryCacheMotionVectorsImport::ImportAbcVelocitiesAsMotionVectors;
    Settings->ConversionSettings.Preset = EAbcConversionPreset::Maya; // 设置坐标系预设

    // 4. 导入轨道数据（读取并处理动画帧）
    int32 NumThreads = FTaskGraphInterface::Get().GetNumWorkerThreads();
    EAbcImportError ImportError = AbcImporter.ImportTrackData(NumThreads, Settings);
    if (ImportError != AbcImportError_NoError)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to import track data"));
        return;
    }

    // 5. 执行最终导入，生成资产
    UGeometryCache* ImportedGeometryCache = AbcImporter.ImportAsGeometryCache(Parent, RF_Public | RF_Standalone);
    if (ImportedGeometryCache)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully imported GeometryCache: %s"), *ImportedGeometryCache->GetName());
        // 可以在这里保存资产等后续操作
    }
}
```

### 进阶用法

**分帧处理与自定义读取**：
对于超大文件或需要极致内存控制的场景，可以使用 `FAbcFile` 的底层接口手动控制帧的读取和清理。

```cpp
#include "AbcFile.h"
#include "AbcUtilities.h"
#include "GeometryCache/GeometryCacheMeshData.h"

void ProcessAbcFileManually(const FString& FilePath)
{
    // 1. 创建并打开 ABC 文件表示
    FAbcFile AbcFile(FilePath);
    EAbcImportError Error = AbcFile.Open();
    if (Error != AbcImportError_NoError) return;

    // 2. 设置导入参数（简化，通常需要更完整设置）
    UAbcImportSettings* Settings = NewObject<UAbcImportSettings>();
    Settings->ImportType = EAlembicImportType::GeometryCache;
    AbcFile.Import(Settings);

    // 3. 获取帧范围和信息
    const int32 StartFrame = AbcFile.GetStartFrameIndex();
    const int32 EndFrame = AbcFile.GetEndFrameIndex();
    const float SecondsPerFrame = AbcFile.GetSecondsPerFrame();

    // 4. 循环处理每一帧（模拟几何缓存构建过程）
    for (int32 FrameIndex = StartFrame; FrameIndex <= EndFrame; ++FrameIndex)
    {
        // a. 读取当前帧的数据（0为并发读取索引）
        AbcFile.ReadFrame(FrameIndex, EFrameReadFlags::None, 0);

        // b. 获取该帧合并后的网格数据
        FGeometryCacheMeshData MeshData;
        FAbcUtilities::GetFrameMeshData(AbcFile, FrameIndex, MeshData, 0);

        // c. 在这里处理 `MeshData` (例如：转换、保存到内存流等)
        // ...

        // d. 释放该帧的原始数据以节省内存
        AbcFile.CleanupFrameData(0);
    }
}
```

## Demo 示例

一个最小的编辑器命令行工具示例，用于将指定的 `.abc` 文件导入为几何缓存。

```cpp
// AlembicDemoCommandlet.h
#pragma once
#include "Commandlets/Commandlet.h"
#include "AlembicDemoCommandlet.generated.h"

UCLASS()
class UAlembicDemoCommandlet : public UCommandlet
{
    GENERATED_BODY()
public:
    virtual int32 Main(const FString& Params) override;
};

// AlembicDemoCommandlet.cpp
#include "AlembicDemoCommandlet.h"
#include "AbcImporter.h"
#include "AbcImportSettings.h"
#include "GeometryCache/GeometryCache.h"
#include "Misc/PackageName.h"
#include "UObject/SavePackage.h"

int32 UAlembicDemoCommandlet::Main(const FString& Params)
{
    // 解析命令行参数
    TArray<FString> Tokens;
    TArray<FString> Switches;
    ParseCommandLine(*Params, Tokens, Switches);

    if (Tokens.Num() < 2)
    {
        UE_LOG(LogTemp, Error, TEXT("Usage: UE5Editor.exe ProjectName -run=UAlembicDemoCommandlet <PathToAbcFile> <OutputPackagePath>"));
        return 1;
    }

    const FString AbcFilePath = Tokens[0];
    const FString OutputPackagePath = Tokens[1]; // 例如: /Game/Imports/MyCache

    // 创建必要的导入器和设置
    FAbcImporter Importer;
    if (Importer.OpenAbcFileForImport(AbcFilePath) != AbcImportError_NoError)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open file: %s"), *AbcFilePath);
        return 1;
    }

    UAbcImportSettings* Settings = NewObject<UAbcImportSettings>();
    Settings->ImportType = EAlembicImportType::GeometryCache;
    Settings->GeometryCacheSettings.bFlattenTracks = true;

    if (Importer.ImportTrackData(FTaskGraphInterface::Get().GetNumWorkerThreads(), Settings) != AbcImportError_NoError)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to import track data"));
        return 1;
    }

    // 创建包并导入
    UPackage* Package = CreatePackage(nullptr, *OutputPackagePath);
    UGeometryCache* GeometryCache = Importer.ImportAsGeometryCache(Package, RF_Public | RF_Standalone | RF_Transactional);

    if (GeometryCache)
    {
        GeometryCache->MarkPackageDirty();
        FString PackageFileName = FPackageName::LongPackageNameToFilename(OutputPackagePath, FPackageName::GetAssetPackageExtension());
        UPackage::SavePackage(Package, GeometryCache, EObjectFlags::RF_Public | EObjectFlags::RF_Standalone, *PackageFileName);
        UE_LOG(LogTemp, Log, TEXT("Successfully saved GeometryCache to: %s"), *PackageFileName);
        return 0;
    }

    UE_LOG(LogTemp, Error, TEXT("Import failed."));
    return 1;
}
```

## 模块依赖

要使用此插件的功能，你的模块需要在 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `AlembicLibrary` | 提供核心的 `FAbcImporter`、`FAbcFile` 等类，用于解析和处理 ABC 文件。 |
| `GeometryCache` | 提供 `UGeometryCache` 资产类和相关数据结构，这是导入“几何缓存”类型时生成的目标资产。 |
| `MeshUtilities` | 用于计算法线、平滑组和切线等网格处理操作。插件内部依赖它。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了在32位和64位系统间格式化字符串说明符不匹配导致的潜在问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将遗留的 `UE_LOG` 宏迁移到新的 `UE_LOGF` 宏，属于代码现代化更新。 |
| 2026-02-27 | `8ce7ca27` | AlembicImporter: Fixed import failure when it couldn't retrieve velocities even though those should | 修复了一个导致导入失败的bug：当理论上应该存在速度数据但实际无法检索时，导入过程会错误地中止。 |
| 2026-02-25 | `74e86b93` | Alembic Import: Fixed out of bounds access (potentially due to negative times). | 修复了一个潜在的数组越界访问错误，该错误可能由文件中存在负时间值引起。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复了代码中无法到达的分支导致的编译错误。 |

### 维护评价

**活跃维护**。AlembicImporter 作为 Epic Games 官方维护的插件，自 2022 年从实验性分支移出后，一直保持稳定更新。从近期的 Git 提交记录可以看出，团队仍在积极处理 bug 修复、代码现代化和稳定性改进。这些更新确保了插件在新版引擎（UE5.8）上的兼容性和可靠性。

该插件是 Unreal Engine 动画和特效工作流中**不可或缺的工具**，尤其对于需要从主流 DCC 软件导入复杂动画数据的项目。尽管最近的更新以修复为主，没有大的功能迭代，但这表明其核心功能已经相当成熟和稳定。**强烈推荐**在需要处理 Alembic 格式数据时使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Importers/AlembicImporter)