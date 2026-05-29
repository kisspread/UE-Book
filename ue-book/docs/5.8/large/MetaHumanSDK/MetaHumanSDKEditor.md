# MetaHuman SDK

> Utilities and tools for working with MetaHumans in Unreal Engine.

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 工具集 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质、管线资产等） |
| 模块 | `InterchangeDNA` (Runtime), `MetaHumanSDKEditor` (Runtime), `MetaHumanSDKRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanSDK) | |

## 用途

MetaHumanSDK 是 Epic 为 MetaHuman 角色工作流提供的**完整资产管理工具集**。它解决的核心问题是：如何在 UE 项目中系统化地发现、验证、打包和导入 MetaHuman 及其关联资产（Groom、服装、配饰等）。

与 Quixel Bridge 的简单"一键导入"不同，MetaHumanSDK 提供了一个**结构化的资产生命周期管理框架**：

- **资产发现**：自动扫描项目中可打包的 MetaHuman 资产（角色、角色组装体、骨骼服装、Outfit 服装、Groom）
- **依赖遍历**：通过 BFS 走访资产依赖图，确保打包时包含所有关联资源
- **验证规则系统**：可扩展的验证框架，检查骨架兼容性、Groom 网格对齐、服装网格标准等
- **归档打包**：将资产及其依赖压缩为 `.mhpkg` 归档文件，支持单个或批量打包
- **版本管理**：语义版本号（Major.Minor.Revision）和资产版本号，处理跨版本升级兼容性
- **云服务集成**：纹理合成（面部/身体）、自动绑定（AutoRig）、TDS 账户管理、EOS 认证
- **MetaHuman Manager UI**：编辑器窗口，支持导航浏览、多选验证/打包、过滤等功能

这个 SDK 同时也是 Quixel Bridge 与 UE 之间 MetaHuman 导入流程的底层实现，处理了资产版本冲突、质量等级切换、批量更新等复杂场景。

## 使用场景

- 你制作了一个自定义 MetaHuman 角色，需要分发给团队其他成员 → 用 `CreateArchive` 打包，对方用 `ImportArchive` 导入
- 你在开发 MetaHuman 相关的 Marketplace 资产（服装、Groom）→ 先用验证规则检查兼容性，再打包
- 你需要从 Quixel Bridge 批量导入或更新多个 MetaHuman → 使用 `FMetaHumanImport` 的批量导入接口
- 你在做自动化 CI/CD 流程，需要验证 MetaHuman 资产质量 → 用 `UMetaHumanVerificationRuleCollection` 运行完整验证套件
- 你需要通过云服务为 MetaHuman 生成高质量纹理或自动绑定 → 使用 `FFaceTextureSynthesisServiceRequest` / `FAutoRigServiceRequest`

## 蓝图用法

### 核心节点 — 资产管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindAssetsForPackaging` | 按类型查找项目中所有可打包的 MetaHuman 资产 | `UMetaHumanAssetManager` |
| `IsAssetOfType` | 检查指定包路径是否为给定类型的可打包资产 | `UMetaHumanAssetManager` |
| `CreateArchive` | 将多个 MetaHuman 资产及其依赖打包为 .mhpkg 归档 | `UMetaHumanAssetManager` |
| `UpdateAssetDependencies` | 更新资产的包依赖列表（打包前必须调用） | `UMetaHumanAssetManager` |
| `UpdateAssetDetails` | 更新资产的技术细节信息（顶点数、LOD 等） | `UMetaHumanAssetManager` |

### 核心节点 — 报告与验证

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSubject` | 设置报告标题（通常是资产名称） | `UMetaHumanAssetReport` |
| `AddInfo` / `AddWarning` / `AddError` | 向报告添加信息/警告/错误消息 | `UMetaHumanAssetReport` |
| `GenerateHtmlReport` | 生成 HTML 格式的报告 | `UMetaHumanAssetReport` |
| `GetReportResult` | 获取报告整体结果（成功/失败） | `UMetaHumanAssetReport` |
| `HasWarnings` | 检查报告是否包含警告 | `UMetaHumanAssetReport` |
| `ApplyAllRules` | 对目标资产运行验证集合中的所有规则 | `UMetaHumanVerificationRuleCollection` |
| `AddVerificationRule` | 向验证集合添加一条规则 | `UMetaHumanVerificationRuleCollection` |

### 核心节点 — TDS 账户

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AcquireTdsAccount` | 获取一个 TDS 临时账户用于云服务认证 | `UMetaHumanTDSUtils` |
| `ReleaseTdsAccount` | 释放 TDS 账户回到资源池 | `UMetaHumanTDSUtils` |

### 使用示例（蓝图描述）

**打包 MetaHuman 资产的完整流程：**

1. 创建 `FMetaHumanAssetDescription` 数组，调用 `FindAssetsForPackaging(Character)` 获取所有可打包的角色资产
2. 对每个资产描述调用 `UpdateAssetDependencies` 填充依赖信息
3. 对每个资产描述调用 `UpdateAssetDetails` 填充技术细节
4. 调用 `CreateArchive`，传入资产数组和输出文件路径（如 `C:/Exports/MyMetaHuman.mhpkg`）
5. 检查返回值确认打包成功

**验证 MetaHuman Groom 兼容性：**

1. 创建 `UMetaHumanAssetReport` 对象
2. 创建 `UMetaHumanVerificationRuleCollection`，添加 `UVerifyMetaHumanGroom` 规则
3. 调用 `ApplyAllRules`，传入 Groom 资产对象、报告对象和验证选项
4. 读取报告的 `Warnings` 和 `Errors` 数组，或调用 `GenerateHtmlReport` 查看

## C++ 用法

### 头文件引入

```cpp
#include "ProjectUtilities/MetaHumanAssetManager.h"    // 资产管理核心 API
#include "Import/MetaHumanImport.h"                     // 导入流程
#include "MetaHumanAssetReport.h"                       // 验证报告
#include "Verification/MetaHumanVerificationRuleCollection.h" // 验证规则
#include "MetaHumanTypesEditor.h"                       // 类型定义（版本号等）
#include "ProjectUtilities/MetaHumanProjectUtilities.h" // 项目工具函数
```

### 基本用法 — 发现并打包 MetaHuman 资产

```cpp
#include "ProjectUtilities/MetaHumanAssetManager.h"

// 1. 查找项目中所有可打包的 MetaHuman 角色
TArray<FMetaHumanAssetDescription> Assets = UMetaHumanAssetManager::FindAssetsForPackaging(
    EMetaHumanAssetType::Character
);

// 2. 更新每个资产的依赖和详情
for (FMetaHumanAssetDescription& Asset : Assets)
{
    UMetaHumanAssetManager::UpdateAssetDependencies(Asset);
    UMetaHumanAssetManager::UpdateAssetDetails(Asset);
}

// 3. 打包到归档文件
bool bSuccess = UMetaHumanAssetManager::CreateArchive(Assets, TEXT("/tmp/MyMetaHuman.mhpkg"));
```
*来源：Public/ProjectUtilities/MetaHumanAssetManager.h*

### 基本用法 — 异步导入 MetaHuman

```cpp
#include "Import/MetaHumanImport.h"

using namespace UE::MetaHuman;

// 配置导入参数
FMetaHumanImportDescription ImportDesc;
ImportDesc.CharacterPath = TEXT("C:/MetaHumans/Ada/SourceAssets");
ImportDesc.CommonPath = TEXT("C:/MetaHumans/Common");
ImportDesc.CharacterName = TEXT("Ada");
ImportDesc.DestinationPath = TEXT("/Game/MetaHumans");
ImportDesc.bForceUpdate = false;

// 获取导入单例并执行异步导入
TSharedPtr<FMetaHumanImport> Importer = FMetaHumanImport::Get();
TOptional<UObject*> Result = Importer->ImportMetaHuman(ImportDesc);

if (Result.IsSet())
{
    UObject* MainAsset = Result.GetValue();
    // 导入成功，MainAsset 是主蓝图资产
}
```
*来源：Public/Import/MetaHumanImport.h*

### 基本用法 — 资产验证

```cpp
#include "MetaHumanAssetReport.h"
#include "Verification/MetaHumanVerificationRuleCollection.h"
#include "Verification/VerifyMetaHumanGroom.h"
#include "Verification/VerifyMetaHumanSkeletalClothing.h"

// 创建报告和验证集合
UMetaHumanAssetReport* Report = NewObject<UMetaHumanAssetReport>();
Report->SetSubject(TEXT("MyGroom"));

UMetaHumanVerificationRuleCollection* Rules = NewObject<UMetaHumanVerificationRuleCollection>();

// 添加验证规则
UVerifyMetaHumanGroom* GroomRule = NewObject<UVerifyMetaHumanGroom>();
GroomRule->bDetailedGroomingMeshVerification = true;
GroomRule->bVerifyGroomToMeshAlignment = true;
Rules->AddVerificationRule(GroomRule);

UVerifyMetaHumanSkeletalClothing* ClothingRule = NewObject<UVerifyMetaHumanSkeletalClothing>();
Rules->AddVerificationRule(ClothingRule);

// 运行验证
FMetaHumanVerificationOptions Options;
Options.bVerbose = true;
Options.bTreatWarningsAsErrors = false;

Rules->ApplyAllRules(TargetAsset, Report, Options);

// 检查结果
if (Report->GetReportResult() == EMetaHumanOperationResult::Failure)
{
    FString HtmlReport = Report->GenerateHtmlReport();
    UE_LOG(LogMetaHumanSDK, Error, TEXT("验证失败:\n%s"), *HtmlReport);
}
else if (Report->HasWarnings())
{
    UE_LOG(LogMetaHumanSDK, Warning, TEXT("验证通过，但有警告"));
}
```
*来源：Public/MetaHumanAssetReport.h, Public/Verification/MetaHumanVerificationRuleCollection.h*

### 进阶用法 — 自定义验证规则

```cpp
#include "Verification/MetaHumanVerificationRuleCollection.h"
#include "MetaHumanAssetReport.h"

// 在蓝图或 C++ 中创建自定义验证规则（继承 UMetaHumanVerificationRuleBase）
UCLASS(BlueprintType)
class UVerifyMyCustomAsset : public UMetaHumanVerificationRuleBase
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
            Report->AddError({ FText::FromString(TEXT("资产为空")) });
            return;
        }

        // 自定义验证逻辑
        if (Options.bVerbose)
        {
            Report->AddVerbose({
                FText::FromString(FString::Printf(TEXT("正在验证: %s"), *ToVerify->GetName()))
            });
        }

        // ... 你的验证逻辑 ...
    }
};
```
*来源：Public/Verification/MetaHumanVerificationRuleCollection.h, Public/Verification/VerifyObjectValid.h*

### 进阶用法 — 使用自动化接口跳过 UI

```cpp
#include "ProjectUtilities/MetaHumanProjectUtilities.h"
#include "Import/MetaHumanImport.h"

using namespace UE::MetaHuman;

// 实现自动化处理器（用于 CI 或测试）
class FMyAutomationHandler : public IMetaHumanImportAutomationHandler
{
public:
    virtual bool ShouldContinueWithBreakingMetaHumans(
        const TArray<FString>& IncompatibleMetaHumans,
        const TArray<FString>& UpdatedFiles) override
    {
        // 在自动化模式下总是继续导入
        return true;
    }
};

// 启用自动化模式
static FMyAutomationHandler Handler;
FMetaHumanProjectUtilities::EnableAutomation(&Handler);

// 现在导入操作不会弹出 UI 对话框
FMetaHumanImportDescription ImportDesc;
ImportDesc.CharacterPath = TEXT("/path/to/source");
ImportDesc.CommonPath = TEXT("/path/to/common");
ImportDesc.CharacterName = TEXT("TestCharacter");
FMetaHumanProjectUtilities::ImportMetaHuman(ImportDesc);
```
*来源：Public/ProjectUtilities/MetaHumanProjectUtilities.h, Public/Import/MetaHumanImport.h*

### 进阶用法 — 云服务纹理合成

```cpp
#include "Cloud/MetaHumanTextureSynthesisServiceRequest.h"

using namespace UE::MetaHuman;

// 创建面部纹理合成请求
FFaceTextureRequestCreateParams CreateParams;
CreateParams.HighFrequency = 0; // 高频 ID

TSharedRef<FFaceTextureSynthesisServiceRequest> FaceRequest =
    FFaceTextureSynthesisServiceRequest::CreateRequest(CreateParams);

// 绑定完成委托
FaceRequest->FaceTextureSynthesisRequestCompleteDelegate.BindLambda(
    [](TSharedPtr<FFaceHighFrequencyData> Data)
    {
        if (Data.IsValid())
        {
            // 处理合成的高分辨率纹理数据
            TConstArrayView<uint8> TextureData = (*Data)[EFaceTextureType::Diffuse];
        }
    }
);

// 绑定失败委托
FaceRequest->OnMetaHumanServiceRequestFailedDelegate.BindLambda(
    [](EMetaHumanServiceRequestResult Result)
    {
        UE_LOG(LogMetaHumanSDK, Error, TEXT("纹理合成失败: %d"), (int32)Result);
    }
);

// 发起请求
TArray<FFaceTextureRequestParams> TexturesToRequest;
TexturesToRequest.Add({ EFaceTextureType::Diffuse, 1024 });
TexturesToRequest.Add({ EFaceTextureType::Normal, 1024 });
FaceRequest->RequestTexturesAsync(TexturesToRequest);
```
*来源：Public/Cloud/MetaHumanTextureSynthesisServiceRequest.h*

## Demo 示例

以下是一个完整的可编译示例，展示如何在编辑器中发现 MetaHuman 资产、验证并打包：

```cpp
// MetaHumanAssetPackagingExample.h
#pragma once

#include "CoreMinimal.h"

class UMetaHumanAssetReport;

namespace UE::MetaHuman
{

struct FMetaHumanAssetDescription;

/**
 * 演示如何使用 MetaHuman SDK 发现、验证和打包资产
 */
class FMetaHumanAssetPackagingExample
{
public:
    /** 运行完整的打包流程演示 */
    static void RunPackagingDemo();

private:
    /** 步骤 1: 发现项目中的 MetaHuman 资产 */
    static TArray<FMetaHumanAssetDescription> DiscoverAssets();

    /** 步骤 2: 验证发现的资产 */
    static UMetaHumanAssetReport* VerifyAssets(
        const TArray<FMetaHumanAssetDescription>& Assets);

    /** 步骤 3: 将资产打包为归档 */
    static bool PackageAssets(
        const TArray<FMetaHumanAssetDescription>& Assets,
        const FString& OutputPath);
};

} // namespace UE::MetaHuman
```

```cpp
// MetaHumanAssetPackagingExample.cpp
#include "MetaHumanAssetPackagingExample.h"

#include "ProjectUtilities/MetaHumanAssetManager.h"
#include "MetaHumanAssetReport.h"
#include "Verification/MetaHumanVerificationRuleCollection.h"
#include "Verification/VerifyMetaHumanCharacter.h"
#include "Verification/VerifyMetaHumanGroom.h"
#include "Verification/VerifyMetaHumanSkeletalClothing.h"
#include "Verification/VerifyObjectValid.h"

DEFINE_LOG_CATEGORY_STATIC(LogMetaHumanDemo, Log, All);

namespace UE::MetaHuman
{

void FMetaHumanAssetPackagingExample::RunPackagingDemo()
{
    UE_LOG(LogMetaHumanDemo, Log, TEXT("=== MetaHuman 打包流程演示 ==="));

    // 步骤 1: 发现资产
    TArray<FMetaHumanAssetDescription> Assets = DiscoverAssets();
    if (Assets.Num() == 0)
    {
        UE_LOG(LogMetaHumanDemo, Warning, TEXT("未找到可打包的 MetaHuman 资产"));
        return;
    }
    UE_LOG(LogMetaHumanDemo, Log, TEXT("发现 %d 个资产"), Assets.Num());

    // 步骤 2: 验证资产
    UMetaHumanAssetReport* Report = VerifyAssets(Assets);
    if (Report && Report->GetReportResult() == EMetaHumanOperationResult::Failure)
    {
        UE_LOG(LogMetaHumanDemo, Error, TEXT("验证失败，中止打包"));
        UE_LOG(LogMetaHumanDemo, Log, TEXT("%s"), *Report->GenerateRawReport());
        return;
    }

    // 步骤 3: 打包
    FString OutputPath = FPaths::ProjectSavedDir() / TEXT("MetaHumanExports/DemoPackage.mhpkg");
    if (PackageAssets(Assets, OutputPath))
    {
        UE_LOG(LogMetaHumanDemo, Log, TEXT("打包成功: %s"), *OutputPath);
    }
    else
    {
        UE_LOG(LogMetaHumanDemo, Error, TEXT("打包失败"));
    }
}

TArray<FMetaHumanAssetDescription> FMetaHumanAssetPackagingExample::DiscoverAssets()
{
    TArray<FMetaHumanAssetDescription> AllAssets;

    // 查找各类型资产
    const EMetaHumanAssetType Types[] = {
        EMetaHumanAssetType::Character,
        EMetaHumanAssetType::CharacterAssembly,
        EMetaHumanAssetType::SkeletalClothing,
        EMetaHumanAssetType::OutfitClothing,
        EMetaHumanAssetType::Groom
    };

    for (EMetaHumanAssetType Type : Types)
    {
        TArray<FMetaHumanAssetDescription> Found =
            UMetaHumanAssetManager::FindAssetsForPackaging(Type);

        for (FMetaHumanAssetDescription& Asset : Found)
        {
            UMetaHumanAssetManager::UpdateAssetDependencies(Asset);
            UMetaHumanAssetManager::UpdateAssetDetails(Asset);
        }

        AllAssets.Append(MoveTemp(Found));
    }

    return AllAssets;
}

UMetaHumanAssetReport* FMetaHumanAssetPackagingExample::VerifyAssets(
    const TArray<FMetaHumanAssetDescription>& Assets)
{
    UMetaHumanAssetReport* Report = NewObject<UMetaHumanAssetReport>();
    Report->SetSubject(TEXT("Demo 资产验证"));

    // 构建验证规则集合
    UMetaHumanVerificationRuleCollection* Rules =
        NewObject<UMetaHumanVerificationRuleCollection>();

    // 添加基础有效性检查
    Rules->AddVerificationRule(NewObject<UVerifyObjectValid>());

    // 添加角色专用验证
    Rules->AddVerificationRule(NewObject<UVerifyMetaHumanCharacter>());

    // 添加 Groom 验证（关闭昂贵的详细网格检查以提高速度）
    UVerifyMetaHumanGroom* GroomRule = NewObject<UVerifyMetaHumanGroom>();
    GroomRule->bDetailedGroomingMeshVerification = false;
    GroomRule->bVerifyGroomToMeshAlignment = false;
    Rules->AddVerificationRule(GroomRule);

    // 添加服装验证
    Rules->AddVerificationRule(NewObject<UVerifyMetaHumanSkeletalClothing>());

    // 配置验证选项
    FMetaHumanVerificationOptions Options;
    Options.bVerbose = true;
    Options.bTreatWarningsAsErrors = false;
    Options.bVerifyPackagingRules = true;

    // 对每个资产运行验证
    for (const FMetaHumanAssetDescription& Asset : Assets)
    {
        if (Asset.AssetData.GetAsset())
        {
            Rules->ApplyAllRules(Asset.AssetData.GetAsset(), Report, Options);
        }
    }

    return Report;
}

bool FMetaHumanAssetPackagingExample::PackageAssets(
    const TArray<FMetaHumanAssetDescription>& Assets,
    const FString& OutputPath)
{
    // 确保输出目录存在
    FString OutputDir = FPaths::GetPath(OutputPath);
    IFileManager::Get().MakeDirectory(*OutputDir, true);

    // 创建归档
    return UMetaHumanAssetManager::CreateArchive(Assets, OutputPath);
}

} // namespace UE::MetaHuman
```

## 模块依赖

由于 Build.cs 文件未完整提供，以下基于公开头文件中的引用关系推断：

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | DNA 数据交换管线基础 |
| `InterchangePipelines` | DNA 到 SkeletalMesh 的转换管线 |
| `MetaHumanSDKRuntime` | 运行时支持（DNA 数据、MetaHuman 类型定义等） |
| `PropertyEditor` | 编辑器属性面板集成 |
| `WorkspaceMenuStructure` | MetaHuman Manager 的工作区菜单集成 |

无特殊依赖（仅标准 Core/Engine/Slate/Interchange 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `5c0dc0e5` | [MHSDK] Remove the VersionInfo.txt existence check when discovering MetaHuman character assemblies a | 移除角色组装体发现时的 VersionInfo.txt 存在性检查，放宽发现条件 |
| 2026-05-21 | `418099aa` | Fix the incorrectly converted parent bones for Legacy DNAConfig case | 修复旧版 DNAConfig 场景下父骨骼转换错误 |
| 2026-05-14 | `d477b10c` | [MHSDK] Replace path-based related-asset filtering in MetaHuman Manager with dependency walking now | MetaHuman Manager 用依赖遍历替代路径过滤，资产发现更准确 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `c0e92a2b` | [MHSDK] Fix MetaHuman skeletal clothing verification reading incorrect texture dimensions by ensurin | 修复骨骼服装验证中读取纹理尺寸错误的问题 |

### 维护评价

**活跃维护** ✅

MetaHumanSDK 是一个**非常年轻的插件**（约 1 年），于 2025 年 4 月从实验状态正式毕业为稳定功能。近期（2026 年 5 月）更新非常频繁，几乎每周都有功能性改进和 bug 修复，包括架构升级（从路径过滤到依赖遍历）、兼容性修复（旧版 DNAConfig）、验证逻辑完善等实质性改动。

**优势**：
- 作为 MetaHuman 生态的核心 SDK，由 Epic 团队积极维护
- 覆盖了 MetaHuman 资产管理的完整生命周期
- 提供可扩展的验证框架和自动化接口
- 云服务集成（纹理合成、AutoRig）为高级需求提供支持

**注意事项**：
- 部分功能标记为 `UE_DEPRECATED(5.8)`（如按类型的打包路径），升级时需注意 API 变化
- 云服务功能需要 EOS 认证，非离线可用
- 验证规则中有些检查（如 `bDetailedGroomingMeshVerification`）计算成本较高，生产环境中建议根据需求开关

**推荐**：如果你在做 MetaHuman 相关的开发工作（角色导入/导出、资产分发、质量验证），这是必用的 SDK。对于纯运行时 MetaHuman 渲染/动画需求，则应关注 `MetaHumanSDKRuntime` 模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanSDK)
- 官方文档（无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanSDK/Source/MetaHumanSDKEditor/Public/Tests)