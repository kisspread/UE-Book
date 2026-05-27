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

Alembic（.abc）是影视和视觉特效行业广泛使用的开放标准几何缓存格式，用于在不同 DCC 工具（Maya、Houdini、Blender 等）之间交换动画几何体数据。

本插件为 UE5 提供 `.abc` 文件的导入能力，支持将 Alembic 中的多边形网格导入为三种资产类型：

1. **Static Mesh** — 将 Alembic 中的静态网格提取为普通静态网格资产
2. **Geometry Cache** — 将逐帧变化的网格数据导入为几何缓存资产（需要依赖 GeometryCache 插件）
3. **Skeletal Mesh** — 将带有骨骼动画的网格数据导入为骨骼网格资产

此外，所有导入的资产都支持**重新导入（Reimport）**，当源 Alembic 文件更新后可以在编辑器中一键刷新。

## 使用场景

- 你在 Houdini 中制作了程序化动画缓存（如破碎、流体网格），需要导入 UE5 做实时渲染 → 用 Geometry Cache 导入模式
- 你从 Maya 导出了带有骨骼绑定的角色动画 Alembic → 用 Skeletal Mesh 导入模式
- 你有一个静态的高模资产以 Alembic 格式交付 → 用 Static Mesh 导入模式
- 你的美术团队频繁迭代 Alembic 文件，需要在引擎中快速刷新 → 使用重新导入功能

## 蓝图用法

本插件是纯编辑器插件（模块类型为 Editor），**没有暴露任何蓝图可调用节点**。所有操作通过编辑器 UI 完成。

### 导入流程

1. 在内容浏览器中右键 → **Import**，或直接拖拽 `.abc` 文件到内容浏览器
2. 弹出 **Alembic Import Options** 窗口，可配置：
   - 导入类型（Static Mesh / Geometry Cache / Skeletal Mesh）
   - 是否导入特定网格轨道（通过勾选框逐轨道选择）
   - 帧范围、采样设置等
3. 点击 **Import** 完成导入

### 重新导入

1. 在内容浏览器中右键已导入的资产 → **Reimport**
2. 插件会自动关联原始 `.abc` 文件路径并重新解析

## C++ 用法

本插件的核心类 `UAlembicImportFactory` 继承自 `UFactory` 和 `FReimportHandler`，是编辑器导入流程的标准实现。开发者通常不需要直接调用 C++ API，但可以通过继承或引用工厂类来扩展自定义导入管线。

### 头文件引入

```cpp
#include "AlembicImportFactory.h"
```

### 基本用法 — 程序化导入 Alembic 文件

```cpp
// 通过工厂类手动触发 Alembic 导入
// 来源: Classes/AlembicImportFactory.h
UAlembicImportFactory* Factory = NewObject<UAlembicImportFactory>();

// 检查文件是否可导入
FString FilePath = TEXT("/path/to/your/file.abc");
if (Factory->FactoryCanImport(FilePath))
{
    bool bCancelled = false;
    FFeedbackContext Warn;
    
    // 执行导入，会根据 ImportSettings 自动选择导入模式
    UObject* ImportedAsset = Factory->FactoryCreateFile(
        nullptr,                    // InClass
        GetTransientPackage(),      // InParent
        FName("ImportedAsset"),     // InName
        RF_NoFlags,                 // Flags
        FilePath,                   // Filename
        nullptr,                    // Parms
        &Warn,                      // Warn
        bCancelled                  // bOutOperationCanceled
    );
}
```

### 进阶用法 — 分类型导入

```cpp
// 来源: Classes/AlembicImportFactory.h

// 如果需要明确指定导入类型，可以使用以下专用方法：

// 导入为静态网格（可能产生多个子对象）
TArray<UObject*> StaticMeshes = Factory->ImportStaticMesh(Importer, Parent, Flags);

// 导入为几何缓存
UGeometryCache* Cache = Cast<UGeometryCache>(Factory->ImportGeometryCache(Importer, Parent, Flags));

// 导入为骨骼网格
TArray<UObject*> SkeletalMeshes = Factory->ImportSkeletalMesh(Importer, Parent, Flags);
```

## Demo 示例

本插件为编辑器导入工具，不提供运行时 API。典型使用方式是通过编辑器 UI 操作，以下展示如何在编辑器工具中程序化触发重新导入：

```cpp
// MyAlembicReimportTool.h
#pragma once

#include "CoreMinimal.h"

class FMyAlembicReimportTool
{
public:
    /** 批量重新导入内容浏览器中选中的 Alembic 资产 */
    static void BatchReimportSelectedAssets(const TArray<UObject*>& Assets);
};
```

```cpp
// MyAlembicReimportTool.cpp
#include "MyAlembicReimportTool.h"
#include "AlembicImportFactory.h"
#include "GeometryCache.h"
#include "StaticMesh.h"
#include "SkeletalMesh.h"

void FMyAlembicReimportTool::BatchReimportSelectedAssets(const TArray<UObject*>& Assets)
{
    UAlembicImportFactory* Factory = NewObject<UAlembicImportFactory>();

    for (UObject* Asset : Assets)
    {
        // 检查该资产是否支持重新导入
        TArray<FString> OutFilenames;
        if (Factory->CanReimport(Asset, OutFilenames) && OutFilenames.Num() > 0)
        {
            // 根据资产类型调用对应的重新导入方法
            if (UStaticMesh* StaticMesh = Cast<UStaticMesh>(Asset))
            {
                Factory->ReimportStaticMesh(StaticMesh);
            }
            else if (UGeometryCache* Cache = Cast<UGeometryCache>(Asset))
            {
                Factory->ReimportGeometryCache(Cache);
            }
            else if (USkeletalMesh* SkelMesh = Cast<USkeletalMesh>(Asset))
            {
                Factory->ReimportSkeletalMesh(SkelMesh);
            }
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryCache` | 几何缓存资产类型，Alembic 动画网格导入的目标类型 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式化字符串中 32/64 位不匹配的平台兼容问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到新的 UE_LOGF 宏 |
| 2026-02-27 | `8ce7ca27` | AlembicImporter: Fixed import failure when it couldn't retrieve velocities even though those should | 修复无法获取速度数据时的导入失败问题 |
| 2026-02-25 | `74e86b93` | Alembic Import: Fixed out of bouds access (potentially due to negative times). | 修复因负时间值导致的数组越界访问 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复不可达代码编译错误 |

### 维护评价

- **创建历史**：该插件在 2022 年从 Experimental 目录迁移到正式目录，但 Alembic 导入功能在 UE4 时代就已存在
- **维护状态**：活跃维护。2026 年 2-4 月期间有多次 bug 修复，包括数据导入稳定性修复和代码现代化（UE_LOG → UE_LOGF）
- **更新内容**：以 bug 修复和代码质量改进为主，功能已趋于稳定
- **推荐使用**：✅ 推荐。作为 Epic 官方维护的 Alembic 导入方案，功能成熟、持续维护，是 UE5 中处理 Alembic 文件的标准选择

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/)