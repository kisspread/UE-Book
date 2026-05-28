# File Logging Analytics Provider

> Writes analytic API calls to local disk for debugging or local use

| 属性 | 值 |
|---|---|
| 中文名 | 文件日志分析 |
| 分类 | Analytics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FileLogging` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-09-12 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/FileLogging) | |

## 用途

FileLogging 是一个 `IAnalyticsProvider` 的本地文件实现。它不连接任何远程分析服务，而是将所有分析 API 调用写入本地磁盘文件。

**解决的问题**：在开发调试阶段，你可能还没有配置真实的 Analytics 后端（如 Firebase、GameAnalytics 等），但又需要验证分析事件是否正确触发。FileLogging 提供了一个"假的"分析服务，将所有事件序列化写入本地文件，方便离线审查和调试。

**为什么存在**：UE 的分析系统（`IAnalyticsProviderModule`）需要一个默认的、零配置的调试实现，FileLogging 就是这个最小化实现。它记录会话开始/结束、用户属性、货币交易、物品购买、进度和错误事件，格式为可读的文本/JSON。

## 使用场景

- 你在开发阶段需要验证分析事件是否正确上报 → 用 FileLogging 本地记录
- 你还没有配置正式的分析后端，但需要一个占位 provider 让代码跑通 → 用 FileLogging
- 你需要离线分析玩家行为数据，不需要联网 → 用 FileLogging 写本地文件
- 你在做自动化测试，需要验证分析事件内容 → 用 FileLogging 写文件后断言内容

## 蓝图用法

此插件主要通过配置使用，不直接暴露蓝图节点。分析事件的触发通过 `IAnalyticsProvider` 接口完成，通常由上层系统（如 `FAnalytics`）管理。

### 核心节点

本插件不提供额外的蓝图节点。分析事件通过 C++ 的 `IAnalyticsProvider` 接口记录，或通过引擎内置的分析蓝图系统间接使用。

### 使用示例（配置启用）

此插件默认禁用（`EnabledByDefault: false`），需要手动启用：

1. 打开 **Edit → Plugins**，搜索 "File Logging"，启用插件并重启
2. 在 `DefaultEngine.ini` 中配置分析系统使用此 Provider：

```ini
[Analytics]
ProviderModuleName=FileLogging
```

启动游戏后，分析事件将自动写入本地文件。

## C++ 用法

### 头文件引入

```cpp
#include "FileLogging.h"
```

### 基本用法

获取模块实例并创建分析 Provider：

```cpp
// 获取 FileLogging 模块单例
FAnalyticsFileLogging& FileLoggingModule = FAnalyticsFileLogging::Get();

// 通过配置委托创建 Provider
FAnalyticsProviderConfigurationDelegate ConfigDelegate;
ConfigDelegate.BindLambda([](const FString& Key) -> FString
{
    // 可在此处返回配置值，例如文件路径
    return FString();
});

TSharedPtr<IAnalyticsProvider> Provider = FileLoggingModule.CreateAnalyticsProvider(ConfigDelegate);
```

### 进阶用法

创建 Provider 后，记录完整的分析事件流：

```cpp
// 启动会话
TArray<FAnalyticsEventAttribute> SessionAttrs;
SessionAttrs.Add(FAnalyticsEventAttribute(TEXT("MapName"), TEXT("MainMenu")));
Provider->StartSession(SessionAttrs);

// 设置用户信息
Provider->SetUserID(TEXT("Player_001"));

// 记录自定义事件
TArray<FAnalyticsEventAttribute> EventAttrs;
EventAttrs.Add(FAnalyticsEventAttribute(TEXT("Weapon"), TEXT("Rifle")));
EventAttrs.Add(FAnalyticsEventAttribute(TEXT("Damage"), FString::FromInt(150)));
Provider->RecordEvent(TEXT("EnemyKilled"), EventAttrs);

// 记录物品购买
Provider->RecordItemPurchase(TEXT("Sword_001"), TEXT("Gold"), 500, 1);

// 记录货币购买
Provider->RecordCurrencyPurchase(TEXT("Gems"), 100, TEXT("USD"), 4.99f, TEXT("Steam"));

// 记录进度
TArray<FAnalyticsEventAttribute> ProgressAttrs;
ProgressAttrs.Add(FAnalyticsEventAttribute(TEXT("Level"), TEXT("Forest")));
Provider->RecordProgress(TEXT("LevelComplete"), TEXT("Chapter1/Forest"), ProgressAttrs);

// 记录错误
TArray<FAnalyticsEventAttribute> ErrorAttrs;
Provider->RecordError(TEXT("ConnectionTimeout"), ErrorAttrs);

// 设置默认事件属性（所有后续事件自动附带）
TArray<FAnalyticsEventAttribute> DefaultAttrs;
DefaultAttrs.Add(FAnalyticsEventAttribute(TEXT("BuildVersion"), TEXT("1.2.3")));
Provider->SetDefaultEventAttributes(MoveTemp(DefaultAttrs));

// 刷新并结束会话
Provider->FlushEvents();
Provider->EndSession();
```

## Demo 示例

一个完整的最小示例，在游戏启动时记录几条分析事件到本地文件：

```cpp
// FileLoggingDemo.h
#pragma once

#include "CoreMinimal.h"

class FFileLoggingDemo
{
public:
    static void RunDemo();
};
```

```cpp
// FileLoggingDemo.cpp
#include "FileLoggingDemo.h"
#include "FileLogging.h"
#include "AnalyticsEventAttribute.h"

void FFileLoggingDemo::RunDemo()
{
    // 加载模块
    FAnalyticsFileLogging& Module = FAnalyticsFileLogging::Get();

    // 创建 Provider（无需特殊配置）
    TSharedPtr<IAnalyticsProvider> Provider = Module.CreateAnalyticsProvider(
        FAnalyticsProviderConfigurationDelegate());
    
    if (!Provider.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create FileLogging analytics provider"));
        return;
    }

    // 启动会话并记录事件
    Provider->StartSession({});
    Provider->SetUserID(TEXT("TestPlayer"));

    TArray<FAnalyticsEventAttribute> Attrs;
    Attrs.Add(FAnalyticsEventAttribute(TEXT("Action"), TEXT("Jump")));
    Attrs.Add(FAnalyticsEventAttribute(TEXT("Count"), TEXT("42")));
    Provider->RecordEvent(TEXT("PlayerAction"), Attrs);

    Provider->RecordItemPurchase(TEXT("Shield"), TEXT("Gold"), 300, 2);

    // 结束会话（自动刷新到文件）
    Provider->EndSession();
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

此插件仅依赖 UE 核心分析接口模块，无需额外引入特殊模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到新的 UE_LOGF 宏 |
| 2024-02-06 | `c02789b4` | [Backout] - CL31042395 | 回退之前的某次变更 |
| 2024-01-31 | `6bfbcbac` | Move the initial declaration of ::BlockUntilFlushed from IAnalyticsProviderET to it's parent class I | 将 BlockUntilFlushed 声明从 ET 子类移到父接口 IAnalyticsProvider |
| 2023-12-08 | `ae0e1db1` | Pushed Set/GetDefaultAttributes into IAnalyticsProvider | 将默认属性的 Get/Set 方法提升到基类 IAnalyticsProvider 接口 |
| 2023-04-11 | `e109a24a` | GitHub #9388 : FileLogging analytic nested json support | 为分析事件添加嵌套 JSON 支持 |

### 维护评价

- **创建于 2014 年**，是 UE4 早期就存在的基础插件
- 代码规模极小（3 个源文件），结构简单稳定
- 更新频率较低，多为跟随引擎接口变更的适配性更新（如接口方法迁移、日志宏替换）
- **功能稳定，无需频繁改动**——作为一个简单的本地文件写入实现，逻辑几乎不会变
- 最近的更新均为被动适配（接口重构、宏迁移），无功能性增强
- **推荐使用**：作为调试和开发阶段的分析 Provider，简单可靠，零依赖
- ⚠️ 注意：此插件默认禁用，需要手动启用；不适合作为生产环境的分析方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Analytics/FileLogging)