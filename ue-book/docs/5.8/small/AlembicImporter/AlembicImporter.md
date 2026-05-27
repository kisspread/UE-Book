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

AlembicImporter 插件的核心功能是将 Alembic (.abc) 格式的文件导入到 Unreal Engine 中。Alembic 是一个开源的计算机图形学数据交换格式，广泛用于在不同的数字内容创建 (DCC) 软件（如 Maya, Houdini, Blender）之间传递复杂的几何体和动画数据。

该插件的存在解决了以下问题：
1.  **工作流程集成**：允许艺术家将在外部 DCC 软件中创建的复杂动画、模拟效果（如布料、流体）和角色动画无缝地带入 UE5 项目。
2.  **数据保真**：确保高精度的几何体拓扑、顶点位置动画（变形动画）和骨骼动画在导入过程中得以保留。
3.  **资产优化**：支持将 Alembic 文件中的动画数据转换为 UE5 原生的“几何缓存”（Geometry Cache）资产或骨骼网格体，便于在引擎内高效使用。

它通常作为 GeometryCache 插件的前置依赖，为其提供源数据。

## 使用场景

-   你需要将角色在 Maya 或 Houdini 中制作的复杂面部动画或身体变形动画导入到 UE5 项目中。
-   你在 DCC 软件中模拟了一个布料飘动或毛发摆动的效果，希望将其作为动画资产在引擎中回放。
-   你从其他软件导出了一个带有复杂拓扑变化的静态模型，希望将其作为带动画的网格体导入。
-   你需要将一系列逐帧变化的几何体数据（如流体模拟）导入引擎，用作特效或环境动画。

## 蓝图用法

AlembicImporter 主要是一个编辑器导入工厂，其核心功能（如导入窗口、选项设置）通常通过编辑器的“导入”操作触发，而不是通过蓝图节点直接调用。它没有暴露用于运行时蓝图交互的 `BlueprintCallable` 函数。

**核心交互**：当在内容浏览器中右键选择“导入”并选择一个 .abc 文件时，引擎会调用此插件的 `UAlembicImportFactory` 来处理导入流程。

## C++ 用法

### 头文件引入

在需要以编程方式控制 Alembic 导入的模块中，可以引入工厂类的头文件。

```cpp
#include "AlembicImportFactory.h"
```

### 基本用法

以下是如何在 C++ 代码中创建一个 Alembic 导入工厂实例并触发导入流程的简化示例。

```cpp
// 假设在某个编辑器工具或自定义资产处理器中
#include "AlembicImportFactory.h"
#include "AbcImportSettings.h"

void ImportAlembicFile(const FString& FilePath)
{
    // 1. 创建导入工厂实例
    UAlembicImportFactory* ImportFactory = NewObject<UAlembicImportFactory>();
    if (ImportFactory)
    {
        // 2. (可选) 配置导入设置，通常由导入对话框完成
        //    UAbcImportSettings* Settings = NewObject<UAbcImportSettings>();
        //    ImportFactory->ImportSettings = Settings;

        // 3. 设置导入参数
        UClass* ClassToCreate = UStaticMesh::StaticClass(); // 或 UGeometryCache, USkeletalMesh
        UObject* ParentPackage = GetTransientPackage();
        FName ObjectName = FPackageName::GetLongPackageAssetName(FilePath);
        EObjectFlags Flags = RF_Public | RF_Standalone;

        // 4. 执行导入
        bool bOperationCanceled = false;
        FFeedbackContext Warn;
        TArray<UObject*> ImportedObjects = ImportFactory->FactoryCreateFile(
            ClassToCreate,
            ParentPackage,
            ObjectName,
            Flags,
            FilePath,
            nullptr, // Parms
            &Warn,
            bOperationCanceled
        );

        // 5. 处理导入结果
        if (!bOperationCanceled && ImportedObjects.Num() > 0)
        {
            UE_LOG(LogTemp, Log, TEXT("Successfully imported %d objects from %s"), ImportedObjects.Num(), *FilePath);
            // 对 ImportedObjects 进行后续处理，如保存到磁盘
        }
    }
}
```
*注意：此代码为概念示例，实际生产环境使用中，通常依赖编辑器完整的导入管线来确保设置正确和资源注册。*

## Demo 示例

以下是一个最小化的自定义资产导入器示例，演示了如何在编辑器扩展中触发 Alembic 导入。

**MyAssetImportTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyAssetImportTool
{
public:
    static void RunImport(const FString& AlembicFilePath);
};
```

**MyAssetImportTool.cpp**
```cpp
#include "MyAssetImportTool.h"
#include "AlembicImportFactory.h"
#include "AbcImportSettings.h"

void FMyAssetImportTool::RunImport(const FString& AlembicFilePath)
{
    // 获取或创建导入工厂
    UAlembicImportFactory* Factory = NewObject<UAlembicImportFactory>();

    // 创建默认导入设置（模拟点击“导入”时的默认行为）
    UAbcImportSettings* DefaultSettings = NewObject<UAbcImportSettings>();
    // 可以在此处修改 DefaultSettings 的成员来调整默认导入参数
    // DefaultSettings->ImportType = EAlembicImportType::GeometryCache;
    Factory->ImportSettings = DefaultSettings;

    // 设置导入目标
    UObject* ImportRoot = GetTransientPackage(); // 或指定一个内容浏览器路径下的包
    FName DesiredName = FPaths::GetBaseFilename(AlembicFilePath);
    EObjectFlags Flags = RF_Public | RF_Standalone;

    // 执行导入
    FFeedbackContext Context;
    bool bCanceled = false;
    TArray<UObject*> Assets = Factory->FactoryCreateFile(
        UStaticMesh::StaticClass(), // 注意：Factory会根据设置和文件内容自动解析实际类型
        ImportRoot,
        DesiredName,
        Flags,
        AlembicFilePath,
        nullptr,
        &Context,
        bCanceled
    );

    if (!bCanceled && Assets.Num() > 0)
    {
        UE_LOG(LogTemp, Display, TEXT("Import tool created %d asset(s)."), Assets.Num());
        // 这里可以将资产移动到内容浏览器中的指定路径并保存
    }
}
```

## 模块依赖

该插件自身包含两个编辑器模块。要在你的项目或插件中使用其 C++ 类，需要添加以下依赖。

| 模块 | 用途 |
|---|---|
| `AlembicLibrary` | 提供 Alembic 文件解析和数据转换的核心库 |
| `GeometryCache` | 插件声明依赖，用于将动画数据存储为几何缓存资产 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了日志格式化说明符在 32 位和 64 位系统上的兼容性问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件内的日志调用从 UE_LOG 迁移到更现代的 UE_LOGF 宏。 |
| 2026-02-27 | `8ce7ca27` | AlembicImporter: Fixed import failure when it couldn't retrieve velocities even though those should | 修复了在无法获取速度数据（理论上应该能获取）时导致导入失败的问题。 |
| 2026-02-25 | `74e86b93` | Alembic Import: Fixed out of bounds access (potentially due to negative times). | 修复了一个可能由负时间值引起的数组越界访问错误。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复了编译时可能产生的“不可达代码”警告或错误。 |

### 维护评价

AlembicImporter 插件目前处于 **活跃维护** 状态。
-   **创建时间**：约 4 年前（2022 年），作为正式功能从 Experimental 目录迁移出来。
-   **更新频率**：在 2026 年初至今有持续的更新，修复了多个 bug 和兼容性问题，表明 Epic 仍在积极维护。
-   **功能状态**：核心功能稳定，近期的提交主要集中在 bug 修复、代码现代化和格式化上，没有新增重大功能，但修复了影响稳定性的关键问题。
-   **推荐使用**：**是**。作为官方提供的标准 Alembic 导入解决方案，它是将 DCC 动画数据引入 UE5 的首选工具。虽然近期没有新功能，但持续的维护保证了其可靠性和与最新引擎版本的兼容性。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/EditorTests/FunctionalTesting/FunctionalTest/Alembic) (推断路径，通常功能测试位于此区域)