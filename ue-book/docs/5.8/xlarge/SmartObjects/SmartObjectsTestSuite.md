# Smart Objects

> Support for ambient life populating the game world

| 属性 | 值 |
|---|---|
| 中文名 | 智能对象 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `SmartObjectsModule` (Runtime), `SmartObjectsEditorModule` (Runtime), `SmartObjectsTestSuite` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SmartObjects) | |

## 用途

SmartObjects 是一个通用的**场景资源标记与占用管理框架**。它允许设计师在关卡中放置带有特定标签和行为定义的"智能对象"，AI 角色或其他系统可以通过查询、筛选、占用/释放这些对象来驱动交互行为。

尽管 .uplugin 描述提到"ambient life"（环境生命体），但该插件实际上是一个**底层框架**，适用于任何需要场景交互点标记的场景，包括但不限于：

- NPC 日常行为（坐在长椅上、靠在吧台边、使用工作台）
- 任务交互点（拾取物品、打开箱子、操作机关）
- 载具/载具交互（上下车、驾驶位）
- 环境叙事点（查看告示牌、阅读书籍）

**核心概念**：
- **SmartObject Definition**：定义一个交互点的类型、可用插槽（Slot）、标签筛选条件和行为逻辑
- **SmartObject Instance**：关卡中放置的具体实例，关联一个 Definition
- **SmartObject Slot**：一个智能对象可以有多个插槽供不同使用者同时使用（如一个多人长椅有多个座位）
- **SmartObject Behavior Definition**：定义使用该对象时执行的具体行为（蓝图或 C++ 实现）
- **Claim / Release**：用户通过 Claim 占用插槽，使用完后 Release 释放

## 使用场景

- 你在做一个开放世界 RPG，需要 NPC 自动找到并使用场景中的互动点（坐下、工作、闲逛）→ 用 SmartObjects 标记这些点位，配合 AI 系统自动分配
- 你需要多个角色同时使用同一场景物件（如一张桌子有 4 个座位）→ 用 SmartObject Slot 管理多插槽
- 你想让设计师在编辑器中直观地放置交互点并配置标签，而不用在 C++ 中硬编码位置 → 用 SmartObject Actor + 编辑器工具
- 你在使用 Mass Entity 系统构建大量 AI 代理，需要将场景资源与 ECS 代理关联 → SmartObjects 支持 Mass Entity 集成

## 蓝图用法

### 核心类

| 类 | 说明 |
|---|---|
| `ASmartObject` | 关卡中放置的智能对象 Actor，包含一个 SmartObject Definition |
| `ASmartObjectPersistentCollection` | 持久化的智能对象集合，自动收集关卡中的 SmartObject |
| `USmartObjectSubsystem` | 核心子系统，管理所有注册的智能对象实例，提供查询和占用 API |
| `USmartObjectBehaviorDefinition` | 行为定义基类，蓝图可继承来定义具体交互行为 |
| `USmartObjectDefinition` | 智能对象定义资产，描述插槽布局、标签和行为 |

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindSmartObjects` | 根据查询条件查找可用的智能对象 | `USmartObjectSubsystem` |
| `ClaimSmartObject` | 占用一个智能对象的指定插槽 | `USmartObjectSubsystem` |
| `ReleaseSmartObjectClaim` | 释放对智能对象插槽的占用 | `USmartObjectSubsystem` |
| `GetSmartObjectComponent` | 获取智能对象组件 | `ASmartObject` |
| `GetSlotCount` | 获取智能对象定义中的插槽数量 | `USmartObjectDefinition` |
| `GetSlotState` | 获取指定插槽的当前状态（可用/已占用） | `USmartObjectSubsystem` |

### 使用示例

1. 在关卡中放置 `ASmartObject` Actor，在 Details 面板中指定 `SmartObjectDefinition` 资产
2. 在 Definition 资产中配置 Slot 位置、偏移和 Behavior Definition
3. 在 AI 蓝图中：先调用 `FindSmartObjects` 按标签/位置查询 → 从结果中选择一个 → 调用 `ClaimSmartObject` 占用 → 移动到 Slot 位置 → 执行交互行为 → 调用 `ReleaseSmartObjectClaim` 释放

## C++ 用法

### 头文件引入

```cpp
#include "SmartObjectSubsystem.h"
#include "SmartObjectDefinition.h"
#include "SmartObjectComponent.h"
#include "SmartObjectTypes.h"
```

### 基本用法：查询并占用智能对象

```cpp
// 获取 SmartObjectSubsystem
USmartObjectSubsystem& Subsystem = USmartObjectSubsystem::Get(GetWorld());

// 构建查询条件
FSmartObjectRequestFilter Filter;
Filter.ActivityTags.AddTag(FGameplayTag::RequestGameplayTag(TEXT("Activity.Sit")));

// 在指定区域内查找
FSmartObjectRequest Request;
Request.Filter = Filter;
Request.QueryBox = FBox(Origin - SearchExtent, Origin + SearchExtent);

TArray<FSmartObjectRequestResult> Results;
if (Subsystem.FindSmartObjects(Request, Results) && Results.Num() > 0)
{
    // 占用第一个找到的结果
    FSmartObjectRequestResult& Result = Results[0];
    FSmartObjectClaimHandle ClaimHandle = Subsystem.ClaimSmartObject(Result.SmartObjectHandle, Result.SlotHandle);
    
    if (ClaimHandle.IsValid())
    {
        // 移动到 Slot 位置...
        // 完成后释放
        Subsystem.ReleaseSmartObjectClaim(ClaimHandle);
    }
}
```

### 进阶用法：自定义 Behavior Definition

```cpp
// 定义自定义行为
UCLASS()
class USmartObjectSitBehavior : public USmartObjectBehaviorDefinition
{
    GENERATED_BODY()
    
public:
    UPROPERTY(EditAnywhere)
    UAnimMontage* SitMontage;
    
    UPROPERTY(EditAnywhere)
    float InteractionDuration = 5.0f;
    
    // 实现具体的交互逻辑
    virtual bool Activate(FSmartObjectExecutionContext& Context) const;
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 智能对象的标签过滤系统 |
| `GameplayAbilities`（可选） | 与 GAS 集成时需要 |
| `MassEntity`（可选） | Mass AI 代理的智能对象支持 |
| `MassNavigation`（可选） | Mass 导航集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移至 UE_LOGF |
| 2026-04-13 | `f10a2daf` | [ContentBrowser] New Add Menu AI Menu | 内容浏览器新增 AI 菜单 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | MassCore 头文件迁移并重命名 |
| 2026-03-31 | `d7c5497a` | [SmartObjects][Debug] Three-level debug rejection tracking in FindSlotsInternal and FindMatchingSlot | 增强查找槽位的三级调试拒绝追踪 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 从 MassEntity 提取 MassCore 模块 |

### 维护评价

SmartObjects 插件处于**活跃维护**状态。从 2021 年创建至今持续有实质性更新，近期（2026 年 3-4 月）仍在积极改进核心功能（如调试追踪增强）和适配 UE5 架构变化（Mass 模块重构）。

该插件虽默认未启用（`EnabledByDefault=false`），但已从早期的 Experimental 状态成熟化，是 Mass AI 生态的关键组成部分。**推荐在需要场景交互管理的项目中使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SmartObjects)
- [官方文档]()（暂无）