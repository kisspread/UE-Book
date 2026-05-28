# AxF Importer

> Importer for AxF material files.

| 属性 | 值 |
|---|---|
| 中文名 | AxF材质导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `AxFImporter` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/AxFImporter) | |

## 用途

AxF（Appearance eXchange Format）是一种由 XRite 定义的开放标准，用于描述物理材质的光学外观，常用于汽车、工业设计和产品可视化领域。该插件的核心功能是作为 Unreal Engine 与 AxF 材质文件之间的桥梁。它并非一个简单的文件读取器，而是一个完整的资产导入管线，负责：

1.  **解码与转换**：通过外部 AxF 解码库解析复杂的 AxF 文件数据。
2.  **资产创建**：将解析后的材质数据（包含纹理贴图和着色器参数）转换并生成为 Unreal Engine 可用的 `UMaterial` 资产。
3.  **编辑器集成**：提供标准的 UE 文件导入/重导入工作流和选项配置窗口。

该插件解决了在 Unreal Engine 中直接使用来自专业 CAD 或材质扫描软件（如 X-Rite 的 AxF 捕获系统）的高保真材质数据的问题，避免了手动重建复杂材质。

## 使用场景

-   **汽车可视化**：将用 AxF 格式扫描的真实车漆、内饰材质直接导入 UE 用于实时渲染和虚拟评审。
-   **工业产品设计**：导入具有精确光学属性（如各向异性、清漆层、金属颗粒）的产品外观材质。
-   **材质参考工作流**：作为材质资产的外部源文件格式进行管理和版本控制。

## 蓝图用法

此插件主要通过编辑器菜单和工厂类工作，**没有提供面向蓝图的公开 API**。所有功能均在内容浏览器的右键菜单或文件拖放操作中触发。

## C++ 用法

### 头文件引入

```cpp
#include "AxFImporterModule.h"
```

### 基本用法

通过模块接口访问导入功能。

```cpp
// 来源: Engine/Plugins/Enterprise/AxFImporter/Source/AxFImporter/Public/AxFImporterModule.h

// 1. 检查模块是否可用
if (IAxFImporterModule::IsAvailable())
{
    // 2. 获取模块实例
    IAxFImporterModule& AxFModule = IAxFImporterModule::Get();

    // 3. 检查底层解码库是否已加载
    if (AxFModule.IsLoaded())
    {
        // 4. 创建一个文件导入器实例
        IAxFFileImporter* FileImporter = AxFModule.CreateFileImporter();
        if (FileImporter)
        {
            // 5. 打开并准备导入 AxF 文件
            UAxFImporterOptions* Options = GetDefault<UAxFImporterOptions>();
            if (FileImporter->OpenFile(TEXT("D:/Materials/CarPaint.axf"), *Options))
            {
                // 6. 获取文件中包含的材质数量
                int32 MaterialCount = FileImporter->GetMaterialCountInFile();
                UE_LOG(LogTemp, Log, TEXT("AxF file contains %d materials."), MaterialCount);

                // 7. 导入材质到指定包（Package）中
                // 注意：此处 ParentPackage 和 Flags 需要由完整的导入流程（如 UFactory）提供
                TMap<FString, UMaterialInterface*> ImportedMaterials = FileImporter->GetCreatedMaterials();
                if (FileImporter->ImportMaterials(ParentPackage, RF_Public | RF_Standalone))
                {
                    for (auto& Pair : ImportedMaterials)
                    {
                        UE_LOG(LogTemp, Log, TEXT("Created material '%s' for object '%s'."), *Pair.Value->GetName(), *Pair.Key);
                    }
                }
            }
            delete FileImporter;
        }
    }
}
```

### 进阶用法

实际生产中的导入由 `UAxFImporterFactory` 驱动，它处理了完整的资产创建、事务、用户交互（选项窗口）和分析数据上报。开发者通常不需要直接调用上述接口，而是集成或扩展这个工厂类。

## Demo 示例

以下示例演示如何通过代码模拟一次 AxF 文件的导入过程。

**AxFDemoImporter.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class UMaterialInterface;
class UAxFImporterOptions;

class FAxFDemoImporter
{
public:
    static bool ImportAxFFile(const FString& InFilePath, const FString& InOutputPath);
};
```

**AxFDemoImporter.cpp**
```cpp
#include "AxFDemoImporter.h"
#include "AxFImporterModule.h"
#include "AxFImporterOptions.h"
#include "Engine/Package.h"
#include "UObject/SavePackage.h"

bool FAxFDemoImporter::ImportAxFFile(const FString& InFilePath, const FString& InOutputPath)
{
    if (!IAxFImporterModule::IsAvailable() || !IAxFImporterModule::Get().IsLoaded())
    {
        UE_LOG(LogTemp, Error, TEXT("AxF Importer module is not available or loaded."));
        return false;
    }

    IAxFImporterModule& Module = IAxFImporterModule::Get();
    IAxFFileImporter* Importer = Module.CreateFileImporter();
    if (!Importer)
    {
        return false;
    }

    // 使用默认选项
    const UAxFImporterOptions* Options = GetDefault<UAxFImporterOptions>();

    // 打开文件
    if (!Importer->OpenFile(InFilePath, *Options))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open AxF file: %s"), *InFilePath);
        delete Importer;
        return false;
    }

    // 创建目标包
    FString AssetName = FPaths::GetBaseFilename(InFilePath);
    FString PackageName = FPaths::Combine(InOutputPath, AssetName);
    UPackage* Package = CreatePackage(*PackageName);

    // 定义导入进度回调
    IAxFFileImporter::FProgressFunc Progress = [](const FString& Msg, int MatIdx)
    {
        UE_LOG(LogTemp, Log, TEXT("Progress: Importing material %d - %s"), MatIdx, *Msg);
    };

    // 执行导入
    bool bSuccess = Importer->ImportMaterials(Package, RF_Public | RF_Transactional, Progress);

    if (bSuccess)
    {
        // 保存资产
        Package->MarkPackageDirty();
        FSavePackageArgs SaveArgs;
        SaveArgs.TopLevelFlags = RF_Public | RF_Standalone;
        UPackage::SavePackage(Package, nullptr, *FPackageName::LongPackageNameToFilename(PackageName, FPackageName::GetAssetPackageExtension()), SaveArgs);

        // 输出导入结果
        TMap<FString, UMaterialInterface*> Materials = Importer->GetCreatedMaterials();
        for (const auto& Pair : Materials)
        {
            UE_LOG(LogTemp, Log, TEXT("Successfully imported material asset: %s"), *Pair.Value->GetPathName());
        }
    }
    else
    {
        // 输出错误日志
        TArray<AxFImporterLogging::FLogMessage> Logs = Importer->GetLogMessages();
        for (const auto& Log : Logs)
        {
            UE_LOG(LogTemp, Error, TEXT("AxF Import Error: %s"), *Log.Value);
        }
    }

    delete Importer;
    return bSuccess;
}
```

## 模块依赖

该插件的模块依赖未在提供的 Build.cs 中明确列出，但从其功能可以推断：

| 模块 | 用途 |
|---|---|
| `AxFDecoding` (或类似库) | 核心依赖，负责 AxF 文件格式的解码（通过 `AxFDecodingHandle` 加载）。 |
| `AssetTools`, `AssetRegistry` | UE 资产导入框架的标准依赖。 |

您的模块如果需要集成或扩展 AxF 导入功能，应依赖 `AxFImporter` 模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量转换为浮点数可能产生警告的代码。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至新的 `UE_LOGF` 格式。 |
| 2025-06-10 | `9356818e` | Disable AxF importer for Windows Arm64 | 在 Windows ARM64 平台上禁用了 AxF 导入器。 |

### 维护评价

-   **创建时间**：约 6 年前（2019年）。
-   **更新频率**：更新非常缓慢，最近三次有意义的提交间隔数月到一年。
-   **维护内容**：近期的提交主要是**编译兼容性修复**（警告修复、平台限制）和**代码现代化**（日志宏迁移），**没有新功能或实质性改进**。
-   **状态**：仍被标记为 **Beta (IsBetaVersion: true)** 且 **默认未启用 (EnabledByDefault: false)**，这表明 Epic 可能不认为它是一个面向所有用户的完整、稳定功能。
-   **限制**：仅支持 **Win64 (x64)** 平台，且明确排除了 **Win64:arm64**。
-   **推荐**：**谨慎使用**。该插件适用于有明确 AxF 文件导入需求的 Windows x64 项目，但需认识到其 Beta 状态和长期缺乏功能性更新。在新项目中使用前，建议在目标引擎版本上进行充分测试。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/AxFImporter)
-   [官方文档]() （无）
-   [测试用例]() （未在提供信息中发现）