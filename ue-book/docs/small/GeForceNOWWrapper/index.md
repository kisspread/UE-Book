# NVidia GeForce NOW Wrapper

> NVidia GeForce NOW Wrapper — 封装 NVIDIA GeForce NOW Runtime SDK，让 UE5 游戏能够与 GeForce NOW 云游戏平台集成。

| 属性 | 值 |
|---|---|
| 分类 | Gameplay Streaming |
| 默认启用 | ❌ `EnabledByDefault: false` |
| 包含内容 | ❌ 无 Content |
| 模块 | `GeForceNOWWrapper` (ClientOnlyNoCommandlet, EarliestPossible) |
| 平台限制 | Win64 only |
| 创建时间 | 2022-08-25 |
| 年龄标签 | 🆕 (约 3.7 年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Nvidia/GeForceNOWWrapper) | |

## 用途

这个 plugin 是 NVIDIA GeForce NOW Runtime SDK（`GfnRuntimeSdk_CAPI.h`）的 UE5 封装层。它解决了以下问题：

1. **云环境检测** — 判断游戏是否运行在 GeForce NOW 的云端服务器上，而非玩家本地机器
2. **流式会话管理** — 启动/停止游戏串流会话
3. **客户端信息获取** — 获取用户客户端的 IP、语言、国家等信息
4. **生命周期通知** — 向 GFN 平台通知应用就绪、退出、暂停等状态变化
5. **虚拟键盘支持** — 通过 Action Zone 机制，让 GFN 客户端知道哪些 UI 区域有文本输入框，从而在用户的流式画面上叠加原生虚拟键盘
6. **URL 转发** — 在云环境中将 URL 打开请求转发到用户本地浏览器

**重要：此 plugin 默认不启用。** 如果你的游戏不打算上架 GeForce NOW 平台，不需要此 plugin。

## 使用场景

- 你的游戏要上架 NVIDIA GeForce NOW 云游戏平台 → 启用此 plugin，调用 SDK 完成平台集成
- 你需要检测游戏是否运行在云端（例如禁用本地文件操作、调整图形设置）→ 使用 `IsRunningInGFN()` / `IsRunningInCloud()`
- 你的游戏在 GFN 上运行时需要支持虚拟键盘输入（文本框）→ 调用 `InitializeActionZoneProcessor()` 自动处理
- 你需要在开发环境中模拟 GFN 运行状态进行测试 → 使用 MockGFN 模式

## 蓝图用法

此 plugin **不暴露任何蓝图节点**。所有 API 均为 C++ 静态/成员函数，没有 `UCLASS`、`UFUNCTION` 或 `UPROPERTY` 标记。这是一个纯 C++ 模块。

## C++ 用法

### 头文件引入

```cpp
#include "GeForceNOWWrapper.h"
```

**注意**：所有代码都被 `#if NV_GEFORCENOW` 预处理宏包裹。该宏由 `GeForceNOWWrapper.Build.cs` 根据以下条件自动定义为 1 或 0：
- 非 Server / Program target
- 非 Unknown / Debug configuration
- Win64 平台且非 ARM64

### 基本用法

#### 初始化与云环境检测

```cpp
// SDK 在模块 StartupModule 中自动初始化（EarliestPossible 加载阶段）
// 你也可以手动检查初始化状态
if (GeForceNOWWrapper::IsSdkInitialized())
{
    // SDK 已加载并初始化
}

// 检测是否在 GFN 环境中运行（包括 Mock 模式）
if (GeForceNOWWrapper::IsRunningInGFN())
{
    // 当前在 GeForce NOW 云环境中
}

// 仅检测真实云环境（不含 Mock）
if (GeForceNOWWrapper::IsRunningInCloud())
{
    // 确认在真实 GFN 云环境中
}

// 安全版本：同时返回安全保证级别
GfnIsRunningInCloudAssurance Assurance;
GfnRuntimeError Err = GeForceNOWWrapper::Get().IsRunningInCloudSecure(Assurance);
```

#### 应用生命周期通知

```cpp
// 通知 GFN 平台应用准备就绪
GeForceNOWWrapper& GFN = GeForceNOWWrapper::Get();

// 设置标题（传入平台应用 ID）
GFN.SetupTitle(TEXT("YourAppId"));

// 通知应用已准备好显示
GFN.NotifyAppReady(true, TEXT("Ready"));

// 退出时通知
GFN.NotifyTitleExited(TEXT("PlatformId"), TEXT("YourAppId"));
```

#### 获取客户端信息

```cpp
GeForceNOWWrapper& GFN = GeForceNOWWrapper::Get();

// 获取客户端 IP
FString ClientIP;
if (GFN.GetClientIpV4(ClientIP) == gfnSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Client IP: %s"), *ClientIP);
}

// 获取客户端语言（格式: "zh-CN"）
FString LanguageCode;
if (GFN.GetClientLanguageCode(LanguageCode) == gfnSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Client Language: %s"), *LanguageCode);
}

// 获取客户端国家代码（ISO 3166-1 Alpha-2）
FString CountryCode;
if (GFN.GetClientCountryCode(CountryCode) == gfnSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Client Country: %s"), *CountryCode);
}

// 获取完整客户端信息结构
GfnClientInfo ClientInfo;
if (GFN.GetClientInfo(ClientInfo) == gfnSuccess)
{
    // 处理客户端信息
}

// 获取会话信息
GfnSessionInfo SessionInfo;
if (GFN.GetSessionInfo(SessionInfo) == gfnSuccess)
{
    // 处理会话信息
}
```

#### 串流控制

```cpp
GeForceNOWWrapper& GFN = GeForceNOWWrapper::Get();

// 同步启动串流
StartStreamInput Input = {};  // 填入串流参数
StartStreamResponse Response;
GfnRuntimeError Err = GFN.StartStream(Input, Response);

// 异步启动串流
GFN.StartStreamAsync(Input, [](StartStreamResponse* Response, void* Context) {
    // 串流启动回调
}, nullptr, 5000 /* timeout ms */);

// 停止串流
GFN.StopStream();
// 或异步停止
GFN.StopStreamAsync([](void* Context) {
    // 停止完成回调
}, nullptr, 5000);
```

#### 注册回调

```cpp
GeForceNOWWrapper& GFN = GeForceNOWWrapper::Get();

// 注册退出回调（GFN 需要退出游戏时调用）
GFN.RegisterExitCallback([](void* Context) {
    // 保存进度并退出
    FGenericPlatformMisc::RequestExit(false);
}, nullptr);

// 注册暂停回调
GFN.RegisterPauseCallback([](void* Context) {
    // 暂停游戏
}, nullptr);

// 注册保存回调（GFN 需要保存用户进度时调用）
GFN.RegisterSaveCallback([](void* Context) {
    // 保存游戏进度
}, nullptr);

// 注册会话初始化回调
GFN.RegisterSessionInitCallback([](void* Context) {
    // 用户已连接到游戏席位
}, nullptr);

// 注册串流状态回调
GFN.RegisterStreamStatusCallback([](StreamStatusCallbackSig, void* Context) {
    // 串流状态变化
}, nullptr);

// 注册安装完成回调
GFN.RegisterInstallCallback([](void* Context) {
    // 安装完成（SetupTitle 之后调用）
}, nullptr);

// 注册客户端信息变化回调
GFN.RegisterClientInfoCallback([](void* Context) {
    // 客户端信息发生变化
}, nullptr);
```

#### URL 打开

```cpp
// 在用户本地浏览器中打开 URL（而非云端浏览器）
int32 ErrorCode;
bool bSuccess = GeForceNOWWrapper::OpenURLOnClient(TEXT("https://example.com"), ErrorCode);
if (!bSuccess)
{
    UE_LOG(LogTemp, Warning, TEXT("Failed to open URL on client, error: %d"), ErrorCode);
}
```

### 进阶用法

#### Action Zone（虚拟键盘集成）

Action Zone 是 GFN 的特殊机制：当游戏有文本输入框时，GFN 需要知道输入框在屏幕上的位置，以便在用户的流式画面上叠加原生虚拟键盘。

```cpp
GeForceNOWWrapper& GFN = GeForceNOWWrapper::Get();

// 初始化 Action Zone 处理器
// 会自动 Hook 到 Slate Widget Tracker，追踪所有标记为 "EditableText" 的控件
if (GFN.InitializeActionZoneProcessor())
{
    UE_LOG(LogTemp, Log, TEXT("GFN Action Zone Processor initialized"));
}

// 关闭时自动清理（在 ShutdownModule 中调用）
```

Action Zone 处理器会自动：
1. 监听 `FSlateWidgetTracker` 中标记为 `EditableText` 的控件注册/注销事件
2. 以 0.1 秒间隔（可调）轮询每个文本输入框的屏幕位置
3. 判断控件是否可交互（通过 `LocateWindowUnderMouse` 检测）
4. 将可交互输入框的矩形区域上报给 GFN SDK（`SetActionZone`）
5. 当输入框不再可交互时清除 Action Zone

#### MockGFN 开发模式

在非 Shipping 构建中，可以通过以下方式模拟 GFN 环境进行本地测试：

```bash
# 方式 1：命令行参数 + 文件
# 启动时添加 -MockGFN 参数，并在工作目录放置 mockgfn.txt 文件
YourGame.exe -MockGFN

# 方式 2：仅创建 mockgfn.txt 文件（需要配合 -MockGFN 参数使用）
```

Mock 模式下：
- `IsRunningMockGFN()` 返回 `true`
- `IsRunningInGFN()` 返回 `true`
- `IsRunningInCloud()` 返回 `true`
- Action Zone 处理器正常工作
- SDK 实际功能调用不会执行（DLL 未加载）

## Demo 示例

### 最小 GFN 集成示例

```cpp
// MyGameInstance.h
#pragma once
#include "Engine/GameInstance.h"
#include "MyGameInstance.generated.h"

UCLASS()
class UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;
    virtual void Shutdown() override;

private:
    bool bIsGFNEnvironment = false;
};
```

```cpp
// MyGameInstance.cpp
#include "MyGameInstance.h"
#include "GeForceNOWWrapper.h"

void UMyGameInstance::Init()
{
    Super::Init();

#if NV_GEFORCENOW
    if (GeForceNOWWrapper::IsRunningInGFN())
    {
        bIsGFNEnvironment = true;

        // 通知 GFN 应用就绪
        GeForceNOWWrapper& GFN = GeForceNOWWrapper::Get();
        GFN.SetupTitle(TEXT("MyGame_Steam_12345"));
        GFN.NotifyAppReady(true, TEXT("Game is ready"));

        // 初始化虚拟键盘支持
        GFN.InitializeActionZoneProcessor();

        // 注册退出回调
        GFN.RegisterExitCallback([](void* Ctx) {
            FGenericPlatformMisc::RequestExit(false);
        }, this);

        // 注册保存回调
        GFN.RegisterSaveCallback([](void* Ctx) {
            UMyGameInstance* GI = static_cast<UMyGameInstance*>(Ctx);
            // 保存游戏进度...
        }, this);

        UE_LOG(LogTemp, Log, TEXT("Running in GeForce NOW cloud"));
    }
#endif
}

void UMyGameInstance::Shutdown()
{
#if NV_GEFORCENOW
    if (bIsGFNEnvironment)
    {
        GeForceNOWWrapper& GFN = GeForceNOWWrapper::Get();
        GFN.NotifyTitleExited(TEXT("Steam"), TEXT("MyGame_Steam_12345"));
    }
#endif

    Super::Shutdown();
}
```

### Build.cs 依赖配置

```csharp
// MyGame.Build.cs
using UnrealBuildTool;

public class MyGame : ModuleRules
{
    public MyGame(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "GeForceNOWWrapper"  // 添加此依赖
        });
    }
}
```

## 模块依赖

从 `GeForceNOWWrapper.Build.cs` 提取。要在你的模块中使用此 plugin，需要在 Build.cs 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `GeForceNOWWrapper` | 本 plugin 模块，提供 `GeForceNOWWrapper` 类 |
| `GeForceNOW` | NVIDIA GFN SDK 的 UE 模块封装（公开依赖，自动传递） |
| `Slate` | UI 框架，Action Zone 处理器使用（公开依赖，自动传递） |

`GeForceNOWWrapper` 自身的私有依赖（无需手动添加）：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `SlateCore` | Slate 核心类型 |

### 第三方库

Plugin 依赖 NVIDIA GeForce NOW SDK：
- 头文件路径：`Engine/Source/ThirdParty/NVIDIA/GeForceNOW/include/`（`GfnRuntimeSdk_CAPI.h`）
- DLL 路径：`Engine/Binaries/ThirdParty/NVIDIA/GeForceNOW/`（`GfnRuntimeSdk.dll`）

### Plugin 依赖

| Plugin | 说明 |
|---|---|
| `CommonUI` | UE 通用 UI 框架 |

### 控制台变量

| CVar | 默认值 | 说明 |
|---|---|---|
| `GFN.ForceProcessGFNWidgetActionZones` | `false` | 强制在非 GFN 环境中也处理 Action Zone（调试用） |
| `GFN.WidgetActionZonesProcessDelay` | `0.1` | Action Zone 处理间隔（秒） |
| `GFN.GFNActionZonesHeightBuffer` | `8` | Action Zone 上下扩展像素数 |

### 日志类别

| 类别 | 说明 |
|---|---|
| `LogGFNWrapper` | GeForceNOWWrapper 主类日志 |
| `LogGeForceNow` | 模块级日志 |
| `LogGFNActionZoneProcessor` | Action Zone 处理器日志 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-07-21 | `2415c7aa` | Fix two types of nodiscard warnings seen when building with Clang 20 | 编译器兼容性修复，适配 Clang 20 |
| 2025-05-27 | `93674ac0` | Streaming - GFN - Enlarge text field action zones vertically | 增大文本输入框的 Action Zone 垂直范围，改善虚拟键盘体验 |
| 2025-05-02 | `33ff2f57` | Streaming - GFN - Refactor mockgfn to use command line | 重构 MockGFN 模式，改为命令行参数触发 |

### 维护评价

- **创建时间**：2022 年 8 月，约 3.7 年历史
- **最近更新**：2025 年 7 月，仍在活跃维护
- **更新频率**：2025 年有 3 次提交，包含功能改进、重构和编译修复
- **维护状态**：🟢 **活跃维护**
- **平台限制**：仅 Win64，仅客户端（非 Server/Program）
- **使用建议**：仅在游戏需要上架 GeForce NOW 平台时启用。此 plugin 默认禁用，不影响普通项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Nvidia/GeForceNOWWrapper)
- [NVIDIA GeForce NOW 开发者文档](https://developer.nvidia.com/geforce-now)
