# Online Subsystem Tencent

> Access to Tencent platform

| 属性 | 值 |
|---|---|
| 中文名 | 腾讯在线子系统 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `OnlineSubsystemTencent` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-04-30 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemTencent) | |

## 用途

`OnlineSubsystemTencent` 是虚幻引擎提供的官方插件，用于将游戏与腾讯的 **WeGame 平台**（底层基于腾讯的 **Rail SDK**）进行深度集成。它实现了引擎标准的 `IOnlineSubsystem` 接口，为面向中国市场的游戏（或使用 WeGame 平台的游戏）提供了完整的在线功能支持，包括身份认证、会话管理、好友系统、在线状态、外部UI、用户信息查询以及商店购买等。

该插件的存在解决了开发者需要对接腾讯平台进行在线服务的问题，确保了游戏能够复用引擎标准的在线子系统架构，从而以一种平台无关的方式调用腾讯平台的功能。

## 使用场景

- 你计划在中国市场发布游戏，并选择在 **WeGame** 平台上架。
- 你的游戏需要集成腾讯平台的社交功能，如好友列表、在线状态、邀请和聊天。
- 你的游戏需要使用腾讯平台的商店进行应用内购买（IAP）。
- 你的游戏需要遵守中国的防沉迷（AAS）规定，集成相关的时间管理和对话框提示。
- 你希望利用 WeGame 平台的会话管理功能来创建和管理游戏房间。

## 蓝图用法

该插件的核心功能通过引擎通用的 `Online Subsystem` 接口暴露，而非提供独立的蓝图节点。具体功能的调用取决于你正在使用的接口（会话、好友、身份等）。

### 核心节点（通过引擎通用在线子系统节点访问）

| 节点 | 说明 | 所在类（由插件实现） |
|---|---|---|
| `Get Session Interface` | 获取腾讯平台会话接口，用于创建、查找、加入游戏房间。 | `FOnlineSessionTencentRail` |
| `Get Friends Interface` | 获取腾讯平台好友接口，用于读取好友列表、发送邀请。 | `FOnlineFriendsTencent` |
| `Get Identity Interface` | 获取腾讯平台身份接口，用于用户登录、获取账号信息。 | `FOnlineIdentityTencent` |
| `Get Presence Interface` | 获取腾讯平台在线状态接口，用于设置和查询用户在线状态。 | `FOnlinePresenceTencent` |
| `Get External UI Interface` | 获取腾讯平台外部UI接口，用于显示登录、好友、成就等原生界面。 | `FOnlineExternalUITencent` |
| `Get Purchase Interface` | 获取腾讯平台购买接口，用于查询收据、发起结账流程。 | `FOnlinePurchaseTencent` |
| `Get Store Interface` | 获取腾讯平台商店接口，用于查询可购买的商品。 | `FOnlineStoreTencent` |
| `Get User Interface` | 获取腾讯平台用户接口，用于查询用户详细信息。 | `FOnlineUserTencent` |
| `Get Message Sanitizer Interface` | 获取消息过滤接口，用于处理敏感词。 | `FMessageSanitizerTencent` |

### 使用示例（蓝图描述）

1.  **用户登录**：
    *   拖入 `Get Online Subsystem` 节点，从返回值拖出 `Get Identity Interface`。
    *   从 `Get Identity Interface` 节点拖出 `Login` 节点。
    *   将 `Local User Num` 设为 `0`（代表第一个本地玩家）。
    *   `Account Credentials` 通常留空或提供空结构体，因为腾讯平台登录由 Rail SDK 控制。

2.  **监听防沉迷对话框（AAS）**：
    *   在 `FOnlineSubsystemTencent` 的实例上（通常通过 C++ 获取），绑定 `OnAASDialog` 委托。
    *   当平台需要弹出防沉迷提示时，此委托将被触发，传递标题、正文和按钮文本。你的游戏 UI 需要据此显示对话框。

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystemTencent.h"
// 如果需要访问具体接口类型，可能还需要包含其头文件，例如：
#include "OnlineIdentityTencent.h"
```

### 基本用法

获取腾讯在线子系统实例并进行登录。

```cpp
// 获取默认的在线子系统实例（在项目配置指定为 Tencent 时，即为本插件实例）
IOnlineSubsystem* OnlineSub = Online::GetSubsystem(GetWorld());
if (OnlineSub)
{
    // 尝试获取身份接口
    IOnlineIdentityPtr IdentityInt = OnlineSub->GetIdentityInterface();
    if (IdentityInt.IsValid())
    {
        // 发起登录流程
        FOnlineAccountCredentials Credentials;
        // 对于腾讯/Rail SDK，通常凭证为空，SDK内部处理Steam/WeGame用户的登录
        IdentityInt->Login(0, Credentials);
    }
}
```

### 进阶用法

监听并处理腾讯平台的防沉迷（AAS）对话框事件。

```cpp
// 在你的游戏模块或游戏实例中
void UMyGameInstance::Init()
{
    Super::Init();

    IOnlineSubsystem* OnlineSub = Online::GetSubsystem(GetWorld());
    if (OnlineSub && OnlineSub->GetSubsystemName() == TENCENT_SUBSYSTEM)
    {
        // 转换为腾讯子系统以访问特定功能
        FOnlineSubsystemTencent* TencentSub = static_cast<FOnlineSubsystemTencent*>(OnlineSub);
        if (TencentSub)
        {
            // 绑定防沉迷对话框事件
            TencentSub->AddOnAASDialogDelegate_Handle(
                FOnAASDialogDelegate::CreateUObject(this, &UMyGameInstance::OnAASDialogReceived)
            );
        }
    }
}

void UMyGameInstance::OnAASDialogReceived(const FString& Title, const FString& Text, const FString& ButtonText)
{
    UE_LOG(LogOnline, Log, TEXT("AAS Dialog: %s - %s [Button: %s]"), *Title, *Text, *ButtonText);
    // 在此处打开你的UI来显示此对话框
    // 例如: ShowAASDialogWidget(Title, Text, ButtonText);
}
```

## Demo 示例

一个最小的 C++ Actor 示例，展示如何获取腾讯子系统并尝试登录。

```cpp
// TencentLoginActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TencentLoginActor.generated.h"

class IOnlineIdentity;

UCLASS()
class ATencentLoginActor : public AActor
{
	GENERATED_BODY()
	
public:	
	ATencentLoginActor();

protected:
	virtual void BeginPlay() override;

private:
	void TryLogin();
	void OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error);

	FDelegateHandle LoginDelegateHandle;
};
```

```cpp
// TencentLoginActor.cpp
#include "TencentLoginActor.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemUtils.h"
#include "Interfaces/OnlineIdentityInterface.h"

ATencentLoginActor::ATencentLoginActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void ATencentLoginActor::BeginPlay()
{
	Super::BeginPlay();
	TryLogin();
}

void ATencentLoginActor::TryLogin()
{
	IOnlineSubsystem* OnlineSub = Online::GetSubsystem(GetWorld());
	if (OnlineSub)
	{
		IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
		if (IdentityInterface.IsValid())
		{
			UE_LOG(LogTemp, Log, TEXT("Attempting to login via Tencent Online Subsystem..."));
			
			// 绑定登录完成委托
			LoginDelegateHandle = IdentityInterface->AddOnLoginCompleteDelegate_Handle(
				0, // LocalUserNum
				FOnLoginCompleteDelegate::CreateUObject(this, &ATencentLoginActor::OnLoginComplete)
			);

			// 发起登录
			FOnlineAccountCredentials Credentials;
			IdentityInterface->Login(0, Credentials);
		}
		else
		{
			UE_LOG(LogTemp, Warning, TEXT("Identity Interface not available."));
		}
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("Online Subsystem not available."));
	}
}

void ATencentLoginActor::OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error)
{
	// 移除委托
	IOnlineSubsystem* OnlineSub = Online::GetSubsystem(GetWorld());
	if (OnlineSub)
	{
		IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
		if (IdentityInterface.IsValid())
		{
			IdentityInterface->ClearOnLoginCompleteDelegate_Handle(LocalUserNum, LoginDelegateHandle);
		}
	}

	if (bWasSuccessful)
	{
		UE_LOG(LogTemp, Log, TEXT("Login successful. UserId: %s"), *UserId.ToString());
		// 登录成功后的逻辑
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("Login failed. Error: %s"), *Error);
		// 处理登录失败，可能需要重试或提示用户
	}
}
```

## 模块依赖

从插件的 `.uplugin` 文件中 `Plugins` 部分可知，使用此插件需要依赖以下在线子系统基础插件。这些是标准在线功能所必需的，并非本插件的特殊依赖。

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 虚幻引擎在线子系统核心框架 |
| `OnlineSubsystemUtils` | 在线子系统的工具集和蓝图支持 |
| `OnlineFramework` | 在线功能的基础框架 |

**注意**：你的游戏模块的 `.Build.cs` 文件通常不需要直接依赖 `OnlineSubsystemTencent` 模块。通过配置引擎的 `DefaultEngine.ini` 将默认在线子系统设置为 `Tencent`，并确保上述基础插件已启用即可。你需要依赖的是 `OnlineSubsystem` 模块来获取通用接口。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复编译器类型转换警告，提升跨平台编译兼容性。 |
| 2025-10-21 | `fc6688b1` | Store ID missmatch interface change | 商店ID不匹配接口变更，涉及在线商店功能的接口调整。 |
| 2025-09-30 | `96cf6b99` | Removed 32-bit support. | 移除了对32位平台的支持。 |
| 2025-09-12 | `fd5c41be` | Addressing instances “ignoring return value of function declared with ‘nodiscard’ attribute” issue | 修复忽略[[nodiscard]]标记函数返回值的编译器警告问题。 |
| 2025-08-13 | `65515472` | - Deprecate OnlineJsonSerializer.h | 废弃了OnlineJsonSerializer.h头文件。 |

### 维护评价

- **创建时间**：2019年4月，已有约7年历史，是成熟的插件。
- **最近更新**：最近一次更新在2026年5月，主要集中在编译器兼容性修复和平台支持调整（如移除32位）。功能更新较少，最后一次功能性接口变更在2025年10月。
- **维护状态**：**维护中**。虽然更新频率不高，但仍在处理编译问题和平台适配，表明它仍然在UE的主分支中被维护。
- **已知问题/限制**：
    1.  插件默认禁用 (`EnabledByDefault: false`)，必须手动在项目设置中启用。
    2.  仅支持 **Win64** 和 **Linux** 平台。
    3.  其核心功能严重依赖腾讯的 Rail SDK。SDK的更新、兼容性以及中国地区的政策变化都会直接影响此插件的可用性。
    4.  由于腾讯平台在国内的特殊性，其接口和行为可能与国际流行的在线子系统（如 Steam）有较大差异。
- **推荐使用**：如果你明确需要在 WeGame 平台上发行游戏，并且目标平台是 Windows 或 Linux，那么这是**必须且唯一**的选择。对于其他平台或其他在线服务的项目，则无需使用此插件。使用前请务必查阅腾讯官方最新的 Rail SDK 文档以了解限制。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemTencent)