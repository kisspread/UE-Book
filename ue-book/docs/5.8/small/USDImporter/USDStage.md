# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD Schema 资产、材质模板等） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

USD Importer 为 Unreal Engine 提供了完整的 [USD（Universal Scene Description）](https://openusd.org) 支持，解决了影视和动画行业标准资产格式与 UE 之间的桥接问题。

该插件的核心功能包括：

- **USD Stage 加载与管理**：通过 `AUsdStageActor` 将 USD 文件作为舞台（Stage）加载到 UE 关卡中，自动将 USD Prim 树转换为 UE 的 Actor/Component 层级
- **资产自动生成**：将 USD 中的 Mesh、材质、骨骼动画等自动转换为 UE 原生资产（`UStaticMesh`、`UMaterial`、`UAnimSequence` 等）
- **双向同步**：通过 USD Notice 监听机制实现 USD Stage 变更到 UE 的实时同步，支持 Undo/Redo
- **Sequencer 集成**：自动将 USD 动画数据转换为 `ULevelSequence`，并支持通过 Dynamic Binding 与 Sequencer 联动
- **USD 导出**：`USDExporter` 模块支持将 UE 资产反向导出为 USD 格式

该插件默认未启用且标记为 Beta，说明它仍在积极开发中。它尤其适用于需要在影视管线（如 VFX）与 UE 实时渲染之间进行资产交换的场景。

## 使用场景

- 你在做影视虚拟制片项目，需要从 Houdini/Maya 等 DCC 工具导入 USD 场景 → 将 USD 文件拖入关卡或通过 `AUsdStageActor` 加载
- 你需要在 Sequencer 中控制 USD 资产的动画和可见性 → 自动生成的 LevelSequence 会包含所有动画轨道
- 你需要精确控制 USD 加载行为（如按 Kind 折叠、合并材质槽、Nanite 阈值等） → 通过 `AUsdStageActor` 的配置属性调整
- 你希望在 USD 和 UE 之间进行双向资产交换 → 使用 USDExporter 模块导出
- 你需要在 USD Stage Editor 中交互式地浏览和编辑 USD Prim 层级 → 启用 `USDStageEditor` 模块

## 子模块概览

本插件包含 9 个运行时模块，按功能可分为以下几组：

| 模块 | 职责 |
|---|---|
| **USDSchemas** | USD Schema 到 UE 类型的翻译框架 |
| **USDStage** | 核心 Stage Actor、Prim 映射、动画集成 |
| **USDStageImporter** | USD 文件导入管线 |
| **USDStageEditor** | USD Stage 编辑器面板（UI） |
| **USDStageEditorViewModels** | 编辑器面板的 ViewModel 层 |
| **USDClassesEditor** | 编辑器辅助类 |
| **USDExporter** | UE 到 USD 的导出功能 |
| **GeometryCacheUSD** | USD GeometryCache 支持 |
| **USDTests** | 自动化测试 |

## 蓝图用法

以下 BlueprintCallable 函数来自 `AUsdStageActor`，按功能分组。

### 核心节点

#### Stage 管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetRootLayer` | 设置 USD 文件路径并打开 Stage | `AUsdStageActor` |
| `SetStageState` | 控制 Stage 状态（关闭/打开/打开并加载） | `AUsdStageActor` |
| `NewStage` | 创建一个全新的内存 Stage | `AUsdStageActor` |
| `SetIsolatedRootLayer` | 进入/退出隔离模式，只显示指定子层 | `AUsdStageActor` |
| `GetIsolatedRootLayer` | 获取当前隔离层标识 | `AUsdStageActor` |

#### 加载与网格设置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetInitialLoadSet` | 设置初始加载集合（LoadAll / LoadNone 等） | `AUsdStageActor` |
| `SetInterpolationType` | 设置动画插值类型 | `AUsdStageActor` |
| `SetPurposesToLoad` | 按 Purpose 过滤加载哪些 Prim | `AUsdStageActor` |
| `SetUsePrimKindsForCollapsing` | 是否按 Kind 自动折叠子树 | `AUsdStageActor` |
| `SetKindsToCollapse` | 指定哪些 Kind 需要折叠 | `AUsdStageActor` |
| `SetMergeIdenticalMaterialSlots` | 折叠时是否合并相同材质槽 | `AUsdStageActor` |
| `SetShareAssetsForIdenticalPrims` | 相同 Prim 是否共享生成的资产 | `AUsdStageActor` |
| `SetNaniteTriangleThreshold` | 超过此三角形数的 Mesh 自动启用 Nanite | `AUsdStageActor` |
| `SetSubdivisionLevel` | 设置细分级别（0 = 不细分） | `AUsdStageActor` |
| `SetFallbackCollisionType` | 无物理 Schema 的 Mesh 的默认碰撞类型 | `AUsdStageActor` |
| `SetGeometryCacheImport` | GeometryCache 导入选项 | `AUsdStageActor` |

#### 材质设置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetRenderContext` | 设置材质解析使用的渲染上下文 | `AUsdStageActor` |
| `SetMaterialPurpose` | 设置材质绑定解析的 Purpose | `AUsdStageActor` |

#### 动画设置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetRootMotionHandling` | 根骨骼运动处理策略 | `AUsdStageActor` |
| `GetTime` | 获取当前 USD 时间码 | `AUsdStageActor` |
| `SetTime` | 设置 USD 时间码（驱动动画） | `AUsdStageActor` |
| `GetLevelSequence` | 获取自动生成的 LevelSequence | `AUsdStageActor` |

#### 元数据设置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCollectMetadata` | 是否收集 USD Prim 元数据 | `AUsdStageActor` |
| `SetCollectFromEntireSubtrees` | 是否从整个子树收集元数据 | `AUsdStageActor` |
| `SetCollectOnComponents` | 是否将元数据附加到组件上 | `AUsdStageActor` |
| `SetBlockedPrefixFilters` | 元数据前缀过滤器 | `AUsdStageActor` |
| `SetInvertFilters` | 是否反转过滤器 | `AUsdStageActor` |

#### 查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetGeneratedComponent` | 根据 Prim 路径获取生成的组件 | `AUsdStageActor` |
| `GetGeneratedAssets` | 根据 Prim 路径获取生成的资产列表 | `AUsdStageActor` |
| `GetSourcePrimPath` | 根据 UObject 反查源 Prim 路径 | `AUsdStageActor` |
| `SetUsdAssetCache` | 设置资产缓存对象 | `AUsdStageActor` |

#### Sequencer 动态绑定

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ResolveWithStageActor` | 解析 Sequencer 动态绑定到 USD Stage Actor 生成的 Actor/Component | `UUsdDynamicBindingResolverLibrary` |

### 使用示例（蓝图描述）

**加载 USD 文件并配置选项：**

1. 在关卡中放置一个 `AUsdStageActor`
2. 在细节面板中设置 `RootLayer` 为 `.usd`/`.usda`/`.usdc` 文件路径
3. 设置 `StageState` 为 `OpenedAndLoaded` 触发加载
4. 调整 `InitialLoadSet`（通常为 `LoadAll`）
5. 如需按 Kind 折叠，启用 `bUsePrimKindsForCollapsing` 并设置 `KindsToCollapse` 位掩码
6. 设置 `NaniteTriangleThreshold` 为合适的值以优化大型网格性能

**通过蓝图动态加载：**

1. 创建 `AUsdStageActor` 的 Spawn Actor 节点
2. 连接 `SetRootLayer` 节点，传入文件路径字符串
3. 连接 `SetStageState` 节点，设为 `OpenedAndLoaded`
4. 使用 `GetGeneratedComponent` 查询特定 Prim（如 `"/root/my_mesh"`）生成的组件
5. 使用 `GetGeneratedAssets` 获取该 Prim 生成的 `UStaticMesh` 等资产引用

**通过 Sequencer Dynamic Binding 绑定 USD 动画：**

1. 在 Sequencer 中对绑定使用 `ResolveWithStageActor` 节点
2. 指定 `StageActorIDNameFilter` 或 `RootLayerFilter` 定位到特定 Stage Actor
3. 设置 `PrimPath` 为目标 Prim 的完整路径（如 `"/root/character"`）
4. 返回的 UObject 将是该 Prim 对应的 Actor 或 Component

## C++ 用法

### 头文件引入

```cpp
// USDStage 模块
#include "USDStageActor.h"
#include "USDStageModule.h"

// LevelSequence 集成
#include "USDLevelSequenceHelper.h"

// Prim 映射
#include "USDPrimTwin.h"

// Sequencer 动态绑定
#include "USDDynamicBindingResolverLibrary.h"
```

### 基本用法

```cpp
// 获取或创建 USD Stage Actor
// 来源: Public/USDStageModule.h
IUsdStageModule& StageModule = FModuleManager::Get().LoadModuleChecked<IUsdStageModule>("USDStage");
AUsdStageActor& StageActor = StageModule.GetUsdStageActor(GetWorld());

// 设置 USD 文件路径并打开 Stage
StageActor.SetRootLayer(TEXT("/Game/USD/MyScene.usd"));

// 配置加载选项
StageActor.SetInitialLoadSet(EUsdInitialLoadSet::LoadAll);
StageActor.SetInterpolationType(EUsdInterpolationType::Linear);
StageActor.SetPurposesToLoad(static_cast<int32>(EUsdPurpose::Default) | static_cast<int32>(EUsdPurpose::Proxy));

// 设置 Nanite 阈值 — 超过 10000 三角形的 Mesh 启用 Nanite
StageActor.SetNaniteTriangleThreshold(10000);

// 打开并加载 Stage
StageActor.SetStageState(EUsdStageState::OpenedAndLoaded);
```

### 查询生成的组件和资产

```cpp
// 来源: Public/USDStageActor.h

// 根据 Prim 路径查询生成的组件
USceneComponent* MeshComponent = StageActor.GetGeneratedComponent(TEXT("/root/scene/my_mesh"));
if (MeshComponent)
{
    // 组件的生命周期由 StageActor 管理，可能在关闭 Stage 时被销毁
    MeshComponent->SetVisibility(false);
}

// 根据 Prim 路径查询生成的资产（可能是多个，如 SkeletalMesh + Skeleton）
TArray<UObject*> Assets = StageActor.GetGeneratedAssets(TEXT("/root/scene/my_mesh"));
for (UObject* Asset : Assets)
{
    UE_LOG(LogTemp, Log, TEXT("Generated asset: %s"), *Asset->GetName());
}

// 反向查询：从 UObject 获取源 Prim 路径
FString PrimPath = StageActor.GetSourcePrimPath(MeshComponent);
// 返回 "/root/scene/my_mesh"
```

### 动画时间控制

```cpp
// 来源: Public/USDStageActor.h

// 获取 LevelSequence
ULevelSequence* Sequence = StageActor.GetLevelSequence();

// 设置时间码来驱动动画
StageActor.SetTime(24.0f);  // 跳转到第 24 帧
float CurrentTime = StageActor.GetTime();
```

### 监听 Stage 变更事件

```cpp
// 来源: Public/USDStageActor.h 中的事件声明

// 监听 Stage 打开/关闭
StageActor.OnStageLoaded.AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("USD Stage loaded"));
});

StageActor.OnStageUnloaded.AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("USD Stage unloaded"));
});

// 监听 Prim 变更
StageActor.OnPrimChanged.AddLambda([](const FString& PrimPath, bool bResync)
{
    UE_LOG(LogTemp, Log, TEXT("Prim changed: %s (resync: %s)"), *PrimPath, bResync ? TEXT("true") : TEXT("false"));
});

// 监听时间变化（用于 Sequencer 集成）
StageActor.OnTimeChanged.AddLambda([]()
{
    // 动画时间更新回调
});

// 静态事件 — 监听任意 Stage Actor 加载完成
AUsdStageActor::FOnActorLoaded& OnLoaded = AUsdStageActor::OnActorLoaded;
OnLoaded.AddLambda([](AUsdStageActor* LoadedActor)
{
    UE_LOG(LogTemp, Log, TEXT("Stage Actor loaded: %s"), *LoadedActor->GetName());
});
```

### C++ 进阶用法

```cpp
// 隔离模式：只显示某个子层
// 来源: Public/USDStageActor.h
StageActor.SetIsolatedRootLayer(TEXT("/path/to/sublayer.usda"));
FString CurrentIsolated = StageActor.GetIsolatedRootLayer();
// 传入空字符串退出隔离模式
StageActor.SetIsolatedRootLayer(TEXT(""));

// 获取底层 USD Stage（需要 UnrealUSDWrapper）
// 来源: Public/USDStageActor.h
UE::FUsdStage& Stage = StageActor.GetOrOpenUsdStage();
UE::FUsdStage& BaseStage = StageActor.GetBaseUsdStage();

// 获取边界框缓存
TSharedPtr<UE::FUsdGeomBBoxCache> BBoxCache = StageActor.GetBBoxCache();

// 控制 USD Notice 监听（写入 Stage 时暂停监听避免循环）
StageActor.StopListeningToUsdNotices();
// ... 执行写入操作 ...
StageActor.ResumeListeningToUsdNotices();

// 控制 LevelSequence 监控（修改 Sequencer 时暂停回写 USD）
StageActor.StopMonitoringLevelSequence();
// ... 执行 Sequencer 操作 ...
StageActor.ResumeMonitoringLevelSequence();
```

## Demo 示例

以下示例展示如何通过 C++ 创建一个自定义的 USD 加载管理器：

```cpp
// MyUSDSceneManager.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyUSDSceneManager.generated.h"

class AUsdStageActor;

UCLASS(BlueprintType, Blueprintable)
class YOURPROJECT_API AMyUSDSceneManager : public AActor
{
    GENERATED_BODY()

public:
    AMyUSDSceneManager();

    UPROPERTY(EditAnywhere, Category = "USD")
    FString USDFilePath;

    UPROPERTY(EditAnywhere, Category = "USD", meta = (ClampMin = "0"))
    int32 NaniteTriangleThreshold = 10000;

    UPROPERTY(EditAnywhere, Category = "USD")
    bool bAutoLoadOnBeginPlay = true;

    UFUNCTION(BlueprintCallable, Category = "USD")
    void LoadUSDStage();

    UFUNCTION(BlueprintCallable, Category = "USD")
    void QueryPrimAssets(const FString& PrimPath, TArray<UObject*>& OutAssets);

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY()
    TObjectPtr<AUsdStageActor> ManagedStageActor;

    FDelegateHandle OnStageLoadedHandle;
};
```

```cpp
// MyUSDSceneManager.cpp
#include "MyUSDSceneManager.h"
#include "USDStageActor.h"
#include "USDStageModule.h"

AMyUSDSceneManager::AMyUSDSceneManager()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyUSDSceneManager::BeginPlay()
{
    Super::BeginPlay();

    if (bAutoLoadOnBeginPlay && !USDFilePath.IsEmpty())
    {
        LoadUSDStage();
    }
}

void AMyUSDSceneManager::LoadUSDStage()
{
    if (USDFilePath.IsEmpty())
    {
        UE_LOG(LogTemp, Warning, TEXT("AMyUSDSceneManager: USDFilePath is empty"));
        return;
    }

    // 获取 USDStage 模块
    IUsdStageModule* StageModule = FModuleManager::Get().GetModulePtr<IUsdStageModule>("USDStage");
    if (!StageModule)
    {
        UE_LOG(LogTemp, Error, TEXT("AMyUSDSceneManager: USDStage module not loaded"));
        return;
    }

    // 获取或创建 Stage Actor
    ManagedStageActor = &StageModule->GetUsdStageActor(GetWorld());

    // 配置加载选项
    ManagedStageActor->SetNaniteTriangleThreshold(NaniteTriangleThreshold);
    ManagedStageActor->SetUsePrimKindsForCollapsing(true);
    ManagedStageActor->SetMergeIdenticalMaterialSlots(true);

    // 监听加载完成
    OnStageLoadedHandle = ManagedStageActor->OnStageLoaded.AddLambda([this]()
    {
        UE_LOG(LogTemp, Log, TEXT("USD Stage loaded successfully from: %s"), *USDFilePath);

        // 获取自动生成的 LevelSequence
        ULevelSequence* Sequence = ManagedStageActor->GetLevelSequence();
        if (Sequence)
        {
            UE_LOG(LogTemp, Log, TEXT("Level sequence generated: %s"), *Sequence->GetName());
        }
    });

    // 设置路径并加载
    ManagedStageActor->SetRootLayer(USDFilePath);
}

void AMyUSDSceneManager::QueryPrimAssets(const FString& PrimPath, TArray<UObject*>& OutAssets)
{
    if (!ManagedStageActor)
    {
        return;
    }

    OutAssets = ManagedStageActor->GetGeneratedAssets(PrimPath);

    // 也可以查询组件
    USceneComponent* Comp = ManagedStageActor->GetGeneratedComponent(PrimPath);
    if (Comp)
    {
        UE_LOG(LogTemp, Log, TEXT("Prim %s -> Component: %s"), *PrimPath, *Comp->GetName());
    }
}

void AMyUSDSceneManager::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (ManagedStageActor)
    {
        ManagedStageActor->OnStageLoaded.Remove(OnStageLoadedHandle);
        ManagedStageActor = nullptr;
    }

    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

> ⚠️ Build.cs 源文件未提供，以下依赖从头文件代码引用推断。

| 模块 | 用途 |
|---|---|
| `UnrealUSDWrapper` | USD 底层 C++ 绑定（PXR/USD 运行时） |
| `LevelSequence` | LevelSequence 资产和轨道支持 |
| `MovieScene` | Sequencer 序列框架（Dynamic Binding） |
| `UniversalObjectLocator` | Sequencer 对象定位器框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译警告 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 新增支持分配不依赖蓝图的 Control Rig |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD validation changes | 解决 UE 更新导致 LOD 验证变更时 AnimQuery 内部引用失效 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符与参数不匹配问题 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 支持烘焙曝光动画轨道的所有帧 |

### 维护评价

- **状态**：🟢 活跃维护中
- **创建时间**：2018 年（从 Experimental 目录迁移），约 8 年历史
- **最近更新**：2026 年 5 月仍有功能更新和 bug 修复，更新频率较高（近一个月 5 次提交）
- **Beta 标记**：仍标记为 Beta 版本（`IsBetaVersion: true`），默认未启用
- **已知限制**：
  - 需要手动在插件设置中启用（`EnabledByDefault: false`）
  - 依赖 UnrealUSDWrapper 和外部 USD 运行时库
  - 部分 API 已标记废弃（如 `UUsdAssetCache2` → `UUsdAssetCache3`）
- **推荐度**：✅ 推荐使用。该插件是 Epic 官方维护的 USD 集成方案，持续更新中，适合作为影视虚拟制片和 DCC-UE 资产交换的基础方案。尽管仍标记 Beta，但已经具备完整的 Stage 管理、资产生成、动画集成和 Sequencer 支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档]()（未提供）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)