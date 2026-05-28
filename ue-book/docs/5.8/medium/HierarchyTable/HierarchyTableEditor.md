# Hierarchy Table

> （Description 为空，以下基于源码分析）

| 属性 | 值 |
|---|---|
| 中文名 | 层级表编辑器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产定义、工厂类） |
| 模块 | `HierarchyTableRuntime` (Runtime), `HierarchyTableEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/HierarchyTable) | |

## 用途

HierarchyTable 是一个**通用层级表资产编辑框架**，用于在 UE5 编辑器中创建、编辑和管理带有树形层级结构的表格数据资产。

该插件解决的核心问题是：动画系统（如 Blend Profiles、骨骼层级映射等）需要一种标准化的方式来管理**父子层级关系 + 每个节点可携带自定义数据**的资产。传统 DataTable 是扁平结构，无法表达层级；而 HierarchyTable 通过树形视图 + 可扩展的列系统，填补了这一空白。

插件采用了高度可扩展的架构：
- **TableTypeHandler** 机制允许不同类型的层级表定义自己的构建逻辑、工具栏按钮和右键菜单
- **IHierarchyTableColumn** 接口允许按元素类型注册自定义列（如 Float 列）
- 编辑器 UI 基于 STreeView，支持拖拽重排父子关系

## 使用场景

- 你需要创建和编辑**骨骼层级权重表**（Blend Profiles）→ 用 HierarchyTable
- 你需要管理一个**带有父子关系的属性映射表**（如动画重定向的骨骼映射）→ 用 HierarchyTable
- 你需要一个通用的**树形结构资产**，每个节点携带自定义浮点值或其他数据 → 用 HierarchyTable
- 你需要为动画系统扩展自定义的层级数据资产类型 → 继承 `UHierarchyTable_TableTypeHandler` 并注册

## 蓝图用法

该插件主要面向编辑器扩展，运行时蓝图 API 较少。编辑器功能通过模块接口暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateHierarchyTableWidget` | 创建层级表编辑器 Slate 控件 | `FHierarchyTableEditorModule` |
| `CreateTableHandler` (by table) | 根据已有资产创建表处理器 | `FHierarchyTableEditorModule` |
| `CreateTableHandler` (by type) | 根据表类型创建表处理器 | `FHierarchyTableEditorModule` |
| `RegisterTableType` | 注册新的表类型及其处理器类 | `FHierarchyTableEditorModule` |
| `UnregisterTableType` | 注销表类型 | `FHierarchyTableEditorModule` |
| `RegisterElementTypeEditorColumns` | 为元素类型注册自定义编辑器列 | `FHierarchyTableEditorModule` |
| `UnregisterElementTypeEditorColumns` | 注销元素类型的编辑器列 | `FHierarchyTableEditorModule` |

### 使用示例（编辑器扩展描述）

1. **创建资产**：右键 Content Browser → Animation 分类下找到 Hierarchy Table 资产类型，创建时会弹出配置面板选择 TableType 和 ElementType
2. **编辑资产**：双击打开后，左侧为树形视图展示层级结构，右侧为可配置列（如 Float 值列），支持拖拽调整父子关系
3. **注册自定义类型**：在模块启动时调用 `RegisterTableType()` 和 `RegisterElementTypeEditorColumns()` 扩展新的层级表类型

## C++ 用法

### 头文件引入

```cpp
#include "HierarchyTableEditorModule.h"
#include "HierarchyTableTypeHandler.h"
#include "IHierarchyTableColumn.h"
```

### 基本用法 - 注册自定义表类型处理器

```cpp
// 在你的 Editor 模块 StartupModule 中注册自定义表类型
// 来源: Public/HierarchyTableEditorModule.h

// 1. 创建一个自定义的 TableTypeHandler
UCLASS()
class UMyTableTypeHandler : public UHierarchyTable_TableTypeHandler
{
    GENERATED_BODY()
public:
    // 重写以提供创建时的额外配置属性
    virtual bool FactoryConfigureProperties(FInstancedStruct& TableType) const override
    {
        // 返回 true 表示需要用户配置属性
        return true;
    }

    // 重写以添加工具栏按钮
    virtual void ExtendToolbar(UToolMenu* ToolMenu, IHierarchyTable& HierarchyTableView) const override
    {
        // 自定义工具栏扩展
    }

    // 重写以自定义右键菜单
    virtual void ExtendContextMenu(FMenuBuilder& MenuBuilder, IHierarchyTable& HierarchyTableView) const override
    {
        // 自定义右键菜单项
    }

    // 提供条目图标
    virtual FSlateIcon GetEntryIcon(const int32 EntryIndex) const override
    {
        return FSlateIcon(FAppStyle::GetAppStyleSetName(), "ClassIcon.Actor");
    }

    // 构建层级结构
    virtual void ConstructHierarchy() override
    {
        // 根据当前表元数据重置并构建层级数据
    }

    virtual bool CanRenameEntry(const int32 EntryIndex) const override { return true; }
    virtual bool CanRemoveEntry(const int32 EntryIndex) const override { return true; }
};
```

### 注册自定义编辑器列

```cpp
// 来源: Private/FloatColumn.h, Public/IHierarchyTableColumn.h

// 实现 IHierarchyTableColumn 接口以创建自定义列
struct FMyColumn : public IHierarchyTableColumn
{
    virtual FName GetColumnId() const override { return FName("MyColumn"); }
    virtual FText GetColumnLabel() const override { return LOCTEXT("MyColumnLabel", "My Value"); }
    virtual float GetColumnSize() const override { return 1.0f; }

    virtual TSharedRef<SWidget> CreateEntryWidget(TObjectPtr<UHierarchyTable> HierarchyTable, int32 EntryIndex) override
    {
        // 创建编辑该条目数据的控件
        return SNew(STextBlock).Text(FText::AsNumber(EntryIndex));
    }

    virtual TSharedRef<SWidget> CreateHeaderWidget() override
    {
        return SNew(STextBlock).Text(LOCTEXT("MyColumnHeader", "My Value"));
    }
};

// 在 StartupModule 中注册
void FMyEditorModule::StartupModule()
{
    FHierarchyTableEditorModule& HierarchyModule = FModuleManager::LoadModuleChecked<FHierarchyTableEditorModule>("HierarchyTableEditor");

    // 注册表类型
    HierarchyModule.RegisterTableType(FMyTableType::StaticStruct(), UMyTableTypeHandler::StaticClass());

    // 注册自定义列
    TArray<TSharedPtr<IHierarchyTableColumn>> Columns;
    Columns.Add(MakeShared<FMyColumn>());
    HierarchyModule.RegisterElementTypeEditorColumns(UMyElementType::StaticStruct(), Columns);
}
```

### 进阶用法 - 编程式创建层级表资产

```cpp
// 来源: Public/HierarchyTableFactory.h
// 工厂类支持通过对话框配置 TableType 和 ElementType

UHierarchyTableFactory Factory;
// 配置 TableMetadata 和 ElementType 后调用
// Factory.FactoryCreateNew(UHierarchyTable::StaticClass(), Parent, Name, Flags, Context, Warn);
```

## Demo 示例

### 自定义层级表类型（最小完整示例）

```cpp
// MyHierarchyTableHandler.h
#pragma once

#include "HierarchyTableTypeHandler.h"
#include "MyHierarchyTableHandler.generated.h"

UCLASS()
class UMyHierarchyTableHandler : public UHierarchyTable_TableTypeHandler
{
    GENERATED_BODY()

public:
    virtual void ConstructHierarchy() override
    {
        // 根据 HierarchyTable 的元数据重建层级
        // HierarchyTable 成员变量来自父类
        if (!HierarchyTable) return;

        // 自定义层级构建逻辑
    }

    virtual bool CanRenameEntry(const int32 EntryIndex) const override { return true; }
    virtual bool CanRemoveEntry(const int32 EntryIndex) const override { return true; }

    virtual FSlateIcon GetEntryIcon(const int32 EntryIndex) const override
    {
        return FSlateIcon(FAppStyle::GetAppStyleSetName(), "ClassIcon.Blueprint");
    }

    virtual void ExtendContextMenu(FMenuBuilder& MenuBuilder, IHierarchyTable& HierarchyTableView) const override
    {
        MenuBuilder.BeginSection("MySection", LOCTEXT("MySection", "Custom Actions"));
        MenuBuilder.AddMenuEntry(
            LOCTEXT("MyAction", "My Custom Action"),
            LOCTEXT("MyActionTooltip", "Perform a custom action"),
            FSlateIcon(),
            FUIAction()
        );
        MenuBuilder.EndSection();
    }
};
```

```cpp
// MyHierarchyTableColumn.h
#pragma once

#include "IHierarchyTableColumn.h"
#include "HierarchyTable.h"
#include "Widgets/Input/SSpinBox.h"

struct FHierarchyTableColumn_MyFloat : public IHierarchyTableColumn
{
    virtual FName GetColumnId() const override { return FName("MyFloat"); }
    virtual FText GetColumnLabel() const override { return LOCTEXT("MyFloatLabel", "Weight"); }
    virtual float GetColumnSize() const override { return 1.0f; }

    virtual TSharedRef<SWidget> CreateEntryWidget(TObjectPtr<UHierarchyTable> HierarchyTable, int32 EntryIndex) override
    {
        // 根据实际数据类型创建对应的编辑控件
        return SNew(SSpinBox<float>)
            .MinValue(0.0f)
            .MaxValue(1.0f);
    }

    virtual TSharedRef<SWidget> CreateHeaderWidget() override
    {
        return SNew(STextBlock).Text(LOCTEXT("WeightHeader", "Weight"));
    }
};
```

## 模块依赖

该插件的 Build.cs 依赖信息未完整提供，但从头文件分析可推断以下独特依赖：

| 模块 | 用途 |
|---|---|
| `AssetDefinition` | 资产定义框架（UAssetDefinitionDefault 基类） |
| `ToolMenus` | 工具栏和菜单扩展 |
| `StructUtils` | FInstancedStruct 支持 |
| `AppStyle` | 编辑器样式和图标 |

其他为标准 Core/Engine/Slate/Editor 等常见依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `c19c7e83` | [ContentBrowser] New Add Menu Misc Menu | ContentBrowser 菜单结构调整，影响资产创建入口 |
| 2026-03-18 | `50b37fba` | [iOS/macOS] Fixes for Clang 21 implicit conversion warnings. | 修复 Clang 21 编译器隐式转换警告 |
| 2026-03-04 | `d9a06590` | Update UAF blend profiles | 更新 UAF 混合配置文件，涉及 HierarchyTable 功能使用 |
| 2025-11-06 | `e75a5dce` | Move hierarchy table from animation category to misc. | 将层级表资产类别从 Animation 移至 Misc |
| 2025-09-08 | `7c9e306e` | Add live updating blend mask weights in the Profile Blend node | Profile Blend 节点支持实时更新混合蒙版权重 |

### 维护评价

- **状态**：实验性插件，仍在活跃维护中
- **年龄**：约 2 年（2024-07-30 创建），相对较新
- **更新频率**：约每 2-3 个月有相关提交，多为编译修复和功能适配
- **实验性**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需要手动启用
- **注意事项**：API 可能在版本间发生变化，生产环境使用需谨慎
- **推荐程度**：如果你需要层级表资产编辑功能（如动画 Blend Profile），这是官方推荐的框架；但作为实验性插件，建议关注后续 API 变更

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/HierarchyTable)
- 官方文档：暂无
- 测试用例：暂未发现独立测试文件