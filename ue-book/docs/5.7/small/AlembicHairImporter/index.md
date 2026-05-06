# Alembic Groom Importer

> Import Hair Strands from Alembic file

| 属性 | 值 |
|---|---|
| 中文名 | Alembic 毛发导入器 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AlembicHairTranslatorModule` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2023-03-07 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/AlembicHairImporter) | |

## 用途

此插件允许从 Alembic（`.abc`）文件中导入毛发引导线（Hair Strands）并生成 Groom 资产。它提供了 Unreal Engine 原生 Groom 系统（HairStrands）的翻译器，支持从 Blender、Maya 等 DCC 工具导出的 Alembic 毛发数据，将曲线几何转换为引擎可理解的描述。同时支持提取 RootUV 等额外属性，以及基于时间轴的动画导入。

## 使用场景

- 你在制作角色毛发，使用 Blender 等工具雕刻毛发后导出为 Alembic → 使用此插件直接导入到 UE Groom 系统
- 需要从 Alembic 文件中读取时间序列的毛发动画（如飘动） → 调用 `Translate(float FrameTime, ...)` 接口
- 你在开发自动化工具，需要编程方式批量导入 Groom 资产 → 使用 `FAlembicHairTranslator` C++ 类

## 蓝图用法

本插件为纯编辑器模块，不提供任何蓝图可调用函数。所有导入操作通过编辑器菜单（`File > Import Into...` 选择 .abc 文件）或 C++ 代码完成。

## C++ 用法

### 头文件引入

```cpp
#include "AlembicHairTranslator.h"
```

### 基本用法

使用 `FAlembicHairTranslator` 直接翻译单个文件：

```cpp
// 创建翻译器实例
FAlembicHairTranslator Translator;

// 检查是否支持文件
if (Translator.CanTranslate(TEXT("/path/to/hair.abc")))
{
    FHairDescription OutDescription;
    FGroomConversionSettings ConversionSettings;
    
    // 执行翻译
    if (Translator.Translate(TEXT("/path/to/hair.abc"), OutDescription, ConversionSettings))
    {
        // OutDescription 已包含所有引导线数据
    }
}
```
*来源：`Engine/Plugins/Importers/AlembicHairImporter/Source/AlembicHairTranslator/Private/AlembicHairTranslator.h`*

### 进阶用法

带动画信息的翻译：

```cpp
FAlembicHairTranslator Translator;
Translator.BeginTranslation(TEXT("/path/to/animated_hair.abc"));

FGroomAnimationInfo AnimInfo;
FHairDescription HairAtFrame;
FGroomConversionSettings Settings;

// 逐帧获取毛发数据（假设帧时间 0.0 到 1.0）
for (float Time = 0.0f; Time <= 1.0f; Time += 0.1f)
{
    if (Translator.Translate(Time, HairAtFrame, Settings, &AnimInfo))
    {
        // 处理该帧的毛发描述
    }
}

Translator.EndTranslation();
```

## Demo 示例

以下是一个在编辑器模块中实现的完整 C++ 示例，演示如何通过插件导入一个 Alembic 毛发文件并保存为 Groom 资产（需要运行时模块引用 HairStrands 和 AlembicLibrary）：

**HairImporterDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "HairImporterDemo.generated.h"

/**
 * 演示通过 AlembicHairTranslator 导入毛发
 */
UCLASS()
class UHairImporterDemo : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(exec)
    void ImportHairFromAlembic(const FString& FilePath);
};
```

**HairImporterDemo.cpp**
```cpp
#include "HairImporterDemo.h"
#include "AlembicHairTranslator.h"
#include "HairDescription.h"
#include "GroomAsset.h"
#include "GroomBuilder.h"
#include "GroomImportOptions.h"
#include "Engine/Engine.h"

void UHairImporterDemo::ImportHairFromAlembic(const FString& FilePath)
{
    FAlembicHairTranslator Translator;
    if (!Translator.CanTranslate(FilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Unsupported file: %s"), *FilePath);
        return;
    }

    FHairDescription HairDescription;
    FGroomConversionSettings ConvSettings;
    if (!Translator.Translate(FilePath, HairDescription, ConvSettings))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to translate Alembic hair file"));
        return;
    }

    // 创建 Groom 资产并填充数据（简化示例）
    UGroomAsset* Groom = NewObject<UGroomAsset>(GetTransientPackage(), NAME_None, RF_Public | RF_Standalone);
    FGroomBuilder::BuildGroom(HairDescription, *Groom, GetDefault<UGroomImportOptions>());
    Groom->MarkPackageDirty();

    // 可选：保存到内容路径
    // UPackage* Package = CreatePackage(*FString::Printf(TEXT("/Game/ImportedHair_%s"), *FPaths::GetBaseFilename(FilePath)));
    // Groom->Rename(nullptr, Package);
    // Package->MarkPackageDirty();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HairStrands` | 提供 Groom 数据结构、翻译器接口和资产管理 |

其他依赖均为标准引擎组件（Core, Engine等），无需额外处理。

## 维护状态

### 近期更新

- 2024-05-03 `1fde5666` PR #10617: AlembicHairImporterFixes: RootUV from Blender Hair / no RootUV registration when not parsed
- 2024-04-16 `96a33f78` Fixed potential uninitialized FVectors in AlembicHairImporter
- 2023-10-13 `ba50d6b0` Alembic: Fix import issues with corrupted Alembic files
- 2023-08-08 `bdb4199e` Remove unnecessary WindowsHWrapper.h & MinWindows.h include
- 2023-03-07 `64bc9a06` Groom: Added support to extract RootUV values from the ICurves UVsParam instead of the groom_root_uv

### 维护评价

- **创建时间**：2023-03-07，距今约2年
- **近期更新**：2024年5月有功能性 PR（RootUV 相关修复），2024年4月修复未初始化变量，2023年修复文件损坏问题。更新频率约半年一次
- **维护状态**：**维护中**，关键功能持续修复，非活跃但非废弃
- **推荐使用**：✅ 推荐，此插件是导入 Alembic 毛发到 Unreal Groom 系统的官方方案。已知限制：Alembic 文件中曲线格式需符合规范，部分 DCC 导出选项可能不兼容

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/AlembicHairImporter)
- [官方文档](https://docs.unrealengine.com/5.3/en-US/groom-hair-and-fur-in-unreal-engine/)（Groom 系统概览）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/AlembicHairImporter/Tests)（如有）