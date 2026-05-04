# Remote Control API

> A suite of tools for controlling the Unreal Engine, both in Editor or at Runtime via a webserver. This allows users to control Unreal Engine remotely through HTTP or WebSockets requests. This functionality allows developers to control Unreal through 3rd party applications and web services.

| 属性 | 值 |
|---|---|
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControl` (Runtime), `RemoteControlCommon` (Runtime), `RemoteControlLogic` (Runtime), `RemoteControlMultiUser` (Runtime), `RemoteControlProtocol` (Runtime), `RemoteControlProtocolWidgets` (Runtime), `RemoteControlUI` (Runtime), `WebRemoteControl` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-07 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl) | |

## 用途

Remote Control API 是一套完整的远程控制框架，允许通过 HTTP REST API 和 WebSocket 连接从外部应用程序控制 Unreal Engine。它解决的核心问题是：**在虚拟制片（Virtual Production）工作流中，需要从外部设备（如 iPad、自定义控制面板、第三方软件）实时操控引擎中的 Actor 属性、调用函数、修改材质参数等**。

该插件通过"预设（Preset）"系统组织暴露的属性和函数，开发者可以在编辑器中选择要暴露的 Actor、Component 和属性，然后通过 Web API 进行读写操作。它还支持协议扩展（Protocol），允许通过自定义通信协议（如 OSC、MIDI 等）绑定属性。

## 使用场景

- 你在做虚拟制片，需要用 iPad 远程调整灯光参数 → 用 Remote Control API 的 Web 接口
- 你需要从自定义控制台应用实时修改引擎中的 Actor 属性 → 用 HTTP/WebSocket API
- 你要将引擎属性绑定到 OSC/MIDI 等外部协议 → 用 Remote Control Protocol 系统
- 你需要在多人协作环境中同步远程控制操作 → 用 RemoteControlMultiUser
- 你要构建一个 Web 界面来控制引擎 → 用 WebRemoteControl 的 REST API

## 模块架构

本插件由 8 个模块组成，按职责分层：

```
┌─────────────────────────────────────────────────┐
│              WebRemoteControl                    │  ← HTTP/WebSocket 服务器
├─────────────────────────────────────────────────┤
│  RemoteControlUI  │  RemoteControlProtocolWidgets│  ← 编辑器 UI
├─────────────────────────────────────────────────┤
│  RemoteControlProtocol  │  RemoteControlMultiUser│  ← 协议 & 多用户
├─────────────────────────────────────────────────┤
│              RemoteControlLogic                  │  ← 核心逻辑层
├─────────────────────────────────────────────────┤
│              RemoteControl                       │  ← 核心数据模型
├─────────────────────────────────────────────────┤
│              RemoteControlCommon                 │  ← 公共工具 & 类型系统
└─────────────────────────────────────────────────┘
```

| 模块 | 职责 |
|---|---|
| `RemoteControlCommon` | 公共类型定义、属性容器、类型工具、网络地址配置 |
| `RemoteControl` | 核心数据模型：Preset、暴露的属性/函数/Actor |
| `RemoteControlLogic` | 核心逻辑：属性读写、函数调用、蓝图操作 |
| `RemoteControlProtocol` | 协议抽象层，支持自定义通信协议绑定 |
| `RemoteControlProtocolWidgets` | 协议相关的编辑器 UI 控件 |
| `RemoteControlMultiUser` | 多用户 Multi-User Editing 集成 |
| `RemoteControlUI` | 编辑器面板和 UI 组件 |
| `WebRemoteControl` | HTTP REST API 和 WebSocket 服务器 |

## 子模块文档

由于本插件规模为 xlarge（659 个源文件），以下按子模块分别说明：

### RemoteControlCommon

公共基础模块，提供类型系统和工具类。

**核心类型：**

- **`ERCMask`** — 属性掩码枚举（MaskA-D），用于选择性暴露属性
- **`ERCProtocolBinding`** — 协议绑定操作（Added/Removed）
- **`FRCNetworkAddress`** — IPv4 网络地址结构体
- **`FRCNetworkAddressRange`** — IP 地址范围，用于白名单/黑名单控制

**核心类：**

- **`URCPropertyContainerBase`** — 属性值容器基类，安全存储和读取属性值
- **`URCPropertyContainerRegistry`** — 属性容器注册表子系统，缓存动态创建的容器类
- **`FRCPropertyVariant`** — 属性变体，统一处理 PropertyHandle 和原始属性数据

**工具命名空间：**

- `RemoteControlPropertyUtilities` — 属性操作工具（获取/设置值、类型转换）
- `RemoteControlTypeUtilities` — 类型转换工具（FOREACH_CAST_PROPERTY 宏等）
- `RemoteControlTypeTraits` — 类型特征（数值类型、字符串类型判断）

### RemoteControl

核心数据模型模块，定义 Remote Control Preset 和暴露项。

### RemoteControlLogic

逻辑执行模块，处理属性读写和函数调用的实际执行。

### RemoteControlProtocol

协议抽象层，允许通过不同通信协议（OSC、自定义协议等）绑定和控制属性。

### WebRemoteControl

Web 服务器模块，提供 HTTP REST API 和 WebSocket 接口。

**主要 API 端点（推测）：**

- `GET /remote/preset/{id}` — 获取预设信息
- `PUT /remote/preset/{id}/property` — 设置属性值
- `POST /remote/preset/{id}/call` — 调用暴露的函数
- WebSocket 连接用于实时属性推送和双向通信

### RemoteControlUI

编辑器 UI 模块，提供 Remote Control 面板。

### RemoteControlProtocolWidgets

协议配置相关的编辑器控件。

### RemoteControlMultiUser

与 Multi-User Editing 系统集成，确保远程控制操作在多人协作中同步。

## C++ 用法

### 头文件引入

```cpp
#include "RemoteControlCommon.h"
#include "RCPropertyContainer.h"
#include "RemoteControlSettings.h"
```

### 基本用法 — 属性容器

```cpp
// 创建属性容器来安全存储属性值
// 来源: RCPropertyContainer.h

// 获取属性容器注册表
URCPropertyContainerRegistry* Registry = GEngine->GetEngineSubsystem<URCPropertyContainerRegistry>();

// 使用属性容器设置和获取值
URCPropertyContainerBase* Container = /* 从注册表获取 */;

// 设置值（原始数据）
float NewValue = 42.0f;
Container->SetValue(reinterpret_cast<const uint8*>(&NewValue), sizeof(float));

// 获取值
float OutValue = 0.0f;
Container->GetValue(reinterpret_cast<uint8*>(&OutValue));

// 模板方式设置值
Container->SetValue<float>(42.0f);

// 模板方式获取值
float* ValuePtr = Container->GetValue<float>();
```

### 基本用法 — 属性变体

```cpp
// 使用 FRCPropertyVariant 统一处理属性数据
// 来源: RCPropertyUtilities.h

// 从原始属性和数据构造
FProperty* Property = SomeActor->GetClass()->FindPropertyByName(FName("ActorLocation"));
void* Data = Property->ContainerPtrToValuePtr<void>(SomeActor);

FRCPropertyVariant Variant(Property, Data);

// 获取属性值
FVector* Location = Variant.GetPropertyValue<FVector>();

// 从 PropertyHandle 构造（编辑器环境）
#if WITH_EDITOR
TSharedPtr<IPropertyHandle> Handle = /* 获取 PropertyHandle */;
FRCPropertyVariant HandleVariant(Handle);
#endif
```

### 基本用法 — 网络配置

```cpp
// 配置远程控制的网络地址
// 来源: RemoteControlSettings.h

// 创建网络地址
FRCNetworkAddress Address(192, 168, 1, 100);
FString AddressStr = Address.ToString(); // "192.168.1.100"

// 创建地址范围（白名单）
FRCNetworkAddressRange Range(
    FRCNetworkAddress(192, 168, 1, 0),
    FRCNetworkAddress(192, 168, 1, 255)
);

// 允许所有 IP
FRCNetworkAddressRange AllowAll = FRCNetworkAddressRange::AllowAllIPs();
```

### 基本用法 — 掩码系统

```cpp
// 使用掩码选择性暴露属性
// 来源: RemoteControlCommon.h

ERCMask Mask = ERCMask::MaskA | ERCMask::MaskB;

// 检查是否包含特定掩码
if (EnumHasAnyFlags(Mask, ERCMask::MaskA))
{
    // 属性属于 MaskA 组
}

// 初始化为所有掩码
ERCMask AllMasks = RC_AllMasks;
```

### 进阶用法 — 类型特征

```cpp
// 使用类型特征系统处理不同属性类型
// 来源: RCTypeTraits.h

// 检查是否为数值类型
static_assert(RemoteControlTypeTraits::TNumericValueConstraint_V<float>, "float is numeric");
static_assert(RemoteControlTypeTraits::TNumericValueConstraint_V<int32>, "int32 is numeric");

// 检查是否为字符串类型
static_assert(RemoteControlTypeTraits::TIsStringLikeProperty<FStrProperty>::Value);
static_assert(RemoteControlTypeTraits::TIsStringLikeValue<FString>::Value);

// 使用 FOREACH_CAST_PROPERTY 宏遍历属性类型
FProperty* SomeProperty = /* 获取属性 */;
FOREACH_CAST_PROPERTY(SomeProperty, HandleProperty<CastPropertyType>(CastProperty));
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HTTP` | HTTP 服务器和客户端支持 |
| `Json` | JSON 序列化/反序列化 |
| `JsonUtilities` | JSON 与 UObject 之间的转换 |
| `WebSockets` | WebSocket 通信支持 |
| `Networking` | 网络基础功能 |
| `MultiUserClient` / `MultiUserServer` | 多用户编辑集成 |

## 维护状态

### 近期更新

```
- e6045b2d7cca Remote Control: The Protocol Generate Transactions option is now available per Preset instead of being a global option in Project Settings
- 4af2fd066dd0 Updating Dev-Release-5.5 from Main at CL #36144969
- befcdf0cadd7 Remote Control: Protocols no longer create Transactions by default. Add a performance mode for Protocols to Project Settings
```

### 维护评价

Remote Control API 是 Epic Games 虚拟制片工具链的核心组件之一，**持续活跃维护中**。

- **创建时间**：2019 年，约 6 年历史
- **维护状态**：活跃。近期有功能性更新（协议事务选项从全局改为按 Preset 配置、性能模式优化）
- **代码规模**：659 个源文件，8 个模块，架构成熟
- **稳定性**：作为 Virtual Production 工作流的关键组件，经过大量生产环境验证
- **推荐程度**：⭐⭐⭐⭐⭐ 强烈推荐。如果你需要从外部控制引擎，这是官方标准方案

**注意事项**：
- 该插件默认启用，但完整的 Web 服务器功能需要在项目设置中配置端口和安全选项
- 生产环境中应注意 API 安全，配置 IP 白名单
- 多用户功能需要额外的 Multi-User Editing 模块支持

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/remote-control-api-in-unreal-engine/)