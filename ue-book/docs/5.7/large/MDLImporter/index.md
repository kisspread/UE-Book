# MDL Importer

> Importer for MDL material files.

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板、MDL 模块文件） |
| 模块 | `MDLImporter` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/MDLImporter) | |

## 用途

MDL Importer 是一个基于 [NVIDIA MDL（Material Definition Language）SDK](https://developer.nvidia.com/mdl-sdk) 的材质导入插件。它将 `.mdl` 文件中定义的材质转换为 UE5 的 `UMaterial` 资产，实现跨渲染器的材质互操作。

**MDL 是什么？** MDL 是 NVIDIA 定义的一种材质描述语言，用于精确描述物理材质的外观（BSDF、散射、吸收等），被广泛用于 V-Ray、Iray、Blender Cycles 等渲染器中。MDL Importer 的存在意义在于：让使用 MDL 生态系统的工作室（汽车可视化、建筑可视化、VFX）能将已有的 MDL 材质直接导入 UE5，而无需手动重建材质图。

**核心流程：**
1. 解析 `.mdl` 文件，提取其中所有 `export material` 声明
2. 通过 NVIDIA MDL SDK 加载和编译 MDL 模块
3. 使用 MDL Distiller 将通用 MDL 材质"蒸馏"为 UE5 目标模型（PBR 参数：BaseColor、Metallic、Roughness 等）
4. 程序化纹理（如噪波、颜色渐变）会烘焙为位图纹理
5. 根据材质特性自动选择合适的 UE5 Shading Model（Opaque、Translucent、ClearCoat、Subsurface 等）
6. 生成 `UMaterial` 资产，包含完整的材质表达式节点图

**⚠️ 重要限制：** 此插件默认禁用（`EnabledByDefault=false`），标记为 Beta（`IsBetaVersion=true`），且依赖 NVIDIA 的受限第三方库（`Restricted/NotForLicensees/Source/ThirdParty/Enterprise/mdl-sdk-349500.8766a`）。标准 UE5 发行版中不包含 MDL SDK 的二进制文件，因此该插件在大多数场景下不可用。

## 使用场景

- **汽车可视化**：你有一个包含完整 MDL 漆面材质（carpaint with flakes）的 `.mdl` 文件，想在 UE5 中使用 → 使用 MDL Importer 导入，自动转换为 ClearCoat Shading Model
- **建筑可视化**：V-Ray 或 Iray 的 MDL 材质库需要导入 UE5 → 使用 MDL Importer 批量导入，保留物理正确的材质参数
- **VFX 工作流**：你的工作室使用 MDL 作为材质交换格式，需要在 UE5 中使用相同材质 → 通过 MDL Importer 确保材质一致性
- **程序化材质导入**：MDL 文件中的程序化纹理（如 noise、gradient）会自动烘焙为纹理贴图，适配 UE5 的材质节点系统

## 蓝图用法

**无蓝图节点。** 此插件是纯编辑器导入工具，不暴露任何 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。所有操作通过编辑器 UI 完成：

- **Content Browser 导入**：右键 → Import → 选择 `.mdl` 文件
- **重新导入**：右键已导入的材质 → Asset Actions → Reimport Material
- **导入选项窗口**：导入时弹出的 `SMDLOptionsWindow` 允许配置烘焙分辨率、搜索路径等

## C++ 用法

### 头文件引入

```cpp
#include "MDLMaterialImporter.h"      // 静态导入接口
#include "MDLImporterModule.h"        // 模块访问
#include "MDLImporterOptions.h"       // 导入选项
```

### 基本用法：通过静态接口导入单个材质

```cpp
// 来源: Source/MDLImporter/Public/MDLMaterialImporter.h, Source/MDLImporter/Private/MDLMaterialImporter.cpp
// FMdlMaterialImporter::ImportMaterialFromModule 是从外部模块导入 MDL 材质的最简方式

#include "MDLMaterialImporter.h"
#include "MDLImporterOptions.h"

// 1. 创建导入选项
TStrongObjectPtr<UMDLImporterOptions> Options(NewObject<UMDLImporterOptions>(
    GetTransientPackage(), TEXT("MDL Options")));

// 2. 添加搜索路径（可选，使用 RAII 的 ScopedSearchPath）
{
    FMdlMaterialImporter::FScopedSearchPath ScopedPath(TEXT("C:/MyMDLLibrary/"));

    // 3. 从 MDL 模块导入指定材质定义
    UMaterialInterface* Material = FMdlMaterialImporter::ImportMaterialFromModule(
        ParentPackage,           // 目标 UPackage
        RF_Public | RF_Standalone, // 对象标志
        TEXT("::my_mdl_module"),   // MDL 模块名（::前缀格式）
        TEXT("my_material"),       // MDL 材质定义名
        *Options                   // 导入选项
    );

    if (Material)
    {
        UE_LOG(LogTemp, Log, TEXT("Imported: %s"), *Material->GetName());
    }
}
// ScopedSearchPath 析构时自动移除搜索路径
```

### 进阶用法：通过模块接口进行完整导入流程

```cpp
// 来源: Source/MDLImporter/Public/MDLImporterModule.h, Source/MDLImporter/Private/MDLImporter.h
// 适用于需要更多控制的场景

#include "MDLImporterModule.h"
#include "MDLImporter.h"
#include "MDLImporterOptions.h"

// 1. 获取模块实例
IMDLImporterModule& Module = IMDLImporterModule::Get();
if (!Module.IsLoaded())
{
    UE_LOG(LogTemp, Error, TEXT("MDL SDK not loaded"));
    return;
}

// 2. 获取内部导入器
FMDLImporter& Importer = Module.GetMDLImporter();

// 3. 设置选项
TStrongObjectPtr<UMDLImporterOptions> Options(NewObject<UMDLImporterOptions>(
    GetTransientPackage(), TEXT("MDL Options")));
Options->BakingResolution = 2048;  // 烘焙纹理分辨率
Options->BakingSamples = 4;        // MSAA 采样数
Options->MetersPerSceneUnit = 0.01f; // 场景单位与米的换算比

// 4. 打开 MDL 文件
Mdl::FMaterialCollection Materials;
bool bSuccess = Importer.OpenFile(TEXT("C:/path/to/material.mdl"), *Options, Materials);

if (bSuccess && Materials.Count() > 0)
{
    // 5. 导入材质到目标 Package
    bSuccess = Importer.ImportMaterials(
        ParentPackage,
        RF_Public | RF_Standalone,
        Materials,
        [](const FString& Msg, int Idx) {
            UE_LOG(LogTemp, Log, TEXT("Progress: %s (idx %d)"), *Msg, Idx);
        }
    );

    // 6. 获取创建的材质
    const TArray<UMaterialInterface*>& Created = Importer.GetCreatedMaterials();
    for (UMaterialInterface* Mat : Created)
    {
        UE_LOG(LogTemp, Log, TEXT("Created: %s"), *Mat->GetName());
    }
}

// 7. 检查日志消息
const TArray<MDLImporterLogging::FLogMessage>& Messages = Importer.GetLogMessages();
for (const auto& Msg : Messages)
{
    UE_LOG(LogTemp, Warning, TEXT("MDL: %s"), *Msg.Get<1>());
}
```

## Demo 示例

### 最小导入工具类

```cpp
// MyMdlImportHelper.h
#pragma once

#include "CoreMinimal.h"

class UMaterialInterface;
class UMDLImporterOptions;

class FMyMdlImportHelper
{
public:
    // 导入单个 MDL 文件中的所有材质
    static TArray<UMaterialInterface*> ImportMdlFile(
        UObject* ParentPackage,
        const FString& MdlFilePath,
        int32 BakingResolution = 1024
    );

    // 从 MDL 模块名导入指定材质
    static UMaterialInterface* ImportSingleMaterial(
        UObject* ParentPackage,
        const FString& ModuleName,
        const FString& DefinitionName
    );
};
```

```cpp
// MyMdlImportHelper.cpp
#include "MyMdlImportHelper.h"

#include "MDLMaterialImporter.h"
#include "MDLImporterModule.h"
#include "MDLImporter.h"
#include "MDLImporterOptions.h"
#include "UObject/StrongObjectPtr.h"

TArray<UMaterialInterface*> FMyMdlImportHelper::ImportMdlFile(
    UObject* ParentPackage,
    const FString& MdlFilePath,
    int32 BakingResolution)
{
    TArray<UMaterialInterface*> Result;

    if (!IMDLImporterModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("MDL Importer module not available"));
        return Result;
    }

    IMDLImporterModule& Module = IMDLImporterModule::Get();
    FMDLImporter& Importer = Module.GetMDLImporter();

    if (!Importer.IsLoaded())
    {
        UE_LOG(LogTemp, Error, TEXT("MDL SDK not loaded"));
        return Result;
    }

    TStrongObjectPtr<UMDLImporterOptions> Options(
        NewObject<UMDLImporterOptions>(GetTransientPackage()));
    Options->BakingResolution = BakingResolution;

    Mdl::FMaterialCollection Materials;
    if (Importer.OpenFile(MdlFilePath, *Options, Materials))
    {
        Importer.ImportMaterials(ParentPackage, RF_Public, Materials);
        Result = Importer.GetCreatedMaterials();
    }

    return Result;
}

UMaterialInterface* FMyMdlImportHelper::ImportSingleMaterial(
    UObject* ParentPackage,
    const FString& ModuleName,
    const FString& DefinitionName)
{
    TStrongObjectPtr<UMDLImporterOptions> Options(
        NewObject<UMDLImporterOptions>(GetTransientPackage()));

    return FMdlMaterialImporter::ImportMaterialFromModule(
        Cast<UPackage>(ParentPackage),
        RF_Public | RF_Standalone,
        ModuleName,
        DefinitionName,
        *Options);
}
```

**Build.cs 依赖：**

```csharp
// 由于所有依赖都是 PrivateDependencyModuleNames，
// 外部模块通常只需依赖 "MDLImporter" 模块
PrivateDependencyModuleNames.Add("MDLImporter");
```

## 模块依赖

MDLImporter 的所有模块依赖均为 `PrivateDependencyModuleNames`，外部使用者通常只需依赖 `MDLImporter` 模块本身：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、路径、日志 |
| `CoreUObject` | UObject 系统、资产注册 |
| `Engine` | 材质系统、纹理 |
| `UnrealEd` | 编辑器工厂、导入/重新导入 |
| `Slate` / `SlateCore` | 导入选项窗口 UI |
| `MaterialEditor` | 材质表达式布局 |
| `AssetTools` | 虚拟纹理转换 |
| `RenderCore` / `RHI` | 渲染相关（虚拟纹理支持） |
| `ImageCore` | 图像处理 |
| `MessageLog` | 导入错误/警告消息 |
| `Analytics` | 导入遥测数据 |
| `EditorFramework` | 资产导入数据 |
| `MainFrame` | 模态窗口父级 |
| `InputCore` | 输入处理 |
| `Projects` | 插件路径管理 |

**第三方库（运行时动态加载）：**

| 库 | 用途 |
|---|---|
| `libmdl_sdk` (.dll/.so) | NVIDIA MDL SDK 核心库 |
| `mdl_distiller` (.dll/.so) | MDL 材质蒸馏器 |
| `dds` (.dll/.so) | DDS 纹理格式支持 |
| `nv_freeimage` (.dll/.so) | 图像格式支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 内容 | 解读 |
|---|---|---|---|
| 2025-03-12 | `6a50af3` | MDL: Downgrade warning into a log when MDL SDK is not available as that can prevent cooking in some cases. | 重要修复：当 MDL SDK 不可用时将 warning 降级为 log，避免在 cooking 时阻塞构建流程。说明该插件在无 SDK 环境下仍会加载，之前会导致 cooking 失败。 |
| 2024-12-11 | `03c9350` | Color functions are [[nodiscard]] | 代码质量改进：为颜色函数添加 `[[nodiscard]]` 属性，防止返回值被忽略。 |
| 2024-07-26 | `37bcc76` | Attempt to fix some Texture code that's not using correct PreEdit/PostEdit pattern | 纹理代码修复：修正 PreEdit/PostEdit 模式的使用，可能修复纹理编辑时的崩溃或数据丢失问题。 |

### 维护评价

- **创建时间**：2019年10月，约 6 年历史
- **更新频率**：低频维护，每年 2-3 次提交，主要是编译修复和平台适配
- **活跃程度**：**维护不活跃** — 自 2019 年创建以来从未有过功能性更新，所有 commit 都是编译修复、代码风格调整或平台适配
- **Beta 状态**：始终标记为 `IsBetaVersion=true`，从未毕业为正式版
- **第三方依赖**：依赖 NVIDIA 受限源码（`Restricted/NotForLicensees`），标准 UE5 发行版不包含
- **已知限制**：
  - 需要完整的 NVIDIA MDL SDK 才能编译和运行
  - 仅支持 PBR 材质子集，复杂的 MDL 特性（如散射介质）可能无法完美转换
  - 无蓝图接口，纯编辑器工具
  - 无自动化测试代码

**⚠️ 推荐评估：** 除非你的团队已有 NVIDIA MDL SDK 许可证且需要在 UE5 中使用 MDL 材质，否则不建议依赖此插件。它本质上是一个**企业级兼容工具**，用于特定行业（汽车/建筑可视化）的材质互操作。对于新项目，建议直接使用 UE5 原生材质系统。

## 子模块文档

| 子模块 | 文档 | 说明 |
|---|---|---|
| MDL SDK 集成 | [MDLSDK.md](MDLSDK.md) | ApiContext、MaterialDistiller、MaterialTraverser — MDL SDK 的 UE5 适配层 |
| 材质工厂 | [MaterialFactory.md](MaterialFactory.md) | 7 种材质类型的工厂（Opaque、Translucent、Clearcoat、Carpaint、Subsurface、Masked、Emissive） |
| 表达式生成器 | [Generator.md](Generator.md) | MaterialExpressionFactory、MaterialTextureFactory — MDL 表达式到 UE5 材质节点的转换 |
| 导入管线 | [ImportPipeline.md](ImportPipeline.md) | MDLImporterFactory、MDLImporter、MdlFileImporter — 文件导入和重新导入的完整流程 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/MDLImporter)
- [NVIDIA MDL SDK 文档](https://developer.nvidia.com/mdl-sdk)（第三方）
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
