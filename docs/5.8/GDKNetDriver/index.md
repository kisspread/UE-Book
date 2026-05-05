# GDK Net Driver

> Net driver for GDK platforms（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GDKNetDriver` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2026-02-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/Microsoft/GDKNetDriver) | |

## 用途

该插件为基于微软 GDK（Game Development Kit）的平台（主要是 Win64）提供了一个专门的网络驱动实现。它继承自标准的 `UIpNetDriver`，并重写了 `GetClientPort` 方法，旨在为使用 GDK 工具链和在线服务的游戏提供更适配或优化的底层网络通信支持。其存在是为了确保在 GDK 平台上运行的游戏能够正确、高效地进行网络数据传输。

## 使用场景

- 你正在使用微软 GDK 工具链为 Xbox 或 Windows 平台开发游戏，并且需要自定义或优化网络驱动。
- 你的项目启用了 `OnlineSubsystemUtils` 插件，并且需要在 GDK 环境下处理网络连接。

## 蓝图用法

该插件没有暴露任何蓝图可调用的函数或属性。其功能主要通过 C++ 继承和配置来使用。

### 核心节点

无直接蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "GDKNetDriver.h"
```

### 基本用法

该插件的核心是 `UGDKNetDriver` 类。通常，你不需要直接实例化它，而是在项目的网络配置中指定使用它。如果需要自定义行为，可以继承它。

```cpp
// MyGDKNetDriver.h
#pragma once
#include "GDKNetDriver.h"
#include "MyGDKNetDriver.generated.h"

UCLASS()
class UMyGDKNetDriver : public UGDKNetDriver
{
    GENERATED_BODY()
public:
    // 可以在此重写其他虚函数进行自定义
    // virtual bool InitBase(bool bInitAsClient, ...) override;
};
```

### 进阶用法

在项目的 `DefaultEngine.ini` 配置文件中，可以将此驱动指定为默认的网络驱动：

```ini
[URL]
Port=7777

[/Script/OnlineSubsystemUtils.IpNetDriver]
NetDriverClassName=/Script/GDKNetDriver.GDKNetDriver
```

## Demo 示例

以下是一个自定义 GDK 网络驱动的最小示例。

**MyGDKNetDriver.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once
#include "GDKNetDriver.h"
#include "MyGDKNetDriver.generated.h"

UCLASS()
class UMyGDKNetDriver : public UGDKNetDriver
{
    GENERATED_BODY()
public:
    UMyGDKNetDriver(const FObjectInitializer& ObjectInitializer);
    // 可以添加自定义成员变量或函数
};
```

**MyGDKNetDriver.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#include "MyGDKNetDriver.h"

UMyGDKNetDriver::UMyGDKNetDriver(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    // 自定义初始化逻辑
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemUtils` | 提供在线子系统工具类，是此插件运行的基础依赖 |

## 维护状态

### 近期更新

- 2026-04-24 101f2bf3 Enable GDK ARM64 support in plugins (requires April 2026 GDK & modern folder layout)
- 2026-03-09 5eb8fada [Backout] - CL51493025
- 2026-03-06 21bccda6 Enable arm64 support in plugins
- 2026-02-17 2fde7fed Move GDK online plugins to the public engine

### 维护评价

该插件创建于 2026 年 2 月，是一个非常新的插件。从近期提交记录看，它在创建后的一个月内经历了多次更新，主要集中在添加 ARM64 架构支持和代码调整上，表明其处于**活跃维护**状态。作为 GDK 平台专用的网络驱动，它对于使用该工具链的项目是必要的。由于其功能相对专一且代码量小，目前没有已知的重大问题。**推荐**在 GDK 平台项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/Microsoft/GDKNetDriver)