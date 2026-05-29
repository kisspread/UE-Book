# Adjust Analytics Provider

> Adjust Analytics Provider（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Adjust 分析提供商 |
| 分类 | Analytics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AdjustEditor` (Editor), `AndroidAdjust` (Runtime), `IOSAdjust` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-06-08 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/Adjust) | |

## 用途

Adjust 是一个移动应用归因与分析平台（Mobile Measurement Partner, MMP），用于追踪用户安装来源、应用内事件、广告效果等。

此插件将 Adjust 的原生 SDK 封装为 UE5 的 Analytics Provider 接口，使引擎内置的 `FAnalytics` 系统能够自动将事件转发到 Adjust 后台。

**核心价值**：如果你需要在移动游戏中追踪用户获取（UA）和应用内行为数据，且使用 Adjust 作为分析平台，此插件提供了开箱即用的集成方案，无需自行编写平台原生代码。

**注意**：此插件默认不启用（`EnabledByDefault: false`），且仅支持 Android 和 iOS 平台。

## 使用场景

- 你在做一款移动游戏，需要追踪广告投放的归因效果 → 用此插件集成 Adjust
- 你需要将游戏内事件（如关卡完成、购买行为）发送到 Adjust 后台做分析 → 配置 EventMap
- 你需要在非发布版本中测试 Adjust 集成 → 启用 Sandbox 模式

## 蓝图用法

此插件没有暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 接口。所有配置通过 **项目设置 → Analytics → Adjust** 完成。

### 配置项说明

| 配置项 | 说明 |
|---|---|
| `Application token` | Adjust 后台生成的应用 Token |
| `Sandbox mode for non-distribution` | 非发布版本是否使用沙盒模式 |
| `Sandbox mode for distribution` | 发布版本是否使用沙盒模式 |
| `Logging level` | 日志级别（VERBOSE / DEBUG / INFO / WARN / ERROR / ASSERT / SUPRESS） |
| `Default tracker token` | 默认追踪器 Token（可选） |
| `Process name` | 进程名覆盖（留空则使用包名） |
| `Enable event buffering` | 事件缓冲（批量发送，约每分钟一次） |
| `Send while in background` | 后台运行时是否继续发送 |
| `Delay start (seconds)` | 首次发送延迟（最多 10 秒） |
| `Event Map` | 事件名称到 Adjust Token 的映射表 |

### 事件映射示例

在项目设置的 `EventMap` 中添加条目：

| Name | Token |
|---|---|
| `LevelComplete` | `abc123` |
| `PurchaseSuccess` | `def456` |

之后在代码中调用标准的 `RecordEvent` 时传入事件名称（如 `"LevelComplete"`），插件会自动查找对应的 Adjust Token 并发送。

## C++ 用法

此插件作为 Analytics Provider 运行，通常无需直接 C++ 调用。所有事件通过引擎标准的 `FAnalytics` 接口发送。

### 基本用法

通过引擎的 Analytics 系统记录事件：

```cpp
#include "Runtime/Analytics/Analytics/Public/Interfaces/IAnalyticsProvider.h"

// 获取当前 Analytics Provider 并发送事件
if (IAnalyticsProviderPtr Provider = FAnalytics::Get().GetDefaultConfiguredProvider())
{
    Provider->RecordEvent(TEXT("LevelComplete"), {
        {TEXT("LevelId"), TEXT("1-1")},
        {TEXT("TimeSpent"), TEXT("120")}
    });
}
```

## Demo 示例

此插件是纯配置型插件，无运行时代码需要编写。配置流程：

1. 在 Plugins 面板中启用 **Adjust Analytics Provider**
2. 重启编辑器
3. 进入 **Project Settings → Analytics → Adjust**
4. 填入 Adjust 后台的 **Application Token**
5. 配置 **Event Map** 映射表
6. 在代码中使用标准 `IAnalyticsProvider::RecordEvent()` 发送事件

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Analytics` | 引擎标准 Analytics 框架接口 |
| `AnalyticsET` | Epic Analytics 后端（AdjustEditor 模块依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 |
| 2026-01-27 | `113268fe` | Fixed include casing mismatch when compiling ios with case sensitive on | 修复 iOS 大小写敏感编译问题 |
| 2026-01-14 | `1a097717` | Fix IOS CIS Issues. | 修复 iOS CI 构建问题 |
| 2025-04-04 | `dce44a87` | Proper fix for analytics check() being replaced with a log. Moved definition of the logging function | 修复分析检查函数替换为日志的问题 |
| 2024-02-06 | `c02789b4` | [Backout] - CL31042395 | 回退之前的提交 |

### 维护评价

- **年龄**：约 8 年的老插件
- **更新频率**：最近 2 年有零星更新（2024-2026），但主要是编译修复和宏迁移，无功能性更新
- **功能状态**：功能稳定，无新增特性，属于维护模式
- **已知限制**：
  - 仅支持 Android 和 iOS
  - 默认不启用，需要手动开启
  - 无蓝图接口，所有配置通过项目设置完成
  - 插件本身不包含 Adjust 原生 SDK，需要额外集成
- **推荐使用**：如果你的项目使用 Adjust 做移动归因分析，可以使用此插件作为起点。但如果需要更丰富的 Adjust 功能（如深度链接、推送归因等），可能需要自行扩展或直接集成 Adjust SDK。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/Adjust)
- [官方文档](https://docs.unrealengine.com/latest/INT/Gameplay/Analytics/index.html)