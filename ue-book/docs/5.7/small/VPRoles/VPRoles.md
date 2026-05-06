# Virtual Production Roles

> Allows users to manage Virtual Production Role assignment.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟制片角色 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `VPRoles` (Runtime), `VPRolesEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-12 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProduction/VPRoles) | |

## 用途

在虚拟制片（Virtual Production）工作流中，不同机器（如渲染节点、控制工作站、摄影机跟踪服务器）需要明确自身承担的角色。本插件提供一套角色管理机制：

- 通过命令行参数 `-VPRole=[Role.SubRole1|Role.SubRole2]` 在启动时指定机器角色
- 通过用户设置（`UserVPRoles.ini`）存储当前机器角色列表
- 提供子系统 `UVirtualProductionRolesSubsystem` 查询、修改、监听角色变化
- 支持在编辑器中添加/删除可用角色（需修改 `VProles.ini` 配置文件）

它将角色定义为标签（`FGameplayTag`），支持层次化结构（如 `Director.Camera`、`Lighting.Master`），并自动从命令行参数和配置文件中合并最终角色。

## 使用场景

- 搭建多机虚拟制片协同环境，你需要让每台机器知道自己是“导演台”、“灯光控制”还是“渲染节点”
- 根据角色动态调整引擎行为（例如灯光工作站在编辑器模式下，渲染节点在游戏模式并禁用 UI）
- 在蓝图中快速判断当前机器是否具备某角色，以控制 UI 显示、功能开关或材质参数

## 蓝图用法

### 核心节点

所有蓝图可用函数均位于 `UVirtualProductionRolesSubsystem`（通过 Game Instance 或全局子系统获取）。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetActiveRoles` | 获取当前启用的所有角色名称数组 | `UVirtualProductionRolesSubsystem` |
| `HasActiveRole` | 判断指定角色是否已启用（参数为字符串，如 `"Director.Camera"`） | `UVirtualProductionRolesSubsystem` |
| `GetActiveRolesString` | 返回当前角色列表的逗号分隔字符串（用于日志显示） | `UVirtualProductionRolesSubsystem` |
| `SetActiveRoles` | 用新角色列表替换当前角色（注意：会清空旧角色，新角色必须事先通过 `AddRole` 添加） | `UVirtualProductionRolesSubsystem` |
| `GetAllRoles` | 获取所有可用的角色名称（来自配置文件中定义的全局角色清单） | `UVirtualProductionRolesSubsystem` |
| `AddRole` (Editor Only) | 添加一个新的可用角色（会尝试写入 `VProles.ini`，需要文件可写） | `UVirtualProductionRolesSubsystem` |
| `RemoveRole` (Editor Only) | 删除一个已有可用角色（同样会修改配置文件） | `UVirtualProductionRolesSubsystem` |

### 委托绑定

- **OnRolesChanged**: 动态多播委托 (`FOnRolesChanged`)，可在蓝图直接绑定，当角色发生变化（添加/删除/切换）时触发，参数为当前启用的角色数组。

### 使用示例（蓝图）

1. **显示当前角色**
    - 事件 `Event BeginPlay` → 获取 `Virtual Production Roles Subsystem` → 调用 `Get Active Roles` → 输出字符串或用 `For Each Loop` 处理。

2. **条件分支：是否有某个角色**
    - 调用 `Has Active Role` (Role = `"Lighting.Master"`) → 如果为真，则执行开启灯光控制 UI 的逻辑；否则隐藏。

3. **切换角色**
    - 调用 `Get All Roles` → 遍历显示给玩家选择 → 玩家选择后调用 `Set Active Roles` (例如只选一个)。注意需要先确保角色已通过 `AddRole` 添加。

## C++ 用法

### 头文件引入

```cpp
#include "VPRolesSubsystem.h"
```

### 基本用法

通过 `UGameInstance` 获取子系统：

```cpp
// 获取角色子系统
UVirtualProductionRolesSubsystem* VPRolesSubsystem = GEngine->GetEngineSubsystem<UVirtualProductionRolesSubsystem>();
if (VPRolesSubsystem)
{
    // 查询当前活跃角色
    TArray<FString> ActiveRoles = VPRolesSubsystem->GetActiveRoles();

    // 判断是否有特定角色
    bool bIsCameraOperator = VPRolesSubsystem->HasActiveRole(TEXT("Camera.Operator"));

    // 获取所有可用角色
    TArray<FString> AllRoles = VPRolesSubsystem->GetAllRoles();

    // 设置角色（清空旧角色，替换为新列表）
    VPRolesSubsystem->SetActiveRoles({TEXT("Director"), TEXT("Lighting.Master")});
}
```

### 进阶用法

监听原生角色变化事件：

```cpp
#include "VPRolesSubsystem.h"

void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    if (UVirtualProductionRolesSubsystem* Subsystem = GEngine->GetEngineSubsystem<UVirtualProductionRolesSubsystem>())
    {
        Subsystem->OnRolesChanged().AddUObject(this, &AMyActor::OnRolesChangedHandler);
    }
}

void AMyActor::OnRolesChangedHandler(const TArray<FString>& EnabledRoles)
{
    UE_LOG(LogTemp, Log, TEXT("Roles changed, now active: %s"), *FString::Join(EnabledRoles, TEXT(",")));
    // 根据新角色调整行为
}

void AMyActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (UVirtualProductionRolesSubsystem* Subsystem = GEngine->GetEngineSubsystem<UVirtualProductionRolesSubsystem>())
    {
        Subsystem->OnRolesChanged().RemoveAll(this);
    }
    Super::EndPlay(EndPlayReason);
}
```

检查是否使用命令行角色：

```cpp
bool bUsingCmdRoles = VPRolesSubsystem->IsUsingCommandLineRoles();
```

## Demo 示例

一个最小 C++ Actor，根据角色决定是否打印信息。

**MyRoleAwareActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyRoleAwareActor.generated.h"

UCLASS()
class AMyRoleAwareActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    void OnRoleChanged(const TArray<FString>& EnabledRoles);
    FDelegateHandle OnRolesChangedHandle;
};
```

**MyRoleAwareActor.cpp**
```cpp
#include "MyRoleAwareActor.h"
#include "VPRolesSubsystem.h"

void AMyRoleAwareActor::BeginPlay()
{
    Super::BeginPlay();
    if (UVirtualProductionRolesSubsystem* Subsystem = GEngine->GetEngineSubsystem<UVirtualProductionRolesSubsystem>())
    {
        // 初始检查
        if (Subsystem->HasActiveRole(TEXT("Director")))
        {
            UE_LOG(LogTemp, Log, TEXT("This machine is the Director."));
        }
        // 注册变化回调
        Subsystem->OnRolesChanged().AddUObject(this, &AMyRoleAwareActor::OnRoleChanged);
    }
}

void AMyRoleAwareActor::OnRoleChanged(const TArray<FString>& EnabledRoles)
{
    bool bIsVFX = EnabledRoles.Contains(TEXT("VFX"));
    UE_LOG(LogTemp, Log, TEXT("Role changed, VFX mode = %s"), bIsVFX ? TEXT("true") : TEXT("false"));
}

void AMyRoleAwareActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (UVirtualProductionRolesSubsystem* Subsystem = GEngine->GetEngineSubsystem<UVirtualProductionRolesSubsystem>())
    {
        Subsystem->OnRolesChanged().RemoveAll(this);
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 角色使用 `FGameplayTag` 表示，支持层次化定义及标签运算 |
| `DeveloperSettings` | 提供 `UVirtualProductionRolesUserSettings` 以持久化角色配置 |

（无其他特殊依赖，标准 Core/Engine/Slate 等已省略）

## 维护状态

### 近期更新

- 2023-01-13 `9d37f2e` 修复非 Unity 编译错误（集成后问题）
- 2023-01-12 `be1992f` 将 VPSettings 和 VPRoles 从旧模块迁移到独立插件

### 维护评价

该插件创建于 2023 年初，仅有两次提交（移动 + 修复编译），此后无任何更新。作为实验性插件，它提供了基本但完整的角色管理功能，适合在虚拟制片项目中试用。但由于长期缺乏维护，可能存在以下风险：
- 不会自动适配更新的 UE 版本（如引擎 API 变更）
- 缺少单元测试（源码目录未见测试文件）
- 文档和示例不足

**建议**：在项目中使用前，充分测试其与当前引擎版本的兼容性；考虑自行 Fork 并维护，或使用更成熟的角色方案（如基于 GameplayTags 自行实现）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProduction/VPRoles)
- [官方文档] 无
- [测试用例] 无（该插件未包含测试）