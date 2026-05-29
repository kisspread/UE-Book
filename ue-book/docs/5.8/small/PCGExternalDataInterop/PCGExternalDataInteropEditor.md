# PCG External Data Interop

> Extra plugin for Procedural Content Generation Framework interacting with external data formats.

| 属性 | 值 |
|---|---|
| 中文名 | PCG外部数据互操作 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PCGExternalDataInterop` (Runtime), `PCGExternalDataInteropEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-08-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGExternalDataInterop) | |

## 用途

本插件为 UE5 的 PCG（程序化内容生成）框架提供与 **Alembic**（.abc）外部文件格式的互操作能力。它解决了以下问题：

- **几何数据导入**：将 Alembic 格式的几何/点云数据读取并转换为 PCG 可使用的数据资产（PCG Data Asset）
- **坐标系转换**：提供左手/右手坐标系翻转（Handedness Flip）及旋转 Swizzle 等设置，适配不同 DCC 工具导出的坐标系差异
- **属性映射**：支持将 Alembic 文件中的自定义属性映射到 PCG 的属性选择器（AttributePropertyInputSelector），实现数据字段的灵活对接

本质上，这是一个"桥梁"插件——让美术在 Houdini、Blender、Maya 等 DCC 工具中生成的程序化数据（散点、植被分布、地形特征等）能以 Alembic 文件为载体，无缝导入 UE5 的 PCG 流水线中使用。

## 使用场景

- 你在 Houdini 中用程序化方法生成了植被/建筑散点分布（Alembic 格式），想导入 UE5 PCG 图中作为输入数据
- 你需要将外部点云数据（带自定义属性如密度、朝向等）转换为 PCG 可读的格式进行后续处理
- 你在做一个开放世界项目，使用 DCC 工具预计算大规模环境分布数据，希望通过 Alembic 管道导入 PCG

## 蓝图用法

本插件通过 `UPCGLoadAlembicFunctionLibrary` 提供蓝图节点，属于 `PCG|IO` 分类。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExportAlembicFileToPCG` | 将 Alembic 文件导出为 PCG Data Asset（推荐） | `UPCGLoadAlembicFunctionLibrary` |
| `SetupFromStandard` | 根据预设标准快速配置 Alembic 加载参数 | `UPCGLoadAlembicFunctionLibrary` |
| ~~`LoadAlembicFileToPCG`~~ | ~~已废弃~~，请使用 `ExportAlembicFileToPCG` | `UPCGLoadAlembicFunctionLibrary` |

### 关键结构体

| 结构体 | 说明 |
|---|---|
| `FPCGLoadAlembicBPData` | Alembic 加载配置，包含文件路径、坐标转换设置、属性映射表 |
| `FPCGAssetExporterParameters` | 资产导出参数（来自 PCG 框架） |

### 使用示例（蓝图描述）

**导入 Alembic 文件并导出为 PCG 资产：**

1. 创建一个 `FPCGLoadAlembicBPData` 变量
2. 设置 `AlembicFilePath` 指向你的 .abc 文件（文件选择器会自动过滤 .abc 扩展名）
3. 根据需要配置 `ConversionSettings`（坐标转换）和 `bConversionFlipHandedness`（手性翻转）
4. 在 `AttributeMapping` 中映射 Alembic 自定义属性到 PCG 属性选择器
5. 调用 `ExportAlembicFileToPCG` 节点，传入设置和导出参数
6. 生成的 PCG Data Asset 可直接拖入 PCG 图作为输入

**快速预设配置：**

调用 `SetupFromStandard` 节点，传入 `EPCGLoadAlembicStandardSetup` 枚举值，可一键填充常用的转换参数，无需手动配置每个字段。

## C++ 用法

### 头文件引入

```cpp
#include "PCGLoadAlembic.h"
```

### 基本用法

从 `PCGLoadAlembic.h` 提取，展示如何在 C++ 中配置并导出 Alembic 文件到 PCG 资产。

```cpp
// 配置 Alembic 加载参数
FPCGLoadAlembicBPData AlembicSettings;
AlembicSettings.AlembicFilePath.FilePath = TEXT("/Game/Alembics/vegetation_scatter.abc");

// 配置坐标系转换（如果 DCC 工具使用右手坐标系）
AlembicSettings.bConversionFlipHandedness = true;

// 映射自定义属性：Alembic 中的 "pscale" 属性映射到 PCG 的 Density 属性
AlembicSettings.AttributeMapping.Add(
    TEXT("pscale"),
    FPCGAttributePropertyInputSelector::CreateAttributeSelector(TEXT("Density"))
);

// 导出为 PCG Data Asset
FPCGAssetExporterParameters ExportParams;
ExportParams.bSaveOnExport = true;
UPCGLoadAlembicFunctionLibrary::ExportAlembicFileToPCG(AlembicSettings, ExportParams);
```

### 进阶用法

使用标准预设快速配置，适合需要适配特定 DCC 工具输出格式的场景：

```cpp
FPCGLoadAlembicBPData AlembicSettings;
AlembicSettings.AlembicFilePath.FilePath = TEXT("/Game/Alembics/terrain_points.abc");

// 使用标准预设初始化（例如匹配 Houdini 的默认导出配置）
UPCGLoadAlembicFunctionLibrary::SetupFromStandard(AlembicSettings, EPCGLoadAlembicStandardSetup::Default);

// 预设之外的自定义调整
AlembicSettings.bConversionFlipHandedness = true;

// 多属性批量映射
AlembicSettings.AttributeMapping.Add(TEXT("Cd"), FPCGAttributePropertyInputSelector::CreateAttributeSelector(TEXT("Color")));
AlembicSettings.AttributeMapping.Add(TEXT("orient"), FPCGAttributePropertyInputSelector::CreateAttributeSelector(TEXT("Orientation")));

UPCGLoadAlembicFunctionLibrary::ExportAlembicFileToPCG(AlembicSettings);
```

## Demo 示例

以下是一个可编译的最小示例，展示如何在编辑器工具中调用 Alembic 导入功能：

```cpp
// MyAlembicImporter.h
#pragma once

#include "CoreMinimal.h"
#include "PCGLoadAlembic.h"
#include "MyAlembicImporter.generated.h"

UCLASS(BlueprintType)
class UMyAlembicImporter : public UObject
{
    GENERATED_BODY()

public:
    /** 从指定路径导入 Alembic 文件到 PCG Data Asset */
    UFUNCTION(BlueprintCallable, Category = "MyTools|PCG")
    static bool ImportAlembicToPCGAsset(const FString& AlembicPath, const FString& OutputAssetPath);

protected:
    /** 配置默认导入参数 */
    static FPCGLoadAlembicBPData BuildDefaultSettings(const FString& AlembicPath);
};
```

```cpp
// MyAlembicImporter.cpp
#include "MyAlembicImporter.h"

FPCGLoadAlembicBPData UMyAlembicImporter::BuildDefaultSettings(const FString& AlembicPath)
{
    FPCGLoadAlembicBPData Settings;
    Settings.AlembicFilePath.FilePath = AlembicPath;
    Settings.bConversionFlipHandedness = false;

    // 示例：将 Alembic 的 "N" 法线属性映射到 PCG 法线
    Settings.AttributeMapping.Add(
        TEXT("N"),
        FPCGAttributePropertyInputSelector::CreateAttributeSelector(TEXT("Normal"))
    );

    return Settings;
}

bool UMyAlembicImporter::ImportAlembicToPCGAsset(const FString& AlembicPath, const FString& OutputAssetPath)
{
    if (AlembicPath.IsEmpty() || !FPaths::FileExists(AlembicPath))
    {
        UE_LOG(LogTemp, Warning, TEXT("Alembic file not found: %s"), *AlembicPath);
        return false;
    }

    FPCGLoadAlembicBPData Settings = BuildDefaultSettings(AlembicPath);

    FPCGAssetExporterParameters ExportParams;
    ExportParams.bSaveOnExport = true;

    UPCGLoadAlembicFunctionLibrary::ExportAlembicFileToPCG(Settings, ExportParams);
    return true;
}
```

## 模块依赖

从 Build.cs 和源码分析，使用本插件需要以下依赖：

| 模块 | 用途 |
|---|---|
| `PCG` | PCG 框架核心，提供 `UPCGDataAsset`、`FPCGDataCollection`、`UPCGAssetExporter` 等基类和类型 |
| `PCGExternalDataInterop` | 本插件的基础 Runtime 模块（若使用编辑器功能需依赖 Editor 模块） |
| `AlembicLib` | Alembic 文件格式解析库，提供 `FAbcConversionSettings` 等转换类型 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 统一日志宏格式，迁移到新的 UE_LOGF 宏 |
| 2026-01-09 | `49c11077` | [UObject] | UObject 相关的通用维护/重构改动 |
| 2025-09-23 | `e22e769b` | [PCG] Better management of windows headers wrt alembic files | 改善 Windows 头文件与 Alembic 头文件的包含顺序管理 |
| 2025-09-23 | `68b1d8a9` | [PCG] Moved code to implementation file for better isolation. Also removed GetObject define that cou | 将代码移至实现文件以更好隔离，移除可能冲突的 GetObject 宏定义 |
| 2025-05-14 | `6bd1bdeb` | Fix compile error because winnt.h is included by Alembic includes, which redefines MemoryBarrier, th | 修复 Alembic 头文件包含 winnt.h 导致的 MemoryBarrier 宏重定义编译错误 |

### 维护评价

- **活跃维护中**：最近一次实质性更新在 2026-04-14，持续保持更新
- **近期改动以稳定性和兼容性为主**：最近的 commit 主要集中在头文件包含顺序、宏冲突修复、日志格式迁移等工程层面的改进，说明核心功能已趋于稳定
- **年轻插件**：创建于 2024 年 8 月，仅约 1 年历史，属于 PCG 框架较新的扩展组件
- **Windows 平台注意事项**：多次 commit 涉及 `winnt.h` 和 Alembic 头文件的冲突问题，Windows 平台编译时需注意头文件包含顺序
- **推荐使用**：如果你的 PCG 工作流需要导入 DCC 工具生成的 Alembic 数据，这是官方提供的标准互操作方案，值得使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGExternalDataInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)