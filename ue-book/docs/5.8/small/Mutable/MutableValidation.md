# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可变对象系统 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时、工具、编辑器模块） |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime), `CustomizableObjectEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是 UE5 中用于创建高度可定制化、动态组合游戏资产（尤其是角色和装备）的系统。它解决的核心问题是：如何在运行时，通过有限的美术资产（基础模型、纹理、材质片段）进行组合、混合和修改，生成几乎无限的、多样化的外观变体，同时保持良好的运行时性能和较低的内存占用。

传统方式下，每个角色变体都需要一个独立的完整资源（SK Mesh + Textures），导致项目资产庞大、管理困难。Mutable 通过一个可定制的对象蓝图（Customizable Object）定义所有可能的部件、纹理、材质等的组合关系和修改规则，然后在运行时根据参数（如是否戴头盔、肤色、装备等级）动态“烘焙”出最终的、优化的网格体和纹理，替代了静态的预烘焙资产。

## 使用场景

- **角色定制系统**：在MMORPG或RPG中，允许玩家自由组合发型、面部特征、盔甲、武器等部件。
- **装备外观组合**：实现装备的部件化，不同部位装备可以独立更换，并且共享基础纹理。
- **NPC 变体生成**：为大量NPC快速生成差异化外观，避免重复劳动。
- **美术资产调试与迭代**：在编辑器中快速预览不同材质参数、纹理组合的效果，加速美术流程。
- **性能优化**：运行时只生成可见部分的完整资源，减少内存消耗。

## 蓝图用法

Mutable 的核心蓝图交互围绕 `UCustomizableObject` 和 `UCustomizableObjectInstance` 展开。用户主要在编辑器中通过专用编辑器（CustomizableObjectEditor）设计可定制对象的逻辑图，然后在运行时通过蓝图或 C++ 修改实例参数来生成最终外观。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UpdateSkeletalMeshAsync` | 异步更新可定制对象实例的网格体。这是生成最终可视化结果的核心异步操作。 | `UCustomizableObjectInstance` |
| `SetBoolParameterByName` | 通过名称设置实例的布尔参数值（如是否显示头盔）。 | `UCustomizableObjectInstance` |
| `SetIntParameterByName` | 通过名称设置实例的整型参数值（如选择发型编号）。 | `UCustomizableObjectInstance` |
| `SetFloatParameterByName` | 通过名称设置实例的浮点参数值（如颜色强度）。 | `UCustomizableObjectInstance` |
| `SetVectorParameterByName` | 通过名称设置实例的向量参数值（如颜色）。 | `UCustomizableObjectInstance` |
| `SetProjectorPosition` | 设置实例投影器的位置，用于动态贴花或纹理投射。 | `UCustomizableObjectInstance` |
| `Compile` | 编辑器专用，编译 CustomizableObject 资源，生成运行时所需的中间数据。 | `UCustomizableObject` |

**注意**：`MutableValidation` 模块提供的 `UCustomizableObjectValidationCommandlet` 等类主要用于资产验证和批量测试，通常不直接暴露为游戏逻辑蓝图节点。

### 使用示例（蓝图描述）

1.  **创建可定制对象资产**：在内容浏览器中右键创建 `CustomizableObject` 资源。双击打开专用编辑器，通过节点图定义模型部件、纹理、材质以及它们的组合逻辑。
2.  **生成实例**：在游戏蓝图中，使用 `Create Customizable Object Instance` 节点基于上一步创建的资产生成一个实例。
3.  **设置参数并更新**：
    - 使用 `Set Bool Parameter By Name` (参数名 “HasHelmet”) 设为 `True`。
    - 使用 `Set Int Parameter By Name` (参数名 “HairStyle”) 设为 `2`。
    - 调用 `Update Skeletal Mesh Async` 节点，该节点会触发异步编译和烘焙过程。
4.  **获取结果**：`Update Skeletal Mesh Async` 节点完成后会有一个 `Completed` 输出引脚，通常你会将其连接到一个处理完成回调的逻辑，比如将生成的 `Skeletal Mesh` 赋值给一个 `Skeletal Mesh Component` 用于显示。

## C++ 用法

### 头文件引入

```cpp
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectInstance.h"
#include "MuCO/CustomizableObjectSystem.h"
```

### 基本用法

从测试和验证代码中提取的用法示例，展示了如何编译一个可定制对象并更新其实例。

```cpp
// 来源: Private/MuV/CustomizableObjectCompilationUtility.h & ValidationUtils.h

// 同步编译一个可定制对象（常用于编辑器工具或测试中）
UCustomizableObject* MyCO = LoadObject<UCustomizableObject>(nullptr, TEXT("/Game/Characters/BP_CharCustom"));
if (MyCO)
{
    // 使用编译工具辅助类进行同步编译
    FCustomizableObjectCompilationUtility CompilationHelper;
    bool bCompileSuccess = CompilationHelper.CompileCustomizableObject(*MyCO, true /*bShouldLogMutableLogs*/);
    
    if (bCompileSuccess)
    {
        // 创建实例并设置参数
        UCustomizableObjectInstance* Instance = MyCO->CreateInstance();
        Instance->SetBoolParameterByName(FName("HasHelmet"), true);
        
        // 使用实例更新工具辅助类进行同步更新（用于测试/基准）
        FCustomizableObjectInstanceUpdateUtility UpdateHelper;
        bool bUpdateSuccess = UpdateHelper.UpdateInstance(*Instance);
        
        if (bUpdateSuccess)
        {
            // 获取生成的骨骼网格体
            USkeletalMesh* GeneratedMesh = Instance->GetSkeletalMesh();
            // 将其应用于组件...
        }
    }
}
```

### 进阶用法

结合验证工具，对资产进行批量或自动化测试。

```cpp
// 来源: Private/MuV/ValidationUtils.h & AssetValidator_CustomizableObjects.h

// 1. 准备资产注册表（命令行工具中常见）
void PrepareAssetRegistry(); // 声明于 ValidationUtils.h

// 2. 查找所有可定制对象资产
TArray<FAssetData> COAssets = FindAllAssetsAtPath(FName("/Game/Characters"), UCustomizableObject::StaticClass());

// 3. 逐一进行验证测试（模拟资产验证器行为）
for (const FAssetData& AssetData : COAssets)
{
    UCustomizableObject* CO = Cast<UCustomizableObject>(AssetData.GetAsset());
    if (CO)
    {
        TArray<FText> Errors, Warnings;
        // 使用静态验证方法检查对象有效性
        EDataValidationResult Result = UAssetValidator_CustomizableObjects::IsCustomizableObjectValid(CO, Errors, Warnings);
        
        if (Result == EDataValidationResult::Invalid)
        {
            // 记录错误日志...
        }
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 类，演示如何封装一个可定制的对象实例及其异步更新逻辑。

**MyCharacterCustomizationComponent.h**
```cpp
// MyCharacterCustomizationComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "MuCO/CustomizableObjectInstance.h"
#include "MyCharacterCustomizationComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UMyCharacterCustomizationComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyCharacterCustomizationComponent();

    // 要使用的可定制对象资产引用
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Customization")
    UCustomizableObject* CustomizableObjectAsset;

    // 当前实例
    UPROPERTY(BlueprintReadOnly, Category = "Customization")
    UCustomizableObjectInstance* CurrentInstance;

    // 异步更新实例外观
    UFUNCTION(BlueprintCallable, Category = "Customization")
    void UpdateCharacterAppearance();

protected:
    virtual void BeginPlay() override;

private:
    // 更新完成的回调
    UFUNCTION()
    void OnUpdateCompleted(bool bSuccess);

    // 用于显示生成网格体的骨骼网格体组件
    UPROPERTY()
    USkeletalMeshComponent* TargetMeshComponent;
};
```

**MyCharacterCustomizationComponent.cpp**
```cpp
// MyCharacterCustomizationComponent.cpp
#include "MyCharacterCustomizationComponent.h"
#include "MuCO/CustomizableObjectSystem.h"
#include "Components/SkeletalMeshComponent.h"

UMyCharacterCustomizationComponent::UMyCharacterCustomizationComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyCharacterCustomizationComponent::BeginPlay()
{
    Super::BeginPlay();

    if (CustomizableObjectAsset)
    {
        // 创建实例
        CurrentInstance = CustomizableObjectAsset->CreateInstance();

        // 找到目标网格体组件（假设在同一个Actor上）
        TargetMeshComponent = GetOwner()->FindComponentByClass<USkeletalMeshComponent>();

        // 设置初始参数（示例）
        CurrentInstance->SetBoolParameterByName(FName("bIsFemale"), false);
        CurrentInstance->SetIntParameterByName(FName("SkinTone"), 3);

        // 启动首次更新
        UpdateCharacterAppearance();
    }
}

void UMyCharacterCustomizationComponent::UpdateCharacterAppearance()
{
    if (CurrentInstance && CustomizableObjectAsset)
    {
        // 绑定更新完成回调
        FOnUpdateContextDelegate OnUpdateDelegate;
        OnUpdateDelegate.BindDynamic(this, &UMyCharacterCustomizationComponent::OnUpdateCompleted);
        CurrentInstance->UpdatedDelegate.Add(OnUpdateDelegate);

        // 发起异步更新
        CurrentInstance->UpdateSkeletalMeshAsync();
    }
}

void UMyCharacterCustomizationComponent::OnUpdateCompleted(bool bSuccess)
{
    // 解绑回调
    CurrentInstance->UpdatedDelegate.RemoveAll(this);

    if (bSuccess && TargetMeshComponent)
    {
        // 将生成的网格体设置到目标组件
        USkeletalMesh* GeneratedMesh = CurrentInstance->GetSkeletalMesh();
        TargetMeshComponent->SetSkeletalMesh(GeneratedMesh);
        
        UE_LOG(LogTemp, Log, TEXT("Character customization updated successfully."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Character customization update failed."));
    }
}
```

## 模块依赖

从 `CustomizableObject.Build.cs` 分析，要使用 Mutable 的核心运行时功能，你的项目模块需要依赖以下**特殊模块**：

| 模块 | 用途 |
|---|---|
| `MutableRuntime` | Mutable 的核心运行时库，处理实例的动态生成。 |
| `MutableTools` | 提供编辑器和工具链所需的资产处理、编译功能。 |
| `CustomizableObject` | 封装了 `UCustomizableObject` 和 `UCustomizableObjectInstance` 等核心资产类。 |
| `DerivedDataCache` | Mutable 编译过程需要与引擎的 DDC 系统交互。 |
| `UnrealEd` | 编辑器集成（仅编辑器/开发工具模块需要）。 |
| `MessageLog` | 用于在编辑器中显示编译警告和错误消息。 |

**注意**：`CustomizableObjectEditor` 和 `MutableValidation` 是编辑器专用模块，一般无需在游戏运行时模块中直接依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复存在多个同名骨骼网格体时几何体重复的 bug。 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复“使用UV遮罩裁剪网格”操作未加载正确遮罩Mip的问题。 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. An incorrect LODBias | 修复纹理参数计算LODBias方法错误的问题。 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用ClothingAssetBase接口，允许更多类型的服装资产。 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较PassthroughObjects时可能发生的竞态条件。 |

### 维护评价

**维护状态：活跃维护**。
- Mutable 插件于 **2024年9月** 从实验状态移至 Beta 状态，表明其功能趋于稳定。
- **最近更新非常活跃**（截至2026年5月底仍有密集的 bug 修复提交），表明 Epic 团队正在积极维护和改进该插件。
- 主要更新集中在 **Bug 修复** 和 **兼容性改进**（如支持更多服装资产类型），未见功能性废弃标记。
- 该插件是 UE5 中处理动态资产定制的**核心官方解决方案**，推荐在需要高级角色/装备定制系统的项目中使用。
- **重要提示**：该插件的 `.uplugin` 中可能未设置 `EnabledByDefault=true`，且依赖关系较复杂。在项目中启用时，需要仔细阅读官方集成指南，并确保编辑器和目标平台的正确配置。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/mutable-plugin-in-unreal-engine/) (链接基于插件类别推测，实际文档请参考 UE 官方发布说明)