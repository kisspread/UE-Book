# GeForce NOW Wrapper

> NVidia GeForce NOW Wrapper

| 属性 | 值 |
|---|---|
| 中文名 | GeForce NOW包装器 |
| 分类 | Gameplay Streaming |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GeForceNOWWrapper` (ClientOnlyNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2022-08-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Nvidia/GeForceNOWWrapper) | |

## 用途

本插件是 NVIDIA GeForce NOW 云游戏平台（GFN）的官方 Unreal Engine 集成模块。它并非一个用于在 GFN 上**运行**游戏的插件（GFN 的宿主服务器通常会管理游戏进程），而是一个**面向游戏开发者的高级封装层**，允许游戏与 GFN 的运行时环境进行深度交互。

它的核心作用是：
1.  **环境感知**：判断当前游戏实例是否运行在 GFN 的云环境中，以及其安全级别。
2.  **会话生命周期管理**：控制 GFN 上游戏流会话的启动、停止，并接收来自客户端（用户的本地设备）的状态回调。
3.  **客户端信息获取**：查询正在使用 GFN 服务的用户客户端信息，如 IP 地址、语言、国家/地区等。
4.  **云交互功能**：通过“动作区域（Action Zones）”在用户的设备上触发原生功能，例如调出虚拟键盘，实现云游戏中的文本输入。
5.  **深度链接**：安全地处理从客户端传递到云游戏的合作伙伴数据（Partner Data）。

简而言之，它解决了在 GFN 云平台环境下，游戏引擎需要与平台服务进行标准化、深度集成的标准化方案，使开发者无需直接处理底层 SDK 的复杂细节。

## 使用场景

-   你的游戏计划登陆 NVIDIA GeForce NOW 云游戏平台，并需要实现特定的云平台功能。
-   你需要在云游戏会话中管理游戏的就绪、退出、暂停、存档等事件。
-   你希望在云游戏环境中，通过用户的本地设备触发特定交互（例如，在云游戏的文本框上点击后，能弹出用户电脑上的原生键盘）。
-   你需要获取当前云游戏玩家的客户端信息（如地理位置、语言）用于游戏逻辑或统计。

## 蓝图用法

本插件的核心功能主要通过 C++ 的静态单例类 `GeForceNOWWrapper` 暴露，不包含 `UFUNCTION(BlueprintCallable)` 节点。因此，要在蓝图中使用，通常需要通过 C++ 包装自定义蓝图节点。

### 核心节点（C++ 静态方法，需包装）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GeForceNOWWrapper::IsRunningInCloud()` | 判断是否运行在GFN云环境（无需进程提权） | `GeForceNOWWrapper` |
| `GeForceNOWWrapper::IsRunningInGFN()` | 判断是否运行在GFN环境（SDK已初始化） | `GeForceNOWWrapper` |
| `GeForceNOWWrapper::SetupTitle()` | 通知GFN客户端准备启动一个应用程序 | `GeForceNOWWrapper` |
| `GeForceNOWWrapper::NotifyAppReady()` | 通知GFN客户端应用程序已准备好显示 | `GeForceNOWWrapper` |
| `GeForceNOWWrapper::StartStream()` / `StartStreamAsync()` | 请求启动一个流媒体会话（同步/异步） | `GeForceNOWWrapper` |
| `GeForceNOWWrapper::StopStream()` / `StopStreamAsync()` | 请求停止当前流媒体会话（同步/异步） | `GeForceNOWWrapper` |

### 使用示例（蓝图描述）

由于没有原生蓝图节点，典型的使用方式是在 C++ GameInstance 或 Subsystem 中调用这些静态函数，并将结果通过蓝图可调用的自定义函数或事件暴露给蓝图。例如，你可以创建一个 `UGFNIntegrationComponent`，在其中封装“初始化GFN SDK”、“检查云环境”、“启动特定游戏流”等逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "GeForceNOWWrapper.h"
#include "GeForceNOWActionZoneProcessor.h" // 如果需要管理动作区域
```

### 基本用法

1.  **初始化与环境检查**
    ```cpp
    // GameInstance 或类似的地方，在启动时初始化
    void UMyGameInstance::Init()
    {
        Super::Init();
        
        // 初始化GeForce NOW SDK
        GfnRuntimeError InitError = GeForceNOWWrapper::Initialize();
        if (InitError != GfnRuntimeError_Success)
        {
            UE_LOG(LogTemp, Warning, TEXT("GeForceNOW SDK initialization failed: %d"), InitError);
            return;
        }

        // 检查是否运行在云环境中
        if (GeForceNOWWrapper::IsRunningInCloud())
        {
            UE_LOG(LogTemp, Log, TEXT("Running in GeForce NOW cloud environment."));
            
            // 获取客户端信息示例
            FString ClientIP;
            if (GeForceNOWWrapper::Get().GetClientIpV4(ClientIP) == GfnRuntimeError_Success)
            {
                UE_LOG(LogTemp, Log, TEXT("Client IP: %s"), *ClientIP);
            }

            // 启动流会话（需要传入正确的StartStreamInput）
            // StartStreamInput StartInput;
            // ... 配置StartInput ...
            // StartStreamResponse Response;
            // GfnRuntimeError StreamError = GeForceNOWWrapper::Get().StartStream(StartInput, Response);
        }
    }
    
    // 在退出时关闭
    void UMyGameInstance::Shutdown()
    {
        GeForceNOWWrapper::Shutdown();
        Super::Shutdown();
    }
    ```

2.  **注册回调**
    ```cpp
    // 在初始化后，注册需要的回调函数
    void RegisterGFNCallbacks()
    {
        // 注册退出回调：当GFN需要退出游戏时调用
        GeForceNOWWrapper::Get().RegisterExitCallback([](void* Context){
            UE_LOG(LogTemp, Warning, TEXT("GFN requested to exit the game."));
            // 执行退出逻辑，例如调用 UKismetSystemLibrary::QuitGame
        }, nullptr);
        
        // 注册会话初始化回调：当用户连接到游戏座位时调用
        GeForceNOWWrapper::Get().RegisterSessionInitCallback([](const SessionInitData& SessionData, void* Context){
            UE_LOG(LogTemp, Log, TEXT("GFN session initialized. User connected."));
        }, nullptr);
    }
    ```

### 进阶用法

集成动作区域处理器，以支持云游戏中的虚拟键盘输入。
```cpp
#include "GeForceNOWWrapper.h"
#include "GeForceNOWActionZoneProcessor.h"

// 在某个管理器（如WorldSubsystem）中
void UGFNWorldSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    
    if (GeForceNOWWrapper::IsRunningInCloud())
    {
        // 初始化动作区域处理器
        bool bActionZoneSuccess = GeForceNOWWrapper::Get().InitializeActionZoneProcessor();
        if (bActionZoneSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("GFN Action Zone Processor initialized."));
        }
    }
}

void UGFNWorldSubsystem::Deinitialize()
{
    // 处理器会在其内部自动处理，或可以通过GeForceNOWWrapper的Shutdown链式清理。
    Super::Deinitialize();
}
```
*来源参考：`GeForceNOWActionZoneProcessor.h` 中的 `Initialize` 和 `Terminate` 接口。*

## Demo 示例

一个最小的、展示如何初始化和检查环境的示例。

**MyGFNGameInstance.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "MyGFNGameInstance.generated.h"

UCLASS()
class MYGAME_API UMyGFNGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;
    virtual void Shutdown() override;

    UFUNCTION(BlueprintCallable, Category = "GFN")
    bool IsRunningInGFNCloud() const;

    UFUNCTION(BlueprintCallable, Category = "GFN")
    FString GetGFNClientIP() const;
};
```

**MyGFNGameInstance.cpp**
```cpp
#include "MyGFNGameInstance.h"
#include "GeForceNOWWrapper.h"

void UMyGFNGameInstance::Init()
{
    Super::Init();

    // 初始化 GFN SDK
    GfnRuntimeError Error = GeForceNOWWrapper::Initialize();
    if (Error != GfnRuntimeError_Success)
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to initialize GeForceNOW SDK. Error: %d"), static_cast<int32>(Error));
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("GeForceNOW SDK initialized successfully."));
        
        // 示例：注册一个简单的回调
        GeForceNOWWrapper::Get().RegisterExitCallback([](void* Context){
            UE_LOG(LogTemp, Warning, TEXT("Game received exit signal from GFN client."));
            // 在实际应用中，这里会调用退出游戏的逻辑
        }, nullptr);
    }
}

void UMyGFNGameInstance::Shutdown()
{
    // 关闭 GFN SDK
    GeForceNOWWrapper::Shutdown();
    UE_LOG(LogTemp, Log, TEXT("GeForceNOW SDK shutdown."));
    Super::Shutdown();
}

bool UMyGFNGameInstance::IsRunningInGFNCloud() const
{
    // 检查是否运行在云环境
    return GeForceNOWWrapper::IsRunningInCloud();
}

FString UMyGFNGameInstance::GetGFNClientIP() const
{
    FString IP;
    if (GeForceNOWWrapper::IsSdkInitialized())
    {
        GfnRuntimeError Error = GeForceNOWWrapper::Get().GetClientIpV4(IP);
        if (Error != GfnRuntimeError_Success)
        {
            UE_LOG(LogTemp, Warning, TEXT("Failed to get client IP. Error: %d"), static_cast<int32>(Error));
        }
    }
    return IP;
}
```

## 模块依赖

本插件依赖于 GFN 本身的 SDK (`GfnRuntimeSdk_CAPI.h`)，并通过构建系统链接。对于使用此插件的项目，需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `CommonUI` | 用于游戏内UI的跨平台支持，GFN包装器可能与之协同工作以处理云环境下的输入焦点或UI交互。 |

无特殊依赖（仅标准 Core/Engine/Slate 等），但 `GeForceNOWWrapper` 模块的 `Build.cs` 应会包含对 GFN SDK 库的链接指令。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将标准UE_LOG日志宏迁移到新的UE_LOGF格式。 |
| 2025-07-21 | `2415c7aa` | Fix two types of nodiscard warnings seen when building with Clang 20 | 修复了在使用Clang 20编译时出现的两类[[nodiscard]]警告。 |
| 2025-05-27 | `93674ac0` | Streaming - GFN - Enlarge text field action zones vertically | 云游戏流媒体 - GFN - 在垂直方向上放大了文本输入框的动作区域，以改善交互体验。 |
| 2025-05-02 | `33ff2f57` | Streaming - GFN - Refactor mockgfn to use command line | 云游戏流媒体 - GFN - 重构了MockGFN（模拟GFN环境的工具）以使用命令行参数进行配置。 |
| 2025-04-23 | `939cc6e5` | Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv | 使用FortniteClient构建目标来查找并转换所有文件，为方法和静态变量添加了DLL导出声明。 |

### 维护评价

-   **创建时间**：2022年创建，至今约3年。
-   **近期活跃度**：更新一直持续到2026年，最近的更新集中在**维护性修复**（日志迁移、编译警告）和**用户体验改进**（动作区域大小调整）上。这表明插件仍在维护中，并且围绕其核心功能（动作区域）有持续的优化。
-   **功能状态**：从源码和更新日志看，该插件功能完整，专注于与NVIDIA GFN SDK的集成，没有迹象表明它已被废弃。
-   **限制**：它高度依赖NVIDIA的专有SDK (`GfnRuntimeSdk_CAPI.h`)，且`EnabledByDefault=false`，需要开发者明确启用。仅支持`Win64`平台，目标排除`Server`构建，符合云游戏客户端的定位。
-   **推荐**：如果你的游戏计划登陆NVIDIA GeForce NOW平台，并且需要利用云平台的深度集成功能（如原生虚拟键盘、会话管理），那么这个官方插件是推荐使用的。对于不依赖特定GFN云交互功能的游戏，则无需引入。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Nvidia/GeForceNOWWrapper)
-   [官方文档](https://developer.nvidia.com/geforce-now) (NVIDIA GeForce NOW开发者门户，提供SDK和集成指南)