# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

## 用途

Chaos Cloth Asset 插件为 UE5 提供了**基于版型（Pattern）的布料模拟资产系统**。它将传统的骨骼网格体蒙皮与 Chaos 物理引擎的布料模拟相结合，允许用户通过 Dataflow 图形系统构建布料资产，然后由 `UChaosClothComponent` 在运行时驱动物理模拟。

这个插件解决的核心问题是：**将布料的视觉表现（渲染网格）与物理模拟（仿真网格）统一管理**。传统的 Cloth 系统依赖 Skeletal Mesh 的 Clothing Data，而 Chaos Cloth Asset 引入了独立的资产类型（`UChaosClothAsset`），支持：

- 通过 Dataflow 节点图进行布料数据的程序化构建
- 多 LOD 布料模拟
- 服装套装（Outfit）资产，将多块布料组合管理
- 运行时通过蓝图交互器动态调整模拟参数
- 与 Chaos 缓存系统集成，支持录制和回放

插件从 Experimental 文件夹迁移而来并标记为 Beta，表明 Epic 正在积极完善该系统，目标是取代旧的 Cloth 系统。

## 使用场景

- 你在制作角色服装系统，需要真实的布料飘动效果 → 使用 `UChaosClothComponent` + `UChaosClothAsset`
- 你需要基于版型（Pattern）从 2D 样片构建布料网格 → 通过 Dataflow 图形系统构建 `UChaosClothAsset`
- 你有多件服装需要统一管理（如上衣、裤子、裙子）→ 使用 Outfit 资产（`UChaosOutfitAsset`）
- 你需要在运行时动态调整布料参数（如风力、刚度）→ 通过 `UChaosClothAssetInteractor` 蓝图接口
- 你需要布料与外部骨骼网格体产生碰撞 → 通过 `AddCollisionSource` 添加碰撞源
- 你需要录制布料模拟数据并回放 → 配合 Chaos Cache 系统

## 蓝图用法

### 组件设置与资产管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetAsset` | 设置布料/服装资产 | `UChaosClothComponent` |
| `GetAsset` | 获取当前使用的布料资产 | `UChaosClothComponent` |
| `SetOverlayMaterial` | 设置覆盖材质 | `UChaosClothAssetBase` |
| `GetOverlayMaterial` | 获取覆盖材质 | `UChaosClothAssetBase` |
| `SetOverlayMaterialMaxDrawDistance` | 设置覆盖材质最大绘制距离 | `UChaosClothAssetBase` |
| `GetOverlayMaterialMaxDrawDistance` | 获取覆盖材质最大绘制距离 | `UChaosClothAssetBase` |

### 模拟控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetEnableSimulation` | 启用/禁用布料模拟 | `UChaosClothComponent` |
| `IsSimulationEnabled` | 查询模拟是否启用 | `UChaosClothComponent` |
| `SuspendSimulation` | 暂停模拟，保持当前姿态 | `UChaosClothComponent` |
| `ResumeSimulation` | 恢复已暂停的模拟 | `UChaosClothComponent` |
| `IsSimulationSuspended` | 查询模拟是否暂停 | `UChaosClothComponent` |
| `ResetConfigProperties` | 重置模拟配置为资产默认值 | `UChaosClothComponent` |
| `RecreateClothSimulationProxy` | 硬重置模拟（重建代理） | `UChaosClothComponent` |

### 传送与重置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ResetTeleportMode` | 重置传送模式 | `UChaosClothComponent` |
| `ForceNextUpdateTeleport` | 下一帧传送布料粒子，保留姿态和速度 | `UChaosClothComponent` |
| `ForceNextUpdateTeleportAndReset` | 下一帧传送并重置姿态和速度 | `UChaosClothComponent` |
| `ResetRestLengthsWithMorphTarget` | 使用 Morph Target 重置布料静止长度 | `UChaosClothComponent` |
| `SetTeleportDistanceThreshold` | 设置自动传送的距离阈值 | `UChaosClothComponent` |
| `SetTeleportRotationThreshold` | 设置自动传送的旋转阈值 | `UChaosClothComponent` |

### 碰撞管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddCollisionSource` | 添加外部碰撞源 | `UChaosClothComponent` |
| `RemoveCollisionSource` | 移除指定碰撞源 | `UChaosClothComponent` |
| `RemoveCollisionSources` | 移除指定组件的所有碰撞源 | `UChaosClothComponent` |
| `ResetCollisionSources` | 清除所有碰撞源 | `UChaosClothComponent` |
| `SetCollideWithEnvironment` | 设置是否与环境碰撞 | `UChaosClothComponent` |
| `GetCollideWithEnvironment` | 查询环境碰撞状态 | `UChaosClothComponent` |

### 属性交互器（Cloth Asset Interactor）

通过 `GetClothOutfitInteractor` 获取交互器后，可读写布料模拟参数：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetClothOutfitInteractor` | 获取布料属性交互器 | `UChaosClothComponent` |
| `GetAllPropertyNames` | 获取所有可配置属性名 | `UChaosClothAssetInteractor` |
| `GetFloatPropertyValue` | 读取浮点属性 | `UChaosClothAssetInteractor` |
| `SetFloatPropertyValue` | 设置浮点属性 | `UChaosClothAssetInteractor` |
| `GetIntPropertyValue` | 读取整数属性 | `UChaosClothAssetInteractor` |
| `SetIntPropertyValue` | 设置整数属性 | `UChaosClothAssetInteractor` |
| `GetVectorPropertyValue` | 读取向量属性 | `UChaosClothAssetInteractor` |
| `SetVectorPropertyValue` | 设置向量属性 | `UChaosClothAssetInteractor` |
| `GetStringPropertyValue` | 读取字符串属性 | `UChaosClothAssetInteractor` |
| `SetStringPropertyValue` | 设置字符串属性 | `UChaosClothAssetInteractor` |
| `GetWeightedFloatPropertyValue` | 读取加权浮点（低值/高值） | `UChaosClothAssetInteractor` |
| `SetWeightedFloatPropertyValue` | 设置加权浮点 | `UChaosClothAssetInteractor` |
| `SetPropertySet` | 从数据资产批量设置属性 | `UChaosClothAssetInteractor` |

### 使用示例（蓝图描述）

**基本布料设置流程：**

1. 在角色的 Skeletal Mesh Component 上添加 `UChaosClothComponent`
2. 创建或引用一个 `UChaosClothAsset`（通过 Dataflow 图构建）
3. 在 `BeginPlay` 中调用 `SetAsset`，传入布料资产
4. 布料自动开始模拟

**运行时调整布料参数：**

1. 调用 `GetClothOutfitInteractor`（默认参数 ModelIndex=0）获取交互器
2. 使用 `SetFloatPropertyValue` 设置如 `WindDragCoefficient` 等参数
3. 或使用 `UClothAssetInteractorDataAsset` 预设多组参数，通过 `SetPropertySet` 一键应用

**碰撞源设置：**

1. 调用 `AddCollisionSource`，传入角色的 Skeletal Mesh Component 和 Physics Asset
2. 布料将在每帧模拟时自动与这些碰撞体交互

## C++ 用法

### 头文件引入

```cpp
#include "ChaosClothAsset/ClothAsset.h"
#include "ChaosClothAsset/ClothComponent.h"
#include "ChaosClothAsset/ClothAssetInteractor.h"
#include "ChaosClothAsset/ClothSimulationModel.h"
```

### 基本用法

**创建布料资产并设置到组件：**

```cpp
// 设置布料组件的资产（来源：Public/ChaosClothAsset/ClothComponent.h）
UChaosClothComponent* ClothComponent = GetClothComponent();
UChaosClothAsset* ClothAsset = LoadObject<UChaosClothAsset>(nullptr, TEXT("/Game/MyClothAsset"));
ClothComponent->SetAsset(ClothAsset);
```

**通过交互器修改模拟参数（运行时）：**

```cpp
// 获取交互器并修改参数（来源：Public/ChaosClothAsset/ClothAssetInteractor.h）
UChaosClothAssetInteractor* Interactor = ClothComponent->GetClothOutfitInteractor();

// 读取当前参数值
float WindDrag = Interactor->GetFloatPropertyValue(FName("WindDragCoefficient"), 0, 0.f);

// 设置新参数值（LODIndex=-1 表示所有 LOD）
Interactor->SetFloatPropertyValue(FName("WindDragCoefficient"), -1, 0.5f);
Interactor->SetVectorPropertyValue(FName("WindVelocity"), -1, FVector(100.f, 0.f, 0.f));

// 获取所有可用属性名
TArray<FName> AllProperties = Interactor->GetAllPropertyNames(-1);
```

### 进阶用法

**通过 C++ 硬重置模拟并控制传送：**

```cpp
// 来源：Public/ChaosClothAsset/ClothComponent.h
UChaosClothComponent* ClothComponent = GetClothComponent();

// 硬重置整个布料模拟代理
ClothComponent->RecreateClothSimulationProxy();

// 传送布料但保留姿态和速度
ClothComponent->ForceNextUpdateTeleport();

// 传送并完全重置姿态
ClothComponent->ForceNextUpdateTeleportAndReset();

// 设置自动传送阈值
ClothComponent->SetTeleportDistanceThreshold(200.f);  // 移动超过 200 单位自动传送
ClothComponent->SetTeleportRotationThreshold(45.f);   // 旋转超过 45 度自动传送
```

**添加外部碰撞源：**

```cpp
// 来源：Public/ChaosClothAsset/ClothComponent.h
ClothComponent->AddCollisionSource(
    OtherSkeletalMeshComponent,
    OtherPhysicsAsset,
    true   // 仅使用 Sphyls（球体和胶囊体），性能更优
);
```

**访问布料模拟模型数据：**

```cpp
// 来源：Public/ChaosClothAsset/ClothSimulationModel.h
const UChaosClothAsset* ClothAsset = Cast<UChaosClothAsset>(ClothComponent->GetAsset());
TSharedPtr<const FChaosClothSimulationModel> SimModel = ClothAsset->GetClothSimulationModel(0);

if (SimModel.IsValid())
{
    int32 NumLODs = SimModel->GetNumLods();
    int32 NumVertices = SimModel->GetNumVertices(0);  // LOD 0 的顶点数
    int32 NumTriangles = SimModel->GetNumTriangles(0);
    
    // 访问顶点位置
    TConstArrayView<FVector3f> Positions = SimModel->GetPositions(0);
    
    // 访问蒙皮数据
    TConstArrayView<FClothVertBoneData> BoneData = SimModel->GetBoneData(0);
    
    // 访问 2D 版型数据
    TConstArrayView<FVector2f> PatternPositions = SimModel->GetPatternPositions(0);
}
```

**批量设置属性从数据资产：**

```cpp
// 来源：Private/ChaosClothAsset/ClothAssetInteractorDataAsset.h
UClothAssetInteractorDataAsset* DataAsset = LoadObject<UClothAssetInteractorDataAsset>(nullptr, TEXT("/Game/MyClothPresets"));
UChaosClothAssetInteractor* Interactor = ClothComponent->GetClothOutfitInteractor();

// 获取特定预设
const FClothAssetInteractorPropertyBag& PropertySet = DataAsset->GetPropertySet(FName("HeavyWind"));

// 批量应用
Interactor->SetPropertySet(PropertySet, -1);
```

## Demo 示例

```cpp
// MyClothActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyClothActor.generated.h"

class UChaosClothComponent;
class UChaosClothAsset;

UCLASS()
class AMyClothActor : public AActor
{
    GENERATED_BODY()

public:
    AMyClothActor();

    UPROPERTY(VisibleAnywhere)
    UChaosClothComponent* ClothComponent;

    UPROPERTY(EditAnywhere, Category = "Cloth")
    TSoftObjectPtr<UChaosClothAsset> ClothAsset;

    UPROPERTY(EditAnywhere, Category = "Cloth")
    float WindStrength = 0.f;

    UFUNCTION(BlueprintCallable, Category = "Cloth")
    void ResetCloth();
};
```

```cpp
// MyClothActor.cpp
#include "MyClothActor.h"
#include "ChaosClothAsset/ClothComponent.h"
#include "ChaosClothAsset/ClothAsset.h"
#include "ChaosClothAsset/ClothAssetInteractor.h"

AMyClothActor::AMyClothActor()
{
    ClothComponent = CreateDefaultSubobject<UChaosClothComponent>(TEXT("ClothComponent"));
    SetRootComponent(ClothComponent);
}

void AMyClothActor::ResetCloth()
{
    // 强制下一帧传送并重置
    ClothComponent->ForceNextUpdateTeleportAndReset();
    
    // 通过交互器修改风力参数
    if (UChaosClothAssetInteractor* Interactor = ClothComponent->GetClothOutfitInteractor())
    {
        Interactor->SetFloatPropertyValue(FName("WindDragCoefficient"), -1, WindStrength);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | Chaos 物理布料模拟引擎核心 |
| `GeometryCache` | 几何体缓存支持 |
| `Dataflow` | Dataflow 数据流图系统，用于程序化构建布料数据 |
| `ClothingSystemRuntimeCommon` | 服装系统运行时基础框架 |
| `Chaos` | Chaos 物理引擎 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Blueprint | 修复蓝图重建脚本中布料组件属性丢失问题 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable. | 将并行模拟等待从帧末移至 TG_LastDemotable 优化性能 |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefershBoneMapping for ClothAssetSKMClothingAsset. | 实现 SKM 服装资产的骨骼映射刷新 |
| 2026-05-22 | `e98c5896` | [Chaos Cloth Asset] Refresh the editor-only Asset alias after a duplicate or paste of an actor. | 修复复制粘贴 Actor 后编辑器资产引用不更新的问题 |
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |

### 维护评价

Chaos Cloth Asset 是 Epic 正在**积极维护**的 Beta 阶段插件。最近一次更新在 2026 年 5 月，更新频率很高（几乎每天都有提交），内容涵盖：

- **功能完善**：骨骼映射刷新、并行模拟优化
- **稳定性修复**：蓝图重建脚本属性保留、复制粘贴引用修复
- **代码清理**：转换器重构

该插件于 2024 年 3 月从 Experimental 迁移至正式插件目录并标记为 Beta，是 Epic 布料系统的下一代方案。当前仍在快速迭代中，API 有大量 deprecated 标记（5.4-5.7 多个版本），说明接口尚未完全稳定。

**注意事项：**
- 插件默认不启用（`EnabledByDefault: false`），需在项目设置中手动启用
- 仅限 Win64/Mac/Linux 平台
- 标记为 Beta，生产环境使用需谨慎，API 可能在后续版本发生变化
- 依赖 ChaosCloth、Dataflow 等插件，需确保这些插件已启用

**推荐使用**：如果你的项目需要高质量布料模拟，且可以接受 Beta 状态的 API 变动风险，推荐使用此插件。它提供了比旧版 Cloth 系统更灵活的 Dataflow 工作流和更强大的运行时控制能力。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
- [官方文档]()（暂无）