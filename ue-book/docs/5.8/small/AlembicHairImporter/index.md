# Alembic Groom Importer

> Import Hair Strands from Alembic file

| 属性 | 值 |
|---|---|
| 中文名 | 毛发导入器 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AlembicHairTranslatorModule` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicHairImporter) | |

## 用途

该插件是一个**专用资产导入器**，用于将存储在 Alembic (.abc) 文件格式中的**头发发缕（Hair Strands）数据**导入到 Unreal Engine 中。它实现了 `IGroomTranslator` 接口，是引擎毛发系统（HairStrands）的配套工具，解决了从其他 DCC 软件（如 Maya, Houdini, Blender 等）导出毛发几何体到 UE 进行渲染和模拟的数据迁移问题。插件默认未启用，需要项目手动启用。

## 使用场景

- 你的美术团队使用 Maya 或 Houdini 创建了高质量的基于发缕的毛发资产，并通过 Alembic 格式导出，你需要将这些资产导入 UE5 用于电影级渲染或高端游戏角色。
- 你正在制作一个需要逼真毛发效果的项目（如影视、CG 动画或角色驱动的游戏），并希望利用外部工具的专业毛发建模功能。
- 你需要导入包含毛发动画序列的 Alembic 文件，用于制作毛发随风飘动或角色运动的效果。

## 蓝图用法

该插件主要作为编辑器内的导入器存在，没有暴露任何蓝图可调用的函数或变量。其功能通过编辑器菜单（例如“导入”对话框）自动集成。

### 核心节点

无。该插件不提供蓝图节点。

### 使用示例（蓝图描述）

不适用。导入操作在编辑器内容浏览器中通过“导入”按钮完成。

## C++ 用法

该插件的核心是注册一个能处理 `.abc` 文件中毛发数据的 `IGroomTranslator` 实现。

### 头文件引入

```cpp
#include "HairStrandsCore/Public/GroomTranslator.h" // 需要依赖 HairStrandsCore 模块
```

### 基本用法

插件在 `StartupModule` 中向引擎的毛发管理系统注册翻译器。开发者通常不需要直接调用此翻译器，而是依赖引擎的导入流程。

```cpp
// 该示例展示了插件内部如何注册翻译器（通常对插件使用者不可见，仅供理解）
// 在 FAlembicHairTranslatorModule::StartupModule() 中可能执行类似逻辑：
// IGroomTranslator::Get()->RegisterTranslator(MakeShared<FAlembicHairTranslator>());
```

### 进阶用法

处理包含动画序列的 Alembic 毛发文件时，插件会使用 `FGroomAnimationInfo` 结构来获取动画元数据。

```cpp
// 伪代码，展示翻译器处理动画的逻辑框架
FGroomAnimationInfo AnimInfo;
FHairDescription HairDescription;
FGroomConversionSettings ConversionSettings;

// 假设获得一个已注册的 Alembic 翻译器实例
TSharedPtr<IGroomTranslator> Translator = MakeShared<FAlembicHairTranslator>();

// 初始化翻译过程，打开文件
if (Translator->BeginTranslation(FilePath))
{
    // 获取第一帧
    Translator->Translate(0.0f, HairDescription, ConversionSettings);
    
    // 获取动画信息（如帧数、时长等）
    // AnimInfo 会被填充
    
    // ... 处理其他帧 ...
    
    // 结束翻译，释放资源
    Translator->EndTranslation();
}
```

## Demo 示例

下面是一个最小的模块示例，演示如何在你自己的编辑器模块中检查或交互 `IGroomTranslator` 系统（假设 AlembicHairImporter 插件已启用）。

```cpp
// MyHairTool.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyHairToolModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    /** 列出所有已注册的毛发文件格式翻译器 */
    void ListRegisteredTranslators() const;
};
```

```cpp
// MyHairTool.cpp
#include "MyHairTool.h"
#include "HairStrandsCore/Public/GroomTranslator.h" // 来自 HairStrandsCore 模块

#define LOCTEXT_NAMESPACE "FMyHairToolModule"

void FMyHairToolModule::StartupModule()
{
    // 模块启动时可以查询可用的翻译器
    ListRegisteredTranslators();
}

void FMyHairToolModule::ShutdownModule()
{
}

void FMyHairToolModule::ListRegisteredTranslators() const
{
    if (IGroomTranslator::IsAvailable())
    {
        const TArray<FString> SupportedFormats = IGroomTranslator::Get()->GetSupportedFormats();
        UE_LOG(LogTemp, Log, TEXT("Supported Groom file formats:"));
        for (const FString& Format : SupportedFormats)
        {
            UE_LOG(LogTemp, Log, TEXT("  - %s"), *Format);
        }
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyHairToolModule, MyHairTool)
```

## 模块依赖

从插件的 `.uplugin` 和常见实现推断，使用此插件需要以下依赖：

| 模块 | 用途 |
|---|---|
| `HairStrandsCore` | 核心毛发资产和翻译器接口，必须依赖 |
| `AlembicLib` 或相关模块 | 底层 Alembic 文件解析库（插件内部依赖，可能自动传递） |

**注意**：由于该插件 `EnabledByDefault: false`，你的项目需要先在 `.uproject` 文件或插件设置中启用它。同时，你的项目需要启用 `HairStrands` 插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 统一日志宏，代码现代化。 |
| 2024-05-03 | `1fde5666` | PR #10617: AlembicHairImporterFixes: RootUV from Blender Hair / no RootUV registration when not pars | 修复从Blender导入时的根UV问题，优化属性注册。 |
| 2024-04-16 | `96a33f78` | Fixed potential uninitialized FVectors in AlembicHairImporter. | 修复可能未初始化的向量变量，提升稳定性。 |
| 2023-10-13 | `ba50d6b0` | Alembic: Fix import issues with corrupted Alembic files. | 修复导入损坏Alembic文件时的问题。 |
| 2023-08-08 | `bdb4199e` | Remove unnecessary WindowsHWrapper.h & MinWindows.h include - both files will be automatically inclu | 清理不必要的头文件包含。 |

### 维护评价

该插件创建于 2020 年 11 月，已有约 5 年历史。**维护状态不活跃**，最后一次实质性的功能或重要 Bug 修复是 2024 年 5 月。此后仅有一项代码现代化的日志宏迁移（2026年）。它主要解决了一个特定的导入需求（Alembic 格式毛发），功能相对单一且稳定。作为 `HairStrands` 系统的配套工具，在相关系统没有大改的前提下，其核心功能仍然有效。

**推荐使用场景**：如果你确实需要从 Alembic 文件导入毛发数据，此插件是官方推荐的方案。但由于其 `EnabledByDefault: false` 且更新不频繁，建议在项目前期评估好需求，确认其他格式（如 FBX）是否能满足。对于新的毛发工作流，Epic 可能更推荐其集成的 Groom 工作流和编辑器内工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicHairImporter)
- [官方文档]()（无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Importers/AlembicHairImporter)（插件目录内未发现明显测试文件）