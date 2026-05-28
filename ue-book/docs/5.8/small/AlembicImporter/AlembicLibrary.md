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

Alembic Importer 插件用于将 Alembic (`.abc`) 格式的 3D 动画数据导入到虚幻引擎中。Alembic 是一种开放标准，常用于在不同的数字内容创作 (DCC) 工具（如 Maya, 3ds Max, Houdini）之间交换复杂的动画数据，例如布料模拟、流体模拟、刚体动画或角色动画。

该插件的核心功能是解析 Alembic 文件中的几何网格 (PolyMesh) 和变换 (Transform) 数据，并将其转换为虚幻引擎原生的资产类型。它支持将动画序列以不同的形式存储，包括：
1.  **静态网格 (Static Mesh)**：只导入动画的第一帧。
2.  **几何缓存 (Geometry Cache)**：将完整的顶点动画数据流式存储，适用于复杂的变形动画。
3.  **骨骼网格 (Skeletal Mesh)**：通过主成分分析 (PCA) 压缩算法，将顶点动画数据转换为骨骼网格的 Morph Target 动画，从而在保持动画效果的同时，大幅减小资产大小并利用引擎的骨骼动画系统进行优化。

## 使用场景

-   **电影与视觉特效制作**：从 Houdini 或 Maya 导入复杂的布料、头发、流体模拟动画到虚幻引擎中进行实时渲染和虚拟制片。
-   **角色动画工作流**：将使用雕刻工具或程序化生成的角色变形动画（如面部表情）导入引擎，并转换为高效的 Morph Target 系统。
-   **资产优化**：当 Alembic 动画数据过大时，使用 PCA 压缩将其转换为骨骼网格，以优化运行时性能和内存占用。
-   **跨软件协作**：接收来自其他 DCC 工具艺术家导出的动画数据，确保在虚幻引擎中的视觉一致性。

## 蓝图用法

此插件主要通过编辑器导入对话框和 C++ API 使用，**没有直接暴露用于创建或控制导入过程的蓝图节点**。所有导入设置（如导入类型、采样、压缩选项）均在导入资产时通过 `UAbcImportSettings` 类进行配置。

在蓝图中，你可能会间接接触到此插件产生的资产类型（`UStaticMesh`, `UGeometryCache`, `USkeletalMesh`），但无法通过蓝图动态触发 Alembic 导入。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无直接蓝图节点 | 插件主要通过编辑器菜单和 C++ API 操作 | N/A |

### 使用示例（蓝图描述）

在编辑器中，通过 **Content Browser** 的 **Import** 按钮或直接拖拽 `.abc` 文件到内容浏览器，会弹出 **Alembic Import Options** 对话框。在这里，你可以设置导入类型、动画采样、法线计算、材质、压缩和几何缓存等所有参数。这些参数对应 `UAbcImportSettings` 中的属性。

## C++ 用法

该插件的核心是 `FAbcImporter` 类，它封装了从打开文件到生成虚幻资产的全部逻辑。

### 头文件引入

```cpp
#include "AbcImporter.h"
#include "AbcFile.h"
#include "AbcImportSettings.h"
```

### 基本用法

以下示例展示了如何使用 `FAbcImporter` 将一个 Alembic 文件作为静态网格导入。

```cpp
// (示例：引擎编辑器工具或自定义 Commandlet 中)
#include "AbcImporter.h"
#include "AbcImportSettings.h"
#include "UObject/SavePackage.h"

void ImportAlembicAsStaticMesh()
{
    const FString AbcFilePath = TEXT("/Game/TestMesh.abc");
    const FString PackagePath = TEXT("/Game/ImportedMesh");
    const FName AssetName = TEXT("MyImportedMesh");

    // 1. 创建导入器实例
    FAbcImporter Importer;

    // 2. 打开 Alembic 文件并读取基础信息
    EAbcImportError OpenError = Importer.OpenAbcFileForImport(AbcFilePath);
    if (OpenError != AbcImportError_NoError)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open Alembic file: %s"), *AbcFilePath);
        return;
    }

    // 3. 配置导入设置
    UAbcImportSettings* ImportSettings = UAbcImportSettings::Get();
    ImportSettings->ImportType = EAlembicImportType::StaticMesh;
    ImportSettings->StaticMeshSettings.bMergeMeshes = true;
    ImportSettings->StaticMeshSettings.bGenerateLightmapUVs = true;

    // 4. 导入轨道数据（应用设置）
    EAbcImportError ImportError = Importer.ImportTrackData(FPlatformMisc::NumberOfCores(), ImportSettings);
    if (ImportError != AbcImportError_NoError)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to import track data from Alembic file."));
        return;
    }

    // 5. 执行导入为静态网格
    UObject* ParentPackage = CreatePackage(*PackagePath);
    TArray<UStaticMesh*> ImportedMeshes = Importer.ImportAsStaticMesh(ParentPackage, RF_Public | RF_Standalone);

    if (ImportedMeshes.Num() > 0)
    {
        // 保存第一个导入的网格
        UStaticMesh* Mesh = ImportedMeshes[0];
        Mesh->Rename(*AssetName, ParentPackage);
        FAssetRegistryModule::AssetCreated(Mesh);

        const FString PackageFileName = FPackageName::LongPackageNameToFilename(PackagePath, FPackageName::GetAssetPackageExtension());
        UPackage::SavePackage(ParentPackage, Mesh, EObjectFlags::RF_Public | EObjectFlags::RF_Standalone, *PackageFileName);

        UE_LOG(LogTemp, Log, TEXT("Successfully imported Alembic as Static Mesh: %s"), *AssetName.ToString());
    }
}
```

### 进阶用法：读取几何缓存网格数据

如果你需要在程序化工具中读取并处理 Alembic 的某一帧数据（例如，用于自定义的网格修改），可以使用 `FAbcFile` 和 `FAbcUtilities`。

```cpp
#include "AbcFile.h"
#include "AbcUtilities.h"
#include "AbcImportSettings.h"
#include "GeometryCache/GeometryCacheMeshData.h"

void ReadSingleFrameData()
{
    const FString AbcFilePath = TEXT("/Game/AnimatedMesh.abc");
    const int32 FrameIndex = 10; // 你想读取的帧

    // 1. 打开文件
    FAbcFile AbcFile(AbcFilePath);
    EAbcImportError Error = AbcFile.Open();
    if (Error != AbcImportError_NoError) return;

    // 2. 准备导入设置（影响如何解释数据）
    UAbcImportSettings* Settings = UAbcImportSettings::Get();
    Settings->ImportType = EAlembicImportType::GeometryCache;
    Settings->GeometryCacheSettings.bFlattenTracks = true;

    Error = AbcFile.Import(Settings);
    if (Error != AbcImportError_NoError) return;

    // 3. 读取指定帧的网格数据
    FGeometryCacheMeshData MeshData;
    FAbcUtilities::GetFrameMeshData(AbcFile, FrameIndex, MeshData);

    // 4. 现在你可以访问 MeshData 中的顶点、索引、法线等数据
    if (MeshData.Positions.Num() > 0)
    {
        UE_LOG(LogTemp, Log, TEXT("Read %d vertices from frame %d."), MeshData.Positions.Num(), FrameIndex);
        // 进行自定义处理...
    }

    // 5. 清理（FAbcFile析构函数会自动处理）
}
```

## Demo 示例

以下是一个完整的、可编译的 Actor 类示例，它在游戏开始时尝试导入指定的 Alembic 文件。

**AlembicImporterDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AlembicImporterDemoActor.generated.h"

UCLASS()
class AAlembicImporterDemoActor : public AActor
{
    GENERATED_BODY()
    
public:
    AAlembicImporterDemoActor();

protected:
    virtual void BeginPlay() override;

public:
    /** 要导入的 Alembic 文件路径（相对于项目 Content 目录或绝对路径） */
    UPROPERTY(EditAnywhere, Category = "Alembic Import")
    FString AlembicFilePath;

    /** 导入后资产保存的路径 */
    UPROPERTY(EditAnywhere, Category = "Alembic Import")
    FString ImportAssetPath = TEXT("/Game/ImportedAlembicAssets");

private:
    void PerformAlembicImport();
};
```

**AlembicImporterDemoActor.cpp**
```cpp
#include "AlembicImporterDemoActor.h"
#include "AbcImporter.h"
#include "AbcImportSettings.h"
#include "UObject/SavePackage.h"
#include "AssetRegistry/AssetRegistryModule.h"

AAlembicImporterDemoActor::AAlembicImporterDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AAlembicImporterDemoActor::BeginPlay()
{
    Super::BeginPlay();

    if (!AlembicFilePath.IsEmpty())
    {
        PerformAlembicImport();
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("AlembicFilePath is not set. No import performed."));
    }
}

void AAlembicImporterDemoActor::PerformAlembicImport()
{
    UE_LOG(LogTemp, Log, TEXT("Starting Alembic import from: %s"), *AlembicFilePath);

    // 步骤 1: 初始化导入器
    FAbcImporter Importer;
    EAbcImportError OpenError = Importer.OpenAbcFileForImport(AlembicFilePath);

    if (OpenError != EAbcImportError::AbcImportError_NoError)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open Alembic file. Error code: %d"), static_cast<int32>(OpenError));
        return;
    }

    // 步骤 2: 配置导入设置
    UAbcImportSettings* ImportSettings = UAbcImportSettings::Get();
    ImportSettings->ImportType = EAlembicImportType::GeometryCache; // 导入为几何缓存
    ImportSettings->GeometryCacheSettings.bFlattenTracks = true;    // 合并所有顶点动画到一条轨道
    ImportSettings->ConversionSettings.Preset = EAbcConversionPreset::Maya; // 假设来自 Maya，自动应用坐标转换

    // 步骤 3: 解析数据并应用设置
    EAbcImportError ImportError = Importer.ImportTrackData(FPlatformMisc::NumberOfCores(), ImportSettings);
    if (ImportError != EAbcImportError::AbcImportError_NoError)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to process Alembic track data."));
        return;
    }

    // 步骤 4: 创建资产包并执行导入
    const FString AssetName = FPaths::GetBaseFilename(AlembicFilePath);
    const FString FinalPackagePath = FPaths::Combine(ImportAssetPath, AssetName);
    UPackage* AssetPackage = CreatePackage(*FinalPackagePath);

    UGeometryCache* ImportedCache = Importer.ImportAsGeometryCache(AssetPackage, RF_Public | RF_Standalone);

    if (ImportedCache)
    {
        // 步骤 5: 保存资产到磁盘
        ImportedCache->Rename(*AssetName, AssetPackage);
        FAssetRegistryModule::AssetCreated(ImportedCache);

        const FString PackageFileName = FPackageName::LongPackageNameToFilename(FinalPackagePath, FPackageName::GetAssetPackageExtension());
        bool bSaved = UPackage::SavePackage(AssetPackage, ImportedCache, EObjectFlags::RF_Public | EObjectFlags::RF_Standalone, *PackageFileName);

        if (bSaved)
        {
            UE_LOG(LogTemp, Log, TEXT("Alembic file imported and saved successfully as GeometryCache at: %s"), *FinalPackagePath);
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to save the imported GeometryCache package."));
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("ImportAsGeometryCache returned null. Import failed."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AlembicLibrary` | 提供 Alembic 文件解析、网格数据处理和导入工具的核心功能库 |
| `GeometryCache` | 提供 `UGeometryCache` 资产类及相关功能，是几何缓存导入模式的必需依赖 |
| `Eigen` (第三方库) | 用于执行 PCA (主成分分析) 压缩算法，以支持将动画数据转换为骨骼网格的 Morph Target |

**注意**：此插件还依赖第三方 Alembic 库（如 AlembicCore），这些依赖已包含在引擎的第三方库目录中，通常无需在你的项目 `Build.cs` 中额外声明。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了32位与64位格式说明符不匹配的潜在问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式 `UE_LOG` 日志宏迁移至新式 `UE_LOGF`。 |
| 2026-02-27 | `8ce7ca27` | AlembicImporter: Fixed import failure when it couldn't retrieve velocities even though those should | 修复了在应当存在速度数据但无法读取时导致的导入失败问题。 |
| 2026-02-25 | `74e86b93` | Alembic Import: Fixed out of bounds access (potentially due to negative times). | 修复了可能由负数时间值引起的数组越界访问错误。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复了不可达代码导致的编译错误。 |

### 维护评价

**活跃维护**。
-   **创建时间**：插件于2022年从实验性状态移出，至今约3年。
-   **更新频率**：最近一次提交（2026-04-27）距今不到一个月，且近期的提交记录显示持续有bug修复和代码质量改进（如日志系统迁移、边界条件修复）。
-   **活跃度**：尽管核心功能已稳定，但团队仍在积极修复使用中发现的问题，表明该插件仍处于活跃维护状态，是导入复杂动画数据的可靠选择。
-   **推荐使用**：✅ 推荐。作为虚幻引擎官方提供的、功能完善的 Alembic 导入解决方案，对于需要处理来自专业DCC工具的动画数据的项目，这是一个必要且维护良好的插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/)
- 测试用例：插件目录内未发现独立的测试文件，相关功能测试可能集成在引擎的整体测试框架中。