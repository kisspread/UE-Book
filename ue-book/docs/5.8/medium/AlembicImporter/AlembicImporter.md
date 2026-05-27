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
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter) | |

## 用途

Alembic Importer 插件为 Unreal Engine 5 提供了对 Alembic (.abc) 文件格式的全面导入支持。Alembic 是一种在视觉特效和动画领域广泛使用的开放标准，用于在不同数字内容创作 (DCC) 工具之间交换复杂的几何体、动画和模拟数据。

此插件的核心功能远不止简单的网格导入。它专门设计用于处理**时间序列数据**，能够将 DCC 软件（如 Houdini, Maya, Blender）中创建的动画变形几何体、流体模拟、布料解算结果等，高效地导入为 UE5 中的**动画几何体缓存 (GeometryCache)** 资产，或者转换为静态网格体或骨骼网格体。它解决了在影视级动画和复杂特效工作流中，资产需要跨软件且保持动态细节的需求。

## 使用场景

- 你需要从 Houdini、Maya 或其他 DCC 软件中导入**粒子流体、布料模拟、刚体破碎动画**等复杂的动画几何体到 UE5 → 使用此插件导入为 **GeometryCache**。
- 你拥有由程序化工具生成的、包含逐帧顶点动画的复杂模型序列 → 使用此插件保留其时间信息。
- 你需要将 DCC 中的角色动画或环境动画序列导入为可播放的资产 → 使用此插件导入为 **GeometryCache** 或尝试转换为 **SkeletalMesh**。
- 项目需要导入来自外部 CAD 或 VFX 管道的复杂静态模型 → 使用此插件作为静态网格体的导入通道。

## 蓝图用法

此插件主要作为**编辑器内容工厂**运行，其核心功能通过内容浏览器的“导入”菜单触发。不直接暴露蓝图可调用的运行时节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无（编辑器操作） | 所有导入操作通过编辑器 UI 驱动 | `UAlembicImportFactory` |

### 使用示例（蓝图描述）

1.  在内容浏览器中右键单击，选择“导入资产”。
2.  选择你的 `.abc` 文件。
3.  弹出导入选项窗口，你可以配置导入类型（GeometryCache/StaticMesh/SkeletalMesh）、时间范围、动画设置等。
4.  点击“导入”按钮，资产将被创建在指定位置。

## C++ 用法

在 C++ 层面，主要的交互点是通过 `UAlembicImportFactory` 类来程序化触发导入，或者理解并扩展其导入逻辑。

### 头文件引入

```cpp
#include "AlembicImporterModule.h"
#include "AlembicImportFactory.h"
```

### 基本用法

通过 UFactory 机制进行文件导入，通常在自动化管道中使用。

```cpp
// 模拟一个简化的程序化导入流程 (仅供示意，实际实现更复杂)
#include "AssetImportTask.h"
#include "AlembicImportFactory.h"

void ImportAlembicAsset()
{
    UAssetImportTask* Task = NewObject<UAssetImportTask>();
    Task->Filename = TEXT("/Path/To/Your/Animation.abc");
    Task->DestinationPath = TEXT("/Game/ImportedAssets");
    Task->bReplaceExisting = true;
    Task->bAutomated = true; // 跳过 UI 提示

    // 使用工厂类，引擎会根据文件后缀自动选择 AlembicImportFactory
    UFactory* Factory = NewObject<UAlembicImportFactory>();
    Task->Factory = Factory;

    // 执行导入
    FAssetToolsModule& AssetToolsModule = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools");
    AssetToolsModule.Get().ImportAssetTasks({Task});

    if (Task->Result == EImportResult::Succeeded)
    {
        UE_LOG(LogTemp, Log, TEXT("Alembic import succeeded. Imported assets: %s"), *Task->ImportedObjectPaths[0]);
    }
}
```
*（来源：`UAlembicImportFactory` 的 `FactoryCreateFile` 接口及通用资产导入逻辑）*

### 进阶用法

操作导入设置，实现自定义的导入流程控制。`UAbcImportSettings` 是配置导入参数的关键。

```cpp
// 假设你已经通过某种方式获取了要导入的 Alembic 文件路径
FString AbcFilePath = TEXT("/Path/To/Complex_Sim.abc");

// 创建或获取一个 AbcImporter 实例来分析文件（概念性代码）
FAbcImporter Importer; // 注意：FAbcImporter 是一个复杂的数据类，需要正确初始化
// ... 初始化 Importer 以分析 AbcFilePath ...

// 创建一个工厂实例并设置其导入参数
UAlembicImportFactory* Factory = NewObject<UAlembicImportFactory>();
if (Factory->ImportSettings)
{
    // 配置导入设置，例如指定为 GeometryCache 导入
    Factory->ImportSettings->ImportType = EAlembicImportType::GeometryCache;
    // 设置动画帧范围等参数...
    // Factory->ImportSettings->...
}

// 然后，你可以像基本用法中一样，将这个预配置的工厂用于 UAssetImportTask
// ... 或者直接调用 Factory->FactoryCreateFile(...) (需要处理所有参数)
```
*（来源：`UAlembicImportFactory::ShowImportOptionsWindow`, `PopulateOptionsWithImportData` 方法及 `UAbcImportSettings` 类）*

## Demo 示例

一个完整的最小示例，演示如何在 C++ 中编写一个自定义的命令行或编辑器工具函数来导入 Alembic 文件。

```cpp
// MyAlembicImporter.h
#pragma once

#include "CoreMinimal.h"

class FMyAlembicImporter
{
public:
    /**
     * 程序化导入一个 Alembic 文件为 GeometryCache。
     * @param AbcFilePath 源 Alembic 文件的完整路径。
     * @param OutputPackagePath 导出资产的目标包路径 (例如: TEXT("/Game/ImportedCache"))
     * @return 导入的 UObject 指针，失败则返回 nullptr。
     */
    static UObject* ImportAsGeometryCache(const FString& AbcFilePath, const FString& OutputPackagePath);
};
```

```cpp
// MyAlembicImporter.cpp
#include "MyAlembicImporter.h"
#include "AssetImportTask.h"
#include "AlembicImportFactory.h"
#include "AbcImportSettings.h"
#include "AssetToolsModule.h"
#include "IAssetTools.h"

UObject* FMyAlembicImporter::ImportAsGeometryCache(const FString& AbcFilePath, const FString& OutputPackagePath)
{
    if (!FPaths::FileExists(AbcFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Alembic file not found: %s"), *AbcFilePath);
        return nullptr;
    }

    // 创建导入任务
    UAssetImportTask* ImportTask = NewObject<UAssetImportTask>();
    ImportTask->Filename = AbcFilePath;
    ImportTask->DestinationPath = OutputPackagePath;
    ImportTask->bReplaceExisting = true;
    ImportTask->bAutomated = true; // 跳过任何导入选项 UI

    // 获取 Alembic 工厂并进行配置
    UAlembicImportFactory* AlembicFactory = NewObject<UAlembicImportFactory>();
    if (AlembicFactory->ImportSettings)
    {
        // 设置为导入 GeometryCache
        AlembicFactory->ImportSettings->ImportType = EAlembicImportType::GeometryCache;
        // 这里可以进一步配置几何体缓存的压缩、采样率等设置
        // AlembicFactory->ImportSettings->GeometryCacheSettings...
    }
    ImportTask->Factory = AlembicFactory;

    // 执行导入
    FAssetToolsModule& AssetToolsModule = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools");
    AssetToolsModule.Get().ImportAssetTasks({ImportTask});

    // 检查结果
    if (ImportTask->Result == EImportResult::Succeeded && ImportTask->ImportedObjectPaths.Num() > 0)
    {
        FString AssetPath = ImportTask->ImportedObjectPaths[0];
        UObject* ImportedAsset = LoadObject<UObject>(nullptr, *AssetPath);
        UE_LOG(LogTemp, Log, TEXT("Successfully imported Alembic as GeometryCache at: %s"), *AssetPath);
        return ImportedAsset;
    }

    UE_LOG(LogTemp, Warning, TEXT("Alembic import failed for file: %s"), *AbcFilePath);
    return nullptr;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryCache` | Alembic 导入器的核心依赖，用于创建和存储动画几何体缓存资产 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化字符串中数据类型不匹配的潜在问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 统一日志宏，迁移到更新的 UE_LOGF 宏 |
| 2026-02-27 | `8ce7ca27` | AlembicImporter: Fixed import failure when it couldn't retrieve velocities even though those should | 修复了无法获取速度数据时导致的导入失败问题 |
| 2026-02-25 | `74e86b93` | Alembic Import: Fixed out of bounds access (potentially due to negative times). | 修复了因负时间值可能引起的数组越界访问错误 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复了编译时不可达代码的错误 |

### 维护评价

**活跃维护**。Alembic Importer 插件自 2022 年从实验性模块移出后，一直在持续维护。从 2026 年初至今，提交记录显示有多次重要的 Bug 修复，特别是解决了导入失败、数据访问越界等稳定性问题，表明开发团队对其运行可靠性非常关注。作为影视、广告和视觉特效项目的关键工具，该插件与 GeometryCache 插件紧密结合，是 UE5 处理复杂动画资产的核心基础设施，预计会长期得到支持。**推荐在需要导入 Alembic 时间序列数据的生产环境中使用。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Runtime/AlembicImporterTest)