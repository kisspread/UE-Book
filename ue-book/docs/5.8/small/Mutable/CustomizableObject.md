# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可定制对象系统 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是 UE5 的**运行时角色/物体定制系统**。它解决的核心问题是：**如何让玩家在游戏运行时实时修改角色外观（骨骼网格体、材质、纹理、变形等），同时保持高性能**。

具体来说，Mutable 允许你：

1. **在编辑器中以节点图方式定义可定制对象**（Customizable Object, CO），声明哪些部分可以被修改
2. **在运行时创建实例**（Customizable Object Instance, COI），通过参数值驱动外观变化
3. **异步生成最终的 SkeletalMesh、材质和纹理**，支持 LOD 流式加载
4. **将定制结果烘焙为静态资产**，用于离线场景

与简单的材质参数切换不同，Mutable 能在运行时**合并、裁剪、重组多个网格体和纹理**，生成全新的几何体。例如将头部、躯干、手臂的多个网格体合并为一个完整的角色模型，同时处理 UV 重映射、骨骼合并、布料模拟、物理资产合并等。

## 使用场景

- **角色定制系统**：玩家在大厅/捏脸界面选择发型、服装、配饰 → Mutable 在运行时合并网格体并生成最终模型
- **多人游戏中的角色展示**：需要在不同玩家身上展示不同外观组合 → 异步更新避免帧率卡顿
- **皮肤系统**：出售不同外观包（服装、武器皮肤）→ 通过参数切换材质/纹理
- **LOD 流式管理**：远距离角色使用低精度网格，靠近时逐步加载高精度 LOD
- **烘焙导出**：将运行时定制结果保存为静态资产，用于过场动画或截图

## 蓝图用法

Mutable 的蓝图 API 分为四层：**可定制对象定义**、**实例参数控制**、**渲染组件**、**系统管理**。

### 核心节点 — 可定制对象（UCustomizableObject）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateInstance` | 创建一个新的实例，参数使用默认值 | `UCustomizableObject` |
| `GetParameterCount` | 获取运行时可编辑的参数总数 | `UCustomizableObject` |
| `GetParameterTypeByName` | 获取指定参数的类型（Bool/Int/Float/Color 等） | `UCustomizableObject` |
| `GetParameterName` | 按索引获取参数名称 | `UCustomizableObject` |
| `GetEnumParameterNumValues` | 获取 Int 枚举参数的可选值数量 | `UCustomizableObject` |
| `GetEnumParameterValue` | 获取 Int 枚举参数的指定值名称 | `UCustomizableObject` |
| `GetFloatParameterDefaultValue` | 获取 Float 参数的默认值 | `UCustomizableObject` |
| `GetBoolParameterDefaultValue` | 获取 Bool 参数的默认值 | `UCustomizableObject` |
| `GetColorParameterDefaultValue` | 获取 Color 参数的默认值 | `UCustomizableObject` |
| `GetComponentCount` | 获取组件数量 | `UCustomizableObject` |
| `GetComponentName` | 获取指定组件的名称 | `UCustomizableObject` |
| `GetStateCount` | 获取对象状态数量 | `UCustomizableObject` |
| `GetStateName` | 获取状态名称 | `UCustomizableObject` |
| `GetStateParameterCount` | 获取某状态下可运行时编辑的参数数量 | `UCustomizableObject` |
| `IsCompiled` | 检查 CO 是否已编译 | `UCustomizableObject` |
| `IsLoading` | 检查 CO 是否仍在加载中 | `UCustomizableObject` |

### 核心节点 — 实例参数（UCustomizableObjectInstance）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetIntParameterSelectedOption` | 设置 Int 参数的选中选项 | `UCustomizableObjectInstance` |
| `SetFloatParameterSelectedOption` | 设置 Float 参数值 | `UCustomizableObjectInstance` |
| `SetBoolParameterSelectedOption` | 设置 Bool 参数值 | `UCustomizableObjectInstance` |
| `SetColorParameterSelectedOption` | 设置 Color 参数值 | `UCustomizableObjectInstance` |
| `SetTextureParameterSelectedOption` | 设置 Texture 参数值 | `UCustomizableObjectInstance` |
| `SetSkeletalMeshParameterSelectedOption` | 设置 SkeletalMesh 参数值 | `UCustomizableObjectInstance` |
| `SetMaterialParameterSelectedOption` | 设置 Material 参数值 | `UCustomizableObjectInstance` |
| `SetTransformParameterSelectedOption` | 设置 Transform 参数值 | `UCustomizableObjectInstance` |
| `SetProjectorPosition` | 设置投影器位置 | `UCustomizableObjectInstance` |
| `SetProjectorDirection` | 设置投影器方向 | `UCustomizableObjectInstance` |
| `SetProjectorScale` | 设置投影器缩放 | `UCustomizableObjectInstance` |
| `SetProjectorAngle` | 设置投影器角度（圆柱投影） | `UCustomizableObjectInstance` |
| `GetFloatParameterSelectedOption` | 获取 Float 参数当前值 | `UCustomizableObjectInstance` |
| `GetBoolParameterSelectedOption` | 获取 Bool 参数当前值 | `UCustomizableObjectInstance` |
| `UpdateSkeletalMeshAsync` | 异步更新实例的骨骼网格体 | `UCustomizableObjectInstance` |
| `SetState` | 设置实例当前状态 | `UCustomizableObjectInstance` |
| `SetReplacePhysicsAssets` | 启用/禁用物理资产替换 | `UCustomizableObjectInstance` |
| `SetKeepOwnershipOfGeneratedResources` | 设置是否保持生成资源的所有权 | `UCustomizableObjectInstance` |
| `GetComponentNames` | 获取实例生成的组件名称列表 | `UCustomizableObjectInstance` |
| `GetAnimBP` | 获取指定组件和槽位的动画蓝图 | `UCustomizableObjectInstance` |
| `MultilayerProjectorCreateLayer` | 创建多层投影器层 | `UCustomizableObjectInstance` |
| `MultilayerProjectorRemoveLayerAt` | 移除多层投影器层 | `UCustomizableObjectInstance` |
| `MultilayerProjectorUpdateLayer` | 更新多层投影器层 | `UCustomizableObjectInstance` |
| `MultilayerProjectorGetLayer` | 获取多层投影器层数据 | `UCustomizableObjectInstance` |

### 核心节点 — 渲染组件

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCustomizableObjectInstance` | 设置组件使用的实例 | `UCustomizableSkeletalComponent` |
| `GetCustomizableObjectInstance` | 获取组件使用的实例 | `UCustomizableSkeletalComponent` |
| `SetComponentName` | 设置组件名称（对应 CO 中的组件名） | `UCustomizableSkeletalComponent` |
| `GetComponentName` | 获取组件名称 | `UCustomizableSkeletalComponent` |
| `UpdateSkeletalMeshAsync` | 异步更新骨骼网格体 | `UCustomizableSkeletalComponent` |
| `UpdateSkeletalMeshAsyncResult` | 异步更新并注册完成回调 | `UCustomizableSkeletalComponent` |
| `SetSkipSetReferenceSkeletalMesh` | 是否跳过设置参考网格体 | `UCustomizableSkeletalComponent` |
| `SetSkipSetSkeletalMeshOnAttach` | 是否跳过附加时设置网格体 | `UCustomizableSkeletalComponent` |
| `GetSkeletalMeshComponent` | 按名称获取骨骼网格体组件 | `ACustomizableSkeletalMeshActor` |
| `GetCustomizableObjectInstance` | 获取 Actor 的实例 | `ACustomizableSkeletalMeshActor` |

### 核心节点 — 系统管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetInstance` | 获取 Mutable 系统单例 | `UCustomizableObjectSystem` |
| `GetNumInstances` | 获取已构建的实例数 | `UCustomizableObjectSystem` |
| `GetNumPendingInstances` | 获取等待更新的实例数 | `UCustomizableObjectSystem` |
| `GetTextureMemoryUsed` | 获取 Mutable 生成纹理占用的 GPU 内存 | `UCustomizableObjectSystem` |
| `GetAverageBuildTime` | 获取平均构建时间（ms） | `UCustomizableObjectSystem` |
| `IsUpdating` | 检查指定实例是否正在更新 | `UCustomizableObjectSystem` |
| `SetWorkingMemory` | 设置工作内存限制（KB） | `UCustomizableObjectSystem` |
| `SetGenerateInstancesWithinRange` | 启用基于距离的实例生成 | `UCustomizableObjectSystem` |
| `SetInstanceGenerationRange` | 设置实例生成距离范围 | `UCustomizableObjectSystem` |
| `AddViewCenter` | 添加视图中心 Actor | `UCustomizableObjectSystem` |
| `RemoveViewCenter` | 移除视图中心 Actor | `UCustomizableObjectSystem` |
| `IsUpdateResultValid` | 判断更新结果是否有效（成功或有警告） | `UCustomizableObjectSystem` |

### 使用示例（蓝图描述）

**基本角色定制流程**：

1. **设置阶段**（BeginPlay）：
   - 从资产获取 `CustomizableObject` 引用
   - 调用 `CreateInstance` 创建 `UCustomizableObjectInstance`
   - 获取场景中的 `CustomizableSkeletalComponent`，调用 `SetCustomizableObjectInstance` 绑定实例

2. **修改参数**：
   - 根据 UI 选择调用 `SetIntParameterSelectedOption`（如发型=2）
   - 调用 `SetFloatParameterSelectedOption`（如肤色=0.7）
   - 调用 `SetBoolParameterSelectedOption`（如是否佩戴帽子=true）

3. **触发更新**：
   - 调用 `CustomizableSkeletalComponent` 的 `UpdateSkeletalMeshAsyncResult` 并绑定回调
   - 在回调中检查 `UpdateResult` 是否为 `Success`

4. **监听事件**：
   - 绑定 `UCustomizableObjectInstance` 的 `UpdatedDelegate` 在更新完成时收到通知

## C++ 用法

### 头文件引入

```cpp
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectInstance.h"
#include "MuCO/CustomizableObjectSystem.h"
#include "MuCO/CustomizableSkeletalComponent.h"
#include "MuCO/CustomizableSkeletalMeshActor.h"
#include "MuCO/CustomizableObjectInstanceUsage.h"
#include "MuCO/CustomizableObjectExtension.h"
```

### 基本用法

**创建实例并设置参数**（来源：`Public/MuCO/CustomizableObject.h` + `Public/MuCO/CustomizableObjectInstance.h`）：

```cpp
// 假设已经有一个编译好的 UCustomizableObject* MyCO
// 创建实例
UCustomizableObjectInstance* Instance = MyCO->CreateInstance();

// 设置整数参数（枚举类型，如发型选择）
Instance->SetIntParameterSelectedOption(TEXT("HairStyle"), TEXT("Mohawk"));

// 设置浮点参数
Instance->SetFloatParameterSelectedOption(TEXT("SkinTone"), 0.75f);

// 设置布尔参数
Instance->SetBoolParameterSelectedOption(TEXT("WearHat"), true);

// 设置颜色参数
Instance->SetColorParameterSelectedOption(TEXT("ShirtColor"), FLinearColor::Red);

// 设置投影器参数
Instance->SetProjectorPosition(TEXT("Tattoo"), FVector(100, 0, 50));
Instance->SetProjectorDirection(TEXT("Tattoo"), FVector(0, 0, -1));
Instance->SetProjectorScale(TEXT("Tattoo"), FVector(10, 10, 10));

// 设置状态
Instance->SetState(0);  // 或 SetCurrentState(TEXT("Combat"));
```

**异步更新实例**（来源：`Public/MuCO/CustomizableObjectInstance.h`）：

```cpp
// 异步更新并监听结果
Instance->UpdateSkeletalMeshAsync();

// 或使用回调版本
FInstanceUpdateDelegate Callback;
Callback.BindDynamic(this, &UMyClass::OnInstanceUpdated);
Instance->UpdateSkeletalMeshAsyncResult(Callback);

// 回调函数
void UMyClass::OnInstanceUpdated(const FUpdateContext& Result)
{
    if (Result.UpdateResult == EUpdateResult::Success)
    {
        UE_LOG(LogTemp, Log, TEXT("实例更新成功"));
    }
    else if (Result.UpdateResult == EUpdateResult::Error)
    {
        UE_LOG(LogTemp, Error, TEXT("实例更新失败"));
    }
}
```

**绑定事件**（来源：`Public/MuCO/CustomizableObjectInstance.h`）：

```cpp
// 监听实例更新完成（动态多播委托）
Instance->UpdatedDelegate.AddDynamic(this, &UMyClass::OnInstanceUpdatedDynamic);

// 监听实例更新完成（原生多播委托，性能更好）
Instance->UpdatedNativeDelegate.AddUObject(this, &UMyClass::OnInstanceUpdatedNative);

// 监听骨骼网格体设置前事件
Instance->PreSetSkeletalMeshNativeDelegate.AddUObject(this, &UMyClass::OnPreSetSkeletalMesh);
```

### 进阶用法

**使用 CustomizableSkeletalComponent 完整流程**（来源：`Public/MuCO/CustomizableSkeletalComponent.h`）：

```cpp
// 在 Actor 中
UCustomizableSkeletalComponent* SkelComp = FindComponentByClass<UCustomizableSkeletalComponent>();
if (SkelComp)
{
    // 绑定实例
    SkelComp->SetCustomizableObjectInstance(MyInstance);
    
    // 设置组件名（对应 CO 编辑器中定义的组件名）
    SkelComp->SetComponentName(FName("Body"));
    
    // 异步更新
    SkelComp->UpdateSkeletalMeshAsync();
    
    // 或带回调的异步更新
    FInstanceUpdateDelegate Callback;
    Callback.BindDynamic(this, &AMyCharacter::OnMeshUpdated);
    SkelComp->UpdateSkeletalMeshAsyncResult(Callback, false, true /* bForceHighPriority */);
}
```

**多层投影器**（来源：`Public/MuCO/MultilayerProjector.h` + `Public/MuCO/CustomizableObjectInstance.h`）：

```cpp
// 创建多层投影器层（用于纹理投影，如贴花系统）
FName ProjectorParamName = TEXT("Decals");
Instance->MultilayerProjectorCreateLayer(ProjectorParamName, 0);

// 设置层数据
FMultilayerProjectorLayer Layer;
Layer.Position = FVector(100, 50, 30);
Layer.Direction = FVector(0, 0, -1);
Layer.Up = FVector(0, 1, 0);
Layer.Scale = FVector(10, 10, 100);
Layer.Angle = 0.0f;
Layer.Image = TEXT("DecalTextureAssetPath");
Layer.Opacity = 1.0f;
Instance->MultilayerProjectorUpdateLayer(ProjectorParamName, 0, Layer);
```

**系统级配置**（来源：`Public/MuCO/CustomizableObjectSystem.h`）：

```cpp
UCustomizableObjectSystem* System = UCustomizableObjectSystem::GetInstance();

// 设置工作内存限制（降低内存压力，但可能增加更新次数）
System->SetWorkingMemory(256 * 1024); // 256 MB

// 启用基于距离的生成
System->SetGenerateInstancesWithinRange(true);
System->SetInstanceGenerationRange(5000.0f); // 5000 单位范围

// 添加视图中心（通常绑定到玩家 Pawn）
System->AddViewCenter(GetWorld()->GetFirstPlayerController()->GetPawn());

// 查询状态
int32 NumInstances = System->GetNumInstances();
int32 NumPending = System->GetNumPendingInstances();
int64 TextureMem = System->GetTextureMemoryUsed();
```

**烘焙实例**（仅编辑器，来源：`Public/MuCO/CustomizableObjectInstance.h`）：

```cpp
#if WITH_EDITOR
FBakingConfiguration BakeConfig;
BakeConfig.OutputPath = TEXT("/Game/BakedCharacters");
BakeConfig.OutputFilesBaseName = TEXT("MyCharacter");
BakeConfig.bExportAllResourcesOnBake = true;
BakeConfig.bGenerateConstantMaterialInstancesOnBake = true;

// 注册回调
BakeConfig.OnBakeOperationCompletedCallback.BindDynamic(
    this, &UMyClass::OnBakeCompleted);

// 执行烘焙
Instance->Bake(BakeConfig);

// 回调
void UMyClass::OnBakeCompleted(const FCustomizableObjectInstanceBakeOutput& Output)
{
    if (Output.bWasBakeSuccessful)
    {
        for (const FBakedResourceData& Data : Output.SavedPackages)
        {
            UE_LOG(LogTemp, Log, TEXT("烘焙保存: %s (%s)"), 
                *Data.AssetPath, *Data.Prefix);
        }
    }
}
#endif
```

**编译 CustomizableObject**（来源：`Internal/MuCO/ICustomizableObjectEditorModule.h` + `Public/MuCO/CustomizableObject.h`）：

```cpp
FCompileParams Params;
Params.bAsync = true;
Params.bSkipIfCompiled = true;
Params.bSkipIfNotOutOfDate = true;

// 使用回调
Params.CallbackNative.BindLambda([](const FCompileCallbackParams& Result)
{
    if (Result.bRequestFailed)
    {
        UE_LOG(LogTemp, Error, TEXT("编译失败"));
    }
    else if (Result.bCompiled)
    {
        UE_LOG(LogTemp, Log, TEXT("编译成功"));
    }
});

// 获取编辑器模块并编译
ICustomizableObjectEditorModule& EditorModule = ICustomizableObjectEditorModule::GetChecked();
EditorModule.CompileCustomizableObject(MyCO, &Params, false, false);
```

## Demo 示例

**最小角色定制 Actor**：

```cpp
// MyCharacter.h
#pragma once

#include "GameFramework/Character.h"
#include "MuCO/CustomizableObjectInstance.h"
#include "MyCharacter.generated.h"

class UCustomizableSkeletalComponent;

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Customization")
    TObjectPtr<UCustomizableObject> CustomizableObjectAsset;

    UPROPERTY(BlueprintReadWrite, Category = "Customization")
    TObjectPtr<UCustomizableObjectInstance> CustomizableInstance;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Customization")
    TObjectPtr<UCustomizableSkeletalComponent> CustomizableComponent;

    UFUNCTION(BlueprintCallable, Category = "Customization")
    void ApplyCustomization();

private:
    UFUNCTION()
    void OnMeshUpdated(const FUpdateContext& Result);
};
```

```cpp
// MyCharacter.cpp
#include "MyCharacter.h"
#include "MuCO/CustomizableSkeletalComponent.h"
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectSystem.h"

AMyCharacter::AMyCharacter()
{
    CustomizableComponent = CreateDefaultSubobject<UCustomizableSkeletalComponent>(
        TEXT("CustomizableComponent"));
    CustomizableComponent->SetupAttachment(GetMesh());
}

void AMyCharacter::ApplyCustomization()
{
    if (!CustomizableObjectAsset || !CustomizableObjectAsset->IsCompiled())
    {
        UE_LOG(LogTemp, Warning, TEXT("Customizable Object 未就绪"));
        return;
    }

    // 创建实例
    CustomizableInstance = CustomizableObjectAsset->CreateInstance();

    // 设置默认参数
    CustomizableInstance->SetIntParameterSelectedOption(TEXT("HairStyle"), TEXT("Short"));
    CustomizableInstance->SetFloatParameterSelectedOption(TEXT("SkinTone"), 0.5f);

    // 绑定到组件
    CustomizableComponent->SetCustomizableObjectInstance(CustomizableInstance);
    CustomizableComponent->SetComponentName(FName("Character"));

    // 注册回调并触发异步更新
    FInstanceUpdateDelegate Delegate;
    Delegate.BindDynamic(this, &AMyCharacter::OnMeshUpdated);
    CustomizableComponent->UpdateSkeletalMeshAsyncResult(Delegate);
}

void AMyCharacter::OnMeshUpdated(const FUpdateContext& Result)
{
    if (UCustomizableObjectSystem::IsUpdateResultValid(Result.UpdateResult))
    {
        UE_LOG(LogTemp, Log, TEXT("角色网格体更新完成"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("角色网格体更新失败: %d"), 
            static_cast<int32>(Result.UpdateResult));
    }
}
```

## 模块依赖

该插件包含 5 个模块，以下是**独特依赖**（不含 Core/Engine/Slate 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `DerivedDataCache` | Mutable 编译数据的派生数据缓存（DDC） |
| `MessageLog` | 编译过程中的消息日志输出 |
| `MutableRuntime` | Mutable 核心运行时库（网格体/纹理生成引擎） |
| `MutableTools` | Mutable 编辑器编译工具 |
| `RenderCore` | 渲染数据操作（LOD/顶点缓冲区） |
| `SkeletalMeshDescription` | 骨骼网格体数据描述与转换 |
| `ClothingSystemRuntimeCommon` | 布料模拟数据处理 |
| `PhysicsCore` | 物理资产合并 |

**使用者最少需要依赖**：`CustomizableObject`（Runtime 模块）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复同名多个骨骼网格体导致的几何体重复问题 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复 UV 遮罩裁剪网格操作未加载正确 mipmap 级别 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. An incorrect LODBias | 修复纹理参数计算 LODBias 的方法错误 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用 ClothingAssetBase 接口支持更多布料资产类型 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较 PassthroughObjects 时可能出现的数据竞争 |

### 维护评价

- **状态**：**活跃维护中**。该插件在 2024 年 9 月从 Experimental 迁移至 Beta 状态，近期（2025-2026 年）持续有高质量的 bug 修复和功能改进
- **更新频率**：密集，几乎每日都有提交，涉及网格体、纹理、布料、物理等多个子系统
- **代码规模**：超大插件（1206 个源文件），架构成熟，有完善的测试覆盖
- **版本号**：1.8.0，表明经过长期迭代
- **已知限制**：
  - 仍为 Beta 状态（`IsBetaVersion=true`），可能有 API 变更
  - 编译 CO 需要一定时间，且内存占用较高
  - 大型 CO 的编译结果体积可能较大
- **推荐使用**：✅ **强烈推荐**。如果你的项目需要运行时角色/物体定制系统，这是 UE5 官方提供的最成熟方案。虽然是 Beta，但已被多个 AAA 项目在生产中使用。需注意该插件默认未启用，需在 Plugins 面板中手动激活。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/CustomizableObjectsAndTextures/index.html)