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

## 用途

Alembic Importer 插件为虚幻引擎提供了导入 Alembic（`.abc`）文件的能力。Alembic 是一种开放标准的计算机图形交换格式，广泛应用于影视和 VFX 行业，用于存储复杂的动画、变形网格、粒子缓存等时间序列数据。

该插件通过两个模块工作：
- **AlembicImporter** – 负责资产工厂、导入 UI 和编辑器集成（工厂类 `UAlembicImportFactory`）。
- **AlembicLibrary** – 底层 C++ 库，封装了 Alembic SDK 的核心解析与转换逻辑（类 `FAbcImporter`）。

插件解决的核心问题是：将来自 DCC 软件（如 Maya、Houdini、Blender）导出的 Alembic 缓存文件，转换为虚幻引擎可直接使用的资产类型（Geometry Cache、Static Mesh、Skeletal Mesh），同时保持动画、变形和拓扑信息的完整性。

## 使用场景

- 你需要导入一个角色变形动画（如服装布料模拟、面部表情），这些数据以 `.abc` 序列形式保存 → 使用 Alembic Importer 生成 **Geometry Cache**。
- 你拥有静态几何体（如建筑模块）的 Alembic 文件，希望直接导入为静态网格体 → 使用它转换为 **Static Mesh**。
- 你希望在虚幻引擎中重放从外部 DCC 导出的蒙皮动画（顶点动画） → 转换为 **Skeletal Mesh**（支持骨骼驱动）。
- 你已经在项目中使用了 Geometry Cache 资产，且源 Alembic 文件发生了变化 → 使用工厂的**重新导入**功能更新资产。

## 蓝图用法

该插件主要面向编辑器，不提供可直接在蓝图中调用的蓝图函数节点。所有导入操作均通过编辑器 UI 或 C++ 编程方式触发。

若需要在运行时动态加载 Alembic 资产，请使用标准的 `UGeometryCache` / `USkeletalMesh` / `UStaticMesh` 加载函数（如 `LoadObject`、`CreatePackage`），但 Alembic 导入本身**仅支持在编辑器中执行**。

## C++ 用法

### 头文件引入

```cpp
#include "AlembicImportFactory.h"
#include "AlembicLibrary/Public/AbcImporter.h"   // 底层库
#include "GeometryCache/Classes/GeometryCache.h"
```

### 基本用法：编程式导入 Alembic 文件

以下示例演示如何通过 `UAlembicImportFactory` 以编程方式将 Alembic 文件导入为 Geometry Cache 资产。

```cpp
// Source: Engine/Plugins/Importers/AlembicImporter/Source/AlembicImporter/Private/AlembicImportFactory.cpp

UObject* UAlembicImportFactory::FactoryCreateFile(UClass* InClass, UObject* InParent, FName InName, EObjectFlags Flags, const FString& Filename, const TCHAR* Parms, FFeedbackContext* Warn, bool& bOutOperationCanceled)
{
    // 内部会调用 ImportGeometryCache / ImportStaticMesh / ImportSkeletalMesh
    // 本示例假设目标类型为 Geometry Cache
    // 实际使用时可调用以下专用函数之一：
    // ImportGeometryCache(Importer, InParent, Flags);
    // ImportStaticMesh(Importer, InParent, Flags);
    // ImportSkeletalMesh(Importer, InParent, Flags);
}
```

更直接的用法：通过资产管理器（AssetTools）触发导入（推荐）：

```cpp
#include "AssetToolsModule.h"
#include "Factories/Factory.h"

void ImportAlembicFile(const FString& FilePath, const FString& DestinationPath)
{
    IAssetTools& AssetTools = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools").Get();

    UFactory* Factory = NewObject<UAlembicImportFactory>();
    TArray<UObject*> ImportedAssets = AssetTools.ImportAssetsWithDialog(FilePath, DestinationPath, Factory);
    
    // 处理导入结果
    for (UObject* Asset : ImportedAssets)
    {
        // 例如，若导入为 GeometryCache
        if (UGeometryCache* Cache = Cast<UGeometryCache>(Asset))
        {
            // 做进一步处理
        }
    }
}
```

### 进阶用法：使用 FAbcImporter 直接解析（AlembicLibrary）

对于需要更精细控制的导入流程，可直接使用 `FAbcImporter` 类。

```cpp
#include "AbcImporter.h"

void ParseAlembicManually(const FString& FilePath)
{
    FAbcImporter Importer;
    if (Importer.OpenAbcFileForImport(FilePath))
    {
        // 获取多边形网格列表
        const TArray<FAbcPolyMesh*>& PolyMeshes = Importer.GetAbcPolyMeshList();

        // 根据自定义条件选取部分网格
        TArray<FAbcPolyMesh*> SelectedMeshes;
        for (FAbcPolyMesh* Mesh : PolyMeshes)
        {
            if (Mesh->GetName().StartsWith("MyMesh"))
            {
                SelectedMeshes.Add(Mesh);
            }
        }

        // 然后可调用 Importer.ImportMesh(SelectedMeshes, ...) 生成资产
        // 注意：FAbcImporter 还提供 GetFrameIndexForFirstData()、GetNumberOfSamples() 等时间信息
    }
}
```

## Demo 示例

以下是一个完整的最小 CMake 集成示例（仅演示概念，非实际运行代码）。

### DemoAlembicImport.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "AlembicImportFactory.h"
#include "GeometryCache.h"

class FBasicAlembicImporter
{
public:
    static UGeometryCache* ImportGeometryCacheFromFile(const FString& FilePath, UObject* Outer, FName Name, EObjectFlags Flags);
};
```

### DemoAlembicImport.cpp

```cpp
#include "DemoAlembicImport.h"

UGeometryCache* FBasicAlembicImporter::ImportGeometryCacheFromFile(const FString& FilePath, UObject* Outer, FName Name, EObjectFlags Flags)
{
    // 创建 Alembic Importer 实例（来自 AlembicLibrary 模块）
    FAbcImporter Importer;
    if (!Importer.OpenAbcFileForImport(FilePath))
    {
        return nullptr;
    }

    // 创建工厂实例
    UAlembicImportFactory* Factory = NewObject<UAlembicImportFactory>();
    Factory->ImportSettings = NewObject<UAbcImportSettings>(Factory);
    
    // 执行导入（返回 UGeometryCache*）
    UObject* Result = Factory->ImportGeometryCache(Importer, Outer, Flags);
    if (Result)
    {
        Result->Rename(*Name.ToString(), Outer);
    }
    return Cast<UGeometryCache>(Result);
}
```

实际项目中，建议使用 `AssetTools` 提供的导入接口，而非直接调用工厂内部方法。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AlembicLibrary` | 提供底层 Alembic 文件解析和网格生成逻辑（类 `FAbcImporter`, `FAbcPolyMesh`） |
| `GeometryCache` | 目标资产类型之一，Plugin 依赖中已声明 |
| `UnrealEd` | 工厂与重新导入机制（常见编辑器依赖，省略） |

其他依赖（如 `Core`, `CoreUObject`, `Engine`, `Slate`, `SlateCore`, `UMG`, `InputCore`）均为标准编辑器模块，不单独列出。

## 维护状态

### 近期更新

- 2025-09-23 `1711cfb6` — 修复导入 Alembic 时因拓扑变化引发的潜在崩溃。
- 2025-09-23 `34eca2a4` — 修复网格缺少必要属性（如位置）时导入可能崩溃的问题。
- 2025-09-23 `c4464ee3` — 修复从 Alembic 导入拓扑变化的几何缓存时的潜在崩溃。
- 2025-07-29 `e8248cbc` — 骨骼网格 LOD 信息结构重构（仅影响内部布局，无关功能）。
- 2025-07-14 `8c4cad91` — 初始版本提交，添加基本导入功能。

### 维护评价

该插件尚处于早期阶段（约 2 个月），但更新较为频繁，主要集中在修复导入过程的稳定性和处理边界情况。目前没有发现被废弃的迹象，推荐用于需要导入 Alembic 文件的编辑器流程。已知限制：
- 仅支持在编辑器中使用，不支持运行时导入。
- 某些复杂的拓扑变化（如顶点数量变化）可能仍需进一步优化（已修复部分此类崩溃）。
- 依赖 Geometry Cache 插件，需确保该插件同时启用。

综合评价：**活跃维护**，适合在生产项目中试用，但在正式上线前建议进行充分的资产测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/AlembicImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/AlembicImporter/Tests)（可能位于 Engine/Tests 目录下）