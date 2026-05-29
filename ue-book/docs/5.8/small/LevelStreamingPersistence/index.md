# Level Streaming Persistence

> An experimental framework for persisting world state: actor and subobject property values, actor destroyed states, and actor respawning. State is associated with streaming levels, and optionally the persistent level.

| 属性 | 值 |
|---|---|
| 中文名 | 关卡流式持久化 |
| 分类 | Runtime |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LevelStreamingPersistence` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-04-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LevelStreamingPersistence) | |

## 用途

这个插件提供了一个实验性框架，用于在关卡流式加载时持久化世界状态。它解决了传统流式加载中世界状态丢失的核心问题：当关卡被卸载（流式隐藏）再重新加载时，玩家对世界所做的改变（如移动物体、打开宝箱、摧毁障碍物）会丢失，导致游戏体验不连贯。

具体来说，插件能够：
1.  **持久化属性值**：自动保存和恢复Actor及其子对象的特定属性值（如位置、生命值、拾取状态）。
2.  **记录Actor销毁**：记住哪些在关卡中预放置（Map-Placed）的Actor被玩家摧毁，并在关卡重新加载时再次将其摧毁。
3.  **管理运行时生成的Actor**：允许将运行时生成的Actor（如玩家建造的结构）与特定关卡关联，并在该关卡重新加载时自动重新生成。

所有持久化的状态数据都与流式加载的关卡绑定，可以选择性地包含持久关卡。

## 使用场景

- **开放世界游戏**：玩家在多个区域间移动，需要保持每个区域内的状态变化（如完成的任务、收集的物品）。
- **带有大量可破坏环境的游戏**：破坏效果需要在区域重新加载时保留。
- **玩家建造/修改世界的游戏**：例如建造基地或铺设道路，这些运行时创建的物体需要在对应关卡重载时恢复。
- **需要复杂存档系统的项目**：将关卡状态序列化为字节数组，可以轻松集成到现有的存档系统中。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SerializeTo` | 将当前地图所有流式关卡的持久化属性序列化为字节数组，可用于存档。 | `ULevelStreamingPersistenceManager` |
| `InitializeFrom` | 从先前序列化的字节数组中反序列化数据，恢复关卡状态。 | `ULevelStreamingPersistenceManager` |
| `EjectPlacedActor` | “弹出”一个地图预放置的Actor，使其在本次会话中保持存活，但在下次重载时消失。 | `ULevelStreamingPersistenceManager` |
| `RecreateActorInLevel` | 将一个Actor（通常是地图预放置的）的持久化状态转移到另一个关卡，使其成为运行时生成的Actor并可跨边界存在。 | `ULevelStreamingPersistenceManager` |
| `RecreateActorInPersistentLevel` | 将一个Actor移动到持久关卡，使其成为运行时生成的Actor。 | `ULevelStreamingPersistenceManager` |

### 使用示例（蓝图描述）

1.  **存档**：在玩家触发保存点时，获取`Level Streaming Persistence Manager`子系统，调用`SerializeTo`节点，将返回的`Payload`（`TArray<uint8>`）存入你的存档文件。
2.  **读档**：在游戏开始时，从存档中加载`Payload`，获取子系统并调用`InitializeFrom`节点。**重要**：最好在自定义的`UWorldSubsystem::Initialize`中调用，以确保在Actor的`BeginPlay`之前恢复状态。
3.  **动态破坏**：当玩家摧毁一个`bPersistAllActorDestruction`为true或属于`PersistedActorDestructionAllowList`的Actor时，系统会自动记录。再次加载该关卡时，该Actor会自动被销毁。

## C++ 用法

### 头文件引入

```cpp
#include "LevelStreamingPersistence/LevelStreamingPersistenceManager.h"
#include "LevelStreamingPersistence/LevelStreamingPersistenceModule.h"
```

### 基本用法

**序列化与反序列化世界状态**

```cpp
// 来自源码：ULevelStreamingPersistenceManager::SerializeTo 和 InitializeFrom
void UMySaveSubsystem::SaveGame()
{
    ULevelStreamingPersistenceManager* PersistenceManager = GetWorld()->GetSubsystem<ULevelStreamingPersistenceManager>();
    if (PersistenceManager && PersistenceManager->IsEnabled())
    {
        TArray<uint8> SavePayload;
        // 强制更新所有可见关卡的持久化数据，以确保保存最新的世界快照
        if (PersistenceManager->SerializeTo(SavePayload, true))
        {
            // 将 SavePayload 存入你的存档对象
            MySaveGame->PersistentData = SavePayload;
        }
    }
}

void UMySaveSubsystem::LoadGame()
{
    ULevelStreamingPersistenceManager* PersistenceManager = GetWorld()->GetSubsystem<ULevelStreamingPersistenceManager>();
    if (PersistenceManager && PersistenceManager->IsEnabled() && MySaveGame)
    {
        // 从存档对象中恢复
        if (!PersistenceManager->InitializeFrom(MySaveGame->PersistentData))
        {
            UE_LOG(LogLevelStreamingPersistence, Error, TEXT("Failed to initialize level streaming persistence from save data."));
        }
    }
}
```

### 进阶用法

**使用模块接口进行自定义游戏逻辑**

插件提供了`ILevelStreamingPersistenceModule`接口，允许你注册回调来精细控制持久化行为。

```cpp
// 来自源码：ILevelStreamingPersistenceModule 接口
void UMyGameModule::StartupModule()
{
    if (ILevelStreamingPersistenceModule::IsAvailable())
    {
        ILevelStreamingPersistenceModule& Module = ILevelStreamingPersistenceModule::Get();

        // 示例1: 自定义属性持久化条件 (只持久化根组件的RelativeLocation)
        Module.OnShouldPersistProperty<USceneComponent>().BindLambda([](const UObject* Object, const FProperty* Property) -> bool
        {
            if (Property->GetName() == TEXT("RelativeLocation"))
            {
                const USceneComponent* SceneComp = Cast<USceneComponent>(Object);
                if (SceneComp && SceneComp->IsRootComponent())
                {
                    return true; // 只有根组件的位置才持久化
                }
            }
            return false; // 其他情况不持久化
        });

        // 示例2: 在属性恢复后执行自定义逻辑
        Module.OnPostRestoreObject<APickupActor>().BindLambda([](const UObject* Object, const TArray<const FProperty*>& RestoredProperties)
        {
            const APickupActor* Pickup = Cast<APickupActor>(Object);
            if (Pickup && Pickup->IsPickedUp())
            {
                // 根据恢复的“已拾取”状态，更新UI或其他系统
                Pickup->UpdateVisualsForPickedUpState();
            }
        });
    }
}
```

## Demo 示例

**.h**
```cpp
#pragma once
#include "Subsystems/GameInstanceSubsystem.h"
#include "LevelStreamingPersistenceManager.h" // 假设已添加模块依赖
#include "MyDemoSubsystem.generated.h"

UCLASS()
class UMyDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    UFUNCTION(BlueprintCallable)
    void SaveWorldState();

    UFUNCTION(BlueprintCallable)
    void LoadWorldState();
};
```

**.cpp**
```cpp
#include "MyDemoSubsystem.h"
#include "Engine/World.h"

void UMyDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
}

void UMyDemoSubsystem::SaveWorldState()
{
    UWorld* World = GetWorld();
    if (!World) return;

    ULevelStreamingPersistenceManager* PersistenceManager = World->GetSubsystem<ULevelStreamingPersistenceManager>();
    if (PersistenceManager && PersistenceManager->IsEnabled())
    {
        TArray<uint8> SaveData;
        // 保存当前世界状态
        if (PersistenceManager->SerializeTo(SaveData, true))
        {
            // 在这里将SaveData保存到文件或云存储
            UE_LOG(LogTemp, Log, TEXT("World state saved, size: %d bytes"), SaveData.Num());
        }
    }
}

void UMyDemoSubsystem::LoadWorldState()
{
    UWorld* World = GetWorld();
    if (!World) return;

    ULevelStreamingPersistenceManager* PersistenceManager = World->GetSubsystem<ULevelStreamingPersistenceManager>();
    if (PersistenceManager && PersistenceManager->IsEnabled())
    {
        TArray<uint8> LoadedData;
        // 从文件或云存储加载LoadedData...

        // 恢复世界状态
        if (PersistenceManager->InitializeFrom(LoadedData))
        {
            UE_LOG(LogTemp, Log, TEXT("World state loaded successfully."));
        }
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件的核心依赖是引擎本身。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `54114a0f` | LevelStreamingPersistence: Added missing pre-persist hooks when saving runtime respawnable actors | 修复了保存可重生运行时Actor时缺少预持久化钩子的Bug。 |
| 2026-05-12 | `761b198b` | LevelStreamingPersistence: Changed RemovedMapActors to be keyed by FName instead of FSoftObjectPath. | 将已移除的地图Actor数据结构的键从`FSoftObjectPath`改为`FName`，可能为优化或解决特定问题。 |
| 2026-05-12 | `c3493909` | LevelStreamingPersistence: Cache redundant GetPathName() calls | 缓存了冗余的`GetPathName()`调用，属于性能优化。 |
| 2026-05-12 | `80b202ac` | LevelStreamingPersistence: Added support for actors in the persistent level, persistent actor destru | **重要更新**：新增了对持久关卡内Actor的支持，并实现了持久化Actor销毁功能。 |
| 2026-04-15 | `f0522de1` | LevelStreamingPersistence: Exposed configurable settings to editor as DeveloperSettings | 将插件的可配置设置暴露给编辑器作为开发者设置（`UDeveloperSettings`），便于项目配置。 |

### 维护评价

该插件是一个**活跃维护中**的实验性项目。
1.  **创建时间**：2023年4月，距今约2年。
2.  **近期更新**：在2026年4月至5月有密集的功能增强和Bug修复，特别是增加了持久关卡支持并将设置暴露到编辑器，表明其仍在被积极开发和集成。
3.  **状态**：`.uplugin`中`IsExperimentalVersion=true`且`EnabledByDefault=false`，确认其实验性质。
4.  **推荐**：**推荐在开发早期进行评估和试用**。由于是实验性功能，可能在复杂场景下存在未发现的问题，且API可能在未来版本中发生变化。但对于解决关卡流式加载中的状态持久化问题，它是一个非常有价值和前景的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LevelStreamingPersistence)
- 官方文档：无
- 测试用例：未在提供的路径中发现明显测试文件