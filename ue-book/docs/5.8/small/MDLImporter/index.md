# MDL Importer

> Importer for MDL material files.

| 属性 | 值 |
|---|---|
| 中文名 | MDL 材质导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质函数资产、纹理资产） |
| 模块 | `MDLImporter` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/MDLImporter) | |

## 用途

MDL Importer 是一个编辑器插件，用于将 NVIDIA Material Definition Language (MDL) 材质文件导入为 Unreal Engine 的 `UMaterial` 资产。

MDL 是一种由 NVIDIA 定义的行业标准材质描述语言，广泛用于光线追踪渲染器（如 Iray、V-Ray 等）中。该插件的核心功能包括：

1. **解析 MDL 材质定义**：通过 NVIDIA MDL SDK 加载 `.mdl` 文件，解析材质模块中的材质定义和实例
2. **材质蒸馏（Distillation）**：将 MDL 的复杂材质图（BSDF 树）蒸馏转换为 Unreal 的 PBR 材质属性（BaseColor、Metallic、Roughness、Normal 等）
3. **程序纹理烘焙**：将 MDL 中的程序化纹理（程序化噪声、棋盘格等）烘焙为位图纹理资产
4. **材质节点图生成**：将 MDL 的函数调用链转换为 Unreal 材质编辑器中的材质表达式节点图，尽可能保留可编辑性而非全部烘焙
5. **材质函数生成**：自动创建所需的材质函数资产（如噪声函数、混合函数、坐标投影函数等）

该插件解决了在 Unreal 中使用 MDL 材质生态的互操作性问题，使影视和建筑可视化领域的艺术家能够在 UE 中复用基于 MDL 的材质资产。

**重要限制**：插件标记为 Beta 版本且默认不启用，表明它仍处于实验阶段。功能依赖 `USE_MDLSDK` 编译宏，需要 NVIDIA MDL SDK 才能正常工作。

## 使用场景

- 你在做一个建筑可视化项目，资产来自支持 MDL 的 DCC 工具（如 3ds Max + V-Ray）→ 用 MDLImporter 导入 `.mdl` 材质
- 你在做一个影视级渲染项目，需要复用 Iray/MaterialX 生态中的 MDL 材质 → 用 MDLImporter 转换到 UE 材质
- 你有一个 MDL 材质库（如 NVIDIA vMaterials），想在 UE 中使用 → 用 MDLImporter 批量导入
- 你需要保留 MDL 材质的程序化纹理生成逻辑而非仅烘焙贴图 → 插件会尝试生成材质节点图

## 蓝图用法

本插件主要面向编辑器工作流，不暴露运行时蓝图节点。以下 `UCLASS` 属性可通过编辑器项目设置（Project Settings）访问：

### 配置选项

| 属性 | 类型 | 说明 | 范围 |
|---|---|---|---|
| `BakingResolution` | `uint32` | 程序纹理烘焙分辨率 | 128 ~ 16384 |
| `BakingSamples` | `uint32` | 烘焙采样数（MSAA） | 1 ~ 16 |
| `ResourcesDir` | `FDirectoryPath` | MDL 资源（纹理、光谱配置等）搜索路径 | — |
| `ModulesDir` | `FDirectoryPath` | 额外 MDL 模块搜索路径 | — |
| `MetersPerSceneUnit` | `float` | 场景单位与米的换算比 | 0.01 ~ 1000 |
| `bForceBaking` | `bool` | 强制烘焙所有贴图（不使用材质节点） | — |

配置路径：**Project Settings → Engine → MDL Importer**

### 编辑器导入流程

1. 在 Content Browser 中右键 → **Import**
2. 选择 `.mdl` 文件
3. 插件自动解析 MDL 模块中的所有材质定义
4. 为每个材质创建 `UMaterial` 资产
5. 烘焙程序纹理并创建 `UTexture2D` 资产

### 重新导入

导入后的材质支持重新导入（Reimport），会更新材质属性和烘焙纹理。

## C++ 用法

### 头文件引入

```cpp
#include "MDLImporterModule.h"
#include "MDLImporterOptions.h"
#include "MDLMaterialImporter.h"
```

### 基本用法

通过模块接口导入 MDL 材质：

```cpp
// 来源: Source/MDLImporter/Public/MDLMaterialImporter.h
#include "MDLMaterialImporter.h"

// 添加 MDL 搜索路径
FScopedSearchPath SearchPath(TEXT("C:/MDL_Libraries/vMaterials"));

// 设置导入选项
UMDLImporterOptions* Options = NewObject<UMDLImporterOptions>();
Options->BakingResolution = 2048;
Options->BakingSamples = 4;
Options->MetersPerSceneUnit = 1.0f;
Options->bForceBaking = false;

// 导入单个材质
UPackage* ParentPackage = CreatePackage(nullptr, TEXT("/Game/Materials/ImportedMaterial"));
UMaterialInterface* ImportedMaterial = FMdlMaterialImporter::ImportMaterialFromModule(
    ParentPackage,
    RF_Public | RF_Standalone,
    TEXT("path/to/module"),           // MDL 模块名
    TEXT("material_definition_name"), // 材质定义名
    *Options
);
```

### 进阶用法

通过完整的导入管线批量导入：

```cpp
// 来源: Source/MDLImporter/Private/MDLImporter.h
#include "MDLImporterModule.h"

// 获取导入器模块
IMDLImporterModule& Module = IMDLImporterModule::Get();
FMDLImporter& Importer = Module.GetMDLImporter();

// 配置导入选项
UMDLImporterOptions Options;
Options.BakingResolution = 4096;
Options.BakingSamples = 8;
Options.ResourcesDir.Path = TEXT("C:/MDL_Resources");
Options.ModulesDir.Path = TEXT("C:/MDL_Modules");

// 加载 MDL 模块中的材质
Mdl::FMaterialCollection Materials;
bool bSuccess = Importer.OpenFile(TEXT("C:/Materials/car_paint.mdl"), Options, Materials);

if (bSuccess)
{
    // 获取材质列表信息
    for (int32 i = 0; i < Materials.Count(); ++i)
    {
        const Mdl::FMaterial& Mat = Materials[i];
        UE_LOG(LogTemp, Log, TEXT("Found material: %s (ID: %u)"), *Mat.Name, Mat.Id);
    }

    // 创建导入材质资产
    UPackage* ParentPackage = CreatePackage(nullptr, TEXT("/Game/Materials/MDL"));
    auto ProgressCallback = [](const FString& MsgName, int32 Index)
    {
        UE_LOG(LogTemp, Log, TEXT("Importing %s (%d)"), *MsgName, Index);
    };

    Importer.ImportMaterials(ParentPackage, RF_Public | RF_Standalone, Materials, ProgressCallback);

    // 获取创建的材质
    const TArray<UMaterialInterface*>& CreatedMaterials = Importer.GetCreatedMaterials();
    for (UMaterialInterface* Material : CreatedMaterials)
    {
        UE_LOG(LogTemp, Log, TEXT("Created material asset: %s"), *Material->GetName());
    }

    // 检查日志消息
    for (const auto& Msg : Importer.GetLogMessages())
    {
        UE_LOG(LogTemp, Warning, TEXT("MDL Import: %s"), *Msg.Message);
    }
}

// 清理
Importer.CleanUp();
```

## Demo 示例

一个完整的 MDL 材质导入工具类：

```cpp
// MDLImporterTool.h
#pragma once

#include "CoreMinimal.h"
#include "MDLImporterModule.h"
#include "MDLImporterOptions.h"
#include "MDLMaterialImporter.h"

class FMDLImporterTool
{
public:
    /** 检查 MDL SDK 是否可用 */
    static bool IsMDLAvailable()
    {
        return IMDLImporterModule::IsAvailable() && IMDLImporterModule::Get().IsLoaded();
    }

    /** 配置导入选项 */
    static UMDLImporterOptions* CreateDefaultOptions()
    {
        UMDLImporterOptions* Options = NewObject<UMDLImporterOptions>();
        Options->BakingResolution = 2048;
        Options->BakingSamples = 4;
        Options->MetersPerSceneUnit = 1.0f;
        Options->bForceBaking = false;
        return Options;
    }

    /** 导入单个 MDL 文件并返回创建的材质 */
    static TArray<UMaterialInterface*> ImportMDLFile(
        const FString& MDLFilePath,
        const FString& OutputPath,
        const UMDLImporterOptions* Options = nullptr)
    {
        TArray<UMaterialInterface*> Results;

        if (!IsMDLAvailable())
        {
            UE_LOG(LogTemp, Error, TEXT("MDL SDK is not available. Ensure the MDLImporter plugin is enabled and MDL SDK is installed."));
            return Results;
        }

        IMDLImporterModule& Module = IMDLImporterModule::Get();
        FMDLImporter& Importer = Module.GetMDLImporter();

        // 使用默认选项或自定义选项
        UMDLImporterOptions* UseOptions = Options ? const_cast<UMDLImporterOptions*>(Options) : CreateDefaultOptions();

        // 加载材质
        Mdl::FMaterialCollection Materials;
        if (!Importer.OpenFile(MDLFilePath, *UseOptions, Materials))
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to open MDL file: %s"), *MDLFilePath);
            return Results;
        }

        // 创建输出包
        FString PackageName = FPaths::Combine(OutputPath, FPaths::GetBaseFilename(MDLFilePath));
        UPackage* Package = CreatePackage(nullptr, *PackageName);

        // 执行导入
        if (Importer.ImportMaterials(Package, RF_Public | RF_Standalone, Materials))
        {
            Results = Importer.GetCreatedMaterials();
            UE_LOG(LogTemp, Log, TEXT("Successfully imported %d materials from %s"),
                Results.Num(), *MDLFilePath);
        }

        // 报告日志
        for (const auto& Msg : Importer.GetLogMessages())
        {
            UE_LOG(LogTemp, Warning, TEXT("MDL: %s"), *Msg.Message);
        }

        Importer.CleanUp();
        return Results;
    }

    /** 使用作用域搜索路径导入材质 */
    static UMaterialInterface* ImportSingleMaterial(
        UPackage* ParentPackage,
        const FString& SearchPath,
        const FString& ModuleName,
        const FString& MaterialName)
    {
        // FScopedSearchPath 在作用域结束时自动移除搜索路径
        FMdlMaterialImporter::FScopedSearchPath ScopedPath(SearchPath);

        UMDLImporterOptions* Options = CreateDefaultOptions();

        return FMdlMaterialImporter::ImportMaterialFromModule(
            ParentPackage,
            RF_Public | RF_Standalone,
            ModuleName,
            MaterialName,
            *Options
        );
    }
};
```

```cpp
// MDLImporterTool.cpp - 使用示例
#include "MDLImporterTool.h"

void ExampleUsage()
{
    // 1. 导入整个 MDL 文件
    TArray<UMaterialInterface*> Materials = FMDLImporterTool::ImportMDLFile(
        TEXT("C:/Materials/car_paint.mdl"),
        TEXT("/Game/Materials/CarPaint")
    );

    // 2. 导入单个材质（使用搜索路径）
    UPackage* Pkg = CreatePackage(nullptr, TEXT("/Game/Materials/WallPaint"));
    UMaterialInterface* WallMat = FMDLImporterTool::ImportSingleMaterial(
        Pkg,
        TEXT("C:/MDL_Libraries/vMaterials"),
        TEXT("wall_paint"),
        TEXT("matte_wall")
    );

    // 3. 将文件路径转换为 MDL 模块名
    FString ModuleName = UE::Mdl::Util::ConvertFilePathToModuleName(TEXT("C:/MDL/Libraries/wood.mdl"));
    // 返回类似 "::Libraries::wood" 的模块名
}
```

## 模块依赖

MDLImporter 模块的依赖关系（Source/MDLImporter/MDLImporter.Build.cs）：

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | 插件仅依赖 Unreal 标准模块和 NVIDIA MDL SDK（通过编译宏 `USE_MDLSDK` 控制） |

**外部依赖**：
- **NVIDIA MDL SDK**：通过 `USE_MDLSDK` 编译宏条件编译。当 SDK 不可用时，插件模块仍会加载但功能不可用（接口返回空值）
- **MDL SDK 动态库**（`nv_freeimage` 等）：运行时通过 `DsoHandle` 加载

**编译条件**：
```cpp
#ifdef USE_MDLSDK
// 完整功能实现
#else
// 空壳实现，接口调用返回默认值
#endif
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32 位与 64 位格式说明符不匹配的跨平台问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新材质翻译器开发工作 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 配置文件命名从 Base 改为 Default（UE5 命名规范迁移） |

### 维护评价

**维护状态：活跃维护中**

- **创建时间**：2019 年 10 月，已存在约 6 年
- **Beta 状态**：插件自创建以来一直标记为 `IsBetaVersion=true`，且 `EnabledByDefault=false`，说明 Epic 认为其尚未达到生产就绪状态
- **近期活动**：2026 年有多次实质性更新（编译修复、新材质翻译器工作），表明仍在活跃开发
- **已知限制**：
  - 需要 NVIDIA MDL SDK 才能运行（`USE_MDLSDK` 编译标志）
  - Beta 版本，API 和行为可能发生变化
  - 程序纹理烘焙可能影响导入性能
  - MDL 的部分高级功能（如散射、体积材质）支持有限
- **推荐**：适合建筑可视化和影视预览项目试用，不建议在生产环境中作为核心材质管线依赖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/MDLImporter)
- [NVIDIA MDL SDK 文档](https://developer.nvidia.com/mdl-sdk)
- [MDL 语言规范](https://registry.khronos.org/MDL/specs/mdl_spec_1.7.html)