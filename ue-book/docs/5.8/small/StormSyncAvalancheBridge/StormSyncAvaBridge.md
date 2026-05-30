# Storm Sync Motion Design Bridge

> Plugin bridge between Motion Design Plugin and Storm Sync to provide in-editor integration to synchronize assets

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计同步桥接 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `StormSyncAvaBridge` (Runtime), `StormSyncAvaBridgeEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSyncAvalancheBridge) | |

## 用途

StormSyncAvalancheBridge 是连接 **Motion Design（Avalanche）** 和 **Storm Sync** 两个插件的桥接层。

Storm Sync 提供了基于消息总线的资产同步能力（push/pull/compare），而 Motion Design 的播放系统（Avalanche Media Playback）需要在多个编辑器实例之间同步运动设计资产。这个插件解决了以下核心问题：

1. **地址自动发现与注册**：将 Storm Sync 的服务器/客户端/发现管理器的消息总线地址写入 Avalanche 播放服务器的 User Data 中，使得远端播放客户端可以自动获取同步地址
2. **资产同步能力**：实现 `IAvaMediaSyncProvider` 接口，为 Motion Design 提供 push/pull/compare 操作，底层调用 Storm Sync 的传输协议
3. **用户数据同步**：播放服务器启动/停止时自动更新 User Data，通过 Avalanche 的播放系统复制到远端客户端，实现自动发现

简单来说：没有这个桥接插件，Motion Design 用户无法利用 Storm Sync 来同步运动设计资产到其他远程编辑器实例。

## 使用场景

- 你正在使用 Motion Design（Avalanche）在多个编辑器实例之间进行实时运动设计预览 → 需要此插件自动处理资产同步
- 你在虚拟制片工作流中，一台机器编辑运动设计资产，需要实时推送到渲染机器的编辑器实例 → 启用此插件后可一键 push
- 你需要比较本地和远程编辑器实例的资产差异 → 使用 Compare 功能

## 前置依赖

此插件需要以下两个插件同时启用：
- **Avalanche**（Motion Design 核心插件）
- **StormSync**（资产同步插件）

## 蓝图用法

本插件主要作为运行时桥接层，核心功能通过模块化特性（Modular Feature）注册，对外暴露 `IAvaMediaSyncProvider` 接口。直接暴露给蓝图的节点较少。

### 工具函数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetServerNamesForChannel` | 获取指定频道下所有 Avalanche 播放服务器名称列表 | `FStormSyncAvaBridgeUtils` |

### 使用示例

该插件的主要功能在后台自动工作：

1. 启用插件后，当 Storm Sync 服务器启动时，插件会自动将消息总线地址注册到 Avalanche 播放服务器的 User Data
2. 远端播放客户端通过 User Data 自动发现 Storm Sync 地址
3. 在 Motion Design 编辑器中，同步操作（push/pull/compare）通过模块化特性系统自动路由到 Storm Sync 实现

## C++ 用法

### 头文件引入

```cpp
#include "StormSyncAvaBridgeCommon.h"
#include "StormSyncAvaBridgeUtils.h"
```

### 基本用法 - 获取指定频道的播放服务器列表

```cpp
#include "StormSyncAvaBridgeUtils.h"

// 获取某个频道下的所有 Avalanche 播放服务器名称
TArray<FString> ServerNames = FStormSyncAvaBridgeUtils::GetServerNamesForChannel(TEXT("MyChannel"));

for (const FString& ServerName : ServerNames)
{
    UE_LOG(LogTemp, Log, TEXT("Found playback server: %s"), *ServerName);
}
```

### 进阶用法 - 直接访问 IAvaMediaSyncProvider 接口

由于插件通过模块化特性注册了同步提供者，可以直接通过 Modular Feature 系统访问：

```cpp
#include "Features/IModularFeatures.h"

// 获取所有注册的 Ava Media Sync Provider
IModularFeatures& ModularFeatures = IModularFeatures::Get();

if (ModularFeatures.IsModularFeatureAvailable(IAvaMediaSyncProvider::GetModularFeatureName()))
{
    TArray<IAvaMediaSyncProvider*> Providers = ModularFeatures.GetModularFeatureImplementations<IAvaMediaSyncProvider>(
        IAvaMediaSyncProvider::GetModularFeatureName()
    );

    for (IAvaMediaSyncProvider* Provider : Providers)
    {
        // 执行资产比较
        TArray<FName> PackageNames = { TEXT("/Game/MyMotionDesign/MyAsset") };
        FString RemoteName = TEXT("RenderMachine");

        Provider->CompareWithRemote(RemoteName, PackageNames,
            FOnAvaMediaSyncCompareResponse::CreateLambda([](const FAvaMediaSyncCompareResponse& Response)
            {
                // 处理比较结果
                UE_LOG(LogTemp, Log, TEXT("Compare complete. Has differences: %s"),
                    Response.bHasDifferences ? TEXT("Yes") : TEXT("No"));
            })
        );
    }
}
```

## Demo 示例

一个最小示例，演示如何在 C++ 中使用 Storm Sync 桥接的 User Data 常量和工具函数：

### StormSyncBridgeDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"

class FStormSyncBridgeDemo
{
public:
    /** 演示如何读取 Storm Sync 地址信息 */
    static void LogStormSyncAddresses();

    /** 演示如何在频道中查找播放服务器 */
    static void FindPlaybackServers(const FString& InChannelName);

    /** 演示如何发起 push 同步 */
    static void PushAssetsToRemote(const FString& InRemoteName, const TArray<FName>& InPackageNames);
};
```

### StormSyncBridgeDemo.cpp

```cpp
#include "StormSyncBridgeDemo.h"

#include "StormSyncAvaBridgeCommon.h"
#include "StormSyncAvaBridgeUtils.h"
#include "Features/IModularFeatures.h"
#include "Interfaces/IAvaMediaSyncProvider.h"

void FStormSyncBridgeDemo::LogStormSyncAddresses()
{
    // 引用插件定义的 User Data 键名常量
    UE_LOG(LogTemp, Log, TEXT("Storm Sync Server Address Key: %s"),
        UE::StormSync::AvaBridgeCommon::StormSyncServerAddressKey);
    UE_LOG(LogTemp, Log, TEXT("Storm Sync Client Address Key: %s"),
        UE::StormSync::AvaBridgeCommon::StormSyncClientAddressKey);
    UE_LOG(LogTemp, Log, TEXT("Storm Sync Discovery Address Key: %s"),
        UE::StormSync::AvaBridgeCommon::StormSyncDiscoveryAddressKey);
}

void FStormSyncBridgeDemo::FindPlaybackServers(const FString& InChannelName)
{
    TArray<FString> ServerNames = FStormSyncAvaBridgeUtils::GetServerNamesForChannel(InChannelName);

    UE_LOG(LogTemp, Log, TEXT("Found %d servers on channel '%s'"),
        ServerNames.Num(), *InChannelName);

    for (const FString& Name : ServerNames)
    {
        UE_LOG(LogTemp, Log, TEXT("  - %s"), *Name);
    }
}

void FStormSyncBridgeDemo::PushAssetsToRemote(const FString& InRemoteName, const TArray<FName>& InPackageNames)
{
    // 通过 Modular Features 获取同步提供者
    IModularFeatures& ModularFeatures = IModularFeatures::Get();
    if (!ModularFeatures.IsModularFeatureAvailable(IAvaMediaSyncProvider::GetModularFeatureName()))
    {
        UE_LOG(LogTemp, Warning, TEXT("No sync provider available"));
        return;
    }

    TArray<IAvaMediaSyncProvider*> Providers = ModularFeatures.GetModularFeatureImplementations<IAvaMediaSyncProvider>(
        IAvaMediaSyncProvider::GetModularFeatureName()
    );

    if (Providers.Num() > 0)
    {
        Providers[0]->PushToRemote(InRemoteName, InPackageNames,
            FOnAvaMediaSyncResponse::CreateLambda([](const FAvaMediaSyncResponse& Response)
            {
                UE_LOG(LogTemp, Log, TEXT("Push completed"));
            })
        );
    }
}
```

## 模块依赖

本插件显式依赖 `Avalanche` 和 `StormSync` 两个插件（通过 .uplugin 的 Plugins 声明）。

| 模块 | 用途 |
|---|---|
| `Avalanche` | Motion Design 核心插件，提供播放服务器/客户端系统和 `IAvaMediaSyncProvider` 接口 |
| `StormSync` | 资产同步传输协议，提供 push/pull/compare 底层能力 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF 新格式 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复错误的查找替换后的二次修正 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退一次有问题的提交 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 适配 CoreDelegates API 变更，修复注册问题 |
| 2025-09-16 | `77ee7eae` | Motion Design: removed beta tag from motion design plugins. | 移除 Motion Design 系列插件的 Beta 标签 |

### 维护评价

**状态：活跃维护中**

- 插件创建于 2025 年 5 月，至今约 1 年，是 Motion Design 系列中的较新成员
- 最近一次实质性代码更新在 2026 年 4 月（日志宏迁移），表明仍在跟随引擎更新
- 2026 年 2 月有多次 API 适配修复（CoreDelegates 变更），说明与引擎核心保持同步
- 2025 年 9 月移除了 Beta 标签，表明已进入稳定状态
- 作为 Motion Design 工作流的关键桥接组件，预期会持续维护
- **Runtime 模块排除了 Server 目标**（TargetDenyList: Server），说明此功能仅用于客户端/编辑器场景

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSyncAvalancheBridge)
- [Avalanche 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [StormSync 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync)