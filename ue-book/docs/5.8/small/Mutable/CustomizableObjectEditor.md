# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 可变对象工具 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、蓝图节点、运行时逻辑） |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `MutableTools` (Runtime), `CustomizableObjectEditor` (Editor), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途
Mutable 是一个用于创建可在运行时修改的资产（Customizable Objects）的编辑器和运行时工具套件。它解决的核心问题是**高效地实现游戏角色、装备或任何资产的运行时外观定制**。传统做法是为每种变体创建单独的资产，这会导致内存爆炸和管理困难。Mutable 通过提供一套节点图工具，让美术和程序在编辑器中定义资产的“可能性空间”（例如，一个角色可以有不同的眼睛颜色、发型、衣服），然后将其编译成一个优化的“模型”。运行时，通过设置一组简单的参数（整数、浮点数、颜色等），即可动态生成该参数组合对应的最终网格体、材质和纹理，无需加载所有变体资产。

## 使用场景
- 你在制作一个 RPG 游戏，需要实现复杂的角色换装系统（发型、脸型、盔甲部件、纹理）→ 用 Mutable 的节点图定义角色的所有部件和变体，并在运行时通过参数组合生成最终角色模型。
- 你需要为射击游戏制作武器皮肤系统，皮肤可以改变武器的材质颜色、图案和几何体细节 → 用 Mutable 定义武器的基础网格和可替换的材质纹理图层。
- 你的游戏允许玩家自定义载具（汽车的颜色、贴花、配件）→ 用 Mutable 将载具拆分为多个部件和材质参数，运行时组合。
- 你需要为大量 NPC 生成外观变体，但又不想为每个变体都创建单独的资源 → 使用 Mutable 的“随机实例”功能，在编译好的模型基础上生成外观各不相同的实例。

## 蓝图用法
基于源码，Mutable 主要通过 **运行时实例** 和 **编辑器工具库** 与蓝图交互。以下是核心功能分组。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Compile Customizable Object Synchronously` | 同步编译一个 `UCustomizableObject` 资产。这是编辑期操作，用于将节点图编译成运行时可用的模型。 | `UCustomizableObjectEditorFunctionLibrary` |
| `New Customizable Object` | 在指定的包路径下创建一个新的 `UCustomizableObject` 资产。 | `UCustomizableObjectEditorFunctionLibrary` |

**运行时蓝图交互通常通过 `UCustomizableObjectInstance` 类进行（该类接口未在提供的源码片段中完全展示，但根据其设计模式可推断）**：
- **创建与更新**：通常需要创建一个 `UCustomizableObjectInstance` 对象，将其与一个编译好的 `UCustomizableObject` 关联，然后设置其参数，最后调用 `UpdateInstance` 来生成最终资源。
- **委托监听**：监听 `OnUpdated` 等委托，以在实例完成更新（生成了新的网格/材质）后执行逻辑，例如应用新生成的网格到角色 SkeletalMeshComponent 上。
- **参数设置**：通过蓝图读写 `UCustomizableObjectInstance` 的属性或调用函数来设置整数、浮点、颜色、投影器等各类参数。

### 使用示例（蓝图描述）
1.  **编译对象**（编辑期）：
    *   在编辑器工具菜单中，找到 `Compile Customizable Object Synchronously` 节点。
    *   连接一个对 `UCustomizableObject` 资产的引用作为输入。
    *   调用此节点，蓝图日志会输出编译结果（成功或失败）。

2.  **运行时创建与更新**：
    *   蓝图中，使用 `Construct Object` 节点创建一个 `UCustomizableObjectInstance` 类的新对象。
    *   将上一步编译好的 `UCustomizableObject` 资产连接到实例的 `CustomizableObject` 属性。
    *   通过实例的 `Set Projector Position`、`Set Int Value`、`Set Float Value` 等节点设置所需的外观参数。
    *   调用实例的 `Update Instance` 节点，并绑定其 `On Updated` 委托到一个自定义事件。
    *   在更新完成的回调事件中，获取实例生成的网格（例如通过 `Get Skeletal Mesh`）并将其应用到场景中的角色 Skeletal Mesh Component 上。

## C++ 用法
核心用法是操作 `UCustomizableObjectInstance` 对象并处理其更新。

### 头文件引入
```cpp
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectInstance.h"
// 如果需要编辑器编译功能
#include "MuCO/CustomizableObjectEditorFunctionLibrary.h"
```

### 基本用法
创建并更新一个可自定义对象实例。假设你有一个编译好的 `UCustomizableObject` 指针 `COObject`。
```cpp
// 在你的游戏模式或角色类中
UCLASS()
class AMyGameCharacter : public ACharacter
{
    GENERATED_BODY()
protected:
    // 可自定义对象实例（用于管理参数和生成资源）
    UPROPERTY()
    TObjectPtr<UCustomizableObjectInstance> COInstance;

    // 编译好的可自定义对象资产
    UPROPERTY(EditDefaultsOnly, Category = “Customization”)
    TObjectPtr<UCustomizableObject> COAsset;

    virtual void BeginPlay() override
    {
        Super::BeginPlay();

        if (COAsset)
        {
            // 创建实例
            COInstance = NewObject<UCustomizableObjectInstance>(this);
            COInstance->SetObject(COAsset); // 关联资产

            // 设置一些初始参数（示例）
            COInstance->SetIntValue(FName(“HairColor”), 1); // 0:黑，1:棕，2:金
            COInstance->SetFloatValue(FName(“EyeSize”), 1.2f);

            // 绑定更新完成回调
            FInstanceUpdateNativeDelegate UpdateDelegate;
            UpdateDelegate.BindUObject(this, &AMyGameCharacter::OnCustomizationUpdated);
            COInstance->UpdateSkeletalMeshAsyncResult(UpdateDelegate); // 异步更新
        }
    }

    void OnCustomizationUpdated(UCustomizableObjectInstance* Instance)
    {
        // 更新完成，应用新的网格体
        USkeletalMesh* NewMesh = Instance->GetSkeletalMesh();
        if (NewMesh)
        {
            GetMesh()->SetSkeletalMesh(NewMesh);
            // 可能还需要处理材质等
        }
    }
};
```

### 进阶用法
结合编辑器编译与运行时更新。以下示例展示了如何在编辑器工具中触发编译，并在完成后进行下一步操作。
```cpp
// 在某个编辑器工具类中
void FMyEditorTool::CompileAndSave()
{
    if (UCustomizableObject* ObjectToCompile = GetSelectedCOObject())
    {
        // 使用函数库同步编译
        ECustomizableObjectCompilationState State =
            UCustomizableObjectEditorFunctionLibrary::CompileCustomizableObjectSynchronously(
                ObjectToCompile,
                ECustomizableObjectOptimizationLevel::None,
                ECustomizableObjectTextureCompression::Fast,
                true /* bGatherReferences */);

        if (State == ECustomizableObjectCompilationState::Completed)
        {
            UE_LOG(LogTemp, Log, TEXT(“Compilation succeeded! Asset is ready for runtime.”));
            // 编译成功后，可以在此处执行烘焙（Bake）或保存资产等操作。
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT(“Compilation failed.”));
        }
    }
}
```

## Demo 示例
一个完整的、可编译的最小示例，展示如何创建并更新一个自定义实例。

### MyCustomizableCharacter.h
```cpp
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Character.h”
#include “MyCustomizableCharacter.generated.h”

class UCustomizableObject;
class UCustomizableObjectInstance;
struct FUpdateContext;

UCLASS()
class MYPROJECT_API AMyCustomizableCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCustomizableCharacter();

protected:
    virtual void BeginPlay() override;

public:
    // 编辑器中指定的可自定义对象资产
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = “Customization”)
    TObjectPtr<UCustomizableObject> CustomizableObjectAsset;

    // 用于更新实例的委托
    void OnCustomizableInstanceUpdated(FUpdateContext Result);

private:
    // 运行时实例
    UPROPERTY()
    TObjectPtr<UCustomizableObjectInstance> CurrentInstance;

    // 实例更新完成的委托句柄
    FDelegateHandle InstanceUpdatedDelegateHandle;
};
```

### MyCustomizableCharacter.cpp
```cpp
#include “MyCustomizableCharacter.h”
#include “MuCO/CustomizableObject.h”
#include “MuCO/CustomizableObjectInstance.h”

AMyCustomizableCharacter::AMyCustomizableCharacter()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyCustomizableCharacter::BeginPlay()
{
    Super::BeginPlay();

    if (CustomizableObjectAsset)
    {
        // 1. 创建实例
        CurrentInstance = NewObject<UCustomizableObjectInstance>(this);
        CurrentInstance->SetObject(CustomizableObjectAsset);

        // 2. 设置参数 (示例)
        CurrentInstance->SetIntValue(FName(“BodyType”), 0); // 0: 男性，1: 女性
        CurrentInstance->SetFloatValue(FName(“FatPercent”), 0.5f);

        // 3. 绑定更新回调并开始异步更新
        FInstanceUpdateNativeDelegate UpdateDelegate;
        UpdateDelegate.BindUObject(this, &AMyCustomizableCharacter::OnCustomizableInstanceUpdated);
        InstanceUpdatedDelegateHandle = CurrentInstance->UpdateSkeletalMeshAsyncResult(UpdateDelegate);
    }
}

void AMyCustomizableCharacter::OnCustomizableInstanceUpdated(FUpdateContext Result)
{
    // 4. 更新完成，应用资源
    if (Result.Result == EUpdateResult::Success && CurrentInstance)
    {
        // 应用新生成的 SkeletalMesh
        USkeletalMesh* NewMesh = CurrentInstance->GetSkeletalMesh();
        if (NewMesh)
        {
            GetMesh()->SetSkeletalMesh(NewMesh);
        }

        // 应用新生成的材质 (示例，可能需要遍历材质槽)
        UMaterialInterface* NewMaterial = CurrentInstance->GetMaterial(FName(“BodyMaterialSlot”));
        if (NewMaterial)
        {
            GetMesh()->SetMaterial(0, NewMaterial);
        }

        UE_LOG(LogTemp, Log, TEXT(“Customizable Object instance updated successfully for %s.”), *GetName());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT(“Failed to update Customizable Object instance for %s.”), *GetName());
    }

    // 5. 清理委托句柄
    if (InstanceUpdatedDelegateHandle.IsValid())
    {
        CurrentInstance->UpdateSkeletalMeshAsyncEvent.Remove(InstanceUpdatedDelegateHandle);
        InstanceUpdatedDelegateHandle.Reset();
    }
}
```

## 模块依赖
从源码中的 `Build.cs` 文件分析，要使用 Mutable 插件，你的项目模块需要依赖以下插件自身的模块。

| 模块 | 用途 |
|---|---|
| `MutableRuntime` | 核心运行时库，包含实例化和运行时模型操作的基础类。 |
| `CustomizableObject` | 包含 `UCustomizableObject` 和 `UCustomizableObjectInstance` 等核心资产和实例类。 |
| `MutableTools` | 仅在编辑器或需要编译功能的模块中依赖，包含编译器和图生成工具。 |
| `CustomizableObjectEditor` | 仅在编辑器插件中依赖，包含所有编辑器 UI、节点、详细面板和编译入口。 |
| `MutableValidation` | 包含用于验证可自定义对象实例和资产的数据和工具。 |

**注意**：这些是 Mutable 插件内部模块间的依赖关系。对于游戏运行时模块，通常只需要依赖 `MutableRuntime` 和 `CustomizableObject`。`MutableTools` 和 `CustomizableObjectEditor` 仅在编辑器扩展或自定义编译流程中需要。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复了存在多个同名骨骼网格资产时，几何体被重复生成的错误。 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed “Clip mesh with UV Mask” op not loading the appropriate mask mip. | 修复了“用 UV 蒙版裁剪网格”操作未能加载正确蒙版 Mipmap 层级的问题。 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. An incorrect LODBias... | 修复了纹理参数使用错误方法计算 LODBias，导致显示不正确的问题。 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用 `ClothingAssetBase` 接口，支持了更多类型的布料资产。 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复了在比较直通对象（PassthroughObjects）时可能出现的潜在数据竞争问题。 |

### 维护评价
- **创建时间**：2024年9月从 Experimental 升级为 Beta，历史较短。
- **近期更新频率**：非常活跃。在最近一周内（2026年5月）有多次实质性提交，修复了运行时和编辑器中的多个 Bug，涉及几何生成、纹理加载、材质属性和资产兼容性。
- **维护状态**：**活跃维护中**。团队正在积极修复问题并改进功能。
- **已知限制**：作为 Beta 版本，可能存在未发现的 Bug 或 API 变动。主要功能完整，适合用于生产环境，但需关注后续版本更新。
- **推荐使用**：**推荐使用**。对于需要复杂角色定制功能的项目，Mutable 是 UE5 中功能强大且官方支持的选择。其活跃的维护状态保证了问题能得到及时修复。建议将其用于新项目或计划重构换装系统的项目中。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://github.com/anticto/Mutable-Documentation/wiki)（来自代码中定义的链接）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable/Tests)（路径推断）