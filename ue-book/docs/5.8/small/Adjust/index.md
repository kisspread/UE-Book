# Adjust Analytics Provider

> Adjust Analytics Provider（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Adjust 分析 |
| 分类 | Analytics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AdjustEditor` (Editor), `AndroidAdjust` (Runtime), `IOSAdjust` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-06-08 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/Adjust) | |

## 用途

此插件提供了一个 UE5 分析框架的提供商实现，专门用于集成第三方服务 Adjust 的移动分析 SDK。它的主要功能是简化在 Android 和 iOS 移动平台上初始化、配置和启动 Adjust SDK 的过程，使得 UE5 项目可以自动将用户行为、广告归因等事件发送到 Adjust 的后端进行分析。

**解决的问题**：为 UE5 项目提供一个标准化的方式，将 Adjust 移动分析 SDK 集成到项目中，避免了开发者手动编写复杂的平台特定初始化代码。

## 使用场景

- 你的 UE5 项目面向 **Android 或 iOS** 移动平台，并且需要集成 **Adjust** 作为第三方分析服务来追踪用户行为、广告转化和归因。
- 你需要在游戏启动时自动初始化 Adjust SDK，并根据游戏内事件（如关卡完成、购买）发送自定义分析事件。

## 蓝图用法

该插件主要提供运行时服务，其核心功能通过 C++ 接口初始化。从其模块结构（Editor 模块名为 `AdjustEditor`）判断，其编辑器部分可能提供项目设置界面，但插件本身不暴露蓝图可调用函数。分析功能的调用通常通过其他分析管理器（如 `UEngine` 内置的分析系统）间接完成。

## C++ 用法

### 头文件引入

由于插件功能主要由引擎的分析系统在启动时调用，使用者通常不直接引入该插件的头文件。若需进行高级配置，可引用：
```cpp
#include "AdjustEditor.h" // 仅用于编辑器环境下的配置
```

### 基本用法

插件的使用主要通过引擎配置（`DefaultEngine.ini`）完成，而非直接调用 C++ API。你需要提供 Adjust 的 `AppToken` 和其他配置。

**配置示例** (`DefaultEngine.ini`):
```ini
[/Script/AndroidAdjust.AndroidAdjustSettings]
AppToken=YOUR_ANDROID_APP_TOKEN

[/Script/IOSAdjust.IOSAdjustSettings]
AppToken=YOUR_IOS_APP_TOKEN
```

插件会在引擎初始化（`PreDefault` 阶段）时，根据当前平台自动加载对应的模块（`AndroidAdjust` 或 `IOSAdjust`），并使用配置的参数启动 Adjust SDK。

## Demo 示例

此插件为配置驱动型插件，无需编写额外代码。一个完整的集成示例是：

1.  启用 `Adjust` 插件（在编辑器插件管理器或 `.uproject` 文件中）。
2.  在项目设置中填写 Adjust 相关的凭证（AppToken, Secret等）。
3.  打包并运行在 Android 或 iOS 设备上，插件会自动工作。

## 模块依赖

从 Build.cs 分析，使用此插件**无需**在你的项目模块中添加特殊依赖。它自给自足，仅依赖于 UE 引擎的核心分析框架。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Analytics 框架） | 插件自身实现了 `IAnalyticsProviderModule` 接口，与引擎分析系统集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移至新的 UE_LOGF 宏，统一日志格式。 |
| 2026-01-27 | `113268fe` | Fixed include casing mismatch when compiling ios with case sensitive on | 修复 iOS 平台大小写敏感编译时头文件包含不匹配的错误。 |
| 2026-01-14 | `1a097717` | Fix IOS CIS Issues. | 修复 iOS 平台的持续集成（CI）编译问题。 |
| 2025-04-04 | `dce44a87` | Proper fix for analytics check() being replaced with a log. Moved definition of the logging function | 正确修复了分析检查函数被日志替换的问题，并移动了日志函数定义。 |
| 2024-02-06 | `c02789b4` | [Backout] - CL31042395 | 撤销了编号为 CL31042395 的更改。 |

### 维护评价

该插件创建于 2017 年，历史较长。从近期提交记录看，它仍在被维护，但更新主要集中在**编译修复、日志系统迁移和代码质量改进**，而非功能性的重大升级。最近的实质性功能更新信息在提供的记录中不明显。

**综合评价**：这是一个稳定但非核心的插件。它持续得到维护以保持与最新引擎版本的兼容性，但本身功能相对固定。对于需要集成 Adjust 的移动项目，它是一个可靠但可能功能选择有限的选择。推荐在确认 Adjust SDK 满足项目需求的前提下使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/Adjust)
- [官方文档](https://docs.unrealengine.com/latest/INT/Gameplay/Analytics/index.html)
- [测试用例]（未在提供信息中发现明确的插件专属测试文件）