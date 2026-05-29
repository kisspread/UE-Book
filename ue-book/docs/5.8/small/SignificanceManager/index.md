# Significance Manager

> The significance manager plugin provides an extensible framework for allowing games to calculate the significance of an object and change behavior in response.

| 属性 | 值 |
|---|---|
| 中文名 | 重要性管理器 |
| 分类 | Performance |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SignificanceManager` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-12-08 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SignificanceManager) | |

## 用途

Significance Manager 解决的核心问题是**大规模场景下的性能优化**。它提供了一个集中式框架，允许游戏根据“重要性”概念来动态管理物体的行为与细节层级。
“重要性”是一个由游戏逻辑定义的浮点数，通常基于物体与玩家摄像机的距离、朝向（是否在玩家视野内）、物体类型等因素计算得出。游戏的其他系统（如动画、AI、粒子效果、物理模拟、音频、LOD切换等）可以根据这个重要性值来决定是否降低更新频率、停止渲染、使用简化逻辑或完全忽略，从而实现性能的按需分配，将资源集中在对玩家体验影响最大的物体上。
插件的 `.uplugin` 描述较为通用，而从源码（`SignificanceManager.h`）可以看出，它管理对象的注册、注销，并提供按标签分类、查询重要性、以及一个可被主循环调用的 `Update` 函数来根据设定的视点更新所有对象的重要性。

## 使用场景

- **开放世界游戏**：远处NPC、植被、动态物体可以根据与玩家的距离和朝向，动态降低AI复杂度、动画更新频率或切换到更低的LOD，甚至暂时禁用。
- **第一/第三人称射击游戏**：对于玩家视野外或远离的子弹轨迹、弹壳、破坏的碎片，可以简化其物理模拟或直接禁用。
- **策略或塔防游戏**：大量单位同时存在时，根据单位在屏幕上的占比和重要性，决定其渲染细节或行为更新频率。
- **任何拥有大量需要“按需更新”的物体的场景**，都可以通过此框架统一管理。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Register Object` | 将一个 UObject 注册到重要性管理器，并指定其标签和重要性计算函数。 | `USignificanceManager` |
| `Unregister Object` | 将一个 UObject 从重要性管理器中注销。 | `USignificanceManager` |
| `Unregister All` | 注销所有具有指定标签的对象。 | `USignificanceManager` |
| `Get Significance` | 查询一个已注册对象的当前重要性值。如果对象未注册则返回 0。 | `USignificanceManager` |
| `Query Significance` | 查询对象的重要性，并返回是否成功。 | `USignificanceManager` |
| `Get Managed Objects` | 获取所有已注册的对象信息（`FManagedObjectInfo` 数组），可选择是否按重要性排序。 | `USignificanceManager` |

### 使用示例（蓝图描述）

1.  **初始化**：在游戏逻辑的合适位置（如 `GameMode` 或 `GameInstance` 的 `BeginPlay`），通过 `USignificanceManager::Get` 节点获取当前世界的重要性管理器实例。
2.  **注册对象**：当一个需要被管理的物体（如一个NPC Actor）生成时，调用 `Register Object` 节点。你需要提供：
    *   **Object**: 要注册的 Actor 或组件。
    *   **Tag**: 一个 `FName`（例如 `"NPC"`, `"Projectile"`），用于对同类对象分组。
    *   **Significance Function**: 一个自定义的计算函数（蓝图中的自定义事件或函数），该函数接收 `UObject*` 和 `FTransform`（视点），返回一个 `float` 重要性值。
    *   **(可选) Post Significance Function**: 一个在重要性更新后执行的函数。
3.  **更新重要性**：在游戏的主循环中（例如自定义的 `GameViewportClient::Tick` 或 `PlayerController` 的 Tick），从玩家摄像机获取视点变换，然后调用 `USignificanceManager::Update` 节点，传入视点数组。管理器会遍历所有已注册对象，调用它们的 `Significance Function` 更新重要性。
4.  **查询与使用**：在物体自身的逻辑中（如 `Event Tick`），可以通过 `Get Significance` 节点查询自己的当前重要性，然后根据该值调整行为，例如：
    *   如果重要性低于某个阈值，则降低动画更新速率或完全暂停。
    *   根据重要性值插值 LOD 等级。
    *   决定是否生成粒子特效。
5.  **注销**：当对象被销毁前，调用 `Unregister Object` 节点将其注销，防止内存泄漏和野指针。

## C++ 用法

### 头文件引入

```cpp
#include "SignificanceManager.h"
```

### 基本用法

**（注：以下示例综合自 `SignificanceManager.h` 中的 API 定义与常见用法模式。）**

```cpp
// 假设在某个 Actor 或 Component 中
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 获取重要性管理器实例
    if (USignificanceManager* SignificanceManager = FSignificanceManagerModule::Get(GetWorld()))
    {
        // 2. 注册对象
        // 定义重要性计算 Lambda
        auto SignificanceFunction = [](UObject* Object, const FTransform& ViewPoint) -> float
        {
            // 示例：根据距离计算重要性，距离越近，重要性越高
            AActor* Actor = Cast<AActor>(Object);
            if (Actor)
            {
                float Distance = FVector::Dist(Actor->GetActorLocation(), ViewPoint.GetLocation());
                return FMath::Clamp(1.0f - (Distance / 10000.0f), 0.0f, 1.0f);
            }
            return 0.0f;
        };

        // 注册，标签为 "MyActor"
        SignificanceManager->RegisterObject(
            this,
            FName("MyActor"),
            USignificanceManager::FManagedObjectSignificanceFunction(SignificanceFunction),
            USignificanceManager::EPostSignificanceType::None, // 不需要后处理
            nullptr
        );
    }
}

void AMyActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 3. 注销对象
    if (USignificanceManager* SignificanceManager = FSignificanceManagerModule::Get(GetWorld()))
    {
        SignificanceManager->UnregisterObject(this);
    }
    Super::EndPlay(EndPlayReason);
}
```

### 进阶用法

在自定义的 `GameViewportClient` 中驱动更新循环：

```cpp
// MyGameViewportClient.h
UCLASS()
class UMyGameViewportClient : public UGameViewportClient
{
    GENERATED_BODY()
public:
    virtual void Tick(float DeltaTime, bool bIdleMode) override;
};

// MyGameViewportClient.cpp
void UMyGameViewportClient::Tick(float DeltaTime, bool bIdleMode)
{
    Super::Tick(DeltaTime, bIdleMode);

    // 确保在有效的游戏世界中
    if (UWorld* World = GetWorld())
    {
        // 获取管理器实例
        if (USignificanceManager* SignificanceManager = USignificanceManager::Get(World))
        {
            // 收集视点（例如玩家摄像机的位置和旋转）
            TArray<FTransform> Viewpoints;
            // ... 根据你的游戏逻辑填充 Viewpoints 数组，例如从本地玩家控制器获取摄像机变换 ...

            // 调用 Update 来更新所有注册对象的重要性
            SignificanceManager->Update(Viewpoints);
        }
    }
}
```

## Demo 示例

一个演示注册、计算和查询的 Actor 示例。

### MySignificanceActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SignificanceManager.h"
#include "MySignificanceActor.generated.h"

UCLASS()
class AMySignificanceActor : public AActor
{
    GENERATED_BODY()

public:
    AMySignificanceActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    virtual void Tick(float DeltaTime) override;

private:
    // 用于演示的重要性值，可在蓝图中观察
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Significance", meta = (AllowPrivateAccess = "true"))
    float CurrentSignificance;

    // 重要性计算函数
    static float CalculateSignificance(UObject* Object, const FTransform& ViewPoint);
};
```

### MySignificanceActor.cpp

```cpp
#include "MySignificanceActor.h"
#include "SignificanceManager.h"

AMySignificanceActor::AMySignificanceActor()
{
    PrimaryActorTick.bCanEverTick = true;
    CurrentSignificance = 0.0f;
}

void AMySignificanceActor::BeginPlay()
{
    Super::BeginPlay();

    if (USignificanceManager* SM = FSignificanceManagerModule::Get(GetWorld()))
    {
        // 使用静态成员函数作为回调
        USignificanceManager::FManagedObjectSignificanceFunction SigFunc(&AMySignificanceActor::CalculateSignificance);
        SM->RegisterObject(this, FName("DemoObject"), SigFunc);
    }
}

void AMySignificanceActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (USignificanceManager* SM = FSignificanceManagerModule::Get(GetWorld()))
    {
        SM->UnregisterObject(this);
    }
    Super::EndPlay(EndPlayReason);
}

void AMySignificanceActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 查询当前重要性，用于调试或驱动其他逻辑
    if (USignificanceManager* SM = USignificanceManager::Get(GetWorld()))
    {
        float OutSignificance;
        if (SM->QuerySignificance(this, OutSignificance))
        {
            CurrentSignificance = OutSignificance;
            // 可以在此根据 CurrentSignificance 做出反应，例如：
            // if (CurrentSignificance < 0.2f) { 降低更新频率; }
        }
    }
}

// 静态函数，符合 FManagedObjectSignificanceFunction 签名
float AMySignificanceActor::CalculateSignificance(UObject* Object, const FTransform& ViewPoint)
{
    AMySignificanceActor* Self = Cast<AMySignificanceActor>(Object);
    if (!Self) return 0.0f;

    // 简单的距离衰减计算
    const float Distance = FVector::Dist(Self->GetActorLocation(), ViewPoint.GetLocation());
    const float MaxDistance = 5000.0f;
    return FMath::Clamp(1.0f - (Distance / MaxDistance), 0.0f, 1.0f);
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。
从源码规模和功能推断，`SignificanceManager` 模块的依赖应仅限于 `Core`、`CoreUObject`、`Engine` 等基础模块。插件自身不依赖其他特殊模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到新的 `UE_LOGF`。 |
| 2025-06-13 | `65e82582` | Replace some usages of FORCEINLINE with inline in SignificanceManager. | 在插件中，将部分 `FORCEINLINE` 替换为 `inline`，进行代码规范化。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 调整导出符号的规范，为所有方法和静态变量添加 `dllstorage`。 |
| 2025-01-10 | `4720e52b` | PR #12649: Virtual USignificanceManager::OnShowDebugInfo | 将 `OnShowDebugInfo` 函数虚化，使其可以被子类重写。 |
| 2024-11-10 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base | 清理旧版兼容性代码，移除 5.2 版本废弃的头文件包含顺序宏。 |

### 维护评价

Significance Manager 是一个创建于 **2016 年底**的“老古董”插件，拥有近 **9 年**历史。从近期提交记录来看，插件在 **2025-2026 年仍有活动**，但改动均为**编译适配、代码规范调整和符号导出修复**，没有新功能或重要的错误修复。
插件的架构在创建之初就较为成熟，API 稳定。虽然 `EnabledByDefault: false` 表明它并非所有项目必需，但它在需要性能优化的场景中依然是一个**成熟可靠的选择**。目前没有发现严重的已知问题。
**综合评价**：处于**维护状态但非活跃开发**。核心功能稳定，可以放心使用。如果项目需要此功能，它是一个久经考验的解决方案，但不要期待近期会有新特性加入。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SignificanceManager)
- [官方文档]()（无）