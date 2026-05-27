# Alembic Groom Importer

> Import Hair Strands from Alembic file

| 属性 | 值 |
|---|---|
| 中文名 | Alembic毛发导入 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AlembicHairTranslatorModule` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicHairImporter) | |

## 用途

`AlembicHairImporter` 是一个专门的文件格式翻译器插件。它实现了 `IGroomTranslator` 接口，其核心作用是将存储在 `.abc` (Alembic) 文件中的毛发数据（发丝几何体）解析并转换为 Unreal Engine 内部的 `FHairDescription` 数据结构，从而能够被 `HairStrands` 插件的 Groom 系统加载和使用。

它解决的问题是**连接第三方数字内容创建（DCC）工具（如 Maya、Houdini、Blender）与 UE5 的毛发渲染/模拟系统**。美术师在 DCC 工具中制作并导出为 Alembic 格式的毛发资产，通过此插件便能无缝导入到 UE5 编辑器中。

## 使用场景

- 你在 Maya 或 Houdini 中为角色制作了复杂的毛发发型，并使用 Alembic 格式导出 → 需要此插件将其导入 UE5。
- 你有一个包含毛发动画（如风吹效果）的 Alembic 文件，需要导入到 UE5 中 → 此插件支持动画信息导入。
- 你的项目需要使用 UE5 的 Groom 系统进行毛发渲染和物理模拟 → 此插件是导入外部毛发资产的关键一环。

## 蓝图用法

此插件是一个底层的文件格式翻译器，**不直接暴露任何蓝图节点**。其功能完全集成在 UE 编辑器的文件导入流程中。当在编辑器中导入 `.abc` 文件时，如果文件包含毛发数据，`HairStrands` 系统会自动调用此翻译器进行处理。

### 核心节点

没有公开的蓝图节点。

### 使用示例（蓝图描述）

无。毛发资产的导入和后续操作（如分配材质、设置物理）通过编辑器的 Content Browser 和 Details 面板完成，不涉及蓝图连接。

## C++ 用法

此插件主要作为编辑器扩展模块，其功能通过注册 `IGroomTranslator` 接口被引擎调用。对于一般用户，通常无需在项目 C++ 代码中直接与之交互。

### 头文件引入

```cpp
// 如果需要在引擎层面扩展或与翻译器系统交互（非常规用法）
#include "HairStrandsInterface.h" // IGroomTranslator 接口定义
```

### 基本用法（接口注册）

`AlembicHairTranslatorModule` 在启动时注册翻译器实例。以下代码展示了其核心逻辑的简化版本（基于源码分析）：

```cpp
// 文件路径: Engine/Plugins/Importers/AlembicHairImporter/Source/AlembicHairTranslator/Private/AlembicHairTranslatorModule.cpp
void FAlembicHairTranslatorModule::StartupModule()
{
    // 注册我们的 Alembic 毛发翻译器
    HairStrands::RegisterTranslator(MakeShared<FAlembicHairTranslator>());
}

void FAlembicHairTranslatorModule::ShutdownModule()
{
    // 注销翻译器
    HairStrands::UnregisterTranslator(/* 对应的 Translator */);
}
```

### 进阶用法（自定义翻译器）

如果你想实现自己的毛发格式导入器，可以参照 `FAlembicHairTranslator` 实现 `IGroomTranslator` 接口：

```cpp
// 文件路径: Engine/Plugins/Importers/AlembicHairImporter/Source/AlembicHairTranslator/Private/AlembicHairTranslator.h (简化)
#include "HairStrandsTranslator.h" // 接口定义

class FMyCustomHairTranslator : public IGroomTranslator
{
public:
    // 判断文件是否可由本翻译器处理
    virtual bool CanTranslate(const FString& FilePath) override;

    // 执行翻译，将文件内容填充到 FHairDescription 中
    virtual bool Translate(const FString& FilePath, FHairDescription& OutHairDescription, const FGroomConversionSettings& ConversionSettings) override;

    // 获取支持的文件格式描述（如 “My Hair Format (*.myhair)”）
    virtual FString GetSupportedFormat() const override;

    // ... 其他可选重载，用于支持动画等
};
```

## Demo 示例

由于此插件是纯粹的编辑器翻译器，没有直接的运行时 API。以下是一个最小化的自定义翻译器头文件示例，说明如何实现一个类似的插件：

```cpp
// MyHairTranslator.h
#pragma once

#include "CoreMinimal.h"
#include "HairStrandsTranslator.h" // 关键接口

class FMyHairTranslator : public IGroomTranslator
{
public:
    FMyHairTranslator();
    virtual ~FMyHairTranslator();

    // IGroomTranslator 接口实现
    virtual bool Translate(const FString& FilePath, FHairDescription& OutHairDescription, const struct FGroomConversionSettings& ConversionSettings) override;
    virtual bool CanTranslate(const FString& FilePath) override;
    virtual bool IsFileExtensionSupported(const FString& FileExtension) const override;
    virtual FString GetSupportedFormat() const override;

    // ... 可以添加更多用于动画的重载函数
};
```

```cpp
// MyHairTranslator.cpp
#include "MyHairTranslator.h"

FMyHairTranslator::FMyHairTranslator()
{
    // 初始化，例如加载解析库
}

FMyHairTranslator::~FMyHairTranslator()
{
    // 清理资源
}

bool FMyHairTranslator::Translate(const FString& FilePath, FHairDescription& OutHairDescription, const FGroomConversionSettings& ConversionSettings)
{
    // 1. 读取 .myhair 文件
    // 2. 解析数据（点、线、曲线、UV等）
    // 3. 填充 OutHairDescription 结构体
    // 4. 应用 ConversionSettings（缩放、坐标系转换等）
    return true; // 成功返回true
}

bool FMyHairTranslator::CanTranslate(const FString& FilePath)
{
    // 通过文件扩展名或文件头魔数判断
    return FPaths::GetExtension(FilePath).Equals(TEXT("myhair"), ESearchCase::IgnoreCase);
}

bool FMyHairTranslator::IsFileExtensionSupported(const FString& FileExtension) const
{
    return FileExtension.Equals(TEXT("myhair"), ESearchCase::IgnoreCase);
}

FString FMyHairTranslator::GetSupportedFormat() const
{
    return TEXT("My Custom Hair Format (*.myhair)");
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HairStrands` | 提供 `IGroomTranslator` 接口、`FHairDescription` 核心数据结构以及 Groom 资产管理系统 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，代码维护性更新。 |
| 2024-05-03 | `1fde5666` | PR #10617: AlembicHairImporterFixes: RootUV from Blender Hair / no RootUV registration when not pars | 修复从Blender毛发导入时的RootUV问题，以及在某些情况下错误注册RootUV。 |
| 2024-04-16 | `96a33f78` | Fixed potential uninitialized FVectors in AlembicHairImporter. | 修复了导入器中潜在的 FVector 未初始化问题，提升稳定性。 |
| 2023-10-13 | `ba50d6b0` | Alembic: Fix import issues with corrupted Alembic files. | 修复了导入损坏的 Alembic 文件时可能出现的问题。 |
| 2023-08-08 | `bdb4199e` | Remove unnecessary WindowsHWrapper.h & MinWindows.h include - both files will be automatically included | 移除不必要的头文件包含，代码清理。 |

### 维护评价

`AlembicHairImporter` 插件自 2020 年创建以来，虽然更新频率不高，但持续有 bug 修复和兼容性改进（如支持特定 DCC 工具的导出格式、处理损坏文件）。最近一次更新在 2026 年 4 月，表明它仍在维护中，以确保与引擎主干兼容。

这是一个**功能单一、接口明确**的编辑器插件，其核心功能稳定。作为 Alembic 毛发导入的**唯一官方支持途径**，只要项目需要从 DCC 工具导入毛发，它就是必需且可靠的。**推荐使用**，但请注意它默认未启用，需要在项目中手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicHairImporter)
- [官方文档]( ) (无)
- [测试用例]( ) (未提供路径，可能集成在引擎整体的 Groom 测试中)