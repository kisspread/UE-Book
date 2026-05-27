# Data Validation

> Editor UI and utilities for running data validation

| 属性 | 值 |
|---|---|
| 中文名 | 数据验证 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DataValidation` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2017-11-29 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/DataValidation) | |

## 用途

DataValidation 插件为 Unreal Engine 编辑器提供了一个全面的资产和数据验证框架。它不仅仅是一个简单的检查工具，而是一个可扩展的验证系统，旨在确保项目资产在提交到源代码控制系统（SCC）或打包前符合质量标准。

这个插件解决的核心问题是：**如何在大型项目中自动化地、系统性地检查资产质量，防止损坏、无效或不符合规范的资产被引入项目**。它通过以下方式实现：

1.  **框架化验证**：提供 `UEditorValidatorBase` 基类，允许开发者（通过 C++ 或蓝图）创建针对特定资产类型或规则的自定义验证器。
2.  **多层次验证**：结合了 `UObject::IsDataValid` 的内置验证（适合项目特定类）和注册的独立验证器（适合引擎类或通用逻辑）。
3.  **深度集成**：与编辑器保存流程、源代码控制提交流程（提交前验证）、以及命令行（用于 CI/CD）深度集成，实现了从个人编辑到团队协作全流程的质量控制。
4.  **详细报告**：提供带有可点击链接的详细错误和警告报告，便于开发者快速定位问题资产。

## 使用场景

-   你在编辑器中保存一个材质或蓝图时，希望系统能**自动检查**并报告其中存在的问题（如引用缺失、配置错误）。
-   你的团队需要在**提交代码或资产到 Perforce/Git 前**，自动验证所有变更的资产，防止问题代码库。
-   你需要在**自动化构建流水线（CI/CD）** 中，通过命令行对项目的所有资产进行批量验证，确保打包版本的数据质量。
-   你需要为项目中的**特定资产类型**（如自定义的 Actor、数据表）编写特殊的验证规则（例如，确保所有角色都有正确的动画蒙太奇）。
-   你希望验证**世界分区（World Partition）** 相关资产的完整性和引用关系。

## 蓝图用法

主要的蓝图 API 通过 `UEditorValidatorSubsystem` 和 `UEditorValidatorBase` 暴露。`UEditorValidatorSubsystem` 是管理所有验证的中心，可以通过 `GEditor->GetEditorSubsystem<UEditorValidatorSubsystem>()` 获取。

### 核心验证节点

这些节点位于 `UEditorValidatorSubsystem` 上。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Validate Assets With Settings` | 对一组资产执行验证，可配置详细设置，并返回包含成功/失败统计的 `FValidateAssetsResults` 结构。 | `UEditorValidatorSubsystem` |
| `Is Asset Valid` | 检查单个资产是否有效，返回 `Valid`/`Invalid`/`NotValidated` 状态，以及错误和警告消息数组。 | `UEditorValidatorSubsystem` |
| `Validate Changelist` | 验证一个源代码控制变更列表（`UDataValidationChangelist`）中的所有资产。 | `UEditorValidatorSubsystem` |

### 验证报告与管理节点

这些节点位于 `UEditorValidatorBase` 上，通常在自定义验证器的蓝图类中使用。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Asset Fails` | 将当前验证的资产标记为失败，并记录一条错误消息。 | `UEditorValidatorBase` |
| `Asset Passes` | 将当前验证的资产标记为通过。必须调用，否则将报告验证器未检查该资产。 | `UEditorValidatorBase` |
| `Asset Warning` | 为当前资产记录一条警告消息，但不将其标记为失败。 | `UEditorValidatorBase` |
| `Get Validation Result` | 获取此验证器上一次验证的结果状态。 | `UEditorValidatorBase` |

### 自定义验证器（蓝图用法）

你可以创建 `UEditorValidatorBase` 的蓝图子类来定义自定义验证逻辑。

**主要重写事件（在蓝图子类中覆盖）：**

1.  **`Can Validate Asset` (Event)**：决定此验证器是否可以验证给定的资产。返回 `true` 才会继续验证。
2.  **`Validate Loaded Asset` (Event)**：执行实际的验证逻辑。在此事件图表中，你可以使用 `Asset Fails`、`Asset Passes` 和 `Asset Warning` 节点来报告结果。

**使用示例（蓝图描述）：**
假设你要验证所有“静态网格体”资产的名称必须以 `SM_` 开头。

1.  创建一个新的蓝图类，父类选择 `EditorValidatorBase`，命名为 `BP_Validator_MeshNaming`。
2.  在 **`Can Validate Asset`** 事件中，添加一个 `Class Is Child Of` 节点检查传入的 `Asset` 对象是否为 `StaticMesh` 类型。如果不是，返回 `false`。
3.  在 **`Validate Loaded Asset`** 事件中：
    a.  使用 `Get Object Name` 节点获取资产名称。
    b.  使用 `Starts With` 节点检查名称是否以 `SM_` 开头。
    c.  如果检查失败，使用 `Asset Fails` 节点，并连接一个格式化的错误文本（如 `"静态网格体名称必须以 SM_ 开头。当前名称: {AssetName}"`）。
    d.  如果检查通过，使用 `Asset Passes` 节点。
4.  编译并保存蓝图。该验证器将被引擎自动发现并集成到编辑器的验证系统中。

## C++ 用法

### 头文件引入

要创建自定义 C++ 验证器，需要包含以下头文件：
```cpp
#include "EditorValidatorBase.h"
```
要使用验证子系统，需要包含：
```cpp
#include "EditorValidatorSubsystem.h"
```

### 基本用法：创建自定义验证器

创建一个继承自 `UEditorValidatorBase` 的类，并重写关键的虚函数。

**MyCustomValidator.h**
```cpp
#pragma once

#include "EditorValidatorBase.h"
#include "MyCustomValidator.generated.h"

UCLASS()
class UMyCustomValidator : public UEditorValidatorBase
{
    GENERATED_BODY()

protected:
    // 判断此验证器能否验证该资产（类型过滤）
    virtual bool CanValidateAsset_Implementation(const FAssetData& InAssetData, UObject* InAsset, FDataValidationContext& InContext) const override;

    // 执行具体的验证逻辑
    virtual EDataValidationResult ValidateLoadedAsset_Implementation(const FAssetData& InAssetData, UObject* InAsset, FDataValidationContext& InContext) override;
};
```

**MyCustomValidator.cpp**
```cpp
#include "MyCustomValidator.h"
#include "Engine/Texture2D.h"

bool UMyCustomValidator::CanValidateAsset_Implementation(const FAssetData& InAssetData, UObject* InAsset, FDataValidationContext& InContext) const
{
    // 只验证纹理资产
    return InAssetData.GetClass() == UTexture2D::StaticClass();
}

EDataValidationResult UMyCustomValidator::ValidateLoadedAsset_Implementation(const FAssetData& InAssetData, UObject* InAsset, FDataValidationContext& InContext)
{
    UTexture2D* Texture = Cast<UTexture2D>(InAsset);
    if (!Texture)
    {
        AssetFails(InAsset, FText::FromString(TEXT("无法将对象转换为 UTexture2D")));
        return EDataValidationResult::Invalid;
    }

    // 检查纹理尺寸是否为2的幂
    if (!FMath::IsPowerOfTwo(Texture->GetSizeX()) || !FMath::IsPowerOfTwo(Texture->GetSizeY()))
    {
        AssetFails(InAsset, FText::Format(
            NSLOCTEXT("MyValidator", "TextureSizeNotPOT", "纹理 '{0}' 的尺寸 ({1}x{2}) 不是2的幂。"),
            FText::FromString(InAssetData.AssetName.ToString()),
            Texture->GetSizeX(),
            Texture->GetSizeY()));
        return EDataValidationResult::Invalid;
    }

    // 验证通过
    AssetPasses(InAsset);
    return EDataValidationResult::Valid;
}
```

### 进阶用法：在验证期间临时禁用“保存时验证”

在执行某些操作（如批量处理资产）时，你可能不希望触发“保存时验证”。可以使用 `FScopedDisableValidateOnSave` 辅助类。

```cpp
#include "EditorValidatorSubsystem.h"

void SomeBatchProcessingFunction()
{
    // 在此作用域内，保存资产将不会触发验证
    FScopedDisableValidateOnSave DisableValidationScope;

    // ... 进行资产修改和保存操作 ...
    SomePackage->SavePackage(...);
}
// 离开作用域后，验证将恢复
```

## Demo 示例

一个完整的自定义验证器示例，验证所有蓝图资产不能有 `Event Tick` 节点被使用（假设项目有此优化规范）。

**BPNoTickValidator.h**
```cpp
#pragma once

#include "EditorValidatorBase.h"
#include "BPNoTickValidator.generated.h"

UCLASS()
class UBPNoTickValidator : public UEditorValidatorBase
{
    GENERATED_BODY()

protected:
    virtual bool CanValidateAsset_Implementation(const FAssetData& InAssetData, UObject* InAsset, FDataValidationContext& InContext) const override;
    virtual EDataValidationResult ValidateLoadedAsset_Implementation(const FAssetData& InAssetData, UObject* InAsset, FDataValidationContext& InContext) override;
};
```

**BPNoTickValidator.cpp**
```cpp
#include "BPNoTickValidator.h"
#include "Engine/Blueprint.h"
#include "K2Node_Event.h"
#include "EdGraph/EdGraph.h"

bool UBPNoTickValidator::CanValidateAsset_Implementation(const FAssetData& InAssetData, UObject* InAsset, FDataValidationContext& InContext) const
{
    return InAssetData.GetClass() == UBlueprint::StaticClass();
}

EDataValidationResult UBPNoTickValidator::ValidateLoadedAsset_Implementation(const FAssetData& InAssetData, UObject* InAsset, FDataValidationContext& InContext)
{
    UBlueprint* Blueprint = Cast<UBlueprint>(InAsset);
    if (!Blueprint)
    {
        return EDataValidationResult::NotValidated;
    }

    bool bFoundTickNode = false;

    // 遍历蓝图中的所有图表
    for (UEdGraph* Graph : Blueprint->UbergraphPages)
    {
        // 遍历图表中的所有节点
        for (UEdGraphNode* Node : Graph->Nodes)
        {
            // 检查是否为事件节点且事件名为 “ReceiveTick” 或 “Tick”
            if (UK2Node_Event* EventNode = Cast<UK2Node_Event>(Node))
            {
                if (EventNode->EventReference.GetMemberName() == UEdGraphSchema_K2::FN_UserConstructionScript ||
                    EventNode->EventReference.GetMemberName() == UEdGraphSchema_K2::FN_ReceiveTick)
                {
                    bFoundTickNode = true;
                    AssetFails(InAsset, FText::Format(
                        NSLOCTEXT("BPNoTickValidator", "TickFound", "蓝图 '{0}' 中发现了被禁用的 {1} 节点。"),
                        FText::FromString(Blueprint->GetName()),
                        FText::FromString(EventNode->GetNodeTitle(ENodeTitleType::FullTitle).ToString())));
                    // 找到一个即可停止
                    break;
                }
            }
        }
        if (bFoundTickNode) break;
    }

    if (!bFoundTickNode)
    {
        AssetPasses(InAsset);
        return EDataValidationResult::Valid;
    }

    return EDataValidationResult::Invalid;
}
```

## 模块依赖

要使用或扩展 DataValidation 插件的功能，你的模块需要依赖以下独特的模块：

| 模块 | 用途 |
|---|---|
| `SourceControl` | 与源代码控制提供商（Perforce, Git 等）交互，用于验证变更列表。 |
| `MessageLog` | 显示带有可点击链接的验证错误和警告日志。 |
| `AssetRegistry` | 查询和过滤资产，是验证系统获取待验证资产列表的核心。 |
| `Slate`, `SlateCore` | 构建验证结果的 UI 显示（如 Asset Audit 窗口）。 |
| `UnrealEd` | 编辑器子系统、命令行和编辑器特定功能的支持。 |
| `PropertyEditor` | 可能用于验证器配置的自定义属性编辑。 |

**注意**：Core, CoreUObject, Engine, InputCore 等是标准依赖，已省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `1356f236` | [WorldPartition] Reject actor descriptor mutator overrides that would split a reference-connected cl | 增强了世界分区验证，拒绝会导致引用链断裂的演员描述符变异。 |
| 2026-04-21 | `837e0aa4` | Updated validation stats analytics to be an embedded JSON array, rather than N separate named events | 改进了验证统计的分析数据格式，使用嵌入式JSON数组而非多个独立事件。 |
| 2026-04-20 | `54b3cb12` | [Backout] - CL52814415 | 回滚了某个变更（CL52814415），可能为修复引入的问题。 |
| 2026-04-20 | `df44c8a9` | [Backout] - CL52924535 | 回滚了另一个变更（CL52924535），与上一条同日。 |
| 2026-04-20 | `50bde1ee` | [Backout] - CL52277962 | 回滚了第三个变更（CL52277962），当日进行了多次回滚操作。 |

### 维护评价

DataValidation 插件自 2017 年创建以来，经历了长期的开发和迭代。从最近的提交记录（2026年5月）可以看出，它仍然是 Unreal Engine **活跃维护**的核心组件，持续进行功能增强和问题修复。

-   **优点**：架构成熟，高度可扩展，与引擎深度集成，是保证项目数据质量的基石工具。Epic Games 持续投入开发，以支持新特性（如世界分区）。
-   **注意点**：框架相对复杂，自定义验证器的开发需要一定的学习成本。回滚提交记录显示其变更可能影响重大，需谨慎更新。
-   **推荐**：**强烈推荐**所有正式项目启用并配置此插件。它是自动化质量保证（QA）和构建流水线（CI/CD）中不可或缺的一环。对于大型团队，基于它构建项目特定的验证规则集是最佳实践。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/DataValidation)
-   [官方文档]() （.uplugin 中未提供 DocsURL）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/DataValidation/Tests) (从代码结构推断)