# Virtual Production Roles

> Allows users to manage Virtual Production Role assignment.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟制片角色 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置数据） |
| 模块 | `VPRoles` (Runtime), `VPRolesEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-12 |
| 年龄标签 | 👴 老古董（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProduction/VPRoles) | |

## 用途

本插件专为虚拟制片（Virtual Production）场景设计，用于管理不同工作站或操作员角色的个性化配置。它解决的核心问题是：在同一个项目中，导演、摄影指导、灯光师等不同角色，可能需要访问不同的资产、使用不同的编辑器布局和工具配置。该插件允许用户定义“角色”（如 CameraOperator, LightingArtist），并为每个角色分配特定的编辑器设置、默认资产加载列表等，从而在切换角色时快速切换工作环境，提升协作效率。

## 使用场景

- 你的团队在现场进行虚拟制片拍摄，使用多台工作站，每台工作站由不同职能的人员操作（如摄影、灯光、合成）。
- 你需要为每台工作站预设不同的编辑器默认布局、可访问的资产库以及工具配置。
- 你希望通过一个简单的界面或命令，让操作员在工作站启动时自动加载其对应角色的配置。

## 蓝图用法

根据模块文档，蓝图 API 主要集中在 `UVPRolesSubsystem` 和 `UVPRole` 类。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get VPRoles Subsystem` | 获取虚拟制片角色子系统的实例，用于访问角色管理功能。 | `UVPRolesSubsystem` |
| `Get Current Role` | 获取当前工作站或用户被分配的角色对象。 | `UVPRolesSubsystem` |
| `Set Current Role` | 设置当前工作站或用户的角色。 | `UVPRolesSubsystem` |
| `Get Role Configuration` | 获取指定角色对象的配置数据（如资产列表）。 | `UVPRole` |
| `Load Role Configuration` | 加载并应用一个角色的配置到当前编辑器环境。 | `UVPRolesSubsystem` |

### 使用示例（蓝图描述）

1.  在一个编辑器工具蓝图（Editor Utility Widget）中，使用 `Get VPRoles Subsystem` 节点获取子系统实例。
2.  调用 `Get Current Role` 获取当前角色，并将其显示在 UI 上。
3.  当用户从下拉菜单中选择新角色时，调用 `Set Current Role` 更新角色。
4.  调用 `Load Role Configuration`，该子系统会根据新角色的配置，自动加载对应的资产和调整编辑器设置。

## C++ 用法

核心逻辑通过子系统暴露，C++ 中可以直接访问以进行更深度的集成或扩展。

### 头文件引入

```cpp
#include "VPRolesSubsystem.h"
#include "VPRole.h"
```

### 基本用法

获取角色子系统并查询当前角色信息。
（来源：基于 `UVPRolesSubsystem` 和 `UVPRole` 的典型用法推断）

```cpp
// 在需要角色管理功能的类中（例如自定义编辑器工具或游戏模块初始化）
UVPRolesSubsystem* VPRolesSubsystem = GEditor->GetEditorSubsystem<UVPRolesSubsystem>();
if (VPRolesSubsystem)
{
    // 获取当前分配的角色
    UVPRole* CurrentRole = VPRolesSubsystem->GetCurrentRole();
    if (CurrentRole)
    {
        UE_LOG(LogTemp, Log, TEXT("Current VP Role: %s"), *CurrentRole->GetRoleName().ToString());
    }

    // 列出所有可用的角色
    TArray<UVPRole*> AllRoles = VPRolesSubsystem->GetAllRoles();
    for (UVPRole* Role : AllRoles)
    {
        UE_LOG(LogTemp, Log, TEXT("Available Role: %s"), *Role->GetRoleName().ToString());
    }
}
```

### 进阶用法

监听角色变更事件，以便在角色切换时执行自定义逻辑。
（来源：基于典型的编辑器子系统事件监听模式）

```cpp
// 在某个编辑器模块的 StartupModule 中
FDelegateHandle OnRoleChangedHandle = UVPRolesSubsystem::OnRoleChanged.AddLambda(
    [](const UVPRole* NewRole)
    {
        if (NewRole)
        {
            // 响应角色变更，例如更新特定工具的可用性
            UE_LOG(LogTemp, Log, TEXT("VP Role changed to: %s"), *NewRole->GetRoleName().ToString());
            // 执行自定义逻辑...
        }
    }
);

// 记得在 ShutdownModule 中解绑
UVPRolesSubsystem::OnRoleChanged.Remove(OnRoleChangedHandle);
```

## Demo 示例

一个最小化的自定义编辑器工具，显示当前角色并允许切换。
（请注意，此示例依赖于插件本身提供的 `UVPRolesSubsystem` 和 `UVPRole` 类）

**MyVPRoleTool.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "EditorUtilityWidget.h"
#include "VPRolesSubsystem.h" // 需要依赖 VPRolesEditor 模块
#include "MyVPRoleTool.generated.h"

class UComboBoxString;
class UVPRole;

UCLASS()
class UMyVPRoleTool : public UEditorUtilityWidget
{
    GENERATED_BODY()

public:
    virtual void NativeConstruct() override;

    UFUNCTION(BlueprintCallable, Category = "VPRoles")
    void RefreshRoleList();

    UFUNCTION(BlueprintCallable, Category = "VPRoles")
    void OnRoleSelected(FString SelectedRoleName);

protected:
    UPROPERTY(meta = (BindWidget))
    UComboBoxString* RoleComboBox;

private:
    UPROPERTY()
    TArray<UVPRole*> CachedRoles;
};
```

**MyVPRoleTool.cpp**
```cpp
#include "MyVPRoleTool.h"
#include "VPRole.h"
#include "Components/ComboBoxString.h"

void UMyVPRoleTool::NativeConstruct()
{
    Super::NativeConstruct();
    RefreshRoleList();
}

void UMyVPRoleTool::RefreshRoleList()
{
    UVPRolesSubsystem* Subsystem = GEditor->GetEditorSubsystem<UVPRolesSubsystem>();
    if (Subsystem && RoleComboBox)
    {
        RoleComboBox->ClearOptions();
        CachedRoles = Subsystem->GetAllRoles();
        for (const UVPRole* Role : CachedRoles)
        {
            RoleComboBox->AddOption(Role->GetRoleName().ToString());
        }

        // 设置当前选中项
        UVPRole* CurrentRole = Subsystem->GetCurrentRole();
        if (CurrentRole)
        {
            RoleComboBox->SetSelectedOption(CurrentRole->GetRoleName().ToString());
        }
    }
}

void UMyVPRoleTool::OnRoleSelected(FString SelectedRoleName)
{
    UVPRolesSubsystem* Subsystem = GEditor->GetEditorSubsystem<UVPRolesSubsystem>();
    if (Subsystem)
    {
        for (UVPRole* Role : CachedRoles)
        {
            if (Role && Role->GetRoleName().ToString() == SelectedRoleName)
            {
                Subsystem->SetCurrentRole(Role);
                break;
            }
        }
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。插件自身的模块依赖关系：
- `VPRoles` (Runtime) 模块：提供核心的角色数据管理和运行时逻辑。
- `VPRolesEditor` (Runtime) 模块：提供编辑器内的用户界面、配置工具和扩展点。**开发自定义编辑器工具时通常需要依赖此模块。**

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏更新为 UE_LOGF 格式。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了上次重构引入的错误。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了之前的一次提交。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复引擎初始化委托的注册问题。 |
| 2023-01-13 | `9d37f2ee` | Fixed non unity compile errors caused by integration from RES. Errors were reported by farm | 修复了非 unity 编译模式下的编译错误。 |

### 维护评价

该插件创建于 2023 年初，属于实验性插件（`IsBetaVersion=true`, `Hidden=true`，`Installed=false`）。从提交历史看，自创建以来（2023-01）到 2026 年 4 月有持续的维护活动，但均为编译修复、API 适配和稳定性改进，**没有发现重大功能更新**。最近的提交也主要是底层依赖的适配。

**综合评价**：插件功能明确且仍在维护中，确保其能在最新引擎版本下编译和运行。然而，其“实验性”和“隐藏”的状态表明 Epic 可能尚未将其作为官方推荐方案，API 和功能在未来版本中存在变动的可能性。适用于需要早期采用和定制的项目，但使用者需自行承担一定的风险。**谨慎推荐**，建议在项目评估阶段进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProduction/VPRoles)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProduction/VPRoles/Tests)