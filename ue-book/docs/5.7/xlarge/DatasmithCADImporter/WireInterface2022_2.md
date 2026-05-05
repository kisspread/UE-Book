# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

DatasmithCADImporter 是 Datasmith 导入管线的 CAD 格式扩展插件，专门负责将工业 CAD 文件（如 Autodesk Alias `.wire`、Rhino `.3dm`、PLMXML 等）转换为 UE 可用的几何体和材质数据。

该插件解决的核心问题是：**工业 CAD 软件使用的参数化曲面（NURBS）和精确几何体无法直接被游戏引擎的三角面片渲染管线使用**。插件通过以下流程完成转换：

1. **格式解析**：通过各 Translator 模块读取原始 CAD 文件格式
2. **曲面细分**：将 NURBS 参数化曲面转换为三角网格（Tessellation）
3. **材质映射**：保留 CAD 文件中的图层/材质信息
4. **分发处理**：通过 Dispatcher 模块实现多进程/异步导入，处理大型装配体

插件默认不启用（`EnabledByDefault=false`），需要在项目设置中手动开启，因为它依赖第三方库（TechSoft、OpenNurbs）且仅面向企业级用户。

## 模块架构

```
DatasmithCADImporter/
├── CADInterfaces          ← TechSoft SDK 封装层（CAD 格式通用接口）
├── CADLibrary             ← CAD 数据结构与工具库
├── CADTools               ← CAD 几何处理工具
├── CADKernelSurface       ← CAD 内核曲面处理
├── ParametricSurface      ← 参数化曲面细分引擎
├── ParametricSurfaceExtension ← 曲面细分扩展
├── DatasmithCADTranslator ← Datasmith 翻译器主入口
├── DatasmithDispatcher    ← 多进程导入调度器
├── DatasmithOpenNurbsTranslator ← Rhino/OpenNurbs (.3dm) 翻译器
├── DatasmithPLMXMLTranslator   ← PLMXML 翻译器
├── DatasmithWireTranslator     ← Alias .wire 翻译器（主模块）
└── WireInterface*         ← Alias SDK 版本适配层（2020~2026）
```

### WireInterface 版本模块说明

`WireInterface2020` 到 `WireInterface2026_0` 是一组版本适配模块，每个模块封装了对应年份版本的 Autodesk Alias `.wire` SDK。运行时根据目标文件的版本自动选择合适的模块加载。这种设计避免了 SDK 版本冲突，同时支持向后兼容旧版 `.wire` 文件。

## 使用场景

- 你在汽车/工业设计领域工作，需要将 Autodesk Alias 的 `.wire` 模型导入 UE → 启用此插件
- 你需要从 Rhino 导入 `.3dm` 文件并保留 NURBS 曲面精度 → 使用 DatasmithOpenNurbsTranslator
- 你需要从 PLM（产品生命周期管理）系统导入 PLMXML 格式的产品数据 → 使用 DatasmithPLMXMLTranslator
- 你有大型 CAD 装配体需要高效导入 → DatasmithDispatcher 提供多进程支持
- 你使用 Datasmith 导入 `.udatasmith` 文件且源数据来自 CAD 软件 → 此插件提供底层翻译能力

## 蓝图用法

此插件主要作为 Datasmith 导入管线的底层组件，不直接暴露蓝图节点。CAD 文件的导入通过以下方式触发：

- **编辑器菜单**：File → Import Into Level → 选择 `.wire` / `.3dm` / `.udatasmith` 文件
- **Datasmith 导入 Actor**：使用 `UDatasmithImportContext` 配置导入参数
- **Python 脚本自动化**：通过 `unreal.DatasmithImportLibrary` 进行批量导入

## C++ 用法

### 头文件引入

```cpp
#include "WireInterfaceModule.h"
```

### 基本用法 — 模块可用性检查

```cpp
// 检查 Wire 翻译器模块是否已加载
namespace UE_DATASMITHWIRETRANSLATOR_NAMESPACE
{
    if (FDatasmithWireTranslatorModule::IsAvailable())
    {
        FDatasmithWireTranslatorModule& WireModule = FDatasmithWireTranslatorModule::Get();
        FString TempDir = WireModule.GetTempDir();
        // 使用临时目录进行文件转换...
    }
}
```

### 进阶用法 — 通过 Datasmith 管线导入 CAD 文件

```cpp
// 通过 Datasmith 框架导入 CAD 文件（间接使用此插件）
#include "DatasmithImportFactory.h"
#include "DatasmithImportContext.h"

UDatasmithImportFactory* Factory = NewObject<UDatasmithImportFactory>();
// 插件注册后，Datasmith 管线会自动选择合适的 Translator
// .wire 文件 → DatasmithWireTranslator
// .3dm 文件 → DatasmithOpenNurbsTranslator
// PLMXML    → DatasmithPLMXMLTranslator
```

## Demo 示例

此插件为底层导入管线组件，不提供独立的运行时 Demo。典型使用方式是在编辑器中通过 Datasmith 导入流程调用：

```cpp
// MyCADImporter.h
#pragma once

#include "CoreMinimal.h"

class FMyCADBatchImporter
{
public:
    /** 批量导入目录下的所有 CAD 文件 */
    static void ImportCADDirectory(const FString& DirectoryPath, const FString& DestinationPath);
};
```

```cpp
// MyCADImporter.cpp
#include "MyCADImporter.h"
#include "DatasmithImportFactory.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Misc/Paths.h"

void FMyCADBatchImporter::ImportCADDirectory(const FString& DirectoryPath, const FString& DestinationPath)
{
    // 支持的 CAD 文件扩展名
    TArray<FString> Extensions = { TEXT("wire"), TEXT("3dm"), TEXT("plmxml") };

    for (const FString& Ext : Extensions)
    {
        TArray<FString> FoundFiles;
        IFileManager::Get().FindFilesRecursive(
            FoundFiles, *DirectoryPath, *(TEXT("*.") + Ext), true, false
        );

        for (const FString& FilePath : FoundFiles)
        {
            UE_LOG(LogTemp, Log, TEXT("Importing CAD file: %s"), *FilePath);
            // 实际导入需通过 UDatasmithStaticMeshImportUI 或编辑器工具
            // 此处为概念示例
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TechSoft` | TechSoft 3D SDK，提供 CAD 格式（STEP、IGES、JT、CATIA 等）的读取能力 |
| `OpenNurbs6` | OpenNurbs 库，提供 Rhino `.3dm` 文件的读取能力 |
| `DatasmithCore` | Datasmith 核心框架，提供翻译器注册和数据模型 |

## 维护状态

### 近期更新

```
- 90f00dd86ae6 Added support for Alias 2026.0
  → 新增 Alias 2026.0 版本的 WireInterface 模块，持续跟进最新 Alias SDK
- 39994edb437c [Wire] Corrected missing incrementation
  → 修复材质分配循环中缺少递增的 bug，导致所有 section 使用相同材质
- 61d36ec7677f [Wire] Fixed missing colors when using group option
  → 修复使用 group 选项时颜色丢失的问题，简化了材质分配逻辑
```

### 维护评价

- **活跃维护**：插件仍在持续更新，最近的 commit 新增了 Alias 2026.0 支持，说明 Epic 仍在跟进最新 CAD 软件版本
- **企业级定位**：作为 Enterprise 分类的插件，面向汽车、航空、建筑等行业的专业用户
- **版本适配策略成熟**：WireInterface 的多版本模块设计表明该插件有长期维护的架构规划
- **已知限制**：
  - 默认不启用，需要手动开启
  - 依赖第三方商业库（TechSoft），可能需要额外许可证
  - 仅 Runtime 模块，不提供编辑器扩展 UI
- **推荐使用**：如果你的工作流涉及工业 CAD 文件导入 UE，这是官方推荐的解决方案，维护状态良好

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)