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
| 创建时间 | 2025-07-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/AlembicImporter) | |

---

## 用途

**Alembic Importer** 是虚幻引擎内置的 Alembic 文件导入工具，用于将 OpenAlembic 格式（`.abc`）的三维动画缓存数据导入到引擎中。它支持将 Alembic 文件转换为**静态网格体**、**几何缓存（Geometry Cache）** 或**骨骼网格体（Skeletal Mesh）**，并提供了丰富的采样、压缩、转换设置，特别适合导入来自 Maya、Houdini、Blender 等 DCC 工具的模拟动画、角色动作或特效缓存。

该插件解决了外部软件生成的复杂动画数据（如布料模拟、粒子变体、角色动画）无法直接使用的问题，通过高效的读取和压缩算法（基于 PCA 的主成分分析）将大量顶点动画转化为引擎可播放的资产。

---

## 使用场景

- 你需要将外部模拟软件（如 Houdini）的布料/流体缓存导入 UE，作为几何缓存播放 → 选择 **Geometry Cache** 导入类型
- 你希望将角色动画以顶点动画形式导入，并利用骨骼网格体进行混合 → 选择 **Skeletal** 导入类型，启用 Morph Target 压缩
- 你只需要 Alembic 文件的某一帧作为静态物体 → 选择 **Static Mesh** 导入类型
- 你希望对导入的动画进行精度/性能权衡，通过 PCA 压缩减少内存占用 → 在导入设置中调整 `CompressionSettings`

---

## 蓝图用法

本插件的主要功能是编辑器导入工具，因此大部分操作在导入对话框（`FAbcImporter`）中完成，蓝图可直接使用的是导入设置结构体和枚举。以下结构体均在 `UAbcImportSettings` 中暴露，可在蓝图节点中创建和修改。

### 核心设置结构体

| 结构体 | 说明 | 所在文件 |
|---|---|---|
| `FAbcSamplingSettings` | 采样方式（逐帧、每隔 X 帧、每隔 X 秒）及帧范围 | `AbcImportSettings.h` |
| `FAbcCompressionSettings` | 压缩策略（PCA 基数计算方式、合并网格等） | `AbcImportSettings.h` |
| `FAbcStaticMeshSettings` | 静态网格体导入相关选项 | `AbcImportSettings.h` |
| `FAbcGeometryCacheSettings` | 几何缓存导入相关选项（如烘焙矩阵动画） | `AbcImportSettings.h` |
| `FAbcNormalGenerationSettings` | 法线生成方式 | `AbcImportSettings.h` |
| `FAbcMaterialSettings` | 材质导入选项（创建材质、忽略材质等） | `AbcImportSettings.h` |
| `FAbcConversionSettings` | 坐标系转换预设及自定义旋转/缩放 | `AbcImportSettings.h` |

### 枚举

| 枚举 | 说明 |
|---|---|
| `EAlembicImportType` | 导入类型：StaticMesh / GeometryCache / Skeletal |
| `EAlembicSamplingType` | 采样类型：PerFrame / PerXFrames / PerTimeStep |
| `EBaseCalculationType` | 压缩基数计算方式：PercentageBased / FixedNumber / NoCompression |

> 注：实际导入触发是在编辑器菜单或 Python 脚本中调用 `FAbcImporter` 的 C++ API，蓝图不直接提供导入节点。

---

## C++ 用法

### 头文件引入

```cpp
#include "AbcImporter.h"
#include "AbcFile.h"
#include "AbcImportSettings.h"
```

### 基本用法

以下示例来自 `AlembicTestCommandlet.cpp`（路径：`Engine/Plugins/Importers/AlembicImporter/Source/AlembicLibrary/Private/AlembicTestCommandlet.cpp`），展示了使用 `FAbcImporter` 打开并导入一个 Alembic 文件的基本流程：

```cpp
// 1. 创建导入器实例
FAbcImporter Importer;

// 2. 打开 Alembic 文件，获取错误码
FString FilePath = TEXT("C:/MyAnim.abc");
EAbcImportError Error = Importer.OpenAbcFileForImport(FilePath);

if (Error == AbcImportError_NoError)
{
    // 3. 创建导入设置对象（也可从已存在的资产导入数据中复制）
    UAbcImportSettings* ImportSettings = NewObject<UAbcImportSettings>();
    ImportSettings->ImportType = EAlembicImportType::GeometryCache;
    ImportSettings->SamplingSettings.SamplingType = EAlembicSamplingType::PerFrame;
    ImportSettings->CompressionSettings.BaseCalculationType = EBaseCalculationType::PercentageBased;
    ImportSettings->CompressionSettings.PercentageOfTotalBases = 100.0f;

    // 4. 开始导入数据（传入设置对象）
    UGeometryCache* GeometryCache = Importer.ImportTrackData(nullptr, ImportSettings);

    if (GeometryCache)
    {
        UE_LOG(LogTemp, Log, TEXT("GeometryCache imported successfully: %s"), *GeometryCache->GetName());
    }
}
```

### 进阶用法：自定义帧处理与数据提取

使用 `FAbcFile` 类可以直接读取 Alembic 文件中的原始帧数据，用于非标准导入流程（如自定义烘焙）：

```cpp
#include "AbcFile.h"
#include "AbcPolyMesh.h"
#include "AbcTransform.h"
#include "GeometryCacheTrackStreamable.h" // 如果生成几何缓存

// 打开文件
FAbcFile AbcFile(TEXT("MyMesh.abc"));
EAbcImportError Error = AbcFile.Open();
if (Error != AbcImportError_NoError) return;

// 导入设置（必须）
UAbcImportSettings* Settings = NewObject<UAbcImportSettings>();
AbcFile.Import(Settings);

// 读取所有帧并获取网格数据
const int32 NumFrames = AbcFile.GetImportNumFrames();
const int32 NumMeshes = AbcFile.GetNumPolyMeshes();
for (int32 FrameIndex = 0; FrameIndex < NumFrames; ++FrameIndex)
{
    AbcFile.ReadFrame(FrameIndex, EFrameReadFlags::None);
    for (int32 MeshIndex = 0; MeshIndex < NumMeshes; ++MeshIndex)
    {
        FAbcPolyMesh* PolyMesh = AbcFile.GetPolyMeshes()[MeshIndex];
        const FAbcMeshSample* Sample = PolyMesh->GetSample(FrameIndex);
        if (Sample)
        {
            // 使用 Sample->Vertices, Sample->Indices, Sample->Normals 等
        }
    }
    AbcFile.CleanupFrameData();
}
```

### 使用 Eigen 库进行 SVD 分解（压缩算法内部）

`EigenHelper` 提供了将数组转换为 Eigen 矩阵并进行奇异值分解的便利函数，此功能在 PCA 压缩内部使用。通常不需要用户直接调用。

```cpp
#include "EigenHelper.h"

TArray64<float> Data; // 原始数据
int32 Rows = 100, Cols = 200;
TArray64<float> U, V, S;
EigenHelpers::PerformSVD(Data, Rows, Cols, U, V, S);
```

---

## Demo 示例

以下是一个完整的 Commandlet 示例，展示了从 Alembic 文件导入并生成几何缓存的最小流程。

**AlembicDemoCommandlet.h**
```cpp
#pragma once

#include "Commandlets/Commandlet.h"
#include "AlembicDemoCommandlet.generated.h"

UCLASS()
class UAlembicDemoCommandlet : public UCommandlet
{
    GENERATED_UCLASS_BODY()

    virtual int32 Main(const FString& Params) override;
};
```

**AlembicDemoCommandlet.cpp**
```cpp
#include "AlembicDemoCommandlet.h"
#include "AbcImporter.h"
#include "GeometryCache/Classes/GeometryCache.h"
#include "GeometryCache/Classes/GeometryCacheTrackStreamable.h"

UAlembicDemoCommandlet::UAlembicDemoCommandlet(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
}

int32 UAlembicDemoCommandlet::Main(const FString& Params)
{
    // 解析命令行参数：期望第一个参数是 .abc 文件路径
    TArray<FString> Tokens, Switches;
    ParseCommandLine(*Params, Tokens, Switches);

    if (Tokens.Num() < 1)
    {
        UE_LOG(LogTemp, Error, TEXT("Usage: AlembicDemo <path_to_abc>"));
        return 1;
    }

    FString AbcFilePath = Tokens[0];

    // 创建导入器
    FAbcImporter Importer;
    EAbcImportError Error = Importer.OpenAbcFileForImport(AbcFilePath);
    if (Error != AbcImportError_NoError)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open Alembic file: %s"), *AbcFilePath);
        return 1;
    }

    // 设置导入选项
    UAbcImportSettings* Settings = NewObject<UAbcImportSettings>();
    Settings->ImportType = EAlembicImportType::GeometryCache;
    Settings->SamplingSettings.SamplingType = EAlembicSamplingType::PerFrame;
    Settings->CompressionSettings.BaseCalculationType = EBaseCalculationType::NoCompression;

    // 执行导入（不指定外部 package，自动创建临时包）
    UGeometryCache* GeometryCache = Importer.ImportTrackData(nullptr, Settings);
    if (!GeometryCache)
    {
        UE_LOG(LogTemp, Error, TEXT("Import failed."));
        return 1;
    }

    UE_LOG(LogTemp, Log, TEXT("GeometryCache imported: %s, Frames: %d"),
        *GeometryCache->GetName(),
        GeometryCache->GetEndFrame() - GeometryCache->GetStartFrame() + 1);

    return 0;
}
```

> **注意**：此示例依赖 `GeometryCache` 插件模块，编译前请确保你的模块的 `Build.cs` 中已添加 `"GeometryCache"` 依赖。

---

## 模块依赖

使用 **Alembic Importer** 插件中的功能时，你的模块需要添加以下特殊依赖（省略了 Core/CoreUObject/Engine/UEOpenExternally 等常见模块）：

| 模块 | 用途 |
|---|---|
| `AlembicLibrary` | 提供核心导入类（FAbcImporter、FAbcFile 等） |
| `GeometryCache` | 用于创建几何缓存资产（UGeometryCache） |
| `MeshUtilities` | 用于网格数据构建与法线计算 |
| `AlembicImporter`（可选） | 如果你需要直接使用导入对话框 UI，需依赖此模块 |

如果你只使用 `AlembicLibrary` 中的底层读取功能（如 `FAbcFile`），则仅需依赖 `AlembicLibrary` 和 `MeshUtilities`；若要创建几何缓存资产，还需要 `GeometryCache`。

---

## 维护状态

### 近期更新

- 2025-09-23 `1711cfb6` Fixed potential crash when importing Alembic with varying topology.
- 2025-09-23 `34eca2a4` Fixed potential crash during Alembic import when the mesh is missing necessary attributes like position.
- 2025-09-23 `c4464ee3` Fixed potential crash when importing geometry cache with varying topologies from Alembic.
- 2025-07-29 `e8248cbc` Skeletal Mesh: Move LOD info FSkeletalMeshSourceModel
- 2025-07-14 `8c4cad91` - Changed all WITH_EDITORONLY_DATA properties in StaticMesh to have accessors, and a few changes to ...

### 维护评价

该插件创建于 2025 年 7 月，由 Epic Games 官方维护，属于**活跃维护**状态。近期（2025 年 9 月）连续提交了多个针对拓扑变化和缺失属性导致崩溃的修复，体现了对稳定性的重视。插件代码质量较高（使用现代 C++ 风格，支持并行帧读取），功能完整。由于创建时间较短，尚未发现已知的重大缺陷或废弃标记。强烈推荐在需要导入 Alembic 动画缓存的项目中使用。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/AlembicImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Programs/TestBatch) （搜索 “Alembic” 相关测试）
- [AlembicLibrary 模块头文件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/AlembicImporter/Source/AlembicLibrary/Public)