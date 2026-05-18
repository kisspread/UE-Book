# USDPregen

> Library to assist with pre-generating USD-based content.

| 属性 | 值 |
|---|---|
| 中文名 | USD预生成库 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（可包含资产内容） |
| 模块 | `UsdPregenCore` (Runtime), `USDPregenHttpWorker` (Runtime), `USDPregenInterchange` (Runtime), `USDPregenInterchangeEditor` (Runtime), `USDPregenPy` (Runtime), `USDPregenUObjectStorage` (Runtime), `USDPregenWrapper` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen) | |

## 用途

USDPregen 是一个用于**预生成 USD 内容**的框架库。它解决的核心问题是：当 USD 资产在编辑器中被引入时，往往包含大量排列组合（permutations）和变体（variants），如果在运行时才去解析和生成这些内容，会导致严重的性能问题和加载延迟。

该插件提供了一套完整的管线，用于：

1. **发现（Discovery）**：扫描 USD Stage，找出所有需要预生成的「目标」（targets），包括各种 variant 排列组合
2. **追踪（Tracking）**：跟踪 USD 场景的变化，识别哪些排列已处理、哪些待处理
3. **清单管理（Manifest）**：记录每个目标已生成的「产品」（products），包括 UAsset 路径、UClass 类型等
4. **存储抽象（Storage）**：通过可插拔的存储接口，将清单数据持久化到不同后端（JSON、UObject、HTTP 等）
5. **资产定义注册（Asset Definition Registry）**：管理外部资产定义的注册、查找和快照

当前文档聚焦于 **USDPregenWrapper** 模块——它是整个插件的公共 API 层，为底层的 `UsdPregen` C++ 原生库提供 Unreal 友好的 C++ 包装器，使得不依赖 RTTI 的 UE 模块也能使用该功能。

## 使用场景

- 你在制作虚拟制片/数字孪生管线，需要将复杂的 USD 资产预先烘焙为 UAssets → 用 USDPregen 的 Discovery + Manifest 管线
- 你需要支持 USD 的大量 variant 排列组合，且不想在运行时承担解析开销 → 用 USDPregen 的 Permutation 追踪系统
- 你需要自定义资产的存储位置和命名规则 → 通过 `IStorageInterface` 实现自定义存储后端，利用模板占位符（`${DEFINITION_NAME}`、`${PERMUTATION_ID}` 等）控制路径结构
- 你需要将预生成结果通过 HTTP 服务分发给远程工作者 → 用 USDPregenHttpWorker 模块
- 你需要用 Python 脚本自动化预生成流程 → 用 USDPregenPy 模块
- 你需要将预生成结果存入 UE UObject 资产系统 → 用 USDPregenUObjectStorage 模块

## 蓝图用法

本插件主要面向 C++ 使用，Blueprint 支持仅限于两个枚举类型。无 BlueprintCallable 函数节点。

### Blueprint 可用枚举

| 枚举 | 说明 |
|---|---|
| `EPregenDiscoveryMode` | 控制发现模式：`AllPermutations`（所有排列）或 `ComposedPermutationOnly`（仅组合排列） |
| `EPregenVersionFallbackMode` | 版本回退策略：`None`（不回退）、`LayerStackFilesAndTimestamps`（层级文件和时间戳）、`ResolvedLayerStackFilesAndTimestamps`（已解析层级文件和时间戳） |

## C++ 用法

### 头文件引入

```cpp
// 核心包装器
#include "USDPregenWrapper.h"

// 按需引入具体类
#include "UsdPregenWrappers/SceneDiscovery.h"
#include "UsdPregenWrappers/SceneTracker.h"
#include "UsdPregenWrappers/Target.h"
#include "UsdPregenWrappers/Manifest.h"
#include "UsdPregenWrappers/ManifestTypes.h"
#include "UsdPregenWrappers/StorageInterface.h"
#include "UsdPregenWrappers/JsonStoragePlugin.h"
#include "UsdPregenWrappers/AssetDefinitionRegistry.h"
#include "UsdPregenWrappers/ExtAssetDefinition.h"
#include "UsdPregenWrappers/StoragePluginRegistry.h"
#include "UsdPregenWrappers/StorageInterfaceAdapter.h"
#include "UsdPregenWrappers/IStorageInterface.h"
```

> **注意**：所有类都位于 `UE::UsdPregen` 命名空间下。大部分功能需要 `USE_USD_SDK` 宏启用。

### 基本用法 — 发现 USD 场景中的目标

使用 `FSceneDiscovery` 扫描一个 USD Stage，找出所有需要预生成的目标：

```cpp
#include "UsdPregenWrappers/SceneDiscovery.h"
#include "UsdPregenWrappers/Target.h"
#include "USDPregenWrapper.h"  // EPregenDiscoveryMode

using namespace UE::UsdPregen;

void DiscoverTargets(const UE::FUsdStage& Stage)
{
    // 使用默认选项创建发现器
    FSceneDiscovery Discovery(Stage);
    
    // 或使用自定义发现选项
    // FPregenDiscoveryOptions Options;
    // FSceneDiscovery Discovery(Stage, Options);

    // 遍历场景并收集结果
    FSceneDiscovery::ResultMap Results;  // TMap<FSdfPath, TArray<FTargetUid>>
    bool bSuccess = Discovery.TraverseAndFindTargets(Results);
    
    if (bSuccess)
    {
        for (const auto& [SdfPath, TargetUids] : Results)
        {
            for (const FTargetUid& Uid : TargetUids)
            {
                // 获取每个目标的数据
                FTargetData Data = Discovery.GetTargetData(Uid);
                
                UE_LOG(LogTemp, Log, TEXT("Found target: %s (Permutation: %s)"),
                    *Uid.GetDefinitionUid(),
                    Uid.HasPermutationUid() ? *Uid.GetPermutationUid() : TEXT("N/A"));
            }
        }
    }

    // 可选：保存发现数据到文件
    Discovery.SaveDiscoveryData(TEXT("D:/discovery_data.json"));
}
```

### 基本用法 — 清单与产品管理

使用 `FManifest` 记录预生成结果：

```cpp
#include "UsdPregenWrappers/Manifest.h"
#include "UsdPregenWrappers/ManifestTypes.h"

using namespace UE::UsdPregen;

void ManageManifest(const FTargetUid& TargetUid)
{
    FManifest Manifest;
    
    // 添加预生成的产品
    FProduct Product;
    Product.UPackagePath = TEXT("/Game/PreGenerated/MyAsset");
    Product.UClass = TEXT("StaticMesh");
    Product.UNodeId = TEXT("node_001");
    Product.UsdPrimType = TEXT("Mesh");
    Product.UsdPrimPath = TEXT("/Root/Geometry/MyMesh");
    
    Manifest.AddProduct(Product);
    
    // 附加目标数据
    FTargetData TargetData;  // 从 FSceneDiscovery 获取
    Manifest.SetTargetData(TargetData);
    
    // 查询产品列表
    TArray<FProduct> Products = Manifest.GetProducts();
    
    // 验证清单有效性
    if (Manifest.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Manifest has %d products"), Products.Num());
    }
}
```

### 基本用法 — 存储接口

使用 `FStorageInterface` 加载/存储清单数据：

```cpp
#include "UsdPregenWrappers/StorageInterface.h"
#include "UsdPregenWrappers/ManifestTypes.h"

using namespace UE::UsdPregen;

void StoreAndLoadManifest(const FStorageInterface& Storage, const FTargetUid& TargetUid, const FManifest& Manifest)
{
    // 将清单序列化为载荷
    FManifestPayload Payload = Storage.SerializeManifest(Manifest);
    
    // 存储清单
    FManifestSaveResult SaveResult = Storage.StoreManifestPayload(TargetUid, Payload);
    if (SaveResult.Status == EManifestSaveStatus::Saved)
    {
        UE_LOG(LogTemp, Log, TEXT("Manifest saved successfully"));
        
        // 持久化（flush 到最终存储）
        Storage.PersistManifestPayload(TargetUid);
    }
    
    // 重新加载清单
    FManifestLoadResult LoadResult = Storage.LoadManifestPayload(TargetUid);
    if (LoadResult.Status == EManifestLoadStatus::Loaded)
    {
        FManifest LoadedManifest = Storage.DeserializeManifestPayload(LoadResult.Payload);
        
        // 获取 UAsset 路径
        TArray<FExtAssetDefinition> Definitions;
        FString AssetName = Storage.GetNameForUAsset(TargetUid, Definitions, TEXT("StaticMesh"));
        FString SubPath = Storage.GetPackageSubPathForUAsset(TargetUid, Definitions, TEXT("StaticMesh"));
    }
}
```

### 基本用法 — 路径模板替换

`IStorageInterface::ResolvePackageSubPathTemplate` 提供强大的路径模板功能：

```cpp
#include "UsdPregenWrappers/IStorageInterface.h"

using namespace UE::UsdPregen;

void ResolvePath(
    const FTargetUid& TargetUid,
    const TArray<FExtAssetDefinition>& Definitions)
{
    // 使用占位符模板
    FString Template = TEXT("assets/${DEFINITION_NAME}/${PERMUTATION_ID}");
    
    FString ResolvedPath = IStorageInterface::ResolvePackageSubPathTemplate(
        Template,
        TargetUid,
        Definitions,
        TEXT("StaticMesh")
    );
    // 示例输出: "assets/chemistry_bottle02/2559017893"
    
    // 支持从 metadata 字典取值
    FString TemplateWithMeta = TEXT("assets/${METADATA:category}/${DEFINITION_NAME}");
    
    // 自定义额外替换（优先级高于内置占位符）
    TMap<FString, FString> ExtraSubstitutions;
    ExtraSubstitutions.Add(TEXT("CUSTOM_FIELD"), TEXT("MyValue"));
    
    FString Resolved = IStorageInterface::ResolvePackageSubPathTemplate(
        TemplateWithMeta,
        TargetUid,
        Definitions,
        TEXT("Material"),
        ExtraSubstitutions
    );
}
```

**支持的占位符**：

| 占位符 | 说明 |
|---|---|
| `${DEFINITION_NAME}` | 最后一个定义的名称 |
| `${DEFINITION_VERSION}` | 最后一个定义的版本 |
| `${DEFINITION_UID}` | 最后一个定义的唯一 ID |
| `${PERMUTATION_ID}` | 目标的排列 ID |
| `${ASSET_TYPE}` | 资产类型参数 |
| `${METADATA:KEY}` | 从叶定义的 metadata 字典取值，支持冒号分隔的嵌套路径 |

### 进阶用法 — 注册自定义存储后端

通过 `FStoragePluginRegistry` 和 `IStorageInterface` 注册自定义存储实现：

```cpp
#include "UsdPregenWrappers/StoragePluginRegistry.h"
#include "UsdPregenWrappers/IStorageInterface.h"

using namespace UE::UsdPregen;

// 实现自定义存储接口
class FMyCustomStorage : public IStorageInterface
{
public:
    virtual FManifestLoadResult LoadManifestPayload(const FTargetUid& TargetUid) override
    {
        FManifestLoadResult Result;
        Result.Status = EManifestLoadStatus::DoesNotExist;
        // ... 自定义加载逻辑
        return Result;
    }
    
    virtual FManifestSaveResult StoreManifestPayload(
        const FTargetUid& TargetUid,
        const FManifestPayload& Payload) override
    {
        FManifestSaveResult Result;
        Result.Status = EManifestSaveStatus::Saved;
        // ... 自定义存储逻辑
        return Result;
    }
    
    virtual FManifestPayload SerializeManifest(const FManifest& Manifest) override { /* ... */ }
    virtual FManifest DeserializeManifestPayload(const FManifestPayload& Payload) override { /* ... */ }
    
    virtual FString GetNameForUAsset(
        const FTargetUid& TargetUid,
        const TArray<FExtAssetDefinition>& Definitions,
        const FString& AssetType) override
    {
        // 自定义 UAsset 命名规则
        return FString::Printf(TEXT("Pregen_%s_%s"),
            *TargetUid.GetDefinitionUid(), *AssetType);
    }
    
    virtual FString GetPackageSubPathForUAsset(
        const FTargetUid& TargetUid,
        const TArray<FExtAssetDefinition>& Definitions,
        const FString& AssetType) override
    {
        // 使用内置模板解析
        return ResolvePackageSubPathTemplate(
            TEXT("pregen/${DEFINITION_NAME}/${ASSET_TYPE}"),
            TargetUid, Definitions, AssetType);
    }
    
    virtual FString GetPathForManifest(const FTargetUid& TargetUid) override
    {
        return FString::Printf(TEXT("Manifests/%s.json"), *TargetUid.GetDefinitionUid());
    }
};

// 注册工厂函数
void RegisterCustomStorage()
{
    FStoragePluginRegistry Registry = FStoragePluginRegistry::GetInstance();
    
    Registry.RegisterFactory(TEXT("MyCustomStorage"),
        [](const FPregenStorageOptions& Options) -> TSharedRef<IStorageInterface, ESPMode::ThreadSafe>
        {
            return MakeShared<FMyCustomStorage>();
        });
}
```

### 进阶用法 — 资产定义注册与快照

使用 `FAssetDefinitionRegistry` 管理资产定义，并通过 `FExtAssetDefinitionSnapshot` 进行持久化：

```cpp
#include "UsdPregenWrappers/AssetDefinitionRegistry.h"
#include "UsdPregenWrappers/ExtAssetDefinition.h"

using namespace UE::UsdPregen;

void ManageAssetDefinitions()
{
    // 获取全局注册表
    FAssetDefinitionRegistry Registry = FAssetDefinitionRegistry::GetInstance();
    
    // 通过唯一 ID 查找定义
    FExtAssetDefinition Definition = Registry.GetDefinition(TEXT("my_asset_uid_001"));
    
    if (Definition)
    {
        FString Name = Definition.GetName();
        FString Version = Definition.GetVersion();
        UE::FSdfPath Identifier = Definition.GetIdentifier();
        FString UniqueId = Definition.GetUniqueId();
        
        UE_LOG(LogTemp, Log, TEXT("Asset: %s v%s (UID: %s)"),
            *Name, *Version, *UniqueId);
        
        // 检查 metadata
        if (Definition.HasMetadata())
        {
            UE::FVtValue Metadata;
            Definition.GetMetadata(Metadata);
        }
        
        // 创建快照用于持久化
        FExtAssetDefinitionSnapshot Snapshot = FExtAssetDefinitionSnapshot::From(Definition);
        
        // ... 将 Snapshot 序列化到磁盘或数据库 ...
        
        // 从快照重建并注册（幂等操作）
        bool bRegistered = Snapshot.RegisterIntoRegistry();
        // true = 成功或定义已存在且一致
        // false = 与同 UID 但不同字段的定义冲突
    }
}
```

### 进阶用法 — 场景追踪与排列迭代

使用 `FSceneTracker` 追踪场景变化并逐个处理排列：

```cpp
#include "UsdPregenWrappers/SceneTracker.h"

using namespace UE::UsdPregen;

void ProcessPermutations(FSceneTracker Tracker)
{
    // 获取场景中被追踪的 prim
    TArray<FTrackedPrim> TrackedPrims;
    // ... 从 tracker 获取 tracked prims ...
    
    for (FTrackedPrim& Prim : TrackedPrims)
    {
        while (Prim.HasUnprocessedPermutations())
        {
            // 准备下一个排列（会修改 USD Stage 状态）
            bool bHasMore = Prim.PrepareNextPermutation();
            
            if (!bHasMore)
                break;
            
            // 当前排列已生效，执行预生成逻辑...
            // 例如：导入材质、生成 StaticMesh 等
        }
    }
    
    // FSceneTracker 也支持弱引用
    FSceneTrackerWeak WeakRef = Tracker;
    FSceneTracker StrongRef(WeakRef);  // 从弱引用恢复强引用
}
```

## 模块依赖

USDPregenWrapper 的核心依赖（从头文件 include 分析）：

| 模块 | 用途 |
|---|---|
| `USD` / `USDUtilities` | 提供 `USDMemory.h`、`UsdWrappers` 等 USD 集成基础 |
| `UsdPregen` (外部原生库) | 底层 C++ 预生成引擎（通过 `UsdPregen/pregen.h` 引入，`USE_USD_SDK` 条件编译） |
| `Python3` | USDPregenPy 模块专用，Python 脚本自动化支持 |

> 无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## Demo 示例

以下是一个完整的最小示例，展示如何在一个 Editor 模块中使用 USDPregenWrapper 的发现与存储功能：

**MyPregenModule.h**

```cpp
#pragma once

#include "Modules/ModuleManager.h"

class FMyPregenModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
    
private:
    void RunPregenPipeline();
};
```

**MyPregenModule.cpp**

```cpp
#include "MyPregenModule.h"

#include "USDPregenWrapper.h"
#include "UsdPregenWrappers/SceneDiscovery.h"
#include "UsdPregenWrappers/Manifest.h"
#include "UsdPregenWrappers/ManifestTypes.h"
#include "UsdPregenWrappers/JsonStoragePlugin.h"
#include "UsdPregenWrappers/Target.h"

#include "USDUObject/UsdStage.h"  // 或合适的 USD Stage 头文件

using namespace UE::UsdPregen;

void FMyPregenModule::StartupModule()
{
    // 可选：模块启动时注册自定义存储工厂等
}

void FMyPregenModule::ShutdownModule()
{
}

void FMyPregenModule::RunPregenPipeline()
{
    // 1. 打开 USD Stage（伪代码，需根据实际 USD 集成调整）
    UE::FUsdStage Stage = /* ... open your stage ... */;
    
    if (!Stage)
        return;

    // 2. 发现所有预生成目标
    FSceneDiscovery Discovery(Stage);
    FSceneDiscovery::ResultMap Results;
    
    if (!Discovery.TraverseAndFindTargets(Results))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to discover targets"));
        return;
    }
    
    UE_LOG(LogTemp, Log, TEXT("Discovered %d path entries"), Results.Num());

    // 3. 创建 JSON 存储插件
    FPregenStorageOptions StorageOptions;
    FJsonStoragePlugin JsonStorage(StorageOptions);
    
    if (!JsonStorage)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create JSON storage"));
        return;
    }

    // 4. 为每个目标创建清单并存储
    for (const auto& [Path, TargetUids] : Results)
    {
        for (const FTargetUid& Uid : TargetUids)
        {
            // 获取目标数据
            FTargetData TargetData = Discovery.GetTargetData(Uid);
            
            // 创建清单
            FManifest Manifest;
            
            // 添加预生成产品（示例）
            FProduct Product;
            Product.UPackagePath = TEXT("/Game/Pregen/") + Uid.GetDefinitionUid();
            Product.UClass = TEXT("StaticMesh");
            Manifest.AddProduct(Product);
            Manifest.SetTargetData(TargetData);
            
            // 序列化并存储
            FManifestPayload Payload = JsonStorage.SerializeManifest(Manifest);
            FManifestSaveResult SaveResult = JsonStorage.StoreManifestPayload(Uid, Payload);
            
            if (SaveResult.Status == EManifestSaveStatus::Saved)
            {
                JsonStorage.PersistManifestPayload(Uid);
                UE_LOG(LogTemp, Log, TEXT("Stored manifest for target: %s"), *Uid.GetString());
            }
            else
            {
                UE_LOG(LogTemp, Warning, TEXT("Failed to store manifest: %s"), *SaveResult.Message);
            }
            
            // 验证：重新加载
            FManifestLoadResult LoadResult = JsonStorage.LoadManifestPayload(Uid);
            if (LoadResult.Status == EManifestLoadStatus::Loaded)
            {
                FManifest Loaded = JsonStorage.DeserializeManifestPayload(LoadResult.Payload);
                UE_LOG(LogTemp, Log, TEXT("Verified: loaded %d products"), Loaded.GetProducts().Num());
            }
        }
    }
}

IMPLEMENT_MODULE(FMyPregenModule, MyPregenModule)
```

## 维护状态

### 近期更新

```
- 2026-05-14 9e86e007 [USD] UsdPregen: Fixes regression introduced by recent clean up, where an item can get incorrectly p...
- 2026-05-14 ddc18470 [USD] UsdPregen: On definition conflicts during registry population, return the existing definition...
- 2026-05-14 60206a86 USD Pregen: Batch renaming for consistency. Also changes the default storage plugin in UE to the UOb...
- 2026-05-14 bad2257d USD Pregen: User-configurable template string with placeholders for determining asset path
- 2026-05-14 9f286b30 USD Pregen: Fix _VT and _NonVT textures not being saved from worker imports.
```

### 维护评价

**⚠️ 实验性 / 开发初期**

- **创建时间**：2026-05-14，插件极其年轻
- **更新频率**：同一天内有 5 次提交，属于密集开发阶段
- **成熟度**：标记为 `IsBetaVersion` 和 `IsExperimentalVersion`，位于 `Experimental` 目录，`Installed: false`
- **代码质量**：API 设计较为完善，有良好的包装器层分离（Wrapper 层隔离 RTTI 依赖），支持模板化路径解析，存储接口抽象化程度高
- **风险提示**：作为实验性插件，API 可能在后续版本中发生重大变更；同一天的多次提交包含回归修复和批量重命名，表明接口仍在快速演进中
- **推荐**：适合在实验性管线中试用和评估，不建议在生产环境依赖此插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen)
- [官方文档](#)（暂无）
- [测试用例](#)（暂未发现）