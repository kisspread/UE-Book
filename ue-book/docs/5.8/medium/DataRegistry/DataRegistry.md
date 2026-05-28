# Data Registry

> Adds Data Registry system that can be used as a generic interface for acquiring structure data from multiple sources at runtime

| 属性 | 值 |
|---|---|
| 中文名 | 数据注册表 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataRegistry` (Runtime), `DataRegistryEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-01-08 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/DataRegistry) | |

## 用途

DataRegistry 插件旨在提供一个**统一的、运行时可扩展的数据获取接口**。它解决了传统 `DataTable` 在大型项目中的几个痛点：

1.  **数据来源单一**：传统 `DataTable` 只能从单一的资产文件加载，而 `DataRegistry` 可以配置多个数据源（`UDataRegistrySource`），按优先级（如：预缓存的内存数据 > 本地 DataTable > 远程数据库）进行查找。
2.  **静态加载与异步支持不足**：`DataTable` 通常需要同步加载或预先硬引用。`DataRegistry` 原生支持**异步获取**（`AcquireItem`），并内置了完善的缓存策略（`FDataRegistryCachePolicy`），可以高效管理内存中的数据生命周期。
3.  **数据孤岛与引用问题**：游戏逻辑代码与具体的数据资产（如某个特定的 `UDataTable`）耦合紧密。通过 `DataRegistryId`（一个由 `RegistryType` 和 `ItemName` 组成的标识符），游戏逻辑可以声明式地请求数据，而无需关心数据实际存储在哪里，便于数据迁移、分包和热更新。

简单来说，它是 Epic 为超大型游戏（如《堡垒之夜》）设计的**高级数据管理系统**，旨在解耦数据提供者和数据消费者，并提供高性能的缓存与异步加载支持。

## 使用场景

- **大型角色扮演游戏 (RPG)**：需要管理成千上万的物品、技能、任务数据，且这些数据可能分布在多个 DLC 或需要在线更新。
- **需要运行时动态数据的游戏**：例如，从服务器下载赛季活动配置，或根据玩家进度解锁新的数据表。
- **追求加载性能优化的项目**：希望将数据加载从主线程剥离，或按需、分批加载非关键数据。
- **需要统一数据访问接口的复杂系统**：游戏中的 UI、AI、游戏逻辑等多个系统都需要访问同一套数据。

## 蓝图用法

DataRegistry 的蓝图 API 主要通过 `UDataRegistrySubsystem` 的静态方法暴露。这些方法处理了查找正确的注册表、缓存查找和异步请求的复杂逻辑。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Find Data Registry Item` | 同步尝试从缓存获取数据项，返回执行引脚（找到/未找到）和数据。**最常用的查询节点。** | `UDataRegistrySubsystem` |
| `Acquire Data Registry Item` | 启动一个异步数据获取请求，通过回调（`FDataRegistryItemAcquiredBPCallback`）通知结果。适用于可能需要加载的数据。 | `UDataRegistrySubsystem` |
| `Find Data Registry Item From Lookup` | 使用之前 `Acquire` 或 `Find` 获得的 `FDataRegistryLookup` 直接从缓存中精确获取，效率最高。 | `UDataRegistrySubsystem` |
| `Evaluate Data Registry Curve` | 从注册表中获取并评估一个曲线表中的曲线值。 | `UDataRegistrySubsystem` |
| `Get Possible Data Registry Id List` | 获取某个注册表类型下所有已知的 `DataRegistryId` 列表。 | `UDataRegistrySubsystem` |

### 使用示例（蓝图描述）

**场景：异步加载一个装备数据。**

1.  在角色蓝图中，定义一个 `FDataRegistryId` 类型的变量 `EquipRegistryId`，其 `RegistryType` 设置为 `“Equips”`， `ItemName` 设置为 `“Sword_001”`。
2.  调用 `Acquire Data Registry Item` 节点，将 `EquipRegistryId` 作为输入。
3.  将 `Acquire Callback` 连接到一个自定义事件（例如 `OnEquipDataLoaded`）。
4.  在 `OnEquipDataLoaded` 事件内，使用 `Find Data Registry Item From Lookup` 节点，传入事件提供的 `ResolvedLookup` 和 `EquipRegistryId`，获取最终的装备数据结构体。

## C++ 用法

在 C++ 中，主要通过 `UDataRegistrySubsystem` 单例和 `UDataRegistry` 类来使用。

### 头文件引入

```cpp
#include "DataRegistrySubsystem.h"
#include "DataRegistryTypes.h"
```

### 基本用法

**同步获取已缓存的数据项。**
来源：基于 `UDataRegistrySubsystem::GetCachedItem` 和 `UDataRegistry::GetCachedItem` 模板方法的用法。

```cpp
// 假设有一个自定义的装备数据结构体
USTRUCT(BlueprintType)
struct FMyEquipData : public FTableRowBase
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float AttackPower = 10.0f;
};

void AMyActor::QueryEquipData()
{
    // 构造数据项标识
    FDataRegistryId EquipId(FName("Equips"), FName("Sword_001"));

    // 通过子系统同步获取
    const FMyEquipData* Data = UDataRegistrySubsystem::Get()->GetCachedItem<FMyEquipData>(EquipId);
    if (Data)
    {
        UE_LOG(LogTemp, Log, TEXT("Sword Attack Power: %f"), Data->AttackPower);
    }
}
```

### 进阶用法

**异步加载数据并处理回调。**
来源：基于 `UDataRegistrySubsystem::AcquireItem` 和 `FDataRegistryAcquireResult` 的用法。

```cpp
// 在 Actor 的头文件中声明回调
DECLARE_DYNAMIC_DELEGATE_OneParam(FOnDataAcquired, const FDataRegistryAcquireResult&, Result);

// .cpp 中
void AMyActor::StartAsyncLoad()
{
    FDataRegistryId ItemId(FName("Items"), FName("Potion_001"));
    FOnDataAcquired Callback;
    Callback.BindDynamic(this, &AMyActor::HandleAsyncData);

    if (UDataRegistrySubsystem::Get()->AcquireItem(ItemId, Callback))
    {
        UE_LOG(LogTemp, Log, TEXT("Async load started for %s"), *ItemId.ToString());
    }
}

void AMyActor::HandleAsyncData(const FDataRegistryAcquireResult& Result)
{
    if (Result.Status == EDataRegistryAcquireStatus::AcquireFinished)
    {
        // 使用模板函数安全获取数据
        const FMyItemData* Item = Result.GetItem<FMyItemData>();
        if (Item)
        {
            UE_LOG(LogTemp, Log, TEXT("Async load success. Item Name: %s"), *Item->DisplayName.ToString());
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Async load failed for %s. Status: %d"),
            *Result.ItemId.ToString(), static_cast<int32>(Result.Status));
    }
}
```

## Demo 示例

一个最小的可编译示例，展示如何定义、初始化和查询 DataRegistry。

**MyDataRegistryTypes.h**
```cpp
#pragma once
#include "DataRegistryTypes.h"
#include "MyDataRegistryTypes.generated.h"

// 定义一个将存储在 DataRegistry 中的结构体
USTRUCT(BlueprintType)
struct FMyCharacterStats : public FTableRowBase
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    float MaxHealth = 100.f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    float MoveSpeed = 600.f;
};
```

**MyCharacter.h**
```cpp
#pragma once
#include "GameFramework/Character.h"
#include "DataRegistryId.h"
#include "MyCharacter.generated.h"

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Data")
    FDataRegistryId StatsRegistryId; // e.g., Type="CharacterStats", Name="Warrior"

    void BeginPlay() override;

    UFUNCTION(BlueprintCallable)
    void RefreshStats();

private:
    UFUNCTION()
    void OnStatsLoaded(const FDataRegistryAcquireResult& Result);
};
```

**MyCharacter.cpp**
```cpp
#include "MyCharacter.h"
#include "DataRegistrySubsystem.h"
#include "MyDataRegistryTypes.h"

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();
    // 开始异步加载角色属性
    if (StatsRegistryId.IsValid())
    {
        FDataRegistryItemAcquiredCallback Callback;
        Callback.BindUObject(this, &AMyCharacter::OnStatsLoaded);
        UDataRegistrySubsystem::Get()->AcquireItem(StatsRegistryId, Callback);
    }
}

void AMyCharacter::RefreshStats()
{
    // 尝试同步获取缓存数据
    const FMyCharacterStats* Stats = UDataRegistrySubsystem::Get()->GetCachedItem<FMyCharacterStats>(StatsRegistryId);
    if (Stats)
    {
        GetCharacterMovement()->MaxWalkSpeed = Stats->MoveSpeed;
        UE_LOG(LogTemp, Log, TEXT("Stats refreshed. Speed: %f"), Stats->MoveSpeed);
    }
}

void AMyCharacter::OnStatsLoaded(const FDataRegistryAcquireResult& Result)
{
    if (Result.Status == EDataRegistryAcquireStatus::AcquireFinished)
    {
        const FMyCharacterStats* Stats = Result.GetItem<FMyCharacterStats>();
        if (Stats)
        {
            // 应用加载到的属性
            GetCharacterMovement()->MaxWalkSpeed = Stats->MoveSpeed;
            UE_LOG(LogTemp, Log, TEXT("Async stats loaded. Health: %f, Speed: %f"), Stats->MaxHealth, Stats->MoveSpeed);
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to load stats for %s"), *StatsRegistryId.ToString());
    }
}
```

## 模块依赖

要使用 DataRegistry 插件，你的模块需要在 `.Build.cs` 中添加对以下模块的依赖（除了通用的 Core, Engine 等）。

| 模块 | 用途 |
|---|---|
| `DataRegistry` | DataRegistry 运行时核心逻辑。 |
| `GameplayTags` | `FDataRegistryId` 和 `FDataRegistryType` 的序列化与解析依赖 GameplayTags 系统。 |
| `AssetManager` | 用于资产扫描、元数据源（Meta Source）和资产优先级管理。 |
| `DeveloperSettings` | 提供 `UDataRegistrySettings` 配置类。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `ffe59a83` | Added toolsets for data registries. Current implemented commands include: | 为数据注册表添加了工具集，实现了新的管理命令。 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | 内容浏览器中新增了“添加数据”菜单项，方便创建注册表资产。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件代码中的日志宏从 UE_LOG 迁移到了 UE_LOGF。 |
| 2026-03-27 | `254999bd` | Removing ensure triggering with intentionally null data | 移除了在预期空数据时触发的断言，避免不必要的警告。 |
| 2026-03-20 | `992fad6c` | Gameplay systems deprecation removal pass for 5.4 and earlier, I skipped anything that was still in use. | 针对 5.4 及更早版本的游戏系统进行了废弃代码清理。 |

### 维护评价

DataRegistry 插件**处于活跃维护状态**。
- **创建时间**：2021年初，作为 UE5 预览功能引入。
- **更新频率**：近期（2026年4月）有密集的功能性更新（新增工具集、改进编辑器集成）和代码质量改进（日志迁移）。
- **实验性状态**：尽管 `.uplugin` 标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，但从持续的功能提交和没有废弃标记来看，它更像是一个**高级、尚未完全稳定**的生产级系统，而非被放弃的实验品。
- **推荐使用**：对于需要复杂数据管理的大型项目，特别是计划上线运营、需要热更新和高性能异步加载的游戏，**强烈推荐学习和使用**。但对于小型、数据结构简单的项目，传统的 `DataTable` 可能更直接。使用时需注意其异步API和缓存逻辑的学习成本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/DataRegistry)