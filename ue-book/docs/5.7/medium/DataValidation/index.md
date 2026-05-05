# Data Validation

> Editor UI and utilities for running data validation

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DataValidation` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2017-11-29 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/DataValidation) | |

## 用途

DataValidation 是 UE5 的**资产验证框架**，提供一套可扩展的机制来检查项目中的资产是否符合质量标准。它解决的核心问题是：在大型项目中，如何自动发现资产中的错误（如损坏的包文件、材质着色器编译失败、本地化资产类型不匹配等），并在保存、提交或打包前阻止这些问题流入下游流程。

插件的架构分三层：
1. **`UObject::IsDataValid`** — 类级别的验证，适合项目自定义类（如在自己的 Actor 中重写 `IsDataValid`）
2. **`UEditorValidatorBase`** — 独立的验证器类，适合验证引擎类或通用规则，C++ 和蓝图均可创建
3. **`UEditorValidatorSubsystem`** — 管理所有验证器的 Editor Subsystem，可被子类化以改变整体验证行为

验证可以在以下时机触发：
- **保存时**（默认启用，可在设置中关闭）
- **手动触发**（右键菜单 "Validate Assets"、Tools 菜单 "Validate Data"）
- **Commandlet**（CI/CD 管线中批量验证）
- **Cook 时**（打包前自动验证源包）
- **SCC 提交前**（集成源码管理 PreSubmit 回调）

## 使用场景

- 你在团队项目中需要确保所有材质在目标平台上能正确编译着色器 → 使用内置的 `UEditorValidator_Material`
- 你需要在 CI 流水线中批量验证所有资产 → 使用 `DataValidationCommandlet`
- 你需要为项目自定义验证规则（如"所有纹理必须是 2 的幂次方"）→ 继承 `UEditorValidatorBase` 创建自定义验证器
- 你需要在提交 Perforce changelist 前自动检查是否有未保存的文件 → 内置的 `UDirtyFilesChangelistValidator` 和 `UWorldPartitionChangelistValidator`
- 你需要验证本地化资产（L10N 文件夹中的资产）与源资产类型一致 → 内置的 `UEditorValidator_Localization`
- 你需要临时禁用保存时验证（例如批量脚本操作）→ 使用 `FScopedDisableValidateOnSave`

## 蓝图用法

DataValidation 提供了蓝图可调用的 API，主要通过 `UEditorValidatorSubsystem` 和 `UEditorValidatorBase` 暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Validate Assets With Settings` | 验证一批资产，返回结果统计 | `UEditorValidatorSubsystem` |
| `Validate Changelist` | 验证一个 changelist 中的资产 | `UEditorValidatorSubsystem` |
| `Validate Changelists` | 验证多个 changelists | `UEditorValidatorSubsystem` |
| `Is Object Valid` | 验证单个 UObject 是否有效 | `UEditorValidatorSubsystem` |
| `Is Asset Valid` | 通过 AssetData 验证单个资产 | `UEditorValidatorSubsystem` |
| `Add Validator` | 动态注册一个验证器 | `UEditorValidatorSubsystem` |
| `Remove Validator` | 移除一个验证器 | `UEditorValidatorSubsystem` |
| `Asset Fails` | 标记资产验证失败（在验证器中使用） | `UEditorValidatorBase` |
| `Asset Passes` | 标记资产验证通过 | `UEditorValidatorBase` |
| `Asset Warning` | 添加警告信息 | `UEditorValidatorBase` |
| `Get Validation Result` | 获取当前验证结果 | `UEditorValidatorBase` |

### 创建蓝图验证器

1. 创建一个新的蓝图类，父类选择 `EditorValidatorBase`
2. 重写事件 **"Can Validate Asset"** — 返回是否可以验证该资产
3. 重写事件 **"Validate Loaded Asset"** — 执行实际验证逻辑
4. 在验证逻辑中调用 `AssetFails`/`AssetPasses`/`AssetWarning` 报告结果
5. 蓝图验证器会被自动发现和注册（无需手动操作）

### 使用示例（蓝图描述）

**手动验证选中的资产：**
在 Content Browser 中选中资产 → 右键 → Asset Actions → Validate Assets。这会调用 `IDataValidationModule::ValidateAssets`，结果显示在 Message Log 中。

**通过蓝图调用验证：**
1. 获取 `Editor Validator Subsystem` 引用
2. 构造 `Validate Assets Settings` 结构体，设置 `ValidationUsecase` 等参数
3. 调用 `Validate Assets With Settings`，传入 `AssetData` 数组
4. 从返回的 `Validate Assets Results` 读取 `NumValid`、`NumInvalid`、`NumWarnings` 等统计

## C++ 用法

### 头文件引入

```cpp
#include "EditorValidatorSubsystem.h"
#include "EditorValidatorBase.h"
#include "DataValidationSettings.h"
#include "DataValidationModule.h"
```

### 基本用法：创建自定义验证器

来源：`Source/DataValidation/Public/EditorValidatorBase.h`

```cpp
// MyAssetValidator.h
#pragma once
#include "EditorValidatorBase.h"
#include "MyAssetValidator.generated.h"

UCLASS()
class UMyAssetValidator : public UEditorValidatorBase
{
    GENERATED_BODY()

protected:
    // 判断此验证器是否能验证该资产
    virtual bool CanValidateAsset_Implementation(
        const FAssetData& InAssetData,
        UObject* InObject,
        FDataValidationContext& InContext) const override
    {
        // 只验证 UMyCustomAsset 类型
        return InObject->IsA<UMyCustomAsset>();
    }

    // 执行验证逻辑
    virtual EDataValidationResult ValidateLoadedAsset_Implementation(
        const FAssetData& InAssetData,
        UObject* InAsset,
        FDataValidationContext& Context) override
    {
        UMyCustomAsset* MyAsset = Cast<UMyCustomAsset>(InAsset);
        if (!MyAsset)
        {
            return EDataValidationResult::NotValidated;
        }

        // 检查规则
        if (MyAsset->TextureSizeX % 2 != 0)
        {
            AssetFails(InAsset, NSLOCTEXT("MyValidator", "NotPowerOfTwo",
                "Texture width must be a power of 2."));
            return EDataValidationResult::Invalid;
        }

        AssetPasses(InAsset);
        return EDataValidationResult::Valid;
    }
};
```

C++ 验证器会被引擎自动发现（通过 `GetDerivedClasses`），无需手动注册。

### 基本用法：通过代码调用验证

来源：`Source/DataValidation/Private/DataValidationCommandlet.cpp`

```cpp
#include "EditorValidatorSubsystem.h"
#include "Editor.h"

// 获取验证子系统
UEditorValidatorSubsystem* ValidationSubsystem =
    GEditor->GetEditorSubsystem<UEditorValidatorSubsystem>();

// 构造设置
FValidateAssetsSettings Settings;
Settings.bSkipExcludedDirectories = true;
Settings.ValidationUsecase = EDataValidationUsecase::Manual;
Settings.bCollectPerAssetDetails = true; // 收集每个资产的详细信息

// 准备资产列表
TArray<FAssetData> AssetDataList;
IAssetRegistry::GetChecked().GetAllAssets(AssetDataList, false);

// 执行验证
FValidateAssetsResults Results;
int32 NumFailures = ValidationSubsystem->ValidateAssetsWithSettings(
    AssetDataList, Settings, Results);

// 读取结果
UE_LOG(LogTemp, Log, TEXT("Valid: %d, Invalid: %d, Warnings: %d, Skipped: %d"),
    Results.NumValid, Results.NumInvalid, Results.NumWarnings, Results.NumSkipped);
```

### 进阶用法：验证单个对象

来源：`Source/DataValidation/Private/EditorValidatorSubsystem.cpp`

```cpp
// 直接验证一个 UObject（不通过 AssetData）
UObject* MyObject = /* ... */;
TArray<FText> Errors;
TArray<FText> Warnings;

EDataValidationResult Result = ValidationSubsystem->IsObjectValid(
    MyObject, Errors, Warnings, EDataValidationUsecase::Manual);

if (Result == EDataValidationResult::Invalid)
{
    for (const FText& Error : Errors)
    {
        UE_LOG(LogTemp, Error, TEXT("Validation Error: %s"), *Error.ToString());
    }
}
```

### 进阶用法：临时禁用保存时验证

来源：`Source/DataValidation/Public/EditorValidatorSubsystem.h`

```cpp
{
    // 在此作用域内，保存时验证被临时禁用
    FScopedDisableValidateOnSave DisableScope;

    // 批量保存操作，不会触发验证
    SaveMultipleAssets();
}
// 离开作用域后，验证自动恢复
```

### 进阶用法：通过模块接口验证

来源：`Source/DataValidation/Public/DataValidationModule.h`

```cpp
#include "DataValidationModule.h"

if (IDataValidationModule::IsAvailable())
{
    IDataValidationModule& DVModule = IDataValidationModule::Get();
    DVModule.ValidateAssets(SelectedAssets, /*bValidateDependencies=*/true,
        EDataValidationUsecase::Manual);
}
```

### 进阶用法：Changelist 验证

来源：`Source/DataValidation/Public/DataValidationChangelist.h`

```cpp
#include "DataValidationChangelist.h"
#include "EditorValidatorSubsystem.h"

// 从 SCC changelist 初始化
UDataValidationChangelist* CL = NewObject<UDataValidationChangelist>();
CL->Initialize(SourceControlChangelistPtr);

// 验证 changelist
FValidateAssetsSettings Settings;
FValidateAssetsResults Results;
EDataValidationResult CLResult = ValidationSubsystem->ValidateChangelist(
    CL, Settings, Results);
```

## Demo 示例

### 最小自定义验证器

**MyTextureValidator.h**
```cpp
#pragma once
#include "EditorValidatorBase.h"
#include "MyTextureValidator.generated.h"

class UTexture2D;

UCLASS()
class UMyTextureValidator : public UEditorValidatorBase
{
    GENERATED_BODY()

protected:
    virtual bool CanValidateAsset_Implementation(
        const FAssetData& InAssetData,
        UObject* InObject,
        FDataValidationContext& InContext) const override;
    virtual EDataValidationResult ValidateLoadedAsset_Implementation(
        const FAssetData& InAssetData,
        UObject* InAsset,
        FDataValidationContext& Context) override;
};
```

**MyTextureValidator.cpp**
```cpp
#include "MyTextureValidator.h"
#include "Engine/Texture2D.h"
#include "Misc/DataValidation.h"

bool UMyTextureValidator::CanValidateAsset_Implementation(
    const FAssetData& InAssetData, UObject* InObject,
    FDataValidationContext& InContext) const
{
    return InObject && InObject->IsA<UTexture2D>();
}

EDataValidationResult UMyTextureValidator::ValidateLoadedAsset_Implementation(
    const FAssetData& InAssetData, UObject* InAsset,
    FDataValidationContext& Context)
{
    UTexture2D* Texture = Cast<UTexture2D>(InAsset);
    if (!Texture)
    {
        return EDataValidationResult::NotValidated;
    }

    // 检查纹理尺寸是否为 2 的幂次方
    int32 SizeX = Texture->GetSizeX();
    int32 SizeY = Texture->GetSizeY();
    bool bIsPowerOfTwoX = (SizeX & (SizeX - 1)) == 0;
    bool bIsPowerOfTwoY = (SizeY & (SizeY - 1)) == 0;

    if (!bIsPowerOfTwoX || !bIsPowerOfTwoY)
    {
        AssetFails(InAsset, FText::Format(
            NSLOCTEXT("TexValidator", "NotPOT",
                "Texture dimensions ({0}x{1}) are not powers of 2."),
            FText::AsNumber(SizeX), FText::AsNumber(SizeY)));
        return EDataValidationResult::Invalid;
    }

    AssetPasses(InAsset);
    return EDataValidationResult::Valid;
}
```

**Build.cs 依赖：**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "DataValidation"
});
```

## 模块依赖

从 `DataValidation.Build.cs` 的 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和工具 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `TargetPlatform` | 目标平台信息（材质验证用） |
| `EditorSubsystem` | Editor Subsystem 框架 |
| `DeveloperSettings` | 项目设置基类 |
| `UnrealEd` | 编辑器框架 |
| `AssetRegistry` | 资产注册表查询 |
| `SourceControl` | 源码管理集成（SCC PreSubmit） |
| `UncontrolledChangelists` | 未受控 changelist 支持 |
| `Slate` / `SlateCore` | UI 框架（Message Log 等） |
| `ToolMenus` | 编辑器菜单扩展 |
| `BlueprintGraph` / `KismetCompiler` | 蓝图验证器支持 |
| `Blutility` | 编辑器工具蓝图支持 |

**使用者需要依赖的模块：** 如果只是创建自定义验证器（继承 `UEditorValidatorBase`），你的模块只需依赖 `DataValidation` 即可，它会传递性地引入所需依赖。

## 内置验证器

插件自带以下验证器：

| 验证器 | 功能 | 触发条件 |
|---|---|---|
| `UEditorValidator_Material` | 检查材质/材质实例的着色器翻译和编译是否在目标平台上成功 | 手动/Cook（保存和Commandlet默认禁用，可通过 CVar `Editor.EnableMaterialAssetValidator` 启用） |
| `UEditorValidator_Localization` | 验证 L10N 文件夹中的本地化资产与源资产类型一致 | 所有 L10N 路径下的资产 |
| `UDirtyFilesChangelistValidator` | 检查即将提交的 changelist 中是否有未保存的文件 | SCC PreSubmit |
| `UWorldPartitionChangelistValidator` | 验证 World Partition changelist 中的 actor 和 data layer 引用是否有效 | SCC PreSubmit（World Partition 地图） |
| `UPackageFileValidator` | 检查包文件磁盘格式是否损坏（验证 summary、trailer、payload hash） | 所有包文件 |

## 项目设置

在 **Editor > Advanced > Data Validation** 中可配置：

| 设置 | 默认值 | 说明 |
|---|---|---|
| `bValidateOnSave` | `true` | 保存时是否自动验证 |
| `bLoadAssetsWhenValidatingChangelists` | `true` | 验证 changelist 时是否加载资产 |
| `bEnableMaterialValidation` | `true` | 是否启用材质验证 |
| `MaterialValidationPlatforms` | 空 | 材质验证的目标平台列表 |

Subsystem 级别配置（在 `EditorValidatorSubsystem` 的 Config 中）：

| 设置 | 说明 |
|---|---|
| `ExcludedDirectories` | 排除验证的目录列表（如测试资产目录） |
| `bAllowBlueprintValidators` | 是否允许蓝图验证器（默认 `true`） |

## Commandlet 用法

在 CI/CD 中使用 `DataValidationCommandlet` 进行批量验证：

```bash
# 验证所有项目资产（排除引擎资产）
UnrealEditor-Cmd.exe MyProject -run=DataValidation

# 包含引擎资产
UnrealEditor-Cmd.exe MyProject -run=DataValidation -includeengine

# 只验证特定类型
UnrealEditor-Cmd.exe MyProject -run=DataValidation -AssetType=Texture2D

# 只验证磁盘上的资产
UnrealEditor-Cmd.exe MyProject -run=DataValidation -IncludeOnlyOnDiskAssets
```

返回值：`0` 表示成功，`2` 表示验证过程中发现错误。

## Fixer 系统

DataValidation 还包含一个 **Fixer（修复器）** 框架（`DataValidationFixers.h`），允许验证器在报告错误的同时提供一键修复方案：

| Fixer 类型 | 说明 |
|---|---|
| `TLambdaFixer` | 由 lambda 构造的简单修复器 |
| `FSingleUseFixer` | 包装另一个修复器使其只能执行一次 |
| `FObjectSetDependentFixer` | 带依赖关系的修复器 |
| `FAutoSavingFixer` | 修复后自动保存资产 |
| `FValidatingFixer` | 修复后自动重新验证资产 |
| `FMutuallyExclusiveFixSet` | 互斥修复集合（只能选一个应用） |

修复器通过 `FFixToken` 附加到验证消息上，在 Message Log 中显示为可点击的修复按钮。

## 模块接口

通过 `IDataValidationModule` 可以从其他模块访问 DataValidation 功能：

```cpp
// 检查模块是否可用
if (IDataValidationModule::IsAvailable())
{
    // 获取模块接口
    IDataValidationModule& DVModule = IDataValidationModule::Get();

    // 验证资产（带依赖）
    DVModule.ValidateAssets(SelectedAssets, true, EDataValidationUsecase::Manual);
}
```

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-08-14 | `16e2e4a57a4c` | 合并材质验证器中跨着色器平台的相同错误信息，减少重复报告 |
| 2025-08-08 | `907a4871d9c6` | 加载验证器时添加进度条（SlowTask），改善大量验证器时的用户体验 |
| 2025-08-07 | `19456f2f09ee` | 在日志记录前添加额外的空指针检查，增强稳定性 |

### 维护评价

DataValidation 是 UE5 的**核心编辑器插件**，自 2017 年创建以来持续维护。2025 年 8 月仍有实质性更新（材质验证器优化、UX 改进、稳定性修复），表明该插件处于**活跃维护**状态。

**优势：**
- 作为 `EnabledByDefault` 的 Editor 插件，是 Epic 官方推荐的资产验证方案
- 架构可扩展：C++、蓝图、Python 均可创建自定义验证器
- 深度集成编辑器工作流：保存验证、SCC PreSubmit、Cook 验证、Commandlet 批量验证
- 支持 Changelist 级别的验证，适合 Perforce 工作流

**限制：**
- 材质验证器在保存和 Commandlet 模式下默认禁用（性能考虑），需手动通过 CVar 启用
- 验证器自动发现机制依赖 `GetDerivedClasses`，热重载 C++ 模块时可能需要重启编辑器
- `UEditorValidatorSubsystem` 可被子类化替换，但子类化后的行为需要自行保证兼容性

**推荐：** ✅ 强烈推荐在所有项目中使用。即使不创建自定义验证器，内置的包文件验证、材质验证和 SCC 集成也能显著提升资产质量。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/DataValidation)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/DataValidation/Source/DataValidation/Private/DataValidationTestActor.cpp) — 插件内置的测试 Actor，通过 `bPassValidation` 属性控制验证结果
