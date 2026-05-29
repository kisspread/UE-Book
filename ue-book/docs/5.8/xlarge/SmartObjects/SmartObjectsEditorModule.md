# Smart Objects Editor Module

> Support for ambient life populating the game world

| 属性 | 值 |
|---|---|
| 中文名 | 智能对象编辑器 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `SmartObjectsModule` (Runtime), `SmartObjectsEditorModule` (Runtime), `SmartObjectsTestSuite` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SmartObjects) | |

## 用途

SmartObjects（智能对象）插件提供了一套框架，用于在游戏世界中定义和管理可交互的空间位置，供 AI 代理（如 NPC）自动发现和使用。核心思想是：场景中的物体（如长椅、自动贩卖机、吧台）可以声明自己拥有哪些"槽位"（Slot），每个槽位描述了一种交互行为及其空间位置，AI 系统可以根据需求查询并占用这些槽位。

`SmartObjectsEditorModule` 专门负责**资产编辑器**的实现——为 `USmartObjectDefinition` 资产提供可视化的 3D 预览编辑环境，包含槽位管理、Gizmo 操作、大纲视图等功能。

**解决了什么问题？**
- 传统做法需要手动放置 Trigger Volume 或用 Gameplay Tag 来标记可用交互点，维护困难且不够直观
- SmartObjects 将交互定义封装为独立资产（`USmartObjectDefinition`），可在编辑器中可视化配置槽位位置、朝向、关联数据
- 为 Mass AI / StateTree 等系统提供标准化的查询接口

## 使用场景

- 你在做一个有大量 NPC 日常行为的开放世界游戏 → 用 SmartObjects 定义"坐下"、"靠墙站"、"使用机器"等交互点
- 你需要让 AI 自动寻找并占用场景中的可用位置 → SmartObjectSubsystem 提供 Find/Claim/Release 接口
- 你希望美术能在编辑器中直接预览和调整交互槽位的位置 → 本模块提供的资产编辑器
- 你使用 Mass Entity 框架做大规模 AI → SmartObjects 与 Mass 系统深度集成

## 蓝图用法

本模块（SmartObjectsEditorModule）是编辑器模块，不直接暴露运行时蓝图 API。运行时功能由 `SmartObjectsModule` 提供。

### 编辑器内资产编辑

通过 `USmartObjectDefinition` 资产双击打开专用编辑器：

| 功能 | 说明 |
|---|---|
| 3D 预览场景 | 带高级预览光照的 3D 视口，可设置预览网格体或 Actor |
| 大纲视图（Outliner） | 树状结构显示所有槽位，支持拖拽重排序 |
| 详情面板（Details） | 查看/编辑选中槽位的属性和参数 |
| Gizmo 操控 | 直接在 3D 视口中移动/旋转槽位变换 |
| 预览设置 | 选择用于预览的静态网格体或 Actor 模板 |

### 资产类型自定义

`FSmartObjectDefinitionReferenceDetails` 为 `FSmartObjectDefinitionReference` 类型提供自定义属性面板：
- 自动同步 Definition 资产中定义的参数
- 槽位引用（`FSmartObjectSlotReference`）提供下拉选择器

## C++ 用法

### 头文件引入

```cpp
#include "SmartObjectsEditorModule.h"
```

### 基本用法 - 检查模块可用性

```cpp
// SmartObjectsEditorModule.h
if (ISmartObjectEditorModule::IsAvailable())
{
    ISmartObjectEditorModule& EditorModule = ISmartObjectEditorModule::Get();
}
```

### 自定义资产编辑器

```cpp
// SmartObjectAssetEditor.h
UCLASS(Transient)
class USmartObjectAssetEditor : public UAssetEditor
{
    GENERATED_BODY()
public:
    void SetObjectToEdit(UObject* InObject);
protected:
    virtual void GetObjectsToEdit(TArray<UObject*>& OutObjectsToEdit) override;
    virtual TSharedPtr<FBaseAssetToolkit> CreateToolkit() override;
};
```

创建资产编辑器的基本流程：

```cpp
// 创建编辑器实例
USmartObjectAssetEditor* AssetEditor = NewObject<USmartObjectAssetEditor>();
AssetEditor->SetObjectToEdit(MySmartObjectDefinition);
// 内部会创建 FSmartObjectAssetToolkit
```

### ViewModel 用于选中状态管理

```cpp
// SmartObjectViewModel.h
// 注册 ViewModel
TSharedPtr<FSmartObjectViewModel> ViewModel = FSmartObjectViewModel::Register(MyDefinition);

// 管理选中
ViewModel->SetSelection({SlotGuid1, SlotGuid2});
ViewModel->AddToSelection(NewSlotGuid);
bool bSelected = ViewModel->IsSelected(SomeSlotGuid);
TConstArrayView<FGuid> CurrentSelection = ViewModel->GetSelection();

// 监听选中变化
ViewModel->GetOnSelectionChanged().AddLambda([](TConstArrayView<FGuid> Selection) {
    // 处理选中变化
});

// 槽位操作
FGuid NewSlotID = ViewModel->AddSlot(InsertAfterID);
ViewModel->MoveSlot(SourceID, TargetID);
ViewModel->RemoveSlot(SlotToRemove);
```

### 世界分区构建器

```cpp
// WorldPartitionSmartObjectCollectionBuilder.h
// 收集世界中的所有智能对象组件到集合中
bool bCanBuild = UWorldPartitionSmartObjectCollectionBuilder::CanBuildCollections(World, BuildOption);
EEditorBuildResult Result = UWorldPartitionSmartObjectCollectionBuilder::BuildCollections(World, BuildOption);
```

## Demo 示例

```cpp
// MySmartObjectEditorExtension.h
#pragma once

#include "CoreMinimal.h"
#include "SmartObjectDefinition.h"
#include "SmartObjectViewModel.h"

class FMySmartObjectEditorHelper
{
public:
    /** 创建一个 SmartObject 定义并设置基本槽位 */
    static USmartObjectDefinition* CreateSimpleDefinition(UObject* Outer)
    {
        USmartObjectDefinition* Definition = NewObject<USmartObjectDefinition>(Outer);
        if (!Definition) return nullptr;

        // 注册 ViewModel 来操作定义
        TSharedPtr<FSmartObjectViewModel> ViewModel = FSmartObjectViewModel::Register(Definition);
        
        // 添加一个槽位
        FGuid SlotID = ViewModel->AddSlot(FGuid());
        
        // 设置选中
        ViewModel->SetSelection({SlotID});
        
        // 完成后取消注册
        ViewModel->Unregister();
        
        return Definition;
    }

    /** 监听定义变化的示例 */
    static void SetupChangeTracking(USmartObjectDefinition* Definition)
    {
        TSharedPtr<FSmartObjectViewModel> ViewModel = FSmartObjectViewModel::Get(Definition);
        if (ViewModel.IsValid())
        {
            ViewModel->GetOnSlotsChanged().AddLambda([](USmartObjectDefinition* ChangedDef)
            {
                UE_LOG(LogTemp, Log, TEXT("Definition slots changed: %s"), *ChangedDef->GetName());
            });
        }
    }
};
```

## 模块依赖

从 Build.cs 分析，SmartObjectsEditorModule 的依赖：

| 模块 | 用途 |
|---|---|
| `SmartObjectsModule` | 核心运行时模块，提供 SmartObject 定义、组件、子系统等基础类型 |
| `AdvancedPreviewScene` | 高级 3D 预览场景（编辑器预览用） |
| `LevelEditor` | 关卡编辑器集成 |
| `PropertyEditor` | 属性面板自定义 |
| `ComponentVisualizers` | 组件可视化器框架 |

> SmartObjectsTestSuite 模块额外依赖 `EditorFramework` 和 `UnrealEd`（仅用于测试）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新格式 |
| 2026-04-13 | `f10a2daf` | [ContentBrowser] New Add Menu AI Menu | 内容浏览器新增 AI 菜单分类 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | MassCore 头文件目录重构 |
| 2026-03-31 | `d7c5497a` | [SmartObjects][Debug] Three-level debug rejection tracking in FindSlotsInternal and FindMatchingSlot | 新增三级调试拒绝追踪，用于槽位查找调试 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 从 MassEntity 抽取 MassCore 模块 |

### 维护评价

**活跃维护** 🟢

- 创建于 2021 年 9 月，约 5 年历史，目前仍在积极开发
- 最近的提交集中在调试增强（三级拒绝追踪）和 Mass 系统深度集成
- 插件默认未启用（`EnabledByDefault=false`），表明 Epic 将其视为可选高级功能
- 随 UE5 版本持续迭代，从 Experimental 迁移到正式 Runtime 目录
- 与 StateTree、Mass AI 等新系统紧密耦合，是 Epic 新一代 AI 框架的重要组成部分
- **推荐使用**：适合需要标准化 AI 交互点管理的项目，尤其是使用 Mass Entity 框架的大型项目

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SmartObjects)
- 官方文档：无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SmartObjects/Source/SmartObjectsTestSuite)