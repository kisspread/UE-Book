# USD Core

> Adds support for USD SDK, UE wrapper classes and USD conversion utilities

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、蓝图资产） |
| 模块 | `UnrealUSDWrapper` (Runtime), `USDClasses` (Runtime), `USDUtilities` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-16 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/USDCore) | |

## 用途

USDCore 是 Unreal Engine 对 Pixar USD（Universal Scene Description）SDK 的核心集成层。它解决的核心问题是：**让 UE 能够读取、操作和写入 USD 格式的场景数据**。

这个插件本身不提供完整的 USD 导入/导出 UI 流程（那是 `USDImporter`/`USDExporter` 的职责），而是提供底层基础设施：

1. **UnrealUSDWrapper**：对 USD C++ SDK 的薄封装，处理 USD 库的加载、plugInfo 配置和跨平台兼容
2. **USDClasses**：定义 UE 侧的 USD 相关数据结构（资产缓存、元数据、绘制模式组件、材质工具等）
3. **USDUtilities**：提供 USD prim 与 UE 资产之间的转换工具函数

如果你需要在项目中使用 USD 工作流（例如从 DCC 工具导入 USD 场景、在运行时加载 USD 文件、或在多个 UE 实例间同步 USD 数据），这个插件是必需的基础设施。

## 使用场景

- 你在做一个需要从 Maya/Houdini/Blender 导入 USD 场景的影视级项目 → 启用 USDCore + USDImporter
- 你需要在运行时动态加载 USD 文件并生成 UE Actor → 使用 USDCore 提供的资产缓存和转换工具
- 你需要在多个关卡编辑器实例间共享 USD 资产以避免重复生成 → 使用 `UUsdAssetCache3`
- 你需要自定义 USD 材质到 UE 材质的映射 → 使用 `UsdUnreal::MaterialUtils` 命名空间
- 你需要为 USD prim 添加自定义元数据并追踪其来源 → 使用 `UUsdAssetUserData` 体系

## 蓝图用法

### 资产缓存（UUsdAssetCache3）

`UUsdAssetCache3` 是可在内容浏览器中创建的资产，用于缓存 USD 生成的 UObject，避免重复创建。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CacheAsset` | 将资产以指定 Hash 存入缓存，可选注册引用者 | `UUsdAssetCache3` |
| `GetCachedAsset` | 根据 Hash 获取已缓存的资产 | `UUsdAssetCache3` |
| `GetOrCreateCachedAsset` | 获取或创建缓存资产（核心方法） | `UUsdAssetCache3` |
| `CanRemoveAsset` | 检查资产是否可以安全移除 | `UUsdAssetCache3` |
| `RemoveAsset` | 从缓存移除资产并返回 | `UUsdAssetCache3` |
| `TouchAsset` | 标记资产为最近使用，防止被 LRU 淘汰 | `UUsdAssetCache3` |
| `AddAssetReference` | 为资产添加引用者，防止被驱逐 | `UUsdAssetCache3` |
| `RemoveAssetReference` | 移除资产的引用者 | `UUsdAssetCache3` |

### 绘制模式组件（UUsdDrawModeComponent）

用于可视化 USD prim 的 `UsdGeomModelAPI` 绘制模式（边界框、卡片、原点轴）。

| 属性 | 说明 |
|---|---|
| `DrawMode` | 绘制模式：Origin / Bounds / Cards |
| `BoundsMin` / `BoundsMax` | 边界框范围 |
| `BoundsColor` | 边界框颜色 |
| `CardGeometry` | 卡片几何类型：Cross / Box |
| `CardTextureXPos` ~ `CardTextureZNeg` | 六个方向的卡片纹理 |

### 参考选项（UUsdReferenceOptions）

添加 USD 引用或载荷时的配置对象。

| 属性 | 说明 |
|---|---|
| `bInternalReference` | 是否引用当前 Stage 内的 prim |
| `TargetFile` | 外部引用文件路径 |
| `bUseDefaultPrim` | 是否使用目标 Stage 的默认 prim |
| `TargetPrimPath` | 指定引用的 prim 路径 |
| `TimeCodeOffset` / `TimeCodeScale` | 时间采样属性的偏移和缩放 |

### 使用示例（蓝图描述）

**创建资产缓存并存取资产**：
1. 在内容浏览器中右键 → 创建 `USD Asset Cache` 资产
2. 将缓存资产赋给 `AUsdStageActor` 的 `AssetCache` 属性
3. 在蓝图中调用 `GetOrCreateCachedAsset`，传入 Hash 字符串和目标类，获取或创建资产
4. 使用 `AddAssetReference` 注册引用者防止资产被驱逐

**配置 USD Stage 选项**：
1. 创建 `FUsdStageOptions` 结构体
2. 设置 `MetersPerUnit`（默认 0.01 = 1cm，匹配 UE 单位）
3. 设置 `UpAxis`（默认 ZAxis，匹配 UE 约定）

## C++ 用法

### 头文件引入

```cpp
// 资产缓存
#include "USDAssetCache3.h"

// 资产用户数据
#include "USDAssetUserData.h"

// Stage 选项
#include "USDStageOptions.h"

// 材质工具
#include "USDMaterialUtils.h"

// 对象工具
#include "USDObjectUtils.h"

// 元数据
#include "USDMetadata.h"

// 绘制模式组件
#include "USDDrawModeComponent.h"

// 项目设置
#include "USDProjectSettings.h"
```

### 基本用法：资产缓存

```cpp
// 来源: USDAssetCache3.h - GetOrCreateCachedAsset

// 获取项目默认资产缓存
UUsdAssetCache3* Cache = IUsdClassesModule::GetAssetCacheForProject();

// 从缓存获取或创建材质实例
bool bCreated = false;
UMaterialInstanceDynamic* MID = Cache->GetOrCreateCachedAsset<UMaterialInstanceDynamic>(
    TEXT("some_hash_value"),       // 基于 prim 数据计算的哈希
    TEXT("MyMaterial"),            // 期望的资产名称
    RF_NoFlags,                    // 对象标志
    &bCreated,                     // 是否新创建
    nullptr                        // 引用者（可选）
);

if (bCreated)
{
    // 首次创建，需要初始化材质参数
    MID->SetVectorParameterValue(TEXT("BaseColor"), FLinearColor::Red);
}
```

### 基本用法：资产用户数据

```cpp
// 来源: USDObjectUtils.h - GetOrCreateAssetUserData

// 为已有的 UStaticMesh 添加 USD 用户数据
UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/MyMesh"));

UUsdAssetUserData* UserData = UsdUnreal::ObjectUtils::GetOrCreateAssetUserData<UUsdMeshAssetUserData>(Mesh);
UserData->PrimPaths.Add(TEXT("/Root/MyPrim/Geometry"));
UserData->OriginalHash = TEXT("abc123");

// 检索用户数据
UUsdMeshAssetUserData* MeshUserData = UsdUnreal::ObjectUtils::GetAssetUserData<UUsdMeshAssetUserData>(Mesh);
if (MeshUserData)
{
    for (const FString& PrimPath : MeshUserData->PrimPaths)
    {
        UE_LOG(LogUsd, Log, TEXT("Mesh generated from prim: %s"), *PrimPath);
    }
}
```

### 进阶用法：材质工具

```cpp
// 来源: USDMaterialUtils.h

// 根据 DisplayColor 数据描述获取参考材质路径
UsdUnreal::MaterialUtils::FDisplayColorMaterial Desc;
Desc.bHasOpacity = true;
Desc.bIsDoubleSided = false;

const FSoftObjectPath* MaterialPath = UsdUnreal::MaterialUtils::GetReferenceMaterialPath(Desc);
if (MaterialPath)
{
    UMaterialInterface* Mat = Cast<UMaterialInterface>(MaterialPath->TryLoad());
}

// 获取 UsdPreviewSurface 参考材质（带半透明属性）
FSoftObjectPath PreviewMatPath = UsdUnreal::MaterialUtils::GetReferencePreviewSurfaceMaterial(
    EUsdReferenceMaterialProperties::Translucent
);

// 注册自定义渲染上下文
UsdUnreal::MaterialUtils::RegisterRenderContext(FName(TEXT("MyCustomRenderer")));
```

### 进阶用法：元数据收集与过滤

```cpp
// 来源: USDMetadataImportOptions.h, USDMetadata.h

// 配置元数据导入选项
FUsdMetadataImportOptions Options;
Options.bCollectMetadata = true;
Options.bCollectFromEntireSubtrees = true;
Options.bCollectOnComponents = true;  // 也为组件收集（适用于 Xform、Camera 等不生成资产的 prim）
Options.BlockedPrefixFilters.Add(TEXT("customData:internal"));  // 忽略 customData.internal 下的条目

// 读取收集到的元数据
FUsdCombinedPrimMetadata CombinedMeta;
FUsdPrimMetadata* PrimMeta = CombinedMeta.PrimPathToMetadata.Find(TEXT("/Root/MyPrim"));
if (PrimMeta)
{
    FUsdMetadataValue* Value = PrimMeta->Metadata.Find(TEXT("customData:author"));
    if (Value)
    {
        // Value->TypeName 可能是 "string"
        // Value->StringifiedValue 可能是 "\"John Doe\""
        UE_LOG(LogUsd, Log, TEXT("Author: %s"), *Value->StringifiedValue);
    }
}
```

### 进阶用法：对象工具与唯一命名

```cpp
// 来源: USDObjectUtils.h

// 生成唯一资产名称
TSet<FString> UsedNames;
UsedNames.Add(TEXT("MyMesh"));
UsedNames.Add(TEXT("MyMesh_0"));

FString UniqueName = UsdUnreal::ObjectUtils::GetUniqueName(TEXT("MyMesh"), UsedNames);
// 结果: "MyMesh_1"

// 清理对象名称（移除 USD 非法字符）
FString CleanName = UsdUnreal::ObjectUtils::SanitizeObjectName(TEXT("My Prim/With:Special*Chars"));

// 获取带前缀的资产名称
FString PrefixedName = UsdUnreal::ObjectUtils::GetPrefixedAssetName(TEXT("MyMesh"), UStaticMesh::StaticClass());
```

## Demo 示例

### 最小示例：使用资产缓存管理 USD 生成的资产

```cpp
// MyUSDManager.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyUSDManager.generated.h"

class UUsdAssetCache3;
class UUsdAssetUserData;

UCLASS()
class AMyUSDManager : public AActor
{
    GENERATED_BODY()

public:
    AMyUSDManager();

    // 在编辑器中指定或留空使用项目默认缓存
    UPROPERTY(EditAnywhere, Category = "USD")
    TObjectPtr<UUsdAssetCache3> AssetCache;

    /** 模拟从 USD prim 生成材质并缓存 */
    UFUNCTION(BlueprintCallable, Category = "USD")
    UMaterialInstanceDynamic* GetOrCreateMaterial(const FString& PrimHash, const FString& PrimPath);

    /** 获取资产的 USD 来源 prim 路径 */
    UFUNCTION(BlueprintCallable, Category = "USD")
    FString GetSourcePrimPath(UObject* Asset) const;

protected:
    virtual void BeginPlay() override;
};
```

```cpp
// MyUSDManager.cpp
#include "MyUSDManager.h"

#include "USDAssetCache3.h"
#include "USDAssetUserData.h"
#include "USDObjectUtils.h"
#include "USDClassesModule.h"
#include "USDLog.h"

#include "Materials/MaterialInstanceDynamic.h"

AMyUSDManager::AMyUSDManager()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyUSDManager::BeginPlay()
{
    Super::BeginPlay();

    // 如果没有手动指定缓存，使用项目默认缓存
    if (!AssetCache)
    {
        AssetCache = IUsdClassesModule::GetAssetCacheForProject();
    }
}

UMaterialInstanceDynamic* AMyUSDManager::GetOrCreateMaterial(const FString& PrimHash, const FString& PrimPath)
{
    if (!AssetCache)
    {
        UE_LOG(LogUsd, Warning, TEXT("No asset cache available"));
        return nullptr;
    }

    // 尝试从缓存获取或创建材质
    bool bCreated = false;
    UMaterialInstanceDynamic* MID = AssetCache->GetOrCreateCachedAsset<UMaterialInstanceDynamic>(
        PrimHash,
        FString::Printf(TEXT("USD_Mat_%s"), *PrimPath.Replace(TEXT("/"), TEXT("_"))),
        RF_NoFlags,
        &bCreated,
        this  // 注册自身为引用者
    );

    if (MID && bCreated)
    {
        // 为新创建的材质设置默认参数
        MID->SetVectorParameterValue(TEXT("BaseColor"), FLinearColor::White);
        MID->SetScalarParameterValue(TEXT("Metallic"), 0.0f);
        MID->SetScalarParameterValue(TEXT("Roughness"), 0.5f);

        // 添加 USD 用户数据追踪来源
        UUsdAssetUserData* UserData = UsdUnreal::ObjectUtils::GetOrCreateAssetUserData(MID);
        UserData->PrimPaths.Add(PrimPath);
        UserData->OriginalHash = PrimHash;
    }

    return MID;
}

FString AMyUSDManager::GetSourcePrimPath(UObject* Asset) const
{
    if (!Asset) return FString();

    UUsdAssetUserData* UserData = UsdUnreal::ObjectUtils::GetAssetUserData(Asset);
    if (UserData && UserData->PrimPaths.Num() > 0)
    {
        return UserData->PrimPaths[0];
    }

    return FString();
}
```

```csharp
// MyModule.Build.cs - 模块依赖
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "USDClasses"    // USD 核心类
});

// 如果需要 USD 转换工具函数
// PrivateDependencyModuleNames.Add("USDUtilities");
```

## 模块依赖

从 Build.cs 分析，USDClasses 模块的依赖如下：

| 模块 | 用途 |
|---|---|
| `UnrealUSDWrapper` | USD SDK 的 UE 封装层，提供底层 USD API 访问 |
| `Python3` | UnrealUSDWrapper 依赖，用于 USD Python 绑定 |

**注意**：`USDClasses` 本身没有列出额外的非标准依赖（仅依赖 Core/Engine 等标准模块）。`UnrealUSDWrapper` 是唯一引入外部依赖（Python3）的模块。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 近期 | `2c158c4` | GetUsedTextures MaterialInterface 改用 TOptional 参数；OverrideNumericParameterDefault 重构为 Set/Clear 对 | 材质接口 API 重构，改善参数处理的类型安全性 |
| 近期 | `8c4cad9` | StaticMesh 的 WITH_EDITORONLY_DATA 属性改为访问器模式，SkeletalMesh 同步调整 | 编辑器数据访问模式标准化，提升封装性 |
| 近期 | `9803c44` | 添加 UE_INLINE_GENERATED_CPP_BY_NAME 宏 | 编译优化，减少生成的 .cpp 文件体积 |

### 维护评价

- **状态**：⚠️ 实验性（IsBetaVersion=true），默认未启用
- **活跃度**：活跃维护中。作为 UE 官方 USD 集成的核心基础设施，随引擎版本持续更新
- **API 稳定性**：存在较多 `UE_DEPRECATED` 标记（如 `UUsdAssetCache` → `UUsdAssetCache2` → `UUsdAssetCache3`，`UUsdAssetImportData` → `UUsdAssetUserData`），说明 API 仍在快速演进
- **注意事项**：
  - 标记为 Beta，API 可能在未来版本中发生变化
  - 需要手动启用（EnabledByDefault=false）
  - `UnrealUSDWrapper` 依赖 Python3 模块，打包时需注意
- **推荐**：如果你的项目需要 USD 工作流，这是必选插件。但需做好 API 变更的准备，建议锁定引擎版本使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/USDCore)
- [USD 官方文档](https://openusd.org/release/index.html)
- [UE USD 文档](https://docs.unrealengine.com/5.7/en-US/usd-support-in-unreal-engine/)