# Variant Manager Content

> Data classes and assets for the Variant Manager plugin

| 属性 | 值 |
|---|---|
| 中文名 | 变体管理数据 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `VariantManagerContent` (Runtime), `VariantManagerContentEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-09-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent) | |

## 用途

Variant Manager Content 是 Variant Manager 插件的**数据层和编辑器集成层**。它定义了变体管理系统的核心数据类（`LevelVariantSets`、`VariantSet`、`Variant` 等资产类型），并提供编辑器端的资产创建工厂、Actor 工厂、属性面板自定义等功能。

这个插件存在的原因是 Variant Manager 功能被拆分为两部分：**UI/交互逻辑**（在 VariantManager 插件中）和**数据定义与编辑器集成**（即本插件）。这种分离使得数据类可以在运行时独立加载，而编辑器功能仅在开发环境中可用。

核心用途包括：
- 定义「级别变体集」（Level Variant Sets）资产类型及其数据结构
- 提供「切换 Actor」（Switch Actor）用于在场景中切换不同变体状态
- 为 Variant Manager 的资产操作提供编辑器工厂和属性自定义

## 使用场景

- 你在做**建筑可视化**，需要快速切换房间布局/材质方案 → 用 Variant Manager 定义不同配置方案
- 你在做**产品配置器**，用户要切换颜色、材质、零部件组合 → 用 LevelVariantSets 管理所有变体
- 你在做**企业展示**，需要一个场景展示多种产品状态 → 用 SwitchActor 在运行时切换
- 你需要通过**Datasmith 工作流**导入 CAD 数据并管理变体 → 本插件是 Datasmith 变体支持的基础数据层

## 蓝图用法

本插件的核心功能更多体现在资产类型（数据类）和编辑器操作上，而非运行时蓝图节点。以下是从源码中提取的关键蓝图接口：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 枚举属性访问 | CapturedByteProperty、EnumWithSecondDefault 等各种类型属性的读写 | `AVariantManagerTestActor` |
| FVector / FLinearColor / FRotator 属性 | 支持捕获的常见引擎类型属性 | `AVariantManagerTestActor` |
| UObject 数组属性 | 支持对象引用数组的变体捕获 | `AVariantManagerTestActor` |

> **注意**：`AVariantManagerTestActor` 主要用于内部测试验证变体捕获功能，涵盖 int、float、bool、FString、FName、FText、FVector、FRotator、FQuat、FColor、FLinearColor、FIntPoint、TArray、UObject、FScriptInterface 等几乎所有属性类型的捕获测试。

### 编辑器模块接口

通过 C++ 接口（非蓝图暴露）可使用以下功能：

| 方法 | 说明 |
|---|---|
| `CreateLevelVariantSetsAssetWithDialog()` | 弹出对话框创建 LevelVariantSets 资产 |
| `CreateLevelVariantSetsAsset(AssetName, PackagePath, bForceOverwrite)` | 以指定名称和路径创建 LevelVariantSets 资产 |
| `GetOrCreateLevelVariantSetsActor(Asset, bForceCreate)` | 获取或创建 LevelVariantSets Actor |

## C++ 用法

### 头文件引入

```cpp
#include "VariantManagerContentEditorModule.h"
```

### 基本用法 - 创建 LevelVariantSets 资产

通过编辑器模块接口以编程方式创建变体集资产：

```cpp
#include "VariantManagerContentEditorModule.h"

// 获取编辑器模块
IVariantManagerContentEditorModule& EditorModule = IVariantManagerContentEditorModule::Get();

// 方式一：通过对话框创建（会弹出资产命名窗口）
UObject* Asset = EditorModule.CreateLevelVariantSetsAssetWithDialog();

// 方式二：直接创建（适合自动化流程）
UObject* Asset = EditorModule.CreateLevelVariantSetsAsset(
    TEXT("MyLevelVariantSets"),
    TEXT("/Game/VariantSets/"),
    /*bForceOverwrite=*/ false
);
```

### 进阶用法 - 获取 Actor 并注册编辑器委托

```cpp
#include "VariantManagerContentEditorModule.h"

IVariantManagerContentEditorModule& EditorModule = IVariantManagerContentEditorModule::Get();

// 创建资产后获取关联的 Actor
UObject* Asset = EditorModule.CreateLevelVariantSetsAsset(
    TEXT("ProductConfig"), TEXT("/Game/Products/"));

AActor* Actor = EditorModule.GetOrCreateLevelVariantSetsActor(Asset);

// 注册编辑器打开委托（当 LevelVariantSets 资产在编辑器中打开时回调）
EditorModule.RegisterOnLevelVariantSetsDelegate(
    FOnLevelVariantSetsEditor::CreateLambda([](
        const EToolkitMode::Type Mode,
        const TSharedPtr<IToolkitHost>& Host,
        ULevelVariantSets* LevelVariantSets)
    {
        // 自定义编辑器打开行为
        UE_LOG(LogTemp, Log, TEXT("Opened LevelVariantSets: %s"), *LevelVariantSets->GetName());
    })
);
```

## Demo 示例

### LevelVariantSets 资产工厂

以下展示如何通过 UFactory 在编辑器中创建新的 LevelVariantSets 资产：

```cpp
// VariantManagerFactoryNew.h 中定义的工厂
UCLASS(hidecategories=Object)
class UVariantManagerFactoryNew : public UFactory
{
    GENERATED_UCLASS_BODY()

public:
    // 当用户在内容浏览器中右键 > 创建 > LevelVariantSets 时调用
    virtual UObject* FactoryCreateNew(
        UClass* Class,
        UObject* InParent,
        FName Name,
        EObjectFlags Flags,
        UObject* Context,
        FFeedbackContext* Warn) override;

    // 控制是否在"新建资产"菜单中显示
    virtual bool ShouldShowInNewMenu() const override;
};
```

### SwitchActor 属性自定义

SwitchActor 的属性面板自定义，展示如何在编辑器详情面板中添加下拉选择器：

```cpp
// SwitchActorCustomization.h
class FSwitchActorCustomization : public IDetailCustomization
{
public:
    static TSharedRef<IDetailCustomization> MakeInstance();

    virtual void CustomizeDetails(IDetailLayoutBuilder& DetailLayout) override;

private:
    // 下拉选择器回调
    void OnComboBoxOpening();
    void OnComboBoxOptionChanged(
        TSharedPtr<FString> NewOption, ESelectInfo::Type SelectType);
    FText GetComboBoxSelectedOptionText() const;
    void ForceRefreshDetails(int32 NewOption);

    ASwitchActor* CurrentActor;
    TSharedPtr<SComboBox<TSharedPtr<FString>>> ComboBox;
    TArray<TSharedPtr<FString>> Options;
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `VariantManager` | 核心变体管理器插件（提供 UI 和交互逻辑） |
| `DatasmithContent` | Datasmith 内容导入支持 |

> 编辑器模块还依赖常见的 UnrealEd、PropertyEditor 等编辑器基础模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `0a77223b` | Fixed crash in LevelVariantSet.cpp | 修复 LevelVariantSet 中的崩溃问题 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | 内容浏览器新增菜单数据适配 |
| 2026-04-14 | `50042443` | TLazyObjectPtr Deprecation: | TLazyObjectPtr 弃用迁移 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新格式 UE_LOGF |
| 2026-03-20 | `c5bb9adf` | [AutoViz] Minor updates to Variant Manager | 变体管理器小幅更新 |

### 维护评价

- **年龄**：2018 年创建，约 7 年历史
- **活跃度**：近期（2026 年）仍有持续更新，包括崩溃修复、API 迁移（TLazyObjectPtr、UE_LOG）和功能改进
- **状态**：⚠️ 实验性（`IsBetaVersion=true`），但默认启用且持续维护
- **已知限制**：标记为 Beta 版本，API 可能在未来版本中发生变化
- **推荐**：**可谨慎使用**。虽然是 Beta 状态，但已默认启用多年且持续有维护，属于企业级可视化工作流的成熟组件。用于建筑可视化和产品配置等场景已被验证可靠。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent/Source/VariantManagerContentEditor/Public/VariantManagerTestActor.h)