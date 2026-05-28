# MetaHuman Creator

> MetaHuman Character Asset Creator and Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 元人类角色编辑器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MetaHumanCharacter` (Runtime), `MetaHumanCharacterEditor` (Runtime), `MetaHumanCharacterMigrationEditor` (Runtime), `MetaHumanCharacterPalette` (Runtime), `MetaHumanCharacterPaletteEditor` (Runtime), `MetaHumanDefaultEditorPipeline` (Runtime), `MetaHumanDefaultPipeline` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter) | |

## 用途

这是一个为 MetaHuman 角色资产创建、编辑和管理提供完整工具链的插件。它并非简单的组件或单一功能，而是一个**系统级插件**，包含了从角色资产定义、外观（妆容、皮肤、眼睛）编辑、发型/服装管理，到旧版 MetaHuman 角色数据迁移的全栈功能。其核心存在价值是提供一套标准化的、数据驱动的 MetaHuman 角色工作流，取代旧版基于蓝图的、复杂的 MetaHuman Creator 流程，使角色资产更容易在项目中管理和复用。

## 使用场景

- 你的项目需要从 **MetaHuman Creator（旧版网页工具）** 导入角色，并希望将其转换为新版的、基于资产的 `UMetaHumanCharacter` 资产。
- 你希望使用一个统一的编辑器界面（`MetaHumanCharacterEditor` 模块）来调整角色的皮肤、妆容、眼睛细节、发型和服装。
- 你需要为项目创建标准化的 MetaHuman 角色预设或模板，以便美术团队使用。
- 你正在开发需要程序化生成或批量处理 MetaHuman 角色的工具。

## 蓝图用法

本插件的蓝图接口主要集中在资产管理和数据映射上。

### 核心资产类

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UMetaHumanMigrationDatabase` | 迁移数据库，定义了从旧资产标识符到新 `UMetaHumanWardrobeItem` 的映射关系。 | `UMetaHumanMigrationDatabase` |
| `UMetaHumanMigrationAssetCollection` | 资产集合，包含一组特定类型（如发型、眉毛）的迁移映射。 | `UMetaHumanMigrationAssetCollection` |

### 使用示例（蓝图描述）

1.  在内容浏览器中创建一个 `UMetaHumanMigrationDatabase` 数据资产。
2.  在该资产的 `Assets` 属性中，为每种毛发/服装类型（`EMetaHumanMigrationDataAssetType`）添加一个 `UMetaHumanMigrationAssetCollection`。
3.  在每个 `UMetaHumanMigrationAssetCollection` 中，填充 `GroomAssetMapping` 属性，将旧 MetaHuman Creator 中的发型名称映射到项目中新的衣橱物品（`UMetaHumanWardrobeItem`）上。
4.  当用户通过 Bridge 或其他方式导入旧版 MetaHuman 时，迁移系统会使用此数据库进行资产匹配和转换。

## C++ 用法

核心迁移逻辑由 `FMetaHumanCharacterMigrationEditorModule` 驱动，它监听导入事件并执行转换。

### 头文件引入

```cpp
#include "MetaHumanCharacterMigrationEditorModule.h"
```

### 基本用法

迁移模块的核心在于处理导入请求。以下是迁移过程的核心逻辑概览（基于源码分析）：

```cpp
// 伪代码，展示迁移流程的核心逻辑
bool FMetaHumanCharacterMigrationEditorModule::OnMetaHumanImportStarted(
    const UE::MetaHuman::FSourceMetaHuman& InSourceMetaHuman)
{
    // 1. 根据设置（Prompt/Always Migrate/Ask）决定迁移动作
    // 2. 如果用户选择迁移，则创建新的 UMetaHumanCharacter 资产
    UMetaHumanCharacter* NewCharacter = CreateNewCharacterAsset();

    // 3. 填充迁移信息结构体
    FMetaHumanMigrationInfo MigrationInfo;
    // ... 从 InSourceMetaHuman 解析并填充 MigrationInfo ...

    // 4. 将迁移信息应用到新角色上
    MigrateMetaHuman(InSourceMetaHuman);

    // 5. 内部会调用以下方法设置各项参数：
    // SetSkin(NewCharacter, MigrationInfo);
    // SetMakeup(NewCharacter, MigrationInfo);
    // SetEyes(NewCharacter, MigrationInfo);
    // SetGrooms(NewCharacter, MigrationInfo, OutSlotSelections);
    // UpdateWardrobe(NewCharacter, MigrationInfo, InSlotSelections);

    return false; // 返回 false 以阻止旧的导入流程
}
```
*注：以上为流程说明，实际代码分散在 `FMetaHumanCharacterMigrationEditorModule` 类的多个私有方法中。*

### 进阶用法

迁移模块深度集成了编辑器子系统来提交资产变更。例如，设置妆容参数后，会通过 `UMetaHumanCharacterEditorSubsystem` 来记录变更并通知预览更新。

```cpp
// 示例：设置妆容参数的简化逻辑
void FMetaHumanCharacterMigrationEditorModule::SetMakeup(
    TNotNull<UMetaHumanCharacter*> InCharacter,
    const FMetaHumanMigrationInfo& InMigrationInfo)
{
    // 获取编辑器子系统
    UMetaHumanCharacterEditorSubsystem* EditorSubsystem = GEditor->GetEditorSubsystem<UMetaHumanCharacterEditorSubsystem>();

    // 修改角色的妆容属性
    FMetaHumanMakeupCharacterProperties MakeupProps = InCharacter->GetMakeupProperties();
    // ... 根据 InMigrationInfo.Face.Makeup 更新 MakeupProps ...

    // 通过子系统提交变更，这将更新资产和编辑器预览
    EditorSubsystem->SetMakeupProperties(InCharacter, MakeupProps);
}
```

## Demo 示例

**创建并配置一个迁移数据库资产：**

```cpp
// MetaHumanMigrationDatabaseFactory.h
#pragma once
#include "CoreMinimal.h"
#include "Factories/Factory.h"
#include "MetaHumanMigrationDatabaseFactory.generated.h"

UCLASS()
class UMetaHumanMigrationDatabaseFactory : public UFactory
{
    GENERATED_BODY()
public:
    UMetaHumanMigrationDatabaseFactory();
    virtual UObject* FactoryCreateNew(UClass* InClass, UObject* InParent, FName InName, EObjectFlags InFlags, UObject* InContext, FFeedbackContext* InWarn) override;
};

// MetaHumanMigrationDatabaseFactory.cpp
#include "MetaHumanMigrationDatabaseFactory.h"
#include "MetaHumanMigrationDatabase.h" // 包含迁移数据库类的头文件

UMetaHumanMigrationDatabaseFactory::UMetaHumanMigrationDatabaseFactory()
{
    SupportedClass = UMetaHumanMigrationDatabase::StaticClass();
    bCreateNew = true;
    bEditAfterNew = true;
}

UObject* UMetaHumanMigrationDatabaseFactory::FactoryCreateNew(UClass* InClass, UObject* InParent, FName InName, EObjectFlags InFlags, UObject* InContext, FFeedbackContext* InWarn)
{
    return NewObject<UMetaHumanMigrationDatabase>(InParent, InClass, InName, InFlags);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCharacter` | 核心角色资产定义和运行时子系统。 |
| `MetaHumanCharacterEditor` | 角色编辑器界面和编辑器子系统（用于提交更改）。 |
| `MetaHumanCharacterPalette` | 管理角色外观部件（妆容、眼睛等）的调色板资产。 |
| `MetaHumanWardrobe` | 管理服装和发型等“衣橱”物品的资产系统。 |
| `MetaHumanIdentity` | 与 MetaHuman 身份相关的基础数据类型。 |
| `SkeletalMeshUtilitiesCommon` | 处理骨骼网格体相关的通用工具。 |
| `MessageLog` | 用于在迁移过程中输出警告和错误日志。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `95d906ba` | [UEMHC] Checking for Asset Registry filter validity before using it | 修复资产注册表过滤器有效性检查，防止崩溃。 |
| 2026-05-26 | `efb27122` | [UEMHC] Duplicate face/body DNA when duplicating archetype skel meshes | 复制原型骨骼网格体时，同时复制其面部/身体DNA数据。 |
| 2026-05-26 | `909bc538` | [MHC] Use safer weak pointers for captured objects in MHC preview delegates | 在预览委托中使用更安全的弱指针，避免悬垂引用。 |
| 2026-05-26 | `cfa3dac6` | [MetaHuman] Titan v9.0.7 | 升级到MetaHuman Titan管线v9.0.7版本。 |

### 维护评价

该插件创建于**2025年3月**，距今约**1年**，仍处于**活跃开发**状态。
- **优势**：最近一周内仍有多个提交，表明 Epic 内部正在积极使用和维护此管线。更新内容以**Bug修复、稳定性提升和功能增强**为主，符合一个大型系统的成熟过程。
- **状态**：标记为 **Beta** 且 **默认禁用**，表明它已基本可用，但 API 和功能可能在未来版本中发生变化。
- **建议**：**推荐在需要标准化 MetaHuman 工作流的项目中使用**，但应做好随引擎版本升级而调整代码的准备。对于小型或短期项目，直接使用蓝图管理的旧式 MetaHuman 可能更简单。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter/Tests) (如果存在)