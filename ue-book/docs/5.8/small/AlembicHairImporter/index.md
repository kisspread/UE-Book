# Alembic Groom Importer

> Import Hair Strands from Alembic file

| 属性 | 值 |
|---|---|
| 中文名 | Alembic毛发导入器 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AlembicHairTranslatorModule` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicHairImporter) | |

## 用途

此插件为 UE5 的毛发系统（Groom）提供了一种关键的资产导入通道。它实现了 `IGroomTranslator` 接口，专门用于解析来自数字内容创建工具（如 Maya, Blender, Houdini）的 Alembic (.abc) 格式文件中的毛发数据（Hair Strands）。其核心作用是将外部工具精心制作的高精度毛发几何体、动画（如果存在）转换为 UE5 内部使用的 `FHairDescription` 数据结构，从而实现在虚幻引擎中进行高品质毛发渲染和物理模拟的基础。

## 使用场景

- **数字人/角色制作**：当你在 Maya 或 Blender 等 DCC 工具中为角色创建了复杂的、基于梳理的毛发（Groom），需要将其导入 UE5 进行最终的渲染和动力学模拟时。
- **高精度毛发动画**：当你从外部工具导出了包含毛发动画（例如，风吹效果）的 Alembic 文件，需要将其作为动画序列导入 UE5 时。
- **跨平台资产流水线**：作为使用 Alembic 作为通用毛发交换格式的资产生产流程中的关键一环。

## 蓝图用法

此插件主要为编辑器导入流程提供底层支持，**不直接暴露可调用的蓝图节点**。其功能通过 UE5 的标准资产导入对话框触发：当用户在内容浏览器中导入一个 `.abc` 文件，且该文件包含毛发数据时，引擎会自动调用此插件中的翻译器进行处理。

## C++ 用法

### 头文件引入

```cpp
#include "AlembicHairTranslator/AlembicHairTranslator.h"
```

### 基本用法

此插件的核心是一个翻译器（Translator），通常由 UE5 的毛发导入器（Groom Importer）在后台调用。以下展示了其接口的基本使用方式（参考 `FAlembicHairTranslator` 的实现）。

```cpp
// 假设我们有一个 Alembic 文件路径和转换设置
FString AbcFilePath = TEXT("/Game/Hair/character_hair.abc");
FGroomConversionSettings ConversionSettings;

// 创建翻译器实例
FAlembicHairTranslator Translator;

// 检查文件是否可以被翻译
if (Translator.CanTranslate(AbcFilePath))
{
    FHairDescription HairDescription;
    // 执行翻译，将 Alembic 数据加载到 HairDescription 中
    bool bSuccess = Translator.Translate(AbcFilePath, HairDescription, ConversionSettings);
    
    if (bSuccess)
    {
        // 翻译成功，HairDescription 现在包含了毛发数据
        // 后续可以将其保存为 .groom 资产或直接用于渲染
    }
}
```

### 进阶用法

如果 Alembic 文件包含毛发动画，可以使用其分帧翻译接口。

```cpp
FString AnimatedAbcPath = TEXT("/Game/Hair/animated_hair.abc");
FGroomConversionSettings ConversionSettings;
FAlembicHairTranslator Translator;

// 开始翻译，打开文件并准备读取动画帧
if (Translator.BeginTranslation(AnimatedAbcPath))
{
    TArray<FHairDescription> FrameDescriptions;
    
    // 假设动画有 30 帧，每帧间隔 1/30 秒
    for (int32 Frame = 0; Frame < 30; ++Frame)
    {
        float FrameTime = static_cast<float>(Frame) / 30.0f;
        FHairDescription CurrentFrameDescription;
        
        // 翻译特定时间点的毛发状态
        if (Translator.Translate(FrameTime, CurrentFrameDescription, ConversionSettings))
        {
            FrameDescriptions.Add(MoveTemp(CurrentFrameDescription));
        }
    }
    
    // 结束翻译，释放资源
    Translator.EndTranslation();
    
    // 此时 FrameDescriptions 包含了每一帧的毛发描述
}
```

## Demo 示例

下面是一个创建自定义毛发翻译器的最小示例，展示了如何将 Alembic 毛发翻译器集成到更广泛的导入流程中。

**MyHairTranslator.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GroomTranslator.h"

class FMyCustomHairTranslator : public IGroomTranslator
{
public:
    virtual ~FMyCustomHairTranslator() override = default;

    // 声明来自 IGroomTranslator 的接口函数
    virtual bool Translate(const FString& FilePath, FHairDescription& OutHairDescription, const FGroomConversionSettings& ConversionSettings) override;
    virtual bool CanTranslate(const FString& FilePath) override;
    virtual bool IsFileExtensionSupported(const FString& FileExtension) const override;
    virtual FString GetSupportedFormat() const override;

    // 可以添加您自己的私有辅助方法
private:
    // ... 私有成员
};
```

**MyHairTranslator.cpp**
```cpp
#include "MyHairTranslator.h"
#include "HairDescription.h"

bool FMyCustomHairTranslator::Translate(const FString& FilePath, FHairDescription& OutHairDescription, const FGroomConversionSettings& ConversionSettings)
{
    // 在这里实现您自己的 .abc 文件解析逻辑
    // 或者，您可以包装并调用原始的 FAlembicHairTranslator
    // 例如: FAlembicHairTranslator AlembicTranslator;
    //       return AlembicTranslator.Translate(FilePath, OutHairDescription, ConversionSettings);
    
    UE_LOG(LogTemp, Warning, TEXT("Custom translation not yet implemented for: %s"), *FilePath);
    return false;
}

bool FMyCustomHairTranslator::CanTranslate(const FString& FilePath)
{
    // 检查文件扩展名或文件头内容，决定是否由本翻译器处理
    return FilePath.EndsWith(TEXT(".abc"), ESearchCase::IgnoreCase);
}

bool FMyCustomHairTranslator::IsFileExtensionSupported(const FString& FileExtension) const
{
    // 仅支持 .abc 扩展名
    return FileExtension.Equals(TEXT("abc"), ESearchCase::IgnoreCase);
}

FString FMyCustomHairTranslator::GetSupportedFormat() const
{
    return TEXT("Alembic Groom (*.abc)|*.abc");
}
```

要使用此翻译器，需要在模块启动时将其注册到 GroomImporter：

```cpp
// 在您的模块 StartupModule 函数中
#include "GroomTranslator.h"
#include "GroomImporter.h"

void FMyModule::StartupModule()
{
    // ... 其他初始化代码
    
    // 注册自定义翻译器（通常由 AlembicHairTranslatorModule 完成对 AlembicHairTranslator 的注册）
    // FGroomImporter::Get().RegisterTranslator<FMyCustomHairTranslator>();
}
```

## 模块依赖

根据插件的功能和接口，使用此插件时需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `HairStrandsCore` | 提供 `FHairDescription` 等核心毛发数据结构 |
| `GroomImporter` | 提供 `IGroomTranslator` 接口和 Groom 导入框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志系统调用更新至新的 UE_LOGF 宏，属于常规代码现代化维护。 |
| 2024-05-03 | `1fde5666` | PR #10617: AlembicHairImporterFixes: RootUV from Blender Hair / no RootUV registration when not pars | 修复了从 Blender 导出的毛发根部 UV 问题，并优化了当解析失败时的处理逻辑。 |
| 2024-04-16 | `96a33f78` | Fixed potential uninitialized FVectors in AlembicHairImporter. | 修复了导入器中可能存在的 FVector 未初始化问题，提高了代码健壮性。 |

### 维护评价

- **年龄**：插件创建于 2020 年底，已有约 5 年历史，属于成熟模块。
- **更新频率**：最近一次功能性更新（Fixes）在 2024 年 5 月，最近一次维护性更新在 2026 年 4 月。更新频率不高，但持续有维护。
- **维护状态**：**维护中**。虽然更新不频繁，但近期仍有针对特定问题（如 Blender 兼容性）的修复，表明它仍在使用和维护范围内。
- **已知限制**：作为仅编辑器（Editor）模块，它不能在运行时打包使用。对 Alembic 文件格式的支持程度和特定版本 DCC 工具的兼容性可能有限制。
- **推荐度**：**推荐使用**。它是 UE5 原生工作流中从 Alembic 导入高质量毛发的唯一官方途径，对于需要高精度毛发资产的项目是必要工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicHairImporter)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicHairImporter/Source/AlembicHairTranslator/Tests) （路径推断，测试通常位于模块的Tests目录）