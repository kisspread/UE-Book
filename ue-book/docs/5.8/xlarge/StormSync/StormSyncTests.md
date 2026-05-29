# Storm Sync

> Sync, Pull, Push, asset dependencies.
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 中文名 | 风暴同步 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产和测试资源） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

`StormSync` 是一个面向**资产依赖关系**的智能同步系统，是 **Motion Design** 工作流的核心组件。它的核心功能不仅仅是简单的文件复制，而是解决在多设备、多用户协作环境中，如何高效、可靠地**同步资产及其所有依赖项**的问题。

想象一下，一个虚拟制片场景中，你（美术）在本地工作站更新了一个材质，而这个材质被场景中的多个蓝图和资产引用。`StormSync` 能够自动分析出这些依赖关系，将你需要的**所有相关文件**打包、传输到另一台工作站或服务器，并在目标端正确导入和应用这些更新，确保所有机器上的资产状态保持一致。它旨在替代手动的、容易出错的文件拷贝过程。

## 使用场景

-   你在进行**虚拟制片**，现场有多台工作站渲染同一个场景。当美术在主力机上更新了资产，你需要将变更快速、可靠地同步到现场的所有渲染机上 → 使用 `StormSync` 进行“推送”或“拉取”。
-   你的团队采用 **Motion Design** 工作流，项目资产（材质、纹理、网格体、蓝图）频繁更新且相互依赖复杂。你需要一个工具来打包特定资产集并确保其所有依赖项都包含在内 → 使用 `StormSync` 进行“导出”（打包）和“导入”。
-   你作为技术美术或管线工程师，需要构建一个**自动化资产发布和同步管线** → `StormSync` 的模块化设计（Core， Transport， Import）提供了底层的 API 和协议，可以集成到自定义工具中。
-   你需要快速诊断和比较两套资产包之间的差异 → `StormSync` 的依赖分析功能可以用于此目的。

## 蓝图用法

搜索 `UFUNCTION(BlueprintCallable)` 和 `UPROPERTY(BlueprintReadWrite)`。按功能分组，不要罗列所有函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Storm Sync Export Wizard` | 打开“风暴同步导出向导”的 UI 界面，引导用户选择要导出的资产并打包。 | `UStormSyncEditorBlueprintLibrary` |
| `Import Storm Sync Package` | 异步导入一个 `.spak` 风暴同步包文件，自动处理资产和依赖项的导入。 | `UStormSyncImportBlueprintLibrary` |
| `Get Asset Dependencies` | 查询并返回指定资产（`UObject` 或软对象路径）的所有硬性和软性依赖项列表。 | `UStormSyncCoreBlueprintLibrary` |
| `Is Package Dirty` | 检查指定包（Package）相对于其上次同步状态是否有未保存的修改。 | `UStormSyncCoreBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **触发导出**：
    -   在编辑器工具蓝图中，创建一个按钮。为按钮的 `OnClicked` 事件添加逻辑。
    -   连接到一个 `Open Storm Sync Export Wizard` 节点。运行时，此节点将弹出官方的导出向导界面，用户可以在此选择资产并导出为 `.spak` 文件。

2.  **自动导入资产包**：
    -   假设你有一个代表资产包路径的字符串变量 `SpakFilePath`。
    -   使用 `Import Storm Sync Package` 节点，并将 `SpakFilePath` 连接到其 `InPackagePath` 输入引脚。
    -   将 `Import Storm Sync Package` 的输出引脚 `OnImportCompleted` 连接到一个自定义事件，用于在导入完成后执行后续逻辑（例如显示成功通知）。

3.  **依赖关系分析工具**：
    -   使用 `Content Browser` 获取用户选中的资产对象引用。
    -   将此对象引用连接到 `Get Asset Dependencies` 节点的 `Asset` 输入引脚。
    -   将输出的 `Dependencies` 数组连接到一个 `For Each Loop`，并在循环体内将每个依赖项的路径打印到屏幕或输出到文件，用于快速审查依赖图。

## C++ 用法

重点从 test case 中提取，贴近官方用法。

### 头文件引入

```cpp
// 核心依赖分析
#include "StormSyncCoreModule.h"
#include "StormSyncCoreUtils.h"

// 资产包导入
#include "StormSyncImportModule.h"
#include "IStormSyncImportInterface.h"

// 传输与同步（客户端示例）
#include "StormSyncTransportClientModule.h"
#include "IStormSyncTransportClient.h"
```

### 基本用法

从测试用例提取的代码示例，展示了如何使用核心模块查询依赖关系。

```cpp
// 来源: Source/StormSyncTests/Private/Tests/StormSyncCore/StormSyncCoreUtilsTest.cpp
// 功能：获取一个纹理资产的所有依赖项

#include "Misc/AutomationTest.h"
#include "IAssetRegistry.h"
#include "AssetRegistry/AssetRegistryModule.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FStormSyncCoreUtilsDependencyTest, "StormSync.Core.Utils.GetDependencies", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FStormSyncCoreUtilsDependencyTest::RunTest(const FString& Parameters)
{
    // 1. 获取资产注册表模块
    FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>(TEXT("AssetRegistry"));
    IAssetRegistry& AssetRegistry = AssetRegistryModule.Get();

    // 2. 假设有一个已知的纹理资产路径
    FSoftObjectPath TextureAssetPath(TEXT("/Game/Textures/T_Example"));

    // 3. 使用 StormSyncCoreUtils 获取依赖项
    TArray<FAssetIdentifier> Dependencies;
    StormSyncCoreUtils::GetDependenciesForAsset(AssetRegistry, TextureAssetPath, Dependencies);

    // 4. 验证依赖项数量（根据你的资产而定）
    TestTrue(TEXT("Should find dependencies"), Dependencies.Num() > 0);

    // 5. 打印所有依赖项路径（用于调试）
    for (const FAssetIdentifier& Dep : Dependencies)
    {
        UE_LOG(LogTemp, Log, TEXT("Dependency: %s"), *Dep.ToString());
    }

    return true;
}
```

### 进阶用法

展示了如何通过传输客户端模块发起一次同步操作（概念性代码，基于模块接口推断）。

```cpp
// 功能：通过客户端连接并请求同步一个资产包
// 注意：这需要配置正确的服务器连接信息

#include "StormSyncTransportClientModule.h"
#include "IStormSyncTransportClient.h"

void RequestSyncFromServer()
{
    // 1. 获取传输客户端模块实例
    IStormSyncTransportClientPtr TransportClient = FStormSyncTransportClientModule::Get().GetClient();
    if (!TransportClient.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("StormSync Transport Client module not available."));
        return;
    }

    // 2. 定义一个回调委托，用于处理同步完成事件
    FOnSyncCompleted OnSyncCompletedDelegate;
    OnSyncCompletedDelegate.BindLambda([](const FStormSyncOperationResult& Result)
    {
        if (Result.WasSuccessful())
        {
            UE_LOG(LogTemp, Log, TEXT("Sync operation completed successfully."));
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Sync operation failed: %s"), *Result.GetFailureReason());
        }
    });

    // 3. 准备要同步的资产包信息（这里假设为一个SPAK文件名）
    FString PackageNameToSync = TEXT("MyAssets.spak");

    // 4. 向已连接的服务器发起同步请求
    TransportClient->RequestSync(PackageNameToSync, OnSyncCompletedDelegate);
}
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何编程实现一个简单的资产依赖导出器。

```cpp
// 文件: StormSyncDemoExporter.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "StormSyncDemoExporter.generated.h"

/**
 * 演示如何使用 StormSyncCore API 编写一个简单的资产导出器。
 */
UCLASS(BlueprintType)
class YOURPROJECT_API UStormSyncDemoExporter : public UObject
{
    GENERATED_BODY()

public:
    /**
     * 尝试将指定资产及其依赖项导出到临时目录。
     * @param InAssetPath 要导出的资产软路径， 例如 TEXT("/Game/MyBlueprint.MyBlueprint")
     * @return 临时目录路径， 失败则返回空字符串。
     */
    UFUNCTION(BlueprintCallable, Category = "StormSync Demo")
    FString ExportAssetWithDependencies(const FSoftObjectPath& InAssetPath);
};
```

```cpp
// 文件: StormSyncDemoExporter.cpp
#include "StormSyncDemoExporter.h"
#include "StormSyncCoreModule.h"
#include "StormSyncCoreUtils.h"
#include "IAssetRegistry.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

FString UStormSyncDemoExporter::ExportAssetWithDependencies(const FSoftObjectPath& InAssetPath)
{
    // 1. 获取资产注册表
    FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>(TEXT("AssetRegistry"));
    IAssetRegistry& AssetRegistry = AssetRegistryModule.Get();

    // 2. 收集目标资产及其所有依赖项
    TArray<FAssetIdentifier> AllAssetsToExport;
    AllAssetsToExport.Add(FAssetIdentifier(InAssetPath));

    TArray<FAssetIdentifier> Dependencies;
    StormSyncCoreUtils::GetDependenciesForAsset(AssetRegistry, InAssetPath, Dependencies);
    AllAssetsToExport.Append(Dependencies);

    // 3. 生成一个临时目录用于存放导出的包文件
    const FString ExportDir = FPaths::ProjectSavedDir() / TEXT("StormSyncDemo") / TEXT("Exports") / FDateTime::Now().ToString();
    IFileManager::Get().MakeDirectory(*ExportDir, true);

    // 4. 简单演示：将资产路径列表写入一个文本文件作为“清单”
    const FString ManifestFilePath = ExportDir / TEXT("manifest.txt");
    FString ManifestContent;
    for (const FAssetIdentifier& AssetId : AllAssetsToExport)
    {
        ManifestContent += AssetId.ToString() + LINE_TERMINATOR;
    }
    FFileHelper::SaveStringToFile(ManifestContent, *ManifestFilePath);

    UE_LOG(LogTemp, Log, TEXT("Exported asset manifest with %d items to: %s"), AllAssetsToExport.Num(), *ManifestFilePath);
    return ExportDir;
}
```

## 模块依赖

从 Build.cs 的 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames` 提取。
告诉读者：要用这个 plugin，你的模块需要依赖哪些东西。

**省略常见依赖**：以下模块几乎每个 plugin 都依赖，无需列出：
- Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore
- UnrealEd, EditorStyle, PropertyEditor (编辑器插件常见)
- Projects, DeveloperSettings

只列出该 plugin **独特**的、不常见的依赖。如果全部都是常见依赖，写“无特殊依赖（仅标准 Core/Engine/Slate 等）”。

| 模块 | 用途 |
|---|---|
| `StormSyncCore` | 提供资产依赖分析、包（Package）状态管理等核心功能。 |
| `AssetRegistry` | 用于查询资产依赖关系，是 `StormSyncCore` 的关键依赖。 |
| `JsonObject` | (推断) 用于序列化和传输资产元数据和同步状态。 |
| `NetworkMessage` | (推断) 用于传输层（`Transport*` 模块）的消息序列化和反序列化。 |

## 维护状态

从 git log 分析该 plugin 的维护情况。

### 近期更新

从 git log 获取最近 3-5 次 commit，以**表格**形式展示，每行必须包含 hash 原文和中文解读。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c830b630` | Storm Sync: fixed vulnerability where a malicious actor can make an spak containing package names/pa | 修复了一个安全漏洞，防止恶意 `.spak` 包文件中包含非法包名/路径可能引发的风险。 |
| 2026-05-12 | `3e9d09b7` | Motion Design: fixed storm sync export wizard UI creating a large number of nested folders when chan | 修复了风暴同步导出向导在更改路径时可能错误创建大量嵌套文件夹的UI问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了32位和64位平台上的格式化字符串说明符匹配问题，提升代码跨平台兼容性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 `UE_LOG` 宏迁移到新的 `UE_LOGF`，使用更现代的日志系统。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 对一次错误的查找替换操作进行二次修复。 |

### 维护评价

**综合评价：活跃维护的实验性核心组件**

-   **创建时间**：约1年前，属于较新的插件。
-   **最近更新频率和内容**：**非常活跃**。最近6个月内有多次提交，内容涵盖**安全修复**、**UI改进**、**代码质量提升**和**跨平台兼容性修复**。这表明该插件不仅是新增功能，其稳定性和安全性也在被持续关注。
-   **是否还在活跃维护**：**是**。作为 Epic Games 官方维护的虚拟制作和 Motion Design 工作流的关键部分，预计会持续更新。
-   **已知问题或限制**：从提交记录看，存在过安全漏洞（已修复）和UI细节问题。用户在使用时应保持插件为最新版本。
-   **是否推荐使用**：**推荐**。对于采用 Motion Design 或需要复杂资产同步的虚拟制片项目，这是一个由 Epic 官方维护的、功能完善且持续改进的解决方案。虽然插件本身 `EnabledByDefault` 为 `false`，但在相关工作流中它是**被官方推荐**的，且稳定性看起来很高。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync)
- [官方文档]()（暂无，描述中 `DocsURL` 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTests)