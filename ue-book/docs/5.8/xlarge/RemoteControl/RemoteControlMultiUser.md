# Remote Control Multi-User

> 为 Remote Control 插件提供多用户协作支持的模块。

| 属性 | 值 |
|---|---|
| 中文名 | 多用户控制 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControlMultiUser` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl) | |

## 用途

本模块是 `RemoteControl` 插件的组成部分，其核心目的是为通过 WebAPI 进行远程控制时，支持多用户并发或协作场景。它解决的核心问题是：当多个客户端（例如不同部门的控制面板或不同操作者）通过 `WebRemoteControl` 同时对同一个 UE5 实例进行控制时，如何确保操作的一致性、同步性并管理冲突。该模块可能为远程属性修改、函数调用等操作提供了一个在多人会话环境下的代理或同步层。

## 使用场景

- **虚拟制片团队协作**：多个控制台（灯光、渲染、虚拟相机）通过各自的 Web 界面实时调整同一虚拟场景的资产属性。
- **远程监控与控制面板**：多个独立的控制面板（如 iPad 应用）需要同时查看并修改同一引擎实例的参数。
- **跨部门预览与反馈**：艺术、灯光、动画部门通过浏览器同时预览并提交对当前镜头资产的微调。

## 蓝图用法

*注意：由于提供的模块头文件仅包含模块接口，且公开的蓝图可调用函数（`UFUNCTION`）通常定义在其它核心模块（如 `RemoteControlLogic`）中，此处基于典型 Remote Control 用法进行推断。*

### 核心节点

在多用户场景下，蓝图中使用 Remote Control 的核心节点通常保持不变，但其背后的行为会受到 `RemoteControlMultiUser` 模块的协调：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Remote Control API` | 获取 Remote Control 系统的核心单例。 | `URemoteControlModule` |
| `Get Exposed Property` | 通过名称获取一个被暴露的远程控制属性句柄。 | `URemoteControlModule` |
| `Set Property Value (Generic)` | 设置远程控制属性的值（通过句柄）。 | `URCController` |
| `Call Remote Function` | 通过远程控制接口调用一个函数。 | `URCController` |

### 使用示例（蓝图描述）

假设你有一个暴露的 `Point Light` 的 `Intensity` 属性。

1.  使用 `Get Remote Control API` 节点获取 `URemoteControlModule` 的引用。
2.  通过该引用调用 `Get Exposed Property`，传入属性的暴露名称（如 `PointLight_Intensity`），获得一个 `FRCObjectReference`。
3.  使用 `Set Property Value (Generic)` 节点，传入上一步获得的引用和新的浮点值。
在 `RemoteControlMultiUser` 模块激活的环境下，所有客户端对这个属性的修改都会被同步并应用到主引擎实例，具体的冲突解决策略由该模块内部处理。

## C++ 用法

### 头文件引入

```cpp
#include "RemoteControlMultiUserModule.h"
```

### 基本用法

获取并引用模块。该模块主要用于内部注册代理，直接的用户代码交互较少，但可检查其是否加载。

```cpp
// 来自一般模块使用模式
#include "Modules/ModuleManager.h"

// 检查 RemoteControlMultiUser 模块是否已加载
if (FModuleManager::Get().IsModuleLoaded(“RemoteControlMultiUser”))
{
    UE_LOG(LogTemp, Log, TEXT(“Remote Control Multi-User support is active.”));
}
```

### 进阶用法

在需要编写与 Remote Control 深度集成的自定义模块时，可能需要处理多用户同步的事件。`RemoteControlMultiUser` 模块可能会通过代理（Delegate）广播其状态。

```cpp
// 假设场景：一个自定义的同步管理器监听远程控制操作
// 注意：以下API为基于上下文推断的示例，具体接口请参考实际Public头文件

// 1. 绑定到一个远程属性的多用户变更事件（示例接口）
// FRCObjectReference PropertyRef = ...; // 通过 URemoteControlModule 获取
// if (PropertyRef.IsValid())
// {
//     PropertyRef.OnMultiUserPropertyChanged.AddLambda(
//         [](const FRCObjectReference& Ref, const FProperty* Prop, const void* NewValue, uint32 UserId)
//         {
//             UE_LOG(LogTemp, Warning, TEXT(“Property changed by user %u via multi-user session.”), UserId);
//         });
// }

// 2. 在发送远程函数调用时，指定或忽略多用户上下文（示例接口）
// FRemoteControlFunctionCallParams Params;
// Params.Function = MyFunction;
// Params.Arguments = ...;
// Params.bOverrideMultiUserSync = true; // 由 RemoteControlMultiUser 模块解释此标志
// URemoteControlModule::Get().CallRemoteFunction(Params);
```

## Demo 示例

一个最小化的 C++ 示例，展示如何创建一个依赖于 `RemoteControlMultiUser` 模块的自定义模块，并在模块启动时检测其存在。

```cpp
// MyMultiUserAwareModule.h
#pragma once

#include "Modules/ModuleInterface.h"

class FMyMultiUserAwareModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyMultiUserAwareModule.cpp
#include "MyMultiUserAwareModule.h"
#include "Modules/ModuleManager.h"

#define LOCTEXT_NAMESPACE “FMyMultiUserAwareModule”

void FMyMultiUserAwareModule::StartupModule()
{
    // 检查并记录 Remote Control Multi-User 模块的状态
    if (FModuleManager::Get().IsModuleLoaded(“RemoteControlMultiUser”))
    {
        UE_LOG(LogTemp, Display, TEXT(“Module started with Remote Control Multi-User support enabled.”));
        // 此处可以初始化依赖多用户同步的自定义功能
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT(“Module started WITHOUT Remote Control Multi-User support.”));
    }
}

void FMyMultiUserAwareModule::ShutdownModule()
{
    // 清理工作
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyMultiUserAwareModule, MyMultiUserAwareModule)
```

## 模块依赖

根据其在 `RemoteControl` 插件中的角色，`RemoteControlMultiUser` 模块依赖于其他核心 Remote Control 模块。从常见的依赖模式推断：

| 模块 | 用途 |
|---|---|
| `RemoteControlCommon` | 提供远程控制的基础数据类型和通信协议。 |
| `CoreUObject` | 反射系统，用于属性/函数发现和调用。 |
*实际依赖项请以其 `Build.cs` 文件中的 `PublicDependencyModuleNames` 为准。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `1716f2e0` | Remote Control: added missing ApplyColorWheelDelta and ApplyColorGradingWheelDelta to the built-in a | 为内置代理（Proxy）补充了颜色轮盘相关的函数，增强颜色校准的远程控制能力。 |
| 2026-05-20 | `d724bb52` | Remote Control: fixed uninitialized ObjectClass in FRCRemoteFunctionCallParams, sometimes causing a | 修复了远程函数调用参数中 ObjectClass 未初始化的偶发崩溃问题。 |
| 2026-05-20 | `12d5ae7f` | Remote Control: added allow list for remote function calls, and specifying built-in functions to all | 增加了远程函数调用的允许列表机制，并配置了内置允许函数，提升安全性。 |
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 调整了编辑器 UI 布局，将 Motion Design 相关选项卡移至独立分组（此改动可能间接影响 Remote Control UI 的加载）。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下 double 转 float 的编译器警告，属于代码质量维护。 |

### 维护评价

- **活跃维护**：`RemoteControl` 插件整体处于 **活跃维护** 状态。从提交记录看，2026年5月有多次针对功能增强、Bug修复和安全性改进的提交。
- **关键价值**：该插件是虚拟制片（Virtual Production）工作流中的关键远程控制工具，对于需要通过自定义Web界面、移动设备或其他第三方应用控制UE5引擎的项目至关重要。
- **推荐使用**：对于需要上述远程控制能力的项目，尤其是涉及多用户协作场景的，**强烈推荐**启用此插件。`RemoteControlMultiUser` 作为其核心模块之一，虽然用户直接编码不多，但确保了多客户端环境下的稳定运行。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl)