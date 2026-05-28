# Asset Manager Editor

> Editor UI and utilities for managing and auditing Assets on disk

| 属性 | 值 |
|---|---|
| 中文名 | 资产管理器编辑器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AssetManagerEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2017-03-22 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/AssetManagerEditor) | |

## 用途

AssetManagerEditor 是 UE5 资产管理体系的**编辑器端 UI 入口**，为 `UAssetManager` 提供完整的可视化审计和管理工具集。

它解决的核心问题是：当项目拥有数百甚至数千个资产时，如何**可视化地理解资产之间的依赖关系、分析磁盘/内存占用、管理分块策略（Chunking），以及审计资产是否符合资产管理规则**。

本插件并不实现资产管理系统本身（那是 Engine 中 `AssetManager` 模块的职责），而是提供以下编辑器工具：

1. **Reference Viewer**：可视化资产依赖图，支持双向（引用者/被引用者）遍历、深度/广度限制、按集合/插件过滤、查找路径等
2. **Asset Audit Browser**：专用资产审计浏览器，按 PrimaryAssetType/Id 分组查看资产，支持自定义列（磁盘大小、资源大小、Cook规则、Chunk分配等）
3. **Size Map**：树状图展示资产及其依赖的磁盘占用大小，快速定位体积大户
4. **PrimaryAssetId/PrimaryAssetType 属性自定义**：在 Details 面板中为这两个结构体提供带过滤的资产选择器 UI

## 使用场景

- 你需要了解某个资产（如纹理、蓝图）的完整依赖链，判断是否引入了不必要的依赖 → 用 **Reference Viewer**
- 你想分析游戏打包后各资产占用多少磁盘空间 → 用 **Size Map**
- 你需要按 PrimaryAssetType 审计所有资产的 Cook 规则和 Chunk 分配 → 用 **Asset Audit Browser**
- 你在编辑器中使用 `FPrimaryAssetId` 或 `FPrimaryAssetType` 类型的属性，需要一个方便的选择器 UI → 本插件提供 **Property Customization**

## 蓝图用法

本插件是纯编辑器 UI 插件，没有暴露 `BlueprintCallable` 函数。所有功能均通过编辑器菜单、上下文菜单和窗口面板访问：

| 入口 | 操作 |
|---|---|
| 内容浏览器右键菜单 | → **Reference Viewer**、**Size Map**、**Asset Audit** |
| Reference Viewer 上下文菜单 | → 创建集合（Collection）、复制路径、查看引用对象 |
| 主菜单 **Window** | → **Developer Tools** → **Asset Audit** |
| Details 面板 | `FPrimaryAssetId`/`FPrimaryAssetType` 属性自动使用自定义选择器 |

## C++ 用法

### 头文件引入

```cpp
#include "AssetManagerEditorModule.h"
```

### 基本用法

通过模块接口访问本插件提供的工具函数：

```cpp
// 获取模块接口
IAssetManagerEditorModule& AssetManagerEditor = IAssetManagerEditorModule::Get();

// 用 AssetData 列表打开资产审计 UI
TArray<FAssetData> SelectedAssets;
// ... 填充选中的资产
AssetManagerEditor.OpenAssetAuditUI(SelectedAssets);

// 用包名列表打开资产审计 UI
TArray<FName> PackageNames;
PackageNames.Add(FName("/Game/Characters/Hero"));
AssetManagerEditor.OpenAssetAuditUI(PackageNames);
```

### 进阶用法

使用虚拟列系统查询资产的管理信息（来源：`AssetManagerEditorModule.h` 中的列名常量和查询接口）：

```cpp
#include "AssetManagerEditorModule.h"

// 查询某个资产的磁盘大小、资源大小等"虚拟列"信息
IAssetManagerEditorModule& EditorModule = IAssetManagerEditorModule::Get();

FAssetData SomeAsset = /* ... */;
FString DiskSizeText;
int64 ResourceSize = 0;

// 获取自定义列的字符串值
if (EditorModule.GetStringValueForCustomColumn(SomeAsset, IAssetManagerEditorModule::DiskSizeName, DiskSizeText))
{
    UE_LOG(LogTemp, Log, TEXT("Disk size: %s"), *DiskSizeText);
}

// 获取自定义列的整数值
if (EditorModule.GetIntegerValueForCustomColumn(SomeAsset, IAssetManagerEditorModule::ResourceSizeName, ResourceSize))
{
    UE_LOG(LogTemp, Log, TEXT("Resource size: %lld bytes"), ResourceSize);
}

// 切换当前注册表源（Editor / 目标平台 / 自定义文件）
EditorModule.SetCurrentRegistrySource(TEXT("Editor"));  // 当前编辑器
// 或加载特定平台的 registry
EditorModule.SetCurrentRegistrySource(TEXT("Windows"));  // 平台名

// 创建伪 AssetData 用于表示 Chunk 和 PrimaryAsset
FAssetData ChunkAsset = IAssetManagerEditorModule::CreateFakeAssetDataFromChunkId(0);
int32 ChunkId = IAssetManagerEditorModule::ExtractChunkIdFromFakeAssetData(ChunkAsset); // 返回 0

FPrimaryAssetId MyAssetId(FPrimaryAssetType(TEXT("Map")), FName("/Game/Maps/MainLevel"));
FAssetData PrimaryAssetData = IAssetManagerEditorModule::CreateFakeAssetDataFromPrimaryAssetId(MyAssetId);
FPrimaryAssetId ExtractedId = IAssetManagerEditorModule::ExtractPrimaryAssetIdFromFakeAssetData(PrimaryAssetData);
```

在 Slate UI 中嵌入 PrimaryAsset 选择器：

```cpp
// 创建 PrimaryAssetType 选择器（下拉框）
TSharedRef<SWidget> TypeSelector = IAssetManagerEditorModule::MakePrimaryAssetTypeSelector(
    FOnGetPrimaryAssetDisplayText::CreateLambda([]() -> FText { return FText::FromString(TEXT("MyType")); }),
    FOnSetPrimaryAssetType::CreateLambda([](FPrimaryAssetType NewType) { /* handle */ }),
    true,  // bAllowClear
    false  // bAllowAll
);

// 创建 PrimaryAssetId 选择器（带过滤）
TSharedRef<SWidget> IdSelector = IAssetManagerEditorModule::MakePrimaryAssetIdSelector(
    FOnGetPrimaryAssetDisplayText::CreateLambda([]() -> FText { return FText::FromString(TEXT("MyAsset")); }),
    FOnSetPrimaryAssetId::CreateLambda([](FPrimaryAssetId NewId) { /* handle */ }),
    true,  // bAllowClear
    { FPrimaryAssetType(TEXT("Map")) }  // AllowedTypes
);
```

## Demo 示例

以下示例展示如何在自定义编辑器模块中调用 Reference Viewer 和 Size Map：

```cpp
// MyAssetToolsModule.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyAssetToolsModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    /** 打开 Reference Viewer 查看指定资产的依赖 */
    void ShowReferencesForAsset(const FString& AssetPath);
};
```

```cpp
// MyAssetToolsModule.cpp
#include "MyAssetToolsModule.h"
#include "AssetManagerEditorModule.h"
#include "AssetRegistry/AssetIdentifier.h"

void FMyAssetToolsModule::StartupModule()
{
    // 模块启动时无需额外初始化
}

void FMyAssetToolsModule::ShutdownModule()
{
    // 清理
}

void FMyAssetToolsModule::ShowReferencesForAsset(const FString& AssetPath)
{
    if (!IAssetManagerEditorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("AssetManagerEditor module is not loaded"));
        return;
    }

    IAssetManagerEditorModule& EditorModule = IAssetManagerEditorModule::Get();

    // 将包路径转为 AssetIdentifier
    TArray<FAssetIdentifier> Identifiers;
    Identifiers.Add(FAssetIdentifier(FName(*AssetPath)));

    // 打开 Reference Viewer
    EditorModule.OpenReferenceViewerUI(Identifiers);
}

IMPLEMENT_MODULE(FMyAssetToolsModule, MyAssetTools)
```

## 模块依赖

从插件的 `.uplugin` 和模块依赖分析，本插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `ContentBrowserAssetDataSource` | 内容浏览器资产数据源接口，提供资产注册表数据 |
| `AssetRegistry` | 资产注册表核心模块，查询资产依赖/引用关系 |
| `AssetManager` | 运行时资产管理系统，提供 PrimaryAssetType/Id 和 Cook 规则 |
| `SourceControl` | 版本控制接口，Reference Viewer 中显示检出状态过滤 |
| `TreeMap` | Size Map 的树状图可视化组件 |
| `Insights` | 资产表树视图框架（TreeView 使用） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的编译警告 |
| 2026-05-12 | `0e90bdad` | Fix issue where reference viewer package name wouldn't update when recentering the graph. | 修复 Reference Viewer 重置中心后包名未更新的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为新的 UE_LOGF 宏 |
| 2026-04-08 | `9e93654f` | UE: Do not load redirectors when looking at them in the reference viewer. | Reference Viewer 中查看重定向器时不再加载它们 |
| 2026-03-26 | `b34c9d1a` | PR #14570: Fix build with clang-cl, UE_API needs to be after UE_INTERNAL. | 修复 clang-cl 编译器下 UE_API 宏位置错误导致的构建失败 |

### 维护评价

- **活跃维护**：最近 6 个月内有多次功能性更新（Reference Viewer 改进、编译修复、日志迁移）
- **长期稳定**：自 2017 年创建以来持续维护，是 UE5 资产管理体系的核心编辑器组件
- **核心依赖**：作为 `UAssetManager` 的官方编辑器界面，几乎所有使用 Asset Manager 系统的项目都隐式依赖此插件
- **推荐使用**：✅ 强烈推荐。这是 UE5 标准工作流的一部分，默认启用，无需额外配置即可使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/AssetManagerEditor)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/AssetManager/)（资产管理系统总览）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/AssetManagerEditor/Tests)（如果存在）