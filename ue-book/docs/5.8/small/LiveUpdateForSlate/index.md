# Live Update for Slate

> Refreshes the editor layout and tabs when Live Coding is complete

| 属性 | 值 |
|---|---|
| 中文名 | Slate 实时刷新 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器设置资产） |
| 模块 | `LiveUpdateForSlate` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-11-29 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/LiveUpdateForSlate) | |

## 用途

解决使用 **Live Coding**（热重载 C++ 代码）时，编辑器的 Slate UI 布局和标签页不会自动刷新的问题。

Live Coding 只替换已编译的函数体，但 Slate 的 Widget 树和编辑器布局不会随之更新，导致你修改了 UI 代码后需要手动关闭再打开标签页才能看到变化。这个插件监听 Live Coding 的 `OnPatchComplete` 事件，在补丁完成后自动请求编辑器主框架和所有 Slate Widget 刷新，省去手动操作。

## 使用场景

- 你在开发编辑器扩展或自定义 Slate 面板，频繁使用 Live Coding 测试 UI 变更
- 你希望每次 Live Coding 完成后，编辑器自动刷新显示最新布局，而不是手动重开标签页

## 蓝图用法

本插件没有暴露任何蓝图节点，仅提供一个编辑器设置项。

## C++ 用法

### 设置类

插件提供一个简单的设置类 `ULiveUpdateSlateSettings`，位于项目级用户配置中：

```cpp
// 该设置自动保存到 EditorPerProjectUserSettings
UPROPERTY(Config, EditAnywhere, Category=Slate)
bool bEnableLiveUpdateForSlate = true;
```

你可以在 **编辑器偏好设置 → Slate** 中找到该选项，控制是否启用自动刷新。

### 模块接口

`FLiveUpdateForSlateModule` 实现了 `IModuleInterface`，在 `StartupModule()` 中注册 Live Coding 的 `OnPatchComplete` 委托，在 `ShutdownModule()` 中解绑。无需手动调用，插件启用后自动工作。

## Demo 示例

本插件是纯编辑器功能，不需要用户编写任何代码。启用插件后，Live Coding 每次完成补丁，编辑器会自动刷新 Slate 布局。

如需在代码中检测/操作该功能：

```cpp
// LiveUpdateForSlate.h
#pragma once

#include "CoreMinimal.h"

// 检查插件是否加载
if (FModuleManager::Get().IsModuleLoaded("LiveUpdateForSlate"))
{
    UE_LOG(LogTemp, Log, TEXT("LiveUpdateForSlate 已加载，Live Coding 完成后将自动刷新 Slate"));
}

// 获取设置（如需编程控制）
const ULiveUpdateSlateSettings* Settings = GetDefault<ULiveUpdateSlateSettings>();
if (Settings && Settings->bEnableLiveUpdateForSlate)
{
    // Slate 自动刷新已启用
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveCoding` | 监听 Live Coding 补丁完成事件，注册 OnPatchComplete 回调 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2022-11-29 | `9387d8ec` | PR #9538: Added a plugin to refresh Mainframe and Slate Widgets when Live Coding is complete. (Contributed by Sythenz) | 首次提交：新增插件，Live Coding 完成后刷新编辑器主框架和 Slate Widget |

### 维护评价

- **创建时间**：2022-11-29，至今约 3 年
- **更新频率**：仅一次提交（初始提交），此后无任何更新
- **活跃程度**：**极低**。自创建以来零更新，无 bug 修复、无功能扩展
- **代码规模**：极小（约 900 字节），功能单一且实现简单
- **已知问题**：代码过于简单，可能未覆盖所有 Live Coding 场景（如多窗口编辑器布局的刷新）
- **推荐程度**：✅ **推荐使用**。虽然长期未更新，但功能极其简单，逻辑清晰，不太可能出现兼容性问题。使用 Live Coding 开发 Slate UI 时这是一个有用的辅助插件。

⚠️ **注意**：该插件 `Installed = false`（非默认安装），需要在插件管理器中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/LiveUpdateForSlate)
- [原始 PR #9538](https://github.com/EpicGames/UnrealEngine/pull/9538)（贡献者 Sythenz）