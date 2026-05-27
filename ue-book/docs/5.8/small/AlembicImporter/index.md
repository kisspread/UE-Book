# Alembic Importer

> Support importing Alembic files

| 属性 | 值 |
|---|---|
| 中文名 | 通用三维导入 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AlembicImporter` (Editor), `AlembicLibrary` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-01-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter) | |

## 用途

该插件为 Unreal Engine 提供导入 Alembic (.abc) 文件格式的支持。Alembic 是一种开源的计算机图形学交换格式，广泛用于在不同 DCC (数字内容创作) 软件（如 Maya, Houdini, Cinema 4D, Blender 等）之间高效、无损地传递复杂的几何体、动画及模拟数据（如流体、布料、刚体）。通过此插件，开发者和艺术家可以在 Unreal Engine 中直接导入由这些软件生成的缓存动画或静态网格，解决资产跨软件交换的核心问题。

## 使用场景

-   **影视与过场动画制作**：从 Maya 或 Houdini 中导入复杂的角色动画或特效模拟（如爆炸、流体）到 UE 中进行最终渲染或实时预览。
-   **游戏资产工作流**：将高精度、细分后的雕刻模型（如 ZBrush）通过 Alembic 格式导入引擎，再进行拓扑优化和纹理烘焙。
-   **建筑可视化**：导入来自 3ds Max 或 Blender 的复杂建筑模型和动画漫游序列。
-   **技术美术与程序化生成**：将 Houdini 等软件中通过程序化方法生成的大量几何体或动画数据，以轻量、高效的方式导入引擎。

## 模块列表

| 模块 | 说明 |
|---|---|
| `AlembicImporter` | 核心导入器模块，负责解析 .abc 文件并将其转换为 Unreal 可用的资产（如静态网格、几何体缓存、动画序列）。 |
| `AlembicLibrary` | 底层库模块，封装了 Alembic SDK 的核心读取和数据转换功能，为 `AlembicImporter` 提供底层支持。 |

## 蓝图用法

此插件主要提供编辑器内的导入功能，其核心 API 大多为编辑器工具类，通过标准的“文件 -> 导入”菜单调用，而非通过蓝图节点在游戏运行时动态调用。

## C++ 用法

主要的 C++ 用法集中在编辑器扩展和自定义导入流程中。

### 头文件引入

```cpp
#include "AbcImportSettings.h"
#include "AbcImportData.h"
```

### 基本用法：通过导入器设置参数

```cpp
// 创建并配置导入设置
UAbcImportSettings* ImportSettings = NewObject<UAbcImportSettings>();
ImportSettings->ImportType = EAlembicImportType::GeometryCache; // 指定导入类型为几何体缓存
ImportSettings->bFlattenHierarchy = true; // 是否展平层次结构
ImportSettings->ConversionSettings.Scale = FVector(100.0f); // 设置转换缩放

// 使用设置执行导入 (通常由编辑器框架调用)
// IAbcImporter::Get().ImportAbcFile(FilePath, ImportSettings);
```

### 进阶用法：自定义导入器重写

该插件设计允许通过继承 `FAbcImporter` 来扩展或修改导入逻辑，以处理自定义属性或特殊数据。

```cpp
#include "AbcImporter.h"

class FMyCustomAbcImporter : public FAbcImporter
{
public:
    // 重写处理顶点颜色的函数，添加自定义逻辑
    virtual bool ProcessVertexColors(const TArray<FLinearColor>& RawColors, UStaticMesh* StaticMesh) override
    {
        // 在默认处理基础上增加额外逻辑
        bool bSuccess = FAbcImporter::ProcessVertexColors(RawColors, StaticMesh);
        // ... 自定义操作 ...
        return bSuccess;
    }
};
```

## Demo 示例

由于 `AlembicImporter` 是一个编辑器导入模块，其“Demo”体现在通过编辑器界面或脚本触发的导入流程。一个最小化的 C++ 使用示例如下：

**MyAbcImportWorker.h**
```cpp
#pragma once

class FMyAbcImportWorker
{
public:
    void RunSimpleImport(const FString& FilePath);
};
```

**MyAbcImportWorker.cpp**
```cpp
#include "MyAbcImportWorker.h"
#include "AbcImportSettings.h"
#include "AbcImporter.h"

void FMyAbcImportWorker::RunSimpleImport(const FString& FilePath)
{
    // 1. 获取导入器实例
    FAbcImporter& AbcImporter = IAbcImporter::Get();

    // 2. 准备默认设置
    UAbcImportSettings* Settings = NewObject<UAbcImportSettings>();
    Settings->ImportType = EAlembicImportType::StaticMesh;

    // 3. 执行导入 (注意：实际使用中需要异步或编辑器上下文)
    // TArray<UObject*> ImportedAssets = AbcImporter.ImportAbcFile(FilePath, Settings);

    UE_LOG(LogTemp, Log, TEXT("ABC Import initiated for: %s"), *FilePath);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryCache` | 必需的插件依赖。用于支持将 Alembic 序列作为几何体缓存（GeometryCache）资产进行导入和播放。 |
| `AlembicLibrary` | 封装底层 Alembic SDK (AlembicFoundation, AlembicOpenGL, HDF5)。 |
| `MeshDescription` | 用于构建和操作导入的网格数据。 |
| `MeshUtilities` | 提供网格处理、LOD 生成等通用工具函数。 |
| `SkeletalMeshDescription` | 处理导入的骨骼网格相关数据。 |
| `AnimationBlueprintLibrary` | 处理导入的动画序列。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式化字符串中32位与64位类型不匹配的编译警告/错误。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏 UE_LOG 统一迁移至新格式的 UE_LOGF。 |
| 2026-02-27 | `8ce7ca27` | AlembicImporter: Fixed import failure when it couldn‘t retrieve velocities even though those should | 修复当文件应包含速度数据但读取失败时，整个导入过程中断的问题。 |
| 2026-02-25 | `74e86b93` | Alembic Import: Fixed out of bouds access (potentially due to negative times). | 修复在读取负时间戳数据时可能导致的数组越界访问问题。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复代码中的死代码（不可达代码）警告。 |

### 维护评价

-   **活跃维护**：该插件创建于 2022 年初（从 Experimental 迁出），近期（2026年）仍有**密集的提交记录**。更新内容主要集中在**错误修复、稳定性提升和代码规范统一**上，表明 Epic Games 团队仍在积极维护该插件，修复用户报告的问题。
-   **稳定性与成熟度**：作为从实验性毕业的核心内容导入插件，其核心功能已相当成熟。近期的更新主要是对边缘情况和编译兼容性的打磨。
-   **推荐使用**：✅ **强烈推荐**。对于任何需要使用 Alembic 格式进行资产交换的 UE5 项目，该插件是官方且成熟的选择。虽然近期更新多为 bug 修复，但这正是其活跃维护和追求稳定的体现。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter/Tests)