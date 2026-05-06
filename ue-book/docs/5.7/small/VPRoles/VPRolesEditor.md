# Virtual Production Roles

> Allows users to manage Virtual Production Role assignment.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟制作角色管理 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资源、图标等） |
| 模块 | `VPRoles` (Runtime), `VPRolesEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-12 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProduction/VPRoles) | |

## 用途

该插件为虚拟制作流程中的角色管理提供基础设施。在电影、电视剧或实时虚拟制作中，不同团队成员（导演、摄影师、灯光师等）需要分配特定角色，以便根据角色控制场景元素（如摄像机、灯光、演员等）。插件基于 GameplayTags 系统实现角色的定义、存储和编辑器支持，允许用户在编辑器或运行时为对象分配角色标签。

- **VPRoles（运行时模块）**：提供角色标签的存储、获取和查询功能（如 `IVPRolesSubsystem`）。
- **VPRolesEditor（运行时/编辑器模块）**：在编辑器工具栏中添加“VP Roles”下拉菜单，嵌入 GameplayTag 小部件，方便用户管理角色标签的添加、删除和查看，同时监听标签源文件变化，确保角色列表及时更新。

## 使用场景

- 在虚拟制作项目中，你需要为不同岗位分配角色（如 Director、Camera Operator、Grip），并根据角色控制 Actor 的行为（例如只有“Director”角色的用户才能移动主摄像机）。
- 你正在搭建一套多用户协作的虚拟制作管线，希望基于角色而非用户个体来定义权限或功能。
- 你需要一个可扩展的角色标签系统，能够通过配置文件或编辑界面对角色进行增删改，并实时生效。

## 蓝图用法

VPRolesEditor 模块不直接暴露蓝图可调用节点（其功能围绕编辑器 UI 展开）。角色数据的读写建议通过运行时模块 `VPRoles` 的子系统实现（`UVPSubsystem` 或 `IVPRolesSubsystem`，需查阅对应模块头文件）。  
若需在蓝图/脚本中获取当前角色列表或检查角色，可参考以下节点（源自 `VPRoles` 运行时模块）：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Current Role Selections` | 获取当前所有激活的角色标签 | 位于相关子系统 |
| `Has Role` | 检查是否拥有指定角色 | 同上 |

> ⚠️ 具体节点名称和签名请通过蓝图右键菜单搜索 `VP Role` 或检查插件运行时模块文档。

## C++ 用法

### 头文件引入

```cpp
#include "VPRolesEditorModule.h"
#include "VPRolesEditorStyle.h"
```

### 基本用法

`VPRolesEditorModule` 在模块启动时自动注册编辑器扩展，通常无需手动调用。若需要在其他编辑器模块中检测角色标签的编辑状态，可通过模块接口获取：

```cpp
// 获取 VPRolesEditor 模块（通常用于注册自定义 UI，非必须）
FVPRolesEditorModule& VPRolesEditorModule = FModuleManager::LoadModuleChecked<FVPRolesEditorModule>("VPRolesEditor");

// 获取样式集，用于自定义 Slate UI
const ISlateStyle& VPRolesStyle = FVPRolesEditorStyle::Get();
```

### 进阶用法

VPRolesEditor 暴露了 `ExtendLevelEditorToolbar` 等内部方法，但通常不供外部直接调用。若需集成角色管理小部件到自定义 UI，可参考以下思路（来自模块源码）：

```cpp
// 生成 GameplayTag 小部件（内部方法，仅示例用法）
TSharedRef<SWidget> TagWidget = FVPRolesEditorModule::Get().GenerateGameplayTagWidget();

// 将小部件嵌入你的面板
SNew(SVerticalBox)
+ SVerticalBox::Slot()
.AutoHeight()
[
    TagWidget
];
```

> 注意：`GenerateGameplayTagWidget` 为私有方法，不建议外部直接引用。更推荐通过 `GameplayTags` 模块的公共 API 构建相似 UI。

## Demo 示例

由于该插件主要提供编辑器基础设施，以下是一个最小 C++ 模块示例，演示如何在自定义编辑器中检测 VPRoles 的 tag 源文件变化：

```cpp
// MyCustomRoleHandler.h
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyCustomRoleHandler
{
public:
    void OnRoleFileChanged();
};
```

```cpp
// MyCustomRoleHandler.cpp
#include "MyCustomRoleHandler.h"
#include "VPRolesEditorModule.h"

void FMyCustomRoleHandler::OnRoleFileChanged()
{
    // 监听 VPRoles 默认 tag 源文件变化（需从模块获取路径）
    FVPRolesEditorModule& Module = FModuleManager::LoadModuleChecked<FVPRolesEditorModule>("VPRolesEditor");
    // 模块内部使用文件监视器，此处仅示意
    UE_LOG(LogTemp, Log, TEXT("VP Role config file likely changed, consider refreshing."));
}
```

完整示例需编写一个独立模块并包含必要的构建依赖。

## 模块依赖

VPRolesEditor 无特殊依赖（仅标准 Core/Engine/Slate/GameplayTagsEditor 等常见模块）。  
若需使用 VPRoles 运行时子系统，需额外依赖 `VPRoles` 模块（其本身依赖 `GameplayTags`）。

| 模块 | 用途 |
|---|---|
| `VPRoles` (运行时) | 提供角色标签的运行时存储与查询 |
| `GameplayTags` | 底层标签系统 |
| `GameplayTagsEditor` | 用于生成 GameplayTag 小部件 |

## 维护状态

### 近期更新

- 2023-01-13 `9d37f2ee` 修复因集成 RES 导致的非 Unity 编译错误（由农场报告）
- 2023-01-12 `be1992fa` 将 VPSettings 和 VPRoles 移入独立模块/插件

### 维护评价

该插件创建于 2023 年 1 月，此后仅有一次编译修复提交，无功能性更新。考虑到其标记为 `IsBetaVersion=true` 且默认隐藏，目前可能处于维护不活跃状态。但在现有虚拟制作管线中仍可使用，基础功能（角色标签管理）完整。因无后续迭代，建议审慎评估是否适用于最新引擎版本，并关注可能的兼容性变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProduction/VPRoles)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/virtual-production-roles/)（如果存在，但 .uplugin 中未提供）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProduction/VPRoles/Tests)（如果存在）