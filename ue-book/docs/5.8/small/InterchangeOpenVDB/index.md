# Interchange OpenVDB

> Allows translation of OpenVDB files via the Interchange framework

| 属性 | 值 |
|---|---|
| 中文名 | 体素数据交换导入 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeOpenVDBImport` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-06 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/OpenVDB) | |

## 用途

本插件为 UE5 的 **Interchange 框架**提供 OpenVDB 格式文件的翻译能力。OpenVDB 是工业界广泛使用的开放体素数据库格式（`.vdb`），常用于存储稀疏体积数据，如烟雾、火焰、云雾、流体模拟等效果。

该插件将 OpenVDB 文件的导入集成到统一的 Interchange 导入管线中，使得体积数据的导入流程与网格、纹理等资产的导入保持一致的架构模式。通过实现 `IInterchangeVolumePayloadInterface` 接口，它能够按需提供体积负载数据（volume payload），支持懒加载等优化策略。

**注意**：此插件默认关闭（`EnabledByDefault: false`）、标记为实验性（`IsExperimentalVersion: true`）且隐藏（`Hidden: true`），表明 Epic 将其视为尚不稳定的实验功能。

## 使用场景

- 你需要在 UE5 中导入 OpenVDB 格式的体积数据（烟雾、火焰、云层、流体模拟缓存等）
- 你希望使用统一的 Interchange 导入管线处理 `.vdb` 文件，而非依赖其他单独的导入路径
- 你正在开发影视或虚拟制片项目，需要导入外部 DCC 工具（如 Houdini）生成的 OpenVDB 缓存
- 你需要按需加载体积数据以优化内存使用

## 蓝图用法

本插件的核心类 `UInterchangeOpenVDBTranslator` 标记为 `BlueprintType`，但未暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 的自定义方法。所有公共接口均来自基类 `UInterchangeTranslatorBase` 和 `IInterchangeVolumePayloadInterface`，由 Interchange 框架内部调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无自定义蓝图节点 | 翻译器由 Interchange 框架自动实例化和调用 | `UInterchangeOpenVDBTranslator` |

插件的工作方式是**注册翻译器**，由 Interchange 框架根据文件扩展名自动选择合适的翻译器进行导入，用户在蓝图层面通常通过通用的 Interchange 导入节点触发。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeOpenVDBTranslator.h"
```

### 基本用法：查询翻译器支持的格式

翻译器会自动向 Interchange 框架注册。你可以通过标准 Interchange API 查询 `.vdb` 文件的导入支持：

```cpp
// 通过 Interchange 框架查询翻译器（插件启用后自动注册）
// 来源: Source/Import/Public/InterchangeOpenVDBTranslator.h

// 检查翻译器是否能处理特定源数据
UInterchangeSourceData* SourceData = UInterchangeManager::CreateSourceData(TEXT("/path/to/volume.vdb"));
UInterchangeOpenVDBTranslator* Translator = NewObject<UInterchangeOpenVDBTranslator>();

// CanImportSourceData 内部会检查文件扩展名是否为 .vdb
bool bCanImport = Translator->CanImportSourceData(SourceData);

// GetSupportedFormats 返回支持的格式列表
TArray<FString> Formats = Translator->GetSupportedFormats();
```

### 进阶用法：自定义翻译器设置

翻译器使用 `UInterchangeVolumeTranslatorSettings` 来控制导入参数：

```cpp
// 来源: Source/Import/Public/InterchangeOpenVDBTranslator.h

// 创建并配置翻译器设置
UInterchangeVolumeTranslatorSettings* Settings = NewObject<UInterchangeVolumeTranslatorSettings>();
// 根据需要配置设置属性...

UInterchangeOpenVDBTranslator* Translator = NewObject<UInterchangeOpenVDBTranslator>();
Translator->SetSettings(Settings);

// 执行翻译，将结果写入节点容器
UInterchangeBaseNodeContainer* NodeContainer = NewObject<UInterchangeBaseNodeContainer>();
bool bSuccess = Translator->Translate(*NodeContainer);
```

## Demo 示例

以下展示如何通过代码创建一个最小的 OpenVDB 翻译器并执行翻译：

```cpp
// InterchangeOpenVBDDemo.h
#pragma once

#include "CoreMinimal.h"

class FInterchangeOpenVBDDemo
{
public:
    /** 使用 Interchange 框架导入一个 OpenVDB 文件 */
    static bool ImportVDBFile(const FString& VDBFilePath);
};
```

```cpp
// InterchangeOpenVBDDemo.cpp
#include "InterchangeOpenVBDDemo.h"
#include "InterchangeOpenVDBTranslator.h"
#include "Nodes/InterchangeBaseNodeContainer.h"
#include "InterchangeManager.h"

bool FInterchangeOpenVBDDemo::ImportVDBFile(const FString& VDBFilePath)
{
    // 1. 创建源数据对象
    UInterchangeSourceData* SourceData = UInterchangeManager::CreateSourceData(VDBFilePath);
    if (!SourceData)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create source data for: %s"), *VDBFilePath);
        return false;
    }

    // 2. 实例化 OpenVDB 翻译器
    UInterchangeOpenVDBTranslator* Translator = NewObject<UInterchangeOpenVDBTranslator>();

    // 3. 检查是否能导入该文件
    if (!Translator->CanImportSourceData(SourceData))
    {
        UE_LOG(LogTemp, Warning, TEXT("Cannot import this source data: %s"), *VDBFilePath);
        return false;
    }

    // 4. 执行翻译
    UInterchangeBaseNodeContainer* NodeContainer = NewObject<UInterchangeBaseNodeContainer>();
    const bool bTranslated = Translator->Translate(*NodeContainer);

    if (bTranslated)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully translated VDB file: %s"), *VDBFilePath);
    }

    // 5. 释放源数据
    Translator->ReleaseSource();

    return bTranslated;
}
```

> **注意**：实际使用中通常不需要手动创建翻译器实例。Interchange 管线会根据文件扩展名自动选择已注册的翻译器。以上仅为展示 API 工作原理。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 框架核心（翻译器基类、节点容器等） |
| `InterchangeVolume` | 体积数据相关的 Interchange 接口和类型（`IInterchangeVolumePayloadInterface`、`FVolumePayloadData`） |

插件依赖：**Interchange**（在 .uplugin 中声明）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新 API |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复上一次批量替换导致的错误 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退上一次提交 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 迁移委托 API 以修复引擎初始化时的注册问题 |
| 2025-12-11 | `9b8fa9f8` | Interchange: Fix missing snippets when registering pipelines on the Interchange extension modules | 修复扩展模块注册管线时的代码片段缺失问题 |

### 维护评价

该插件创建于 2024 年，年龄约 1 年，属于较新的插件。从 git 历史来看，近期更新主要是**框架层面的维护性改动**（日志宏迁移、委托 API 变更、批量替换修复），而非功能增强。

关键信息：
- **实验性插件**：`IsExperimentalVersion=true`，默认隐藏且关闭，表明 Epic 仍在验证该功能
- **更新频率低**：近一年仅有 5 次相关提交，且均为被动维护而非功能开发
- **源码规模极小**：仅约 5 个文件，说明功能范围有限（仅翻译器注册 + 基本 VDB 解析）
- **跨平台支持**：仅支持 Win64 和 Linux

**推荐程度**：⚠️ 谨慎使用。适合对 OpenVDB 导入有明确需求的项目，但需注意该插件处于实验阶段，API 可能变动，生产环境使用前建议充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/OpenVDB)
- [OpenVDB 官网](https://www.openvdb.org/)（第三方格式标准）
- [UE5 Interchange 框架](https://docs.unrealengine.com/5.8/en-US/interchange-overview-in-unreal-engine/)