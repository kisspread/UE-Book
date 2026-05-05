# Data Registry

> Adds Data Registry system that can be used as a generic interface for acquiring structure data from multiple sources at runtime

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataRegistry` (Runtime), `DataRegistryEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-01-08 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/DataRegistry) | |

## 用途

Data Registry 提供了一个**统一的异步数据访问抽象层**，用于从多种数据源（DataTable、CurveTable 或自定义源）获取 USTRUCT 数据，并带有内置缓存机制。

它解决的核心问题是：游戏运行时需要从不同类型的数据表中获取结构化数据，但这些数据可能分散在多个表中、需要异步加载、或需要运行时动态替换来源。Data Registry 用一个 `FDataRegistryId`（Type:Name 对）作为统一标识，屏蔽了底层数据源的差异。

与直接使用 DataTable 相比，Data Registry 的优势：
- **多源聚合**：一个 Registry 可以配置多个 Source，按优先级依次查找
- **异步获取**：内置异步加载支持，回调通知就绪
- **缓存管理**：内置 LRU 缓存策略，可配置保留时间、最大条目数等
- **运行时动态注册**：支持运行时注册/注销数据源资产
- **Meta Source**：可通过目录扫描自动发现并注册多个 DataTable/CurveTable

## 使用场景

- 你需要一个统一接口来访问分散在多个 DataTable 中的配置数据（如武器属性、角色属性等），而不是硬编码引用某个特定表 → 用 DataRegistry 包装这些表，通过 `FDataRegistryId` 统一查询
- 你需要在 DLC 或热更新中动态替换数据源而不改动查询代码 → 用 Meta Source + 动态注册
- 你需要从 CurveTable 中按名称查找并求值曲线，且希望有缓存 → 用 `EvaluateDataRegistryCurve`
- 你想在代码中用 `FSoftDataRegistryOrTable` 让属性同时支持 DataTable 和 DataRegistry 两种模式

## 蓝图用法

DataRegistry 的蓝图接口全部在 `UDataRegistrySubsystem` 上暴露，通过静态函数调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Data Registry Item` | 同步获取缓存中的数据项，通过 OutItem 返回，bool 表示是否找到 | `UDataRegistrySubsystem` |
| `Find Data Registry Item` | 同步获取缓存中的数据项，有 Found/NotFound 两个执行输出引脚 | `UDataRegistrySubsystem` |
| `Acquire Data Registry Item` | 异步获取数据项，完成后通过回调通知 | `UDataRegistrySubsystem` |
| `Find Data Registry Item From Lookup` | 使用异步获取返回的 Lookup 从缓存中精确查找 | `UDataRegistrySubsystem` |
| `Evaluate Data Registry Curve` | 查找并求值 DataRegistry 中的曲线数据 | `UDataRegistrySubsystem` |
| `Get Possible Data Registry Id List` | 获取某个 Registry 类型下所有已知的 ID 列表 | `UDataRegistrySubsystem` |
| `Is Valid (DataRegistryType)` | 检查 DataRegistryType 是否有效 | `UDataRegistrySubsystem` |
| `Is Valid (DataRegistryId)` | 检查 DataRegistryId 是否有效 | `UDataRegistrySubsystem` |
| `To String (DataRegistryType)` | 将类型转为字符串 | `UDataRegistrySubsystem` |
| `To String (DataRegistryId)` | 将 ID 转为 "Type:Name" 格式字符串 | `UDataRegistrySubsystem` |
| `Equal / Not Equal (DataRegistryId)` | 比较两个 ID 或 Type 是否相等 | `UDataRegistrySubsystem` |

### 使用示例（蓝图描述）

**同步获取数据**：
1. 创建一个 `FDataRegistryId` 变量，设置 `RegistryType` 为你的注册表类型名（如 "WeaponStats"），`ItemName` 为目标行名（如 "Sword_Iron"）
2. 拖出 `Find Data Registry Item` 节点，连接 Id，OutItem 引脚类型选为你的结构体类型
3. Found 引脚 → 使用数据；NotFound 引脚 → 处理缺失

**异步获取数据**：
1. 调用 `Acquire Data Registry Item`，传入 Id 和一个回调委托
2. 在回调中，使用返回的 `ResolvedLookup` 调用 `Find Data Registry Item From Lookup` 获取数据
3. 注意：异步回调中内存仅在当前栈帧有效，应立即读取或复制数据

## C++ 用法

### 头文件引入

```cpp
#include "DataRegistrySubsystem.h"
#include "DataRegistryId.h"
#include "DataRegistryTypes.h"
```

### 基本用法

**同步获取缓存数据**：

```cpp
// 构造 DataRegistryId
FDataRegistryId ItemId(FName("WeaponStats"), FName("Sword_Iron"));

// 通过 Subsystem 获取缓存项
const UDataRegistrySubsystem* Subsystem = UDataRegistrySubsystem::Get();
if (Subsystem)
{
    // 模板版本，直接返回类型化指针
    const FMyWeaponStruct* WeaponData = Subsystem->GetCachedItem<FMyWeaponStruct>(ItemId);
    if (WeaponData)
    {
        // 使用数据
        float Damage = WeaponData->BaseDamage;
    }
}
```

**Raw 访问（泛型 C++）**：

```cpp
const uint8* ItemMemory = nullptr;
const UScriptStruct* ItemStruct = nullptr;

FDataRegistryCacheGetResult Result = Subsystem->GetCachedItemRaw(ItemMemory, ItemStruct, ItemId);
if (Result.WasFound())
{
    // ItemStruct 是实际结构体类型，可以做类型检查后 reinterpret_cast
    if (ItemStruct->IsChildOf(FMyWeaponStruct::StaticStruct()))
    {
        const FMyWeaponStruct* Data = reinterpret_cast<const FMyWeaponStruct*>(ItemMemory);
    }
}
```

### 异步获取

```cpp
FDataRegistryId ItemId(FName("WeaponStats"), FName("Sword_Iron"));

// 启动异步获取
Subsystem->AcquireItem(ItemId,
    FDataRegistryItemAcquiredCallback::CreateLambda(
        [](const FDataRegistryAcquireResult& Result)
        {
            if (Result.Status == EDataRegistryAcquireStatus::AcquireFinished)
            {
                // Result.GetItem<T>() 获取类型化数据
                const FMyWeaponStruct* Data = Result.GetItem<FMyWeaponStruct>();
                if (Data)
                {
                    // 使用数据 - 注意：仅在当前栈帧有效
                }
            }
        }
    )
);
```

### 曲线求值

```cpp
FDataRegistryId CurveId(FName("DamageCurves"), FName("LevelScaling"));

float OutValue = 0.0f;
const FRealCurve* OutCurve = nullptr;
FDataRegistryCacheGetResult CurveResult = Subsystem->EvaluateCachedCurve(
    OutValue, OutCurve, CurveId,
    /*InputValue=*/ 10.0f,  // 等级/时间
    /*DefaultValue=*/ 1.0f
);
```

### 遍历所有缓存项

```cpp
// 通过 UDataRegistry 实例遍历
const UDataRegistry* Registry = Subsystem->GetRegistryForType(FName("WeaponStats"));
if (Registry)
{
    Registry->ForEachCachedItem<FMyWeaponStruct>(
        TEXT("WeaponIteration"),
        [](const FName& Name, const FMyWeaponStruct& Item)
        {
            // 对每个缓存项执行操作
        }
    );
}
```

### 自定义 Resolver

```cpp
// 创建临时 resolver 作用域，用于将 DataRegistryId 映射到不同的 Source 名称
struct FMyResolver : public FDataRegistryResolver
{
    virtual bool ResolveIdToName(FName& OutResolvedName, const FDataRegistryId& ItemId,
        const UDataRegistry* Registry, const UDataRegistrySource* RegistrySource) override
    {
        // 自定义映射逻辑，例如将 GameplayTag 转换为行名
        if (ItemId.RegistryType == FName("MyType"))
        {
            OutResolvedName = FName(*ItemId.ItemName.ToString().Replace(TEXT("."), TEXT("_")));
            return true;
        }
        return false;
    }
};

// 使用栈上 resolver（作用域结束自动清理）
FMyResolver Resolver;
FDataRegistryResolverScope Scope(Resolver);
// 此作用域内的所有 DataRegistry 查询都会先经过 Resolver
```

### 动态注册资产

```cpp
// 注册一个 DataTable 资产到指定 Registry
FAssetData AssetData;
// ... 填充 AssetData
Subsystem->RegisterSpecificAsset(FDataRegistryType(FName("WeaponStats")), AssetData, /*Priority=*/ 10);

// 取消注册
Subsystem->UnregisterSpecificAsset(FDataRegistryType(FName("WeaponStats")), AssetPath);

// 批量预注册（在 Registry 尚未加载时也可调用）
TMap<FDataRegistryType, TArray<FSoftObjectPath>> AssetMap;
AssetMap.FindOrAdd(FDataRegistryType(FName("WeaponStats"))).Add(FSoftObjectPath("/Game/DT_Weapons"));
Subsystem->PreregisterSpecificAssets(AssetMap, /*Priority=*/ 0);
```

## Demo 示例

### Build.cs

```csharp
using UnrealBuildTool;

public class MyGame : ModuleRules
{
    public MyGame(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "DataRegistry"  // 依赖 DataRegistry 模块
        });
    }
}
```

### 最小示例：定义结构体并查询

```cpp
// MyWeaponData.h
#pragma once
#include "Engine/DataTable.h"
#include "MyWeaponData.generated.h"

USTRUCT(BlueprintType)
struct FMyWeaponData : public FTableRowBase
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float BaseDamage = 10.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float AttackSpeed = 1.0f;
};
```

```cpp
// MyGameplaySystem.cpp
#include "MyWeaponData.h"
#include "DataRegistrySubsystem.h"

void UMyGameplaySystem::LoadWeaponStats(const FName& WeaponName)
{
    const UDataRegistrySubsystem* DR = UDataRegistrySubsystem::Get();
    if (!DR) return;

    FDataRegistryId Id(FName("WeaponData"), WeaponName);

    // 方式1：同步读取缓存
    const FMyWeaponData* Cached = DR->GetCachedItem<FMyWeaponData>(Id);
    if (Cached)
    {
        UE_LOG(LogTemp, Log, TEXT("Damage: %f"), Cached->BaseDamage);
        return;
    }

    // 方式2：异步获取
    DR->AcquireItem(Id,
        FDataRegistryItemAcquiredCallback::CreateUObject(this, &UMyGameplaySystem::OnWeaponLoaded)
    );
}

void UMyGameplaySystem::OnWeaponLoaded(const FDataRegistryAcquireResult& Result)
{
    if (const FMyWeaponData* Data = Result.GetItem<FMyWeaponData>())
    {
        UE_LOG(LogTemp, Log, TEXT("Async loaded damage: %f"), Data->BaseDamage);
    }
}
```

## 模块依赖

从 `DataRegistry.Build.cs` 的 `PublicDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、日志 |
| `CoreUObject` | UObject 系统、反射、序列化 |
| `Engine` | DataTable、CurveTable、资产加载、Subsystem 基类 |
| `GameplayTags` | FGameplayTag 支持，用于 IdFormat 中的 Tag 层级命名 |
| `DeveloperSettings` | UDeveloperSettings 基类，用于项目设置面板 |

如果你的模块要使用 DataRegistry，需要在 Build.cs 中添加 `DataRegistry` 依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-09-23 | `419df4c5` | 为 DataRegistry 重置 ScalableFloat 变量时添加警告日志，方便调试 ID 无效的情况 |
| 2025-06-17 | `de2f01ed` | 新增 `WantsDelayedDataRegistryLoadingUntilPIE()` 和 `IsReadyForInitialization()` 方法，修复了编辑器中延迟加载 DataRegistry 的边界情况 |
| 2025-06-13 | `185bf170` | 将 Engine 模块中部分 `FORCEINLINE` 替换为 `inline`（代码规范化） |

### 维护评价

- **年龄**：约 5 年（2021 年 1 月创建），仍标记为 `IsBetaVersion = true`
- **活跃度**：2025 年仍有实质性功能更新（延迟加载修复、调试日志增强），属于**活跃维护**状态
- **状态**：虽然是 Beta 标记，但 Epic 自身在 Lyra 等项目中广泛使用，核心功能稳定
- **已知限制**：
  - `EnabledByDefault = false`，需要手动在插件设置中启用
  - Beta 版本，API 可能在未来版本变动
  - 蓝图中 `GetCachedItemBP` / `FindCachedItemBP` 使用 `CustomThunk`，OutItem 的类型需要与 Registry 的 ItemStruct 匹配
- **推荐**：如果你有多个 DataTable 需要统一管理、需要异步加载、或需要运行时数据源切换，推荐使用。对于简单的单表查询，直接用 DataTable 更简单

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/DataRegistry)
- 官方文档：无（.uplugin 中 DocsURL 为空）
