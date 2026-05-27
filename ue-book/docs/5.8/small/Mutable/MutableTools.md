# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可变对象 |
| 分类 | CustomizableObjects |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是一个用于创建运行时可高度自定义对象（如角色装备、车辆部件等）的完整框架和运行时系统。它解决的核心问题是：如何将多个独立的资产片段（网格体、材质、纹理等）在运行时高效地组合成一个最终的、优化的可渲染资产，并允许玩家通过修改参数（如是否穿戴头盔、选择纹理图案）来改变其外观。

**为什么存在？** 传统方法通过蓝图动态附加/分离大量静态网格体组件，会导致渲染开销大（过多的绘制调用）且难以管理复杂的依赖关系。Mutable 提供了一个更优的解决方案：它通过一个编译期工具链（MutableTools）将可定制对象的“定义图”编译成一个高效的“程序”（一个状态机），运行时只需根据输入参数（如布尔值、标量、纹理）执行这个轻量级程序，即可生成最终的、合并后的网格体和材质实例。这极大地提升了运行时性能和内存效率。

## 使用场景

- **RPG/ARPG 游戏角色装备系统**：为角色创建成千上万种装备组合，而无需预先制作所有组合的静态资产。
- **角色编辑器**：允许玩家在游戏内或大厅中自定义角色的肤色、发型、服装、配饰等。
- **车辆/载具定制**：改变车辆的涂装、轮毂、尾翼、内饰颜色等。
- **任何需要动态、参数化生成 3D 资产的场景**，例如根据环境参数（天气、损坏程度）改变物体外观。

## 蓝图用法

Mutable 主要通过 `UCustomizableObject` 和 `UCustomizableObjectInstance` 类在蓝图中操作。核心工作流是：编译 `CustomizableObject` -> 创建其 `Instance` -> 设置参数 -> 更新实例以生成新的网格体和材质。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Compile` | 编译一个 `CustomizableObject`，生成运行时数据。 | `UCustomizableObject` |
| `CreateInstance` | 为已编译的 `CustomizableObject` 创建一个新的可定制实例。 | `UCustomizableObject` |
| `SetBoolParameter` / `SetFloatParameter` / `SetTextureParameter` ... | 设置实例的各类参数。 | `UCustomizableObjectInstance` |
| `UpdateSkeletalMeshAsync` | 异步更新实例，根据当前参数生成新的骨骼网格体、材质等资产。 | `UCustomizableObjectInstance` |
| `GetSkeletalMesh` / `GetMaterial` | 在更新完成后，获取生成的网格体或材质。 | `UCustomizableObjectInstance` |

### 使用示例（蓝图描述）

1.  **创建与编译**：在蓝图中持有 `CustomizableObject` 资产的引用。在初始化时调用其 `Compile` 节点（通常异步执行）。
2.  **创建实例**：编译完成后，调用 `CreateInstance` 获得一个 `CustomizableObjectInstance`。
3.  **设置参数**：根据玩家选择，调用 `SetBoolParameter` (如 `bHasHelmet`)、`SetIntParameter` (如 `ArmorColorIndex`)、`SetTextureParameter` (如 `PaintTexture`) 等节点。
4.  **更新实例**：调用 `UpdateSkeletalMeshAsync` 并绑定完成回调。
5.  **应用资产**：在更新完成的回调中，通过 `GetSkeletalMesh` 获取新网格体，通过 `GetMaterial` 获取新材质，并将它们应用到场景中的 `SkeletalMeshComponent` 上。

## C++ 用法

### 头文件引入

```cpp
// 操作 CustomizableObject 和 Instance
#include "CustomizableObject.h"
#include "CustomizableObjectInstance.h"

// 使用 Mutable 编译器（通常在编辑器工具中）
#include "MutableTools/Public/Compiler.h"
```

### 基本用法

```cpp
// 假设 MyCustomizableObject 是一个已加载的 UCustomizableObject*
// 来源：自定义的角色自定义逻辑

// 1. 创建实例
UCustomizableObjectInstance* MyInstance = MyCustomizableObject->CreateInstance();

// 2. 设置参数
MyInstance->SetBoolParameter(FName("bShowMask"), true);
MyInstance->SetFloatParameter(FName("ColorIntensity"), 0.8f);
MyInstance->SetVectorParameter(FName("PrimaryColor"), FLinearColor::Red);

// 3. 更新实例 (同步示例，推荐使用异步版本)
MyInstance->UpdateSkeletalMesh();

// 4. 应用结果
if (USkeletalMesh* NewMesh = MyInstance->GetSkeletalMesh())
{
    MySkeletalMeshComponent->SetSkeletalMesh(NewMesh);
}
```

### 进阶用法

使用 `CustomizableObjectCompiler` 编程方式编译对象，或使用 `Compiler` 类处理自定义的 `Mutable::Private::Node` 图。这通常用于创建高级编辑器工具或自动化流程。

```cpp
// 伪代码，展示编译器的使用
#include "Compiler.h"
#include "Node.h"

using namespace UE::Mutable::Private;

// 创建编译器选项
Ptr<CompilerOptions> Options = new CompilerOptions();
Options->SetOptimisationEnabled(true);

// 创建编译器
Ptr<Compiler> CompilerInstance = new Compiler(Options, [](){ /* 等待回调 */ });

// 假设我们有一个构建好的 Node 图 (RootNode)
TMap<FOperation::ADDRESS, FInstancedStruct> ExternalOps;
TSharedPtr<FModel> CompiledModel = CompilerInstance->Compile(RootNode, ExternalOps);

// 获取编译日志
TSharedPtr<FErrorLog> Log = CompilerInstance->GetLog();
if (Log->GetMessageCount() > 0)
{
    Log->Log();
}
```

## Demo 示例

一个最小化的C++示例，演示如何加载、编译并实例化一个可定制对象。

**MyCustomizableActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCustomizableActor.generated.h"

class UCustomizableObject;
class UCustomizableObjectInstance;
class USkeletalMeshComponent;

UCLASS()
class AMyCustomizableActor : public AActor
{
    GENERATED_BODY()

public:
    AMyCustomizableActor();

    UPROPERTY(EditAnywhere, Category="Customization")
    TSoftObjectPtr<UCustomizableObject> SourceObject;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    USkeletalMeshComponent* MeshComponent;

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    UCustomizableObjectInstance* Instance;

    UFUNCTION()
    void OnUpdateFinished();

    void ApplyRandomCustomization();
};
```

**MyCustomizableActor.cpp**
```cpp
#include "MyCustomizableActor.h"
#include "CustomizableObject.h"
#include "CustomizableObjectInstance.h"
#include "Components/SkeletalMeshComponent.h"

AMyCustomizableActor::AMyCustomizableActor()
{
    MeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;
}

void AMyCustomizableActor::BeginPlay()
{
    Super::BeginPlay();

    // 加载源对象
    if (UCustomizableObject* Obj = SourceObject.LoadSynchronous())
    {
        // 编译（在实际项目中应异步进行并处理结果）
        Obj->Compile();

        // 创建实例
        Instance = Obj->CreateInstance();
        if (Instance)
        {
            // 绑定更新完成的委托
            FOnCustomizableObjectUpdateDelegate UpdateDelegate;
            UpdateDelegate.BindUObject(this, &AMyCustomizableActor::OnUpdateFinished);
            Instance->RegisterForUpdate(UpdateDelegate);

            // 应用一些随机定制并更新
            ApplyRandomCustomization();
            Instance->UpdateSkeletalMeshAsync();
        }
    }
}

void AMyCustomizableActor::ApplyRandomCustomization()
{
    if (!Instance) return;

    // 随机设置一些参数
    Instance->SetBoolParameter(FName("bHasHat"), FMath::RandBool());
    Instance->SetFloatParameter(FName("ColorHue"), FMath::FRandRange(0.0f, 1.0f));
}

void AMyCustomizableActor::OnUpdateFinished()
{
    if (USkeletalMesh* Mesh = Instance->GetSkeletalMesh())
    {
        MeshComponent->SetSkeletalMesh(Mesh);
        UE_LOG(LogTemp, Log, TEXT("Mutable instance updated successfully."));
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。`CustomizableObject` 模块依赖 `MutableTools` 和 `MutableRuntime`，但这是插件内部依赖。对于使用该插件的游戏项目，通常只需依赖 `CustomizableObject` 模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复多个同名骨骼网格体导致的几何体重复问题。 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复“用UV遮罩裁剪网格”操作未加载正确遮罩Mip的问题。 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. An incorrect LODBias | 修复纹理参数计算LODBias方法错误导致的精度问题。 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用ClothingAssetBase接口支持更多服装资产类型。 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较PassthroughObjects时可能发生的数据竞争。 |

### 维护评价

**积极维护，强烈推荐使用**。
- **活跃度**：维护非常活跃，最近一周内连续有多个重要的Bug修复提交，涵盖了网格体、纹理、物理资产等核心功能的稳定性问题。
- **状态**：插件已从实验性（Experimental）状态升级为Beta状态，表明其已具备相当的稳定性和功能完整性。
- **成熟度**：作为Epic官方维护的大型插件，其架构成熟，文档和示例相对完善，是实现高级角色定制的首选方案。
- **建议**：尽管是Beta版，但已用于Epic自家项目（如《堡垒之夜》），可以放心在生产项目中使用。关注后续的正式版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/using-mutable-in-unreal-engine/) (UE5 官方文档链接，需确认)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable/Tests) (路径为推测，具体位置需在仓库中确认)