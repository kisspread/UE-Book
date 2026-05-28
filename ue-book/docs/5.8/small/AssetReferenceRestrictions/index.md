# Asset Referencing Restrictions

> Apply project-specific restrictions to how content in different folders or plugins can be referenced

| 属性 | 值 |
|---|---|
| 中文名 | 资产引用限制 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AssetReferenceRestrictions` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2021-03-23 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/AssetReferenceRestrictions) | |

## 用途

此插件用于在项目中实施跨资产域（Domain）的引用限制策略。它解决了在大型或模块化项目中，确保内容组织规则得以遵守的核心问题。具体而言，它允许您定义基于文件夹路径或插件的“域”，并为这些域配置精确的可见性规则。例如，您可以配置规则以防止项目核心资产（`/Game/`）引用游戏功能插件（Game Feature Plugins）中的内容，或者防止会被烘焙到最终游戏中的资产引用仅用于开发的 `Developer` 文件夹内容。它通过拦截编辑器中的资产引用选择器（如属性面板中的资产选择器）和集成数据验证（Data Validation）来工作，确保不允许的引用无法被创建或被及时发现。

## 使用场景

-   当您的项目包含多个功能插件（Game Feature Plugins）或内容插件时，您希望隔离它们，防止项目内容意外依赖插件内容，以保持架构清晰。
-   您有一个 `Developer` 文件夹存放测试资产、原型或调试工具，并希望确保这些内容永远不会被烘焙到发布版本中。
-   您需要强制执行严格的内容分层架构，例如，UI 目录中的资产只能引用材质库中的资产，而不能引用角色模型资产。
-   在使用“资产验证”功能进行批量检查时，需要自动检测违反此类规则的错误引用。

## 蓝图用法

此插件主要通过编辑器项目设置进行配置，不直接提供额外的蓝图节点。核心交互界面是项目设置中的 `Asset Referencing Policy` 页面。

### 核心配置 (项目设置)

在编辑器中，通过 `编辑 -> 项目设置 -> 项目 -> Asset Referencing Policy` 访问配置界面。

| 设置项 | 说明 |
|---|---|
| `Use Asset Reference Restrictions` | 主开关，启用或禁用整个插件功能。 |
| `Engine Plugins` | 配置引擎插件的域规则（通过路径前缀或类别匹配）。 |
| `Project Plugins` | 配置项目插件的域规则（通过路径前缀或类别匹配）。 |
| `Project Content` | 配置项目内容目录 `/Game/` 的默认规则以及额外的自定义域。 |
| `Additional Domains` | 在此列表中添加基于内容根路径或特定资产的自定义域。 |
| `Ignore Editor Only References` | 如果为 `true`，则忽略仅编辑器存在的引用（如蓝图中的调试节点引用）。 |

### 使用示例（蓝图描述）

配置过程完全在项目设置编辑器中完成，不涉及蓝图图表连接。主要步骤是：
1.  打开项目设置，找到 `Asset Referencing Policy`。
2.  在 `Additional Domains` 下，点击 `+` 添加一个新域。
3.  为域命名，设置 `Content Roots`（例如，选择 `/Game/Developer/`）。
4.  在 `Can Reference These Domains` 中选择此域允许引用哪些其他域（例如，`EngineContent` 和 `GameContent`）。
5.  保存设置。现在，任何试图将 `/Game/Developer/` 下的资产被 `/Game/Characters/` 引用的操作，都会在资产选择器中受到限制，并在数据验证时报错。

## C++ 用法

主要通过与 `UAssetReferencingPolicySettings` 配置对象交互，或通过 `UAssetReferencingPolicySubsystem` 进行验证。

### 头文件引入

```cpp
#include "AssetReferencingPolicySettings.h"
#include "AssetReferencingPolicySubsystem.h"
```

### 基本用法

获取并修改资产引用策略的运行时设置。

```cpp
// 获取设置单例 (来源： AssetReferencingPolicySettings.h)
UAssetReferencingPolicySettings* Settings = GetMutableDefault<UAssetReferencingPolicySettings>();

// 确保插件功能已启用
Settings->bUseAssetReferenceRestrictions = true;

// 定义一个新的基于内容根的域
FARPDomainDefinitionByContentRoot NewDomain;
NewDomain.DomainName = TEXT("TestingContent");
NewDomain.DomainDisplayName = FText::FromString(TEXT("测试内容"));
NewDomain.ErrorMessageIfUsedElsewhere = FText::FromString(TEXT("测试内容不能被正式游戏内容引用。"));
NewDomain.ContentRoots.Add(FDirectoryPath{TEXT("/Game/Testing/")});
NewDomain.CanReferenceTheseDomains.Add(UAssetReferencingPolicySettings::EngineDomainName);
NewDomain.CanReferenceTheseDomains.Add(UAssetReferencingPolicySettings::GameDomainName);

// 添加到设置中
Settings->AdditionalDomains.Add(NewDomain);

// 通知系统设置已更改 (触发域数据库重建)
#if WITH_EDITOR
FPropertyChangedEvent DummyEvent(nullptr);
Settings->PostEditChangeProperty(DummyEvent);
#endif
```

### 进阶用法

使用子系统直接查询或验证特定资产的引用关系。

```cpp
// 获取编辑器子系统 (来源： AssetReferencingPolicySubsystem.h)
UAssetReferencingPolicySubsystem* Subsystem = GEditor->GetEditorSubsystem<UAssetReferencingPolicySubsystem>();

// 检查某个资产数据是否受引用限制
FAssetData MyAssetData = ...; // 获取某个资产
bool bRestricted = Subsystem->ShouldValidateAssetReferences(MyAssetData);

// 如果受限制，执行验证
if (bRestricted)
{
    auto ValidationResult = Subsystem->ValidateAssetReferences(MyAssetData);
    if (ValidationResult.HasError())
    {
        // 处理错误，打印不允许的引用信息
        TArray<FAssetReferenceError> Errors = ValidationResult.StealError();
        for (const FAssetReferenceError& Error : Errors)
        {
            UE_LOG(LogTemp, Warning, TEXT("引用错误: %s -> %s, 原因: %s"),
                *Error.ReferencingAsset.ToString(),
                *Error.ReferencedAsset.ToString(),
                *Error.ErrorText.ToString());
        }
    }
}
```

## Demo 示例

一个在编辑器模块启动时，通过 C++ 配置一个新限制域的最小示例。

**MyEditorSettingsModule.h**
```cpp
#pragma once

class FMyEditorSettingsModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyEditorSettingsModule.cpp**
```cpp
#include "MyEditorSettingsModule.h"
#include "AssetReferencingPolicySettings.h"
#include "ISettingsModule.h"

#define LOCTEXT_NAMESPACE "FMyEditorSettingsModule"

void FMyEditorSettingsModule::StartupModule()
{
    // 可以在这里通过代码动态添加域，或者依赖UI配置
    UAssetReferencingPolicySettings* Settings = GetMutableDefault<UAssetReferencingPolicySettings>();
    if (Settings && !Settings->bUseAssetReferenceRestrictions)
    {
        // 例如，在某些开发环境下自动启用
        Settings->bUseAssetReferenceRestrictions = true;
        UE_LOG(LogTemp, Log, TEXT("已启用资产引用限制功能。"));
    }
}

void FMyEditorSettingsModule::ShutdownModule()
{
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorSettingsModule, MyEditorSettings)
```

## 模块依赖

此插件依赖于 `DataValidation` 插件以集成资产验证功能。

| 模块 | 用途 |
|---|---|
| `DataValidation` | 提供 `UEditorValidatorBase` 基类，用于注册自定义的资产引用验证器。 |

**说明**：您自己的项目模块如果要使用此插件的设置或子系统功能，需要在 `.Build.cs` 文件中添加对 `AssetReferenceRestrictions` 模块的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `b6d06144` | Improved error reference issue message, so that the source and referenced asset are always at the st... | 改进错误引用消息的格式，确保源资产和引用资产始终清晰可见。 |
| 2026-04-21 | `a3829d3d` | UE: Fix missing reference reporting to include an asset name so the assetdata is considered valid | 修复缺失引用的报告，现在会包含资产名称以使资产数据被视为有效。 |
| 2026-04-20 | `403878d6` | Migrated some common reference validation logic to UAssetReferencingPolicySubsystem::ValidateAssetRe... | 将一些通用的引用验证逻辑迁移到 `UAssetReferencingPolicySubsystem` 中，提高复用性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 `UE_LOG` 迁移为格式化版本 `UE_LOGF`。 |
| 2026-04-02 | `4c2482d7` | Fix AssetReferenceRestrictions phantom domain error for platform-disabled plugin dependencies | 修复当插件依赖被平台禁用时，出现的“幽灵域”错误。 |

### 维护评价

该插件处于**活跃维护**状态。尽管自2021年创建以来已有约4年历史（🆕），但从近期（2026年）的提交记录可以看出，Epic 仍在持续投入，主要集中在错误报告质量的改进、内部代码重构和平台兼容性修复。最近的更新没有涉及新功能，但修复了多个影响用户体验和准确性的实际问题。作为编辑器工具，其稳定性比新功能更重要。

**推荐使用**：对于任何有明确内容组织架构和跨团队协作需求的中大型项目，强烈建议启用此插件。它能有效将内容依赖问题在编辑期和打包前暴露出来，避免运行时错误。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/AssetReferenceRestrictions)
-   [官方文档]() (此插件无官方文档链接)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Editor/AssetReferenceRestrictions) (如果存在，位于 `Engine/Tests` 目录下)