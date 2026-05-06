# Tool Presets

> Adds support for saving and loading tool settings as presets.

| 属性 | 值 |
|---|---|
| 中文名 | 工具预设 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `ToolPresetAsset` (Editor), `ToolPresetEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-08-01 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ToolPresets) | |

## 用途

Tool Presets 插件允许用户保存和恢复编辑器工具的配置设置（如建模、雕刻等交互式工具的参数），以预设的形式在项目内共享或重用。它解决了工具参数重复配置的问题，并提供了可视化的预设管理器界面。该插件本质上是一个轻量级的编辑器扩展，依赖于预设资产系统（`ToolPresetAsset`），通过编辑器模块（`ToolPresetEditor`）提供 UI 交互和设置持久化。

## 使用场景

- 在建模或雕刻工具中需要频繁切换不同参数组合时，可将当前所有设置保存为预设。
- 团队协作时，将一组最佳实践的工具配置打包为项目预设资产，供所有成员加载。
- 个人工作流优化：为不同任务（高模雕刻、低模调整）分别保存预设，一键切换。

## 蓝图用法

该插件的主要功能在编辑器层面，未暴露面向蓝图的公开接口。底部设置类 `UToolPresetUserSettings` 和 `UToolPresetProjectSettings` 可以在项目设置中配置，但不可在蓝图中直接调用函数。因此蓝图用户无法直接操作预设的保存/加载逻辑，所有操作需通过编辑器面板手动进行。

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无 | 无公开蓝图可调用节点 | - |

## C++ 用法

### 头文件引入

```cpp
#include "IToolPresetEditorModule.h"
#include "ToolPresetSettings.h"
```

### 基本用法

打开预设编辑器面板：

```cpp
// 获取模块并调用编辑器界面显示
IToolPresetEditorModule& Module = IToolPresetEditorModule::Get();
Module.ExecuteOpenPresetEditor();
```

配置项目级预设集合（通常通过项目设置或代码初始化）：

```cpp
// 在游戏模块或编辑器模块中设置项目加载的预设集合
UToolPresetProjectSettings* Settings = GetMutableDefault<UToolPresetProjectSettings>();
if (Settings)
{
    FSoftObjectPath PresetPath = FSoftObjectPath("/Game/MyPresets/CustomPresetCollection.CustomPresetCollection");
    Settings->LoadedPresetCollections.Add(PresetPath);
    Settings->SaveConfig();
}
```

### 进阶用法

使用 `UToolPresetUserSettings` 管理用户个人启用的预设集合（EditorConfig 持久化）：

```cpp
// 初始化用户设置
UToolPresetUserSettings::Initialize();

// 获取实例
UToolPresetUserSettings* UserSettings = UToolPresetUserSettings::Get();
if (UserSettings)
{
    // 启用一个预设集合
    UserSettings->EnabledPresetCollections.Add(MyCollectionPath);
    UserSettings->bDefaultCollectionEnabled = true;
    UserSettings->SaveEditorConfig();
}
```

注：这些 API 主要用于编辑器内部代码，不建议在运行时游戏模块中调用。

## Demo 示例

本文档为插件级概述，不提供完整可编译 Demo。以下为简单示例，展示在编辑器模块中注册并使用预设管理器。

**`ToolPresetDemoModule.h`**

```cpp
#pragma once
#include "Modules/ModuleManager.h"
#include "IToolPresetEditorModule.h"

class FToolPresetDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
    
    void OpenPresetManager();
};
```

**`ToolPresetDemoModule.cpp`**

```cpp
#include "ToolPresetDemoModule.h"
#include "IToolPresetEditorModule.h"
#include "ToolPresetSettings.h"

void FToolPresetDemoModule::StartupModule()
{
    // 在编辑器模块启动时注册命令等（略）
}

void FToolPresetDemoModule::ShutdownModule()
{
}

void FToolPresetDemoModule::OpenPresetManager()
{
    // 执行预设编辑器面板
    if (IToolPresetEditorModule::IsAvailable())
    {
        IToolPresetEditorModule::Get().ExecuteOpenPresetEditor();
    }
}

IMPLEMENT_MODULE(FToolPresetDemoModule, ToolPresetDemo);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ToolPresetAsset` | 提供 `InteractiveToolsPresetCollectionAsset` 预设资产类型及其子系统 |
| `EditorStyle` (常见) | 编辑器风格图标 |
| `Slate` (常见) | 界面组件 |

其他常见依赖（如 Core, Engine, SlateCore 等）已省略。

## 维护状态

### 近期更新

- 2025-07-10 9803c44 为包含 .gen.cpp 文件的源文件添加 UE_INLINE_GENERATED_CPP_BY_NAME
- 2025-05-31 52e3dac 使用 UnrealCodeFixup 更新头文件以确保 DLL 存储位于方法/静态变量而非类型
- 2024-11-15 a2c3875 清理整个解决方案中使用字体路径的 FSlateFontInfo 构造函数（将弃用）
- 2024-05-01 a2b5613 Slate：弃用 SListView::ItemHeight 和 STreeViewItemHeight
- 2023-08-01 37e4334 ToolPresets：修复重命名用户集合时包含空格的问题

### 维护评价

插件自 2023 年引入后，持续获得维护性更新（编译适配、API 清理、弃用处理），但未出现重大功能扩展。目前处于稳定维护中，但属于实验性插件，可能存在 API 变化或未来整合进主线工具的风险。对于需要使用工具预设功能的项目来说，该插件提供了实用的基础功能，但建议谨慎依赖其内部接口（优先使用公开预设管理器 UI）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ToolPresets)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ToolPresets/Tests)（若有，未在本仓库内发现）