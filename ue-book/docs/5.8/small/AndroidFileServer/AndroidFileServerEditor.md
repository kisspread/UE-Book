# Android File Server

> Adds support for remote file management to Android projects.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 安卓文件服务器 |
| 分类 | Android |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidFileServer` (Runtime), `AndroidFileServerEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-02-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidFileServer) | |

## 用途

这个插件为 Android 平台提供了运行时文件服务器功能，主要用于解决开发和调试阶段的痛点。它允许开发者通过 USB 或本地网络，将编辑器（或使用 `UnrealAndroidFileTool`）直接连接到运行中的 Android 应用，实现快速部署项目、安装 APK、同步文件以及进行远程调试。相比传统的手动复制文件或使用 `adb` 命令，它提供了一个集成化、图形化或脚本化的管理方案，极大地提升了 Android 项目的迭代效率。其核心价值在于简化了打包构建后的“部署-安装-测试”循环。

## 使用场景

- **频繁迭代移动游戏**：当你在 UE5 编辑器中修改了游戏逻辑或资源，点击“启动”或“打包并部署”时，该插件能自动通过 USB 或局域网将新的构建包发送到目标 Android 设备上安装并运行，省去了手动传输的步骤。
- **团队远程设备管理**：在局域网环境下，一位开发者可以通过网络连接到另一台连接着 Android 设备的电脑，并远程管理该设备上的应用和文件。
- **自动化测试流水线**：在持续集成/持续部署（CI/CD）流程中，可以使用 `UnrealAndroidFileTool` 命令行工具，借助此插件实现 APK 的自动安装和测试文件的推送。
- **需要安全连接的场景**：通过配置安全令牌，确保只有授权的客户端可以连接到你的应用文件服务器，防止未授权访问。

## 蓝图用法

此插件的功能主要通过项目设置进行配置，运行时交互较少，未发现公开的 `BlueprintCallable` 核心功能节点。其主要蓝图/编辑器界面集成体现在“项目设置”中。

### 核心配置（通过项目设置）

配置位于：`Project Settings` -> `Platforms` -> `Android` -> `File Server`

| 配置项 | 说明 |
|---|---|
| Use AndroidFileServer | 启用/禁用插件的主开关 |
| Allow Network Connection | 是否允许通过网络（而非仅 USB）连接 |
| Security Token | 设置连接所需的安全令牌（留空则无验证） |
| Connection Type | 连接方式：仅 USB、仅网络、或两者结合 |
| Use Manual IP Address | 对于网络连接，是否手动指定设备 IP 地址 |

## C++ 用法

此插件主要提供编辑器扩展和运行时服务，C++ API 的使用侧重于设置和配置。

### 头文件引入

```cpp
#include "AndroidFileServerRuntimeSettings.h"
```

### 基本用法

在代码中访问和修改插件运行时设置。

```cpp
// 来源：Public/AndroidFileServerRuntimeSettings.h
#include "AndroidFileServerRuntimeSettings.h"

// 获取当前设置实例
UAndroidFileServerRuntimeSettings* Settings = GetMutableDefault<UAndroidFileServerRuntimeSettings>();

// 检查插件是否启用
bool bIsAFSEnabled = Settings->bEnablePlugin;

// 修改设置（例如，强制使用网络连接）
Settings->bAllowNetworkConnection = true;
Settings->ConnectionType = EAFSConnectionType::NetworkOnly;
Settings->bUseManualIPAddress = true;
Settings->ManualIPAddress = TEXT("192.168.1.100");
Settings->SaveConfig(); // 保存更改
```

### 进阶用法

通常，你不直接操作这些设置，而是依赖编辑器模块（`AndroidFileServerEditor`）在启动时根据项目配置初始化和启动文件服务器服务。下面的示例模拟了启动模块可能进行的内部逻辑（非公开 API，仅作原理说明）。

```cpp
// 模拟编辑器模块的启动逻辑（基于模块初始化流程推断）
#include "AndroidFileServerEditor.h"
// 假设存在一个内部函数 StartFileServer
// #include "AndroidFileServerInternal.h" // 可能存在的内部头文件

void FAndroidFileServerEditorModule::StartupModule()
{
    // 1. 检查设置是否启用
    const UAndroidFileServerRuntimeSettings* Settings = GetDefault<UAndroidFileServerRuntimeSettings>();
    if (!Settings->bEnablePlugin)
    {
        return;
    }

    // 2. 根据设置启动服务器
    if (Settings->bAllowNetworkConnection)
    {
        // 启动网络监听
        // NetworkFileServer::Start(Settings->ManualIPAddress);
    }
    // ... 其他初始化逻辑
}
```

## Demo 示例

一个简单的类，用于演示如何在运行时检查和提示文件服务器状态。

**AndroidFileServerStatus.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AndroidFileServerStatus.generated.h"

UCLASS()
class MYGAME_API AAndroidFileServerStatus : public AActor
{
	GENERATED_BODY()
	
public:	
	AAndroidFileServerStatus();

protected:
	virtual void BeginPlay() override;

public:	
	virtual void Tick(float DeltaTime) override;

	// 蓝图可调用函数，用于检查并显示文件服务器状态
	UFUNCTION(BlueprintCallable, Category = "Debug")
	void CheckAndPrintFileServerStatus() const;
};
```

**AndroidFileServerStatus.cpp**
```cpp
#include "AndroidFileServerStatus.h"
#include "AndroidFileServerRuntimeSettings.h"

AAndroidFileServerStatus::AAndroidFileServerStatus()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AAndroidFileServerStatus::BeginPlay()
{
	Super::BeginPlay();
}

void AAndroidFileServerStatus::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
}

void AAndroidFileServerStatus::CheckAndPrintFileServerStatus() const
{
	const UAndroidFileServerRuntimeSettings* Settings = GetDefault<UAndroidFileServerRuntimeSettings>();
	
	if (Settings)
	{
		FString Status = Settings->bEnablePlugin ? TEXT("已启用") : TEXT("已禁用");
		FString ConnectionMode;
		switch (Settings->ConnectionType)
		{
		case EAFSConnectionType::USBOnly:
			ConnectionMode = TEXT("仅USB");
			break;
		case EAFSConnectionType::NetworkOnly:
			ConnectionMode = TEXT("仅网络");
			break;
		case EAFSConnectionType::Combined:
			ConnectionMode = TEXT("USB与网络");
			break;
		}
		
		UE_LOG(LogTemp, Warning, TEXT("Android File Server 状态: %s, 连接模式: %s"), *Status, *ConnectionMode);
		if (Settings->bAllowNetworkConnection && Settings->bUseManualIPAddress)
		{
			UE_LOG(LogTemp, Warning, TEXT("  手动IP地址: %s"), *Settings->ManualIPAddress);
		}
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("无法获取Android File Server运行时设置。"));
	}
}
```

## 模块依赖

从 `Build.cs` 文件分析，使用此插件或进行深度开发需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `AndroidFileServerRuntime` | 文件服务器的核心运行时逻辑模块 |
| `LaunchAndroid` | Android 平台启动和部署相关功能 |
| `ProjectLauncher` | 项目启动器，用于管理部署配置 |

**说明**：编辑器模块 `AndroidFileServerEditor` 可能还依赖 `UnrealEd` 和 `Slate` 等常见编辑器模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-27 | `409776cd` | Fix an issue with compressed file writes to AFS with uncompressable blocks | 修复向文件服务器写入无法压缩数据块时的压缩问题 |
| 2026-05-26 | `2585a962` | [Android] AFS shipping build fix | 修复 Android 平台打包构建（Shipping）的兼容性问题 |
| 2026-05-25 | `09e10f3d` | [Android] AFS build fix | 修复 Android 平台的编译问题 |
| 2026-05-23 | `6d9338cd` | Fix unacceptable words in RemoteFileManager.java | 修复 Java 代码中的不规范用词 |
| 2026-05-22 | `a35e5b4a` | New version of UnrealAndroidFileTool with better error handling, faster data transfer and new GUI mode | 发布新版本 UnrealAndroidFileTool，改进错误处理、提升传输速度并新增 GUI 模式 |

### 维护评价

**综合评价：活跃维护且推荐使用。**

- **活跃维护**：最后更新距今非常近（2026年5月），且近期提交集中于**功能修复（压缩问题）、平台兼容性修复（Android 构建）以及配套工具升级（UnrealAndroidFileTool）**，表明 Epic 官方仍在积极维护和改进此插件。
- **功能稳定**：插件自 2022 年创建以来，核心功能（远程文件管理）稳定，近期更新以修复和优化为主，没有重大架构变动。
- **实用价值高**：对于任何需要频繁部署到 Android 设备进行测试的 UE5 项目，该插件都是标准工具链的重要组成部分，能显著提升开发效率。
- **无重大警告**：虽然创建时间约3年，但持续的维护和功能更新使其完全适用于当前版本的 UE5。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidFileServer)
- 测试用例：未在当前路径下发现标准测试目录（Tests），主要功能验证可能通过 `UnrealAndroidFileTool` 或编辑器操作进行。