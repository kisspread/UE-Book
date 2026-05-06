# Tool Presets

> Adds support for saving and loading tool settings as presets.

| 属性 | 值 |
|---|---|
| 中文名 | 工具预设 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（预设资产类型） |
| 模块 | `ToolPresetAsset` (Editor), `ToolPresetEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-08-01 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ToolPresets) | |

## 用途

Tool Presets 插件允许用户将交互式工具（如建模、绘制、编辑工具）的当前设置状态捕获并保存为预设，以便后续快速恢复和复用。它解决了在频繁调整工具参数时缺乏持久化存储的问题，让艺术家和设计师可以管理多组工具配置，并在不同任务间切换。

该插件提供了一套数据资产结构，用于存储每个工具的多组预设（包括序列化属性）、标签、工具提示以及工具图标，并通过编辑器子系统自动维护一个默认预设集合。

## 使用场景

- 在建模编辑器中，需要为不同几何体类型保存不同的雕刻笔刷设置。
- 在材质编辑器中，保存多组材质参数预设，方便在不同场景下快速应用。
- 在一个团队项目中，共享经过验证的工具配置以减少手动调参时间。

## 蓝图用法

由于预设管理主要涉及资产创建和序列化操作，该插件没有暴露直接的蓝图可调用函数。但在蓝图中可以访问预设资产对象的属性：

- **读取预设集合**：通过 `GetDefaultCollection()`（C++ 方法）或直接加载 `UInteractiveToolsPresetCollectionAsset` 资产，读取 `PerToolPresets` 映射。
- **修改预设**：直接设置 `FString Label` 和 `FString Tooltip` 字段，以及调用 `SetStoredPropertyData` / `LoadStoredPropertyData`（需通过 C++ 调用）。

因此蓝图端主要通过引用资产对象并遍历其数据结构来获取预设信息。

## C++ 用法

### 头文件引入

```cpp
#include "ToolPresetAsset.h"
#include "ToolPresetAssetSubsystem.h"
```

### 基本用法

通过编辑器子系统获取默认预设集合，并添加一个预设定义：

```cpp
// Source: Engine/Plugins/Experimental/ToolPresets/Source/ToolPresetAsset/Private/... (示例)

void FMyTool::SavePreset(UInteractiveToolsPresetCollectionAsset* Collection, const FString& ToolName, const FString& PresetLabel)
{
    // 获取或创建该工具对应的预设存储
    FInteractiveToolPresetStore* Store = Collection->PerToolPresets.Find(ToolName);
    if (!Store)
    {
        Store = &Collection->PerToolPresets.Add(ToolName);
        Store->ToolLabel = FText::FromString(ToolName);
    }

    // 创建新预设定义
    FInteractiveToolPresetDefinition NewPreset;
    NewPreset.Label = PresetLabel;
    NewPreset.Tooltip = TEXT("My preset for " + ToolName);

    // 将当前工具设置属性序列化到预设
    TArray<UObject*> ToolSettingsObjects = GetToolSettings(); // 用户自定义
    NewPreset.SetStoredPropertyData(ToolSettingsObjects);

    Store->NamedPresets.Add(NewPreset);

    // 保存资产
    Collection->MarkPackageDirty();
}
```

### 进阶用法

使用编辑器子系统确保默认集合可用，并加载预设应用到工具：

```cpp
// Source: Engine/Plugins/Experimental/ToolPresets/Source/ToolPresetEditor/Private/... (示例)

#include "ToolPresetAssetSubsystem.h"
#include "InteractiveToolsPresetCollectionAsset.h"

void FMyTool::LoadPreset(const FString& ToolName, const FString& PresetLabel)
{
    UToolPresetAssetSubsystem* PresetSubsystem = GEditor->GetEditorSubsystem<UToolPresetAssetSubsystem>();
    if (!PresetSubsystem) return;

    UInteractiveToolsPresetCollectionAsset* DefaultCollection = PresetSubsystem->GetDefaultCollection();
    if (!DefaultCollection) return;

    FInteractiveToolPresetStore* Store = DefaultCollection->PerToolPresets.Find(ToolName);
    if (!Store) return;

    for (FInteractiveToolPresetDefinition& Preset : Store->NamedPresets)
    {
        if (Preset.Label == PresetLabel)
        {
            TArray<UObject*> ToolSettingsObjects = GetToolSettings();
            Preset.LoadStoredPropertyData(ToolSettingsObjects);
            break;
        }
    }
}
```

## Demo 示例

一个完整的、可编译的最小示例如下：

**MyToolPresetDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "InteractiveToolsPresetCollectionAsset.h"
#include "ToolPresetAssetSubsystem.h"

class FMyToolPresetDemo
{
public:
    void SaveMyToolPreset(const FString& PresetName);
    void LoadMyToolPreset(const FString& PresetName);
};
```

**MyToolPresetDemo.cpp**
```cpp
#include "MyToolPresetDemo.h"
#include "Engine/Engine.h"

void FMyToolPresetDemo::SaveMyToolPreset(const FString& PresetName)
{
    UToolPresetAssetSubsystem* Subsystem = GEditor->GetEditorSubsystem<UToolPresetAssetSubsystem>();
    if (!Subsystem) return;

    UInteractiveToolsPresetCollectionAsset* Collection = Subsystem->GetDefaultCollection();
    if (!Collection) return;

    const FString ToolName = TEXT("MyDemoTool");
    FInteractiveToolPresetStore& Store = Collection->PerToolPresets.FindOrAdd(ToolName);
    Store.ToolLabel = FText::FromString(ToolName);

    FInteractiveToolPresetDefinition Preset;
    Preset.Label = PresetName;
    Preset.Tooltip = TEXT("Demo preset");

    // 假设有一个工具设置对象数组
    TArray<UObject*> DummySettings;
    // DummySettings.Add(SomeToolSettings);
    Preset.SetStoredPropertyData(DummySettings);

    Store.NamedPresets.Add(Preset);
    Collection->MarkPackageDirty();

    Subsystem->SaveDefaultCollection();
}

void FMyToolPresetDemo::LoadMyToolPreset(const FString& PresetName)
{
    UToolPresetAssetSubsystem* Subsystem = GEditor->GetEditorSubsystem<UToolPresetAssetSubsystem>();
    if (!Subsystem) return;

    UInteractiveToolsPresetCollectionAsset* Collection = Subsystem->GetDefaultCollection();
    if (!Collection) return;

    FInteractiveToolPresetStore* Store = Collection->PerToolPresets.Find(TEXT("MyDemoTool"));
    if (!Store) return;

    for (FInteractiveToolPresetDefinition& Preset : Store->NamedPresets)
    {
        if (Preset.Label == PresetName)
        {
            TArray<UObject*> DummySettings;
            // DummySettings.Add(SomeToolSettings);
            Preset.LoadStoredPropertyData(DummySettings);
            break;
        }
    }
}
```

注意：实际使用时需要将 `DummySettings` 替换为有效的工具设置对象，并确保它们继承了 `UObject` 且其属性带有 `EditorConfig` 元数据标记（因为预设序列化基于 `EditorConfigBase`）。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EditorConfigBase` | 提供 `UEditorConfigBase` 基类和编辑器配置序列化支持 |
| `AssetTools` | 提供资产定义注册和工厂类 |

其余依赖均为标准编辑器插件常见模块（Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore, UnrealEd, PropertyEditor, Projects, DeveloperSettings）。

## 维护状态

### 近期更新

- 2025-07-10 `9803c443` 添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 到有对应 .gen.cpp 的源文件
- 2025-05-31 `52e3dac1` 更新头文件，修复 DLL 存储导出方法/静态变量的设置
- 2024-11-15 `a2c3875d` 清理全项目中的 FSlateFontInfo 构造函数，弃用字体路径用法
- 2024-05-01 `a2b56134` Slate: 弃用 SListView::ItemHeight 和 STreeViewItemHeight
- 2023-08-01 `37e43345` 修复：重命名预设管理器中的用户集合时，名称中包含空格的问题

### 维护评价

- **创建时间**：2023年8月，距今约2年，仍算较新的插件。
- **更新频率**：最近一年内有数次实质性更新（包括功能修复和编译适配），最近一次在2025年7月，说明项目仍然活跃维护。
- **限制与推荐**：插件处于实验性状态，数据结构设计明确标记为临时性（TODO注释），API可能在未来变更。但核心功能已经可用，适合需要简单工具预设管理的项目。推荐在个人或小型团队项目中试用，生产环境需注意兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ToolPresets)
- [官方文档](https://docs.unrealengine.com/5.3/en-US/tool-presets/)（5.3版本开始引入）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ToolPresets/Tests)（未找到独立测试目录，功能测试可能集成在编辑器自动化框架中）