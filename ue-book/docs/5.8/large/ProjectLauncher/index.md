# Project Launcher

> Configure custom project launch profiles.

| 属性 | 值 |
|---|---|
| 中文名 | 项目启动器 |
| 分类 | Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ProjectLauncher` (Editor), `CommonLaunchExtensions` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2025-04-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/ProjectLauncher) | |

## 用途

本插件为 UnrealFrontend (UFE) 工具提供了一个高度可配置、可扩展的**项目启动配置系统**。它解决了传统启动配置功能单一、难以定制的问题，允许用户创建、保存和组合复杂的启动配置（Launch Profiles），用于自动化构建、部署、测试等流程。其核心设计是“树状构建器”（Tree Builder）模式，用于灵活构建启动命令和参数。

## 使用场景

- 你需要为你的项目创建一套标准化的启动流程（如：构建特定平台、部署到设备、运行特定测试）。
- 你的团队需要一个图形化界面来管理和共享不同的启动配置，而不仅仅是命令行参数。
- 你需要通过插件或脚本扩展启动流程，添加自定义的步骤或参数校验。
- 你在使用 UnrealFrontend (UFE) 进行项目管理、测试和部署。

## 蓝图用法

本插件主要为编辑器工具 (UnrealFrontend) 提供后端支持，未发现公开的蓝图节点。

## C++ 用法

本插件提供了一套 C++ API 用于构建和扩展启动配置系统。

### 头文件引入

```cpp
#include "ProjectLauncher.h"
```

### 基本用法

基于模块设计，主要使用 `ProjectLauncher` 和 `CommonLaunchExtensions` 模块提供的类来定义或使用启动配置。具体 API 需参考子模块文档。

### 进阶用法

通过 `CommonLaunchExtensions` 模块，可以扩展或覆盖默认的启动行为，例如添加自定义的设备发现、配置校验或后处理步骤。

## Demo 示例

一个完整的最小使用示例涉及创建自定义的 `ILauncherExtension` 并注册到系统中。具体实现细节请参考 `CommonLaunchExtensions` 模块中的现有扩展作为范例。

## 模块依赖

从模块类型和名称推断，本插件依赖编辑器和开发者工具模块。

| 模块 | 用途 |
|---|---|
| `ProjectLauncher` | 核心启动器框架与配置管理 |
| `CommonLaunchExtensions` | 内置的常用启动流程扩展（如设备管理、同步等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `4225c8f8` | Remove the restriction from Project Launcher that prevents package & deploy to be specified together | 移除了打包和部署不能同时进行的限制 |
| 2026-04-27 | `77966850` | Launcher2: Use the value of bUseZenStore from ProjectSettings when deciding whether to pass -ZenStor | 启动时根据项目设置决定是否传递 ZenStore 参数 |
| 2026-04-17 | `921928f4` | Add support for skipping content when downloading staged build via Project Launcher 2 Build Sync ext | 为构建同步扩展添加了跳过特定内容下载的功能 |
| 2026-04-16 | `9870b120` | Declare that several Developer modules only support desktop platforms | 声明多个开发者模块仅支持桌面平台 |
| 2026-04-14 | `c58ad33c` | Project Launcher now allows you to select maps that are in plugins. | 启动器现在允许选择插件中的地图 |

### 维护评价

- **活跃维护**：插件非常新（约1年），且在近期（2026年4-5月）有多次功能性更新和增强。
- **实验性**：插件标记为 `IsBetaVersion=true`，表明仍处于积极开发阶段，API 和功能可能发生变化。
- **推荐使用**：对于需要在 UnrealFrontend 中实现复杂启动流程的用户和团队，这是一个值得尝试的实验性工具。鉴于其活跃的开发状态，建议关注其后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/ProjectLauncher)
- [ProjectLauncher 模块文档](ProjectLauncher.md)
- [CommonLaunchExtensions 模块文档](CommonLaunchExtensions.md)