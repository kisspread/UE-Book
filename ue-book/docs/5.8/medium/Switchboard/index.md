# Switchboard

> Launcher/Installer for the Switchboard application.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 多机同步管理器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `SwitchboardCommon` (Runtime), `SwitchboardEditor` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Switchboard) | |

## 用途

Switchboard 是一个独立的外部应用程序（使用 Python 和 Qt 开发），其插件部分（即本插件）为 Switchboard 提供与 Unreal Engine 编辑器交互的桥梁和基础支持。它主要用于在虚拟制作（Virtual Production）环境中管理多个 Unreal Engine 实例（例如用于 LED 墙渲染、广播图形、多机位控制）的配置、启动、监控和同步。插件自身不直接提供蓝图或运行时游戏功能，而是作为支撑外部 Switchboard 应用运行的必要组件。

## 使用场景

- 你在使用虚拟制片技术，需要同时控制一个主控机（运行 Switchboard）和多个渲染机（运行 UE）来为 LED 墙或实时合成生成画面 → 使用 Switchboard 来集中配置、启动和监控所有实例。
- 你需要在拍摄现场快速调整多个渲染节点的设置（如渲染分辨率、摄像机数据流、Live Link 源） → 通过 Switchboard 的图形界面统一管理，避免手动逐个修改。
- 你正在搭建一个广播级或高质量的实时图形渲染流水线，需要确保多个引擎实例间的帧同步和时间码同步 → 使用 Switchboard 进行协调。

## 蓝图用法

此插件主要作为外部应用的后端支持，其模块主要提供编辑器集成和运行时通信基础。它不直接暴露广泛的、用于游戏逻辑的蓝图节点。其功能主要通过 Switchboard 应用的用户界面来间接调用。

## C++ 用法

此插件的 C++ 代码主要服务于编辑器集成（如菜单、设置面板）和运行时通信协议。对于开发者而言，更常见的用法是修改或扩展 Switchboard 应用本身（其 Python 代码）或调整本插件提供的基础设置。

### 头文件引入

```cpp
#include "SwitchboardCommon.h"
// 或
#include "SwitchboardEditor.h"
```

## Demo 示例

此插件不提供独立的蓝图或 C++ 功能演示。其完整的用法演示是配合外部 Switchboard 应用程序。请参考 [Switchboard 官方文档](https://docs.unrealengine.com/5.0/en-US/virtual-production-camp-switchboard-getting-started/) 了解应用级别的使用教程。

## 模块依赖

基于插件模块的性质，其依赖主要包括用于编辑器扩展和网络通信的模块。具体的依赖关系需查看各模块的 `Build.cs` 文件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `75168502` | Switchboard - Fix unhandled PermissionError in Save Logs zip cleanup. | 修复了保存日志压缩清理时的权限错误。 |
| 2026-05-12 | `769529af` | Switchboard: Fix host vs remote platform handling for Linux nodes. | 修复了 Linux 节点的宿主与远程平台处理逻辑。 |
| 2026-05-12 | `603cb935` | Allow users to specify which plugins are enabled for Live Link Hub on launch. | 允许用户在启动时为 Live Link Hub 指定启用哪些插件。 |
| 2026-04-28 | `7c48f485` | Switchboard - add renamed MediaProfile module classname to MEDIAPROFILE_CLASS_NAMES so Media Profile | 将重命名的 MediaProfile 模块类名添加到支持列表，确保媒体配置文件功能正常。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |

### 维护评价

**维护状态：活跃维护中。**
尽管该插件创建于约 6 年前，并且长期处于实验性状态（`IsBetaVersion=true`，`EnabledByDefault=false`），但从 Git 历史看，其相关代码仍在持续获得更新和 bug 修复（最近的提交在 2026 年 5 月）。这表明 Epic 仍在维护此插件及其关联的 Switchboard 工具，以适配引擎版本升级和修复问题。

**建议**：对于需要使用 Switchboard 进行虚拟制作项目的团队，可以放心使用此插件。但请注意：
1.  它需要手动启用，并且需要配合外部 Switchboard 应用程序使用。
2.  它标记为实验性，意味着其 API 和功能在未来版本中可能发生不兼容的变更。
3.  由于其功能特殊，不适用于常规的游戏项目开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Switchboard)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/virtual-production-camp-switchboard-getting-started/) （Switchboard 应用整体文档）