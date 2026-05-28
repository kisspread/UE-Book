# Asset Registry Export

> （无描述）

| 属性 | 值 |
|---|---|
| 中文名 | 资产注册表导出 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AssetRegistryExport` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-02-24 |
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/AssetRegistryExport) | |

## 用途

这个插件提供了一个命令行工具（Commandlet），用于将 Unreal Engine 的资产注册表（Asset Registry）数据导出为 SQLite 数据库文件。由于主引擎编辑器模块（`UnrealEd`）本身不依赖于 SQLite 功能，为了避免将不必要的依赖引入核心编辑器模块，Epic 将此功能独立封装为一个编辑器插件。它解决了在项目外部分析资产元数据或自动化流水线中提取资产信息的需求。

## 使用场景

-   **资产分析与报告**：你需要定期导出项目中所有资产的元数据（如类型、路径、标签、大小等）到一个外部数据库，以便使用 SQL 进行复杂查询和生成分析报告。
-   **CI/CD 流水线集成**：在持续集成和交付流程中，需要自动化地提取资产信息，用于自动化检查、依赖分析或资源审计。
-   **工具开发**：开发自定义的资产管理或分析工具，需要访问结构化的资产注册表数据，而不想直接依赖引擎的内存数据结构。

## 蓝图用法

此插件主要通过命令行调用，不提供直接的蓝图节点。资产导出是一个离线处理过程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接蓝图节点） | 此插件提供命令行功能，非运行时蓝图 API | `UAssetRegistryExportCommandlet` |

## C++ 用法

### 头文件引入

```cpp
#include "AssetRegistryExportCommandlet.h"
```

### 基本用法

此插件的核心是 `UAssetRegistryExportCommandlet`。通常不直接实例化，而是通过引擎的命令行参数调用。

**来源文件**: `Engine/Plugins/Editor/AssetRegistryExport/Source/Private/AssetRegistryExportCommandlet.h`

```cpp
// 在命令行中调用此 Commandlet 的示例（非 C++ 代码）
// UE5Editor-Cmd.exe <ProjectPath> -run=AssetRegistryExport -ExportPath=<输出文件路径>.db
```

### 进阶用法

在 C++ 中，你可以通过 `FCommandLine` 或自定义模块启动命令行处理来间接调用此 Commandlet，但这通常用于编辑器扩展或自动化测试框架内部。

## Demo 示例

以下是一个演示如何在自定义编辑器工具中触发 AssetRegistryExport Commandlet 的最小示例。

**MyEditorTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyEditorTool.generated.h"

UCLASS()
class UMyEditorTool : public UObject
{
    GENERATED_BODY()

public:
    /** 调用命令行导出资产注册表到指定 SQLite 文件 */
    UFUNCTION(BlueprintCallable, Category = "Editor Tools")
    static void ExportAssetRegistry(const FString& OutputDatabasePath);
};
```

**MyEditorTool.cpp**
```cpp
#include "MyEditorTool.h"
#include "AssetRegistryExportCommandlet.h" // 包含 Commandlet 的头文件
#include "Misc/CommandLine.h"

void UMyEditorTool::ExportAssetRegistry(const FString& OutputDatabasePath)
{
    // 构建命令行参数字符串
    FString CommandLine = FString::Printf(TEXT("-run=AssetRegistryExport -ExportPath=%s"), *OutputDatabasePath);

    // 注意：在实际使用中，直接调用 Commandlet 主入口比较复杂。
    // 更常见的用法是，用户通过引擎的可执行文件 (UnrealEditor-Cmd.exe) 并带上这些参数来执行导出。
    // 本示例展示其设计意图：它是一个命令行工具，而非库调用。

    // 模拟调用过程（伪代码，说明原理）
    // UAssetRegistryExportCommandlet* Commandlet = NewObject<UAssetRegistryExportCommandlet>();
    // Commandlet->Main(*CommandLine);
    UE_LOG(LogTemp, Warning, TEXT("To export, please run the engine with command: -run=AssetRegistryExport -ExportPath=%s"), *OutputDatabasePath);
}
```

## 模块依赖

从 `.uplugin` 文件分析，使用此插件的模块需要依赖以下内容：

| 模块 | 用途 |
|---|---|
| `SQLiteCore` | 提供 SQLite 数据库的核心读写功能，是本插件将数据写入 `.db` 文件的基础 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了32位和64位格式说明符不匹配的编译问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版日志宏迁移至新版 UE_LOGF 宏 |
| 2025-09-23 | `480c0200` | Don't try to add to an existing database when exporting the AR to SQL. | 修复了向已存在的SQLite数据库追加导出时可能出错的问题 |
| 2025-05-21 | `269aeb1b` | Replaced bool arguments with EFindObjectFlags. | 跟随引擎重构，将布尔参数替换为枚举类型参数 |
| 2025-03-26 | `f4067b30` | Update AssetRegistryExport: | 更新了资产注册表导出功能（具体提交信息被截断） |

### 维护评价

该插件创建于 2022 年，至今约 4 年。从 Git 历史看，**维护状态尚可但更新频率较低**。最近一次实质性功能更新（修复数据库追加问题）在 2025 年 9 月，之后主要是编译兼容性和日志宏的维护性更新。

-   **优点**：功能单一明确，不易出大问题；仍在被维护，没有被明确废弃。
-   **风险/注意**：插件**默认未启用**（`EnabledByDefault: false`），需要用户手动在项目设置中启用。
-   **推荐**：适用于有明确“将资产注册表导出为SQLite”需求的项目或工具流水线。如果仅需运行时查询资产信息，应使用 `AssetRegistry` 模块本身，而非此导出插件。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/AssetRegistryExport)
-   [官方文档]（无）
-   [测试用例]（未发现位于此插件目录下的独立测试文件）