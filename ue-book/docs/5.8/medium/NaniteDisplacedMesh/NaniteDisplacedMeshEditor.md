# Nanite Displaced Mesh

> Asset and component types that provide a basic pre-displacement pipeline for Nanite meshes

| 属性 | 值 |
|---|---|
| 中文名 | Nanite 置换网格 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（置换网格资产类型） |
| 模块 | `NaniteDisplacedMesh` (Runtime), `NaniteDisplacedMeshEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-05-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NaniteDisplacedMesh) | |

## 用途

Nanite 置换网格插件为 Nanite 虚拟几何体系统提供了一套**离线预置换（Pre-Displacement）管线**。在 Nanite 的渲染流程中，原始静态网格（Static Mesh）经过置换（Displacement）后生成新的网格资产（`UNaniteDisplacedMesh`），这些置换后的网格可以直接用于渲染，而无需在运行时动态计算置换。

该插件解决的核心问题是：**如何将置换效果烘焙到 Nanite 网格中，使其在编辑器和运行时都能高效使用**。它提供了一套完整的编辑器工具链，包括：
- 置换网格资产的创建和管理
- 基于源资产变更的自动重编译机制
- 批量处理的 Commandlet 工具
- 资产依赖关系追踪和自动更新

## 使用场景

- 你有一组使用 Nanite 的静态网格，需要应用置换贴图（Displacement Map）生成高质量地形或建筑细节
- 你需要在编辑器中修改源资产后，置换网格能自动更新
- 你需要批量更新关卡中所有使用置换网格的 Actor（通过 Commandlet）
- 你在开发需要 Nanite 置换功能的大型开放世界项目，需要自动化管线管理置换资产

## 蓝图用法

此插件主要面向 C++ 和编辑器工具链，**没有暴露 BlueprintCallable 函数**。所有操作均通过编辑器 UI（Details 面板）或 C++ API 完成。

### 编辑器用法

- 在 Content Browser 中右键创建 **Nanite Displaced Mesh** 资产
- 在资产的 Details 面板中配置置换参数
- 点击 **Apply** 按钮将参数应用到置换网格

## C++ 用法

### 头文件引入

```cpp
// 编辑器模块
#include "NaniteDisplacedMeshFactory.h"
#include "GeneratedNaniteDisplacedMeshEditorSubsystem.h"
```

### 基本用法：创建和关联置换网格资产

```cpp
// 来源: Public/NaniteDisplacedMeshFactory.h

#include "NaniteDisplacedMeshFactory.h"

// 创建一个新的 NaniteDisplacedMesh 资产
UClass* MeshClass = UNaniteDisplacedMesh::StaticClass();
UPackage* Package = CreatePackage(TEXT("/Game/MyDisplacedMesh"));
FName AssetName = TEXT("DM_MyAsset");

UNaniteDisplacedMesh* DisplacedMesh = UNaniteDisplacedMeshFactory::StaticFactoryCreateNew(
    MeshClass,
    Package,
    AssetName,
    RF_Public | RF_Standalone,
    nullptr,  // Context
    GWarn      // Feedback context
);

// 使用 LinkDisplacedMeshAsset 关联现有资产
FValidatedNaniteDisplacedMeshParams ValidatedParams;  // 填充置换参数
FNaniteDisplacedMeshLinkParameters LinkParams;
LinkParams.DisplacedMeshFolder = TEXT("/Game/DisplacedMeshes");
LinkParams.LinkDisplacedMeshAssetSetting = ELinkDisplacedMeshAssetSetting::LinkAgainstPersistentAsset;

UNaniteDisplacedMesh* LinkedMesh = LinkDisplacedMeshAsset(
    nullptr,             // ExistingDisplacedMesh（首次创建传 nullptr）
    MoveTemp(ValidatedParams),
    LinkParams
);
```

### 进阶用法：注册 Actor 类型的依赖追踪

```cpp
// 来源: Public/GeneratedNaniteDisplacedMeshEditorSubsystem.h

#include "GeneratedNaniteDisplacedMeshEditorSubsystem.h"

// 获取编辑器子系统
UGeneratedNaniteDisplacedMeshEditorSubsystem* Subsystem =
    GEditor->GetEditorSubsystem<UGeneratedNaniteDisplacedMeshEditorSubsystem>();

// 注册自定义 Actor 类型的依赖变化回调
UGeneratedNaniteDisplacedMeshEditorSubsystem::FActorClassHandler Handler;
Handler.Callback = [](AActor* ActorToUpdate, UObject* AssetChanged, FPropertyChangedEvent& Event)
{
    // 当依赖的资产发生变化时，自动触发置换网格的更新逻辑
    UE_LOG(LogTemp, Log, TEXT("Asset %s changed, updating actor %s"),
        *AssetChanged->GetName(), *ActorToUpdate->GetName());
};

// 可选：限制只监听特定资产类型的特定属性
TSet<FProperty*> WatchedProperties;
WatchedProperties.Add(FindFProperty<UNaniteDisplacedMesh>(
    GET_MEMBER_NAME_CHECKED(UNaniteDisplacedMesh, DisplacementParams)));
Handler.PropertiesToWatchPerAssetType.Add(UNaniteDisplacedMesh::StaticClass(), MoveTemp(WatchedProperties));

Subsystem->RegisterClassHandler(AMyDisplacedActor::StaticClass(), MoveTemp(Handler));

// 为特定 Actor 设置依赖追踪
TArray<TObjectKey<UObject>> Dependencies;
Dependencies.Add(SourceMesh);
Dependencies.Add(DisplacementTexture);
Subsystem->UpdateActorDependencies(MyActor, MoveTemp(Dependencies));

// Actor 销毁时移除追踪
Subsystem->RemoveActor(MyActor);
```

## Demo 示例

一个完整的最小示例，展示如何通过 C++ 创建和使用 NaniteDisplacedMesh 资产：

### DisplacedMeshDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "DisplacedMeshDemo.generated.h"

class UNaniteDisplacedMesh;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UDisplacedMeshDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Displaced Mesh")
    FSoftObjectPath SourceMeshPath;

    UPROPERTY(EditAnywhere, Category = "Displaced Mesh")
    FString OutputFolder = TEXT("/Game/DisplacedMeshes");

    /** 调用此函数生成置换网格 */
    UFUNCTION(CallInEditor, Category = "Displaced Mesh")
    void GenerateDisplacedMesh();
};
```

### DisplacedMeshDemo.cpp

```cpp
#include "DisplacedMeshDemo.h"
#include "NaniteDisplacedMeshFactory.h"

void UDisplacedMeshDemoComponent::GenerateDisplacedMesh()
{
    // 构建置换参数
    FValidatedNaniteDisplacedMeshParams ValidatedParams;
    ValidatedParams.SourceMesh = Cast<UStaticMesh>(SourceMeshPath.TryLoad());

    if (!ValidatedParams.SourceMesh)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load source mesh: %s"), *SourceMeshPath.ToString());
        return;
    }

    // 配置链接参数
    FNaniteDisplacedMeshLinkParameters LinkParams;
    LinkParams.DisplacedMeshFolder = OutputFolder;
    LinkParams.LinkDisplacedMeshAssetSetting = ELinkDisplacedMeshAssetSetting::LinkAgainstPersistentAsset;
    LinkParams.bForcePackageToBePublic = true;

    // 生成或更新置换网格
    bool bCreatedNew = false;
    LinkParams.bOutCreatedNewMesh = &bCreatedNew;

    UNaniteDisplacedMesh* Result = LinkDisplacedMeshAsset(
        nullptr,  // 首次创建
        MoveTemp(ValidatedParams),
        LinkParams
    );

    if (Result)
    {
        UE_LOG(LogTemp, Log, TEXT("Displaced mesh %s: %s"),
            bCreatedNew ? TEXT("created") : TEXT("updated"),
            *Result->GetPathName());
    }
}
```

## 模块依赖

### NaniteDisplacedMeshEditor（Editor 模块）

| 模块 | 用途 |
|---|---|
| `NaniteDisplacedMesh` | 置换网格核心运行时模块 |
| `AssetDefinition` | 资产定义框架（Editor 5.x 新资产系统） |

其余均为常见编辑器/引擎模块依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `dcfc273f` | [Nanite] Merging //UE5/Dev-NaniteResearch to Main (//UE5/Main) | Nanite 研究分支合并到主线 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 64 位格式化字符串问题 |
| 2026-04-20 | `61ad5fea` | Nanite Displaced Mesh Editor \| When cooking ignore editor only and NeverCook levels and assets | 打包时跳过编辑器专用和 NeverCook 关卡/资产 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到 UE_LOGF |
| 2025-10-20 | `bbe63845` | [Nanite Displaced Mesh] Fix mesh with single UV channel not having any displacement when using custo | 修复单 UV 通道网格自定义置换失效问题 |

### 维护评价

**活跃维护中** 🟢

- **创建于 2022 年**，作为 Nanite 渲染管线的实验性扩展
- **近期（2026 年）更新频繁**，最近一个月内有多次提交，且从 `Dev-NaniteResearch` 分支合并到 `Main`，说明 Nanite 团队正在积极开发此功能
- 作为 `Experimental` 插件且 `EnabledByDefault=false`，API 尚不稳定（5.6 已有废弃标记）
- **推荐在 Nanite 重度项目中关注**，但不建议在生产环境依赖当前 API

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NaniteDisplacedMesh)
- [Nanite 概述](https://docs.unrealengine.com/5.8/en-US/nanite-virtualized-geometry-in-unreal-engine/)