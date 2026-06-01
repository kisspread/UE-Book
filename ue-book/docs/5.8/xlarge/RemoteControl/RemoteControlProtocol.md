# Remote Control Protocol

> A suite of tools for controlling the Unreal Engine, both in Editor or at Runtime via a webserver. This allows users to control Unreal Engine remotely through HTTP or WebSockets requests. This functionality allows developers to control Unreal through 3rd party applications and web services.

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制协议框架 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControlProtocol` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl/Source/RemoteControlProtocol) | |

> **注意**：本文档描述的是 Remote Control API 插件中的 **RemoteControlProtocol** 子模块。该插件共包含 8 个模块，完整插件详见 [RemoteControl 插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl)。

## 用途

RemoteControlProtocol 模块为 Remote Control 系统提供**协议抽象层**。它定义了一套统一的接口框架，使得不同的外部协议（如 DMX、OSC、MIDI 等）可以以插件方式接入远程控制系统。

核心解决的问题：
- **协议解耦**：将"如何通过 HTTP/WebSocket 暴露属性"与"如何通过具体协议驱动属性值"分离
- **多协议并存**：支持同时注册多个协议，每个协议独立管理自己的绑定实体
- **帧同步队列**：协议值在帧内排队，避免同一帧多次写入同一属性
- **编辑器集成**：通过列系统（Column）为不同协议提供自定义 UI 展示

该模块是 Remote Control 生态的底层基石，上层的 `RemoteControlLogic` 和 `WebRemoteControl` 都依赖它。

## 使用场景

- 你需要通过 DMX 协议控制 UE 内的灯光参数 → 使用此模块注册 DMX 协议实现
- 你需要让第三方控制台（如 GrandMA）远程调节材质参数 → 通过协议绑定暴露的属性
- 你需要开发自定义控制协议（如私有 UDP 协议） → 继承 `FRemoteControlProtocol` 并注册
- 你在做虚拟制片，需要实时通过协议驱动 Actor 属性 → 此模块提供帧级队列保证线程安全

## 蓝图用法

本模块是底层协议框架层，主要面向 C++ 开发者。蓝图层面的远程控制操作（如添加/暴露属性）由上层 `RemoteControl` 和 `RemoteControlLogic` 模块提供。

### 核心节点

本模块不直接暴露蓝图节点，但通过 `FRCSignatureProtocolAction` 可在 Remote Control Signature 系统中配置协议动作。

| 属性 | 说明 | 所在类 |
|---|---|---|
| `ProtocolName` | 选择使用的协议名称 | `FRCSignatureProtocolAction` |
| `ProtocolEntity` | 协议实体配置（协议特定数据） | `FRCSignatureProtocolAction` |
| `MappingSpace` | 值映射方式：Additive/Multiply/Absolute | `FRCSignatureProtocolAction` |
| `OverrideMask` | 多维属性的位掩码覆盖 | `FRCSignatureProtocolAction` |
| `bSingleProtocolChannel` | 是否将所有掩码合并到单通道 | `FRCSignatureProtocolAction` |

## C++ 用法

### 头文件引入

```cpp
// 模块接口
#include "IRemoteControlProtocolModule.h"

// 协议接口
#include "IRemoteControlProtocol.h"

// 基类实现
#include "RemoteControlProtocol.h"
```

### 基本用法

**获取协议模块并注册自定义协议**：

```cpp
// 来源: Public/IRemoteControlProtocolModule.h

// 获取协议模块单例
IRemoteControlProtocolModule& ProtocolModule = IRemoteControlProtocolModule::Get();

// 注册自定义协议
TSharedRef<IRemoteControlProtocol> MyProtocol = MakeShared<FMyCustomProtocol>(FName("MyProtocol"));
ProtocolModule.AddProtocol(FName("MyProtocol"), MyProtocol);

// 查询已注册协议
TArray<FName> ProtocolNames = ProtocolModule.GetProtocolNames();
int32 NumProtocols = ProtocolModule.GetProtocolNum();
```

### 进阶用法

**实现自定义协议（继承 FRemoteControlProtocol）**：

```cpp
// 来源: Public/RemoteControlProtocol.h + Public/IRemoteControlProtocol.h

class FMyDMXProtocol : public FRemoteControlProtocol
{
public:
    FMyDMXProtocol() : FRemoteControlProtocol(FName("MyDMX")) {}

    virtual void Init() override
    {
        // 初始化协议连接（如打开 UDP Socket）
    }

    virtual FRemoteControlProtocolEntityPtr CreateNewProtocolEntity(
        FProperty* InProperty,
        URemoteControlPreset* InOwner,
        FGuid InPropertyId) const override
    {
        // 创建协议特定的绑定实体
        FRemoteControlProtocolEntityPtr Entity = MakeShared<TStructOnScope<FRemoteControlProtocolEntity>>();
        Entity->InitializeAs<FMyDMXProtocolEntity>();
        return Entity;
    }

    virtual UScriptStruct* GetProtocolScriptStruct() const override
    {
        return FMyDMXProtocolEntity::StaticStruct();
    }

    virtual void Bind(FRemoteControlProtocolEntityPtr InEntityPtr) override
    {
        // 开始监听该实体对应的 DMX 通道
    }

    virtual void Unbind(FRemoteControlProtocolEntityPtr InEntityPtr) override
    {
        // 停止监听
    }

    virtual void UnbindAll() override
    {
        // 停止所有监听
    }

    virtual void QueueValue(
        const FRemoteControlProtocolEntityPtr InProtocolEntity,
        const double InProtocolValue) override
    {
        // 将收到的协议值排队，下一帧统一应用
        // 基类 FRemoteControlProtocol 已提供默认实现
        FRemoteControlProtocol::QueueValue(InProtocolEntity, InProtocolValue);
    }

    // 帧回调（可选）
    virtual void OnBeginFrame() override
    {
        // 帧开始时处理（如读取外部数据）
    }
};
```

**应用/解除协议绑定到 Preset**：

```cpp
// 来源: Private/RemoteControlProtocolModule.h

IRemoteControlProtocolModule& Module = IRemoteControlProtocolModule::Get();

// 当 Preset 加载完成后，应用所有协议绑定
Module.ApplyProtocolBindings(MyPreset);

// 关闭时解除绑定
Module.UnapplyProtocolBindings(MyPreset);
```

## Demo 示例

一个最小的自定义协议实现：

**MyCustomProtocol.h**：

```cpp
#pragma once

#include "RemoteControlProtocol.h"

USTRUCT()
struct FMyCustomProtocolEntity : public FRemoteControlProtocolEntity
{
    GENERATED_BODY()

    // 协议特定参数（如通道号）
    UPROPERTY(EditAnywhere, Category = "Protocol")
    int32 Channel = 0;
};

class FMyCustomProtocol : public FRemoteControlProtocol
{
public:
    FMyCustomProtocol();

    virtual void Init() override;
    virtual FRemoteControlProtocolEntityPtr CreateNewProtocolEntity(
        FProperty* InProperty,
        URemoteControlPreset* InOwner,
        FGuid InPropertyId) const override;
    virtual UScriptStruct* GetProtocolScriptStruct() const override;
    virtual void Bind(FRemoteControlProtocolEntityPtr InEntityPtr) override;
    virtual void Unbind(FRemoteControlProtocolEntityPtr InEntityPtr) override;
    virtual void UnbindAll() override;
    virtual void QueueValue(
        const FRemoteControlProtocolEntityPtr InProtocolEntity,
        const double InProtocolValue) override;
};
```

**MyCustomProtocol.cpp**：

```cpp
#include "MyCustomProtocol.h"

FMyCustomProtocol::FMyCustomProtocol()
    : FRemoteControlProtocol(FName("MyCustom"))
{
}

void FMyCustomProtocol::Init()
{
    // 初始化协议资源
    UE_LOG(LogTemp, Log, TEXT("MyCustom Protocol initialized"));
}

FRemoteControlProtocolEntityPtr FMyCustomProtocol::CreateNewProtocolEntity(
    FProperty* InProperty,
    URemoteControlPreset* InOwner,
    FGuid InPropertyId) const
{
    FRemoteControlProtocolEntityPtr Entity =
        MakeShared<TStructOnScope<FRemoteControlProtocolEntity>>();
    Entity->InitializeAs<FMyCustomProtocolEntity>();
    return Entity;
}

UScriptStruct* FMyCustomProtocol::GetProtocolScriptStruct() const
{
    return FMyCustomProtocolEntity::StaticStruct();
}

void FMyCustomProtocol::Bind(FRemoteControlProtocolEntityPtr InEntityPtr)
{
    // 注册通道监听
}

void FMyCustomProtocol::Unbind(FRemoteControlProtocolEntityPtr InEntityPtr)
{
    // 取消通道监听
}

void FMyCustomProtocol::UnbindAll()
{
    // 清理所有监听
}

void FMyCustomProtocol::QueueValue(
    const FRemoteControlProtocolEntityPtr InProtocolEntity,
    const double InProtocolValue)
{
    // 调用基类排队（在 OnBeginFrame 中统一应用）
    FRemoteControlProtocol::QueueValue(InProtocolEntity, InProtocolValue);
}
```

**注册协议（在模块 StartupModule 中）**：

```cpp
#include "IRemoteControlProtocolModule.h"
#include "MyCustomProtocol.h"

void FMyGameModule::StartupModule()
{
    IRemoteControlProtocolModule& RCProtocolModule = IRemoteControlProtocolModule::Get();
    MyProtocol = MakeShared<FMyCustomProtocol>();
    RCProtocolModule.AddProtocol(FName("MyCustom"), MyProtocol.ToSharedRef());
}

void FMyGameModule::ShutdownModule()
{
    IRemoteControlProtocolModule& RCProtocolModule = IRemoteControlProtocolModule::Get();
    RCProtocolModule.RemoveProtocol(FName("MyCustom"), MyProtocol.ToSharedRef());
}
```

## 模块依赖

从模块结构推断的依赖关系：

| 模块 | 用途 |
|---|---|
| `RemoteControlCommon` | 共享类型定义（`FRemoteControlProtocolEntity`、`FRemoteControlProtocolBinding` 等） |
| `RemoteControlLogic` | `URemoteControlPreset`、Signature 系统（`FRCSignatureAction` 基类） |

> 依赖列表根据头文件引用推断，完整依赖请参考 [RemoteControlProtocol.Build.cs](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/VirtualProduction/RemoteControl/Source/RemoteControlProtocol/RemoteControlProtocol.Build.cs)。

## 维护状态

### 近期更新

以下为 RemoteControl 插件整体的近期提交（RemoteControlProtocol 模块随插件一起维护）：

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `1716f2e0` | Remote Control: added missing ApplyColorWheelDelta and ApplyColorGradingWheelDelta to the built-in a | 补充内置协议的色轮增量和色彩分级增量功能 |
| 2026-05-20 | `d724bb52` | Remote Control: fixed uninitialized ObjectClass in FRCRemoteFunctionCallParams, sometimes causing a | 修复远程函数调用参数中 ObjectClass 未初始化导致的崩溃 |
| 2026-05-20 | `12d5ae7f` | Remote Control: added allow list for remote function calls, and specifying built-in functions to all | 新增远程函数调用白名单及内置函数权限控制 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |

### 维护评价

- **创建时间**：2019 年 6 月，约 7 年历史
- **维护状态**：**活跃维护中** — 2026 年 5 月仍有功能性更新和 bug 修复
- **更新频率**：近期更新频繁（单月多次提交），主要集中在协议功能增强和稳定性修复
- **代码质量**：接口设计清晰，采用模块化协议注册机制，支持命令行禁用（`-RCProtocolsDisable`）
- **推荐程度**：✅ 推荐使用。作为 Epic 官方虚拟制片工具链的核心组件，持续获得维护和功能更新。适用于任何需要通过外部协议与 UE 交互的场景。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl/Source/RemoteControlProtocol)
- [RemoteControl 插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl)
- [官方文档](https://docs.unrealengine.com/en-US/production-pipelines/virtual-production/remote-control/)