# Datasmith CAD Importer

> Collection of tools to work with CAD files.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | CAD数据导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithCADTranslator` (Runtime), `CADInterfaces` (Runtime), `CADLibrary` (Runtime), `DatasmithDispatcher` (Runtime), `ParametricSurface` (Runtime), `WireInterface2025_0` (Runtime), 等共21个模块 |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

`DatasmithCADImporter` 不仅仅是一个简单的文件导入工具，而是一个**完整的 CAD 数据处理管线**。它的核心作用是将各种专业 CAD 软件（如 CATIA, NX, SolidWorks, Alias 等）生成的复杂文件格式（如 .catpart, .jt, .step, .aliaswire），通过一系列转换、优化和场景图构建步骤，转换成 Unreal Engine 的 Datasmith 场景元素（`IDatasmithScene`）。它解决了专业 CAD 数据在结构、精度、材质和历史记录上与游戏引擎实时渲染需求之间的鸿沟，为建筑、工程、制造（AEC/Manufacturing）领域的数字孪生、可视化、虚拟样机等应用提供了数据导入基础。

## 使用场景

- **建筑与工业设计可视化**：设计师使用 CATIA 或 SolidWorks 创建精密的零件和装配体模型，需要将它们导入 UE 进行实时渲染、动画或 VR 评审。
- **产品设计与虚拟展示**：需要将 CAD 模型导入 UE 以创建产品配置器或线上虚拟展厅。
- **数字孪生与仿真**：在构建工厂数字孪生或进行装配仿真时，需要将来自不同 CAD 系统的数十个甚至上百个文件作为统一场景导入。

## 蓝图用法

该插件主要是一个 Runtime 模块，其核心功能（如 `FDatasmithCADTranslator`）是作为 Datasmith 导入器的一部分在后台执行，不直接暴露为可拖拽的蓝图节点。用户通常通过 **Datasmith 导入器** 或 **Datasmith 场景导入** 对话框与之交互。插件提供的核心价值在于其**转换能力**，而非面向设计师的即用型蓝图 API。

### 核心节点

无直接蓝图节点。所有功能通过 `Datasmith CAD Importer` 导入器钩子（Hook）在引擎内部触发。

### 使用示例（蓝图描述）

不适用。用户使用流程为：在 Content Browser 中右键 -> **Import Into Level** 或使用 **Datasmith Scene** 导入按钮，在文件类型选择中支持的 CAD 格式将由该插件的转换器处理。

## C++ 用法

该插件为 Runtime 模块，主要为 Datasmith 导入管线提供服务。开发者可通过 `FDatasmithCADTranslatorModule` 进行模块级操作。

### 头文件引入

```cpp
#include "DatasmithCADTranslatorModule.h"
```

### 基本用法

**获取模块实例与缓存目录**（来源：`Public/DatasmithCADTranslatorModule.h`）。

```cpp
if (FDatasmithCADTranslatorModule::IsAvailable())
{
    FDatasmithCADTranslatorModule& CADTranslatorModule = FDatasmithCADTranslatorModule::Get();
    FString CacheDirectory = CADTranslatorModule.GetCacheDir();
    UE_LOG(LogTemp, Log, TEXT("Datasmith CAD Translator cache directory: %s"), *CacheDirectory);
}
```

### 进阶用法

**编程方式调用 CAD 翻译器**（综合自 `Private/DatasmithCADTranslator.h` 和 `Public/DatasmithSceneGraphBuilder.h` 的设计逻辑）。

通常，你不会直接实例化 `FDatasmithCADTranslator`。更常见的做法是利用其底层的 `FDatasmithSceneGraphBuilder` 来处理场景图。以下为概念性示例，展示了主要类之间的协作流程：

```cpp
// 1. 准备数据：加载CAD文件到场景图归档 (FArchiveSceneGraph)
// 这一步通常由 CADInterfaces 模块和具体转换器完成。
CADLibrary::FArchiveSceneGraph SceneGraphArchive;
// ... 填充 SceneGraphArchive 的代码 ...

// 2. 使用场景图构建器将归档数据转为 Datasmith 场景
TSharedRef<IDatasmithScene> NewScene = FDatasmithScene::Create();
FDatasmithSceneSource SceneSource;
CADLibrary::FImportParameters ImportParameters;

// 假设 CADFileToSceneGraphDescriptionFile 已从缓存加载
TMap<uint32, FString> CADFileToSceneGraphDescriptionFile;
FString CachePath = FDatasmithCADTranslatorModule::Get().GetCacheDir();

FDatasmithSceneGraphBuilder SceneBuilder(
    CADFileToSceneGraphDescriptionFile,
    CachePath,
    NewScene,
    SceneSource,
    ImportParameters
);

// 3. 执行构建，将 CAD 层次结构转换为 Datasmith Actor 和 Mesh 元素
if (SceneBuilder.Build())
{
    // NewScene 现在包含了从 CAD 文件转换而来的完整场景层次
    // 可以将其用于后续的 Datasmith 导入流程或直接使用
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何检查和获取 `DatasmithCADTranslator` 模块。

```cpp
// MyCADManager.h
#pragma once
#include "CoreMinimal.h"

class FMyCADManager
{
public:
    void CheckCADTranslatorAvailability();
    FString GetCADCachedFilePath(const FString& OriginalCADPath) const;
};
```

```cpp
// MyCADManager.cpp
#include "MyCADManager.h"
#include "DatasmithCADTranslatorModule.h" // 核心头文件

void FMyCADManager::CheckCADTranslatorAvailability()
{
    if (FDatasmithCADTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Display, TEXT("Datasmith CAD Translator module is available."));
        FDatasmithCADTranslatorModule& Module = FDatasmithCADTranslatorModule::Get();
        UE_LOG(LogTemp, Display, TEXT("Cache directory: %s"), *Module.GetCacheDir());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Datasmith CAD Translator module is not loaded."));
    }
}

FString FMyCADManager::GetCADCachedFilePath(const FString& OriginalCADPath) const
{
    // 此为示例，实际路径构建逻辑更复杂，通常由插件内部的哈希和路径映射管理
    if (FDatasmithCADTranslatorModule::IsAvailable())
    {
        return FPaths::Combine(FDatasmithCADTranslatorModule::Get().GetCacheDir(),
                               FPaths::GetBaseFilename(OriginalCADPath) + TEXT(".uedat"));
    }
    return FString();
}
```

## 模块依赖

要使用此插件（特别是 `DatasmithCADTranslator` 模块），你的模块需要依赖以下核心模块。常见依赖（如 Core， Engine）已省略。

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | 提供 Datasmith 场景元素的核心接口（`IDatasmithScene`, `IDatasmithActorElement` 等）。 |
| `CADLibrary` | 提供 CAD 数据归档（Archive）、场景图结构体、材质/颜色映射等底层数据类型和工具。 |
| `CADInterfaces` | 提供与外部 CAD 内核（如 TechSoft）的接口层，是转换管道的输入端。 |
| `ParametricSurface` | 提供参数化曲面到网格的转换逻辑。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下 double 常量截断为 float 的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 更新了线框转换器逻辑，使其兼容 Alias 2027。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 升级了底层 TechSoft 库至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 DatasmithCAD 缓存版本标识。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复了函数类型转换警告，提升代码跨编译器兼容性。 |

### 维护评价

- **活跃维护**：尽管插件创建于 2019 年，但 git 记录显示在 2026 年 5 月仍有持续的功能更新（如支持新版 CAD 软件）、依赖升级（TechSoft）和代码质量改进。
- **企业级支持**：作为 Epic Games 官方维护的 Enterprise 插件，它受到持续关注，以适配不断发展的工业软件生态。
- **推荐使用**：对于需要处理标准 CAD 格式的 UE 项目，该插件是官方且成熟的解决方案。虽然默认未启用（`EnabledByDefault: false`），但只需在插件列表中手动启用即可。鉴于其活跃的维护状态和明确的用途，**强烈推荐**有相关需求的项目使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests) (路径推断，实际测试可能位于其他位置)