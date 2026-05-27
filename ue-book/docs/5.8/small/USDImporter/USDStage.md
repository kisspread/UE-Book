# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

USDImporter 是 Unreal Engine 的 Pixar USD (Universal Scene Description) 格式全流程支持插件。它不仅提供 USD 文件的导入功能，还包含完整的 USD Stage 运行时管理、动画序列生成、材质解析、几何缓存、以及反向导出能力。

**核心解决的问题**：USD 是影视和工业领域的标准场景描述格式，支持分层编辑、变体、引用等高级特性。本插件在 UE 中实现了一个"USD Stage Actor"——一个特殊的 Actor，能够以交互方式打开 USD Stage、实时解析 Prim 层级、生成对应的组件和资产，并通过 Sequencer 驱动动画。这使得 UE 可以直接作为 USD 管线的一部分，而不仅仅是静态导入资产。

**为什么默认未启用且标记为实验性**：该插件依赖 Pixar 的 OpenUSD 库，编译配置特殊（需要 ENABLE_USD_INTEROP 宏），且 API 仍在演进中（可见源码中大量 `UE_DEPRECATED` 标记和 `AssetCache2` → `AssetCache3` 的迁移）。

## 使用场景

- 你有一个从 Maya/Houdini/Katana 导出的 USD 文件，需要在 UE 中实时查看和编辑 → 放置 `AUsdStageActor` 并设置 `RootLayer`
- 你需要将 USD 动画（骨骼、变换、可见性）导入为 UE 的 LevelSequence → 开启 Stage 后自动生成 Sequencer 轨道
- 你需要将 UE 中的资产导出为 USD 格式供下游 DCC 使用 → 使用 `USDExporter` 模块
- 你正在构建虚拟制片管线，需要 USD 的分层和变体功能 → `AUsdStageActor` 支持隔离子图层（Isolated Layer）
- 你需要 Nanite 支持大三角形数的 USD 网格体 → 设置 `NaniteTriangleThreshold`

## 蓝图用法

所有蓝图可调用函数均定义在 `AUsdStageActor` 上，分类为 `"USD"`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetRootLayer` | 设置 USD 文件路径并打开 Stage | `AUsdStageActor` |
| `SetStageState` | 控制 Stage 状态（关闭/打开/打开并加载） | `AUsdStageActor` |
| `SetUsdAssetCache` | 设置新版资产缓存（UUsdAssetCache3） | `AUsdStageActor` |
| `SetInitialLoadSet` | 设置初始加载集合（LoadAll / LoadNone 等） | `AUsdStageActor` |
| `SetInterpolationType` | 设置动画插值类型 | `AUsdStageActor` |
| `SetTime` | 设置当前 USD Stage 的求值时间码 | `AUsdStageActor` |
| `GetTime` | 获取当前 USD Stage 的求值时间码 | `AUsdStageActor` |
| `GetGeneratedComponent` | 根据 Prim 路径获取生成的场景组件 | `AUsdStageActor` |
| `GetGeneratedAssets` | 根据 Prim 路径获取生成的资产（StaticMesh 等） | `AUsdStageActor` |
| `GetSourcePrimPath` | 根据 UObject 反查其来源 Prim 路径 | `AUsdStageActor` |
| `GetLevelSequence` | 获取当前生成的 LevelSequence 资产 | `AUsdStageActor` |
| `NewStage` | 创建全新的内存 USD Stage 并打开 | `AUsdStageActor` |
| `SetIsolatedRootLayer` | 进入/退出子图层隔离模式 | `AUsdStageActor` |

### 材质与渲染设置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetRenderContext` | 设置 USD 材质解析使用的着色器上下文 | `AUsdStageActor` |
| `SetMaterialPurpose` | 设置材质绑定时的材质用途过滤 | `AUsdStageActor` |
| `SetMergeIdenticalMaterialSlots` | 合并相同材质插槽 | `AUsdStageActor` |
| `SetShareAssetsForIdenticalPrims` | 为相同 Prim 共享生成的资产 | `AUsdStageActor` |

### 折叠与优化

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetUsePrimKindsForCollapsing` | 启用/禁用基于 Kind 的 Prim 折叠 | `AUsdStageActor` |
| `SetKindsToCollapse` | 设置要折叠的 Kind 位掩码 | `AUsdStageActor` |
| `SetPurposesToLoad` | 设置要加载的 Purpose 位掩码 | `AUsdStageActor` |
| `SetNaniteTriangleThreshold` | Nanite 自动启用的三角形阈值 | `AUsdStageActor` |
| `SetSubdivisionLevel` | 设置细分级别（0=不细分） | `AUsdStageActor` |

### 元数据采集

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCollectMetadata` | 启用/禁用 Prim 元数据采集 | `AUsdStageActor` |
| `SetCollectFromEntireSubtrees` | 从整个子树采集元数据 | `AUsdStageActor` |
| `SetCollectOnComponents` | 将元数据挂载到组件上 | `AUsdStageActor` |
| `SetBlockedPrefixFilters` | 设置元数据前缀过滤列表 | `AUsdStageActor` |
| `SetInvertFilters` | 反转前缀过滤逻辑 | `AUsdStageActor` |

### 动态绑定解析

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ResolveWithStageActor` | 为 Sequencer 动态绑定解析 Actor/组件 | `UUsdDynamicBindingResolverLibrary` |

### 使用示例（蓝图描述）

**基本导入流程**：
1. 在关卡中放置 `AUsdStageActor`（搜索 "USD Stage Actor"）
2. 在 Details 面板设置 `RootLayer` 为 `.usd` / `.usda` / `.usdc` 文件路径
3. 将 `StageState` 设为 `OpenedAndLoaded`，Stage 会自动解析并生成组件和资产
4. 如需动画，调用 `GetLevelSequence` 获取自动生成的 LevelSequence，放入 Sequencer 播放

**蓝图动态控制**：
1. 获取场景中的 `AUsdStageActor` 引用
2. 调用 `SetTime(float)` 设置时间码以求值特定帧
3. 调用 `GetGeneratedComponent(FString)` 按 Prim 路径获取组件，进行变换或材质替换
4. 调用 `GetGeneratedAssets(FString)` 获取生成的 UStaticMesh 等资产

## C++ 用法

### 头文件引入

```cpp
#include "USDStageActor.h"
#include "USDStageModule.h"
```

### 基本用法

获取 USD Stage Actor 并打开 Stage：

```cpp
// 来源: Public/USDStageModule.h, Public/USDStageActor.h
#include "USDStageModule.h"
#include "USDStageActor.h"
#include "Modules/ModuleManager.h"

void OpenUsdFile(UWorld* World, const FString& UsdFilePath)
{
    // 获取 USD Stage 模块
    IUsdStageModule& UsdStageModule = FModuleManager::GetModuleChecked<IUsdStageModule>("USDStage");

    // 获取或查找 USD Stage Actor
    AUsdStageActor& StageActor = UsdStageModule.GetUsdStageActor(World);

    // 设置 USD 文件路径
    StageActor.SetRootLayer(UsdFilePath);

    // Stage 会自动打开并加载资产
    // 如果需要手动控制状态：
    StageActor.SetStageState(EUsdStageState::OpenedAndLoaded);
}
```

### 查询生成的组件和资产

```cpp
// 来源: Public/USDStageActor.h
void QueryGeneratedObjects(AUsdStageActor& StageActor)
{
    // 根据 Prim 路径获取生成的组件
    // 注意: 组件生命周期由 StageActor 管理，随时可能被销毁
    USceneComponent* Component = StageActor.GetGeneratedComponent(TEXT("/root_prim/my_mesh"));
    if (Component)
    {
        // 对组件进行操作...
    }

    // 获取生成的资产（可能有多个，如 SkeletalMesh + Skeleton）
    TArray<UObject*> Assets = StageActor.GetGeneratedAssets(TEXT("/root_prim/my_mesh"));
    for (UObject* Asset : Assets)
    {
        if (UStaticMesh* StaticMesh = Cast<UStaticMesh>(Asset))
        {
            // 处理 StaticMesh...
        }
    }

    // 反向查询：从 UObject 找到来源 Prim 路径
    FString PrimPath = StageActor.GetSourcePrimPath(Component);
    // PrimPath == "/root_prim/my_mesh"
}
```

### 动画与时间控制

```cpp
// 来源: Public/USDStageActor.h
void AnimateUsdStage(AUsdStageActor& StageActor)
{
    // 获取当前时间
    float CurrentTime = StageActor.GetTime();

    // 设置时间码以求值特定帧
    StageActor.SetTime(30.0f);

    // 获取自动生成的 LevelSequence
    ULevelSequence* LevelSeq = StageActor.GetLevelSequence();
    if (LevelSeq)
    {
        // 将 LevelSequence 添加到 Sequencer 播放...
    }
}
```

### 事件监听

```cpp
// 来源: Public/USDStageActor.h - 事件委托声明
void BindToStageEvents(AUsdStageActor& StageActor)
{
    // Stage 加载完成
    StageActor.OnStageLoaded.AddLambda([]()
    {
        UE_LOG(LogTemp, Log, TEXT("USD Stage loaded"));
    });

    // Stage 变化（属性修改等）
    StageActor.OnStageChanged.AddLambda([]()
    {
        UE_LOG(LogTemp, Log, TEXT("USD Stage changed"));
    });

    // 单个 Prim 变化
    StageActor.OnPrimChanged.AddLambda([](const FString& PrimPath, bool bResync)
    {
        UE_LOG(LogTemp, Log, TEXT("Prim %s changed (resync: %s)"),
            *PrimPath, bResync ? TEXT("true") : TEXT("false"));
    });

    // 时间变化
    StageActor.OnTimeChanged.AddLambda([]()
    {
        // 时间码变化时的回调
    });

    // 静态事件：任意 StageActor 加载时
    AUsdStageActor::OnActorLoaded.AddLambda([](AUsdStageActor* Actor)
    {
        UE_LOG(LogTemp, Log, TEXT("Stage Actor loaded: %s"), *Actor->GetName());
    });
}
```

### 隔离子图层

```cpp
// 来源: Public/USDStageActor.h
void IsolateSublayer(AUsdStageActor& StageActor, const FString& SublayerIdentifier)
{
    // 进入隔离模式：只显示指定子图层的内容
    StageActor.SetIsolatedRootLayer(SublayerIdentifier);

    // 检查当前是否处于隔离模式
    FString IsolatedLayer = StageActor.GetIsolatedRootLayer();
    if (!IsolatedLayer.IsEmpty())
    {
        UE_LOG(LogTemp, Log, TEXT("Currently isolating layer: %s"), *IsolatedLayer);
    }

    // 退出隔离模式
    StageActor.SetIsolatedRootLayer(TEXT(""));
}
```

### 进阶用法

直接操作底层 USD Stage 对象：

```cpp
// 来源: Public/USDStageActor.h
void AdvancedStageAccess(AUsdStageActor& StageActor)
{
    // 获取或打开 USD Stage
    UE::FUsdStage& UsdStage = StageActor.GetOrOpenUsdStage();

    // 获取边界框缓存
    TSharedPtr<UE::FUsdGeomBBoxCache> BBoxCache = StageActor.GetBBoxCache();

    // 获取材质到 Primvar 到 UV 通道的映射
    TMap<FString, TMap<FString, int32>> MatPrimvarUV = StageActor.GetMaterialToPrimvarToUVIndex();

    // 获取 BlendShape 映射
    const UsdUtils::FBlendShapeMap& BlendShapes = StageActor.GetBlendShapeMap();

    // 获取 USD 监听器
    FUsdListener& Listener = StageActor.GetUsdListener();

    // 临时暂停 USD 通知响应（在向 Stage 写入数据时使用）
    StageActor.StopListeningToUsdNotices();
    // ... 执行写入操作 ...
    StageActor.ResumeListeningToUsdNotices();

    // 控制 LevelSequence 监控
    StageActor.StopMonitoringLevelSequence();
    // ... 修改 LevelSequence 但不想回写到 USD ...
    StageActor.ResumeMonitoringLevelSequence();
}
```

### LevelSequence Helper 直接使用

```cpp
// 来源: Public/USDLevelSequenceHelper.h
#include "USDLevelSequenceHelper.h"

void UseLevelSequenceHelper()
{
    FUsdLevelSequenceHelper Helper;

    // 从 USD Stage 初始化 LevelSequence
    ULevelSequence* MainSeq = Helper.Init(UsdStage);

    // 获取主序列和子序列
    ULevelSequence* Main = Helper.GetMainLevelSequence();
    TArray<ULevelSequence*> Subs = Helper.GetSubSequences();

    // 设置边界框缓存（导入时使用，此时没有 StageActor）
    Helper.SetBBoxCache(BBoxCache);

    // 设置根运动处理策略
    Helper.SetRootMotionHandling(EUsdRootMotionHandling::NoRootMotion);

    // 绑定到 StageActor
    Helper.BindToUsdStageActor(StageActor);

    // 控制变更监控
    Helper.StartMonitoringChanges();
    // ... 执行可能触发变更通知的操作 ...
    Helper.StopMonitoringChanges();
}
```

## Demo 示例

### 完整的 USD Stage Actor 使用示例

```cpp
// UsdDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "UsdDemoActor.generated.h"

class AUsdStageActor;

UCLASS()
class AUsdDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AUsdDemoActor();

    /** 要加载的 USD 文件路径 */
    UPROPERTY(EditAnywhere, Category = "USD Demo")
    FFilePath UsdFile;

    /** 是否自动播放动画 */
    UPROPERTY(EditAnywhere, Category = "USD Demo")
    bool bAutoPlay = true;

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "USD Demo")
    void LoadAndAnimate();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY()
    TObjectPtr<AUsdStageActor> StageActor;

    UPROPERTY()
    FDelegateHandle OnLoadedHandle;

    float AnimationTime = 0.0f;

    void OnStageLoaded(AUsdStageActor* LoadedActor);
    void QueryPrimInfo(const FString& PrimPath);
};
```

```cpp
// UsdDemoActor.cpp
#include "UsdDemoActor.h"
#include "USDStageActor.h"
#include "USDStageModule.h"
#include "Modules/ModuleManager.h"

AUsdDemoActor::AUsdDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AUsdDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 监听任意 StageActor 加载事件
    OnLoadedHandle = AUsdStageActor::OnActorLoaded.AddUObject(
        this, &AUsdDemoActor::OnStageLoaded);

    if (!UsdFile.FilePath.IsEmpty())
    {
        LoadAndAnimate();
    }
}

void AUsdDemoActor::LoadAndAnimate()
{
    if (UsdFile.FilePath.IsEmpty())
    {
        UE_LOG(LogTemp, Warning, TEXT("USD 文件路径未设置"));
        return;
    }

    // 获取 USD Stage 模块
    IUsdStageModule* UsdStageModule = FModuleManager::GetModulePtr<IUsdStageModule>("USDStage");
    if (!UsdStageModule)
    {
        UE_LOG(LogTemp, Error, TEXT("USDStage 模块未加载，请确认插件已启用"));
        return;
    }

    // 获取 Stage Actor 并设置文件
    StageActor = &UsdStageModule->GetUsdStageActor(GetWorld());
    StageActor->SetRootLayer(UsdFile.FilePath);

    // 配置导入选项
    StageActor->SetInitialLoadSet(EUsdInitialLoadSet::LoadAll);
    StageActor->SetNaniteTriangleThreshold(100000);
    StageActor->SetUsePrimKindsForCollapsing(true);
    StageActor->SetPurposesToLoad(
        static_cast<int32>(EUsdPurpose::Default) |
        static_cast<int32>(EUsdPurpose::Proxy)
    );

    UE_LOG(LogTemp, Log, TEXT("USD Stage 加载中: %s"), *UsdFile.FilePath);
}

void AUsdDemoActor::OnStageLoaded(AUsdStageActor* LoadedActor)
{
    if (LoadedActor != StageActor)
    {
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("USD Stage 加载完成"));

    // 查询一些已生成的组件
    QueryPrimInfo(TEXT("/root"));

    // 获取 LevelSequence
    ULevelSequence* LevelSeq = StageActor->GetLevelSequence();
    if (LevelSeq)
    {
        UE_LOG(LogTemp, Log, TEXT("已生成 LevelSequence: %s"), *LevelSeq->GetName());
    }
}

void AUsdDemoActor::QueryPrimInfo(const FString& PrimPath)
{
    if (!StageActor) return;

    USceneComponent* Comp = StageActor->GetGeneratedComponent(PrimPath);
    if (Comp)
    {
        UE_LOG(LogTemp, Log, TEXT("Prim %s 对应组件: %s"),
            *PrimPath, *Comp->GetName());
    }

    TArray<UObject*> Assets = StageActor->GetGeneratedAssets(PrimPath);
    for (UObject* Asset : Assets)
    {
        UE_LOG(LogTemp, Log, TEXT("Prim %s 对应资产: %s (%s)"),
            *PrimPath, *Asset->GetName(), *Asset->GetClass()->GetName());
    }
}

void AUsdDemoActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (bAutoPlay && StageActor)
    {
        AnimationTime += DeltaTime * 24.0f; // 假设 24fps
        StageActor->SetTime(AnimationTime);
    }
}
```

## 模块依赖

由于 USDImporter 包含 9 个模块且依赖关系复杂，以下是各模块的独特依赖概要：

| 模块 | 用途 |
|---|---|
| `UnrealUSDWrapper` | UE 封装的 OpenUSD C++ 库（提供 `UE::FUsdStage`、`UE::FSdfLayer` 等类型） |
| `USDClasses` | USD 通用资产类型定义（`UUsdAssetCache3` 等） |
| `SequencerScripting` | LevelSequence 集成支持 |
| `UniversalObjectLocator` | USD Prim 定位器框架 |
| `LevelSequence` | LevelSequence 资产和轨道系统 |
| `GeometryCache` | GeometryCache 资产支持（用于 USD 网格动画） |

> 注：UnrealUSDWrapper 是本插件最核心的依赖，提供所有 USD C++ API 的 UE 封装。使用者的模块通常只需依赖 `USDStage`（运行时）或 `USDStageEditor`（编辑器时）即可。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 新增独立于蓝图的 Control Rig 分配支持 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD values change. | 修复 USD 26.03 更新导致 LOD 值变化时 AnimQuery 内部引用失效的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 烘焙曝光动画轨道的所有帧 |

### 维护评价

- **创建时间**：2018 年 11 月，已维护约 7 年
- **活跃度**：**非常活跃**。2026 年仍有持续的功能性更新（Control Rig 集成、USD 26.03 兼容性修复等）
- **API 稳定性**：中等。可见 `UUsdAssetCache2` → `UUsdAssetCache3` 的迁移，多个属性和函数标记为 `UE_DEPRECATED`
- **实验性状态**：仍标记为 `IsBetaVersion = true` 且 `EnabledByDefault = false`，但已广泛用于生产环境（虚拟制片、建筑可视化等）
- **推荐使用**：✅ 推荐。对于需要 USD 管线集成的项目，这是 UE 官方提供的标准方案。注意默认未启用，需在插件设置中手动激活。虽然仍为实验性状态，但代码质量高、维护活跃、功能完整。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)