# Live Update for Slate

> Refreshes the editor layout and tabs when Live Coding is complete

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | 是 |
| 包含内容 | 是 |
| 模块 | LiveUpdateForSlate (Editor) |
| 创建时间 | 2022-11-29 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/LiveUpdateForSlate) | |

## 用途

LiveUpdateForSlate 解决了一个非常具体的痛点：当你使用 **Live Coding**（热重载 C++ 代码）修改了 Slate 相关的代码后，编辑器的 UI 布局和控件不会自动刷新。你需要手动关闭再重新打开编辑器窗口才能看到变更效果。

这个 plugin 监听 Live Coding 的 patch 完成事件，自动执行以下操作：

1. **保存当前编辑器布局状态**（所有已打开的标签页位置和停靠状态）
2. **重新加载编辑器布局配置文件**
3. **重建整个主框架**（Main Frame），使 Slate 控件代码变更生效
4. **重新打开之前已打开的资产编辑器**

整个过程对用户透明——Live Coding patch 完成后，编辑器 UI 会自动刷新，无需手动操作。

## 使用场景

- 你正在开发自定义的 Slate 编辑器面板/停靠标签页，使用 Live Coding 迭代 UI 代码
- 你修改了编辑器扩展中的 Slate 控件样式或布局逻辑，希望立即看到效果
- 你不想每次改代码都重启编辑器来验证 Slate UI 变更

**前置条件**：项目必须启用 **Live Coding**（`bWithLiveCoding = true`），否则此 plugin 不会有任何效果。

## 蓝图用法

此 plugin 不暴露任何蓝图接口。它是一个纯编辑器模块，通过自动挂接 Live Coding 的 delegate 来工作，无需蓝图调用。

## C++ 用法

### 概述

此 plugin 的设计目标是"安装即忘"（install and forget）。用户不需要编写任何 C++ 代码来使用它。插件在编辑器启动时自动挂接 Live Coding 的 `OnPatchComplete` 委托，patch 完成后自动重建 Slate。

### 核心机制

源码位于 `LiveUpdateForSlate.cpp`，核心逻辑如下：

```cpp
// 监听 Live Coding 的 patch 完成事件
void FLiveUpdateForSlateModule::StartupModule()
{
    // 注册设置面板 (Editor > Plugins > Live Update for Slate)
    SettingsModule->RegisterSettings("Editor", "Plugins", "Live Update for Slate", ...);

#if WITH_LIVE_CODING
    if (ILiveCodingModule* LiveCoding = FModuleManager::LoadModulePtr<ILiveCodingModule>(LIVE_CODING_MODULE_NAME))
    {
        OnPatchCompleteHandle = LiveCoding->GetOnPatchCompleteDelegate().AddRaw(this, &FLiveUpdateForSlateModule::OnPatchComplete);
    }
#endif
}

// Patch 完成后自动重建 Slate
void FLiveUpdateForSlateModule::OnPatchComplete()
{
    // 检查用户是否在设置中启用了此功能
    if (!Settings->bEnableLiveUpdateForSlate) return;

    // 1. 保存所有打开的标签页状态
    FGlobalTabmanager::Get()->SaveAllVisualState();

    // 2. 重新加载布局配置
    GConfig->Flush(bRead, GEditorLayoutIni);

    // 3. 记录当前打开的资产编辑器
    TArray<UObject*> OpenedAssets = Subsystem->GetAllEditedAssets();

    // 4. 重建主框架（触发 Slate 重新加载）
    MainFrameModule.RecreateDefaultMainFrame(false, false);

    // 5. 重新打开之前的资产编辑器
    for (const UObject* Asset : OpenedAssets)
    {
        Subsystem->OpenEditorForAsset(Asset);
    }
}
```

### 设置

插件通过 `ULiveUpdateSlateSettings` 暴露一个配置项，可在 **编辑器偏好设置 → Plugins → Live Update for Slate** 中找到：

| 设置项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bEnableLiveUpdateForSlate` | bool | `true` | 是否在 Live Coding patch 完成后自动刷新 Slate 布局 |

设置存储在 `EditorPerProjectUserSettings` 配置文件中（per-project per-user）。

## Demo 示例

此 plugin 无需编写代码。使用方式：

1. 在插件浏览器（Edit → Plugins）中确认 **Live Update for Slate** 已启用
2. 确保项目启用了 Live Coding（Edit → Editor Preferences → Live Coding）
3. 编写或修改 Slate 相关的编辑器扩展代码
4. 按 **Ctrl+Alt+F11** 触发 Live Coding patch
5. Patch 完成后，编辑器 UI 会自动重建并反映你的代码变更

如果你不想自动刷新（例如正在调试布局问题），可以在设置中将 `bEnableLiveUpdateForSlate` 设为 `false`。

## 模块依赖

此 plugin 本身依赖以下模块（来自 `LiveUpdateForSlate.Build.cs`）：

| 模块 | 用途 |
|---|---|
| `Core` | 基础功能（公共依赖） |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `MainFrame` | 编辑器主框架重建 (`RecreateDefaultMainFrame`) |
| `Settings` | 编辑器设置注册 |
| `SettingsEditor` | 设置编辑器 UI |
| `Slate` | Slate UI 框架 |
| `SlateCore` | Slate 核心类型 |
| `UnrealEd` | 编辑器子系统 (`UAssetEditorSubsystem`) |
| `LiveCoding` | Live Coding 模块（条件依赖，仅当 `bWithLiveCoding=true`） |

**使用者注意**：这是一个独立的 Editor 插件，不需要你的项目模块额外依赖任何东西。只需在插件浏览器中启用即可。

## 维护状态

### 近期更新

仅有 1 次 commit（即创建时的提交）：

| 日期 | Commit | 说明 |
|---|---|---|
| 2022-11-29 | `b4fe0fa7` | 初始添加：Live Coding 完成后刷新 Mainframe 和 Slate 控件（社区贡献者 Sythenz） |

### 维护评价

- ⚠️ **自 2022 年 11 月创建以来从未更新过**
- 功能非常简单（仅 84 行 .cpp），代码逻辑清晰且自包含
- 由社区成员 Sythenz 贡献，后被 Epic 合并到引擎中
- 虽然超过 3 年没有更新，但由于功能足够简单且核心 API（`ILiveCodingModule`、`RecreateDefaultMainFrame`）保持稳定，目前仍然可以正常工作
- 没有已知的 bug 或废弃标记
- **推荐使用**：如果你使用 Live Coding 开发 Slate 相关代码，这是一个非常实用的小工具，几乎零配置

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/LiveUpdateForSlate)
- [头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Editor/LiveUpdateForSlate/Source/LiveUpdateForSlate/Public/LiveUpdateForSlate.h)
- [实现](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Editor/LiveUpdateForSlate/Source/LiveUpdateForSlate/Private/LiveUpdateForSlate.cpp)
- [设置类](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Editor/LiveUpdateForSlate/Source/LiveUpdateForSlate/Public/LiveUpdateSlateSettings.h)
