# Console Variables Editor

> Save, load and control Console Variables (cvars) from this panel using Slate.

| 属性 | 值 |
|---|---|
| 中文名 | 控制台变量编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（配置资源） |
| 模块 | `ConsoleVariablesEditor` (UncookedOnly), `ConsoleVariablesEditorRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（年龄未知） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ConsoleVariablesEditor) | |

## 用途

该插件提供了一个集成在编辑器中的 Slate 面板，用于集中管理控制台变量（Console Variables， CVars）。它解决的核心问题是**在复杂项目（尤其是虚拟制片）中，参数的可视化管理、团队共享与持久化配置**。

传统上，开发者需要通过控制台命令手动输入和记忆众多的 CVars。此插件将这一过程图形化，允许用户将特定的 CVar 集合保存为预设（Presets），方便在不同场景（如角色光照、环境渲染、性能调试）间快速切换。其运行时模块进一步确保了配置的持久化和跨会话同步，与多用户编辑（Concert）集成，支持团队协作。

## 使用场景

- **虚拟制片项目协调**：在电影或广告的虚拟制片现场，不同部门（如灯光、渲染、特效）需要实时调整引擎参数。使用此插件可以保存和加载不同部门的参数预设，避免现场混乱。
- **团队开发与参数共享**：团队成员可以各自保存针对特定调试任务的 CVar 集合，并通过源码或共享配置文件进行分发，确保环境一致性。
- **调试与性能测试**：快速创建并切换用于不同测试目的（如 CPU 性能、GPU 性能、特定功能开关）的参数预设，提升调试效率。

## 模块列表

- **`ConsoleVariablesEditor` (UncookedOnly)**：编辑器模块，负责提供 Slate 用户界面、预设的编辑与管理逻辑。
- **`ConsoleVariablesEditorRuntime` (Runtime)**：运行时模块，负责 CVar 配置的存储、加载逻辑，并暴露蓝图和 C++ API，确保配置在打包后的程序中依然有效。

## 蓝图用法

运行时模块 (`ConsoleVariablesEditorRuntime`) 提供了蓝图接口，主要用于在运行时加载和应用预设。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Load Preset` | 根据名称加载一个预设并应用其中的 CVar 设置。 | `UConsoleVariablesEditorFunctionLibrary` |
| `Save Preset` | 将当前所有 CVar 状态保存到指定名称的预设中。 | `UConsoleVariablesEditorFunctionLibrary` |
| `Get Preset Names` | 获取所有已保存的预设名称列表。 | `UConsoleVariablesEditorFunctionLibrary` |

## C++ 用法

### 基本用法

主要使用运行时模块的功能库来程序化地管理 CVar 预设。

```cpp
// 头文件引入
#include "ConsoleVariablesEditorFunctionLibrary.h"

// 示例：保存当前 CVar 状态到名为 “MyDebugPreset” 的预设
UConsoleVariablesEditorFunctionLibrary::SaveConsoleVariablePreset(TEXT("MyDebugPreset"));

// 示例：加载并应用预设
UConsoleVariablesEditorFunctionLibrary::LoadConsoleVariablePreset(TEXT("MyDebugPreset"));
```

## 模块依赖

此插件依赖于多个用于多用户编辑和协作的 Concert 插件，是其核心功能的一部分。

| 模块 | 用途 |
|---|---|
| `ConcertSyncClient` | 提供多用户编辑的客户端连接与同步能力。 |
| `ConcertSyncCore` | 提供多用户编辑的核心数据模型与同步协议。 |
| `ConcertMain` | 多用户编辑的主要界面和基础框架。 |
| `ConcertSharedSlate` | 提供多用户编辑界面中共享的 Slate 控件。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the... | 虚拟制片资产分类重组，插件可能因此调整了所属分类或资源路径。 |
| 2026-05-12 | `de91208d` | CVAR Editor - Copy/Paste Cosmetic Fixes | 修复了 CVar 编辑器中复制/粘贴功能的外观问题。 |
| 2026-04-22 | `0f1a8af2` | Copy / Paste support for Console Variable Editor | 为 CVar 编辑器新增了复制和粘贴功能。 |
| 2026-04-14 | `c19c7e83` | [ContentBrowser] New Add Menu Misc Menu | 内容浏览器“添加”菜单更新，可能影响插件资产的创建入口。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，属于代码维护和现代化更新。 |

### 维护评价

该插件维护状态**非常活跃**。从近期提交记录看（集中在 2026 年 4-5 月），开发团队正在持续为其添加新功能（如复制粘贴）、修复问题并优化用户体验。作为 Virtual Production 分类下的核心工具，它显然是 Epic 重点维护的插件之一。

插件设计成熟，分为编辑器和运行时模块，架构清晰。集成多用户编辑（Concert）功能表明其面向协作的严肃生产环境。**强烈推荐**在需要管理大量 CVars 或进行团队协作的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ConsoleVariablesEditor)
- [官方文档]()（暂无）
- [测试用例]()（暂无路径）