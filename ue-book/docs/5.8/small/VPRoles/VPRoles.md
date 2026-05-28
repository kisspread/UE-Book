# Virtual Production Roles

> Allows users to manage Virtual Production Role assignment.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟生产角色 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `VPRoles` (Runtime), `VPRolesEditor` (Runtime) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2023-01-12 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProduction/VPRoles) | |

## 用途

`VPRoles` 插件的核心功能是管理虚拟制片（Virtual Production）环境中的“设备角色”（Role）。它提供了一个运行时子系统 (`UVirtualProductionRolesSubsystem`)，用于根据当前设备的用途（例如：摄像机、切换台、追踪系统、渲染节点等）来分配和查询一个或多个“角色”标识。这使得同一套虚幻引擎项目可以基于命令行参数或配置文件，自动适配不同的硬件设备，从而简化虚拟制片现场的复杂工作流配置和同步。它主要解决的问题是，在多设备协作的虚拟制片项目中，如何让每台机器明确自己的功能定位，并基于此进行逻辑和界面的定制化。

## 使用场景

- 你正在搭建一个虚拟制片片场，有多台运行虚幻引擎的电脑，分别负责摄像机追踪、实时渲染、切换台控制等。使用 `VPRoles`，你可以为每台机器在启动时通过 `-VPRole=Camera|Tracker` 这样的命令行参数定义其角色，并在蓝图或C++中查询当前角色，从而加载对应的界面、功能或资产。
- 你需要开发一个自定义的虚拟制片控制面板，其显示的控件应根据当前机器的角色动态变化（例如，渲染节点不显示摄像机控制选项）。使用 `VPRoles` 子系统可以方便地获取当前活跃的角色列表，并据此更新UI。

## 蓝图用法

所有与角色交互的蓝图节点都位于 `UVirtualProductionRolesSubsystem` 类中，分类路径为 `Virtual Production | Roles`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Active Roles` | 获取当前所有激活的角色名称列表（字符串数组）。 | `UVirtualProductionRolesSubsystem` |
| `Has Active Role` | 检查指定角色（字符串）是否为当前激活的角色之一。 | `UVirtualProductionRolesSubsystem` |
| `Set Active Roles` | 设置当前激活的角色列表。注意：角色必须已经通过“Add Role”添加过。 | `UVirtualProductionRolesSubsystem` |
| `Get All Roles` | 获取所有可被设置为“当前角色”的、已注册的角色列表。 | `UVirtualProductionRolesSubsystem` |
| `Add Role` | 添加一个新的角色（仅编辑器下可用）。操作会尝试修改底层配置文件。 | `UVirtualProductionRolesSubsystem` |
| `Remove Role` | 移除一个角色（仅编辑器下可用）。操作会尝试修改底层配置文件。 | `UVirtualProductionRolesSubsystem` |
| `On Roles Changed` (Delegate) | 当角色列表发生变更（添加、移除、替换当前角色）时广播的蓝图可分配委托。 | `UVirtualProductionRolesSubsystem` |

### 使用示例（蓝图描述）

1.  **查询当前角色**：在一个BeginPlay事件中，拖拽出`GetActiveRoles`节点，其返回值是一个字符串数组，你可以将其用于后续逻辑判断或日志输出。
2.  **角色条件分支**：使用`HasActiveRole`节点，传入一个角色名字符串（如“Camera”），其返回的布尔值可以直接连接到一个`Branch`节点，从而根据当前设备是否为摄像机执行不同的代码路径。
3.  **监听角色变化**：在蓝图的事件图表中，从`UVirtualProductionRolesSubsystem`对象拖引线，找到`Assign OnRolesChangedBP`事件，然后在事件节点中编写你的响应逻辑（例如刷新UI）。

## C++ 用法

### 头文件引入

```cpp
#include "VPRolesSubsystem.h"
```

### 基本用法

```cpp
// 获取子系统实例。它在引擎初始化时自动创建。
UVirtualProductionRolesSubsystem* RoleSubsystem = GEngine->GetEngineSubsystem<UVirtualProductionRolesSubsystem>();
if (RoleSubsystem)
{
    // 查询当前激活的角色
    TArray<FString> ActiveRoles = RoleSubsystem->GetActiveRoles();
    
    // 检查特定角色是否激活
    FString TargetRole = TEXT("CinematicCamera");
    bool bIsCinematicCamera = RoleSubsystem->HasActiveRole(TargetRole);
    
    // 获取所有可用的角色
    TArray<FString> AllAvailableRoles = RoleSubsystem->GetAllRoles();
}
```

### 进阶用法

```cpp
// 在代码中动态设置当前活跃的角色（需要确保角色已存在）
TArray<FString> NewActiveRoles = { TEXT("RenderNode"), TEXT("Compositor") };
RoleSubsystem->SetActiveRoles(NewActiveRoles);

// 监听角色变更的原生委托（C++中通常使用此委托）
FOnRolesChangedNative& OnRolesChangedDelegate = RoleSubsystem->OnRolesChanged();
OnRolesChangedDelegate.AddLambda([](const TArray<FString>& EnabledRoles)
{
    UE_LOG(LogTemp, Log, TEXT("Roles changed! New roles: %s"), *FString::Join(EnabledRoles, TEXT(", ")));
});

// 查询是否使用了命令行参数指定的角色
bool bUsingCmdLine = RoleSubsystem->IsUsingCommandLineRoles();
bool bHasCmdLineRoles = RoleSubsystem->HasCommandLineRoles();
```

## Demo 示例

以下是一个最小化的 Actor 组件示例，演示了如何初始化角色子系统、查询角色并响应变化。

**VPRolesDemoComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "VPRolesSubsystem.h"
#include "VPRolesDemoComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UVPRolesDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    void OnRolesChanged(const TArray<FString>& NewRoles);

    FDelegateHandle RoleChangedDelegateHandle;
};
```

**VPRolesDemoComponent.cpp**
```cpp
#include "VPRolesDemoComponent.h"

void UVPRolesDemoComponent::BeginPlay()
{
    Super::BeginPlay();

    // 获取子系统
    if (UVirtualProductionRolesSubsystem* RoleSubsystem = GEngine->GetEngineSubsystem<UVirtualProductionRolesSubsystem>())
    {
        // 绑定原生委托
        RoleChangedDelegateHandle = RoleSubsystem->OnRolesChanged().AddUObject(this, &UVPRolesDemoComponent::OnRolesChanged);

        // 初始查询
        TArray<FString> CurrentRoles = RoleSubsystem->GetActiveRoles();
        if (!CurrentRoles.IsEmpty())
        {
            UE_LOG(LogTemp, Log, TEXT("Initial Active Roles: %s"), *FString::Join(CurrentRoles, TEXT(", ")));
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("No active VP roles found for this machine."));
        }
    }
}

void UVPRolesDemoComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (UVirtualProductionRolesSubsystem* RoleSubsystem = GEngine->GetEngineSubsystem<UVirtualProductionRolesSubsystem>())
    {
        // 解绑委托
        RoleSubsystem->OnRolesChanged().Remove(RoleChangedDelegateHandle);
    }
    Super::EndPlay(EndPlayReason);
}

void UVPRolesDemoComponent::OnRolesChanged(const TArray<FString>& NewRoles)
{
    UE_LOG(LogTemp, Log, TEXT("Roles changed during runtime! New roles: %s"), *FString::Join(NewRoles, TEXT(", ")));
    // 在这里可以执行基于新角色的逻辑，例如重新加载UI等。
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 核心依赖。`VPRoles` 插件使用 `FGameplayTagContainer` 来内部存储和管理角色标签，提供了强大的层次化标签查询和匹配能力。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏更新为新的 UE_LOGF 宏。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复之前一次错误替换后的第二次尝试。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 撤销了某个特定的改动列表。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing registration. | 调整引擎初始化委托的注册方式以修复问题。 |
| 2023-01-13 | `9d37f2ee` | Fixed non unity compile errors caused by integration from RES. Errors were reported by farm. | 修复了从 RES 集成导致的非统一编译错误。 |

### 维护评价

`VPRoles` 是一个较新的实验性插件（创建于2023年初）。其近期提交（2026年）主要是跟随引擎核心API的通用重构（如日志宏和委托的调整），而非插件自身的功能增强或Bug修复。自创建以来，该插件的功能似乎已经稳定。考虑到其“隐藏”(`Hidden: true`)和“Beta”(`IsBetaVersion: true`)的状态，表明 Epic 可能将其内部使用或作为实验功能提供，尚未准备作为公开的稳定特性。**推荐用于实验性虚拟制片工作流或需要动态设备角色管理的项目，但在生产环境中需谨慎评估其长期支持情况。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProduction/VPRoles)
- [官方文档]()（无）