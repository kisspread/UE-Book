# Console Variables Editor

> Save, load and control Console Variables (cvars) from this panel using Slate.

| 属性 | 值 |
|---|---|
| 中文名 | 控制台变量编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有 |
| 模块 | `ConsoleVariablesEditor` (UncookedOnly), `ConsoleVariablesEditorRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🏛️ 文物（年龄未知） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ConsoleVariablesEditor) | |

## 用途

提供一个可停靠的Slate编辑器面板，用于集中化、可视化地管理和组织控制台变量（CVar）。它解决了在复杂项目（如虚拟制片）中需要频繁调整和同步大量CVar的痛点，允许用户将变量分组、保存为预设、进行实时调整，并支持与多用户编辑（Concert）集成，从而大幅提升了工作流效率。

## 使用场景

- **虚拟制片团队协作**：需要多个开发者和美术在同一场景中同步工作，使用此插件共享和同步一套控制台变量配置，确保所有人的预览效果一致。
- **性能调优与调试**：在开发过程中，需要快速开关大量调试变量或调整渲染、物理参数。通过编辑器面板可以直观地浏览、搜索和修改，避免了手动输入冗长的命令。
- **材质与特效预览**：美术人员需要频繁调整材质参数（如r.MaterialQualityLevel）来预览不同质量等级的效果，使用此插件可以一键切换预设配置。

## 蓝图用法

此插件主要为编辑器工具，蓝图可用的API较少。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplyPreset` | 通过字符串名称应用一个已保存的控制台变量预设。 | `UConsoleVariablesEditorFunctionLibrary` |
| `GetCurrentPresetAsConfigFile` | 将当前面板中的控制台变量设置保存到一个临时的Config文件中。 | `UConsoleVariablesEditorFunctionLibrary` |

### 使用示例（蓝图描述）

在编辑器工具蓝图中，调用 `ApplyPreset` 节点，并将预设名称（如 “LowQuality_Mobile”）作为字符串输入。这将立即在编辑器会话中应用所有关联的CVar，适用于构建自定义的性能分析工具。

## C++ 用法

此插件的C++使用场景主要在于扩展或与编辑器工具集成。

### 头文件引入

```cpp
#include "ConsoleVariablesEditorModule.h"
```

### 基本用法

获取插件模块并操作预设。

```cpp
// 来源: 模块公共接口推断
if (FConsoleVariablesEditorModule* CVarEditorModule = FModuleManager::GetModulePtr<FConsoleVariablesEditorModule>(TEXT("ConsoleVariablesEditor")))
{
    // 应用一个预设
    CVarEditorModule->ApplyPreset(TEXT("MySavedPreset"));
}
```

### 进阶用法

监听面板中的变量变化。

```cpp
// 来源: 模块公共接口推断
FConsoleVariablesEditorModule* CVarEditorModule = FModuleManager::GetModulePtr<FConsoleVariablesEditorModule>(TEXT("ConsoleVariablesEditor"));
if (CVarEditorModule)
{
    CVarEditorModule->OnConsoleVariableChanged().AddLambda([](const FString& VariableName, const FString& Value)
    {
        UE_LOG(LogTemp, Log, TEXT("CVar Changed: %s = %s"), *VariableName, *Value);
    });
}
```

## 模块依赖

从Build.cs分析，此插件的核心依赖是多用户编辑（Concert）相关模块，以实现同步功能。

| 模块 | 用途 |
|---|---|
| `ConcertSyncClient` | 用于在多用户编辑会话中作为客户端同步控制台变量状态。 |
| `ConcertSyncCore` | 提供多用户同步的核心协议和数据结构。 |
| `ConcertMain` | 多用户编辑框架的主要模块。 |
| `ConcertSharedSlate` | 提供与Concert共享的Slate UI组件。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 将插件资产归类至虚拟制片分类，属于常规资产整理迁移。 |
| 2026-05-12 | `de91208d` | CVAR Editor - Copy/Paste Cosmetic Fixes | 修复了控制台变量编辑器复制粘贴功能的UI显示问题。 |
| 2026-04-22 | `0f1a8af2` | Copy / Paste support for Console Variable Editor | 为编辑器面板添加了关键的复制和粘贴功能，提升了易用性。 |
| 2026-04-14 | `c19c7e83` | [ContentBrowser] New Add Menu Misc Menu | 与内容浏览器集成的改动，可能涉及插件资产在右键菜单中的显示。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出从UE_LOG迁移至UE_LOGF，属于代码规范更新。 |

### 维护评价

**活跃维护**。该插件作为虚拟制片（Virtual Production）工作流的核心工具之一，仍在持续接收功能更新（如近期添加的复制粘贴支持）和问题修复。Git记录显示在2026年4月至5月有多次实质性提交，表明由Epic团队在积极维护和改进。推荐在虚拟制片及需要复杂控制台变量管理的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ConsoleVariablesEditor)