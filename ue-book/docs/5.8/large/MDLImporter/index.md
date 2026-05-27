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

MDL (Material Definition Language) 是 NVIDIA 主导的材质定义语言标准。`MDLImporter` 插件的核心功能是**调用 NVIDIA 的 MDL SDK，解析并转换 `.mdl` 材质文件，将其转换为 Unreal Engine 的材质资产**。

它解决的核心问题是**跨软件、跨渲染器的材质资产互操作性**。许多 DCC 工具（如 3ds Max, Maya, Blender）和渲染器（如 V-Ray, Redshift）支持 MDL 格式。通过此插件，用户可以将在这些工具中精心调制的 MDL 材质无损地导入到 UE 中，保留其复杂的节点网络和程序化纹理，避免了手动重新创建材质的繁琐工作。

该插件**默认禁用 (`EnabledByDefault: false`)，且处于 Beta 状态 (`IsBetaVersion: true`)**，表明它可能并非为所有用户准备，功能或 API 可能不完全稳定。

## 使用场景

- 你在使用 **NVIDIA Omniverse** 平台，并希望将其中使用 MDL 材质创建的资产（如建筑、工业模型）导入到 Unreal Engine 项目中进行实时渲染或虚拟拍摄。
- 你的美术团队使用 **3ds Max** 或 **Maya**，并依赖 **V-Ray** 或其他支持 MDL 输出的渲染器进行最终渲染。现在需要将这些资产迁移到 UE 中，希望材质外观保持高度一致。
- 你需要导入一些行业标准的 MDL 材质库（例如 NVIDIA 提供的材质库），用于建筑可视化或产品设计展示。
- 你有一个使用 MDL 材质定义复杂表面属性（如车漆、布料、次表面散射）的资产，需要将其导入 UE 并尽可能保留其物理正确的渲染效果。

## 蓝图用法

MDL Importer 主要是编辑器导入功能，其核心逻辑通过 C++ 接口暴露。蓝图中主要涉及配置选项的设置。

### 核心配置对象

| 属性 | 说明 | 所在类 |
|---|---|---|
| `BakingResolution` | 烘焙程序化纹理的分辨率 | `UMDLImporterOptions` |
| `BakingSamples` | 烘焙程序化纹理使用的采样数 | `UMDLImporterOptions` |
| `ResourcesDir` | MDL 资源（纹理、光谱等）的查找路径 | `UMDLImporterOptions` |
| `ModulesDir` | 额外 MDL 模块的查找路径 | `UMDLImporterOptions` |
| `bForceBaking` | 强制将所有贴图烘焙为纹理，而非使用材质节点 | `UMDLImporterOptions` |

### 使用示例（蓝图描述）
此插件的使用通常不在游戏运行时蓝图中，而是在**编辑器工具或自动化导入流程**中。
1.  创建一个 `UMDLImporterOptions` 类的实例。
2.  在蓝图中设置其属性，如调整 `BakingResolution` 以控制纹理质量，或设置 `ResourcesDir` 指向包含纹理的文件夹。
3.  调用 C++ 层封装的导入函数（例如通过 `FMDLImporter` 的接口），传入 `.mdl` 文件路径和配置好的选项对象。
4.  导入过程会创建 `UMaterialInterface` 资产，可在蓝图中接收这些新创建的材质并应用到静态网格体上。

## C++ 用法

### 头文件引入

```cpp
#include "MDLImporterModule.h" // 访问模块接口
#include "MDLImporterOptions.h" // 导入选项
#include "MDLMaterialImporter.h" // 材质导入器
```

### 基本用法

最直接的用法是导入单个 MDL 模块中的材质。

```cpp
// 来源于 Source/MDLImporter/Public/MDLMaterialImporter.h
#include "MDLMaterialImporter.h"
#include "MDLImporterOptions.h"

void ImportSingleMDLMaterial()
{
    // 1. 准备导入选项
    UMDLImporterOptions* Options = NewObject<UMDLImporterOptions>();
    Options->BakingResolution = 1024;
    Options->BakingSamples = 8;
    // Options->ResourcesDir.Path = TEXT("/Game/MDLResources");

    // 2. 定义父包和对象标志
    UPackage* ParentPackage = CreatePackage(nullptr, TEXT("/Game/ImportedMaterials"));
    EObjectFlags Flags = RF_Public | RF_Standalone;

    // 3. 定义 MDL 材质信息（通常来自解析文件）
    FString MDLModuleName = TEXT("::nvidia::sdk_examples::example_mdl");
    FString MDLDefinitionName = TEXT("example_material");

    // 4. 执行导入
    UMaterialInterface* ImportedMaterial = FMdlMaterialImporter::ImportMaterialFromModule(
        ParentPackage,
        Flags,
        MDLModuleName,
        MDLDefinitionName,
        *Options
    );

    if (ImportedMaterial)
    {
        UE_LOG(LogTemp, Log, TEXT("成功导入材质: %s"), *ImportedMaterial->GetName());
        // 可以将材质保存到磁盘
        FAssetRegistryModule::AssetCreated(ImportedMaterial);
        ImportedPackage->MarkPackageDirty();
    }
}
```

### 进阶用法

使用完整的 `FMDLImporter` 流程来导入一个 `.mdl` 文件，该文件可能包含多个材质。

```cpp
// 来源于 Source/MDLImporter/Private/MDLImporter.h (通过 Module 访问)
#include "MDLImporterModule.h"

void ImportMDLFile(const FString& InMDLFilePath)
{
    // 1. 获取 MDL Importer 模块
    if (!IMDLImporterModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("MDLImporter 模块未加载"));
        return;
    }
    IMDLImporterModule& MDLModule = IMDLImporterModule::Get();

    // 2. 创建导入器实例并准备选项
    FMDLImporter Importer(FPaths::ProjectPluginsDir()); // 传入插件路径
    UMDLImporterOptions* Options = NewObject<UMDLImporterOptions>();
    Options->BakingResolution = 2048;
    // ... 设置其他选项

    // 3. 准备材质收集器
    Mdl::FMaterialCollection MaterialCollection;

    // 4. 打开并解析 MDL 文件
    bool bSuccess = Importer.OpenFile(InMDLFilePath, *Options, MaterialCollection);
    if (!bSuccess)
    {
        UE_LOG(LogTemp, Error, TEXT("打开 MDL 文件失败: %s"), *InMDLFilePath);
        // 检查 Importer.GetLogMessages() 获取错误详情
        return;
    }

    // 5. 创建导入材质的目标包
    UPackage* ParentPackage = CreatePackage(nullptr, TEXT("/Game/MDLImported"));
    EObjectFlags Flags = RF_Public | RF_Standalone;

    // 6. 导入所有收集到的材质
    bSuccess = Importer.ImportMaterials(
        ParentPackage,
        Flags,
        MaterialCollection,
        [](const FString& MsgName, int MaterialIndex) {
            UE_LOG(LogTemp, Log, TEXT("正在导入材质 %d: %s"), MaterialIndex, *MsgName);
        }
    );

    if (bSuccess)
    {
        // 获取导入结果
        const TArray<UMaterialInterface*>& CreatedMaterials = Importer.GetCreatedMaterials();
        for (UMaterialInterface* Mat : CreatedMaterials)
        {
            FAssetRegistryModule::AssetCreated(Mat);
            UE_LOG(LogTemp, Log, TEXT("创建的材质: %s"), *Mat->GetName());
        }
        ParentPackage->MarkPackageDirty();
    }
    else
    {
        // 处理错误
        for (const auto& Msg : Importer.GetLogMessages())
        {
            UE_LOG(LogTemp, Warning, TEXT("导入消息: %s"), *Msg.Message);
        }
    }

    // 7. 清理
    Importer.CleanUp();
}
```

## Demo 示例

一个封装了基本 MDL 文件导入功能的编辑器工具类。

```cpp
// MDLImportTool.h
#pragma once

#include "CoreMinimal.h"
#include "MDLImporterModule.h"

class FMDLImportTool
{
public:
    static bool ImportMDLFileToContentBrowser(const FString& MDLFilePath, const FString& TargetPackagePath);

private:
    static void LogMDLMessages(const TArray<MDLImporterLogging::FLogMessage>& Messages);
};
```

```cpp
// MDLImportTool.cpp
#include "MDLImportTool.h"
#include "MDLImporter.h"
#include "MDLImporterOptions.h"
#include "AssetRegistry/AssetRegistryModule.h"

bool FMDLImportTool::ImportMDLFileToContentBrowser(const FString& MDLFilePath, const FString& TargetPackagePath)
{
    // 检查模块可用性
    if (!IMDLImporterModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("MDLImporter 模块不可用"));
        return false;
    }

    // 创建导入器
    FMDLImporter Importer(FPaths::GetPath(FModuleManager::Get().GetModuleFilename(TEXT("MDLImporter"))));

    // 配置选项
    UMDLImporterOptions* Options = NewObject<UMDLImporterOptions>();
    Options->BakingResolution = 1024; // 中等质量，加快示例速度
    Options->BakingSamples = 4;
    // 如果你的MDL文件引用了外部纹理，可能需要设置此路径
    // Options->ResourcesDir.Path = TEXT("C:/MDLResources");

    // 解析文件
    Mdl::FMaterialCollection Materials;
    if (!Importer.OpenFile(MDLFilePath, *Options, Materials))
    {
        UE_LOG(LogTemp, Error, TEXT("无法解析 MDL 文件: %s"), *MDLFilePath);
        LogMDLMessages(Importer.GetLogMessages());
        return false;
    }

    UE_LOG(LogTemp, Log, TEXT("在文件 %s 中发现 %d 个材质"), *MDLFilePath, Materials.Count());

    // 准备包
    UPackage* Package = CreatePackage(nullptr, *TargetPackagePath);
    EObjectFlags Flags = RF_Public | RF_Standalone | RF_Transactional;

    // 执行导入
    bool bImportSuccess = Importer.ImportMaterials(Package, Flags, Materials);
    LogMDLMessages(Importer.GetLogMessages());

    if (bImportSuccess)
    {
        // 保存所有新创建的材质
        for (UMaterialInterface* Material : Importer.GetCreatedMaterials())
        {
            FAssetRegistryModule::AssetCreated(Material);
            UE_LOG(LogTemp, Log, TEXT("已导入并注册材质资产: %s"), *Material->GetPathName());
        }

        // 保存包
        FString PackagePath = Package->GetPathName();
        if (!UPackage::SavePackage(Package, nullptr, EObjectFlags::RF_NoFlags, *PackagePath))
        {
            UE_LOG(LogTemp, Warning, TEXT("保存包 %s 失败"), *PackagePath);
        }
        else
        {
            UE_LOG(LogTemp, Log, TEXT("成功保存材质包至: %s"), *PackagePath);
        }
        return true;
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("MDL 材质导入失败"));
        // 可以尝试清理失败创建的资产
        return false;
    }
}

void FMDLImportTool::LogMDLMessages(const TArray<MDLImporterLogging::FLogMessage>& Messages)
{
    for (const auto& Msg : Messages)
    {
        // 根据消息级别输出到不同的日志频道
        switch (Msg.Level)
        {
        case MDLImporterLogging::ELevel::Error:
            UE_LOG(LogTemp, Error, TEXT("[MDL] %s"), *Msg.Message);
            break;
        case MDLImporterLogging::ELevel::Warning:
            UE_LOG(LogTemp, Warning, TEXT("[MDL] %s"), *Msg.Message);
            break;
        default:
            UE_LOG(LogTemp, Log, TEXT("[MDL] %s"), *Msg.Message);
            break;
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MDLImporter` | 插件核心模块，提供导入器逻辑和接口。 |
| `MDLCore` (如果存在) | 可能封装了基础的 MDL SDK 调用（具体依赖需查看 Build.cs）。 |
| `MaterialEditor` | 用于创建和编辑材质资产的编辑器功能。 |
| `UnrealEd` | 编辑器核心框架。 |
| `AssetRegistry` | 用于注册新创建的资产，使其在内容浏览器中可见。 |
| `ApplicationCore` | 可能用于平台相关的文件系统操作。 |
| `Projects` | 用于获取插件路径等项目信息。 |

**注意**：该插件严重依赖**外部的 NVIDIA MDL SDK**（通常通过 `USE_MDLSDK` 宏和外部库引入）。具体集成方式需查看其 Build.cs 文件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数时产生的编译警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式说明符与64位参数不匹配的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的日志宏 `UE_LOG` 迁移为 `UE_LOGF`。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新材质转换器的工作提交。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将配置文件名从 `Base<Plugin>.ini` 重命名为 `Default<Plugin>.ini`。 |

### 维护评价

**综合评价：维护不活跃，存在使用风险。**

1.  **创建时间久远**：插件创建于 2019 年，至今已超过 6 年。
2.  **更新频率低**：近期的更新主要是**编译警告修复、日志宏迁移和配置文件重命名**等维护性工作。`1adb9f68` 提交描述为“新材质转换器工作”，暗示可能有重要重构，但细节不明。
3.  **状态特殊**：插件**默认禁用且标记为 Beta 版**，这表明 Epic 官方可能认为其尚不适合大规模生产使用，或者需要特定的环境（如安装了 MDL SDK）才能启用。
4.  **依赖风险**：其核心功能依赖于外部的 NVIDIA MDL SDK，这增加了配置的复杂性和潜在的分发问题。
5.  **无近期实质性功能更新**：没有看到针对 UE5 新特性（如 Nanite, Lumen）的适配或重大功能增强。

**建议**：
-   **谨慎使用**：除非你的项目有明确且强烈的 MDL 材质互操作需求，并且愿意承担 Beta 功能可能带来的不稳定风险，否则不建议在核心项目中使用。
-   **技术验证先行**：如果决定使用，务必先在单独的项目中进行充分的技术验证，确认其与你的 UE 版本、MDL SDK 版本的兼容性，以及最终生成的材质质量。
-   **准备备选方案**：考虑将 MDL 材质在 DCC 工具中预先烘焙为标准的 PBR 贴图（如 BaseColor, Normal, ORM），然后在 UE 中手动重建材质，这是一种更稳定、可控的迁移方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/MDLImporter)
- [NVIDIA MDL SDK 官方文档](https://developer.nvidia.com/mdl-sdk) (外部依赖，非插件自带文档)
- [测试用例] (提供的源码片段中未显示独立的测试文件路径)