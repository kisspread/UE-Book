# MSGaming Support

> Microsoft Gaming Runtime and Microsoft Game Store plugins.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 微软游戏支持 |
| 分类 | Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MSGamingSupportEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-16 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Windows/MSGamingSupport) | |

## 用途

该插件是专门为使用 Microsoft Game Development Kit (GDK) 进行游戏开发（如目标平台为 Xbox 和 Windows 商店）的团队提供的**配置中心**。它不包含可玩的游戏功能，而是作为 GDK 插件套件的统一设置入口。其核心作用是将 `UGDKTargetSettings` 基类中的通用 GDK 配置选项，针对微软游戏商店和运行时环境进行具体化和扩展，让开发者可以在项目设置中集中管理打包、运行时初始化等关键行为。

## 使用场景

- 你正在使用 Microsoft GDK 开发一款面向 Xbox 或 Windows 商店的游戏。
- 你需要配置游戏在打包时是否自动生成 MSIXVC 包，或者是否强制包含 DX11 / GameInput 运行时。
- 你希望控制 GDK 运行时在编辑器中测试时的行为，例如是否在每次 PIE 时重启，或是否采用延迟初始化以提升启动速度。
- 你需要为游戏设置特定的 Windows 版本最低要求，并在商店页面中展示。

## 蓝图用法

此插件主要提供项目设置（Project Settings）中的配置界面，不包含可在蓝图图表中直接调用的函数。所有配置项均为编辑器属性（`UPROPERTY`），通过插件设置面板进行修改。

### 核心节点

无（本插件不提供蓝图可调用函数）

## C++ 用法

主要通过 C++ 代码访问和读取插件提供的配置项，用于打包流程或运行时逻辑判断。

### 头文件引入

```cpp
#include "MSGamingSettings.h"
```

### 基本用法

从项目设置中获取并读取 `UMSGamingSettings` 的配置值。

```cpp
// 来源: 通用用法，基于 MSGamingSettings.h 中的 UPROPERTY 推断
#include "MSGamingSettings.h"
#include "Engine/World.h"

void ReadMSGamingConfig()
{
    // 获取默认配置对象
    const UMSGamingSettings* Settings = GetDefault<UMSGamingSettings>();
    if (Settings)
    {
        UE_LOG(LogTemp, Log, TEXT("Auto Generate Package: %s"), Settings->bAutoGeneratePackage ? TEXT("True") : TEXT("False"));
        UE_LOG(LogTemp, Log, TEXT("Lazy Initialize GDK Runtime: %s"), Settings->bLazyInitialize ? TEXT("True") : TEXT("False"));
        
        // 检查是否需要在 PIE 时重启运行时
        if (Settings->bRestartRuntimeForPIE)
        {
            // 可能需要执行重启 GDK 运行时的相关逻辑
        }
    }
}
```

## Demo 示例

以下示例展示了如何在游戏模块中访问 MSGaming 配置，并根据配置执行一项简单的运行时检查。

**MyGameModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void CheckMSGamingSettings();
};
```

**MyGameModule.cpp**
```cpp
#include "MyGameModule.h"
#include "MSGamingSettings.h"
#include "Misc/MessageDialog.h"

void FMyGameModule::StartupModule()
{
    CheckMSGamingSettings();
}

void FMyGameModule::ShutdownModule()
{
}

void FMyGameModule::CheckMSGamingSettings()
{
    const UMSGamingSettings* Settings = GetDefault<UMSGamingSettings>();
    if (Settings && Settings->bLazyInitialize)
    {
        UE_LOG(LogTemp, Warning, TEXT("MSGaming Runtime is configured for lazy initialization. Ensure this is compatible with your online services."));
        // 可以在这里添加针对延迟初始化模式的额外初始化逻辑
    }
}
```

## 模块依赖

从 `MSGamingSupportEditor.Build.cs` 分析，使用者需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `GDK` | 基础 GDK 模块，提供 `UGDKTargetSettings` 基类 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `4237a656` | Show the MSGamingSupport plugin in the browser | 让插件在插件浏览器中可见。 |
| 2026-04-17 | `5f051051` | fixes for MSGamingRuntime's bLazyInitialize: | 修复了与 GDK 运行时延迟初始化功能相关的问题。 |
| 2026-02-16 | `ecdeac29` | Move MSGaming plugins to the public engine | 将 MSGaming 插件集从内部或实验分支迁移至公共引擎。 |

### 维护评价

该插件**创建时间非常新**（2026年2月），且处于**实验性（Beta）** 状态。从提交历史看，在创建后的两个月内仍有功能修复（`bLazyInitialize`）和可用性改进（使其在插件浏览器可见），表明**处于活跃开发初期**。由于是实验性插件，其API和功能未来可能发生变化。目前推荐用于评估和测试 Microsoft GDK 工作流，但在正式生产项目中使用时需注意其稳定性风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Windows/MSGamingSupport)
- 官方文档：无
- 测试用例：未在当前目录发现测试文件。