# MetaHuman SDK Editor

> Utilities and tools for working with MetaHumans in Unreal Engine.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、本地化资源） |
| 模块 | `MetaHumanSDKRuntime` (Runtime), `MetaHumanSDKEditor` (Editor), `InterchangeDNA` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanSDK/Source/MetaHumanSDKEditor) | |

## 用途

MetaHumanSDKEditor 是 MetaHuman SDK 的编辑器模块，提供了在 UE 编辑器中导入、验证、打包和管理 MetaHuman 角色及其配套资产（服装、发型）的完整工具链。该模块解决以下核心问题：

1. **MetaHuman 导入**：从 Quixel Bridge 或本地 zip 包导入 MetaHuman 角色到项目中，处理资产版本兼容性检查、文件覆盖冲突和批量导入
2. **资产验证**：提供可扩展的验证规则系统，检查 MetaHuman 角色、发型（Groom）、骨骼服装（Skeletal Clothing）和 Outfit 服装是否符合 MetaHuman 兼容标准
3. **资产打包**：将 MetaHuman 角色及其依赖项打包为 `.mharchive` 文件，支持跨项目共享
4. **云服务集成**：通过 EOS（Epic Online Services）进行身份验证，调用云端 Auto-Rig 和纹理合成服务
5. **项目工具**：枚举项目中已安装的 MetaHuman，管理导入路径和打包路径配置

该模块是纯 Editor 类型，仅在编辑器中加载，不会包含在打包构建中。

## 使用场景

- 你从 Quixel Bridge 下载了一个 MetaHuman 并想导入到 UE 项目 → 使用 `FMetaHumanImport::ImportMetaHuman()` 或通过 Quixel Bridge 自动集成
- 你需要验证自定义的发型资产是否符合 MetaHuman 标准 → 使用 `UVerifyMetaHumanGroom` 验证规则
- 你想将一个 MetaHuman 及其所有依赖项打包为一个可分享的归档文件 → 使用 `UMetaHumanAssetManager::CreateArchive()`
- 你需要在 CI/CD 中自动化验证 MetaHuman 资产 → 使用 `UMetaHumanVerificationRuleCollection` 组合验证规则并生成报告
- 你想在编辑器中调用云端 Auto-Rig 服务来生成面部骨骼 → 使用 `FAutoRigServiceRequest`
- 你需要管理项目中所有已安装的 MetaHuman 列表 → 使用 `FMetaHumanProjectUtilities::GetInstalledMetaHumans()`

## 蓝图用法

MetaHumanSDKEditor 的核心类大量使用 `BlueprintCallable` 和 `BlueprintType` 标记，可在蓝图中直接使用。

### 资产管理核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindAssetsForPackaging` | 按类型查找项目中可打包的 MetaHuman 资产 | `UMetaHumanAssetManager` |
| `IsAssetOfType` | 检查一个资产是否为指定类型的 MetaHuman 资产 | `UMetaHumanAssetManager` |
| `CreateArchive` | 将 MetaHuman 资产及其依赖打包为 zip 归档 | `UMetaHumanAssetManager` |
| `UpdateAssetDependencies` | 更新 MetaHuman 资产的依赖关系信息 | `UMetaHumanAssetManager` |
| `UpdateAssetDetails` | 更新 MetaHuman 资产的详细信息（LOD 数、顶点数等） | `UMetaHumanAssetManager` |
| `ImportArchive` | 异步导入 MetaHuman 归档文件到项目 | `UMetaHumanAssetManager` |

### 验证系统核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddVerificationRule` | 向验证集合添加一条验证规则 | `UMetaHumanVerificationRuleCollection` |
| `ApplyAllRules` | 对目标资产运行所有已注册的验证规则 | `UMetaHumanVerificationRuleCollection` |
| `Verify` | 对单个资产执行验证（由子类实现具体逻辑） | `UMetaHumanVerificationRuleBase` |

### 报告系统核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSubject` | 设置报告标题（通常是资产名称） | `UMetaHumanAssetReport` |
| `AddInfo` | 添加信息性消息 | `UMetaHumanAssetReport` |
| `AddWarning` | 添加警告消息（标记报告含警告） | `UMetaHumanAssetReport` |
| `AddError` | 添加错误消息（标记报告为失败） | `UMetaHumanAssetReport` |
| `GenerateHtmlReport` | 生成 HTML 格式的报告 | `UMetaHumanAssetReport` |
| `GenerateJsonReport` | 生成 JSON 格式的报告 | `UMetaHumanAssetReport` |
| `GenerateRawReport` | 生成纯文本格式的报告 | `UMetaHumanAssetReport` |
| `GetReportResult` | 获取报告的最终结果（Success / Failure） | `UMetaHumanAssetReport` |

### 蓝图验证选项

| 节点 | 说明 | 所在类 |
|---|---|---|
| `bVerbose` | 是否在报告中包含详细信息 | `FMetaHumanVerificationOptions` |
| `bTreatWarningsAsErrors` | 将警告视为错误 | `FMetaHumanVerificationOptions` |
| `bVerifyPackagingRules` | 是否验证打包规则 | `FMetaHumanVerificationOptions` |

### 使用示例（蓝图描述）

**验证 MetaHuman 资产并生成报告：**

1. 创建一个 `UMetaHumanAssetReport` 对象
2. 调用 `SetSubject` 设置报告标题为资产名称
3. 创建一个 `UMetaHumanVerificationRuleCollection` 对象
4. 添加验证规则：`AddVerificationRule`（如 `UVerifyMetaHumanGroom`、`UVerifyMetaHumanSkeletalClothing` 等）
5. 调用 `ApplyAllRules` 并传入目标资产、报告对象和选项
6. 调用 `GetReportResult` 检查结果，或调用 `GenerateHtmlReport` 导出报告

**打包 MetaHuman 资产：**

1. 调用 `FindAssetsForPackaging(EMetaHumanAssetType::Character)` 获取可打包的角色列表
2. 选择需要打包的资产
3. 调用 `CreateArchive` 并指定输出路径，生成 `.mharchive` 文件

## C++ 用法

### 头文件引入

```cpp
// 导入功能
#include "Import/MetaHumanImport.h"

// 验证系统
#include "Verification/MetaHumanVerificationRuleCollection.h"
#include "Verification/VerifyMetaHumanGroom.h"
#include "Verification/VerifyMetaHumanCharacter.h"
#include "Verification/VerifyMetaHumanSkeletalClothing.h"
#include "Verification/VerifyMetaHumanOutfitClothing.h"

// 资产管理与打包
#include "ProjectUtilities/MetaHumanAssetManager.h"
#include "ProjectUtilities/MetaHumanProjectUtilities.h"

// 报告系统
#include "MetaHumanAssetReport.h"

// 云服务
#include "Cloud/MetaHumanServiceRequest.h"
#include "Cloud/MetaHumanCloudAuthentication.h"
#include "Cloud/MetaHumanTextureSynthesisServiceRequest.h"
#include "Cloud/MetaHumanARServiceRequest.h"

// 类型与版本
#include "MetaHumanTypesEditor.h"

// 设置
#include "MetaHumanSDKSettings.h"
```

### 基本用法 — 导入 MetaHuman

从 Quixel Bridge 导入一个 MetaHuman 的核心流程（来源：`Private/Import/MetaHumanImport.cpp`）：

```cpp
using namespace UE::MetaHuman;

// 获取导入器单例
TSharedPtr<FMetaHumanImport> Importer = FMetaHumanImport::Get();

// 设置自动化处理器（用于 CI 测试或脚本）
Importer->SetAutomationHandler(MyAutomationHandler);

// 配置导入参数
FMetaHumanImportDescription ImportDesc;
ImportDesc.CharacterName = TEXT("MyMetaHuman");
ImportDesc.CharacterPath = TEXT("/path/to/character");
ImportDesc.CommonPath = TEXT("/path/to/common");
ImportDesc.DestinationPath = TEXT("/Game/MetaHumans");
ImportDesc.bForceUpdate = false;

// 执行导入
TOptional<UObject*> Result = Importer->ImportMetaHuman(ImportDesc);
if (Result.IsSet())
{
    // 导入成功，Result.GetValue() 为主资产
}
```

### 基本用法 — 资产验证

使用验证规则系统检查资产兼容性（来源：`Private/Verification/`）：

```cpp
using namespace UE::MetaHuman;

// 创建报告
UMetaHumanAssetReport* Report = NewObject<UMetaHumanAssetReport>();
Report->SetSubject(TEXT("MyGroom"));
Report->SetVerbose(true);

// 创建验证选项
FMetaHumanVerificationOptions Options;
Options.bVerbose = true;
Options.bTreatWarningsAsErrors = false;
Options.bVerifyPackagingRules = true;

// 创建验证规则集合
UMetaHumanVerificationRuleCollection* RuleCollection = NewObject<UMetaHumanVerificationRuleCollection>();

// 添加验证规则
UMetaHumanVerificationRuleBase* GroomRule = NewObject<UVerifyMetaHumanGroom>();
RuleCollection->AddVerificationRule(GroomRule);

UMetaHumanVerificationRuleBase* PackageRule = NewObject<UVerifyMetaHumanPackageSource>();
RuleCollection->AddVerificationRule(PackageRule);

// 运行所有规则
UMetaHumanAssetReport* Result = RuleCollection->ApplyAllRules(MyGroomAsset, Report, Options);

// 检查结果
if (Result->GetReportResult() == EMetaHumanOperationResult::Success)
{
    UE_LOG(LogMetaHumanSDK, Log, TEXT("Verification passed"));
}
else
{
    FString HtmlReport = Result->GenerateHtmlReport();
    // 输出或保存报告
}
```

### 进阶用法 — 资产管理与打包

使用 `UMetaHumanAssetManager` 发现、描述和打包 MetaHuman 资产：

```cpp
// 查找项目中所有可打包的角色资产
TArray<FMetaHumanAssetDescription> Characters =
    UMetaHumanAssetManager::FindAssetsForPackaging(EMetaHumanAssetType::Character);

// 更新每个资产的依赖和详细信息
for (FMetaHumanAssetDescription& CharDesc : Characters)
{
    UMetaHumanAssetManager::UpdateAssetDependencies(CharDesc);
    UMetaHumanAssetManager::UpdateAssetDetails(CharDesc);
}

// 打包为归档文件
TArray<FMetaHumanAssetDescription> SelectedAssets;
SelectedAssets.Add(Characters[0]);
bool bSuccess = UMetaHumanAssetManager::CreateArchive(SelectedAssets, TEXT("C:/Exports/MyMetaHuman.mharchive"));

// 异步导入归档文件
FMetaHumanImportOptions ImportOptions;
ImportOptions.bForceUpdate = false;
ImportOptions.bVerbose = true;
UMetaHumanAssetReport* ImportReport = NewObject<UMetaHumanAssetReport>();

TFuture<bool> ImportFuture = UMetaHumanAssetManager::ImportArchive(
    TEXT("C:/Exports/MyMetaHuman.mharchive"), ImportOptions, ImportReport);

ImportFuture.Then([](TFuture<bool> Future)
{
    bool bImported = Future.Get();
    // 处理导入结果
});
```

### 进阶用法 — 云服务请求

调用云端 Auto-Rig 和纹理合成服务：

```cpp
using namespace UE::MetaHuman;

// ---- 身份验证 ----
// 检查是否已登录
ServiceAuthentication::CheckHasLoggedInUserAsync(
    FOnCheckHasLoggedInUserCompleteDelegate::CreateLambda(
        [](bool bLoggedIn, FString AccountId, FString UserName)
        {
            if (bLoggedIn)
            {
                UE_LOG(LogMetaHumanSDK, Log, TEXT("Logged in as %s"), *UserName);
            }
        }));

// 登录
ServiceAuthentication::LoginToAuthEnvironment(
    FOnLoginCompleteDelegate::CreateLambda([](FString AccountId) { /* 成功 */ }),
    FOnLoginFailedDelegate::CreateLambda([]() { /* 失败 */ }));

// ---- Auto-Rig 请求 ----
FTargetSolveParameters SolveParams;
SolveParams.ConformedFaceVertices = MyFaceVertices;
SolveParams.HighFrequency = 0;
SolveParams.RigType = ERigType::JointsAndBlendshapes;
SolveParams.Scale = 1.0f;

TSharedRef<FAutoRigServiceRequest> AutoRigRequest =
    FAutoRigServiceRequest::CreateRequest(SolveParams);

AutoRigRequest->AutorigRequestCompleteDelegate.BindLambda(
    [](const FAutorigResponse& Response)
    {
        if (Response.IsValid())
        {
            // Response.Dna 包含生成的 DNA 数据
            TSharedPtr<IDNAReader> DnaReader = Response.Dna;
        }
    });

AutoRigRequest->OnMetaHumanServiceRequestFailedDelegate.BindLambda(
    [](EMetaHumanServiceRequestResult Result)
    {
        // 处理错误
    });

AutoRigRequest->RequestSolveAsync();

// ---- 面部纹理合成请求 ----
TSharedRef<FFaceTextureSynthesisServiceRequest> TextureRequest =
    detail::FTextureSynthesisServiceRequestBase::CreateRequest(
        FFaceTextureRequestCreateParams{ .HighFrequency = 0 });

TextureRequest->FaceTextureSynthesisRequestCompleteDelegate.BindLambda(
    [](TSharedPtr<FFaceHighFrequencyData> Data)
    {
        // 处理合成的纹理数据
    });

TArray<FFaceTextureRequestParams> TexturesToRequest = {
    { EFaceTextureType::BaseColor, 1024 },
    { EFaceTextureType::Normal, 1024 }
};
TextureRequest->RequestTexturesAsync(TexturesToRequest);
```

### 进阶用法 — MetaHuman 版本管理

使用版本系统确保资产兼容性（来源：`Private/MetaHumanTypesEditor.cpp`）：

```cpp
using namespace UE::MetaHuman;

// 读取 MetaHuman 版本
FMetaHumanVersion Version = FMetaHumanVersion::ReadFromFile(TEXT("/path/to/VersionInfo.txt"));

// 比较版本
FMetaHumanVersion CurrentVersion(TEXT("2.1.0"));
if (Version.IsCompatible(CurrentVersion))
{
    UE_LOG(LogMetaHumanSDK, Log, TEXT("版本兼容"));
}

// 使用 SourceMetaHuman 读取已导出 MetaHuman 的信息
FSourceMetaHuman SourceMH(TEXT("/path/to/character"), TEXT("/path/to/common"), TEXT("MyMH"));
FString Name = SourceMH.GetName();
FMetaHumanVersion SrcVersion = SourceMH.GetVersion();
EMetaHumanQualityLevel Quality = SourceMH.GetQualityLevel();
bool bIsUEFN = SourceMH.IsUEFN();
```

### 进阶用法 — 项目工具

列出和管理项目中已安装的 MetaHuman（来源：`Private/ProjectUtilities/MetaHumanProjectUtilities.cpp`）：

```cpp
using namespace UE::MetaHuman;

// 获取项目中所有已安装的 MetaHuman
TArray<FInstalledMetaHuman> Installed = FMetaHumanProjectUtilities::GetInstalledMetaHumans();
for (const FInstalledMetaHuman& MH : Installed)
{
    FString RootAsset = MH.GetRootAsset();
    FName RootPackage = MH.GetRootPackage();
    FMetaHumanVersion Version = MH.GetVersion();
    EMetaHumanQualityLevel Quality = MH.GetQualityLevel();
    FString CommonPath = MH.GetCommonAssetPath();
}

// 配置导入路径（也可在项目设置中配置）
UMetaHumanSDKSettings* Settings = GetMutableDefault<UMetaHumanSDKSettings>();
Settings->CinematicImportPath.Path = TEXT("/Game/MetaHumans");
Settings->OptimizedImportPath.Path = TEXT("/Game/MetaHumans");
```

## Demo 示例

以下示例展示如何创建一个自定义验证规则并在蓝图中使用：

```cpp
// MyCustomVerificationRule.h
#pragma once

#include "Verification/MetaHumanVerificationRuleCollection.h"
#include "MyCustomVerificationRule.generated.h"

UCLASS(BlueprintType)
class UMyCustomVerificationRule : public UMetaHumanVerificationRuleBase
{
    GENERATED_BODY()

public:
    virtual void Verify_Implementation(
        const UObject* ToVerify,
        UMetaHumanAssetReport* Report,
        const FMetaHumanVerificationOptions& Options) const override
    {
        if (!ToVerify)
        {
            FMetaHumanAssetReportItem ErrorItem;
            ErrorItem.Message = FText::FromString(TEXT("目标对象为空"));
            Report->AddError(ErrorItem);
            return;
        }

        // 自定义验证逻辑
        FMetaHumanAssetReportItem InfoItem;
        InfoItem.Message = FText::FromString(
            FString::Printf(TEXT("已验证资产: %s"), *ToVerify->GetName()));
        Report->AddInfo(InfoItem);
    }
};
```

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new[]
{
    "Core",
    "Engine",
    "MetaHumanSDKRuntime"
});

PrivateDependencyModuleNames.AddRange(new[]
{
    "MetaHumanSDKEditor"
});
```

## 模块依赖

MetaHumanSDKEditor 的公共依赖（使用者必须引用）：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `Engine` | 引擎核心功能 |
| `MetaHumanSDKRuntime` | MetaHuman 运行时模块（类型定义、组件） |

MetaHumanSDKEditor 的私有依赖（使用者无需关心）：

| 模块 | 用途 |
|---|---|
| `AssetDefinition` | 资产类型定义框架 |
| `BlueprintGraph` | 蓝图图表支持 |
| `ContentBrowser` | 内容浏览器集成 |
| `ControlRig` / `ControlRigDeveloper` | Control Rig 动画系统集成 |
| `DerivedDataCache` | 派生数据缓存 |
| `EditorScriptingUtilities` | 编辑器脚本工具 |
| `HairStrandsCore` | Groom（毛发）系统核心 |
| `HTTP` | HTTP 网络请求（云服务通信） |
| `Json` / `JsonUtilities` | JSON 序列化 |
| `MeshDescription` / `StaticMeshDescription` | 网格体描述 |
| `RigLogicModule` / `RigLogicDeveloper` | Rig Logic 面部动画系统 |
| `RigVMDeveloper` | Rig VM 开发者工具 |
| `Slate` / `SlateCore` / `ToolMenus` / `ToolWidgets` | UI 框架 |
| `UnrealEd` | 编辑器核心 |
| `EOSSDK` / `EOSShared` | Epic Online Services 身份认证（仅编辑器目标） |
| `zlib`（第三方） | 归档文件压缩 |
| `Protobuf`（第三方） | 云服务请求序列化格式 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-10-10 | `9585d26c9f7f` | 添加对包含 Virtual Texture 或 Substrate 材质的 MetaHuman 包的验证警告 |
| 2025-10-03 | `15c2d59e870e` | 检测可能与用户项目设置不兼容的引擎特性（Substrate 材质、Virtual Texture 流式传输），并在导入时发出警告 |
| 2025-10-01 | `b35afec6a307` | 修复阿拉伯语本地化问题 |

### 维护评价

- **活跃维护**：该模块于 2025 年 4 月创建，距今约 1 年，近期（2025 年 10 月）仍在活跃更新
- 最近的更新聚焦于资产兼容性检测和项目设置适配，表明 Epic 在持续改进导入和打包流程
- 作为 MetaHuman 工作流的核心编辑器组件，该模块将随 MetaHuman 产品线持续演进
- **推荐使用**：这是 Epic 官方维护的 MetaHuman 编辑器工具链，是处理 MetaHuman 资产导入、验证和打包的标准方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanSDK/Source/MetaHumanSDKEditor)
- [插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanSDK)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanSDK/Source/MetaHumanSDKEditor/Private/Tests)
- [MetaHumanSDKRuntime 文档](./MetaHumanSDKRuntime.md)
