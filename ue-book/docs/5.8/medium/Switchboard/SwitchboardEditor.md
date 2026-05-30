# Switchboard

> Launcher/Installer for the Switchboard application.

| 属性 | 值 |
|---|---|
| 中文名 | Switchboard启动器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、脚本） |
| 模块 | `SwitchboardCommon` (Runtime), `SwitchboardEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Switchboard) | |

## 用途

Switchboard 是虚幻引擎虚拟制片工作流中的中央控制应用程序，用于管理 nDisplay 集群、Live Link、Media 等设备的连接和同步。此插件 **并非** Switchboard 应用本身，而是一个集成在虚幻编辑器中的**启动器、安装器和配置管理器**。它解决了在编辑器内直接启动 Switchboard、自动生成匹配当前项目的配置文件、以及编译和管理 SwitchboardListener 等一系列便利性工具需求，简化了虚拟制片环境的部署和启动流程。

## 使用场景

- 当你的团队使用 nDisplay 进行多机位渲染或 LED 墙拍摄，需要一个集中控制点来管理所有渲染节点和设备。
- 你希望在虚幻编辑器中一键启动 Switchboard 应用，并自动加载与当前打开项目和关卡相匹配的配置。
- 你需要为当前项目快速生成一个标准的 Switchboard 配置文件，而无需手动编写 JSON。
- 你需要编译或检查 SwitchboardListener（一个常驻后台的服务端程序）的状态。
- 你希望将 Switchboard 或 SwitchboardListener 设置为 Windows 开机自启动。

## 蓝图用法

插件在蓝图中主要通过 `FSwitchboardNewConfigUserOptions` 结构体和项目/编辑器设置类暴露功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSwitchboardProjectSettings` | 获取 Switchboard 项目设置单例，用于配置 OSC 监听器等项目级参数。 | `USwitchboardProjectSettings` |
| `GetSwitchboardEditorSettings` | 获取 Switchboard 编辑器设置单例，用于配置虚拟环境路径、监听器参数等编辑器级参数。 | `USwitchboardEditorSettings` |

### 数据结构（蓝图可用）

| 结构体 | 说明 |
|---|---|
| `FSwitchboardNewConfigUserOptions` | 用于创建新配置的参数集合，包含配置名、nDisplay Actor 引用、设备数量、网络设置等。 |
| `FDisplayClusterRootActorReference` | 封装了一个 `AActor` 的软引用，专门用于在 Switchboard 设置中指定 nDisplay 根 Actor。 |

### 使用示例（蓝图描述）

在蓝图中，你可以使用 `Get Switchboard Project Settings` 节点来修改项目的默认 OSC 监听器资产。为了以编程方式创建新配置，你需要构造一个 `FSwitchboardNewConfigUserOptions` 结构体，填入你想要的参数（如配置名、关联的 nDisplay Actor、编辑器设备数量等）。虽然直接启动 Switchboard 的核心函数 `LaunchSwitchboard` 是 C++ 模块接口，但通过项目设置或编辑器菜单的 UI 入口是更常见的蓝图交互方式。

## C++ 用法

### 头文件引入

```cpp
#include "SwitchboardCommon.h"
#include "SwitchboardEditor.h"
```

### 基本用法

从 `FSwitchboardEditorModule` 的公共接口中调用功能。

```cpp
// 来源: Private/SwitchboardEditorModule.h
#include "SwitchboardEditor.h"

// 1. 启动 Switchboard 应用（无参数）
FSwitchboardEditorModule& SBModule = FSwitchboardEditorModule::Get();
SBModule.LaunchSwitchboard();

// 2. 启动 Switchboard 并传入特定配置文件路径
FString ConfigPath = TEXT("D:/MyProject/Config/Switchboard/MyConfig.json");
SBModule.LaunchSwitchboard(FString::Printf(TEXT("-config \"%s\""), *ConfigPath));

// 3. 启动 SwitchboardListener
SBModule.LaunchListener();
```

### 进阶用法：创建新配置

```cpp
// 来源: Private/SwitchboardTypes.h
#include "SwitchboardTypes.h"
#include "SwitchboardEditor.h"

// 构造创建新配置的选项
FSwitchboardNewConfigUserOptions Options;
Options.ConfigName = TEXT("MyNewVPConfig");
Options.NumEditorDevices = 2; // 启动两个编辑器实例
Options.bUseLocalhost = true; // 设备间使用 localhost 通信
Options.bAutoConnect = true;  // 自动连接监听器

// 设置 nDisplay Actor 引用 (需要获取一个有效的 AActor 指针)
// Options.DCRA.DCRA = MyDisplayClusterRootActor;

// 创建配置文件
FSwitchboardEditorModule& SBModule = FSwitchboardEditorModule::Get();
bool bSuccess = SBModule.CreateNewConfig(Options);

if (bSuccess)
{
    UE_LOG(LogSwitchboardPlugin, Log, TEXT("Switchboard configuration created successfully."));
}
```

### 进阶用法：检查安装状态与运行脚本

```cpp
// 来源: Private/SwitchboardEditorModule.h, Private/SwitchboardScriptInterop.h
#include "SwitchboardEditor.h"
#include "SwitchboardScriptInterop.h"

// 检查 Switchboard 安装状态
FSwitchboardEditorModule& SBModule = FSwitchboardEditorModule::Get();
FSwitchboardEditorModule::ESwitchboardInstallState InstallState = SBModule.GetSwitchboardInstallState();

switch (InstallState)
{
case FSwitchboardEditorModule::ESwitchboardInstallState::Nominal:
    UE_LOG(LogSwitchboardPlugin, Log, TEXT("Switchboard is correctly installed."));
    break;
case FSwitchboardEditorModule::ESwitchboardInstallState::NeedInstallOrRepair:
    UE_LOG(LogSwitchboardPlugin, Warning, TEXT("Switchboard needs installation or repair."));
    // 可以触发安装向导： SSwitchboardSetupWizard::OpenWindow();
    break;
// ... 处理其他状态
}

// 异步验证安装（例如检查Python虚拟环境）
TSharedFuture<FSwitchboardVerifyResult> FutureResult = SBModule.GetVerifyResult(true /*bForceRefresh*/);
FutureResult.Get().OnComplete([](const FSwitchboardVerifyResult& Result)
{
    if (Result.Summary == FSwitchboardVerifyResult::ESummary::Success)
    {
        UE_LOG(LogSwitchboardPlugin, Log, TEXT("Switchboard verification succeeded: %s"), *Result.Log);
    }
    else
    {
        UE_LOG(LogSwitchboardPlugin, Error, TEXT("Switchboard verification failed with code %d: %s"),
               static_cast<int32>(Result.Summary), *Result.Log);
    }
});

// 手动运行一个安装脚本
FString VenvPath = /* 获取虚拟环境路径 */;
TSharedRef<FSwitchboardUtilScript> InstallScript = FSwitchboardUtilScript::RunInstall(VenvPath);
// 脚本在后台运行，可以通过 PollStdoutAndReturnCode() 检查进度
```

## Demo 示例

以下示例演示了如何从 C++ 创建一个新的 Switchboard 配置并启动 Switchboard。

**MySwitchboardController.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MySwitchboardController.generated.h"

UCLASS()
class UMySwitchboardController : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    /** 创建一个包含两个编辑器设备的 Switchboard 配置并启动 */
    UFUNCTION(BlueprintCallable, Category = "VirtualProduction")
    void CreateConfigAndLaunch();

private:
    void OnConfigCreated(bool bSuccess);
};
```

**MySwitchboardController.cpp**
```cpp
#include "MySwitchboardController.h"
#include "SwitchboardEditor.h"
#include "SwitchboardTypes.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"

void UMySwitchboardController::CreateConfigAndLaunch()
{
    // 准备配置选项
    FSwitchboardNewConfigUserOptions Options;
    Options.ConfigName = FString::Printf(TEXT("MyGameVP_%s"), *FGuid::NewGuid().ToString(EGuidFormats::Short).Left(8));
    Options.NumEditorDevices = 2;
    Options.bUseLocalhost = true;
    Options.bAutoConnect = true;

    // 尝试将当前关卡地图路径填入配置（如果 Switchboard 脚本支持）
    if (UWorld* World = GetWorld())
    {
        // Options.Map = World->GetMapName(); // 注意：实际获取有效路径需要更复杂的逻辑
    }

    // 异步创建配置
    FSwitchboardEditorModule& SBModule = FSwitchboardEditorModule::Get();
    // 注意：实际 CreateNewConfig 可能涉及异步文件操作，此处简化为同步示例
    bool bSuccess = SBModule.CreateNewConfig(Options);

    OnConfigCreated(bSuccess);
}

void UMySwitchboardController::OnConfigCreated(bool bSuccess)
{
    if (bSuccess)
    {
        // 配置创建成功，启动 Switchboard
        FSwitchboardEditorModule::Get().LaunchSwitchboard();
        UE_LOG(LogTemp, Display, TEXT("Switchboard launched with new config."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create Switchboard config."));
    }
}
```

## 模块依赖

此插件具有特定的虚拟制片和媒体依赖。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | 用于与 nDisplay 系统交互，获取 `ADisplayClusterRootActor` 的类型信息。 |
| `OSC` | 用于支持项目设置中配置的 OSC 监听器，实现与 Switchboard 的通信。 |
| `MediaProfile` | 用于支持媒体配置文件。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `75168502` | Switchboard - Fix unhandled PermissionError in Save Logs zip cleanup. | 修复了保存日志压缩包清理时未处理的权限错误。 |
| 2026-05-12 | `769529af` | Switchboard: Fix host vs remote platform handling for Linux nodes. | 修复了 Linux 节点与远程主机平台处理的兼容性问题。 |
| 2026-05-12 | `603cb935` | Allow users to specify which plugins are enabled for Live Link Hub on launch. | 允许用户在启动时指定为 Live Link Hub 启用哪些插件。 |
| 2026-04-28 | `7c48f485` | Switchboard - add renamed MediaProfile module classname to MEDIAPROFILE_CLASS_NAMES so Media Profile | 将重命名的 MediaProfile 模块类名添加到列表，以确保 Media Profile 功能正常。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |

### 维护评价

**活跃维护**。该插件仍在 Epic Games 的虚拟制片团队下积极维护和更新。从提交记录看，最近6个月内（2026年）有多次功能性改进和 bug 修复，特别是针对跨平台兼容性（Linux）、错误处理和 Live Link 集成的优化。作为 IsBetaVersion 标记的工具，其功能仍在演进中。对于需要集成 Switchboard 到虚幻编辑器工作流的虚拟制片项目，这是一个官方支持且持续维护的可靠工具，推荐使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Switchboard)