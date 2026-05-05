# Network Service Discovery

> Cross-platform mDNS/DNS-SD service discovery using native platform APIs (NSNetServiceBrowser on Apple, NsdManager on Android, native DNS-SD via dnsapi on Windows)

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NetworkServiceDiscovery` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-09 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NetworkServiceDiscovery) | |

## 用途

这个插件提供跨平台的 **mDNS/DNS-SD 局域网服务发现**能力，解决的核心问题是：**在同一局域网内，让设备之间无需手动输入 IP 地址即可自动发现彼此**。

典型场景是 UE 的 RemoteSession 工作流——编辑器（Windows/Mac）作为服务端广播自己的存在，移动端 App（iOS/Android）作为客户端自动发现并连接编辑器。插件封装了三个平台的原生 API：

- **Windows**：动态加载 `dnsapi.dll`（Windows 10 1803+），使用原生 DNS-SD API
- **Apple (iOS/macOS)**：使用 `NSNetServiceBrowser` / `NSNetService`
- **Android**：通过 JNI 调用 `NsdManager`

不支持的平台会回退到 Null 实现（所有操作静默失败并输出一次警告）。

## 使用场景

- 你在开发 RemoteSession / 多设备联调工具，需要编辑器自动广播给移动端 → 用 NetworkServiceDiscovery
- 你需要在局域网内让 UE 应用自动发现自定义服务（如自定义游戏服务器列表）→ 注册自定义 `_yourservice._tcp.` 类型
- 你需要跨平台统一的服务注册/发现 API，不想自己封装各平台差异 → 用此插件

## 蓝图用法

此插件**没有暴露任何蓝图 API**。所有接口均为纯 C++ `IModuleInterface` 形式，不包含 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。需要在 C++ 代码中使用。

## C++ 用法

### 头文件引入

```cpp
#include "INetworkServiceDiscovery.h"
#include "NetworkServiceDiscoveryTypes.h"
```

### 基本用法 — 服务注册（Host 端）

在编辑器或服务端进程中注册一个 mDNS 服务，让局域网内的客户端可以发现你：

```cpp
// 获取模块实例
INetworkServiceDiscoveryModule* DiscoveryModule = INetworkServiceDiscoveryModule::Get();
if (!DiscoveryModule)
{
    UE_LOG(LogTemp, Error, TEXT("NetworkServiceDiscovery module not loaded"));
    return;
}

// 监听注册成功回调
DiscoveryModule->OnServiceRegistered().AddLambda([](const FNetworkServiceInfo& Service)
{
    UE_LOG(LogTemp, Log, TEXT("Service registered: %s at %s:%d"),
        *Service.ServiceName, *Service.Address, Service.Port);
});

// 监听错误回调
DiscoveryModule->OnDiscoveryError().AddLambda([](const FString& ErrorMessage)
{
    UE_LOG(LogTemp, Error, TEXT("Discovery error: %s"), *ErrorMessage);
});

// 注册服务：名称、类型、端口、TXT 记录
TMap<FString, FString> TxtData;
TxtData.Add(TEXT("AppName"), TEXT("MyProject"));
TxtData.Add(TEXT("Version"), TEXT("1.0"));

bool bStarted = DiscoveryModule->RegisterService(
    TEXT("MyProject on DESKTOP-ABC"),
    TEXT("_unrealremote._tcp."),
    12345,
    TxtData
);

// 取消注册
DiscoveryModule->UnregisterService(TEXT("MyProject on DESKTOP-ABC"));
// 或取消所有服务
DiscoveryModule->UnregisterService();
```

### 基本用法 — 服务发现（Client 端）

在移动端或客户端进程中浏览局域网内的服务：

```cpp
INetworkServiceDiscoveryModule* DiscoveryModule = INetworkServiceDiscoveryModule::Get();
if (!DiscoveryModule) return;

// 监听服务发现事件
DiscoveryModule->OnServiceFound().AddLambda([](const FNetworkServiceInfo& Service)
{
    UE_LOG(LogTemp, Log, TEXT("Found service: %s (type: %s)"),
        *Service.ServiceName, *Service.ServiceType);
    // 注意：此时 Address/Port 尚未解析，需要调用 ResolveService
});

DiscoveryModule->OnServiceResolved().AddLambda([](const FNetworkServiceInfo& Service)
{
    UE_LOG(LogTemp, Log, TEXT("Resolved: %s -> %s:%d"),
        *Service.ServiceName, *Service.Address, Service.Port);
    // 现在可以使用 Service.Address 和 Service.Port 建立连接
});

DiscoveryModule->OnServiceLost().AddLambda([](const FNetworkServiceInfo& Service)
{
    UE_LOG(LogTemp, Log, TEXT("Lost service: %s"), *Service.ServiceName);
});

// 开始浏览指定类型的服务
DiscoveryModule->StartDiscovery(TEXT("_unrealremote._tcp."));

// 发现服务后，解析其地址
// （通常在 OnServiceFound 回调中对每个发现的服务调用）
// DiscoveryModule->ResolveService(FoundService);

// 停止浏览
DiscoveryModule->StopDiscovery();
```

### 进阶用法 — 查询已发现的服务列表

```cpp
// 获取当前所有已发现的服务（线程安全，内部有锁）
TArray<FNetworkServiceInfo> Services = DiscoveryModule->GetDiscoveredServices();

for (const FNetworkServiceInfo& Service : Services)
{
    if (Service.bIsResolved)
    {
        UE_LOG(LogTemp, Log, TEXT("  %s @ %s:%d"),
            *Service.ServiceName, *Service.Address, Service.Port);

        // 读取 TXT 记录中的元数据
        if (const FString* AppName = Service.TxtRecord.Find(TEXT("AppName")))
        {
            UE_LOG(LogTemp, Log, TEXT("    AppName: %s"), **AppName);
        }
    }
}

// 查询注册状态
bool bAnyRegistered = DiscoveryModule->IsServiceRegistered();  // 任意服务
bool bSpecific = DiscoveryModule->IsServiceRegistered(TEXT("MyProject on DESKTOP-ABC"));

// 查询发现状态
bool bBrowsing = DiscoveryModule->IsDiscovering();
```

## Demo 示例

一个完整的最小示例：在编辑器端注册服务，在客户端发现并连接。

### ServiceHost.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "INetworkServiceDiscovery.h"

class FServiceHost
{
public:
    void StartHosting(int32 Port);
    void StopHosting();

private:
    FDelegateHandle OnRegisteredHandle;
    FDelegateHandle OnErrorHandle;
};
```

### ServiceHost.cpp

```cpp
#include "ServiceHost.h"

void FServiceHost::StartHosting(int32 Port)
{
    INetworkServiceDiscoveryModule* Module = INetworkServiceDiscoveryModule::Get();
    if (!Module) return;

    OnRegisteredHandle = Module->OnServiceRegistered().AddLambda(
        [](const FNetworkServiceInfo& Info)
        {
            UE_LOG(LogTemp, Log, TEXT("Hosting service '%s' on port %d"),
                *Info.ServiceName, Info.Port);
        });

    OnErrorHandle = Module->OnDiscoveryError().AddLambda(
        [](const FString& Error)
        {
            UE_LOG(LogTemp, Error, TEXT("Registration failed: %s"), *Error);
        });

    TMap<FString, FString> TxtRecord;
    TxtRecord.Add(TEXT("Platform"), FPlatformProperties::PlatformName());

    Module->RegisterService(
        FString::Printf(TEXT("%s on %s"), FApp::GetProjectName(), *FPlatformProcess::ComputerName()),
        TEXT("_unrealremote._tcp."),
        Port,
        TxtRecord
    );
}

void FServiceHost::StopHosting()
{
    INetworkServiceDiscoveryModule* Module = INetworkServiceDiscoveryModule::Get();
    if (!Module) return;

    Module->UnregisterService();
    Module->OnServiceRegistered().Remove(OnRegisteredHandle);
    Module->OnDiscoveryError().Remove(OnErrorHandle);
}
```

### ServiceBrowser.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "INetworkServiceDiscovery.h"

class FServiceBrowser
{
public:
    void StartBrowsing();
    void StopBrowsing();

    /** 获取所有已解析的服务地址，可用于建立连接 */
    TArray<FNetworkServiceInfo> GetResolvedEndpoints() const;

private:
    FDelegateHandle OnFoundHandle;
    FDelegateHandle OnResolvedHandle;
    FDelegateHandle OnLostHandle;
};
```

### ServiceBrowser.cpp

```cpp
#include "ServiceBrowser.h"

void FServiceBrowser::StartBrowsing()
{
    INetworkServiceDiscoveryModule* Module = INetworkServiceDiscoveryModule::Get();
    if (!Module) return;

    OnFoundHandle = Module->OnServiceFound().AddLambda(
        [Module](const FNetworkServiceInfo& Service)
        {
            UE_LOG(LogTemp, Log, TEXT("Discovered: %s — resolving..."), *Service.ServiceName);
            Module->ResolveService(Service);
        });

    OnResolvedHandle = Module->OnServiceResolved().AddLambda(
        [](const FNetworkServiceInfo& Service)
        {
            UE_LOG(LogTemp, Log, TEXT("Ready to connect: %s -> %s:%d"),
                *Service.ServiceName, *Service.Address, Service.Port);
        });

    OnLostHandle = Module->OnServiceLost().AddLambda(
        [](const FNetworkServiceInfo& Service)
        {
            UE_LOG(LogTemp, Warning, TEXT("Service gone: %s"), *Service.ServiceName);
        });

    Module->StartDiscovery(TEXT("_unrealremote._tcp."));
}

void FServiceBrowser::StopBrowsing()
{
    INetworkServiceDiscoveryModule* Module = INetworkServiceDiscoveryModule::Get();
    if (!Module) return;

    Module->StopDiscovery();
    Module->OnServiceFound().Remove(OnFoundHandle);
    Module->OnServiceResolved().Remove(OnResolvedHandle);
    Module->OnServiceLost().Remove(OnLostHandle);
}

TArray<FNetworkServiceInfo> FServiceBrowser::GetResolvedEndpoints() const
{
    INetworkServiceDiscoveryModule* Module = INetworkServiceDiscoveryModule::Get();
    if (!Module) return {};

    TArray<FNetworkServiceInfo> Result;
    for (const FNetworkServiceInfo& Info : Module->GetDiscoveredServices())
    {
        if (Info.bIsResolved)
        {
            Result.Add(Info);
        }
    }
    return Result;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Launch` | 模块加载基础设施（极少见的轻量依赖） |

无特殊依赖（仅标准 Core/Engine 等隐式依赖 + Launch）。此插件依赖极少，因为平台原生 API 通过动态加载（Windows）或平台头文件（Apple/Android）直接调用。

## 维护状态

### 近期更新

```
- 2026-04-20 bbd3c956 Change Windows NetworkServiceDiscovery warnings to log when dnsapi.dll imports are not available
- 2026-04-15 e087683c Change NetworkServiceDiscovery warnings on Windows when dnsapi.dll is not available to log
- 2026-04-14 35e60df1 Migrate UE_LOG to UE_LOGF
- 2026-04-13 fb2897b0 IPv6 support for RemoteSession client and server
- 2026-04-09 c24a04d4 Fix NoPCH Compile UnrealGame Android
```

### 维护评价

- **状态**：🆕 全新插件，创建于 2026-04-09，距今不到 1 个月
- **活跃度**：非常活跃，创建后 11 天内有 5 次提交，涵盖编译修复、日志规范化、IPv6 支持等功能性改进
- **实验性标记**：`IsBetaVersion=true` 且 `EnabledByDefault=false`，明确处于实验阶段
- **平台限制**：仅支持 Win64、Mac、iOS、Android，其他平台回退到 Null 实现
- **Windows 限制**：依赖 Windows 10 1803+ 的 `dnsapi.dll`，旧版本 Windows 会静默失败；且 Windows DNS-SD 不提供服务移除通知，插件通过周期性重新浏览来检测服务消失
- **推荐**：如果你在做 RemoteSession 或局域网设备发现相关功能，可以尝试使用，但需注意这是实验性 API，接口可能发生变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NetworkServiceDiscovery)
- 官方文档（无）
- 测试用例（未发现）