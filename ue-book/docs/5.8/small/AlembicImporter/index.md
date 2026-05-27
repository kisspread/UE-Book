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
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter) | |

## 用途
该插件解决了在虚幻引擎中导入和解析 Alembic (`.abc`) 文件格式的问题。Alembic 是影视和游戏行业广泛使用的开放标准，用于交换复杂的几何缓存（如动画角色、刚体模拟、粒子系统）数据。此插件使得用户能够将这些资产直接导入到虚幻引擎中，用于过场动画、实时动态几何等场景，是工作流中连接 DCC（数字内容创作）工具与引擎的关键桥梁。

## 使用场景
- 你需要从 Houdini、Maya、Blender 或其他 DCC 软件导出复杂的顶点动画、布料或刚体模拟缓存到 UE5 中 → 使用 Alembic Importer
- 你正在制作一个过场动画，其中包含需要在引擎中回放的预计算角色或物体动画 → 导入 Alembic 几何缓存
- 你希望用程序化方式（通过蓝图或C++）处理从外部工具生成的粒子或流体缓存数据 → 通过此插件导入 `.abc` 文件

## 蓝图用法
插件主要提供导入功能，通常通过编辑器的文件导入对话框触发。其核心类 `UAlembicImportFactory` 处理导入任务。蓝图可间接通过资产操作或自定义导入逻辑与导入过程交互，但直接蓝图节点相对有限，更倾向于由编辑器在后台完成。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| *(无公开的 BlueprintCallable 导入函数)* | 导入过程主要由编辑器 UI 和工厂类驱动。 | `UAlembicImportFactory` |

### 使用示例（蓝图描述）
通常，在“内容浏览器”中右键选择“导入”，选择 `.abc` 文件即可。如果需要自定义流程（如批量导入），可以在 C++ 中创建 `FAssetTools` 的导入任务或使用 `UEditorAssetLibrary`，并指定 `UFactory` 类型为 `UAlembicImportFactory`。

## C++ 用法
### 头文件引入
```cpp
#include "AlembicImporterModule.h"
```

### 基本用法
调用插件的导入接口（通常通过资产工具）来导入一个 Alembic 文件。
*（示例逻辑，基于常见的工厂导入模式推断）*
```cpp
#include "AssetToolsModule.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "AlembicImporterModule.h"

// 获取资产工具模块
FAssetToolsModule& AssetToolsModule = FModuleManager::LoadModuleChecked<FAssetToolsModule>(“AssetTools”);
IAssetTools& AssetTools = AssetToolsModule.Get();

// 设置导入参数
UImportFactory* Factory = NewObject<UAlembicImportFactory>();
TArray<FString> FilesToImport = { TEXT(“C:/path/to/your/file.abc”) };
AssetTools.ImportAssets(FilesToImport, TEXT(“/Game/ImportedAlembic”));
```

### 进阶用法
通过 C++ 完全控制导入过程，例如批量处理或修改默认导入设置。
```cpp
// 假设需要为每个导入任务设置自定义选项
FAssetImportInfo ImportInfo;
ImportInfo.Insert(FAssetImportInfo::FSourceFile(FilesToImport[0]));

// 使用UFactory的ImportObject函数进行更精细的控制
UObject* ImportedAsset = Factory->ImportObject(UStaticMesh::StaticClass(),
                                                GetTransientPackage(),
                                                TEXT(“TestMesh”),
                                                RF_Public | RF_Standalone,
                                                FilesToImport[0],
                                                nullptr,
                                                ImportInfo);
```

## Demo 示例
一个最小示例，展示如何通过 C++ 代码在编辑器或运行时（如果支持）触发 Alembic 文件导入。
```cpp
// MyAlembicImporterExample.h
#pragma once
#include "CoreMinimal.h"

class FMyAlembicImporterExample
{
public:
    static void ImportAlembicFile(const FString& FilePath);
};
```
```cpp
// MyAlembicImporterExample.cpp
#include “MyAlembicImporterExample.h”
#include “AssetToolsModule.h”
#include “AlembicImporterModule.h”

void FMyAlembicImporterExample::ImportAlembicFile(const FString& FilePath)
{
    // 确保文件存在
    if (!FPaths::FileExists(FilePath)) return;

    // 加载资产工具
    FAssetToolsModule& AssetToolsModule = FModuleManager::LoadModuleChecked<FAssetToolsModule>(TEXT(“AssetTools”));
    IAssetTools& AssetTools = AssetToolsModule.Get();

    // 创建导入工厂实例
    UAlembicImportFactory* AlembicFactory = NewObject<UAlembicImportFactory>();

    // 指定目标路径（例如在 Game 目录下）
    const FString DestinationPath = TEXT(“/Game/ImportedAlembic”);

    // 执行导入
    TArray<UObject*> ImportedObjects;
    AssetTools.ImportAssets({ FilePath }, DestinationPath, AlembicFactory, ImportedObjects);

    if (ImportedObjects.Num() > 0)
    {
        UE_LOG(LogTemp, Log, TEXT(“成功导入 Alembic 文件: %s”), *FilePath);
    }
}
```

## 模块依赖
从 `Build.cs` 分析，要使用此插件，你的模块除了标准依赖外，可能还需要：
| 模块 | 用途 |
|---|---|
| `GeometryCache` | 处理几何缓存资产的核心模块，Alembic 导入的动画数据常存储于此。 |
| `GeometryCore` | 提供几何数据结构处理的基础功能。 |
| `MeshDescription` | 用于构建和编辑静态网格的中间表示，可能用于导入静态几何体。 |

## 维护状态
### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化字符串中32位与64位说明符匹配问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从旧版 UE_LOG 迁移到新版 UE_LOGF。 |
| 2026-02-27 | `8ce7ca27` | AlembicImporter: Fixed import failure when it couldn‘t retrieve velocities even though those should | 修复了在应有速度数据但获取失败时导致导入失败的问题。 |
| 2026-02-25 | `74e86b93` | Alembic Import: Fixed out of bounds access (potentially due to negative times). | 修复了导入时可能因负时间值导致的数组越界访问问题。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复了不可达代码错误。 |

### 维护评价
该插件由 Epic Games 从 `Experimental` 目录正式移出，已有约 5 年历史。近期（2026年）的提交主要集中在修复导入过程中的 bug、改善代码健壮性和进行现代化代码迁移（如日志宏更新）。这表明插件目前处于**活跃维护**状态，主要进行稳定性和可靠性修复，而非添加新功能。作为引擎核心导入功能的一部分，它被广泛使用且可靠。**推荐使用**，尤其是需要 Alembic 工作流的项目。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter/Tests) *(路径基于插件结构推测)*