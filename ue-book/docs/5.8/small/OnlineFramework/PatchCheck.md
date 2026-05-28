# Online Framework Plugin

> Shared code for interacting with online gameplay services.

| 属性 | 值 |
|---|---|
| 中文名 | 在线框架插件 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Hotfix` (Runtime), `Lobby` (Runtime), `LoginFlow` (Runtime), `Party` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Qos` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework) | |

## 用途

`OnlineFramework` 插件提供了一组核心模块，用于与在线游戏服务进行交互的基础框架。它并非一个独立的功能，而是一个提供通用功能（如大厅、派对、补丁检查等）的“工具箱”，旨在供各个 `OnlineSubsystem` 平台插件复用和扩展。其主要解决的问题是：将平台无关的在线服务逻辑（如创建派对、检查游戏版本）从特定的平台实现（如 Steam、PlayStation Network）中解耦出来，构建一个可共享的底层框架。

**本文档聚焦于 `PatchCheck` 子模块**，该模块负责在游戏启动或进入多人游戏前，执行一系列补丁和版本检查，以确保客户端符合服务器或平台的要求。

## 使用场景

- 你的游戏需要确保玩家在进入在线模式前已安装了必要的更新（热修复、DLC）。
- 你需要在游戏启动时检查平台商店（如 Epic Games Store、PlayStation Store）是否有强制性的版本更新。
- 你需要一个统一的流程来检测游戏环境、平台补丁和在线服务补丁，并根据结果执行不同操作（如显示更新提示、阻止游戏进行）。

## 蓝图用法

`PatchCheck` 模块主要通过 C++ 接口 `FPatchCheck` 使用，未发现其暴露 `BlueprintCallable` 函数。所有操作均在 C++ 层完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无） | 无蓝图公开函数 | N/A |

### 使用示例（蓝图描述）

不适用。

## C++ 用法

### 头文件引入

```cpp
#include "PatchCheckModule.h"
```

### 基本用法

获取 `PatchCheck` 单例并启动检查流程，同时监听结果。
(来源: `Public/PatchCheck.h`)

```cpp
// 获取 PatchCheck 实例（通常在游戏启动时）
FPatchCheck& PatchCheck = FPatchCheck::Get();

// 绑定补丁检查完成的委托
PatchCheck.GetOnComplete().AddLambda([](EPatchCheckResult Result) {
    switch (Result)
    {
    case EPatchCheckResult::NoPatchRequired:
        UE_LOG(LogTemp, Log, TEXT("版本检查通过，无需补丁。"));
        // 继续游戏启动或进入大厅
        break;
    case EPatchCheckResult::PatchRequired:
        UE_LOG(LogTemp, Warning, TEXT("需要更新，将跳转至商店。"));
        // 显示更新提示或关闭游戏
        break;
    case EPatchCheckResult::NoLoggedInUser:
    case EPatchCheckResult::PatchCheckFailure:
        UE_LOG(LogTemp, Error, TEXT("补丁检查失败或无用户。"));
        // 处理错误
        break;
    }
});

// 启动补丁检查
PatchCheck.StartPatchCheck();
```

### 进阶用法

通过继承 `TPatchCheckModule` 创建自己的补丁检查模块，并实现自定义的统计收集器。
(来源: `Public/PatchCheckModule.h`, `Public/PatchCheck.h`)

```cpp
// MyGame_PatchCheckModule.h
#include "PatchCheckModule.h"

class FMyGamePatchCheck : public FPatchCheck
{
    // 可以重写 EnvironmentWantsPatchCheck() 等虚函数来自定义逻辑
protected:
    virtual bool EnvironmentWantsPatchCheck() const override
    {
        // 例如：仅在 Shipping 配置下进行检查
        return !UE_BUILD_SHIPPING;
    }
};

// MyGame_PatchCheckModule.cpp
#include "MyGame_PatchCheckModule.h"
#include "Modules/ModuleManager.h"

// 1. 定义模块类
class FMyGamePatchCheckModule : public TPatchCheckModule<FMyGamePatchCheck>
{
};

// 2. 注册模块
IMPLEMENT_MODULE(FMyGamePatchCheckModule, MyGamePatchCheck);

// 3. 在项目的 .uproject 或 .Target.cs 中启用插件，并在配置中指定使用此模块
// Engine/Config/DefaultEngine.ini:
// [PatchCheck]
// ModuleName=MyGamePatchCheck
```

## Demo 示例

一个最小化的自定义补丁检查模块实现。

**MyGamePatchCheck.h**
```cpp
#pragma once
#include "PatchCheck.h"

// 派生自 FPatchCheck，可以添加自定义数据或重写方法
class FMyGamePatchCheck : public FPatchCheck
{
public:
    // 重写此函数以自定义“是否需要检查补丁”的判断逻辑
    virtual bool EnvironmentWantsPatchCheck() const override
    {
        // 示例：始终返回 true，或根据项目设置判断
        return true;
    }
};
```

**MyGamePatchCheckModule.h**
```cpp
#pragma once
#include "PatchCheckModule.h"

// 定义模块入口点，使用我们的自定义 PatchCheck 类
class FMyGamePatchCheckModule : public TPatchCheckModule<FMyGamePatchCheck>
{
public:
    // 模块启动时由引擎调用，基类 IPatchCheckModule 已处理好实例化逻辑
};
```

**MyGamePatchCheckModule.cpp**
```cpp
#include "MyGamePatchCheckModule.h"
#include "Modules/ModuleManager.h"

// 实现并注册模块
IMPLEMENT_MODULE(FMyGamePatchCheckModule, MyGamePatchCheck);
```

## 模块依赖

从 `PatchCheck.Build.cs` 分析：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 进行平台级别的在线服务补丁检查（例如检查平台商店更新） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `09a2dfc6` | [Hotfix on Load] Fix issue where certain baked hotfixes will not apply when no backend hotfixes exis | 修复了在无后端热修复时，某些内置热修复不应用的问题 |
| 2026-05-12 | `0b9170a8` | Guard Invite and RTJ social party calls when epic parties mirroring is enabled. | 在启用 Epic 派对镜像时，保护邀请和加入派对的社交调用 |
| 2026-04-30 | `fe1eaff2` | Add a hook for PartyPlatformSessionMonitor to allow the game party to add a special key to the platf | 为派对平台会话监视器添加钩子，允许游戏派对向平台添加特殊键 |
| 2026-04-29 | `0badc43f` | Restore LogHotfixManager summary logs for hotfix on load | 恢复了“加载时热修复”的日志管理器摘要日志 |
| 2026-04-28 | `85cae1c6` | Broadcast party initialization after we've processed our first update | 在处理完第一次更新后广播派对初始化事件 |

### 维护评价

- **创建时间**：2016年，已近10年。
- **最近更新频率**：2026年4-5月有多次提交，非常活跃。
- **维护状态**：**活跃维护**。该插件作为核心在线框架，持续有功能修复和特性添加。
- **已知问题/限制**：`EnabledByDefault=false`，使用时需手动在项目配置中启用。
- **推荐使用**：如果你的项目需要深度集成在线服务（大厅、派对、版本管理），且不满足于单一平台子系统，这个框架是必不可少的。但对于简单的单平台集成，可能直接使用对应的 `OnlineSubsystem` 插件即可。

**注意**：该插件包含多个独立模块（Hotfix, Lobby, Party等），本文档仅详细介绍了 `PatchCheck` 子模块。其他模块的功能和用法需要参考其各自的源码。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework/Tests)