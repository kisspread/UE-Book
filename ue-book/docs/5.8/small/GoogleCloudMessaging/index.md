# Google Cloud Messaging

> Support for remote notifications using Google Cloud Messaging

| 属性 | 值 |
|---|---|
| 中文名 | GCM推送 |
| 分类 | Online Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GoogleCloudMessaging` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-02-10 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GoogleCloudMessaging) | |

## 用途

该插件是 Unreal Engine 在 Android 平台上对 Google Cloud Messaging (GCM) 服务的封装。GCM 是一种允许服务器向安装了特定应用的 Android 设备发送数据消息的服务。这个插件为 UE 项目提供了接入 GCM 推送通知的能力，常用于实现后台消息推送、服务器事件提醒等功能。

**注意**: GCM 已被 Google 弃用，官方推荐使用其继任者 Firebase Cloud Messaging (FCM)。此插件主要适用于需要维护旧版 GCM 集成或研究其历史实现的项目。

## 使用场景

- 你需要为 Android 游戏实现服务器推送通知功能。
- 你正在维护一个使用旧版 GCM 服务的 Android 游戏项目。

## 蓝图用法

根据提供的头文件分析，该插件主要暴露的是模块接口，**没有提供任何 `BlueprintCallable` 的函数或 `BlueprintReadWrite` 的属性**。所有功能均需通过 C++ 代码访问。

## C++ 用法

### 头文件引入

```cpp
#include "GoogleCloudMessaging.h"
```

### 基本用法

该插件提供了一个模块接口 `IGoogleCloudMessagingModuleInterface`，主要用于管理模块的生命周期和访问。

```cpp
// 检查 GoogleCloudMessaging 模块是否可用
if (IGoogleCloudMessagingModuleInterface::IsAvailable())
{
    // 获取模块实例
    IGoogleCloudMessagingModuleInterface& GCMModule = IGoogleCloudMessagingModuleInterface::Get();
    
    // 在这里可以使用 GCMModule 提供的任何未来可能添加的功能
}
```

**来源文件**: `Engine/Plugins/Runtime/GoogleCloudMessaging/Source/GoogleCloudMessaging/Public/GoogleCloudMessaging.h`

## Demo 示例

由于该插件没有暴露具体的业务功能（如注册设备、发送消息），仅提供模块框架，以下是一个最基础的、展示如何检查和访问该模块的示例。

**MyGCMGameMode.h**
```cpp
// MyGCMGameMode.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyGCMGameMode.generated.h"

UCLASS()
class AMyGCMGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	virtual void StartPlay() override;
};
```

**MyGCMGameMode.cpp**
```cpp
// MyGCMGameMode.cpp
#include "MyGCMGameMode.h"
#include "GoogleCloudMessaging.h" // 引入插件头文件
#include "Kismet/GameplayStatics.h"

void AMyGCMGameMode::StartPlay()
{
	Super::StartPlay();

#if PLATFORM_ANDROID
	if (IGoogleCloudMessagingModuleInterface::IsAvailable())
	{
		IGoogleCloudMessagingModuleInterface& GCMModule = IGoogleCloudMessagingModuleInterface::Get();
		UE_LOG(LogTemp, Log, TEXT("Google Cloud Messaging module is loaded and available."));
		// 在实际项目中，这里会初始化 GCM 并注册设备以接收通知。
	}
	else
	{
		UE_LOG(LogTemp, Warning, TEXT("Google Cloud Messaging module is not available."));
	}
#else
	UE_LOG(LogTemp, Log, TEXT("Google Cloud Messaging is only available on Android."));
#endif
}
```

## 模块依赖

根据 `GoogleCloudMessaging.Build.cs` 文件，该插件依赖于 `EditorFramework` 和 `UnrealEd`。**这是一个不寻常的配置**，因为该插件被定义为 `Runtime` 类型，理论上不应依赖编辑器模块。这可能是一个历史遗留问题或构建配置错误。在实际项目中，如果你的模块需要使用此插件，可能需要添加这些依赖，但这会增加不必要的编辑器代码到你的运行时构建中。

| 模块 | 用途 |
|---|---|
| `EditorFramework` | （疑为错误依赖）编辑器框架 |
| `UnrealEd` | （疑为错误依赖）虚幻编辑器核心 |

**建议**: 使用此插件时请仔细评估其依赖项，或考虑直接在 Android 项目中通过 JNI 集成更新的 Firebase Cloud Messaging。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至 `UE_LOGF`。 |
| 2023-12-18 | `13ed363e` | Fix up more references to GameActivity._activity | 修复了对 `GameActivity._activity` 的更多引用。 |
| 2023-12-15 | `3dcdaa23` | Fix usage of _activity errors | 修复了 `_activity` 的使用错误。 |
| 2023-04-11 | `c3a3d4f2` | Fix up support for Google Play Services (remove CVE-2022-2390 issue) | 修复了对 Google Play Services 的支持（移除 CVE-2022-2390 漏洞问题）。 |
| 2022-11-22 | `333817f8` | Fix missing flag on PendingIntent for Target SDK 31+ | 为面向 Android API 31+ 的 `PendingIntent` 修复了缺失的标志。 |

### 维护评价

该插件创建于 **2017 年**，最初用于支持 Android 平台的 GCM 服务。近期提交显示它**仍在被维护**，主要进行 Android 平台兼容性修复、安全漏洞修补和构建系统更新（如 UE_LOG 迁移）。然而，由于其底层依赖的 Google Cloud Messaging 服务已被 Google 弃用，该插件的功能已过时。Epic 保持其代码可用性主要是为了旧版项目的兼容性。

**综合评价**:
- **维护状态**: 活跃（有近期维护性提交）。
- **推荐度**: **不推荐用于新项目**。新项目应使用更现代的推送解决方案（如 Firebase Cloud Messaging）。对于需要维护的旧项目，此插件仍可工作，但需注意其模块依赖的异常之处。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GoogleCloudMessaging)
- [官方文档](https://developers.google.com/cloud-messaging)（已废弃，存档参考）