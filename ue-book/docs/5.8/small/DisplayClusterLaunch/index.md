# nDisplay Launch

> Launch local nDisplay nodes with ease.

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay启动器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资源） |
| 模块 | `DisplayClusterLaunchEditor` (Runtime) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2022-04-07 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/DisplayClusterLaunch) | |

## 用途

该插件旨在简化 UE5 虚拟制作中 nDisplay 多节点渲染环境的启动流程。它提供了一个集成的编辑器界面，允许用户从编辑器内部一键启动和管理多个本地 nDisplay 渲染节点，并深度集成了 Unreal Concert（多用户编辑）功能，能够自动处理多用户服务器的发现、连接和会话管理。其核心价值在于将原本需要通过命令行或外部工具（如 Switchboard）完成的复杂启动配置和协作流程，内嵌到编辑器中，提升了工作流效率。

## 使用场景

- 你正在使用 nDisplay 进行虚拟制片（Virtual Production）或多屏投影项目，需要同时启动和同步多个渲染节点。
- 你的 nDisplay 工作流需要集成 Unreal Concert 多用户协作，希望自动发现并连接到正确的服务器会话。
- 你希望在启动 nDisplay 节点时，能够方便地切换不同的显示配置（`ADisplayClusterRootActor`）和控制台变量预设。
- 你希望为 nDisplay 启动配置项目级默认设置，如是否关闭主编辑器以优化性能、是否启用 Unreal Insights 性能分析等。

## 蓝图用法

该插件主要提供编辑器工具栏集成，其核心功能通过 `FDisplayClusterLaunchEditorModule` 类暴露。大部分操作通过编辑器 UI 触发，直接蓝图节点较少。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FDisplayClusterLaunchEditorModule::Get()` | 获取插件模块单例 | `FDisplayClusterLaunchEditorModule` |
| `FDisplayClusterLaunchEditorModule::OpenProjectSettings()` | 打开 nDisplay 启动项目设置 | `FDisplayClusterLaunchEditorModule` |
| `FDisplayClusterLaunchEditorModule::TryLaunchDisplayClusterProcess()` | 尝试启动 nDisplay 进程（异步） | `FDisplayClusterLaunchEditorModule` |
| `FDisplayClusterLaunchEditorModule::TerminateActiveDisplayClusterProcesses()` | 终止所有活动的 nDisplay 节点进程 | `FDisplayClusterLaunchEditorModule` |

### 使用示例（蓝图描述）

由于该插件主要为编辑器扩展，典型的使用方式是：
1.  在编辑器工具栏中找到“nDisplay Launch”按钮（通过插件注册的 Toolbar Item）。
2.  点击下拉菜单，从当前世界中存在的 `ADisplayClusterRootActor` 配置中选择要启动的配置。
3.  选择特定的节点或“全部节点”。
4.  （可选）附加一个 Console Variables Asset 进行变量覆盖。
5.  点击启动。插件会根据项目设置（`UDisplayClusterLaunchEditorProjectSettings`）处理多用户连接、Unreal Insights 等配置，并启动所选节点的独立进程。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterLaunchEditorModule.h"
#include "DisplayClusterLaunchEditorProjectSettings.h"
```

### 基本用法

访问插件模块并触发启动流程。

```cpp
// 获取插件模块实例
FDisplayClusterLaunchEditorModule& LaunchModule = FDisplayClusterLaunchEditorModule::Get();

// 检查当前世界是否有nDisplay配置，并尝试启动流程
if (LaunchModule.DoesCurrentWorldHaveDisplayClusterConfig())
{
    // 启动异步流程：检查Concert连接，最终调用LaunchDisplayClusterProcess
    LaunchModule.TryLaunchDisplayClusterProcess();
}
```
*(来源: 基于 `DisplayClusterLaunchEditorModule.h` 中的公开方法推断)*

### 进阶用法

读取项目设置并决定启动行为。

```cpp
// 获取项目设置
const UDisplayClusterLaunchEditorProjectSettings* ProjectSettings = GetDefault<UDisplayClusterLaunchEditorProjectSettings>();
if (ProjectSettings)
{
    // 根据设置决定是否在启动时关闭编辑器
    if (ProjectSettings->bCloseEditorOnLaunch)
    {
        UE_LOG(LogDisplayClusterLaunchEditor, Display, TEXT("Editor will be closed for performance."));
        // ... 执行关闭编辑器逻辑
    }
    
    // 检查是否需要连接多用户
    if (ProjectSettings->bConnectToMultiUser)
    {
        UE_LOG(LogDisplayClusterLaunchEditor, Display, TEXT("Connecting to Multi-User session..."));
        // 插件内部会处理服务器查找和连接
    }
}
```
*(来源: 基于 `DisplayClusterLaunchEditorProjectSettings.h` 中的属性推断)*

## Demo 示例

以下是一个最小化的示例，展示如何在 C++ 代码中获取并使用该插件的模块接口。

**DisplayClusterLaunchTestActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DisplayClusterLaunchTestActor.generated.h"

UCLASS()
class ADisplayClusterLaunchTestActor : public AActor
{
	GENERATED_BODY()
	
public:	
	ADisplayClusterLaunchTestActor();

protected:
	virtual void BeginPlay() override;

public:	
	virtual void Tick(float DeltaTime) override;

	/** 在编辑器中调用此函数，尝试启动nDisplay */
	UFUNCTION(BlueprintCallable, Category="nDisplay Test")
	void TestLaunchnDisplay();

	/** 在编辑器中调用此函数，终止所有nDisplay节点 */
	UFUNCTION(BlueprintCallable, Category="nDisplay Test")
	void TestTerminateAllNodes();
};
```

**DisplayClusterLaunchTestActor.cpp**
```cpp
#include "DisplayClusterLaunchTestActor.h"
#include "DisplayClusterLaunchEditorModule.h"
#include "Engine/World.h"

ADisplayClusterLaunchTestActor::ADisplayClusterLaunchTestActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void ADisplayClusterLaunchTestActor::BeginPlay()
{
	Super::BeginPlay();
}

void ADisplayClusterLaunchTestActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
}

void ADisplayClusterLaunchTestActor::TestLaunchnDisplay()
{
	// 确保模块已加载
	if (FModuleManager::Get().IsModuleLoaded("DisplayClusterLaunchEditor"))
	{
		FDisplayClusterLaunchEditorModule& Module = FDisplayClusterLaunchEditorModule::Get();
		// 执行启动流程
		Module.TryLaunchDisplayClusterProcess();
		UE_LOG(LogTemp, Warning, TEXT("nDisplay Launch process initiated."));
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("DisplayClusterLaunchEditor module is not loaded."));
	}
}

void ADisplayClusterLaunchTestActor::TestTerminateAllNodes()
{
	if (FModuleManager::Get().IsModuleLoaded("DisplayClusterLaunchEditor"))
	{
		FDisplayClusterLaunchEditorModule& Module = FDisplayClusterLaunchEditorModule::Get();
		Module.TerminateActiveDisplayClusterProcesses();
		UE_LOG(LogTemp, Warning, TEXT("Terminated all active nDisplay node processes."));
	}
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。
*(注: 根据源码头文件，该模块依赖了 `DisplayClusterConfiguration`、`Concert` 等模块，但这些是 nDisplay 和多用户功能的内部依赖，对于使用此插件的最终用户项目，通常无需额外添加模块依赖，因为插件已封装了这些功能。)*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式 UE_LOG 日志宏更新为新的 UE_LOGF 格式。 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了日志输出中的 printf 格式说明符错误。 |
| 2025-10-09 | `1d4d3982` | Specify the SupportedPlatformTargets in the DisplayClusterLaunch plugin to prevent it from getting i | 在插件中明确指定支持的平台目标，防止其被意外禁用。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将配置文件 Base<Plugin>.ini 重命名为标准的 Default<Plugin>.ini 格式。 |
| 2025-09-03 | `65d9e8d9` | [nDisplay] Added few more CVars to the DisplayClusterLauncher launch command line | 向 nDisplay 启动器的命令行添加了更多控制台变量（CVars）。 |

### 维护评价

**维护中**。该插件自2022年创建以来，近期（2025-2026年）仍有多次实质性更新，包括功能增强（添加 CVar）、稳定性修复（日志格式、平台支持）和代码现代化（迁移日志宏）。最后一次更新距今不到1个月，表明它仍在被积极维护。

**主要注意事项**：该插件在 `.uplugin` 中被标记为 `IsBetaVersion: true` 且默认不启用 (`EnabledByDefault: false`)。这意味着它可能尚未达到完全稳定的状态，使用时可能遇到问题，需要用户手动在插件管理器中启用。

**推荐**：对于使用 nDisplay 和 Unreal Concert 进行虚拟制作的团队，推荐启用此插件以简化工作流。鉴于其 Beta 状态，建议在生产环境中进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/DisplayClusterLaunch)
- 官方文档链接未在 .uplugin 中提供。
- 测试用例路径未在提供的信息中明确。