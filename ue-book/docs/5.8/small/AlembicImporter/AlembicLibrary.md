# Alembic Importer

> Support importing Alembic files

| 属性 | 值 |
|---|---|
| 中文名 | Alembic导入器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AlembicImporter` (Runtime), `AlembicLibrary` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-01-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter) | |

## 用途

此插件用于将 **Alembic (.abc)** 文件导入到虚幻引擎中。Alembic 是视觉特效和动画行业广泛使用的开放标准格式，用于存储复杂的动画几何体（如角色、流体、粒子系统等）缓存数据。插件解决了从DCC工具（如Maya, 3ds Max, Blender等）导出复杂动画资产到游戏引擎的关键需求，支持将动画数据转化为UE可使用的资产。

核心功能包括：
*   **多类型导入**：支持将ABC文件作为静态网格、几何缓存（Geometry Cache）或骨骼网格导入。
*   **动画采样控制**：提供灵活的采样选项（按帧、按时间步长、按X帧），支持重采样和压缩。
*   **数据压缩优化**：支持使用PCA（主成分分析）算法压缩顶点动画数据，以减少内存占用和提升性能。
*   **材质与法线处理**：能够从ABC文件的面集（Face Sets）创建或查找材质，并提供丰富的法线计算与平滑组生成选项。
*   **空间转换**：内置对Maya、3ds Max等不同DCC软件坐标系和轴向的预设转换。

## 使用场景

*   你从Maya或3ds Max中导出了一个角色面部表情动画的Alembic缓存 → 使用`Skeletal`或`GeometryCache`模式导入，将动画数据压缩为形态目标（Morph Targets）或几何缓存资产。
*   你需要将一段复杂的流体模拟（如水、烟雾）作为动画网格导入游戏引擎 → 使用`GeometryCache`模式导入，并调整采样和压缩设置以获得最佳性能和视觉效果。
*   你有一个由DCC工具导出的、带动画的静态场景（如摇摆的树木、飘动的旗帜）→ 使用`GeometryCache`模式将其导入为动画静态网格。
*   你需要为特定的动画序列精确控制导入的起始帧、结束帧和采样率 → 在导入设置中配置`FAbcSamplingSettings`。

## 蓝图用法

该插件的核心导入逻辑由C++实现，主要通过编辑器导入对话框进行交互。但其导入参数通过蓝图可读写的`UCLASS`和`USTRUCT`暴露，允许在蓝图或编辑器工具中进行程序化设置。

### 核心节点

此插件没有直接暴露`BlueprintCallable`函数供游戏逻辑调用。其蓝图交互点主要体现在可编辑的导入设置类`UAbcImportSettings`及其关联结构体上。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UAbcImportSettings` | 存储所有Alembic文件导入选项的单例对象。在导入对话框中被读取和修改。 | `UAbcImportSettings` |
| `EAlembicImportType` | 枚举：指定导入类型（静态网格、几何缓存、骨骼）。 | `EAlembicImportType` |
| `FAbcSamplingSettings` | 结构体：控制动画采样（类型、步长、起止帧）。 | `FAbcSamplingSettings` |
| `FAbcCompressionSettings` | 结构体：控制动画压缩（合并网格、基准计算方式）。 | `FAbcCompressionSettings` |
| `FAbcGeometryCacheSettings` | 结构体：控制几何缓存特有设置（扁平化轨迹、运动向量）。 | `FAbcGeometryCacheSettings` |

### 使用示例（蓝图描述）

在蓝图中，你可以通过获取`UAbcImportSettings::Get()`单例来访问和修改导入选项。例如，你可以创建一个编辑器工具蓝图，在其中：
1.  使用`Set Property`节点将`ImportType`设置为`GeometryCache`。
2.  访问`SamplingSettings`属性，将`SamplingType`设置为`PerXFrames`，并设置`FrameSteps`为2。
3.  访问`GeometryCacheSettings`属性，将`MotionVectors`设置为`ImportAbcVelocitiesAsMotionVectors`。
这些设置会直接影响下次通过该插件导入Alembic文件时的行为。

## C++ 用法

### 头文件引入

```cpp
#include "AbcImporter.h"
#include "AbcImportSettings.h"
#include "AbcFile.h"
```

### 基本用法

以下示例展示了如何通过C++编程方式打开一个Alembic文件并将其作为几何缓存导入。

```cpp
// 源文件参考: Public/AbcImporter.h
#include "AbcImporter.h"
#include "AbcImportSettings.h"

void ImportAbcAsGeometryCache(const FString& AbcFilePath, UObject* InParent, EObjectFlags Flags)
{
    // 1. 创建并配置导入器实例
    FAbcImporter AbcImporter;
    
    // 2. 打开ABC文件并检查错误
    const EAbcImportError OpenError = AbcImporter.OpenAbcFileForImport(AbcFilePath);
    if (OpenError != EAbcImportError::AbcImportError_NoError)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open ABC file: %s"), *AbcFilePath);
        return;
    }
    
    // 3. 获取并配置导入设置
    UAbcImportSettings* Settings = UAbcImportSettings::Get();
    if (Settings)
    {
        Settings->ImportType = EAlembicImportType::GeometryCache;
        // 可以进一步配置Settings->SamplingSettings, Settings->GeometryCacheSettings等
    }
    
    // 4. 导入轨道数据
    const EAbcImportError ImportError = AbcImporter.ImportTrackData(FPlatformMisc::NumberOfCores(), Settings);
    if (ImportError != EAbcImportError::AbcImportError_NoError)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to import track data."));
        return;
    }
    
    // 5. 执行几何缓存导入
    UGeometryCache* GeometryCache = AbcImporter.ImportAsGeometryCache(InParent, Flags);
    if (GeometryCache)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully imported GeometryCache: %s"), *GeometryCache->GetName());
        // 对导入的GeometryCache资产进行后续处理...
    }
}
```

### 进阶用法

对于更复杂的场景，如需要并发读取帧数据或进行后期处理，可以直接使用`FAbcFile`和`FAbcUtilities`类。

```cpp
// 源文件参考: Public/AbcFile.h, Public/AbcUtilities.h
#include "AbcFile.h"
#include "AbcUtilities.h"

void ProcessAbcFileFrames(const FString& AbcFilePath)
{
    // 1. 创建FAbcFile实例并打开
    FAbcFile AbcFile(AbcFilePath);
    EAbcImportError Error = AbcFile.Open();
    if (Error != EAbcImportError::AbcImportError_NoError)
    {
        return;
    }
    
    // 2. 配置导入设置（可选）
    // ... 设置AbcFile的ImportSettings ...
    
    // 3. 处理帧数据（例如，用于自定义分析或预览）
    int32 StartFrame = AbcFile.GetStartFrameIndex();
    int32 EndFrame = AbcFile.GetEndFrameIndex();
    
    for (int32 FrameIndex = StartFrame; FrameIndex <= EndFrame; ++FrameIndex)
    {
        FGeometryCacheMeshData MeshData;
        // 使用FAbcUtilities获取特定帧的合并网格数据
        FAbcUtilities::GetFrameMeshData(AbcFile, FrameIndex, MeshData);
        
        // 此处可以对MeshData进行分析、修改或序列化等操作
        // ...
    }
}
```

## Demo 示例

一个最小化的、用于将Alembic文件作为几何缓存导入并获取其动画时长信息的C++示例。

**AbcImportDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class UGeometryCache;

DECLARE_LOG_CATEGORY_EXTERN(LogAbcImportDemo, Log, All);

class FAbcImportDemo
{
public:
    static UGeometryCache* ImportAbcAsGeometryCacheWithInfo(const FString& AbcFilePath, UObject* Outer);
    static float GetAnimationDuration(const FString& AbcFilePath);
};
```

**AbcImportDemo.cpp**
```cpp
#include "AbcImportDemo.h"
#include "AbcImporter.h"
#include "AbcFile.h"
#include "AbcImportSettings.h"

DEFINE_LOG_CATEGORY(LogAbcImportDemo);

UGeometryCache* FAbcImportDemo::ImportAbcAsGeometryCacheWithInfo(const FString& AbcFilePath, UObject* Outer)
{
    FAbcImporter Importer;
    
    // 打开文件
    if (Importer.OpenAbcFileForImport(AbcFilePath) != EAbcImportError::AbcImportError_NoError)
    {
        UE_LOG(LogAbcImportDemo, Error, TEXT("Cannot open file: %s"), *AbcFilePath);
        return nullptr;
    }
    
    // 设置为几何缓存导入
    UAbcImportSettings* Settings = UAbcImportSettings::Get();
    Settings->ImportType = EAlembicImportType::GeometryCache;
    
    // 导入轨道
    if (Importer.ImportTrackData(1, Settings) != EAbcImportError::AbcImportError_NoError)
    {
        UE_LOG(LogAbcImportDemo, Error, TEXT("Failed to import tracks for: %s"), *AbcFilePath);
        return nullptr;
    }
    
    // 执行导入
    UGeometryCache* GC = Importer.ImportAsGeometryCache(Outer, RF_NoFlags);
    
    if (GC)
    {
        UE_LOG(LogAbcImportDemo, Log, TEXT("Imported GC '%s' with %d tracks."), *GC->GetName(), GC->GetTracks().Num());
    }
    
    return GC;
}

float FAbcImportDemo::GetAnimationDuration(const FString& AbcFilePath)
{
    FAbcFile AbcFile(AbcFilePath);
    if (AbcFile.Open() != EAbcImportError::AbcImportError_NoError)
    {
        return 0.0f;
    }
    
    // 导入设置是获取正确帧范围信息所必需的
    UAbcImportSettings* Settings = UAbcImportSettings::Get();
    AbcFile.Import(Settings);
    
    const float Duration = AbcFile.GetImportLength();
    UE_LOG(LogAbcImportDemo, Log, TEXT("Animation duration for '%s': %.3f seconds"), *AbcFilePath, Duration);
    
    return Duration;
}
```

## 模块依赖

从插件源码和`.uplugin`文件分析，使用者需依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `AlembicLibrary` | 本插件的核心功能库，提供了Alembic文件解析、数据转换和导入的主要API。 |
| `GeometryCache` | 提供`UGeometryCache`资产类型，用于存储导入的顶点动画数据。这是此插件的强制依赖。 |
| `Alembic (第三方库)` | `AlembicLibrary`模块内部链接的Alembic C++库，用于解析`.abc`文件格式。无需使用者直接链接。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了32位与64位数据格式化字符串不匹配的潜在问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的日志宏迁移到新的UE_LOGF宏，属于代码现代化更新。 |
| 2026-02-27 | `8ce7ca27` | AlembicImporter: Fixed import failure when it couldn't retrieve velocities even though those should | 修复了在应该能获取速度数据但无法获取时导致的导入失败问题。 |
| 2026-02-25 | `74e86b93` | Alembic Import: Fixed out of bounds access (potentially due to negative times). | 修复了可能由负时间值引起的数组越界访问错误，增强了稳定性。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复了编译器报出的无法到达代码错误，改善代码质量。 |

### 维护评价

*   **活跃维护**：插件从实验阶段移出（2022年），并持续获得更新。最近一次更新在2026年4月，表明仍在积极维护。
*   **更新内容**：近期的提交主要集中在**错误修复**和**代码质量改进**（格式化、宏迁移、越界访问修复），说明插件功能已趋于稳定，团队致力于提升其可靠性和兼容性。
*   **推荐使用**：推荐使用。作为官方提供的、功能完备的Alembic导入解决方案，它经过了广泛测试，并能得到持续维护。对于需要在UE中处理复杂动画缓存的工作流，这是首选方案。
*   **注意事项**：插件为**Editor-only**模块，不会打包到发布版本中，仅用于内容创建。导入过程可能较为耗时和消耗内存，特别是处理大型或高保真度的ABC文件时，建议合理配置采样和压缩选项。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter/Tests) (路径基于常规插件结构推断)