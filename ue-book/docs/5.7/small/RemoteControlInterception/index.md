# Remote Control Interception API

> Plugin that allows to intercept Remote Control commands

| 属性 | 值 |
|---|---|
| 分类 | Messaging (VirtualProduction) |
| 默认启用 | Hidden (不显示在插件列表中) |
| 包含内容 | false |
| 模块 | RemoteControlInterception (Runtime) |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControlInterception) | |

## 用途

Remote Control Interception (RCI) 是 Remote Control API 的**拦截/处理扩展接口**。它基于 UE 的 Modular Features 系统，允许外部模块在 Remote Control 命令（设置属性、重置属性、调用函数、操作 Preset Controller）到达最终执行之前进行拦截和自定义处理。

这个 plugin 本身只定义接口和数据结构（4 个源文件），不包含任何实际的拦截逻辑。真正的使用方式是：

1. **Interceptor（拦截器）**：实现 `IRemoteControlInterceptionFeatureInterceptor` 接口，当 RC 命令到来时决定是放行（`Apply`）还是拦截（`Intercept`）
2. **Processor（处理器）**：实现 `IRemoteControlInterceptionFeatureProcessor` 接口，接收被拦截的命令并自行处理

设计目的是为了让 Virtual Production 工具链（如 nDisplay、Stage App）能够透明地代理或自定义 Remote Control 的行为，例如将属性变更转发到多机同步系统。

## 使用场景

- **多机同步**：你在用 nDisplay 做多机渲染，需要将 Remote Control 的属性变更同步到所有节点 → 用 RCI 拦截命令，转发给各节点的 processor
- **自定义 RPC 转发**：你需要将 Remote Control 命令通过自定义网络协议发送到远程设备 → 用 Interceptor 拦截后自行序列化发送
- **审计/日志**：你想记录所有通过 Remote Control 进行的属性修改 → 用 Interceptor 记录后再 `Apply`
- **权限控制**：你需要在 Remote Control 层面实现额外的权限检查 → 用 Interceptor 拒绝未授权的操作

## 蓝图用法

此 plugin **没有蓝图接口**。所有功能都是纯 C++ 接口，通过 `IModularFeatures` 系统注册和使用。

## C++ 用法

### 头文件引入

```cpp
// 核心接口和数据结构
#include "IRemoteControlInterceptionFeature.h"
#include "IRemoteControlInterceptionCommands.h"

// Modular Features 系统（用于注册/查找）
#include "Features/IModularFeatures.h"
```

### 核心概念

RCI 定义了两个角色，都通过 Modular Features 注册：

| 角色 | 接口 | 模板参数 | 功能 |
|---|---|---|---|
| **Interceptor** | `IRemoteControlInterceptionFeatureInterceptor` | `ERCIResponse` | 拦截 RC 命令，返回 `Apply`（放行）或 `Intercept`（拦截） |
| **Processor** | `IRemoteControlInterceptionFeatureProcessor` | `void` | 接收被拦截的命令并执行自定义处理 |

### 可拦截的命令

两种角色都需要实现以下 4 个虚函数：

| 方法 | 参数结构体 | 说明 |
|---|---|---|
| `SetObjectProperties` | `FRCIPropertiesMetadata` | 设置对象属性值 |
| `ResetObjectProperties` | `FRCIObjectMetadata` | 重置对象属性到默认值 |
| `InvokeCall` | `FRCIFunctionMetadata` | 调用 UFunction |
| `SetPresetController` | `FRCIControllerMetadata` | 操作 Preset Controller |

### 数据结构

RCI 使用独立的代理类型（前缀 `RCI`）来避免对 RemoteControl 模块的直接依赖：

| 结构体 | 关键字段 | 说明 |
|---|---|---|
| `FRCIObjectMetadata` | `ObjectPath`, `PropertyPath`, `Access` | 对象和属性的路径信息 |
| `FRCIPropertiesMetadata` | `PayloadType`, `Operation`, `Payload` | 属性值的序列化载荷（继承自 ObjectMetadata） |
| `FRCIFunctionMetadata` | `ObjectPath`, `FunctionPath`, `Payload` | 函数调用的序列化参数 |
| `FRCIControllerMetadata` | `Preset`, `Controller`, `Payload` | Controller 操作信息 |

枚举类型：

| 枚举 | 值 | 说明 |
|---|---|---|
| `ERCIResponse` | `Apply`, `Intercept` | Interceptor 的返回值 |
| `ERCIPayloadType` | `Cbor`, `Json` | 序列化格式 |
| `ERCIAccess` | `NO_ACCESS`, `READ_ACCESS`, `WRITE_ACCESS`, `WRITE_TRANSACTION_ACCESS`, `WRITE_MANUAL_TRANSACTION_ACCESS` | 属性访问模式 |
| `ERCIModifyOperation` | `EQUAL`, `ADD`, `SUBTRACT`, `MULTIPLY`, `DIVIDE` | 属性修改操作类型 |

### 基本用法：注册 Interceptor 和 Processor

```cpp
// 来源: Engine/Plugins/VirtualProduction/RemoteControl/Source/RemoteControl/Private/Tests/RemoteControlInterceptionTest.cpp

// 1. 创建实例
TUniquePtr<IRemoteControlInterceptionFeatureInterceptor> FeatureInterceptor = MakeUnique<FMyInterceptor>();
TUniquePtr<IRemoteControlInterceptionFeatureProcessor>   FeatureProcessor   = MakeUnique<FMyProcessor>();

// 2. 注册到 Modular Features
IModularFeatures& ModularFeatures = IModularFeatures::Get();
ModularFeatures.RegisterModularFeature(IRemoteControlInterceptionFeatureInterceptor::GetName(), FeatureInterceptor.Get());
ModularFeatures.RegisterModularFeature(IRemoteControlInterceptionFeatureProcessor::GetName(),   FeatureProcessor.Get());

// 3. 用完后取消注册
ModularFeatures.UnregisterModularFeature(IRemoteControlInterceptionFeatureInterceptor::GetName(), FeatureInterceptor.Get());
ModularFeatures.UnregisterModularFeature(IRemoteControlInterceptionFeatureProcessor::GetName(),   FeatureProcessor.Get());
```

### 进阶用法：实现一个简单的 Forward Interceptor

参考官方测试代码中的 `FRemoteControlInterceptionForwardInterceptor`，它将拦截到的命令直接转发给所有已注册的 Processor：

```cpp
// 来源: Engine/Plugins/VirtualProduction/RemoteControl/Source/RemoteControl/Private/Tests/RemoteControlInterceptionForwardInterceptor.cpp

class FMyInterceptor : public IRemoteControlInterceptionFeatureInterceptor
{
public:
    virtual ERCIResponse SetObjectProperties(FRCIPropertiesMetadata& InObjectProperties) override
    {
        // 遍历所有已注册的 Processor，转发命令
        IModularFeatures& ModularFeatures = IModularFeatures::Get();
        const FName ProcessorName = IRemoteControlInterceptionFeatureProcessor::GetName();
        const int32 NumProcessors = ModularFeatures.GetModularFeatureImplementationCount(ProcessorName);

        for (int32 i = 0; i < NumProcessors; ++i)
        {
            auto* Processor = static_cast<IRemoteControlInterceptionFeatureProcessor*>(
                ModularFeatures.GetModularFeatureImplementation(ProcessorName, i));
            if (Processor)
            {
                Processor->SetObjectProperties(InObjectProperties);
            }
        }

        // 有 Processor 接收则拦截，否则放行由 RC 自行处理
        return NumProcessors > 0 ? ERCIResponse::Intercept : ERCIResponse::Apply;
    }

    // 同理实现 ResetObjectProperties、InvokeCall、SetPresetController...
};
```

## Demo 示例

### 最小可编译 Interceptor + Processor

```cpp
// MyRCIProcessor.h
#pragma once
#include "IRemoteControlInterceptionFeature.h"

class FMyRCIProcessor : public IRemoteControlInterceptionFeatureProcessor
{
public:
    virtual void SetObjectProperties(FRCIPropertiesMetadata& InProperties) override
    {
        // 在这里处理属性变更，例如记录日志
        UE_LOG(LogTemp, Log, TEXT("RCI: SetObjectProperties on %s, property %s"),
            *InProperties.ObjectPath, *InProperties.PropertyPath);
    }

    virtual void ResetObjectProperties(FRCIObjectMetadata& InObject) override
    {
        UE_LOG(LogTemp, Log, TEXT("RCI: ResetObjectProperties on %s"), *InObject.ObjectPath);
    }

    virtual void InvokeCall(FRCIFunctionMetadata& InFunction) override
    {
        UE_LOG(LogTemp, Log, TEXT("RCI: InvokeCall %s on %s"),
            *InFunction.FunctionPath, *InFunction.ObjectPath);
    }

    virtual void SetPresetController(FRCIControllerMetadata& InController) override
    {
        UE_LOG(LogTemp, Log, TEXT("RCI: SetPresetController %s:%s"),
            *InController.Preset.ToString(), *InController.Controller.ToString());
    }
};
```

**Build.cs 依赖**：此 plugin 的所有依赖都是 `PrivateDependencyModuleNames`（Cbor, Core, CoreUObject, Engine, Serialization）。使用方不需要额外依赖这些模块，只需 `#include` 头文件即可。但如果你需要使用 `IRemoteControlModule` 来主动发起 RC 命令，则需要依赖 `RemoteControl` 模块。

## 模块依赖

此 plugin 的依赖全部为私有依赖，**对使用者透明**：

| 模块 | 用途 |
|---|---|
| `Cbor` | CBOR 序列化格式支持 |
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `Serialization` | 序列化框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-23 | `df329aa` | Motion Design: removed beta tag from motion design plugins | 批量修改，非 RCI 专属更新 |
| 2022-10-21 | `610c467` | Update vendor links for built-in plugins to use secure protocol | 文档链接更新，非功能性改动 |
| 2022-08-26 | `c6e8791` | Fix stage app failing to control nDisplay nodes when connected directly | **功能性修复**：修复 Stage App 直连 nDisplay 节点时的控制问题，说明 RCI 在 VP 工作流中被实际使用 |

### 维护评价

- **创建时间**：2021-04-29，约 5 年历史
- **最后实质性更新**：2022-08-26（功能性修复），距今超过 3 年
- **接口稳定性**：plugin 本身只有 4 个源文件，定义的是接口层，非常稳定
- **实际使用者**：Stage App、nDisplay 等 VP 工具链依赖此接口
- **状态**：接口层已基本定型，不太可能有大的变更。作为 Virtual Production 管线的一部分，仍在使用中但不活跃开发
- **推荐**：如果你在开发 VP 工具需要拦截/代理 Remote Control 命令，这是唯一官方支持的接口。直接使用即可，不用担心废弃风险——只要 Remote Control API 存在，这个接口就会保留

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControlInterception)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/RemoteControl/Source/RemoteControl/Private/Tests/RemoteControlInterceptionTest.cpp)（位于 RemoteControl plugin 内部）
- [ForwardInterceptor 参考实现](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/RemoteControl/Source/RemoteControl/Private/Tests/RemoteControlInterceptionForwardInterceptor.h)
