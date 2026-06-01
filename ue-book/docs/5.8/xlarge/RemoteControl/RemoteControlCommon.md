# Remote Control API

> A suite of tools for controlling the Unreal Engine, both in Editor or at Runtime via a webserver. This allows users to control Unreal Engine remotely through HTTP or WebSockets requests. This functionality allows developers to control Unreal through 3rd party applications and web services.

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制 API |
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（运行时蓝图资产、配置资产、协议资产） |
| 模块 | `RemoteControl` (Runtime), `RemoteControlCommon` (Runtime), `RemoteControlLogic` (Runtime), `RemoteControlMultiUser` (Runtime), `RemoteControlProtocol` (Runtime), `RemoteControlProtocolWidgets` (Runtime), `RemoteControlUI` (Runtime), `WebRemoteControl` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-07 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl) | |

## 用途

Remote Control API 是一个完整的远程控制框架，它通过内置的 HTTP 和 WebSocket 服务器，允许开发者在引擎运行时或编辑器中，通过外部的第三方应用程序、Web 服务或简单的网页界面来监控和修改 Unreal Engine 内部的对象属性和调用函数。该插件的核心是 `RemoteControlCommon` 模块，它提供了底层的类型特征系统、属性工具函数、网络地址管理和全局配置，为上层模块（如协议绑定、Web 服务器、UI）奠定基础。

## 使用场景

- **现场灯光与参数调整**：在大型虚拟制片或演播室环境中，灯光师可以通过平板电脑或自定义控制界面，实时调整场景中灯光组件的强度、颜色和位置，而无需坐在主控台前。
- **自动化测试与集成**：在 CI/CD 流水线中，可以通过脚本（如 Python）向运行中的游戏实例发送 HTTP 请求，修改游戏状态或读取特定属性值，实现自动化验证。
- **多机位协作**：在多人编辑会话（Multi-User Editing）中，不同机器上的用户可以通过 Remote Control 同步调整共享对象的属性。
- **安全远程管理**：对于服务器或无需图形界面的“无头”（Headless）应用，可以通过 WebSocket 连接进行运行时监控和管理。

## 蓝图用法

`RemoteControlCommon` 模块主要提供底层数据结构和设置，其配置项可以通过 `URemoteControlSettings` 在蓝图或项目设置中访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Remote Control Settings` | 获取全局远程控制设置单例对象 | `URemoteControlSettings` |
| `Remote Control HTTP Server Port` (属性) | 获取或设置 HTTP 服务器端口 | `URemoteControlSettings` |
| `Remote Control WebSocket Server Port` (属性) | 获取或设置 WebSocket 服务器端口 | `URemoteControlSettings` |
| `Auto Start Web Server` (属性) | 控制 Web 服务器是否自动启动 | `URemoteControlSettings` |
| `Allowlisted Clients` (属性) | 允许访问的客户端 IP 地址范围集合 | `URemoteControlSettings` |
| `Passphrases` (属性) | 用于远程客户端认证的密码短语列表 | `URemoteControlSettings` |

### 使用示例（蓝图描述）

在蓝图中，首先使用 `Get Remote Control Settings` 节点获取 `URemoteControlSettings` 对象。然后，可以读取或设置其属性，例如 `Remote Control HTTP Server Port` 来更改 HTTP 服务器监听的端口，或者修改 `Allowlisted Clients` 来动态调整允许连接的 IP 范围。

## C++ 用法

### 头文件引入

```cpp
#include "RemoteControlSettings.h"
#include "RCTypeUtilities.h"
#include "RCTypeTraits.h"
```

### 基本用法

**1. 检查属性是否支持远程控制映射**

```cpp
// 来源: Public/RCTypeUtilities.h
FProperty* SomeProperty = ...; // 获取一个UObject的属性
if (RemoteControlTypeUtilities::IsSupportedMappingType(SomeProperty))
{
    // 该属性可以作为远程控制的输出（映射）目标
}
```

**2. 获取属性的默认值范围**

```cpp
// 来源: Public/RCTypeUtilities.h
FProperty* FloatProperty = ...; // 一个float属性
float MinValue = RemoteControlTypeUtilities::GetDefaultRangeValueMin<float>(FloatProperty);
float MaxValue = RemoteControlTypeUtilities::GetDefaultRangeValueMax<float>(FloatProperty);
// MinValue 和 MaxValue 会考虑属性元数据（如ClampMin, ClampMax）
```

### 进阶用法

**使用类型特征系统处理多种属性类型**

```cpp
// 来源: Public/RCTypeUtilities.h
void ProcessProperty(FProperty* Property, const void* Data)
{
    // 使用宏遍历并转换属性类型
    FOREACH_CAST_PROPERTY(Property,
    {
        // 此时 CastProperty 是转换后的具体类型指针 (如 FIntProperty*)
        // CastPropertyType 是对应的类型 (如 FIntProperty)
        if constexpr (TRemoteControlPropertyTypeTraits<CastPropertyType>::IsSupportedRangeType())
        {
            // 处理支持范围输入的属性类型
            // 可以获取默认范围值
            auto Min = RemoteControlTypeUtilities::GetDefaultRangeValueMin<typename CastPropertyType::TCppType>(Property);
            auto Max = RemoteControlTypeUtilities::GetDefaultRangeValueMax<typename CastPropertyType::TCppType>(Property);
            // ... 执行业务逻辑
        }
    });
}
```

**配置和访问远程控制设置**

```cpp
// 来源: Public/RemoteControlSettings.h
void ConfigureRemoteControl()
{
    URemoteControlSettings* Settings = GetMutableDefault<URemoteControlSettings>();
    if (Settings)
    {
        // 设置HTTP服务器端口
        Settings->RemoteControlHttpServerPort = 30015;
        // 启用自动启动Web服务器
        Settings->bAutoStartWebServer = true;
        // 添加一个允许的客户端IP
        FRCNetworkAddress NewAddress(192, 168, 1, 100);
        FRCNetworkAddressRange NewRange(NewAddress, NewAddress);
        Settings->AllowlistedClients.Add(NewRange);
        // 保存设置
        Settings->SaveConfig();
    }
}
```

## Demo 示例

以下示例演示了如何在 C++ 模块中检查属性类型支持情况并读取带元数据的默认范围值。

**MyRemoteControlHelper.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "RCTypeUtilities.h"
#include "UObject/UnrealType.h"

class FMyRemoteControlHelper
{
public:
    static void AnalyzePropertyForRemoteControl(UObject* TargetObject, FName PropertyName);
};
```

**MyRemoteControlHelper.cpp**
```cpp
#include "MyRemoteControlHelper.h"
#include "RCTypeTraits.h"
#include "UObject/UnrealType.h"

void FMyRemoteControlHelper::AnalyzePropertyForRemoteControl(UObject* TargetObject, FName PropertyName)
{
    if (!TargetObject) return;

    FProperty* Property = FindFProperty<FProperty>(TargetObject->GetClass(), PropertyName);
    if (!Property) return;

    UE_LOG(LogTemp, Log, TEXT("Analyzing property: %s"), *Property->GetName());

    // 检查是否支持作为映射（输出）类型
    bool bSupported = RemoteControlTypeUtilities::IsSupportedMappingType(Property);
    UE_LOG(LogTemp, Log, TEXT("Supported as Mapping Type: %s"), bSupported ? TEXT("Yes") : TEXT("No"));

    // 如果是支持的数值类型，获取其带元数据的默认范围值
    if (FNumericProperty* NumericProp = CastField<FNumericProperty>(Property))
    {
        if (NumericProp->IsFloatingPoint())
        {
            float DefaultMin = RemoteControlTypeUtilities::GetDefaultRangeValueMin<float>(Property);
            float DefaultMax = RemoteControlTypeUtilities::GetDefaultRangeValueMax<float>(Property);
            UE_LOG(LogTemp, Log, TEXT("Float Property Default Range: [%f, %f]"), DefaultMin, DefaultMax);
        }
        else if (NumericProp->IsInteger())
        {
            int64 DefaultMin = RemoteControlTypeUtilities::GetDefaultRangeValueMin<int64>(Property);
            int64 DefaultMax = RemoteControlTypeUtilities::GetDefaultRangeValueMax<int64>(Property);
            UE_LOG(LogTemp, Log, TEXT("Integer Property Default Range: [%lld, %lld]"), DefaultMin, DefaultMax);
        }
    }
}
```

## 模块依赖

`RemoteControlCommon` 模块无特殊依赖（仅标准 Core/Engine/Slate 等）。其 Build.cs 中的依赖主要是 `Core`, `CoreUObject`, `Engine`, `InputCore`, `Slate`, `SlateCore`, `UMG`, `DeveloperSettings` 等基础模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `1716f2e0` | Remote Control: added missing ApplyColorWheelDelta and ApplyColorGradingWheelDelta to the built-in a | 为内置函数白名单添加了颜色相关的缺失函数。 |
| 2026-05-20 | `d724bb52` | Remote Control: fixed uninitialized ObjectClass in FRCRemoteFunctionCallParams, sometimes causing a | 修复了远程函数调用参数中未初始化的ObjectClass可能导致的崩溃问题。 |
| 2026-05-20 | `12d5ae7f` | Remote Control: added allow list for remote function calls, and specifying built-in functions to all | 新增了远程函数调用的允许列表功能，并指定了内置的允许函数。 |
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | （无关改动，属于Motion Design模块的UI调整） |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数时产生的编译器警告。 |

### 维护评价

**活跃维护**。该插件自 2019 年创建，已有约 6 年历史，属于虚拟制片（Virtual Production）工作流的核心组件。从近期（2026 年 5 月）的提交记录看，开发团队仍在积极维护和增强其功能，包括安全加固（新增函数调用白名单）和 bug 修复。作为 Epic 官方维护的插件，其稳定性和可靠性有保障。对于需要引擎远程控制、自动化集成或多端协作的项目，**强烈推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/remote-control-in-unreal-engine/)（参考官方相关章节）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl/Source/RemoteControlCommon/Private/Tests)