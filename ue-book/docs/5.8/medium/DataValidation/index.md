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
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/DataValidation) | |

## 用途

DataValidation 是 UE5 的**资产验证框架**，用于在编辑器和 CI/CD 流程中自动检查资产的有效性。

它解决的核心问题是：**如何确保项目中的资产（蓝图、材质、地图、本地化资源等）在保存、提交到源码管理或打包之前不会包含错误？** 没有这个插件，团队只能靠人工检查或等运行时崩溃才发现问题。

该插件提供了一个可扩展的验证系统：
1. **UObject::IsDataValid** — 最基础的验证入口，适合在项目自定义类中直接重写
2. **UEditorValidatorBase** — 验证器基类，适合针对引擎类或特定资产类型编写独立验证规则，支持 C++ 和蓝图
3. **UEditorValidatorSubsystem** — 统一管理所有验证器，提供批量验证、保存时验证、Changelist 验证等能力

验证可以在多个时机触发：手动运行、资产保存时自动运行、源码管理提交前自动运行、CI/CD 中通过 Commandlet 运行。

## 使用场景

- 你在团队项目中想要**防止错误资产被提交** → 配置保存时验证或提交前验证
- 你需要为**特定资产类型**（如自定义的材质或蓝图）编写验证规则 → 继承 UEditorValidatorBase
- 你在 CI/CD 流水线中想要**自动化资产检查** → 使用 UDataValidationCommandlet
- 你需要在提交 Changelist 前检查**修改的资产是否合法** → 使用 ValidateChangelist 系列接口
- 你需要验证**本地化资产**是否与源资产类型匹配 → 内置 UEditorValidator_Localization
- 你需要检查**材质是否能在目标平台上正确编译** → 内置 UEditorValidator_Material
- 你需要检查**包文件格式**是否损坏 → 内置 UPackageFileValidator

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Validate Assets With Settings` | 对一批资产执行验证，返回失败/警告数量 | `UEditorValidatorSubsystem` |
| `Validate Changelist` | 验证一个源码管理 Changelist 中的资产 | `UEditorValidatorSubsystem` |
| `Validate Changelists` | 批量验证多个 Changelist | `UEditorValidatorSubsystem` |
| `Is Object Valid` | 验证单个 UObject 是否有效 | `UEditorValidatorSubsystem` |
| `Is Asset Valid` | 通过 FAssetData 加载并验证资产 | `UEditorValidatorSubsystem` |
| `Add Validator` | 动态注册一个验证器 | `UEditorValidatorSubsystem` |
| `Remove Validator` | 动态移除一个验证器 | `UEditorValidatorSubsystem` |
| `Asset Fails` | 在验证器中标记资产验证失败并添加错误信息 | `UEditorValidatorBase` |
| `Asset Passes` | 在验证器中标记资产验证通过 | `UEditorValidatorBase` |
| `Asset Warning` | 在验证器中添加警告但不标记为失败 | `UEditorValidatorBase` |
| `Get Validation Result` | 获取当前验证结果 | `UEditorValidatorBase` |

### 创建自定义蓝图验证器

1. **创建蓝图类**：基于 `EditorValidatorBase` 创建一个新的蓝图类
2. **重写 Can Validate 事件**：返回 `true` 表示当前用例允许验证
3. **重写 Can Validate Asset 事件**：返回 `true` 表示该资产应该由此验证器检查
4. **重写 Validate Loaded Asset 事件**：执行实际验证逻辑，调用 `AssetFails`、`AssetPasses` 或 `AssetWarning` 报告结果

### 批量验证资产示例

```
[Get All Assets By Class] → [Make FAssetData Array] →
[Validate Assets With Settings]
    - Settings: bSkipExcludedDirectories = true
                bShowIfNoFailures = true
                ValidationUsecase = Commandlet
    - OutResults → [Print: "Valid: {NumValid}, Invalid: {NumInvalid}"]
```

## C++ 用法

### 头文件引入

```cpp
#include "EditorValidatorSubsystem.h"
#include "EditorValidatorBase.h"
#include "DataValidationSettings.h"
```

### 基本用法 — 创建自定义验证器

```cpp
// 来源: Source/DataValidation/Public/EditorValidatorBase.h

#pragma once

#include "EditorValidatorBase.h"
#include "MyGameAsset.h"
#include "MyAssetValidator.generated.h"

UCLASS()
class UMyAssetValidator : public UEditorValidatorBase
{
    GENERATED_BODY()

public:
    UMyAssetValidator()
    {
        bIsEnabled = true;
    }

protected:
    // 判断是否可以验证该资产
    virtual bool CanValidateAsset_Implementation(
        const FAssetData& InAssetData,
        UObject* InObject,
        FDataValidationContext& InContext) const override
    {
        // 只验证 UMyGameAsset 类型的资产
        return InObject && InObject->IsA<UMyGameAsset>();
    }

    // 执行验证逻辑
    virtual EDataValidationResult ValidateLoadedAsset_Implementation(
        const FAssetData& InAssetData,
        UObject* InAsset,
        FDataValidationContext& InContext) override
    {
        UMyGameAsset* MyAsset = Cast<UMyGameAsset>(InAsset);
        if (!MyAsset)
        {
            return EDataValidationResult::NotValidated;
        }

        EDataValidationResult Result = EDataValidationResult::Valid;

        // 检查必须属性
        if (MyAsset->DisplayName.IsEmpty())
        {
            AssetFails(MyAsset,
                FText::FromString(TEXT("Display Name 不能为空")));
            Result = EDataValidationResult::Invalid;
        }

        // 检查数值范围
        if (MyAsset->MaxHealth <= 0)
        {
            AssetFails(MyAsset,
                FText::FromString(TEXT("MaxHealth 必须大于 0")));
            Result = EDataValidationResult::Invalid;
        }

        // 添加警告
        if (MyAsset->Description.IsEmpty())
        {
            AssetWarning(MyAsset,
                FText::FromString(TEXT("建议填写 Description")));
        }

        if (Result == EDataValidationResult::Valid)
        {
            AssetPasses(MyAsset);
        }

        return Result;
    }
};
```

### 基本用法 — 程序化验证资产

```cpp
// 来源: Source/DataValidation/Public/EditorValidatorSubsystem.h

#include "EditorValidatorSubsystem.h"

void ValidateMyAssets()
{
    // 获取验证子系统
    UEditorValidatorSubsystem* ValidationSubsystem =
        GEditor->GetEditorSubsystem<UEditorValidatorSubsystem>();

    if (!ValidationSubsystem)
    {
        return;
    }

    // 准备要验证的资产列表
    TArray<FAssetData> AssetsToValidate;
    // ... 通过 AssetRegistry 获取资产数据 ...

    // 配置验证设置
    FValidateAssetsSettings Settings;
    Settings.bSkipExcludedDirectories = true;
    Settings.bShowIfNoFailures = true;
    Settings.bCollectPerAssetDetails = true; // 收集每个资产的详细信息
    Settings.ValidationUsecase = EDataValidationUsecase::Commandlet;
    Settings.bLoadAssetsForValidation = true;
    Settings.bCaptureLogsDuringValidation = true;

    // 执行验证
    FValidateAssetsResults Results;
    int32 FailureCount = ValidationSubsystem->ValidateAssetsWithSettings(
        AssetsToValidate, Settings, Results);

    UE_LOG(LogTemp, Log,
        TEXT("验证完成: %d 请求, %d 成功, %d 失败, %d 跳过"),
        Results.NumRequested, Results.NumValid,
        Results.NumInvalid, Results.NumSkipped);
}
```

### 进阶用法 — 验证单个对象并检查上下文

```cpp
// 来源: Source/DataValidation/Public/EditorValidatorSubsystem.h

#include "EditorValidatorSubsystem.h"

void ValidateSingleAsset(UObject* AssetToValidate)
{
    UEditorValidatorSubsystem* Subsystem =
        GEditor->GetEditorSubsystem<UEditorValidatorSubsystem>();

    // 方式1: 简单验证，直接获取错误和警告文本
    TArray<FText> Errors;
    TArray<FText> Warnings;
    EDataValidationResult Result = Subsystem->IsObjectValid(
        AssetToValidate, Errors, Warnings,
        EDataValidationUsecase::Save);

    if (Result == EDataValidationResult::Invalid)
    {
        for (const FText& Error : Errors)
        {
            UE_LOG(LogTemp, Error, TEXT("验证错误: %s"), *Error.ToString());
        }
    }
}
```

### 进阶用法 — 临时禁用保存时验证

```cpp
// 来源: Source/DataValidation/Public/EditorValidatorSubsystem.h

#include "EditorValidatorSubsystem.h"

void SaveAssetWithoutValidation(UObject* Asset)
{
    // 使用 RAII 机制临时禁用验证
    // FScopedDisableValidateOnSave 构造时 Push，析构时 Pop
    {
        FScopedDisableValidateOnSave DisableValidation;

        // 在此作用域内的保存不会触发自动验证
        UPackage* Package = Asset->GetPackage();
        FEditorFileUtils::PromptForCheckoutAndSave({Package}, false, false);
    }
    // 离开作用域后，验证自动恢复
}
```

### 进阶用法 — 创建带修复能力的验证器

```cpp
// 来源: Source/DataValidation/Public/DataValidationFixers.h

#include "DataValidationFixers.h"

using namespace UE::DataValidation;

// 创建一个总是可用的修复器
TSharedRef<IFixer> Fixer = MakeFix(
    []() -> FFixResult
    {
        // 执行修复逻辑
        // 修复资产、重新保存等
        return FFixResult();
    }
);

// 创建一个带条件判断的修复器
TSharedRef<IFixer> ConditionalFixer = MakeFix(
    // 可用性判断
    []() -> EFixApplicability
    {
        // 检查是否可以应用修复
        return EFixApplicability::CanBeApplied;
    },
    // 执行修复
    []() -> FFixResult
    {
        return FFixResult();
    }
);

// 创建单次使用修复器（适用于非幂等操作）
TSharedRef<FSingleUseFixer> SingleUseFixer =
    FSingleUseFixer::Create(ConditionalFixer);

// 创建自动保存修复器（修复后自动保存资产）
TSharedRef<FAutoSavingFixer> AutoSavingFixer =
    FAutoSavingFixer::Create(ConditionalFixer);

// 创建互斥修复集（多个修复方案只能选一个）
FMutuallyExclusiveFixSet FixSet;
FixSet.Add(FText::FromString(TEXT("方案 A: 自动修复")), FixerA);
FixSet.Add(FText::FromString(TEXT("方案 B: 手动标记")), FixerB);
```

## Demo 示例

```cpp
// MyAssetValidator.h
#pragma once

#include "EditorValidatorBase.h"
#include "MyAssetValidator.generated.h"

class UTexture2D;

UCLASS()
class UMyTextureValidator : public UEditorValidatorBase
{
    GENERATED_BODY()

public:
    UMyTextureValidator();

protected:
    virtual bool CanValidateAsset_Implementation(
        const FAssetData& InAssetData,
        UObject* InObject,
        FDataValidationContext& InContext) const override;

    virtual EDataValidationResult ValidateLoadedAsset_Implementation(
        const FAssetData& InAssetData,
        UObject* InAsset,
        FDataValidationContext& InContext) override;
};
```

```cpp
// MyAssetValidator.cpp
#include "MyAssetValidator.h"
#include "Engine/Texture2D.h"

UMyTextureValidator::UMyTextureValidator()
{
    bIsEnabled = true;
}

bool UMyTextureValidator::CanValidateAsset_Implementation(
    const FAssetData& InAssetData,
    UObject* InObject,
    FDataValidationContext& InContext) const
{
    return InObject && InObject->IsA<UTexture2D>();
}

EDataValidationResult UMyTextureValidator::ValidateLoadedAsset_Implementation(
    const FAssetData& InAssetData,
    UObject* InAsset,
    FDataValidationContext& InContext)
{
    UTexture2D* Texture = Cast<UTexture2D>(InAsset);
    if (!Texture)
    {
        return EDataValidationResult::NotValidated;
    }

    EDataValidationResult Result = EDataValidationResult::Valid;

    // 检查纹理尺寸是否为 2 的幂次
    int32 Width = Texture->GetSizeX();
    int32 Height = Texture->GetSizeY();

    auto IsPowerOfTwo = [](int32 Value) -> bool
    {
        return Value > 0 && (Value & (Value - 1)) == 0;
    };

    if (!IsPowerOfTwo(Width) || !IsPowerOfTwo(Height))
    {
        AssetWarning(Texture, FText::Format(
            NSLOCTEXT("MyValidator", "NotPOT",
                "纹理 {0} 尺寸 {1}x{2} 不是 2 的幂次，可能影响性能"),
            FText::FromString(Texture->GetName()),
            FText::AsNumber(Width),
            FText::AsNumber(Height)));
    }

    // 检查最大尺寸
    const int32 MaxSize = 4096;
    if (Width > MaxSize || Height > MaxSize)
    {
        AssetFails(Texture, FText::Format(
            NSLOCTEXT("MyValidator", "TooLarge",
                "纹理 {0} 尺寸 {1}x{2} 超过限制 {3}x{3}"),
            FText::FromString(Texture->GetName()),
            FText::AsNumber(Width),
            FText::AsNumber(Height),
            FText::AsNumber(MaxSize)));
        Result = EDataValidationResult::Invalid;
    }

    if (Result == EDataValidationResult::Valid)
    {
        AssetPasses(Texture);
    }

    return Result;
}
```

## 模块依赖

从源码分析，该插件使用以下非标准依赖：

| 模块 | 用途 |
|---|---|
| `SourceControl` | 源码管理集成，用于 Changelist 验证和提交前检查 |
| `AssetRegistry` | 资产注册表查询，用于获取和过滤待验证资产 |
| `MessageLog` | 消息日志系统，用于显示验证结果（错误、警告可点击跳转） |
| `ToolMenus` | 编辑器菜单集成，用于添加验证菜单项 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `1356f236` | [WorldPartition] Reject actor descriptor mutator overrides that would split a reference-connected cl | WorldPartition 验证器新增：拒绝会拆分引用连接的 actor 描述符覆盖 |
| 2026-04-21 | `837e0aa4` | Updated validation stats analytics to be an embedded JSON array, rather than N separate named events | 遥测统计改为嵌入式 JSON 数组，减少独立事件数量 |
| 2026-04-20 | `54b3cb12` | [Backout] - CL52814415 | 回退变更 CL52814415 |
| 2026-04-20 | `df44c8a9` | [Backout] - CL52924535 | 回退变更 CL52924535 |
| 2026-04-20 | `50bde1ee` | [Backout] - CL52277962 | 回退变更 CL52277962 |

### 维护评价

**活跃维护**。该插件创建于 2017 年，是 UE 编辑器基础设施的核心组件之一。从最近的 commit 可以看出：

- **持续更新**：2026 年仍有功能性更新（WorldPartition 验证器增强、遥测优化）
- **功能不断扩展**：从最初的基础验证，发展到支持 Changelist 验证、蓝图验证器、修复器系统、日志捕获等完整功能
- **稳定性维护**：有多次 backout 操作，说明团队在谨慎维护稳定性
- **生态完善**：内置了材质、本地化、包文件、World Partition 等多种专业验证器

作为编辑器插件默认启用，数据验证是**推荐使用的**。对于大型团队项目，建议：
1. 继承 `UEditorValidatorBase` 为项目资产编写自定义验证规则
2. 在项目设置（`UDataValidationSettings`）中配置保存时验证
3. 在 CI/CD 中使用 `UDataValidationCommandlet` 进行自动化检查

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/DataValidation)
- [官方文档]()（无专用文档页面）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/DataValidation/Tests)