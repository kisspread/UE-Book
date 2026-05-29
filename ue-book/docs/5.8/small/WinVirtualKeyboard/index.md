# Windows Virtual Keyboard

> Virtual Keyboard support for Windows. Requires Windows 11 26100.5061 or later

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟键盘插件 |
| 分类 | Input Devices |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WinVirtualKeyboard` (RuntimeNoCommandlet) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2025-08-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Windows/WinVirtualKeyboard) | |

## 用途

该插件为基于 Windows 的 **手持设备**（如 Surface Go 等平板）提供操作系统原生虚拟键盘的集成支持。它通过 `Windows.UI.ViewManagement.Core.CoreInputView` API 来显示、隐藏和管理虚拟键盘，并与 Unreal Engine 的输入系统对接。主要解决在手持 Windows 设备上进行文本输入时，无法方便地调出系统虚拟键盘的问题。

**重要限制**：根据首次提交记录，该功能的实现依赖于 Windows 11 的特定版本（26100.5061）中的修复。在之前的版本中，由于操作系统自身的 Bug，此插件的功能可能无法正常工作。

## 使用场景

- 你正在开发一款运行在 **Windows 平板或手持设备** 上的游戏或应用。
- 游戏或应用中包含需要玩家输入文本的界面（如聊天框、重命名、代码输入）。
- 你需要自动或手动弹出 Windows 系统自带的虚拟键盘，而不是使用 UE4 内置的触摸键盘。

## 蓝图用法

此插件主要在 C++ 层面与操作系统交互，为引擎输入系统提供支持。目前源码中未发现可直接供蓝图调用的 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。虚拟键盘的显隐通常由引擎输入系统（如文本框获得焦点时）自动管理。

## C++ 用法

插件的核心是实现 `GenericApplication` 的平台接口，通过 `CoreInputView` API 控制虚拟键盘。

### 头文件引入

```cpp
// 通常无需直接引入此模块头文件，插件通过引擎接口自动加载。
// 如果需要访问其特定类型，可引入：
#include "WinVirtualKeyboardModule.h"
```

### 基本用法

插件作为 `GenericApplication` 的扩展运行。当 `FGenericApplication` 的实例需要处理虚拟键盘相关事件时（例如文本输入控件获得焦点），此插件提供的实现会被调用。

**关键回调 (来自 `GenericApplication` 平台 API)**:
- `CoreInputView::Showing`: 键盘即将显示时被调用，引擎可据此调整视口。
- `CoreInputView::Hiding`: 键盘即将隐藏时被调用。
- `CoreInputView::OccludedRectChanged`: 键盘遮挡屏幕区域变化时被调用（插件已实现此回调）。

### 进阶用法

该插件通过 `FGenericWindowsApplication` 的继承和扩展来集成。其初始化过程会尝试获取 `CoreInputView` 实例，并注册上述回调。`WinVirtualKeyboard` 模块在 `Win64` 平台且目标非 `Server` 时（`TargetDenyList: ["Server"]`）自动加载。

## Demo 示例

以下示例展示如何在应用程序启动时检查虚拟键盘插件是否加载并可用。这不是一个直接控制键盘的示例，因为控制权主要在引擎输入系统内部。

**WinVirtualKeyboardDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FWinVirtualKeyboardDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**WinVirtualKeyboardDemo.cpp**
```cpp
#include "WinVirtualKeyboardDemo.h"
#include "Modules/ModuleManager.h"

void FWinVirtualKeyboardDemoModule::StartupModule()
{
    // 在运行时检查 WinVirtualKeyboard 模块是否被加载。
    // 这是验证插件是否在目标平台（Win64 非服务器）上生效的一种方式。
    IModuleInterface* WinVirtualKeyboardModule = FModuleManager::Get().GetModule(TEXT("WinVirtualKeyboard"));
    if (WinVirtualKeyboardModule)
    {
        UE_LOG(LogTemp, Log, TEXT("WinVirtualKeyboard 模块已成功加载。虚拟键盘功能已就绪。"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("WinVirtualKeyboard 模块未加载。虚拟键盘功能不可用。"));
    }
}

void FWinVirtualKeyboardDemoModule::ShutdownModule()
{
    // 清理代码
}

IMPLEMENT_PRIMARY_GAME_MODULE(FWinVirtualKeyboardDemoModule, WinVirtualKeyboardDemo, "WinVirtualKeyboardDemo");
```

## 模块依赖

您的项目模块无需直接依赖 `WinVirtualKeyboard` 插件模块。该插件作为引擎平台抽象层的扩展，自动为引擎的 `GenericApplication` 提供支持。

其内部依赖为：
| 模块 | 用途 |
|---|---|
| `ApplicationCore` | 访问平台核心应用功能，是扩展 `GenericApplication` 的基础。 |
| `SlateCore`, `Slate` | 处理与 UI 系统相关的虚拟键盘交互和布局调整。 |
| `Core`, `Engine` | 基础引擎功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至 `UE_LOGF`，属于代码现代化更新。 |
| 2026-02-19 | `edb605c2` | WinVirtualKeyboard can send occlusion rect to OnVirtualKeyboardShown | 实现了将键盘遮挡矩形信息传递给 `OnVirtualKeyboardShown` 回调。 |
| 2026-02-10 | `e08affa3` | remove unused cppwinrt implementation from WinVirtualKeyboard | 清理了未使用的 C++/WinRT 实现，精简代码。 |
| 2026-01-21 | `8a7dcc76` | [WinVirtualKeyboard] Implemented GenericApplication Platform API callbacks | 核心功能实现：为 `GenericApplication` 实现了平台 API 回调。 |
| 2025-11-25 | `daf9dd51` | disallow WinVirtualKeyboard on servers | 禁止在服务器目标上加载此插件。 |

### 维护评价

- **活跃度**：该插件自 2025 年 8 月创建以来，持续收到更新（最近一次在 2026 年 4 月），表明处于**活跃开发与维护**阶段。
- **成熟度**：标记为 **`IsBetaVersion: true`**，且首次提交明确指出依赖未广泛普及的 Windows 11 修复，属于**实验性功能**。
- **稳定性**：作为 Beta 插件，且涉及较新的 OS API，**稳定性可能存在风险**。其功能实现直接受限于操作系统版本。
- **推荐度**：仅推荐用于面向特定手持 Windows 设备的项目，并需接受其测试状态和平台依赖限制。**不建议在主流或需要高度稳定性的桌面 PC 项目中使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Windows/WinVirtualKeyboard)
- [官方文档] (暂无)
- [测试用例] (暂未发现)