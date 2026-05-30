# Remote Control Web Interface

> Provides a web interface to control unreal engine via presets, requires nodejs to be installed

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制 Web 界面 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Web 应用程序资源） |
| 模块 | `RemoteControlWebInterface` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-12-11 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControlWebInterface) | |

## 用途

本插件为 Remote Control 插件提供了一个基于浏览器的 Web 界面。它在后台启动一个 Node.js 进程作为中间层服务器（Middleman Server），通过 WebSocket 与 UE 引擎通信，使得用户可以通过网页远程控制 UE 中通过 Remote Control Preset 暴露的属性。

**核心工作原理**：插件启动后会运行一个独立的 Node.js 外部进程，该进程托管 Web 应用程序。浏览器通过访问该 Web 应用来查看和操控 UE 中已暴露的远程控制属性。插件还允许在 Remote Control Panel 的 UI 中自定义每个属性的 Web 控件类型和描述，从而决定它在网页上的展示方式。

**前提条件**：必须在系统上安装 Node.js。

## 使用场景

- 你需要在浏览器中远程查看和控制 UE 中暴露的属性（例如在虚拟制片现场通过平板电脑调整灯光参数）
- 你需要将 UE 中的 Actor 属性通过 Web 界面暴露给不直接操作 UE 编辑器的团队成员
- 你需要在 Virtual Production 工作流中实现多设备、跨平台的参数控制

## 蓝图用法

本插件提供了一个蓝图函数库 `URCWebInterfaceBlueprintLibrary`，主要用于远程控制属性的重新绑定和 Actor 管理。

### 核心节点

**属性重绑定相关：**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindMatchingActorsToRebind` | 查找可重新绑定指定远程控制属性的兼容 Actor，返回 Actor 标签到 Actor 指针的映射 | `URCWebInterfaceBlueprintLibrary` |
| `GetOwnerActorLabel` | 获取远程控制属性所属 Owner Actor 的标签，若属性归属不同 Actor 则返回空字符串 | `URCWebInterfaceBlueprintLibrary` |
| `RebindProperties` | 将指定的远程控制属性重新绑定到新的 Owner Actor | `URCWebInterfaceBlueprintLibrary` |

**Actor 工具相关：**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindAllActorsOfClass` | 查找场景中指定类的所有 Actor，返回 Actor 指针到名称的映射 | `URCWebInterfaceBlueprintLibrary` |
| `SpawnActor` | 生成一个指定类的 Actor 并返回其引用 | `URCWebInterfaceBlueprintLibrary` |
| `GetValuesOfActorsByClass` | 获取指定类所有 Actor 的属性值（JSON 格式），返回 Actor 指针到 JSON 字符串的映射 | `URCWebInterfaceBlueprintLibrary` |

### 使用示例（蓝图描述）

**重新绑定远程控制属性到新 Actor：**

1. 调用 `GetOwnerActorLabel`，传入 PresetId 和 PropertyIds，获取当前属性所属 Actor 标签
2. 调用 `FindMatchingActorsToRebind`，传入相同的 PresetId 和 PropertyIds，获取兼容的 Actor 列表
3. 从返回的 Map 中选择目标 Actor
4. 调用 `RebindProperties`，传入 PresetId、PropertyIds 和目标 Actor，完成属性重绑定

**批量获取同类 Actor 的属性值：**

1. 使用 `FindAllActorsOfClass` 获取场景中所有指定类的 Actor
2. 调用 `GetValuesOfActorsByClass` 传入同一类，直接获取所有 Actor 的属性 JSON 数据
3. 解析返回的 Map 中的 JSON 字符串以获取具体属性值

## C++ 用法

### 头文件引入

```cpp
#include "RCWebInterface.h"
```

### 基本用法

获取模块单例并检查 Web 进程状态：

```cpp
// 获取模块单例
FRemoteControlWebInterfaceModule& WebInterfaceModule = FRemoteControlWebInterfaceModule::Get();

// 注意：模块内部管理了 Node.js 进程的生命周期
// 启动时会自动启动 WebApp 进程，关闭时会自动清理
// 无需手动调用 Start/Shutdown
```

来源：`Source/RemoteControlWebInterface/Public/RCWebInterface.h`

### 进阶用法

通过命令行参数禁用 Web Interface（适用于不需要 Web 功能的场景）：

```cpp
// 在启动 UE 时传入命令行参数：
// UnrealEditor.exe -RCWebInterfaceDisable
// 
// 模块内部会检查 bRCWebInterfaceDisable 标志
// 当该标志为 true 时，WebApp 进程不会被启动
```

来源：`Source/RemoteControlWebInterface/Public/RCWebInterface.h`

在蓝图中通过 C++ 库函数操作远程控制属性：

```cpp
#include "RCWebInterfaceLibrary.h"

// 查找可重绑定的 Actor
TMap<FString, AActor*> MatchingActors = 
    URCWebInterfaceBlueprintLibrary::FindMatchingActorsToRebind(PresetId, PropertyIds);

// 将属性重绑定到新 Actor
AActor* NewOwner = /* ... */;
URCWebInterfaceBlueprintLibrary::RebindProperties(PresetId, PropertyIds, NewOwner);

// 获取指定类所有 Actor 的属性值（JSON）
TMap<AActor*, FString> ActorValues = 
    URCWebInterfaceBlueprintLibrary::GetValuesOfActorsByClass(MyActorClass);
```

来源：`Source/RemoteControlWebInterface/Private/RCWebInterfaceLibrary.h`

## Demo 示例

以下示例展示如何在运行时检测 Remote Control Web Interface 的状态并通过命令行控制其行为：

```cpp
// RemoteControlWebDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RemoteControlWebDemo.generated.h"

UCLASS()
class ARemoteControlWebDemo : public AActor
{
    GENERATED_BODY()

public:
    ARemoteControlWebDemo();

    virtual void BeginPlay() override;
};
```

```cpp
// RemoteControlWebDemo.cpp
#include "RemoteControlWebDemo.h"
#include "RCWebInterface.h"
#include "RCWebInterfaceLibrary.h"

ARemoteControlWebDemo::ARemoteControlWebDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ARemoteControlWebDemo::BeginPlay()
{
    Super::BeginPlay();

    // 确保 RemoteControlWebInterface 模块已加载
    if (FModuleManager::Get().IsModuleLoaded("RemoteControlWebInterface"))
    {
        UE_LOG(LogTemp, Log, TEXT("Remote Control Web Interface 模块已加载"));
        
        // 模块会自动管理 Node.js 进程
        // 可通过 -RCWebInterfaceDisable 命令行参数禁用
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Remote Control Web Interface 模块未加载"));
    }
}
```

## 模块依赖

本插件依赖 RemoteControl 插件（在 .uplugin 中声明），自身无特殊 Build.cs 依赖。

| 模块 | 用途 |
|---|---|
| `RemoteControl` | 核心远程控制功能（插件依赖，非模块依赖） |

无特殊依赖（仅标准 Core/Engine 等），主要通过插件级依赖 RemoteControl 实现功能。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-28 | `1ee0e10a` | Remote Control: tentative fix for rc webapp not building in linux | 尝试修复 Linux 平台下 Web 应用无法构建的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF 宏 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修正之前错误的查找替换操作 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了 CL51314860 的改动 |

### 维护评价

该插件创建于 2020 年底（约 6 年前），近期（2026 年）仍有持续的维护更新，包括平台兼容性修复（Linux 构建）和代码质量改进（编译警告修复、日志宏迁移）。维护更新以编译兼容性和小修为主，未见重大功能变更。

**当前状态**：维护中，仍有活跃的 bug 修复和平台适配工作。

**注意事项**：
- 该插件**默认不启用**（`Installed: false`），需要手动在插件设置中启用
- 依赖系统安装 Node.js 环境
- 仅支持 Mac、Win64 和 Linux 平台
- Web 应用首次启动时需要编译，可能需要较长时间

**推荐程度**：如果你的 Virtual Production 工作流需要通过浏览器远程控制 UE 属性，此插件是官方提供的标准方案，推荐使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControlWebInterface)
- 测试用例：未在插件目录内发现独立测试文件