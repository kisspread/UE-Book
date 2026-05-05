# Object Mixer

> Edit any properties of scene objects in a spreadsheet format!

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器样式资产） |
| 模块 | `ObjectMixerEditor` (Editor), `LightMixer` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-23 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ObjectMixer) | |

## 用途

Object Mixer 是一个**电子表格式的场景对象属性编辑器**。它解决的核心问题是：当你需要同时修改大量同类对象（比如 50 盏灯的强度或颜色）时，逐个点击 Actor 打开 Details 面板效率极低。Object Mixer 提供了一个类似 Excel 的列表视图，将所有匹配的对象按行排列，将属性按列排列，让你可以**批量查看和编辑**场景中对象的属性。

Plugin 采用**可扩展的 Filter 架构**：核心框架负责 UI 和数据绑定，具体过滤哪些对象类型由 `UObjectMixerObjectFilter` 子类决定。LightMixer 就是基于此架构构建的第一个具体实现——专门编辑灯光对象。

## 使用场景

- 你有 50 盏灯需要统一调整 Intensity 或 LightColor → 用 LightMixer
- 你需要快速对比同一类对象的某个属性值（比如所有 PostProcessVolume 的 Exposure） → 创建自定义 Object Filter
- 你需要在一个表格视图中批量修改场景对象的属性，而不是逐个打开 Details → 用 ObjectMixer
- 你需要管理用户集合（Collections），对特定对象分组操作 → ObjectMixer 内置 Collections 功能

## 蓝图用法

ObjectMixer 主要是编辑器工具，不直接暴露蓝图节点用于运行时。但它的 Filter 系统支持蓝图扩展。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetObjectClassesToFilter` | 返回要过滤的对象类型集合 | `UObjectMixerBlueprintObjectFilter` |
| `GetObjectClassesToPlace` | 返回可通过 Add 按钮放置的 Actor 类型 | `UObjectMixerBlueprintObjectFilter` |
| `GetColumnsToShowByDefault` | 指定默认显示的属性列 | `UObjectMixerBlueprintObjectFilter` |
| `GetColumnsToExclude` | 指定永远不显示的属性列 | `UObjectMixerBlueprintObjectFilter` |
| `GetForceAddedColumns` | 强制显示来自父类的属性列 | `UObjectMixerBlueprintObjectFilter` |
| `GetShowTransientObjects` | 是否显示临时对象（如 Sequencer Spawnables） | `UObjectMixerBlueprintObjectFilter` |
| `GetObjectMixerPropertyInheritanceInclusionOptions` | 控制属性继承范围 | `UObjectMixerBlueprintObjectFilter` |
| `ShouldIncludeUnsupportedProperties` | 是否显示不受支持的属性 | `UObjectMixerBlueprintObjectFilter` |
| `GetPropertiesThatRequireListRefresh` | 属性变更后需要刷新列表的属性名 | `UObjectMixerBlueprintObjectFilter` |

### 使用示例（蓝图描述）

**创建蓝图 Filter**：

1. 在 Content Browser 右键 → Blueprints → Object Mixer Blueprint Filter
2. 打开蓝图，Override `GetObjectClassesToFilter`，返回你想编辑的对象类型（如 `UStaticMeshComponent`）
3. Override `GetColumnsToShowByDefault`，返回默认显示的属性名（如 `"StaticMesh"`, `"bVisible"`）
4. Override `GetObjectMixerPropertyInheritanceInclusionOptions`，选择继承策略
5. 保存编译后，在 Object Mixer 窗口的 Filter 选择器中勾选该 Filter

## C++ 用法

### 头文件引入

```cpp
#include "ObjectFilter/ObjectMixerEditorObjectFilter.h"
#include "ObjectMixerEditorModule.h"
```

### 基本用法——创建自定义 Object Filter

核心方式是继承 `UObjectMixerObjectFilter` 并 override 虚函数。以下示例来自 `LightMixerObjectFilter`：

```cpp
// 来源: LightMixer/Source/LightMixer/Public/LightMixerObjectFilter.h

UCLASS(MinimalAPI, BlueprintType, EditInlineNew)
class UMyCustomObjectFilter : public UObjectMixerObjectFilter
{
    GENERATED_BODY()
public:
    // 要过滤的对象类型（组件类）
    virtual TSet<UClass*> GetObjectClassesToFilter() const override
    {
        return { UStaticMeshComponent::StaticClass() };
    }

    // 可通过 Add 按钮放置的 Actor 类型
    virtual TSet<TSubclassOf<AActor>> GetObjectClassesToPlace() const override
    {
        return { AStaticMeshActor::StaticClass() };
    }

    // 默认显示的属性列
    virtual TSet<FName> GetColumnsToShowByDefault() const override
    {
        return { "StaticMesh", "bVisible", "Mobility" };
    }

    // 从父类强制添加的属性列
    virtual TSet<FName> GetForceAddedColumns() const override
    {
        return {};
    }

    // 属性继承策略
    virtual EObjectMixerInheritanceInclusionOptions
    GetObjectMixerPropertyInheritanceInclusionOptions() const override
    {
        return EObjectMixerInheritanceInclusionOptions::IncludeAllParentsAndChildren;
    }

    // 是否显示临时对象
    virtual bool GetShowTransientObjects() const override
    {
        return false;
    }
};
```

### 进阶用法——以编程方式打开 Object Mixer

```cpp
#include "ObjectMixerEditorModule.h"

// 获取模块实例
FObjectMixerEditorModule& Module = FObjectMixerEditorModule::Get();

// 创建 Object Mixer 对话框 Widget，指定默认 Filter
TSharedPtr<SWidget> MixerWidget = Module.MakeObjectMixerDialog(
    UMyCustomObjectFilter::StaticClass()
);

// 或者注册自定义 Tab Spawner
Module.RegisterTabSpawner();
```

### 进阶用法——扩展子模块（如 LightMixer）

LightMixer 展示了如何创建一个完整的子模块。关键是：

1. 创建 `.uplugin`，声明依赖 `ObjectMixer` plugin
2. 创建 `Module` 类继承 `FObjectMixerEditorModule`，设置菜单项名称/图标/Tooltip
3. 创建 `ObjectFilter` 类继承 `UObjectMixerObjectFilter`
4. 重写 `GetDefaultFilterClass()` 返回你的 Filter 类

```cpp
// 来源: LightMixer/Source/LightMixer/Public/LightMixerModule.h
class FLightMixerModule : public FObjectMixerEditorModule
{
    // 设置 Tab 标签、菜单项名称、图标等
    // 重写 GetDefaultFilterClass() 返回 ULightMixerObjectFilter
};
```

## Demo 示例

### 最小自定义 Filter（C++）

**MyMixerFilter.h**
```cpp
#pragma once
#include "ObjectFilter/ObjectMixerEditorObjectFilter.h"
#include "MyMixerFilter.generated.h"

UCLASS(BlueprintType, EditInlineNew)
class UMyMixerFilter : public UObjectMixerObjectFilter
{
    GENERATED_BODY()
public:
    virtual TSet<UClass*> GetObjectClassesToFilter() const override
    {
        return { AActor::StaticClass() };
    }

    virtual TSet<FName> GetColumnsToShowByDefault() const override
    {
        return { "ActorLabel" };
    }
};
```

**Build.cs 依赖**
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "ObjectMixerEditor",
    "PropertyEditor"
});
```

## 模块依赖

### ObjectMixerEditor（核心模块）

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和容器 |
| `OutputLog` | 输出日志 |
| `PropertyEditor` | 属性编辑器集成 |
| `SceneOutliner` | Scene Outliner 框架（ObjectMixer 基于此构建） |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `Slate` / `SlateCore` | UI 框架 |
| `UnrealEd` | 编辑器功能 |
| `LevelEditor` | 关卡编辑器集成 |
| `Sequencer` / `LevelSequence` | Sequencer 集成 |
| `ToolMenus` | 菜单系统 |
| `TypedElementFramework` / `TypedElementRuntime` | 类型化元素框架 |
| `SourceControl` | 源代码管理集成 |
| `EditorConfig` | 编辑器配置持久化 |

### LightMixer（子模块）

| 模块 | 用途 |
|---|---|
| `ObjectMixerEditor` | ObjectMixer 核心框架 |
| `Core` | 基础类型 |
| `PropertyEditor` | 属性编辑 |

## 架构概览

ObjectMixer 的核心架构如下：

```
┌─────────────────────────────────────────────┐
│           FObjectMixerEditorModule           │  ← 模块入口，管理 Tab Spawner
├─────────────────────────────────────────────┤
│           FObjectMixerEditorList             │  ← 数据模型，管理 Filter 实例和列表状态
├─────────────────────────────────────────────┤
│        FObjectMixerOutlinerMode              │  ← Scene Outliner 模式，处理选择/拖放/过滤
├─────────────────────────────────────────────┤
│        SObjectMixerEditorList                │  ← Slate Widget，电子表格 UI
├─────────────────────────────────────────────┤
│       UObjectMixerObjectFilter               │  ← 抽象 Filter 基类（用户继承此类）
│  ┌──────────────┐  ┌─────────────────────┐  │
│  │ ULightMixer  │  │ UMyCustomFilter     │  │
│  │ ObjectFilter │  │ (用户自定义)         │  │
│  └──────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────┘
```

**关键类说明**：

- **`UObjectMixerObjectFilter`**：抽象基类，定义了"过滤哪些对象"、"显示哪些列"、"继承策略"等接口。C++ 类直接继承此类。
- **`UObjectMixerBlueprintObjectFilter`**：蓝图可继承版本，将所有虚函数标记为 `BlueprintNativeEvent`。
- **`FObjectMixerEditorList`**：数据模型层，管理 Filter 实例的生命周期、性能缓存、Collections、Solo 模式。
- **`FObjectMixerOutlinerMode`**：继承自 `FActorMode`，是 Scene Outliner 的自定义模式，处理选择同步、拖放、文件夹管理。
- **`UObjectMixerEditorSerializedData`**：持久化数据，保存 Collections 和列显示配置到 `ObjectMixerSerializedData.ini`。
- **`UObjectMixerEditorSettings`**：用户设置，包括选择同步和 Hybrid Row 策略。
- **`IObjectMixerSelectionInterface`**：选择同步接口，默认实现 `FLevelEditorObjectMixerSelectionInterface` 通过 `GEditor` 同步。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-18 | `462ec4ed` | Fix warning V623: Consider inspecting the '?:' operator | 静态分析警告修复，非功能性改动 |
| 2025-07-11 | `1bb7cec8` | Ran update script to remove null initializers for TSubclassOf | 代码规范化，移除冗余 `= nullptr` |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 编译优化宏，非功能性改动 |

### 维护评价

- **创建时间**：2022 年 8 月，约 4 年历史
- **维护状态**：**活跃维护中**。最近的更新（2025-07）虽为代码质量改进而非功能更新，但说明该插件仍被纳入 Epic 的常规代码维护流程
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion: true`，`Hidden: true`，说明 Epic 将其标记为实验性功能，API 可能在未来版本中变更
- **无测试用例**：插件目录内未发现自动化测试文件
- **推荐程度**：可以使用，但需注意 Beta 标签。Filter 架构设计良好且可扩展，LightMixer 是其成功的参考实现

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ObjectMixer)
- [官方文档]()（无，.uplugin 的 DocsURL 为空）
