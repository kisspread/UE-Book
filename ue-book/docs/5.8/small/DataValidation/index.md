# Data Validation

> Editor UI and utilities for running data validation

| 属性 | 值 |
|---|---|
| 中文名 | 资产验证 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DataValidation` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2017-11-29 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/DataValidation) | |

## 用途

`DataValidation` 插件为 UE5 编辑器提供了一套完整的资产验证框架。它解决了在开发过程中如何系统性地检查资产（如蓝图、材质、地图等）是否符合特定规范和质量标准的问题。通过该插件，团队可以在资产被提交、保存或打包前自动检测并报告错误和警告，从而减少运行时错误，提高内容质量和开发效率。其核心是 `UEditorValidatorSubsystem`，它管理着一系列注册的验证器（`UEditorValidatorBase`），负责协调整个验证流程。

## 使用场景

- **自动化构建流水线**：在 CI/CD 中集成，使用命令行工具（`UDataValidationCommandlet`）在构建前验证所有资产。
- **提交前检查**：与源代码管理（如 Perforce）集成，在提交变更列表前自动验证修改的资产，防止引入错误。
- **保存时验证**：在编辑器中保存资产时，自动运行相关验证，确保资产始终有效。
- **项目特定规则**：为项目创建自定义验证器（如检查特定命名规范、资源尺寸限制、特定逻辑完整性等），强制执行团队规范。
- **质量监控**：通过收集验证统计数据（`FValidatorStatistics`），监控资产质量趋势和验证器性能。

## 蓝图用法

主要通过 `UEditorValidatorSubsystem` 和 `UEditorValidatorBase` 的蓝图接口进行操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Validate Assets With Settings` | 验证一批资产，返回失败数量，并将详细结果写入 `FValidateAssetsResults`。 | `UEditorValidatorSubsystem` |
| `Is Asset Valid` | 验证单个资产数据，返回验证结果（有效/无效/未验证）。 | `UEditorValidatorSubsystem` |
| `Is Object Valid` | 验证单个 UObject 对象，返回验证结果。 | `UEditorValidatorSubsystem` |
| `Asset Fails` | （在自定义验证器中使用）标记资产验证失败，并记录一条错误信息。 | `UEditorValidatorBase` |
| `Asset Passes` | （在自定义验证器中使用）标记资产验证通过。 | `UEditorValidatorBase` |
| `Asset Warning` | （在自定义验证器中使用）记录一条警告信息，但不标记为失败。 | `UEditorValidatorBase` |
| `Can Validate Asset` | （在自定义验证器中重写）判断验证器是否应验证给定资产。 | `UEditorValidatorBase` |
| `Validate Loaded Asset` | （在自定义验证器中重写）实现具体的资产验证逻辑。 | `UEditorValidatorBase` |

### 使用示例（蓝图描述）

1.  **调用批量验证**：
    *   创建一个 `FValidateAssetsSettings` 结构体变量，配置 `ValidationUsecase`、`bSkipExcludedDirectories` 等选项。
    *   通过资产注册表或其他方式获取一个 `TArray<FAssetData>`（待验证资产列表）。
    *   调用 `UEditorValidatorSubsystem` 的 `Validate Assets With Settings` 节点，传入资产列表和设置，接收结果和失败计数。
    *   可以检查 `FValidateAssetsResults` 中的 `NumInvalid` 和 `AssetsDetails` 了解具体情况。

2.  **创建蓝图验证器**：
    *   创建一个继承自 `UEditorValidatorBase` 的蓝图类。
    *   重写 `Can Validate Asset` 事件，输入 `InAsset`（UObject），返回布尔值表示是否要验证它（例如，只验证特定类的资产）。
    *   重写 `Validate Loaded Asset` 事件，输入 `InAsset`（UObject），使用 `Asset Fails`、`Asset Warning` 和 `Asset Passes` 节点来报告验证结果。
    *   编译并保存该蓝图类。引擎启动时，`UEditorValidatorSubsystem` 会自动发现并注册它。

## C++ 用法

### 头文件引入

```cpp
#include "EditorValidatorSubsystem.h"
#include "EditorValidatorBase.h"
```

### 基本用法

以下示例展示如何创建一个简单的 C++ 验证器，检查 `UStaticMesh` 的顶点数是否超过上限。

**源码文件路径**: `EditorValidatorBase.h` 及项目代码

```cpp
// MyVertexCountValidator.h
#pragma once
#include "EditorValidatorBase.h"
#include "MyVertexCountValidator.generated.h"

UCLASS()
class UMyVertexCountValidator : public UEditorValidatorBase
{
    GENERATED_BODY()

public:
    UMyVertexCountValidator();

protected:
    // 判断是否验证给定资产
    virtual bool CanValidateAsset_Implementation(
        const FAssetData& InAssetData,
        UObject* InAsset,
        FDataValidationContext& InContext) const override;

    // 执行验证逻辑
    virtual EDataValidationResult ValidateLoadedAsset_Implementation(
        const FAssetData& InAssetData,
        UObject* InAsset,
        FDataValidationContext& InContext) override;
};
```

```cpp
// MyVertexCountValidator.cpp
#include "MyVertexCountValidator.h"
#include "Engine/StaticMesh.h"

UMyVertexCountValidator::UMyVertexCountValidator()
{
    // 可在此设置验证器默认属性，如 bIsEnabled = false;
}

bool UMyVertexCountValidator::CanValidateAsset_Implementation(
    const FAssetData& InAssetData,
    UObject* InAsset,
    FDataValidationContext& InContext) const
{
    // 只验证 UStaticMesh 类型的资产
    return InAssetData.AssetClassPath == FTopLevelAssetPath(FName("/Script/Engine"), FName("StaticMesh"));
}

EDataValidationResult UMyVertexCountValidator::ValidateLoadedAsset_Implementation(
    const FAssetData& InAssetData,
    UObject* InAsset,
    FDataValidationContext& InContext)
{
    // 确保资产已加载且类型正确
    const UStaticMesh* StaticMesh = Cast<UStaticMesh>(InAsset);
    if (!StaticMesh)
    {
        AssetFails(InAsset, FText::FromString("Failed to load static mesh."));
        return EDataValidationResult::Invalid;
    }

    // 示例规则：顶点数超过 10000 则失败
    const int32 MaxVertices = 10000;
    int32 VertexCount = 0;
    for (const FStaticMeshSourceModel& LOD : StaticMesh->GetSourceModels())
    {
        if (LOD.BuildSettings.bGenerateMeshDistanceField) // 示例，实际统计逻辑可能更复杂
        {
            VertexCount += LOD.GetNumVertices(); // 注意：此函数可能不存在，仅为示意
        }
    }

    if (VertexCount > MaxVertices)
    {
        AssetFails(InAsset, FText::Format(
            NSLOCTEXT("VertexValidator", "TooManyVertices", "Static mesh has {0} vertices, exceeding limit of {1}."),
            FText::AsNumber(VertexCount),
            FText::AsNumber(MaxVertices)));
        return EDataValidationResult::Invalid;
    }
    else
    {
        AssetPasses(InAsset);
        return EDataValidationResult::Valid;
    }
}
```

### 进阶用法

1.  **在 C++ 中调用验证**:
    ```cpp
    // 从 UEditorValidatorSubsystem 获取子系统实例
    UEditorValidatorSubsystem* ValidationSubsystem = GEditor->GetEditorSubsystem<UEditorValidatorSubsystem>();
    if (ValidationSubsystem)
    {
        // 验证单个资产
        TArray<FText> Errors, Warnings;
        FAssetData AssetData = ...; // 从资产注册表获取
        EDataValidationResult Result = ValidationSubsystem->IsAssetValid(AssetData, Errors, Warnings, EDataValidationUsecase::Script);

        // 验证批量资产并获取详细结果
        TArray<FAssetData> AssetList = ...;
        FValidateAssetsSettings Settings;
        FValidateAssetsResults Results;
        int32 FailureCount = ValidationSubsystem->ValidateAssetsWithSettings(AssetList, Settings, Results);
        UE_LOG(LogTemp, Log, TEXT("Validation completed. Failures: %d, Valid: %d, Total: %d"),
            FailureCount, Results.NumValid, Results.NumRequested);
    }
    ```

2.  **自定义验证设置**:
    可以通过 `UDataValidationSettings`（`DataValidationSettings.h`）或覆盖 `UEditorValidatorSubsystem` 来自定义验证行为，例如排除特定目录或配置材质验证平台。

## Demo 示例

下面是一个完整的、可编译的最小示例，创建一个验证器，检查资产名称是否以指定前缀开头。

```cpp
// PrefixNameValidator.h
#pragma once

#include "CoreMinimal.h"
#include "EditorValidatorBase.h"
#include "PrefixNameValidator.generated.h"

UCLASS()
class UPrefixNameValidator : public UEditorValidatorBase
{
    GENERATED_BODY()

public:
    UPrefixNameValidator();

protected:
    virtual bool CanValidateAsset_Implementation(const FAssetData& InAssetData, UObject* InAsset, FDataValidationContext& InContext) const override;
    virtual EDataValidationResult ValidateLoadedAsset_Implementation(const FAssetData& InAssetData, UObject* InAsset, FDataValidationContext& InContext) override;

    UPROPERTY(EditAnywhere, Category = "Prefix Validation")
    FString RequiredPrefix = "M_";
};
```

```cpp
// PrefixNameValidator.cpp
#include "PrefixNameValidator.h"

UPrefixNameValidator::UPrefixNameValidator()
{
    // 默认验证器是启用的
    bIsEnabled = true;
}

bool UPrefixNameValidator::CanValidateAsset_Implementation(const FAssetData& InAssetData, UObject* InAsset, FDataValidationContext& InContext) const
{
    // 对所有资产类型生效
    return true;
}

EDataValidationResult UPrefixNameValidator::ValidateLoadedAsset_Implementation(const FAssetData& InAssetData, UObject* InAsset, FDataValidationContext& InContext)
{
    // 检查资产名称
    FString AssetName = InAssetData.AssetName.ToString();
    if (!AssetName.StartsWith(RequiredPrefix))
    {
        // 使用 AssetFails 记录错误
        AssetFails(InAsset, FText::Format(
            NSLOCTEXT("PrefixValidator", "InvalidName", "Asset name '{0}' does not start with required prefix '{1}'."),
            FText::FromString(AssetName),
            FText::FromString(RequiredPrefix)));
        return EDataValidationResult::Invalid;
    }

    AssetPasses(InAsset);
    return EDataValidationResult::Valid;
}
```

## 模块依赖

插件自身的构建依赖已在 `DataValidation.Build.cs` 中配置。对于使用此插件功能的外部模块，通常只需依赖 `DataValidation` 模块即可获得大部分公共 API。

| 模块 | 用途 |
|---|---|
| `DataValidation` | 插件核心模块，提供子系统、验证器基类和命令行工具。 |
| `SourceControl` | 用于集成源代码管理，实现提交前验证（Changelist Validation）。 |
| `MessageLog` | 用于在编辑器中显示验证结果和消息。 |
| `AssetRegistry` | 用于查询和过滤待验证的资产。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `1356f236` | [WorldPartition] Reject actor descriptor mutator overrides that would split a reference-connected cl | 增强世界分区验证，拒绝会分裂引用连接的Actor描述符变异器重写 |
| 2026-04-21 | `837e0aa4` | Updated validation stats analytics to be an embedded JSON array, rather than N separate named events | 将验证统计数据从多个独立事件改为嵌入式JSON数组，优化分析 |
| 2026-04-20 | `54b3cb12` | [Backout] - CL52814415 | 回退了之前的某个更改（CL52814415） |
| 2026-04-20 | `df44c8a9` | [Backout] - CL52924535 | 回退了之前的某个更改（CL52924535） |
| 2026-04-20 | `50bde1ee` | [Backout] - CL52277962 | 回退了之前的某个更改（CL52277962） |

### 维护评价

- **创建时间**: 插件于 2017 年创建，是一个成熟的编辑器工具。
- **活跃度**: 最近的更新集中在 2026 年 4-5 月，主要是功能增强（如世界分区验证、分析数据优化）和稳定性修复（回退操作），表明插件仍在积极维护中。
- **功能完善**: 作为 Epic Games 官方维护的核心编辑器插件，其功能非常完整，覆盖了从资产验证、命令行工具到编辑器集成和源代码管理集成的各个方面。
- **已知问题/限制**: 主要限制在于验证逻辑的实现质量完全依赖于开发者编写的自定义验证器。框架本身是稳健的。
- **推荐使用**: **强烈推荐**。对于任何有一定规模的 UE5 项目，集成数据验证是保证资产质量和构建稳定性的最佳实践。该插件提供了强大的基础设施，并且仍在持续改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/DataValidation)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/data-validation-in-unreal-engine/) （注：.uplugin 中未提供 DocsURL，此处为推测的通用文档页面）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/DataValidation/Tests) （根据插件结构推测）