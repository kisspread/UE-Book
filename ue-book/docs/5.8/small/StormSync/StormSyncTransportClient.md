# Storm Sync

> Sync, Pull, Push, asset dependencies.
This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 中文名 | 资产同步传输客户端 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

`StormSyncTransportClient` 是 StormSync 插件的核心网络通信模块，专门负责**客户端侧**的资产同步逻辑。它封装了与远程编辑器实例进行资产依赖同步（Sync）、推送（Push）和拉取（Pull）操作的所有客户端功能。该模块利用 Unreal Engine 的消息总线（MessageBus）进行设备发现和通信协议协商，并通过 TCP 连接进行高速的原始数据（资产包）传输。它是实现团队协作、多设备资产同步的关键组件，尤其服务于 Motion Design 工作流。

## 使用场景

-   你的虚拟制片团队有多台运行 Unreal Editor 的工作站，需要在它们之间快速、可靠地同步大型资产包（如模型、动画、材质等）。
-   你在进行运动设计（Motion Design）项目，需要在本地编辑器和远程渲染农场或其他艺术家工作站之间推送或拉取特定资产及其依赖项。
-   你需要一个自动化的流程，通过命令行或蓝图脚本触发资产同步，而不是手动复制文件。

## 蓝图用法

`StormSyncTransportClient` 模块主要通过 `IStormSyncTransportClientModule` 接口暴露功能。在蓝图中，通常需要先获取该模块的实例。

### 核心节点

由于这是一个底层网络模块，其大部分核心API设计为C++调用。蓝图中可通过调用C++暴露的包装函数或使用模块接口间接访问。主要接口节点如下：

| 节点 | 说明 | 所在类/接口 |
|---|---|---|
| `Get()` (静态函数) | 获取 `IStormSyncTransportClientModule` 的单例实例。 | `IStormSyncTransportClientModule` |
| `StartClientEndpoint` | 启动客户端通信端点，使其能够接收和发送消息。 | `IStormSyncTransportClientModule` |
| `SynchronizePackages` | 广播一个同步请求，通知所有连接的设备同步指定的资产包。 | `IStormSyncTransportClientModule` |
| `PushPackages` | 向指定的远程地址发送推送请求，将本地资产包发送给对方。 | `IStormSyncTransportClientModule` |
| `PullPackages` | 向指定的远程地址发送拉取请求，从对方获取资产包。 | `IStormSyncTransportClientModule` |
| `RequestPackagesStatus` | 向指定的远程地址查询其本地是否存在特定资产包及其状态。 | `IStormSyncTransportClientModule` |

### 使用示例（蓝图描述）

1.  **获取模块实例**：在蓝图中，通过 `Get` 类节点获取 `IStormSyncTransportClientModule` 的引用。
2.  **启动端点**：调用 `StartClientEndpoint` 并传入一个友好的名称（如“Artist_PC1”）来初始化网络通信。
3.  **发现设备**：利用引擎的消息总线功能（需结合其他模块）或通过 `GetClientEndpointMessageAddressId` 获取本机地址，用于配置远程连接。
4.  **执行操作**：调用 `SynchronizePackages`、`PushPackages` 等节点，传入资产包名称列表（`PackageNames`）和包描述符（`PackageDescriptor`）来执行同步。
5.  **处理回调**：对于 `PushPackages` 和 `PullPackages`，可以绑定一个委托（Delegate）来接收操作完成的回调。

## C++ 用法

### 头文件引入

```cpp
#include "IStormSyncTransportClientModule.h"
```

### 基本用法

从模块接口获取实例并启动客户端，然后进行资产包同步操作。

```cpp
// 来源：基于 Public/IStormSyncTransportClientModule.h 和 Private/StormSyncTransportClientModule.h 推断的用法
#include "IStormSyncTransportClientModule.h"

void AMySyncManager::InitializeSyncClient()
{
    // 1. 检查模块是否可用
    if (IStormSyncTransportClientModule::IsAvailable())
    {
        // 2. 获取模块单例
        IStormSyncTransportClientModule& ClientModule = IStormSyncTransportClientModule::Get();

        // 3. 启动客户端端点（通常在应用程序初始化时调用一次）
        ClientModule.StartClientEndpoint(TEXT("MyEditorClient"));

        // 4. 准备资产包名称和描述符
        TArray<FName> PackageNames = {TEXT("/Game/Maps/Level_Main"), TEXT("/Game/Characters/CH_Hero")};
        FStormSyncPackageDescriptor PackageDesc; // 需要填充描述信息，如版本、来源等

        // 5. 广播同步请求
        ClientModule.SynchronizePackages(PackageDesc, PackageNames);
    }
}
```

### 进阶用法

使用 `PushPackages` 向特定设备推送资产，并通过委托处理完成回调。

```cpp
// 来源：基于 Public/IStormSyncTransportClientModule.h 和 Private/StormSyncTransportClientEndpoint.h 推断的用法
#include "IStormSyncTransportClientModule.h"
#include "MessageEndpointBuilder.h"

void AMySyncManager::PushAssetToSpecificHost(const FMessageAddress& RemoteAddress)
{
    if (!IStormSyncTransportClientModule::IsAvailable()) return;

    IStormSyncTransportClientModule& ClientModule = IStormSyncTransportClientModule::Get();

    TArray<FName> PackageNames = {TEXT("/Game/VFX/NS_Explosion")};
    FStormSyncPackageDescriptor PackageDesc;

    // 定义完成回调
    FOnStormSyncPushComplete OnPushComplete;
    OnPushComplete.BindLambda([](const TSharedPtr<FStormSyncTransportPushResponse>& Response)
    {
        if (Response.IsValid() && Response->bSuccess)
        {
            UE_LOG(LogTemp, Display, TEXT("资产推送成功！"));
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("资产推送失败: %s"), *Response->ErrorText.ToString());
        }
    });

    // 发送推送到特定地址
    ClientModule.PushPackages(PackageDesc, PackageNames, RemoteAddress, OnPushComplete);
}

// 获取客户端消息端点的地址（用于被其他设备发现或配置）
FString GetLocalClientAddress()
{
    if (IStormSyncTransportClientModule::IsAvailable())
    {
        return IStormSyncTransportClientModule::Get().GetClientEndpointMessageAddressId();
    }
    return FString();
}
```

## Demo 示例

一个最小化的C++类，展示如何初始化客户端并执行拉取操作。

```cpp
// StormSyncClientDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IStormSyncTransportClientModule.h"
#include "StormSyncClientDemo.generated.h"

UCLASS()
class AStormSyncClientDemo : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    // 发起拉取请求
    UFUNCTION(BlueprintCallable, Category = "StormSync Demo")
    void PullAssetsFromRemote(const FMessageAddress& RemoteAddress, const TArray<FName>& AssetNames);

private:
    // 存储一个远程地址，可通过其他方式（如消息总线发现）获取
    FMessageAddress TargetRemoteAddress;
};
```

```cpp
// StormSyncClientDemo.cpp
#include "StormSyncClientDemo.h"

void AStormSyncClientDemo::BeginPlay()
{
    Super::BeginPlay();

    // 确保模块已加载并启动客户端
    if (IStormSyncTransportClientModule::IsAvailable())
    {
        IStormSyncTransportClientModule::Get().StartClientEndpoint(TEXT("DemoClient"));
    }
}

void AStormSyncClientDemo::PullAssetsFromRemote(const FMessageAddress& RemoteAddress, const TArray<FName>& AssetNames)
{
    if (!IStormSyncTransportClientModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("StormSync Transport Client 模块不可用。"));
        return;
    }

    IStormSyncTransportClientModule& ClientModule = IStormSyncTransportClientModule::Get();

    // 创建一个简单的包描述符
    FStormSyncPackageDescriptor PackageDesc;
    PackageDesc.PackageName = TEXT("DemoPullPackage");
    PackageDesc.Description = TEXT("通过Demo拉取的资产包");

    // 设置拉取完成回调
    FOnStormSyncPullComplete OnPullComplete;
    OnPullComplete.BindLambda([AssetNames](const TSharedPtr<FStormSyncTransportPullResponse>& Response)
    {
        if (Response.IsValid() && Response->bSuccess)
        {
            UE_LOG(LogTemp, Display, TEXT("成功拉取 %d 个资产。"), AssetNames.Num());
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("拉取失败: %s"), Response.IsValid() ? *Response->ErrorText.ToString() : TEXT("未知错误"));
        }
    });

    // 发送拉取请求
    ClientModule.PullPackages(PackageDesc, AssetNames, RemoteAddress, OnPullComplete);
    UE_LOG(LogTemp, Log, TEXT("已发送拉取请求至: %s"), *RemoteAddress.ToString());
}
```

## 模块依赖

`StormSyncTransportClient` 模块依赖于消息总线系统和网络传输核心。以下是其独特的依赖模块（已在 `StormSyncTransportClient.Build.cs` 中配置）。

| 模块 | 用途 |
|---|---|
| `Messaging` | Unreal Engine 的消息总线系统，用于实现编辑器实例间的设备发现和消息通信。 |
| `StormSyncTransportCore` | 定义了 StormSync 网络传输所使用的核心数据结构、消息类型（如 `FStormSyncTransportPushRequest`）和协议。 |
| `Sockets` | 提供底层的网络套接字（Socket）功能，用于建立 TCP 连接进行数据传输。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c830b630` | Storm Sync: fixed vulnerability where a malicious actor can make an spak containing package names/pa | 修复了安全漏洞，防止恶意包名和路径注入。 |
| 2026-05-12 | `3e9d09b7` | Motion Design: fixed storm sync export wizard UI creating a large number of nested folders when chan | 修复了导出向导UI在特定情况下错误创建大量嵌套文件夹的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了日志输出中64位变量使用32位格式化说明符的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版日志宏 UE_LOG 迁移到新版 UE_LOGF。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修正了前次提交中错误的查找替换操作。 |

### 维护评价

-   **活跃维护**：`StormSyncTransportClient` 是一个相对较新的模块（创建于2025年5月），且在2026年5月仍有**功能性更新和安全修复**提交。这表明它处于活跃维护状态，是 Epic Games 虚拟制片工作流的重要组成部分。
-   **注意事项**：作为一个网络模块，其稳定性和安全性至关重要。近期提交中包含安全漏洞修复，建议用户及时更新到包含这些修复的引擎版本。
-   **推荐使用**：对于正在使用或计划使用 Motion Design 工作流的团队，**推荐使用**此插件。它提供了开箱即用的、基于消息总线和TCP的资产同步解决方案，能显著提升团队协作效率。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTransportClient)
-   [官方文档]() (暂无)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTests) (测试用例位于 `StormSyncTests` 模块)