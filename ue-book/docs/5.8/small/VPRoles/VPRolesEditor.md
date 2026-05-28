# Virtual Production Roles

> Allows users to manage Virtual Production Role assignment.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟制作角色 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `VPRoles` (Runtime), `VPRolesEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-12 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProduction/VPRoles) | |

## 用途

VPRoles 插件提供了一套用于管理虚拟制作（Virtual Production）中用户角色的系统。它通过 Gameplay Tags 机制来定义和分配角色，解决了在多团队协作的虚拟制作环境中，需要根据不同角色（如导演、灯光师、摄影指导等）来管理不同设备配置、权限或视图的痛点。该插件为编辑器提供了扩展界面，方便用户创建和管理这些角色标签。

## 使用场景

- 在一个复杂的虚拟制作现场，需要根据不同的岗位角色（如摄影师、灯光师、技术美术）配置不同的工作站和设备参数。
- 你需要一个中心化的地方来管理所有可能用到的角色类型，并确保这些类型在项目中使用一致。
- 你希望在编辑器的关卡编辑器工具栏中快速访问和配置这些角色。

## 蓝图用法

该插件主要提供编辑器扩展功能，**没有公开的蓝图可调用节点（BlueprintCallable）或蓝图可读写属性（BlueprintReadWrite）**。其核心管理功能主要通过编辑器 UI 和 C++ 模块内部接口提供。

## C++ 用法

该插件的核心功能集成在 `VPRolesEditor` 模块中，主要用于扩展编辑器。其内部 API 主要围绕 UI 扩展。

### 头文件引入

```cpp
#include "VPRolesEditorModule.h"
```

### 基本用法

插件通过 `FVPRolesEditorModule` 模块在编辑器启动时自动扩展关卡编辑器工具栏。以下是模块内部接口的示例，展示了如何生成和管理 Gameplay Tag 窗口。

```cpp
// 来自 Private/VPRolesEditorModule.h
// 生成工具栏菜单项
TSharedRef<SWidget> ToolbarMenuWidget = FVPRolesEditorModule::GenerateVPRolesLevelEditorToolbarMenu();

// 生成用于管理角色的 Gameplay Tag 编辑控件
TSharedRef<SWidget> TagWidget = FVPRolesEditorModule::GenerateGameplayTagWidget();

// 检查默认的 Tag 源是否可修改（通常判断配置文件是否为只读）
bool bCanModify = FVPRolesEditorModule::CanModifyTagSource();

// 处理用户在 UI 中提交的新角色 Tag
void OnSubmitNewTag(const FText& CommittedText, ETextCommit::Type CommitType)
{
    // 在这里，插件内部会将新文本解析为 Gameplay Tag 并尝试添加到默认源
}
```

### 进阶用法

插件允许你判断是否显示特定的 UI 元素，例如监视默认配置文件的文件浏览器小部件。

```cpp
// 来自 Private/VPRolesEditorModule.h
// 判断是否显示文件监视器小部件（通常用于监视配置文件变化）
EVisibility Visibility = FVPRolesEditorModule::DetermineFileWatcherWidgetVisibility();
if (Visibility == EVisibility::Visible)
{
    // 文件监视器可见，用户可能修改了默认标签源文件
}
```

## Demo 示例

以下是一个最小示例，展示如何在你的编辑器模块中注册一个自定义的角色标签源，并监听标签变更。这需要你自己的编辑器模块依赖 `GameplayTags` 和 `VPRoles`。

**MyRolesExtension.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyRolesExtensionModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void RegisterCustomTagSource();
    void UnregisterCustomTagSource();
};
```

**MyRolesExtension.cpp**
```cpp
#include "MyRolesExtension.h"
#include "GameplayTagsModule.h"
#include "GameplayTagsSettings.h"

#define LOCTEXT_NAMESPACE "FMyRolesExtensionModule"

void FMyRolesExtensionModule::StartupModule()
{
    RegisterCustomTagSource();
}

void FMyRolesExtensionModule::ShutdownModule()
{
    UnregisterCustomTagSource();
}

void FMyRolesExtensionModule::RegisterCustomTagSource()
{
    // 确保GameplayTag系统已加载
    if (IGameplayTagsModule* GameplayTagsModule = FModuleManager::GetModulePtr<IGameplayTagsModule>("GameplayTags"))
    {
        // 获取设置对象
        UGameplayTagsSettings* Settings = GetMutableDefault<UGameplayTagsSettings>();
        if (Settings)
        {
            // 在这里，你可以通过代码向 Settings->GameplayTagList 添加预定义的角色 Tag
            // 例如： FGameplayTag MyCameramanTag = FGameplayTag::RequestGameplayTag(FName("Role.Cameraman"));
            // 但更常见的做法是通过VPRoles的编辑器UI来管理。
            UE_LOG(LogTemp, Log, TEXT("MyRolesExtension: Tag source registered."));
        }
    }
}

void FMyRolesExtensionModule::UnregisterCustomTagSource()
{
    // 清理逻辑
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyRolesExtensionModule, MyRolesExtension)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 提供 Gameplay Tags 核心框架，用于定义和查询角色标签。 |
| `GameplayTagsEditor` | 提供 Gameplay Tags 的编辑器 UI 组件（如 `SGameplayTagWidget`），被本插件的编辑器模块复用。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将标准日志宏迁移到新的 `UE_LOGF` 宏，属于代码维护性更新。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了前一次提交中错误的查找替换操作。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了之前一个导致问题的提交。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修改委托获取方式以修复引擎初始化时的注册问题。 |
| 2023-01-13 | `9d37f2ee` | Fixed non unity compile errors caused by integration from RES. Errors were reported by farm | 修复了非统一构建模式下的编译错误。 |

### 维护评价

该插件创建于2023年初，是实验性插件（`IsBetaVersion=true`，且默认隐藏 `Hidden=true`）。从提交记录看，自2023年1月初始创建后，其核心功能在近两年内没有实质性新增或修改。2026年的提交均为底层引擎API适配或编译错误修复等维护性工作，表明**插件功能已趋于稳定，但整体处于低维护状态**。

由于是实验性插件，且更新不活跃，建议在生产环境中谨慎使用，优先考虑其是否满足你特定的需求。它适合作为虚拟制作流程中角色管理概念的起点或参考。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProduction/VPRoles)
- [测试用例]（在提供的插件目录源码中未发现独立的测试文件）