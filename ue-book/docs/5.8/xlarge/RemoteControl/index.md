# Remote Control API

> A suite of tools for controlling the Unreal Engine, both in Editor or at Runtime via a webserver. This allows users to control Unreal Engine remotely through HTTP or WebSockets requests. This functionality allows developers to control Unreal through 3rd party applications and web services.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制接口 |
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器工具、UI界面、示例资产） |
| 模块 | `RemoteControl` (Runtime), `RemoteControlCommon` (Runtime), `RemoteControlLogic` (Runtime), `RemoteControlMultiUser` (Runtime), `RemoteControlProtocol` (Runtime), `RemoteControlProtocolWidgets` (Runtime), `RemoteControlUI` (Runtime), `WebRemoteControl` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl) | |

## 用途

Remote Control 插件提供了一套标准化的远程控制接口。它解决了在虚拟制片、自动化测试或工具集成等场景下，**需要从外部（如网页、移动App、控制面板）实时、安全地读取或设置引擎内属性、调用函数**的核心问题。它通过内置的 Web 服务器，将 UE 的对象、属性、函数和事件暴露为可寻址的 HTTP API 和 WebSocket 通道，使外部应用无需直接链接引擎即可进行交互。

## 使用场景

- **虚拟制片控制**：在片场通过平板电脑或专用控制界面，远程调整灯光强度、摄像机参数、后期处理效果等。
- **自动化与测试**：编写外部脚本（如 Python）通过 HTTP 请求批量设置场景状态、运行测试用例、采集性能数据。
- **自定义监控面板**：创建自定义 Web 仪表盘，实时显示游戏内的关键数据（如玩家状态、性能指标）。
- **MIDI/OSC 控制器集成**：通过 WebSocket 接收来自硬件控制器（如 MIDI 调音台）的信号，用于控制颜色分级、镜头切换等。
- **Web 应用集成**：在浏览器中开发复杂的交互界面，用于原型设计或内容审核，直接与 UE 场景交互。

## 蓝图用法

Remote Control 的蓝图使用主要集中在编辑器中创建和配置“远程控制预设”。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Register Object` | 将一个 Actor 或 UObject 注册到远程控制预设中，使其属性和方法可通过 API 访问。 | `URCController` / 预设资产 |
| `Expose Property` | 明确暴露一个已注册对象的特定属性，并设置其访问权限和显示名。 | 预设资产 |
| `Expose Function` | 明确暴露一个已注册对象的可调用函数。 | 预设资产 |
| `Get Preset` | 在运行时获取指定的远程控制预设资产引用。 | `URCSubsystem` |
| `Get Exposed Actors` | 获取当前预设中所有已暴露的 Actor 列表。 | 预设资产 |
| `Get Actor Properties` | 获取指定 Actor 的所有已暴露属性及其当前值。 | 预设资产 |

### 使用示例（蓝图描述）

1.  在 Content Browser 中创建一个 `Remote Control Preset` 资产。
2.  打开该资产，在编辑器 UI 中，将场景中的 `Point Light` Actor 拖入“注册的对象”区域。
3.  在暴露的属性列表中，找到 `Intensity` 属性，勾选它以暴露。
4.  在运行时，通过以下 URL 可以获取或设置该灯光的强度：
    - GET: `/remote/presets/{PresetName}/objects/{ActorId}/properties/Intensity`
    - POST: `/remote/presets/{PresetName}/objects/{ActorId}/properties/Intensity` (请求体包含新值)

## C++ 用法

在 C++ 中，通常用于在服务端初始化子系统或创建自定义的远程控制逻辑。

### 头文件引入

```cpp
#include "IRemoteControlModule.h"
#include "RemoteControlPreset.h"
```

### 基本用法

获取远程控制子系统并操作预设。

```cpp
// 来源: RemoteControl 模块基础用法
#include "IRemoteControlModule.h"
#include "RemoteControlPreset.h"

void SetupRemoteControl()
{
    // 获取 Remote Control 模块实例
    IRemoteControlModule& RemoteControlModule = IRemoteControlModule::Get();
    
    // 加载或创建一个预设资产
    URemoteControlPreset* Preset = LoadObject<URemoteControlPreset>(nullptr, TEXT("/Game/MyRemotePreset"));
    
    if (Preset)
    {
        // 可以通过 C++ API 注册对象和暴露属性，但通常更推荐在编辑器UI中操作。
        // 这里演示获取已暴露的API信息。
        TArray<FRemoteControlObjectBinding> Bindings = Preset->GetBindings();
        for (const FRemoteControlObjectBinding& Binding : Bindings)
        {
            UE_LOG(LogTemp, Log, TEXT("Exposed Object: %s"), *Binding.Object->GetName());
        }
    }
}
```

### 进阶用法

监听远程控制事件。

```cpp
// 来源: RemoteControlLogic 模块事件处理
#include "RemoteControlPreset.h"

void BindRemoteControlEvents(URemoteControlPreset* Preset)
{
    if (!Preset) return;
    
    // 监听通过 API 修改属性值的事件
    Preset->OnEntityUpdated().AddLambda([](const FGuid& EntityId, const FName& PropertyName, const FRCObjectReference& ObjectRef)
    {
        UE_LOG(LogTemp, Warning, TEXT("Remote property update: Entity %s, Property: %s"), 
            *EntityId.ToString(), *PropertyName.ToString());
    });
    
    // 监听远程函数调用事件
    Preset->OnFunctionCalled().AddLambda([](const FGuid& EntityId, const UFunction* Function, const FRCObjectReference& ObjectRef)
    {
        UE_LOG(LogTemp, Warning, TEXT("Remote function call: Entity %s, Function: %s"), 
            *EntityId.ToString(), *Function->GetName());
    });
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何在自定义模块中创建一个基本的远程控制预设。

```cpp
// MyRemoteControlSetup.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyRemoteControlSetup.generated.h"

class URemoteControlPreset;

UCLASS()
class UMyRemoteControlSetupSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

private:
    UPROPERTY()
    TObjectPtr<URemoteControlPreset> RuntimePreset;
};
```

```cpp
// MyRemoteControlSetup.cpp
#include "MyRemoteControlSetup.h"
#include "IRemoteControlModule.h"
#include "RemoteControlPreset.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"

void UMyRemoteControlSetupSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    
    // 仅在编辑器或带服务器的游戏中启用
    if (IsRunningDedicatedServer() || GIsEditor)
    {
        IRemoteControlModule& RCModule = IRemoteControlModule::Get();
        
        // 在运行时动态创建一个预设（也可使用资产中预设）
        RuntimePreset = NewObject<URemoteControlPreset>();
        
        if (RuntimePreset)
        {
            // 将自身（GameInstance）注册为可远程访问的对象
            FRemoteControlObjectBinding Binding;
            Binding.Object = GetGameInstance();
            RuntimePreset->AddObjectBinding(Binding);
            
            // 暴露一个简单的自定义属性（假设 GameInstance 子类有此属性）
            FRemoteControlProperty Property;
            Property.DisplayName = TEXT("Game Status");
            Property.PropertyName = TEXT("CurrentStatus");
            RuntimePreset->AddExposedProperty(Property);
            
            UE_LOG(LogTemp, Log, TEXT("Remote Control runtime preset created."));
        }
    }
}

void UMyRemoteControlSetupSubsystem::Deinitialize()
{
    RuntimePreset = nullptr;
    Super::Deinitialize();
}
```

## 模块依赖

该插件是大型模块化架构，模块间依赖紧密。对于外部使用者而言，主要关注以下模块：

| 模块 | 用途 |
|---|---|
| `WebRemoteControl` | **核心模块**。提供 Web 服务器、HTTP 路由、WebSocket 管理以及 RESTful API 端点的实现。 |
| `RemoteControlUI` | 提供编辑器中的预设资产编辑器 UI 和相关编辑器工具。 |
| `RemoteControlProtocol` | 定义了协议的抽象层，支持扩展不同的通信协议（当前主要是 HTTP 和 WebSocket）。 |
| `RemoteControlCommon` | 包含所有模块共享的基础数据类型、接口和实用工具。 |
| `RemoteControlLogic` | 包含核心业务逻辑，如属性暴露规则、函数调用处理等。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `1716f2e0` | Remote Control: added missing ApplyColorWheelDelta and ApplyColorGradingWheelDelta to the built-in a | 为内置节点添加了缺失的颜色轮盘应用函数。 |
| 2026-05-20 | `d724bb52` | Remote Control: fixed  uninitialized ObjectClass in FRCRemoteFunctionCallParams, sometimes causing a | 修复了函数调用参数中对象类未初始化的 bug。 |
| 2026-05-20 | `12d5ae7f` | Remote Control: added allow list for remote function calls, and specifying built-in functions to all | 增加了远程函数调用的白名单安全机制。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下的编译器警告。 |

### 维护评价

Remote Control 插件自 2019 年随 Unreal Engine 4.23 发布以来，一直是 **活跃维护** 的核心模块，尤其是在虚拟制片领域。
- **近期更新频繁**：最近的提交（2026年5月）显示团队仍在积极添加新功能（如颜色轮盘支持）、修复 bug 和增强安全性（函数调用白名单）。
- **架构成熟稳定**：从 465 个源文件和清晰的模块划分可以看出，它已发展成一个复杂而稳定的企业级系统。
- **推荐使用**：对于任何需要引擎远程通信、自动化控制或构建自定义制片工具链的项目，**强烈推荐使用**。它是 Epic 虚拟制片工作流（如 nDisplay、Live Link）的重要基础设施。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/remote-control-api-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl/Tests)