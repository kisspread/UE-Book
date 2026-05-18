# USDPregen Interchange

> Library to assist with pre-generating USD-based content.

| 属性 | 值 |
|---|---|
| 中文名 | USD 预生成交换模块 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图库、C++ 模块） |
| 模块 | `USDPregenInterchange` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen) | |

## 用途

`USDPregenInterchange` 模块是 `USDPregen` 插件的核心，它提供了一套完整的 API，用于将 USD 文件（如 `.usda`、`.usd`）异步导入到虚幻引擎中，并在此过程中进行“预生成”（Pregen）处理。它的核心目标是自动化和优化大规模 USD 内容的导入工作流。

具体来说，它解决了以下问题：
1.  **异步导入**：允许在后台异步执行耗时的 USD 资产导入，避免阻塞编辑器主线程。
2.  **智能去重**：通过 `USDPregenContext` 重写资产节点 UID 生成逻辑，确保同一 USD 资产定义（Definition）在不同实例中生成相同的 UID，从而在导入管线中自动实现资产去重和合并。
3.  **自定义资产路径**：支持通过模板字符串（如 `${DEFINITION_NAME}/${PERMUTATION_ID}`）动态配置导入资产在内容浏览器中的存放路径，使项目结构更规范。
4.  **插件化扩展**：其架构依赖于 `SceneDiscovery` 和 `StorageInterface` 等插件接口，允许用户自定义 USD 场景的发现逻辑和资产存储逻辑。
5.  **自动化管线集成**：提供了蓝图和 Python API，便于集成到自动化构建或批量处理管线中。

## 使用场景

-   **影视或游戏开发**：你有一个大型的 USD 资产库（包含角色、道具、环境），需要批量导入到虚幻项目中，并希望自动处理重复资产和规范存放路径。
-   **程序化内容生成**：你需要在运行时或编辑时动态生成基于 USD 的资产变体（Permutations），并希望有一个高效的导入和存储流程。
-   **自动化管线**：你需要在 CI/CD 流程中，通过 Python 脚本或命令行调用，将最新的 USD 资产自动导入并保存到指定位置。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Import File` | 启动一个异步的 USD 预生成导入流程。 | `UUSDPregenBlueprintLibrary` |

### 使用示例

1.  **创建导入选项**：
    在蓝图中创建一个 `PregenImportOptions` 结构体变量。
    设置 `SourceFilePath` 为你的 USD 文件绝对路径。
    可选配置 `DiscoveryOptions` 和 `StorageOptions` 来指定自定义插件或参数。

2.  **处理完成回调**：
    创建一个自定义事件或函数，将其作为 `USDPregenOnImportDoneDynamic` 委托的目标。
    该委托会传入三个参数：原始的 `ImportOptions`、一个布尔值 `bSuccess` 表示是否成功，以及一个字符串数组 `SavedPackageFilePaths`，其中包含所有已保存资产包的文件路径（仅在 `ImportOptions.bAutoSavePackages` 为 `true` 时填充）。

3.  **调用导入**：
    调用 `Import File` 节点，将准备好的 `ImportOptions` 和完成回调委托连接到输入引脚。
    一旦导入后台任务完成（包括资产存储和可选的自动保存），完成回调将在游戏线程上触发。

## C++ 用法

### 头文件引入

```cpp
#include "USDPregenInterchangeModule.h"
```

### 基本用法

异步导入一个 USD 文件并处理完成事件。

```cpp
// 来源：基于 USDPregenBlueprintLibrary.h 和 USDPregenInterchangeModule.h 的用法推断
#include "USDPregenInterchangeModule.h"

void ImportMyUsdAsset()
{
    // 1. 配置导入选项
    FPregenImportOptions ImportOptions;
    ImportOptions.SourceFilePath = TEXT("/Game/Assets/Characters/Hero.usda");
    ImportOptions.bAutomated = true; // 使用自动化模式，不显示UI
    ImportOptions.bAutoSavePackages = true; // 导入后自动保存到磁盘

    // 可选：配置发现和存储插件选项
    ImportOptions.DiscoveryOptions.DiscoveryPluginName = TEXT("CustomStudioDiscovery");
    ImportOptions.StorageOptions.StoragePluginName = TEXT("JsonStorage");

    // 2. 定义完成回调
    FUSDPregenInterchangeModule::FOnImportDone OnImportDone = [](
        const FPregenImportOptions& InImportOptions,
        bool bSuccess,
        const TArray<FString>& SavedPackageFilePaths)
    {
        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("USD Pregen import succeeded. Saved %d packages."), SavedPackageFilePaths.Num());
            for (const FString& Path : SavedPackageFilePaths)
            {
                UE_LOG(LogTemp, Log, TEXT(" - %s"), *Path);
            }
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("USD Pregen import failed for: %s"), *InImportOptions.SourceFilePath);
        }
    };

    // 3. 执行导入
    FUSDPregenInterchangeModule::ImportFile(ImportOptions, OnImportDone);
}
```

### 进阶用法

在自定义 Interchange 管线中使用 `USDPregenContext` 来控制特定资产的处理。

```cpp
// 来源：基于 USDPregenContext.h 的用法推断
#include "USDPregenContext.h"

void SetupPregenContextForImport(UInterchangeSourceData* SourceData)
{
    // 创建自定义的 Pregen Context 实例
    UUSDPregenContext* PregenContext = NewObject<UUSDPregenContext>();

    // （可选）加载或初始化场景发现结果，这里通常由插件内部流程完成。
    // PregenContext->SceneDiscovery = ...;
    // PregenContext->SceneDiscoveryResults = ...;

    // （可选）设置存储接口，用于获取资产包路径
    PregenContext->Storage = ...;

    // （可选）设置过滤条件，只处理特定的目标UID
    PregenContext->AllowedTargetUid = TEXT("TargetHero001");

    // 将这个自定义 Context 设置到 SourceData 上，替换默认的 USD 上下文。
    // 这需要通过 Interchange 的标签系统或扩展 SourceData 来完成。
    // 假设存在一个函数可以设置标签为 “USD” 的数据为我们的 Context。
    // SourceData->SetTagValue(TEXT("USD"), PregenContext);
}
```

## Demo 示例

以下是一个最小的 C++ 示例，演示如何从一个编辑器按钮触发 USD 预生成导入。

**MyPregenActor.h**
```cpp
// Copyright Your Studio. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "USDPregenInterchangeModule.h" // 包含选项和模块头文件
#include "MyPregenActor.generated.h"

UCLASS()
class AMyPregenActor : public AActor
{
	GENERATED_BODY()

public:
	AMyPregenActor();

protected:
	// 将此函数绑定到 UI 按钮或蓝图可调用事件
	UFUNCTION(BlueprintCallable, Category = "Test")
	void TriggerUsdImport();

private:
	// 保存回调上下文，防止提前销毁
	FUSDPregenInterchangeModule::FOnImportDone CurrentImportCallback;
};
```

**MyPregenActor.cpp**
```cpp
// Copyright Your Studio. All Rights Reserved.

#include "MyPregenActor.h"
#include "USDPregenInterchangeModule.h"

AMyPregenActor::AMyPregenActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AMyPregenActor::TriggerUsdImport()
{
	// 构造导入选项
	FPregenImportOptions Options;
	Options.SourceFilePath = TEXT("/Game/MyUSD/Scene.usda");
	Options.Title = TEXT("DemoImport");
	Options.bAutomated = true;
	Options.bAutoSavePackages = true;

	// 配置一个简单的存储路径模板
	Options.StorageOptions.PackageSubPathTemplate = TEXT("PregenAssets/${DEFINITION_NAME}");

	// 定义一个成员变量作为回调的持有者，确保其生命周期
	CurrentImportCallback = [WeakThis = TWeakObjectPtr<AMyPregenActor>(this)](
		const FPregenImportOptions& InOptions,
		bool bSuccess,
		const TArray<FString>& SavedPaths)
	{
		if (bSuccess)
		{
			UE_LOG(LogTemp, Warning, TEXT("Import completed! Saved %d files."), SavedPaths.Num());
		}
	};

	// 启动导入
	FUSDPregenInterchangeModule::ImportFile(Options, CurrentImportCallback);
}
```

## 模块依赖

从模块名称和头文件包含关系推断，`USDPregenInterchange` 依赖于以下 **独特** 的模块：

| 模块 | 用途 |
|---|---|
| `USDPregenCore` | USD 预生成的核心类型、接口和逻辑。 |
| `InterchangeCore`, `InterchangeEngine`, `InterchangeUsd` | 虚幻引擎的资产交换框架，用于驱动资产导入管线。 |
| `UsdUtilities`, `Usd` | Epic 提供的底层 USD 绑定库。 |
| `USDPregenWrapper` | 对 USD 操作的封装层。 |

## 维护状态

### 近期更新

从提供的 Git 提交记录看，所有提交均发生在同一天（2026-05-14），表明该模块正处于密集开发或初始集成阶段。

```
- 2026-05-14 9e86e007 [USD] UsdPregen: Fixes regression introduced by recent clean up, where an item can get incorrectly p
- 2026-05-14 ddc18470 [USD] UsdPregen: On definition conflicts during registry population, return the existing definition
- 2026-05-14 60206a86 USD Pregen: Batch renaming for consistency. Also changes the default storage plugin in UE to the UOb
- 2026-05-14 bad2257d USD Pregen: User-configurable template string with placeholders for deterimining asset path;
- 2026-05-14 9f286b30 USD Pregen: Fix _VT and _NonVT textures not being saved from worker imports.
```

### 维护评价

-   **状态**：**活跃开发中**。所有提交日期都非常新，显示这是一个正在积极开发和修复问题的新模块。
-   **稳定性**：从提交信息（如“Fixes regression”、“Fix... textures not being saved”）来看，正在解决开发过程中出现的回归和功能缺陷，处于功能稳定化阶段。
-   **推荐度**：**实验性，谨慎使用**。虽然功能强大，但 `IsBetaVersion` 和 `IsExperimentalVersion` 标记均为 `true`，且创建日期非常新，API 和行为未来可能发生较大变化。建议仅在愿意跟踪最新变更和容忍潜在 breaking changes 的项目或实验性工作流中使用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen)
-   官方文档：无（`.uplugin` 中 `DocsURL` 为空）
-   测试用例：未在提供的信息中明确给出，可能位于 `Engine/Tests/` 目录或插件内部的 `Tests/` 子目录。