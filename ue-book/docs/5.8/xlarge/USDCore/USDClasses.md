# USD Core

> Adds support for USD SDK, UE wrapper classes and USD conversion utilities（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | USD 核心 |
| 分类 | 通用 |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD资产、材质模板） |
| 模块 | `USDClasses` (Runtime), `USDUtilities` (Runtime), `UnrealUSDWrapper` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-16 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/USDCore) | |

## 用途

USDCore 插件是 Unreal Engine 中整个 USD (Universal Scene Description) 工作流的基础和核心。它主要解决三个问题：
1.  **提供 USD SDK 访问**：通过 `UnrealUSDWrapper` 模块封装了对 OpenUSD 库的底层调用，让 UE 其他模块和插件能安全、稳定地使用 USD API。
2.  **定义 UE 侧的 USD 数据模型**：通过 `USDClasses` 模块定义了一系列 UObject 类（如 `UUsdAssetCache3`, `UUsdDrawModeComponent`）和数据结构（如 `FUsdPrimMetadata`），用于在 UE 中表示和管理从 USD 阶段转换而来的资产、材质、元数据等信息。
3.  **提供通用的转换与工具函数**：`USDUtilities` 模块（以及 `USDClasses` 中的命名空间）包含了大量辅助函数，用于处理 USD 与 UE 之间的数据转换、资产哈希、分析事件发送等，是连接 USD 和 UE 的“胶水层”。

简单来说，USDCore 是 USD 在 UE 中运行的基石。其他更高级的 USD 功能插件（如 `USDStage`、`USDImporter`）都依赖于它。

## 使用场景

-   你的项目需要与 DCC 工具（如 Maya、Houdini）通过 USD 格式交换资产 → 使用 USDCore 提供的基础支持。
-   你在编辑器中需要创建、编辑和管理 USD 阶段（`.usd`, `.usda`, `.usdc`），并期望资产被缓存以提高性能 → 依赖 `UUsdAssetCache3`。
-   你需要自定义 USD 材质在 UE 中的渲染方式 → 通过 `UUsdProjectSettings` 配置参考材质。
-   你需要从 USD 阶段中提取元数据并附加到生成的 UE 资产上 → 使用 `UUsdAssetUserData` 相关类。
-   你需要在 C++ 或蓝图中直接调用 USD SDK 功能 → 通过 `UnrealUSDWrapper` 模块。

## 蓝图用法

从源码中提取的 `BlueprintCallable` 和 `BlueprintReadWrite` API 主要集中在 `UUsdAssetCache3`、`UUsdAssetCache2`（已弃用）和 `UUsdProjectSettings`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOrCreateCachedAsset` | 根据哈希值获取或创建一个缓存资产。这是 USD 资产缓存的核心函数。 | `UUsdAssetCache3` |
| `CacheAsset` | 将一个已有的资产路径关联到指定哈希值并存入缓存。 | `UUsdAssetCache3` |
| `GetCachedAsset` | 根据哈希值获取一个已缓存的资产。 | `UUsdAssetCache3` |
| `StopTrackingAsset` | 从缓存中移除一个哈希值及其关联的资产路径，但不删除资产本身。 | `UUsdAssetCache3` |
| `DeleteUnreferencedAssets` | 删除所有未被引用且可删除的缓存资产。 | `UUsdAssetCache3` |
| `AddAssetReferencer` / `RemoveAssetReferencer` | 管理资产的引用计数，防止被自动清理。 | `UUsdAssetCache3` |
| `SendAnalytics` | 发送一条 USD 操作的分析事件。 | `IUsdClassesModule` |
| `HashObjectPackage` | 计算一个 UObject 及其关联文件的哈希值，用于检测变更。 | `IUsdClassesModule` |
| `SetBoundsMin` / `SetDrawMode` | 设置 `UUsdDrawModeComponent` 的边界或绘制模式。 | `UUsdDrawModeComponent` |

### 使用示例（蓝图描述）

1.  **配置项目设置**：在 `项目设置 -> USDCore` 中，可以指定“默认资产缓存”对象（`UUsdAssetCache3` 类型的资产）、设置各种对话框行为、以及替换默认的 USD 材质。
2.  **使用资产缓存**：
    -   在蓝图中，获取一个 `UUsdAssetCache3` 对象引用（通常从 `AUsdStageActor` 的属性或通过项目设置获取）。
    -   当需要根据 USD prim 数据生成一个 UE 材质实例时，调用 `GetOrCreateCachedAsset`。传入一个基于 prim 数据计算的唯一哈希值、目标类（`UMaterialInstanceDynamic`）、期望的名称和标志。如果缓存中已有该哈希对应的资产，则直接返回；否则创建一个新的。
    -   在生成资产后，调用 `AddAssetReferencer` 将生成资产的组件或 Actor 注册为该资产的引用者，确保在清理时不会被误删。
3.  **清理缓存**：当不再需要某些 USD 阶段时，可以调用 `DeleteUnreferencedAssets` 来释放不再使用的资产所占用的磁盘和内存。

## C++ 用法

### 头文件引入

```cpp
#include "USDClassesModule.h"
#include "USDAssetCache3.h"
#include "USDObjectUtils.h"
#include "USDMaterialUtils.h"
```

### 基本用法

以下代码展示了如何获取模块接口、使用资产缓存和计算对象哈希。

*来源：基于 `USDClassesModule.h` 和 `USDAssetCache3.h` 的公共 API。*

```cpp
// 1. 获取模块接口并发送分析事件
IUsdClassesModule& USDClassesModule = FModuleManager::Get().LoadModuleChecked<IUsdClassesModule>("USDClasses");
TArray<FAnalyticsEventAttribute> Attributes;
Attributes.Add(FAnalyticsEventAttribute(TEXT("Details"), TEXT("Some details")));
USDClassesModule.SendAnalytics(MoveTemp(Attributes), TEXT("Export.StaticMesh"), /*bAutomated=*/false, /*ElapsedSeconds=*/2.5, /*NumberOfFrames=*/1, TEXT("usda"));

// 2. 计算对象包的哈希，用于增量导出
FSHA1 Hasher;
if (USDClassesModule.HashObjectPackage(MyStaticMesh, Hasher))
{
    FSHAHash FinalHash;
    Hasher.Finalize();
    Hasher.GetHash(FinalHash);
    UE_LOG(LogUsd, Log, TEXT("Asset hash: %s"), *FinalHash.ToString());
}

// 3. 使用 UUsdAssetCache3 模板方法
UUsdAssetCache3* AssetCache = /* 获取缓存对象 */;
FString Hash = TEXT("material_prim_hash_123");
bool bCreated = false;
UMaterialInstanceDynamic* MID = AssetCache->GetOrCreateCachedAsset<UMaterialInstanceDynamic>(
    Hash,
    TEXT("MyMID"),
    RF_NoFlags,
    &bCreated,
    /*Referencer=*/this // 将当前对象注册为引用者
);
```

### 进阶用法

自定义资产创建逻辑和使用作用域引用器。

*来源：基于 `USDAssetCache3.h` 中的 `GetOrCreateCustomCachedAsset` 和 `FUsdScopedReferencer`。*

```cpp
// 1. 使用自定义创建函数（例如，用于创建纹理）
FString TextureHash = TEXT("texture_prim_hash_456");
UTexture2D* Texture = AssetCache->GetOrCreateCustomCachedAsset<UTexture2D>(
    TextureHash,
    TEXT("MyTexture"),
    RF_Public | RF_Standalone,
    [](UPackage* PackageOuter, FName SanitizedName, EObjectFlags FlagsToUse) -> UObject*
    {
        // 这里可以调用 UTextureFactory 或其他复杂逻辑来创建纹理
        UTexture2D* NewTexture = NewObject<UTexture2D>(PackageOuter, SanitizedName, FlagsToUse);
        // ... 填充纹理数据 ...
        return NewTexture;
    },
    /*bOutCreatedAsset=*/nullptr,
    /*Referencer=*/nullptr
);

// 2. 使用作用域引用器，在一个代码块内自动管理引用
{
    // 在此作用域内，`StageActor` 将自动成为 `AssetCache` 中所有缓存资产的引用者
    UUsdAssetCache3::FUsdScopedReferencer ScopedRef(AssetCache, StageActor);
    
    // ... 执行一系列可能向缓存添加资产的操作（如加载USD阶段） ...
    
} // ScopedRef 析构时，会自动移除 StageActor 作为这些资产的引用者

// 3. 使用 ObjectUtils 工具函数
UUsdMeshAssetUserData* UserData = UsdUnreal::ObjectUtils::GetOrCreateAssetUserData<UUsdMeshAssetUserData>(MyStaticMesh);
if (UserData)
{
    UserData->PrimPaths.Add(TEXT("/Root/MyMesh"));
    UserData->OriginalHash = Hash;
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何创建一个资产缓存并使用它。

**MyUsdDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyUsdDemo.generated.h"

class UUsdAssetCache3;

UCLASS()
class AMyUsdDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyUsdDemo();

    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "USD")
    TObjectPtr<UUsdAssetCache3> AssetCache;

    /** 演示如何使用缓存获取或创建资产 */
    UFUNCTION(BlueprintCallable, Category = "USD Demo")
    UStaticMesh* GetOrCreateDemoMesh(const FString& Hash, const FString& Name);

private:
    /** 用于引用追踪的内部Actor */
    UPROPERTY()
    TObjectPtr<AActor> InternalReferencer;
};
```

**MyUsdDemo.cpp**
```cpp
#include "MyUsdDemo.h"
#include "USDAssetCache3.h"

AMyUsdDemo::AMyUsdDemo()
{
    PrimaryActorTick.bCanEverTick = false;
    // 创建一个临时的资产缓存用于演示
    AssetCache = CreateDefaultSubobject<UUsdAssetCache3>(TEXT("DemoAssetCache"));
}

void AMyUsdDemo::BeginPlay()
{
    Super::BeginPlay();
    // 创建一个内部Actor，专门用于持有对缓存资产的引用，便于后续管理
    InternalReferencer = GetWorld()->SpawnActor<AActor>();
}

UStaticMesh* AMyUsdDemo::GetOrCreateDemoMesh(const FString& Hash, const FString& Name)
{
    if (!AssetCache)
    {
        return nullptr;
    }

    bool bCreated = false;
    // 使用缓存获取或创建一个StaticMesh
    UStaticMesh* Mesh = AssetCache->GetOrCreateCachedAsset<UStaticMesh>(
        Hash,
        Name,
        RF_Public | RF_Standalone,
        &bCreated,
        InternalReferencer // 将InternalReferencer注册为该资产的引用者
    );

    if (bCreated && Mesh)
    {
        UE_LOG(LogTemp, Log, TEXT("Created new mesh '%s' with hash '%s' in cache."), *Name, *Hash);
        // 在这里可以对新创建的Mesh进行初始化，例如加载模型数据
        // Mesh->SetStaticMesh(...);
    }
    else if (Mesh)
    {
        UE_LOG(LogTemp, Log, TEXT("Retrieved existing mesh '%s' from cache."), *Name);
    }

    return Mesh;
}
```

## 模块依赖

使用 `USDCore` 插件本身不需要额外依赖，但若要在此基础上开发，可能需要依赖其内部模块。

| 模块 | 用途 |
|---|---|
| `USDClasses` | 访问资产缓存、项目设置、用户数据等核心 UE-USD 类。 |
| `USDUtilities` | 访问底层的 USD 转换工具函数。 |
| `UnrealUSDWrapper` | 直接调用 USD SDK 函数。依赖 `Python3`。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `561d9c2d` | USD Pregen: Fix materials inside instances not being deduplicated; | 修复了预生成时，实例内部的材质未被去重的问题。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数产生警告的代码。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了用于格式化函数的枚举可能导致输出乱码的问题。 |
| 2026-04-28 | `5b5d2b22` | [USD] Harden USDZ extraction in InterchangeUSD against path traversal (Zip Slip) and unsafe archive | 增强了 USDZ 提取的安全性，防止路径遍历和不安全的存档。 |
| 2026-04-28 | `bf5d0e5b` | USD: Add Nanite/mesh build settings schemas | 添加了 Nanite/网格体构建设置的 USD 模式。 |

### 维护评价

**实验性且活跃维护**。USDCore 插件标记为 `IsBetaVersion=true`，表明其 API 和行为可能还不稳定，未来会有较大变动。然而，从近期的提交历史来看，该插件正处于非常活跃的开发和维护阶段。最近的更新主要集中在功能增强（如添加 Nanite 设置模式）、错误修复（材质去重、浮点精度警告）和安全性加固上。鉴于其作为整个 USD 工作流基石的关键地位，Epic Games 很可能会持续投入进行维护和完善。目前可以安全地用于开发和生产预览，但需注意可能存在的破坏性更改。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/USDCore)
-   [官方文档]() （暂无）