# Remote Control Protocol OSC

> Allows interactions between OSC and RemoteControl API.

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制OSC协议 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControlProtocolOSC` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-04-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControlProtocolOSC) | |

## 用途

该插件为 Unreal Engine 的 Remote Control API 提供 OSC（Open Sound Control）协议支持，使外部 OSC 设备或软件能够通过网络控制引擎内的属性。

核心功能包括：
- 将 OSC 消息地址映射到 Remote Control 的属性绑定
- 管理 OSC 服务器实例，接收外部 OSC 消息
- 支持自动绑定（AutoBinding）机制，根据 OSC 地址自动关联 Remote Control 实体
- 支持范围输入（0.0-1.0），适用于滑块、旋钮等连续值控制

## 使用场景

- 你在使用 TouchOSC、Lemur 等 OSC 控制器远程控制 Unreal Engine 中的灯光、材质参数
- 你在虚拟制片场景中需要通过 OSC 协议控制远程控制面板暴露的属性
- 你需要将外部音频软件（如 Max/MSP、Ableton Live）的 OSC 输出映射到引擎参数

## 蓝图用法

该插件主要通过 Remote Control 面板的编辑器界面进行配置，蓝图层面暴露的功能有限。核心配置通过 `URemoteControlProtocolOSCSettings` 进行。

### 核心配置

配置通过 **编辑器 → 项目设置 → Plugins → OSC** 进行：

| 设置项 | 说明 |
|---|---|
| `ServersSettings` | OSC 服务器列表，每项包含 IP 地址和端口（默认 `127.0.0.1:8001`） |

### OSC 协议实体属性

在 Remote Control 面板中绑定 OSC 协议时，可配置：

| 属性 | 说明 |
|---|---|
| `PathName` | OSC 地址路径，格式为 `/Container1/Container2/Method` |
| `RangeInputTemplate` | 范围输入模板值（0.0-1.0），用于绑定映射 |

## C++ 用法

### 头文件引入

```cpp
#include "RemoteControlProtocolOSC.h"
```

### 基本用法

自定义 OSC 协议实体，检查绑定重复：

```cpp
// 检查两个 OSC 协议实体是否相同（用于去重）
FRemoteControlOSCProtocolEntity* EntityA = /* ... */;
FRemoteControlOSCProtocolEntity* EntityB = /* ... */;

if (EntityA->IsSame(EntityB))
{
    // 两个实体绑定到相同的 OSC 路径和参数，视为重复
}
```

### 进阶用法

通过 C++ 直接操作 OSC 绑定映射：

```cpp
// 获取 OSC 协议实例
FRemoteControlProtocolOSC* OSCProtocol = /* 获取协议实例 */;

// 绑定一个 Remote Control 实体到 OSC
FRemoteControlProtocolEntityPtr EntityPtr = /* ... */;
OSCProtocol->Bind(EntityPtr);

// 处理接收到的 OSC 消息
// 内部会根据 PathName 查找绑定的实体并更新其值
```

## Demo 示例

### 自定义 OSC 服务器设置

```cpp
// RemoteControlOSCDemo.h
#pragma once

#include "CoreMinimal.h"

class FRemoteControlOSCDemo
{
public:
    /** 初始化自定义 OSC 服务器 */
    static void InitCustomServer();
};
```

```cpp
// RemoteControlOSCDemo.cpp
#include "RemoteControlOSCDemo.h"
#include "RemoteControlProtocolOSCSettings.h"

void FRemoteControlOSCDemo::InitCustomServer()
{
    // 获取默认配置对象
    URemoteControlProtocolOSCSettings* Settings = GetMutableDefault<URemoteControlProtocolOSCSettings>();
    
    // 添加自定义服务器配置
    FRemoteControlOSCServerSettings ServerSetting;
    ServerSetting.ServerAddress = TEXT("0.0.0.0:9000");
    Settings->ServersSettings.Add(ServerSetting);
    
    // 初始化所有 OSC 服务器
    Settings->InitOSCServers();
}
```

## 模块依赖

该插件依赖以下插件（声明在 .uplugin 中）：

| 依赖插件 | 用途 |
|---|---|
| `RemoteControl` | 提供 Remote Control API 核心框架 |
| `OSC` | 提供 OSC 协议通信基础（UOSCServer、FOSCMessage 等） |

| 模块 | 用途 |
|---|---|
| `OSC` | OSC 消息解析与服务器管理 |
| `RemoteControl` | Remote Control 协议接口与实体绑定框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移，将 UE_LOG 替换为 UE_LOGF |
| 2025-09-16 | `77ee7eae` | Motion Design: removed beta tag from motion design plugins. | 移除 Motion Design 插件的 beta 标签 |
| 2025-07-24 | `cfcacc25` | Handle invalid or null OSC protocol entity. | 处理无效或空的 OSC 协议实体，增加安全性检查 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件批量更新 |
| 2022-11-03 | `fa90b399` | Added includes for future change. This changelist only contains added #include and a couple of empty | 预添加头文件包含，为后续修改做准备 |

### 维护评价

- **活跃度**：该插件仍在维护中，最近一次功能性更新在 2025-07-24，增加了空值保护
- **稳定性**：作为 Runtime 模块，代码结构简洁，无实验性标记
- **更新频率**：更新频率较低，属于稳定型插件，符合协议类插件的特征
- **推荐使用**：✅ 推荐。作为 VirtualProduction 工作流的基础组件，由 Epic 维护，适合生产环境使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControlProtocolOSC)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControlProtocolOSC/Tests)（未发现测试文件）