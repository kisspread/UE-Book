# Significance Manager

> The significance manager plugin provides an extensible framework for allowing games to calculate the significance of an object and change behavior in response.

| 属性 | 值 |
|---|---|
| 分类 | Performance |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | SignificanceManager (Runtime) |
| 创建时间 | 2016-12-08 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SignificanceManager) | |

## 用途

SignificanceManager 为游戏提供了一个**重要性评估框架**，用于根据对象相对于玩家视角的距离和位置计算一个"重要性值"（significance），然后游戏逻辑可以基于这个值决定如何处理该对象——例如降低 LOD、减少 Tick 频率、跳过粒子特效等。

核心解决的问题：当场景中有大量对象（NPC、特效、音频源等）时，不可能对所有对象一视同仁地运行全精度逻辑。SignificanceManager 提供了一个统一的注册/查询机制，让每个对象声明自己的重要性计算方式，游戏代码再根据重要性值做分级处理。

**注意：** `EnabledByDefault = false`，需要在项目的 `.uproject` 或插件设置中手动启用。

## 使用场景

- 你有大量 NPC/敌人，需要根据与玩家的距离动态调整 AI Tick 频率、动画更新率
- 场景中有大量粒子特效或音频源，需要根据重要性决定是否播放
- 你需要一个统一的系统来管理所有对象的"细节层级"决策，而不是每个系统各自实现距离判断
- 你需要支持分屏/多视角，SignificanceManager 原生支持多 Viewpoint

## 蓝图用法

SignificanceManager 的核心 API 都是 C++ 层面的，蓝图直接访问较少。但可以通过以下方式间接使用：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Significance Manager` | 静态方法，获取当前 World 的 SignificanceManager 实例 | `USignificanceManager` |
| `Get Significance` | 查询某个对象的重要性值 | `USignificanceManager` |
| `Query Significance` | 查询对象是否被管理及其重要性值 | `USignificanceManager` |

> 由于 `RegisterObject` / `UnregisterObject` 接受 C++ lambda 作为重要性计算函数，蓝图中无法直接注册对象。实际使用中通常在 C++ 中完成注册逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "SignificanceManager.h"
```

### 基本用法

注册对象到 SignificanceManager 并在每帧查询重要性值：

```cpp
// 获取 SignificanceManager 实例
USignificanceManager* SigMan = USignificanceManager::Get(GetWorld());
if (!SigMan)
{
    return; // 插件未启用或 World 无效
}

// 注册对象，提供 Tag 和重要性计算函数
SigMan->RegisterObject(
    this,                                      // 要注册的 UObject
    FName("NPC"),                              // Tag，用于分组
    USignificanceManager::FManagedObjectSignificanceFunction(
        [](USignificanceManager::FManagedObjectInfo* ObjectInfo, const FTransform& Viewpoint) -> float
        {
            // 计算对象到 Viewpoint 的距离，返回重要性值
            // 值越大越重要（默认行为，取决于 bSortSignificanceAscending）
            UObject* Obj = ObjectInfo->GetObject();
            float Distance = FVector::Distance(
                Cast<AActor>(Obj)->GetActorLocation(),
                Viewpoint.GetLocation()
            );
            // 距离越近，重要性越高（返回值越大）
            return 1.0f / FMath::Max(Distance, 1.0f);
        }
    )
);

// 查询重要性值
float Significance = SigMan->GetSignificance(this);
// 或使用带布尔返回的版本
float OutSig;
if (SigMan->QuerySignificance(this, OutSig))
{
    // 根据 OutSig 调整行为
}

// 对象销毁时必须反注册（否则会导致悬挂指针和崩溃）
SigMan->UnregisterObject(this);
```

> 来源：`SignificanceManager.h` 中 `RegisterObject` / `UnregisterObject` / `GetSignificance` / `QuerySignificance` 的声明和 `SignificanceManager.cpp` 中的实现。

### 进阶用法

#### 使用 PostSignificance 回调

当重要性值更新后需要执行后续操作（如切换 LOD）时，可以提供 PostSignificance 回调：

```cpp
SigMan->RegisterObject(
    this,
    FName("Character"),
    // 重要性计算函数
    USignificanceManager::FManagedObjectSignificanceFunction(
        [](USignificanceManager::FManagedObjectInfo* ObjectInfo, const FTransform& Viewpoint) -> float
        {
            AActor* Actor = Cast<AActor>(ObjectInfo->GetObject());
            return FVector::Dist(Actor->GetActorLocation(), Viewpoint.GetLocation());
        }
    ),
    // PostSignificanceType: Concurrent（可并行）或 Sequential（必须顺序执行）
    USignificanceManager::EPostSignificanceType::Concurrent,
    // PostSignificance 回调
    USignificanceManager::FManagedObjectPostSignificanceFunction(
        [](USignificanceManager::FManagedObjectInfo* ObjectInfo,
           float OldSignificance, float NewSignificance, bool bUnregistering)
        {
            // OldSignificance: 上一帧的重要性值
            // NewSignificance: 当前帧的重要性值
            // bUnregistering: 是否正在反注册
            if (NewSignificance < 0.001f && OldSignificance >= 0.001f)
            {
                // 从"重要"变为"不重要"，可以降低 LOD 等
            }
        }
    )
);
```

#### 按 Tag 查询和批量反注册

```cpp
// 获取某个 Tag 下的所有对象（已按重要性排序）
const TArray<USignificanceManager::FManagedObjectInfo*>& NPCs = SigMan->GetManagedObjects(FName("NPC"));
for (const auto* Info : NPCs)
{
    UObject* Obj = Info->GetObject();
    float Sig = Info->GetSignificance();
    // 对每个 NPC 根据重要性做不同处理
}

// 批量反注册某个 Tag 下的所有对象
SigMan->UnregisterAll(FName("NPC"));
```

#### 每帧更新重要性

```cpp
// 通常在 GameViewportClient::Tick 或类似位置调用
TArray<FTransform> Viewpoints;
Viewpoints.Add(PlayerCameraTransform);  // 可以添加多个视角（分屏）
SigMan->Update(Viewpoints);
```

#### 自定义子类

通过配置 `SignificanceManagerClassName`（在 DefaultEngine.ini 或项目设置中），可以使用自定义的 `USignificanceManager` 子类来重写 `Update`、`RegisterObject` 等虚函数。

### FOrderedBudget 辅助工具

`OrderedBudget.h` 提供了一个预算分配工具，用于按重要性顺序分配资源预算（如 LOD 级别）：

```cpp
#include "OrderedBudget.h"

FOrderedBudget Budget;
// 规格字符串：第0级0个，第1级2个，第2级3个，第3级5个
// 展开为：索引0→LOD1, 索引1→LOD1, 索引2→LOD2, 索引3→LOD2, 索引4→LOD2, ...
Budget.RecreateBudget("0,2,3,5");

// 获取第 i 个最近对象的 LOD 级别
int32 LODLevel = Budget.GetBudgetForIndex(i);
```

## Demo 示例

### Build.cs 依赖

```csharp
// YourModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[] {
    "SignificanceManager"
});
```

### 最小完整示例

```cpp
// MySignificanceActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MySignificanceActor.generated.h"

UCLASS()
class AMySignificanceActor : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
};

// MySignificanceActor.cpp
#include "MySignificanceActor.h"
#include "SignificanceManager.h"

void AMySignificanceActor::BeginPlay()
{
    Super::BeginPlay();

    if (USignificanceManager* SigMan = USignificanceManager::Get(GetWorld()))
    {
        SigMan->RegisterObject(
            this,
            FName("MyActors"),
            [](USignificanceManager::FManagedObjectInfo* Info, const FTransform& Viewpoint) -> float
            {
                AActor* Actor = Cast<AActor>(Info->GetObject());
                if (!Actor) return 0.f;
                return 1.0f / FMath::Max(FVector::Dist(Actor->GetActorLocation(), Viewpoint.GetLocation()), 1.0f);
            }
        );
    }
}

void AMySignificanceActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (USignificanceManager* SigMan = USignificanceManager::Get(GetWorld()))
    {
        SigMan->UnregisterObject(this);
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

SignificanceManager 的 Build.cs 中只有 `PrivateDependencyModuleNames`，意味着使用者不需要额外依赖这些模块（它们是内部依赖）。使用者只需在自己的 Build.cs 中添加 `SignificanceManager` 即可。

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和容器 |
| `CoreUObject` | UObject 系统 |
| `Engine` | World、Canvas 等引擎功能 |
| `EngineSettings` | 控制台设置 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-06-13 | `65e82582` | Replace some usages of FORCEINLINE with inline in SignificanceManager | 代码风格微调，将 `FORCEINLINE` 替换为 `inline`，无功能变化 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar instead of on types | 构建系统适配，DLL 导出方式调整，无功能变化 |
| 2025-01-10 | `4720e52b` | PR #12649: Virtual USignificanceManager::OnShowDebugInfo | 将 `OnShowDebugInfo` 改为虚函数，允许子类自定义调试显示 |

### 维护评价

- **创建时间**：2016 年 12 月，已存在约 9.4 年
- **最近更新**：2025 年 6 月有更新，但均为构建/风格层面的改动，无实质性功能更新
- **维护状态**：**维护不活跃** — 核心功能早已稳定，近年仅有被动维护（构建系统适配、小重构）
- **已知限制**：
  - `EnabledByDefault = false`，需手动启用
  - 重要性计算函数使用 `TFunction`（lambda），无法在蓝图中直接注册对象
  - 注册的对象必须在销毁前反注册，否则会导致崩溃
- **推荐使用**：✅ 推荐。这是一个成熟、稳定、轻量的工具。虽然更新不频繁，但正说明其设计已经足够完善。Epic 自己的项目（如 Fortnite）也在使用此系统。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SignificanceManager)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
