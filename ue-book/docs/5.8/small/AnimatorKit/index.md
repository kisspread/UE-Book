# Animator Kit

> Utilities for Animating in Unreal with Sequencer

| 属性 | 值 |
|---|---|
| 中文名 | 动画师工具包 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（动画辅助绑定、变形器绑定、物理绑定） |
| 模块 | `AnimatorKitSettings` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-03 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimatorKit) | |

## 用途

AnimatorKit 是 Epic 为动画师在 Sequencer 中工作提供的辅助工具集合。它不是一个运行时功能插件，而是一套**动画师工作流加速器**——通过提供预设的辅助绑定（Helper Rigs）、变形器绑定（Deformer Rigs）和物理绑定（Physics Rigs），让动画师在 Sequencer 中调动画时更高效。

插件的核心是一个基于项目级设置的配置系统，允许用户开关 Focus Mode（聚焦模式），帮助动画师在复杂场景中只关注当前编辑的动画对象。设置变更通过多播委托广播，确保系统各处同步响应。

**为什么存在？** 在 Sequencer 中做角色动画时，动画师经常需要辅助骨骼、IK 控制器、物理模拟等工具。AnimatorKit 将这些常用工具打包为插件，并提供聚焦模式等编辑体验优化，降低动画师的配置门槛。

## 使用场景

- 你在 Sequencer 中为角色调关键帧动画，需要辅助 IK 控制器 → 用 AnimatorKit 的 Helper Rigs
- 你需要在 Sequencer 中预览布料/物理效果配合动画 → 用 AnimatorKit 的 Physics Rigs
- 你在复杂场景中做动画，想隐藏无关元素只关注当前角色 → 启用 AnimatorKit 的 Focus Mode
- 你需要变形器辅助（如面部表情）绑定 → 用 AnimatorKit 的 Deformer Rigs

## 蓝图用法

AnimatorKit 主要是设置驱动型插件，公共蓝图 API 较少。其配置通过 **项目设置 → Animation Settings → Focus** 面板进行。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `bEnableFocusMode` | 是否启用动画聚焦模式 | `UAnimatorKitSettings` |

### 使用示例（蓝图描述）

AnimatorKit 主要通过编辑器设置面板使用：

1. 打开 **编辑 → 项目设置 → 插件 → Animator Kit Settings**
2. 在 **Animation Settings → Focus** 分类下找到 **Enable Focus Mode** 复选框
3. 勾选后，Sequencer 中将启用聚焦模式，自动淡化非当前编辑对象

设置也可通过控制台变量 `AnimMode.PendingFocusMode` 动态切换。

## C++ 用法

### 头文件引入

```cpp
#include "AnimatorKitSettings.h"
```

### 基本用法

监听 AnimatorKit 设置变更事件，当用户在项目设置中修改 Focus Mode 时做出响应：

```cpp
// 订阅设置变更委托
UAnimatorKitSettings::OnSettingsChange.AddLambda([](const UAnimatorKitSettings* Settings)
{
    if (Settings)
    {
        UE_LOG(LogAnimation, Log, TEXT("Focus Mode: %s"), 
            Settings->bEnableFocusMode ? TEXT("Enabled") : TEXT("Disabled"));
    }
});
```

### 进阶用法

通过 CDO 访问当前设置值，以及通过控制台变量动态修改：

```cpp
// 读取当前 Focus Mode 设置
const UAnimatorKitSettings* Settings = GetDefault<UAnimatorKitSettings>();
bool bIsFocusModeActive = Settings->bEnableFocusMode;

// 通过控制台变量动态修改（等价于修改 UPROPERTY(config)）
static IConsoleVariable* FocusModeCVar = IConsoleManager::Get().FindConsoleVariable(TEXT("AnimMode.PendingFocusMode"));
if (FocusModeCVar)
{
    FocusModeCVar->Set(true);  // 启用聚焦模式
}
```

> **来源**：`Source/AnimatorKitSettings/Public/AnimatorKitSettings.h`

## Demo 示例

一个监听 AnimatorKit 设置变更的最小模块示例：

```cpp
// MyAnimHelper.h
#pragma once

#include "CoreMinimal.h"

class FMyAnimHelper
{
public:
    void Initialize();
    void Shutdown();

private:
    FDelegateHandle SettingsDelegateHandle;
    void OnAnimatorKitSettingsChanged(const class UAnimatorKitSettings* InSettings);
};
```

```cpp
// MyAnimHelper.cpp
#include "MyAnimHelper.h"
#include "AnimatorKitSettings.h"

void FMyAnimHelper::Initialize()
{
    SettingsDelegateHandle = UAnimatorKitSettings::OnSettingsChange.AddRaw(
        this, &FMyAnimHelper::OnAnimatorKitSettingsChanged);
}

void FMyAnimHelper::Shutdown()
{
    UAnimatorKitSettings::OnSettingsChange.Remove(SettingsDelegateHandle);
}

void FMyAnimHelper::OnAnimatorKitSettingsChanged(const UAnimatorKitSettings* InSettings)
{
    if (InSettings && InSettings->bEnableFocusMode)
    {
        UE_LOG(LogTemp, Log, TEXT("AnimatorKit Focus Mode 已启用"));
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。

AnimatorKitSettings 模块继承自 `UDeveloperSettings`，仅依赖 UE 核心框架模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-17 | `1a5b88cf` | [AnimatorKit] Add physics rigs. Fixed bad reference. | 新增物理绑定，修复错误引用 |
| 2026-04-15 | `cf2bf43d` | [AnimatorKit] - Update plugin settings and icon | 更新插件设置和图标 |
| 2025-07-12 | `3413adf5` | Ran UnrealCodeFixup to fix dll storage | 修复 DLL 导出符号存储 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files... | 源文件添加内联生成宏 |
| 2025-01-16 | `dbb55c1b` | Animation mode & AnimatorKit: fixed focus mode value propagation | 修复聚焦模式值传播问题 |

### 维护评价

**活跃维护中**。AnimatorKit 于 2024 年 9 月创建，至今约 2 年。从 git 历史看：

- **2026 年 4 月**仍有多次实质性更新（新增 Physics Rigs、更新设置和图标），表明插件仍在积极开发
- 标记为 `IsBetaVersion: true`，说明功能仍在迭代中，API 可能变化
- 默认启用（`EnabledByDefault: true`），说明 Epic 将其视为标准动画工具链的一部分
- 作为较新的插件（2024 年创建），还在快速完善阶段

⚠️ **注意**：该插件标记为 Beta 版本，设置类 meta 中包含 `Experimental` 标记，API 可能在后续版本中变更。建议关注版本更新日志。

**推荐使用**：如果你在 Sequencer 中做动画工作，这是一个值得启用的官方工具。但需注意其 Beta 状态，避免在关键生产流程中过度依赖其特定实现细节。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimatorKit)
- 官方文档：暂无
- 测试用例：暂无公开测试用例