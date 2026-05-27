# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可定制对象 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableRuntime` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

---

## 模块文档索引

本插件包含 1200+ 源文件，属于超大型插件，按模块拆分文档：

| 文档 | 模块 | 说明 |
|---|---|---|
| [Core API](CoreAPI.md) | CustomizableObject | 核心运行时 API：可定制对象定义、实例、系统管理 |
| [Components & Actors](ComponentsActors.md) | CustomizableObject | 场景组件、Actor、实例使用 |
| [Streaming & Resources](StreamingResources.md) | CustomizableObject | 网格流式加载、纹理 MIP 数据提供、资源管理 |
| [Internal Systems](InternalSystems.md) | CustomizableObject | 私有系统：任务图、流式管理器、缓存、编译器类型 |
| [Editor Tools](EditorTools.md) | CustomizableObjectEditor + MutableTools | 编辑器接口、编译、烘焙、日志、验证 |

---

## 用途

Mutable 是 UE5 的**运行时角色/物体定制系统**。它解决的核心问题是：如何在不为每种外观组合预先烘焙独立资产的前提下，让玩家在运行时动态组合、修改和生成角色外观。

### 核心能力

- **参数化定制**：通过 Int/Float/Bool/Color/Projector/Texture/SkeletalMesh/Material 等参数控制外观变化
- **运行时网格生成**：根据参数组合动态生成 Skeletal Mesh、材质和纹理
- **流式加载**：支持网格 LOD 和纹理 MIP 的渐进式流式加载
- **烘焙**：将定制结果导出为静态资产，用于离线场景
- **扩展系统**：通过 `UCustomizableObjectExtension` 添加自定义引脚类型和回调

### 为什么存在

传统做法是为角色每种外观组合创建独立的 Skeletal Mesh 和材质，导致资产数量爆炸。Mutable 采用**图节点编译**的方式，将所有组合可能性编译成一个紧凑的中间表示，在运行时按需生成最终资源。这使得：
- 资产数量从 O(N×M×K...) 降至 O(N+M+K...)
- 磁盘和内存占用大幅减少
- 玩家可以在游戏运行时实时看到定制效果

---

## 使用场景

- 你在做一个 RPG 游戏，有数十个角色外观部位需要玩家自由搭配 → 用 Mutable 创建可定制角色
- 你需要一个武器/载具皮肤系统，让玩家更换贴花、颜色、材质 → 用 Mutable 的 Projector 和 Texture 参数
- 你需要在大型开放世界中为数百个 NPC 做外观变体，但不想制作数百个独立网格 → 用 Mutable 的随机化和参数系统
- 你需要将定制结果导出为静态资产用于存档或展示 → 用 Mutable 的 Bake 功能
- 你需要根据 LOD 距离动态生成/丢弃网格和纹理 → 用 Mutable 的流式加载系统

---

## 蓝图用法

### 核心节点 — 可定制对象（UCustomizableObject）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateInstance` | 创建此对象的一个新实例，参数初始化为默认值 | `UCustomizableObject` |
| `IsCompiled` | 检查此对象是否已编译 | `UCustomizableObject` |
| `IsLoading` | 检查对象是否仍在加载中 | `UCustomizableObject` |
| `GetParameterCount` | 获取实例可用的参数数量 | `UCustomizableObject` |
| `GetParameterTypeByName` | 按名称获取参数类型 | `UCustomizableObject` |
| `GetParameterName` | 按索引获取参数名称 | `UCustomizableObject` |
| `ContainsParameter` | 检查是否包含指定名称的参数 | `UCustomizableObject` |
| `GetEnumParameterNumValues` | 获取 Int 参数的可选值数量 | `UCustomizableObject` |
| `GetEnumParameterValue` | 获取 Int 参数第 N 个可选值的名称 | `UCustomizableObject` |
| `GetFloatParameterDefaultValue` | 获取 Float 参数的默认值 | `UCustomizableObject` |
| `GetEnumParameterDefaultValue` | 获取 Int 参数的默认值 | `UCustomizableObject` |
| `GetBoolParameterDefaultValue` | 获取 Bool 参数的默认值 | `UCustomizableObject` |
| `GetComponentCount` | 获取此对象的组件数量 | `UCustomizableObject` |
| `GetComponentName` | 获取指定索引组件的名称 | `UCustomizableObject` |
| `GetStateCount` | 获取对象状态数量 | `UCustomizableObject` |
| `GetStateName` | 获取指定索引状态的名称 | `UCustomizableObject` |
| `GetStateParameterCount` | 获取某状态下可运行时编辑的参数数量 | `UCustomizableObject` |
| `GetStateParameterName` | 获取某状态的第 N 个运行时参数名称 | `UCustomizableObject` |
| `GetParameterUIMetadata` | 获取参数的 UI 元数据 | `UCustomizableObject` |
| `GetEnumParameterValueUIMetadata` | 获取 Int 参数选项的 UI 元数据 | `UCustomizableObject` |
| `GetSkeletalMeshComponentReferenceSkeletalMesh` | 获取网格组件的参考骨骼网格 | `UCustomizableObject` |

### 核心节点 — 实例操作（UCustomizableObjectInstance）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UpdateSkeletalMeshAsync` | 异步更新骨骼网格 | `UCustomizableObjectInstance` |
| `SetIntParameterSelectedOption` | 设置 Int 参数的选中选项 | `UCustomizableObjectInstance` |
| `SetFloatParameterSelectedOption` | 设置 Float 参数值 | `UCustomizableObjectInstance` |
| `SetBoolParameterSelectedOption` | 设置 Bool 参数值 | `UCustomizableObjectInstance` |
| `SetVectorParameterSelectedOption` | 设置 Vector/Color 参数值 | `UCustomizableObjectInstance` |
| `SetProjectorParameterSelectedOption` | 设置投影器参数值 | `UCustomizableObjectInstance` |
| `SetTextureParameterSelectedOption` | 设置纹理参数值 | `UCustomizableObjectInstance` |
| `SetTransformParameterSelectedOption` | 设置 Transform 参数值 | `UCustomizableObjectInstance` |
| `SetSkeletalMeshParameterSelectedOption` | 设置骨骼网格参数值 | `UCustomizableObjectInstance` |
| `SetMaterialParameterSelectedOption` | 设置材质参数值 | `UCustomizableObjectInstance` |
| `GetIntParameterSelectedOption` | 获取 Int 参数当前值 | `UCustomizableObjectInstance` |
| `GetFloatParameterSelectedOption` | 获取 Float 参数当前值 | `UCustomizableObjectInstance` |
| `GetBoolParameterSelectedOption` | 获取 Bool 参数当前值 | `UCustomizableObjectInstance` |
| `GetVectorParameterSelectedOption` | 获取 Vector 参数当前值 | `UCustomizableObjectInstance` |
| `GetProjectorParameterSelectedOption` | 获取投影器参数当前值 | `UCustomizableObjectInstance` |
| `GetTextureParameterSelectedOption` | 获取纹理参数当前值 | `UCustomizableObjectInstance` |
| `GetTransformParameterSelectedOption` | 获取 Transform 参数当前值 | `UCustomizableObjectInstance` |
| `SetCurrentState` | 按名称设置当前状态 | `UCustomizableObjectInstance` |
| `GetCurrentState` | 获取当前状态名称 | `UCustomizableObjectInstance` |
| `GetComponentNames` | 获取生成的组件名称列表 | `UCustomizableObjectInstance` |
| `GetAnimBP` | 获取指定组件/槽位的动画 BP | `UCustomizableObjectInstance` |
| `GetAnimationGameplayTags` | 获取动画 GameplayTag 容器 | `UCustomizableObjectInstance` |
| `MultilayerProjectorCreateLayer` | 创建多层投影器图层 | `UCustomizableObjectInstance` |
| `MultilayerProjectorRemoveLayerAt` | 移除多层投影器图层 | `UCustomizableObjectInstance` |
| `MultilayerProjectorGetLayer` | 获取多层投影器图层数据 | `UCustomizableObjectInstance` |
| `MultilayerProjectorUpdateLayer` | 更新多层投影器图层数据 | `UCustomizableObjectInstance` |
| `Bake` | 将实例烘焙为静态资产 | `UCustomizableObjectInstance` |
| `SetReplacePhysicsAssets` | 启用/禁用物理资产替换 | `UCustomizableObjectInstance` |
| `SetKeepOwnershipOfGeneratedResources` | 设置是否保留生成资源的所有权 | `UCustomizableObjectInstance` |

### 核心节点 — 系统管理（UCustomizableObjectSystem）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetInstance` | 获取系统单例 | `UCustomizableObjectSystem` |
| `GetPluginVersion` | 获取插件版本字符串 | `UCustomizableObjectSystem` |
| `GetNumInstances` | 获取已构建的实例数量 | `UCustomizableObjectSystem` |
| `GetNumPendingInstances` | 获取等待更新的实例数量 | `UCustomizableObjectSystem` |
| `GetTotalInstances` | 获取总实例数量 | `UCustomizableObjectSystem` |
| `GetTextureMemoryUsed` | 获取 Mutable 纹理占用的 GPU 内存（字节） | `UCustomizableObjectSystem` |
| `GetAverageBuildTime` | 获取平均构建时间（毫秒） | `UCustomizableObjectSystem` |
| `IsUpdating` | 检查指定实例是否正在更新 | `UCustomizableObjectSystem` |
| `SetWorkingMemory` | 设置工作内存限制（KB） | `UCustomizableObjectSystem` |
| `GetWorkingMemory` | 获取工作内存限制 | `UCustomizableObjectSystem` |
| `SetGenerateInstancesWithinRange` | 启用基于距离的实例生成 | `UCustomizableObjectSystem` |
| `SetInstanceGenerationRange` | 设置实例生成范围 | `UCustomizableObjectSystem` |
| `AddViewCenter` | 添加视图中心 Actor | `UCustomizableObjectSystem` |
| `RemoveViewCenter` | 移除视图中心 Actor | `UCustomizableObjectSystem` |
| `ClearViewCenters` | 清除所有视图中心 | `UCustomizableObjectSystem` |

### 核心节点 — 组件（UCustomizableSkeletalComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCustomizableObjectInstance` | 获取关联的可定制对象实例 | `UCustomizableSkeletalComponent` |
| `SetCustomizableObjectInstance` | 设置关联的可定制对象实例 | `UCustomizableSkeletalComponent` |
| `SetComponentName` | 设置组件名称 | `UCustomizableSkeletalComponent` |
| `GetComponentName` | 获取组件名称 | `UCustomizableSkeletalComponent` |
| `UpdateSkeletalMeshAsync` | 异步更新骨骼网格 | `UCustomizableSkeletalComponent` |
| `UpdateSkeletalMeshAsyncResult` | 异步更新骨骼网格（带回调） | `UCustomizableSkeletalComponent` |
| `SetSkipSetReferenceSkeletalMesh` | 是否跳过设置参考网格 | `UCustomizableSkeletalComponent` |
| `SetSkipSetSkeletalMeshOnAttach` | 是否跳过附加时设置网格 | `UCustomizableSkeletalComponent` |

### 使用示例（蓝图描述）

**场景：创建一个可定制角色并设置外观参数**

1. **创建实例**：对 `CustomizableObject` 资产调用 `CreateInstance`，获得 `CustomizableObjectInstance`
2. **设置参数**：
   - 对实例调用 `SetIntParameterSelectedOption("HairStyle", "Long")` 设置发型
   - 对实例调用 `SetBoolParameterSelectedOption("HasHat", true)` 启用帽子
   - 对实例调用 `SetFloatParameterSelectedOption("SkinColor", 0.7)` 设置肤色
   - 对实例调用 `SetVectorParameterSelectedOption("HairColor", FVector4f(1,0.8,0.6,1))` 设置发色
3. **附加组件**：将 `CustomizableSkeletalComponent` 添加到角色 Actor，通过 `SetCustomizableObjectInstance` 关联实例
4. **触发更新**：调用组件的 `UpdateSkeletalMeshAsync` 开始异步生成
5. **监听完成**：在实例的 `UpdatedDelegate` 上绑定回调，更新完成后将自动刷新网格

**场景：动态切换状态**

1. 调用 `SetCurrentState("Combat")` 切换到战斗状态
2. 调用 `UpdateSkeletalMeshAsync` 触发更新
3. 状态切换会自动应用该状态下配置的参数约束和强制值

---

## C++ 用法

### 头文件引入

```cpp
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectInstance.h"
#include "MuCO/CustomizableObjectSystem.h"
#include "MuCO/CustomizableSkeletalComponent.h"
#include "MuCO/CustomizableObjectInstanceDescriptor.h"
#include "MuCO/CustomizableObjectExtension.h"
```

### 基本用法 — 创建实例并设置参数

```cpp
// 创建实例
UCustomizableObject* CustomizableObject = LoadObject<UCustomizableObject>(nullptr, TEXT("/Game/CO/MyCharacter"));
UCustomizableObjectInstance* Instance = CustomizableObject->CreateInstance();

// 设置参数
Instance->SetIntParameterSelectedOption(TEXT("HairStyle"), TEXT("Long"));
Instance->SetBoolParameterSelectedOption(TEXT("HasHat"), true);
Instance->SetFloatParameterSelectedOption(TEXT("SkinColor"), 0.7f);
Instance->SetVectorParameterSelectedOption(TEXT("HairColor"), FVector4f(1.0f, 0.8f, 0.6f, 1.0f));

// 异步更新
Instance->UpdateSkeletalMeshAsync();

// 监听更新完成
Instance->UpdatedDelegate.AddDynamic(this, &AMyActor::OnInstanceUpdated);
```

*来源：Public/MuCO/CustomizableObjectInstance.h、Public/MuCO/CustomizableObjectParameterTypeDefinitions.h*

### 基本用法 — 查询对象信息

```cpp
// 查询参数信息
int32 ParamCount = CustomizableObject->GetParameterCount();
for (int32 i = 0; i < ParamCount; ++i)
{
    const FString& ParamName = CustomizableObject->GetParameterName(i);
    EMutableParameterType Type = CustomizableObject->GetParameterTypeByName(ParamName);
    
    if (Type == EMutableParameterType::Int)
    {
        int32 NumValues = CustomizableObject->GetEnumParameterNumValues(ParamName);
        for (int32 j = 0; j < NumValues; ++j)
        {
            const FString& ValueName = CustomizableObject->GetEnumParameterValue(ParamName, j);
        }
    }
}

// 查询状态信息
int32 StateCount = CustomizableObject->GetStateCount();
FString StateName = CustomizableObject->GetStateName(0);
int32 StateParamCount = CustomizableObject->GetStateParameterCount(StateName);
```

*来源：Public/MuCO/CustomizableObject.h*

### 进阶用法 — 系统管理与距离优化

```cpp
// 获取系统单例
UCustomizableObjectSystem* System = UCustomizableObjectSystem::GetInstance();

// 设置工作内存限制（KB）
System->SetWorkingMemory(256 * 1024); // 256 MB

// 启用距离优化：只在摄像机附近的实例才生成网格
System->SetGenerateInstancesWithinRange(true);
System->SetInstanceGenerationRange(2000.0f); // 2000 cm

// 添加视图中心
System->AddViewCenter(MyPlayerActor);

// 监控状态
int32 NumInstances = System->GetNumInstances();
int32 NumPending = System->GetNumPendingInstances();
int64 TextureMem = System->GetTextureMemoryUsed();
```

*来源：Public/MuCO/CustomizableObjectSystem.h*

### 进阶用法 — 烘焙实例为静态资产

```cpp
FBakingConfiguration BakeConfig;
BakeConfig.OutputPath = TEXT("/Game/BakedCharacters");
BakeConfig.OutputFilesBaseName = TEXT("CharacterBake");
BakeConfig.bExportAllResourcesOnBake = true;
BakeConfig.bGenerateConstantMaterialInstancesOnBake = true;
BakeConfig.bReplaceRestrictedCharacters = true;

// 自定义资源前缀
BakeConfig.SkeletalMeshAssetPrefix = TEXT("SK_");
BakeConfig.TextureAssetPrefix = TEXT("T_");
BakeConfig.MaterialAssetPrefix = TEXT("M_");

// 绑定完成回调
BakeConfig.OnBakeOperationCompletedCallback.BindDynamic(this, &AMyActor::OnBakeCompleted);

// 执行烘焙（仅编辑器可用）
Instance->Bake(BakeConfig);
```

*来源：Public/MuCO/CustomizableObjectInstance.h*

### 进阶用法 — 投影器参数

```cpp
// 设置投影器位置、方向、缩放、角度
FVector Pos(100, 0, 50);
FVector Dir(0, 0, -1);
FVector Up(1, 0, 0);
FVector Scale(10, 10, 100);
float Angle = 0.0f;

Instance->SetProjectorPosition(TEXT("DecalProjector"), Pos);
Instance->SetProjectorDirection(TEXT("DecalProjector"), Dir);
Instance->SetProjectorUp(TEXT("DecalProjector"), Up);
Instance->SetProjectorScale(TEXT("DecalProjector"), Scale);
Instance->SetProjectorAngle(TEXT("DecalProjector"), Angle);

// 或一次性设置
FCustomizableObjectProjector Projector;
Projector.Position = FVector3f(Pos);
Projector.Direction = FVector3f(Dir);
Projector.Up = FVector3f(Up);
Projector.Scale = FVector3f(Scale);
Projector.ProjectionType = ECustomizableObjectProjectorType::Planar;
Projector.Angle = Angle;

Instance->SetProjectorParameterSelectedOption(TEXT("DecalProjector"), Projector);
```

*来源：Public/MuCO/CustomizableObjectInstance.h、Public/MuCO/CustomizableObjectParameterTypeDefinitions.h*

### 进阶用法 — 多层投影器

```cpp
// 多层投影器用于叠加多张贴花/图案
FName ProjectorParamName = TEXT("MultiLayerDecal");

// 创建图层
Instance->MultilayerProjectorCreateLayer(ProjectorParamName, 0);

// 设置图层数据
FMultilayerProjectorLayer Layer;
Layer.Position = FVector(0, 0, 100);
Layer.Direction = FVector(0, 0, -1);
Layer.Image = TEXT("Tattoo_01");
Layer.Opacity = 0.8f;
Layer.Scale = FVector(5, 5, 10);
Instance->MultilayerProjectorUpdateLayer(ProjectorParamName, 0, Layer);

// 获取和移除图层
FMultilayerProjectorLayer Retrieved = Instance->MultilayerProjectorGetLayer(ProjectorParamName, 0);
int32 NumLayers = Instance->MultilayerProjectorNumLayers(ProjectorParamName);
Instance->MultilayerProjectorRemoveLayerAt(ProjectorParamName, 0);
```

*来源：Public/MuCO/CustomizableObjectInstance.h、Public/MuCO/MultilayerProjector.h*

### 进阶用法 — 序列化/反序列化实例描述

```cpp
// 保存实例描述到存档
FCustomizableObjectInstanceDescriptor Descriptor;
FMemoryWriter MemWriter(SavedData);
Descriptor.SaveDescriptor(MemWriter, /*bUseCompactDescriptor=*/true);

// 从存档加载
FMemoryReader MemReader(SavedData);
FCustomizableObjectInstanceDescriptor LoadedDescriptor;
LoadedDescriptor.LoadDescriptor(MemReader);

// 直接操作描述符参数
LoadedDescriptor.SetIntParameterSelectedOption(TEXT("HairStyle"), TEXT("Short"));
LoadedDescriptor.SetFloatParameterSelectedOption(TEXT("SkinColor"), 0.5f);
LoadedDescriptor.SetState(1);

// 将描述符应用到实例
Instance->LoadDescriptor(MemReader);
```

*来源：Public/MuCO/CustomizableObjectInstanceDescriptor.h*

### 进阶用法 — 注册扩展

```cpp
// 创建自定义扩展类
UCLASS()
class UMyCustomExtension : public UCustomizableObjectExtension
{
    GENERATED_BODY()
public:
    virtual TArray<FCustomizableObjectPinType> GetPinTypes() const override;
    virtual TArray<FObjectNodeInputPin> GetAdditionalObjectNodePins() const override;
    virtual void OnSkeletalMeshCreated(FName ComponentName, USkeletalMesh* SkeletalMesh) const override;
    virtual void OnCustomizableObjectInstanceUsageUpdated(UCustomizableObjectInstanceUsage& Usage, TArray<TObjectPtr<const UObject>>& ExtensionData) const override;
};

// 注册扩展
UMyCustomExtension* MyExt = NewObject<UMyCustomExtension>();
ICustomizableObjectModule::Get().RegisterExtension(MyExt);
```

*来源：Public/MuCO/CustomizableObjectExtension.h、Public/MuCO/ICustomizableObjectModule.h*

---

## Demo 示例

### 最小可编译示例 — 可定制角色组件

**MyCustomizableCharacter.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MuCO/CustomizableObjectInstance.h"
#include "MyCustomizableCharacter.generated.h"

class UCustomizableSkeletalComponent;

UCLASS(BlueprintType, Blueprintable)
class AMyCustomizableCharacter : public AActor
{
    GENERATED_BODY()

public:
    AMyCustomizableCharacter();

    /** 创建实例并初始化 */
    UFUNCTION(BlueprintCallable)
    void InitializeWithObject(UCustomizableObject* InObject);

    /** 随机化外观 */
    UFUNCTION(BlueprintCallable)
    void RandomizeAppearance();

    /** 设置发型参数 */
    UFUNCTION(BlueprintCallable)
    void SetHairStyle(const FString& StyleName);

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UCustomizableSkeletalComponent> CustomizableComponent;

    UPROPERTY(BlueprintReadOnly)
    TObjectPtr<UCustomizableObjectInstance> Instance;

private:
    UFUNCTION()
    void OnInstanceUpdated(UCustomizableObjectInstance* UpdatedInstance);
};
```

**MyCustomizableCharacter.cpp**

```cpp
#include "MyCustomizableCharacter.h"
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableSkeletalComponent.h"
#include "MuCO/CustomizableObjectSystem.h"

AMyCustomizableCharacter::AMyCustomizableCharacter()
{
    CustomizableComponent = CreateDefaultSubobject<UCustomizableSkeletalComponent>(TEXT("CustomizableComponent"));
    RootComponent = CustomizableComponent;
}

void AMyCustomizableCharacter::InitializeWithObject(UCustomizableObject* InObject)
{
    if (!InObject || !InObject->IsCompiled())
    {
        UE_LOG(LogTemp, Warning, TEXT("Customizable Object is not compiled or null"));
        return;
    }

    Instance = InObject->CreateInstance();
    if (!Instance) return;

    CustomizableComponent->SetCustomizableObjectInstance(Instance);

    // 绑定更新完成回调
    Instance->UpdatedNativeDelegate.AddUObject(this, &AMyCustomizableCharacter::OnInstanceUpdated);

    // 触发首次更新
    CustomizableComponent->UpdateSkeletalMeshAsync();
}

void AMyCustomizableCharacter::RandomizeAppearance()
{
    if (!Instance) return;

    Instance->SetRandomValues();
    CustomizableComponent->UpdateSkeletalMeshAsync();
}

void AMyCustomizableCharacter::SetHairStyle(const FString& StyleName)
{
    if (!Instance) return;

    Instance->SetIntParameterSelectedOption(TEXT("HairStyle"), StyleName);
    CustomizableComponent->UpdateSkeletalMeshAsync();
}

void AMyCustomizableCharacter::OnInstanceUpdated(UCustomizableObjectInstance* UpdatedInstance)
{
    if (!UpdatedInstance) return;

    // 获取生成的组件名称
    TArray<FName> Components = UpdatedInstance->GetComponentNames();
    UE_LOG(LogTemp, Log, TEXT("Instance updated with %d components"), Components.Num());
}
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MutableTools` | Mutable 编译工具链（CO 图节点编译为 Mutable 模型） |
| `DerivedDataCache` | 派生数据缓存，用于缓存编译后的 CO 数据 |
| `MessageLog` | 编辑器消息日志输出 |

*注：MutableRuntime、Core、CoreUObject、Engine、Slate、UMG 等常见依赖已省略。*

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复多个同名 SKM 导致骨骼网格几何体重复的问题 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复 UV Mask 裁剪操作未加载正确 MIP 级别的问题 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. An incorrect LODBias | 修复纹理参数计算 LODBias 方法错误的问题 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 使用 ClothingAssetBase 接口支持更多布料资产类型 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较 PassthroughObjects 时可能出现的数据竞争 |

### 维护评价

**活跃维护**

- **创建时间**：2024 年 9 月从 Experimental 迁移到 Beta 状态（底层引擎有更长历史）
- **更新频率**：最近提交集中在 2026 年 5 月，持续有 bug 修复和功能改进
- **维护状态**：由 Epic Games 官方维护，是 UE5 官方角色定制方案
- **实验性警告**：当前标记为 Beta（`IsBetaVersion=true`），API 可能仍有变动
- **推荐程度**：推荐用于需要运行时角色定制的项目，但需注意 Beta 状态可能带来的 API 变化。该插件从 Experimental 提升到 Beta 表明 Epic 认为其核心功能已稳定，但仍在持续优化中。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/MutablePlugin/)