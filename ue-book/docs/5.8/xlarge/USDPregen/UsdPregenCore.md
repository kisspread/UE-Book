# USDPregen

> Library to assist with pre-generating USD-based content.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | USD预生成库 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时库、Python绑定） |
| 模块 | `UsdPregenCore` (Runtime), `USDPregenHttpWorker` (Runtime), `USDPregenInterchange` (Runtime), `USDPregenInterchangeEditor` (Runtime), `USDPregenPy` (Runtime), `USDPregenUObjectStorage` (Runtime), `USDPregenWrapper` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-14 |
| 年龄标签 | 🆕（约 0.8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen) | |

## 用途

USDPregen 是一个高级工具库，旨在通过系统性地“预生成”（pre-generate）基于 USD (Universal Scene Description) 的资产内容，来优化和自动化复杂的 USD 内容管线。它并非一个面向最终用户的简单导入/导出工具，而是一个为管线工程师和开发者构建的底层框架。

**核心问题**：在大规模、复杂的 USD 工作流中，资产（如模型、材质、变体）可能有无数种组合（permutations）。在游戏运行时或编辑器实时操作中，动态解析所有这些组合既耗时又不可预测。这个插件通过**提前扫描、发现、序列化**这些资产组合及其依赖关系，将不确定性的运行时计算转化为确定性的离线预生成任务。

**它解决**：
1.  **资产发现与注册**：在庞大的 USD 舞台中，自动识别哪些 `prim`（尤其是那些具有 `assetInfo` 元数据的）代表可重用的外部资产定义。
2.  **排列管理**：系统性地枚举资产可能处于的不同状态（由变体选择、继承关系等引入的“排列”）。
3.  **清单生成**：为每个独特的资产定义和排列组合创建详细的“清单”（Manifest），记录它由哪些 Unreal 产品（如 UAsset）组成，以及它们之间的依赖关系。
4.  **确定性管线**：通过将清单持久化（如存储为 JSON 文件或 UObject），确保无论何时需要某个资产配置，都能精确地重建它，而无需重新遍历原始 USD 场景。

## 使用场景

-   你在构建一个支持**海量资产变体**（例如，不同服装、武器的组合）的游戏角色系统，需要将所有这些变体预先打包成确定的资源包。
-   你的团队使用 **USD 作为资产交换格式**，但希望无缝地将这些资产集成到 Unreal 的 UAsset 体系中，并需要管理和追踪复杂的依赖关系。
-   你需要**优化大型 USD 场景的加载时间**，通过提前生成中间表示或最终资产，避免在加载时进行昂贵的动态解析和组合。
-   你正在开发一个**自定义的内容导入/转换管线**，需要一个可扩展的框架来识别、转换和存储 USD 内容。

## 蓝图用法

**注意**：根据提供的头文件，`USDPregenCore` 模块主要提供 C++ API。其 Public 接口类（如 `SceneDiscovery`, `AssetDefinitionRegistry`, `StoragePluginRegistry` 等）目前没有标记为 `BlueprintCallable` 或 `BlueprintReadWrite`。这意味着直接通过蓝图使用核心发现和预生成功能的节点可能有限。

该插件的蓝图交互更可能通过其他上层模块（如 `USDPregenInterchange` 或 `USDPregenWrapper`）或通过 Python（`USDPregenPy`）暴露。`USDPregenPy` 模块明确依赖 Python3，表明 Python 是其首要的脚本接口。

### 可能的蓝图交互模式

虽然核心 C++ 类未直接暴露为蓝图节点，但可以推断以下交互模式：

1.  **通过 Python 脚本**：使用 `USDPregenPy` 模块提供的 Python 绑定，在蓝图中调用 Python 脚本来执行发现和序列化任务。
2.  **通过编辑器工具或插件**：`USDPregenInterchangeEditor` 模块（尽管 Build.cs 信息显示为 Runtime，但模块名暗示编辑器集成）可能提供编辑器内 UI 或工具来触发预生成流程。
3.  **通过 UObject 存储**：`USDPregenUObjectStorage` 模块可能负责将预生成的清单以 UObject 的形式存储，使得这些对象可以在蓝图中被引用和管理。

## C++ 用法

`USDPregenCore` 提供了一套完整的 C++ API 来驱动 USD 资产发现和清单生成流程。

### 头文件引入

```cpp
#include "UsdPregen/sceneDiscovery.h" // 主要的发现入口
#include "UsdPregen/assetDefinitionRegistry.h" // 资产定义注册表
#include "UsdPregen/storagePluginRegistry.h" // 存储插件注册表
#include "UsdPregen/target.h" // TargetUid 和 TargetData
#include "UsdPregen/manifest.h" // Manifest 和 Product 定义
```

### 基本用法：执行一次简单的场景发现

此示例展示了如何使用 `SceneDiscovery` 类对一个 USD 舞台进行遍历，并收集发现的资产目标。**(来源: Public/UsdPregen/sceneDiscovery.h)**

```cpp
#include "UsdPregen/sceneDiscovery.h"
#include "UsdPregen/discoveryOptions.h"

using namespace ue::usdpregen; // PREGEN_NAMESPACE

void DiscoverAssetsFromStage(const pxr::UsdStageRefPtr& stage)
{
    // 1. 创建发现选项（可选）
    DiscoveryOptions options;
    options.discoveryMode = DiscoveryMode::AllPermutations; // 发现所有排列
    // options.discoveryPluginName = "MyCustomPlugin"; // 或使用自定义插件

    // 2. 创建场景发现实例
    SceneDiscovery discovery(stage, options);

    // 3. 准备结果容器
    SceneDiscovery::ResultMap results; // SdfPath -> vector<TargetUid>

    // 4. 执行遍历并查找目标
    bool success = discovery.TraverseAndFindTargets(results);

    if (success)
    {
        UE_LOG(LogTemp, Log, TEXT("Discovery completed. Found %d unique scene paths with targets."), results.size());

        // 5. 遍历结果
        for (const auto& [scenePath, targetUids] : results)
        {
            for (const TargetUid& targetUid : targetUids)
            {
                // 6. 获取每个目标的详细数据
                TargetDataRefPtr targetData = discovery.GetTargetData(targetUid);
                if (targetData && targetData->IsValid())
                {
                    UE_LOG(LogTemp, Log, TEXT("  Found valid target: %s (Definition: %s)"),
                        *FString(targetUid.GetString().c_str()),
                        *FString(targetUid.GetDefinitionUid().c_str()));

                    // 在这里，你可以将 targetData 序列化为清单并存储
                }
            }
        }

        // 7. （可选）保存发现过程的中间数据层，用于调试
        discovery.SaveDiscoveryData(TEXT("C:/Temp/USDPregen_Discovery.usda"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Discovery encountered fatal errors."));
    }
}
```

### 进阶用法：注册自定义存储插件并手动驱动流程

此示例展示如何注册一个自定义的存储插件，并更精细地控制发现和清单管理过程。**(综合来源: storagePluginRegistry.h, storageInterface.h, manifest.h)**

```cpp
#include "UsdPregen/storagePluginRegistry.h"
#include "UsdPregen/storageInterface.h"
#include "UsdPregen/storageOptions.h"
#include "UsdPregen/manifest.h"
#include "UsdPregen/jsonManifestSerializer.h"

using namespace ue::usdpregen;

// 1. 定义一个简单的内存存储插件（示例）
class FMemoryStoragePlugin : public StorageInterface
{
public:
    FMemoryStoragePlugin(const StorageOptions& InOptions) : Options(InOptions) {}

    virtual ManifestLoadResult LoadManifestPayload(const TargetUid& targetUid) override
    {
        ManifestLoadResult result;
        auto it = MemoryStore.find(targetUid.GetString());
        if (it != MemoryStore.end())
        {
            result.status = ManifestLoadStatus::Loaded;
            result.payload = it->second;
        }
        else
        {
            result.status = ManifestLoadStatus::DoesNotExist;
        }
        return result;
    }

    virtual ManifestSaveResult StoreManifestPayload(const TargetUid& targetUid, const ManifestPayload& payload) override
    {
        ManifestSaveResult result;
        MemoryStore[targetUid.GetString()] = payload;
        result.status = ManifestSaveStatus::Saved;
        return result;
    }
    // 其他必要方法的简单实现...
    virtual ManifestPayload SerializeManifest(const Manifest& manifest) override { /* 使用默认序列化 */ return {}; }
    virtual Manifest DeserializeManifestPayload(const ManifestPayload& payload) override { /* 使用默认反序列化 */ return {}; }

private:
    StorageOptions Options;
    std::unordered_map<std::string, ManifestPayload> MemoryStore;
};

void AdvancedPregenWorkflow()
{
    // 2. 注册自定义存储插件
    StoragePluginRegistry& storageRegistry = StoragePluginRegistry::GetInstance();
    storageRegistry.RegisterFactory("memory_storage", [](const StorageOptions& opts) -> StorageInterface* {
        return new FMemoryStoragePlugin(opts);
    });

    // 3. 创建并配置存储选项
    StorageOptions storageOptions;
    storageOptions.storagePluginName = "memory_storage";
    storageOptions.manifestDir = "/tmp/pregen_manifests";
    storageOptions.packageSubPathTemplate = "Generated/${DEFINITION_NAME}/${PERMUTATION_ID}";

    // 4. 通过注册表创建存储插件实例
    StorageInterfaceRefPtr storagePlugin = storageRegistry.Create(storageOptions);

    // 5. 假设你已经通过其他方式（如 SceneDiscovery）获得了一个 TargetUid 和它的 TargetData
    TargetUid myTargetUid("Chair_v1", "WoodenVariant");
    TargetDataRefPtr myTargetData = /* ... 获取 ... */;

    // 6. 创建一个清单，并附加目标数据
    Manifest manifest;
    manifest.SetTargetData(myTargetData);

    // 7. 添加产品（生成的UAsset信息）
    Product product;
    product.upackagePath = "/Game/Generated/Chair/Chair_Wood";
    product.uclass = "StaticMesh";
    product.unodeId = "ChairMeshNode";
    product.usdPrimType = "Mesh";
    product.usdPrimPath = "/World/Props/Chair";
    manifest.AddProduct(product);

    // 8. 序列化并存储清单
    ManifestPayload payload = storagePlugin->SerializeManifest(manifest);
    ManifestSaveResult saveResult = storagePlugin->StoreManifestPayload(myTargetUid, payload);

    if (saveResult.status == ManifestSaveStatus::Saved)
    {
        UE_LOG(LogTemp, Log, TEXT("Manifest stored for target: %s"), *FString(myTargetUid.GetString().c_str()));

        // 9. 稍后，可以加载并验证
        ManifestLoadResult loadResult = storagePlugin->LoadManifestPayload(myTargetUid);
        if (loadResult.status == ManifestLoadStatus::Loaded)
        {
            Manifest loadedManifest = storagePlugin->DeserializeManifestPayload(loadResult.payload);
            // 验证 loadedManifest 的内容
        }
    }
}
```

## Demo 示例

一个展示核心发现流程的最小示例。**(综合来源: sceneDiscovery.h, target.h)**

```cpp
// USDPreGenDemo.h
#pragma once

#include "CoreMinimal.h"

class AUSDPreGenDemoActor : public AActor
{
    GENERATED_BODY()

public:
    // 在编辑器工具或测试函数中调用
    UFUNCTION(BlueprintCallable, Category = "USD PreGen")
    void RunUSDPregenDemo(const FString& USDStagePath);
};
```

```cpp
// USDPreGenDemo.cpp
#include "USDPreGenDemo.h"
#include "UsdPregen/sceneDiscovery.h"
#include "UsdPregen/target.h"
#include "UsdIncludesStart.h"
#include "pxr/usd/usd/stage.h"
#include "UsdIncludesEnd.h"

void AUSDPreGenDemoActor::RunUSDPregenDemo(const FString& USDStagePath)
{
#if USE_USD_SDK
    pxr::UsdStageRefPtr stage = pxr::UsdStage::Open(TCHAR_TO_UTF8(*USDStagePath));
    if (!stage)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open USD stage: %s"), *USDStagePath);
        return;
    }

    ue::usdpregen::SceneDiscovery discovery(stage);
    ue::usdpregen::SceneDiscovery::ResultMap results;

    UE_LOG(LogTemp, Log, TEXT("Starting USD Pregen discovery on: %s"), *USDStagePath);
    bool bSuccess = discovery.TraverseAndFindTargets(results);

    if (bSuccess)
    {
        int32 TotalTargets = 0;
        for (const auto& Pair : results)
        {
            TotalTargets += Pair.Value.Num();
        }
        UE_LOG(LogTemp, Log, TEXT("Discovery successful. Found %d scene locations, containing a total of %d targets."),
            results.Num(), TotalTargets);

        // 示例：列出前10个发现的目标
        int32 Count = 0;
        for (const auto& [Path, Uids] : results)
        {
            for (const ue::usdpregen::TargetUid& uid : Uids)
            {
                UE_LOG(LogTemp, Log, TEXT("  [%d] Scene: %s -> Target: %s"),
                    Count++,
                    *FString(Path.GetString().c_str()),
                    *FString(uid.GetString().c_str()));

                if (Count >= 10) break;
            }
            if (Count >= 10) break;
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("USD Pregen discovery failed."));
    }
#endif // USE_USD_SDK
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `USD` / `USDUtilities` | USD SDK 核心绑定和工具函数 |
| `InterchangeCore` / `InterchangeNodes` | 用于 `USDPregenInterchange` 模块，与 UE 的 Interchange 框架集成 |
| `Python3` | 用于 `USDPregenPy` 模块，提供 Python 脚本绑定 |

## 维护状态

### 近期更新
- `9e86e007` 2026-05-14 — [USD] UsdPregen: Fixes regression introduced by recent clean up, where an item can get incorrectly p...
- `ddc18470` 2026-05-14 — [USD] UsdPregen: On definition conflicts during registry population, return the existing definition...
- `60206a86` 2026-05-14 — USD Pregen: Batch renaming for consistency. Also changes the default storage plugin in UE to the UOb...
- `bad2257d` 2026-05-14 — USD Pregen: User-configurable template string with placeholders for deterimining asset path;
- `9f286b30` 2026-05-14 — USD Pregen: Fix _VT and _NonVT textures not being saved from worker imports.

### 维护评价

- **状态**: **实验性 & 活跃开发中**。从创建时间和最近的 commit 记录看，这是一个非常新的插件（约0.8年），并且近期（2026-05-14）有密集的提交，内容涵盖功能修复、重构和特性添加（如可配置模板）。
- **风险**: 作为实验性插件，其 API 和行为可能会发生重大变化。`.uplugin` 元数据不完整，且标记为 `IsBetaVersion` 和 `IsExperimentalVersion`，表明它还未稳定。
- **推荐**: **不推荐在生产项目中直接依赖**。非常适合用于**研究、原型开发或内部工具链构建**。建议关注其发展，并准备应对接口变更。如果你在构建复杂的 USD 管线，这是一个值得关注和参与的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen)
- [官方文档]() (无)
- [测试用例]() (暂未发现)