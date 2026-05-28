# Concert - Main

> Allow collaborative multi-users sessions in the Editor

| 属性 | 值 |
|---|---|
| 中文名 | 协奏主框架 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Concert` (UncookedOnly), `ConcertClient` (UncookedOnly), `ConcertServer` (UncookedOnly), `ConcertTransport` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertMain) | |

## 用途

ConcertMain 是虚幻引擎多人编辑器协作（Multi-User Editing）功能的底层核心框架。它并非提供直接的用户界面或功能，而是为上层的 Multi-User Editing 插件提供基础通信、会话管理、数据同步和连接控制能力。该插件默认禁用且隐藏，主要服务于 `UnrealMultiUserServer` 等特定服务器程序和编辑器内部模块。

## 使用场景

- 你的团队正在开发一个大型项目，需要多名开发者同时在同一个编辑器会话中协作，实时看到彼此的操作。
- 你需要为自定义的、受控的多人编辑器协作环境（如内部管线）搭建底层通信基础。
- 你正在开发一个类似 LiveLinkHub 或 CrashReportClient 的特殊工具，并需要其接入多人会话管理。

## 蓝图用法

该插件主要为底层C++框架，不直接向蓝图暴露编辑器会话或项目蓝图的节点。其功能由上层插件（如 Multi-User Editing）封装后提供给用户使用。

## C++ 用法

### 头文件引入

```cpp
#include "ConcertClient.h"
#include "ConcertServer.h"
#include "ConcertTransport.h"
```

### 基本用法

主要用法是作为基础设施，被其他模块依赖，以建立和管理多人会话。例如，创建一个客户端连接到服务器会话。

（此处展示的是框架典型交互模式，非独立可运行示例）

### 进阶用法

框架支持自定义消息类型和同步逻辑。开发者可以基于 `ConcertTransport` 模块的消息系统，扩展出特定领域（如资产同步、属性复制）的协作功能。

## Demo 示例

由于 ConcertMain 是一个大型基础设施框架，其“最小示例”通常是创建并连接一个会话。以下是一个概念性的客户端连接示例。

**ConcertDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FConcertDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    // 客户端连接对象
    TSharedPtr<class IConcertClient> ConcertClient;
};
```

**ConcertDemo.cpp**
```cpp
#include "ConcertDemo.h"
#include "ConcertClient.h"

void FConcertDemoModule::StartupModule()
{
    // 创建一个客户端实例
    ConcertClient = IConcertClient::CreateInstance();
    if (ConcertClient.IsValid())
    {
        // 配置服务器连接信息
        FConcertClientConnectionSettings ConnectionSettings;
        ConnectionSettings.ServerEndpoint = TEXT("127.0.0.1:6666");
        ConnectionSettings.SessionName = TEXT("DemoSession");

        // 启动连接过程
        ConcertClient->Connect(ConnectionSettings);
    }
}

void FConcertDemoModule::ShutdownModule()
{
    if (ConcertClient.IsValid())
    {
        ConcertClient->Disconnect();
        ConcertClient.Reset();
    }
}

IMPLEMENT_MODULE(FConcertDemoModule, ConcertDemo)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Sockets` | 提供底层网络套接字能力 |
| `Networking` | 提供高级网络功能和序列化 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移至新的UE_LOGF宏。 |
| 2026-04-02 | `5cc4482f` | Add descriptions to trace channels and a few other places. | 为追踪通道及其他位置添加描述信息。 |
| 2026-03-10 | `a69ab07d` | [IsSavingPackage] | 相关于包保存状态的功能或修复。 |
| 2025-12-10 | `11a770db` | Specify FConcertSessionChallengeData::ChallengeKey should be ignored when running member initializat... | 指定在成员初始化时应忽略挑战密钥。 |
| 2025-12-08 | `ce8c0205` | Implements a file sharing system that can be used with Multi-user. FConcertCloudSharingService will ... | 实现了一个可与多人协作配合的文件共享系统。 |

### 维护评价

ConcertMain 插件创建于 2019 年初，是 Epic Games 为多人编辑器协作开发的核心底层框架。虽然它默认禁用且标记为实验性（Beta），但从 Git 提交历史看，它仍在持续维护中，最近一次更新在一个月前。其更新内容主要是维护性改进（如日志宏迁移）、功能增强（添加描述、文件共享）和内部逻辑调整。作为多人编辑器技术栈的基础，它不太可能被废弃，但通常不会作为独立功能向普通开发者开放。**推荐**有底层多人协作定制需求的开发者或团队使用，普通项目编辑器协作请直接使用官方的 Multi-User Editing 插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertMain)