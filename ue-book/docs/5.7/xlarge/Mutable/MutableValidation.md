# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 分类 | CustomizableObjects |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime), `CustomizableObjectEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Mutable) | |

## 用途

Mutable 是 Epic Games 开发的**可定制对象系统**，用于在游戏中创建高度可定制的角色、装备和物品。它解决的核心问题是：当游戏中存在大量外观变体（如角色捏脸、装备染色、武器皮肤组合）时，传统方式需要为每种组合创建独立资产，导致内存爆炸和工作流低效。

Mutable 通过**编译时图（Graph）系统**将可定制对象定义为一组参数化规则，运行时根据参数动态生成最终的 SkeletalMesh / StaticMesh，实现：

- **内存高效**：共享基础网格，仅存储差异数据
- **流式加载**：按需生成 LOD 和纹理区域
- **参数化组合**：支持布尔开关、整数枚举、浮点范围、颜色、纹理等多种参数类型
- **蓝图驱动**：运行时通过蓝图修改参数即可切换外观

### 模块架构

| 模块 | 职责 |
|---|---|
| **MutableRuntime** | 运行时核心引擎，负责根据参数生成最终 Mesh/纹理 |
| **CustomizableObject** | UE 集成层，提供 `UCustomizableObject`、`UCustomizableObjectInstance` 等 UObject 封装 |
| **MutableTools** | 编辑器工具链，负责编译 CO（CustomizableObject）图、烘焙数据 |
| **MutableValidation** | 验证模块，确保编译和烘焙流程的正确性 |
| **CustomizableObjectEditor** | 编辑器 UI，提供 CO 编辑器和实例预览面板 |

## 使用场景

- 你在做一个 RPG 游戏，角色有数百种装备/发型/肤色组合 → 用 Mutable 替代为每种组合创建独立 Mesh
- 你需要在运行时让玩家自定义角色外观（捏脸系统） → 用 MutableInstance 的参数系统
- 你的游戏有装备染色/贴花系统 → 用 Mutable 的纹理层混合功能
- 你需要流式加载角色外观变体以节省内存 → 用 Mutable 的按需生成机制
- 你需要在编辑器中可视化编辑可定制对象 → 用 CustomizableObjectEditor 模块

## 蓝图用法

Mutable 的蓝图 API 主要集中在 `UCustomizableObjectInstance` 类上，用于运行时操控可定制对象实例。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetIntParameterSelectedOption` | 设置整数/枚举参数的选中值 | `UCustomizableObjectInstance` |
| `SetFloatParameterSelectedOption` | 设置浮点参数值 | `UCustomizableObjectInstance` |
| `SetBoolParameterSelectedOption` | 设置布尔开关参数 | `UCustomizableObjectInstance` |
| `SetVectorParameterSelectedOption` | 设置向量/颜色参数值 | `UCustomizableObjectInstance` |
| `SetTextureParameterSelectedOption` | 设置纹理参数 | `UCustomizableObjectInstance` |
| `SetProjectorParameterSelectedOption` | 设置投影器参数（贴花/变形） | `UCustomizableObjectInstance` |
| `GetFloatParameterSelectedOption` | 获取浮点参数当前值 | `UCustomizableObjectInstance` |
| `GetBoolParameterSelectedOption` | 获取布尔参数当前值 | `UCustomizableObjectInstance` |
| `GetIntParameterSelectedOption` | 获取整数参数当前值 | `UCustomizableObjectInstance` |
| `GetVectorParameterSelectedOption` | 获取向量参数当前值 | `UCustomizableObjectInstance` |
| `GetProjectorParameterSelectedOption` | 获取投影器参数当前值 | `UCustomizableObjectInstance` |
| `GetTextureParameterSelectedOption` | 获取纹理参数当前值 | `UCustomizableObjectInstance` |
| `GetNumParameters` | 获取参数总数 | `UCustomizableObjectInstance` |
| `GetParameterName` | 根据索引获取参数名 | `UCustomizableObjectInstance` |
| `GetParameterType` | 获取参数类型 | `UCustomizableObjectInstance` |
| `GetParameterDescription` | 获取参数描述 | `UCustomizableObjectInstance` |
| `GetParameterRangeValues` | 获取参数范围值（Min/Max） | `UCustomizableObjectInstance` |
| `GetParameterPossibleValues` | 获取枚举参数的可选值列表 | `UCustomizableObjectInstance` |
| `UpdateSkeletalMeshAsync` | 异步更新 SkeletalMesh（触发重新生成） | `UCustomizableObjectInstance` |
| `GetSkeletalMesh` | 获取当前生成的 SkeletalMesh | `UCustomizableObjectInstance` |
| `SetReplacePhysicsAssets` | 设置是否替换物理资产 | `UCustomizableObjectInstance` |
| `GetProjectorPosition` | 获取投影器位置 | `UCustomizableObjectInstance` |
| `SetProjectorPosition` | 设置投影器位置 | `UCustomizableObjectInstance` |
| `GetProjectorDirection` | 获取投影器方向 | `UCustomizableObjectInstance` |
| `SetProjectorDirection` | 设置投影器方向 | `UCustomizableObjectInstance` |
| `GetProjectorUp` | 获取投影器上方向 | `UCustomizableObjectInstance` |
| `SetProjectorUp` | 设置投影器上方向 | `UCustomizableObjectInstance` |
| `GetProjectorScale` | 获取投影器缩放 | `UCustomizableObjectInstance` |
| `SetProjectorScale` | 设置投影器缩放 | `UCustomizableObjectInstance` |
| `GetProjectorAngle` | 获取投影器角度 | `UCustomizableObjectInstance` |
| `SetProjectorAngle` | 设置投影器角度 | `UCustomizableObjectInstance` |
| `GetProjectorParameterType` | 获取投影器参数类型 | `UCustomizableObjectInstance` |
| `SetRandomValues` | 随机设置所有参数值 | `UCustomizableObjectInstance` |
| `SetReplaceMaterial` | 设置是否替换材质 | `UCustomizableObjectInstance` |
| `GetStateTags` | 获取当前状态标签 | `UCustomizableObjectInstance` |
| `SetStateTags` | 设置状态标签 | `UCustomizableObjectInstance` |
| `GetCurrentState` | 获取当前状态名称 | `UCustomizableObjectInstance` |
| `SetCurrentState` | 设置当前状态 | `UCustomizableObjectInstance` |
| `GetProjectorParameterType` | 获取投影器参数类型 | `UCustomizableObjectInstance` |
| `GetProjectorRange` | 获取投影器范围 | `UCustomizableObjectInstance` |
| `SetProjectorRange` | 设置投影器范围 | `UCustomizableObjectInstance` |
| `GetProjectorParameterType` | 获取投影器参数类型 | `UCustomizableObjectInstance` |
| `GetProjectorParameterType` | 获取投影器参数类型 | `UCustomizableObjectInstance` |

### 使用示例（蓝图描述）

**创建可定制角色实例：**

1. 创建 `UCustomizableObjectInstance` 变量
2. 调用 `UCustomizableObject::CreateInstance()` 创建实例
3. 使用 `Set*ParameterSelectedOption` 节点设置参数
4. 调用 `UpdateSkeletalMeshAsync` 触发异步更新
5. 监听 `OnCustomizableObjectInstanceUpdated` 委托
6. 在委托回调中获取 `GetSkeletalMesh` 并应用到 SkeletalMeshComponent

**参数遍历示例：**

1. 调用 `GetNumParameters` 获取参数总数
2. 循环调用 `GetParameterName` 和 `GetParameterType`
3. 根据类型调用对应的 `Get*ParameterSelectedOption`
4. 构建 UI 列表供玩家选择

## C++ 用法

### 头文件引入

```cpp
#include "CustomizableObject.h"
#include "CustomizableObjectInstance.h"
#include "CustomizableObjectSystem.h"
```

### 基本用法

```cpp
// 创建可定制对象实例
UCustomizableObject* CustomizableObject = LoadObject<UCustomizableObject>(nullptr, TEXT("/Game/Characters/CO_Character"));
UCustomizableObjectInstance* Instance = CustomizableObject->CreateInstance();

// 设置参数
Instance->SetIntParameterSelectedOption(FName("HairStyle"), FName("Long"));
Instance->SetFloatParameterSelectedOption(FName("SkinTone"), 0.75f);
Instance->SetBoolParameterSelectedOption(FName("HasHat"), true);
Instance->SetVectorParameterSelectedOption(FName("HairColor"), FLinearColor(0.8f, 0.2f, 0.1f));

// 异步更新
Instance->UpdateSkeletalMeshAsync();

// 监听更新完成
Instance->UpdatedDelegate.AddDynamic(this, &AMyCharacter::OnInstanceUpdated);
```

### 进阶用法

```cpp
// 遍历所有参数
int32 NumParams = Instance->GetNumParameters();
for (int32 i = 0; i < NumParams; ++i)
{
    FName ParamName = Instance->GetParameterName(i);
    EMutableParameterType ParamType = Instance->GetParameterType(i);
    
    switch (ParamType)
    {
    case EMutableParameterType::Int:
        // 处理整数参数
        break;
    case EMutableParameterType::Float:
        // 处理浮点参数
        break;
    case EMutableParameterType::Bool:
        // 处理布尔参数
        break;
    case EMutableParameterType::Color:
        // 处理颜色参数
        break;
    case EMutableParameterType::Texture:
        // 处理纹理参数
        break;
    case EMutableParameterType::Projector:
        // 处理投影器参数
        break;
    }
}

// 使用投影器参数（贴花系统）
FVector ProjectorPosition = FVector(0, 0, 100);
FVector ProjectorDirection = FVector(0, 0, -1);
FVector ProjectorUp = FVector(1, 0, 0);
FVector ProjectorScale = FVector(1, 1, 1);
float ProjectorAngle = 0.0f;

Instance->SetProjectorParameterSelectedOption(
    FName("DecalSlot"),
    ProjectorPosition,
    ProjectorDirection,
    ProjectorUp,
    ProjectorScale,
    ProjectorAngle
);

// 状态管理
FName DesiredState = FName("Armored");
Instance->SetCurrentState(DesiredState);
```

## Demo 示例

```cpp
// MyCharacter.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "CustomizableObjectInstance.h"
#include "MyCharacter.generated.h"

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Customizable")
    UCustomizableObject* CustomizableObjectAsset;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Customizable")
    UCustomizableObjectInstance* CustomizableInstance;

    UFUNCTION(BlueprintCallable, Category = "Customizable")
    void InitializeCustomizableObject();

    UFUNCTION(BlueprintCallable, Category = "Customizable")
    void SetHairStyle(const FName& StyleName);

    UFUNCTION(BlueprintCallable, Category = "Customizable")
    void SetSkinColor(const FLinearColor& Color);

    UFUNCTION(BlueprintCallable, Category = "Customizable")
    void RandomizeAppearance();

protected:
    UFUNCTION()
    void OnInstanceUpdated();

    virtual void BeginPlay() override;
};
```

```cpp
// MyCharacter.cpp
#include "MyCharacter.h"
#include "CustomizableObject.h"
#include "CustomizableObjectSystem.h"
#include "Components/SkeletalMeshComponent.h"

AMyCharacter::AMyCharacter()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();
    InitializeCustomizableObject();
}

void AMyCharacter::InitializeCustomizableObject()
{
    if (!CustomizableObjectAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT("CustomizableObjectAsset is null"));
        return;
    }

    CustomizableInstance = CustomizableObjectAsset->CreateInstance();
    if (!CustomizableInstance)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create CustomizableObjectInstance"));
        return;
    }

    // 绑定更新回调
    CustomizableInstance->UpdatedDelegate.AddDynamic(this, &AMyCharacter::OnInstanceUpdated);

    // 初始更新
    CustomizableInstance->UpdateSkeletalMeshAsync();
}

void AMyCharacter::SetHairStyle(const FName& StyleName)
{
    if (!CustomizableInstance) return;
    
    CustomizableInstance->SetIntParameterSelectedOption(FName("HairStyle"), StyleName);
    CustomizableInstance->UpdateSkeletalMeshAsync();
}

void AMyCharacter::SetSkinColor(const FLinearColor& Color)
{
    if (!CustomizableInstance) return;
    
    CustomizableInstance->SetVectorParameterSelectedOption(FName("SkinColor"), Color);
    CustomizableInstance->UpdateSkeletalMeshAsync();
}

void AMyCharacter::RandomizeAppearance()
{
    if (!CustomizableInstance) return;
    
    CustomizableInstance->SetRandomValues();
    CustomizableInstance->UpdateSkeletalMeshAsync();
}

void AMyCharacter::OnInstanceUpdated()
{
    if (!CustomizableInstance) return;

    USkeletalMesh* NewMesh = CustomizableInstance->GetSkeletalMesh();
    if (NewMesh)
    {
        GetMesh()->SetSkeletalMesh(NewMesh);
        UE_LOG(LogTemp, Log, TEXT("Customizable mesh updated successfully"));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MutableRuntime` | 运行时核心引擎，Mesh/纹理生成 |
| `MutableTools` | 编辑器工具链，CO 图编译和烘焙 |
| `DerivedDataCache` | 派生数据缓存，存储编译后的 CO 数据 |
| `MessageLog` | 编辑器消息日志，显示编译错误/警告 |

## 维护状态

### 近期更新

```
- 75e4adbd31f8 [Mutable] Change namespace name
- 304e190718a6 [mutable] Compilations with errors will now not allow for the baking of a COI - This change affects all paths available for the requesting of COI bakes.
- 3073da075fa3 [mutable] Static analisis bug fix (infinite loop)
```

### 维护评价

**活跃维护** ✅

- **创建时间**：2022-09-26，约 3 年历史
- **版本**：1.8.0，持续迭代
- **维护频率**：近期有实质性更新（编译流程改进、静态分析修复）
- **维护质量**：修复了无限循环 bug，增强了编译错误处理，表明代码质量持续改进
- **官方支持**：由 Epic Games 维护，是 UE5 官方插件
- **推荐使用**：✅ 强烈推荐用于需要角色/装备定制系统的项目

**注意事项**：
- 模块类型标注为 Runtime，但 CustomizableObjectEditor 实际是编辑器模块（Build.cs 依赖 UnrealEd）
- MutableValidation 模块负责验证编译和烘焙流程的正确性，确保错误的 CO 不会被烘焙

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/CustomizableObjects/)（UE 官方文档）

---

# MutableValidation 模块文档

> Mutable Validation module for ensuring compilation and baking correctness.

| 属性 | 值 |
|---|---|
| 分类 | CustomizableObjects |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableValidation` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Mutable/Source/MutableValidation) | |

## 用途

MutableValidation 是 Mutable 插件的**验证模块**，负责确保 CustomizableObject 的编译和实例烘焙流程的正确性。它的核心职责是：

1. **编译验证**：在 CO 图编译完成后，验证生成的中间数据是否符合预期
2. **烘焙拦截**：当编译存在错误时，阻止 COI（CustomizableObjectInstance）的烘焙流程
3. **静态分析**：检测潜在的逻辑错误（如无限循环）
4. **错误报告**：收集和报告验证过程中的问题

### 为什么需要这个模块？

在 Mutable 的工作流中：
- **编译**：将 CO 图转换为可执行的中间表示
- **烘焙**：将编译结果转换为运行时可用的数据

如果编译阶段存在错误（如无效的节点连接、缺失的资源引用），但仍然允许烘焙，会导致：
- 运行时崩溃
- 渲染错误
- 数据损坏

MutableValidation 作为**质量门禁**，确保只有通过验证的 CO 才能进入烘焙流程。

## 使用场景

- 你在编辑器中编译 CO 时看到错误提示 → MutableValidation 检测到问题并阻止烘焙
- 你在 CI/CD 流程中批量烘焙 CO → MutableValidation 确保只有有效资产被处理
- 你在调试 CO 编译问题 → MutableValidation 提供详细的错误信息

## 蓝图用法

MutableValidation 主要是**内部验证模块**，不直接暴露蓝图 API。它的验证逻辑在以下场景自动触发：

- 编辑器中点击"编译"按钮时
- 调用 `UCustomizableObject::Compile()` 时
- 请求烘焙 COI 时

### 间接使用

虽然没有直接的蓝图节点，但你可以通过以下方式观察验证结果：

| 场景 | 验证行为 |
|---|---|
| 编辑器编译 CO | 如果验证失败，Message Log 显示错误 |
| 蓝图调用 UpdateSkeletalMeshAsync | 如果 CO 编译未通过验证，更新不会执行 |
| 批量烘焙工具 | 验证失败的 CO 会被跳过并记录日志 |

## C++ 用法

### 头文件引入

```cpp
#include "MutableValidation.h"
```

### 基本用法

MutableValidation 主要被 MutableTools 和 CustomizableObject 模块内部调用，典型流程：

```cpp
// 在编译流程中（由 MutableTools 调用）
bool bCompilationSuccess = CompileCustomizableObject(CO);

if (bCompilationSuccess)
{
    // MutableValidation 验证编译结果
    bool bValidationPassed = ValidateCompilationResult(CO);
    
    if (bValidationPassed)
    {
        // 允许烘焙
        BakeCustomizableObjectInstance(COI);
    }
    else
    {
        // 验证失败，阻止烘焙
        UE_LOG(LogMutable, Error, TEXT("Validation failed for %s"), *CO->GetName());
    }
}
```

### 进阶用法

```cpp
// 自定义验证规则（如果需要扩展）
// 注意：这需要修改 MutableValidation 模块源码

// 验证编译结果的完整性
bool ValidateCompilationIntegrity(const FCustomizableObjectCompilationResult& Result)
{
    // 检查所有资源引用是否有效
    for (const FResourceReference& Ref : Result.ResourceReferences)
    {
        if (!IsResourceValid(Ref))
        {
            return false;
        }
    }
    
    // 检查数据结构完整性
    if (!Result.DataStructure.IsValid())
    {
        return false;
    }
    
    return true;
}
```

## Demo 示例

MutableValidation 是内部模块，不直接提供用户级 API。以下示例展示如何在自定义工具中集成验证逻辑：

```cpp
// CustomBakeTool.h
#pragma once

#include "CoreMinimal.h"
#include "CustomizableObject.h"
#include "CustomizableObjectInstance.h"
#include "CustomBakeTool.generated.h"

UCLASS()
class UCustomBakeTool : public UObject
{
    GENERATED_BODY()

public:
    /**
     * 批量烘焙 COI，包含验证步骤
     * @param ObjectsToBake 要烘焙的 CO 列表
     * @return 成功烘焙的数量
     */
    UFUNCTION(BlueprintCallable, Category = "Mutable|Bake")
    int32 BatchBakeWithValidation(const TArray<UCustomizableObject*>& ObjectsToBake);

private:
    bool ValidateBeforeBake(UCustomizableObject* CO);
    void LogValidationResult(UCustomizableObject* CO, bool bSuccess, const FString& ErrorMessage);
};
```

```cpp
// CustomBakeTool.cpp
#include "CustomBakeTool.h"
#include "MutableValidation.h"
#include "CustomizableObjectSystem.h"

int32 UCustomBakeTool::BatchBakeWithValidation(const TArray<UCustomizableObject*>& ObjectsToBake)
{
    int32 SuccessCount = 0;
    
    for (UCustomizableObject* CO : ObjectsToBake)
    {
        if (!CO)
        {
            UE_LOG(LogMutable, Warning, TEXT("Skipping null CO"));
            continue;
        }
        
        // 验证阶段
        if (!ValidateBeforeBake(CO))
        {
            LogValidationResult(CO, false, TEXT("Validation failed"));
            continue;
        }
        
        // 烘焙阶段
        UCustomizableObjectInstance* Instance = CO->CreateInstance();
        if (Instance)
        {
            // 设置默认参数
            Instance->SetRandomValues();
            
            // 触发更新（会经过内部验证）
            Instance->UpdateSkeletalMeshAsync();
            
            SuccessCount++;
            LogValidationResult(CO, true, TEXT("Bake initiated"));
        }
    }
    
    UE_LOG(LogMutable, Log, TEXT("Batch bake completed: %d/%d succeeded"), 
           SuccessCount, ObjectsToBake.Num());
    
    return SuccessCount;
}

bool UCustomBakeTool::ValidateBeforeBake(UCustomizableObject* CO)
{
    // 基本验证
    if (!CO->IsCompiled())
    {
        UE_LOG(LogMutable, Error, TEXT("CO %s is not compiled"), *CO->GetName());
        return false;
    }
    
    // 检查编译状态
    // 注意：实际的验证逻辑在 MutableValidation 模块内部
    // 这里只是示例性的前置检查
    
    return true;
}

void UCustomBakeTool::LogValidationResult(UCustomizableObject* CO, bool bSuccess, const FString& ErrorMessage)
{
    if (bSuccess)
    {
        UE_LOG(LogMutable, Log, TEXT("Validation passed for %s"), *CO->GetName());
    }
    else
    {
        UE_LOG(LogMutable, Error, TEXT("Validation failed for %s: %s"), 
               *CO->GetName(), *ErrorMessage);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MutableRuntime` | 运行时核心，提供数据结构定义 |
| `MutableTools` | 工具链，提供编译结果数据 |
| `CustomizableObject` | UE 集成层，提供 UObject 封装 |

## 维护状态

### 近期更新

```
- 75e4adbd31f8 [Mutable] Change namespace name
- 304e190718a6 [mutable] Compilations with errors will now not allow for the baking of a COI - This change affects all paths available for the requesting of COI bakes.
- 3073da075fa3 [mutable] Static analisis bug fix (infinite loop)
```

### 维护评价

**活跃维护** ✅

- **创建时间**：2022-09-26，与 Mutable 插件同龄
- **维护频率**：近期有重要更新
- **关键改进**：
  - `304e190718a6`：增强了编译错误处理，现在编译失败会阻止所有烘焙路径
  - `3073da075fa3`：修复了静态分析发现的无限循环 bug
- **维护质量**：持续改进验证逻辑的健壮性
- **推荐使用**：✅ 作为 Mutable 插件的核心组件，自动参与验证流程

**注意事项**：
- 这是内部模块，用户通常不直接调用
- 验证逻辑会自动在编译和烘焙流程中执行
- 如果遇到"Validation failed"错误，检查 CO 图的节点连接和资源引用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Mutable/Source/MutableValidation)
- [Mutable 插件文档](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Mutable)