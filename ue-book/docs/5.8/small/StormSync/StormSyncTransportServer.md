# Storm Sync Transport Server

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 中文名 | 风暴同步传输服务器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（资产和内容） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

`StormSyncTransportServer` 模块是 Storm Sync 插件中负责**网络服务端**的核心组件。它解决了在多个 UE 实例（如设计师工作站、渲染农场节点）之间同步、拉取和推送资产及其依赖关系的网络通信问题。其存在是为了在 Motion Design 等协作工作流中，提供一个自动化的资产同步中心，确保所有参与者使用一致的资产版本。

具体功能包括：
- **服务发现**：通过 Message Bus 自动发现网络中的其他 Storm Sync 客户端和服务器。
- **TCP 数据传输**：创建 TCP 服务器，直接接收来自客户端的序列化资产数据包（spak）。
- **连接管理**：使用心跳机制维护已连接设备的状态，自动清理断开的连接。
- **同步请求处理**：接收并处理来自客户端的资产同步请求，计算差异并启动数据传输。

## 使用场景

- **多人协作的 Motion Design 项目**：当你在编辑器 A 上修改了资产，需要实时将修改同步到运行着渲染引擎的编辑器 B 上时。
- **远程资产部署**：需要将本地的资产包一键推送到渲染农场的指定节点时。
- **构建自动化流水线**：在持续集成/持续部署（CI/CD）流程中，自动化同步构建所需的资产。
- **现场虚拟制作（Virtual Production）**：在拍摄现场，需要快速将预处理的资产同步到现场的 LED 墙控制服务器上。

## 蓝图用法

根据提供的源码头文件分析，`StormSyncTransportServer` 模块主要通过 C++ 和控制台命令进行控制，其公开接口 `IStormSyncTransportServerModule` 中没有直接暴露给蓝图的 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。因此，蓝图用法主要体现在通过 `IStormSyncTransportServerModule` 的 C++ 接口间接控制，或在编辑器 UI 中通过插件提供的控制台命令触发。

### 核心节点（C++ 接口映射）

由于是纯 C++ 模块，无直接蓝图节点。其功能可通过控制台命令访问。

### 使用示例（控制台命令）

在编辑器控制台中输入以下命令：
- `StormSync.Server.Start [EndpointName]`：启动传输服务器。
- `StormSync.Server.Stop`：停止传输服务器。
- `StormSync.Server.Status`：查询服务器状态。

## C++ 用法

### 头文件引入

```cpp
#include "IStormSyncTransportServerModule.h"
```

### 基本用法

获取模块实例并启动服务器。

```cpp
// 检查模块是否可用
if (IStormSyncTransportServerModule::IsAvailable())
{
    // 获取模块接口引用
    IStormSyncTransportServerModule& ServerModule = IStormSyncTransportServerModule::Get();
    
    // 启动服务发现管理器（客户端和服务器互相看见的前提）
    ServerModule.StartDiscoveryManager();
    
    // 启动服务器端点，开始监听网络同步请求
    ServerModule.StartServerEndpoint(TEXT("MyProductionServer"));
    
    // 检查服务器是否正在运行
    bool bIsRunning = ServerModule.IsRunning();
    UE_LOG(LogTemp, Log, TEXT("StormSync Server Running: %s"), bIsRunning ? TEXT("Yes") : TEXT("No"));
}
```

### 进阶用法

查询详细的服务器状态，包括地址信息。

```cpp
if (IStormSyncTransportServerModule::IsAvailable())
{
    IStormSyncTransportServerModule& ServerModule = IStormSyncTransportServerModule::Get();
    
    FText StatusText;
    bool bIsRunning = ServerModule.GetServerStatus(StatusText);
    
    if (bIsRunning)
    {
        // 获取服务器 Message Bus 地址
        FString ServerEndpointId = ServerModule.GetServerEndpointMessageAddressId();
        // 获取发现管理器地址
        FString DiscoveryManagerId = ServerModule.GetDiscoveryManagerMessageAddressId();
        
        UE_LOG(LogTemp, Log, TEXT("Server Status: %s\nServer Message Address: %s\nDiscovery Address: %s"),
            *StatusText.ToString(),
            *ServerEndpointId,
            *DiscoveryManagerId);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Server Status: %s"), *StatusText.ToString());
    }
}
```

## Demo 示例

一个展示如何初始化并启动 Storm Sync 传输服务器的最小示例。

**MyStormSyncServer.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyStormSyncServer.generated.h"

class IStormSyncTransportServerModule;

UCLASS()
class AMyStormSyncServer : public AActor
{
    GENERATED_BODY()

public:
    AMyStormSyncServer();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    /** 模块接口的引用，用于控制服务器 */
    IStormSyncTransportServerModule* ServerModule;
};
```

**MyStormSyncServer.cpp**
```cpp
#include "MyStormSyncServer.h"
#include "IStormSyncTransportServerModule.h"

AMyStormSyncServer::AMyStormSyncServer()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyStormSyncServer::BeginPlay()
{
    Super::BeginPlay();

    if (IStormSyncTransportServerModule::IsAvailable())
    {
        ServerModule = &IStormSyncTransportServerModule::Get();
        // 启动服务发现，以便能被其他客户端找到
        ServerModule->StartDiscoveryManager();
        // 启动服务器，监听传入的同步请求
        ServerModule->StartServerEndpoint(TEXT("GameServer"));
        
        UE_LOG(LogTemp, Log, TEXT("StormSync Transport Server has been started."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("StormSyncTransportServer module is not available."));
    }
}

void AMyStormSyncServer::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 模块通常由插件系统管理其生命周期，此处无需手动关闭。
    // 服务器的停止通常由插件关闭或控制台命令触发。
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

从 `StormSyncTransportServer.Build.cs` 分析，该模块没有特殊的外部依赖。它依赖于引擎核心模块以及 Storm Sync 插件内的其他模块（如 `StormSyncTransportCore`）来实现其功能。对于使用者而言，无需添加额外的依赖。

| 模块 | 用途 |
|---|---|
| `无特殊依赖（仅标准 Core/Engine/Slate 等）` | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c830b630` | Storm Sync: fixed vulnerability where a malicious actor can make an spak containing package names/pa | 修复了资产包中可能包含恶意包名路径的安全漏洞。 |
| 2026-05-12 | `3e9d09b7` | Motion Design: fixed storm sync export wizard UI creating a large number of nested folders when chan | 修复了在修改导出路径时，向导UI会创建大量嵌套文件夹的UI问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了32位格式说明符与64位参数不匹配的潜在问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的UE_LOG宏迁移到新的UE_LOGF宏。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 继续修复之前的查找替换错误。 |

### 维护评价

**活跃维护**。该插件创建于 2025 年 5 月，是一个相对较新的功能。从 git 历史看，近期（2026 年内）有多次更新，涵盖了安全漏洞修复、UI 问题修复、代码规范升级和持续错误修正，表明该插件正在被积极使用和维护。

- **年龄**：约 1 年，属于新插件。
- **更新频率**：最近几个月内有多次实质性提交。
- **维护活跃度**：非常活跃。
- **已知限制**：作为服务端模块，其网络和线程模型（基于 `FRunnable`）是成熟的，但需要确保部署环境的网络配置正确。
- **推荐使用**：**是**。对于需要实现资产自动同步的虚拟制片或 Motion Design 工作流，该插件是核心推荐组件，并且正处于活跃的改进和 bug 修复阶段。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync)
- [官方文档]()（暂无）
- [测试用例]()（插件源码目录内未提供标准测试文件，相关测试可能在 `Engine/Tests/` 或通过 `StormSyncTests` 模块提供）