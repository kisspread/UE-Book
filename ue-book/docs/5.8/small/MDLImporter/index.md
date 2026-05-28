# MDL Importer

> Importer for MDL material files.

| 属性 | 值 |
|---|---|
| 中文名 | MDL材质导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MDLImporter` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/MDLImporter) | |

## 用途

该插件用于将 NVIDIA MDL (Material Definition Language) 材质文件导入到 Unreal Engine 中。MDL 是一种用于定义材质属性的高级语言，广泛应用于电影、游戏和工业领域的材质交换。此插件能够解析 MDL 文件，将其转换为 UE 的材质资产，并处理相关的纹理烘焙和材质节点生成。它解决了在不同 DCC 工具间共享和复用复杂材质的需求，使艺术家能够使用标准化的材质定义语言在 UE 中实现高质量的渲染效果。

## 使用场景

- 当你从支持 MDL 的 DCC 软件（如 Maya、3ds Max）导出材质，并希望在 UE 中保持相同的材质外观时。
- 当你需要使用 NVIDIA 提供的 MDL 材质库，将其集成到 UE 项目中。
- 当你需要处理包含程序化纹理（如 Perlin 噪声）或复杂材质属性的 MDL 材质时。

## 蓝图用法

此插件主要通过编辑器界面进行操作，没有提供直接的蓝图可调用节点。导入功能通过编辑器的“导入”按钮或右键菜单中的“导入”选项触发，选择 `.mdl` 文件即可。

## C++ 用法

### 头文件引入

```cpp
#include "MDLImporterModule.h"
#include "MDLMaterialImporter.h"
```

### 基本用法

以下示例展示如何通过 C++ 代码导入 MDL 材质。首先获取 MDL 导入器模块实例，然后使用其 API 导入材质。

```cpp
// 检查 MDL 导入器模块是否可用
if (IMDLImporterModule::IsAvailable())
{
    // 获取模块实例
    IMDLImporterModule& MDLModule = IMDLImporterModule::Get();
    
    // 创建文件导入器
    TUniquePtr<IMdlFileImporter> FileImporter = MDLModule.CreateFileImporter();
    
    // 设置导入选项（例如烘焙分辨率）
    UMDLImporterOptions* Options = GetMutableDefault<UMDLImporterOptions>();
    Options->BakingResolution = 1024;
    
    // 导入 MDL 文件
    FString FilePath = TEXT("/Path/To/Your/File.mdl");
    if (FileImporter->ImportFile(FilePath, Options))
    {
        // 获取导入的材质
        TArray<UMaterialInterface*> Materials = FileImporter->GetImportedMaterials();
        // 处理材质...
    }
}
```
*来源：基于 `MDLImporterModule.h` 和 `MDLMaterialImporter.h` 中的接口分析。*

### 进阶用法

使用 `FMdlMaterialImporter` 直接导入特定的 MDL 材质定义。

```cpp
// 设置导入选项
UMDLImporterOptions Options;
Options.BakingResolution = 2048;
Options.BakingSamples = 4;

// 指定 MDL 模块名和材质定义名
FString MdlModuleName = TEXT("::nvidia::sdk_examples");
FString MdlDefinitionName = TEXT("example_material");

// 准备导入包
UPackage* Package = CreatePackage(nullptr, TEXT("/Game/ImportedMaterials"));
EObjectFlags Flags = RF_Public | RF_Standalone;

// 导入材质
UMaterialInterface* Material = FMdlMaterialImporter::ImportMaterialFromModule(
    Package, 
    Flags, 
    MdlModuleName, 
    MdlDefinitionName, 
    Options
);

if (Material)
{
    // 材质导入成功
    UE_LOG(LogTemp, Log, TEXT("Successfully imported MDL material: %s"), *Material->GetName());
}
```
*来源：基于 `MDLMaterialImporter.h` 中的静态方法分析。*

## Demo 示例

以下是一个完整的、可编译的最小示例，展示如何在编辑器工具中使用 MDL 导入器。

**MDLImporterExample.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MDLImporterModule.h"

class FMDLImporterExample
{
public:
    static void ImportMDLFile(const FString& FilePath);
};
```

**MDLImporterExample.cpp**
```cpp
#include "MDLImporterExample.h"
#include "MDLMaterialImporter.h"
#include "MDLImporterOptions.h"

void FMDLImporterExample::ImportMDLFile(const FString& FilePath)
{
    // 检查模块是否加载
    if (!IMDLImporterModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("MDL Importer module is not available."));
        return;
    }

    // 获取模块实例
    IMDLImporterModule& MDLModule = IMDLImporterModule::Get();
    
    // 设置导入选项
    UMDLImporterOptions* Options = NewObject<UMDLImporterOptions>();
    Options->BakingResolution = 512;
    Options->BakingSamples = 2;
    
    // 创建导入器
    TUniquePtr<IMdlFileImporter> Importer = MDLModule.CreateFileImporter();
    
    // 执行导入
    FFeedbackContext Context;
    if (Importer->ImportFile(FilePath, Options))
    {
        // 获取结果
        TArray<UMaterialInterface*> ImportedMaterials = Importer->GetImportedMaterials();
        UE_LOG(LogTemp, Log, TEXT("Imported %d materials from %s"), ImportedMaterials.Num(), *FilePath);
        
        // 清理
        Importer.Reset();
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to import MDL file: %s"), *FilePath);
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件在编译时通过宏 `USE_MDLSDK` 依赖 NVIDIA MDL SDK，但这不是 UE 模块依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数产生的警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了当参数为64位时使用32位格式说明符的问题，反之亦然。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新的材质转换器工作： |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 重命名 Base<Plugin>.ini 为 Default<Plugin>.ini |

### 维护评价

MDLImporter 插件自 2019 年创建以来一直存在，但维护频率较低。近期的更新主要集中在编译警告修复、日志迁移和格式规范调整等维护性工作，没有重大的功能更新。插件被标记为实验性（`IsBetaVersion: true`）且默认未启用，表明其稳定性可能未达到生产级别要求。尽管如此，最近的提交记录（截至 2026 年）显示它仍被偶尔维护，没有明确的废弃标记。对于需要 MDL 支持的特定项目，它仍然是一个可用的工具，但用户应预期可能存在的限制和未修复的问题。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/MDLImporter)
- 官方文档（无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/MDLImporter/Tests)